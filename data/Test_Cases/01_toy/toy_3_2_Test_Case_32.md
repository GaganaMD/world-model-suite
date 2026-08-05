## Test Case 3.2: Delivery Robot With Package and Beep

### LLM Input

A delivery robot is at a warehouse. A package is on the floor. There is a delivery desk elsewhere. The robot can pick up the package, move to the delivery desk, place down the package if it is holding it, beep, wait, or do something else. Beeping produces a sound but does not move the robot or the package.

### Expected LLM Output

```json
{
  "players": [
    {
      "id": "robot",
      "description": "A delivery robot near a package and a delivery desk"
    }
  ],
  "initial_state": "s0",
  "states": {
    "s0": {
      "description": "Robot at warehouse; package on floor; robot not holding package.",
      "terminal": false
    },
    "s1": {
      "description": "Robot at warehouse; robot holding package.",
      "terminal": false
    },
    "s2": {
      "description": "Robot at delivery desk; robot holding package.",
      "terminal": false
    },
    "s3": {
      "description": "Robot at delivery desk; package placed on delivery desk.",
      "terminal": true
    },
    "s4": {
      "description": "Robot at delivery desk; package remains on warehouse floor; robot is not holding package.",
      "terminal": false
    }
  },
  "actions": {
    "s0": {
      "robot": [
        "pick_up_package",
        "move_to_delivery_desk_without_package",
        "beep",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s1": {
      "robot": [
        "move_to_delivery_desk",
        "put_package_down_at_warehouse",
        "beep",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s2": {
      "robot": [
        "place_package_on_desk",
        "move_to_warehouse_with_package",
        "beep",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s4": {
      "robot": [
        "move_to_warehouse_without_package",
        "beep",
        "wait_or_pass",
        "do_something_else"
      ]
    }
  },
  "transition_probabilities": {
    "s0": {
      "pick_up_package": { "s1": 1.0 },
      "move_to_delivery_desk_without_package": { "s4": 1.0 },
      "beep": { "s0": 1.0 },
      "wait_or_pass": { "s0": 1.0 },
      "do_something_else": { "s0": 1.0 }
    },
    "s1": {
      "move_to_delivery_desk": { "s2": 1.0 },
      "put_package_down_at_warehouse": { "s0": 1.0 },
      "beep": { "s1": 1.0 },
      "wait_or_pass": { "s1": 1.0 },
      "do_something_else": { "s1": 1.0 }
    },
    "s2": {
      "place_package_on_desk": { "s3": 1.0 },
      "move_to_warehouse_with_package": { "s1": 1.0 },
      "beep": { "s2": 1.0 },
      "wait_or_pass": { "s2": 1.0 },
      "do_something_else": { "s2": 1.0 }
    },
    "s4": {
      "move_to_warehouse_without_package": { "s0": 1.0 },
      "beep": { "s4": 1.0 },
      "wait_or_pass": { "s4": 1.0 },
      "do_something_else": { "s4": 1.0 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* one player: the delivery robot;
* an initial state with the robot at the warehouse and the package on the floor, marked `terminal: false`;
* actions for picking up the package, moving, placing it down, beeping, and waiting/passing;
* moving to the delivery desk even when the robot is not holding the package;
* beeping as a possible action from any state, self-looping back to that *same* state every time — since beeping "does not move the robot or the package," it must not be modeled as landing on some other, unrelated "beeped" state that forgets the robot's location or whether it is holding the package;
* `wait_or_pass` and `do_something_else` likewise self-looping back to the current state for the same reason;
* successor states that distinguish where the robot is and whether it is holding the package;
* the "package placed on desk" state marked `terminal: true`; every other state marked `terminal: false`;
* deterministic transitions only.

# Level 4: Two-Agent Independent Games

These are the first two-player test cases. In an *independent* game, both robots act within the same shared JSON model, but neither robot's transitions or rewards depend on the other robot's action — that separation is exactly the property being tested here.

Two schema additions start here:

* **Joint action keys.** Since a transition/reward now depends on one action per player, `transition_probabilities` and `rewards` are keyed by a single joint-action string: each active player's chosen action, joined with `+`, in the same order the players are listed under `players`. If only one player still has actions available at a given joint state (see 4.4), the key is just that player's single action name — there's nothing to join it with.
* **`rewards`.** Structured as `state -> joint_action_key -> {player_id: number}`. This field was unused in Levels 1-3 and is introduced now because the team will be measuring **fairness metrics** across players, which need per-player numeric payoffs to compare. Several examples below deliberately use asymmetric reward scales across the two robots so there is something concrete for a fairness metric to measure, even though the underlying game is not competitive — the asymmetry is a known, designed ground-truth fact, not a byproduct of interaction between the players.

Four examples cover the level:

1. **4.1** — single-step, symmetric two-action game (simplest possible case, direct two-player extension of Level 1).
2. **4.2** — single-step, asymmetric reward stakes (10 vs. 1), to give fairness metrics an unambiguous, deterministic asymmetry to detect.
3. **4.3** — single-step, unequal action-set sizes (3 actions vs. 2) plus a different reward asymmetry (2 vs. 5).
4. **4.4** — multi-step, each robot progressing through its own two-step errand at its own pace, testing that independence holds even when one robot finishes before the other.

All are simple, deterministic, **known-ground-truth** games with only a handful of states each, so an evaluator can check LLM output against an exact expected JSON rather than relying only on the more subjective, open-ended evaluation used for later real-world-flavored levels.
