"""quantra.diagnostics.telemetry_logger  —  SOW tier: 05_diagnostics/telemetry_logger.

WHAT THIS PACKAGE DOES
----------------------
Records the VERSIONED per-step / per-trade / per-day data contract (observation, law state, all four head outputs, V(s), hidden summaries, full reward decomposition, risk snapshot, outcome) the diagnostics layer reasons from.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
No telemetry -> no interpretability -> no diagnosis (Term 9). Capturing the full chain is what lets the Risk Doctor prove Layer-0 dominance and reconstruct any breach or pass day.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
