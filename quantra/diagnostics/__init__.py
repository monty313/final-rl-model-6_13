"""quantra.diagnostics  —  SOW tier: 05_diagnostics.

WHAT THIS PACKAGE DOES
----------------------
The interpretability layer: ``telemetry_logger`` (versioned per-step/-trade/-day
packets per the data contract), ``mlp_interpreter`` (the 7 required visuals),
``llm_risk_doctor`` (read-only, evidence-only diagnosis following the output
template + 8-failure taxonomy), and ``failure_atlas`` builders.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
A model can look good on PnL while quietly damaging its ability to pass (drifting
near the wall, winning on one seed, learning shortcuts). This tier turns the black
box into an inspectable machine so failures are classified and fixed before they
cost a challenge.

HARD BOUNDARY (SOW C7/R5): everything here is offline/supervisory. The LLM Risk
Doctor MAY read any file in the repo to reason; it MAY NEVER write, execute, or
touch masks/sizing/walls.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``
(it must be read at the start of EVERY diagnosis session, or the code fails loud).
"""
