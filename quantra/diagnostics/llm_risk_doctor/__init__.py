"""quantra.diagnostics.llm_risk_doctor  —  SOW tier: 05_diagnostics/llm_risk_doctor.

WHAT THIS PACKAGE DOES
----------------------
The offline, READ-ONLY supervisory diagnosis module: reads telemetry + interpreter artifacts + (read-only) any repo file, and emits a structured diagnosis using the output template and the 8-failure taxonomy.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
It catches models that pass by luck or drift toward the wall BEFORE they cost a real challenge. It MUST read the rulebook first and MAY NEVER write, execute, or touch masks/sizing/walls (hard boundary).

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
