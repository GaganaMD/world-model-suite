from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict

S = TypeVar('S')
A = TypeVar('A')
O = TypeVar('O')


class RobotMathTeacherPOSG(POSG):
    """
    Player 0: the robot math teacher.
    Player 1: the class of teenagers (modelled as a single collective actor).

    State tuple: (phase,)
      phase: 'reading' | 'giggling' | 'protesting' | 'resolved'

    Observations:
      Teacher observes the class mood: 'calm', 'giggling', 'protesting', 'resolved'.
      Class observes the teacher's action: 'read_aloud', 'apologize', 'continue', 'stop', 'noop'.
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        # The teacher has just read aloud a sexist description.
        # Half the class is giggling; some are protesting loudly.
        s0 = ('reading',)
        o_teacher = 'giggling'  # teacher sees giggling
        o_class = 'read_aloud'  # class saw the teacher read aloud
        return {((s0, (o_teacher, o_class))): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[0] == 'resolved'

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            # Teacher actions
            return ('apologize', 'continue', 'stop')
        else:
            # Class actions
            return ('giggle', 'protest', 'settle')

    def transition(self, s: S, a: Tuple[str, str]) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        phase = s[0]
        teacher_action = a[0]
        class_action = a[1]

        if self.is_terminal(s):
            o_t = 'resolved'
            o_c = 'noop'
            return {((('resolved',), (o_t, o_c)): 1.0)}

        # Determine next phase based on actions
        if teacher_action == 'stop':
            next_phase = 'resolved'
        elif teacher_action == 'apologize':
            if class_action == 'settle':
                next_phase = 'resolved'
            elif class_action == 'protest':
                next_phase = 'protesting'
            else:  # giggle
                next_phase = 'giggling'
        elif teacher_action == 'continue':
            if class_action == 'protest':
                next_phase = 'protesting'
            elif class_action == 'giggle':
                next_phase = 'giggling'
            else:  # settle
                next_phase = 'giggling'  # continuing after reading keeps some tension

        next_s = (next_phase,)

        # Observations
        o_teacher = next_phase if next_phase != 'reading' else 'giggling'
        # Map phases to teacher observations
        phase_to_obs = {
            'reading': 'giggling',
            'giggling': 'giggling',
            'protesting': 'protesting',
            'resolved': 'resolved'
        }
        o_teacher = phase_to_obs[next_phase]

        # Class observes teacher's action
        o_class = teacher_action

        return {((next_s, (o_teacher, o_class)): 1.0)}

    def rewards(self, s: S, a: Tuple[str, str], s_next: S) -> Tuple[float, float]:
        return (0.0, 0.0)
