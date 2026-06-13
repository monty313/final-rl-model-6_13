"""quantra.market_pipeline.resampler  —  SOW tier: 03_market_pipeline/resampler.

WHAT THIS PACKAGE DOES
----------------------
Builds 5m / 30m / 4H bars from the 1m stream using completed-bar-only semantics so a 1m step never sees an unfinished higher-TF bar.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
The laws read multi-timeframe structure; lookahead there would teach the bot a fantasy edge that evaporates live and breaches. Completed-bar-only protects the pass rate from leakage.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""

# [C - 2026-06-13, M1] Export the resampler API. Connects to resampler.py;
# consumed by the feature builder (M2) which as-of-merges higher TFs onto the 1m
# clock. Why: lookahead-safe multi-TF alignment must be a single shared utility.
from .resampler import (
    TIMEFRAMES,
    as_of_higher_tf,
    build_all_timeframes,
    resample_ohlcv,
)

__all__ = ["TIMEFRAMES", "as_of_higher_tf", "build_all_timeframes", "resample_ohlcv"]


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
