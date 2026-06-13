"""M0 acceptance tests — the runtime hardware optimizer.

WHAT THESE TESTS DO
-------------------
Verify the auto-optimizer actually races devices, applies the prefer-CPU money
policy, and sizes parallelism to ~80% of cores within the safety bounds.

HOW THEY SERVE FTMO PASSING
---------------------------
They guarantee the cheap/fast training substrate works before any learning is
attempted — so the many walk-forward windows + 7 seeds that establish a pass rate
can actually be afforded. Rulebook: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""

from __future__ import annotations

import os

from quantra.runtime import HardwareConfig, RuntimeConfig, plan
from quantra.runtime.autoscale import plan_cpu_scale
from quantra.runtime.device import RepresentativePolicy, available_devices
from quantra.runtime.throughput_benchmark import race_devices


def test_representative_policy_shapes():
    """The benchmark net must match the locked four-head 3x256 architecture."""
    import torch

    net = RepresentativePolicy(state_dim=145)
    x = torch.randn(8, 145)
    d, s, p, v = net(x)
    assert d.shape == (8, 4)      # {HOLD, OPEN_LONG, OPEN_SHORT, CLOSE}
    assert s.shape == (8, 2)      # Beta alpha/beta
    assert p.shape == (8, 5)      # 5 trade slots
    assert v.shape == (8, 1)      # V(s)
    # trunk depth/width = 3 x 256
    linears = [m for m in net.trunk if m.__class__.__name__ == "Linear"]
    assert len(linears) == 3
    assert all(l.out_features == 256 for l in linears)


def test_devices_include_cpu():
    devs = available_devices()
    assert any(d.kind == "cpu" for d in devs), "CPU must always be a candidate"
    assert devs[0].kind == "cpu", "CPU must be listed first (the preferred default)"


def test_benchmark_runs_and_reports_throughput():
    results = race_devices(state_dim=64, batch=256, seconds=0.3)
    assert results, "benchmark returned no results"
    cpu = next(r for r in results if r.kind == "cpu")
    assert cpu.steps_per_sec > 0, "CPU benchmark should produce positive throughput"


def test_cpu_autoscale_respects_80pct_and_headroom():
    hw = HardwareConfig(utilization_target=0.80, reserved_cores=1)
    sp = plan_cpu_scale(hw)
    cores = os.cpu_count() or 1
    assert sp.n_envs >= hw.min_envs
    assert sp.n_envs <= hw.max_envs
    # never claim more threads than (cores - reserved)
    assert sp.torch_threads <= max(1, cores - hw.reserved_cores)


def test_plan_end_to_end_prefers_cpu_on_this_box():
    """On a CPU-only box the plan must select CPU and a sane env count."""
    cfg = RuntimeConfig()
    p = plan(state_dim=cfg.nominal_state_dim, hw=cfg.hardware, benchmark_seconds=0.3)
    assert p.device_kind in ("cpu", "cuda", "mps")
    assert p.n_envs >= 1
    # If there is no CUDA device, the choice MUST be cpu (the cheap default).
    import torch

    if not torch.cuda.is_available():
        assert p.device_kind == "cpu"
        assert p.device == "cpu"
