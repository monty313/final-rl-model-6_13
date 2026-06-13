# Safety Boundaries

## The LLM Risk Doctor — read-only across the entire repo (SOW R5, §9.3)

**MAY:**
- Read all telemetry and all interpretability artifacts.
- **READ-ONLY access to the entire repo** (blueprint + codebase) — it may VIEW any
  file to support reasoning.
- Produce diagnoses + prescriptions per the output template in
  `docs/MLP_INTERPRETABILITY_LAYER.md`.

**MAY NOT:**
- Write, modify, or delete ANY file.
- Touch execution, action masks, sizing, or hard walls.
- Issue broker commands.
- Override the operator.

**Mandatory read:** the Risk Doctor must read
`docs/MLP_INTERPRETABILITY_LAYER.md` on EVERY diagnosis session. The codebase
**fails loudly** if the LLM is invoked without that file being accessible.

**No 9th category:** every failure is classified into exactly one of the 8 taxonomy
items. If none fit, it reports *"unclassified — additional telemetry required"* and
stops. It does NOT invent a 9th category.

## Live deployment hard kill switches (SOW §10.1)
- **Manual halt** (operator action) — always available, always immediate.
- **Breach auto-flat** (4% trailing wall) — automatic, all positions, lock out for
  the day.

## Training-vs-live separation (SOW C7, §12.3)
- Training runs are batch jobs (Colab / cloud).
- Live runs are isolated processes on the deployment machine.
- The LLM Risk Doctor reads **checkpointed** telemetry — it never sees live state in
  real time and never touches live execution.

## Financial-action guardrail (operator-level)
This codebase plans and sizes trades and can place them via the live bridge only
when the operator explicitly runs the live runner. No automated process here moves
money without that explicit operator action plus the kill switches above.
