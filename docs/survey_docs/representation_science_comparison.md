# Representation Science Comparison

## 1. Research question

This report asks:

> **What exactly is an explicit world model in the current repository?**

It does not ask how to build a benchmark suite. It examines the represented objects, the assumptions required by the representation, and the unresolved criteria by which two representations might describe the same world.

> **Evidence convention**
>
> - **Repository evidence**: directly instantiated or stated in the notebooks.
> - **Inference**: a representational consequence of those choices.
> - **Literature comparison**: comparison with the external frameworks listed in `benchmark_methodology_comparison.md`.
> - **Speculation**: a possible research extension not currently implemented or claimed.

The primary repository artifact is `notebooks/Copy_of_Test_Cases (1).ipynb`; the earlier notebook records a less developed version of the same representation.

## 2. Current repository representation

### 2.1 Formal core

**Repository evidence.** The notebook defines its desired output as a compact JSON-style stochastic game. Its recurring formal object can be summarized as:

\[
M=(P,s_0,S,A,T,R?)
\]

where:

- \(P\) is a non-empty set of players;
- \(s_0\) is an initial state;
- \(S\) is a finite set of states with terminal labels;
- \(A\) gives state-dependent actions for active players;
- \(T\) maps actions or joint actions to probability distributions over successor states; and
- \(R\) is an optional reward representation.

The notebook stresses that this object represents **possibilities**, not actual behavior, policies, or goals. A model describes what actors could do and what could follow, not what they will choose (expanded notebook, cell 41 and the discussion in cell 43).

```text
Natural-language situation
          |
          v
   explicit entities and state
          |
          v
state-dependent action affordances
          |
          v
probabilistic successor possibilities
          |
          v
optional player-indexed value signals
```

### 2.2 Representation components

#### Players

**Definition.** Active decision-makers that receive identifiers and may have actions or rewards.

**Where they appear.** Every exact expected model contains `players`, with one robot in Levels 1–3 and two players in Level 4 and the game situations.

**Status.** Explicit and mandatory.

**Issue.** The representation has no separate type for an affected but non-acting stakeholder. This becomes important in the situational cases, where passengers, owners, children, residents, employees, family members, institutions, and animals must be represented without necessarily being decision-making players.

#### Stakeholders

**Definition.** Parties whose safety, autonomy, interests, standing, or claims are affected by modeled actions.

**Where they appear.** The “should include” lists for S.1–S.11 and C.1–C.4 repeatedly require central, absent, vulnerable, or institutional stakeholders.

**Status.** Explicit in annotation prose but missing from the formal schema.

#### States

**Definition.** Discrete world configurations sufficient to determine available actions and transition behavior.

**Where they appear.** Every formal case uses a `states` dictionary with descriptions and `terminal` flags.

**Status.** Explicit and mandatory.

**Issue.** State variables are not factorized. Location, possession, lighting, completion, evidence, and social conditions are embedded in state names or free-text descriptions.

#### Actions and affordances

**Definition.** Options available to a player in a particular state.

**Where they appear.** `actions[state][player]`. Preconditions are typically encoded by making actions available only in appropriate states or by making premature attempts self-loop.

**Status.** Explicit. Affordance conditions are implicit in the state-indexed action table.

#### Joint actions

**Definition.** Simultaneous action profiles for all currently active players.

**Where they appear.** Level 4 and game situations use `+`-joined action names in player-list order. Once only one player remains active in 4.4, the key becomes a single action name.

**Status.** Derived concept with an explicit but fragile string encoding.

#### Transitions

**Definition.** Action-conditioned probability distributions over successor states.

**Where they appear.** `transition_probabilities[state][action_key]`.

**Status.** Explicit and mandatory.

**Issue.** The schema represents extensionally what happens for each action profile, but does not represent causal mechanisms or reusable transition rules.

#### Consequences

**Definition.** Changes following an action, including physical, informational, social, safety, and institutional effects.

**Where they appear.** Formal cases encode them as successor states. Situational criteria request consequences such as harm from a false intervention, delayed tasks, embarrassment, autonomy loss, or unequal allocation.

**Status.** Derived from successor states in exact cases; implicit in prose for open cases.

#### Rewards and values

**Definition.** Player-indexed numerical consequences used to compare outcomes or actions.

**Where they appear.** Level 4 and G.1 attach rewards to state/joint-action pairs. G.2 attaches rewards to terminal outcome states because one stochastic action can lead to differently valued outcomes.

**Status.** Optional and inconsistently represented.

**Repository evidence.** G.2 explicitly flags the unresolved choice between outcome-state rewards and rewards on `(state, action, next_state)` triples (expanded notebook, cell 83).

#### Goals and policies

**Definition.** Objectives and behavior-selection rules.

**Where they appear.** They are discussed primarily to exclude them. The notebook states that the JSON specifies possibilities, not actual behavior or policy.

**Status.** Deliberately missing from the formal world model.

**Issue.** The Level 3 heading refers to actions that may matter under different goals, but goals are not themselves represented. Decision relevance is therefore assessed externally.

#### Resources and objects

**Definition.** Physical or scarce entities that enable, constrain, or are changed by actions.

**Where they appear.** Keys, packages, tools, supply items, medication, seats, vehicles, rooms, lights, and doors.

**Status.** Implicit inside state descriptions and action names; no first-class entity or resource type.

#### Constraints and preconditions

**Definition.** Conditions governing action availability or effects.

**Where they appear.** Keys are required for doors; location is required for pickup; code entry and unlocking precede retrieval; scarce seats constrain allocation.

**Status.** Implicit in action availability and transitions.

#### Observations and evidence

**Definition.** Information received by an actor about the world, potentially noisy or incomplete.

**Where they appear.** A rattling package, an unconfirmed warning, someone looking ill or tired, a barking dog, a fire alarm, a guard’s unexplained instruction.

**Status.** Present in prompts and annotations but missing as a first-class representational object.

#### Knowledge and beliefs

**Definition.** What each actor knows, believes, or assigns probability to.

**Where they appear.** The hidden coins and most S/C cases require distinctions between truth, evidence, claims, and uncertainty.

**Status.** Missing. The representation has no observation function, belief state, information set, or actor-relative knowledge relation.

#### Uncertainty

**Definition.** Multiple live hypotheses about world facts, intentions, risks, rules, or future outcomes.

**Where it appears.** Stochastic successor distributions in G.2; prose requirements in S/C cases such as true/false warning, intact/broken vase, guardian present/absent, real/false alarm, and legitimate/unequal institutional restriction.

**Status.** Explicit for aleatoric transition randomness; implicit and inconsistently represented for epistemic uncertainty.

#### Institutions, norms, and authority

**Definition.** Social or organizational structures that constrain options, assign authority, or create legitimate expectations.

**Where they appear.** Factory lockout requirements, emergency procedures, transit rules, workplace hierarchy, laïcité policy, residential-society restrictions, and reporting relationships.

**Status.** Present in scenario prose and annotations but missing from the formal schema.

#### Time and interaction depth

**Definition.** Ordering, duration, deadlines, and temporal persistence.

**Where they appear.** Sequential paths encode ordering. Situational cases request “a few steps”; Lane 2 unrolls cycles to a finite horizon. Medication delay, traffic pressure, fire evacuation, and asynchronous completion introduce time sensitivity.

**Status.** Ordering is derived from transitions; duration, deadlines, and temporal units are missing.

#### Provenance and modeling assumptions

**Definition.** Whether a modeled element is given by the prompt, inferred from general knowledge, introduced as a borderline hypothesis, or invented without support.

**Where it appears.** Expect/avoid annotations repeatedly distinguish reasonable, borderline, and forbidden inference. Lane 2 records conversion assumptions such as finite-horizon truncation and default terminal payoffs.

**Status.** Modeling assumptions are partially recorded by the converter; element-level provenance is missing.

## 3. Ontology table

| Component | Explicit | Implicit/derived | Missing or inconsistent | Notes |
|---|:---:|:---:|:---:|---|
| Player | ✓ |  |  | Mandatory identifier |
| Stakeholder |  | ✓ | ✓ | Required in annotations; no schema type |
| Initial state | ✓ |  |  | Mandatory |
| State | ✓ |  |  | Discrete and finite |
| State variable |  | ✓ | ✓ | Bundled into descriptions |
| Terminality | ✓ |  |  | Episode boundary may not equal real-world termination |
| Action | ✓ |  |  | State- and player-indexed |
| Affordance |  | ✓ |  | Derived from action availability |
| Joint action |  | ✓ | ✓ | String concatenation rather than structured profile |
| Transition | ✓ |  |  | Extensional table |
| Probability | ✓ |  |  | Represents stochastic outcomes, not beliefs |
| Consequence |  | ✓ |  | Successor state or annotation prose |
| Reward | ✓ |  | ✓ | Optional; two incompatible placements |
| Goal |  |  | ✓ | Deliberately outside current model |
| Policy |  |  | ✓ | Deliberately outside current model |
| Preference |  | ✓ | ✓ | Sometimes reward, often prose |
| Object/resource |  | ✓ | ✓ | Embedded in state/action text |
| Constraint |  | ✓ |  | Encoded via availability/effects |
| Precondition |  | ✓ |  | No reusable rule object |
| Observation |  | ✓ | ✓ | Prompt-only evidence |
| Knowledge |  |  | ✓ | No actor-relative representation |
| Belief |  |  | ✓ | No epistemic distribution |
| Hidden fact |  | ✓ | ✓ | In prose or bundled states |
| Aleatoric uncertainty | ✓ |  |  | Transition probabilities |
| Epistemic uncertainty |  | ✓ | ✓ | Annotation requirement, no formal semantics |
| Institution |  | ✓ | ✓ | Scenario prose only |
| Norm/rule |  | ✓ | ✓ | Scenario prose only |
| Authority |  | ✓ | ✓ | Annotation prose only |
| Time order |  | ✓ |  | Transition depth |
| Duration/deadline |  |  | ✓ | Not formalized |
| Simultaneity |  | ✓ |  | Joint-action convention |
| Independence |  | ✓ |  | Property of transitions/rewards |
| Provenance |  | ✓ | ✓ | No per-element support label |
| Alternative valid model |  | ✓ | ✓ | Discussed, no equivalence-class object |

## 4. Representation assumptions

### 4.1 Finite discrete-state assumption

**Repository evidence.** Every expected model enumerates a finite dictionary of states. Continuous location, time, risk, and physical variables are discretized or omitted.

**Inference.** The representation is most natural for compact propositional worlds and becomes expensive when many independently varying facts must be represented.

### 4.2 Markov sufficiency assumption

**Inference.** Because transition behavior is indexed by current state and action profile, the state is assumed to contain all history relevant to future possibilities. This is not stated explicitly, but it follows from the schema.

### 4.3 Closed modeled-world assumption

**Repository evidence.** Lane 1 rejects transitions to undeclared states and undeclared action profiles.

**Inference.** Once a model is generated, its declared state/action space functions as a closed possibility space. This makes omissions scientifically important: an absent action or stakeholder is not merely undocumented but unavailable to downstream reasoning.

### 4.4 Episodic terminality assumption

**Repository evidence.** Toy cases mark benchmark outcomes terminal after a chosen modeling horizon. Jobst’s annotation questions why delivery states in 2.2 must be terminal when the prompt does not imply that the world ends.

**Inference.** `terminal` sometimes means “the benchmark stops evaluating here,” not “nothing else can happen.” This conflates world semantics with evaluation scope.

### 4.5 Action enumeration assumption

**Repository evidence.** All formal behavior must appear as an action entry. Open scenarios expect the model to infer actions absent from the prompt.

**Inference.** Representation quality depends critically on action-space construction, not merely transition prediction.

### 4.6 Determinism bias

**Repository evidence.** Eleven of the twelve exact expected models are deterministic. G.2 is explicitly the first stochastic case.

**Inference.** The schema allows stochasticity, but the test bank provides little evidence about how well the representation handles it.

### 4.7 Single shared state assumption

**Repository evidence.** All actors act in one shared state graph.

**Inference.** There is no formal separation between world truth and actor-specific observation or belief. Hidden information can be described but not represented epistemically.

### 4.8 Player-centric ontology assumption

**Repository evidence.** `players` is the only actor-like field, while S/C criteria repeatedly require affected parties who may not act.

**Inference.** The exact schema is game-centric; the open cases require a broader socio-technical ontology.

### 4.9 Numeric-value assumption

**Repository evidence.** When value is formalized, it is encoded as player-indexed numeric reward.

**Inference.** Autonomy, consent, procedural fairness, authority, and rights cannot be represented faithfully by the current reward field alone without additional modeling assumptions.

## 5. Representation philosophies in the literature

### 5.1 Internal versus external world models

Many world-model benchmarks surveyed in 2026 assess internal learned representations indirectly through predictions, generated video, control fidelity, or downstream policy utility. The repository instead requires an **externalized** model whose states, actions, and transitions are inspectable.

**Literature comparison.** The survey’s targets—state consistency, persistence, physical plausibility, causal reasoning, control fidelity, and utility—describe what learned models should achieve. They do not require a human-readable symbolic ontology. See [A Survey of World Model Benchmarks](https://world-model-benchmarks.github.io/).

**Repository distinction.** Errors can be localized to a declared state, missing affordance, unsupported transition, or collapsed uncertainty before a policy acts.

### 5.2 Explicit versus latent representation

**Repository evidence.** The generated artifact is JSON and is evaluated mechanically and structurally.

**Inference.** Explicitness enables auditing but imposes ontological commitments: a model must decide what counts as a state, player, action, and consequence. Latent models may avoid making those commitments readable, but cannot be inspected with Lane 1/2 methods.

### 5.3 Completeness versus economy

**Repository evidence.** Lane 2 penalizes missing reference structure through coverage and invented structure through candidate precision. Jobst’s note accepts that a valid model may be larger than the reference.

**Inference.** Representation quality is not maximized by either minimality or detail alone. It lies between omission and unjustified elaboration.

### 5.4 Abstraction and equivalence

**Repository evidence.** Lane 2 handles renaming through structural matching and finite-horizon conversion. It does not establish that state splitting, state merging, intermediate steps, or longer horizons are equivalent.

**Literature comparison.** AIBench treats abstraction fidelity as preservation of application-level performance. Formal methods contain behavioral equivalence concepts. Neither directly resolves equivalence between LLM-generated explicit models under textual underspecification.

### 5.5 Epistemic fidelity

**Repository evidence.** S/C cases repeatedly forbid converting an observation or claim into established fact. Examples include the unconfirmed hijack warning, rattling vase, ill-looking passenger, absent guardian, barking dog, manager’s false-alarm claim, and unexplained delivery restriction.

**Inference.** A good world model must preserve not only possible world states but the epistemic status of claims. The current schema cannot express that distinction directly.

### 5.6 Decision relevance

**Repository evidence.** Level 3 tests retention of facts that may matter under different goals, while the notebook excludes a particular policy or goal from the representation.

**Inference.** A state abstraction is adequate when it preserves distinctions that could alter available actions, consequences, or values for a relevant class of decisions. This criterion is present conceptually but has no formal definition.

## 6. Representation-quality boundary

The repository suggests a layered view:

```text
Layer 1 — Formal admissibility
  Can the representation be parsed and traversed?

Layer 2 — Structural and causal fidelity
  Does it preserve the stated dynamics and affordances?

Layer 3 — Semantic and epistemic adequacy
  Does it include justified actors and possibilities while preserving uncertainty?

Layer 4 — Decision-relative sufficiency
  Does it preserve the distinctions needed for downstream reasoning without unsupported detail?
```

Layers 1 and part of 2 are operationalized. Layers 3 and 4 are evidenced by annotations but remain research questions.

## 7. Representation research opportunities

Scores range from 1 (low) to 5 (high).

| Opportunity | Novelty | Scientific impact | Alignment | Evidence basis |
|---|---:|---:|---:|---|
| Adequacy under underspecification | 5 | 5 | 5 | Exact/open ground-truth split and expect/avoid annotations |
| Equivalence under abstraction and refinement | 5 | 5 | 5 | Valid larger models acknowledged; Lane 2 limited to structural matching |
| Semantic omission versus unsupported invention | 4 | 5 | 5 | Coverage/precision plus S/C annotations |
| Epistemic fidelity and uncertainty preservation | 4 | 5 | 5 | Repeated uncertainty requirements; missing belief/observation model |
| Stakeholder versus player ontology | 4 | 4 | 5 | Stakeholders central in S/C cases but absent from schema |
| Normative option spaces without policy choice | 4 | 5 | 4 | S.9–S.11 and C cases preserve competing claims |
| Per-element given/inferred/invented provenance | 4 | 4 | 5 | Borderline and forbidden inference distinctions |
| Reward semantics across deterministic/stochastic models | 2 | 4 | 4 | Explicit inconsistency flagged in G.2 |
| Terminality as world property versus evaluation boundary | 3 | 4 | 4 | Jobst’s 2.2 annotation and finite-horizon conversion |

### Recommended representation direction

**Inference.** The strongest direction is a theory of **decision-relative representation adequacy and equivalence**:

> Two generated world models should count as equivalent when their differences in granularity or encoding do not change the decision-relevant actors, affordances, uncertainties, or consequences supported by the source situation.

This direction builds directly on the existing distinction between mechanical validity, structural coverage/precision, and open-ended semantic criteria. It does not require the project to become a general ontology effort or another broad benchmark taxonomy.

## References

- Gao, W. et al. [AIBench Scenario: Scenario-distilling AI Benchmarking](https://arxiv.org/abs/2005.03459).
- Zhou, L. et al. [General Scales Unlock AI Evaluation with Explanatory and Predictive Power](https://www.nature.com/articles/s41586-026-10303-2).
- Blagec, K. et al. [Intelligence Task Ontology](https://arxiv.org/abs/2110.01434).
- Anonymous authors. [A Survey of World Model Benchmarks](https://world-model-benchmarks.github.io/), 2026 manuscript snapshot.
