"""FeatureBuilder — assemble the ~145-scalar observation; precompute market block offline.

WHAT THIS MODULE DOES
---------------------
Turns clean 1m bars into the policy's observation:
  1. resample to 5m/30m/4H (lookahead-safe, M1),
  2. compute the locked indicators per timeframe (indicators.py),
  3. as-of merge higher-TF features onto the 1m clock (closed bars only),
  4. assemble the 89-scalar MARKET+TIME block in canonical schema order,
  5. clean (inf/NaN -> 0) and clip to a bounded range for a stable MLP,
  6. cache the result to a float32 memmap so the RL loop never recomputes it.

The action-DEPENDENT blocks (law flags, per-slot trade ×5, portfolio, account) are
filled at env-step time (M3/M4); ``assemble_state`` concatenates everything into the
full 146-vector in schema order.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
The 89 market features are a pure function of price, so computing them ONCE offline
(not every step) is the single biggest training-speed win — it makes many
walk-forward windows × 7 seeds affordable (the user's cost mandate) and keeps the
hot loop to array-indexing + a microsecond MLP. Bounded, NaN-free inputs keep the
tiny 3×256 trunk stable so it can actually learn the breach-risk vs safe distinction
that passing depends on.

LLM RISK DOCTOR — HOW TO THINK ABOUT THIS FILE
----------------------------------------------
Rulebook: ``docs/MLP_INTERPRETABILITY_LAYER.md``. The observation you analyse comes
from here. If hidden states can't separate regimes (Representation Collapse), check
``valid_from`` (warmup) and whether the market block is constant/zeroed for the
episode window before blaming the trunk. Features are clipped to ±CLIP; a feature
pinned at ±CLIP across an episode is a saturation signal worth flagging.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

from quantra.runtime import config as cfg
from quantra.market_pipeline.data_loader import load_symbol
from quantra.market_pipeline.resampler import build_all_timeframes

from . import indicators as ind
from .schema import MARKET_DIM, MARKET_NAMES, SCHEMA, STATE_DIM

# Continuous features are clipped to +/- CLIP after normalization. Real ATR-scaled
# distances / z-scores live well inside this; the clip only kills warmup blow-ups
# and flat-market division spikes that would destabilise the small MLP.
CLIP = 10.0


def _flag_three_way(cond_pos: pd.Series, cond_neg: pd.Series) -> pd.Series:
    """Encode a directional ingredient as -1 / 0 / +1 (the regime-flag convention)."""
    out = pd.Series(0.0, index=cond_pos.index)
    out[cond_pos] = 1.0
    out[cond_neg] = -1.0
    return out


def _compute_tf_features(df: pd.DataFrame, tf: str) -> pd.DataFrame:
    """Compute every schema market feature that belongs to timeframe ``tf``.

    Returns a frame indexed like ``df`` with columns named exactly per schema
    (e.g. ``boll_bb20_mid_5m``), so assembly is a pure column-select — the naming
    alignment the telemetry contract relies on.
    """
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    atr_tf = ind.atr(h, l, c, ind.ATR_PERIOD).replace(0, np.nan)
    out: Dict[str, pd.Series] = {}

    # --- Bollinger (5m/30m/4H): price-vs-band distance in ATR units ---
    if tf in ("5m", "30m", "4H"):
        bb20_mid, bb20_up, bb20_lo = ind.bollinger(c, ind.BB_FAST)
        bb200_mid, bb200_up, bb200_lo = ind.bollinger(c, ind.BB_SLOW)
        for base, line in [
            ("bb20_mid", bb20_mid), ("bb20_up", bb20_up), ("bb20_lo", bb20_lo),
            ("bb200_mid", bb200_mid), ("bb200_up", bb200_up), ("bb200_lo", bb200_lo),
        ]:
            out[f"boll_{base}_{tf}"] = (c - line) / atr_tf

    # --- CCI (1m/5m/30m/4H): normalized + deviation-from-shifted-SMA + sync ---
    if tf in ("1m", "5m", "30m", "4H"):
        cci_dev = {}
        for p in ind.CCI_PERIODS:
            cp = ind.cci(h, l, c, p)
            csma = ind.applied_sma_shift(cp, ind.CCI_APPLIED_SMA, ind.SHIFT)
            out[f"cci{p}_norm_{tf}"] = cp / 100.0
            dev = (cp - csma) / 100.0
            out[f"cci{p}_dev_{tf}"] = dev
            cci_dev[p] = dev
        all_pos = (cci_dev[10] > 0) & (cci_dev[30] > 0) & (cci_dev[100] > 0)
        all_neg = (cci_dev[10] < 0) & (cci_dev[30] < 0) & (cci_dev[100] < 0)
        out[f"cci_sync_{tf}"] = _flag_three_way(all_pos, all_neg)
        if tf == "5m":
            # Pull Back ingredient: large CCIs aligned while small (10) desyncs.
            buy = (cci_dev[30] > 0) & (cci_dev[100] > 0) & (cci_dev[10] < 0)
            sell = (cci_dev[30] < 0) & (cci_dev[100] < 0) & (cci_dev[10] > 0)
            out["cci_pullback_5m"] = _flag_three_way(buy, sell)

    # --- ATR regime (1m/30m/4H): level, shifted ref, normalized deviation ---
    if tf in ("1m", "30m", "4H"):
        atr_t = ind.atr(h, l, c, ind.ATR_PERIOD)
        baseline = atr_t.rolling(100, min_periods=20).mean().replace(0, np.nan)
        ref = atr_t.rolling(ind.ATR_REF_PERIOD).mean().shift(ind.SHIFT)
        out[f"atr_level_{tf}"] = atr_t / baseline
        out[f"atr_ref_{tf}"] = ref / baseline
        out[f"atr_dev_{tf}"] = (atr_t - ref) / ref.replace(0, np.nan)

    # --- Shifted SMA (1m/5m/30m/4H) on high/low + alignment flag ---
    if tf in ("1m", "5m", "30m", "4H"):
        ssma_h = ind.shifted_sma(h, ind.SSMA_PERIOD, ind.SHIFT)
        ssma_l = ind.shifted_sma(l, ind.SSMA_PERIOD, ind.SHIFT)
        out[f"ssma_high_dist_{tf}"] = (c - ssma_h) / atr_tf
        out[f"ssma_low_dist_{tf}"] = (c - ssma_l) / atr_tf
        out[f"ssma_align_{tf}"] = _flag_three_way((c > ssma_h) & (c > ssma_l),
                                                  (c < ssma_h) & (c < ssma_l))

    # --- Z-scores (1m/5m/30m/4H): dual lookback ---
    if tf in ("1m", "5m", "30m", "4H"):
        out[f"z10_{tf}"] = ind.zscore(c, 10)
        out[f"z100_{tf}"] = ind.zscore(c, 100)

    # --- ADX (1m/30m/4H): trend strength, normalized /100 ---
    if tf in ("1m", "30m", "4H"):
        out[f"adx5_{tf}"] = ind.adx(h, l, c, 5) / 100.0
        out[f"adx15_{tf}"] = ind.adx(h, l, c, 15) / 100.0

    # --- Candle structure + time context: 1m only ---
    if tf == "1m":
        ret, rng_atr, uwick, lwick = ind.candle_structure(o, h, l, c, atr_tf)
        out["candle_return_1m"] = ret
        out["candle_range_1m"] = rng_atr
        out["candle_uwick_1m"] = uwick
        out["candle_lwick_1m"] = lwick
        idx = df.index
        hour = idx.hour + idx.minute / 60.0
        out["time_sin_hour"] = pd.Series(np.sin(2 * np.pi * hour / 24.0), index=idx)
        out["time_cos_hour"] = pd.Series(np.cos(2 * np.pi * hour / 24.0), index=idx)
        out["time_dow"] = pd.Series((idx.dayofweek / 4.0) * 2.0 - 1.0, index=idx)

    return pd.DataFrame(out, index=df.index)


def _asof_onto(base_index: pd.DatetimeIndex, feat: pd.DataFrame) -> pd.DataFrame:
    """Backward as-of merge a higher-TF feature frame onto the 1m index (no peek)."""
    base = pd.DataFrame(index=base_index)
    base.index.name = "time"
    merged = pd.merge_asof(
        base.reset_index(), feat.reset_index(), on="time", direction="backward"
    ).set_index("time")
    return merged


@dataclass
class MarketMatrix:
    """The precomputed market block + provenance for the env / telemetry."""

    matrix: np.ndarray          # (T, 89) float32, schema MARKET order
    index: pd.DatetimeIndex     # 1m timestamps aligned to rows
    valid_from: int             # first row with no warmup NaN (env starts here)
    names: list                 # MARKET_NAMES (for telemetry block labels)


def build_market_matrix(df_1m: pd.DataFrame) -> MarketMatrix:
    """Compute the 89-wide market+time matrix for one symbol from its 1m bars.

    Pure (no IO): used directly by tests and by ``precompute_symbol``. Higher-TF
    features are as-of merged so row t only sees closed 5m/30m/4H bars.
    """
    frames = build_all_timeframes(df_1m)  # {1m,5m,30m,4H}
    cols = pd.DataFrame(index=df_1m.index)

    one_min = _compute_tf_features(frames["1m"], "1m")
    cols = cols.join(one_min)
    for tf in ("5m", "30m", "4H"):
        feat = _compute_tf_features(frames[tf], tf)
        cols = cols.join(_asof_onto(df_1m.index, feat))

    # Order to the canonical schema; missing columns would be a coding error.
    missing = [n for n in MARKET_NAMES if n not in cols.columns]
    if missing:
        raise RuntimeError(f"FeatureBuilder produced no values for: {missing}")
    ordered = cols[MARKET_NAMES]

    # valid_from = first row where all NON-4H market features are ready (warmup end).
    # 4H is observation-only (4H Observation Rule) and may legitimately stay 0 during
    # its long BB200 warmup, so we don't make the env wait ~33 days for it — we wait
    # only for the law-relevant 1m/5m/30m features. This keeps usable training bars
    # per window high, which matters for getting enough pass/fail samples per seed.
    non_4h = [n for n in MARKET_NAMES if not n.endswith("_4H")]
    valid_mask = ordered[non_4h].notna().all(axis=1).to_numpy()
    valid_from = int(np.argmax(valid_mask)) if valid_mask.any() else len(ordered)

    cleaned = (
        ordered.replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
        .clip(-CLIP, CLIP)
        .to_numpy(dtype=np.float32)
    )
    return MarketMatrix(cleaned, df_1m.index, valid_from, list(MARKET_NAMES))


def precompute_symbol(symbol: str, force: bool = False) -> MarketMatrix:
    """Build + memmap-cache the market block for ``symbol`` (Drive/local via M1).

    First call computes and writes ``data/features/{symbol}_market.npy`` (+ a
    timestamp sidecar); later calls memory-map it. This is the offline step that
    keeps training cheap enough to validate a real pass rate.
    """
    cfg.ensure_dirs()
    npy = cfg.FEATURE_CACHE_DIR / f"{symbol}_market.npy"
    meta = cfg.FEATURE_CACHE_DIR / f"{symbol}_market_index.parquet"
    if npy.exists() and meta.exists() and not force:
        mat = np.load(npy, mmap_mode="r")
        idx = pd.read_parquet(meta).index
        valid_from = int(np.argmax(np.abs(mat).sum(axis=1) > 0)) if len(mat) else 0
        return MarketMatrix(mat, pd.DatetimeIndex(idx), valid_from, list(MARKET_NAMES))

    df_1m, _ = load_symbol(symbol)
    mm = build_market_matrix(df_1m)
    np.save(npy, mm.matrix)
    pd.DataFrame(index=mm.index).to_parquet(meta)
    return mm


def assemble_state(
    market_row: np.ndarray,
    law_flags: Optional[np.ndarray] = None,
    trade: Optional[np.ndarray] = None,
    portfolio: Optional[np.ndarray] = None,
    account: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Concatenate the 5 blocks into the full 146-vector in canonical schema order.

    The env (M4) calls this each step with the live law/trade/portfolio/account
    sub-vectors; any omitted block is zero-filled (used in M2 tests and warmup).
    The result width is asserted == STATE_DIM so a block-size drift fails loudly
    rather than silently feeding the policy a malformed world.
    """
    def _blk(name: str, vec: Optional[np.ndarray]) -> np.ndarray:
        width = SCHEMA.block_spans[name][1] - SCHEMA.block_spans[name][0]
        if vec is None:
            return np.zeros(width, dtype=np.float32)
        v = np.asarray(vec, dtype=np.float32).ravel()
        if v.shape[0] != width:
            raise ValueError(f"block '{name}' expected {width} values, got {v.shape[0]}")
        return v

    state = np.concatenate([
        _blk("market", np.asarray(market_row, dtype=np.float32).ravel()),
        _blk("law", law_flags),
        _blk("trade", trade),
        _blk("portfolio", portfolio),
        _blk("account", account),
    ])
    assert state.shape[0] == STATE_DIM, f"assembled {state.shape[0]} != {STATE_DIM}"
    return state.astype(np.float32)


# Convenience re-exports for the env/agent/telemetry.
__all__ = [
    "MarketMatrix", "build_market_matrix", "precompute_symbol", "assemble_state",
    "MARKET_NAMES", "MARKET_DIM", "STATE_DIM", "SCHEMA", "CLIP",
]


# ─────────────────────────────────────────────────────────────────────────────
# UPDATE LOG (IRAC) - standing rule since 2026-06-13.
# Every change APPENDS a dated IRAC entry (newest last). Conclusion is ALWAYS why
# the change makes the bot pass FTMO more consistently with no bug/inefficiency.
# Rulebook: docs/MLP_INTERPRETABILITY_LAYER.md
# ─────────────────────────────────────────────────────────────────────────────
# [2026-06-13] M2 — FeatureBuilder + offline market precompute.
#   I: Computing ~89 multi-TF indicators every RL step would make walk-forward
#      validation unaffordable, and any lookahead/NaN would teach a fantasy edge
#      or destabilise the tiny MLP — both wreck consistent passing.
#   R: STATE_VECTOR.md (~145, 4H observation copies) + offline-precompute design +
#      lookahead-safe as-of merge (M1) + bounded encodings.
#   A: Vectorized per-TF compute -> backward as-of merge -> schema-ordered 89-wide
#      matrix -> inf/NaN->0, clip ±10 -> float32 memmap cache; assemble_state()
#      concatenates the full 146 with asserted block widths.
#   C: The hot loop is just array indexing + a microsecond MLP on a faithful,
#      bounded, lookahead-free observation, so we can afford the seeds/windows that
#      prove a real, transferable FTMO pass rate.
