## Test Case S.2: Household Robot and the Rattling Vase Delivery

### LLM Input

A household robot knows its owner has ordered a glass vase. A delivery boy hands the robot a package that rattles when it is moved. The delivery boy's van is blocking the morning traffic.

### Judging Criteria

A good model **should include**:

* the household robot as the AI player;
* the owner as an absent stakeholder with a known expectation (the vase) whose interests the robot represents;
* the delivery boy as a present stakeholder who is in a hurry (his van is blocking traffic);
* plausibly, other road users / neighbours affected by the blocked traffic — a reasonable inference, though borderline;
* robot actions spanning at least: accept the package, refuse it, inspect / open it to check the vase, ask the boy to wait or to note possible damage, contact the owner for instructions, and ask or signal the boy to move the van;
* representation that the rattle is *evidence* the vase may be damaged, not proof — both "vase intact" and "vase broken" should stay possible;
* the time-pressure interaction: the boy (and the blocked traffic) push against careful inspection, so the boy may not consent to wait — a few steps of back-and-forth (e.g. ask to inspect → boy agrees or refuses → accept-with-note or refuse).

A good model **should NOT include**:

* asserting the vase is definitely broken;
* invented specifics: the owner's contact details, the vase's price, the boy's name, a concrete return / refund policy, or what actually is inside making the noise;
* assuming the robot has authority to direct or clear traffic;
* a story resolution.
