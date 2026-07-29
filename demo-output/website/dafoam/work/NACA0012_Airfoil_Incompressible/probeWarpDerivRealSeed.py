#!/usr/bin/env python
"""
Decisive follow-up to PROOF.md sections 15-16 / UPSTREAM_BUG_REPORT_mesh_warpDeriv.md.

Section 16.2 found that A1's idx6 (LE combo mode) AND idx7 (TE combo mode) both
fail the generic warpDeriv dot-product self-consistency test just as badly
(108-149%, sign-flipped), yet only idx6's REAL dCD/dShape is wrong -- idx7's is
clean to 1.5-1.8% in the actual CFD+adjoint check. The best-supported,
not-yet-confirmed explanation: the generic test used an ARBITRARY random seed w
on the volume-mesh output space. The real adjoint never uses an arbitrary seed --
it uses w = dCD/dXv, the CD objective's own reverse-mode sensitivity to the
volume mesh, which for a force objective on an airfoil is concentrated near the
leading edge and small at the trailing edge. If that is right, an idx6-located
warpDeriv error overlaps dCD/dXv and corrupts the real gradient; an idx7-located
one does not.

THIS script gets the REAL dCD/dXv, not a reconstruction of it: it builds the
exact, unmodified Top model from runScript.py (mesh + geometry + scenario1,
same daOptions, same 8-component "shape" DV), runs the real primal + a real
CD adjoint solve via prob.compute_totals(of=["scenario1.aero_post.CD"],
wrt=["shape"]), and installs a capture hook on DAFoamWarper.compute_jacvec_product
(dafoam/mphys/mphys_dafoam.py) -- the exact component whose reverse-mode
d_outputs["aero_vol_coords"] argument becomes the "dxV" that gets passed
verbatim to mesh.warpDeriv(dxV) in the real adjoint chain. That captured vector,
not a random one, is the seed used below.

After capture, it reuses the SAME DASolver/mesh/DVGeo objects (no re-init, no
possible partition mismatch) to repeat exactly the section 15/16 dot-product
identity,

    <w, dXv/dShape_idx>_FD   ==   <warpDeriv(w), dXs/dShape_idx>_analytic

for idx=4 (control), idx=6 (suspect, real gradient WRONG) and idx=7 (suspect
construction, real gradient CLEAN), with w = the captured real dCD/dXv instead
of np.random. The prediction under test: idx6 should still disagree badly,
idx7 should now agree (unlike the random-seed test, where both failed alike).

No number here is adjusted, no seed is picked to fit -- w is whatever the real
adjoint chain actually produced this run, taken verbatim.
"""
import os
import sys
import time
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP
import dafoam.mphys.mphys_dafoam as mphys_dafoam

comm = MPI.COMM_WORLD
rank = comm.rank
nRanks = comm.size

U0 = 10.0
p0 = 0.0
nuTilda0 = 4.5e-5
CL_target = 0.5
aoa0 = 5.13918623195176
A0 = 0.1
rho0 = 1.0

daOptions = {
    "designSurfaces": ["wing"],
    "solverName": "DASimpleFoam",
    "primalMinResTol": 1.0e-8,
    "primalBC": {
        "U0": {"variable": "U", "patches": ["inout"], "value": [U0, 0.0, 0.0]},
        "p0": {"variable": "p", "patches": ["inout"], "value": [p0]},
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
        "nuTilda": nuTilda0 * 10.0,
        "phi": 1.0,
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

meshOptions = {
    "gridFile": os.getcwd(),
    "fileType": "OpenFOAM",
    "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]], [[0.0, 0.0, 0.1], [0.0, 0.0, 1.0]]],
}

# ---------------------------------------------------------------------------
# capture hook: record every d_outputs["aero_vol_coords"] seen by
# DAFoamWarper.compute_jacvec_product in reverse mode. In this model's linear
# chain (LinearRunOnce over an explicit component sequence) this is called
# exactly once per compute_totals(of=CD) call, with the FULL accumulated
# dCD/dXv already summed in from both the direct DAFoamFunctions term and the
# state-adjoint (psi) term inside DAFoamSolver -- i.e. exactly the "dxV" the
# real adjoint hands to mesh.warpDeriv(dxV). We keep every call, not just the
# first, and report the count honestly.
# ---------------------------------------------------------------------------
_captures = []
_orig_cjp = mphys_dafoam.DAFoamWarper.compute_jacvec_product


def _capturing_cjp(self, inputs, d_inputs, d_outputs, mode):
    if mode == "rev":
        key = "%s_vol_coords" % self.discipline
        if key in d_outputs:
            _captures.append(np.array(d_outputs[key], copy=True))
    return _orig_cjp(self, inputs, d_inputs, d_outputs, mode)


mphys_dafoam.DAFoamWarper.compute_jacvec_product = _capturing_cjp


class Top(Multipoint):
    def setup(self):
        dafoam_builder = DAFoamBuilder(daOptions, meshOptions, scenario="aerodynamic")
        dafoam_builder.initialize(self.comm)
        # stash for retrieval after prob.setup()
        self.dafoam_builder = dafoam_builder

        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])
        self.add_subsystem("mesh", dafoam_builder.get_mesh_coordinate_subsystem())
        self.add_subsystem("geometry", OM_DVGEOCOMP(file="FFD/wingFFD.xyz", type="ffd"))
        self.mphys_add_scenario("scenario1", ScenarioAerodynamic(aero_builder=dafoam_builder))
        self.connect("mesh.x_aero0", "geometry.x_aero_in")
        self.connect("geometry.x_aero0", "scenario1.x_aero")

    def configure(self):
        points = self.mesh.mphys_get_surface_mesh()
        self.geometry.nom_add_discipline_coords("aero", points)
        tri_points = self.mesh.mphys_get_triangulated_surface()
        self.geometry.nom_setConstraintSurface(tri_points)

        pts = self.geometry.DVGeo.getLocalIndex(0)
        dir_y = np.array([0.0, 1.0, 0.0])
        shapes = []
        for i in range(1, pts.shape[0] - 1):
            for j in range(pts.shape[1]):
                shapes.append({pts[i, j, 0]: dir_y, pts[i, j, 1]: dir_y})
        for i in [0, pts.shape[0] - 1]:
            shapes.append({pts[i, 0, 0]: dir_y, pts[i, 0, 1]: dir_y, pts[i, 1, 0]: -dir_y, pts[i, 1, 1]: -dir_y})
        self.geometry.nom_addShapeFunctionDV(dvName="shape", shapes=shapes)
        self.nShape = len(shapes)

        leList = [[1e-4, 0.0, 1e-4], [1e-4, 0.0, 0.1 - 1e-4]]
        teList = [[0.998 - 1e-4, 0.0, 1e-4], [0.998 - 1e-4, 0.0, 0.1 - 1e-4]]
        self.geometry.nom_addThicknessConstraints2D("thickcon", leList, teList, nSpan=2, nChord=10)
        self.geometry.nom_addVolumeConstraint("volcon", leList, teList, nSpan=2, nChord=10)
        self.geometry.nom_addLERadiusConstraints("rcon", leList, 2, [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0])

        self.dvs.add_output("shape", val=np.array([0.0] * len(shapes)))
        self.dvs.add_output("patchV", val=np.array([U0, aoa0]))
        self.connect("patchV", "scenario1.patchV")
        self.connect("shape", "geometry.shape")

        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)
        self.add_design_var("patchV", lower=[U0, 0.0], upper=[U0, 10.0], scaler=0.1)
        self.add_objective("scenario1.aero_post.CD", scaler=1.0)
        self.add_constraint("scenario1.aero_post.CL", equals=CL_target, scaler=1.0)
        self.add_constraint("geometry.thickcon", lower=0.5, upper=3.0, scaler=1.0)
        self.add_constraint("geometry.volcon", lower=1.0, scaler=1.0)
        self.add_constraint("geometry.rcon", lower=0.8, scaler=1.0)


t0 = time.time()
prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")

if rank == 0:
    print("REALSEED === running primal (run_model) ===", flush=True)
prob.run_model()
if rank == 0:
    print("REALSEED === primal done, t=%.1fs, running real CD adjoint (compute_totals) ===" % (time.time() - t0), flush=True)

# ONE real reverse-mode CD adjoint solve -- of=CD only, so no CL/geometry
# constraint adjoint is mixed in. This is what produces the real dCD/dXv seed.
totals = prob.compute_totals(of=["scenario1.aero_post.CD"], wrt=["shape"])

if rank == 0:
    print(
        "REALSEED === adjoint done, t=%.1fs, warper compute_jacvec_product captured %d rev-mode call(s) ==="
        % (time.time() - t0, len(_captures)),
        flush=True,
    )

if len(_captures) == 0:
    raise RuntimeError("REALSEED FAIL: DAFoamWarper.compute_jacvec_product was never called in rev mode -- "
                        "capture hook did not fire, cannot get the real dCD/dXv seed.")

# use the LAST captured vector -- the fully-accumulated seed at the point the
# framework actually invoked mesh.warpDeriv with it in the real chain
w_real_local = _captures[-1]
nXvLocal = w_real_local.size
nXvGlobal = comm.allreduce(nXvLocal, op=MPI.SUM)
wnorm_local = float(np.dot(w_real_local, w_real_local))
wnorm_global = comm.allreduce(wnorm_local, op=MPI.SUM) ** 0.5

# sanity: also report dCD/dshape from this same real adjoint solve, so the
# printed idx6/idx7 numbers below can be cross-checked against the
# already-established real check_totals record in PROOF.md/DAFOAM_CASE_STATUS.md
dCDdshape = np.array(totals[("scenario1.aero_post.CD", "shape")]).flatten()
if rank == 0:
    print("REALSEED dCD/dshape (this run, real adjoint) = %s" % np.array2string(dCDdshape, precision=6), flush=True)
    print("REALSEED ||w_real||_2 (global) = %.6e, nXvGlobal=%d" % (wnorm_global, nXvGlobal), flush=True)

# ---------------------------------------------------------------------------
# Reuse the SAME DASolver / mesh / DVGeo objects (no reinitialization, no
# partition mismatch possible) to repeat the section 15/16 dot-product
# identity, now seeded with w_real instead of a random vector.
# ---------------------------------------------------------------------------
DASolver = prob.model.dafoam_builder.DASolver
mesh = DASolver.mesh
DVGeo = prob.model.geometry.DVGeo
ptSetName = "x_aero0"
nShape = prob.model.nShape

xs0 = DASolver.getSurfaceCoordinates(DASolver.designSurfacesGroup)


def set_shape(vec):
    DVGeo.setDesignVars({"shape": np.array(vec)})


def get_warped_Xv(shapeVec):
    set_shape(shapeVec)
    xs = DVGeo.update(ptSetName)
    DASolver.setSurfaceCoordinates(xs, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    return mesh.getSolverGrid().copy()


# baseline re-warp -- confirms partitioning still matches w_real_local exactly
Xv0_check = get_warped_Xv(np.zeros(nShape))
if Xv0_check.size != nXvLocal:
    raise RuntimeError(
        "REALSEED FAIL: local partition size changed between the real adjoint solve (%d) "
        "and this post-hoc re-warp (%d) -- cannot reuse w_real as a seed." % (nXvLocal, Xv0_check.size)
    )

results = []
for idx in [4, 6, 7]:
    for h in [1e-4, 1e-5]:
        ePlus = np.zeros(nShape)
        ePlus[idx] = h
        eMinus = np.zeros(nShape)
        eMinus[idx] = -h

        Xv_p = get_warped_Xv(ePlus)
        Xv_m = get_warped_Xv(eMinus)
        FD_dXv_idx_local = (Xv_p - Xv_m) / (2.0 * h)
        FD_scalar_local = float(np.dot(w_real_local, FD_dXv_idx_local))
        FD_scalar_global = comm.allreduce(FD_scalar_local, op=MPI.SUM)

        set_shape(np.zeros(nShape))
        DVGeo.update(ptSetName)
        seedDV = {"shape": np.zeros(nShape)}
        seedDV["shape"][idx] = 1.0
        AN_dXs_idx = DVGeo.totalSensitivityProd(seedDV, ptSetName).reshape(xs0.shape)

        # THE function under test: mesh.warpDeriv, seeded with the REAL dCD/dXv
        set_shape(np.zeros(nShape))
        xs_base = DVGeo.update(ptSetName)
        DASolver.setSurfaceCoordinates(xs_base, DASolver.designSurfacesGroup)
        mesh.warpMesh()
        mesh.warpDeriv(w_real_local)
        dXs_seed = mesh.getdXs()
        dXs_seed = DASolver.mapVector(dXs_seed, DASolver.allWallsGroup, DASolver.designSurfacesGroup)

        AN_scalar_local = float(np.dot(dXs_seed.flatten(), AN_dXs_idx.flatten()))
        AN_scalar_global = comm.allreduce(AN_scalar_local, op=MPI.SUM)

        absdiff = FD_scalar_global - AN_scalar_global
        relerr = abs(absdiff) / (abs(FD_scalar_global) + 1e-300)
        sign = "agree" if (FD_scalar_global * AN_scalar_global) > 0 else "FLIPPED"

        if rank == 0:
            print(
                "REALSEED_RESULT idx=%d h=%.3e nRanks=%d nXvGlobal=%d "
                "FD_scalar=%.12e AN_scalar=%.12e abs_diff=%.6e rel_err=%.6e sign=%s"
                % (idx, h, nRanks, nXvGlobal, FD_scalar_global, AN_scalar_global, absdiff, relerr, sign),
                flush=True,
            )
        results.append((idx, h, FD_scalar_global, AN_scalar_global, relerr, sign))

if rank == 0:
    print("REALSEED_DONE nRanks=%d t=%.1fs" % (nRanks, time.time() - t0), flush=True)
