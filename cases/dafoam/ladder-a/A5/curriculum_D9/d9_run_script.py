#!/usr/bin/env python
"""
CURRICULUM D9 -- U-BEND PRESSURE-LOSS MINIMISATION.  Frozen instrument.

DERIVED FROM /home/ubuntu/certonomous-runs/W5-regrade/a5pl_stock/runScript.py
(md5 06fb0ed4228d9927992a12a2fb68055c), the EXACT configuration the published A5
numbers came from.  Every change from it is listed here and nowhere else:

  D9-1  `-maxit` sets the SLSQP major-iteration limit from the launcher, so the
        CALIBRATION MAJOR (maxit=1) and the full buy run the SAME instrument.
  D9-2  ONLY `shapexUpper` is an optimiser design variable.  The other five DV
        groups are still declared to pyGeo (so the FFD object is byte-identical)
        but are NOT added as design variables.  REASON, and it is the whole
        design decision of this item: `OBJ.val wrt shapexUpper` is the ONLY A5
        total derivative this lab has ever FD-verified -- PASS (patched), 2.768 %
        aggregate, 0 sign flips, at np=1.  DAFOAM_CHARTER section 2 forbids a
        DAFoam gradient entering an optimisation without an FD table beside it,
        so an optimiser driven by the other five groups would be driving on
        unverified derivatives.  The five commented lines are left in place,
        commented, so the departure is visible as a diff rather than as an absence.
  D9-3  every graded quantity is written to JSON.  NOTHING IS GRADED FROM STDOUT.
        For `check_totals` the RAW `J_fwd` and `J_fd` arrays are recorded and the
        aggregate is computed by the GRADER, not here -- an instrument that
        computes its own headline can round it.
  D9-4  measured CPU affinity is written into every record, so placement is READ
        FROM THE PROCESS and never inferred from the flag the launcher passed.
  D9-5  the driver history is recorded best-effort; a recorder failure is recorded
        as `hist_error` and DOES NOT reach any gate.
  D9-6  the original's `probe` and `compute_totals` task branches are REMOVED --
        D9 uses none of them, and a task this item never registered must not be
        reachable from this item's instrument.  `run_driver`, `run_model` and
        `check_totals` are the three registered tasks and the only three that exist.
  D9-7  `-dvFile` loads an optimised `shapexUpper` before the task, so the endpoint
        FD spot-check verifies the OPTIMISED geometry rather than the baseline.
  D9-8  `-fdStep` exposes the central-FD step, which is SIZED AGAINST A MEASURED
        NOISE FLOOR (delta_repeat) rather than copied from A5's 1e-4.

np=1 THROUGHOUT, deliberately.  A5's np=1 re-verification localised the idx16
`check_totals` anomaly to the np=4 FD path: np=1 reports -5.00483123 at idx16,
inside the cluster of three independent re-measurements, while the published np=4
value -4.30296296 sits 16.3 % away and the neighbouring idx15 agrees across rank
counts to 5 parts in 100,000.  The endpoint FD spot-check this item is gated on
therefore MUST be at np=1 or it would be read through the corrupted path.
"""
# =============================================================================
# Imports
# =============================================================================
import argparse
import json
from mpi4py import MPI
import os
import numpy as np
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP
from pygeo import geo_utils

# =============================================================================
# Input Parameters
# =============================================================================
parser = argparse.ArgumentParser()
# which optimizer to use. Options are: IPOPT (default), SLSQP, and SNOPT
parser.add_argument("-optimizer", help="optimizer to use", type=str, default="SLSQP")
# which task to run. Options are: run_driver (default), run_model, compute_totals, check_totals
parser.add_argument("-task", help="type of run to do", type=str, default="run_driver")
# LADDER A5 diagnostic: manual single-index FD probe at a chosen step, to check step-size
# sensitivity of the FD verification (distinguish primal-residual noise from a real gradient gap)
parser.add_argument("-probeIdx", help="index into shapexUpper for manual FD probe", type=int, default=0)
parser.add_argument("-probeDelta", help="perturbation applied to shapexUpper[probeIdx]", type=float, default=0.0)
# D9-1: SLSQP major-iteration limit, so the calibration major and the full buy are one instrument
parser.add_argument("-maxit", help="SLSQP major iteration limit", type=int, default=25)
# D9-3: every graded quantity goes to this file as JSON
parser.add_argument("-out", help="JSON record path", type=str, default="d9_out.json")
# D9-3: the endpoint check runs at the OPTIMISED design point, loaded from the run_driver record
parser.add_argument("-dvFile", help="JSON holding shapexUpper to load before the task", type=str, default="")
parser.add_argument("-fdStep", help="central-FD step for check_totals", type=float, default=1.0e-4)
args = parser.parse_args()
gcomm = MPI.COMM_WORLD

# =============================================================================
# daOptions Setup
# =============================================================================
CPL_weight = 0.50                 # Weight of pressure loss (PL) in Obj. Function
HFX_weight = CPL_weight - 1.0     # Weight of heat flux (HFX) in obj. Function
HFX0 = 305                        # HFX value for baseline design
CPL0 = 85.23 - 35.62              # PL value for baseline design
U0 = 8.4                          # Fluid flow (m/s) in x-direction

daOptionsAero = {
    "solverName": "DASimpleFoam",
    "designSurfaces": ["ubend"],
    "useAD": {"mode": "reverse"},
    "primalMinResTol": 1e-8,
    "primalMinResTolDiff": 1e7,
    "writeMinorIterations": True,
    "wallDistanceMethod": "daCustom",
    "primalBC" : {
        "useWallFunction": True,
    },

    "function": {

            "TP1": {
                "type": "totalPressure",
                "source": "patchToFace",
                "patches": ["inlet"],
                "scale": 1.0,
                "addToAdjoint": True,
            },

            "TP2": {
                "type": "totalPressure",
                "source": "patchToFace",
                "patches": ["outlet"],
                "scale": 1.0,
                "addToAdjoint": True,
            },

            "HFX": {
                "type": "wallHeatFlux",
                "source": "patchToFace",
                "patches": ["ubend"],
                "scale": 1.0,
                "addToAdjoint": False,
            },

    },

    "adjStateOrdering": "cell",

    "adjEqnOption": {"gmresRelTol"      : 1e-5,
                     "gmresTolDiff"     : 1e4,
                     "pcFillLevel"      : 2,
                     "jacMatReOrdering" : "natural",
                     "gmresMaxIters"    : 3000,
                     "gmresRestart"     : 3000},

    "normalizeStates": {"U"       : U0,
                        "p"       : (U0 * U0) / 2.,
                        "nuTilda" : 1e-3,
                        "phi"     : 1.0,
                        "T"       : 300},

    "inputInfo": {
        "aero_vol_coords": {"type": "volCoord", "components": ["solver" , "function"]},
    },

    "outputInfo": {
        "q_convect": {
            "type"       : "thermalCouplingOutput",
            "patches"    : ["ubend"],
            "components" : ["thermalCoupling"],
        },
    },

}

# =============================================================================
# Mesh Setup
# =============================================================================
meshOptions = {
    "gridFile"       : os.getcwd(),
    "fileType"       : "OpenFOAM",
    "symmetryPlanes" : [],
}

# =============================================================================
# Top class To Setup The Optimization Problem
# =============================================================================
class Top(Multipoint):
    def setup(self):

        # initialize builders
        dafoam_builder = DAFoamBuilder(daOptionsAero , meshOptions , scenario = "aerodynamic")
        dafoam_builder.initialize(self.comm)

        # add design variable component and promote to top level
        self.add_subsystem("dvs" , om.IndepVarComp() , promotes = ["*"])

        # add mesh component
        self.add_subsystem("mesh_aero" , dafoam_builder.get_mesh_coordinate_subsystem())

        # add geometry component
        self.add_subsystem("geometry_aero" , OM_DVGEOCOMP(file = "FFD/UBendDuctFFDSym.xyz" , type = "ffd"))

        # add a scenario (flow condition) for optimization. For no themal (solid) use ScenarioAerodynamic, for thermal (solid) use ScenarioAerothermal
        self.mphys_add_scenario("scenario" , ScenarioAerodynamic(aero_builder = dafoam_builder))

        # need to manually connect the x_aero0 between the mesh and geometry components
        self.connect("mesh_aero.x_aero0" , "geometry_aero.x_aero_in")
        self.connect("geometry_aero.x_aero0" , "scenario.x_aero")

        # add obj val for PL
        # LADDER A5: pure pressure-loss objective (stock tutorial blends in HFX; we don't)
        self.add_subsystem("OBJ" , om.ExecComp("val = TP1 - TP2"))

    def configure(self):

        # initialize the optimization
        super().configure()

        # get surface coordinates from mesh component
        points_aero = self.mesh_aero.mphys_get_surface_mesh()

        # add pointset to the geometry component
        self.geometry_aero.nom_add_discipline_coords("aero" , points_aero)

        # get FFD points
        pts = self.geometry_aero.nom_getDVGeo().getLocalIndex(0)

        #---------- setup DVs ----------
        # shapex
        indexList = []
        indexList.extend(pts[7:16 , 1 , :].flatten())
        PS = geo_utils.PointSelect("list" , indexList)
        shapexUpper = self.geometry_aero.nom_addLocalDV(dvName = "shapexUpper" , pointSelect = PS , axis = "x")

        # shapey
        indexList = []
        indexList.extend(pts[7:16 , 1 , :].flatten())
        PS = geo_utils.PointSelect("list" , indexList)
        shapeyUpper = self.geometry_aero.nom_addLocalDV(dvName = "shapeyUpper" , pointSelect = PS , axis = "y")

        # shapez
        indexList = []
        indexList.extend(pts[7:16 , 1 , :].flatten())
        PS = geo_utils.PointSelect("list", indexList)
        shapezUpper = self.geometry_aero.nom_addLocalDV(dvName = "shapezUpper" , pointSelect = PS , axis = "z")

        # shapex
        indexList = []
        indexList.extend(pts[7:16 , 0 , :].flatten())
        PS = geo_utils.PointSelect("list" , indexList)
        shapexLower = self.geometry_aero.nom_addLocalDV(dvName = "shapexLower" , pointSelect = PS , axis = "x")

        # shapey
        indexList = []
        indexList.extend(pts[7:16 , 0 , :].flatten())
        PS = geo_utils.PointSelect("list" , indexList)
        shapeyLower = self.geometry_aero.nom_addLocalDV(dvName = "shapeyLower" , pointSelect = PS , axis = "y")

        # shapez
        indexList = []
        indexList.extend(pts[7:16 , 0 , :].flatten())
        PS = geo_utils.PointSelect("list", indexList)
        shapezLower = self.geometry_aero.nom_addLocalDV(dvName = "shapezLower" , pointSelect = PS , axis = "z")

        #---------- Add Outputs For The DVs ----------
        self.dvs.add_output("shapexUpper" , val = np.array([0]*shapexUpper))
        self.dvs.add_output("shapeyUpper" , val = np.array([0]*shapeyUpper))
        self.dvs.add_output("shapezUpper" , val = np.array([0]*shapezUpper))

        self.dvs.add_output("shapexLower" , val = np.array([0]*shapexLower))
        self.dvs.add_output("shapeyLower" , val = np.array([0]*shapeyLower))
        self.dvs.add_output("shapezLower" , val = np.array([0]*shapezLower))

        #---------- Connect The Design Variables To The Geometry ----------
        self.connect("shapexUpper" , "geometry_aero.shapexUpper")
        self.connect("shapeyUpper" , "geometry_aero.shapeyUpper")
        self.connect("shapezUpper" , "geometry_aero.shapezUpper")

        self.connect("shapexLower" , "geometry_aero.shapexLower")
        self.connect("shapeyLower" , "geometry_aero.shapeyLower")
        self.connect("shapezLower" , "geometry_aero.shapezLower")

        #---------- Define The Design Variables To The Top Level ----------
        # D9-2  ONLY the FD-VERIFIED DV GROUP is an optimiser design variable.
        # `OBJ.val wrt shapexUpper` is the only A5 total derivative this lab has FD-verified
        # (PASS patched, 2.768 % aggregate, 0 sign flips, np=1).  The five lines below stay
        # COMMENTED, not deleted, so the departure reads as a diff.
        self.add_design_var("shapexUpper" , lower = -0.04 , upper = 0.04 , scaler = 25.0)
        # self.add_design_var("shapeyUpper" , lower = -0.04 , upper = 0.04 , scaler = 25.0)
        # self.add_design_var("shapezUpper" , lower = -0.04 , upper = 0.04 , scaler = 25.0)
        # self.add_design_var("shapexLower" , lower = -0.04 , upper = 0.04 , scaler = 25.0)
        # self.add_design_var("shapeyLower" , lower = -0.04 , upper = 0.04 , scaler = 25.0)
        # self.add_design_var("shapezLower" , lower = -0.04 , upper = 0.04 , scaler = 25.0)

        # add objective and constraints
        self.connect("scenario.aero_post.TP1" , "OBJ.TP1")
        self.connect("scenario.aero_post.TP2" , "OBJ.TP2")
        self.add_objective("OBJ.val" , scaler = 1.0)

# =============================================================================
# Problem Setup
# =============================================================================
prob = om.Problem(reports = None)
prob.model = Top()
prob.setup(mode = "rev")
prob.driver = om.pyOptSparseDriver()
prob.driver.options["optimizer"] = args.optimizer

if args.optimizer == "SNOPT":
    prob.driver.opt_settings = {
        "Major feasibility tolerance" : 1.0e-5,
        "Major optimality tolerance"  : 1.0e-5,
        "Minor feasibility tolerance" : 1.0e-5,
        "Verify level"                : -1,
        "Function precision"          : 1.0e-5,
        "Major iterations limit"      : 100,
        "Nonderivative linesearch"    : None,
        "Print file"                  : "opt_SNOPT_print.txt",
        "Summary file"                : "opt_SNOPT_summary.txt",
    }
elif args.optimizer == "IPOPT":
    prob.driver.opt_settings = {
        "tol"                        : 1.0e-5,
        "constr_viol_tol"            : 1.0e-5,
        "max_iter"                   : 100,
        "print_level"                : 5,
        "output_file"                : "opt_IPOPT.txt",
        "mu_strategy"                : "adaptive",
        "limited_memory_max_history" : 10,
        "nlp_scaling_method"         : "none",
        "alpha_for_y"                : "full",
        "recalc_y"                   : "yes",
    }
elif args.optimizer == "SLSQP":
    prob.driver.opt_settings = {
        "ACC"   : 1.0e-5,
        "MAXIT" : args.maxit,          # D9-1
        "IFILE" : "opt_SLSQP.txt",
    }
else:
    print("optimizer arg not valid!")
    exit(1)

prob.driver.options["debug_print"] = ["nl_cons" , "objs" , "desvars"]
prob.driver.options["print_opt_prob"] = True
prob.driver.hist_file = "OptView.hst"

# D9-3  load an optimised design point, if one was handed to this run.
if args.dvFile:
    with open(args.dvFile) as _f:
        _dv = json.load(_f)["shapexUpper"]
    prob.set_val("shapexUpper", np.array(_dv, dtype=float))
    print("D9_DVFILE_LOADED: %s  n=%d  l2=%.10e" % (args.dvFile, len(_dv), float(np.linalg.norm(_dv))))

# D9-3/4/5  ------------------------------------------------------------------
rec = {"task": args.task, "maxit": args.maxit, "optimizer": args.optimizer,
       "sched_affinity": sorted(os.sched_getaffinity(0)), "status": "STARTED"}

if args.task == "run_driver":
    # D9-5  history recorder, BEST EFFORT.  A failure here reaches no gate.
    try:
        prob.driver.add_recorder(om.SqliteRecorder("d9_hist.sql"))
        prob.driver.recording_options["includes"] = ["*"]
    except Exception as e:
        rec["recorder_error"] = repr(e)
    failed = prob.run_driver()
    rec["driver_failed"] = bool(failed)
    rec["driver_iter_count"] = int(getattr(prob.driver, "iter_count", -1))
    try:
        prob.cleanup()
        cr = om.CaseReader("d9_hist.sql")
        cs = cr.list_cases("driver", out_stream=None)
        rec["obj_history"] = [float(np.atleast_1d(cr.get_case(c).get_objectives()["OBJ.val"])[0]) for c in cs]
    except Exception as e:
        rec["hist_error"] = repr(e)
    rec["OBJ_val"] = float(np.atleast_1d(prob.get_val("OBJ.val"))[0])
    rec["TP1"] = float(np.atleast_1d(prob.get_val("scenario.aero_post.TP1"))[0])
    rec["TP2"] = float(np.atleast_1d(prob.get_val("scenario.aero_post.TP2"))[0])
    rec["shapexUpper"] = [float(v) for v in np.atleast_1d(prob.get_val("shapexUpper"))]

elif args.task == "run_model":
    prob.run_model()
    rec["OBJ_val"] = float(np.atleast_1d(prob.get_val("OBJ.val"))[0])
    rec["TP1"] = float(np.atleast_1d(prob.get_val("scenario.aero_post.TP1"))[0])
    rec["TP2"] = float(np.atleast_1d(prob.get_val("scenario.aero_post.TP2"))[0])
    rec["shapexUpper"] = [float(v) for v in np.atleast_1d(prob.get_val("shapexUpper"))]

elif args.task == "check_totals":
    # D9-3  the endpoint FD spot-check.  The design point is whatever `-dvFile` loaded,
    # so this task verifies the OPTIMISED geometry, not the baseline.
    prob.run_model()
    rec["OBJ_val"] = float(np.atleast_1d(prob.get_val("OBJ.val"))[0])
    rec["shapexUpper"] = [float(v) for v in np.atleast_1d(prob.get_val("shapexUpper"))]
    data = prob.check_totals(
        of            = ["OBJ.val"],
        wrt           = ["shapexUpper"],
        compact_print = False,
        step          = args.fdStep,
        form          = "central",
        step_calc     = "abs",
        out_stream    = None,
    )
    rec["fd_step"] = args.fdStep
    # RAW arrays only.  The aggregate is the GRADER's to compute.
    key = None
    for k in data:
        if "OBJ.val" in str(k) and "shapexUpper" in str(k):
            key = k
            break
    if key is None:
        rec["check_totals_error"] = "no (OBJ.val, shapexUpper) key in check_totals output; keys=%r" % [str(k) for k in data]
    else:
        d = data[key]
        for src_name, dst in (("J_fwd", "J_an"), ("J_rev", "J_an_rev"), ("J_fd", "J_fd")):
            if src_name in d:
                rec[dst] = [float(v) for v in np.atleast_1d(np.array(d[src_name]).ravel())]

else:
    print("task arg not found!")
    exit(1)

rec["status"] = "COMPLETE"
if MPI.COMM_WORLD.rank == 0:
    with open(args.out, "w") as f:
        json.dump(rec, f, indent=2, sort_keys=True)
    print("D9_JSON_WRITTEN: " + os.path.abspath(args.out))
