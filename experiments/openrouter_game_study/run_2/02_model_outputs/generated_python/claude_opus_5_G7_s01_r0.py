class GeneratedPOSG(AbstractPOSG):
    """
    Classic two-suspect interrogation (prisoner's dilemma) with a chance element:
    the prosecutor may or may not have partial evidence, which is privately hinted
    to each suspect before they simultaneously choose to stay silent or testify.

    States (all strings):
      "start"                     - chance node: evidence strength drawn
      "interrogate_weak"          - decision node, weak evidence
      "interrogate_strong"        - decision node, strong evidence
      "terminal_<ev>_<a1><a2>"    - terminal outcome
    """

    EVIDENCE = ["weak", "strong"]

    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "start"

    def legal_actions(self, state, player):
        if state == "start":
            # chance node modeled as a no-op joint action
            return ["wait"]
        if state in ("interrogate_weak", "interrogate_strong"):
            return ["silent", "testify"]
        return ["wait"]

    def transition(self, state, joint_action):
        if state == "start":
            return {"interrogate_weak": 0.5, "interrogate_strong": 0.5}

        if state in ("interrogate_weak", "interrogate_strong"):
            ev = "weak" if state == "interrogate_weak" else "strong"
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            if a1 not in ("silent", "testify"):
                a1 = "silent"
            if a2 not in ("silent", "testify"):
                a2 = "silent"
            c1 = "S" if a1 == "silent" else "T"
            c2 = "S" if a2 == "silent" else "T"
            return {"terminal_" + ev + "_" + c1 + c2: 1.0}

        return {"terminal_weak_SS": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "start":
            if next_state == "interrogate_strong":
                hint = "prosecutor_hints_strong_case"
            else:
                hint = "prosecutor_hints_weak_case"
            return f"phase=interrogation;hint={hint};room=isolated;player={player}"

        if state in ("interrogate_weak", "interrogate_strong"):
            ev = "weak" if state == "interrogate_weak" else "strong"
            own = joint_action.get(player, "silent")
            if own not in ("silent", "testify"):
                own = "silent"
            other = "player_2" if player == "player_1" else "player_1"
            other_act = joint_action.get(other, "silent")
            if other_act not in ("silent", "testify"):
                other_act = "silent"
            return (
                f"phase=verdict;evidence={ev};my_choice={own};"
                f"other_choice={other_act};state={next_state}"
            )

        return f"phase=closed;state={next_state};player={player}"

    def reward(self, state, joint_action, next_state, player):
        if state not in ("interrogate_weak", "interrogate_strong"):
            return 0.0

        own = joint_action.get(player, "silent")
        other = "player_2" if player == "player_1" else "player_1"
        opp = joint_action.get(other, "silent")
        if own not in ("silent", "testify"):
            own = "silent"
        if opp not in ("silent", "testify"):
            opp = "silent"

        # Sentences (years) as negative payoffs; strong evidence worsens sentences.
        if own == "silent" and opp == "silent":
            base = -1.0
        elif own == "testify" and opp == "testify":
            base = -6.0
        elif own == "testify" and opp == "silent":
            base = 0.0
        else:  # own silent, opp testifies
            base = -10.0

        if state == "interrogate_strong":
            if base < 0.0:
                base -= 2.0
            else:
                base = -1.0  # even a cooperator with prosecution serves a little time
        return float(base)

    def is_terminal(self, state):
        return isinstance(state, str) and state.startswith("terminal_")
