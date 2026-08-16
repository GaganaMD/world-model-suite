#!/usr/bin/env python3
"""Load the test-case bank from ``data/Test_Cases/**``.

Two kinds of case live in the bank:

* **Ground-truth cases** (``01_toy``, ``03_game``) ship an expected world model
  inside a ```json fenced block. These feed Lane 1 (validity) and Lane 2
  (equivalence).
* **Open cases** (``02_situational``, ``04_cultural``) ship no JSON — only an
  input situation and ``should include`` / ``should NOT include`` bullet lists.
  These feed Lane 3 (ingredient checklist).

Nothing here evaluates; it only parses. Paths are resolved relative to the repo
root so the module works from anywhere.
"""
from __future__ import annotations

import json
import pathlib
import re
from dataclasses import dataclass, field

ROOT = pathlib.Path(__file__).resolve().parent.parent
BANK = ROOT / "data" / "Test_Cases"

_JSON_BLOCK = re.compile(r"```json\s*(.*?)```", re.S)
_BULLET = re.compile(r"^\s*[-*•]\s+(.*\S)\s*$")
# Any line that starts a "should (not) include" list, in either house style:
#   "**A good model should include:**"   /   "A good model **should include**:"
_INCLUDE = re.compile(r"should\s+include", re.I)
_EXCLUDE = re.compile(r"should\s+(?:not|never)\s+include", re.I)


@dataclass
class GroundTruthCase:
    case_id: str          # e.g. "toy_1_1" or "game_G_7"
    group: str            # "01_toy" | "03_game"
    path: pathlib.Path
    model: dict           # the expected world model (canonical schema)


@dataclass
class OpenCase:
    case_id: str          # e.g. "situational_S_1" or "cultural_C_3"
    group: str            # "02_situational" | "04_cultural"
    path: pathlib.Path
    situation: str
    should_include: list[str] = field(default_factory=list)
    should_not: list[str] = field(default_factory=list)


def json_blocks(text: str) -> list[str]:
    """The raw string of every ```json fenced block, in order."""
    return [m.group(1) for m in _JSON_BLOCK.finditer(text)]


def _first_model(text: str) -> dict | None:
    for raw in json_blocks(text):
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def _case_id(path: pathlib.Path) -> str:
    """``toy_1_1`` from ``toy_1_1_Test_Case_11.md`` — the stable prefix."""
    stem = path.stem
    m = re.match(r"([a-z]+_[A-Za-z0-9]+_[A-Za-z0-9]+)", stem)
    return m.group(1) if m else stem


def _section(text: str, header_re: re.Pattern, stop_res: list[re.Pattern]) -> list[str]:
    """Bullet lines after the first line matching `header_re`, until a stop line."""
    lines = text.splitlines()
    out: list[str] = []
    collecting = False
    for line in lines:
        if not collecting:
            if header_re.search(line):
                collecting = True
            continue
        if any(s.search(line) for s in stop_res):
            break
        if line.strip().startswith("#"):   # next markdown heading ends the list
            break
        m = _BULLET.match(line)
        if m:
            out.append(_clean(m.group(1)))
    return out


def _clean(item: str) -> str:
    """Drop markdown emphasis so the bare claim is left for a judge."""
    item = re.sub(r"\*\*(.*?)\*\*", r"\1", item)
    item = re.sub(r"\*(.*?)\*", r"\1", item)
    item = re.sub(r"`(.*?)`", r"\1", item)
    return item.strip().rstrip(";.").strip()


def _situation(text: str) -> str:
    """The paragraph(s) under an '### LLM Input' heading."""
    lines = text.splitlines()
    grab, out = False, []
    for line in lines:
        if re.match(r"#+\s*LLM Input", line, re.I):
            grab = True
            continue
        if grab:
            if line.strip().startswith("#"):
                break
            out.append(line)
    return "\n".join(out).strip()


def parse_open_case(path: pathlib.Path) -> OpenCase:
    text = path.read_text(encoding="utf-8")
    include = _section(text, _INCLUDE, [_EXCLUDE])
    exclude = _section(text, _EXCLUDE, [])
    return OpenCase(
        case_id=_case_id(path),
        group=path.parent.name,
        path=path,
        situation=_situation(text),
        should_include=include,
        should_not=exclude,
    )


def ground_truth_cases(bank: pathlib.Path = BANK) -> list[GroundTruthCase]:
    cases = []
    for group in ("01_toy", "03_game"):
        for path in sorted((bank / group).glob("*.md")):
            model = _first_model(path.read_text(encoding="utf-8"))
            if model is not None:
                cases.append(GroundTruthCase(_case_id(path), group, path, model))
    return cases


def open_cases(bank: pathlib.Path = BANK) -> list[OpenCase]:
    cases = []
    for group in ("02_situational", "04_cultural"):
        for path in sorted((bank / group).glob("*.md")):
            cases.append(parse_open_case(path))
    return cases


if __name__ == "__main__":
    gt = ground_truth_cases()
    op = open_cases()
    print(f"ground-truth cases (have expected JSON): {len(gt)}")
    for c in gt:
        print(f"  {c.case_id:16} players={len(c.model.get('players', []))} "
              f"states={len(c.model.get('states', {}))}")
    print(f"\nopen cases (checklists): {len(op)}")
    for c in op:
        print(f"  {c.case_id:18} +{len(c.should_include):2} include  "
              f"-{len(c.should_not):2} avoid   sit={len(c.situation)}c")
