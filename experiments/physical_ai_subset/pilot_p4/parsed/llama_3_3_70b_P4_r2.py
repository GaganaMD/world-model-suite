class GeneratedPOSG:
    def __init__(self):
        self.player_id = "robot"
        self.state_id = "start"
        self.action_ids = ["safe_route", "risky_route"]
        self.outcome_probabilities = {
            ("start", "safe_route"): {("destination", True): 1.0},
            ("start", "risky_route"): {("collision", True): 0.2, ("destination", True): 0.8},
            ("destination", "safe_route"): {("destination", True): 1.0},
            ("destination", "risky_route"): {("destination", True): 1.0},
            ("collision", "safe_route"): {("collision", True): 1.0},
            ("collision", "risky_route"): {("collision", True): 1.0},
        }
        self.rewards = {
            ("start", "safe_route", "destination"): 10,
            ("start", "risky_route", "destination"): 20,
            ("start", "risky_route", "collision"): -10,
        }

    def initial_state(self):
        return "start"

    def is_terminal(self, state):
        return state in ["destination", "collision"]

    def transition(self, state, action):
        return self.outcome_probabilities.get((state, action), {})

    def reward(self, state, action, next_state):
        return self.rewards.get((state, action, next_state), 0)