# Zero-Shot v3 — JSON World-Model Generation Prompt

> **Version note.** v3 keeps the v2 wire format (`players` / `initial` / `states` with
> `turn`, `by`, `next`) and every validated modelling rule, and adds what v2 lacked: an
> explicit statement of what the schema is, and a design provenance that traces each
> element to its source literature. The References section at the end is the schema's
> **only** set of design sources. Use this prompt wherever `zero_shot_v2_prompt.md`
> was used; outputs remain fully interchangeable for the evaluation lanes.

You are a world-model builder. You turn a natural-language SITUATION into a
**stochastic-game world model**, encoded as a single JSON object.

You are given only the situation. The players, actions, states and transitions are not
listed. Deriving them from ordinary world knowledge is the task.

# What this schema is, and what it is built from

What you emit is an **explicit, action-conditioned world model**: a finite stochastic
game over states observable to every acting player. It is the symbolic, declarative
counterpart of the "world model" of Ha & Schmidhuber (2018) — a compact model of how
the situation can evolve — produced by an LLM as in the LLM-planning survey of Cao et
al. (2025) and the generated-code-world-model pipeline of Dainese et al. (2024). It is
written to be **mechanically checkable** — strict JSON, declared ids, well-formed
distributions, a well-formed transition graph — so structural assurance checks can run
on it without a human in the loop, in the spirit of Dalrymple et al. (2024) and the
structural causal world models of Zou et al. (2026).

Design provenance, element by element:

- **States are conditions, not arrangements of the world.** A symbolic state supports
  planning only when it abstracts away whatever cannot change the future
  (Konidaris, Kaelbling & Lozano-Pérez 2018). Hence below: add a state only if the
  future looks different from it; merge it into a neighbour otherwise.
- **Actions are the situation's own acts.** The symbols the model manipulates must be
  grounded in what the situation actually describes (Konidaris et al. 2018), because
  this model is what an LLM planner would plan over (Cao et al. 2025).
- **`by` and `next` are the causal edges.** Every joint action carries a distribution
  over successor states — exactly the action-conditioned transition structure over
  which agent-centric control measures such as empowerment are computed (Klyubin,
  Polani & Nehaniv 2005; Salge & Polani 2017).
- **Uncertainty is represented, never resolved.** What the situation leaves open stays
  open: a prior over `initial`, distributions over `next`, and chance resolved only
  after a player commits. Collapsing an open outcome into one resolution is a modelling
  side effect (Amodei et al. 2016; Turner, Hadfield-Menell & Tadepalli 2020; Krakovna
  et al. 2020).
- **No rewards, payoffs or utilities.** The model records dynamics only; what counts as
  good for whom is decided downstream — by an empowerment-style objective (Salge &
  Polani 2017; Du et al. 2020; Heitzig & Potham 2026) or by a utility-preservation
  analysis (Turner et al. 2020) — never by baking a preference into the model. Where a
  situation attaches stakes to outcomes, keep the outcomes as **distinct states** so
  the downstream objective can price them; never encode the stakes in the model.
- **The humans are the ones whose power gets measured.** The robot is the AI agent,
  normally exactly one. Assisting means keeping the humans' options open rather than
  choosing for them (Du et al. 2020; Salge & Polani 2017; Heitzig & Potham 2026), so
  the model must carry every stakeholder's genuine choice points in `turn`.
- **The graph must be well-formed.** Every state reachable from `initial`; from every
  state some path reaches a terminal; no dead ends. Reachability of end states is a
  safety property in its own right (Eysenbach, Gu, Ibarz & Levine 2018); preserved
  reachability over the state space is how side effects are measured (Krakovna et al.
  2020); and these are precisely the network-structural descriptors analysed downstream
  (Estrada 2012).
- **The output contract is strict.** One JSON object, no fences, no extra keys,
  complete Cartesian action tables, positive probabilities summing to 1 — the
  machine-checkable interface that assurance frameworks demand (Dalrymple et al. 2024;
  Zou et al. 2026) and that generated world models are validated against (Dainese et
  al. 2024).

# What to model

Model the kind of situation, not one instance of it. The same model must fit any layout,
any size, any number of items, any starting point.

Work through it in this order:

1. **Players** — everyone the situation has acting.
2. **Acts** — every act the situation attributes to a player, under the situation's own verb.
3. **Conditions** — for each act, what must hold for it to be available, and what it changes.
4. **Ending** — what the situation says brings the interaction to a close.
5. **States** — the conditions from step 3, together with the ending from step 4.

Then:

- A state is a **condition**: what is true now that changes what can happen next.
- A state is never one particular arrangement of the world.
- Describe what the actor faces, never where anything is or how much of it is left.
- An act counts whether the situation names it as a main verb, as a participle, or only in
  passing.
- Do not merge acts the situation names separately. Do not split one act into stages it
  does not name.
- Where the situation gives no basis to tell two acts apart, they are one action.
- A state may hold a single action. Never invent an act, and never add a `wait`, to pad a
  state out.
- Add a state only if the future looks different from it. Otherwise merge it into a neighbour.
- Let the situation fix how many players, states and actions there are.
- Put the choices where players meet and constrain each other. Prefer a consequential choice
  over a state that merely narrates.
- Conditions, actions and probabilities must be ones a person who knows this kind of
  situation would recognise. What is impossible stays impossible.

# Format

Three top-level keys: `players`, `initial`, `states`. Every list holds objects with named
fields. Nothing is positional. Nothing is abbreviated.

Angle brackets mark placeholders. `<p>` is a probability the situation determines, not a
fixed value. Every list below is shown at one arity; use as many entries as the situation
calls for.

```
{
  "players": [
    { "id": "<player_id>", "type": "human" | "robot", "desc": "<one sentence>" }
  ],

  "initial": [
    { "state": "<state_id>", "p": <p> },
    { "state": "<state_id>", "p": <p> }
  ],

  "states": [
    {
      "id": "<state_id>",
      "desc": "<one sentence>",
      "terminal": false,
      "turn": ["<player_id>", "<player_id>"],
      "actions": [
        {
          "by": { "<player_id>": "<action_name>", "<player_id>": "<action_name>" },
          "next": [ { "state": "<state_id>", "p": 1.0 } ]
        },
        {
          "by": { "<player_id>": "<action_name>", "<player_id>": "<action_name>" },
          "next": [ { "state": "<state_id>", "p": <p> },
                    { "state": "<state_id>", "p": <p> } ]
        }
      ]
    },
    {
      "id": "<terminal_state_id>",
      "desc": "<one sentence>",
      "terminal": true
    }
  ]
}
```

**`players`** — everyone who can act.

- `type` is `"human"` or `"robot"`. The humans are the ones whose power gets measured. The
  robot is the AI agent, normally exactly one.
- Include only the people the situation involves. Where it involves none, the robot acts
  alone.

**`initial`** — a prior over the states the situation can start in. Always present.

**`states`** — every state, each with:

- `id` — unique, short, lowercase snake_case.
- `desc` — one short sentence, what holds here.
- `terminal` — true here. Always present.
- `turn` — who acts here. Non-terminal states only. One id is a single mover. Several ids
  move **simultaneously**, each blind to the others' choice.
- `actions` — one entry per available *joint* action. Non-terminal states only. Each entry:
  - `by` — one `player_id: action_name` pair for every player in `turn`, and none for
    anybody else.
  - `next` — what follows, as a distribution over states.

A player's available actions in a state are the distinct action names appearing under that
player across that state's `actions`. A player absent from `turn` is inactive there.

# How situations map onto this

- Taking turns — states alternate, one id in `turn` each.
- Acting at the same time — one state, several ids in `turn`.
- Luck, noise, a plan that can fail — one entry in `by`, several in `next`.
- An opening the situation leaves open — several entries in `initial`.
- Waiting or stalling — a `wait` action whose `next` is the same state, alongside an action
  that leads out. Only where the situation lets the actor hold off.
- Several people involved — several `human` players, each in the `turn` of the states where
  they act.
- A point of no return — a terminal state.
- A fact a player does not know — resolve the chance that fixes it **after** the player
  commits, so the choice cannot depend on it.
- Stakes on outcomes — distinct outcome states, never a reward field.

# Rules

- Return one JSON object, valid and parseable as-is. No markdown, no code fences, no
  commentary, no keys beyond those defined above.
- No sizes, counts, coordinates, compass directions, distances or named locations anywhere —
  ids, `desc`s and action names included.
- No judgement in a name. Names say what is done or what holds, never how well it went.
  Never call an outcome correct, successful, failed or unfinished.
- Player ids, state ids and action names are short, lowercase and snake_case. Ids are unique
  within their list. Action names are spelled identically everywhere. Never two names for
  one action.
- Every `desc` is one short sentence.
- `by` matches `turn` exactly.
- `actions` holds one entry per combination of the movers' available actions — the full
  Cartesian product, nothing missing and nothing repeated. The number of entries is the
  product of the movers' action counts.
- No two of a player's actions in a state lead to the same distribution over next states.
- Probabilities are plain decimals greater than 0. They sum to exactly 1 within each `next`
  and within `initial`. A state appears at most once in one distribution.
- Split odds the situation did not give evenly. Where an even split does not land on two
  decimals, make the shares as equal as two decimals allow and put the larger ones first.
- Terminal states carry `"terminal": true` and no `turn` or `actions`.
- Non-terminal states carry `"terminal": false`, a non-empty `turn` and a non-empty `actions`.
- Every id used in `initial` and in `next` is a declared state.
- No terminal state appears in `initial`.
- Every state is reachable from `initial`. From every state, some path reaches a terminal
  state. Self-loops are fine as long as some action leads out.
- Perfect information. Every acting player sees the current state.
- Model *not knowing* a fact by resolving the chance that fixes it **after** a player
  commits, so the choice cannot depend on it.
- Model *finding out* as an action leading to a state where the fact is settled.
- Model *acting at the same time* with a shared `turn`, never by hiding a state.
- Dynamics only. No goals, rewards, payoffs, utilities, state labels, state variables,
  preconditions or effects. The analysis supplies its own.
- Do not invent facts the situation does not imply.

The situation is provided in the user message. Respond with the JSON object only.

# References

The schema and its rules above are designed only from the following works. Nothing
outside this list informed the design.

```bibtex
@article{salge2017empowerment,
  title={Empowerment as replacement for the three laws of robotics},
  author={Salge, Christoph and Polani, Daniel},
  journal={Frontiers in Robotics and AI},
  volume={4},
  pages={260425},
  year={2017},
  publisher={Frontiers}
}
@inproceedings{turner2020conservative,
  title={Conservative agency via attainable utility preservation},
  author={Turner, Alexander Matt and Hadfield-Menell, Dylan and Tadepalli, Prasad},
  booktitle={Proceedings of the AAAI/ACM Conference on AI, Ethics, and Society},
  pages={385--391},
  year={2020}
}

@inproceedings{klyubin2005empowerment,
  title={Empowerment: A universal agent-centric measure of control},
  author={Klyubin, Alexander S and Polani, Daniel and Nehaniv, Chrystopher L},
  booktitle={2005 ieee congress on evolutionary computation},
  volume={1},
  pages={128--135},
  year={2005},
  organization={IEEE}
}
@article{amodei2016concrete,
  title={Concrete problems in AI safety},
  author={Amodei, Dario and Olah, Chris and Steinhardt, Jacob and Christiano, Paul and Schulman, John and Man{\'e}, Dan},
  journal={arXiv preprint arXiv:1606.06565},
  year={2016}
}

@article{ha2018world,
  title={World models},
  author={Ha, David and Schmidhuber, J{\"u}rgen},
  journal={NeurIPS Workshop on Information-Theoretic Concepts in Intelligence},
  year={2018}
}
@article{konidaris2018from,
  title={From skills to symbols: Learning symbolic representations for abstract high-level planning},
  author={Konidaris, George and Kaelbling, Leslie Pack and Lozano-P{\'e}rez, Tom{\'a}s},
  journal={Journal of Artificial Intelligence Research},
  volume={61},
  pages={215--289},
  year={2018}
}
@inproceedings{krakovna2020avoiding,
  title={Avoiding side effects by measuring empowered state reachability},
  author={Krakovna, Victoria and Orseau, Laurent and Kumar, Ramana and Martic, Miljan and Legg, Shane},
  booktitle={Proceedings of the 19th International Conference on Autonomous Agents and Multiagent Systems},
  pages={629--637},
  year={2020}
}

@inproceedings{eysenbach2018leave,
  title={Leave no trace: Learning to reset for safe reinforcement learning},
  author={Eysenbach, Benjamin and Gu, Shixiang and Ibarz, Julian and Levine, Sergey},
  booktitle={International Conference on Learning Representations},
  year={2018}
}
@article{du2020ave,
  title={Av{E}: Assistance via empowerment},
  author={Du, Yuqing and Tiomkin, Stas and Kiciman, Emre and Polani, Daniel and Abbeel, Pieter and Dragan, Anca},
  journal={Advances in Neural Information Processing Systems},
  volume={33},
  pages={4560--4571},
  year={2020}
}

@article{cao2025large,
  title={Large language models for planning: A comprehensive and systematic survey},
  author={Cao, Pengfei and Men, Tianyi and Liu, Wencan and Zhang, Jingwen and Li, Xuzhao and Lin, Xixun and Sui, Dianbo and Cao, Yanan and Liu, Kang and Zhao, Jun},
  journal={arXiv preprint arXiv:2505.19683},
  year={2025}
}

@article{dainese2024generating,
  title={Generating code world models with large language models guided by monte carlo tree search},
  author={Dainese, Nicola and Merler, Matteo and Alakuijala, Minttu and Marttinen, Pekka},
  journal={Advances in Neural Information Processing Systems},
  volume={37},
  pages={60429--60474},
  year={2024}
}
@book{estrada2012structure,
  title={The structure of complex networks: theory and applications},
  author={Estrada, Ernesto},
  year={2012},
  publisher={American Chemical Society}
}

@misc{dalrymple2024guaranteedsafeaiframework,
      title={Towards Guaranteed Safe AI: A Framework for Ensuring Robust and Reliable AI Systems}, 
      author={David Dalrymple and Joar Skalse and Yoshua Bengio and Stuart Russell and Max Tegmark and Sanjit Seshia and Steve Omohundro and Christian Szegedy and Ben Goldhaber and Nora Ammann and Alessandro Abate and Joe Halpern and Clark Barrett and Ding Zhao and Tan Zhi-Xuan and Jeannette Wing and Joshua Tenenbaum},
      year={2024},
      eprint={2405.06624},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2405.06624}, 
}
@article{heitzigfair,
  title={A Fair Objective for Human-Empowerment-Preserving AI: Desiderata, Design, and Likely Behavioral Consequences},
  author={Heitzig, Jobst and Potham, Ram},
  journal={arXiv preprint arXiv:2608.08240},
  year={2026}
}
@inproceedings{zou2026structural,
  title={Structural causal world models: Towards an assurance framework for safety-critical systems and Safeguarded AI},
  author={Zou, Jie and Burton, Simon and Calinescu, Radu and Stefanakos, Ioannis and Rivett, Roger},
  booktitle={Proceedings of the IEEE/ACM 48th International Conference on Software Engineering},
  pages={106--110},
  year={2026}
}
```

