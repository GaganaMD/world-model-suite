# Cultural Track Evaluation (04_cultural, C1-C14)

## Experiment

This is the cultural counterpart of the game-track EDA report. The case bank is
loaded from `data/Test_Cases/04_cultural`; every case is an open situation judged by
expect/avoid criteria, so there is no canonical reference model and a Lane-2
reference comparison is N/A by design. Candidates are instead run through:

- **Lane 0** - strict JSON parse of the raw reply;
- **Lane 1** - the repository's mechanical checks (`json_generation/lane1.check_v2`)
  after normalizing v2 / declarative / rollout inputs to the v2 schema;
- **Cross-case structural EDA** - `WorldModelEDA` descriptors as for G1-G9;
- **Lane 3** - expect/avoid checklist scoring against each case's parsed criteria
  (coverage of expected ingredients with evidence, flags on forbidden content).

## Case bank

| Case | Country | Title | Expected | Forbidden |
| --- | --- | --- | ---: | ---: |
| C1 | Korea | office robot and a junior employee's correct but unwelcome point | 6 | 4 |
| C2 | China | business robot deciding who to introduce first at a negotiation | 5 | 4 |
| C3 | France | school robot and a student's religious dress in class | 6 | 4 |
| C4 | India | delivery robot and a residential society's entry restriction | 6 | 4 |
| C5 | Japan | office robot and a gift brought by a visiting client | 6 | 4 |
| C6 | Brazil | household robot asked to shorten a family gathering | 6 | 4 |
| C7 | Nigeria | community robot and an elder's disputed land boundary claim | 7 | 4 |
| C8 | Germany | conference robot and a late-arriving speaker | 7 | 4 |
| C9 | Saudi Arabia | hospitality robot and a mixed-group seating request | 8 | 4 |
| C10 | Mexico | event robot and a quinceañera speech conflict | 7 | 4 |
| C11 | Egypt | navigation robot and a prayer-time interruption | 7 | 4 |
| C12 | Russia | warehouse robot and an informal supervisor override | 7 | 4 |
| C13 | USA | hr robot and an anonymous workplace complaint | 8 | 4 |
| C14 | Indonesia | village robot and a divided community vote | 7 | 4 |

## Lane results

| Case | Model | Sample | Schema | Lane 0 | Lane 1 | Fails | Warns | Coverage | Avoidance | Lane 3 |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| C1 | demo | good_v2 | v2 | PASS | PASS | 0 | 2 | 0.92 | 1.00 | 0.96 |
| C5 | demo | weak_v2 | v2 | PASS | PASS | 0 | 1 | 0.50 | 0.75 | 0.61 |
| C9 | demo | declarative_v1 | v1 | PASS | PASS | 0 | 2 | 1.00 | 1.00 | 1.00 |
| C11 | demo | fenced_broken | - | FAIL | - | - | - | - | - | - |

### Cross-case structural results

| Case and title | States | Terminal | Joint actions | Avg. branch | Stochastic | Avg. entropy (bits) | Max depth | SCCs | Avg. path |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C1 - demo/good_v2 | 8 | 6 | 6 | 0.75 | 17% | 0.167 | 2 | 8 | 1.42 |
| C5 - demo/weak_v2 | 3 | 2 | 2 | 0.67 | 0% | 0.000 | 1 | 3 | 1.00 |
| C9 - demo/declarative_v1 | 5 | 4 | 4 | 0.80 | 0% | 0.000 | 1 | 5 | 1.00 |
| C11 - demo/fenced_broken | - | - | - | - | - | - | - | - | - |

## Per-case checklists

### C1 - demo/good_v2

Lane 1 **PASS** (0 fail / 2 warn), coverage 0.92, avoidance 1.00, lane3 0.96.

- Lane 1: `[WARN] (Cat3) G11-idle-player: player 'junior' never appears in any 'turn'`
- Lane 1: `[WARN] (Cat3) G11-idle-player: player 'senior_manager' never appears in any 'turn'`

Expected ingredients:

- [ok]  the robot as the AI player <- structural: robot-type player present
- [ok]  the junior employee as a stakeholder whose factual correction has standing regardless of tenure <- inexperienc, colleag, factual, accura
- [ok]  the senior manager as a stakeholder whose seniority is a social fact in the scene, not a determinant of factual correctness <- elder, boss, social, fact, factual, accura
- [ok]  actions spanning: verify the claim, correct with or without attribution, leave it as stated, or flag it to the manager <- confirm, accura, anonym, stat, flag, boss
- [ok]  verification of the underlying fact treated as separate from, and prior to, any decision about how to handle hierarchy/face <- confirm, underly, fact, separate, hierarchy, courtes
- [~]   the real workplace norm around seniority acknowledged as a live consideration (e.g. attribution, how directly to flag it) without being used to override factual accuracy <- elder, anonym, flag, bypass, factual

Forbidden content flags (suspected - human review):

- none flagged.

### C5 - demo/weak_v2

Lane 1 **PASS** (0 fail / 1 warn), coverage 0.50, avoidance 0.75, lane3 0.61.

- Lane 1: `[WARN] (Cat3) G11-idle-player: player 'client' never appears in any 'turn'`

Expected ingredients:

- [ok]  the robot as the AI player <- structural: robot-type player present
- [~]   the visiting client as a stakeholder whose gesture carries relational meaning <- visit, client
- [ok]  the team (or its representative) as a stakeholder whose response to the gift matters <- team, gift
- [  ] actions spanning: accept on behalf of the team and set aside for later opening, thank the client and pass immediately to a human colleague, ask a clarifying question about the gift, or open it in front of the client
- [  ] the Japanese norm of *not* opening gifts immediately in the giver's presence acknowledged as a live, legitimate convention — not framed as overly formal or outdated
- [~]   uncertainty about whether the client expects immediate acknowledgment or is comfortable with deferred opening held genuinely open <- ambiguit, client, immediate, open

Forbidden content flags (suspected - human review):

- FLAG: resolved-narrative marker (the model settles the scenario instead of modelling it) (matched: `correctly`) -> a resolved narrative ("the robot correctly opened the gift later")

### C9 - demo/declarative_v1

Lane 1 **PASS** (0 fail / 2 warn), coverage 1.00, avoidance 1.00, lane3 1.00.
- note: converted from declarative game-case schema

- Lane 1: `[WARN] (Cat3) G11-idle-player: player 'host_company' never appears in any 'turn'`
- Lane 1: `[WARN] (Cat3) G11-idle-player: player 'venue_staff' never appears in any 'turn'`

Expected ingredients:

- [ok]  the robot as the AI player <- structural: robot-type player present
- [ok]  the host company as a stakeholder with an explicit, stated preference for the event <- host, company, stat, preference
- [ok]  the venue and its staff as stakeholders with an institutional policy and local standing <- venue, staff, law, local
- [ok]  the event attendees as stakeholders whose comfort and preferences are relevant but not yet known <- attende, comfort, preferenc, known
- [ok]  actions spanning: follow the host's request, follow the venue's policy, surface the conflict to a human decision-maker from either party, or ask both parties to clarify and resolve the conflict directly <- follow, host', request, venue', law, surface, conflict, human, ask
- [ok]  the venue's policy acknowledged as a real local convention — not automatically framed as improper <- venue', law, real, local, convention
- [ok]  the host's request acknowledged as legitimate without being treated as automatically overriding the venue's policy <- host', request, venue', law
- [ok]  the conflict surfaced as a genuine authority ambiguity requiring human resolution, not robot judgment <- conflict, surfac, authorit, ambiguity, human

Forbidden content flags (suspected - human review):

- none flagged.

### C11 - demo/fenced_broken

**Lane 0 failed.**

- `FAIL: reply is not valid JSON: Expecting value: line 1 column 1 (char 0); reply is wrapped in a code fence (try --lenient)`

