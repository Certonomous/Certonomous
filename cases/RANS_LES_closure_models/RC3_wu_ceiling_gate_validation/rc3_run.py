#!/usr/bin/env python3
"""RC3 campaign runner -- the producer, and the only thing in RC3 that launches.

Registration: cases/RANS_LES_closure_models/RC3_wu_ceiling_gate_validation/
PREREGISTRATION.md -- section 8 (strict completion, clauses 1-3 are THIS
module's contract to satisfy), section 9 (the model set and `simpleFoam`,
serial, ranks = 1), section 10 (the per-solve `timeout 3600` and the
campaign-level 24,000 wall-s accumulator that is the BINDING control) and
section 11 (this module's registered job and its registered refusals).

WHY THIS MODULE EXISTS -- the defect it closes
---------------------------------------------
`docs/closure/CLAUSE_SATISFIABILITY_AUDIT.md` FINDING B, measured: RC3's
completion clauses 1-3 delegate to `r4_lib.solve_complete`, which requires a
file named `rc` in the case directory (`r4_lib.py:508-511`) and a log named
`log.solve` (`r4_lib.py:505`).  The Wu predecessor runner
`Wu2018_PIML_RF/aposteriori/run_solves.sh:14` records the return code as the
TEXT `rc=<n> seconds=<e>` inside `log.solve.done` and NEVER writes a file named
`rc`.  Measured on the producers RC3 would have run: `rc` present 0 of 18
(`aposteriori/wu2018`) and 0 of 36 (`aposteriori_frozenk/wu2018`), against the
same reader finding it 60 of 60 on `r4/aposteriori`.  Every RC3 row would have
failed clause 1 and RC3 would have returned NOT A RESULT for the whole item
independently of the physics.

RC3 had NO committed runner at all.  The repair taken is the STRICTER of the two
available: **the clause is not weakened; the producer is made to emit what the
clause reads.**  This module writes BOTH channels -- the `rc` file the frozen
helper reads AND the predecessor's `log.solve.done` line, so nothing that read
the predecessor's convention loses it -- and then READS BOTH BACK from disk and
refuses if either did not land.

THE R5D-PROOF SMOKE ROW
-----------------------
`grade_r5d.py:296` froze a clause no producer could satisfy, and it was found 54
records later.  The mechanism that made that possible was that nothing checked
the producer's FIRST real output against the clause.  So:
`campaign()` puts the FIRST completed solve of the campaign through
`r4_lib.solve_complete(case, required=())` -- the exact frozen helper
`rc3_ceiling.completion()` will call -- and REFUSES THE WHOLE CAMPAIGN if the
real producer's real output does not satisfy clauses 1-3.  A producer-contract
gap can then cost one solve, never thirty.

SERIAL, AND WHY THAT IS NOT A CONVENIENCE
-----------------------------------------
Both predecessor runners drive `xargs -P 6` (`aposteriori/run_solves.sh:20`,
`aposteriori_frozenk/run_solves.sh:19`), i.e. six concurrent solves.  Section 9
fixes the formulation as "steady, `simpleFoam`, serial (ranks = 1)" and section
10 defines the campaign accumulator as 24,000 WALL seconds AT RANKS 1.  Under a
`-P 6` runner the campaign's wall clock is not the sum of its solves' wall
times, so a wall-clock accumulator would admit up to six times the registered
budget.  This runner is therefore SERIAL and the accumulator sums PER-SOLVE wall
seconds, which at ranks = 1 is exactly core-minutes x 60.

NOTHING IS LAUNCHED WHILE THE REGISTRATION IS DRAFT/UNFROZEN.  Every entry point
calls `build_rc3_ladder.refuse_if_unfrozen()` first.

NO ast.Assert CARRIES ANY REFUSAL, GUARD, CONTROL OR GATE (section 6.1, L-332 /
D476 section 31.3).  `--selftest` parses this file with `ast` and requires zero.
"""
from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CLOSURE = os.path.dirname(HERE)
COMMON = os.path.join(CLOSURE, "_common")
R4 = os.path.join(CLOSURE, "R4_sparta_build")
for _p in (HERE, COMMON, R4):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import r4_lib                                    # noqa: E402
import build_rc3_ladder as B                     # noqa: E402

# ---- the producer contract, FIXED.  Every name here is read by a clause.
SOLVER = "simpleFoam"                 # section 9: the same solver, no new one
LOG_NAME = "log.solve"                # r4_lib.py:505 reads exactly this name
RC_NAME = "rc"                        # r4_lib.py:508-511 reads exactly this file
DONE_NAME = "log.solve.done"          # the predecessor's channel, kept as well
PER_SOLVE_TIMEOUT_S = B.PER_SOLVE_TIMEOUT_S      # 3600, section 10
CAMPAIGN_WALL_CAP_S = B.CAMPAIGN_WALL_CAP_S      # 24000, section 10, BINDING
RANKS = B.RANKS                                  # 1, section 9/10


def refuse(msg):
    """The only refusal primitive here.  Survives `python3 -O` (section 6.1)."""
    sys.stderr.write("RC3 REFUSED (sys.exit 2): " + str(msg) + "\n")
    sys.stderr.flush()
    raise SystemExit(2)


def _default_writer(path, text):
    open(path, "w").write(text)


def record(case, rc, wall_s, _writer=_default_writer):
    """Write the return code into BOTH channels and READ BOTH BACK.

    `<case>/rc` is the file `r4_lib.solve_complete` reads (r4_lib.py:508-511);
    `<case>/log.solve.done` is the predecessor's own line
    (`run_solves.sh:14`), kept verbatim in shape so nothing that read the
    predecessor's convention is lost.

    Standing rule 3 applied to the WRITER, exactly as
    `build_rc3_ladder.write_bdelta_and_verify` applies it (amendment A1.5): a
    writer not shown to have put the value on disk has not been shown to have
    recorded anything.  `_writer` is injectable so `--selftest` can drive a
    writer that silently fails to land the file and show this guard FIRE.
    """
    if not os.path.isdir(case):
        refuse("record(): case directory absent: " + case)
    rc_i = int(rc)
    rc_path = os.path.join(case, RC_NAME)
    done_path = os.path.join(case, DONE_NAME)
    _writer(rc_path, str(rc_i) + "\n")
    _writer(done_path, "rc=%d seconds=%d\n" % (rc_i, int(wall_s)))
    if not os.path.exists(rc_path):
        refuse("record(): " + RC_NAME + " did not land in " + case
               + "; clause 1 reads this exact file (r4_lib.py:508)")
    back = open(rc_path).read().strip()
    if back != str(rc_i):
        refuse("record(): " + RC_NAME + " read back as " + repr(back)
               + " but " + repr(str(rc_i)) + " was written")
    if not os.path.exists(done_path):
        refuse("record(): " + DONE_NAME + " did not land in " + case)
    dback = open(done_path).read().strip()
    if not dback.startswith("rc=%d " % rc_i):
        refuse("record(): " + DONE_NAME + " read back as " + repr(dback))
    return {"case": case, "rc": rc_i, "wall_s": float(wall_s),
            "rc_file": rc_path, "done_file": done_path,
            "rc_readback": back, "done_readback": dback}


def _default_spawn(argv, cwd, log_path, timeout_s):
    """Launch `argv` in `cwd`, tee stdout+stderr into `log_path`, return rc.

    The timeout is enforced by the `timeout` binary in argv, exactly as
    `aposteriori_frozenk/run_solves.sh:11` does, so the enforcement is the
    predecessor's and not a Python-side kill that could leave the solver alive.
    """
    with open(log_path, "w") as fh:
        p = subprocess.Popen(argv, cwd=cwd, stdout=fh,
                             stderr=subprocess.STDOUT)
        return int(p.wait())


def solve_one(case, spent_s, _spawn=_default_spawn, _writer=_default_writer,
              check_freeze=True):
    """One solve, with the accumulator checked BEFORE the launch.

    Section 10 line 519 names the campaign accumulator "the binding control".
    Two stops, both of them stops and neither an extension:
      * if the accumulator is already at or over the cap, this REFUSES rather
        than launching;
      * the per-solve timeout handed to `timeout` is
        `min(PER_SOLVE_TIMEOUT_S, CAMPAIGN_WALL_CAP_S - spent_s)`, so the
        campaign cannot walk past the cap inside a single solve.  It can only
        ever SHORTEN a solve, never lengthen one.
    """
    if check_freeze:
        B.refuse_if_unfrozen()
    if not os.path.isdir(case):
        refuse("solve_one(): case directory absent: " + case)
    remaining = float(CAMPAIGN_WALL_CAP_S) - float(spent_s)
    if remaining <= 0.0:
        refuse("section 10 campaign accumulator: %.0f wall s already spent of "
               "the registered cap %d (= %d core-min at ranks %d).  An overrun "
               "STOPS the campaign; it does not get a new budget"
               % (float(spent_s), CAMPAIGN_WALL_CAP_S,
                  CAMPAIGN_WALL_CAP_S // 60, RANKS))
    budget = int(min(float(PER_SOLVE_TIMEOUT_S), remaining))
    log_path = os.path.join(case, LOG_NAME)
    argv = ["timeout", str(budget), SOLVER]
    t0 = time.time()
    rc = _spawn(argv, case, log_path, budget)
    wall = time.time() - t0
    rec = record(case, rc, wall, _writer=_writer)
    rec.update({"argv": argv, "timeout_s": budget, "log": log_path,
                "ranks": RANKS, "core_minutes": wall * RANKS / 60.0})
    print("[rc3 solve] %s rc=%d wall=%.1fs timeout=%ds core-min=%.2f"
          % (case, rc, wall, budget, rec["core_minutes"]))
    return rec


def verify_producer_contract(case):
    """THE SMOKE ROW.  Clauses 1-3 against the REAL producer's REAL output.

    Calls the same frozen helper `rc3_ceiling.completion()` calls, with the same
    argument, so what is checked here is exactly what will grade the campaign.
    Refuses on failure: a producer-contract gap costs one solve, not thirty.
    """
    ok, reason, info = r4_lib.solve_complete(case, required=())
    print("[rc3 smoke row] clauses 1-3 on the first real solve: "
          + ("SATISFIED" if ok else "NOT SATISFIED") + " -- " + str(reason))
    if not ok:
        refuse("section 8 clauses 1-3 are NOT satisfied by this campaign's own "
               "first real solve (" + case + "): " + str(reason)
               + ".  This is the FINDING B / R5D failure mode and the campaign "
               "STOPS here rather than producing 30 rows that cannot be graded")
    return info


def campaign(cases, out_path=None, _spawn=_default_spawn,
             _writer=_default_writer, check_freeze=True):
    """Run the registered solves SERIALLY under the section 10 accumulator."""
    if check_freeze:
        B.refuse_if_unfrozen()
    spent = 0.0
    recs = []
    smoke = None
    for case in cases:
        rec = solve_one(case, spent, _spawn=_spawn, _writer=_writer,
                        check_freeze=False)
        spent += rec["wall_s"]
        rec["campaign_spent_wall_s"] = spent
        rec["campaign_spent_core_min"] = spent * RANKS / 60.0
        recs.append(rec)
        if smoke is None:
            smoke = verify_producer_contract(case)
    out = {"solves": recs, "n_solves": len(recs),
           "campaign_wall_s": spent, "ranks": RANKS,
           "campaign_core_minutes": spent * RANKS / 60.0,
           "registered_cap_core_minutes": CAMPAIGN_WALL_CAP_S // 60,
           "registered_estimate_core_minutes": 160,
           "smoke_row": smoke}
    print("[rc3 campaign] %d solves, %.1f wall s, %.1f core-min of the "
          "registered %d core-min cap"
          % (len(recs), spent, spent * RANKS / 60.0, CAMPAIGN_WALL_CAP_S // 60))
    if out_path:
        json.dump(out, open(out_path, "w"), indent=1, default=str)
    return out


# ---------------------------------------------------------------- selftest
def _fires(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except SystemExit as e:
        return int(e.code or 0) == 2
    return False


# The NAMED real producer artifacts the parity check is built from.  Every byte
# of the log, the controlDict and the time directory below is `simpleFoam`
# output already on disk; the ONLY thing this module adds is the one file
# `record()` writes.  Zero solver compute.
REAL_CASES = (
    "/home/ubuntu/closure-data/aposteriori/wu2018/AR_1_Ret_360/truth",
    "/home/ubuntu/closure-data/aposteriori_frozenk/wu2018/CBFS13700/L_truth",
)
# A NAMED real producer artifact whose own recorded rc is NON-zero (it hit
# `timeout 3600`): the negative direction of the parity check.
REAL_TIMED_OUT = ("/home/ubuntu/closure-data/aposteriori_frozenk/wu2018/"
                  "AR_3_Ret_360/S_null")


def link_real_case(src, dst):
    """A case directory whose every artifact IS the real producer's, by symlink.

    Nothing under `src` is written, renamed or touched.  `os.path.getmtime`
    follows symlinks, so the age guard (clause 6) still dates the real files.
    """
    os.makedirs(dst)
    for name in sorted(os.listdir(src)):
        if name in (RC_NAME, DONE_NAME):
            continue
        os.symlink(os.path.join(src, name), os.path.join(dst, name))
    return dst


def selftest():
    ok = []

    def note(name, passed, detail=""):
        ok.append((name, bool(passed), detail))

    tree = ast.parse(open(os.path.abspath(__file__)).read())
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    note("ast.Assert count == 0", n_assert == 0, "counted " + str(n_assert))

    note("LOG_NAME is the name the frozen helper reads",
         LOG_NAME == "log.solve")
    note("RC_NAME is the file the frozen helper reads (r4_lib.py:508)",
         RC_NAME == "rc")
    note("RANKS == 1 and the accumulator is in wall s at ranks 1",
         RANKS == 1 and CAMPAIGN_WALL_CAP_S == 24000)
    note("per-solve timeout is the registered 3600 s",
         PER_SOLVE_TIMEOUT_S == 3600)

    tmp = tempfile.mkdtemp(prefix="rc3_run_selftest_")
    try:
        # ---- 1. record(): both channels land and are read back.
        c = os.path.join(tmp, "rec")
        os.makedirs(c)
        r = record(c, 0, 12.5)
        note("record() writes the rc file the clause reads",
             open(os.path.join(c, RC_NAME)).read().strip() == "0")
        note("record() also writes the predecessor's log.solve.done line",
             open(os.path.join(c, DONE_NAME)).read().strip()
             == "rc=0 seconds=12")
        note("record() read-back is reported", r["rc_readback"] == "0")

        def blind(path, text):
            return None                     # writes nothing at all

        c2 = os.path.join(tmp, "rec_blind")
        os.makedirs(c2)
        note("record() REFUSES when the writer silently fails to land the rc "
             "file (rule 3 applied to the writer)",
             _fires(record, c2, 0, 1.0, blind))

        def liar(path, text):
            open(path, "w").write("999\n")

        c3 = os.path.join(tmp, "rec_liar")
        os.makedirs(c3)
        note("record() REFUSES when the rc file reads back as something else",
             _fires(record, c3, 0, 1.0, liar))
        note("record() REFUSES on an absent case directory",
             _fires(record, os.path.join(tmp, "nope"), 0, 1.0))

        # ---- 2. solve_one(): the accumulator is checked BEFORE the launch,
        #         and the launch is shown to happen with a REAL subprocess.
        launched = []

        def spy(argv, cwd, log_path, timeout_s):
            launched.append((tuple(argv), cwd, timeout_s))
            # a REAL subprocess, not a written fixture: whatever it prints is
            # printed by a process this module actually spawned.
            with open(log_path, "w") as fh:
                p = subprocess.Popen(["/bin/sh", "-c",
                                      "printf 'Time = 1\\nExecutionTime = "
                                      "0.1 s\\nEnd\\n'"],
                                     cwd=cwd, stdout=fh,
                                     stderr=subprocess.STDOUT)
                return int(p.wait())

        c4 = os.path.join(tmp, "solve")
        os.makedirs(c4)
        rec = solve_one(c4, 0.0, _spawn=spy, check_freeze=False)
        note("solve_one() launches and the rc file lands", rec["rc"] == 0
             and os.path.exists(os.path.join(c4, RC_NAME)))
        note("solve_one() invokes `timeout <n> simpleFoam`, the predecessor's "
             "own enforcement shape",
             launched[0][0] == ("timeout", str(PER_SOLVE_TIMEOUT_S), SOLVER))
        note("solve_one() writes the log under the name the clause reads",
             os.path.exists(os.path.join(c4, LOG_NAME)))
        note("a REAL spawned subprocess wrote that log, not a Python write",
             "End" in open(os.path.join(c4, LOG_NAME)).read())

        c5 = os.path.join(tmp, "solve_capped")
        os.makedirs(c5)
        note("solve_one() REFUSES to launch when the accumulator is already at "
             "the registered cap",
             _fires(solve_one, c5, float(CAMPAIGN_WALL_CAP_S), spy,
                    _default_writer, False))
        c6 = os.path.join(tmp, "solve_clamped")
        os.makedirs(c6)
        launched.clear()
        solve_one(c6, float(CAMPAIGN_WALL_CAP_S) - 100.0, _spawn=spy,
                  check_freeze=False)
        note("the per-solve timeout is CLAMPED to the remaining campaign "
             "budget -- it can only ever shorten a solve",
             launched[0][2] == 100, "clamped to " + str(launched[0][2]) + " s")

        # ---- 3. THE PARITY CHECK.  Clauses 1-3 on REAL producer output, with
        #         nothing added but the file record() writes.
        for src in REAL_CASES:
            nm = os.path.basename(os.path.dirname(src)) + "_" + \
                os.path.basename(src)
            if not os.path.isdir(src):
                note("real producer case present: " + nm, False, "absent")
                continue
            dst = link_real_case(src, os.path.join(tmp, "real_" + nm))
            done = os.path.join(src, DONE_NAME)
            real_rc = 0
            if os.path.exists(done):
                t = open(done).read().strip()
                real_rc = int(t.split("rc=")[1].split()[0])
            record(dst, real_rc, 1.0)
            okc, reason, _i = r4_lib.solve_complete(dst, required=())
            note("PARITY: clauses 1-3 SATISFIED on real simpleFoam output "
                 "plus only the file this runner writes -- " + nm, okc, reason)

        if os.path.isdir(REAL_TIMED_OUT):
            dst = link_real_case(REAL_TIMED_OUT,
                                 os.path.join(tmp, "real_timedout"))
            record(dst, 124, 3600.0)
            okc, reason, _i = r4_lib.solve_complete(dst, required=())
            note("PARITY, NEGATIVE DIRECTION: clauses 1-3 REJECT the real "
                 "`timeout 3600` row this runner would have recorded as rc=124",
                 not okc, reason)
            # and the same real tree with rc=0 forged must STILL be rejected,
            # because that row carries no End line
            os.remove(os.path.join(dst, RC_NAME))
            record(dst, 0, 3600.0)
            okc2, reason2, _i2 = r4_lib.solve_complete(dst, required=())
            note("PARITY: a forged rc=0 on that same real timed-out tree is "
                 "STILL rejected -- clause 2's End line is independent of the "
                 "rc channel", not okc2, reason2)
        else:
            note("real timed-out producer case present", False, "absent")

        # ---- 4. the smoke row fires on a producer that does not comply.
        c7 = os.path.join(tmp, "smoke_bad")
        os.makedirs(c7)
        open(os.path.join(c7, LOG_NAME), "w").write("Time = 1\nEnd\n")
        note("verify_producer_contract() REFUSES a case with no rc file -- the "
             "exact FINDING B condition",
             _fires(verify_producer_contract, c7))

        # ---- 5. campaign(): serial, accumulator carried, smoke row first.
        cs = []
        for i in range(3):
            d = os.path.join(tmp, "camp%d" % i)
            os.makedirs(os.path.join(d, "0"))
            os.makedirs(os.path.join(d, "system"))
            open(os.path.join(d, "system", "controlDict"), "w").write(
                "endTime         1;\n")
            os.makedirs(os.path.join(d, "1"))
            for f in ("U", "p", "k", "omega", "nut", "phi"):
                open(os.path.join(d, "0", f), "w").write("0\n")
            t0 = os.path.getmtime(os.path.join(d, "0", "U"))
            for f in ("U", "p", "k", "omega", "nut", "phi"):
                p = os.path.join(d, "1", f)
                open(p, "w").write("0\n")
                os.utime(p, (t0 + 60, t0 + 60))
            cs.append(d)

        def spy2(argv, cwd, log_path, timeout_s):
            with open(log_path, "w") as fh:
                p = subprocess.Popen(
                    ["/bin/sh", "-c", "printf 'Time = 1\\nExecutionTime = 0.1 "
                     "s\\nSIMPLE solution converged in 1 iterations\\nEnd\\n'"],
                    cwd=cwd, stdout=fh, stderr=subprocess.STDOUT)
                return int(p.wait())

        out = campaign(cs, _spawn=spy2, check_freeze=False)
        note("campaign() ran every registered solve serially",
             out["n_solves"] == 3)
        note("campaign() carries the accumulator in core-minutes at ranks 1",
             out["campaign_core_minutes"] == out["campaign_wall_s"] / 60.0)
        note("campaign() ran the smoke row and it passed on its own output",
             out["smoke_row"] is not None
             and out["smoke_row"].get("rc") == "0")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    width = max(len(n) for n, _, _ in ok)
    for name, passed, detail in ok:
        print(("  %-" + str(width) + "s  %s%s")
              % (name, "PASS" if passed else "FAIL",
                 ("   [" + detail + "]") if detail else ""))
    bad = [n for n, p, _ in ok if not p]
    if bad:
        sys.stderr.write("SELFTEST FAILED: " + "; ".join(bad) + "\n")
        raise SystemExit(1)
    print("rc3_run selftest: %d/%d PASS" % (len(ok), len(ok)))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--campaign" in argv:
        B.refuse_if_unfrozen()
        cases = [a for a in argv if a != "--campaign"]
        if not cases:
            sys.stderr.write("usage: rc3_run.py --campaign <case dir> ...\n")
            return 1
        campaign(cases)
        return 0
    sys.stderr.write("usage: rc3_run.py --selftest | --campaign <case> ...\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
