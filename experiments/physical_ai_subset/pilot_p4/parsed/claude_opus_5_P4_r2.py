class GeneratedPOSG(AbstractPOSG):
    """
    Single-agent POSG (a POMDP expressed in the POSG interface) for a robot
    choosing between a safe longer route and a short risky route.

    States (string identifiers only):
        "start"      : robot at origin, must choose a route
        "goal"       : destination reached (terminal, success)
        "collision"  : robot collided on the risky route (terminal, unsafe)

    Actions for player "robot":
        "safe_route"  : deterministically reaches the goal, but costs more
        "risky_route" : short route; may reach the goal or collide
    """

    # ---------------- structural accessors ----------------

    def players(self):
        return ["robot"]

    def states(self):
        return ["start", "goal", "collision"]

    def initial_state(self):
        return "start"

    def initial_belief(self):
        return {"start": 1.0}

    def actions(self, player, state=None):
        if player != "robot":
            return []
        if state is not None and self.is_terminal(state):
            return []
        return ["safe_route", "risky_route"]

    def joint_actions(self, state=None):
        return [{"robot": a} for a in self.actions("robot", state)]

    # ---------------- terminality ----------------

    def is_terminal(self, state):
        return state in ("goal", "collision")

    def terminal_type(self, state):
        if state == "goal":
            return "success"
        if state == "collision":
            return "unsafe"
        return None

    def is_unsafe(self, state):
        return state == "collision"

    def is_success(self, state):
        return state == "goal"

    # ---------------- dynamics ----------------

    def transition(self, state, joint_action):
        """
        Returns a dict mapping next_state -> probability.
        All action-conditioned outcomes are exposed explicitly.
        """
        if self.is_terminal(state):
            return {state: 1.0}

        action = self._extract_action(joint_action)

        if state == "start":
            if action == "safe_route":
                return {"goal": 1.0}
            if action == "risky_route":
                return {"goal": 0.8, "collision": 0.2}

        return {state: 1.0}

    def reward(self, state, joint_action, next_state=None):
        """
        Numeric rewards:
            safe_route  -> reaches goal, cost of longer route      : +5.0
            risky_route -> goal (short route)                      : +10.0
                        -> collision (unsafe terminal)             : -20.0
        Terminal states yield no further reward.
        """
        if self.is_terminal(state):
            return 0.0

        action = self._extract_action(joint_action)

        if state == "start":
            if action == "safe_route":
                return 5.0
            if action == "risky_route":
                if next_state == "collision":
                    return -20.0
                if next_state == "goal":
                    return 10.0
                # expected value when next_state is unspecified
                return 0.8 * 10.0 + 0.2 * (-20.0)

        return 0.0

    def rewards(self, state, joint_action, next_state=None):
        return {"robot": self.reward(state, joint_action, next_state)}

    # ---------------- observations ----------------

    def observations(self, player=None):
        return ["obs_start", "obs_goal", "obs_collision"]

    def observation(self, state, joint_action=None, next_state=None):
        s = next_state if next_state is not None else state
        return self.observation_distribution(s)

    def observation_distribution(self, state):
        if state == "goal":
            return {"obs_goal": 1.0}
        if state == "collision":
            return {"obs_collision": 1.0}
        return {"obs_start": 1.0}

    def observation_probability(self, observation, state, joint_action=None,
                                next_state=None):
        s = next_state if next_state is not None else state
        return self.observation_distribution(s).get(observation, 0.0)

    # ---------------- misc ----------------

    def discount(self):
        return 1.0

    def horizon(self):
        return 2

    # ---------------- helpers ----------------

    def _extract_action(self, joint_action):
        if isinstance(joint_action, dict):
            return joint_action.get("robot")
        if isinstance(joint_action, (list, tuple)):
            for item in joint_action:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    if item[0] == "robot":
                        return item[1]
                elif isinstance(item, str):
                    return item
            return None
        return joint_action