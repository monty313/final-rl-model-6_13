"""quantra.diagnostics.telemetry_logger  —  SOW tier: 05_diagnostics/telemetry_logger.

WHAT THIS PACKAGE DOES
----------------------
Records the VERSIONED per-step / per-trade / per-day data contract (observation, law state, all four head outputs, V(s), hidden summaries, full reward decomposition, risk snapshot, outcome) the diagnostics layer reasons from.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
No telemetry -> no interpretability -> no diagnosis (Term 9). Capturing the full chain is what lets the Risk Doctor prove Layer-0 dominance and reconstruct any breach or pass day.

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
