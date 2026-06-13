"""quantra.learning_system.hpo  —  SOW tier: 04_learning_system/hpo.

WHAT THIS PACKAGE DOES
----------------------
Optuna hyperparameter search over the NON-SACRED dials only (entropy, clip, LR, epochs ranges, later-phase stability).

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
gamma, lambda, and the aggression-scheduler logic are hand-locked and OFF-LIMITS (SOW G6): the 'patience' math that underpins passing is never tuned away by a search chasing short-term reward.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
