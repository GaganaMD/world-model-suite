class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player): 
        if state == "s0":
            return ["0-3", "1-2", "2-1", "3-0"]
        else:
            return []
    def transition(self, state, joint_action): 
        if state == "s0":
            player1_action = joint_action["player_1"]
            player2_action = joint_action["player_2"]
            if player1_action == "0-3" and player2_action == "0-3":
                return {"s1": 1.0}
            elif player1_action == "0-3" and player2_action == "1-2":
                return {"s2": 1.0}
            elif player1_action == "0-3" and player2_action == "2-1":
                return {"s3": 1.0}
            elif player1_action == "0-3" and player2_action == "3-0":
                return {"s4": 1.0}
            elif player1_action == "1-2" and player2_action == "0-3":
                return {"s5": 1.0}
            elif player1_action == "1-2" and player2_action == "1-2":
                return {"s6": 1.0}
            elif player1_action == "1-2" and player2_action == "2-1":
                return {"s7": 1.0}
            elif player1_action == "1-2" and player2_action == "3-0":
                return {"s8": 1.0}
            elif player1_action == "2-1" and player2_action == "0-3":
                return {"s9": 1.0}
            elif player1_action == "2-1" and player2_action == "1-2":
                return {"s10": 1.0}
            elif player1_action == "2-1" and player2_action == "2-1":
                return {"s11": 1.0}
            elif player1_action == "2-1" and player2_action == "3-0":
                return {"s12": 1.0}
            elif player1_action == "3-0" and player2_action == "0-3":
                return {"s13": 1.0}
            elif player1_action == "3-0" and player2_action == "1-2":
                return {"s14": 1.0}
            elif player1_action == "3-0" and player2_action == "2-1":
                return {"s15": 1.0}
            elif player1_action == "3-0" and player2_action == "3-0":
                return {"s16": 1.0}
        else:
            return {state: 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if player == "player_1":
            if next_state == "s1":
                return f"player_1 loses"
            elif next_state == "s2":
                return f"player_1 loses"
            elif next_state == "s3":
                return f"draw"
            elif next_state == "s4":
                return f"player_1 wins"
            elif next_state == "s5":
                return f"player_1 wins"
            elif next_state == "s6":
                return f"draw"
            elif next_state == "s7":
                return f"player_1 loses"
            elif next_state == "s8":
                return f"player_1 wins"
            elif next_state == "s9":
                return f"player_1 wins"
            elif next_state == "s10":
                return f"draw"
            elif next_state == "s11":
                return f"player_1 loses"
            elif next_state == "s12":
                return f"player_1 wins"
            elif next_state == "s13":
                return f"player_1 loses"
            elif next_state == "s14":
                return f"player_1 wins"
            elif next_state == "s15":
                return f"player_1 wins"
            elif next_state == "s16":
                return f"draw"
        else:
            if next_state == "s1":
                return f"player_2 wins"
            elif next_state == "s2":
                return f"player_2 wins"
            elif next_state == "s3":
                return f"draw"
            elif next_state == "s4":
                return f"player_2 loses"
            elif next_state == "s5":
                return f"player_2 loses"
            elif next_state == "s6":
                return f"draw"
            elif next_state == "s7":
                return f"player_2 wins"
            elif next_state == "s8":
                return f"player_2 loses"
            elif next_state == "s9":
                return f"player_2 loses"
            elif next_state == "s10":
                return f"draw"
            elif next_state == "s11":
                return f"player_2 wins"
            elif next_state == "s12":
                return f"player_2 loses"
            elif next_state == "s13":
                return f"player_2 wins"
            elif next_state == "s14":
                return f"player_2 loses"
            elif next_state == "s15":
                return f"player_2 loses"
            elif next_state == "s16":
                return f"draw"
    def reward(self, state, joint_action, next_state, player): 
        if player == "player_1":
            if next_state == "s1":
                return -1.0
            elif next_state == "s2":
                return -1.0
            elif next_state == "s3":
                return 0.0
            elif next_state == "s4":
                return 1.0
            elif next_state == "s5":
                return 1.0
            elif next_state == "s6":
                return 0.0
            elif next_state == "s7":
                return -1.0
            elif next_state == "s8":
                return 1.0
            elif next_state == "s9":
                return 1.0
            elif next_state == "s10":
                return 0.0
            elif next_state == "s11":
                return -1.0
            elif next_state == "s12":
                return 1.0
            elif next_state == "s13":
                return -1.0
            elif next_state == "s14":
                return 1.0
            elif next_state == "s15":
                return 1.0
            elif next_state == "s16":
                return 0.0
        else:
            if next_state == "s1":
                return 1.0
            elif next_state == "s2":
                return 1.0
            elif next_state == "s3":
                return 0.0
            elif next_state == "s4":
                return -1.0
            elif next_state == "s5":
                return -1.0
            elif next_state == "s6":
                return 0.0
            elif next_state == "s7":
                return 1.0
            elif next_state == "s8":
                return -1.0
            elif next_state == "s9":
                return -1.0
            elif next_state == "s10":
                return 0.0
            elif next_state == "s11":
                return 1.0
            elif next_state == "s12":
                return -1.0
            elif next_state == "s13":
                return 1.0
            elif next_state == "s14":
                return -1.0
            elif next_state == "s15":
                return -1.0
            elif next_state == "s16":
                return 0.0
    def is_terminal(self, state): 
        return state != "s0"
