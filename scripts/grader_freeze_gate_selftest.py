#!/usr/bin/env python3
"""grader_freeze_gate_selftest.py -- the planted-violation controls for STEP (1),
and step (3) of Sanaa's wiring order made REACHABLE.

    "(3) then a planted violation proves the enforcer fires through the real path --
     the enforcer is itself an instrument and gets instrument-tested"
    -- SANAA-DIRECT 2026-09-03 ~17:30Z, item 6

THE REAL PATH, NOT A UNIT STUB.  Every arm below drives
`queue_runner.tick()` -- the same function the daemon's main() loop calls -- against
a scratch queue root of PRODUCTION SHAPE (<tmp>/prod/verification/queue/<team>/), so
the entry travels the whole production route: tick -> qec.load_entry -> qec.validate
(which now carries GRADER-FREEZE) -> move_refused() or launch().  Nothing is
monkeypatched on the enforcement path; the only injection is the box reading
(`measure=`), which queue_runner already accepts for its own controls and which
exists so a control cannot be flaky on live load (the L-339 class).

THE FIXTURE IS REAL HISTORY, AND NO FILE IS MODIFIED.  Planting a comparator drift by
editing a tracked script would dirty a shared working tree.  Instead the drift is
taken from the repository's own past: C = the commit that last touched
scripts/check_comparator_freeze.py, so the file on disk hashes EXACTLY as C froze it
(the PERMIT direction), while at C^ it hashed differently (the REFUSE direction --
that commit added +144/-8 lines).  One file, two commits, zero writes to the tree.

BOTH DIRECTIONS OR IT IS NOT TESTED.  An enforcer that refuses everything makes
coverage look perfect and grades nothing; an enforcer that refuses nothing is the
state this order exists to end.  Arms A1/A2 are the pair.  Arm A4 is the
planted-zero limb (standing rule 3): the SAME violating entry is re-validated with
GRADER-FREEZE removed from CHECKS and MUST come back clean, proving A1's refusal
comes from this guard and not from some other one that would have fired anyway.

NO `assert` (L-332).  Every control is an `if` that appends to a failure list.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

# __pycache__ IS CLEARED HERE, ABOVE THE IMPORTS, AND THE POSITION IS THE WHOLE POINT.
# FREEZE_ENFORCEMENT_SPEC section 3 makes this a binding condition on the harness, and
# this lab has had a clean control FAIL and a mutated case PASS off stale bytecode. A
# clear placed inside run() would fire AFTER the three modules below were already
# imported and would protect nothing in this process -- it would look like compliance
# and buy none. It must run before the first import or not at all.
shutil.rmtree(HERE / "__pycache__", ignore_errors=True)

import grader_freeze_gate as gfg      # noqa: E402
import queue_entry_check as qec       # noqa: E402
import queue_runner as qr             # noqa: E402

GRADER = "scripts/check_comparator_freeze.py"


def _git(*args) -> tuple[int, str]:
    p = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def _base(prereg_commit: str, cwd: Path, case: str) -> dict:
    return {
        "team": "cfd",
        "case_id": case,
        "prereg_commit": prereg_commit,
        "prereg_path": "CLAUDE.md",
        "launch_cmd": ["true"],
        "cwd": str(cwd),
        "ranks": 1,
        "cost_core_min_estimate": 0.1,
        # The wording is the validator's own SCHEMA requirement, not decoration: it
        # must carry "not measured" and an origin word, because this box cannot read
        # its own billing (COMPUTE_BUDGET_CHARTER section 5).
        "cost_basis": ("derived, not measured: selftest fixture whose launch_cmd is "
                       "`true`; it performs no compute and spends nothing"),
        "memory_floor_gb": 0.5,
        "enqueued_by": "grader_freeze_gate_selftest",
    }


def run() -> int:  # noqa: C901 -- a flat list of controls reads better than a framework
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, ok, detail))
        print(("  ok   " if ok else "  FAIL ") + name + (f"  [{detail}]" if detail else ""))

    skips: list[str] = []

    def skip(name: str, why: str) -> None:
        skips.append(f"{name}: {why}")
        print(f"  SKIP {name}  [{why}]")

    print("grader_freeze_gate --selftest (real repo history, scratch queue root; "
          "no tracked file is modified)")

    bad = gfg.ast_self_check()
    check("A0 the instrument carries 0 `assert` nodes (L-332)", not bad, "; ".join(bad))

    rc, c_match = _git("log", "-1", "--format=%H", "--", GRADER)
    if rc != 0 or not gfg.is_full_sha(c_match):
        print("REFUSED: cannot derive the fixture commit; no arm can run.")
        return 2
    rc, c_drift = _git("rev-parse", f"{c_match}^")
    if rc != 0 or not gfg.is_full_sha(c_drift):
        print("REFUSED: cannot derive the parent commit; no arm can run.")
        return 2

    frozen_match = gfg._git_rev_parse(REPO, f"{c_match}:{GRADER}")
    frozen_drift = gfg._git_rev_parse(REPO, f"{c_drift}:{GRADER}")
    disk = gfg.blob_sha((REPO / GRADER).read_bytes())
    fixture_ok = (frozen_match == disk and frozen_drift is not None
                  and frozen_drift != disk)
    check("A0b THE FIXTURE IS A DIFFERENCE, not an assumption: the grader on disk "
          "hashes EXACTLY as its last-touch commit froze it and DIFFERENTLY from that "
          "commit's parent -- so the two arms below cannot both be the same reading",
          fixture_ok,
          f"disk={disk[:12]} at_C={str(frozen_match)[:12]} at_C^={str(frozen_drift)[:12]}")
    if not fixture_ok:
        print("REFUSED: the working tree's copy of the grader is dirty, so the PERMIT "
              "direction cannot be distinguished from the REFUSE direction. "
              "Refusing rather than reporting a half-test.")
        return 2

    tmp = Path(tempfile.mkdtemp(prefix="grader_freeze_selftest_"))
    root = tmp / "prod" / "verification" / "queue"
    for t in qr.TEAMS:
        (root / t).mkdir(parents=True, exist_ok=True)
    log = qr.Log(root / "runner.log", echo=False)
    quiet = lambda: (3.0, 64.0)   # noqa: E731 -- injected box reading, as qr's own controls do

    def drive(entry: dict, name: str) -> tuple[str, Path, Path]:
        """Put ONE entry in the cfd queue and run a real tick over it."""
        for stray in root.glob("*/*.json"):
            stray.unlink()
        p = root / "cfd" / f"{name}.json"
        p.write_text(json.dumps(entry, indent=2) + "\n")
        verdict = qr.tick(root, log, 85.0, 0.9, 0.0, {}, measure=quiet)
        return verdict, root / "cfd" / "launched" / p.name, root / "cfd" / "refused" / p.name

    # --- A1 PLANTED VIOLATION -> the daemon REFUSES, through the real path ----------
    cwd1 = tmp / "case_violation"; cwd1.mkdir()
    e_bad = {**_base(c_drift, cwd1, "GFG_VIOLATION"), "grading_paths": [GRADER]}
    v1, launched1, refused1 = drive(e_bad, "GFG_VIOLATION")
    txt1 = ""
    rtxt = root / "cfd" / "refused" / "GFG_VIOLATION.REFUSED.txt"
    if rtxt.exists():
        txt1 = rtxt.read_text()
    check("A1 PLANTED VIOLATION: an entry whose comparator does NOT hash to what its "
          "frozen registration pinned is REFUSED by the live tick() -- moved to "
          "refused/, never launched, and the reason names GRADER-FREEZE",
          v1 == "REFUSED-ONLY" and refused1.exists() and not launched1.exists()
          and "GRADER-FREEZE" in txt1,
          f"tick={v1} refused={refused1.exists()} launched={launched1.exists()} "
          f"named={'GRADER-FREEZE' in txt1}")

    # --- A2 THE PERMIT DIRECTION + THE WRONG-OBJECT CONTROL ------------------------
    # FREEZE_ENFORCEMENT_SPEC section 3 arm 3: a case where a DIFFERENT file moved while
    # the comparator's sha is untouched must still LAUNCH, or the enforcer is merely
    # detecting "something moved" and is keyed on the wrong artifact. That property used
    # to be INCIDENTALLY true of this arm and was never asserted, so it was not tested:
    # the entry pins to an old commit at which many other files differ, but nothing
    # measured that. It is measured here and folded into the predicate, so the arm fails
    # if the wrong-object condition ever stops holding rather than passing on an
    # assumption.
    rc_o, moved = _git("diff", "--name-only", c_match)
    others = [m for m in moved.splitlines() if m.strip() and m.strip() != GRADER]
    cwd2 = tmp / "case_match"; cwd2.mkdir()
    e_ok = {**_base(c_match, cwd2, "GFG_MATCH"), "grading_paths": [GRADER]}
    v2, launched2, refused2 = drive(e_ok, "GFG_MATCH")
    stamp2 = {}
    if launched2.exists():
        stamp2 = (json.loads(launched2.read_text()).get("_grading_freeze") or {})
    check("A2 PERMIT DIRECTION + WRONG-OBJECT CONTROL: the SAME entry pinned to the "
          "commit the grader actually matches LAUNCHES and is stamped PINNED -- WHILE "
          f"{len(others)} OTHER file(s) demonstrably differ between that commit and the "
          "worktree. So the enforcer distinguishes (it is not a brick) AND it is keyed on "
          "the comparator itself, not on 'something in the repository moved'",
          v2 == "LAUNCHED" and launched2.exists() and not refused2.exists()
          and stamp2.get("verdict") == "PINNED" and rc_o == 0 and len(others) > 0,
          f"tick={v2} stamp={stamp2.get('verdict')} other_files_moved={len(others)} "
          f"e.g.={others[0] if others else '<NONE -- wrong-object limb NOT established>'}")

    # --- A3 THE TOLERANT DEFAULT IS VISIBLE, not silent -----------------------------
    cwd3 = tmp / "case_unpinned"; cwd3.mkdir()
    e_np = _base(c_match, cwd3, "GFG_UNPINNED")           # no grading_paths at all
    v3, launched3, _ = drive(e_np, "GFG_UNPINNED")
    stamp3 = {}
    if launched3.exists():
        stamp3 = (json.loads(launched3.read_text()).get("_grading_freeze") or {})
    logtxt = (root / "runner.log").read_text()
    check("A3 TOLERANT DEFAULT: an entry naming no comparator still launches (today's "
          "306 rows all look like this), but the launch record carries verdict UNPINNED "
          "and refusal_eligible=true, and runner.log carries a GRADER-FREEZE line -- so "
          "step (2) can COUNT what is uncovered instead of inferring it",
          v3 == "LAUNCHED" and stamp3.get("verdict") == "UNPINNED"
          and stamp3.get("refusal_eligible") is True
          and "GRADER-FREEZE GFG_UNPINNED: UNPINNED" in logtxt,
          f"tick={v3} stamp={stamp3.get('verdict')} eligible={stamp3.get('refusal_eligible')} "
          f"logged={'GRADER-FREEZE GFG_UNPINNED: UNPINNED' in logtxt}")

    # --- A4 PLANTED-ZERO / MUTATION LIMB (standing rule 3) --------------------------
    # The SAME violating entry, validated with GRADER-FREEZE REMOVED from CHECKS, must
    # come back CLEAN. If it does not, A1's refusal was never this guard's and the
    # guard is not shown load-bearing.
    without = {k: v for k, v in qec.CHECKS.items() if k != "GRADER-FREEZE"}
    fails_with = qec.validate(e_bad, REPO, None)
    fails_without = qec.validate(e_bad, REPO, None, without)
    check("A4 MUTATION/VISIBILITY LIMB: with GRADER-FREEZE removed from CHECKS the same "
          "violating entry is validated CLEAN -- so A1's refusal is produced by THIS "
          "guard and by nothing else that would have fired anyway",
          any(f.startswith("GRADER-FREEZE") for f in fails_with) and not fails_without,
          f"with={len(fails_with)} without={len(fails_without)}")

    # --- A5 A GRADER THAT DID NOT EXIST AT THE FREEZE -------------------------------
    # Board 47 measured 2 rows launched with a grader that did not exist at their
    # freeze. This file itself is exactly that shape against any historical commit.
    cwd5 = tmp / "case_absent_freeze"; cwd5.mkdir()
    e_af = {**_base(c_drift, cwd5, "GFG_ABSENT_FREEZE"),
            "grading_paths": ["scripts/grader_freeze_gate.py"]}
    v5, launched5, refused5 = drive(e_af, "GFG_ABSENT_FREEZE")
    check("A5 ABSENT-AT-FREEZE: a comparator that did not exist in the tree the freeze "
          "commit fixes is REFUSED -- a sha cannot pin a file that was not there",
          v5 == "REFUSED-ONLY" and refused5.exists() and not launched5.exists(),
          f"tick={v5} verdict={gfg.grading_freeze_record(e_af, REPO)['verdict']}")

    # --- A6 A PATH THAT ESCAPES THE REPO -------------------------------------------
    cwd6 = tmp / "case_escape"; cwd6.mkdir()
    e_esc = {**_base(c_match, cwd6, "GFG_ESCAPE"),
             "grading_paths": ["../../../etc/passwd"]}
    v6, launched6, refused6 = drive(e_esc, "GFG_ESCAPE")
    check("A6 MALFORMED: a grading path that escapes the repository is REFUSED, not "
          "silently normalised into something the pin appears to cover",
          v6 == "REFUSED-ONLY" and refused6.exists() and not launched6.exists(),
          f"tick={v6}")

    # --- A7 THE UNREGISTERED EXEMPTION IS AN EXEMPTION, NOT A PASS ------------------
    cwd7 = tmp / "case_feas"; cwd7.mkdir()
    e_fe = _base("FEASIBILITY", cwd7, "GFG_FEASIBILITY")
    rec7 = gfg.grading_freeze_record(e_fe, REPO)
    v7, launched7, _ = drive(e_fe, "GFG_FEASIBILITY")
    check("A7 UNREGISTERED EXEMPTION: Sanaa's 2026-08-31 feasibility/physics tag has no "
          "freeze to pin against, so the row launches and is recorded UNREGISTERED -- "
          "a distinct word from PINNED, and excluded from --pin-reading's denominator "
          "rather than counted as covered",
          v7 == "LAUNCHED" and rec7["verdict"] == "UNREGISTERED"
          and rec7["refusal_eligible"] is False,
          f"tick={v7} verdict={rec7['verdict']}")

    # --- A8 ABSENT-ON-DISK, if history offers the shape ----------------------------
    rc, deleted = _git("diff", "--name-only", "--diff-filter=D", c_match, "HEAD")
    cand = next((d for d in deleted.splitlines()
                 if d.strip() and not (REPO / d.strip()).exists()), None)
    if cand is None:
        skip("A8 ABSENT-ON-DISK",
             "no path exists that is present at the fixture commit and absent from the "
             "working tree, so this shape cannot be planted from real history without "
             "deleting a file -- which this control will not do")
    else:
        cwd8 = tmp / "case_absent_disk"; cwd8.mkdir()
        e_ad = {**_base(c_match, cwd8, "GFG_ABSENT_DISK"), "grading_paths": [cand]}
        v8, launched8, refused8 = drive(e_ad, "GFG_ABSENT_DISK")
        check("A8 ABSENT-ON-DISK: a comparator frozen at the registration but missing "
              "from the working tree is REFUSED -- the run would have nothing to grade it",
              v8 == "REFUSED-ONLY" and refused8.exists() and not launched8.exists(),
              f"tick={v8} path={cand}")

    # --- A9 THE PIN IS DERIVED, SO IT CANNOT BE SELF-CERTIFIED ----------------------
    # A row that writes a matching-looking sha beside a drifted comparator must still
    # be refused: the pin comes from prereg_commit, never from a field the row supplies.
    e_lie = {**e_bad, "grader_sha": disk, "grading_sha": disk}
    check("A9 NO SELF-CERTIFICATION: adding a field that states the drifted grader's own "
          "disk sha does NOT clear the refusal -- the pin is derived from prereg_commit, "
          "so the party who drifted the comparator cannot also write its alibi",
          any(f.startswith("GRADER-FREEZE") for f in qec.validate(e_lie, REPO, None)),
          "grader_sha/grading_sha ignored by construction")

    # --- A10 THE EMPTY-POPULATION REFUSAL (section 2p.2 at the METRIC's level) -------
    # FAILED BEFORE THIS REPAIR, measured: the walk returned total=0, eligible=0 and rc 0,
    # printing `PINNED / ELIGIBLE 0/0`. FREEZE_ENFORCEMENT_SPEC section 2 forbids exactly
    # that -- "empty population -> REFUSE, not 0/0 and not clean".
    empty = tmp / "emptyq"
    (empty / "cfd").mkdir(parents=True)
    refused_empty = False
    try:
        gfg.coverage(empty, REPO)
    except gfg.Refusal:
        refused_empty = True
    check("A10 EMPTY POPULATION REFUSES: a pin reading taken over a queue root holding "
          "no rows raises Refusal instead of reporting 0/0 -- an instrument that answers "
          "cleanly on an empty input would pass a repository whose every comparator was "
          "rewritten this morning",
          refused_empty, f"refused={refused_empty}")

    # --- A11 A REFUSED VIOLATION STAYS IN THE POPULATION -----------------------------
    # FAILED BEFORE THIS REPAIR, measured on this exact fixture: the row was correctly
    # refused into refused/ and the walk over that same root then reported total=0,
    # MISMATCH=0. Acting on the violation ERASED it from the metric, which is the one
    # way section 2s.4 says this kind of number can leave the lab worse off than none.
    cov = gfg.coverage(root, REPO)
    check("A11 A REFUSED VIOLATION IS COUNTED, NOT ERASED: after A1's MISMATCH row was "
          "refused into refused/, the pin reading over the same root still counts it -- "
          "in its own state's tally AND in a separate refused column, so the number "
          "cannot be improved by hiding a violation",
          cov["tally"].get("MISMATCH", 0) >= 1 and cov["refused_total"] >= 1
          and cov["refused_tally"].get("MISMATCH", 0) >= 1,
          f"MISMATCH={cov['tally'].get('MISMATCH', 0)} refused_total={cov['refused_total']} "
          f"refused_tally={dict(sorted(cov['refused_tally'].items()))} "
          f"rows_walked={cov['total']}")

    # --- A12 THE REAL REGISTRATION CARRIES NO DECLARATION -> FALL BACK, NOT REFUSE ----
    # The day-one non-regression limb for D8. Every registration in this repository is in
    # this state (measured: zero files at HEAD carry a GRADING_PATHS: line), so if the
    # fallback were wrong the whole queue would refuse on the day the precedence landed.
    reg_paths_real, reg_state_real = gfg.registration_declaration(e_ok, REPO)
    check("A12 REGISTRATION-FIRST FALLS BACK CLEANLY: a real frozen registration that is "
          "readable and carries NO declaration reads NONE (not UNREADABLE, not a "
          "conflict), so the entry's own field still governs and no row on disk today "
          "changes verdict",
          reg_state_real == "NONE" and not reg_paths_real,
          f"state={reg_state_real} paths={reg_paths_real}")

    # --- A13/A14 THE PRECEDENCE ITSELF, ON A REAL GIT REPOSITORY ---------------------
    # THE FIXTURE IS A REAL REPOSITORY, NOT A MONKEYPATCH. No file at HEAD carries a
    # GRADING_PATHS: declaration, so the two arms below cannot be planted from this
    # repository's history the way A1/A2 are. They are planted in a THROWAWAY GIT REPO in
    # tmp instead: real `git init`, a real commit, and the same real `rev-parse` +
    # `cat-file` reads the production path makes. The ONLY injection is which repository
    # queue_runner reads -- `qr.REPO` -- which is a configuration constant, not a step in
    # the guarded logic; the whole enforcement route (tick -> validate -> CHECKS ->
    # gfg.refusals -> move_refused) runs untouched. The shared repository is never
    # written, never committed to, and never read as a fixture here.
    fixrepo = tmp / "fixrepo"
    (fixrepo / "scripts").mkdir(parents=True)
    (fixrepo / "scripts" / "analyse_x.py").write_text("# comparator X, v1\n")
    (fixrepo / "scripts" / "analyse_y.py").write_text("# comparator Y\n")
    (fixrepo / "PREREG.md").write_text(
        "# fixture registration\n\nGRADING_PATHS: scripts/analyse_x.py\n")
    (fixrepo / "PREREG_CONFLICT.md").write_text(
        "# fixture registration with two disagreeing declarations\n\n"
        "GRADING_PATHS: scripts/analyse_x.py\n\nGRADING_PATHS: scripts/analyse_y.py\n")
    for args in (("init", "-q", "-b", "main"),
                 ("config", "user.email", "selftest@localhost"),
                 ("config", "user.name", "grader_freeze_gate_selftest"),
                 ("add", "PREREG.md", "PREREG_CONFLICT.md",
                  "scripts/analyse_x.py", "scripts/analyse_y.py"),
                 ("commit", "-q", "-m", "fixture")):
        subprocess.run(["git", "-C", str(fixrepo), *args], capture_output=True, text=True)
    _fx = subprocess.run(["git", "-C", str(fixrepo), "rev-parse", "HEAD"],
                         capture_output=True, text=True)
    rcf, fix_sha = _fx.returncode, _fx.stdout.strip()

    if rcf != 0 or not gfg.is_full_sha(fix_sha):
        skip("A13/A14 REGISTRATION PRECEDENCE",
             "the throwaway fixture repository could not be created, so the precedence "
             "arms cannot be driven against a real git read and will NOT be faked")
    else:
        # THE DRIFT: comparator X is edited AFTER the commit that froze it, so its disk
        # bytes no longer hash to the frozen blob -- the same shape as A1, in the fixture.
        (fixrepo / "scripts" / "analyse_x.py").write_text("# comparator X, v2 DRIFTED\n")
        saved_repo = qr.REPO
        try:
            qr.REPO = fixrepo
            # A13: the entry names NOTHING. Before D8 that read UNPINNED and LAUNCHED.
            cwdA = tmp / "case_regwins"; cwdA.mkdir()
            e_reg = {**_base(fix_sha, cwdA, "GFG_REG_WINS"), "prereg_path": "PREREG.md"}
            vA, launchedA, refusedA = drive(e_reg, "GFG_REG_WINS")
            recA = gfg.grading_freeze_record(e_reg, fixrepo)
            check("A13 THE REGISTRATION PINS WHAT THE ENTRY OMITS: an entry declaring NO "
                  "comparator, whose FROZEN REGISTRATION declares one that has since "
                  "drifted, is REFUSED -- before D8 this row read UNPINNED and launched, "
                  "so omitting the field was a way out of the pin",
                  vA == "REFUSED-ONLY" and refusedA.exists() and not launchedA.exists()
                  and recA["verdict"] == "MISMATCH",
                  f"tick={vA} verdict={recA['verdict']} field={recA['field']}")

            # A14: registration says X, entry says Y. Section 2s.6: never choose.
            cwdB = tmp / "case_conflict"; cwdB.mkdir()
            e_con = {**_base(fix_sha, cwdB, "GFG_DECL_CONFLICT"),
                     "prereg_path": "PREREG.md",
                     "grading_paths": ["scripts/analyse_y.py"]}
            vB, launchedB, refusedB = drive(e_con, "GFG_DECL_CONFLICT")
            recB = gfg.grading_freeze_record(e_con, fixrepo)
            check("A14 DISAGREEMENT REFUSES, IT DOES NOT PICK: a registration naming "
                  "comparator X against an entry naming comparator Y is REFUSED "
                  "(DECLARATION-CONFLICT) -- and note comparator Y is UNDRIFTED, so a "
                  "guard that silently preferred the entry would have PASSED this row",
                  vB == "REFUSED-ONLY" and refusedB.exists() and not launchedB.exists()
                  and recB["verdict"] == "DECLARATION-CONFLICT",
                  f"tick={vB} verdict={recB['verdict']}")

            # A15: two disagreeing declarations INSIDE one registration.
            e_int = {**_base(fix_sha, tmp / "case_regwins", "GFG_INTERNAL"),
                     "prereg_path": "PREREG_CONFLICT.md"}
            recC = gfg.grading_freeze_record(e_int, fixrepo)
            check("A15 'NEVER CHOOSE' APPLIES INSIDE ONE DOCUMENT TOO: a registration "
                  "carrying two GRADING_PATHS declarations that disagree is a conflict, "
                  "not a menu",
                  recC["verdict"] == "DECLARATION-CONFLICT",
                  f"verdict={recC['verdict']}")
        finally:
            qr.REPO = saved_repo

    skip("A16 REGISTRATION-UNREADABLE",
         "the blob-exists-but-unreadable shape cannot be planted without corrupting a "
         "git object store, which this control will not do; the branch is reachable by "
         "inspection only and is reported as UNTESTED rather than claimed")

    shutil.rmtree(tmp)

    n_fail = sum(1 for _, ok, _ in checks if not ok)
    n_pass = len(checks) - n_fail
    print(f"\n  {n_pass} pass / {n_fail} fail / {len(skips)} skip")
    for s in skips:
        print(f"    SKIPPED -- {s}")
    if n_fail:
        print(f"SELFTEST FAIL: {n_fail} of {len(checks)} controls failed")
        return 1
    if n_pass < 8:
        print("SELFTEST FAIL: too few controls ran to call this instrument tested")
        return 1
    print(f"SELFTEST PASS: {n_pass}/{len(checks)} controls, both directions proven, "
          f"0 asserts")
    return 0


if __name__ == "__main__":
    sys.exit(run())
