class GeneratedPOSG(AbstractPOSG):
    """
    Two-round Stag Hunt as a partially observable stochastic game.

    World state: ("day", day_index, food_player_1, food_player_2)
                 ("end", food_player_1, food_player_2)   -- terminal

    Each day both hunters independently choose to pursue the stag or a hare.
    A stag is only brought down if BOTH hunters show up at the stag meadow
    (and then only with probability 0.85 -- the stag may still escape).
    A lone stag hunter goes home empty-handed.  A hare hunt succeeds with
    probability 0.9 and feeds exactly one person.

    Partial observability: a hunter always sees his own catch, but only learns
    whether his partner came to the stag meadow if he himself went there.
    A hare hunter is off alone in the brush and gets no information about the
    partner's choice (only a noiseless report of the total meat brought home
    at the end of the second day).
    """

    NUM_DAYS = 2
    P_STAG = 0.85
    P_HARE = 0.9
    STAG_SHARE = 4
    HARE_VALUE = 1

    # ------------------------------------------------------------------ #
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return ("day", 1, 0, 0)

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        return ["stag", "hare"]

    # ------------------------------------------------------------------ #
    def _outcome_distribution(self, a1, a2):
        """Distribution over (gain_player_1, gain_player_2) for one day."""
        ps, ph = self.P_STAG, self.P_HARE
        s, h = self.STAG_SHARE, self.HARE_VALUE

        if a1 == "stag" and a2 == "stag":
            return {(s, s): ps, (0, 0): 1.0 - ps}
        if a1 == "stag" and a2 == "hare":
            return {(0, h): ph, (0, 0): 1.0 - ph}
        if a1 == "hare" and a2 == "stag":
            return {(h, 0): ph, (0, 0): 1.0 - ph}

        # both hunt hare: independent successes
        dist = {}
        for g1, p1 in ((h, ph), (0, 1.0 - ph)):
            for g2, p2 in ((h, ph), (0, 1.0 - ph)):
                key = (g1, g2)
                dist[key] = dist.get(key, 0.0) + p1 * p2
        return dist

    def _clean(self, a):
        return "stag" if a == "stag" else "hare"

    # ------------------------------------------------------------------ #
    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        a1 = self._clean(joint_action["player_1"])
        a2 = self._clean(joint_action["player_2"])

        day = state[1]
        f1 = state[2]
        f2 = state[3]

        raw = self._outcome_distribution(a1, a2)

        result = {}
        for (g1, g2), p in raw.items():
            if p <= 0.0:
                continue
            n1 = f1 + g1
            n2 = f2 + g2
            if day >= self.NUM_DAYS:
                nxt = ("end", n1, n2)
            else:
                nxt = ("day", day + 1, n1, n2)
            result[nxt] = result.get(nxt, 0.0) + p

        total = sum(result.values())
        if total <= 0.0:
            # defensive fallback: never happens with the numbers above
            return {("end", f1, f2): 1.0}
        return {k: v / total for k, v in result.items()}

    # ------------------------------------------------------------------ #
    def observation(self, state, joint_action, next_state, player):
        if self.is_terminal(state):
            return "hunt_over"

        my_action = self._clean(joint_action[player])
        partner = "player_2" if player == "player_1" else "player_1"
        partner_action = self._clean(joint_action[partner])

        if player == "player_1":
            my_gain = next_state[-2] - state[2]
        else:
            my_gain = next_state[-1] - state[3]

        caught = "caught" if my_gain > 0 else "empty"

        if my_action == "stag":
            seen = "partner_at_meadow" if partner_action == "stag" else "partner_absent"
        else:
            seen = "partner_unseen"

        if next_state[0] == "end":
            phase = "final"
            totals = "total_%d_%d" % (next_state[1], next_state[2])
        else:
            phase = "day_%d" % next_state[1]
            totals = "ongoing"

        return "%s|went_%s|%s|%s|%s" % (phase, my_action, caught, seen, totals)

    # ------------------------------------------------------------------ #
    def reward(self, state, joint_action, next_state, player):
        if self.is_terminal(state):
            return 0.0
        if player == "player_1":
            return float(next_state[-2] - state[2])
        return float(next_state[-1] - state[3])

    # ------------------------------------------------------------------ #
    def is_terminal(self, state):
        return isinstance(state, tuple) and len(state) > 0 and state[0] == "end"