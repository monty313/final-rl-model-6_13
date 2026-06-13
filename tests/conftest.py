"""Shared pytest fixtures — reusable synthetic market data.

WHY THIS EXISTS
---------------
Unit tests must run fast and offline (no 480 MB Drive pull), yet exercise the same
shapes the real MT5 bars have. These fixtures synthesise realistic 1m OHLCV+spread
series and can write them out in MT5 export format, so every milestone (M1 loader,
M2 features, M4 env, ...) can test against deterministic, lookahead-free data.

This serves FTMO passing indirectly: trustworthy tests are how we keep the pipeline
that feeds the bot its world correct, so a green suite means the challenge physics
the bot trains against are faithful. Rulebook: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def _make_1m(symbol: str = "EURUSD", n_bars: int = 5000, seed: int = 0,
             start: str = "2021-01-04 00:00:00", base: float = 1.20) -> pd.DataFrame:
    """Deterministic geometric-random-walk 1m OHLCV+spread series.

    Returns a frame indexed by minute timestamps (bar OPEN time) with the canonical
    loader columns, so it stands in for a parsed MT5 export.
    """
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start=start, periods=n_bars, freq="1min")
    # log-returns ~ small vol; metals/indices get a bigger base price.
    if symbol in ("XAUUSD",):
        base = 1800.0
    elif symbol in ("US30",):
        base = 34000.0
    rets = rng.normal(0.0, 0.0004, size=n_bars)
    close = base * np.exp(np.cumsum(rets))
    open_ = np.empty_like(close)
    open_[0] = base
    open_[1:] = close[:-1]
    spread_ticks = rng.integers(1, 5, size=n_bars).astype(float)
    wiggle = np.abs(rng.normal(0, 0.0003, size=n_bars)) * close
    high = np.maximum(open_, close) + wiggle
    low = np.minimum(open_, close) - wiggle
    return pd.DataFrame(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "tick_volume": rng.integers(10, 200, size=n_bars).astype(float),
            "spread": spread_ticks,
        },
        index=pd.DatetimeIndex(idx, name="time"),
    )


@pytest.fixture
def make_1m():
    """Factory fixture: ``make_1m(symbol=..., n_bars=..., seed=...)`` -> 1m DataFrame."""
    return _make_1m


@pytest.fixture
def write_mt5_csv(tmp_path):
    """Factory: write a 1m DataFrame to a tab-delimited MT5-format CSV, return path.

    Mimics the real export header ``<DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE>
    <TICKVOL> <VOL> <SPREAD>`` with ``YYYY.MM.DD`` dates so the loader's
    delimiter/column sniffing is exercised exactly as it will be on the real files.
    """

    def _write(df: pd.DataFrame, name: str = "EURUSD_M1_test.csv", sep: str = "\t") -> Path:
        out = tmp_path / name
        rows = ["<DATE>" + sep + "<TIME>" + sep + "<OPEN>" + sep + "<HIGH>" + sep
                + "<LOW>" + sep + "<CLOSE>" + sep + "<TICKVOL>" + sep + "<VOL>" + sep + "<SPREAD>"]
        for ts, r in df.iterrows():
            rows.append(sep.join([
                ts.strftime("%Y.%m.%d"), ts.strftime("%H:%M:%S"),
                f"{r.open:.5f}", f"{r.high:.5f}", f"{r.low:.5f}", f"{r.close:.5f}",
                str(int(r.tick_volume)), "0", str(int(r.spread)),
            ]))
        out.write_text("\n".join(rows), encoding="utf-8")
        return out

    return _write


# ─────────────────────────────────────────────────────────────────────────────
# UPDATE LOG (IRAC) - standing rule since 2026-06-13.
# Every change to this file APPENDS a dated IRAC entry below (newest last):
#   I (Issue) / R (Rule) / A (Application) / C (Conclusion -> why this makes the
#   bot pass FTMO MORE CONSISTENTLY, with no bug or inefficiency). The LLM Risk
#   Doctor reads this log to reconstruct the chronological 'why' when
#   triangulating a pass-rate regression. Rulebook: docs/MLP_INTERPRETABILITY_LAYER.md
# ─────────────────────────────────────────────────────────────────────────────
# [2026-06-13] Deterministic offline fixtures for the whole suite.
#   I: Tests must be fast and offline yet match the real bar shapes the pipeline produces.
#   R: Trustworthy fixtures underpin every FTMO-relative guard in the master suite.
#   A: Deterministic synthetic 1m OHLCV+spread generator + MT5-CSV writer fixtures, reused by all milestones.
#   C: Reliable fixtures keep the suite green, which is how the bot's substrate stays correct as milestones land.
