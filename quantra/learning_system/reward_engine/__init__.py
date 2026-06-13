"""quantra.learning_system.reward_engine  —  SOW tier: 04_learning_system/reward_engine.

WHAT THIS PACKAGE DOES
----------------------
The layered reward r(t) = L0 net-PnL + shaping layers L1-L5 + L6 daily bonus (E7 streak + E9 QUAD), with Layer-0 dominance enforced and the QUAD bonus clamped at 95% of day PnL.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
Layer 0 (net PnL after costs) must always dominate so the bot can never win the reward game while losing the trading game (the E8 rule) — the shaping layers only help timing/restraint toward passing.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""


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
