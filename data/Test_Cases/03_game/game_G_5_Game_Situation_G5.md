## Game Situation G.5: Matching Pennies

### LLM Input

Two players each secretly place a penny on a table, choosing heads or tails. They reveal simultaneously. If both show the same face, Player 1 keeps both coins; if they differ, Player 2 keeps both.

### Expected LLM Output

This is the **pure matching-pennies** game — a canonical two-player zero-sum simultaneous game with deterministic outcomes. The prompt explicitly states the payoff rule (same face → P1 wins both; different face → P2 wins both), so the reward structure is given. Rewards live on (state, joint action) pairs.

```json
{
  "players": [
    { "id": "player_1", "description": "The player who wins when faces match" },
    { "id": "player_2", "description": "The player who wins when faces differ" }
  ],
  "initial_state": "s0",
  "states": {
    "s0": { "description": "Both players are about to reveal their penny; nothing shown yet.", "terminal": false },
    "s1": { "description": "Both pennies show the same face; Player 1 keeps both coins.", "terminal": true },
    "s2": { "description": "Pennies show different faces; Player 2 keeps both coins.", "terminal": true }
  },
  "actions": {
    "s0": {
      "player_1": ["heads", "tails"],
      "player_2": ["heads", "tails"]
    }
  },
  "transition_probabilities": {
    "s0": {
      "heads+heads": { "s1": 1.0 },
      "heads+tails": { "s2": 1.0 },
      "tails+heads": { "s2": 1.0 },
      "tails+tails": { "s1": 1.0 }
    }
  },
  "rewards": {
    "s0": {
      "heads+heads": { "player_1": 1, "player_2": -1 },
      "heads+tails": { "player_1": -1, "player_2": 1 },
      "tails+heads": { "player_1": -1, "player_2": 1 },
      "tails+tails": { "player_1": 1, "player_2": -1 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* exactly two players with **asymmetric winning conditions** — P1 wins on match, P2 wins on mismatch;
* two actions each — heads, tails — revealed simultaneously;
* four joint-action keys covering all combinations;
* deterministic transitions (no randomness — the pennies are placed, not flipped);
* zero-sum rewards consistent with the stated rule: the winner collects the loser's coin, so ±1 or ±2 are both acceptable as long as they are zero-sum;
* no draw state — every outcome is decisive in this game.

A good answer should NOT include:

* a draw or tie state — the prompt's rule always produces a winner;
* treating this as stochastic (e.g. adding a probability for the penny "landing");
* symmetric winning conditions (both players winning on match) — that would contradict the stated rule;
* inventing stake amounts beyond one coin per player, or a story.
