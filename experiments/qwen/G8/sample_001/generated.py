class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["hunter_1", "hunter_2"]
    def initial_state(self): return ("stag", False)
    def legal_actions(self, state, player): return ["cooperate", "hunt_alone"]
    def transition(self, state, joint_action):
        stag_available, both_cooperated = state
        if stag_available and joint_action == {"hunter_1": "cooperate", "hunter_2": "cooperate"}:
            return {"terminal": 1.0}
        elif stag_available and joint_action != {"hunter_1": "cooperate", "hunter_2": "cooperate"}:
            return {"terminal": 1.0}
        else:
            return {"terminal": 1.0}
    def observation(self, state, joint_action, next_state, player):
        if joint_action == {"hunter_1": "cooperate", "hunter_2": "cooperate"}:
            return "stag"
        else:
            return "hare"
    def reward(self, state, joint_action, next_state, player):
        stag_available, both_cooperated = state
        if stag_available and joint_action == {"hunter_1": "cooperate", "hunter_2": "cooperate"}:
            return 3.0
        elif stag_available and joint_action != {"hunter_1": "cooperate", "hunter_2": "cooperate"}:
            return 1.0
        else:
            return 0.0
    def is_terminal(self, state): return state == ("terminal", False)