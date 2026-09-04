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

# ===========================================================================
# THE OUTPUT PATHS ARE DERIVED FROM THE FROZEN READER'S OWN EXPRESSIONS.
#
# ADDENDUM 1 measured two mismatches between this producer and `so3af2_read.py`:
# the per-point directories were written to `XM/mp<i>` while the reader's F3
# reads `<root>/XM/case/`, and the artefact was written to `<root>/XM/XM/` --
# one nested `XM` too many -- while the reader reads `<root>/XM/`.  F3 would have
# scored MISS on a separation that had actually worked, which is the worst kind
# of wrong answer: a confident negative on a working mechanism.
#
# THE READER IS FROZEN AND PINNED SINCE 2026-08-31 AND IS NOT TOUCHED.  THE
# PRODUCER CONFORMS TO THE READER'S CONTRACT, NEVER THE REVERSE.
#
# And the paths are DERIVED, not transcribed -- the `a1wrt_controldict.py` shape.
# Transcribing them would put the same literal in two files and let a future edit
# to one silently reopen exactly this defect.  Every value below is parsed out of
# the reader's OWN BYTES with `ast`, and anything not UNIQUELY determined REFUSES.
# ===========================================================================
def _reader_path_contract(reader_path):
    """Parse `so3af2_read.py` and return (artefact_segments, case_segments,
    run_dir_names) as the reader itself expresses them.  Refuses rather than
    guessing: this is the file the grading depends on agreeing with."""
    import ast as _ast

    def _fail(reason, detail):
        print("SO3aF2 PRODUCER REFUSAL: %s %s" % (reason, detail))
        raise SystemExit(9)

    if not os.path.isfile(reader_path):
        _fail("READER_ABSENT", reader_path + " -- the producer derives its output "
              "paths from the reader and will not guess them")
    tree = _ast.parse(open(reader_path).read())

    joins = []
    for node in _ast.walk(tree):
        if not isinstance(node, _ast.Call):
            continue
        f = node.func
        if not (isinstance(f, _ast.Attribute) and f.attr == "join"):
            continue
        if not node.args:
            continue
        a0 = node.args[0]
        if not (isinstance(a0, _ast.Name) and a0.id == "root"):
            continue
        segs = [a.value for a in node.args[1:]
                if isinstance(a, _ast.Constant) and isinstance(a.value, str)]
        if len(segs) == len(node.args) - 1:
            joins.append(segs)

    # THE CASE PATH IS IDENTIFIED BY ITS CONSUMER, NOT BY A FILENAME HEURISTIC.
    # A first draft took "the join that is not a .json" and REFUSED against the
    # real reader, because there are three of them -- <root>/XM/XM.log, <root>/XM
    # and <root>/XM/case. The refusal was right and the rule was wrong: it used a
    # PROXY for the quantity instead of the relation that actually defines it.
    # The case path is the argument of the call to `read_run_dirs`, which is the
    # function whose result F3 is scored from, and nothing else is.
    case = []
    for node in _ast.walk(tree):
        if not (isinstance(node, _ast.Call) and isinstance(node.func, _ast.Name)
                and node.func.id == "read_run_dirs" and len(node.args) == 1):
            continue
        a = node.args[0]
        if not (isinstance(a, _ast.Call) and isinstance(a.func, _ast.Attribute)
                and a.func.attr == "join" and a.args
                and isinstance(a.args[0], _ast.Name) and a.args[0].id == "root"):
            _fail("READER_CASE_PATH_NOT_A_ROOT_JOIN",
                  "read_run_dirs is called with something this producer cannot derive")
        segs = [x.value for x in a.args[1:]
                if isinstance(x, _ast.Constant) and isinstance(x.value, str)]
        if len(segs) != len(a.args) - 1:
            _fail("READER_CASE_PATH_NOT_LITERAL", "non-literal segment in read_run_dirs' join")
        case.append(segs)

    art = [j for j in joins if j and j[-1].endswith(".json")]
    if len(art) != 1:
        _fail("READER_ARTEFACT_PATH_NOT_UNIQUE", repr(art))
    if len(case) != 1:
        _fail("READER_CASE_PATH_NOT_UNIQUE", repr(case))

    run_dirs = None
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], _ast.Name) \
                and node.targets[0].id == "RUN_DIRS" \
                and isinstance(node.value, (_ast.List, _ast.Tuple)):
            vals = [e.value for e in node.value.elts
                    if isinstance(e, _ast.Constant) and isinstance(e.value, str)]
            if len(vals) == len(node.value.elts):
                if run_dirs is not None:
                    _fail("READER_RUN_DIRS_NOT_UNIQUE", "more than one RUN_DIRS assignment")
                run_dirs = vals
    if not run_dirs:
        _fail("READER_RUN_DIRS_ABSENT", "no list-literal RUN_DIRS in the reader")
    return art[0], case[0], run_dirs


_READER = os.path.join(os.getcwd(), "so3af2_read.py")
ART_SEGS, CASE_SEGS, READER_RUN_DIRS = _reader_path_contract(_READER)

# The arm directory is `<root>/<ARM>`; both derived paths must agree on that first
# segment, and it must be the directory this process is running in.  Asserting it
# is what makes the derivation a check rather than an assumption.
if ART_SEGS[0] != CASE_SEGS[0]:
    print("SO3aF2 PRODUCER REFUSAL: READER_SEGMENTS_DISAGREE %r vs %r" % (ART_SEGS, CASE_SEGS))
    raise SystemExit(9)
if os.path.basename(os.getcwd()) != ART_SEGS[0]:
    print("SO3aF2 PRODUCER REFUSAL: WRONG_WORKING_DIRECTORY cwd=%s expected basename %r "
          "-- the reader's contract is <root>/%s/..." % (os.getcwd(), ART_SEGS[0], ART_SEGS[0]))
    raise SystemExit(9)

RUN_ROOT_DIR = os.path.dirname(os.getcwd())          # <root>
ARTEFACT_PATH = os.path.join(RUN_ROOT_DIR, *ART_SEGS)  # <root>/XM/so3af2_M.json
CASE_DIR = os.path.join(RUN_ROOT_DIR, *CASE_SEGS)      # <root>/XM/case

# The per-point directories must be created UNDER the reader's case path, so the
# producer runs from there.  A missing case directory REFUSES BY NAME rather than
# failing somewhere inside DAFoam -- ADDENDUM 1 finding 1 (the XM arm stages one
# file into an otherwise empty directory) is NOT repaired here and this refusal is
# what makes it legible instead of a crash.
if not os.path.isdir(CASE_DIR):
    print("SO3aF2 PRODUCER REFUSAL: CASE_DIRECTORY_ABSENT %s -- the reader's F3 reads "
          "run directories from here (%s), so the case must be staged under it. "
          "The XM staging repair is NOT part of this addendum." % (CASE_DIR, "/".join(CASE_SEGS)))
    raise SystemExit(9)
os.chdir(CASE_DIR)
print("SO3aF2 PRODUCER path contract DERIVED from the reader: artefact=%s case=%s run_dirs=%r"
      % (ARTEFACT_PATH, CASE_DIR, READER_RUN_DIRS))

# RUN_DIRS now come FROM THE READER, so the two files cannot disagree.  A count
# mismatch against SCENARIOS refuses rather than silently pairing the shorter list.
if len(READER_RUN_DIRS) != len(SCENARIOS):
    print("SO3aF2 PRODUCER REFUSAL: RUN_DIRS_COUNT reader=%d scenarios=%d"
          % (len(READER_RUN_DIRS), len(SCENARIOS)))
    raise SystemExit(9)
RUN_DIRS = {sc: READER_RUN_DIRS[i] for i, sc in enumerate(SCENARIOS)}

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

    # =====================================================================
    # ADDENDUM 15.  THE RESIDUAL HISTORY IS READ FROM THE LOG.
    #
    # Section 5 F1 of the frozen registration scores convergence "counted from
    # the log, both ways".  The four attribute names this function used to try
    # were an UNREGISTERED SUBSTITUTE for that, and they are gone -- not
    # because they failed, but because they were never the registered route.
    # ADDENDUM 13 ruled that F1's approach as registered could not work; that
    # ruling was WRONG and is corrected by ADDENDUM 15.  What could not work
    # was this file's substitute.
    #
    # THIS PROCESS CAN READ ITS OWN LOG WHILE IT RUNS, and that is a property
    # of OpenFOAM rather than a hope: `Foam::endl` reaches
    # `OSstream::endl()`, whose whole body is `write('\n'); os_.flush();`
    # (OSstream.C:301-305 in the registered image).  Every `Info << ... << endl`
    # therefore flushes, so a residual line printed is a residual line on disk.
    # The arm redirects this script's stdout into the mounted run root
    # (`python so3af2_runScript.py -task run_model > XM.log 2>&1`), so fd 1 IS
    # the log.
    # =====================================================================
    import re as _re
    import shutil as _shutil
    import tempfile as _tempfile

    _BLOCK = "Running Primal Solver"
    _RE_TIME = _re.compile(r"^Time = (\d+)\s*$")
    _RE_RES = _re.compile(
        r"^(\S+) initRes: (\S+) finalRes: (\S+) nIters: (\d+)\s*$")
    _RE_RES_LINE = _re.compile(r"^\S+ initRes: .*\n", _re.M)
    _RE_CD = _re.compile(r"^CD: (\S+) final: (\S+)\s*$")

    def _own_log_path():
        """The log THIS PROCESS IS WRITING, resolved from its own fd 1 rather
        than guessed by name.

        Resolving it this way is the point: the producer cannot read a sibling
        arm's file, cannot read a stale log left by an earlier container, and
        cannot silently read nothing if the arm's redirect is ever changed --
        any of which a hard-coded `XM.log` would do without saying so."""
        try:
            path = os.readlink("/proc/self/fd/1")
        except OSError as exc:                     # noqa: BLE001
            return None, "fd 1 is not resolvable: %s" % exc
        if not path.startswith("/") or path.endswith(" (deleted)"):
            return None, "fd 1 does not name a live file on disk: %r" % path
        if not os.path.isfile(path):
            return None, "fd 1 resolves to %r, not a regular file" % path
        return path, None

    def _parse_primal_blocks(path):
        """Per-primal residual histories, parsed from a solver log ON DISK.

        One block per `Running Primal Solver`.  Within a block, every
        `<var> initRes: <a> finalRes: <b> nIters: <n>` line is a sample of that
        equation's residual at the enclosing `Time = <n>`, printed by
        `DAUtility::primalResidualControl` under `if (printToScreen)`.  The
        sampling interval is the `printInterval` DAOption; THIS REPAIR DOES NOT
        CHANGE IT and the histories are therefore at the registered
        resolution."""
        blocks, cur, t = [], None, None
        with open(path, "r", errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if line.startswith(_BLOCK):
                    if cur is not None:
                        blocks.append(cur)
                    cur, t = {"times": [], "equations": {}, "CD_final": None}, None
                    continue
                if cur is None:
                    continue
                m = _RE_TIME.match(line)
                if m:
                    t = int(m.group(1))
                    continue
                m = _RE_RES.match(line)
                if m:
                    try:
                        a, b, n = float(m.group(2)), float(m.group(3)), int(m.group(4))
                    except ValueError:
                        continue
                    eq = cur["equations"].setdefault(
                        m.group(1),
                        {"time": [], "initRes": [], "finalRes": [], "nIters": []})
                    eq["time"].append(t)
                    eq["initRes"].append(a)
                    eq["finalRes"].append(b)
                    eq["nIters"].append(n)
                    if t not in cur["times"]:
                        cur["times"].append(t)
                    continue
                m = _RE_CD.match(line)
                if m:
                    try:
                        cur["CD_final"] = float(m.group(2))
                    except ValueError:
                        pass
        if cur is not None:
            blocks.append(cur)
        return blocks

    def _plant_short_read(path, blocks):
        """PLANTED-ZERO CONTROL, run in the SAME invocation as the reading it
        licenses (`CLAUDE.md` rule 3).

        A parser that has only ever been shown reading THREE histories is not
        evidence that there are three.  This strips the `initRes:` lines of the
        LAST primal block from a SCRATCH COPY, re-parses FROM DISK, and requires
        the read to come back with exactly one fewer block carrying residuals.
        If the planted short read is invisible, the producer REFUSES and writes
        nothing -- the plant is a precondition on the reading, not a note
        beside it."""
        live = sum(1 for b in blocks if b["equations"])
        out = {"demonstrated": False, "live_blocks_with_residuals": live,
               "target": "the LAST primal block's initRes lines",
               "note": "a reader not shown able to read SHORT is not evidence "
                       "that the list is COMPLETE"}
        if live < 1:
            out["why"] = "no primal block carries residuals; nothing to plant into"
            return out
        tdir = _tempfile.mkdtemp(prefix="so3af2_plant_")
        try:
            with open(path, "r", errors="replace") as fh:
                parts = fh.read().split(_BLOCK)
            if len(parts) < 2:
                out["why"] = "no %r marker to plant into" % _BLOCK
                return out
            parts[-1] = _RE_RES_LINE.sub("", parts[-1])
            planted_path = os.path.join(tdir, "planted.log")
            with open(planted_path, "w") as fh:
                fh.write(_BLOCK.join(parts))
            planted = sum(1 for b in _parse_primal_blocks(planted_path)
                          if b["equations"])
        finally:
            _shutil.rmtree(tdir, ignore_errors=True)
        out["planted_blocks_with_residuals"] = planted
        out["demonstrated"] = (planted == live - 1)
        return out

    def _history_from_blocks(blocks, i_sc):
        """The i-th primal's history, or None.  Order is solve order, and the
        caller CHECKS that against the functional rather than trusting it."""
        usable = [b for b in blocks if b["equations"]]
        if i_sc >= len(usable):
            return None
        b = usable[i_sc]
        return {"scenario_index": i_sc,
                "times": b["times"],
                "n_samples": len(b["times"]),
                "equations": b["equations"],
                "CD_final_in_log": b["CD_final"],
                "source": "solver log -- section 5 F1, 'counted from the log'",
                "resolution": "sampled at the registered printInterval, which "
                              "this repair does NOT change"}

    def _enumerate_for_refusal(scenario):
        """ADDENDUM 12. What the object ACTUALLY exposes, reported INSIDE the
        refusal that could not find a residual history.

        THIS ADDS WHAT THE REFUSAL REPORTS, NEVER WHAT IT DECIDES. The refusal
        below is unchanged -- same trigger, same `rc=7`, same
        RESIDUAL_HISTORY_UNAVAILABLE, still no artefact written. A refusal that
        starts producing a product is not a refusal.

        WHY HERE AND NOT IN A SEPARATE ARM: a diagnostic that must re-reach this
        state costs a whole run and can stall before arriving -- as one did,
        twice, for 6.0 core-min and no enumeration. THE INSTRUMENT THAT ALREADY
        REACHES THE MOMENT IS ASKED TO SAY WHAT IT SAW, at the moment the
        question arises, rather than reconstructing that moment from scratch.

        AN UNREADABLE ATTRIBUTE IS RECORDED, NEVER SKIPPED: a silently omitted
        attribute is exactly the blindness this enumeration exists to remove.
        NOTHING HERE RAISES -- a failure to enumerate must not replace the
        refusal it is describing."""
        out = {}
        try:
            node = prob.model
            path = []
            for part in (scenario, "coupling", "solver"):
                node = getattr(node, part, None)
                path.append(part)
                if node is None:
                    out["resolved_to"] = "/".join(path[:-1])
                    out["missing_at"] = part
                    return out
            out["resolved_to"] = "/".join(path)

            def describe(obj, label):
                d = {"label": label, "type": type(obj).__name__, "attributes": {}}
                try:
                    names = sorted(set(dir(obj)))
                except Exception as exc:          # noqa: BLE001
                    d["dir_failed"] = str(exc)
                    return d
                for name in names:
                    if name.startswith("__"):
                        continue
                    try:
                        val = getattr(obj, name)
                    except Exception as exc:      # noqa: BLE001
                        d["attributes"][name] = {"UNREADABLE": str(exc)}
                        continue
                    rec = {"type": type(val).__name__, "callable": callable(val)}
                    try:
                        rec["len"] = len(val)
                        rec["sequence_shaped"] = True
                    except Exception:             # noqa: BLE001
                        rec["sequence_shaped"] = False
                    d["attributes"][name] = rec
                return d

            out["solver"] = describe(node, "%s.coupling.solver" % scenario)
            das = getattr(node, "DASolver", None)
            if das is None:
                out["DASolver"] = "ABSENT on the solver object"
            else:
                out["DASolver"] = describe(das, "%s.coupling.solver.DASolver" % scenario)
        except Exception as exc:                  # noqa: BLE001
            out["ENUMERATION_FAILED"] = str(exc)
        return out

    # ---- ADDENDUM 15.  THE LOG IS RESOLVED, PARSED AND ITS READER IS PLANTED
    # ---- AGAINST, ALL BEFORE ANY HISTORY IS ACCEPTED.
    import sys as _sys
    _sys.stdout.flush()
    _log_path, _log_why = _own_log_path()
    if _log_path is None:
        _fail("RESIDUAL_LOG_UNRESOLVABLE", {
            "why": _log_why,
            "note": "section 5 F1 is scored 'counted from the log, both ways'. "
                    "If this process cannot identify the log it is writing, it "
                    "cannot perform the registered reading, and it refuses "
                    "rather than substituting a route the registration does "
                    "not name -- which is the defect ADDENDUM 15 corrects."})
    _blocks = _parse_primal_blocks(_log_path)
    _plant = _plant_short_read(_log_path, _blocks)
    if not _plant["demonstrated"]:
        _fail("RESIDUAL_PLANT_NOT_VISIBLE", {
            "log": _log_path, "control": _plant,
            "note": "CLAUDE.md rule 3. A zero -- or a THREE -- from a reader "
                    "not shown able to see something else is not evidence."})
    print("SO3aF2 PRODUCER RESIDUAL SOURCE: log=%s blocks=%d "
          "blocks_with_residuals=%d plant_demonstrated=%s"
          % (_log_path, len(_blocks), _plant["live_blocks_with_residuals"],
             _plant["demonstrated"]))

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
        h = _history_from_blocks(_blocks, i_sc)
        if h is None:
            _fail("RESIDUAL_HISTORY_UNAVAILABLE", {
                "scenario": sc,
                "note": "refusing to write a short residual_histories list; "
                        "see (B) -- a short list reaches the reader as a "
                        "CONVERGENCE DISAGREEMENT, which is a finding about the "
                        "multipoint assembly this file would have manufactured",
                "route": "solver log, resolved from this process's own fd 1 -- "
                         "section 5 F1, 'counted from the log, both ways'",
                "log": _log_path,
                "blocks_seen": len(_blocks),
                "blocks_with_residuals": _plant["live_blocks_with_residuals"],
                "scenarios_wanted": len(SCENARIOS),
                "planted_control": _plant,
                "what_the_object_exposes": _enumerate_for_refusal(sc),
                "this_enumeration_decides_nothing":
                    "ADDENDUM 12. The refusal is unchanged -- same trigger, same "
                    "rc=7, same reason, still no artefact. This field is what the "
                    "refusal REPORTS, not what it DECIDES."})
        # ---- ADDENDUM 15.  BIND BLOCK i TO SCENARIO i BY MEASUREMENT, NOT BY
        # ---- ORDER.  The i-th log block is assumed to be the i-th scenario's
        # ---- primal; that assumption is CHECKED against the functional this
        # ---- loop just read from the model, so a scenario-ordering change
        # ---- cannot silently attach the wrong history to the wrong point.
        _cdl = h["CD_final_in_log"]
        if _cdl is None or abs(_cdl - cd) > 1.0e-12 * max(1.0, abs(cd)):
            _fail("RESIDUAL_HISTORY_SCENARIO_MISMATCH", {
                "scenario": sc, "scenario_index": i_sc,
                "CD_from_model": cd, "CD_final_in_log_block": _cdl,
                "note": "the i-th primal block in the log does not carry the "
                        "functional the model reports for the i-th scenario, so "
                        "the block-to-scenario mapping is not established. "
                        "Attaching a history to the wrong point would be a "
                        "confident wrong answer, which is the one kind this "
                        "item may not produce."})
        histories.append(h)

    if len(histories) != len(SCENARIOS):
        _fail("RESIDUAL_HISTORY_COUNT", {"got": len(histories),
                                         "want": len(SCENARIOS)})

    try:
        j_val = float(prob.get_val("obj.J")[0])
    except Exception as exc:           # noqa: BLE001
        _fail("OBJECTIVE_UNREADABLE", {"error": str(exc)})

    art = ARTEFACT_PATH
    os.makedirs(os.path.dirname(art), exist_ok=True)
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
