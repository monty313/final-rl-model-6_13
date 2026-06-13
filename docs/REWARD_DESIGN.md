# REWARD DESIGN
### The Scoreboard — What "Winning" Means to the Bot
*Laws run before. Reward governs the legal space. The bot must never win the reward game while losing the trading game.*

**Status key:** 🔴 Locked | 🟡 Suggested | ❓ Open / Parked
**Origin key:** [M] = Monty | [P] = Perplexity adopted | [C] = Claude bridge
**Repo:** https://github.com/monty313/Qunatra_Deep-Reinforcement-Learning-in-Trading.git

---

## NORTH STAR 🔴 [M — SOW-A1 answered]
One universal policy. Job: trade in a way that **repeatedly passes FTMO-style constraints over time**, not chase raw PnL.
- `ftmo_mode` input: ON = enforce daily-target behavior + challenge-style stopping. OFF = keep trading after target, but DAILY_RISK trailing wall still hard-stops.
- DAILY_TARGET (default 2.5%) and DAILY_RISK (default 4% trailing) = configurable inputs, never hardcoded (SOW-A3).

## THE PROGRESSIVE STANCE 🔴 [M]
Laws remove bad actions → the failure mode shifts. **Stagnation is the new failure.** Flat or frozen inside a favorable legal state is a negative signal.

---

## THE LAYERED REWARD — ALL LAYERS ANSWERED 🔴/🟡

```
r(t) = Layer0_ΔNetPnL  + α·L1_momentum − β·L2_stagnation − δ·L3_painzone
     + ε·L4_target_progress  ×  L5_category_weighting  + L6_daily_bonus(EOD: E7 streak + E9 QUAD)
```

### Layer 0 — Outcome Engine 🔴 (E1)
Per-bar net PnL after costs, realized + unrealized, **plus an explicit closed-trade realization event** so actor and critic clearly register what a close actually made or lost. Base anchor; subordinate to the FTMO objective (no breach, efficient progress).

### Layer 1 — Momentum Bonus 🔴 logic / 🟡 α (E2)
Momentum continuation = **small CCI back in sync with the bigger CCIs in trade direction AND ATR above its shifted reference** (move aligned AND alive). Small positive bonus only while a position is open and BOTH are true. α small — Layer 0 stays dominant.

### Layer 2 — Stagnation Penalty 🔴 logic / 🟡 β (E3)
Stagnation = in a favorable legal state, **no equity/trade-value improvement AND no active momentum continuation for 3 consecutive 5m bars**. Small penalty only under that joint condition. β small.

### Layer 3 — Pain Zone 🔴 (E4)
**Exponential** penalty ramp from 3.5% → 4.0% daily loss. Below 3.5%: normal. Penalty accelerates nonlinearly approaching the wall. At 4.0%+: the hard risk layer stops trading — that's risk/ code, never reward.

### Layer 4 — Target Progress 🔴 keep / 🟡 ε (E5)
Tiny bonus for movement toward DAILY_TARGET and equity above its short baseline. A weak "feel the challenge continuously" gradient, not a profit substitute. ε very small.

### Layer 5 — Category Weighting 🔴 intent (E6) — synced with SOW-C10
Macro account context re-weights the dense layers; it never replaces them:
| Context | Weighting intent |
|---|---|
| advancing (learned) | slightly favor productive continuation |
| neutral (learned) | baseline |
| warning (learned) | stagnation punished harder; less upside shaping |
| **breach-risk (explicit)** | strongly prioritize capital protection + drawdown relief |
| recovery (learned) | reward controlled progress, less than advancing |

Per C10: only breach-risk is hard-coded (real constraint proximity). The other regimes are soft-learned from account features — so L5 implements as: explicit breach-risk multiplier set + learned-context features doing the rest. Multipliers small; Layer 0 dominance preserved.

### Layer 6 — Daily Bonus 🔴 (E7 base + E9 QUAD BONUS, both locked)
**Base (E7):** a day earns streak credit only if it (1) hits DAILY_TARGET, (2) avoids the 4% trailing breach, (3) passes the stability qualifier (TD/advantage line below its shifted SMA — qualifier ONLY, never standalone reward). Streak bonus escalates **linearly in equal steps** per consecutive qualifying day, **resets on any failed day**, capped so it stays auxiliary.
**Extension (E9):** the QUAD BONUS — four signals, flow-state synergy, streak wrapper, 95% ceiling, on/off toggle. Full spec locked below.

### Layer 7 rule — Reward Scale Sanity 🔴 (E8)
All shaping layers are helpers. **Layer 0 — net post-cost trading performance — is the dominant driver.** No shaping layer may let the bot win the reward game while losing the trading game.

---

## ✅ QUAD BONUS — Layer 6 Daily Bonus Extension 🔴 [M — SOW-E9 LOCKED, renamed from Triad]
*End-of-day bonus subsystem. Sits on top of the E7 streak. Fires only on a valid pass day. Auxiliary — Layer 0 net PnL always dominates. **Gets an on/off input.***

### The four signals (house pattern: SMA-4 vs shift-4 on each metric)
Three "above," one "below."
| Signal | Metric | Pass condition | Role |
|---|---|---|---|
| Drawdown Efficiency | cushion from the 4% wall across the day | SMA-4 ABOVE its shift-4 line | PAYABLE |
| Law Productivity | closed-trade profit from law-active, allowed-direction trades | SMA-4 ABOVE its shift-4 line | PAYABLE |
| Target Velocity | day net profit ÷ bars in open positions | SMA-4 ABOVE its shift-4 line | PAYABLE |
| TD-stability | TD-error / advantage line | SMA-4 BELOW its shift-4 line | QUALIFIER only (gates flow-state) |

Target Velocity formula: `TV = day_net_profit / bars_in_open_positions`

### Firing logic (toggle: ON in training / OFF in early law school)
1. **Pass-day gate** — day hit DAILY_TARGET AND avoided the 4% trailing breach. If not, NOTHING in the Quad pays.
2. **Micro-bonuses** — each payable signal whose SMA-4 is above its shift-4 line pays **5% of day net PnL**, independently.
3. **Flow-state synergy** — all 3 payable signals TRUE *and* TD-stability TRUE → one **+5%** synergy bonus.
4. **Streak wrapper** — consecutive flow-state days add **+5% each, linear**; resets on any failed / non-flow day; escalates beyond the ordinary E7 pass-day streak.
5. **Ceiling** — total Quad bonus clamped at **95% of day net PnL** (strictly < 1×, so E8 holds and Layer 0 stays dominant).

### Bonus sizes (all as % of day net PnL)
micro 5% each · flow-state +5% · streak +5% per extra consecutive flow day · hard ceiling 95%.

### Leashes [C — carried from your design notes]
- TD-stability is NEVER a paid signal — qualifier only, so the bot can't learn critic-pleasing
- Sizes stay small: Drawdown Efficiency overlaps Layer 3 and Target Velocity overlaps Layer 2, so multipliers must avoid double-paying the per-bar gradients
- Layer 0 dominance preserved (E8): the 95% ceiling keeps the bonus strictly below one day's PnL
- Law Productivity is the safest core signal — it's also a scoreboard metric (I1: law-protected stand-aside profit time)
- One reusable code block builds every signal: SMA-4 of the metric vs its shift-4 line (above = pay, below = the TD qualifier)

### Toggle
Whole Quad subsystem enables/disables as ONE unit. Default: ON in training, OFF in early law school.

---

## DELAYED GRATIFICATION 🔴 [M+P]
High γ (0.997 locked) + high λ (0.97 locked) + GAE = the math of patience. The "reason to hold" = positive advantage while in position. Your momentum features feed the critic's prediction. No retroactive labeling — curriculum is prospective.

## LAW SCHOOL CURRICULUM 🔴 [M — F1–F5 answered, amended]
**Main path = FULL-CHART training.** Not snippets, not synthetic-first.
| Element | Decision |
|---|---|
| World | Always full-chart real data (1m MT5, ~5yr, 4 assets) |
| Stage control | Trading allowed only when the stage's required LAW context is active (trend stage → trend laws; reversion stage → reversion context; etc.) |
| Stationarity stage | Merged with ATR-gate stage: trade only when ADF-stationary (rolling 100-bar, p<0.05) AND ATR-gate active (F4) |
| Costs | Real FTMO costs from day 1 — the bot never meets a costless world (A2/H2) |
| Synthetic envs | OPTIONAL auxiliary only: debugging, warm starts, stress tests (F2/F3). Not the progression path |
| Graduation | Stage passed when the bot trades only inside its allowed law context on full charts AND meets the validation target with zero law-adjacent failures → forward test → real (F5) |

## TRAINING HARD-WALL RULE 🔴 [M — cross-ref SOW-H4]
Two-phase episode rule (training): Phase A = 4% trailing DD until net +2.5% → instant auto-flat of ALL positions → Phase B = fresh 1% trailing DD anchored at post-flat equity. Live: configured platform walls. Minimum trading days = validation metric only, never a live blocker or reward term.

---

*Last updated: SOW-E9 sync — Triad replaced by locked QUAD BONUS (4 signals, 5%/5%/5% sizes, 95% ceiling, on/off toggle); all of Section E now closed*
