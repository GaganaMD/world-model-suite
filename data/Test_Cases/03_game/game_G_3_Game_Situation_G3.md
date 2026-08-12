## Game Situation G.3: Coin Flip Showdown

### LLM Input

Two players each call heads or tails before a single fair coin is flipped. The player whose call matches the result wins; if both match or neither matches, the round is a draw.

### Expected LLM Output

This game is **two-stage**: players choose simultaneously (call heads or tails), then a random event (the flip) determines the outcome. Rewards attach to outcome states (reward-on-arrival) because the coin flip is stochastic, not chosen.

The coin has probability 0.5 of landing heads and 0.5 of landing tails. For each joint call:
- If both players called the same face: both are right or both are wrong together → always a draw (1.0 → s_draw).
- If players called different faces: exactly one will match the coin → 0.5 chance each wins.

```json
{
  "players": [
    { "id": "player_1", "description": "The first player, who calls a face before the flip" },
    { "id": "player_2", "description": "The second player, who calls a face before the flip" }
  ],
  "initial_state": "s0",
  "states": {
    "s0": { "description": "Both players are about to call; coin not yet flipped.", "terminal": false },
    "s1": { "description": "Player 1's call matched the coin result; player 1 wins.", "terminal": true, "reward": { "player_1": 1, "player_2": -1 } },
    "s2": { "description": "Player 2's call matched the coin result; player 2 wins.", "terminal": true, "reward": { "player_1": -1, "player_2": 1 } },
    "s3": { "description": "Both calls matched (or neither did); the round is a draw.", "terminal": true, "reward": { "player_1": 0, "player_2": 0 } }
  },
  "actions": {
    "s0": {
      "player_1": ["heads", "tails"],
      "player_2": ["heads", "tails"]
    }
  },
  "transition_probabilities": {
    "s0": {
      "heads+heads": { "s3": 1.0 },
      "tails+tails": { "s3": 1.0 },
      "heads+tails": { "s1": 0.5, "s2": 0.5 },
      "tails+heads": { "s1": 0.5, "s2": 0.5 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* exactly two symmetric players, each making a call before the flip;
* two actions each — heads, tails — chosen simultaneously;
* correct treatment of **two sources of structure**: the players' choices AND the random coin — not collapsing them into one;
* the key insight that matching calls always resolve to a draw (probability-1 transition to draw state), while opposing calls resolve 50/50 to either player winning;
* zero-sum payoffs on outcome states (reward-on-arrival), not on the action pair;
* three terminal outcome states: player 1 wins, player 2 wins, draw.

A good answer should NOT include:

* treating the coin flip as a chosen action (e.g. "player_3: coin" or a third actor);
* assigning 0.5/0.5 to all four joint actions regardless of whether calls match;
* omitting the draw case for matching calls;
* inventing stakes, bet amounts, or a best-of-N framing the prompt never states;
* a story.
