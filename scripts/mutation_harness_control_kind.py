#!/usr/bin/env python3
"""Mutation proof for `scripts/control_kind.py` and its first adopter.

WHY IT IS TRACKED. A mutation result quoted in a commit message cannot be
re-run by the next reader. This one can.

WHAT IT PROVES AND WHAT IT DOES NOT. It shows each assertion CAN fail, never
that it asserts the right thing. The evidence that the convention catches the
defect that actually existed is not a mutation: the pin's fixture IS the
measured failure -- a literal sweep for *"the tie is lost"* over a corpus
containing *"the tie was lost"* -- and the tests assert the module tells the
firing reachability control apart from the failing recognition one.

NO SYMLINK MIRROR. `Path(__file__).resolve()` follows symlinks and cost an hour
tonight: a mirror made of symlinks resolved back to the real repository and
every mutant survived with zero new failures. Here BOTH files are copied into a
temporary directory as real files, the mutant is written over one of them, and
the suite is pointed at the copies by explicit `*_PATH` env vars. The adopter
does `sys.path.insert(0, Path(__file__).resolve().parent)` and therefore imports
the temp-directory `control_kind.py`, which is the mutated one -- verified by
mutant M1, which only reddens if the substitution really happened.

HOW IT IS JUDGED. The control runs FIRST and must be GREEN. A mutant is killed
only when a test IT NAMED is in the NEW-FAILURE set -- failure-count delta
against that green control, never `returncode != 0`.

`__pycache__` is purged before every cell. Both subjects' sha256 are asserted
unchanged in a `finally`; no tracked file is ever mutated in place.

Run:  python3 scripts/mutation_harness_control_kind.py
      python3 scripts/mutation_harness_control_kind.py --list
Exit: 0 when the control is green AND every mutant reddened a test it aimed at.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HELPER = REPO / "scripts" / "control_kind.py"
ADOPTER = REPO / "scripts" / "check_docket_reconciliation.py"
TEST_MODULE = "sdk.tests.test_control_kind"

# (name, defect, subject, old, new, tests it must redden)
MUTANTS: list[tuple[str, str, Path, str, str, tuple[str, ...]]] = [
    (
        "M1-first-arity-guard-removed",
        "the explicit one-form guard is deleted. NOTE it does NOT on its own "
        "promote a single form to RECOGNITION: the mutual-independence guard "
        "below catches a lone form too, so only the REASON printed changes. "
        "Recorded with that aim rather than a wider one, because a mutant "
        "scored against tests it cannot redden manufactures survivors.",
        HELPER,
        "        if len(self.planted) < 2:\n"
        "            return REACHABILITY, (\"only one form was planted",
        "        if False:\n"
        "            return REACHABILITY, (\"only one form was planted",
        ("test_naming_a_control_recognition_does_not_make_it_one",),
    ),
    (
        "M1b-both-arity-guards-removed",
        "THE CORE DEFECT, and it takes BOTH guards to reach it: a single "
        "planted literal is classified RECOGNITION, so a reachability probe is "
        "reported as proof that the pattern recognises the claim class. "
        "Removing either guard alone does NOT produce it -- the first version "
        "of this mutant deleted only the independence guard and merely "
        "duplicated M2, which is why it survived its own aim.",
        HELPER,
        "        if len(self.planted) < 2:\n"
        "            return REACHABILITY, (\"only one form was planted -- that proves the \"\n"
        "                                  \"sweep could OPEN the corpus, not that its \"\n"
        "                                  \"pattern recognises the claim class\")\n"
        "        distinct = self.distinct_forms\n"
        "        if len(distinct) < 2:",
        "        distinct = self.distinct_forms\n"
        "        if False:",
        (
            "test_a_reachability_control_fires_and_does_not_earn_the_zero",
            "test_naming_a_control_recognition_does_not_make_it_one",
            "test_a_reachability_only_control_turns_the_same_pass_into_unknown",
        ),
    ),
    (
        "M2-substrings-count-as-independent",
        "forms that are substrings of one another count as mutually "
        "independent, so planting `tie lost` and `the tie lost` reads as "
        "recognition though a literal search for either finds the other.",
        HELPER,
        "            if any(a != _norm(other) and a in _norm(other) for other in forms):\n"
        "                continue",
        "            if False:\n"
        "                continue",
        ("test_two_forms_that_are_substrings_are_not_independent",),
    ),
    (
        "M3-a-control-that-did-not-fire-is-fine",
        "a planted form that was NOT found stops making the control BROKEN, so "
        "an instrument known not to work still licenses its own zero. This is "
        "the is/was case exactly.",
        HELPER,
        "        if not self.all_fired:",
        "        if False:",
        (
            "test_a_recognition_control_on_the_same_sweep_is_BROKEN",
        ),
    ),
    (
        "M4-a-matched-negative-is-fine",
        "a negative form that WAS matched no longer breaks the control, so a "
        "pattern loose enough to match anything reports itself sound.",
        HELPER,
        "        if not self.negatives_held:",
        "        if False:",
        ("test_a_negative_form_that_matches_makes_the_control_BROKEN",),
    ),
    (
        "M5-reachability-earns-the-zero",
        "THE FAIL-OPEN. A zero under a reachability-only control is reported "
        "as a measurement of absence, which is the sentence this module was "
        "written to stop anybody writing.",
        HELPER,
        "        if kind == RECOGNITION:\n"
        "            return ZERO_IS_A_MEASUREMENT",
        "        if kind in (RECOGNITION, REACHABILITY):\n"
        "            return ZERO_IS_A_MEASUREMENT",
        (
            "test_a_reachability_control_fires_and_does_not_earn_the_zero",
            "test_the_two_kinds_produce_different_output",
            "test_a_reachability_only_control_turns_the_same_pass_into_unknown",
        ),
    ),
    (
        "M6-no-control-earns-the-zero",
        "a sweep that ran no control at all reports its zero as a measurement, "
        "which is indistinguishable from a sweep that read nothing.",
        HELPER,
        "        return ZERO_IS_UNSUPPORTED, (\n"
        "            f\"zero hits and NO control was run at all",
        "        return ZERO_IS_A_MEASUREMENT, (\n"
        "            f\"zero hits and NO control was run at all",
        ("test_no_control_at_all_is_not_a_measurement",),
    ),
    (
        "M7-adopter-stops-gating-its-pass",
        "the adopter grants PASS on an empty difference without consulting its "
        "control, so weakening its id pattern silently restores a false zero.",
        ADOPTER,
        "    elif zero_verdict != control_kind.ZERO_IS_A_MEASUREMENT:",
        "    elif False:",
        ("test_a_reachability_only_control_turns_the_same_pass_into_unknown",),
    ),
    (
        "M8-adopter-plants-one-form-only",
        "the adopter's own control degrades to a SINGLE bare id, so it proves "
        "it can read the docket and nothing about recognising a decorated row. "
        "Dropping only ONE of its five forms is deliberately NOT the mutation: "
        "four mutually independent forms are still a genuine recognition "
        "control, so that version was a no-op dressed as a defect and it "
        "survived, correctly.",
        ADOPTER,
        '    forms = {\n        "| D9001 | a bare row |": "D9001",',
        '    forms = {  # MUTANT: one form only\n        "| D9001 | a bare row |": "D9001",\n    }\n    _unused = {',
        (
            "test_the_adopters_own_planted_forms_are_mutually_independent",
        ),
    ),
]


def purge_pycache(root: Path) -> None:
    for cache in root.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)


def run_tests(helper: Path | None, adopter: Path | None) -> tuple[int, set[str]]:
    purge_pycache(REPO)
    env = {**os.environ}
    env.pop("CONTROL_KIND_PATH", None)
    env.pop("CHECK_DOCKET_RECONCILIATION_PATH", None)
    if helper is not None:
        env["CONTROL_KIND_PATH"] = str(helper)
    if adopter is not None:
        env["CHECK_DOCKET_RECONCILIATION_PATH"] = str(adopter)
    done = subprocess.run(
        [sys.executable, "-m", "unittest", TEST_MODULE, "-v"],
        cwd=str(REPO), capture_output=True, text=True, env=env,
    )
    failing = {line.split(": ", 1)[1].split(" ")[0]
               for line in done.stderr.splitlines()
               if line.startswith(("FAIL: ", "ERROR: "))}
    return done.returncode, failing


def main() -> int:
    parser = argparse.ArgumentParser(description="Mutation proof for control_kind.")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.list:
        for name, why, subject, _, _, aimed in MUTANTS:
            print(f"{name}  [{subject.name}]\n    reintroduces: {why}\n"
                  f"    aimed at: {', '.join(aimed)}\n")
        return 0

    originals = {p: p.read_text() for p in (HELPER, ADOPTER)}
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in originals}

    try:
        print("CONTROL (must be GREEN before any mutant is scored)")
        code, control = run_tests(None, None)
        if code != 0 or control:
            print(f"  CONTROL RED: rc={code} failures={sorted(control)}")
            return 1
        print("  control GREEN, 0 failures\n")

        killed, survived = [], []
        for name, why, subject, old, new, aimed in MUTANTS:
            source = originals[subject]
            if old not in source:
                print(f"{name}: ANCHOR NOT FOUND in {subject.name}")
                survived.append((name, "anchor missing"))
                continue
            mutated = source.replace(old, new, 1)
            with tempfile.TemporaryDirectory() as tmp:
                tmpdir = Path(tmp)
                # BOTH files are real copies so the adopter's sibling import
                # resolves to the temp directory rather than to scripts/.
                for path, text in originals.items():
                    (tmpdir / path.name).write_text(
                        mutated if path == subject else text)
                _, failures = run_tests(tmpdir / HELPER.name,
                                        tmpdir / ADOPTER.name)
            hit = sorted(set(aimed) & (failures - control))
            if hit:
                killed.append(name)
                print(f"{name}: KILLED by {', '.join(hit)}")
            else:
                survived.append((name, f"new failures {sorted(failures - control)}"))
                print(f"{name}: SURVIVED -- {sorted(failures - control)}")

        print(f"\n{len(killed)} killed, {len(survived)} survived, {len(MUTANTS)} total")
        for name, detail in survived:
            print(f"  SURVIVOR {name}: {detail}")
        return 0 if not survived else 1
    finally:
        for path, digest in before.items():
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                path.write_text(originals[path])
                print(f"{path.name} WAS MODIFIED AND HAS BEEN RESTORED")
            else:
                print(f"{path.name} sha256 unchanged: {digest[:16]}")
        purge_pycache(REPO)


if __name__ == "__main__":
    sys.exit(main())
