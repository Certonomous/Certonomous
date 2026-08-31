#!/usr/bin/env python
"""CURRICULUM SO-3aR2 -- THE PRODUCER.  NACA0012 ALPHA-MULTIPOINT, INCOMPRESSIBLE.

Three operating points differing ONLY in angle of attack, one shared `shape`
design-variable vector, one shared geometry component, and a weighted objective
`J = SUM_i w_i * CD_i` assembled by an `om.ExecComp`.

Derived from `curriculum_SO2a/so2a_runScript.py` (the single-point ancestor whose
flow setup, FFD box, shape-function construction and geometric constraints are
REUSED UNCHANGED by Sanaa's 2026-08-31 ruling) plus `curriculum_D6/
d6_opt_runScript.py`'s multipoint assembly.  `PREREGISTRATION.md` (frozen
1a06a7d6) governs; nothing here may move a gate, threshold, cap or label.

--------------------------------------------------------------------------
(A) THIS FILE CONTAINS NO OPTIMISER.  NOT A DRIVER, NOT A SETTING, NOT A TASK.
--------------------------------------------------------------------------
Section 2 LIMB 1: *"A frozen chain that cannot express an optimisation iteration
cannot take one out of order... This is not a promise about behaviour; it is the
ABSENCE OF THE CAPABILITY, checkable by a reviewer against the arm table today."*

The SO-2a parent carries `om.pyOptSparseDriver()`, an IPOPT settings block with
`max_iter`, and a `run_driver` task.  **All of it is REMOVED here, not merely left
unreached.**  `so3ar2_xf.py` only ever `exec`s this file's header (everything above
the OpenMDAO-setup anchor, whose literal bytes are held in `so3ar2_xf.py:112` and
are deliberately NOT spelled anywhere in this docstring -- see (E)), so leaving
the driver below the anchor would have been harmless AT RUNTIME -- and would still have left a reviewer reading a file
that ships the capability section 2 says this item does not have.  The registered
tasks are `run_model`, `compute_totals` and `check_totals`.  There is no
`run_driver`, no `pyOptSparse`, no IPOPT/SLSQP/SNOPT block, no `max_iter` and no
major count anywhere in this file.  `G-NOOPT` checks the ARTEFACTS; this removal
is what makes the reviewer's check of the FILE come out the same way.

--------------------------------------------------------------------------
(B) ONE SHARED GEOMETRY.  THIS IS A REGISTERED DIVERGENCE FROM D6.
--------------------------------------------------------------------------
Section 0, in the frozen document's own words: the multipoint adjoint *"runs one
`DASolver` instance per operating point behind ONE SHARED `OM_DVGEOCOMP` and sums
through an `om.ExecComp`."*  `d6_opt_runScript.py:143` builds `geometry_<pt>` PER
SCENARIO.  SO-3aR2 does not, and the difference is the point of the item: with one
geometry there is exactly one `shape` -> surface map, so `G-MP-STRUCT`'s identity
`J_adj[J,k] == SUM_i w_i J_adj[CD_i,k]` tests the ASSEMBLY rather than three
independent single-point problems that happen to share a DV name.

Each scenario keeps its own `DAFoamBuilder`, its own mesh coordinate subsystem AND
ITS OWN `run_directory` -- one `DASolver` per operating point in one case copy per
operating point, which is what D6R measured to work -- and the SHARED geometry's
`x_aero0` feeds all three.  SO-3aR's docstring said "own builder, own mesh" and
stopped there; the missing third noun is what killed it, and it is the delta.  That is consistent because the
three points differ ONLY in alpha, and alpha enters through `patchV`, a BOUNDARY
CONDITION, never through the mesh: the three surface point sets are the same
points.  `nom_add_discipline_coords` and `nom_setConstraintSurface` therefore take
`point0`'s mesh, and which mesh they take is recorded here rather than left to be
wondered at.

**WHAT IS NOT VERIFIED BY THIS FILE, STATED PLAINLY.** Whether three
`DASimpleFoam` `DASolver` instances co-exist in one process against one case
directory is a RUNTIME question this lane cannot answer without a container, and
this lane spends zero solver compute.  It is exactly the surface section 6
registers `P-EVAL` against and section 0 names as *"where a multipoint gradient
can be wrong while every single-point gradient is right"*.  Nothing in this
docstring claims it works; the MESH and X-S arms are what measure it.

--------------------------------------------------------------------------
(C) `patchV` IS NOT A DESIGN VARIABLE HERE, AND THE REMOVAL IS REGISTERED.
--------------------------------------------------------------------------
Line 4: alpha is this item's OPERATING POINT and cannot simultaneously be a design
variable trimmed to a lift target.  The parent's `add_design_var("patchV", ...)`
is REMOVED, and `CL_target` survives only as a recorded provenance constant --
the angle `aoa0` is the tutorial's own trimmed angle AT that target, which is why
the number is quoted rather than re-derived.  Nothing trims anything here.

--------------------------------------------------------------------------
(D) THE HEADER/ANCHOR CONTRACT WITH `so3ar2_xf.py`.
--------------------------------------------------------------------------
`so3ar2_xf.py:112` holds an ANCHOR string; the instrument splits this file at it and
`exec`s everything ABOVE it.  Everything the instrument needs is therefore defined
above the anchor: `Top`, `daOptions`, `U0`, `p0`, `CL_target`, `ALPHAS`, `WEIGHTS`.
The instrument then queries, by these exact paths:

    obj.J                        the assembled objective          (so3ar2_xf.OBJ_PATH)
    point{i}.aero_post.CD / .CL  per-scenario forces              (so3ar2_xf.SCENARIOS)
    point{i}.patchV, patchV{i}   the operating point, BOTH paths  (G-ALPHA's source)
    shape                        the shared 8-component DV vector

`patchV{i}` is added on `dvs` (promoted) AND connected to `point{i}.patchV`, so
BOTH of G-ALPHA's read paths resolve to the same value.  The instrument records
which path resolved and writes `None` for one that does not; it never substitutes
its own constant, because an instrument that echoes its own constant back cannot
detect a scenario wired to the wrong angle.

--------------------------------------------------------------------------
(E) THE ANCHOR IS NEVER SPELLED IN THIS DOCSTRING, AND THAT IS LOAD-BEARING.
--------------------------------------------------------------------------
`so3ar2_xf.py:478` REFUSES (exit 2) unless the anchor appears in this file EXACTLY
ONCE.  This lane's first draft quoted the anchor's literal bytes twice while
explaining it, so the file carried it THREE times and the instrument would have
refused every arm before writing a single artefact -- the chain would have
produced nothing and the reason would have been a docstring.  It was caught by
DRIVING the instrument's own split against this file, not by reading either.  The
anchor is therefore referred to by NAME and by its line number in the instrument,
never by its bytes.  The same discipline is why `so3ar2_grade.py` reconstructs the
old instrument alias from parts at U88 and assembles its row-label known positive
from parts at U101: a file must not spell a token whose count it has to control.

**AND THE DISTINCTION THAT MATTERS, because collapsing it would make this file
LESS honest, not more.**  The ANCHOR count is enforced by the INSTRUMENT against
this file's RAW BYTES, so prose genuinely must not spell it.  The optimiser-,
design-variable- and geometry-absence checks are the SELFTEST'S OWN, and they are
scoped to this file's CODE with the module docstring stripped -- because a rule
that forbade the docstring from NAMING what the file removed would buy a green
check by deleting the explanation.  This lane wrote those checks against the whole
file first, and all four went red on its own prose; the repair was to scope the
check, not to silence the paragraph.
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
parser.add_argument("-task", help="run_model (default), compute_totals, check_totals",
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
    # just run the primals once -- one multipoint evaluation is THREE primals
    prob.run_model()
elif args.task == "compute_totals":
    # the primals and the adjoint once, over the registered `of` set
    prob.run_model()
    of = ["obj.J"] + ["%s.aero_post.CD" % sc for sc in SCENARIOS] \
        + ["%s.aero_post.CL" % sc for sc in SCENARIOS]
    totals = prob.compute_totals(of=of, wrt=["shape"])
    if MPI.COMM_WORLD.rank == 0:
        print(totals)
elif args.task == "check_totals":
    # OpenMDAO's own FD check.  It is a CONVENIENCE, not this item's gate: the
    # gate is `so3ar2_grade.py`'s FD table at steps proved to lie in the plateau
    # PER PAIR, and no number printed here reaches a verdict.
    prob.run_model()
    prob.check_totals(compact_print=False, step=1e-3, form="central", step_calc="abs")
else:
    print("task arg not valid for SO-3aR2: run_model, compute_totals, check_totals "
          "(this item runs NO optimiser and `run_driver` is deliberately absent)")
    exit(1)
