# Quantra — Mission

> **The single mission anchors everything (SOW R1).**

Quantra is **one universal PPO policy** built to **repeatedly pass FTMO-style
challenges over time** — default **2.5% daily target**, **4% trailing wall** —
across many walk-forward windows and seeds.

**It is NOT built to maximize PnL.** Raw PnL is a diagnostic sanity check only.

## The only ranking that matters (the scoreboard)
1. **FTMO pass rate**
2. **Breach count** (lower is better)
3. **Target-hit consistency**
4. **Max drawdown path**

## What success means
The bot passes FTMO-style challenges repeatedly across walk-forward windows on
**≥3 of 7 seeds**, with stable or improving scoreboard metrics.

## Runtime inputs (pure runtime memory — no strategy config file)
- `daily_target_pct` (default 2.5)
- `daily_risk_pct` (default 4.0)
- `ftmo_mode` (default True)
- `ftmo_account_size` (default 10,000 — reference scaling only; the policy is
  account-size-blind via its normalized size output)

## The test every line of code must pass
> If a piece of code can't explain how it serves **repeated FTMO-style passing**,
> it probably shouldn't be there (SOW R2).

Every module references `docs/MLP_INTERPRETABILITY_LAYER.md` — the binding rulebook
for the LLM Risk Doctor and the interpretability layer.


---

## Update Log (IRAC) — standing rule since 2026-06-13
*Every change appends a dated IRAC entry; the **Conclusion** always states why it
makes the bot pass FTMO more consistently. Rule: [update_rules.md](update_rules.md).*

- **[2026-06-13]** Mission doc anchored under the IRAC rule.
  - **I:** The mission statement had no change-history anchor.
  - **R:** Operator IRAC rule (2026-06-13).
  - **A:** Added this update log.
  - **C:** A stable, logged mission keeps every module anchored to passing FTMO, not chasing PnL.
