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
