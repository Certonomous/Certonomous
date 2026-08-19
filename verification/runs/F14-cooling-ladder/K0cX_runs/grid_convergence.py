#!/usr/bin/env python3
"""
Observed order and grid-convergence band on the tall cavity's THREE-level ladder.

ZERO COMPUTE.  Every value is read from the committed gate_k0cx.json.  No case
directory is touched and no solve is run.  GRADES NOTHING: this reports whether
the solutions are in the asymptotic range, which is a precondition for reading a
deviation as model error, not a verdict about a model.

Why it exists: K0cX graded on the FINE mesh of a coarse/fine pair and reported
deviations against the experiment.  A deviation is only attributable to the
MODEL once the DISCRETISATION error is bounded, and that requires three levels
and an observed order.  Three levels exist for the hi-Ra rung and the order was
never computed.

VERIFICATION_CHARTER.md 3.2 records the two ways an observed order lies, so this
refuses to report an order at all where the sequence is oscillatory or
divergent, rather than printing a number that looks like convergence.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FS = 1.25          # Roache safety factor for a three-grid study


def main():
    g = json.load(open(os.path.join(HERE, "gate_k0cx.json")))
    m = g["measurements"]
    ref = g["reference_parsed"]
    bands = g["bands_parsed"]

    NU_REF, NU_BAND = ref["Nu"]["hi"], bands["Nu_pct"]["hi"]
    S_REF, S_BAND = ref["S"]["hi"], bands["S_hi"]

    print("GRID CONVERGENCE -- tall cavity, hi Ra, three levels")
    print("Zero compute.  Grades nothing.  Charter 3.2 governs when an order may be reported.")
    print("=" * 100)

    out = {"quantities": {}, "reference": {"Nu_avg": NU_REF, "S": S_REF},
           "bands": {"Nu_pct": NU_BAND, "S_abs": S_BAND}, "Fs": FS}

    for tag in ("SST", "KE", "LS"):
        cases = [f"X_hi_{l}_{tag}" for l in ("x", "f", "c")]   # 1=finest
        if not all(c in m for c in cases):
            continue
        N = [m[c]["cells"] for c in cases]
        r21 = math.sqrt(N[1] and N[0] / N[1])
        r32 = math.sqrt(N[1] / N[2])
        print(f"\n### {tag}   cells {N[2]} -> {N[1]} -> {N[0]}   r32={r32:.4f} r21={r21:.4f}")
        for qty, refv, band, unit in (("Nu_avg", NU_REF, NU_BAND, "%"),
                                      ("S", S_REF, S_BAND, "abs")):
            f1, f2, f3 = (m[c][qty] for c in cases)
            e21, e32 = f2 - f1, f3 - f2
            dev = [100.0 * (v - refv) / refv if unit == "%" else v - refv
                   for v in (f1, f2, f3)]
            inb = [abs(d) <= band for d in dev]
            rec = dict(quantity=qty, finest=f1, fine=f2, coarse=f3,
                       eps21=e21, eps32=e32,
                       deviation_finest=dev[0], deviation_fine=dev[1],
                       deviation_coarse=dev[2],
                       in_band_finest=inb[0], in_band_fine=inb[1],
                       in_band_coarse=inb[2])
            print(f"  {qty:7s} coarse {f3:11.6f} ({dev[2]:+7.3f}{'%' if unit=='%' else ''})"
                  f"  fine {f2:11.6f} ({dev[1]:+7.3f})"
                  f"  finest {f1:11.6f} ({dev[0]:+7.3f})")
            print(f"          band {band}{' %' if unit=='%' else ' abs'}   in band:"
                  f" coarse={'Y' if inb[2] else 'n'} fine={'Y' if inb[1] else 'n'}"
                  f" finest={'Y' if inb[0] else 'n'}")

            if e21 == 0.0:
                rec["state"] = "EXACT"; rec["order"] = None
                print("          state: the two finest meshes agree exactly")
            elif e32 / e21 < 0.0:
                rec["state"] = "OSCILLATORY"; rec["order"] = None
                print("          state: **OSCILLATORY** -- the correction changes SIGN between"
                      " levels.\n"
                      "                 No observed order is reported and no band is"
                      " extractable; the\n"
                      "                 sequence is not in the asymptotic range.")
            else:
                ratio = e32 / e21
                p = math.log(abs(ratio)) / math.log(r21)
                rec["order"] = p
                if p <= 0.0:
                    rec["state"] = "DIVERGENT"
                    print(f"          state: **DIVERGENT** -- observed order p = {p:.3f} <= 0."
                          " The correction\n"
                          "                 GROWS under refinement.  No band is extractable.")
                elif p < 0.5:
                    rec["state"] = "STAGNANT"
                    print(f"          state: **STAGNANT** -- observed order p = {p:.3f}."
                          " The solution is\n"
                          "                 barely responding to refinement; a Richardson"
                          " extrapolation here\n"
                          "                 would be dominated by a near-zero denominator and"
                          " is not taken.")
                else:
                    den = r21 ** p - 1.0
                    gci = FS * abs(e21 / f1) / den
                    fext = f1 + e21 / den
                    rec["state"] = "CONVERGING"
                    rec["GCI_finest_pct"] = 100.0 * gci
                    rec["richardson_extrapolate"] = fext
                    print(f"          state: CONVERGING -- observed order p = {p:.3f}")
                    print(f"                 GCI(finest) = {100.0*gci:.3f} %"
                          f"   Richardson extrapolate = {fext:.6f}")
            # A PRACTICAL BOUND WHERE A FORMAL ORDER IS UNAVAILABLE.
            # Roache's GCI needs monotone convergence.  Where the sequence is
            # oscillatory, stagnant or divergent, the spread across the three
            # levels is still a defensible bound on how much the DISCRETISATION
            # can be moving the answer -- it is what the meshes actually did.
            # It is NOT a GCI and is not labelled as one.
            vals = [f1, f2, f3]
            spread = max(vals) - min(vals)
            rec["spread_abs"] = spread
            rec["spread_pct_of_value"] = 100.0 * spread / abs(f1) if f1 else None
            if unit == "%":
                rec["spread_in_deviation_points"] = max(dev) - min(dev)
                ratio_txt = (f"{abs(dev[0]) / rec['spread_in_deviation_points']:.1f}x"
                             if rec["spread_in_deviation_points"] > 0 else "infinite")
                print(f"          mesh spread {spread:.6f} = {rec['spread_pct_of_value']:.3f} %"
                      f" of the value = {rec['spread_in_deviation_points']:.3f} deviation points;"
                      f"\n                 the deviation is {ratio_txt} the spread")
            else:
                rec["spread_in_deviation_points"] = max(dev) - min(dev)
                print(f"          mesh spread {spread:.6f} abs"
                      f" = {rec['spread_in_deviation_points']:.6f} in deviation")
            if unit == "%" and not (inb[0] == inb[1] == inb[2]):
                rec["band_straddled"] = True
                print("          **THE BAND IS STRADDLED**: this row's verdict depends on"
                      " which mesh is graded.")
            out["quantities"][f"{tag}/{qty}"] = rec

    with open(os.path.join(HERE, "grid_convergence.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)

    print("\n" + "-" * 100)
    states = {}
    for k, v in out["quantities"].items():
        states.setdefault(v["state"], []).append(k)
    for s in sorted(states):
        print(f"  {s:12s} {len(states[s])}: {', '.join(sorted(states[s]))}")
    n_ok = len(states.get("CONVERGING", []))
    print(f"\n  {n_ok} of {len(out['quantities'])} (model, quantity) pairs are in the"
          " asymptotic range.")
    print("  CANNOT SEE: whether a finer mesh would restore monotone behaviour; anything"
          " about the lo-Ra rung, which has two levels only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
