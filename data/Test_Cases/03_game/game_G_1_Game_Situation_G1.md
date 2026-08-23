Game Situation G.1: One Round of Rock-Paper-Scissors

LLM Input

Two people sit down to play a single round of rock-paper-scissors.

Expected LLM Output

{
  "players": [
    {"id": "player_1", "description": "The first person playing the round"},
    {"id": "player_2", "description": "The second person playing the round"}
  ],
  "initial_state": "s0",
  "states": {
    "s0": {"description": "Both players are about to reveal their choice; nothing thrown yet.", "terminal": false},
    "s1": {"description": "Player 1 wins the round.", "terminal": true},
    "s2": {"description": "Player 2 wins the round.", "terminal": true},
    "s3": {"description": "The round is a draw because both players chose the same.", "terminal": true}
  },
  "actions": {
    "s0": {
      "player_1": ["rock", "paper", "scissors"],
      "player_2": ["rock", "paper", "scissors"]
    }
  },
  "transition_probabilities": {
    "s0": {
      "rock+rock": {"s3": 1.0},
      "rock+paper": {"s2": 1.0},
      "rock+scissors": {"s1": 1.0},
      "paper+rock": {"s1": 1.0},
      "paper+paper": {"s3": 1.0},
      "paper+scissors": {"s2": 1.0},
      "scissors+rock": {"s2": 1.0},
      "scissors+paper": {"s1": 1.0},
      "scissors+scissors": {"s3": 1.0}
    }
  },
  "rewards": {
    "s0": {
      "rock+rock": {"player_1": 0, "player_2": 0},
      "rock+paper": {"player_1": -1, "player_2": 1},
      "rock+scissors": {"player_1": 1, "player_2": -1},
      "paper+rock": {"player_1": 1, "player_2": -1},
      "paper+paper": {"player_1": 0, "player_2": 0},
      "paper+scissors": {"player_1": -1, "player_2": 1},
      "scissors+rock": {"player_1": -1, "player_2": 1},
      "scissors+paper": {"player_1": 1, "player_2": -1},
      "scissors+scissors": {"player_1": 0, "player_2": 0}
    }
  }
}

Judging Criteria

A good model should include

Exactly two symmetric players.

Three actions for each player: rock, paper, and scissors.

Simultaneous single-step decisions by both players.

Joint actions covering all nine possible combinations.

Rock beats scissors, scissors beats paper, and paper beats rock.

Identical choices result in a draw.

Three terminal outcome types: Player 1 wins, Player 2 wins, and draw.

Deterministic transitions for every joint action.

Zero-sum rewards, using any consistent numerical scale where the winner gains what the loser loses and a draw gives both players zero.

A good model should NOT include

Additional players or roles.

Additional actions or variants such as lizard-spock.

Multiple rounds or a best-of-several format.

Sequential play where one player observes the other's choice before acting.

Stochastic transitions or random outcomes.

Cooperative or common-payoff rewards.

Invented player names, money stakes, or other scenario details not present in the input.

A non-terminal state after the choices have been revealed and the winner determined.11