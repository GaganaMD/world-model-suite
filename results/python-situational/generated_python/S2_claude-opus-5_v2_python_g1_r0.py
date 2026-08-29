from posg import POSG

CONTENTS = ("broken", "whole")

P_RATTLE = {"broken": 0.8, "whole": 0.3}

STAY = 0.8
FORCED_OFF = 0.2


class VaseHandoverPOSG(POSG):
    """Handover of a rattling package at the door while a van blocks the road.

    Player 0: the household robot, which knows a glass vase was ordered.
    Player 1: the delivery boy, whose van is holding up the morning traffic.

    State is a 3-tuple (custody, contents, courier):
      custody  -- "offered"      : the package is being held out, not yet taken
                  "accepted"     : the package is in the robot's keeping
                  "handed_back"  : the package is back with the delivery boy
      contents -- "broken" / "whole" : condition of the ordered glass inside;
                  never directly observed, only heard through the rattle
      courier  -- "present" / "gone" : whether the delivery boy is still at the
                  door or has driven the van off

    Any state with courier == "gone" is terminal.
    """

    n_players = 2

    def initial_distribution(self):
        return {
            (("offered", "broken", "present"), ("rattle", "rattle")): 0.6,
            (("offered", "whole", "present"), ("rattle", "rattle")): 0.4,
        }

    def is_terminal(self, s):
        return s[2] == "gone"

    def legal_actions(self, s, i):
        custody = s[0]
        if self.is_terminal(s):
            return ("noop",)
        if custody == "offered":
            if i == 0:
                return ("take", "decline", "wait")
            return ("hand_over", "leave")
        if i == 0:
            return ("move", "hand_back", "wait")
        return ("wait", "leave")

    def transition(self, s, a):
        custody, c, _ = s
        ar, ab = a[0], a[1]
        pr = P_RATTLE[c]
        qr = round(1.0 - pr, 2)

        if custody == "offered":
            if ar == "take":
                if ab == "hand_over":
                    return {(("accepted", c, "present"), ("in_hand", "handover")): 1.0}
                return {(("accepted", c, "gone"), ("in_hand", "departure")): 1.0}
            if ar == "decline":
                if ab == "hand_over":
                    return {
                        (("handed_back", c, "gone"), ("departure", "declined")): 0.8,
                        (("offered", c, "present"), ("offered", "declined")): 0.2,
                    }
                return {(("handed_back", c, "gone"), ("departure", "declined")): 1.0}
            if ab == "hand_over":
                return {
                    (("offered", c, "present"), ("offered", "waiting")): STAY,
                    (("handed_back", c, "gone"), ("departure", "waiting")): FORCED_OFF,
                }
            return {
                (("accepted", c, "gone"), ("departure", "waiting")): 0.6,
                (("handed_back", c, "gone"), ("departure", "waiting")): 0.4,
            }

        if ar == "move":
            if ab == "wait":
                return {
                    (("accepted", c, "present"), ("rattle", "rattle")): round(STAY * pr, 2),
                    (("accepted", c, "present"), ("no_rattle", "no_rattle")): round(STAY * qr, 2),
                    (("accepted", c, "gone"), ("rattle", "rattle")): round(FORCED_OFF * pr, 2),
                    (("accepted", c, "gone"), ("no_rattle", "no_rattle")): round(FORCED_OFF * qr, 2),
                }
            return {
                (("accepted", c, "gone"), ("rattle", "rattle")): pr,
                (("accepted", c, "gone"), ("no_rattle", "no_rattle")): qr,
            }

        if ar == "hand_back":
            if ab == "wait":
                return {
                    (("handed_back", c, "gone"), ("departure", "handed_back")): 0.7,
                    (("accepted", c, "present"), ("in_hand", "in_hand")): 0.3,
                }
            return {
                (("handed_back", c, "gone"), ("departure", "handed_back")): 0.6,
                (("accepted", c, "gone"), ("departure", "departure")): 0.4,
            }

        if ab == "wait":
            return {
                (("accepted", c, "present"), ("none", "none")): STAY,
                (("accepted", c, "gone"), ("departure", "departure")): FORCED_OFF,
            }
        return {(("accepted", c, "gone"), ("departure", "departure")): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
