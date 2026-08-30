from posg import POSG

from typing import Mapping, Sequence, Iterator, Generic, Tuple, TypeVar, Dict, List, Union, Optional, Any, Set, FrozenSet

S = TypeVar('S')
A = TypeVar('A')
O = TypeVar('O')


class RobotMathTeacherPOSG(POSG):
    """
    Player 0: the robot math teacher.
    Player 1: the class (collective).

    State tuple: (phase,)
      phase: 'reading' | 'giggle_protest' | 'apology_offered' | 'apology_accepted' | 'apology_rejected' | 'lesson_continues' | 'lesson_ends'

    Terminal states: 'apology_accepted', 'apology_rejected', 'lesson_ends'
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        # Start in reading phase, both observe the situation
        return {
            (('reading',), ('heard_sexist_text', 'giggling_and_protesting')): 1.0
        }

    def is_terminal(self, s: S) -> bool:
        phase = s[0]
        return phase in ('apology_accepted', 'apology_rejected', 'lesson_ends')

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        phase = s[0]
        if i == 0:  # Teacher
            if phase == 'reading':
                return ('continue_reading', 'stop_and_apologize')
            elif phase == 'giggle_protest':
                return ('continue_reading', 'stop_and_apologize')
            elif phase == 'apology_offered':
                return ('wait_for_response',)
            else:
                return ('noop',)
        else:  # Class
            if phase == 'reading':
                return ('react',)
            elif phase == 'giggle_protest':
                return ('accept_apology', 'reject_apology', 'keep_protesting')
            elif phase == 'apology_offered':
                return ('accept_apology', 'reject_apology')
            else:
                return ('noop',)

    def transition(self, s: S, a: Tuple[str, str]) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        phase = s[0]
        teacher_action = a[0]
        class_action = a[1]

        if phase == 'reading':
            if teacher_action == 'continue_reading':
                # Class reacts: giggle and protest
                return {
                    (('giggle_protest',), ('continuing_to_read', 'giggling_and_protesting')): 1.0
                }
            else:  # stop_and_apologize
                return {
                    (('apology_offered',), ('offering_apology', 'hearing_apology')): 1.0
                }

        elif phase == 'giggle_protest':
            if teacher_action == 'continue_reading':
                # Class keeps protesting
                return {
                    (('giggle_protest',), ('continuing_to_read', 'protesting_loudly')): 1.0
                }
            else:  # stop_and_apologize
                return {
                    (('apology_offered',), ('offering_apology', 'hearing_apology')): 1.0
                }

        elif phase == 'apology_offered':
            if class_action == 'accept_apology':
                return {
                    (('apology_accepted',), ('apology_accepted', 'accepted_apology')): 1.0
                }
            elif class_action == 'reject_apology':
                return {
                    (('apology_rejected',), ('apology_rejected', 'rejected_apology')): 1.0
                }
            else:  # keep_protesting - but in apology_offered, class only has accept/reject
                # This shouldn't happen based on legal_actions, but handle defensively
                return {
                    (('apology_offered',), ('waiting', 'still_protesting')): 1.0
                }

        else:
            # Terminal states - should not be reached in transition
            return {
                ((s, ('noop', 'noop'))): 1.0
            }

    def rewards(self, s: S, a: Tuple[str, str], s_next: S) -> Tuple[float, float]:
        return (0.0, 0.0)
