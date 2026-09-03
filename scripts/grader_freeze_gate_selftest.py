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

    # --- A2 THE PERMIT DIRECTION. Without this, refusing everything would pass A1 ---
    cwd2 = tmp / "case_match"; cwd2.mkdir()
    e_ok = {**_base(c_match, cwd2, "GFG_MATCH"), "grading_paths": [GRADER]}
    v2, launched2, refused2 = drive(e_ok, "GFG_MATCH")
    stamp2 = {}
    if launched2.exists():
        stamp2 = (json.loads(launched2.read_text()).get("_grading_freeze") or {})
    check("A2 PERMIT DIRECTION: the SAME entry pinned to the commit the grader "
          "actually matches LAUNCHES, and its record is stamped PINNED -- the enforcer "
          "distinguishes, it is not a brick",
          v2 == "LAUNCHED" and launched2.exists() and not refused2.exists()
          and stamp2.get("verdict") == "PINNED",
          f"tick={v2} launched={launched2.exists()} stamp={stamp2.get('verdict')}")

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
          "a distinct word from PINNED, and excluded from --coverage's denominator "
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
