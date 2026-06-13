# PPO ENGINE
### How the Bot Learns — Architecture and Dials

**Status key:** 🔴 Locked | 🟡 Suggested | ❓ Open
**Origin key:** [M] = Monty | [P] = Perplexity adopted | [C] = Claude bridge
**Repo:** https://github.com/monty313/Qunatra_Deep-Reinforcement-Learning-in-Trading.git

---

## LOCKED ARCHITECTURE 🔴

### Algorithm: PPO, on-policy, no replay memory [M]
Rollout buffer per step: `(s, a_direction, a_size, a_pointer, reward, s', logp_old, V_old, done, masks)` → GAE → epochs of minibatch updates → discard. `logp_old` is the SUM of the three action-head log-probs (direction + size + pointer); `masks` covers both the direction-action mask and the pointer/slot mask.

### Actor-Critic: shared trunk, FOUR heads 🔴 [M — SOW-B2 adds pointer head; G3 locks size dist]
| Head | Output |
|---|---|
| Direction/action head | categorical over {HOLD, OPEN_LONG, OPEN_SHORT, CLOSE}, masked per position state (table below) |
| Size head | raw_size ∈ 0.0–1.0, **Beta distribution** (G3 locked) |
| **Pointer head (NEW)** | categorical over the symbol's trade slots — picks WHICH slot to close |
| Value head (critic) | V(s) — powers GAE, the reason-to-hold signal |

### ✅ ACTION SPACE — A-1 ADOPTED + PER-TRADE CLOSE 🔴 [M — SOW-B1/B2/B3 LOCKED]
**Portfolio-aware, not single-position.** The bot manages multiple trades, same-symbol stacking, and multiple symbols, relative to passing the challenge at the ACCOUNT level.
| Position state (current symbol) | Legal actions |
|---|---|
| Flat | HOLD, OPEN_LONG, OPEN_SHORT |
| Net long | HOLD, CLOSE, OPEN_LONG (scale-in) |
| Net short | HOLD, CLOSE, OPEN_SHORT (scale-in) |
CLOSE = intentional exit management, never auto-reversal.

### Trade slots + pointer head 🔴 [M — SOW-B2 LOCKED, amends B1 🔴]
**N = 5 trade slots per symbol** (caps same-symbol scale-in depth, B3). The model learns WHICH individual trade to close AND WHEN, judged on passing FTMO.
| Mechanic | Rule |
|---|---|
| On CLOSE | pointer head selects which of the 5 slots to exit |
| On OPEN | fills the next free slot; if all 5 are occupied, OPEN is masked (5 = scale-in ceiling, B3) |
| On HOLD / OPEN | pointer masked (ignored) |
| 1 trade open | pointer forced to that slot |
| 0 trades open | CLOSE action masked entirely |
| Pointer type | categorical, SEPARATE from the Beta size head |
| CLOSE scope (B2) | exit the single pointer-selected trade on the current symbol. FIFO / symbol-flatten RETIRED as the v1 mechanism |
| Telemetry | pointer-head outputs logged for the Risk Doctor (G7) |

### Multi-symbol decision loop 🔴 [M — SOW-B5 LOCKED]
One universal policy over 4 assets:
- Policy steps symbols **SEQUENTIALLY** each 1m bar; each symbol gets its own observation (carrying its 5 slots, per B2)
- **ONE shared account block** (equity, remaining daily-risk buffer, challenge progress) read by every symbol's decision → this is what makes it portfolio-aware (a EURUSD decision sees risk already consumed by an open XAUUSD trade)
- **True-sequential within-bar updates:** each symbol sees the account state ALREADY updated by the prior symbols in the same bar. Guarantees the 4 symbols cannot collectively overshoot the daily-risk buffer in one bar — directly protects the FTMO wall
- Bar-open snapshot REJECTED (would double-spend the risk buffer)
- Open sub-note for SOW #2: symbol processing order = fixed default; flag if you want randomized/rotating later

### Decision frequency 🔴 [M — SOW-B4 answered]
Policy evaluates/acts on **every 1m bar**. 5m + 30m = structure/law context. Laws + risk enforced at the 1m-bar basis (no tick data assumed in v1, per H1/D2).
**Curriculum note [M]:** early phases may mask most 1m timing features (except where a law needs them) so the bot learns structure first; later phases unmask 1m for fine entries/exits.

### raw_size is platform-blind 🔴 [M — SOW-H3]
raw_size → RiskManager: per-trade cap from REMAINING daily risk buffer → lots/contracts/shares with broker rounding, min/max clamps, feasibility checks. Policy never sees the platform. `ftmo_account_size` input scales sizing (10k reference, larger supported — A2).

### Laws run first 🔴 — masking logit −1e9; two enforcement modes (live ban / law-school permission) per THE_TRADING_CODE.md.

### PPO loss 🔴 — `L = L_clip − c1·L_value + c2·entropy`
The policy ratio in `L_clip` uses the **summed log-prob across all three action heads** (direction + Beta size + pointer); `c2·entropy` is the **sum of the three heads' entropies**. The size head contributes only when an OPEN fires; the pointer head contributes only when CLOSE fires (masked otherwise), so masked heads contribute zero log-prob and zero entropy on that step.

### Deployment mode 🔴 [P] — training stochastic (sample all heads); live = **argmax direction · Beta-mean size · argmax pointer slot on CLOSE**, clipped by RiskManager. Live execution fully separated from diagnostics (I4).

---

## THE DIALS — ANSWERED

### G1 Backbone 🔴: **MLP for v1.** Shifted features carry temporal memory; trunk stays fast and stable. LSTM = v2 experiment only if open-trade sequence memory proves the bottleneck.
### G5 Network 🔴: **3×256 shared MLP trunk.** Must generalize across normalized symbols, account sizes, session inputs, law states, and market×trade×account interaction.
### G2 Patience locked 🔴: **γ = 0.997, λ = 0.97** — delayed gratification is non-negotiable.
### G2 Law-school aggression = RANGES + DYNAMIC SCHEDULER 🔴 [M] (metric locked — see G8)
| Dial | Law-school range |
|---|---|
| Entropy coef | 0.03 – 0.08 |
| Clip epsilon | 0.25 – 0.35 |
| Learning rate | 5e-4 – 1e-3 |
| Epochs/rollout | 10 – 15 |
A **missed-opportunity-driven scheduler** moves the live values inside these ranges: aggression stays high while the bot misses premium legal setups, cools as captures improve, cools further for real-data/FTMO-prep phases.

### G8 Missed-opportunity metric 🔴 [M — SOW-G8 LOCKED] (scheduler input)
TRUE for a symbol when ALL three hold:
1. Permitted direction agrees across **5m AND 30m AND 4H** — all three aligned at the same time
2. Bot was **FLAT** on that symbol during the window
3. Price then ran **≥ 1.5 × ATR** in the permitted direction (threshold locked)

Use: counts feed the hand-locked scheduler — many misses → aggression stays high (explore more); few misses → cool down, cooling further on real-data/FTMO-prep phases.
**TRAINING-ONLY signal — never touches reward, masks, or live execution.**
**Critical scope (protects the 4H rule 🔴):** 4H is used ONLY inside this metric as a confirmation lens. Law ACTIVATION is UNCHANGED — 4H is still NOT required to trade (4H Observation Rule stands). This is a measurement filter for the scheduler, not a new law trigger.

### G4 Rollout/minibatch 🔴: early law school **512 / 64** (fast rewrites from rare premium windows) → scale up later phases for steadier refinement.
### G3 Size-head distribution 🔴 [M — SOW-G3 LOCKED]: **Beta.** Outputs raw_size 0–1 (naturally bounded, no clipping). Training samples from Beta (exploration); live outputs the Beta MEAN (deterministic best guess). The pointer head stays a SEPARATE categorical head (B2); size = Beta only. Rejected: clipped Gaussian, squashed Gaussian (edge-value distortion). RiskManager converts the fraction → lots against the remaining daily-risk buffer + broker rounding.
### G6 HPO 🔴 [M]: **Optuna**, on law-school phases, **restricted to non-sacred dials.** Hand-locked and off-limits to Optuna: γ, λ, the aggression scheduler logic. Optuna tunes the rest + later-phase stability.

---

## DIAGNOSTICS & LLM RISK DOCTOR 🔴 [M — G7 + I4 answered, option (d)]
- Telemetry hooks (offline/supervisory ONLY): shared-trunk hidden-state summaries, all four head outputs (direction · size · pointer · value), reward-layer decomposition, FTMO risk telemetry
- After failed/weak evaluations and on live-performance deterioration events: the LLM Risk Doctor reads telemetry → structured diagnosis + prescription (curriculum changes, regime restrictions, reward review, retraining focus, operator alerts)
- **Must include MLP interpretation** — so you can understand the bot's decisions, actor behavior, critic behavior, reward effects, and reasoning from telemetry summaries
- **Never touches live execution, masks, or sizing.** Hard boundary.

---

## VALIDATION 🔴 [M — I1–I3 answered]
| Item | Locked decision |
|---|---|
| Scoreboard ranking | (1) FTMO pass rate → (2) breach count → (3) target-hit consistency → (4) max DD path. Also report: trade win rate, lowest DD% among passing runs, law-protected stand-aside profit time. Raw PnL = diagnostic only |
| Walk-forward | **12mo train / 2mo test / 1mo step / 7 seeds** — the single locked protocol, everywhere |
| 🟡→🟢 promotion | Survives full walk-forward on ≥3 seeds with scoreboard improvement AND no worse breach count |

---

## REJECTED / DEFERRED (unchanged) [C]
Regime ensembles (violates One Universal Policy) · HER relabeling · CNN backbone · Meta-learning v1 · DQN epsilon-bumping.

---

## OPEN POINTERS
**None.** All PPO-side decisions locked (B1/B2/B3/B5 action space + pointer head, G1–G8 dials, validation). Only project-wide item left is SOW-J0 (your final re-read).

---

*Last updated: SOW-B2/B5/G3/G8 sync — four-head architecture (pointer head added), 5 slots/symbol, sequential multi-symbol loop, Beta size head, missed-opportunity metric locked*
