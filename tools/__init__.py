"""quantra dev tools — change-impact tracker (snapshot guard + AST impact analyzer).

Not part of the importable bot package; these are operator/CI utilities that keep
the codebase honest so the bot keeps passing FTMO consistently. See snapshot.py
(Tier 1 state-vector guard) and impact.py (Tier 2 reverse-dependency analyzer).
Rulebook for the LLM Risk Doctor: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""


# ─────────────────────────────────────────────────────────────────────────────
# UPDATE LOG (IRAC) - standing rule since 2026-06-13.
# Every change APPENDS a dated IRAC entry (newest last). Conclusion is ALWAYS why
# the change makes the bot pass FTMO more consistently with no bug/inefficiency.
# Rulebook: docs/MLP_INTERPRETABILITY_LAYER.md
# ─────────────────────────────────────────────────────────────────────────────
# [2026-06-13] Created the dev-tools package for the change-impact tracker.
#   I: A feature/observation change could ripple to env/agent/telemetry/tests
#      undetected, silently degrading pass-rate between runs.
#   R: Operator request for a change-impact tracking system (snapshot + import graph).
#   A: Added tools/ with snapshot.py (state-vector guard) + impact.py (AST reverse-deps).
#   C: Blast radius of any pipeline change is now visible + enforced, so the bot's
#      world and the code reasoning about it never drift apart — protecting passing.
