"""quantra.locked_core.cost_layer  —  SOW tier: 01_locked_core/cost_layer  🔴.

WHAT THIS PACKAGE DOES
----------------------
Applies real FTMO costs from day 1: $5 round-trip per lot on forex, spread, and fixed slippage; metals/indices carry no per-trade commission.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
No costless world ever exists in training (SOW C8/H2), so the learned edge is real after fees — an edge that survives costs is one that can actually pass.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
