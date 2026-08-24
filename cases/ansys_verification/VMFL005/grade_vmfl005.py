#!/usr/bin/env python3
"""VMFL005 comparator -- Poiseuille flow in a pipe.

Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p. 25.
Reference: F. M. White, *Fluid Mechanics*, 3rd ed., McGraw-Hill, 1994
(Hagen-Poiseuille, analytical).

THIS FILE IS THE GRADING PATH.  It is committed BEFORE the pre-registration
that cites it by sha, and before any solver runs (CLAUDE.md rule 2;
VERIFICATION_CHARTER section 2d).  Nothing in it may change once the first
graded solve has started; instrumentation that is not on the grading path may
be added later only with a dated disclosure in RESULTS.md.

It REFUSES (exit 2) rather than degrades.  Every refusal names the clause.

The gated quantity is the PRESSURE DROP, read from two surfaceFieldValue
function objects (areaAverage(p) over the inlet and outlet patches).  The reader
is built directly against the v2606 writer source, NOT a belief about it
(the lesson of VMFL001 run 1 = N-AV4 / L-286):

  * output path  postProcessing/<foName>/<startTime>/surfaceFieldValue.dat
    -- src/OpenFOAM/db/functionObjects/writeFile/writeFile.C, baseFileDir()
       (globalPath()/"postProcessing"), baseTimeDir()=prefix_/timeName, and
       src/functionObjects/field/fieldValues/fieldValue/fieldValue.C:56 which
       passes the object NAME as prefix_ and the valueType "surfaceFieldValue"
       as the base file name; startTime dir = 0.
  * header    lines prefixed "# " (writeCommented), last header line
              "# Time <tab> areaAverage(p)"
    -- surfaceFieldValue.C writeFileHeader (~:712-755).
  * data      one "<time> <tab> <value>" row per write, at the object's
              writePrecision (we set 12 in controlDict; writeFile::read honours
              "writePrecision", writeFile.C:248)
    -- surfaceFieldValueTemplates.C writeValues (~:519/527), writeCurrentTime
       writeFile.C:360.

    python3 grade_vmfl005.py                 # grade the run tree
    python3 grade_vmfl005.py --selftest      # reader, plant, classifier, gate
                                             # on synthetic data; no run tree
    python3 grade_vmfl005.py --dryrun-reader <surfaceFieldValue.dat>
                                             # parse a REAL file, print row count
                                             # only -- NEVER a value
"""

import glob
import json
import math
import os
import re
import shutil
import sys
import tempfile

# ---------------------------------------------------------------------------
# THE FROZEN GRADING PATH -- references, bands, verdict rules
# ---------------------------------------------------------------------------
CASE = "VMFL005"
MANUAL_PAGE = "25"

RHO = 1.0                   # kg/m3                            (manual p. 25)
MU = 1.0e-5                 # kg/m-s                           (manual p. 25)
NU = MU / RHO               # m2/s -- what simpleFoam is given (1e-5)
L = 0.1                     # m, pipe length                  (manual p. 25)
R = 0.00125                 # m, pipe radius                  (manual p. 25)
VAVG = 2.0                  # m/s, average inlet velocity     (manual p. 25)
RE_NOMINAL = 500.0          # Reynolds number on the diameter (manual p. 25)

# manual Table .05.1 (Ansys Fluent) and .05.2 (Ansys CFX), pressure drop [Pa]:
MANUAL_TARGET_DP = 10.24    # Pa, "Target" (Hagen-Poiseuille), THE GATE reference
ANSYS_FLUENT_DP = 10.22     # Pa, ratio 0.998 -- CONTEXT ONLY, never the gate
ANSYS_CFX_DP = 10.49        # Pa, ratio 1.024 -- CONTEXT ONLY, never the gate

TOL_GATE = 0.02             # THE GATE: relative, against the MANUAL's target
TOL_DIAG = 0.01             # DIAGNOSTIC only: relative, against the exact formula

FS = 1.25                   # Roache factor of safety, three-grid
RATIO = 2.0                 # refinement ratio, both directions, exact

PLANT = 1.234               # Pa, planted-zero control perturbation
PLANT_TOL = 1e-9            # Pa, read-back tolerance (12 s.f. on ~10 Pa)

RES_TOL = 1e-6              # initial residual at the final iteration (Ux Uy p)
PLATEAU_TOL = 1e-4          # Pa, peak-to-peak of the inlet-pressure series over
PLATEAU_FRAC = 0.20         # the last 20 % (~1e-5 relative to dP ~ 10.24 Pa)

# Roache classification thresholds, written down so they cannot be chosen later:
EPS_ABS = 1e-12             # Pa: a level-to-level difference below this is zero
STAG_TOL = 1e-3             # |R - 1| <= STAG_TOL  =>  STAGNANT

# per-level endTime (SIMPLE iterations).  ESTIMATE, fixed before any run, from
# VMFL001's measured convergence-rate-vs-cell-count (VMFL001 R1 log: ~1000-cell
# level < 1e-12 by 3000; ~16000-cell level needed ~6000 to clear 1e-6).  VMFL005
# L3 (16000 cells) ~ VMFL001 L3 (16384) -> 6000.  The residual < RES_TOL clause
# is the ACTUAL arbiter: if a level misses it at its endTime the rung is NOT A
# RESULT and re-runs as a new rung (as VMFL001 R1 -> R2).  See PREREGISTRATION.md
# section 4.
ENDTIME_BY_LEVEL = {"L1_100x10": 2000, "L2_200x20": 3000, "L3_400x40": 6000}

LEVELS = (                  # coarse -> fine; name, axial cells, radial cells
    ("L1_100x10", 100, 10),
    ("L2_200x20", 200, 20),
    ("L3_400x40", 400, 40),
)

PINLET_FO = "pInletMonitor"
POUTLET_FO = "pOutletMonitor"
SFV_FILE = "surfaceFieldValue.dat"

RUN_ROOT = "/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL005"
OUT_JSON = os.path.join(RUN_ROOT, "GRADING_VMFL005.json")

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


def refuse(msg):
    print("REFUSE: " + msg, file=sys.stderr)
    sys.exit(2)


def _endtime_for(level_dir):
    name = os.path.basename(level_dir.rstrip("/"))
    if name not in ENDTIME_BY_LEVEL:
        refuse("no registered endTime for level %r" % name)
    return ENDTIME_BY_LEVEL[name]


# ---------------------------------------------------------------------------
# the reference: exact Hagen-Poiseuille pressure drop, White (analytical)
# ---------------------------------------------------------------------------
def dp_exact():
    """dP = 8 mu L Vavg / R^2  ==  8 mu L Q / (pi R^4), Q = Vavg pi R^2.
    Both forms are identical; returned in Pa (multiply by RHO=1)."""
    return 8.0 * MU * L * VAVG / R**2


def dp_exact_via_Q():
    """The 8 mu L Q / (pi R^4) form, computed independently as a cross-check."""
    Q = VAVG * math.pi * R**2
    return RHO * 8.0 * MU * L * Q / (math.pi * R**4)


def reynolds():
    return RHO * VAVG * (2.0 * R) / MU


# ---------------------------------------------------------------------------
# the reader: v2606 surfaceFieldValue.dat (see module docstring for provenance)
# ---------------------------------------------------------------------------
def find_sfv_file(level_dir, fo_name):
    """postProcessing/<fo_name>/<startTime>/surfaceFieldValue.dat -- exactly one
    hit is required.  Never guesses."""
    pat = os.path.join(level_dir, "postProcessing", fo_name, "*", SFV_FILE)
    hits = sorted(glob.glob(pat))
    if len(hits) > 1:
        refuse("ambiguous surfaceFieldValue files for %r in %s: %s"
               % (fo_name, level_dir, ", ".join(hits)))
    if len(hits) != 1:
        refuse("no surfaceFieldValue.dat for function object %r under "
               "%s/postProcessing (expected one "
               "postProcessing/%s/<startTime>/%s)"
               % (fo_name, level_dir, fo_name, SFV_FILE))
    return hits[0]


def read_sfv(path):
    """Parse a v2606 surfaceFieldValue.dat.  Returns [(time, value), ...].

    Header lines are prefixed '#' and skipped.  Every data line is
    '<time> <tab> <value>' -- split on whitespace, first token is the time,
    second is the scalar areaAverage.  A data line with fewer than two numeric
    columns is REFUSED (never guessed), and a file with no data rows is REFUSED.
    """
    if not os.path.isfile(path):
        refuse("surfaceFieldValue file does not exist: " + path)
    rows = []
    for line in open(path, errors="replace"):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) < 2:
            refuse("data row has %d columns, expected >= 2 (time value) in %s: %r"
                   % (len(parts), path, s))
        try:
            t = float(parts[0])
            v = float(parts[1])
        except ValueError:
            refuse("unparseable data row in %s: %r" % (path, s))
        rows.append((t, v))
    if not rows:
        refuse("no data rows in " + path)
    return rows


def sfv_at_endtime(level_dir, fo_name):
    """The areaAverage value at this level's endTime (exactly one matching row)."""
    path = find_sfv_file(level_dir, fo_name)
    rows = read_sfv(path)
    endtime = _endtime_for(level_dir)
    match = [v for (t, v) in rows if abs(t - endtime) < 1e-6]
    if len(match) != 1:
        refuse("expected exactly one row at endTime %d in %s, found %d"
               % (endtime, path, len(match)))
    return match[0], path


def pressure_drop(level_dir):
    """dP = RHO * (areaAverage(p)_inlet - areaAverage(p)_outlet) at endTime [Pa]."""
    p_in, src_in = sfv_at_endtime(level_dir, PINLET_FO)
    p_out, src_out = sfv_at_endtime(level_dir, POUTLET_FO)
    dp = RHO * (p_in - p_out)
    return dict(dp=dp, p_inlet=p_in, p_outlet=p_out,
                source_inlet=os.path.relpath(src_in, RUN_ROOT),
                source_outlet=os.path.relpath(src_out, RUN_ROOT))


# ---------------------------------------------------------------------------
# planted-zero control (CLAUDE.md rule 3)
# ---------------------------------------------------------------------------
def _plant_into_sfv(path, endtime, plant):
    """Add `plant` to the value column of the endTime row, IN PLACE, then read
    back FROM DISK.  Returns (before, after)."""
    lines = open(path).read().split("\n")
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) < 2:
            continue
        if abs(float(parts[0]) - endtime) < 1e-6:
            before = float(parts[1])
            parts[1] = repr(before + plant)
            lines[i] = "\t".join(parts)
            open(path, "w").write("\n".join(lines))
            back = None
            for l2 in open(path).read().split("\n"):
                s2 = l2.strip()
                if not s2 or s2.startswith("#"):
                    continue
                p2 = s2.split()
                if len(p2) >= 2 and abs(float(p2[0]) - endtime) < 1e-6:
                    back = float(p2[1])
                    break
            if back is None:
                raise RuntimeError("planted row could not be re-read from " + path)
            if abs((back - before) - plant) > PLANT_TOL:
                raise RuntimeError("plant did not land: %r -> %r" % (before, back))
            return before, back
    raise RuntimeError("no row at endTime %d in %s" % (endtime, path))


def planted_zero_control(level_dir):
    """Copy the inlet monitor to a temp tree, plant PLANT into its endTime value,
    read it back from disk, and run the SAME extraction.  The extracted pressure
    drop must move by exactly PLANT -- otherwise a small number the reader
    returns on the real case would be a statement about the reader, not the
    fields.  The run tree is never modified (only the temp copy)."""
    endtime = _endtime_for(level_dir)
    src = find_sfv_file(level_dir, PINLET_FO)
    p_out, _ = sfv_at_endtime(level_dir, POUTLET_FO)
    before_dp = pressure_drop(level_dir)["dp"]
    tmp = tempfile.mkdtemp(prefix="vmfl005plant_")
    try:
        work = os.path.join(tmp, SFV_FILE)
        shutil.copy(src, work)
        before, after = _plant_into_sfv(work, endtime, PLANT)
        rows = read_sfv(work)
        planted_p_in = [v for (t, v) in rows if abs(t - endtime) < 1e-6][0]
        seen_dp = RHO * (planted_p_in - p_out)
        moved = seen_dp - before_dp
        return dict(passed=abs(moved - PLANT) <= PLANT_TOL,
                    planted=PLANT, read_back_delta=after - before,
                    reader_dp_delta=moved, file=os.path.basename(src))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# strict completion rule (CLAUDE.md rule 4), adapted for simpleFoam / VMFL005
# ---------------------------------------------------------------------------
def _time_dirs(level_dir):
    out = []
    for d in os.listdir(level_dir):
        if os.path.isdir(os.path.join(level_dir, d)) and re.fullmatch(r"\d+(\.\d+)?", d):
            out.append(d)
    return sorted(out, key=float)


def strict_completion(level_dir):
    name = os.path.basename(level_dir)
    endtime = _endtime_for(level_dir)
    if not os.path.isdir(level_dir):
        refuse("%s: run directory does not exist" % name)

    rc_path = os.path.join(level_dir, "RUN_RC.txt")
    if not os.path.isfile(rc_path):
        refuse("%s: no RUN_RC.txt -- the run script did not finish this level" % name)
    m = re.search(r"^rc=(-?\d+)$", open(rc_path).read(), re.M)
    if not m:
        refuse("%s: RUN_RC.txt carries no rc" % name)
    rc = int(m.group(1))
    if rc != 0:
        refuse("%s: rc = %d (strict completion clause 1)" % (name, rc))

    log = os.path.join(level_dir, "log.simpleFoam")
    if not os.path.isfile(log):
        refuse("%s: no log.simpleFoam" % name)
    text = open(log, errors="replace").read()
    if not re.search(r"^End\s*$", text, re.M):
        refuse("%s: no 'End' line in log.simpleFoam (clause 2)" % name)

    times = _time_dirs(level_dir)
    if not times or float(times[-1]) != float(endtime):
        refuse("%s: last time is %r, endTime is %d (clause 3)"
               % (name, times[-1] if times else None, endtime))
    tdir = os.path.join(level_dir, times[-1])
    for f in ("U", "p"):
        if not os.path.isfile(os.path.join(tdir, f)):
            refuse("%s: field %s missing at endTime (clause 4)" % (name, f))

    n_exec = len(re.findall(r"^ExecutionTime = ", text, re.M))
    if n_exec != endtime:
        refuse("%s: %d ExecutionTime lines, endTime is %d (clause 5)"
               % (name, n_exec, endtime))

    marker = os.path.join(level_dir, "0", "U")
    if not os.path.isfile(marker):
        refuse("%s: no 0/U age-guard marker (clause 6)" % name)
    t_marker = os.path.getmtime(marker)
    for f in ("U", "p"):
        t_f = os.path.getmtime(os.path.join(tdir, f))
        if not t_f > t_marker:
            refuse("%s: endTime/%s (%.3f) is NOT newer than 0/U (%.3f) -- AGE GUARD "
                   "(clause 6): this field was not produced by the run that was "
                   "allowed to answer" % (name, f, t_f, t_marker))

    return dict(rc=rc, endTime=float(times[-1]), n_exec=n_exec,
                fields_at_endTime=["U", "p"], age_guard="fields newer than 0/U",
                times=times)


# ---------------------------------------------------------------------------
# iterative convergence: residuals AND an inlet-pressure plateau
# ---------------------------------------------------------------------------
RES_RE = re.compile(r"Solving for (\w+),\s+Initial residual = ([0-9eE.+-]+)")


def residual_history(level_dir):
    text = open(os.path.join(level_dir, "log.simpleFoam"), errors="replace").read()
    hist = {}
    for fld, val in RES_RE.findall(text):
        hist.setdefault(fld, []).append(float(val))
    return hist


def iterative_convergence(level_dir):
    name = os.path.basename(level_dir)
    hist = residual_history(level_dir)
    finals = {}
    for fld in ("Ux", "Uy", "p"):
        if fld not in hist or not hist[fld]:
            refuse("%s: no residual history for %s" % (name, fld))
        finals[fld] = hist[fld][-1]
    uz_final = hist["Uz"][-1] if hist.get("Uz") else None   # reported, not gated
    res_ok = all(v < RES_TOL for v in finals.values())

    rows = read_sfv(find_sfv_file(level_dir, PINLET_FO))
    vals = [v for (_, v) in rows]
    if len(vals) < 10:
        refuse("%s: inlet-pressure series too short (%d samples)" % (name, len(vals)))
    n = max(2, int(round(PLATEAU_FRAC * len(vals))))
    tail = vals[-n:]
    ptp = max(tail) - min(tail)
    plateau_ok = ptp < PLATEAU_TOL

    return dict(final_residuals=finals, uz_final_residual=uz_final,
                residual_tol=RES_TOL, residuals_ok=res_ok,
                plateau_ptp=ptp, plateau_tol=PLATEAU_TOL, plateau_n=n,
                plateau_ok=plateau_ok, converged=(res_ok and plateau_ok),
                inlet_p_last=vals[-1])


# ---------------------------------------------------------------------------
# Roache triple (CLAUDE.md rule 5), thresholds fixed above
# ---------------------------------------------------------------------------
def roache(f_coarse, f_med, f_fine, ratio=RATIO, fs=FS):
    d21 = f_med - f_fine        # medium - fine
    d32 = f_coarse - f_med      # coarse - medium
    out = dict(f_coarse=f_coarse, f_med=f_med, f_fine=f_fine,
               d21=d21, d32=d32, ratio=ratio, fs=fs,
               p=None, R=None, gci_fine=None, f_extrapolated=None)

    if abs(d21) < EPS_ABS and abs(d32) < EPS_ABS:
        out["state"] = "EXACT"
        return out
    if abs(d32) < EPS_ABS:
        out["state"] = "DIVERGENT"
        out["why"] = ("the coarse-medium difference is below %g Pa while the "
                      "medium-fine difference is not" % EPS_ABS)
        return out

    R_ = d21 / d32
    out["R"] = R_
    if R_ < 0:
        out["state"] = "OSCILLATORY"
        return out
    if abs(R_ - 1.0) <= STAG_TOL:
        out["state"] = "STAGNANT"
        return out
    if R_ > 1.0:
        out["state"] = "DIVERGENT"
        return out

    p = math.log(1.0 / R_) / math.log(ratio)
    out["p"] = p
    out["state"] = "CONVERGING"
    denom = ratio**p - 1.0
    if denom <= 0:
        out["state"] = "DIVERGENT"
        out["why"] = "r^p - 1 <= 0"
        return out
    out["gci_fine"] = fs * abs(d21 / f_fine) / denom
    out["f_extrapolated"] = f_fine + (f_fine - f_med) / denom
    return out


# ---------------------------------------------------------------------------
# levers verified active (VERIFICATION_CHARTER section 9); three-valued
# ---------------------------------------------------------------------------
def levers(level_dir, n_axial, n_radial):
    name = os.path.basename(level_dir)
    out = {}

    tp = os.path.join(level_dir, "constant", "transportProperties")
    if not os.path.isfile(tp):
        refuse("%s: no constant/transportProperties" % name)
    m = re.search(r"^\s*nu\s+([0-9eE.+-]+)\s*;", open(tp).read(), re.M)
    if not m:
        refuse("%s: nu not readable from constant/transportProperties" % name)
    nu_ran = float(m.group(1))
    if abs(nu_ran - NU) > 1e-15:
        refuse("%s: nu = %g in the run, %g was registered" % (name, nu_ran, NU))
    out["nu"] = nu_ran

    u0 = os.path.join(level_dir, "0", "U")
    txt = open(u0).read()
    if "codedFixedValue" not in txt or "poiseuilleInlet" not in txt:
        refuse("%s: inlet is not the codedFixedValue poiseuilleInlet in 0/U" % name)
    out["inlet"] = "codedFixedValue poiseuilleInlet"

    log = open(os.path.join(level_dir, "log.simpleFoam"), errors="replace").read()
    out["laminar"] = "active-in-log" if "laminar" in log else "unverifiable-from-logs"
    out["wedge_in_log"] = ("wedge" in log)

    cm = os.path.join(level_dir, "log.checkMesh")
    if os.path.isfile(cm):
        ctext = open(cm, errors="replace").read()
        m = re.search(r"^\s*cells:\s+(\d+)", ctext, re.M)
        expect = n_axial * n_radial
        if not m:
            out["mesh"] = "unverifiable-from-logs (no cell count in log.checkMesh)"
        elif int(m.group(1)) != expect:
            refuse("%s: checkMesh reports %s cells, the level is %d x %d = %d"
                   % (name, m.group(1), n_axial, n_radial, expect))
        else:
            out["mesh"] = dict(cells=int(m.group(1)), mesh_ok=("Mesh OK" in ctext))
    else:
        out["mesh"] = "unverifiable-from-logs (no log.checkMesh)"
    return out


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    exact = dp_exact()

    print("=" * 78)
    print("%s -- Poiseuille flow in a pipe" % CASE)
    print("Ansys Fluid Dynamics Verification Manual 2026 R1, p. %s" % MANUAL_PAGE)
    print("reference: White, Fluid Mechanics 3rd ed. (Hagen-Poiseuille, analytical)")
    print("=" * 78)
    print("  Reynolds number (rho Vavg D / mu)          %10.4f  (manual: 500)"
          % reynolds())
    print("  manual target dP (Table .05.1)             %10.4f Pa" % MANUAL_TARGET_DP)
    print("  Ansys Fluent %6.2f Pa (ratio 0.998), CFX %6.2f Pa (ratio 1.024) [context]"
          % (ANSYS_FLUENT_DP, ANSYS_CFX_DP))
    print("  exact Hagen-Poiseuille  8 mu L Vavg / R^2  %s Pa (6 s.f.)"
          % format(exact, ".6g"))
    print("  exact via 8 mu L Q/(pi R^4) cross-check    %s Pa" % format(dp_exact_via_Q(), ".6g"))

    results, completion, conv = {}, {}, {}
    for name, nx, nr in LEVELS:
        d = os.path.join(RUN_ROOT, name)
        completion[name] = strict_completion(d)
        completion[name]["levers"] = levers(d, nx, nr)
        conv[name] = iterative_convergence(d)
        pd = pressure_drop(d)
        results[name] = dict(pd, cells=nx * nr)

    # ---- planted-zero control, on the level the verdict is taken from --------
    fine = LEVELS[-1][0]
    pz = planted_zero_control(os.path.join(RUN_ROOT, fine))
    print("\nplanted-zero control on %s: %s" % (fine, pz))
    if not pz.get("passed"):
        refuse("planted-zero control failed: the reader cannot see a %g Pa "
               "difference planted on disk; its numbers mean nothing" % PLANT)

    # ---- verdict, in the order rule 5 fixes ---------------------------------
    not_converged = [n for n in conv if not conv[n]["converged"]]
    f_c = results[LEVELS[0][0]]["dp"]
    f_m = results[LEVELS[1][0]]["dp"]
    f_f = results[LEVELS[2][0]]["dp"]
    triple = roache(f_c, f_m, f_f)

    dp_fine = results[fine]["dp"]
    rel_manual = abs(dp_fine - MANUAL_TARGET_DP) / abs(MANUAL_TARGET_DP)
    rel_exact = abs(dp_fine - exact) / abs(exact)
    gate_ok = rel_manual <= TOL_GATE
    diagnostic_ok = rel_exact <= TOL_DIAG

    if not_converged:
        verdict = "NOT A RESULT"
        why = "iterative convergence not met at: " + ", ".join(sorted(not_converged))
    elif triple["state"] != "CONVERGING":
        verdict = "NOT A RESULT"
        why = "grid triple is %s, not CONVERGING (rule 5 step 2)" % triple["state"]
    else:
        verdict = "PASS" if gate_ok else "GATE FAIL"
        why = ("dP within %.1f %% of the manual target" % (TOL_GATE * 100) if gate_ok
               else "dP outside %.1f %% of the manual target" % (TOL_GATE * 100))
    assert verdict in VERDICTS

    print("\n--- gate: |dP_lab - dP_manual| / |dP_manual| <= %.3f, at %s ---"
          % (TOL_GATE, fine))
    print("  dP_lab %10.6f Pa   manual %8.4f Pa   dev %6.3f %%  %s"
          % (dp_fine, MANUAL_TARGET_DP, rel_manual * 100, "ok" if gate_ok else "OUT"))
    print("  vs exact %10.6f Pa   dev %6.3f %%  %s (diagnostic, tol %.1f %%)"
          % (exact, rel_exact * 100, "ok" if diagnostic_ok else "out",
             TOL_DIAG * 100))
    print("  per level: coarse %s  medium %s  fine %s"
          % (format(f_c, ".6g"), format(f_m, ".6g"), format(f_f, ".6g")))
    print("\n--- Roache triple on dP, ratio %.1f, Fs %.2f ---" % (RATIO, FS))
    print("  state %s  R %s  p %s  GCI_fine %s"
          % (triple["state"],
             "n/a" if triple["R"] is None else "%.6f" % triple["R"],
             "n/a" if triple["p"] is None else "%.4f" % triple["p"],
             "n/a" if triple["gci_fine"] is None else "%.4e" % triple["gci_fine"]))
    print("\nVERDICT: %s -- %s" % (verdict, why))

    payload = dict(case=CASE, manual_page=MANUAL_PAGE, verdict=verdict, why=why,
                   gate=dict(tol=TOL_GATE, dp_fine=dp_fine,
                             manual_target=MANUAL_TARGET_DP,
                             rel_vs_manual=rel_manual, passed=gate_ok),
                   diagnostic=dict(tol=TOL_DIAG, exact=exact, rel_vs_exact=rel_exact,
                                   ok=diagnostic_ok, exact_via_Q=dp_exact_via_Q()),
                   reynolds=reynolds(),
                   ansys_context=dict(fluent=ANSYS_FLUENT_DP, cfx=ANSYS_CFX_DP),
                   triple=triple, levels=results, completion=completion,
                   iterative_convergence=conv, planted_zero=pz,
                   comparator=os.path.abspath(__file__))
    os.makedirs(RUN_ROOT, exist_ok=True)
    with open(OUT_JSON, "w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True, default=str)
    print("grading written to %s" % OUT_JSON)
    return 0


# ---------------------------------------------------------------------------
# self-test: reader, plant (both arms), classifier, gate -- synthetic, no solver
# ---------------------------------------------------------------------------
def _write_fixture(path, endtime, endvalue, ramp=True):
    """Write a surfaceFieldValue.dat in the REAL v2606 format: a '# '-prefixed
    header block, then '<time>\\t<value>' data rows, the last at endtime."""
    with open(path, "w") as fh:
        fh.write("# Region type : patch inlet\n")
        fh.write("# Faces : 10\n")
        fh.write("# Area : 4.90873852123405e-06\n")
        fh.write("# Scale factor : 1\n")
        fh.write("# Time            \tareaAverage(p)\n")
        n = 20
        for i in range(1, n + 1):
            t = int(round(endtime * i / n))
            v = endvalue if not ramp else endvalue * (0.5 + 0.5 * i / n)
            fh.write("%d\t%r\n" % (t, v))


def selftest():
    ok = True

    def check(label, cond, detail=""):
        nonlocal ok
        print("  [%s] %s%s" % ("PASS" if cond else "FAIL", label,
                               "" if not detail else "  <- " + str(detail)))
        ok = ok and bool(cond)

    print("--- selftest: exact formula and Reynolds number ---")
    check("dP_exact == 10.2400 Pa (6 s.f.)", abs(dp_exact() - 10.24) < 5e-4, dp_exact())
    check("the two exact forms agree", abs(dp_exact() - dp_exact_via_Q()) < 1e-12)
    check("Reynolds number == 500", abs(reynolds() - 500.0) < 1e-9, reynolds())
    check("manual target equals the exact value to its printed precision",
          abs(MANUAL_TARGET_DP - dp_exact()) < 5e-3, dp_exact())

    tmp = tempfile.mkdtemp(prefix="vmfl005self_")
    try:
        print("--- selftest: reader on the REAL v2606 surfaceFieldValue.dat format ---")
        f = os.path.join(tmp, SFV_FILE)
        _write_fixture(f, 6000, 10.2384, ramp=False)
        rows = read_sfv(f)
        check("reader parses the headerless-data rows (20 rows)", len(rows) == 20, len(rows))
        end = [v for (t, v) in rows if abs(t - 6000) < 1e-6]
        check("reader recovers the endTime value", len(end) == 1 and abs(end[0] - 10.2384) < 1e-12)

        print("--- selftest: reader refuses a one-column data row ---")

        def refuses(fn):
            pid = os.fork()
            if pid == 0:
                devnull = os.open(os.devnull, os.O_WRONLY)
                os.dup2(devnull, 2)
                try:
                    fn()
                except SystemExit as e:
                    os._exit(e.code if isinstance(e.code, int) else 1)
                os._exit(0)
            _, status = os.waitpid(pid, 0)
            return os.WIFEXITED(status) and os.WEXITSTATUS(status) == 2

        bad = os.path.join(tmp, "bad.dat")
        open(bad, "w").write("# Time areaAverage(p)\n6000\n")   # value column missing
        check("a data row with < 2 columns is REFUSED with exit 2",
              refuses(lambda: read_sfv(bad)))

        print("--- selftest: planted-zero, positive arm ---")
        work = os.path.join(tmp, "plant.dat")
        _write_fixture(work, 6000, 10.2384, ramp=False)
        before = [v for (t, v) in read_sfv(work) if abs(t - 6000) < 1e-6][0]
        b, a = _plant_into_sfv(work, 6000, PLANT)
        after = [v for (t, v) in read_sfv(work) if abs(t - 6000) < 1e-6][0]
        check("the reader sees the planted %g Pa at endTime" % PLANT,
              abs((after - before) - PLANT) <= PLANT_TOL, after - before)

        print("--- selftest: planted-zero, negative arm (no plant, no signal) ---")
        work2 = os.path.join(tmp, "noplant.dat")
        _write_fixture(work2, 6000, 10.2384, ramp=False)
        v2 = [v for (t, v) in read_sfv(work2) if abs(t - 6000) < 1e-6][0]
        check("an unplanted copy shows no change", abs(v2 - before) < 1e-15)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("--- selftest: Roache classifier ---")
    # first-order synthetic (the half-cell axial bias is O(h)): f(h)=f_ex + C h
    fex, C = 10.24, 0.05
    t = roache(fex + C * 4, fex + C * 2, fex + C * 1)   # h = 4,2,1
    check("first-order family -> CONVERGING", t["state"] == "CONVERGING", t["state"])
    check("observed order p == 1 to 1e-9", abs(t["p"] - 1.0) < 1e-9, t["p"])
    check("Richardson extrapolation recovers f_exact",
          abs(t["f_extrapolated"] - fex) < 1e-9, t["f_extrapolated"])
    # second-order synthetic: f(h)=f_ex + C h^2
    t2 = roache(fex + C * 16, fex + C * 4, fex + C * 1)
    check("second-order family -> CONVERGING, p == 2", t2["state"] == "CONVERGING"
          and abs(t2["p"] - 2.0) < 1e-9, t2["p"])
    check("divergent family -> DIVERGENT", roache(1.0, 1.1, 1.4)["state"] == "DIVERGENT")
    check("oscillatory family -> OSCILLATORY", roache(1.0, 1.2, 1.0)["state"] == "OSCILLATORY")
    check("equal-step family -> STAGNANT", roache(1.0, 1.1, 1.2)["state"] == "STAGNANT")
    check("identical values -> EXACT", roache(2.5, 2.5, 2.5)["state"] == "EXACT")

    print("--- selftest: the gate can fail, and can pass ---")
    lab_bad = MANUAL_TARGET_DP * 1.025
    lab_good = MANUAL_TARGET_DP * 1.015
    check("+2.5 %% is outside the gate",
          abs(lab_bad - MANUAL_TARGET_DP) / MANUAL_TARGET_DP > TOL_GATE)
    check("+1.5 %% is inside the gate",
          abs(lab_good - MANUAL_TARGET_DP) / MANUAL_TARGET_DP <= TOL_GATE)

    print("\nSELFTEST: %s" % ("all checks passed" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# --dryrun-reader: run the reader on a REAL run file and print ONLY whether it
# parsed and the row count, NEVER a value.  The pre-freeze external-reader check
# that VMFL001 run 1 taught us to do (N-AV4 / L-286): the reader had never seen a
# real v2606 file, so its format assumption went undetected until it refused at
# grade time.
# ---------------------------------------------------------------------------
def dryrun_reader(path):
    rows = read_sfv(path)
    print("dryrun-reader: parsed, %d rows" % len(rows))
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--dryrun-reader" in sys.argv:
        i = sys.argv.index("--dryrun-reader")
        sys.exit(dryrun_reader(sys.argv[i + 1]))
    sys.exit(main())
