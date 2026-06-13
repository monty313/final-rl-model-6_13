"""quantra.learning_system.ppo_agent  —  SOW tier: 04_learning_system/ppo_agent.

WHAT THIS PACKAGE DOES
----------------------
The four-head PPO actor-critic: direction (categorical), size (Beta), pointer (categorical over 5 slots), value — on a shared 3x256 MLP trunk. Emits the summed log-prob of the three action heads.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
The heads encode WHAT/HOW-MUCH/WHICH-to-close and the critic encodes patience; together, inside the masks, they are how the bot learns to hit target without breaching (PPO_ENGINE.md).

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
