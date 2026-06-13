"""quantra.runtime  —  SOW tier: [C] cross-cutting infrastructure (not a SOW tier).

WHAT THIS PACKAGE DOES
----------------------
Owns *how* Quantra runs rather than *what* it learns: the hardware auto-optimizer
(CPU-vs-GPU throughput race, ~80% utilisation autoscaling, utilisation monitor)
and the runtime configuration (FTMO defaults, traded symbols, Drive data IDs,
paths).

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
The mission needs many walk-forward windows x 7 seeds. This package makes each one
fast and cheap — auto-selecting the genuinely-faster device and driving it to ~80%
so we validate more pass-rate evidence per dollar and never idle a paid GPU on a
3x256 MLP.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
Everything here is infrastructure and is OUTSIDE the failure-taxonomy causal chain.
"""

from .config import (
    ChallengeConfig,
    HardwareConfig,
    RuntimeConfig,
    SYMBOLS,
    DRIVE_FILE_IDS,
    ensure_dirs,
    in_colab,
)
from .optimizer import HardwarePlan, plan, print_report
from .utilization_monitor import UtilizationMonitor, UtilizationSummary

__all__ = [
    "ChallengeConfig",
    "HardwareConfig",
    "RuntimeConfig",
    "SYMBOLS",
    "DRIVE_FILE_IDS",
    "ensure_dirs",
    "in_colab",
    "HardwarePlan",
    "plan",
    "print_report",
    "UtilizationMonitor",
    "UtilizationSummary",
]
