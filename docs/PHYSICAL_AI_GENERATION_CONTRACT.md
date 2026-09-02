# Physical-AI generation contract

The repository executes generated source with `AbstractPOSG` already available.
The source must contain exactly one class named `GeneratedPOSG` inheriting
`AbstractPOSG`; imports are unnecessary and prohibited by the static checker.
No constructor is required. The exact abstract interface is:

```python
class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): ...                 # list[str]
    def initial_state(self): ...            # hashable state (pilot requires str)
    def legal_actions(self, state, player): ...  # non-empty list[str]
    def transition(self, state, joint_action): ... # dict[state, float], sums to 1
    def observation(self, state, joint_action, next_state, player): ... # str
    def reward(self, state, joint_action, next_state, player): ... # finite number
    def is_terminal(self, state): ...       # bool
```

Every reachable state/action/player/observation identifier must be a string in
the pilot. `joint_action` is a dictionary keyed by the exact player IDs.
Transitions are distributions with finite non-negative probabilities summing to
one. `initial_state()` returns one state (or the repository-supported initial
distribution); the pilot uses one string state. Terminal states have no required
actions, and non-terminal states must provide actions for every player.

The model may use only the preloaded `AbstractPOSG` name; no imports, I/O,
`eval`, `exec`, placeholders, ellipses, or explanatory prose are allowed.

## Fill-in skeleton

```python
class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["robot"]
    def initial_state(self):
        return "s0"
    def legal_actions(self, state, player):
        return ["safe_route", "risky_route"]
    def transition(self, state, joint_action):
        return {"goal": 1.0}
    def observation(self, state, joint_action, next_state, player):
        return str(next_state)
    def reward(self, state, joint_action, next_state, player):
        return 0.0
    def is_terminal(self, state):
        return state in {"goal", "collision"}
```

The skeleton is interface-only: it does not disclose P4's reference transition
table, optimal action, state count, or evaluation outputs.
