#!/usr/bin/env python3
"""Mutation proof for `check_rank_claim_values` and its controls.

WHY THIS EXISTS AND WHY IT IS NOT A COMMENT. A test that never fails proves
nothing about the code it names. Every assertion this lab relies on is proved
by reintroducing the defect it was written for and watching the AIMED test go
red -- control and mutant in ONE invocation, so the pair cannot be separated by
a stale interpreter, a changed working tree or a different day.

`__pycache__` IS PURGED BEFORE EVERY CELL, and `PYTHONDONTWRITEBYTECODE=1` is
NOT relied on. Measured in this lab: stale bytecode has INVERTED mutation
results here -- the clean control failing and the mutated case passing -- and
the environment variable did not fix it. Only removing the directories does.

THE MUTANT NEVER TOUCHES THE WORKING TREE. Six agents share this checkout, and
a harness that edits `scripts/self_audit.py` in place and reverts is one
interrupt away from leaving a mutant committed by somebody else. Each cell
builds a MIRROR: a temporary root whose every entry is a symlink back to the
repository except the one file being mutated, which is a real copy carrying the
mutation. `Path(__file__).resolve()` inside both the audit and its test then
lands in the mirror, and `git ls-files` still works because `.git` is linked.

Run:  python3 scripts/mutation_harness_rank_values.py
Exit: 0 when every mutant reddens its aimed test AND the control is green.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TARGET = "scripts/self_audit.py"
SUITE = "sdk.tests.test_rank_claim_values"

# (name, what defect it reintroduces, old, new, aimed tests)
MUTATIONS = [
    ("M1 form-only grading",
     "the defect itself: grade FORM, return no value fault ever",
     "    live, history = _live_claim_text(text, cdf)",
     "    live, history = _live_claim_text(text, cdf)\n"
     "    return [], list(history)",
     ["ThePositiveControlIsTheShippedArtifactTests",
      "TheFormGuardDoesNotGradeValueTests"
      ".test_the_form_guard_clears_a_well_formed_falsehood",
      "TheDeferralHasAReceivingEndTests.test_the_deferred_class_is_now_graded"]),
    ("M2 denominator typed, not derived",
     "hold the board size as a constant instead of reading the board",
     '    board_n = facts["entries"] + 1',
     "    board_n = 7",
     ["TheValuesAreDerivedNotTypedTests"
      ".test_the_denominator_follows_the_board_it_is_given"]),
    ("M3 no dated-context discriminator",
     "grade dated history as if it were a live claim",
     '    heads = [i for i, line in enumerate(lines) if cdf._HEADING.match(line)]',
     "    return []\n"
     "    heads = [i for i, line in enumerate(lines) "
     "if cdf._HEADING.match(line)]",
     ["TheMustNotMatchHalfTests.test_correctly_dated_history_does_not_fail"]),
    ("M4 banner swallowed by its own span",
     "mask from the heading, so a banner's own live claim is exempted",
     "        start = starts[body]",
     "        start = starts[head]",
     ["TheMustNotMatchHalfTests"
      ".test_the_banner_itself_is_live_text_and_is_graded"]),
    ("M5 the empty set passes",
     "defect class B1: return PASS from a sweep that examined nothing",
     "    if not surfaces or not claims:\n        return _no_evidence(",
     "    if not surfaces or not claims:\n"
     "        return Result(name, PASS, 'nothing to grade')\n"
     "        return _no_evidence(",
     ["TheEmptySetIsNotAgreementTests.test_no_claims_found_is_UNKNOWN_not_PASS"]),
    ("M6 the strike masker is dropped",
     "grade struck and quoted text as if it were a live claim",
     "    live, _ = cdf.mask_exempt(text)",
     "    live, _ = text, None",
     ["TheMustNotMatchHalfTests.test_a_struck_claim_is_not_a_live_one",
      "TheMustNotMatchHalfTests.test_a_quoted_defect_is_not_a_fresh_defect"]),
    ("M7 `comparable` graded without its ratio",
     "fault the word wherever it appears, whatever the bound actually is",
     "            if ratio_lo > 100:",
     "            if True:",
     ["TheValuesAreDerivedNotTypedTests"
      ".test_comparable_is_graded_against_the_ratio_it_is_given"]),
    ("M8 the frozen pin is not declined",
     "grade a third party's placement on the pin against the live board",
     "            if _VALUE_FROZEN_PIN.search(window):",
     "            if False:",
     ["TheMustNotMatchHalfTests"
      ".test_somebody_elses_placement_on_the_frozen_pin_is_declined"]),
]


def purge_pycache(root: Path) -> None:
    for path in root.rglob("__pycache__"):
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path, ignore_errors=True)


def build_mirror(tmp: Path, mutated: str | None) -> Path:
    """A root that is the repository, except for one real, mutated file."""
    root = tmp / "mirror"
    root.mkdir()
    real_dirs = {"scripts", "sdk"}
    for entry in REPO.iterdir():
        if entry.name in real_dirs:
            continue
        (root / entry.name).symlink_to(entry)
    (root / "scripts").mkdir()
    for entry in (REPO / "scripts").iterdir():
        if entry.name == "self_audit.py" and mutated is not None:
            (root / "scripts" / entry.name).write_text(mutated,
                                                       encoding="utf-8")
        else:
            (root / "scripts" / entry.name).symlink_to(entry)
    (root / "sdk").mkdir()
    for entry in (REPO / "sdk").iterdir():
        if entry.name == "tests":
            continue
        (root / "sdk" / entry.name).symlink_to(entry)
    (root / "sdk" / "tests").mkdir()
    for entry in (REPO / "sdk" / "tests").iterdir():
        if entry.name == "test_rank_claim_values.py":
            shutil.copy2(entry, root / "sdk" / "tests" / entry.name)
        else:
            (root / "sdk" / "tests" / entry.name).symlink_to(entry)
    return root


def run(root: Path, targets: list[str]) -> tuple[bool, str]:
    purge_pycache(root)
    purge_pycache(REPO)
    proc = subprocess.run(
        [sys.executable, "-m", "unittest",
         *[f"{SUITE}.{t}" for t in targets]],
        cwd=root, capture_output=True, text=True, timeout=1800)
    return proc.returncode == 0, (proc.stdout + proc.stderr)[-400:]


def main() -> int:
    source = (REPO / TARGET).read_text(encoding="utf-8")
    aimed = sorted({t for _, _, _, _, ts in MUTATIONS for t in ts})
    failures = []
    with tempfile.TemporaryDirectory() as raw:
        control_dir = Path(raw) / "c"
        control_dir.mkdir()
        control_root = build_mirror(control_dir, None)
        ok, tail = run(control_root, aimed)
        print(f"CONTROL (no mutation), {len(aimed)} aimed test(s): "
              f"{'GREEN' if ok else 'RED'}")
        if not ok:
            print(tail)
            failures.append("control is not green")

        for name, why, old, new, targets in MUTATIONS:
            if source.count(old) != 1:
                print(f"{name}: SKIPPED -- anchor occurs "
                      f"{source.count(old)} time(s), not once")
                failures.append(f"{name}: anchor not unique")
                continue
            with tempfile.TemporaryDirectory() as mraw:
                root = build_mirror(Path(mraw), source.replace(old, new))
                ok, tail = run(root, targets)
            verdict = "RED (proved)" if not ok else "GREEN (NOT PROVED)"
            print(f"{name}: {verdict}  -- {why}")
            print(f"    aimed: {', '.join(t.split('.')[-1] for t in targets)}")
            if ok:
                failures.append(f"{name}: the aimed test did not redden")

    print()
    if failures:
        print("MUTATION PROOF INCOMPLETE:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"MUTATION PROOF COMPLETE: control green, all {len(MUTATIONS)} "
          f"mutant(s) reddened their aimed test(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
