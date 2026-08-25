#!/usr/bin/env python
"""
CURRICULUM D12 CAPABILITY PROBE -- unsteady-adjoint reachability (`DAPimpleFoam`,
unsteadyAdjoint mode timeAccurate) on the installed DAFoam image.
Frozen instrument; do not edit after the pre-registration commit.

Substrate: the upstream DAFoam `Cylinder` tutorial (2D cylinder, time-averaged CD),
which IS the curriculum's D12 case, at a REGISTERED PROBE REDUCTION of 5 timesteps
started from 0_orig rather than the tutorial's 300 steps from an equilibrium field.
The daOptions block below is the tutorial's, verbatim except for the two probe
reductions named in the pre-registration.

Every graded quantity, including the checkpoint RAM envelope, is written to disk
as JSON.  Nothing is graded from stdout.
"""
import argparse, json, os, resource, sys
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys.mphys_dafoam import DAFoamBuilderUnsteady
from pygeo.mphys import OM_DVGEOCOMP

parser = argparse.ArgumentParser()
parser.add_argument("-task", type=str, default="compute_totals")
parser.add_argument("-out", type=str, default="d12_probe_out.json")
parser.add_argument("-shapePlant", type=float, default=0.0,
                    help="value planted into shape[0]; 0.0 is the unplanted baseline")
args = parser.parse_args()

U0 = 10.0
p0 = 0.0
nuTilda0 = 4.5e-5
A0 = 0.1

daOptions = {
    "designSurfaces": ["cylinder"],
    "solverName": "DAPimpleFoam",
    "primalBC": {
        "U0": {"variable": "U", "patches": ["inout"], "value": [U0, 0.0, 0.0]},
        "useWallFunction": True,
    },
    "unsteadyAdjoint": {
        "mode": "timeAccurate",
        "PCMatPrecomputeInterval": 100,
        "PCMatUpdateInterval": 1,
        "reduceIO": True,
        "zeroInitFields": False,
    },
    "printIntervalUnsteady": 1,
    "function": {
        "CD": {
            "type": "force",
            "source": "patchToFace",
            "patches": ["cylinder"],
            "directionMode": "fixedDirection",
            "direction": [1.0, 0.0, 0.0],
            "scale": 1.0 / (0.5 * U0 * U0 * A0),
            "timeOp": "average",
        },
        "CL": {
            "type": "force",
            "source": "patchToFace",
            "patches": ["cylinder"],
            "directionMode": "fixedDirection",
            "direction": [0.0, 1.0, 0.0],
            "scale": 1.0 / (0.5 * U0 * U0 * A0),
            "timeOp": "average",
        },
    },
    "adjStateOrdering": "cell",
    "adjEqnOption": {
        "gmresRelTol": 1.0e-100,
        "gmresAbsTol": 1.0e-6,
        "gmresMaxIters": 100,
        "pcFillLevel": 1,
        "jacMatReOrdering": "natural",
        "useNonZeroInitGuess": False,
        "useMGSO": True,
    },
    "normalizeStates": {
        "U": U0,
        "p": U0 * U0 / 2.0,
        "nuTilda": nuTilda0 * 10.0,
        "phi": 1.0,
    },
    "inputInfo": {
        "aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]},
    },
    "checkMeshThreshold": {"maxAspectRatio": 5000.0},
    "unsteadyCompOutput": {"obj": ["CD"]},
}

meshOptions = {
    "gridFile": os.getcwd(),
    "fileType": "OpenFOAM",
    "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]], [[0.0, 0.0, 0.1], [0.0, 0.0, 1.0]]],
}

NSHAPES = []


class Top(Multipoint):
    def setup(self):
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])
        self.add_subsystem("geometry", OM_DVGEOCOMP(file="FFD/FFD.xyz", type="ffd"), promotes=["*"])
        self.add_subsystem(
            "scenario1",
            DAFoamBuilderUnsteady(solver_options=daOptions, mesh_options=meshOptions),
            promotes=["*"],
        )
        self.connect("x_aero0", "x_aero")

    def configure(self):
        points = self.scenario1.get_surface_mesh()
        self.geometry.nom_add_discipline_coords("aero", points)
        pts = self.geometry.DVGeo.getLocalIndex(0)
        dir_x = np.array([1.0, 0.0, 0.0])
        shapes = []
        for j in [0, 1]:
            for i in [0, 1]:
                shapes.append({pts[i, j, 0]: dir_x, pts[i, j, 1]: dir_x,
                               pts[i, 3 - j, 0]: dir_x, pts[i, 3 - j, 1]: dir_x})
        self.geometry.nom_addShapeFunctionDV(dvName="shape", shapes=shapes)
        NSHAPES.append(len(shapes))
        shape0 = np.array([0.0] * len(shapes))
        shape0[0] = args.shapePlant          # THE PLANT, when non-zero
        self.dvs.add_output("shape", val=shape0)
        self.dvs.add_output("x_aero_in", val=points, distributed=True)
        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)
        self.add_objective("obj", scaler=1.0)


prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")

rec = {"task": args.task, "shapePlant": args.shapePlant, "status": "STARTED"}
prob.run_model()
rec["obj"] = float(np.atleast_1d(prob.get_val("obj"))[0])
rec["shape"] = [float(v) for v in np.atleast_1d(prob.get_val("shape"))]
rec["nShapes"] = NSHAPES[0] if NSHAPES else 0
rec["maxrss_GiB_after_primal"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0

if args.task == "compute_totals":
    totals = prob.compute_totals(of=["obj"], wrt=["shape"])
    d = np.atleast_1d(np.array(totals[("obj", "shape")]).ravel())
    rec["dobj_dshape"] = [float(v) for v in d]
    rec["maxrss_GiB_after_adjoint"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0 / 1024.0

rec["status"] = "COMPLETE"
if MPI.COMM_WORLD.rank == 0:
    with open(args.out, "w") as f:
        json.dump(rec, f, indent=2, sort_keys=True)
    print("D12_PROBE_JSON_WRITTEN: " + os.path.abspath(args.out))
