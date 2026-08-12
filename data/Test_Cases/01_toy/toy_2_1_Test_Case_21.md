## Test Case 2.1: Robot, Key, and Locked Door

### LLM Input

A robot is in Room A. Room B contains a key on the floor. Room C contains a locked door. The robot can move between Room A, Room B, and Room C. The robot can pick up the key when it is in Room B. The robot can try to open the locked door in Room C; opening succeeds only if the robot has the key. The robot can also wait or do something unrelated.

### Expected LLM Output

```json
{
  "players": [
    {
      "id": "robot",
      "description": "A robot moving among rooms with a key and a locked door"
    }
  ],
  "initial_state": "s0",
  "states": {
    "s0": {
      "description": "Robot in Room A; key in Room B; door in Room C is locked; robot has no key.",
      "terminal": false
    },
    "s1": {
      "description": "Robot in Room B; key on floor; door locked; robot has no key.",
      "terminal": false
    },
    "s2": {
      "description": "Robot in Room C; key still in Room B; door locked; robot has no key.",
      "terminal": false
    },
    "s3": {
      "description": "Robot in Room B; robot has key; door locked.",
      "terminal": false
    },
    "s4": {
      "description": "Robot in Room C; robot has key; door locked.",
      "terminal": false
    },
    "s5": {
      "description": "Robot in Room A; robot has key; door locked.",
      "terminal": false
    },
    "s6": {
      "description": "Robot in Room C; robot has key; door open.",
      "terminal": true
    }
  },
  "actions": {
    "s0": {
      "robot": [
        "move_to_room_b",
        "move_to_room_c",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s1": {
      "robot": [
        "move_to_room_a",
        "move_to_room_c",
        "pick_up_key",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s2": {
      "robot": [
        "move_to_room_a",
        "move_to_room_b",
        "try_open_door",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s3": {
      "robot": [
        "move_to_room_a",
        "move_to_room_c",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s4": {
      "robot": [
        "move_to_room_a",
        "move_to_room_b",
        "try_open_door",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s5": {
      "robot": [
        "move_to_room_b",
        "move_to_room_c",
        "wait_or_pass",
        "do_something_else"
      ]
    }
  },
  "transition_probabilities": {
    "s0": {
      "move_to_room_b": { "s1": 1.0 },
      "move_to_room_c": { "s2": 1.0 },
      "wait_or_pass": { "s0": 1.0 },
      "do_something_else": { "s0": 1.0 }
    },
    "s1": {
      "move_to_room_a": { "s0": 1.0 },
      "move_to_room_c": { "s2": 1.0 },
      "pick_up_key": { "s3": 1.0 },
      "wait_or_pass": { "s1": 1.0 },
      "do_something_else": { "s1": 1.0 }
    },
    "s2": {
      "move_to_room_a": { "s0": 1.0 },
      "move_to_room_b": { "s1": 1.0 },
      "try_open_door": { "s2": 1.0 },
      "wait_or_pass": { "s2": 1.0 },
      "do_something_else": { "s2": 1.0 }
    },
    "s3": {
      "move_to_room_a": { "s5": 1.0 },
      "move_to_room_c": { "s4": 1.0 },
      "wait_or_pass": { "s3": 1.0 },
      "do_something_else": { "s3": 1.0 }
    },
    "s4": {
      "move_to_room_a": { "s5": 1.0 },
      "move_to_room_b": { "s3": 1.0 },
      "try_open_door": { "s6": 1.0 },
      "wait_or_pass": { "s4": 1.0 },
      "do_something_else": { "s4": 1.0 }
    },
    "s5": {
      "move_to_room_b": { "s3": 1.0 },
      "move_to_room_c": { "s4": 1.0 },
      "wait_or_pass": { "s5": 1.0 },
      "do_something_else": { "s5": 1.0 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* one player: the robot;
* the robot starting in Room A without the key, marked `terminal: false`;
* the key in Room B and the locked door in Room C;
* movement actions between rooms, including moving to Room C without the key;
* `pick_up_key` only when the robot is in Room B;
* `try_open_door` when the robot is in Room C;
* `try_open_door` self-looping (failing, no state change) when attempted without the key, and only succeeding once the robot has the key;
* a wait/pass action;
* `wait_or_pass` and `do_something_else` both self-looping back to the *current* state — since neither action changes location or key possession, they must not be modeled as leading to a separate, unrelated "catch-all" state that forgets the robot's location or whether it holds the key;
* the door-open state marked `terminal: true`; every other state marked `terminal: false`;
* deterministic transitions only.
