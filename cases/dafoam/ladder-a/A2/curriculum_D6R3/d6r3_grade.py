#!/usr/bin/env python3
"""
D6R3 GRADER -- the production gates of PREREGISTRATION.md (R4) section 7b.

DRAFT.  Nothing here launches compute.  Nothing is sent, filed or submitted (rule 7).

EVERY THRESHOLD, LITERAL, COMPARISON DIRECTION AND LABEL IS COPIED VERBATIM FROM SECTION 7b, and
each constant below carries the sentence it was copied from.  Where section 7b is ambiguous this
instrument does NOT resolve the ambiguity: it computes the strict reading, reports the alternative
beside it, and REFUSES (exit 2) rather than pick.

THE VERDICT VOCABULARY IS FIXED (CLAUDE.md rule 1): PASS / GATE REACHED / GATE FAIL / NOT A RESULT.
"""
import argparse, json, math, os, re, sys

VERSION = "D6R3-GRADE-DRAFT-1"

# "BAND-CL05 ... cl05's own drag reduction against the page's 7.6 % (0.02090 -> 0.01932), and
#  cl05's baseline CD against 0.02090."   Source: dafoam_crm_tutorial_page.txt line 131,
#  md5 a536f12b9b71703c62932e0248fa672b, retrieved 2026-09-13T18:22:27Z from
#  https://dafoam.github.io/tutorials-aero-crm.html (HTTP 200), title-page verified by <title>.
BAND_CD0 = 0.02090
BAND_CDF = 0.01932
BAND_PCT = 7.6
# "Tolerance registered before the run: baseline within +/- 2 % of 0.02090; reduction within
#  +/- 2 percentage points of 7.6 %."
BAND_CD0_REL = 0.02
BAND_PCT_ABS = 2.0
# "G3 -- the lift equalities.  max_i |CL_i - target_i| <= 1.0e-3 at the final design, and
#  <= 1.0e-4 for any value entering a ratio."
G3_TOL = 1.0e-3
G3_RATIO_TOL = 1.0e-4
CL_TARGETS = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}
WEIGHTS = {"cl04": 0.25, "cl05": 0.50, "cl06": 0.25}
# "MAXIT = 100 is a BUDGET, not a tolerance, and a run that reaches it is GATE REACHED, never PASS."
PUBLISHED_MAXIT = 100
PLANT = 1.234e-03


class Refusal(Exception):
    pass


def _finite(*v):
    for x in v:
        if x is None:
            raise Refusal("non-finite: None")
        try:
            f = float(x)
        except (TypeError, ValueError):
            raise Refusal("non-finite: %r is not a number" % (x,))
        if not math.isfinite(f):
            raise Refusal("non-finite: %r" % (f,))


def _counts(ok, bad, tot):
    if ok + bad != tot:
        raise Refusal("count identity failed: %d + %d != %d" % (ok, bad, tot))
    return {"n_ok": ok, "n_bad": bad, "n_total": tot}


def gate_g1(rc, slsqp_text, artefact_newer_than_datum):
    """G1 -- the optimiser terminated at its published budget."""
    if rc is None:
        raise Refusal("G1: rc not readable")
    if slsqp_text is None:
        raise Refusal("G1: opt_SLSQP.txt not readable -- a gate whose channel has no writer "
                      "defaults to success, and this one refuses instead (rule 27)")
    if not artefact_newer_than_datum:
        return {"gate": "G1", "ok": False, "why": "artefacts not newer than the age datum"}
    if int(rc) != 0:
        return {"gate": "G1", "ok": False, "why": "rc=%d" % int(rc)}
    m = re.search(r"NUMBER OF ITERATIONS\s*[=:]\s*(\d+)", slsqp_text, re.I)
    n_iter = int(m.group(1)) if m else None
    return {"gate": "G1", "ok": True, "n_iter": n_iter,
            "at_budget": (n_iter == PUBLISHED_MAXIT) if n_iter is not None else None,
            "derived_from": "section 7b G1; PUBLISHED_MAXIT copied from runScript.py:253"}


def gate_band_cl05(cd0_cl05, cdf_cl05, cl_miss_cl05):
    """BAND-CL05 -- the reproduction gate.  The published band binds cl05 ALONE."""
    _finite(cd0_cl05, cdf_cl05, cl_miss_cl05)
    cd0, cdf = float(cd0_cl05), float(cdf_cl05)
    if cd0 <= 0:
        raise Refusal("BAND-CL05: baseline CD is not positive (%r)" % cd0)
    # rule 19 / section 5 T1: a value entering a ratio must be at matched lift.
    if float(cl_miss_cl05) > G3_RATIO_TOL:
        raise Refusal("BAND-CL05: cl05 is NOT at matched lift -- |CL-target| = %.6e against %.1e. "
                      "A drag ratio across different lifts is not a number (rule 19)."
                      % (float(cl_miss_cl05), G3_RATIO_TOL))
    base_rel = abs(cd0 - BAND_CD0) / BAND_CD0
    pct = 100.0 * (cd0 - cdf) / cd0
    base_ok = base_rel <= BAND_CD0_REL
    pct_ok = abs(pct - BAND_PCT) <= BAND_PCT_ABS
    counts = _counts(int(base_ok) + int(pct_ok), int(not base_ok) + int(not pct_ok), 2)
    return {"gate": "BAND-CL05", "ok": base_ok and pct_ok,
            "baseline_cd05": cd0, "published_baseline": BAND_CD0,
            "baseline_rel_err": base_rel, "baseline_ok": base_ok,
            "reduction_pct": pct, "published_pct": BAND_PCT, "reduction_ok": pct_ok,
            "counts": counts,
            "derived_from": "dafoam_crm_tutorial_page.txt:131, quoted in PREREGISTRATION R4 s1b"}


def report_gj(cd_by_point, cl_miss):
    """G-J -- the weighted objective is REPORTED with BAND: NOT AVAILABLE.  It is NOT gated."""
    for p in CL_TARGETS:
        if p not in cd_by_point:
            raise Refusal("G-J: condition %r missing" % p)
        _finite(cd_by_point[p], cl_miss.get(p))
    worst = max(float(cl_miss[p]) for p in CL_TARGETS)
    if worst > G3_RATIO_TOL:
        raise Refusal("G-J: a weighted objective formed at unconverged lift is not a number "
                      "(worst |CL-target| = %.6e)" % worst)
    J = sum(WEIGHTS[p] * float(cd_by_point[p]) for p in CL_TARGETS)
    return {"report": "G-J", "J": J, "band": "NOT AVAILABLE",
            "why": "the tutorial is single-point at CL 0.5; a weighted number is never compared "
                   "against a single-point published figure (PREREGISTRATION R4 s1c)"}


def gate_g3(cl_final):
    """G3 -- the lift equalities at the final design."""
    for p in CL_TARGETS:
        if p not in cl_final:
            raise Refusal("G3: condition %r missing from the final design record" % p)
        _finite(cl_final[p])
    miss = {p: abs(float(cl_final[p]) - CL_TARGETS[p]) for p in CL_TARGETS}
    worst = max(miss.values())
    bad = sum(1 for v in miss.values() if v > G3_TOL)
    return {"gate": "G3", "ok": worst <= G3_TOL, "miss": miss, "worst": worst, "tol": G3_TOL,
            "counts": _counts(len(miss) - bad, bad, len(miss))}


def label(g1, band, g3, cap_crossed):
    """Section 7b's label rule.  No synonyms, no hedging (rule 1)."""
    if cap_crossed:
        return "NOT A RESULT"
    if not g1["ok"]:
        return "NOT A RESULT"
    if not g3["ok"]:
        return "GATE FAIL"
    if not band["ok"]:
        return "GATE FAIL"
    return "GATE REACHED" if g1.get("at_budget") else "PASS"


def _c(name, fn, want):
    try:
        got = fn()
    except Refusal as e:
        got = "REFUSE:" + str(e)[:70]
    ok = (got == want) if not isinstance(want, str) or not want.startswith("REFUSE") \
        else str(got).startswith("REFUSE")
    return {"control": name, "want": want, "got": got, "PASS": ok}


def selftest(verbose=True):
    r = []
    matched = {p: 0.0 for p in CL_TARGETS}
    clf = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}

    r.append(_c("G1.clean -- rc=0, 100 iterations, artefacts newer",
                lambda: gate_g1(0, "NUMBER OF ITERATIONS = 100", True)["ok"], True))
    r.append(_c("G1.KNOWN-BAD -- rc=137 (OOM)", lambda: gate_g1(137, "x", True)["ok"], False))
    r.append(_c("G1.KNOWN-BAD -- artefacts not newer than the age datum",
                lambda: gate_g1(0, "x", False)["ok"], False))
    r.append(_c("G1.BLIND -- opt_SLSQP.txt unreadable: a gate with no writer must REFUSE",
                lambda: gate_g1(0, None, True), "REFUSE"))
    r.append(_c("G1.budget -- reaching MAXIT 100 is GATE REACHED, never PASS",
                lambda: label(gate_g1(0, "NUMBER OF ITERATIONS = 100", True),
                              gate_band_cl05(0.02090, 0.01932, 0.0), gate_g3(clf), False),
                "GATE REACHED"))
    # BAND-CL05, driven on the PUBLISHED numbers themselves
    r.append(_c("BAND.PUBLISHED -- the page's own 0.02090 -> 0.01932 must PASS its own band",
                lambda: gate_band_cl05(0.02090, 0.01932, 0.0)["ok"], True))
    r.append(_c("BAND.A6 -- A6's independently measured baseline 0.02090143421526141 must PASS",
                lambda: gate_band_cl05(0.02090143421526141, 0.01932, 0.0)["baseline_ok"], True))
    r.append(_c("BAND.KNOWN-BAD -- a baseline 5 % off the published value fails",
                lambda: gate_band_cl05(0.02090 * 1.05, 0.01932, 0.0)["baseline_ok"], False))
    r.append(_c("BAND.KNOWN-BAD -- a 2.0 % reduction against the published 7.6 % fails",
                lambda: gate_band_cl05(0.02090, 0.02090 * 0.98, 0.0)["reduction_ok"], False))
    r.append(_c("BAND.boundary -- 9.6 % (exactly 2 points high) still passes",
                lambda: gate_band_cl05(0.02090, 0.02090 * (1 - 0.096), 0.0)["reduction_ok"], True))
    r.append(_c("BAND.boundary -- 9.7 % (2.1 points high) fails",
                lambda: gate_band_cl05(0.02090, 0.02090 * (1 - 0.097), 0.0)["reduction_ok"], False))
    r.append(_c("BAND.RULE-19 -- an off-target cl05 must REFUSE, not report a ratio",
                lambda: gate_band_cl05(0.02090, 0.01932, 1.0e-3), "REFUSE"))
    r.append(_c("BAND.PLANT -- a plant of 1.234e-03 on a CD of 0.0209 (5.9 %) must be seen",
                lambda: gate_band_cl05(0.02090 + PLANT, 0.01932, 0.0)["baseline_ok"], False))
    r.append(_c("BAND.NON-FINITE -- NaN baseline must REFUSE",
                lambda: gate_band_cl05(float("nan"), 0.01932, 0.0), "REFUSE"))
    # G-J
    r.append(_c("GJ.clean -- the weighted objective is reported with BAND: NOT AVAILABLE",
                lambda: report_gj({"cl04": 0.021, "cl05": 0.0209, "cl06": 0.023},
                                  matched)["band"], "NOT AVAILABLE"))
    r.append(_c("GJ.RULE-19 -- an off-target condition must REFUSE",
                lambda: report_gj({"cl04": 0.021, "cl05": 0.0209, "cl06": 0.023},
                                  dict(matched, cl06=1.0e-3)), "REFUSE"))
    r.append(_c("GJ.BLIND -- a missing condition must REFUSE",
                lambda: report_gj({"cl04": 0.021, "cl05": 0.0209}, matched), "REFUSE"))
    # G3
    r.append(_c("G3.clean -- all three lifts on target", lambda: gate_g3(clf)["ok"], True))
    r.append(_c("G3.KNOWN-BAD/MEASURED -- D6R2C's own final misses 5.539e-4 / 1.210e-3 / 2.787e-3",
                lambda: gate_g3({"cl04": 0.4 + 5.539e-4, "cl05": 0.5 + 1.210e-3,
                                 "cl06": 0.6 + 2.787e-3})["ok"], False))
    r.append(_c("G3.NON-FINITE -- a NaN CL must REFUSE (the parent's gate_g3 defect exactly)",
                lambda: gate_g3({"cl04": float("nan"), "cl05": 0.5, "cl06": 0.6}), "REFUSE"))
    r.append(_c("G3.BLIND -- a missing condition must REFUSE",
                lambda: gate_g3({"cl04": 0.4, "cl05": 0.5}), "REFUSE"))
    # labels
    g1ok = gate_g1(0, "NUMBER OF ITERATIONS = 12", True)
    r.append(_c("LABEL -- G3 misses -> GATE FAIL",
                lambda: label(g1ok, gate_band_cl05(0.02090, 0.01932, 0.0),
                              gate_g3({"cl04": 0.4 + 2e-3, "cl05": 0.5, "cl06": 0.6}), False),
                "GATE FAIL"))
    r.append(_c("LABEL -- band misses -> GATE FAIL",
                lambda: label(g1ok, gate_band_cl05(0.02090, 0.02090 * 0.98, 0.0),
                              gate_g3(clf), False), "GATE FAIL"))
    r.append(_c("LABEL -- G1 fails -> NOT A RESULT",
                lambda: label(gate_g1(137, "x", True), gate_band_cl05(0.02090, 0.01932, 0.0),
                              gate_g3(clf), False), "NOT A RESULT"))
    r.append(_c("LABEL -- cap crossed -> NOT A RESULT, and the cap is never raised",
                lambda: label(g1ok, gate_band_cl05(0.02090, 0.01932, 0.0), gate_g3(clf), True),
                "NOT A RESULT"))
    r.append(_c("LABEL -- everything holds below the budget -> PASS",
                lambda: label(g1ok, gate_band_cl05(0.02090, 0.01932, 0.0), gate_g3(clf), False),
                "PASS"))

    n_pass = sum(1 for x in r if x["PASS"]); n_fail = len(r) - n_pass
    assert n_pass + n_fail == len(r)
    if verbose:
        for x in r:
            print("%-6s want=%-14r got=%-14r %s" % ("PASS" if x["PASS"] else "FAIL",
                                                    x["want"], x["got"], x["control"]))
        print("\nD6R3_GRADE SELFTEST  n_total=%d  n_pass=%d  n_fail=%d" % (len(r), n_pass, n_fail))
        print("D6R3_GRADE SELFTEST %s" % ("PASS" if n_fail == 0 else "FAIL"))
    return r, n_pass, n_fail


def main(argv=None):
    ap = argparse.ArgumentParser(prog="d6r3_grade.py")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", default=None)
    ap.add_argument("--version", action="store_true")
    a = ap.parse_args(argv)
    if a.version:
        print(VERSION); return 0
    if not a.selftest:
        ap.print_help(); return 64
    r, np_, nf = selftest()
    if a.json:
        json.dump({"version": VERSION, "n_total": len(r), "n_pass": np_, "n_fail": nf,
                   "controls": r}, open(a.json, "w"), indent=1, default=str)
        print("wrote %s" % a.json)
    return 0 if nf == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
