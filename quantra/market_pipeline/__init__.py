"""quantra.market_pipeline  —  SOW tier: 03_market_pipeline.

WHAT THIS PACKAGE DOES
----------------------
Turns raw MT5 1m bars into the policy's world: ``data_loader`` (Drive/local CSV ->
clean UTC-indexed bars + Parquet cache), ``resampler`` (5m/30m/4H from 1m, no
lookahead), ``feature_builder`` (the ~145-scalar state vector, offline-precomputed
+ memmapped), and ``law_mask_engine`` (law/gate states -> action mask).

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
If the state vector doesn't faithfully describe the FTMO-relevant situation, the
MLP can't form a useful belief about challenge state (MLP_INTERPRETABILITY_LAYER
Term 1). This tier guarantees a complete, normalized, lookahead-free observation —
and does the heavy feature math ONCE, offline, so training stays fast and cheap.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""


# ─────────────────────────────────────────────────────────────────────────────
# UPDATE LOG (IRAC) - standing rule since 2026-06-13.
# Every change to this file APPENDS a dated IRAC entry below (newest last):
#   I (Issue) / R (Rule) / A (Application) / C (Conclusion -> why this makes the
#   bot pass FTMO MORE CONSISTENTLY, with no bug or inefficiency). The LLM Risk
#   Doctor reads this log to reconstruct the chronological 'why' when
#   triangulating a pass-rate regression. Rulebook: docs/MLP_INTERPRETABILITY_LAYER.md
# ─────────────────────────────────────────────────────────────────────────────
# [2026-06-13] Package documented under the new IRAC rule.
#   I: Scaffolded in M0 with a header docstring but no standing change-log, so future FTMO-relevant implementation could drift undocumented.
#   R: SOW R2-R4 + the new IRAC update-log rule (2026-06-13).
#   A: Confirmed the header states the package's FTMO role + the LLM rulebook pointer; added this IRAC log as the permanent change-story anchor for when real code lands.
#   C: A documented, discoverable package keeps its future implementation aligned to repeated FTMO passing and prevents silent, bug-introducing drift.
