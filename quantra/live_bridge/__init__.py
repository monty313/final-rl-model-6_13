"""quantra.live_bridge  —  SOW tier: 06_live_bridge.

WHAT THIS PACKAGE DOES
----------------------
Isolated live deployment: ``live_runner`` (deterministic inference — argmax
direction · Beta-mean size · argmax pointer on CLOSE, clipped by RiskManager),
``execution_adapter`` (manages the 5 slots/symbol on the broker, routes CLOSE to
the pointer-selected slot), and ``manual_halt`` (always-available hard kill).

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
Live is where passes are actually banked. This tier keeps execution deterministic
and fully separated from diagnostics (SOW C7/I4), with hard kill switches (manual
halt + breach auto-flat) so a single bad session can't blow a funded account.

HARD BOUNDARY: the LLM Risk Doctor never touches this tier in real time — it reads
only checkpointed telemetry (SOW §12.3).

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
