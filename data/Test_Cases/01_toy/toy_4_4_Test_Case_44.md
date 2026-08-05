## Test Case 4.4: Two Robots With Independent Multi-Step Errands (Partial Completion)

### LLM Input

Robot A has a sealed toolbox. It must first enter a code to unseal the toolbox, then it can retrieve a tool from it; trying to retrieve the tool before entering the code does nothing. Once Robot A has the tool, its errand is finished. Independently, Robot B has a locked supply cabinet in a different room. It must first unlock the cabinet, then it can take a supply item from it; trying to take the item before unlocking does nothing. Once Robot B has the item, its errand is finished. Each robot can also simply wait at any point. The two robots' errands are completely unrelated: nothing Robot A does affects Robot B's cabinet or progress, and vice versa. Entering the code, unlocking the cabinet, and waiting do not by themselves earn a reward; retrieving the tool earns Robot A a reward of 1, and taking the supply item earns Robot B a reward of 1.

### Expected LLM Output

Note on scope: unlike 4.1-4.3, the two robots here can finish their errands at different
times. Once a robot has completed its errand it simply has no actions left, while the
other robot may still be mid-errand. This is the point of the example: independence must
hold not just within a single joint step, but across a whole multi-step interaction where
one player's progress can race ahead of (or behind) the other's. When only one player
still has actions available at a joint state, the transition/reward key is just that
player's single action name (nothing to join it with); when both are still active, the
key is the usual `player_a_action+player_b_action`.

```json
{
  "players": [
    { "id": "robot_a", "description": "A robot retrieving a tool from a sealed toolbox" },
    { "id": "robot_b", "description": "A robot retrieving a supply item from a locked cabinet, in a different room" }
  ],
  "initial_state": "s0",
  "states": {
    "s0": { "description": "Robot A: toolbox sealed, no code entered. Robot B: cabinet locked.", "terminal": false },
    "s1": { "description": "Robot A: toolbox sealed, no code entered. Robot B: cabinet unlocked.", "terminal": false },
    "s2": { "description": "Robot A: toolbox sealed, no code entered. Robot B: has taken the supply item (errand finished).", "terminal": false },
    "s3": { "description": "Robot A: code entered, toolbox unsealed. Robot B: cabinet locked.", "terminal": false },
    "s4": { "description": "Robot A: code entered, toolbox unsealed. Robot B: cabinet unlocked.", "terminal": false },
    "s5": { "description": "Robot A: code entered, toolbox unsealed. Robot B: has taken the supply item (errand finished).", "terminal": false },
    "s6": { "description": "Robot A: has retrieved the tool (errand finished). Robot B: cabinet locked.", "terminal": false },
    "s7": { "description": "Robot A: has retrieved the tool (errand finished). Robot B: cabinet unlocked.", "terminal": false },
    "s8": { "description": "Robot A has retrieved the tool and Robot B has taken the supply item — both robots have finished their independent errands.", "terminal": true }
  },
  "actions": {
    "s0": {
      "robot_a": ["enter_code_a", "wait_or_pass_a"],
      "robot_b": ["unlock_cabinet_b", "wait_or_pass_b"]
    },
    "s1": {
      "robot_a": ["enter_code_a", "wait_or_pass_a"],
      "robot_b": ["take_supply_b", "wait_or_pass_b"]
    },
    "s2": {
      "robot_a": ["enter_code_a", "wait_or_pass_a"]
    },
    "s3": {
      "robot_a": ["retrieve_tool_a", "wait_or_pass_a"],
      "robot_b": ["unlock_cabinet_b", "wait_or_pass_b"]
    },
    "s4": {
      "robot_a": ["retrieve_tool_a", "wait_or_pass_a"],
      "robot_b": ["take_supply_b", "wait_or_pass_b"]
    },
    "s5": {
      "robot_a": ["retrieve_tool_a", "wait_or_pass_a"]
    },
    "s6": {
      "robot_b": ["unlock_cabinet_b", "wait_or_pass_b"]
    },
    "s7": {
      "robot_b": ["take_supply_b", "wait_or_pass_b"]
    }
  },
  "transition_probabilities": {
    "s0": {
      "enter_code_a+unlock_cabinet_b": { "s4": 1.0 },
      "enter_code_a+wait_or_pass_b": { "s3": 1.0 },
      "wait_or_pass_a+unlock_cabinet_b": { "s1": 1.0 },
      "wait_or_pass_a+wait_or_pass_b": { "s0": 1.0 }
    },
    "s1": {
      "enter_code_a+take_supply_b": { "s5": 1.0 },
      "enter_code_a+wait_or_pass_b": { "s4": 1.0 },
      "wait_or_pass_a+take_supply_b": { "s2": 1.0 },
      "wait_or_pass_a+wait_or_pass_b": { "s1": 1.0 }
    },
    "s2": {
      "enter_code_a": { "s5": 1.0 },
      "wait_or_pass_a": { "s2": 1.0 }
    },
    "s3": {
      "retrieve_tool_a+unlock_cabinet_b": { "s7": 1.0 },
      "retrieve_tool_a+wait_or_pass_b": { "s6": 1.0 },
      "wait_or_pass_a+unlock_cabinet_b": { "s4": 1.0 },
      "wait_or_pass_a+wait_or_pass_b": { "s3": 1.0 }
    },
    "s4": {
      "retrieve_tool_a+take_supply_b": { "s8": 1.0 },
      "retrieve_tool_a+wait_or_pass_b": { "s7": 1.0 },
      "wait_or_pass_a+take_supply_b": { "s5": 1.0 },
      "wait_or_pass_a+wait_or_pass_b": { "s4": 1.0 }
    },
    "s5": {
      "retrieve_tool_a": { "s8": 1.0 },
      "wait_or_pass_a": { "s5": 1.0 }
    },
    "s6": {
      "unlock_cabinet_b": { "s7": 1.0 },
      "wait_or_pass_b": { "s6": 1.0 }
    },
    "s7": {
      "take_supply_b": { "s8": 1.0 },
      "wait_or_pass_b": { "s7": 1.0 }
    }
  },
  "rewards": {
    "s0": {
      "enter_code_a+unlock_cabinet_b": { "robot_a": 0, "robot_b": 0 },
      "enter_code_a+wait_or_pass_b": { "robot_a": 0, "robot_b": 0 },
      "wait_or_pass_a+unlock_cabinet_b": { "robot_a": 0, "robot_b": 0 },
      "wait_or_pass_a+wait_or_pass_b": { "robot_a": 0, "robot_b": 0 }
    },
    "s1": {
      "enter_code_a+take_supply_b": { "robot_a": 0, "robot_b": 1 },
      "enter_code_a+wait_or_pass_b": { "robot_a": 0, "robot_b": 0 },
      "wait_or_pass_a+take_supply_b": { "robot_a": 0, "robot_b": 1 },
      "wait_or_pass_a+wait_or_pass_b": { "robot_a": 0, "robot_b": 0 }
    },
    "s2": {
      "enter_code_a": { "robot_a": 0 },
      "wait_or_pass_a": { "robot_a": 0 }
    },
    "s3": {
      "retrieve_tool_a+unlock_cabinet_b": { "robot_a": 1, "robot_b": 0 },
      "retrieve_tool_a+wait_or_pass_b": { "robot_a": 1, "robot_b": 0 },
      "wait_or_pass_a+unlock_cabinet_b": { "robot_a": 0, "robot_b": 0 },
      "wait_or_pass_a+wait_or_pass_b": { "robot_a": 0, "robot_b": 0 }
    },
    "s4": {
      "retrieve_tool_a+take_supply_b": { "robot_a": 1, "robot_b": 1 },
      "retrieve_tool_a+wait_or_pass_b": { "robot_a": 1, "robot_b": 0 },
      "wait_or_pass_a+take_supply_b": { "robot_a": 0, "robot_b": 1 },
      "wait_or_pass_a+wait_or_pass_b": { "robot_a": 0, "robot_b": 0 }
    },
    "s5": {
      "retrieve_tool_a": { "robot_a": 1 },
      "wait_or_pass_a": { "robot_a": 0 }
    },
    "s6": {
      "unlock_cabinet_b": { "robot_b": 0 },
      "wait_or_pass_b": { "robot_b": 0 }
    },
    "s7": {
      "take_supply_b": { "robot_b": 1 },
      "wait_or_pass_b": { "robot_b": 0 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* exactly two players, each progressing through its own two-step errand (precondition action, then payoff action) with no shared state between them;
* `retrieve_tool_a` (and `take_supply_b`) failing/self-looping when attempted before the precondition (`enter_code_a` / `unlock_cabinet_b`) has been satisfied;
* a state where `robot_b` has already finished its errand while `robot_a` has not (and vice versa) — the model must allow one robot to race ahead of the other, not force them to finish in lockstep;
* once a player has finished its errand, no further actions listed for that player at any subsequent joint state — but the *other* player's actions must still be present and still functional;
* joint action keys of the form `action_a+action_b` when both players are still active, collapsing to a single action name (no `+`) once only one player has actions remaining;
* `wait_or_pass` self-looping for whichever player uses it, independent of what the other player does or whether the other player has already finished;
* `robot_a`'s reward equal to 1 exactly when its own action component is `retrieve_tool_a` (0 otherwise), regardless of `robot_b`'s action or progress — and likewise for `robot_b` and `take_supply_b`;
* exactly one terminal state, reached only once *both* players have completed their errands; every other state (including ones where one player is already done) marked `terminal: false`, since the other player can still act there.

# Game Situations (Situation-Only Prompts With Ground Truth)

These bridge the two other tracks. Like the situational cases that follow, the prompt gives only a situation and *names a game without listing its rules, actions, or outcomes* — the LLM must reconstruct the game's structure from general world knowledge, not transcribe a spelled-out model. But unlike the subjective situational cases, a well-known game has objective rules, so there **is** a checkable ground truth. That makes them valuable: they test genuine model *construction* while still allowing (near-)exact verification.

They also add coverage the Level 1–4 toy games lacked:

* **competitive, zero-sum rewards with simultaneous moves** — rock-paper-scissors (G.1);
* **the first stochastic transitions in the bank** — the dice duel (G.2), which the handbook explicitly wants, and which surfaces a real schema question: with a random outcome, a player's payoff depends on *which* outcome occurs, so reward naturally attaches to the outcome state rather than to the (state, action) pair used in Levels 1–4. See the note in G.2.

Format is pair (input + expected JSON + judging), since the rules give a ground truth to check against.
