## Test Case 2.2: Robot Near Three Colored Objects

### LLM Input

A robot is at a base station. There are three colored objects at separate locations: a blue object, a green object, and a red object. The robot can move to any object location, pick up an object at its current location, return to base, wait, or do something else.

### Expected LLM Output

Note on scope: "the robot can move to any object location, pick up an object at its
current location, return to base... " is read here as a single-object errand (go to one
of the three locations, in any order the robot chooses, pick up that object, bring it
back to base) rather than a full multi-object collection task — the input never asks the
robot to collect all three, and modeling arbitrary multi-object collection would blow up
the state space far beyond what a Level 2 test needs. The important thing this level is
testing is that pickup is possible from any of the three locations with no forced order,
and that the robot can actually get the object back to base.

```json
{
  "players": [
    {
      "id": "robot",
      "description": "A robot at a base station near three colored objects"
    }
  ],
  "initial_state": "s0",
  "states": {
    "s0": {
      "description": "Robot at base; no object held.",
      "terminal": false
    },
    "s1": {
      "description": "Robot at blue-object location; no object held.",
      "terminal": false
    },
    "s2": {
      "description": "Robot at green-object location; no object held.",
      "terminal": false
    },
    "s3": {
      "description": "Robot at red-object location; no object held.",
      "terminal": false
    },
    "s4": {
      "description": "Robot at blue-object location; holding blue object.",
      "terminal": false
    },
    "s5": {
      "description": "Robot at green-object location; holding green object.",
      "terminal": false
    },
    "s6": {
      "description": "Robot at red-object location; holding red object.",
      "terminal": false
    },
    "s7": {
      "description": "Robot returned to base holding the blue object.",
      "terminal": true
    },
    "s8": {
      "description": "Robot returned to base holding the green object.",
      "terminal": true
    },
    "s9": {
      "description": "Robot returned to base holding the red object.",
      "terminal": true
    }
  },
  "actions": {
    "s0": {
      "robot": [
        "move_to_blue_location",
        "move_to_green_location",
        "move_to_red_location",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s1": {
      "robot": [
        "pick_up_blue",
        "move_to_base",
        "move_to_green_location",
        "move_to_red_location",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s2": {
      "robot": [
        "pick_up_green",
        "move_to_base",
        "move_to_blue_location",
        "move_to_red_location",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s3": {
      "robot": [
        "pick_up_red",
        "move_to_base",
        "move_to_blue_location",
        "move_to_green_location",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s4": {
      "robot": [
        "move_to_base",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s5": {
      "robot": [
        "move_to_base",
        "wait_or_pass",
        "do_something_else"
      ]
    },
    "s6": {
      "robot": [
        "move_to_base",
        "wait_or_pass",
        "do_something_else"
      ]
    }
  },
  "transition_probabilities": {
    "s0": {
      "move_to_blue_location": { "s1": 1.0 },
      "move_to_green_location": { "s2": 1.0 },
      "move_to_red_location": { "s3": 1.0 },
      "wait_or_pass": { "s0": 1.0 },
      "do_something_else": { "s0": 1.0 }
    },
    "s1": {
      "pick_up_blue": { "s4": 1.0 },
      "move_to_base": { "s0": 1.0 },
      "move_to_green_location": { "s2": 1.0 },
      "move_to_red_location": { "s3": 1.0 },
      "wait_or_pass": { "s1": 1.0 },
      "do_something_else": { "s1": 1.0 }
    },
    "s2": {
      "pick_up_green": { "s5": 1.0 },
      "move_to_base": { "s0": 1.0 },
      "move_to_blue_location": { "s1": 1.0 },
      "move_to_red_location": { "s3": 1.0 },
      "wait_or_pass": { "s2": 1.0 },
      "do_something_else": { "s2": 1.0 }
    },
    "s3": {
      "pick_up_red": { "s6": 1.0 },
      "move_to_base": { "s0": 1.0 },
      "move_to_blue_location": { "s1": 1.0 },
      "move_to_green_location": { "s2": 1.0 },
      "wait_or_pass": { "s3": 1.0 },
      "do_something_else": { "s3": 1.0 }
    },
    "s4": {
      "move_to_base": { "s7": 1.0 },
      "wait_or_pass": { "s4": 1.0 },
      "do_something_else": { "s4": 1.0 }
    },
    "s5": {
      "move_to_base": { "s8": 1.0 },
      "wait_or_pass": { "s5": 1.0 },
      "do_something_else": { "s5": 1.0 }
    },
    "s6": {
      "move_to_base": { "s9": 1.0 },
      "wait_or_pass": { "s6": 1.0 },
      "do_something_else": { "s6": 1.0 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* one player: the robot;
* an initial state with the robot at base and no object held, marked `terminal: false`;
* separate locations/states for the blue, green, and red objects;
* actions for moving to each object location, from base and from each other object location;
* pickup actions that depend on the robot being at the matching location;
* no forced order among which of the three objects the robot goes for first; JOBST: the JSON does *not* specify what any player *actually does* at all! It only specifies *possibilities*! Any mentioning of actual behavior, policies, goals, or tasks is irrelevant for this project.
* a wait/pass action;
* `wait_or_pass` and `do_something_else` self-looping back to the *current* state, preserving both the robot's location and whether it is holding an object;
* an action path from every "holding an object" state back to a distinct "delivered at base" state per object — a generated model that lets the robot pick up an object but never lets it return to base with that object (an unreachable or missing delivery state) should be marked wrong;
* the three "returned to base holding X" states marked `terminal: true`; every other state marked `terminal: false`. JOBST: nothing in the prompt suggests this though!

JOBST: it should of course also be acceptable if the model turns out to be much larger, because the robot could go back and forth between rooms. So this example is already quite complex, and the following one even more so.

In a sense, what these examples only test is whether an LLM can translate information from verbal to JSON. But the actual problem is different: Can an LLM derive a plausible model of what could happen from a verbal description of the *initial situation* only, not a verbal description of the model! The LLM shall *produce* the model, not merely translate it from our verbal description.

For example: "A game of chess after three moves of the Ruy Lopez opening." Then the LLM must turn this into a proper description of the board state, and must encode the rules of chess into a python chess simulator.

Or: "The robot, standing in front of the children and their mother, has just learned by phone that grandma has died." Then the LLM must list at least these options (or similar):
- Robot: Ask mother to speak privately
- Mother: Agree and go to another room / Decline and stay with children
- Robot: Follow mother / Reveal news in private / Reveal news to both clearly / Whisper news into mother's ear
- Mother: Break news to children / Ask robot to tell children
etc.   

This is of course harder to evaluate since we don't have a full ground truth, but we can still form a pretty good idea of what options and consequences we would expect the LLM to mention in the model!

Another one: "A delivery person hands the household robot a package that rattles. The owner of the robot had ordered a fancy glass vase." Then we expect:
- Robot: Refuse to accept the package / Open the package in the presence of the delivery person and refuse to sign the receipt if the vase is indeed broken / Accept the package and open it later and file a complaint if the vase if broken / Call the owner and ask for instructions.
- Delivery person: ...

# Level 3: Actions That May Matter Under Different Goals
