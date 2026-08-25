#!/usr/bin/env python
"""Curriculum D7 producer -- ONERA M6 lift-constrained transonic drag minimisation.

PROVENANCE, STATED SO IT CAN BE AUDITED RATHER THAN TRUSTED.  The flow
conditions, daOptions, adjoint block, FFD/refAxis setup, constraint geometry
(leList/teList) and DV bounds below are A3 RUNG 2's OWN, copied from the file
that produced that rung's graded FD table:
    /home/ubuntu/certonomous-runs/A3-rung2-n28-tpc1/runScript_tpc1.py
PREREGISTRATION.md sec.1 calls that configuration "quoted not chosen".  The
departures from that file are FOUR, each required by the pre-registration and
each named here:

  1. `primalMinResTol` 1.0e-6 -> **1.0e-8** and `primalMinResTolDiff` added at
     **1e4**.  PREREGISTRATION.md sec.1 registers both.  Rung 2 relaxed the
     tolerance for its check_totals stage only, and said so in its own comment;
     D7 is an optimisation and buys the tight tolerance the pre-registration
     froze.
  2. IPOPT `max_iter` 100 -> **30**.  PREREGISTRATION.md sec.2a: COST-DERIVED,
     not taste, and sec.7/sec.11 register the consequence in advance -- D7 is
     EXPECTED to cap-stop and its ceiling verdict is `GATE REACHED`, never
     `PASS` (DAFOAM_CHARTER.md sec.9).
  3. `CL_target` is **NOT a literal**.  Rung 2's file carries `CL_target =
     0.270` typed in.  PREREGISTRATION.md sec.1 forbids that: the target CL is
     "read from the baseline primal at run time and written to a file BEFORE
     the driver starts; it is not typed into this document from memory".  This
     file READS `d7_cl_target.json` and REFUSES to run the driver without it.
  4. `-optimizer` default SLSQP -> **IPOPT**, the optimiser sec.1 registers.

`findFeasibleDesign` is NOT called, exactly as in rung 2's own file where it is
commented out.  It would be a no-op here BY CONSTRUCTION: the CL target IS the
baseline CL, so the starting design is already feasible in CL to the precision
of the primal that measured it.  Stated rather than left as a silent omission.

EVERY GRADED NUMBER IS WRITTEN TO A FILE BY RANK 0.  MPI log splicing on this
ladder is MEASURED (A2/per_component_table/RESULTS.md sec.2.2, commit 79679a84):
four ranks interleave on one stdout and sever arrays mid-number.
"""
import os
import argparse
import json
import sys
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder, OptFuncs
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP
from pygeo import geo_utils

parser = argparse.ArgumentParser()
parser.add_argument("-optimizer", help="optimizer to use", type=str, default="IPOPT")
parser.add_argument("-task", help="type of run to do", type=str, default="run_driver")
args = parser.parse_args()

# =============================================================================
# Input Parameters -- A3 rung 2's own, unchanged
# =============================================================================
# Rung 2's documented flow condition: NASA TMR Onera M6 Case 2308 (Schmitt &
# Charpin, AGARD AR-138, 1979), M=0.84, alpha=3.06 deg, made self-consistent
# with THIS case's own gas properties (a = 347.08 m/s):  U0 = 0.84*347.08.
U0 = 291.6
p0 = 101325.0
nuTilda0 = 4.5e-5
T0 = 300.0
aoa0 = 3.06
A0 = 0.7575
rho0 = 1.0  # density for normalizing CD and CL

# ---- registered DV sizes (PREREGISTRATION.md sec.1), ASSERTED not assumed ---
N_TWIST_REGISTERED = 5
N_SHAPE_REGISTERED = 120
N_PATCHV_REGISTERED = 2

CL_TARGET_FILE = "d7_cl_target.json"
BASELINE_FILE = "d7_baseline.json"


def _read_cl_target(task):
    """PREREGISTRATION.md sec.1: the target CL is READ FROM THE BASELINE PRIMAL
    AT RUN TIME, from a FILE written before the driver starts.  It is never
    typed in from memory.  For `run_driver` a missing file is a HARD REFUSAL:
    a driver that invented its own constraint target would be grading itself."""
    if os.path.isfile(CL_TARGET_FILE):
        with open(CL_TARGET_FILE) as fh:
            d = json.load(fh)
        v = float(d["CL_target"])
        if MPI.COMM_WORLD.rank == 0:
            sys.stdout.write("D7_CL_TARGET_READ %r source=%s\n" % (v, d.get("_source")))
        return v, True
    if task == "run_driver":
        sys.stderr.write(
            "D7_PRODUCER REFUSE run_driver requires %s, written from the "
            "baseline primal BEFORE the driver starts (PREREGISTRATION sec.1). "
            "It is absent.\n" % CL_TARGET_FILE)
        MPI.COMM_WORLD.Barrier()
        sys.exit(2)
    # For run_model / compute_totals the equality target does not enter the
    # primal or the totals; it is a placeholder and is DECLARED as one.
    if MPI.COMM_WORLD.rank == 0:
        sys.stdout.write("D7_CL_TARGET_PLACEHOLDER task=%s (target unused by "
                         "this task; no file present)\n" % task)
    return 0.0, False


CL_target, CL_TARGET_FROM_FILE = _read_cl_target(args.task)

# Set the parameters for optimization -- A3 rung 2's own block
daOptions = {
    "designSurfaces": ["wing"],
    "solverName": "DARhoSimpleCFoam",
    # DEPARTURE 1 (see module docstring): rung 2 ran 1.0e-6 for its check_totals
    # stage only.  PREREGISTRATION.md sec.1 freezes 1.0e-8 / diff 1e4 for D7.
    "primalMinResTol": 1.0e-8,
    "primalMinResTolDiff": 1.0e4,
    "primalBC": {
        "U0": {"variable": "U", "patches": ["inout"], "value": [U0, 0.0, 0.0]},
        "p0": {"variable": "p", "patches": ["inout"], "value": [p0]},
        "T0": {"variable": "T", "patches": ["inout"], "value": [T0]},
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
    "adjStateOrdering": "cell",
    # A3 RUNG 2's OWN ADJOINT BLOCK, quoted not chosen (PREREGISTRATION sec.1):
    # ILU(0) stock, natural ordering, gmresRestart 200, relTol 1e-4, 2000 iters.
    # DAFOAM_SUBPC_TYPE is UNSET at launch -- the launcher does not export it.
    "adjEqnOption": {"gmresRelTol": 1.0e-4, "pcFillLevel": 0,
                     "jacMatReOrdering": "natural", "gmresRestart": 200,
                     "gmresMaxIters": 2000},
    # transonicPCOption 1: 2 is dead code for DARhoSimpleCFoam
    # (DAResidualRhoSimpleCFoam.C:173) -- rung 2's finding, carried.
    "transonicPCOption": 1,
    "normalizeStates": {"U": U0, "p": p0, "nuTilda": nuTilda0 * 10.0,
                        "phi": 1.0, "T": T0},
    "adjPCLag": 5,
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
    "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]]],
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

        nRefAxPts = self.geometry.nom_addRefAxis(name="wingAxis", xFraction=0.25, alignIndex="k")

        def twist(val, geo):
            for i in range(1, nRefAxPts):
                geo.rot_z["wingAxis"].coef[i] = -val[i - 1]

        self.geometry.nom_addGlobalDV(dvName="twist", value=np.array([0] * (nRefAxPts - 1)), func=twist)

        pts = self.geometry.DVGeo.getLocalIndex(0)
        indexList = pts[:, :, :].flatten()
        PS = geo_utils.PointSelect("list", indexList)
        nShapes = self.geometry.nom_addLocalDV(dvName="shape", pointSelect=PS)

        # ---- REGISTERED DV SIZES, ASSERTED FROM THE GEOMETRY ITSELF --------
        # PREREGISTRATION.md sec.1 registers twist 5, shape 120, patchV 2, read
        # from A3 rung 2's own record.  They are ASSERTED here against what the
        # FFD actually produces rather than hard-coded: a silently different DV
        # count would move `shape[115]`, `shape[119]` and `twist[1]` onto
        # different physical quantities and every named component in sec.6
        # would then be a different measurement wearing the same label.
        n_twist = int(nRefAxPts - 1)
        if n_twist != N_TWIST_REGISTERED:
            raise RuntimeError(
                "D7_PRODUCER REFUSE twist size %d != registered %d "
                "(nRefAxPts=%d)" % (n_twist, N_TWIST_REGISTERED, nRefAxPts))
        if int(nShapes) != N_SHAPE_REGISTERED:
            raise RuntimeError(
                "D7_PRODUCER REFUSE shape size %d != registered %d"
                % (int(nShapes), N_SHAPE_REGISTERED))
        if self.comm.rank == 0:
            sys.stdout.write("D7_DV_SIZES_OK twist=%d shape=%d patchV=%d\n"
                             % (n_twist, int(nShapes), N_PATCHV_REGISTERED))

        leList = [[0.01, 0.0, 1e-3], [0.7, 0.0, 1.19]]
        teList = [[0.79, 0.0, 1e-3], [1.135, 0.0, 1.19]]
        self.geometry.nom_addThicknessConstraints2D("thickcon", leList, teList, nSpan=10, nChord=10)
        self.geometry.nom_addVolumeConstraint("volcon", leList, teList, nSpan=10, nChord=10)
        self.geometry.nom_add_LETEConstraint("lecon", volID=0, faceID="iLow")
        self.geometry.nom_add_LETEConstraint("tecon", volID=0, faceID="iHigh")

        self.dvs.add_output("twist", val=np.array([0] * (nRefAxPts - 1)))
        self.dvs.add_output("shape", val=np.array([0] * nShapes))
        self.dvs.add_output("patchV", val=np.array([U0, aoa0]))
        self.connect("twist", "geometry.twist")
        self.connect("shape", "geometry.shape")
        self.connect("patchV", "scenario1.patchV")

        self.add_design_var("twist", lower=-10.0, upper=10.0, scaler=0.1)
        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)
        # U0 is fixed at BOTH bounds, so AoA (patchV[1]) is the only free
        # component -- PREREGISTRATION.md sec.1, verbatim.
        self.add_design_var("patchV", lower=[U0, 0.0], upper=[U0, 10.0], scaler=0.1)

        self.add_objective("scenario1.aero_post.CD", scaler=1.0)
        self.add_constraint("scenario1.aero_post.CL", equals=CL_target, scaler=1.0)
        self.add_constraint("geometry.thickcon", lower=0.5, upper=3.0, scaler=1.0)
        self.add_constraint("geometry.volcon", lower=1.0, scaler=1.0)
        self.add_constraint("geometry.tecon", equals=0.0, scaler=1.0, linear=True)
        self.add_constraint("geometry.lecon", equals=0.0, scaler=1.0, linear=True)


# OpenMDAO setup
prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")
om.n2(prob, show_browser=False, outfile="mphys.html")

optFuncs = OptFuncs(daOptions, prob)

prob.driver = om.pyOptSparseDriver()
prob.driver.options["optimizer"] = args.optimizer
if args.optimizer == "IPOPT":
    prob.driver.opt_settings = {
        "tol": 1.0e-5,
        "constr_viol_tol": 1.0e-5,
        # DEPARTURE 2: COST-DERIVED cap, PREREGISTRATION.md sec.2a.  D7 is
        # EXPECTED to cap-stop; a cap-stop is GATE REACHED, never PASS.
        "max_iter": 30,
        "print_level": 5,
        "output_file": "opt_IPOPT.txt",
        "mu_strategy": "adaptive",
        "limited_memory_max_history": 10,
        "nlp_scaling_method": "none",
        "alpha_for_y": "full",
        "recalc_y": "yes",
    }
elif args.optimizer == "SLSQP":
    prob.driver.opt_settings = {"ACC": 1.0e-5, "MAXIT": 30, "IFILE": "opt_SLSQP.txt"}
else:
    print("optimizer arg not valid!")
    exit(1)

prob.driver.options["debug_print"] = ["nl_cons", "objs", "desvars"]
prob.driver.options["print_opt_prob"] = True
prob.driver.hist_file = "OptView.hst"

CDKEY = "scenario1.aero_post.CD"
CLKEY = "scenario1.aero_post.CL"


def _write_baseline(tag):
    """Write the baseline primal's CD and CL to a FILE, from rank 0, fsynced.
    This file is what sec.1's CL target is derived from -- the run measures it,
    nobody types it."""
    if MPI.COMM_WORLD.rank != 0:
        return
    rec = {"_tag": tag,
           "_cwd": os.getcwd(),
           "CD": float(prob.get_val(CDKEY)[0]),
           "CL": float(prob.get_val(CLKEY)[0]),
           "CD_repr": repr(float(prob.get_val(CDKEY)[0])),
           "CL_repr": repr(float(prob.get_val(CLKEY)[0])),
           "aoa0_deg": aoa0, "U0": U0, "A0": A0,
           "primalMinResTol": daOptions["primalMinResTol"],
           "cl_target_used": CL_target,
           "cl_target_from_file": CL_TARGET_FROM_FILE}
    with open(BASELINE_FILE, "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    sys.stdout.write("D7_BASELINE_WRITTEN %s CD=%r CL=%r\n"
                     % (BASELINE_FILE, rec["CD"], rec["CL"]))


if args.task == "run_driver":
    if not CL_TARGET_FROM_FILE:
        sys.stderr.write("D7_PRODUCER REFUSE run_driver without a measured CL target\n")
        sys.exit(2)
    prob.run_driver()
elif args.task == "run_model":
    prob.run_model()
    _write_baseline("run_model")
elif args.task == "compute_totals":
    prob.run_model()
    _write_baseline("compute_totals_primal")
    totals = prob.compute_totals()
    if MPI.COMM_WORLD.rank == 0:
        print(totals)
elif args.task == "check_totals":
    prob.run_model()
    prob.check_totals(compact_print=False, step=1e-2, form="central", step_calc="abs")
else:
    print("task arg not found!")
    exit(1)
