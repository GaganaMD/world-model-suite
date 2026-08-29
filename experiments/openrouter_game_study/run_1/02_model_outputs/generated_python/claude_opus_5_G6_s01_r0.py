class GeneratedPOSG(AbstractPOSG):
    """
    Sealed-bid first-price auction with private binary values.

    Timeline:
      s0                      -> chance node: nature draws (v1, v2) in {L,H}^2, uniform (1/4 each)
      "bid_v1_v2"             -> simultaneous bidding stage; each bidder chooses bid in {0,1,2,3}
      "tie_v1_v2_b1_b2"       -> chance node: coin flip breaks a tie
      "end_..."               -> terminal

    Values: L = 2, H = 4. Bids are integers 0..3.
    Payoff to winner = value - bid; loser gets 0.
    """

    VALUE = {"L": 2.0, "H": 4.0}
    BIDS = ["0", "1", "2", "3"]

    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    # ---------------- helpers ----------------

    def _parts(self, state):
        return state.split("_")

    # ---------------- interface ----------------

    def legal_actions(self, state, player):
        if state == "s0":
            # chance node encoded as a single dummy action for both players
            return ["wait"]
        if state.startswith("bid_"):
            return list(self.BIDS)
        if state.startswith("tie_"):
            return ["wait"]
        return ["wait"]

    def transition(self, state, joint_action):
        if state == "s0":
            return {
                "bid_L_L": 0.25,
                "bid_L_H": 0.25,
                "bid_H_L": 0.25,
                "bid_H_H": 0.25,
            }

        if state.startswith("bid_"):
            p = self._parts(state)  # ["bid", v1, v2]
            v1, v2 = p[1], p[2]
            b1 = joint_action["player_1"]
            b2 = joint_action["player_2"]
            if b1 not in self.BIDS:
                b1 = "0"
            if b2 not in self.BIDS:
                b2 = "0"
            if b1 == b2:
                return {"tie_" + v1 + "_" + v2 + "_" + b1 + "_" + b2: 1.0}
            winner = "1" if int(b1) > int(b2) else "2"
            return {"end_" + v1 + "_" + v2 + "_" + b1 + "_" + b2 + "_" + winner: 1.0}

        if state.startswith("tie_"):
            p = self._parts(state)  # ["tie", v1, v2, b1, b2]
            base = "end_" + p[1] + "_" + p[2] + "_" + p[3] + "_" + p[4]
            return {base + "_1": 0.5, base + "_2": 0.5}

        return {state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            p = self._parts(next_state)  # ["bid", v1, v2]
            own = p[1] if player == "player_1" else p[2]
            return f"phase=bid;my_value={own};opp_value=hidden"

        if state.startswith("bid_"):
            b1 = joint_action.get("player_1", "0")
            b2 = joint_action.get("player_2", "0")
            if b1 not in self.BIDS:
                b1 = "0"
            if b2 not in self.BIDS:
                b2 = "0"
            my = b1 if player == "player_1" else b2
            opp = b2 if player == "player_1" else b1
            if next_state.startswith("tie_"):
                return f"phase=tie;my_bid={my};opp_bid={opp};result=coinflip"
            winner = self._parts(next_state)[5]
            outcome = "won" if winner == ("1" if player == "player_1" else "2") else "lost"
            return f"phase=end;my_bid={my};opp_bid={opp};result={outcome}"

        if state.startswith("tie_"):
            p = self._parts(state)  # ["tie", v1, v2, b1, b2]
            my = p[3] if player == "player_1" else p[4]
            opp = p[4] if player == "player_1" else p[3]
            winner = self._parts(next_state)[5]
            outcome = "won" if winner == ("1" if player == "player_1" else "2") else "lost"
            return f"phase=end;my_bid={my};opp_bid={opp};result={outcome}_after_coinflip"

        return "phase=end;result=none"

    def reward(self, state, joint_action, next_state, player):
        if not next_state.startswith("end_"):
            return 0.0
        p = self._parts(next_state)  # ["end", v1, v2, b1, b2, winner]
        v1, v2, b1, b2, winner = p[1], p[2], p[3], p[4], p[5]
        if player == "player_1":
            if winner == "1":
                return self.VALUE[v1] - float(int(b1))
            return 0.0
        else:
            if winner == "2":
                return self.VALUE[v2] - float(int(b2))
            return 0.0

    def is_terminal(self, state):
        return state.startswith("end_")
