"""QUANTRA MASTER TEST SUITE — the one big runnable test for the whole folder.

WHY THIS FILE EXISTS (read before adding tests)
-----------------------------------------------
STANDING RULE [2026-06-13]: this is the SINGLE place every Quantra test lives.
All future tests — for any milestone (laws, env, agent, reward, telemetry, ...) —
are APPENDED here under the matching section, never scattered into new files. One
command runs the entire folder's guarantees:

    pytest tests/test_ftmo_master_suite.py        # or just: pytest

WHAT IT PROVES (everything is judged against repeated FTMO passing, not PnL)
---------------------------------------------------------------------------
The suite is organised along the interpretability chain from
``docs/MLP_INTERPRETABILITY_LAYER.md`` (State Vector -> Law -> Hidden State ->
Heads -> Risk -> Reward -> Outcome), plus the cost/speed substrate that lets us
afford enough seeds and walk-forward windows to *establish* a pass rate:

    SECTION A  Runtime / hardware efficiency   (afford the validation budget)
    SECTION B  Data pipeline - loader          (faithful FTMO situation in)
    SECTION C  Data pipeline - resampler       (no lookahead -> edge transfers)
    (SECTION D+ added as M2+ land: features, laws, env, agent, reward, telemetry)

HOW THE LLM RISK DOCTOR SHOULD USE THIS FILE
--------------------------------------------
A green master suite means the *substrate* the bot trains on is faithful and fast;
it does NOT by itself prove the policy passes. When triangulating a pass-rate
regression, first confirm this suite is green — a red data/resampler test means the
bot's world is corrupt (e.g. lookahead leakage masquerading as a learned edge), and
that is the break, not the actor/critic. Only if the substrate is sound do you walk
the chain into hidden-state / reward / critic diagnostics.

Rulebook: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""

from __future__ import annotations

import os
import time

import pandas as pd
import pytest

import quantra.runtime.config as cfg
from quantra.market_pipeline.data_loader import OHLCV_COLUMNS, load_symbol, parse_mt5_csv
from quantra.market_pipeline.resampler import (
    as_of_higher_tf,
    build_all_timeframes,
    resample_ohlcv,
)
from quantra.runtime import HardwareConfig, RuntimeConfig, plan
from quantra.runtime.autoscale import plan_cpu_scale
from quantra.runtime.device import RepresentativePolicy, available_devices
from quantra.runtime.throughput_benchmark import race_devices


# =============================================================================
# SECTION A — RUNTIME / HARDWARE EFFICIENCY
# FTMO link: the validation that selects brains by pass-rate needs many windows x
# 7 seeds. These tests guarantee we run on the cheapest fast device at ~80% load,
# so that budget is affordable and no paid GPU is wasted on a 3x256 MLP.
# =============================================================================
def test_representative_policy_matches_locked_architecture():
    """The benchmark net must mirror the locked four-head 3x256 design.

    FTMO link: an honest device race must time the REAL workload shape (direction
    {HOLD,OPEN_LONG,OPEN_SHORT,CLOSE} + Beta size + 5-slot pointer + value), or we
    might pick a device that is slower for the actual policy and waste training time.
    """
    import torch

    net = RepresentativePolicy(state_dim=145)
    d, s, p, v = net(torch.randn(8, 145))
    assert d.shape == (8, 4)
    assert s.shape == (8, 2)
    assert p.shape == (8, 5)
    assert v.shape == (8, 1)
    linears = [m for m in net.trunk if m.__class__.__name__ == "Linear"]
    assert len(linears) == 3 and all(l.out_features == 256 for l in linears)


def test_cpu_is_always_a_candidate_device():
    devs = available_devices()
    assert devs and devs[0].kind == "cpu", "CPU must be the first/default candidate"


def test_benchmark_reports_positive_throughput():
    results = race_devices(state_dim=64, batch=256, seconds=0.3)
    cpu = next(r for r in results if r.kind == "cpu")
    assert cpu.steps_per_sec > 0


def test_autoscale_targets_80pct_with_headroom():
    """n_envs/threads never exceed (cores - reserved); ~80% target, kernel stays alive."""
    hw = HardwareConfig(utilization_target=0.80, reserved_cores=1)
    sp = plan_cpu_scale(hw)
    cores = os.cpu_count() or 1
    assert hw.min_envs <= sp.n_envs <= hw.max_envs
    assert sp.torch_threads <= max(1, cores - hw.reserved_cores)


def test_plan_prefers_cpu_when_no_accelerator():
    """On a CPU-only box the plan MUST pick CPU (the cheap default) — money guard."""
    import torch

    p = plan(state_dim=RuntimeConfig().nominal_state_dim, benchmark_seconds=0.3)
    assert p.n_envs >= 1
    if not torch.cuda.is_available():
        assert p.device_kind == "cpu" and p.device == "cpu"


def test_challenge_defaults_are_the_locked_ftmo_values():
    """Defaults must be 2.5%/4.0% (SOW-A3). A wrong default silently trains/judges
    against the wrong wall, so every 'pass' would be meaningless."""
    c = RuntimeConfig().challenge
    assert c.daily_target_pct == 2.5
    assert c.daily_risk_pct == 4.0
    assert c.phase_b_trailing_pct == 1.0
    assert c.hard_wall_pct == 4.0


# =============================================================================
# SECTION B — DATA PIPELINE: LOADER
# FTMO link: the bot can only learn to pass the challenge it is shown. Faithful
# bars (correct stamps, real spread, deduped, monotonic) are the ground truth the
# laws, costs, and risk walls all read.
# =============================================================================
def test_parse_tab_delimited_mt5_export(make_1m, write_mt5_csv):
    df = make_1m(n_bars=600, seed=1)
    parsed, meta = parse_mt5_csv(write_mt5_csv(df, sep="\t"))
    assert list(parsed.columns) == OHLCV_COLUMNS
    assert meta["delimiter"] == "\t" and meta["had_spread"] is True
    assert parsed.index.is_monotonic_increasing and len(parsed) == 600
    assert abs(parsed["close"].iloc[-1] - df["close"].iloc[-1]) < 1e-4


def test_parse_comma_delimited_variant(make_1m, write_mt5_csv):
    parsed, meta = parse_mt5_csv(write_mt5_csv(make_1m(n_bars=200, seed=2), sep=","))
    assert meta["delimiter"] == "," and len(parsed) == 200


def test_parser_drops_duplicate_timestamps(make_1m, write_mt5_csv):
    df = make_1m(n_bars=100, seed=3)
    dup = pd.concat([df, df.iloc[:10]]).sort_index()
    parsed, meta = parse_mt5_csv(write_mt5_csv(dup, sep="\t"))
    assert meta["dropped_duplicates"] == 10 and parsed.index.is_unique


def test_load_symbol_local_source(make_1m, write_mt5_csv):
    out, rep = load_symbol("EURUSD", path=write_mt5_csv(make_1m(n_bars=150, seed=4)),
                           use_cache=False)
    assert rep.rows == 150 and rep.source == "local"
    assert list(out.columns) == OHLCV_COLUMNS


def test_parquet_cache_used_on_second_load(make_1m, write_mt5_csv, monkeypatch):
    """Efficiency: first load parses CSV + writes Parquet; second reads the cache.

    FTMO link: cheap re-loads are what make many walk-forward windows affordable;
    a broken cache would 10x the cost of establishing a pass rate.
    """
    name = cfg.DRIVE_FILENAMES["EURUSD"]
    path = write_mt5_csv(make_1m(n_bars=300, seed=11), name=name)
    monkeypatch.setattr(cfg, "RAW_DIR", path.parent)
    monkeypatch.setattr(cfg, "PARQUET_DIR", path.parent)
    out1, rep1 = load_symbol("EURUSD")
    out2, rep2 = load_symbol("EURUSD")
    assert rep1.source == "local" and rep2.source == "cache"
    assert len(out1) == len(out2) == 300
    assert (cfg.PARQUET_DIR / "EURUSD_1m.parquet").exists()


def test_parse_throughput_is_reasonable(make_1m, write_mt5_csv):
    """Efficiency guard: parsing 20k bars must not regress into minutes.

    FTMO link: the offline data step must stay cheap so iteration time (and cost)
    per validated seed stays low. Bound is generous — it only catches pathologies.
    """
    path = write_mt5_csv(make_1m(n_bars=20_000, seed=12))
    t0 = time.perf_counter()
    parsed, _ = parse_mt5_csv(path)
    assert len(parsed) == 20_000
    assert (time.perf_counter() - t0) < 10.0


# =============================================================================
# SECTION C — DATA PIPELINE: RESAMPLER (NO LOOKAHEAD)
# FTMO link: lookahead is the deadliest trading-RL bug. A bot that peeks at an
# unfinished 5m/30m/4H bar learns a fantasy edge that vanishes live and walks into
# the 4% wall. These tests make peeking structurally impossible.
# =============================================================================
def test_resample_5m_ohlc_aggregation(make_1m):
    df = make_1m(n_bars=60, seed=5, start="2021-01-04 00:00:00")
    five = resample_ohlcv(df, "5min")
    block = df.iloc[0:5]
    assert five.index[0] == pd.Timestamp("2021-01-04 00:05:00")  # close-time stamp
    assert five.iloc[0]["open"] == block["open"].iloc[0]
    assert five.iloc[0]["high"] == block["high"].max()
    assert five.iloc[0]["low"] == block["low"].min()
    assert five.iloc[0]["close"] == block["close"].iloc[-1]
    assert five.iloc[0]["tick_volume"] == block["tick_volume"].sum()


def test_build_all_timeframes_keys(make_1m):
    assert set(build_all_timeframes(make_1m(n_bars=1000, seed=6))) == {"1m", "5m", "30m", "4H"}


def test_as_of_merge_has_no_lookahead(make_1m):
    df = make_1m(n_bars=120, seed=7)
    five = resample_ohlcv(df, "5min")
    merged = as_of_higher_tf(df.index, five, suffix="5m")
    for t in [df.index[3], df.index[7], df.index[42], df.index[99]]:
        val = merged.loc[t, "close_5m"]
        eligible = five[five.index <= t]
        if eligible.empty:
            assert pd.isna(val)
        else:
            assert val == eligible["close"].iloc[-1]  # last CLOSED bar only


# Allow `python tests/test_ftmo_master_suite.py` to run the whole suite directly.
if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))


# ─────────────────────────────────────────────────────────────────────────────
# UPDATE LOG (IRAC) — standing rule since 2026-06-13.
# Every change APPENDS a dated IRAC entry (newest last). Conclusion is ALWAYS why
# the change makes the bot pass FTMO more consistently with no bug/inefficiency.
# Rulebook: docs/MLP_INTERPRETABILITY_LAYER.md
# ─────────────────────────────────────────────────────────────────────────────
# [2026-06-13] Created the single master suite (hardening pass).
#   I: Tests were split across test_runtime.py + test_data_pipeline.py; the operator
#      wanted ONE runnable suite, and future milestones risked fragmenting tests.
#   R: New standing rule — one master suite all future tests append to; every guard
#      framed against repeated FTMO passing (SOW Section 11 acceptance tests).
#   A: Consolidated all runtime + data-pipeline tests here under chain-ordered
#      sections (A runtime, B loader, C resampler); added efficiency/caching guards
#      (parquet-cache reuse, parse throughput); deleted the two old test files.
#   C: A single green command now proves the training substrate is faithful and
#      cheap, so we can afford the seeds/windows that establish a reproducible pass
#      rate — and the LLM can rule the substrate out first when triangulating.
