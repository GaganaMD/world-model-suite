from posg import POSG

class VaseDelivery(POSG):

    n_players = 2

    def initial_distribution(self):
        # (state, obs_profile) where obs_profile = (robot_obs, delivery_obs)
        return {("pending", ("none", "none")): 1.0}

    def is_terminal(self, s):
        return s in ("accepted", "left")

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ()  # should not be called by the framework
        if i == 0:  # robot
            if s == "pending":
                return ("accept", "shake")
            if s == "shaken":
                return ("accept",)
        elif i == 1:  # delivery boy
            return ("wait", "leave")
        return ()

    def transition(self, s, a):
        robot_act, delivery_act = a
        if s == "pending":
            if robot_act == "accept" and delivery_act == "wait":
                return {("accepted", ("none", "none")): 1.0}
            if robot_act == "accept" and delivery_act == "leave":
                return {("left", ("none", "none")): 1.0}
            if robot_act == "shake" and delivery_act == "wait":
                return {("shaken", ("rattle", "none")): 1.0}
            if robot_act == "shake" and delivery_act == "leave":
                return {("left", ("none", "none")): 1.0}
        elif s == "shaken":
            # robot's only legal action here is "accept"
            if robot_act == "accept" and delivery_act == "wait":
                return {("accepted", ("none", "none")): 1.0}
            if robot_act == "accept" and delivery_act == "leave":
                return {("left", ("none", "none")): 1.0}
        return {}  # should not be reached

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
