"""quantra.market_pipeline.feature_builder  —  SOW tier: 03_market_pipeline/feature_builder.

WHAT THIS PACKAGE DOES
----------------------
Builds the ~145-scalar state vector (market 1m/5m/30m/4H + law/gate flags + per-slot x5 trade block + portfolio aggregates + shared account + challenge progress). Offline-precomputes the action-independent blocks to a memmap.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
A complete, normalized observation lets the MLP tell breach-risk from safe trading (Term 1). Precomputing the heavy market math once keeps training fast and cheap so more windows/seeds get validated.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""

# [C - 2026-06-13, M2] Export the FeatureBuilder + schema API. Connects schema.py
# (canonical 146-dim layout), indicators.py (locked params), builder.py (offline
# precompute + assemble_state). Consumed by the env (M4) and telemetry (M9).
from .schema import SCHEMA, STATE_DIM, MARKET_NAMES, MARKET_DIM, build_schema
from .builder import (
    MarketMatrix,
    assemble_state,
    build_market_matrix,
    precompute_symbol,
)

__all__ = [
    "SCHEMA", "STATE_DIM", "MARKET_NAMES", "MARKET_DIM", "build_schema",
    "MarketMatrix", "assemble_state", "build_market_matrix", "precompute_symbol",
]


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
