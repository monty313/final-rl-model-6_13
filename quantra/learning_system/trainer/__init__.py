"""quantra.learning_system.trainer  —  SOW tier: 04_learning_system/trainer.

WHAT THIS PACKAGE DOES
----------------------
The PPO training loop: GAE with the LOCKED gamma=0.997, lambda=0.97, the missed-opportunity aggression scheduler, and checkpoint/benchmark vs the last brain.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
High gamma/lambda is the 'math of patience' that teaches delayed gratification — holding winners, not panicking — which is exactly the temperament that passes challenges consistently.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
