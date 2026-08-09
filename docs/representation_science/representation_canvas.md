# Representation Canvas

## Purpose

This canvas is a reusable template for analyzing future benchmark scenarios. It is not a completed analysis of the existing scenario suite.

Use it to separate what the prompt states, what a model may reasonably infer, what remains uncertain, and what a representation must preserve for evaluation.

## Repository Evidence

The notebook code evaluates explicit JSON models with players, states, state-dependent actions, transition probabilities, terminal states, and optional rewards. The executable fixtures show that the benchmark currently requires compact finite state-transition structures.

The notebook's code-level evaluation does not provide first-class fields for stakeholders, observations, beliefs, institutions, norms, uncertainty provenance, or representation boundaries. Those categories are therefore included here as analysis aids, not as current schema requirements.

## Literature

This canvas is informed by common concerns in knowledge representation, planning, MDP abstraction, causal abstraction, ontology quality, and benchmark construct validity. It does not implement any one framework from those literatures.

## Inference

Future scenario review needs a stable way to ask whether a generated world model includes the right distinctions without rewarding unnecessary detail. The sections below are prompts for analysis, not mandatory schema fields.

## Canvas

### Entities

Purpose: identify the things whose identity or properties may matter.

Questions:

- What entities are explicitly named?
- What entities are clearly implied by the situation?
- Which entities are optional or borderline inferences?
- Which entities would be unsupported inventions?

Example observations:

- Explicit: robot, room, package, passenger.
- Implied: safety system, owner, delivery recipient.
- Borderline: neighbors, traffic authority, customer support.

### Actors

Purpose: distinguish entities capable of choosing actions in the modeled situation.

Questions:

- Who can act?
- Which actors are controlled by the AI model?
- Which actors may respond but are not under AI control?
- Which actors should not be invented as decision-makers?

Example observations:

- A robot with available actions is an actor.
- A human supervisor may be an actor if escalation is plausible.
- A crowd may need to be represented as multiple actors or as a background process.

### Stakeholders

Purpose: capture affected parties whether or not they act.

Questions:

- Whose safety, autonomy, property, status, rights, or interests are affected?
- Are any affected parties absent from the scene?
- Are there vulnerable or institutionally important stakeholders?
- Does the representation collapse distinct stakeholders into one group?

Example observations:

- A passenger inside a vehicle is a stakeholder even if not the AI player.
- A resident affected by a delivery restriction is a stakeholder even if absent.
- A child near a loading dock is a stakeholder even if their intentions are unknown.

### Objects

Purpose: identify physical or informational objects that affect action availability or outcomes.

Questions:

- Which objects create affordances, constraints, or risks?
- Which objects change ownership, location, condition, or status?
- Which object properties are known, uncertain, or irrelevant?

Example observations:

- A key enables opening a locked door.
- A package may contain fragile contents.
- A wheelchair changes evacuation affordances.

### States

Purpose: identify world configurations that distinguish available actions or consequences.

Questions:

- What facts must be true in the initial state?
- Which facts need separate state distinctions?
- Which facts can remain descriptive rather than state-defining?
- Which states are terminal because of the world and which are terminal because of evaluation scope?

Example observations:

- Location and possession often define states in toy fixtures.
- Alarm truth, package damage, or guardian presence may define live hypotheses.
- A terminal delivery state may be an evaluation boundary rather than world termination.

### Actions

Purpose: capture available choices without predicting which action will be taken.

Questions:

- What actions are directly stated?
- What actions are reasonably implied by the situation?
- Which information-gathering actions are needed before irreversible choices?
- Which actions assume unsupported authority or capability?

Example observations:

- Wait/pass is often an available no-op.
- Inspect, verify, ask, escalate, and alert often preserve uncertainty.
- Force, restrain, unlock, or punish may be unsupported without explicit authority.

### Transitions

Purpose: specify how actions change or preserve the modeled world.

Questions:

- Which actions are no-ops?
- Which actions deterministically change the world?
- Which actions have stochastic or uncertain outcomes?
- Do transitions preserve the state variables that should not change?

Example observations:

- Waiting in a room should self-loop if nothing changes.
- Picking up a key should preserve location and door status.
- Asking for confirmation can branch into confirmed, denied, and still-uncertain states.

### Resources

Purpose: represent scarce, enabling, or consumed resources.

Questions:

- What is scarce?
- What enables an action?
- What is consumed, occupied, delayed, or allocated?
- Does the model invent exact quantities not in the prompt?

Example observations:

- Seats in a shuttle are scarce.
- A key enables a door action.
- Time and attention can become resources in emergency settings.

### Institutions

Purpose: identify organizations and rule-bearing structures.

Questions:

- Which institutions are explicitly present?
- Which institutions are plausible background authorities?
- Which rules or procedures may apply?
- Who has authority to interpret the rule?

Example observations:

- A school administration may interpret school policy.
- Building security may confirm an alarm.
- A transit service may define priority seating rules.

### Norms

Purpose: capture social, procedural, cultural, legal, or safety norms without turning them into fixed outcomes.

Questions:

- Which norms are stated?
- Which norms are plausible but uncertain?
- Which norms constrain process rather than result?
- Does the model treat a norm as the only possible correct decision without support?

Example observations:

- Workplace seniority may affect communication style but not factual truth.
- Safety lockout requirements affect action urgency.
- Fair allocation can involve multiple legitimate criteria.

### Beliefs

Purpose: distinguish world facts from actor-relative mental states.

Questions:

- Who knows what?
- Who merely claims something?
- Who is uncertain?
- Does the representation collapse evidence into truth?

Example observations:

- A warning is not proof that a pilot is hostile.
- A manager's assertion is not proof an alarm is false.
- A rattle is evidence of possible damage, not proof.

### Evidence

Purpose: record the support for represented elements.

Questions:

- Is the element explicitly given by the prompt?
- Is it a necessary commonsense inference?
- Is it a plausible but optional inference?
- Is it unsupported?

Example observations:

- "No adult visible" supports uncertainty about guardian presence.
- "Looks ill" supports concern, not diagnosis.
- "The guard gives no reason" supports uncertainty about motive.

### Observations

Purpose: capture sensor-like inputs and reported claims.

Questions:

- What does the AI observe directly?
- What is reported by another party?
- What observations are noisy or ambiguous?
- What information could the AI gather next?

Example observations:

- Smoke detected by a robot is an observation.
- A warning from ground authorities is a report.
- Giggling and protest are observed reactions, not full explanations.

### Uncertainty

Purpose: preserve multiple live hypotheses when the prompt does not settle the fact.

Questions:

- What is unknown?
- Which hypotheses should remain possible?
- Which branch would collapse uncertainty too early?
- Is the uncertainty epistemic, stochastic, normative, or preference-based?

Example observations:

- A dice roll is stochastic uncertainty.
- Whether a vase is broken is epistemic uncertainty.
- Which fairness rule should govern an allocation is normative uncertainty.

### Constraints

Purpose: identify limits on possible actions and effects.

Questions:

- What physical, legal, institutional, temporal, or capability constraints apply?
- Which constraints determine action availability?
- Which constraints are inferred but not guaranteed?

Example observations:

- A locked gate constrains delivery paths.
- A wheelchair constrains stair evacuation.
- A robot may not have authority to discipline a coworker.

### Goals

Purpose: record decision-relevant objectives without assuming a policy.

Questions:

- Which goals are stated?
- Which goals are plausible background objectives?
- Which goals belong to which actor or stakeholder?
- Would different goals require preserving different state distinctions?

Example observations:

- A delivery robot may have a delivery objective.
- A care robot may balance medication adherence, autonomy, and safety.
- The current schema does not require explicit goals.

### Decision Relevance

Purpose: identify distinctions that could change available actions, consequences, values, or evaluation judgments.

Questions:

- Which distinctions would affect downstream decision quality?
- Which distinctions are irrelevant to all plausible decisions?
- Which distinctions matter only under some goals?
- Does a refinement change decision-relevant structure or only naming/detail?

Example observations:

- Holding a key is decision-relevant for opening a door.
- A passenger's consent is decision-relevant for changing a ride.
- A student's religion may be scene context but not automatically a decision criterion.

### Representation Boundary

Purpose: state what the model is and is not trying to include.

Questions:

- What horizon is modeled?
- Which external parties are inside or outside the model?
- Which consequences are represented directly?
- Which details are deliberately abstracted away?

Example observations:

- A one-step benchmark may stop after one action even though the real world continues.
- A structural score may ignore payoff semantics.
- A situation model may include a few steps, not a complete story.

### Potential Ambiguities

Purpose: make underspecification explicit.

Questions:

- Which prompt phrases admit multiple interpretations?
- Which inferred entities are borderline?
- Which action capabilities are uncertain?
- Which outcome branches depend on facts not given?

Example observations:

- "May be inconsistent with policy" does not mean "is a violation."
- "Looks tired" does not determine medical risk.
- "No one came to the door" does not prove nobody is home.

### Representation Challenges

Purpose: record why a scenario is hard for the current representation or metrics.

Questions:

- Does the scenario require non-acting stakeholders?
- Does it require actor-relative beliefs?
- Does it require norms, institutions, or authority?
- Does it admit many valid granularities?
- Would a structurally larger model be more adequate or merely more complex?

Example observations:

- A jointly acting game stresses action-profile completeness.
- A hidden-information case stresses belief representation.
- A social allocation case stresses fairness criteria and scarcity.

## Speculation

The canvas may later become an annotation instrument, but it is currently only a research template.

## Open Questions

- Which canvas sections should become formal schema fields?
- Which sections should remain human-review notes?
- Can future metrics use this canvas without making evaluation too subjective?
- How many sections can be reliably annotated by independent reviewers?

