#!/usr/bin/env python3
"""D19 -- THE TRAVELLING PROVENANCE GUARD (PREREGISTRATION.md section 9, gate G19-2h).

`SO3b_STUB.md` section 3 states the condition on which a PATCHED-row result may
be built at all:

    legitimate only with the SHIPPED `GATE FAIL` travelling attached to every
    downstream claim, in code (the `curriculum_SO1bR/so1br_precondition.py`
    `require_travelling_provenance()` form).

D19 takes that route.  This file pins D15's graded output BY ABSOLUTE PATH AND BY
MD5 -- never by glob, which is the defect that closed SO-1b at rc = 7 on
2026-08-28 -- and refuses to let ANY D19 verdict be emitted without the SHIPPED
failure attached to it.

The requirement is met BY THE BYTES OR THE EMIT REFUSES.  `require_travelling_
provenance()` returns its argument unchanged so it can wrap an emit expression
directly and cannot be satisfied by a caller who calls it and drops the result.
"""
import hashlib
import json
import os
import sys

D15_GRADE = ("/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic/"
             "D15_grade_20260827T114315Z.json")
D15_GRADE_MD5 = "73e02ebf49b6459e40abc2d6525d7bea"

# The measured values section 9 names, asserted as RELATIONS with the measurement
# recorded beside each, so a future edit to D15 cannot pass silently.
EXPECT = {
    "verdict": "GATE FAIL",
    "rows": {"SHIPPED": "GATE FAIL", "PATCHED": "PASS"},
    "shipped_CD_aggregate_gt": 5.0,        # measured 34.680703
    "patched_CD_aggregate_le": 5.0,        # measured 0.047405
    "shipped_CD_aggregate_measured": 34.680702875524474,
    "patched_CD_aggregate_measured": 0.04740516150798638,
    "shipped_worst_component_measured": 44.873808244835125,   # shape[6]
}

# The frozen suffix.  Section 9: "A D19 number quoted without it is quoted wrongly."
SUFFIX = ("on the PATCHED toolchain; the SHIPPED toolchain FAILS the gradient gate on this "
          "exact ground (D15 shipped worst 44.8738 % on `shape[6]`, aggregate 34.6807 %)")

VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}


class Refusal(Exception):
    pass


def _local_refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def read_upstream(refuse=None):
    """Pin D15's graded output by ABSOLUTE PATH and by MD5.  Never by glob."""
    refuse = refuse or _local_refuse
    if not os.path.isfile(D15_GRADE):
        refuse("G-PROV", {"upstream_absent": D15_GRADE,
                          "note": "no D19 verdict may be emitted without D15's graded output"})
    got = md5_of(D15_GRADE)
    if got != D15_GRADE_MD5:
        refuse("G-PROV", {"upstream_md5_drifted": D15_GRADE, "got": got,
                          "frozen": D15_GRADE_MD5,
                          "note": "the upstream row moved under this item"})
    g = json.load(open(D15_GRADE))
    if g.get("verdict") != EXPECT["verdict"]:
        refuse("G-PROV", {"upstream_verdict": g.get("verdict"), "expected": EXPECT["verdict"]})
    rows = g.get("rows") or {}
    for row, want in EXPECT["rows"].items():
        if rows.get(row) != want:
            refuse("G-PROV", {"upstream_row": row, "got": rows.get(row), "expected": want})
    try:
        s_agg = g["gates"]["G5_SHIPPED"]["G5_CD"]["aggregate_rel_err_pct"]
        p_agg = g["gates"]["G5_PATCHED"]["G5_CD"]["aggregate_rel_err_pct"]
    except (KeyError, TypeError):
        refuse("G-PROV", {"upstream_aggregates_unreadable": True})
    if not s_agg > EXPECT["shipped_CD_aggregate_gt"]:
        refuse("G-PROV", {"shipped_CD_aggregate": s_agg,
                          "must_exceed": EXPECT["shipped_CD_aggregate_gt"]})
    if not p_agg <= EXPECT["patched_CD_aggregate_le"]:
        refuse("G-PROV", {"patched_CD_aggregate": p_agg,
                          "must_not_exceed": EXPECT["patched_CD_aggregate_le"]})
    return {"path": D15_GRADE, "md5": got, "verdict": g["verdict"], "rows": rows,
            "shipped_CD_aggregate_rel_err_pct": s_agg,
            "patched_CD_aggregate_rel_err_pct": p_agg,
            "shipped_worst_component_rel_err_pct": EXPECT["shipped_worst_component_measured"],
            "suffix": SUFFIX}


def require_travelling_provenance(out, refuse=None):
    """G-PROV, THE ENFORCEMENT STEP -- AND IT IS THE CALL SITE.

    No verdict leaves this item without its upstream provenance.  Called on the
    output object immediately before it is written, so the requirement cannot be
    met by intention: it is met by the bytes or the emit REFUSES.

    Returns `out` unchanged on success so it can wrap an emit expression directly
    and cannot be forgotten by a caller who merely calls it and drops the result.
    """
    refuse = refuse or _local_refuse
    verdict = out.get("verdict")
    if verdict not in VOCAB:
        refuse("G-PROV", {"verdict_outside_the_fixed_vocabulary": verdict, "vocab": sorted(VOCAB)})
    prov = read_upstream(refuse=refuse)
    carried = out.get("provenance") or {}
    if carried.get("md5") != prov["md5"] or carried.get("path") != prov["path"]:
        refuse("G-PROV", {"provenance_not_carried": True, "carried": carried,
                          "note": "the SHIPPED GATE FAIL must travel attached to the verdict"})
    if SUFFIX not in str(out.get("verdict_statement", "")):
        refuse("G-PROV", {"suffix_absent_from_verdict_statement": True,
                          "required_suffix": SUFFIX,
                          "note": "section 9: a D19 number quoted without it is quoted wrongly"})
    return out


def selftest():
    """The guard must ACCEPT a correct emit and REFUSE every way of getting it wrong."""
    prov = read_upstream()
    ok = {"verdict": "PASS", "provenance": prov,
          "verdict_statement": "PASS " + SUFFIX}
    n_pass = n_refused = 0
    require_travelling_provenance(dict(ok))
    n_pass += 1

    bad_cases = {
        "verdict_outside_vocab": dict(ok, verdict="roughly converged"),
        "provenance_absent": {k: v for k, v in ok.items() if k != "provenance"},
        "provenance_md5_wrong": dict(ok, provenance=dict(prov, md5="0" * 32)),
        "provenance_path_wrong": dict(ok, provenance=dict(prov, path="/tmp/elsewhere.json")),
        "suffix_missing": dict(ok, verdict_statement="PASS"),
        "suffix_truncated": dict(ok, verdict_statement="PASS on the PATCHED toolchain"),
    }
    for name, bad in bad_cases.items():
        try:
            require_travelling_provenance(bad)
        except Refusal:
            n_refused += 1
            print("  %-24s REFUSED" % name)
            continue
        print("  %-24s ACCEPTED -- THE GUARD IS BLIND" % name)
        return 2
    print("  %-24s ACCEPTED (correct emit)" % "well_formed_verdict")
    print("G-PROV selftest OK: %d accepted, %d refused" % (n_pass, n_refused))
    print("upstream: %s" % prov["path"])
    print("  md5 %s  verdict %s  rows %s" % (prov["md5"], prov["verdict"], json.dumps(prov["rows"])))
    print("  SHIPPED CD aggregate %.6f %% (> 5.0)   PATCHED CD aggregate %.6f %% (<= 5.0)"
          % (prov["shipped_CD_aggregate_rel_err_pct"], prov["patched_CD_aggregate_rel_err_pct"]))
    return 0


def main():
    try:
        if "--selftest" in sys.argv:
            return selftest()
        prov = read_upstream()
        print(json.dumps(prov, indent=1, sort_keys=True))
        return 0
    except Refusal as e:
        sys.stderr.write("D19_PRECONDITION REFUSED: %s\n" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
