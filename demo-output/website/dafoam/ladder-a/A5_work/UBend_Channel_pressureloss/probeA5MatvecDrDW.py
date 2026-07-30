#!/usr/bin/env python
"""
Coordinator-directed off-diagonal test for A5's dR/dW. The diagonal-ratio test
(probeA5DiagRatio.py) only probed each residual component's dependence on ITS
OWN state -- diagonal entries. Off-diagonals encode cell-to-cell and
field-to-field COUPLING, and a defect confined there would look exactly like
A5: locally correct magnitudes, a globally wrong assembled answer, and sign
flips only where coupling happens to dominate.

Method: a matvec dot-product identity exactly like the one used throughout
this investigation for mesh.warpDeriv, but for dR/dW, with the diagonal
test's own units correction applied so the 285-337x factor does not reappear
disguised as a "coupling defect":

    FD_scalar = <w_R, (R(W0+h*dW) - R(W0-h*dW))/(2h)>
    AN_scalar = <dW, calcJacTVecProduct(stateVar, W0, residual, seed=w_R)>

dW is DENSE (nonzero at every state DOF, relative-magnitude scaled, exactly
as in probeChainLinksA5.py) -- this is what exercises off-diagonal coupling:
a dense direction perturbs every cell's state simultaneously, and any residual
component that couples to a NEIGHBORING cell or a DIFFERENT field picks up a
contribution through that coupling, not just through its own diagonal term.

w_R is the part that needs the units fix. probeA5DiagRatio.py established
that calcJacTVecProduct's "residual" output is row-scaled: for 43 of 60
sampled diagonal indices, AN_i/FD_i landed on EXACTLY one of four constants
-- 8.4, 35.28, 0.001, 300 -- matching that ROW's own normalizeStates constant
(U, p, nuTilda, T respectively), independent of which column contributed. If
that row-scaling extends to the full matrix (AN_row = D_row * J_true_row for
every column, not just the diagonal -- the standard "normalize each equation
by its own reference scale" convention), then pre-dividing w_R's components
by their OWN row's D BEFORE calling calcJacTVecProduct exactly cancels the
row scaling: seed_i = sign_i / D_i. This script reuses the 43 indices whose
D_i is already independently confirmed (hardcoded below, copied verbatim from
diagratio_out.log) as w_R's support -- sparse in row-index, but spanning 4
different variable types and dozens of physically different cells
simultaneously, and dense dW still exercises coupling into and out of all of
them.

Three independent random dW directions (coordinator's request: one unlucky
vector should not be able to hide a defect in a subspace it doesn't excite).
Also prints the UNCORRECTED comparison (w_R without the 1/D_i scaling) at the
same seeds, to show the correction is doing real work, not just picked to
force an answer.
"""
import os
import time
import numpy as np
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP
from pygeo import geo_utils
from mpi4py import MPI

comm = MPI.COMM_WORLD
assert comm.size == 1, "serial, matching probeA5DiagRatio.py"

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
        "TP1": {"type": "totalPressure", "source": "patchToFace", "patches": ["inlet"], "scale": 1.0, "addToAdjoint": True},
        "TP2": {"type": "totalPressure", "source": "patchToFace", "patches": ["outlet"], "scale": 1.0, "addToAdjoint": True},
        "HFX": {"type": "wallHeatFlux", "source": "patchToFace", "patches": ["ubend"], "scale": 1.0, "addToAdjoint": False},
    },
    "adjStateOrdering": "cell",
    "adjEqnOption": {"gmresRelTol": 1e-5, "gmresTolDiff": 1e4, "pcFillLevel": 2,
                      "jacMatReOrdering": "natural", "gmresMaxIters": 3000, "gmresRestart": 3000},
    "normalizeStates": {"U": U0, "p": (U0 * U0) / 2.0, "nuTilda": 1e-3, "phi": 1.0, "T": 300},
    "inputInfo": {"aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]}},
    "outputInfo": {"q_convect": {"type": "thermalCouplingOutput", "patches": ["ubend"], "components": ["thermalCoupling"]}},
}
meshOptions = {"gridFile": os.getcwd(), "fileType": "OpenFOAM", "symmetryPlanes": []}


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
        indexList = []
        indexList.extend(pts[7:16, 1, :].flatten())
        PS = geo_utils.PointSelect("list", indexList)
        shapexUpper = self.geometry_aero.nom_addLocalDV(dvName="shapexUpper", pointSelect=PS, axis="x")
        self.dvs.add_output("shapexUpper", val=np.array([0.0] * shapexUpper))
        self.connect("shapexUpper", "geometry_aero.shapexUpper")
        self.add_design_var("shapexUpper", lower=-0.04, upper=0.04, scaler=25.0)
        self.connect("scenario.aero_post.TP1", "OBJ.TP1")
        self.connect("scenario.aero_post.TP2", "OBJ.TP2")
        self.add_objective("OBJ.val", scaler=1.0)


t0 = time.time()
prob = om.Problem(reports=None)
prob.model = Top()
prob.setup(mode="rev")
print("MATVEC === running real primal (serial) ===", flush=True)
prob.run_model()
print("MATVEC === primal done, t=%.1fs ===" % (time.time() - t0), flush=True)

DASolver = prob.model.dafoam_builder.DASolver
discipline = DASolver.getOption("discipline")
stateName = "%s_states" % discipline
residualName = "%s_residuals" % discipline

W0 = DASolver.getStates().copy()
nW = W0.size
DASolver.setStates(W0)

# (index, D_i) pairs, copied verbatim from diagratio_out.log's 43 clean
# (non-phi-like) diagonal samples -- see probeA5DiagRatio.py's own log.
KNOWN_D = {
    560: 300.0, 1373: 35.28, 2490: 8.4, 3674: 0.001, 4045: 8.4, 4870: 0.001,
    5529: 35.28, 5818: 0.001, 9601: 8.4, 10568: 35.28, 10610: 8.4, 12651: 0.001,
    17020: 8.4, 17088: 8.4, 17492: 8.4, 17648: 8.4, 18441: 8.4, 19223: 8.4,
    19880: 35.28, 20436: 35.28, 20739: 0.001, 21543: 8.4, 23607: 8.4,
    23934: 8.4, 27697: 35.28, 28522: 8.4, 30600: 35.28, 30843: 8.4,
    32502: 8.4, 32659: 35.28, 34587: 8.4, 35193: 35.28, 36749: 300.0,
    37396: 8.4, 38303: 8.4, 39976: 8.4, 41018: 0.001, 41199: 0.001,
    41408: 300.0, 41590: 300.0, 42274: 8.4, 43974: 8.4, 44215: 8.4,
}
assert all(0 <= i < nW for i in KNOWN_D)
print("MATVEC nW=%d nKnownD=%d (types: U=%d p=%d nuTilda=%d T=%d)" % (
    nW, len(KNOWN_D),
    sum(1 for v in KNOWN_D.values() if abs(v - 8.4) < 1e-6),
    sum(1 for v in KNOWN_D.values() if abs(v - 35.28) < 1e-6),
    sum(1 for v in KNOWN_D.values() if abs(v - 0.001) < 1e-6),
    sum(1 for v in KNOWN_D.values() if abs(v - 300.0) < 1e-6),
), flush=True)

idxArr = np.array(sorted(KNOWN_D.keys()))
Darr = np.array([KNOWN_D[i] for i in idxArr])

h = 1e-4
for seedNum in [2026, 42, 777]:
    np.random.seed(seedNum)
    r = np.random.uniform(-1.0, 1.0, size=nW)
    dW = W0 * r  # dense, relative-magnitude, spans every state DOF

    np.random.seed(seedNum + 500)
    signs = np.random.choice([-1.0, 1.0], size=len(idxArr))

    w_R_corrected = np.zeros(nW)
    w_R_corrected[idxArr] = signs / Darr  # pre-divide by each row's own D_i

    w_R_uncorrected = np.zeros(nW)
    w_R_uncorrected[idxArr] = signs  # same support, no units fix -- contrast

    Wp = W0 + h * dW
    Wm = W0 - h * dW
    DASolver.setStates(Wp)
    Rp = DASolver.getResiduals().copy()
    DASolver.setStates(Wm)
    Rm = DASolver.getResiduals().copy()
    DASolver.setStates(W0)
    FD_dR = (Rp - Rm) / (2.0 * h)

    FD_scalar_corr = float(np.dot(w_R_corrected, FD_dR))
    FD_scalar_uncorr = float(np.dot(w_R_uncorrected, FD_dR))

    product_corr = np.zeros(nW)
    DASolver.solverAD.calcJacTVecProduct(stateName, "stateVar", W0, residualName, "residual", w_R_corrected, product_corr)
    AN_scalar_corr = float(np.dot(dW, product_corr))

    product_uncorr = np.zeros(nW)
    DASolver.solverAD.calcJacTVecProduct(stateName, "stateVar", W0, residualName, "residual", w_R_uncorrected, product_uncorr)
    AN_scalar_uncorr = float(np.dot(dW, product_uncorr))

    for label, FD_s, AN_s in [("CORRECTED", FD_scalar_corr, AN_scalar_corr),
                               ("uncorrected", FD_scalar_uncorr, AN_scalar_uncorr)]:
        absdiff = FD_s - AN_s
        relerr = abs(absdiff) / (abs(FD_s) + 1e-300)
        sign = "agree" if (FD_s * AN_s) > 0 else "FLIPPED"
        print("MATVEC_RESULT seed=%d variant=%s FD=%.8e AN=%.8e rel_err=%.6e sign=%s" % (
            seedNum, label, FD_s, AN_s, relerr, sign), flush=True)

print("MATVEC_DONE t=%.1fs" % (time.time() - t0), flush=True)
