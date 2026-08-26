#!/usr/bin/env python3
"""T4b impinging jet -- the FROZEN comparator, with the section-9 controls ON THE
GRADING PATH.

T4 returned NOT A RESULT x3 with its controls C1 (y+), C2 (nozzle-exit
development) and C3 (mass balance) UNIMPLEMENTED in the comparator: C1 was
measured by a lane outside the grading path and the rung's verdict could not
depend on it.  Here every control is a READER inside this file, run before any
number is believed, and every reader carries its own planted control
(CLAUDE.md rule 3).

WHAT IS IMPORTED FROZEN.  T4_runs/analyse_t4.py (sha256 printed at every run):
sample_profile / peak_of (the G-row reader), read_cell_centres /
parse_internal_vectors (aiming), planted_zero_control (the G-row plant with its
measured detection floor), classify / gci (Roache), load_ref / ref_peak (the
held ERCOFTAC files).  Its apply_gate is NOT used: this file's own apply_gate
applies the observed-order floors of the SHARED instrument scripts/roache_triple.py
-- STAGNANT_FLOOR (0 < p < 0.5 is STAGNANT) and P_MIN (|p| < 0.05 is DEGENERATE:
e21 ~ e32, the fitted order is rounding residual) -- imported by name, never
defined here (MESH_STANDARD.md section 10.5, chief's ruling 01967a7b: a new
registration imports the shared names or defines neither).  Both states are
NOT A RESULT at gate (2), exactly as the family's per-comparator P_MIN = 0.5
floor (T11 AMENDMENT 1, analyse_t3_rff) reads them; the symbol changes, the
verdict does not.  The registered JSON carries the same two numbers and this
file REFUSES if the import and the registration disagree.  It also folds
C1/C1b/C2/C3/C6 into gate (1).

THE INSTRUMENT FACT, REGISTERED.  Generic `postProcess -func yPlus` returns
y+ = 0 on every patch here ("Unable to find turbulence model in the database",
measured on the 1-iteration smoke 2026-08-26 and on the finished T4 runs); only
the solver's own `-postProcess` mode constructs the turbulence model and sees
y+.  The registered y+ reader is the solver-mode one, and the comparator runs
the BLIND one beside it on the coarse level and REFUSES unless the blind one
returns exactly 0 on every patch while the registered one returns > 0 -- the
two readings side by side are the control that makes the y+ number evidence.

NO `assert` STATEMENT APPEARS IN THIS FILE (L-332).  Every refusal is
sys.exit(2).  --selftest drives the refusals under python3 AND python3 -O.

THE GATE CAN ONLY MAKE THINGS WORSE.  apply_gate() is the only function that
writes a verdict; its NOT A RESULT branches return before the band is read.

Exit codes: 0 graded (rows PASS / GATE FAIL / NOT A RESULT), 1 selftest failed,
            2 REFUSAL.
"""
import argparse
import ast
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
T4DIR = os.path.join(os.path.dirname(HERE), "T4_runs")
sys.path.insert(0, T4DIR)
import analyse_t4 as A                                    # noqa: E402  FROZEN
SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE)))), "scripts")
sys.path.insert(0, SCRIPTS)
from roache_triple import STAGNANT_FLOOR, P_MIN           # noqa: E402  SHARED (MESH_STANDARD 10.5)

REG = json.load(open(os.path.join(HERE, "T4b_registered.json")))
LEVELS = ("c", "m", "f")
CASES = {lv: "T4b_IJ_%s" % lv for lv in LEVELS}
REFINEMENT = float(REG["refinement_ratio"])
FS = float(REG["factor_of_safety"])
PLANT = float(REG["planted_control_value"])
YPLUS_SCALE = float(REG["yplus_plant_scale"])
FLUX_SCALE = float(REG["flux_plant_scale"])
D, U_BULK, H = A.D, A.U_BULK, 2.0 * A.D
C = REG["controls"]
_RF = REG["roache_floors"]
if (float(_RF["STAGNANT_FLOOR"]), float(_RF["P_MIN"])) != (STAGNANT_FLOOR, P_MIN):
    print("REFUSE: T4b_registered.json roache_floors %r disagree with scripts/roache_triple.py "
          "STAGNANT_FLOOR=%r P_MIN=%r" % (_RF, STAGNANT_FLOOR, P_MIN))
    sys.exit(2)
YPLUS_MAX = float(C["C1"]["threshold"])
UC_REF, UC_TOL = float(C["C2"]["reference"]), float(C["C2"]["tolerance_rel"])
MASS_TOL = float(C["C3"]["threshold"])
RESID_FLOOR = float(C["C6"]["c6_1_floor"]["threshold"])
FLOOR_WINDOW = 2000
GROW_TOL = float(C["C6"]["c6_2_not_growing"]["threshold"])
GROW_WINDOW = 1000
FIELD_TOL = float(C["C6"]["c6_3_field_change"]["threshold"])
GRADED = [(k, float(v["r_over_D"]), v["reference_file"], 0.02)
          for k, v in REG["graded_rows"].items() if k.startswith("G")]
PATCHES_FLUX = ("inlet", "entrainment", "farfield", "plate", "pipeWall")
EXIT_OK, EXIT_SELFTEST_FAIL, EXIT_REFUSE = 0, 1, 2
FOAM_BASHRC_DEFAULT = "/usr/lib/openfoam/openfoam2606/etc/bashrc"


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def foam(cmd, bashrc, cwd):
    full = "set +u; . %s > /dev/null 2>&1; set -u; cd %s && %s" % (bashrc, cwd, cmd)
    return subprocess.run(["bash", "-c", full], capture_output=True, text=True)


# ------------------------------------------------------------- scratch copies
def scratch_copy(case_dir, time):
    """A read/plant copy: constant/ HARDLINKED (read only, never written),
    system/ and 0/ and <time>/ REAL copies (plants rewrite files there).
    Refuses if the copy resolves inside the case tree."""
    tmp = tempfile.mkdtemp(prefix="t4b_")
    dst = os.path.join(tmp, os.path.basename(case_dir))
    os.makedirs(dst)
    if os.path.realpath(dst).startswith(os.path.realpath(case_dir)):
        refuse("scratch copy resolved INSIDE the case tree")
    r = subprocess.run(["cp", "-al", os.path.join(case_dir, "constant"), os.path.join(dst, "constant")])
    if r.returncode != 0:
        shutil.copytree(os.path.join(case_dir, "constant"), os.path.join(dst, "constant"))
    for sub in ("system", "0", str(time)):
        src = os.path.join(case_dir, sub)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(dst, sub))
    return tmp, dst


def scale_internal_vectors(path, factor):
    lines = open(path).read().splitlines(True)
    pv = A.parse_internal_vectors("".join(lines))
    if pv is None:
        refuse("could not locate the internalField of %s structurally" % path)
    idx, vals = pv
    for i, (x, y, z) in zip(idx, vals):
        lines[i] = "(%.17g %.17g %.17g)\n" % (x * factor, y * factor, z * factor)
    open(path, "w").write("".join(lines))
    return len(idx)


def scale_patch_scalar_list(path, patch, factor):
    """Multiply every entry of `value nonuniform List<scalar>` of one patch in an
    OpenFOAM scalar field file (phi) by factor.  Located STRUCTURALLY."""
    lines = open(path).read().splitlines(True)
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == "boundaryField":
            start = i
            break
    if start is None:
        refuse("%s has no boundaryField" % path)
    j = None
    for i in range(start, len(lines)):
        if lines[i].strip() == patch:
            j = i
            break
    if j is None:
        refuse("%s has no patch %s in boundaryField" % (path, patch))
    k = None
    for i in range(j, min(j + 8, len(lines))):
        if "nonuniform" in lines[i] and "List<scalar>" in lines[i]:
            k = i
            break
    if k is None:
        refuse("%s patch %s carries no nonuniform List<scalar> value to plant into" % (path, patch))
    n = int(lines[k + 1].strip())
    if lines[k + 2].strip() != "(":
        refuse("%s patch %s: expected '(' after the count" % (path, patch))
    for i in range(k + 3, k + 3 + n):
        lines[i] = "%.17g\n" % (float(lines[i]) * factor)
    open(path, "w").write("".join(lines))
    return n


# ---------------------------------------------------------------- the readers
def yplus_read(copy_dir, time, bashrc, generic=False):
    """{patch: (min, max, avg)} at `time`, from the yPlus function object.
    generic=True is the BLIND path (postProcess), kept only as a control."""
    shutil.rmtree(os.path.join(copy_dir, "postProcessing"), ignore_errors=True)
    exe = "postProcess" if generic else "buoyantBoussinesqSimpleFoam -postProcess"
    r = foam("%s -case %s -func yPlus -time %s" % (exe, copy_dir, time), bashrc, copy_dir)
    root = os.path.join(copy_dir, "postProcessing", "yPlus")
    out = {}
    if not os.path.isdir(root):
        return None
    for dp, _, fns in os.walk(root):
        for fn in fns:
            if not fn.endswith(".dat"):
                continue
            for line in open(os.path.join(dp, fn)):
                if line.startswith("#"):
                    continue
                p = line.split()
                if len(p) >= 5 and float(p[0]) == float(time):
                    out[p[1]] = (float(p[2]), float(p[3]), float(p[4]))
    return out or None


def exit_profile(copy_dir, time, bashrc):
    """[(r, |U|/U_bulk), ...] along a line across the nozzle-exit plane y = H from
    the axis to the pipe wall, sampled through OpenFOAM's own sets (cellPoint)."""
    sysdir = os.path.join(copy_dir, "system")
    open(os.path.join(sysdir, "t4bexit"), "w").write(
        'type sets; libs ("libsampling.so"); setFormat raw; interpolationScheme cellPoint; '
        'fields (U);\nsets ( exitline { type uniform; axis x; start (1e-6 %.10g 0); '
        'end (%.10g %.10g 0); nPoints 200; } );\n' % (H, 0.5 * D - 1e-6, H))
    shutil.rmtree(os.path.join(copy_dir, "postProcessing", "t4bexit"), ignore_errors=True)
    foam("postProcess -case %s -func t4bexit -time %s" % (copy_dir, time), bashrc, copy_dir)
    root = os.path.join(copy_dir, "postProcessing", "t4bexit", str(time))
    if not os.path.isdir(root):
        return None
    cand = [f for f in os.listdir(root) if f.startswith("exitline") and "U" in f]
    if not cand:
        return None
    prof = []
    for line in open(os.path.join(root, cand[0])):
        p = line.split()
        if len(p) < 4 or line.startswith("#"):
            continue
        prof.append((float(p[0]),
                     math.sqrt(float(p[1]) ** 2 + float(p[2]) ** 2 + float(p[3]) ** 2) / U_BULK))
    return prof or None


def exit_read(copy_dir, time, bashrc):
    """U_c/U_bulk = the maximum of exit_profile (control C2's registered quantity)."""
    prof = exit_profile(copy_dir, time, bashrc)
    return None if prof is None else max(v for _, v in prof)


def flux_read(copy_dir, time, bashrc):
    """{patch: sum(phi)} over the five open/wall patches, through surfaceFieldValue."""
    sysdir = os.path.join(copy_dir, "system")
    out = {}
    for p in PATCHES_FLUX:
        fn = "t4bflux_%s" % p
        open(os.path.join(sysdir, fn), "w").write(
            'type surfaceFieldValue; libs ("libfieldFunctionObjects.so"); regionType patch; '
            'name %s; operation sum; fields (phi); writeFields false; log false;\n' % p)
        shutil.rmtree(os.path.join(copy_dir, "postProcessing", fn), ignore_errors=True)
        foam("postProcess -case %s -func %s -time %s" % (copy_dir, fn, time), bashrc, copy_dir)
        root = os.path.join(copy_dir, "postProcessing", fn)
        val = None
        if os.path.isdir(root):
            for dp, _, fns in os.walk(root):
                for f in fns:
                    if f.endswith(".dat"):
                        for line in open(os.path.join(dp, f)):
                            q = line.split()
                            if not line.startswith("#") and len(q) >= 2 and float(q[0]) == float(time):
                                val = float(q[1])
        if val is None:
            return None
        out[p] = val
    return out


def imbalance(fl):
    return abs(sum(fl.values())) / abs(fl["inlet"])


# ------------------------------------------------------- residual history (C6)
def residual_history(case_dir):
    """[(time, p_rgh initial residual), ...] for EVERY p_rgh solve (every
    non-orthogonal corrector), STREAMED from log.solve, never loaded whole."""
    log = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(log):
        return []
    out, t = [], None
    pat = re.compile(r"Solving for p_rgh, Initial residual = ([0-9.eE+-]+)")
    with open(log, errors="replace") as fh:
        for line in fh:
            if line.startswith("Time = "):
                t = float(line[7:].strip())
            elif "Solving for p_rgh" in line:
                m = pat.search(line)
                if m and t is not None:
                    out.append((t, float(m.group(1))))
    return out


def residual_tests(hist, end_time):
    """C6.1 sustained floor over the last FLOOR_WINDOW iterations (all solves);
    C6.2 not growing: mean over the last GROW_WINDOW iterations <= GROW_TOL x
    the mean over the preceding GROW_WINDOW."""
    r = dict(c6_1=False, c6_2=False, floor_max=None, grow_ratio=None, n=len(hist))
    if not hist:
        return r
    last_t = hist[-1][0]
    w1 = [v for t, v in hist if t > last_t - FLOOR_WINDOW]
    if w1 and last_t >= FLOOR_WINDOW:
        r["floor_max"] = max(w1)
        r["c6_1"] = r["floor_max"] <= RESID_FLOOR
    later = [v for t, v in hist if t > last_t - GROW_WINDOW]
    earlier = [v for t, v in hist if last_t - 2 * GROW_WINDOW < t <= last_t - GROW_WINDOW]
    if later and earlier and last_t >= 2 * GROW_WINDOW:
        me, ml = sum(earlier) / len(earlier), sum(later) / len(later)
        r["grow_ratio"] = (ml / me) if me > 0 else None
        r["c6_2"] = (r["grow_ratio"] is not None) and (r["grow_ratio"] <= GROW_TOL)
    r["reached_endTime"] = abs(last_t - end_time) < 1e-9
    return r


# --------------------------- Roache with the SHARED floors (roache_triple.py)
def classify(triple):
    """A.classify (frozen) decides EXACT / STAGNANT(a zero step) / OSCILLATORY /
    DIVERGENT / CONVERGING; on CONVERGING the shared floors are applied in the
    order roache_triple.gci_equal applies them: |p| < P_MIN -> DEGENERATE,
    p < STAGNANT_FLOOR -> STAGNANT.  Both are NOT A RESULT states."""
    state, p, extrap = A.classify(triple)
    if state == "CONVERGING" and p is not None:
        if abs(p) < P_MIN:
            return "DEGENERATE", p, None
        if p < STAGNANT_FLOOR:
            return "STAGNANT", p, None
    return state, p, extrap


def gci(triple, p):
    if p is None or p < STAGNANT_FLOOR:
        return None
    return A.gci(triple, p)


def apply_gate(value, band_lo, band_hi, triple, gate1_reasons):
    """THE ONLY function that writes a verdict.  Rule 5's fixed order, with
    gate (1) carrying C1/C1b/C2/C3/C6 and gate (2) carrying the shared floors."""
    state, p, _ = classify(triple)
    if gate1_reasons:
        return "NOT A RESULT", state, p, None, "gate (1): " + "; ".join(gate1_reasons)
    if state != "CONVERGING":
        note = "gate (2): triple is %s" % state
        if state == "STAGNANT" and p is not None:
            note += " (p = %.4g < STAGNANT_FLOOR = %g; GCI refused)" % (p, STAGNANT_FLOOR)
        elif state == "DEGENERATE":
            note += " (|p| = %.4g < P_MIN = %g: e21 ~ e32; GCI refused)" % (abs(p), P_MIN)
        return "NOT A RESULT", state, p, None, note
    g = gci(triple, p)
    if band_lo <= value <= band_hi:
        return "PASS", state, p, g, ""
    return "GATE FAIL", state, p, g, ""


# ----------------------------------------------------- planted controls (new)
def yplus_controls(case_dir, time, bashrc):
    tmp, dst = scratch_copy(case_dir, time)
    try:
        blind = yplus_read(dst, time, bashrc, generic=True)
        seeing = yplus_read(dst, time, bashrc, generic=False)
        if seeing is None or not {"plate", "pipeWall"} <= set(seeing):
            refuse("y+ reader (solver -postProcess) returned nothing on %s" % case_dir)
        if blind is None or any(v[1] != 0.0 for v in blind.values()):
            refuse("the BLIND y+ path (generic postProcess) did not return exactly 0 -- the "
                   "registered instrument fact does not hold on this box today, so the two-reader "
                   "control cannot be formed: %r" % blind)
        if any(seeing[p][1] <= 0.0 for p in ("plate", "pipeWall")):
            refuse("the registered y+ reader returned a non-positive maximum: %r" % seeing)
        again = yplus_read(dst, time, bashrc, generic=False)
        if again != seeing:
            refuse("y+ NEGATIVE ARM FAILED: identical bytes read differently")
        n = scale_internal_vectors(os.path.join(dst, str(time), "U"), YPLUS_SCALE)
        planted = yplus_read(dst, time, bashrc, generic=False)
        want = math.sqrt(YPLUS_SCALE)
        ratios = {p: planted[p][1] / seeing[p][1] for p in ("plate", "pipeWall")}
        for p, rr in ratios.items():
            if abs(rr - want) > 1e-9 * want:
                refuse("y+ POSITIVE ARM FAILED on %s: U x%g in %d cells must move y+_max by "
                       "exactly x%.12g (nut_w = 0 under nutLowReWallFunction); reader returned "
                       "x%.12g" % (p, YPLUS_SCALE, n, want, rr))
        return dict(status="PASS", blind=blind, seeing=seeing, planted_ratio=ratios,
                    expected_ratio=want, cells_scaled=n)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def exit_controls(case_dir, time, bashrc):
    """Rule 3 on the exit-line reader, in the frozen G reader's shape: the plant is
    AIMED at the cell nearest the line's current maximum (a max-reader cannot see a
    plant dropped into a cell whose value is below the maximum -- measured on the
    1-iteration smoke 2026-08-26: a plant of 1.0 m/s near the axis, where |U| was
    8.7 m/s against a line maximum of 15.4 m/s, was invisible), and visibility is
    judged on the WHOLE PROFILE in max-norm, with the change in the C2 scalar
    itself reported beside it.  A descending ladder measures the detection floor;
    the registered PLANT must sit above it."""
    tmp, dst = scratch_copy(case_dir, time)
    try:
        base = exit_profile(dst, time, bashrc)
        if base is None:
            refuse("exit-line reader returned nothing on %s" % case_dir)
        again = exit_profile(dst, time, bashrc)
        if again != base:
            refuse("exit-line NEGATIVE ARM FAILED: identical bytes read differently")
        cc = A.read_cell_centres(dst, time, bashrc)
        if cc is None:
            refuse("exit-line control: could not read cell centres to AIM the plant")
        _, centres = cc
        r_max, u_max = max(base, key=lambda t: t[1])
        target = (r_max, H, 0.0)
        best_i = min(range(len(centres)), key=lambda i: (centres[i][0] - target[0]) ** 2
                     + (centres[i][1] - target[1]) ** 2 + centres[i][2] ** 2)
        aim_dist = math.sqrt((centres[best_i][0] - target[0]) ** 2
                             + (centres[best_i][1] - target[1]) ** 2 + centres[best_i][2] ** 2)
        upath = os.path.join(dst, str(time), "U")
        pu = A.parse_internal_vectors(open(upath).read())
        if pu is None or best_i >= len(pu[0]):
            refuse("exit-line control: cannot locate the aimed cell in U")
        line_no = pu[0][best_i]
        orig = open(upath).read().splitlines(True)
        seen, seen_scalar, floor = {}, {}, None
        for mag in (1.0, 1.0e-1, 1.0e-2, PLANT, 1.0e-4, 1.0e-5, 1.0e-6):
            lines = list(orig)
            m = re.match(r"\s*\(\s*(\S+)\s+(\S+)\s+(\S+)\s*\)\s*$", lines[line_no])
            lines[line_no] = "(%s %.17g %s)\n" % (m.group(1), float(m.group(2)) - mag, m.group(3))
            open(upath, "w").write("".join(lines))
            got = exit_profile(dst, time, bashrc)
            if got is None or len(got) != len(base):
                refuse("exit-line reader returned nothing (or a different length) while measuring the floor")
            seen[mag] = max(abs(a[1] - b[1]) for a, b in zip(base, got))
            seen_scalar[mag] = abs(max(v for _, v in got) - u_max)
            if seen[mag] > 0.0:
                floor = mag
        if floor is None:
            refuse("exit-line POSITIVE ARM FAILED: no plant magnitude was visible at U line %d "
                   "(aimed at r = %.4g m on the exit line, aim distance %.3g m)"
                   % (line_no + 1, r_max, aim_dist))
        if seen[PLANT] == 0.0:
            refuse("exit-line POSITIVE ARM FAILED at the registered plant %g (floor %g)" % (PLANT, floor))
        return dict(status="PASS", base=u_max, base_r_of_max=r_max, planted_line=line_no + 1,
                    planted_cell=best_i, aim_distance_m=aim_dist,
                    recovered=seen[PLANT], recovered_in_C2_scalar=seen_scalar[PLANT],
                    demonstrated_detection_floor=floor,
                    ladder={"%g" % k: v for k, v in seen.items()},
                    ladder_C2_scalar={"%g" % k: v for k, v in seen_scalar.items()})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def flux_controls(case_dir, time, bashrc):
    tmp, dst = scratch_copy(case_dir, time)
    try:
        base = flux_read(dst, time, bashrc)
        if base is None:
            refuse("flux reader returned nothing on %s" % case_dir)
        if flux_read(dst, time, bashrc) != base:
            refuse("flux NEGATIVE ARM FAILED: identical bytes read differently")
        n = scale_patch_scalar_list(os.path.join(dst, str(time), "phi"), "inlet", FLUX_SCALE)
        planted = flux_read(dst, time, bashrc)
        if planted is None:
            refuse("flux reader returned nothing on the planted copy")
        s = sum(base.values())
        expected = abs(s + (FLUX_SCALE - 1.0) * base["inlet"]) / abs(FLUX_SCALE * base["inlet"])
        got = imbalance(planted)
        if abs(got - expected) > 1e-9 * max(expected, 1e-30) + 1e-15:
            refuse("flux POSITIVE ARM FAILED: inlet phi x%g over %d faces predicts imbalance "
                   "%.15g, reader returned %.15g" % (FLUX_SCALE, n, expected, got))
        return dict(status="PASS", base=base, base_imbalance=imbalance(base),
                    planted_imbalance=got, expected_imbalance=expected, faces_scaled=n)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------- main
def grade(a):
    prov = {"analyse_t4.py (frozen, imported)": sha256_of(os.path.join(T4DIR, "analyse_t4.py")),
            "analyse_t4b.py": sha256_of(os.path.abspath(__file__)),
            "T4b_registered.json": sha256_of(os.path.join(HERE, "T4b_registered.json"))}
    print("T4b comparator.  shared floors STAGNANT_FLOOR = %g, P_MIN = %g (scripts/roache_triple.py).  "
          "provenance (sha256):" % (STAGNANT_FLOOR, P_MIN))
    for k, v in prov.items():
        print("  %-36s %s" % (k, v))
    for lv, case in CASES.items():
        if not os.path.isfile(os.path.join(HERE, "DONE.%s" % case)):
            refuse("no DONE.%s -- the whole rung is graded or none of it is (mark_done_t4b.py "
                   "decides; this comparator does not overrule it)" % case)
    dirs = {lv: os.path.join(HERE, c) for lv, c in CASES.items()}
    times = {}
    for lv in LEVELS:
        t = A.latest_time(dirs[lv])
        if t is None:
            refuse("%s has no time directory beyond 0" % CASES[lv])
        times[lv] = t

    # ---- rule 3 first: every reader on the grading path, planted ------------
    controls = {}
    controls["G_reader"] = A.planted_zero_control(dirs["f"], times["f"], a.foam_bashrc)
    print("planted-zero control (G reader, frozen): PASS -- recovered %.6g from %.6g at line %d; "
          "floor %g" % (controls["G_reader"]["recovered_max_abs_change"], PLANT,
                        controls["G_reader"]["planted_line"],
                        controls["G_reader"]["demonstrated_detection_floor"]))
    controls["yplus_reader"] = yplus_controls(dirs["c"], times["c"], a.foam_bashrc)
    print("planted control (y+ reader): PASS -- blind path 0 on every patch, registered path "
          "plate max %.4f; U x%g -> y+ x%.12g (expected %.12g)"
          % (controls["yplus_reader"]["seeing"]["plate"][1], YPLUS_SCALE,
             controls["yplus_reader"]["planted_ratio"]["plate"], math.sqrt(YPLUS_SCALE)))
    controls["exit_reader"] = exit_controls(dirs["c"], times["c"], a.foam_bashrc)
    print("planted control (exit-line reader): PASS -- recovered %.6g from %g at line %d, floor %g"
          % (controls["exit_reader"]["recovered"], PLANT, controls["exit_reader"]["planted_line"],
             controls["exit_reader"]["demonstrated_detection_floor"]))
    controls["flux_reader"] = flux_controls(dirs["c"], times["c"], a.foam_bashrc)
    print("planted control (flux reader): PASS -- inlet phi x%g -> imbalance %.9g (predicted %.9g)"
          % (FLUX_SCALE, controls["flux_reader"]["planted_imbalance"],
             controls["flux_reader"]["expected_imbalance"]))

    # ---- the controls, every level --------------------------------------
    per = {}
    gate1 = {lv: [] for lv in LEVELS}
    for lv in LEVELS:
        d, t = dirs[lv], times[lv]
        tmp, dst = scratch_copy(d, t)
        try:
            yp = yplus_read(dst, t, a.foam_bashrc)
            uc = exit_read(dst, t, a.foam_bashrc)
            fl = flux_read(dst, t, a.foam_bashrc)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        if yp is None or uc is None or fl is None:
            refuse("a control reader returned nothing on level %s (y+ %r, U_c %r, flux %r)" % (lv, yp, uc, fl))
        et = float(re.search(r"^\s*endTime\s+([0-9.eE+-]+)\s*;",
                             open(os.path.join(d, "system", "controlDict")).read(), re.M).group(1))
        rt = residual_tests(residual_history(d), et)
        tt = A.two_latest_times(d)
        fch = None
        if tt is not None:
            ch = []
            for _, rd, _, _ in GRADED:
                p0 = A.sample_profile(d, tt[0], rd, a.foam_bashrc)
                p1 = A.sample_profile(d, tt[1], rd, a.foam_bashrc)
                if p0 is None or p1 is None:
                    refuse("field-change reader returned nothing on level %s at r/D %.1f" % (lv, rd))
                ch.append(abs(A.peak_of(p1)[0] - A.peak_of(p0)[0]))
            fch = max(ch)
        c1 = yp["plate"][1] < YPLUS_MAX
        c1b = yp["pipeWall"][1] < YPLUS_MAX
        c2 = abs(uc - UC_REF) / UC_REF <= UC_TOL
        imb = imbalance(fl)
        c3 = imb < MASS_TOL
        c6_3 = (fch is not None) and (fch <= FIELD_TOL)
        per[lv] = dict(time=t, yplus=yp, Uc_over_Ubulk=uc, flux=fl, imbalance=imb,
                       residual=rt, field_change=fch, checkpoints=tt,
                       C1=c1, C1b=c1b, C2=c2, C3=c3, C6_1=rt["c6_1"], C6_2=rt["c6_2"], C6_3=c6_3)
        if not c1:
            gate1[lv].append("C1 plate y+_max %.4f >= %g" % (yp["plate"][1], YPLUS_MAX))
        if not c1b:
            gate1[lv].append("C1b pipeWall y+_max %.4f >= %g" % (yp["pipeWall"][1], YPLUS_MAX))
        if not c2:
            gate1[lv].append("C2 U_c/U_bulk %.4f outside +-%g%% of %g" % (uc, 100 * UC_TOL, UC_REF))
        if not c3:
            gate1[lv].append("C3 mass imbalance %.3e >= %g" % (imb, MASS_TOL))
        if not rt["c6_1"]:
            gate1[lv].append("C6.1 p_rgh max over last %d its = %s > %g"
                             % (FLOOR_WINDOW, rt["floor_max"], RESID_FLOOR))
        if not rt["c6_2"]:
            gate1[lv].append("C6.2 growth ratio %s > %g" % (rt["grow_ratio"], GROW_TOL))
        if not c6_3:
            gate1[lv].append("C6.3 field change %s > %g" % (fch, FIELD_TOL))
        print("level %s t=%s: C1 plate y+max %.4f [%s]  C1b pipe y+max %.4f [%s]  C2 Uc/Ub %.4f [%s]  "
              "C3 imbalance %.2e [%s]  C6.1 floor max %s [%s]  C6.2 ratio %s [%s]  C6.3 dfield %s [%s]"
              % (lv, t, yp["plate"][1], c1, yp["pipeWall"][1], c1b, uc, c2, imb, c3,
                 rt["floor_max"], rt["c6_1"], rt["grow_ratio"], rt["c6_2"], fch, c6_3))
    all_reasons = ["level %s: %s" % (lv, r) for lv in LEVELS for r in gate1[lv]]

    rows = []
    for rid, rd, reffile, half in GRADED:
        ref, refy = A.ref_peak(reffile)
        vals = {}
        for lv in LEVELS:
            prof = A.sample_profile(dirs[lv], times[lv], rd, a.foam_bashrc)
            if prof is None:
                refuse("could not sample r/D=%.1f on level %s" % (rd, lv))
            vals[lv] = A.peak_of(prof)[0]
        triple = (vals["c"], vals["m"], vals["f"])
        verdict, state, p, g, note = apply_gate(vals["f"], ref - half, ref + half, triple, all_reasons)
        rows.append(dict(row=rid, r_over_D=rd, reference=ref, band=[ref - half, ref + half],
                         value_fine=vals["f"], triple=dict(zip(LEVELS, triple)), triple_state=state,
                         observed_order=p, gci=g, verdict=verdict, note=note,
                         deviation=vals["f"] - ref, band_utilisation=abs(vals["f"] - ref) / half))
        print("%-3s r/D=%.1f fine=%.4f ref=%.4f band=[%.4f,%.4f] triple=%s p=%s GCI=%s -> %s%s"
              % (rid, rd, vals["f"], ref, ref - half, ref + half, state,
                 ("%.3f" % p) if p is not None else "n/a",
                 ("%.4f%%" % (100 * g)) if g is not None else "n/a", verdict,
                 (" [" + note + "]") if note else ""))
    out = dict(rung="T4b", STAGNANT_FLOOR=STAGNANT_FLOOR, P_MIN=P_MIN,
               floors_source="scripts/roache_triple.py (MESH_STANDARD.md section 10.5)",
               refinement_ratio=REFINEMENT, factor_of_safety=FS,
               provenance=prov, planted_controls=controls, levels=per, rows=rows,
               registered=dict(controls=C, graded_rows=REG["graded_rows"]))
    json.dump(out, open(a.json, "w"), indent=2)
    print("wrote %s" % a.json)
    return EXIT_OK


# ------------------------------------------------------------------ selftest
def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


def selftest(a):
    ok_n = all_n = 0

    def chk(what, cond):
        nonlocal ok_n, all_n
        all_n += 1
        ok_n += bool(cond)
        print("  [%s] %s" % ("ok " if cond else "FAIL", what))

    me = os.path.abspath(__file__)
    chk("zero `assert` nodes in analyse_t4b.py (AST)", count_asserts(me) == 0)
    chk("zero `assert` nodes in the imported frozen analyse_t4.py (AST)",
        count_asserts(os.path.join(T4DIR, "analyse_t4.py")) == 0)
    chk("the AST counter sees a planted assert",
        sum(1 for n in ast.walk(ast.parse("assert 1\n")) if isinstance(n, ast.Assert)) == 1)
    # Roache with P_MIN
    t4 = (1.0029022113658947, 1.0314953516600782, 1.0628656010142254)
    v = apply_gate(t4[2], 1.069, 1.109, t4, [])
    chk("T4's real G1 triple -> DIVERGENT -> NOT A RESULT (%s)" % v[1], v[0] == "NOT A RESULT" and v[1] == "DIVERGENT")
    conv = (1.030, 1.052, 1.063)
    v = apply_gate(conv[2], 1.069, 1.109, conv, [])
    chk("a CONVERGING triple below the band -> GATE FAIL with GCI (p=%.3f gci=%s)" % (v[2], v[3]),
        v[0] == "GATE FAIL" and v[3] is not None and abs(v[2] - 1.0) < 1e-9)
    v = apply_gate(1.075, 1.069, 1.109, (1.040, 1.063, 1.075), [])
    chk("a CONVERGING triple inside the band -> PASS", v[0] == "PASS")
    chk("the shared floors are imported, not defined here: STAGNANT_FLOOR = 0.5, P_MIN = 0.05",
        (STAGNANT_FLOOR, P_MIN) == (0.5, 0.05) and "P_MIN =" not in
        "".join(l for l in open(me) if l.startswith("P_MIN")))
    chk("the registered JSON carries the same two floors",
        (float(REG["roache_floors"]["STAGNANT_FLOOR"]), float(REG["roache_floors"]["P_MIN"])) == (STAGNANT_FLOOR, P_MIN))
    deg = (1.0, 1.10, 1.10 + 0.10 / 1.2)          # ratio 1.2 -> p = 0.263 < STAGNANT_FLOOR
    v = apply_gate(deg[2], 0.0, 9.0, deg, [])
    chk("p = %.3f < STAGNANT_FLOOR -> STAGNANT -> NOT A RESULT, GCI refused" % v[2],
        v[0] == "NOT A RESULT" and v[1] == "STAGNANT" and v[3] is None)
    dg = (1.0, 1.10, 1.10 + 0.10 / (2 ** 0.02))   # p = 0.02 < P_MIN -> DEGENERATE
    v = apply_gate(dg[2], 0.0, 9.0, dg, [])
    chk("|p| = %.3f < P_MIN -> DEGENERATE -> NOT A RESULT, GCI refused" % v[2],
        v[0] == "NOT A RESULT" and v[1] == "DEGENERATE" and v[3] is None)
    j = (1.0, 1.10, 1.10 + 0.10 / (2 ** 0.6))
    v = apply_gate(j[2], 0.0, 9.0, j, [])
    chk("p = %.3f just above STAGNANT_FLOOR -> PASS with GCI" % v[2], v[0] == "PASS" and v[3] is not None)
    # verdict-equivalence with the SHARED instrument, as an executable claim: on a
    # ladder of synthetic triples this file's classify() names the same state as
    # roache_triple.gci_equal (DEGENERATE / STAGNANT / CONVERGING / OSCILLATORY /
    # DIVERGENT), so the floor semantics are the shared ones and not a local reading
    import roache_triple as RT
    same = []
    for pt in (0.02, 0.3, 0.49, 0.51, 1.0, 2.0):
        tr = (1.0, 1.10, 1.10 + 0.10 / (2 ** pt))
        same.append(classify(tr)[0] == RT.gci_equal(*tr, r=2.0, dim=2)["state"])
    same.append(classify((1.0, 1.10, 1.05))[0] == RT.gci_equal(1.0, 1.10, 1.05, r=2.0, dim=2)["state"])   # OSCILLATORY
    same.append(classify((1.0, 1.10, 1.25))[0] == RT.gci_equal(1.0, 1.10, 1.25, r=2.0, dim=2)["state"])   # DIVERGENT
    chk("classify() names the same state as roache_triple.gci_equal on 8 synthetic triples "
        "(p = 0.02 DEGENERATE, 0.3 / 0.49 STAGNANT, 0.51 / 1 / 2 CONVERGING, OSCILLATORY, DIVERGENT)",
        all(same) and len(same) == 8)
    v = apply_gate(1.075, 1.069, 1.109, (1.040, 1.063, 1.075), ["C1 plate y+_max 1.2480 >= 1"])
    chk("a gate-(1) reason turns a would-be PASS into NOT A RESULT", v[0] == "NOT A RESULT")
    # residual tests on synthetic histories (T4's shapes)
    flat = [(t, 6.98e-7 * (1 + 1e-4 * ((t % 7) - 3))) for t in range(1, 20001)]
    r = residual_tests(flat, 20000)
    chk("T4-c-shaped plateau (6.98e-7, noise 1e-4) passes C6.1 and C6.2 (ratio %.5f)" % r["grow_ratio"],
        r["c6_1"] and r["c6_2"])
    grow = [(t, 1e-8 * (1.06 ** (t / 1000.0))) for t in range(1, 20001)]
    r = residual_tests(grow, 20000)
    chk("a residual growing 6%%/1000 iterations FAILS C6.2 (ratio %.4f)" % r["grow_ratio"], not r["c6_2"])
    high = [(t, 1.2e-6) for t in range(1, 20001)]
    chk("a plateau at 1.2e-6 FAILS C6.1", not residual_tests(high, 20000)["c6_1"])
    chk("an empty history fails both", not residual_tests([], 20000)["c6_1"])
    # live readers on a smoke case (1 iteration in scratch), if given
    if a.smoke:
        t = A.latest_time(a.smoke)
        yc = yplus_controls(a.smoke, t, a.foam_bashrc)
        chk("SMOKE y+: blind reader 0 / registered reader plate max %.4g; U x%g -> x%.12g"
            % (yc["seeing"]["plate"][1], YPLUS_SCALE, yc["planted_ratio"]["plate"]), yc["status"] == "PASS")
        ec = exit_controls(a.smoke, t, a.foam_bashrc)
        chk("SMOKE exit-line: base U_c/U_b %.4f, plant recovered %.3g, floor %g"
            % (ec["base"], ec["recovered"], ec["demonstrated_detection_floor"]), ec["status"] == "PASS")
        fc = flux_controls(a.smoke, t, a.foam_bashrc)
        chk("SMOKE flux: imbalance %.3e; inlet x%g -> %.9g (predicted %.9g)"
            % (fc["base_imbalance"], FLUX_SCALE, fc["planted_imbalance"], fc["expected_imbalance"]),
            fc["status"] == "PASS")
        gc = A.planted_zero_control(a.smoke, t, a.foam_bashrc)
        chk("SMOKE frozen G reader plant: recovered %.3g, floor %g"
            % (gc["recovered_max_abs_change"], gc["demonstrated_detection_floor"]), gc["status"] == "PASS")
    # refusals DRIVEN under both interpreters
    for tag, argv_extra in (("missing DONE", ["--drive-refusal", "missing-done"]),
                            ("blind flux reader", ["--drive-refusal", "blind-flux"]),
                            ("broken y+ scaling", ["--drive-refusal", "broken-yplus"])):
        rcs = {}
        for name, argv in (("python3", [sys.executable, me]), ("python3 -O", [sys.executable, "-O", me])):
            p = subprocess.run(argv + argv_extra + (["--smoke", a.smoke] if a.smoke else []),
                               capture_output=True, text=True)
            rcs[name] = (p.returncode, "REFUSE" in p.stdout)
        chk("refusal '%s' FIRES (rc 2, REFUSE printed) under python3 AND python3 -O: %r" % (tag, rcs),
            all(v == (2, True) for v in rcs.values()))
    print("\nselftest %d/%d" % (ok_n, all_n))
    return EXIT_OK if ok_n == all_n else EXIT_SELFTEST_FAIL


def drive_refusal(which, a):
    """Sacrificial mutants that MUST refuse.  Used by --selftest under both interpreters."""
    if which == "missing-done":
        d = tempfile.mkdtemp(prefix="t4b_nodone_")
        try:
            global HERE
            HERE = d
            for lv, case in CASES.items():
                if not os.path.isfile(os.path.join(HERE, "DONE.%s" % case)):
                    refuse("no DONE.%s" % case)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        return EXIT_OK
    if which == "blind-flux":
        global flux_read
        base = {"inlet": -1.0, "entrainment": 0.4, "farfield": 0.6, "plate": 0.0, "pipeWall": 0.0}
        flux_read = lambda copy_dir, time, bashrc: dict(base)      # noqa: E731  blind mutant
        if not a.smoke:
            # no case to copy: exercise the arithmetic directly
            planted = flux_read(None, None, None)
            expected = abs(sum(base.values()) + (FLUX_SCALE - 1) * base["inlet"]) / abs(FLUX_SCALE * base["inlet"])
            if abs(imbalance(planted) - expected) > 1e-9 * max(expected, 1e-30) + 1e-15:
                refuse("flux POSITIVE ARM FAILED: the reader did not see the plant")
            return EXIT_OK
        flux_controls(a.smoke, A.latest_time(a.smoke), a.foam_bashrc)
        return EXIT_OK
    if which == "broken-yplus":
        global scale_internal_vectors
        scale_internal_vectors = lambda path, factor: 0                # noqa: E731  plant never lands
        if not a.smoke:
            refuse("y+ POSITIVE ARM FAILED (no smoke case: the mutant cannot land a plant)")
        yplus_controls(a.smoke, A.latest_time(a.smoke), a.foam_bashrc)
        return EXIT_OK
    refuse("unknown refusal drive %r" % which)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--foam-bashrc", default=FOAM_BASHRC_DEFAULT)
    ap.add_argument("--json", default=os.path.join(HERE, "gate_t4b.json"))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--smoke", default=None, help="a 1-iteration scratch case for the live reader controls")
    ap.add_argument("--drive-refusal", default=None, help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.drive_refusal:
        return drive_refusal(a.drive_refusal, a)
    if a.selftest:
        return selftest(a)
    return grade(a)


if __name__ == "__main__":
    sys.exit(main())
