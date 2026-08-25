#!/usr/bin/env python
"""
DAFoam run script for the NACA0012 airfoil at low-speed

CURRICULUM ITEM D13 PRODUCER -- basin/restart robustness on D1's problem.

DERIVED FROM the frozen D1 producer `curriculum_D2/d1_opt_runScript.py`
(md5 4c9811d16f344bc23136981cd6092d8f), which is NOT EDITED: D1's file is
frozen by `curriculum_D1/PREREGISTRATION.md` and CLAUDE.md rule 6 forbids
editing it.  This is a SEPARATE FILE with exactly TWO registered changes and
no others:
  (1) this header block;
  (2) the task name `d13_start` added to the guard tuple, and one new
      `elif args.task == "d13_start":` branch appended inside it.
Every line of the D1 case setup, daOptions, meshOptions, DV/constraint
definition, IPOPT settings and the whole `_fd_suite` instrument is BYTE
IDENTICAL to the D1 file.  `d13_script.diff` in the run root carries the proof
and the registered hunk count.

The finite-difference instrument `d1_fd_endpoint.py`
(md5 7e454d2f1830a40086465d9b5c57a941) is staged UNCHANGED and imported
UNCHANGED.  D13 selects no step: every step is chosen inside this process by
that frozen file from |J_adj| and the inherited eta alone.
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
U0 = 10.0
p0 = 0.0
nuTilda0 = 4.5e-5
CL_target = 0.5
aoa0 = 5.13918623195176
A0 = 0.1
# rho is used for normalizing CD and CL
rho0 = 1.0

# Input parameters for DAFoam
daOptions = {
    "designSurfaces": ["wing"],
    "solverName": "DASimpleFoam",
    "primalMinResTol": 1.0e-8,
    "printInterval": 10,
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
        "max_iter": 40,
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
elif args.task in ("d1_eta", "d1_opt", "d1_endpoint_shipped", "d13_start"):
    # ---------------------------------------------------------------------
    # Curriculum item D1.  Frozen in
    #   cases/dafoam/ladder-a/A1/curriculum_D1/PREREGISTRATION.md
    # ---------------------------------------------------------------------
    import json as _json
    import os as _os
    import resource as _res
    import time as _time

    import numpy as _np

    import d1_fd_endpoint as _d1

    _rank = MPI.COMM_WORLD.rank

    def _p(*a):
        if _rank == 0:
            print(*a, flush=True)

    def _getf(names):
        for n in names:
            try:
                return float(_np.asarray(prob.get_val(n)).ravel()[0])
            except Exception:
                continue
        raise RuntimeError("unreadable: %s" % names)

    def _CD():
        return _getf(["scenario1.aero_post.CD",
                      "scenario1.aero_post.functionals.CD"])

    def _CL():
        return _getf(["scenario1.aero_post.CL",
                      "scenario1.aero_post.functionals.CL"])

    def _vec(name):
        return _np.asarray(prob.get_val(name)).ravel()

    def _setv(name, val):
        try:
            prob.set_val(name, _np.asarray(val))
        except Exception:
            prob.set_val("dvs." + name, _np.asarray(val))

    def _cons():
        out = {}
        for c in ["geometry.thickcon", "geometry.volcon", "geometry.rcon"]:
            try:
                out[c] = _np.asarray(prob.get_val(c)).ravel().tolist()
            except Exception as e:
                out[c] = "UNREADABLE %s" % e
        return out

    def _rss():
        return _res.getrusage(_res.RUSAGE_SELF).ru_maxrss / 1048576.0

    def _totals():
        """Endpoint adjoint.  Returns {'shape': [...], 'patchV': [...]}."""
        trials = [
            (["scenario1.aero_post.functionals.CD"], ["dvs.shape", "dvs.patchV"]),
            (["scenario1.aero_post.CD"], ["shape", "patchV"]),
            (["scenario1.aero_post.CD"], ["dvs.shape", "dvs.patchV"]),
        ]
        for of_, wrt_ in trials:
            try:
                t = prob.compute_totals(of=of_, wrt=wrt_)
                return {"shape": _np.asarray(t[(of_[0], wrt_[0])]).ravel().tolist(),
                        "patchV": _np.asarray(t[(of_[0], wrt_[1])]).ravel().tolist(),
                        "of": of_[0], "wrt": wrt_}
            except Exception as e:
                _p("D1_TOTALS_TRY_FAILED %s %s :: %s" % (of_, wrt_, e))
        raise RuntimeError("compute_totals failed on every registered name form")

    def _fd_suite(tag, eta, steps_in=None):
        """Gate G3 + G4.  Steps come from |J_adj| and eta only, never from an
        FD value.  When steps_in is given (arm C) the SAME steps are reused so
        the two images' FD columns are directly comparable."""
        _p("D1_%s_RUNMODEL_BEGIN" % tag)
        prob.run_model()
        x_sh = _vec("shape").copy()
        x_pv = _vec("patchV").copy()
        cd0, cl0 = _CD(), _CL()
        _p("D1_%s_CD %.17g" % (tag, cd0))
        _p("D1_%s_CL %.17g" % (tag, cl0))
        _p("D1_%s_SHAPE %s" % (tag, _json.dumps(x_sh.tolist())))
        _p("D1_%s_PATCHV %s" % (tag, _json.dumps(x_pv.tolist())))
        _p("D1_%s_CONS %s" % (tag, _json.dumps(_cons())))

        J = _totals()
        _p("D1_%s_JADJ %s" % (tag, _json.dumps(J)))

        def f_sh(v):
            _setv("shape", v)
            prob.run_model()
            return _CD()

        def f_pv(v):
            _setv("patchV", v)
            prob.run_model()
            return _CD()

        res = {}
        plan = {}
        for dv, idx in _d1.NAMED:
            key = "%s[%d]" % (dv, idx)
            Jc = J[dv][idx]
            if steps_in is not None and key in steps_in:
                s_lo, s_hi = steps_in[key]["s_lo"], steps_in[key]["s_hi"]
                src_ = "reused-from-armO"
            else:
                s_lo, s_hi, _, _ = _d1.pick_steps(Jc, eta, dv)
                src_ = "rule"
            plan[key] = {"J_adj": Jc, "s_lo": s_lo, "s_hi": s_hi,
                         "C_lo": None if s_lo is None else _d1.clearance(Jc, s_lo, eta),
                         "C_hi": None if s_hi is None else _d1.clearance(Jc, s_hi, eta),
                         "step_source": src_}
        _p("D1_%s_FDPLAN %s" % (tag, _json.dumps(plan)))

        for dv, idx in _d1.NAMED:
            key = "%s[%d]" % (dv, idx)
            pl = plan[key]
            x = x_sh if dv == "shape" else x_pv
            f = f_sh if dv == "shape" else f_pv
            rst = (lambda v, _n=dv: _setv(_n, v))
            res[key] = {"J_adj": pl["J_adj"], "steps": {}}
            for tagstep in ("s_lo", "s_hi"):
                s = pl[tagstep]
                if s is None:
                    res[key]["steps"][tagstep] = {"step": None,
                                                  "status": "NO ADMISSIBLE RUNG"}
                    continue
                d, fp, fm = _d1.central_fd(f, x, idx, s, restore=rst)
                rel = abs(pl["J_adj"] - d) / abs(d) if d != 0.0 else float("inf")
                flip = (pl["J_adj"] * d) < 0.0
                res[key]["steps"][tagstep] = {
                    "step": s, "fd": d, "f_plus": fp, "f_minus": fm,
                    "rel_err": rel, "sign_flip": bool(flip),
                    "C_measured": abs(d) * 2.0 * s / eta}
                _p("D1_%s_FD %s %s step=%.6g fd=%.17g adj=%.17g rel=%.6e flip=%s"
                   % (tag, key, tagstep, s, d, pl["J_adj"], rel, flip))
            lo = res[key]["steps"].get("s_lo", {}).get("fd")
            hi = res[key]["steps"].get("s_hi", {}).get("fd")
            if lo is not None and hi is not None and hi != 0.0:
                pt = abs(hi - lo) / abs(hi)
                res[key]["plateau"] = pt
                res[key]["graded"] = bool(pt <= _d1.PLATEAU_TOL
                                          and res[key]["steps"]["s_hi"]["C_measured"] >= _d1.CMIN)
                _p("D1_%s_PLATEAU %s %.6e graded=%s"
                   % (tag, key, pt, res[key]["graded"]))
            else:
                res[key]["plateau"] = None
                res[key]["graded"] = False

        # ---- gate G4, trivial baseline: shape idx6 at a deliberately wrong step
        d, fp, fm = _d1.central_fd(f_sh, x_sh, 6, _d1.TRIVIAL_STEP,
                                   restore=lambda v: _setv("shape", v))
        Jc = J["shape"][6]
        relt = abs(Jc - d) / abs(d) if d != 0.0 else float("inf")
        trivial = {"component": "shape[6]", "step": _d1.TRIVIAL_STEP,
                   "fd": d, "adj": Jc, "rel_err": relt,
                   "sign_flip": bool(Jc * d < 0.0)}
        _p("D1_%s_TRIVIAL %s" % (tag, _json.dumps(trivial)))

        _setv("shape", x_sh)
        _setv("patchV", x_pv)
        return {"tag": tag, "CD": cd0, "CL": cl0,
                "shape": x_sh.tolist(), "patchV": x_pv.tolist(),
                "cons": _cons(), "J_adj": J, "eta": eta,
                "plan": plan, "fd": res, "trivial": trivial,
                "maxrss_GiB": _rss()}

    _eta_env = float(_os.environ.get("D1_ETA", "0") or 0)

    if args.task == "d1_eta":
        prob.run_model()
        _p("D1_ETA_BASELINE_CD %.17g" % _CD())
        _p("D1_ETA_BASELINE_CL %.17g" % _CL())
        _p("D1_ETA_BASELINE_CONS %s" % _json.dumps(_cons()))
        _p("D1_ETA_MAXRSS_GiB %.4f" % _rss())

    elif args.task == "d1_opt":
        assert _eta_env > 0.0, "D1_ETA must be exported from arm E"
        _p("D1_OPT_ETA %.17g" % _eta_env)
        optFuncs.findFeasibleDesign(["scenario1.aero_post.CL"], ["patchV"],
                                    targets=[CL_target], designVarsComp=[1])
        _p("D1_FEASIBLE_CD %.17g" % _CD())
        _p("D1_FEASIBLE_CL %.17g" % _CL())
        _p("D1_FEASIBLE_PATCHV %s" % _json.dumps(_vec("patchV").tolist()))
        _p("D1_FEASIBLE_SHAPE %s" % _json.dumps(_vec("shape").tolist()))
        _t0 = _time.time()
        prob.run_driver()
        _p("D1_DRIVER_WALL_S %.2f" % (_time.time() - _t0))
        out = _fd_suite("ENDPOINT_PATCHED", _eta_env)
        out["feasible_note"] = "CD/CL above are the post-run_driver values"
        if _rank == 0:
            with open(_os.environ.get("D1_ENDPOINT_JSON", "endpoint.json"), "w") as fh:
                _json.dump(out, fh, indent=1)
        _p("D1_OPT_MAXRSS_GiB %.4f" % _rss())

    elif args.task == "d1_endpoint_shipped":
        src_json = _os.environ["D1_ENDPOINT_IN"]
        if _rank == 0:
            _d1.planted_zero_control(src_json)      # gate G5, refuses on failure
        ep = _d1.read_endpoint(src_json)
        _setv("shape", _np.asarray(ep["shape"]))
        _setv("patchV", _np.asarray(ep["patchV"]))
        _p("D1_SHIPPED_DV_INJECTED shape=%s patchV=%s"
           % (_json.dumps(ep["shape"]), _json.dumps(ep["patchV"])))
        steps_in = {k: {"s_lo": v["s_lo"], "s_hi": v["s_hi"]}
                    for k, v in ep["plan"].items()}
        out = _fd_suite("ENDPOINT_SHIPPED", ep["eta"], steps_in=steps_in)
        out["design_point_from"] = src_json
        if _rank == 0:
            with open(_os.environ.get("D1_ENDPOINT_OUT", "endpoint_shipped.json"), "w") as fh:
                _json.dump(out, fh, indent=1)
        _p("D1_SHIPPED_MAXRSS_GiB %.4f" % _rss())

    elif args.task == "d13_start":
        # -------------------------------------------------------------------
        # Curriculum item D13.  ONE perturbed start of the D1 problem.
        # Frozen in cases/dafoam/ladder-a/A1/curriculum_D13/PREREGISTRATION.md
        #
        # The start vector comes from the FROZEN LITERAL TABLE in d13_basin.py
        # and from nowhere else.  The seed regeneration below is PRINTED FOR
        # THE RECORD and never sets a design variable: a start set whose
        # identity depends on an RNG implementation detail is not a registered
        # experiment, so the table is the authority and the seed documents it.
        # -------------------------------------------------------------------
        import d13_basin as _d13b

        _eta13 = float(_os.environ.get("D13_ETA", "0") or 0)
        assert _eta13 > 0.0, "D13_ETA must be exported (D1 arm E run 2 value)"
        _k = int(_os.environ["D13_START_ID"])
        assert _k in _d13b.START_IDS, "D13_START_ID must be one of %s" % (
            _d13b.START_IDS,)

        _p("D13_START_ID %d" % _k)
        _p("D13_ETA %.17g" % _eta13)
        _p("D13_SEED %d DELTA_SHAPE %.17g DELTA_AOA %.17g"
           % (_d13b.SEED, _d13b.DELTA_SHAPE, _d13b.DELTA_AOA))

        _sh0, _pv0 = _d13b.start_vectors(_k)
        try:
            _rg = _np.random.default_rng(_d13b.SEED)
            _rs = _rg.uniform(-_d13b.DELTA_SHAPE, _d13b.DELTA_SHAPE,
                              size=(5, 8))
            _ra = _rg.uniform(-_d13b.DELTA_AOA, _d13b.DELTA_AOA, size=5)
            _dev_s = max(abs(a - b)
                         for a, b in zip(_rs[_k - 1].tolist(), _sh0))
            _dev_a = abs(float(_ra[_k - 1]) - (_pv0[1] - _d13b.AOA0))
            _p("D13_SEED_REGEN numpy=%s max_shape_dev=%.6e aoa_dev=%.6e"
               % (_np.__version__, _dev_s, _dev_a))
        except Exception as _e:
            _p("D13_SEED_REGEN UNAVAILABLE %s" % _e)

        _setv("shape", _np.asarray(_sh0))
        _setv("patchV", _np.asarray(_pv0))
        prob.run_model()
        _p("D13_START_SHAPE %s" % _json.dumps(_vec("shape").tolist()))
        _p("D13_START_PATCHV %s" % _json.dumps(_vec("patchV").tolist()))
        _p("D13_START_CD %.17g" % _CD())
        _p("D13_START_CL %.17g" % _CL())
        _start_cons = _cons()
        _p("D13_START_CONS %s" % _json.dumps(_start_cons))

        # restore the CL equality by AoA, exactly as D1 arm O did
        optFuncs.findFeasibleDesign(["scenario1.aero_post.CL"], ["patchV"],
                                    targets=[CL_target], designVarsComp=[1])
        _feas_cd, _feas_cl = _CD(), _CL()
        _feas_pv = _vec("patchV").tolist()
        _p("D13_FEASIBLE_CD %.17g" % _feas_cd)
        _p("D13_FEASIBLE_CL %.17g" % _feas_cl)
        _p("D13_FEASIBLE_PATCHV %s" % _json.dumps(_feas_pv))

        _t0 = _time.time()
        prob.run_driver()
        _wall = _time.time() - _t0
        _p("D13_DRIVER_WALL_S %.2f" % _wall)

        # IPOPT's own statement, embedded here as ONE channel; the grader reads
        # opt_IPOPT.txt INDEPENDENTLY and refuses if the two disagree.
        import re as _re
        _exit_line, _majors = "NOT READ", -1
        try:
            with open("opt_IPOPT.txt") as _fh:
                _txt = _fh.read()
            _me = _re.findall(r"^(EXIT:.*)$", _txt, _re.M)
            _mi = _re.findall(r"^Number of Iterations\.*:\s*(\d+)\s*$",
                              _txt, _re.M)
            if _me:
                _exit_line = _me[-1].strip()
            if _mi:
                _majors = int(_mi[-1])
        except Exception as _e:
            _exit_line = "UNREADABLE %s" % _e
        _p("D13_IPOPT_EXIT %s" % _exit_line)
        _p("D13_IPOPT_MAJORS %d" % _majors)

        out = _fd_suite("ENDPOINT_S%d" % _k, _eta13)
        out["start_id"] = _k
        out["start_shape"] = _sh0
        out["start_patchV"] = _pv0
        out["start_cons"] = _start_cons
        out["feasible_CD"] = _feas_cd
        out["feasible_CL"] = _feas_cl
        out["feasible_patchV"] = _feas_pv
        out["driver_wall_s"] = _wall
        out["ipopt_exit"] = _exit_line
        out["ipopt_majors"] = _majors
        if _rank == 0:
            with open(_os.environ.get("D13_ENDPOINT_JSON",
                                      "endpoint_d13.json"), "w") as fh:
                _json.dump(out, fh, indent=1)
        _p("D13_MAXRSS_GiB %.4f" % _rss())

else:
    print("task arg not found!")
    exit(1)
