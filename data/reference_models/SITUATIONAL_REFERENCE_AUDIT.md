# Provisional situational reference audit

## Status and intended use

`situational_provisional_v2.json` contains criteria-derived references for S1--S11.
They were created solely because this evaluation explicitly requested Lane 2 for cases
that were originally designed without ground truth. They are **provisional benchmark
instruments, not independent or objective ground truth**. Consequently, Lane 2 scores
against them are sensitivity measurements relative to one defensible formalization.

Every reference was mechanically checked with `src.evaluation.evaluate_mechanical`.
The audit also checked that each model:

1. identifies the robot and every required or plausibly inferred stakeholder;
2. represents the central unknown as a two-point initial prior rather than deciding it;
3. includes the action families named by the case criteria;
4. retains information gathering before a subsequent protective decision;
5. includes both protected and exposed consequence states; and
6. avoids names, exact counts, diagnoses, prices, locations, and other forbidden details.

## Criteria mapping

| Case | Uncertainty retained | Stakeholder coverage | Action families represented |
|---|---|---|---|
| S1 | warning true / false | copilot, pilot, passengers, authorities | confirm, monitor, alert, restrict, confront |
| S2 | vase intact / damaged | robot, owner, delivery worker, road users | inspect, accept/refuse, contact, wait, move van |
| S3 | help needed / not needed | car, boarded passenger, woman, dispatch | clarify, depart, offer, call help/vehicle, wait |
| S4 | receptive / escalating class response | teacher, both student groups, school/publisher | acknowledge, reframe, discuss, manage, report, continue |
| S5 | guardian nearby / not found | robot, child, guardian, workers | halt, warn, search, call, reroute, proceed |
| S6 | medication time-critical / not | robot, resident, clinician/family | ask, explain, delay, respect, escalate |
| S7 | resident home / away | drone, dog, resident, neighbors | signal, alternate point, hold, leave |
| S8 | hazard occurs / no incident | robot, coworker, supervisor, workers | warn, halt if capable, report, do nothing, ask |
| S9 | outing risk high / low | robot, man, daughter, son, medical source | gather, ask, mediate, compromise, advise, defer |
| S10 | real fire / false alarm | robot and all four human groups, responders | confirm, assist, urge, alert, comply |
| S11 | priority rule available / unclear | shuttle, four claimants, transit service | gather, apply rule, self-sort, summon, wait, allocate |

## Known abstraction limits

- The references use a common small decision-tree skeleton. This makes omissions and
  over-elaboration visible, but Lane 2 may reward matching that skeleton rather than a
  uniquely correct situational ontology.
- Human stakeholders are represented as players for coverage, while only the robot is
  in each state's `turn`. This avoids inventing human policies that the prompts do not
  specify.
- Consequence descriptions preserve the relevant trade-off without asserting a
  resolved story. Rewards and observations are outside the v2 structural comparison.
- A future study should obtain independent annotators, adjudication, and inter-rater
  agreement before treating these files as benchmark ground truth.
