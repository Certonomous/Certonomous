#!/usr/bin/env python
"""Supervisor-sweep independent verification driver, 2026-08-04.

Written from scratch for the adversarial verification of the
getRotationMatrix3d degenerate-branch claim. NOT the lab's diag/repro script.
Deliberate differences from the lab's instrument:

  * The real objective seed w = d(OBJ)/dXv is captured by wrapping
    idwarp.USMesh.warpDeriv itself (the function under test), not by hooking
    DAFoamWarper.compute_jacvec_product.
  * The perturbation direction eta = dXs/dShape_idx is obtained by CENTRAL FD
    of DVGeo.update (two step sizes, linearity checked), not by
    DVGeo.totalSensitivityProd; totalSensitivityProd is printed only as a
    cross-check.
  * The warp FD is evaluated at two steps (1e-4 and 3e-4) so the FD itself is
    step-verified inside this run.
  * Per-rank md5 of the baseline warped grid bytes is printed for the primal
    invariance check.

Case: official DAFoam tutorial UBend_Channel (tutorials @ d3b7e38), with the
published A5 rung's pure pressure-loss objective val = TP1 - TP2 (HFX not in
the adjoint). Single DV group shapexUpper (27 comps), idx from env VIDX.
"""
import os
import time
import hashlib
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from dafoam.mphys import DAFoamBuilder
from pygeo.mphys import OM_DVGEOCOMP
from pygeo import geo_utils

import idwarp

comm = MPI.COMM_WORLD
rank = comm.rank
IDX = int(os.environ.get("VIDX", "8"))


def p0(*a):
    if rank == 0:
        print("SUPV", *a, flush=True)


p0("idwarp_from", idwarp.__file__)

# --- capture the seed at the function under test itself --------------------
_seeds = []
_orig_warpDeriv = idwarp.USMesh.warpDeriv


def _capturing_warpDeriv(self, dXv, **kw):
    _seeds.append(np.array(dXv, copy=True))
    return _orig_warpDeriv(self, dXv, **kw)


idwarp.USMesh.warpDeriv = _capturing_warpDeriv

# --- tutorial model, pressure-loss objective --------------------------------
U0 = 8.4
daOptions = {
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


class Top(Multipoint):
    def setup(self):
        b = DAFoamBuilder(daOptions, meshOptions, scenario="aerodynamic")
        b.initialize(self.comm)
        self.dafoam_builder = b
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])
        self.add_subsystem("mesh_aero", b.get_mesh_coordinate_subsystem())
        self.add_subsystem("geometry_aero", OM_DVGEOCOMP(file="FFD/UBendDuctFFDSym.xyz", type="ffd"))
        self.mphys_add_scenario("scenario", ScenarioAerodynamic(aero_builder=b))
        self.connect("mesh_aero.x_aero0", "geometry_aero.x_aero_in")
        self.connect("geometry_aero.x_aero0", "scenario.x_aero")
        self.add_subsystem("OBJ", om.ExecComp("val = TP1 - TP2"))

    def configure(self):
        super().configure()
        self.geometry_aero.nom_add_discipline_coords("aero", self.mesh_aero.mphys_get_surface_mesh())
        pts = self.geometry_aero.nom_getDVGeo().getLocalIndex(0)
        PS = geo_utils.PointSelect("list", list(pts[7:16, 1, :].flatten()))
        n = self.geometry_aero.nom_addLocalDV(dvName="shapexUpper", pointSelect=PS, axis="x")
        self.dvs.add_output("shapexUpper", val=np.zeros(n))
        self.connect("shapexUpper", "geometry_aero.shapexUpper")
        self.add_design_var("shapexUpper", lower=-0.04, upper=0.04, scaler=25.0)
        self.nShape = n
        self.connect("scenario.aero_post.TP1", "OBJ.TP1")
        self.connect("scenario.aero_post.TP2", "OBJ.TP2")
        self.add_objective("OBJ.val", scaler=1.0)


t0 = time.time()
prob = om.Problem(reports=None)
prob.model = Top()
prob.setup(mode="rev")
prob.run_model()
p0("primal_done t=%.1f OBJ=%.15e" % (time.time() - t0, float(prob.get_val("OBJ.val")[0])))

totals = prob.compute_totals(of=["OBJ.val"], wrt=["shapexUpper"])
dOBJ = np.array(totals[("OBJ.val", "shapexUpper")]).flatten()
p0("adjoint_done t=%.1f warpDeriv_calls_captured=%d" % (time.time() - t0, len(_seeds)))

if not _seeds:
    raise RuntimeError("SUPV FAIL: warpDeriv wrapper never fired")
w = _seeds[-1]

DASolver = prob.model.dafoam_builder.DASolver
mesh = DASolver.mesh
DVGeo = prob.model.geometry_aero.nom_getDVGeo()
nShape = prob.model.nShape
ptSet = "x_aero0"

wn = comm.allreduce(float(np.dot(w, w)), op=MPI.SUM) ** 0.5
p0("seed idx=%d nShape=%d ||w||=%.8e nRanks=%d" % (IDX, nShape, wn, comm.size))


def xs_of(dv):
    DVGeo.setDesignVars({"shapexUpper": np.array(dv)})
    return DVGeo.update(ptSet)


def warp_xs(xs):
    DASolver.setSurfaceCoordinates(xs, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    return mesh.getSolverGrid().copy()


# eta by central FD of DVGeo at two steps: linearity check on the FFD map
e = np.zeros(nShape)
e[IDX] = 1.0
etas = {}
for s in (1e-5, 1e-3):
    etas[s] = (xs_of(s * e) - xs_of(-s * e)) / (2.0 * s)
lin = comm.allreduce(float(np.max(np.abs(etas[1e-5] - etas[1e-3]))) if etas[1e-5].size else 0.0, op=MPI.MAX)
eta = etas[1e-5]
en = comm.allreduce(float(np.dot(eta.flatten(), eta.flatten())), op=MPI.SUM) ** 0.5
# cross-check against pygeo's own product
seedDV = {"shapexUpper": np.zeros(nShape)}
seedDV["shapexUpper"][IDX] = 1.0
eta2 = DVGeo.totalSensitivityProd(seedDV, ptSet).reshape(eta.shape)
xdiff = comm.allreduce(float(np.max(np.abs(eta - eta2))) if eta.size else 0.0, op=MPI.MAX)
p0("eta ||eta||=%.8e ffd_linearity_maxdiff=%.3e vs_totalSensitivityProd_maxdiff=%.3e" % (en, lin, xdiff))

# baseline
xs_base = xs_of(np.zeros(nShape))
Xv0 = warp_xs(xs_base)
if w.size != Xv0.size:
    raise RuntimeError("SUPV FAIL: seed/Xv size mismatch %d vs %d" % (w.size, Xv0.size))
md5 = hashlib.md5(Xv0.tobytes()).hexdigest()
for r in range(comm.size):
    if rank == r:
        print("SUPV baseline_grid rank=%d n=%d md5=%s" % (r, Xv0.size, md5), flush=True)
    comm.Barrier()
n0 = comm.allreduce(float(np.dot(Xv0, Xv0)), op=MPI.SUM) ** 0.5
p0("baseline ||Xv0||=%.15e" % (n0 / (comm.allreduce(Xv0.size, op=MPI.SUM) ** 0.5)))

# FD of the warp along eta, two steps
FDs = {}
for h in (1e-4, 3e-4):
    Xvp = warp_xs(xs_base + h * eta)
    Xvm = warp_xs(xs_base - h * eta)
    FDs[h] = comm.allreduce(float(np.dot(w, (Xvp - Xvm) / (2.0 * h))), op=MPI.SUM)
    p0("FD h=%.0e  FD=%.10e" % (h, FDs[h]))

# analytic: warpDeriv at the baseline
warp_xs(xs_base)
mesh.warpDeriv(w)
dXs = mesh.getdXs()
dXs = DASolver.mapVector(dXs, DASolver.allWallsGroup, DASolver.designSurfacesGroup)
AN = comm.allreduce(float(np.dot(dXs.flatten(), eta.flatten())), op=MPI.SUM)

FD = FDs[1e-4]
rel = abs(AN - FD) / (abs(FD) + 1e-300)
flip = (AN * FD) <= 0
p0("RESULT idx=%d FD(1e-4)=%.10e FD(3e-4)=%.10e AN=%.10e framework_dOBJ=%.10e rel_err=%.6e sign=%s t=%.1f"
   % (IDX, FDs[1e-4], FDs[3e-4], AN, dOBJ[IDX], rel, "FLIP" if flip else "ok", time.time() - t0))
