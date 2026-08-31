#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SO-3aF2 FEASIBILITY READER -- host-only, ZERO solver compute.

=============================================================================
THIS READER COMPUTES NO GRADIENT.  IT SCORES NO GATE.  IT EMITS NO VERDICT.
=============================================================================
`FEASIBILITY_PREREGISTRATION.md` section 0 registers this item as `prereg=FEASIBILITY`:
no gradient gate, no FD table, no adjoint.  This file reads primal functionals and
directory structure and scores the section-5 predictions HIT / MISS.  HIT and MISS
are NOT the verdict vocabulary of `CLAUDE.md` rule 1 and must never be rendered as
`PASS` or `GATE FAIL`.  The only rule-1 words this module may emit describe the
ITEM's infrastructure state -- `BLOCKED` (a NO-LAUNCH branch fired) or
`NOT A RESULT` (a refusal) -- and never a number.

It REFUSES (exit 2) rather than degrading (`CLAUDE.md` rule 4's comparator
discipline): a reading it cannot stand behind is not reported with a caveat, it is
not reported.

=============================================================================
THE PLANTED CONTROL IS RELATIVE, AND THAT IS THE POINT
=============================================================================
`CD ~ 0.017` and `CL ~ 0.66` on this case differ by a factor of 38.  A single
ABSOLUTE plant sized for one is wrong for the other BY CONSTRUCTION.  That is
exactly the defect SO-2M died of and SO-2MR repaired
(`curriculum_SO2MR/PREREGISTRATION.md` sections 0 and 7.2): an absolute plant
magnitude does not port across functionals.  The plant here is therefore a RULE
relative to the quantity it perturbs, with K_F fixed at freeze, and the reader
RE-DERIVES its sufficiency from the row's own numbers and REFUSES
`PLANT_NOT_SUFFICIENT_BY_CONSTRUCTION` if the plant cannot cross the band.

A control whose plant cannot cross the band it must cross is a control in name
only, and shipping one is what cost this family a whole item.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# REGISTERED CONSTANTS -- frozen by FEASIBILITY_PREREGISTRATION.md sections 4.2 and 5.
# ---------------------------------------------------------------------------

# The reproduction band, section 5 F2: relative 1.0e-6, carried here as a PERCENT
# so the plant algebra below reads in the same units as the band.
BAND_REP_PCT = 1.0e-4                      # 1.0e-4 % == relative 1.0e-6

# THE PLANT MULTIPLIER, registered at freeze.  K_F > 1 is what makes the plant
# sufficient by construction; the sufficiency assertion below re-derives it anyway
# rather than trusting this line, and selftest leg S3 drives it RED at K_F = 0.5.
FLIP_PLANT_K_F = 2.0

# THE REFERENCE FUNCTIONALS, from TWO independent prior runs that agree to a
# relative 1.8e-9 on their worst entry.  Section 0 of the pre-registration records
# both sources; these are SO-3aR's digits [MEASURED, curriculum_SO3aR/RESULTS.md:151-153].
CD_REF = [0.01723938072177922, 0.020910510045267394, 0.027268054119716875]
CL_REF = [0.31189588769251864, 0.49876526085592926, 0.6639763551107052]
J_REF = 0.02180598162892116
WEIGHTS = [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]
ALPHAS = [3.13918623195176, 5.13918623195176, 7.13918623195176]
RUN_DIRS = ["mp0", "mp1", "mp2"]

# The token whose ABSENCE is prediction F4.  Counted PER LINE, never as a
# whole-file substring scan (the scan shape that killed SO-1a's grade).
COLLISION_TOKEN = "already exists, moving failed!"

# The token whose PRESENCE in the staged producer refuses NL-2: the structural half
# of the no-gradient promise (pre-registration section 3).
FORBIDDEN_PRODUCER_TOKEN = "compute_totals"

TOL_LINE = "satisfied the prescribed tolerance"


class Refusal(Exception):
    """Raised INSTEAD of returning a reading this module cannot stand behind."""


def refuse(kind: str, detail: dict) -> None:
    raise Refusal(json.dumps({"REFUSE": kind, "detail": detail}, sort_keys=True))


# ---------------------------------------------------------------------------
# THE PLANT RULE (pre-registration section 4.2)
# ---------------------------------------------------------------------------

def flip_plant(v_ref: float, v_live: float):
    """Return (magnitude, signed_delta, need) for the RELATIVE plant rule.

        need = (BAND_REP_PCT/100) * |v_ref|      the margin that must be crossed
        P    = K_F * need                        (MAGNITUDE)
        s    = +1 if v_live >= v_ref else -1     (SIGN -- AWAY from v_ref)

    Because s moves v_live AWAY from v_ref, |v_ref - v'| = |v_ref - v| + P
    EXACTLY, so no cancellation is reachable from any live position and

        rel_planted = rel_live + K_F * BAND_REP_PCT >= K_F * BAND_REP_PCT

    which at K_F = 2.0 is 2.0e-4 % against a 1.0e-4 % band: 100 % margin, at
    EITHER functional's scale, whatever the live agreement happens to be.
    """
    need = (BAND_REP_PCT / 100.0) * abs(v_ref)
    mag = FLIP_PLANT_K_F * need
    sign = 1.0 if v_live >= v_ref else -1.0
    return mag, sign * mag, need


def rel_pct(v_ref: float, v: float) -> float:
    """Relative error in PERCENT against v_ref.  |v_ref| is never zero for any
    reference in this item (the smallest is CD_REF[0] ~ 1.7e-2), and a zero
    reference REFUSES rather than dividing."""
    if v_ref == 0.0:
        refuse("READER", {"ZERO_REFERENCE": {"v_ref": v_ref, "v": v}})
    return abs(v_ref - v) / abs(v_ref) * 100.0


def reproduces(v_ref: float, v: float) -> bool:
    """HIT iff the read value sits inside the registered reproduction band.
    NOT a gate -- section 5 scores these HIT/MISS and a MISS is a FINDING."""
    return rel_pct(v_ref, v) <= BAND_REP_PCT


# ---------------------------------------------------------------------------
# READING FROM DISK
# ---------------------------------------------------------------------------

def read_artefact(path: str) -> dict:
    """Read the XM artefact FROM DISK.  Every traversal below walks the full
    per-point structure; a control that EMPTIES that structure is refused by
    `check_plant_visible`, because an empty container is seen by a broken reader
    too (`CLAUDE.md` rule 3)."""
    if not os.path.isfile(path):
        refuse("READER", {"ARTEFACT_ABSENT": {"path": path}})
    with open(path) as fh:
        j = json.load(fh)
    pts = j.get("points")
    if not isinstance(pts, list) or len(pts) != len(ALPHAS):
        refuse("READER", {"POINTS_MALFORMED": {
            "path": path, "want_n": len(ALPHAS),
            "got": (len(pts) if isinstance(pts, list) else type(pts).__name__)}})
    for i, p in enumerate(pts):
        for key in ("CD", "CL", "alpha"):
            if key not in p:
                refuse("READER", {"POINT_KEY_MISSING": {"point": i, "key": key}})
            if not isinstance(p[key], (int, float)) or p[key] != p[key]:
                refuse("READER", {"POINT_VALUE_NON_FINITE": {
                    "point": i, "key": key, "value": p[key]}})
    return j


def count_token_per_line(log_path: str, token: str) -> int:
    """Count a token PER LINE.  Never a whole-file substring scan: that shape
    cannot say WHERE a token appeared or how many times, and it is the shape that
    killed SO-1a's grade (`so1a_grade.py:122-125`)."""
    if not os.path.isfile(log_path):
        refuse("READER", {"LOG_ABSENT": {"path": log_path}})
    n = 0
    with open(log_path, errors="replace") as fh:
        for line in fh:
            if token in line:
                n += 1
    return n


def read_run_dirs(case_root: str):
    """Prediction F3, read from the disk: three DISTINCT run directories, each
    holding its own time directories.  Returns the per-directory time listing."""
    out = {}
    for d in RUN_DIRS:
        full = os.path.join(case_root, d)
        if not os.path.isdir(full):
            out[d] = None
            continue
        times = sorted(x for x in os.listdir(full)
                       if re.fullmatch(r"\d+(\.\d+)?", x))
        out[d] = times
    return out


# ---------------------------------------------------------------------------
# THE CONTROLS
# ---------------------------------------------------------------------------

def check_plant_visible(tmpdir: str) -> dict:
    """DIRECTION A -- the reader can see a non-zero.

    Write a synthetic artefact, plant a known perturbation INSIDE the per-point
    structure the reader must traverse in full, re-read it FROM DISK, and REFUSE
    if the plant is invisible.  A control that EMPTIES the structure is refused
    rather than accepted: an empty container is seen by a broken reader too."""
    path = os.path.join(tmpdir, "plantA.json")
    clean = {"points": [{"alpha": ALPHAS[i], "CD": CD_REF[i], "CL": CL_REF[i]}
                        for i in range(3)], "J": J_REF}
    with open(path, "w") as fh:
        json.dump(clean, fh)
    base = read_artefact(path)

    mag, signed, _need = flip_plant(CD_REF[1], CD_REF[1])
    planted = json.loads(json.dumps(clean))
    planted["points"][1]["CD"] = CD_REF[1] + signed
    with open(path, "w") as fh:
        json.dump(planted, fh)
    back = read_artefact(path)                       # RE-READ FROM DISK

    seen = back["points"][1]["CD"] - base["points"][1]["CD"]
    if abs(abs(seen) - mag) > 1e-18:
        refuse("CONTROL", {"DIRECTION_A_PLANT_INVISIBLE": {
            "planted": signed, "seen": seen, "magnitude": mag,
            "note": "the reader did not read back the perturbation it wrote to "
                    "disk; a zero from this reader would not be evidence"}})

    # THE EMPTY-STRUCTURE REFUSAL, driven here rather than asserted.
    with open(path, "w") as fh:
        json.dump({"points": [], "J": J_REF}, fh)
    emptied_refused = False
    try:
        read_artefact(path)
    except Refusal:
        emptied_refused = True
    if not emptied_refused:
        refuse("CONTROL", {"EMPTY_STRUCTURE_NOT_REFUSED": {
            "note": "an emptied per-point structure must REFUSE, because an empty "
                    "container is traversed successfully by a broken reader"}})
    return {"demonstrated": True, "planted": signed, "seen": seen,
            "empty_structure_refused": True}


def check_reproduction_flips(points, tmpdir: str) -> dict:
    """DIRECTION B -- the reproduction check must be SHOWN able to read MISS.

    Plant the RELATIVE rule into the target entry, RE-READ FROM DISK, and require
    the reproduction check to flip HIT -> MISS.  THE SUFFICIENCY ASSERTION IS
    RE-DERIVED FROM THIS ROW'S OWN NUMBERS AND REFUSES IF IT DOES NOT HOLD."""
    # target: the graded CD entry with the smallest |reference|, ties by index.
    idx = min(range(3), key=lambda i: (abs(CD_REF[i]), i))
    v_ref, v_live = CD_REF[idx], float(points[idx]["CD"])
    mag, signed, need = flip_plant(v_ref, v_live)

    # THE SUFFICIENCY ASSERTION.  A plant that cannot cross the band demonstrates
    # nothing and is a control in name only.
    if not mag > need:
        refuse("CONTROL", {"PLANT_NOT_SUFFICIENT_BY_CONSTRUCTION": {
            "target": ["CD", idx], "v_ref": v_ref, "band_REP_pct": BAND_REP_PCT,
            "K_F": FLIP_PLANT_K_F, "plant_magnitude": mag,
            "plant_needed_to_cross_band": need,
            "rule": "P = K_F * (band_REP/100) * |v_ref|, sign AWAY from v_ref"},
            "note": "section 4.2 registers the plant as a RULE RELATIVE to the "
                    "quantity it perturbs.  A K_F at or below 1 makes the plant "
                    "unable to cross the band BY CONSTRUCTION, and this control "
                    "REFUSES rather than reporting a demonstration it did not make."})

    live_hit = reproduces(v_ref, v_live)
    path = os.path.join(tmpdir, "plantB.json")
    with open(path, "w") as fh:
        json.dump({"points": [dict(p) for p in points], "J": J_REF}, fh)
    with open(path) as fh:
        doc = json.load(fh)
    doc["points"][idx]["CD"] = v_live + signed
    with open(path, "w") as fh:
        json.dump(doc, fh)
    back = read_artefact(path)                       # RE-READ FROM DISK
    planted_hit = reproduces(v_ref, float(back["points"][idx]["CD"]))

    return {"demonstrated": (live_hit and not planted_hit),
            "target": ["CD", idx], "v_ref": v_ref, "v_live": v_live,
            "plant_K_F": FLIP_PLANT_K_F, "plant_magnitude": mag,
            "plant_needed_to_cross_band": need,
            "plant_margin_ratio": (mag / need) if need else None,
            "plant_is_sufficient": bool(mag > need),
            "live_reads_HIT": live_hit, "planted_reads_HIT": planted_hit,
            "rel_live_pct": rel_pct(v_ref, v_live),
            "rel_planted_pct": rel_pct(v_ref, float(back["points"][idx]["CD"]))}


# ---------------------------------------------------------------------------
# THE READING
# ---------------------------------------------------------------------------

def read_item(root: str, tmpdir: str) -> dict:
    """Score the section-5 predictions HIT / MISS.  Both controls run in the SAME
    invocation as the reading they license."""
    art = os.path.join(root, "XM", "so3af2_M.json")
    j = read_artefact(art)
    points = j["points"]

    ctrl_a = check_plant_visible(tmpdir)
    ctrl_b = check_reproduction_flips(points, tmpdir)
    if not ctrl_b["demonstrated"]:
        refuse("CONTROL", {"REPRODUCTION_CHECK_DID_NOT_FLIP": ctrl_b,
               "note": "a check never shown reading MISS is not known to be "
                       "load-bearing (L-314)"})

    log = os.path.join(root, "XM", "XM.log")
    n_tol = count_token_per_line(log, TOL_LINE)
    n_collide = count_token_per_line(log, COLLISION_TOKEN)
    resid = j.get("residual_histories")
    n_resid = len(resid) if isinstance(resid, list) else 0

    # F1 -- convergence read TWO WAYS, and a disagreement REFUSES rather than
    # picking one.  SO3aF's reader reported converged=0 with n_res=0 while a
    # different instrument read the same three points converging: a disagreement
    # between two readings, one of which saw no residuals at all, is a reading
    # defect and is refused here instead of being reported as physics.
    if n_tol != n_resid:
        refuse("READER", {"CONVERGENCE_READINGS_DISAGREE": {
            "counted_tolerance_lines": n_tol, "residual_histories": n_resid,
            "note": "section 5 F1 requires the two readings to agree"}})
    f1 = (n_tol == len(ALPHAS))

    f2_entries = []
    for i in range(3):
        f2_entries.append({"point": i, "CD": reproduces(CD_REF[i], float(points[i]["CD"])),
                           "CL": reproduces(CL_REF[i], float(points[i]["CL"])),
                           "CD_rel_pct": rel_pct(CD_REF[i], float(points[i]["CD"])),
                           "CL_rel_pct": rel_pct(CL_REF[i], float(points[i]["CL"]))})
    j_read = float(j.get("J", float("nan")))
    f2 = all(e["CD"] and e["CL"] for e in f2_entries) and reproduces(J_REF, j_read)

    dirs = read_run_dirs(os.path.join(root, "XM", "case"))
    f3 = (all(dirs.get(d) for d in RUN_DIRS)
          and len({tuple(dirs[d]) for d in RUN_DIRS if dirs[d]}) >= 1
          and all(dirs[d] is not None for d in RUN_DIRS))
    f4 = (n_collide == 0)

    # F5 -- J RECOMPUTED from the read CD, never trusted from the artefact.
    j_recomputed = sum(WEIGHTS[i] * float(points[i]["CD"]) for i in range(3))
    f5 = abs(j_recomputed - j_read) <= 1e-12

    return {"prereg": "FEASIBILITY",
            "NOT_A_GRADIENT_FREEZE": True,
            "gradient_numbers_produced": 0,
            "predictions": {"F1": f1, "F2": f2, "F3": f3, "F4": f4, "F5": f5},
            "F1_detail": {"tolerance_lines": n_tol, "residual_histories": n_resid},
            "F2_detail": {"entries": f2_entries, "J_read": j_read,
                          "J_ref": J_REF, "band_REP_pct": BAND_REP_PCT},
            "F3_detail": {"run_dirs": dirs},
            "F4_detail": {"collision_token_count": n_collide},
            "F5_detail": {"J_recomputed": j_recomputed, "J_read": j_read},
            "controls": {"direction_A": ctrl_a, "direction_B": ctrl_b}}


# ---------------------------------------------------------------------------
# SELFTEST
# ---------------------------------------------------------------------------

def _fixture(tmpdir: str, cd=None, cl=None, jval=None, collide=0, ntol=3,
             nresid=3, dirs=True) -> str:
    """A CLEAN fixture that reads every prediction HIT, so a leg that drives one
    RED is driving exactly one thing."""
    root = os.path.join(tmpdir, "root")
    xm = os.path.join(root, "XM")
    os.makedirs(xm, exist_ok=True)
    cd = CD_REF if cd is None else cd
    cl = CL_REF if cl is None else cl
    jv = (sum(WEIGHTS[i] * cd[i] for i in range(3)) if jval is None else jval)
    doc = {"points": [{"alpha": ALPHAS[i], "CD": cd[i], "CL": cl[i]}
                      for i in range(3)],
           "J": jv, "residual_histories": [[1e-3, 1e-8]] * nresid}
    with open(os.path.join(xm, "so3af2_M.json"), "w") as fh:
        json.dump(doc, fh)
    with open(os.path.join(xm, "XM.log"), "w") as fh:
        for _ in range(ntol):
            fh.write("  %s\n" % TOL_LINE)
        for _ in range(collide):
            fh.write("pyDAFoam Error: /mnt/XM/0.0001 %s\n" % COLLISION_TOKEN)
    if dirs:
        for k, d in enumerate(RUN_DIRS):
            p = os.path.join(xm, "case", d, str(100 + k))
            os.makedirs(p, exist_ok=True)
    return root


def _refused(fn):
    """Return the refusal kinds, or None if the call did NOT refuse."""
    try:
        fn()
    except Refusal as exc:
        return list(json.loads(str(exc)).get("detail", {}).keys())
    return None


def _drive_k_red(tmpdir, k_red=0.5):
    """LEG S3, DRIVEN RED.  Move the REGISTERED K_F -- and nothing else -- below 1,
    read the SAME clean fixture that reads HIT at the registered K_F, and require
    the refusal to be PLANT_NOT_SUFFICIENT_BY_CONSTRUCTION BY NAME.

    A bare `refused()` would be satisfied by ANY refusal and could not tell a
    working assertion from an unrelated crash.  K_F is restored in a `finally` so a
    failure inside cannot leave the module mutated, and the restore is asserted
    here AND again from outside by leg S4."""
    global FLIP_PLANT_K_F
    keep = FLIP_PLANT_K_F
    kinds, other = None, None
    try:
        FLIP_PLANT_K_F = k_red
        root = _fixture(os.path.join(tmpdir, "kred"))
        try:
            read_item(root, os.path.join(tmpdir, "kred"))
        except Refusal as exc:
            kinds = list(json.loads(str(exc)).get("detail", {}).keys())
        except Exception as exc:                             # pragma: no cover
            other = "%s: %s" % (type(exc).__name__, exc)
    finally:
        FLIP_PLANT_K_F = keep
    return (FLIP_PLANT_K_F == keep and keep > 1.0 and other is None
            and kinds is not None
            and "PLANT_NOT_SUFFICIENT_BY_CONSTRUCTION" in kinds)


def selftest(tmp: str) -> int:
    n = [0]
    fails = []

    def unit(desc, ok):
        n[0] += 1
        print("  [%s] %s" % ("OK " if ok else "FAIL", desc))
        if not ok:
            fails.append(desc)

    clean = _fixture(os.path.join(tmp, "clean"))
    res = read_item(clean, os.path.join(tmp, "clean"))

    unit("S0 the clean fixture reads every registered prediction HIT",
         all(res["predictions"].values()))
    unit("S0b the reader reports it produced ZERO gradient numbers and is not a "
         "gradient freeze",
         res["gradient_numbers_produced"] == 0 and res["NOT_A_GRADIENT_FREEZE"])

    # --- the plant rule, driven from both sides
    unit("S1a (DIRECTION A) the reader reads back from DISK a plant it wrote, and "
         "the magnitude matches the rule exactly",
         res["controls"]["direction_A"]["demonstrated"])
    unit("S1b (DIRECTION A) an EMPTIED per-point structure REFUSES -- an empty "
         "container is traversed successfully by a broken reader too",
         res["controls"]["direction_A"]["empty_structure_refused"])
    unit("S2a (DIRECTION B) the reproduction check is SHOWN reading MISS under the "
         "planted copy while the live row reads HIT",
         res["controls"]["direction_B"]["demonstrated"])
    unit("S2b (DIRECTION B) the plant margin ratio is exactly K_F = %g"
         % FLIP_PLANT_K_F,
         abs(res["controls"]["direction_B"]["plant_margin_ratio"]
             - FLIP_PLANT_K_F) < 1e-12)

    # THE ALGEBRA THE RULE RESTS ON, at BOTH functional scales -- this is the leg
    # that would have caught SO-2M's defect, and it is driven at CD's scale AND
    # CL's scale because a plant that ports across a factor of 38 is the claim.
    ok_alg = True
    for v_ref in (CD_REF[0], CL_REF[2]):
        for v_live in (v_ref * (1.0 + 3e-7), v_ref * (1.0 - 3e-7)):
            mag, signed, need = flip_plant(v_ref, v_live)
            lhs = rel_pct(v_ref, v_live + signed)
            rhs = rel_pct(v_ref, v_live) + FLIP_PLANT_K_F * BAND_REP_PCT
            ok_alg = ok_alg and abs(lhs - rhs) < 1e-9 and mag > need
    unit("S2c (THE ALGEBRA) rel_planted = rel_live + K_F*band EXACTLY, and the plant "
         "exceeds the need, at BOTH the CD scale and the CL scale -- the factor of "
         "38 an ABSOLUTE plant could not port across",
         ok_alg)
    unit("S2d (THE SIGN RULE) the plant moves the value AWAY from the reference "
         "from EITHER side, so no cancellation is reachable",
         flip_plant(1.0, 2.0)[1] > 0 and flip_plant(1.0, 0.5)[1] < 0)

    # --- S3: DRIVEN RED, the leg that makes sufficiency load-bearing
    unit("S3 (SUFFICIENCY, DRIVEN RED) with K_F moved BELOW 1 the plant can no "
         "longer cross the band and the reader REFUSES "
         "PLANT_NOT_SUFFICIENT_BY_CONSTRUCTION BY NAME",
         _drive_k_red(tmp))
    unit("S4 (THE RESTORE, ASSERTED FROM OUTSIDE) K_F is back at its registered %g "
         "after the RED drive and the clean fixture reads HIT again -- the RED leg "
         "left no residue" % FLIP_PLANT_K_F,
         FLIP_PLANT_K_F == 2.0
         and all(read_item(clean, os.path.join(tmp, "clean"))["predictions"].values()))

    # --- each prediction driven RED individually
    bad_cd = list(CD_REF)
    bad_cd[1] = CD_REF[1] * (1.0 + 1e-4)          # 100x the band
    r = read_item(_fixture(os.path.join(tmp, "f2"), cd=bad_cd),
                  os.path.join(tmp, "f2"))
    unit("N-F2 a CD entry moved 100x the reproduction band reads F2 MISS",
         r["predictions"]["F2"] is False)

    r = read_item(_fixture(os.path.join(tmp, "f4"), collide=2),
                  os.path.join(tmp, "f4"))
    unit("N-F4 a PLANTED collision token is COUNTED (2) and reads F4 MISS -- the "
         "zero in F4 is a reading, not an absence the counter cannot see",
         r["F4_detail"]["collision_token_count"] == 2
         and r["predictions"]["F4"] is False)

    r = read_item(_fixture(os.path.join(tmp, "f3"), dirs=False),
                  os.path.join(tmp, "f3"))
    unit("N-F3 absent per-point run directories read F3 MISS",
         r["predictions"]["F3"] is False)

    r = read_item(_fixture(os.path.join(tmp, "f1"), ntol=2, nresid=2),
                  os.path.join(tmp, "f1"))
    unit("N-F1 two converged points of three read F1 MISS (both readings agreeing)",
         r["predictions"]["F1"] is False)

    unit("N-F1b a DISAGREEMENT between the two convergence readings REFUSES rather "
         "than reporting either -- SO3aF's reader recorded converged=0 with "
         "n_res=0 while another instrument read three converging",
         _refused(lambda: read_item(_fixture(os.path.join(tmp, "f1b"), ntol=3,
                                             nresid=1), os.path.join(tmp, "f1b")))
         == ["CONVERGENCE_READINGS_DISAGREE"])

    r = read_item(_fixture(os.path.join(tmp, "f5"), jval=0.5),
                  os.path.join(tmp, "f5"))
    unit("N-F5 a J inconsistent with the weighted CD sum reads F5 MISS, because J "
         "is RECOMPUTED and never trusted from the artefact",
         r["predictions"]["F5"] is False)

    unit("N-ART an ABSENT artefact REFUSES rather than reading zeros",
         _refused(lambda: read_item(os.path.join(tmp, "nope"),
                                    os.path.join(tmp, "clean")))
         == ["ARTEFACT_ABSENT"])

    print("SO3aF2 READER SELFTEST units=%d failures=%d python_O=%s"
          % (n[0], len(fails), not __debug__))
    if fails:
        for f in fails:
            print("  FAILED: %s" % f)
        print("SO3aF2 READER SELFTEST FAIL")
        return 1
    print("SO3aF2 READER SELFTEST PASS %d/%d" % (n[0], n[0]))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    import tempfile
    if a.selftest:
        with tempfile.TemporaryDirectory() as tmp:
            return selftest(tmp)
    if not a.root:
        print("--root or --selftest required")
        return 64
    with tempfile.TemporaryDirectory() as tmp:
        try:
            res = read_item(a.root, tmp)
        except Refusal as exc:
            print("REFUSED (exit 2): %s" % exc)
            if a.out:
                with open(a.out, "w") as fh:
                    json.dump({"refusal": json.loads(str(exc))}, fh, indent=2)
            return 2
    txt = json.dumps(res, indent=2, sort_keys=True)
    print(txt)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
