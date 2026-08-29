class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        return ["0-3", "1-2", "2-1", "3-0"]

    def transition(self, state, joint_action):
        first = int(joint_action["player_1"][0])
        second = int(joint_action["player_2"][0])
        if first > second:
            return {"player_1_wins": 1.0}
        if first < second:
            return {"player_2_wins": 1.0}
        return {"draw": 1.0}

    def observation(self, state, joint_action, next_state, player):
        return f"{joint_action['player_1']}_vs_{joint_action['player_2']}:{next_state}"

    def reward(self, state, joint_action, next_state, player):
        if next_state == "draw":
            return 0.0
        if next_state == f"{player}_wins":
            return 1.0
        return -1.0

    def is_terminal(self, state):
        return state in ["player_1_wins", "player_2_wins", "draw"]
