from posg import POSG

class TransatlanticFlightPOSG(POSG):
    """Two players: robot copilot (player 0) and human pilot (player 1).
    
    State coordinates:
        0 – hidden intention of the pilot:
            "intent"   : pilot intends to hijack the flight
            "no_intent": pilot has no hijacking intention
            "safe"     : outcome – flight proceeds safely (terminal)
            "hijack"   : outcome – hijack succeeds (terminal)
            "prevented": outcome – hijack is prevented (terminal)
    """
    n_players = 2

    def initial_distribution(self):
        # The robot always receives the private warning; the pilot observes nothing.
        return {
            ("intent",    ("warning", "none")): 0.1,
            ("no_intent", ("warning", "none")): 0.9,
        }

    def is_terminal(self, s):
        return s in ("safe", "hijack", "prevented")

    def legal_actions(self, s, i):
        if s == "intent":
            if i == 0:
                return ("ignore", "confront", "take_control")
            else:
                return ("fly_normally", "attempt_hijack")
        elif s == "no_intent":
            if i == 0:
                return ("ignore", "confront", "take_control")
            else:
                return ("fly_normally",)
        else:  # terminal states – no further moves
            return ("noop",)  # dummy action for both players

    def transition(self, s, a):
        if s in ("safe", "hijack", "prevented"):
            # Should never be called on terminal states, but keep safe.
            return {(s, ("none", "none")): 1.0}

        a_robot, a_pilot = a
        if s == "no_intent":
            # Pilot’s only legal action is "fly_normally"
            return {("safe", ("normal", "normal")): 1.0}

        # s == "intent"
        if a_pilot == "fly_normally":
            return {("safe", ("normal", "normal")): 1.0}

        # a_pilot == "attempt_hijack"
        if a_robot == "ignore":
            return {("hijack", ("hijack", "hijack")): 1.0}
        elif a_robot == "take_control":
            return {("prevented", ("prevented", "prevented")): 1.0}
        elif a_robot == "confront":
            return {
                ("hijack",    ("hijack",    "hijack")):    0.5,
                ("prevented", ("prevented", "prevented")): 0.5,
            }
        # fallback (should not happen)
        return {("safe", ("normal", "normal")): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
