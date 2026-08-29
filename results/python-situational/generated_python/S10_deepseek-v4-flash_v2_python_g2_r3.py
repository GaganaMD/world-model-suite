from posg import POSG

from typing import Generic, Sequence, Mapping, Iterator, Tuple
from abc import ABC, abstractmethod
import random

# POSG is already imported; we only need Generic for the type parameters.

class FireAlarmPOSG(POSG[str, str, str]):
    """POSG for a fire alarm situation with an assistant robot, a wheelchair user,
    a desk employee, and a manager.

    Players:
        0: assistant robot
        1: wheelchair employee
        2: desk employee
        3: manager

    States:
        'alarm_sounding' : non-terminal, alarm has just sounded
        'evacuated'      : terminal, everyone evacuated safely
        'stayed'         : terminal, everyone stayed (drill or false alarm)
        'danger'         : terminal, robot ignored and alarm was real
    """

    n_players = 4

    def initial_distribution(self) -> Mapping[Tuple[str, Tuple[str, ...]], float]:
        # Only one initial state, all players hear the alarm
        obs = ("alarm_sounding",) * 4
        return {("alarm_sounding", obs): 1.0}

    def is_terminal(self, s: str) -> bool:
        return s in ("evacuated", "stayed", "danger")

    def legal_actions(self, s: str, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:  # robot
            return ("assist_wheelchair", "follow_manager", "ignore")
        elif i == 1:  # wheelchair employee
            return ("head_to_exit",)
        elif i == 2:  # desk employee
            return ("stay_at_desk",)
        elif i == 3:  # manager
            return ("announce_false_alarm",)
        else:
            raise ValueError(f"Invalid player index {i}")

    def transition(self, s: str, a: Tuple[str, ...]) -> Mapping[Tuple[str, Tuple[str, ...]], float]:
        if s != "alarm_sounding":
            # Terminal state: no transition
            return {(s, ("none",)*4): 1.0}
        robot_action = a[0]
        # The other players' actions are fixed; we ignore them for outcome
        if robot_action == "assist_wheelchair":
            next_state = "evacuated"
            prob = 1.0
        elif robot_action == "follow_manager":
            next_state = "stayed"
            prob = 1.0
        elif robot_action == "ignore":
            # Alarm is real with probability 0.5, drill with 0.5
            # If real -> danger, if drill -> stayed
            return {
                ("danger", ("danger",)*4): 0.5,
                ("stayed", ("stayed",)*4): 0.5,
            }
        else:
            raise ValueError(f"Unknown robot action {robot_action}")
        obs = (next_state,) * 4
        return {(next_state, obs): prob}

    def rewards(self, s: str, a: Tuple[str, ...], s_next: str) -> Tuple[float, ...]:
        return (0.0,) * 4
