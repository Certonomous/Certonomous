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
CL_target = 0.5
aoa0 = 4.0
rho0 = p0 / T0 / 287.0
A0 = 45.5

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

# Mesh deformation setup
meshOptions = {
    "gridFile": os.getcwd(),
    "fileType": "OpenFOAM",
    # point and normal for the symmetry plane
    "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]]],
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
        nRefAxPts = self.geometry.nom_addRefAxis(name="wingAxis", xFraction=0.25, alignIndex="k")

        # Set up global design variables. We dont change the root twist
        def twist(val, geo):
            for i in range(1, nRefAxPts):
                geo.rot_z["wingAxis"].coef[i] = -val[i - 1]

        # add twist variable
        self.geometry.nom_addGlobalDV(dvName="twist", value=np.array([0] * (nRefAxPts - 1)), func=twist)

        # select the FFD points to move
        pts = self.geometry.DVGeo.getLocalIndex(0)
        indexList = pts[:, :, :].flatten()
        PS = geo_utils.PointSelect("list", indexList)
        nShapes = self.geometry.nom_addLocalDV(dvName="shape", pointSelect=PS)

        # setup the volume and thickness constraints
        leList = [[0.1, 0, 0.01], [7.5, 0, 13.9]]
        teList = [[4.9, 0, 0.01], [8.9, 0, 13.9]]
        self.geometry.nom_addThicknessConstraints2D("thickcon", leList, teList, nSpan=10, nChord=10)
        self.geometry.nom_addVolumeConstraint("volcon", leList, teList, nSpan=10, nChord=10)
        # add the LE/TE constraints
        self.geometry.nom_add_LETEConstraint("lecon", volID=0, faceID="iLow")
        self.geometry.nom_add_LETEConstraint("tecon", volID=0, faceID="iHigh")

        # add the design variables to the dvs component's output
        self.dvs.add_output("twist", val=np.array([0] * (nRefAxPts - 1)))
        self.dvs.add_output("shape", val=np.array([0] * nShapes))
        self.dvs.add_output("patchV", val=np.array([U0, aoa0]))
        # manually connect the dvs output to the geometry and scenario1
        self.connect("twist", "geometry.twist")
        self.connect("shape", "geometry.shape")
        self.connect("patchV", "scenario1.patchV")

        # define the design variables
        self.add_design_var("twist", lower=-10.0, upper=10.0, scaler=0.1)
        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)
        self.add_design_var("patchV", lower=[U0, 0.0], upper=[U0, 10.0], scaler=0.1)

        # add objective and constraints to the top level
        self.add_objective("scenario1.aero_post.CD", scaler=1.0)
        self.add_constraint("scenario1.aero_post.CL", equals=CL_target, scaler=1.0)
        self.add_constraint("geometry.thickcon", lower=0.5, upper=3.0, scaler=1.0)
        self.add_constraint("geometry.volcon", lower=1.0, scaler=1.0)
        self.add_constraint("geometry.tecon", equals=0.0, scaler=1.0, linear=True)
        self.add_constraint("geometry.lecon", equals=0.0, scaler=1.0, linear=True)


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
elif args.task == "decomp":
    # ---------------------------------------------------------------------
    # ACT-D DRAG DECOMPOSITION -- the ONLY block added to runScript_AeroOnly.py
    # (pristine md5 2906d52a5dbed2bacbaeaf85a37d3fe8). Frozen with
    # cases/dafoam/A2_DRAG_DECOMPOSITION_PREREGISTRATION.md. Evaluates the
    # pre-registered design-variable rows and prints one tagged block each.
    # Nothing above this line is modified.
    # ---------------------------------------------------------------------
    import json as _json

    _rowsfile = os.environ.get("DECOMP_ROWS", "a2_decomposition_rows.json")
    _spec = _json.load(open(_rowsfile))
    _rank = MPI.COMM_WORLD.rank

    def _p(_m):
        if _rank == 0:
            print(_m, flush=True)

    def _getf(_name):
        for _n in ("scenario1.aero_post.functionals." + _name, "scenario1.aero_post." + _name):
            try:
                return float(np.array(prob.get_val(_n)).ravel()[0])
            except Exception:
                continue
        raise RuntimeError("cannot read function " + _name)

    _p("DECOMP_SPEC_FILE %s" % _rowsfile)
    _p("DECOMP_NROWS %d" % len(_spec["rows"]))
    for _row in _spec["rows"]:
        _rid = _row["id"]
        _p("DECOMP_ROW_BEGIN %s" % _rid)
        _tw = np.array(_row["twist"], dtype=float)
        _sh = np.array(_row["shape"], dtype=float)
        _pv = np.array(_row["patchV"], dtype=float)
        prob.set_val("twist", _tw)
        prob.set_val("shape", _sh)
        prob.set_val("patchV", _pv)
        # PLANTED-ZERO CONTROL 1 (rule 3): read the design variables BACK out of the
        # problem rather than trusting the write. A row whose vector did not take is
        # REFUSED here -- it must never be able to return the baseline drag quietly.
        _dtw = float(np.max(np.abs(prob.get_val("twist") - _tw)))
        _dsh = float(np.max(np.abs(prob.get_val("shape") - _sh)))
        _dpv = float(np.max(np.abs(prob.get_val("patchV") - _pv)))
        _p("DECOMP_SETCHECK %s twist %.3e shape %.3e patchV %.3e" % (_rid, _dtw, _dsh, _dpv))
        if max(_dtw, _dsh, _dpv) > 1e-12:
            _p("DECOMP_REFUSE %s design variables did not take" % _rid)
            raise RuntimeError("DV set/readback mismatch on row %s" % _rid)
        if _row.get("trim_to_CL") is not None:
            _p("DECOMP_TRIM_BEGIN %s target_CL %.6f" % (_rid, _row["trim_to_CL"]))
            optFuncs.findFeasibleDesign(
                ["scenario1.aero_post.CL"],
                ["patchV"],
                targets=[_row["trim_to_CL"]],
                designVarsComp=[1],
            )
            _p("DECOMP_TRIM_END %s AoA %.11f" % (_rid, float(prob.get_val("patchV")[1])))
        prob.run_model()
        _cd = _getf("CD")
        _cl = _getf("CL")
        _tc = np.array(prob.get_val("geometry.thickcon"), dtype=float)
        _vc = float(np.array(prob.get_val("geometry.volcon")).ravel()[0])
        _aoa = float(prob.get_val("patchV")[1])
        # PLANTED-ZERO CONTROL 2 (rule 3): thickcon reads exactly 1.0 on every one of
        # its 100 points on the baseline geometry and spans [0.500101, 1.727944] on the
        # final one. A shape vector that never reached the mesh reads 1.0 here, so this
        # is an independent, geometry-side witness that the reader can see a non-zero.
        _p(
            "DECOMP_RESULT %s CD %.11f CL %.11f AoA %.11f thickcon_min %.9f thickcon_max %.9f volcon %.11f"
            % (_rid, _cd, _cl, _aoa, float(_tc.min()), float(_tc.max()), _vc)
        )
        _p("DECOMP_ROW_END %s" % _rid)
    _p("DECOMP_ALL_ROWS_DONE")
else:
    print("task arg not found!")
    exit(1)
