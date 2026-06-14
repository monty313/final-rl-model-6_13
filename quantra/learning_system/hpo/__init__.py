"""quantra.learning_system.hpo  —  SOW tier: 04_learning_system/hpo.

WHAT THIS PACKAGE DOES
----------------------
Optuna hyperparameter search over the NON-SACRED dials only (entropy, clip, LR, epochs ranges, later-phase stability).

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
gamma, lambda, and the aggression-scheduler logic are hand-locked and OFF-LIMITS (SOW G6): the 'patience' math that underpins passing is never tuned away by a search chasing short-term reward.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""

# [C - 2026-06-13, M13] Export the HPO API (sacred-guarded Optuna search).
from .hpo import DEFAULT_SEARCH_SPACE, SACRED_DIALS, run_study, suggest, validate_not_sacred

__all__ = ["SACRED_DIALS", "DEFAULT_SEARCH_SPACE", "suggest", "run_study", "validate_not_sacred"]


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
