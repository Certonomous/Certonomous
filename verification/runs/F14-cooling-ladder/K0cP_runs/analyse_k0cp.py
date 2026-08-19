#!/usr/bin/env python3
"""
K0cP comparator -- is the defect the VALUE of Prt or the FORM of the closure?

WRITTEN AND COMMITTED BEFORE ANY CASE PRODUCED A RESULT.  The outcome table
below is transcribed from K0cP_PREREGISTRATION.md section 3.1.

Same two design rules as K0cQ and K0cR: each arm is measured by the instrument
that produced its baseline (analyse_k0cs.measure), and NO baseline case
directory is written to -- baseline and laminar-control values are read from the
committed gate_k0cs.json.

References and bands are PARSED from that JSON, not typed here.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LADDER = os.path.dirname(HERE)
K0CS = os.path.join(LADDER, "K0cS_runs")
sys.path.insert(0, K0CS)
import analyse_k0cs as SQ          # noqa: E402

CASES = {
    "P021_sq_c": dict(baseline="S_KE_c", prt=0.21),
    "P021_sq_f": dict(baseline="S_KE_f", prt=0.21),
    "P102_sq_c": dict(baseline="S_KE_c", prt=1.02),
    "P102_sq_f": dict(baseline="S_KE_f", prt=1.02),
}
CONTROL = "C1_laminar"
DECIDING_ROW = "Nu_hot"
BASE_PRT = 0.85


def refuse(msg):
    print(msg)
    sys.exit(2)


def spec_and_cases():
    g = json.load(open(os.path.join(K0CS, "gate_k0cs.json")))
    spec = {}
    for r in g["graded_rows"]:
        spec[r["quantity"]] = dict(reference=r["reference"], band=r["band"],
                                   kind=r.get("kind"))
    return spec, g["cases"]


def deviation(value, s):
    if s["kind"] == "REL":
        return 100.0 * (value - s["reference"]) / s["reference"]
    return value - s["reference"]


def main():
    missing = [c for c in CASES if not os.path.isfile(os.path.join(HERE, f"DONE.{c}"))]
    if missing:
        refuse("REFUSE: no completion marker for " + ", ".join(sorted(missing)))

    spec, base_cases = spec_and_cases()
    ctl = base_cases[CONTROL]["measure"]
    out = {"cases": {}, "rows": {},
           "decision_rule": dict(source="K0cP_PREREGISTRATION.md Section 3.1",
                                 deciding_row=DECIDING_ROW, base_Prt=BASE_PRT)}

    for name, c in sorted(CASES.items()):
        arm = SQ.measure(os.path.join(HERE, name), name)
        base = base_cases[c["baseline"]]["measure"]
        out["cases"][name] = dict(measure=arm, baseline=c["baseline"], Prt=c["prt"])
        rows = {}
        for q, s in spec.items():
            if q not in arm or q not in base:
                continue
            d_a, d_b = deviation(arm[q], s), deviation(base[q], s)
            row = dict(quantity=q, reference=s["reference"], band=s["band"],
                       kind=s["kind"], value_arm=arm[q], value_baseline=base[q],
                       deviation_arm=d_a, deviation_baseline=d_b,
                       in_band_arm=abs(d_a) <= s["band"],
                       in_band_baseline=abs(d_b) <= s["band"],
                       improvement_points=abs(d_b) - abs(d_a))
            if q in ctl:
                d_c = deviation(ctl[q], s)
                row["deviation_control"] = d_c
                row["in_band_control"] = abs(d_c) <= s["band"]
                row["pass_carries_evidence"] = bool(
                    row["in_band_arm"] and not row["in_band_control"])
            rows[q] = row
        out["rows"][name] = rows

    # ---- the registered outcome table --------------------------------------
    def nu(name):
        return out["rows"][name][DECIDING_ROW]

    lo = [nu("P021_sq_c"), nu("P021_sq_f")]     # Prt 0.21, alphat x4.05
    hi = [nu("P102_sq_c"), nu("P102_sq_f")]     # Prt 1.02, alphat x0.83

    lo_worse = all(r["improvement_points"] < 0 for r in lo)
    lo_better = all(r["improvement_points"] > 0 for r in lo)
    hi_in_band = all(r["in_band_arm"] for r in hi)
    lo_in_band = all(r["in_band_arm"] for r in lo)

    if lo_in_band or hi_in_band:
        verdict = "VALUE"
        why = ("a constant Prt brought Nu_hot inside the 10 % band on both "
               "meshes: the defect is the VALUE, and a constant closure can be "
               "right if it is the right constant")
    elif lo_better:
        verdict = "REFUTED"
        why = ("Prt = 0.21 quadrupled alpha_t and made the over-prediction "
               "BETTER: the mechanism registered in section 3 is wrong and "
               "D424's transmission argument is withdrawn with it")
    elif lo_worse and not hi_in_band:
        verdict = "FORM"
        why = ("the measured WALL value made it worse and the measured OUTER "
               "value did not reach band: no single constant can be right on a "
               "field that runs 0.00 to 1.02 across the layer, so the defect is "
               "the FORM of the closure and X4 arm (b) is the experiment")
    else:
        verdict = "MIXED"
        why = "the two meshes of an arm disagree; see the per-row table"

    out["verdict"], out["verdict_because"] = verdict, why
    with open(os.path.join(HERE, "gate_k0cp.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)

    print("K0cP -- is the defect the VALUE of Prt or the FORM of the closure?")
    print("=" * 104)
    print("  baseline kEpsilon at Prt = %.2f; alpha_t scales as 0.85/Prt" % BASE_PRT)
    print("  %-11s %5s %9s %11s %11s %8s %8s  %s" %
          ("case", "Prt", "a_t scale", "Nu base", "Nu arm", "dev arm", "improv", "in band (arm/base/lam)"))
    for name, c in sorted(CASES.items()):
        r = nu(name)
        print("  %-11s %5.2f %9.3f %11.4f %11.4f %8.3f %8.2f  %s/%s/%s%s" %
              (name, c["prt"], BASE_PRT / c["prt"],
               r["value_baseline"], r["value_arm"], r["deviation_arm"],
               r["improvement_points"],
               "Y" if r["in_band_arm"] else "n",
               "Y" if r["in_band_baseline"] else "n",
               "Y" if r.get("in_band_control") else "n",
               "   <- hollow pass, 2c" if (r["in_band_arm"] and r.get("in_band_control")) else ""))
    print("-" * 104)
    print("  VERDICT: %s" % verdict)
    print("  BECAUSE: %s" % why)
    return 0


if __name__ == "__main__":
    sys.exit(main())
