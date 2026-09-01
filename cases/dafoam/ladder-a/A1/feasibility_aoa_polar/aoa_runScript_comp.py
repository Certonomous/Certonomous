#!/usr/bin/env python
"""
DAFoam run script for the NACA0012 airfoil at low-speed
"""

# =============================================================================
# Imports
# =============================================================================
import os
import argparse
import numpy as np
import json
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder, OptFuncs
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP


parser = argparse.ArgumentParser()
# which optimizer to use. Options are: IPOPT (default), SLSQP, and SNOPT
parser.add_argument("-optimizer", help="optimizer to use", type=str, default="IPOPT")
# which task to run. Options are: run_driver (default), run_model, compute_totals, check_totals
parser.add_argument("-task", help="type of run to do", type=str, default="run_driver")
args = parser.parse_args()

# =============================================================================
# Input Parameters
# =============================================================================
# THE PHYSICS BLOCK BELOW IS `curriculum_D19M/d19m_runScript.py`'s, CARRIED
# ACROSS AS BYTES BETWEEN ITS OWN MARKERS.  The md5 is asserted IMMEDIATELY
# AFTER the block and BEFORE the model is built, so a drifted byte aborts this
# producer rather than quietly solving different physics.
#
# NO HEADER-IDENTITY CLAIM IS MADE.  D19M's producer is a MULTIPOINT model with
# three DAFoamBuilders and an ExecComp; this is a SINGLE-point model and cannot
# be that file.  What is claimed, and is checkable, is the PHYSICS ONLY.
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

# ---- THE SELF-ASSERT.  Runs at import, before `Top` is instantiated. --------
_PHYS_MD5 = "c66504acc57bd9ef009599e883d2ef3b"
with open(__file__) as _fh:
    _src = _fh.read()
# THE MARKER LITERALS ARE SPLIT ACROSS AN IMPLICIT CONCATENATION ON PURPOSE.
# Written whole, they would be a SECOND occurrence of each marker inside this
# very file, and the count-must-be-1 limb below -- the limb that makes the
# split unambiguous -- would refuse its own producer. G-PHYS caught exactly
# that on the first launch attempt, before any compute.
_B = "# ---- D19M_PHYSICS" "_BEGIN ----\n"
_E = "# ---- D19M_PHYSICS" "_END ----"
if _src.count(_B) != 1 or _src.count(_E) != 1:
    raise SystemExit("AOAC_ABORT physics markers appear %d/%d times, expected 1/1"
                     % (_src.count(_B), _src.count(_E)))
_got = __import__("hashlib").md5(
    _src.split(_B)[1].split(_E)[0].strip().encode()).hexdigest()
if _got != _PHYS_MD5:
    raise SystemExit("AOAC_ABORT physics block md5 %s != D19M's %s -- the physics"
                     " continuity claim rests on these bytes" % (_got, _PHYS_MD5))
print("AOAC_PHYSICS_MD5_PASS %s (D19M's block, byte-identical)" % _got, flush=True)

# ---- THE OPERATING POINT.  Not physics: it is what this item sweeps. --------
aoa0 = float(os.environ["AOA_ALPHA0"])  # FEASIBILITY: supplied per solve;
# NOT trimmed to CL_target -- alpha is this item's operating point, and
# `findFeasibleDesign` is deliberately never called on this path.

# Mesh deformation setup
meshOptions = {
    "gridFile": os.getcwd(),
    "fileType": "OpenFOAM",
    # point and normal for the symmetry plane
    "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]], [[0.0, 0.0, 0.1], [0.0, 0.0, 1.0]]],
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

        # use the shape function to define shape variables for 2D airfoil
        pts = self.geometry.DVGeo.getLocalIndex(0)
        dir_y = np.array([0.0, 1.0, 0.0])
        shapes = []
        for i in range(1, pts.shape[0] - 1):
            for j in range(pts.shape[1]):
                # k=0 and k=1 move together to ensure symmetry
                shapes.append({pts[i, j, 0]: dir_y, pts[i, j, 1]: dir_y})
        # LE/TE shape, the j=0 and j=1 move in opposite directions so that
        # the LE/TE are fixed
        for i in [0, pts.shape[0] - 1]:
            shapes.append({pts[i, 0, 0]: dir_y, pts[i, 0, 1]: dir_y, pts[i, 1, 0]: -dir_y, pts[i, 1, 1]: -dir_y})
        self.geometry.nom_addShapeFunctionDV(dvName="shape", shapes=shapes)

        # setup the volume and thickness constraints
        leList = [[1e-4, 0.0, 1e-4], [1e-4, 0.0, 0.1 - 1e-4]]
        teList = [[0.998 - 1e-4, 0.0, 1e-4], [0.998 - 1e-4, 0.0, 0.1 - 1e-4]]
        self.geometry.nom_addThicknessConstraints2D("thickcon", leList, teList, nSpan=2, nChord=10)
        self.geometry.nom_addVolumeConstraint("volcon", leList, teList, nSpan=2, nChord=10)
        self.geometry.nom_addLERadiusConstraints("rcon", leList, 2, [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0])
        # NOTE: we no longer need to define the sym and LE/TE constraints
        # because these constraints are defined in the above shape function

        # add the design variables to the dvs component's output
        self.dvs.add_output("shape", val=np.array([0] * len(shapes)))
        self.dvs.add_output("patchV", val=np.array([U0, aoa0]))
        # manually connect the dvs output to the geometry and scenario1
        self.connect("patchV", "scenario1.patchV")
        self.connect("shape", "geometry.shape")

        # define the design variables to the top level
        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)
        # here we fix the U0 magnitude and allows the aoa to change
        self.add_design_var("patchV", lower=[U0, 0.0], upper=[U0, 10.0], scaler=0.1)

        # add objective and constraints to the top level
        self.add_objective("scenario1.aero_post.CD", scaler=1.0)
        self.add_constraint("scenario1.aero_post.CL", equals=CL_target, scaler=1.0)
        self.add_constraint("geometry.thickcon", lower=0.5, upper=3.0, scaler=1.0)
        self.add_constraint("geometry.volcon", lower=1.0, scaler=1.0)
        self.add_constraint("geometry.rcon", lower=0.8, scaler=1.0)


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
elif args.task == "sweep":
    # =========================================================================
    # THE CONTINUATION SWEEP.  ONE process, N operating points, `patchV` reset
    # between them and `run_model()` called again.  The DASolver is NOT torn
    # down between points, so each point begins from the previous point's
    # converged state: that IS the continuation, and it is the same mechanism
    # an optimiser's primal sequence uses, which is where the warm per-primal
    # anchors this item is priced from were measured.
    #
    # THREE THINGS THIS BLOCK REFUSES TO DO:
    #   1. It never stops the sweep because one point failed.  A point that
    #      raises is RECORDED and the sweep continues -- a missing point on a
    #      polar is a lie by omission.
    #   2. It never retries, relaxes, or re-tunes a point that did not
    #      converge.  The non-convergence is the finding.
    #   3. It never writes a stall angle.  This block emits alpha, CL, CD,
    #      iteration count and wall time.  Nothing here infers separation from
    #      a solver's stopping behaviour, and the reader is built the same way.
    # =========================================================================
    import json
    import time

    _alphas = [float(x) for x in os.environ["AOA_ALPHAS"].split()]
    _mode = os.environ["AOA_MODE"]
    _pts = os.environ["AOA_POINTS_JSON"]
    _ledger = os.environ.get("AOA_LEDGER", "/mnt/out/LEDGER.tsv")
    _rank0 = MPI.COMM_WORLD.rank == 0

    # THE PER-POINT LEDGER. Appended and FLUSHED AND fsync'd as each point
    # completes, onto the host bind mount, so a fleet kill loses at most the
    # single point in flight and never the points already finished.
    def _ledger_row(*cols):
        if not _rank0:
            return
        with open(_ledger, "a") as _lh:
            _lh.write("\t".join(str(c) for c in cols) + "\n")
            _lh.flush()
            os.fsync(_lh.fileno())

    if _rank0 and not os.path.exists(_ledger):
        _ledger_row("idx", "alpha_deg", "mode", "continued_from", "after_exception",
                    "CL", "CD", "wall_s", "error")

    print("AOA_SWEEP_BEGIN mode=%s n_declared=%d list=[%s]"
          % (_mode, len(_alphas), " ".join("%.10f" % a for a in _alphas)), flush=True)

    _rows = []
    _prev = None
    _after_exc = False
    _executed = 0
    for _i, _a in enumerate(_alphas):
        print("AOA_POINT_BEGIN idx=%d alpha=%.10f mode=%s continued_from=%s "
              "after_exception=%s"
              % (_i, _a, _mode, ("NONE" if _prev is None else "%.10f" % _prev),
                 ("TRUE" if _after_exc else "FALSE")), flush=True)
        _t0 = time.time()
        _err = None
        _cl = None
        _cd = None
        try:
            prob.set_val("patchV", np.array([U0, _a]))
            prob.run_model()
            _cl = float(prob.get_val("scenario1.aero_post.CL")[0])
            _cd = float(prob.get_val("scenario1.aero_post.CD")[0])
            _executed += 1
        except Exception as _e:          # noqa: BLE001 -- recorded, never swallowed
            _err = repr(_e).replace("\n", " ")
            _after_exc = True
        _dt = time.time() - _t0
        # The SECOND, INDEPENDENT channel on CL/CD.  The solver also prints its
        # own `CL:` / `CD:` lines into this same log; the reader takes both and
        # a disagreement between them is a finding, not a tie broken silently.
        print("AOA_POINT_VALUES idx=%d alpha=%.10f CL=%s CD=%s wall_s=%.4f err=%s"
              % (_i, _a,
                 ("NA" if _cl is None else "%.12g" % _cl),
                 ("NA" if _cd is None else "%.12g" % _cd),
                 _dt, ("NONE" if _err is None else _err)), flush=True)
        print("AOA_POINT_END idx=%d alpha=%.10f" % (_i, _a), flush=True)
        _ledger_row(_i, "%.10f" % _a, _mode,
                    ("NONE" if _prev is None else "%.10f" % _prev),
                    ("TRUE" if _after_exc else "FALSE"),
                    ("NA" if _cl is None else "%.12g" % _cl),
                    ("NA" if _cd is None else "%.12g" % _cd),
                    "%.4f" % _dt, ("NONE" if _err is None else _err))
        _rows.append({"idx": _i, "alpha_deg": _a, "mode": _mode,
                      "continued_from_deg": _prev, "after_exception": _after_exc,
                      "CL_getval": _cl, "CD_getval": _cd,
                      "wall_s": _dt, "error": _err})
        _prev = _a

    if _rank0:
        with open(_pts, "w") as _fh:
            json.dump({"mode": _mode, "n_declared": len(_alphas),
                       "n_executed": _executed, "rows": _rows}, _fh, indent=2)
    print("AOA_SWEEP_END n_declared=%d n_executed=%d json=%s"
          % (len(_alphas), _executed, _pts), flush=True)
    if _executed != len(_alphas):
        print("AOA_SWEEP_TRUNCATED n_declared=%d n_executed=%d -- NOT a completion"
              % (len(_alphas), _executed), flush=True)
        exit(97)
elif args.task == "check_totals":
    # verify the total derivatives against the finite-difference
    prob.run_model()
    prob.check_totals(compact_print=False, step=1e-3, form="central", step_calc="abs")
else:
    print("task arg not found!")
    exit(1)
