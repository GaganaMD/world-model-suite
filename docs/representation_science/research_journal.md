# Research Journal

## 2026-08-07

### Repository Evidence

Reviewed the notebook code in `notebooks/Copy_of_Test_Cases (1).ipynb` and compared it with the older `notebooks/Copy_of_Test_Cases.ipynb`.

Code-level observations:

- The expanded notebook contains Lane 1 mechanical checks, a runner, Lane 2 `game_matching` setup, a schema converter, a Lane 2 scoring wrapper, ten exact expected fixtures, a Lane 2 TC 1.1 demo, and a 17-mutation Lane 1 self-test.
- The older notebook contains Lane 1 and the ten exact fixtures/self-test, but not Lane 2 conversion/scoring code.
- The current executable fixtures are `expected_1_1` through `expected_4_4`.
- Stored output records all ten expected fixtures passing Lane 1.
- Stored output records `17/17 caught` for the Lane 1 negative self-test.
- Stored output records Lane 2 score 1.000 for a renamed TC 1.1 model, and low scores for missing-action and invented-content variants.

### Literature

Initial literature themes identified:

- abstraction and refinement in formal methods;
- counterexample-guided abstraction refinement;
- simulation and bisimulation;
- MDP state abstraction and homomorphisms;
- bisimulation metrics for MDPs;
- graph matching, graph coarsening, and node-splitting invariant measures;
- ontology quality and ontology evolution;
- knowledge graph quality and refinement;
- causal abstraction between structural causal models;
- AI benchmark construct validity;
- world-model benchmark surveys;
- symbolic world-model generation from natural language.

### Inference

The current repository can support a research program about representation quality because it already separates:

- validity from adequacy;
- coverage from precision;
- renaming-equivalent structure from missing or invented structure.

The current code cannot yet support claims about:

- refinement invariance;
- state-splitting invariance;
- semantic equivalence;
- epistemic fidelity;
- stakeholder adequacy;
- ontology quality;
- metric stabilization across granularity levels.

### Speculation

Jobst's stabilization idea appears related to several existing traditions, especially CEGAR, state abstraction, model minimization, graph coarsening, node-splitting invariance, and causal abstraction.

The potentially distinctive project angle is the application to language-induced explicit possibility models, where the target is not a latent predictor, a policy, or a fully specified MDP, but an inspectable representation produced from underspecified text.

### Insights

- Renaming invariance is already a working baseline.
- State splitting and state merging are the next natural invariance tests.
- Finite-horizon unrolling is both useful and conceptually risky because it can turn ongoing states into terminal artifacts.
- Optional rewards make value-preserving abstraction theories only partially applicable.
- Explicit world models need a distinction between structural validity and semantic support.

### Interesting Ideas

- Treat metric behavior under transformations as the central experimental object.
- Build paired models for the same scenario: renamed, split, merged, decomposed, horizon-extended, uncertainty-collapsed, and stakeholder-augmented.
- Ask experts whether each paired model is equivalent, better, worse, or incomparable.
- Compare expert judgments to Lane 1 and Lane 2 behavior.
- Use stabilization curves over refinement depth as evidence, not as a proof of adequacy.

### Literature to Read

- Cousot and Cousot on abstract interpretation.
- Clarke, Grumberg, Jha, Lu, and Veith on CEGAR.
- Abadi and Lamport on refinement mappings.
- Givan, Dean, and Greig on MDP model minimization.
- Ferns, Panangaden, and Precup on bisimulation metrics.
- Li, Walsh, and Littman on state abstraction.
- Ravindran and Barto on MDP/SMDP homomorphisms.
- Sutton, Precup, and Singh on options.
- Loukas on graph reduction.
- Heitzig and collaborators on node-splitting invariant network measures.
- Guarino and Welty on OntoClean.
- Paulheim on knowledge graph refinement.
- Rubenstein et al. and Beckers/Halpern on causal abstraction.
- Text2World and current world-model benchmark surveys.

### Hypotheses

- H1: Lane 2 is appropriately invariant to renaming but not to many semantically harmless refinements.
- H2: State-splitting invariance will require an explicit abstraction map from candidate states to reference states.
- H3: Some refinements should improve semantic adequacy even if they lower structural precision against a compact reference.
- H4: Metric stabilization can help select representation granularity only if the metric has first passed perturbation-based sensitivity tests.
- H5: Open-ended situations need equivalence-class or checklist references rather than single expected JSON graphs.

### Future Experiments

- Create controlled variants of one exact fixture: renamed, state-split, action-decomposed, horizon-extended, and state-merged.
- Create controlled variants of one open situation: uncertainty-preserving, uncertainty-collapsing, stakeholder-omitting, and unsupported-invention variants.
- Score all variants with Lane 1 and Lane 2.
- Compare metric outcomes to expert adequacy judgments.
- Plot metric stabilization as detail is progressively added.

### Open Questions

- What counts as a legitimate refinement in this schema?
- Should refinements be required to provide a mapping back to the coarse model?
- Should semantic adequacy override structural precision when a candidate is larger but better justified?
- Can the current `game_matching` score be decomposed enough to diagnose state, action, transition, and reward differences separately?
- Which open scenarios are best for the first refinement experiment?

## Future Entries

### YYYY-MM-DD

Repository Evidence:

Literature:

Inference:

Speculation:

Insights:

Hypotheses:

Future experiments:

Questions:
