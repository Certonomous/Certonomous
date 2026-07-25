"""Language/register regression tests (GUI-2b register round).

Two house rules pinned here:

1. **No em dash in user-visible strings.** The transcript, reports, agenda
   scopes, and verdict reasons are read on camera; an em dash reads as an
   LLM-ism the product owner explicitly banned ("I have told you to drop the
   dashes ... I don't ever want to see them"). Rewritten with commas, colons,
   periods, or semicolons instead. Docstrings and code comments are not
   user-visible, so they are exempt from the scan (comments are invisible to
   the AST entirely; module/class/function docstrings are located and
   excluded explicitly below).

2. **No self-grading narration.** An agent must never lecture the viewer
   about its own fidelity chip, tier, or grade, or cite a validation standard
   as a defense of its own result (see G2 in docs/HANDOFF-GUI2.md). The chip
   is still computed and stored; it is simply never spoken.
"""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
EM_DASH = "—"

# The exact surface the owner named: every workflow, plus the five
# chief_engineer modules whose strings feed transcript bullets, report
# sections, verdict reasons, agenda scopes, and channel notes.
_WORKFLOWS_DIR = SDK / "workflows"
_CHIEF_ENGINEER_FILES = ("researcher.py", "lab.py", "server.py",
                         "head_engineer.py", "chief_researcher.py",
                         "display_names.py", "uq.py")


def _target_files() -> list[Path]:
    files = sorted(_WORKFLOWS_DIR.glob("*.py"))
    files += [SDK / "chief_engineer" / name for name in _CHIEF_ENGINEER_FILES]
    return files


def _docstring_node_ids(tree: ast.AST) -> set[int]:
    """id() of every string-constant node that IS a docstring (module,
    class, or function/async-function), so the scan can skip them."""
    ids: set[int] = set()
    candidates: list[ast.AST] = [tree] + [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]
    for node in candidates:
        body = getattr(node, "body", None)
        if (body and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            ids.add(id(body[0].value))
    return ids


def _non_docstring_string_literals(path: Path):
    """Yield (lineno, value) for every string-constant node that is not a
    docstring. Comments never reach this scan at all (the tokenizer drops
    them before the AST exists), and f-string literal segments are Constant
    nodes too, so they are covered."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    doc_ids = _docstring_node_ids(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in doc_ids:
                continue
            yield node.lineno, node.value


class NoEmDashInUserVisibleStrings(unittest.TestCase):
    """G-EMDASH: the owner's dash purge, regression-tested at the source."""

    def test_workflows_and_chief_engineer_core_carry_no_em_dash(self):
        offenders = []
        for path in _target_files():
            for lineno, value in _non_docstring_string_literals(path):
                if EM_DASH in value:
                    offenders.append(f"{path.relative_to(SDK)}:{lineno}: {value!r}")
        self.assertEqual(
            offenders, [],
            "Em dash found in a non-docstring string literal (user-visible "
            "narration/report text). Rewrite with a comma, colon, period, or "
            "semicolon instead:\n" + "\n".join(offenders))


class NoSelfGradingNarration(unittest.TestCase):
    """G-GRADE: agents state findings and next steps, never their own chip."""

    # Phrases that mean "I am now lecturing you about my own trust tier".
    # Matched as substrings so "grade" inside an unrelated word ("upgrade")
    # is not the target class of phrase, but the check below narrows on
    # word boundaries via simple containment of the exact banned phrase.
    _SELF_GRADE_PHRASES = (
        "grade: SOLVER-BACKED", "grade: RESEARCH MODEL", "grade: VALIDATED",
        "grade: UNCONVERGED", "the tier says", "the chip says",
        "per the ASME V&V 20 validation-uncertainty standard",
    )

    def test_no_self_grading_lecture_strings(self):
        offenders = []
        for path in _target_files():
            for lineno, value in _non_docstring_string_literals(path):
                for phrase in self._SELF_GRADE_PHRASES:
                    if phrase in value:
                        offenders.append(
                            f"{path.relative_to(SDK)}:{lineno}: {phrase!r} in {value!r}")
        self.assertEqual(
            offenders, [],
            "Self-grading narration found (agent lecturing about its own "
            "tier/chip/grade). State the finding and next step instead:\n"
            + "\n".join(offenders))


if __name__ == "__main__":
    unittest.main()
