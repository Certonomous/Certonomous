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

REVISION 2026-09-12, ON THE CFD-SUPERVISOR'S CHECK-1 READ OF REVISION 1.  Two required
additions; NO result, statistic or caveat of revision 1 is removed.

  A.  THE TWO PLANTED CONTROLS WERE ASYMMETRIC AND THE WEAKER ONE GUARDED THE NUMBER
      THAT FLATTERS US.  Revision 1 planted into OUR array and checked only that the
      array moved, while the REFERENCE control planted into the conclusion's statistic.
      Ours is the side reporting 7 of 11 inside the error bar.  Both controls now run
      BOTH limbs -- a RAW-ARRAY limb and a STATISTIC limb with a predicted expected move
      -- and both refuse on either limb.  A plant that only proves the array changed does
      not prove the conclusion's reader saw it, and that standard now applies to our own
      side too.

  B.  DIGITISATION UNCERTAINTY ON THE ZONE-1 CURVE, WHICH REVISION 1 TREATED AS EXACT.
      The one-sided-sign claim is exactly what a small systematic digitisation offset
      would manufacture.  This revision answers it two ways: an ANALYTIC invariance
      argument (sec. `calibration_invariance`) and an EMPIRICAL per-point reading band
      measured from the digitiser's own known-truth error bars (`digitisation_band`),
      then reports how many points' signs survive it.
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


def _expected_stat_move(curve, lda):
    """A uniform +PLANT on a curve shifts its interpolated value at every LDA abscissa by
    exactly PLANT, so mean_signed_rel_pct must rise by 100*mean(PLANT/k_lda) over the
    points that are actually EVALUATED.  Computed from the UNPLANTED curve."""
    ev = [q for q in lda if interp(curve, q["two_z_over_W"]) is not None]
    if not ev:
        refuse("expected-move cannot be formed: no LDA point is evaluated")
    return 100.0 * sum(PLANT / q["k_over_Utip2"] for q in ev) / len(ev)


def plant_control_ours(path, lda):
    """TWO LIMBS, and the control FAILS if either fails.

    LIMB 1 (raw array): PLANT into EVERY k of a COPY on disk, re-read through read_ours,
    every returned value must move by exactly PLANT.
    LIMB 2 (the statistic the conclusion is built on): the OURS_VS_LDA mean signed
    relative deviation must move by the PREDICTED amount.  Added 2026-09-12 because
    limb 1 alone is the weaker form this script already rejected on the reference side,
    and it was guarding the side of the comparison that flatters us."""
    j = json.load(open(path))
    st = j["levels"]["fine"]["profiles"][STATION]
    base = list(st["k_over_Utip2"])
    base_curve = list(zip(st["two_z_over_W"], base))
    st["k_over_Utip2"] = [v + PLANT for v in base]
    d = tempfile.mkdtemp(prefix="mrf_plant_ours_")
    try:
        p = os.path.join(d, "planted.json")
        json.dump(j, open(p, "w"))
        planted_curve = read_ours(p)
        after = [k for _, k in planted_curve]
        if len(after) != len(base):
            return dict(passed=False, why="reader returned a different length")
        worst = max(abs((a - b) - PLANT) for a, b in zip(after, base))
        limb1 = dict(limb="raw array", passed=worst < 1e-12, n_values=len(base),
                     worst_abs_error=worst, reader="read_ours(k_over_Utip2)")
        _, s_base = deviations(base_curve, lda)
        _, s_plant = deviations(planted_curve, lda)
        moved = s_plant["mean_signed_rel_pct"] - s_base["mean_signed_rel_pct"]
        expect = _expected_stat_move(base_curve, lda)
        limb2 = dict(limb="the conclusion's statistic", passed=abs(moved - expect) < 1e-9,
                     statistic="mean_signed_rel_pct of OUR curve vs the LDA points",
                     expected_move_pct=expect, observed_move_pct=moved,
                     reader="read_ours -> deviations")
        return dict(passed=limb1["passed"] and limb2["passed"], planted=PLANT,
                    artifact=path, limbs=[limb1, limb2])
    finally:
        import shutil; shutil.rmtree(d, ignore_errors=True)


def plant_control_reference(path):
    """The SAME TWO LIMBS as plant_control_ours, on the Zone-1 curve: raw array, and the
    deviation statistic the conclusion is actually built on.  Fails if either fails."""
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
        worst = max(abs((a[1] - b[1]) - PLANT) for a, b in zip(zp, base_zone))
        limb1 = dict(limb="raw array", passed=worst < 1e-12, n_values=len(base_zone),
                     worst_abs_error=worst, reader="read_reference(paper_MRF_Zone1_curve)")
        _, s_base = deviations(base_zone, lda_p)
        _, s_plant = deviations(zp, lda_p)
        moved = s_plant["mean_signed_rel_pct"] - s_base["mean_signed_rel_pct"]
        expect = _expected_stat_move(base_zone, lda_p)
        limb2 = dict(limb="the conclusion's statistic", passed=abs(moved - expect) < 1e-9,
                     statistic="mean_signed_rel_pct of the Zone-1 curve vs the LDA points",
                     expected_move_pct=expect, observed_move_pct=moved,
                     reader="read_reference -> deviations")
        return dict(passed=limb1["passed"] and limb2["passed"], planted=PLANT,
                    artifact=path, limbs=[limb1, limb2])
    finally:
        import shutil; shutil.rmtree(d, ignore_errors=True)


# =====================================================================================
# ADDITION B -- DIGITISATION UNCERTAINTY.  Revision 1 treated the digitised Zone-1
# ordinates as EXACT and banded only the LDA points at their 15 %.  A one-sided sign at
# 11 of 11 points is precisely what a small systematic digitisation offset would
# manufacture, so it is answered here rather than left for a hostile reader.
# =====================================================================================
TRUE_BAR_PCT = 15.0      # Wu & Patterson TKE uncertainty, as the paper states it


def calibration_invariance():
    """ANALYTIC LIMB, and it is the stronger of the two.

    Both the LDA markers and the Zone-1 polyline are recovered from the SAME PDF content
    stream and mapped through the SAME affine calibration
        k(x) = XV0 + (x - X0) * s,   s = (XV1 - XV0) / (X1 - X0)
    (digitise_reid2025_fig16.py, `xs`).  Therefore:

      * OFFSET error.  If X0 is wrong by d, EVERY recovered k shifts by -d*s, both
        curves alike.  The DIFFERENCE (Zone1 - LDA) is EXACTLY unchanged.  A calibration
        offset cannot create, destroy or flip a single sign.
      * SCALE error.  If s is wrong by a factor (1+e), every k -- and so the difference
        -- is multiplied by (1+e).  A positive factor cannot change a sign; it changes
        only the magnitude.

    So the ONE-SIDED SIGN RESULT IS INVARIANT UNDER ANY AFFINE CALIBRATION ERROR BY
    CONSTRUCTION.  What remains is per-point reading noise, which the empirical band
    below measures.  This is an argument about the reader's algebra, not a measurement,
    and is labelled as such."""
    return dict(
        kind="ANALYTIC, not a measurement",
        offset_error="difference EXACTLY unchanged; cannot alter any sign",
        scale_error="difference scaled by a POSITIVE factor; cannot alter any sign",
        conclusion=("the one-sided sign result is invariant under any affine axis "
                    "calibration error, because both curves pass through the identical "
                    "transform read from the identical content stream"),
        residual="per-point reading noise only -- measured empirically below")


def digitisation_band(lda):
    """EMPIRICAL LIMB, from the digitiser's OWN KNOWN-TRUTH check.

    Every LDA error bar in this figure has a true half-width of EXACTLY 15.0 % of its
    own centre (the paper states it), so the recovered `half_width_pct` has a KNOWN
    TRUTH and its departure from 15.0 is the digitiser's reading error, measured rather
    than asserted.  ALL of that departure is attributed to the ORDINATE k -- the
    conservative direction, since some of it certainly belongs to the cap positions."""
    devs = []
    for p in lda:
        hp = p.get("half_width_pct")
        if hp is None:
            refuse("an LDA point carries no half_width_pct -- the digitisation band "
                   "cannot be measured and is NOT assumed")
        devs.append(abs(hp - TRUE_BAR_PCT))
    worst_rel = max(devs) / TRUE_BAR_PCT
    return dict(kind="EMPIRICAL, from the digitiser's known-truth 15 % bars",
                n_bars=len(devs), worst_abs_dev_pct_points=max(devs),
                mean_abs_dev_pct_points=sum(devs) / len(devs),
                worst_relative_reading_error=worst_rel,
                applied_to_a_difference=2.0 * worst_rel,
                applied_to_a_difference_why=(
                    "the difference (Zone1 - LDA) carries a reading error on BOTH "
                    "ordinates, summed rather than added in quadrature -- the "
                    "conservative direction"),
                transfer_caveat=(
                    "this band is measured on the LDA MARKERS and transferred to the "
                    "Zone-1 POLYLINE, which the known-truth check cannot reach. The "
                    "transfer is an assumption, stated, not a measurement."))


def sign_robustness(rows, band):
    """How many of the per-point signs survive the empirical digitisation band."""
    tol = band["applied_to_a_difference"]
    out, survive = [], 0
    for r in rows:
        if r.get("model") is None:
            out.append(dict(two_z_over_W=r["two_z_over_W"], state=r["state"]))
            continue
        rel = abs(r["abs_dev"]) / r["lda"]
        ok = rel > tol
        survive += ok
        out.append(dict(two_z_over_W=r["two_z_over_W"],
                        excess_as_frac_of_lda=rel, band=tol,
                        sign_survives_digitisation=ok,
                        sign="+" if r["abs_dev"] > 0 else "-"))
    ev = [r for r in rows if r.get("model") is not None]
    pos = sum(1 for r in ev if r["abs_dev"] > 0)
    return dict(n_evaluated=len(ev), n_positive=pos, n_negative=len(ev) - pos,
                n_signs_surviving_band=survive, band_used=tol, per_point=out)


def main():
    lda, zone = read_reference(DIGI)          # needed by BOTH controls' statistic limbs
    c1 = plant_control_ours(RESULTS, lda)
    if not c1["passed"]:
        refuse(f"planted-zero control on OUR profile reader did not behave: {c1}")
    c2 = plant_control_reference(DIGI)
    if not c2["passed"]:
        refuse(f"planted-zero control on the REFERENCE reader did not behave: {c2}")

    ours = read_ours(RESULTS)
    zone_pts = [(p["two_z_over_W"], p["k_over_Utip2"]) for p in zone]

    rows_ours, stat_ours = deviations(ours, lda)
    rows_zone, stat_zone = deviations(zone_pts, lda)

    band = digitisation_band(lda)
    robust_zone = sign_robustness(rows_zone, band)
    robust_ours = sign_robustness(rows_ours, band)

    out = dict(
        what=("k/Utip^2 at the station matched to the paper's r = 5 cm (r/D = 0.538), "
              "our FINE level and the paper's MRF Zone 1 curve, each measured against "
              "the SAME 11 digitised Wu & Patterson (1989) LDA points"),
        NOT_A_GATE=("No band is registered for this comparison "
                    "(MRF_PAPER_REGISTRATION_REID2025.md sec.3.1). These are deviations, "
                    "not a verdict. No PASS, no GATE FAIL is produced or implied."),
        station=STATION, plant=PLANT,
        planted_controls=dict(ours=c1, reference=c2),
        calibration_invariance=calibration_invariance(),
        digitisation_band=band,
        sign_robustness_paper_Zone1=robust_zone,
        sign_robustness_ours=robust_ours,
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
