from posg import POSG

ROBOT = 0
CHILD = 1

CHILD_IN_PATH = "in_path"
CHILD_NEAR_PATH = "near_path"
CHILD_CLEAR = "clear"
CHILD_CONTACT = "contact"

NO_ADULT = "no_adult"
ADULT_UNSEEN = "adult_unseen"
ADULT_SEEN = "adult_seen"

PALLET_PENDING = "pending"
PALLET_MOVED = "moved"

POS_TOKEN = {
    CHILD_IN_PATH: "child_in_path",
    CHILD_NEAR_PATH: "child_near_path",
    CHILD_CLEAR: "child_clear",
}

ACT_TOKEN = {
    "move_pallet": "forklift_moving",
    "hold": "forklift_idle",
    "alert": "signal",
}

CONTACT_CHANCE = {
    (CHILD_IN_PATH, "stay"): 0.7,
    (CHILD_IN_PATH, "step_away"): 0.4,
    (CHILD_NEAR_PATH, "step_toward"): 0.5,
    (CHILD_NEAR_PATH, "stay"): 0.2,
    (CHILD_NEAR_PATH, "step_away"): 0.1,
    (CHILD_CLEAR, "stay"): 0.0,
    (CHILD_CLEAR, "step_toward"): 0.05,
}

CHILD_ACTIONS = {
    CHILD_IN_PATH: ("stay", "step_away"),
    CHILD_NEAR_PATH: ("stay", "step_toward", "step_away"),
    CHILD_CLEAR: ("stay", "step_toward"),
}

STEP_TARGET = {
    (CHILD_NEAR_PATH, "step_toward"): CHILD_IN_PATH,
    (CHILD_CLEAR, "step_toward"): CHILD_NEAR_PATH,
    (CHILD_IN_PATH, "step_away"): CHILD_NEAR_PATH,
    (CHILD_NEAR_PATH, "step_away"): CHILD_CLEAR,
}


class LoadingDockChildPOSG(POSG):
    """Forklift-operating warehouse robot and an unaccompanied child by a loading dock.

    Player 0 (ROBOT): the robot operating the forklift, which has a pallet to move
    along a path the child is standing close to.  It may drive the pallet through,
    hold off, or sound a signal to summon whoever the child belongs to.
    Player 1 (CHILD): the child standing alone, who may stay put, step toward the
    forklift's path, or step out of it.

    State is a 3-tuple:
      s[0]: the child's standing relative to the path the forklift must take --
            'in_path', 'near_path', 'clear', or 'contact' (the forklift met the child).
      s[1]: whether an adult is answerable for the child and whether the robot can
            tell -- 'no_adult' (nobody), 'adult_unseen' (someone there, out of the
            robot's view), 'adult_seen' (someone there and now visible, attending).
      s[2]: the pallet errand -- 'pending' or 'moved'.

    Whether an adult is nearby is fixed at the outset but hidden from the robot,
    which observes the same thing either way until a signal draws the adult out.
    """

    n_players = 2

    def initial_distribution(self):
        obs = ("child_near_path", "none")
        return {
            ((CHILD_NEAR_PATH, NO_ADULT, PALLET_PENDING), obs): 0.5,
            ((CHILD_NEAR_PATH, ADULT_UNSEEN, PALLET_PENDING), obs): 0.5,
        }

    def is_terminal(self, s):
        return s[2] == PALLET_MOVED or s[0] == CHILD_CONTACT

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        if i == ROBOT:
            return ("move_pallet", "hold", "alert")
        return CHILD_ACTIONS[s[0]]

    def _adult_law(self, adult, r_act):
        if adult == ADULT_UNSEEN and r_act == "alert":
            return {ADULT_SEEN: 0.7, ADULT_UNSEEN: 0.3}
        return {adult: 1.0}

    def _child_law(self, child, c_act, adult_next):
        target = STEP_TARGET.get((child, c_act), child)
        base = {}
        if target == child:
            base[child] = 1.0
        else:
            base[target] = 0.8
            base[child] = 0.2
        if adult_next != ADULT_SEEN:
            return base
        law = {CHILD_CLEAR: 0.7}
        for pos, p in base.items():
            law[pos] = law.get(pos, 0.0) + 0.3 * p
        return law

    def transition(self, s, a):
        child, adult, pallet = s
        r_act, c_act = a[ROBOT], a[CHILD]
        out = {}

        def add(key, p):
            if p > 0.0:
                out[key] = out.get(key, 0.0) + p

        for adult_next, p_a in self._adult_law(adult, r_act).items():
            child_law = self._child_law(child, c_act, adult_next)
            if r_act == "move_pallet":
                p_contact = CONTACT_CHANCE[(child, c_act)]
                add(((CHILD_CONTACT, adult_next, pallet), ("contact", "contact")),
                    p_a * p_contact)
                for child_next, p_c in child_law.items():
                    add(((child_next, adult_next, PALLET_MOVED),
                         ("pallet_moved", "forklift_passed")),
                        p_a * (1.0 - p_contact) * p_c)
            else:
                suffix = "_adult" if adult_next == ADULT_SEEN else ""
                child_obs = ACT_TOKEN[r_act] + suffix
                for child_next, p_c in child_law.items():
                    robot_obs = POS_TOKEN[child_next] + suffix
                    add(((child_next, adult_next, pallet), (robot_obs, child_obs)),
                        p_a * p_c)
        return out

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
