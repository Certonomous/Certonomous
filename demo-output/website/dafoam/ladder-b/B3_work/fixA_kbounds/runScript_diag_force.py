#!/usr/bin/env python
"""
DIAGNOSTIC ONLY (not part of the field-inversion pilot): swap the custom
"variance" objective for a standard "force" objective (same type used
successfully in this lab's naca0012 case) on the SAME CBFS mesh/case/DVs, to
isolate whether the adjoint KSP divergence (PetscConvergedReason -9,
NaN/Inf, seen with the variance objective) is caused by something specific
to the variance-function setup, or is a general property of this mesh/case
in DAFoam's adjoint framework regardless of objective. Everything else
(mesh, BCs, design variable, primalMinResTol, adjEqnOption) is identical to
runScript.py.
"""
import os
import argparse
import time
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic

parser = argparse.ArgumentParser()
parser.add_argument("-task", type=str, default="compute_totals")
args = parser.parse_args()

U0 = 0.72
k0 = 0.0042
omega0 = 1000.0

daOptions = {
    "designSurfaces": ["bottomWall", "topWall"],
    "solverName": "DASimpleFoam",
    "primalMinResTol": 1.0e-6,
    "primalBC": {},
    "function": {
        "CD": {
            "type": "force",
            "source": "patchToFace",
            "patches": ["bottomWall", "topWall"],
            "directionMode": "parallelToFlow",
            "patchVelocityInputName": "patchV",
            "scale": 1.0 / (0.5 * U0 * U0 * 1.0),
        },
    },
    # pcFillLevel bumped 1 -> 4: diagnosing a KSP DIVERGED_NANORINF (PETSc
    # reason -9) at iteration 0 seen with pcFillLevel=1 on this mesh,
    # reproduced with BOTH the variance objective and this plain force
    # objective (rules out the custom objective as the cause) -- classic
    # symptom of an ILU(1) zero-pivot on a stiff SST Jacobian (U~1, p~1,
    # k~1e-3, omega~1e3 magnitude spread). Deeper fill level is the
    # standard PETSc remedy.
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 4, "jacMatReOrdering": "rcm"},
    "normalizeStates": {
        "U": U0,
        "p": U0 * U0 / 2.0,
        "k": k0,
        "omega": omega0,
        "phi": 1.0,
        "nut": 1e-4,
    },
    "inputInfo": {
        "patchV": {
            "type": "patchVelocity",
            "patches": ["inlet"],
            "flowAxis": "x",
            "normalAxis": "y",
            "components": ["solver", "function"],
        },
    },
}

meshOptions = {
    "gridFile": os.getcwd(),
    "fileType": "OpenFOAM",
    "symmetryPlanes": [[[0.0, 0.0, -0.1], [0.0, 0.0, 1.0]], [[0.0, 0.0, 0.1], [0.0, 0.0, 1.0]]],
}


class Top(Multipoint):
    def setup(self):
        dafoam_builder = DAFoamBuilder(daOptions, meshOptions, scenario="aerodynamic")
        dafoam_builder.initialize(self.comm)
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])
        self.add_subsystem("mesh", dafoam_builder.get_mesh_coordinate_subsystem())
        self.mphys_add_scenario("scenario1", ScenarioAerodynamic(aero_builder=dafoam_builder))
        self.connect("mesh.x_aero0", "scenario1.x_aero")

    def configure(self):
        self.dvs.add_output("patchV", val=np.array([U0, 0.0]))
        self.connect("patchV", "scenario1.patchV")
        self.add_design_var("patchV", lower=[0.1, -10.0], upper=[2.0, 10.0], scaler=1.0)
        self.add_objective("scenario1.aero_post.CD", scaler=1.0)


prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")
rank = MPI.COMM_WORLD.rank

if args.task == "compute_totals":
    t0 = time.time()
    prob.run_model()
    t1 = time.time()
    totals = prob.compute_totals()
    t2 = time.time()
    if rank == 0:
        print("TIMING primal_wall_s:", t1 - t0)
        print("TIMING adjoint_wall_s:", t2 - t1)
        print("CD objective:", prob.get_val("scenario1.aero_post.CD"))
        print("totals:", totals)
