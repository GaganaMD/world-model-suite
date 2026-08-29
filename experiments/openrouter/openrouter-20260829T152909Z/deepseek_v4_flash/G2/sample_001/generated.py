```python
class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["roll"]
        return []

    def transition(self, state, joint_action):
        # state is "s0", both players choose "roll"
        # Fair six-sided dice, higher number wins
        # 36 equally likely outcomes: 15 player1 wins, 15 player2 wins, 6 draws
        return {
            "p1_wins": 15 / 36,
            "p2_wins": 15 / 36,
            "draw": 6 / 36,
        }

    def observation(self, state, joint_action, next_state, player):
        # Fully observable: all players see the outcome
        return next_state

    def reward(self, state, joint_action, next_state, player):
        if player == "player_1":
            if next_state == "p1_wins":
                return 1.0
            elif next_state == "p2_wins":
                return -1.0
            else:  # draw
                return 0.0
        else:  # player_2
            if next_state == "p2_wins":
                return 1.0
            elif next_state == "p1_wins":
                return -1.0
            else:
                return 0.0

    def is_terminal(self, state):
        return state in ["p1_wins", "p2_wins", "draw"]