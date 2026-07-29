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

# --- (c) true per-cell k, compare to the actual FD perturbation delta ---
try:
    fdStep = DASolver.getOption("adjPartDerivFDStep")
    normStates = DASolver.getOption("normalizeStates")
    if rank == 0:
        print("adjPartDerivFDStep:", fdStep)
        print("normalizeStates:", normStates)
    kArr = np.zeros(DASolver.getNLocalCells(), dtype=np.float64)
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
for turbOnly, tag in [(1, "turbOnly"), (0, "full_incl_meanflow")]:
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

if rank == 0:
    print("DIAG_FROZEN_DONE")
