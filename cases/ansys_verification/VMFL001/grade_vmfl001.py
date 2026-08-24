#!/usr/bin/env python3
"""VMFL001 comparator -- flow between rotating and stationary concentric cylinders.

Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p. 15-16.
Reference: F. M. White, *Viscous Fluid Flow*, section 3-2.3 (analytical).

THIS FILE IS THE GRADING PATH.  It is committed BEFORE the pre-registration that
cites it by sha, and before any solver runs (CLAUDE.md rule 2;
VERIFICATION_CHARTER section 2d).  Nothing in it may change once the first
graded solve has started; instrumentation that is not on the grading path may be
added later only with a dated disclosure in RESULTS.md.

It REFUSES (exit 2) rather than degrades.  Every refusal names the clause.

    python3 grade_vmfl001.py            # grade the run tree
    python3 grade_vmfl001.py --selftest # exercise reader, plant, classifier, gate
                                        # on synthetic data; no run tree needed
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
# THE FROZEN GRADING PATH -- bands, references, row definitions, verdict rules
# ---------------------------------------------------------------------------
CASE = "VMFL001"
MANUAL_PAGES = "15-16"

OMEGA = 1.0                 # rad/s, inner cylinder            (manual p. 15)
R_I = 0.0178                # m, inner radius                  (manual p. 15)
R_O = 0.04628               # m, outer radius                  (manual p. 15)
RHO = 1.0                   # kg/m3                            (manual p. 15)
MU = 2.0e-4                 # kg/m-s                           (manual p. 15)
NU = MU / RHO               # m2/s -- what simpleFoam is given

RADII = (0.020, 0.025, 0.030, 0.035)                    # m, manual table .01.1
MANUAL_TARGET = {0.020: 0.0151, 0.025: 0.0105,
                 0.030: 0.0072, 0.035: 0.0046}          # m/s, manual "Target"

TOL_GATE = 0.02             # THE GATE: relative, against the MANUAL's target
TOL_DIAG = 0.005            # DIAGNOSTIC only: relative, against the exact formula

TRIPLE_RADIUS = 0.035       # m -- the manual's worst-agreement point
FS = 1.25                   # Roache factor of safety, three-grid
RATIO = 2.0                 # refinement ratio, both directions, exact

PLANT = 1.234e-3            # m/s, planted-zero control perturbation
PLANT_TOL = 1e-15           # m/s, read-back tolerance on the plant

ENDTIME = 3000              # iterations; controlDict endTime, no residualControl
RES_TOL = 1e-6              # initial residual at the final iteration, all of Ux Uy p
PLATEAU_TOL = 1e-6          # m/s, peak-to-peak of the probe over the last 20 %
PLATEAU_FRAC = 0.20

# Roache classification thresholds, written down so they cannot be chosen later:
EPS_ABS = 1e-12             # m/s: a level-to-level difference below this is zero
STAG_TOL = 1e-3             # |R - 1| <= STAG_TOL  =>  STAGNANT

LEVELS = (                  # coarse -> fine; name, radial cells, azimuthal cells
    ("L1_16x64", 16, 64),
    ("L2_32x128", 32, 128),
    ("L3_64x256", 64, 256),
)
SET_NAME = "gateAxis"
DIAG_SET_NAME = "azimuthCheck"
PROBE_FO = "gateProbes"

RUN_ROOT = "/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL001"
OUT_JSON = os.path.join(RUN_ROOT, "GRADING_VMFL001.json")

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


def refuse(msg):
    print("REFUSE: " + msg, file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------------------
# the reference: exact analytical solution, White section 3-2.3
# ---------------------------------------------------------------------------
def v_exact(r):
    """v_theta(r) = omega R_i^2 (R_o^2 - r^2) / (r (R_o^2 - R_i^2))."""
    return OMEGA * R_I**2 * (R_O**2 - r**2) / (r * (R_O**2 - R_I**2))


def torque_exact_per_length():
    """M' = 4 pi mu omega R_i^2 R_o^2 / (R_o^2 - R_i^2), N-m per m of axial length.
    Printed as a DIAGNOSTIC: unlike v_theta it does depend on mu, which is the
    one thing this case's velocity gate provably cannot see."""
    return 4.0 * math.pi * MU * OMEGA * R_I**2 * R_O**2 / (R_O**2 - R_I**2)


# ---------------------------------------------------------------------------
# the reader: OpenFOAM raw coordSet output
# ---------------------------------------------------------------------------
def read_raw_set(path):
    """Parse an OpenFOAM `raw` coordSet file.  Returns (columns, rows).

    Expected shape (src/meshTools/coordSet/writers/raw, v2606):
        POINT_DATA <n>
        # x y z  U_x U_y U_z
        <numbers> ...
    The column NAMES are read from the header; nothing is positional beyond
    requiring that the header and the data rows agree in width.  A file whose
    columns cannot be identified is a REFUSAL, never a guess.
    """
    if not os.path.isfile(path):
        refuse("sampled file does not exist: " + path)
    cols, rows = None, []
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                toks = s.lstrip("#").split()
                if len(toks) >= 4:
                    cols = toks
                continue
            if s[0].isalpha():        # e.g. "POINT_DATA 4"
                continue
            parts = s.split()
            try:
                rows.append([float(p) for p in parts])
            except ValueError:
                refuse("unparseable data row in %s: %r" % (path, s))
    if cols is None:
        refuse("no '#' column header in %s -- the column layout cannot be "
               "identified and this comparator does not guess" % path)
    if not rows:
        refuse("no data rows in " + path)
    for r in rows:
        if len(r) != len(cols):
            refuse("header has %d columns but a data row has %d in %s"
                   % (len(cols), len(r), path))
    return cols, rows


def _col(cols, name, path):
    if name not in cols:
        refuse("column %r not found in %s (header: %s)" % (name, path, " ".join(cols)))
    return cols.index(name)


def vtheta_from_raw(path):
    """Return [(r, theta, v_theta), ...] from a raw U file.

    v_theta = -U_x sin(theta) + U_y cos(theta), theta = atan2(y, x), r = hypot(x, y).
    On the +x axis (theta = 0) this reduces to v_theta == U_y exactly, which is
    the fixed probe procedure the pre-registration names for the gate.
    """
    cols, rows = read_raw_set(path)
    ix, iy = _col(cols, "x", path), _col(cols, "y", path)
    iux, iuy = _col(cols, "U_x", path), _col(cols, "U_y", path)
    out = []
    for row in rows:
        x, y, ux, uy = row[ix], row[iy], row[iux], row[iuy]
        r = math.hypot(x, y)
        th = math.atan2(y, x)
        out.append((r, th, -ux * math.sin(th) + uy * math.cos(th)))
    return out


def find_set_file(level_dir, set_name, field="U", time=None):
    """postProcessing/<fo>/<time>/<field>_<setName>.<ext> (v2606 naming)."""
    t = str(ENDTIME) if time is None else str(time)
    pats = [os.path.join(level_dir, "postProcessing", "*", t, "%s_%s.*" % (field, set_name)),
            os.path.join(level_dir, "postProcessing", "*", t, "*%s*" % set_name)]
    for p in pats:
        hits = sorted(h for h in glob.glob(p)
                      if os.path.basename(h).startswith(field + "_"))
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            refuse("ambiguous sampled files for set %r in %s: %s"
                   % (set_name, level_dir, ", ".join(os.path.basename(h) for h in hits)))
    refuse("no sampled file for set %r, field %r at time %s under %s/postProcessing"
           % (set_name, field, t, level_dir))


def gate_values(level_dir):
    """The four gate radii -> v_theta, from the frozen probe procedure."""
    path = find_set_file(level_dir, SET_NAME)
    got = vtheta_from_raw(path)
    out = {}
    for r_target in RADII:
        match = [g for g in got if abs(g[0] - r_target) < 1e-6]
        if len(match) != 1:
            refuse("expected exactly one sampled point at r = %.4f m in %s, found %d"
                   % (r_target, path, len(match)))
        out[r_target] = match[0][2]
    return out, path


# ---------------------------------------------------------------------------
# planted-zero control (CLAUDE.md rule 3; pattern carried from
# verification/runs/T-family/T3_runs/analyse_t3.py)
# ---------------------------------------------------------------------------
def plant_into_raw(path, r_target, plant):
    """Add `plant` to the U_y column of the row at r_target, IN PLACE, then read
    the file back FROM DISK to prove the plant landed.  Returns (before, after)."""
    cols = None
    lines = open(path).read().split("\n")
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("#"):
            toks = s.lstrip("#").split()
            if len(toks) >= 4:
                cols = toks
            continue
        if not s or s[0].isalpha():
            continue
        if cols is None:
            raise RuntimeError("data before any header in " + path)
        parts = s.split()
        if len(parts) != len(cols):
            continue
        vals = [float(p) for p in parts]
        if abs(math.hypot(vals[cols.index("x")], vals[cols.index("y")]) - r_target) < 1e-6:
            j = cols.index("U_y")
            before = vals[j]
            vals[j] = before + plant
            lines[i] = " ".join(repr(v) for v in vals)
            open(path, "w").write("\n".join(lines))
            back = None
            for l2 in open(path).read().split("\n"):
                s2 = l2.strip()
                if not s2 or s2.startswith("#") or s2[0].isalpha():
                    continue
                v2 = [float(p) for p in s2.split()]
                if abs(math.hypot(v2[cols.index("x")], v2[cols.index("y")]) - r_target) < 1e-6:
                    back = v2[j]
                    break
            if back is None:
                raise RuntimeError("the planted row could not be re-read from " + path)
            if abs((back - before) - plant) > PLANT_TOL:
                raise RuntimeError("the plant did not land: %r -> %r" % (before, back))
            return before, back
    raise RuntimeError("no row at r = %.4f m in %s" % (r_target, path))


def planted_zero_control(level_dir):
    """Copy the sampled output to a temp tree, plant PLANT into the U_y of the
    triple radius, read it back from disk, and run the SAME reader on the copy.
    The reader must report a v_theta larger by exactly PLANT.  What this
    establishes is that a PLANT-sized difference is VISIBLE to this reader, so a
    small number it returns on the real case is a statement about the fields and
    not about the reader."""
    src = find_set_file(level_dir, SET_NAME)
    before_read = dict(gate_values(level_dir)[0])
    tmp = tempfile.mkdtemp(prefix="vmfl001plant_")
    try:
        work = os.path.join(tmp, os.path.basename(src))
        shutil.copy(src, work)
        before, after = plant_into_raw(work, TRIPLE_RADIUS, PLANT)
        got = vtheta_from_raw(work)
        match = [g for g in got if abs(g[0] - TRIPLE_RADIUS) < 1e-6]
        if len(match) != 1:
            return dict(passed=False, why="planted row not uniquely re-read")
        seen = match[1 - 1][2] - before_read[TRIPLE_RADIUS]
        return dict(passed=abs(seen - PLANT) <= PLANT_TOL,
                    planted=PLANT,
                    read_back_delta=after - before,
                    reader_delta=seen,
                    file=os.path.basename(src))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# strict completion rule (CLAUDE.md rule 4), adapted for simpleFoam / VMFL001
# ---------------------------------------------------------------------------
def _time_dirs(level_dir):
    out = []
    for d in os.listdir(level_dir):
        if os.path.isdir(os.path.join(level_dir, d)) and re.fullmatch(r"\d+(\.\d+)?", d):
            out.append(d)
    return sorted(out, key=float)


def strict_completion(level_dir):
    name = os.path.basename(level_dir)
    if not os.path.isdir(level_dir):
        refuse("%s: run directory does not exist" % name)

    rc_path = os.path.join(level_dir, "RUN_RC.txt")
    if not os.path.isfile(rc_path):
        refuse("%s: no RUN_RC.txt -- the run script did not finish this level" % name)
    rc_txt = open(rc_path).read()
    m = re.search(r"^rc=(-?\d+)$", rc_txt, re.M)
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
    if not times or float(times[-1]) != float(ENDTIME):
        refuse("%s: last time is %r, endTime is %d (clause 3)"
               % (name, times[-1] if times else None, ENDTIME))
    tdir = os.path.join(level_dir, times[-1])
    for f in ("U", "p"):
        if not os.path.isfile(os.path.join(tdir, f)):
            refuse("%s: field %s missing at endTime (clause 4)" % (name, f))

    n_exec = len(re.findall(r"^ExecutionTime = ", text, re.M))
    if n_exec != ENDTIME:
        refuse("%s: %d ExecutionTime lines, endTime is %d (clause 5)"
               % (name, n_exec, ENDTIME))

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
# iterative convergence: residuals AND a probe plateau
# ---------------------------------------------------------------------------
RES_RE = re.compile(r"Solving for (\w+),\s+Initial residual = ([0-9eE.+-]+)")


def residual_history(level_dir):
    text = open(os.path.join(level_dir, "log.simpleFoam"), errors="replace").read()
    hist = {}
    for fld, val in RES_RE.findall(text):
        hist.setdefault(fld, []).append(float(val))
    return hist


def probe_series(level_dir):
    """Per-iteration v_theta at the triple radius, from the `probes` function
    object.  CELL values, not point-interpolated: used ONLY for the plateau leg
    of the convergence test, never as the graded number."""
    pats = os.path.join(level_dir, "postProcessing", PROBE_FO, "*", "U")
    hits = sorted(glob.glob(pats))
    if not hits:
        refuse("%s: no %s probe series under postProcessing"
               % (os.path.basename(level_dir), PROBE_FO))
    times, vals = [], []
    vec = re.compile(r"\(([-0-9eE.+]+)\s+([-0-9eE.+]+)\s+([-0-9eE.+]+)\)")
    for h in hits:
        for line in open(h, errors="replace"):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            vs = vec.findall(s)
            if len(vs) != len(RADII):
                continue
            t = float(s.split()[0])
            # the triple radius is the LAST probe location, on the +x axis,
            # so v_theta == U_y there
            times.append(t)
            vals.append(float(vs[-1][1]))
    if len(vals) < 10:
        refuse("%s: probe series too short (%d samples)"
               % (os.path.basename(level_dir), len(vals)))
    return times, vals


def iterative_convergence(level_dir):
    name = os.path.basename(level_dir)
    hist = residual_history(level_dir)
    finals = {}
    for fld in ("Ux", "Uy", "p"):
        if fld not in hist or not hist[fld]:
            refuse("%s: no residual history for %s" % (name, fld))
        finals[fld] = hist[fld][-1]
    res_ok = all(v < RES_TOL for v in finals.values())

    times, vals = probe_series(level_dir)
    n = max(2, int(round(PLATEAU_FRAC * len(vals))))
    tail = vals[-n:]
    ptp = max(tail) - min(tail)
    plateau_ok = ptp < PLATEAU_TOL

    return dict(final_residuals=finals, residual_tol=RES_TOL, residuals_ok=res_ok,
                plateau_ptp=ptp, plateau_tol=PLATEAU_TOL, plateau_n=n,
                plateau_ok=plateau_ok, converged=(res_ok and plateau_ok),
                probe_last=vals[-1])


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
        out["why"] = ("the coarse-medium difference is below %g m/s while the "
                      "medium-fine difference is not" % EPS_ABS)
        return out

    R = d21 / d32
    out["R"] = R
    if R < 0:
        out["state"] = "OSCILLATORY"
        return out
    if abs(R - 1.0) <= STAG_TOL:
        out["state"] = "STAGNANT"
        return out
    if R > 1.0:
        out["state"] = "DIVERGENT"
        return out

    p = math.log(1.0 / R) / math.log(ratio)
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
def levers(level_dir, n_radial, n_azimuthal):
    name = os.path.basename(level_dir)
    out = {}

    tp = os.path.join(level_dir, "constant", "transportProperties")
    if os.path.isfile(tp):
        m = re.search(r"^\s*nu\s+([0-9eE.+-]+)\s*;", open(tp).read(), re.M)
        if not m:
            refuse("%s: nu not readable from constant/transportProperties" % name)
        nu_ran = float(m.group(1))
        if abs(nu_ran - NU) > 1e-12:
            refuse("%s: nu = %g in the run, %g was registered" % (name, nu_ran, NU))
        out["nu"] = nu_ran
    else:
        refuse("%s: no constant/transportProperties" % name)

    u0 = os.path.join(level_dir, "0", "U")
    txt = open(u0).read()
    if "rotatingWallVelocity" not in txt:
        refuse("%s: innerWall is not rotatingWallVelocity in 0/U" % name)
    m = re.search(r"omega\s+([0-9eE.+-]+)\s*;", txt)
    if not m or abs(float(m.group(1)) - OMEGA) > 1e-12:
        refuse("%s: omega in 0/U is %s, %g was registered"
               % (name, m.group(1) if m else None, OMEGA))
    out["omega"] = float(m.group(1))

    log = open(os.path.join(level_dir, "log.simpleFoam"), errors="replace").read()
    if "laminar" in log:
        out["laminar"] = "active-in-log"
    else:
        out["laminar"] = "unverifiable-from-logs"

    cm = os.path.join(level_dir, "log.checkMesh")
    if os.path.isfile(cm):
        ctext = open(cm, errors="replace").read()
        m = re.search(r"^\s*cells:\s+(\d+)", ctext, re.M)
        expect = n_radial * n_azimuthal
        if not m:
            out["mesh"] = "unverifiable-from-logs (no cell count in log.checkMesh)"
        elif int(m.group(1)) != expect:
            refuse("%s: checkMesh reports %s cells, the level is %d x %d = %d"
                   % (name, m.group(1), n_radial, n_azimuthal, expect))
        else:
            out["mesh"] = dict(cells=int(m.group(1)),
                               mesh_ok=("Mesh OK" in ctext))
    else:
        out["mesh"] = "unverifiable-from-logs (no log.checkMesh)"
    return out


def azimuthal_spread(level_dir):
    """DIAGNOSTIC: max spread of v_theta over 8 azimuths at each gate radius.
    The exact solution is axisymmetric, so this measures discrete anisotropy of
    the mesh.  Never gated on."""
    try:
        path = find_set_file(level_dir, DIAG_SET_NAME)
    except SystemExit:
        return "unavailable"
    got = vtheta_from_raw(path)
    out = {}
    for r_target in RADII:
        vs = [g[2] for g in got if abs(g[0] - r_target) < 1e-6]
        if len(vs) >= 2:
            out["%.3f" % r_target] = dict(n=len(vs), spread=max(vs) - min(vs),
                                          mean=sum(vs) / len(vs))
    return out


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    exact = {r: v_exact(r) for r in RADII}

    print("=" * 78)
    print("%s -- flow between rotating and stationary concentric cylinders" % CASE)
    print("Ansys Fluid Dynamics Verification Manual 2026 R1, p. %s" % MANUAL_PAGES)
    print("reference: White, Viscous Fluid Flow, section 3-2.3 (analytical)")
    print("=" * 78)
    for r in RADII:
        print("  r = %5.1f mm   manual target %8.4f mm/s   exact %10.6f mm/s"
              % (r * 1e3, MANUAL_TARGET[r] * 1e3, exact[r] * 1e3))
    print("  analytic torque per unit length: %.6e N-m/m (diagnostic)"
          % torque_exact_per_length())

    results, completion, conv = {}, {}, {}
    for name, nr, naz in LEVELS:
        d = os.path.join(RUN_ROOT, name)
        completion[name] = strict_completion(d)
        completion[name]["levers"] = levers(d, nr, naz)
        conv[name] = iterative_convergence(d)
        vals, src = gate_values(d)
        results[name] = dict(values=vals, source=os.path.relpath(src, RUN_ROOT),
                             cells=nr * naz,
                             azimuthal_spread=azimuthal_spread(d))

    # ---- planted-zero control, on the level the verdict is taken from --------
    fine = LEVELS[-1][0]
    pz = planted_zero_control(os.path.join(RUN_ROOT, fine))
    print("\nplanted-zero control on %s: %s" % (fine, pz))
    if not pz.get("passed"):
        refuse("planted-zero control failed: the reader cannot see a %g m/s "
               "difference planted on disk; its numbers mean nothing" % PLANT)

    # ---- verdict, in the order rule 5 fixes ---------------------------------
    not_converged = [n for n in conv if not conv[n]["converged"]]
    f_c = results[LEVELS[0][0]]["values"][TRIPLE_RADIUS]
    f_m = results[LEVELS[1][0]]["values"][TRIPLE_RADIUS]
    f_f = results[LEVELS[2][0]]["values"][TRIPLE_RADIUS]
    triple = roache(f_c, f_m, f_f)

    fine_vals = results[fine]["values"]
    gate_rows = []
    for r in RADII:
        lab = fine_vals[r]
        rel_manual = abs(lab - MANUAL_TARGET[r]) / abs(MANUAL_TARGET[r])
        rel_exact = abs(lab - exact[r]) / abs(exact[r])
        gate_rows.append(dict(r_m=r, lab=lab, manual_target=MANUAL_TARGET[r],
                              exact=exact[r], rel_vs_manual=rel_manual,
                              rel_vs_exact=rel_exact,
                              gate_ok=(rel_manual <= TOL_GATE),
                              diagnostic_ok=(rel_exact <= TOL_DIAG)))
    gate_pass = all(g["gate_ok"] for g in gate_rows)

    if not_converged:
        verdict = "NOT A RESULT"
        why = ("iterative convergence not met at: " + ", ".join(sorted(not_converged)))
    elif triple["state"] != "CONVERGING":
        verdict = "NOT A RESULT"
        why = ("grid triple is %s, not CONVERGING (rule 5 step 2)" % triple["state"])
    else:
        verdict = "PASS" if gate_pass else "GATE FAIL"
        why = ("all four radii within %.1f %% of the manual target" % (TOL_GATE * 100)
               if gate_pass else
               "at least one radius outside %.1f %% of the manual target" % (TOL_GATE * 100))
    assert verdict in VERDICTS

    print("\n--- gate: |v_lab - v_manual| / |v_manual| <= %.3f, at %s ---"
          % (TOL_GATE, fine))
    for g in gate_rows:
        print("  r = %5.1f mm  lab %10.6f  manual %10.6f  dev %6.3f %%  %s"
              " | vs exact %10.6f  dev %6.3f %%  %s"
              % (g["r_m"] * 1e3, g["lab"] * 1e3, g["manual_target"] * 1e3,
                 g["rel_vs_manual"] * 100, "ok" if g["gate_ok"] else "OUT",
                 g["exact"] * 1e3, g["rel_vs_exact"] * 100,
                 "ok" if g["diagnostic_ok"] else "out(diagnostic)"))
    print("\n--- Roache triple on v_theta(%.0f mm), ratio %.1f, Fs %.2f ---"
          % (TRIPLE_RADIUS * 1e3, RATIO, FS))
    print("  coarse %.9f  medium %.9f  fine %.9f m/s" % (f_c, f_m, f_f))
    print("  state %s  R %s  p %s  GCI_fine %s"
          % (triple["state"],
             "n/a" if triple["R"] is None else "%.6f" % triple["R"],
             "n/a" if triple["p"] is None else "%.4f" % triple["p"],
             "n/a" if triple["gci_fine"] is None else "%.4e" % triple["gci_fine"]))
    print("\nVERDICT: %s -- %s" % (verdict, why))

    payload = dict(case=CASE, manual_pages=MANUAL_PAGES, verdict=verdict, why=why,
                   gate=dict(tol=TOL_GATE, rows=gate_rows, passed=gate_pass),
                   diagnostic_tol_vs_exact=TOL_DIAG,
                   exact={"%.3f" % r: exact[r] for r in RADII},
                   manual_target={"%.3f" % r: MANUAL_TARGET[r] for r in RADII},
                   torque_exact_per_length=torque_exact_per_length(),
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
def selftest():
    ok = True

    def check(label, cond, detail=""):
        nonlocal ok
        print("  [%s] %s%s" % ("PASS" if cond else "FAIL", label,
                               "" if not detail else "  <- " + str(detail)))
        ok = ok and bool(cond)

    print("--- selftest: exact formula ---")
    check("v_exact(20 mm) == 0.0151201 m/s (6 s.f.)",
          abs(v_exact(0.020) - 0.0151201) < 5e-8, v_exact(0.020))
    check("v_exact(R_i) == omega R_i", abs(v_exact(R_I) - OMEGA * R_I) < 1e-15)
    check("v_exact(R_o) == 0", abs(v_exact(R_O)) < 1e-18)

    tmp = tempfile.mkdtemp(prefix="vmfl001self_")
    try:
        print("--- selftest: raw reader ---")
        path = os.path.join(tmp, "U_gateAxis.raw")
        with open(path, "w") as fh:
            fh.write("POINT_DATA 4\n# x y z  U_x U_y U_z\n")
            for r in RADII:
                fh.write("%r 0 0.0025 0 %r 0\n" % (r, v_exact(r)))
        got = dict((round(a, 6), c) for a, b, c in vtheta_from_raw(path))
        check("reader recovers v_theta at all four radii",
              all(abs(got[round(r, 6)] - v_exact(r)) < 1e-15 for r in RADII))

        print("--- selftest: reader refuses an unreadable layout ---")
        bad = os.path.join(tmp, "U_bad.raw")
        open(bad, "w").write("0.02 0 0.0025 0 0.015 0\n")
        pid = os.fork()
        if pid == 0:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, 2)
            try:
                read_raw_set(bad)
            except SystemExit as e:
                os._exit(e.code if isinstance(e.code, int) else 1)
            os._exit(0)
        _, status = os.waitpid(pid, 0)
        check("headerless file is REFUSED with exit 2",
              os.WIFEXITED(status) and os.WEXITSTATUS(status) == 2,
              os.WEXITSTATUS(status))

        print("--- selftest: planted-zero, positive arm ---")
        work = os.path.join(tmp, "U_plant.raw")
        shutil.copy(path, work)
        before_v = dict((round(a, 6), c) for a, b, c in vtheta_from_raw(work))
        b, a = plant_into_raw(work, TRIPLE_RADIUS, PLANT)
        after_v = dict((round(a2, 6), c) for a2, b2, c in vtheta_from_raw(work))
        delta = after_v[round(TRIPLE_RADIUS, 6)] - before_v[round(TRIPLE_RADIUS, 6)]
        check("the reader sees the planted %g m/s" % PLANT,
              abs(delta - PLANT) <= PLANT_TOL, delta)
        check("the plant is confined to the planted row",
              all(abs(after_v[round(r, 6)] - before_v[round(r, 6)]) < 1e-18
                  for r in RADII if abs(r - TRIPLE_RADIUS) > 1e-9))

        print("--- selftest: planted-zero, negative arm (no plant, no signal) ---")
        work2 = os.path.join(tmp, "U_noplant.raw")
        shutil.copy(path, work2)
        v2 = dict((round(a2, 6), c) for a2, b2, c in vtheta_from_raw(work2))
        check("an unplanted copy shows no change",
              abs(v2[round(TRIPLE_RADIUS, 6)] - before_v[round(TRIPLE_RADIUS, 6)]) < 1e-18)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("--- selftest: Roache classifier ---")
    # second-order synthetic: f(h) = f_ex + C h^2, h = 4, 2, 1
    fex, C = 0.00454781, 1.0e-4
    t = roache(fex + C * 16, fex + C * 4, fex + C * 1)
    check("second-order family -> CONVERGING", t["state"] == "CONVERGING", t["state"])
    check("observed order p == 2 to 1e-9", abs(t["p"] - 2.0) < 1e-9, t["p"])
    check("Richardson extrapolation recovers f_exact",
          abs(t["f_extrapolated"] - fex) < 1e-12, t["f_extrapolated"])
    check("GCI_fine == Fs |d21/f1| / (r^p - 1)",
          abs(t["gci_fine"] - FS * abs((fex + 4 * C - (fex + C)) / (fex + C)) / 3.0) < 1e-15)
    check("divergent family -> DIVERGENT",
          roache(1.0, 1.1, 1.4)["state"] == "DIVERGENT")
    check("oscillatory family -> OSCILLATORY",
          roache(1.0, 1.2, 1.0)["state"] == "OSCILLATORY")
    check("equal-step family -> STAGNANT",
          roache(1.0, 1.1, 1.2)["state"] == "STAGNANT")
    check("identical values -> EXACT",
          roache(2.5, 2.5, 2.5)["state"] == "EXACT")

    print("--- selftest: the gate can fail, and can pass ---")
    r = 0.035
    lab_bad = MANUAL_TARGET[r] * 1.025
    lab_good = MANUAL_TARGET[r] * 1.015
    check("+2.5 %% is outside the gate",
          abs(lab_bad - MANUAL_TARGET[r]) / MANUAL_TARGET[r] > TOL_GATE)
    check("+1.5 %% is inside the gate",
          abs(lab_good - MANUAL_TARGET[r]) / MANUAL_TARGET[r] <= TOL_GATE)
    check("the manual's own printed target at 35 mm is 1.1 %% from the exact "
          "formula -- which is why the gate is 2 %% and not 0.5 %%",
          0.010 < abs(MANUAL_TARGET[r] - v_exact(r)) / v_exact(r) < 0.012,
          abs(MANUAL_TARGET[r] - v_exact(r)) / v_exact(r))

    print("\nSELFTEST: %s" % ("all checks passed" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
