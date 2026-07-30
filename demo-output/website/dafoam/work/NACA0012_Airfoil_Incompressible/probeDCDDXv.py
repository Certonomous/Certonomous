#!/usr/bin/env python
"""
r6-airfoil-second-gradient-mechanism: isolate the LAST unprobed link in the
derivative chain, dCD/dXv itself, and test it against a finite difference of
the link itself.

Every mechanism tested so far for idx0/idx1's 9-16% gap (PROOF.md 11-19) was a
NAMED SUB-MECHANISM inside dCD/dXv (frozen wall-distance, the SA wall-function
branch, mesh quality). Two links upstream of it -- dXs/dShape (the FFD/DVGeo
Jacobian) and dXv/dXs (mesh.warpDeriv) -- were independently verified clean
for idx0/idx1 (11.1, 18). dCD/dXv, the CFD/turbulence residual's own
differentiated sensitivity to volume-mesh coordinates, has never itself been
tested against a finite difference of ITSELF -- every previous check either
tested a named piece of it (branch, wall-distance) or tested it together with
the warp/FFD chain (the real-seed test, section 18, which uses dCD/dXv as a
FROZEN, given seed, not as the thing under test).

METHOD. DASolver exposes exactly the low-level API needed to isolate this
link, found by reading dafoam/pyDAFoam.py and dafoam/mphys/mphys_dafoam.py
directly (the same method that found mesh.warpDeriv and calcNut() earlier in
this investigation):

    DASolver.setVolCoords(Xv)   -> solver.updateOFMesh(Xv) / solverAD ditto
                                    (pushes arbitrary Xv into OpenFOAM's mesh,
                                    completely bypassing DVGeo/IDWarp)
    DASolver()                  -> solver.solvePrimal() (the real nonlinear
                                    primal solve, at whatever Xv is currently
                                    set)
    DASolver.evalFunctions(fd)  -> fd["CD"] (functional, from the just-solved
                                    state)

This lets CD be evaluated as a genuine function of Xv alone, with NO shape/
DVGeo/warp anywhere in the loop, and NO frozen/linearized approximation on
the FD side -- each evaluation is a full, real, re-converged primal solve.

The perturbation direction used is deliberately not arbitrary: it is
delta_Xv = dXv/dShape_idx (idx0 or idx1), computed the same way section 18's
real-seed script computes it (central difference of the REAL nonlinear warp,
mesh.warpMesh(), at shape=idx+-h) -- i.e. exactly the volume-mesh direction
idx0/idx1's own shape motion actually produces, already independently
verified (18) to be a clean, non-defective quantity in its own right. Given
that, to first order in h, Xv0 + h*delta_Xv IS the same mesh warpMesh()+DVGeo
would have produced at shape=+h -- so this construction lets the SAME
physical mesh state be reached two different ways (through DVGeo+warp, the
already-proven-clean route; and directly via setVolCoords, bypassing it
entirely), which is itself a check on the construction, not just on dCD/dXv.

The comparison:
    AN_scalar = <w_real, delta_Xv>        (adjoint's own dCD/dXv, captured
                                            from a real CD adjoint solve via
                                            the same hook as section 17/18,
                                            dotted with delta_Xv -- a LINEAR
                                            prediction, no new solve)
    FD_scalar = (CD(Xv0+h*delta_Xv) - CD(Xv0-h*delta_Xv)) / (2h)
                                           (a TRUE finite difference of CD as
                                            a function of Xv, via two full
                                            primal RESOLVES at the directly-
                                            set, perturbed mesh -- this is the
                                            finite difference OF THE LINK
                                            ITSELF, dCD/dXv, not of dCD/dShape)

If dCD/dXv is correct, AN_scalar should match FD_scalar to roughly the same
tolerance idx4 (control) already shows elsewhere in this investigation
(2-3%). A large, sign-flipped, or step-unstable disagreement specific to
idx0/idx1 (and absent for idx4) would newly implicate this link. Agreement
(for idx0/idx1 too) would mean every link is now independently verified
clean, and the defect lives in the assembly/solve, not any single link --
mirroring the U-bend finding on a different case.

CAUTIONS carried over from the U-bend agent's own probe failures (both were
its own instrumentation bugs, not the code under test):
  - if FD_scalar changes by an order of magnitude or more between two step
    sizes, suspect this probe before the adjoint;
  - if AN_scalar/FD_scalar lands on an implausibly large or small ratio,
    check it component-by-component against this case's own known constants
    (U0=10, CD scale=1/(0.5*U0^2*A0*rho0)=0.2, normalizeStates U=10/p=50/
    nuTilda=4.5e-4) before believing a "defect".

Runs SERIAL (np=1), matching sections 13/19's budget-respecting convention
and, more importantly, avoiding decomposePar entirely -- DASolver.setVolCoords
pushes a FULL, undecomposed array in serial, so there is no possibility of a
decomposition mismatch of the kind that invalidated one early parallel run in
this investigation (section 15.2).
"""
import os
import sys
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
parser.add_argument("--idx", type=int, required=True, help="shape DV to build delta_Xv from (0,1,4,...)")
parser.add_argument("--h", type=float, default=1e-4, help="step size, both for delta_Xv and for the Xv perturbation")
args = parser.parse_args()

comm = MPI.COMM_WORLD
rank = comm.rank
nRanks = comm.size
if nRanks != 1:
    raise RuntimeError("This probe is designed to run serial (np=1) -- see module docstring.")

U0 = 10.0
p0 = 0.0
nuTilda0 = 4.5e-5
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
            "type": "force", "source": "patchToFace", "patches": ["wing"],
            "directionMode": "parallelToFlow", "patchVelocityInputName": "patchV",
            "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0),
        },
        "CL": {
            "type": "force", "source": "patchToFace", "patches": ["wing"],
            "directionMode": "normalToFlow", "patchVelocityInputName": "patchV",
            "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0),
        },
    },
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 1, "jacMatReOrdering": "rcm"},
    "normalizeStates": {"U": U0, "p": U0 * U0 / 2.0, "nuTilda": nuTilda0 * 10.0, "phi": 1.0},
    "inputInfo": {
        "aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]},
        "patchV": {
            "type": "patchVelocity", "patches": ["inout"], "flowAxis": "x",
            "normalAxis": "y", "components": ["solver", "function"],
        },
    },
}

meshOptions = {
    "gridFile": os.getcwd(), "fileType": "OpenFOAM",
    "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]], [[0.0, 0.0, 0.1], [0.0, 0.0, 1.0]]],
}

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
        self.add_constraint("scenario1.aero_post.CL", equals=0.5, scaler=1.0)
        self.add_constraint("geometry.thickcon", lower=0.5, upper=3.0, scaler=1.0)
        self.add_constraint("geometry.volcon", lower=1.0, scaler=1.0)
        self.add_constraint("geometry.rcon", lower=0.8, scaler=1.0)


t0 = time.time()
prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")

print("DCDDXV === running primal (run_model) ===", flush=True)
prob.run_model()
cd_baseline = float(prob.get_val("scenario1.aero_post.CD")[0])
print("DCDDXV === primal done, t=%.1fs, CD_baseline=%.15e, running real CD adjoint ===" % (time.time() - t0, cd_baseline), flush=True)

totals = prob.compute_totals(of=["scenario1.aero_post.CD"], wrt=["shape"])
dCDdshape = np.array(totals[("scenario1.aero_post.CD", "shape")]).flatten()
print("DCDDXV === adjoint done, t=%.1fs, warper captured %d rev-mode call(s) ===" % (time.time() - t0, len(_captures)), flush=True)
print("DCDDXV dCD/dshape (this run) = %s" % np.array2string(dCDdshape, precision=6), flush=True)

if len(_captures) == 0:
    raise RuntimeError("DCDDXV FAIL: capture hook never fired, no real dCD/dXv seed available.")
w_real = _captures[-1]
nXv = w_real.size
print("DCDDXV ||w_real||_2 = %.6e, nXv=%d" % (float(np.linalg.norm(w_real)), nXv), flush=True)

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


Xv0 = get_warped_Xv(np.zeros(nShape))
if Xv0.size != nXv:
    raise RuntimeError("DCDDXV FAIL: Xv size (%d) != w_real size (%d), partition mismatch." % (Xv0.size, nXv))


def resolve_CD_at_Xv(Xv):
    """Directly push Xv into OpenFOAM (bypassing DVGeo/warp entirely), run
    the real nonlinear primal solve, and read CD back. This is the FD side
    of the dCD/dXv link test -- a true re-solve, not a linearization."""
    DASolver.setVolCoords(Xv.copy())
    DASolver()
    if DASolver.primalFail != 0:
        raise RuntimeError("DCDDXV FAIL: primal failed at perturbed Xv.")
    states = DASolver.getStates()
    DASolver.setStates(states)
    funcs = {}
    DASolver.evalFunctions(funcs)
    return float(funcs["CD"])


idx = args.idx
h = args.h

ePlus = np.zeros(nShape)
ePlus[idx] = h
eMinus = np.zeros(nShape)
eMinus[idx] = -h

Xv_p_dvgeo = get_warped_Xv(ePlus)
Xv_m_dvgeo = get_warped_Xv(eMinus)
delta_Xv = (Xv_p_dvgeo - Xv_m_dvgeo) / (2.0 * h)
print("DCDDXV idx=%d h=%.3e ||delta_Xv||_2=%.6e" % (idx, h, float(np.linalg.norm(delta_Xv))), flush=True)

# restore baseline mesh state on the geometry/warp side before driving Xv directly
set_shape(np.zeros(nShape))
DVGeo.update(ptSetName)

AN_scalar = float(np.dot(w_real, delta_Xv))
print("DCDDXV_AN idx=%d h=%.3e AN_scalar=%.12e" % (idx, h, AN_scalar), flush=True)

Xv_plus_direct = Xv0 + h * delta_Xv
Xv_minus_direct = Xv0 - h * delta_Xv

t_solve = time.time()
CD_plus = resolve_CD_at_Xv(Xv_plus_direct)
print("DCDDXV_SOLVE idx=%d h=%.3e sign=+ CD=%.15e t=%.1fs" % (idx, h, CD_plus, time.time() - t_solve), flush=True)

t_solve = time.time()
CD_minus = resolve_CD_at_Xv(Xv_minus_direct)
print("DCDDXV_SOLVE idx=%d h=%.3e sign=- CD=%.15e t=%.1fs" % (idx, h, CD_minus, time.time() - t_solve), flush=True)

# restore the solver's mesh/state to baseline before exiting, tidy
DASolver.setVolCoords(Xv0.copy())

FD_scalar = (CD_plus - CD_minus) / (2.0 * h)
absdiff = AN_scalar - FD_scalar
relerr = abs(absdiff) / (abs(FD_scalar) + 1e-300)
sign = "agree" if (AN_scalar * FD_scalar) > 0 else "FLIPPED"

print(
    "DCDDXV_RESULT idx=%d h=%.3e AN_scalar=%.12e FD_scalar=%.12e abs_diff=%.6e rel_err=%.6e sign=%s"
    % (idx, h, AN_scalar, FD_scalar, absdiff, relerr, sign),
    flush=True,
)
print("DCDDXV_DONE idx=%d t=%.1fs" % (idx, time.time() - t0), flush=True)
