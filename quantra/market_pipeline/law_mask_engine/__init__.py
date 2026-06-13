"""quantra.market_pipeline.law_mask_engine  —  SOW tier: 03_market_pipeline/law_mask_engine.

WHAT THIS PACKAGE DOES
----------------------
Wraps the locked_core laws for the env: computes all 12 law/gate states each step and emits the direction + pointer action masks, in live-ban OR law-school-permission mode.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
It is the per-step enforcement point that keeps the policy inside the legal space the laws define — the same masks in training and live, so behaviour transfers to real passing.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
