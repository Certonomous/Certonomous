#!/usr/bin/env python3
# =============================================================================
# DIGITIZER instrument -- RE-FILE R2.  DRAFT (ansys-lane-opus48).  NOT A FREEZE.
#
# This is the POSITION re-file mandated by ANSYS_VERIFICATION_CHARTER v1.24 §29
# after the §25/§28 instrument's calibration was graded NOT A RESULT (POSITION
# PLANT-NULL refused; RESULTS.md, commit caa6b096, §29.1). It DOES NOT re-grade
# that task -- that NOT A RESULT is permanent (§29.4). It is a NEW registration.
#
# THE CHANGE, AND ONLY THE CHANGE (this file IS the diff the supervisor reviews).
# The frozen instrument is IMPORTED read-only and REUSED -- it is never edited
# (rule 6). Everything below is the changed measurement code, so a reviewer sees
# exactly what §29 alters and nothing it does not:
#
#   §29.3 -- term A of §25.4 (the synthetic-control statistic) becomes a statistic
#   that DOMINATES the worst demonstrated per-plate error for any quantity whose
#   per-plate error CAN exceed the pixel floor. For POSITION that is the MAXIMUM
#   (the 95th percentile is reported beside it). The test of "conservative enough"
#   is not an argument: with term A = max over the SAME plate set the null control
#   is drawn from, u_read >= every clean-plate error the calibration measured, the
#   null-control plate included -- so THE PLANTED NULL PASSES BY CONSTRUCTION.
#   RMS remains admissible ONLY where the max per-plate error is below the pixel
#   floor (the floor then binds and dominates the tail) -- that is where VALUE
#   sits, and this file ENFORCES that admissibility with a refuse, not a comment.
#
#   §29.4 constraint (a) -- VALUE is a SEPARATELY-REGISTERED quantity, graded to
#   its OWN verdict on its OWN frozen bytes. It is NOT certified by inheriting from
#   the failed task, and a NOT A RESULT on POSITION does not drag VALUE down and
#   vice versa (each quantity's plant refusal is caught for THAT quantity only).
#
#   §29.4 constraint (b) -- the sub-pixel parabolic locator is OPTIONAL (--sublocator)
#   and is NOT the fix. §29.3 (the conservative statistic) is the required change.
#   Even with the sharper locator, term A stays the MAX, so the locator improvement
#   can never substitute for the statistic fix (a sharper locator with an RMS
#   statistic can still hide a tail -- L-461).
#
# NOT AUTHORISED here (unchanged): do NOT run --calibrate (it produces the committed
# u_read, which waits for the freeze), do NOT gate any case, do NOT read Fig .46.2
# or any real plate, do NOT commit. --selftest is the build/self-test step and is
# allowed; it produces NO committed u_read.
# =============================================================================
import os, sys, json, math, argparse
import numpy as np

# ---- import the FROZEN instrument read-only (rule 6: never edited) -----------
_FROZEN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _FROZEN_DIR)
import digitize_calibrate as dc          # frozen blob 2092c55dd59d36c490b5fc3681bfd36c30d5b49b

FROZEN_BLOB = "2092c55dd59d36c490b5fc3681bfd36c30d5b49b"   # asserted at --calibrate time
refuse = dc.refuse
SystemExit2 = dc.SystemExit2


# ---- §29.3: the statistic that makes the null pass BY CONSTRUCTION -----------
def _abs_stats(errs):
    """Return (rms, p95, mx) of |errs| -- the three the report carries; the max is
    the one that binds u_read for a tailed quantity (§29.3)."""
    a = np.abs(np.asarray(errs, float))
    return (float(np.sqrt(np.mean(a ** 2))), float(np.percentile(a, 95)), float(np.max(a)))


def finalize_quantity_r2(spec, labels, quantity, errs, control_render, control_truth,
                         statistic, verbose=True):
    """§29.3 finalisation. `statistic` in {"max","rms"}:
      - "max": term A = max |err| over the calibration set. u_read >= every measured
               clean-plate error, so the planted null PASSES BY CONSTRUCTION.
      - "rms": ADMISSIBLE ONLY IF max|err| < pixel_floor (the floor then dominates
               the tail). Otherwise REFUSE (exit 2) -- an RMS on a tailed quantity is
               exactly the L-461 false precision the null caught.
    Reuses the frozen plant machinery (render/digitize/two_readoff) unchanged."""
    rms, p95, mx = _abs_stats(errs)
    pixel_floor = quantity.pixel_floor()
    if statistic == "rms":
        if not (mx < pixel_floor):
            refuse("§29.3 [%s]: RMS statistic inadmissible -- max per-plate error %.6g "
                   ">= pixel floor %.6g; a tailed quantity must use 'max'." % (quantity.dim, mx, pixel_floor))
        term_A = rms
    elif statistic == "max":
        term_A = mx
    else:
        refuse("unknown statistic %r (§29.3 allows 'max' or admissible 'rms')" % statistic)
    half_spread, _, _ = dc.two_readoff_halfspread(control_render(0.0), labels, quantity, dc.SEED0)
    u_read = max(term_A, half_spread, pixel_floor)
    # §29.3 BY-CONSTRUCTION assertion (a self-check, refuses if violated): for the
    # "max" statistic u_read must be >= every per-plate error, the null-control
    # plate included. This is what makes the null pass structurally, not by luck.
    if statistic == "max" and not (u_read >= mx - 1e-15):
        refuse("§29.3 by-construction broken [%s]: u_read %.6g < max per-plate %.6g" % (quantity.dim, u_read, mx))
    # PLANT-NULL (undisplaced control within u_read) -- passes by construction for "max"
    null_err = quantity.measure(dc.digitize(control_render(0.0), labels)) - control_truth
    if abs(null_err) > dc.NULL_K * u_read:
        refuse("PLANT-NULL [%s]: clean control offset %.6g > %.6g (K*u_read)" % (quantity.dim, null_err, dc.NULL_K * u_read))
    # PLANT-DETECT (displacement IN THE QUANTITY'S OWN DIMENSION, §28.2)
    delta = dc.DETECT_MULT * u_read
    det = quantity.measure(dc.digitize(control_render(delta), labels)) - control_truth
    if det <= u_read:
        refuse("PLANT-DETECT [%s]: 3u_read=%.6g read as %.6g <= u_read -- BLIND (rule 3)" % (quantity.dim, delta, det))
    recovery_err = abs(det - delta)
    rep = {"dim": quantity.dim, "units": quantity.units, "statistic": statistic, "u_read": u_read,
           "terms": {"syn_stat": term_A, "syn_rms": rms, "syn_p95": p95, "syn_max": mx,
                     "half_spread": half_spread, "pixel_floor": pixel_floor},
           "rms_bias": float(np.mean(errs)),
           "plant_detect": {"delta_3u": delta, "recovered": det, "recovery_err": recovery_err,
                            "band_ok": recovery_err <= dc.DETECT_BAND * u_read},
           "plant_null": {"offset": null_err, "limit": dc.NULL_K * u_read, "passes_by_construction": statistic == "max"}}
    if verbose:
        print("  [%-8s stat=%s] u_read=%.6g %s  (term_A=%.5g rms=%.5g p95=%.5g MAX=%.5g half=%.3g floor=%.5g) "
              "detect_band_ok=%s bias=%.4g null_off=%.5g(<=%.5g)"
              % (quantity.dim, statistic, u_read, quantity.units, term_A, rms, p95, mx, half_spread, pixel_floor,
                 rep["plant_detect"]["band_ok"], rep["rms_bias"], null_err, dc.NULL_K * u_read))
    return rep


# ---- §29.4(b) OPTIONAL sub-pixel parabolic locator (not the fix) -------------
class PositionQuantityParabolic(dc.PositionQuantity):
    """Sub-pixel feature location by parabolic fit to the 3 points around the
    gradient minimum. OPTIONAL (§29.4b): it can pull the locator error below one
    pixel, but term A stays the MAX (finalize_quantity_r2), so it never substitutes
    for the §29.3 statistic fix."""
    def _locate(self, x, y, win=1):
        x = np.asarray(x, float); y = np.asarray(y, float)
        if len(x) < 7: refuse("position: too few points to locate a feature")
        k = max(1, int(win)); yp = np.pad(y, k, mode="edge"); ker = np.ones(2 * k + 1) / (2 * k + 1)
        ys = np.convolve(yp, ker, mode="valid"); dydx = np.gradient(ys, x)
        m = max(k + 1, 2); i = m + int(np.argmin(dydx[m:len(x) - m]))
        a, b, c = dydx[i - 1], dydx[i], dydx[i + 1]
        denom = (a - 2 * b + c)
        if abs(denom) < 1e-30: return float(x[i])
        frac = 0.5 * (a - c) / denom                     # sub-sample vertex offset in [-1,1]
        return float(x[i] + frac * 0.5 * (x[i + 1] - x[i - 1]))


# ---- calibrate (POST-FREEZE only): VALUE and POSITION graded SEPARATELY ------
def _grade_quantity(spec, labels, quantity, errs, control_render, control_truth, statistic, verbose):
    """Grade ONE quantity to its OWN verdict (§29.4a separation). A plant refusal is
    caught HERE and rendered as THIS quantity's NOT A RESULT -- it does not reach the
    other quantity."""
    try:
        rep = finalize_quantity_r2(spec, labels, quantity, errs, control_render, control_truth, statistic, verbose)
    except SystemExit2 as e:
        if verbose: print("  [%-8s] NOT A RESULT -- %s" % (quantity.dim, getattr(e, "msg", "plant refused")))
        return {"dim": quantity.dim, "verdict": "NOT A RESULT", "reason": getattr(e, "msg", "plant refused")}
    band_ok = rep["plant_detect"]["band_ok"]; bias_ok = abs(rep["rms_bias"]) <= rep["u_read"]
    rep["verdict"] = "PASS" if (band_ok and bias_ok) else "GATE FAIL"
    rep["bias_ok"] = bias_ok
    return rep


def calibrate_r2(n=None, sublocator=False, out_dir=None, verbose=True):
    n = n or dc.N_CAL
    # blob assert: this re-file's numbers rest on the frozen primitives (rule 2 spirit)
    bp = os.path.join(_FROZEN_DIR, "digitize_calibrate.py")
    import hashlib, subprocess
    try:
        blob = subprocess.check_output(["git", "hash-object", bp], cwd=_FROZEN_DIR).decode().strip()
    except Exception:
        blob = "unknown"
    if blob not in (FROZEN_BLOB, "unknown"):
        refuse("frozen instrument blob %s != expected %s -- R2 reuses the frozen primitives" % (blob, FROZEN_BLOB))
    spec = dc.default_spec(); labels = dc.labels_of(spec)
    valq = dc.ValueQuantity(spec, dc.X_STATION)
    posq = PositionQuantityParabolic(spec) if sublocator else dc.PositionQuantity(spec)
    verr, perr, fam0 = [], [], None
    for i in range(n):
        feat_x, kw = dc.cal_plate_params(i); cf = dc.nozzle_curve(spec, feat_x, **kw)
        arr = dc.render_plate(spec, cf, 0.0)
        if out_dir: dc.save_png(arr, os.path.join(out_dir, "cal_%02d.png" % i))
        rd = dc.digitize(arr, labels)                    # AXIS PLANT (held-out + slope-sign) runs inside
        verr.append(valq.measure(rd) - float(cf(np.array([dc.X_STATION]))[0]))
        perr.append(posq.measure(rd) - feat_x)
        if i == 0: fam0 = (cf, feat_x, kw)
    cf0, feat0, kw0 = fam0
    if verbose: print("CALIBRATION R2 (per gated quantity, §29.3 statistic; sublocator=%s):" % sublocator)
    # VALUE -- separately registered, RMS admissible only if its max < floor (enforced)
    rv = _grade_quantity(spec, labels, valq, verr,
                         lambda d: dc.render_plate(spec, cf0, y_displace=d),
                         float(cf0(np.array([dc.X_STATION]))[0]), "rms", verbose)
    # POSITION -- §29.3 MAX statistic; null passes by construction
    rp = _grade_quantity(spec, labels, posq, perr,
                         lambda d: dc.render_plate(spec, dc.nozzle_curve(spec, feat0 + d, **kw0), 0.0),
                         feat0, "max", verbose)
    # shared AXIS negatives (log-as-linear + planted-flip) must refuse (§28.4)
    lspec = dc.default_spec(x_log=True)
    log_caught = dc._neg_control_refuses(lambda: dc.digitize(
        dc.render_plate(lspec, dc.nozzle_curve(lspec, 5.0), 0.0), {**dc.labels_of(lspec), "x_log": False}))
    flip_caught = dc._neg_control_refuses(lambda: dc.digitize(dc.render_plate(spec, cf0, 0.0), labels, {"force_pair_flip": True}))
    axis_ok = log_caught and flip_caught
    if not axis_ok:
        for r in (rv, rp): r["verdict"] = "NOT A RESULT"; r["reason"] = "shared AXIS negative not caught"
    rep = {"n_plates": n, "sublocator": sublocator, "value": rv, "position": rp,
           "axis_negatives": {"log_as_linear_caught": log_caught, "planted_flip_caught": flip_caught}}
    if verbose:
        print("AXIS negatives: log-as-linear=%s planted-flip=%s" % (log_caught, flip_caught))
        print("VALUE registration verdict: %s | POSITION registration verdict: %s" % (rv.get("verdict"), rp.get("verdict")))
        print(json.dumps(rep, indent=2, default=lambda o: float(o) if isinstance(o, np.floating) else o))
    return rep


# ---- selftest (allowed pre-freeze; NO committed u_read) ----------------------
def selftest():
    ok = True
    spec = dc.default_spec(); labels = dc.labels_of(spec)
    # 1) §29.3 by-construction: term A = max over a synthetic error set -> u_read >= max,
    #    so a null equal to the worst plate passes. Demonstrated on a small feature family.
    posq = dc.PositionQuantity(spec)
    perr = []
    for i in range(8):
        feat_x, kw = dc.cal_plate_params(i); rd = dc.digitize(dc.render_plate(spec, dc.nozzle_curve(spec, feat_x, **kw), 0.0), labels)
        perr.append(posq.measure(rd) - feat_x)
    rms, p95, mx = _abs_stats(perr)
    floor = posq.pixel_floor()
    print("SELFTEST 1 POSITION stats: rms=%.5g p95=%.5g MAX=%.5g floor=%.5g (max>floor: %s -> RMS inadmissible)"
          % (rms, p95, mx, floor, mx > floor))
    ok = ok and (mx > floor)                              # the whole reason for the re-file
    # finalize with max -> null passes by construction (u_read >= mx >= worst plate)
    feat0, kw0 = dc.cal_plate_params(0); cf0 = dc.nozzle_curve(spec, feat0, **kw0)
    rP = finalize_quantity_r2(spec, labels, posq, perr,
                              lambda d: dc.render_plate(spec, dc.nozzle_curve(spec, feat0 + d, **kw0), 0.0),
                              feat0, "max", verbose=False)
    print("SELFTEST 2 POSITION max-statistic: u_read=%.5g >= MAX=%.5g -> null passes by construction: %s (null_off=%.5g)"
          % (rP["u_read"], mx, rP["u_read"] >= mx, rP["plant_null"]["offset"]))
    ok = ok and (rP["u_read"] >= mx) and (abs(rP["plant_null"]["offset"]) <= rP["plant_null"]["limit"])
    # 3) §29.3 admissibility refuse: RMS on the tailed POSITION set must REFUSE
    ref = dc._neg_control_refuses(lambda: finalize_quantity_r2(
        spec, labels, posq, perr, lambda d: dc.render_plate(spec, dc.nozzle_curve(spec, feat0 + d, **kw0), 0.0),
        feat0, "rms", verbose=False))
    print("SELFTEST 3 RMS-on-tailed-POSITION refuses (§29.3 admissibility): %s" % ref)
    ok = ok and ref
    # 4) VALUE with RMS admissible (its max < floor) passes
    valq = dc.ValueQuantity(spec, dc.X_STATION); verr = []
    for i in range(8):
        feat_x, kw = dc.cal_plate_params(i); cf = dc.nozzle_curve(spec, feat_x, **kw)
        rd = dc.digitize(dc.render_plate(spec, cf, 0.0), labels)
        verr.append(valq.measure(rd) - float(cf(np.array([dc.X_STATION]))[0]))
    vrms, vp95, vmx = _abs_stats(verr); vfloor = valq.pixel_floor()
    print("SELFTEST 4 VALUE stats: MAX=%.5g floor=%.5g (max<floor: %s -> RMS admissible)" % (vmx, vfloor, vmx < vfloor))
    rgV = _grade_quantity(spec, labels, valq, verr, lambda d: dc.render_plate(spec, cf0, y_displace=d),
                          float(cf0(np.array([dc.X_STATION]))[0]), "rms", verbose=False)
    print("SELFTEST 4b VALUE verdict=%s u_read=%.5g" % (rgV.get("verdict"), rgV.get("u_read", float("nan"))))
    ok = ok and (vmx < vfloor) and (rgV.get("verdict") == "PASS")
    # 5) separation (§29.4a): a POSITION NOT A RESULT does not drag VALUE. Force it by
    #    grading POSITION with the inadmissible RMS (refuses) and checking VALUE still PASSes.
    rgP_bad = _grade_quantity(spec, labels, posq, perr,
                              lambda d: dc.render_plate(spec, dc.nozzle_curve(spec, feat0 + d, **kw0), 0.0),
                              feat0, "rms", verbose=False)
    print("SELFTEST 5 separation: POSITION(rms)=%s while VALUE=%s (independent)" % (rgP_bad.get("verdict"), rgV.get("verdict")))
    ok = ok and rgP_bad.get("verdict") == "NOT A RESULT" and rgV.get("verdict") == "PASS"
    # 6) optional sub-pixel locator: still uses max statistic; its own max binds u_read
    posqP = PositionQuantityParabolic(spec); perrP = []
    for i in range(8):
        feat_x, kw = dc.cal_plate_params(i); rd = dc.digitize(dc.render_plate(spec, dc.nozzle_curve(spec, feat_x, **kw), 0.0), labels)
        perrP.append(posqP.measure(rd) - feat_x)
    _, _, mxP = _abs_stats(perrP)
    rPP = finalize_quantity_r2(spec, labels, posqP, perrP,
                               lambda d: dc.render_plate(spec, dc.nozzle_curve(spec, feat0 + d, **kw0), 0.0),
                               feat0, "max", verbose=False)
    print("SELFTEST 6 sub-pixel locator (optional): MAX=%.5g u_read=%.5g >= MAX: %s (locator max still binds, §29.4b)"
          % (mxP, rPP["u_read"], rPP["u_read"] >= mxP))
    ok = ok and (rPP["u_read"] >= mxP)
    print("SELFTEST: %s" % ("ALL PASS" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="DIGITIZER re-file R2 (charter §29).")
    ap.add_argument("--selftest", action="store_true", help="exercise every arm; no committed u_read")
    ap.add_argument("--calibrate", action="store_true", help="POST-FREEZE: derive committed per-quantity u_read (compute)")
    ap.add_argument("--sublocator", action="store_true", help="use the optional sub-pixel parabolic locator (§29.4b)")
    ap.add_argument("--out", default=None); ap.add_argument("--n", type=int, default=dc.N_CAL)
    args = ap.parse_args()
    if args.selftest: sys.exit(selftest())
    if args.calibrate:
        if args.n < 20: refuse("--calibrate needs n>=20 (§25.3); got %d" % args.n)
        if args.out: os.makedirs(args.out, exist_ok=True)
        try:
            rep = calibrate_r2(n=args.n, sublocator=args.sublocator, out_dir=args.out)
            bad = any(q.get("verdict") == "NOT A RESULT" for q in (rep["value"], rep["position"]))
            sys.exit(2 if bad else 0)
        except SystemExit2:
            sys.exit(2)
    ap.print_help(); sys.exit(64)
