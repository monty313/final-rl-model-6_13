"""quantra.market_pipeline.data_loader  —  SOW tier: 03_market_pipeline/data_loader.

WHAT THIS PACKAGE DOES
----------------------
Loads MT5 1m bars (Colab Drive mount / gdown by file ID / local CSV), sniffs the export delimiter+columns, builds clean UTC-indexed OHLCV+spread, caches to Parquet.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
Faithful, lookahead-free bars with real per-bar spread feed both the Spread Filter law and the cost layer — the FTMO situation the bot must learn to pass.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""

# [C - 2026-06-13, M1] Export the loader API for short, stable import paths
# (`from quantra.market_pipeline.data_loader import load_symbol`). Connects to
# loader.py; consumed by the env/feature precompute (M2/M4).
from .loader import (
    OHLCV_COLUMNS,
    LoadReport,
    load_all,
    load_symbol,
    parse_mt5_csv,
)

__all__ = ["OHLCV_COLUMNS", "LoadReport", "load_all", "load_symbol", "parse_mt5_csv"]
