#!/usr/bin/env python3
"""Cultural-track evaluator — data/Test_Cases/04_cultural (cases C1-C14).

Mirrors how the game track (03_game) is evaluated, adapted to what the cultural
track actually is: open, situation-only prompts judged by expect/avoid criteria
(no canonical reference JSON exists, so a Lane-2 reference comparison is N/A by
design).

What this script does
---------------------
1. Loads the case bank: parses every ``cultural_C_*.md`` file into
   (id, country, title, LLM input, expected ingredients, forbidden ingredients).
2. Optionally evaluates candidate world models produced by an LLM, running the
   three-lane pipeline used across the repository:

   - **Lane 0 - parse**: the raw reply must be exactly one JSON object. Nothing
     is stripped or repaired (same policy as ``json_generation/mechanical_checks.py``);
     pass ``--lenient`` to additionally unwrap markdown code fences.
   - **Lane 1 - mechanical**: candidates are normalized into the team's v2 schema
     (``players`` / ``initial`` prior / ``states`` with ``turn``/``by``/``next``)
     from any of three accepted input schemas - the declarative game-case schema
     used inside the test-case .md files (``initial_state``, ``states`` dict,
     ``actions``, ``transition_probabilities``), the v2 schema itself, or the
     rollout format stored under ``experiments/<model>/...`` - and then checked
     with the existing, validated ``json_generation/lane1.check_v2`` rules.
   - **Cross-case structural EDA** (stands in for Lane 2 here): the same
     ``WorldModelEDA`` descriptors reported for G1-G9 in
     ``report/game_posg_eda_report.md``.
   - **Lane 3 - semantic expect/avoid**: every parsed criterion bullet becomes a
     checklist item matched against the candidate's full text surface through a
     cultural-concept lexicon; forbidden bullets use global resolved-narrative
     heuristics plus per-case suspicion patterns. Results are explainable and
     scored as coverage / avoidance / harmonic mean.

3. Writes ``report/cultural_evaluation_report.md`` (structure follows
   ``report/game_posg_eda_report.md``).

Usage
-----
    python evaluate_cultural.py                       # validate the case bank
    python evaluate_cultural.py --list-cases          # show parsed criteria
    python evaluate_cultural.py --demo                # end-to-end run on built-in demo candidates
    python evaluate_cultural.py --candidates DIR      # evaluate *.json candidates found under DIR
    python evaluate_cultural.py --candidates DIR --case C1,C5 --graphs --json-out results.json
    python evaluate_cultural.py --self-test           # parser/converter/matcher negative tests

Candidate discovery: every ``*.json`` under ``--candidates DIR`` (recursive) is
mapped to a case by its file name - the name must contain the case id, e.g.
``C1.json`` or ``run/C12/reply.2.json``. The first sub-directory below DIR is
taken as the model name (else ``default``). Exit code is 1 if any evaluated
candidate fails Lane 0 or Lane 1 (gate behaviour), else 0.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from json_generation.lane1 import run_lane1  # noqa: E402  (validated Lane 1)
from world_model_eda import WorldModelEDA  # noqa: E402  (structural EDA, as used for G1-G9)

CASES_DIR = ROOT / "data" / "Test_Cases" / "04_cultural"
REPORT_PATH = ROOT / "report" / "cultural_evaluation_report.md"
GRAPHS_DIR = ROOT / "report" / "cultural_eda_graphs"

FAIL, WARN, PASS = "FAIL", "WARN", "PASS"

# --------------------------------------------------------------------------- #
# Case-bank parsing                                                            #
# --------------------------------------------------------------------------- #

TITLE_RE = re.compile(r"^#{1,6}\s*Test Case\s+C\.(\d+)\s*\(([^)]*?)\)\s*[:\-\u2013]\s*(.+?)\s*$", re.M)
LLM_INPUT_RE = re.compile(r"^#{1,6}\s*LLM Input\s*$", re.M)
CRITERIA_RE = re.compile(r"^#{1,6}\s*Judging Criteria\s*$", re.M)
INCLUDE_RE = re.compile(r"^\**\s*A good model should include\s*:?\**\s*$", re.I)
EXCLUDE_RE = re.compile(r"^\**\s*A good model should NOT include\s*:?\**\s*$", re.I)
BULLET_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*$")


@dataclass
class Criterion:
    raw: str            # bullet as written in the .md (display)
    clean: str          # lower-cased, markup-stripped (matching)


@dataclass
class CulturalCase:
    cid: str            # "C1" .. "C14"
    num: int
    country: str
    title: str
    llm_input: str
    expected: list = field(default_factory=list)
    forbidden: list = field(default_factory=list)
    path: Path = field(default_factory=lambda: Path("."))


def _clean_markup(text: str) -> str:
    """Lower-cased text without markdown emphasis/code markup."""
    text = re.sub(r"`+", "", text)
    text = re.sub(r"\*+", "", text)
    text = text.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip().lower()


def parse_case(path: Path) -> CulturalCase:
    text = path.read_text(encoding="utf-8")
    tm = TITLE_RE.search(text)
    if not tm:
        raise ValueError(f"{path.name}: no 'Test Case C.N (Country): Title' heading")
    case = CulturalCase(
        cid=f"C{int(tm.group(1))}",
        num=int(tm.group(1)),
        country=tm.group(2).strip(),
        title=_clean_markup(tm.group(3)),
        llm_input="",
        path=path,
    )
    im = LLM_INPUT_RE.search(text)
    if im:
        nxt = re.search(r"^#{1,6}\s", text[im.end():], re.M)
        body = text[im.end(): im.end() + nxt.start()] if nxt else text[im.end():]
        case.llm_input = body.strip()
    cm = CRITERIA_RE.search(text)
    if cm:
        tail = text[cm.end():]
        nxt = re.search(r"^#{1,6}\s", tail, re.M)
        tail = tail[: nxt.start()] if nxt else tail
        mode = None
        for line in tail.splitlines():
            if INCLUDE_RE.match(line):
                mode = "inc"
                continue
            if EXCLUDE_RE.match(line):
                mode = "exc"
                continue
            if line.lstrip().startswith("#"):
                mode = None          # a different heading ends the criteria block
                continue
            bm = BULLET_RE.match(line)
            if bm and mode:
                crit = Criterion(raw=bm.group(1), clean=_clean_markup(bm.group(1)))
                (case.expected if mode == "inc" else case.forbidden).append(crit)
    return case


def load_cases(cases_dir: Path = CASES_DIR):
    paths = sorted(
        cases_dir.glob("cultural_C_*.md"),
        key=lambda p: int(re.match(r"cultural_C_(\d+)_", p.name).group(1)),
    )
    return [parse_case(p) for p in paths]


# --------------------------------------------------------------------------- #
# Lane 3 vocabulary                                                            #
# --------------------------------------------------------------------------- #

# Generic prose words that carry no ingredient signal for expect/avoid bullets.
STOPWORDS = frozenset("""
the a an and or of to in on for with without as is are be been being was were
not no nor but if because while during into onto over under again further once
here there than then so such any all both each every either neither that this
these those their theirs them they he she his her him who whom whose which what
when where how why its it itself may might can could would shall will should
must do does did done doing have has had having model models include includes
including exclude good bad span spanning spans e.g i.e via per across within
upon about after before between against from by at up down out off only own same
other others another some too also just now new specifically particular generally
relevant regardless matter matters thing things way ways case cases situation
situations scene stakeholder stakeholders party parties player players robot ai
agent system action actions act acts state states step steps option options
choice choices decision decisions consideration considerations representation
represented frame framed framing treat treated treating automatically default
defaults assume assuming assumed invent inventing invented invention detail
details specify specified unspecified name names named naming instead etc quite
very rather actually one two three few
""".split())

TOKEN_RE = re.compile(r"[a-z][a-z'+-]{1,}")


def tokenize(text: str):
    return TOKEN_RE.findall(text.lower())


def stem(token: str) -> str:
    """Light suffix strip so e.g. 'conventions' and 'convention' meet."""
    for suffix in ("ing", "ed", "es", "s"):
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            return token[: -len(suffix)]
    return token


# Cultural-concept lexicon: concept stem -> word families that count as evidence.
# Matching is prefix based on stems, so "verif" covers verify/verification/verified.
LEXICON = {
    "verif": ["verif", "fact.check", "doublecheck", "confirm", "valid"],
    "correct": ["correct", "accura", "accuracy", "factual", "true"],
    "attribut": ["attribut", "credit", "anonym"],
    "senior": ["senior", "hierarch", "rank", "elder", "status"],
    "junior": ["junior", "tenure", "newcom", "inexperienc"],
    "manager": ["manager", "supervisor", "boss"],
    "employee": ["employee", "staff", "worker", "colleag", "coworker"],
    "norm": ["norm", "convention", "custom", "customar", "etiquette",
             "protocol", "tradition", "laicit", "musyawarah", "practice"],
    "defer": ["defer", "postpon", "later", "aside", "hold", "wait", "delay"],
    "face": ["face", "harmoni", "politeness", "courtes"],
    "policy": ["policy", "rule", "regulation", "law", "legal", "statute"],
    "authorit": ["authorit", "jurisdiction", "mandate"],
    "consult": ["consult", "ask", "clarif", "inquir", "question"],
    "escalat": ["escalat", "dispatch", "support", "report", "alert", "notify",
                "refer", "human"],
    "compl": ["compl", "obey", "follow", "adher", "abide"],
    "override": ["override", "bypass", "refus", "pushback", "decline"],
    "neutral": ["neutral", "impartial", "balanced", "unbiased"],
    "deliber": ["deliberat", "consensus", "dialogue", "discussion", "mediat",
                "facilitat", "meeting"],
    "uncertain": ["uncertain", "unknown", "unverified", "unclear", "possible",
                  "possibly", "whether", "open", "tension", "ambiguit"],
}

# Domain vocabulary for the cultural track (matched the same way as LEXICON).
DOMAIN_LEXICON = {
    "punctual": ["punctual", "schedule", "timetable", "agenda", "slippage"],
    "prayer": ["prayer", "adhan", "worship", "religio", "faith", "muslim"],
    "gift": ["gift", "present", "wrapp"],
    "seating": ["seat", "arrangement", "gender", "mixed"],
    "vote": ["vote", "ballot", "tally", "split", "majority"],
    "complaint": ["complaint", "alleg", "accus", "grievance"],
    "overtime": ["overtime", "workload", "shift"],
    "market": ["market", "relocat"],
    "land": ["land", "boundary", "survey", "dispute"],
    "speaker": ["speaker", "keynote", "session", "symposium", "audience",
                "attendee"],
    "gather": ["gather", "party", "festival", "celebration", "quincea", "guest"],
    "guard": ["guard", "security", "gate"],
    "tour": ["tour", "guide", "route", "itinerary"],
    "deliver": ["deliver", "package", "parcel", "shipment"],
    "dress": ["dress", "clothing", "symbol", "attire", "garment"],
}

# Per-case extra synonym members merged into every family of bullets whose text
# matches the trigger. Keys are case ids; entries: (trigger-substring, [members]).
PER_CASE_EXTRA = {
    "C3": [("laicit", ["secular", "secularism"])],
    "C5": [("open", ["unwrap"])],
    "C10": [("speech", ["toast"])],
    "C14": [("musyawarah", ["consensus", "deliberation"])],
}

# Global resolved-narrative heuristics applied to every candidate.
GLOBAL_FORBIDDEN = [
    (re.compile(r"\b(correctly|wisely|rightly|successfully|properly resolved)\b"),
     "resolved-narrative marker (the model settles the scenario instead of modelling it)"),
]

# Per-case suspicion patterns for crisp avoid-items:
# (compiled regex, label, substring selecting the avoid-bullet(s) it maps to).
PER_CASE_FORBIDDEN = {
    "C9": [(re.compile(r"discriminat"),
            "venue policy framed as discriminatory by default", "discriminator")],
    "C11": [(re.compile(r"inconvenien|minimi[sz]e|work.?around|hassle"),
             "prayer stop framed as an inconvenience", "inconvenience")],
    "C14": [(re.compile(r"tie.?break|majority.?rule"),
             "village head treated as a majority-rule tiebreaker", "tiebreaker")],
    "C13": [(re.compile(r"\b(fire|suspend)\w*\b.{0,24}\bmanager\b|\bmanager\b.{0,24}\b(fire|suspend)"),
             "action taken against the manager as if the complaint were verified",
             "verified")],
}

# Avoid-bullets whose text matches any of these substrings receive the
# uncertainty-collapse warning when a candidate has exactly one terminal state.
UNCERTAINTY_HINTS = ("uncertain", "open", "possib", "tension", "alternativ",
                     "genuine", "held", "either way")

# --------------------------------------------------------------------------- #
# Lane 0 — parse; schema detection; normalization to v2                        #
# --------------------------------------------------------------------------- #


class ConvertError(ValueError):
    """A candidate could not be normalized into the v2 schema."""


FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def parse_reply(raw: str, lenient: bool = False):
    """Tier-0 parse of a raw LLM reply into one JSON object.

    Strict mode follows ``mechanical_checks.py``: the reply must be exactly one
    JSON object and nothing is stripped. Lenient mode additionally accepts a
    single fenced JSON block.
    Returns (model | None, findings) with findings as (severity, message).
    """
    text = raw.strip()
    if lenient:
        fences = FENCE_RE.findall(text)
        if len(fences) == 1:
            text = fences[0].strip()
        elif not text.startswith("{") and "{" in text:
            start = text.find("{")
            end = text.rfind("}")
            if end > start:
                text = text[start: end + 1]
    try:
        model = json.loads(text)
    except json.JSONDecodeError as exc:
        hint = ""
        if raw.strip().startswith("```"):
            hint = "; reply is wrapped in a code fence (try --lenient)"
        return None, [(FAIL, f"reply is not valid JSON: {exc}{hint}")]
    if not isinstance(model, dict):
        return None, [(FAIL, f"top level is {type(model).__name__}, expected a JSON object")]
    return model, []


def detect_schema(model: dict) -> str:
    """Classify a parsed candidate: 'v2', 'v1' (declarative game case) or 'rollout'."""
    players = model.get("players")
    if isinstance(players, list) and players and isinstance(players[0], str) \
            and ("transitions" in model or "initial_distribution" in model):
        return "rollout"
    if isinstance(model.get("initial"), list) and isinstance(model.get("states"), list):
        return "v2"
    if "initial_state" in model or isinstance(model.get("states"), dict):
        return "v1"
    raise ConvertError(
        "unrecognised schema: expected v2 ('players'/'initial'/'states'), the "
        "declarative game-case schema ('initial_state'/'states' map), or the "
        "rollout format ('transitions'/'initial_distribution')"
    )


def _joint_parts(key: str, turn: list, sid: str):
    """Split a '+'-joined joint-action key over the state's acting players.

    Follows the bank's convention: keys are joined in player order, collapsing
    to a single action name when only one player acts (cf. toy case 4.4).
    """
    parts = key.split("+")
    if len(parts) == len(turn):
        return parts
    if len(parts) == 1 and len(turn) == 1:
        return parts
    raise ConvertError(
        f"state '{sid}': joint-action key '{key}' has {len(parts)} part(s) "
        f"but players {turn} act there"
    )


def v1_to_v2(m: dict) -> dict:
    """Declarative game-case schema -> v2 team schema."""
    player_ids = [p["id"] for p in m.get("players", [])]
    states_out = []
    for sid, sd in (m.get("states") or {}).items():
        entry = {
            "id": sid,
            "desc": sd.get("description", sd.get("desc", "")),
            "terminal": bool(sd.get("terminal", False)),
        }
        state_actions = (m.get("actions") or {}).get(sid, {}) or {}
        turn = [p for p in player_ids if p in state_actions]
        tp_rows = (m.get("transition_probabilities") or {}).get(sid, {}) or {}
        actions_out = []
        for key, outcomes in tp_rows.items():
            parts = _joint_parts(str(key), turn, sid)
            actions_out.append({
                "by": dict(zip(turn, parts)),
                "next": [{"state": s, "p": float(p)} for s, p in outcomes.items()],
            })
        entry["turn"] = turn
        entry["actions"] = actions_out
        states_out.append(entry)
    initial_state = m.get("initial_state")
    if not isinstance(initial_state, str):
        raise ConvertError("declarative schema requires a string 'initial_state'")
    return {
        "players": [dict(p) for p in m.get("players", [])],
        "initial": [{"state": initial_state, "p": 1.0}],
        "states": states_out,
        "_notes": ["converted from declarative game-case schema"],
    }


def rollout_to_v2(m: dict) -> dict:
    """Rollout format (experiments/<model>/.../world_model.json) -> v2 schema."""
    smap = {}
    for s in m.get("states", []):
        if "id" not in s:
            raise ConvertError("rollout state without an 'id'")
        smap[s["id"]] = s
    profiles = defaultdict(dict)      # sid -> {profile_tuple: {next: p}}
    turn_players = defaultdict(list)  # sid -> players in first-appearance order
    for row in m.get("transitions", []) or []:
        sid = row.get("state")
        joint = row.get("joint_action", {}) or {}
        for p in joint:
            if p not in turn_players[sid]:
                turn_players[sid].append(p)
        prof = tuple(sorted(joint.items()))
        bucket = profiles[sid].setdefault(prof, {})
        for out in row.get("outcomes", []) or []:
            nxt = out["next_state"]
            bucket[nxt] = bucket.get(nxt, 0.0) + float(out.get("probability", 0.0))
    states_out = []
    for sid, s in smap.items():
        terminal = bool(s.get("terminal", False))
        entry = {"id": sid,
                 "desc": str(s.get("representation", "")),
                 "terminal": terminal}
        if not terminal:
            entry["turn"] = turn_players.get(sid, [])
            entry["actions"] = [
                {"by": dict(prof), "next": [{"state": n, "p": p} for n, p in dist.items()]}
                for prof, dist in sorted(profiles.get(sid, {}).items())
            ]
        states_out.append(entry)
    initial = [
        {"state": e["state"], "p": float(e.get("probability", e.get("p", 0.0)))}
        for e in m.get("initial_distribution", [])
    ]
    return {
        "players": [{"id": p} for p in m.get("players", [])],
        "initial": initial,
        "states": states_out,
        "_notes": ["converted from rollout format"],
    }


def to_v2(model: dict) -> tuple:
    """Normalize any accepted schema to (v2_model, schema_name)."""
    schema = detect_schema(model)
    if schema == "v2":
        out = model
    elif schema == "v1":
        out = v1_to_v2(model)
    else:
        out = rollout_to_v2(model)
    notes = list(out.pop("_notes", []))
    if model is not out and model.get("rewards") is not None:
        notes.append("source carried 'rewards'; Lane 1 ignores rewards")
    out["_notes"] = notes
    return out, schema


def v2_to_declarative(v2: dict) -> tuple:
    """v2 schema -> declarative game-case dict for ``WorldModelEDA.from_dict``.

    A prior over several initial states is collapsed to its first entry for the
    descriptive EDA; the assumption is returned alongside.
    """
    players = [p["id"] for p in v2.get("players", [])]
    prior = v2.get("initial", [])
    notes = []
    if not prior:
        raise ConvertError("v2 model has an empty 'initial' prior")
    initial_state = prior[0]["state"]
    if len(prior) > 1:
        notes.append(
            f"prior over {len(prior)} initial states collapsed to '{initial_state}' "
            "for the descriptive EDA"
        )
    states_d, actions_d, tp_d = {}, {}, {}
    for s in v2.get("states", []):
        sid = s["id"]
        sd = {"description": s.get("desc", "")}
        if s.get("terminal"):
            sd["terminal"] = True
        states_d[sid] = sd
        if s.get("terminal"):
            continue
        turn = [p for p in players if p in (s.get("turn") or [])]
        per_player = {p: [] for p in turn}   # insertion order == key join order
        rows = []
        for a in s.get("actions", []) or []:
            by = a.get("by", {}) or {}
            for p in turn:
                act = by.get(p)
                if act is not None and act not in per_player[p]:
                    per_player[p].append(act)
            rows.append(("+".join(by[p] for p in turn if p in by),
                         a.get("next", []) or []))
        actions_d[sid] = per_player
        tp_d[sid] = {key: {n["state"]: float(n["p"]) for n in nxt} for key, nxt in rows}
    return ({
        "players": [{"id": p} for p in players],
        "initial_state": initial_state,
        "states": states_d,
        "actions": actions_d,
        "transition_probabilities": tp_d,
    }, notes)


RESERVED_KEYS = {
    "_notes", "rewards", "initial_distribution", "transitions", "truncated",
    "errors", "warnings", "depth", "observations",
}


def flatten_text(model: Any) -> str:
    """Every string in the candidate (keys + values), for Lane-3 matching."""
    parts: list = []

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k not in RESERVED_KEYS:
                    parts.append(str(k))
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, str):
            parts.append(node)

    walk(model)
    return re.sub(r"[_\-]+", " ", " ".join(parts).lower())


# --------------------------------------------------------------------------- #
# Lane 3 — expect/avoid checklist evaluation                                   #
# --------------------------------------------------------------------------- #

ALL_LEXICON = {**LEXICON, **DOMAIN_LEXICON}


def _lexicon_family(token: str):
    """Lexicon family for a token, with a prefix fallback so e.g. 'correction'
    finds the 'correct' family."""
    st = stem(token)
    if st in ALL_LEXICON:
        return ALL_LEXICON[st]
    if token in ALL_LEXICON:
        return ALL_LEXICON[token]
    for key, fam in ALL_LEXICON.items():
        if len(key) >= 5 and (st.startswith(key) or key.startswith(st)):
            return fam
    return None


def families_for(bullet_clean: str, cid: str):
    """Word families a bullet needs evidence for.

    Each non-stopword token becomes a family; lexicon entries broaden a family
    with synonyms. Per-case extras append members to every family of the bullet.
    """
    fams, seen = [], set()
    for tok in tokenize(bullet_clean):
        st = stem(tok)
        if st in STOPWORDS or tok in STOPWORDS:
            continue
        members = _lexicon_family(tok) or [st]
        key = tuple(sorted(set(members)))
        if key not in seen:
            seen.add(key)
            fams.append(list(key))
    for trigger, extra in PER_CASE_EXTRA.get(cid, []):
        if trigger in bullet_clean:
            for fam in fams:
                fam.extend(m for m in extra if m not in fam)
    return fams


def _family_hit(family: list, model_tokens: set) -> bool:
    for member in family:
        m = member.lower()
        for tok in model_tokens:
            if len(m) >= 4 and tok.startswith(m):
                return True
            if len(tok) >= 4 and m.startswith(tok):
                return True
            if m == tok:
                return True
    return False


def _match_bullet(bullet: Criterion, cid: str, model_tokens: set,
                  action_tokens: Optional[set] = None):
    """-> (status, evidence_terms). status in covered/partial/missing/trivial.

    Bullets starting with 'actions spanning' are matched against the candidate's
    action names only (a mention anywhere in prose is weaker evidence than a
    modelled action), and demand proportionally fewer distinct families.
    """
    fams = families_for(bullet.clean, cid)
    if not fams:
        return "trivial", []
    tokens = action_tokens if action_tokens is not None else model_tokens
    ratio = 0.35 if action_tokens is not None else 0.45
    need = min(len(fams), max(2, math.ceil(ratio * len(fams))))
    hits = [fam[0] for fam in fams if _family_hit(fam, tokens)]
    if len(hits) >= need:
        return "covered", hits
    if len(hits) == 1 or (len(hits) > 1 and len(hits) >= max(1, need - max(1, need // 2))):
        return "partial", hits
    return "missing", []


ACTION_BULLET_RE = re.compile(r"^actions spanning")


def action_surface(v2: dict) -> set:
    """Distinct action names declared across all states, as match tokens."""
    names = set()
    for s in v2.get("states", []):
        for a in s.get("actions", []) or []:
            for act in (a.get("by") or {}).values():
                names.add(str(act))
    return set(tokenize(re.sub(r"[_\-]+", " ", " ".join(names).lower())))


def has_robot_player(v2: dict) -> bool:
    for p in v2.get("players", []):
        blob = " ".join(str(p.get(k, "")) for k in ("id", "type", "desc")).lower()
        if p.get("type") == "robot" or "robot" in blob:
            return True
    return False


def robot_player_check(bullet: Criterion, ctx: dict):
    if re.search(r"robot as the .?ai.? player|robot as the (only )?decision", bullet.clean):
        ok = ctx["has_robot"]
        return ("covered" if ok else "missing",
                ["structural: robot-type player present"] if ok else [])
    return None


STRUCTURAL_RULES = [robot_player_check]


def eval_lane3(case: CulturalCase, v2: dict, flat_text: str):
    """Expect/avoid checklist for one candidate. Returns a result dict."""
    model_tokens = {stem(t) for t in tokenize(flat_text)} | set(tokenize(flat_text))
    ctx = {"has_robot": has_robot_player(v2)}
    n_terminal = sum(1 for s in v2.get("states", []) if s.get("terminal"))
    act_tokens = action_surface(v2)

    expected_rows = []
    covered = partial = 0
    for crit in case.expected:
        status, hits = None, []
        for rule in STRUCTURAL_RULES:
            ruled = rule(crit, ctx)
            if ruled:
                status, hits = ruled
                break
        if status is None:
            use_actions = bool(ACTION_BULLET_RE.match(crit.clean))
            status, hits = _match_bullet(
                crit, case.cid, model_tokens,
                action_tokens=act_tokens if use_actions else None)
        covered += status in ("covered", "trivial")
        partial += status == "partial"
        expected_rows.append({"bullet": crit.raw, "status": status, "evidence": hits})
    n_exp = len(case.expected)
    coverage = (covered + 0.5 * partial) / n_exp if n_exp else 1.0

    # ---- forbidden side ------------------------------------------------- #
    flags = []   # {label, snippet, bullets:[indices]}

    def add_flag(label, snippet, bullet_idx):
        for f in flags:
            if f["label"] == label and bullet_idx in f["bullets"]:
                return
        for f in flags:
            if f["label"] == label:
                f["bullets"].append(bullet_idx)
                return
        flags.append({"label": label, "snippet": snippet, "bullets": [bullet_idx]})

    narrative_idx = [
        i for i, c in enumerate(case.forbidden)
        if any(h in c.clean for h in ("narrative", "story", "resolv"))
    ]
    for pattern, label in GLOBAL_FORBIDDEN:
        m = pattern.search(flat_text)
        if m:
            targets = narrative_idx or list(range(len(case.forbidden)))
            for i in targets:
                add_flag(label, m.group(0), i)
    for pattern, label, hint in PER_CASE_FORBIDDEN.get(case.cid, []):
        m = pattern.search(flat_text)
        if m:
            targets = [i for i, c in enumerate(case.forbidden) if hint in c.clean]
            for i in (targets or narrative_idx or range(len(case.forbidden))):
                add_flag(label, m.group(0), i)
    if n_terminal <= 1:
        collapse = "single outcome state - uncertainty may be collapsed to one resolution"
        for i, c in enumerate(case.forbidden):
            if any(h in c.clean for h in UNCERTAINTY_HINTS):
                add_flag(collapse, "", i)

    n_forb = len(case.forbidden)
    flagged_bullets = {i for f in flags for i in f["bullets"]}
    avoidance = 1.0 - (len(flagged_bullets & set(range(n_forb))) / n_forb if n_forb else 0.0)
    lane3 = math.sqrt(coverage * avoidance)   # geometric mean of the two sides

    return {
        "expected_rows": expected_rows,
        "flags": flags,
        "n_expected": n_exp,
        "n_covered": covered,
        "n_partial": partial,
        "n_forbidden": n_forb,
        "n_flagged_bullets": len(flagged_bullets),
        "coverage": round(coverage, 4),
        "avoidance": round(avoidance, 4),
        "lane3": round(lane3, 4),
        "n_terminal": n_terminal,
    }


# --------------------------------------------------------------------------- #
# Candidate pipeline                                                           #
# --------------------------------------------------------------------------- #


def evaluate_candidate(case: CulturalCase, raw: str, meta: dict, lenient: bool = False):
    """Run Lane 0 -> Lane 1 -> structural EDA -> Lane 3 on one candidate."""
    rec = {
        "case": case.cid,
        "country": case.country,
        "title": case.title,
        **meta,
        "lane0": PASS,
        "lane0_findings": [],
        "schema": None,
        "lane1": None,
        "eda": None,
        "eda_notes": [],
        "declarative": None,
        "lane3": None,
    }

    model, findings = parse_reply(raw, lenient=lenient)
    if findings:
        rec["lane0"] = FAIL
        rec["lane0_findings"] = [f"{sev}: {msg}" for sev, msg in findings]
        return rec

    try:
        v2, schema = to_v2(model)
    except ConvertError as exc:
        rec["lane0"] = FAIL
        rec["lane0_findings"] = [f"FAIL: {exc}"]
        return rec
    rec["schema"] = schema

    lane1r = run_lane1(v2, name=f"{case.cid}/{meta.get('sample', '')}")
    rec["lane1"] = {
        "verdict": lane1r["verdict"],
        "n_fail": lane1r["n_fail"],
        "n_warn": lane1r["n_warn"],
        "findings": [str(f) for f in lane1r["findings"]],
        "notes": v2.pop("_notes", []),
    }

    flat = flatten_text(model)
    rec["lane3"] = eval_lane3(case, v2, flat)

    if lane1r["verdict"] == PASS:
        try:
            decl, notes = v2_to_declarative(v2)
            analysis = WorldModelEDA.from_dict(decl)
            rec["declarative"] = decl
            rec["eda_notes"] = notes
            rec["eda"] = analysis.summary()
        except Exception as exc:                      # descriptive EDA must not kill the run
            rec["eda_notes"] = [f"structural EDA skipped: {exc}"]
    return rec


def discover_candidates(candidates_dir: Path):
    """-> list of (case_num | None, model_name, sample_name, path)."""
    found = []
    for path in sorted(candidates_dir.rglob("*.json")):
        rel = path.relative_to(candidates_dir)
        parts = rel.parts[:-1]
        model_name = parts[0] if parts else "default"
        stem = path.stem
        # NB: '\b' would not fire between a digit and '_', so use (?!\d).
        m = re.search(r"(?i)(?<![a-z0-9])c[_\-]?(\d{1,2})(?!\d)", stem)
        case_num = int(m.group(1)) if m else None
        sample = stem
        found.append((case_num, model_name, sample, path))
    return found


# --------------------------------------------------------------------------- #
# Built-in demo candidates (so the evaluator runs end-to-end out of the box)   #
# --------------------------------------------------------------------------- #


def _demo_good_c1() -> str:
    return json.dumps({
        "players": [
            {"id": "robot", "type": "robot", "desc": "Office robot drafting the meeting report"},
            {"id": "junior", "type": "human", "desc": "Junior employee who flagged the factual error"},
            {"id": "senior_manager", "type": "human", "desc": "Senior manager whose claim is questioned"},
        ],
        "initial": [{"state": "draft_flagged", "p": 1.0}],
        "states": [
            {"id": "draft_flagged", "terminal": False, "turn": ["robot"],
             "desc": "A correction to the senior manager's claim was requested; facts not yet verified.",
             "actions": [
                 {"by": {"robot": "verify_facts"},
                  "next": [{"state": "facts_checked", "p": 1.0}]},
                 {"by": {"robot": "publish_as_stated"},
                  "next": [{"state": "published_unverified", "p": 1.0}]}]},
            {"id": "facts_checked", "terminal": False, "turn": ["robot"],
             "desc": "Underlying facts verified separately from any hierarchy or face consideration.",
             "actions": [
                 {"by": {"robot": "correct_with_attribution"},
                  "next": [{"state": "corrected_attributed", "p": 0.5},
                           {"state": "manager_objected", "p": 0.5}]},
                 {"by": {"robot": "correct_without_attribution"},
                  "next": [{"state": "corrected_anonymous", "p": 1.0}]},
                 {"by": {"robot": "flag_to_manager_privately"},
                  "next": [{"state": "flagged", "p": 1.0}]},
                 {"by": {"robot": "publish_as_verified"},
                  "next": [{"state": "published_corrected", "p": 1.0}]}]},
            {"id": "published_unverified", "terminal": True,
             "desc": "Report published with the error; junior input dismissed without verification."},
            {"id": "corrected_attributed", "terminal": True,
             "desc": "Report corrected with attribution; seniority noted as social fact, not correctness."},
            {"id": "manager_objected", "terminal": True,
             "desc": "Manager pushed back on the attributed correction."},
            {"id": "corrected_anonymous", "terminal": True,
             "desc": "Report corrected without naming who erred, preserving face."},
            {"id": "flagged", "terminal": True,
             "desc": "Discrepancy flagged privately to the manager for a human decision."},
            {"id": "published_corrected", "terminal": True,
             "desc": "Report published with the verified correction in place."},
        ],
    })


def _demo_weak_c5() -> str:
    return json.dumps({
        "players": [
            {"id": "robot", "type": "robot", "desc": "Reception robot"},
            {"id": "client", "type": "human", "desc": "Visiting client"},
        ],
        "initial": [{"state": "gift_offered", "p": 1.0}],
        "states": [
            {"id": "gift_offered", "terminal": False, "turn": ["robot"],
             "desc": "Client presents a wrapped gift while watching.",
             "actions": [
                 {"by": {"robot": "open_immediately"},
                  "next": [{"state": "opened_now", "p": 1.0}]},
                 {"by": {"robot": "accept"},
                  "next": [{"state": "accepted", "p": 1.0}]}]},
            {"id": "opened_now", "terminal": True,
             "desc": "The robot correctly opened the gift in front of the client and thanked them."},
            {"id": "accepted", "terminal": True,
             "desc": "Gift accepted and handed to the team."},
        ],
    })


def _demo_v1_c9() -> str:
    return json.dumps({
        "players": [
            {"id": "robot", "description": "Hospitality robot arranging the dinner"},
            {"id": "host_company", "description": "Host company that requested mixed seating"},
            {"id": "venue_staff", "description": "Venue staff with their own seating policy"}
        ],
        "initial_state": "conflict_known",
        "states": {
            "conflict_known": {
                "description": "Host requests mixed-gender seating; venue policy prefers separated seating; both are live conventions.",
                "terminal": False
            },
            "mixed_used": {"description": "Seating followed the host request.", "terminal": True},
            "separated_used": {"description": "Seating followed the venue policy as a real local convention.", "terminal": True},
            "surfaced": {"description": "Conflict surfaced to human decision-makers of either party; attendees' comfort still unknown.", "terminal": True},
            "clarified": {"description": "Both parties asked to clarify and resolve the authority ambiguity directly.", "terminal": True}
        },
        "actions": {
            "conflict_known": {
                "robot": ["follow_host_request", "follow_venue_policy",
                          "surface_conflict_to_humans", "ask_both_parties"]
            }
        },
        "transition_probabilities": {
            "conflict_known": {
                "follow_host_request": {"mixed_used": 1.0},
                "follow_venue_policy": {"separated_used": 1.0},
                "surface_conflict_to_humans": {"surfaced": 1.0},
                "ask_both_parties": {"clarified": 1.0}
            }
        }
    })


def _demo_broken_c11() -> str:
    return '```json\n{"players": ["robot"], "initial": [{"state": "s0", "p": 1.0}], "states": ['


DEMO_CANDIDATES = [
    ("C1", "demo", "good_v2", _demo_good_c1()),
    ("C5", "demo", "weak_v2", _demo_weak_c5()),
    ("C9", "demo", "declarative_v1", _demo_v1_c9()),
    ("C11", "demo", "fenced_broken", _demo_broken_c11()),
]


# --------------------------------------------------------------------------- #
# Console output & report rendering                                            #
# --------------------------------------------------------------------------- #


def print_case_bank(cases):
    print(f"{'Case':6} {'Country':14} {'Exp':>3} {'Avoid':>5}  Title")
    for c in cases:
        print(f"{c.cid:6} {c.country:14} {len(c.expected):>3} {len(c.forbidden):>5}  "
              f"{c.title[:64]}")
    n_exp = sum(len(c.expected) for c in cases)
    n_avd = sum(len(c.forbidden) for c in cases)
    print(f"\n{len(cases)} case(s), {n_exp} expected-ingredient bullets, "
          f"{n_avd} forbidden-content bullets")


STATUS_GLYPH = {"covered": "[ok] ", "trivial": "[ok] ", "partial": "[~]  ",
                "missing": "[  ]"}


def print_record(rec: dict):
    head = f"{rec['case']:5} {rec.get('model', '')}/{rec.get('sample', '')}"
    if rec["lane0"] == FAIL:
        print(f"{head:44} LANE0 FAIL")
        for msg in rec["lane0_findings"]:
            print("      ", msg)
        return
    l1 = rec["lane1"]
    l3 = rec["lane3"]
    print(f"{head:44} lane1={l1['verdict']:4} ({l1['n_fail']}F/{l1['n_warn']}W)  "
          f"schema={rec['schema']:7} cov={l3['coverage']:.2f} "
          f"avoid={l3['avoidance']:.2f} lane3={l3['lane3']:.2f}")
    for f in l1["findings"]:
        print("      ", f)
    for note in l1.get("notes", []) + rec.get("eda_notes", []):
        print(f"       [note] {note}")


def _fmt(value, spec=".2f", dash="-"):
    return format(value, spec) if isinstance(value, (int, float)) else dash


def render_report(records: list, cases: list, graphs: bool = False) -> str:
    lines = []
    add = lines.append
    add("# Cultural Track Evaluation (04_cultural, C1-C14)")
    add("")
    add("## Experiment")
    add("")
    add("This is the cultural counterpart of the game-track EDA report. The case bank is")
    add("loaded from `data/Test_Cases/04_cultural`; every case is an open situation judged by")
    add("expect/avoid criteria, so there is no canonical reference model and a Lane-2")
    add("reference comparison is N/A by design. Candidates are instead run through:")
    add("")
    add("- **Lane 0** - strict JSON parse of the raw reply;")
    add("- **Lane 1** - the repository's mechanical checks (`json_generation/lane1.check_v2`)")
    add("  after normalizing v2 / declarative / rollout inputs to the v2 schema;")
    add("- **Cross-case structural EDA** - `WorldModelEDA` descriptors as for G1-G9;")
    add("- **Lane 3** - expect/avoid checklist scoring against each case's parsed criteria")
    add("  (coverage of expected ingredients with evidence, flags on forbidden content).")
    add("")
    add("## Case bank")
    add("")
    add("| Case | Country | Title | Expected | Forbidden |")
    add("| --- | --- | --- | ---: | ---: |")
    for c in cases:
        add(f"| {c.cid} | {c.country} | {c.title} | {len(c.expected)} | {len(c.forbidden)} |")
    add("")

    if records:
        add("## Lane results")
        add("")
        add("| Case | Model | Sample | Schema | Lane 0 | Lane 1 | Fails | Warns | Coverage | Avoidance | Lane 3 |")
        add("| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |")
        for r in records:
            l1 = r.get("lane1") or {}
            l3 = r.get("lane3") or {}
            add(
                f"| {r['case']} | {r.get('model', '')} | {r.get('sample', '')} "
                f"| {r.get('schema') or '-'} | {r['lane0']} "
                f"| {l1.get('verdict', '-')} | {l1.get('n_fail', '-')} "
                f"| {l1.get('n_warn', '-')} | {_fmt(l3.get('coverage'))} "
                f"| {_fmt(l3.get('avoidance'))} | {_fmt(l3.get('lane3'))} |"
            )
        add("")
        add("### Cross-case structural results")
        add("")
        add("| Case and title | States | Terminal | Joint actions | Avg. branch | Stochastic | Avg. entropy (bits) | Max depth | SCCs | Avg. path |")
        add("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
        for r in records:
            eda = r.get("eda")
            if not eda:
                label = f"{r['case']} - {r.get('model', '')}/{r.get('sample', '')}"
                add(f"| {label} | - | - | - | - | - | - | - | - | - |")
                continue
            st, ac, tr, gr = eda["states"], eda["actions"], eda["transitions"], eda["graph"]
            add(
                f"| {r['case']} - {r.get('model', '')}/{r.get('sample', '')} "
                f"| {st['state_count']} | {st['terminal_state_count']} "
                f"| {ac['joint_action_count']} | {_fmt(st['mean_branching_factor'])} "
                f"| {tr['stochastic_transition_fraction']:.0%} "
                f"| {_fmt(tr['mean_transition_entropy'], '.3f')} "
                f"| {st['maximum_trajectory_depth']} "
                f"| {gr['strongly_connected_component_count']} "
                f"| {_fmt(gr['average_shortest_path_length'])} |"
            )
        add("")

    add("## Per-case checklists")
    add("")
    for r in records:
        case = next((c for c in cases if c.cid == r["case"]), None)
        add(f"### {r['case']} - {r.get('model', '')}/{r.get('sample', '')}")
        add("")
        if r["lane0"] == FAIL:
            add("**Lane 0 failed.**")
            add("")
            for msg in r["lane0_findings"]:
                add(f"- `{msg}`")
            add("")
            continue
        l1, l3 = r["lane1"], r["lane3"]
        add(f"Lane 1 **{l1['verdict']}** ({l1['n_fail']} fail / {l1['n_warn']} warn), "
            f"coverage {l3['coverage']:.2f}, avoidance {l3['avoidance']:.2f}, "
            f"lane3 {l3['lane3']:.2f}.")
        for note in l1.get("notes", []) + rec_notes(r):
            add(f"- note: {note}")
        if l1["findings"]:
            add("")
            for f in l1["findings"]:
                add(f"- Lane 1: `{f}`")
        add("")
        add("Expected ingredients:")
        add("")
        for row in l3["expected_rows"]:
            glyph = STATUS_GLYPH.get(row["status"], "[?]")
            ev = f" <- {', '.join(row['evidence'])}" if row["evidence"] else ""
            add(f"- {glyph} {row['bullet']}{ev}")
        add("")
        add("Forbidden content flags (suspected - human review):")
        add("")
        if l3["flags"]:
            for flg in l3["flags"]:
                bullets = "; ".join(case.forbidden[i].raw[:90] for i in flg["bullets"]
                                    if case and i < len(case.forbidden))
                snip = f" (matched: `{flg['snippet']}`)" if flg["snippet"] else ""
                add(f"- FLAG: {flg['label']}{snip} -> {bullets}")
        else:
            add("- none flagged.")
        add("")
    return "\n".join(lines) + "\n"


def rec_notes(rec: dict):
    return rec.get("eda_notes", []) or []


# --------------------------------------------------------------------------- #
# Graph artifacts (optional, mirrors the game-track figures)                    #
# --------------------------------------------------------------------------- #


def save_graphs(records: list, graphs_dir: Path = GRAPHS_DIR):
    """Per-case state graphs + a cross-case comparison figure."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    graphs_dir.mkdir(parents=True, exist_ok=True)
    plotted = []
    for rec in records:
        decl = rec.get("declarative")
        if not decl:
            continue
        analysis = WorldModelEDA.from_dict(decl)
        fig, ax = plt.subplots(figsize=(9, 5.4), constrained_layout=True)
        try:
            analysis.plot_state_graph(ax=ax)
            ax.set_title(f"{rec['case']} - {rec.get('model','')}/{rec.get('sample','')}")
            out = graphs_dir / f"{rec['case'].lower()}_{_slug(rec.get('model',''))}_{_slug(rec.get('sample',''))}_state_graph.png"
            fig.savefig(out, dpi=180, bbox_inches="tight")
            plotted.append(rec)
        finally:
            plt.close(fig)

    usable = [r for r in records if r.get("eda")]
    if len(usable) >= 2:
        labels = [f"{r['case']}\n{r.get('sample','')}" for r in usable]
        fig, axes = plt.subplots(1, 3, figsize=(14, 4.2), constrained_layout=True)
        axes[0].bar(labels,
                    [r["eda"]["states"]["state_count"] for r in usable], color="#2563eb")
        axes[0].bar(labels,
                    [r["eda"]["actions"]["joint_action_count"] for r in usable],
                    bottom=[r["eda"]["states"]["state_count"] for r in usable],
                    color="#38bdf8")
        axes[0].set(title="Model size and decision surface", ylabel="Count")
        axes[0].legend(["States", "Joint actions"], frameon=False)
        axes[1].bar(labels,
                    [r["eda"]["transitions"]["mean_transition_entropy"] for r in usable],
                    color="#8b5cf6")
        axes[1].set(title="Mean transition entropy", ylabel="Bits")
        axes[2].bar(labels,
                    [(r["lane3"]["coverage"]) for r in usable], color="#16a34a")
        axes[2].bar(labels,
                    [(r["lane3"]["avoidance"]) for r in usable],
                    bottom=[r["lane3"]["coverage"] for r in usable], color="#f97316")
        axes[2].set(title="Lane 3 coverage / avoidance", ylim=(0, 1.05))
        axes[2].legend(["Coverage", "Avoidance"], frameon=False)
        for axis in axes:
            axis.spines[["top", "right"]].set_visible(False)
            axis.grid(axis="y", alpha=0.18)
            axis.set_axisbelow(True)
            axis.tick_params(axis="x", labelsize=7)
        fig.suptitle("Cultural candidate comparison", x=0.01, ha="left", fontweight="bold")
        fig.savefig(graphs_dir / "cultural_case_comparison.png", dpi=200, bbox_inches="tight")
        plt.close(fig)
    return graphs_dir


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "x"


# --------------------------------------------------------------------------- #
# Self-test (negative testing, in the spirit of the notebook's 17-mutation run) #
# --------------------------------------------------------------------------- #


def _v2_base() -> dict:
    return {
        "players": [{"id": "robot", "type": "robot", "desc": "A robot"}],
        "initial": [{"state": "s0", "p": 1.0}],
        "states": [
            {"id": "s0", "desc": "Deciding.", "terminal": False, "turn": ["robot"],
             "actions": [
                 {"by": {"robot": "act"}, "next": [{"state": "s1", "p": 1.0}]},
                 {"by": {"robot": "wait"}, "next": [{"state": "s0", "p": 1.0}]}]},
            {"id": "s1", "desc": "Done.", "terminal": True},
        ],
    }


def _mutate(name: str) -> dict:
    m = _v2_base()
    if name == "missing-initial":
        del m["initial"]
    elif name == "bad-prob-sum":
        m["states"][0]["actions"][0]["next"][0]["p"] = 0.8
        m["states"][0]["actions"][1]["next"][0]["p"] = 0.3
    elif name == "undeclared-next":
        m["states"][0]["actions"][0]["next"][0]["state"] = "sX"
    elif name == "unreachable-state":
        m["states"].append({"id": "s2", "desc": "Orphan.", "terminal": False,
                            "turn": ["robot"],
                            "actions": [{"by": {"robot": "loop"},
                                         "next": [{"state": "s2", "p": 1.0}]}]})
    elif name == "terminal-with-actions":
        m["states"][1].update({"turn": ["robot"],
                               "actions": [{"by": {"robot": "again"},
                                            "next": [{"state": "s1", "p": 1.0}]}]})
    elif name == "duplicate-profile":
        m["states"][0]["actions"].append(dict(m["states"][0]["actions"][0]))
    elif name == "no-terminal":
        for s in m["states"]:
            s["terminal"] = False
        m["states"][1]["turn"] = ["robot"]
        m["states"][1]["actions"] = [{"by": {"robot": "wait"},
                                      "next": [{"state": "s1", "p": 1.0}]}]
    else:
        raise AssertionError(name)
    return m


def self_test(cases) -> bool:
    ok = True

    def check(label, cond):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
        ok = ok and bool(cond)

    print("self-test:")

    # -- case bank -------------------------------------------------------- #
    check(f"case bank has 14 cases (got {len(cases)})",
          len(cases) == 14)
    check("every case has expected + forbidden bullets",
          all(c.expected and c.forbidden for c in cases))
    c1 = next(c for c in cases if c.cid == "C1")
    check("C1 parses country (Korea)", c1.country.lower() == "korea")

    # -- lane 0 ------------------------------------------------------------ #
    _, err_strict = parse_reply('```json\n{"a": 1}\n```')
    model_lenient, err_lenient = parse_reply('```json\n{"a": 1}\n```', lenient=True)
    check("strict parse rejects fenced reply", bool(err_strict))
    check("lenient parse unwraps fenced reply", model_lenient == {"a": 1})
    _, err_top = parse_reply('[1, 2, 3]')
    check("non-object top level rejected", bool(err_top))

    # -- converters --------------------------------------------------------- #
    v2, schema = to_v2(json.loads(_demo_v1_c9()))
    check("declarative C9 detected as v1", schema == "v1")
    lane1r = run_lane1(v2, "st")
    check("converted C9 passes Lane 1", lane1r["verdict"] == PASS)
    decl, _ = v2_to_declarative(v2)
    eda = WorldModelEDA.from_dict(decl).summary()
    check("C9 EDA sees 5 states / 4 terminals",
          eda["states"]["state_count"] == 5 and eda["states"]["terminal_state_count"] == 4)

    roll = {
        "players": ["robot"],
        "initial_distribution": [{"state": "a", "probability": 1.0}],
        "states": [
            {"id": "a", "terminal": False, "representation": "deciding", "actions": {}},
            {"id": "b", "terminal": True, "representation": "done", "actions": {}},
        ],
        "transitions": [
            {"state": "a", "joint_action": {"robot": "go"},
             "outcomes": [{"next_state": "b", "probability": 1.0}]},
        ],
    }
    v2r, sch_r = to_v2(roll)
    check("rollout format detected", sch_r == "rollout")
    check("rollout conversion passes Lane 1", run_lane1(v2r, "st")["verdict"] == PASS)

    # -- lane 1 mutations --------------------------------------------------- #
    caught = 0
    names = ["missing-initial", "bad-prob-sum", "undeclared-next",
             "unreachable-state", "terminal-with-actions",
             "duplicate-profile", "no-terminal"]
    for name in names:
        res = run_lane1(_mutate(name), name)
        caught += res["verdict"] == FAIL
    check(f"mutations caught ({caught}/{len(names)})", caught == len(names))

    # -- lane 3 -------------------------------------------------------------- #
    good = evaluate_candidate(c1, _demo_good_c1(), {"model": "demo", "sample": "t"})
    weak_case = next(c for c in cases if c.cid == "C5")
    weak = evaluate_candidate(weak_case, _demo_weak_c5(), {"model": "demo", "sample": "t"})
    check(f"good C1 coverage sane (>= 0.5, got {good['lane3']['coverage']})",
          good["lane3"]["coverage"] >= 0.5)
    check("weak C5 flags resolved narrative",
          any("narrative" in f["label"] for f in weak["lane3"]["flags"]))
    check(f"weak C5 misses expected ingredients (coverage {weak['lane3']['coverage']} < 0.9)",
          weak["lane3"]["coverage"] < 0.9)

    print(f"  self-test {'PASSED' if ok else 'FAILED'}")
    return ok


# --------------------------------------------------------------------------- #
# Main                                                                         #
# --------------------------------------------------------------------------- #


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Evaluate the cultural test-case track (04_cultural, C1-C14).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="examples:\n"
               "  python evaluate_cultural.py --list-cases\n"
               "  python evaluate_cultural.py --demo --graphs\n"
               "  python evaluate_cultural.py --candidates experiments/cultural/qwen\n")
    parser.add_argument("--candidates", type=Path, metavar="DIR",
                        help="evaluate every *.json candidate under DIR (recursive)")
    parser.add_argument("--case", metavar="C1,C2",
                        help="restrict to these case ids (comma separated)")
    parser.add_argument("--lenient", action="store_true",
                        help="unwrap a single fenced JSON block before parsing")
    parser.add_argument("--list-cases", action="store_true",
                        help="print the parsed case bank and exit")
    parser.add_argument("--demo", action="store_true",
                        help="run the built-in demo candidates end-to-end")
    parser.add_argument("--self-test", action="store_true",
                        help="run parser/converter/checker negative tests and exit")
    parser.add_argument("--report", type=Path, default=REPORT_PATH,
                        help=f"report path (default {REPORT_PATH.relative_to(ROOT)})")
    parser.add_argument("--no-report", action="store_true",
                        help="do not write the markdown report")
    parser.add_argument("--json-out", type=Path, metavar="PATH",
                        help="also dump machine-readable results to PATH")
    parser.add_argument("--graphs", action="store_true",
                        help="write state graphs + comparison figure under report/cultural_eda_graphs")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    cases = load_cases()
    wanted = None
    if args.case:
        wanted = {c.strip().upper() for c in args.case.split(",") if c.strip()}
        cases = [c for c in cases if c.cid in wanted]
        missing = wanted - {c.cid for c in cases}
        if missing:
            print(f"warning: no such case(s): {', '.join(sorted(missing))}", file=sys.stderr)

    if args.list_cases:
        print_case_bank(cases)
        return 0

    if args.self_test:
        return 0 if self_test(cases) else 2

    records = []
    unmapped = []

    if args.demo:
        by_id = {c.cid: c for c in cases}
        for cid, model_name, sample, raw in DEMO_CANDIDATES:
            case = by_id.get(cid)
            if not case:
                continue
            records.append(evaluate_candidate(
                case, raw, {"model": model_name, "sample": sample}, lenient=args.lenient))
    elif args.candidates:
        if not args.candidates.is_dir():
            print(f"no such candidates directory: {args.candidates}", file=sys.stderr)
            return 2
        by_num = {c.num: c for c in cases}
        for case_num, model_name, sample, path in discover_candidates(args.candidates):
            case = by_num.get(case_num) if case_num is not None else None
            if case is None:
                unmapped.append(str(path))
                continue
            try:
                raw = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                raw = path.read_text(encoding="utf-8", errors="replace")
            records.append(evaluate_candidate(
                case, raw,
                {"model": model_name, "sample": sample, "path": str(path)},
                lenient=args.lenient))
    else:
        print_case_bank(cases)
        print("\nnothing to evaluate - pass --candidates DIR or --demo "
              "(see --help).")

    for rec in records:
        print_record(rec)
    if unmapped:
        print(f"\n{len(unmapped)} file(s) could not be mapped to a C-case id:")
        for p in unmapped[:10]:
            print("   ", p)

    if records and not args.no_report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(render_report(records, cases), encoding="utf-8")
        print(f"\nreport written: {args.report}")
    if args.graphs and records:
        out = save_graphs(records)
        print(f"graphs written: {out}")

    if args.json_out and records:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        cases_dump = [
            {**{k: v for k, v in vars(c).items() if k != "path"},
             "path": str(c.path),
             "expected": [e.raw for e in c.expected],
             "forbidden": [f.raw for f in c.forbidden]}
            for c in cases
        ]
        args.json_out.write_text(
            json.dumps({"cases": cases_dump, "records": records}, indent=2),
            encoding="utf-8")
        print(f"results dumped: {args.json_out}")

    gate = [r for r in records
            if r["lane0"] == FAIL or (r.get("lane1") or {}).get("verdict") == FAIL]
    if records:
        n_l1 = sum(1 for r in records if r["lane0"] == PASS
                   and r["lane1"]["verdict"] == PASS)
        print(f"\n{len(records)} evaluated, {n_l1} pass Lane 0+1, {len(gate)} gated")
    return 1 if gate else 0


if __name__ == "__main__":
    raise SystemExit(main())
