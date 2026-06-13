"""Quantra — Deep-Reinforcement-Learning-in-Trading (PPO + MLP).

MISSION (the anchor for every line in this package)
---------------------------------------------------
Quantra is ONE universal PPO policy trained to **repeatedly pass FTMO-style
challenges over time** (default 2.5% daily target / 4% trailing wall) across
walk-forward windows and seeds — NOT to maximise PnL (SOW R1, §1). Raw PnL is a
sanity check; the scoreboard is pass-rate -> breach count -> target-hit
consistency -> max-DD path.

PACKAGE MAP (SOW J1 tier tree -> importable packages)
-----------------------------------------------------
The SOW Section 3 tree uses digit-prefixed directory names; Python identifiers
cannot start with a digit (and ``python -m quantra.live_runner`` requires valid
names), so each tier is exposed under an importable alias. Full mapping lives in
``REPO_MAP.md``. The tiers:

    constitution   -> 00_constitution   (mission, constitutional rules, safety)
    locked_core    -> 01_locked_core    🔴 laws, risk_manager, cost_layer, platform_adapter
    ftmo_passing   -> 02_ftmo_passing    scoreboard, challenge_state, episode_rule, validation
    market_pipeline-> 03_market_pipeline data_loader, resampler, feature_builder, law_mask_engine
    learning_system-> 04_learning_system ppo_agent, rollout_buffer, reward_engine, trainer, curriculum, hpo
    diagnostics    -> 05_diagnostics     telemetry_logger, mlp_interpreter, llm_risk_doctor, failure_atlas
    live_bridge    -> 06_live_bridge     live_runner, execution_adapter, manual_halt
    runtime        -> [C] hardware optimizer + runtime config (cross-cutting)
    env            -> the gym environment (4 symbols, true-sequential, 5 slots)

BINDING RULEBOOK FOR THE LLM RISK DOCTOR: ``docs/MLP_INTERPRETABILITY_LAYER.md``.
Every module points there; it defines the terms, failure taxonomy, reverse-chain
reasoning protocol, and the diagnosis output template.

HARD ARCHITECTURAL RULES (SOW R5 — never violated anywhere in this package):
  * Laws are masks, never reward terms (logit = -1e9 on forbidden actions).
  * Reward Layer 0 (net PnL) always dominates (the E8 rule).
  * The LLM Risk Doctor is read-only across the whole repo; it never writes,
    executes, or touches masks/sizing/walls.
"""

__version__ = "0.1.0"  # M0 — skeleton + runtime optimizer
