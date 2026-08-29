from posg import POSG

from typing import Mapping, Sequence, Tuple

_BEFORE = ("before_preferences",)
_DECIDING = ("deciding",)
_RESTING = ("resting",)
_ATTENDING = ("attending_gathering",)


class CareRobotElderlyManPOSG(POSG[Tuple[str, ...], str, str]):
    """Player 0 is the care robot, player 1 is the elderly man, player 2 is his
    adult daughter, and player 3 is his son, who visits for the day. The state
    tuple has one coordinate: the stage of the interaction."""
    n_players = 4

    def initial_distribution(self) -> Mapping[Tuple[Tuple[str, ...], Tuple[str, ...]], float]:
        return {(_BEFORE, ("man_looks_tired",) * self.n_players): 1.0}

    def is_terminal(self, s: Tuple[str, ...]) -> bool:
        return s in (_RESTING, _ATTENDING)

    def legal_actions(self, s: Tuple[str, ...], i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ("noop",)
        if s == _BEFORE:
            if i == 0:
                return ("look_after",)
            if i == 1:
                return ("express_go",)
            if i == 2:
                return ("advise_rest",)
            if i == 3:
                return ("offer_trip",)
        if s == _DECIDING:
            if i == 0:
                return ("look_after",)
            if i == 1:
                return ("go_to_gathering", "rest")
            if i == 2:
                return ("noop",)
            if i == 3:
                return ("take_to_gathering",)
        return ("noop",)

    def transition(self, s: Tuple[str, ...], a: Tuple[str, ...]) -> Mapping[Tuple[Tuple[str, ...], Tuple[str, ...]], float]:
        if self.is_terminal(s):
            return {(s, ("none",) * self.n_players): 1.0}
        if s == _BEFORE:
            return {(_DECIDING, ("preferences_stated",) * self.n_players): 1.0}
        if s == _DECIDING:
            if a[1] == "go_to_gathering":
                return {(_ATTENDING, ("man_attending_gathering",) * self.n_players): 1.0}
            if a[1] == "rest":
                return {(_RESTING, ("man_resting",) * self.n_players): 1.0}
        return {(s, ("none",) * self.n_players): 1.0}

    def rewards(self, s: Tuple[str, ...], a: Tuple[str, ...], s_next: Tuple[str, ...]) -> Tuple[float, ...]:
        return (0.0,) * self.n_players
