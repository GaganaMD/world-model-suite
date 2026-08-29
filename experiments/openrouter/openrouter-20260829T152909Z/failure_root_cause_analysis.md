# Benchmark Failure Root-Cause Analysis

Run analyzed: `openrouter-20260829T152909Z` (45 total runs; 23 passed, 22 failed).

> Artifact note: this run contains no files named `validation_details.json`. The runner stored the validator diagnostics, stage statuses, and error/trace text in each `sample_001/result.json`; this report uses those records together with `summary.json`, `generated.py`, the prompt, and the evaluator source.

## Summary Table

| Model | Game | Failure Category | Triggering Error / Mismatch |
| :--- | :--- | :--- | :--- |
| Claude Opus 5 | G1 | Observation-Contract Failure | `observation()` returned non-string `('waiting',)` at generated.py:44 |
| Claude Opus 5 | G2 | Observation-Contract Failure | `observation()` returned non-string `('own_die', own, outcome)` at generated.py:71 |
| Claude Opus 5 | G3 | Observation-Contract Failure | `observation()` returned non-string `('flip_result', coin, 'my_call', own_call, 'opponent_call', opp_call, result)` at generated.py:47 |
| Claude Opus 5 | G4 | Observation-Contract Failure | `observation()` returned non-string `('kicker_view', kick, keep, outcome)` at generated.py:80 |
| Claude Opus 5 | G5 | Observation-Contract Failure | `observation()` returned non-string `('reveal', 'my_face:' + f1, 'their_face:' + f2, outcome)` at generated.py:45 |
| Claude Opus 5 | G6 | Observation-Contract Failure | `observation()` returned non-string `('private_value', own)` at generated.py:75 |
| Claude Opus 5 | G7 | Observation-Contract Failure | `observation()` returned non-string `('verdict', own, other)` at generated.py:57 |
| Claude Opus 5 | G9 | Execution Error (EDA node-type incompatibility) | NetworkX compared mixed string/tuple state IDs during modularity analysis |
| DeepSeek V4 Flash | G2 | Invalid-Python Failure | Markdown fence at generated.py:1 caused `SyntaxError` |
| DeepSeek V4 Flash | G6 | Invalid-Actions Failure | `legal_actions()` returned `list[int]` `[0, 1, 2]` at generated.py:17 |
| GPT-5.6 Sol | G1 | Observation-Contract Failure | `observation()` returned non-string `(outcome, own_action, opponent_action)` at generated.py:49 |
| GPT-5.6 Sol | G2 | Observation-Contract Failure | `observation()` returned non-string `('roll_result', player_1_roll, player_2_roll)` at generated.py:43 |
| GPT-5.6 Sol | G3 | Observation-Contract Failure | `observation()` returned non-string `(result, player_call, outcome)` at generated.py:50 |
| GPT-5.6 Sol | G4 | Observation-Contract Failure | `observation()` returned non-string `(next_state[1], next_state[2], next_state[3])` at generated.py:41 |
| GPT-5.6 Sol | G5 | Observation-Contract Failure | `observation()` returned non-string `('revealed', 'heads', 'heads')` at generated.py:41 |
| GPT-5.6 Sol | G6 | Observation-Contract Failure | `observation()` returned non-string `('private_value', own_value)` at generated.py:60 |
| GPT-5.6 Sol | G9 | Execution Error (EDA node-type incompatibility) | NetworkX compared mixed string/tuple state IDs during modularity analysis |
| Qwen 3.8 27B | G2 | Interface Failure (empty/truncated generation) | OpenRouter exhausted 8,192 reasoning tokens and returned `content=null` |
| Qwen 3.8 27B | G4 | Observation-Contract Failure | `observation()` returned non-string `('player_1', joint_action['player_1'], next_state)` at generated.py:26 |
| Qwen 3.8 27B | G5 | Observation-Contract Failure | `observation()` returned non-string `(p1, p2)` at generated.py:38 |
| Qwen 3.8 27B | G6 | Execution Error (EDA node-type incompatibility) | NetworkX compared mixed string/tuple state IDs during modularity analysis |
| Qwen 3.8 27B | G9 | Interface Failure (empty/truncated generation) | OpenRouter exhausted 8,192 reasoning tokens and returned `content=null` |

## Detailed Case-by-Case Breakdown

### Claude Opus 5 — Game G1

- **Failure Category:** Observation-Contract Failure
- **File & Function:** `generated.py:42`, `GeneratedPOSG.observation()`; offending returns: line 44 (`('waiting',)`), line 59 (`('reveal', own, other, result)`).
- **Error Message / Trace:** `Outcome ('end', 'rock', 'rock'), player 'player_1': TypeError: observation() must return str.`
- **Root Cause Analysis:** The rollout validator exhaustively called `observation(state, joint_action, next_state, player)` for reachable outcomes. At least one reachable branch returned a structured tuple instead of a string. The first violating return is at generated.py:44; `rollout_world_model()` rejects it in `world_model_eda/python_posg.py:393`. This is a return-type violation, not a missing-key or player-ID error.
- **Contract/Schema Difference:**
  - Expected: every reachable `observation()` branch returns `str`, such as `"outcome=win;own=rock;other=scissors"`.
  - Actual: reachable branches return structured values; observed static return sites are line 44 (`('waiting',)`), line 59 (`('reveal', own, other, result)`).
- **Recommended Fix:** Add an explicit generation rule: “`observation()` MUST return `str` on every control-flow path; tuple/list/dict/set observations are forbidden. Encode multiple fields with an f-string.” Add an AST preflight that rejects non-string literal containers returned from `observation` before rollout.

---

### Claude Opus 5 — Game G2

- **Failure Category:** Observation-Contract Failure
- **File & Function:** `generated.py:50`, `GeneratedPOSG.observation()`; offending returns: line 71 (`('own_die', own, outcome)`).
- **Error Message / Trace:** `Outcome ('done', 1, 1), player 'player_1': TypeError: observation() must return str.`
- **Root Cause Analysis:** The rollout validator exhaustively called `observation(state, joint_action, next_state, player)` for reachable outcomes. At least one reachable branch returned a structured tuple instead of a string. The first violating return is at generated.py:71; `rollout_world_model()` rejects it in `world_model_eda/python_posg.py:393`. This is a return-type violation, not a missing-key or player-ID error.
- **Contract/Schema Difference:**
  - Expected: every reachable `observation()` branch returns `str`, such as `"outcome=win;own=rock;other=scissors"`.
  - Actual: reachable branches return structured values; observed static return sites are line 71 (`('own_die', own, outcome)`).
- **Recommended Fix:** Add an explicit generation rule: “`observation()` MUST return `str` on every control-flow path; tuple/list/dict/set observations are forbidden. Encode multiple fields with an f-string.” Add an AST preflight that rejects non-string literal containers returned from `observation` before rollout.

---

### Claude Opus 5 — Game G3

- **Failure Category:** Observation-Contract Failure
- **File & Function:** `generated.py:39`, `GeneratedPOSG.observation()`; offending returns: line 47 (`('flip_result', coin, 'my_call', own_call, 'opponent_call', opp_call, result)`).
- **Error Message / Trace:** `Outcome ('done', 'heads', 'heads', 'heads'), player 'player_1': TypeError: observation() must return str.`
- **Root Cause Analysis:** The rollout validator exhaustively called `observation(state, joint_action, next_state, player)` for reachable outcomes. At least one reachable branch returned a structured tuple instead of a string. The first violating return is at generated.py:47; `rollout_world_model()` rejects it in `world_model_eda/python_posg.py:393`. This is a return-type violation, not a missing-key or player-ID error.
- **Contract/Schema Difference:**
  - Expected: every reachable `observation()` branch returns `str`, such as `"outcome=win;own=rock;other=scissors"`.
  - Actual: reachable branches return structured values; observed static return sites are line 47 (`('flip_result', coin, 'my_call', own_call, 'opponent_call', opp_call, result)`).
- **Recommended Fix:** Add an explicit generation rule: “`observation()` MUST return `str` on every control-flow path; tuple/list/dict/set observations are forbidden. Encode multiple fields with an f-string.” Add an AST preflight that rejects non-string literal containers returned from `observation` before rollout.

---

### Claude Opus 5 — Game G4

- **Failure Category:** Observation-Contract Failure
- **File & Function:** `generated.py:69`, `GeneratedPOSG.observation()`; offending returns: line 80 (`('kicker_view', kick, keep, outcome)`), line 82 (`('keeper_view', kick, keep, outcome)`), line 83 (`('spectator_view', outcome)`).
- **Error Message / Trace:** `Outcome 'save', player 'player_1': TypeError: observation() must return str.`
- **Root Cause Analysis:** The rollout validator exhaustively called `observation(state, joint_action, next_state, player)` for reachable outcomes. At least one reachable branch returned a structured tuple instead of a string. The first violating return is at generated.py:80; `rollout_world_model()` rejects it in `world_model_eda/python_posg.py:393`. This is a return-type violation, not a missing-key or player-ID error.
- **Contract/Schema Difference:**
  - Expected: every reachable `observation()` branch returns `str`, such as `"outcome=win;own=rock;other=scissors"`.
  - Actual: reachable branches return structured values; observed static return sites are line 80 (`('kicker_view', kick, keep, outcome)`), line 82 (`('keeper_view', kick, keep, outcome)`), line 83 (`('spectator_view', outcome)`).
- **Recommended Fix:** Add an explicit generation rule: “`observation()` MUST return `str` on every control-flow path; tuple/list/dict/set observations are forbidden. Encode multiple fields with an f-string.” Add an AST preflight that rejects non-string literal containers returned from `observation` before rollout.

---

### Claude Opus 5 — Game G5

- **Failure Category:** Observation-Contract Failure
- **File & Function:** `generated.py:38`, `GeneratedPOSG.observation()`; offending returns: line 45 (`('reveal', 'my_face:' + f1, 'their_face:' + f2, outcome)`), line 46 (`('reveal', 'my_face:' + f2, 'their_face:' + f1, outcome)`), line 47 (`('hidden', 'pennies_not_yet_revealed')`).
- **Error Message / Trace:** `Outcome ('end', 'heads', 'heads'), player 'player_1': TypeError: observation() must return str.`
- **Root Cause Analysis:** The rollout validator exhaustively called `observation(state, joint_action, next_state, player)` for reachable outcomes. At least one reachable branch returned a structured tuple instead of a string. The first violating return is at generated.py:45; `rollout_world_model()` rejects it in `world_model_eda/python_posg.py:393`. This is a return-type violation, not a missing-key or player-ID error.
- **Contract/Schema Difference:**
  - Expected: every reachable `observation()` branch returns `str`, such as `"outcome=win;own=rock;other=scissors"`.
  - Actual: reachable branches return structured values; observed static return sites are line 45 (`('reveal', 'my_face:' + f1, 'their_face:' + f2, outcome)`), line 46 (`('reveal', 'my_face:' + f2, 'their_face:' + f1, outcome)`), line 47 (`('hidden', 'pennies_not_yet_revealed')`).
- **Recommended Fix:** Add an explicit generation rule: “`observation()` MUST return `str` on every control-flow path; tuple/list/dict/set observations are forbidden. Encode multiple fields with an f-string.” Add an AST preflight that rejects non-string literal containers returned from `observation` before rollout.

---

### Claude Opus 5 — Game G6

- **Failure Category:** Observation-Contract Failure
- **File & Function:** `generated.py:71`, `GeneratedPOSG.observation()`; offending returns: line 75 (`('private_value', own)`), line 84 (`('auction_result', own, own_bid, rival_bid, 'won' if winner == player else 'lost')`), line 92 (`('nothing',)`).
- **Error Message / Trace:** `Outcome ('values', 'low', 'low'), player 'player_1': TypeError: observation() must return str.`
- **Root Cause Analysis:** The rollout validator exhaustively called `observation(state, joint_action, next_state, player)` for reachable outcomes. At least one reachable branch returned a structured tuple instead of a string. The first violating return is at generated.py:75; `rollout_world_model()` rejects it in `world_model_eda/python_posg.py:393`. This is a return-type violation, not a missing-key or player-ID error.
- **Contract/Schema Difference:**
  - Expected: every reachable `observation()` branch returns `str`, such as `"outcome=win;own=rock;other=scissors"`.
  - Actual: reachable branches return structured values; observed static return sites are line 75 (`('private_value', own)`), line 84 (`('auction_result', own, own_bid, rival_bid, 'won' if winner == player else 'lost')`), line 92 (`('nothing',)`).
- **Recommended Fix:** Add an explicit generation rule: “`observation()` MUST return `str` on every control-flow path; tuple/list/dict/set observations are forbidden. Encode multiple fields with an f-string.” Add an AST preflight that rejects non-string literal containers returned from `observation` before rollout.

---

### Claude Opus 5 — Game G7

- **Failure Category:** Observation-Contract Failure
- **File & Function:** `generated.py:48`, `GeneratedPOSG.observation()`; offending returns: line 57 (`('verdict', own, other)`), line 58 (`('waiting', joint_action.get(player, self.SILENT))`).
- **Error Message / Trace:** `Outcome ('outcome', 'silent', 'silent'), player 'player_1': TypeError: observation() must return str.`
- **Root Cause Analysis:** The rollout validator exhaustively called `observation(state, joint_action, next_state, player)` for reachable outcomes. At least one reachable branch returned a structured tuple instead of a string. The first violating return is at generated.py:57; `rollout_world_model()` rejects it in `world_model_eda/python_posg.py:393`. This is a return-type violation, not a missing-key or player-ID error.
- **Contract/Schema Difference:**
  - Expected: every reachable `observation()` branch returns `str`, such as `"outcome=win;own=rock;other=scissors"`.
  - Actual: reachable branches return structured values; observed static return sites are line 57 (`('verdict', own, other)`), line 58 (`('waiting', joint_action.get(player, self.SILENT))`).
- **Recommended Fix:** Add an explicit generation rule: “`observation()` MUST return `str` on every control-flow path; tuple/list/dict/set observations are forbidden. Encode multiple fields with an f-string.” Add an AST preflight that rejects non-string literal containers returned from `observation` before rollout.

---

### Claude Opus 5 — Game G9

- **Failure Category:** Execution Error (EDA node-type incompatibility)
- **File & Function:** generated.py state constructors described below; evaluator failure at `world_model_eda/eda.py:348`, `WorldModelEDA.graph_statistics()`.
- **Error Message / Trace:** `TypeError: Consider using a tuple, with a priority value that can be compared.`
- **Root Cause Analysis:** The generated class executed successfully, passed interface validation, completed exhaustive rollout, and built both graphs. Failure occurred afterward in `WorldModelEDA.summary()` → `graph_statistics()` → `networkx.community.greedy_modularity_communities()` → `MappedQueue._heapify()`. The graph contains both string and tuple node IDs. NetworkX used node IDs to break equal-priority heap ties, reached `str < tuple`, and raised `TypeError`. Therefore this is an evaluator compatibility defect exposed by a contract-permitted mixed hashable state representation, not a generated-POSG execution defect.
- **Contract/Schema Difference:**
  - Expected by POSG contract: any hashable state identifier; strings and tuples are both explicitly permitted.
  - Actual graph: `initial_state()` returns the string `"deploy"` at generated.py:41; `transition()` returns tuple states at generated.py:57 and 60. NetworkX's modularity routine implicitly requires mutually orderable node labels when priorities tie.
- **Stack Trace Summary:** `ExperimentRunner.run_case()` → `WorldModelEDA.summary()` (`eda.py:461`) → `graph_statistics()` (`eda.py:348`) → NetworkX `greedy_modularity_communities()` → `MappedQueue`/`heapq.heapify()` → failed comparison between `str` and `tuple`.
- **Recommended Fix:** Fix the evaluator by relabeling graph nodes to stable integer IDs before community detection (or pass a deterministic comparable tie-break key), while retaining original labels as attributes. As a secondary prompt guardrail, require one uniform state-ID type per generated model, but do not treat mixed hashable types as a POSG contract violation.

---

### DeepSeek V4 Flash — Game G2

- **Failure Category:** Invalid-Python Failure
- **File & Function:** `generated.py:1`; parsing occurs in `execute_generated_posg()` at `world_model_eda/python_posg.py:438`.
- **Error Message / Trace:** `SyntaxError: invalid syntax (<unknown>, line 1)`
- **Root Cause Analysis:** The saved response begins with three backticks followed by `python` at line 1 and has no closing fence. The backend's fence stripper only removes a complete opening/closing pair, so the raw incomplete response was saved. `ast.parse()` encountered backticks at column 1 and raised `SyntaxError` before class execution. The Python class body itself is syntactically plausible, but it was never reached. A latent semantic issue is that its stochastic transition aggregates dice outcomes into win/draw states rather than retaining individual rolls; that is not the recorded failure.
- **Contract/Schema Difference:**
  - Expected: raw Python beginning with `class GeneratedPOSG(AbstractPOSG):`, without Markdown fences.
  - Actual: line 1 is a `python` Markdown opening fence; the response was truncated before a closing fence.
- **Recommended Fix:** Reject or strip a leading fence independently of whether a closing fence exists, check `finish_reason`, and run `ast.parse()` before artifact acceptance. Retry truncated/fenced responses with “begin immediately with `class GeneratedPOSG` and never emit backticks.”

---

### DeepSeek V4 Flash — Game G6

- **Failure Category:** Invalid-Actions Failure
- **File & Function:** `generated.py:14–17`, `GeneratedPOSG.legal_actions()`.
- **Error Message / Trace:** `State 's0_1_2', player 'player_1': legal_actions must return a non-empty list of string actions.`
- **Root Cause Analysis:** For reachable non-terminal state `s0_1_2`, line 17 returns `[0, 1, 2]`. The list is non-empty but its elements are integers. `rollout_world_model()` requires action identifiers to be strings and rejected both players before invoking `transition()`. No action was out of bounds; the failure is element type. There is a separate latent contract issue at generated.py:20–21: a terminal transition returns `{}`, but terminal states are not expanded by this rollout, so it did not trigger this run.
- **Contract/Schema Difference:**
  - Expected: non-terminal `legal_actions()` returns a non-empty `list[str]`, e.g. `["bid_0", "bid_1", "bid_2"]`.
  - Actual: `[0, 1, 2]` (`list[int]`) at line 17.
- **Recommended Fix:** State explicitly that action IDs must be strings even when semantically numeric, and add an AST/runtime preflight asserting `all(isinstance(a, str) for a in actions)`. Also require every `transition()` branch, including terminal self-loops, to return a non-empty distribution.

---

### GPT-5.6 Sol — Game G1

- **Failure Category:** Observation-Contract Failure
- **File & Function:** `generated.py:24`, `GeneratedPOSG.observation()`; offending returns: line 49 (`(outcome, own_action, opponent_action)`).
- **Error Message / Trace:** `Outcome ('terminal', 'rock', 'rock'), player 'player_1': TypeError: observation() must return str.`
- **Root Cause Analysis:** The rollout validator exhaustively called `observation(state, joint_action, next_state, player)` for reachable outcomes. At least one reachable branch returned a structured tuple instead of a string. The first violating return is at generated.py:49; `rollout_world_model()` rejects it in `world_model_eda/python_posg.py:393`. This is a return-type violation, not a missing-key or player-ID error.
- **Contract/Schema Difference:**
  - Expected: every reachable `observation()` branch returns `str`, such as `"outcome=win;own=rock;other=scissors"`.
  - Actual: reachable branches return structured values; observed static return sites are line 49 (`(outcome, own_action, opponent_action)`).
- **Recommended Fix:** Add an explicit generation rule: “`observation()` MUST return `str` on every control-flow path; tuple/list/dict/set observations are forbidden. Encode multiple fields with an f-string.” Add an AST preflight that rejects non-string literal containers returned from `observation` before rollout.

---

### GPT-5.6 Sol — Game G2

- **Failure Category:** Observation-Contract Failure
- **File & Function:** `generated.py:38`, `GeneratedPOSG.observation()`; offending returns: line 43 (`('roll_result', player_1_roll, player_2_roll)`), line 45 (`('roll_result', player_2_roll, player_1_roll)`).
- **Error Message / Trace:** `Outcome ('terminal', 1, 1), player 'player_1': TypeError: observation() must return str.`
- **Root Cause Analysis:** The rollout validator exhaustively called `observation(state, joint_action, next_state, player)` for reachable outcomes. At least one reachable branch returned a structured tuple instead of a string. The first violating return is at generated.py:43; `rollout_world_model()` rejects it in `world_model_eda/python_posg.py:393`. This is a return-type violation, not a missing-key or player-ID error.
- **Contract/Schema Difference:**
  - Expected: every reachable `observation()` branch returns `str`, such as `"outcome=win;own=rock;other=scissors"`.
  - Actual: reachable branches return structured values; observed static return sites are line 43 (`('roll_result', player_1_roll, player_2_roll)`), line 45 (`('roll_result', player_2_roll, player_1_roll)`).
- **Recommended Fix:** Add an explicit generation rule: “`observation()` MUST return `str` on every control-flow path; tuple/list/dict/set observations are forbidden. Encode multiple fields with an f-string.” Add an AST preflight that rejects non-string literal containers returned from `observation` before rollout.

---

### GPT-5.6 Sol — Game G3

- **Failure Category:** Observation-Contract Failure
- **File & Function:** `generated.py:35`, `GeneratedPOSG.observation()`; offending returns: line 50 (`(result, player_call, outcome)`).
- **Error Message / Trace:** `Outcome ('terminal', 'heads', 'heads', 'heads'), player 'player_1': TypeError: observation() must return str.`
- **Root Cause Analysis:** The rollout validator exhaustively called `observation(state, joint_action, next_state, player)` for reachable outcomes. At least one reachable branch returned a structured tuple instead of a string. The first violating return is at generated.py:50; `rollout_world_model()` rejects it in `world_model_eda/python_posg.py:393`. This is a return-type violation, not a missing-key or player-ID error.
- **Contract/Schema Difference:**
  - Expected: every reachable `observation()` branch returns `str`, such as `"outcome=win;own=rock;other=scissors"`.
  - Actual: reachable branches return structured values; observed static return sites are line 50 (`(result, player_call, outcome)`).
- **Recommended Fix:** Add an explicit generation rule: “`observation()` MUST return `str` on every control-flow path; tuple/list/dict/set observations are forbidden. Encode multiple fields with an f-string.” Add an AST preflight that rejects non-string literal containers returned from `observation` before rollout.

---

### GPT-5.6 Sol — Game G4

- **Failure Category:** Observation-Contract Failure
- **File & Function:** `generated.py:37`, `GeneratedPOSG.observation()`; offending returns: line 41 (`(next_state[1], next_state[2], next_state[3])`).
- **Error Message / Trace:** `Outcome ('terminal', 'saved', 'left', 'left'), player 'player_1': TypeError: observation() must return str.`
- **Root Cause Analysis:** The rollout validator exhaustively called `observation(state, joint_action, next_state, player)` for reachable outcomes. At least one reachable branch returned a structured tuple instead of a string. The first violating return is at generated.py:41; `rollout_world_model()` rejects it in `world_model_eda/python_posg.py:393`. This is a return-type violation, not a missing-key or player-ID error.
- **Contract/Schema Difference:**
  - Expected: every reachable `observation()` branch returns `str`, such as `"outcome=win;own=rock;other=scissors"`.
  - Actual: reachable branches return structured values; observed static return sites are line 41 (`(next_state[1], next_state[2], next_state[3])`).
- **Recommended Fix:** Add an explicit generation rule: “`observation()` MUST return `str` on every control-flow path; tuple/list/dict/set observations are forbidden. Encode multiple fields with an f-string.” Add an AST preflight that rejects non-string literal containers returned from `observation` before rollout.

---

### GPT-5.6 Sol — Game G5

- **Failure Category:** Observation-Contract Failure
- **File & Function:** `generated.py:37`, `GeneratedPOSG.observation()`; offending returns: line 41 (`('revealed', 'heads', 'heads')`), line 43 (`('revealed', 'heads', 'tails')`), line 45 (`('revealed', 'tails', 'heads')`), line 47 (`('revealed', 'tails', 'tails')`).
- **Error Message / Trace:** `Outcome 'terminal_heads_heads', player 'player_1': TypeError: observation() must return str.`
- **Root Cause Analysis:** The rollout validator exhaustively called `observation(state, joint_action, next_state, player)` for reachable outcomes. At least one reachable branch returned a structured tuple instead of a string. The first violating return is at generated.py:41; `rollout_world_model()` rejects it in `world_model_eda/python_posg.py:393`. This is a return-type violation, not a missing-key or player-ID error.
- **Contract/Schema Difference:**
  - Expected: every reachable `observation()` branch returns `str`, such as `"outcome=win;own=rock;other=scissors"`.
  - Actual: reachable branches return structured values; observed static return sites are line 41 (`('revealed', 'heads', 'heads')`), line 43 (`('revealed', 'heads', 'tails')`), line 45 (`('revealed', 'tails', 'heads')`), line 47 (`('revealed', 'tails', 'tails')`).
- **Recommended Fix:** Add an explicit generation rule: “`observation()` MUST return `str` on every control-flow path; tuple/list/dict/set observations are forbidden. Encode multiple fields with an f-string.” Add an AST preflight that rejects non-string literal containers returned from `observation` before rollout.

---

### GPT-5.6 Sol — Game G6

- **Failure Category:** Observation-Contract Failure
- **File & Function:** `generated.py:54`, `GeneratedPOSG.observation()`; offending returns: line 60 (`('private_value', own_value)`), line 67 (`('auction_result', own_value, own_bid, winning_bid, outcome)`).
- **Error Message / Trace:** `Outcome ('bidding', 'low', 'low'), player 'player_1': TypeError: observation() must return str.`
- **Root Cause Analysis:** The rollout validator exhaustively called `observation(state, joint_action, next_state, player)` for reachable outcomes. At least one reachable branch returned a structured tuple instead of a string. The first violating return is at generated.py:60; `rollout_world_model()` rejects it in `world_model_eda/python_posg.py:393`. This is a return-type violation, not a missing-key or player-ID error.
- **Contract/Schema Difference:**
  - Expected: every reachable `observation()` branch returns `str`, such as `"outcome=win;own=rock;other=scissors"`.
  - Actual: reachable branches return structured values; observed static return sites are line 60 (`('private_value', own_value)`), line 67 (`('auction_result', own_value, own_bid, winning_bid, outcome)`).
- **Recommended Fix:** Add an explicit generation rule: “`observation()` MUST return `str` on every control-flow path; tuple/list/dict/set observations are forbidden. Encode multiple fields with an f-string.” Add an AST preflight that rejects non-string literal containers returned from `observation` before rollout.

---

### GPT-5.6 Sol — Game G9

- **Failure Category:** Execution Error (EDA node-type incompatibility)
- **File & Function:** generated.py state constructors described below; evaluator failure at `world_model_eda/eda.py:348`, `WorldModelEDA.graph_statistics()`.
- **Error Message / Trace:** `TypeError: Consider using a tuple, with a priority value that can be compared.`
- **Root Cause Analysis:** The generated class executed successfully, passed interface validation, completed exhaustive rollout, and built both graphs. Failure occurred afterward in `WorldModelEDA.summary()` → `graph_statistics()` → `networkx.community.greedy_modularity_communities()` → `MappedQueue._heapify()`. The graph contains both string and tuple node IDs. NetworkX used node IDs to break equal-priority heap ties, reached `str < tuple`, and raised `TypeError`. Therefore this is an evaluator compatibility defect exposed by a contract-permitted mixed hashable state representation, not a generated-POSG execution defect.
- **Contract/Schema Difference:**
  - Expected by POSG contract: any hashable state identifier; strings and tuples are both explicitly permitted.
  - Actual graph: `initial_state()` returns the string `"s0"` at generated.py:7; `transition()` constructs a six-element tuple at generated.py:66–73 and returns it at line 74. NetworkX's modularity routine implicitly requires mutually orderable node labels when priorities tie.
- **Stack Trace Summary:** `ExperimentRunner.run_case()` → `WorldModelEDA.summary()` (`eda.py:461`) → `graph_statistics()` (`eda.py:348`) → NetworkX `greedy_modularity_communities()` → `MappedQueue`/`heapq.heapify()` → failed comparison between `str` and `tuple`.
- **Recommended Fix:** Fix the evaluator by relabeling graph nodes to stable integer IDs before community detection (or pass a deterministic comparable tie-break key), while retaining original labels as attributes. As a secondary prompt guardrail, require one uniform state-ID type per generated model, but do not treat mixed hashable types as a POSG contract violation.

---

### Qwen 3.8 27B — Game G2

- **Failure Category:** Interface Failure (empty/truncated generation)
- **File & Function:** no `generated.py` exists; backend check at `experiments/run_openrouter_game_experiments.py:124–126`.
- **Error Message / Trace:** `RuntimeError: OpenRouter returned no message content: {'id': 'gen-1788018386-bxRQaRRBNvq3vVcIQoMX', 'object': 'chat.completion', 'created': 1788018386, 'model': 'qwen/qwen3.8-27b', 'provider': 'CoreWeave', 'system_fingerprint': None, 'service_tier': None, 'ch…`
- **Root Cause Analysis:** During the dice-game generation, OpenRouter returned `finish_reason="length"`, `content=null`, and 8,192 completion tokens entirely in the reasoning channel. The backend read `message.content` at line 124, found it empty, and raised `RuntimeError` at line 126. Generation therefore failed before Python parsing or `GeneratedPOSG` interface inspection; there are no missing methods or altered signatures to list.
- **Contract/Schema Difference:**
  - Expected: a non-empty assistant `content` string containing `class GeneratedPOSG(AbstractPOSG)` with `players`, `initial_state`, `legal_actions`, `transition`, `observation`, `reward`, and `is_terminal`.
  - Actual: no code content and consequently no class or callable interface; only truncated reasoning was returned.
- **Taxonomy Note:** `classify_failure()` labeled this `interface_failure` because the serialized provider payload echoed the prompt terms `GeneratedPOSG`/`AbstractPOSG`. The primary cause is output-budget exhaustion, not an interface mismatch.
- **Recommended Fix:** For reasoning models, reserve a separate/larger output budget or disable reasoning for code-only generations. Treat `finish_reason=length` or `content is None` as a dedicated `generation_truncated` category and retry once with constrained reasoning and a higher content budget.

---

### Qwen 3.8 27B — Game G4

- **Failure Category:** Observation-Contract Failure
- **File & Function:** `generated.py:24`, `GeneratedPOSG.observation()`; offending returns: line 26 (`('player_1', joint_action['player_1'], next_state)`), line 28 (`('player_2', joint_action['player_2'], next_state)`).
- **Error Message / Trace:** `Outcome 'save', player 'player_1': TypeError: observation() must return str.`
- **Root Cause Analysis:** The rollout validator exhaustively called `observation(state, joint_action, next_state, player)` for reachable outcomes. At least one reachable branch returned a structured tuple instead of a string. The first violating return is at generated.py:26; `rollout_world_model()` rejects it in `world_model_eda/python_posg.py:393`. This is a return-type violation, not a missing-key or player-ID error.
- **Contract/Schema Difference:**
  - Expected: every reachable `observation()` branch returns `str`, such as `"outcome=win;own=rock;other=scissors"`.
  - Actual: reachable branches return structured values; observed static return sites are line 26 (`('player_1', joint_action['player_1'], next_state)`), line 28 (`('player_2', joint_action['player_2'], next_state)`).
- **Recommended Fix:** Add an explicit generation rule: “`observation()` MUST return `str` on every control-flow path; tuple/list/dict/set observations are forbidden. Encode multiple fields with an f-string.” Add an AST preflight that rejects non-string literal containers returned from `observation` before rollout.

---

### Qwen 3.8 27B — Game G5

- **Failure Category:** Observation-Contract Failure
- **File & Function:** `generated.py:27`, `GeneratedPOSG.observation()`; offending returns: line 38 (`(p1, p2)`), line 40 (`(p2, p1)`), line 41 (`(p1, p2)`).
- **Error Message / Trace:** `Outcome 'terminal_same', player 'player_1': TypeError: observation() must return str.`
- **Root Cause Analysis:** The rollout validator exhaustively called `observation(state, joint_action, next_state, player)` for reachable outcomes. At least one reachable branch returned a structured tuple instead of a string. The first violating return is at generated.py:38; `rollout_world_model()` rejects it in `world_model_eda/python_posg.py:393`. This is a return-type violation, not a missing-key or player-ID error.
- **Contract/Schema Difference:**
  - Expected: every reachable `observation()` branch returns `str`, such as `"outcome=win;own=rock;other=scissors"`.
  - Actual: reachable branches return structured values; observed static return sites are line 38 (`(p1, p2)`), line 40 (`(p2, p1)`), line 41 (`(p1, p2)`).
- **Recommended Fix:** Add an explicit generation rule: “`observation()` MUST return `str` on every control-flow path; tuple/list/dict/set observations are forbidden. Encode multiple fields with an f-string.” Add an AST preflight that rejects non-string literal containers returned from `observation` before rollout.

---

### Qwen 3.8 27B — Game G6

- **Failure Category:** Execution Error (EDA node-type incompatibility)
- **File & Function:** generated.py state constructors described below; evaluator failure at `world_model_eda/eda.py:348`, `WorldModelEDA.graph_statistics()`.
- **Error Message / Trace:** `TypeError: Consider using a tuple, with a priority value that can be compared.`
- **Root Cause Analysis:** The generated class executed successfully, passed interface validation, completed exhaustive rollout, and built both graphs. Failure occurred afterward in `WorldModelEDA.summary()` → `graph_statistics()` → `networkx.community.greedy_modularity_communities()` → `MappedQueue._heapify()`. The graph contains both string and tuple node IDs. NetworkX used node IDs to break equal-priority heap ties, reached `str < tuple`, and raised `TypeError`. Therefore this is an evaluator compatibility defect exposed by a contract-permitted mixed hashable state representation, not a generated-POSG execution defect.
- **Contract/Schema Difference:**
  - Expected by POSG contract: any hashable state identifier; strings and tuples are both explicitly permitted.
  - Actual graph: `initial_state()` returns the tuple `("auction", "low", "high")` at generated.py:7; `transition()` returns string terminal states at generated.py:42, 44, and 45. NetworkX's modularity routine implicitly requires mutually orderable node labels when priorities tie.
- **Stack Trace Summary:** `ExperimentRunner.run_case()` → `WorldModelEDA.summary()` (`eda.py:461`) → `graph_statistics()` (`eda.py:348`) → NetworkX `greedy_modularity_communities()` → `MappedQueue`/`heapq.heapify()` → failed comparison between `str` and `tuple`.
- **Recommended Fix:** Fix the evaluator by relabeling graph nodes to stable integer IDs before community detection (or pass a deterministic comparable tie-break key), while retaining original labels as attributes. As a secondary prompt guardrail, require one uniform state-ID type per generated model, but do not treat mixed hashable types as a POSG contract violation.

---

### Qwen 3.8 27B — Game G9

- **Failure Category:** Interface Failure (empty/truncated generation)
- **File & Function:** no `generated.py` exists; backend check at `experiments/run_openrouter_game_experiments.py:124–126`.
- **Error Message / Trace:** `RuntimeError: OpenRouter returned no message content: {'id': 'gen-1788020394-4Avi6RpoSuql6uYzp4Ts', 'object': 'chat.completion', 'created': 1788020394, 'model': 'qwen/qwen3.8-27b', 'provider': 'Parasail', 'system_fingerprint': None, 'service_tier': None, 'cho…`
- **Root Cause Analysis:** During the Colonel-Blotto generation, OpenRouter returned `finish_reason="length"`, `content=null`, and 8,192 completion tokens entirely in the reasoning channel. The backend read `message.content` at line 124, found it empty, and raised `RuntimeError` at line 126. Generation therefore failed before Python parsing or `GeneratedPOSG` interface inspection; there are no missing methods or altered signatures to list.
- **Contract/Schema Difference:**
  - Expected: a non-empty assistant `content` string containing `class GeneratedPOSG(AbstractPOSG)` with `players`, `initial_state`, `legal_actions`, `transition`, `observation`, `reward`, and `is_terminal`.
  - Actual: no code content and consequently no class or callable interface; only truncated reasoning was returned.
- **Taxonomy Note:** `classify_failure()` labeled this `interface_failure` because the serialized provider payload echoed the prompt terms `GeneratedPOSG`/`AbstractPOSG`. The primary cause is output-budget exhaustion, not an interface mismatch.
- **Recommended Fix:** For reasoning models, reserve a separate/larger output budget or disable reasoning for code-only generations. Treat `finish_reason=length` or `content is None` as a dedicated `generation_truncated` category and retry once with constrained reasoning and a higher content budget.

---

## Cross-Cutting Findings and Prevention Priorities

1. **Make the observation type unambiguous.** Fifteen of 22 failures are the same tuple-versus-string contract violation. Put `MUST return str on every branch` immediately beside the method signature and validate generated AST return sites before paid evaluation.
2. **Separate generation failures from interface failures.** Qwen G2/G9 never produced code. Add `generation_truncated` and preserve compact provider metadata (`finish_reason`, content-token count, reasoning-token count) rather than embedding the entire provider response in `error_message`.
3. **Make EDA label-agnostic.** Relabel nodes to integers before NetworkX modularity/heap algorithms. The POSG contract permits any hashable label, so evaluator metrics must not require cross-type ordering.
4. **Validate syntax and interface before rollout.** Strip incomplete fences, call `ast.parse`, inspect required method signatures, and enforce `list[str]` actions with a cheap preflight.
5. **Persist real tracebacks and validation details.** `result.json` currently stores flattened errors only. Add `validation_details.json` and `traceback.txt` so future reports need not reproduce evaluator exceptions.
