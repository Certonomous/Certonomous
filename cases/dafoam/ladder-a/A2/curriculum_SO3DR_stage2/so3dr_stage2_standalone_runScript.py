#!/usr/bin/env python
"""SO-3D-R STAGE 2 -- the STANDALONE single-point cl04 rig.

DERIVED FROM cases/dafoam/ladder-a/A2/curriculum_D6R/d6r_opt_runScript.py
(md5 93edb4a231e13a7af065368f61a468ef, 306 lines) with the REGISTERED DELTAS of
../curriculum_SO3DR_stage2/PREREGISTRATION.md section 1 and no other. The
companion diff is so3dr_stage2_standalone_runScript_DELTAS_from_d6r.diff.

WHAT THIS RIG DOES, and why each delta exists (RULING 3 section 9.2):
  * ONE scenario only -- cl04. The cl05/cl06 scenarios, the `obj` om.ExecComp
    composite objective and its three CD connects, every geometric/CL/LE/TE
    constraint, add_design_var, add_objective, the pyOptSparseDriver, the
    findFeasibleDesign trim and run_driver are all REMOVED. There is no
    optimiser and no CL trim: the AoA is the EXACT value the multipoint
    evaluated, injected, not re-solved. This is what holds the design perfectly
    fixed so the ONLY difference from the multipoint is the assembly context.
  * INJECT one exact design vector -- shape[90] + twist[7] + patchV_cl04
    [100, AoA] -- parsed from the sha256-pinned D6R log at a registered
    `dv_block_line` (the `Driver debug print for iter coord` block). The full
    vector is taken from the log, not retyped, so it is provably the design the
    multipoint ran.
  * COLD start -- run_model() ONCE from a fresh 0/ (no warm-start / no prior
    time directory). The launcher stages a clean case copy per leg; this rig
    REFUSES if the run directory already carries a non-0 time directory.
  * BYTE-IDENTICAL numerics -- daOptions (solverName DARhoSimpleFoam,
    primalMinResTol 1e-8, primalMinResTolDiff 1e3 => accept floor 1e-5,
    primalBC, function, normalizeStates, checkMeshThreshold maxNonOrth 70,
    inputInfo), meshOptions and the np=4 / method scotch decomposition are D6R's
    bytes. The accept floor is NOT touched -- the `Primal solution failed!`
    banner / N-D42 post-End acceptance outcome is exactly what Stage-2 measures,
    so suppressing or forcing it would destroy the experiment. A guard REFUSES
    if either tolerance is not the D6R value.

NOT_FROZEN permission gate: this rig REFUSES to run unless a freeze marker
(so3dr_stage2_FREEZE.marker in the case directory, or env SO3DR_STAGE2_FROZEN=1)
is present. The freeze is the dafoam-supervisor's; while it is not taken this rig
cannot launch compute.

RULING 2's bar, preserved: the 39.7x is a DATUM, never a verdict. This rig
computes no ratio and grades nothing; it runs one primal and records what it
injected. SUBMISSIONS PARKED.

No `assert` statement carries anything here (family convention); every guard is
an explicit if/raise.
"""
import os
import re
import sys
import json
import hashlib
import argparse
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder, OptFuncs
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP
from pygeo import geo_utils

# --------------------------------------------------------------------------
# STAGE-2 REGISTERED CONSTANTS (frozen in PREREGISTRATION.md; do not edit here)
# --------------------------------------------------------------------------
D6R_LOG = "/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/O_mp_20260828T162849Z_1898072.log"
D6R_LOG_SHA256 = "394d9f5d8c59ea79602e678cec7a75915bef53a048b61e153d835fce57fc675d"
ACCEPT_FLOOR_TOL = 1.0e-8      # primalMinResTol  -- D6R value, must not move
ACCEPT_FLOOR_DIFF = 1.0e3      # primalMinResTolDiff -- D6R value, must not move
EXPECT_N_SHAPE = 96      # measured from the D6R log blocks (5x17 + 11); NOT 90
EXPECT_N_TWIST = 7


def _refuse(msg):
    sys.stderr.write("STAGE2 RIG REFUSE: %s\n" % msg)
    sys.exit(7)


def check_not_frozen_gate(case_dir):
    """NOT_FROZEN permission gate. The freeze is the supervisor's."""
    marker = os.path.join(case_dir, "so3dr_stage2_FREEZE.marker")
    if os.environ.get("SO3DR_STAGE2_FROZEN") == "1" or os.path.isfile(marker):
        return
    _refuse(
        "NOT FROZEN. This rig will not launch compute until the dafoam-supervisor's "
        "freeze places %s (or sets SO3DR_STAGE2_FROZEN=1). No gate has been "
        "committed-before-compute for this leg." % marker
    )


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _floats_between(text, start_key):
    """Parse a numpy-repr array `start_key array([ ... ])` that may span lines."""
    i = text.find(start_key)
    if i < 0:
        return None
    j = text.find("array([", i)
    if j < 0:
        return None
    k = text.find("])", j)
    if k < 0:
        return None
    body = text[j + len("array(["):k]
    toks = re.findall(r"[-+]?\d+\.?\d*(?:[eE][-+]?\d+)?", body)
    return [float(t) for t in toks]


def read_design_vector(log_path, dv_block_line):
    """Read shape[90], twist[7], patchV_cl04 [U, AoA] from the D6R log block that
    begins at 1-based line `dv_block_line`. Refuses on any shape/count anomaly."""
    if sha256_of(log_path) != D6R_LOG_SHA256:
        _refuse("D6R log sha256 mismatch -- the registered source has changed. UNMEASURED, not assumed.")
    with open(log_path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    if dv_block_line < 1 or dv_block_line > len(lines):
        _refuse("dv_block_line %d out of range 1..%d" % (dv_block_line, len(lines)))
    if not lines[dv_block_line - 1].startswith("Driver debug print for iter coord:"):
        _refuse("line %d is not a `Driver debug print for iter coord:` block header" % dv_block_line)
    # the Design Vars dict is printed within a bounded window after the header
    window = "\n".join(lines[dv_block_line - 1: dv_block_line - 1 + 120])
    patchv = _floats_between(window, "'dvs.patchV_cl04':")
    shape = _floats_between(window, "'dvs.shape':")
    twist = _floats_between(window, "'dvs.twist':")
    if patchv is None or shape is None or twist is None:
        _refuse("could not parse patchV_cl04 / shape / twist from block at line %d" % dv_block_line)
    if len(patchv) != 2:
        _refuse("patchV_cl04 has %d elements, expected 2 [U, AoA]" % len(patchv))
    if len(shape) != EXPECT_N_SHAPE:
        _refuse("shape has %d elements, expected %d" % (len(shape), EXPECT_N_SHAPE))
    if len(twist) != EXPECT_N_TWIST:
        _refuse("twist has %d elements, expected %d" % (len(twist), EXPECT_N_TWIST))
    return np.array(patchv), np.array(shape), np.array(twist)


def check_cold_start(run_dir):
    """Cold-start guard: the run directory must carry ONLY time dir 0 (fresh)."""
    if not os.path.isdir(run_dir):
        _refuse("run directory %s does not exist -- the launcher stages a fresh case copy per leg" % run_dir)
    times = []
    for name in os.listdir(run_dir):
        if re.fullmatch(r"\d+(\.\d+)?", name) and os.path.isdir(os.path.join(run_dir, name)):
            times.append(name)
    others = [t for t in times if float(t) != 0.0]
    if others:
        _refuse("run directory %s already carries non-0 time dirs %r -- not a cold start" % (run_dir, sorted(others)))
    if "0" not in times:
        _refuse("run directory %s has no 0/ time dir -- cannot cold start" % run_dir)


# --------------------------------------------------------------------------
# daOptions -- D6R's bytes, single-point (accept floor NOT touched)
# --------------------------------------------------------------------------
U0 = 100.0
p0 = 101325.0
nuTilda0 = 4.5e-5
T0 = 300.0
aoa0 = 4.0
rho0 = p0 / T0 / 287.0
A0 = 45.5

POINT = "cl04"
RUN_DIR = "mp04"

daOptions = {
    "designSurfaces": ["wing"],
    "solverName": "DARhoSimpleFoam",
    "primalMinResTol": ACCEPT_FLOOR_TOL,
    "primalMinResTolDiff": ACCEPT_FLOOR_DIFF,
    "primalBC": {
        "U0": {"variable": "U", "patches": ["inout"], "value": [U0, 0.0, 0.0]},
        "p0": {"variable": "p", "patches": ["inout"], "value": [p0]},
        "T0": {"variable": "T", "patches": ["inout"], "value": [T0]},
        "nuTilda0": {"variable": "nuTilda", "patches": ["inout"], "value": [nuTilda0]},
        "useWallFunction": True,
    },
    "function": {
        "CD": {
            "type": "force",
            "source": "patchToFace",
            "patches": ["wing"],
            "directionMode": "parallelToFlow",
            "patchVelocityInputName": "patchV",
            "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0),
        },
        "CL": {
            "type": "force",
            "source": "patchToFace",
            "patches": ["wing"],
            "directionMode": "normalToFlow",
            "patchVelocityInputName": "patchV",
            "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0),
        },
    },
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 1, "jacMatReOrdering": "rcm"},
    "normalizeStates": {
        "U": U0,
        "p": U0 * U0 / 2.0,
        "T": T0,
        "nuTilda": 1e-3,
        "phi": 1.0,
    },
    "checkMeshThreshold": {
        "maxAspectRatio": 1000.0,
        "maxNonOrth": 70.0,
        "maxSkewness": 5.0,
    },
    "inputInfo": {
        "aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]},
        "patchV": {
            "type": "patchVelocity",
            "patches": ["inout"],
            "flowAxis": "x",
            "normalAxis": "y",
            "components": ["solver", "function"],
        },
    },
}


def mesh_options():
    return {
        "gridFile": os.path.join(os.getcwd(), RUN_DIR),
        "fileType": "OpenFOAM",
        "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]]],
    }


class Top(Multipoint):
    """Single-point cl04 standalone -- NO composite objective, NO constraints,
    NO optimiser. The design vector is injected before run_model."""

    def __init__(self, patchv, shape, twist, **kwargs):
        super().__init__(**kwargs)
        self._inj_patchv = patchv
        self._inj_shape = shape
        self._inj_twist = twist

    def setup(self):
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])
        b = DAFoamBuilder(daOptions, mesh_options(), scenario="aerodynamic",
                          run_directory=RUN_DIR)
        b.initialize(self.comm)
        self.builder = b
        self.add_subsystem("mesh_" + POINT, b.get_mesh_coordinate_subsystem())
        self.add_subsystem("geometry_" + POINT, OM_DVGEOCOMP(file="FFD/wingFFD.xyz", type="ffd"))
        self.mphys_add_scenario(POINT, ScenarioAerodynamic(aero_builder=b))
        self.connect("mesh_%s.x_aero0" % POINT, "geometry_%s.x_aero_in" % POINT)
        self.connect("geometry_%s.x_aero0" % POINT, "%s.x_aero" % POINT)
        # NO `obj` ExecComp, NO cl05/cl06, NO cross-scenario connects.

    def configure(self):
        geometry = getattr(self, "geometry_" + POINT)
        mesh = getattr(self, "mesh_" + POINT)
        points = mesh.mphys_get_surface_mesh()
        geometry.nom_add_discipline_coords("aero", points)
        tri_points = mesh.mphys_get_triangulated_surface()
        geometry.nom_setConstraintSurface(tri_points)
        nRefAxPts = geometry.nom_addRefAxis(name="wingAxis", xFraction=0.25, alignIndex="k")

        def twist(val, geo, _n=nRefAxPts):
            for i in range(1, _n):
                geo.rot_z["wingAxis"].coef[i] = -val[i - 1]

        geometry.nom_addGlobalDV(dvName="twist", value=np.array([0] * (nRefAxPts - 1)), func=twist)
        pts = geometry.DVGeo.getLocalIndex(0)
        indexList = pts[:, :, :].flatten()
        PS = geo_utils.PointSelect("list", indexList)
        nShapes = geometry.nom_addLocalDV(dvName="shape", pointSelect=PS)

        # guards: the injected vector must fit this geometry EXACTLY
        if nShapes != len(self._inj_shape):
            _refuse("geometry has %d shape DVs but the injected vector has %d" % (nShapes, len(self._inj_shape)))
        if (nRefAxPts - 1) != len(self._inj_twist):
            _refuse("geometry has %d twist DVs but the injected vector has %d" % (nRefAxPts - 1, len(self._inj_twist)))

        # INJECT the exact design vector (no optimiser will move it)
        self.dvs.add_output("twist", val=self._inj_twist)
        self.dvs.add_output("shape", val=self._inj_shape)
        self.dvs.add_output("patchV_" + POINT, val=self._inj_patchv)
        self.connect("twist", "geometry_%s.twist" % POINT)
        self.connect("shape", "geometry_%s.shape" % POINT)
        self.connect("patchV_" + POINT, "%s.patchV" % POINT)
        # NO add_design_var, NO add_objective, NO add_constraint -- there is no driver.


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-dv_block_line", type=int, required=True,
                        help="1-based line of the registered `Driver debug print` block in the D6R log")
    parser.add_argument("-case_dir", type=str, default=os.path.dirname(os.path.abspath(__file__)),
                        help="the SO3DR stage-2 case dir that carries the freeze marker")
    args = parser.parse_args()

    # accept-floor guard -- the two values must be the D6R values, unmoved
    if daOptions["primalMinResTol"] != ACCEPT_FLOOR_TOL or daOptions["primalMinResTolDiff"] != ACCEPT_FLOOR_DIFF:
        _refuse("accept floor moved from the D6R value -- the banner outcome may not be suppressed or forced")

    check_not_frozen_gate(args.case_dir)
    patchv, shape, twist = read_design_vector(D6R_LOG, args.dv_block_line)
    run_dir_abs = os.path.join(os.getcwd(), RUN_DIR)
    check_cold_start(run_dir_abs)

    prob = om.Problem()
    prob.model = Top(patchv, shape, twist)
    prob.setup(mode="rev")
    # run the primal ONCE, cold. No findFeasibleDesign, no run_driver, no adjoint.
    prob.run_model()

    if MPI.COMM_WORLD.rank == 0:
        sidecar = {
            "dv_block_line": args.dv_block_line,
            "d6r_log_sha256": D6R_LOG_SHA256,
            "patchV_cl04": patchv.tolist(),
            "aoa_injected": float(patchv[1]),
            "shape_md5": hashlib.md5(np.ascontiguousarray(shape).tobytes()).hexdigest(),
            "twist_md5": hashlib.md5(np.ascontiguousarray(twist).tobytes()).hexdigest(),
            "shape_n": int(len(shape)),
            "twist_n": int(len(twist)),
            "primalMinResTol": daOptions["primalMinResTol"],
            "primalMinResTolDiff": daOptions["primalMinResTolDiff"],
            "cold_start": True,
        }
        with open(os.path.join(run_dir_abs, "injected_dv.json"), "w") as fh:
            json.dump(sidecar, fh, indent=1)


if __name__ == "__main__":
    main()
