## Game Situation G.1: One Round of Rock-Paper-Scissors

### LLM Input

Two people sit down to play a single round of rock-paper-scissors.

### Expected LLM Output

The ±1 / 0 reward scale is a modeling choice; any consistent zero-sum scheme is fine. This
game is deterministic *given the joint action*, so reward stays on the (state, joint action)
pair as in Levels 1–4.

```json
{
  "players": [
    { "id": "player_1", "description": "The first person playing the round" },
    { "id": "player_2", "description": "The second person playing the round" }
  ],
  "initial_state": "s0",
  "states": {
    "s0": { "description": "Both players are about to reveal their choice; nothing thrown yet.", "terminal": false },
    "s1": { "description": "Player 1 wins the round.", "terminal": true },
    "s2": { "description": "Player 2 wins the round.", "terminal": true },
    "s3": { "description": "The round is a draw (both chose the same).", "terminal": true }
  },
  "actions": {
    "s0": {
      "player_1": ["rock", "paper", "scissors"],
      "player_2": ["rock", "paper", "scissors"]
    }
  },
  "transition_probabilities": {
    "s0": {
      "rock+rock": { "s3": 1.0 },
      "rock+paper": { "s2": 1.0 },
      "rock+scissors": { "s1": 1.0 },
      "paper+rock": { "s1": 1.0 },
      "paper+paper": { "s3": 1.0 },
      "paper+scissors": { "s2": 1.0 },
      "scissors+rock": { "s2": 1.0 },
      "scissors+paper": { "s1": 1.0 },
      "scissors+scissors": { "s3": 1.0 }
    }
  },
  "rewards": {
    "s0": {
      "rock+rock": { "player_1": 0, "player_2": 0 },
      "rock+paper": { "player_1": -1, "player_2": 1 },
      "rock+scissors": { "player_1": 1, "player_2": -1 },
      "paper+rock": { "player_1": 1, "player_2": -1 },
      "paper+paper": { "player_1": 0, "player_2": 0 },
      "paper+scissors": { "player_1": -1, "player_2": 1 },
      "scissors+rock": { "player_1": -1, "player_2": 1 },
      "scissors+paper": { "player_1": 1, "player_2": -1 },
      "scissors+scissors": { "player_1": 0, "player_2": 0 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* exactly two symmetric players;
* three actions each — rock, paper, scissors — supplied by the model, since the prompt never listed them;
* simultaneous single-step play (both choose at once), hence joint-action keys over all nine combinations;
* the correct dominance relation: rock beats scissors, scissors beats paper, paper beats rock, identical choices draw;
* three outcome types (player 1 wins, player 2 wins, draw), all terminal;
* zero-sum rewards under some consistent scheme (e.g. +1 / −1 / 0) — the winner's gain is the loser's loss and draws pay 0 to both, reflecting mutually exclusive competitive outcomes.

A good answer should NOT include:

* extra or altered rules not in standard rock-paper-scissors (e.g. lizard-spock variants), or making it best-of-several when the prompt says a single round;
* cooperative or common-payoff rewards (both players positive for the same outcome);
* turning simultaneous play into a turn-based game where player 2 sees player 1's choice first;
* invented specifics (player names, money stakes) or a story.
