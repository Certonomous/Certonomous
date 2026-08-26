#!/usr/bin/env python
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
    "primalMinResTolDiff": 1.0e4,
    "primalMinIters": 1000,
    "printInterval": 10,
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
    "transonicPCOption": 1,
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


# Top class to setup the optimization problem
class Top(Multipoint):
    def setup(self):

        # create the builder to initialize the DASolvers
        dafoam_builder = DAFoamBuilder(daOptions, meshOptions, scenario="aerodynamic")
        dafoam_builder.initialize(self.comm)

        # add the design variable component to keep the top level design variables
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])

        # add the mesh component
        self.add_subsystem("mesh", dafoam_builder.get_mesh_coordinate_subsystem())

        # add the geometry component (FFD)
        self.add_subsystem("geometry", OM_DVGEOCOMP(file="FFD/wingFFD.xyz", type="ffd"))

        # add a scenario (flow condition) for optimization, we pass the builder
        # to the scenario to actually run the flow and adjoint
        self.mphys_add_scenario("scenario1", ScenarioAerodynamic(aero_builder=dafoam_builder))

        # need to manually connect the x_aero0 between the mesh and geometry components
        # here x_aero0 means the surface coordinates of structurally undeformed mesh
        self.connect("mesh.x_aero0", "geometry.x_aero_in")
        # need to manually connect the x_aero0 between the geometry component and the scenario1
        # scenario group
        self.connect("geometry.x_aero0", "scenario1.x_aero")

    def configure(self):

        # get the surface coordinates from the mesh component
        points = self.mesh.mphys_get_surface_mesh()

        # add pointset to the geometry component
        self.geometry.nom_add_discipline_coords("aero", points)

        # set the triangular points to the geometry component for geometric constraints
        tri_points = self.mesh.mphys_get_triangulated_surface()
        self.geometry.nom_setConstraintSurface(tri_points)

        # Create reference axis for the twist variable
        nRefAxPts = self.geometry.nom_addRefAxis(name="wingAxis", xFraction=0.25, alignIndex="j")

        # Set up global design variables. We dont change the root twist
        def twist(val, geo):
            for i in range(1, nRefAxPts):
                geo.rot_y["wingAxis"].coef[i] = -val[i - 1]

        # add twist variable
        self.geometry.nom_addGlobalDV(dvName="twist", value=np.array([0] * (nRefAxPts - 1)), func=twist)

        # D8 EDIT 3 (twist-only): the `shape` local FFD DV is NOT added.

        # setup the volume and thickness constraints
        # NOTE: the LE and TE lists are not parallel lines anymore, these two lists define lines that
        # are close to the leading and trailing edges while being completely within the wing surface
        leList = [[0.1, 0, 0.01], [7.5, 0, 13.9]]
        teList = [[4.9, 0, 0.01], [8.9, 0, 13.9]]
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
        self.geometry.nom_addThicknessConstraints2D("thickcon", leList, teList, nSpan=25, nChord=30)
        self.geometry.nom_addVolumeConstraint("volcon", leList, teList, nSpan=25, nChord=30)
        # D8 EDIT 4: LE/TE constraints act on local shape DVs; none exist here.

        # add the design variables to the dvs component's output
        self.dvs.add_output("twist", val=np.array([0] * (nRefAxPts - 1)))
        self.dvs.add_output("patchV", val=np.array([U0, aoa0]))
        # manually connect the dvs output to the geometry and scenario1
        self.connect("twist", "geometry.twist")
        self.connect("patchV", "scenario1.patchV")

        # define the design variables
        self.add_design_var("twist", lower=-10.0, upper=10.0, scaler=0.1)
        self.add_design_var("patchV", lower=[U0, 0.0], upper=[U0, 10.0], scaler=0.1)

        # add objective and constraints to the top level
        self.add_objective("scenario1.aero_post.CD", scaler=1.0)
        self.add_constraint("scenario1.aero_post.CL", equals=CL_target, scaler=1.0)
        self.add_constraint("geometry.thickcon", lower=0.5, upper=3.0, scaler=1.0)
        self.add_constraint("geometry.volcon", lower=1.0, scaler=1.0)


# OpenMDAO setup
prob = om.Problem()
prob.model = Top()
prob.setup(mode="rev")
om.n2(prob, show_browser=False, outfile="mphys.html")

# initialize the optimization function
optFuncs = OptFuncs(daOptions, prob)

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
        "max_iter": 3,
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
    # solve CL
    optFuncs.findFeasibleDesign(["scenario1.aero_post.CL"], ["patchV"], targets=[CL_target], designVarsComp=[1])
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
elif args.task == "optd8":
    import json
    try:
        _dv = prob.model.get_design_vars()
        _rs = prob.model.get_responses()
        if MPI.COMM_WORLD.rank == 0:
            print("D8_DVS %s" % sorted([(k, int(v.get("size", -1))) for k, v in _dv.items()]))
            print("D8_RESPONSES %s" % sorted([(k, int(v.get("size", -1))) for k, v in _rs.items()]))
    except Exception as _e:
        if MPI.COMM_WORLD.rank == 0:
            print("D8_DVS_ERR %r" % (_e,))
    prob.run_model()
    cd_cold = float(prob.get_val("scenario1.aero_post.CD")[0])
    cl_cold = float(prob.get_val("scenario1.aero_post.CL")[0])
    if MPI.COMM_WORLD.rank == 0:
        print("D8_COLD_CD %r" % cd_cold)
        print("D8_COLD_CL %r" % cl_cold)
    optFuncs.findFeasibleDesign(["scenario1.aero_post.CL"], ["patchV"], targets=[CL_target],
                                designVarsComp=[1], epsFD=[1.0e-1], tol=1.0e-3, maxIter=4)
    prob.run_model()
    cd_s = float(prob.get_val("scenario1.aero_post.CD")[0])
    cl_s = float(prob.get_val("scenario1.aero_post.CL")[0])
    dv_s = {"twist": [float(x) for x in prob.get_val("twist")],
            "patchV": [float(x) for x in prob.get_val("patchV")]}
    if MPI.COMM_WORLD.rank == 0:
        print("D8_START_CD %r" % cd_s)
        print("D8_START_CL %r" % cl_s)
        print("D8_START_DVS %s" % json.dumps(dv_s))
        open("/mnt/d8_start_dvs.json", "w").write(json.dumps({"CD": cd_s, "CL": cl_s, "dvs": dv_s}, indent=1))
    prob.run_driver()
    cd_f = float(prob.get_val("scenario1.aero_post.CD")[0])
    cl_f = float(prob.get_val("scenario1.aero_post.CL")[0])
    dv_f = {"twist": [float(x) for x in prob.get_val("twist")],
            "patchV": [float(x) for x in prob.get_val("patchV")]}
    if MPI.COMM_WORLD.rank == 0:
        print("D8_FINAL_CD %r" % cd_f)
        print("D8_FINAL_CL %r" % cl_f)
        print("D8_FINAL_DVS %s" % json.dumps(dv_f))
        open("/mnt/d8_dvs.json", "w").write(json.dumps({"CD": cd_f, "CL": cl_f, "dvs": dv_f}, indent=1))
    prob.set_val("twist", np.array(dv_f["twist"]))
    prob.set_val("patchV", np.array(dv_f["patchV"]))
    prob.run_model()
    cd_e = float(prob.get_val("scenario1.aero_post.CD")[0])
    if MPI.COMM_WORLD.rank == 0:
        print("D8_ADJPOINT_CD %r" % cd_e)
    _of = "scenario1.aero_post.CD"
    try:
        tot = prob.compute_totals(of=[_of], wrt=["twist", "patchV"])
    except Exception as _e1:
        if MPI.COMM_WORLD.rank == 0:
            print("D8_OF_FALLBACK %r" % (_e1,))
        _of = "scenario1.aero_post.functionals.CD"
        tot = prob.compute_totals(of=[_of], wrt=["twist", "patchV"])
    if MPI.COMM_WORLD.rank == 0:
        _out = {"CD": cd_e}
        for dvn in ("twist", "patchV"):
            row = np.atleast_1d(np.array(tot[(_of, dvn)]).ravel())
            _out[dvn] = [float(x) for x in row]
            for i, v in enumerate(row):
                print("ADJ_DERIV dv=%s idx=%d deriv=%r" % (dvn, i, float(v)))
        open("/mnt/d8_adj.json", "w").write(json.dumps(_out, indent=1))
    if MPI.COMM_WORLD.rank == 0:
        print("D8_OPT_ARM_COMPLETE")
elif args.task == "fdsub8":
    import json
    plan = json.loads(open("/mnt/fdplan.json").read())
    dvs0 = json.loads(open("/mnt/d8_dvs.json").read())["dvs"]
    for _k in sorted(dvs0):
        prob.set_val(_k, np.array(dvs0[_k]))
    prob.run_model()
    cd0 = float(prob.get_val("scenario1.aero_post.CD")[0])
    if MPI.COMM_WORLD.rank == 0:
        print("FD_BASELINE_CD %r" % cd0)
    base = {}
    for dv in sorted(set(p["dv"] for p in plan)):
        base[dv] = prob.get_val(dv).copy()
    for p in plan:
        dv, idx, step = p["dv"], int(p["idx"]), float(p["step"])
        vals = {}
        for sgn in (1.0, -1.0):
            x = base[dv].copy()
            x[idx] = x[idx] + sgn * step
            prob.set_val(dv, x)
            prob.run_model()
            vals[sgn] = float(prob.get_val("scenario1.aero_post.CD")[0])
            if MPI.COMM_WORLD.rank == 0:
                print("FD_POINT dv=%s idx=%d step=%r sgn=%+g CD=%r" % (dv, idx, step, sgn, vals[sgn]))
        prob.set_val(dv, base[dv].copy())
        d = (vals[1.0] - vals[-1.0]) / (2.0 * step)
        if MPI.COMM_WORLD.rank == 0:
            print("FD_DERIV dv=%s idx=%d step=%r deriv=%r" % (dv, idx, step, d))
    if MPI.COMM_WORLD.rank == 0:
        print("D8_FD_ARM_COMPLETE")
else:
    print("task arg not found!")
    exit(1)
