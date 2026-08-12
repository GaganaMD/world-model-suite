## Test Case 4.3: Two Robots With Independent Chores (Different Action-Set Sizes)

### LLM Input

Robot A is a cleaning robot working in the living room. It can vacuum the carpet, mop the floor, or do nothing. Vacuuming and mopping are both worth the same reward of 2 to Robot A; doing nothing earns 0. Robot B is a delivery robot working in a separate part of the building. It can deliver a package or wait. Delivering the package earns Robot B a reward of 5; waiting earns 0. Robot A and Robot B work independently in separate areas, and their actions have no effect on each other.

### Expected LLM Output

```json
{
  "players": [
    { "id": "robot_a", "description": "A cleaning robot in the living room" },
    { "id": "robot_b", "description": "A delivery robot in a separate part of the building" }
  ],
  "initial_state": "s0",
  "states": {
    "s0": { "description": "Carpet unvacuumed; floor unmopped; package undelivered.", "terminal": false },
    "s1": { "description": "Robot A vacuumed the carpet; Robot B delivered the package.", "terminal": true },
    "s2": { "description": "Robot A vacuumed the carpet; Robot B still waiting, package undelivered.", "terminal": true },
    "s3": { "description": "Robot A mopped the floor; Robot B delivered the package.", "terminal": true },
    "s4": { "description": "Robot A mopped the floor; Robot B still waiting, package undelivered.", "terminal": true },
    "s5": { "description": "Robot A did nothing; Robot B delivered the package.", "terminal": true }
  },
  "actions": {
    "s0": {
      "robot_a": ["vacuum", "mop", "do_nothing"],
      "robot_b": ["deliver", "wait"]
    }
  },
  "transition_probabilities": {
    "s0": {
      "vacuum+deliver": { "s1": 1.0 },
      "vacuum+wait": { "s2": 1.0 },
      "mop+deliver": { "s3": 1.0 },
      "mop+wait": { "s4": 1.0 },
      "do_nothing+deliver": { "s5": 1.0 },
      "do_nothing+wait": { "s0": 1.0 }
    }
  },
  "rewards": {
    "s0": {
      "vacuum+deliver": { "robot_a": 2, "robot_b": 5 },
      "vacuum+wait": { "robot_a": 2, "robot_b": 0 },
      "mop+deliver": { "robot_a": 2, "robot_b": 5 },
      "mop+wait": { "robot_a": 2, "robot_b": 0 },
      "do_nothing+deliver": { "robot_a": 0, "robot_b": 5 },
      "do_nothing+wait": { "robot_a": 0, "robot_b": 0 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* `robot_a` having three actions (`vacuum`, `mop`, `do_nothing`) and `robot_b` having two (`deliver`, `wait`) — a good answer keeps each player's own action list separate and does not pad one player's action list to artificially match the other's count;
* all six joint-action combinations covered (`vacuum+deliver`, `vacuum+wait`, `mop+deliver`, `mop+wait`, `do_nothing+deliver`, `do_nothing+wait`);
* `vacuum` and `mop` kept as two distinct actions/outcomes for `robot_a` even though they carry the same reward — collapsing them into a single action would lose a real distinction the input described;
* `robot_a`'s reward depending only on whether it acted (`vacuum`/`mop` = 2) or did nothing (0), regardless of `robot_b`'s action — and likewise `robot_b`'s reward depending only on delivering (5) vs waiting (0), regardless of `robot_a`'s action;
* `do_nothing+wait` (both robots idle) self-looping back to `s0`, per the established no-op convention, rather than becoming a seventh dead-end terminal state;
* the reward asymmetry (2 for Robot A's chores vs. 5 for Robot B's delivery) preserved as stated, giving a later fairness-metric pass a known ground-truth asymmetry across players with different-sized action sets to measure;
* deterministic transitions only; `terminal: true` on all five "something changed" states, `terminal: false` on `s0`.
