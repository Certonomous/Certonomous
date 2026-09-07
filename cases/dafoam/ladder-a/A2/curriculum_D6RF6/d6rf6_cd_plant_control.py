#!/usr/bin/env python3
"""Curriculum D6RF6 -- `PREREGISTRATION.md` section 3e's THIRD PLANTED-ZERO
CONTROL, and the ONE reader of `CD_i(mp)` in this item.

WHY THIS FILE EXISTS AS A SEPARATE INSTRUMENT AND NOT AS A BLOCK INSIDE THE
GRADER.  `CLAUDE.md` rule 3 says a zero -- or an agreement -- from a reader not
shown able to see a non-zero is not evidence.  The strongest way to satisfy it
is to make the control and the graded path THE SAME FUNCTION, so that a control
cannot drift away from what it is controlling.  `d6rf6_grade.py` imports
`read_cd` from here and calls NOTHING ELSE to obtain a `CD`.  A control that
exercises a different reader controls nothing, and `d6rf2_grade.py:481-484`
already says so about the FD reader; this file applies the same discipline to
the reader that moved.

WHY THE SOURCE MOVED AT ALL.  `PREREGISTRATION.md` section 2a re-points
`CD_i(mp)` from the producing optimiser's history to the FD arm's own
`baseline` primal, because `D6RF3-DEF-4` established BY COMPLETE ENUMERATION
that the history contains no `CD` at all.  **A CD read from a new source is not
evidence until a reader has been shown able to see a non-zero in it**, and that
is the whole content of this file.

BOTH DIRECTIONS ARE DRIVEN, and the drive is committed with the freeze:
  * `--drive` runs the control on a synthetic product it builds itself and
    requires `EXERCISED-PASS`;
  * the SAME `--drive` then runs the control against FOUR DELIBERATELY BLIND
    READERS -- one looking at the wrong top-level block, one at the wrong
    point, one at the wrong quantity, one that ignores its argument and returns
    a constant -- and requires the control to REFUSE on every one of them.
    A control never shown failing is a control never shown working.

  ⚠ AND THE LESSON THIS FAMILY PAID FOR TWICE THIS WEEK: a control that passes
  for a reason unrelated to its name is not a control.  The blind-reader drive
  therefore asserts THE REASON -- that the refusal is `PLANT_CD` with
  `reader_saw_the_plant` false -- and never merely that the call raised.  A
  blind reader that happened to raise `KeyError` would satisfy `rc != 0` while
  proving nothing about plant visibility.

NO `assert` STATEMENT APPEARS IN THIS FILE.  `python -O` deletes them, and a
control that vanishes under an optimisation flag is worse than no control.
Every check is an explicit `if ... refuse(...)`.
"""
import argparse
import hashlib
import json
import math
import os
import sys
import tempfile

PLANT = 1.234e-03                    # the registered perturbation, section 3e
PLANT_REL_TOL = 1.0e-9
CD_ARTEFACT = "d6rf6_fd_endpoint.json"
PLANT_POINT = "cl05"                 # section 3e: planted BY KEY at points.cl05.CD
POINTS = ("cl04", "cl05", "cl06")

# The three states of DAFOAM_CHARTER.md section 18.5's proposal.  That proposal
# is NOT ENACTED lab-wide -- adopting it for every family's comparators is
# Sanaa's call and no agent's message is her consent (CLAUDE.md rule 9).  It is
# taken HERE, inside this item's own instruments, where this item's supervisor
# may take it: a control that did not run is the limiting case of a reader
# shown nothing, and its silence must not be indistinguishable from its success.
EXERCISED_PASS = "EXERCISED-PASS"
EXERCISED_FAIL = "EXERCISED-FAIL"
NOT_EXERCISED = "NOT EXERCISED"


class CDRefusal(Exception):
    pass


def refuse(where, detail):
    raise CDRefusal(json.dumps({"REFUSE": where, "detail": detail},
                               sort_keys=True, default=str)[:4000])


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


# ============================== THE READER ==================================
def read_cd(path, point):
    """THE CD READER of this item, and the ONLY one.

    Returns the raw token at `points.<point>.CD` of `path` EXACTLY as the
    artefact holds it -- a `repr()`'d string, because `d6rf6_fd_endpoint.py`
    writes `repr(float(...))`.  IT DOES NOT PARSE AND IT DOES NOT CHECK
    FINITENESS: parsing and the section 3f finiteness check are the grader's,
    through `_ff`, so that the reader shown able to see a plant is byte-for-byte
    the reader the gate uses and NOT a permissive variant of it.

    REFUSES rather than returning a default at every structural failure. There
    is no `.get(..., 0.0)` anywhere in this function, deliberately: a default
    is how a missing measurement becomes a number."""
    if not os.path.isfile(path):
        refuse("CD_READER", {"absent": path})
    with open(path) as fh:
        doc = json.load(fh)
    if "points" not in doc:
        refuse("CD_READER", {"path": path, "no_points_block": True,
                             "top_level_keys": sorted(doc)[:40],
                             "note": "PREREGISTRATION.md section 2a registers "
                                     "the source as `points.<pt>.CD`"})
    pts = doc["points"]
    if point not in pts:
        refuse("CD_READER", {"path": path, "point_absent": point,
                             "points_present": sorted(pts)})
    if "CD" not in pts[point]:
        refuse("CD_READER", {"path": path, "point": point, "no_CD_key": True,
                             "keys_at_point": sorted(pts[point])})
    return pts[point]["CD"]


def read_cl(path, point):
    """The companion CL reader, same structure, same refusal discipline.  G-OFF
    prints CL beside every CD row (section 3a) and a CL obtained by a laxer
    route than its CD would make the pair incomparable."""
    if not os.path.isfile(path):
        refuse("CL_READER", {"absent": path})
    with open(path) as fh:
        doc = json.load(fh)
    if "points" not in doc or point not in doc.get("points", {}) \
            or "CL" not in doc["points"][point]:
        refuse("CL_READER", {"path": path, "point": point,
                             "no_points_point_CL": True})
    return doc["points"][point]["CL"]


def plant_into_cd(src, dst, point=PLANT_POINT):
    """Plant PLANT into `points.<point>.CD` of a COPY, BY KEY.

    BY KEY and not by line index, because the artefact is JSON written with
    `sort_keys=True` and a line-index plant would silently follow whatever
    happened to sort into that position.  Returns the identity planted."""
    with open(src) as fh:
        doc = json.load(fh)
    if "points" not in doc or point not in doc.get("points", {}) \
            or "CD" not in doc["points"][point]:
        refuse("PLANT_CD", {"nothing_to_plant_into": True, "src": src,
                            "point": point,
                            "note": "a control with nothing to plant into is "
                                    "not a control (L-302)"})
    before = float(doc["points"][point]["CD"])
    doc["points"][point]["CD"] = repr(before + PLANT)
    with open(dst, "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    return {"point": point, "key": "points.%s.CD" % point,
            "unperturbed": before}


# ============================== THE CONTROL =================================
def run_cd_control(ctrl_dir, cd_path, reader=read_cd, point=PLANT_POINT):
    """Section 3e's third control.  Plants into a COPY, reads it back FROM DISK
    through `reader`, and REFUSES if `reader` returns the unperturbed value --
    i.e. if the reader is looking somewhere else.

    `reader` is a parameter ONLY so the blind-reader drive can pass a reader
    that is known to be wrong.  `d6rf6_grade.py` never passes it, so the graded
    path and the controlled path are the same function.

    Returns a record whose `state` is one of the three section-18.5 tokens.
    `NOT EXERCISED` is returned, never inferred, when the FD arm did not run and
    there is no artefact to plant into -- and the grader prints it beside the
    verdict rather than omitting it."""
    os.makedirs(ctrl_dir, exist_ok=True)
    base = {"control": "CD_reader", "PLANT": PLANT, "rel_tol": PLANT_REL_TOL,
            "registered_key": "points.%s.CD" % point,
            "artefact": cd_path}
    if cd_path is None or not os.path.isfile(cd_path):
        base.update({"state": NOT_EXERCISED,
                     "reader_saw_the_plant": None,
                     "why": ("the FD arm did not run, so the artefact this "
                             "control plants into does not exist. This is "
                             "REPORTED, never counted as a pass and never "
                             "inferred from the absence of a failure.")})
        return base
    m_before = md5_of(cd_path)
    unperturbed = float(reader(cd_path, point))
    planted_copy = os.path.join(ctrl_dir, "d6rf6_fd_endpoint.PLANTED.json")
    who = plant_into_cd(cd_path, planted_copy, point)
    got = float(reader(planted_copy, point))
    delta = got - unperturbed
    seen = (math.isfinite(delta)
            and abs(delta - PLANT) <= PLANT_REL_TOL
            * max(abs(PLANT), abs(unperturbed), 1.0))
    m_after = md5_of(cd_path)
    base.update({"planted_into": who, "unperturbed": unperturbed,
                 "planted_read_back": got, "delta": delta,
                 "reader_saw_the_plant": bool(seen),
                 "original_md5_before": m_before,
                 "original_md5_after": m_after,
                 "original_unchanged": m_before == m_after,
                 "planted_copy": planted_copy,
                 "state": EXERCISED_PASS if seen else EXERCISED_FAIL})
    if not seen:
        refuse("PLANT_CD", dict(base, note="the reader did not see the plant: "
                                           "it is not reading the registered "
                                           "key. A CD read from a new source "
                                           "is not evidence until a reader has "
                                           "been shown able to see a non-zero "
                                           "in it."))
    if m_before != m_after:
        refuse("PLANT_CD", dict(base,
                                the_control_modified_the_artefact_it_grades=True))
    return base


# ============================ THE DRIVE, BOTH WAYS ==========================
def _synthetic_product(path):
    """A minimal artefact of the shape `d6rf6_fd_endpoint.py` writes.  Built
    here rather than taken from a run.

    THE REASON IS TENSELESS AND STAYS TRUE AFTER THE ITEM RUNS: a control that
    can only be driven ONCE the compute it guards has happened is not a
    pre-compute control, and this one has to be drivable at the freeze, when
    no product exists."""
    cd = {"cl04": 1.846929883e-02, "cl05": 2.176156349e-02,
          "cl06": 2.696277508e-02}
    cl = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}
    doc = {"points": {p: {"CD": repr(cd[p]), "CL": repr(cl[p])}
                      for p in POINTS},
           "points_baseline": {p: {"CD": repr(cd[p]), "CL": repr(cl[p])}
                               for p in POINTS},
           "points_source": "FD_BASELINE_PRIMAL",
           "J_baseline": repr(0.022238800232340834), "rows": [], "n_rows": 0}
    with open(path, "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
    return cd


# ---- the four deliberately blind readers, each blind in a NAMED way --------
def _blind_wrong_block(path, point):
    """Reads `points_baseline` instead of `points`.  The most likely real
    mistake, because the parent product carried ONLY that block."""
    with open(path) as fh:
        return json.load(fh)["points_baseline"][point]["CD"]


def _blind_wrong_point(path, point):                          # noqa: ARG001
    """Reads cl04 whatever it is asked for -- D6RF3-DEF-4's own trap: the
    extractor's refusal named `cl04` because it is simply the first missing
    pair, while the verdict depends on `cl05`."""
    with open(path) as fh:
        return json.load(fh)["points"]["cl04"]["CD"]


def _blind_wrong_quantity(path, point):
    """Reads CL where CD was asked for."""
    with open(path) as fh:
        return json.load(fh)["points"][point]["CL"]


def _blind_constant(path, point):                             # noqa: ARG001
    """Ignores its argument entirely and returns the registered value.  The
    limiting case: a reader that cannot see ANY plant because it never opens
    the file it was handed."""
    return repr(2.176156349e-02)


BLIND = (("wrong_top_level_block__points_baseline", _blind_wrong_block),
         ("wrong_point__always_cl04", _blind_wrong_point),
         ("wrong_quantity__CL_for_CD", _blind_wrong_quantity),
         ("ignores_its_argument__returns_a_constant", _blind_constant))


def drive():
    """Runs the control in BOTH directions and prints an auditable record.
    Returns 0 only if every direction behaved as registered."""
    tmp = tempfile.mkdtemp(prefix="d6rf6_cd_ctrl_")
    prod = os.path.join(tmp, CD_ARTEFACT)
    cd = _synthetic_product(prod)
    print("D6RF6 CD PLANT CONTROL -- BOTH DIRECTIONS, no `assert` statement "
          "anywhere in this file")
    print("  product %s" % prod)
    print("  registered key points.%s.CD = %r" % (PLANT_POINT, cd[PLANT_POINT]))
    results = {"positive": None, "blind": [], "n_not_exercised": 0}
    rc = 0

    # ---- direction 1: the real reader MUST see the plant -------------------
    m0 = md5_of(prod)
    try:
        r = run_cd_control(os.path.join(tmp, "ctrl"), prod)
    except CDRefusal as e:
        print("  FAIL  direction 1: the registered reader REFUSED -- %s" % e)
        return 1
    ok1 = (r["state"] == EXERCISED_PASS and r["reader_saw_the_plant"] is True
           and r["original_unchanged"] is True and md5_of(prod) == m0)
    results["positive"] = r
    print("  %-5s direction 1  state=%s delta=%.6e (PLANT %.6e) "
          "original_unchanged=%s"
          % ("OK" if ok1 else "FAIL", r["state"], r["delta"], PLANT,
             r["original_unchanged"]))
    if not ok1:
        rc = 1

    # ---- direction 2: every blind reader MUST be refused, FOR ITS REASON ---
    for name, fn in BLIND:
        m_pre = md5_of(prod)
        got, why = None, None
        try:
            run_cd_control(os.path.join(tmp, "blind_" + name), prod, reader=fn)
            got = "NO REFUSAL"
        except CDRefusal as e:
            got = "REFUSED"
            try:
                why = json.loads(str(e))
            except ValueError:
                why = {}
        except Exception as e:                                # noqa: BLE001
            # A blind reader that dies of a KeyError has NOT demonstrated that
            # the control detects plant-blindness.  Recorded as a FAIL of the
            # DRIVE, never counted as the control working.
            got = "RAISED %s" % type(e).__name__
        d = (why or {}).get("detail", {})
        reason_ok = ((why or {}).get("REFUSE") == "PLANT_CD"
                     and d.get("reader_saw_the_plant") is False
                     and d.get("state") == EXERCISED_FAIL)
        good = (got == "REFUSED" and reason_ok and md5_of(prod) == m_pre)
        results["blind"].append({"blind_reader": name, "outcome": got,
                                 "refusal_reason_asserted": reason_ok,
                                 "original_unchanged": md5_of(prod) == m_pre,
                                 "as_registered": good})
        print("  %-5s direction 2  blind=%-42s outcome=%-9s reason_is_PLANT_CD"
              "_with_reader_saw_the_plant_false=%s"
              % ("OK" if good else "FAIL", name, got, reason_ok))
        if not good:
            rc = 1

    # ---- the NOT EXERCISED path is itself exercised, and RETURNS the token -
    ne = run_cd_control(os.path.join(tmp, "ctrl_absent"),
                        os.path.join(tmp, "does_not_exist.json"))
    ok3 = (ne["state"] == NOT_EXERCISED and ne["reader_saw_the_plant"] is None)
    print("  %-5s direction 3  absent artefact -> state=%s (reported, never "
          "counted as a pass)" % ("OK" if ok3 else "FAIL", ne["state"]))
    if not ok3:
        rc = 1

    results["n_not_exercised_on_a_real_grading_run"] = (
        "0 is REQUIRED at the freeze drive; this drive builds its own product "
        "so direction 1 is EXERCISED-PASS and direction 3 is the token's own "
        "test, not a skipped control")
    print("  RESULT %s  (positive=1  blind=%d  not-exercised-token=1)"
          % ("ALL DIRECTIONS AS REGISTERED" if rc == 0 else "NOT AS REGISTERED",
             len(BLIND)))
    return rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drive", action="store_true",
                    help="drive the control in both directions (no compute)")
    ap.add_argument("--artefact", help="run the control on a real product")
    ap.add_argument("--ctrl-dir", default=None)
    a = ap.parse_args()
    if a.drive:
        return drive()
    if a.artefact:
        try:
            r = run_cd_control(a.ctrl_dir or tempfile.mkdtemp(
                prefix="d6rf6_cd_"), a.artefact)
        except CDRefusal as e:
            sys.stderr.write("D6RF6_CD_CONTROL REFUSED %s\n" % e)
            return 2
        print(json.dumps(r, indent=1, sort_keys=True, default=str))
        return 0
    sys.stderr.write("usage: d6rf6_cd_plant_control.py --drive "
                     "| --artefact <d6rf6_fd_endpoint.json>\n")
    return 64


if __name__ == "__main__":
    sys.exit(main())
