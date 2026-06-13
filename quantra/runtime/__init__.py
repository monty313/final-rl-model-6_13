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


# ─────────────────────────────────────────────────────────────────────────────
# UPDATE LOG (IRAC) - standing rule since 2026-06-13.
# Every change to this file APPENDS a dated IRAC entry below (newest last):
#   I (Issue) / R (Rule) / A (Application) / C (Conclusion -> why this makes the
#   bot pass FTMO MORE CONSISTENTLY, with no bug or inefficiency). The LLM Risk
#   Doctor reads this log to reconstruct the chronological 'why' when
#   triangulating a pass-rate regression. Rulebook: docs/MLP_INTERPRETABILITY_LAYER.md
# ─────────────────────────────────────────────────────────────────────────────
# [2026-06-13] Package documented under the new IRAC rule.
#   I: Scaffolded in M0 with a header docstring but no standing change-log, so future FTMO-relevant implementation could drift undocumented.
#   R: SOW R2-R4 + the new IRAC update-log rule (2026-06-13).
#   A: Confirmed the header states the package's FTMO role + the LLM rulebook pointer; added this IRAC log as the permanent change-story anchor for when real code lands.
#   C: A documented, discoverable package keeps its future implementation aligned to repeated FTMO passing and prevents silent, bug-introducing drift.
