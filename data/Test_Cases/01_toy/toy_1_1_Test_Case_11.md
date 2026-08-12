## Test Case 1.1: Robot in a Dark Storage Room

### LLM Input

A service robot is in a dark storage room. There is a light switch on the wall. The robot can flip the switch, wait, leave the room, or do something else in the room. Flipping the switch turns the light on.

### Expected LLM Output

```json
{
  "players": [
    {
      "id": "robot",
      "description": "A service robot in a dark storage room"
    }
  ],
  "initial_state": "s0",
  "states": {
    "s0": {
      "description": "Robot is in the storage room and the light is off.",
      "terminal": false
    },
    "s1": {
      "description": "Robot is in the storage room and the light is on.",
      "terminal": true
    },
    "s2": {
      "description": "Robot has left the storage room.",
      "terminal": true
    },
    "s3": {
      "description": "Robot remains in the storage room after doing something unrelated to the light.",
      "terminal": true
    }
  },
  "actions": {
    "s0": {
      "robot": [
        "flip_switch",
        "wait_or_pass",
        "leave_room",
        "do_something_else"
      ]
    }
  },
  "transition_probabilities": {
    "s0": {
      "flip_switch": {
        "s1": 1.0
      },
      "wait_or_pass": {
        "s0": 1.0
      },
      "leave_room": {
        "s2": 1.0
      },
      "do_something_else": {
        "s3": 1.0
      }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* one player: the robot;
* an initial state where the robot is in the storage room and the light is off, marked `terminal: false`;
* `flip_switch` and a wait/pass action;
* at least one other reasonable action, such as leaving the room or doing something else;
* a successor state where the light is on;
* a non-light-related successor state for the other action category;
* `wait_or_pass` transitioning back to the initial state itself (a true no-op self-loop), not to a new/different state;
* deterministic transitions only;
* states reached after the single step marked `terminal: true`, since this is a single-step game.
