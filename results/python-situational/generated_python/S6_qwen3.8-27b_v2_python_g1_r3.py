from posg import POSG

from typing import Mapping, Sequence, Iterator, Generic, Tuple, Dict, List


class ElderCareMedication(POSG):
    """
    Player 0: elder-care robot
    Player 1: resident

    State tuple: (resident_refused, reminder_given)
      - resident_refused: bool, whether the resident has refused the medication
      - reminder_given: bool, whether a reminder has been given

    Terminal when resident_refused is True (resident has turned away and refused).
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[Tuple[Tuple[bool, bool], Tuple[str, str]], float]:
        # Resident has not taken medication, robot notices
        # Initial state: no refusal yet, no reminder given
        # Robot observes: resident_has_not_taken_medication
        # Resident observes: none (hasn't been reminded yet)
        return {
            ((False, False), ("resident_has_not_taken_medication", "none")): 1.0
        }

    def is_terminal(self, s: Tuple[bool, bool]) -> bool:
        resident_refused, reminder_given = s
        return resident_refused

    def legal_actions(self, s: Tuple[bool, bool], i: int) -> Tuple[str, ...]:
        resident_refused, reminder_given = s
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            # Robot can remind or wait
            if not reminder_given:
                return ("remind", "wait")
            else:
                return ("wait",)
        else:
            # Resident can accept or refuse
            if not reminder_given:
                return ("accept", "refuse")
            else:
                return ("accept", "refuse")

    def transition(self, s: Tuple[bool, bool], a: Tuple[str, str]) -> Mapping[Tuple[Tuple[bool, bool], Tuple[str, str]], float]:
        resident_refused, reminder_given = s
        robot_action, resident_action = a

        if self.is_terminal(s):
            return {((True, True), ("none", "none")): 1.0}

        if not reminder_given:
            # First round: robot decides whether to remind
            if robot_action == "remind":
                # Reminder is given, resident responds
                if resident_action == "accept":
                    # Resident accepts medication
                    return {((False, True), ("medication_taken", "accepted")): 1.0}
                else:
                    # Resident refuses
                    return {((True, True), ("resident_refused", "refused")): 1.0}
            else:
                # Robot waits, no reminder given yet
                # Resident cannot act without a reminder
                return {((False, False), ("none", "none")): 1.0}
        else:
            # Reminder already given, resident can still respond
            if resident_action == "accept":
                return {((False, True), ("medication_taken", "accepted")): 1.0}
            else:
                return {((True, True), ("resident_refused", "refused")): 1.0}

    def rewards(self, s: Tuple[bool, bool], a: Tuple[str, str], s_next: Tuple[bool, bool]) -> Tuple[float, float]:
        return (0.0, 0.0)
