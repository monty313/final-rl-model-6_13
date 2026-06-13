"""quantra.learning_system.reward_engine  —  SOW tier: 04_learning_system/reward_engine.

WHAT THIS PACKAGE DOES
----------------------
The layered reward r(t) = L0 net-PnL + shaping layers L1-L5 + L6 daily bonus (E7 streak + E9 QUAD), with Layer-0 dominance enforced and the QUAD bonus clamped at 95% of day PnL.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
Layer 0 (net PnL after costs) must always dominate so the bot can never win the reward game while losing the trading game (the E8 rule) — the shaping layers only help timing/restraint toward passing.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
