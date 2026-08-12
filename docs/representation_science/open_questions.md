# Open Questions

## Purpose

This file collects unresolved questions that should guide future work on explicit world models, representation refinement, and metric invariance.

## Repository Evidence

The notebook code currently answers some mechanical questions:

- whether a model parses as JSON;
- whether required top-level schema fields are present;
- whether states, actions, transitions, probabilities, rewards, terminality, and reachability are mechanically coherent;
- whether an exact candidate structurally matches a reference up to renaming, after conversion to the `game_matching` format.

The notebook code does not answer the questions below.

## Literature

The literature suggests many relevant distinctions: abstraction versus refinement, exact equivalence versus approximate distance, state abstraction versus action abstraction, structural graph similarity versus semantic equivalence, and metric invariance versus metric sensitivity.

## Inference

The core open problem is not only "how should a world model be represented?" It is also "which differences between two representations should matter for evaluation?"

## Open Questions

### Repository Questions

- Are the Level 1-4 fixtures intended as permanent benchmark cases, debugging fixtures, or pedagogical examples?
- Should the benchmark continue using notebooks as the primary executable artifact, or should later work extract validator/scorer code into importable modules?
- Should the earlier and expanded notebooks remain parallel artifacts, or should one become canonical?
- Should the exact fixture set include executable stochastic examples beyond deterministic Levels 1-4?
- Should the game and situation-only cases receive executable reference objects, checklist-only annotations, or equivalence-class annotations?
- Should terminality mean world termination, task completion, or evaluation horizon?
- Should the schema continue treating only active decision-makers as `players`?
- Should non-acting stakeholders become first-class objects?
- Should the validator handle arbitrary malformed nested JSON defensively, or is it enough to validate near-schema outputs?
- Should the `+`-joined joint-action convention remain part of the public schema?
- Should the `game_matching` conversion be considered part of the official evaluation pipeline or an experimental adapter?

### Literature Questions

- Which abstraction/refinement literature most directly fits language-induced explicit world models?
- Is CEGAR a useful theoretical analogue for metric-guided representation refinement, or does it rely too heavily on formal property checking?
- Can MDP bisimulation handle explicit world models when rewards are absent or optional?
- Can MDP homomorphisms represent action decomposition and state splitting in the current schema?
- Can graph coarsening metrics handle action labels and transition probabilities, or are they too graph-generic?
- Can node-splitting invariant metrics be adapted to state-transition graphs with action-conditioned edges?
- Can causal abstraction apply if transitions are possibilities rather than explicit causal mechanisms?
- Which ontology-quality dimensions transfer cleanly to generated world models?
- Which knowledge graph quality metrics are meaningful without a closed set of true facts?
- Which benchmark-validity methods should be used before making capability claims about representation quality?

### Representation Questions

- When should refinement change evaluation?
- When should refinement leave evaluation unchanged?
- Which refinements add information?
- Which refinements merely increase complexity?
- When are two representations equivalent?
- What should metrics ignore?
- What should metrics never ignore?
- How should uncertainty affect granularity?
- How should epistemic uncertainty differ from stochastic transition uncertainty?
- When does adding a stakeholder improve adequacy, and when is it unsupported invention?
- When does adding an institution improve adequacy, and when does it overfit the scene?
- Can a representation be adequate without explicit beliefs?
- Can a representation be adequate without explicit goals?
- What is the boundary between world modeling and policy recommendation?
- Should a model represent values as rewards, annotations, constraints, or something else?
- How should evidence provenance be represented without bloating the schema?
- Should objects and state variables be factored, or is enumerated state text sufficient for the benchmark's goals?
- How should long-horizon consequences be bounded?

### Evaluation Questions

- What should count as a reference for open-ended situation prompts?
- Should open cases be evaluated against multiple acceptable representations rather than one target?
- How should coverage and precision be computed when the reference is an ingredient checklist?
- How should a metric distinguish unsupported invention from useful commonsense inference?
- How should a metric distinguish harmless state splitting from meaningful uncertainty preservation?
- How should a metric distinguish harmful state merging from useful abstraction?
- Should structural matching be weighted by decision relevance?
- Should all states/actions count equally?
- Should stakeholder omissions be weighted more heavily than naming or horizon differences?
- Should uncertainty collapse be a separate failure category?
- Should metrics be evaluated for sensitivity and specificity using controlled perturbations?
- What perturbation suite would test metric invariance?
- What constitutes stabilization across refinement levels?
- Should stabilization be measured per scenario, per quality dimension, or across the full benchmark?
- Can metric stabilization hide systematic blind spots?
- What human-review protocol can validate whether a refinement is meaningful?
- How should inter-rater disagreement be handled when multiple representations are valid?

## Speculation

Future work may need an explicit transformation test suite:

- renaming transformations that should not change score;
- state-splitting transformations that may or may not change score depending on semantic content;
- state-merging transformations that test loss of relevant distinctions;
- action-decomposition transformations;
- horizon-extension transformations;
- stakeholder-addition and stakeholder-removal transformations;
- uncertainty-collapse and uncertainty-preservation transformations;
- unsupported-invention transformations.

Such a suite would make metric invariance testable rather than rhetorical.
