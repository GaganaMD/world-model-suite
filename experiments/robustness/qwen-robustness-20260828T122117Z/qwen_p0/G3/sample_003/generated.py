class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return ("s0", None)
    def legal_actions(self, state, player): return ["heads", "tails"]
    def transition(self, state, joint_action):
        current_state, result = state
        if result is None:
            coin_flip = random.choice(["heads", "tails"])
            next_state = (current_state, coin_flip)
        else:
            next_state = (current_state, result)
        return {next_state: 1.0}
    def observation(self, state, joint_action, next_state, player):
        _, result = next_state
        if result == joint_action[player]:
            return "win"
        elif result != joint_action[player] and joint_action["player_1"] != joint_action["player_2"]:
            return "draw"
        else:
            return "loss"
    def reward(self, state, joint_action, next_state, player):
        _, result = next_state
        if result == joint_action[player]:
            return 1.0
        elif result != joint_action[player] and joint_action["player_1"] != joint_action["player_2"]:
            return 0.5
        else:
            return -1.0
    def is_terminal(self, state): return state[1] is not None