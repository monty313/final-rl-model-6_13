"""quantra.diagnostics.mlp_interpreter  —  SOW tier: 05_diagnostics/mlp_interpreter.

WHAT THIS PACKAGE DOES
----------------------
Converts raw telemetry into the 7 required visuals (activation trace, hidden-state PCA projection, action/value timeline, reward-layer timeline, correlation heatmap, failure atlas, pass-day atlas).

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
Raw arrays explain nothing; these visuals make 'did the internal behaviour help the bot pass?' answerable — clustering by breach-risk, showing Layer-0 dominance, exposing shortcut learning.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""

# [C - 2026-06-13, M10] Export the interpreter (consumed by the Risk Doctor + reports).
from .interpreter import MLPInterpreter

__all__ = ["MLPInterpreter"]


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
