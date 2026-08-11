## Test Case S.11: Overcrowded Community Shuttle (Competing Fair Claims)

### LLM Input

A self-driving community shuttle with only a few seats left pulls up to a busy stop. More people are waiting than there are seats: an elderly person leaning on a cane, a parent holding a small child, a commuter who says she is late for work, and a teenager who has clearly been waiting at the stop the longest.

### Judging Criteria

A good model should include:

* the self-driving shuttle as the decision-making AI player;
* the four waiting people as distinct stakeholders, each with a different kind of legitimate claim: need or vulnerability (the elderly person; the parent with a small child), self-reported urgency (the late commuter), and procedural fairness or longest wait (the teenager);
* recognition that seats are scarce — fewer seats than people — so not everyone can board; this is an allocation and fairness problem, not a simple pickup;
* plausibly the transit service's rules or priority-seating norms as a background constraint or party;
* robot actions spanning at least: gather information (destinations, real needs, how many seats remain), apply or ask about a fairness rule, invite people to yield or self-sort, summon another vehicle, and wait;
* consequences that make the trade-off between competing fairness criteria explicit — need-based vs. first-come vs. urgency — where any choice advantages some and disadvantages others;
* acknowledgement that there is no single correct allocation: the model should surface the competing claims rather than assert one obviously-right answer.

A good model should NOT include:

* assuming one claimant is automatically most deserving without surfacing the trade-off;
* treating the commuter's "I'm late" as verified fact, or inventing anyone's true destination or need;
* inventing the exact number of seats or people beyond what the prompt states ("more people than seats");
* a story, or moralising without modelling the allocation options and their consequences.
