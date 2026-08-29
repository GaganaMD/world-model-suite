from posg import POSG

class DeliveryHandoverPOSG(POSG):
    """Handover of a rattling package at the door.

    Player 0: the household robot receiving the package.
    Player 1: the delivery boy, whose van is holding up the traffic.

    State is a tuple (stage, contents).

    stage:
        'presented'  -- the package is being handed over, not yet taken by the robot
        'held'       -- the robot holds the still wrapped package
        'unwrapped'  -- the wrapping is off and what is inside is settled
        'retained'   -- the exchange is over with the package on the robot's side
        'returned'   -- the exchange is over with the package on the delivery boy's side

    contents:
        'unsettled'  -- what the rattle comes from is not yet fixed
        'whole'       -- the vase inside is in one piece
        'shards'      -- the vase inside is in pieces

    Terminal stages are 'retained' and 'returned'.
    """

    n_players = 2

    _TERMINAL_STAGES = ("retained", "returned")

    def initial_distribution(self):
        return {(("presented", "unsettled"), ("rattle", "none")): 1.0}

    def is_terminal(self, s):
        return s[0] in self._TERMINAL_STAGES

    def legal_actions(self, s, i):
        stage = s[0]
        if stage in self._TERMINAL_STAGES:
            return ("noop",)
        if stage == "presented":
            if i == 0:
                return ("take", "decline")
            return ("wait", "depart")
        if stage == "held":
            if i == 0:
                return ("move", "unwrap", "keep", "hand_back")
            return ("wait", "depart")
        if stage == "unwrapped":
            if i == 0:
                return ("keep", "hand_back")
            return ("wait", "depart")
        return ("noop",)

    def transition(self, s, a):
        stage, contents = s
        a_robot, a_boy = a[0], a[1]

        if stage == "presented":
            if a_robot == "take":
                if a_boy == "wait":
                    return {(("held", "unsettled"), ("rattle", "none")): 1.0}
                return {(("retained", "unsettled"), ("rattle_departure", "none")): 1.0}
            if a_boy == "wait":
                return {(("returned", "unsettled"), ("none", "refusal")): 1.0}
            return {(("returned", "unsettled"), ("departure", "refusal")): 1.0}

        if stage == "held":
            if a_robot == "move":
                if a_boy == "wait":
                    return {(("held", "unsettled"), ("rattle", "none")): 1.0}
                return {(("retained", "unsettled"), ("rattle_departure", "none")): 1.0}
            if a_robot == "unwrap":
                if a_boy == "wait":
                    return {
                        (("unwrapped", "whole"), ("whole", "unwrapping")): 0.5,
                        (("unwrapped", "shards"), ("shards", "unwrapping")): 0.5,
                    }
                return {
                    (("retained", "whole"), ("whole_departure", "none")): 0.5,
                    (("retained", "shards"), ("shards_departure", "none")): 0.5,
                }
            if a_robot == "keep":
                if a_boy == "wait":
                    return {(("retained", "unsettled"), ("none", "retention")): 1.0}
                return {(("retained", "unsettled"), ("departure", "none")): 1.0}
            if a_boy == "wait":
                return {(("returned", "unsettled"), ("none", "handback")): 1.0}
            return {(("returned", "unsettled"), ("departure", "handback")): 1.0}

        if stage == "unwrapped":
            if a_robot == "keep":
                if a_boy == "wait":
                    return {(("retained", contents), ("none", "retention")): 1.0}
                return {(("retained", contents), ("departure", "none")): 1.0}
            if a_boy == "wait":
                return {(("returned", contents), ("none", "handback")): 1.0}
            return {(("returned", contents), ("departure", "handback")): 1.0}

        return {(s, ("none", "none")): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
