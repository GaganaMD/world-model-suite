# Future Directions

## Purpose

This file summarizes possible research directions that build on the current repository without modifying production code, the benchmark, or the evaluation pipeline.

## Repository Evidence

The current notebook code provides:

- exact finite state-transition fixtures;
- a mechanical validity gate;
- structural matching up to renaming;
- coverage and precision as separate structural scores;
- visible assumptions introduced by finite-horizon unrolling and default terminal payoffs.

These are enough to design research experiments around representation quality and metric invariance, even before changing the evaluator.

## Literature

The relevant literature does not suggest that metric-guided refinement is a wholly new idea. Related formulations exist in:

- abstraction refinement and CEGAR;
- MDP model minimization and state abstraction;
- bisimulation and simulation relations;
- graph coarsening and node-splitting invariant metrics;
- ontology evolution and ontology quality;
- causal abstraction;
- benchmark construct validity and measurement invariance.

## Inference

The repository's strongest research direction is not a new benchmark taxonomy. It is the study of when explicit world-model representations of the same situation should be judged equivalent, better, worse, or incomparable.

## Representation Refinement

Possible direction: define a catalog of refinement transformations for explicit world models.

Candidate transformations:

- state splitting;
- state merging;
- action decomposition;
- action aggregation;
- horizon extension;
- stakeholder addition;
- object/resource factoring;
- uncertainty factoring;
- evidence/provenance labeling;
- reward/value relocation.

Research value: This would make "granularity" concrete enough to test.

Main risk: The transformation list could become arbitrary unless each transformation is tied to repository examples and literature analogues.

## Metric Invariance

Possible direction: specify which metrics should stay stable under which transformations.

Candidate invariance claims:

- renaming should not change structural score;
- harmless state splitting should not reduce adequacy;
- unsupported added branches should reduce precision;
- relevant omitted branches should reduce coverage;
- uncertainty-preserving splits may improve adequacy;
- uncertainty-collapsing merges should reduce adequacy;
- horizon extension should be reported with boundary assumptions.

Research value: This directly develops Jobst's stabilization hypothesis.

Main risk: Metric stability is not the same as metric validity. A metric can be stable because it ignores important information.

## Representation Quality

Possible direction: develop a quality model for generated explicit world models.

Candidate dimensions:

- mechanical validity;
- structural coverage;
- structural precision;
- semantic support;
- stakeholder adequacy;
- uncertainty preservation;
- institutional/normative adequacy;
- decision-relative sufficiency;
- conciseness;
- provenance clarity.

Research value: This connects code-level evaluator behavior to the richer needs of open situations.

Main risk: Too many dimensions may reduce reliability and make evaluation harder to interpret.

## Granularity

Possible direction: study coarse-to-fine representation sequences.

Possible experiment:

1. Start with a deliberately coarse model for a scenario.
2. Add one refinement at a time.
3. Recompute available metrics.
4. Ask expert reviewers whether each refinement changed adequacy.
5. Compare metric stabilization against expert stabilization.

Research value: This directly tests whether metrics can guide the choice of representation granularity.

Main risk: The result may depend heavily on the scenario and selected metric.

## Explicit World Models

Possible direction: clarify what makes this project different from latent world-model evaluation.

Candidate framing:

- explicit world models expose states, actions, transitions, and assumptions;
- errors can be localized to modeled components;
- representation quality can be evaluated before policy selection;
- underspecified language often admits multiple valid formalizations.

Research value: This can position the work relative to Text2World and world-model benchmark surveys.

Main risk: The project should avoid overclaiming novelty for world-model benchmarking as a whole.

## AI Safety

Possible direction: connect representation omissions and inventions to safety-relevant failures.

Examples:

- missing a vulnerable stakeholder;
- treating a claim as verified fact;
- omitting information-gathering actions;
- inventing authority to physically intervene;
- collapsing competing legitimate claims into one "correct" choice.

Research value: Explicit representations may make safety-relevant failures inspectable before deployment.

Main risk: Safety claims require careful evidence. The repository currently supports diagnostic examples, not deployed-system conclusions.

## Decision Support

Possible direction: evaluate whether the representation preserves distinctions needed for downstream decisions without evaluating the policy itself.

Research value: This respects the repository's separation between possible actions/consequences and actual behavior choice.

Main risk: Decision relevance may require specifying goals or values that the current schema omits.

## Potential Experiments

- Renaming invariance: verify that score remains stable under pure relabeling across all exact fixtures.
- State-splitting test: split a state into two behaviorally identical substates and observe Lane 2 behavior.
- State-merging test: merge states that differ in a precondition and confirm the metric changes.
- Horizon-sensitivity test: rerun Lane 2 with different unrolling horizons.
- Reward-sensitivity test: compare structurally identical models with different reward placements.
- Uncertainty-preservation test: compare models that keep versus collapse live hypotheses.
- Stakeholder-coverage test: compare open-situation models with and without non-acting stakeholders.
- Human-equivalence test: collect expert judgments on paired representations.

## Potential Publication Venues

Candidate venue families:

- AI evaluation and benchmarking workshops;
- knowledge representation and reasoning venues;
- AI safety workshops focused on world models, oversight, or decision support;
- reinforcement learning workshops on abstraction and representation;
- planning workshops on abstraction and model quality;
- graph learning or network-science workshops if the metric-invariance angle becomes central.

Specific venue selection should wait until experiments clarify whether the main contribution is evaluation methodology, formal equivalence, or empirical benchmark analysis.

## Potential Collaborators

The current repository evidence identifies Jobst's `game_matching` contribution as central to Lane 2. Future work would benefit from collaborators with expertise in:

- formal methods and refinement;
- reinforcement-learning abstraction;
- graph similarity and coarsening;
- knowledge representation and ontology quality;
- human annotation and psychometrics;
- AI safety and decision-support evaluation;
- domain experts for open social, safety, and institutional scenarios.

## Speculation

A future paper could be organized around this claim:

> Explicit world-model evaluation should move beyond graph identity. It should characterize which representation refinements preserve, improve, or degrade task-relevant adequacy, and it should test whether metrics stabilize at an appropriate granularity.

That claim still needs empirical support.

## Open Questions

- Which future direction should be prioritized first: invariance tests, semantic adequacy annotations, or ontology refinement?
- Can the current benchmark support the first experiment without adding new scenarios?
- How much expert annotation is needed to validate "meaningful refinement" judgments?
- Which metrics are worth testing for stabilization?
- What evidence would falsify the metric-guided granularity hypothesis?

