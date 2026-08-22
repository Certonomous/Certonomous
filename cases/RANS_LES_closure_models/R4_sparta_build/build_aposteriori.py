#!/usr/bin/env python3
"""R4 step 4 - build the a-posteriori propagation cases (PREREGISTRATION sec. 6).

Three configurations per case, all restarted from the SHIPPED baseline field
and all sharing one solver, one stopping rule and one set of schemes, so the
only difference between them is the correction:

  NULL       `kOmegaSSTSparta` with EMPTY RTerms and bDeltaTerms.  Zero
             correction through the identical code path -- the comparator
             PREREGISTRATION sec. 6 names, not stock kOmegaSST.
  CEILING    `kOmegaSSTCorrected` reading the frozen extraction's own
             `bijDelta` and `kDeficit` as STATIC fields.  This is the
             per-case frozen-field ceiling, measured in this lane rather
             than quoted (sec. 6), and the NOT A RESULT branch fires if it
             fails to beat NULL by 30%.
  DISCOVERED `kOmegaSSTSparta` with the FS4-frozen symbolic term sets,
             re-evaluated from the current solution every iteration.

L-221 is applied at the one call site that writes `libs`: r4_lib.set_libs
inserts-or-replaces and then asserts.  These cases matter for it in both
directions -- the 21 hills carry no libs line at all and the ducts, CBFS and
PHLL10595 carry one naming a library that does not exist on this machine.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r4_lib as R

OUT = os.path.join(R.WORK, "aposteriori")
FROZEN = os.path.join(R.WORK, "frozen")
CAPS = {"hills": 20000, "ducts": 20000, "PHLL10595": 10000, "CBFS13700": 30000}
CHECKPOINT = {"hills": 2500, "ducts": 2500, "PHLL10595": 2500,
              "CBFS13700": 5000}


def terms_str(terms):
    """[(n,p,q,c)] -> the OpenFOAM list literal kOmegaSSTSparta reads."""
    if not terms:
        return "( )"
    return "( " + " ".join(f"({n} {p} {q} {c:.12g})" for n, p, q, c in terms) \
        + " )"


def set_residual_control(fv_solution, tol=1e-6):
    s = open(fv_solution).read()
    new = ("    residualControl\n    {\n"
           f'        "(U|Ux|Uy|Uz)"  {tol};\n'
           f"        p               {tol};\n"
           f"        k               {tol};\n"
           f"        omega           {tol};\n    }}")
    if "residualControl" in s:
        s = re.sub(r"\n\s*residualControl\s*\{[^{}]*\}", "\n" + new, s, count=1)
    else:
        s = re.sub(r"(SIMPLE\s*\{)", r"\1\n" + new, s, count=1)
    open(fv_solution, "w").write(s)


def build(case, src, family, cfg, rterms, bterms):
    dst = os.path.join(OUT, case, cfg)
    R.copy_skeleton(src, dst)                     # keeps system/fvOptions
    t = R.latest_time(src)
    for f in ("U", "p", "k", "omega", "nut", "phi"):
        p = os.path.join(src, t, f)
        if os.path.exists(p):
            R.retag(p, os.path.join(dst, "0", f), f)
    if cfg == "ceiling":
        fz = os.path.join(FROZEN, case)
        ft = R.latest_time(fz)
        for f in ("bijDelta", "kDeficit"):
            R.retag(os.path.join(fz, ft, f), os.path.join(dst, "0", f), f)
        R.write_turbulence_properties(
            dst, "kOmegaSSTCorrected",
            extra="\n    kOmegaSSTCorrectedCoeffs\n    {\n"
                  "        RScale          1;\n        bScale          1;\n"
                  "    }\n")
    else:
        R.write_turbulence_properties(
            dst, "kOmegaSSTSparta",
            extra="\n    kOmegaSSTSpartaCoeffs\n    {\n"
                  f"        RTerms          {terms_str(rterms)};\n"
                  f"        bDeltaTerms     {terms_str(bterms)};\n"
                  "        writeInitialCorrections true;\n    }\n")
    R.write_control_dict(os.path.join(dst, "system", "controlDict"),
                         end_time=CAPS[family],
                         write_interval=CHECKPOINT[family])
    set_residual_control(os.path.join(dst, "system", "fvSolution"))
    return dict(case=case, cfg=cfg, family=family, dir=dst,
                baseline_time=t, cap=CAPS[family],
                checkpoint=CHECKPOINT[family],
                RTerms=terms_str(rterms), bDeltaTerms=terms_str(bterms))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--model", default="", help="MODEL.json from FS4")
    ap.add_argument("--configs", default="null,ceiling,discovered")
    a = ap.parse_args()
    cases = a.cases.split(",")
    R.assert_no_test_case(cases)
    want = a.configs.split(",")
    model, rterms, bterms = None, [], []
    if "discovered" in want:
        model = json.load(open(a.model))
        rterms = [tuple(t) for t in model["R"]["terms"]]
        bterms = [tuple(t) for t in model["bDelta"]["terms"]]
        assert all(int(t[0]) in (1, 2, 3) for t in rterms + bterms), (
            "PREREGISTRATION sec. 1: no term is ever registered with n = 4 - "
            "kOmegaSSTSparta would silently evaluate it as T3")
    byname = {c: (p, f) for c, p, f in R.training_cases()}
    os.makedirs(OUT, exist_ok=True)
    rec = []
    for case in cases:
        src, family = byname[case]
        for cfg, rt, bt in (("null", [], []), ("ceiling", None, None),
                            ("discovered", rterms, bterms)):
            if cfg not in want:
                continue
            rec.append(build(case, src, family, cfg, rt or [], bt or []))
            print(f"[built] {case:22s} {cfg:11s} cap={rec[-1]['cap']}",
                  flush=True)
    mf = os.path.join(OUT, "build_manifest.json")
    old = json.load(open(mf))["cases"] if os.path.exists(mf) else []
    keep = [r for r in old
            if (r["case"], r["cfg"]) not in {(x["case"], x["cfg"]) for x in rec}]
    json.dump(dict(model=model, cases=keep + rec), open(mf, "w"), indent=1)
    print(f"\n{len(rec)} propagation cases -> {OUT}")


if __name__ == "__main__":
    main()
