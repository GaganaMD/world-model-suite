class GeneratedPOSG(AbstractPOSG):
    def __init__(self):
        self._states = {"start", "safe_progress", "destination", "collision"}
        self._players = {"robot"}
        self._actions = {
            "robot": {"safe_route", "risky_route"}
        }

    def players(self):
        return self._players

    def states(self):
        return self._states

    def actions(self, player, state=None):
        if player != "robot":
            return set()
        if state in {"destination", "collision"}:
            return set()
        return self._actions[player]

    def initial_state(self):
        return "start"

    def transition(self, state, actions):
        action = actions["robot"] if isinstance(actions, dict) else actions

        if state == "start":
            if action == "safe_route":
                return [("safe_progress", 1.0)]
            if action == "risky_route":
                return [("destination", 0.8), ("collision", 0.2)]

        if state == "safe_progress":
            if action in {"safe_route", "risky_route"}:
                return [("destination", 1.0)]

        if state in {"destination", "collision"}:
            return [(state, 1.0)]

        return []

    def reward(self, state, actions, next_state):
        if next_state == "destination":
            return {"robot": 10.0}
        if next_state == "collision":
            return {"robot": -10.0}
        if next_state == "safe_progress":
            return {"robot": -1.0}
        return {"robot": 0.0}

    def is_terminal(self, state):
        return state in {"destination", "collision"}