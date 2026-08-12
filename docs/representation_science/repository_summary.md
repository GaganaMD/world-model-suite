# Repository Summary

## Scope

This file summarizes only repository-supported observations from the notebook code and executable fixtures. It does not treat external literature or prior prose docs as evidence for repository behavior.

## Repository Evidence

### Current repository shape

The repository is compact. The code-bearing artifacts are two notebooks:

- `notebooks/Copy_of_Test_Cases (1).ipynb`
- `notebooks/Copy_of_Test_Cases.ipynb`

The expanded notebook has 134 cells. Its executable code includes Lane 1 validation, Lane 2 conversion and scoring, exact expected model fixtures, a Lane 2 demonstration, and a Lane 1 negative-test appendix.

The earlier notebook has the same Lane 1 validator and ten exact expected fixtures, but lacks the Lane 2 `game_matching` setup, converter, scoring wrapper, and demo cells.

### Current explicit representation

The executable fixtures use a JSON-style representation with these top-level fields:

- `players`: non-empty list of player records, each with an `id`;
- `initial_state`: state identifier;
- `states`: dictionary keyed by state identifier, where each state must contain a boolean `terminal` field;
- `actions`: dictionary keyed by state, then player, listing available actions;
- `transition_probabilities`: dictionary keyed by state and action profile, mapping successor states to probabilities;
- `rewards`: optional dictionary keyed by state and action profile, mapping active players to numeric rewards.

Joint actions are encoded as strings by joining the active players' actions with `+` in player-list order. If only one player is active, the transition key is the bare action name. The validator treats `+` as a reserved separator and rejects action names containing it.

### Current benchmark fixtures in code

The expanded executable fixtures define ten exact expected models:

| Fixture | Players | States | Non-terminal states | Flat transition keys | Reward entries |
|---|---:|---:|---:|---:|---:|
| `expected_1_1` | 1 | 4 | 1 | 4 | 0 |
| `expected_1_2` | 1 | 5 | 1 | 5 | 0 |
| `expected_2_1` | 1 | 7 | 6 | 27 | 0 |
| `expected_2_2` | 1 | 10 | 7 | 32 | 0 |
| `expected_3_1` | 1 | 6 | 4 | 16 | 0 |
| `expected_3_2` | 1 | 5 | 4 | 19 | 0 |
| `expected_4_1` | 2 | 4 | 1 | 4 | 4 |
| `expected_4_2` | 2 | 5 | 1 | 4 | 4 |
| `expected_4_3` | 2 | 6 | 1 | 6 | 6 |
| `expected_4_4` | 2 | 9 | 8 | 24 | 24 |

The stored notebook output records that all ten expected fixtures pass Lane 1 with zero failures and zero warnings.

### Lane 1 evaluation

Lane 1 contains a parse gate, schema checks, and mechanical checks.

The parse gate accepts a Python dictionary directly or parses a raw JSON string. JSON parse failures are returned as Category 1 findings.

The schema checks require:

- required top-level keys;
- non-empty `players`;
- player `id` fields;
- no duplicate player ids;
- non-empty `states`;
- boolean `terminal` field on each state;
- dictionary-valued `actions`;
- dictionary-valued `transition_probabilities`.

The mechanical checks validate:

- the initial state is declared;
- action tables reference declared states and players;
- action lists are non-empty lists;
- action names are unique for a player in a state;
- action names do not contain `+`;
- terminal states have no outgoing actions or transitions;
- non-terminal states have both actions and transitions;
- transition keys match exactly the declared action or joint-action profiles;
- successor maps are non-empty dictionaries;
- successor states are declared;
- probabilities are numeric, in `[0, 1]`, and sum to 1 within tolerance;
- optional rewards reference declared states, declared transition keys, and declared players;
- all states are reachable from `initial_state`;
- at least one terminal state is reachable, reported as a warning if absent.

Lane 1 returns a `PASS` or `FAIL`, findings, 0/1 subscores, and `min_score`, where the minimum subscore is the overall mechanical score.

The self-test mutates known-good fixtures in 17 ways and the stored notebook output reports `17/17 caught`.

### Lane 2 evaluation

The expanded notebook adds a Lane 2 adapter and scoring wrapper around Jobst's `game_matching` repository.

The adapter converts the repository schema to a game-matching schema:

- player records become a player id list;
- `initial_state` becomes `root`;
- state terminality becomes terminal states with payoffs;
- action tables become per-state action profiles;
- flat joint-action keys become explicit `{player: action}` profiles.

Two conversion assumptions are introduced:

- cyclic models are unrolled to a finite horizon because the matching loader expects an acyclic graph;
- terminal payoffs default to `0.0` for all players when the repository model lacks payoff data.

The Lane 2 wrapper computes:

- `coverage = score(reference, candidate) / score(reference, reference)`;
- `precision = score(reference, candidate) / score(candidate, candidate)`;
- `lane2` as the harmonic mean of coverage and precision.

The stored demo output on TC 1.1 shows:

- renamed but structurally equivalent model: Lane 2 score 1.000;
- missing action variant: Lane 2 score 0.302;
- invented extra content variant: Lane 2 score 0.320.

### What is evaluated today

The executable code evaluates:

- syntactic parseability as JSON;
- schema conformity;
- internal graph/action/probability/reward consistency;
- reachability;
- structural similarity to an exact reference up to renaming;
- omission and invention indirectly through Lane 2 coverage and precision.

### Current assumptions

The code assumes:

- finite discrete states;
- closed-world declaration of states, actions, and transitions;
- state-dependent action availability;
- active players are exactly those with action lists at a state;
- joint actions are the Cartesian product of active players' action lists;
- joint keys are encoded with `+`;
- terminal states end the modeled episode;
- transition probabilities represent successor distributions;
- rewards, when present, are indexed by state/action profile;
- structural similarity can be evaluated after finite-horizon unrolling;
- default terminal payoffs are acceptable for structure-only comparison.

## Literature

No literature claim is needed to describe the repository code. External work becomes relevant when asking whether the current metrics should be invariant under abstraction, refinement, graph coarsening, or semantic equivalence.

## Inference

The executable representation is closest to a compact explicit stochastic game or Markov game schema. It is explicit and inspectable, but it forces all modeled distinctions into finite states, state-indexed actions, and transition tables.

Lane 1 is a validity gate, not an adequacy evaluator. A model can pass Lane 1 while omitting an important stakeholder, collapsing uncertainty, or inventing unsupported details, as long as the resulting JSON is mechanically coherent.

Lane 2 handles renaming invariance. It does not yet establish invariance under state splitting, state merging, adding intermediate states, changing horizon, changing reward placement, or replacing flat state names with factorized state variables.

The fixed-horizon unrolling used for Lane 2 makes structural comparison tractable but makes horizon choice part of the metric. That matters for any future claim about refinement stability.

## Speculation

The code already contains the seed of a representation-quality program: validity, coverage, and precision are separated. A future research layer could ask which representation refinements preserve these scores for principled reasons and which refinements expose genuine omissions.

## Open Questions

- Should Lane 1 be a strict evaluator for arbitrary malformed model outputs, or only for outputs that approximately follow the expected schema?
- Should rewards be attached to state/action profiles, successor states, or `(state, action, next_state)` triples?
- What should terminality mean: world termination, evaluation boundary, or horizon cutoff?
- Should state variables, objects, observations, beliefs, and stakeholders become first-class fields?
- How should Lane 2 behave when a candidate splits one reference state into multiple semantically meaningful substates?
- How should Lane 2 behave when a candidate merges reference states that differ only in irrelevant detail?
- What invariances should hold for open-ended situation cases with no single canonical JSON?

