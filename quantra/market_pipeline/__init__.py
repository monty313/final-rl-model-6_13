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
