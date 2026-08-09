# Literature Review

## Purpose

This review organizes literature by theme rather than chronology. Each entry is written for relevance to explicit world models, representation refinement, and metric invariance.

## Repository Evidence

The repository code represents explicit world models as finite state/action/transition structures with optional rewards. Lane 1 evaluates mechanical validity. Lane 2 evaluates structural similarity to exact references up to renaming and reports coverage, precision, and a harmonic mean.

The code does not yet implement abstraction/refinement equivalence, ontology quality evaluation, causal abstraction, or metric-stability tests.

## Literature

### Explicit World Models and World-Model Benchmarks

#### Text2World: Benchmarking Large Language Models for Symbolic World Model Generation

Link: https://arxiv.org/abs/2502.13092

Summary: Text2World studies generation of symbolic world models from natural language, with a focus on whether language models can produce structured representations suitable for planning-like tasks.

Main contribution: It frames world-model generation as a symbolic construction task rather than only as latent prediction or video generation.

Connection to explicit world models: It is close to this repository's object: a language prompt is converted into an explicit model of entities, states, actions, and effects.

Potential relevance: Useful for situating this project among language-to-world-model benchmarks and for comparing representation output formats.

Potential limitations: Its evaluation choices may not directly address metric invariance under refinement or open-ended social/normative adequacy.

#### A Survey of World Model Benchmarks

Link: https://world-model-benchmarks.github.io/

Summary: The survey organizes world-model benchmarks by target, protocol, metric level, and data source.

Main contribution: It clarifies that "world-model evaluation" spans many targets, including prediction quality, state consistency, physical plausibility, interactive dynamics, control fidelity, and downstream utility.

Connection to explicit world models: It provides landscape context but most covered benchmarks concern learned, latent, visual, embodied, or control-oriented models rather than inspectable symbolic transition systems.

Potential relevance: Useful for preventing overclaiming. The repository should specify its evaluation target precisely: explicit representation quality.

Potential limitations: It does not appear to solve the problem of multiple valid symbolic granularities for underspecified text.

#### World Models by Ha and Schmidhuber

Link: https://arxiv.org/abs/1803.10122

Summary: This work popularized "world models" as learned latent dynamics models used by agents.

Main contribution: It showed that compact learned latent representations can support control.

Connection to explicit world models: It is mostly a contrast case. The repository evaluates externalized, inspectable models, not latent dynamics.

Potential relevance: Useful for explaining why explicitness changes evaluation: errors can be localized to states, actions, or transitions.

Potential limitations: It does not address symbolic representation adequacy, stakeholder coverage, or metric invariance under refinement.

### Benchmark and Evaluation Science

#### AIBench Scenario: Scenario-distilling AI Benchmarking

Link: https://arxiv.org/abs/2005.03459

Summary: AIBench derives benchmark scenarios from real AI application workflows by distilling essential task dependencies.

Main contribution: It treats a benchmark scenario as a purposeful abstraction whose fidelity should be validated against real systems.

Connection to explicit world models: This is relevant to scenario selection and abstraction. A world-model benchmark scenario also removes detail and must justify what it preserves.

Potential relevance: Helps frame benchmark cases as abstractions rather than miniature realities.

Potential limitations: It focuses on systems benchmarking, not evaluating model-generated symbolic representations.

#### General Scales Unlock AI Evaluation with Explanatory and Predictive Power

Link: https://www.nature.com/articles/s41586-026-10303-2

Summary: This work develops general demand scales for benchmark items and studies explanatory/predictive links between item demands and model performance.

Main contribution: It gives a construct-validity-oriented methodology for describing benchmark items by anchored demands.

Connection to explicit world models: It can help separate scenario difficulty from representation quality failure.

Potential relevance: Useful for future item-level annotation of demands such as uncertainty, multi-agent structure, institutional reasoning, and abstraction pressure.

Potential limitations: It evaluates task demands and model ability, not whether a generated explicit representation is adequate.

#### Intelligence Task Ontology

Link: https://arxiv.org/abs/2110.01434

Summary: ITO is a curated ontology and knowledge graph for AI tasks, benchmarks, metrics, and results.

Main contribution: It provides a structured way to organize AI evaluation artifacts.

Connection to explicit world models: It can help represent benchmark metadata, but not the internal adequacy of a generated world model.

Potential relevance: Useful for avoiding reinvention of general benchmark/task metadata.

Potential limitations: It is not an ontology of the represented world inside each model.

### Formal Abstraction, Refinement, and Verification

#### Abstract Interpretation

Link: https://doi.org/10.1145/512950.512973

Summary: Cousot and Cousot introduced a lattice-based theory for approximating program semantics while preserving soundness properties.

Main contribution: It formalized abstraction and concretization as mathematical relations between precise and approximate semantic domains.

Connection to explicit world models: A coarse world model can be seen as an abstraction of a more detailed possible-world structure.

Potential relevance: Provides rigorous language for what an abstraction preserves and what precision is lost.

Potential limitations: The original setting is program analysis, and direct transfer to natural-language world-model evaluation requires defining the semantic domain.

#### Model Checking and Abstraction

Link: https://doi.org/10.1145/174644.174646

Summary: Clarke, Grumberg, and Long studied abstraction as a way to make model checking tractable.

Main contribution: It connects abstract transition systems to preservation of temporal properties.

Connection to explicit world models: The repository's state-transition models are structurally similar to systems checked in formal verification.

Potential relevance: Useful for asking which properties survive coarsening or refinement.

Potential limitations: Formal model checking usually starts from a precise system model, not an underspecified natural-language prompt.

#### Counterexample-Guided Abstraction Refinement

Link: https://doi.org/10.1145/876638.876643

Summary: CEGAR begins with an abstraction, checks it, and refines it when spurious counterexamples reveal that the abstraction was too coarse.

Main contribution: It gives an iterative coarse-to-fine refinement loop.

Connection to explicit world models: It is a close analogue to metric-guided refinement, where failures identify missing distinctions.

Potential relevance: Useful background for Jobst's stabilization direction.

Potential limitations: It depends on formal properties and counterexamples; the repository needs equivalents for semantic omissions and unsupported inventions.

#### The Existence of Refinement Mappings

Link: https://doi.org/10.1016/0304-3975(91)90224-P

Summary: Abadi and Lamport studied mappings showing that one specification implements or refines another.

Main contribution: It formalized refinement mappings between abstract and concrete specifications.

Connection to explicit world models: A future equivalence/refinement test may require mappings from fine states/actions back to coarse ones.

Potential relevance: Useful for defining explicit transformation witnesses.

Potential limitations: It assumes formal specifications rather than language-grounded representations with uncertain semantics.

### Planning and Hierarchical Representation

#### A Theory of Abstraction

Link: https://doi.org/10.1016/0004-3702(92)90021-O

Summary: Giunchiglia and Walsh analyze abstraction in AI problem solving.

Main contribution: It offers a general account of abstraction mappings and their role in reasoning.

Connection to explicit world models: It supports the idea that model granularity is tied to intended reasoning tasks.

Potential relevance: Useful for defining coarse and fine representations without assuming maximal detail is best.

Potential limitations: It is broad and not tailored to generated stochastic-game-like artifacts.

#### Automatically Generating Abstractions for Planning

Link: https://doi.org/10.1016/0004-3702(94)90053-1

Summary: Knoblock studies automatic generation of abstraction hierarchies for planning.

Main contribution: It shows how abstraction can reduce planning complexity while preserving problem-solving utility.

Connection to explicit world models: World-model granularity affects planning-like reasoning over available actions and effects.

Potential relevance: Provides background for hierarchy and goal-relative abstraction.

Potential limitations: Planning abstractions usually assume a known planning problem and goal; the repository often excludes policy/goal selection from the representation.

#### Between MDPs and Semi-MDPs: Options

Link: https://doi.org/10.1016/S0004-3702(99)00052-1

Summary: Sutton, Precup, and Singh formalize temporally extended actions in reinforcement learning.

Main contribution: It gives a framework for action abstraction over multiple time steps.

Connection to explicit world models: Some candidate models may split one high-level action into a sequence of lower-level actions.

Potential relevance: Helps distinguish action refinement from state refinement.

Potential limitations: It is tied to learning and control, while the repository evaluates model construction.

### MDP Abstraction, Homomorphism, and Bisimulation

#### Equivalence Notions and Model Minimization in Markov Decision Processes

Link: https://doi.org/10.1016/S0004-3702(02)00376-4

Summary: Givan, Dean, and Greig examine equivalence relations for MDP states and how they support model minimization.

Main contribution: It connects behavioral equivalence to reducing MDP size.

Connection to explicit world models: It is central for asking when two states can be merged without changing behavior.

Potential relevance: Useful for formalizing model coarsening and equivalence.

Potential limitations: It assumes an MDP with defined rewards/transitions, while the repository sometimes has optional rewards and underspecified semantics.

#### Metrics for Finite Markov Decision Processes

Link: https://www.auai.org/uai2004/proceedings/defs/ferns.htm

Summary: Ferns, Panangaden, and Precup introduce metrics measuring behavioral similarity between MDP states.

Main contribution: It relaxes exact equivalence into graded distance.

Connection to explicit world models: Lane 2 already produces graded structural scores; bisimulation metrics offer a formal analogue for behavior-sensitive distance.

Potential relevance: Could inform metric behavior under approximate refinements.

Potential limitations: It depends on reward and transition semantics, not natural-language support or stakeholder adequacy.

#### Towards a Unified Theory of State Abstraction for MDPs

Link: https://people.cs.umass.edu/~mlittman/papers/li-aaai06.pdf

Summary: Li, Walsh, and Littman compare abstraction types that preserve different aspects of MDP behavior.

Main contribution: It organizes state abstractions by what they preserve, such as Q-values, model structure, rewards, or optimal actions.

Connection to explicit world models: It shows why "same representation" is not one relation; the preserved quantity matters.

Potential relevance: Useful for deciding whether representation metrics should be model-preserving, reward-preserving, or decision-preserving.

Potential limitations: It assumes a defined MDP task and often a value/policy target.

#### MDP and SMDP Homomorphisms

Link: https://people.cs.umass.edu/~barto/courses/cs687/ravindran-barto-homomorphisms.pdf

Summary: Ravindran and Barto study abstraction as homomorphic mappings between decision processes.

Main contribution: It gives algebraic structure to mappings between concrete and abstract processes.

Connection to explicit world models: A refined model may map back to a coarse model through state and action mappings.

Potential relevance: Provides a template for explicit witnesses of abstraction/refinement.

Potential limitations: Requires formal transition and reward structures that may be absent or incomplete in open cases.

### Graph Coarsening and Node-Splitting Invariance

#### Graph Reduction with Spectral and Cut Guarantees

Link: https://jmlr.org/papers/v20/18-680.html

Summary: Loukas studies graph reduction methods with guarantees for preserving spectral and cut properties.

Main contribution: It provides formal guarantees for graph coarsening quality.

Connection to explicit world models: State-transition graphs may be coarsened or expanded, and metrics may need to know which properties are preserved.

Potential relevance: Useful for understanding graph-level preservation.

Potential limitations: Generic graph guarantees do not encode actions, rewards, stakeholders, or natural-language support.

#### Node-Splitting Invariant Network Measures

Link: https://arxiv.org/abs/1101.4757

Summary: Heitzig and collaborators study network measures that remain stable when nodes are split according to sampling or representation choices.

Main contribution: It directly addresses metric dependence on how represented units are partitioned.

Connection to explicit world models: This is a close analogue for state-splitting invariance.

Potential relevance: It can help operationalize "do not penalize harmless refinement."

Potential limitations: World-model state splits can carry semantic content; they are not always sampling artifacts.

### Ontology, Knowledge Representation, and Knowledge Graph Quality

#### OntoClean

Link: https://doi.org/10.1145/503124.503150

Summary: OntoClean uses formal meta-properties to evaluate ontological modeling decisions.

Main contribution: It provides principled criteria for class hierarchy correctness.

Connection to explicit world models: If the project adds stakeholders, norms, institutions, or evidence types, ontology discipline will matter.

Potential relevance: Helps avoid ad hoc schema growth.

Potential limitations: It does not evaluate state-transition dynamics or metric invariance.

#### OntoQA

Link: https://corescholar.libraries.wright.edu/knoesis/460/

Summary: OntoQA proposes metrics for ontology quality analysis.

Main contribution: It brings quantitative evaluation to ontology structure and instance usage.

Connection to explicit world models: Similar quality concerns include completeness, richness, and relation structure.

Potential relevance: Useful as a vocabulary source for representation quality.

Potential limitations: Ontology metrics can reward structural richness even when added detail is not decision-relevant.

#### OQuaRE

Link: https://doi.org/10.1016/j.eswa.2011.06.049

Summary: OQuaRE adapts software quality ideas to ontology evaluation.

Main contribution: It organizes ontology quality into measurable characteristics.

Connection to explicit world models: The schema itself can be evaluated for clarity, consistency, completeness, and maintainability.

Potential relevance: Useful if future work evolves the representation ontology.

Potential limitations: It is a schema/ontology quality framework, not a model-output adequacy metric.

#### Knowledge Graph Refinement

Link: https://doi.org/10.3233/SW-160218

Summary: Paulheim surveys methods for improving knowledge graphs by adding missing knowledge and correcting errors.

Main contribution: It organizes refinement methods and evaluation practices for KGs.

Connection to explicit world models: Missing actions/stakeholders resemble incompleteness; invented transitions resemble incorrect additions.

Potential relevance: Useful for separating completeness and correctness in open-ended generated artifacts.

Potential limitations: KGs are usually relational fact graphs, not action-conditioned stochastic transition systems.

### Causal Abstraction

#### Causal Consistency of Structural Equation Models

Link: https://proceedings.mlr.press/v70/rubenstein17a.html

Summary: Rubenstein and collaborators study conditions under which causal models at different levels are consistent.

Main contribution: It formalizes when high-level and low-level causal models align under interventions.

Connection to explicit world models: Actions in a world model resemble interventions if transitions are interpreted causally.

Potential relevance: Useful for evaluating whether coarse and fine action-effect models preserve intervention consequences.

Potential limitations: The repository's transitions may represent possibilities rather than causal mechanisms.

#### Abstracting Causal Models

Link: https://doi.org/10.1609/aaai.v33i01.33012678

Summary: Beckers and Halpern develop formal criteria for abstraction between causal models.

Main contribution: It gives a rigorous account of mapping detailed causal models to higher-level ones.

Connection to explicit world models: It supports thinking about state variables and action effects at different granularities.

Potential relevance: Strong conceptual support for refinement and abstraction equivalence.

Potential limitations: Requires explicit causal variables and interventions, which the current schema does not define.

### Representation Similarity and Metric Invariance

#### Representational Similarity Analysis

Link: https://doi.org/10.3389/neuro.06.004.2008

Summary: RSA compares representations by comparing patterns of similarity among represented items.

Main contribution: It shifts comparison from raw representation units to relational structure among items.

Connection to explicit world models: The analogy is that models may be compared through preserved relationships rather than surface labels.

Potential relevance: Useful as a general metric-invariance caution.

Potential limitations: It is not a transition-system equivalence theory.

#### Similarity of Neural Network Representations Revisited

Link: http://proceedings.mlr.press/v97/kornblith19a.html

Summary: Kornblith and collaborators analyze representation similarity measures and their invariance properties.

Main contribution: Centered Kernel Alignment became a widely used representation comparison method with defined invariances.

Connection to explicit world models: It reinforces that metric invariance choices are substantive scientific assumptions.

Potential relevance: Useful when articulating why a representation metric should be invariant to some transformations and not others.

Potential limitations: It concerns neural activations, not symbolic world models.

## Inference

The literature supports Jobst's research direction as a serious existing idea family, not a blank-slate invention. Similar loops and principles appear in CEGAR, abstraction refinement, model minimization, graph coarsening, causal abstraction, and state abstraction.

The repository differs because its inputs are underspecified natural language and its outputs are inspectable possibility models. That combination makes semantic support and human judgment more central than in many formal abstractions.

## Speculation

The strongest future literature framing may be:

- take renaming-invariant structural matching as the current baseline;
- study which additional transformations preserve explicit world-model adequacy;
- test whether metric stabilization can identify an appropriate granularity;
- treat semantic omissions and unsupported inventions as separate failure modes.

## Open Questions

- Which reviewed theories can handle optional rewards and missing goals?
- Which theories can handle non-acting stakeholders and normative constraints?
- Which theories require a fully specified ground truth?
- Which papers provide reusable experimental methodology rather than just vocabulary?
- Which source communities are missing from this first pass, especially semantic parsing, requirements engineering, and safety-case modeling?

