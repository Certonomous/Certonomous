#!/usr/bin/env python3
"""
T1b fourth-level comparator -- the (m, f, x) triple, graded under the AMENDED
rule: a Nu row whose grid triple is not CONVERGING is NOT A RESULT.

THE FROZEN COMPARATOR analyse_t1b.py IS NOT EDITED AND IS NOT RE-RUN BY THIS
FILE.  Its verdicts stand as returned (T1b_RESULTS.md section 1, gate_t1b.json)
and are printed beside the amended ones here for the record.  This file is the
amendment candidate of T1b_RESULTS.md section 8 (Charter 2b addendum, dated
2026-08-20, docket D440) made binding for the fourth level, registered in
docs/campaigns/T-family/T1b_L4_AMENDMENT.md before any R_*_x case existed.

WHAT IS REUSED, SO THAT NOTHING IN THE MEASUREMENT CAN DIFFER:
  * analyse_t1b.measure()   Nu, f, u_tau, y+ at a station; the wall radius
                            READ from points; the alphaEff factor READ from
                            the written alphat; friction from the 50-80 D
                            pressure drop.  Called exactly as the frozen
                            comparator calls it, at 60 / 70 / 80 D.
  * analyse_t1b.petukhov_f, RE_TAGS, STATIONS, PLATEAU_FRACTION
  * analyse_t1c.gci()       the observed order and GCI, r = 1.6
  * analyse_t1c.iterative_convergence()   the last-two-checkpoints gate
  * T1b_band.json           the band, committed before any case existed

WHAT IS NEW, AND IS THE WHOLE AMENDMENT (verdict_amended() below):
  order of evaluation for every Nu row --
    (1) any level of (m, f, x) NOT iteratively CONVERGED, or not plateaued
        across 60/70/80 D                                  -> NOT A RESULT
    (2) the (m, f, x) triple not CONVERGING (DIVERGENT, STAGNANT, OSCILLATORY
        or EXACT, as gci() classes it)                     -> NOT A RESULT,
        the x value, both triples and the orders printed beside it
    (3) CONVERGING: PASS if the x value lies within the band of T1b_band.json,
        else GATE FAIL; the GCI of the x level printed beside the verdict.
  The band is NOT the GCI (that is T1c's rule); it is the correlations'
  disagreement, as in the frozen comparator.  Only the gate on the triple
  state is added, and it can only turn a PASS or GATE FAIL into NOT A RESULT.

  Both triples are reported per Re: (c, m, f) as the frozen comparator graded
  it, and (m, f, x).  The friction triples are reported the same way.

--selftest proves, on synthetic triples and without touching any case, that
  a DIVERGENT, a STAGNANT and an OSCILLATORY triple whose x value lies INSIDE
  the band return NOT A RESULT, and that with a CONVERGING triple both PASS
  and GATE FAIL are reachable by moving the x value (the mutation control).

WHAT THIS COMPARATOR CANNOT SEE: everything the frozen one cannot (its
docstring), plus: it does not re-grade the Prt discrimination, the
wall-function comparison or C_lam -- those rows are the frozen rung's and are
not touched; and a CONVERGING (m, f, x) triple says the x-to-f step has fallen
to at most 1.6^-0.5 of the f-to-m step, not that the limit has been reached.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_t1b as T1B                              # noqa: E402
import analyse_t1c as T1C                              # noqa: E402

LEVELS_FROZEN = ("c", "m", "f")
LEVELS_L4 = ("m", "f", "x")
CASES_ORIGINAL = [f"R_{t}_{l}" for t in T1B.RE_TAGS for l in LEVELS_FROZEN]
CASES_X = [f"R_{t}_x" for t in T1B.RE_TAGS]
EXIT_OK, EXIT_REFUSE, EXIT_FAIL = T1B.EXIT_OK, T1B.EXIT_REFUSE, T1B.EXIT_FAIL


def verdict_amended(nu_m, nu_f, nu_x, reference, band):
    """THE AMENDED RULE, as a pure function so --selftest can prove it.

    Returns dict(verdict, grid, deviation_pct, band_pct, value).  verdict is
    NOT A RESULT unless gci(m, f, x) is CONVERGING; then PASS / GATE FAIL
    against the band.  Iterative convergence and the plateau are gated
    BEFORE this is called, exactly as in the frozen comparator.
    """
    g = T1C.gci(nu_m, nu_f, nu_x)
    dev = 100.0 * abs(nu_x - reference) / reference
    bpct = 100.0 * band / reference
    if g["state"] != "CONVERGING":
        return dict(verdict="NOT A RESULT", grid=g, deviation_pct=dev,
                    band_pct=bpct, value=nu_x,
                    why=f"grid triple (m,f,x) is {g['state']}; the x value "
                        f"is {dev:.3f} % from the reference against a band of "
                        f"{bpct:.3f} %, and that is a statement about the "
                        "finest mesh built, not about a limit")
    return dict(verdict="PASS" if dev <= bpct else "GATE FAIL", grid=g,
                deviation_pct=dev, band_pct=bpct, value=nu_x)


def verdict_frozen(nu_c, nu_m, nu_f, reference, band):
    """The frozen rule (analyse_t1b.py lines 189-197), for printing beside."""
    g = T1C.gci(nu_c, nu_m, nu_f)
    dev = 100.0 * abs(nu_f - reference) / reference
    bpct = 100.0 * band / reference
    return dict(verdict="PASS" if dev <= bpct else "GATE FAIL", grid=g,
                deviation_pct=dev, band_pct=bpct, value=nu_f)


def fmt_grid(g):
    s = g["state"]
    if "order" in g:
        s += f" p={g['order']:+.3f}"
    if "GCI_pct" in g:
        s += f" GCI={g['GCI_pct']:.3f} %"
    return s


def selftest():
    """Synthetic triples at the Re = 1e4 band.  No case is read."""
    Rf, Bd = 30.906752151303174, 0.8789035978385069     # T1b_band.json, 1e4
    bp = 100.0 * Bd / Rf
    inside = Rf * (1.0 + 0.5 * Bd / Rf)        # 1.42 % off, inside 2.84 %
    outside = Rf * (1.0 + 2.0 * Bd / Rf)       # 5.69 % off, outside
    tests = [
        # name,           m,            f,            x,         expect
        ("DIVERGENT inside band",  inside - 1.6, inside - 0.8, inside, "NOT A RESULT"),
        ("STAGNANT inside band",   inside - 1.7, inside - 0.8, inside, "NOT A RESULT"),
        ("OSCILLATORY inside band", inside + 0.5, inside - 0.5, inside, "NOT A RESULT"),
        ("EXACT (f == x) inside band", inside - 0.5, inside, inside, "NOT A RESULT"),
        ("CONVERGING inside band",  inside - 1.0, inside - 0.25, inside, "PASS"),
        ("CONVERGING outside band", outside - 1.0, outside - 0.25, outside, "GATE FAIL"),
        ("CONVERGING, x outside, f inside", inside - 2.0, inside, inside + 0.9, "GATE FAIL"),
    ]
    print(f"selftest: reference {Rf:.3f}, band {Bd:.3f} ({bp:.3f} %)")
    ok = True
    states = set()
    for name, m, f, x, expect in tests:
        v = verdict_amended(m, f, x, Rf, Bd)
        states.add(v["grid"]["state"])
        good = v["verdict"] == expect
        ok &= good
        print(f"  {'ok ' if good else 'BAD'} {name:34s} ({m:.3f}, {f:.3f}, "
              f"{x:.3f}) -> {fmt_grid(v['grid']):32s} dev {v['deviation_pct']:.3f} % "
              f"-> {v['verdict']}  (expected {expect})")
    need = {"DIVERGENT", "STAGNANT", "OSCILLATORY", "EXACT", "CONVERGING"}
    if not need <= states:
        ok = False
        print(f"  BAD states exercised {sorted(states)}, missing {sorted(need - states)}")
    # the frozen rule, for contrast: the same DIVERGENT triple PASSES under it
    fv = verdict_frozen(inside - 1.6, inside - 0.8, inside, Rf, Bd)
    print(f"  frozen rule on the DIVERGENT triple: {fv['verdict']} "
          f"({fmt_grid(fv['grid'])}) -- this is the defect the amendment closes")
    ok &= fv["verdict"] == "PASS"
    # the measured T1b triples, as recorded, under both rules
    rec = {1e4: (30.1192, 30.8307, 31.6193, 30.906752151303174, 0.8789035978385069),
           3e5: (430.2197, 439.7609, 449.2554, 456.72281129214036, 26.256112316273573)}
    for Re, (c, m, f, R0, B0) in rec.items():
        a = verdict_amended(c, m, f, R0, B0)
        z = verdict_frozen(c, m, f, R0, B0)
        print(f"  T1b (c,m,f) at Re {Re:.0f} as recorded: frozen {z['verdict']}, "
              f"amended {a['verdict']} ({a['grid']['state']})")
        ok &= a["verdict"] == "NOT A RESULT" and z["verdict"] == "PASS"
    print("SELFTEST " + ("PASSED" if ok else "FAILED"))
    return EXIT_OK if ok else EXIT_FAIL


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return selftest()

    band = json.load(open(os.path.join(HERE, "T1b_band.json")))
    ref = {f"{r['Re']:.0f}": r for r in band["rows"]}
    frozen = {}
    gp = os.path.join(HERE, "gate_t1b.json")
    if os.path.isfile(gp):
        for r in json.load(open(gp))["rows"]:
            if r.get("quantity") == "Nu":
                frozen[f"{r['Re']:.0f}"] = r

    missing = [c for c in CASES_ORIGINAL + CASES_X
               if not os.path.isfile(os.path.join(HERE, f"DONE.{c}"))]
    if missing:
        T1B.refuse("REFUSE: no completion marker for " + ", ".join(sorted(missing)))

    out = {"band_source": "T1b_band.json (committed before any case existed)",
           "rule": "amended: NOT A RESULT unless the (m,f,x) triple is "
                   "CONVERGING; then PASS/GATE FAIL against the band "
                   "(T1b_L4_AMENDMENT.md)",
           "frozen_comparator": "analyse_t1b.py, untouched; its verdicts "
                                "printed beside from gate_t1b.json",
           "rows": [], "cases": {}}
    tag_n = 0

    def m_all(case):
        """Exactly analyse_t1b.main's m_all: every station, plateau, conv."""
        d = os.path.join(HERE, case)
        ms = {s: T1B.measure(d, s) for s in T1B.STATIONS}
        conv = T1C.iterative_convergence(d)
        nus = [ms[s]["Nu"] for s in T1B.STATIONS]
        last = T1B.STATIONS[-1]
        rec = dict(case=case, stations=ms, iterative_convergence=conv,
                   Nu=ms[last]["Nu"], Nu_station_spread=max(nus) - min(nus),
                   yplus=ms[last]["yplus"], f=ms[last]["f"], Re=ms[last]["Re"],
                   alphaEff_factor=ms[last]["alphaEff_factor"])
        out["cases"][case] = rec
        return rec

    for tag, Re in sorted(T1B.RE_TAGS.items(), key=lambda kv: kv[1]):
        s = ref[f"{Re:.0f}"]
        Rf, Bd = s["reference"], s["band"]
        bpct = 100.0 * Bd / Rf
        print(f"\n### Re = {Re:.0f}   reference {Rf:.3f} +/- {Bd:.3f} "
              f"({bpct:.2f} %)   [midpoint of two correlations]")
        lv = {l: m_all(f"R_{tag}_{l}") for l in ("c", "m", "f", "x")}
        for l in ("c", "m", "f", "x"):
            r = lv[l]
            print(f"    {l}  Nu = {r['Nu']:9.3f}  y+ = {r['yplus']:7.3f}  "
                  f"f = {r['f']:.5f}  station spread {r['Nu_station_spread']:.3f}"
                  f"  [{r['iterative_convergence']['state']}]")

        gf = T1C.gci(*[lv[l]["Nu"] for l in LEVELS_FROZEN])
        gx = T1C.gci(*[lv[l]["Nu"] for l in LEVELS_L4])
        ff = T1C.gci(*[lv[l]["f"] for l in LEVELS_FROZEN])
        fx = T1C.gci(*[lv[l]["f"] for l in LEVELS_L4])
        print(f"    Nu triple (c,m,f): {fmt_grid(gf)}     (m,f,x): {fmt_grid(gx)}")
        print(f"    f  triple (c,m,f): {fmt_grid(ff)}     (m,f,x): {fmt_grid(fx)}")
        fz = frozen.get(f"{Re:.0f}")
        fz_txt = (f"{fz['verdict']} (Nu {fz['value']:.3f}, {fz['deviation_pct']:.3f} %"
                  f", grid {fz['grid']['state']})" if fz else "not on disk")
        print(f"    frozen comparator's verdict on (c,m,f), for the record: {fz_txt}")

        bad = [l for l in LEVELS_L4
               if lv[l]["iterative_convergence"]["state"] != "CONVERGED"]
        notflat = [l for l in LEVELS_L4
                   if lv[l]["Nu_station_spread"] > T1B.PLATEAU_FRACTION * Bd]
        row = dict(row=f"X{tag_n}", Re=Re, quantity="Nu", reference=Rf, band=Bd,
                   band_pct=bpct, value=lv["x"]["Nu"],
                   levels={l: lv[l]["Nu"] for l in ("c", "m", "f", "x")},
                   grid_cmf=gf, grid_mfx=gx, frozen_verdict=fz,
                   dittus_boelter=s["dittus_boelter"], gnielinski=s["gnielinski"])
        if bad or notflat:
            why = []
            if bad:
                why.append("levels " + ",".join(bad) + " not iteratively converged")
            if notflat:
                why.append("levels " + ",".join(notflat) +
                           " have not plateaued across 60/70/80 D")
            row.update(verdict="NOT A RESULT", why="; ".join(why))
            out["rows"].append(row)
            print(f"    ROW X{tag_n}: NOT A RESULT -- {'; '.join(why)}")
            tag_n += 1
            continue

        v = verdict_amended(lv["m"]["Nu"], lv["f"]["Nu"], lv["x"]["Nu"], Rf, Bd)
        row.update(verdict=v["verdict"], deviation_pct=v["deviation_pct"],
                   why=v.get("why"))
        out["rows"].append(row)
        print(f"    ROW X{tag_n}: Nu_x = {v['value']:.3f}, deviation "
              f"{v['deviation_pct']:.3f} % against band {bpct:.3f} %  "
              f"(m,f,x) {fmt_grid(gx)}  -> {v['verdict']}"
              + (f"\n         {v['why']}" if v.get("why") else ""))
        tag_n += 1

        fref = T1B.petukhov_f(Re)
        fdev = 100.0 * abs(lv["x"]["f"] - fref) / fref
        out["rows"].append(dict(row=f"X{tag_n}", Re=Re, quantity="f",
                                value=lv["x"]["f"], reference=fref,
                                deviation_pct=fdev, grid_cmf=ff, grid_mfx=fx,
                                levels={l: lv[l]["f"] for l in ("c", "m", "f", "x")},
                                verdict="REPORTED"))
        print(f"    ROW X{tag_n}: f_x = {lv['x']['f']:.5f} vs Petukhov {fref:.5f}, "
              f"{fdev:.2f} %  (m,f,x) {fmt_grid(fx)}   [REPORTED -- a friction "
              "error is a solver or mesh fault; a Nusselt error with correct "
              "friction is the thermal closure]")
        tag_n += 1

    with open(os.path.join(HERE, "gate_t1b_L4.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)

    fails = [r for r in out["rows"] if r["verdict"] == "GATE FAIL"]
    nres = [r for r in out["rows"] if r["verdict"] == "NOT A RESULT"]
    graded = [r for r in out["rows"] if r["verdict"] in ("PASS", "GATE FAIL")]
    print(f"\n{'-'*72}")
    print(f"  {len(graded)} graded rows: {len(fails)} GATE FAIL, "
          f"{len(nres)} NOT A RESULT   [amended rule; frozen verdicts above]")
    print("  The band is the DISAGREEMENT between two correlations, not either")
    print("  one's own accuracy.  Inside it means consistent with the canon,")
    print("  NOT verified to that tolerance.  A CONVERGING triple means the")
    print("  x-to-f step fell to at most 1.6^-0.5 of the f-to-m step, not that")
    print("  a limit was reached.")
    return EXIT_FAIL if fails else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
