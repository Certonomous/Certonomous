#!/usr/bin/env python
r"""Curriculum D19M -- NACA0012 COMPRESSIBLE ALPHA-MULTIPOINT producer.

`DARhoSimpleFoam`, M 0.288, A1's own 4,032-cell mesh, np = 1, weighted objective
`J = SUM_i w_i * CD_i(alpha_i)` over ONE SHARED `shape` vector, assembled by an
`om.ExecComp`.

===========================================================================
THIS PRODUCER IS **NEW**, AND THE D19O/D15 HEADER-IDENTITY CLAIM IS NOT
AVAILABLE TO THIS ITEM.  THAT IS STATED FIRST BECAUSE IT IS A REAL LOSS.
===========================================================================
`curriculum_D19O/d19o_runScript.py` is BYTE-IDENTICAL to D19R's, which is
D15's, so D19O could assert `HEADER_MD5_SHARED_WITH_D15` and stand its whole
reproduction claim on the bytes.  **A multipoint model cannot be that file.** It
needs three `DAFoamBuilder`s, three mesh subsystems, three `patchV{i}` outputs
and an `ExecComp`, and none of those exist in a single-point header.

**So this file is a NEW producer with its own md5 and NO inherited reproduction
claim, and the pre-registration says so rather than implying continuity that
does not exist.**  What IS carried across, and is checkable line by line, is the
PHYSICS BLOCK -- `U0`, `p0`, `T0`, `nuTilda0`, `A0`, `rho0`, `daOptions`'
`solverName` / `primalMinResTol` / `primalBC` / `function` / `adjEqnOption` /
`normalizeStates` / `inputInfo` -- which is quoted from D19O's producer
unchanged.  `d19m_xf.py` asserts that block's md5 separately from the file's, so
"the physics is D15's" is a property of bytes even though "the model is D15's"
is no longer true.

===========================================================================
THE STRUCTURE, AND THE TWO COLLISIONS IT IS BUILT NOT TO REPEAT
===========================================================================
**ONE `DASolver` PER OPERATING POINT, EACH IN ITS OWN `run_directory`, BEHIND
ONE SHARED `OM_DVGEOCOMP`.**

  * **SO-3aR died** because three `DAFoamBuilder`s were given NO `run_directory`,
    so three independent `DASolver` instances shared one case directory and each
    renamed its solution to the same time (`pyDAFoam.renameSolution`).  `RUN_DIRS`
    gives each point its own full case copy, following `d6r_opt_runScript.py`.
  * **D6 built `geometry_<pt>` PER SCENARIO.**  That makes the objective a
    statement about three design vectors that happen to be equal.  **ONE SHARED
    GEOMETRY is what makes `J` a statement about ONE design vector**, which is
    the whole point of a multipoint optimisation.

**ALPHA IS THE OPERATING POINT AND IS NOT A DESIGN VARIABLE.**  `patchV{i}` is a
fixed per-scenario output carrying `[U0, ALPHAS[i]]`, promoted through `dvs` AND
connected to the scenario, so both read paths resolve to the same value and
`G-ALPHA` can check either.  `add_design_var("patchV", ...)` is GONE -- D19O had
it, because D19O trimmed alpha to a lift target; here nothing is trimmed.

**CONSEQUENCE, REGISTERED RATHER THAN DISCOVERED: `CL` IS UNCONSTRAINED.**  With
no alpha DV there is nothing to trim with, so each point's `CL` floats.  **The
three-`CL` triple therefore travels with every drag number this item publishes.**
A weighted-drag reduction at unstated lift is not a reportable number.

**THE ALPHA BRACKET IS QUOTED FROM MEASUREMENT, NOT CHOSEN.**  Its centre is
`4.787333582` degrees -- D19O's OWN measured trimmed angle at `CL_target = 0.5`
on this exact compressible case, read from
`.../CURRICULUM-D19O-.../O-S/d19o_O.json` -> `dv_trimmed.patchV[1]`.  The +/- 2
degree half-width and the equal weights are LANE-CHOSEN and registered as
lane-chosen.  All three points lie inside the tutorial's own `[0.0, 10.0]` aoa
bound and well below stall for NACA0012 at this Reynolds number.
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
from dafoam.mphys import DAFoamBuilder, OptFuncs
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP
from pygeo import geo_utils


parser = argparse.ArgumentParser()
parser.add_argument("-optimizer", help="optimizer to use", type=str, default="IPOPT")
parser.add_argument("-task", help="type of run to do", type=str, default="run_driver")
args = parser.parse_args()

# =============================================================================
# THE PHYSICS BLOCK -- QUOTED UNCHANGED FROM curriculum_D19O/d19o_runScript.py
# (itself D19R's, itself D15's).  `d19m_xf.py` asserts this block's md5.
# =============================================================================
# ---- D19M_PHYSICS_BEGIN ----
U0 = 100.0
p0 = 101325.0
T0 = 300.0
nuTilda0 = 4.5e-5
CL_target = 0.5
A0 = 0.1
# rho is used for normalizing CD and CL
rho0 = p0 / T0 / 287

# Input parameters for DAFoam
daOptions = {
    "designSurfaces": ["wing"],
    "solverName": "DARhoSimpleFoam",
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
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 1, "jacMatReOrdering": "rcm"},
    "normalizeStates": {
        "U": U0,
        "p": p0,
        "T": T0,
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
# ---- D19M_PHYSICS_END ----

# =============================================================================
# THE MULTIPOINT REGISTRATION
# =============================================================================
# THE CENTRE IS A QUOTATION, NOT A CHOICE.  4.787333582 deg is D19O's MEASURED
# trimmed angle at CL_target = 0.5 on this exact compressible case, read from
# `.../CURRICULUM-D19O-.../O-S/d19o_O.json` -> `dv_trimmed.patchV[1]`.  Using the
# incompressible tutorial's 5.13918623195176 here would have been a number from a
# different solver on a different state equation.
aoa0 = 4.787333582
# THREE alpha, degrees: aoa0 - 2, aoa0, aoa0 + 2.  WRITTEN OUT rather than
# computed, so the file states its own operating points and a reader does not
# have to evaluate arithmetic to know what ran.  All three are inside the
# tutorial's own [0.0, 10.0] aoa bound.
ALPHAS = [2.787333582, 4.787333582, 6.787333582]
# EQUAL WEIGHTS.  A CHOICE, NOT A DEFAULT, and registered as one.
WEIGHTS = [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]
SCENARIOS = ["point%d" % i for i in range(len(ALPHAS))]
# ONE FULL CASE COPY PER POINT.  The SO-3aR collision needs two writers in one
# directory; this gives each point its own.
RUN_DIRS = {sc: "mp%d" % i for i, sc in enumerate(SCENARIOS)}


def mesh_options_for(point):
    return {
        "gridFile": os.path.join(os.getcwd(), RUN_DIRS[point]),
        "fileType": "OpenFOAM",
        # point and normal for the symmetry plane
        "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]],
                           [[0.0, 0.0, 0.1], [0.0, 0.0, 1.0]]],
    }


# The ExecComp expression, BUILT FROM `WEIGHTS` rather than written as a literal,
# so a weight changed above cannot leave a stale coefficient in the objective.
OBJ_EXPR = "J = " + " + ".join("%r*CD%d" % (w, i) for i, w in enumerate(WEIGHTS))


class Top(Multipoint):
    def setup(self):

        # ONE builder per operating point -- one DASolver per scenario -- EACH IN
        # ITS OWN `run_directory`.  They share `daOptions` because the three points
        # differ ONLY in alpha, which is a boundary condition and not a mesh or a
        # solver setting.
        self.builders = []
        for sc in SCENARIOS:
            b = DAFoamBuilder(daOptions, mesh_options_for(sc), scenario="aerodynamic",
                              run_directory=RUN_DIRS[sc])
            b.initialize(self.comm)
            self.builders.append(b)

        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])

        # one mesh coordinate subsystem per scenario (each DASolver needs its own)
        for i, sc in enumerate(SCENARIOS):
            self.add_subsystem("mesh_%s" % sc,
                               self.builders[i].get_mesh_coordinate_subsystem())

        # ---- ONE SHARED GEOMETRY.  This is what makes J a statement about ONE
        # ---- design vector rather than about three that happen to be equal.
        self.add_subsystem("geometry", OM_DVGEOCOMP(file="FFD/wingFFD.xyz", type="ffd"))

        for i, sc in enumerate(SCENARIOS):
            self.mphys_add_scenario(sc, ScenarioAerodynamic(aero_builder=self.builders[i]))

        # The SHARED geometry is fed from SCENARIO 0's mesh and feeds ALL THREE
        # scenarios.  WHICH mesh is recorded here rather than left implicit.
        self.connect("mesh_%s.x_aero0" % SCENARIOS[0], "geometry.x_aero_in")
        for sc in SCENARIOS:
            self.connect("geometry.x_aero0", "%s.x_aero" % sc)

        # ---- the weighted objective, assembled by an ExecComp
        self.add_subsystem("obj", om.ExecComp(OBJ_EXPR))
        for i, sc in enumerate(SCENARIOS):
            self.connect("%s.aero_post.CD" % sc, "obj.CD%d" % i)

    def configure(self):

        # surface coordinates from SCENARIO 0's mesh -- see the note in setup()
        points = getattr(self, "mesh_%s" % SCENARIOS[0]).mphys_get_surface_mesh()
        self.geometry.nom_add_discipline_coords("aero", points)

        tri_points = getattr(self, "mesh_%s" % SCENARIOS[0]).mphys_get_triangulated_surface()
        self.geometry.nom_setConstraintSurface(tri_points)

        # ---- the shape function construction, UNCHANGED from D19O's producer.
        # ---- 5x2x2 FFD -> 8 `shape` functions.
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

        # ---- the geometric constraints, UNCHANGED from D19O's producer.  They
        # ---- live on the SHARED geometry, so there is ONE set for the whole
        # ---- multipoint problem rather than three that could disagree.
        leList = [[1e-4, 0.0, 1e-4], [1e-4, 0.0, 0.1 - 1e-4]]
        teList = [[0.998 - 1e-4, 0.0, 1e-4], [0.998 - 1e-4, 0.0, 0.1 - 1e-4]]
        self.geometry.nom_addThicknessConstraints2D("thickcon", leList, teList, nSpan=2, nChord=10)
        self.geometry.nom_addVolumeConstraint("volcon", leList, teList, nSpan=2, nChord=10)
        self.geometry.nom_addLERadiusConstraints("rcon", leList, 2, [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0])

        # ---- ONE shared `shape` vector across all three scenarios
        self.dvs.add_output("shape", val=np.array([0] * len(shapes)))
        self.connect("shape", "geometry.shape")

        # ---- the operating points.  ONE `patchV{i}` per scenario, differing ONLY
        # ---- in the angle.  Promoted through `dvs` AND connected to the scenario,
        # ---- so BOTH of G-ALPHA's read paths resolve to the same value.
        for i, sc in enumerate(SCENARIOS):
            self.dvs.add_output("patchV%d" % i, val=np.array([U0, ALPHAS[i]]))
            self.connect("patchV%d" % i, "%s.patchV" % sc)

        # ---- the design variables.  `shape` ONLY.  D19O's
        # ---- `add_design_var("patchV", ...)` is GONE and its removal is
        # ---- REGISTERED, not silent: alpha is this item's operating point and
        # ---- cannot simultaneously be a design variable.
        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)

        # ---- the weighted objective and the geometric constraints.  The
        # ---- per-scenario CL is NOT constrained: alpha is the operating point,
        # ---- nothing is trimmed, and the CL triple travels with every drag
        # ---- number instead.
        self.add_objective("obj.J", scaler=1.0)
        self.add_constraint("geometry.thickcon", lower=0.5, upper=3.0, scaler=1.0)
        self.add_constraint("geometry.volcon", lower=1.0, scaler=1.0)
        self.add_constraint("geometry.rcon", lower=0.8, scaler=1.0)


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
        "max_iter": 40,
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

if args.task == "run_driver":
    prob.run_driver()
elif args.task == "run_model":
    prob.run_model()
elif args.task == "compute_totals":
    prob.run_model()
    totals = prob.compute_totals()
    if MPI.COMM_WORLD.rank == 0:
        print(totals)
else:
    print("task arg not found!")
    exit(1)
