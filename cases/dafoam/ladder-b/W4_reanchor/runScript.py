#!/usr/bin/env python
"""
DAFoam DASimpleFoam run script for CBFS (curved backward-facing step),
Ladder B3. CBFS is the paper's field-inversion TRAINING case (not one of the
8 scored closure-challenge test cases) -- reading its LES fields carries no
leakage exposure.

Objective function: DAFoam's native "variance" DAFunction (mode=field,
source=allCells) against 0/UData, which is CBFS's own LES U field, macro-
resolved by macro_field_reader.py and written out as a standard OpenFOAM
volVectorField. This is DAFoam's built-in mechanism for field-inversion-style
loss functions (Description in DAFunctionVariance.C: reads "<varName>Data"
from the 0/ folder, cell-by-cell variance against the current state).

Design variable for this pilot: inlet patch velocity (patchVelocity,
magnitude+angle), NOT the paper's actual beta destruction-term field. The
paper's real design variable requires a custom OpenFOAM turbulence-model
library (source not distributed anywhere in the public benchmark clone --
documented in B2) that multiplies the SST omega equation's destruction term
by a spatially-varying beta(x). Building that library is out of scope for
this timed pilot. patchV is used here ONLY to get one real primal+adjoint
solve through DAFoam's actual discrete-adjoint machinery on this exact
mesh/case, to measure the linear-solve-dominated cost per iteration -- that
cost is expected to be roughly independent of which specific design variable
the total derivative is being computed with respect to, since it is
dominated by one adjoint (transpose) linear solve of the discrete residual
Jacobian, sized by the state vector (all cells x all state variables), not
by the number/type of design variables. This substitution is reported
explicitly, not hidden.

NOTE: using patchVelocity on "inlet" overwrites CBFS's real nonuniform inlet
profile with a uniform velocity derived from (magnitude, angle) for the
DURATION OF THIS PILOT RUN ONLY. Stage 2 (confirming the primal reproduces
B2's converged field) is run as a SEPARATE, plain run_model with NO design
variables and the case's real BCs untouched -- see runScript_stage2.py.
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
parser.add_argument("-task", help="type of run to do", type=str, default="run_model")
parser.add_argument("-betafile", type=str, default="")
parser.add_argument("-gradout", type=str, default="cbfs_beta_grad.npy")
# S1 reinversion FD diagnosis 2026-08-07: the 1e-6 stop leaves O(tol) state error
# that pollutes central differences of ~2e-6 in J (fd/adj ~0.7 on all 3 cells,
# stop iters scattering 383-458). Tolerance made an argument so FD/eval runs can
# converge deeper; every use is billed and disclosed in the item record.
parser.add_argument("-primalTol", type=float, default=1.0e-6)
args = parser.parse_args()
import numpy as _np
NCELLS = 21000

U0 = 0.72
p0 = 0.0
k0 = 0.0042
omega0 = 1000.0

daOptions = {
    "designSurfaces": ["bottomWall", "topWall"],
    "solverName": "DASimpleFoam",
    # Both settings fixed per the stage-2 debugging (see runScript_stage2.py
    # comments): useWallFunction:True forcibly overrides CBFS's real
    # low-Re wall BCs (nutLowReWallFunction, k fixedValue 1e-15) with
    # high-Re wall functions -- a real physics change, not just noise.
    # primalMinResTol relaxed from 1e-8 to 1e-6, matching what a
    # warm-started primal on this case actually reaches (see stage2
    # convergence trend: 0.82% U MAE @300 iters -> 0.087% @1223 iters,
    # residual satisfied 1e-6 at iteration 1223).
    "primalMinResTol": args.primalTol,
    "primalBC": {},
    "function": {
        "varianceU": {
            "type": "variance",
            "source": "allCells",
            "mode": "field",
            "varName": "U",
            "varType": "vector",
            "indices": [0, 1, 2],
            "timeDependentRefData": False,
            "scale": 1.0,
        },
    },
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 1, "jacMatReOrdering": "rcm"},
    "normalizeStates": {
        "U": U0,
        "p": U0 * U0 / 2.0,
        "k": k0,
        "omega": omega0,
        "phi": 1.0,
        "nut": 1e-4,
    },
    "inputInfo": {
        "beta": {"type": "field", "fieldName": "betaFIOmega", "fieldType": "scalar",
                 "distributed": False, "components": ["solver", "function"]},
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
        b0 = np.ones(NCELLS)
        if args.betafile:
            b0 = np.load(args.betafile)
        self.dvs.add_output("beta", val=b0, distributed=False)
        self.connect("beta", "scenario1.beta")
        self.add_design_var("beta", lower=0.2, upper=4.0, scaler=1.0)  # S1 prereg bounds; no effect on compute_totals
        self.add_objective("scenario1.aero_post.varianceU", scaler=1.0)


prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")

rank = MPI.COMM_WORLD.rank

t_setup_done = time.time()

if args.task == "run_model":
    t0 = time.time()
    prob.run_model()
    t1 = time.time()
    if rank == 0:
        print("TIMING run_model wall_s:", t1 - t0)
        print("OBJ varianceU: %.16e" % prob.get_val("scenario1.aero_post.varianceU")[0])
elif args.task == "compute_totals":
    t0 = time.time()
    prob.run_model()
    t1 = time.time()
    totals = prob.compute_totals()
    t2 = time.time()
    if rank == 0:
        print("TIMING primal_wall_s:", t1 - t0)
        print("TIMING adjoint_wall_s:", t2 - t1)
        print("TIMING compute_totals_total_wall_s:", t2 - t0)
        print("OBJ varianceU: %.16e" % prob.get_val("scenario1.aero_post.varianceU")[0])
        g = np.array(totals[("scenario1.aero_post.functionals.varianceU", "dvs.beta")]).ravel()
        print("GRAD n=%d norm=%.10e min=%.6e max=%.6e" % (g.size, np.linalg.norm(g), g.min(), g.max()))
        np.save(args.gradout, g)
else:
    print("task arg not found!")
    exit(1)
