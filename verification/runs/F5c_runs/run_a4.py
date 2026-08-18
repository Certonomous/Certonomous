#!/usr/bin/env python3
"""F5c A4 -- the isolating leg (pre-registration F5C_LEVER_ISOLATION_PREREGISTRATION.md, 9eaefc7f).

A4: coarse, plain SIMPLE (consistent no), relax p 0.3 / U 0.6, 2000 it.
Completes the 2x2 factorial: A1 vs A4 isolates `consistent`; A4 vs A3
isolates relaxation. Bar M4: an effect is ATTRIBUTABLE only if |dx_r|
exceeds the LARGER of the two contributing runs' own second-half x_r spread.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_stage_a as sa

A1_SPREAD, A3_SPREAD = 6.559889154920512, 2.578046981162763
A1_XR, A3_XR = 5.563518924973768, 6.876362063906673
A1_HASH = "2569808326111612f20a6ab9aeb0ebc345277200dbbd2f1221a08556e59101c9"
A3_HASH = "94150fe67f56a6e56e1c28244eb345ebc2a659f94960e07fd4ba8c51e5625dcd"

LEG = {"name": "A4", "level": "coarse", "iterations": 2000, "sample_every": 50,
       "consistent": False, "relax_p": 0.3, "relax_u": 0.6,
       "basis_s": 126.6, "basis": "Stage A leg A3, identical mesh/iterations/"
                                  "sampling and same `consistent no`"}

def main() -> int:
    sa.log("F5c A4 isolating leg starting (prereg 9eaefc7f)")
    try:
        rec = sa.run_leg(LEG)
    except Exception as exc:                      # O-I4: pre-registered outcome
        sa.log(f"A4 DID NOT RUN: {type(exc).__name__}: {exc}")
        (sa.HERE / "a4_record.json").write_text(json.dumps(
            {"outcome": "O-I4", "reading": "plain SIMPLE at SIMPLEC's relaxation "
             "(p 0.3 / U 0.6) did not complete; the factorial corner is "
             "unreachable and the two recorded configurations are not separable "
             "by this route. Pre-registered outcome, not a failed run.",
             "error": f"{type(exc).__name__}: {exc}"}, indent=2) + "\n")
        return 0

    hist = [(t, v) for t, v in (rec.get("x_r_over_h_history") or []) if v is not None]
    half = [v for _, v in hist[len(hist)//2:]]
    a4_spread = (max(half) - min(half)) if half else None
    xr = rec.get("x_r_over_h")
    h = rec.get("fvSolution_sha256")

    hashes_ok = bool(h) and h != A1_HASH and h != A3_HASH
    out = {"prereg": "campaign/F5C_LEVER_ISOLATION_PREREGISTRATION.md",
           "prereg_commit": "9eaefc7f", "timestamp": sa.now(),
           "a4": {k: v for k, v in rec.items()
                  if k not in ("wall_shear_profile", "pressure_profile",
                               "x_r_over_h_history")},
           "a4_second_half_spread": a4_spread,
           "hash_precondition_met": hashes_ok}
    if not hashes_ok:
        out["scored"] = {"branch": "VOID", "reading":
            "A4's fvSolution hash matches A1's or A3's (or is absent): the run "
            "did not do what it was asked and nothing is scored."}
    else:
        contrasts = {}
        for label, other_xr, other_spread, isolates in (
                ("algorithm_A1_vs_A4", A1_XR, A1_SPREAD, "`consistent` alone"),
                ("relaxation_A4_vs_A3", A3_XR, A3_SPREAD, "relaxation alone")):
            d = abs(xr - other_xr)
            bar = max(other_spread, a4_spread or 0.0)
            contrasts[label] = {"delta_x_r": d, "bar": bar, "isolates": isolates,
                                "attributable": d > bar}
        alg = contrasts["algorithm_A1_vs_A4"]["attributable"]
        rel = contrasts["relaxation_A4_vs_A3"]["attributable"]
        branch = ("O-I1" if alg else "O-I2" if rel else "O-I3")
        reading = {
         "O-I1": "algorithm ATTRIBUTABLE: SIMPLE and SIMPLEC differ by more than "
                 "either run's internal wander at fixed relaxation; the record's "
                 "claim is vindicated and isolated for the first time",
         "O-I2": "relaxation attributable, algorithm not: the 1.313 H Stage A saw "
                 "was RELAXATION, not SIMPLEC -- the record's attribution is "
                 "misattributed, not merely unproven",
         "O-I3": "NEITHER lever is resolvable at 2000 iterations on coarse, "
                 "because each configuration's own iteration wander exceeds every "
                 "difference between configurations; the record's 'SIMPLEC moved "
                 "the number substantially' is WITHDRAWN as unsupported"}[branch]
        out["scored"] = {"branch": branch, "reading": reading,
                         "contrasts": contrasts, "x_r_A4": xr,
                         "x_r_A1": A1_XR, "x_r_A3": A3_XR}
        sa.log(f"M4 {branch}: x_r(A4)={xr:.4f} spread={a4_spread:.4f} | "
               f"alg d={contrasts['algorithm_A1_vs_A4']['delta_x_r']:.4f} vs bar "
               f"{contrasts['algorithm_A1_vs_A4']['bar']:.4f} | rel d="
               f"{contrasts['relaxation_A4_vs_A3']['delta_x_r']:.4f} vs bar "
               f"{contrasts['relaxation_A4_vs_A3']['bar']:.4f}")
    (sa.HERE / "a4_record.json").write_text(
        json.dumps(out, indent=2, sort_keys=True, default=str) + "\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
