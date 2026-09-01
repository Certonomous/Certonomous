#!/usr/bin/env python
"""CURRICULUM SO-3 -- THE PRODUCER.  NACA0012 ALPHA-MULTIPOINT, INCOMPRESSIBLE.

Three operating points differing ONLY in angle of attack, one shared `shape`
design-variable vector, one shared geometry component, and a weighted objective
`J = SUM_i w_i * CD_i` assembled by an `om.ExecComp`.

Derived from `curriculum_SO2a/so2a_runScript.py` (the single-point ancestor whose
flow setup, FFD box, shape-function construction and geometric constraints are
REUSED UNCHANGED by Sanaa's 2026-08-31 ruling) plus `curriculum_D6/
d6_opt_runScript.py`'s multipoint assembly.  `PREREGISTRATION.md` (frozen
1a06a7d6) governs; nothing here may move a gate, threshold, cap or label.

--------------------------------------------------------------------------
(A) THIS FILE CONTAINS THE OPTIMISER, AND THAT INVERSION IS THE WHOLE ITEM.
--------------------------------------------------------------------------
SO-3aR2's ancestor of this file said, in terms: *"THIS FILE CONTAINS NO
OPTIMISER.  NOT A DRIVER, NOT A SETTING, NOT A TASK"*, and its `G-NOOPT` gate
checked the artefacts to prove it.  That was RIGHT FOR A GRADIENT RUNG: an
optimisation taken before its own gradient is verified inherits the guess as a
measurement.  SO-3aR2 has now bought that gradient
(`SO3aR2_grade_20260831T230221Z.json`, PATCHED row `PASS`), and SO-3 is the
optimisation rung the scope memo names -- `SO3_MULTIPOINT_SCOPE_MEMO.md` section
5 item 2: *"SO-3 proper is its optimisation rung."*  So the driver comes BACK,
deliberately, and `G-NOOPT` is REPLACED by `G-OPT`, which asserts the opposite
and is no weaker for it.

**AND THE INHERITANCE IS CONDITIONAL, WHICH IS WHY np = 1 IS NOT NEGOTIABLE.**
`DAFOAM_CHARTER.md` section 5: *"A gradient verified at one np is a statement
about that np and is never carried to another."*  SO-3aR2's FD table was measured
at np = 1.  This file runs at np = 1 or the inheritance is VOID, and the rank
count is enforced in `so3_run_arm.sh:ranks_of`, asserted here at import, and
recorded in every artefact.

**WHAT SECTION 9 DEMANDS OF THIS FILE, AND IT IS NOT THE OPTIMUM.**  An
optimisation is graded `PASS` only if the OPTIMISER ITSELF printed a convergence
statement against its own tolerance; one stopped by a wall clock, an iteration
cap or a budget is `GATE REACHED` or `NOT A RESULT` and **never `PASS`**.  A2's
own 48-row history is the incident: 47 majors, 28.275488 % drag reduction, and
`opt_IPOPT.txt` carries NO `EXIT` line anywhere -- which this lane RE-MEASURED on
the artefact (`so3_stall.py` leg s8: `A2-mach-wing/opt_IPOPT.txt`, 48 majors,
`exit=None`).  So this file writes IPOPT's own output to a named file, records
whether an `EXIT` statement exists, and NEVER writes a verdict of its own.

--------------------------------------------------------------------------
(B) ONE SHARED GEOMETRY.  THIS IS A REGISTERED DIVERGENCE FROM D6.
--------------------------------------------------------------------------
Section 0, in the frozen document's own words: the multipoint adjoint *"runs one
`DASolver` instance per operating point behind ONE SHARED `OM_DVGEOCOMP` and sums
through an `om.ExecComp`."*  `d6_opt_runScript.py:143` builds `geometry_<pt>` PER
SCENARIO.  SO-3 does not, and the difference is the point of the item: with one
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
(C) `patchV` IS STILL NOT A DESIGN VARIABLE, AND THE CHOICE IS REGISTERED.
--------------------------------------------------------------------------
Line 4: alpha is this item's OPERATING POINT and cannot simultaneously be a design
variable trimmed to a lift target.  `add_design_var("patchV", ...)` stays REMOVED,
and `CL_target` survives only as a recorded provenance constant -- the angle
`aoa0` is the tutorial's own trimmed angle AT that target, which is why the number
is quoted rather than re-derived.  **NOTHING IS TRIMMED HERE, AND THAT IS A
LIMITATION OF THIS ITEM, NOT A PROPERTY OF THE PROBLEM.**

The scope memo names this as an open registration question and it is answered
HERE rather than left open: *"either each carries its own `aoa` DV and its own
`CL` equality (N constraints, N extra DVs), or the points are specified at fixed
`aoa` and `CL` floats.  THESE ARE DIFFERENT PROBLEMS and the choice changes the
objective's meaning"* (`SO3_MULTIPOINT_SCOPE_MEMO.md` section 2).  **SO-3 takes
the fixed-alpha, floating-`CL` branch**, for one reason that is checkable rather
than aesthetic: SO-3aR2 verified `dCD_i/dx` and `dCL_i/dx` AT FIXED ALPHA, at
np = 1, on this exact assembly.  A per-point `aoa` design variable would make the
optimiser's gradient a DIFFERENT quantity from the one that was verified, and
`DAFOAM_CHARTER.md` section 2 bars an unverified gradient from entering an
optimisation.  Adding the trim is a rung of its own.

**THE CONSEQUENCE IS STATED SO IT CANNOT BE DISCOVERED IN THE FIGURE.**  With
`CL` unconstrained, a weighted-drag minimisation can and probably will buy drag
by shedding lift.  `CL` per point is therefore RECORDED at the baseline and at
the optimum in `so3_O.json`, and the record must carry it beside any drag number:
"the optimiser reduced weighted drag by X" is only a claim about drag, and
`so3_grade.py` refuses to compose a drag-reduction line without the `CL` pair
beside it.

--------------------------------------------------------------------------
(D) THE HEADER/ANCHOR CONTRACT WITH `so3_xf.py`.
--------------------------------------------------------------------------
`so3_xf.py:112` holds an ANCHOR string; the instrument splits this file at it and
`exec`s everything ABOVE it.  Everything the instrument needs is therefore defined
above the anchor: `Top`, `daOptions`, `U0`, `p0`, `CL_target`, `ALPHAS`, `WEIGHTS`.
The instrument then queries, by these exact paths:

    obj.J                        the assembled objective          (so3_xf.OBJ_PATH)
    point{i}.aero_post.CD / .CL  per-scenario forces              (so3_xf.SCENARIOS)
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
`so3_xf.py:478` REFUSES (exit 2) unless the anchor appears in this file EXACTLY
ONCE.  This lane's first draft quoted the anchor's literal bytes twice while
explaining it, so the file carried it THREE times and the instrument would have
refused every arm before writing a single artefact -- the chain would have
produced nothing and the reason would have been a docstring.  It was caught by
DRIVING the instrument's own split against this file, not by reading either.  The
anchor is therefore referred to by NAME and by its line number in the instrument,
never by its bytes.  The same discipline is why `so3_grade.py` reconstructs the
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
import sys
import json
import time
import argparse
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP


parser = argparse.ArgumentParser()
parser.add_argument("-optimizer", help="IPOPT only; any other value REFUSES",
                    type=str, default="IPOPT")
parser.add_argument("-task", help="run_driver, run_model, compute_totals, check_totals",
                    type=str, default="run_model")
parser.add_argument("-xopt", help="path to a so3_xopt.json whose `shape` is applied "
                                  "BEFORE the task runs (the endpoint arms' entry point)",
                    type=str, default="")
args = parser.parse_args()

# ---- THE REGISTERED OPTIMISER SETTINGS.  Frozen with PREREGISTRATION.md. -----
# `MAX_MAJORS` IS A BUDGET, NOT A SETTLE CRITERION.  `VERIFICATION_CHARTER.md`
# section 4: *"a rung that reaches it has not converged, it has run out of money,
# and the two are recorded differently or the ladder inherits the guess as if it
# were a measurement."*  Reaching it is `GATE REACHED`, never `PASS`.
#
# 50 is derived from measurement, not chosen: the nearest sibling on this exact
# case, `CURRICULUM-SO1bR-a1-naca0012-dragmin-opt`, converged in **12 majors**
# on BOTH rows with `EXIT: Optimal Solution Found.`, and `CURRICULUM-D1-a1-
# constrained-opt/armO` -- C-24's own cost anchor -- in **12**.  50 carries better
# than 4x headroom over the single-point precedent while staying inside a cap the
# stall abort can defend.
OPTIMIZER_REGISTERED = "IPOPT"
MAX_MAJORS = 50
OPT_TOL = 1.0e-5
OPT_OUTPUT_FILE = "opt_IPOPT.txt"
OPT_RECORD = "so3_O.json"
XOPT_OUT = "so3_xopt.json"

# ---- THE ROW IS READ FROM THE TOOLCHAIN'S OWN IDENTITY, NEVER FROM A FLAG. ---
# `DAFOAM_CHARTER.md` section 11 makes the IMAGE ID and the LIBRARY HASH the
# identity, never a version string and never a name.  A `-row PATCHED` flag would
# let a mislabelled launch stamp the wrong row into the artefact the endpoint arm
# then reads, and that is the SO-1c failure in its most expensive position.  The
# md5s below are the box's own, taken FROM INSIDE the containers, and both match
# SO-3aR2's G9.  An md5 matching NEITHER refuses: this file will not stamp a row
# it cannot prove.
SO_MD5_ROW = {
    "85f59e87253e0a71a813f64ca6e4c425": "PATCHED",   # dafoam-idwarp-rot:v1
    "f0fcb488e0e98156575cd19548e91663": "SHIPPED",   # dafoam/opt-packages:latest
}


def libidwarp_md5():
    """md5 of the `libidwarp.so` THIS interpreter actually imported, read from
    inside the container.  Not the image tag, not a claim: the bytes."""
    import hashlib
    import idwarp
    so = os.path.join(os.path.dirname(idwarp.__file__), "libidwarp.so")
    return hashlib.md5(open(so, "rb").read()).hexdigest(), so

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
# The scenario group names.  `so3_xf.SCENARIOS` is the same tuple and the
# comparator refuses an artefact whose scenario names are not these.
SCENARIOS = ["point%d" % i for i in range(len(ALPHAS))]

# ===========================================================================
# THE PER-POINT RUN DIRECTORIES -- THE WHOLE REASON SO-3 EXISTS.
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
# the failure being repaired.  `so3_collision_leg.py` DRIVES the invariant
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
# so2a_runScript.py:87-92; `gridFile` is now PER POINT, which is the SO-3 delta.
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

# ---- np = 1, ASSERTED BEFORE SETUP AND NOT MERELY REQUESTED. ---------------
# `DAFOAM_CHARTER.md` section 5 forbids carrying an FD reference across np, and
# SO-3aR2's table -- the entire basis on which this optimisation is admissible --
# was measured at np = 1.  A launcher misconfiguration that handed this file four
# ranks would produce numbers whose gradient has never been verified, and A4
# measured a **16,600x** spread between two decompositions of one mesh.  So the
# rank count is a REFUSAL, not a setting.
NPROCS = MPI.COMM_WORLD.size
if NPROCS != 1:
    if MPI.COMM_WORLD.rank == 0:
        sys.stderr.write(
            "SO3_REFUSE_NP this item is registered at np = 1 and is running at "
            "np = %d.  SO-3aR2's FD table -- the only reason this optimisation is "
            "admissible -- was measured at np = 1, and DAFOAM_CHARTER section 5 "
            "forbids carrying an FD reference across np.  REFUSED.\n" % NPROCS)
    MPI.COMM_WORLD.Abort(66)

prob.setup(mode="rev")

# ---- THE ROW, PROVED FROM THE LIBRARY'S OWN BYTES. -------------------------
SO_MD5, SO_PATH = libidwarp_md5()
ROW = SO_MD5_ROW.get(SO_MD5)
print("SO3_IDWARP_SO_MD5: %s" % SO_MD5)
print("SO3_IDWARP_IMPORTED_FROM: %s" % SO_PATH)
print("SO3_ROW: %s" % (ROW or "UNREGISTERED"))
if ROW is None:
    sys.stderr.write(
        "SO3_REFUSE_ROW libidwarp.so md5 %s matches NEITHER registered toolchain.  "
        "This file will not stamp a row it cannot prove, and the endpoint arms "
        "read that stamp to decide which optimum they are allowed to verify.\n"
        % SO_MD5)
    MPI.COMM_WORLD.Abort(67)

# ---- THE ENDPOINT ENTRY POINT.  `-xopt` applies a design vector BEFORE the
# ---- task runs, so `XE`/`FE` evaluate the gradient AT THE FINAL DESIGN POINT
# ---- section 9 requires rather than at the baseline SO-3aR2 already bought.
if args.xopt:
    with open(args.xopt) as _fh:
        _x = json.load(_fh)
    if _x.get("row") != ROW:
        sys.stderr.write(
            "SO3_REFUSE_XOPT_ROW %s is stamped row=%r but this container is row=%r.  "
            "An endpoint gradient must be verified at the design point ITS OWN "
            "toolchain produced.\n" % (args.xopt, _x.get("row"), ROW))
        MPI.COMM_WORLD.Abort(68)
    _shape = np.array(_x["shape"], dtype=float)
    if _shape.shape != prob.get_val("shape").shape:
        sys.stderr.write("SO3_REFUSE_XOPT_SHAPE %r vs %r\n"
                         % (_shape.shape, prob.get_val("shape").shape))
        MPI.COMM_WORLD.Abort(68)
    prob.set_val("shape", _shape)
    print("SO3_XOPT_APPLIED file=%s row=%s n_dv=%d linf=%.6e"
          % (args.xopt, ROW, _shape.size, float(np.max(np.abs(_shape)))))
else:
    print("SO3_XOPT_APPLIED none -- this task runs at the BASELINE design")

if args.task == "run_driver":
    # =======================================================================
    # THE OPTIMISATION.  IPOPT through pyOptSparse, at np = 1.
    #
    # `output_file` is NAMED so the stall watchdog and the grader read the SAME
    # bytes the optimiser wrote.  `print_level` is high enough that the
    # iteration table -- `iter objective inf_pr inf_du lg(mu) ||d|| lg(rg)
    # alpha_du alpha_pr ls` -- is present, because `so3_stall.py` parses those
    # columns and a truncated table would make the stall detector blind rather
    # than wrong, which is worse.
    # =======================================================================
    if args.optimizer != OPTIMIZER_REGISTERED:
        sys.stderr.write("SO3_REFUSE_OPTIMIZER registered=%s got=%s\n"
                         % (OPTIMIZER_REGISTERED, args.optimizer))
        MPI.COMM_WORLD.Abort(69)
    prob.driver = om.pyOptSparseDriver()
    prob.driver.options["optimizer"] = OPTIMIZER_REGISTERED
    prob.driver.opt_settings = {
        "tol": OPT_TOL,
        "constr_viol_tol": OPT_TOL,
        "max_iter": MAX_MAJORS,
        "output_file": OPT_OUTPUT_FILE,
        "print_level": 5,
        "nlp_scaling_method": "none",
        "mu_strategy": "adaptive",
        "limited_memory_max_history": 10,
    }
    prob.add_recorder(om.SqliteRecorder("so3_driver_history.sql"))

    # THE BASELINE IS EVALUATED AND RECORDED BEFORE THE DRIVER MOVES ANYTHING.
    # A drag reduction quoted against a baseline the same run did not measure is
    # a comparison across two configurations, and this family has paid for that.
    prob.run_model()
    base = {"J": float(prob.get_val("obj.J")[0]),
            "CD": [float(prob.get_val("%s.aero_post.CD" % sc)[0]) for sc in SCENARIOS],
            "CL": [float(prob.get_val("%s.aero_post.CL" % sc)[0]) for sc in SCENARIOS]}
    print("SO3_BASELINE J=%.10e CD=%r CL=%r" % (base["J"], base["CD"], base["CL"]))

    t_start = time.time()
    fail = prob.run_driver()
    t_end = time.time()
    prob.record("final")

    prob.run_model()
    final = {"J": float(prob.get_val("obj.J")[0]),
             "CD": [float(prob.get_val("%s.aero_post.CD" % sc)[0]) for sc in SCENARIOS],
             "CL": [float(prob.get_val("%s.aero_post.CL" % sc)[0]) for sc in SCENARIOS]}
    shape = [float(v) for v in np.asarray(prob.get_val("shape")).ravel()]

    if MPI.COMM_WORLD.rank == 0:
        # ---- THE OPTIMUM, FOR THE ENDPOINT ARMS.  Row-stamped from the library
        # ---- md5 above, so an endpoint arm cannot verify the other row's design.
        with open(XOPT_OUT, "w") as fh:
            json.dump({"row": ROW, "libidwarp_so_md5": SO_MD5, "shape": shape,
                       "n_dv": len(shape), "J_final": final["J"],
                       "alphas": ALPHAS, "weights": WEIGHTS,
                       "scenarios": SCENARIOS, "nprocs": NPROCS,
                       "optimizer": OPTIMIZER_REGISTERED,
                       "max_iter_registered": MAX_MAJORS, "tol_registered": OPT_TOL},
                      fh, indent=2, sort_keys=True)

        # ---- THE STALL READING, FROM THE OPTIMISER'S OWN OUTPUT.  This file
        # ---- RECORDS it and NEVER maps it to a verdict: the mapping to
        # ---- `GATE REACHED` / `NOT A RESULT` is section 9's and lives in the
        # ---- grader.  A producer that also graded could launder its own stop.
        stall, exit_stmt = None, None
        try:
            import so3_stall
            if os.path.isfile(OPT_OUTPUT_FILE):
                _txt = open(OPT_OUTPUT_FILE, errors="replace").read()
                exit_stmt = so3_stall.read_exit_statement(_txt)
                _rows = so3_stall.parse_majors(_txt)
                if len(_rows) > so3_stall.N_STALL:
                    stall = so3_stall.detect_stall(_rows)
                else:
                    stall = {"stall": "NOT_MEASURED",
                             "why": "fewer majors (%d) than the registered window "
                                    "(%d); the detector REFUSES rather than "
                                    "grading a window it does not have"
                                    % (len(_rows), so3_stall.N_STALL)}
        except SystemExit:
            stall = {"stall": "NOT_MEASURED", "why": "so3_stall refused this log"}
        except Exception as e:                              # noqa: BLE001
            stall = {"stall": "NOT_MEASURED", "why": "so3_stall unavailable: %r" % e}

        rec = {
            "item": "SO-3", "row": ROW, "libidwarp_so_md5": SO_MD5,
            "nprocs": NPROCS, "optimizer": OPTIMIZER_REGISTERED,
            "max_iter_registered": MAX_MAJORS, "tol_registered": OPT_TOL,
            "opt_settings": dict(prob.driver.opt_settings),
            "driver_fail_flag": bool(fail),
            "wall_s": round(t_end - t_start, 3),
            "alphas": ALPHAS, "weights": WEIGHTS, "scenarios": SCENARIOS,
            "baseline": base, "final": final, "shape_final": shape,
            # THE NUMBER EVERY READER WANTS, AND THE TWO THAT MUST TRAVEL WITH IT.
            "weighted_drag_reduction_pct":
                (100.0 * (base["J"] - final["J"]) / base["J"]) if base["J"] else None,
            "CL_baseline": base["CL"], "CL_final": final["CL"],
            "CL_note": ("CL is NOT constrained in this item (see docstring (C)).  A "
                        "weighted-drag reduction quoted without these two lists "
                        "beside it is not a claim about this optimisation."),
            "optimiser_exit_statement": exit_stmt,
            "convergence_statement_in_log": exit_stmt is not None,
            "converged_to_optimizer_tolerance": None,
            "converged_note": ("this file records IPOPT's own statement and NEVER "
                               "decides convergence; section 9's mapping is "
                               "so3_grade.py's and a producer that graded itself "
                               "could launder its own stop"),
            "stall": stall,
            "stall_abort_marker_present": os.path.isfile("SO3_STALL_ABORT"),
            "output_file": OPT_OUTPUT_FILE,
        }
        with open(OPT_RECORD, "w") as fh:
            json.dump(rec, fh, indent=2, sort_keys=True)
        print("SO3_O_WRITTEN %s J %.10e -> %.10e (%.6f%%) exit=%r stall=%r"
              % (OPT_RECORD, base["J"], final["J"],
                 rec["weighted_drag_reduction_pct"], exit_stmt,
                 (stall or {}).get("stall")))
        print("SO3_XOPT_WRITTEN %s row=%s n_dv=%d" % (XOPT_OUT, ROW, len(shape)))
elif args.task == "run_model":
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
    # gate is `so3_grade.py`'s FD table at steps proved to lie in the plateau
    # PER PAIR, and no number printed here reaches a verdict.
    prob.run_model()
    prob.check_totals(compact_print=False, step=1e-3, form="central", step_calc="abs")
else:
    print("task arg not valid for SO-3: run_driver, run_model, compute_totals, "
          "check_totals")
    exit(1)
