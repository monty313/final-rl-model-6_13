"""quantra.market_pipeline.feature_builder  —  SOW tier: 03_market_pipeline/feature_builder.

WHAT THIS PACKAGE DOES
----------------------
Builds the ~145-scalar state vector (market 1m/5m/30m/4H + law/gate flags + per-slot x5 trade block + portfolio aggregates + shared account + challenge progress). Offline-precomputes the action-independent blocks to a memmap.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
A complete, normalized observation lets the MLP tell breach-risk from safe trading (Term 1). Precomputing the heavy market math once keeps training fast and cheap so more windows/seeds get validated.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
