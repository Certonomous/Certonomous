#!/usr/bin/env python
"""
CURRICULUM D10-F' FD PAIR -- the finite-difference table for the D10-P' adjoint
gradient d(HFX)/d(patchV).  Frozen instrument; do not edit after the pre-registration
commit.

DERIVED BY EXPLICIT SUBSTITUTION from d10p_run_script.py (md5 1d04151dba68061fce2c34b35f9fcb4e).
EXACTLY THREE deltas, all listed in the pre-registration and all reproduced by the
generator in that document:
  (a) this header;
  (b) a `-patchV0` argument, POSITIVE-ONLY by construction so argparse can never read
      it as an option flag (the D11-O' waste class);
  (c) `val=np.array([U0, aoa0])` becomes `val=np.array([args.patchV0, aoa0])`.
Nothing else moves.  In particular daOptions is byte-identical, so `normalizeStates["U"]`
stays pinned at the LITERAL 10.0 across every FD step -- a normalisation that moved with
the step would make the difference quotient measure the normalisation as well as the flow.

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
parser.add_argument("-patchV0", type=float, default=10.0,
                    help="value of patchV[0] (inlet speed, m/s).  ALWAYS POSITIVE.")
args = parser.parse_args()
if args.patchV0 <= 0.0:
    sys.exit("REFUSE: patchV0 must be positive; got %r" % (args.patchV0,))

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
        self.dvs.add_output("patchV", val=np.array([args.patchV0, aoa0]))
        self.connect("patchV", "scenario1.patchV")
        self.add_design_var("patchV", lower=[1.0, -5.0], upper=[50.0, 5.0], scaler=1.0)
        self.add_objective("scenario1.aero_post.HFX", scaler=1.0)


prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")

rec = {"task": args.task, "patchV0_arg": args.patchV0, "status": "STARTED"}
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
