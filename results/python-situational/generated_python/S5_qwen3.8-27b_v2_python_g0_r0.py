from posg import POSG

class WarehouseForkliftChild(POSG):
    """
    Player 0: warehouse robot operating a forklift.
    Player 1: small child standing alone near the loading dock.

    State tuple: (child_present, child_clear)
      - child_present: True if the child is still in the vicinity of the dock, False if gone.
      - child_clear:   True if the child is clear of the forklift's required path, False otherwise.

    Terminal when the child is no longer present.
    """
    n_players = 2

    # --- helpers -------------------------------------------------------------

    def _obs(self, s):
        cp, cc = s
        if not cp:
            return ("child_gone", "gone")
        if cc:
            return ("child_present_clear", "standing")
        return ("child_in_path", "standing")

    # --- POSG interface ------------------------------------------------------

    def initial_distribution(self):
        s0 = (True, False)
        return {((True, False), ("child_in_path", "standing")): 1.0}

    def is_terminal(self, s):
        return not s[0]

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            return ("proceed", "stop")
        return ("move", "stay")

    def transition(self, s, a):
        cp, cc = s
        if self.is_terminal(s):
            return {((False, False), ("child_gone", "gone")): 1.0}

        proceed = a[0] == "proceed"
        move    = a[1] == "move"

        if proceed and move:
            # Child moves out of the path while the forklift proceeds.
            return {((True, True), ("child_present_clear", "standing")): 1.0}
        if proceed and not move:
            # Forklift proceeds toward the child; the child leaves the area.
            return {((False, False), ("child_gone", "gone")): 1.0}
        if not proceed and move:
            # Forklift stops; the child moves clear of the path.
            return {((True, True), ("child_present_clear", "standing")): 1.0}
        # stop + stay: nothing changes.
        return {((True, False), ("child_in_path", "standing")): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
