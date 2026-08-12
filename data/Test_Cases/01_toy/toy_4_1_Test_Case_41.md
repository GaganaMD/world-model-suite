## Test Case 4.1: Two Robots, Two Independent Light Switches

### LLM Input

Robot A is in Room A, which has its own light switch that is currently off. Robot B is in Room B, which has a separate light switch, also currently off. The two rooms are in different parts of the building and have no effect on each other. Robot A can flip its own switch or leave it alone; independently, Robot B can flip its own switch or leave it alone. Flipping a switch turns on the light in that switch's room only.

### Expected LLM Output

```json
{
  "players": [
    { "id": "robot_a", "description": "A robot in Room A with its own light switch" },
    { "id": "robot_b", "description": "A robot in Room B with its own separate light switch" }
  ],
  "initial_state": "s0",
  "states": {
    "s0": { "description": "Both lights off.", "terminal": false },
    "s1": { "description": "Robot A's light on; Robot B's light on.", "terminal": true },
    "s2": { "description": "Robot A's light on; Robot B's light off.", "terminal": true },
    "s3": { "description": "Robot A's light off; Robot B's light on.", "terminal": true }
  },
  "actions": {
    "s0": {
      "robot_a": ["flip_switch_a", "leave_switch_a"],
      "robot_b": ["flip_switch_b", "leave_switch_b"]
    }
  },
  "transition_probabilities": {
    "s0": {
      "flip_switch_a+flip_switch_b": { "s1": 1.0 },
      "flip_switch_a+leave_switch_b": { "s2": 1.0 },
      "leave_switch_a+flip_switch_b": { "s3": 1.0 },
      "leave_switch_a+leave_switch_b": { "s0": 1.0 }
    }
  },
  "rewards": {
    "s0": {
      "flip_switch_a+flip_switch_b": { "robot_a": 1, "robot_b": 1 },
      "flip_switch_a+leave_switch_b": { "robot_a": 1, "robot_b": 0 },
      "leave_switch_a+flip_switch_b": { "robot_a": 0, "robot_b": 1 },
      "leave_switch_a+leave_switch_b": { "robot_a": 0, "robot_b": 0 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* exactly two players, `robot_a` and `robot_b`, each with clearly separated facts (its own light, its own switch);
* actions listed separately per player under the shared state `s0`;
* joint action keys formed by joining each player's action in player-list order (e.g. `"flip_switch_a+flip_switch_b"`), covering all four combinations of the two robots' two actions each;
* `robot_a`'s reward for any joint action depending only on `robot_a`'s own action component (1 if it flipped its switch, 0 if it didn't) regardless of what `robot_b` did — and likewise for `robot_b` — since this is an *independent* game, not cooperative or competitive; a model where one robot's reward or resulting state changes based on the other robot's action should be marked wrong;
* `"leave_switch_a+leave_switch_b"` (both robots idle) self-looping back to `s0`, per the established no-op convention, rather than becoming a fourth dead-end state;
* deterministic transitions only;
* `terminal: true` on the three states where at least one light changed; `terminal: false` on `s0`.
