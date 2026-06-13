# SCOPE OF WORK — SOW #1: DEFINE THE BOT
### Master decision document. ☑ = answered & synced into blueprint files. ☐ = still open (see THE FINAL 8).

**Status: 57 of 58 items answered.** Only SOW-J0 (your final re-read/sign-off) remains.
**SOW_2_BUILD_SPEC.md (the J3 deliverable) is already generated** — J0 is now a final sign-off pass before handing it to Claude Code.

**Origin key:** [M] = Monty | [P] = Perplexity adopted | [C] = Claude bridge

---

# SECTION A — CONSTITUTION ✅ 3/3

☑ **SOW-A1 — North Star.** One universal policy; repeatedly pass FTMO-style constraints, not raw PnL. `ftmo_mode` ON = daily-target behavior + challenge stopping; OFF = keep trading after target, trailing wall still hard-stops. Expose platform inputs, hyperparameter inputs, HPO function in the build spec.

☑ **SOW-A2 — v1 platform/universe.** FTMO MT5. **Multi-asset from day one** (forex + metals/indices). EA on one chart, trades any supported broker asset. Reference account 10k with `ftmo_account_size` input for larger sizes. Policy platform-blind; conversion after the decision layer. Real FTMO costs in training AND evaluation.

☑ **SOW-A3 — Defaults.** DAILY_TARGET 2.5% / DAILY_RISK 4% trailing when ftmo_mode ON. Configurable inputs, never hardcoded. OFF-mode keeps the trailing wall.

# SECTION B — ACTION SPACE ⚠️ 3/5

☑ **SOW-B1 — Portfolio-aware action space (A-1 adopted + extended).** Flat: {HOLD, OPEN_LONG, OPEN_SHORT}. Net long: {HOLD, CLOSE, OPEN_LONG}. Net short: {HOLD, CLOSE, OPEN_SHORT}. Multiple trades, same-symbol stacking, multi-symbol. PPO learns trade management at the ACCOUNT level. CLOSE = intentional exit, never auto-reversal.

☑ **SOW-B2 — Per-trade CLOSE via pointer head** (amends B1 🔴, G3, C9). Policy gains a 4th head: a categorical **pointer head** over **N=5 trade slots per symbol**. On CLOSE the pointer picks WHICH slot to exit; masked on HOLD/OPEN; forced if 1 open; CLOSE masked if 0 open. CLOSE = exit the single pointer-selected trade. FIFO/symbol-flatten retired as the v1 mechanism. (Full text: PPO_ENGINE.md; trade block → per-slot ×5 in STATE_VECTOR.md.)

☑ **SOW-B3 — Scale-in allowed.** OPEN_LONG adds to long exposure; OPEN_SHORT adds to short, subject to account state + challenge constraints.

☑ **SOW-B4 — Decision frequency.** Policy acts every **1m bar**. 5m/30m = structure + law context. Laws/risk enforced on 1m-bar basis (no tick assumption). Curriculum: early phases mask most 1m timing features (except law-required), later phases unmask for fine entries/exits.

☑ **SOW-B5 — Multi-symbol decision loop.** One universal policy steps the 4 symbols **sequentially** each 1m bar; each carries its 5 slots; **one shared account block**; **true-sequential within-bar updates** (each symbol sees account state already updated by prior symbols — prevents collective overshoot of the daily-risk buffer in one bar). Bar-open snapshot rejected. Sub-note for SOW #2: symbol processing order = fixed default.

# SECTION C — STATE VECTOR ✅ 11/12 (C3 rides on D4)

☑ **C1 — Timeframe universe: 1m, 5m, 30m, 4H.** Law bindings per-law. **NEW 4H RULE [M]: 4H is observed for ALL laws (same indicators as 5m/30m) but NEVER required for activation.** Written into THE_TRADING_CODE.md + STATE_VECTOR.md.
☑ **C2 — BB encoding** derived from law definitions (the inventory's field-7/8 specs). Resolved by the law book.
☐ **C3 — CCI periods** → folded into SOW-D4 (observation family 10/30/100 [from D1]; law bindings to confirm).
☑ **C4 — ATR spec.** ATR14, applied SMA-4 shift-4, on 1m + 30m. Features: level, reference, normalized distance per TF.
☑ **C5 — Z-scores.** Lookback **10 AND 100** per TF on 1m/5m/30m. Short vs long deviation context.
☑ **C6 — ADX replaces OBV.** ADX 5 + ADX 15 on 1m + 30m, normalized /100. Observation only, not a law. All OBV references retired.
☑ **C7 — Candle block keep.** 1m: bar return, range/ATR, wick ratios.
☑ **C8 — Time block keep.** sin/cos hour + day-of-week.
☑ **C9 — Trade-state block confirmed** (direction, uPnL, age, entry distance/ATR, MFE/MAE, momentum flag) + portfolio aggregates note (rides on B5).
☑ **C10 — Macro categories SOFT-LEARNED** except breach-risk (explicit, tied to hard constraint proximity).
☑ **C11 — Equity SMA confirmed exactly:** equity → SMA-1 → SMA-4 shift-4 baseline.
☑ **C12 — Challenge features added:** daily challenge progress (day PnL vs target) + overall challenge progress (equity vs initial balance).

# SECTION D — LAWS ✅ 4/4

☑ **D1 — CCI Confluence Law RETIRED as standalone** — absorbed by CCI Trend + CCI Super Trend. ±60 2-of-3 logic logged as a future law candidate.
☑ **D2 — Time-Warp Doctrine RETIRED** (it was the period-1 shifted-SMA family). The shifted-SMA family is **period 4, shift 4** across all three SMA laws.
☑ **SOW-D3 — v1 law scope: build ALL 12 at once** (9 core laws + 3 gates). No subset/phased build. Complete LawMask up front; curriculum activates them stage by stage at TRAINING time.
☑ **SOW-D4 — Indicator harmonization LOCKED:** (a) shifted-SMA = **period 4, shift 4** (the flip from the period-1 default), (b) CCI laws bind 30+100; **pullback small=10 / large=100**; observation carries 10/30/100, (c) ATR gate reference = **SMA-4, shift-4**, (d) name merge confirmed: F-001 → Super Trend Law 1, Bollinger Push No. 1 → Trend Law 1, legal names kept.

**The full 9-law inventory + 3 gates + law template + two enforcement modes + observation coverage rule are LEGISLATED in THE_TRADING_CODE.md** — single source of truth, no duplication here.

# SECTION E — REWARD ✅ 9/9

☑ **E1 — Layer 0 Outcome Engine:** per-bar net PnL (realized + unrealized) after costs + explicit closed-trade realization event.
☑ **E2 — Layer 1 momentum:** small CCI back in sync with bigger CCIs in trade direction AND ATR above shifted reference; bonus only in-position; α small.
☑ **E3 — Layer 2 stagnation:** favorable legal state + no improvement + no momentum continuation for 3 consecutive 5m bars; β small.
☑ **E4 — Layer 3 pain zone: exponential** ramp 3.5→4.0%; 4%+ = hard risk layer, not reward.
☑ **E5 — Layer 4 target progress:** keep, ε very small.
☑ **E6 — Layer 5 category weighting:** breach-risk explicit, others learned context; multipliers small; Layer 0 dominant.
☑ **E7 — Layer 6 v1 streak:** pass-day + no-breach + stability QUALIFIER → linear equal-step escalation, resets on fail, capped, auxiliary only.
☑ **E8 — Scale sanity:** bot can never win the reward game while losing the trading game; Layer 0 dominates.
☑ **SOW-E9 — QUAD BONUS** (renamed from Triad). Layer 6 end-of-day extension on top of the E7 streak. Four signals on the house pattern (SMA-4 vs shift-4): **Drawdown Efficiency, Law Productivity, Target Velocity** (payable, SMA above line) + **TD-stability** (qualifier only, SMA below line, gates flow-state). Sizes: micro 5% each / flow-state +5% / streak +5% per extra flow day; **ceiling 95% of day PnL** (E8-safe). On/off toggle, ON in training / OFF early law school. Full spec in REWARD_DESIGN.md.

# SECTION F — CURRICULUM ✅ 5/5

☑ **F1 — Full-chart law-gated curriculum.** Always whole charts; stage controls trading by LAW activation (trend stage = trend laws, etc.). Promotion: law school → forward test → real.
☑ **F2 — Synthetic envs = optional auxiliary** (debug, warm starts, stress tests). Not the progression path.
☑ **F3 — Costs always on.** Real FTMO costs from day 1; no costless worlds.
☑ **F4 — Stationarity stage merged with ATR-gate stage.** Rolling ADF, 100-bar window, p<0.05 = stationary; trade only when gate + ATR-law context both active.
☑ **F5 — Graduation:** trade only inside allowed law context on full charts + meet validation target with zero law-adjacent failures → forward test → real.

# SECTION G — PPO INTERNALS ✅ 8/8

☑ **G1 — MLP v1.** LSTM = v2 experiment only if open-trade memory proves the bottleneck.
☑ **G2 — γ 0.997, λ 0.97 LOCKED.** Law-school aggression as RANGES (entropy 0.03–0.08, clip 0.25–0.35, LR 5e-4–1e-3, epochs 10–15) driven by the missed-opportunity scheduler; cools as captures improve, cools more for real-data phases.
☑ **SOW-G3 — Size head = Beta.** raw_size 0–1, naturally bounded. Training samples from Beta; live outputs the Beta mean. Pointer head stays a separate categorical head (B2). Rejected: clipped/squashed Gaussian.
☑ **G4 — Rollout 512 / minibatch 64 early law school** → scale up later phases.
☑ **G5 — 3×256 shared MLP trunk.**
☑ **G6 — Optuna**, law-school phases, **non-sacred dials only.** Hand-locked: γ, λ, the scheduler logic.
☑ **G7 — Telemetry hooks** (trunk summaries, head outputs, reward decomposition, FTMO risk telemetry) feeding I4. No execution authority.
☑ **SOW-G8 — Missed-opportunity metric (scheduler input).** TRUE when: permitted direction agrees across **5m AND 30m AND 4H** + bot was **flat** on that symbol + price then ran **≥1.5×ATR** in the permitted direction. Training-only; never touches reward/masks/live. 4H is a confirmation lens here ONLY — law activation unchanged (protects the 4H rule 🔴).

# SECTION H — DATA, COSTS, RISK ✅ 5/5

☑ **H1 — Data:** existing MT5 1m bars on Google Cloud, ~5yr × 4 assets. 5m/30m (and 4H) built by resampling the same 1m stream. No tick data in v1.
☑ **H2 — Costs:** $5/lot RT forex base + estimated average spread + fixed slippage on fills. Spread/slippage configurable; conservative fixed assumptions, never zero-cost.
☑ **H3 — RiskManager:** raw_size → per-trade cap from REMAINING daily risk buffer → lots with rounding, min/max clamps, feasibility checks. Policy stays platform-blind.
☑ **H4 — Hard walls (risk/ code, never reward):** TRAINING two-phase rule — Phase A: 4% trailing DD until net +2.5% → auto-flat ALL → Phase B: fresh 1% trailing anchored at post-flat equity. LIVE: configured platform walls. Min trading days = validation only. Target + trailing DD exposed as inputs for Apex/other platforms.
☑ **H5 — Kill switches:** manual halt + breach auto-flat = hard. Max trades/day + max consecutive losses = monitoring only. Daily reset 00:00 CE(S)T. Platform monitors: 200 orders / 800 positions.

# SECTION I — VALIDATION ✅ 4/4

☑ **I1 — Scoreboard:** pass rate → breach count → target-hit consistency → max DD path. Plus: win rate, lowest DD% among passes, law-protected stand-aside profit time. Raw PnL = diagnostic.
☑ **I2 — Walk-forward LOCKED: 12mo train / 2mo test / 1mo step / 7 seeds.** The single protocol, everywhere (old 6/1/5 references retired).
☑ **I3 — Promotion:** survives full walk-forward on ≥3 seeds with scoreboard improvement AND no worse breach count.
☑ **I4 — LLM Risk Doctor, option (d):** telemetry + LLM diagnosis + curriculum prescription + deterioration trigger + **MLP interpretation** (understand decisions, actor, critic, reward effects). Offline/supervisory only; never touches execution, masks, sizing.

# SECTION J — HANDOFF ✅ 3/3 (J0 sync-bless pending = final-8 item)

☑ **J1 — Hybrid tier tree LOCKED** — `project_root/` with `00_constitution/`, `01_locked_core/` (laws, risk, costs, platform), `02_ftmo_passing/` (scoreboard, challenge state, validation), `03_market_pipeline/` (data, features, env), `04_learning_system/` (agent, rewards by layer, training, configs), `05_diagnostics/` (telemetry, llm_risk_doctor, reports), `06_live_bridge/`, `99_docs/`. FTMO-critical first. (Full tree as you wrote it — carried verbatim into SOW #2.)
☑ **J2 — Expanded module list LOCKED:** Env, FeatureBuilder, LawMask, RiskManager, CostLayer, PPOAgent, RolloutBuffer, RewardEngine, Trainer, CurriculumManager, HPO, Backtester, WalkForwardRunner, Scoreboard, PromotionGate, TelemetryLogger, MLPInterpreter, LLMRiskDoctor, LiveBridge(MT5), ExecutionAdapter, ManualHalt — with your one-line contracts (carried verbatim into SOW #2).

**B2 ripple into module contracts (for SOW #2 — must be reflected in the contracts):**
- **PPOAgent / action_heads:** four heads (direction · Beta size · pointer · value); pointer is categorical over the 5 slots, masked per position state.
- **RolloutBuffer:** stores `a_pointer` and the summed three-head log-prob.
- **Env / ExecutionAdapter:** maintains 5 trade slots PER symbol; CLOSE routes to the pointer-selected slot; OPEN fills the next free slot (capped at 5 = scale-in ceiling, B3).
- **RiskManager:** per-trade sizing tracks all open slots against the shared daily-risk buffer (a new OPEN must fit alongside the 4 possible existing slots, per the B5 true-sequential rule).
- **FeatureBuilder:** emits the per-slot ×5 trade block + occupied flags + portfolio aggregates.
- **TelemetryLogger / MLPInterpreter:** log pointer-head outputs (which slot, with what confidence) for the Risk Doctor.
☑ **J3 — SOW #2 = full spec package (d):** Mission & Constitution · Locked Architecture · Repo Tree · Module Contracts · State & Features · Reward System · Curriculum & Training Flow · Validation & Promotion · Diagnostics & LLM Supervision · Live Deployment Rules · Acceptance Tests · Operator Appendix · Implementation Order · Milestone Checklist · Definition of Done per module.

---

# 🔍 COHESION AUDIT [C — Issue 5: does everything point at passing FTMO consistently?]

**Verdict: the architecture is coherent. The chain holds:**
laws filter → state shows market+trade+account+challenge → reward pays net progress with protection layers → curriculum teaches structure-first on real charts → hard walls cap damage → scoreboard selects for PASS RATE, not PnL → Risk Doctor explains failures. Every module in J2 serves a link in that chain.

**The 8 cracks found in the prior sync — 7 now CLOSED:**
1. ✅ Shifted-SMA period drift → **period 4** locked (D4); period-1 Time-Warp retired
2. ✅ CCI period drift → laws bind 30+100, pullback 10/100, observation 10/30/100 (D4); ±60 logic retired to future candidate
3. ✅ CLOSE scope → per-trade via pointer head, 5 slots/symbol (B2)
4. ✅ Multi-symbol loop → sequential, shared account, true-sequential within-bar (B5)
5. ✅ v1 law scope → all 12 built up front (D3)
6. ✅ Size-head distribution → Beta (G3)
7. ✅ Scheduler input metric → 5m+30m+4H aligned + flat + ≥1.5×ATR (G8)
8. ✅ Triad bonus → QUAD BONUS locked (E9)

**Only J0 remains** — your final re-read.

**New ripples introduced by these 7 (all already propagated):** pointer head added to PPO_ENGINE four-head architecture · trade-state block expanded to per-slot ×5 in STATE_VECTOR · LawMask must respect the pointer/slot mechanics + sequential loop (env cross-ref added to THE_TRADING_CODE) · pointer-head telemetry added to the Risk Doctor's inputs (G7).

**Resolved in earlier syncs (no action needed):** walk-forward conflict (12/2/1/7) · OBV→ADX swap · enforcement-mode wording unified · 4H observation rule wired in.

---

## PROGRESS TRACKER (real numbers)
| Section | Items | Done |
|---|---|---|
| A Constitution | 3 | 3 |
| B Action space | 5 | 5 |
| C State vector | 12 | 11* |
| D Laws | 4 | 4 |
| E Reward | 9 | 9 |
| F Curriculum | 5 | 5 |
| G PPO internals | 8 | 8 |
| H Data/risk | 5 | 5 |
| I Validation | 4 | 4 |
| J Handoff | 3 | 3 |
| **Total** | **58** | **57** |

*\*C3 (CCI periods) was folded into D4 and is locked there — counted under D4, so C shows 11/12 by line but is functionally complete.*

**Path to handoff: SOW-J0 (your final re-read/sign-off) → SOW_2_BUILD_SPEC.md is already written and ready for Claude Code.**

*[C — 2026-06-13: SOW_2_BUILD_SPEC.md (the J3 deliverable) has been generated and added to the folder. This line previously said "generate the build spec" as a future step; it's done. J0 is now sign-off only — connects to OPEN_QUESTIONS.md and 00_START_HERE.md, both updated the same way.]*

---

*Last updated: SOW-D4/D3/B2/B5/G3/G8/E9 locked — 57/58, only J0 remains; ripples propagated across all four spec files*
