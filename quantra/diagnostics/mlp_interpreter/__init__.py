"""quantra.diagnostics.mlp_interpreter  —  SOW tier: 05_diagnostics/mlp_interpreter.

WHAT THIS PACKAGE DOES
----------------------
Converts raw telemetry into the 7 required visuals (activation trace, hidden-state PCA projection, action/value timeline, reward-layer timeline, correlation heatmap, failure atlas, pass-day atlas).

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
Raw arrays explain nothing; these visuals make 'did the internal behaviour help the bot pass?' answerable — clustering by breach-risk, showing Layer-0 dominance, exposing shortcut learning.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
