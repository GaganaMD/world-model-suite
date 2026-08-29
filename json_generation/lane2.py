"""Lane 2 scoring on the v2 schema (see gm_convert.py).

Raw game_matching scores are unnormalised sums that grow with game size, so they are not
comparable across test cases and cannot feed a worst-element aggregation. We normalise
against self-match baselines and report both sides:

    coverage  = score(ref, cand) / score(ref, ref)    how much of the reference is present
    precision = score(ref, cand) / score(cand, cand)  how much of the candidate is justified
    lane2     = harmonic mean, on 0-1

Reporting both matters: omissions cost coverage, inventions cost precision. One number
would hide which way the model went wrong.
"""
from __future__ import annotations
import copy

try:
    from .gm_convert import strip_private, to_game_matching
except ImportError:
    # Supports the standalone notebook workflow that adds json_generation to sys.path.
    from gm_convert import strip_private, to_game_matching
try:
    from game_match import load_game, match
except ImportError:
    load_game = match = None

DEFAULT_SA_ITERS = 3000
DEFAULT_HORIZON = 3


def _prep(model, horizon, unroll):
    if load_game is None:
        raise ImportError(
            "Lane 2 requires the external game_matching repository. Clone "
            "https://github.com/mensch72/game_matching.git and add it to PYTHONPATH."
        )
    g = strip_private(to_game_matching(model, horizon=horizon, unroll=unroll))
    return load_game(g), g


def lane2_score(reference, candidate, horizon=DEFAULT_HORIZON, unroll="always",
                sa_iters=DEFAULT_SA_ITERS, seed=0, use_intrinsic=False):
    A, gA = _prep(reference, horizon, unroll)
    B, gB = _prep(candidate, horizon, unroll)
    kw = dict(seed=seed, sa_iters=sa_iters, use_intrinsic=use_intrinsic)
    res = match(A, B, **kw)
    sa = match(A, load_game(copy.deepcopy(gA)), **kw)["score"]
    sb = match(B, load_game(copy.deepcopy(gB)), **kw)["score"]
    cov = res["score"] / sa if sa else 0.0
    pre = res["score"] / sb if sb else 0.0
    f1 = 2 * cov * pre / (cov + pre) if (cov + pre) else 0.0
    readable = {}
    for sA, sB in res["state_map"].items():
        if sA.startswith("__"):
            continue                      # hide the synthetic root
        readable[sA.split("@")[0]] = sB.split("@")[0]
    return {"lane2": round(f1, 4), "coverage": round(cov, 4), "precision": round(pre, 4),
            "player_map": res["player_map"], "state_map_src": readable,
            "assumptions": to_game_matching(reference, horizon=horizon,
                                            unroll=unroll)["_conversion"]["assumptions"]}


def print_lane2(r, name="candidate"):
    print(f"=== Lane 2 {name} ===")
    print(f"  lane2 score .... {r['lane2']:.3f}   (0-1, harmonic mean)")
    print(f"    coverage ..... {r['coverage']:.3f}   how much of the reference is present")
    print(f"    precision .... {r['precision']:.3f}   how much of the candidate is justified")
    print(f"  players matched  {r['player_map']}")
    print(f"  states matched   {r['state_map_src']}")
    for a in r["assumptions"]:
        print(f"  [assumption] {a}")
