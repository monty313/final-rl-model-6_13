# RAW_INPUTS — operator override, risks & safeguards

**Decision [2026-06-13, operator]:** the observation includes a `market_raw` block of
**30 UNNORMALIZED features** — raw SMA (period-1 shift 0–3, SMA-30, SMA-50 on
5m/30m/4H) and raw CCI (10/30/100 on 1m/5m/30m/4H) — **in addition to** the existing
normalized/ATR-scaled features (nothing was removed). Toggle:
`quantra.runtime.config.INCLUDE_RAW_INPUTS` (default `True`). Dim: 146 → **176**.

This intentionally **overrides** `STATE_VECTOR.md`'s encoding rule *"raw prices:
never fed raw — returns or distance-from-reference only."* The operator wants the
policy to also see un-transformed levels. This file records the risks that rule was
protecting against and the safeguards we will add so the override doesn't cost
pass-rate.

## Why this is risky (what the no-raw-price rule prevents)
1. **Non-stationarity / scale.** Raw price levels drift over years and differ wildly
   across symbols (EURUSD ~1.1 vs US30 ~34,000). Fed unscaled into a 3×256 MLP they
   dominate gradients and destabilize training → **Representation Chaos**.
2. **Shortcut learning.** Absolute price/level is a near-unique fingerprint of date
   and symbol. The policy can memorize "in this price band, do X" — great in
   backtest, collapses live when price moves to a new band → **Shortcut Learning**
   (failure-taxonomy #8). This directly threatens *consistent* passing across
   windows/seeds.
3. **Platform-blindness break.** Raw levels couple the policy to a symbol's price
   scale, undermining the "one universal brain, account-size-blind" goal (SOW A2/H3).
4. **`raw_sma1` redundancy.** SMA period 1 = price; shifts 0–3 are just lagged
   closes, highly collinear with each other and partly with the existing z-scores +
   `candle_return`. Low marginal information for the added input width.

## Safeguards already in place (M2)
- **Isolated + flagged.** Raw features live in their own `market_raw` block and in
  `schema.RAW_FEATURE_NAMES`, so every consumer can treat them specially and the LLM
  can attribute instability to them specifically.
- **Not clipped.** The FeatureBuilder clips only the normalized block; raw levels
  pass through intact (clipping raw price to ±10 would destroy it).
- **Toggleable for ablation.** Flip `INCLUDE_RAW_INPUTS=False` to rebuild the 146-dim
  schema and run a clean raw-vs-normalized comparison on the scoreboard.
- **Change-guarded.** The snapshot guard + impact tool track this block; any further
  change fails the suite with a checklist.

## Safeguards to ADD (scaling / stability — for M5 and the ablation)
1. **Input standardization layer (REQUIRED, M5).** The PPO agent must standardize the
   raw block before the trunk — a running mean/std (VecNormalize-style) **or** offline
   per-feature, **per-symbol** z-stats computed on the training window only (never
   leaking test data). The normalized block is already bounded and should bypass this.
   *This is the single most important safeguard; without it, expect instability.*
2. **Prefer returns/log-levels if instability persists.** If standardized raw levels
   still misbehave, switch `raw_sma*` to log-price or to differences (`price[t]−price[t−k]`)
   — stationary cousins that keep the intent.
3. **Per-symbol normalization stats.** Because of the EURUSD-vs-US30 scale gap, fit and
   apply standardization **per symbol**, not globally.
4. **Monitor for shortcut learning (M10/M11).** Watch the correlation heatmap + hidden
   projection: if pass-day outcomes scatter across hidden states or held-out
   symbols/dates collapse, the Risk Doctor flags Shortcut Learning → prescription:
   reduce/disable the raw block (`INCLUDE_RAW_INPUTS=False`) and re-validate.
5. **Ablate before trusting (M12).** Run baseline(146) vs candidate(176) through the
   same walk-forward; the raw block must clear the `PromotionGate` (≥3 seeds, scoreboard
   improvement, no worse breach) on **pass-rate**, not PnL. Cheap pre-screen: zero the
   raw block at inference on a trained candidate and measure pass-rate delta (~0 ⇒ drop it).

## Update Log (IRAC) — standing rule since 2026-06-13
- **[2026-06-13]** Documented the raw-input override + safeguards.
  - **I:** Raw, unnormalized levels can destabilize the MLP and invite shortcut learning,
    threatening consistent passing.
  - **R:** Operator directive to add raw SMA/CCI while keeping the normalized features;
    overrides the no-raw-price rule for this block only.
  - **A:** Isolated + flagged + unclipped + toggleable raw block; recorded the required
    M5 standardization + the ablation/monitoring plan here.
  - **C:** The policy gets the requested raw signal with a clear stability plan and a
    clean off-ramp, so if raw inputs hurt pass-rate we disable them without touching the
    rest of perception — the override can't quietly break consistent passing.
