#!/usr/bin/env python
"""Curriculum D6 -- multipoint cruise on D4's case: three CL targets, one geometry,
weighted composite objective.  DERIVED FROM curriculum_D4/d4_opt_runScript.py
(md5 2906d52a5dbed2bacbaeaf85a37d3fe8) with the REGISTERED DELTAS of
PREREGISTRATION.md section 1 and no other:
  * three ScenarioAerodynamic scenarios cl04 / cl05 / cl06 (CL targets 0.4 / 0.5 /
    0.6), each with its OWN DAFoamBuilder in its OWN run_directory mp04/ mp05/
    mp06/ (a full copy of the case, staged by the launcher), its own mesh and
    geometry components, its own patchV<k> (AoA) design variable and its own CL
    equality constraint;
  * ONE set of shape/twist design variables, connected to all three geometries;
    the geometric constraints (thickness, volume, LE/TE) are taken from the
    cl05 geometry only -- the three geometries are the same FFD on the same
    surface, so a second copy of each constraint would be the same constraint;
  * the objective is the composite J = 0.25*CD04 + 0.50*CD05 + 0.25*CD06
    (weights FROZEN in PREREGISTRATION.md section 1; a second weight set is a
    new item), formed by an ExecComp;
  * findFeasibleDesign solves the three CL targets on the three patchV DVs at
    once before run_driver (the DAFoam multipoint form).
daOptions, meshOptions, the DV bounds and scalers, IPOPT settings and the task
switch are D4's bytes.  The ANCHOR line `# OpenMDAO setup` is kept so that
d6r2_fd_endpoint.py and d6r2_ref_off.py exec the header exactly as D4's FD
instrument does.

D6R2C REGISTERED DELTAS from d6r2_opt_runScript.py (md5
0abba50ab8baeefa3f59a3f1fc8f5336), and NO OTHERS.  Every one of them exists to
satisfy a numbered item of Sanaa's 2026-09-12 run instruction; none of them
touches the physics, the mesh, the weights, the targets, the constraints, the
solver, the tolerances or the design variables.

  D1 (her Checkpoints item 2 -- "every optimization writes its history and the
      design vector every iteration and can hot-start from them").
      `-hotstart <file>` sets pyOptSparseDriver.hotstart_file.  pyoptsparse
      2.10.1 `_setHistory` (pyOpt_optimizer.py:145-199) then restores the
      initial design vector from call counter 0 of that history and
      `_masterFunc2` (:232-299) replays every cached evaluation whose x matches
      to numpy EPS, writing the exact cached dictionary back into the new
      history.  The history itself (`hist_file`, already D6R2's bytes) IS the
      per-iteration design-vector record.
  D2  A JSONL line per REAL (non-replayed) evaluation and per gradient:
      objective, every constraint, the full design vector, fail flag and wall
      seconds.  Written by a driver SUBCLASS that calls super() FIRST and
      records AFTER, so it cannot alter a number it observes.  Rank 0 only.
  D3  `-max_iter` (default 25, the REGISTERED PRODUCTION CAP).  The ONLY
      registered non-default use is the kill-and-resume proof at 4.  The value
      actually used is written into the JSONL header line, so no reader has to
      trust the flag.
  D4  On a cold start the design vector AFTER findFeasibleDesign is written to
      `d6r2c_x0.json`.  On a hot start findFeasibleDesign is SKIPPED (its
      result is already call counter 0 of the history) and the script REFUSES
      before any compute if the history's call-0 design vector does not match
      the staged `d6r2c_x0.json` to 1e-12.  A restart that silently began from
      a different point is the failure this guard exists to make impossible.
"""
import os
import sys
import json
import time
import argparse
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder, OptFuncs
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP
from pygeo import geo_utils

parser = argparse.ArgumentParser()
# which optimizer to use. Options are: IPOPT (default), SLSQP, and SNOPT
parser.add_argument("-optimizer", help="optimizer to use", type=str, default="IPOPT")
# which task to run. Options are: run_driver (default), run_model, compute_totals, check_totals
parser.add_argument("-task", help="type of run to do", type=str, default="run_driver")
# ---- D6R2C DELTA D3: the iteration budget is a CAP, not a tolerance.  25 is
# ---- the REGISTERED PRODUCTION VALUE; 4 is the registered kill-and-resume
# ---- proof value.  Any other value is outside the freeze.
parser.add_argument("-max_iter", help="IPOPT major iteration CAP (registered: 25 production, 4 KR proof)",
                    type=int, default=25)
# ---- D6R2C DELTA D1: hot start.  Empty string = cold start.
parser.add_argument("-hotstart", help="pyoptsparse history file to hot-start from ('' = cold)",
                    type=str, default="")
args = parser.parse_args()

if args.max_iter not in (25, 4):
    print("D6R2C REFUSE: -max_iter %d is outside the freeze (25 production, 4 KR proof)." % args.max_iter)
    sys.exit(70)

HOTSTART = args.hotstart.strip()
COLD = (HOTSTART == "")
EVAL_LOG = "d6r2c_evals.jsonl"
X0_FILE = "d6r2c_x0.json"
X0_MATCH_TOL = 1.0e-12   # REGISTERED (PREREGISTRATION.md section 5)

# =============================================================================
# Input Parameters
# =============================================================================

U0 = 100.0
p0 = 101325.0
nuTilda0 = 4.5e-5
T0 = 300.0
aoa0 = 4.0
rho0 = p0 / T0 / 287.0
A0 = 45.5

# ---- D6 REGISTERED DELTA: the three points, their targets and their FROZEN weights
POINTS = ["cl04", "cl05", "cl06"]
CL_TARGETS = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}
WEIGHTS = {"cl04": 0.25, "cl05": 0.50, "cl06": 0.25}
RUN_DIRS = {"cl04": "mp04", "cl05": "mp05", "cl06": "mp06"}

daOptions = {
    "designSurfaces": ["wing"],
    "solverName": "DARhoSimpleFoam",
    "primalMinResTol": 1.0e-8,
    "primalMinResTolDiff": 1e3,
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
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 1, "jacMatReOrdering": "rcm"},
    "normalizeStates": {
        "U": U0,
        "p": U0 * U0 / 2.0,
        "T": T0,
        "nuTilda": 1e-3,
        "phi": 1.0,
    },
    "checkMeshThreshold": {
        "maxAspectRatio": 1000.0,
        "maxNonOrth": 70.0,
        "maxSkewness": 5.0,
    },
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


def mesh_options_for(point):
    # Mesh deformation setup, per run directory (each point owns a full case copy)
    return {
        "gridFile": os.path.join(os.getcwd(), RUN_DIRS[point]),
        "fileType": "OpenFOAM",
        # point and normal for the symmetry plane
        "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]]],
    }


# Top class to setup the optimization problem
class Top(Multipoint):
    def setup(self):

        # add the design variable component to keep the top level design variables
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])

        self.builders = {}
        for pt in POINTS:
            # one builder per point, in its own run directory
            b = DAFoamBuilder(daOptions, mesh_options_for(pt), scenario="aerodynamic",
                              run_directory=RUN_DIRS[pt])
            b.initialize(self.comm)
            self.builders[pt] = b
            # mesh and geometry (FFD) components for this point
            self.add_subsystem("mesh_" + pt, b.get_mesh_coordinate_subsystem())
            self.add_subsystem("geometry_" + pt, OM_DVGEOCOMP(file="FFD/wingFFD.xyz", type="ffd"))
            # the scenario (flow condition)
            self.mphys_add_scenario(pt, ScenarioAerodynamic(aero_builder=b))
            self.connect("mesh_%s.x_aero0" % pt, "geometry_%s.x_aero_in" % pt)
            self.connect("geometry_%s.x_aero0" % pt, "%s.x_aero" % pt)

        # the composite objective (weights FROZEN)
        self.add_subsystem("obj", om.ExecComp(
            "J = %r * CD04 + %r * CD05 + %r * CD06" % (WEIGHTS["cl04"], WEIGHTS["cl05"], WEIGHTS["cl06"])))
        self.connect("cl04.aero_post.CD", "obj.CD04")
        self.connect("cl05.aero_post.CD", "obj.CD05")
        self.connect("cl06.aero_post.CD", "obj.CD06")

    def configure(self):

        nRefAxPts = None
        nShapes = None
        for pt in POINTS:
            mesh = getattr(self, "mesh_" + pt)
            geometry = getattr(self, "geometry_" + pt)
            # get the surface coordinates from the mesh component
            points = mesh.mphys_get_surface_mesh()
            # add pointset to the geometry component
            geometry.nom_add_discipline_coords("aero", points)
            # set the triangular points to the geometry component for geometric constraints
            tri_points = mesh.mphys_get_triangulated_surface()
            geometry.nom_setConstraintSurface(tri_points)
            # Create reference axis for the twist variable
            n = geometry.nom_addRefAxis(name="wingAxis", xFraction=0.25, alignIndex="k")
            if nRefAxPts is None:
                nRefAxPts = n
            elif n != nRefAxPts:
                raise RuntimeError("D6 REFUSE: ref-axis point count differs between points (%d vs %d)" % (n, nRefAxPts))

            # Set up global design variables. We dont change the root twist
            def twist(val, geo, _n=nRefAxPts):
                for i in range(1, _n):
                    geo.rot_z["wingAxis"].coef[i] = -val[i - 1]

            # add twist variable
            geometry.nom_addGlobalDV(dvName="twist", value=np.array([0] * (nRefAxPts - 1)), func=twist)

            # select the FFD points to move
            pts = geometry.DVGeo.getLocalIndex(0)
            indexList = pts[:, :, :].flatten()
            PS = geo_utils.PointSelect("list", indexList)
            ns = geometry.nom_addLocalDV(dvName="shape", pointSelect=PS)
            if nShapes is None:
                nShapes = ns
            elif ns != nShapes:
                raise RuntimeError("D6 REFUSE: shape DV count differs between points (%d vs %d)" % (ns, nShapes))

        # setup the volume and thickness constraints on the cl05 geometry (one geometry, one set)
        leList = [[0.1, 0, 0.01], [7.5, 0, 13.9]]
        teList = [[4.9, 0, 0.01], [8.9, 0, 13.9]]
        self.geometry_cl05.nom_addThicknessConstraints2D("thickcon", leList, teList, nSpan=10, nChord=10)
        self.geometry_cl05.nom_addVolumeConstraint("volcon", leList, teList, nSpan=10, nChord=10)
        # add the LE/TE constraints
        self.geometry_cl05.nom_add_LETEConstraint("lecon", volID=0, faceID="iLow")
        self.geometry_cl05.nom_add_LETEConstraint("tecon", volID=0, faceID="iHigh")

        # add the design variables to the dvs component's output
        self.dvs.add_output("twist", val=np.array([0] * (nRefAxPts - 1)))
        self.dvs.add_output("shape", val=np.array([0] * nShapes))
        for pt in POINTS:
            self.dvs.add_output("patchV_" + pt, val=np.array([U0, aoa0]))
            # manually connect the dvs output to the geometry and the scenario
            self.connect("twist", "geometry_%s.twist" % pt)
            self.connect("shape", "geometry_%s.shape" % pt)
            self.connect("patchV_" + pt, "%s.patchV" % pt)

        # define the design variables
        self.add_design_var("twist", lower=-10.0, upper=10.0, scaler=0.1)
        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)
        for pt in POINTS:
            self.add_design_var("patchV_" + pt, lower=[U0, 0.0], upper=[U0, 10.0], scaler=0.1)

        # add objective and constraints to the top level
        self.add_objective("obj.J", scaler=1.0)
        for pt in POINTS:
            self.add_constraint("%s.aero_post.CL" % pt, equals=CL_TARGETS[pt], scaler=1.0)
        self.add_constraint("geometry_cl05.thickcon", lower=0.5, upper=3.0, scaler=1.0)
        self.add_constraint("geometry_cl05.volcon", lower=1.0, scaler=1.0)
        self.add_constraint("geometry_cl05.tecon", equals=0.0, scaler=1.0, linear=True)
        self.add_constraint("geometry_cl05.lecon", equals=0.0, scaler=1.0, linear=True)


# OpenMDAO setup
prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")
om.n2(prob, show_browser=False, outfile="mphys.html")

# initialize the optimization function (one daOptions per point, the multipoint form)
optFuncs = OptFuncs([daOptions] * len(POINTS), prob)

# ===========================================================================
# D6R2C DELTA D2 -- THE PER-EVALUATION RECORD.
# The subclass calls super() FIRST and records AFTER.  It has no branch that
# can change a returned value, and it writes on rank 0 only.  A replayed
# (hot-started) evaluation never reaches here -- pyoptsparse serves it from
# its cache inside _masterFunc2 -- so a line in this file is proof that the
# primal actually RAN for that point.  That asymmetry is the point: it is how
# the comparator tells a genuine replay from a silent cold restart.
# ===========================================================================
_RANK0 = (MPI.COMM_WORLD.rank == 0)
_T_START = time.time()


def _jsonable(v):
    if isinstance(v, np.ndarray):
        return [float(x) for x in v.flatten()]
    if isinstance(v, (np.floating, np.integer)):
        return float(v)
    if isinstance(v, dict):
        return {str(k): _jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    return v


def _emit(row):
    if not _RANK0:
        return
    row["utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    row["wall_since_start_s"] = round(time.time() - _T_START, 3)
    with open(EVAL_LOG, "a") as fh:
        fh.write(json.dumps(_jsonable(row), sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


class D6R2C_Driver(om.pyOptSparseDriver):
    """D6R2's driver plus an observer.  super() first, record after."""

    def _objfunc(self, dv_dict):
        t0 = time.time()
        func_dict, fail = super()._objfunc(dv_dict)
        _emit({"kind": "F", "n": getattr(self, "iter_count", None), "fail": int(fail),
               "eval_wall_s": round(time.time() - t0, 3),
               "dv": dict(dv_dict), "funcs": dict(func_dict)})
        return func_dict, fail

    def _gradfunc(self, dv_dict, func_dict):
        t0 = time.time()
        sens_dict, fail = super()._gradfunc(dv_dict, func_dict)
        _emit({"kind": "G", "n": getattr(self, "iter_count", None), "fail": int(fail),
               "eval_wall_s": round(time.time() - t0, 3),
               "dv": dict(dv_dict), "funcs": dict(func_dict)})
        return sens_dict, fail


# use pyoptsparse to setup optimization
prob.driver = D6R2C_Driver()
prob.driver.options["optimizer"] = args.optimizer
# options for optimizers
if args.optimizer == "SNOPT":
    prob.driver.opt_settings = {
        "Major feasibility tolerance": 1.0e-5,
        "Major optimality tolerance": 1.0e-5,
        "Minor feasibility tolerance": 1.0e-5,
        "Verify level": -1,
        "Function precision": 1.0e-5,
        "Major iterations limit": 100,
        "Nonderivative linesearch": None,
        "Print file": "opt_SNOPT_print.txt",
        "Summary file": "opt_SNOPT_summary.txt",
    }
elif args.optimizer == "IPOPT":
    prob.driver.opt_settings = {
        "tol": 1.0e-5,
        "constr_viol_tol": 1.0e-5,
        "max_iter": args.max_iter,
        "print_level": 5,
        "output_file": "opt_IPOPT.txt",
        "mu_strategy": "adaptive",
        "limited_memory_max_history": 10,
        "nlp_scaling_method": "none",
        "alpha_for_y": "full",
        "recalc_y": "yes",
    }
elif args.optimizer == "SLSQP":
    prob.driver.opt_settings = {
        "ACC": 1.0e-5,
        "MAXIT": 100,
        "IFILE": "opt_SLSQP.txt",
    }
else:
    print("optimizer arg not valid!")
    exit(1)

prob.driver.options["debug_print"] = ["nl_cons", "objs", "desvars"]
prob.driver.options["print_opt_prob"] = True
prob.driver.hist_file = "OptView.hst"

# ---- D6R2C DELTA D1 -- HOT START ------------------------------------------
if not COLD:
    if not os.path.exists(HOTSTART):
        print("D6R2C REFUSE: -hotstart %s does not exist." % HOTSTART)
        sys.exit(71)
    prob.driver.hotstart_file = HOTSTART
    print("D6R2C_HOTSTART_FILE: %s" % HOTSTART)
print("D6R2C_MODE: %s  max_iter=%d" % ("COLD" if COLD else "HOT", args.max_iter))
_emit({"kind": "HEADER", "mode": "COLD" if COLD else "HOT", "max_iter": args.max_iter,
       "hotstart_file": HOTSTART, "ranks": MPI.COMM_WORLD.size,
       "points": POINTS, "cl_targets": CL_TARGETS, "weights": WEIGHTS,
       "uid": os.getuid(), "gid": os.getgid()})
if os.getuid() == 0:
    print("D6R2C REFUSE: running as uid 0. Sanaa's Launch item 6: as ubuntu, NEVER root.")
    sys.exit(72)


def _dv_snapshot():
    d = {"twist": prob.get_val("twist"), "shape": prob.get_val("shape")}
    for pt in POINTS:
        d["patchV_" + pt] = prob.get_val("patchV_" + pt)
    return _jsonable(d)


def _hotstart_x0_guard():
    """D6R2C DELTA D4.  REFUSE, BEFORE ANY COMPUTE, if the history we are about
    to hot-start from did not begin where the cold reference began.  pyoptsparse
    restores x0 from call counter 0 of this same file, so a mismatch here means
    the resumed run would silently be a different optimisation."""
    if not os.path.exists(X0_FILE):
        print("D6R2C REFUSE: hot start without a staged %s to check the history against." % X0_FILE)
        sys.exit(73)
    ref = json.load(open(X0_FILE))["dv"]
    from pyoptsparse.pyOpt_history import History
    h = History(HOTSTART, temp=False, flag="r")
    got = h.getValues(names=h.getDVNames(), callCounters=[0], major=False, allowSens=True)
    h.close()
    worst = 0.0
    seen = []
    for k, v in ref.items():
        cand = [n for n in got if n == k or n.endswith("." + k) or n.split(".")[-1] == k]
        if not cand:
            print("D6R2C REFUSE: history call-0 has no design variable matching %r (has %r)"
                  % (k, sorted(got)))
            sys.exit(73)
        g = np.asarray(got[cand[0]]).flatten()
        r = np.asarray(v, dtype=float).flatten()
        if g.size != r.size:
            print("D6R2C REFUSE: %s size %d in history vs %d in %s" % (k, g.size, r.size, X0_FILE))
            sys.exit(73)
        d = float(np.max(np.abs(g - r))) if r.size else 0.0
        seen.append((k, d))
        worst = max(worst, d)
    print("D6R2C_X0_GUARD worst_abs_diff=%.3e tol=%.1e per_dv=%s"
          % (worst, X0_MATCH_TOL, ";".join("%s:%.3e" % t for t in seen)))
    if worst > X0_MATCH_TOL:
        print("D6R2C REFUSE: hot-start history call-0 design vector differs from the cold "
              "reference x0 by %.3e > %.1e." % (worst, X0_MATCH_TOL))
        sys.exit(73)
    _emit({"kind": "X0_GUARD", "worst_abs_diff": worst, "tol": X0_MATCH_TOL,
           "per_dv": dict(seen), "hotstart_file": HOTSTART})


if args.task == "run_driver":
    if COLD:
        # solve the three CL targets on the three patchV DVs at once
        optFuncs.findFeasibleDesign(["%s.aero_post.CL" % pt for pt in POINTS],
                                    ["patchV_" + pt for pt in POINTS],
                                    targets=[CL_TARGETS[pt] for pt in POINTS],
                                    designVarsComp=[1] * len(POINTS))
        # D6R2C DELTA D4: the trimmed starting point IS the optimisation's x0,
        # and a restart must be able to prove it began there.
        if _RANK0:
            with open(X0_FILE, "w") as fh:
                json.dump({"dv": _dv_snapshot(),
                           "note": "design vector AFTER findFeasibleDesign; this is IPOPT's x0"},
                          fh, indent=1, sort_keys=True)
                fh.flush()
                os.fsync(fh.fileno())
        MPI.COMM_WORLD.Barrier()
    else:
        # D6R2C DELTA D4: findFeasibleDesign is NOT re-run.  Its result is call
        # counter 0 of the history pyoptsparse is about to restore x0 from, and
        # the guard below refuses if that is not where the cold run started.
        _hotstart_x0_guard()
    # run the optimization
    prob.run_driver()
elif args.task == "run_model":
    # just run the primal once
    prob.run_model()
elif args.task == "compute_totals":
    # just run the primal and adjoint once
    prob.run_model()
    totals = prob.compute_totals()
    if MPI.COMM_WORLD.rank == 0:
        print(totals)
elif args.task == "check_totals":
    # verify the total derivatives against the finite-difference
    prob.run_model()
    prob.check_totals(compact_print=False, step=1e-3, form="central", step_calc="abs")
else:
    print("task arg not found!")
    exit(1)
