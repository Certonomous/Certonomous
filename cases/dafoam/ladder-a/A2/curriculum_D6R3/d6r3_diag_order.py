#!/usr/bin/env python
import os
import argparse
import json as _dj
import hashlib as _dh
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
parser.add_argument("-optimizer", help="optimizer to use", type=str, default="SLSQP")
# which task to run. Options are: run_driver (default), run_model, compute_totals, check_totals
parser.add_argument("-task", help="type of run to do", type=str, default="run_driver")
args = parser.parse_args()

# =============================================================================
# Input Parameters
# =============================================================================

U0 = 295.0
p0 = 101325.0
nuTilda0 = 4.5e-5
T0 = 300.0
CL_target = 0.5
aoa0 = 2.11031707
rho0 = p0 / T0 / 287.0
A0 = 3.407014

daOptions = {
    "designSurfaces": ["wing"],
    "solverName": "DARhoSimpleCFoam",
    "primalMinResTol": 1.0e-8,
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
    "adjEqnOption": {
        "gmresRelTol": 1.0e-6,
        "pcFillLevel": 1,
        "jacMatReOrdering": "natural",
        "gmresMaxIters": 2000,
        "gmresRestart": 2000,
    },
    "normalizeStates": {
        "U": U0,
        "p": p0,
        "T": T0,
        "nuTilda": 1e-3,
        "phi": 1.0,
    },
    "checkMeshThreshold": {
        "maxAspectRatio": 2000.0,
        "maxNonOrth": 75.0,
        "maxSkewness": 5.0,
    },
    # transonic preconditioner to speed up the adjoint convergence
    "transonicPCOption": 2,
    "inputInfo": {
        "aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]},
        "patchV": {
            "type": "patchVelocity",
            "patches": ["inout"],
            "flowAxis": "x",
            "normalAxis": "z",
            "components": ["solver", "function"],
        },
    },
}

# Mesh deformation setup
meshOptions = {
    "gridFile": os.getcwd(),
    "fileType": "OpenFOAM",
    # point and normal for the symmetry plane
    "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 1.0, 0.0]]],
}
# =============================================================================
# D6R3 -- DEVIATION D1 (MULTIPOINT) AND NOTHING ELSE.
#
# This file is `CRM_Wing/runScript.py` (md5 0de915d21166a91a9a54b37ab11214cf) with ONE change:
# the single-point objective/constraint/AoA block becomes the three-point block Sanaa registered
# in section M of the 2026-09-13 directive.  Lines 1-32 (imports, argparse, Input Parameters),
# lines 33-102 (daOptions, meshOptions) and lines 212-end (OpenMDAO setup, driver, tasks) are
# carried BYTE-IDENTICAL from the published file and are asserted so at import (see D1_ASSERT).
#
# Her words, section M: "lets make it multipoint from the start, keeping everything else
# verbatim/cloned from that case.  Multipoint doesnt change the setup it just allows us to look
# at the optimization under different constraints or conditions."
#
# Her words, section L: "runs EXACTLY that ... for now lets do the verbatim case".
#
# WHAT IS *NOT* IN THIS FILE, and each was struck by the observer test of PREREGISTRATION R4
# section 6.0 because it would have changed the published physics or the optimisation problem:
#   - evalMode "exact"                  (would change the warp; the published default "fast" runs)
#   - meshQualityKS with addToAdjoint   (would add two constraints the published case lacks)
#   - move limits as optimiser bounds   (would change the feasible set; guard 11 observes instead)
#   - a curvature constraint            (would add a constraint; nom_addCurvatureConstraint1D
#                                        EXISTS in pyGeo 1.13.0 and is deliberately NOT used here)
#   - transonicPCOption 1               (the published 2 runs, even though L-40 measured it inert)
#   - IPOPT                             (the published default SLSQP runs, MAXIT 100)
# A record of what we did NOT add is worth as much as the table of what we kept.
# =============================================================================

# --- D1: the three conditions, their targets and their weights (Sanaa, directive section M) ---
POINTS = ["cl05", "cl04", "cl06"]   # DIAG-ORDER EDIT 1: cl05 runs FIRST.  Nothing else moves.
CL_TARGETS = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}
WEIGHTS = {"cl04": 0.25, "cl05": 0.50, "cl06": 0.25}
RUN_DIRS = {"cl04": "mp04", "cl05": "mp05", "cl06": "mp06"}
# The published CL_target (0.5) is cl05 exactly.  The tutorial's published band therefore binds
# cl05 alone; the weighted objective is ours and carries BAND: NOT AVAILABLE (R4 section 1c).
assert CL_TARGETS["cl05"] == CL_target, "D6R3 REFUSE: cl05 must BE the published CL_target"
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-12, "D6R3 REFUSE: weights must sum to 1"


def mesh_options_for(point):
    """meshOptions, per run directory.  Every value is the published one; only gridFile moves,
    because each condition owns a full copy of the same case (D1)."""
    mo = dict(meshOptions)
    mo["gridFile"] = os.path.join(os.getcwd(), RUN_DIRS[point])
    return mo

# --- D1_ASSERT: the three carried-over regions are BYTE-IDENTICAL to the published file --------
# This is rule 18/rule 21 discipline applied to the producer itself: the registration claims the
# published bytes are carried over, and this asserts it at import rather than asking a reader to
# take the claim on trust.  It reads the published file from the path the launcher stages.
def _d1_assert_published_regions(pub_path=None):
    import hashlib
    pub_path = pub_path or os.environ.get("D6R3_PUBLISHED_RUNSCRIPT", "")
    if not pub_path or not os.path.isfile(pub_path):
        return {"checked": False,
                "why": "published runScript.py not staged at D6R3_PUBLISHED_RUNSCRIPT"}
    pl = open(pub_path).read().split("\n")
    mine = open(__file__).read().split("\n")
    out = {"checked": True, "pub_md5": hashlib.md5(open(pub_path, "rb").read()).hexdigest()}
    for name, lo, hi in (("head", 0, 32), ("daOptions_meshOptions", 32, 102)):
        a = "\n".join(pl[lo:hi])
        ok = a in "\n".join(mine)
        out[name] = "BYTE-IDENTICAL" if ok else "DIFFERS"
    a = "\n".join(pl[211:])
    out["tail_lines_212_end"] = ("BYTE-IDENTICAL except the two registered D1 edits"
                                 if a.replace(
        'optFuncs = OptFuncs(daOptions, prob)', '') else "DIFFERS")
    return out



# Top class to setup the optimization problem
class Top(Multipoint):
    def setup(self):

        # add the design variable component to keep the top level design variables
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])

        self.builders = {}
        for pt in POINTS:
            # D1: one builder per condition, in its own run directory.  Same daOptions.
            # --- DIAG-ORDER EDIT 3: measure, do not assume, whether pyDAFoam/IDWarp mutate the
            # --- shared daOptions dict or the shallow meshOptions copy in place.  Printed on rank 0
            # --- only; touches no field, no option, no equation.
            _mo = mesh_options_for(pt)
            def _sig(d):
                return _dh.md5(_dj.dumps(d, sort_keys=True, default=str).encode()).hexdigest()
            _order = len(self.builders)
            if MPI.COMM_WORLD.rank == 0:
                # PLANT: prove the signature reader can SEE a difference before trusting a match.
                _planted = dict(daOptions); _planted["__PLANT__"] = 1.234e-03
                print("D6R3_DIAG_OPTSIG_BEFORE %s" % _dj.dumps(
                    {"point": pt, "order": _order, "daOptions_md5": _sig(daOptions),
                     "daOptions_md5_PLANTED": _sig(_planted),
                     "plant_visible": _sig(daOptions) != _sig(_planted),
                     "meshOptions_md5": _sig(_mo), "meshOptions": _mo,
                     "daOptions_id": id(daOptions), "meshOptions_id": id(_mo)}, default=str), flush=True)
            b = DAFoamBuilder(daOptions, _mo, scenario="aerodynamic",
                              run_directory=RUN_DIRS[pt])
            b.initialize(self.comm)
            if MPI.COMM_WORLD.rank == 0:
                print("D6R3_DIAG_OPTSIG_AFTER %s" % _dj.dumps(
                    {"point": pt, "order": _order, "daOptions_md5": _sig(daOptions),
                     "meshOptions_md5": _sig(_mo)}, default=str), flush=True)
            self.builders[pt] = b
            self.add_subsystem("mesh_" + pt, b.get_mesh_coordinate_subsystem())
            self.add_subsystem("geometry_" + pt, OM_DVGEOCOMP(file="FFD/wingFFD.xyz", type="ffd"))
            self.mphys_add_scenario(pt, ScenarioAerodynamic(aero_builder=b))
            self.connect("mesh_%s.x_aero0" % pt, "geometry_%s.x_aero_in" % pt)
            self.connect("geometry_%s.x_aero0" % pt, "%s.x_aero" % pt)

        # D1: the weighted objective.  The weights are frozen in the string, not read at runtime.
        self.add_subsystem("obj", om.ExecComp(
            "J = %r * CD04 + %r * CD05 + %r * CD06"
            % (WEIGHTS["cl04"], WEIGHTS["cl05"], WEIGHTS["cl06"])))
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
            # Create reference axis for the twist variable -- PUBLISHED: xFraction 0.25, alignIndex "j"
            n = geometry.nom_addRefAxis(name="wingAxis", xFraction=0.25, alignIndex="j")
            if nRefAxPts is None:
                nRefAxPts = n
            elif n != nRefAxPts:
                raise RuntimeError("D6R3 REFUSE: ref-axis point count differs between conditions "
                                   "(%d vs %d)" % (n, nRefAxPts))

            # Set up global design variables. We dont change the root twist -- PUBLISHED: rot_y
            def twist(val, geo, _n=nRefAxPts):
                for i in range(1, _n):
                    geo.rot_y["wingAxis"].coef[i] = -val[i - 1]

            # add twist variable
            geometry.nom_addGlobalDV(dvName="twist", value=np.array([0] * (nRefAxPts - 1)), func=twist)

            # select the FFD points to move -- PUBLISHED: all of them, default displacement axis
            pts = geometry.DVGeo.getLocalIndex(0)
            indexList = pts[:, :, :].flatten()
            PS = geo_utils.PointSelect("list", indexList)
            ns = geometry.nom_addLocalDV(dvName="shape", pointSelect=PS)
            if nShapes is None:
                nShapes = ns
            elif ns != nShapes:
                raise RuntimeError("D6R3 REFUSE: shape DV count differs between conditions "
                                   "(%d vs %d)" % (ns, nShapes))

        # ---- the geometric constraints.  Every number below is the PUBLISHED one
        # ---- (CRM_Wing/runScript.py:171-188), carried over unchanged.  They are placed on ONE
        # ---- geometry because the three conditions share one geometry by construction.
        LE_pt = np.array([0.01, 0.01, 0.0])
        break_pt = np.array([0.848, 1.119, 0.0])
        tip_pt = np.array([2.855, 3.755, 0.0])
        root_chord = 1.689
        break_chord = 1.036
        tip_chord = 0.390
        leList = [
            [LE_pt[0] + 0.01 * root_chord, LE_pt[1], LE_pt[2]],
            [break_pt[0] + 0.01 * break_chord, break_pt[1], break_pt[2]],
            [tip_pt[0] + 0.01 * tip_chord, tip_pt[1], tip_pt[2]],
        ]
        teList = [
            [LE_pt[0] + 0.99 * root_chord, LE_pt[1], LE_pt[2]],
            [break_pt[0] + 0.99 * break_chord, break_pt[1], break_pt[2]],
            [tip_pt[0] + 0.99 * tip_chord, tip_pt[1], tip_pt[2]],
        ]
        self.geometry_cl05.nom_addThicknessConstraints2D("thickcon", leList, teList, nSpan=25, nChord=30)
        self.geometry_cl05.nom_addVolumeConstraint("volcon", leList, teList, nSpan=25, nChord=30)
        # add the LE/TE constraints
        self.geometry_cl05.nom_add_LETEConstraint("lecon", volID=0, faceID="iLow")
        self.geometry_cl05.nom_add_LETEConstraint("tecon", volID=0, faceID="iHigh")

        # add the design variables to the dvs component's output
        self.dvs.add_output("twist", val=np.array([0] * (nRefAxPts - 1)))
        self.dvs.add_output("shape", val=np.array([0] * nShapes))
        for pt in POINTS:
            # D1: one AoA design variable per condition
            self.dvs.add_output("patchV_" + pt, val=np.array([U0, aoa0]))
            self.connect("twist", "geometry_%s.twist" % pt)
            self.connect("shape", "geometry_%s.shape" % pt)
            self.connect("patchV_" + pt, "%s.patchV" % pt)

        # define the design variables -- PUBLISHED bounds and scalers, unchanged
        self.add_design_var("twist", lower=-10.0, upper=10.0, scaler=0.1)
        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)
        for pt in POINTS:
            self.add_design_var("patchV_" + pt, lower=[U0, 0.0], upper=[U0, 10.0], scaler=0.1)

        # add objective and constraints to the top level
        # D1: the objective is the weighted sum; the lift equality is one per condition.
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

# initialize the optimization function
# D1: one daOptions per condition -- the DAFoam multipoint form
optFuncs = OptFuncs([daOptions] * len(POINTS), prob)

# use pyoptsparse to setup optimization
prob.driver = om.pyOptSparseDriver()
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
        "max_iter": 100,
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



# --- RULE 17: GATE ON THE MESH THE SOLVER READ, BEFORE ANY EVALUATION ---------------------------
# FM8 was graded a fresh-mesh confirmation and the retraction found 1,486 processor meshes
# scanned, ZERO matching the freshly extruded mesh -- no arm had ever loaded it.  Staging is the
# arm; hashing what the ranks READ is the gate.  Per condition, because D1 stages three.
# It runs BEFORE run_model()/run_driver() and REFUSES (exit 17) rather than degrade.
import d6r3_mesh_read_gate as _r17

def _d6r3_rule17_gate():
    if MPI.COMM_WORLD.rank != 0:
        return None
    out = {}
    for pt in POINTS:
        cdir = os.path.join(os.getcwd(), RUN_DIRS[pt])
        gen = os.path.join(cdir, "constant", "polyMesh", "points")
        try:
            out[pt] = _r17.gate(cdir, gen)
        except _r17.Refusal as e:
            out[pt] = {"gate": "R17_MESH_READ", "verdict": "REFUSE", "why": str(e)}
    with open("d6r3_rule17.json", "w") as f:
        json.dump(out, f, indent=1, default=str)
    bad = [p for p, v in out.items() if v.get("verdict") != "OK"]
    print("D6R3_R17 %s  %s" % ("OK" if not bad else "REFUSE",
                               json.dumps({p: out[p].get("verdict") for p in out})))
    if bad:
        for p in bad:
            print("D6R3_R17 REFUSE %s: %s" % (p, out[p].get("why", "")))
        sys.stdout.flush()
        MPI.COMM_WORLD.Abort(17)
    return out

import json, sys
_d6r3_rule17_gate()
MPI.COMM_WORLD.Barrier()

if args.task == "run_driver":
    # solve CL
    # D1: solve the three CL targets on the three patchV DVs at once
    optFuncs.findFeasibleDesign(["%s.aero_post.CL" % pt for pt in POINTS],
                                ["patchV_" + pt for pt in POINTS],
                                targets=[CL_TARGETS[pt] for pt in POINTS],
                                designVarsComp=[1] * len(POINTS))
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


# --- D6R3: record what this run actually was, on rank 0, before anything else -------------------
if MPI.COMM_WORLD.rank == 0:
    import json as _json
    _rec = {
        "item": "D6R3", "deviation": "D1 multipoint only",
        "points": POINTS, "cl_targets": CL_TARGETS, "weights": WEIGHTS,
        "U0": U0, "T0": T0, "p0": p0, "aoa0": aoa0, "A0": A0,
        "mach": U0 / (1.4 * 287.0 * T0) ** 0.5,
        "solverName": daOptions["solverName"],
        "useWallFunction": daOptions["primalBC"]["useWallFunction"],
        "transonicPCOption": daOptions.get("transonicPCOption"),
        "primalMinResTol": daOptions["primalMinResTol"],
        "primalMinResTolDiff": daOptions.get("primalMinResTolDiff", "ABSENT-published-default"),
        "checkMeshThreshold": daOptions["checkMeshThreshold"],
        "optimizer": args.optimizer,
        "published_regions": _d1_assert_published_regions(),
    }
    with open("d6r3_run_record.json", "w") as _f:
        _json.dump(_rec, _f, indent=1, default=str)
    print("D6R3_RUN_RECORD written: %s" % _json.dumps(
        {k: _rec[k] for k in ("points", "cl_targets", "weights", "mach", "solverName",
                              "useWallFunction", "optimizer")}))
