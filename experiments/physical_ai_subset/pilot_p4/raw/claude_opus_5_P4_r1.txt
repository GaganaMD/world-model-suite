class GeneratedPOSG(AbstractPOSG):
    """
    Single-agent POSG (POMDP-shaped) navigation scenario.

    States (string identifiers only):
        "start"       - robot at origin, must choose a route
        "en_route"    - robot committed to the safe (longer) route
        "goal"        - terminal success: destination reached
        "collision"   - terminal unsafe outcome: collision occurred

    Player:
        "robot"

    Actions:
        "safe_route"  - longer route, no collision possibility
        "risky_route" - short route with a known collision possibility
    """

    PLAYER = "robot"

    START = "start"
    EN_ROUTE = "en_route"
    GOAL = "goal"
    COLLISION = "collision"

    SAFE = "safe_route"
    RISKY = "risky_route"

    # Known collision possibility on the risky route.
    RISKY_COLLISION_PROB = 0.3
    RISKY_SUCCESS_PROB = 0.7

    # Numeric rewards.
    R_STEP_SAFE = -2.0        # cost of taking the longer safe leg
    R_STEP_RISKY = -1.0       # cost of the short risky leg
    R_GOAL = 10.0             # success terminal bonus
    R_COLLISION = -20.0       # unsafe terminal penalty
    R_TERMINAL = 0.0          # no further reward once terminal

    # ---------------------------------------------------------------- players

    def players(self):
        return [self.PLAYER]

    def num_players(self):
        return 1

    # ----------------------------------------------------------------- states

    def states(self):
        return [self.START, self.EN_ROUTE, self.GOAL, self.COLLISION]

    def initial_state(self):
        return self.START

    def initial_belief(self):
        return {self.START: 1.0}

    def is_terminal(self, state):
        return state in (self.GOAL, self.COLLISION)

    def is_unsafe(self, state):
        return state == self.COLLISION

    def is_success(self, state):
        return state == self.GOAL

    # ---------------------------------------------------------------- actions

    def actions(self, player=None):
        return [self.SAFE, self.RISKY]

    def legal_actions(self, state, player=None):
        if self.is_terminal(state):
            return []
        return [self.SAFE, self.RISKY]

    def joint_actions(self, state):
        return [(a,) for a in self.legal_actions(state)]

    # ---------------------------------------------------------- observations

    def observations(self, player=None):
        return [self.START, self.EN_ROUTE, self.GOAL, self.COLLISION]

    def observation(self, state, player=None):
        return state

    def observation_distribution(self, state, player=None):
        return {state: 1.0}

    # ----------------------------------------------------------- transitions

    def _action_id(self, action):
        if isinstance(action, dict):
            return action[self.PLAYER]
        if isinstance(action, (list, tuple)):
            return action[0]
        return action

    def transition(self, state, action):
        """
        Returns a dict mapping successor state identifier -> probability.
        All outcomes are exposed explicitly.
        """
        a = self._action_id(action)

        if self.is_terminal(state):
            return {state: 1.0}

        if state == self.START:
            if a == self.SAFE:
                # Safe longer route: deterministic intermediate leg, no collision.
                return {self.EN_ROUTE: 1.0}
            if a == self.RISKY:
                # Short risky route: known collision possibility.
                return {
                    self.GOAL: self.RISKY_SUCCESS_PROB,
                    self.COLLISION: self.RISKY_COLLISION_PROB,
                }

        if state == self.EN_ROUTE:
            # Remaining safe leg always completes safely, regardless of action.
            if a == self.SAFE:
                return {self.GOAL: 1.0}
            if a == self.RISKY:
                # Cutting across from en route still carries the known risk.
                return {
                    self.GOAL: self.RISKY_SUCCESS_PROB,
                    self.COLLISION: self.RISKY_COLLISION_PROB,
                }

        return {state: 1.0}

    def successors(self, state, action):
        return list(self.transition(state, action).keys())

    # --------------------------------------------------------------- rewards

    def reward(self, state, action, next_state=None):
        """
        Reward for player "robot". Terminal states yield no further reward.
        """
        if self.is_terminal(state):
            return self.R_TERMINAL

        a = self._action_id(action)
        step = self.R_STEP_SAFE if a == self.SAFE else self.R_STEP_RISKY

        if next_state is None:
            return step

        if next_state == self.GOAL:
            return step + self.R_GOAL
        if next_state == self.COLLISION:
            return step + self.R_COLLISION
        return step

    def rewards(self, state, action, next_state=None):
        return {self.PLAYER: self.reward(state, action, next_state)}

    def discount(self):
        return 0.95