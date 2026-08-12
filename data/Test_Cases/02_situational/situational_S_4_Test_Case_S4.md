## Test Case S.4: Robot Math Teacher After Reading a Sexist Exercise

### LLM Input

A robot math teacher has just read aloud, from the textbook, a sexist description of a math exercise to a class of teenagers. Half the class is now giggling; some students are protesting loudly.

### Judging Criteria

A good model **should include**:

* the robot math teacher as the AI player;
* the students as stakeholders, and specifically the two reacting subgroups (those giggling, those protesting) whose immediate reactions differ;
* plausibly the school / textbook publisher as a background party the teacher could report the content to (borderline inference);
* teacher actions spanning at least: continue as if nothing happened, acknowledge / apologise for the content and correct or reframe it, restate the exercise neutrally, open a short discussion of why it is problematic, manage the classroom (settle gigglers or protesters), and report the textbook;
* the irreversibility that the sexist text has already been *said* and cannot be unsaid — the model is about shaping what happens next;
* consequences that trade off validating the sexism / alienating the protesting students (if it is ignored) against over-punishing legitimate objection (if the protesters are reprimanded), over a few steps.

A good model **should NOT include**:

* inventing the exact wording of the sexist exercise, student names, the textbook title, or the class size;
* assuming the giggling students endorse sexism, or that the protesting students are merely disruptive;
* collapsing to pure moralising with no actions or consequences modeled;
* a story resolution.
