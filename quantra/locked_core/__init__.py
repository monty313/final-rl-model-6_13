"""quantra.locked_core  —  SOW tier: 01_locked_core  🔴 PROTECTED.

WHAT THIS PACKAGE DOES
----------------------
The FTMO-critical machinery that converts the policy's intentions into legal,
sized, costed, broker-ready actions: the 9 laws + 3 gates (``laws``), the
``risk_manager`` (raw_size -> lots vs the remaining daily-risk buffer, slot-aware),
the ``cost_layer`` (real FTMO costs from day 1), and the ``platform_adapter`` (MT5
interface, live + sim).

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
This tier is what physically prevents a breach: masks forbid the wrong direction,
RiskManager guarantees open-slot risk never exceeds the buffer, costs are never
zero. It is the spine that makes "pass the challenge" mechanically enforceable.

🔴 LOCK NOTE (SOW R5): nothing here changes without Monty's explicit approval.
Propose amendments; do not apply them.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
The Risk Doctor may VIEW this tier to reason but MUST NEVER modify it, nor touch
execution, masks, sizing, or hard walls.
"""
