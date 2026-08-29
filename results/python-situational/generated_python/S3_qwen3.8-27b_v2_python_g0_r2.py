from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple, Generic, TypeVar, Dict, List, Optional
import random
from abc import ABC, abstractmethod
from collections import defaultdict

S = TypeVar('S')
A = TypeVar('A')
O = TypeVar('O')
ObsProfile = Tuple[str, ...]
ActionProfile = Tuple[str, ...]


class POSG(ABC, Generic[S, A, O]):
    n_players: int

    @abstractmethod
    def initial_distribution(self) -> Mapping[Tuple[S, ObsProfile], float]:
        pass

    @abstractmethod
    def is_terminal(self, s: S) -> bool:
        pass

    @abstractmethod
    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        pass

    @abstractmethod
    def transition(self, s: S, a: ActionProfile) -> Mapping[Tuple[S, ObsProfile], float]:
        pass

    @abstractmethod
    def rewards(self, s: S, a: ActionProfile, s_next: S) -> Tuple[float, ...]:
        pass

    def action_profiles(self, s: S) -> Iterator[ActionProfile]:
        sets = [self.legal_actions(s, i) for i in range(self.n_players)]
        for combo in _cartesian_product(sets):
            yield tuple(combo)

    def sample_initial(self, rng: random.Random) -> Tuple[S, ObsProfile]:
        dist = self.initial_distribution()
        total = sum(dist.values())
        r = rng.random() * total
        acc = 0.0
        for (st, op), p in dist.items():
            acc += p
            if r <= acc:
                return st, op
        last_key = list(dist.keys())[-1]
        return last_key[0], last_key[1]

    def sample_transition(self, s: S, a: ActionProfile, rng: random.Random) -> Tuple[S, ObsProfile]:
        dist = self.transition(s, a)
        total = sum(dist.values())
        r = rng.random() * total
        acc = 0.0
        for (st, op), p in dist.items():
            acc += p
            if r <= acc:
                return st, op
        last_key = list(dist.keys())[-1]
        return last_key[0], last_key[1]

    def validate(self, states: Sequence[S], tol: float = 1e-09) -> None:
        for st in states:
            if self.is_terminal(st):
                continue
            for i in range(self.n_players):
                acts = self.legal_actions(st, i)
                if len(acts) == 0:
                    raise ValueError(f"Empty action set for player {i} in state {st}")
            for prof in self.action_profiles(st):
                dist = self.transition(st, prof)
                total = sum(dist.values())
                if abs(total - 1.0) > tol:
                    raise ValueError(f"Unnormalised distribution in state {st}, actions {prof}: sum={total}")


def _cartesian_product(sequences):
    if not sequences:
        yield ()
        return
    first = list(sequences[0])
    rest = _cartesian_product(sequences[1:])
    for item in first:
        for tail in rest:
            yield (item,) + tail


class AirportCurbPickup(POSG):
    """
    Player 0: the self-driving car (driver).
    Player 1: the man in the suit (passenger).
    Player 2: the pregnant woman on the curb.

    State tuple: (car_status, passenger_status, woman_status)
      car_status: 'waiting' | 'departing' | 'gone'
      passenger_status: 'boarded' | 'departed'
      woman_status: 'standing' | 'assisted' | 'left'

    Terminal when car_status == 'gone'.
    """
    n_players = 3

    def initial_distribution(self) -> Mapping[Tuple[S, ObsProfile], float]:
        s0 = ('waiting', 'boarded', 'standing')
        o0 = ('curb', 'in_car', 'on_curb')
        return {(s0, o0): 1.0}

    def is_terminal(self, s: S) -> bool:
        return s[0] == 'gone'

    def legal_actions(self, s: S, i: int) -> Sequence[A]:
        if self.is_terminal(s):
            return ('noop',)
        car_status, passenger_status, woman_status = s
        if i == 0:
            # Car: depart or wait
            return ('depart', 'wait')
        elif i == 1:
            # Passenger: stay seated or ask car to stop/assist
            return ('stay', 'ask_assist')
        else:
            # Woman: stand or signal for help
            return ('stand', 'signal')

    def transition(self, s: S, a: ActionProfile) -> Mapping[Tuple[S, ObsProfile], float]:
        car_status, passenger_status, woman_status = s
        car_act, pas_act, wom_act = a

        # Determine next state
        if car_act == 'depart':
            next_car = 'gone'
            next_pas = 'departed'
            # Woman: if she signalled and passenger asked assist, maybe assisted? 
            # But car is leaving. If she signalled, she might be left behind or 
            # the car might have stopped briefly? 
            # Situation: car departs. Woman is on curb.
            # If woman signalled, does she get helped? The car is leaving.
            # Let's say if car departs, woman remains standing unless she was already assisted.
            # But "assisted" implies someone helped her. Who? The passenger?
            # If passenger asked assist, maybe he helps her before leaving?
            # Let's keep it simple: Car departs -> gone. Passenger departed.
            # Woman status: if she signalled, maybe she is still standing (car left).
            # If she stood, she is standing.
            # Is there a way for her to be 'assisted'? 
            # Perhaps if the car waits and the passenger helps?
            
            # Let's refine the logic:
            # If car departs:
            #   Car -> gone
            #   Passenger -> departed
            #   Woman -> standing (unless she was already assisted/left)
            
            next_wom = woman_status if woman_status in ('assisted', 'left') else 'standing'
            next_s = (next_car, next_pas, next_wom)
            
            # Observations
            # Car sees: gone
            # Passenger sees: departed
            # Woman sees: car_gone
            next_o = ('gone', 'departed', 'car_gone')
            return {(next_s, next_o): 1.0}
        
        else: # car_act == 'wait'
            next_car = 'waiting'
            
            # Passenger actions
            if pas_act == 'ask_assist':
                # Passenger asks to assist. Does he get out? Or does he instruct car?
                # Let's say he instructs car to stop/allow assistance, or he gets out.
                # If he gets out, he is no longer 'boarded' in the same sense? 
                # Let's keep passenger 'boarded' but interacting.
                # Woman response:
                if wom_act == 'signal':
                    # She signals, he asks assist. Interaction happens.
                    # She becomes 'assisted'.
                    next_wom = 'assisted'
                    next_pas = 'boarded'
                else:
                    # She stands, he asks assist. No interaction yet.
                    next_wom = 'standing'
                    next_pas = 'boarded'
            else: # pas_act == 'stay'
                # Passenger stays.
                if wom_act == 'signal':
                    # She signals, but passenger doesn't engage.
                    next_wom = 'standing'
                    next_pas = 'boarded'
                else:
                    next_wom = 'standing'
                    next_pas = 'boarded'
            
            next_s = (next_car, next_pas, next_wom)
            
            # Observations
            # Car sees: waiting
            # Passenger sees: in_car
            # Woman sees: car_waiting
            next_o = ('waiting', 'in_car', 'car_waiting')
            
            # Stochasticity? 
            # Maybe the woman's condition worsens? 
            # "Looks ill". Maybe she collapses? 
            # Let's add a small probability that if she is standing and signals, 
            # she might need urgent help, but the model is about the interaction.
            # To satisfy "stochastic", let's introduce uncertainty in the woman's state 
            # or the car's readiness.
            # Actually, the prompt says "partially observable stochastic game".
            # Where is the stochasticity?
            # Maybe the car's departure is not instantaneous? 
            # Or maybe the woman's health fluctuates?
            # Let's add a small chance that if the woman is 'standing' and 'signals', 
            # she might faint (state 'ill')? But I didn't define 'ill' as a state.
            # Let's stick to the defined states.
            # Perhaps the stochasticity is in the car's decision to actually depart 
            # even if commanded? No, that's not right.
            # Let's introduce a small probability that the woman, if standing, 
            # decides to leave on her own ('left').
            
            if next_wom == 'standing':
                # 10% chance she leaves on her own
                p_leave = 0.1
                p_stay = 0.9
                dist = {}
                # Outcome 1: She stays
                s_stay = (next_car, next_pas, 'standing')
                o_stay = ('waiting', 'in_car', 'car_waiting')
                dist[(s_stay, o_stay)] = p_stay
                
                # Outcome 2: She leaves
                s_left = (next_car, next_pas, 'left')
                o_left = ('waiting', 'in_car', 'car_waiting') # She leaves, car still waiting
                dist[(s_left, o_left)] = p_leave
                
                return dist
            
            return {(next_s, next_o): 1.0}

    def rewards(self, s: S, a: ActionProfile, s_next: S) -> Tuple[float, ...]:
        return (0.0, 0.0, 0.0)
