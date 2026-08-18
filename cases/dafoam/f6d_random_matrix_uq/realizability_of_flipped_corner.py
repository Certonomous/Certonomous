"""
F6d -- measure the consequence of the inverted source-term sign in

    demo-output/website/dafoam/f6a_epistemic_band/*/system/fvOptions
    (18 dictionaries, all `eqn += fvc::div(deltaR)`, deltaR = 2k(bPert - bB))

Established by signcheck/ (four controlled runs) and by the OpenFOAM v2606
sources, an fvOption `eqn += X` places +X on the RHS of the momentum equation,
so the EFFECTIVE deviatoric Reynolds stress carried by the momentum equation is

        R_eff = R_model - deltaR

Substituting deltaR = 2k(b_pert - b_B) and R_model_dev = 2k b_B gives

        b_eff = 2 b_B - b_pert        instead of the intended  b_pert

i.e. the perturbation is applied with the opposite sign: b_eff - b_B
= -(b_pert - b_B).

The question this script answers, as a measurement rather than an inference:
IS b_eff STILL A REALIZABLE ANISOTROPY TENSOR?  A realizable b has all three
barycentric coordinates in [0,1] (equivalently, all three eigenvalues of
R = 2k(I/3 + b) non-negative).  If it is not, the momentum equation is being
fed a Reynolds stress that no velocity field can have, which is the standard
explanation for the kind of violent, limiter-dominated non-convergence F6a
recorded for its 1C and 2C corners.

Run on both meshes this project has a converged kOmegaSST baseline for:
  * the F6b periodic hill      (this study's case)
  * the F6a NASA wall-mounted hump (F6a's own case -- so the claim about F6a
    is evidenced on F6a's own data, not transplanted from another geometry)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rmt_sampler as rmt  # noqa: E402

FOAM = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

CASES = {
    "F6b_periodic_hill": (
        HERE.parent / "f6b_periodic_hills" / "case_breuer_re10595", "10000"),
    "F6a_nasa_hump": (
        HERE.parent / "f6a_epistemic_band" / "r4_band_tightening_hump" / "oneC_delta0.00",
        "1795"),
}

CORNERS = {
    "oneC":   np.array([2.0 / 3.0, -1.0 / 3.0, -1.0 / 3.0]),
    "twoC":   np.array([1.0 / 6.0, 1.0 / 6.0, -1.0 / 3.0]),
    "threeC": np.array([0.0, 0.0, 0.0]),
}


def ensure_R(case: Path, time: str):
    f = case / time / "turbulenceProperties:R"
    if not f.exists():
        cmd = (f"source {FOAM} && cd {case} && simpleFoam -postProcess "
               f"-func 'turbulenceFields(R)' -time {time} -noFunctionObjects "
               f"> /tmp/ppR_{case.name}.log 2>&1")
        subprocess.run(["bash", "-lc", cmd], check=True)
    return f


def bary_from_b(b):
    ev = np.linalg.eigvalsh(b)[:, ::-1]  # descending
    C1 = ev[:, 0] - ev[:, 1]
    C2 = 2.0 * (ev[:, 1] - ev[:, 2])
    C3 = 3.0 * ev[:, 2] + 1.0
    return np.column_stack([C1, C2, C3])


def main():
    out = {}
    for label, (case, time) in CASES.items():
        if not case.exists():
            out[label] = {"error": f"case dir not found: {case}"}
            continue
        Rf = ensure_R(case, time)
        R = rmt.read_symmtensor_internal(Rf)
        k = 0.5 * np.trace(R, axis1=1, axis2=2)
        kk = np.maximum(k, 1e-30)
        bB = R / (2.0 * kk[:, None, None]) - np.eye(3) / 3.0

        # cells with meaningful turbulence, matching the fvOptions' own guard
        # `if (k[celli] < kMinCell) continue;` with kMinCell = 1e-8
        live = k >= 1e-8
        entry = {"source_field": str(Rf), "n_cells": int(R.shape[0]),
                 "n_cells_k_ge_1e-8": int(live.sum())}

        evals, evecs = np.linalg.eigh(bB)
        evecs_desc = evecs[:, :, ::-1]

        Cb = bary_from_b(bB)
        entry["baseline_bary_min_coord"] = float(Cb[live].min())

        for cname, lam in CORNERS.items():
            bP = np.einsum("nik,k,njk->nij", evecs_desc, lam, evecs_desc)
            b_intended = bP
            b_actual = 2.0 * bB - bP           # what `eqn +=` really imposes

            res = {}
            for tag, b in (("intended", b_intended), ("actual_with_plus_sign", b_actual)):
                C = bary_from_b(b)
                bad = (C < -1e-12).any(axis=1) | (C > 1.0 + 1e-12).any(axis=1)
                # equivalent test on the tensor itself
                Rr = 2.0 * kk[:, None, None] * (np.eye(3) / 3.0 + b)
                negeig = (np.linalg.eigvalsh(Rr)[:, 0] < -1e-14)
                res[tag] = {
                    "frac_cells_nonrealizable_barycentric":
                        float(bad[live].mean()),
                    "frac_cells_R_has_negative_eigenvalue":
                        float(negeig[live].mean()),
                    "worst_barycentric_coordinate": float(C[live].min()),
                }
            entry[cname] = res
        out[label] = entry

    print(json.dumps(out, indent=2))
    (HERE / "realizability_of_flipped_corner.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
