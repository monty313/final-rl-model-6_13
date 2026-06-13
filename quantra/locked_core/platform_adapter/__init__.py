"""quantra.locked_core.platform_adapter  —  SOW tier: 01_locked_core/platform_adapter  🔴.

WHAT THIS PACKAGE DOES
----------------------
The MT5 broker interface (live + simulation) — the platform-blind boundary between the policy's normalized intentions and concrete broker orders.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
Keeping the policy platform-blind (it never sees lots/account size) is what lets ONE brain pass challenges on any account size or supported asset (SOW A2).

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
