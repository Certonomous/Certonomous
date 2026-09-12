#!/usr/bin/env python
"""
CURRICULUM MP_A5 -- A5 U-BEND, 3D INCOMPRESSIBLE **MULTIPOINT** PRESSURE-LOSS
MINIMISATION OVER THREE INLET VELOCITIES (THREE REYNOLDS NUMBERS).

DERIVED FROM cases/dafoam/ladder-a/A5/curriculum_D9successor/d9succ_run_script.py.
The objective's PHYSICS, the design variable, the optimiser, the image and np are
carried from D9successor.  This item changes exactly three things:

  MPA5-1  THREE scenarios instead of one.  Three DAFoamBuilder instances, one per
      registered inlet speed U0 in {6.30, 8.40, 10.50} m/s, each with its own
      `primalBC` inlet value AND its own `normalizeStates` scaled by ITS OWN U0
      (a single shared normalisation would make the state scaling wrong for two
      of the three points).  Same mesh, same geometry component, same FFD, one
      shared `shapexUpper`.  This is SO3's proven construct
      (cases/dafoam/ladder-a/A1/curriculum_SO3/so3_runScript.py, mphys Multipoint
      + ScenarioAerodynamic + one shared OM_DVGEOCOMP + an ExecComp objective),
      transplanted from A1 2D to A5 3D.  SO3's construct ran to
      `EXIT: Optimal Solution Found.` on DASimpleFoam -- the SAME solver.

  MPA5-2  THE COMPOSITE OBJECTIVE.  J = sum_i w_i * (TP1_i - TP2_i) / n_i .
      The weights w_i are REGISTERED CONSTANTS.  The normalisers n_i are the
      BASELINE pressure losses measured in arm `B` of THIS chain at shape = 0,
      handed in through `-normFile`.  With n_i taken from the baseline and
      sum(w_i) = 1, J at the baseline design is EXACTLY 1.0 by construction --
      gate G-J0 grades that identity, so a mis-assembled objective cannot pass
      silently.  THE WEIGHTS AND NORMALISERS ARE COMPILED INTO THE ExecComp
      EXPRESSION STRING, and the exact string is written into the record as
      `obj_expr`, so a changed weight cannot leave a stale coefficient behind and
      the grader can rebuild the expression and compare it character for
      character (SO3's own lesson, so3_runScript.py:345-347).

  MPA5-3  THE MESH-QUALITY CONSTRAINT IS TAKEN FROM ONE SCENARIO, NOT THREE.
      All three scenarios deform the SAME mesh from the SAME shared geometry
      component, so their three `nonOrtho` KS values are the same number; three
      identical constraints would be one constraint written three times.  The
      registered constraint is `point1.aero_post.nonOrtho <= 70.0` (the centre
      scenario), carried byte-identical in bound and scaler from D9successor,
      which measured a raw endpoint maxNonOrth of 69.2937 under it.  All three
      values are RECORDED so gate G-NONORTHO-IDENTITY can prove they agree.

CARRIED IN UNCHANGED FROM D9successor, and not re-derived here:
  * ONLY `shapexUpper` is an optimiser design variable (D9-2): it is the only A5
    total derivative this lab has FD-verified.  The other five DV groups stay
    declared-but-commented so the departure reads as a diff.
  * THE PATCHED IMAGE IS THE ONE BOUGHT (dafoam-idwarp-rot:v1).  Stock is GATE
    FAIL on A5's OBJ.val wrt shapexUpper (2 sign flips), so an optimiser on the
    stock gradient would be driving on a broken derivative.
  * np = 1 THROUGHOUT.  Two independent reasons, both measured: A5's np=1
    re-verification localised the idx16 check_totals anomaly to the np=4 FD path;
    and defect D-B (the parallel reverse-AD operator is not the transpose
    Jacobian under decomposition) is structurally absent at one rank.
  * every graded quantity goes to JSON; NOTHING is graded from stdout (D9-3).
  * measured CPU affinity is written into the record, never inferred (D9-4).
  * the driver history recorder is BEST EFFORT and reaches no gate (D9-5).

PRIMAL CONFIGURATION.  This item runs at the A5P2 `P2` setting --
`system/fvSolution` SIMPLE `nNonOrthogonalCorrectors 0 -> 2` -- applied by the
launcher, not here.  A5P2 measured that this takes the U-bend `p` initRes from
2.056815e-04 to 1.448577e-08 (a factor of 14,199) while `TP1-TP2` moves by
8.0e-08 RELATIVE: the better-converged primal is the same answer, measured, not
assumed (cases/dafoam/ladder-a/A5/curriculum_A5P2/RESULTS.md).

SUBMISSIONS PARKED.  Nothing in this item is sent, filed or uploaded anywhere.
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
parser.add_argument("-optimizer", help="optimizer to use", type=str, default="SLSQP")
parser.add_argument("-task", help="type of run to do", type=str, default="run_driver")
parser.add_argument("-maxit", help="SLSQP major iteration limit", type=int, default=30)
parser.add_argument("-out", help="JSON record path", type=str, default="mpa5r_out.json")
parser.add_argument("-dvFile", help="JSON holding shapexUpper to load before the task", type=str, default="")
parser.add_argument("-normFile", help="JSON holding the three baseline normalisers", type=str, default="")
args = parser.parse_args()
gcomm = MPI.COMM_WORLD

# =============================================================================
# MPA5-1  THE REGISTERED SCENARIO SET.  Three inlet speeds, three weights.
# These five lines are the whole multipoint declaration; nothing below re-states
# them, and every assert here fails the run rather than defaulting.
# =============================================================================
SCENARIOS = ["point0", "point1", "point2"]
U0S       = [6.30, 8.40, 10.50]          # m/s, inlet x-velocity.  8.40 is the case's own
                                         # 0/U internalField (8.4 0 0); the flanks are +-25 %.
WEIGHTS   = [0.25, 0.50, 0.25]           # centre-weighted duty cycle, registered
NU        = 1.5e-5                       # constant/transportProperties: nu 0.0000150000000000

assert len(SCENARIOS) == len(U0S) == len(WEIGHTS) == 3, "the scenario set is three points"
assert abs(sum(WEIGHTS) - 1.0) < 1e-12, "registered weights must sum to exactly 1.0"
assert abs(U0S[1] - 8.40) < 1e-12, "the centre scenario must be the case's own 8.4 m/s"

# =============================================================================
# MPA5-4  ADDENDUM 1, 2026-09-12.  PER-SCENARIO `run_directory` ISOLATION.
#
# THE DEFECT THIS REPAIRS, MEASURED ON THIS ITEM'S OWN FIRST ARM.  MP_A5's arm B
# died at 56 s with
#     pyDAFoam Error: /mnt/0.0001 already exists, moving failed!
#     pyDAFoam.py:1543 in renameSolution(self.nSolvePrimals)
# Three `DASolver` instances shared ONE case directory, each carrying its OWN
# `solution_counter`, and each renamed its converged solution to the SAME
# `0.0001`.  point0 renamed and succeeded; point1 collided and raised.
#
# THIS IS NOT A NEW DEFECT AND NOT AN UPSTREAM ONE.  It is the exact SO-3aR
# failure, recorded verbatim at so3_runScript.py:253-277, and THE CURE IS THE
# LAB'S OWN: A2's D6R already carried it
# (d6r_opt_runScript.py:59 RUN_DIRS, :120 per-point gridFile, :138
# run_directory), SO3 ported it to A1 and ran clean.  MP_A5 was derived from
# D9successor, which is SINGLE-point and therefore never needed it, so the
# isolation was never carried in.  Cause class BOOKKEEPING/INSTRUMENT.
# It is exactly the integration risk this item's PREREGISTRATION section 6 item 1
# registered before compute.
#
# THE KEYS ARE DERIVED FROM `SCENARIOS`, NEVER SPELLED OUT.  A hand-written map
# is one more call site of the scenario label, and a scenario added above with no
# row here would silently fall back to the shared directory -- which is exactly
# the failure being repaired.
# =============================================================================
RUN_DIRS = {sc: "mp%d" % i for i, sc in enumerate(SCENARIOS)}
assert len(set(RUN_DIRS.values())) == len(SCENARIOS), "RUN_DIRS must be injective over SCENARIOS"
assert all(sc in RUN_DIRS for sc in SCENARIOS), "RUN_DIRS must be total over SCENARIOS"

# MPA5-2  the normalisers.  Absent -> all 1.0 (arm B, which MEASURES them).
if args.normFile:
    with open(args.normFile) as _f:
        _n = json.load(_f)["norms"]
    assert len(_n) == 3, "normFile must carry exactly three normalisers"
    for _v in _n:
        assert float(_v) > 0.0, "a normaliser must be strictly positive"
    NORMS = [float(v) for v in _n]
    NORM_SOURCE = os.path.abspath(args.normFile)
else:
    NORMS = [1.0, 1.0, 1.0]
    NORM_SOURCE = "NONE -- unnormalised (this is arm B, which measures the normalisers)"

# MPA5-2  the expression string, BUILT from the registered constants so a changed
# weight cannot leave a stale coefficient anywhere.  Recorded verbatim.
OBJ_TERMS = ["%.17g*(TP1_%d - TP2_%d)/%.17g" % (WEIGHTS[i], i, i, NORMS[i]) for i in range(3)]
OBJ_EXPR = "val = " + " + ".join(OBJ_TERMS)

# =============================================================================
# daOptions -- ONE PER SCENARIO.  Everything except the inlet speed and the
# U0-dependent state normalisation is byte-identical across the three.
# =============================================================================


def make_da_options(u0):
    return {
        "solverName": "DASimpleFoam",
        "designSurfaces": ["ubend"],
        "useAD": {"mode": "reverse"},
        "primalMinResTol": 1e-8,
        "primalMinResTolDiff": 1e7,
        "writeMinorIterations": True,
        "wallDistanceMethod": "daCustom",
        # MPA5-1  the ONLY physics difference between the three scenarios.
        "primalBC": {
            "useWallFunction": True,
            "U0": {"variable": "U", "patches": ["inlet"], "value": [u0, 0.0, 0.0]},
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
            # carried from D9successor: the whole-domain KS aggregate of the
            # per-face non-orthogonality angle, in DEGREES, a smooth OVER-bound
            # of the true max, so constraining KS <= 70 forces raw max <= 70.
            "nonOrtho": {
                "type": "meshQualityKS",
                "source": "allCells",
                "coeffKS": 1.0,
                "metric": "nonOrthoAngle",
                "scale": 1.0,
                "addToAdjoint": True,
            },
        },
        "adjStateOrdering": "cell",
        "adjEqnOption": {
            "gmresRelTol": 1e-5,
            "gmresTolDiff": 1e4,
            "pcFillLevel": 2,
            "jacMatReOrdering": "natural",
            "gmresMaxIters": 3000,
            "gmresRestart": 3000,
        },
        # MPA5-1  per-scenario state normalisation.  U and p scale with THIS
        # scenario's U0; a single shared U0 would mis-scale two of the three.
        "normalizeStates": {
            "U": u0,
            "p": (u0 * u0) / 2.0,
            "nuTilda": 1e-3,
            "phi": 1.0,
            "T": 300,
        },
        "inputInfo": {
            "aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]},
        },
    }


# MPA5-4  `gridFile` is now PER SCENARIO.  D6R's shape
# (d6r_opt_runScript.py:117-124): each point owns a full case copy and reads its
# mesh out of that copy, so no two IDWarp instances and no two DASolvers address
# the same directory.
def mesh_options_for(point):
    return {
        "gridFile": os.path.join(os.getcwd(), RUN_DIRS[point]),
        "fileType": "OpenFOAM",
        "symmetryPlanes": [],
    }


# =============================================================================
# Top class
# =============================================================================
class Top(Multipoint):
    def setup(self):
        # MPA5-1  one builder per scenario -- one DASolver per operating point --
        # MPA5-4  EACH IN ITS OWN `run_directory`.  They differ in `daOptions`
        # only through the inlet speed and the state normalisation, which are
        # boundary/scaling properties and not mesh properties; they do NOT share
        # a directory, because each DASolver carries its own `solution_counter`
        # and renames into `run_directory`.  Sharing one is what killed this
        # item's own first arm B, and SO-3aR's second arm before it.
        self.builders = []
        for i, sc in enumerate(SCENARIOS):
            b = DAFoamBuilder(
                make_da_options(U0S[i]),
                mesh_options_for(sc),
                scenario="aerodynamic",
                run_directory=RUN_DIRS[sc],
            )
            b.initialize(self.comm)
            self.builders.append(b)

        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])

        # one mesh component per scenario (each builder owns its own solver), but
        # ONE geometry component shared by all three -- that sharing is what makes
        # this a multipoint problem rather than three separate optimisations.
        for i, sc in enumerate(SCENARIOS):
            self.add_subsystem("mesh_" + sc, self.builders[i].get_mesh_coordinate_subsystem())

        self.add_subsystem("geometry", OM_DVGEOCOMP(file="FFD/UBendDuctFFDSym.xyz", type="ffd"))

        for i, sc in enumerate(SCENARIOS):
            self.mphys_add_scenario(sc, ScenarioAerodynamic(aero_builder=self.builders[i]))

        # the shared surface comes from point0's mesh.  Recorded here rather than
        # left implicit: the three meshes ARE the same points, and reading point0's
        # is a choice this file makes on purpose (SO3's so3_runScript.py:385-389).
        self.connect("mesh_%s.x_aero0" % SCENARIOS[0], "geometry.x_aero_in")
        for sc in SCENARIOS:
            self.connect("geometry.x_aero0", "%s.x_aero" % sc)

        # MPA5-2  the weighted, baseline-normalised composite objective.
        self.add_subsystem("OBJ", om.ExecComp(OBJ_EXPR))
        for i, sc in enumerate(SCENARIOS):
            self.connect("%s.aero_post.TP1" % sc, "OBJ.TP1_%d" % i)
            self.connect("%s.aero_post.TP2" % sc, "OBJ.TP2_%d" % i)

    def configure(self):
        super().configure()

        points_aero = self.mesh_point0.mphys_get_surface_mesh()
        self.geometry.nom_add_discipline_coords("aero", points_aero)
        pts = self.geometry.nom_getDVGeo().getLocalIndex(0)

        # ---------- setup DVs.  Carried byte-identical from D9successor. ----------
        indexList = []
        indexList.extend(pts[7:16, 1, :].flatten())
        PS = geo_utils.PointSelect("list", indexList)
        shapexUpper = self.geometry.nom_addLocalDV(dvName="shapexUpper", pointSelect=PS, axis="x")

        indexList = []
        indexList.extend(pts[7:16, 1, :].flatten())
        PS = geo_utils.PointSelect("list", indexList)
        shapeyUpper = self.geometry.nom_addLocalDV(dvName="shapeyUpper", pointSelect=PS, axis="y")

        indexList = []
        indexList.extend(pts[7:16, 1, :].flatten())
        PS = geo_utils.PointSelect("list", indexList)
        shapezUpper = self.geometry.nom_addLocalDV(dvName="shapezUpper", pointSelect=PS, axis="z")

        indexList = []
        indexList.extend(pts[7:16, 0, :].flatten())
        PS = geo_utils.PointSelect("list", indexList)
        shapexLower = self.geometry.nom_addLocalDV(dvName="shapexLower", pointSelect=PS, axis="x")

        indexList = []
        indexList.extend(pts[7:16, 0, :].flatten())
        PS = geo_utils.PointSelect("list", indexList)
        shapeyLower = self.geometry.nom_addLocalDV(dvName="shapeyLower", pointSelect=PS, axis="y")

        indexList = []
        indexList.extend(pts[7:16, 0, :].flatten())
        PS = geo_utils.PointSelect("list", indexList)
        shapezLower = self.geometry.nom_addLocalDV(dvName="shapezLower", pointSelect=PS, axis="z")

        self.dvs.add_output("shapexUpper", val=np.array([0] * shapexUpper))
        self.dvs.add_output("shapeyUpper", val=np.array([0] * shapeyUpper))
        self.dvs.add_output("shapezUpper", val=np.array([0] * shapezUpper))
        self.dvs.add_output("shapexLower", val=np.array([0] * shapexLower))
        self.dvs.add_output("shapeyLower", val=np.array([0] * shapeyLower))
        self.dvs.add_output("shapezLower", val=np.array([0] * shapezLower))

        self.connect("shapexUpper", "geometry.shapexUpper")
        self.connect("shapeyUpper", "geometry.shapeyUpper")
        self.connect("shapezUpper", "geometry.shapezUpper")
        self.connect("shapexLower", "geometry.shapexLower")
        self.connect("shapeyLower", "geometry.shapeyLower")
        self.connect("shapezLower", "geometry.shapezLower")

        # D9-2, carried: ONLY the FD-verified DV group is an optimiser design
        # variable.  The five lines below stay COMMENTED, not deleted.
        self.add_design_var("shapexUpper", lower=-0.04, upper=0.04, scaler=25.0)
        # self.add_design_var("shapeyUpper", lower=-0.04, upper=0.04, scaler=25.0)
        # self.add_design_var("shapezUpper", lower=-0.04, upper=0.04, scaler=25.0)
        # self.add_design_var("shapexLower", lower=-0.04, upper=0.04, scaler=25.0)
        # self.add_design_var("shapeyLower", lower=-0.04, upper=0.04, scaler=25.0)
        # self.add_design_var("shapezLower", lower=-0.04, upper=0.04, scaler=25.0)

        self.add_objective("OBJ.val", scaler=1.0)
        # MPA5-3  the mesh-quality inequality constraint, taken from the CENTRE
        # scenario because all three share one deformed mesh.  Bound and scaler
        # byte-identical to D9successor.
        self.add_constraint("%s.aero_post.nonOrtho" % SCENARIOS[1], upper=70.0, scaler=1.0)


# =============================================================================
# Problem Setup
# =============================================================================
prob = om.Problem(reports=None)
prob.model = Top()
prob.setup(mode="rev")
prob.driver = om.pyOptSparseDriver()
prob.driver.options["optimizer"] = args.optimizer

if args.optimizer == "SLSQP":
    prob.driver.opt_settings = {
        "ACC": 1.0e-5,
        "MAXIT": args.maxit,
        "IFILE": "opt_SLSQP.txt",
    }
elif args.optimizer == "IPOPT":
    prob.driver.opt_settings = {
        "tol": 1.0e-5,
        "constr_viol_tol": 1.0e-5,
        "max_iter": 100,
        "print_level": 5,
        "output_file": "opt_IPOPT.txt",
        "mu_strategy": "adaptive",
        "limited_memory_max_history": 10,
        "nlp_scaling_method": "none",
        "alpha_for_y": "full",
        "recalc_y": "yes",
    }
else:
    print("optimizer arg not valid!")
    exit(1)

prob.driver.options["debug_print"] = ["nl_cons", "objs", "desvars"]
prob.driver.options["print_opt_prob"] = True
prob.driver.hist_file = "OptView.hst"

if args.dvFile:
    with open(args.dvFile) as _f:
        _dv = json.load(_f)["shapexUpper"]
    prob.set_val("shapexUpper", np.array(_dv, dtype=float))
    print("MPA5R_DVFILE_LOADED: %s  n=%d  l2=%.10e" % (args.dvFile, len(_dv), float(np.linalg.norm(_dv))))

# =============================================================================
# The record.  Everything a gate reads is written here; nothing is graded from stdout.
# =============================================================================
rec = {
    "task": args.task,
    "maxit": args.maxit,
    "optimizer": args.optimizer,
    "sched_affinity": sorted(os.sched_getaffinity(0)),
    "scenarios": SCENARIOS,
    "run_dirs": RUN_DIRS,          # MPA5-4, addendum 1
    "U0s": U0S,
    "weights": WEIGHTS,
    "nu": NU,
    "norms": NORMS,
    "norm_source": NORM_SOURCE,
    "obj_expr": OBJ_EXPR,
    "status": "STARTED",
}


def _read_scenario_outputs(prob, rec):
    """Per-scenario TP1, TP2, dP and the KS constraint value.  REPORTED here;
    every verdict on them is the grader's."""
    tp1, tp2, dp, ks = [], [], [], []
    for sc in SCENARIOS:
        try:
            a = float(np.atleast_1d(prob.get_val("%s.aero_post.TP1" % sc))[0])
            b = float(np.atleast_1d(prob.get_val("%s.aero_post.TP2" % sc))[0])
            tp1.append(a)
            tp2.append(b)
            dp.append(a - b)
        except Exception as e:
            rec.setdefault("scenario_read_errors", []).append("%s TP: %r" % (sc, e))
        try:
            ks.append(float(np.atleast_1d(prob.get_val("%s.aero_post.nonOrtho" % sc))[0]))
        except Exception as e:
            rec.setdefault("scenario_read_errors", []).append("%s nonOrtho: %r" % (sc, e))
    rec["TP1"] = tp1
    rec["TP2"] = tp2
    rec["dP"] = dp
    rec["nonOrtho_KS"] = ks


if args.task == "run_driver":
    try:
        prob.driver.add_recorder(om.SqliteRecorder("mpa5r_hist.sql"))
        # MP_A5R-2  ADDENDUM 1.  `includes` was `["*"]`, carried byte-identical
        # from the SINGLE-point D9successor.  `["*"]` records EVERY variable at
        # every driver iteration, INCLUDING FULL FIELD ARRAYS, and at three
        # scenarios MP_A5's history reached **460 MB** -- against D9successor's
        # 105 MB for one scenario and SO3's **3.5 MB** for its own three-scenario
        # multipoint, i.e. **131x** the proven item's.  It is the thing that was
        # GROWING when MP_A5's arm O was OOM-killed at evaluation 33 of 33 after
        # 3556 s: a run that dies instantly tells you the limit is wrong, a run
        # that dies at evaluation 33 tells you something is accumulating.
        #
        # `[]` records NO extra variables; the driver's own desvars, objectives
        # and constraints are still recorded by their own flags, which is exactly
        # and only what this item reads back.
        #
        # WHY NOT SO3's PROBLEM-RECORDER PATTERN VERBATIM, which was the shape
        # suggested: SO3 uses `prob.add_recorder(...)` and reads its history its
        # own way.  THE GRADING PATH OF THIS ITEM IS FROZEN and its reader is
        # `om.CaseReader(...).list_cases("driver")` (mpa5r_grade.py, the
        # `obj_history` field).  A problem recorder leaves `list_cases("driver")`
        # EMPTY, so adopting that pattern would silently blank a field the frozen
        # comparator reads -- and the frozen file may not be edited to suit it
        # (rule 6).  Dropping `["*"]` fixes the whole defect, is a one-token
        # change, and leaves every frozen reader working.  Recorded here rather
        # than done quietly, because it departs from the shape asked for.
        prob.driver.recording_options["includes"] = []
    except Exception as e:
        # MP_A5R-5  ADDENDUM 2.  THIS WAS `rec["recorder_error"] = repr(e)` AND THE
        # ARM RAN ON.  Sanaa 2026-09-12 checkpoint item 2: "Every optimization
        # writes its history and design vector every iteration and can hot-start
        # from them."  A history that is ALLOWED to be absent is not a checkpoint.
        # An optimiser that has run for hours with a silently dead recorder has
        # nothing to resume from and nothing notices.  REFUSING TO START IS NOT A
        # CAP: it never signals, throttles or shortens anything already running.
        rec["recorder_error"] = repr(e)
        rec["status"] = "REFUSED_NO_RECORDER"
        if MPI.COMM_WORLD.rank == 0:
            with open(args.out, "w") as f:
                json.dump(rec, f, indent=2, sort_keys=True)
            print("MPA5R_REFUSE: driver recorder could not be attached: %r" % (e,))
        exit(3)

    # MP_A5R-5  ADDENDUM 2 -- HOT START.  pyOptSparse restarts from ITS OWN `.hst`
    # history, reached through the driver's `hist_file` / `hotstart_file`
    # attributes.  An OpenMDAO SqliteRecorder is a RECORD, not a RESTART, and
    # cannot feed it; `mpa5r_hist.sql` never could.  This is the identical defect
    # the 2026-09-12 census found in D6R2, which lost twelve completed design
    # iterations at the reboot for exactly this reason.
    #
    # hist_file is set UNCONDITIONALLY -- writing the history is not optional.
    # hotstart_file is set ONLY when a history is already on disk, so a hot start
    # is an explicit act on a pre-populated tree and never an accident on a fresh
    # one.  WHICH BRANCH WAS TAKEN IS RECORDED, so the record can never be read as
    # a cold start that silently resumed, or a resume that silently cold-started.
    _hst = os.path.abspath("mpa5r_opt.hst")
    prob.driver.hist_file = _hst
    rec["opt_hist_file"] = _hst
    if os.path.exists(_hst):
        prob.driver.hotstart_file = _hst
        rec["hot_start"] = True
        rec["hot_start_bytes_at_entry"] = os.path.getsize(_hst)
    else:
        rec["hot_start"] = False

    failed = prob.run_driver()
    rec["driver_failed"] = bool(failed)
    rec["driver_iter_count"] = int(getattr(prob.driver, "iter_count", -1))
    try:
        prob.cleanup()
        cr = om.CaseReader("mpa5r_hist.sql")
        cs = cr.list_cases("driver", out_stream=None)
        rec["obj_history"] = [
            float(np.atleast_1d(cr.get_case(c).get_objectives()["OBJ.val"])[0]) for c in cs
        ]
    except Exception as e:
        rec["hist_error"] = repr(e)
    rec["OBJ_val"] = float(np.atleast_1d(prob.get_val("OBJ.val"))[0])
    rec["shapexUpper"] = [float(v) for v in np.atleast_1d(prob.get_val("shapexUpper"))]
    _read_scenario_outputs(prob, rec)

elif args.task == "run_model":
    prob.run_model()
    rec["OBJ_val"] = float(np.atleast_1d(prob.get_val("OBJ.val"))[0])
    rec["shapexUpper"] = [float(v) for v in np.atleast_1d(prob.get_val("shapexUpper"))]
    _read_scenario_outputs(prob, rec)

else:
    print("task arg not found!")
    exit(1)

rec["status"] = "COMPLETE"
if MPI.COMM_WORLD.rank == 0:
    with open(args.out, "w") as f:
        json.dump(rec, f, indent=2, sort_keys=True)
    print("MPA5R_JSON_WRITTEN: " + os.path.abspath(args.out))
