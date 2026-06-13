# THE TRADING CODE
### The Bot's Permanent Laws
*Laws are guardrails and gates. They run BEFORE PPO action selection through masking logic.*
*They are never reward terms. Reward only governs behavior inside the legal space.*

**Status key:** 🔴 Locked | 🟡 Suggested/In Progress | ❓ Open Question
**Origin key:** [M] = Monty | [P] = Perplexity adopted | [C] = Claude bridge
**Repo:** https://github.com/monty313/Qunatra_Deep-Reinforcement-Learning-in-Trading.git

---

## LAW PRINCIPLE 🔴
- Laws define what directions or trade permissions are legal.
- Enforced by masking: forbidden actions get logit = −1e9 before sampling.
- Laws are NOT reward terms. Ever.
- Every law gets the 8-field definition template (below).

## TWO ENFORCEMENT MODES 🔴 [C — codifies your F1 answer so the coder doesn't guess]
| Mode | How laws act |
|---|---|
| LIVE / deployment | Laws BAN directions. Everything else is legal. Bot trades freely inside the law. |
| LAW SCHOOL (training) | Curriculum flips the default: trading is allowed ONLY when the phase's required law context is active. Laws act as permission gates. |

*Same law definitions, two uses. The mask code must support both modes.*

## OBSERVATION COVERAGE RULE 🔴 [M]
Every indicator and timeframe used by ANY law or gate must also appear in the global observation:
- All law ingredients = mandatory observation features
- Each law/gate adds a compact 0/1 state flag ON TOP of its ingredients
- The flag never replaces the ingredients

## 4H OBSERVATION RULE 🔴 [M — new]
**4H is observed for ALL laws. It is NEVER required for law activation.**
- Every law-family indicator (BB20/BB200, CCI family + applied SMA, shifted SMAs on high/low, ATR + reference) is ALSO computed on 4H
- 4H features enter the state vector as context only
- No law reads 4H to trigger. Activation bindings stay exactly as written per law.
*Purpose: the bot sees the macro picture; the laws stay surgical.*

---

## LAW DEFINITION TEMPLATE 🔴 [M]
Every law and gate must define:
1. Name
2. Exact rule logic
3. Timeframe binding
4. Mirrored buy/sell logic (or note if asymmetric)
5. Masking behavior
6. Law-school usage
7. Observation representation for PPO
8. Normalization / encoding in the state vector

---

# THE CORE LAW STRUCTURE 🔴 [M]
Three families × three laws = **9 core directional laws**:
1. **super trend** — strongest expansion; only continuation is legal
2. **trend** — directional structure; only one side legal
3. **pull back** — retracement inside higher-TF direction; only that direction legal

Plus **miscellaneous gates** (non-directional filters, mainly for training):
ATR Liquidity Gate, Spread Filter, Stationarity Regime Gate.

### Naming reconciliation 🔴 [M — SOW-D4 LOCKED]
Your two original locked laws slot into the grid with their legal names kept:
| Original locked law | Grid position | Logic match |
|---|---|---|
| F-001 The Trend Sovereignty Act 🔴 | Super Trend Law 1 (Bollinger Super Trend) | Identical — above/below outer bands of BB20+BB200 on 5m+30m |
| Bollinger Push No. 1 🔴 | Trend Law 1 (Bollinger Trend) | Identical — above/below midlines of BB20+BB200 on 5m+30m |

*Nothing was loosened. The grid organizes; the laws stand.*

---

## SUPER TREND LAWS

### Super Trend Law 1 — Bollinger Super Trend (= F-001 The Trend Sovereignty Act 🔴)
| Field | Definition |
|---|---|
| Rule | BUY state: price above upper band of both BB20 AND BB200 on both 5m and 30m. SELL state: below lower band of both, both TFs. (Deviation 1) |
| Timeframes | 5m + 30m |
| Mirrored | Yes — symmetric |
| Masking | Buy state → no sells. Sell state → no buys. Neither → no permission granted by this law |
| Law school | Trend/expansion phases; high-conviction continuation gate in mixed phases |
| Observation | 8 distances: price vs BB20 upper/lower + BB200 upper/lower, per TF (5m, 30m) + law-state flag. Plus 4H copies (observation only) |
| Encoding | Distances in ATR units; regime flags −1/0/+1; law flag 0/1; no raw prices |

### Super Trend Law 2 — CCI Super Trend 🔴 (spec per your inventory)
| Field | Definition |
|---|---|
| Rule | CCI applied SMA period 2, shift 4. BUY state: all four CCIs (5m + 30m) above their applied SMA AND above +100. SELL state: all four below applied SMA AND below −100 |
| Timeframes | 5m + 30m |
| CCIs | CCI 30 + CCI 100 per TF [M — SOW-D4 locked] |
| Mirrored | Yes |
| Masking | Buy state → no sells. Sell state → no buys |
| Law school | Momentum-heavy phases; "never fade aligned momentum" drills |
| Observation | CCI30/CCI100 per TF, each minus applied SMA, ±100 threshold flags, law flag. Plus 4H copies |
| Encoding | (CCI − CCI_SMA)/100; flags −1/0/+1; law flag 0/1 |

### Super Trend Law 3 — Shifted SMA Super Trend 🔴 [M — SOW-D4 locked]
| Field | Definition |
|---|---|
| Rule | Shifted SMA on HIGH and LOW (period 4, shift 4). BUY state: price above both lines on 1m, 5m AND 30m. SELL state: below both on all three |
| Timeframes | 1m + 5m + 30m |
| Mirrored | Yes |
| Masking | Buy state → no sells. Sell state → no buys |
| Law school | Stacked-timeframe alignment drills: 1m must agree with 5m and 30m |
| Observation | price − SMA-high and price − SMA-low per TF (6 distances), per-TF agreement flags, law flag. Plus 4H copies |
| Encoding | Distances / ATR; flags −1/0/+1; law flag 0/1 |

---

## TREND LAWS

### Trend Law 1 — Bollinger Trend (= Bollinger Push No. 1 🔴)
| Field | Definition |
|---|---|
| Rule | BUY state: price above MIDLINES of both BB20 and BB200 on both 5m and 30m. SELL state: below both midlines, both TFs |
| Timeframes | 5m + 30m |
| Mirrored | Yes |
| Masking | Buy state → no sells. Sell state → no buys |
| Law school | First trend curriculum — what multi-TF directional agreement looks like |
| Observation | 4 midline distances (BB20/BB200 × 5m/30m) + law flag. Plus 4H copies |
| Encoding | ATR units; flags −1/0/+1; law flag 0/1 |

### Trend Law 2 — CCI Trend 🔴 (spec per inventory)
| Field | Definition |
|---|---|
| Rule | CCI 30 and 100 per TF, applied SMA period 2 shift 4. BUY state: all four CCIs (5m+30m) above their applied SMA. SELL state: all four below |
| Timeframes | 5m + 30m |
| Mirrored | Yes |
| Masking | Buy state → no sells. Sell state → no buys |
| Law school | Basic momentum alignment, before the ±100 super-trend version |
| Observation | The 4 CCIs + each minus applied SMA + law flag. Plus 4H copies |
| Encoding | (CCI − SMA)/100; flags −1/0/+1; law flag 0/1 |

### Trend Law 3 — Shifted SMA Trend 🔴 [M — SOW-D4 locked]
| Field | Definition |
|---|---|
| Rule | Shifted SMA on HIGH and LOW (period 4, shift 4). BUY state: price above both lines on 5m AND 30m. SELL state: below both on both |
| Timeframes | 5m + 30m |
| Mirrored | Yes |
| Masking | Buy state → no sells. Sell state → no buys |
| Law school | Trend structure via shifted lines instead of Bollinger location |
| Observation | 4 distances + per-TF flags + law flag. Plus 4H copies |
| Encoding | Distances / ATR; flags −1/0/+1; law flag 0/1 |

---

## PULL BACK LAWS
*Masking note: pullback laws are written as "buys only / sells only." Functionally in LIVE mode this = ban the opposite direction. In LAW SCHOOL the active pullback state is the permission window.*

### Pull Back Law 1 — Bollinger Pull Back 🔴
| Field | Definition |
|---|---|
| Rule | BUY state: 30m price above midlines of BOTH BBs; 5m price above BB200 midline but BELOW BB20 midline. SELL state: mirror |
| Timeframes | 5m + 30m |
| Mirrored | Yes |
| Masking | Buy state → buys only. Sell state → sells only. Neither → no pullback permission |
| Law school | Core pullback curriculum: enter with the higher TF while the lower TF dips |
| Observation | 30m BB20/BB200 midline distances, 5m BB20/BB200 midline distances, pullback-shape flag, law flag. Plus 4H copies |
| Encoding | ATR units; flags −1/0/+1; law flag 0/1 |

### Pull Back Law 2 — CCI Pull Back 🔴 [M — SOW-D4 locked: small=10, large=100]
| Field | Definition |
|---|---|
| Rule | Applied SMA period 2 shift 4. SMALL CCI = 10, LARGE CCI = 100. BUY state: 30m both CCIs above their applied SMA; 5m LARGE (100) CCI above its SMA while SMALL (10) CCI is below its SMA. SELL state: mirror |
| Timeframes | 5m + 30m |
| Mirrored | Yes |
| Masking | Buy state → buys only. Sell state → sells only |
| Law school | Momentum desync drills: lower-TF small-CCI weakness inside higher-TF alignment = entry, not reversal [M — your original 2.7 insight] |
| Observation | All 4 CCIs + each minus SMA + 5m sync/desync indicator + law flag. Plus 4H copies |
| Encoding | (CCI − SMA)/100; flags −1/0/+1; law flag 0/1 |

### Pull Back Law 3 — Shifted SMA Pull Back 🔴 [M — SOW-D4 locked]
| Field | Definition |
|---|---|
| Rule | Shifted SMA on HIGH and LOW (period 4, shift 4). BUY state: 5m AND 30m price above both lines; 1m price BELOW both lines. SELL state: mirror |
| Timeframes | 1m + 5m + 30m |
| Mirrored | Yes |
| Masking | Buy state → buys only. Sell state → sells only |
| Law school | Micro-structure pullback: 1m weakness inside 5m+30m alignment = entry window |
| Observation | 6 distances (3 TFs × high/low) + HTF alignment flag + 1m countertrend flag + law flag. Plus 4H copies |
| Encoding | Distances / ATR; flags −1/0/+1; law flag 0/1 |

---

## MISCELLANEOUS GATES (non-directional; mainly training)

### ATR Liquidity Gate 🔴 [M]
| Field | Definition |
|---|---|
| Rule | ATR vs its shifted reference (SMA period 4, shift 4 — SOW-D4 locked). Trading allowed ONLY when ATR > reference on BOTH gate TFs |
| Timeframes | 1m + 30m (working version) |
| Masking | Condition false → no NEW buys or sells. Open-position management unaffected |
| Law school | Trade only when movement exists; never learn habits in dead markets |
| Observation | ATR + reference + (ATR − ref) per gate TF + gate flag. Plus 4H copies |
| Encoding | Normalized by rolling ATR baseline; gate flag 0/1 |

### Spread Filter 🔴 [M]
| Field | Definition |
|---|---|
| Rule | Trading allowed ONLY when current spread < high–low range of the last 1m candle |
| Masking | False → no new trades. Management unaffected |
| Law school | Learn under realistic execution; also retained live |
| Observation | spread, last-1m range, spread/range ratio, gate flag |
| Encoding | Spread normalized by ATR or candle range; flag 0/1 |

### Stationarity Regime Gate 🔴 [M]
| Field | Definition |
|---|---|
| Rule | Rolling ADF test, 100-bar window, p < 0.05 = stationary (per F4). Mode A: trade only when stationary. Mode B: trade only when NOT |
| Masking | Active mode condition false → no new trades |
| Law school | One phase per mode. Regime awareness, not entry timing. Merged with ATR-gate stage per your F4 answer |
| Observation | regime code, binary indicator, normalized test stat, gate flag |
| Encoding | Binary/one-hot; stat normalized; flag 0/1 |

---

## SUPERSEDED / RECONCILED 🔴 (SOW-D4 CLOSED) [M]
| Earlier spec | Resolution |
|---|---|
| D1 "CCI Confluence Law" (3 CCIs 10/30/100, 2-of-3 ±60, SMA-2 shift-4, 1m+30m) | RETIRED as standalone. CCI Trend + CCI Super Trend cover it. ±60 2-of-3 logic logged as future candidate. |
| D2 "Time-Warp Doctrine" (SMA period 1) | RETIRED. Shifted-SMA family is **period 4, shift 4** across all three SMA laws. [M — D4 decision; this is the FLIP from the period-1 default] |

**Locked families [M — SOW-D4]:**
- CCI family: observation carries 10 / 30 / 100; laws bind 30 + 100; pullback small = 10 / large = 100
- Shifted-SMA family: period 4, shift 4, all three SMA laws
- ATR gate reference: SMA-4, shift-4
- F-001 Trend Sovereignty Act → Super Trend Law 1; Bollinger Push No. 1 → Trend Law 1; legal names kept

## V1 SCOPE 🔴 (SOW-D3 CLOSED) [M]
**v1 builds ALL 12 at once: 9 core directional laws + 3 gates** (ATR Liquidity, Spread, Stationarity).
- No subset / phased build. The complete LawMask module is built up front.
- The curriculum activates laws stage by stage at TRAINING time, not build time — so the code and the law book stay in sync.

---

## ENV / DECISION LOOP (cross-ref PPO_ENGINE.md) 🔴 [M — SOW-B2 + B5]
The law book governs WHAT is legal; the env executes it. Two locked decisions live in full in PPO_ENGINE.md and are summarized here because LawMask must respect them:
- **Per-trade CLOSE via pointer head (B2):** N = 5 trade slots per symbol. On CLOSE the policy's pointer head selects WHICH slot to exit. CLOSE is masked when 0 trades are open on the symbol; the pointer is forced when exactly 1 is open. FIFO/symbol-flatten retired as the v1 mechanism.
- **Multi-symbol loop (B5):** one universal policy steps the 4 symbols SEQUENTIALLY each 1m bar, each symbol carrying its 5 slots, sharing ONE account block, with true-sequential within-bar account updates so the symbols cannot collectively overshoot the daily-risk buffer in one bar.

---

*Last updated: SOW-D4/D3 sync — shifted-SMA period 4 locked, CCI 10/100 pullback locked, ATR ref SMA-4 locked, D1/D2 retired, all 12 laws/gates v1, B2/B5 env cross-ref added*
