#!/usr/bin/env python
"""
CURRICULUM D12 (proper) -- unsteady adjoint, 2D cylinder time-averaged drag.
FROZEN INSTRUMENT.  Do not edit after the pre-registration commit.

daOptions below is the upstream DAFoam `Cylinder` tutorial's runScript.py block
VERBATIM.  Unlike the D12 reachability probe there is NO reduction of any kind:
the window comes from system/controlDict, and the initial field comes from `0`,
which the launcher stages as FIELD_B (the frozen post-transient field).

Every graded quantity is written to disk as JSON.  NOTHING is graded from stdout.

CLI NOTE, and it is not cosmetic.  D11-O' was destroyed by argparse treating
`-1.0e-3` as an option flag: argparse's negative-number matcher accepts `-1` and
`-0.001` but NOT exponent notation.  Every numeric option here is therefore
declared with a DOUBLE dash and MUST be passed in the `--name=value` form, which
argparse resolves before any flag matching can occur.
"""
import argparse, json, os, resource, sys
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys.mphys_dafoam import DAFoamBuilderUnsteady
from pygeo.mphys import OM_DVGEOCOMP

parser = argparse.ArgumentParser()
parser.add_argument("--task", type=str, default="run_model",
                    choices=["run_model", "compute_totals", "opt"])
parser.add_argument("--out", type=str, default="d12r_out.json")
parser.add_argument("--dvIndex", type=int, default=0,
                    help="which shape component carries --dvDelta")
parser.add_argument("--dvDelta", type=str, default="0.0",
                    help="value written into shape[dvIndex]; STRING, parsed by float(), "
                         "so exponent notation and a leading minus are both safe")
parser.add_argument("--maxIter", type=int, default=15, help="IPOPT max majors, task=opt only")
args = parser.parse_args()

DV_DELTA = float(args.dvDelta)

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
        if not (0 <= args.dvIndex < len(shapes)):
            raise RuntimeError("dvIndex %d out of range for %d shapes" % (args.dvIndex, len(shapes)))
        shape0[args.dvIndex] = DV_DELTA
        self.dvs.add_output("shape", val=shape0)
        self.dvs.add_output("x_aero_in", val=points, distributed=True)
        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)
        self.add_objective("obj", scaler=1.0)


prob = om.Problem()
prob.model = Top()

rec = {"task": args.task, "dvIndex": args.dvIndex, "dvDelta": DV_DELTA,
       "cwd": os.getcwd(), "status": "STARTED"}

if args.task == "opt":
    prob.driver = om.pyOptSparseDriver()
    prob.driver.options["optimizer"] = "IPOPT"
    prob.driver.opt_settings = {
        "tol": 1.0e-5,
        "constr_viol_tol": 1.0e-5,
        "max_iter": args.maxIter,
        "print_level": 5,
        "output_file": "opt_IPOPT.out",
        "mu_strategy": "adaptive",
        "limited_memory_max_history": 10,
        "nlp_scaling_method": "none",
        "alpha_for_y": "full",
        "recalc_y": "no",
    }
    prob.driver.options["debug_print"] = ["nl_cons", "objs", "desvars"]
    prob.driver.hist_file = "d12r_opt_hist.hst"

prob.setup(mode="rev")

if args.task == "opt":
    prob.run_driver()
else:
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
    print("D12R_JSON_WRITTEN: " + os.path.abspath(args.out))
