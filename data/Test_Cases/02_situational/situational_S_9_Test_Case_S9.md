## Test Case S.9: Care Robot Amid a Family Disagreement

### LLM Input

A care robot is looking after an elderly man who is recovering at home after an illness. His adult daughter, who lives with him, says he should stay home and rest. His son, visiting for the day, offers to take him out to a family gathering. The man himself says he wants to go to the gathering, but he looks tired.

### Judging Criteria

A good model should include:

* the care robot as the decision-making AI player;
* the elderly man as the central stakeholder whose autonomy and wellbeing both matter, and whose stated wish (to go) may conflict with his apparent state (he looks tired);
* the daughter and the son as two distinct stakeholders with opposing preferences (rest at home vs. go to the gathering) — a mixed-motive family disagreement, not a single robot-vs-human choice;
* plausibly the man's doctor or care plan as a background source the robot could consult for the health facts it does not have;
* robot actions spanning at least: gather information (his current condition, any medical guidance), ask the man about his own wishes and how he feels, facilitate or mediate between daughter and son, support a compromise (e.g. a short or assisted visit), and advise / defer;
* consequences that trade off the man's autonomy (his right to decide about his own life) against his health and safety, and that recognise taking either sibling's side carries a social cost;
* a few steps of interaction (find out more → help the parties decide → act and monitor), not a single one-shot choice.

A good model should NOT include:

* deciding for the man by fiat without consulting him or gathering the health facts;
* inventing medical specifics — his diagnosis, exact risk level, medications — or the doctor's actual orders;
* inventing names, the nature of the gathering, or family backstory;
* collapsing the daughter and son into one "the family" agent, or assuming one of them is simply right;
* a story.
