#!/usr/bin/env python
"""
A5 (U-bend) analog of A1's `probeWarpDerivRealSeed.py` + `probeHandComposition.py`,
run as ONE script so all three quantities come from the SAME model instance and
the SAME captured seed.

WHY THIS EXISTS. Every `mesh.warpDeriv` test ever run on A5
(`probeWarpDerivA5.py`, `probeA5HandComposition.py`) used an ARBITRARY RANDOM
seed vector `w` on the volume-mesh output space (seeds 2026 and 42). A1's record
(PROOF.md section 17) shows that is exactly the test that gives a MISLEADING
answer: under a random seed, A1's idx6 and idx7 failed identically (108-149%,
both sign-flipped); under the REAL objective's own `dCD/dXv` seed they split
apart exactly as the real `check_totals` result does (idx6 634% flipped, idx7
1.74% clean). A random direction measures whether warpDeriv's error is large
SOMEWHERE; only the real seed measures whether it reaches THIS objective's
gradient. A5's warpDeriv "clearance" (0.32-1.30%, no sign flip) rests entirely
on random seeds and has never been repeated with the real seed.

WHAT THIS SCRIPT MEASURES, per component, with `w = w_real` (the real,
fully-accumulated d(OBJ.val)/dXv captured verbatim from the framework's own
reverse-mode call on DAFoamWarper):

  AN      = <warpDeriv(w_real), dXs/dShape_idx>          (hand-composed chain)
  FD_dvgeo= <w_real, [Xv(shape+h e) - Xv(shape-h e)]/2h>  (FD through DVGeo.update)
  FD_xs   = <w_real, [Xv(xs0+h eta) - Xv(xs0-h eta)]/2h>  (FD with DVGeo BYPASSED,
                                                           isolates warpDeriv alone)

and cross-checks AN against the framework's own compute_totals column, which is
A1 PROOF.md section 21.1's Stage-1 hand-composition test (if they agree to
machine precision, OpenMDAO's assembly is exact and the seed capture is valid).

No number is adjusted and no seed is chosen: `w_real` is whatever this run's
adjoint produced. Two step sizes per component so step-size instability -- one
of the two probe-failure signatures this investigation has already been burned
by -- is visible rather than assumed absent.
"""
import os
import time
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP
from pygeo import geo_utils
import dafoam.mphys.mphys_dafoam as mphys_dafoam

comm = MPI.COMM_WORLD
rank = comm.rank
nRanks = comm.size

U0 = 8.4

daOptionsAero = {
    "solverName": "DASimpleFoam",
    "designSurfaces": ["ubend"],
    "useAD": {"mode": "reverse"},
    "primalMinResTol": 1e-8,
    "primalMinResTolDiff": 1e7,
    "writeMinorIterations": True,
    "wallDistanceMethod": "daCustom",
    "primalBC": {"useWallFunction": True},
    "function": {
        "TP1": {"type": "totalPressure", "source": "patchToFace", "patches": ["inlet"],
                "scale": 1.0, "addToAdjoint": True},
        "TP2": {"type": "totalPressure", "source": "patchToFace", "patches": ["outlet"],
                "scale": 1.0, "addToAdjoint": True},
        "HFX": {"type": "wallHeatFlux", "source": "patchToFace", "patches": ["ubend"],
                "scale": 1.0, "addToAdjoint": False},
    },
    "adjStateOrdering": "cell",
    "adjEqnOption": {"gmresRelTol": 1e-5, "gmresTolDiff": 1e4, "pcFillLevel": 2,
                     "jacMatReOrdering": "natural", "gmresMaxIters": 3000, "gmresRestart": 3000},
    "normalizeStates": {"U": U0, "p": (U0 * U0) / 2.0, "nuTilda": 1e-3, "phi": 1.0, "T": 300},
    "inputInfo": {"aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]}},
    "outputInfo": {"q_convect": {"type": "thermalCouplingOutput", "patches": ["ubend"],
                                 "components": ["thermalCoupling"]}},
}

meshOptions = {"gridFile": os.getcwd(), "fileType": "OpenFOAM", "symmetryPlanes": []}

# ---------------------------------------------------------------------------
# capture hook -- identical to A1's, records every reverse-mode
# d_outputs["aero_vol_coords"] the framework hands the warper. That argument IS
# the `dxV` passed verbatim to mesh.warpDeriv(dxV) in the real adjoint chain.
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

DVGROUPS = ["shapexUpper", "shapeyUpper", "shapezUpper",
            "shapexLower", "shapeyLower", "shapezLower"]


class Top(Multipoint):
    def setup(self):
        dafoam_builder = DAFoamBuilder(daOptionsAero, meshOptions, scenario="aerodynamic")
        dafoam_builder.initialize(self.comm)
        self.dafoam_builder = dafoam_builder

        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])
        self.add_subsystem("mesh_aero", dafoam_builder.get_mesh_coordinate_subsystem())
        self.add_subsystem("geometry_aero", OM_DVGEOCOMP(file="FFD/UBendDuctFFDSym.xyz", type="ffd"))
        self.mphys_add_scenario("scenario", ScenarioAerodynamic(aero_builder=dafoam_builder))
        self.connect("mesh_aero.x_aero0", "geometry_aero.x_aero_in")
        self.connect("geometry_aero.x_aero0", "scenario.x_aero")
        self.add_subsystem("OBJ", om.ExecComp("val = TP1 - TP2"))

    def configure(self):
        super().configure()
        points_aero = self.mesh_aero.mphys_get_surface_mesh()
        self.geometry_aero.nom_add_discipline_coords("aero", points_aero)
        pts = self.geometry_aero.nom_getDVGeo().getLocalIndex(0)

        nComp = {}
        for name, jj, ax in [("shapexUpper", 1, "x"), ("shapeyUpper", 1, "y"), ("shapezUpper", 1, "z"),
                             ("shapexLower", 0, "x"), ("shapeyLower", 0, "y"), ("shapezLower", 0, "z")]:
            indexList = list(pts[7:16, jj, :].flatten())
            PS = geo_utils.PointSelect("list", indexList)
            nComp[name] = self.geometry_aero.nom_addLocalDV(dvName=name, pointSelect=PS, axis=ax)

        for name in DVGROUPS:
            self.dvs.add_output(name, val=np.array([0.0] * nComp[name]))
            self.connect(name, "geometry_aero.%s" % name)
            self.add_design_var(name, lower=-0.04, upper=0.04, scaler=25.0)

        self.nComp = nComp
        self.connect("scenario.aero_post.TP1", "OBJ.TP1")
        self.connect("scenario.aero_post.TP2", "OBJ.TP2")
        self.add_objective("OBJ.val", scaler=1.0)


t0 = time.time()
prob = om.Problem(reports=None)
prob.model = Top()
prob.setup(mode="rev")

if rank == 0:
    print("A5REALSEED === running primal (run_model) ===", flush=True)
prob.run_model()
if rank == 0:
    print("A5REALSEED === primal done t=%.1fs OBJ.val=%.15e TP1=%.15e TP2=%.15e ==="
          % (time.time() - t0, float(prob.get_val("OBJ.val")[0]),
             float(prob.get_val("scenario.aero_post.TP1")[0]),
             float(prob.get_val("scenario.aero_post.TP2")[0])), flush=True)

# ONE real reverse-mode adjoint solve for the real objective only.
totals = prob.compute_totals(of=["OBJ.val"], wrt=["shapexUpper"])
dOBJ = np.array(totals[("OBJ.val", "shapexUpper")]).flatten()

if rank == 0:
    print("A5REALSEED === adjoint done t=%.1fs, warper captured %d rev-mode call(s) ==="
          % (time.time() - t0, len(_captures)), flush=True)
    print("A5REALSEED dOBJ/dshapexUpper (this run) = %s"
          % np.array2string(dOBJ, precision=8, max_line_width=200), flush=True)

if len(_captures) == 0:
    raise RuntimeError("A5REALSEED FAIL: warper rev-mode hook never fired; no real dOBJ/dXv seed.")

for ic, c in enumerate(_captures):
    n2 = comm.allreduce(float(np.dot(c, c)), op=MPI.SUM) ** 0.5
    if rank == 0:
        print("A5REALSEED capture[%d] ||.||_2(global)=%.8e" % (ic, n2), flush=True)

w_real_local = _captures[-1]
nXvLocal = w_real_local.size
nXvGlobal = comm.allreduce(nXvLocal, op=MPI.SUM)

DASolver = prob.model.dafoam_builder.DASolver
mesh = DASolver.mesh
DVGeo = prob.model.geometry_aero.nom_getDVGeo()
ptSetName = "x_aero0"
nShape = prob.model.nComp["shapexUpper"]
xs0 = DASolver.getSurfaceCoordinates(DASolver.designSurfacesGroup).copy()


def set_shape(vec):
    DVGeo.setDesignVars({"shapexUpper": np.array(vec)})


def warp_via_dvgeo(shapeVec):
    set_shape(shapeVec)
    xs = DVGeo.update(ptSetName)
    DASolver.setSurfaceCoordinates(xs, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    return mesh.getSolverGrid().copy()


def warp_via_direct_xs(xs):
    DASolver.setSurfaceCoordinates(xs, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    return mesh.getSolverGrid().copy()


Xv0 = warp_via_dvgeo(np.zeros(nShape))
if Xv0.size != nXvLocal:
    raise RuntimeError("A5REALSEED FAIL: partition mismatch, Xv local %d vs w_real local %d"
                       % (Xv0.size, nXvLocal))

set_shape(np.zeros(nShape))
xs_base = DVGeo.update(ptSetName)
DASolver.setSurfaceCoordinates(xs_base, DASolver.designSurfacesGroup)
mesh.warpMesh()

# --- warpDeriv seeded with the REAL objective sensitivity, once (it does not
#     depend on idx; only its contraction with eta does) ---
mesh.warpDeriv(w_real_local)
dXs_seed = mesh.getdXs()
dXs_seed = DASolver.mapVector(dXs_seed, DASolver.allWallsGroup, DASolver.designSurfacesGroup)

# idx set: the two sign-flipped components (8, 17), the two cleanest controls
# (2, 26), plus idx3 (largest non-flipping error, 179%) and idx15 (largest-
# magnitude gradient component, 42.9% error).
for idx in [2, 3, 8, 15, 17, 26]:
    # eta = dXs/dShape_idx, DVGeo's own analytic Jacobian column
    seedDV = {name: np.zeros(prob.model.nComp[name]) for name in DVGROUPS}
    seedDV["shapexUpper"][idx] = 1.0
    eta = DVGeo.totalSensitivityProd(seedDV, ptSetName).reshape(xs0.shape)

    AN_local = float(np.dot(dXs_seed.flatten(), eta.flatten()))
    AN = comm.allreduce(AN_local, op=MPI.SUM)

    for h in [1e-4, 1e-5]:
        ePlus = np.zeros(nShape)
        ePlus[idx] = h
        eMinus = np.zeros(nShape)
        eMinus[idx] = -h

        Xv_p = warp_via_dvgeo(ePlus)
        Xv_m = warp_via_dvgeo(eMinus)
        FD_dvgeo = comm.allreduce(float(np.dot(w_real_local, (Xv_p - Xv_m) / (2.0 * h))), op=MPI.SUM)

        Xv_p = warp_via_direct_xs(xs_base + h * eta)
        Xv_m = warp_via_direct_xs(xs_base - h * eta)
        FD_xs = comm.allreduce(float(np.dot(w_real_local, (Xv_p - Xv_m) / (2.0 * h))), op=MPI.SUM)

        # restore baseline mesh
        set_shape(np.zeros(nShape))
        DVGeo.update(ptSetName)
        DASolver.setSurfaceCoordinates(xs_base, DASolver.designSurfacesGroup)
        mesh.warpMesh()

        rel_xs = abs(AN - FD_xs) / (abs(FD_xs) + 1e-300)
        rel_dvgeo = abs(AN - FD_dvgeo) / (abs(FD_dvgeo) + 1e-300)
        nonlin = abs(FD_dvgeo - FD_xs) / (abs(FD_dvgeo) + 1e-300)
        sign = "agree" if (AN * FD_xs) > 0 else "FLIPPED"

        if rank == 0:
            print("A5REALSEED_RESULT idx=%d h=%.1e nRanks=%d AN=%.12e framework=%.12e "
                  "AN_vs_framework_reldiff=%.3e FD_dvgeo=%.12e FD_xs=%.12e "
                  "relerr_vs_FDxs=%.6e relerr_vs_FDdvgeo=%.6e dvgeo_nonlin=%.3e sign=%s"
                  % (idx, h, nRanks, AN, dOBJ[idx],
                     abs(AN - dOBJ[idx]) / (abs(dOBJ[idx]) + 1e-300),
                     FD_dvgeo, FD_xs, rel_xs, rel_dvgeo, nonlin, sign), flush=True)

if rank == 0:
    print("A5REALSEED_DONE nRanks=%d t=%.1fs" % (nRanks, time.time() - t0), flush=True)
