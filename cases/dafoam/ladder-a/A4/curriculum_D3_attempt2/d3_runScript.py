#!/usr/bin/env python
"""
Curriculum item D3 -- A4 Ahmed body 25 deg, CONSTRAINED drag minimisation.
ATTEMPT 2. Built from attempt 1's frozen producer (md5
af2ce474e7954c03e3937161510f6590, committed 0cbf463c), which is NOT edited and
NOT moved: this is a separate file in a separate item directory, the D1-C'
mini-item pattern that attempt 1's own sec.4.3 requires.
FROZEN by the commit that carries PREREGISTRATION.md. Not edited after first
compute (CLAUDE.md rule 6; PREREGISTRATION.md sec.4.3).

Derived from the A4 optimisation script
  /home/ubuntu/certonomous-runs/P3-a4-opt-shipped/opt_runScript.py
  md5 387a09b76d4774186be4b83a80f14e8a
Lines 32-83 of that file (flow parameters, daOptions, meshOptions) are carried
BYTE-IDENTICAL below. The differences from it, and only these, are:

  D3-1  a SECOND shape-function design variable `shapeRear` on the FFD rear-top
        control-point pair pts[2,0,1]/pts[2,1,1]  (A4 has one DV, line 109)
  D3-2  `nom_addThicknessConstraints2D("thickcon_slant", ...)` + add_constraint
        (A4 has NO DVConstraints anywhere in its 195 lines)
  D3-3  `nom_addVolumeConstraint("volcon_aft", ...)` + add_constraint
  D3-4  the four stage tasks geom_probe / eta / run_driver / endpoint_at
  D3-5  a single JSON summary `d3_summary.json` whose key set is frozen and
        asserted against the comparator's key set at the freeze (L-273)
  D3-6  ATTEMPT 2's ONE repair: `nom_setConstraintSurface` on the triangulated
        wall surface -- the prerequisite of every DVCon call. pygeo
        mphys_dvgeo.py:541-545 is the ONLY registrar of the surface name
        "default" that :425 (thickness) and :446 (volume) default to, and
        DVCon.py:3217-3219 raises KeyError without it. Attempt 1 omitted it and
        died at its first constraint call (attempt 1 geom.log:491).

y-SYMMETRY is enforced BY CONSTRUCTION: every shape function moves the j=0 and
j=1 control points of a pair TOGETHER, so no deformation can be asymmetric.
`nom_addLinearConstraintsShape` (the JBC_Hull "reflect" pattern) is DECLINED BY
NAME -- see PREREGISTRATION.md sec.2.4.
"""
import os
import json
import argparse
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder, OptFuncs
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP

parser = argparse.ArgumentParser()
parser.add_argument("-optimizer", help="optimizer to use", type=str, default="IPOPT")
parser.add_argument("-task", help="type of run to do", type=str, default="run_driver")
parser.add_argument("-dvfile", help="JSON holding {'shapeBreak':x,'shapeRear':y} for endpoint_at",
                    type=str, default="")
parser.add_argument("-fdsteps", help="comma-separated FD steps for the endpoint sweep",
                    type=str, default="1e-1,1e-2,1e-3,1e-4")
args = parser.parse_args()

# =============================================================================
# Input parameters -- CARRIED BYTE-IDENTICAL from A4 opt_runScript.py:32-83
# =============================================================================
U0 = 40.0
p0 = 0.0
k0 = 0.24
omega0 = 8.56731
rho0 = 1.225
Aref = 0.401696  # measured planform area, same basis as the OpenFOAM baseline
lRef = 1.044

daOptions = {
    "designSurfaces": ["body"],
    "solverName": "DASimpleFoam",
    "primalMinResTol": 1.0e-4,
    "primalMinResTolDiff": 1.0e5,
    "function": {
        "CD": {
            "type": "force",
            "source": "patchToFace",
            "patches": ["body"],
            "directionMode": "fixedDirection",
            "direction": [1.0, 0.0, 0.0],
            "scale": 1.0 / (0.5 * U0 * U0 * Aref * rho0),
        },
        "CL": {
            "type": "force",
            "source": "patchToFace",
            "patches": ["body"],
            "directionMode": "fixedDirection",
            "direction": [0.0, 0.0, 1.0],
            "scale": 1.0 / (0.5 * U0 * U0 * Aref * rho0),
        },
    },
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 1, "jacMatReOrdering": "rcm"},
    "normalizeStates": {
        "U": U0,
        "p": U0 * U0 / 2.0,
        "k": k0,
        "omega": omega0,
        "phi": 1.0,
    },
    "inputInfo": {
        "aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]},
    },
}

meshOptions = {
    "gridFile": os.getcwd(),
    "fileType": "OpenFOAM",
    # full (non-half) Ahmed body mesh -- no real symmetry plane, but IDWarp
    # requires this key to be present for OpenFOAM meshes to skip its
    # (unsupported for OpenFOAM/PLOT3D) auto-detection of symmetry surfaces.
    "symmetryPlanes": [],
}

# =============================================================================
# D3 registered constraint geometry. Ahmed 25 body: x[0, 1.044], y[+-0.1945],
# z[0, 0.288]; slant break at x = 0.8428, z = 0.288; rear-edge top z = 0.1942.
# The aft-region lines sit INSIDE the body in x, y and z.
# =============================================================================
LE_AFT = [[0.86, -0.17, 0.10], [0.86, 0.17, 0.10]]
TE_AFT = [[1.03, -0.17, 0.10], [1.03, 0.17, 0.10]]
N_SPAN = 5
N_CHORD = 6
THICK_LO, THICK_HI = 0.85, 1.15
VOL_LO = 0.98
DV_LO, DV_HI = -0.05, 0.05

# Frozen geometric probe points for the rear-slant angle (PREREGISTRATION sec.2.5)
X_BREAK, Z_BREAK = 0.8428, 0.288
X_REAR, Z_REAR = 1.044, 0.1942
ETA_PLANT = 1.0e-4   # planted perturbation on shapeBreak for the eta control


class Top(Multipoint):
    def setup(self):
        dafoam_builder = DAFoamBuilder(daOptions, meshOptions, scenario="aerodynamic")
        dafoam_builder.initialize(self.comm)

        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])
        self.add_subsystem("mesh", dafoam_builder.get_mesh_coordinate_subsystem())
        self.add_subsystem("geometry", OM_DVGEOCOMP(file="FFD/ahmedFFD.xyz", type="ffd"))
        self.mphys_add_scenario("scenario1", ScenarioAerodynamic(aero_builder=dafoam_builder))

        self.connect("mesh.x_aero0", "geometry.x_aero_in")
        self.connect("geometry.x_aero0", "scenario1.x_aero")

    def configure(self):
        points = self.mesh.mphys_get_surface_mesh()
        self.geometry.nom_add_discipline_coords("aero", points)

        # D3-6. THE ATTEMPT-2 REPAIR, and the only executable change from
        # attempt 1. DVConstraints projects onto a triangulated surface that
        # nom_add_discipline_coords does NOT register -- that call registers the
        # point set with DVGeo only (mphys_dvgeo.py:103-116). JBC_Hull
        # runScript.py:106-107 and D1-C' d1c_runScript.py:134-135 both do
        # exactly this, ~40 lines before their constraint calls.
        tri_points = self.mesh.mphys_get_triangulated_surface()
        self.geometry.nom_setConstraintSurface(tri_points)

        pts = self.geometry.DVGeo.getLocalIndex(0)
        dir_z = np.array([0.0, 0.0, 1.0])

        # D3-1. TWO shape-function DVs, each a SYMMETRIC PAIR moved purely in z.
        #   shapeBreak: i=1 (x=0.80), k=1 (top) -- A4's own DV, unchanged.
        #   shapeRear : i=2 (x=1.07), k=1 (top) -- new; with shapeBreak it sets
        #               the rear-slant angle.
        # Nose (i=0) and the whole underbody (k=0) are untouched by construction.
        sB = [{pts[1, 0, 1]: dir_z, pts[1, 1, 1]: dir_z}]
        sR = [{pts[2, 0, 1]: dir_z, pts[2, 1, 1]: dir_z}]
        self.geometry.nom_addShapeFunctionDV(dvName="shapeBreak", shapes=sB)
        self.geometry.nom_addShapeFunctionDV(dvName="shapeRear", shapes=sR)

        # D3-2 / D3-3. The constraints A4 does not have. JBC_Hull precedent
        # (/home/ubuntu/dafoam-tutorials/JBC_Hull/runScript.py:175-185, 202-204).
        self.geometry.nom_addThicknessConstraints2D(
            "thickcon_slant", LE_AFT, TE_AFT, nSpan=N_SPAN, nChord=N_CHORD)
        self.geometry.nom_addVolumeConstraint(
            "volcon_aft", LE_AFT, TE_AFT, nSpan=N_SPAN, nChord=N_CHORD)

        self.dvs.add_output("shapeBreak", val=np.array([0.0] * len(sB)))
        self.dvs.add_output("shapeRear", val=np.array([0.0] * len(sR)))
        self.connect("shapeBreak", "geometry.shapeBreak")
        self.connect("shapeRear", "geometry.shapeRear")

        self.add_design_var("shapeBreak", lower=DV_LO, upper=DV_HI, scaler=1.0)
        self.add_design_var("shapeRear", lower=DV_LO, upper=DV_HI, scaler=1.0)
        self.add_objective("scenario1.aero_post.CD", scaler=1.0)
        self.add_constraint("geometry.thickcon_slant", lower=THICK_LO, upper=THICK_HI, scaler=1.0)
        self.add_constraint("geometry.volcon_aft", lower=VOL_LO, scaler=1.0)


prob = om.Problem()
prob.model = Top()

# IPOPT settings CARRIED BYTE-IDENTICAL from A4 opt_runScript.py:129-145,
# max_iter included. A stop on max_iter is GATE REACHED, never PASS
# (DAFOAM_CHARTER.md sec.9).
prob.driver = om.pyOptSparseDriver()
prob.driver.options["optimizer"] = "IPOPT"
prob.driver.opt_settings = {
    "tol": 1.0e-6,
    "constr_viol_tol": 1.0e-6,
    "max_iter": 15,
    "print_level": 5,
    "output_file": "opt_IPOPT.txt",
    "mu_strategy": "adaptive",
    "limited_memory_max_history": 10,
    "nlp_scaling_method": "none",
    "alpha_for_y": "full",
    "recalc_y": "yes",
}
prob.driver.options["debug_print"] = ["objs", "desvars", "nl_cons"]
prob.driver.options["print_opt_prob"] = True
prob.driver.hist_file = "opt.hst"

prob.setup(mode="rev")
om.n2(prob, show_browser=False, outfile="mphys.html")

optFuncs = OptFuncs(daOptions, prob)
RANK0 = MPI.COMM_WORLD.rank == 0


def _f(name):
    return [float(v) for v in prob.get_val(name)]


def _dump(d):
    """D3-5. The ONE summary artifact. Its key set is frozen; d3_grade.py reads
    exactly these keys and the freeze invocation asserts the two sets equal."""
    if RANK0:
        json.dump(d, open("d3_summary.json", "w"), indent=1, sort_keys=True)
        print("D3_SUMMARY_WRITTEN:", sorted(d.keys()))


def _state(tag):
    return {
        "%s_CD" % tag: float(prob.get_val("scenario1.aero_post.CD")[0]),
        "%s_CL" % tag: float(prob.get_val("scenario1.aero_post.CL")[0]),
        "%s_shapeBreak" % tag: _f("shapeBreak")[0],
        "%s_shapeRear" % tag: _f("shapeRear")[0],
        "%s_thickcon_slant" % tag: _f("geometry.thickcon_slant"),
        "%s_volcon_aft" % tag: _f("geometry.volcon_aft"),
    }


# ---------------------------------------------------------------------------
# STAGE G -- geometry probe. NO FLOW SOLVE. Exercises every DVGeo/DVCon call
# above and measures the FFD->surface z-Jacobian at the two slant probe points.
# ---------------------------------------------------------------------------
if args.task == "geom_probe":
    out = {"task": "geom_probe"}
    dvg = prob.model.geometry.DVGeo

    def probe_surface():
        pts = dvg.update("aero")
        return np.asarray(pts)

    def z_at(pts, x, tol=2.0e-3):
        sel = [i for i in range(pts.shape[0])
               if abs(pts[i, 0] - x) <= tol and abs(pts[i, 1]) <= 0.19]
        return (max(float(pts[i, 2]) for i in sel), len(sel)) if sel else (None, 0)

    base = probe_surface()
    zb0, nb0 = z_at(base, X_BREAK)
    zr0, nr0 = z_at(base, X_REAR)
    out["G_nsurf"] = int(base.shape[0])
    out["G_zbreak0"], out["G_nbreak"] = zb0, nb0
    out["G_zrear0"], out["G_nrear"] = zr0, nr0
    out["G_thickcon_slant0"] = _f("geometry.thickcon_slant")
    out["G_volcon_aft0"] = _f("geometry.volcon_aft")

    delta = 0.01
    jac = {}
    for dv in ("shapeBreak", "shapeRear"):
        # NO FLOW SOLVE anywhere in this stage: DVGeo is driven directly.
        dvs = {"shapeBreak": np.array([0.0]), "shapeRear": np.array([0.0])}
        dvs[dv] = np.array([delta])
        dvg.setDesignVars(dvs)
        p = probe_surface()
        zb, _ = z_at(p, X_BREAK)
        zr, _ = z_at(p, X_REAR)
        # y-symmetry assertion: for every surface point a mirrored partner must
        # exist at the same z. Symmetry is BY CONSTRUCTION; this measures it.
        asym = 0.0
        n = min(p.shape[0], 4000)
        for i in range(n):
            xi, yi, zi = p[i, 0], p[i, 1], p[i, 2]
            best = None
            for j in range(p.shape[0]):
                if abs(p[j, 0] - xi) < 1e-9 and abs(p[j, 1] + yi) < 1e-9:
                    d = abs(p[j, 2] - zi)
                    best = d if best is None else min(best, d)
            if best is not None:
                asym = max(asym, best)
        jac["dzbreak_d%s" % dv] = (zb - zb0) / delta if (zb is not None and zb0 is not None) else None
        jac["dzrear_d%s" % dv] = (zr - zr0) / delta if (zr is not None and zr0 is not None) else None
        jac["symmetry_max_dz_%s" % dv] = asym
        jac["symmetry_npts_checked_%s" % dv] = int(n)
    dvg.setDesignVars({"shapeBreak": np.array([0.0]), "shapeRear": np.array([0.0])})
    out["G_jac"] = jac
    _dump(out)

# ---------------------------------------------------------------------------
# STAGE ETA -- delta_repeat of CD at the baseline (N-D15 discipline) plus the
# planted perturbation that proves the reader can see a non-zero (rule 3).
# ---------------------------------------------------------------------------
elif args.task == "eta":
    out = {"task": "eta"}
    prob.run_model()
    out.update(_state("eta_call1"))
    prob.run_model()
    out.update(_state("eta_call2"))
    out["eta_delta_repeat"] = abs(out["eta_call2_CD"] - out["eta_call1_CD"])
    prob.set_val("shapeBreak", np.array([ETA_PLANT]))
    prob.run_model()
    out.update(_state("eta_plant"))
    out["eta_plant_dv"] = ETA_PLANT
    out["eta_plant_dCD"] = abs(out["eta_plant_CD"] - out["eta_call2_CD"])
    _dump(out)
    if RANK0:
        print("ETA_DELTA_REPEAT:", repr(out["eta_delta_repeat"]))
        print("ETA_PLANT_DCD:", repr(out["eta_plant_dCD"]))

# ---------------------------------------------------------------------------
# STAGE O -- the constrained optimisation, plus the in-process endpoint FD
# sweep at the optimum (DAFOAM_CHARTER sec.3 plateau, sec.4 trivial baseline).
# ---------------------------------------------------------------------------
elif args.task == "run_driver":
    out = {"task": "run_driver"}
    prob.run_model()
    out.update(_state("base"))
    prob.run_driver()
    out.update(_state("final"))
    out["reduction_pct"] = 100.0 * (out["base_CD"] - out["final_CD"]) / out["base_CD"]
    _dump(out)
    if RANK0:
        print("D3_BASE_CD:", repr(out["base_CD"]))
        print("D3_FINAL_CD:", repr(out["final_CD"]))
        print("D3_FINAL_DV:", repr([out["final_shapeBreak"], out["final_shapeRear"]]))
        print("D3_REDUCTION_PCT:", repr(out["reduction_pct"]))
    for s in [float(x) for x in args.fdsteps.split(",")]:
        if RANK0:
            print("D3_CHECK_TOTALS_BEGIN step=%g" % s)
        prob.check_totals(compact_print=False, step=s, form="central", step_calc="abs")
        if RANK0:
            print("D3_CHECK_TOTALS_END step=%g" % s)

# ---------------------------------------------------------------------------
# STAGE T -- endpoint gradient at a FROZEN design vector, cold. Run once per
# image at the SAME design vector reached by the SAME path (Stage O's), which is
# the clean toolchain comparison A4 shipped RESULTS sec.8 limit 3 never bought.
# ---------------------------------------------------------------------------
elif args.task == "endpoint_at":
    dv = json.load(open(args.dvfile))
    prob.set_val("shapeBreak", np.array([float(dv["shapeBreak"])]))
    prob.set_val("shapeRear", np.array([float(dv["shapeRear"])]))
    prob.run_model()
    out = {"task": "endpoint_at", "T_dv_in": dv}
    out.update(_state("T"))
    _dump(out)
    if RANK0:
        print("D3_T_CD:", repr(out["T_CD"]))
    for s in [float(x) for x in args.fdsteps.split(",")]:
        if RANK0:
            print("D3_CHECK_TOTALS_BEGIN step=%g" % s)
        prob.check_totals(compact_print=False, step=s, form="central", step_calc="abs")
        if RANK0:
            print("D3_CHECK_TOTALS_END step=%g" % s)

else:
    print("task arg not supported!")
    exit(1)
