class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]

    def initial_state(self): return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return [f"{i}-{3-i}" for i in range(4)]
        else:
            return []

    def transition(self, state, joint_action):
        if state == "s0":
            player_1_action = joint_action["player_1"]
            player_2_action = joint_action["player_2"]
            player_1_battlefield_1_soldiers = int(player_1_action.split("-")[0])
            player_1_battlefield_2_soldiers = int(player_1_action.split("-")[1])
            player_2_battlefield_1_soldiers = int(player_2_action.split("-")[0])
            player_2_battlefield_2_soldiers = int(player_2_action.split("-")[1])

            player_1_wins_battlefield_1 = player_1_battlefield_1_soldiers > player_2_battlefield_1_soldiers
            player_1_wins_battlefield_2 = player_1_battlefield_2_soldiers > player_2_battlefield_2_soldiers

            if player_1_wins_battlefield_1 and player_1_wins_battlefield_2:
                return {"player_1_wins": 1.0}
            elif player_1_wins_battlefield_1 and not player_1_wins_battlefield_2:
                return {"draw": 1.0}
            elif not player_1_wins_battlefield_1 and player_1_wins_battlefield_2:
                return {"draw": 1.0}
            else:
                return {"player_2_wins": 1.0}
        else:
            return {}

    def observation(self, state, joint_action, next_state, player):
        if next_state == "player_1_wins":
            return "player_1_wins"
        elif next_state == "player_2_wins":
            return "player_2_wins"
        else:
            return "draw"

    def reward(self, state, joint_action, next_state, player):
        if next_state == "player_1_wins" and player == "player_1":
            return 1.0
        elif next_state == "player_2_wins" and player == "player_2":
            return 1.0
        elif next_state == "draw":
            return 0.5
        else:
            return 0.0

    def is_terminal(self, state):
        return state in ["player_1_wins", "player_2_wins", "draw"]