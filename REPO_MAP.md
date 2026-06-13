# REPO_MAP — SOW J1 tier tree ↔ importable Python packages

The SOW Section 3 tree uses **digit-prefixed directory names** (`00_constitution/`,
`04_learning_system/`, …). Python identifiers cannot begin with a digit, and the
SOW's own Section 12 invocation (`python -m quantra.live_runner`) requires valid,
importable names. So each SOW tier is exposed under an **importable alias** while
its tier number is preserved here and as a `# SOW tier:` tag in every package's
`__init__.py`. **No architecture changed — only directory names became valid
identifiers** (approved deviation, plan sign-off 2026-06-13, per SOW R5).

| SOW tier (Section 3)        | Importable package                         | Contents |
|-----------------------------|--------------------------------------------|----------|
| `00_constitution/`          | `quantra.constitution`                     | mission, constitutional_rules, safety_boundaries |
| `01_locked_core/` 🔴        | `quantra.locked_core`                      | `laws`, `risk_manager`, `cost_layer`, `platform_adapter` |
| `02_ftmo_passing/`          | `quantra.ftmo_passing`                     | scoreboard, challenge_state, episode_rule, `validation` |
| `03_market_pipeline/`       | `quantra.market_pipeline`                  | `data_loader`, `resampler`, `feature_builder`, `law_mask_engine` |
| `04_learning_system/`       | `quantra.learning_system`                  | `ppo_agent`, `rollout_buffer`, `reward_engine`, `trainer`, `curriculum_manager`, `hpo` |
| `05_diagnostics/`           | `quantra.diagnostics`                      | `telemetry_logger`, `mlp_interpreter`, `llm_risk_doctor`, `failure_atlas` |
| `06_live_bridge/`           | `quantra.live_bridge`                      | live_runner, execution_adapter, manual_halt |
| `99_docs/`                  | `docs/`                                     | the 10 blueprint files (binding) |
| — (cross-cutting) [C]       | `quantra.runtime`                          | hardware optimizer + runtime config |
| — (the env)                 | `quantra.env`                              | the gym environment (Env module) |

## Where the binding docs live
`docs/` holds the in-tree copy of the blueprint (SOW §3 `99_docs/`):

```
docs/
├── 00_START_HERE.md
├── OPEN_QUESTIONS.md
├── THE_TRADING_CODE.md
├── STATE_VECTOR.md
├── REWARD_DESIGN.md
├── PPO_ENGINE.md
├── MLP_INTERPRETABILITY_LAYER.md   ← the LLM Risk Doctor's binding rulebook
├── SCOPE_OF_WORK.md
├── SOW_2_BUILD_SPEC.md
└── wtf_are_you_talking_about.md
```

## Build status (milestones, SOW §13–14)
- [x] **M0** — repo skeleton, docs in-tree, runtime hardware optimizer, Colab notebook
- [ ] M1 data pipeline · M2 features · M3 LawMask · M4 Env+Risk+Cost · M5 PPOAgent ·
  M6 RewardEngine · M7 curriculum+episode · M8 trainer · M9 telemetry · M10 interpreter ·
  M11 risk doctor · M12 validation · M13 HPO · M14 live bridge · M15 acceptance
