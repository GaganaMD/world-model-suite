# Representation Science Workspace

## Purpose

This workspace collects research notes for explicit world models, with a focus on representation quality, representation refinement, and metric invariance. It is meant to guide later benchmark and evaluation work without changing the current benchmark or evaluation pipeline.

The central working idea is:

> There may not be a universally correct level of granularity for an explicit world model. A coarse representation can be refined progressively, evaluation metrics can be recomputed, and refinement may stop when the relevant metrics stabilize.

This idea is a research hypothesis, not a project claim. The workspace exists to test it against the repository and against adjacent literature.

## Current Research Questions

- What makes an explicit world model adequate rather than merely valid?
- Which representation refinements should change evaluation metrics?
- Which representation refinements should leave evaluation metrics invariant?
- Can metric stabilization guide the choice of representation granularity?
- When are two explicit world models equivalent despite different state/action decompositions?
- How should open-ended situation prompts be evaluated when there is no single canonical JSON target?

## Repository Evidence

The repository currently contains notebook-based benchmark and evaluation code in `notebooks/Copy_of_Test_Cases (1).ipynb` and an earlier notebook variant in `notebooks/Copy_of_Test_Cases.ipynb`.

The executable notebook code defines:

- a JSON-style explicit world model schema with `players`, `initial_state`, `states`, `actions`, `transition_probabilities`, and optional `rewards`;
- Lane 1 mechanical checks for parse, schema, probability, action, transition, reward, terminality, and reachability validity;
- a Lane 2 adapter from the repository schema to Jobst's `game_matching` schema;
- a Lane 2 structural similarity wrapper that reports coverage, precision, and a harmonic mean score;
- ten executable expected models for Levels 1-4;
- a Lane 2 demo on one renamed, one omission, and one invention variant of TC 1.1;
- a 17-mutation self-test for Lane 1.

This pass is intentionally grounded in the notebook code and embedded executable fixtures. Existing prose documents in the repository should be reconciled in a later pass.

## Relationship to Benchmark Design

The workspace treats benchmark cases as diagnostic instruments for representation quality. It does not redesign the benchmark. Instead, it records questions future benchmark work may need to answer: whether scenarios isolate specific representational demands, whether exact references are appropriate, and whether open-ended cases need equivalence-class or checklist-style references.

## Relationship to Evaluation

The workspace treats Lane 1 and Lane 2 as the current executable baseline. Lane 1 establishes mechanical validity. Lane 2 establishes structural comparison up to renaming. The research problem is what evaluation should do beyond those baselines, especially under refinement, abstraction, state splitting, horizon changes, and semantic equivalence.

## Relationship to Explicit World Models

The workspace focuses on explicit, inspectable possibility models: finite states, available actions, transition probabilities, terminality, and optional rewards. It intentionally separates this object from policy evaluation, latent world-model prediction, and narrative story completion.

## Literature

The workspace surveys adjacent work from:

- formal methods: abstraction, refinement, simulation, bisimulation, predicate abstraction, and counterexample-guided abstraction refinement;
- reinforcement learning and planning: state abstraction, MDP homomorphisms, bisimulation metrics, hierarchy, and abstraction heuristics;
- graph methods: graph isomorphism, graph coarsening, graph refinement, and node-splitting invariant metrics;
- knowledge representation: ontology quality, ontology evolution, knowledge graph quality, and semantic equivalence;
- causal modeling: causal abstraction and transformations between structural causal models;
- AI evaluation: benchmark construct validity, capability demand scales, and world-model benchmark taxonomies.

## Inference

The repository is already organized around a layered distinction:

- validity: whether a model can be parsed and traversed mechanically;
- structural fidelity: whether it preserves a reference transition structure up to renaming;
- semantic adequacy: whether it includes justified entities, actions, uncertainties, and consequences;
- decision relevance: whether the representation keeps the distinctions needed for downstream reasoning.

Only the first two layers are executable in the current notebook code. The later layers are research targets.

## Speculation

The stabilization hypothesis suggests that representation granularity may be chosen operationally rather than declared in advance. If a refinement does not materially change coverage, precision, uncertainty preservation, value-relevant distinctions, or downstream decisions, it may be unnecessary for the benchmark's purpose.

This does not mean all stable metrics are valid. A bad metric can stabilize on a bad abstraction. Stability should be studied alongside sensitivity, construct validity, and expert judgment.

## Open Questions

- Which metric changes should count as evidence that a refinement added meaningful information?
- Which refinements should evaluation ignore as representational variants?
- Can Lane 2 structural matching be extended beyond renaming to state splitting, state merging, horizon extension, and abstraction/refinement equivalence?
- How should open-ended semantic criteria be validated against multiple expert representations?
- How should uncertainty, stakeholder status, institutional authority, and norms be represented without turning the model into a policy?

## Roadmap

1. Ground the current repository: `repository_summary.md` and `representation_quality_notes.md`.
2. Establish reusable scenario analysis practice: `representation_canvas.md`.
3. Map granularity and invariance concepts across literatures: `terminology_mapping.md`.
4. Survey refinement, abstraction, and invariance theory: `representation_invariance_survey.md` and `literature_review.md`.
5. Track unanswered research problems: `open_questions.md`.
6. Record evolving hypotheses and next experiments: `research_journal.md` and `future_directions.md`.

## Files

- `repository_summary.md`: code-supported summary of the current repository representation and evaluation.
- `representation_canvas.md`: reusable template for analyzing future scenarios.
- `representation_quality_notes.md`: evidence, inferences, and questions about representation quality.
- `representation_invariance_survey.md`: main survey of refinement, abstraction, equivalence, and invariance.
- `granularity_notes.md`: notes on coarse and fine representations without proposing solutions.
- `terminology_mapping.md`: cross-field vocabulary map.
- `literature_review.md`: theme-organized paper notes.
- `open_questions.md`: research questions grouped by repository, literature, representation, and evaluation.
- `research_journal.md`: dated research log.
- `future_directions.md`: possible research directions, experiments, venues, and collaborators.
