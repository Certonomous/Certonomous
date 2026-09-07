#!/usr/bin/env python3
"""Curriculum D6RF6 -- `PREREGISTRATION.md` section 3f's TWO-DIRECTION MUTATION
HARNESS.  It is the executable control on the finiteness clause, and it exists
because **a restrictive repair is not self-certifying**.

WHY IT IS A SEPARATE FILE AND NOT A BLOCK INSIDE THE GRADER, stated as a reason
rather than left as a preference: `d6rf6_grade.py` IS the grading path frozen by
`CLAUDE.md` rule 2, and it is the one file in this item a reviewer must be able
to read line by line.  Two hundred lines of fixture construction inside it are
dead weight on every such read, forever.  The supervisor may overrule this and
inline it; nothing in the clause requires the separation.  What the clause DOES
require is that the harness exist and be driven, and it is.

WHAT SECTION 3f REGISTERS, and what this file therefore does:

  > Every value the grader reads from an artefact and compares against a
  > threshold is checked finite at the point of reading.  A non-finite value
  > makes its gate NOT A RESULT with reason `NON_FINITE_INPUT`, naming the
  > artefact, the key and the token as read.  It is NEVER `GATE FAIL` and never
  > `PASS`.

  ... and it ships with a harness that writes `NaN`, `+Inf` and `-Inf` into a
  copy of each gated input IN TURN and requires the corresponding gate to
  return `NOT A RESULT` with reason `NON_FINITE_INPUT` -- AND requires the
  UNMUTATED control to return a verdict that is NOT `NOT A RESULT`.
  **Both directions, or the clause is not established.**

THE SECOND DIRECTION IS THE ONE THAT MATTERS AND IT IS THE ONE HARNESSES SKIP.
A guard that returns `NOT A RESULT` for everything satisfies direction 1
perfectly and is worthless.  Every gate below is therefore driven UNMUTATED
first, and a gate that cannot produce a non-`NOT A RESULT` verdict on clean
data FAILS THIS HARNESS -- which is falsifier `F2`: if the harness fails in
EITHER direction the clause is not established, `D6RF3-DEF-5` is not repaired,
and the item reports `NOT A RESULT` for want of a working guard rather than
shipping gates it cannot trust.

AND THE LESSON THIS FAMILY PAID FOR TWICE THIS WEEK: **a control that passes
for a reason unrelated to its name is not a control.**  Direction 1 therefore
asserts THE REASON -- verdict `NOT A RESULT` **and** `reason ==
NON_FINITE_INPUT` **and** the recorded `non_finite` detail naming the artefact
and the key that was mutated.  A gate that returned `NOT A RESULT` because a
fixture was malformed would satisfy a verdict-only check and prove nothing.

`5` GATED INPUT FAMILIES ARE DRIVEN, and they are section 3f's registered
binding list VERBATIM AND NOT WIDENED: `G-OFF`, `G-PRICE`, `G-FD`, `G-DVL`,
`R-RED`.  It is deliberately NOT extended to `G-CAPS`/`G1`, which also parse
floats from the ledger unchecked -- widening a registered clause inside its own
control is how a clause stops meaning what it was frozen meaning.  That gap is
REPORTED to the supervisor, not silently closed.

NO COMPUTE.  Every fixture is built here from constants; no container starts.
NO `assert` STATEMENT APPEARS IN THIS FILE.
"""
import json
import math
import os
import re
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import d6rf6_grade as G                                          # noqa: E402

NONFINITE = (("NaN", float("nan")), ("+Inf", float("inf")),
             ("-Inf", float("-inf")))

# A clean, finite fixture set.  The CD values are section 2b's stdout-recovered
# numbers; the REF_off values are set ABOVE them so the unmutated G-OFF has a
# definite, non-`NOT A RESULT` verdict (PASS) rather than an accidental one.
CD_MP = {"cl04": 1.846929883e-02, "cl05": 2.176156349e-02,
         "cl06": 2.696277508e-02}
CD_REF = {p: v * 1.05 for p, v in CD_MP.items()}
CL_REF = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}
# THE FIXTURE CENSUS, AND IT IS SYNTHETIC ON PURPOSE.  `REF_off` is NOT a
# registered arm of D6RF6 (PREREGISTRATION.md section 8.2) and on a real
# grading run its census state is NOT_REGISTERED_AT_THIS_FREEZE, which makes
# G-OFF read NOT A RESULT for want of an input.  THE CLAUSE UNDER TEST HERE IS
# THE FINITENESS FOLD, WHICH IS PER-GATE AND ARM-AGNOSTIC, so the fixture gives
# both arms a RAN state in order to reach the fold at all.  Saying so here
# rather than letting a reader infer that D6RF6 buys a REF_off arm.
CENSUS = {"P_conv": {"state": "RAN", "source": "fixture"},
          "REF_off": {"state": "RAN", "source": "fixture"}}


def _w(path, doc):
    with open(path, "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)


def _fd_doc():
    """The shape `d6rf6_fd_endpoint.py` writes, with `points` (section 2a's
    registered CD path) and five PLANNED FD rows inside band D."""
    rows = []
    for i, (dv, idx) in enumerate((("shape", 46), ("shape", 18), ("shape", 0),
                                   ("twist", 0), ("patchV_cl05", 1))):
        j = 1.0e-3 * (i + 1)
        d_hi = j * 1.01                       # 0.99 % rel err, inside 5.0 %
        d_lo = d_hi * 1.01                    # 1.0 % plateau, inside 10.0 %
        rows.append({"dv": dv, "idx": idx, "status": "PLANNED",
                     "s_lo": 1.0e-3, "s_hi": 3.0e-3, "J_adj": repr(j),
                     "fd": {"s_lo": {"ok": True, "step": 1.0e-3,
                                     "d": repr(d_lo)},
                            "s_hi": {"ok": True, "step": 3.0e-3,
                                     "d": repr(d_hi)}}})
    return {"points": {p: {"CD": repr(CD_MP[p]), "CL": repr(CL_REF[p])}
                       for p in G.POINTS},
            "points_baseline": {p: {"CD": repr(CD_MP[p]), "CL": repr(CL_REF[p])}
                                for p in G.POINTS},
            "points_source": "FD_BASELINE_PRIMAL",
            "J_baseline": repr(0.022238800232340834),
            "J_baseline_repeat": repr(0.022238800232340840),
            "eta_raw": repr(6.0e-18), "eta_used": repr(1.0e-14),
            "eta_floored": True, "producer_md5": "fixture",
            "rows": rows, "n_rows": len(rows)}


def _ref_doc():
    return {"points": {p: {"CD": repr(CD_REF[p]), "CL": repr(CL_REF[p])}
                       for p in G.POINTS},
            "consistency_CD_cl05_minus_D4_CD_f": "0.0"}


def _hist_doc():
    return {"_source": "fixture", "_n_major_rows": 80,
            "J": [2.60e-2] + [2.03e-2] * 79}


def _dv_doc():
    """A PHYSICAL design-vector artefact carrying every registered family, with
    finite values.  `G-DVL` may still GATE FAIL on the locus controls -- that
    is fine and is the point: `GATE FAIL` is NOT `NOT A RESULT`, so direction 2
    is satisfied by it, while direction 1 must still convert it to `NOT A
    RESULT` when a component is mutated."""
    return {"_units": "PHYSICAL", "_source": "fixture",
            "twist": [0.5, -0.25], "shape": [1.0e-3 * (i + 1) for i in range(8)],
            "patchV_cl04": [30.0, 1.5], "patchV_cl05": [30.0, 2.0],
            "patchV_cl06": [30.0, 2.5]}


LEDGER_ROW = (
    "ARM={arm} ROW=PATCHED IMG=dafoam-idwarp-rot:v1 DIGEST={dig} rc=0 "
    "wall_s={wall} ranks=4 core_min={cm} cap_core_min={cap} "
    "enforced_wall_s={tmo} enforced_core_min={cap} memory=20g "
    "inspect(exit,oomkilled)=[0 false] container_wall_s={cw} "
    "frame_allowance_s=90 memavail_pre_GiB=26.00 memavail_post_GiB=26.00 "
    "cpuset=2,3,4,14 delivered_cores_mean=[3.9900 n=10 max_nr_throttled=0] "
    "siblings_pre=[] siblings_post=[] log={arm}_fix.log\n")


def _ledger(path, overrides=None):
    """A clean two-arm ledger. `overrides` replaces one field's TOKEN AS TEXT,
    which is how a real malformed ledger arrives -- the mutation must go in as
    the launcher would have written it, not as a Python float."""
    ov = overrides or {}
    with open(path, "w") as fh:
        fh.write("ITEM=D6RF6 staged=fixture\n")
        # ONLY THE REGISTERED ARM GETS A LEDGER ROW.  `arm_census` REFUSES on
        # a ledger row for an unregistered arm -- it would mean this item
        # bought compute it never registered -- so the fixture must not write
        # one either, or the harness would be testing a state the grader
        # forbids.
        for arm in G.ARMS:
            row = LEDGER_ROW.format(arm=arm, dig=G.DIGEST_PATCHED,
                                    wall=1000, cm=10.0, cap=G.CAPS[arm],
                                    tmo=G.TMO[arm], cw=995)
            for field, token in ov.get(arm, {}).items():
                row = re.sub(r'(?<= )%s=\S+' % re.escape(field),
                             "%s=%s" % (field, token), row)
            fh.write(row)


def _ledger_rows(path):
    rows, _ = G.parse_ledger(path)
    return rows


def _d4_ipopt(path):
    with open(path, "w") as fh:
        fh.write("Number of Iterations....: 80\n\n"
                 "Objective...............:   %.16e    %.16e\n\n"
                 "EXIT: Optimal Solution Found.\n"
                 % (G.CD_F_D4_RECORDED, G.CD_F_D4_RECORDED))


def build(root, ledger_overrides=None):
    """A complete two-arm fixture: every REGISTERED_PRODUCT, an age datum older
    than every product, a terminal-line log for the SOLVER arm, an `.ok.`
    marker for the SCRIPT arm, a ledger and D4's reference. Complete enough
    that `G1` and `G-CAPS` are drivable, which the section 3f WIDENING of
    2026-09-05 requires -- a widened clause is not established until the gates
    it was widened to have been driven in both directions like the rest."""
    if os.path.isdir(root):
        shutil.rmtree(root)
    for a in ("P_conv", "REF_off"):
        os.makedirs(os.path.join(root, a))
    datum = time.time() - 100.0
    f = os.path.join(root, "P_conv")
    _w(os.path.join(f, "d6rf6_fd_endpoint.json"), _fd_doc())
    _w(os.path.join(f, "d6rf6_major_history.json"), _hist_doc())
    _w(os.path.join(f, "d6rf6_endpoint_dvs_PHYSICAL.json"), _dv_doc())
    _w(os.path.join(f, "d6rf6_endpoint_dvs_DRIVERSCALED.json"), _dv_doc())
    _w(os.path.join(f, "d6rf6_endpoint_dvs.json"), _dv_doc())
    _w(os.path.join(f, "d6rf6_f5_endpoint.json"), _fd_doc())
    r = os.path.join(root, "REF_off")
    _w(os.path.join(r, "d6rf6_ref_off.json"), _ref_doc())
    _w(os.path.join(r, "d4_endpoint_dvs_PHYSICAL.json"), _dv_doc())
    _w(os.path.join(r, "d4_endpoint_dvs.json"), _dv_doc())
    for a in ("P_conv", "REF_off"):
        with open(os.path.join(root, a, ".d4_age_datum"), "w") as fh:
            fh.write("%.3f" % datum)
        log = os.path.join(root, "%s_fix.log" % a)
        with open(log, "w") as fh:
            fh.write("start\nD4S_IDWARP_SO_MD5: %s\n%s\n"
                     % (G.IDWARP_SO_MD5, G.TERMINAL_STATEMENT))
        if G.ARM_KIND[a] != "SOLVER":
            open(log + ".ok.fix", "w").close()
    d4 = os.path.join(root, "d4_opt_IPOPT.txt")
    _d4_ipopt(d4)
    _ledger(os.path.join(root, "ledger.txt"), ledger_overrides)
    return d4


# --------------------------------------------------------------- mutation ---
def _mutate(path, keypath, value):
    """Write `value` at `keypath` in a JSON artefact IN PLACE.  `keypath` is a
    list of dict keys / list indices, so the mutation is BY KEY and never by
    line index: these files are written `sort_keys=True` and a line-index
    mutation would silently follow whatever sorted into that position."""
    with open(path) as fh:
        doc = json.load(fh)
    node = doc
    for k in keypath[:-1]:
        node = node[k]
    node[keypath[-1]] = repr(value)
    _w(path, doc)


# ------------------------------------------------- the five gated families ---
def _cases(root, d4):
    """(label, gate-callable, artefact path, key path) -- section 3f's
    REGISTERED binding list, verbatim, NOT widened."""
    f = os.path.join(root, "P_conv")
    r = os.path.join(root, "REF_off")
    fd = os.path.join(f, "d6rf6_fd_endpoint.json")
    ref = os.path.join(r, "d6rf6_ref_off.json")
    hist = os.path.join(f, "d6rf6_major_history.json")
    dv = os.path.join(f, "d6rf6_endpoint_dvs_PHYSICAL.json")
    rs = os.path.join(HERE, "d6rf6_opt_runScript.py")

    def off():
        return G.gate_off(root, CENSUS)

    def price():
        return G.gate_price(root, CENSUS, {})

    def gfd():
        return G.gate_fd(root, CENSUS)

    def dvl():
        return G.gate_dvl(root, CENSUS, rs, rs)

    def red():
        return G.report_reduction(root, CENSUS)

    # (label, gate, artefact, JSON path to mutate, key the GRADER must name)
    return [
        ("G-OFF   CD_i(mp)      ", off, fd, ["points", "cl05", "CD"],
         "points.cl05.CD"),
        ("G-OFF   CD_i(REF_off) ", off, ref, ["points", "cl04", "CD"],
         "points.cl04.CD"),
        ("G-OFF   CL_i(REF_off) ", off, ref, ["points", "cl04", "CL"],
         "points.cl04.CL"),
        ("G-PRICE CD_cl05(mp)   ", price, fd, ["points", "cl05", "CD"],
         "points.cl05.CD"),
        ("G-FD    J_adj         ", gfd, fd, ["rows", 0, "J_adj"], "J_adj"),
        ("G-FD    d(s_hi)       ", gfd, fd, ["rows", 0, "fd", "s_hi", "d"],
         "fd.s_hi.d"),
        ("G-FD    d(s_lo)       ", gfd, fd, ["rows", 0, "fd", "s_lo", "d"],
         "fd.s_lo.d"),
        ("G-FD    eta_used      ", gfd, fd, ["eta_used"], "eta_used"),
        ("G-DVL   shape[0]      ", dvl, dv, ["shape", 0], "shape[0]"),
        ("R-RED   J[-1]         ", red, hist, ["J", 79], "J[-1]"),
    ]


def _is_nar(res):
    """`R-RED` is a REPORTED row and carries no verdict; its section 3c
    obligation is the DISCLOSURE.  Both shapes are read here rather than
    pretending a reported row has a verdict."""
    if "verdict" in res:
        return res.get("verdict") == "NOT A RESULT"
    return res.get("value_pct") is None and "reason" in res


def _reason_ok(res, artefact, expect_key):
    """THE REASON, not the token.  A gate that says `NOT A RESULT` without
    `NON_FINITE_INPUT`, or without naming the artefact and key that were
    mutated, has not demonstrated the clause."""
    d = res.get("non_finite")
    if d is None:
        for row in list((res.get("per_point") or {}).values()) \
                + list(res.get("components") or []) \
                + list((res.get("arms") or {}).values()):
            if isinstance(row, dict) and row.get("non_finite"):
                d = row["non_finite"]
                break
    if not isinstance(d, dict):
        return False, "no non_finite detail recorded"
    if d.get("reason") != G.NON_FINITE_REASON:
        return False, "reason is %r not %r" % (d.get("reason"),
                                               G.NON_FINITE_REASON)
    if os.path.basename(artefact) not in str(d.get("artefact")):
        return False, "artefact %r does not name %r" % (d.get("artefact"),
                                                        artefact)
    # `expect_key` is stated per case rather than derived from the mutation's
    # JSON path, because the two are legitimately different: the harness
    # mutates `J[79]` by index while the grader names the key it READ, `J[-1]`
    # -- the endpoint. Deriving the expectation from the mutation would make
    # this check assert the harness's own bookkeeping instead of the grader's
    # disclosure, which is the failure this whole file exists to prevent.
    if expect_key not in str(d.get("key")):
        return False, "key %r does not name %r" % (d.get("key"), expect_key)
    return True, "reason=%s artefact=%s key=%s token=%s" % (
        d.get("reason"), d.get("artefact"), d.get("key"),
        d.get("token_as_read"))


LEDGER_CASES = (
    ("G-CAPS  core_min      ", "caps", "P_conv", "core_min"),
    ("G-CAPS  container_wall", "caps", "P_conv", "container_wall_s"),
    ("G-CAPS  frame_allow   ", "caps", "P_conv", "frame_allowance_s"),
    ("G1      core_min      ", "g1", "P_conv", "core_min"),
    ("G1      wall_s        ", "g1", "P_conv", "wall_s"),
)


# ============ THE TWO NEW GATES ARE WIRED INTO THE SAME FOLD ================
# PREREGISTRATION.md section 3.4: "G-CONV (and G-SCHEME's reported CD/CL) are wired into the same
# fold, so the new gates inherit the restriction rather than sitting
# outside it. THIS IS A NON-REGRESSION REQUIREMENT, AND section 7 ASSERTS IT
# EXECUTABLY."  A clause asserted only in prose about a NEW gate is a clause
# whose newest call sites are the untested ones (CLAUDE.md rule 14's shape).
LEG_LOG_CLEAN = """\
D6RF6_FVSCHEMES_INSTALLED leg=L1_L2 md5={fvmd5} sites=1 file=d6rf6_fvSchemes_LIMITED
D6RF6_LEG_BEGIN baseline mode=P_conv
    primalMinResTol 1e-08;
    primalMinResTolDiff 1000;

Time = 1000

U0 initRes: 1.1e-08 finalRes: 1.0e-11 nIters: 3
U1 initRes: 1.2e-08 finalRes: 1.0e-11 nIters: 3
U2 initRes: 1.3e-08 finalRes: 1.0e-11 nIters: 3
he initRes: 1.4e-09 finalRes: 1.0e-12 nIters: 3
p initRes: {p0} finalRes: 1.0e-10 nIters: 8
p initRes: {p1} finalRes: 1.0e-10 nIters: 8
p initRes: {p2} finalRes: 1.0e-10 nIters: 8
p initRes: {p3} finalRes: 1.0e-10 nIters: 8
nuTilda initRes: {nut} finalRes: 1.0e-10 nIters: 3
CD: {cd} final: {cd}
CL: {cl} final: {cl}
ExecutionTime = 118.3 s  ClockTime = 119 s

End
D6RF6_LEG_END baseline mode=P_conv J=0.0222 wall_s=118.300 primal_raised=False
Finalising parallel run
"""


def _leg_log(path, p0="1.30e-07", p1="9.0e-08", p2="7.0e-08", p3="6.0e-08",
             nut="1.10e-07", cd="0.0184758685", cl="0.3999751808", fvmd5=None):
    # THE FVSCHEMES INSTALL MARKER IS PART OF THE FIXTURE, because read_legs
    # binds each leg to the fvSchemes installed before it and gate_scheme reads
    # that binding; a fixture without the marker would test that refusal instead
    # of the finiteness fold it is here for.  FOUR p-solve lines reproduce the
    # 1 + nNonOrthogonalCorrectors (== 3) per-corrector solves, so read_legs
    # records p_first_uncorrected (p0) and p_corrected (p3) and counts 4 solves
    # (gate_scheme reads nCorr = 4 - 1 = 3).  The md5 is read FROM THE GRADER'S
    # OWN REGISTERED TABLE, never retyped.
    with open(path, "w") as fh:
        fh.write(LEG_LOG_CLEAN.format(
            p0=p0, p1=p1, p2=p2, p3=p3, nut=nut, cd=cd, cl=cl,
            fvmd5=fvmd5 or G.FVSCHEMES_MD5[G.LEG_FVSCHEMES["L1"]]))
    return path


# a synthetic accept-floor result: gate_scheme reads floor.accept_floor_unmoved,
# which grade() produces from afc.run_floor_control on the real log.  The
# finiteness fold under test is the per-field / CD/CL read, not the floor, so a
# clean pass-state floor is handed in here.
FLOOR_PASS = {"state": "EXERCISED-PASS", "accept_floor_unmoved": True}


def _drive_new_gates(root):
    """`G-CONV` (per-field, p split) and `G-SCHEME`, driven in BOTH directions
    on a synthetic container log.  Returns (rc, n_direction1, n_direction2).

    G-SCHEME replaces D6RF4's G-SOLN.  Its VERDICT rests on scheme md5 / corrector
    count / coefficient equality / accept-floor state, none of them a run float
    vs a threshold; but it READS L1's CD/CL through `_ff` (for the shift report),
    so a non-finite CD/CL still folds to NOT A RESULT -- and that fold is what
    this drives.  The clean fixture makes gate_scheme PASS (LIMITED installed,
    4 p-solves => 3 correctors, coefficients equal at 0.333, floor unmoved) so
    the mutated CD/CL reaches the fold rather than tripping an earlier clause."""
    rc, n1, n2 = 0, 0, 0
    tmpdir = os.path.join(root, "_leglogs")
    os.makedirs(tmpdir, exist_ok=True)
    print("  --- section 3.4 on the TWO NEW GATES: G-CONV (p split) and G-SCHEME")
    cases = (
        ("G-CONV  p_first_unc  ", "conv", {"p0": "nan"},
         "L1.p_first_uncorrected.initRes"),
        ("G-CONV  p_corrected  ", "conv", {"p3": "-inf"},
         "L1.p_corrected.initRes"),
        ("G-CONV  nuTilda      ", "conv", {"nut": "-inf"}, "L1.nuTilda.initRes"),
        ("G-SCHEME CD          ", "scheme", {"cd": "nan"}, "L1.CD"),
        ("G-SCHEME CL          ", "scheme", {"cl": "inf"}, "L1.CL"),
    )
    # ---- DIRECTION 2 FIRST: the UNMUTATED control ------------------------
    clean = _leg_log(os.path.join(tmpdir, "clean.log"))
    legs = G.read_legs(clean)
    for name in ("G-CONV", "G-SCHEME"):
        res = (G.gate_conv(root, CENSUS, legs) if name == "G-CONV"
               else G.gate_scheme(root, CENSUS, legs, FLOOR_PASS))
        ok = res.get("verdict") != "NOT A RESULT"
        n2 += 1 if ok else 0
        rc = rc if ok else 1
        print("  %-4s %-21s direction 2  unmutated -> %s"
              % ("OK" if ok else "FAIL", name, res.get("verdict")))
    # ---- DIRECTION 1: a non-finite value MUST fold to NOT A RESULT --------
    for label, which, kw, expect_key in cases:
        lp = _leg_log(os.path.join(tmpdir, "mut_%s_%s.log"
                                   % (which, "_".join(sorted(kw)))), **kw)
        lg = G.read_legs(lp)
        res = (G.gate_conv(root, CENSUS, lg) if which == "conv"
               else G.gate_scheme(root, CENSUS, lg, FLOOR_PASS))
        nar = res.get("verdict") == "NOT A RESULT"
        okr, why = _reason_ok(res, os.path.basename(lp), expect_key)
        good = nar and okr
        n1 += 1 if good else 0
        rc = rc if good else 1
        print("      %-4s %s %-8s -> %-13s %s"
              % ("OK" if good else "FAIL", label, list(kw.values())[0],
                 res.get("verdict"), why))
    return rc, n1, n2


def _drive_ledger(root, d4):
    """The 2026-09-05 WIDENING of section 3f to `G-CAPS` and `G1`, driven in
    both directions.

    The mutation goes in AS A TEXT TOKEN in the ledger row, exactly as a
    malformed launcher would have written it -- `core_min=nan`, not a Python
    float handed to the gate. A harness that injected a float would be testing
    the gate's arithmetic and not the ledger reader that actually failed.

    THE MEASURED SHAPE THIS CLOSES: `nan <= cap` is False, so `within_cap` was
    False and `G-CAPS` returned **GATE FAIL** -- an accusation that an arm
    BREACHED ITS BUDGET, manufactured from a non-number. That is `D6RF3-DEF-5`
    one gate over and it is the most damaging form of it, because a cap breach
    is a finding about discipline rather than about physics."""
    rc, n1, n2 = 0, 0, 0
    for label, which, arm, field in LEDGER_CASES:
        def run(ov=None):
            build(root, ov)
            rows, _ = G.parse_ledger(os.path.join(root, "ledger.txt"))
            cen = G.arm_census(root, rows, None)
            if which == "caps":
                return G.gate_caps(rows, cen)
            return G.gate_g1(root, rows, cen)

        # ---- direction 2: unmutated -------------------------------------
        try:
            clean = run()
        except Exception as e:                                  # noqa: BLE001
            print("  FAIL %s  direction 2 (unmutated) RAISED %s: %s"
                  % (label, type(e).__name__, str(e)[:200]))
            rc = 1
            continue
        clean_nar = (clean.get("verdict") == "NOT A RESULT"
                     or clean.get("reason") == G.NON_FINITE_REASON)
        if not clean_nar:
            n2 += 1
        else:
            rc = 1
        print("  %-4s %s direction 2  unmutated -> %s"
              % ("OK" if not clean_nar else "FAIL", label,
                 clean.get("verdict", "ran_clean=%s" % clean.get("ran_clean"))))

        # ---- direction 1: the token replaced, one at a time --------------
        for name, _v in NONFINITE:
            token = {"NaN": "nan", "+Inf": "inf", "-Inf": "-inf"}[name]
            try:
                res = run({arm: {field: token}})
            except Exception as e:                              # noqa: BLE001
                print("      FAIL %s %-5s RAISED %s -- a refusal is not the "
                      "registered behaviour" % (label, name, type(e).__name__))
                rc = 1
                continue
            d = res.get("non_finite") or {}
            if not d:
                for row in (res.get("arms") or {}).values():
                    if isinstance(row, dict) and row.get("non_finite"):
                        d = row["non_finite"]
                        break
            good = (d.get("reason") == G.NON_FINITE_REASON
                    and field in str(d.get("key"))
                    and "ledger.txt" in str(d.get("artefact")))
            # AND the composed verdict must be NOT A RESULT for THIS reason,
            # at rung 0 -- not swallowed as a completion-clause failure.
            if good and which == "g1":
                rows, _ = G.parse_ledger(os.path.join(root, "ledger.txt"))
                cen = G.arm_census(root, rows, None)
                v, why = G.compose(res, {"verdict": "PASS", "gate": "d"},
                                   {"verdict": "PASS", "gate": "f"},
                                   {"verdict": "PASS", "gate": "o"},
                                   {"verdict": "PASS", "gate": "p"},
                                   G.gate_caps(rows, cen),
                                   {"verdict": "PASS", "gate": "t"},
                                   {"verdict": "PASS", "gate": "z"}, cen)
                good = (v == "NOT A RESULT"
                        and any("rung 0" in r for r in why))
            if good:
                n1 += 1
            else:
                rc = 1
            print("      %-4s %s %-5s -> %-13s reason=%s key=%s"
                  % ("OK" if good else "FAIL", label, name,
                     res.get("verdict", "G1"), d.get("reason"), d.get("key")))
    return rc, n1, n2


def drive():
    tmp = tempfile.mkdtemp(prefix="d6rf6_finmut_")
    root = os.path.join(tmp, "run")
    d4 = build(root)
    G.D4_OPT_IPOPT = d4
    print("D6RF6 SECTION 3f FINITENESS MUTATION HARNESS -- BOTH DIRECTIONS")
    print("  the fixture census gives REF_off a RAN state so the G-OFF fold is "
          "reachable; on a REAL grading run REF_off is "
          "NOT_REGISTERED_AT_THIS_FREEZE and G-OFF reads NOT A RESULT")
    print("  fixture root %s" % root)
    print("  binding list (section 3f, VERBATIM, not widened): %s"
          % ", ".join(G.FINITENESS_BINDS))
    rc = 0
    n_dir2, n_dir1, n_not_exercised = 0, 0, 0

    for label, fn, art, keypath, expect_key in _cases(root, d4):
        # ---- DIRECTION 2 FIRST: the UNMUTATED control ----------------------
        # Driven before any mutation, because a guard that returns NOT A
        # RESULT for everything passes direction 1 perfectly and is worthless.
        build(root)
        G.D4_OPT_IPOPT = d4
        try:
            clean = fn()
        except Exception as e:                                  # noqa: BLE001
            print("  FAIL %s  direction 2 (unmutated) RAISED %s: %s"
                  % (label, type(e).__name__, str(e)[:200]))
            rc = 1
            continue
        clean_ok = not _is_nar(clean)
        clean_v = clean.get("verdict", "REPORTED value_pct=%s"
                            % clean.get("value_pct"))
        if clean_ok:
            n_dir2 += 1
        else:
            rc = 1
        print("  %-4s %s direction 2  unmutated -> %s"
              % ("OK" if clean_ok else "FAIL", label, clean_v))

        # ---- DIRECTION 1: NaN, +Inf, -Inf, one at a time -------------------
        for name, val in NONFINITE:
            build(root)
            G.D4_OPT_IPOPT = d4
            _mutate(art, keypath, val)
            try:
                res = fn()
            except Exception as e:                              # noqa: BLE001
                print("      FAIL %s %-5s RAISED %s -- a refusal is not the "
                      "registered behaviour; section 3f requires NOT A RESULT"
                      % (label, name, type(e).__name__))
                rc = 1
                continue
            nar = _is_nar(res)
            ok_reason, why = _reason_ok(res, art, expect_key)
            good = nar and ok_reason
            if good:
                n_dir1 += 1
            else:
                rc = 1
            print("      %-4s %s %-5s -> %-13s %s"
                  % ("OK" if good else "FAIL", label, name,
                     res.get("verdict", "REPORTED"),
                     why if ok_reason else "REASON NOT ESTABLISHED: " + why))

    print("  --- the 2026-09-05 WIDENING to G-CAPS and G1, driven the same way")
    lrc, ln1, ln2 = _drive_ledger(root, d4)
    if lrc:
        rc = 1
    grc, gn1, gn2 = _drive_new_gates(root)
    if grc:
        rc = 1
    print("  ----------------------------------------------------------------")
    print("  section 3f AS DRAFTED : %s" % ", ".join(G.FINITENESS_BINDS_AS_DRAFTED))
    print("  section 3f WIDENED TO : %s   (pre-compute; run root asserted "
          "ABSENT; only ever ADDS refusals)" % ", ".join(G.FINITENESS_WIDENED_TO))
    print("  direction 1 (mutated -> NOT A RESULT, reason asserted) : %d of %d"
          % (n_dir1 + ln1 + gn1,
             (10 + len(LEDGER_CASES)) * len(NONFINITE) + 5))
    print("  direction 2 (unmutated -> NOT `NOT A RESULT`)          : %d of %d"
          % (n_dir2 + ln2 + gn2, 10 + len(LEDGER_CASES) + 2))
    print("  NOT EXERCISED                                          : %d"
          % n_not_exercised)
    print("  F2: %s"
          % ("the section 3f clause IS ESTABLISHED in both directions"
             if rc == 0 else
             "THE CLAUSE IS NOT ESTABLISHED -- D6RF3-DEF-5 is NOT repaired "
             "and the item must report NOT A RESULT for want of a working "
             "guard rather than ship gates it cannot trust"))
    return rc


if __name__ == "__main__":
    sys.exit(drive())
