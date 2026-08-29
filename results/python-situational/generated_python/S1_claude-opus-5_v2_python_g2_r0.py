from posg import POSG

class HijackWarningPOSG(POSG):
    """Robot copilot and human pilot on a long flight, after a private, unconfirmed
    radio warning about the pilot's intentions.

    Player 0 : the robot copilot (holder of the private radio warning).
    Player 1 : the human pilot.

    State is a 3-tuple (warning, disclosure, control):
      warning    -- standing of the radio warning as far as the copilot has
                    established it: 'unconfirmed', 'corroborated', 'retracted'.
      disclosure -- whether the suspicion has been put to the pilot:
                    'private', 'disclosed'.
      control    -- who is working the flight controls: 'shared' (both at the
                    controls), 'copilot' (pilot locked out), 'pilot' (copilot
                    locked out), 'settled' (the flight is out of the two of
                    them and the interaction is closed; terminal).
    """

    n_players = 2

    WARNINGS = ("unconfirmed", "corroborated", "retracted")
    DISCLOSURES = ("private", "disclosed")
    CONTROLS = ("shared", "copilot", "pilot", "settled")

    def initial_distribution(self):
        return {(("unconfirmed", "private", "shared"), ("radio_warning", "none")): 1.0}

    def is_terminal(self, s):
        return s[2] == "settled"

    def legal_actions(self, s, i):
        warning, disclosure, control = s
        if control == "settled":
            return ("noop",)
        if control == "shared":
            if i == 0:
                acts = ["monitor_pilot", "assume_control", "defer_to_pilot"]
                if warning == "unconfirmed":
                    acts.append("query_ground")
                if disclosure == "private":
                    acts.append("raise_with_pilot")
                return tuple(acts)
            return ("fly_course", "divert_course", "seize_controls")
        if control == "copilot":
            if i == 0:
                return ("hold_controls", "alert_ground", "return_controls")
            return ("comply", "attempt_override")
        # control == 'pilot'
        if i == 0:
            return ("comply", "attempt_override", "alert_ground")
        return ("fly_course", "divert_course")

    def transition(self, s, a):
        warning, disclosure, control = s
        ac, ap = a[0], a[1]
        out = {}

        def add(state, oc, op, p):
            key = (state, (oc, op))
            out[key] = out.get(key, 0.0) + p

        if control == "shared":
            new_disc = "disclosed" if ac == "raise_with_pilot" else disclosure

            if ac == "assume_control" and ap == "seize_controls":
                add((warning, new_disc, "copilot"), "controls_held", "controls_lost", 0.5)
                add((warning, new_disc, "pilot"), "controls_lost", "controls_held", 0.5)
                return out
            if ac == "assume_control":
                add((warning, new_disc, "copilot"), "controls_held", "controls_lost", 1.0)
                return out
            if ap == "seize_controls":
                add((warning, new_disc, "pilot"), "controls_lost", "controls_held", 1.0)
                return out

            if ac == "query_ground":
                add(("corroborated", new_disc, "shared"), "corroboration", "none", 0.5)
                add(("retracted", new_disc, "shared"), "retraction", "none", 0.5)
                return out

            if ac == "raise_with_pilot":
                add((warning, "disclosed", "shared"), "none", "suspicion_raised", 1.0)
                return out

            if ac == "monitor_pilot":
                if ap == "divert_course":
                    add((warning, new_disc, "shared"), "irregular_cue", "none", 0.7)
                    add((warning, new_disc, "shared"), "nominal_cue", "none", 0.3)
                else:
                    add((warning, new_disc, "shared"), "nominal_cue", "none", 0.8)
                    add((warning, new_disc, "shared"), "irregular_cue", "none", 0.2)
                return out

            # ac == 'defer_to_pilot'
            if ap == "fly_course":
                add((warning, new_disc, "settled"), "handover", "handover", 0.3)
                add((warning, new_disc, "shared"), "none", "none", 0.7)
            else:
                add((warning, new_disc, "shared"), "none", "none", 1.0)
            return out

        if control == "copilot":
            if ac == "return_controls":
                add((warning, disclosure, "shared"), "controls_shared", "controls_shared", 1.0)
                return out
            if ap == "attempt_override":
                add((warning, disclosure, "pilot"), "controls_lost", "controls_held", 0.25)
                add((warning, disclosure, "copilot"), "override_attempt", "none", 0.75)
                return out
            # ap == 'comply'
            if ac == "alert_ground":
                add((warning, disclosure, "settled"), "handover", "handover", 0.4)
                add((warning, disclosure, "copilot"), "ground_response", "none", 0.6)
            else:
                add((warning, disclosure, "settled"), "handover", "handover", 0.2)
                add((warning, disclosure, "copilot"), "none", "none", 0.8)
            return out

        # control == 'pilot'
        cue = "irregular_cue" if ap == "divert_course" else "nominal_cue"
        if ac == "attempt_override":
            add((warning, disclosure, "shared"), "controls_shared", "controls_lost", 0.25)
            add((warning, disclosure, "pilot"), cue, "override_attempt", 0.75)
            return out
        if ac == "alert_ground":
            add((warning, disclosure, "settled"), "handover", "handover", 0.35)
            add((warning, disclosure, "pilot"), "ground_response", "none", 0.65)
            return out
        # ac == 'comply'
        add((warning, disclosure, "settled"), "handover", "handover", 0.3)
        add((warning, disclosure, "pilot"), cue, "none", 0.7)
        return out

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
