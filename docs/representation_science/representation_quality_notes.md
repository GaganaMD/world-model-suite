# Representation Quality Notes

## Purpose

These notes collect what the current repository code suggests about representation quality. They separate code-supported evidence from interpretation and unresolved research questions.

## Repository Evidence

### What appears represented

The executable expected models represent:

- active players;
- an initial state;
- finite states;
- terminal and non-terminal states;
- state-dependent action affordances;
- deterministic transition maps in the ten executable fixtures;
- optional action-indexed rewards in Level 4 fixtures;
- simultaneous action profiles for two-player fixtures;
- partial completion in TC 4.4, where one player can stop acting while another remains active;
- no-op actions through self-loops;
- preconditions through action availability and self-looping failure transitions;
- reachability from the initial state.

### What Lane 1 treats as quality

Lane 1 treats a model as mechanically valid when it is parseable, schema-conformant, internally referentially consistent, probability-normalized, reachable, and coherent about terminal states.

Lane 1 uses fail/warn findings and a minimum-over-subscore aggregation. A single fatal parse, schema, or mechanical issue can make the whole Lane 1 result fail.

### What Lane 2 treats as quality

Lane 2 treats structural correspondence to a reference as quality. It explicitly handles renaming of players and states through matching. The demo distinguishes:

- equivalent renaming;
- missing reference structure;
- invented candidate structure.

It reports coverage and precision separately before combining them with a harmonic mean.

### What appears missing from executable representation

The executable schema does not contain first-class fields for:

- non-acting stakeholders;
- objects as reusable typed entities;
- resources as quantities or constraints;
- state variables separate from state names/descriptions;
- observations;
- actor-specific beliefs;
- evidence provenance;
- institutions;
- norms;
- authority;
- goals;
- policies;
- uncertainty type;
- reward placement for stochastic successor outcomes;
- representation boundary or modeled horizon.

### Current code limitations

Lane 1 catches the 17 deliberate mutations in the notebook. However, simple extra probes show it is not a fully defensive validator for arbitrary malformed JSON-like structures. For example, scalar JSON or incorrect nested container types can raise Python exceptions instead of returning structured findings.

Lane 2 introduces finite-horizon unrolling and default terminal payoffs. Those assumptions are reported in the scoring output, but they still affect what is compared.

The executable fixtures in Levels 1-4 are deterministic. The expanded notebook contains game and situational markdown beyond those fixtures, but the executable model fixtures reviewed here do not include a stochastic executable example.

## Literature

Adjacent literatures treat representation quality through different lenses:

- formal methods: correctness under refinement and abstraction;
- MDP/RL theory: state abstraction, value preservation, policy preservation, bisimulation, and homomorphism;
- graph methods: isomorphism, coarsening quality, and invariance to node splitting;
- ontology engineering: consistency, completeness, conciseness, clarity, and ontological commitment;
- knowledge graph evaluation: factual correctness, completeness, schema consistency, redundancy, and downstream utility;
- causal abstraction: whether high-level variables preserve intervention-relevant structure.

These literatures suggest that quality is task-relative. A representation can be valid but inadequate, detailed but unsupported, compact but too coarse, or structurally different while semantically equivalent.

## Inference

The repository code currently operationalizes three quality dimensions:

- admissibility: whether the artifact is well formed;
- coverage: how much of the reference structure is present;
- precision: how much of the candidate structure is justified by the reference.

The code also implies several representational commitments:

- actions are possible choices, not predicted behavior;
- state identity carries all information needed for transition lookup;
- the modeled state/action space is closed after generation;
- a state split matters to Lane 2 even when it may not matter semantically;
- a state merge matters to Lane 2 even when it may preserve decision-relevant behavior;
- a finite horizon can convert ongoing processes into terminal comparison artifacts.

## Speculation

Representation quality may require a family of metrics rather than one score. A future evaluation may need to preserve:

- mechanical validity;
- structural fidelity;
- semantic coverage;
- unsupported invention control;
- epistemic fidelity;
- normative and institutional adequacy;
- decision-relative sufficiency;
- invariance under harmless refinements.

The repository's coverage/precision split is a useful starting point because it distinguishes omission from invention. It is not sufficient for granularity, abstraction, or equivalence questions.

## Open Questions

- Which quality dimensions are independent enough to measure separately?
- Which quality dimensions can be automated, and which require expert review?
- When is an extra state a useful refinement rather than invented complexity?
- When is a missing state an acceptable abstraction rather than an omission?
- Should reward semantics be part of representation quality or downstream decision quality?
- How should models represent uncertainty without requiring a full POMDP-like schema?
- What should a metric do when two structurally different models preserve the same decision-relevant distinctions?

