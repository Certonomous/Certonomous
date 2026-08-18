#!/usr/bin/env python
"""
A5 analog of A1's `probeDCDDXv.py` (PROOF.md section 20), plus a direct
dXs/dShape machine-precision check.

TWO LINKS, TWO TESTS, one model instance:

STAGE A -- dXs/dShape (DVGeo's FFD Jacobian), expect machine precision.
  eta_AN = DVGeo.totalSensitivityProd(e_idx)                (analytic column)
  eta_FD = [DVGeo.update(shape + h e) - DVGeo.update(shape - h e)] / 2h
  reported as a max/relative componentwise error over the surface points, not
  as a contracted scalar -- a scalar dot product can hide a componentwise
  defect that happens to be orthogonal to the contraction direction, which is
  the exact failure mode that made A1's original warpDeriv clearance wrong.

STAGE B -- dObj/dXv, the objective's own reverse-mode sensitivity to the
volume mesh. This is the ONE link in A5's chain never tested against a true
finite difference of itself. `dR/dXv` was tested (2026-07-30 addendum) -- that
is the RESIDUAL's sensitivity, a different quantity.

  delta_Xv = [Xv(shape + h e) - Xv(shape - h e)] / 2h        (real warp FD)
  AN       = <w_real, delta_Xv>                              (chain rule, no solve)
  FD       = [OBJ(Xv0 + h delta_Xv) - OBJ(Xv0 - h delta_Xv)] / 2h

where each OBJ() is a FULL nonlinear primal re-solve at a DIRECTLY-SET volume
mesh (DASolver.setVolCoords), bypassing DVGeo and IDWarp entirely on the FD
side. w_real is the real captured d(OBJ.val)/dXv, same hook as probeA5RealSeed.

The objective is read back TWO ways at every solve -- solver.calcFunction()
(live) and evalFunctions() (time-history getter) -- because A5's own record has
a retracted probe that used evalFunctions without a solve and got 0.0. After a
real solvePrimal both should agree; printing both makes that visible instead of
assumed.

Serial (np=1) by construction: setVolCoords pushes a full undecomposed array,
and with one rank there is no processor-boundary consistency question of the
kind that invalidated an earlier A5 dR/dXv attempt.
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
from pygeo import geo_utils
import dafoam.mphys.mphys_dafoam as mphys_dafoam

parser = argparse.ArgumentParser()
parser.add_argument("--idxs", type=str, default="8,17,2")
parser.add_argument("--hs", type=str, default="1e-4,5e-5")
args = parser.parse_args()
IDXS = [int(s) for s in args.idxs.split(",")]
HS = [float(s) for s in args.hs.split(",")]

comm = MPI.COMM_WORLD
if comm.size != 1:
    raise RuntimeError("serial only (np=1) -- see module docstring")

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
        b = DAFoamBuilder(daOptionsAero, meshOptions, scenario="aerodynamic")
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
        nComp = {}
        for name, jj, ax in [("shapexUpper", 1, "x"), ("shapeyUpper", 1, "y"), ("shapezUpper", 1, "z"),
                             ("shapexLower", 0, "x"), ("shapeyLower", 0, "y"), ("shapezLower", 0, "z")]:
            PS = geo_utils.PointSelect("list", list(pts[7:16, jj, :].flatten()))
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
print("A5DOBJDXVRESET === running primal ===", flush=True)
prob.run_model()
obj0_om = float(prob.get_val("OBJ.val")[0])
print("A5DOBJDXVRESET === primal done t=%.1fs OBJ=%.15e ===" % (time.time() - t0, obj0_om), flush=True)

totals = prob.compute_totals(of=["OBJ.val"], wrt=["shapexUpper"])
dOBJ = np.array(totals[("OBJ.val", "shapexUpper")]).flatten()
print("A5DOBJDXVRESET === adjoint done t=%.1fs, captured %d rev call(s) ===" % (time.time() - t0, len(_captures)), flush=True)
print("A5DOBJDXVRESET dOBJ/dshapexUpper = %s" % np.array2string(dOBJ, precision=8, max_line_width=250), flush=True)
if not _captures:
    raise RuntimeError("A5DOBJDXVRESET FAIL: warper rev hook never fired")
w_real = _captures[-1]
print("A5DOBJDXVRESET ||w_real||=%.8e nXv=%d" % (float(np.linalg.norm(w_real)), w_real.size), flush=True)

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


Xv0 = warp_via_dvgeo(np.zeros(nShape))
if Xv0.size != w_real.size:
    raise RuntimeError("A5DOBJDXVRESET FAIL: Xv %d vs w_real %d" % (Xv0.size, w_real.size))

# ---------------------------------------------------------------------------
# STAGE A: dXs/dShape, componentwise, expect machine precision
# ---------------------------------------------------------------------------
for idx in IDXS:
    seedDV = {n: np.zeros(prob.model.nComp[n]) for n in DVGROUPS}
    seedDV["shapexUpper"][idx] = 1.0
    eta_AN = DVGeo.totalSensitivityProd(seedDV, ptSetName).reshape(xs0.shape)
    for h in HS:
        ep = np.zeros(nShape); ep[idx] = h
        em = np.zeros(nShape); em[idx] = -h
        set_shape(ep); xs_p = DVGeo.update(ptSetName).copy()
        set_shape(em); xs_m = DVGeo.update(ptSetName).copy()
        eta_FD = (xs_p - xs_m) / (2.0 * h)
        num = float(np.max(np.abs(eta_AN - eta_FD)))
        den = float(np.max(np.abs(eta_FD)))
        print("A5DXSDSHAPE idx=%d h=%.1e max_abs_diff=%.6e max_abs_eta=%.6e max_rel=%.6e nnz_AN=%d nnz_FD=%d"
              % (idx, h, num, den, num / (den + 1e-300),
                 int(np.sum(np.abs(eta_AN) > 1e-14)), int(np.sum(np.abs(eta_FD) > 1e-14))), flush=True)
set_shape(np.zeros(nShape))
DVGeo.update(ptSetName)

# ---------------------------------------------------------------------------
# STAGE B: dObj/dXv vs a true re-solve finite difference
# ---------------------------------------------------------------------------
W0_RESET = [None]


def obj_at_Xv(Xv, tag):
    ts = time.time()
    DASolver.setVolCoords(Xv.copy())
    # PATH-DEPENDENCE CONTROL: every solve starts from the SAME baseline state,
    # not from whatever the previous solve in the sweep left behind. Without
    # this, the "+" leg warm-starts from the "-" leg's converged state and vice
    # versa, so the two legs of a central difference travel different paths to
    # a limit-cycle fixed point -- an asymmetry that does not shrink with h and
    # therefore mimics a real gradient error. Cost: identical (same iteration
    # count). This is a control on the PROBE, not on the code under test.
    if W0_RESET[0] is not None:
        DASolver.setStates(W0_RESET[0].copy())
    DASolver()
    if DASolver.primalFail != 0:
        raise RuntimeError("A5DOBJDXVRESET FAIL: primal failed at perturbed Xv (%s)" % tag)
    tp1_c = float(DASolver.solver.calcFunction("TP1"))
    tp2_c = float(DASolver.solver.calcFunction("TP2"))
    f = {}
    DASolver.evalFunctions(f)
    tp1_e, tp2_e = float(f["TP1"]), float(f["TP2"])
    print("A5DOBJDXVRESET_SOLVE %s calcFunction: TP1=%.15e TP2=%.15e OBJ=%.15e | "
          "evalFunctions: TP1=%.15e TP2=%.15e OBJ=%.15e | agree_diff=%.3e t=%.1fs"
          % (tag, tp1_c, tp2_c, tp1_c - tp2_c, tp1_e, tp2_e, tp1_e - tp2_e,
             (tp1_c - tp2_c) - (tp1_e - tp2_e), time.time() - ts), flush=True)
    return tp1_c - tp2_c


# baseline re-solve at the unperturbed, directly-set Xv0 -- must reproduce the
# established converged objective, or the whole setVolCoords path is suspect
obj0_direct = obj_at_Xv(Xv0, "BASELINE_warmpath")
W0_RESET[0] = DASolver.getStates().copy()
obj0_direct = obj_at_Xv(Xv0, "BASELINE_reset")
print("A5RESET baseline state captured, ||W0||=%.8e" % float(np.linalg.norm(W0_RESET[0])), flush=True)
print("A5DOBJDXVRESET_BASELINE direct=%.15e openmdao=%.15e diff=%.3e"
      % (obj0_direct, obj0_om, obj0_direct - obj0_om), flush=True)

for idx in IDXS:
    for h in HS:
        ep = np.zeros(nShape); ep[idx] = h
        em = np.zeros(nShape); em[idx] = -h
        Xv_p = warp_via_dvgeo(ep)
        Xv_m = warp_via_dvgeo(em)
        delta_Xv = (Xv_p - Xv_m) / (2.0 * h)
        set_shape(np.zeros(nShape))
        DVGeo.update(ptSetName)

        AN = float(np.dot(w_real, delta_Xv))
        objp = obj_at_Xv(Xv0 + h * delta_Xv, "idx=%d h=%.1e +" % (idx, h))
        objm = obj_at_Xv(Xv0 - h * delta_Xv, "idx=%d h=%.1e -" % (idx, h))
        FD = (objp - objm) / (2.0 * h)
        rel = abs(AN - FD) / (abs(FD) + 1e-300)
        sign = "agree" if (AN * FD) > 0 else "FLIPPED"
        print("A5DOBJDXVRESET_RESULT idx=%d h=%.1e AN=%.12e FD=%.12e rel_err=%.6e sign=%s "
              "framework_dOBJdshape=%.12e ||delta_Xv||=%.6e"
              % (idx, h, AN, FD, rel, sign, dOBJ[idx], float(np.linalg.norm(delta_Xv))), flush=True)

DASolver.setVolCoords(Xv0.copy())
print("A5DOBJDXVRESET_DONE t=%.1fs" % (time.time() - t0), flush=True)
