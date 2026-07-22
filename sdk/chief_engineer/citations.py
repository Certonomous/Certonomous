"""Human-readable names for the knowledge the chiefs cite.

Internally a citation is a file reference, because that is what an auditor
needs.  On screen a file path is noise at best and looks like a leaked
implementation detail at worst.  This module is the display layer: it turns
``docs/NUMERICS_KNOWLEDGE.md #3 (convergence ≠ physical validity)`` into
``Numerics knowledge №3 — convergence is not physical validity``.

Paths stay in the saved transcript and the event log; only the display form
reaches the interface.
"""

from __future__ import annotations

import re

# Numbered entries of the numerics knowledge base, titled for a reader.
KNOWLEDGE_TITLES: dict[str, str] = {
    "1": "validated cylinder benchmark against experiment",
    "2": "grid convergence measured on this machine",
    "3": "convergence is not physical validity",
    "4": "how a solver degrades past its regime",
    "5": "scheme dictionary completeness",
    "6": "runtime-compiled code cannot run as administrator",
    "7": "motorBike benchmark, meshed and solved here",
}

LESSON_TITLES: dict[str, str] = {
    "L-001": "reduce sampling uncertainty until only the irreducible remains",
}

# Sources that are whole documents rather than numbered entries.
DOCUMENT_TITLES: dict[str, str] = {
    "NUMERICS_KNOWLEDGE": "Numerics knowledge base",
    "LESSONS": "Operating lessons",
    "UNCERTAINTY": "Uncertainty method",
    "OPENFOAM": "Solver adapter record",
}

_KNOWLEDGE = re.compile(r"NUMERICS_KNOWLEDGE\.md\s*((?:#\d+\s*,?\s*)+)?(?:\((.*?)\))?", re.I)
_LESSON = re.compile(r"LESSONS\.md\s*(L-\d+)", re.I)
_NUMBERS = re.compile(r"#(\d+)")
_PATHISH = re.compile(r"[\w./\\-]+\.(?:md|py|html|json|yaml|txt|obj|stl)\b", re.I)


def display(raw: str) -> str:
    """Return the on-screen name for one citation."""
    text = str(raw or "").strip()
    if not text:
        return ""

    lesson = _LESSON.search(text)
    if lesson:
        key = lesson.group(1).upper()
        title = LESSON_TITLES.get(key)
        return f"Lesson {key} — {title}" if title else f"Lesson {key}"

    knowledge = _KNOWLEDGE.search(text)
    if knowledge:
        numbers = _NUMBERS.findall(knowledge.group(1) or "")
        parenthetical = (knowledge.group(2) or "").strip()
        if numbers:
            titles = [KNOWLEDGE_TITLES.get(number) for number in numbers]
            named = [t for t in titles if t]
            label = "№" + ", №".join(numbers)
            if named:
                return f"Numerics knowledge {label} — {named[0]}"
            if parenthetical:
                return f"Numerics knowledge {label} — {parenthetical}"
            return f"Numerics knowledge {label}"
        if parenthetical:
            return f"Numerics knowledge base — {parenthetical}"
        return DOCUMENT_TITLES["NUMERICS_KNOWLEDGE"]

    # Unknown source: strip anything path-shaped so no file reference escapes.
    cleaned = _PATHISH.sub("", text).strip(" -—:·,")
    return cleaned or "Internal record"


def display_all(raws) -> list[str]:
    seen: list[str] = []
    for raw in raws or ():
        name = display(raw)
        if name and name not in seen:
            seen.append(name)
    return seen


def contains_path(text: str) -> bool:
    """True when a string still carries a file reference — used by tests."""
    return bool(_PATHISH.search(str(text or "")))
