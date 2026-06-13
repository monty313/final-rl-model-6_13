# STATE VECTOR
### Everything the Bot Sees When It Makes a Decision
*Four blocks — Market, Time, Trade, Account. The bot sees all four every 1m step.*

**Status key:** 🔴 Locked | 🟡 Suggested | ❓ Open
**Origin key:** [M] = Monty | [P] = Perplexity adopted | [C] = Claude bridge
**Repo:** https://github.com/monty313/Qunatra_Deep-Reinforcement-Learning-in-Trading.git

---

## THE THREE-LAYER PRINCIPLE 🔴 [M]
> Market state = what price is doing.
> Trade state = what I'm holding.
> Account state = is my whole behavior moving toward FTMO success or toward the wall.

## TIMEFRAME UNIVERSE 🔴 [M — SOW-C1 answered]
**1m, 5m, 30m, 4H.**
| TF | Role |
|---|---|
| 1m | Decision/execution frame: micro confirmation, pullback timing, spread reference. Policy acts every 1m bar (SOW-B4) |
| 5m | Execution structure / lower trend |
| 30m | Higher-TF trend / regime |
| 4H | **Observation only — never a law trigger.** Same indicators as 5m/30m, context for the bot's macro view (4H Observation Rule, THE_TRADING_CODE.md) |

Not every law uses every TF. Bindings are per-law. The architecture supports all four.

## LAW-INGREDIENT COVERAGE RULE 🔴 [M]
Every indicator + TF used by any law or gate is a mandatory observation feature, plus one compact 0/1 flag per law/gate. Flags never replace ingredients.

## ENCODING / NORMALIZATION RULES 🔴 [P adopted]
| Type | Rule |
|---|---|
| Raw prices | Never fed raw — returns or distance-from-reference only |
| Distances | Divide by ATR |
| Unbounded (CCI etc.) | (X − X_SMA)/100 or rolling z-score |
| Bounded | Rescale to [−1, 1] |
| Regime flags | −1 / 0 / +1 |
| Law/gate flags | 0 / 1 |
| Account features | Normalize by initial balance / risk budget |

---

# BLOCK 1 — MARKET STATE

### 1. Bollinger Structure 🔴 (encoding derived from law definitions — SOW-C2 resolved)
BB20 + BB200, deviation 1. Per law specs: midline distances, outer-band distances, in ATR units, on 5m + 30m (+ 4H observation copies). Feeds Super Trend 1, Trend 1, Pull Back 1.

### 2. CCI Family 🔴 (SOW-D4 LOCKED)
- Observation family: CCI 10 / 30 / 100 per TF, applied SMA period 2 shift 4 on each
- Computed on 1m, 5m, 30m (+ 4H copies)
- Encoding: each CCI, each (CCI − applied SMA)/100, sync/desync indicators per law specs
- Your core insight [M]: small CCI desyncing from large ones, then snapping back = the pullback signal
- Law bindings (D4 locked): Super Trend 2 + Trend 2 bind CCI 30+100; Pull Back 2 binds small=10 / large=100. Observation carries all three (10/30/100).

*[C — 2026-06-13, J0 sync]: Removed the stale ❓ — already resolved in SOW-D4 (locked in THE_TRADING_CODE.md and SCOPE_OF_WORK.md). No content change, just removing a confirm-flag that was already answered.*

### 3. ATR Regime 🔴 [M — SOW-C4 + D4 confirmed]
- ATR14 with applied SMA period 4, shift 4, on **1m and 30m** (+ 4H copies)
- Features: ATR14 per TF, its applied-SMA reference per TF, normalized (ATR − reference) per TF
- Powers the ATR Liquidity Gate — gate reference = SMA-4, shift-4 (D4 confirmed C4's spec, no change)

*[C — 2026-06-13, J0 sync]: Removed the stale ❓ — D4 confirmed C4 (SMA-4 shift-4) as the ATR gate reference, resolving the earlier-notes conflict. No content change, just removing a resolved confirm-flag.*

### 4. Shifted SMA Structure 🔴 (SOW-D4 LOCKED)
- SMA **period 4, shift 4**, applied to HIGH and LOW (the period-1 "Time-Warp" option was retired — D2)
- Computed on 1m, 5m, 30m (+ 4H copies)
- Encoding: (price − line)/ATR per line per TF + alignment flags
- Feeds Super Trend 3, Trend 3, Pull Back 3

*[C — 2026-06-13, J0 sync]: This was the most stale entry in the file — it still read "period 1 OR 4, your call" and referenced "Time-Warp Doctrine reconciliation" as if still open. SOW-D4 locked this to period 4, shift 4 (and D2 retired the period-1 Time-Warp family entirely). Updated to match THE_TRADING_CODE.md and SCOPE_OF_WORK.md, which already had it right. No design change — just closing the loop on a file that hadn't been updated when D4 closed.*

### 5. Z-Score (Pullback Depth) 🔴 [M — SOW-C5 answered]
- TWO lookbacks per TF: **10 and 100**
- On 1m, 5m, 30m (+ 4H copies 🟡 — consistent with 4H rule; cheap)
- Purpose: short-horizon vs long-horizon deviation → temporary retracement vs broader continuation
- Encoding: z per lookback per TF

### 6. ADX Trend Strength 🔴 [M — SOW-C6 answered; REPLACES the old OBV feature everywhere]
- ADX 5 and ADX 15 on **1m and 30m** (+ 4H copies)
- 4+ scalars: ADX5_1m, ADX15_1m, ADX5_30m, ADX15_30m, normalized /100
- Observation feature only — NOT a directional law in v1

### 7. Candle Structure 🔴 [P — SOW-C7 answered: keep]
- On the execution TF (1m): bar return, range/ATR, upper-wick ratio, lower-wick ratio
- Cheap rejection/expansion/push info the slower indicators smooth over

---

# BLOCK 2 — TIME CONTEXT 🔴 [P — SOW-C8 answered: keep]
- sin/cos hour-of-day + day-of-week encoding
- Forex sessions (Asia/London/NY) behave differently; cyclical encoding keeps midnight neighbors adjacent

---

# BLOCK 3 — TRADE STATE 🔴 [M — SOW-C9 + B2 amendment: PER-SLOT ×5]
The trade-state block is repeated for each of the **5 trade slots per symbol** (per SOW-B2 pointer head). Each slot carries:
| Per-slot feature | Detail |
|---|---|
| Position direction | flat/long/short → −1/0/+1 |
| Unrealized PnL | in R or % |
| Holding age | time in trade |
| Entry distance | in ATR units |
| MFE / MAE | max favorable / adverse excursion |
| Momentum flag | continuing vs weakening, from active momentum context |
| **Occupied flag** | 0/1 — is this slot in use? |

**Empty slots: zero-filled + occupied flag = 0.** So the block is a fixed 5×(features) shape regardless of how many trades are open — the pointer head reads it to pick which slot to CLOSE.

**Portfolio aggregates [M — SOW-B5]:** on top of the 5 per-slot blocks, compact aggregates across slots (net exposure count, net size, total uPnL) feed the policy. The shared ACCOUNT block (Block 4) is what carries cross-symbol awareness — a EURUSD decision sees risk consumed by an open XAUUSD trade.

---

# BLOCK 4 — ACCOUNT STATE 🔴 [M — SOW-C10/C11 + challenge addition answered]

### Your macro equity construction (C11 confirmed exactly as written) [M]
1. Take total equity → SMA period 1 (the equity line)
2. Apply SMA period 4, shift 4, to that line → the shifted baseline
3. Baseline powers: equity deviation, equity trend direction, macro category context

### The block
| Feature | Detail |
|---|---|
| Normalized equity E(t) | equity / initial balance |
| Equity deviation | E(t) − shifted-SMA4 baseline |
| Equity slope | Δ of the SMA4 baseline |
| Trailing-loss buffer | distance to the trailing wall |
| Daily-loss buffer | distance to today's limit |
| **Daily challenge progress** [M] | day's realized+unrealized PnL vs DAILY_TARGET |
| **Overall challenge progress** [M] | total equity vs initial balance |

### Macro categories — SOFT-LEARNED (C10 answered) [M]
- Do NOT hard-code cutoffs for advancing / neutral / warning / recovery — PPO learns the soft boundaries from the raw account features above
- ONLY **breach-risk** stays explicitly tied to hard challenge-risk proximity (real external constraint)
- Consequence for reward Layer 5: category weighting keys off breach-risk explicitly; other regimes are learned context, not coded bins

---

## STATE VECTOR SHAPE (updated estimate) 🟡
| Group | Approx. scalars |
|---|---|
| Bollinger distances (5m+30m, mid+outer) + flags | ~12 |
| Bollinger 4H copies | ~6 |
| CCI family (3 CCIs × 2 forms × 3 TFs) + sync flags | ~22 |
| CCI 4H copies | ~7 |
| ATR (1m+30m: level, ref, diff) | ~6 |
| ATR 4H copies | ~3 |
| Shifted SMA (3 TFs × 2 lines) + flags | ~9 |
| Shifted SMA 4H copies | ~3 |
| Z-scores (2 lookbacks × 3 TFs) | ~6 |
| Z-score 4H copies | ~2 |
| ADX (1m+30m × 2 periods) | ~4 |
| ADX 4H copies | ~2 |
| Candle structure (1m) | ~4 |
| Time context | ~3 |
| Law/gate state flags (9 + 3) | ~12 |
| Trade state — PER-SLOT ×5 (7 features × 5 slots) | ~35 |
| Portfolio aggregates across slots | ~3 |
| Account state | ~7 |
| **Total (v1 estimate)** | **~145 scalars** |

*Grew to ~145 because: 1m everywhere, 4H observation copies, dual z-scores, 12 law/gate flags, challenge features, and the per-slot ×5 trade block (SOW-B2). Still tractable for a 3×256 trunk (SOW-G5). Every scalar passes the law-coverage or admission rule.*

---

## REMOVED / REPLACED
- ~~OBV shifted-SMA feature~~ → REPLACED by ADX (SOW-C6). All OBV references retired.
- Raw OHLC, CNN tensors, pair-spread z-score — still rejected as before.

---

*Last updated: SOW-J0 sync — removed three stale ❓ markers (CCI periods, ATR gate ref, shifted-SMA period) that SOW-D4 had already locked; STATE_VECTOR now matches THE_TRADING_CODE.md exactly. No architecture changes. Trade-state block remains per-slot ×5; shape ~145 scalars.*
