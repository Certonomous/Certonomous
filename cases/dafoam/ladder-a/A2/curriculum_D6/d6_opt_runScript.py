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
d6_fd_endpoint.py and d6_ref_off.py exec the header exactly as D4's FD
instrument does.
"""
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
# which optimizer to use. Options are: IPOPT (default), SLSQP, and SNOPT
parser.add_argument("-optimizer", help="optimizer to use", type=str, default="IPOPT")
# which task to run. Options are: run_driver (default), run_model, compute_totals, check_totals
parser.add_argument("-task", help="type of run to do", type=str, default="run_driver")
args = parser.parse_args()

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


if args.task == "run_driver":
    # solve the three CL targets on the three patchV DVs at once
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
