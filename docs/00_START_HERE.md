# 00 — START HERE
### Quantra: Deep-Reinforcement-Learning-in-Trading — Blueprint Folder
**GitHub:** https://github.com/monty313/Qunatra_Deep-Reinforcement-Learning-in-Trading.git

---

## WHAT'S IN THIS FOLDER

| File | What it is | When to open it |
|---|---|---|
| **OPEN_QUESTIONS.md** | THE FINAL 8 — the work queue | Every working session, FIRST |
| **SCOPE_OF_WORK.md** | Master tracker, 50/58 done, cohesion audit | To check overall progress |
| **THE_TRADING_CODE.md** | The 9-law + 3-gate inventory, masking rules | Reference for any law question |
| **STATE_VECTOR.md** | Every feature the bot sees, 4 timeframes | Reference for any feature question |
| **REWARD_DESIGN.md** | Layered reward + parked Triad Bonus model | Reference for any reward question |
| **PPO_ENGINE.md** | Architecture, dials, action space | Reference for any PPO/architecture question |
| **MLP_INTERPRETABILITY_LAYER.md** | Add-on diagnostics contract + the LLM Risk Doctor's operating manual (definitions, rules, failure taxonomy, output template) | Reference for any diagnostics/Risk-Doctor question; binding for the live LLM at inference |
| **SOW_2_BUILD_SPEC.md** | The complete Claude Code build spec (Mission → Definition of Done, M0–M15 implementation order) | Hand this to Claude Code to build the bot |
| **wtf_are_you_talking_about.md** | Correction log — errors never to repeat | If something gets flagged as wrong |

---

## CURRENT STATUS
**SOW #2 is generated.** `SOW_2_BUILD_SPEC.md` is the complete Claude Code build spec. SOW-J0 (your final re-read of the six blueprint files) is the only thing standing between this and handing the spec to Claude Code — do J0, then start the build.

---

## HOW TO WORK A SESSION
1. **If J0 isn't done yet:** open OPEN_QUESTIONS.md, re-read the six blueprint files in the order below, confirm they're correct. If something's wrong, log it in `wtf_are_you_talking_about.md` immediately.
2. **Once J0 is blessed:** hand `SOW_2_BUILD_SPEC.md` to Claude Code. It tells Claude Code to read this whole folder first, then build in the M0→M15 order.
3. **During the build:** if any blueprint file needs updating (new decision, amendment, correction), follow the STANDING RULES below — every update gets a what/how/why comment.

---

## READING ORDER (first time / context refresh)
1. THE_TRADING_CODE.md
2. STATE_VECTOR.md
3. REWARD_DESIGN.md
4. PPO_ENGINE.md
5. MLP_INTERPRETABILITY_LAYER.md
6. SCOPE_OF_WORK.md

*(OPEN_QUESTIONS.md = the work queue, read anytime)*

---

## TAGS USED THROUGHOUT
- **[M]** = Monty's idea / from his notes
- **[P]** = Perplexity suggestion, adopted
- **[C]** = bridge/addition, acting as Monty

New content added during sessions always gets tagged.

---

## HARD RULES — NEVER VIOLATE
- Laws are NEVER reward terms. They run before the reward as hard masks.
- Layer 0 (net PnL) always dominates the reward — no shaping layer wins the reward game while losing the trading game.
- No 🔴 locked item changes without Monty's explicit approval. Propose amendments; don't apply them.

---

## STANDING RULES FOR ANY LLM TOUCHING THIS PROJECT
*(These apply to Claude Code building the codebase, the LLM Risk Doctor diagnosing it, and any LLM editing these blueprint files later.)*

### For any LLM updating files in this folder
Every update MUST leave a comment at the change site explaining:
1. **What** was changed.
2. **How** it connects with the rest of the folder (which files / sections / locks it touches).
3. **Why** the change was made.

The goal is simple: future sessions never get lost reconstructing why a thing is the way it is.

### For Claude Code building the codebase
- **Comment EVERYTHING relative to passing the FTMO challenge.** Every function, every reward term, every law, every mask, every telemetry hook — the comment must say what it's for AND how it serves repeated FTMO-style passing (not generic ML accuracy, not raw PnL).
- **Leave detailed inline comments telling the LLM Risk Doctor HOW TO THINK** when reading that code. The comments are the LLM's safety rail — without them, it gets lost in the codebase and starts inventing.
- **Every module file MUST reference `MLP_INTERPRETABILITY_LAYER.md` in its header docstring** — that file is the LLM's binding rulebook at inference time. The codebase must point the LLM at it on every entry.

### For the LLM Risk Doctor (diagnostics layer)
- **MUST read `MLP_INTERPRETABILITY_LAYER.md` first** — it contains the definitions, rules, failure taxonomy, reverse-chain reasoning protocol, and the diagnostic output template the Risk Doctor is required to follow.
- **HAS READ-ONLY ACCESS** to the entire repo (this blueprint folder + the eventual codebase). It can VIEW any file in the repo to support its reasoning. This is intentional — its diagnoses are stronger when it can cross-reference the code it's interpreting against the spec it was built from.
- **MAY NOT** write to, modify, or delete ANY file. Its outputs are diagnoses and prescriptions only — never edits, never execution, never touching masks/sizing/walls. Hard boundary.

---

## ENDPOINT
1. **SOW-J0** — Monty re-reads all six blueprint files in the order above and confirms they're the single source of truth.
2. **Hand `SOW_2_BUILD_SPEC.md` to Claude Code** — it's already written, per the J3 structure (Mission, Locked Architecture, Repo Tree, Module Contracts, State & Features, Reward System, Curriculum, Validation, Diagnostics, Live Deployment, Acceptance Tests, Operator Appendix, Implementation Order M0–M15, Milestone Checklist, Definition of Done).

*[C — 2026-06-13: Updated to reflect SOW #2 already generated (SOW_2_BUILD_SPEC.md added to folder). Previously this section described SOW#2 as a future deliverable; it's now complete and ready to hand to Claude Code. Connects to: file inventory table above, CURRENT STATUS section, HOW TO WORK A SESSION section — all three updated together so the front door stays internally consistent.]*

---

*This file is the front door. Everything else lives at the same level in this folder.*
