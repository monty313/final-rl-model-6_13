# Change-Impact Tracker

A two-tier safety net that makes it impossible to *silently* change the policy's
observation/feature pipeline — because the observation is the bot's entire world,
and a quiet change to it invalidates normalization, the agent input dim, telemetry
labels, and every checkpoint, any of which can erode FTMO pass-rate between runs.

Everything here is **framed against repeated FTMO passing** and is **LLM-readable**
so the Risk Doctor can use it to triangulate a regression. Binding rulebook:
[`docs/MLP_INTERPRETABILITY_LAYER.md`](docs/MLP_INTERPRETABILITY_LAYER.md).

## Tier 1 — State-vector snapshot guard (`tools/snapshot.py`)
The canonical observation layout (dim, blocks, ordered feature names, raw-feature
set, sha) is pinned in [`tests/snapshots/state_vector.json`](tests/snapshots/state_vector.json),
which also carries an `_llm_interpretation` section describing each block and what a
drift implies for passing. The master suite test `test_state_vector_snapshot_matches`
**fails loudly with a concrete checklist** if the live schema differs.

```bash
python tools/snapshot.py --check     # exit 1 on drift (CI / pre-commit)
python tools/snapshot.py --update    # after an INTENDED change, re-pin the snapshot
```

## Tier 2 — AST change-impact analyzer (`tools/impact.py`)
Builds an import graph of `quantra` (resolving relative imports), computes the
**reverse-dependency closure** of changed files (what transitively imports them, and
so may need updating), and prints a static "pipeline file → FTMO follow-ups"
checklist.

```bash
python tools/impact.py quantra/market_pipeline/feature_builder/schema.py
python tools/impact.py --staged      # uses `git diff --cached --name-only`
```

## Enforcement — pre-commit (`.pre-commit-config.yaml`)
```bash
pip install pre-commit && pre-commit install
```
- **Hard gate:** snapshot guard fails the commit on un-re-snapshotted drift.
- **Advisory:** the impact report prints the blast radius + follow-ups.
- Fast master-suite slice (snapshot/impact/schema/config) runs on every commit.

## The follow-up checklist (what a state-vector change requires)
1. If intended, re-snapshot: `python tools/snapshot.py --update`.
2. Verify the PPO agent (M5) reads `STATE_DIM` dynamically — no hardcoded input dim.
3. Regenerate input normalization stats for the **new/changed** features only.
4. Extend `TelemetryLogger` (M9) block labels so the LLM can name the new features.
5. Re-run baseline-vs-candidate walk-forward; promote only via the `PromotionGate`
   (≥3 seeds, scoreboard improvement, no worse breach) — never on raw PnL.
6. Append an IRAC entry to `schema.py`, bump `REPO_MAP`, and run `python tools/impact.py`.

## Update Log (IRAC) — standing rule since 2026-06-13
- **[2026-06-13]** Created the change-impact tracker.
  - **I:** Observation/pipeline changes could ripple undetected and silently degrade pass-rate.
  - **R:** Operator request for a change-impact tracking system with LLM-readable, FTMO-framed I/O.
  - **A:** Built Tier 1 snapshot guard + Tier 2 AST analyzer + pre-commit + master-suite Section E.
  - **C:** The bot's world can no longer change by accident; intended changes carry a concrete,
    LLM-readable follow-up list — keeping observation, code, and checkpoints in sync, which is
    what protects consistent FTMO passing.
