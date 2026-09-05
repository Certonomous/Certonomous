#!/usr/bin/env python3
"""Curriculum D6RF3 -- `PREREGISTRATION.md` section 3f's TWO-DIRECTION MUTATION
HARNESS.  It is the executable control on the finiteness clause, and it exists
because **a restrictive repair is not self-certifying**.

WHY IT IS A SEPARATE FILE AND NOT A BLOCK INSIDE THE GRADER, stated as a reason
rather than left as a preference: `d6rf3_grade.py` IS the grading path frozen by
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
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import d6rf3_grade as G                                          # noqa: E402

NONFINITE = (("NaN", float("nan")), ("+Inf", float("inf")),
             ("-Inf", float("-inf")))

# A clean, finite fixture set.  The CD values are section 2b's stdout-recovered
# numbers; the REF_off values are set ABOVE them so the unmutated G-OFF has a
# definite, non-`NOT A RESULT` verdict (PASS) rather than an accidental one.
CD_MP = {"cl04": 1.846929883e-02, "cl05": 2.176156349e-02,
         "cl06": 2.696277508e-02}
CD_REF = {p: v * 1.05 for p, v in CD_MP.items()}
CL_REF = {"cl04": 0.4, "cl05": 0.5, "cl06": 0.6}
CENSUS = {"F_mp": {"state": "RAN", "source": "fixture"},
          "REF_off": {"state": "RAN", "source": "fixture"}}


def _w(path, doc):
    with open(path, "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)


def _fd_doc():
    """The shape `d6rf3_fd_endpoint.py` writes, with `points` (section 2a's
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


def _d4_ipopt(path):
    with open(path, "w") as fh:
        fh.write("Number of Iterations....: 80\n\n"
                 "Objective...............:   %.16e    %.16e\n\n"
                 "EXIT: Optimal Solution Found.\n"
                 % (G.CD_F_D4_RECORDED, G.CD_F_D4_RECORDED))


def build(root):
    if os.path.isdir(root):
        shutil.rmtree(root)
    for a in ("F_mp", "REF_off"):
        os.makedirs(os.path.join(root, a))
    f = os.path.join(root, "F_mp")
    _w(os.path.join(f, "d6rf3_fd_endpoint.json"), _fd_doc())
    _w(os.path.join(f, "d6rf3_major_history.json"), _hist_doc())
    _w(os.path.join(f, "d6rf3_endpoint_dvs_PHYSICAL.json"), _dv_doc())
    r = os.path.join(root, "REF_off")
    _w(os.path.join(r, "d6rf3_ref_off.json"), _ref_doc())
    _w(os.path.join(r, "d4_endpoint_dvs_PHYSICAL.json"), _dv_doc())
    d4 = os.path.join(root, "d4_opt_IPOPT.txt")
    _d4_ipopt(d4)
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
    f = os.path.join(root, "F_mp")
    r = os.path.join(root, "REF_off")
    fd = os.path.join(f, "d6rf3_fd_endpoint.json")
    ref = os.path.join(r, "d6rf3_ref_off.json")
    hist = os.path.join(f, "d6rf3_major_history.json")
    dv = os.path.join(f, "d6rf3_endpoint_dvs_PHYSICAL.json")
    rs = os.path.join(HERE, "d6rf3_opt_runScript.py")

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


def drive():
    tmp = tempfile.mkdtemp(prefix="d6rf3_finmut_")
    root = os.path.join(tmp, "run")
    d4 = build(root)
    G.D4_OPT_IPOPT = d4
    print("D6RF3 SECTION 3f FINITENESS MUTATION HARNESS -- BOTH DIRECTIONS")
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

    print("  ----------------------------------------------------------------")
    print("  direction 1 (mutated -> NOT A RESULT, reason asserted) : %d of %d"
          % (n_dir1, 10 * len(NONFINITE)))
    print("  direction 2 (unmutated -> NOT `NOT A RESULT`)          : %d of %d"
          % (n_dir2, 10))
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
