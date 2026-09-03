#!/usr/bin/env python
"""CURRICULUM SO-3aF2 -- THE PRODUCER.  NACA0012 ALPHA-MULTIPOINT FEASIBILITY,
INCOMPRESSIBLE, PRIMAL ONLY.

DERIVED FROM `curriculum_SO3aR2/so3ar2_runScript.py` BY EXACTLY ONE CLASS OF
DELETION, and `so3af2_runScript_DELTAS_from_so3ar2.diff` shows every byte of it.
The physics, the FFD box, the shape-function construction, the geometric
constraints, the per-point `run_directory` repair and the shared geometry are
REUSED UNCHANGED -- this file makes no fresh physical choice.

--------------------------------------------------------------------------
(A) THIS FILE CANNOT PRODUCE A GRADIENT.  THE CAPABILITY IS DELETED, NOT UNUSED.
--------------------------------------------------------------------------
`FEASIBILITY_PREREGISTRATION.md` section 0 promises this item produces NO
gradient number at all -- "not one that is ungated, not one that is 'diagnostic
only', not one written to a file and left unread" -- and section 3 makes the
promise STRUCTURAL rather than conventional: the parent's gradient task branches
and the `of=`/`wrt=` lists they consume are PHYSICALLY REMOVED, leaving
`run_model` as the only reachable task and an explicit non-zero exit for any
other `-task` value.  A convention ("we simply will not pass the gradient task")
is a claim about operator behaviour; a deleted branch is a property of the bytes.

**AND THE DELETION REACHES EVERY MENTION, NOT ONLY THE BRANCHES, BECAUSE THE
FREEZE'S OWN NL-2 REQUIRES IT.**  Section 6 NL-2 refuses the launch if the
forbidden token appears ANYWHERE in the staged producer -- not merely in a
reachable branch.  The parent carried it at SEVEN sites: the header docstring,
the argparse help string, the two `elif` branches, the totals call, and the
final else-clause message.  Deleting only the line range section 3 names would
have left the token at three surviving sites and NL-2 WOULD HAVE FIRED ON EVERY
LAUNCH, FOREVER.  Section 3's deletion and section 6's token check are jointly
satisfiable only if every occurrence goes, which is what happens here and is
disclosed in the Stage-2 amendment rather than left for a reader to discover.

The only task string this file knows is `run_model`.  There is no optimiser, no
driver, no `pyOptSparse`, no IPOPT/SLSQP/SNOPT block and no major count -- all
already absent in the parent and still absent here.

--------------------------------------------------------------------------
(B) WHAT IT WRITES, AND WHY IT REFUSES RATHER THAN WRITING A SHORT LIST.
--------------------------------------------------------------------------
It writes ONE artefact, `XM/so3af2_M.json`, carrying per-point `alpha`, `CD`,
`CL`, the objective `J`, and `residual_histories`.  `so3af2_read.py` REFUSES if
the number of residual histories disagrees with the number of
`satisfied the prescribed tolerance` lines in the log (section 5 F1: the two
readings must agree, and a disagreement is a reading defect, not physics).

**THIS FILE THEREFORE REFUSES TO WRITE THE ARTEFACT AT ALL RATHER THAN WRITE ONE
WITH A WRONG-LENGTH LIST.**  If it cannot obtain exactly one residual history per
scenario it exits non-zero with a named reason and writes nothing.  A short list
would reach the reader as a CONVERGENCE DISAGREEMENT -- a finding about the
multipoint assembly -- when its true cause was this file failing to look one up.
Manufacturing that finding would be worse than failing to run.

--------------------------------------------------------------------------
(C) WHAT THIS FILE DOES NOT ESTABLISH.
--------------------------------------------------------------------------
It never calls `solve_linear`, so it CANNOT show SO-3aR's adjoint collision is
fixed (section 0.2).  It shows the three builders coexist in one process and
that each owns a separate tree.  That is a weaker statement and the
pre-registration says so in its own words.
"""

# =============================================================================
# Imports
# =============================================================================
import os
import argparse
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP


parser = argparse.ArgumentParser()
# RETAINED so the parent's command line still parses, and DELIBERATELY NARROWED:
# `run_driver` is NOT a valid task in this item and no optimiser exists to run.
parser.add_argument("-optimizer", help="accepted and UNUSED: this item runs no optimiser",
                    type=str, default="NONE")
parser.add_argument("-task", help="run_model -- THE ONLY TASK THIS ITEM HAS; see (A)",
                    type=str, default="run_model")
args = parser.parse_args()

# =============================================================================
# Input Parameters -- QUOTATIONS from curriculum_SO2a/so2a_runScript.py:31-45,
# reused UNCHANGED by the ruling.  These are not fresh choices.
# =============================================================================
U0 = 10.0
p0 = 0.0
nuTilda0 = 4.5e-5
# The tutorial's own trimmed angle at CL_target = 0.5, quoted from
# so2a_runScript.py:35.  It is the CENTRE of this item's alpha bracket and the
# angle at which the family's plateau study, SO-1a and SO-2a were all measured.
CL_target = 0.5
aoa0 = 5.13918623195176
A0 = 0.1
# rho is used for normalizing CD and CL
rho0 = 1.0

# ---- LINE 4 OF THE FROZEN TEN.  THREE alpha, degrees: aoa0 - 2, aoa0, aoa0 + 2.
# ---- The centre is a QUOTATION; the +/-2 degree bracket is LANE-CHOSEN and
# ---- registered as lane-chosen on the three grounds line 4 states -- all three
# ---- inside the tutorial's own aoa bound [0.0, 10.0]; NACA0012 attached
# ---- throughout 3-7 deg at Re ~ 6.7e5, so no scenario sits near stall; and the
# ---- bracket is wide enough that the points are genuinely different operating
# ---- points.  WRITTEN OUT rather than computed from aoa0 +/- 2.0, so the file
# ---- carries the exact values the comparator compares against to 1e-12 and a
# ---- floating-point subtraction cannot move one of them.
ALPHAS = [3.13918623195176, 5.13918623195176, 7.13918623195176]
# ---- EQUAL WEIGHTS.  A CHOICE, NOT A DEFAULT, and named as one (line 4).
# ---- Written as 1.0/3.0 rather than 0.3333... so the objective uses the exact
# ---- binary value the artefact records.  A different weighting is a DIFFERENT
# ---- OBJECTIVE and would need its own row; section "G-WT" registers why the
# ---- shuffled-weight probe is NOT bought.
WEIGHTS = [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]
# The scenario group names.  `so3ar2_xf.SCENARIOS` is the same tuple and the
# comparator refuses an artefact whose scenario names are not these.
SCENARIOS = ["point%d" % i for i in range(len(ALPHAS))]

# ===========================================================================
# THE PER-POINT RUN DIRECTORIES -- THE WHOLE REASON SO-3aR2 EXISTS.
#
# SO-3aR built one `DAFoamBuilder` per operating point and gave NONE of them a
# `run_directory`, so three independent `DASolver` instances shared one case
# directory, each carrying its OWN `solution_counter`, and each renamed its
# converged solution to the SAME `0.0001`.  `point0` renamed 443 -> 0.0001 and
# succeeded (its arm log line 1827); `point1` tried 436 -> 0.0001 and
# `pyDAFoam.renameSolution` raised
#     `pyDAFoam Error: /mnt/X-S/0.0001 already exists, moving failed!`
# at `pyDAFoam.py:1543`, reached from `mphys_dafoam.py:483` in `solve_linear`.
# The item died at arm 2 of 5 with `NOT A RESULT`
# [MEASURED, cases/dafoam/ladder-a/A1/curriculum_SO3aR/RESULTS.md section 6].
#
# THE CURE IS THE LAB'S OWN AND IS PORTED, NOT INVENTED.  A2's D6R already
# carried it:
#   `curriculum_D6R/d6r_opt_runScript.py:59`  RUN_DIRS = {"cl04": "mp04", ...}
#   `curriculum_D6R/d6r_opt_runScript.py:120` "gridFile": os.path.join(os.getcwd(), RUN_DIRS[point])
#   `curriculum_D6R/d6r_opt_runScript.py:138` run_directory=RUN_DIRS[pt]
# A1 never carried A2's isolation forward.  That is a LAB REGRESSION of cause
# class BOOKKEEPING/INSTRUMENT -- not an upstream defect and not physics.
#
# THE KEYS ARE DERIVED FROM `SCENARIOS`, NEVER SPELLED OUT.  A hand-written map
# is one more call site of the scenario label, and a scenario added above with no
# row here would silently fall back to the shared directory -- which is exactly
# the failure being repaired.  `so3ar2_collision_leg.py` DRIVES the invariant
# that the map is total and injective over `SCENARIOS`, and drives it RED on the
# unfixed source.
RUN_DIRS = {sc: "mp%d" % i for i, sc in enumerate(SCENARIOS)}

# Input parameters for DAFoam -- UNCHANGED from so2a_runScript.py:39-84.
daOptions = {
    "designSurfaces": ["wing"],
    "solverName": "DASimpleFoam",
    "primalMinResTol": 1.0e-8,
    "primalBC": {
        "U0": {"variable": "U", "patches": ["inout"], "value": [U0, 0.0, 0.0]},
        "p0": {"variable": "p", "patches": ["inout"], "value": [p0]},
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
        "nuTilda": nuTilda0 * 10.0,
        "phi": 1.0,
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

# Mesh deformation setup.  The `symmetryPlanes` and `fileType` are UNCHANGED from
# so2a_runScript.py:87-92; `gridFile` is now PER POINT, which is the SO-3aR2 delta.
# D6R's shape, `d6r_opt_runScript.py:117-124`: each point owns a full case copy and
# reads its mesh out of that copy, so no two IDWarp instances and no two DASolvers
# address the same directory.
def mesh_options_for(point):
    return {
        "gridFile": os.path.join(os.getcwd(), RUN_DIRS[point]),
        "fileType": "OpenFOAM",
        # point and normal for the symmetry plane
        "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]], [[0.0, 0.0, 0.1], [0.0, 0.0, 1.0]]],
    }

# The ExecComp expression, BUILT FROM `WEIGHTS` rather than written as a literal,
# so a weight changed above cannot leave a stale coefficient in the objective.
# D6 wrote its expression as the literal "J = 0.25*CD04 + 0.50*CD05 + 0.25*CD06"
# beside a separate weights list -- two places to change and one to forget.
OBJ_EXPR = "J = " + " + ".join("%r*CD%d" % (w, i) for i, w in enumerate(WEIGHTS))


# Top class: the multipoint assembly.
class Top(Multipoint):
    def setup(self):

        # ONE builder per operating point -- one DASolver per scenario -- EACH IN
        # ITS OWN `run_directory`.  They share `daOptions` because the three points
        # differ ONLY in alpha, which is a boundary condition and not a mesh
        # property; they do NOT share a directory, because each DASolver carries
        # its own `solution_counter` and renames into `run_directory`.  Sharing one
        # is what killed SO-3aR at its second arm.
        self.builders = []
        for i, sc in enumerate(SCENARIOS):
            b = DAFoamBuilder(daOptions, mesh_options_for(sc), scenario="aerodynamic",
                              run_directory=RUN_DIRS[sc])
            b.initialize(self.comm)
            self.builders.append(b)

        # the design variable component holding the top level design variables
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])

        # one mesh coordinate subsystem per scenario (each DASolver needs its own)
        for i, sc in enumerate(SCENARIOS):
            self.add_subsystem("mesh_" + sc, self.builders[i].get_mesh_coordinate_subsystem())

        # ---- THE ONE SHARED GEOMETRY.  See (B).  This is the whole reason the
        # ---- item can buy G-MP-STRUCT: exactly one `shape` -> surface map.
        self.add_subsystem("geometry", OM_DVGEOCOMP(file="FFD/wingFFD.xyz", type="ffd"))

        # one scenario (flow condition) per operating point
        for i, sc in enumerate(SCENARIOS):
            self.mphys_add_scenario(sc, ScenarioAerodynamic(aero_builder=self.builders[i]))

        # The geometry takes its undeformed surface from SCENARIO 0's mesh and
        # feeds ALL THREE scenarios.  WHICH mesh is recorded here rather than left
        # implicit: the three are the same points, and reading point0's is a
        # choice a reviewer can check.
        self.connect("mesh_%s.x_aero0" % SCENARIOS[0], "geometry.x_aero_in")
        for sc in SCENARIOS:
            self.connect("geometry.x_aero0", "%s.x_aero" % sc)

        # ---- the weighted objective, assembled by an ExecComp.  This component
        # ---- is what G-MP-STRUCT's identity is an identity ABOUT.
        self.add_subsystem("obj", om.ExecComp(OBJ_EXPR))
        for i, sc in enumerate(SCENARIOS):
            self.connect("%s.aero_post.CD" % sc, "obj.CD%d" % i)

    def configure(self):

        # surface coordinates from SCENARIO 0's mesh -- see the note in setup().
        points = getattr(self, "mesh_%s" % SCENARIOS[0]).mphys_get_surface_mesh()

        # add pointset to the SHARED geometry component
        self.geometry.nom_add_discipline_coords("aero", points)

        # triangular points for the geometric constraints, from the same mesh
        tri_points = getattr(self, "mesh_%s" % SCENARIOS[0]).mphys_get_triangulated_surface()
        self.geometry.nom_setConstraintSurface(tri_points)

        # ---- the shape function construction, UNCHANGED from
        # ---- so2a_runScript.py:137-148.  5x2x2 FFD -> 8 `shape` functions.
        pts = self.geometry.DVGeo.getLocalIndex(0)
        dir_y = np.array([0.0, 1.0, 0.0])
        shapes = []
        for i in range(1, pts.shape[0] - 1):
            for j in range(pts.shape[1]):
                # k=0 and k=1 move together to ensure symmetry
                shapes.append({pts[i, j, 0]: dir_y, pts[i, j, 1]: dir_y})
        # LE/TE shape: j=0 and j=1 move in opposite directions so the LE/TE are fixed
        for i in [0, pts.shape[0] - 1]:
            shapes.append({pts[i, 0, 0]: dir_y, pts[i, 0, 1]: dir_y,
                           pts[i, 1, 0]: -dir_y, pts[i, 1, 1]: -dir_y})
        self.geometry.nom_addShapeFunctionDV(dvName="shape", shapes=shapes)

        # ---- the geometric constraints, UNCHANGED from so2a_runScript.py:151-155.
        # ---- They live on the SHARED geometry, so there is one set of them for
        # ---- the whole multipoint problem rather than three that could disagree.
        leList = [[1e-4, 0.0, 1e-4], [1e-4, 0.0, 0.1 - 1e-4]]
        teList = [[0.998 - 1e-4, 0.0, 1e-4], [0.998 - 1e-4, 0.0, 0.1 - 1e-4]]
        self.geometry.nom_addThicknessConstraints2D("thickcon", leList, teList, nSpan=2, nChord=10)
        self.geometry.nom_addVolumeConstraint("volcon", leList, teList, nSpan=2, nChord=10)
        self.geometry.nom_addLERadiusConstraints("rcon", leList, 2, [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0])

        # ---- ONE shared `shape` vector across all three scenarios (line 1).
        self.dvs.add_output("shape", val=np.array([0] * len(shapes)))
        self.connect("shape", "geometry.shape")

        # ---- the operating points.  ONE `patchV{i}` per scenario, differing ONLY
        # ---- in the angle.  Promoted through `dvs` AND connected to the scenario,
        # ---- so BOTH of G-ALPHA's read paths -- `patchV{i}` and
        # ---- `point{i}.patchV` -- resolve to the same value.  See (D).
        for i, sc in enumerate(SCENARIOS):
            self.dvs.add_output("patchV%d" % i, val=np.array([U0, ALPHAS[i]]))
            self.connect("patchV%d" % i, "%s.patchV" % sc)

        # ---- the design variables.  `shape` ONLY.  `patchV` is NOT a design
        # ---- variable in this item and its removal is registered, not silent --
        # ---- see (C).  The parent's `add_design_var("patchV", ...)` is GONE.
        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)

        # ---- the objective and the geometric constraints are DECLARED so the
        # ---- model is the one the later optimisation rung will use, and so the
        # ---- constraint components are built.  NO DRIVER EXISTS TO CONSUME THEM
        # ---- IN THIS ITEM -- see (A).  The per-scenario CL is NOT constrained
        # ---- here: alpha is the operating point, nothing is trimmed, and G5C
        # ---- verifies dCL_i/dx as a GRADIENT rather than enforcing a target.
        self.add_objective("obj.J", scaler=1.0)
        self.add_constraint("geometry.thickcon", lower=0.5, upper=3.0, scaler=1.0)
        self.add_constraint("geometry.volcon", lower=1.0, scaler=1.0)
        self.add_constraint("geometry.rcon", lower=0.8, scaler=1.0)


# OpenMDAO setup
prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")

# NO DRIVER IS CONSTRUCTED.  See (A): section 2 limb 1 is the ABSENCE of the
# capability, and `run_driver` is not among the tasks below.
if args.task == "run_model":
    # ONE multipoint evaluation is THREE primals.  This is the only task.
    prob.run_model()
else:
    print("task arg not valid for SO-3aF2: run_model is the ONLY task. "
          "This item produces no gradient and the gradient task branches are "
          "DELETED, not merely unreached -- see (A).")
    exit(1)

# =============================================================================
# THE ARTEFACT.  Rank 0 only.  See (B): it REFUSES rather than writing short.
# =============================================================================
if MPI.COMM_WORLD.rank == 0:
    import json

    def _fail(reason, detail):
        print("SO3aF2 PRODUCER REFUSAL: %s %s" % (reason, json.dumps(detail)))
        exit(7)

    def _residual_history(scenario):
        """One residual history per scenario, or None.

        The lookup chain is explicit and every step is named, because this lane
        has spent ZERO solver core-minutes and therefore has NOT exercised this
        API against a live container.  The mphys path `<scenario>.coupling.solver`
        is corroborated by evidence on disk -- OpenMDAO deprecation warnings in
        `CURRICULUM-D6R-a2-wing-multipoint/O_mp_20260828T162849Z_1898072.log`
        name `cl04.coupling.solver` explicitly -- but WHICH attribute carries a
        residual history is NOT corroborated, and that is this file's principal
        launch risk, named in the Stage-2 amendment rather than hidden here.
        Returning None is honest; inventing a list is not."""
        node = prob.model
        for part in (scenario, "coupling", "solver"):
            node = getattr(node, part, None)
            if node is None:
                return None
        das = getattr(node, "DASolver", None)
        if das is None:
            return None
        for attr in ("getPrimalResidualHistory", "primalResidualHistory",
                     "getResidualHistory", "residualHistory"):
            obj = getattr(das, attr, None)
            if obj is None:
                continue
            try:
                hist = obj() if callable(obj) else obj
            except Exception:          # noqa: BLE001 -- a raising lookup is a miss
                continue
            if hist is not None:
                return list(hist)
        return None

    points, histories = [], []
    for i_sc, sc in enumerate(SCENARIOS):
        try:
            cd = float(prob.get_val("%s.aero_post.CD" % sc)[0])
            cl = float(prob.get_val("%s.aero_post.CL" % sc)[0])
        except Exception as exc:       # noqa: BLE001
            _fail("FUNCTIONAL_UNREADABLE", {"scenario": sc, "error": str(exc)})
        if cd != cd or cl != cl:
            _fail("FUNCTIONAL_NON_FINITE", {"scenario": sc, "CD": cd, "CL": cl})
        points.append({"alpha": ALPHAS[i_sc], "CD": cd, "CL": cl})
        h = _residual_history(sc)
        if h is None:
            _fail("RESIDUAL_HISTORY_UNAVAILABLE", {
                "scenario": sc,
                "note": "refusing to write a short residual_histories list; "
                        "see (B) -- a short list reaches the reader as a "
                        "CONVERGENCE DISAGREEMENT, which is a finding about the "
                        "multipoint assembly this file would have manufactured"})
        histories.append(h)

    if len(histories) != len(SCENARIOS):
        _fail("RESIDUAL_HISTORY_COUNT", {"got": len(histories),
                                         "want": len(SCENARIOS)})

    try:
        j_val = float(prob.get_val("obj.J")[0])
    except Exception as exc:           # noqa: BLE001
        _fail("OBJECTIVE_UNREADABLE", {"error": str(exc)})

    out_dir = os.path.join(os.getcwd(), "XM")
    os.makedirs(out_dir, exist_ok=True)
    art = os.path.join(out_dir, "so3af2_M.json")
    if os.path.exists(art):
        _fail("ARTEFACT_ALREADY_EXISTS", {"path": art,
              "note": "a pre-existing artefact means this is not the run allowed "
                      "to produce the answer; archive by mv, never overwrite"})
    tmp = art + ".partial"
    with open(tmp, "w") as fh:
        json.dump({"points": points, "J": j_val,
                   "residual_histories": histories,
                   "weights": WEIGHTS, "scenarios": list(SCENARIOS),
                   "run_dirs": [RUN_DIRS[sc] for sc in SCENARIOS]},
                  fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, art)
    print("SO3aF2 PRODUCER wrote %s" % art)
