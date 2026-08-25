#!/usr/bin/env python
"""
CURRICULUM D10 CAPABILITY PROBE -- thermal-objective reachability on the installed
DAFoam image.  Frozen instrument; do not edit after the pre-registration commit.

What it does: builds a 720-cell 2D heated channel (DASimpleFoam, SpalartAllmaras,
T solved as an adjoint state per DAResidualSimpleFoam.C:221-235), declares a
`wallHeatFlux` function on the heated lower wall with addToAdjoint True, runs the
primal, and -- for task compute_totals -- the adjoint for d(HFX)/d(patchV).

Every graded quantity is written to disk as JSON.  Nothing is graded from stdout.
"""
import argparse, json, os, sys
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic

parser = argparse.ArgumentParser()
parser.add_argument("-task", type=str, default="compute_totals")
parser.add_argument("-out", type=str, default="d10_probe_out.json")
args = parser.parse_args()

U0 = 10.0
p0 = 0.0
nuTilda0 = 4.5e-5
aoa0 = 0.0
T0 = 293.15

daOptions = {
    "designSurfaces": ["lowerWall"],
    "solverName": "DASimpleFoam",
    "primalMinResTol": 1.0e-8,
    "primalMinResTolDiff": 1.0e4,
    "printInterval": 200,
    "wallDistanceMethod": "daCustom",
    "primalBC": {
        "U0": {"variable": "U", "patches": ["inlet"], "value": [U0, 0.0, 0.0]},
        "p0": {"variable": "p", "patches": ["outlet"], "value": [p0]},
        "nuTilda0": {"variable": "nuTilda", "patches": ["inlet"], "value": [nuTilda0]},
        "useWallFunction": True,
    },
    # THE CAPABILITY UNDER PROBE: a thermal objective, in the adjoint.
    "function": {
        "HFX": {
            "type": "wallHeatFlux",
            "source": "patchToFace",
            "patches": ["lowerWall"],
            "scale": 1.0,
            "addToAdjoint": True,
        },
        "TPIn": {
            "type": "totalPressure",
            "source": "patchToFace",
            "patches": ["inlet"],
            "scale": 1.0 / (0.5 * U0 * U0),
            "addToAdjoint": True,
        },
    },
    "adjEqnOption": {
        "gmresRelTol": 1.0e-6,
        "gmresMaxIters": 2000,
        "gmresRestart": 2000,
        "pcFillLevel": 1,
        "jacMatReOrdering": "rcm",
    },
    "normalizeStates": {
        "U": U0,
        "p": U0 * U0 / 2.0,
        "nuTilda": nuTilda0 * 10.0,
        "phi": 1.0,
        "T": T0,
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


class Top(Multipoint):
    def setup(self):
        builder = DAFoamBuilder(options=daOptions, mesh_options=None, scenario="aerodynamic")
        builder.initialize(self.comm)
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])
        self.mphys_add_scenario("scenario1", ScenarioAerodynamic(aero_builder=builder))

    def configure(self):
        self.dvs.add_output("patchV", val=np.array([U0, aoa0]))
        self.connect("patchV", "scenario1.patchV")
        self.add_design_var("patchV", lower=[1.0, -5.0], upper=[50.0, 5.0], scaler=1.0)
        self.add_objective("scenario1.aero_post.HFX", scaler=1.0)


prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")

rec = {"task": args.task, "status": "STARTED"}
prob.run_model()
rec["HFX"] = float(np.atleast_1d(prob.get_val("scenario1.aero_post.HFX"))[0])
rec["TPIn"] = float(np.atleast_1d(prob.get_val("scenario1.aero_post.TPIn"))[0])
rec["patchV"] = [float(v) for v in np.atleast_1d(prob.get_val("patchV"))]

if args.task == "compute_totals":
    totals = prob.compute_totals(of=["scenario1.aero_post.HFX"], wrt=["patchV"])
    key = ("scenario1.aero_post.HFX", "patchV")
    d = np.atleast_1d(np.array(totals[key]).ravel())
    rec["dHFX_dpatchV"] = [float(v) for v in d]

rec["status"] = "COMPLETE"
if MPI.COMM_WORLD.rank == 0:
    with open(args.out, "w") as f:
        json.dump(rec, f, indent=2, sort_keys=True)
    print("D10_PROBE_JSON_WRITTEN: " + os.path.abspath(args.out))
