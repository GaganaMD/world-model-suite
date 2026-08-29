"""Build the `cultural_without_loc` case bank.

Reads every `cultural_C_*.md` under `data/Test_Cases/04_cultural`, removes the
place / location references (country names, city names, and the country adjective
in norm descriptions such as *the Japanese norm* -> *the local norm*; the French
*laïcité* legal term is genericised to *secularism*). The culturally specific
concepts that are NOT place names (*quinceañera*, *musyawarah*, *adhan*) are kept,
because they name the norm, not the location. The sanitized copies are written
into `data/Test_Cases/cultural_without_loc/`.

The goal is a robustness study: the cultural-track cases hinge on *social norms*
that are country-associated. Removing the country/city label tests whether the
expected level of model output (the same set of explicitly modelled social stakes)
is preserved when the place name is omitted.

    python report\\make_cultural_without_loc.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "Test_Cases" / "04_cultural"
DST = ROOT / "data" / "Test_Cases" / "cultural_without_loc"
CASE_PATTERN = re.compile(r"cultural_C_(\d+)_.*\.md$")

# Whole-place tokens to scrub (case-insensitive), longest-first in application.
# Each entry becomes a regex `\b<token>\b` removal, so "West Java" is dropped
# before its word "Java" (which is not in the list anyway).
PLACES = [
    "South Korea", "North Korea", "United States", "Saudi Arabia",
    "Seoul", "Tokyo", "Shanghai", "Bengaluru", "São Paulo", "Sao Paulo",
    "Berlin", "Riyadh", "Guadalajara", "Cairo", "Yekaterinburg", "Chicago",
    "Oyo State", "West Java",
    "Korea", "China", "France", "India", "Japan", "Brazil", "Nigeria",
    "Germany", "Saudi", "Mexico", "Egypt", "Russia", "USA", "US", "Indonesia",
]

# Country-identifying phrases replaced with natural generics, applied before the
# blanket token scrub so the surrounding wording stays grammatical
# (case-insensitive, word-boundary matched).
PHRASE_REPLACE = [
    ("a Seoul office", "an office"),
    ("a Tokyo office", "an office"),
    ("French public middle school", "a public middle school"),
    ("the Brazilian norm", "the local norm"),
    ("the Japanese norm", "the local norm"),
    ("the German professional norm", "the local professional norm"),
    ("secularism (laïcité) policy", "secularism policy"),
    ("(laïcité) policy", "secularism policy"),
    ("that laïcité is", "that secularism is"),
    ("laïcité policy", "secularism policy"),
    ("laïcité", "secularism"),
]

# Country adjectives in norm descriptions -> neutral "local" (word-boundary).
COUNTRY_ADJECTIVES = [
    r"\bJapanese\b", r"\bKorean\b", r"\bChinese\b", r"\bIndian\b",
    r"\bBrazilian\b", r"\bNigerian\b", r"\bMexican\b", r"\bEgyptian\b",
    r"\bAmerican\b", r"\bIndonesian\b", r"\bGerman\b", r"\bFrench\b",
    r"\bRussian\b", r"\bSaudi\b",
]

# Prepositions that would be left dangling by removing a following place token.
DANGLING_PREPS = r"(?:in |at |from |of |near |around )?"
DANGLING_OPTIONS = "|".join(
    r"\b" + re.escape(place) + r"\b" for place in sorted(PLACES, key=len, reverse=True)
)


def _phrase_replace(text: str) -> str:
    for old, new in PHRASE_REPLACE:
        if old == new:
            continue
        text = re.sub(r"\b" + re.escape(old) + r"\b", new, text, flags=re.IGNORECASE)
    return text


def _normalize(text: str) -> str:
    """Collapse stray whitespace and repeated articles left by removals.

    Works line-by-line so the markdown heading structure is preserved (blank lines
    and single newlines are not collapsed into a single long line).
    """
    out = []
    for line in text.split("\n"):
        line = re.sub(r"[ \t]{2,}", " ", line)
        # Repeat-article / repeated-word artifacts from empty removals.
        line = re.sub(r"\b(the|an?|a|and) \1\b", r"\1", line, flags=re.IGNORECASE)
        line = re.sub(r"\b(an?|the) (an?|the)\b", r"\2", line, flags=re.IGNORECASE)
        line = re.sub(r"\s*\(\s*\)", "", line)          # empty parentheses
        line = re.sub(r"\s+([,.;:])", r"\1", line)
        line = re.sub(r",,", ",", line)
        out.append(line.rstrip())
    return "\n".join(out).strip()


def scrub(text: str) -> str:
    text = _phrase_replace(text)
    for pattern in COUNTRY_ADJECTIVES:
        text = re.sub(pattern, "local", text)
    # Remove every place token together with a preceding dangling preposition, so
    # "in Cairo" -> "" rather than "in ." and "in a village in West Java" keeps
    # only the first "in".
    text = re.sub(r"\b" + DANGLING_PREPS + "(" + DANGLING_OPTIONS + r")\b",
                  "",
                  text,
                  flags=re.IGNORECASE)
    return _normalize(text)


def scrub_heading(text: str) -> str:
    """Replace the country in the `Test Case C.N (...)` heading with a neutral token."""
    return re.sub(
        r"^(#{1,6}\s*Test Case\s+C\.\d+\s*\()([^)]*?)(\)\s*:.*)$",
        lambda m: f"{m.group(1)}Location-neutral{m.group(3)}",
        text,
        flags=re.MULTILINE,
    )


def main() -> int:
    DST.mkdir(parents=True, exist_ok=True)
    count = 0
    for path in sorted(SRC.glob("cultural_C_*.md"), key=lambda p: int(CASE_PATTERN.match(p.name).group(1))):
        num = CASE_PATTERN.match(path.name).group(1)
        raw = path.read_text(encoding="utf-8")
        # scrub_heading FIRST so the "(Location-neutral)" token survives the empty-paren
        # cleanup that scrub() applies to the rest of the document.
        out = scrub(scrub_heading(raw))
        target = DST / f"cultural_C_{num}_Test_Case_C{num}_without_loc.md"
        target.write_text(out, encoding="utf-8")
        count += 1
    print(f"wrote {count} location-scrubbed cultural cases to {DST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())