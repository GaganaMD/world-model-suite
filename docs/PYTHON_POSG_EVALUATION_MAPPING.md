# JSON Evaluation and Python POSG Mapping

The JSON and Python tracks are separate generation representations. The Python
track does not compare generated Python source to a JSON reference. It first
executes and exhaustively rolls out an `AbstractPOSG`, exports the reachable
model as canonical state/action/transition JSON, then adapts that explicit
representation to the existing Lane 2 input format.

| Analysis layer | Existing JSON framework | Python POSG track |
| --- | --- | --- |
| Mechanical validity | Lane 1 checks the v2 schema, probabilities, action profiles, reachability, and terminal paths. | `validate_posg` and exhaustive rollout check the `AbstractPOSG` interface, finite distributions, hashable states, legal joint actions, observations, rewards, reachability, and rollout bounds. |
| Structural fidelity | Lane 2 uses `game_matching` to compare a candidate and reference up to player/state/action renaming; it returns coverage, precision, and their harmonic mean. | `rollout_to_lane2_model` converts canonical Python rollouts to Lane 2 input, then calls the same scorer. |
| Semantic correctness | Neither lane establishes semantic correctness. | Case-specific mechanisms, currently the G1 semantic oracle, inspect intended rewards and observations after structural validation. |
| Exploratory graph EDA | Outside Lane 1/Lane 2. | `WorldModelEDA` measures state/action/transition structure, branching, stochasticity, entropy, depth, SCCs, terminal distance, and degree patterns. |

Lane 2 is intentionally structure-only: canonical rewards and observations are
preserved in Python rollout artifacts but are not passed to `game_matching`.
Consequently, a high structural score is not evidence of semantic correctness.
