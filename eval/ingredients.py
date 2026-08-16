#!/usr/bin/env python3
"""Lane 3 — ingredient checklist for open cases (situational, cultural).

Open cases have no single ground-truth model, so "how true is it" becomes: does
the model contain the ingredients that must be there and none that must not?
Each case ships a ``should include`` and a ``should NOT include`` list; this lane
scores a candidate against them and reports two numbers the repo docs keep
deliberately separate:

* **coverage** — fraction of *should-include* items present  (1 − omission rate)
* **violation_rate** — fraction of *should-NOT* items present (the invention /
  hallucination / uncertainty-collapse rate)

An LLM-judge is *not* trusted on its own. Per ``benchmark_methodology_comparison``
§9, the judge is an **anchored rubric** and must be validated against human labels
with an agreement statistic (`cohen_kappa` below) before its scores are believed.

A judge is any callable ``(situation, model_output, item, polarity) -> bool``
answering "is this item present in the model?". Two are provided:

* ``LLMJudge`` — the real one: wraps a completion function you supply (so no
  network dependency lives here). Not exercised offline.
* ``KeywordJudge`` — a naive lexical-overlap stub, ONLY for wiring the pipeline
  and unit tests. It is not a semantic judge and must never be reported as one.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Callable, Protocol


class Judge(Protocol):
    def __call__(self, situation: str, model_output: str, item: str, polarity: str) -> bool: ...


# --------------------------------------------------------------------------- scoring

@dataclass
class IngredientScore:
    case_id: str
    coverage: float          # present / should_include
    violation_rate: float    # present / should_not
    ingredient_score: float  # coverage * (1 - violation_rate)
    present_include: list[str]
    missing_include: list[str]
    triggered_avoid: list[str]

    def as_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "coverage": round(self.coverage, 4),
            "violation_rate": round(self.violation_rate, 4),
            "ingredient_score": round(self.ingredient_score, 4),
            "missing_include": self.missing_include,
            "triggered_avoid": self.triggered_avoid,
        }


def score_case(case, model_output: str, judge: Judge, *, votes: int = 1) -> IngredientScore:
    """Score one open case. `votes` (>1) polls the judge and takes the majority."""
    def present(item: str, polarity: str) -> bool:
        calls = [judge(case.situation, model_output, item, polarity) for _ in range(votes)]
        return sum(calls) > len(calls) / 2

    inc_present = [it for it in case.should_include if present(it, "include")]
    inc_missing = [it for it in case.should_include if it not in inc_present]
    avoid_hit = [it for it in case.should_not if present(it, "avoid")]

    n_inc = len(case.should_include) or 1
    n_avoid = len(case.should_not)
    coverage = len(inc_present) / n_inc
    violation = (len(avoid_hit) / n_avoid) if n_avoid else 0.0
    return IngredientScore(
        case_id=case.case_id,
        coverage=coverage,
        violation_rate=violation,
        ingredient_score=coverage * (1 - violation),
        present_include=inc_present,
        missing_include=inc_missing,
        triggered_avoid=avoid_hit,
    )


# --------------------------------------------------------------------------- judges

class LLMJudge:
    """Anchored-rubric judge. `complete` maps a prompt to model text.

    Kept dependency-free: you pass any callable that returns a completion (an SDK
    call, a local model, a cached fixture). Validate it with `cohen_kappa` against
    human labels before trusting its scores.
    """

    PROMPT = (
        "You are grading a formal world model built from a described situation.\n"
        "SITUATION:\n{situation}\n\nWORLD MODEL:\n{model}\n\n"
        "Question: Does the world model {verb} the following?\n\"{item}\"\n"
        "Answer strictly 'yes' or 'no'."
    )

    def __init__(self, complete: Callable[[str], str]):
        self.complete = complete

    def __call__(self, situation: str, model_output: str, item: str, polarity: str) -> bool:
        verb = "adequately represent" if polarity == "include" else "contain / do"
        reply = self.complete(self.PROMPT.format(
            situation=situation.strip(), model=model_output.strip(), item=item, verb=verb))
        return reply.strip().lower().startswith("y")


_WORD = re.compile(r"[a-z][a-z_]+")
_STOP = set("the a an and or of to in on with for is are be that this its it as no not "
            "should model player robot its their them who can may not without any some".split())


class KeywordJudge:
    """NAIVE lexical-overlap stub — pipeline wiring and tests only, NOT a real judge.

    Declares an item "present" if enough of its content words appear in the model
    text. Blind to meaning, negation, and paraphrase; never report it as a score.
    """

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold

    def __call__(self, situation: str, model_output: str, item: str, polarity: str) -> bool:
        want = {w for w in _WORD.findall(item.lower()) if w not in _STOP}
        have = set(_WORD.findall(model_output.lower()))
        if not want:
            return False
        return len(want & have) / len(want) >= self.threshold


# --------------------------------------------------------------------------- judge validation

def cohen_kappa(a: list[bool], b: list[bool]) -> float:
    """Cohen's κ for two binary labelings. 1 = perfect, 0 = chance, <0 = worse."""
    if len(a) != len(b) or not a:
        raise ValueError("label lists must be equal, non-empty length")
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum((ca[k] / n) * (cb[k] / n) for k in (True, False))
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def judge_agreement(human: list[bool], machine: list[bool]) -> dict:
    """Agreement of a judge against a human gold set — the go/no-go for a judge."""
    n = len(human)
    agree = sum(x == y for x, y in zip(human, machine))
    return {
        "n": n,
        "raw_agreement": round(agree / n, 4) if n else 0.0,
        "cohen_kappa": round(cohen_kappa(human, machine), 4) if n else 0.0,
    }


if __name__ == "__main__":
    from eval import casebank
    cases = casebank.open_cases()
    print(f"open cases: {len(cases)}  "
          f"(avg +{sum(len(c.should_include) for c in cases)/len(cases):.1f} include, "
          f"-{sum(len(c.should_not) for c in cases)/len(cases):.1f} avoid)")

    # Demo the pipeline on one case with the naive stub judge (illustrative only).
    c = next(c for c in cases if c.case_id == "situational_S_1")
    fake_output = ("players: robot copilot, human pilot, passengers, ground authorities. "
                   "the warning is unconfirmed; both possibilities modeled. actions: verify, "
                   "continue monitoring, alert ground, intervene.")
    s = score_case(c, fake_output, KeywordJudge())
    print("demo score (KeywordJudge stub, NOT a real judge):", s.as_dict())

    # Validate the kappa util on known inputs.
    print("kappa perfect :", cohen_kappa([1, 0, 1, 1], [1, 0, 1, 1]))
    print("kappa inverted:", cohen_kappa([1, 1, 0, 0], [0, 0, 1, 1]))
    print("agreement demo:", judge_agreement([1, 1, 0, 1, 0], [1, 0, 0, 1, 0]))
