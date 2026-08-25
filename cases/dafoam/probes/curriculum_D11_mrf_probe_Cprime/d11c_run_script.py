#!/usr/bin/env python
"""
CURRICULUM D11-C' PROBE -- the COMPONENT-1 finite-difference STEP SWEEP.
Frozen instrument; do not edit after the pre-registration commit.

WHY THIS EXISTS.  D11-F' returned GATE REACHED on an adjoint-vs-FD agreement of
1.704895e-07, but its gate G11-5 set `adj = dP[0]` -- it compared COMPONENT 0 ONLY.
`dTPIn_dpatchV` has TWO components: [0] is d(TPIn)/d(inlet speed) in 1/(m/s), [1] is
d(TPIn)/d(angle of attack) in 1/deg.  Measured off disk from the D11-F' artifacts,
switching the MRF zone from omega=0 to omega=30 rad/s moves component 0 by 1.26e-04
relative and component 1 from 3.1484221063860114e-09 to -1.366011909783860e-04 --
four to five orders of magnitude.  THE COMPONENT MRF DOMINATES IS THE ONE THAT WAS
NEVER FD-CHECKED.  This instrument buys that check, and buys it as a STEP SWEEP
because DAFOAM_CHARTER.md section 3 requires the plateau to be read PER COMPONENT and
a step chosen for component 0 has no standing in component 1.

THE ONE FUNCTIONAL CHANGE from d11f_run_script.py: a second FD knob, `-aoaOffset`,
added to patchV[1].  `-uOffset` is unchanged and still adds to patchV[0].  Nothing
else -- not the case, not the mesh, not omega, not a single daOption -- differs.

Both offsets are passed in the `-flag=value` form.  D11-F' measured that argparse
reads a bare `-uOffset -1.0e-3` as an option flag, not a value, because argparse's
negative-number matcher accepts `-1` and `-0.001` but NOT exponent notation; that
defect cost three attempts and is not repeated here.

The process's measured CPU affinity is written into every JSON record, so container
placement is READ FROM THE PROCESS, never inferred from the flag the launcher passed.

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
parser.add_argument("-out", type=str, default="d11_probe_out.json")
parser.add_argument("-uOffset", type=float, default=0.0, help="FD offset added to patchV[0], m/s")
parser.add_argument("-aoaOffset", type=float, default=0.0, help="FD offset added to patchV[1], deg")
args = parser.parse_args()

U0 = 10.0
p0 = 0.0
nuTilda0 = 4.5e-5
aoa0 = 0.0

daOptions = {
    "designSurfaces": ["lowerWall"],
    "solverName": "DASimpleFoam",
    "primalMinResTol": 1.0e-10,
    "primalMinResTolDiff": 1.0e4,
    "printInterval": 200,
    "wallDistanceMethod": "daCustom",
    "primalBC": {
        "U0": {"variable": "U", "patches": ["inlet"], "value": [U0, 0.0, 0.0]},
        "p0": {"variable": "p", "patches": ["outlet"], "value": [p0]},
        "nuTilda0": {"variable": "nuTilda", "patches": ["inlet"], "value": [nuTilda0]},
        "useWallFunction": True,
    },
    "function": {
        "TPIn": {
            "type": "totalPressure",
            "source": "patchToFace",
            "patches": ["inlet"],
            "scale": 1.0 / (0.5 * U0 * U0),
            "addToAdjoint": True,
        },
    },
    "adjEqnOption": {
        "gmresRelTol": 1.0e-8,
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
        self.dvs.add_output("patchV", val=np.array([U0 + args.uOffset, aoa0 + args.aoaOffset]))
        self.connect("patchV", "scenario1.patchV")
        self.add_design_var("patchV", lower=[1.0, -5.0], upper=[50.0, 5.0], scaler=1.0)
        self.add_objective("scenario1.aero_post.TPIn", scaler=1.0)


prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")

rec = {"task": args.task, "uOffset": args.uOffset, "aoaOffset": args.aoaOffset,
       "sched_affinity": sorted(os.sched_getaffinity(0)), "status": "STARTED"}
prob.run_model()
rec["TPIn"] = float(np.atleast_1d(prob.get_val("scenario1.aero_post.TPIn"))[0])
rec["patchV"] = [float(v) for v in np.atleast_1d(prob.get_val("patchV"))]

if args.task == "compute_totals":
    totals = prob.compute_totals(of=["scenario1.aero_post.TPIn"], wrt=["patchV"])
    key = ("scenario1.aero_post.TPIn", "patchV")
    d = np.atleast_1d(np.array(totals[key]).ravel())
    rec["dTPIn_dpatchV"] = [float(v) for v in d]

rec["status"] = "COMPLETE"
if MPI.COMM_WORLD.rank == 0:
    with open(args.out, "w") as f:
        json.dump(rec, f, indent=2, sort_keys=True)
    print("D11C_PROBE_JSON_WRITTEN: " + os.path.abspath(args.out))
