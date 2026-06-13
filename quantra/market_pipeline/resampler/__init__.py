"""quantra.market_pipeline.resampler  —  SOW tier: 03_market_pipeline/resampler.

WHAT THIS PACKAGE DOES
----------------------
Builds 5m / 30m / 4H bars from the 1m stream using completed-bar-only semantics so a 1m step never sees an unfinished higher-TF bar.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
The laws read multi-timeframe structure; lookahead there would teach the bot a fantasy edge that evaporates live and breaches. Completed-bar-only protects the pass rate from leakage.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
