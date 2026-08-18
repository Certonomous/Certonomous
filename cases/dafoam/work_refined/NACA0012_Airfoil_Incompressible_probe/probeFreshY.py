#!/usr/bin/env python
"""
Fresh-process probe: evaluate CD and the internal 'yWall' field at ONE shape
point, in a brand-new process (so meshWaveFrozen's isComputed_ latch has
never fired before -- its one-and-only correct() call is tied to whatever
shape is set before the FIRST run_model() call in this process, unlike
checkAll8Refined.py, which reuses one persistent process/mesh object across
baseline + all FD perturbations, freezing yWall at the baseline (shape=0)
geometry for every subsequent evaluation).

Usage: python probeFreshY.py --idx N --step H
  idx  : shape DV component to perturb (0-7), or -1 for baseline (shape=0)
  step : signed perturbation (e.g. 1e-4 or -1e-4); ignored if idx=-1

Identical daOptions/meshOptions/Top class to checkAll8Refined.py (same case,
same mesh, same primalMinResTol=1e-11), run from a copy of the refined case
(NACA0012_Airfoil_Incompressible_probe) sharing the identical constant/system/
FFD/0.orig setup, so the mesh (14720 cells) and CD normalization are identical
to the established refined-mesh numbers in PROOF.md section 11.2.
"""
import os
import argparse
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP

parser = argparse.ArgumentParser()
parser.add_argument("--idx", type=int, required=True)
parser.add_argument("--step", type=float, default=0.0)
args = parser.parse_args()

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
    "primalMinResTol": 1.0e-11,
    "primalBC": {
        "U0": {"variable": "U", "patches": ["inout"], "value": [U0, 0.0, 0.0]},
        "p0": {"variable": "p", "patches": ["inout"], "value": [p0]},
        "nuTilda0": {"variable": "nuTilda", "patches": ["inout"], "value": [nuTilda0]},
        "useWallFunction": True,
    },
    "function": {
        "CD": {"type": "force", "source": "patchToFace", "patches": ["wing"],
               "directionMode": "parallelToFlow", "patchVelocityInputName": "patchV",
               "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0)},
        "CL": {"type": "force", "source": "patchToFace", "patches": ["wing"],
               "directionMode": "normalToFlow", "patchVelocityInputName": "patchV",
               "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0)},
    },
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 1, "jacMatReOrdering": "rcm"},
    "normalizeStates": {"U": U0, "p": U0 * U0 / 2.0, "nuTilda": nuTilda0 * 10.0, "phi": 1.0},
    "inputInfo": {
        "aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]},
        "patchV": {"type": "patchVelocity", "patches": ["inout"], "flowAxis": "x",
                   "normalAxis": "y", "components": ["solver", "function"]},
    },
}

meshOptions = {
    "gridFile": os.getcwd(),
    "fileType": "OpenFOAM",
    "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]], [[0.0, 0.0, 0.1], [0.0, 0.0, 1.0]]],
}


class Top(Multipoint):
    def setup(self):
        dafoam_builder = DAFoamBuilder(daOptions, meshOptions, scenario="aerodynamic")
        dafoam_builder.initialize(self.comm)
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

        leList = [[1e-4, 0.0, 1e-4], [1e-4, 0.0, 0.1 - 1e-4]]
        teList = [[0.998 - 1e-4, 0.0, 1e-4], [0.998 - 1e-4, 0.0, 0.1 - 1e-4]]
        self.geometry.nom_addThicknessConstraints2D("thickcon", leList, teList, nSpan=2, nChord=10)
        self.geometry.nom_addVolumeConstraint("volcon", leList, teList, nSpan=2, nChord=10)
        self.geometry.nom_addLERadiusConstraints("rcon", leList, 2, [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0])

        self.dvs.add_output("shape", val=np.array([0] * len(shapes)))
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


prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")

rank = MPI.COMM_WORLD.rank
nShape = 8
shapeVec = np.zeros(nShape)
if args.idx >= 0:
    shapeVec[args.idx] = args.step

# THIS is the key difference vs checkAll8Refined.py: shape is set to its
# FINAL (possibly perturbed) value BEFORE the first-ever run_model() call in
# this brand-new process, so meshWaveFrozen's one-time correct() call (fired
# during this first solve) computes yWall tied to THIS shape, not shape=0.
prob.set_val("dvs.shape", shapeVec)
prob.set_val("dvs.patchV", np.array([U0, aoa0]))
prob.run_model()
cd = float(prob.get_val("scenario1.aero_post.CD")[0])

DASolver = prob.model.scenario1.aero_post.functionals.DASolver
nCells = DASolver.solver.getNLocalCells()
yWall = np.zeros(nCells)
DASolver.solver.getOFField("yWall", "scalar", yWall)

# cross-validation: p should clearly vary with shape (CD is derived from it);
# if getOFField were returning a stale/cached snapshot regardless of solver
# state, p would ALSO look frozen -- this distinguishes "yWall is genuinely
# frozen" from "getOFField itself is broken/cached".
pField = np.zeros(nCells)
DASolver.solver.getOFField("p", "scalar", pField)
pMean = float(np.mean(pField))
pMin = float(np.min(pField))
pMax = float(np.max(pField))

localMin = float(np.min(yWall))
localMax = float(np.max(yWall))
localMean = float(np.mean(yWall))
localSum = float(np.sum(yWall))
localSumSq = float(np.sum(yWall ** 2))
localN = int(nCells)

# gather to rank 0 for a global summary (sum/sumSq/N -> global mean, and
# global min/max via MPI reduce)
comm = MPI.COMM_WORLD
gMin = comm.reduce(localMin, op=MPI.MIN, root=0)
gMax = comm.reduce(localMax, op=MPI.MAX, root=0)
gSum = comm.reduce(localSum, op=MPI.SUM, root=0)
gSumSq = comm.reduce(localSumSq, op=MPI.SUM, root=0)
gN = comm.reduce(localN, op=MPI.SUM, root=0)
gPMean = comm.reduce(pMean * nCells, op=MPI.SUM, root=0)
gPMin = comm.reduce(pMin, op=MPI.MIN, root=0)
gPMax = comm.reduce(pMax, op=MPI.MAX, root=0)

print(
    "PROBE rank=%d idx=%d step=%.6e CD=%.15e nCells=%d yWall_min=%.10e yWall_max=%.10e yWall_mean=%.10e p_mean=%.10e"
    % (rank, args.idx, args.step, cd, nCells, localMin, localMax, localMean, pMean),
    flush=True,
)

if rank == 0:
    gMean = gSum / gN
    gPMeanFinal = gPMean / gN
    print(
        "PROBE_GLOBAL idx=%d step=%.6e CD=%.15e nCellsGlobal=%d yWall_min=%.10e yWall_max=%.10e yWall_mean=%.10e p_min=%.10e p_max=%.10e p_mean=%.10e"
        % (args.idx, args.step, cd, gN, gMin, gMax, gMean, gPMin, gPMax, gPMeanFinal),
        flush=True,
    )
    print("PROBE DONE", flush=True)
