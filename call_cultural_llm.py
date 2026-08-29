#!/usr/bin/env python3
"""Call Llama on the cultural track — data/Test_Cases/04_cultural (with location).

For each of the 14 cases C1-C14, sends ``prompts_library/zero_shot_v2_prompt.md``
as the system message and the case's ``### LLM Input`` situation as the user
message, then prints the raw reply to stdout. Display only: nothing is written
to disk, and no ``max_tokens`` cap is sent, so the reply is the world-model JSON
with transition probabilities exactly as the v2 prompt asks for it.

Provider: Groq (``groq`` package, ``llama-3.3-70b-versatile``) when GROQ_API_KEY
is set; otherwise OpenRouter (``openrouter`` package,
``meta-llama/llama-3.3-70b-instruct``) when OPENROUTER_API_KEY is set. A Groq
call that fails mid-run falls back to OpenRouter for that reply and stays there.

Usage:
    python call_cultural_llm.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from evaluate_cultural import CASES_DIR, load_cases  # noqa: E402  (validated case-bank parser)

PROMPT_PATH = ROOT / "prompts_library" / "zero_shot_v2_prompt.md"

GROQ_MODEL = "llama-3.3-70b-versatile"
OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct"


def _groq_caller():
    """(label, call) for Groq, or None without the package or GROQ_API_KEY."""
    if not os.getenv("GROQ_API_KEY"):
        return None
    try:
        from groq import Groq
    except ImportError:
        return None
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    def call(messages):
        completion = client.chat.completions.create(model=GROQ_MODEL, messages=messages)
        return completion.choices[0].message.content

    return f"groq:{GROQ_MODEL}", call


def _openrouter_caller():
    """(label, call) for OpenRouter, or None without the package or OPENROUTER_API_KEY."""
    if not os.getenv("OPENROUTER_API_KEY"):
        return None
    try:
        from openrouter import OpenRouter
    except ImportError:
        return None
    client = OpenRouter(api_key=os.environ["OPENROUTER_API_KEY"])

    def call(messages):
        response = client.chat.send(model=OPENROUTER_MODEL, messages=messages)
        return response.choices[0].message.content

    return f"openrouter:{OPENROUTER_MODEL}", call


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
        sys.stderr.reconfigure(errors="replace")

    system = PROMPT_PATH.read_text(encoding="utf-8")
    cases = load_cases()  # C1-C14 from 04_cultural, the with-location bank
    if not cases:
        raise SystemExit(f"no cultural cases found under {CASES_DIR}")

    groq = _groq_caller()
    openrouter = _openrouter_caller()
    if groq is None and openrouter is None:
        raise SystemExit(
            "no usable provider: set GROQ_API_KEY (pip install groq) or "
            "OPENROUTER_API_KEY (pip install openrouter)"
        )

    active = groq or openrouter
    print(f"provider: {active[0]} | cases: {len(cases)} | system: {PROMPT_PATH.name}\n")
    for case in cases:
        print(f"===== {case.cid} ({case.country}) — {case.title} =====")
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": case.llm_input},
        ]
        try:
            label, call = active
            reply = call(messages)
        except Exception as exc:
            if openrouter is None or openrouter is active:
                raise
            print(f"[warn] {active[0]} failed ({exc.__class__.__name__}: {exc}); "
                  f"falling back to {openrouter[0]}", file=sys.stderr)
            active = openrouter
            reply = active[1](messages)
        print(reply)
        print()


if __name__ == "__main__":
    main()
