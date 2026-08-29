# Qwen robustness baseline diagnostic

Source baseline: `experiments/robustness/qwen-robustness-20260828T122117Z/`.
The baseline artifacts are immutable and were not changed. Counts below are
derived from all 65 `result.json` files and representative `generated.py`
sources. This is a descriptive diagnosis, not a causal or statistical claim.

## Failure counts

| Failure category | Count |
| --- | ---: |
| `invalid_actions` | 34 |
| `invalid_transition` | 20 |
| `invalid_terminal_structure` | 10 |
| `execution_error` | 1 |

## Failure category by case

| Case | Failure counts |
| --- | --- |
| G1 | `invalid_transition`: 10; `invalid_actions`: 5 |
| G2 | `invalid_actions`: 5 |
| G3 | `invalid_transition`: 5 |
| G4 | `invalid_actions`: 5 |
| G5 | `invalid_terminal_structure`: 5 |
| G6 | `invalid_actions`: 4; `execution_error`: 1 |
| G7 | `invalid_transition`: 5 |
| G8 | `invalid_terminal_structure`: 5 |
| G9 | `invalid_actions`: 15 |

## Failure category by prompt variant

| Variant | Failure counts |
| --- | --- |
| P0 | `invalid_actions`: 19; `invalid_transition`: 15; `invalid_terminal_structure`: 10; `execution_error`: 1 |
| P1 | `invalid_actions`: 5; `invalid_transition`: 5 |
| P2 | `invalid_actions`: 10 |

## Cross-tabulation

| Category | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `invalid_actions` | 5 | 5 | 0 | 5 | 0 | 4 | 0 | 0 | 15 |
| `invalid_transition` | 10 | 0 | 5 | 0 | 0 | 0 | 5 | 0 | 0 |
| `invalid_terminal_structure` | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 5 | 0 |
| `execution_error` | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |

| Category | P0 | P1 | P2 |
| --- | ---: | ---: | ---: |
| `invalid_actions` | 19 | 5 | 10 |
| `invalid_transition` | 15 | 5 | 0 |
| `invalid_terminal_structure` | 10 | 0 | 0 |
| `execution_error` | 1 | 0 | 0 |

## Representative observed conditions

| Category | Artifact | Exact condition | Primary diagnosis |
| --- | --- | --- | --- |
| `invalid_transition` | `qwen_p0/G1/sample_001` | `transition` uses undefined `player` in `joint_action[player]`; rollout reports `NameError`. | AbstractPOSG method-scope misunderstanding; transition implementation. |
| `invalid_actions` | `qwen_p0/G2/sample_001` | `legal_actions` returns `list(range(1, 7))`, not `list[str]`. | Action representation misunderstanding. |
| `invalid_terminal_structure` | `qwen_p0/G5/sample_001` | `is_terminal` returns `True` for the initial state. | Terminal implementation misunderstanding. |
| `execution_error` | `qwen_p0/G6/sample_001` | Rollout and graph complete, but EDA reports `TypeError: Consider using a tuple, with a priority value that can be compared.` | EDA/graph processing of mixed state representations, not a repaired generation. |

## G1 P0 control

The separate unchanged control at
`experiments/debug/qwen-g1-debug-p0-20260828T132638Z/` ran five P0 G1
generations. All five were identical and failed structural validation:
`observation` and `reward` access `joint_action["other"]`, which is not a
declared player key, and `transition` raises `ValueError("Invalid joint action")`
for legal profiles. This confirms a general method-signature/key-contract
misunderstanding rather than a missing RPS rule in the prompt.

## Minimal correction

The corrected prompt must explicitly distinguish `transition(state,
joint_action)` from methods that receive `player`, require exact declared
player IDs when reading `joint_action`, and require a transition distribution
for every legal joint-action profile. It also reiterates non-empty
`list[str]` actions and a non-terminal initial state. This is a general POSG
interface clarification; it contains no G1/RPS outcome logic.

The first corrected G1 batch at
`experiments/debug/qwen-g1-debug-corrected-20260828T133005Z/` removed the
undefined `player` reference but still failed all five samples: its
`transition` compared the player-keyed `joint_action` dictionary directly to
tuples and consequently returned `None` for every legal profile. The recovery
prompt therefore adds one general rule: treat `joint_action` as a mapping,
read declared player-ID keys, never numeric-index/tuple-compare it, and return
a distribution on every control-flow path.
