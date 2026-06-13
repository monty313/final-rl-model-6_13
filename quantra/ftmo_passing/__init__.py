"""quantra.ftmo_passing  —  SOW tier: 02_ftmo_passing.

WHAT THIS PACKAGE DOES
----------------------
Defines what "winning" means: the ``scoreboard`` (pass-rate -> breach -> target-hit
consistency -> max-DD path), the ``challenge_state`` tracker (equity, buffers,
day PnL vs target), the two-phase ``episode_rule`` (Phase A 4% trailing until
+2.5% -> auto-flat all -> Phase B 1% trailing), and ``validation`` (walk-forward +
promotion gate).

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
This tier IS the mission's measuring stick. It encodes the FTMO physics the bot
must respect and the ranking that selects brains by pass-rate rather than profit,
so training pressure always points at consistent passing.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
