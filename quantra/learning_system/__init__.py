"""quantra.learning_system  —  SOW tier: 04_learning_system.

WHAT THIS PACKAGE DOES
----------------------
The PPO learning machine: ``ppo_agent`` (four heads — direction · Beta size ·
pointer · value — on a shared 3x256 trunk), ``rollout_buffer`` (on-policy, no
replay), ``reward_engine`` (layered L0-L6 + QUAD bonus), ``trainer`` (GAE with the
locked γ=0.997 λ=0.97 + the missed-opportunity aggression scheduler),
``curriculum_manager`` (law-school stages), and ``hpo`` (Optuna on non-sacred dials
only).

HOW IT SERVES REPEATED FTMO-STYLE PASSING
-----------------------------------------
This is where the bot actually learns patience and restraint inside the legal,
risk-bounded space the locked_core defines. Layer-0 dominance and the high-γ "math
of patience" are what turn raw exploration into behaviour that hits the target
without touching the wall — repeatedly.

🔴 LOCKS: γ, λ, and the aggression-scheduler logic are hand-locked and OFF-LIMITS
to Optuna. Laws are never reward terms.

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
"""
