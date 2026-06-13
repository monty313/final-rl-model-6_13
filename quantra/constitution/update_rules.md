# Standing Rules — Update Log (IRAC) + Single Master Test Suite

*Declared 2026-06-13 by the operator. These bind every future session (Claude Code,
the LLM Risk Doctor reading the repo, and any human).*

---

## RULE 1 — Every file carries an IRAC Update Log

Every code file ends with an **UPDATE LOG (IRAC)** block. **Any change to a file
APPENDS a new dated entry** (newest last). It must read like a chronological story
so a future reader — or the LLM Risk Doctor triangulating a pass-rate regression —
can reconstruct *why* the file is the way it is.

Each entry uses the **IRAC** method:

| Letter | Means | Content |
|---|---|---|
| **I** | Issue | What was wrong, missing, or risky **for passing the FTMO challenge**. |
| **R** | Rule | The SOW/blueprint principle, lock, or invariant that governs it. |
| **A** | Application | What was actually changed in this file. |
| **C** | Conclusion | **Always** why this makes the bot pass FTMO **more consistently, with no bug or inefficiency.** |

The Conclusion is non-negotiable: if a change can't be explained as serving
*repeated FTMO-style passing*, it shouldn't be made (SOW R2).

Template (Python files use `#` comments; markdown files use a `## Update Log` section):

```
# [YYYY-MM-DD] <short title>
#   I: <issue, framed against FTMO passing>
#   R: <the governing rule / lock / spec section>
#   A: <what changed here>
#   C: <why this -> more consistent FTMO passing, no bug/inefficiency>
```

**Why this serves the mission:** consistent passing over months requires that no
future edit silently breaks an invariant. The IRAC log turns the codebase into a
self-documenting case file the LLM can read backward along the interpretability
chain (Outcome → Reward → Critic → Actor → Hidden State → Law → State Vector) to
find the first broken link.

> Note: the blueprint mirrors in `docs/` (the binding spec, copied from Drive)
> keep their own `[C — date]` change-comment convention at the source of truth and
> are not edited here, so they never desync from Drive.

---

## RULE 2 — One Master Test Suite

All tests live in **`tests/test_ftmo_master_suite.py`**. There is exactly one
runnable suite; **future tests are APPENDED there** under the matching section,
never scattered into new files. Run the whole folder's guarantees with:

```bash
pytest                                  # discovers the one suite
# or explicitly:
pytest tests/test_ftmo_master_suite.py
```

Fixtures live in `tests/conftest.py` (not a test file). Sections are ordered along
the interpretability chain (runtime/efficiency → data → features → laws → env →
agent → reward → telemetry → validation) and **every test is framed against
repeated FTMO passing**, including code-efficiency guards.

**Why this serves the mission:** one command, run before every commit and every
promotion candidate, proves the substrate the bot trains on is faithful and fast.
A green suite lets the LLM Risk Doctor *rule the substrate out first* (a red data or
no-lookahead test means the bot's world is corrupt — that's the break, not the
actor/critic). Catching errors and inefficiencies here is how we stop the bugs that
would otherwise cost a challenge.

---

## Update Log (IRAC)

- **[2026-06-13]** Standing rules created (folder-wide hardening pass).
  - **I:** The build had FTMO-framed docstrings but no enforced change-history and
    fragmented tests, so future edits could silently break challenge-passing
    invariants and tests could drift apart — exactly the bugs that erode a months-
    long pass streak.
  - **R:** Operator directive (2026-06-13): IRAC log in every file + one master test
    suite; consistent with SOW R2–R4 (comment what/how/why, relative to FTMO).
  - **A:** Authored these two rules; appended IRAC footers to all code files;
    consolidated every test into `tests/test_ftmo_master_suite.py` and deleted the
    split test files; added efficiency/caching guards.
  - **C:** The repo is now a self-documenting, single-command-verifiable case file,
    so regressions are caught before they reach a live challenge and the bot keeps
    passing FTMO consistently with no silent bug or inefficiency.
