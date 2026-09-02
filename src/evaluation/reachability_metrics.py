"""Objective graph metrics for small declarative POSGs."""
from __future__ import annotations
from collections import deque

def graph_edges(model):
    return {s["id"]: {n["state"] for a in s.get("actions", []) for n in a.get("next", [])}
            for s in model.get("states", [])}

def reachable_states(model, horizon=None):
    edges, seeds = graph_edges(model), {x["state"] for x in model.get("initial", [])}
    seen, q = set(seeds), deque((s, 0) for s in seeds)
    while q:
        s, d = q.popleft()
        if horizon is not None and d >= horizon: continue
        for n in edges.get(s, ()):
            if n not in seen: seen.add(n); q.append((n, d+1))
    return seen

def reversible_edges(model, horizon=8):
    edges = graph_edges(model)
    out = set()
    for s, nxts in edges.items():
        for n in nxts:
            frontier, seen = {n}, {n}
            for _ in range(horizon):
                if s in frontier: out.add((s, n)); break
                frontier = {x for y in frontier for x in edges.get(y, ())} - seen
                seen |= frontier
    return out

def reachable_option_counts(model, horizon=3):
    return {s: len(_from(model, s, horizon)) for s in graph_edges(model)}

def _from(model, seed, horizon):
    edges = graph_edges(model); seen={seed}; frontier={seed}
    for _ in range(horizon):
        frontier={n for s in frontier for n in edges.get(s, ())}-seen; seen |= frontier
    return seen
