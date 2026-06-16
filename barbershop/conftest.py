# ==========================================================================
# FILE: barbershop/conftest.py
# PURPOSE: Pytest setup for the Barbershop test suite. Puts the repo root on
#          sys.path so `import barbershop...` resolves when tests are run via
#          `pytest barbershop/`, and provides shared fixtures that build the
#          SYNTHETIC MOCK telemetry + price data every test runs against
#          (no real training run required — spec Section 5).
# ==========================================================================
#
# DEPENDS ON: barbershop.data (mock generators)
# PRODUCES: nothing persistent — fixtures write only into pytest tmp_path.
#
# UPDATE LOG — every change to this file must be logged here:
#   [2026-06-15] [Claude] — First build. Repo-root sys.path + mock-data fixtures
#                            (trajectory, shap, prices, 4-day scoreboard).
# ==========================================================================

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Repo root on sys.path so `import barbershop.*` works under `pytest barbershop/`.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from barbershop import data  # noqa: E402  (after sys.path is set)


@pytest.fixture
def mock_trajectory():
    """A deterministic 4-day mock trajectory DataFrame (spec data contract).

    Returns: pandas DataFrame with every column from Section 4, covering 4 days
    (2 pass, 2 fail) with one DD-breached day — ready for scoreboard/replay tests.
    """
    return data.make_mock_trajectory(seed=0)


@pytest.fixture
def mock_shap():
    """Deterministic mock SHAP DataFrame matching the mock trajectory's trades."""
    return data.make_mock_shap(seed=0)


@pytest.fixture
def mock_prices():
    """Deterministic per-timeframe mock price frames {tf: DataFrame}."""
    return data.make_mock_prices(seed=0)


@pytest.fixture
def barbershop_tmp(tmp_path, monkeypatch):
    """Redirect every Barbershop read/write path into an isolated tmp dir.

    Reads: nothing. Writes the mock data files into tmp_path and repoints the
    config path constants at them, so tests never touch the real repo files and
    concurrent test runs can't collide. Returns the tmp Path.
    """
    from barbershop import config

    logs = tmp_path / "logs"; logs.mkdir()
    data_dir = tmp_path / "data"; data_dir.mkdir()
    docs = tmp_path / "docs"; docs.mkdir()
    # Repoint the write/read targets at the isolated tmp tree.
    monkeypatch.setattr(config, "LOGS_DIR", logs)
    monkeypatch.setattr(config, "DATA_DIR", data_dir)
    monkeypatch.setattr(config, "SUGGESTED_RULES_JSON", logs / "suggested_rules.json")
    monkeypatch.setattr(config, "DOCTOR_DIAGNOSES_JSONL", logs / "doctor_diagnoses.jsonl")
    monkeypatch.setattr(config, "TRAJECTORY_PARQUET", logs / "trajectory.parquet")
    monkeypatch.setattr(config, "SHAP_PARQUET", logs / "shap_values.parquet")
    return tmp_path
