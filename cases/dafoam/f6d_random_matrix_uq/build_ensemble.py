"""
F6d -- build and drive the random-matrix UQ ensemble on the F6b periodic-hill
case (PH_Breuer, Re_H = 10595).

Propagation model (paper Appendix A step 3.1: "Use the obtained sampled
Reynolds stress to velocity and other QoIs by solving the RANS equation"):

  The sampled Reynolds stress [R] is PRESCRIBED.  The turbulence transport
  equations are switched off (`turbulence off`) so k, omega, nut stay frozen at
  their converged baseline values; nut is retained ONLY inside the implicit
  diffusion operator, for linear-solver conditioning, and is then cancelled
  exactly by the explicit source, so that at convergence the deviatoric stress
  carried by the momentum equation is dev([R]) and nothing else.

  simpleFoam assembles      div(phi,U) + divDevReff(U) == fvOptions(U)
  with divDevReff(U) = -div(2*nuEff*symm(grad U)).  A source `eqn += X` puts
  +X on the RHS (verified: signcheck/, four runs, and OpenFOAM v2606 sources
  fvMatrix.C:1676-1683, meanVelocityForce.C:190-210).  Therefore the effective
  deviatoric Reynolds stress is

        R_eff = R_model - deltaR,    R_model = -2*nut*dev(symm(grad U))

  so prescribing R_eff = dev(R_sample) requires

        deltaR = -nut*dev(twoSymm(grad U)) - dev(R_sample)              (*)

  which is what system/fvOptions computes, live, every outer iteration.

  NULL TEST built into this design: with R_sample = R_bar (the baseline
  Boussinesq stress itself), (*) is identically zero at the baseline velocity
  field, so the ensemble member must sit still at the baseline.  Any drift is
  an implementation error, not physics.  Sample id "null" does exactly this.

Usage:
    python3 build_ensemble.py --delta 0.2 --n 30 --seed 20260730
    python3 build_ensemble.py --null
    python3 build_ensemble.py --corners          # eigenspace corner comparison
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CASE = HERE.parent / "f6b_periodic_hills" / "case_breuer_re10595"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(CASE))

import rmt_sampler as rmt  # noqa: E402
import foam_io as fio      # noqa: E402

BASELINE_TIME = "10000"
R_PATH = CASE / BASELINE_TIME / "turbulenceProperties:R"
ENS = HERE / "ens"
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

END_TIME = 4000
WRITE_INTERVAL = 4000


# --------------------------------------------------------------------------
FVOPTIONS = """FoamFile
{{
    version 2.0; format ascii; class dictionary; location "system"; object fvOptions;
}}
// F6d random-matrix UQ propagation source.  See build_ensemble.py for the
// full derivation and for the sign verification (signcheck/).
//
//   deltaR = -nut*dev(twoSymm(grad U)) - dev(Rsample)
//   eqn += fvc::div(deltaR)   =>   R_eff = R_model - deltaR = dev(Rsample)
//
// mode "prescribe"  : exactly the above (this study's propagation model).
// mode "f6a_sign"   : eqn += fvc::div(+2k(bPert-bB)), i.e. bit-for-bit the
//                     sign used by f6a_epistemic_band/*/system/fvOptions,
//                     kept only so the two can be compared on one case.

momentumSource
{{
    type            meanVelocityForce;
    selectionMode   all;
    fields          (U);
    Ubar            (0.72 0 0);
}}

rmtPropagate
{{
    type            vectorCodedSource;
    active          true;
    name            rmtPropagate{tag};

    vectorCodedSourceCoeffs
    {{
        selectionMode   all;
        fields          (U);
        name            rmtPropagate{tag};

        codeInclude
        #{{
            #include "fvCFD.H"
        #}};

        codeCorrect   #{{ #}};
        codeConstrain #{{ #}};

        codeAddSup
        #{{
            const fvMesh& m = this->mesh();
            const volVectorField& U = eqn.psi();
            const volScalarField& nut = m.lookupObject<volScalarField>("nut");

            if (!m.foundObject<volSymmTensorField>("Rsample"))
            {{
                volSymmTensorField* pf = new volSymmTensorField
                (
                    IOobject
                    (
                        "Rsample",
                        m.time().constant(),
                        m,
                        IOobject::MUST_READ,
                        IOobject::NO_WRITE
                    ),
                    m
                );
                pf->store();
            }}
            const volSymmTensorField& Rs =
                m.lookupObject<volSymmTensorField>("Rsample");

            volSymmTensorField deltaR
            (
                "deltaR",
                (-1.0)*nut*dev(twoSymm(fvc::grad(U))) - dev(Rs)
            );

            eqn += fvc::div(deltaR);
        #}};
    }}
}}
"""

CONTROLDICT = """FoamFile
{{
    version 2.0; format ascii; class dictionary; location "system"; object controlDict;
}}
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {end};
deltaT          1;
writeControl    timeStep;
writeInterval   {wi};
purgeWrite      0;
writeFormat     ascii;
writePrecision  15;
writeCompression uncompressed;
timeFormat      general;
timePrecision   15;
runTimeModifiable no;

functions
{{
  #includeFunc  singleGraph_x0
  #includeFunc  singleGraph_x1
  #includeFunc  singleGraph_x2
  #includeFunc  singleGraph_x3
  #includeFunc  singleGraph_x4
  #includeFunc  singleGraph_x5
  #includeFunc  singleGraph_x6
  #includeFunc  singleGraph_x7
  #includeFunc  singleGraph_x8

    wallShearStress
    {{
        type            wallShearStress;
        libs            (fieldFunctionObjects);
        writeFields     yes;
        executeControl  writeTime;
        writeControl    writeTime;
    }}
}}
"""

TURB_FROZEN = """FoamFile
{
    version 2.0; format ascii; class dictionary; location "constant"; object turbulenceProperties;
}
// Frozen turbulence: the sampled Reynolds stress is PRESCRIBED (paper
// Appendix A step 3.1), so the k/omega transport equations must not run.
// `turbulence off` makes kOmegaSST::correct() return immediately, leaving
// k, omega and nut at their converged baseline values.
simulationType RAS;
RAS
{
    RASModel        kOmegaSST;
    turbulence      off;
    printCoeffs     off;
}
"""


# --------------------------------------------------------------------------
def make_case(name: str, R_sample: np.ndarray) -> Path:
    dst = ENS / name
    if dst.exists():
        shutil.rmtree(dst)
    (dst / "0").mkdir(parents=True)
    shutil.copytree(CASE / "constant", dst / "constant")
    shutil.copytree(CASE / "system", dst / "system")
    shutil.copy(CASE / "fieldDef", dst / "fieldDef")
    for f in ("U", "p", "k", "omega", "nut", "phi"):
        shutil.copy(CASE / BASELINE_TIME / f, dst / "0" / f)
    # The converged driving pressure gradient of meanVelocityForce lives in
    # <time>/uniform/momentumSourceProperties; without it every member restarts
    # from gradP = 0 and burns iterations re-finding it.
    # Copy ONLY that file.  The sibling <time>/uniform/time carries
    # `index 10000`, and copying it makes OpenFOAM resume its TIME INDEX at
    # 10000, so a `writeControl timeStep; writeInterval 4000` write lands at
    # index 12000 == Time 2000 instead of Time 4000.  (Found the hard way: the
    # first corner batch wrote a 2000/ directory and no 4000/.)
    src_msp = CASE / BASELINE_TIME / "uniform" / "momentumSourceProperties"
    if src_msp.is_file():
        (dst / "0" / "uniform").mkdir(exist_ok=True)
        shutil.copy(src_msp, dst / "0" / "uniform" / "momentumSourceProperties")
    (dst / "constant" / "turbulenceProperties").write_text(TURB_FROZEN)
    (dst / "system" / "controlDict").write_text(
        CONTROLDICT.format(end=END_TIME, wi=WRITE_INTERVAL))
    (dst / "system" / "fvOptions").write_text(FVOPTIONS.format(tag=""))
    rmt.write_symmtensor_field(dst / "constant" / "Rsample", R_sample,
                               obj="Rsample", loc="constant")
    return dst


def run_case(dst: Path, log_name="log.simpleFoam"):
    cmd = f"source {FOAM_BASHRC} && cd {dst} && simpleFoam > {log_name} 2>&1"
    return subprocess.Popen(["bash", "-lc", cmd])


# --------------------------------------------------------------------------
def load_baseline():
    R_bar = rmt.read_symmtensor_internal(R_PATH)
    Cx = fio.read_internal_field(str(CASE / "0" / "Cx"))
    Cy = fio.read_internal_field(str(CASE / "0" / "Cy"))
    return R_bar, np.column_stack([Cx, Cy])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--delta", type=float, default=0.2)
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--seed", type=int, default=20260730)
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--corners", action="store_true")
    ap.add_argument("--prefix", default=None)
    ap.add_argument("--build-only", action="store_true")
    ap.add_argument("--concurrency", type=int, default=6)
    args = ap.parse_args()

    ENS.mkdir(exist_ok=True)
    R_bar, xy = load_baseline()
    manifest = {"baseline_R": str(R_PATH), "n_cells": int(R_bar.shape[0])}

    cases = []
    if args.null:
        cases.append(("null", R_bar.copy()))
        manifest["kind"] = "null"

    elif args.corners:
        # Eigenspace (Emory/Iaccarino) corner states, for the head-to-head
        # comparison against the corner-union envelope.  Built from the SAME
        # baseline R_bar and injected through the SAME prescribe path, so the
        # only difference from the random-matrix members is the target tensor.
        k, _ = rmt.barycentric(R_bar)
        A = R_bar / (2.0 * np.maximum(k, 1e-30)[:, None, None]) - np.eye(3) / 3.0
        evals, evecs = np.linalg.eigh(A)          # ascending
        evecs = evecs[:, :, ::-1]                 # columns now descending order
        corner_lams = {
            "oneC":   np.array([2.0 / 3.0, -1.0 / 3.0, -1.0 / 3.0]),
            "twoC":   np.array([1.0 / 6.0, 1.0 / 6.0, -1.0 / 3.0]),
            "threeC": np.array([0.0, 0.0, 0.0]),
        }
        for cname, lam in corner_lams.items():
            Apert = np.einsum("nik,k,njk->nij", evecs, lam, evecs)
            Rc = 2.0 * k[:, None, None] * (np.eye(3) / 3.0 + Apert)
            cases.append((f"corner_{cname}", Rc))
        manifest["kind"] = "corners"
        manifest["corner_eigenvalues"] = {k_: v.tolist() for k_, v in corner_lams.items()}

    else:
        kl = rmt.build_kl_basis()  # paper Table 1: 50x30 KL mesh, N_KL=30, lx=2, ly=1
        P = rmt.build_interp_operator(kl, xy)
        L_R, audit = rmt.cholesky_upper_field(R_bar)
        s = rmt.RandomMatrixSampler(args.delta, kl, seed=args.seed)
        manifest.update({
            "kind": "rmt",
            "delta": args.delta,
            "n_samples": args.n,
            "seed": args.seed,
            "n_kl": int(kl.lam.size),
            "kl_mesh": [50, 30],
            "kl_variance_captured": kl.variance_captured,
            "lx": kl.lx, "ly": kl.ly,
            "n_p": s.n_p,
            "baseline_realizability_audit": audit,
        })
        prefix = args.prefix or f"d{args.delta:g}"
        for i in range(args.n):
            G = rmt.interp_G(P, s.sample_G_field())
            G = 0.5 * (G + np.transpose(G, (0, 2, 1)))
            R = rmt.assemble_R(L_R, G)
            assert np.isfinite(R).all()
            assert np.linalg.eigvalsh(R)[:, 0].min() >= -1e-12
            cases.append((f"{prefix}_s{i:03d}", R))

    built = []
    for name, R in cases:
        dst = make_case(name, R)
        built.append(name)
        print(f"built {dst}")
    manifest["cases"] = built
    (ENS / f"manifest_{manifest.get('kind','x')}"
          f"{'_'+args.prefix if args.prefix else ''}.json").write_text(
        json.dumps(manifest, indent=2, default=float))

    if args.build_only:
        return 0

    procs, queue = [], list(built)
    while queue or procs:
        while queue and len(procs) < args.concurrency:
            n = queue.pop(0)
            procs.append((n, run_case(ENS / n)))
            print(f"launched {n}")
        procs = [(n, p) for (n, p) in procs if p.poll() is None] or []
        if procs and not queue:
            for n, p in procs:
                p.wait()
                print(f"done {n}")
            procs = []
        elif procs:
            import time
            time.sleep(5)
    print("all launched/finished")
    return 0


if __name__ == "__main__":
    sys.exit(main())
