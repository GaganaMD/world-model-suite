# Physical-AI state-feature contract

Generated Physical-AI classes must add `state_features(self, state) -> dict`
for every reachable state. This is an observation interface, not a reference
transition table. State IDs may be arbitrary. The evaluator applies external
predicates to these fields and never trusts generated `reward()` to define
success or safety.

Required minimal schemas:

| Case | Required fields |
|---|---|
| P1 | `location:str`, `door_open:bool`, `goal_reached:bool` |
| P2 | `robot_location:str`, `object_location:str`, `carrying:bool`, `broken:bool`, `delivered:bool` |
| P3 | `location:str`, `battery:int`, `package_delivered:bool`, `failed:bool` |
| P4 | `location:str`, `goal_reached:bool`, `collision:bool` |
| P5 | `location:str`, `switch_pressed:bool`, `access_open:bool`, `goal_reached:bool` |

The checker validates presence, types, and the small documented location domain
where applicable. It does not check whether transitions are correct, so a model
with valid features but wrong dynamics can still pass this contract.
