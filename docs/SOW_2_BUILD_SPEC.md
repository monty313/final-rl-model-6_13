# SOW #2 — QUANTRA BUILD SPECIFICATION
### The complete, binding build spec for Claude Code.
### Quantra: Deep-Reinforcement-Learning-in-Trading
### GitHub: https://github.com/monty313/Qunatra_Deep-Reinforcement-Learning-in-Trading.git

**Status:** 🔴 BUILD SPEC — implement exactly as written. Deviation requires Monty's explicit approval.
**Origin key:** [M] = Monty | [P] = Perplexity adopted | [C] = Claude bridge

---

# READ THIS FIRST — RULES FOR CLAUDE CODE

These rules govern HOW you build, not just WHAT you build. They are non-negotiable.

## R1 — The single mission anchors everything
The bot is being built to **repeatedly pass FTMO-style challenges over time** (2.5% daily target, 4% trailing wall). Not to maximize PnL. Every line of code, every comment, every test must serve that single mission.

## R2 — Comment everything relative to passing FTMO
- Every function, class, reward term, law, mask, telemetry hook MUST carry a comment explaining:
  1. **What it does** technically.
  2. **How it serves repeated FTMO-style passing** (not generic ML accuracy, not raw PnL).
- The audience for these comments is BOTH future maintainers AND the LLM Risk Doctor at inference time.
- If a comment can't explain how the thing serves FTMO passing, the code probably shouldn't be there.

## R3 — Leave very detailed comments telling the LLM Risk Doctor HOW TO THINK
- The LLM Risk Doctor reads telemetry AND has read-only access to this codebase.
- Every module's header docstring MUST point to `MLP_INTERPRETABILITY_LAYER.md` as the binding rulebook.
- Diagnostic comments at key code sites (reward layers, masks, RiskManager logic, heads) must include "How the LLM should interpret this" notes.
- These comments are the LLM's safety rail. Without them it gets lost and starts inventing.

## R4 — Comment-on-every-update rule
Any LLM (including future Claude Code sessions) updating any file in this repo MUST leave a comment at the change site explaining:
1. **What** was changed.
2. **How** it connects with the rest of the folder/codebase (which files, sections, locks it touches).
3. **Why** the change was made.
Goal: future sessions never get lost reconstructing why a thing is the way it is.

## R5 — Hard architectural rules (never violate)
- Laws are NEVER reward terms. They run BEFORE reward as hard masks (logit = −1e9 on forbidden actions).
- Layer 0 (net PnL) always dominates the reward — no shaping layer wins the reward game while losing the trading game (the E8 rule).
- No 🔴 locked item changes without Monty's explicit approval. Propose amendments; don't apply them.
- The LLM Risk Doctor has READ-ONLY access to the repo. It may VIEW any file to support reasoning. It may NEVER write, modify, or delete ANY file. It may NEVER touch execution, masks, sizing, or hard walls.

## R6 — Implementation order is binding
The Implementation Order in Section 13 is not a suggestion. Build in that order. Each step requires the previous to be DONE per Section 15's Definition of Done.

---

# SECTION 1 — MISSION & CONSTITUTION

## 1.1 What we're building
A PPO-based reinforcement learning trading agent that takes two runtime inputs (daily profit target, max daily loss) and learns to hit the target while respecting the loss constraint, consistently — across many windows and seeds. Primary target platform: FTMO via MT5. Multi-asset: 4 symbols (forex pairs + metals/indices supported, real costs from day 1).

## 1.2 What success means
Success = the bot passes FTMO-style challenges repeatedly across walk-forward windows on ≥3 of 7 seeds, with stable or improving scoreboard metrics. Raw PnL is diagnostic only.

## 1.3 Scoreboard (the only ranking that matters)
1. FTMO pass rate
2. Breach count (lower is better)
3. Target-hit consistency
4. Max drawdown path
Raw PnL is **not** a ranking criterion. It's a sanity check.

## 1.4 Runtime inputs (no saved config file — pure runtime memory)
- `daily_target_pct` (default: 2.5)
- `daily_risk_pct` (default: 4.0)
- `ftmo_mode` (boolean, default: True)
- `ftmo_account_size` (default: 10000 — used for ref scaling; policy is account-size-blind via normalized size output)

## 1.5 Constitutional rules (the 9 hard architectural commitments)
| # | Rule |
|---|---|
| C1 | One universal policy. No regime-specialist ensembles. |
| C2 | Multi-asset day one: FTMO MT5, 4 symbols, real costs day 1, no costless world. |
| C3 | Defaults: 2.5% daily target / 4% trailing loss. Configurable at runtime. |
| C4 | Decision frequency: every 1m bar. 5m/30m/4H carry structure context. |
| C5 | Laws are masks, not rewards. Pre-mask logits set to −1e9 on forbidden actions. |
| C6 | Layer 0 (net PnL) dominates the reward. No shaping layer overrides it. |
| C7 | Live execution is fully separated from diagnostics. LLM Risk Doctor is offline/read-only/supervisory. |
| C8 | Real FTMO costs from training day 1. No costless warm-up. |
| C9 | Full-chart curriculum — never snippets. Stages gate by law context, not by chart slicing. |

---

# SECTION 2 — LOCKED ARCHITECTURE

## 2.1 Algorithm
- **PPO**, on-policy, no replay buffer
- **γ = 0.997, λ = 0.97** (hand-locked, "math of patience" — Optuna may NOT tune these)
- Rollout: 512 early law school, scales up later
- Minibatch: 64 early, scales up
- Aggression dial ranges (scheduler input only): entropy 0.03–0.08 · clip 0.25–0.35 · LR 5e-4–1e-3 · epochs 10–15

## 2.2 Network
- **MLP trunk**, 3 hidden layers × 256 units, shared between actor and critic
- LSTM = v2 only, if memory turns out to be the bottleneck

## 2.3 Four-head architecture (locked, B2 amendment to B1)
1. **Direction head** — categorical over `{HOLD, OPEN_LONG, OPEN_SHORT, CLOSE}`, masked per position state
2. **Size head** — Beta distribution over `raw_size ∈ [0, 1]` (samples in training, mean in live)
3. **Pointer head** — categorical over the 5 trade slots, ONLY used on CLOSE (masked on HOLD/OPEN; forced if 1 slot open; CLOSE itself masked if 0 slots open)
4. **Value head (critic)** — V(s) for GAE; no log-prob (only the 3 action heads contribute to the policy loss)

## 2.4 Action space + slot mechanics
- N = 5 trade slots PER symbol
- OPEN fills the next free slot. All 5 full → OPEN masked.
- CLOSE: pointer head selects which slot to exit.
- Scale-in allowed (additional OPEN_LONG on an already-long symbol is allowed up to the 5-slot ceiling).
- FIFO/symbol-flatten RETIRED as the v1 mechanism.

## 2.5 Multi-symbol decision loop
- One universal policy steps the 4 symbols **sequentially** each 1m bar.
- Each symbol gets its own observation (carrying its 5 slots).
- ONE shared account block — read by every symbol's decision.
- **True-sequential within-bar updates**: each symbol sees the account state already updated by prior symbols in the same bar (prevents collective overshoot of the daily-risk buffer).
- Symbol processing order: fixed default (rotation/randomization flagged for future work).

## 2.6 Episode rule — TWO-PHASE LOCKED [M]
- **Phase A:** 4% trailing drawdown is the wall, until day net hits +2.5% → instant auto-flat ALL positions
- **Phase B:** fresh 1% trailing drawdown anchored at the post-flat equity
- LIVE: platform walls, not training walls
- Min trading days: validation only (not a training constraint)

## 2.7 Risk model — three-zone [M]
- Normal: 0–3.5% drawdown
- Pain zone: 3.5–4.0% — reward Layer 3 punishes hard (exponential)
- Hard wall: 4.0% trailing → force-flatten ALL, lock out for the day

## 2.8 PPO loss
`L = L_clip − c1·L_value + c2·entropy`
- The policy ratio in `L_clip` uses the **summed log-prob across the 3 action heads** (direction + Beta size + pointer)
- `c2·entropy` is the **sum of the 3 heads' entropies**
- Masked heads contribute zero log-prob and zero entropy on that step (size head only contributes when OPEN fires; pointer only when CLOSE fires)

## 2.9 Rollout buffer per step
`(s, a_direction, a_size, a_pointer, reward, s', logp_old, V_old, done, masks)`
- `logp_old` is the SUM of the 3 action-head log-probs
- `masks` covers both the direction-action mask and the pointer/slot mask

## 2.10 Deployment / live mode
Training is stochastic (sample all heads). Live is deterministic:
- **argmax direction**
- **Beta-mean size**
- **argmax pointer slot** on CLOSE
- Clipped by RiskManager
- Live execution fully separated from diagnostics (I4)

---

# SECTION 3 — REPO TREE (J1 hybrid tier tree)

```
quantra/
├── 00_constitution/        # The non-negotiables, mission, rules-of-the-road
│   ├── mission.md
│   ├── constitutional_rules.md
│   └── safety_boundaries.md
├── 01_locked_core/         # 🔴 protected — no changes without Monty's approval
│   ├── laws/               # all 9 laws + 3 gates
│   ├── risk_manager/       # the size→lots→buffer translator
│   ├── cost_layer/         # FTMO costs (spread, $5/RT/lot forex, fixed slip)
│   └── platform_adapter/   # MT5 broker interface (live + sim)
├── 02_ftmo_passing/        # the scoreboard logic — what "winning" means
│   ├── scoreboard.py
│   ├── challenge_state.py
│   ├── episode_rule.py     # the two-phase rule
│   └── validation/         # walk-forward + promotion gates
├── 03_market_pipeline/     # data ingestion + feature building
│   ├── data_loader/        # GCS MT5 1m bars
│   ├── resampler/          # 5m/30m/4H from 1m
│   ├── feature_builder/    # the state vector
│   └── law_mask_engine/    # law states → action mask
├── 04_learning_system/     # PPO trainer + curriculum + HPO
│   ├── ppo_agent/
│   ├── rollout_buffer/
│   ├── reward_engine/
│   ├── trainer/
│   ├── curriculum_manager/
│   └── hpo/                # Optuna for non-sacred dials only
├── 05_diagnostics/         # the interpretability layer
│   ├── telemetry_logger/
│   ├── mlp_interpreter/
│   ├── llm_risk_doctor/    # read-only — never touches execution
│   └── failure_atlas/
├── 06_live_bridge/         # MT5 live deployment (isolated from diagnostics)
│   ├── live_runner.py
│   ├── execution_adapter.py
│   └── manual_halt.py
├── 99_docs/                # the blueprint folder (copy of Drive)
│   ├── 00_START_HERE.md
│   ├── OPEN_QUESTIONS.md
│   ├── THE_TRADING_CODE.md
│   ├── STATE_VECTOR.md
│   ├── REWARD_DESIGN.md
│   ├── PPO_ENGINE.md
│   ├── MLP_INTERPRETABILITY_LAYER.md
│   ├── SCOPE_OF_WORK.md
│   ├── SOW_2_BUILD_SPEC.md
│   └── wtf_are_you_talking_about.md
└── README.md
```

*[C — 2026-06-13: Repo tree's 99_docs listing corrected to include OPEN_QUESTIONS.md and SOW_2_BUILD_SPEC.md itself — both belong in the in-tree docs folder alongside the other 8. Previously this list showed only 8 files and was missing these two. Connects to Section 17 final-instructions list below, which should be read as "all 10 files in 99_docs", not 7.]*

---

# SECTION 4 — MODULE CONTRACTS (J2 — 21 modules)

Each module gets its own file/package. Every module's header docstring MUST:
1. State what the module does
2. State how it serves repeated FTMO-style passing
3. Reference `99_docs/MLP_INTERPRETABILITY_LAYER.md` as the LLM's rulebook

| Module | One-line contract |
|---|---|
| **Env** | Real-chart gym env, 4 symbols, true-sequential within-bar loop, 5 slots/symbol, shared account block. |
| **FeatureBuilder** | Builds the ~145-scalar state vector from 1m/5m/30m/4H + trade slots ×5 + shared account block + challenge progress. |
| **LawMask** | Computes all 12 law/gate states each step; emits the pre-mask logits (−1e9 on forbidden); enforces live-ban OR law-school permission mode. |
| **RiskManager** | Converts `raw_size ∈ [0,1]` → lots against remaining daily-risk buffer + broker rounding + per-trade caps; slot-aware (tracks all 5 open slots' risk). |
| **CostLayer** | Real FTMO costs from day 1: spread, $5/RT/lot for forex (metals/indices = no per-trade cost), fixed slippage. |
| **PPOAgent** | 4 heads (direction · Beta size · pointer · value), 3×256 trunk; produces summed log-probs for the 3 action heads. |
| **RolloutBuffer** | Stores `(s, a_direction, a_size, a_pointer, reward, s', logp_old, V_old, done, masks)`; no replay. |
| **RewardEngine** | Layered reward (L0–L6 + QUAD bonus), Layer 0 dominance enforced, QUAD ceiling 95% of day PnL. |
| **Trainer** | PPO loop, GAE (γ=0.997, λ=0.97), aggression scheduler (G2 + G8 missed-opportunity input). |
| **CurriculumManager** | Stage controller (trend → reversion → stationarity+ATR); law-school permission mode in stages; full-chart always. |
| **HPO** | Optuna for non-sacred dials only (γ, λ, scheduler logic = hand-locked). |
| **Backtester** | Single-window backtest + cost replay. |
| **WalkForwardRunner** | 12mo train / 2mo test / 1mo step / 7 seeds — the single locked protocol. |
| **Scoreboard** | Ranks runs by (1) pass rate (2) breach count (3) target-hit consistency (4) max DD path. |
| **PromotionGate** | A run promotes only on ≥3 seeds with scoreboard improvement AND no worse breach count. |
| **TelemetryLogger** | Per-step + per-trade + per-day packets per the data contract in MLP_INTERPRETABILITY_LAYER.md; versioned schema. |
| **MLPInterpreter** | Generates the 7 required visuals from telemetry (activation traces, projections, action/value timelines, reward timelines, heatmaps, failure atlas, pass-day atlas). |
| **LLMRiskDoctor** | Reads telemetry + interpretability artifacts + has READ-ONLY repo access. Produces diagnoses per the output template in MLP_INTERPRETABILITY_LAYER.md. NEVER writes, never executes. |
| **LiveBridge(MT5)** | MT5 live execution adapter, fully isolated from diagnostics. |
| **ExecutionAdapter** | Manages the 5 slots per symbol on the live broker; routes CLOSE to the pointer-selected slot. |
| **ManualHalt** | Hard kill switch for the operator. Always available. |

### B2 amendment notes (already propagated through the contracts above):
- PPOAgent: four heads; pointer is categorical over the 5 slots
- RolloutBuffer: stores `a_pointer`, summed three-head log-prob
- Env / ExecutionAdapter: 5 slots/symbol; CLOSE routes via pointer; OPEN fills next free slot
- RiskManager: slot-aware sizing against the shared daily-risk buffer
- FeatureBuilder: per-slot ×5 trade block + occupied flags + portfolio aggregates
- TelemetryLogger / MLPInterpreter: log pointer-head outputs for the Risk Doctor

---

# SECTION 5 — STATE & FEATURES (~145 scalars)

Full spec lives in `99_docs/STATE_VECTOR.md`. The header counts:

| Block | Approx scalars |
|---|---|
| Market features (1m/5m/30m/4H — multi-period CCI, shifted SMAs, BB, ATR, ADX, z-scores) | ~75 |
| Law/gate states + flags (12 entries × ingredients) | ~25 |
| Trade state — PER-SLOT ×5 (7 features × 5 slots) | ~35 |
| Portfolio aggregates across slots | ~3 |
| Account block (equity vs initial, equity SMA, buffers, day PnL) | ~5 |
| Challenge-progress features (day PnL vs target, equity vs initial, post-target flag) | ~2 |
| Total | **~145** |

### Hard locks
- Shifted-SMA family: period 4, shift 4 (all 3 SMA laws) [M]
- CCI Pull Back: small=10, large=100; applied SMA period 2 shift 4 [M]
- ATR Liquidity Gate reference: SMA-4, shift-4 [C confirmed by M]
- Timeframes: 1m + 5m + 30m + 4H. **4H Observation Rule [M]: 4H observed for ALL laws, NEVER required for activation.**
- ADX replaces OBV: ADX5 + ADX15 on 1m+30m, normalized /100 (observation only, not a law)
- Z-scores: dual lookback 10 AND 100 on 1m/5m/30m
- Macro categories: SOFT-LEARNED except breach-risk (the only explicit hardcoded category)
- Equity SMA: SMA-1 of equity → SMA-4 shift-4 baseline (exact)

---

# SECTION 6 — REWARD SYSTEM

Full spec in `99_docs/REWARD_DESIGN.md`. Layer structure:

`r(t) = L0_ΔNetPnL + α·L1_momentum − β·L2_stagnation − δ·L3_painzone + ε·L4_target_progress × L5_category_weighting + L6_daily_bonus`

| Layer | What it pays/punishes | Comment for the LLM |
|---|---|---|
| **L0** | Per-bar net PnL after costs + explicit closed-trade realization | Must always dominate. The E8 rule. |
| **L1** | Small CCI back in sync with bigger CCIs in trade direction AND ATR above shifted ref; small α | Timing helper, never the objective. |
| **L2** | Favorable legal state + no equity improvement + no momentum continuation for 3 consecutive 5m bars; small β | Punishes coasting in good context. |
| **L3** | Pain zone — EXPONENTIAL ramp 3.5%→4.0% daily loss | Saves the bot from breaching. |
| **L4** | Target progress — tiny ε | Whisper, not a shout. |
| **L5** | Category weighting — only breach-risk is explicit; others learned | Context modifier, not a payer. |
| **L6** | Daily bonus = E7 streak + E9 QUAD bonus | End-of-day only. Auxiliary. |

### QUAD BONUS (L6 extension) — locked [M]
| Signal | Pass when | Role | Size |
|---|---|---|---|
| Drawdown Efficiency | SMA-4 above shift-4 line | Payable | +5% of day PnL |
| Law Productivity | SMA-4 above shift-4 line | Payable | +5% of day PnL |
| Target Velocity | SMA-4 above shift-4 line | Payable | +5% of day PnL |
| TD-stability | SMA-4 BELOW shift-4 line | Qualifier (gates flow-state only) | not paid alone |

- Flow-state synergy: all 3 payable TRUE AND TD-stability TRUE → +5%
- Streak: +5% per extra consecutive flow day, linear, resets on non-flow day
- Ceiling: 95% of day PnL (E8-safe: strictly < 1×)
- Toggle: ON in training, OFF in early law school

---

# SECTION 7 — CURRICULUM & TRAINING FLOW

Full spec in `99_docs/THE_TRADING_CODE.md` + `REWARD_DESIGN.md`. Summary:

## 7.1 Stages
| Stage | Trading permitted only when... |
|---|---|
| Trend | trend laws are active |
| Reversion/Pullback | reversion/pullback law context is active |
| Stationarity + ATR-gate (merged) | ADF 100-bar p<0.05 AND ATR gate is open |

## 7.2 Mode flips per stage
- **Law school mode** — laws act as PERMISSION GATES (bot may trade ONLY when stage's required law context is live)
- Early stages: 1m timing features MASKED except law-required ones (forces structure-first learning)
- Later stages: 1m unmasked for fine entry/exit
- **Live mode (post-graduation)** — laws act as BANS (forbid bad directions; everything else legal)

## 7.3 Graduation per stage
- Trade only inside allowed law context, AND
- Meet validation target, AND
- ZERO law-adjacent failures
- Then: forward test → real

## 7.4 V1 scope
Build all 12 (9 laws + 3 gates) at once. The complete LawMask module up front. Curriculum activates them stage by stage at TRAINING time, not BUILD time.

## 7.5 G8 Missed-Opportunity Metric (aggression scheduler input)
TRUE when: permitted direction agrees across 5m AND 30m AND 4H + bot was FLAT + price ran ≥1.5×ATR in permitted direction.
- TRAINING-ONLY signal
- Feeds the hand-locked aggression scheduler (more misses → keep aggression high; few misses → cool down)
- 4H used ONLY as confirmation lens here — law activation UNCHANGED (4H Observation Rule protected)

---

# SECTION 8 — VALIDATION & PROMOTION

## 8.1 Walk-forward protocol (single, locked)
**12 months train / 2 months test / 1 month step / 7 seeds.**

## 8.2 Scoreboard ranking
1. FTMO pass rate
2. Breach count
3. Target-hit consistency
4. Max DD path
(Raw PnL = diagnostic only — never used to rank.)

## 8.3 Promotion gate
A run promotes only when ALL of:
- Survives full walk-forward on ≥3 of the 7 seeds
- Scoreboard improvement vs the previous checkpoint
- NO WORSE breach count vs the previous checkpoint

## 8.4 Checkpointing
Every trained brain checkpointed and benchmarked against the last. Never overwrite without scoreboard proof.

---

# SECTION 9 — DIAGNOSTICS & LLM SUPERVISION

**Binding file:** `99_docs/MLP_INTERPRETABILITY_LAYER.md`. The LLM Risk Doctor's operating manual lives there.

## 9.1 TelemetryLogger
Per-step packet per the data contract in MLP_INTERPRETABILITY_LAYER.md. Versioned schema. Must capture (at minimum):
- IDs (run, seed, window, episode, timestep, symbol), timestamp, bar index
- Full normalized observation + grouped feature block names
- Active laws/gates + enforcement mode, legal actions before sampling
- Pre-mask logits, post-mask logits, action probabilities, chosen action, pointer-head output (on CLOSE), raw_size, feasible size after RiskManager
- V(s) output
- Hidden layer vectors or compressed summaries
- Full reward decomposition by layer + QUAD signal states
- Risk context snapshot (all Term 6 attributes)
- Short-horizon outcome labels, trade lifecycle link

## 9.2 MLPInterpreter — the 7 required visuals
1. Activation Trace
2. Hidden-State Projection (PCA primary; UMAP/t-SNE optional)
3. Action/Value Timeline
4. Reward Layer Timeline
5. Correlation Heatmap
6. Failure Atlas
7. Pass-Day Atlas

## 9.3 LLM Risk Doctor — access + boundary
**MAY:**
- Read all telemetry, all interpretability artifacts
- **READ-ONLY access to the entire repo** (blueprint folder + codebase) — it can VIEW any file to support its reasoning
- Produce diagnoses + prescriptions per the output template in MLP_INTERPRETABILITY_LAYER.md

**MAY NOT:**
- Write, modify, or delete ANY file
- Touch execution, action masks, sizing, hard walls
- Issue broker commands
- Override the operator

Implementation note: the LLM must be wired to read `99_docs/MLP_INTERPRETABILITY_LAYER.md` on EVERY diagnosis session. It's the binding rulebook. The codebase should fail loudly if the LLM is invoked without that file being accessible.

## 9.4 The 8-failure taxonomy
The LLM classifies every failure into one of: Mask Dependence, Representation Collapse, Representation Chaos, Critic Misalignment, Reward Hijack, Risk Blindness, Stagnation Blindness, Shortcut Learning.
If a failure fits none, the LLM reports "unclassified — additional telemetry required" and stops. **It does NOT invent a 9th category.**

## 9.5 Reverse-chain reasoning protocol
The LLM walks the chain BACKWARD (outcome → reward → critic → actor → hidden state → law → state vector) and stops at the first link where evidence shows the break.

---

# SECTION 10 — LIVE DEPLOYMENT RULES

## 10.1 Hard kill switches
- **Manual halt** (operator action) — always available, always immediate
- **Breach auto-flat** (4% trailing wall) — automatic, all positions, lock out for the day

## 10.2 Monitoring-only (not hard kills)
- Max trades/day cap
- Consecutive losses cap
- Platform limits: 200 orders / 800 positions monitored

## 10.3 Daily reset
00:00 CE(S)T.

## 10.4 Live mode determinism
- argmax direction · Beta-mean size · argmax pointer slot on CLOSE
- RiskManager clips to feasible
- LLM Risk Doctor stays OFFLINE — never touches live

## 10.5 Cost structure
- $5 round-trip per lot on forex pairs
- Metals + indices: no per-trade cost (spread + slippage only)
- Spread + fixed slippage: configurable per symbol

---

# SECTION 11 — ACCEPTANCE TESTS

Each module gets unit tests + integration tests. Acceptance requires ALL of:

## 11.1 Unit
- Every law produces correct 0/1 state on hand-crafted bar sequences
- LawMask produces logit = −1e9 on every forbidden action in every position state
- RiskManager: total open-slot risk never exceeds remaining daily-risk buffer
- RewardEngine: Layer 0 dominates across 1000 random rollouts (E8 invariant test)
- RolloutBuffer: stores all 10 fields per step, log-prob is sum of 3 action heads
- TelemetryLogger: round-trip serialization preserves every field per the data contract

## 11.2 Integration
- 4-symbol true-sequential bar: the 4 symbols cannot collectively overshoot the daily-risk buffer in one bar (B5 invariant test)
- Two-phase episode: after +2.5% day net, all positions auto-flat AND Phase B 1% trailing engages
- Pointer head: CLOSE always routes to the pointer-selected slot; OPEN always fills the next free slot; OPEN masked when all 5 occupied
- Curriculum: in law-school mode, the bot CANNOT trade outside the stage's required law context

## 11.3 End-to-end
- 1 full walk-forward window (12mo train, 2mo test) completes on real MT5 1m bars without crashing
- Scoreboard produces the 4 ranking metrics
- TelemetryLogger output passes MLPInterpreter and produces all 7 required visuals
- LLMRiskDoctor produces a diagnosis using the output template, citing specific evidence fields

---

# SECTION 12 — OPERATOR APPENDIX

## 12.1 Runtime invocation (planned GUI; for v1 CLI is fine)
```
python -m quantra.live_runner \
  --daily_target_pct 2.5 \
  --daily_risk_pct 4.0 \
  --ftmo_mode true \
  --ftmo_account_size 10000 \
  --symbols EURUSD,XAUUSD,GBPUSD,US30
```

## 12.2 Manual halt
Always one button/command away. Hard kill — flats everything, locks the bot out until manual reset.

## 12.3 Training-vs-live separation
- Training runs are batch jobs on Google Cloud
- Live runs are isolated processes on the deployment machine
- The LLM Risk Doctor reads CHECKPOINTED telemetry — never sees live state in real time

## 12.4 Where the blueprint lives
- Drive (primary): Quantra folder
- Repo: `99_docs/` (in-tree copy)
- Single source of truth: whichever is most recently updated, with the change comment explaining what/how/why per R4.

---

# SECTION 13 — IMPLEMENTATION ORDER (BINDING)

Build in this order. Do not skip ahead. Each milestone gates on the previous being DONE per Section 15.

| # | Milestone | Why this comes here |
|---|---|---|
| **M0** | Repo skeleton, 99_docs in-tree, header docstrings everywhere pointing to MLP_INTERPRETABILITY_LAYER.md | Nothing builds without the docs the LLM is required to reference. |
| **M1** | Data pipeline (GCS MT5 1m → 5m/30m/4H resampler) | No features without data. |
| **M2** | FeatureBuilder + state vector (~145 scalars, verified shape) | Nothing learns without observations. |
| **M3** | LawMask (all 12 laws + gates) + unit tests | Laws-as-masks must work before training. |
| **M4** | RiskManager + CostLayer + Env (4 symbols, true-sequential, 5 slots) + B5 invariant test | Env physics must hold before training. |
| **M5** | PPOAgent (4 heads, 3×256 trunk) + RolloutBuffer + PPO loss with summed log-probs | The learning machine. |
| **M6** | RewardEngine (L0–L6 + QUAD bonus) + E8 invariant test | The objective. |
| **M7** | CurriculumManager + law-school mode + two-phase episode rule | Training shape. |
| **M8** | Trainer + GAE + aggression scheduler + G8 missed-opportunity metric | The training loop. |
| **M9** | TelemetryLogger (per data contract) + versioned schema | Diagnostics scaffolding. |
| **M10** | MLPInterpreter (all 7 required visuals) | Human + LLM-readable evidence. |
| **M11** | LLMRiskDoctor (read-only repo access wired, MLP_INTERPRETABILITY_LAYER.md mandatory-read) | Supervisory layer. |
| **M12** | Scoreboard + WalkForwardRunner + PromotionGate | Validation pipeline. |
| **M13** | HPO (Optuna on non-sacred dials) | Tuning. |
| **M14** | LiveBridge(MT5) + ExecutionAdapter + ManualHalt | Live deployment. |
| **M15** | End-to-end acceptance test passing | DONE. |

---

# SECTION 14 — MILESTONE CHECKLIST

Track each milestone with these binary boxes:

```
M0  Repo skeleton                            [ ]
M1  Data pipeline                            [ ]
M2  FeatureBuilder + state vector            [ ]
M3  LawMask + 12 laws/gates                  [ ]
M4  RiskManager + CostLayer + Env            [ ]
M5  PPOAgent + RolloutBuffer + PPO loss      [ ]
M6  RewardEngine + QUAD bonus                [ ]
M7  CurriculumManager + two-phase episode    [ ]
M8  Trainer + GAE + scheduler                [ ]
M9  TelemetryLogger (full data contract)     [ ]
M10 MLPInterpreter (7 visuals)               [ ]
M11 LLMRiskDoctor (read-only access wired)   [ ]
M12 Scoreboard + WalkForwardRunner + Gate    [ ]
M13 HPO                                      [ ]
M14 LiveBridge + ExecutionAdapter + Halt     [ ]
M15 End-to-end acceptance                    [ ]
```

---

# SECTION 15 — DEFINITION OF DONE (per module)

A module is DONE only when ALL of:

1. **Code compiles, runs, lints clean.**
2. **Header docstring** states what + how-it-serves-FTMO-passing + references `MLP_INTERPRETABILITY_LAYER.md`.
3. **Every function/class** has a comment explaining what it's for relative to passing the FTMO challenge (per R2).
4. **Diagnostic comments at key sites** tell the LLM Risk Doctor how to interpret that code section (per R3).
5. **Unit tests** for the module exist and pass.
6. **Integration tests** the module participates in exist and pass.
7. **TelemetryLogger hooks** in place where the module's outputs feed diagnostics (per the data contract).
8. **No 🔴 locked items violated.**
9. **Comment-on-update rule honored:** any modification to existing files carries a what/how/why comment per R4.

---

# SECTION 16 — REJECTED ARCHITECTURES (do not implement)

Logged for posterity. Do NOT implement these unless Monty explicitly overrules:
- Regime-specialist ensembles (conflicts with C1: one universal policy)
- HER (Hindsight Experience Replay) — contaminates on-policy PPO
- Dreamer-style world-model rollouts — creates psychotic learning (false memory of edge)
- CNN backbones — MLP is sufficient at this state-vector size
- Meta-learning — premature complexity
- Clipped Gaussian / squashed Gaussian size head — Beta won (G3)
- FIFO/symbol-flatten CLOSE — replaced by pointer head (B2)

---

# SECTION 17 — OPEN POINTERS FOR LATER (not blocking v1)

These are flagged for SOW #3 or post-launch:
- LSTM backbone (only if MLP shows memory bottleneck)
- Symbol processing order randomization/rotation (currently fixed)
- ±60 CCI 2-of-3 confluence as a candidate law (parked, not retired)
- GUI for runtime inputs (CLI is fine for v1)
- AI-clone "Monty agent" project monitor (potentially merges with LLM Risk Doctor scope)
- Survival/hostile-conditions curriculum stage (training-plan improvement, pending Monty's decision)
- Curriculum stage reorder (ATR gate first? — pending Monty's decision)

---

# CLAUDE CODE — FINAL INSTRUCTIONS

1. **Read this entire file before writing a single line of code.**
2. **Then read all files in `99_docs/`** in this order: 00_START_HERE → OPEN_QUESTIONS → THE_TRADING_CODE → STATE_VECTOR → REWARD_DESIGN → PPO_ENGINE → MLP_INTERPRETABILITY_LAYER → SCOPE_OF_WORK → wtf_are_you_talking_about. (SOW_2_BUILD_SPEC.md is this file — you're already reading it.)
3. **Build in the M0→M15 order. Don't skip ahead.**
4. **Comment everything per R2 and R3.** If you can't explain how a piece of code serves FTMO passing, stop and ask before continuing.
5. **Leave change comments per R4** on every file modification.
6. **The LLM Risk Doctor's authority is read-only — across the entire repo.** Wire it so it CAN view any file (it needs that for reasoning), and CANNOT write to any file.
7. **When in doubt, check the blueprint.** When the blueprint is silent, ask. Never guess at locked architecture.

*[C — 2026-06-13: Final Instructions step 2 corrected — was "all 7 files", now lists all 9 docs explicitly (OPEN_QUESTIONS and wtf_are_you_talking_about were missing from the reading order) and clarifies SOW_2_BUILD_SPEC.md is self-referential, not a 10th file to re-read. Connects to Section 3 repo tree fix above — both reflect the real 10-file 99_docs/ folder.]*

**End of SOW #2. Build the bot.**

---

*This file is the binding build spec. Pair it with the blueprint files in `99_docs/`. Together they are the complete, single source of truth for Quantra v1.*
