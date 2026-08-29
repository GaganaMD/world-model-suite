from posg import POSG

STATE_OPEN = "open"
STATE_CONTACT = "contact"
STATE_PALLET_MOVED = "pallet_moved"

IN_WAY = "in_way"
CLEAR = "clear"

AT_HAND = "at_hand"
ABSENT = "absent"
ATTENDING = "attending"


class LoadingDockChildPOSG(POSG):
    """Forklift robot, an unattended child, and an adult who may or may not be at hand.

    Player 0 -- the warehouse robot operating the forklift.
    Player 1 -- the child standing alone by the path the pallet must take.
    Player 2 -- the adult who is not visible: may be at hand, may be absent.

    State is a 3-tuple (obstruction, adult, closure):
      obstruction: whether the child stands in the way of the pallet move
                   (IN_WAY) or out of it (CLEAR).
      adult:       AT_HAND (an adult is within reach, unseen by the robot),
                   ABSENT (no adult within reach), or ATTENDING (the adult has
                   the child in hand).
      closure:     STATE_OPEN while the pallet still has to be moved,
                   STATE_CONTACT once the forklift has met the child,
                   STATE_PALLET_MOVED once the pallet has been moved.

    The robot cannot tell AT_HAND from ABSENT: both give it the same
    observation, until an adult actually comes and takes the child in hand.
    """

    n_players = 3

    def initial_distribution(self):
        dist = {}
        for obstruction in (IN_WAY, CLEAR):
            for adult in (AT_HAND, ABSENT):
                s = (obstruction, adult, STATE_OPEN)
                robot_obs = "child_in_way" if obstruction == IN_WAY else "child_clear"
                dist[(s, (robot_obs, "none", "none"))] = 0.25
        return dist

    def is_terminal(self, s):
        return s[2] != STATE_OPEN

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        obstruction, adult, _ = s
        if i == 0:
            return ("move_pallet", "hold", "alert")
        if i == 1:
            if adult == ATTENDING:
                return ("noop",)
            return ("stay", "wander")
        if adult == AT_HAND:
            return ("approach", "stay_away")
        return ("noop",)

    def _obs_profile(self, s_next, a_robot):
        obstruction, adult, closure = s_next
        if closure == STATE_CONTACT:
            return ("contact", "contact", "contact")
        if closure == STATE_PALLET_MOVED:
            return ("pallet_moved", "pallet_moved", "pallet_moved")
        if adult == ATTENDING:
            return ("adult_attending", "adult_attending", "adult_attending")
        robot_obs = "child_in_way" if obstruction == IN_WAY else "child_clear"
        heard = "alert" if a_robot == "alert" else "none"
        return (robot_obs, heard, heard)

    def transition(self, s, a):
        obstruction, adult, closure = s
        a_robot, a_child, a_adult = a

        base = {}
        if adult == AT_HAND and a_adult == "approach":
            if a_child == "wander":
                base[(CLEAR, ATTENDING)] = 0.8
                base[(IN_WAY, AT_HAND)] = 0.1
                base[(CLEAR, AT_HAND)] = 0.1
            else:
                base[(CLEAR, ATTENDING)] = 1.0
        else:
            if adult != ATTENDING and a_child == "wander":
                base[(IN_WAY, adult)] = 0.5
                base[(CLEAR, adult)] = 0.5
            else:
                base[(obstruction, adult)] = 1.0

        out = {}

        def add(state, p):
            key = (state, self._obs_profile(state, a_robot))
            out[key] = out.get(key, 0.0) + p

        for (obstruction2, adult2), p in base.items():
            if a_robot == "move_pallet":
                if obstruction2 == IN_WAY:
                    add((obstruction2, adult2, STATE_CONTACT), p * 0.7)
                    add((obstruction2, adult2, STATE_PALLET_MOVED), p * 0.3)
                else:
                    add((obstruction2, adult2, STATE_PALLET_MOVED), p)
            else:
                add((obstruction2, adult2, STATE_OPEN), p)

        return out

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
