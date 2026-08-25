#!/usr/bin/env python3
"""D10-F' GRADER -- the finite-difference table for the D10-P' adjoint gradient.

FROZEN INSTRUMENT.  Fixed at the pre-registration commit; verify by hashing this
file against the committed blob before believing anything it prints.

WHAT THIS ARM BUYS AND WHAT IT DOES NOT
---------------------------------------
D10-P' reported `max |d(HFX)/d(patchV)| = 1.9771502962e+02` with NO FINITE-DIFFERENCE
TABLE BESIDE IT, disclaimed in prose as a reachability datum.  `DAFOAM_CHARTER.md` §2:
"No DAFoam gradient enters a record, a report or an optimisation without a
finite-difference table beside it."  This arm buys the table.

**D10-P''s reachability verdict DOES NOT MOVE.**  `GATE REACHED` stands whatever this
grader prints.  This arm converts a disclaimed gradient into a verified or a refuted
one and does nothing else.  It is not a re-grade of D10-P' and cannot become one.

EVERY GRADED QUANTITY IS READ FROM A JSON FILE ON DISK.  Nothing is graded from stdout:
MPI log splicing is a measured defect in this family (commit 79679a84).

THE CONTROLS, AND WHY EACH ONE IS HERE
--------------------------------------
C1  INSTRUMENT IDENTITY.  `d10f_run_script.py` is a THREE-DELTA derivative of the frozen
    `d10p_run_script.py`.  An FD table is a table about D10-P''s gradient only if the
    script that produced it is the same instrument.  The `base` stage re-runs
    compute_totals under the defaults and this grader REFUSES unless BOTH adjoint
    components and HFX reproduce the committed D10-P' values BIT-FOR-BIT.

C2  PLANTED-ZERO, PHYSICAL (CLAUDE.md rule 3).  A `plant` stage carries +1.234 K on the
    heated lower wall's fixedValue boundary -- D10-P''s own proven plant, which is where
    the plant had to move to after D10's plant on the INITIAL field returned exactly
    0.0 because a converged steady solve is independent of its initial guess.  The
    reader must see a response at or above PLANT_FLOOR or this grader REFUSES.

C3  PLANTED-ZERO, READER-LEVEL.  C2 proves the SOLVER responds.  It does not prove THIS
    GRADER'S FD ARITHMETIC responds.  So the grader writes a known offset into a COPY
    of one FD JSON on disk, RE-READS THAT COPY FROM DISK, recomputes the derivative, and
    REFUSES unless the recomputed value moved by the analytically predicted amount.
    A zero from a reader not shown able to see a non-zero is not evidence, and "the
    reader" here is two different readers.

C4  NON-EMPTINESS BY COUNT, PRINTED.  A percentage computed over an empty component set
    is this family's own measured failure (`d3_grade.py` returned PASS at 0.0000 % over
    an empty set).  The usable-step count is printed and a short set REFUSES.

C5  delta_repeat.  A repeat stage at the unperturbed DV.  An FD step sized without
    knowing the run-to-run scatter is a step sized against nothing (N-D15).

EXIT CODES: 0 verdict rendered; 2 REFUSED (a control failed -- the grader refuses rather
than degrading); 3 usage/IO.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import sys
import tempfile

# ---------------------------------------------------------------- frozen constants
# The committed D10-P' reference, from
# /home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D10P/base/d10p_base.json
# and cases/dafoam/ladder-a/A5/curriculum_D10_probe_Pprime/RESULTS.md gate G10-4.
REF_HFX = 2846.286928273276
REF_DHFX_DPATCHV = [197.7150296242168, -37.57503164797164]
REF_COMPONENT = 0                    # patchV[0], the inlet speed; the MAX-|.| component
REF_ADJOINT = REF_DHFX_DPATCHV[REF_COMPONENT]
DV_BASE = 10.0                       # patchV[0] baseline, m/s

# The step sweep, frozen.  Tags are filesystem-safe and map one-to-one onto steps.
STEPS = [("s1", 1.0e-5), ("s2", 1.0e-4), ("s3", 1.0e-3),
         ("s4", 1.0e-2), ("s5", 1.0e-1), ("s6", 5.0e-1)]

MIN_USABLE_STEPS = 4                 # C4: fewer than this REFUSES
MIN_PLATEAU_STEPS = 3                # charter §3: a plateau is >= 3 consecutive steps
PLATEAU_TOL = 1.0e-2                 # adjacent central-FD values within 1 % => plateau
PLANT_FLOOR = 1.0e-6                 # C2 floor, inherited from D10-P' gate G10-3b
PLANT_K = 1.234                      # K added to the lowerWall fixedValue
IDENTITY_TOL = 0.0                   # C1 is BIT-FOR-BIT.  Not a tolerance: a threshold of zero.
READER_PLANT = 7.531e-02             # C3: absolute offset written into a COPY of an FD obj
READER_PLANT_TOL = 1.0e-9            # C3 relative agreement with the analytic prediction

# A DELIBERATE MUTANT SWITCH, exercised only by --selftest.  When set, the C3 probe
# re-reads the ORIGINAL FD file instead of the planted COPY -- i.e. it simulates exactly
# the blindness C3 exists to detect.  A control whose FAILURE path has never been walked
# is a control nobody has shown to work; this switch walks it.
_C3_BLIND = False

# The pre-registered band and the verdict mapping.  DAFOAM_CHARTER.md §2 grades the TABLE
# in three bands; CLAUDE.md rule 1 fixes the VERDICT vocabulary.  The mapping is frozen
# here so it cannot be chosen after the number is seen:
#   table PASS         (err <= 5 %)                       -> verdict PASS
#   table CONDITIONAL  (5 % < err <= 15 %)                -> verdict GATE FAIL   [outside band]
#   table FAIL         (err > 15 %, or a sign flip)       -> verdict GATE FAIL
#   any control refused, or no plateau                    -> verdict NOT A RESULT
BAND_PASS = 5.0e-2
BAND_COND = 1.5e-1


def refuse(msg: str) -> None:
    print("REFUSED: " + msg)
    print("VERDICT: NOT A RESULT")
    sys.exit(2)


def load(path: str) -> dict:
    if not os.path.isfile(path):
        refuse("required artifact absent on disk: %s" % path)
    with open(path) as f:
        try:
            d = json.load(f)
        except Exception as exc:                       # noqa: BLE001
            refuse("unreadable JSON %s: %s" % (path, exc))
    if d.get("status") != "COMPLETE":
        refuse("%s status is %r, not COMPLETE" % (path, d.get("status")))
    return d


def central(hfx_plus: float, hfx_minus: float, h: float) -> float:
    return (hfx_plus - hfx_minus) / (2.0 * h)


def rel(a: float, b: float) -> float:
    """Relative difference of a against reference b.  b == 0 is refused upstream."""
    return abs(a - b) / abs(b)


# ------------------------------------------------------------------------ the grade
def grade(base_dir: str, quiet: bool = False) -> str:
    out = (lambda *a: None) if quiet else (lambda *a: print(*a))

    out("=" * 78)
    out("D10-F'  FINITE-DIFFERENCE TABLE for d(HFX)/d(patchV[%d])" % REF_COMPONENT)
    out("run root: %s" % base_dir)
    out("=" * 78)

    # ---- C1 INSTRUMENT IDENTITY -------------------------------------------------
    b = load(os.path.join(base_dir, "base", "d10f_base.json"))
    if b.get("task") != "compute_totals":
        refuse("base stage task is %r, not compute_totals" % b.get("task"))
    got_d = b.get("dHFX_dpatchV")
    if not isinstance(got_d, list) or len(got_d) != len(REF_DHFX_DPATCHV):
        refuse("base adjoint vector is %r; expected %d components"
               % (got_d, len(REF_DHFX_DPATCHV)))
    for i, (g, r) in enumerate(zip(got_d, REF_DHFX_DPATCHV)):
        if abs(float(g) - r) > IDENTITY_TOL:
            refuse("C1 INSTRUMENT IDENTITY BROKEN: adjoint component %d is %.16e, "
                   "committed D10-P' value is %.16e, delta %.6e (threshold is ZERO). "
                   "The FD table would not be a table about D10-P''s gradient."
                   % (i, float(g), r, abs(float(g) - r)))
    if abs(float(b["HFX"]) - REF_HFX) > IDENTITY_TOL:
        refuse("C1 INSTRUMENT IDENTITY BROKEN: HFX is %.16e, committed %.16e"
               % (float(b["HFX"]), REF_HFX))
    out("\nC1 INSTRUMENT IDENTITY   PASS -- base reproduces D10-P' BIT-FOR-BIT")
    out("   HFX               %.16e  (== committed)" % float(b["HFX"]))
    out("   d(HFX)/d(patchV)  [%s]" % ", ".join("%.10e" % float(v) for v in got_d))
    out("   ADJOINT UNDER TEST, component %d: %.16e" % (REF_COMPONENT, REF_ADJOINT))

    # ---- C5 delta_repeat --------------------------------------------------------
    r0 = load(os.path.join(base_dir, "rep0", "d10f_rep0.json"))
    r1 = load(os.path.join(base_dir, "rep1", "d10f_rep1.json"))
    hfx0, hfx1 = float(r0["HFX"]), float(r1["HFX"])
    if hfx0 == 0.0:
        refuse("delta_repeat reference HFX is exactly zero")
    d_repeat_abs = abs(hfx1 - hfx0)
    d_repeat_rel = d_repeat_abs / abs(hfx0)
    out("\nC5 delta_repeat          MEASURED")
    out("   rep0 HFX %.16e" % hfx0)
    out("   rep1 HFX %.16e" % hfx1)
    out("   delta_repeat  abs %.6e   rel %.6e" % (d_repeat_abs, d_repeat_rel))

    # ---- C2 PLANTED ZERO, PHYSICAL ----------------------------------------------
    p = load(os.path.join(base_dir, "plant", "d10f_plant.json"))
    hfx_p = float(p["HFX"])
    plant_resp = rel(hfx_p, float(b["HFX"]))
    out("\nC2 PLANT, PHYSICAL       +%.3f K on the lowerWall fixedValue" % PLANT_K)
    out("   HFX_base  %.16e" % float(b["HFX"]))
    out("   HFX_plant %.16e" % hfx_p)
    out("   response  %.6e   floor %.6e" % (plant_resp, PLANT_FLOOR))
    if not (plant_resp >= PLANT_FLOOR):
        refuse("C2 PLANTED-ZERO CONTROL FAILED: the reader saw %.6e against a floor of "
               "%.6e.  A zero from a reader not shown able to see a non-zero is not "
               "evidence (CLAUDE.md rule 3)." % (plant_resp, PLANT_FLOOR))
    out("   C2                    PASS")

    # ---- read the sweep ---------------------------------------------------------
    rows = []
    missing = []
    for tag, h in STEPS:
        fp = os.path.join(base_dir, "fdp_" + tag, "d10f_fdp_%s.json" % tag)
        fm = os.path.join(base_dir, "fdm_" + tag, "d10f_fdm_%s.json" % tag)
        if not (os.path.isfile(fp) and os.path.isfile(fm)):
            missing.append(tag)
            continue
        dp, dm = load(fp), load(fm)
        # the DV each stage ACTUALLY used, read back from the stage's own JSON --
        # never assumed from the directory name
        vp, vm = float(dp["patchV"][REF_COMPONENT]), float(dm["patchV"][REF_COMPONENT])
        want_p, want_m = DV_BASE + h, DV_BASE - h
        if abs(vp - want_p) > 1e-12 * max(1.0, abs(want_p)):
            refuse("step %s: fdp ran at patchV[%d]=%.16e, registered %.16e"
                   % (tag, REF_COMPONENT, vp, want_p))
        if abs(vm - want_m) > 1e-12 * max(1.0, abs(want_m)):
            refuse("step %s: fdm ran at patchV[%d]=%.16e, registered %.16e"
                   % (tag, REF_COMPONENT, vm, want_m))
        rows.append({"tag": tag, "h": h, "hp": float(dp["HFX"]), "hm": float(dm["HFX"]),
                     "fd": central(float(dp["HFX"]), float(dm["HFX"]), h),
                     "fp": fp, "fm": fm})

    # ---- C4 NON-EMPTINESS BY COUNT, PRINTED -------------------------------------
    out("\nC4 USABLE FD STEPS       %d of %d registered   (minimum %d)"
        % (len(rows), len(STEPS), MIN_USABLE_STEPS))
    if missing:
        out("   steps with no artifact on disk: %s" % ", ".join(missing))
    if len(rows) < MIN_USABLE_STEPS:
        refuse("C4 SHORT COMPONENT SET: %d usable FD steps, registered minimum %d. "
               "A percentage over a short or empty set is not a result."
               % (len(rows), MIN_USABLE_STEPS))
    out("   C4                    PASS")

    # ---- C3 PLANTED ZERO, READER-LEVEL ------------------------------------------
    probe = rows[len(rows) // 2]
    tmpd = tempfile.mkdtemp(prefix="d10f_readerplant_")
    try:
        copy = os.path.join(tmpd, "planted.json")
        shutil.copyfile(probe["fp"], copy)
        with open(copy) as f:
            j = json.load(f)
        j["HFX"] = float(j["HFX"]) + READER_PLANT
        with open(copy, "w") as f:
            json.dump(j, f, indent=2, sort_keys=True)
        # RE-READ FROM DISK.  Not from the object we just wrote.
        with open(probe["fp"] if _C3_BLIND else copy) as f:
            reread = json.load(f)
        fd_planted = central(float(reread["HFX"]), probe["hm"], probe["h"])
        moved = fd_planted - probe["fd"]
        predicted = READER_PLANT / (2.0 * probe["h"])
        out("\nC3 PLANT, READER-LEVEL   +%.6e written into a COPY of %s, re-read from disk"
            % (READER_PLANT, os.path.basename(probe["fp"])))
        out("   FD before  %.16e" % probe["fd"])
        out("   FD after   %.16e" % fd_planted)
        out("   moved      %.16e   predicted %.16e" % (moved, predicted))
        if predicted == 0.0:
            refuse("C3 predicted movement is zero; the control cannot discriminate")
        if rel(moved, predicted) > READER_PLANT_TOL:
            refuse("C3 READER-LEVEL PLANTED-ZERO CONTROL FAILED: this grader's FD "
                   "arithmetic moved %.16e against a predicted %.16e (rel %.6e, tol "
                   "%.1e).  The reader that produces the FD numbers has not been shown "
                   "able to see a non-zero." % (moved, predicted, rel(moved, predicted),
                                                READER_PLANT_TOL))
        out("   C3                    PASS")
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    # ---- the table --------------------------------------------------------------
    out("\nTHE FD TABLE -- central differences, one component, per-component by construction")
    out("   %-4s %-12s %-22s %-22s %-22s %-12s" %
        ("tag", "h", "HFX(+h)", "HFX(-h)", "central FD", "vs adjoint"))
    for r in rows:
        e = rel(r["fd"], REF_ADJOINT) if REF_ADJOINT != 0.0 else float("nan")
        out("   %-4s %-12.3e %-22.16e %-22.16e %-22.16e %-12.6e"
            % (r["tag"], r["h"], r["hp"], r["hm"], r["fd"], e))

    # ---- the plateau ------------------------------------------------------------
    runs, cur = [], [0]
    for i in range(len(rows) - 1):
        a, bb = rows[i]["fd"], rows[i + 1]["fd"]
        if bb != 0.0 and abs(a - bb) / abs(bb) <= PLATEAU_TOL:
            cur.append(i + 1)
        else:
            runs.append(cur)
            cur = [i + 1]
    runs.append(cur)
    best = max(runs, key=len)
    out("\nPLATEAU  tol %.1e on adjacent central-FD values, minimum run %d steps"
        % (PLATEAU_TOL, MIN_PLATEAU_STEPS))
    out("   longest consecutive run: %d steps -- %s"
        % (len(best), ", ".join(rows[i]["tag"] for i in best)))
    for i in range(len(rows) - 1):
        a, bb = rows[i]["fd"], rows[i + 1]["fd"]
        d = abs(a - bb) / abs(bb) if bb != 0.0 else float("inf")
        out("   adjacent %s->%s  %.6e  %s"
            % (rows[i]["tag"], rows[i + 1]["tag"], d, "IN" if d <= PLATEAU_TOL else "out"))
    if len(best) < MIN_PLATEAU_STEPS:
        print("\nNO PLATEAU: longest consecutive run is %d steps, registered minimum %d."
              % (len(best), MIN_PLATEAU_STEPS))
        print("A step not proved to lie in a plateau is not a proved step "
              "(DAFOAM_CHARTER.md §3).")
        print("VERDICT: NOT A RESULT")
        return "NOT A RESULT"

    # reference step, FIXED BEFORE THE DATA: the middle of the longest plateau run,
    # ties broken toward the SMALLER step (lower index).
    ref_i = best[(len(best) - 1) // 2]
    ref = rows[ref_i]
    out("   REFERENCE STEP (registered rule: middle of the longest run, ties to the "
        "smaller step): %s, h = %.3e" % (ref["tag"], ref["h"]))

    # ---- the gate ---------------------------------------------------------------
    fd = ref["fd"]
    if fd == 0.0:
        refuse("reference-step FD derivative is exactly zero; no relative error is defined")
    err = rel(REF_ADJOINT, fd)
    sign_flip = (REF_ADJOINT * fd) < 0.0
    out("\nTHE GATE -- statistic: single-component relative error |D_adj - D_fd| / |D_fd|")
    out("   (NAMED as a statistic, DAFOAM_CHARTER.md §2.  This is NOT the vector-relative")
    out("    error the ladder's multi-component records quote, and NOT the per-component")
    out("    average the DAFoam papers quote.  One component, one number, named.)")
    out("   adjoint    %.16e" % REF_ADJOINT)
    out("   FD         %.16e   at h = %.3e" % (fd, ref["h"]))
    out("   rel err    %.6e     band PASS <= %.3e" % (err, BAND_PASS))
    out("   sign flip  %s" % ("YES" if sign_flip else "no"))
    out("   delta_repeat rel %.6e -- the FD signal at the reference step is "
        "|HFX(+h)-HFX(-h)|/|HFX| = %.6e"
        % (d_repeat_rel, abs(ref["hp"] - ref["hm"]) / abs(float(b["HFX"]))))

    if sign_flip or err > BAND_COND:
        v = "GATE FAIL"
        why = "sign flip" if sign_flip else "rel err %.6e > %.3e" % (err, BAND_COND)
    elif err > BAND_PASS:
        v = "GATE FAIL"
        why = ("rel err %.6e is in the charter's CONDITIONAL band (%.3e, %.3e] and so is "
               "OUTSIDE the pre-registered PASS band" % (err, BAND_PASS, BAND_COND))
    else:
        v = "PASS"
        why = "rel err %.6e <= %.3e" % (err, BAND_PASS)
    out("\n   %s -- %s" % (v, why))
    print("VERDICT: %s" % v)
    return v


# ------------------------------------------------------------------------- selftest
def _write(d: str, name: str, obj: dict) -> None:
    os.makedirs(os.path.join(d, name), exist_ok=True)
    fn = {"base": "d10f_base.json", "rep0": "d10f_rep0.json", "rep1": "d10f_rep1.json",
          "plant": "d10f_plant.json"}.get(name)
    if fn is None:
        fn = "d10f_%s.json" % name
    with open(os.path.join(d, name, fn), "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)


def _synth(root: str, adj_scale: float = 1.0, plant_resp: float = 2.05e-2,
           n_steps: int = 6, noise: float = 0.0, break_identity: bool = False,
           curvature: float = 0.0) -> None:
    """A synthetic run tree whose FD derivative is REF_ADJOINT * adj_scale."""
    true_slope = REF_ADJOINT * adj_scale
    d = list(REF_DHFX_DPATCHV)
    if break_identity:
        d[0] = d[0] * 1.0000001
    _write(root, "base", {"status": "COMPLETE", "task": "compute_totals",
                          "HFX": REF_HFX, "dHFX_dpatchV": d,
                          "patchV": [DV_BASE, 0.0], "patchV0_arg": DV_BASE})
    _write(root, "rep0", {"status": "COMPLETE", "task": "run_model", "HFX": REF_HFX,
                          "patchV": [DV_BASE, 0.0], "patchV0_arg": DV_BASE})
    _write(root, "rep1", {"status": "COMPLETE", "task": "run_model", "HFX": REF_HFX,
                          "patchV": [DV_BASE, 0.0], "patchV0_arg": DV_BASE})
    _write(root, "plant", {"status": "COMPLETE", "task": "run_model",
                           "HFX": REF_HFX * (1.0 + plant_resp),
                           "patchV": [DV_BASE, 0.0], "patchV0_arg": DV_BASE})
    for k, (tag, h) in enumerate(STEPS[:n_steps]):
        # a deliberate step-dependent wobble so a "no plateau" case can be built
        w = noise / h if noise else 0.0
        hp = REF_HFX + true_slope * h + curvature * h * h + w
        hm = REF_HFX - true_slope * h + curvature * h * h
        _write(root, "fdp_" + tag, {"status": "COMPLETE", "task": "run_model", "HFX": hp,
                                    "patchV": [DV_BASE + h, 0.0], "patchV0_arg": DV_BASE + h})
        _write(root, "fdm_" + tag, {"status": "COMPLETE", "task": "run_model", "HFX": hm,
                                    "patchV": [DV_BASE - h, 0.0], "patchV0_arg": DV_BASE - h})


def _expect(name: str, want: str, c3_blind: bool = False, **kw) -> bool:
    global _C3_BLIND
    root = tempfile.mkdtemp(prefix="d10f_selftest_")
    _C3_BLIND = c3_blind
    try:
        _synth(root, **kw)
        try:
            got = grade(root, quiet=True)
        except SystemExit as e:
            got = "NOT A RESULT" if e.code == 2 else "EXIT %s" % e.code
        ok = got == want
        print("   %-42s want %-13s got %-13s  %s"
              % (name, want, got, "PASS" if ok else "*** FAIL ***"))
        return ok
    finally:
        _C3_BLIND = False
        shutil.rmtree(root, ignore_errors=True)


def selftest() -> int:
    print("D10-F' GRADER SELFTEST -- a selftest that has never been shown able to fail")
    print("is not a selftest.  Each mutant below MUST flip the verdict.\n")
    ok = True
    ok &= _expect("clean tree, adjoint == FD", "PASS")
    ok &= _expect("adjoint 3 % off  (inside PASS band)", "PASS", adj_scale=1.0 / 1.03)
    ok &= _expect("adjoint 8 % off  (CONDITIONAL band)", "GATE FAIL", adj_scale=1.0 / 1.08)
    ok &= _expect("adjoint 40 % off (FAIL band)", "GATE FAIL", adj_scale=1.0 / 1.40)
    ok &= _expect("adjoint SIGN FLIPPED", "GATE FAIL", adj_scale=-1.0)
    ok &= _expect("C2 plant response EXACTLY ZERO", "NOT A RESULT", plant_resp=0.0)
    ok &= _expect("C2 plant response below floor", "NOT A RESULT", plant_resp=1.0e-9)
    ok &= _expect("C4 only 3 steps on disk", "NOT A RESULT", n_steps=3)
    ok &= _expect("C1 instrument identity broken", "NOT A RESULT", break_identity=True)
    ok &= _expect("no plateau (step-dependent wobble)", "NOT A RESULT", noise=1.0e-3)
    ok &= _expect("C3 reader BLINDED to the planted copy", "NOT A RESULT", c3_blind=True)
    print("\n   %s" % ("ALL SELFTESTS PASS" if ok else "*** SELFTEST FAILURE ***"))
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="/home/ubuntu/certonomous-runs/"
                                      "CURRICULUM-PROBES-D10-D11-D12/D10F")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    grade(a.base)
