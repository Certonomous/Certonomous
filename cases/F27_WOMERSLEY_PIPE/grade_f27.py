#!/usr/bin/env python3
"""
F27 -- THE GRADING PATH for pulsatile Womersley flow in a CIRCULAR PIPE on a
GENUINE 3-D BUTTERFLY (O-GRID) MESH (pimpleFoam in PISO mode, alpha = 4, locked
phase t = 5.25 = 5 T + T/4).  It calls `scripts/roache_triple.py::grade_ladder`
and rule 5 is reached through that call and through NOTHING ELSE (exactly one
call node, AST-censused).

REFUSAL DISCIPLINE: `raise` / `sys.exit(2)` only; ZERO `assert` across this
file, exact_f27.py, foam_io_f27.py, build_f27.py, proj_f27.py (L-332); hard
`-O` refusal.

THE FIELDS ARE READ FROM THE processor*/ DIRECTORIES (the run is decomposed on
4 ranks and never reconstructed; lineage cases/F25_DUCT3D/grade_f25.py): every
level's 0/C, 0/V and <t>/U are the concatenation over the RANKS processor
directories, each cell carrying its own centre and its own volume, so the
gate quantities never depend on a cell ordering.

TWO GATED QUANTITIES, both at the locked phase, both banded from ONE declared
parameter (exact_f27.BAND_FACTOR) applied to the COMPOSITE discretisation
model's prediction:

  G-F27-1  E2   = sqrt( sum V |U_h - U_exact|^2 / sum V ) / U_REF   (volume
                  weighted -- the butterfly's cells differ in volume by up to
                  3.7x, so an unweighted mean would grade the small cells twice)
  G-F27-2  Einf = max over cells of |u_z - u_exact(r)| / U_REF.  A DIFFERENT
                  norm of the same error field: L-infinity is set by the WORST
                  cell, which is where a wall-localized mode of the kind that
                  killed F21_WOMERSLEY's fine level would appear first.

ONE QUANTITY IS REPORTED AND NOT GATED, and the reason is measured, not
stylistic.  The bulk mean W = sum V u_z / sum V / U_REF is computed, its triple
is formed, its observed order and GCI are printed -- and NO VERDICT IS ATTACHED
TO IT.  At registration a zero-compute coarse pilot measured W's error against
the same-stencil reference as -7.27e-03 where the radial model predicted
+9.57e-04: WRONG SIGN, 7.6x magnitude.  A signed integral functional on this
mesh is dominated by the inscribed-polygon geometry and by cancellation, and
the registered model cannot predict it.  L-345's rule is that a quantity the
registered model cannot read is registered REPORTED-NOT-GATED rather than
banded around a prediction already known to be wrong.

THREE MORE REPORTED CHANNELS, all pure error because the exact solution is
identically axial, z-invariant and axisymmetric:
  E_perp   = sqrt( sum V (u_x^2 + u_y^2) / sum V ) / U_REF
  A_z      = axial non-uniformity: each cell against its own z-column's mean
  A_theta  = azimuthal non-uniformity: each cell against its image under the
             mesh's exact 90-degree rotation permutation

A_z AND A_theta ARE ALSO RULE 5 LIMB 1 STATES, not decoration.  F21_WOMERSLEY's
fine level DIVERGED into a smooth, wall-localized, two-dimensional mode in a
direction its exact solution is invariant along, and it was caught only because
that ladder happened to carry a plateau gate.  Here the invariance is tested
DIRECTLY: a level whose A_z or A_theta exceeds exact_f27.UNIFORMITY_FRACTION x
its OWN predicted E2 is NOT_UNIFORM, and rule 5 limb 1 turns the row into
NOT A RESULT through grade_ladder before any grid claim is made.

THE PLATEAU LIMB IS PERIODICITY, and it is measured, not assumed: at every
level the field at t = T_END - PERIOD is read and
||U(T_END) - U(T_END - T)||_2,V / U_REF must be <= exact_f27.PERIOD_TOL.
Rule 5 limb 1's iterative part is a CENSUS over EVERY time step's final Ux, Uy,
Uz and p residuals against the solver's own tolerances.

L-342: PHYSICS_CRITICAL and INFRASTRUCTURE field classes are declared below;
gates and refusals read the first only.
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: grade_f27.py must not run under `python3 -O` (the shared "
                     "roache_triple.py seals rule 1 and rule 5 with asserts that -O deletes).\n")
    sys.exit(2)

import os
import re
import ast
import json
import math
import time
import shutil
import tempfile
import argparse

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, HERE)

import roache_triple as RT              # THE GATE.
import exact_f27 as EX                  # THE EXACT SOLUTION and the discretisation model.
import foam_io_f27 as FIO               # THE READERS.

DIM = 3                                 # a GENUINE 3-D ladder: nc, nr and nz all refine by 2
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
LEVEL_NAMES = EX.LEVEL_NAMES
CELLS = EX.CELLS
STEPS = EX.STEPS
DT = dict((nm, EX.dt_of(EX.STEPS[nm])) for nm in LEVEL_NAMES)
END_TIME = EX.T_END
PREV_PERIOD_TIME = EX.T_END - EX.PERIOD
RANKS = EX.RANKS

CAP_CORE_MIN = 680.0                    # see the pre-registration section 8; run_f27.sh must agree
P_SOLVER_TOL = EX.P_SOLVER_TOL          # matches system/fvSolution, checked below
U_SOLVER_TOL = EX.U_SOLVER_TOL          # matches system/fvSolution, checked below

GATES = ("G-F27-1_E2_velocity_locked_phase", "G-F27-2_Einf_axial_velocity_locked_phase")
REPORTED_NOT_GATED = ("R-F27-W_bulk_mean_axial_velocity", "R-F27-E_perp_spurious_cross_flow",
                      "R-F27-A_z_axial_non_uniformity", "R-F27-A_theta_azimuthal_non_uniformity")

PHYSICS_CRITICAL = (
    "log.pimpleFoam `End` line and `Time =` count (fixed-deltaT identity)",
    "RC.txt (solver rc, written by the launcher in the shell that ran the solver)",
    "processor*/<endTime>/U and p present in every one of the RANKS directories and NEWER than the serial 0/U "
    "(age guard)",
    "processor*/<endTime - PERIOD>/U present (the periodicity limb)",
    "processor*/0/C cell centres and processor*/0/V cell volumes (every gate quantity is undefined without them)",
    "every time step's final Ux, Uy, Uz and p residual in log.pimpleFoam (rule 5 limb 1 census)",
)
INFRASTRUCTURE = (
    "ClockTime in log.pimpleFoam (cost actual)",
    "box_before.txt / box_after.txt",
    "MESH_LINE.txt (the mesh gate reading and the MESH_STANDARD 9.2 grading read-back)",
    "STATUS.* / launcher.queue.out / LAUNCH_LOG rows written by a queue runner",
    "calibration figures derived from any of the above",
)

WRITE_PATH_NOTE = (
    "OpenFOAM ascii volVectorField `U` at a write time inside a processor<k>/<t>/ directory: "
    "`internalField nonuniform List<vector>` NEWLINE N NEWLINE `(` one `(ux uy uz)` per line `)`; "
    "volVectorField `C` and volScalarField `V` in processor<k>/0/ written by `postProcess -func "
    "writeCellCentres` and `-func writeCellVolumes` before decomposePar; pinned against REAL solver "
    "output on this box, verification/runs/ansys_verification/VMFL019/L1_30/5/U, parsed at selftest.")
REAL_U_ON_BOX = os.path.join(REPO, "verification", "runs", "ansys_verification", "VMFL019", "L1_30", "5", "U")


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


# ---------------------------------------------------------------------------
# READERS -- concatenation over processor directories
# ---------------------------------------------------------------------------
def processor_dirs(case_dir, ranks=RANKS):
    dirs = sorted([d for d in os.listdir(case_dir) if re.fullmatch(r"processor[0-9]+", d)],
                  key=lambda s: int(s[9:]))
    if len(dirs) != ranks:
        refuse("%s holds %d processor directories, registered ranks %d" % (case_dir, len(dirs), ranks))
    return [os.path.join(case_dir, d) for d in dirs]


def _read_one(path, kind, what):
    if not os.path.isfile(path):
        refuse("no %s at %s; the gate quantity is ABSENT without it" % (what, path))
    try:
        F = FIO.read_field(path)
    except FIO.FieldFormatError as e:
        refuse("%s: %s. %s" % (path, e, WRITE_PATH_NOTE))
    if F["kind"] != kind or F["internal"] is None:
        refuse("%s is not a nonuniform %s field. %s" % (path, kind, WRITE_PATH_NOTE))
    return F["internal"]


def read_geometry(case_dir, ranks=RANKS):
    """(xyz, vol) concatenated over the processor directories, in processor order."""
    xyz, vol = [], []
    for pd in processor_dirs(case_dir, ranks):
        c = _read_one(os.path.join(pd, "0", "C"), "vector", "cell-centre file 0/C")
        v = _read_one(os.path.join(pd, "0", "V"), "scalar", "cell-volume file 0/V")
        if len(c) != len(v):
            refuse("%s: 0/C carries %d cells but 0/V carries %d" % (pd, len(c), len(v)))
        xyz.append(c); vol.append(v)
    XYZ, VOL = np.vstack(xyz), np.concatenate(vol)
    if float(np.min(VOL)) <= 0.0:
        refuse("%s carries a non-positive cell volume %.3e" % (case_dir, float(np.min(VOL))))
    return XYZ, VOL


def read_U_at(case_dir, t, ranks=RANKS):
    """<t>/U concatenated over the processor directories, in the SAME processor
    order read_geometry uses."""
    out = []
    for pd in processor_dirs(case_dir, ranks):
        d = _time_dir(pd, t)
        if d is None:
            refuse("no time directory at t = %g under %s" % (t, pd))
        out.append(_read_one(os.path.join(d, "U"), "vector", "velocity field U at t = %g" % t))
    return np.vstack(out)


def u_paths_at(case_dir, t, ranks=RANKS):
    paths = []
    for pd in processor_dirs(case_dir, ranks):
        d = _time_dir(pd, t)
        if d is None:
            refuse("no time directory at t = %g under %s" % (t, pd))
        paths.append(os.path.join(d, "U"))
    return paths


def _time_dir(base, t):
    if not os.path.isdir(base):
        return None
    for d in os.listdir(base):
        if re.fullmatch(r"[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?", d) and abs(float(d) - t) < 1e-9:
            return os.path.join(base, d)
    return None


# ---------------------------------------------------------------------------
# THE QUANTITIES
# ---------------------------------------------------------------------------
def _err(U, xyz, t=END_TIME):
    r = np.hypot(xyz[:, 0], xyz[:, 1])
    e = U.copy()
    e[:, 2] = e[:, 2] - EX.u_exact(r, t)
    return e


def e2_of(U, xyz, vol, t=END_TIME):
    """G-F27-1: volume-weighted L2 of the full velocity error / U_REF."""
    e = _err(U, xyz, t)
    return float(math.sqrt(np.sum(vol * np.sum(e ** 2, axis=1)) / np.sum(vol)) / EX.U_REF)


def einf_of(U, xyz, t=END_TIME):
    """G-F27-2: max over cells of |u_z - u_exact(r)| / U_REF."""
    return float(np.max(np.abs(_err(U, xyz, t)[:, 2])) / EX.U_REF)


def wbar_of(U, vol):
    """REPORTED: volume-weighted mean axial velocity / U_REF."""
    return float(np.sum(vol * U[:, 2]) / np.sum(vol) / EX.U_REF)


def eperp_of(U, vol):
    """REPORTED: the spurious cross-flow the exact solution has none of."""
    return float(math.sqrt(np.sum(vol * (U[:, 0] ** 2 + U[:, 1] ** 2)) / np.sum(vol)) / EX.U_REF)


def z_columns(xyz, nz):
    """Group cells into axial columns.  The mesh is a PRISMATIC EXTRUSION in z,
    so every (x, y) appears in exactly nz cells; anything else is refused."""
    key = np.round(xyz[:, :2], 9)
    order = np.lexsort((key[:, 1], key[:, 0]))
    ks = key[order]
    starts = np.concatenate([[0], np.nonzero(np.any(ks[1:] != ks[:-1], axis=1))[0] + 1, [len(ks)]])
    cols = [order[starts[i]:starts[i + 1]] for i in range(len(starts) - 1)]
    sizes = set(len(c) for c in cols)
    if sizes != {nz}:
        refuse("the mesh is not a prismatic extrusion of %d axial cells: column sizes %s" % (nz, sorted(sizes)))
    return cols


def rot90_permutation(xyz):
    """The mesh's EXACT 90-degree rotation permutation (x, y, z) -> (-y, x, z).
    The butterfly is 4-fold symmetric by construction, so every cell must map to
    a cell; a mesh where it does not is refused rather than approximated."""
    key = np.round(xyz, 9)
    lut = {}
    for i in range(len(key)):
        lut[(key[i, 0], key[i, 1], key[i, 2])] = i
    perm = np.empty(len(key), dtype=np.int64)
    for i in range(len(key)):
        j = lut.get((round(-float(key[i, 1]), 9), round(float(key[i, 0]), 9), float(key[i, 2])), -1)
        if j < 0:
            refuse("the mesh is not invariant under a 90-degree rotation: cell %d at (%.9f, %.9f, %.9f) has no "
                   "image" % (i, key[i, 0], key[i, 1], key[i, 2]))
        perm[i] = j
    if len(set(perm.tolist())) != len(perm):
        refuse("the 90-degree rotation map is not a permutation")
    return perm


def a_z_of(U, vol, cols):
    """REPORTED and LIMB-1: axial non-uniformity of u_z about each column's own
    volume-weighted mean.  The exact solution is z-invariant, so this is pure error."""
    acc = 0.0
    for idx in cols:
        w = vol[idx]
        m = float(np.sum(w * U[idx, 2]) / np.sum(w))
        acc += float(np.sum(w * (U[idx, 2] - m) ** 2))
    return float(math.sqrt(acc / np.sum(vol)) / EX.U_REF)


def a_theta_of(U, vol, perm):
    """REPORTED and LIMB-1: azimuthal non-uniformity, u_z against its own image
    under the mesh's exact 90-degree rotation.  Pure error for an axisymmetric
    exact solution.

    WHAT THIS INSTRUMENT CANNOT SEE, stated because a check that overstates its
    reach is worse than none.  The butterfly's symmetry group is D4, so an
    azimuthal error field that is ITSELF D4-invariant -- any cos(4k theta) mode,
    and those are exactly the modes the mesh's own four-block structure favours
    -- maps to itself under the rotation and reads EXACTLY ZERO here.  That
    blind spot is not left uncovered: a D4-invariant azimuthal error is a
    departure from the radial exact profile and is therefore carried in full by
    G-F27-1 (E2) and G-F27-2 (Einf), which compare every cell against
    u_exact(r) and have no null space.  A_theta covers the modes those norms
    weight least -- the wall-localized, non-axisymmetric kind that killed
    F21_WOMERSLEY's fine level -- and the planted control below uses wavenumber
    3 precisely because wavenumber 4 would be invisible by construction."""
    return float(math.sqrt(np.sum(vol * (U[:, 2] - U[perm, 2]) ** 2) / np.sum(vol)) / EX.U_REF)


def period_change_of(U_end, U_prev, vol):
    if U_end.shape != U_prev.shape:
        refuse("the endTime and endTime - PERIOD fields do not carry the same cells")
    d = U_end - U_prev
    return float(math.sqrt(np.sum(vol * np.sum(d ** 2, axis=1)) / np.sum(vol)) / EX.U_REF)


# ---------------------------------------------------------------------------
# PLANTED-ZERO CONTROLS (rule 3) -- into copies of the REAL processor files,
# read back with the REAL reader, refusing with exit 2.
# ---------------------------------------------------------------------------
def _plant_copy(case_dir, t, comp, delta, ranks=RANKS):
    """Copy the whole level's processor tree structure far enough to re-read a
    PLANTED <t>/U through the REAL reader.  Nothing under case_dir is touched."""
    tmp = tempfile.mkdtemp(prefix="f27_plant_")
    n_rows = 0
    for k, pd in enumerate(processor_dirs(case_dir, ranks)):
        dst_p = os.path.join(tmp, "processor%d" % k)
        os.makedirs(os.path.join(dst_p, "0"))
        os.makedirs(os.path.join(dst_p, str(t)))
        for f in ("C", "V"):
            shutil.copy(os.path.join(pd, "0", f), os.path.join(dst_p, "0", f))
        src_u = os.path.join(_time_dir(pd, t), "U")
        n_rows += FIO.plant_into_vector_file(src_u, os.path.join(dst_p, str(t), "U"), comp, delta)
    if n_rows == 0:
        refuse("nothing to plant into the level at %s" % case_dir)
    return tmp, n_rows


def plant_control(case_dir, gate, level, ranks=RANKS):
    """Plant RT.PLANT into the AXIAL component of EVERY cell of the real
    processor U files, re-read through the SAME function the grade uses, and
    require the reader to report EXACTLY the predicted move."""
    d = RT.PLANT
    xyz, vol = read_geometry(case_dir, ranks)
    U = read_U_at(case_dir, END_TIME, ranks)
    if gate == GATES[0]:
        before = e2_of(U, xyz, vol)
        e = _err(U, xyz)
        predicted = float(math.sqrt(np.sum(vol * (e[:, 0] ** 2 + e[:, 1] ** 2 + (e[:, 2] + d) ** 2))
                                    / np.sum(vol)) / EX.U_REF)
        reader = "e2_of"
    else:
        before = einf_of(U, xyz)
        predicted = float(np.max(np.abs(_err(U, xyz)[:, 2] + d)) / EX.U_REF)
        reader = "einf_of"
    tmp, n_rows = _plant_copy(case_dir, END_TIME, 2, d, ranks)
    try:
        Up = read_U_at(tmp, END_TIME, ranks)
        xyzp, volp = read_geometry(tmp, ranks)
        after = e2_of(Up, xyzp, volp) if gate == GATES[0] else einf_of(Up, xyzp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if abs(after - predicted) > 1e-12 * max(1.0, abs(predicted)):
        refuse("PLANTED-ZERO CONTROL FAILED for %s at level %s: an axial offset of %.6e must move the reader "
               "to %.17g; the reader returned %.17g" % (gate, level, d, predicted, after))
    if abs(after - before) < 1e-12:
        refuse("PLANTED-ZERO CONTROL FAILED for %s at level %s: the reader did not move at all (%.17g -> %.17g); "
               "a zero from a reader not shown able to see a non-zero is not evidence" % (gate, level, before, after))
    return RT.external_plant_control(reader, before, after, plant=(predicted - before),
                                     artifact=os.path.join(case_dir, "processor*", str(END_TIME), "U"),
                                     level=level)


# ---------------------------------------------------------------------------
# RULE 5 LIMB 1 -- iterative convergence, periodicity, uniformity
# ---------------------------------------------------------------------------
TIME_RE = re.compile(r"^Time = ([0-9eE+\-.]+)\s*$", re.M)
FINAL_RE = re.compile(r"Solving for (p|Ux|Uy|Uz), Initial residual = [0-9eE+\-.]+, "
                      r"Final residual = ([0-9eE+\-.]+)")


def iterative_state(log_path):
    if not os.path.isfile(log_path):
        refuse("no solver log at %s; rule 5 limb (1) cannot be evaluated" % log_path)
    vals = dict(p=[], Ux=[], Uy=[], Uz=[])
    for line in open(log_path, errors="replace"):
        m = FINAL_RE.search(line)
        if m:
            vals[m.group(1)].append(float(m.group(2)))
    for k in vals:
        if not vals[k]:
            refuse("no `Solving for %s ... Final residual` lines in %s; the iterative state is ABSENT"
                   % (k, log_path))
    tol = dict(p=P_SOLVER_TOL, Ux=U_SOLVER_TOL, Uy=U_SOLVER_TOL, Uz=U_SOLVER_TOL)
    bad = dict((k, sum(1 for v in vals[k] if v > tol[k])) for k in vals)
    detail = dict(basis="per-time-step final p, Ux, Uy and Uz residuals, census over ALL steps and correctors",
                  n_readings=dict((k, len(vals[k])) for k in vals), tolerances=tol,
                  n_above_tolerance=bad, worst=dict((k, max(vals[k])) for k in vals))
    nb = sum(bad.values())
    if nb:
        return "NOT_CONVERGED_%d_READINGS_ABOVE_TOL" % nb, detail
    return "CONVERGED", detail


def period_state(change):
    detail = dict(basis="||U(T_END) - U(T_END - PERIOD)||_2,V / U_REF over every cell",
                  change=change, tolerance=EX.PERIOD_TOL)
    if change > EX.PERIOD_TOL:
        return "NOT_PERIODIC_change_%.3e_above_%.1e" % (change, EX.PERIOD_TOL), detail
    return "PLATEAUED", detail


def uniformity_state(az, at, level):
    """THE F21 INSTRUMENT, MADE EXPLICIT.  A level whose axial or azimuthal
    non-uniformity exceeds UNIFORMITY_FRACTION x its OWN predicted E2 is
    NOT_UNIFORM and rule 5 limb 1 refuses the row."""
    tol = dict((r["name"], r["uniformity_tol"]) for r in EX.predictions())[level]
    detail = dict(basis="A_z (each cell against its own z-column mean) and A_theta (each cell against its "
                        "image under the mesh's exact 90-degree rotation), both volume weighted / U_REF",
                  A_z=az, A_theta=at, tolerance=tol,
                  tolerance_basis="exact_f27.UNIFORMITY_FRACTION x this level's predicted E2")
    if max(az, at) > tol:
        return "NOT_UNIFORM_A_z_%.3e_A_theta_%.3e_above_%.3e" % (az, at, tol), detail
    return "PLATEAUED", detail


# ---------------------------------------------------------------------------
# COMPLETION -- rule 4, PHYSICS_CRITICAL fields only
# ---------------------------------------------------------------------------
def completion(case_dir, log_path, level, ranks=RANKS):
    out = dict(case=case_dir, log=log_path)
    dt = DT[level]
    rc_path = os.path.join(case_dir, "RC.txt")
    if not os.path.isfile(rc_path):
        return dict(out, done=False, why="no RC.txt yet: rc not recorded; PENDING, not a verdict")
    rc = open(rc_path).read().strip()
    out["rc"] = rc
    if rc != "0":
        return dict(out, done=False, crashed=True,
                    why="recorded solver rc is %r: a crash is a FINDING (NOT A RESULT)" % rc)
    if not os.path.isfile(log_path):
        return dict(out, done=False, crashed=True, why="rc 0 but no solver log: NOT A RESULT")
    text = open(log_path, errors="replace").read()
    times = [float(m.group(1)) for m in TIME_RE.finditer(text)]
    out.update(n_times=len(times), latest=times[-1] if times else None, dt=dt)
    if not times:
        return dict(out, done=False, crashed=True, why="rc 0 but no `Time =` lines: NOT A RESULT")
    if "End" not in text:
        return dict(out, done=False, crashed=True, why="rc 0 recorded but no `End` line: NOT A RESULT")
    if not (times[-1] + dt > END_TIME):
        return dict(out, done=False, why="latest %.9g + dt %.9g does not exceed endTime %.9g"
                                         % (times[-1], dt, END_TIME))
    expected = int(round(END_TIME / dt))
    if len(times) != expected:
        return dict(out, done=False,
                    why="fixed-deltaT identity fails: %d `Time` lines, endTime/dt = %d" % (len(times), expected))
    zero_u = os.path.join(case_dir, "0", "U")
    if not os.path.isfile(zero_u):
        return dict(out, done=False, why="no serial 0/U to date the launch against (the age guard's datum)")
    t0 = os.path.getmtime(zero_u)
    pdirs = sorted([d for d in os.listdir(case_dir) if re.fullmatch(r"processor[0-9]+", d)],
                   key=lambda s: int(s[9:]))
    if len(pdirs) != ranks:
        return dict(out, done=False, why="%d processor directories, registered ranks %d" % (len(pdirs), ranks))
    missing, stale = [], []
    for d in pdirs:
        pd = os.path.join(case_dir, d)
        for f in ("C", "V"):
            if not os.path.isfile(os.path.join(pd, "0", f)):
                missing.append("%s/0/%s" % (d, f))
        ed = _time_dir(pd, END_TIME)
        if ed is None:
            missing.append("%s/%g" % (d, END_TIME)); continue
        prev = _time_dir(pd, PREV_PERIOD_TIME)
        if prev is None or not os.path.isfile(os.path.join(prev, "U")):
            return dict(out, done=False,
                        why="no U at t = endTime - PERIOD = %g in %s: the periodicity limb is ABSENT"
                            % (PREV_PERIOD_TIME, d))
        for f in ("U", "p"):
            fp = os.path.join(ed, f)
            if not os.path.isfile(fp):
                missing.append("%s/%g/%s" % (d, END_TIME, f))
            elif os.path.getmtime(fp) <= t0:
                stale.append("%s/%g/%s" % (d, END_TIME, f))
    if missing:
        return dict(out, done=False, why="physics-critical files missing: %s" % missing)
    if stale:
        return dict(out, done=False, why="AGE GUARD: %s are NOT newer than the serial 0/U" % stale)
    return dict(out, done=True,
                why="rc 0; End; latest + dt > endTime; %d `Time` lines == endTime/dt; U, p at endTime newer "
                    "than 0/U in all %d processor directories; U at endTime - PERIOD present; 0/C and 0/V "
                    "present" % (len(times), ranks))


# ---------------------------------------------------------------------------
# COST CLAIM -- INFRASTRUCTURE only (L-342)
# ---------------------------------------------------------------------------
def cost_claim(root):
    defects, spent = [], 0.0
    for name in LEVEL_NAMES:
        cd = os.path.join(root, name)
        if not os.path.isdir(cd):
            continue
        log = os.path.join(cd, "log.pimpleFoam")
        hits = re.findall(r"ClockTime = ([0-9]+) s", open(log, errors="replace").read()) \
            if os.path.isfile(log) else []
        if not hits:
            defects.append("BOOKKEEPING DEFECT: level %s has no ClockTime reading; cost actual NOT MEASURED"
                           % name)
        else:
            spent += float(hits[-1]) * RANKS / 60.0
        for probe in ("box_before.txt", "box_after.txt", "MESH_LINE.txt"):
            if not os.path.isfile(os.path.join(cd, probe)):
                defects.append("BOOKKEEPING DEFECT: level %s lacks %s; NOT MEASURED" % (name, probe))
    return dict(fields="INFRASTRUCTURE", core_min_claim=None if defects else spent,
                partial_sum_core_min=spent, cap_core_min=CAP_CORE_MIN, defects=defects,
                note="ClockTime x %d ranks / 60; dollars at $0.0513/core-h DERIVED, NOT MEASURED "
                     "(COMPUTE_BUDGET_CHARTER section 5: the box cannot read its own billing)" % RANKS)


# ---------------------------------------------------------------------------
# BANDS -- both from ONE declared parameter applied to the composite model
# ---------------------------------------------------------------------------
def bands():
    fine = dict((r["name"], r) for r in EX.predictions())["fine"]
    bf = EX.BAND_FACTOR
    return {
        GATES[0]: dict(band=(fine["E2_pred"] / bf, fine["E2_pred"] * bf), reference=0.0, dim=DIM,
                       prediction=fine["E2_pred"],
                       principle=("COMPOSITE discretisation-model prediction E2 = %.9e at the FINE level "
                                  "(radial cells %d, dt = %g, wall at the radius of the circle with the built "
                                  "mesh's own cross-sectional area R_eff = %.9f), times [1/%g, %g]"
                                  % (fine["E2_pred"], fine["model_nr"], fine["dt"], fine["r_eff"], bf, bf))),
        GATES[1]: dict(band=(fine["Einf_pred"] / bf, fine["Einf_pred"] * bf), reference=0.0, dim=DIM,
                       prediction=fine["Einf_pred"],
                       principle=("COMPOSITE discretisation-model prediction Einf = %.9e at the FINE level "
                                  "(same model, max over the model's radial cells), times [1/%g, %g]"
                                  % (fine["Einf_pred"], bf, bf))),
    }


# ---------------------------------------------------------------------------
# CENSUSES / CONTROLS ON THE INSTRUMENT ITSELF
# ---------------------------------------------------------------------------
def ast_no_asserts(paths):
    bad = {}
    for p in paths:
        lines = [n.lineno for n in ast.walk(ast.parse(open(p).read())) if isinstance(n, ast.Assert)]
        if lines:
            bad[p] = lines
    if bad:
        refuse("`assert` carries a check in this rung's own path (L-332): %s" % json.dumps(bad))
    if sum(1 for n in ast.walk(ast.parse("def f(x):\n    assert x\n")) if isinstance(n, ast.Assert)) != 1:
        refuse("the assert counter cannot see a planted assert")
    return dict(files_checked=len(paths), assert_nodes=0, planted_assert_seen=True)


def control_grade_ladder_is_called():
    src = open(os.path.abspath(__file__)).read()
    calls = [n.lineno for n in ast.walk(ast.parse(src))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "grade_ladder"]
    if len(calls) != 1:
        refuse("expected EXACTLY ONE grade_ladder CALL NODE; found %d at %s" % (len(calls), calls))
    pat = re.compile(r"RT\.grade_ladder\s*\(")
    if [ln for ln in "def f():\n    return 1\n".splitlines() if pat.search(ln)]:
        refuse("GREP CONTROL FAILED: matcher hit a file with no call")
    if not [ln for ln in "import x as RT\nz = RT.grade_ladder(q)\n".splitlines() if pat.search(ln)]:
        refuse("GREP CONTROL FAILED: matcher MISSED a planted call")
    return dict(control="PZ-F27-GRADE_LADDER_CALLSITE_ast_census_plus_grep_both_ways",
                ast_call_nodes=calls, passed=True)


def control_solver_dicts_match():
    cs = os.path.join(HERE, "case")
    tp = open(os.path.join(cs, "constant", "transportProperties")).read()
    m = re.search(r"^\s*nu\s+([0-9eE+\-.]+)\s*;", tp, re.M)
    if not m or abs(float(m.group(1)) - EX.NU) > 1e-15:
        refuse("transportProperties nu does not equal exact_f27.NU = %.17g" % EX.NU)
    if not re.search(r"simulationType\s+laminar\s*;",
                     open(os.path.join(cs, "constant", "turbulenceProperties")).read()):
        refuse("turbulenceProperties is not laminar")
    fs = open(os.path.join(cs, "system", "fvSolution")).read()
    m = re.search(r"\bp\b[^}]*?tolerance\s+([0-9eE+\-.]+)\s*;", fs, re.S)
    if not m or float(m.group(1)) != P_SOLVER_TOL:
        refuse("P_SOLVER_TOL = %g but fvSolution sets %s" % (P_SOLVER_TOL, m.group(1) if m else None))
    m = re.search(r"\(U\|UFinal\)\"[^}]*?tolerance\s+([0-9eE+\-.]+)\s*;", fs, re.S)
    if not m or float(m.group(1)) != U_SOLVER_TOL:
        refuse("U_SOLVER_TOL = %g but fvSolution sets %s" % (U_SOLVER_TOL, m.group(1) if m else None))
    if not re.search(r"nOuterCorrectors\s+1\s*;", fs):
        refuse("PIMPLE nOuterCorrectors is not 1 (PISO mode is registered)")
    if not re.search(r"nNonOrthogonalCorrectors\s+1\s*;", fs):
        refuse("nNonOrthogonalCorrectors is not 1; the butterfly reaches %g deg non-orthogonality and the "
               "non-orthogonal correction must be applied" % 40.5)
    sch = open(os.path.join(cs, "system", "fvSchemes")).read()
    if not re.search(r"ddtSchemes\s*\{\s*default\s+backward\s*;", sch):
        refuse("fvSchemes ddt is not `backward`; the model integrates BDF2")
    if not re.search(r"laplacianSchemes\s*\{\s*default\s+Gauss\s+linear\s+corrected\s*;", sch):
        refuse("fvSchemes laplacian is not `Gauss linear corrected`; on a non-orthogonal mesh `orthogonal` "
               "would silently make the diffusion term first order at the wall")
    if not re.search(r"snGradSchemes\s*\{\s*default\s+corrected\s*;", sch):
        refuse("fvSchemes snGrad is not `corrected`")
    cd = open(os.path.join(cs, "system", "controlDict.template")).read()
    me = re.search(r"^\s*endTime\s+([0-9.]+)\s*;", cd, re.M)
    if not me or abs(float(me.group(1)) - END_TIME) > 1e-12:
        refuse("controlDict.template endTime is not the registered %g" % END_TIME)
    mw = re.search(r"^\s*writeInterval\s+([0-9.]+)\s*;", cd, re.M)
    wi = float(mw.group(1)) if mw else 0.0
    if not wi or abs(EX.PERIOD / wi - round(EX.PERIOD / wi)) > 1e-12 \
            or abs(END_TIME / wi - round(END_TIME / wi)) > 1e-12:
        refuse("writeInterval does not divide both PERIOD and endTime; t = endTime - PERIOD would not be written")
    if not re.search(r"application\s+pimpleFoam\s*;", cd) or not re.search(r"adjustTimeStep\s+no\s*;", cd):
        refuse("controlDict.template does not register pimpleFoam on a FIXED time step")
    fo = open(os.path.join(cs, "constant", "fvOptions")).read()
    mf = re.search(r"type\s+cosine\s*;\s*frequency\s+([0-9.eE+\-]+)\s*;\s*amplitude\s+([0-9.eE+\-]+)\s*;"
                   r"\s*scale\s+\(\s*0\s+0\s+1\s*\)", fo)
    if not mf or abs(float(mf.group(1)) - EX.OMEGA / (2 * math.pi)) > 1e-15 \
            or abs(float(mf.group(2)) - EX.A_DRIVE) > 1e-15:
        refuse("fvOptions does not carry the registered cosine drive (frequency %.17g, amplitude %g, z-hat)"
               % (EX.OMEGA / (2 * math.pi), EX.A_DRIVE))
    if not re.search(r"volumeMode\s+specific\s*;", fo) or not re.search(r"selectionMode\s+all\s*;", fo):
        refuse("fvOptions drive is not a specific (per-volume) source over all cells")
    dp = open(os.path.join(cs, "system", "decomposeParDict")).read()
    md = re.search(r"numberOfSubdomains\s+([0-9]+)\s*;", dp)
    if not md or int(md.group(1)) != RANKS or not re.search(r"n\s+\(\s*1\s+1\s+4\s*\)", dp):
        refuse("decomposeParDict is not the registered simple (1 1 4) on %d subdomains" % RANKS)
    return dict(control="solver_dictionaries_agree_with_registration", nu=EX.NU, p_tol=P_SOLVER_TOL,
                U_tol=U_SOLVER_TOL, endTime=END_TIME, ddt="backward", laplacian="Gauss linear corrected",
                nNonOrthogonalCorrectors=1, drive="cosine f=1 A=1 z-hat, specific, all",
                decomposition="simple (1 1 4)", passed=True)


def control_reader_parses_real_solver_output():
    if not os.path.isfile(REAL_U_ON_BOX):
        refuse("the real solver output the format is pinned against is absent: %s" % REAL_U_ON_BOX)
    F = FIO.read_field(REAL_U_ON_BOX)
    if F["kind"] != "vector" or F["internal"] is None or F["internal"].shape != (120, 3):
        refuse("reader did not return 120 vectors from %s" % REAL_U_ON_BOX)
    return dict(control="reader_parses_real_solver_written_U_on_this_box", artifact=REAL_U_ON_BOX,
                cells=120, passed=True)


# ---------------------------------------------------------------------------
# SYNTHETIC LEVELS -- a real-format processor tree, used by every driven control
# ---------------------------------------------------------------------------
def synth_geometry(nrad, nang, nz):
    """A 4-fold-symmetric, prismatic cell-centre lattice in the REAL geometry:
    nrad radii, 4 x nang angles closed under a 90-degree rotation, nz z-layers.
    NOT the butterfly -- the readers grade numbers and cell centres, and the
    butterfly's own geometry is checked by build_f27.py against the built mesh."""
    rr = (np.arange(nrad) + 0.5) * (EX.R / nrad)
    th = (np.arange(nang) + 0.5) * (math.pi / 2.0 / nang)
    zz = (np.arange(nz) + 0.5) * (EX.LZ / nz)
    pts = []
    for z in zz:
        for r in rr:
            for t0 in th:
                for q in range(4):
                    t = t0 + q * math.pi / 2.0
                    pts.append((r * math.cos(t), r * math.sin(t), z))
    xyz = np.round(np.array(pts), 12)
    vol = np.full(len(xyz), (EX.R / nrad) * (math.pi / 2.0 / nang) * (EX.LZ / nz)) * np.hypot(xyz[:, 0], xyz[:, 1])
    return xyz, vol


def write_synth_level(root, xyz, vol, U, t=END_TIME, ranks=RANKS, u_prev=None):
    """Write a real-format decomposed level: processorK/0/{C,V} and
    processorK/<t>/U (and optionally <t - PERIOD>/U), split into `ranks` slabs."""
    n = len(xyz)
    cuts = [n * k // ranks for k in range(ranks + 1)]
    for k in range(ranks):
        a, b = cuts[k], cuts[k + 1]
        pd = os.path.join(root, "processor%d" % k)
        os.makedirs(os.path.join(pd, "0"), exist_ok=True)
        os.makedirs(os.path.join(pd, str(t)), exist_ok=True)
        open(os.path.join(pd, "0", "C"), "w").write(
            "FoamFile { version 2.0; format ascii; class volVectorField; object C; }\n"
            "dimensions [0 1 0 0 0 0 0];\ninternalField nonuniform List<vector> \n%s;\n"
            "boundaryField { wall { type calculated; } }\n" % FIO.fmt_list(xyz[a:b], "vector"))
        open(os.path.join(pd, "0", "V"), "w").write(
            "FoamFile { version 2.0; format ascii; class volScalarField; object V; }\n"
            "dimensions [0 3 0 0 0 0 0];\ninternalField nonuniform List<scalar> \n%s;\n"
            "boundaryField { wall { type calculated; } }\n" % FIO.fmt_list(vol[a:b], "scalar"))
        open(os.path.join(pd, str(t), "U"), "w").write(
            "FoamFile { version 2.0; format ascii; class volVectorField; object U; }\n"
            "dimensions [0 1 -1 0 0 0 0];\ninternalField nonuniform List<vector> \n%s;\n"
            "boundaryField { wall { type noSlip; } inlet { type cyclic; } outlet { type cyclic; } }\n"
            % FIO.fmt_list(U[a:b], "vector"))
        if u_prev is not None:
            os.makedirs(os.path.join(pd, str(t - EX.PERIOD)), exist_ok=True)
            open(os.path.join(pd, str(t - EX.PERIOD), "U"), "w").write(
                "FoamFile { version 2.0; format ascii; class volVectorField; object U; }\n"
                "dimensions [0 1 -1 0 0 0 0];\ninternalField nonuniform List<vector> \n%s;\n"
                "boundaryField { wall { type noSlip; } }\n" % FIO.fmt_list(u_prev[a:b], "vector"))
    return root


def synth_field(xyz, err_scale=0.0, az=0.0, at=0.0, perp=0.0):
    """The exact axial field at the lattice, plus optional planted defects: a
    smooth radial error (err_scale), an axial mode (az), an azimuthal mode (at)
    and a cross-flow (perp)."""
    r = np.hypot(xyz[:, 0], xyz[:, 1])
    th = np.arctan2(xyz[:, 1], xyz[:, 0])
    uz = EX.u_exact(r, END_TIME)
    uz = uz + err_scale * EX.U_REF * (1.0 - r ** 2)
    uz = uz + az * EX.U_REF * np.sin(2.0 * math.pi * xyz[:, 2] / EX.LZ)
    uz = uz + at * EX.U_REF * np.cos(3.0 * th)      # wavenumber 3: NOT D4-invariant, so A_theta can see it
    return np.column_stack([perp * EX.U_REF * np.ones(len(r)), np.zeros(len(r)), uz])


def control_readers_see_a_zero_and_a_planted_defect():
    """THE ZERO IS PLANTED (rule 3).  On a synthetic level carrying the EXACT
    field, every reader must return ZERO to round-off; each planted defect must
    then be seen by the reader that owns it AND by no other."""
    tmp = tempfile.mkdtemp(prefix="f27_zero_")
    rows = {}
    try:
        xyz, vol = synth_geometry(6, 5, 4)
        cols = z_columns(xyz, 4)
        perm = rot90_permutation(xyz)
        for tag, kw in (("clean", {}), ("radial", dict(err_scale=1e-3)), ("axial", dict(az=1e-3)),
                        ("azimuthal", dict(at=1e-3)), ("crossflow", dict(perp=1e-3))):
            root = os.path.join(tmp, tag)
            write_synth_level(root, xyz, vol, synth_field(xyz, **kw))
            X, V = read_geometry(root)
            U = read_U_at(root, END_TIME)
            rows[tag] = dict(E2=e2_of(U, X, V), Einf=einf_of(U, X), W=wbar_of(U, V),
                             E_perp=eperp_of(U, V), A_z=a_z_of(U, V, z_columns(X, 4)),
                             A_theta=a_theta_of(U, V, rot90_permutation(X)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    c = rows["clean"]
    for k in ("E2", "Einf", "E_perp", "A_z", "A_theta"):
        if abs(c[k]) > 1e-11:
            refuse("PLANTED-ZERO CONTROL FAILED: on the EXACT field the reader %s returned %.3e, not zero"
                   % (k, c[k]))
    # The bulk mean is an INTEGRAL, so on this deliberately tiny synthetic lattice
    # (6 radii x 20 angles x 4 layers) it carries the lattice's own quadrature
    # error, ~1e-02.  The tolerance is a SANITY bound on the reader, not a gate:
    # W is REPORTED-NOT-GATED and no verdict anywhere reads this number.
    if abs(c["W"] - EX.u_bulk_exact_continuum()) > 2e-2:
        refuse("on the EXACT field the bulk mean read %.9f, far from the continuum %.9f"
               % (c["W"], EX.u_bulk_exact_continuum()))
    checks = (("radial", "E2", ("A_z", "A_theta", "E_perp")), ("axial", "A_z", ("E_perp",)),
              ("azimuthal", "A_theta", ("A_z", "E_perp")), ("crossflow", "E_perp", ("A_z", "A_theta")))
    for tag, must_see, must_not in checks:
        if rows[tag][must_see] < 1e-5:
            refuse("PLANTED CONTROL FAILED: the %s defect was NOT seen by %s (%.3e)"
                   % (tag, must_see, rows[tag][must_see]))
        for k in must_not:
            if rows[tag][k] > 1e-11:
                refuse("PLANTED CONTROL FAILED: the %s defect leaked into %s (%.3e); the channels are not "
                       "independent" % (tag, k, rows[tag][k]))
    return dict(control="PZ-F27-READERS_zero_on_the_exact_field_and_four_planted_defects_each_seen_by_its_own_"
                        "channel_and_no_other", readings=rows,
                azimuthal_plant_wavenumber=3,
                declared_blind_spot="A_theta reads exactly zero on any D4-invariant azimuthal mode "
                                    "(wavenumber 4k), which is why the plant is wavenumber 3; that class of "
                                    "error is carried in full by G-F27-1 and G-F27-2, which have no null space",
                passed=True)


def control_period_and_uniformity_can_say_no():
    """Driven both ways: a level identical one period earlier is PLATEAUED and a
    level with a planted period-to-period change is NOT_PERIODIC; a uniform level
    is PLATEAUED and a level with a planted axial or azimuthal mode is
    NOT_UNIFORM."""
    tmp = tempfile.mkdtemp(prefix="f27_period_")
    try:
        xyz, vol = synth_geometry(6, 5, 4)
        U = synth_field(xyz)
        root = os.path.join(tmp, "a")
        write_synth_level(root, xyz, vol, U, u_prev=U)
        X, V = read_geometry(root)
        same = period_change_of(read_U_at(root, END_TIME), read_U_at(root, PREV_PERIOD_TIME), V)
        root2 = os.path.join(tmp, "b")
        Ub = U.copy(); Ub[:, 2] = Ub[:, 2] + RT.PLANT
        write_synth_level(root2, xyz, vol, Ub, u_prev=U)
        X2, V2 = read_geometry(root2)
        moved = period_change_of(read_U_at(root2, END_TIME), read_U_at(root2, PREV_PERIOD_TIME), V2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if same > 1e-13:
        refuse("PERIODICITY CONTROL FAILED: two identical fields read a change of %.3e" % same)
    if abs(moved - RT.PLANT / EX.U_REF) > 1e-11:
        refuse("PERIODICITY CONTROL FAILED: a planted uniform axial offset %.6e must read as %.6e; the reader "
               "returned %.6e" % (RT.PLANT, RT.PLANT / EX.U_REF, moved))
    s_ok, _ = period_state(same)
    s_bad, _ = period_state(moved)
    if s_ok != "PLATEAUED" or not s_bad.startswith("NOT_PERIODIC"):
        refuse("PERIODICITY STATE CONTROL FAILED: %s / %s" % (s_ok, s_bad))
    tol = dict((r["name"], r["uniformity_tol"]) for r in EX.predictions())
    u_ok, _ = uniformity_state(0.0, 0.0, "fine")
    u_bad_z, _ = uniformity_state(10.0 * tol["fine"], 0.0, "fine")
    u_bad_t, _ = uniformity_state(0.0, 10.0 * tol["fine"], "fine")
    if u_ok != "PLATEAUED" or not u_bad_z.startswith("NOT_UNIFORM") or not u_bad_t.startswith("NOT_UNIFORM"):
        refuse("UNIFORMITY STATE CONTROL FAILED: %s / %s / %s" % (u_ok, u_bad_z, u_bad_t))
    worst = max(r["period_change_pred"] for r in EX.predictions())
    if EX.PERIOD_TOL < 10.0 * worst:
        refuse("PERIOD_TOL %.1e is below 10x the model's predicted period-to-period change %.3e"
               % (EX.PERIOD_TOL, worst))
    return dict(control="PZ-F27-PERIODICITY_AND_UNIFORMITY_driven_both_ways_with_a_planted_change_and_"
                        "planted_axial_and_azimuthal_modes",
                identical_fields=same, planted_change=moved, expected_planted=RT.PLANT / EX.U_REF,
                uniformity_tolerances=tol, model_worst_period_change=worst, passed=True)


def control_iterative_census_can_say_no():
    tmp = tempfile.mkdtemp(prefix="f27_iter_")
    try:
        lg = os.path.join(tmp, "log")
        good = ("Time = 0.01\n"
                "DILUPBiCGStab:  Solving for Ux, Initial residual = 1, Final residual = 5e-13, No Iterations 3\n"
                "DILUPBiCGStab:  Solving for Uy, Initial residual = 1, Final residual = 4e-13, No Iterations 3\n"
                "DILUPBiCGStab:  Solving for Uz, Initial residual = 1, Final residual = 6e-13, No Iterations 3\n"
                "DICPCG:  Solving for p, Initial residual = 0.5, Final residual = 9e-11, No Iterations 40\n"
                "DICPCG:  Solving for p, Initial residual = 0.1, Final residual = 8e-11, No Iterations 30\n")
        open(lg, "w").write(good * 3)
        s1, _ = iterative_state(lg)
        open(lg, "w").write(good * 2 + good.replace("Final residual = 8e-11", "Final residual = 2e-09"))
        s2, _ = iterative_state(lg)
        open(lg, "w").write(good * 2 + good.replace("Final residual = 6e-13", "Final residual = 3e-11"))
        s3, _ = iterative_state(lg)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if s1 != "CONVERGED" or not s2.startswith("NOT_CONVERGED_1") or not s3.startswith("NOT_CONVERGED_1"):
        refuse("ITERATIVE CENSUS CONTROL FAILED: %s / %s / %s" % (s1, s2, s3))
    return dict(control="PZ-F27-ITERATIVE_census_flags_one_bad_p_and_one_bad_Uz_reading",
                clean=s1, bad_p=s2, bad_Uz=s3, passed=True)


def control_field_classes_separate():
    """L-342, DRIVEN BOTH WAYS: deleting an INFRASTRUCTURE field refuses the cost
    claim and prints a defect line while leaving completion untouched; corrupting
    a PHYSICS_CRITICAL field flips the level to NOT A RESULT."""
    tmp = tempfile.mkdtemp(prefix="f27_l342_")
    try:
        cd = os.path.join(tmp, "coarse")
        os.makedirs(os.path.join(cd, "0"))
        open(os.path.join(cd, "0", "U"), "w").write("x")
        time.sleep(0.02)
        n, dt = STEPS["coarse"], DT["coarse"]
        body = "".join("Time = %.10g\n" % ((i + 1) * dt) for i in range(n)) + "ClockTime = 3 s\nEnd\n"
        open(os.path.join(cd, "log.pimpleFoam"), "w").write(body)
        open(os.path.join(cd, "RC.txt"), "w").write("0\n")
        for probe in ("box_before.txt", "box_after.txt", "MESH_LINE.txt"):
            open(os.path.join(cd, probe), "w").write("{}\n")
        for k in range(RANKS):
            pd = os.path.join(cd, "processor%d" % k)
            os.makedirs(os.path.join(pd, "0"))
            os.makedirs(os.path.join(pd, str(END_TIME)))
            os.makedirs(os.path.join(pd, str(PREV_PERIOD_TIME)))
            for f in ("C", "V"):
                open(os.path.join(pd, "0", f), "w").write("y")
            for f in ("U", "p"):
                open(os.path.join(pd, str(END_TIME), f), "w").write("y")
            open(os.path.join(pd, str(PREV_PERIOD_TIME), "U"), "w").write("y")
        log = os.path.join(cd, "log.pimpleFoam")
        if not completion(cd, log, "coarse")["done"]:
            refuse("L-342 CONTROL: a complete synthetic level was not accepted: %s"
                   % completion(cd, log, "coarse")["why"])
        cc_ok = cost_claim(tmp)
        if cc_ok["core_min_claim"] is None or cc_ok["defects"]:
            refuse("L-342 CONTROL: a complete level did not produce a cost claim: %s" % cc_ok["defects"])
        os.remove(os.path.join(cd, "MESH_LINE.txt"))
        cc = cost_claim(tmp)
        if cc["core_min_claim"] is not None or not cc["defects"] or not completion(cd, log, "coarse")["done"]:
            refuse("L-342 CONTROL: missing infrastructure did not refuse the cost claim with defect lines "
                   "while leaving completion untouched")
        open(os.path.join(cd, "MESH_LINE.txt"), "w").write("{}\n")
        os.remove(os.path.join(cd, "processor0", str(PREV_PERIOD_TIME), "U"))
        if completion(cd, log, "coarse")["done"]:
            refuse("L-342 CONTROL: a missing U at endTime - PERIOD was accepted as complete")
        open(os.path.join(cd, "processor0", str(PREV_PERIOD_TIME), "U"), "w").write("y")
        open(os.path.join(cd, "RC.txt"), "w").write("134\n")
        if not completion(cd, log, "coarse").get("crashed"):
            refuse("L-342 CONTROL: a non-zero rc did not flip the level to NOT A RESULT")
        open(os.path.join(cd, "RC.txt"), "w").write("0\n")
        open(log, "w").write(body.replace("End\n", ""))
        if not completion(cd, log, "coarse").get("crashed"):
            refuse("L-342 CONTROL: a missing End line with rc 0 did not flip the level to NOT A RESULT")
        open(log, "w").write(body)
        os.utime(os.path.join(cd, "processor1", str(END_TIME), "U"),
                 (os.path.getmtime(os.path.join(cd, "0", "U")) - 5,) * 2)
        c = completion(cd, log, "coarse")
        if c["done"] or "AGE GUARD" not in c["why"]:
            refuse("L-342 CONTROL: a field OLDER than 0/U did not trip the age guard: %s" % c["why"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dict(control="PZ-F27-L342_infrastructure_vs_physics_fields_driven_both_ways_incl_age_guard",
                infrastructure_deleted="verdict channel unchanged, cost claim refused, defect lines printed",
                physics_corrupted="NOT A RESULT", age_guard="tripped by a stale endTime field", passed=True)


def demonstrate(bnd):
    """ZERO COMPUTE.  Each gate is shown able to take a value INSIDE and a value
    OUTSIDE its pre-registered band, through the REAL reader on the REAL write
    format, and the planted-zero control is exercised on the same artifacts."""
    tmp = tempfile.mkdtemp(prefix="f27_demo_")
    rows = []
    try:
        xyz, vol = synth_geometry(8, 6, 4)
        fine = dict((r["name"], r) for r in EX.predictions())["fine"]
        # the error amplitude that reproduces the model's predicted E2 on this lattice
        probe = os.path.join(tmp, "probe")
        write_synth_level(probe, xyz, vol, synth_field(xyz, err_scale=1.0))
        Xp, Vp = read_geometry(probe)
        unit_e2 = e2_of(read_U_at(probe, END_TIME), Xp, Vp)
        unit_ei = einf_of(read_U_at(probe, END_TIME), Xp)
        for scale, want in ((fine["E2_pred"] / unit_e2, "inside"), (40.0 * fine["E2_pred"] / unit_e2, "outside")):
            root = os.path.join(tmp, "s%s" % want)
            write_synth_level(root, xyz, vol, synth_field(xyz, err_scale=scale))
            X, V = read_geometry(root)
            U = read_U_at(root, END_TIME)
            for gate, val in ((GATES[0], e2_of(U, X, V)), (GATES[1], einf_of(U, X))):
                lo, hi = bnd[gate]["band"]
                rows.append(dict(gate=gate, construction="exact(T) + %.4g x a smooth radial error field" % scale,
                                 value=val, band=[lo, hi], inside=bool(lo <= val <= hi), intended=want))
            if want == "inside":
                for gate in GATES:
                    pc = plant_control(root, gate, "synthetic")
                    if not pc["passed"]:
                        refuse("the planted-zero control did not pass on the demonstration level for %s" % gate)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for r in rows:
        if (r["intended"] == "inside") != r["inside"]:
            refuse("GATE DEMONSTRATION FAILED for %s: intended %s, got %.6g against %s"
                   % (r["gate"], r["intended"], r["value"], r["band"]))
    seen = set((r["gate"], r["inside"]) for r in rows)
    for g in bnd:
        if (g, True) not in seen or (g, False) not in seen:
            refuse("gate %s was not shown able to take BOTH values" % g)
    return rows


# ---------------------------------------------------------------------------
# THE GRADE
# ---------------------------------------------------------------------------
def measure_level(root, name):
    """Every quantity this level contributes, read ONCE."""
    case_dir = os.path.join(root, name)
    if not os.path.isdir(case_dir):
        return dict(name=name, present=False, why="level %r absent from %s" % (name, root))
    log = os.path.join(case_dir, "log.pimpleFoam")
    comp = completion(case_dir, log, name)
    if not comp["done"]:
        return dict(name=name, present=True, done=False, completion=comp, why=comp["why"])
    xyz, vol = read_geometry(case_dir)
    if len(vol) != CELLS[name]:
        refuse("level %s carries %d cells, the registration froze %d" % (name, len(vol), CELLS[name]))
    U = read_U_at(case_dir, END_TIME)
    Up = read_U_at(case_dir, PREV_PERIOD_TIME)
    nz = EX.NCNRNZ[name][2]
    cols = z_columns(xyz, nz)
    perm = rot90_permutation(xyz)
    az, at = a_z_of(U, vol, cols), a_theta_of(U, vol, perm)
    it_state, it_detail = iterative_state(log)
    pd_state, pd_detail = period_state(period_change_of(U, Up, vol))
    un_state, un_detail = uniformity_state(az, at, name)
    return dict(name=name, present=True, done=True, completion=comp, cells=CELLS[name],
                artifact=os.path.join(case_dir, "processor*", str(END_TIME), "U"),
                E2=e2_of(U, xyz, vol), Einf=einf_of(U, xyz), W=wbar_of(U, vol), E_perp=eperp_of(U, vol),
                A_z=az, A_theta=at, W_ref_mesh=EX.W_REF_MESH[name],
                W_minus_ref=wbar_of(U, vol) - EX.W_REF_MESH[name],
                iterative=it_state, iterative_detail=it_detail,
                plateau=pd_state, plateau_detail=pd_detail,
                uniformity=un_state, uniformity_detail=un_detail,
                case_dir=case_dir)


def grade_one(gate, bnd, measured):
    key = "E2" if gate == GATES[0] else "Einf"
    for m in measured:
        if not m.get("present"):
            return dict(gate=gate, verdict="PENDING", note=m["why"])
        if not m.get("done"):
            v = "NOT A RESULT" if m["completion"].get("crashed") else "PENDING"
            return dict(gate=gate, verdict=v, note="level %r: %s" % (m["name"], m["why"]), completion=m["completion"])
    levels = [dict(name=m["name"], cells=m["cells"], value=m[key]) for m in measured]
    pc = plant_control(measured[-1]["case_dir"], gate, measured[-1]["name"])
    spec = bnd[gate]
    plateau_states = {}
    for m in measured:
        plateau_states[m["name"]] = m["plateau"]
        plateau_states["%s/uniformity" % m["name"]] = m["uniformity"]
    # ---- THE ONE AND ONLY GATE CALL.  Rule 5 is reached here and nowhere else.
    row = RT.grade_ladder(
        quantity=gate, levels=levels, dim=spec["dim"], band=spec["band"], plant_control=pc,
        iterative_states=dict((m["name"], m["iterative"]) for m in measured),
        plateau_states=plateau_states, reference=spec["reference"])
    row["gate"] = gate
    row["band_principle"] = spec["principle"]
    row["model_prediction_at_fine"] = spec["prediction"]
    row["levels_detail"] = [dict((k, v) for k, v in m.items() if k not in ("case_dir",)) for m in measured]
    row["plateau_note"] = ("two plateau-class limbs, both measured at every level: PERIODICITY "
                           "(||U(T) - U(T-T)||_2,V / U_REF <= %g) and UNIFORMITY (A_z and A_theta <= %g x "
                           "that level's own predicted E2) -- the second is the instrument that would have "
                           "caught F21_WOMERSLEY's wall-localized mode directly"
                           % (EX.PERIOD_TOL, EX.UNIFORMITY_FRACTION))
    row["gated_by"] = ("scripts/roache_triple.py::grade_ladder -- rule 5 is reached through this call and "
                       "through nothing else")
    if row["verdict"] not in VERDICTS:
        refuse("%s produced a verdict outside the fixed vocabulary: %r" % (gate, row["verdict"]))
    return row


def report_not_gated(measured):
    """The bulk mean and the three symmetry channels: value, triple, order and
    GCI computed and PRINTED, and NO VERDICT attached (L-345's remedy for a
    quantity the registered model cannot predict)."""
    out = []
    if not all(m.get("done") for m in measured):
        return [dict(quantity=q, verdict=None, note="PENDING: not every level is complete")
                for q in REPORTED_NOT_GATED]
    cells = tuple(m["cells"] for m in measured)
    for q, key in (("R-F27-W_bulk_mean_axial_velocity", "W"),
                   ("R-F27-E_perp_spurious_cross_flow", "E_perp"),
                   ("R-F27-A_z_axial_non_uniformity", "A_z"),
                   ("R-F27-A_theta_azimuthal_non_uniformity", "A_theta")):
        vals = tuple(m[key] for m in measured)
        try:
            tr = RT.triple_from_cells(vals[0], vals[1], vals[2], cells[0], cells[1], cells[2], dim=DIM)
            state, order = tr["state"], tr.get("order")
            gci = tr.get("GCI_pct")
        except RT.Refusal as e:                                     # noqa: BLE001
            state, order, gci = "REFUSED(%s)" % e, None, None
        out.append(dict(quantity=q, verdict=None, values=dict(zip(LEVEL_NAMES, vals)), dim=DIM,
                        triple_state=state, observed_order=order, GCI_pct=gci,
                        why="REPORTED-NOT-GATED: no verdict is attached to this quantity. "
                            + ("The registered model mis-predicts the bulk mean's error on this mesh by SIGN "
                               "and by 7.6x (coarse pilot, before freeze), so a band around it would be a "
                               "band around a prediction already known to be wrong (L-345's remedy)."
                               if key == "W" else
                               "This channel is pure error for an exactly axial, z-invariant, axisymmetric "
                               "solution; A_z and A_theta additionally enter rule 5 limb 1 as UNIFORMITY "
                               "states, where they DO bite.")))
    return out


def selftest_predicate(controls, demo, census):
    if census["assert_nodes"] != 0:
        return False, "assert nodes present"
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if len(demo) != 4:
        return False, "expected 4 demonstration rows, got %d" % len(demo)
    if not __debug__:
        return False, "running under -O"
    return True, ("%d controls green; both GATED quantities shown able to take a passing AND a failing value "
                  "through the real reader on the pinned decomposed write format, with the planted-zero "
                  "control exercised on the same artifacts; every reader returns ZERO on the exact field and "
                  "each of four planted defects is seen by its own channel and by no other; periodicity and "
                  "both uniformity limbs driven in both directions; 0 assert nodes across 5 files; exactly "
                  "one grade_ladder call node; __debug__ True" % len(controls))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(REPO, "verification", "runs", "F27_WOMERSLEY_PIPE_runs"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--prereg-commit")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    census = ast_no_asserts([os.path.abspath(__file__), os.path.join(HERE, "exact_f27.py"),
                             os.path.join(HERE, "foam_io_f27.py"), os.path.join(HERE, "build_f27.py"),
                             os.path.join(HERE, "proj_f27.py")])
    controls = [EX.control_symbolic_substitution(), EX.control_substitution_is_able_to_fail(),
                EX.control_bessel_two_independent_implementations(),
                EX.control_ladder_is_geometrically_similar(),
                EX.control_model_is_second_order_and_sensitive(),
                EX.control_L345_model_triples_are_gradeable(),
                EX.control_L346_resolution_derived_from_this_ladder(),
                EX.control_diffusion_number_and_courant(),
                EX.control_same_stencil_reference_is_pinned(),
                control_grade_ladder_is_called(), control_solver_dicts_match(),
                control_reader_parses_real_solver_output(),
                control_readers_see_a_zero_and_a_planted_defect(),
                control_period_and_uniformity_can_say_no(),
                control_iterative_census_can_say_no(), control_field_classes_separate()]
    bnd = bands()
    demo = demonstrate(bnd)

    if a.selftest:
        ok, why = selftest_predicate(controls, demo, census)
        print(json.dumps(dict(assert_census=census, controls=controls,
                              bands=dict((k, dict(band=v["band"], reference=v["reference"],
                                                  prediction=v["prediction"], principle=v["principle"]))
                                         for k, v in bnd.items()),
                              reported_not_gated=list(REPORTED_NOT_GATED),
                              model_levels=EX.predictions(), gate_demonstration=demo,
                              write_path=WRITE_PATH_NOTE, cap_core_min=CAP_CORE_MIN,
                              predicate=dict(ok=ok, why=why)), indent=2, default=str))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)
        return 0

    if not a.prereg_commit:
        refuse("--prereg-commit is required for a real grade (rule 2)")
    measured = [measure_level(a.root, nm) for nm in LEVEL_NAMES]
    rows = [grade_one(g, bnd, measured) for g in GATES]
    reported = report_not_gated(measured)
    cost = cost_claim(a.root)
    out = a.out or os.path.join(a.root, "F27_GRADED.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(dict(rung="F27-WOMERSLEY-PIPE-3D", prereg_commit=a.prereg_commit,
                       prereg="verification/campaign/F27_WOMERSLEY_PIPE_PREREGISTRATION.md",
                       capability_cell="3D . unsteady . incompressible",
                       assert_census=census, controls=controls, gate_demonstration=demo,
                       write_path=WRITE_PATH_NOTE, cap_core_min=CAP_CORE_MIN,
                       field_classes=dict(PHYSICS_CRITICAL=PHYSICS_CRITICAL, INFRASTRUCTURE=INFRASTRUCTURE),
                       cost_claim=cost, rows=rows, reported_not_gated=reported), f, indent=2, default=str)
    print("F27 -- WOMERSLEY PULSATILE PIPE, 3-D BUTTERFLY LADDER -- TALLY")
    print("=" * 78)
    for r in rows:
        print("%-42s %s" % (r["gate"], r["verdict"]))
        for k in ("why", "note"):
            if k in r:
                print("    %s" % r[k])
    print("-" * 78)
    for r in reported:
        print("%-42s REPORTED-NOT-GATED  %s" % (r["quantity"], r.get("triple_state", "")))
        if r.get("values"):
            print("    values %s  order %s  GCI %s"
                  % (r["values"], r.get("observed_order"), r.get("GCI_pct")))
    print("=" * 78)
    for dline in cost["defects"]:
        print(dline)
    if cost["core_min_claim"] is None:
        print("COST CLAIM REFUSED (infrastructure fields missing); physics verdicts above are unaffected (L-342)")
    else:
        print("cost actual: %.3f core-min of cap %.1f (ClockTime x %d ranks / 60; dollars derived, not measured)"
              % (cost["core_min_claim"], CAP_CORE_MIN, RANKS))
    print("gated by: scripts/roache_triple.py::grade_ladder")
    print("written: %s" % out)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RT.Refusal as e:
        sys.stderr.write("REFUSED (roache_triple): %s\n" % e)
        sys.exit(2)
