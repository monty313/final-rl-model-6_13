"""quantra.locked_core.risk_manager  —  SOW tier: 01_locked_core/risk_manager  🔴.

WHAT THIS PACKAGE DOES
----------------------
Converts raw_size in [0,1] into broker lots against the REMAINING daily-risk buffer, slot-aware across all 5 open slots, with rounding and per-trade caps.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
It is the hard guarantee that total open-slot risk can never exceed the remaining buffer — the mechanical reason the bot cannot size its way into a breach (SOW H3, B5).

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
