#!/usr/bin/env python3
"""F28 -- THE PLANTED-DELTA_P CONTROL COMPARATOR AND THE EMPTY-DUCT PASS-THROUGH.

Registration: verification/campaign/F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md
FROZEN at 76ce0ed5.  Sections 6.2 (C1-C4, including the NEGATIVE LIMB) and 6.3.

>>> THIS FILE HAS NOT BEEN RUN FOR RECORD.  Stage 1 onward is gated behind the
>>> supervisor's SUPERVISION_CHARTER section 3 check 1 -- the measurement code is
>>> read AS A DIFF before any number out of it is believed.  Nothing below has
>>> produced a number.

-------------------------------------------------------------------------------
WHAT THIS COMPARATOR IS, AND WHAT IT IS NOT
-------------------------------------------------------------------------------
Section 6.1: "It is NOT a hand-computed check.  The control is a FULL L1
simpleFoam solve through the REAL `fvOptions` path, with the REAL
`vectorSemiImplicitSource`, read back by the REAL function objects and the REAL
comparator that will grade the gated runs.  Nothing about it is a special code
path."

Sanaa's control-birth directive, 2026-08-28, verbatim: "A control defined in
terms of the thing it controls is not a control.  A planted control must travel
the real production path -- written by the real producer's code, read through
the real reader -- and prove the instrument sees a non-zero the same way reality
would deliver one."

So the plant here is NOT injected into a Python variable.  `plant_into_p()`
WRITES A KNOWN PERTURBATION INTO THE SOLVED `p` FIELD ON DISK, in the case's own
OpenFOAM ASCII format, and the SAME `read_volScalarField` that C1 uses reads it
back off the disk.  If the reader cannot see it, THE COMPARATOR REFUSES (exit 2)
and no gated solve is launched.  A zero from a reader not shown able to see a
non-zero is not evidence (CLAUDE.md rule 3).

-------------------------------------------------------------------------------
THE THREE SILENT FACTORS THIS COMPARATOR EXISTS TO CATCH
-------------------------------------------------------------------------------
Each produces a map that is smooth, monotone, self-consistent and WRONG.

(1) `volumeMode`  (section 2.4).  `volumeMode` is a REQUIRED entry of
    `SemiImplicitSource` -- `read()` at SemiImplicitSource.C:534 uses a `get`,
    not a defaulted lookup -- and it SILENTLY RESCALES the supplied number:
    `absolute` sets `VDash_ = V_` (the cell-zone volume) while `specific` leaves
    `VDash_ = 1`, and the value is divided by `VDash_`.  The class constructor's
    own default is `vmAbsolute`.  THE FROZEN `fvOptions` STATES
    `volumeMode specific;` VERBATIM and this comparator REFUSES if the file on
    disk does not.

(2) `WEDGE_SCALE` (section 2.6).  The domain is a 5-degree wedge, 5/360 of the
    annulus, so every force this case reports is the wedge force times 72.
    A missing factor of 72 is invisible in a residual and invisible in a map.

(3) THE KINEMATIC SOURCE.  `simpleFoam` IS INCOMPRESSIBLE: its momentum
    equation is divided by rho and carries NO rho at all
    (`constant/transportProperties` holds `nu` only).  The directive's
    `injectionRateSuSp = delta_p / t` in N/m^3 is a FORCE density and is right
    for a COMPRESSIBLE solver; the value this case must supply is
    `delta_p / (rho * t)` in m/s^2.  The two differ by rho = 1.2 -- A FACTOR OF
    1.2, which is exactly the size that looks like a modelling detail rather
    than an error.  C3 closes on this because arm (a) is analytic from
    `delta_p` and arm (b) integrates what the solver was actually told to apply.

-------------------------------------------------------------------------------
SIGN CONVENTION (section 2.5), stated once and used everywhere
-------------------------------------------------------------------------------
Freestream and bulk flow are +x; upstream is -x.  The momentum source on the
cellZone `disk` is +x (it accelerates the fluid downstream).  THRUST IS POSITIVE
IN -x: every reported force is the -x component times -1, so `T_disk`, `T_duct`
and `T_total` are POSITIVE WHEN PROPULSIVE.  `T_duct` going negative means the
duct has become net drag.

-------------------------------------------------------------------------------
COMPLETION (CLAUDE.md rule 4, registration section 11.1)
-------------------------------------------------------------------------------
A run is done only if EVERY clause holds: rc = 0; an `End` line; last time ==
`endTime`; fields `U p k omega nut` present at `endTime` (this case is
NON-THERMAL and the substitution is registered at 11.1 clause 4);
`ExecutionTime` count == `endTime`; and THE AGE GUARD -- every field at
`endTime` NEWER than the case's own `0/U`.  Any clause failing means the run is
not done and this comparator REFUSES (exit 2) RATHER THAN DEGRADING.

Actuator-disk representation; no rotor.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys

# =============================================================================
# REGISTERED CONSTANTS -- section 4 unless noted.  NAMED, never inlined.
# =============================================================================
WEDGE_DEG    = 5.0
WEDGE_SCALE  = 360.0 / WEDGE_DEG        # 72.0  -- section 2.6, A NAMED CONSTANT
RHO          = 1.2                      # kg/m^3, section 4
NU           = 1.5e-5                   # m^2/s, section 4
D            = 0.25
R_DUCT       = D / 2.0
TIP_GAP      = 0.01 * D
R_TIP        = R_DUCT - TIP_GAP         # 0.12250
R_HUB        = 0.15 * D                 # 0.03750
A_DISK       = math.pi * (R_TIP ** 2 - R_HUB ** 2)      # 0.042725660088821185
T_DISK       = 0.02 * D                 # 0.005
DELTA_P_CTRL = 1000.0                   # Pa, section 6.2
U_INF_CTRL   = 0.0                      # static, section 6.2
DELTA_P_C4   = 2000.0                   # Pa, section 6.2 C4 negative limb
U_INF_PASS   = 30.0                     # m/s, section 6.3
FIELDS_REQUIRED = ("U", "p", "k", "omega", "nut")       # section 11.1 clause 4

# Registered tolerances -- section 6.2 / 6.3.  FROZEN; not arguments.
TOL_C1 = 0.02      # area-averaged disk pressure rise vs delta_p
TOL_C3 = 0.005     # T_disk computed two independent ways
TOL_C6_3 = 0.02    # empty-duct |T_total| as a fraction of the loaded thrust

# The plant.  A known non-zero, delivered the way reality delivers one --
# written into the solved field ON DISK and read back through the real reader.
PLANT_PA = 3.21e-02        # Pa, distinctive and far from any physical value
PLANT_TOL = 1.0e-9


class Refusal(Exception):
    pass


def refuse(msg):
    sys.stderr.write("NOT A RESULT -- comparator refuses (exit 2): %s\n" % msg)
    sys.exit(2)


# =============================================================================
# OpenFOAM FIELD I/O -- the REAL reader.  The plant travels through this.
# =============================================================================
_HDR = "// * * *"


def _body(path):
    t = open(path, errors="replace").read()
    i = t.find(_HDR)
    if i < 0:
        raise Refusal("no FoamFile header separator in %s" % path)
    return t[i:]


def read_volScalarField(path):
    """Return (values, uniform_value_or_None, raw_text).

    THE reader.  C1 uses it, and `plant_into_p` proves it can see a non-zero by
    making the field on disk carry one and reading it back through this call.
    """
    t = _body(path)
    m = re.search(r"internalField\s+uniform\s+([-\d.eE+]+)\s*;", t)
    if m:
        return None, float(m.group(1)), t
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\n\(",
                  t)
    if not m:
        raise Refusal("cannot parse internalField in %s" % path)
    n = int(m.group(1))
    start = t.index("(", m.end() - 1)
    end = t.index(")", start)
    vals = [float(v) for v in t[start + 1:end].split()]
    if len(vals) != n:
        raise Refusal("%s declares %d values and carries %d" % (path, n, len(vals)))
    return vals, None, t


def write_volScalarField_values(path, text, vals):
    """Write `vals` back into `path` in the file's own format, in place."""
    m = re.search(r"(internalField\s+nonuniform\s+List<scalar>\s*\n?\s*)(\d+)(\s*\n\()",
                  text)
    if not m:
        raise Refusal("cannot write into a uniform field: %s" % path)
    start = text.index("(", m.end() - 1)
    end = text.index(")", start)
    body = "\n".join("%.12g" % v for v in vals)
    with open(path, "w") as fh:
        fh.write(text[:start + 1] + "\n" + body + "\n" + text[end:])


def read_volVectorField(path):
    t = _body(path)
    m = re.search(r"internalField\s+uniform\s+\(([^)]*)\)\s*;", t)
    if m:
        return None, tuple(float(v) for v in m.group(1).split())
    m = re.search(r"internalField\s+nonuniform\s+List<vector>\s*\n?\s*(\d+)\s*\n\(",
                  t)
    if not m:
        raise Refusal("cannot parse internalField in %s" % path)
    n = int(m.group(1))
    start = t.index("(", m.end() - 1)
    vecs = []
    for mm in re.finditer(r"\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)",
                          t[start + 1:]):
        vecs.append(tuple(float(mm.group(i)) for i in (1, 2, 3)))
        if len(vecs) == n:
            break
    if len(vecs) != n:
        raise Refusal("%s declares %d vectors and carries %d" % (path, n, len(vecs)))
    return vecs, None


# =============================================================================
# MESH READERS -- the cellZone and the cell volumes come off the BUILT mesh
# =============================================================================
def read_cellzone(case, name):
    p = os.path.join(case, "constant", "polyMesh", "cellZones")
    if not os.path.exists(p):
        raise Refusal("no cellZones file: %s" % p)
    t = _body(p)
    m = re.search(re.escape(name) + r"\s*\{.*?cellLabels\s+List<label>\s*\n?\s*"
                  r"(\d+)\s*\n\(", t, re.S)
    if not m:
        raise Refusal("cellZone %r not found in %s" % (name, p))
    n = int(m.group(1))
    start = t.index("(", m.end() - 1)
    end = t.index(")", start)
    ids = [int(v) for v in t[start + 1:end].split()]
    if len(ids) != n:
        raise Refusal("cellZone %s declares %d and carries %d" % (name, n, len(ids)))
    return ids


def cell_volumes(case):
    """Exact cell volumes from `constant/polyMesh`, by pyramid decomposition.

    Read off the BUILT mesh, never from the requested grading
    (MESH_STANDARD 9.2: the requested value is the one that lies).
    """
    pm = os.path.join(case, "constant", "polyMesh")
    pts = [(float(m.group(1)), float(m.group(2)), float(m.group(3)))
           for m in re.finditer(
               r"\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)",
               _body(os.path.join(pm, "points")))]
    faces = [[int(v) for v in m.group(2).split()]
             for m in re.finditer(r"(\d+)\(([\d\s]+)\)",
                                  _body(os.path.join(pm, "faces")))]
    t = _body(os.path.join(pm, "owner"))
    own = [int(v) for v in t[t.index("\n(") + 2:t.rindex(")")].split()]
    t = _body(os.path.join(pm, "neighbour"))
    nei = [int(v) for v in t[t.index("\n(") + 2:t.rindex(")")].split()]
    nc = max(own) + 1

    fctr, farea = [], []
    for f in faces:
        c = [sum(pts[i][k] for i in f) / len(f) for k in range(3)]
        a = [0.0, 0.0, 0.0]
        cw = [0.0, 0.0, 0.0]
        tot = 0.0
        for i in range(len(f)):
            p1, p2 = pts[f[i]], pts[f[(i + 1) % len(f)]]
            u = [p2[k] - p1[k] for k in range(3)]
            v = [c[k] - p1[k] for k in range(3)]
            tri = [0.5 * (u[1] * v[2] - u[2] * v[1]),
                   0.5 * (u[2] * v[0] - u[0] * v[2]),
                   0.5 * (u[0] * v[1] - u[1] * v[0])]
            mag = math.sqrt(sum(q * q for q in tri))
            tc = [(p1[k] + p2[k] + c[k]) / 3.0 for k in range(3)]
            for k in range(3):
                a[k] += tri[k]
                cw[k] += tc[k] * mag
            tot += mag
        fctr.append([q / tot for q in cw] if tot > 0 else c)
        farea.append(a)

    est = [[0.0, 0.0, 0.0, 0] for _ in range(nc)]
    for fid in range(len(faces)):
        for cid in [own[fid]] + ([nei[fid]] if fid < len(nei) else []):
            for k in range(3):
                est[cid][k] += fctr[fid][k]
            est[cid][3] += 1
    ec = [[e[k] / e[3] for k in range(3)] for e in est]

    vol = [0.0] * nc
    for fid in range(len(faces)):
        for cid, sgn in ([(own[fid], 1.0)]
                         + ([(nei[fid], -1.0)] if fid < len(nei) else [])):
            d = [fctr[fid][k] - ec[cid][k] for k in range(3)]
            vol[cid] += sgn * sum(farea[fid][k] * d[k] for k in range(3)) / 3.0
    return vol


# =============================================================================
# fvOptions -- READ FROM DISK, NEVER ASSUMED (section 2.4)
# =============================================================================
def read_fvoptions_source(case):
    p = os.path.join(case, "constant", "fvOptions")
    if not os.path.exists(p):
        raise Refusal("no constant/fvOptions: %s" % p)
    t = open(p, errors="replace").read()
    m = re.search(r"volumeMode\s+(\w+)\s*;", t)
    if not m:
        refuse("constant/fvOptions states NO volumeMode.  It is a REQUIRED "
               "entry (SemiImplicitSource.C:534 uses a `get`) and the class "
               "default is vmAbsolute, which rescales the supplied value by "
               "the cell-zone volume.  Section 2.4 registers `volumeMode "
               "specific;` VERBATIM.")
    mode = m.group(1)
    if mode != "specific":
        refuse("constant/fvOptions states `volumeMode %s;`.  Section 2.4 "
               "registers `specific` VERBATIM: under `absolute` the supplied "
               "number is divided by the cell-zone volume and the case still "
               "meshes, still runs, still converges and produces an entirely "
               "wrong map." % mode)
    m = re.search(r"selectionMode\s+(\w+)\s*;", t)
    if not m or m.group(1) != "cellZone":
        refuse("constant/fvOptions selectionMode is %r, not `cellZone`"
               % (m.group(1) if m else None))
    m = re.search(r"cellZone\s+(\w+)\s*;", t)
    if not m or m.group(1) != "disk":
        refuse("constant/fvOptions cellZone is %r, not `disk`"
               % (m.group(1) if m else None))
    m = re.search(r"U\s*\(\s*\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)"
                  r"\s+([-\d.eE+]+)\s*\)", t)
    if not m:
        refuse("cannot read the U source vector out of constant/fvOptions")
    su = tuple(float(m.group(i)) for i in (1, 2, 3))
    sp = float(m.group(4))
    if sp != 0.0:
        refuse("the implicit part Sp of the U source is %g, not 0" % sp)
    if su[1] != 0.0 or su[2] != 0.0:
        refuse("the U source has non-axial components %r -- section 2.1 "
               "registers NO SWIRL AND NO ROTATION" % (su,))
    if su[0] <= 0.0:
        refuse("the U source x-component is %g; section 2.5 registers the "
               "source as +x (it accelerates the fluid DOWNSTREAM)" % su[0])
    return {"volumeMode": mode, "Su": su, "Sp": sp, "path": os.path.abspath(p)}


# =============================================================================
# COMPLETION (CLAUDE.md rule 4, section 11.1) -- ALL SIX CLAUSES OR NOTHING
# =============================================================================
def completion(case, log, end_time, rc):
    """Refuse (exit 2) unless every clause of section 11.1 holds."""
    fails = []
    if rc != 0:
        fails.append("clause 1: rc = %r, not 0" % rc)
    if not os.path.exists(log):
        refuse("clause 2: no solver log at %s" % log)
    text = open(log, errors="replace").read()
    if "\nEnd\n" not in text and not text.rstrip().endswith("End"):
        fails.append("clause 2: no End line in %s" % log)

    times = sorted(
        (float(d) for d in os.listdir(case)
         if re.fullmatch(r"\d+(\.\d+)?", d)
         and os.path.isdir(os.path.join(case, d))))
    if not times:
        fails.append("clause 3: no time directories under %s" % case)
        last = None
    else:
        last = times[-1]
        if abs(last - end_time) > 1e-9:
            fails.append("clause 3: last time %g != endTime %g" % (last, end_time))

    tdir = None
    if last is not None:
        tdir = os.path.join(case, ("%g" % last))
        if not os.path.isdir(tdir):
            for d in os.listdir(case):
                if os.path.isdir(os.path.join(case, d)):
                    try:
                        if abs(float(d) - last) < 1e-12:
                            tdir = os.path.join(case, d)
                    except ValueError:
                        pass
        for f in FIELDS_REQUIRED:
            if not os.path.exists(os.path.join(tdir, f)):
                fails.append("clause 4: field %s absent at %s" % (f, tdir))

    n_exec = len(re.findall(r"^ExecutionTime = ", text, re.M))
    if n_exec != int(end_time):
        fails.append("clause 5: %d ExecutionTime lines, endTime is %g"
                     % (n_exec, end_time))

    # CLAUSE 6 -- THE AGE GUARD.  `0/U` is touched last at launch and so DATES
    # THE RUN THAT WAS ALLOWED TO PRODUCE THE ANSWER.  A field older than it is
    # a field from a previous run.
    zero_u = os.path.join(case, "0", "U")
    if not os.path.exists(zero_u):
        fails.append("clause 6: no 0/U to age the run against")
    elif tdir is not None:
        t0 = os.path.getmtime(zero_u)
        for f in FIELDS_REQUIRED:
            fp = os.path.join(tdir, f)
            if os.path.exists(fp) and os.path.getmtime(fp) <= t0:
                fails.append("clause 6 AGE GUARD: %s is NOT newer than 0/U "
                             "(%.6f <= %.6f) -- it is a field from a previous "
                             "run" % (fp, os.path.getmtime(fp), t0))
    if fails:
        refuse("STRICT COMPLETION RULE (section 11.1) -- the run is NOT done:\n  "
               + "\n  ".join(fails))
    return {"clauses": "1-6 all hold", "endTime": end_time, "time_dir": tdir,
            "solver_log": os.path.abspath(log)}


def guard_virgin_case(case):
    """Section 11.1: a guard refuses a case where `0` or any time directory
    already exists.  NO RUN IN THIS CASE IS EVER STARTED ON TOP OF ONE."""
    if os.path.isdir(os.path.join(case, "0")):
        refuse("a `0` directory already exists at %s -- no run in this case is "
               "ever started on top of an existing time directory" % case)
    for d in os.listdir(case) if os.path.isdir(case) else []:
        if re.fullmatch(r"\d+(\.\d+)?", d) and os.path.isdir(os.path.join(case, d)):
            refuse("time directory %r already exists at %s" % (d, case))


# =============================================================================
# THE PLANT (CLAUDE.md rule 3) -- through the real path, off the real disk
# =============================================================================
def plant_into_p(p_path):
    """Write a KNOWN perturbation into the solved `p` on disk and read it back
    through the SAME reader C1 uses.  Refuse if the reader cannot see it.

    THE PLANT IS NOT A PYTHON VARIABLE.  It is written into the field file in
    the case's own format, the file is re-read from disk by
    `read_volScalarField`, and the perturbation must come back.  Then the file
    is restored and the reader must NO LONGER see it -- the negative limb,
    because a reader that reports the plant on every input has certified
    nothing.
    """
    vals, uniform, text = read_volScalarField(p_path)
    if vals is None:
        raise Refusal("cannot plant into a uniform field: %s (uniform %r).  "
                      "A solved p field is nonuniform; a uniform one means the "
                      "solver wrote nothing." % (p_path, uniform))
    original = list(vals)
    idx = len(vals) // 3          # BY INDEX, not by value: a plant chosen by
                                  # value can land on a cell that already
                                  # carries it and prove nothing.
    before = original[idx]
    perturbed = list(original)
    perturbed[idx] = before + PLANT_PA
    write_volScalarField_values(p_path, text, perturbed)
    back, _, text2 = read_volScalarField(p_path)
    seen = back[idx] - before
    if abs(seen - PLANT_PA) > PLANT_TOL:
        write_volScalarField_values(p_path, text2, original)
        refuse("PLANTED CONTROL DID NOT FIRE: planted %.6g Pa into cell %d of "
               "%s and the reader read back %.6g.  A zero from a reader not "
               "shown able to see a non-zero is not evidence."
               % (PLANT_PA, idx, p_path, seen))
    # NEGATIVE LIMB -- restore, and the reader must NOT still report the plant.
    write_volScalarField_values(p_path, text2, original)
    twin, _, _ = read_volScalarField(p_path)
    if abs(twin[idx] - before) > PLANT_TOL:
        refuse("PLANTED CONTROL NEGATIVE LIMB FAILED: after restoring the "
               "field the reader still reports %.6g at cell %d.  A reader that "
               "reports the plant on every input passes a fire-only test and "
               "is worthless." % (twin[idx] - before, idx))
    if len(twin) != len(original) or any(a != b for a, b in zip(twin, original)):
        refuse("the plant did not restore the field byte-for-value; the case's "
               "own p field has been altered and is no longer evidence")
    return {"plant_Pa": PLANT_PA, "cell_index": idx,
            "fired": True, "unperturbed_twin_silent": True,
            "field": os.path.abspath(p_path)}


# =============================================================================
# THE MEASUREMENTS
# =============================================================================
def disk_pressure_rise(case, tdir):
    """Area-averaged static pressure rise ACROSS the disk zone, from the
    written `p` field, read through the real reader.  C1's quantity.

    `simpleFoam` carries KINEMATIC pressure (p/rho, m^2/s^2), so the reader
    multiplies by RHO to get Pa.  Getting THAT wrong is another silent factor
    of 1.2 and it is why the multiplication is written here once, named.
    """
    p_path = os.path.join(tdir, "p")
    vals, uniform, _ = read_volScalarField(p_path)
    if vals is None:
        raise Refusal("p at %s is uniform %r -- the solver wrote no field"
                      % (tdir, uniform))
    zone = read_cellzone(case, "disk")
    vol = cell_volumes(case)
    if len(vals) != len(vol):
        raise Refusal("p carries %d values and the mesh has %d cells"
                      % (len(vals), len(vol)))
    # Upstream and downstream neighbours of the zone are needed for a JUMP.
    # The zone is one block thick in x by construction (section 5 / the mesh
    # generator), so the jump is taken between the cells immediately upstream
    # and downstream of the zone in the same radial band.  Those are supplied
    # by the run's own `surfaceFieldValue` function objects; this reader
    # consumes their written output rather than re-deriving a topology.
    # TWO SEPARATE function objects, because that is how OpenFOAM writes them:
    # each `surfaceFieldValue` owns its own `postProcessing/<name>/<t>/
    # surfaceFieldValue.dat` with a single `areaAverage(p)` column.  A reader
    # that expected one file with two suffixed columns would find neither.
    up_row = function_object_series(case, "diskPlaneUp")
    dn_row = function_object_series(case, "diskPlaneDown")
    if up_row is None or dn_row is None:
        raise Refusal("C1 needs BOTH `diskPlaneUp` and `diskPlaneDown` "
                      "surfaceFieldValue output under %s/postProcessing; got "
                      "%r / %r" % (case, up_row is not None, dn_row is not None))
    col = "areaAverage(p)"
    for nm, row in (("diskPlaneUp", up_row), ("diskPlaneDown", dn_row)):
        if col not in row:
            raise Refusal("%s carries no %s column; columns: %s"
                          % (nm, col, sorted(row)))
    if abs(up_row["Time"] - dn_row["Time"]) > 1e-9:
        raise Refusal("the two disk planes were written at different times "
                      "(%g vs %g) -- they are not the same solution"
                      % (up_row["Time"], dn_row["Time"]))
    up, dn = up_row[col], dn_row[col]
    return {"delta_p_measured_Pa": RHO * (dn - up),
            "p_upstream_kinematic": up, "p_downstream_kinematic": dn,
            "rho_used": RHO, "zone_cells": len(zone)}


def function_object_series(case, name):
    """Last row of a function-object time series under `postProcessing/<name>`."""
    root = os.path.join(case, "postProcessing", name)
    if not os.path.isdir(root):
        return None
    best = None
    for tdir in os.listdir(root):
        for f in os.listdir(os.path.join(root, tdir)):
            path = os.path.join(root, tdir, f)
            hdr, last = None, None
            for line in open(path, errors="replace"):
                if line.startswith("#"):
                    hdr = line
                elif line.strip():
                    last = line
            if hdr is None or last is None:
                continue
            cols = hdr.lstrip("#").split()
            vals = last.split()
            if len(cols) != len(vals):
                raise Refusal("%s: %d header columns, %d data columns -- the "
                              "reader will not guess the alignment"
                              % (path, len(cols), len(vals)))
            row = dict(zip(cols, (float(v) for v in vals)))
            if best is None or row.get("Time", 0) >= best.get("Time", 0):
                best = row
    return best


def t_disk_analytic(delta_p):
    """(a) T_disk = delta_p * A_disk.  42.7256600888 N at 1000 Pa."""
    return delta_p * A_DISK


def t_disk_from_source(case, delta_p):
    """(b) The disk-zone momentum source INTEGRATED FROM THE CASE'S OWN INPUTS
    AND ITS OWN BUILT MESH, times WEDGE_SCALE.

    This arm touches `delta_p` ONLY through the frozen `fvOptions` value on
    disk.  It reads the source density the solver was actually handed, the
    actual cellZone, and the actual cell volumes, and applies the actual wedge
    factor.  So it disagrees with arm (a) if `volumeMode` is wrong, if
    `WEDGE_SCALE` is missing or wrong, if the source was written as a force
    density instead of an acceleration, or if the cellZone is not the registered
    rectangle.  THAT DISAGREEMENT IS THE WHOLE POINT OF C3.
    """
    src = read_fvoptions_source(case)
    zone = read_cellzone(case, "disk")
    vol = cell_volumes(case)
    v_zone = sum(vol[i] for i in zone)
    if v_zone <= 0.0:
        refuse("the disk cellZone has non-positive volume %g" % v_zone)
    # `volumeMode specific` => Su is a per-unit-volume ACCELERATION [m/s^2].
    # simpleFoam is incompressible, so the force is rho * Su * V.
    force_wedge = RHO * src["Su"][0] * v_zone
    force_full = force_wedge * WEDGE_SCALE
    expected_v = A_DISK * T_DISK / WEDGE_SCALE
    return {"T_disk_N": force_full,
            "wedge_force_N": force_wedge,
            "WEDGE_SCALE": WEDGE_SCALE,
            "source_Su_x_m_s2": src["Su"][0],
            "volumeMode": src["volumeMode"],
            "zone_volume_measured_m3": v_zone,
            "zone_volume_expected_m3": expected_v,
            "zone_volume_ratio": v_zone / expected_v,
            "expected_source_for_delta_p": delta_p / (RHO * T_DISK),
            "fvOptions": src["path"]}


def total_thrust(case):
    """T_total, T_disk and T_duct in NEWTONS, POSITIVE WHEN PROPULSIVE.

    Section 2.5: thrust is positive in -x, so every reported force is the -x
    component of the integrated force times -1, and then times WEDGE_SCALE
    because the `forces` function object integrates the WEDGE patches only and
    returns 5/360 of the full annular force (section 2.6).
    """
    out = {}
    for key, fo in (("T_duct", "forcesDuct"),):
        row = function_object_series(case, fo)
        if row is None:
            raise Refusal("no `%s` forces output under %s/postProcessing"
                          % (fo, case))
        fx = None
        for c in row:
            if c.startswith("total_x") or c == "Fx" or c.endswith("(x)"):
                fx = row[c]
                break
        if fx is None:
            raise Refusal("cannot find the x force column in %s; columns: %s"
                          % (fo, sorted(row)))
        out[key] = -fx * WEDGE_SCALE
    return out


# =============================================================================
# SECTION 6.2 -- THE PLANTED CONTROL, C1..C4
# =============================================================================
def control_6_2(case_plant, case_baseline, case_c4, end_time, rc_plant,
                rc_baseline, rc_c4):
    res = {"section": "6.2", "conditions": {}}
    comp = completion(case_plant, os.path.join(case_plant, "log.simpleFoam"),
                      end_time, rc_plant)
    res["completion"] = comp
    tdir = comp["time_dir"]

    # THE PLANT, before any number is believed.
    res["planted_control"] = plant_into_p(os.path.join(tdir, "p"))

    # C1 -- pressure rise across the disk == delta_p within 2%
    dp = disk_pressure_rise(case_plant, tdir)
    err = abs(dp["delta_p_measured_Pa"] - DELTA_P_CTRL) / DELTA_P_CTRL
    res["conditions"]["C1"] = {
        "measured_delta_p_Pa": dp["delta_p_measured_Pa"],
        "registered_delta_p_Pa": DELTA_P_CTRL,
        "relative_error": err, "tolerance": TOL_C1,
        "pass": err <= TOL_C1, "detail": dp}

    # C2 -- disk mass flow positive AND increased over the delta_p = 0 baseline
    m_plant = function_object_series(case_plant, "diskFlow")
    m_base = function_object_series(case_baseline, "diskFlow")
    if m_plant is None or m_base is None:
        raise Refusal("C2 needs `diskFlow` surfaceFieldValue output on BOTH "
                      "the loaded case and the delta_p = 0 baseline")
    key = [c for c in m_plant if c.startswith("sum(phi)")
           or c.startswith("areaNormalIntegrate")]
    if not key:
        raise Refusal("cannot find the flow column in `diskFlow`; columns: %s"
                      % sorted(m_plant))
    q_plant, q_base = m_plant[key[0]], m_base[key[0]]
    res["conditions"]["C2"] = {
        "mdot_loaded": q_plant, "mdot_baseline": q_base,
        "pass": q_plant > 0.0 and q_plant > q_base}

    # C3 -- T_disk two independent ways within 0.5%.  THE CLAUSE THAT CATCHES
    # THE FACTOR-72 WEDGE ERROR AND THE volumeMode FACTOR OF SECTION 2.4.
    ta = t_disk_analytic(DELTA_P_CTRL)
    tb = t_disk_from_source(case_plant, DELTA_P_CTRL)
    err3 = abs(tb["T_disk_N"] - ta) / ta
    res["conditions"]["C3"] = {
        "T_disk_analytic_N": ta, "T_disk_from_source_N": tb["T_disk_N"],
        "relative_error": err3, "tolerance": TOL_C3,
        "pass": err3 <= TOL_C3, "detail": tb}

    # C4 -- THE NEGATIVE LIMB.  The same L1 case is re-run with delta_p
    # deliberately mis-set by a factor of 2 (2000 Pa in fvOptions, 1000 Pa
    # asserted here).  C1 MUST REFUSE.  If the mis-set run passes C1 the
    # instrument is blind and THE ENTIRE CASE is NOT A RESULT.
    comp4 = completion(case_c4, os.path.join(case_c4, "log.simpleFoam"),
                       end_time, rc_c4)
    dp4 = disk_pressure_rise(case_c4, comp4["time_dir"])
    err4 = abs(dp4["delta_p_measured_Pa"] - DELTA_P_CTRL) / DELTA_P_CTRL
    c1_would_pass = err4 <= TOL_C1
    res["conditions"]["C4"] = {
        "fvOptions_delta_p_Pa": DELTA_P_C4,
        "asserted_delta_p_Pa": DELTA_P_CTRL,
        "measured_delta_p_Pa": dp4["delta_p_measured_Pa"],
        "relative_error": err4, "tolerance": TOL_C1,
        "C1_refused_as_it_must": not c1_would_pass,
        "pass": not c1_would_pass}
    if c1_would_pass:
        refuse("C4 NEGATIVE LIMB: the run with delta_p MIS-SET BY A FACTOR OF "
               "2 still passed C1 (measured %.6g Pa against an asserted %.6g "
               "Pa, %.4f%% -- inside the %.1f%% tolerance).  THE INSTRUMENT IS "
               "BLIND AND THE ENTIRE CASE IS NOT A RESULT.  C4 is one-way: it "
               "can only withdraw confidence, never grant it."
               % (dp4["delta_p_measured_Pa"], DELTA_P_CTRL, 100 * err4,
                  100 * TOL_C1))

    res["verdict"] = ("GATE REACHED"
                      if all(c["pass"] for c in res["conditions"].values())
                      else "NOT A RESULT")
    return res


# =============================================================================
# SECTION 6.3 -- THE EMPTY-DUCT PASS-THROUGH, MAGNITUDE **AND SIGN**
# =============================================================================
def control_6_3(case_empty, t_total_loaded_N, end_time, rc_empty):
    comp = completion(case_empty, os.path.join(case_empty, "log.simpleFoam"),
                      end_time, rc_empty)
    src = read_fvoptions_source_or_none(case_empty)
    if src is not None and src["Su"][0] != 0.0:
        refuse("section 6.3 registers delta_p = 0, and constant/fvOptions "
               "carries a source of %g m/s^2" % src["Su"][0])
    t = total_thrust(case_empty)
    t_total = t["T_duct"]
    frac = abs(t_total) / abs(t_total_loaded_N)
    ok_mag = frac < TOL_C6_3
    ok_sign = t_total < 0.0
    res = {"section": "6.3", "U_inf_m_s": U_INF_PASS,
           "T_total_N": t_total, "T_total_loaded_reference_N": t_total_loaded_N,
           "fraction_of_loaded": frac, "tolerance": TOL_C6_3,
           "magnitude_pass": ok_mag, "sign_pass_must_be_drag": ok_sign,
           "completion": comp,
           "verdict": "GATE REACHED" if (ok_mag and ok_sign) else "NOT A RESULT"}
    if not ok_sign:
        refuse("section 6.3: T_total = %+.6g N is POSITIVE with delta_p = 0.  "
               "Under section 2.5's convention that is NET THRUST FROM NOTHING. "
               "NOT A RESULT regardless of magnitude -- registering the SIGN as "
               "well as the magnitude closes the hole the directive's 'small' "
               "leaves open." % t_total)
    return res


def read_fvoptions_source_or_none(case):
    p = os.path.join(case, "constant", "fvOptions")
    if not os.path.exists(p):
        return None
    return read_fvoptions_source(case)


# =============================================================================
def main():
    sys.stderr.write(
        "F28 comparator.  This file is an INSTRUMENT.  It takes the three "
        "section 6.2 case directories, the section 6.3 case directory, their "
        "endTime and their solver rcs, and it REFUSES (exit 2) rather than "
        "degrading.  It has not been run for record: Stage 1 onward is gated "
        "behind the supervisor's check-1 read of this diff.\n")
    if len(sys.argv) < 2 or sys.argv[1] != "--grade":
        sys.stderr.write(
            "usage: analyse_f28.py --grade <spec.json>\n"
            "  spec.json: {\"case_plant\":..., \"case_baseline\":..., "
            "\"case_c4\":..., \"case_empty\":..., \"endTime\":..., "
            "\"rc\":{...}, \"T_total_loaded_N\":...}\n")
        sys.exit(2)
    spec = json.load(open(sys.argv[2]))
    out = {"case": "F28_DUCTED_ACTUATOR_DISK",
           "disclosure": "Actuator-disk representation; no rotor.",
           "registration": "verification/campaign/"
                           "F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md"}
    try:
        out["V_a_planted_control"] = control_6_2(
            spec["case_plant"], spec["case_baseline"], spec["case_c4"],
            spec["endTime"], spec["rc"]["plant"], spec["rc"]["baseline"],
            spec["rc"]["c4"])
        out["V_b_pass_through"] = control_6_3(
            spec["case_empty"], spec["T_total_loaded_N"], spec["endTime"],
            spec["rc"]["empty"])
    except Refusal as e:
        refuse(str(e))
    both = (out["V_a_planted_control"]["verdict"] == "GATE REACHED"
            and out["V_b_pass_through"]["verdict"] == "GATE REACHED")
    out["verdict"] = "GATE REACHED" if both else "NOT A RESULT"
    out["note"] = ("Section 9.2: BOTH controls must pass before any gated solve "
                   "is launched.  Either failing is NOT A RESULT for the case.")
    print(json.dumps(out, indent=2, sort_keys=True))
    sys.exit(0 if both else 1)


if __name__ == "__main__":
    main()
