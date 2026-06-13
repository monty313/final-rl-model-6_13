"""StateVectorSchema — the canonical, ordered layout of the ~145-scalar observation.

WHAT THIS MODULE DOES
---------------------
Defines EXACTLY which scalars the policy sees, in what order, grouped into named
blocks, so the total width is fixed and asserted everywhere. This is the contract
that the FeatureBuilder fills, the env assembles, the PPO trunk consumes, and the
TelemetryLogger labels (the data contract requires "grouped feature block names").

Block widths (per STATE_VECTOR.md, total = 146 ≈ the spec's "~145"):
    market+time  89   (action-independent — precomputed offline, memmapped)
    law/gate     12   (9 laws + 3 gates; filled by LawMask, M3)
    trade x5     35   (7 features x 5 slots; filled by the env, M4)
    portfolio     3   (aggregates across slots; env, M4)
    account       7   (equity/buffers + 2 challenge-progress; env, M4)
    --------------------
    TOTAL       146

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
If the observation is incomplete or mis-ordered, the MLP cannot tell a breach-risk
state from a safe one (MLP_INTERPRETABILITY_LAYER Term 1) — the single most common
root cause of inconsistent passing. A frozen, named, asserted schema guarantees the
bot always sees the full FTMO-relevant picture and that telemetry can map any neuron
back to the exact feature that drove a decision.

LLM RISK DOCTOR — HOW TO THINK ABOUT THIS FILE
----------------------------------------------
Rulebook: ``docs/MLP_INTERPRETABILITY_LAYER.md``. Use ``block_slice(name)`` /
``FEATURE_NAMES`` to know precisely which observation indices belong to which block.
When you suspect Representation Collapse (breach-risk and safe states look alike),
first confirm the account/challenge block is actually populated and non-constant —
a zeroed account block makes danger invisible regardless of the trunk.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Timeframe groupings per the law/observation specs (THE_TRADING_CODE.md,
# STATE_VECTOR.md). 4H is ALWAYS observation-only (4H Observation Rule).
# ---------------------------------------------------------------------------
BOLL_TFS = ["5m", "30m", "4H"]          # Bollinger laws bind 5m/30m; 4H observed
CCI_TFS = ["1m", "5m", "30m", "4H"]     # observation carries 1m too; 4H observed
ATR_TFS = ["1m", "30m", "4H"]
SSMA_TFS = ["1m", "5m", "30m", "4H"]
Z_TFS = ["1m", "5m", "30m", "4H"]
ADX_TFS = ["1m", "30m", "4H"]

_BB_BANDS = ["bb20_mid", "bb20_up", "bb20_lo", "bb200_mid", "bb200_up", "bb200_lo"]
_CCI_PERIODS = [10, 30, 100]


def _market_names() -> List[str]:
    """Generate the 89 market+time feature names in canonical order.

    builder.py generates its columns by the SAME loops, so names and values stay
    aligned by construction — the alignment guarantee the telemetry contract needs.
    """
    names: List[str] = []
    # Bollinger (18): price-vs-band distances in ATR units
    for tf in BOLL_TFS:
        for band in _BB_BANDS:
            names.append(f"boll_{band}_{tf}")
    # CCI (29): per period, the normalized CCI and (CCI - appliedSMA), + sync flags
    for tf in CCI_TFS:
        for p in _CCI_PERIODS:
            names.append(f"cci{p}_norm_{tf}")
            names.append(f"cci{p}_dev_{tf}")
        names.append(f"cci_sync_{tf}")          # all CCIs same side of their SMA
    names.append("cci_pullback_5m")              # small(10) desync vs large in 5m
    # ATR (9): level, shifted reference, normalized deviation
    for tf in ATR_TFS:
        names.append(f"atr_level_{tf}")
        names.append(f"atr_ref_{tf}")
        names.append(f"atr_dev_{tf}")
    # Shifted SMA (12): distance to shifted high/low lines + alignment flag
    for tf in SSMA_TFS:
        names.append(f"ssma_high_dist_{tf}")
        names.append(f"ssma_low_dist_{tf}")
        names.append(f"ssma_align_{tf}")
    # Z-scores (8): dual lookback 10 + 100
    for tf in Z_TFS:
        names.append(f"z10_{tf}")
        names.append(f"z100_{tf}")
    # ADX (6): ADX5 + ADX15, normalized /100
    for tf in ADX_TFS:
        names.append(f"adx5_{tf}")
        names.append(f"adx15_{tf}")
    # Candle structure on 1m (4)
    names += ["candle_return_1m", "candle_range_1m", "candle_uwick_1m", "candle_lwick_1m"]
    # Time context (3)
    names += ["time_sin_hour", "time_cos_hour", "time_dow"]
    return names


def _law_names() -> List[str]:
    """The 12 law/gate state flags (9 directional laws + 3 gates)."""
    return [
        "law_super_trend_bb", "law_super_trend_cci", "law_super_trend_ssma",
        "law_trend_bb", "law_trend_cci", "law_trend_ssma",
        "law_pullback_bb", "law_pullback_cci", "law_pullback_ssma",
        "gate_atr_liquidity", "gate_spread", "gate_stationarity",
    ]


N_SLOTS = 5
_SLOT_FEATURES = ["dir", "upnl", "age", "entry_dist", "mfe", "mae", "occupied"]


def _trade_names() -> List[str]:
    """Per-slot ×5 trade block (7 features each) — the pointer head reads this."""
    return [f"slot{s}_{f}" for s in range(N_SLOTS) for f in _SLOT_FEATURES]


def _portfolio_names() -> List[str]:
    return ["port_net_exposure", "port_net_size", "port_total_upnl"]


def _account_names() -> List[str]:
    """Account block incl. the 2 challenge-progress features (SOW C12)."""
    return [
        "acct_equity_norm", "acct_equity_dev", "acct_equity_slope",
        "acct_trailing_buffer", "acct_daily_buffer",
        "acct_day_progress", "acct_overall_progress",
    ]


# Ordered blocks: (name, feature_names). Order IS the observation order.
_BLOCK_BUILDERS = [
    ("market", _market_names),
    ("law", _law_names),
    ("trade", _trade_names),
    ("portfolio", _portfolio_names),
    ("account", _account_names),
]


@dataclass(frozen=True)
class StateVectorSchema:
    """Frozen, validated layout of the observation vector."""

    blocks: Dict[str, List[str]]
    feature_names: List[str]
    block_spans: Dict[str, Tuple[int, int]]  # name -> (start, end) half-open

    @property
    def dim(self) -> int:
        return len(self.feature_names)

    def block_slice(self, name: str) -> slice:
        s, e = self.block_spans[name]
        return slice(s, e)

    def index_of(self, feature: str) -> int:
        return self.feature_names.index(feature)


def build_schema() -> StateVectorSchema:
    """Assemble + validate the canonical schema. Raises if names aren't unique."""
    blocks: Dict[str, List[str]] = {}
    feature_names: List[str] = []
    spans: Dict[str, Tuple[int, int]] = {}
    for name, fn in _BLOCK_BUILDERS:
        block = fn()
        start = len(feature_names)
        feature_names.extend(block)
        spans[name] = (start, len(feature_names))
        blocks[name] = block
    if len(set(feature_names)) != len(feature_names):
        dupes = [n for n in feature_names if feature_names.count(n) > 1]
        raise ValueError(f"duplicate feature names in schema: {sorted(set(dupes))}")
    return StateVectorSchema(blocks=blocks, feature_names=feature_names, block_spans=spans)


# Singleton + public constants. STATE_DIM is the asserted observation width.
SCHEMA = build_schema()
STATE_DIM = SCHEMA.dim                    # 146
MARKET_NAMES = SCHEMA.blocks["market"]    # the 89 precomputable features
MARKET_DIM = len(MARKET_NAMES)            # 89

# Expected block widths — asserted by the master suite so a refactor can't silently
# drop a challenge-critical feature (which would blind the bot to breach-risk).
EXPECTED_WIDTHS = {"market": 89, "law": 12, "trade": 35, "portfolio": 3, "account": 7}


# ─────────────────────────────────────────────────────────────────────────────
# UPDATE LOG (IRAC) - standing rule since 2026-06-13.
# Every change to this file APPENDS a dated IRAC entry below (newest last):
#   I (Issue) / R (Rule) / A (Application) / C (Conclusion -> why this makes the
#   bot pass FTMO MORE CONSISTENTLY, with no bug or inefficiency). The LLM Risk
#   Doctor reads this log to reconstruct the chronological 'why' when triangulating
#   a pass-rate regression. Rulebook: docs/MLP_INTERPRETABILITY_LAYER.md
# ─────────────────────────────────────────────────────────────────────────────
# [2026-06-13] M2 — canonical state-vector schema created.
#   I: The bot's perception had no single, asserted layout; without one, a later
#      refactor could drop/reorder a challenge-critical feature and silently blind
#      the policy to breach-risk — a top cause of inconsistent passing.
#   R: STATE_VECTOR.md block counts (~145) + the telemetry data contract's
#      "grouped feature block names" requirement (MLP_INTERPRETABILITY_LAYER).
#   A: Defined 146 scalars in 5 ordered blocks (market 89, law 12, trade 35,
#      portfolio 3, account 7) with unique-name validation + block slices.
#   C: A frozen, named, asserted observation means the bot always sees the full
#      FTMO picture and telemetry can map any neuron to its driving feature — the
#      precondition for diagnosable, repeatable passing.
