class GeneratedPOSG(AbstractPOSG):
    def __init__(self):
        self.players = ("robot",)
        self.states = ("start", "destination", "collision")
        self.actions = {
            "robot": ("safe_route", "risky_route")
        }

    def initial_state(self):
        return "start"

    def transition(self, state, actions):
        action = actions["robot"] if isinstance(actions, dict) else actions

        if state == "start":
            if action == "safe_route":
                return (("destination", 1.0),)
            if action == "risky_route":
                return (("destination", 0.8), ("collision", 0.2))
            raise ValueError("invalid action")

        if state in ("destination", "collision"):
            return ((state, 1.0),)

        raise ValueError("invalid state")

    def reward(self, state, actions, next_state):
        action = actions["robot"] if isinstance(actions, dict) else actions

        if state != "start":
            return {"robot": 0.0}
        if next_state == "collision":
            return {"robot": -100.0}
        if next_state == "destination" and action == "safe_route":
            return {"robot": 90.0}
        if next_state == "destination" and action == "risky_route":
            return {"robot": 100.0}
        raise ValueError("invalid transition")

    def is_terminal(self, state):
        return state in ("destination", "collision")

    def available_actions(self, state, player):
        if player != "robot":
            raise ValueError("invalid player")
        if state == "start":
            return ("safe_route", "risky_route")
        return ()