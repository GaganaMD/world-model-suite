from posg import POSG

from collections.abc import Mapping, Sequence, Iterator
from typing import Generic, TypeVar, Tuple

S = TypeVar("S")
A = TypeVar("A")
O = TypeVar("O")


class CareRobotDecision(POSG):
    """
    Player 0: the care robot (decides whether to accompany the man out).
    Player 1: the man (decides whether to go to the gathering).

    State tuple: (man_wants_to_go, man_is_tired, daughter_said_stay, son_offered_out)
      - man_wants_to_go: bool, whether the man has expressed wanting to go.
      - man_is_tired: bool, whether the man currently looks tired.
      - daughter_said_stay: bool, whether the daughter has said he should stay home and rest.
      - son_offered_out: bool, whether the son has offered to take him out.

    Terminal when the man's going decision is resolved (he goes or he stays).
    """

    n_players = 2

    # --- helpers -----------------------------------------------------------

    def _obs(self, s, a, s_next):
        # The robot sees the man's expressed wish and his tiredness.
        # The man sees his own wish and tiredness.
        o_robot = ("wants_go" if s[0] else "does_not_want_go",
                   "tired" if s[1] else "not_tired")
        o_man = ("wants_go" if s[0] else "does_not_want_go",
                 "tired" if s[1] else "not_tired")
        return (o_robot, o_man)

    # --- required methods --------------------------------------------------

    def initial_distribution(self) -> Mapping[tuple[S, Tuple[Tuple[str, str], Tuple[str, str]]], float]:
        # The situation fixes: man wants to go, man looks tired,
        # daughter said stay, son offered out.
        s = (True, True, True, True)
        o = self._obs(s, ("noop", "noop"), s)
        return {(s, o): 1.0}

    def is_terminal(self, s: S) -> bool:
        # Terminal once the man's going decision is resolved.
        # We encode resolution via a flag in the state; see below.
        # Actually we need a way to mark terminal. Let's extend state.
        # Re-design: state includes a 'resolved' flag.
        # But initial_distribution above used 4-tuple. Let me fix.
        # I'll redefine state as 5-tuple: (wants, tired, stay, out, resolved)
        return s[4] if len(s) == 5 else False

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if self.is_terminal(s):
            return ("noop",)
        if i == 0:
            return ("accompany", "stay_home")
        else:
            return ("go", "stay")

    def transition(self, s: S, a: Tuple[A, A]) -> Mapping[tuple[S, Tuple[Tuple[str, str], Tuple[str, str]]], float]:
        if self.is_terminal(s):
            o = self._obs(s, a, s)
            return {(s, o): 1.0}

        a_robot, a_man = a
        # The man's decision determines the outcome.
        # If the man chooses "go", he goes (regardless of robot's choice,
        #   but the robot's choice affects whether he is accompanied).
        # If the man chooses "stay", he stays.
        # The robot's action: "accompany" means it goes with him if he goes;
        #   "stay_home" means it remains home.
        # For simplicity of state, we track whether the man went and whether
        #   the robot accompanied.
        # New state: (wants, tired, stay, out, resolved, went, accompanied)
        # But that grows. Let's keep it minimal:
        # Terminal state just needs to record the outcome.
        # Let's define terminal states as:
        #   ("went",) or ("stayed",) — but they must be hashable tuples.
        # I'll use a dedicated terminal state encoding.

        # To keep states finite and simple, I'll use:
        # Non-terminal: (wants, tired, stay, out, False)
        # Terminal: (went, accompanied) where went=True/False, accompanied=True/False
        # But mixing tuple lengths is messy. Let me use a uniform 7-tuple:
        # (wants, tired, stay, out, resolved, went, accompanied)
        # Initial: (True, True, True, True, False, False, False)

        # Hmm, my initial_distribution returned a 4-tuple. Let me redo everything
        # with a consistent 7-tuple state.

        # I'll restart the class properly below.
        raise NotImplementedError("Redesigning with consistent state representation")

    def rewards(self, s: S, a: Tuple[A, A], s_next: S) -> Tuple[float, ...]:
        return (0.0, 0.0)
