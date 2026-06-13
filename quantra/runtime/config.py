"""Quantra runtime configuration — the single source of runtime knobs.

WHAT THIS MODULE DOES
---------------------
Holds the runtime-memory inputs and infrastructure constants Quantra needs at
launch: the FTMO challenge defaults, the four traded symbols, the Google-Drive
file IDs for the price data, filesystem paths, and the hardware-utilisation
targets used by the rest of ``quantra.runtime``.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
Per SOW Section 1.4 the policy is *account-size-blind* and takes its targets as
**pure runtime memory** (no saved config file dictating strategy). This module is
that runtime memory: ``daily_target_pct`` (2.5) and ``daily_risk_pct`` (4.0) are
the very constraints the bot is being trained to respect on every window. Keeping
them here — never hardcoded inside laws, rewards, or the env — is what lets the
same brain be pointed at a different target/loss pair without retraining, which is
the whole point of "repeatedly pass FTMO-style challenges over time".

The hardware section exists so training cycles are cheap and fast: we want to
*finish* walk-forward windows, not burn paid GPU hours on a tiny MLP. Faster,
cheaper iterations = more seeds, more windows, a better-validated pass rate.

LLM RISK DOCTOR — HOW TO THINK ABOUT THIS FILE
----------------------------------------------
Binding rulebook: ``docs/MLP_INTERPRETABILITY_LAYER.md``. If you (the Risk Doctor)
see a diagnosis that depends on the daily target / loss / account size, read those
values FROM the telemetry packet's run-config block, NOT from this file — at
inference the operator may have passed different runtime values. This file only
provides the *defaults* (SOW-A3) and the immutable infrastructure constants.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List


# ---------------------------------------------------------------------------
# Filesystem layout. Everything Quantra writes (data cache, checkpoints,
# telemetry, reports) hangs off the repo root so a Colab run and a local run
# behave identically.
# ---------------------------------------------------------------------------
REPO_ROOT: Path = Path(__file__).resolve().parents[2]
DATA_DIR: Path = REPO_ROOT / "data"
RAW_DIR: Path = DATA_DIR / "raw"            # original MT5 CSV exports
PARQUET_DIR: Path = DATA_DIR / "parquet"    # cleaned, UTC-indexed bars
FEATURE_CACHE_DIR: Path = DATA_DIR / "features"  # memmapped precomputed features
ARTIFACT_DIR: Path = REPO_ROOT / "artifacts"
CHECKPOINT_DIR: Path = ARTIFACT_DIR / "checkpoints"
TELEMETRY_DIR: Path = ARTIFACT_DIR / "telemetry"
REPORT_DIR: Path = ARTIFACT_DIR / "reports"
DOCS_DIR: Path = REPO_ROOT / "docs"

# The interpretability rulebook the LLM Risk Doctor MUST be able to read
# (MLP_INTERPRETABILITY_LAYER.md §"the codebase should fail loudly if the LLM is
# invoked without that file being accessible"). Referenced here so a single
# constant locates it for every module.
INTERPRETABILITY_RULEBOOK: Path = DOCS_DIR / "MLP_INTERPRETABILITY_LAYER.md"


# ---------------------------------------------------------------------------
# Symbols + their Google-Drive price-data file IDs (folder `rl-trading-data`,
# owner mmayes313@gmail.com). The data_loader (M1) resolves bars in this order:
# explicit local path -> Colab Drive mount -> gdown by these IDs.
# ---------------------------------------------------------------------------
SYMBOLS: List[str] = ["EURUSD", "XAUUSD", "GBPUSD", "US30"]  # SOW §12.1 order

# Asset class drives the cost model (SOW §10.5): forex pays $5/RT/lot; metals &
# indices pay no per-trade commission (spread + slippage only).
ASSET_CLASS: Dict[str, str] = {
    "EURUSD": "forex",
    "GBPUSD": "forex",
    "XAUUSD": "metal",
    "US30": "index",
}

DRIVE_FILE_IDS: Dict[str, str] = {
    "EURUSD": "1tsR789vdRYE4rwDAE-hreWF2zN1slcjH",
    "GBPUSD": "1503qJQxjLwA2O0zIiakiOM_68Ucb-ypm",
    "XAUUSD": "1bzICq5oXh3z5PIwrovDa8xUHwRV-d8Gz",
    "US30": "1YF3vr4gBAm-4PZPLGCG0plWPDSaXH14h",
}

# Original Drive filenames (for Colab Drive-mount resolution, where we look the
# file up by name under the mounted `rl-trading-data` folder rather than by ID).
DRIVE_FILENAMES: Dict[str, str] = {
    "EURUSD": "EURUSD_M1_202101131130_202605270000_2020_2026.csv",
    "GBPUSD": "GBPUSD_M1_202101131952_202605270000.csv",
    "XAUUSD": "XAUUSD_M1_202009230753_202605262259.csv",
    "US30": "US30_M1_202007231046_202605262359.csv",
}
DRIVE_FOLDER_NAME: str = "rl-trading-data"
DRIVE_FOLDER_ID: str = "1azEnCfwQjxPkBemmv9mxY3GyVAMcjF-3"


@dataclass(frozen=True)
class ChallengeConfig:
    """Runtime FTMO inputs (SOW §1.4, §2.6, §2.7). Defaults per SOW-A3.

    Why frozen: these define *what passing means* on a given run. They must be
    captured verbatim into telemetry so the Risk Doctor judges behaviour against
    the exact target/wall that were in force — never against assumed defaults.
    """

    daily_target_pct: float = 2.5     # Phase-A profit that triggers auto-flat
    daily_risk_pct: float = 4.0       # Phase-A trailing wall
    phase_b_trailing_pct: float = 1.0  # fresh trailing wall after target (SOW §2.6)
    pain_zone_start_pct: float = 3.5  # exponential reward Layer 3 begins here
    hard_wall_pct: float = 4.0        # force-flatten + lockout (SOW §2.7)
    ftmo_mode: bool = True
    ftmo_account_size: float = 10_000.0  # reference scaling only; policy is blind


@dataclass(frozen=True)
class HardwareConfig:
    """Targets for the auto-optimizer (``quantra.runtime.optimizer``).

    The user's instruction: use ~80% of whichever device (CPU or GPU) trains
    fastest, prefer CPU, never waste paid GPU hours on a 3x256 MLP. These knobs
    encode that policy; ``optimizer.plan()`` reads them.
    """

    utilization_target: float = 0.80   # fraction of the chosen device to drive
    prefer_cpu: bool = True            # tie-break / near-tie goes to CPU (cheaper)
    # A GPU must beat CPU throughput by at least this factor to be worth its cost,
    # otherwise we stay on CPU and tell the operator to drop the GPU runtime.
    gpu_speedup_required: float = 1.30
    benchmark_seconds: float = 2.5     # wall-time budget for the startup race
    min_envs: int = 1
    max_envs: int = 256                # safety ceiling on vectorised worlds
    # Leave at least this many logical cores free so Colab stays responsive and
    # the kernel isn't OOM/again-killed.
    reserved_cores: int = 1


@dataclass
class RuntimeConfig:
    """Top-level runtime memory assembled at launch and logged to telemetry."""

    challenge: ChallengeConfig = field(default_factory=ChallengeConfig)
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    symbols: List[str] = field(default_factory=lambda: list(SYMBOLS))
    seed: int = 0

    # Nominal state-vector width for the *startup* benchmark only. The real width
    # is asserted by the FeatureBuilder (M2) against STATE_VECTOR.md (~145). We
    # never let this nominal value leak into training shapes.
    nominal_state_dim: int = 145

    def to_dict(self) -> dict:
        """Flatten for telemetry's run-config block (M9 data contract)."""
        d = asdict(self)
        d["repo_root"] = str(REPO_ROOT)
        return d


def ensure_dirs() -> None:
    """Create all writable directories. Safe to call repeatedly (idempotent).

    Called once at launch so the very first Colab run has somewhere to put the
    parquet cache, checkpoints, and telemetry without manual mkdir.
    """
    for d in (DATA_DIR, RAW_DIR, PARQUET_DIR, FEATURE_CACHE_DIR,
              ARTIFACT_DIR, CHECKPOINT_DIR, TELEMETRY_DIR, REPORT_DIR):
        d.mkdir(parents=True, exist_ok=True)


def in_colab() -> bool:
    """True when running inside a Google Colab kernel.

    Used by the data_loader to prefer a Drive mount and by the optimizer to size
    the utilisation monitor's logging cadence.
    """
    return "google.colab" in os.sys.modules or os.environ.get("COLAB_RELEASE_TAG") is not None


# ─────────────────────────────────────────────────────────────────────────────
# UPDATE LOG (IRAC) - standing rule since 2026-06-13.
# Every change to this file APPENDS a dated IRAC entry below (newest last):
#   I (Issue) / R (Rule) / A (Application) / C (Conclusion -> why this makes the
#   bot pass FTMO MORE CONSISTENTLY, with no bug or inefficiency). The LLM Risk
#   Doctor reads this log to reconstruct the chronological 'why' when
#   triangulating a pass-rate regression. Rulebook: docs/MLP_INTERPRETABILITY_LAYER.md
# ─────────────────────────────────────────────────────────────────────────────
# [2026-06-13] Runtime config documented + pinned by the master suite.
#   I: FTMO target/loss defaults, Drive file IDs and paths had no change-log or test pin.
#   R: SOW-A3 (2.5%/4.0% configurable, never hardcoded strategy) + the new IRAC rule.
#   A: Annotated every constant for its FTMO role; defaults now asserted in the master suite (Section A).
#   C: The bot always trains/judges against the real 2.5%/4% walls, so a 'pass' is reproducible and meaningful.
