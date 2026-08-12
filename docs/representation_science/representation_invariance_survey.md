# Representation Invariance Survey

## Purpose

This is the main survey for refinement, abstraction, equivalence, and metric invariance as they relate to explicit world models.

The organizing hypothesis is not that all refinements should be ignored. It is that evaluation metrics should be stable under representational changes that preserve the task-relevant content, and sensitive to refinements that add or remove meaningful information.

## Repository Evidence

The expanded notebook implements one invariance directly: Lane 2 compares a generated model to a reference "up to renaming" through Jobst's `game_matching` wrapper. The TC 1.1 demo records a Lane 2 score of 1.000 for a renamed but structurally equivalent model.

The same demo records lower scores for a missing-action variant and an invented-extra-content variant. This establishes a code-level distinction between omission and invention through coverage and precision.

The Lane 2 adapter unrolls cycles to a finite horizon and defaults terminal payoffs to 0.0. Those assumptions mean the current metric is not purely about semantic world-model equivalence.

## Literature

### Refinement Invariance

Core idea: A property or metric is refinement-invariant when it is preserved as a representation becomes more detailed, provided the refinement does not change the underlying behavior or meaning being evaluated.

Representative papers:

- Patrice Cousot and Radhia Cousot, "Abstract Interpretation: A Unified Lattice Model for Static Analysis of Programs by Construction or Approximation of Fixpoints" (POPL 1977), https://doi.org/10.1145/512950.512973
- E. M. Clarke, O. Grumberg, S. Jha, Y. Lu, and H. Veith, "Counterexample-Guided Abstraction Refinement" (JACM 2003), https://doi.org/10.1145/876638.876643
- Martin Abadi and Leslie Lamport, "The Existence of Refinement Mappings" (Theoretical Computer Science 1991), https://doi.org/10.1016/0304-3975(91)90224-P

Connection to our project: The current repository can validate a concrete model and compare it to a reference, but it does not yet say whether a more detailed candidate should count as equivalent. Refinement invariance is directly related to Jobst's idea that a model can be refined until metrics stabilize.

Potential implications: A future metric could distinguish behavior-preserving refinements from refinements that reveal missing actions, uncertainty, or consequences.

Open questions: What is the refinement relation for a language-induced world model? Is it state splitting, adding variables, adding actors, adding evidence labels, extending horizon, or all of these?

### Graph Invariance

Core idea: Graph metrics often should be invariant to label changes and sometimes to graph transformations that preserve structural meaning.

Representative papers:

- Laszlo Babai, "Graph Isomorphism in Quasipolynomial Time" (STOC 2016), https://doi.org/10.1145/2897518.2897542
- Nils M. Kriege, Fredrik D. Johansson, and Christopher Morris, "A Survey on Graph Kernels" (Applied Network Science 2020), https://doi.org/10.1007/s41109-019-0195-3

Connection to our project: Lane 2 already uses matching to ignore names and compare structure. This is graph invariance at the identity/isomorphism level.

Potential implications: Existing graph similarity methods may help evaluate renamed or approximately matching state-transition graphs, but they do not by themselves solve semantic equivalence under abstraction.

Open questions: Which graph differences are harmless encodings and which are semantic changes? Should edge labels, probabilities, rewards, and player-indexed actions be preserved exactly?

### Model Refinement

Core idea: A model refinement adds detail while preserving the behavior, properties, or obligations established by a more abstract model.

Representative papers:

- Edmund M. Clarke, Orna Grumberg, and David E. Long, "Model Checking and Abstraction" (TOPLAS 1994), https://doi.org/10.1145/174644.174646
- Edmund M. Clarke et al., "Counterexample-Guided Abstraction Refinement" (JACM 2003), https://doi.org/10.1145/876638.876643

Connection to our project: A coarse explicit world model might omit details that are irrelevant at first but need to be refined when a metric or counterexample reveals a failure.

Potential implications: CEGAR is a close formal analogue to "start coarse, refine when the abstraction is inadequate." The repository's metric-stabilization hypothesis can be compared against this family of methods.

Open questions: What is the world-model equivalent of a counterexample? A failed Lane 2 score, a human-identified omission, a changed downstream decision, or an uncertainty collapse?

### Abstraction

Core idea: Abstraction removes detail while preserving selected properties of interest.

Representative papers:

- Fausto Giunchiglia and Toby Walsh, "A Theory of Abstraction" (Artificial Intelligence 1992), https://doi.org/10.1016/0004-3702(92)90021-O
- Patrick Cousot and Radhia Cousot, abstract interpretation work, https://doi.org/10.1145/512950.512973

Connection to our project: The current expected fixtures are abstractions of natural-language situations. They choose which facts become states, actions, and terminal outcomes.

Potential implications: Any claim about model quality must specify what abstraction is being evaluated and what it is intended to preserve.

Open questions: Should explicit world-model abstraction preserve possible actions, transition behavior, stakeholder effects, values, uncertainty, or some combination?

### Coarsening

Core idea: Coarsening collapses a detailed structure into a smaller one while attempting to preserve important properties.

Representative papers:

- Andreas Loukas, "Graph Reduction with Spectral and Cut Guarantees" (JMLR 2019), https://jmlr.org/papers/v20/18-680.html
- George Karypis and Vipin Kumar, "A Fast and High Quality Multilevel Scheme for Partitioning Irregular Graphs" (SIAM Journal on Scientific Computing 1998), https://doi.org/10.1137/S1064827595287997

Connection to our project: A coarser world model may merge states, actors, actions, or hypotheses. Lane 2 does not currently identify when such merges preserve the relevant model.

Potential implications: Graph coarsening offers vocabulary for compression quality, but explicit world models add semantics not present in generic graphs.

Open questions: What should be preserved during coarsening: reachability, optimal decisions, risk ordering, uncertainty status, stakeholder coverage, or all transition probabilities?

### State Abstraction

Core idea: State abstraction groups states that are equivalent for a task, policy, value function, transition structure, or reward structure.

Representative papers:

- Lihong Li, Thomas J. Walsh, and Michael L. Littman, "Towards a Unified Theory of State Abstraction for MDPs" (AAAI 2006), commonly available as PDF: https://people.cs.umass.edu/~mlittman/papers/li-aaai06.pdf
- Robert Givan, Thomas Dean, and Matthew Greig, "Equivalence Notions and Model Minimization in Markov Decision Processes" (Artificial Intelligence 2003), https://doi.org/10.1016/S0004-3702(02)00376-4

Connection to our project: State abstraction is one of the closest analogues to deciding when two explicit world-model states can be merged without losing evaluation-relevant distinctions.

Potential implications: Different abstractions preserve different things. A value-preserving abstraction may be too weak if the benchmark cares about stakeholder or uncertainty representation independent of a fixed reward.

Open questions: Which state-abstraction criterion fits a model that deliberately excludes policy and goal selection?

### Semantic Equivalence

Core idea: Two representations are semantically equivalent when they preserve meaning, even if syntax, labels, or internal structure differ.

Representative papers:

- Robin Milner, "A Calculus of Communicating Systems" (1980) and subsequent bisimulation literature.
- Davide Sangiorgi, "On the Origins of Bisimulation and Coinduction" (ACM Transactions on Programming Languages and Systems 2009), https://doi.org/10.1145/1516507.1516510

Connection to our project: Lane 2 renaming equivalence is a narrow case of semantic equivalence. The open problem is equivalence under state splitting, action decomposition, horizon differences, and alternative factorizations.

Potential implications: Semantic equivalence may require task-relative interpretation, not pure graph matching.

Open questions: Who decides semantic equivalence for underspecified natural-language prompts: formal rules, expert annotations, downstream tasks, or a combination?

### Ontology Refinement

Core idea: Ontology refinement changes classes, relations, constraints, or hierarchy to improve coverage, correctness, or fitness for use.

Representative papers:

- Nicola Guarino and Christopher Welty, OntoClean work on ontology analysis, including "Evaluating Ontological Decisions with OntoClean" (CACM 2002), https://doi.org/10.1145/503124.503150
- Ljiljana Stojanovic, "Methods and Tools for Ontology Evolution" (PhD thesis, 2004), often cited in ontology evolution literature.

Connection to our project: The current schema has players, states, actions, transitions, and rewards, while scenario reasoning often seems to require stakeholders, observations, norms, and institutions.

Potential implications: Ontology refinement could clarify whether missing categories are schema limitations, annotation concepts, or unnecessary complexity.

Open questions: Which ontology refinements improve evaluation and which only re-label existing free-text descriptions?

### Knowledge Representation

Core idea: Knowledge representation studies formal structures for entities, relations, rules, uncertainty, events, and inference.

Representative papers:

- Ronald J. Brachman and Hector J. Levesque, "Knowledge Representation and Reasoning" (book, 2004).
- Deborah L. McGuinness and Frank van Harmelen, "OWL Web Ontology Language Overview" (W3C, 2004), https://www.w3.org/TR/owl-features/

Connection to our project: Explicit world models are knowledge representations specialized for possible actions and state transitions.

Potential implications: KR can supply language for open-world versus closed-world assumptions, ontological commitment, provenance, and reasoning over incomplete information.

Open questions: How much KR machinery is useful before the benchmark stops being compact and inspectable?

### Knowledge Graph Evaluation

Core idea: Knowledge graph quality is evaluated through correctness, completeness, consistency, conciseness, provenance, and downstream usefulness.

Representative papers:

- Shaoxiong Ji et al., "A Survey on Knowledge Graphs: Representation, Acquisition, and Applications" (IEEE TNNLS 2021), https://doi.org/10.1109/TNNLS.2021.3070843
- Heiko Paulheim, "Knowledge Graph Refinement: A Survey of Approaches and Evaluation Methods" (Semantic Web 2017), https://doi.org/10.3233/SW-160218

Connection to our project: Lane 2 coverage and precision resemble completeness and correctness dimensions in knowledge graph evaluation, but the repository's artifacts are action-conditioned transition models rather than general triples.

Potential implications: KG evaluation vocabulary can help separate missing facts from unsupported additions and structural inconsistency.

Open questions: Can KG-style completeness be adapted when there is no complete ground truth for open situations?

### Metric Stability

Core idea: A metric is stable when small or irrelevant representation changes do not produce misleading score changes.

Representative papers:

- William Meredith, "Measurement Invariance, Factor Analysis and Factorial Invariance" (Psychometrika 1993), https://doi.org/10.1007/BF02294825
- Roger E. Millsap, "Statistical Approaches to Measurement Invariance" (book, 2011), https://doi.org/10.4324/9780203821961
- Simon Kornblith et al., "Similarity of Neural Network Representations Revisited" (ICML 2019), http://proceedings.mlr.press/v97/kornblith19a.html
- Nikolaus Kriegeskorte, Marieke Mur, and Peter Bandettini, "Representational Similarity Analysis" (Frontiers in Systems Neuroscience 2008), https://doi.org/10.3389/neuro.06.004.2008

Connection to our project: The stabilization hypothesis directly asks whether evaluation metrics converge as representation granularity changes.

Potential implications: Stability is a diagnostic, not a guarantee. A metric can be stably insensitive to important information.

Open questions: Which perturbations should be classified as irrelevant, refinement-preserving, or meaning-changing?

### Node Splitting

Core idea: Some network measures should not change merely because one node is split into several equivalent subnodes representing the same underlying object or spatial area.

Representative papers:

- J. Heitzig, J. F. Donges, Y. Zou, N. Marwan, and J. Kurths, "Node-weighted measures for complex networks with spatially embedded sampling" / related node-splitting invariant network measures, arXiv: https://arxiv.org/abs/1101.4757

Connection to our project: A world-model candidate might split a reference state into several substates that preserve the same downstream behavior. Node-splitting invariance provides a direct analogy for metrics that should not reward or punish arbitrary representational subdivision.

Potential implications: The analogy is strong for metric design but incomplete because world-model state splitting can add semantic content, not just duplicate sampling units.

Open questions: When is a state split just a representational artifact, and when does it add relevant evidence, uncertainty, or action affordances?

### Bisimulation

Core idea: Bisimulation relates states or systems that match each other's observable behavior step by step.

Representative papers:

- Robert Givan, Thomas Dean, and Matthew Greig, "Equivalence Notions and Model Minimization in Markov Decision Processes" (Artificial Intelligence 2003), https://doi.org/10.1016/S0004-3702(02)00376-4
- Norm Ferns, Prakash Panangaden, and Doina Precup, "Metrics for Finite Markov Decision Processes" (UAI 2004), https://www.auai.org/uai2004/proceedings/defs/ferns.htm

Connection to our project: Bisimulation is a formal candidate for when states, or whole models, preserve transition behavior.

Potential implications: Bisimulation may be too strict if semantic adequacy allows different horizons or action decompositions, and too narrow if the benchmark cares about non-transition concepts such as stakeholder standing.

Open questions: What observations count as observable behavior in an explicit world model? State labels, actions, probabilities, rewards, stakeholder effects, or natural-language semantics?

### Simulation Relations

Core idea: Simulation is a preorder: one system can match the behavior of another without requiring exact symmetry.

Representative papers:

- Robin Milner and later process-algebra work on simulation and bisimulation.
- Formal verification literature on refinement and implementation relations.

Connection to our project: Coverage and precision resemble asymmetric comparisons. A candidate that includes all reference behavior plus extra branches may simulate the reference but fail precision.

Potential implications: Simulation can formalize one-sided adequacy, while precision penalizes unsupported additions.

Open questions: Should a richer candidate model be allowed to simulate a reference while also being penalized for unsupported branches?

### Abstraction in Planning

Core idea: Planning abstractions reduce problem complexity by ignoring distinctions not needed for plan construction or heuristic guidance.

Representative papers:

- Craig A. Knoblock, "Automatically Generating Abstractions for Planning" (Artificial Intelligence 1994), https://doi.org/10.1016/0004-3702(94)90053-1
- Malte Helmert et al., "Merge-and-Shrink Abstraction: A Method for Generating Lower Bounds in Factored State Spaces" and follow-up planning literature.

Connection to our project: The benchmark's expected models are compact planning-like transition systems with state-dependent actions and preconditions.

Potential implications: Planning abstraction suggests task-relative granularity, but the repository's open cases care about representing live options and consequences before choosing a plan.

Open questions: Can planning abstractions help evaluate world models that are not tied to one goal?

### Abstraction in Reinforcement Learning

Core idea: RL abstraction groups states or actions to preserve value, policy, transition, reward, or option structure.

Representative papers:

- Lihong Li, Thomas J. Walsh, and Michael L. Littman, "Towards a Unified Theory of State Abstraction for MDPs" (AAAI 2006), https://people.cs.umass.edu/~mlittman/papers/li-aaai06.pdf
- Balaraman Ravindran and Andrew G. Barto, work on MDP/SMDP homomorphisms, including "SMDP Homomorphisms: An Algebraic Approach to Abstraction in Semi-Markov Decision Processes."
- Richard S. Sutton, Doina Precup, and Satinder Singh, "Between MDPs and Semi-MDPs: A Framework for Temporal Abstraction in Reinforcement Learning" (Artificial Intelligence 1999), https://doi.org/10.1016/S0004-3702(99)00052-1

Connection to our project: RL abstraction is highly relevant but often assumes rewards and policies matter. The repository often evaluates possibility representations before policy choice.

Potential implications: The literature can help separate value-preserving, policy-preserving, and model-preserving equivalence.

Open questions: Which RL abstraction family applies when rewards are optional and often absent?

### Causal Abstraction

Core idea: A high-level causal model abstracts a lower-level model when interventions and outcomes correspond under a mapping.

Representative papers:

- Ilya Rubenstein et al., "Causal Consistency of Structural Equation Models" (UAI 2017), https://proceedings.mlr.press/v70/rubenstein17a.html
- Sander Beckers and Joseph Y. Halpern, "Abstracting Causal Models" (AAAI 2019), https://doi.org/10.1609/aaai.v33i01.33012678

Connection to our project: A world-model refinement can be viewed as introducing lower-level variables while trying to preserve higher-level intervention/action consequences.

Potential implications: Causal abstraction may help ask whether action effects survive changes in variable granularity.

Open questions: Are repository transitions causal claims, merely possible successor links, or both?

### Invariant Metrics

Core idea: A metric should be invariant under transformations that do not change the target construct and sensitive to transformations that do.

Representative papers:

- Measurement invariance literature in psychometrics distinguishes forms of invariance across groups and instruments.
- Benchmark construct-validity work in AI evaluation emphasizes sensitivity and specificity of metrics.

Connection to our project: A representation metric should ignore harmless renaming and perhaps harmless refinements, but detect omissions, unsupported inventions, and uncertainty collapse.

Potential implications: Metric invariance should be specified transformation by transformation rather than asserted globally.

Open questions: What is the target construct: structural identity, behavioral equivalence, semantic adequacy, or decision-support usefulness?

### Representation Equivalence

Core idea: Two representations may be equivalent under a mapping even if their syntax or internal units differ.

Representative papers:

- Formal model equivalence literature, including bisimulation and simulation.
- Causal abstraction literature on mappings between low-level and high-level variables.
- State-abstraction literature in MDPs and RL.

Connection to our project: The repository needs equivalence concepts beyond renaming if it accepts multiple valid representations for one situation.

Potential implications: Equivalence classes may be more appropriate than single canonical expected JSON for open scenarios.

Open questions: Can equivalence be judged without specifying a downstream decision problem?

### Semantic Equivalence Under Natural Language

Core idea: Natural-language prompts underdetermine formal models; two models can both be faithful to the prompt while differing in detail.

Representative papers:

- Semantic parsing and KR literature on underspecification and logical form.
- Text2World work on generating symbolic world models from language, https://arxiv.org/abs/2502.13092

Connection to our project: The repository explicitly asks LLMs to induce compact world models from short situation descriptions.

Potential implications: Evaluation should not assume one reference JSON is always the only correct target.

Open questions: How can expert annotation specify a family of acceptable models without becoming too loose?

### Node-Splitting Invariance

Core idea: A score should not change solely because one represented unit is split into multiple units that carry the same aggregate meaning.

Representative papers:

- Heitzig et al. on node-splitting invariant network measures, https://arxiv.org/abs/1101.4757

Connection to our project: Node splitting is a concrete version of the granularity problem. It asks whether a metric reacts to arbitrary representational subdivision.

Potential implications: This is one of the closest literatures to the metric-stabilization hypothesis, especially for testing whether model scores change only because the state graph was subdivided.

Open questions: How should probability mass, action availability, and rewards be redistributed when a state is split?

### Refinement Invariance

Core idea: Evaluation remains stable under refinements that preserve the intended abstract model.

Representative papers:

- Abstract interpretation, model refinement, CEGAR, MDP abstraction, and causal abstraction all contain related formulations.

Connection to our project: This is the central research direction: refine a coarse explicit world model and track whether evaluation metrics stabilize.

Potential implications: The research contribution may be a principled account of which explicit-world-model metrics should be invariant under which refinements.

Open questions: Which transformations define legitimate refinement in this repository: state splitting, action decomposition, stakeholder addition, uncertainty factoring, or ontology extension?

## Inference

No single literature exactly matches the repository's object: a language-induced, explicit, action-conditioned possibility model evaluated for validity, structural correspondence, omission, invention, and semantic adequacy. The closest ingredients are distributed across formal verification, MDP abstraction, graph metrics, ontology quality, and causal abstraction.

## Speculation

The most promising organizing principle is not a new universal representation schema. It is a map from transformation types to expected metric behavior:

- renaming: metric should be invariant;
- unsupported invention: metric should change;
- omission of relevant affordance: metric should change;
- semantically redundant state split: metric may be invariant;
- uncertainty-preserving hypothesis split: metric may improve;
- uncertainty-collapsing merge: metric should degrade;
- horizon extension: metric should be interpreted with explicit boundary conditions.

This remains a research hypothesis.

## Open Questions

- Which transformations can be defined syntactically and which require semantic judgment?
- Can refinement invariance be tested with paired generated models?
- Can a metric stabilize before the representation is adequate?
- Should metric stabilization be local to one scenario or aggregated over scenario families?
- How should human reviewers label "same enough" for underspecified prompts?
