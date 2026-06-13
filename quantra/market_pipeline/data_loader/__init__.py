"""quantra.market_pipeline.data_loader  —  SOW tier: 03_market_pipeline/data_loader.

WHAT THIS PACKAGE DOES
----------------------
Loads MT5 1m bars (Colab Drive mount / gdown by file ID / local CSV), sniffs the export delimiter+columns, builds clean UTC-indexed OHLCV+spread, caches to Parquet.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
Faithful, lookahead-free bars with real per-bar spread feed both the Spread Filter law and the cost layer — the FTMO situation the bot must learn to pass.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
