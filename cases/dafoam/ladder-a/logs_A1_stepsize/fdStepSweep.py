#!/usr/bin/env python
"""
A1 finite-difference step-size sweep (Ladder A priority probe).

Reuses the EXACT Top class / daOptions / meshOptions from runScript.py (the
actual A1 baseline run in this directory: primalMinResTol=1e-8, same FFD,
same 8 shape design variables, same flow conditions). Only variable changed
across invocations: the central-difference step size, passed via -step.

For a single invocation:
  1. run_model() at shape=0 (baseline CD, recorded for a noise-floor check)
  2. compute_totals() for CD wrt shape only -> adjoint 8-vector (recomputed
     every invocation as a determinism cross-check against check_totals_run2.log)
  3. for idx in 0..7: central-difference CD at +step/-step on that one shape
     component, all others held at 0 (i.e. one row of the same central-diff
     Jacobian OpenMDAO's check_totals computes internally)
  4. prints the full 8-component FD vector and, in Python, the same
     rel-error metric OpenMDAO's check_totals reports:
        rel = norm(Jan - Jfd) / norm(Jfd)
  Nothing is skipped or approximated; every CD value printed is a real
  converged (or non-converged, reported honestly) DASimpleFoam solve.
"""

import os
import sys
import argparse
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder, OptFuncs
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP

parser = argparse.ArgumentParser()
parser.add_argument("-step", type=float, required=True)
args = parser.parse_args()
STEP = args.step

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
baselineShape = np.zeros(nShape)

prob.set_val("dvs.shape", baselineShape)
prob.set_val("dvs.patchV", np.array([U0, aoa0]))
prob.run_model()
cd0 = float(prob.get_val("scenario1.aero_post.CD")[0])
if rank == 0:
    print("FDSWEEP step=%.1e BASELINE_CD=%.15e" % (STEP, cd0))

totals = prob.compute_totals(of=["scenario1.aero_post.CD"], wrt=["dvs.shape"])
adjointKey = [k for k in totals.keys() if k[1] == "dvs.shape"][0]
adjoint = np.array(totals[adjointKey]).flatten()
if rank == 0:
    for i in range(nShape):
        print("FDSWEEP step=%.1e ADJOINT idx=%d value=%.15e" % (STEP, i, adjoint[i]))

fd = np.zeros(nShape)
for idx in range(nShape):
    plus = baselineShape.copy()
    plus[idx] = STEP
    prob.set_val("dvs.shape", plus)
    prob.set_val("dvs.patchV", np.array([U0, aoa0]))
    prob.run_model()
    CDp = float(prob.get_val("scenario1.aero_post.CD")[0])

    minus = baselineShape.copy()
    minus[idx] = -STEP
    prob.set_val("dvs.shape", minus)
    prob.set_val("dvs.patchV", np.array([U0, aoa0]))
    prob.run_model()
    CDm = float(prob.get_val("scenario1.aero_post.CD")[0])

    fd[idx] = (CDp - CDm) / (2.0 * STEP)
    if rank == 0:
        print(
            "FDSWEEP step=%.1e FD idx=%d CD_plus=%.15e CD_minus=%.15e fd=%.15e"
            % (STEP, idx, CDp, CDm, fd[idx])
        )

if rank == 0:
    anMag = np.linalg.norm(adjoint)
    fdMag = np.linalg.norm(fd)
    absErr = np.linalg.norm(adjoint - fd)
    relErr = absErr / fdMag if fdMag != 0 else float("nan")
    print("FDSWEEP step=%.1e SUMMARY an_mag=%.15e fd_mag=%.15e abs_err=%.15e rel_err=%.15e rel_err_pct=%.6f" %
          (STEP, anMag, fdMag, absErr, relErr, relErr * 100.0))
    print("FDSWEEP step=%.1e DONE" % STEP)
