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
            bid1, bid2 = joint_action["bidder_1"], joint_action["bidder_2"]
            if bid1 == bid2:
                return {"bid_tie": 0.5, "bid_1_high": 0.5}
            elif bid1 > bid2:
                return {"bid_1_high": 1.0}
            else:
                return {"bid_2_high": 1.0}
        elif state.startswith("bid_"):
            return {"terminal": 1.0}
    def observation(self, state, joint_action, next_state, player): 
        if state == "start":
            return f"{player}_bids_{joint_action[player]}"
        elif state.startswith("bid_"):
            if player == "bidder_1":
                return f"bidder_1_wins" if next_state == "bid_1_high" else f"bidder_2_wins"
            else:
                return f"bidder_2_wins" if next_state == "bid_2_high" else f"bidder_1_wins"
    def reward(self, state, joint_action, next_state, player): 
        if state == "start":
            return 0.0
        elif state.startswith("bid_"):
            if player == "bidder_1":
                return 10.0 if next_state == "bid_1_high" else -5.0
            else:
                return 10.0 if next_state == "bid_2_high" else -5.0
    def is_terminal(self, state): return state == "terminal" or state.startswith("bid_")
