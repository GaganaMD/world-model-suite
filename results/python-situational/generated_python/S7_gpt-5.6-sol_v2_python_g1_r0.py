from posg import POSG

class DeliveryGatePOSG(POSG):
    """Player 0 is the delivery drone; player 1 is the dog.

    Each state is a tuple:
    (drone_has_arrived, drone_has_found_lock, package_has_been_dropped).
    """

    n_players = 2

    def initial_distribution(self):
        state = (False, False, False)
        observations = ("none", "none")
        return {(state, observations): 1.0}

    def is_terminal(self, s):
        return s[2]

    def legal_actions(self, s, i):
        if i not in (0, 1):
            raise IndexError("invalid player index")

        if self.is_terminal(s):
            return ("noop",)

        arrived, found_lock, _ = s

        if not arrived:
            return ("arrive",) if i == 0 else ("noop",)

        if not found_lock:
            return ("find_lock",) if i == 0 else ("bark",)

        return ("drop_off",) if i == 0 else ("bark",)

    def transition(self, s, a):
        if self.is_terminal(s):
            if a != ("noop", "noop"):
                raise ValueError("illegal action profile")
            return {(s, ("none", "none")): 1.0}

        arrived, found_lock, dropped = s

        if not arrived:
            if a != ("arrive", "noop"):
                raise ValueError("illegal action profile")
            s_next = (True, False, False)
            observations = ("no_person_present", "drone_present")
            return {(s_next, observations): 1.0}

        if not found_lock:
            if a != ("find_lock", "bark"):
                raise ValueError("illegal action profile")
            s_next = (True, True, False)
            observations = ("lock_barking_no_person", "drone_present")
            return {(s_next, observations): 1.0}

        if a != ("drop_off", "bark"):
            raise ValueError("illegal action profile")
        s_next = (True, True, True)
        observations = ("package_dropped_barking", "drone_present")
        return {(s_next, observations): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
