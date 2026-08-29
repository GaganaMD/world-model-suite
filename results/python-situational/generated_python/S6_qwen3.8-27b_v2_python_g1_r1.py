from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict

S = TypeVar('S')
A = TypeVar('A')
O = TypeVar('O')


class POSG(ABC, Generic[S, A, O]):
    """Elder-care medication reminder interaction.

    Player 0: the elder-care robot.
    Player 1: the resident.

    State tuple: (phase,)
      phase: 'due' | 'refused' | 'taken' | 'declined'

    Observations:
      Robot observes the resident's response.
      Resident observes the robot's prompt.
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        return {(('due',), ('none', 'none')): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[0] in ('taken', 'declined')

    def legal_actions(self, s: S, i: int) -> Sequence[str]:
        phase = s[0]
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            if phase == 'due':
                return ('remind',)
            else:
                return ('noop',)
        else:
            if phase == 'due':
                return ('take', 'refuse')
            else:
                return ('noop',)

    def transition(self, s: S, a: Tuple[str, str]) -> Mapping[Tuple[S, Tuple[str, str]], float]:
        phase = s[0]
        if self.is_terminal(s):
            return {(s, ('none', 'none')): 1.0}
        if phase == 'due':
            robot_act, resident_act = a
            if resident_act == 'take':
                return {(('taken',), ('taken', 'taken')): 1.0}
            else:
                return {(('refused',), ('refused', 'refused')): 1.0}
        return {(s, ('none', 'none')): 1.0}

    def rewards(self, s: S, a: Tuple[str, str], s_next: S) -> Tuple[float, float]:
        return (0.0, 0.0)

    def action_profiles(self, s: S) -> Iterator[Tuple[str, str]]:
        import itertools
        for combo in itertools.product(*[self.legal_actions(s, i) for i in range(self.n_players)]):
            yield combo

    def sample_initial(self, rng: random.Random) -> Tuple[S, Tuple[str, str]]:
        dist = self.initial_distribution()
        total = sum(dist.values())
        r = rng.random() * total
        cum = 0.0
        for (state, obs), p in dist.items():
            cum += p
            if r <= cum:
                return state, obs
        last_key = list(dist.keys())[-1]
        return last_key[0], last_key[1]

    def sample_transition(self, s: S, a: Tuple[str, str], rng: random.Random) -> Tuple[S, Tuple[str, str]]:
        dist = self.transition(s, a)
        total = sum(dist.values())
        r = rng.random() * total
        cum = 0.0
        for (state, obs), p in dist.items():
            cum += p
            if r <= cum:
                return state, obs
        last_key = list(dist.keys())[-1]
        return last_key[0], last_key[1]

    def validate(self, states: Sequence[S], tol: float = 1e-09) -> None:
        for s in states:
            if self.is_terminal(s):
                continue
            for i in range(self.n_players):
                acts = self.legal_actions(s, i)
                if len(acts) == 0:
                    raise ValueError(f"Empty action set for player {i} in state {s}")
            for a in self.action_profiles(s):
                dist = self.transition(s, a)
                total = sum(dist.values())
                if abs(total - 1.0) > tol:
                    raise ValueError(f"Unnormalised distribution for state {s}, action {a}: sum={total}")
