#!/usr/bin/env python3
"""Mutation proof for the FORM-or-VALUE declaration (D174) and the empty
selection (D175).

WHY THIS EXISTS AND WHY IT IS NOT A COMMENT. A test that never fails proves
nothing about the code it names, and the whole subject of this work is
instruments reporting agreement they did not measure. So every assertion is
proved by REINTRODUCING the defect it was written for and watching the AIMED
test go red -- control and mutant in ONE invocation, so the pair cannot be
separated by a stale interpreter, a changed working tree or a different day.

`__pycache__` IS PURGED BEFORE EVERY CELL, and `PYTHONDONTWRITEBYTECODE=1` is
NOT relied on. Measured in this lab: stale bytecode has INVERTED mutation
results here -- clean control failing, mutated case passing -- and the
environment variable did not fix it. Only removing the directories does.

THE MUTANT NEVER TOUCHES THE WORKING TREE. Five agents share this checkout, so
each cell builds a MIRROR: a temporary root whose every entry is a symlink back
to the repository except the one file being mutated, which is a real copy
carrying the mutation.

Run:  python3 scripts/mutation_harness_form_or_value.py
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
TEST_FILE = "test_form_or_value_and_empty_selection.py"
SUITE = "sdk.tests.test_form_or_value_and_empty_selection"

PY_SHARERS = "TheEmptySelectionIsNotAgreementTests.test_the_py_corpus_sharers"
STUDY_SHARERS = ("TheEmptySelectionIsNotAgreementTests"
                 ".test_the_stored_study_sharers")


def restore_pass(title: str, helper: str, summary: str, extra: str = "") -> tuple:
    """(old, new) that puts the empty-selection PASS back.

    The anchor is the `_no_selection`/`_no_study_in_scope` call plus its title,
    which is unique per check; the mutant returns the exact sentence the check
    printed BEFORE this repair, so the mutation reintroduces the defect rather
    than merely breaking the branch.
    """
    old = f'        return {helper}(\n            "{title}",{extra}'
    new = (f'        return Result("{title}", PASS,\n'
           f'                      "{summary}")\n'
           f'        return {helper}(\n            "{title}",{extra}')
    return old, new


# (name, what defect it reintroduces, old, new, aimed tests)
MUTATIONS: list[tuple] = []

# ---- D175, the eighteen empty-selection PASSes ---------------------------
for _title, _summary, _aimed in [
    ("non-conclusive band readers",
     "all 0 band_abs readers also read the flag", PY_SHARERS),
    ("channel totals vs the one rule",
     "all 0 channel-reporting act(s) combine through the one rule", PY_SHARERS),
    ("declared fleet vs work",
     "no worker declaration on any of 0 restored-path branches", PY_SHARERS),
    ("restated thresholds",
     "0 threshold default(s) read the governed constant", PY_SHARERS),
    ("record writers name their drops",
     "no writer whitelists keys off a parameter", PY_SHARERS),
    ("cited evidence paths",
     "all 0 repo-rooted citations resolve",
     "TheEmptySelectionIsNotAgreementTests.test_cited_evidence_paths"),
    ("campaign json citations",
     "all 0 machine-readable campaign citations resolve",
     "TheEmptySelectionIsNotAgreementTests.test_campaign_json_citations"),
    ("register group counts",
     "0 groups, 0 entries, every count agrees",
     "TheEmptySelectionIsNotAgreementTests.test_register_group_counts"),
    ("rung estimates state their iterations",
     "no rung-shaped compute proposal is on the docket",
     "TheEmptySelectionIsNotAgreementTests.test_rung_estimates"),
    ("gate table vs transcripts",
     "all 0 rows re-derive from their cited transcript",
     "TheEmptySelectionIsNotAgreementTests.test_gate_table"),
    ("completed but ungated runs",
     "no completed run is missing its gate verdict",
     "TheEmptySelectionIsNotAgreementTests.test_ungated_completed_runs"),
    ("closure entry of record",
     "the wall quotes the current entry of record",
     "TheEmptySelectionIsNotAgreementTests.test_the_closure_wall_empty_block"),
]:
    _old, _new = restore_pass(_title, "_no_selection", _summary)
    MUTATIONS.append((f"B1b {_title}",
                      f"restore the empty-selection PASS: {_summary!r}",
                      _old, _new, [_aimed]))

for _title, _summary in [
    ("studies carry what the fit records",
     "all 0 fitted study(s) carry every field their own fit records"),
    ("stored fits reproduce their values",
     "all 0 stored value(s) across 0 study(s) reproduce"),
    ("stored rungs carry solved precision",
     "all 0 extrapolating ladder(s) store rungs precise enough"),
    ("ladder rungs share one recipe",
     "all 0 fitted ladder(s) fit inside a family"),
    ("declined ladders name their guard",
     "all 0 declined ladder(s) name the guard that held them"),
    ("order-window declines state their dimensionality",
     "no stored ladder is declined on order_window"),
]:
    _old, _new = restore_pass(_title, "_no_study_in_scope", _summary,
                              extra=" studies,")
    MUTATIONS.append((f"B1b {_title}",
                      f"restore the empty-selection PASS: {_summary!r}",
                      _old, _new, [STUDY_SHARERS]))

# ---- the subject/evidence split, which is a FAIL and not an UNKNOWN ------
MUTATIONS.append((
    "B1b absent wall reads as clean",
    "drop the SUBJECT guard so a wall.json repointed at nothing chains "
    "through `or {}` to the PASS D174 measured",
    '    wall = _load_json(WALL)\n    if "__error__" in wall:\n'
    '        return Result("closure entry of record", FAIL,',
    '    wall = _load_json(WALL)\n    if False:\n'
    '        return Result("closure entry of record", FAIL,',
    ["TheTwoReasonsAreDifferentTests"
     ".test_an_absent_wall_is_a_FAIL_because_the_wall_is_the_SUBJECT"]))

# ---- D174, the declaration's own rules ----------------------------------
MUTATIONS += [
    ("D174 the probe is skipped",
     "THE DEFECT ITSELF: accept a VALUE declaration without executing "
     "anything -- a declaration nothing verifies",
     "            if before == after:",
     "            if False:",
     ["AForgedValueDeclarationFailsTests"
      ".test_a_check_that_never_reads_the_record_it_names_FAILS"]),
    ("D174 a value claim need not name a record",
     "let VALUE be declared with no source at all",
     "        if not sources:\n            problems.append(",
     "        if False:\n            problems.append(",
     ["AForgedValueDeclarationFailsTests"
      ".test_a_value_declaration_naming_no_record_FAILS"]),
    ("D174 the self-contradiction is allowed",
     "stop comparing a VALUE claim against its own blind_to -- the live "
     "instance D174 filed",
     '        if _VALUE_DISCLAIMER.search(blind or ""):',
     "        if False:",
     ["TheContradictionIsCaughtTests.test_declaring_value_beside_that_blind_to_FAILS"]),
    ("D174 EVIDENCE may grade form",
     "allow basis EVIDENCE -- a claim that a published NUMBER is re-derived "
     "here -- beside a form grade",
     "        if declared and declared[0] == EVIDENCE and kind in (FORM,",
     "        if False and declared[0] == EVIDENCE and kind in (FORM,",
     ["TheContradictionIsCaughtTests"
      ".test_declaring_basis_EVIDENCE_while_grading_form_FAILS"]),
    ("D174 the form column costs nothing",
     "let a FORM-OVER-VALUE entry decline to name what gets through it",
     "            if not isinstance(evidence, str) or len(evidence.strip()) < 40:",
     "            if False:",
     ["AForgedValueDeclarationFailsTests"
      ".test_a_form_over_value_declaration_naming_no_falsehood_FAILS"]),
    ("D174 an absent record reads as proven",
     "treat a record that is not on this box as if the probe had cleared it",
     "            if not path.exists():\n                unproven.append(",
     "            if False:\n                unproven.append(",
     ["AForgedValueDeclarationFailsTests"
      ".test_a_record_absent_from_this_box_is_UNKNOWN_not_PASS"]),
    ("D174 the blindfold leaves the bytecode",
     "blind only the .py and let SourceFileLoader read __pycache__ -- the "
     "stale-bytecode trap that has inverted mutation results in this lab",
     "        if self._cache_stem is None:\n            return False",
     "        return False\n        if self._cache_stem is None:\n"
     "            return False",
     ["TheBlindfoldIsHonestTests"
      ".test_it_blinds_an_import_and_its_compiled_copy"]),
    ("D174 the blindfold leaves the parent binding",
     "evict sys.modules and leave the submodule bound on its package, so "
     "`from pkg import leaf` never re-imports and the probe sees nothing move",
     "                if parent is not None and hasattr(parent, attribute):",
     "                if False:",
     ["TheBlindfoldIsHonestTests"
      ".test_it_detaches_the_submodule_from_its_parent_package"]),
    ("D174 the import machinery is not blinded",
     "leave `_io.open_code` alone, so every module-valued declaration reads "
     "as unconstrained by a record it cannot run without",
     "        _io.open_code = blind_open_code",
     "        pass",
     ["TheBlindfoldIsHonestTests"
      ".test_it_blinds_an_import_and_its_compiled_copy"]),
]


def purge_pycache(root: Path) -> None:
    for path in root.rglob("__pycache__"):
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path, ignore_errors=True)


def build_mirror(tmp: Path, mutated: str | None) -> Path:
    """A root that is the repository, except for one real, mutated file."""
    root = tmp / "mirror"
    root.mkdir()
    for entry in REPO.iterdir():
        if entry.name in {"scripts", "sdk"}:
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
        if entry.name == TEST_FILE:
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
    return proc.returncode == 0, (proc.stdout + proc.stderr)[-500:]


def main() -> int:
    source = (REPO / TARGET).read_text(encoding="utf-8")
    aimed = sorted({t for _, _, _, _, ts in MUTATIONS for t in ts})
    failures = []
    with tempfile.TemporaryDirectory() as raw:
        root = build_mirror(Path(raw), None)
        ok, tail = run(root, aimed)
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
                mirror = build_mirror(Path(mraw), source.replace(old, new))
                ok, tail = run(mirror, targets)
            print(f"{name}: {'RED (proved)' if not ok else 'GREEN (NOT PROVED)'}"
                  f"  -- {why}")
            print(f"    aimed: {', '.join(t.split('.')[-1] for t in targets)}")
            if ok:
                failures.append(f"{name}: the aimed test did not redden")

    print()
    if failures:
        print("MUTATION PROOF INCOMPLETE:")
        for item in failures:
            print(f"  - {item}")
        return 1
    print(f"MUTATION PROOF COMPLETE: control green, all {len(MUTATIONS)} "
          f"mutant(s) reddened their aimed test(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
