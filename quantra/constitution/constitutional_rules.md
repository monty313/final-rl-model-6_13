# Constitutional Rules — the 9 hard architectural commitments (SOW §1.5)

| # | Rule |
|---|---|
| **C1** | One universal policy. No regime-specialist ensembles. |
| **C2** | Multi-asset day one: FTMO MT5, 4 symbols, real costs day 1, no costless world. |
| **C3** | Defaults: 2.5% daily target / 4% trailing loss. Configurable at runtime. |
| **C4** | Decision frequency: every 1m bar. 5m/30m/4H carry structure context. |
| **C5** | Laws are masks, not rewards. Pre-mask logits set to −1e9 on forbidden actions. |
| **C6** | Layer 0 (net PnL) dominates the reward. No shaping layer overrides it (E8). |
| **C7** | Live execution is fully separated from diagnostics. LLM Risk Doctor is offline/read-only/supervisory. |
| **C8** | Real FTMO costs from training day 1. No costless warm-up. |
| **C9** | Full-chart curriculum — never snippets. Stages gate by law context, not by chart slicing. |

## The two rules that override everything (SOW R5)
- **Laws are NEVER reward terms.** They run BEFORE reward as hard masks
  (logit = −1e9 on forbidden actions).
- **Layer 0 (net PnL) always dominates the reward** — no shaping layer wins the
  reward game while losing the trading game (the E8 rule).

## Locked items
🔴 No locked item changes without Monty's explicit approval. Propose amendments;
don't apply them. Locked set includes: γ=0.997, λ=0.97; 3×256 trunk; four-head
architecture; 5 slots/symbol; Beta size head; two-phase episode rule; the 12
laws/gates and their indicator parameters; the walk-forward protocol (12/2/1/7).


---

## Update Log (IRAC) — standing rule since 2026-06-13
*Every change appends a dated IRAC entry; the **Conclusion** always states why it
makes the bot pass FTMO more consistently. Rule: [update_rules.md](update_rules.md).*

- **[2026-06-13]** C1-C9 cross-referenced to the new standing rules.
  - **I:** The constitutional rules needed the IRAC + master-suite rules linked for auditability.
  - **R:** Operator IRAC rule (2026-06-13).
  - **A:** Added this update log pointing to update_rules.md.
  - **C:** The invariants stay enforced and auditable, which is what protects a months-long pass streak.
