#!/usr/bin/env python3
"""A1WRT3 -- THE CONTROL DRIVER.  `A1WRT3_SUCCESSOR_DRAFT.md` section 11 item 3.

EVERY CONTROL, BOTH DIRECTIONS, WITH ITS `EXERCISED-*` STATE PRINTED
====================================================================
`CLAUDE.md` rule 3.  Each control here DRIVES THE REAL GATE FUNCTION -- the
same code the run path executes -- over STATIC COMMITTED FIXTURE BYTES, asserts
the verdict is what the registration says it must be, and prints one of

    EXERCISED-PASS    the control ran and the gate answered as registered
    EXERCISED-FAIL    the control ran and the gate DID NOT
    NOT EXERCISED     the control could not be driven at all

**`NOT EXERCISED` IS NEVER COUNTED AS A PASS.**  A control that could not be
driven is a control that proved nothing, and the summary counts it separately
and makes the selftest's rc non-zero.

THE IN-CONTAINER GATES ARE DRIVEN AS THEMSELVES, NOT AS COPIES
==============================================================
`G-WALLTREAT` clause 1 and `G-ENVSEAM` clause 2 live inside `a1wrt3_cmd.sh`, on
the far side of a `docker run`.  Controls `W1a`, `W1b` and `E4` therefore
invoke `a1wrt3_cmd.sh`'s own registered selftest entry points as a subprocess,
so what is exercised IS the code the container runs.  A control that
re-implemented those clauses in this file would be testing a copy -- THE L-493
WRONG-ROUTE SHAPE, arriving inside the control that exists to rule it out.

`E2` GOES FURTHER: it SOURCES `a1wrt3_run_arm.sh` and drives clause 1 against
THE REAL LAUNCHER'S REAL `-e` ARRAY.  If this control typed its own array out,
it would BE the second list section 4.1 rejects.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures"
CMD = HERE / "a1wrt3_cmd.sh"
LAUNCHER = HERE / "a1wrt3_run_arm.sh"

_g = importlib.util.spec_from_file_location("a1wrt3_grade",
                                            str(HERE / "a1wrt3_grade.py"))
G = importlib.util.module_from_spec(_g); _g.loader.exec_module(G)
# ⚠ THE INSTRUMENT MODULE IS TAKEN **THROUGH THE GRADER**, NOT LOADED AGAIN.
# Loading `a1wrt3_instruments.py` a second time by path produces a SECOND module
# object with a SECOND `Refusal` class, and `except I.Refusal` then fails to
# catch a refusal raised through the grader's copy -- so a control that SHOULD
# have scored EXERCISED-PASS scores NOT EXERCISED, and, far worse, a control
# written the other way round could have scored a pass while catching nothing.
# MEASURED in this build: ten controls read NOT EXERCISED for exactly this
# reason before the two module objects were collapsed into one.
I = G.INSTR

RESULTS = []


def control(cid, direction, fixture, expectation):
    """Decorator: run the body, classify, print.  A body that RETURNS a failure
    string is EXERCISED-FAIL; a body that RAISES is NOT EXERCISED, because a
    control that blew up did not exercise anything and must not be scored as a
    pass by the mere absence of an assertion error."""
    def wrap(fn):
        try:
            problem = fn()
            state = "EXERCISED-PASS" if not problem else "EXERCISED-FAIL"
            detail = problem or expectation
        except Exception as exc:                      # noqa: BLE001
            state = "NOT EXERCISED"
            detail = "the control could not be driven: %r" % (exc,)
        RESULTS.append((cid, state))
        print("A1WRT3_CONTROL %-4s %-14s %-8s fixture=%-46s %s"
              % (cid, state, direction, fixture, detail))
        return fn
    return wrap


def run_cmd(*args):
    p = subprocess.run(["bash", str(CMD), *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def real_docker_env(arm="SEAM"):
    """THE REAL LAUNCHER'S REAL ARRAY, read out of `a1wrt3_run_arm.sh`."""
    script = ('source "%s"; build_docker_env %s; printf "%%s\\n" "${DOCKER_ENV[@]}"'
              % (LAUNCHER, arm))
    p = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("sourcing the launcher failed: %s" % (p.stderr,))
    return [ln for ln in p.stdout.splitlines() if ln != ""]


# =========================================================================
# G-WALLTREAT -- the three clauses and the count-pinned presence assertion
# =========================================================================

@control("W0", "pass", "envseam_a1wrt2_producer.py",
         "the REAL producer bytes pass clause 1 and the OK line names them")
def _w0():
    rc, out = run_cmd("--selftest-walltreat", str(FIX / "envseam_a1wrt2_producer.py"))
    if rc != 0:
        return "expected rc 0, got %d: %s" % (rc, out.strip())
    if I.PIN_RUNSCRIPT_MD5 not in out:
        return "the OK line does not carry the pinned md5"
    if "live_false=1 live_true=0" not in out:
        return "the OK line does not report the live counts"
    return None


@control("W1a", "fail", "walltreat_false_deleted.py",
         "the LIVE False line deleted => exit 98")
def _w1a():
    rc, out = run_cmd("--selftest-walltreat", str(FIX / "walltreat_false_deleted.py"))
    if rc != 98:
        return "expected exit 98, got %d" % rc
    if "limb (a)" not in out:
        return "limb (a) did not name itself: %s" % out.strip()
    return None


@control("W1b", "fail", "walltreat_true_beside_false.py",
         "A LIVE True BESIDE AN UNTOUCHED False => exit 98 -- the limb cmd.sh "
         "COULD NOT HAVE PASSED")
def _w1b():
    rc, out = run_cmd("--selftest-walltreat",
                      str(FIX / "walltreat_true_beside_false.py"))
    if rc != 98:
        return "expected exit 98, got %d -- clause 1 is a substring test, not a "\
               "configuration assertion" % rc
    if "limb (b)" not in out:
        return "limb (b) did not name itself: %s" % out.strip()
    # AND THE PLANTED CONTROL IS SHOWN ABLE TO SEE A NON-ZERO: the SAME fixture
    # with the True line removed must PASS, or limb (b) is refusing for some
    # other reason and this control proves nothing (`CLAUDE.md` rule 3).
    rc2, _ = run_cmd("--selftest-walltreat", str(FIX / "envseam_a1wrt2_producer.py"))
    if rc2 != 0:
        return "the un-planted control does not pass, so the refusal above is "\
               "not attributable to the plant"
    return None


@control("W1c", "fail", "container_ok_wrong_md5.log",
         "one byte changed => the md5 limb refuses host-side, though the "
         "in-container config limbs still pass")
def _w1c():
    # The config is intact, so clause 1 PASSES inside the container...
    rc, out = run_cmd("--selftest-walltreat",
                      str(FIX / "walltreat_one_byte_changed.py"))
    if rc != 0:
        return "the mutated fixture's CONFIG should still be valid; got rc %d" % rc
    # ...and the HOST side is where the identity limb bites.
    v, got, note = I.gate_walltreat_presence(str(FIX / "container_ok_wrong_md5.log"))
    if v != "GATE FAIL":
        return "expected GATE FAIL on the md5 limb, got %s" % v
    if got == I.PIN_RUNSCRIPT_MD5:
        return "the fixture's md5 equals the pin, so nothing was tested"
    return None


@control("W1d", "fail", "container_ok_no_md5.log",
         "an OK line with NO md5 field => GATE FAIL, never a silent pass")
def _w1d():
    v, _, _ = I.gate_walltreat_presence(str(FIX / "container_ok_no_md5.log"))
    return None if v == "GATE FAIL" else "expected GATE FAIL, got %s" % v


@control("W2a", "KNOWN-POSITIVE", "walltreat_bc_present.log",
         "REAL A1WRT U1 bytes: clause 2 counts exactly 1 BCType line => PASS")
def _w2a():
    v, n, _ = I.gate_walltreat_clause2(str(FIX / "walltreat_bc_present.log"))
    if v != "PASS":
        return "expected PASS, got %s" % v
    if n != 1:
        return "expected count 1 on the real log, got %d" % n
    return None


@control("W2b", "fail", "walltreat_bc_stripped.log",
         "the BC line stripped => count 0 => GATE FAIL")
def _w2b():
    v, n, _ = I.gate_walltreat_clause2(str(FIX / "walltreat_bc_stripped.log"))
    if v != "GATE FAIL" or n != 0:
        return "expected GATE FAIL at count 0, got %s at %d" % (v, n)
    return None


@control("W2c", "fail", "(absent path)",
         "an UNREADABLE log REFUSES; it never reads as count 0")
def _w2c():
    try:
        I.gate_walltreat_clause2(str(FIX / "no_such_log_at_all.log"))
    except I.Refusal:
        return None
    return "an absent log did not refuse -- a zero from a reader that could not "\
           "see is not evidence"


@control("W3a", "fail", "walltreat_spalding.log",
         "a Spalding wall-function line => clause 3 REFUSES at exit 2")
def _w3a():
    try:
        I.gate_walltreat_clause3(str(FIX / "walltreat_spalding.log"))
    except I.Refusal as r:
        return None if r.code == 2 else "refused with code %d, expected 2" % r.code
    return "clause 3 did not refuse over a planted Spalding line"


@control("W3b", "pass", "walltreat_bc_present.log",
         "the same reader over the clean log does NOT refuse")
def _w3b():
    v, _, _ = I.gate_walltreat_clause3(str(FIX / "walltreat_bc_present.log"))
    return None if v == "PASS" else "expected PASS, got %s" % v


@control("W4a", "fail", "container_ok_absent.log",
         "the OK line DELETED => GATE FAIL reported as *the guard did not run*")
def _w4a():
    v, _, note = I.gate_walltreat_presence(str(FIX / "container_ok_absent.log"))
    if v != "GATE FAIL":
        return "expected GATE FAIL, got %s" % v
    if "DID NOT RUN" not in note:
        return "the finding was not reported as *the guard did not run*"
    return None


@control("W4b", "fail", "container_ok_duplicated.log",
         "the OK line DUPLICATED => count 2 => GATE FAIL. L-493: PRESENCE IS "
         "NOT ENOUGH, THE COUNT IS PINNED")
def _w4b():
    v, _, note = I.gate_walltreat_presence(str(FIX / "container_ok_duplicated.log"))
    if v != "GATE FAIL":
        return "expected GATE FAIL at count 2, got %s -- the assertion is on "\
               "PRESENCE and can be satisfied by the wrong route" % v
    if "occurs 2 times" not in note:
        return "the finding did not state the observed count"
    return None


@control("W4c", "pass", "container_ok_single.log",
         "exactly one OK line carrying the pinned md5 => PASS")
def _w4c():
    v, got, _ = I.gate_walltreat_presence(str(FIX / "container_ok_single.log"))
    if v != "PASS":
        return "expected PASS, got %s" % v
    if got != I.PIN_RUNSCRIPT_MD5:
        return "the passing route did not assert the pinned md5"
    return None


# =========================================================================
# G-ENVSEAM
# =========================================================================
A1WRT2_SUPPLIED = ["-e", "OMP_NUM_THREADS=1"]
E1_EXPECTED = {"AOA_ALPHA0", "AOA_ALPHAS", "AOA_MODE", "AOA_POINTS_JSON"}


@control("E1", "KNOWN-POSITIVE", "envseam_a1wrt2_producer.py",
         "TONIGHT'S CRASH, ON REAL BYTES, AT ZERO COMPUTE: A1WRT2's exact "
         "configuration => BLOCKED NAMING ALL FOUR")
def _e1():
    v, missing, notes = I.gate_envseam_clause1(
        str(FIX / "envseam_a1wrt2_producer.py"), A1WRT2_SUPPLIED, None)
    if v != "BLOCKED":
        return "expected BLOCKED, got %s" % v
    # ⚠ ALL FOUR.  NAMING ONE IS NOT A PASS.  A successor that "fixes" this by
    # adding a single `-e` reproduces the defect, and this assertion is what
    # stops that from being scored as a repair.
    if len(missing) != 4:
        return "the gate named %d name(s) %s -- the registered known-positive "\
               "is FOUR, and naming one is not a pass" % (len(missing), missing)
    if set(missing) != E1_EXPECTED:
        return "named %s, expected exactly %s" % (sorted(missing),
                                                  sorted(E1_EXPECTED))
    # The four are the four measured at runScript.py:51, :285, :286, :287.
    lines = {n.split()[1]: n for n in notes if n.strip().startswith("FATAL")}
    if len(lines) != 4:
        return "the gate reported %d fatal read line(s), expected 4" % len(lines)
    return None


@control("E1b", "fail", "envseam_a1wrt2_producer.py",
         "A SINGLE `-e` ADDED IS NOT A REPAIR: supplying only AOA_ALPHA0 still "
         "BLOCKS, naming the remaining three")
def _e1b():
    v, missing, _ = I.gate_envseam_clause1(
        str(FIX / "envseam_a1wrt2_producer.py"),
        A1WRT2_SUPPLIED + ["-e", "AOA_ALPHA0=12"], None)
    if v != "BLOCKED":
        return "a single -e was accepted as a repair; got %s" % v
    if len(missing) != 3:
        return "expected 3 remaining, got %d (%s)" % (len(missing), missing)
    return None


@control("E2", "pass", "the REAL launcher array + the REAL cmd.sh",
         "the repaired A1WRT3 configuration => CLEAN, AND IT PRINTS THE SET IT "
         "COMPARED AGAINST, so its silence is not its evidence")
def _e2():
    env = real_docker_env("SEAM")
    if "-e" not in env:
        return "the launcher's array did not come back as an -e array: %r" % env
    v, missing, notes = I.gate_envseam_clause1(
        str(FIX / "envseam_a1wrt2_producer.py"), env, str(CMD))
    if v != "PASS":
        return "expected PASS, got %s (missing %s)" % (v, missing)
    if not any("the set compared against was" in n for n in notes):
        return "the gate passed WITHOUT printing the set it compared against"
    # AND THE TRANSLATION HALF CAME OUT OF cmd.sh, NOT OUT OF THIS FILE.
    if not any("EXTRACTED FROM THE FILE THAT RUNS" in n for n in notes):
        return "the AOA_* half was not extracted from a1wrt3_cmd.sh"
    return None


@control("E2b", "fail", "a cmd.sh whose translation markers are absent",
         "no registered markers => REFUSE, never a silent empty set")
def _e2b():
    import tempfile
    txt = CMD.read_text().replace(I.XLAT_BEGIN, "x").replace(I.XLAT_END, "y")
    with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as fh:
        fh.write(txt); p = fh.name
    try:
        I.translation_names(p)
    except I.Refusal:
        return None
    return "a cmd.sh with no translation markers did not refuse"


@control("E3", "fail", "envseam_fifth_fatal.py",
         "a FIFTH fatal read the translation does not supply => BLOCKED naming "
         "it -- THE GATE IS NOT HARD-CODED TO FOUR")
def _e3():
    env = real_docker_env("SEAM")
    v, missing, _ = I.gate_envseam_clause1(
        str(FIX / "envseam_fifth_fatal.py"), env, str(CMD))
    if v != "BLOCKED":
        return "expected BLOCKED, got %s" % v
    if missing != ["AOA_FIFTH_NAME"]:
        return "expected exactly ['AOA_FIFTH_NAME'], got %s" % missing
    return None


@control("E4", "fail", "a1wrt3_cmd.sh --selftest-envseam-c2",
         "clause 2 with AOA_ALPHA0 EMPTY => exit 94. AN EMPTY VALUE IS NOT A "
         "PRESENT VALUE")
def _e4():
    rc, out = run_cmd("--selftest-envseam-c2", "AOA_MODE=CONTINUED",
                      "AOA_ALPHAS=12", "AOA_POINTS_JSON=/mnt/out/points.json",
                      "AOA_ALPHA0=", "AOA_LEDGER=/mnt/out/LEDGER.tsv",
                      "A1WR_PRIMAL_TOL=1.0e-8")
    if rc != 94:
        return "expected exit 94, got %d: %s" % (rc, out.strip())
    if "AOA_ALPHA0 is EMPTY" not in out:
        return "clause 2 did not name the empty variable"
    # Shown able to see a non-zero: the same six with AOA_ALPHA0 populated pass.
    rc2, _ = run_cmd("--selftest-envseam-c2", "AOA_MODE=CONTINUED",
                     "AOA_ALPHAS=12", "AOA_POINTS_JSON=/mnt/out/points.json",
                     "AOA_ALPHA0=12", "AOA_LEDGER=/mnt/out/LEDGER.tsv",
                     "A1WR_PRIMAL_TOL=1.0e-8")
    if rc2 != 0:
        return "the un-planted control does not pass (rc %d), so the refusal "\
               "above is not attributable to the plant" % rc2
    return None


@control("E4b", "fail", "a1wrt3_cmd.sh --selftest-envseam-c2 (no pairs)",
         "a clause that CHECKED NOTHING is not a clause that passed => exit 94")
def _e4b():
    rc, out = run_cmd("--selftest-envseam-c2")
    if rc != 94:
        return "expected exit 94, got %d" % rc
    if "NOTHING WAS CHECKED" not in out:
        return "the empty-input case did not name itself"
    return None


@control("E5", "FALSE-POSITIVE", "envseam_all_defaulted.py",
         "a producer whose only reads are .get(...) => CLEAN, and the control "
         "asserts it DOES NOT BLOCK. 31 of 37 entry scripts in this family "
         "read nothing fatal; a gate that blocked them would be useless")
def _e5():
    v, missing, notes = I.gate_envseam_clause1(
        str(FIX / "envseam_all_defaulted.py"), A1WRT2_SUPPLIED, None)
    if v != "PASS":
        return "THE FALSE-POSITIVE DIRECTION FAILED: got %s over a producer "\
               "with no fatal reads (missing %s)" % (v, missing)
    if not any("reads 0 FATAL" in n for n in notes):
        return "the gate did not report zero fatal reads on the defaulted fixture"
    # And the defaulted names were SEEN, not merely unclassified into silence.
    if not any("DEFAULTED name(s)" in n and "AOA_ALPHA0" in n for n in notes):
        return "the defaulted reads were not enumerated -- a reader that saw "\
               "nothing is indistinguishable from one that saw only .get()"
    return None


@control("E6", "fail", "a bare pass-through '-e NAME'",
         "the bare form REFUSES: it makes the supplied set depend on the host's "
         "ambient environment, which the manifest cannot record")
def _e6():
    try:
        I.supplied_from_docker_env(["-e", "AOA_ALPHA0"])
    except I.Refusal:
        return None
    return "the bare pass-through form was accepted"


@control("E7", "fail", "an unrecognised token in the -e array",
         "an unrecognised token REFUSES; skipping one would silently shrink the "
         "supplied set")
def _e7():
    try:
        I.supplied_from_docker_env(["--memory=8g", "-e", "OMP_NUM_THREADS=1"])
    except I.Refusal:
        return None
    return "an unrecognised token was silently skipped"


@control("E8", "fail", "a producer with a NON-CONSTANT os.environ key",
         "an unresolvable subscript => BLOCKED; the gate will not report clean "
         "over what it cannot enumerate")
def _e8():
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write("import os\nk = 'AOA_' + 'MODE'\nv = os.environ[k]\n")
        p = fh.name
    v, _, _ = I.gate_envseam_clause1(p, A1WRT2_SUPPLIED, None)
    return None if v == "BLOCKED" else "expected BLOCKED, got %s" % v


@control("E9", "pass", "os.environ['X'] = 'y' (a WRITE)",
         "a WRITE is not a READ and must not block a launcher that is already "
         "correct")
def _e9():
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write("import os\nos.environ['AOA_MODE'] = 'CONTINUED'\n"); p = fh.name
    v, missing, _ = I.gate_envseam_clause1(p, A1WRT2_SUPPLIED, None)
    return None if v == "PASS" else "a write was counted as a fatal read (%s)" % missing


# =========================================================================
# F-SEAM -- THE REGISTERED TRIVIAL BASELINE (draft section 9)
# =========================================================================
COLD_CL, COLD_CD = 1.183635361576276, 0.03075803313291197
CONT_CL, CONT_CD = 1.19079592024, 0.030665481166


@control("FS1", "ARITHMETIC", "a1wr_alpha12_reference.tsv:4000 + STAGE12 idx=12",
         "the section 9.1 arithmetic RECOMPUTED, with the inequality written out")
def _fs1():
    rel_cl = abs(COLD_CL - CONT_CL) / CONT_CL
    rel_cd = abs(COLD_CD - CONT_CD) / CONT_CD
    print("    F-SEAM arithmetic  |%.13f - %.11f| / %.11f = %.6e  >  %.1e  "
          "=> %.3fx the bar => THE TRIVIAL BASELINE FAILS G-SEAM"
          % (COLD_CL, CONT_CL, CONT_CL, rel_cl, G.SEAM_BAND_REL,
             rel_cl / G.SEAM_BAND_REL))
    print("    F-SEAM CD limb, DISCLOSED AS THE WEAKER OF THE TWO: %.6e > %.1e "
          "=> %.3fx" % (rel_cd, G.SEAM_BAND_REL, rel_cd / G.SEAM_BAND_REL))
    if abs(rel_cl - 6.013254e-03) > 1e-8:
        return "the registered CL figure 6.013254e-03 does not reproduce (%.6e)" % rel_cl
    if abs(rel_cd - 3.018116e-03) > 1e-8:
        return "the registered CD figure 3.018116e-03 does not reproduce (%.6e)" % rel_cd
    if not (rel_cl > G.SEAM_BAND_REL and rel_cd > G.SEAM_BAND_REL):
        return "the baseline does not exceed the bar it names"
    return None


@control("FS2", "fail", "fseam_trivial_baseline_cold_vs_continued.log",
         "THE NAMED GATE, DRIVEN: G-SEAM against the CONTINUED terminal state "
         "while its reference is the COLD one => GATE FAIL")
def _fs2():
    v, notes = G.g_seam(str(FIX / "fseam_trivial_baseline_cold_vs_continued.log"))
    if v != "GATE FAIL":
        return "G-SEAM returned %s over the deliberately-wrong START. THE "\
               "WITHDRAWAL CLAUSE BITES: G-SEAM is not measuring restart "\
               "fidelity and its verdict on the real SEAM arm is WITHDRAWN." % v
    # DISCLOSURE, read as arithmetic and not as a summary: the gate divides by
    # its own REFERENCE, section 9.1 divides by the CONTINUED value.  Both
    # exceed the bar by ~6x; the two denominators are named rather than blurred.
    print("    %s" % notes[0])
    return None


@control("FS3", "pass", "fseam_pass_direction.log",
         "the SAME gate over a state that DOES reproduce the reference => PASS. "
         "Without this limb the failing direction proves only that the gate "
         "always fails")
def _fs3():
    v, _ = G.g_seam(str(FIX / "fseam_pass_direction.log"))
    return None if v == "PASS" else "expected PASS, got %s" % v


@control("FS4", "fail", "(a log with no AOA_POINT_VALUES line)",
         "F-SEAM's THIRD READING: a missing statistic reads UNRESOLVED, not PASS")
def _fs4():
    v, notes = G.g_seam(str(FIX / "seamtime_branch_C_crash.log"))
    if v != "NOT A RESULT":
        return "expected NOT A RESULT, got %s" % v
    if "UNRESOLVED" not in notes[0]:
        return "the missing statistic was not labelled UNRESOLVED"
    return None


# =========================================================================
# P-SEAMTIME3 -- FOUR BRANCHES AND THE REFUSING CATCH-ALL
# =========================================================================
@control("PS-A", "pass", "fseam_pass_direction.log",
         "first=4001 last=4200 => branch A, the restart LOADED THE STATE")
def _psa():
    b, s, g, _ = G.p_seamtime3(str(FIX / "fseam_pass_direction.log"), 0)
    return None if (b, s, g) == ("A", "HIT", "PASS") else "got %s/%s/%s" % (b, s, g)


@control("PS-B", "fail", "seamtime_branch_B_reset.log",
         "first=1 => branch B, the producer RESETS on a latestTime start")
def _psb():
    b, s, g, _ = G.p_seamtime3(str(FIX / "seamtime_branch_B_reset.log"), 0)
    return None if (b, g) == ("B", "GATE FAIL") else "got %s/%s/%s" % (b, s, g)


@control("PS-C", "fail", "seamtime_branch_C_crash.log",
         "anchored_count=0 => branch C, UNRESOLVED. THIS SAYS NOTHING ABOUT "
         "`startFrom latestTime`")
def _psc():
    b, s, g, note = G.p_seamtime3(str(FIX / "seamtime_branch_C_crash.log"), 1)
    if (b, s, g) != ("C", "UNRESOLVED", "NOT A RESULT"):
        return "got %s/%s/%s" % (b, s, g)
    if "NOTHING ABOUT" not in note:
        return "branch C did not disclaim what it cannot say"
    return None


@control("PS-D", "fail", "seamtime_branch_D_truncated.log",
         "first=4001 last!=4200 => branch D, A REAL RESULT ABOUT THE SEAM, NOT "
         "COLLAPSED INTO C")
def _psd():
    b, s, g, _ = G.p_seamtime3(str(FIX / "seamtime_branch_D_truncated.log"), 0)
    return None if (b, g) == ("D", "GATE FAIL") else "got %s/%s/%s" % (b, s, g)


@control("PS-E", "fail", "seamtime_branch_E_unclassified.log",
         "an outcome in NONE of the registered branches => UNCLASSIFIED and "
         "NOT A RESULT. **BRANCH E IS THE POINT OF THE TABLE, AND IT FAILS.**")
def _pse():
    b, s, g, note = G.p_seamtime3(str(FIX / "seamtime_branch_E_unclassified.log"), 0)
    if (b, s, g) != ("E", "UNCLASSIFIED", "NOT A RESULT"):
        return "got %s/%s/%s -- a catch-all that PASSES reproduces the defect "\
               "one level up" % (b, s, g)
    if "anchored_count=2" not in note:
        return "the catch-all did not print the observed tuple"
    return None


# =========================================================================
# G-FREEZE -- SECTION 11 ITEM 5, THE `cmd.sh` PIN
# =========================================================================
def _base_manifest():
    return {
        "image_digest": G.PIN_IMG_DIGEST,
        "libidwarp_md5": G.PIN_IDWARP_MD5,
        "instruments": dict(G.PIN_INSTRUMENTS),
    }


@control("Q-FREEZE-1", "pass", "(a manifest matching every pin)",
         "all THREE instrument md5s exact => PASS")
def _qf1():
    v, notes = G.g_img_freeze(_base_manifest())
    if v != "PASS":
        return "expected PASS, got %s" % v
    if not any("including cmd.sh" in n for n in notes):
        return "G-FREEZE passed without naming cmd.sh"
    return None


@control("Q-FREEZE-2", "fail", "(cmd.sh md5 perturbed by one hex digit)",
         "**THE SECTION 11 ITEM 5 CONTROL**: a post-freeze edit to the restored "
         "cmd.sh is CAUGHT. A1WRT2 recorded its launcher's md5 and never gated "
         "it, so this edit would have been silent.")
def _qf2():
    m = _base_manifest()
    orig = m["instruments"]["cmd.sh"]
    m["instruments"]["cmd.sh"] = ("0" if orig[0] != "0" else "1") + orig[1:]
    try:
        G.g_img_freeze(m)
    except I.Refusal as r:
        if r.code != 4:
            return "refused with code %d, expected 4" % r.code
        if "cmd.sh" not in str(r):
            return "the refusal did not name cmd.sh"
        return None
    return "A PERTURBED cmd.sh MD5 PASSED G-FREEZE -- the most load-bearing "\
           "file in this item is recorded but not gated"


@control("Q-FREEZE-3", "fail", "(cmd.sh absent from the manifest)",
         "a GATED instrument MISSING from the manifest => REFUSE. A missing "
         "observation is not an agreement")
def _qf3():
    m = _base_manifest()
    del m["instruments"]["cmd.sh"]
    try:
        G.g_img_freeze(m)
    except I.Refusal:
        return None
    return "a manifest with no cmd.sh row passed G-FREEZE"


@control("Q-FREEZE-4", "fail", "(a manifest recording an UNGATED instrument)",
         "the RECORDED-BUT-UNGATED SHAPE IS ITSELF A REFUSAL, so it cannot "
         "recur by omission")
def _qf4():
    m = _base_manifest()
    m["instruments"]["stage.py"] = "0" * 32
    try:
        G.g_img_freeze(m)
    except I.Refusal as r:
        return None if "does not GATE" in str(r) else "refused for the wrong reason"
    return "an instrument recorded but not gated passed G-FREEZE"


# =========================================================================
# Q-COMPOSE -- the composer
# =========================================================================
def _all_pass():
    return {g: "PASS" for g in G.HARD_GATES + G.SOFT_GATES}


@control("Q-COMPOSE-1", "fail", "(NOT A RESULT planted into one HARD gate)",
         "the composed token is NOT A RESULT and NOT GATE REACHED -- the "
         "D19M-COMPOSE-DEF-1 repair")
def _qc1():
    bad = []
    for g in G.HARD_GATES:
        v = _all_pass(); v[g] = "NOT A RESULT"
        raw, final = G.compose_item(v)
        if final != "NOT A RESULT":
            bad.append((g, final))
    return None if not bad else "hard gate(s) whose NOT A RESULT did not "\
                                "propagate: %s" % bad


@control("Q-COMPOSE-2", "fail", "(GATE FAIL planted into EVERY gate in turn)",
         "EVERY hard AND soft list is tested for BOTH GATE FAIL and NOT A RESULT")
def _qc2():
    bad = []
    for g in G.HARD_GATES + G.SOFT_GATES:
        v = _all_pass(); v[g] = "GATE FAIL"
        _, final = G.compose_item(v)
        if final != "GATE FAIL":
            bad.append((g, final))
    return None if not bad else "gate(s) whose GATE FAIL did not propagate: %s" % bad


@control("Q-COMPOSE-3", "pass", "(every gate PASS)",
         "PASS IS UNREACHABLE BY CONSTRUCTION: raw=PASS caps to GATE REACHED, "
         "and BOTH are printed so the cap is visible")
def _qc3():
    raw, final = G.compose_item(_all_pass())
    if raw != "PASS":
        return "expected raw PASS, got %s" % raw
    if final != "GATE REACHED":
        return "the L3 ceiling did not bind: %s" % final
    return None


@control("Q-COMPOSE-4", "fail", "(one gate with NO reading at all)",
         "the composer REFUSES over a missing gate. A GATE WITH NO READING IS "
         "NOT A GATE THAT PASSED")
def _qc4():
    v = _all_pass(); del v["G-ENVSEAM"]
    try:
        G.compose_item(v)
    except I.Refusal:
        return None
    return "the composer composed a verdict while blind to G-ENVSEAM"


@control("Q-TRAP", "fail", "(a grader run that reaches no composer)",
         "NO ITEM VERDICT BY CONSTRUCTION IS FORBIDDEN: the EXIT trap prints "
         "PENDING with its last checkpoint and exits 12")
def _qtrap():
    p = subprocess.run(
        [sys.executable, str(HERE / "a1wrt3_grade.py"), "--grade",
         "/home/ubuntu/certonomous-runs/A1WRT3"],
        capture_output=True, text=True)
    if "A1WRT3_VERDICT PENDING" not in p.stdout:
        return "no PENDING verdict was emitted (rc %d): %s"\
               % (p.returncode, (p.stdout + p.stderr).strip()[:300])
    if p.returncode != 12:
        return "expected rc 12 from the trap, got %d" % p.returncode
    if "last checkpoint" not in p.stdout:
        return "the trap did not name its last checkpoint"
    return None


# =========================================================================
# G-FIXTURE, G-STALL, G-NOGRAD, G-YPLUS
# =========================================================================
@control("Q-FIXTURE-1", "pass", "fixtures/*",
         "every fixture is static committed bytes and NONE resolves inside "
         "this item's run root (the L-435 repair, unweakened)")
def _qfx1():
    v, _ = G.g_fixture(sorted(p for p in FIX.glob("*") if p.is_file()))
    return None if v == "PASS" else "G-FIXTURE returned %s" % v


@control("Q-FIXTURE-2", "fail", "(a path inside /home/ubuntu/certonomous-runs/A1WRT3)",
         "a fixture inside the run root REFUSES")
def _qfx2():
    try:
        G.g_fixture([Path(G.RUN_ROOT) / "SEAM" / "out" / "sweep.log"])
    except I.Refusal:
        return None
    return "a fixture inside the item's own run root was accepted"


@control("Q-STALL-1", "fail", "(text binding 'stall' to an angle)",
         "G-STALL REFUSES. THE TAIL IS EXACTLY WHERE THAT TEMPTATION LIVES")
def _qs1():
    try:
        G.g_stall([("planted", "the wing stalls at 15 degrees")])
    except I.Refusal:
        return None
    return "a stall angle passed G-STALL"


@control("Q-STALL-2", "pass", "walltreat_bc_present.log",
         "the REAL solver log does NOT trip G-STALL, so the refusal above is "
         "attributable to the plant and not to the reader")
def _qs2():
    v, _ = G.g_stall([("A1WRT U1 sweep.log",
                       (FIX / "walltreat_bc_present.log").read_text(errors="replace"))])
    return None if v == "PASS" else "the clean log tripped G-STALL"


@control("Q-NOGRAD-1", "fail", "(a producer containing compute_totals)",
         "G-NOGRAD refuses -- this item computes no gradient")
def _qng1():
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write("prob.compute_totals()\n"); p = fh.name
    try:
        G.g_nograd(p)
    except I.Refusal:
        return None
    return "compute_totals passed G-NOGRAD"


@control("Q-NOGRAD-2", "pass", "(a producer with no compute_totals)",
         "the clean direction passes, so Q-NOGRAD-1's refusal is attributable "
         "to the plant and not to the reader")
def _qng2():
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write("prob.run_model()\n"); p = fh.name
    v, _ = G.g_nograd(p)
    return None if v == "PASS" else "got %s" % v


@control("Q-NOGRAD-3", "FREEZE-BLOCKER", "envseam_a1wrt2_producer.py (THE PIN)",
         "**MEASURED, AND IT IS A FINDING, NOT A PASS.** The gate as section 9 "
         "words it REFUSES THE PINNED PRODUCER: `compute_totals` appears 3x "
         "(:40 a comment, :257 a task-name comparison, :260 the only call, in a "
         "branch `-task sweep` never enters). The item cannot reach a verdict "
         "until the dafoam-supervisor amends the wording pre-freeze.")
def _qng3():
    try:
        G.g_nograd(str(FIX / "envseam_a1wrt2_producer.py"))
    except I.Refusal as r:
        if "FREEZE BLOCKER" not in str(r):
            return "the refusal did not identify itself as a freeze blocker"
        if "[40, 257, 260]" not in str(r):
            return "the refusal did not name the three lines: %s" % r
        return None
    return "G-NOGRAD passed the pinned producer -- then the gate is not the one "\
           "section 9 registers and the discrepancy is in the other direction"


@control("Q-YPLUS-1", "fail", "(a y+ log reading min=0 max=0)",
         "**THE BARE `postProcess` BLIND READER'S SIGNATURE REFUSES.** C16's "
         "clause is dropped; ITS LESSON IS NOT")
def _qy1():
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False) as fh:
        fh.write("patch wing y+ : min = 0, max = 0\n"); p = fh.name
    try:
        G.g_yplus(p)
    except I.Refusal as r:
        return None if "BLIND READER" in str(r) else "refused for the wrong reason"
    return "an all-zero y+ field passed G-YPLUS -- a planted zero"


@control("Q-YPLUS-2", "pass", "(a y+ log reading max = 0.0388)",
         "a real wall-resolved reading passes, so Q-YPLUS-1's refusal is "
         "attributable to the zero and not to the reader")
def _qy2():
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False) as fh:
        fh.write("patch wing y+ : min = 0.0113, max = 0.03875163378783598\n")
        p = fh.name
    v, _ = G.g_yplus(p)
    return None if v == "PASS" else "got %s" % v


@control("Q-LEDGER-1", "fail", "(an unparseable ledger row)",
         "AN UNPARSEABLE LEDGER REFUSES RATHER THAN ASSUMING ZERO. A zero that "
         "means *could not read* would read as maximum headroom")
def _ql1():
    import tempfile
    d = Path(tempfile.mkdtemp())
    (d / "ledger.txt").write_text("ARM=SEAM something went wrong here\n")
    try:
        G.read_ledger(str(d))
    except I.Refusal:
        return None
    return "an unparseable ledger read as zero spend"


@control("Q-LEDGER-2", "fail", "(spend that projects past the item ceiling)",
         "G-CEILING refuses BEFORE the arm launches. THE TWO CAPS SUMMED ARE "
         "NOT A NEW BUDGET")
def _ql2():
    import tempfile
    d = Path(tempfile.mkdtemp())
    (d / "ledger.txt").write_text(
        "ARM=SEAM ROW=PATCHED rc=0 wall_s=1 ranks=1 core_min=100.0 cap_core_min=10.0\n")
    v, _ = G.g_ceiling(str(d), "TAIL")
    if v != "GATE FAIL":
        return "expected GATE FAIL on the projection, got %s" % v
    v2, _ = G.g_caps(str(d))
    if v2 != "NOT A RESULT":
        return "G-CAPS did not report NOT A RESULT over a 10x overrun (%s)" % v2
    return None


# =========================================================================
# THE MANIFEST -- SECTION 11 ITEM 6.  DRIVEN, NOT ASSERTED.
#
# `write_manifest` is invoked as ITSELF, out of the real launcher, into a
# throwaway run root, and the manifest it produces is then read by the REAL
# `g_envseam`.  A control that inspected the launcher's SOURCE for the right
# words would prove only that the words are there.
# =========================================================================
def _drive_write_manifest():
    import tempfile
    d = Path(tempfile.mkdtemp())
    for name, src in (("runScript.py", FIX / "envseam_a1wrt2_producer.py"),
                      ("cmd.sh", CMD), ("run_arm.sh", LAUNCHER)):
        (d / name).write_bytes(src.read_bytes())
    script = (
        'source "%s"\n'
        'RUN_ROOT="%s"; MANIFEST_PATH="$RUN_ROOT/MANIFEST.json"\n'
        'build_docker_env SEAM\n'
        'write_manifest SEAM "%s" "%s" "$(env_sig)" 2>/dev/null\n'
        % (LAUNCHER, d, G.PIN_IMG_DIGEST, G.PIN_IDWARP_MD5))
    p = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("write_manifest failed: %s" % (p.stdout + p.stderr))
    return d, json.loads((d / "MANIFEST.json").read_text())


@control("M1", "pass", "(the real write_manifest, driven)",
         "**THE MANIFEST DECLARES THE CONTAINER'S ENVIRONMENT**: the -e array, "
         "the names parsed out of it, the AOA_* translation read from cmd.sh, "
         "and the producer's own fatal reads. BOTH SIDES OF THE SEAM.")
def _m1():
    _, m = _drive_write_manifest()
    env = m.get("env_declared")
    if not isinstance(env, dict):
        return "env_declared is %r, not the container-side record" % type(env).__name__
    for k in ("docker_e_array", "container_supplied", "aoa_translation",
              "producer_fatal_reads"):
        if not env.get(k):
            return "env_declared lacks a populated %r" % k
    if sorted(env["producer_fatal_reads"]) != sorted(E1_EXPECTED):
        return "the producer's fatal reads were not recorded: %s" \
               % env["producer_fatal_reads"]
    if set(env["aoa_translation"]) < E1_EXPECTED:
        return "the translation record does not cover the four fatal names: %s" \
               % env["aoa_translation"]
    return None


@control("M2", "fail", "(the A1WRT2 defect shape, searched for)",
         "**THE LAUNCHER'S OWN SHELL VARIABLES ARE ABSENT.** A1WRT2 declared "
         "`A1WRT2_RUN_ROOT`, `A1WRT2_STATUS_DIR` and `BASH_SOURCE` here -- the "
         "wrong side of the boundary, the same blindness as the unbound-variable "
         "guard, in a second instrument.")
def _m2():
    _, m = _drive_write_manifest()
    blob = json.dumps(m["env_declared"])
    offenders = [w for w in ("BASH_SOURCE", "A1WRT3_RUN_ROOT", "A1WRT3_STATUS_DIR",
                             "MANIFEST_PATH", "DAFOAM_LOADER") if w in blob]
    if offenders:
        return "the manifest declares LAUNCHER-side names %s -- the A1WRT2 "\
               "defect has reappeared" % offenders
    return None


@control("M3", "pass", "(the produced manifest, read by the real g_envseam)",
         "the manifest is SUFFICIENT: G-ENVSEAM reconstructs both sides of the "
         "seam from it alone and returns PASS. This was impossible from "
         "A1WRT2's manifest, and the crash is the proof.")
def _m3():
    _, m = _drive_write_manifest()
    v, notes = G.g_envseam(m, None)
    return None if v == "PASS" else "g_envseam returned %s over the manifest" % v


@control("M4", "fail", "(a manifest carrying A1WRT2's env_declared list)",
         "G-ENVSEAM REFUSES a launcher-side env_declared rather than reading it "
         "as an empty seam")
def _m4():
    m = {"env_declared": ["A1WRT3_RUN_ROOT", "A1WRT3_STATUS_DIR", "BASH_SOURCE"]}
    try:
        G.g_envseam(m, None)
    except I.Refusal as r:
        return None if "LAUNCHER" in str(r) else "refused for the wrong reason"
    return "a launcher-side env_declared was accepted"


# =========================================================================
# THE INSTRUMENT TABLE -- SECTION 11 ITEM 4, DRIVEN
# =========================================================================
@control("T1", "pass", "a1wrt3_instrument_table.py",
         "EXISTENCE FIRST AND SEPARATELY, then md5 agreement -- and the cmd.sh "
         "pin in PIN_INSTRUMENTS is proved EQUAL to the file on disk, so the "
         "gate is not pinning a placeholder")
def _t1():
    p = subprocess.run([sys.executable, str(HERE / "a1wrt3_instrument_table.py")],
                       capture_output=True, text=True)
    if p.returncode != 0:
        return "the table failed: %s" % p.stdout.strip()[-400:]
    if "OK       cmd.sh" not in p.stdout:
        return "phase 2 did not report agreement on cmd.sh"
    if G.PIN_INSTRUMENTS["cmd.sh"] != I.md5_of(CMD):
        return "PIN_INSTRUMENTS['cmd.sh'] does not equal a1wrt3_cmd.sh on disk"
    return None


@control("T2", "fail", "(PHASE 1 with a dependency removed)",
         "**PHASE ORDER IS THE POINT**: a missing dependency stops the run "
         "BEFORE md5 agreement is consulted, because agreement over a subset is "
         "not coverage of the set")
def _t2():
    import importlib.util as iu
    s = iu.spec_from_file_location("t", str(HERE / "a1wrt3_instrument_table.py"))
    t = iu.module_from_spec(s); s.loader.exec_module(t)
    refs, _ = t.extract()
    refs["a_file_that_is_not_there.py"] = {"a1wrt3_cmd.sh:1"}
    problems = t.phase1_existence(refs, [])
    return None if problems else "phase 1 passed over an absent dependency"


@control("T3", "fail", "(a stale EXCEPTION)",
         "an exception whose predicate stops holding FAILS phase 1 instead of "
         "hiding a real absence behind it")
def _t3():
    import importlib.util as iu
    s = iu.spec_from_file_location("t", str(HERE / "a1wrt3_instrument_table.py"))
    t = iu.module_from_spec(s); s.loader.exec_module(t)
    # `no_such_log_at_all.log` is excepted ONLY while it is genuinely absent.
    refs = {"no_such_log_at_all.log": {"a1wrt3_selftest.py:1"}}
    saved = t.EXCEPTIONS["no_such_log_at_all.log"]
    t.EXCEPTIONS["no_such_log_at_all.log"] = (saved[0], lambda n, r: False)
    problems = t.phase1_existence(refs, [])
    t.EXCEPTIONS["no_such_log_at_all.log"] = saved
    return None if problems else "a stale exception was honoured"


# =========================================================================
def main():
    print("=" * 78)
    print("A1WRT3 SELFTEST -- every control, both directions, EXERCISED state "
          "printed.\nNOT EXERCISED IS NEVER COUNTED AS A PASS.")
    print("=" * 78)
    ok = sum(1 for _, s in RESULTS if s == "EXERCISED-PASS")
    bad = sum(1 for _, s in RESULTS if s == "EXERCISED-FAIL")
    nx = sum(1 for _, s in RESULTS if s == "NOT EXERCISED")
    print("-" * 78)
    print("A1WRT3_SELFTEST controls=%d EXERCISED-PASS=%d EXERCISED-FAIL=%d "
          "NOT-EXERCISED=%d" % (len(RESULTS), ok, bad, nx))
    if bad or nx:
        print("A1WRT3_SELFTEST rc=1 -- the control set is NOT clean")
        return 1
    print("A1WRT3_SELFTEST rc=0 -- every control exercised and every gate "
          "answered as registered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
