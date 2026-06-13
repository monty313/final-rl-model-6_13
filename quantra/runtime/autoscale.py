"""Parallelism sizing: drive ~80% of the chosen device, leave headroom.

WHAT THIS MODULE DOES
---------------------
Decides (a) how many vectorised environment "worlds" to step in parallel and
(b) how many CPU threads torch/numpy may use, so the chosen device runs near the
configured utilisation target (default 80%) without oversubscribing the machine.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
80% (not 100%) is deliberate: a fully-pinned Colab kernel gets sluggish and is
more likely to be reclaimed, killing a half-finished window and wasting the spend.
Targeting 80% keeps the box healthy while still pushing throughput, so walk-forward
windows actually finish and contribute to the pass-rate scoreboard.

LLM RISK DOCTOR — HOW TO THINK ABOUT THIS FILE
----------------------------------------------
Rulebook: ``docs/MLP_INTERPRETABILITY_LAYER.md``. ``n_envs`` is an infrastructure
parallelism count, NOT a hyperparameter that changes the locked PPO math. Rollout
and minibatch sizes (G4: 512 / 64 early) are set in the trainer, not here. Do not
read ``n_envs`` as an aggression dial.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import torch

from .config import HardwareConfig


@dataclass(frozen=True)
class ScalePlan:
    """The concrete parallelism decision for a run."""

    n_envs: int
    torch_threads: int
    logical_cores: int
    rationale: str


def _logical_cores() -> int:
    """Best-effort logical core count (Colab usually reports 2-8)."""
    return os.cpu_count() or 1


def plan_cpu_scale(hw: HardwareConfig) -> ScalePlan:
    """Size CPU parallelism to the utilisation target with reserved headroom.

    We aim env workers + torch threads at ``utilization_target`` of the cores,
    keeping ``reserved_cores`` free. For the vectorised numpy env the dominant
    cost is feature/trade math, so n_envs scales with usable cores; torch (the
    tiny MLP) gets the same thread budget since matmuls are small.
    """
    cores = _logical_cores()
    usable = max(hw.min_envs, int(round(cores * hw.utilization_target)) - hw.reserved_cores)
    usable = max(hw.min_envs, min(usable, hw.max_envs))
    threads = max(1, min(usable, cores - hw.reserved_cores))
    return ScalePlan(
        n_envs=usable,
        torch_threads=threads,
        logical_cores=cores,
        rationale=(
            f"{cores} logical cores x {hw.utilization_target:.0%} target "
            f"- {hw.reserved_cores} reserved -> {usable} vectorised envs, {threads} torch threads"
        ),
    )


def plan_gpu_scale(hw: HardwareConfig) -> ScalePlan:
    """Size GPU parallelism: enough parallel worlds to fill the device.

    A 3x256 MLP is so small that GPU utilisation is driven by *batch size* (i.e.
    number of parallel envs feeding one forward). We pick a generous env count;
    the utilization_monitor then confirms whether we actually approached 80%. If
    not, the optimizer's report tells the operator the GPU is underused (drop it).
    """
    cores = _logical_cores()
    # Env stepping is still CPU-side, so keep that near the CPU target; the GPU
    # just consumes the resulting big batch.
    n_envs = max(hw.min_envs, min(hw.max_envs, max(64, int(round(cores * hw.utilization_target)) * 16)))
    return ScalePlan(
        n_envs=n_envs,
        torch_threads=max(1, cores - hw.reserved_cores),
        logical_cores=cores,
        rationale=(
            f"GPU path: {n_envs} parallel envs feed batched forward; env stepping "
            f"uses {cores - hw.reserved_cores} CPU threads"
        ),
    )


def apply_thread_limits(plan: ScalePlan) -> None:
    """Pin torch (and BLAS) thread counts so we don't oversubscribe cores.

    Oversubscription causes context-thrash that *lowers* throughput while showing
    misleadingly high CPU% — the opposite of an efficient 80%. Setting these makes
    the utilisation reading meaningful.
    """
    torch.set_num_threads(plan.torch_threads)
    os.environ.setdefault("OMP_NUM_THREADS", str(plan.torch_threads))
    os.environ.setdefault("MKL_NUM_THREADS", str(plan.torch_threads))
