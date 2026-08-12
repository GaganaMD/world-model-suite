## Test Case 3.1: Robot With Key, Door, and Lamp

### LLM Input

A robot is in Room A. A key lies on the floor. A locked door is in the room. A lamp is also in the room and is currently off. The robot can pick up the key, try to open the door, turn on the lamp, wait, or do something else. The key is needed to open the locked door. Turning on the lamp changes the lighting but does not unlock the door.

### Expected LLM Output

```json
{
  "players": [
    {
      "id": "robot",
      "description": "A robot in a room with a key, locked door, and lamp"
    }
  ],
  "initial_state": "s0",
  "states": {
    "s0": {
      "description": "Robot in Room A; key on floor; door locked; lamp off; robot has no key.",
      "terminal": false
    },
    "s1": {
      "description": "Robot has key; door locked; lamp off.",
      "terminal": false
    },
    "s2": {
      "description": "Robot has no key; door locked; lamp on.",
      "terminal": false
    },
    "s3": {
      "description": "Robot has key; door locked; lamp on.",
      "terminal": false
    },
    "s4": {
      "description": "Door open; lamp off.",
      "terminal": true
    },
    "s5": {
      "description": "Door open; lamp on.",
      "terminal": true
    }
  },
  "actions": {
    "s0": {
      "robot": [
        "pick_up_key",
        "try_open_door",
        "turn_on_lamp",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s1": {
      "robot": [
        "try_open_door",
        "turn_on_lamp",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s2": {
      "robot": [
        "pick_up_key",
        "try_open_door",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s3": {
      "robot": [
        "try_open_door",
        "wait_or_pass",
        "do_something_else"
      ]
    }
  },
  "transition_probabilities": {
    "s0": {
      "pick_up_key": { "s1": 1.0 },
      "try_open_door": { "s0": 1.0 },
      "turn_on_lamp": { "s2": 1.0 },
      "wait_or_pass": { "s0": 1.0 },
      "do_something_else": { "s0": 1.0 }
    },
    "s1": {
      "try_open_door": { "s4": 1.0 },
      "turn_on_lamp": { "s3": 1.0 },
      "wait_or_pass": { "s1": 1.0 },
      "do_something_else": { "s1": 1.0 }
    },
    "s2": {
      "pick_up_key": { "s3": 1.0 },
      "try_open_door": { "s2": 1.0 },
      "wait_or_pass": { "s2": 1.0 },
      "do_something_else": { "s2": 1.0 }
    },
    "s3": {
      "try_open_door": { "s5": 1.0 },
      "wait_or_pass": { "s3": 1.0 },
      "do_something_else": { "s3": 1.0 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* one player: the robot;
* an initial state with the key on the floor, the door locked, and the lamp off, marked `terminal: false`;
* `pick_up_key`, `try_open_door`, `turn_on_lamp`, and wait/pass;
* turning on the lamp as a real, tracked state change;
* no connection between turning on the lamp and unlocking the door — a door-open state must be reachable regardless of lamp status, and the lamp's on/off status prior to opening the door must still be distinguishable afterward (two separate door-open states — one per lamp status — not one merged/ambiguous state);
* failed door-opening attempts when the robot lacks the key, self-looping back to the current state (no key, no lamp change) rather than jumping to some other state;
* successful door opening only after the robot has the key;
* `wait_or_pass` and `do_something_else` both self-looping back to the *current* state, preserving key possession and lamp status rather than collapsing into one generic "did something else" state;
* the two door-open states marked `terminal: true`; every other state marked `terminal: false`.
