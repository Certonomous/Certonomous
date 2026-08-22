#!/usr/bin/env python3
"""R4 step 1 - build the 27 k-corrective-frozen-RANS extraction cases.

PREREGISTRATION sec. 5: targets come from `kOmegaSSTFrozen` (the W2-validated
path), run on TRAINING FLOWS ONLY, producing `bijDelta` and `kDeficit`.

The benchmark clone is READ-ONLY; every case is copied out to
/home/ubuntu/closure-data/r4/frozen/<case>.  Layout is byte-compatible with
verification/runs/W2_sparta_runs/ph_frozen, which is the validated reference:
  0/U      <- benchmark 0/U_LES        (high-fidelity mean velocity)
  0/k      <- benchmark 0/k_LES        (high-fidelity turbulent KE)
  0/tauij  <- benchmark 0/tauij_LES    (high-fidelity Reynolds stress)
  0/omega  <- benchmark <latest>/omega (baseline k-omega SST initial condition)
  0/nut    <- benchmark <latest>/nut   (        "                            )
Only the FoamFile `object` line is rewritten; every value and boundary
condition is the benchmark's own.

Nothing is fitted here and no test or validation case is touched (asserted).
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r4_lib as R

OUT = os.path.join(R.WORK, "frozen")
BACKSTOP = 5000          # controlDict cap; the settle criterion is in the solver


def build(case, src, family):
    dst = os.path.join(OUT, case)
    R.copy_skeleton(src, dst)
    t = R.latest_time(src)
    for obj, rel in (("omega", f"{t}/omega"), ("nut", f"{t}/nut")):
        R.retag(os.path.join(src, rel), os.path.join(dst, "0", obj), obj)
    # CBFS13700 ships its LES fields as #include-d value lists under
    # 0/interpolatedFields; the directory travels with the case.
    inc = os.path.join(src, "0", "interpolatedFields")
    if os.path.isdir(inc):
        import shutil as _sh
        _sh.copytree(inc, os.path.join(dst, "0", "interpolatedFields"))
    headerless = open(os.path.join(src, "0", "U_LES")).read(1).strip() != "/"
    if not headerless:
        # hills / PHLL10595 / CBFS13700: the *_LES files are complete
        # OpenFOAM fields, boundary values included.  Only the object name
        # is rewritten; every value and BC is the benchmark's own.
        for obj, rel in (("U", "0/U_LES"), ("k", "0/k_LES"),
                         ("tauij", "0/tauij_LES")):
            R.retag(os.path.join(src, rel), os.path.join(dst, "0", obj), obj)
        les_mode = "retag"
    else:
        # DUCT family: *_LES are bare value lists.  U and k are spliced into
        # the benchmark's own 0/U and 0/k so the BCs stay the benchmark's;
        # tauij has no shipped field file and is built with constraint patches
        # matched and zeroGradient elsewhere (see r4_lib.write_field_from_les).
        R.splice_internal(os.path.join(src, "0", "U"),
                          os.path.join(src, "0", "U_LES"),
                          os.path.join(dst, "0", "U"), "U")
        R.splice_internal(os.path.join(src, "0", "k"),
                          os.path.join(src, "0", "k_LES"),
                          os.path.join(dst, "0", "k"), "k")
        R.write_field_from_les(os.path.join(src, "0", "tauij_LES"),
                               os.path.join(dst, "0", "tauij"), "tauij",
                               "volSymmTensorField", "[0 2 -2 0 0 0 0]",
                               R.patch_types(dst))
        les_mode = "splice"
    R.write_turbulence_properties(dst, "kOmegaSSTFrozen")
    # L-221 applies even though kCorrectiveFrozenFoam links the library
    # directly: the entry is inserted-or-replaced and asserted, so a case that
    # is later reused by a *solver* run cannot inherit the absent
    # libfrozenIncompressibleTurbulenceModels.so the benchmark ships.
    R.write_control_dict(os.path.join(dst, "system", "controlDict"),
                         end_time=BACKSTOP, write_interval=BACKSTOP)
    n = len(open(os.path.join(dst, "constant", "polyMesh", "owner")).read())
    return {"case": case, "family": family, "src": src,
            "baseline_time": t, "dir": dst, "backstop": BACKSTOP,
            "les_mode": les_mode, "owner_bytes": n}


def main():
    cases = R.training_cases()
    R.assert_no_test_case([c for c, _, _ in cases])
    os.makedirs(OUT, exist_ok=True)
    rec = []
    for case, src, family in cases:
        rec.append(build(case, src, family))
        print(f"[built] {case:22s} {family:10s} baseline_t={rec[-1]['baseline_time']}",
              flush=True)
    json.dump({"n_cases": len(rec), "out": OUT, "cases": rec},
              open(os.path.join(OUT, "build_manifest.json"), "w"), indent=1)
    print(f"\n{len(rec)} frozen cases -> {OUT}")


if __name__ == "__main__":
    main()
