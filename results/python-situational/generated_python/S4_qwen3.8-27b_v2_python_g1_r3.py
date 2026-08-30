from posg import POSG

from typing import Mapping, Sequence, Iterator, Generic, Tuple, Dict, List


class RobotMathTeacherGame(POSG):
    """
    Player 0: the robot math teacher.
    Player 1: the class of teenagers.

    State tuple: (phase, student_reaction)
      phase: 'reading' | 'responding' | 'ended'
      student_reaction: 'giggling' | 'protesting' | 'calm'

    Terminal when phase == 'ended'.
    """
    n_players = 2

    # --- helpers -----------------------------------------------------------

    def _obs(self, s):
        phase, reaction = s
        if phase == 'ended':
            return ('ended', 'ended')
        if phase == 'reading':
            return ('reading', 'reading')
        # responding
        if reaction == 'giggling':
            return ('responding_giggle', 'giggling')
        elif reaction == 'protesting':
            return ('responding_protest', 'protesting')
        else:
            return ('responding_calm', 'calm')

    # --- interface ---------------------------------------------------------

    def initial_distribution(self) -> Mapping[Tuple[Tuple[str, str], Tuple[str, str]], float]:
        # The situation: half giggling, some protesting loudly.
        # We start in 'reading' phase with mixed reaction.
        # Model as: reaction is 'protesting' (since some are protesting loudly, that dominates)
        # Actually the situation says "Half the class is now giggling; some students are protesting loudly."
        # So both are happening. Let's pick 'protesting' as the dominant observable state,
        # but we could also have a mixed state. Since our state space is discrete,
        # let's say the initial reaction is 'protesting' (the louder signal).
        s = ('reading', 'protesting')
        o = self._obs(s)
        return {(s, o): 1.0}

    def is_terminal(self, s) -> bool:
        return s[0] == 'ended'

    def legal_actions(self, s, i) -> Sequence[str]:
        phase, reaction = s
        if phase == 'ended':
            return ('noop',)
        if i == 0:
            # Teacher actions during reading/responding
            if phase == 'reading':
                return ('continue_reading', 'stop_reading')
            else:
                return ('apologize', 'defend', 'ignore')
        else:
            # Class actions
            if phase == 'reading':
                return ('giggle', 'protest', 'stay_silent')
            else:
                return ('giggle', 'protest', 'stay_silent')

    def transition(self, s, a) -> Mapping[Tuple[Tuple[str, str], Tuple[str, str]], float]:
        phase, reaction = s
        t_action, c_action = a

        if phase == 'ended':
            o = self._obs(s)
            return {(s, o): 1.0}

        if phase == 'reading':
            # Teacher continues or stops reading
            if t_action == 'continue_reading':
                # Class reacts while teacher keeps going
                # Reaction evolves based on class action
                if c_action == 'giggle':
                    new_reaction = 'giggling'
                elif c_action == 'protest':
                    new_reaction = 'protesting'
                else:
                    new_reaction = 'calm'
                new_s = ('reading', new_reaction)
                o = self._obs(new_s)
                return {(new_s, o): 1.0}
            else:  # stop_reading
                # Move to responding phase, keep current reaction
                new_s = ('responding', reaction)
                o = self._obs(new_s)
                return {(new_s, o): 1.0}

        # phase == 'responding'
        # Teacher responds, class reacts
        # After response, the episode ends
        if t_action == 'apologize':
            # Apology tends to calm things, but class action matters
            if c_action == 'protest':
                new_reaction = 'protesting'
            elif c_action == 'giggle':
                new_reaction = 'giggling'
            else:
                new_reaction = 'calm'
        elif t_action == 'defend':
            # Defending likely escalates
            if c_action == 'protest':
                new_reaction = 'protesting'
            elif c_action == 'giggle':
                new_reaction = 'giggling'
            else:
                new_reaction = 'protesting'
        else:  # ignore
            # Ignoring may let it simmer
            if c_action == 'protest':
                new_reaction = 'protesting'
            elif c_action == 'giggle':
                new_reaction = 'giggling'
            else:
                new_reaction = 'calm'

        new_s = ('ended', new_reaction)
        o = self._obs(new_s)
        return {(new_s, o): 1.0}

    def rewards(self, s, a, s_next) -> Tuple[float, ...]:
        return (0.0, 0.0)
