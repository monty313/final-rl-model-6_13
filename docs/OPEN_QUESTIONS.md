# OPEN QUESTIONS
### One item left — SOW-J0.
*57 of 58 SOW items are answered. Everything is written into the blueprint files. Only your final re-read remains.*

**Repo:** https://github.com/monty313/Qunatra_Deep-Reinforcement-Learning-in-Trading.git

---

## THE LAST ITEM

| # | ID | Question | Why it's last | What it unlocks |
|---|---|---|---|---|
| 1 | **SOW-J0** | Final sync-bless: re-read all six blueprint files in order and confirm they're the single source of truth | SOW #2 was drafted FROM these files — confirming J0 finalizes it | Final sign-off on **SOW_2_BUILD_SPEC.md**, ready to hand to Claude Code |

**Note [C — 2026-06-13]:** SOW_2_BUILD_SPEC.md has already been written (added to this folder). It was drafted from the current state of the six blueprint files. J0 is now a final-check / sign-off pass — if your re-read finds something wrong, flag it (→ wtf_are_you_talking_about.md), we patch both the blueprint file AND SOW_2_BUILD_SPEC.md together, then it's ready for Claude Code.

**Reading order for J0:** THE_TRADING_CODE → STATE_VECTOR → REWARD_DESIGN → PPO_ENGINE → SCOPE_OF_WORK.

When you've read them and they're right, say so — SOW_2_BUILD_SPEC.md is ready to hand to Claude Code.

---

## ANSWERED & MOVED (the full 57)
**Section A:** A1 North Star · A2 FTMO MT5 multi-asset, 10k ref · A3 defaults 2.5%/4%
**Section B:** B1 portfolio action space · **B2 per-trade CLOSE via pointer head, N=5 slots/symbol** · B3 scale-in allowed · B4 1m decision frequency · **B5 sequential multi-symbol loop, true-sequential within-bar, shared account block**
**Section C:** C1 TFs 1m/5m/30m/4H · C2 BB encoding from law specs · C3 CCI periods (→ D4) · C4 ATR14 SMA-4 shift-4 · C5 z-scores 10+100 · C6 ADX replaces OBV · C7 candle keep · C8 time keep · **C9 trade block now per-slot ×5 (B2)** · C10 soft-learned categories · C11 equity SMA-1→SMA-4 shift-4 · C12 challenge-progress features
**Section D:** **D1 retired (CCI Confluence → future candidate)** · **D2 retired (Time-Warp period-1; family is period 4)** · **D3 all 12 laws/gates built in v1** · **D4 shifted-SMA period 4 shift 4; CCI pullback 10/100; ATR ref SMA-4 shift-4; F-001→Super Trend 1, Bollinger Push→Trend 1, legal names kept**
**Section E:** E1 Outcome Engine + closed-trade event · E2 momentum (CCI sync + ATR slope) · E3 stagnation (3×5m bars) · E4 exponential pain ramp · E5 target progress tiny · E6 category weighting (breach-risk explicit) · E7 streak base · E8 scale sanity · **E9 QUAD BONUS (Drawdown Efficiency + Law Productivity + Target Velocity payable; TD-stability qualifier; 5%/5%/5%; 95% ceiling; on/off toggle)**
**Section F:** F1 full-chart law-gated curriculum · F2 synthetic optional · F3 costs always on · F4 ADF 100-bar p<0.05 merged with ATR-gate stage · F5 graduation → forward test → real
**Section G:** G1 MLP · G2 γ 0.997 λ 0.97 + aggression ranges/scheduler · **G3 size head = Beta** · G4 rollout 512 / minibatch 64 early · G5 3×256 trunk · G6 Optuna non-sacred dials · G7 telemetry hooks · **G8 missed-opportunity metric: 5m+30m+4H aligned + flat + move ≥1.5×ATR, training-only, 4H rule protected**
**Section H:** H1 GCloud 1m MT5 resampled · H2 $5/lot + spread + slippage · H3 RiskManager conversion · H4 two-phase training walls · H5 manual halt + breach auto-flat
**Section I:** I1 pass-rate scoreboard · I2 walk-forward 12/2/1/7 · I3 promotion ≥3 seeds · I4 LLM Risk Doctor (d) with MLP interpretation
**Section J:** J1 hybrid tier tree · J2 expanded module list · J3 full SOW #2 spec package

---

## NEW SUB-NOTES PARKED FOR SOW #2 (not blockers)
- **B5 symbol processing order:** fixed default each bar; flag if you later want randomized/rotating
- **D1 ±60 2-of-3 CCI logic:** retired as a standalone law, logged as a future law candidate

---

*Last updated: SOW-D4/D3/B2/B5/G3/G8/E9 locked — 57/58, only J0 (your final re-read) remains*
