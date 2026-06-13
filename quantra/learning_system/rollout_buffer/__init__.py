"""quantra.learning_system.rollout_buffer  —  SOW tier: 04_learning_system/rollout_buffer.

WHAT THIS PACKAGE DOES
----------------------
On-policy storage of (s, a_dir, a_size, a_ptr, r, s', logp_old, V_old, done, masks); no replay buffer.

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
PPO is on-policy by design (SOW §2.1); replay would contaminate the gradient. Storing the masks + summed log-prob exactly is what keeps the patient, law-bounded policy update correct.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
