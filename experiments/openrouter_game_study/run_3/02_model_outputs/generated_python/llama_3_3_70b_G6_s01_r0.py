class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["bidder_1", "bidder_2"]
    def initial_state(self): return "start"
    def legal_actions(self, state, player): 
        if state == "start": 
            return ["low", "high"]
        elif state.startswith("bid_"): 
            return ["reveal"]
        else: 
            return []
    def transition(self, state, joint_action): 
        if state == "start": 
            bid_state = f"bid_{joint_action['bidder_1']}_{joint_action['bidder_2']}"
            return {bid_state: 1.0}
        elif state.startswith("bid_"): 
            if joint_action["bidder_1"] == joint_action["bidder_2"]: 
                return {"win_bidder_1": 0.5, "win_bidder_2": 0.5}
            elif joint_action["bidder_1"] == "high" and joint_action["bidder_2"] == "low": 
                return {"win_bidder_1": 1.0}
            else: 
                return {"win_bidder_2": 1.0}
        else: 
            return {"terminal": 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if next_state == "terminal": 
            return f"game_over_{player}"
        elif next_state.startswith("win_"): 
            return f"{next_state}_{player}"
        else: 
            return f"{state}_{player}"
    def reward(self, state, joint_action, next_state, player): 
        if next_state == "win_bidder_1" and player == "bidder_1": 
            if joint_action["bidder_1"] == "high": 
                return 10.0
            else: 
                return 5.0
        elif next_state == "win_bidder_2" and player == "bidder_2": 
            if joint_action["bidder_2"] == "high": 
                return 10.0
            else: 
                return 5.0
        else: 
            return 0.0
    def is_terminal(self, state): 
        return state == "terminal" or state.startswith("win_")
