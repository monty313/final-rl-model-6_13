# ==========================================================================
# FILE: barbershop/dashboard.py
# PURPOSE: Visual diagnostics dashboard for the Quantra PPO trading bot.
#          Monty uses this AFTER training to understand why the bot acted
#          the way it did and to write generalised reward/penalty rules.
#          This file is READ-ONLY — it cannot change training or the policy.
# ==========================================================================
#
# DEPENDS ON (reads from these files/modules):
#   data/prices_1m.csv          — 1m EURUSD candles
#   data/prices_5m.csv          — 5m EURUSD candles
#   data/prices_30m.csv         — 30m EURUSD candles
#   data/prices_4h.csv          — 4H EURUSD candles
#   logs/trajectory.parquet     — bot action/state/reward log (from telemetry/logger.py)
#   logs/shap_values.parquet    — SHAP attributions per trade step (from telemetry/interpreter.py)
#   models/ppo_actor.pt         — frozen actor weights for SHAP (from ppo/trainer.py)
#   (the REAL pipeline writes artifacts/telemetry/<run_id>.jsonl; barbershop/adapter.py
#    maps it onto the contract above and flags the fields it cannot yet produce.)
#
# DEPENDED ON BY (these read what this file produces):
#   logs/suggested_rules.json   — pattern finder + Doctor export (read by Monty manually)
#   NOTHING ELSE — this is a terminal tool, not a pipeline component
#
# RELATED BLUEPRINT FILES (read these to understand the terms used here):
#   docs/MLP_INTERPRETABILITY_LAYER.md — hidden state, SHAP, action distribution,
#                                        advantage, value estimate
#   docs/STATE_VECTOR.md               — every feature name and group
#   docs/THE_TRADING_CODE.md           — the 9 laws and 3 gates
#   docs/REWARD_DESIGN.md              — reward layers referenced in advantage
#   docs/PPO_ENGINE.md                 — actor/critic architecture
#
# RULE 3 (READ ONLY): this file only ever WRITES under logs/ (the pattern/Doctor
# export). It never writes to models/, ppo/, env/, or quantra/, and never calls
# the live actor — only frozen weights for SHAP.
#
# UPDATE LOG — every change to this file must be logged here:
#   [2026-06-15] [Claude] — First build. All 5 screens implemented per
#                            Quantra Barbershop spec v1.0 + Risk Doctor chat box.
# ==========================================================================

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from dash import ALL, Dash, Input, Output, State, ctx, dcc, html

from barbershop import config, data, doctor_chat, figures, risk_doctor


# ==========================================================================
# DATA LOADING — fail loud on a missing required file (RULE 4), else fall back
# to deterministic mock data so `python barbershop/dashboard.py` runs out of the
# box with no training run.
# ==========================================================================
def load_bundle(use_mock: bool = True) -> Dict[str, Any]:
    """Load everything the screens need (trajectory, shap, prices, training wall).

    Reads: the logs/ + data/ files when use_mock is False; otherwise builds
    deterministic mock data. Returns a dict bundle. With use_mock=False a missing
    file raises data.MissingDataFile, which the caller turns into a red banner.
    """
    if use_mock:
        traj = data.make_mock_trajectory()
        shap = data.make_mock_shap()
        prices = data.make_mock_prices()
    else:
        traj = data.load_trajectory()
        shap = data.load_shap()
        prices = {tf: data.load_prices(tf) for tf in config.TIMEFRAMES}
    return {"trajectory": traj, "shap": shap, "prices": prices,
            "training_wall": _mock_training_wall()}


def _mock_training_wall(n: int = 40) -> Dict[str, List[float]]:
    """Synthesise a rising-then-plateauing pass-rate curve for Screen 1 mock mode."""
    rng = np.random.default_rng(1)
    iters = list(range(0, n * 500, 500))
    # Rise toward ~82% then flatten (so the plateau banner can demonstrate).
    base = 82 * (1 - np.exp(-np.linspace(0, 3, n)))
    rate = list(np.clip(base + rng.normal(0, 1.5, n), 0, 100))
    return {"iterations": iters, "pass_rate": [float(x) for x in rate]}


def error_banner(exc: "data.MissingDataFile") -> html.Div:
    """Build the red FAIL-LOUD banner naming the missing file + its producer (RULE 4).

    Reads: a MissingDataFile exception. Returns an html.Div clearly stating WHICH
    file is missing and WHAT module produces it — never a silent empty chart.
    """
    return html.Div([
        html.B("⚠️ Required data file missing"),
        html.Div(f"File: {exc.path}"),
        html.Div(f"Produced by: {exc.producer}"),
    ], style={"background": config.COLOR_RED, "color": "#fff", "padding": "12px",
              "borderRadius": "8px", "margin": "8px 0", "whiteSpace": "pre-line"})


# ==========================================================================
# SCREEN BUILDERS — each returns a Dash component tree from the data bundle.
# ==========================================================================
def screen_training_wall(bundle: Dict[str, Any]) -> html.Div:
    """Screen 1 — the live training-wall pass-rate chart + status panel + plateau banner."""
    tw = bundle["training_wall"]
    fig = figures.training_wall_figure(tw["iterations"], tw["pass_rate"])
    plateau = figures.is_plateaued(tw["pass_rate"])
    children = [
        html.H3("Screen 1 — Training Wall"),
        dcc.Graph(id="training-wall-graph", figure=fig),
        # Live refresh every 60s (spec). Disabled in mock mode would still tick;
        # the callback simply rebuilds the (mock) curve.
        dcc.Interval(id="training-wall-interval", interval=config.TRAINING_WALL_REFRESH_MS),
        html.Div([
            html.Span(f"Current iteration: {tw['iterations'][-1]:,}  |  "),
            html.Span(f"Best pass rate: {max(tw['pass_rate']):.1f}%  |  "),
            html.Span("Last checkpoint: (mock)"),
        ], style={"padding": "6px"}),
    ]
    if plateau:
        children.append(html.Div(
            "⚠️ Policy plateau detected — go to Day Scoreboard to investigate",
            id="plateau-banner",
            style={"background": config.COLOR_YELLOW, "padding": "10px",
                   "fontWeight": "bold", "borderRadius": "6px"}))
    return html.Div(children)


def screen_scoreboard(bundle: Dict[str, Any]) -> html.Div:
    """Screen 2 — four day cards, sorted worst (DD breached) first; click to replay."""
    cards = data.day_scoreboard(bundle["trajectory"])
    card_divs = [_scoreboard_card(c) for c in cards]
    return html.Div([
        html.H3("Screen 2 — 4-Day Scoreboard"),
        html.Div(card_divs, style={"display": "flex", "gap": "12px"}),
    ])


def _scoreboard_card(card: Dict[str, Any]) -> html.Div:
    """Build one scoreboard card (PASS/FAIL badge, DD status, regime, P&L, trades)."""
    badge = "PASS ✅" if card["passed"] else "FAIL ❌"
    dd_icon = {"Safe": "Safe", "Warning": "Warning", "Breached": "Breached 🚨"}[card["dd_status"]]
    highlight = card["dd_status"] == "Breached"            # worst day -> red highlight
    return html.Div([
        html.H4(f"Day {card['day_id']} — {card['regime']}"),
        html.Div(f"P&L: {card['pnl_pct']:+.2f}%"),
        html.Div(badge),
        html.Div(f"DD Wall: {dd_icon}"),
        html.Div(f"Trades: {card['n_trades']}"),
    ], id={"type": "scoreboard-card", "index": card["day_id"]}, n_clicks=0,
        style={"flex": "1", "padding": "12px", "borderRadius": "8px", "cursor": "pointer",
               "border": f"2px solid {config.COLOR_RED if highlight else config.COLOR_GREY}",
               "background": "rgba(224,83,61,0.08)" if highlight else "transparent"})


def screen_day_replay(bundle: Dict[str, Any], day_id: int, tf: str = "1m",
                      trade_id: Optional[int] = None) -> html.Div:
    """Screen 3 — candlestick replay for one day/TF, with the 1m-only sub-panels.

    Reads: the bundle + selected day/TF. Returns the TF buttons + candlestick
    (with trade overlays) + (on 1m only) the advantage strip + indicator heatmap.
    """
    traj = bundle["trajectory"]
    trades = data.extract_trades(traj, day_id)
    # Centre the window on the selected trade's entry (or the first trade / day start).
    if trade_id is not None and 1 <= trade_id <= len(trades):
        entry = trades[trade_id - 1]["entry_time"]
    elif trades:
        entry = trades[0]["entry_time"]
    else:
        entry = traj[traj["day_id"] == day_id]["timestamp"].iloc[0]
    window = data.timeframe_window(entry, tf)
    # DD breach marker (if this day breached, mark the last breached bar).
    day_rows = traj[traj["day_id"] == day_id]
    breach_time = (day_rows[day_rows["dd_breached"]]["timestamp"].iloc[-1]
                   if day_rows["dd_breached"].any() else None)
    candle = figures.candlestick_figure(bundle["prices"][tf], trades, tf, entry,
                                        window=window, dd_breach_time=breach_time)
    children = [
        html.H3(f"Screen 3 — Day {day_id} Replay"),
        _tf_buttons(tf),
        dcc.Graph(id="replay-candles", figure=candle),
    ]
    # Panels 2 + 3 are 1m-only (spec).
    if tf == "1m":
        adv = data.advantage_series(traj, day_id)
        children.append(dcc.Graph(id="replay-advantage",
                                  figure=figures.advantage_figure(adv, window=window)))
        grouped = [data.group_indicators(r) for _, r in day_rows.sort_values("timestamp").iterrows()]
        ts = list(day_rows.sort_values("timestamp")["timestamp"])
        children.append(dcc.Graph(id="replay-heatmap",
                                  figure=figures.heatmap_figure(grouped, ts)))
    return html.Div(children)


def _tf_buttons(active: str) -> html.Div:
    """Build the [1m][5m][30m][4H] timeframe buttons; the active one is highlighted."""
    return html.Div([
        html.Button(tf, id={"type": "tf-button", "index": tf}, n_clicks=0,
                    style={"marginRight": "6px", "fontWeight": "bold" if tf == active else "normal",
                           "border": f"2px solid {config.COLOR_GOLD if tf == active else config.COLOR_GREY}"})
        for tf in config.TIMEFRAMES
    ], style={"margin": "6px 0"})


def screen_autopsy(bundle: Dict[str, Any], day_id: int, trade_id: int) -> html.Div:
    """Screen 4 — trade autopsy: SAW | chose | caused, side by side (right panel)."""
    traj = bundle["trajectory"]
    trades = data.extract_trades(traj, day_id)
    if not (1 <= trade_id <= len(trades)):
        return html.Div("Select a trade marker to open the autopsy.")
    tr = trades[trade_id - 1]
    # The decision row = the trade's entry row.
    entry_rows = traj[(traj["day_id"] == day_id) & (traj["timestamp"] == tr["entry_time"])]
    row = entry_rows.iloc[0]
    groups = data.group_indicators(row)
    bars = data.action_probability_bars(row)
    masked, legal = data.masked_legal(row)
    # SHAP for this trade step.
    shap_df = bundle["shap"]
    srows = shap_df[(shap_df["day_id"] == day_id) & (shap_df["step"] == int(row["step"]))]
    if len(srows):
        ss = data.shap_sorted(srows.iloc[0], row["action"])
    else:
        ss = {"chosen_action": row["action"], "toward": [], "away": [], "explained": 0.0}

    left = html.Div([html.H4("What the bot SAW"),
                     html.Small(str(tr["entry_time"])),
                     dcc.Graph(figure=figures.state_bars_figure(groups))],
                    style={"flex": "1"})
    middle = html.Div([html.H4("Why it chose this action"),
                       dcc.Graph(figure=figures.action_prob_figure(bars)),
                       html.Div(f"LEGAL: {', '.join(legal)}"),
                       html.Div(f"MASKED: {', '.join(masked) or 'none'}",
                                style={"color": config.COLOR_RED})],
                      style={"flex": "1"})
    right = html.Div([html.H4("What CAUSED that probability"),
                      dcc.Graph(figure=figures.shap_figure(ss))],
                     style={"flex": "1"})
    return html.Div([html.H3(f"Screen 4 — Trade #{trade_id} Autopsy (Day {day_id})"),
                     html.Div([left, middle, right], style={"display": "flex", "gap": "10px"})])


def screen_pattern_finder(bundle: Dict[str, Any]) -> html.Div:
    """Screen 5 — auto-scan losing trades, surface top 3 patterns, apply/ignore/modify."""
    losing = data.losing_trades(bundle["trajectory"])
    # When the trajectory has too few losers to mine, demonstrate on the mock set.
    if len(losing) < 3:
        losing = data.make_mock_losing_trades()
    patterns = data.find_patterns(losing)
    blocks = [_pattern_block(p) for p in patterns]
    return html.Div([html.H3("Screen 5 — Pattern Finder")] + blocks)


def _pattern_block(p: Dict[str, Any]) -> html.Div:
    """Build one pattern card with the plain-English finding + Apply/Ignore/Modify."""
    return html.Div([
        html.H4(f"Pattern {p['rank']} — Found in {p['count']} of {p['total']} losing trades"),
        html.Ul([html.Li(c) for c in p["conditions"]]),
        html.Div(html.B("Suggested rule: ")),
        html.Div(p["suggested_rule"]),
        html.Div([
            html.Button("✅ APPLY RULE", id={"type": "pattern-apply", "index": p["rank"]}, n_clicks=0),
            html.Button("❌ IGNORE", id={"type": "pattern-ignore", "index": p["rank"]}, n_clicks=0),
            html.Button("✏️ MODIFY", id={"type": "pattern-modify", "index": p["rank"]}, n_clicks=0),
        ], style={"marginTop": "6px"}),
        dcc.Input(id={"type": "pattern-text", "index": p["rank"]}, value=p["suggested_rule"],
                  style={"width": "90%", "display": "none"}),
    ], style={"border": f"1px solid {config.COLOR_GREY}", "borderRadius": "8px",
              "padding": "10px", "margin": "8px 0"})


# ==========================================================================
# THE APP.
# ==========================================================================
def make_app(use_mock: bool = True) -> Dash:
    """Build the Dash app: tab nav over the 5 screens + the Risk Doctor chat box.

    Reads: the data bundle (mock by default). Returns a configured Dash app with
    all callbacks registered. RULE 3: nothing here writes outside logs/.
    """
    app = Dash(__name__, suppress_callback_exceptions=True)
    init_state = {"screen": 1, "day_id": None, "trade_id": None, "tf": "1m", "use_mock": use_mock}

    app.layout = html.Div([
        dcc.Store(id="screen-state", data=init_state),
        html.H2("Quantra Barbershop — training diagnostics"),
        dcc.Tabs(id="screen-tabs", value="s1", children=[
            dcc.Tab(label="1 · Training Wall", value="s1"),
            dcc.Tab(label="2 · Scoreboard", value="s2"),
            dcc.Tab(label="3 · Day Replay", value="s3"),
            dcc.Tab(label="4 · Trade Autopsy", value="s4"),
            dcc.Tab(label="5 · Pattern Finder", value="s5"),
        ]),
        html.Div(id="screen-content"),
        doctor_chat.chat_panel(init_state),
    ], style={"fontFamily": "system-ui, sans-serif", "padding": "12px"})

    _register_callbacks(app)
    return app


def _content_for(state: Dict[str, Any]) -> html.Div:
    """Render the active screen, catching a missing-file error into a red banner."""
    try:
        bundle = load_bundle(use_mock=state.get("use_mock", True))
    except data.MissingDataFile as exc:
        return error_banner(exc)                          # RULE 4 — fail loud
    screen = state.get("screen", 1)
    if screen == 1:
        return screen_training_wall(bundle)
    if screen == 2:
        return screen_scoreboard(bundle)
    if screen == 3:
        return screen_day_replay(bundle, state.get("day_id") or 1,
                                 state.get("tf", "1m"), state.get("trade_id"))
    if screen == 4:
        if state.get("day_id") is None or state.get("trade_id") is None:
            return html.Div("Click a trade marker on Screen 3 to open the autopsy.")
        return screen_autopsy(bundle, state["day_id"], state["trade_id"])
    if screen == 5:
        return screen_pattern_finder(bundle)
    return html.Div("Unknown screen.")


def _register_callbacks(app: Dash) -> None:
    """Wire every interaction (tab/card/TF/trade nav, pattern apply, Doctor chat)."""

    # --- Navigation: tab change -> screen number -> rebuild content. ---
    @app.callback(Output("screen-state", "data"),
                  Output("screen-content", "children"),
                  Input("screen-tabs", "value"),
                  Input({"type": "scoreboard-card", "index": ALL}, "n_clicks"),
                  Input({"type": "tf-button", "index": ALL}, "n_clicks"),
                  Input("replay-candles", "clickData"),
                  State("screen-state", "data"))
    def navigate(tab, card_clicks, tf_clicks, candle_click, state):
        state = dict(state or {})
        trig = ctx.triggered_id
        if trig == "screen-tabs":
            state["screen"] = int(str(tab)[-1])
        elif isinstance(trig, dict) and trig.get("type") == "scoreboard-card":
            state.update(screen=3, day_id=int(trig["index"]), trade_id=None, tf="1m")
        elif isinstance(trig, dict) and trig.get("type") == "tf-button":
            state["tf"] = trig["index"]; state["screen"] = 3
        elif trig == "replay-candles" and candle_click:
            # A trade marker click carries customdata=trade_id -> open the autopsy.
            pts = candle_click.get("points", [{}])
            cd = pts[0].get("customdata")
            if cd is not None:
                tid = cd[0] if isinstance(cd, list) else cd
                state.update(screen=4, trade_id=int(tid))
        return state, _content_for(state)

    # --- Screen 1 live refresh (rebuild the training-wall curve). ---
    @app.callback(Output("training-wall-graph", "figure"),
                  Input("training-wall-interval", "n_intervals"),
                  prevent_initial_call=True)
    def refresh_wall(_n):
        tw = _mock_training_wall()
        return figures.training_wall_figure(tw["iterations"], tw["pass_rate"])

    # --- Doctor: expand/collapse the chat panel. ---
    @app.callback(Output("doctor-body", "style"),
                  Input("doctor-toggle", "n_clicks"),
                  State("doctor-body", "style"))
    def toggle_doctor(n, style):
        style = dict(style or {})
        style["display"] = "none" if (n or 0) % 2 == 1 else "block"
        return style

    # --- Doctor: context indicator follows navigation (spec TEST 15). ---
    @app.callback(Output("doctor-context-indicator", "children"),
                  Input("screen-state", "data"))
    def update_context(state):
        return doctor_chat.context_indicator_text(state or {})

    # --- Doctor: send a message / full diagnosis -> append to the conversation. ---
    @app.callback(Output("doctor-conversation", "children"),
                  Input("doctor-send", "n_clicks"),
                  Input("doctor-full-diagnosis", "n_clicks"),
                  State("doctor-input", "value"),
                  State("doctor-conversation", "children"),
                  State("screen-state", "data"),
                  prevent_initial_call=True)
    def doctor_send(send_n, full_n, question, convo, state):
        convo = list(convo or [])
        full = ctx.triggered_id == "doctor-full-diagnosis"
        q = question or ("Give me a full diagnosis of this day." if full else "")
        if not q:
            return convo
        try:
            bundle = load_bundle(use_mock=(state or {}).get("use_mock", True))
            traj, shap = bundle["trajectory"], bundle["shap"]
        except data.MissingDataFile:
            traj = shap = None
        resp = risk_doctor.ask(q, state or {}, trajectory=traj, shap=shap, full_diagnosis=full)
        convo.append(doctor_chat.render_user_message(q))
        if resp.get("offline") or resp.get("manual_missing"):
            convo.append(doctor_chat.render_offline_banner(resp["text"]))
        else:
            convo.append(doctor_chat.render_doctor_message(resp, msg_id=len(convo)))
        return convo


# Entry point: `python barbershop/dashboard.py` -> open http://localhost:8050.
if __name__ == "__main__":          # pragma: no cover (manual launch only)
    make_app(use_mock=True).run(host=config.DASH_HOST, port=config.DASH_PORT, debug=False)
