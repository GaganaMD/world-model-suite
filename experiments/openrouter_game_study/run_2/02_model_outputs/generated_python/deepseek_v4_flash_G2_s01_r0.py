class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["roll"]
        return ["noop"]

    def transition(self, state, joint_action):
        if state == "s0":
            if joint_action["player_1"] == "roll" and joint_action["player_2"] == "roll":
                return {
                    "s1": 1.0 / 36.0,
                    "s2": 2.0 / 36.0,
                    "s3": 3.0 / 36.0,
                    "s4": 4.0 / 36.0,
                    "s5": 5.0 / 36.0,
                    "s6": 6.0 / 36.0,
                    "s7": 5.0 / 36.0,
                    "s8": 4.0 / 36.0,
                    "s9": 3.0 / 36.0,
                    "s10": 2.0 / 36.0,
                    "s11": 1.0 / 36.0,
                }
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            if next_state == "s1":
                return "player_1_rolled_1_player_2_rolled_1_tie"
            if next_state == "s2":
                return "player_1_rolled_" + str(1 if player == "player_1" else 2) + "_player_2_rolled_" + str(2 if player == "player_1" else 1)
            if next_state == "s3":
                return "player_1_rolled_" + str(1 if player == "player_1" else 3) + "_player_2_rolled_" + str(3 if player == "player_1" else 2)
            if next_state == "s4":
                return "player_1_rolled_" + str(1 if player == "player_1" else 4) + "_player_2_rolled_" + str(4 if player == "player_1" else 3)
            if next_state == "s5":
                return "player_1_rolled_" + str(1 if player == "player_1" else 5) + "_player_2_rolled_" + str(5 if player == "player_1" else 4)
            if next_state == "s6":
                return "player_1_rolled_" + str(1 if player == "player_1" else 6) + "_player_2_rolled_" + str(6 if player == "player_1" else 5)
            if next_state == "s7":
                return "player_1_rolled_" + str(2 if player == "player_1" else 6) + "_player_2_rolled_" + str(6 if player == "player_1" else 2)
            if next_state == "s8":
                return "player_1_rolled_" + str(3 if player == "player_1" else 6) + "_player_2_rolled_" + str(6 if player == "player_1" else 3)
            if next_state == "s9":
                return "player_1_rolled_" + str(4 if player == "player_1" else 6) + "_player_2_rolled_" + str(6 if player == "player_1" else 4)
            if next_state == "s10":
                return "player_1_rolled_" + str(5 if player == "player_1" else 6) + "_player_2_rolled_" + str(6 if player == "player_1" else 5)
            if next_state == "s11":
                return "player_1_rolled_6_player_2_rolled_6_tie"
        return "game_over"

    def reward(self, state, joint_action, next_state, player):
        p1_roll = 0
        p2_roll = 0
        if next_state == "s1":
            p1_roll = 1
            p2_roll = 1
        elif next_state == "s2":
            p1_roll = 1
            p2_roll = 2
        elif next_state == "s3":
            p1_roll = 1
            p2_roll = 3
        elif next_state == "s4":
            p1_roll = 1
            p2_roll = 4
        elif next_state == "s5":
            p1_roll = 1
            p2_roll = 5
        elif next_state == "s6":
            p1_roll = 1
            p2_roll = 6
        elif next_state == "s7":
            p1_roll = 2
            p2_roll = 6
        elif next_state == "s8":
            p1_roll = 3
            p2_roll = 6
        elif next_state == "s9":
            p1_roll = 4
            p2_roll = 6
        elif next_state == "s10":
            p1_roll = 5
            p2_roll = 6
        elif next_state == "s11":
            p1_roll = 6
            p2_roll = 6
        if p1_roll > p2_roll:
            return 1.0 if player == "player_1" else -1.0
        elif p2_roll > p1_roll:
            return -1.0 if player == "player_1" else 1.0
        return 0.0

    def is_terminal(self, state):
        return state == "terminal"
