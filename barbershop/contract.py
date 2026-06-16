# ==========================================================================
# FILE: barbershop/contract.py
# PURPOSE: The SINGLE source of truth for the Barbershop data contract — the
#          column lists, the action ordering, the engine-int -> action map, and
#          the placeholder fields. The mock generators, the real-telemetry adapter,
#          and the loaders/validators ALL import from here, so the shape can never
#          drift between them (the drift that caused two earlier review bugs).
# ==========================================================================
#
# DEPENDS ON: nothing (pure constants — imported by config, data, adapter).
# PRODUCES:   nothing.
#
# UPDATE LOG — every change to this file must be logged here:
#   [2026-06-16] [Claude] — WI-7 first build. Lifted the contract column lists,
#                            action order, engine-int map, and placeholder fields
#                            out of config/data into one authoritative module.
# ==========================================================================

from __future__ import annotations

# Trajectory.parquet columns (spec Section 4) — the per-step decision record.
TRAJECTORY_COLUMNS: list[str] = [
    "timestamp", "day_id", "step", "action", "action_prob", "all_probs",
    "masked_actions", "advantage", "value_estimate", "reward",
    "pnl_cumulative", "dd_buffer", "trade_open", "trade_direction",
    "trade_pnl", "law_state", "obs_vector", "regime", "pass_result",
    "dd_breached",
]

# Shap_values.parquet columns (spec Section 4) — per trade-step attribution.
SHAP_COLUMNS: list[str] = [
    "timestamp", "day_id", "step", "chosen_action", "shap_toward", "shap_away",
]

# Dashboard action order: probabilities are [long, short, hold, close] (spec Section 4).
ACTIONS: list[str] = ["OPEN_LONG", "OPEN_SHORT", "HOLD", "CLOSE"]

# Live engine integer encoding {HOLD:0, OPEN_LONG:1, OPEN_SHORT:2, CLOSE:3} -> action str.
ENGINE_ACTION_INTS: dict[int, str] = {0: "HOLD", 1: "OPEN_LONG", 2: "OPEN_SHORT", 3: "CLOSE"}

# Contract fields the LIVE telemetry pipeline does not always produce — flagged as
# placeholders so the Doctor / UI never present a NaN as if it were real evidence.
PLACEHOLDER_FIELDS: list[str] = ["advantage", "shap_toward", "shap_away", "regime"]
