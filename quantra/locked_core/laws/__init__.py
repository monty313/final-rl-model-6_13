"""quantra.locked_core.laws  —  SOW tier: 01_locked_core/laws  🔴.

WHAT THIS PACKAGE DOES
----------------------
The 9 directional laws (3 super-trend, 3 trend, 3 pullback) + 3 gates (ATR Liquidity, Spread Filter, Stationarity) and the LawMask that turns their states into pre-mask logits (logit = -1e9 on forbidden actions).

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
Laws run BEFORE the policy and forbid the directions that would breach the wall — directional stupidity is masked out, never merely penalised. They are masks, never reward terms (SOW R5).

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
