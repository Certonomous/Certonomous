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

# =============================================================================
# Curriculum mini-item D1-C' -- the SHIPPED-image endpoint gradient at arm O's
# converged design point.  Frozen by the commit that carries
#   cases/dafoam/ladder-a/A1/curriculum_D1_Cprime/PREREGISTRATION.md
#
# Everything above this line is byte-identical to the staged case's own
# runScript.py (md5 0557da51f6f179f6de865144343c499f), head -231.  The single
# registered change is the replacement of that file's task chain (its lines
# 232-252) by the one branch below.  No numeric setting is altered: the IPOPT
# block above is inert here because run_driver() is never called.
#
# NOT EDITED AFTER THE FIRST LAUNCH.  An edit voids the arm.
# =============================================================================
if args.task == "d1c_shipped":
    import json as _json
    import os as _os
    import resource as _res
    import time as _time

    import numpy as _np

    import d1c_endpoint as _c

    _rank = MPI.COMM_WORLD.rank
    _t_start = _time.time()

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
        """The SHIPPED endpoint adjoint.  Same name-form ladder arm O used."""
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
                _p("D1C_TOTALS_TRY_FAILED %s %s :: %s" % (of_, wrt_, e))
        raise RuntimeError("compute_totals failed on every registered name form")

    # ---------------------------------------------------------------------
    # Stage 1 -- the controls, BEFORE the design point is touched.  All three
    # are stdlib-only and were dry-run against this same real artifact on the
    # host before the freeze (PREREGISTRATION.md section 5).
    # ---------------------------------------------------------------------
    _src = _os.environ["D1C_ENDPOINT_IN"]
    _wd = _os.environ["D1C_WORKDIR"]
    if _rank == 0:
        _st = _c.selftest_cubic()
        _p("D1C_SELFTEST_CUBIC %s" % _json.dumps(_st, sort_keys=True))
        if not _st["pass"]:
            raise SystemExit(2)
        try:
            _c.planted_zero_control(_src, _wd)      # gate G5-C', refuses on failure
            if not _c.negative_control(_src, _wd)["pass"]:
                raise SystemExit(2)
            if not _c.keyset_control(_src, _wd)["pass"]:
                raise SystemExit(2)
        except _c.Refuse:
            raise SystemExit(2)
    MPI.COMM_WORLD.barrier()

    _frozen = _os.path.join(_wd, "armO_endpoint_frozen.json")
    if _c.md5_of(_frozen) != _c.ARMO_JSON_MD5:
        _p("D1C_REFUSE FROZEN_COPY_MD5 %s" % _c.md5_of(_frozen))
        raise SystemExit(2)
    ep = _c.read_endpoint(_frozen)
    _c.assert_keys(ep, "armO_endpoint_frozen.json")
    _c.assert_steps(ep, "armO_endpoint_frozen.json")

    # ---------------------------------------------------------------------
    # Stage 2 -- inject arm O's design point and prove it landed.
    # ---------------------------------------------------------------------
    _setv("shape", _np.asarray(ep["shape"]))
    _setv("patchV", _np.asarray(ep["patchV"]))
    _rb_sh = _vec("shape").tolist()
    _rb_pv = _vec("patchV").tolist()
    _p("D1C_DV_INJECTED shape=%s patchV=%s"
       % (_json.dumps(ep["shape"]), _json.dumps(ep["patchV"])))
    _p("D1C_DV_READBACK shape=%s patchV=%s"
       % (_json.dumps(_rb_sh), _json.dumps(_rb_pv)))
    _dv_ok = (all(a == b for a, b in zip(ep["shape"], _rb_sh))
              and all(a == b for a, b in zip(ep["patchV"], _rb_pv))
              and len(_rb_sh) == len(ep["shape"])
              and len(_rb_pv) == len(ep["patchV"]))
    _p("D1C_DV_READBACK_EXACT %s" % _dv_ok)
    if not _dv_ok:
        _p("D1C_REFUSE DV_READBACK design point did not land bit-exactly")
        raise SystemExit(2)

    # ---------------------------------------------------------------------
    # Stage 3 -- one cold primal, then one adjoint, on the shipped image.
    # ---------------------------------------------------------------------
    _p("D1C_PRIMAL_BEGIN")
    prob.run_model()
    _cd0, _cl0 = _CD(), _CL()
    _p("D1C_SHIPPED_CD %.17g" % _cd0)
    _p("D1C_SHIPPED_CL %.17g" % _cl0)
    _p("D1C_SHIPPED_CONS %s" % _json.dumps(_cons()))
    _p("D1C_PATCHED_CD_ARMO %.17g" % ep["CD"])
    _p("D1C_CD_DELTA_VS_ARMO %.6e" % (_cd0 - ep["CD"]))

    J = _totals()
    _p("D1C_SHIPPED_JADJ %s" % _json.dumps(J))
    _p("D1C_PATCHED_JADJ_ARMO %s" % _json.dumps(ep["J_adj"]))

    # ---------------------------------------------------------------------
    # Stage 4 -- central differences at the INHERITED steps.  No step is
    # selected here; every one comes from arm O's frozen plan and has already
    # been asserted equal to the literal frozen in d1c_endpoint.py.
    # ---------------------------------------------------------------------
    _x_sh = _vec("shape").tolist()
    _x_pv = _vec("patchV").tolist()

    def _f_sh(v):
        _setv("shape", _np.asarray(v))
        prob.run_model()
        return _CD()

    def _f_pv(v):
        _setv("patchV", _np.asarray(v))
        prob.run_model()
        return _CD()

    res = {}
    for dv, idx in _c.NAMED:
        key = "%s[%d]" % (dv, idx)
        Jc = J[dv][idx]
        x = _x_sh if dv == "shape" else _x_pv
        f = _f_sh if dv == "shape" else _f_pv
        rst = (lambda v, _n=dv: _setv(_n, _np.asarray(v)))
        res[key] = {"J_adj_shipped": Jc,
                    "J_adj_patched_armO": ep["J_adj"][dv][idx],
                    "steps": {}}
        for which in ("s_lo", "s_hi"):
            s = _c.FROZEN_STEPS[key][which]
            d, fp, fm = _c.central_fd(f, x, idx, s, restore=rst)
            rel = abs(Jc - d) / abs(d) if d != 0.0 else float("inf")
            flip = (Jc * d) < 0.0
            Cm = _c.clearance_from_fd(fp, fm)
            fd_armO = ep["fd"][key]["steps"][which]["fd"]
            res[key]["steps"][which] = {
                "step": s, "fd": d, "f_plus": fp, "f_minus": fm,
                "rel_err": rel, "sign_flip": bool(flip), "C_measured": Cm,
                "fd_armO_patched": fd_armO,
                "fd_vs_armO_rel": abs(d - fd_armO) / abs(fd_armO)
                if fd_armO != 0.0 else float("inf")}
            _p("D1C_FD %s %s step=%.6g fd=%.17g adj=%.17g rel=%.6e flip=%s "
               "C=%.6g fd_armO=%.17g fd_vs_armO=%.6e"
               % (key, which, s, d, Jc, rel, flip, Cm, fd_armO,
                  res[key]["steps"][which]["fd_vs_armO_rel"]))
        lo = res[key]["steps"]["s_lo"]["fd"]
        hi = res[key]["steps"]["s_hi"]["fd"]
        pt = abs(hi - lo) / abs(hi) if hi != 0.0 else float("inf")
        res[key]["plateau"] = pt
        res[key]["graded"] = bool(pt <= _c.PLATEAU_TOL
                                  and res[key]["steps"]["s_hi"]["C_measured"] >= _c.CMIN)
        res[key]["grade_at_s_hi"] = _c.grade(res[key]["steps"]["s_hi"]["rel_err"],
                                             res[key]["steps"]["s_hi"]["sign_flip"])
        # the toolchain comparison this mini-item was bought for
        dpa = Jc - ep["J_adj"][dv][idx]
        res[key]["shipped_minus_patched"] = dpa
        res[key]["shipped_minus_patched_rel"] = (
            abs(dpa) / abs(ep["J_adj"][dv][idx])
            if ep["J_adj"][dv][idx] != 0.0 else float("inf"))
        _p("D1C_PLATEAU %s %.6e graded=%s grade=%s"
           % (key, pt, res[key]["graded"], res[key]["grade_at_s_hi"]))
        _p("D1C_TOOLCHAIN %s shipped=%.17g patched=%.17g diff=%.17g rel=%.6e"
           % (key, Jc, ep["J_adj"][dv][idx], dpa,
              res[key]["shipped_minus_patched_rel"]))

    # ---------------------------------------------------------------------
    # Stage 5 -- gate G4-C', the trivial baseline: the same probe at a
    # deliberately wrong step (DAFOAM_CHARTER.md section 4).
    # ---------------------------------------------------------------------
    d, fp, fm = _c.central_fd(_f_sh, _x_sh, 6, _c.TRIVIAL_STEP,
                              restore=lambda v: _setv("shape", _np.asarray(v)))
    Jc6 = J["shape"][6]
    relt = abs(Jc6 - d) / abs(d) if d != 0.0 else float("inf")
    trivial = {"component": "shape[6]", "step": _c.TRIVIAL_STEP, "fd": d,
               "adj": Jc6, "rel_err": relt, "sign_flip": bool(Jc6 * d < 0.0),
               "armO_patched_rel_err": ep["trivial"]["rel_err"]}
    _p("D1C_TRIVIAL %s" % _json.dumps(trivial))

    _setv("shape", _np.asarray(_x_sh))
    _setv("patchV", _np.asarray(_x_pv))

    out = {"tag": "ENDPOINT_SHIPPED", "image": "dafoam/opt-packages:latest",
           "CD": _cd0, "CL": _cl0, "shape": _x_sh, "patchV": _x_pv,
           "cons": _cons(), "J_adj_shipped": J,
           "J_adj_patched_armO": ep["J_adj"],
           "eta_inherited": _c.ETA_INHERITED, "fd": res, "trivial": trivial,
           "design_point_from": _src, "design_point_md5": _c.ARMO_JSON_MD5,
           "maxrss_GiB": _rss(), "wall_s": _time.time() - _t_start}
    if _rank == 0:
        with open(_os.environ["D1C_ENDPOINT_OUT"], "w") as fh:
            _json.dump(out, fh, indent=1)
    _p("D1C_MAXRSS_GiB %.4f" % _rss())
    _p("D1C_WALL_S %.2f" % (_time.time() - _t_start))
    _p("D1C_COMPLETE")
else:
    print("task arg not found!")
    exit(1)
