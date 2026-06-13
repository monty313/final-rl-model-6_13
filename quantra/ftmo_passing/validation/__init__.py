"""quantra.ftmo_passing.validation  —  SOW tier: 02_ftmo_passing/validation.

WHAT THIS PACKAGE DOES
----------------------
The walk-forward runner (12mo train / 2mo test / 1mo step / 7 seeds) and the promotion gate (>=3 seeds, scoreboard improvement, no worse breach count).

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
This is the single locked protocol that decides whether a brain is genuinely better at PASSING — not luckier on one window — before it is ever promoted.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
