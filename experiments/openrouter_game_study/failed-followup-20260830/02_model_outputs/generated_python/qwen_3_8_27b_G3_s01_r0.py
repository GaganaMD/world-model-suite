class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["heads", "tails"]
        return []

    def transition(self, state, joint_action):
        if state != "s0":
            return {"terminal": 1.0}
        p1 = joint_action["player_1"]
        p2 = joint_action["player_2"]
        # Fair coin: heads or tails with prob 0.5 each
        return {f"s_heads_{p1}_{p2}": 0.5, f"s_tails_{p1}_{p2}": 0.5}

    def observation(self, state, joint_action, next_state, player):
        if state != "s0":
            return "game_over"
        # next_state is like "s_heads_h_t" or "s_tails_t_h"
        parts = next_state.split("_")
        # parts[0] = "s", parts[1] = "heads"/"tails", parts[2] = p1 call, parts[3] = p2 call
        result = parts[1]
        p1_call = parts[2]
        p2_call = parts[3]
        my_call = p1_call if player == "player_1" else p2_call
        other_call = p2_call if player == "player_1" else p1_call
        return f"result={result};my_call={my_call};other_call={other_call}"

    def reward(self, state, joint_action, next_state, player):
        if state != "s0":
            return 0.0
        parts = next_state.split("_")
        result = parts[1]
        p1_call = parts[2]
        p2_call = parts[3]
        p1_match = (p1_call == result)
        p2_match = (p2_call == result)
        if player == "player_1":
            if p1_match and not p2_match:
                return 1.0
            elif p2_match and not p1_match:
                return -1.0
            else:
                return 0.0
        else:
            if p2_match and not p1_match:
                return 1.0
            elif p1_match and not p2_match:
                return -1.0
            else:
                return 0.0

    def is_terminal(self, state):
        return state.startswith("s_heads_") or state.startswith("s_tails_")
