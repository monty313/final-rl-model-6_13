"""quantra.market_pipeline.law_mask_engine  —  SOW tier: 03_market_pipeline/law_mask_engine.

WHAT THIS PACKAGE DOES
----------------------
Wraps the locked_core laws for the env: computes all 12 law/gate states each step and emits the direction + pointer action masks, in live-ban OR law-school-permission mode.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
It is the per-step enforcement point that keeps the policy inside the legal space the laws define — the same masks in training and live, so behaviour transfers to real passing.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""

# [C - 2026-06-13, M3] Export the mask API. engine.py turns law states + position +
# slots into the -1e9 action mask; consumed by the env (M4) and PPOAgent (M5).
from .engine import (
    CLOSE,
    HOLD,
    MODE_LIVE,
    MODE_SCHOOL,
    OPEN_LONG,
    OPEN_SHORT,
    LawMask,
    MaskResult,
    build_direction_mask,
    build_pointer_mask,
)

__all__ = [
    "LawMask", "MaskResult", "build_direction_mask", "build_pointer_mask",
    "MODE_LIVE", "MODE_SCHOOL", "HOLD", "OPEN_LONG", "OPEN_SHORT", "CLOSE",
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
