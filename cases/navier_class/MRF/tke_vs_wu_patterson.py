#!/usr/bin/env python3
"""MRF PAPER PARITY -- INDEPENDENT MEASURED-TIER CHECK, added by a cfd lab-lane.

WHAT THIS MEASURES.  The paper's only EXTERNAL EXPERIMENTAL anchor is Wu & Patterson
(1989) LDA velocity and TKE -- it reports no measured power number at all
(MRF_PAPER_REGISTRATION_REID2025.md sec.2.3).  So the honest question about our solve is
not only "how far is our Np from their CFD band" but "how far is our TKE from the
EXPERIMENT, compared with how far THEIR CFD is from the same experiment".  This script
answers exactly that and nothing else.

IT IS NOT A GATE AND REGISTERS NONE.  MRF_PAPER_REGISTRATION_REID2025.md sec.3.1 records
the Wu & Patterson TKE comparison as a measured-tier check with NO band registered.  This
script therefore prints deviations; it produces no PASS, no GATE FAIL and no verdict.

RULE 3.  Both readers are exercised by a planted perturbation written into a COPY ON
DISK, re-read THROUGH THE SAME reader the numbers come from, and the script REFUSES
(exit 2) unless the reader moves by the planted amount.  A zero from a reader not shown
able to see a non-zero is not evidence.

REFUSE-NOT-DEGRADE: exit 2 on bad input or a bad control; exit 0 only with a result.
Reads inputs only; sends nothing, commits nothing, launches nothing.
"""
import json, math, os, sys, tempfile

PLANT = 1.234e-03
EXIT_REFUSE = 2
REPO = "/home/ubuntu/Certonomous"
PARITY = f"{REPO}/verification/runs/navier_class/MRF/R2/PAPER_PARITY"
RESULTS = f"{PARITY}/PAPER_PARITY_RESULTS.json"
DIGI = f"{PARITY}/REID2025_FIG16_DIGITISED.json"
STATION = "0.0538"          # r/D = 0.538, the station matched to the paper's r = 5 cm


def refuse(msg):
    sys.stderr.write("REFUSE (exit 2): " + msg + "\n")
    sys.exit(EXIT_REFUSE)


def read_ours(path, station=STATION):
    """Reader A: our fine-level k/Utip^2 profile, as (2z/W, k) pairs."""
    try:
        j = json.load(open(path))
    except Exception as e:
        refuse(f"{path}: unreadable ({e})")
    try:
        s = j["levels"]["fine"]["profiles"][station]
    except KeyError:
        refuse(f"{path}: no fine-level profile at station {station}")
    z, k = s["two_z_over_W"], s["k_over_Utip2"]
    if not z or len(z) != len(k):
        refuse(f"{path}: station {station} z/k arrays absent or mismatched")
    return list(zip(z, k))


def read_reference(path):
    """Reader B: the digitised Wu & Patterson LDA points and the paper's Zone 1 curve."""
    try:
        j = json.load(open(path))
    except Exception as e:
        refuse(f"{path}: unreadable ({e})")
    lda = j.get("wu_patterson_1989_LDA")
    zone = j.get("paper_MRF_Zone1_curve")
    if not lda:
        refuse(f"{path}: no wu_patterson_1989_LDA points")
    if not zone:
        refuse(f"{path}: no paper_MRF_Zone1_curve")
    for p in lda:
        for key in ("two_z_over_W", "k_over_Utip2", "half_width_k_over_Utip2"):
            if p.get(key) is None:
                refuse(f"{path}: an LDA point is missing '{key}' -- a missing error bar "
                       f"cannot silently become a zero-width one")
    return lda, zone


def interp(curve, x):
    """Linear interpolation onto x; REFUSES rather than extrapolating."""
    pts = sorted(curve)
    if x < pts[0][0] or x > pts[-1][0]:
        return None
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 if x1 == x0 else y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return None


def deviations(curve, lda):
    """Per-point deviation of `curve` from the LDA points, in units of the LDA point's
    OWN stated half-width.  Points outside the curve's span are reported as absent."""
    rows, covered = [], 0
    for p in lda:
        x, y, hw = p["two_z_over_W"], p["k_over_Utip2"], p["half_width_k_over_Utip2"]
        v = interp(curve, x)
        if v is None:
            rows.append(dict(two_z_over_W=x, lda=y, model=None,
                             state="OUTSIDE THE CURVE'S SPAN -- not evaluated, not zero"))
            continue
        covered += 1
        rows.append(dict(two_z_over_W=x, lda=y, model=v, abs_dev=v - y,
                         rel_dev_pct=100.0 * (v - y) / y,
                         dev_in_half_widths=(v - y) / hw,
                         inside_error_bar=abs(v - y) <= hw))
    if covered == 0:
        refuse("no LDA point falls inside the curve's span -- nothing was compared, and "
               "an empty comparison is not a zero deviation")
    ev = [r for r in rows if r.get("model") is not None]
    rms = math.sqrt(sum(r["abs_dev"] ** 2 for r in ev) / len(ev))
    rms_hw = math.sqrt(sum(r["dev_in_half_widths"] ** 2 for r in ev) / len(ev))
    return rows, dict(n_points=len(lda), n_evaluated=len(ev),
                      n_inside_error_bar=sum(1 for r in ev if r["inside_error_bar"]),
                      rms_abs=rms, rms_in_half_widths=rms_hw,
                      mean_signed_rel_pct=sum(r["rel_dev_pct"] for r in ev) / len(ev))


def plant_control_ours(path):
    """Plant PLANT into EVERY k value of a COPY of the results file, re-read through
    read_ours, and require every returned k to move by exactly PLANT."""
    j = json.load(open(path))
    s = j["levels"]["fine"]["profiles"][STATION]
    base = list(s["k_over_Utip2"])
    s["k_over_Utip2"] = [v + PLANT for v in base]
    d = tempfile.mkdtemp(prefix="mrf_plant_ours_")
    try:
        p = os.path.join(d, "planted.json")
        json.dump(j, open(p, "w"))
        after = [k for _, k in read_ours(p)]
        if len(after) != len(base):
            return dict(passed=False, why="reader returned a different length")
        deltas = [a - b for a, b in zip(after, base)]
        worst = max(abs(x - PLANT) for x in deltas)
        return dict(passed=worst < 1e-12, planted=PLANT, n_values=len(base),
                    worst_abs_error=worst, reader="read_ours(k_over_Utip2)",
                    artifact=path)
    finally:
        import shutil; shutil.rmtree(d, ignore_errors=True)


def plant_control_reference(path):
    """Plant PLANT into EVERY Zone-1 curve ordinate of a COPY, re-read through
    read_reference, and require the DEVIATION STATISTIC to move -- the number the
    conclusion is actually built on, not merely the raw array."""
    j = json.load(open(path))
    base_zone = [(p["two_z_over_W"], p["k_over_Utip2"]) for p in j["paper_MRF_Zone1_curve"]]
    for p in j["paper_MRF_Zone1_curve"]:
        p["k_over_Utip2"] = p["k_over_Utip2"] + PLANT
    d = tempfile.mkdtemp(prefix="mrf_plant_ref_")
    try:
        p = os.path.join(d, "planted.json")
        json.dump(j, open(p, "w"))
        lda_p, zone_p = read_reference(p)
        zp = [(q["two_z_over_W"], q["k_over_Utip2"]) for q in zone_p]
        _, s_base = deviations(base_zone, lda_p)
        _, s_plant = deviations(zp, lda_p)
        moved = s_plant["mean_signed_rel_pct"] - s_base["mean_signed_rel_pct"]
        # the mean signed relative deviation must rise by PLANT/lda averaged over points
        ev = [q for q in lda_p if interp(base_zone, q["two_z_over_W"]) is not None]
        expect = 100.0 * sum(PLANT / q["k_over_Utip2"] for q in ev) / len(ev)
        return dict(passed=abs(moved - expect) < 1e-9, planted=PLANT,
                    statistic="mean_signed_rel_pct of the Zone-1 curve vs the LDA points",
                    expected_move_pct=expect, observed_move_pct=moved,
                    reader="read_reference -> deviations", artifact=path)
    finally:
        import shutil; shutil.rmtree(d, ignore_errors=True)


def main():
    c1 = plant_control_ours(RESULTS)
    if not c1["passed"]:
        refuse(f"planted-zero control on OUR profile reader did not behave: {c1}")
    c2 = plant_control_reference(DIGI)
    if not c2["passed"]:
        refuse(f"planted-zero control on the REFERENCE reader did not behave: {c2}")

    ours = read_ours(RESULTS)
    lda, zone = read_reference(DIGI)
    zone_pts = [(p["two_z_over_W"], p["k_over_Utip2"]) for p in zone]

    rows_ours, stat_ours = deviations(ours, lda)
    rows_zone, stat_zone = deviations(zone_pts, lda)

    out = dict(
        what=("k/Utip^2 at the station matched to the paper's r = 5 cm (r/D = 0.538), "
              "our FINE level and the paper's MRF Zone 1 curve, each measured against "
              "the SAME 11 digitised Wu & Patterson (1989) LDA points"),
        NOT_A_GATE=("No band is registered for this comparison "
                    "(MRF_PAPER_REGISTRATION_REID2025.md sec.3.1). These are deviations, "
                    "not a verdict. No PASS, no GATE FAIL is produced or implied."),
        station=STATION, plant=PLANT,
        planted_controls=dict(ours=c1, reference=c2),
        ours_vs_LDA=stat_ours, paper_Zone1_vs_LDA=stat_zone,
        per_point_ours=rows_ours, per_point_paper_Zone1=rows_zone,
        caveat=("DIFFERENT TANKS. Wu & Patterson and Reid 2025 are T = 0.27 m, D = 0.093 m, "
                "Re 28,830; ours is T = 0.30 m, D = 0.100 m, Re 50,000, with 3x wider "
                "baffles and 4x thicker blades relative to D. NO MATCH IS EXPECTED and "
                "none is claimed. A smaller deviation here is NOT evidence that our solve "
                "is better; it is one number, on one profile, between two tanks that "
                "differ."))
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
