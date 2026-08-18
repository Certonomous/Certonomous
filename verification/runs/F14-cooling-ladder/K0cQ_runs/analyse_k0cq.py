#!/usr/bin/env python3
"""
K0cQ (X2) comparator -- constitutive anisotropy on both cavities.

WRITTEN AND COMMITTED BEFORE ANY CASE PRODUCED A RESULT.  The rung it serves
was pre-registered in K0cQ_PREREGISTRATION.md and the decision rule below is
transcribed from that document, not chosen here.

TWO DESIGN RULES, both of them reactions to recorded defects:

 1. THE QCR ARM IS MEASURED BY ITS OWN GEOMETRY'S INSTRUMENT.  The square arms
    go through analyse_k0cs.measure and the tall arms through
    analyse_k0cx.measure -- the same functions that produced the baselines.  A
    difference measured by two different instruments is not a difference.

 2. NO BASELINE CASE DIRECTORY IS WRITTEN TO.  Both measure() functions run
    `postProcess -func writeCellCentres`, which writes into the case it is
    pointed at.  Baseline values are therefore READ FROM THE COMMITTED GATE
    JSON rather than re-measured, so that this rung cannot modify a recorded
    artifact of another rung.  The Ccr1=0 control needs the baseline U field,
    which is read directly and never written.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LADDER = os.path.dirname(HERE)
K0CS = os.path.join(LADDER, "K0cS_runs")
K0CX = os.path.join(LADDER, "K0cX_runs")

sys.path.insert(0, K0CS)
sys.path.insert(0, K0CX)
import analyse_k0cs as SQ          # noqa: E402
import analyse_k0cx as TL          # noqa: E402

# ---- the registered decision rule, transcribed from Section 4 --------------
SMALL_DNU_PCT = 1.0        # abs(dNu) below this, on BOTH geometries
SMALL_DS_ABS = 0.02        # abs(dS)  below this, on BOTH geometries
LARGE_BAND = {"sq": 10.0,  # K0cS G1 gate band
              "tl": 5.41}  # K0cX R10 u_val, hi Ra

# ---- reference values, for DIRECTION only; they gate nothing ---------------
# Direction is registered separately from size (Section 4.1) and decides
# nothing on its own.  The decision rule is over DIFFERENCES and needs no
# reference at all.
REF_NU = {"sq": 63.45,     # Ampofo, K0cS G1 reference
          "tl": 7.57}      # Betts Table 1 average Nu, hi Ra

CASES = {
    "Q_sq_c": dict(geom="sq", baseline="S_SST_c",   ccr1=0.3),
    "Q_sq_f": dict(geom="sq", baseline="S_SST_f",   ccr1=0.3),
    "Q_tl_c": dict(geom="tl", baseline="X_hi_c_SST", ccr1=0.3),
    "Q_tl_f": dict(geom="tl", baseline="X_hi_f_SST", ccr1=0.3),
    "Z_sq_c": dict(geom="sq", baseline="S_SST_c",   ccr1=0.0),
    "Z_tl_c": dict(geom="tl", baseline="X_hi_c_SST", ccr1=0.0),
}
BASE_DIR = {"sq": K0CS, "tl": K0CX}
# the stratification parameter carries a different name on each geometry
STRAT_KEY = {"sq": "Sp", "tl": "S"}


def refuse(msg):
    print(msg)
    sys.exit(2)


def latest_time(case):
    ts = []
    for d in os.listdir(case):
        try:
            v = float(d)
        except ValueError:
            continue
        if os.path.isdir(os.path.join(case, d)):
            ts.append((v, d))
    if not ts:
        refuse(f"REFUSE: no time directory in {case}")
    return sorted(ts)[-1][1]


def baseline_measure(geom, name):
    """Recorded baseline values, read from the committed gate JSON."""
    if geom == "sq":
        g = json.load(open(os.path.join(K0CS, "gate_k0cs.json")))
        if name not in g["cases"]:
            refuse(f"REFUSE: {name} absent from gate_k0cs.json")
        return g["cases"][name]["measure"]
    g = json.load(open(os.path.join(K0CX, "gate_k0cx.json")))
    if name not in g["measurements"]:
        refuse(f"REFUSE: {name} absent from gate_k0cx.json")
    return g["measurements"][name]


def measure_arm(name, geom):
    """Measure a K0cQ arm with its own geometry's instrument."""
    case = os.path.join(HERE, name)
    if geom == "sq":
        return SQ.measure(case, name)
    saved = TL.HERE
    try:
        TL.HERE = HERE          # point the tall instrument at THIS run tree
        return TL.measure(name)
    finally:
        TL.HERE = saved


def control_delta(zname, geom, bname):
    """max abs component difference between the Ccr1=0 arm and stock kOmegaSST.

    Registered requirement (Section 4.2): exactly 0.0.  Read-only on both
    sides -- nothing is written into the baseline case."""
    zc = os.path.join(HERE, zname)
    bc = os.path.join(BASE_DIR[geom], bname)
    zt, bt = latest_time(zc), latest_time(bc)
    zu = SQ.read_internal(os.path.join(zc, zt, "U"), vector=True)
    bu = SQ.read_internal(os.path.join(bc, bt, "U"), vector=True)
    if len(zu) != len(bu):
        refuse(f"REFUSE: {zname} has {len(zu)} cells, {bname} has {len(bu)}")
    worst = 0.0
    for a, b in zip(zu, bu):
        for i in range(3):
            d = abs(a[i] - b[i])
            if d > worst:
                worst = d
    return dict(control=zname, against=bname, cells=len(zu),
                max_abs_dU=worst, time_control=zt, time_baseline=bt,
                machine_zero=(worst == 0.0))


def main():
    missing = [c for c in CASES if not os.path.isfile(os.path.join(HERE, f"DONE.{c}"))]
    if missing:
        refuse("REFUSE: no completion marker for " + ", ".join(sorted(missing)))

    out = {"cases": {}, "controls": {}, "arms": {}}

    # ---- controls FIRST.  A failed control makes its geometry NOT A RESULT,
    # and that must be known before any difference from it is reported.
    for z in ("Z_sq_c", "Z_tl_c"):
        spec = CASES[z]
        out["controls"][z] = control_delta(z, spec["geom"], spec["baseline"])

    for name, spec in sorted(CASES.items()):
        out["cases"][name] = dict(measure=measure_arm(name, spec["geom"]),
                                  baseline=spec["baseline"], geom=spec["geom"],
                                  Ccr1=spec["ccr1"])

    # ---- the differences, QCR arm against its own baseline twin ------------
    for name, spec in sorted(CASES.items()):
        if spec["ccr1"] == 0.0:
            continue
        geom = spec["geom"]
        sk = STRAT_KEY[geom]
        arm = out["cases"][name]["measure"]
        base = baseline_measure(geom, spec["baseline"])
        for k in ("Nu_hot", sk):
            if k not in arm or k not in base:
                refuse(f"REFUSE: '{k}' missing for {name} or {spec['baseline']}")
        dnu_pct = 100.0 * (arm["Nu_hot"] - base["Nu_hot"]) / base["Nu_hot"]
        ds_abs = arm[sk] - base[sk]
        ref = REF_NU[geom]
        e_base = abs(base["Nu_hot"] - ref)
        e_arm = abs(arm["Nu_hot"] - ref)
        rec = dict(
            case=name, geom=geom, baseline=spec["baseline"],
            Nu_hot_baseline=base["Nu_hot"], Nu_hot_qcr=arm["Nu_hot"],
            dNu_pct=dnu_pct,
            strat_key=sk, strat_baseline=base[sk], strat_qcr=arm[sk],
            dS_abs=ds_abs,
            large_band=LARGE_BAND[geom],
            is_small=(abs(dnu_pct) < SMALL_DNU_PCT and abs(ds_abs) < SMALL_DS_ABS),
            is_large=(abs(dnu_pct) >= LARGE_BAND[geom]),
            # DIRECTION, registered separately and gating nothing
            direction=("toward" if e_arm < e_base else
                       ("away" if e_arm > e_base else "unchanged")),
            reference_used_for_direction_only=ref,
            control_ok=out["controls"]["Z_%s_c" % geom]["machine_zero"],
        )
        # REPORTED, NEVER GATED: the Reynolds shear stress is the quantity an
        # anisotropy correction acts on most directly, and the registered rule
        # does not mention it.  It is carried so the reading has it, and it
        # decides nothing.
        for key in ("uv_peak", "uv_peak_midheight"):
            if key in arm and key in base:
                rec["reported_not_gated_d_uv_pct"] = (
                    100.0 * (arm[key] - base[key]) / base[key]
                    if base[key] else None)
                rec["reported_not_gated_uv_key"] = key
                break
        out["arms"][name] = rec

    # ---- the rung verdict, by the registered rule ---------------------------
    arms = list(out["arms"].values())
    bad = [c for c, v in out["controls"].items() if not v["machine_zero"]]
    if bad:
        verdict = "NOT A RESULT"
        why = ("the Ccr1=0 control did not reproduce stock kOmegaSST for "
               + ", ".join(sorted(bad)))
    elif all(a["is_small"] for a in arms):
        verdict = "SMALL"
        why = ("every arm moved Nusselt by less than %.1f %% and stratification "
               "by less than %.2f: the anisotropy route is ruled out and the "
               "synthesis group-C reading survives" % (SMALL_DNU_PCT, SMALL_DS_ABS))
    elif any(a["is_large"] for a in arms):
        verdict = "LARGE"
        why = ("at least one arm moved Nusselt by at least its geometry's own "
               "gate band: the anisotropy route is live and the synthesis "
               "group-C reading is FALSIFIED")
    else:
        verdict = "INTERMEDIATE"
        why = ("the effect is above the SMALL threshold and below every gate "
               "band: the term acts but does not dominate, and this settles "
               "nothing on its own")

    out["verdict"] = verdict
    out["verdict_because"] = why
    out["decision_rule"] = dict(small_dNu_pct=SMALL_DNU_PCT,
                                small_dS_abs=SMALL_DS_ABS,
                                large_band=LARGE_BAND,
                                source="K0cQ_PREREGISTRATION.md Section 4")

    with open(os.path.join(HERE, "gate_k0cq.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)

    print("K0cQ (X2) -- constitutive anisotropy on both cavities")
    print("=" * 96)
    for z, v in sorted(out["controls"].items()):
        print("  CONTROL %-8s vs %-12s  max|dU| = %.17g   %s"
              % (z, v["against"], v["max_abs_dU"],
                 "machine zero" if v["machine_zero"] else "*** NOT ZERO ***"))
    print("-" * 96)
    print("  %-8s %-8s %12s %12s %9s %10s %10s %9s" %
          ("arm", "geom", "Nu base", "Nu QCR", "dNu %", "dS", "direction", "d uv %"))
    for a in sorted(arms, key=lambda r: r["case"]):
        duv = a.get("reported_not_gated_d_uv_pct")
        print("  %-8s %-8s %12.5f %12.5f %9.3f %10.5f %10s %9s" %
              (a["case"], a["geom"], a["Nu_hot_baseline"], a["Nu_hot_qcr"],
               a["dNu_pct"], a["dS_abs"], a["direction"],
               ("%.3f" % duv) if duv is not None else "-"))
    print("-" * 96)
    print("  VERDICT: %s" % verdict)
    print("  BECAUSE: %s" % why)
    return 0


if __name__ == "__main__":
    sys.exit(main())
