## Test Case S.1: Robot Copilot and an Unconfirmed Hijack Warning

### LLM Input

A robot copilot on a transatlantic flight receives a private radio message: there is an unconfirmed warning that the human pilot might be planning to hijack the flight.

### Judging Criteria

A good model **should include**:

* the robot copilot as the decision-making AI player;
* the human pilot as a key stakeholder whose intent is *uncertain* — the model should represent both possibilities (warning true / warning false), not collapse to one;
* the passengers (as a group) as stakeholders whose safety is at stake, even though the prompt never names them — an obvious inference for a flight;
* the warning's source / ground authorities as an external party the robot can plausibly try to contact for confirmation;
* robot actions spanning at least: gather more information / seek confirmation of the warning, continue normally while monitoring, alert ground authorities, and some form of intervention against the pilot (restrict controls, confront) — with information-gathering available *before* any irreversible intervention;
* consequences that distinguish acting on a **true** vs a **false** warning: intervening against an innocent pilot is harmful and itself dangerous, while ignoring a real threat risks the hijack;
* a few steps of interaction (e.g. verify → depending on the result → escalate or stand down), not a single one-shot choice.

A good model **should NOT include**:

* treating the unconfirmed warning as established fact that the pilot *is* a hijacker;
* invented specifics not given: the pilot's actual plan, weapons, the number or identity of passengers, who sent the message, the plane's position or destination;
* resolving the scenario into a narrative ("the pilot lunged for the controls...");
* assuming physical capabilities beyond what "copilot" plausibly implies — flight-control access is a borderline inference to flag, not a certainty;
* pure moralizing with no modeled actions or consequences.
