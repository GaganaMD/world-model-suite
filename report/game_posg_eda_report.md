# Game POSG World-Model EDA

## Experiment

This report applies `WorldModelEDA` to the complete expected-output POSG schemas in the
current game benchmark. The repository currently contains **nine** game cases (G1-G9), not
ten. The analysis is descriptive: it enumerates the declared finite state/action/transition
structure and does not score whether the generated model is semantically correct.

Each case is loaded from its Markdown expected-output JSON. For every state reachable in the
declared schema, the experiment builds a directed state graph and a state-action-transition
graph, then calculates action branching, transition stochasticity and entropy, terminal
distance, and graph connectivity.

## Cross-case results

| Case and game | States | Terminal | Joint actions | Avg. branch | Stochastic | Avg. entropy (bits) | Max depth | SCCs | Avg. path |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| G1 — One Round of Rock-Paper-Scissors | 4 | 3 | 9 | 2.25 | 0% | 0.000 | 1 | 4 | 1.00 |
| G2 — A Dice Duel (First Stochastic Case) | 4 | 3 | 1 | 0.25 | 100% | 1.483 | 1 | 4 | 1.00 |
| G3 — Coin Flip Showdown | 4 | 3 | 4 | 1.00 | 50% | 0.500 | 1 | 4 | 1.00 |
| G4 — Penalty Shootout (Kicker vs. Goalkeeper) | 3 | 2 | 9 | 3.00 | 0% | 0.000 | 1 | 3 | 1.00 |
| G5 — Matching Pennies | 3 | 2 | 4 | 1.33 | 0% | 0.000 | 1 | 3 | 1.00 |
| G6 — Silent Auction — Two Bidders, One Item | 6 | 4 | 5 | 0.83 | 20% | 0.200 | 2 | 6 | 1.29 |
| G7 — The Prisoner's Dilemma | 5 | 4 | 4 | 0.80 | 0% | 0.000 | 1 | 5 | 1.00 |
| G8 — Stag Hunt | 5 | 4 | 4 | 0.80 | 0% | 0.000 | 1 | 5 | 1.00 |
| G9 — Colonel Blotto — Two Battlefields, Three Soldiers | 5 | 4 | 16 | 3.20 | 0% | 0.000 | 1 | 5 | 1.00 |

![Cross-case comparison](game_posg_eda_graphs/game_case_comparison.png)

## Structural observations

- **One-step games dominate:** G1-G5 and G7-G9 transition directly from a single decision
  state to terminal outcomes. Their maximum terminal depth is one, and every state is its own
  strongly connected component, confirming that the schemas contain no cycles.
- **G6 is the only multi-step model:** equal bids route to a non-terminal tie-break state,
  then a stochastic Nature action selects a winner. It therefore has maximum terminal depth
  two and is the only case with a non-terminal transition after the initial joint action.
- **Stochasticity is localized:** G2 (dice duel) is stochastic at its only action; G3 is
  stochastic only for mismatched calls; and G6 is stochastic only at the tie-break. The
  remaining six cases are deterministic.
- **Outcome compression exposes action redundancy:** RPS (G1) maps nine joint actions to
  three outcomes, while Colonel Blotto (G9) maps sixteen allocations to four declared outcome
  classes. This is structural redundancy, not an error: distinct strategic choices can share
  an outcome state.
- **The report measures declared structure:** state labels collapse strategically distinct
  histories when the supplied schema uses a common outcome state. Use the state-action graph
  and reward metadata alongside this report for strategic interpretation.

## Case reference

This section links the metrics to the actual declared model. `Initial` identifies the reset
state; `terminal` identifies a state with no further decision in the schema. The terminal
distance is the shortest number of transitions from that state to any terminal state.

### G1 — One Round of Rock-Paper-Scissors

**Players:** `player_1` (The first person playing the round), `player_2` (The second person playing the round).
**Transition character:** deterministic for every declared state-action pair.
**Reward placement:** state-action pairs.
**Structural reading:** 4 states, 9
declared joint actions, 0.333 outcome compression, and
4 strongly connected components.

| State | Role | Declared meaning | Shortest terminal distance |
| --- | --- | --- | ---: |
| `s0` | initial | Both players are about to reveal their choice; nothing thrown yet. | 1 |
| `s1` | terminal | Player 1 wins the round. | 0 |
| `s2` | terminal | Player 2 wins the round. | 0 |
| `s3` | terminal | The round is a draw because both players chose the same. | 0 |

**Available actions**
- **`s0`:** `player_1`: `rock`, `paper`, `scissors`; `player_2`: `rock`, `paper`, `scissors`. This creates **9 joint actions**.


### G2 — A Dice Duel (First Stochastic Case)

**Players:** `player_1` (The first player, rolling one die), `player_2` (The second player, rolling one die).
**Transition character:** stochastic for every declared state-action pair (mean entropy 1.483 bits).
**Reward placement:** outcome states (reward-on-arrival).
**Structural reading:** 4 states, 1
declared joint actions, 1.000 outcome compression, and
4 strongly connected components.

| State | Role | Declared meaning | Shortest terminal distance |
| --- | --- | --- | ---: |
| `s0` | initial | Both players are about to roll; no dice rolled yet. | 1 |
| `s1` | terminal | Player 1 rolled higher and wins the round. | 0 |
| `s2` | terminal | Player 2 rolled higher and wins the round. | 0 |
| `s3` | terminal | Both rolled the same number; the round is a tie. | 0 |

**Available actions**
- **`s0`:** `player_1`: `roll`; `player_2`: `roll`. This creates **1 joint action**.


### G3 — Coin Flip Showdown

**Players:** `player_1` (The first player, who calls a face before the flip), `player_2` (The second player, who calls a face before the flip).
**Transition character:** mixed: 50% of declared state-action pairs are stochastic (mean entropy 0.500 bits).
**Reward placement:** outcome states (reward-on-arrival).
**Structural reading:** 4 states, 4
declared joint actions, 0.500 outcome compression, and
4 strongly connected components.

| State | Role | Declared meaning | Shortest terminal distance |
| --- | --- | --- | ---: |
| `s0` | initial | Both players are about to call; coin not yet flipped. | 1 |
| `s1` | terminal | Player 1's call matched the coin result; player 1 wins. | 0 |
| `s2` | terminal | Player 2's call matched the coin result; player 2 wins. | 0 |
| `s3` | terminal | Both calls matched (or neither did); the round is a draw. | 0 |

**Available actions**
- **`s0`:** `player_1`: `heads`, `tails`; `player_2`: `heads`, `tails`. This creates **4 joint actions**.


### G4 — Penalty Shootout (Kicker vs. Goalkeeper)

**Players:** `kicker` (The player taking the penalty kick), `goalkeeper` (The player defending the goal).
**Transition character:** deterministic for every declared state-action pair.
**Reward placement:** state-action pairs.
**Structural reading:** 3 states, 9
declared joint actions, 0.222 outcome compression, and
3 strongly connected components.

| State | Role | Declared meaning | Shortest terminal distance |
| --- | --- | --- | ---: |
| `s0` | initial | Both players are deciding simultaneously; kick not yet taken. | 1 |
| `s1` | terminal | The kick goes in; kicker scores. | 0 |
| `s2` | terminal | The goalkeeper blocks the kick; no goal. | 0 |

**Available actions**
- **`s0`:** `kicker`: `shoot_left`, `shoot_center`, `shoot_right`; `goalkeeper`: `dive_left`, `stay_center`, `dive_right`. This creates **9 joint actions**.


### G5 — Matching Pennies

**Players:** `player_1` (The player who wins when faces match), `player_2` (The player who wins when faces differ).
**Transition character:** deterministic for every declared state-action pair.
**Reward placement:** state-action pairs.
**Structural reading:** 3 states, 4
declared joint actions, 0.500 outcome compression, and
3 strongly connected components.

| State | Role | Declared meaning | Shortest terminal distance |
| --- | --- | --- | ---: |
| `s0` | initial | Both players are about to reveal their penny; nothing shown yet. | 1 |
| `s1` | terminal | Both pennies show the same face; Player 1 keeps both coins. | 0 |
| `s2` | terminal | Pennies show different faces; Player 2 keeps both coins. | 0 |

**Available actions**
- **`s0`:** `player_1`: `heads`, `tails`; `player_2`: `heads`, `tails`. This creates **4 joint actions**.


### G6 — Silent Auction — Two Bidders, One Item

**Players:** `bidder_1` (The first bidder, with private value unknown to bidder 2), `bidder_2` (The second bidder, with private value unknown to bidder 1).
**Transition character:** mixed: 20% of declared state-action pairs are stochastic (mean entropy 0.200 bits).
**Reward placement:** outcome states (reward-on-arrival).
**Structural reading:** 6 states, 5
declared joint actions, 0.800 outcome compression, and
6 strongly connected components.

| State | Role | Declared meaning | Shortest terminal distance |
| --- | --- | --- | ---: |
| `s0` | initial | Both bidders are preparing their sealed bids; no bids submitted yet. | 1 |
| `s1` | terminal | Bidder 1 submitted the higher bid and wins the item. | 0 |
| `s2` | terminal | Bidder 2 submitted the higher bid and wins the item. | 0 |
| `s3` | decision | Both bids are equal; a coin flip decides the winner. | 1 |
| `s4` | terminal | Tie broken: Bidder 1 wins the item. | 0 |
| `s5` | terminal | Tie broken: Bidder 2 wins the item. | 0 |

**Available actions**
- **`s0`:** `bidder_1`: `bid_low`, `bid_high`; `bidder_2`: `bid_low`, `bid_high`. This creates **4 joint actions**.
- **`s3`:** `nature`: `flip`. This creates **1 joint action**.


### G7 — The Prisoner's Dilemma

**Players:** `suspect_1` (The first suspect, deciding in isolation), `suspect_2` (The second suspect, deciding in isolation).
**Transition character:** deterministic for every declared state-action pair.
**Reward placement:** state-action pairs.
**Structural reading:** 5 states, 4
declared joint actions, 1.000 outcome compression, and
5 strongly connected components.

| State | Role | Declared meaning | Shortest terminal distance |
| --- | --- | --- | ---: |
| `s0` | initial | Both suspects are deciding simultaneously in separate rooms; no decision made yet. | 1 |
| `s1` | terminal | Both stayed silent; each receives a light sentence. | 0 |
| `s2` | terminal | Both testified; each receives a heavy sentence. | 0 |
| `s3` | terminal | Suspect 1 testified, suspect 2 stayed silent; suspect 1 goes free, suspect 2 gets maximum sentence. | 0 |
| `s4` | terminal | Suspect 2 testified, suspect 1 stayed silent; suspect 2 goes free, suspect 1 gets maximum sentence. | 0 |

**Available actions**
- **`s0`:** `suspect_1`: `silent`, `testify`; `suspect_2`: `silent`, `testify`. This creates **4 joint actions**.


### G8 — Stag Hunt

**Players:** `hunter_1` (The first hunter choosing their quarry), `hunter_2` (The second hunter choosing their quarry).
**Transition character:** deterministic for every declared state-action pair.
**Reward placement:** state-action pairs.
**Structural reading:** 5 states, 4
declared joint actions, 1.000 outcome compression, and
5 strongly connected components.

| State | Role | Declared meaning | Shortest terminal distance |
| --- | --- | --- | ---: |
| `s0` | initial | Both hunters are deciding independently what to hunt; no choice made yet. | 1 |
| `s1` | terminal | Both hunted stag; they cooperate successfully and both eat well. | 0 |
| `s2` | terminal | Hunter 1 hunted stag alone; hunter 2 hunted hare. Hunter 1 gets nothing, hunter 2 catches a hare. | 0 |
| `s3` | terminal | Hunter 2 hunted stag alone; hunter 1 hunted hare. Hunter 2 gets nothing, hunter 1 catches a hare. | 0 |
| `s4` | terminal | Both hunted hare independently; each catches one hare. | 0 |

**Available actions**
- **`s0`:** `hunter_1`: `hunt_stag`, `hunt_hare`; `hunter_2`: `hunt_stag`, `hunt_hare`. This creates **4 joint actions**.


### G9 — Colonel Blotto — Two Battlefields, Three Soldiers

**Players:** `commander_1` (The first commander allocating three soldiers), `commander_2` (The second commander allocating three soldiers).
**Transition character:** deterministic for every declared state-action pair.
**Reward placement:** state-action pairs.
**Structural reading:** 5 states, 16
declared joint actions, 0.250 outcome compression, and
5 strongly connected components.

| State | Role | Declared meaning | Shortest terminal distance |
| --- | --- | --- | ---: |
| `s0` | initial | Both commanders are allocating soldiers simultaneously; no deployment yet. | 1 |
| `s1` | terminal | Commander 1 wins the overall engagement (wins more battlefields). | 0 |
| `s2` | terminal | Commander 2 wins the overall engagement. | 0 |
| `s3` | terminal | Each commander wins exactly one battlefield; draw. | 0 |
| `s4` | terminal | Both commanders tie on both battlefields (equal allocations on each); overall draw. | 0 |

**Available actions**
- **`s0`:** `commander_1`: `0+3`, `1+2`, `2+1`, `3+0`; `commander_2`: `0+3`, `1+2`, `2+1`, `3+0`. This creates **16 joint actions**.



## Graph artifacts

The files below use an initial-state/terminal-state color system and aggregate parallel
state transitions into edge labels showing joint-action count and probability mass. This keeps
the diagrams readable for sharing while preserving the full action-level representation in
the EDA object.

| Case | State-transition graph |
| --- | --- |
| G1 — One Round of Rock-Paper-Scissors | ![G1 graph](game_posg_eda_graphs/g1_state_graph.png) |
| G2 — A Dice Duel (First Stochastic Case) | ![G2 graph](game_posg_eda_graphs/g2_state_graph.png) |
| G3 — Coin Flip Showdown | ![G3 graph](game_posg_eda_graphs/g3_state_graph.png) |
| G4 — Penalty Shootout (Kicker vs. Goalkeeper) | ![G4 graph](game_posg_eda_graphs/g4_state_graph.png) |
| G5 — Matching Pennies | ![G5 graph](game_posg_eda_graphs/g5_state_graph.png) |
| G6 — Silent Auction — Two Bidders, One Item | ![G6 graph](game_posg_eda_graphs/g6_state_graph.png) |
| G7 — The Prisoner's Dilemma | ![G7 graph](game_posg_eda_graphs/g7_state_graph.png) |
| G8 — Stag Hunt | ![G8 graph](game_posg_eda_graphs/g8_state_graph.png) |
| G9 — Colonel Blotto — Two Battlefields, Three Soldiers | ![G9 graph](game_posg_eda_graphs/g9_state_graph.png) |

## Reproduction

```powershell
python report\generate_game_eda_report.py
python -m unittest tests.test_world_model_eda
```

`report\generate_game_eda_report.py` discovers G1-G9 from
`data\Test_Cases\03_game`, extracts each expected JSON object, regenerates the PNG figures,
and overwrites this report. The analysis implementation is in `world_model_eda\eda.py`.
