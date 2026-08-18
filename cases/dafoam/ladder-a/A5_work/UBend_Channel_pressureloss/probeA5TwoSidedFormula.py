#!/usr/bin/env python
"""
Test the two candidate off-diagonal correction formulas for A5's dR/dW against
DIRECT, independently-measured (row, col) pairs where BOTH indices' D_i are
determined by the SAME reliable diagonal method (not a magnitude heuristic).

  max-of-the-two:  corrected = raw_AN[row,col] / max(D_row, D_col)
  ratio (row/col):  corrected = raw_AN[row,col] / D_row * D_col

Method per pair: pick row i and col j, both drawn from a broadened
KNOWN_D set (measured via the same self-derivative diagonal trick used in
probeA5DiagRatio.py: AN_ii/FD_ii). Get raw_AN[i,j] via ONE
calcJacTVecProduct(seed=e_i) call, reading component j of the result. Get
FD[i,j] directly via perturbing state j alone and reading residual i back
(no aggregation). Apply both candidate corrections and compare to FD[i,j].

Then, using whichever formula collapses every tested pair to ~1.0, redo the
matvec test with BOTH w_R and dW restricted to the (now dual-sided-correctable)
KNOWN_D support -- a genuine multi-row-by-multi-column coupling test, properly
corrected on both sides, not just the row side as in probeA5MatvecDrDW.py.
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
assert comm.size == 1

U0 = 8.4
daOptionsAero = {
    "solverName": "DASimpleFoam", "designSurfaces": ["ubend"], "useAD": {"mode": "reverse"},
    "primalMinResTol": 1e-8, "primalMinResTolDiff": 1e7, "writeMinorIterations": True,
    "wallDistanceMethod": "daCustom", "primalBC": {"useWallFunction": True},
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
        points_aero = self.mesh_aero.mphys_get_surface_mesh()
        self.geometry_aero.nom_add_discipline_coords("aero", points_aero)
        pts = self.geometry_aero.nom_getDVGeo().getLocalIndex(0)
        indexList = []
        indexList.extend(pts[7:16, 1, :].flatten())
        PS = geo_utils.PointSelect("list", indexList)
        n = self.geometry_aero.nom_addLocalDV(dvName="shapexUpper", pointSelect=PS, axis="x")
        self.dvs.add_output("shapexUpper", val=np.array([0.0] * n))
        self.connect("shapexUpper", "geometry_aero.shapexUpper")
        self.add_design_var("shapexUpper", lower=-0.04, upper=0.04, scaler=25.0)
        self.connect("scenario.aero_post.TP1", "OBJ.TP1")
        self.connect("scenario.aero_post.TP2", "OBJ.TP2")
        self.add_objective("OBJ.val", scaler=1.0)


t0 = time.time()
prob = om.Problem(reports=None)
prob.model = Top()
prob.setup(mode="rev")
prob.run_model()
print("TWOSIDED === primal done t=%.1fs ===" % (time.time() - t0), flush=True)

DASolver = prob.model.dafoam_builder.DASolver
stateName = "%s_states" % DASolver.getOption("discipline")
residualName = "%s_residuals" % DASolver.getOption("discipline")
W0 = DASolver.getStates().copy()
nW = W0.size
DASolver.setStates(W0)

# 43 diagonal-confirmed indices from probeA5DiagRatio.py, verbatim
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


def get_full_row(rowIdx):
    seed = np.zeros(nW)
    seed[rowIdx] = 1.0
    row = np.zeros(nW)
    DASolver.solverAD.calcJacTVecProduct(stateName, "stateVar", W0, residualName, "residual", seed, row)
    return row


def fd_entry(rowIdx, colIdx):
    hj = 1e-4 * max(abs(W0[colIdx]), 1e-8)
    Wp = W0.copy()
    Wp[colIdx] += hj
    DASolver.setStates(Wp)
    Rp = float(DASolver.getResiduals()[rowIdx])
    Wm = W0.copy()
    Wm[colIdx] -= hj
    DASolver.setStates(Wm)
    Rm = float(DASolver.getResiduals()[rowIdx])
    DASolver.setStates(W0)
    return (Rp - Rm) / (2.0 * hj)


def measure_D_at(idx):
    """Diagonal self-derivative D_idx = AN_ii/FD_ii, same method as
    probeA5DiagRatio.py, applied fresh to a SPECIFIC index (not assumed from
    a magnitude heuristic)."""
    seed = np.zeros(nW)
    seed[idx] = 1.0
    prod = np.zeros(nW)
    DASolver.solverAD.calcJacTVecProduct(stateName, "stateVar", W0, residualName, "residual", seed, prod)
    AN_ii = float(prod[idx])
    FD_ii = fd_entry(idx, idx)
    if abs(FD_ii) < 1e-300:
        return None
    return AN_ii / FD_ii


# pick one representative row per variable type (known D_row from the
# original diagonal sample). For EACH row, find its ACTUAL largest-magnitude
# off-diagonal entries (guaranteed real, nonzero coupling -- picking
# arbitrary far-away indices, tried first, gave all-zero entries: most cell
# pairs in a sparse discretization simply don't couple directly). Then
# MEASURE D_col at each of those specific columns directly (not reused from
# the original 43, which mostly don't overlap a given row's actual
# neighbors) -- this is the fix for the all-zero result above.
byType = {}
for idx, d in KNOWN_D.items():
    byType.setdefault(d, []).append(idx)
print("TWOSIDED byType counts: %s" % {k: len(v) for k, v in byType.items()}, flush=True)

testRows = [byType[8.4][0], byType[35.28][0], byType[0.001][0], byType[300.0][0]]

results = []
for rowIdx in testRows:
    D_row = KNOWN_D[rowIdx]
    fullRow = get_full_row(rowIdx)
    absRow = np.abs(fullRow).copy()
    absRow[rowIdx] = 0.0
    topCols = np.argsort(absRow)[::-1][:4]
    for colIdx in topCols:
        colIdx = int(colIdx)
        D_col = measure_D_at(colIdx)
        if D_col is None:
            print("TWOSIDED_SKIP row=%d col=%d -- FD_ii is zero, cannot measure D_col" % (rowIdx, colIdx), flush=True)
            continue
        raw_AN = float(fullRow[colIdx])
        FD = fd_entry(rowIdx, colIdx)
        corrected_max = raw_AN / max(D_row, D_col)
        corrected_ratio = raw_AN / D_row * D_col
        ratio_max = corrected_max / FD if abs(FD) > 1e-300 else float("nan")
        ratio_ratio = corrected_ratio / FD if abs(FD) > 1e-300 else float("nan")
        print(
            "TWOSIDED_PAIR row=%d(D=%.3f) col=%d(D_col_measured=%.6f) raw_AN=%.6e FD=%.6e "
            "max_corrected/FD=%.6f ratio_corrected/FD=%.6f"
            % (rowIdx, D_row, colIdx, D_col, raw_AN, FD, ratio_max, ratio_ratio),
            flush=True,
        )
        results.append((rowIdx, D_row, colIdx, D_col, raw_AN, FD, ratio_max, ratio_ratio))

maxDevs = [abs(r[6] - 1.0) for r in results if np.isfinite(r[6])]
ratioDevs = [abs(r[7] - 1.0) for r in results if np.isfinite(r[7])]
print("TWOSIDED_SUMMARY n=%d max_formula_meanAbsDevFrom1=%.6f ratio_formula_meanAbsDevFrom1=%.6f" % (
    len(results), float(np.mean(maxDevs)), float(np.mean(ratioDevs))), flush=True)
print("TWOSIDED_DONE t=%.1fs" % (time.time() - t0), flush=True)
