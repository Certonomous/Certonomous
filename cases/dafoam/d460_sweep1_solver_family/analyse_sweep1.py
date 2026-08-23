#!/usr/bin/env python3
"""D460 sweep 1 (solver family) comparator — FROZEN AT THE PRE-REGISTRATION COMMIT.

Grades the four-log comparison registered in PREREGISTRATION.md §5-§7:

    ARM F-SM  forward-AD build, p solved by smoothSolver/GaussSeidel   (new)
    ARM P-SM  plain build,      p solved by smoothSolver/GaussSeidel   (new, the control)
    ARM F-GAMG  = /home/ubuntu/certonomous-runs/P3-a6-n16-ref/s1b.log  (on record, D460 s3)
    ARM P-GAMG  = /home/ubuntu/certonomous-runs/P2-a6-n16/patched.log  (on record, D460 s3)

This script REFUSES (exit 2) rather than degrading. It never writes a verdict it
cannot support, and it never grades a run whose planted controls did not read back.

CLAUDE.md rule 3 (planted-zero control): on EVERY invocation, three known
perturbations are written to a copy of ARM F-SM's log ON DISK, re-read from disk
through the same parser used for grading, and asserted visible. If any plant is
invisible the script exits 2 before grading anything. A zero from a reader not
shown able to see a non-zero is not evidence.

Exit codes:  0 graded (verdict on stdout)   2 refused   3 usage error
"""

import os
import re
import sys
import shutil
import tempfile

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS.  Registered in PREREGISTRATION.md and not changed after the
# pre-registration commit.  Values are the PRINTED STRINGS from the two logs on
# record, because bit-identity is asserted on the printed token, not on a float
# that has been through a parse/format round trip.
# ---------------------------------------------------------------------------

PLANT_REL = 1.234e-03           # relative perturbation planted into he finalRes
ENDTIME = 10                    # registered endTime for both new arms
RATIO_BAND = 2.0                # registered band on the continuity amplification
FIELDS_REQUIRED = ("T", "U", "p", "nut", "nuTilda", "alphat")

REF = {
    "P-GAMG": {
        "log": "/home/ubuntu/certonomous-runs/P2-a6-n16/patched.log",
        "U0_finalRes": "0.07283048716260687",
        "U1_finalRes": "0.003381492464613624",
        "U2_finalRes": "0.07283327010584476",
        "he_initRes":  "0.9999999999746546",
        "he_finalRes": "0.06128002514528321",
        "p_finalRes":  "0.08186984767127925",
        "p_nIters":    "7",
        "cumulative":  "-0.00504349133910657",
        "CD":          "0.02122521539888314",
    },
    "F-GAMG": {
        "log": "/home/ubuntu/certonomous-runs/P3-a6-n16-ref/s1b.log",
        "U0_finalRes": "0.07283048716260687",
        "U1_finalRes": "0.003381492464613624",
        "U2_finalRes": "0.07283327010584476",
        "he_initRes":  "0.9999999999746546",
        "he_finalRes": "0.06128001402295498",
        "p_finalRes":  "0.07694766099874849",
        "p_nIters":    "5",
        "cumulative":  "-0.05058272456310364",
        "CD":          "0.01835565832247826",
    },
}

# The quantities that MUST be bit-identical between an arm and its own-build GAMG
# reference at Time = 1, because nothing upstream of them in the SIMPLE loop
# depends on the pressure solver (gate G0, PREREGISTRATION.md s6).
G0_KEYS = ("U0_finalRes", "U1_finalRes", "U2_finalRes", "he_initRes", "he_finalRes")


def refuse(msg):
    print("REFUSED: %s" % msg)
    sys.exit(2)


# ---------------------------------------------------------------------------
# Parser.  One function, used for grading AND for reading the plants back, so a
# plant that the parser cannot see is a plant the grader cannot see.
# ---------------------------------------------------------------------------

RE_TIME = re.compile(r"^Time = (\d+)\s*$", re.M)
RE_EQN = re.compile(
    r"^(?P<name>U0|U1|U2|he|p|nuTilda) initRes: (?P<init>\S+) finalRes: (?P<fin>\S+) nIters: (?P<it>\d+)",
    re.M)
RE_CUM = re.compile(r"^\s*cumulative = (?P<v>\S+)\s*$", re.M)
RE_CD = re.compile(r"^CD: (?P<v>\S+) final: (?P<f>\S+)", re.M)
RE_EXEC = re.compile(r"^ExecutionTime = ", re.M)
# NOTE: written as an explicit non-letter boundary, NOT as \bn?an\b -- that form
# matches the English word "an" and would report NaN in every log ever written.
RE_NAN = re.compile(r"(?<![A-Za-z0-9_])-?nan(?![A-Za-z0-9_])", re.I)


def read_log(path):
    if not os.path.isfile(path):
        refuse("log not found on disk: %s" % path)
    with open(path, "rb") as fh:
        return fh.read().decode("utf-8", "replace")


def parse(text, path_for_msg="<text>"):
    """Extract the registered observables. Refuses on anything missing."""
    starts = [(m.start(), int(m.group(1))) for m in RE_TIME.finditer(text)]
    if not starts:
        refuse("no 'Time = N' block in %s -- nothing to grade" % path_for_msg)

    # --- the Time = 1 block: from its header to the next Time header ---
    first = None
    for i, (pos, t) in enumerate(starts):
        if t == 1:
            end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
            first = text[pos:end]
            break
    if first is None:
        refuse("no 'Time = 1' block in %s" % path_for_msg)

    out = {}
    for m in RE_EQN.finditer(first):
        n = m.group("name")
        out["%s_initRes" % n] = m.group("init")
        out["%s_finalRes" % n] = m.group("fin")
        out["%s_nIters" % n] = m.group("it")

    mc = RE_CUM.search(first)
    if not mc:
        refuse("no cumulative continuity line in the Time = 1 block of %s" % path_for_msg)
    out["cumulative"] = mc.group("v")

    md = RE_CD.search(first)
    if md:
        out["CD"] = md.group("v")

    for k in G0_KEYS:
        if k not in out:
            refuse("required Time = 1 quantity %s absent from %s" % (k, path_for_msg))

    out["_last_time"] = starts[-1][1]
    out["_n_time_blocks"] = len(starts)
    out["_n_exec"] = len(RE_EXEC.findall(text))
    out["_has_end"] = re.search(r"^End\s*$", text, re.M) is not None
    out["_nan"] = RE_NAN.search(text) is not None
    return out


# ---------------------------------------------------------------------------
# Planted controls (CLAUDE.md rule 3).  Written to disk, re-read from disk.
# ---------------------------------------------------------------------------

def planted_controls(f_sm_log):
    text = read_log(f_sm_log)
    tmpd = tempfile.mkdtemp(prefix="d460_plant_")
    try:
        # --- plant 0: the NEGATIVE control. An untouched copy must read clean. ---
        p0 = os.path.join(tmpd, "clean.log")
        shutil.copyfile(f_sm_log, p0)
        base = parse(read_log(p0), p0)
        if base["_nan"]:
            print("  plant 0 (clean copy): NaN present in the arm's own log "
                  "-- not a control failure, recorded and carried into grading")

        # --- plant 1: he finalRes perturbed by a known relative amount ---
        try:
            orig = float(base["he_finalRes"])
        except ValueError:
            refuse("he finalRes is not parseable as a float: %r" % base["he_finalRes"])
        planted_val = orig * (1.0 + PLANT_REL)
        p1 = os.path.join(tmpd, "plant_he.log")
        newtext = text.replace(
            "he initRes: %s finalRes: %s" % (base["he_initRes"], base["he_finalRes"]),
            "he initRes: %s finalRes: %.17g" % (base["he_initRes"], planted_val), 1)
        if newtext == text:
            refuse("plant 1 could not be written: the he line was not found for substitution")
        with open(p1, "w") as fh:
            fh.write(newtext)
        got = parse(read_log(p1), p1)
        seen = float(got["he_finalRes"])
        rel = abs(seen - orig) / abs(orig)
        if abs(rel - PLANT_REL) > 0.05 * PLANT_REL:
            refuse("PLANT 1 INVISIBLE: planted a %.4e relative change in he finalRes, "
                   "the reader saw %.4e. The comparator cannot see a non-zero and its "
                   "zeros are not evidence." % (PLANT_REL, rel))
        # and the G0 string test must now FAIL on the planted copy
        if got["he_finalRes"] == base["he_finalRes"]:
            refuse("PLANT 1 INVISIBLE: the planted he finalRes string is identical to the "
                   "original -- the G0 bit-identity test cannot discriminate.")
        print("  plant 1 OK: he finalRes %s -> %s, reader saw rel=%.4e (planted %.4e)"
              % (base["he_finalRes"], got["he_finalRes"], rel, PLANT_REL))

        # --- plant 2: a NaN, to prove the NaN detector is live ---
        p2 = os.path.join(tmpd, "plant_nan.log")
        with open(p2, "w") as fh:
            fh.write(text + "\nU Residual Norm2: (nan -nan nan)\n")
        got2 = parse(read_log(p2), p2)
        if not got2["_nan"]:
            refuse("PLANT 2 INVISIBLE: a literal 'nan' was written into the log on disk and "
                   "the NaN detector did not fire. A 'no NaN' reading would not be evidence.")
        print("  plant 2 OK: planted NaN was seen by the detector")

        # --- plant 3: the continuity value, which carries the registered band ---
        try:
            cum0 = float(base["cumulative"])
        except ValueError:
            refuse("cumulative continuity is not parseable: %r" % base["cumulative"])
        p3 = os.path.join(tmpd, "plant_cum.log")
        newtext3 = text.replace("cumulative = %s" % base["cumulative"],
                                "cumulative = %.17g" % (cum0 * 3.0), 1)
        if newtext3 == text:
            refuse("plant 3 could not be written: the cumulative line was not found")
        with open(p3, "w") as fh:
            fh.write(newtext3)
        got3 = parse(read_log(p3), p3)
        seen3 = float(got3["cumulative"])
        if abs(abs(seen3 / cum0) - 3.0) > 1e-9:
            refuse("PLANT 3 INVISIBLE: planted a 3x change in cumulative continuity, the "
                   "reader saw %.6f x. The registered band cannot be graded." % (seen3 / cum0))
        print("  plant 3 OK: planted 3x continuity change was seen as %.6fx" % (seen3 / cum0))
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)


# ---------------------------------------------------------------------------
# Strict completion (CLAUDE.md rule 4, adapted in PREREGISTRATION.md s6a).
# ---------------------------------------------------------------------------

def completion(arm_dir, log_path, rc, label):
    text = read_log(log_path)
    p = parse(text, log_path)
    clauses = {}
    clauses["rc==0"] = (rc == 0)
    clauses["End line"] = p["_has_end"]
    clauses["last time == endTime"] = (p["_last_time"] == ENDTIME)
    clauses["ExecutionTime count == endTime"] = (p["_n_exec"] == ENDTIME)

    tdir = os.path.join(arm_dir, str(ENDTIME))
    clauses["endTime dir exists"] = os.path.isdir(tdir)
    present, missing = [], []
    if os.path.isdir(tdir):
        have = set()
        for fn in os.listdir(tdir):
            have.add(fn[:-3] if fn.endswith(".gz") else fn)
        for f in FIELDS_REQUIRED:
            (present if f in have else missing).append(f)
    clauses["fields present %s" % (",".join(FIELDS_REQUIRED),)] = (not missing) and os.path.isdir(tdir)

    # age guard: every field at endTime NEWER than the case's own 0/T
    zt = None
    for cand in (os.path.join(arm_dir, "0", "T"), os.path.join(arm_dir, "0", "T.gz")):
        if os.path.isfile(cand):
            zt = cand
            break
    if zt is None:
        clauses["age guard (0/T exists)"] = False
    else:
        t0 = os.path.getmtime(zt)
        ok = os.path.isdir(tdir)
        if ok:
            for fn in os.listdir(tdir):
                fp = os.path.join(tdir, fn)
                if os.path.isfile(fp) and os.path.getmtime(fp) <= t0:
                    ok = False
                    break
        clauses["age guard (every endTime field newer than 0/T)"] = ok

    print("  %s strict completion:" % label)
    for k, v in clauses.items():
        print("     %-52s %s" % (k, "OK" if v else "FAIL"))
    return all(clauses.values()), p


def main():
    if len(sys.argv) != 5:
        print(__doc__)
        print("usage: analyse_sweep1.py <F-SM arm dir> <F-SM rc> <P-SM arm dir> <P-SM rc>")
        sys.exit(3)
    f_dir, f_rc, p_dir, p_rc = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
    f_log = f_dir.rstrip("/") + ".log"
    p_log = p_dir.rstrip("/") + ".log"

    print("=" * 78)
    print("D460 SWEEP 1 (solver family) -- grading against the frozen pre-registration")
    print("=" * 78)

    # 1. the references must still be the files the pre-registration froze
    print("\n[1] reference logs on record")
    refs = {}
    for name, spec in REF.items():
        r = parse(read_log(spec["log"]), spec["log"])
        for k in G0_KEYS + ("cumulative",):
            if r.get(k) != spec[k]:
                refuse("reference %s moved: %s is %r on disk, the pre-registration froze %r. "
                       "The grading path is not the one that was registered."
                       % (name, k, r.get(k), spec[k]))
        refs[name] = r
        print("  %-8s %s  he finalRes %s  cumulative %s  OK"
              % (name, spec["log"], spec["he_finalRes"], spec["cumulative"]))

    # 2. planted controls, before any grading
    print("\n[2] planted controls (CLAUDE.md rule 3) -- written to disk, read back from disk")
    planted_controls(f_log)

    # 3. strict completion
    print("\n[3] strict completion")
    f_done, F = completion(f_dir, f_log, f_rc, "ARM F-SM")
    p_done, P = completion(p_dir, p_log, p_rc, "ARM P-SM")
    if not (f_done and p_done):
        print("\nVERDICT: NOT A RESULT")
        print("REASON: an arm failed the strict completion rule; a run that fails any clause "
              "is not done, and no observable from it is graded.")
        sys.exit(0)

    # 4. gate G0 -- bit-identity upstream of the pressure solve at Time = 1
    print("\n[4] gate G0: quantities upstream of the p solve must be bit-identical to the "
          "same-build GAMG reference")
    g0 = True
    for arm_name, arm, ref_name in (("F-SM", F, "F-GAMG"), ("P-SM", P, "P-GAMG")):
        for k in G0_KEYS:
            same = arm.get(k) == REF[ref_name][k]
            g0 &= same
            print("     %-6s %-14s %-22s vs %-22s %s"
                  % (arm_name, k, arm.get(k), REF[ref_name][k], "OK" if same else "DIFFERS"))
    if not g0:
        print("\nVERDICT: NOT A RESULT")
        print("REASON: G0 failed. A quantity computed BEFORE the pressure solve at iteration 1 "
              "changed when only the pressure solver was changed. The arm is not the registered "
              "one-variable comparison, so nothing downstream of it can be read.")
        sys.exit(0)

    # 5. the observables
    print("\n[5] registered observables at Time = 1, and NaN over the whole run")
    cf, cp = abs(float(F["cumulative"])), abs(float(P["cumulative"]))
    if cp == 0.0:
        refuse("the control arm's cumulative continuity is exactly zero; the registered "
               "ratio is undefined and no band can be graded.")
    ratio = cf / cp
    rg = abs(float(REF["F-GAMG"]["cumulative"])) / abs(float(REF["P-GAMG"]["cumulative"]))
    print("     p finalRes / nIters   F-SM %s / %s      P-SM %s / %s"
          % (F.get("p_finalRes"), F.get("p_nIters"), P.get("p_finalRes"), P.get("p_nIters")))
    print("     cumulative continuity F-SM %s   P-SM %s" % (F["cumulative"], P["cumulative"]))
    print("     ratio r = |cum_F| / |cum_P|  = %.6f      (GAMG pair on record: %.6f)" % (ratio, rg))
    print("     CD                    F-SM %s   P-SM %s" % (F.get("CD"), P.get("CD")))
    print("     NaN anywhere in log   F-SM %s          P-SM %s" % (F["_nan"], P["_nan"]))

    # 6. the registered decision rule
    print("\n[6] decision rule as frozen in PREREGISTRATION.md s7")
    if P["_nan"]:
        print("\nVERDICT: NOT A RESULT")
        print("CLASS:   undetermined")
        print("REASON:  the CONTROL arm went NaN. The plain build does not survive the "
              "registered fvSolution change, so the forward-AD arm's behaviour carries no "
              "information about the AD build. Separate finding: smoothSolver/GaussSeidel on p "
              "destabilises this case's PLAIN primal.")
        sys.exit(0)

    if F["_nan"]:
        print("\nVERDICT: GATE FAIL")
        print("CLASS:   AD CORRECTNESS")
        print("REASON:  the pre-registered prediction (the NaN disappears once the "
              "value-dependent multigrid stopping rule is removed) is REFUTED. The forward-AD "
              "primal reaches NaN under a non-multigrid, non-PBiCGStab/DILU pressure solver "
              "while the plain build under the identical setting does not. The upstream "
              "OpenFOAM-AD #2 confound is EXCLUDED by construction: smoothSolver/GaussSeidel is "
              "neither GAMG nor the PBiCGStab/DILU pair that issue reports.")
        print("NOTE:    GATE FAIL here means the registered threshold was not met. It is the "
               "MORE serious scientific outcome, not a failed run.")
        sys.exit(0)

    if ratio <= RATIO_BAND:
        print("\nVERDICT: PASS")
        print("CLASS:   CONDITIONING / DIAGNOSABILITY")
        print("REASON:  prediction confirmed. With the multigrid stopping rule removed the "
              "forward-AD primal no longer reaches NaN, and the iteration-1 continuity "
              "amplification fell from %.3fx (GAMG pair) to %.3fx, inside the registered "
              "band of %.1f. The 8th-significant-figure AD difference is present but is not "
              "amplified. The upstream ask is documentation + a warning, not an AD fix."
              % (rg, ratio, RATIO_BAND))
    else:
        print("\nVERDICT: GATE REACHED")
        print("CLASS:   CONDITIONING / DIAGNOSABILITY, PARTIAL")
        print("REASON:  the NaN disappeared, so the mechanism is solver-dependent and the class "
              "is conditioning; but the iteration-1 continuity amplification is %.3fx, OUTSIDE "
              "the registered band of %.1f (GAMG pair on record: %.3fx). The multigrid stopping "
              "rule does not account for the whole amplification and the residue is unexplained."
              % (ratio, RATIO_BAND, rg))
    sys.exit(0)


if __name__ == "__main__":
    main()
