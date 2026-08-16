#!/usr/bin/env python3
"""Mutation proof for the printed remedies of the proposal-coverage check (D261).

WHY IT IS TRACKED. A mutation result quoted in a commit message cannot be
re-run by the next reader. This one can.

WHAT IT PROVES AND WHAT IT DOES NOT. It shows each assertion CAN fail, never
that it asserts the right thing. The stronger evidence for this repair is not a
mutation at all and is recorded beside it: the pin was run against the PRISTINE
pre-repair check, whose LOST remedy really did name `set_status`, and it failed
with the behavioural message *"the printed LOST remedy names set_status(), it
was executed, and the id is STILL LOST"*. A mutant tests the tests against a
change the author invented; that run tested them against the defect that
actually existed.

NO SYMLINK MIRROR, AND THAT IS DELIBERATE. The sibling harnesses build a mirror
of the repository out of symlinks, which cost an hour earlier tonight:
`Path(__file__).resolve()` FOLLOWS SYMLINKS, so the suite resolved back to the
real repository and loaded the unmutated subject, and every mutant survived
with zero new failures. `sdk/tests/test_coverage_remedy_is_executable.py`
instead honours an explicit `COVERAGE_CHECK_PATH` override, so a mutant is a
real file in a temp directory and the env var points the suite at it. There is
no symlink anywhere in this harness and therefore no `resolve()` to be fooled.

HOW IT IS JUDGED. The control runs FIRST and must be GREEN. A mutant is killed
only when a test IT NAMED is in the NEW-FAILURE set -- failure-count delta
against that green control. `returncode != 0` is never the kill criterion.

`__pycache__` is purged before every cell. The subject's sha256 is asserted
unchanged in a `finally`; no tracked file is ever held mutated, because the
mutant is written to a temp path and the tracked file is never touched at all.

Run:  python3 scripts/mutation_harness_coverage_remedy.py
      python3 scripts/mutation_harness_coverage_remedy.py --list
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
TARGET = REPO / "scripts" / "check_proposal_surface_coverage.py"
TEST_MODULE = "sdk.tests.test_coverage_remedy_is_executable"

_LOST_REPAIRED = (
    '"LOST": "a decision recorded ONLY in the file; ONE `refresh_docket()` "\n'
    '            "merges every id in this class into docket.json -- NOT "\n'
    '            "`set_status`, which returns None for an id the docket does not "\n'
    '            "yet hold and changes nothing",'
)

MUTANTS: list[tuple[str, str, str, str, tuple[str, ...]]] = [
    (
        "M1-restore-the-historical-no-op",
        "THE ORIGINAL DEFECT. LOST is told to use `set_status`, which returns "
        "None for an id the docket does not hold -- so the printed instruction "
        "changes nothing on every id the class reports.",
        _LOST_REPAIRED,
        '"LOST": "a decision recorded ONLY in the file; move it into "\n'
        '            "docket.json via set_status so the control room can act on it",',
        (
            "test_following_the_printed_remedy_clears_the_fault",
            "test_the_lost_remedy_does_not_name_set_status",
        ),
    ),
    (
        "M2-lost-names-a-function-that-does-not-exist",
        "the remedy names a plausible call that `chief_engineer.agenda` does "
        "not define, so an operator following it gets an AttributeError rather "
        "than a repair -- loud, but still not a remedy.",
        _LOST_REPAIRED,
        '"LOST": "a decision recorded ONLY in the file; run "\n'
        '            "`merge_inbox_into_docket()` to fix it",',
        (
            "test_following_the_printed_remedy_clears_the_fault",
            "test_every_named_call_resolves_on_the_agenda_module",
        ),
    ),
    (
        "M3-lost-names-no-call-at-all",
        "the remedy degrades to prose with no runnable action, which is how a "
        "class stops being checkable: nobody can execute a sentence.",
        _LOST_REPAIRED,
        '"LOST": "a decision recorded ONLY in the file; someone should move "\n'
        '            "the record across so the control room can act on it",',
        ("test_following_the_printed_remedy_clears_the_fault",),
    ),
    (
        "M4-unabsorbed-told-to-refresh",
        "UNABSORBED is pointed at `refresh_docket()`, which cannot fix it: a "
        "refresh carries only what the inbox FILE holds and this class's "
        "evidence lives in an artifact. The call succeeds and the fault stays.",
        '"UNABSORBED": "an artifact on disk names this item and the docket record "\n'
        '                  "carries no trace of that work; READ THE ARTIFACT, then "\n'
        '                  "`set_status(<id>, <status>, outcome=...)` -- a "\n'
        '                  "`refresh_docket()` cannot fix this class, it carries only "\n'
        '                  "what the inbox FILE holds",',
        '"UNABSORBED": "an artifact on disk names this item; run "\n'
        '                  "`refresh_docket()` to absorb it",',
        ("test_following_the_printed_remedy_clears_the_fault",),
    ),
    (
        "M5-lost-classification-removed",
        "a decided inbox-only id stops being called LOST, which would make the "
        "fixture guard vacuous and every remedy assertion meaningless.",
        'klass, detail = "LOST", f"file records {status!r}, docket has "',
        'klass, detail = "PENDING", f"file records {status!r}, docket has "',
        ("test_the_fixture_is_genuinely_lost",),
    ),
    (
        "M6-unabsorbed-detection-removed",
        "artifacts stop producing UNABSORBED rows, so that fixture guard goes "
        "vacuous too.",
        "    unabsorbed: list[dict] = []",
        "    unabsorbed: list[dict] = []\n    named = {}",
        ("test_the_fixture_is_genuinely_unabsorbed",),
    ),
]


def purge_pycache(root: Path) -> None:
    for cache in root.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)


def run_tests(subject: Path | None) -> tuple[int, set[str]]:
    """Run the pin, optionally against a substituted subject."""
    purge_pycache(REPO)
    env = {**os.environ}
    if subject is not None:
        env["COVERAGE_CHECK_PATH"] = str(subject)
    else:
        env.pop("COVERAGE_CHECK_PATH", None)
    done = subprocess.run(
        [sys.executable, "-m", "unittest", TEST_MODULE, "-v"],
        cwd=str(REPO), capture_output=True, text=True, env=env,
    )
    failing = {line.split(": ", 1)[1].split(" ")[0]
               for line in done.stderr.splitlines()
               if line.startswith(("FAIL: ", "ERROR: "))}
    return done.returncode, failing


def main() -> int:
    parser = argparse.ArgumentParser(description="Mutation proof for D261.")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.list:
        for name, why, _, _, aimed in MUTANTS:
            print(f"{name}\n    reintroduces: {why}\n    aimed at: {', '.join(aimed)}\n")
        return 0

    original = TARGET.read_text()
    before = hashlib.sha256(TARGET.read_bytes()).hexdigest()

    try:
        print("CONTROL (must be GREEN before any mutant is scored)")
        code, control = run_tests(None)
        if code != 0 or control:
            print(f"  CONTROL RED: rc={code} failures={sorted(control)}")
            return 1
        print("  control GREEN, 0 failures\n")

        killed, survived = [], []
        for name, why, old, new, aimed in MUTANTS:
            if old not in original:
                print(f"{name}: ANCHOR NOT FOUND")
                survived.append((name, "anchor missing"))
                continue
            mutated = original.replace(old, new, 1)
            with tempfile.TemporaryDirectory() as tmp:
                subject = Path(tmp) / "check_proposal_surface_coverage.py"
                subject.write_text(mutated)
                _, failures = run_tests(subject)
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
        after = hashlib.sha256(TARGET.read_bytes()).hexdigest()
        if after != before:  # pragma: no cover - must never fire
            TARGET.write_text(original)
            print("SUBJECT WAS MODIFIED AND HAS BEEN RESTORED -- investigate")
        else:
            print(f"subject sha256 unchanged: {before[:16]}")
        purge_pycache(REPO)


if __name__ == "__main__":
    sys.exit(main())
