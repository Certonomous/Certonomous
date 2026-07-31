#!/usr/bin/env python
"""
Stage 1 FIML capability probe, built from DAFoam's own official field-inversion
tutorial (dafoam-tutorials/Ramp/steady/train/runScript_FI.py), reduced to the
single question that matters here: does a *field* design variable (beta on the
omega equation) drive a converging discrete adjoint, and is mesh.warpDeriv in
its derivative chain at all?

Deliberate reductions vs the tutorial, all disclosed:
  - regressionModel deactivated: the DV here is the raw betaFIOmega field, not
    a neural-network parameterisation of it. Removes a confound.
  - single objective (UFieldVar) rather than the tutorial's 3-term composite,
    so the adjoint seed is one unambiguous quantity.
  - task=compute_totals only; FD verification is done separately and manually
    (a 5000-component check_totals would need 10,000 primal re-solves).
"""
import os, sys, time, argparse, json
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic

parser = argparse.ArgumentParser()
parser.add_argument("-task", type=str, default="compute_totals")
parser.add_argument("-case", type=str, default="c1")
parser.add_argument("-turb", type=str, default="kOmega")
parser.add_argument("-ncells", type=int, default=5000)
parser.add_argument("-out", type=str, default="s1_out.json")
parser.add_argument("-betafile", type=str, default="")   # optional beta to load
parser.add_argument("-beta0", type=float, default=1.0)  # uniform initial beta
parser.add_argument("-tol", type=float, default=1e-8)
args = parser.parse_args()

# ---------------------------------------------------------------- warp probe
# Instrument every route by which mesh.warpDeriv could enter the chain.
PROBE = {"warper_init": 0, "warper_jacvec": 0, "idwarp_imported_at_setup": None,
         "warpderiv_calls": 0}
from dafoam.mphys import mphys_dafoam as _md
if hasattr(_md, "DAFoamWarper"):
    _oi = _md.DAFoamWarper.__init__
    def _init(self, *a, **k):
        PROBE["warper_init"] += 1
        return _oi(self, *a, **k)
    _md.DAFoamWarper.__init__ = _init
    if hasattr(_md.DAFoamWarper, "compute_jacvec_product"):
        _oj = _md.DAFoamWarper.compute_jacvec_product
        def _jv(self, *a, **k):
            PROBE["warper_jacvec"] += 1
            return _oj(self, *a, **k)
        _md.DAFoamWarper.compute_jacvec_product = _jv

U0 = 10.0
nCells = args.ncells

daOptions = {
    "solverName": "DASimpleFoam",
    "primalMinResTol": args.tol,
    "primalMinResTolDiff": 1e3,
    "primalBC": {"U0": {"variable": "U", "patches": ["inlet"], "value": [U0, 0, 0]},
                 "useWallFunction": True},
    "primalVarBounds": {"omegaMin": -1e16},
    "function": {
        "UFieldVar": {
            "type": "variance", "source": "boxToCell",
            "min": [-10.0, -10.0, -10.0], "max": [10.0, 10.0, 10.0],
            "scale": 0.1, "mode": "field", "varName": "U", "varType": "vector",
            "indices": [0, 1], "timeDependentRefData": False,
        },
    },
    "adjStateOrdering": "cell",
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 1,
                     "jacMatReOrdering": "natural"},
    "normalizeStates": {"U": U0, "p": U0 * U0 / 2.0, "nuTilda": 1e-3, "phi": 1.0},
    "inputInfo": {
        "beta": {"type": "field", "fieldName": "betaFIOmega", "fieldType": "scalar",
                 "distributed": False, "components": ["solver", "function"]},
    },
}

class Top(Multipoint):
    def setup(self):
        b = DAFoamBuilder(options=daOptions, mesh_options=None,
                          scenario="aerodynamic", run_directory=args.case)
        b.initialize(self.comm)
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])
        self.mphys_add_scenario("scenario1", ScenarioAerodynamic(aero_builder=b))

    def configure(self):
        beta0 = np.ones(nCells) * args.beta0
        if args.betafile:
            beta0 = np.load(args.betafile)
        self.dvs.add_output("beta", val=beta0, distributed=False)
        self.connect("beta", "scenario1.beta")
        self.add_design_var("beta", lower=-5.0, upper=10.0, scaler=1.0)
        self.add_objective("scenario1.aero_post.UFieldVar", scaler=1.0)

prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")
PROBE["idwarp_imported_at_setup"] = "idwarp" in sys.modules
rank = MPI.COMM_WORLD.rank

OF = "scenario1.aero_post.UFieldVar"

if args.task == "run_model":
    t0 = time.time(); prob.run_model(); t1 = time.time()
    if rank == 0:
        print("TIMING primal_wall_s: %.3f" % (t1 - t0))
        print("OBJ UFieldVar: %.16e" % prob.get_val(OF)[0])

elif args.task == "compute_totals":
    t0 = time.time(); prob.run_model(); t1 = time.time()
    totals = prob.compute_totals(of=[OF], wrt=["beta"])
    t2 = time.time()
    g = np.array(totals[(OF, "beta")]).ravel()
    if rank == 0:
        print("TIMING primal_wall_s: %.3f" % (t1 - t0))
        print("TIMING adjoint_wall_s: %.3f" % (t2 - t1))
        print("OBJ UFieldVar: %.16e" % prob.get_val(OF)[0])
        print("GRAD n=%d  norm=%.10e  min=%.6e  max=%.6e"
              % (g.size, np.linalg.norm(g), g.min(), g.max()))
        print("WARP PROBE:", json.dumps(PROBE))
        np.save(args.out.replace(".json", "_grad.npy"), g)
        json.dump({"obj": float(prob.get_val(OF)[0]),
                   "grad_norm": float(np.linalg.norm(g)),
                   "primal_s": t1 - t0, "adjoint_s": t2 - t1,
                   "probe": PROBE, "n": int(g.size)},
                  open(args.out, "w"), indent=2)
else:
    print("bad task"); sys.exit(1)
