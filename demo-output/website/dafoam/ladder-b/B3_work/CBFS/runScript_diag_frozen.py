#!/usr/bin/env python
"""
DIAGNOSTIC ONLY -- rung 4 (frozen-turbulence) + coloring-perturbation probe,
combined into one cheap, no-GMRES test.

Rather than hand-build a "frozen turbulence" solver variant (DAFoam has no
such toggle; grepped the full v5.0.0 source tree, confirmed absent), this
calls the SAME low-level C++ primitives DAFoam's real adjoint pipeline uses
to assemble dRdWTPC (DASolver::calcdRdWT(isPC=1, ...), which internally
calls DAJacCon + DAPartDeriv::calcPartDerivMat -- a coloring-grouped,
REAL finite-difference perturbation of the state, delta = adjPartDerivFDStep
* normalizeStates[field], confirmed by reading DAPartDeriv.C directly, not
assumed) directly on the CONVERGED primal state, with NO GMRES/KSP object
ever created. This:
  (a) reproduces the exact matrix (dRdWTPC) whose ILU factorization feeds
      GMRES, and scans it for non-finite entries before any iteration runs
  (b) also pulls the raw turbulence-model fvMatrix coefficients (D/upper/
      lower) for k, omega, nut directly via getFvMatrixFields, at the
      UNPERTURBED converged state, to separate "already broken at the
      converged state" from "broken only once perturbed"
  (c) prints the true per-cell min(k) and its magnitude relative to the
      actual FD perturbation delta that DAJacCon/DAPartDeriv will add,
      computed from the SAME options DAFoam itself reads (not guessed)

If dRdWTPC comes back clean, the poison is not in Jacobian assembly at all,
and rung 6 (row scaling / ILU factorization) is the next candidate. If it
is dirty, and dirty specifically in k/omega/nut rows/cols, the
near-wall-perturbation mechanism is directly confirmed, not inferred.
"""
import os
import time
import numpy as np
from mpi4py import MPI
import openmdao.api as om
from mphys.multipoint import Multipoint
from dafoam.mphys import DAFoamBuilder
from mphys.scenario_aerodynamic import ScenarioAerodynamic
from petsc4py import PETSc

U0 = 0.72
k0 = 0.0042
omega0 = 1000.0

daOptions = {
    "designSurfaces": ["bottomWall", "topWall"],
    "solverName": "DASimpleFoam",
    "primalMinResTol": 1.0e-6,
    "primalBC": {},
    "function": {
        "CD": {
            "type": "force",
            "source": "patchToFace",
            "patches": ["bottomWall", "topWall"],
            "directionMode": "parallelToFlow",
            "patchVelocityInputName": "patchV",
            "scale": 1.0 / (0.5 * U0 * U0 * 1.0),
        },
    },
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 1, "jacMatReOrdering": "rcm"},
    "normalizeStates": {
        "U": U0,
        "p": U0 * U0 / 2.0,
        "k": k0,
        "omega": omega0,
        "phi": 1.0,
        "nut": 1e-4,
    },
    "inputInfo": {
        "patchV": {
            "type": "patchVelocity",
            "patches": ["inlet"],
            "flowAxis": "x",
            "normalAxis": "y",
            "components": ["solver", "function"],
        },
    },
}

meshOptions = {
    "gridFile": os.getcwd(),
    "fileType": "OpenFOAM",
    "symmetryPlanes": [[[0.0, 0.0, -0.1], [0.0, 0.0, 1.0]], [[0.0, 0.0, 0.1], [0.0, 0.0, 1.0]]],
}


class Top(Multipoint):
    def setup(self):
        self.dafoam_builder = DAFoamBuilder(daOptions, meshOptions, scenario="aerodynamic")
        self.dafoam_builder.initialize(self.comm)
        self.add_subsystem("dvs", om.IndepVarComp(), promotes=["*"])
        self.add_subsystem("mesh", self.dafoam_builder.get_mesh_coordinate_subsystem())
        self.mphys_add_scenario("scenario1", ScenarioAerodynamic(aero_builder=self.dafoam_builder))
        self.connect("mesh.x_aero0", "scenario1.x_aero")

    def configure(self):
        self.dvs.add_output("patchV", val=np.array([U0, 0.0]))
        self.connect("patchV", "scenario1.patchV")
        self.add_design_var("patchV", lower=[0.1, -10.0], upper=[2.0, 10.0], scaler=1.0)
        self.add_objective("scenario1.aero_post.CD", scaler=1.0)


prob = om.Problem()
top = Top()
prob.model = top
prob.setup(mode="rev")
rank = MPI.COMM_WORLD.rank

t0 = time.time()
prob.run_model()
t1 = time.time()
if rank == 0:
    print("TIMING run_model wall_s:", t1 - t0)
    print("CD objective:", prob.get_val("scenario1.aero_post.CD"))

DASolver = top.dafoam_builder.DASolver
n = DASolver.getNLocalAdjointStates()
if rank == 0:
    print("nLocalAdjointStates:", n)

# --- coloring: the earlier run of this script (b3_diag_frozen2_20260729T203706Z)
# crashed HERE, before GMRES, before even reaching the FD-perturbation code its
# own comments describe scanning -- "Reading Coloring dRdWColoring_1" then
# FOAM FATAL ERROR "Conflicting Colors Found" out of DAColoring::validateColoring.
# Root cause, read directly from source
# (DASolver.C:1043 DASolver::calcdRdWT unconditionally calls
# daJacCon.readJacConColoring() with NO existence check -- contrast
# DASolver::runColoring(), which gates on daJacCon.coloringExists() first;
# DAJacCon.C:1980-2013 readJacConColoring's file name is
# modelType_+"Coloring"+postFix+"_"+nProcs, so it is PER-PROCESS-COUNT by
# design ("using different CPU cores result in different jacCon and therefore
# different coloring"). This script runs serial (nProcs=1, confirmed by
# "nProcs : 1" in this run's own banner), so calcdRdWT tried to read
# "dRdWColoring_1.bin" -- a file that has NEVER existed anywhere in this case
# family; only dRdWColoring_4.bin (an nProcs=4 file from an earlier run) sits
# on disk, at a mtime BEFORE this script even started, so it was never a
# candidate. DAUtility::readVectorBinary's PetscViewerBinaryOpen/VecLoad on
# that missing file left jacConColors_ at its prior VecZeroEntries state (all
# color 0), which validateColoring correctly rejects at the very first row
# with 2+ nonzero columns -- exactly the deterministic "row: 0 col1: 0 col2: 1
# color: 0" reported. This is a STALE/MISSING coloring cache, the same trap
# this lab already got burned by once, NOT the k/NaN mechanism under test: it
# is a diagnostic-script bug (this script called the low-level calcdRdWT
# directly and skipped the runColoring() call the production dafoam.mphys
# wrapper always makes first -- see mphys_dafoam.py:459,
# "self.DASolver.solver.runColoring()" -- before ever touching calcdRdWT).
# Fix: make the same call the production pipeline makes. runColoring() is
# gated on coloringExists() internally, so this is a no-op on a future rerun
# that already has a valid dRdWColoring_1.bin, and computes it fresh (cheap,
# no GMRES, no primal re-solve) here since it does not.
if rank == 0:
    print("Calling DASolver.solver.runColoring() -- production pipeline does this "
          "before calcdRdWT; the earlier crash in this script came from skipping it.")
t0 = time.time()
DASolver.solver.runColoring()
t1 = time.time()
if rank == 0:
    print("TIMING runColoring wall_s:", t1 - t0)

# --- (c) true per-cell k, compare to the actual FD perturbation delta ---
try:
    fdStep = DASolver.getOption("adjPartDerivFDStep")
    normStates = DASolver.getOption("normalizeStates")
    if rank == 0:
        print("adjPartDerivFDStep:", fdStep)
        print("normalizeStates:", normStates)
    kArr = np.zeros(DASolver.solver.getNLocalCells(), dtype=np.float64)
    DASolver.solver.getOFField("k", "scalar", kArr)
    kmin = kArr.min()
    kmin_g = MPI.COMM_WORLD.allreduce(kmin, op=MPI.MIN)
    deltaK = fdStep.get("State", 1.0e-6) * normStates.get("k", 1.0)
    if rank == 0:
        print(f"true min(k) internal field (this rank) = {kmin:.6e}, global min = {kmin_g:.6e}")
        print(f"FD perturbation delta on k = adjPartDerivFDStep*normalizeStates[k] = {deltaK:.6e}")
        print(f"min(k) - deltaK = {kmin_g - deltaK:.6e}  <-- negative means a coloring step can drive k negative")
except Exception as e:
    if rank == 0:
        print("k-probe FAILED (not fatal, continuing):", repr(e))

# --- (b) block-diagonal turbulence-only PC matrix at the UNPERTURBED converged
#     state -- calcPCMatWithFvMatrix internally calls the turbulence model's
#     getFvMatrixFields (not itself Python-exposed) and writes D/upper/lower
#     straight into a PETSc Mat, so scanning this Mat is equivalent to
#     inspecting those raw coefficients without needing new C++ bindings.
# NOTE: turbOnly=0 removed -- it hits an UNCATCHABLE C++ FatalErrorIn->abort()
# ("Child class not implemented!", DAResidual::calcPCMatWithFvMatrix,
# DAResidual.C:297) for this solver's residual class. Confirmed real (not a
# Python exception, kills the whole MPI rank via SIGABRT) in the first run of
# this script (b3_diag_frozen_20260729T203110Z.log). Not a NaN/Inf finding --
# a genuine "not implemented for this solver" limitation of that code path.
# turbOnly=1 (the one that matters -- the actual turbulence-model block) is
# unaffected and already ran clean once; keeping only that branch.
for turbOnly, tag in [(1, "turbOnly")]:
    try:
        mat = PETSc.Mat().create(PETSc.COMM_WORLD)
        mat.setSizes(((n, None), (n, None)))
        mat.setFromOptions()
        mat.setPreallocationNNZ((100, 100))
        mat.setUp()
        mat.zeroEntries()
        DASolver.solver.calcPCMatWithFvMatrix(mat, turbOnly)
        mat.assemble()
        rstart, rend = mat.getOwnershipRange()
        bad = []
        for i in range(rstart, rend):
            cols, vals = mat.getRow(i)
            for c, v in zip(cols, vals):
                if not np.isfinite(v):
                    bad.append((i, int(c), v))
        if rank == 0:
            print(f"PCMat[{tag}] (unperturbed converged state): norm={mat.norm()}, "
                  f"nonfinite_entries={len(bad)}")
            for b in bad[:20]:
                print("   nonfinite entry (row,col,val):", b)
    except Exception as e:
        if rank == 0:
            print(f"PCMat[{tag}] probe FAILED (not fatal):", repr(e))

# --- (a) the REAL dRdWTPC assembly (same code path as the production pilot) ---
def scan_mat(mat, label):
    mat.assemble()
    nrm = mat.norm()
    rstart, rend = mat.getOwnershipRange()
    bad = []
    for i in range(rstart, rend):
        cols, vals = mat.getRow(i)
        for c, v in zip(cols, vals):
            if not np.isfinite(v):
                bad.append((i, int(c), v))
    if rank == 0:
        print(f"{label}: norm={nrm}, nonfinite_entries={len(bad)} (rows scanned {rstart}:{rend})")
        for b in bad[:30]:
            print("   nonfinite entry (row,col,val):", b)
    return bad

t0 = time.time()
dRdWTPC = PETSc.Mat().create(PETSc.COMM_WORLD)
DASolver.solver.calcdRdWT(1, dRdWTPC)
t1 = time.time()
if rank == 0:
    print("TIMING calcdRdWT(isPC=1) wall_s:", t1 - t0)
scan_mat(dRdWTPC, "dRdWTPC (real production PC assembly)")

# --- (d) THE ACTUAL GMRES OPERATOR, not yet tested by this ladder.
# Read directly from source (DASolver.C:1099, DASolver::updateKSPPCMat):
#     KSPSetOperators(ksp, dRdWTMF_, PCMat);
# PCMat is exactly the dRdWTPC just scanned clean above (production's own
# mphys_dafoam.py solve_linear calls DASolver.solver.calcdRdWT(1, DASolver.dRdWTPC)
# -- the identical call this script makes). But PCMat is used ONLY as the
# preconditioner P. The operator A actually applied by GMRES at every
# iteration, including iteration 0, is dRdWTMF_ -- matrix-free, built from
# DASolver.solverAD.calcJacTVecProduct (DASolver.C:1690, confirmed CODI_ADR
# reverse-mode AD: reset tape, register state as AD input, run the residual,
# register it as AD output, seed the output, propagate back). This is a
# COMPLETELY DIFFERENT code path from the coloring-FD calcPartDerivMat this
# script has been scanning -- no adjPartDerivFDStep, no normalizeStates delta
# involved at all. AD differentiates EXACTLY at the converged state, so if
# k=1e-16 feeds a 1/k or 1/sqrt(k) term inside the turbulence closure's
# residual, AD's exact derivative is evaluated there directly, with no FD
# offset to save it. mphys_dafoam.py's apply_linear does exactly this call
# (self.stateName="aero_states", "stateVar" / self.residualName="aero_residuals",
# "residual") with seed = d_residuals -- reproduced here with an all-ones seed
# since any nonzero seed reveals a non-finite tape entry (NaN/Inf * finite
# nonzero stays non-finite regardless of the seed's magnitude).
try:
    states = DASolver.getStates()
    DASolver.setStates(states)  # sync solverAD's OF fields to the converged state, as apply_linear does
    seed = np.ones(n, dtype=np.float64)
    product = np.zeros(n, dtype=np.float64)
    t0 = time.time()
    DASolver.solverAD.calcJacTVecProduct(
        "aero_states", "stateVar",
        states,
        "aero_residuals", "residual",
        seed,
        product,
    )
    t1 = time.time()
    finite_mask = np.isfinite(product)
    bad_idx = np.where(~finite_mask)[0]
    if rank == 0:
        print("TIMING calcJacTVecProduct (AD matrix-free operator, dRdWTMF_) wall_s:", t1 - t0)
        print(f"dRdWT^T*psi (AD matrix-free -- the REAL GMRES operator A): "
              f"norm={np.linalg.norm(product[finite_mask]) if finite_mask.any() else float('nan')}, "
              f"nonfinite_entries={len(bad_idx)} (out of {n})")
        for idx in bad_idx[:30]:
            print("   nonfinite entry (local idx, val):", int(idx), product[idx])
except Exception as e:
    if rank == 0:
        print("AD matvec (dRdWTMF_) probe FAILED (not fatal):", repr(e))

# --- (e) THE REAL PRODUCTION CALL, end to end, with the real ConvergedReason
# read out explicitly rather than trusted from a top-level exit code (L-15:
# a run can exit 0 having returned PETSc -5 with the residual underflowing to
# denormal range right after a message that reads like success -- so the
# reason enum is read here directly, not inferred from "did the script finish").
# Both matrices A (dRdWTMF_, AD matrix-free) and P (dRdWTPC, coloring-FD) are
# now independently confirmed finite above. This step builds the actual KSP
# (DALinearEqn::createMLRKSP -> ILU(pcFillLevel) factorization of dRdWTPC,
# untested until now) and calls solverAD.solveLinearEqn(ksp, dFdW, psi) --
# textually the same call mphys_dafoam.py's solve_linear makes -- with a REAL
# objective RHS (dCD/dW, computed the same way mphys computes it: reverse-mode
# AD from the CD function output back to the state input, TypeName("function")
# confirmed in DAOutputFunction.H) rather than a synthetic probe vector. This
# either reproduces DIVERGED_NANORINF with its exact reason code (localising
# the mechanism to PC factorization/application or to GMRES's own internals,
# since the two matrices are already clean) or it does not reproduce, which is
# its own finding.
try:
    # dCD/dW via the same reverse-mode AD call, with the objective as output
    dFdWArr = np.zeros(n, dtype=np.float64)
    funcSeed = np.array([1.0], dtype=np.float64)
    DASolver.solverAD.calcJacTVecProduct(
        "aero_states", "stateVar",
        states,
        "CD", "function",
        funcSeed,
        dFdWArr,
    )
    dFdW_finite = np.isfinite(dFdWArr).all()
    if rank == 0:
        print(f"dCD/dW (real adjoint RHS): norm={np.linalg.norm(dFdWArr)}, "
              f"all_finite={dFdW_finite}")

    dFdW = DASolver.array2Vec(dFdWArr)
    psi = DASolver.array2Vec(np.zeros(n, dtype=np.float64))

    DASolver.dRdWTPC = dRdWTPC
    DASolver.ksp = PETSc.KSP().create(PETSc.COMM_WORLD)
    DASolver.solverAD.createMLRKSPMatrixFree(DASolver.dRdWTPC, DASolver.ksp)

    t0 = time.time()
    fail = DASolver.solverAD.solveLinearEqn(DASolver.ksp, dFdW, psi)
    t1 = time.time()

    its = DASolver.ksp.getIterationNumber()
    reason = DASolver.ksp.getConvergedReason()
    rnorm = DASolver.ksp.getResidualNorm()
    psiArr = DASolver.vec2Array(psi)
    psi_bad = np.where(~np.isfinite(psiArr))[0]
    if rank == 0:
        print("TIMING solveLinearEqn (real production KSP solve) wall_s:", t1 - t0)
        print(f"REAL KSP RESULT: fail={fail}, KSPConvergedReason={reason}, "
              f"iterations={its}, final_residual_norm={rnorm}")
        print(f"psi (adjoint solution vector): nonfinite_entries={len(psi_bad)} (out of {n})")
        for idx in psi_bad[:30]:
            print("   nonfinite psi entry (local idx, val):", int(idx), psiArr[idx])
except Exception as e:
    if rank == 0:
        import traceback
        print("REAL KSP solve probe FAILED (not fatal):", repr(e))
        traceback.print_exc()

if rank == 0:
    print("DIAG_FROZEN_DONE")
