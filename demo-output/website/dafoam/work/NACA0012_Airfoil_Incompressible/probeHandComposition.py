#!/usr/bin/env python
"""
r6-airfoil-second-gradient-mechanism: the decisive test the coordinator asked
for -- compose the three independently-verified links BY HAND and compare
against the framework, the finite difference, and the individual links.

The three links and how each was independently verified before this script:
  dXs/dShape  (FFD/DVGeo Jacobian)     -- machine precision, 1e-10 to 1e-13,
                                           against geometric constraint FDs
                                           (PROOF.md 11.1)
  dXv/dXs     (mesh.warpDeriv)          -- tested only IN COMBINATION with
                                           dXs/dShape (never alone) via a
                                           dot-product identity against a
                                           real nonlinear re-warp FD (15, 18)
  dCD/dXv     (captured adjoint seed)   -- true re-solve at a directly-set
                                           Xv, bypassing DVGeo/warp entirely,
                                           0.4-1.4% agreement (PROOF.md 20)

STAGE 1 (no new solve -- this is just re-stating existing numbers correctly,
per the coordinator's own note that this needs none): hand-compose the three
links exactly as section 18 already did --

    hand_composed = <warpDeriv(w_real), dXs/dShape_idx>

-- and compare against (a) the framework's own prob.compute_totals() answer,
(b) the established real check_totals finite difference, (c) this session's
own direct-Xv-resolve finite difference (section 20). Already known from
existing logs: hand_composed == framework's answer EXACTLY (both idx0 and
idx1), while both disagree with every flavor of finite difference by
11.6-11.9%. This is the coordinator's outcome #2: the hand composition
matches the framework, not the FD -- so one of the three links is not as
clean as it tests in isolation.

STAGE 2 (new this script, still no CFD solve needed beyond the one already-
required adjoint capture -- pure geometry, seconds not minutes): since
dXs/dShape and dCD/dXv are independently verified WITHOUT ever combining them
with warpDeriv, and warpDeriv has ONLY ever been tested IN COMBINATION with
dXs/dShape (never alone), this decomposes that combination to find out which
piece is responsible. Perturbs the SURFACE coordinates (Xs) DIRECTLY, along
the exact direction eta = dXs/dShape_idx (DVGeo's own analytic Jacobian
column, already trusted), bypassing DVGeo.update() entirely on the FD side.
This tests whether warpDeriv is linear along that direction independent of
any nonlinearity in DVGeo's OWN shape-to-surface parameterization (which the
original section 15/18 test could not separate out, since it perturbed SHAPE
by h and let DVGeo.update() compute the resulting xs -- a real, possibly
nonlinear, re-evaluation of the FFD, not just its own linearization):

    FD_scalar_xs_direct = <w_real, (Xv(xs0+h*eta) - Xv(xs0-h*eta))/2h>
                           where Xv(xs) = mesh.warpMesh() at that xs, DVGeo
                           never touched
    AN_scalar (unchanged) = <warpDeriv(w_real), eta>

If FD_scalar_xs_direct still disagrees with AN_scalar by ~12%: warpDeriv
itself is not linear along this direction (a real defect in warpDeriv,
independent of DVGeo). If FD_scalar_xs_direct suddenly agrees (unlike
section 18's shape-perturbation-based FD): the 12% gap was DVGeo's own
nonlinearity (real FFD response vs its own linear Jacobian), not warpDeriv.
"""
import os
import time
import argparse
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP
import dafoam.mphys.mphys_dafoam as mphys_dafoam

parser = argparse.ArgumentParser()
parser.add_argument("--idx", type=int, required=True)
parser.add_argument("--h", type=float, default=1e-4)
args = parser.parse_args()

comm = MPI.COMM_WORLD
if comm.size != 1:
    raise RuntimeError("serial only")

U0, p0, nuTilda0, aoa0, A0, rho0 = 10.0, 0.0, 4.5e-5, 5.13918623195176, 0.1, 1.0
daOptions = {
    "designSurfaces": ["wing"], "solverName": "DASimpleFoam", "primalMinResTol": 1.0e-8,
    "primalBC": {"U0": {"variable": "U", "patches": ["inout"], "value": [U0, 0.0, 0.0]},
                 "p0": {"variable": "p", "patches": ["inout"], "value": [p0]},
                 "nuTilda0": {"variable": "nuTilda", "patches": ["inout"], "value": [nuTilda0]},
                 "useWallFunction": True},
    "function": {"CD": {"type": "force", "source": "patchToFace", "patches": ["wing"],
                         "directionMode": "parallelToFlow", "patchVelocityInputName": "patchV",
                         "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0)},
                 "CL": {"type": "force", "source": "patchToFace", "patches": ["wing"],
                        "directionMode": "normalToFlow", "patchVelocityInputName": "patchV",
                        "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0)}},
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 1, "jacMatReOrdering": "rcm"},
    "normalizeStates": {"U": U0, "p": U0 * U0 / 2.0, "nuTilda": nuTilda0 * 10.0, "phi": 1.0},
    "inputInfo": {"aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]},
                  "patchV": {"type": "patchVelocity", "patches": ["inout"], "flowAxis": "x",
                             "normalAxis": "y", "components": ["solver", "function"]}},
}
meshOptions = {"gridFile": os.getcwd(), "fileType": "OpenFOAM",
               "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]], [[0.0, 0.0, 0.1], [0.0, 0.0, 1.0]]]}

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
        b = DAFoamBuilder(daOptions, meshOptions, scenario="aerodynamic")
        b.initialize(self.comm)
        self.dafoam_builder = b
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])
        self.add_subsystem("mesh", b.get_mesh_coordinate_subsystem())
        self.add_subsystem("geometry", OM_DVGEOCOMP(file="FFD/wingFFD.xyz", type="ffd"))
        self.mphys_add_scenario("scenario1", ScenarioAerodynamic(aero_builder=b))
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
        self.add_constraint("scenario1.aero_post.CL", equals=0.5, scaler=1.0)
        self.add_constraint("geometry.thickcon", lower=0.5, upper=3.0, scaler=1.0)
        self.add_constraint("geometry.volcon", lower=1.0, scaler=1.0)
        self.add_constraint("geometry.rcon", lower=0.8, scaler=1.0)


t0 = time.time()
prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")
prob.run_model()
cd_baseline = float(prob.get_val("scenario1.aero_post.CD")[0])
print("HANDCOMP === primal done t=%.1fs CD_baseline=%.15e ===" % (time.time() - t0, cd_baseline), flush=True)

totals = prob.compute_totals(of=["scenario1.aero_post.CD"], wrt=["shape"])
dCDdshape = np.array(totals[("scenario1.aero_post.CD", "shape")]).flatten()
print("HANDCOMP dCD/dshape (framework) = %s" % np.array2string(dCDdshape, precision=8), flush=True)
if len(_captures) == 0:
    raise RuntimeError("no capture")
w_real = _captures[-1]

DASolver = prob.model.dafoam_builder.DASolver
mesh = DASolver.mesh
DVGeo = prob.model.geometry.DVGeo
ptSetName = "x_aero0"
nShape = prob.model.nShape
xs0 = DASolver.getSurfaceCoordinates(DASolver.designSurfacesGroup).copy()


def set_shape(vec):
    DVGeo.setDesignVars({"shape": np.array(vec)})


idx = args.idx
h = args.h

# --- eta = dXs/dShape_idx, DVGeo's own analytic forward Jacobian column ---
set_shape(np.zeros(nShape))
DVGeo.update(ptSetName)
seedDV = {"shape": np.zeros(nShape)}
seedDV["shape"][idx] = 1.0
eta = DVGeo.totalSensitivityProd(seedDV, ptSetName).reshape(xs0.shape)
print("HANDCOMP idx=%d ||eta||_2 (dXs/dShape_idx) = %.6e" % (idx, float(np.linalg.norm(eta))), flush=True)

# --- warpDeriv(w_real): dCD/dXs via the reverse-mode warp derivative ---
set_shape(np.zeros(nShape))
DVGeo.update(ptSetName)
DASolver.setSurfaceCoordinates(xs0, DASolver.designSurfacesGroup)
mesh.warpMesh()
mesh.warpDeriv(w_real)
dXs_seed = mesh.getdXs()
dXs_seed = DASolver.mapVector(dXs_seed, DASolver.allWallsGroup, DASolver.designSurfacesGroup)

AN_scalar = float(np.dot(dXs_seed.flatten(), eta.flatten()))
print("HANDCOMP_STAGE1 idx=%d AN_scalar(hand-composed: warpDeriv x DVGeo-Jacobian) = %.12e" % (idx, AN_scalar), flush=True)
print(
    "HANDCOMP_STAGE1 idx=%d matches framework dCD/dshape[idx]=%.12e ? diff=%.3e"
    % (idx, dCDdshape[idx], AN_scalar - dCDdshape[idx]),
    flush=True,
)

# --- STAGE 2: perturb Xs DIRECTLY along eta, bypassing DVGeo.update() ---
def warp_at_direct_xs(xs):
    DASolver.setSurfaceCoordinates(xs, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    return mesh.getSolverGrid().copy()


xs_plus = xs0 + h * eta
xs_minus = xs0 - h * eta
Xv_plus = warp_at_direct_xs(xs_plus)
Xv_minus = warp_at_direct_xs(xs_minus)
# restore baseline surface state
DASolver.setSurfaceCoordinates(xs0, DASolver.designSurfacesGroup)
mesh.warpMesh()

FD_dXv_xs_direct = (Xv_plus - Xv_minus) / (2.0 * h)
FD_scalar_xs_direct = float(np.dot(w_real, FD_dXv_xs_direct))

absdiff = AN_scalar - FD_scalar_xs_direct
relerr = abs(absdiff) / (abs(FD_scalar_xs_direct) + 1e-300)
sign = "agree" if (AN_scalar * FD_scalar_xs_direct) > 0 else "FLIPPED"

print(
    "HANDCOMP_STAGE2 idx=%d h=%.3e AN_scalar=%.12e FD_scalar_xs_direct=%.12e abs_diff=%.6e rel_err=%.6e sign=%s"
    % (idx, h, AN_scalar, FD_scalar_xs_direct, absdiff, relerr, sign),
    flush=True,
)
print("HANDCOMP_DONE idx=%d t=%.1fs" % (idx, time.time() - t0), flush=True)
