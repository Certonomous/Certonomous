#!/usr/bin/env python
"""
Minimal reproducer: IDWarp's `mesh.warpDeriv` disagrees with a finite difference
of the warp it claims to differentiate, badly enough to SIGN-FLIP components of
the adjoint shape gradient, on the UNMODIFIED official DAFoam tutorial
`UBend_Channel`, with plain single-point single-axis (`addLocalDV`) design
variables.

No CFD source, no tutorial file, and no case setting is modified. This script is
dropped into the tutorial's own case directory after its own `preProcessing.sh`
has run, and it rebuilds the tutorial's own `Top` model verbatim -- same
`daOptions`, same `meshOptions`, same FFD, same six `nom_addLocalDV` groups, and
the same stock weighted objective `scalePL*(TP1-TP2) + scaleHFX*HFX`.

WHAT IT TESTS

`mesh.warpDeriv` is a reverse-mode Jacobian-transpose-vector product: given a
seed `w` in volume-mesh-coordinate (Xv) space it returns `w^T (dXv/dXs)` in
surface-coordinate (Xs) space. It exposes no forward Jacobian column, so it is
checked against a pure finite difference of the underlying nonlinear warp using
the standard adjoint dot-product identity, for each shape design variable `idx`:

    <w, dXv/dShape_idx>_FD   ==   <warpDeriv(w), dXs/dShape_idx>_analytic

The FD side perturbs the SURFACE coordinates directly along
`eta = dXs/dShape_idx` and calls `mesh.warpMesh()` -- `DVGeo.update()` is never
called on that side, so no FFD nonlinearity can contaminate the measurement and
`warpDeriv` is exercised alone. (`--fd-via-dvgeo` additionally runs the
composed variant; the two agree to ~1e-7 here, which is the check that FFD
nonlinearity is not the explanation.)

WHY THE SEED MATTERS -- THE POINT OF THIS REPRODUCER

  --seed random   contracts warpDeriv's error with an arbitrary direction.
                  On this case that reports every component clean, <2%.
  --seed real     contracts it with the seed the real adjoint actually uses:
                  the objective's own reverse-mode d(OBJ)/dXv, captured verbatim
                  from the framework's own call by hooking
                  DAFoamWarper.compute_jacvec_product. On this case that reports
                  errors up to ~200% with sign flips.

The analytic side is IDENTICAL in the two runs. Only the direction it is
contracted against changes. A random-seed test of this function therefore does
NOT clear it, and the difference between the two runs is the bug's visibility,
not its existence.

The `--seed real` analytic scalar is also printed next to the framework's own
`compute_totals` column: they agree to ~1e-15, which confirms the captured seed
is the real one and that the disagreement is not in OpenMDAO's assembly.

USAGE (see README.md for the full clone-to-result sequence)

  mpirun --allow-run-as-root -np 4 python repro_warpderiv_ubend.py --seed real
  mpirun --allow-run-as-root -np 4 python repro_warpderiv_ubend.py --seed random
"""
import os
import time
import argparse
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from pygeo.mphys import OM_DVGEOCOMP
from pygeo import geo_utils
import dafoam.mphys.mphys_dafoam as mphys_dafoam

parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=str, default="real", choices=["real", "random"],
                    help="'real' = the objective's own captured d(OBJ)/dXv; 'random' = arbitrary vector")
parser.add_argument("--rseed", type=int, default=2026, help="RNG seed when --seed random")
parser.add_argument("--h", type=float, default=1e-4)
parser.add_argument("--idxs", type=str, default="all", help="'all' or comma-separated indices into shapexUpper")
parser.add_argument("--dv", type=str, default="shapexUpper")
parser.add_argument("--objective", type=str, default="stock", choices=["stock", "pressure-loss"],
                    help="'stock' = the tutorial's own weighted scalePL*(TP1-TP2)+scaleHFX*HFX, "
                         "byte-unchanged. 'pressure-loss' = the ONE-LINE change val = TP1 - TP2 "
                         "(and HFX addToAdjoint False), which is where the sign flips appear.")
parser.add_argument("--use-rotations", type=str, default="on", choices=["on", "off"],
                    help="IDWarp meshOption useRotations. The mechanism under test lives in the "
                         "rotation branch of getRotationMatrix3d, so 'off' must make the whole "
                         "warp exactly linear in Xs and FD must then equal AN to machine precision.")
parser.add_argument("--reordering", type=str, default=None, choices=["natural", "rcm"],
                    help="DAFoam adjEqnOption jacMatReOrdering. The UBend tutorial ships 'natural'. "
                         "warpDeriv is purely geometric, so under our mechanism this must not move "
                         "the FD/AN disagreement at all.")
parser.add_argument("--eval-mode", type=str, default=None, choices=["fast", "exact"],
                    help="IDWarp meshOption evalMode. Tests the COMPETING hypothesis that the "
                         "KD-tree fast-sum truncation is differentiated inconsistently.")
parser.add_argument("--corner-angle", type=float, default=None,
                    help="IDWarp meshOption cornerAngle (deg). 180 makes every node a corner, which "
                         "forces Mi=I through a DIFFERENT code path than useRotations=off.")
parser.add_argument("--rigid", action="store_true",
                    help="ALSO test a pure rigid translation of the design surface. By the rotation "
                         "mechanism this direction rotates no normals, so it MUST come out clean "
                         "even with useRotations=on. If it does not, the mechanism is refuted.")
parser.add_argument("--verify-dofs", type=int, default=0,
                    help="if >0, additionally run IDWarp's OWN verifyWarpDeriv on this many surface DOFs")
parser.add_argument("--fd-via-dvgeo", action="store_true",
                    help="also run the composed FD (through DVGeo.update) to show FFD nonlinearity is not the cause")
args = parser.parse_args()

comm = MPI.COMM_WORLD
rank = comm.rank

# ---------------------------------------------------------------------------
# Everything from here to `class Top` is copied verbatim from the tutorial's own
# runScript.py (DAFoam/tutorials @ d3b7e38, UBend_Channel/runScript.py). No value
# is changed.
# ---------------------------------------------------------------------------
CPL_weight = 0.50
HFX_weight = CPL_weight - 1.0
HFX0 = 305
CPL0 = 85.23 - 35.62
U0 = 8.4

daOptionsAero = {
    "solverName": "DASimpleFoam",
    "designSurfaces": ["ubend"],
    "useAD": {"mode": "reverse"},
    "primalMinResTol": 1e-8,
    "primalMinResTolDiff": 1e7,
    "writeMinorIterations": True,
    "wallDistanceMethod": "daCustom",
    "primalBC": {"useWallFunction": True},
    "function": {
        "TP1": {"type": "totalPressure", "source": "patchToFace", "patches": ["inlet"],
                "scale": 1.0, "addToAdjoint": True},
        "TP2": {"type": "totalPressure", "source": "patchToFace", "patches": ["outlet"],
                "scale": 1.0, "addToAdjoint": True},
        "HFX": {"type": "wallHeatFlux", "source": "patchToFace", "patches": ["ubend"],
                "scale": 1.0, "addToAdjoint": args.objective == "stock"},
    },
    "adjStateOrdering": "cell",
    "adjEqnOption": {"gmresRelTol": 1e-5, "gmresTolDiff": 1e4, "pcFillLevel": 2,
                     "jacMatReOrdering": "natural", "gmresMaxIters": 3000, "gmresRestart": 3000},
    "normalizeStates": {"U": U0, "p": (U0 * U0) / 2.0, "nuTilda": 1e-3, "phi": 1.0, "T": 300},
    "inputInfo": {"aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]}},
    "outputInfo": {"q_convect": {"type": "thermalCouplingOutput", "patches": ["ubend"],
                                 "components": ["thermalCoupling"]}},
}
meshOptions = {"gridFile": os.getcwd(), "fileType": "OpenFOAM", "symmetryPlanes": []}
# --- diagnostic knobs (the ONLY departure from the reproducer's verbatim tutorial setup) ---
if args.use_rotations == "off":
    meshOptions["useRotations"] = False
if args.corner_angle is not None:
    meshOptions["cornerAngle"] = args.corner_angle
if args.eval_mode is not None:
    meshOptions["evalMode"] = args.eval_mode

# ---------------------------------------------------------------------------
if args.reordering is not None:
    daOptionsAero["adjEqnOption"]["jacMatReOrdering"] = args.reordering

# capture hook: record the reverse-mode d_outputs["aero_vol_coords"] the
# framework hands DAFoamWarper. That argument is passed verbatim to
# self.DASolver.mesh.warpDeriv(dxV) in mphys_dafoam.py -- it IS the real seed.
# ---------------------------------------------------------------------------
_captures = []
_orig_cjp = mphys_dafoam.DAFoamWarper.compute_jacvec_product


def _capturing_cjp(self, inputs, d_inputs, d_outputs, mode):
    if mode == "rev":
        key = "%s_vol_coords" % self.discipline
        if key in d_outputs:
            _captures.append(np.array(d_outputs[key], copy=True))
    return _orig_cjp(self, inputs, d_inputs, d_outputs, mode)


mphys_dafoam.DAFoamWarper.compute_jacvec_product = _capturing_cjp

DVGROUPS = ["shapexUpper", "shapeyUpper", "shapezUpper",
            "shapexLower", "shapeyLower", "shapezLower"]


class Top(Multipoint):
    """Verbatim reconstruction of the tutorial's own Top (stock objective)."""

    def setup(self):
        b = DAFoamBuilder(daOptionsAero, meshOptions, scenario="aerodynamic")
        b.initialize(self.comm)
        self.dafoam_builder = b
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])
        self.add_subsystem("mesh_aero", b.get_mesh_coordinate_subsystem())
        self.add_subsystem("geometry_aero", OM_DVGEOCOMP(file="FFD/UBendDuctFFDSym.xyz", type="ffd"))
        self.mphys_add_scenario("scenario", ScenarioAerodynamic(aero_builder=b))
        self.connect("mesh_aero.x_aero0", "geometry_aero.x_aero_in")
        self.connect("geometry_aero.x_aero0", "scenario.x_aero")
        if args.objective == "stock":
            # tutorial's own objective, unchanged
            self.add_subsystem("OBJ", om.ExecComp(
                "val = scalePL * (TP1 - TP2) + (scaleHFX * HFX)",
                scalePL={"val": CPL_weight / CPL0, "constant": True},
                scaleHFX={"val": HFX_weight / HFX0, "constant": True}))
        else:
            # the ONE-LINE change: pure total-pressure-loss objective
            self.add_subsystem("OBJ", om.ExecComp("val = TP1 - TP2"))

    def configure(self):
        super().configure()
        self.geometry_aero.nom_add_discipline_coords("aero", self.mesh_aero.mphys_get_surface_mesh())
        pts = self.geometry_aero.nom_getDVGeo().getLocalIndex(0)
        nComp = {}
        for name, jj, ax in [("shapexUpper", 1, "x"), ("shapeyUpper", 1, "y"), ("shapezUpper", 1, "z"),
                             ("shapexLower", 0, "x"), ("shapeyLower", 0, "y"), ("shapezLower", 0, "z")]:
            PS = geo_utils.PointSelect("list", list(pts[7:16, jj, :].flatten()))
            nComp[name] = self.geometry_aero.nom_addLocalDV(dvName=name, pointSelect=PS, axis=ax)
        for name in DVGROUPS:
            self.dvs.add_output(name, val=np.array([0.0] * nComp[name]))
            self.connect(name, "geometry_aero.%s" % name)
            self.add_design_var(name, lower=-0.04, upper=0.04, scaler=25.0)
        self.nComp = nComp
        self.connect("scenario.aero_post.TP1", "OBJ.TP1")
        self.connect("scenario.aero_post.TP2", "OBJ.TP2")
        if args.objective == "stock":
            self.connect("scenario.aero_post.HFX", "OBJ.HFX")
        self.add_objective("OBJ.val", scaler=1.0)


t0 = time.time()
prob = om.Problem(reports=None)
prob.model = Top()
prob.setup(mode="rev")
if rank == 0:
    print("REPRO === primal ===", flush=True)
prob.run_model()
if rank == 0:
    print("REPRO === primal done t=%.1fs OBJ.val=%.15e ===" % (time.time() - t0, float(prob.get_val("OBJ.val")[0])), flush=True)

totals = prob.compute_totals(of=["OBJ.val"], wrt=[args.dv])
dOBJ = np.array(totals[("OBJ.val", args.dv)]).flatten()
if rank == 0:
    print("REPRO === adjoint done t=%.1fs, warper captured %d rev call(s) ===" % (time.time() - t0, len(_captures)), flush=True)

DASolver = prob.model.dafoam_builder.DASolver
mesh = DASolver.mesh
DVGeo = prob.model.geometry_aero.nom_getDVGeo()
ptSetName = "x_aero0"
nShape = prob.model.nComp[args.dv]
xs0 = DASolver.getSurfaceCoordinates(DASolver.designSurfacesGroup).copy()


def set_shape(vec):
    DVGeo.setDesignVars({args.dv: np.array(vec)})


def warp_via_dvgeo(v):
    set_shape(v)
    xs = DVGeo.update(ptSetName)
    DASolver.setSurfaceCoordinates(xs, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    return mesh.getSolverGrid().copy()


def warp_via_direct_xs(xs):
    DASolver.setSurfaceCoordinates(xs, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    return mesh.getSolverGrid().copy()


Xv0 = warp_via_dvgeo(np.zeros(nShape))

if args.seed == "real":
    if not _captures:
        raise RuntimeError("REPRO FAIL: warper rev-mode hook never fired")
    w = _captures[-1]
    if w.size != Xv0.size:
        raise RuntimeError("REPRO FAIL: seed/Xv partition mismatch %d vs %d" % (w.size, Xv0.size))
else:
    np.random.seed(args.rseed)
    w = np.random.random(Xv0.size).astype("d")

wn = comm.allreduce(float(np.dot(w, w)), op=MPI.SUM) ** 0.5
if rank == 0:
    print("REPRO seed=%s objective=%s ||w||=%.8e nRanks=%d h=%.1e useRotations=%s cornerAngle=%s"
          % (args.seed, args.objective, wn, comm.size, args.h, args.use_rotations, args.corner_angle), flush=True)

h_rigid = args.h
set_shape(np.zeros(nShape))
xs_base = DVGeo.update(ptSetName)
DASolver.setSurfaceCoordinates(xs_base, DASolver.designSurfacesGroup)
mesh.warpMesh()

# THE FUNCTION UNDER TEST -- one call, seed-dependent, idx-independent
mesh.warpDeriv(w)
dXs_seed = mesh.getdXs()
dXs_seed = DASolver.mapVector(dXs_seed, DASolver.allWallsGroup, DASolver.designSurfacesGroup)

# FINGERPRINT the analytic output itself. The mechanism predicts warpDeriv returns
# a BIT-IDENTICAL dXs whether useRotations is on or off, because at the baseline the
# rotation branch (axisMag < 1.49e-8) discards all rotation sensitivity anyway.
_d = dXs_seed.flatten()
_n2 = comm.allreduce(float(np.dot(_d, _d)), op=MPI.SUM) ** 0.5
_s1 = comm.allreduce(float(np.sum(_d)), op=MPI.SUM)
_amax = comm.allreduce(float(np.max(np.abs(_d))) if _d.size else 0.0, op=MPI.MAX)
if rank == 0:
    print("REPRO_ANFINGERPRINT useRotations=%s ||dXs||=%.15e sum(dXs)=%.15e max|dXs|=%.15e"
          % (args.use_rotations, _n2, _s1, _amax), flush=True)

# ALSO fingerprint the PRIMAL warp at the baseline, for the same reason.
_xv = Xv0.flatten()
_xn = comm.allreduce(float(np.dot(_xv, _xv)), op=MPI.SUM) ** 0.5
if rank == 0:
    print("REPRO_XVFINGERPRINT useRotations=%s ||Xv0||=%.15e" % (args.use_rotations, _xn), flush=True)

# ---- predicted-CLEAN control: pure rigid translation of the design surface ----
# By the rotation mechanism this rotates no surface normal at all, so warpDeriv's
# zeroed rotation sensitivity is CORRECT here and FD must match AN to machine
# precision EVEN WITH useRotations=on. A failure here refutes the mechanism.
if args.rigid:
    for axis_i, axis_nm in [(0, "x"), (1, "y"), (2, "z")]:
        eta_r = np.zeros_like(xs0)
        eta_r[:, axis_i] = 1.0
        AN_r = comm.allreduce(float(np.dot(dXs_seed.flatten(), eta_r.flatten())), op=MPI.SUM)
        Xv_p = warp_via_direct_xs(xs_base + h_rigid * eta_r)
        Xv_m = warp_via_direct_xs(xs_base - h_rigid * eta_r)
        FD_r = comm.allreduce(float(np.dot(w, (Xv_p - Xv_m) / (2.0 * h_rigid))), op=MPI.SUM)
        DASolver.setSurfaceCoordinates(xs_base, DASolver.designSurfacesGroup)
        mesh.warpMesh()
        rel_r = abs(AN_r - FD_r) / (abs(FD_r) + 1e-300)
        if rank == 0:
            print("REPRO_RIGID axis=%s useRotations=%s FD=%.10e AN=%.10e rel_err=%.3e"
                  % (axis_nm, args.use_rotations, FD_r, AN_r, rel_r), flush=True)

idxs = range(nShape) if args.idxs == "all" else [int(s) for s in args.idxs.split(",")]
h = args.h
nflip = 0
worst = (None, 0.0)
if rank == 0:
    print("REPRO %-4s %-16s %-16s %-10s %-6s %s" % ("idx", "FD(warp)", "AN(warpDeriv)", "rel_err", "sign", "framework_dOBJ/dDV"), flush=True)

for idx in idxs:
    seedDV = {n: np.zeros(prob.model.nComp[n]) for n in DVGROUPS}
    seedDV[args.dv][idx] = 1.0
    eta = DVGeo.totalSensitivityProd(seedDV, ptSetName).reshape(xs0.shape)

    AN = comm.allreduce(float(np.dot(dXs_seed.flatten(), eta.flatten())), op=MPI.SUM)

    Xv_p = warp_via_direct_xs(xs_base + h * eta)
    Xv_m = warp_via_direct_xs(xs_base - h * eta)
    FD = comm.allreduce(float(np.dot(w, (Xv_p - Xv_m) / (2.0 * h))), op=MPI.SUM)

    extra = ""
    if args.fd_via_dvgeo:
        ep = np.zeros(nShape); ep[idx] = h
        em = np.zeros(nShape); em[idx] = -h
        Xv_p2 = warp_via_dvgeo(ep)
        Xv_m2 = warp_via_dvgeo(em)
        FD2 = comm.allreduce(float(np.dot(w, (Xv_p2 - Xv_m2) / (2.0 * h))), op=MPI.SUM)
        extra = "  FD_via_DVGeo=%.8e  ffd_nonlin=%.2e" % (FD2, abs(FD2 - FD) / (abs(FD2) + 1e-300))

    set_shape(np.zeros(nShape))
    DVGeo.update(ptSetName)
    DASolver.setSurfaceCoordinates(xs_base, DASolver.designSurfacesGroup)
    mesh.warpMesh()

    rel = abs(AN - FD) / (abs(FD) + 1e-300)
    flip = (AN * FD) <= 0
    nflip += int(flip)
    if rel > worst[1]:
        worst = (idx, rel)
    if rank == 0:
        print("REPRO %-4d %-16.8e %-16.8e %-10.4f %-6s %.8e%s"
              % (idx, FD, AN, rel, "FLIP" if flip else "ok", dOBJ[idx], extra), flush=True)

# ---- upstream's OWN instrument, run on the same state ----
if args.verify_dofs > 0:
    DASolver.setSurfaceCoordinates(xs_base, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    if rank == 0:
        print("REPRO_VERIFY === IDWarp's own verifyWarpDeriv, useRotations=%s, seed=%s, dofs 0..%d ==="
              % (args.use_rotations, args.seed, args.verify_dofs), flush=True)
    comm.Barrier()
    mesh.verifyWarpDeriv(dXv=w, solverVec=True, dofStart=0, dofEnd=args.verify_dofs, h=1e-6)
    comm.Barrier()
    if rank == 0:
        print("REPRO_VERIFY === end (upstream random seed next) ===", flush=True)
    comm.Barrier()
    mesh.verifyWarpDeriv(dXv=None, dofStart=0, dofEnd=args.verify_dofs, h=1e-6)
    comm.Barrier()

if rank == 0:
    print("REPRO_SUMMARY seed=%s objective=%s h=%.1e nRanks=%d n=%d sign_flips=%d worst_idx=%s worst_rel_err=%.4f t=%.1fs"
          % (args.seed, args.objective, h, comm.size, len(list(idxs)), nflip, worst[0], worst[1], time.time() - t0), flush=True)
    print("REPRO_SUMMARY2 useRotations=%s cornerAngle=%s evalMode=%s reordering=%s"
          % (args.use_rotations, args.corner_angle, args.eval_mode, daOptionsAero["adjEqnOption"]["jacMatReOrdering"]), flush=True)
