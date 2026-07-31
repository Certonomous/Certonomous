#!/usr/bin/env python
"""
Coordinator's mechanism test for A5. dF/dW showed dTP1/dW off by exactly
35.28x (=p0) and dTP2/dW off by exactly 8.4x (=U0), direction-independent,
both seeds/steps identical. A5's objective is OBJ.val = TP1 - TP2 -- a
DIFFERENCE of two differently-mis-scaled terms. A uniform scaling on a single
objective divides out; on a difference of two terms scaled by DIFFERENT
constants it does not -- the composite becomes 35.28*dTP1 - 8.4*dTP2 where it
should be a single constant times (dTP1 - dTP2), a genuine change in the
RELATIVE WEIGHT between the two contributions, not just an overall magnitude
error. That would produce exactly A5's symptom: most components roughly
right, large aggregate error, sign flips specifically where the two
mis-weighted terms are close in magnitude and opposite in sign.

THE TEST: get the REAL adjoint's dTP1/dshapexUpper and dTP2/dshapexUpper
SEPARATELY (one compute_totals call with of=[TP1, TP2] does two independent
reverse solves -- valid because the combined OBJ adjoint psi_combined =
psi_TP1 - psi_TP2 exactly, by linearity of the discrete adjoint equation; this
is not an approximation). Correct each by its own measured factor
(dTP1/35.28, dTP2/8.4), recompose corrected_OBJ = corrected_dTP1 -
corrected_dTP2, and compare EVERY component (not just idx8/idx17) against the
already-established real check_totals FD table (A5_ubend_internal.md's
per-component breakdown, step=1e-4) -- the full 27-component comparison, so a
correction that happens to fix idx8/idx17 while breaking the previously-clean
components is caught, not hidden.

Real, unmodified case setup (byte-identical daOptionsAero/meshOptions/DV
construction to runScript.py) so the comparison against the established FD
table is apples-to-apples.
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

U0 = 8.4
CPL_weight = 0.5
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
        shapexUpper = self.geometry_aero.nom_addLocalDV(dvName="shapexUpper", pointSelect=PS, axis="x")

        indexList = []
        indexList.extend(pts[7:16, 1, :].flatten())
        PS = geo_utils.PointSelect("list", indexList)
        shapeyUpper = self.geometry_aero.nom_addLocalDV(dvName="shapeyUpper", pointSelect=PS, axis="y")
        indexList = []
        indexList.extend(pts[7:16, 1, :].flatten())
        PS = geo_utils.PointSelect("list", indexList)
        shapezUpper = self.geometry_aero.nom_addLocalDV(dvName="shapezUpper", pointSelect=PS, axis="z")
        indexList = []
        indexList.extend(pts[7:16, 0, :].flatten())
        PS = geo_utils.PointSelect("list", indexList)
        shapexLower = self.geometry_aero.nom_addLocalDV(dvName="shapexLower", pointSelect=PS, axis="x")
        indexList = []
        indexList.extend(pts[7:16, 0, :].flatten())
        PS = geo_utils.PointSelect("list", indexList)
        shapeyLower = self.geometry_aero.nom_addLocalDV(dvName="shapeyLower", pointSelect=PS, axis="y")
        indexList = []
        indexList.extend(pts[7:16, 0, :].flatten())
        PS = geo_utils.PointSelect("list", indexList)
        shapezLower = self.geometry_aero.nom_addLocalDV(dvName="shapezLower", pointSelect=PS, axis="z")

        self.dvs.add_output("shapexUpper", val=np.array([0.0] * shapexUpper))
        self.dvs.add_output("shapeyUpper", val=np.array([0.0] * shapeyUpper))
        self.dvs.add_output("shapezUpper", val=np.array([0.0] * shapezUpper))
        self.dvs.add_output("shapexLower", val=np.array([0.0] * shapexLower))
        self.dvs.add_output("shapeyLower", val=np.array([0.0] * shapeyLower))
        self.dvs.add_output("shapezLower", val=np.array([0.0] * shapezLower))
        self.connect("shapexUpper", "geometry_aero.shapexUpper")
        self.connect("shapeyUpper", "geometry_aero.shapeyUpper")
        self.connect("shapezUpper", "geometry_aero.shapezUpper")
        self.connect("shapexLower", "geometry_aero.shapexLower")
        self.connect("shapeyLower", "geometry_aero.shapeyLower")
        self.connect("shapezLower", "geometry_aero.shapezLower")

        self.add_design_var("shapexUpper", lower=-0.04, upper=0.04, scaler=25.0)
        self.add_design_var("shapeyUpper", lower=-0.04, upper=0.04, scaler=25.0)
        self.add_design_var("shapezUpper", lower=-0.04, upper=0.04, scaler=25.0)
        self.add_design_var("shapexLower", lower=-0.04, upper=0.04, scaler=25.0)
        self.add_design_var("shapeyLower", lower=-0.04, upper=0.04, scaler=25.0)
        self.add_design_var("shapezLower", lower=-0.04, upper=0.04, scaler=25.0)

        self.connect("scenario.aero_post.TP1", "OBJ.TP1")
        self.connect("scenario.aero_post.TP2", "OBJ.TP2")
        self.add_objective("OBJ.val", scaler=1.0)


t0 = time.time()
prob = om.Problem(reports=None)
prob.model = Top()
prob.setup(mode="rev")
prob.run_model()
if comm.rank == 0:
    print("CORRCOMP === primal done t=%.1fs ===" % (time.time() - t0), flush=True)
    print("CORRCOMP OBJ.val=%.10f TP1=%.10f TP2=%.10f" % (
        float(prob.get_val("OBJ.val")), float(prob.get_val("scenario.aero_post.TP1")),
        float(prob.get_val("scenario.aero_post.TP2"))), flush=True)

# ONE call, two separate reverse solves (of=[TP1, TP2] both requested) --
# gives the REAL adjoint's dTP1/dshapexUpper and dTP2/dshapexUpper directly,
# not a reconstruction.
totals = prob.compute_totals(
    of=["scenario.aero_post.TP1", "scenario.aero_post.TP2"],
    wrt=["shapexUpper"],
)
dTP1 = np.array(totals[("scenario.aero_post.TP1", "shapexUpper")]).flatten()
dTP2 = np.array(totals[("scenario.aero_post.TP2", "shapexUpper")]).flatten()

if comm.rank == 0:
    print("CORRCOMP === adjoint(s) done t=%.1fs ===" % (time.time() - t0), flush=True)
    print("CORRCOMP dTP1/dshapexUpper = %s" % np.array2string(dTP1, precision=6), flush=True)
    print("CORRCOMP dTP2/dshapexUpper = %s" % np.array2string(dTP2, precision=6), flush=True)

# sanity: dTP1 - dTP2 should equal the REAL OBJ.val adjoint (already on
# record from runScript.py's own compute_totals) to numerical precision --
# confirms psi_combined = psi_TP1 - psi_TP2 by linearity, not an assumption.
dOBJ_uncorrected = dTP1 - dTP2
established_dOBJ = np.array([
    0.23711358, -0.43555559, -0.41765751, 1.96883727, -0.10505221, -1.3953011,
    1.61077383, 0.90578111, -0.84337258, 7.81935558, 4.80044882, 3.90871135,
    -4.43512493, -0.91203487, 0.55598334, -13.86041673, -3.77483865, -0.62881205,
    -4.33825856, -0.94864214, 1.90894278, -1.78264732, -1.17260622, -2.25173312,
    -0.96908608, 0.74690602, -1.95653977,
])
if comm.rank == 0:
    diffFromEstablished = dOBJ_uncorrected - established_dOBJ
    print("CORRCOMP sanity: max|dTP1-dTP2 - established dOBJ| = %.6e (should be ~0, confirms linearity)" % (
        np.max(np.abs(diffFromEstablished))), flush=True)

# THE CORRECTION
dTP1_corrected = dTP1 / 35.28
dTP2_corrected = dTP2 / 8.4
dOBJ_corrected = dTP1_corrected - dTP2_corrected

# established real check_totals FD table (A5_ubend_internal.md, step=1e-4)
FD_established = np.array([
    0.11014, -0.46795, -0.41319, 0.70507, -0.43988, -1.21264, 1.36334, 1.32814,
    0.78391, 11.56848, 7.26987, 8.17581, -10.30518, -1.25570, 4.64655, -24.27272,
    -4.30296, 2.90530, -8.32702, -0.35517, 4.82274, -3.07833, -0.94309, -1.37502,
    -1.05939, 0.76429, -1.90572,
])

if comm.rank == 0:
    print("", flush=True)
    print("CORRCOMP_TABLE idx  uncorrected_AN  corrected_AN    FD(established)  uncorr_relerr%  corr_relerr%  uncorr_sign  corr_sign", flush=True)
    nSignFlipsUncorr = 0
    nSignFlipsCorr = 0
    sqErrUncorr = 0.0
    sqErrCorr = 0.0
    sqFD = 0.0
    for i in range(27):
        fd = FD_established[i]
        an_u = dOBJ_uncorrected[i]
        an_c = dOBJ_corrected[i]
        relerr_u = abs(an_u - fd) / (abs(fd) + 1e-300) * 100
        relerr_c = abs(an_c - fd) / (abs(fd) + 1e-300) * 100
        sign_u = "agree" if (an_u * fd) > 0 else "FLIP"
        sign_c = "agree" if (an_c * fd) > 0 else "FLIP"
        if sign_u == "FLIP":
            nSignFlipsUncorr += 1
        if sign_c == "FLIP":
            nSignFlipsCorr += 1
        sqErrUncorr += (an_u - fd) ** 2
        sqErrCorr += (an_c - fd) ** 2
        sqFD += fd ** 2
        flag = "  <== idx8/17" if i in (8, 17) else ""
        print("CORRCOMP_TABLE %3d  %13.6f  %13.6f  %13.6f  %13.2f  %13.2f  %6s  %6s%s" % (
            i, an_u, an_c, fd, relerr_u, relerr_c, sign_u, sign_c, flag), flush=True)

    aggUncorr = (sqErrUncorr ** 0.5) / (sqFD ** 0.5) * 100
    aggCorr = (sqErrCorr ** 0.5) / (sqFD ** 0.5) * 100
    print("", flush=True)
    print("CORRCOMP_SUMMARY signFlips_uncorrected=%d signFlips_corrected=%d aggRelErr_uncorrected=%.2f%% aggRelErr_corrected=%.2f%%" % (
        nSignFlipsUncorr, nSignFlipsCorr, aggUncorr, aggCorr), flush=True)

print("CORRCOMP_DONE t=%.1fs" % (time.time() - t0), flush=True)
