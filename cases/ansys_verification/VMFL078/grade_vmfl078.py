#!/usr/bin/env python3
# =============================================================================
# VMFL078 COMPARATOR -- Polyhedral Mesh Accuracy / 3-D lid-driven CUBIC cavity,
# Re = 1000.  Ansys Fluid Dynamics Verification Manual, Release 2026 R1,
# printed pages 223-224 (PDF pages 237-238).
#
# Frozen pre-registration: cases/ansys_verification/VMFL078/PREREGISTRATION.md
# Run root               : verification/runs/ansys_verification/VMFL078/
#
# THE ONE THING A READER MUST KNOW FIRST.  The manual prints NO numeric result for
# VMFL078.  Its entire result section is one plate -- "Figure .78.2: Comparison of
# X-Velocity along the vertical centerline in the symmetry plane" (p.224).  There is
# no table, no scalar, nothing to gate a value against.  Therefore:
#
#   * LIMB A (grid convergence of the centreline functional on our own r = 2 family)
#     is graded here and is PASS-capable ON ITS OWN TERMS.
#   * LIMB B (the manual comparison, Figure .78.2) is BLOCKED -- ANSYS_VERIFICATION
#     CHARTER sec.25.7 forbids gating on a digitized reference until a PER-CASE
#     digitizer registration freezes prediction, per-case u_read, band arithmetic and
#     plate hash.  None of that exists for plate .78.2.
#   * SO THE ROW VERDICT IS CAPPED AT `GATE REACHED`.  `PASS` IS UNAVAILABLE FOR
#     VMFL078 IN THIS ROUND, BY CONSTRUCTION, AND THAT WAS REGISTERED BEFORE COMPUTE.
#     row_verdict() CANNOT RETURN "PASS".  The selftest drives that.
#
# This is the same disposition VMFL054-R3 reached on the same ground (register row
# #69, GATE REACHED: "the manual states the reference only as a plotted profile").
#
# NO `assert` ANYWHERE.  `python3 -O` deletes every assert, so a control written as an
# assert is not a control (L-332).  Every check is an explicit `if not X: refuse()`,
# and --selftest proves ast.Assert count == 0 in this file under BOTH interpreters.
#
# REFUSE, NEVER DEGRADE.  Every guard exits 2.  A missing artefact, an unreadable
# probe, a plant the reader cannot see, a boundary condition that is not what was
# registered -- each is a refusal, never a softer number.
# =============================================================================
import argparse, ast, glob, hashlib, json, math, os, re, subprocess, sys, tempfile, shutil

# ----------------------------------------------------------- FROZEN CONSTANTS --
CASE_ID       = "VMFL078"
MANUAL_PAGES  = "VM2026R1 printed pp.223-224 (PDF pp.237-238)"
LEVELS        = ("L1", "L2", "L3")          # the r = 2 family, coarse -> fine
MESH_NX       = {"L1": 32, "L2": 64, "L3": 128}
MESH_NY       = {"L1": 32, "L2": 64, "L3": 128}
MESH_NZ       = {"L1": 16, "L2": 32, "L3":  64}
RATIO         = 2.0                          # grid refinement ratio r
FS            = 1.25                         # Roache factor of safety

# The frozen centreline sample line: x = 0.5, z = 0.5 (the cube's mid-span = the
# symmetry plane), 201 points y = 0.005 .. 0.995.  IDENTICAL at every level -- this
# is the VMFL054 fix (cellPoint + frozen abscissae) that keeps the observed order
# clean.  These MUST agree with case/system/controlDict.template; check_abscissae()
# verifies that against the real file rather than trusting this comment.
N_PROBE       = 201
Y_LO, Y_HI    = 0.005, 0.995
X_LINE, Z_LINE = 0.5, 0.5

# THE GATE FUNCTIONAL, frozen:
#   J = sqrt( (1/(Y_HI-Y_LO)) * INTEGRAL_{Y_LO}^{Y_HI} u_x(0.5, y, 0.5)^2 dy )
# by trapezoid over the 201 frozen abscissae.  Units m/s.  An INTEGRAL functional of
# the whole profile, not a point value and not an extremum locator: it has no locator
# error to shift between levels, and it is the profile the manual's own figure plots.
# The window excludes y = 0 and y = 1 because those carry EXACTLY the imposed BC
# values at every level -- an identity component, which VERIFICATION_CHARTER sec.2a
# permits reporting and forbids gating on.

# LIMB A GATE BAND -- CLASS DEFAULT, carried unchanged from VMFL054-R3, the same flow
# class (steady laminar lid-driven cavity, simpleFoam/SIMPLEC, cellPoint centreline
# probe), where it was frozen before compute and the run measured p = 1.195,
# GCI_fine = 0.0356 %.  NOT tuned for VMFL078.  Provenance: "class default, first use
# in 3-D" (Case Protocol sec.1).
P_LO, P_HI    = 1.0, 3.0
GCI_MAX_PCT   = 5.0

# Iterative error must be at least this many times smaller than the level-to-level
# difference (Case Protocol sec.5).  Reported and gating: below it, the triple is
# measuring solver noise, not discretisation.
ITER_ERR_MARGIN = 10.0

# Rule 3 planted-zero control.
PLANT_DELTA   = 1.234e-03     # m/s, planted into u_x on the REAL bytes on disk
PLANT_MIN_ABS = 1.0e-12       # a reader that moves by less than this has not moved

# Strict completion (rule 4).  Fields for a steady laminar incompressible solve.
REQUIRED_FIELDS = ("U", "p", "phi")

# Registered boundary conditions.  The comparator reads the RUN'S OWN bytes and
# refuses on any departure -- this is what gates the wrong-treatment mode named a
# priori in the registration (a WALL where the symmetry plane should be).
REQUIRED_MESH_PATCH_TYPES = {
    "lid": "wall", "floor": "wall", "sideXmin": "wall",
    "sideXmax": "wall", "wallZmin": "wall", "symmetry": "symmetryPlane",
}
REQUIRED_U_BC = {
    "lid": "fixedValue", "floor": "noSlip", "sideXmin": "noSlip",
    "sideXmax": "noSlip", "wallZmin": "noSlip", "symmetry": "symmetryPlane",
}
LID_VALUE = (1.0, 0.0, 0.0)

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


class Refusal(SystemExit):
    """Exit 2.  Refuse, never degrade."""
    def __init__(self, msg):
        sys.stderr.write("REFUSE: %s\n" % msg)
        SystemExit.__init__(self, 2)


def refuse(msg):
    raise Refusal(msg)


def frozen_abscissae():
    return [Y_LO + i * (Y_HI - Y_LO) / (N_PROBE - 1) for i in range(N_PROBE)]


# ------------------------------------------------- THE CARDINALITY GUARD -------
def one_match(pattern, what):
    """Exactly one match or refuse.  Two matches is as dangerous as none: a glob that
    silently picks the first of two is how a stale artefact gets graded."""
    hits = sorted(glob.glob(pattern))
    if len(hits) == 0:
        refuse("no %s matched %s" % (what, pattern))
    if len(hits) > 1:
        refuse("%d matches for %s (%s) -- one_match refuses on ambiguity" %
               (len(hits), what, ", ".join(os.path.basename(h) for h in hits)))
    return hits[0]


def numeric_time_dirs(level_dir):
    """Numeric time directories, sorted NUMERICALLY.  A lexicographic sort puts 950
    after 2000 and grades the wrong time.  A `[0-9]*` glob also matches `0.orig`."""
    out = []
    if not os.path.isdir(level_dir):
        return out
    for name in os.listdir(level_dir):
        if not os.path.isdir(os.path.join(level_dir, name)):
            continue
        if re.match(r'^[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?$', name):
            out.append((float(name), name))
    out.sort(key=lambda t: t[0])
    return out


# ---------------------------------------------------------------- readers ------
def read_probe_ux(path, n_expected=N_PROBE):
    """Read the LAST data row of an OpenFOAM `probes` U file and return the list of
    u_x.  This is THE gate reader: the planted-zero control plants into this file's
    real bytes and reads back through THIS function."""
    if not os.path.isfile(path):
        refuse("probe file absent: %s" % path)
    data = [l for l in open(path, errors="replace").read().splitlines()
            if l.strip() and not l.lstrip().startswith('#')]
    if not data:
        refuse("probe file %s has no data rows" % path)
    vecs = re.findall(r'\(\s*([-0-9.eE+]+)\s+([-0-9.eE+]+)\s+([-0-9.eE+]+)\s*\)', data[-1])
    if len(vecs) != n_expected:
        refuse("probe file %s last row carries %d vectors, registered %d"
               % (path, len(vecs), n_expected))
    ux = []
    for a, _b, _c in vecs:
        try:
            v = float(a)
        except ValueError:
            refuse("non-numeric u_x in %s" % path)
        if math.isnan(v) or math.isinf(v):
            refuse("NaN/Inf u_x in %s -- refuse, never degrade" % path)
        ux.append(v)
    return ux


def gate_functional(ux, ys=None):
    """J = sqrt(mean-square of u_x over the frozen window), trapezoid."""
    ys = frozen_abscissae() if ys is None else ys
    if len(ux) != len(ys):
        refuse("gate_functional: %d values against %d abscissae" % (len(ux), len(ys)))
    acc = 0.0
    for i in range(len(ys) - 1):
        acc += 0.5 * (ux[i] ** 2 + ux[i + 1] ** 2) * (ys[i + 1] - ys[i])
    return math.sqrt(acc / (ys[-1] - ys[0]))


def probe_path(level_dir, fo="centrelineProbe"):
    return one_match(os.path.join(level_dir, "postProcessing", fo, "*", "U"),
                     "%s U output under %s" % (fo, level_dir))


# --------------------------------- in-place planting on the REAL bytes ---------
def plant_into_probe(path, delta, indices=None):
    """Add `delta` to u_x of the named probe indices IN THE FILE ON DISK, rewriting the
    real bytes the real reader reads.  Not a mock, not a monkeypatch: the plant goes
    through the same path the graded number does."""
    txt = open(path, errors="replace").read()
    lines = txt.splitlines()
    last = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() and not lines[i].lstrip().startswith('#'):
            last = i
            break
    if last is None:
        refuse("plant_into_probe: %s has no data row to plant into" % path)
    n = [0]

    def sub(m):
        idx = n[0]
        n[0] += 1
        if indices is not None and idx not in indices:
            return m.group(0)
        return "(%.12g %s %s)" % (float(m.group(1)) + delta, m.group(2), m.group(3))

    lines[last] = re.sub(r'\(\s*([-0-9.eE+]+)\s+([-0-9.eE+]+)\s+([-0-9.eE+]+)\s*\)',
                         sub, lines[last])
    open(path, "w").write("\n".join(lines) + "\n")
    return n[0]


def planted_zero_control(level_dir):
    """Rule 3.  THREE plants, all through the real path, into a scratch COPY of the
    level so the graded artefacts are never mutated.

      P1a  a single-probe plant must be seen, at that index, at exactly its size.
      P1b  an all-probe plant must MOVE THE GATE FUNCTIONAL by a non-zero amount.
      P1c  a BLIND writer (plant written to a decoy file, graded file untouched) must
           read back UNMOVED -- and a reader that reports movement anyway is refused.

    A zero from a reader not shown able to see a non-zero is not evidence."""
    tmp = tempfile.mkdtemp(prefix="vmfl078_plant_")
    try:
        work = os.path.join(tmp, "lvl")
        shutil.copytree(level_dir, work)
        p = probe_path(work)
        base = read_probe_ux(p)
        j0 = gate_functional(base)

        # --- P1a: one probe, one known delta ---------------------------------
        target = N_PROBE // 2
        plant_into_probe(p, PLANT_DELTA, indices={target})
        seen = read_probe_ux(p)
        moved = seen[target] - base[target]
        if abs(moved - PLANT_DELTA) > 1e-9:
            refuse("PLANT P1a: planted %.6e at probe %d, reader saw %.6e -- the gate "
                   "reader cannot see its own plant" % (PLANT_DELTA, target, moved))
        others = max(abs(seen[i] - base[i]) for i in range(N_PROBE) if i != target)
        if others > PLANT_MIN_ABS:
            refuse("PLANT P1a: an unplanted probe moved by %.6e -- the plant leaked"
                   % others)

        # --- P1b: all probes, the FUNCTIONAL must move ------------------------
        shutil.rmtree(work)
        shutil.copytree(level_dir, work)
        p = probe_path(work)
        nplanted = plant_into_probe(p, PLANT_DELTA)
        if nplanted != N_PROBE:
            refuse("PLANT P1b: planted into %d probes, registered %d" % (nplanted, N_PROBE))
        j1 = gate_functional(read_probe_ux(p))
        if abs(j1 - j0) <= PLANT_MIN_ABS:
            refuse("PLANT P1b: an all-probe plant of %.6e moved the GATE FUNCTIONAL by "
                   "%.6e (<= %.1e) -- the functional is blind to its input"
                   % (PLANT_DELTA, j1 - j0, PLANT_MIN_ABS))

        # --- P1c: the blind writer -------------------------------------------
        shutil.rmtree(work)
        shutil.copytree(level_dir, work)
        p = probe_path(work)
        decoy = p + ".decoy"
        shutil.copyfile(p, decoy)
        plant_into_probe(decoy, PLANT_DELTA)      # graded file deliberately untouched
        j2 = gate_functional(read_probe_ux(p))
        if abs(j2 - j0) > PLANT_MIN_ABS:
            refuse("PLANT P1c: the graded file was NOT planted, yet the reader moved by "
                   "%.6e -- the reader is not reading the file it claims" % (j2 - j0))
        return {"J_unplanted": j0, "P1a_seen": moved, "P1a_expected": PLANT_DELTA,
                "P1b_dJ": j1 - j0, "P1c_dJ_blind": j2 - j0, "n_planted": nplanted}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------- BOUNDARY-CONDITION PROVENANCE
def read_mesh_patch_types(level_dir):
    path = os.path.join(level_dir, "constant", "polyMesh", "boundary")
    if not os.path.isfile(path):
        refuse("constant/polyMesh/boundary absent under %s" % level_dir)
    txt = open(path, errors="replace").read()
    out = {}
    for m in re.finditer(r'^\s{4}(\w+)\s*$\s*^\s*\{(.*?)^\s*\}', txt, re.M | re.S):
        tm = re.search(r'\btype\s+(\w+)\s*;', m.group(2))
        if tm:
            out[m.group(1)] = tm.group(1)
    return out


def read_field_bc_types(path):
    if not os.path.isfile(path):
        refuse("field file absent: %s" % path)
    txt = open(path, errors="replace").read()
    if "boundaryField" not in txt:
        refuse("no boundaryField in %s" % path)
    body = txt[txt.index("boundaryField"):]
    out = {}
    for m in re.finditer(r'^\s{4}(\w+)\s*\{(.*?)\}', body, re.M | re.S):
        tm = re.search(r'\btype\s+(\w+)\s*;', m.group(2))
        if tm:
            out[m.group(1)] = (tm.group(1), m.group(2))
    return out


def bc_provenance(level_dir):
    """Answers VERIFICATION_CHARTER sec.2a question (2) -- "could a wrong treatment
    still pass this gate?"  YES: a WALL at z = 0.5 instead of the symmetry plane would
    still grid-converge and still pass limb A.  So the wrong treatment is gated HERE,
    exactly, on the run's own bytes, not on a statistic."""
    mesh = read_mesh_patch_types(level_dir)
    for patch, want in REQUIRED_MESH_PATCH_TYPES.items():
        if patch not in mesh:
            refuse("BC provenance: mesh patch '%s' absent under %s (found: %s)"
                   % (patch, level_dir, ", ".join(sorted(mesh)) or "none"))
        if mesh[patch] != want:
            refuse("BC provenance: mesh patch '%s' is type '%s', REGISTERED '%s' -- the "
                   "case that ran is not the case that was registered"
                   % (patch, mesh[patch], want))
    extra = set(mesh) - set(REQUIRED_MESH_PATCH_TYPES)
    if extra:
        refuse("BC provenance: unregistered mesh patch(es) %s" % sorted(extra))

    ubc = read_field_bc_types(os.path.join(level_dir, "0", "U"))
    for patch, want in REQUIRED_U_BC.items():
        if patch not in ubc:
            refuse("BC provenance: 0/U has no entry for patch '%s'" % patch)
        if ubc[patch][0] != want:
            refuse("BC provenance: 0/U patch '%s' is '%s', REGISTERED '%s'"
                   % (patch, ubc[patch][0], want))
    vm = re.search(r'value\s+uniform\s*\(\s*([-0-9.eE+]+)\s+([-0-9.eE+]+)\s+([-0-9.eE+]+)\s*\)',
                   ubc["lid"][1])
    if not vm:
        refuse("BC provenance: lid has no uniform value in 0/U")
    got = tuple(float(x) for x in vm.groups())
    if max(abs(a - b) for a, b in zip(got, LID_VALUE)) > 1e-12:
        refuse("BC provenance: lid velocity %s, REGISTERED %s (the manual: 1 m/s at the "
               "top of the domain)" % (str(got), str(LID_VALUE)))
    return {"mesh_patch_types": mesh, "U_bc_types": {k: v[0] for k, v in ubc.items()},
            "lid_value": list(got)}


def check_abscissae(case_dir):
    """The frozen abscissae in THIS file must be the abscissae in the controlDict the
    solver actually reads.  A comparator whose sample line has drifted from the case's
    is grading a different line than it says it is."""
    p = os.path.join(case_dir, "system", "controlDict.template")
    if not os.path.isfile(p):
        refuse("controlDict.template absent at %s" % p)
    txt = open(p, errors="replace").read()
    blk = re.search(r'centrelineProbe\s*\{(.*?)\n    \}', txt, re.S)
    if not blk:
        refuse("no centrelineProbe block in %s" % p)
    if "cellPoint" not in blk.group(1):
        refuse("centrelineProbe has no `interpolationScheme cellPoint` -- the VMFL054 "
               "order-pollution fix is MISSING from the case that would run")
    locs = re.findall(r'\(\s*([-0-9.eE+]+)\s+([-0-9.eE+]+)\s+([-0-9.eE+]+)\s*\)',
                      blk.group(1))
    if len(locs) != N_PROBE:
        refuse("controlDict centrelineProbe carries %d locations, comparator frozen at %d"
               % (len(locs), N_PROBE))
    want = frozen_abscissae()
    for i, (x, y, z) in enumerate(locs):
        if (abs(float(x) - X_LINE) > 1e-9 or abs(float(z) - Z_LINE) > 1e-9
                or abs(float(y) - want[i]) > 1e-9):
            refuse("controlDict probe %d is (%s %s %s), comparator frozen at (%g %g %g)"
                   % (i, x, y, z, X_LINE, want[i], Z_LINE))
    return {"n_locations": len(locs), "cellPoint": True}


# ---------------------------------------------------------- STRICT COMPLETION --
def completion(run_root, level):
    """Rule 4, in full, with the AGE GUARD.

    DECLARED FROZEN DEPARTURE, and it is the same one VMFL054-R3/VMFL063 froze: this is
    a residualControl-terminated STEADY solve, so `last time == endTime` is the FAILURE
    case, not the success case.  A converged run stops BELOW endTime.  The frozen rule
    is therefore: EITHER the log carries a SIMPLE-convergence line and the last time is
    strictly below endTime, OR the run reached endTime -- and reaching endTime WITHOUT
    converging is NOT A RESULT (rule 5 limb 1: a level not iteratively converged)."""
    lvl = os.path.join(run_root, level)
    out = {"level": level, "checks": {}}
    if not os.path.isdir(lvl):
        refuse("level directory absent: %s" % lvl)

    rcp = os.path.join(run_root, "RUN_RC.%s" % level)
    if os.path.isfile(rcp):
        rt = open(rcp, errors="replace").read()
        m = re.search(r'^rc\s*=\s*(-?\d+)', rt, re.M)
        out["rc"] = int(m.group(1)) if m else None
        m = re.search(r'^endTime\s*=\s*([0-9.]+)', rt, re.M)
        out["endTime"] = float(m.group(1)) if m else None
        m = re.search(r'^core_min\s*=\s*([0-9.]+)', rt, re.M)
        out["core_min"] = float(m.group(1)) if m else None
    else:
        # L-342: RUN_RC is INFRASTRUCTURE.  Its absence is reported, never silently
        # treated as rc 0, and never voids the physics artefacts.
        out["rc"] = None
        out["endTime"] = None
        out["core_min"] = None
        out["rc_note"] = "RUN_RC.%s absent -- rc NOT MEASURED (infrastructure, L-342)" % level
    out["checks"]["rc_zero"] = (out["rc"] == 0)

    log = os.path.join(lvl, "log.simpleFoam")
    if not os.path.isfile(log):
        refuse("log.simpleFoam absent under %s" % lvl)
    txt = open(log, errors="replace").read()
    out["checks"]["End_line"] = bool(re.search(r'^End\s*$', txt, re.M))
    times = re.findall(r'^Time = ([0-9.eE+-]+)\s*$', txt, re.M)
    if not times:
        refuse("no `Time = ` lines in %s" % log)
    out["last_time"] = float(times[-1])
    out["n_exec"] = len(re.findall(r'^ExecutionTime', txt, re.M))
    out["converged_lines"] = len(re.findall(r'SIMPLE solution converged', txt))
    out["checks"]["converged"] = out["converged_lines"] > 0
    if out["endTime"] is not None:
        if out["checks"]["converged"]:
            out["checks"]["stopped_below_endTime"] = out["last_time"] < out["endTime"]
        else:
            out["checks"]["stopped_below_endTime"] = False
    else:
        out["checks"]["stopped_below_endTime"] = None
    # clause-5, unit deltaT: ExecutionTime count == steps written == last time
    out["checks"]["n_exec_matches_steps"] = (out["n_exec"] == int(round(out["last_time"])))

    tds = numeric_time_dirs(lvl)
    nonzero = [t for t in tds if t[0] > 0]
    if not nonzero:
        refuse("no non-zero time directory under %s -- the run produced no answer" % lvl)
    tdir = os.path.join(lvl, nonzero[-1][1])
    out["latest_time_dir"] = nonzero[-1][1]
    out["checks"]["latest_dir_is_last_time"] = abs(nonzero[-1][0] - out["last_time"]) < 1e-9

    missing = [f for f in REQUIRED_FIELDS if not os.path.isfile(os.path.join(tdir, f))]
    out["checks"]["fields_present"] = not missing
    if missing:
        out["missing_fields"] = missing

    # --- THE AGE GUARD.  0/U is touched LAST at launch, so it dates the run allowed to
    # produce the answer.  Every field at endTime must be NEWER than it.
    z = os.path.join(lvl, "0", "U")
    if not os.path.isfile(z):
        refuse("age guard: %s absent -- the guard's datum is missing, refuse" % z)
    t0 = os.path.getmtime(z)
    ages = {}
    ok = True
    for f in REQUIRED_FIELDS:
        fp = os.path.join(tdir, f)
        if not os.path.isfile(fp):
            ok = False
            continue
        ages[f] = os.path.getmtime(fp) - t0
        if ages[f] <= 0:
            ok = False
    out["age_guard_deltas_s"] = ages
    out["checks"]["age_guard"] = ok

    out["complete"] = all(v is True for v in out["checks"].values())
    return out


# ------------------------------------------------------------ ROACHE TRIPLE ----
def roache(f1, f2, f3, r=RATIO, fs=FS):
    """f1 coarse, f2 medium, f3 fine.  Never quotes a GCI when the three are not
    monotone."""
    e21, e32 = f2 - f1, f3 - f2
    out = {"f_coarse": f1, "f_medium": f2, "f_fine": f3, "e21": e21, "e32": e32,
           "R": None, "p": None, "gci_fine_pct": None, "state": None}
    if e21 == 0.0 and e32 == 0.0:
        out["state"] = "EXACT"
        return out
    if e21 == 0.0:
        out["state"] = "STAGNANT"
        return out
    R = e32 / e21
    out["R"] = R
    if R < 0:
        out["state"] = "OSCILLATORY"
        return out
    if R >= 1.0:
        out["state"] = "DIVERGENT"
        return out
    if abs(e32) < 1e-300:
        out["state"] = "STAGNANT"
        return out
    p = math.log(abs(e21 / e32)) / math.log(r)
    out["p"] = p
    out["state"] = "CONVERGING"
    denom = (r ** p) - 1.0
    if abs(denom) < 1e-300 or f3 == 0.0:
        out["state"] = "STAGNANT"
        out["p"] = p
        return out
    out["gci_fine_pct"] = fs * abs(e32 / f3) / denom * 100.0
    return out


# ------------------------------------------------------------------ VERDICTS ---
def verdict_limb_a(tri, iter_margin_ok):
    """Rule 5, in its fixed order.  ONE-WAY: the gate can turn PASS or GATE FAIL INTO
    NOT A RESULT, never the reverse."""
    if tri["state"] != "CONVERGING":
        return "NOT A RESULT", "triple state %s" % tri["state"]
    if iter_margin_ok is False:
        return "NOT A RESULT", ("iterative error is not %gx smaller than the "
                                "level-to-level difference" % ITER_ERR_MARGIN)
    p, g = tri["p"], tri["gci_fine_pct"]
    if p is None or g is None:
        return "NOT A RESULT", "CONVERGING but order/GCI unavailable"
    inside = (P_LO <= p <= P_HI) and (g <= GCI_MAX_PCT)
    if inside:
        return "PASS", "p=%.4f in [%g,%g] and GCI_fine=%.5f%% <= %g%%" % (p, P_LO, P_HI, g, GCI_MAX_PCT)
    why = []
    if not (P_LO <= p <= P_HI):
        why.append("p=%.4f outside [%g,%g]" % (p, P_LO, P_HI))
    if g > GCI_MAX_PCT:
        why.append("GCI_fine=%.5f%% > %g%%" % (g, GCI_MAX_PCT))
    return "GATE FAIL", "; ".join(why)


def verdict_limb_b():
    """LIMB B IS BLOCKED AND THAT WAS REGISTERED BEFORE COMPUTE.  The manual prints no
    number for VMFL078 -- its result is Figure .78.2 alone -- and ANSYS_VERIFICATION
    CHARTER sec.25.7 forbids gating on a digitized reference until a per-case digitizer
    registration (prediction, per-case u_read on THIS plate, band arithmetic, plate
    hash) is filed and committed.  None exists.  This function takes no argument
    because there is nothing about the run that could change its answer."""
    return "BLOCKED", ("manual reference for VMFL078 is Figure .78.2 (p.224) ONLY -- no "
                       "printed scalar; sec.25.7 per-case digitizer registration not filed")


def row_verdict(limb_a, limb_b):
    """THE CEILING.  `PASS` IS UNAVAILABLE FOR VMFL078 THIS ROUND, BY CONSTRUCTION.

    VERIFICATION_CHARTER sec.2: "A gate that was not reached is stated as not reached,
    never replaced by a nearer gate that was."  Limb A is a nearer gate -- it verifies
    OUR OWN discretisation and compares against nothing the manual publishes.  Recording
    a limb-A PASS as a VMFL078 PASS would be exactly that substitution.

    So: this function CANNOT return "PASS".  A limb-A PASS with limb B BLOCKED is
    `GATE REACHED` -- the same disposition VMFL054-R3 reached on the same ground.
    Rule 5's one-way direction is preserved: a NOT A RESULT on limb A still dominates."""
    if limb_a == "NOT A RESULT":
        return "NOT A RESULT"
    if limb_a == "GATE FAIL":
        return "GATE FAIL"
    if limb_a == "PASS" and limb_b == "BLOCKED":
        return "GATE REACHED"
    return "NOT A RESULT"


# ------------------------------------------------------------ FREEZE CHECK -----
def sha_of(path):
    h = hashlib.sha1()
    b = open(path, "rb").read()
    h.update(b"blob %d\0" % len(b))
    h.update(b)
    return h.hexdigest()


def verify_frozen(repo=None):
    here = os.path.dirname(os.path.abspath(__file__))
    repo = repo or subprocess.run(["git", "-C", here, "rev-parse", "--show-toplevel"],
                                  capture_output=True, text=True).stdout.strip()
    if not repo:
        refuse("not inside a git repository -- cannot verify the freeze")
    out = {}
    for rel in ("cases/ansys_verification/VMFL078/PREREGISTRATION.md",
                "cases/ansys_verification/VMFL078/grade_vmfl078.py"):
        r = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD:%s" % rel],
                           capture_output=True, text=True)
        if r.returncode != 0:
            refuse("%s is NOT committed at HEAD -- the freeze IS the evidence (rule 2)" % rel)
        head = r.stdout.strip()
        disk = sha_of(os.path.join(repo, rel))
        if head != disk:
            refuse("freeze check: %s on disk (%s) != HEAD blob (%s)" % (rel, disk, head))
        out[rel] = disk
    return out


# ------------------------------------------------------------- THE AST GUARD ---
def ast_guard():
    src = open(os.path.abspath(__file__), errors="replace").read()
    n = sum(1 for node in ast.walk(ast.parse(src)) if isinstance(node, ast.Assert))
    return n


# ---------------------------------------------------------------- GRADE --------
def grade(run_root, case_dir=None):
    case_dir = case_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "case")
    rep = {"case": CASE_ID, "manual": MANUAL_PAGES, "run_root": run_root, "levels": {}}
    rep["abscissae_check"] = check_abscissae(case_dir)

    Js, comps = {}, {}
    for lv in LEVELS:
        c = completion(run_root, lv)
        comps[lv] = c
        if not c["complete"]:
            bad = [k for k, v in c["checks"].items() if v is not True]
            rep["levels"][lv] = {"completion": c, "note": "incomplete: %s" % bad}
            rep["limb_a"] = {"verdict": "NOT A RESULT",
                             "why": "level %s failed strict completion: %s" % (lv, bad)}
            rep["limb_b"] = dict(zip(("verdict", "why"), verdict_limb_b()))
            rep["row_verdict"] = row_verdict("NOT A RESULT", rep["limb_b"]["verdict"])
            return rep
        lvl = os.path.join(run_root, lv)
        rep["levels"][lv] = {"completion": c,
                             "bc_provenance": bc_provenance(lvl),
                             "plants": planted_zero_control(lvl)}
        ux = read_probe_ux(probe_path(lvl))
        J = gate_functional(ux)
        Js[lv] = J
        rep["levels"][lv]["J"] = J
        rep["levels"][lv]["u_x_min"] = min(ux)
        rep["levels"][lv]["y_at_u_x_min"] = frozen_abscissae()[ux.index(min(ux))]
        rep["levels"][lv]["cells"] = MESH_NX[lv] * MESH_NY[lv] * MESH_NZ[lv]

    tri = roache(Js["L1"], Js["L2"], Js["L3"])
    rep["triple_J"] = tri

    # Case Protocol sec.5: iterative error must be >= ITER_ERR_MARGIN times smaller
    # than the level-to-level difference.  residualControl 1e-08/1e-09 bounds the
    # iterative error on J at ~1e-8 m/s; the comparison is made explicit here.
    iter_err = 1.0e-8
    d = abs(Js["L3"] - Js["L2"])
    rep["iterative_error_check"] = {"iter_err_bound": iter_err, "level_diff": d,
                                    "margin": (d / iter_err) if iter_err else None,
                                    "required": ITER_ERR_MARGIN}
    margin_ok = (d >= ITER_ERR_MARGIN * iter_err)
    rep["iterative_error_check"]["ok"] = margin_ok

    va, wa = verdict_limb_a(tri, margin_ok)
    vb, wb = verdict_limb_b()
    rep["limb_a"] = {"verdict": va, "why": wa, "classification": "DISCRETE -- a property "
                     "of our own r=2 family; it compares against nothing external"}
    rep["limb_b"] = {"verdict": vb, "why": wb}
    rep["secondary_demote_only"] = {
        "u_x_min_triple": roache(rep["levels"]["L1"]["u_x_min"],
                                 rep["levels"]["L2"]["u_x_min"],
                                 rep["levels"]["L3"]["u_x_min"]),
        "note": "REPORTED, DEMOTE-ONLY: can turn the row into NOT A RESULT, never licence a PASS"}
    rep["row_verdict"] = row_verdict(va, vb)
    rep["ceiling_note"] = ("PASS IS UNAVAILABLE FOR VMFL078 BY CONSTRUCTION, registered "
                           "before compute: the manual prints no scalar for this case "
                           "(Figure .78.2 only) and sec.25.7 blocks a digitized gate.")
    return rep


# ---------------------------------------------------------------- SELFTEST -----
_P = [0]
_F = [0]


def ck(name, ok):
    if ok:
        _P[0] += 1
        print("  [PASS] %s" % name)
    else:
        _F[0] += 1
        print("  [FAIL] %s" % name)


def refuses(fn, *a, **k):
    try:
        fn(*a, **k)
    except Refusal:
        return True
    except SystemExit as e:
        return e.code == 2
    return False


def _write_level(root, lv, ux_fn, endtime=40000, iters=1234, converged=True,
                 sym_type="symmetryPlane", sym_u_type=None, lid=(1.0, 0.0, 0.0),
                 nprobe=N_PROBE, fields=REQUIRED_FIELDS, stale=False):
    """Build a synthetic level tree that is byte-shaped like a real one."""
    lvl = os.path.join(root, lv)
    os.makedirs(os.path.join(lvl, "0"))
    os.makedirs(os.path.join(lvl, "constant", "polyMesh"))
    tdir = os.path.join(lvl, str(iters))
    os.makedirs(tdir)
    pp = os.path.join(lvl, "postProcessing", "centrelineProbe", "0")
    os.makedirs(pp)

    ys = frozen_abscissae()
    rows = ["# Probe %d (%g %g %g)" % (i, X_LINE, ys[i], Z_LINE) for i in range(nprobe)]
    rows.append("#       Time")
    vals = " ".join("(%.12g 0 0)" % ux_fn(ys[i]) for i in range(nprobe))
    rows.append("       %d  %s" % (iters, vals))
    open(os.path.join(pp, "U"), "w").write("\n".join(rows) + "\n")

    bnd = ["FoamFile { version 2.0; format ascii; class polyBoundaryMesh; object boundary; }", "6", "("]
    for patch, ty in (("lid", "wall"), ("floor", "wall"), ("sideXmin", "wall"),
                      ("sideXmax", "wall"), ("wallZmin", "wall"), ("symmetry", sym_type)):
        bnd += ["    %s" % patch, "    {", "        type            %s;" % ty,
                "        nFaces          1024;", "    }"]
    bnd += [")"]
    open(os.path.join(lvl, "constant", "polyMesh", "boundary"), "w").write("\n".join(bnd) + "\n")

    u = ["FoamFile { version 2.0; format ascii; class volVectorField; object U; }",
         "dimensions      [0 1 -1 0 0 0 0];", "internalField   uniform (0 0 0);",
         "boundaryField", "{",
         "    lid          { type fixedValue; value uniform (%g %g %g); }" % lid,
         "    floor        { type noSlip; }", "    sideXmin     { type noSlip; }",
         "    sideXmax     { type noSlip; }", "    wallZmin     { type noSlip; }",
         "    symmetry     { type %s; }" % (sym_u_type if sym_u_type is not None
                                       else ("symmetryPlane" if sym_type == "symmetryPlane" else "noSlip")),
         "}"]
    open(os.path.join(lvl, "0", "U"), "w").write("\n".join(u) + "\n")

    log = ["Time = %d" % t for t in range(1, iters + 1)]
    log = sum([[l, "ExecutionTime = %.2f s  ClockTime = %d s" % (i * 0.05, i)]
               for i, l in enumerate(log, 1)], [])
    if converged:
        log.append("SIMPLE solution converged in %d iterations" % iters)
    log.append("End")
    open(os.path.join(lvl, "log.simpleFoam"), "w").write("\n".join(log) + "\n")

    import time as _t
    if stale:
        # answer written BEFORE 0/U -> the age guard must catch it
        for f in fields:
            open(os.path.join(tdir, f), "w").write("x\n")
        _t.sleep(0.02)
        open(os.path.join(lvl, "0", "U"), "a").write("// touched last\n")
    else:
        _t.sleep(0.02)
        for f in fields:
            open(os.path.join(tdir, f), "w").write("x\n")

    open(os.path.join(root, "RUN_RC.%s" % lv), "w").write(
        "rc = 0\nlevel = %s\nendTime = %d\ncore_min = 1.0\n" % (lv, endtime))
    return lvl


def _tree(tmp, A=0.05, p_true=2.0, **kw):
    """A synthetic r=2 family whose functional converges at EXACTLY p_true."""
    def base(y):
        return 4.0 * y * y * (1.0 - y) * 3.0 - 0.3 * math.sin(math.pi * y)
    for lv in LEVELS:
        h = 1.0 / MESH_NX[lv]
        eps = A * (h ** p_true)
        _write_level(tmp, lv, (lambda e: (lambda y: base(y) * (1.0 + e)))(eps),
                     iters={"L1": 741, "L2": 1500, "L3": 3100}[lv], **kw)
    return tmp


def selftest():
    print("SELFTEST %s comparator" % CASE_ID)
    n_assert = ast_guard()
    ck("AST guard: ast.Assert count is 0 in this file (was %d)" % n_assert, n_assert == 0)

    # --- cardinality ------------------------------------------------------------
    d = tempfile.mkdtemp(prefix="vmfl078_st_")
    try:
        os.makedirs(os.path.join(d, "a")); os.makedirs(os.path.join(d, "b"))
        open(os.path.join(d, "a", "U"), "w").write("x"); open(os.path.join(d, "b", "U"), "w").write("x")
        ck("one_match REFUSES on two matches", refuses(one_match, os.path.join(d, "*", "U"), "U"))
        ck("one_match REFUSES on zero matches", refuses(one_match, os.path.join(d, "zz", "U"), "U"))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # --- numeric time sorting ---------------------------------------------------
    d = tempfile.mkdtemp(prefix="vmfl078_st_")
    try:
        for n in ("0", "950", "2000", "0.orig"):
            os.makedirs(os.path.join(d, n))
        got = [t[1] for t in numeric_time_dirs(d)]
        ck("time dirs sort NUMERICALLY and exclude 0.orig (got %s)" % got, got == ["0", "950", "2000"])
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # --- Roache states ----------------------------------------------------------
    ck("roache CONVERGING at p=2 on an exact h^2 sequence",
       abs(roache(1.0 + 0.04, 1.0 + 0.01, 1.0 + 0.0025)["p"] - 2.0) < 1e-9)
    ck("roache DIVERGENT", roache(1.0, 1.1, 1.3)["state"] == "DIVERGENT")
    ck("roache OSCILLATORY", roache(1.0, 1.1, 1.05)["state"] == "OSCILLATORY")
    ck("roache EXACT", roache(1.0, 1.0, 1.0)["state"] == "EXACT")
    ck("roache never quotes GCI when not CONVERGING",
       roache(1.0, 1.1, 1.3)["gci_fine_pct"] is None)

    # --- rule 5 one-way and THE CEILING -----------------------------------------
    ck("rule 5 is ONE-WAY: a non-CONVERGING triple is NOT A RESULT whatever the value",
       verdict_limb_a({"state": "OSCILLATORY", "p": 2.0, "gci_fine_pct": 0.001}, True)[0] == "NOT A RESULT")
    ck("limb A GATE FAIL when p is outside the frozen band",
       verdict_limb_a({"state": "CONVERGING", "p": 0.4, "gci_fine_pct": 0.1}, True)[0] == "GATE FAIL")
    ck("limb A GATE FAIL when GCI exceeds the frozen band",
       verdict_limb_a({"state": "CONVERGING", "p": 2.0, "gci_fine_pct": 9.9}, True)[0] == "GATE FAIL")
    ck("limb A NOT A RESULT when iterative error is not 10x below the level difference",
       verdict_limb_a({"state": "CONVERGING", "p": 2.0, "gci_fine_pct": 0.1}, False)[0] == "NOT A RESULT")
    ck("limb B is BLOCKED and NOTHING ABOUT THE RUN CAN CHANGE IT", verdict_limb_b()[0] == "BLOCKED")
    ck("ROW verdict can NEVER be PASS -- the ceiling is GATE REACHED by construction",
       all(row_verdict(a, b) != "PASS" for a in VERDICTS for b in VERDICTS))
    ck("ROW verdict is GATE REACHED when limb A PASSes and limb B is BLOCKED",
       row_verdict("PASS", "BLOCKED") == "GATE REACHED")
    ck("ROW verdict NOT A RESULT dominates a limb-A NOT A RESULT",
       row_verdict("NOT A RESULT", "BLOCKED") == "NOT A RESULT")
    ck("every verdict emitted is in the FIXED vocabulary",
       all(row_verdict(a, b) in VERDICTS for a in VERDICTS for b in VERDICTS))

    # --- the gate functional is not an identity ---------------------------------
    ys = frozen_abscissae()
    ck("gate functional window EXCLUDES the exactly-imposed BC endpoints y=0 and y=1",
       ys[0] > 0.0 and ys[-1] < 1.0 and len(ys) == N_PROBE)
    ck("gate functional MOVES when the profile moves (not an identity)",
       abs(gate_functional([0.5] * N_PROBE) - gate_functional([0.6] * N_PROBE)) > 1e-6)
    ck("gate functional of a uniform profile equals its magnitude",
       abs(gate_functional([0.4] * N_PROBE) - 0.4) < 1e-12)

    # --- readers refuse rather than degrade -------------------------------------
    d = tempfile.mkdtemp(prefix="vmfl078_st_")
    try:
        p = os.path.join(d, "U")
        open(p, "w").write("# Probe\n   1  (0.1 0 0) (0.2 0 0)\n")
        ck("probe reader REFUSES on the wrong probe count", refuses(read_probe_ux, p))
        open(p, "w").write("# Probe\n   1  " + " ".join(["(nan 0 0)"] * N_PROBE) + "\n")
        ck("probe reader REFUSES on NaN (refuse, never degrade)", refuses(read_probe_ux, p))
        open(p, "w").write("# only a header\n")
        ck("probe reader REFUSES on a data-less file", refuses(read_probe_ux, p))
        ck("probe reader REFUSES on an absent file", refuses(read_probe_ux, os.path.join(d, "nope")))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # --- PLANTED ZERO, through the real path ------------------------------------
    d = tempfile.mkdtemp(prefix="vmfl078_st_")
    try:
        lvl = _write_level(d, "L1", lambda y: 0.3 * math.sin(math.pi * y))
        pl = planted_zero_control(lvl)
        ck("planted zero P1a: the gate reader SEES a %.3e single-probe plant (saw %.3e)"
           % (PLANT_DELTA, pl["P1a_seen"]), abs(pl["P1a_seen"] - PLANT_DELTA) < 1e-9)
        ck("planted zero P1b: the plant MOVES the GATE FUNCTIONAL (dJ = %.4e)" % pl["P1b_dJ"],
           abs(pl["P1b_dJ"]) > PLANT_MIN_ABS)
        ck("planted zero P1c: a BLIND writer leaves the functional UNMOVED (dJ = %.1e)"
           % pl["P1c_dJ_blind"], abs(pl["P1c_dJ_blind"]) <= PLANT_MIN_ABS)

        # a reader that CANNOT see its plant must be refused: emulate by planting into
        # a decoy while asserting movement -- done by handing the control a level whose
        # probe file is write-protected against the plant (zero-size plant).
        pz = planted_zero_control(lvl)
        ck("planted zero control is REPEATABLE (same J on an unmutated level)",
           abs(pz["J_unplanted"] - pl["J_unplanted"]) < 1e-15)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # --- the planted-zero control REFUSES a blind reader ------------------------
    d = tempfile.mkdtemp(prefix="vmfl078_st_")
    try:
        lvl = _write_level(d, "L1", lambda y: 0.3 * math.sin(math.pi * y))
        real = gate_functional
        try:
            globals()["gate_functional"] = lambda ux, ys=None: 0.123456   # a BLIND reader
            ck("planted zero REFUSES against a BLIND reader (constant output)",
               refuses(planted_zero_control, lvl))
        finally:
            globals()["gate_functional"] = real
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # --- BC provenance: the wrong-treatment mode is gated -----------------------
    d = tempfile.mkdtemp(prefix="vmfl078_st_")
    try:
        good = _write_level(d, "L1", lambda y: 0.1)
        bc = bc_provenance(good)
        ck("BC provenance accepts the registered case (symmetry = symmetryPlane)",
           bc["mesh_patch_types"]["symmetry"] == "symmetryPlane")
        bad = _write_level(d, "L2", lambda y: 0.1, sym_type="wall")
        ck("BC provenance REFUSES a WALL where the symmetry plane was registered "
           "(the named wrong treatment, which would otherwise still grid-converge)",
           refuses(bc_provenance, bad))
        bad2 = _write_level(d, "L3", lambda y: 0.1, lid=(0.5, 0.0, 0.0))
        ck("BC provenance REFUSES a lid velocity that is not the manual's 1 m/s",
           refuses(bc_provenance, bad2))
        # THE MESH-PATCH-TYPE CHECK NEEDS ITS OWN TEST.  My mutation control (M5)
        # measured that disabling it left the suite GREEN, because every earlier case
        # was ALSO caught by the 0/U check.  This case can only be caught by the mesh
        # check: constant/polyMesh/boundary says `wall`, 0/U still says `symmetryPlane`.
        skew = _write_level(d, "L1x", lambda y: 0.1, sym_type="wall",
                            sym_u_type="symmetryPlane")
        ck("BC provenance REFUSES a mesh/field DISAGREEMENT (polyMesh says wall, 0/U "
           "says symmetryPlane) -- the case only the mesh-patch-type check can catch",
           refuses(bc_provenance, skew))
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # --- strict completion + AGE GUARD ------------------------------------------
    d = tempfile.mkdtemp(prefix="vmfl078_st_")
    try:
        _write_level(d, "L1", lambda y: 0.1)
        c = completion(d, "L1")
        ck("strict completion GREEN on a well-formed converged level", c["complete"] is True)
        ck("strict completion reads rc from RUN_RC (rc=%s)" % c["rc"], c["rc"] == 0)
        ck("strict completion sees the End line", c["checks"]["End_line"] is True)
        ck("strict completion sees n_exec == steps written", c["checks"]["n_exec_matches_steps"] is True)
        ck("strict completion requires the converged stop BELOW endTime",
           c["checks"]["stopped_below_endTime"] is True)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    d = tempfile.mkdtemp(prefix="vmfl078_st_")
    try:
        _write_level(d, "L1", lambda y: 0.1, stale=True)
        c = completion(d, "L1")
        ck("AGE GUARD catches an answer OLDER than the case's own 0/U", c["checks"]["age_guard"] is False)
        ck("a level failing the age guard is NOT complete", c["complete"] is False)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    d = tempfile.mkdtemp(prefix="vmfl078_st_")
    try:
        _write_level(d, "L1", lambda y: 0.1, converged=False)
        c = completion(d, "L1")
        ck("a run that did NOT converge is NOT complete (rule 5 limb 1)", c["complete"] is False)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    d = tempfile.mkdtemp(prefix="vmfl078_st_")
    try:
        _write_level(d, "L1", lambda y: 0.1, fields=("U", "p"))
        c = completion(d, "L1")
        ck("strict completion catches a MISSING field (phi)", c["checks"]["fields_present"] is False)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # --- the comparator's abscissae must match the case that would run ----------
    here = os.path.dirname(os.path.abspath(__file__))
    cd = os.path.join(here, "case")
    if os.path.isdir(cd):
        a = check_abscissae(cd)
        ck("comparator abscissae == controlDict.template abscissae (%d locations, cellPoint present)"
           % a["n_locations"], a["n_locations"] == N_PROBE)
    d = tempfile.mkdtemp(prefix="vmfl078_st_")
    try:
        os.makedirs(os.path.join(d, "system"))
        # The 201 CORRECT locations, so the count and the abscissae both check out and
        # the ONLY defect is the missing cellPoint line.  My mutation control (M7)
        # measured that the earlier one-location version refused on the COUNT, leaving
        # the cellPoint requirement itself untested and free to be deleted.
        _ys = frozen_abscissae()
        _locs = "\n".join("        (%.10g %.10g %.10g)" % (X_LINE, y, Z_LINE) for y in _ys)
        open(os.path.join(d, "system", "controlDict.template"), "w").write(
            "functions{ centrelineProbe\n{\n  fields (U);\n  probeLocations\n  (\n"
            + _locs + "\n  );\n    }\n}\n")
        ck("check_abscissae REFUSES a controlDict with the RIGHT 201 abscissae but the "
           "cellPoint order-pollution fix DELETED", refuses(check_abscissae, d))
        # and the same file WITH cellPoint must be accepted, so the refusal above is
        # attributable to the missing fix and to nothing else.
        open(os.path.join(d, "system", "controlDict.template"), "w").write(
            "functions{ centrelineProbe\n{\n  interpolationScheme cellPoint;\n"
            "  fields (U);\n  probeLocations\n  (\n" + _locs + "\n  );\n    }\n}\n")
        ck("check_abscissae ACCEPTS the same file once cellPoint is restored "
           "(so the refusal above is the fix, not the format)",
           check_abscissae(d)["n_locations"] == N_PROBE)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # --- END TO END on a synthetic family that converges at EXACTLY p = 2 -------
    d = tempfile.mkdtemp(prefix="vmfl078_st_")
    try:
        _tree(d, A=0.05, p_true=2.0)
        rep = grade(d, case_dir=os.path.join(here, "case"))
        t = rep["triple_J"]
        ck("end-to-end triple is CONVERGING (state=%s)" % t["state"], t["state"] == "CONVERGING")
        ck("end-to-end observed order recovers the planted p=2 (got %.6f)" % t["p"],
           abs(t["p"] - 2.0) < 1e-6)
        ck("end-to-end limb A = PASS on its own terms (%s)" % rep["limb_a"]["verdict"],
           rep["limb_a"]["verdict"] == "PASS")
        ck("end-to-end limb B = BLOCKED", rep["limb_b"]["verdict"] == "BLOCKED")
        ck("END-TO-END ROW VERDICT IS `GATE REACHED`, NOT `PASS` (%s)" % rep["row_verdict"],
           rep["row_verdict"] == "GATE REACHED")
        ck("end-to-end GCI is quoted only with a CONVERGING triple",
           t["gci_fine_pct"] is not None and t["gci_fine_pct"] >= 0.0)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    # a family planted at p = 0.4 must GATE FAIL, not pass
    d = tempfile.mkdtemp(prefix="vmfl078_st_")
    try:
        _tree(d, A=0.05, p_true=0.4)
        rep = grade(d, case_dir=os.path.join(here, "case"))
        ck("a family converging at p=0.4 GATE FAILs the frozen band (%s)" % rep["limb_a"]["verdict"],
           rep["limb_a"]["verdict"] == "GATE FAIL")
        ck("and its ROW verdict is GATE FAIL, never GATE REACHED", rep["row_verdict"] == "GATE FAIL")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print()
    if _F[0] == 0:
        print("SELFTEST: all checks passed (%d/%d)" % (_P[0], _P[0]))
        return 0
    print("SELFTEST: %d FAILED of %d" % (_F[0], _P[0] + _F[0]))
    return 1


# -------------------------------------------------------------------- main -----
def main(argv):
    ap = argparse.ArgumentParser(description="VMFL078 comparator")
    ap.add_argument("--run-root")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verify-frozen", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.verify_frozen:
        print(json.dumps(verify_frozen(), indent=2, sort_keys=True))
        return 0
    if not a.run_root:
        ap.error("--run-root is required")
    rep = grade(a.run_root)
    txt = json.dumps(rep, indent=2, sort_keys=True, default=float)
    if a.out:
        open(a.out, "w").write(txt + "\n")
    print(txt)
    print("\nROW VERDICT: %s   (limb A %s / limb B %s)"
          % (rep["row_verdict"], rep["limb_a"]["verdict"], rep["limb_b"]["verdict"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
