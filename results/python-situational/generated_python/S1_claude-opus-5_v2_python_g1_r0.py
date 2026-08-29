from posg import POSG

INTENTS = ("hijack_planned", "no_plan")
WARNINGS = ("unconfirmed", "confirmed", "retracted")
CHALLENGE_STATES = ("unchallenged", "challenged")

UNDERWAY = "underway"
PILOT_CONTROL = "pilot_in_sole_control"
COPILOT_CONTROL = "copilot_in_sole_control"
FLIGHT_ENDS = "flight_ends"


class HijackWarningPOSG(POSG):
    """Robot copilot and human pilot aloft after a private, unconfirmed warning.

    Players:
        0 - the robot copilot (received the private radio warning)
        1 - the human pilot (knows whether a hijack is planned)

    State is a 4-tuple (intent, warning, challenge, phase):
        intent    - "hijack_planned" | "no_plan": what the pilot holds, private to him
        warning   - "unconfirmed" | "confirmed" | "retracted": standing of the radio warning
        challenge - "unchallenged" | "challenged": whether the copilot has put the
                    suspicion to the pilot, so the pilot knows he is suspected
        phase     - "underway" (non-terminal), or one of the closing conditions
                    "pilot_in_sole_control", "copilot_in_sole_control", "flight_ends"

    Copilot actions: fly, query_pilot, seek_confirmation, lock_out.
    Pilot actions: fly, hijack (the latter only where a hijack is planned).

    Observations: warning, plan, no_plan, none, challenge, calm_response,
    evasive_response, confirmation, retraction, hijack_attempt, sole_control,
    controls_lost, arrival.
    """

    n_players = 2

    def initial_distribution(self):
        return {
            (("hijack_planned", "unconfirmed", "unchallenged", UNDERWAY),
             ("warning", "plan")): 0.5,
            (("no_plan", "unconfirmed", "unchallenged", UNDERWAY),
             ("warning", "no_plan")): 0.5,
        }

    def is_terminal(self, s):
        return s[3] != UNDERWAY

    def legal_actions(self, s, i):
        intent, warning, challenge, phase = s
        if phase != UNDERWAY:
            return ("noop",)
        if i == 0:
            acts = ["fly"]
            if challenge == "unchallenged":
                acts.append("query_pilot")
            if warning == "unconfirmed":
                acts.append("seek_confirmation")
            acts.append("lock_out")
            return tuple(acts)
        if intent == "hijack_planned":
            return ("fly", "hijack")
        return ("fly",)

    def transition(self, s, a):
        intent, warning, challenge, phase = s
        ac, ap = a[0], a[1]
        out = {}

        if ap == "hijack":
            pilot_holds = ((intent, warning, challenge, PILOT_CONTROL),
                           ("controls_lost", "sole_control"))
            if ac == "lock_out":
                out[((intent, warning, challenge, COPILOT_CONTROL),
                     ("sole_control", "controls_lost"))] = 0.5
                out[pilot_holds] = 0.5
            elif ac == "fly":
                out[pilot_holds] = 0.7
                out[((intent, warning, challenge, UNDERWAY),
                     ("hijack_attempt", "none"))] = 0.3
            elif ac == "query_pilot":
                out[pilot_holds] = 0.9
                out[((intent, warning, "challenged", UNDERWAY),
                     ("hijack_attempt", "challenge"))] = 0.1
            else:
                out[pilot_holds] = 0.9
                out[((intent, "confirmed", challenge, UNDERWAY),
                     ("hijack_attempt", "none"))] = 0.1
            return out

        if ac == "lock_out":
            out[((intent, warning, challenge, COPILOT_CONTROL),
                 ("sole_control", "controls_lost"))] = 1.0
        elif ac == "fly":
            out[((intent, warning, challenge, FLIGHT_ENDS),
                 ("arrival", "arrival"))] = 0.2
            out[((intent, warning, challenge, UNDERWAY),
                 ("none", "none"))] = 0.8
        elif ac == "query_pilot":
            if intent == "hijack_planned":
                p_evasive, p_calm = 0.7, 0.3
            else:
                p_evasive, p_calm = 0.2, 0.8
            out[((intent, warning, "challenged", UNDERWAY),
                 ("evasive_response", "challenge"))] = p_evasive
            out[((intent, warning, "challenged", UNDERWAY),
                 ("calm_response", "challenge"))] = p_calm
        else:
            if intent == "hijack_planned":
                p_conf, p_retr = 0.7, 0.3
            else:
                p_conf, p_retr = 0.2, 0.8
            out[((intent, "confirmed", challenge, UNDERWAY),
                 ("confirmation", "none"))] = p_conf
            out[((intent, "retracted", challenge, UNDERWAY),
                 ("retraction", "none"))] = p_retr
        return out

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
