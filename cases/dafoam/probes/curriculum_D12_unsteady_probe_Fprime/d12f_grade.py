#!/usr/bin/env python3
"""D12-F' GRADER -- the finite-difference table for the D12 probe's UNSTEADY adjoint.

FROZEN INSTRUMENT.  Fixed at the pre-registration commit; verify by hashing this file
against the committed blob before believing anything it prints.

WHAT THIS ARM BUYS AND WHAT IT DOES NOT
---------------------------------------
The D12 probe reported `max |d(obj)/d(shape)| = 1.1622935280e-01` -- obj = time-averaged
CD over a 5-step window on the upstream DAFoam `Cylinder` tutorial -- with NO
FINITE-DIFFERENCE TABLE BESIDE IT, disclaimed in prose as a reachability datum.
`DAFOAM_CHARTER.md` §2 forbids a DAFoam gradient entering a record without the table.
This arm buys it.

**D12's reachability verdict DOES NOT MOVE.**  `GATE REACHED` stands whatever this grader
prints.  This arm converts a disclaimed gradient into a verified or a refuted one and does
nothing else.  It is not a re-grade of the probe and cannot become one.

TWO COMPONENTS ARE BOUGHT, NOT ONE, AND THE SECOND ONE IS THE INTERESTING ONE
----------------------------------------------------------------------------
  idx 3  d(obj)/d(shape[3]) = -1.1622935280e-01 -- the HEADLINE, the max-|.| component,
         and therefore the number §2 actually bites on.
  idx 0  d(obj)/d(shape[0]) = +3.5023163495e-02 -- bought because the probe's own PLANT
         STAGE is already a one-sided FD point on this component and it DISAGREES:
         (obj_plant - obj_base) / 1.234e-03 = 4.5682e-02 against an adjoint 3.5023e-02,
         a 30 % gap.  A one-sided difference at a single large step proves nothing on its
         own -- it is exactly as consistent with curvature as with a wrong gradient.  The
         only way to tell those apart is a CENTRAL difference over a STEP SWEEP, which is
         what this arm runs.  Buying idx 3 alone would have left that gap unexamined
         beside a table, which is worse than leaving it beside a disclaimer.

`DAFOAM_CHARTER.md` §3: "a flat curve is per component or it is not flat."  Every plateau,
every reference step and every relative error below is PER COMPONENT.  No aggregate over
the two is formed, quoted, or implied.

EVERY GRADED QUANTITY IS READ FROM A JSON FILE ON DISK.  Nothing is graded from stdout
(MPI log splicing is a measured defect in this family, commit 79679a84).

THE CONTROLS -- C1..C5 as in d10f_grade.py, with C5 carrying more weight here
----------------------------------------------------------------------------
C1  INSTRUMENT IDENTITY, BIT-FOR-BIT, on all four adjoint components and on obj.
C2  PLANTED-ZERO, PHYSICAL: shape[0] = 1.234e-03, the probe's own proven plant.
C3  PLANTED-ZERO, READER-LEVEL: a known offset written into a COPY of an FD JSON on disk,
    RE-READ FROM DISK, with a refusal if the FD arithmetic does not move as predicted.
    Carries a deliberate blind-reader mutant switch so the FAILURE path is walked.
C4  NON-EMPTINESS BY COUNT, PRINTED, PER COMPONENT.
C5  delta_repeat ON THE TIME-AVERAGE.  This is N-D15 at its worst: a time-averaged
    objective on a shedding flow has run-to-run scatter, and an FD step sized without it
    is sized against nothing.  MEASURED HERE, AND SCOPED HONESTLY: this window is 5 steps
    from a COLD START, not a developed limit cycle.  A delta_repeat measured here is a
    statement about THIS window and is NOT the delta_repeat D12-proper needs.  The grader
    prints that scope beside the number so it cannot be quoted onward stripped of it.

EXIT CODES: 0 verdict rendered; 2 REFUSED; 3 usage/IO.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile

# ---------------------------------------------------------------- frozen constants
# The committed D12 probe reference, from
# /home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D12/base/d12_base.json
REF_OBJ = 0.08990393910381672
REF_DOBJ_DSHAPE = [0.03502316349491921, 0.028868992749916934,
                   0.05233719655030368, -0.11622935279513776]
REF_NSHAPES = 4
COMPONENTS = [3, 0]                  # idx 3 = headline max-|.|; idx 0 = the plant's own

STEPS = [("s1", 1.0e-6), ("s2", 1.0e-5), ("s3", 1.0e-4),
         ("s4", 1.0e-3), ("s5", 1.0e-2)]

MIN_USABLE_STEPS = 4
MIN_PLATEAU_STEPS = 3
PLATEAU_TOL = 1.0e-2
PLANT_FLOOR = 1.0e-9                 # inherited from the probe's own gate G12-3b
PLANT_SHAPE = 1.234e-03
IDENTITY_TOL = 0.0                   # BIT-FOR-BIT.  A threshold of zero, not a tolerance.
READER_PLANT = 3.719e-04
READER_PLANT_TOL = 1.0e-9

BAND_PASS = 5.0e-2
BAND_COND = 1.5e-1

# See d10f_grade.py: a control whose FAILURE path has never been walked is a control
# nobody has shown to work.  --selftest walks it.
_C3_BLIND = False


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


def rel(a: float, b: float) -> float:
    return abs(a - b) / abs(b)


def grade(base_dir: str, quiet: bool = False) -> str:
    out = (lambda *a: None) if quiet else (lambda *a: print(*a))
    out("=" * 78)
    out("D12-F'  FINITE-DIFFERENCE TABLE for the UNSTEADY adjoint d(obj)/d(shape)")
    out("        obj = time-averaged CD, 5-step window, cold start from 0_orig, np=1")
    out("run root: %s" % base_dir)
    out("=" * 78)

    # ---- C1 -----------------------------------------------------------------
    b = load(os.path.join(base_dir, "base", "d12f_base.json"))
    if b.get("task") != "compute_totals":
        refuse("base stage task is %r, not compute_totals" % b.get("task"))
    if int(b.get("nShapes", -1)) != REF_NSHAPES:
        refuse("base nShapes is %r, committed probe value is %d"
               % (b.get("nShapes"), REF_NSHAPES))
    got = b.get("dobj_dshape")
    if not isinstance(got, list) or len(got) != REF_NSHAPES:
        refuse("base adjoint vector is %r; expected %d components" % (got, REF_NSHAPES))
    for i, (g, r) in enumerate(zip(got, REF_DOBJ_DSHAPE)):
        if abs(float(g) - r) > IDENTITY_TOL:
            refuse("C1 INSTRUMENT IDENTITY BROKEN: adjoint component %d is %.16e, "
                   "committed probe value is %.16e, delta %.6e (threshold is ZERO). "
                   "The FD table would not be a table about the probe's gradient."
                   % (i, float(g), r, abs(float(g) - r)))
    if abs(float(b["obj"]) - REF_OBJ) > IDENTITY_TOL:
        refuse("C1 INSTRUMENT IDENTITY BROKEN: obj is %.16e, committed %.16e"
               % (float(b["obj"]), REF_OBJ))
    out("\nC1 INSTRUMENT IDENTITY   PASS -- base reproduces the D12 probe BIT-FOR-BIT")
    out("   obj (time-avg CD) %.16e  (== committed)" % float(b["obj"]))
    out("   d(obj)/d(shape)   [%s]" % ", ".join("%.10e" % float(v) for v in got))

    # ---- C5 delta_repeat ----------------------------------------------------
    r0 = load(os.path.join(base_dir, "rep0", "d12f_rep0.json"))
    r1 = load(os.path.join(base_dir, "rep1", "d12f_rep1.json"))
    o0, o1 = float(r0["obj"]), float(r1["obj"])
    if o0 == 0.0:
        refuse("delta_repeat reference obj is exactly zero")
    d_rep_abs, d_rep_rel = abs(o1 - o0), abs(o1 - o0) / abs(o0)
    out("\nC5 delta_repeat ON THE TIME-AVERAGE   MEASURED")
    out("   rep0 obj %.16e" % o0)
    out("   rep1 obj %.16e" % o1)
    out("   delta_repeat  abs %.6e   rel %.6e" % (d_rep_abs, d_rep_rel))
    out("   SCOPE, STATED SO IT CANNOT BE QUOTED ONWARD WITHOUT IT: this is a 5-step")
    out("   window from a COLD START at np=1, NOT a developed vortex-shedding limit")
    out("   cycle.  It is a statement about THIS window.  It is NOT the delta_repeat")
    out("   that D12-proper's 300-step time-average needs, and must never be reused as")
    out("   one.  Limit-cycle phase noise is a different quantity on a different flow.")

    # ---- C2 -----------------------------------------------------------------
    p = load(os.path.join(base_dir, "plant", "d12f_plant.json"))
    resp = rel(float(p["obj"]), float(b["obj"]))
    out("\nC2 PLANT, PHYSICAL       shape[0] = %.6e" % PLANT_SHAPE)
    out("   obj_base  %.16e" % float(b["obj"]))
    out("   obj_plant %.16e" % float(p["obj"]))
    out("   response  %.6e   floor %.6e" % (resp, PLANT_FLOOR))
    if not (resp >= PLANT_FLOOR):
        refuse("C2 PLANTED-ZERO CONTROL FAILED: the reader saw %.6e against a floor of "
               "%.6e (CLAUDE.md rule 3)." % (resp, PLANT_FLOOR))
    out("   C2                    PASS")

    # ---- per-component sweeps ----------------------------------------------
    verdicts = []
    for idx in COMPONENTS:
        adj = REF_DOBJ_DSHAPE[idx]
        out("\n" + "-" * 78)
        out("COMPONENT %d   adjoint d(obj)/d(shape[%d]) = %.16e" % (idx, idx, adj))
        out("-" * 78)
        rows, missing = [], []
        for tag, h in STEPS:
            fp = os.path.join(base_dir, "c%d_fdp_%s" % (idx, tag),
                              "d12f_c%d_fdp_%s.json" % (idx, tag))
            fm = os.path.join(base_dir, "c%d_fdm_%s" % (idx, tag),
                              "d12f_c%d_fdm_%s.json" % (idx, tag))
            if not (os.path.isfile(fp) and os.path.isfile(fm)):
                missing.append(tag)
                continue
            dp, dm = load(fp), load(fm)
            # what the stage ACTUALLY ran, read back from its own JSON -- never assumed
            # from the directory name
            for who, d, want in (("fdp", dp, h), ("fdm", dm, -h)):
                sv = list(d["shape"])
                if len(sv) != REF_NSHAPES:
                    refuse("step %s %s: shape vector length %d" % (tag, who, len(sv)))
                if abs(float(sv[idx]) - want) > 1e-15 * max(1.0, abs(want)):
                    refuse("step %s %s: ran at shape[%d]=%.16e, registered %.16e"
                           % (tag, who, idx, float(sv[idx]), want))
                for j, v in enumerate(sv):
                    if j != idx and float(v) != 0.0:
                        refuse("step %s %s: shape[%d] is %.16e, must be exactly zero -- "
                               "the FD would not be a partial derivative"
                               % (tag, who, j, float(v)))
            rows.append({"tag": tag, "h": h, "op": float(dp["obj"]), "om": float(dm["obj"]),
                         "fd": (float(dp["obj"]) - float(dm["obj"])) / (2.0 * h),
                         "fp": fp})

        out("\nC4 USABLE FD STEPS       %d of %d registered   (minimum %d)"
            % (len(rows), len(STEPS), MIN_USABLE_STEPS))
        if missing:
            out("   steps with no artifact on disk: %s" % ", ".join(missing))
        if len(rows) < MIN_USABLE_STEPS:
            refuse("C4 SHORT COMPONENT SET on component %d: %d usable FD steps, "
                   "registered minimum %d.  A percentage over a short or empty set is "
                   "not a result." % (idx, len(rows), MIN_USABLE_STEPS))
        out("   C4                    PASS")

        # ---- C3, per component ---------------------------------------------
        probe = rows[len(rows) // 2]
        tmpd = tempfile.mkdtemp(prefix="d12f_readerplant_")
        try:
            copy = os.path.join(tmpd, "planted.json")
            shutil.copyfile(probe["fp"], copy)
            with open(copy) as f:
                j = json.load(f)
            j["obj"] = float(j["obj"]) + READER_PLANT
            with open(copy, "w") as f:
                json.dump(j, f, indent=2, sort_keys=True)
            with open(probe["fp"] if _C3_BLIND else copy) as f:
                reread = json.load(f)
            fd_planted = (float(reread["obj"]) - probe["om"]) / (2.0 * probe["h"])
            moved, predicted = fd_planted - probe["fd"], READER_PLANT / (2.0 * probe["h"])
            out("\nC3 PLANT, READER-LEVEL   +%.6e into a COPY of %s, re-read from disk"
                % (READER_PLANT, os.path.basename(probe["fp"])))
            out("   FD before %.16e   after %.16e" % (probe["fd"], fd_planted))
            out("   moved     %.16e   predicted %.16e" % (moved, predicted))
            if predicted == 0.0:
                refuse("C3 predicted movement is zero; the control cannot discriminate")
            if rel(moved, predicted) > READER_PLANT_TOL:
                refuse("C3 READER-LEVEL PLANTED-ZERO CONTROL FAILED on component %d: this "
                       "grader's FD arithmetic moved %.16e against a predicted %.16e "
                       "(rel %.6e).  The reader that produces the FD numbers has not been "
                       "shown able to see a non-zero."
                       % (idx, moved, predicted, rel(moved, predicted)))
            out("   C3                    PASS")
        finally:
            shutil.rmtree(tmpd, ignore_errors=True)

        out("\nTHE FD TABLE -- central differences, component %d" % idx)
        out("   %-4s %-11s %-22s %-22s %-22s %-12s"
            % ("tag", "h", "obj(+h)", "obj(-h)", "central FD", "vs adjoint"))
        for r in rows:
            e = rel(r["fd"], adj) if adj != 0.0 else float("nan")
            out("   %-4s %-11.3e %-22.16e %-22.16e %-22.16e %-12.6e"
                % (r["tag"], r["h"], r["op"], r["om"], r["fd"], e))

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
        out("\nPLATEAU, COMPONENT %d   tol %.1e on adjacent values, minimum run %d steps"
            % (idx, PLATEAU_TOL, MIN_PLATEAU_STEPS))
        for i in range(len(rows) - 1):
            a, bb = rows[i]["fd"], rows[i + 1]["fd"]
            d = abs(a - bb) / abs(bb) if bb != 0.0 else float("inf")
            out("   adjacent %s->%s  %.6e  %s"
                % (rows[i]["tag"], rows[i + 1]["tag"], d,
                   "IN" if d <= PLATEAU_TOL else "out"))
        out("   longest consecutive run: %d steps -- %s"
            % (len(best), ", ".join(rows[i]["tag"] for i in best)))
        if len(best) < MIN_PLATEAU_STEPS:
            out("\n   NO PLATEAU on component %d: longest run %d steps, minimum %d."
                % (idx, len(best), MIN_PLATEAU_STEPS))
            out("   A step not proved to lie in a plateau is not a proved step "
                "(DAFOAM_CHARTER.md §3).")
            out("   COMPONENT %d: NOT A RESULT" % idx)
            verdicts.append((idx, "NOT A RESULT", None, None, None))
            continue

        ref = rows[best[(len(best) - 1) // 2]]
        out("   REFERENCE STEP (registered rule: middle of the longest run, ties to the "
            "smaller step): %s, h = %.3e" % (ref["tag"], ref["h"]))
        fd = ref["fd"]
        if fd == 0.0:
            refuse("component %d reference-step FD is exactly zero" % idx)
        err = rel(adj, fd)
        flip = (adj * fd) < 0.0
        out("\n   GATE, COMPONENT %d -- statistic: single-component relative error "
            "|D_adj - D_fd| / |D_fd|" % idx)
        out("   (NAMED as a statistic per DAFOAM_CHARTER.md §2.  NOT the vector-relative")
        out("    error, NOT the DAFoam papers' per-component average.  No aggregate over")
        out("    the two components is formed anywhere in this grader.)")
        out("   adjoint %.16e" % adj)
        out("   FD      %.16e  at h = %.3e" % (fd, ref["h"]))
        out("   rel err %.6e    band PASS <= %.3e    sign flip %s"
            % (err, BAND_PASS, "YES" if flip else "no"))
        if flip or err > BAND_COND:
            v = "GATE FAIL"
        elif err > BAND_PASS:
            v = "GATE FAIL"
        else:
            v = "PASS"
        out("   COMPONENT %d: %s" % (idx, v))
        verdicts.append((idx, v, err, fd, ref["h"]))

    out("\n" + "=" * 78)
    out("PER-COMPONENT SUMMARY -- reported BESIDE nothing, because there is no aggregate")
    for idx, v, err, fd, h in verdicts:
        if err is None:
            out("   component %d   %-12s  (no plateau)" % (idx, v))
        else:
            out("   component %d   %-12s  rel err %.6e   FD %.10e at h %.3e"
                % (idx, v, err, fd, h))
    order = {"NOT A RESULT": 0, "GATE FAIL": 1, "PASS": 2}
    final = min((v for _, v, _, _, _ in verdicts), key=lambda x: order[x])
    out("\nARM VERDICT = the WORST per-component verdict (registered rule: a table with a")
    out("failing component is a failing table; the aggregate never rescues a component).")
    print("VERDICT: %s" % final)
    return final


# ------------------------------------------------------------------------- selftest
def _w(root: str, sub: str, fn: str, obj: dict) -> None:
    os.makedirs(os.path.join(root, sub), exist_ok=True)
    with open(os.path.join(root, sub, fn), "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)


def _shape(idx: int, v: float) -> list:
    s = [0.0] * REF_NSHAPES
    s[idx] = v
    return s


def _synth(root: str, adj_scale: float = 1.0, plant_resp: float = 6.27e-4,
           n_steps: int = 5, noise: float = 0.0, break_identity: bool = False,
           only_component: int | None = None, bad_cross: bool = False) -> None:
    d = list(REF_DOBJ_DSHAPE)
    if break_identity:
        d[3] = d[3] * 1.0000001
    _w(root, "base", "d12f_base.json",
       {"status": "COMPLETE", "task": "compute_totals", "obj": REF_OBJ,
        "dobj_dshape": d, "nShapes": REF_NSHAPES, "shape": [0.0] * REF_NSHAPES,
        "shapeIdx": 0, "shapeSign": "plus", "shapeMag": 0.0, "shapeValue": 0.0})
    for r in ("rep0", "rep1"):
        _w(root, r, "d12f_%s.json" % r,
           {"status": "COMPLETE", "task": "run_model", "obj": REF_OBJ,
            "nShapes": REF_NSHAPES, "shape": [0.0] * REF_NSHAPES,
            "shapeIdx": 0, "shapeSign": "plus", "shapeMag": 0.0, "shapeValue": 0.0})
    _w(root, "plant", "d12f_plant.json",
       {"status": "COMPLETE", "task": "run_model", "obj": REF_OBJ * (1.0 + plant_resp),
        "nShapes": REF_NSHAPES, "shape": _shape(0, PLANT_SHAPE),
        "shapeIdx": 0, "shapeSign": "plus", "shapeMag": PLANT_SHAPE,
        "shapeValue": PLANT_SHAPE})
    for idx in COMPONENTS:
        slope = REF_DOBJ_DSHAPE[idx] * (adj_scale if (only_component in (None, idx)) else 1.0)
        for tag, h in STEPS[:n_steps]:
            w = noise / h if noise else 0.0
            sp = _shape(idx, h)
            sm = _shape(idx, -h)
            if bad_cross:
                sp[(idx + 1) % REF_NSHAPES] = 1.0e-9
            _w(root, "c%d_fdp_%s" % (idx, tag), "d12f_c%d_fdp_%s.json" % (idx, tag),
               {"status": "COMPLETE", "task": "run_model",
                "obj": REF_OBJ + slope * h + w, "nShapes": REF_NSHAPES, "shape": sp,
                "shapeIdx": idx, "shapeSign": "plus", "shapeMag": h, "shapeValue": h})
            _w(root, "c%d_fdm_%s" % (idx, tag), "d12f_c%d_fdm_%s.json" % (idx, tag),
               {"status": "COMPLETE", "task": "run_model",
                "obj": REF_OBJ - slope * h, "nShapes": REF_NSHAPES, "shape": sm,
                "shapeIdx": idx, "shapeSign": "minus", "shapeMag": h, "shapeValue": -h})


def _expect(name: str, want: str, c3_blind: bool = False, **kw) -> bool:
    global _C3_BLIND
    root = tempfile.mkdtemp(prefix="d12f_selftest_")
    _C3_BLIND = c3_blind
    try:
        _synth(root, **kw)
        try:
            got = grade(root, quiet=True)
        except SystemExit as e:
            got = "NOT A RESULT" if e.code == 2 else "EXIT %s" % e.code
        ok = got == want
        print("   %-46s want %-13s got %-13s  %s"
              % (name, want, got, "PASS" if ok else "*** FAIL ***"))
        return ok
    finally:
        _C3_BLIND = False
        shutil.rmtree(root, ignore_errors=True)


def selftest() -> int:
    print("D12-F' GRADER SELFTEST -- each mutant MUST flip the verdict.\n")
    ok = True
    ok &= _expect("clean tree, adjoint == FD", "PASS")
    ok &= _expect("adjoint 3 % off, both components", "PASS", adj_scale=1.0 / 1.03)
    ok &= _expect("adjoint 8 % off, both components", "GATE FAIL", adj_scale=1.0 / 1.08)
    ok &= _expect("adjoint 40 % off, both components", "GATE FAIL", adj_scale=1.0 / 1.40)
    ok &= _expect("SIGN FLIP, both components", "GATE FAIL", adj_scale=-1.0)
    ok &= _expect("component 0 ALONE 40 % off (worst-of rule)", "GATE FAIL",
                  adj_scale=1.0 / 1.40, only_component=0)
    ok &= _expect("component 3 ALONE 40 % off (worst-of rule)", "GATE FAIL",
                  adj_scale=1.0 / 1.40, only_component=3)
    ok &= _expect("C2 plant response EXACTLY ZERO", "NOT A RESULT", plant_resp=0.0)
    ok &= _expect("C2 plant response below floor", "NOT A RESULT", plant_resp=1.0e-12)
    ok &= _expect("C4 only 3 steps on disk", "NOT A RESULT", n_steps=3)
    ok &= _expect("C1 instrument identity broken", "NOT A RESULT", break_identity=True)
    ok &= _expect("no plateau (step-dependent wobble)", "NOT A RESULT", noise=1.0e-6)
    ok &= _expect("C3 reader BLINDED to the planted copy", "NOT A RESULT", c3_blind=True)
    ok &= _expect("a NON-ZERO OFF-COMPONENT in an FD stage", "NOT A RESULT", bad_cross=True)
    print("\n   %s" % ("ALL SELFTESTS PASS" if ok else "*** SELFTEST FAILURE ***"))
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="/home/ubuntu/certonomous-runs/"
                                      "CURRICULUM-PROBES-D10-D11-D12/D12F")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    grade(a.base)
