import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
import requests

OPENROUTER_API_KEY = "API_KEY
OPENROUTER_MODEL = "MODEL_NAME"
OUTPUT_FILE = "FILE_NAME"
PROMPT_PATH = Path("../prompts_library/zero_shot_v2_prompt.md")
OUTPUT_FILE = Path(OUTPUT_FILE)


@dataclass
class TestCase:
    cid: str
    country: str
    title: str
    llm_input: str


def load_cases():
    cases = []
    content_dir = Path("../data/Test_Cases/04_cultural/")
    files = sorted(
        content_dir.glob("cultural_C_*_Test_Case_C*.md"),
        key=lambda p: int(re.search(r"C(\d+)", p.name).group(1)),
    )

    for filepath in files:
        text = filepath.read_text(encoding="utf-8")
        match_id = re.search(r"C\d+", filepath.name)
        cid = match_id.group(0) if match_id else filepath.stem

        if "### LLM Input" in text:
            llm_input = text.split("### LLM Input", 1)[1].strip()
        else:
            llm_input = text.strip()

        title_match = re.search(r"^#\s*(.+)$", text, re.MULTILINE)
        title = title_match.group(1) if title_match else filepath.stem

        country_match = re.search(r"\(([^)]+)\)", title)
        country = country_match.group(1) if country_match else "Location"
        print(country) #For no country input harcode country variable value to "Location"
        
        cases.append(
            TestCase(
                cid=cid,
                country=country,
                title=title,
                llm_input=llm_input,
            )
        )

    return cases


def call_openrouter(messages):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {
                "model": OPENROUTER_MODEL,
                "messages": messages,
                "reasoning": {"enabled": True},
            }
        ),
    )
    res_json = response.json()
    return res_json["choices"][0]["message"]["content"]


def run_cultural_eval(cases):
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Prompt file not found: {PROMPT_PATH}")

    system = PROMPT_PATH.read_text(encoding="utf-8")
    start_time = time.time()
    output_lines = []

    header = f"provider: openrouter:{OPENROUTER_MODEL} | cases: {len(cases)} | system: {PROMPT_PATH.name}\n"
    print(header)
    output_lines.append(header)

    for case in cases:
        case_header = f"===== {case.cid} ({case.country}) — {case.title} ====="
        print(case_header)
        output_lines.append(case_header)

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": case.llm_input},
        ]

        reply = call_openrouter(messages)
        print(reply)
        print()

        output_lines.append(reply)
        output_lines.append("\n")

    total_time = time.time() - start_time
    time_str = f"Total Time to Response: {total_time:.2f} seconds"
    print(time_str)
    output_lines.append(time_str)

    # Save complete output to text file
    OUTPUT_FILE.write_text("\n".join(output_lines), encoding="utf-8")
    print(f"\nSaved output to {OUTPUT_FILE}")


if __name__ == "__main__":
    cases = load_cases()
    run_cultural_eval(cases)
