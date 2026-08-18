#!/usr/bin/env python3
"""
K0cR (X3) comparator -- Reynolds-stress transport on both cavities.

WRITTEN AND COMMITTED BEFORE ANY CASE PRODUCED A RESULT.  The decision rule
below is transcribed from K0cR_PREREGISTRATION.md section 5, not chosen here.

Design rules carried from K0cQ, both of them reactions to recorded defects:
 1. each SSG arm is measured by its own geometry's instrument, the same
    function that produced its kEpsilon baseline;
 2. no baseline case directory is written to -- baseline and laminar-control
    values are read from the committed gate JSONs, because both measure()
    functions run a postProcess call that writes into the case.

REFERENCES AND BANDS ARE PARSED FROM THE COMMITTED GATE JSONS, NOT TYPED HERE.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LADDER = os.path.dirname(HERE)
K0CS = os.path.join(LADDER, "K0cS_runs")
K0CX = os.path.join(LADDER, "K0cX_runs")
sys.path.insert(0, K0CS)
sys.path.insert(0, K0CX)
import analyse_k0cs as SQ          # noqa: E402
import analyse_k0cx as TL          # noqa: E402

MATERIAL_PTS = 3.0                 # "improves materially", section 5

CASES = {
    "R_sq_c": dict(geom="sq", baseline="S_KE_c",    control="C1_laminar"),
    "R_sq_f": dict(geom="sq", baseline="S_KE_f",    control="C1_laminar"),
    "R_tl_c": dict(geom="tl", baseline="X_hi_c_KE", control="X_hi_c_LAM"),
    "R_tl_f": dict(geom="tl", baseline="X_hi_f_KE", control="X_hi_f_LAM"),
}


def refuse(msg):
    print(msg)
    sys.exit(2)


def latest_time(case):
    ts = [(float(d), d) for d in os.listdir(case)
          if os.path.isdir(os.path.join(case, d)) and re.fullmatch(r"[\d.]+", d)]
    if not ts:
        refuse(f"REFUSE: no time directory in {case}")
    return sorted(ts)[-1][1]


def read_symmtensor(path):
    """symmTensor internal field -> list of 6-tuples (xx xy xz yy yz zz)."""
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<symmTensor>\s*\n?\s*(\d+)\s*\(", txt)
    if m:
        k = txt.index("(", m.end() - 1) + 1
        body = txt[k:txt.index("\n)", k)]
        return [tuple(float(v) for v in t.split())
                for t in re.findall(r"\(([^)]*)\)", body)]
    m = re.search(r"internalField\s+uniform\s+\(([^)]*)\)", txt)
    if not m:
        refuse(f"REFUSE: could not read symmTensor internalField from {path}")
    return [tuple(float(v) for v in m.group(1).split())]


def realizability(name):
    """Section 6: diagonals >= 0 and det(R) >= 0, on every cell."""
    case = os.path.join(HERE, name)
    t = latest_time(case)
    p = os.path.join(case, t, "R")
    if not os.path.isfile(p):
        refuse(f"REFUSE: {name} has no R field at time {t}")
    R = read_symmtensor(p)
    min_diag, min_det, bad_diag, bad_det = float("inf"), float("inf"), 0, 0
    for xx, xy, xz, yy, yz, zz in R:
        d = min(xx, yy, zz)
        det = (xx * (yy * zz - yz * yz)
               - xy * (xy * zz - yz * xz)
               + xz * (xy * yz - yy * xz))
        if d < min_diag:
            min_diag = d
        if det < min_det:
            min_det = det
        if d < 0.0:
            bad_diag += 1
        if det < 0.0:
            bad_det += 1
    return dict(cells=len(R), min_diagonal=min_diag, min_determinant=min_det,
                cells_negative_diagonal=bad_diag, cells_negative_determinant=bad_det,
                realizable=(bad_diag == 0 and bad_det == 0), time=t)


def square_rows():
    """reference and band per row, PARSED from the committed square gate JSON."""
    g = json.load(open(os.path.join(K0CS, "gate_k0cs.json")))
    out = {}
    for r in g["graded_rows"]:
        out[r["quantity"]] = dict(reference=r["reference"], band=r["band"],
                                  kind=r.get("kind"), unit=r.get("unit"))
    return out, g["cases"]


def tall_rows():
    g = json.load(open(os.path.join(K0CX, "gate_k0cx.json")))
    R, B = g["reference_parsed"], g["bands_parsed"]
    out = {
        "Nu_avg": dict(reference=R["Nu"]["hi"], band=B["Nu_pct"]["hi"], kind="REL"),
        "S":      dict(reference=R["S"]["hi"],  band=B["S_hi"],         kind="ABS"),
        "Vup":    dict(reference=R["Vup"]["hi"], band=B["V_pct"],       kind="REL"),
    }
    return out, g["measurements"]


def deviation(value, spec):
    if spec["kind"] == "REL":
        return 100.0 * (value - spec["reference"]) / spec["reference"]
    return value - spec["reference"]


def measure_arm(name, geom):
    case = os.path.join(HERE, name)
    if geom == "sq":
        return SQ.measure(case, name)
    saved = TL.HERE
    try:
        TL.HERE = HERE
        return TL.measure(name)
    finally:
        TL.HERE = saved


def main():
    missing = [c for c in CASES if not os.path.isfile(os.path.join(HERE, f"DONE.{c}"))]
    if missing:
        refuse("REFUSE: no completion marker for " + ", ".join(sorted(missing)))

    sq_spec, sq_cases = square_rows()
    tl_spec, tl_cases = tall_rows()
    SPEC = {"sq": sq_spec, "tl": tl_spec}
    BASE = {"sq": sq_cases, "tl": tl_cases}
    # the row that decides, and the rows that must not degrade
    NU = {"sq": "Nu_hot", "tl": "Nu_avg"}
    STRESS_SIDE = {"sq": ["Vpeak", "uv_peak"], "tl": ["Vup"]}
    STRAT = {"sq": "Sp", "tl": "S"}

    out = {"cases": {}, "realizability": {}, "rows": {},
           "decision_rule": dict(material_points=MATERIAL_PTS,
                                 source="K0cR_PREREGISTRATION.md Section 5")}

    for name, spec in sorted(CASES.items()):
        out["realizability"][name] = realizability(name)

    for name, spec in sorted(CASES.items()):
        geom = spec["geom"]
        arm = measure_arm(name, geom)
        base = BASE[geom][spec["baseline"]]
        base = base["measure"] if "measure" in base else base
        ctl = BASE[geom][spec["control"]]
        ctl = ctl["measure"] if "measure" in ctl else ctl
        out["cases"][name] = dict(measure=arm, baseline=spec["baseline"],
                                  control=spec["control"], geom=geom)
        rows = {}
        for q, s in SPEC[geom].items():
            if q not in arm or q not in base:
                continue
            d_ssg, d_base = deviation(arm[q], s), deviation(base[q], s)
            band = s["band"]
            row = dict(quantity=q, reference=s["reference"], band=band, kind=s["kind"],
                       value_ssg=arm[q], value_baseline=base[q],
                       deviation_ssg=d_ssg, deviation_baseline=d_base,
                       in_band_ssg=abs(d_ssg) <= band,
                       in_band_baseline=abs(d_base) <= band,
                       improvement_points=abs(d_base) - abs(d_ssg))
            if q in ctl:
                d_ctl = deviation(ctl[q], s)
                row["deviation_control"] = d_ctl
                row["in_band_control"] = abs(d_ctl) <= band
                # 2c: a pass the null arm also achieves carries no evidence
                row["pass_carries_evidence"] = bool(
                    row["in_band_ssg"] and not row["in_band_control"])
            rows[q] = row
        out["rows"][name] = rows

    # ---- the registered decision rule ---------------------------------------
    unreal = [n for n, v in out["realizability"].items() if not v["realizable"]]
    per_geom = {}
    for geom in ("sq", "tl"):
        names = [n for n, s in CASES.items() if s["geom"] == geom]
        nu = NU[geom]
        nus = [out["rows"][n].get(nu) for n in sorted(names)]
        nus = [r for r in nus if r]
        if len(nus) < 2:
            per_geom[geom] = "INCOMPLETE"
            continue
        if all(r["in_band_ssg"] for r in nus):
            per_geom[geom] = "STRESS"
        elif all(r["improvement_points"] >= MATERIAL_PTS for r in nus):
            per_geom[geom] = "PARTIAL"
        elif all(r["improvement_points"] <= -MATERIAL_PTS for r in nus):
            per_geom[geom] = "WORSE"
        elif all(abs(r["improvement_points"]) < MATERIAL_PTS for r in nus):
            per_geom[geom] = "NU_UNMOVED"
        else:
            per_geom[geom] = "MIXED"
    out["per_geometry"] = per_geom

    if unreal:
        verdict = "NOT A RESULT"
        why = "R went non-realizable in " + ", ".join(sorted(unreal)) + " (section 6)"
    elif "STRESS" in per_geom.values():
        verdict = "STRESS"
        why = ("the Nusselt deviation fell inside the gate band on both meshes of "
               "at least one geometry: the residual defect WAS the stress closure")
    elif all(v == "NU_UNMOVED" for v in per_geom.values()):
        verdict = "HEAT FLUX"
        why = ("a fully tensorial Reynolds-stress transport model, carrying the same "
               "gradient-diffusion heat flux, left the wall heat flux outside its band "
               "and moved it by less than %.0f points on every mesh: the defect is the "
               "heat-flux closure" % MATERIAL_PTS)
    elif "WORSE" in per_geom.values():
        verdict = "WORSE"
        why = "the Nusselt deviation grew materially; SSG does not separate the split here"
    elif "PARTIAL" in per_geom.values():
        verdict = "PARTIAL"
        why = ("Nusselt improved materially without reaching band: the stress closure "
               "carries PART of the defect")
    else:
        verdict = "MIXED"
        why = "the two meshes of a geometry disagree; see per_geometry"
    out["verdict"], out["verdict_because"] = verdict, why

    with open(os.path.join(HERE, "gate_k0cr.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)

    print("K0cR (X3) -- Reynolds-stress transport on both cavities")
    print("=" * 104)
    for n, v in sorted(out["realizability"].items()):
        print("  REALIZABILITY %-8s min diag %+.4e  min det %+.4e  bad %d/%d  %s"
              % (n, v["min_diagonal"], v["min_determinant"],
                 v["cells_negative_diagonal"] + v["cells_negative_determinant"],
                 v["cells"], "OK" if v["realizable"] else "*** NON-REALIZABLE ***"))
    print("-" * 104)
    print("  %-8s %-9s %10s %10s %9s %9s %8s %6s %s" %
          ("case", "quantity", "kEpsilon", "SSG", "dev base", "dev SSG", "band",
           "improv", "in band (SSG/base/lam)"))
    for n in sorted(out["rows"]):
        for q, r in sorted(out["rows"][n].items()):
            print("  %-8s %-9s %10.5g %10.5g %9.3f %9.3f %8.3g %6.2f  %s/%s/%s%s" %
                  (n, q, r["value_baseline"], r["value_ssg"],
                   r["deviation_baseline"], r["deviation_ssg"], r["band"],
                   r["improvement_points"],
                   "Y" if r["in_band_ssg"] else "n",
                   "Y" if r["in_band_baseline"] else "n",
                   ("Y" if r.get("in_band_control") else "n")
                   if "in_band_control" in r else "-",
                   "" if r.get("pass_carries_evidence", True) else "   <- hollow pass, 2c"))
    print("-" * 104)
    print("  per geometry: " + ", ".join(f"{k}={v}" for k, v in sorted(per_geom.items())))
    print("  VERDICT: %s" % verdict)
    print("  BECAUSE: %s" % why)
    return 0


if __name__ == "__main__":
    sys.exit(main())
