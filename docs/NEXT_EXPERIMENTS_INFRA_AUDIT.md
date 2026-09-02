# Next-experiments infrastructure audit

## Existing components

- POSG loading and schema validation: `world_model_eda/reference_games.py`, `src/evaluation/`.
- Exhaustive state/transition graph enumeration and graph statistics: `world_model_eda/`.
- Permutation-invariant structural matching: `json_generation/lane2.py` and the pinned `third_party/game_matching` submodule.
- Preserved 135 game candidates and reference schemas: `experiments/openrouter_game_study/`.
- Reward-aware reference fixtures exist, but generated artifacts are not guaranteed to use the same reward semantics.

## Missing before this extension

There was no reusable finite-horizon planner, policy evaluation/regret module, reversibility metric, intervention-invariant checker, or embodied/horizon benchmark. These are being added as no-call, exact-reference infrastructure. Existing graph statistics remain the source of structural complexity features.

## Evidence boundary

The G1--G9 reference schemas contain explicit reward fields, but matching generated reward semantics across arbitrary state/action renamings is not yet validated. Therefore the new planner is used first for controlled reference perturbations; natural generated-model planning is reported as pending until objective/state/action alignment is audited.
