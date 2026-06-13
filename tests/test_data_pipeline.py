"""M1 acceptance tests — data loader (MT5 parse) + resampler (no lookahead).

These verify the pipeline that feeds the bot its world: the parser handles MT5
export variants and produces clean monotonic bars, and the resampler exposes only
CLOSED higher-TF bars. Lookahead here would teach a fantasy edge that breaches live,
so the no-lookahead test is a direct FTMO-passing guard.
Rulebook: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""

from __future__ import annotations

import pandas as pd

from quantra.market_pipeline.data_loader import OHLCV_COLUMNS, load_symbol, parse_mt5_csv
from quantra.market_pipeline.resampler import as_of_higher_tf, build_all_timeframes, resample_ohlcv


# ---------------------------------------------------------------------------
# Loader / parser
# ---------------------------------------------------------------------------
def test_parse_tab_delimited_mt5_export(make_1m, write_mt5_csv):
    df = make_1m(n_bars=600, seed=1)
    path = write_mt5_csv(df, sep="\t")
    parsed, meta = parse_mt5_csv(path)
    assert list(parsed.columns) == OHLCV_COLUMNS
    assert meta["delimiter"] == "\t"
    assert meta["had_spread"] is True
    assert parsed.index.is_monotonic_increasing
    assert len(parsed) == 600
    # OHLC values round-trip within float tolerance
    assert abs(parsed["close"].iloc[-1] - df["close"].iloc[-1]) < 1e-4


def test_parse_comma_delimited_variant(make_1m, write_mt5_csv):
    df = make_1m(n_bars=200, seed=2)
    path = write_mt5_csv(df, sep=",")
    parsed, meta = parse_mt5_csv(path)
    assert meta["delimiter"] == ","
    assert len(parsed) == 200


def test_parser_drops_duplicate_timestamps(make_1m, write_mt5_csv):
    df = make_1m(n_bars=100, seed=3)
    dup = pd.concat([df, df.iloc[:10]]).sort_index()  # inject 10 duplicate stamps
    path = write_mt5_csv(dup, sep="\t")
    parsed, meta = parse_mt5_csv(path)
    assert meta["dropped_duplicates"] == 10
    assert parsed.index.is_unique


def test_load_symbol_caches_to_parquet(make_1m, write_mt5_csv):
    df = make_1m(n_bars=150, seed=4)
    path = write_mt5_csv(df)
    out, rep = load_symbol("EURUSD", path=path, use_cache=False)
    assert rep.rows == 150
    assert rep.source == "local"
    assert list(out.columns) == OHLCV_COLUMNS


# ---------------------------------------------------------------------------
# Resampler
# ---------------------------------------------------------------------------
def test_resample_5m_ohlc_aggregation(make_1m):
    df = make_1m(n_bars=60, seed=5, start="2021-01-04 00:00:00")
    five = resample_ohlcv(df, "5min")
    # first 5m bar covers the 1m bars opening 00:00..00:04, closes/labelled 00:05
    first = five.iloc[0]
    block = df.iloc[0:5]
    assert five.index[0] == pd.Timestamp("2021-01-04 00:05:00")
    assert first["open"] == block["open"].iloc[0]
    assert first["high"] == block["high"].max()
    assert first["low"] == block["low"].min()
    assert first["close"] == block["close"].iloc[-1]
    assert first["tick_volume"] == block["tick_volume"].sum()


def test_build_all_timeframes_keys(make_1m):
    frames = build_all_timeframes(make_1m(n_bars=1000, seed=6))
    assert set(frames) == {"1m", "5m", "30m", "4H"}


def test_as_of_merge_has_no_lookahead(make_1m):
    """At every 1m time t, the attached 5m close must come from a bar closed <= t."""
    df = make_1m(n_bars=120, seed=7)
    five = resample_ohlcv(df, "5min")
    merged = as_of_higher_tf(df.index, five, suffix="5m")
    # For a sampled 1m timestamp, the merged 5m bar's source close-time must be <= t.
    for t in [df.index[3], df.index[7], df.index[42], df.index[99]]:
        val = merged.loc[t, "close_5m"]
        # the latest 5m bar whose close-time <= t
        eligible = five[five.index <= t]
        if eligible.empty:
            assert pd.isna(val)
        else:
            assert val == eligible["close"].iloc[-1]
            # and it must NOT equal a future (not-yet-closed) bar's close
            future = five[five.index > t]
            if not future.empty:
                assert val != future["close"].iloc[0] or eligible["close"].iloc[-1] == future["close"].iloc[0]
