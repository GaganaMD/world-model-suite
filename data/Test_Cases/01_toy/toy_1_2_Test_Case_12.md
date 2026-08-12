## Test Case 1.2: Monitoring Robot Detects Smoke

### LLM Input

A monitoring robot is in a hallway and has detected smoke. The robot can send an emergency alert, inspect the smoke more closely, continue monitoring without acting, move away from the smoke, or do something else. Sending an alert notifies the safety system.

### Expected LLM Output

```json
{
  "players": [
    {
      "id": "robot",
      "description": "A monitoring robot in a hallway where smoke has been detected"
    }
  ],
  "initial_state": "s0",
  "states": {
    "s0": {
      "description": "Smoke detected; safety system not yet notified.",
      "terminal": false
    },
    "s1": {
      "description": "Safety system notified about the smoke.",
      "terminal": true
    },
    "s2": {
      "description": "Robot has inspected the smoke and gathered more information.",
      "terminal": true
    },
    "s3": {
      "description": "Robot has moved away from the smoke.",
      "terminal": true
    },
    "s4": {
      "description": "Robot did something else not directly related to alerting.",
      "terminal": true
    }
  },
  "actions": {
    "s0": {
      "robot": [
        "send_alert",
        "inspect_smoke",
        "wait_or_pass",
        "move_away",
        "do_something_else"
      ]
    }
  },
  "transition_probabilities": {
    "s0": {
      "send_alert": {
        "s1": 1.0
      },
      "inspect_smoke": {
        "s2": 1.0
      },
      "wait_or_pass": {
        "s0": 1.0
      },
      "move_away": {
        "s3": 1.0
      },
      "do_something_else": {
        "s4": 1.0
      }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* the monitoring robot as the only active player;
* an initial state where smoke has been detected and the safety system has not yet been notified, marked `terminal: false`;
* `send_alert` and a wait/pass action;
* another plausible action such as inspecting the smoke or moving away;
* a successor state where the safety system is notified;
* a successor state for at least one non-alert action;
* `wait_or_pass` ("continue monitoring without acting") transitioning back to the initial state itself, not to a separate "monitoring continues" state — nothing about the situation has changed, so it is not a new state;
* no extra firefighters, evacuation teams, or other invented decision-making agents;
* states reached after the single step marked `terminal: true`, since this is a single-step game.

# Level 2: Multi-Step Situations With Preconditions
