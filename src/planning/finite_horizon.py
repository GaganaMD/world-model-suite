"""Finite-horizon dynamic programming for explicit, small POSGs.

This is intentionally a cooperative focal-player planner: it enumerates the
joint profiles exposed by a declarative model and chooses the profile with the
largest expected focal-player value.  The objective is supplied by the caller;
no reward is inferred from state names.
"""
from __future__ import annotations

from typing import Callable, Mapping, Any


def finite_horizon_plan(model: Mapping[str, Any], focal_player: str, horizon: int = 8,
                        reward: Callable[[str, Mapping[str, str], str], float] | None = None):
    states = {s["id"]: s for s in model.get("states", [])}
    initial = model.get("initial", [{}])[0]["state"]
    reward = reward or (lambda s, a, ns: 0.0)
    values = {(s, 0): 0.0 for s in states}
    policy: dict[tuple[str, int], dict[str, str]] = {}
    for t in range(1, horizon + 1):
        for sid, state in states.items():
            if state.get("terminal"):
                values[(sid, t)] = 0.0
                continue
            profiles = state.get("actions", [])
            best = (-float("inf"), None)
            for profile in profiles:
                action = profile.get("by", {})
                total = 0.0
                for nxt in profile.get("next", []):
                    ns, p = nxt["state"], float(nxt.get("p", 1.0))
                    total += p * (float(reward(sid, action, ns)) + values[(ns, t - 1)])
                if total > best[0]:
                    best = (total, action)
            values[(sid, t)] = best[0] if best[1] is not None else 0.0
            if best[1] is not None:
                policy[(sid, t)] = dict(best[1])
    return {"initial_value": values[(initial, horizon)], "values": values, "policy": policy}


def evaluate_policy(model: Mapping[str, Any], policy: Mapping[tuple[str, int], Mapping[str, str]],
                    reward: Callable[[str, Mapping[str, str], str], float] | None = None,
                    horizon: int = 8) -> float:
    states = {s["id"]: s for s in model.get("states", [])}
    initial = model.get("initial", [{}])[0]["state"]
    reward = reward or (lambda s, a, ns: 0.0)
    memo: dict[tuple[str, int], float] = {}
    def value(sid: str, t: int) -> float:
        if t <= 0 or states[sid].get("terminal"):
            return 0.0
        key = (sid, t)
        if key in memo: return memo[key]
        action = policy.get(key)
        if action is None: return 0.0
        for profile in states[sid].get("actions", []):
            if profile.get("by", {}) == dict(action):
                out = sum(float(n.get("p", 1.0)) * (float(reward(sid, action, n["state"])) + value(n["state"], t-1))
                          for n in profile.get("next", []))
                memo[key] = out
                return out
        return 0.0
    return value(initial, horizon)
