#!/usr/bin/env python3
"""
T1b comparator -- fully developed turbulent pipe against TWO correlations.

WRITTEN AND COMMITTED BEFORE ANY CASE PRODUCED A RESULT (Charter 2d).

The band is NOT computed here and NOT typed here.  It is read from
T1b_band.json, which was committed before any T1b case directory existed:
reference = the midpoint of Dittus-Boelter and Gnielinski, band = the
half-spread.  No solution can move it.

WHAT IS CARRIED FORWARD FROM T1c, BECAUSE IT WAS PAID FOR ONCE:
  * the wall radius is READ from polyMesh/points, never taken as D/2.  In T1c
    that assumption cost 9 % of the Nusselt number and produced a false
    DIVERGENT verdict, because the fixed absolute error grew in relative terms
    as the mesh refined.
  * no grid claim is made from a triple containing a level still moving between
    its last two checkpoints.  In T1c NO case tripped residualControl and the
    offending case's residual was an unremarkable 4e-05, so the residual is not
    the instrument -- the written fields are.
  * the alphaEff factor is READ from the written alphat field, not assumed.  On
    the wall-function arm the thermal wall function puts a non-zero turbulent
    conductivity on the patch, and the wall heat flux is alphaEff.dT/dn, not
    alpha.dT/dn.  Dropping it would report only the molecular part.

WHAT THIS COMPARATOR CANNOT SEE:
  * whether either correlation is right.  It grades against their MIDPOINT and
    bands by their DISAGREEMENT, which bounds what the literature agrees on --
    a solution inside the band is consistent with the canon, NOT verified to
    that tolerance.
  * roughness, variable properties, entrance effects or buoyancy, all excluded
    by the design.
  * anything at a Reynolds number where the wall-function arm was not built.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_t1c as T1C                              # noqa: E402

FS = 1.25
R_REFINE = 1.6
RE_TAGS = {"10k": 1.0e4, "30k": 3.0e4, "100k": 1.0e5, "300k": 3.0e5}
LEVELS = ("c", "m", "f")
STATIONS = (60.0, 70.0, 80.0)
PLATEAU_FRACTION = 0.2      # Nu spread across stations must be < this x band
WF_YPLUS_FLOOR = 30.0       # below this a wall function is outside its validity
EXIT_OK, EXIT_REFUSE, EXIT_FAIL = 0, 2, 1


def refuse(msg):
    print(msg)
    sys.exit(EXIT_REFUSE)


def case_txt(case_dir, key):
    return T1C.case_txt(case_dir, key)


def measure(case_dir, station_xD):
    """Nu, f, u_tau and achieved y+ at one axial station."""
    t = T1C.latest_time(case_dir)
    for func in ("writeCellCentres", "writeCellVolumes"):
        r = T1C.foam(case_dir, f"postProcess -func {func} -time {t} "
                               f"> log.{func} 2>&1")
        if r.returncode != 0:
            refuse(f"REFUSE: {func} failed in {case_dir}")
    Cx = T1C.read_internal(os.path.join(case_dir, t, "Cx"))
    Cy = T1C.read_internal(os.path.join(case_dir, t, "Cy"))
    V = T1C.read_internal(os.path.join(case_dir, t, "V"))
    T = T1C.read_internal(os.path.join(case_dir, t, "T"))
    U = T1C.read_internal(os.path.join(case_dir, t, "U"), vector=True)
    P = T1C.read_internal(os.path.join(case_dir, t, "p_rgh"))

    R_wall = T1C.wall_radius(case_dir)
    D = 2.0 * R_wall
    nu = float(case_txt(case_dir, "nu").split()[0])
    Pr = float(case_txt(case_dir, "Pr"))
    Ub = float(case_txt(case_dir, "U").split()[0])
    grad = float(case_txt(case_dir, "dTdn_wall").split()[0])
    alpha = nu / Pr

    xs = sorted(set(round(v, 10) for v in Cx))
    xsel = min(xs, key=lambda v: abs(v - station_xD * D))
    idx = [i for i, v in enumerate(Cx) if round(v, 10) == xsel]

    T_bulk = (sum(U[i][0] * T[i] * V[i] for i in idx)
              / sum(U[i][0] * V[i] for i in idx))
    iw = max(idx, key=lambda i: Cy[i])
    h = R_wall - Cy[iw]

    # THE alphaEff FACTOR, READ AND NOT ASSUMED.
    at_path = os.path.join(case_dir, t, "alphat")
    at = T1C.read_patch(at_path, "wall") if os.path.isfile(at_path) else None
    alphat_w = (at[0] if at else 0.0)
    aeff = 1.0 + alphat_w / alpha
    Tw = T[iw] + grad * h
    Nu = D * grad * aeff / abs(Tw - T_bulk)

    # friction from the fully developed pressure gradient, and u_tau from the
    # force balance tau_w = -(dp/dx) R / 2, which needs no velocity derivative
    def p_at(xv):
        ii = [i for i, v in enumerate(Cx) if round(v, 10) == xv]
        return sum(P[i] * V[i] for i in ii) / sum(V[i] for i in ii)
    x1 = min(xs, key=lambda v: abs(v - 50.0 * D))
    x2 = min(xs, key=lambda v: abs(v - 80.0 * D))
    dpdx = (p_at(x2) - p_at(x1)) / (x2 - x1)
    f = -dpdx * D / (0.5 * Ub ** 2)
    tau_w = -dpdx * R_wall / 2.0
    ut = math.sqrt(abs(tau_w))
    y1 = h
    return dict(Nu=Nu, T_bulk=T_bulk, T_wall=Tw, alphat_wall=alphat_w,
                alphaEff_factor=aeff, station_xD=xsel / D, f=f, u_tau=ut,
                yplus=y1 * ut / nu, first_cell_centre=y1, R_wall=R_wall,
                D_used=D, dpdx=dpdx, time=t, Re=Ub * D / nu)


def petukhov_f(Re):
    return (0.790 * math.log(Re) - 1.64) ** -2.0


def main():
    band = json.load(open(os.path.join(HERE, "T1b_band.json")))
    ref = {}
    for r in band["rows"]:
        ref[f"{r['Re']:.0f}"] = r

    cases = []
    for tag in RE_TAGS:
        cases += [f"R_{tag}_{l}" for l in LEVELS] + [f"P_{tag}"]
    cases += ["W_100k", "W_300k", "C_lam"]
    missing = [c for c in cases
               if not os.path.isfile(os.path.join(HERE, f"DONE.{c}"))]
    if missing:
        refuse("REFUSE: no completion marker for " + ", ".join(sorted(missing)))

    out = {"band_source": "T1b_band.json (committed before any case existed)",
           "rows": [], "cases": {}, "wall_treatment_comparison": [],
           "prt_discrimination": [], "controls": []}
    tag_n = 0

    def m_all(case):
        """Measure at every station and test the development plateau."""
        d = os.path.join(HERE, case)
        ms = {s: measure(d, s) for s in STATIONS}
        conv = T1C.iterative_convergence(d)
        nus = [ms[s]["Nu"] for s in STATIONS]
        spread = max(nus) - min(nus)
        rec = dict(case=case, stations=ms, iterative_convergence=conv,
                   Nu=ms[STATIONS[-1]]["Nu"], Nu_station_spread=spread,
                   yplus=ms[STATIONS[-1]]["yplus"], f=ms[STATIONS[-1]]["f"],
                   Re=ms[STATIONS[-1]]["Re"],
                   alphaEff_factor=ms[STATIONS[-1]]["alphaEff_factor"])
        out["cases"][case] = rec
        return rec

    for tag, Re in sorted(RE_TAGS.items(), key=lambda kv: kv[1]):
        s = ref[f"{Re:.0f}"]
        Rf, Bd = s["reference"], s["band"]
        print(f"\n### Re = {Re:.0f}   reference {Rf:.3f} +/- {Bd:.3f} "
              f"({100*Bd/Rf:.2f} %)   [midpoint of two correlations]")
        lv = {l: m_all(f"R_{tag}_{l}") for l in LEVELS}
        for l in LEVELS:
            r = lv[l]
            print(f"    {l}  Nu = {r['Nu']:9.3f}  y+ = {r['yplus']:7.3f}  "
                  f"f = {r['f']:.5f}  station spread {r['Nu_station_spread']:.3f}"
                  f"  [{r['iterative_convergence']['state']}]")

        bad = [l for l in LEVELS
               if lv[l]["iterative_convergence"]["state"] != "CONVERGED"]
        notflat = [l for l in LEVELS
                   if lv[l]["Nu_station_spread"] > PLATEAU_FRACTION * Bd]
        if bad or notflat:
            why = []
            if bad:
                why.append("levels " + ",".join(bad) + " not iteratively converged")
            if notflat:
                why.append("levels " + ",".join(notflat) +
                           " have not plateaued across 60/70/80 D")
            out["rows"].append(dict(row=f"B{tag_n}", Re=Re, quantity="Nu",
                                    verdict="NOT A RESULT", why="; ".join(why)))
            print(f"    ROW B{tag_n}: NOT A RESULT -- {'; '.join(why)}")
            tag_n += 1
            continue

        g = T1C.gci(lv["c"]["Nu"], lv["m"]["Nu"], lv["f"]["Nu"])
        val = lv["f"]["Nu"]
        dev = 100.0 * abs(val - Rf) / Rf
        bpct = 100.0 * Bd / Rf
        verdict = "PASS" if dev <= bpct else "GATE FAIL"
        out["rows"].append(dict(row=f"B{tag_n}", Re=Re, quantity="Nu",
                                value=val, reference=Rf, band=Bd,
                                deviation_pct=dev, band_pct=bpct,
                                grid=g, verdict=verdict,
                                dittus_boelter=s["dittus_boelter"],
                                gnielinski=s["gnielinski"]))
        print(f"    ROW B{tag_n}: Nu = {val:.3f}, deviation {dev:.3f} % "
              f"against band {bpct:.3f} %  grid {g['state']}"
              + (f" p={g['order']:.3f} GCI={g['GCI_pct']:.3f} %"
                 if g["state"] == "CONVERGING" else "")
              + f"  -> {verdict}")
        tag_n += 1

        # friction, the attribution lever
        fref = petukhov_f(Re)
        fdev = 100.0 * abs(lv["f"]["f"] - fref) / fref
        out["rows"].append(dict(row=f"B{tag_n}", Re=Re, quantity="f",
                                value=lv["f"]["f"], reference=fref,
                                deviation_pct=fdev,
                                verdict="REPORTED"))
        print(f"    ROW B{tag_n}: f = {lv['f']['f']:.5f} vs Petukhov "
              f"{fref:.5f}, {fdev:.2f} %   [REPORTED -- a friction error is a "
              "solver or mesh fault; a Nusselt error with correct friction is "
              "the thermal closure]")
        tag_n += 1

        # Prt discrimination (T1 section 7.1)
        p = m_all(f"P_{tag}")
        sep = 100.0 * abs(p["Nu"] - val) / val
        out["prt_discrimination"].append(
            dict(Re=Re, Nu_prt085=val, Nu_prt100=p["Nu"], separation_pct=sep,
                 band_pct=bpct, separated=sep > bpct))
        print(f"    Prt 0.85 -> 1.0 moves Nu {sep:.2f} % against a band of "
              f"{bpct:.2f} %  -> {'SEPARATED' if sep > bpct else 'NOT SEPARATED'}")

        # wall treatment, where the arm exists
        wcase = f"W_{tag}"
        if os.path.isdir(os.path.join(HERE, wcase)):
            w = m_all(wcase)
            diff = 100.0 * abs(w["Nu"] - val) / val
            inval = w["yplus"] < WF_YPLUS_FLOOR
            out["wall_treatment_comparison"].append(
                dict(Re=Re, Nu_resolved=val, Nu_wallfunction=w["Nu"],
                     difference_pct=diff, band_pct=bpct,
                     yplus_achieved=w["yplus"],
                     alphaEff_factor=w["alphaEff_factor"],
                     outside_wall_function_validity=inval,
                     exceeds_band=diff > bpct))
            note = (f"  ** y+ = {w['yplus']:.1f} is below {WF_YPLUS_FLOOR:.0f}: "
                    "outside the wall function's own validity, REPORTED not graded"
                    if inval else "")
            print(f"    wall functions: Nu = {w['Nu']:.3f} (y+ = {w['yplus']:.1f},"
                  f" alphaEff factor {w['alphaEff_factor']:.3f}) differs from "
                  f"resolved by {diff:.2f} % against a band of {bpct:.2f} %"
                  f"{note}")

    # trivial baseline
    c = m_all("C_lam")
    s10 = ref[f"{1.0e4:.0f}"]
    cdev = 100.0 * abs(c["Nu"] - s10["reference"]) / s10["reference"]
    met = cdev > 100.0 * s10["band"] / s10["reference"]
    out["controls"].append(dict(control="C_lam", Nu=c["Nu"],
                                reference=s10["reference"],
                                deviation_pct=cdev, must="FAIL", met=met))
    print(f"\nC_lam (turbulence OFF, the Charter 2c trivial baseline): "
          f"Nu = {c['Nu']:.3f} vs reference {s10['reference']:.3f}, "
          f"{cdev:.1f} %  -> {'MET (fails, as it must)' if met else 'NOT MET'}")

    with open(os.path.join(HERE, "gate_t1b.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)

    fails = [r for r in out["rows"] if r["verdict"] == "GATE FAIL"]
    nres = [r for r in out["rows"] if r["verdict"] == "NOT A RESULT"]
    graded = [r for r in out["rows"] if r["verdict"] in ("PASS", "GATE FAIL")]
    print(f"\n{'-'*72}")
    print(f"  {len(graded)} graded rows: {len(fails)} GATE FAIL, "
          f"{len(nres)} NOT A RESULT")
    print("  The band is the DISAGREEMENT between two correlations, not either")
    print("  one's own accuracy.  Inside it means consistent with the canon,")
    print("  NOT verified to that tolerance.")
    return EXIT_FAIL if fails else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
