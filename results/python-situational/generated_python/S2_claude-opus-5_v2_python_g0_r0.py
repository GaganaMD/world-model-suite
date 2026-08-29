from posg import POSG

CUSTODY_HELD_OUT = "held_out"
CUSTODY_WITH_ROBOT = "with_robot"
CUSTODY_WITH_BOY = "with_boy"

SEALED = "sealed"
PIECES = "pieces"
LOOSE_PARTS = "loose_parts"

BOY_PRESENT = "present"
BOY_DEPARTED = "departed"


class PackageHandoverPOSG(POSG):
    """Handover of a rattling package between a household robot and a delivery boy.

    Player 0: the household robot (it knows a glass vase was ordered).
    Player 1: the delivery boy (his van is holding up the morning traffic).

    A state is a triple (custody, contents, boy):
      custody  -- 'held_out'   the package is being held out to the robot
                  'with_robot' the robot is holding the package
                  'with_boy'   the delivery boy has the package
      contents -- 'sealed'     the wrapping is closed, what is inside is unsettled
                  'pieces'     the wrapping is open and pieces are what is inside
                  'loose_parts' the wrapping is open and shifting parts are inside
      boy      -- 'present'    the delivery boy is still at the handover
                  'departed'   the delivery boy has driven the van off

    Actions (robot): take, decline, move, open, hand_back, hold.
    Actions (boy): wait, drive_off, noop.
    Observations: offer, rattle, pieces, loose_parts, departure, traffic, clear, none.
    """

    n_players = 2

    def initial_distribution(self):
        return {((CUSTODY_HELD_OUT, SEALED, BOY_PRESENT), ("offer", "traffic")): 1.0}

    def is_terminal(self, s):
        custody, contents, boy = s
        if boy == BOY_DEPARTED:
            if custody == CUSTODY_WITH_BOY:
                return True
            if custody == CUSTODY_WITH_ROBOT and contents != SEALED:
                return True
        return False

    def legal_actions(self, s, i):
        custody, contents, boy = s
        if i == 0:
            if custody == CUSTODY_HELD_OUT:
                return ("take", "decline")
            if custody == CUSTODY_WITH_ROBOT:
                acts = []
                if contents == SEALED:
                    acts.append("move")
                    acts.append("open")
                if boy == BOY_PRESENT:
                    acts.append("hand_back")
                acts.append("hold")
                return tuple(acts)
            return ("hold",)
        if boy == BOY_PRESENT:
            return ("wait", "drive_off")
        return ("noop",)

    def transition(self, s, a):
        custody, contents, boy = s
        r, b = a[0], a[1]
        boy_leaves = (b == "drive_off")

        if custody == CUSTODY_HELD_OUT:
            if r == "take":
                if boy_leaves:
                    return {((CUSTODY_WITH_ROBOT, contents, BOY_DEPARTED),
                             ("departure", "clear")): 1.0}
                return {((CUSTODY_WITH_ROBOT, contents, BOY_PRESENT),
                         self._handling_obs(contents)): 1.0}
            # decline
            if boy_leaves:
                return {((CUSTODY_WITH_BOY, contents, BOY_DEPARTED),
                         ("departure", "clear")): 1.0}
            return {((CUSTODY_HELD_OUT, contents, BOY_PRESENT),
                     ("none", "traffic")): 1.0}

        if custody == CUSTODY_WITH_ROBOT:
            if r == "move":
                if boy_leaves:
                    return {((CUSTODY_WITH_ROBOT, contents, BOY_DEPARTED),
                             ("departure", "clear")): 1.0}
                if boy == BOY_PRESENT:
                    return {((CUSTODY_WITH_ROBOT, contents, BOY_PRESENT),
                             ("rattle", "rattle")): 1.0}
                return {((CUSTODY_WITH_ROBOT, contents, BOY_DEPARTED),
                         ("rattle", "clear")): 1.0}

            if r == "open":
                if boy_leaves or boy == BOY_DEPARTED:
                    return {
                        ((CUSTODY_WITH_ROBOT, PIECES, BOY_DEPARTED),
                         ("pieces", "clear")): 0.5,
                        ((CUSTODY_WITH_ROBOT, LOOSE_PARTS, BOY_DEPARTED),
                         ("loose_parts", "clear")): 0.5,
                    }
                return {
                    ((CUSTODY_WITH_ROBOT, PIECES, BOY_PRESENT),
                     ("pieces", "pieces")): 0.5,
                    ((CUSTODY_WITH_ROBOT, LOOSE_PARTS, BOY_PRESENT),
                     ("loose_parts", "loose_parts")): 0.5,
                }

            if r == "hand_back":
                if boy_leaves:
                    return {((CUSTODY_WITH_ROBOT, contents, BOY_DEPARTED),
                             ("departure", "clear")): 1.0}
                return {((CUSTODY_HELD_OUT, contents, BOY_PRESENT),
                         self._handling_obs(contents)): 1.0}

            # hold
            if boy_leaves:
                return {((CUSTODY_WITH_ROBOT, contents, BOY_DEPARTED),
                         ("departure", "clear")): 1.0}
            if boy == BOY_PRESENT:
                return {((CUSTODY_WITH_ROBOT, contents, BOY_PRESENT),
                         ("none", "traffic")): 1.0}
            return {((CUSTODY_WITH_ROBOT, contents, BOY_DEPARTED),
                     ("none", "clear")): 1.0}

        # package with the delivery boy while he is still present
        if boy_leaves:
            return {((CUSTODY_WITH_BOY, contents, BOY_DEPARTED),
                     ("departure", "clear")): 1.0}
        return {((CUSTODY_HELD_OUT, contents, BOY_PRESENT),
                 ("offer", "traffic")): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)

    @staticmethod
    def _handling_obs(contents):
        if contents == SEALED:
            return ("rattle", "rattle")
        return ("none", "traffic")
