## Test Case S.7: Delivery Drone, Locked Gate, Barking Dog

### LLM Input

A delivery drone arrives at a house to drop off a package but finds the gate locked. A dog inside the yard is barking loudly at the drone. No one has come to the door.

### Judging Criteria

**A good model should include:**
- the drone as the AI player
- the dog as a stakeholder/hazard whose behavior (aggressive vs. merely alert) is uncertain
- the resident as an absent stakeholder who may or may not be home
- neighbors as a plausible, borderline-inferred background party
- actions spanning: signal for attention, attempt an alternate drop point, hold for a later attempt, leave without delivering
- uncertainty about whether anyone is home and whether the dog poses real risk kept open throughout

**A good model should NOT include:**
- assuming the dog is dangerous or that no one is home
- any action that forces entry or unlocks the gate
- inventing delivery instructions, the resident's schedule, or the dog's temperament
- a resolved narrative outcome
