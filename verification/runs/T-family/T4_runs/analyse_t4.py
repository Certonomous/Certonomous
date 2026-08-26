#!/usr/bin/env python3
"""T4 impinging jet -- the FROZEN comparator.

Grades the three registered rows against ERCOFTAC case025 (`ij2lr`, H/D = 2,
Re = 23 000), applies CLAUDE.md rule 5 (Roache triple gating) in its fixed
order, and REFUSES rather than degrading.

NO `assert` STATEMENT APPEARS IN THIS FILE.  Every gate and every refusal is an
explicit `sys.exit(2)` or a recorded verdict.  `assert` is stripped by `python
-O` and a gate that a flag can remove is not a gate; the lab has a live finding
of twelve forbidden asserts in shared instruments, and none of them is here.

THE GATE CAN ONLY MAKE THINGS WORSE.  Per rule 5 the triple gate can turn a
PASS or a GATE FAIL *into* NOT A RESULT and never the reverse.  That direction
is enforced structurally in `apply_gate()`: it is the only function that writes
a verdict, and its NOT-A-RESULT branch is unconditional.

Exit codes:  0 graded (rows may be PASS, GATE FAIL or NOT A RESULT)
             2 REFUSAL -- a structural precondition failed, or the planted-zero
               control found the reader blind or noisy
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REFDIR = os.path.normpath(os.path.join(
    HERE, "..", "..", "..", "..", "docs", "campaigns", "T-family",
    "reference-data", "ercoftac_case025"))

LEVELS = ("c", "m", "f")
CASES = {lv: "T4_IJ_%s" % lv for lv in LEVELS}
REFINEMENT = 2.0          # r21 = r32, exact by construction (build_t4.py)
FS = 1.25                 # Roache factor of safety
D = 0.02
U_BULK = 17.25
PLANT = 1.234e-03         # m/s -- the constant analyse_t3.py:81 uses
TOL_REL = 1.0e-06

# ---- the registered graded rows: (id, r/D, reference file, band half-width) --
GRADED = (("G1", 1.0, "ij2lr-10-sw-mu.dat", 0.02),
          ("G2", 2.0, "ij2lr-20-sw-mu.dat", 0.02),
          ("G3", 3.0, "ij2lr-30-sw-mu.dat", 0.02))

EXIT_OK, EXIT_REFUSE = 0, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# ---------------------------------------------------------------- references
def load_ref(name):
    p = os.path.join(REFDIR, name)
    if not os.path.isfile(p):
        refuse("reference file missing: %s" % p)
    out = []
    for line in open(p):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        out.append((float(parts[0]), float(parts[1])))
    if not out:
        refuse("reference file %s parsed to zero rows" % name)
    return out


def ref_peak(name):
    """Peak mean velocity U_max/U_bulk and its y/D, from the digitised file."""
    d = load_ref(name)
    y, u = max(d, key=lambda t: t[1])
    return u, y


# ------------------------------------------------------------------- reading
def latest_time(case_dir):
    ts = [t for t in os.listdir(case_dir)
          if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) and float(t) > 0]
    if not ts:
        return None
    return max(ts, key=float)


def sample_profile(case_dir, time, r_over_d, foam_bashrc):
    """U magnitude along a wall-normal line at r/D, READ FROM DISK through
    OpenFOAM's own postProcess -- not reimplemented here.  A reimplemented
    reader tests the reimplementation, not the instrument."""
    r = r_over_d * D
    sets = """
type sets;
libs ("libsampling.so");
setFormat raw;
interpolationScheme cellPoint;
fields (U);
sets
(
    line
    {
        type    uniform;
        axis    y;
        start   (%.10g 1e-6 0);
        end     (%.10g %.10g 0);
        nPoints 400;
    }
);
""" % (r, r, 0.5 * D * 2.0)
    sysdir = os.path.join(case_dir, "system")
    fn = os.path.join(sysdir, "t4sample")
    open(fn, "w").write(sets)
    cmd = ("source %s > /dev/null 2>&1; postProcess -case %s -func t4sample "
           "-time %s > /dev/null 2>&1" % (foam_bashrc, case_dir, time))
    subprocess.run(["bash", "-lc", cmd], check=False)
    root = os.path.join(case_dir, "postProcessing", "t4sample", str(time))
    if not os.path.isdir(root):
        return None
    cand = [f for f in os.listdir(root) if f.startswith("line") and "U" in f]
    if not cand:
        return None
    prof = []
    for line in open(os.path.join(root, cand[0])):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        p = line.split()
        if len(p) < 4:
            continue
        y = float(p[0])
        ux, uy, uz = float(p[1]), float(p[2]), float(p[3])
        prof.append((y / D, math.sqrt(ux * ux + uy * uy + uz * uz) / U_BULK))
    return prof or None


def peak_of(prof):
    y, u = max(prof, key=lambda t: t[1])
    return u, y


# ------------------------------------------- rule 3: the planted-zero control
def read_cell_centres(case_dir, time, foam_bashrc):
    """Cell centres READ FROM DISK, in cell-index order, via OpenFOAM's own
    writeCellCentres.  Needed because the plant must be AIMED."""
    cmd = ("source %s > /dev/null 2>&1; postProcess -case %s -func writeCellCentres "
           "-time %s > /dev/null 2>&1" % (foam_bashrc, case_dir, time))
    subprocess.run(["bash", "-lc", cmd], check=False)
    p = os.path.join(case_dir, str(time), "C")
    if not os.path.isfile(p):
        return None
    return parse_internal_vectors(open(p).read())


def parse_internal_vectors(txt):
    """(start_line_index, [(x,y,z), ...]) for an OpenFOAM vector internalField.

    Located STRUCTURALLY -- by the `internalField nonuniform List<vector>`
    header and the parenthesis that follows it -- never by matching a value.
    A value-matching locator can silently fail to find its target and then
    report success having done nothing.
    """
    lines = txt.splitlines(True)
    start = None
    for i, ln in enumerate(lines):
        if "internalField" in ln and "nonuniform" in ln:
            for j in range(i, min(i + 5, len(lines))):
                if lines[j].strip() == "(":
                    start = j + 1
                    break
            break
    if start is None:
        return None
    vals, idx = [], []
    for i in range(start, len(lines)):
        t = lines[i].strip()
        if t == ")":
            break
        m = re.match(r"\(\s*(\S+)\s+(\S+)\s+(\S+)\s*\)$", t)
        if not m:
            continue
        vals.append((float(m.group(1)), float(m.group(2)), float(m.group(3))))
        idx.append(i)
    return (idx, vals) if vals else None


def _plant_and_read(dst, time, upath, line_no, comp_before, magnitude,
                    r_over_d, foam_bashrc, base):
    """Write `magnitude` into one U component at a known line, re-read through
    the production reader, return the max-norm change the reader recovers."""
    lines = open(upath).read().splitlines(True)
    m = re.match(r"\s*\(\s*(\S+)\s+(\S+)\s+(\S+)\s*\)\s*$", lines[line_no])
    lines[line_no] = "(%.17g %s %s)\n" % (comp_before + magnitude, m.group(2), m.group(3))
    open(upath, "w").write("".join(lines))
    shutil.rmtree(os.path.join(dst, "postProcessing"), ignore_errors=True)
    got = sample_profile(dst, time, r_over_d, foam_bashrc)
    if got is None:
        return None
    return max(abs(a[1] - b[1]) for a, b in zip(base, got))


def planted_zero_control(case_dir, time, foam_bashrc, r_over_d=1.0):
    """BOTH ARMS, an AIMED plant, and a MEASURED detection floor.

    WHY THE PLANT IS AIMED.  The reader is a line sample at one radial station.
    A plant dropped into an arbitrary cell -- cell 0, say -- is almost certainly
    nowhere near that line, so the reader returns EXACTLY ZERO and the control
    condemns a perfectly sound reader.  The aim is therefore recovered from the
    mesh's own cell centres, written to disk by OpenFOAM, and the chosen cell's
    distance to the sampling line is REPORTED.  The safety property is the
    asymmetry: a mis-aimed plant can only make the positive arm FAIL, never pass
    falsely.

    WHY THE FLOOR IS MEASURED AND NOT ASSUMED.  This reader is compared under a
    MAX-NORM, and a max-norm change gate has a detection floor equal to its own
    current dmax.  Measured on T8: a registered plant of 1.234e-03 was INVISIBLE
    and only 1.0 moved the gate, because dmax was 1.012e-01 -- 82x the plant.
    Such a control "gets weaker exactly as the case gets worse."  So this one
    does not assert its sensitivity, it MEASURES it: a descending ladder of
    plant magnitudes is driven through the same reader and the smallest one the
    reader still resolves is recorded as the DEMONSTRATED DETECTION FLOOR.  The
    registered PLANT must sit above that floor or the control refuses.

    THE CONTROL NEVER WRITES INTO ANY CASE DIRECTORY.  It copies first.
    """
    tmp = tempfile.mkdtemp(prefix="t4pz_")
    try:
        dst = os.path.join(tmp, os.path.basename(case_dir))
        shutil.copytree(case_dir, dst, symlinks=True)
        if os.path.realpath(dst).startswith(os.path.realpath(case_dir)):
            refuse("planted-zero control: the scratch copy resolved INSIDE the "
                   "case tree; refusing to plant anywhere near live data")

        base = sample_profile(dst, time, r_over_d, foam_bashrc)
        if base is None:
            refuse("planted-zero control: the reader returned nothing on the "
                   "unplanted copy, so neither arm can be judged")

        # ---- NEGATIVE ARM: identical bytes must parse identically ----------
        again = sample_profile(dst, time, r_over_d, foam_bashrc)
        if again is None:
            refuse("planted-zero control: negative arm produced no profile")
        dneg = max(abs(a[1] - b[1]) for a, b in zip(base, again))
        if dneg != 0.0:
            refuse("planted-zero control NEGATIVE ARM FAILED: the reader returned "
                   "%.17g on identical bytes. The reader is NOISY and its zeros "
                   "are not zeros. Every T4 number that depends on it is "
                   "withdrawn, not re-graded." % dneg)

        # ---- AIM: the cell the sampling line actually reads -----------------
        cc = read_cell_centres(dst, time, foam_bashrc)
        if cc is None:
            refuse("planted-zero control: could not read cell centres, so the "
                   "plant cannot be AIMED and an unaimed plant would libel a "
                   "sound reader")
        _, centres = cc
        y_peak = max(base, key=lambda t: t[1])[0] * D
        target = (r_over_d * D, y_peak, 0.0)
        best_i, best_d = None, None
        for i, (x, y, z) in enumerate(centres):
            dd = (x - target[0]) ** 2 + (y - target[1]) ** 2 + z * z
            if best_d is None or dd < best_d:
                best_i, best_d = i, dd
        aim_dist = math.sqrt(best_d)

        upath = os.path.join(dst, str(time), "U")
        if not os.path.isfile(upath):
            refuse("planted-zero control: no %s to plant into" % upath)
        pu = parse_internal_vectors(open(upath).read())
        if pu is None:
            refuse("planted-zero control: could not locate U's internalField "
                   "STRUCTURALLY (the plant is never located by value match)")
        uidx, uvals = pu
        if best_i >= len(uidx):
            refuse("planted-zero control: cell centres (%d) and U entries (%d) "
                   "disagree in length; refusing to plant by a mismatched index"
                   % (len(centres), len(uvals)))
        line_no, comp_before = uidx[best_i], uvals[best_i][0]

        # ---- MEASURE THE DETECTION FLOOR -----------------------------------
        ladder = (1.0, 1.0e-1, 1.0e-2, PLANT, 1.0e-4, 1.0e-5, 1.0e-6)
        seen = {}
        floor = None
        for mag in ladder:
            d = _plant_and_read(dst, time, upath, line_no, comp_before, mag,
                                r_over_d, foam_bashrc, base)
            if d is None:
                refuse("planted-zero control: the reader returned nothing while "
                       "measuring the detection floor at plant %.6g" % mag)
            seen[mag] = d
            if d > 0.0:
                floor = mag
        if floor is None:
            refuse("planted-zero control POSITIVE ARM FAILED: NO plant magnitude "
                   "in %r was visible to the reader at %s line %d. The reader is "
                   "BLIND and every zero it has produced for this rung is "
                   "worthless." % (ladder, upath, line_no + 1))

        dpos = seen[PLANT]
        if dpos == 0.0:
            refuse("planted-zero control POSITIVE ARM FAILED at the REGISTERED "
                   "plant: %s line %d was changed by %.6g m/s on disk and the "
                   "reader returned EXACTLY ZERO, while %.6g WAS visible. The "
                   "registered plant sits BELOW this reader's demonstrated "
                   "detection floor and the control would pass while seeing "
                   "nothing." % (upath, line_no + 1, PLANT, floor))

        return dict(status="PASS", plant=PLANT, planted_line=line_no + 1,
                    planted_cell=best_i, aim_distance_m=aim_dist,
                    station_r_over_D=r_over_d,
                    recovered_max_abs_change=dpos, negative_arm=dneg,
                    demonstrated_detection_floor=floor,
                    ladder={("%g" % k): v for k, v in seen.items()})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------- rule 5: Roache triple gate
def classify(triple):
    """(state, observed_order p, extrapolate).  Never quotes an order for a
    non-monotone triple."""
    f3, f2, f1 = triple          # coarse, medium, fine
    e21, e32 = f1 - f2, f2 - f3
    if e21 == 0.0 and e32 == 0.0:
        return "EXACT", None, f1
    if e21 == 0.0 or e32 == 0.0:
        return "STAGNANT", None, f1
    ratio = e32 / e21
    if ratio <= 0.0:
        return "OSCILLATORY", None, f1
    if abs(e21) >= abs(e32):
        return "DIVERGENT", None, f1
    p = math.log(abs(ratio)) / math.log(REFINEMENT)
    # Richardson extrapolate.  Sign convention checked against the lab's own
    # finding that analyse_t3.py:384 and analyse_t1c.py:337 carry an INVERTED
    # form (`f_fine + e21/den`); the correct form is f_fine - e21/den and is
    # what is used here.
    den = REFINEMENT ** p - 1.0
    return "CONVERGING", p, (f1 - e21 / den)


def gci(triple, p):
    f3, f2, f1 = triple
    if p is None or f1 == 0.0:
        return None
    eps = abs((f1 - f2) / f1)
    return FS * eps / (REFINEMENT ** p - 1.0)


def apply_gate(value, band_lo, band_hi, triple, converged_all, plateaued_all):
    """THE ONLY function that writes a verdict.  Rule 5's fixed order."""
    state, p, extrap = classify(triple)
    # (1) any level not iteratively converged or not plateaued -> NOT A RESULT
    if not (converged_all and plateaued_all):
        return "NOT A RESULT", state, p, None, ("gate (1): a level is not "
                                                "iteratively converged or not plateaued")
    # (2) a non-CONVERGING triple -> NOT A RESULT, whatever the value says
    if state != "CONVERGING":
        return "NOT A RESULT", state, p, None, "gate (2): triple is %s" % state
    # (3) only now may the band be consulted
    g = gci(triple, p)
    if band_lo <= value <= band_hi:
        return "PASS", state, p, g, ""
    return "GATE FAIL", state, p, g, ""


# --------------------------------------------------------------- convergence
RESID_FLOOR = 1.0e-6      # registered: p_rgh initial residual
SUSTAIN = 200             # iterations the floor must be held for
FIELD_TOL = 2.0e-4        # registered: the graded quantity must move less than
                          # this between the last two checkpoints, in U/U_bulk
                          # units == 1 % of the band half-width (0.02)


def two_latest_times(case_dir):
    ts = sorted((t for t in os.listdir(case_dir)
                 if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) and float(t) > 0),
                key=float)
    if len(ts) < 2:
        return None
    return ts[-2], ts[-1]


def iterative_state(case_dir, r_over_d, foam_bashrc):
    """A RESIDUAL IS NOT CONVERGENCE.

    Measured on T8: the fine level's `T` initial residual reached 5.932e-07
    against a registered 1e-6 -- a pass on residuals alone -- while the
    temperature field was STILL MOVING 0.101 K between checkpoints, wrong by
    16 400x.  A residual measures how well the current linear system was
    solved, not whether the solution has stopped moving.

    So the registered criterion is three-part, in the directional form this
    territory already uses (`analyse_e4a2.py:308`, `c2 = not cl["growing"]`):

      C1  sustained floor : the last SUSTAIN p_rgh initial residuals <= 1e-6
      C2  NOT GROWING     : the residual is not trending upward.  Directional,
                            deliberately -- a trend-divided-by-spread form
                            admits a run that never converged at all
                            (measured: T8's coarse level passes one).
      C3  FIELD CHANGE    : the GRADED QUANTITY moves less than FIELD_TOL
                            between the last two written checkpoints.

    All three, or the level is not converged and rule 5 gate (1) fires.
    """
    log = os.path.join(case_dir, "log.solve")
    out = dict(c1=False, c2=False, c3=False, final_residual=None,
               field_change=None, converged=False)
    if not os.path.isfile(log):
        return out
    body = open(log, errors="replace").read()
    res = [float(m) for m in re.findall(
        r"Solving for p_rgh, Initial residual = ([0-9.eE+-]+)", body)]
    if len(res) < 2 * SUSTAIN:
        return out
    out["final_residual"] = res[-1]

    # C1 -- sustained, not a single lucky iteration
    out["c1"] = max(res[-SUSTAIN:]) <= RESID_FLOOR

    # C2 -- directional: is it growing?
    n = SUSTAIN
    earlier = sum(res[-2 * n:-n]) / n
    later = sum(res[-n:]) / n
    out["c2"] = not (later > earlier)

    # C3 -- has the GRADED QUANTITY stopped moving?
    tt = two_latest_times(case_dir)
    if tt is not None:
        prev, last = tt
        a = sample_profile(case_dir, prev, r_over_d, foam_bashrc)
        b = sample_profile(case_dir, last, r_over_d, foam_bashrc)
        if a is not None and b is not None:
            ch = abs(peak_of(b)[0] - peak_of(a)[0])
            out["field_change"] = ch
            out["c3"] = ch <= FIELD_TOL
            out["checkpoints"] = [prev, last]

    out["converged"] = bool(out["c1"] and out["c2"] and out["c3"])
    return out


# --------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--foam-bashrc",
                    default="/usr/lib/openfoam/openfoam2606/etc/bashrc")
    ap.add_argument("--json", default=os.path.join(HERE, "gate_t4.json"))
    ap.add_argument("--skip-plant-control", action="store_true",
                    help=argparse.SUPPRESS)
    a = ap.parse_args()

    # --- structural preconditions: refuse, never degrade -------------------
    for lv, case in CASES.items():
        if not os.path.isfile(os.path.join(HERE, "DONE.%s" % case)):
            refuse("no DONE.%s -- the whole rung is graded or none of it is. "
                   "Run mark_done_t4.py; if it says NOT DONE, that is the "
                   "answer and this comparator does not overrule it." % case)

    times, dirs = {}, {}
    for lv, case in CASES.items():
        d = os.path.join(HERE, case)
        t = latest_time(d)
        if t is None:
            refuse("%s has no time directory beyond 0" % case)
        times[lv], dirs[lv] = t, d

    # --- CLAUDE.md rule 3, BEFORE any number is believed -------------------
    control = {"status": "SKIPPED"}
    if not a.skip_plant_control:
        control = planted_zero_control(dirs["f"], times["f"], a.foam_bashrc)
        print("planted-zero control: PASS  (positive arm recovered %.6g m/s "
              "from a %.6g m/s plant at line %d; negative arm returned %.17g)"
              % (control["recovered_max_abs_change"], control["plant"],
                 control["planted_line"], control["negative_arm"]))

    conv = {lv: iterative_state(dirs[lv], GRADED[0][1], a.foam_bashrc)
            for lv in LEVELS}
    converged_all = all(conv[lv]["converged"] for lv in LEVELS)
    plateaued_all = converged_all   # C2/C3 are inside `converged`; rule 5 gate
                                    # (1) reads the conjunction either way
    for lv in LEVELS:
        c = conv[lv]
        print("level %s: C1 floor=%s C2 not-growing=%s C3 field-change=%s "
              "(resid %.3e, field moved %s) -> %s"
              % (lv, c["c1"], c["c2"], c["c3"],
                 c["final_residual"] if c["final_residual"] is not None else float("nan"),
                 ("%.3e" % c["field_change"]) if c["field_change"] is not None else "UNMEASURED",
                 "CONVERGED" if c["converged"] else "NOT CONVERGED"))

    rows = []
    for rid, rd, reffile, half in GRADED:
        ref, refy = ref_peak(reffile)
        vals = {}
        for lv in LEVELS:
            prof = sample_profile(dirs[lv], times[lv], rd, a.foam_bashrc)
            if prof is None:
                refuse("could not sample r/D=%.1f on level %s -- the reader "
                       "returned nothing, and a missing number is not a zero"
                       % (rd, lv))
            vals[lv] = peak_of(prof)[0]
        triple = (vals["c"], vals["m"], vals["f"])
        verdict, state, p, g, note = apply_gate(
            vals["f"], ref - half, ref + half, triple,
            converged_all, plateaued_all)
        rows.append(dict(row=rid, r_over_D=rd, reference=ref,
                         band=[ref - half, ref + half], value_fine=vals["f"],
                         triple=dict(zip(LEVELS, triple)), triple_state=state,
                         observed_order=p, gci=g, verdict=verdict, note=note,
                         deviation=vals["f"] - ref,
                         band_utilisation=abs(vals["f"] - ref) / half))
        print("%-3s r/D=%.1f  fine=%.4f  ref=%.4f  band=[%.4f,%.4f]  "
              "triple=%-11s p=%s GCI=%s  ->  %s%s"
              % (rid, rd, vals["f"], ref, ref - half, ref + half, state,
                 ("%.3f" % p) if p is not None else "n/a",
                 ("%.4f%%" % (100 * g)) if g is not None else "n/a",
                 verdict, (" [" + note + "]") if note else ""))

    out = dict(rung="T4", reference="ERCOFTAC case025 ij2lr (H/D=2, Re=23000)",
               refinement_ratio=REFINEMENT, factor_of_safety=FS,
               planted_zero_control=control,
               iterative={lv: conv[lv] for lv in LEVELS},
               convergence_criterion=dict(resid_floor=RESID_FLOOR,
                                          sustain=SUSTAIN, field_tol=FIELD_TOL),
               rows=rows)
    json.dump(out, open(a.json, "w"), indent=2)
    print("wrote %s" % a.json)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
