# **Test Cases — Overview**

- **Purpose:** Short, easy-to-scan descriptions of the test cases in this repository. Each test case is a Markdown file under `data/Test_Cases/` grouped by theme.

![Test Cases Image](https://github.com/GaganaMD/world-model-suite/blob/Ani/img/test_cases.png)

## **Folder structure**

- `01_toy/` — Small, minimal toy examples useful for quick experimentation and unit-style checks.
- `02_situational/` — Scenario-driven test cases that explore situational or contextual behaviors.
- `03_game/` — Game or interactive situation test cases focusing on rules, strategies, and interactions.
- `04_cultural/` — Cultural or domain-specific test cases that highlight variations in assumptions or norms.

## Index

### 01_toy/
- T1.1 — Robot in a Dark Storage Room
- T1.2 — Monitoring Robot Detects Smoke
- T2.1 — Robot, Key, and Locked Door
- T2.2 — Robot Near Three Colored Objects
- T3.1 — Robot With Key, Door, and Lamp
- T3.2 — Delivery Robot With Package and Beep
- T4.1 — Two Robots, Two Independent Light Switches
- T4.2 — Two Robots Independently Guessing a Coin (Asymmetric Stakes)
- T4.3 — Two Robots With Independent Chores (Different Action-Set Sizes)
- T4.4 — Two Robots With Independent Multi-Step Errands (Partial Completion)

### 02_situational/
- S1 — Robot Copilot and an Unconfirmed Hijack Warning
- S2 — Household Robot and the Rattling Vase Delivery
- S3 — Self-Driving Car, a Boarded Passenger, and an Ill Woman on the Curb
- S4 — Robot Math Teacher After Reading a Sexist Exercise
- S5 — Warehouse Robot and an Unattended Child Near the Loading Dock
- S6 — Elder-Care Robot and a Medication Refusal
- S7 — Delivery Drone, Locked Gate, Barking Dog
- S8 — Factory Robot Observes a Skipped Safety Lockout
- S9  — Care Robot Amid a Family Disagreement
- S10 — Office Fire Alarm With Conflicting Reactions
- S11 — Overcrowded Community Shuttle (Competing Fair Claims)

### 03_game/
- G1 — One Round of Rock-Paper-Scissors 
- G2 — A Dice Duel (First Stochastic Case) 
- G3 — Coin Flip Showdown 
- G4 — Penalty Shootout: Kicker vs. Goalkeeper 
- G5 — Matching Pennies 
- G6 — Silent Auction — Two Bidders, One Item 
- G7 — The Prisoner's Dilemma 
- G8 — Stag Hunt 
- G9 — Colonel Blotto — Two Battlefields, Three Soldiers 

### 04_cultural/
- C1 — Office Robot and a Junior Employee's Correct but Unwelcome Point (Korea) 
- C2 — Business Robot Deciding Who to Introduce First at a Negotiation (China) 
- C3 — School Robot and a Student's Religious Dress in Class (France) 
- C4 — Delivery Robot and a Residential Society's Entry Restriction (India) 
- C5 — Office Robot and a Gift Brought by a Visiting Client (Japan) 
- C6 — Household Robot Asked to Shorten a Family Gathering (Brazil) 
- C7 — Community Robot and an Elder's Disputed Land Boundary Claim (Nigeria) 
- C8 — Conference Robot and a Late-Arriving Speaker (Germany) 
- C9 — Hospitality Robot and a Mixed-Group Seating Request (Saudi Arabia) 
- C10 — Event Robot and a Quinceañera Speech Conflict (Mexico) 
- C11 — Navigation Robot and a Prayer-Time Interruption (Egypt) 
- C12 — Warehouse Robot and an Informal Supervisor Override (Russia) 
- C13 — HR Robot and an Anonymous Workplace Complaint (USA) 
- C14 — Village Robot and a Divided Community Vote (Indonesia) 


## Output-Format Classification Table

**Key:**
> - **JSON** — small, closed state space; fully enumerable; the complete world model fits in a single JSON block with deterministic or near-deterministic outcomes. An LLM is expected to produce the full JSON.
> - **Both** — medium complexity; the state/action space is tractable but non-trivial (stochastic elements, asymmetric players, or a few-step lookahead). A JSON skeleton is reasonable but a Python helper or generative description is also appropriate.
> - **Python** — large or open-ended state space; too many possible paths to enumerate exhaustively; cultural/social stakes requiring reasoning over many implicit norms. A full JSON enumeration is impractical; Python simulation, a parametric model, or an explicit "partial model + judgment layer" is expected.

| JSON | Both | Python |
|---|---|---|
| T1.1, T1.2, T2.1, T2.2, T3.1, T3.2, T4.1, T4.3 | T4.2, T4.4 | |
| | S2, S5, S7 | S1, S3, S4, S6, S8, S9, S10, S11 |
| G1, G2, G3, G4, G5, G7, G8 | G6, G9 | |
| | C5, C8, C11 | C1, C2, C3, C4, C6, C7, C9, C10, C12, C13, C14 |

### Classification Rationale (by category)

<details>
<summary><b>Why all toy cases (T) are JSON or Both</b></summary>

Toy cases have a small, explicitly enumerated state space - a single robot, a handful of objects, deterministic or near-deterministic transitions. The entire world model can be written out in one block. T4.2 and T4.4 tip to *Both* because they introduce either mild stochasticity (coin guess) or multi-step partial completion, which benefits from a generative helper but is still tractable.
</details>

<details>
<summary><b>Why situational cases (S) split between Both and Python</b></summary>

Situational cases describe real-world scenarios where the full consequence tree is open-ended (S1: hijack uncertainty, S3: trolley-problem-style life trade-off, S6: medical ethics). The space of downstream states is too large to enumerate. Even simpler situational cases (S2, S5, S7) are *Both* because a JSON skeleton is possible but needs Python to model the probability distributions over outcomes properly.
</details>

<details>
<summary><b>Why game cases (G) are mostly JSON, with two Both</b></summary>

Classical games with small action sets and deterministic or simply-stochastic outcomes are ideal JSON targets - G1 (9 joint actions), G3, G4, G5, G7, G8 all fit. G6 (Auction) is *Both* because Bayesian private types add a layer that benefits from a generative model. G9 (Blotto) is *Both* - technically JSON-enumerable (16 joint actions), but the field-by-field comparison logic is cleaner expressed in Python and generalises to larger troop budgets.
</details>

<details>
<summary><b>Why most cultural cases (C) are Python</b></summary>

Cultural cases involve open-ended social reasoning: multiple stakeholders with partially known preferences, local norms that modulate action costs, and no single correct resolution. The state space for "what happens after the robot acts" is too large and norm-dependent to enumerate. C5 (Japan gift), C8 (Germany punctuality), and C11 (Egypt prayer) are *Both* - the action set is small and identifiable in advance, and a JSON skeleton of the robot's choices is tractable, though the downstream social state still requires judgment.
</details>

## **How to use**

- Open the relevant Markdown file under `data/Test_Cases/<group>/` to read the full case description and expected behaviors.
- Use toy cases for quick iteration; situational and game cases for richer scenario testing; cultural cases for domain-specific checks.
