#!/usr/bin/env python3
"""
K0cG comparator -- the square cavity's three-level grid-convergence study.

WRITTEN AND COMMITTED BEFORE ANY CASE PRODUCED A RESULT.

Grades nothing.  It reports whether the square cavity's solutions are in the
asymptotic range, which is the precondition for reading K0cS's deviations as
model error.  No K0cS verdict can move and none is recomputed here.

Design rules carried from K0cQ, K0cR and K0cP:
  * the third level is measured by analyse_k0cs.measure, the SAME function that
    produced levels one and two;
  * no K0cS case directory is written to -- the coarse and fine values are read
    from the committed gate_k0cs.json;
  * references and bands are parsed from that JSON, not typed here.

The convergence classification is the one D428 shipped for the tall cavity, so
the two geometries are judged by identical rules.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LADDER = os.path.dirname(HERE)
K0CS = os.path.join(LADDER, "K0cS_runs")
sys.path.insert(0, K0CS)
import analyse_k0cs as SQ          # noqa: E402

FS = 1.25
ARMS = {"S_SST_x": dict(model="kOmegaSST", coarse="S_SST_c", fine="S_SST_f"),
        "S_KE_x":  dict(model="kEpsilon",  coarse="S_KE_c",  fine="S_KE_f")}
QUANTITIES = ("Nu_hot", "Nu_cold", "Sp", "Vpeak", "uv_peak")
CONTROL = "C1_laminar"


def refuse(msg):
    print(msg)
    sys.exit(2)


def main():
    missing = [c for c in ARMS if not os.path.isfile(os.path.join(HERE, f"DONE.{c}"))]
    if missing:
        refuse("REFUSE: no completion marker for " + ", ".join(sorted(missing)))

    g = json.load(open(os.path.join(K0CS, "gate_k0cs.json")))
    spec = {}
    for r in g["graded_rows"]:
        spec[r["quantity"]] = dict(reference=r["reference"], band=r["band"],
                                   kind=r.get("kind"))
    base = g["cases"]
    ctl = base[CONTROL]["measure"]

    out = {"quantities": {}, "cases": {}, "Fs": FS,
           "classification_source": "D428 / K0cX_runs/grid_convergence.py"}

    def dev(v, s):
        return 100.0 * (v - s["reference"]) / s["reference"] if s["kind"] == "REL" \
            else v - s["reference"]

    for arm, a in sorted(ARMS.items()):
        m3 = SQ.measure(os.path.join(HERE, arm), arm)      # finest
        m2 = base[a["fine"]]["measure"]
        m1 = base[a["coarse"]]["measure"]
        n3 = m3.get("cells") or 94249
        out["cases"][arm] = dict(measure=m3, model=a["model"],
                                 fine=a["fine"], coarse=a["coarse"])
        # h ~ 1/sqrt(N) in 2D; the ladder was built at a nominal ratio of 1.6
        r21 = 1.6
        print(f"\n### {a['model']}   {a['coarse']} -> {a['fine']} -> {arm}   nominal r = {r21}")
        for q in QUANTITIES:
            if q not in spec or q not in m3 or q not in m2 or q not in m1:
                continue
            s = spec[q]
            f1, f2, f3 = m3[q], m2[q], m1[q]      # 1 = finest
            d = [dev(v, s) for v in (f1, f2, f3)]
            inb = [abs(x) <= s["band"] for x in d]
            e21, e32 = f2 - f1, f3 - f2
            rec = dict(quantity=q, model=a["model"], band=s["band"],
                       reference=s["reference"], kind=s["kind"],
                       coarse=f3, fine=f2, finest=f1,
                       deviation_coarse=d[2], deviation_fine=d[1],
                       deviation_finest=d[0],
                       in_band=dict(coarse=inb[2], fine=inb[1], finest=inb[0]),
                       eps21=e21, eps32=e32)
            spread = max(f1, f2, f3) - min(f1, f2, f3)
            rec["spread_abs"] = spread
            rec["spread_in_deviation_points"] = max(d) - min(d)
            if e21 == 0.0:
                rec["state"] = "EXACT"
            elif e32 / e21 < 0.0:
                rec["state"] = "OSCILLATORY"
            else:
                p = math.log(abs(e32 / e21)) / math.log(r21)
                rec["order"] = p
                if p <= 0.0:
                    rec["state"] = "DIVERGENT"
                elif p < 0.5:
                    rec["state"] = "STAGNANT"
                else:
                    den = r21 ** p - 1.0
                    rec["state"] = "CONVERGING"
                    rec["GCI_finest_pct"] = 100.0 * FS * abs(e21 / f1) / den
                    rec["richardson_extrapolate"] = f1 + e21 / den
            if not (inb[0] == inb[1] == inb[2]):
                rec["band_straddled"] = True
            if q in ctl:
                rec["deviation_control"] = dev(ctl[q], s)
                rec["in_band_control"] = abs(rec["deviation_control"]) <= s["band"]
            out["quantities"][f"{a['model']}/{q}"] = rec

            unit = "%" if s["kind"] == "REL" else ""
            print(f"  {q:9s} coarse {f3:11.5g} ({d[2]:+8.3f}{unit})  fine {f2:11.5g} "
                  f"({d[1]:+8.3f})  finest {f1:11.5g} ({d[0]:+8.3f})")
            extra = ""
            if rec["state"] == "CONVERGING":
                extra = (f"  p={rec['order']:.3f}  GCI={rec['GCI_finest_pct']:.3f} %"
                         f"  extrap={rec['richardson_extrapolate']:.6g}")
            elif "order" in rec:
                extra = f"  p={rec['order']:.3f}"
            ratio = (abs(d[0]) / rec["spread_in_deviation_points"]
                     if rec["spread_in_deviation_points"] > 0 else float("inf"))
            print(f"            state {rec['state']}{extra}")
            print(f"            spread {rec['spread_in_deviation_points']:.3f} deviation pts;"
                  f" deviation is {ratio:.1f}x the spread"
                  + ("   **BAND STRADDLED**" if rec.get("band_straddled") else ""))

    with open(os.path.join(HERE, "gate_k0cg.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)

    states = {}
    for k, v in out["quantities"].items():
        states.setdefault(v["state"], []).append(k)
    print("\n" + "-" * 100)
    for s in sorted(states):
        print(f"  {s:12s} {len(states[s])}: {', '.join(sorted(states[s]))}")
    print(f"\n  {len(states.get('CONVERGING', []))} of {len(out['quantities'])}"
          " (model, quantity) pairs are in the asymptotic range.")
    print("  GRADES NOTHING.  No K0cS verdict moves.")
    print("  CANNOT SEE: the lo-Ra question, LaunderSharmaKE (K0cS REFUSED it), or"
          " whether a fourth level would restore monotone behaviour.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
