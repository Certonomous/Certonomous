#!/usr/bin/env python3
"""Curriculum D6RF5 -- `ACCEPT_FLOOR_UNMOVED`, this item's own non-regression
instrument (`PREREGISTRATION.md` section 7 instrument 4).

WHAT IT IS FOR, AND IT IS THE ONLY REASON IT EXISTS.  `D6RF5` is lawful as a
successor to `D6RF3` on ONE ground: it tightens the linear-solver stopping rule,
which makes the solve HARDER at an UNCHANGED acceptance bar.  Loosening the
acceptance bar instead -- raising `primalMinResTol` or `primalMinResTolDiff` so
that `D6RF3`'s own measured `primalMaxRes 1.316217833e-05` would be accepted --
would be widening a gate to fit an answer, and whether a successor may EVER
register a different acceptance rule is ESCALATED TO SANAA AND UNRULED
(`N-D43`; `PREREGISTRATION.md` sections 0 and 9.3).

The registration STATES that boundary.  This file MAKES IT EXECUTABLE.  It
reads `primalMinResTol` and `primalMinResTolDiff` back out of the arm's OWN
container log -- the bytes DAFoam actually ran with, not the bytes anybody
intended -- and REFUSES the grading (exit 2) if either has moved in EITHER
direction, or if their product is not the registered accept floor `1.0e-05`.

WHY "IN EITHER DIRECTION" AND NOT "NOT LOOSENED".  A rule that only refuses
loosening is a rule about intent.  `UNMOVED` is a rule about bytes: a
TIGHTENED floor refuses too, because a successor that silently tightened the
bar would be reporting a `G-CONV PASS` earned against a different bar from the
one `D6RF3` failed, and the two items would no longer be comparable.  The
registered value is a value, not an inequality.

THE PARSING TRAP THIS INSTRUMENT IS BUILT AROUND, AND IT IS `N-D43`'s OWN.
`primalMinResTol` is a PREFIX of `primalMinResTolDiff`, both are printed in the
same `DAOption` dump, and the miss was reported twice with the wrong
denominator before a lane caught it.  A reader that matches the shorter key
loosely reads the longer key's value and reports a floor that was never set.
So the two patterns below are ANCHORED on the terminating whitespace, the
control drives a deliberately loose reader as a named blind case, and the
accept floor is always the PRODUCT and never the tolerance alone.

RULE 3, AND IT IS NOT DECORATION.  `run_floor_control` plants a KNOWN DRIFT
into a COPY of the log, reads it back FROM DISK through THE SAME reader the
gate calls, and REFUSES if that reader cannot see it.  A log that reads
"unmoved" from a reader never shown able to see a moved one is not evidence
that nothing moved.  The original's md5 is asserted before and after: a control
that modifies what it grades is not a control.

THREE STATES, ALWAYS PRINTED.  `EXERCISED-PASS` / `EXERCISED-FAIL` /
`NOT EXERCISED`.  `NOT EXERCISED` is printed beside the verdict, is NEVER
counted as a pass, and is NEVER inferred from the absence of a failure
(`DAFOAM_CHARTER.md` section 18.5's proposal, taken here inside this item's own
comparator where this item may take it).

NO `assert` STATEMENT APPEARS IN THIS FILE.  `python -O` deletes them.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

# ======================= REGISTERED CONSTANTS, FROZEN ========================
# Carried forward from `D6RF3` BYTE-IDENTICALLY.  These do not move in this
# item and this file is what makes that statement checkable.
PRIMAL_MIN_RES_TOL = 1.0e-08
PRIMAL_MIN_RES_TOL_DIFF = 1000.0
# `N-D43`: the accept floor is the PRODUCT.  Dividing by the tolerance alone
# overstates the miss by the value of `primalMinResTolDiff` -- measured, 1000x.
ACCEPT_FLOOR = PRIMAL_MIN_RES_TOL * PRIMAL_MIN_RES_TOL_DIFF        # 1.0e-05

# The known drift the control plants.  Registered as a LITERAL so a reader that
# reports it is reporting the plant and not a coincidence.
DRIFT_TOKEN = "1e12"
DRIFT_VALUE = 1.0e12

EXERCISED_PASS = "EXERCISED-PASS"
EXERCISED_FAIL = "EXERCISED-FAIL"
NOT_EXERCISED = "NOT EXERCISED"

# ANCHORED ON THE TERMINATING WHITESPACE.  `primalMinResTol\s` cannot match
# inside `primalMinResTolDiff`, which is the whole point.
RE_TOL = re.compile(r'^[ \t]*primalMinResTol[ \t]+([^;\s]+)[ \t]*;', re.M)
RE_DIFF = re.compile(r'^[ \t]*primalMinResTolDiff[ \t]+([^;\s]+)[ \t]*;', re.M)


class AcceptFloorRefusal(Exception):
    pass


def refuse(where, detail):
    raise AcceptFloorRefusal(json.dumps({"REFUSE": where, "detail": detail},
                                        sort_keys=True, default=str)[:4000])


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


# ============================== THE READER ===================================
def read_accept_floor(path):
    """THE ONE READER OF THIS ITEM'S ACCEPT FLOOR.

    Returns EVERY occurrence, not the first.  `D6RF3`'s own log carries THREE
    byte-identical `DAOption` dumps (`:333-600`, `:941-1208`, `:1547-1814`) --
    one per registered point -- so a reader that took `[0]` would report the
    floor the FIRST point ran under and say nothing about the others.  A
    multipoint arm can in principle be handed three different option blocks;
    this reader is built so that it would SEE that rather than average it away.
    """
    if not os.path.isfile(path):
        refuse("ACCEPT_FLOOR_READ", {"log_absent": path})
    with open(path, errors="replace") as fh:
        txt = fh.read()
    tol_tok = RE_TOL.findall(txt)
    diff_tok = RE_DIFF.findall(txt)
    out = {"log": path,
           "primalMinResTol_tokens": tol_tok,
           "primalMinResTolDiff_tokens": diff_tok,
           "n_tol_occurrences": len(tol_tok),
           "n_diff_occurrences": len(diff_tok)}
    # A READER THAT FOUND NOTHING HAS NOT FOUND AGREEMENT.  CLAUDE.md rule 3:
    # a zero from a reader not shown able to see a non-zero is not evidence,
    # and "no occurrence of a drifted value" is exactly such a zero.
    if not tol_tok or not diff_tok:
        refuse("ACCEPT_FLOOR_READ",
               {"log": path, "n_tol_occurrences": len(tol_tok),
                "n_diff_occurrences": len(diff_tok),
                "note": "the accept floor is ABSENT from this log, so it was "
                        "not read as unmoved -- it was not read at all. An "
                        "absent floor is UNMEASURED, never UNMOVED."})
    def _num(toks, key):
        vals = []
        for tok in toks:
            try:
                vals.append(float(tok))
            except ValueError:
                refuse("ACCEPT_FLOOR_READ",
                       {"log": path, "key": key, "token_as_read": tok,
                        "note": "unparseable as a float; reported as read"})
        return vals
    out["primalMinResTol_values"] = _num(tol_tok, "primalMinResTol")
    out["primalMinResTolDiff_values"] = _num(diff_tok, "primalMinResTolDiff")
    out["distinct_tol"] = sorted(set(out["primalMinResTol_values"]))
    out["distinct_diff"] = sorted(set(out["primalMinResTolDiff_values"]))
    out["accept_floors"] = sorted({t * d
                                   for t in out["distinct_tol"]
                                   for d in out["distinct_diff"]})
    return out


# ============================ THE PLANT ======================================
def plant_drift(src, dst, key="primalMinResTolDiff", token=DRIFT_TOKEN,
                where="all"):
    """Write a COPY of the log with ONE registered key drifted to `token`.

    `where="all"`  drifts every occurrence.
    `where="last"` drifts ONLY THE LAST occurrence, and it is not a decorative
    second mode.  This case is multipoint: `D6RF3`'s log carries THREE
    `DAOption` dumps, one per registered point, and a reader that takes the
    FIRST is blind to a floor that moved at the third point only.  A plant that
    only ever drifts every site cannot catch that reader -- MEASURED here, on
    this control's own drive, where `first_DAOption_dump_only` sailed through a
    whole-log plant because the first dump carried the drift too.  The plant
    was strengthened rather than the case dropped.

    Returns the number of sites rewritten.  ZERO SITES IS A REFUSAL: a plant
    that planted nothing produces a copy the reader cannot distinguish from the
    original, and the control would then pass for the wrong reason."""
    with open(src, errors="replace") as fh:
        txt = fh.read()
    rx = RE_DIFF if key == "primalMinResTolDiff" else RE_TOL
    hits = list(rx.finditer(txt))
    if not hits:
        refuse("PLANT_ACCEPT_FLOOR",
               {"key": key, "src": src, "sites": 0, "where": where,
                "note": "nothing to plant into; a control with nothing to "
                        "plant into is not a control (L-302)"})
    targets = hits if where == "all" else hits[-1:]
    out, cut = [], 0
    for m in targets:
        out.append(txt[cut:m.start()])
        out.append(m.group(0).replace(m.group(1), token, 1))
        cut = m.end()
    out.append(txt[cut:])
    with open(dst, "w") as fh:
        fh.write("".join(out))
        fh.flush()
        os.fsync(fh.fileno())
    return len(targets)


# ======================= THE GATE'S OWN CHECK ================================
def check_accept_floor_unmoved(values):
    """The registered comparison, on values ALREADY READ.  Separated from the
    reader so the control can hand it a planted read and require a refusal
    without touching the disk a second time."""
    bad = {}
    if values["distinct_tol"] != [PRIMAL_MIN_RES_TOL]:
        bad["primalMinResTol"] = {"registered": PRIMAL_MIN_RES_TOL,
                                  "read": values["distinct_tol"],
                                  "tokens": values["primalMinResTol_tokens"]}
    if values["distinct_diff"] != [PRIMAL_MIN_RES_TOL_DIFF]:
        bad["primalMinResTolDiff"] = {"registered": PRIMAL_MIN_RES_TOL_DIFF,
                                      "read": values["distinct_diff"],
                                      "tokens": values["primalMinResTolDiff_tokens"]}
    if values["accept_floors"] != [ACCEPT_FLOOR]:
        bad["accept_floor_product"] = {"registered": ACCEPT_FLOOR,
                                       "read": values["accept_floors"]}
    return bad


def run_floor_control(ctrl_dir, log_path, reader=read_accept_floor):
    """`ACCEPT_FLOOR_UNMOVED`, both directions, in one call.

    1  log absent                     -> `NOT EXERCISED`, reported, never a pass
    2  plant a known drift into a COPY and read it back through THE SAME
       reader -- if the reader cannot see it, REFUSE (it is blind)
    3  the original must be byte-unchanged by the control
    4  the REAL log's values must equal the registered ones EXACTLY, in both
       directions, or REFUSE `ACCEPT_FLOOR_MOVED`
    """
    if log_path is None or not os.path.isfile(log_path):
        return {"state": NOT_EXERCISED, "reader_saw_the_plant": None,
                "accept_floor_unmoved": None, "log": log_path,
                "why": "the arm's container log is not on disk, so the accept "
                       "floor was not read. UNMEASURED, never UNMOVED, and "
                       "never counted as a pass."}
    os.makedirs(ctrl_dir, exist_ok=True)
    m_before = md5_of(log_path)
    values = reader(log_path)

    # ---- direction A: THE PLANT.  Rule 3, on the reader the gate calls. -----
    # TWO PLANTS, NOT ONE.  `all` catches a reader that never opens the file;
    # `last` catches a reader that opens it and stops at the first `DAOption`
    # dump -- and on a THREE-dump multipoint log those are different blindnesses.
    # The reader must see BOTH or it is refused.
    plants, sites_by_plant, saw_by_plant = {}, {}, {}
    for where in ("all", "last"):
        p = os.path.join(ctrl_dir,
                         "container_log.PLANTED_ACCEPT_FLOOR.%s.txt" % where)
        sites_by_plant[where] = plant_drift(log_path, p, where=where)
        saw_by_plant[where] = (DRIFT_VALUE
                               in reader(p)["distinct_diff"])
        plants[where] = p
    planted = plants["all"]
    sites = sites_by_plant["all"]
    saw = all(saw_by_plant.values())
    res = {"log": log_path, "planted_copies": plants,
           "planted_sites_by_plant": sites_by_plant,
           "reader_saw_the_plant_by_plant": saw_by_plant,
           "planted_copy": planted, "planted_sites": sites,
           "planted_token": DRIFT_TOKEN,
           "reader_saw_the_plant": saw,
           "registered": {"primalMinResTol": PRIMAL_MIN_RES_TOL,
                          "primalMinResTolDiff": PRIMAL_MIN_RES_TOL_DIFF,
                          "accept_floor": ACCEPT_FLOOR},
           "read": {"primalMinResTol": values["distinct_tol"],
                    "primalMinResTolDiff": values["distinct_diff"],
                    "accept_floor": values["accept_floors"],
                    "n_tol_occurrences": values["n_tol_occurrences"],
                    "n_diff_occurrences": values["n_diff_occurrences"]},
           "original_md5_before": m_before}
    m_after = md5_of(log_path)
    res["original_md5_after"] = m_after
    res["original_unchanged"] = (m_before == m_after)
    if not saw:
        res["state"] = EXERCISED_FAIL
        refuse("PLANT_ACCEPT_FLOOR",
               dict(res, note="the reader the gate calls could not see a "
                              "planted drift of %s: sites %r, seen %r. A log "
                              "that reads UNMOVED from a blind reader is not "
                              "evidence that nothing moved."
                              % (DRIFT_TOKEN, sites_by_plant, saw_by_plant)))
    if not res["original_unchanged"]:
        refuse("PLANT_ACCEPT_FLOOR",
               dict(res, the_control_modified_the_artefact_it_grades=True))

    # ---- direction B: THE GATE ITSELF --------------------------------------
    bad = check_accept_floor_unmoved(values)
    res["accept_floor_unmoved"] = (not bad)
    res["state"] = EXERCISED_PASS if not bad else EXERCISED_FAIL
    if bad:
        refuse("ACCEPT_FLOOR_MOVED",
               dict(res, moved=bad,
                    clause="PREREGISTRATION.md section 7 instrument 4 and "
                           "section 9.3: primalMinResTol and "
                           "primalMinResTolDiff DO NOT MOVE IN THIS ITEM, in "
                           "EITHER direction. Whether a successor may ever "
                           "register a different acceptance rule is ESCALATED "
                           "TO SANAA AND UNRULED. This grading stops rather "
                           "than reporting a number earned against a bar "
                           "nobody registered."))
    return res


# ========================= THE DRIVE, BOTH DIRECTIONS ========================
D6RF3_REAL_LOG = ("/home/ubuntu/certonomous-runs/"
                  "CURRICULUM-D6RF3-a2-wing-multipoint-fd/"
                  "F_mp_20260905T222250Z_43793.log")


def _synthetic_log(path, tol="1e-08", diff="1000", dumps=3):
    """A minimal log of the shape the arm's container actually writes, built
    here rather than taken from a run.

    THE REASON IS TENSELESS AND STAYS TRUE AFTER THE ITEM RUNS: a control that
    can only be driven ONCE the compute it guards has happened is not a
    pre-compute control, and this one has to be drivable at the freeze, when
    no arm log exists.  Direction 6 of the drive exercises the SAME reader on
    the real D6RF3 container log, so the fixture is not the only thing this
    reader has ever been shown.  `dumps` reproduces D6RF3's THREE `DAOption`
    blocks."""
    block = ("    solverName      DARhoSimpleFoam;\n"
             "    primalMinResTol %s;\n"
             "    printIntervalUnsteady 1;\n"
             "    primalMinResTolDiff %s;\n"
             "    adjUseColoring  1;\n" % (tol, diff))
    body = ["D6RF5_LEG_BEGIN baseline mode=P_conv"]
    for i in range(dumps):
        body.append("Setting UMag = 100 AoA = 0.8829754496 degs   # point %d" % i)
        body.append(block)
    body += ["", "Time = 1000", "",
             "p initRes: 1.316217833e-05 finalRes: 1.098439549e-06 nIters: 1",
             "nuTilda initRes: 1.050443706e-05 finalRes: 4.697819428e-07 nIters: 1",
             "ExecutionTime = 19.71 s  ClockTime = 20 s", "", "End",
             "D6RF5_LEG_END baseline mode=P_conv", "Finalising parallel run"]
    with open(path, "w") as fh:
        fh.write("\n".join(body) + "\n")
    return path


# ---- deliberately blind readers, each blind in a NAMED way ------------------
def _blind_prefix_confusion(path):
    """`N-D43`'s OWN TRAP, as a reader.  Matches `primalMinResTol` LOOSELY, so
    `primalMinResTolDiff 1000;` satisfies it too and the tolerance is reported
    as 1000.  This is the reader that produced the `1316x` figure twice."""
    with open(path, errors="replace") as fh:
        txt = fh.read()
    tol = re.findall(r'primalMinResTol\s*(\S+?);', txt)
    return {"log": path, "primalMinResTol_tokens": tol,
            "primalMinResTolDiff_tokens": ["1000"],
            "n_tol_occurrences": len(tol), "n_diff_occurrences": 1,
            "primalMinResTol_values": [1.0e-08], "primalMinResTolDiff_values": [1000.0],
            "distinct_tol": [PRIMAL_MIN_RES_TOL],
            "distinct_diff": [PRIMAL_MIN_RES_TOL_DIFF],
            "accept_floors": [ACCEPT_FLOOR]}


def _blind_first_occurrence_only(path):
    """Reads only the FIRST `DAOption` dump.  On a multipoint arm whose later
    points carried a different floor this reports the first point's bar and is
    silent about the rest."""
    v = read_accept_floor(path)
    return dict(v, distinct_tol=[v["primalMinResTol_values"][0]],
                distinct_diff=[v["primalMinResTolDiff_values"][0]],
                accept_floors=[v["primalMinResTol_values"][0]
                               * v["primalMinResTolDiff_values"][0]])


def _blind_constant(path):                                    # noqa: ARG001
    """Never opens the file it is handed and returns the registered values.
    The limiting case: a reader that cannot see ANY plant."""
    return {"log": path, "primalMinResTol_tokens": ["1e-08"],
            "primalMinResTolDiff_tokens": ["1000"],
            "n_tol_occurrences": 1, "n_diff_occurrences": 1,
            "primalMinResTol_values": [PRIMAL_MIN_RES_TOL],
            "primalMinResTolDiff_values": [PRIMAL_MIN_RES_TOL_DIFF],
            "distinct_tol": [PRIMAL_MIN_RES_TOL],
            "distinct_diff": [PRIMAL_MIN_RES_TOL_DIFF],
            "accept_floors": [ACCEPT_FLOOR]}


BLIND = (("prefix_confusion__N_D43s_own_trap", _blind_prefix_confusion),
         ("first_DAOption_dump_only", _blind_first_occurrence_only),
         ("ignores_its_argument__returns_the_registered_values", _blind_constant))

# ---- the drifts the control MUST refuse, in BOTH senses ---------------------
# The registered rule is UNMOVED, not `not loosened`, so a TIGHTENING refuses
# too.  A rule that only catches the direction its author feared is a rule
# about intent; this one is about bytes.
DRIFTS = (
    ("LOOSENED  diff 1000 -> 1e12   (accept floor 1.0e-05 -> 1.0e+04; this is "
     "the drift that would let D6RF3's own 1.316e-05 through)",
     {"diff": "1e12"}),
    ("LOOSENED  tol 1e-08 -> 1e-04  (accept floor 1.0e-05 -> 1.0e-01)",
     {"tol": "1e-04"}),
    ("TIGHTENED diff 1000 -> 10     (accept floor 1.0e-05 -> 1.0e-07)",
     {"diff": "10"}),
    ("TIGHTENED tol 1e-08 -> 1e-10  (accept floor 1.0e-05 -> 1.0e-07)",
     {"tol": "1e-10"}),
    ("PRODUCT PRESERVED, BOTH TERMS MOVED  tol 1e-05 x diff 1 = 1.0e-05 -- the "
     "case a product-only check would WAVE THROUGH",
     {"tol": "1e-05", "diff": "1"}),
)


def drive():
    """Runs `ACCEPT_FLOOR_UNMOVED` in BOTH directions and prints an auditable
    record.  Returns 0 only if every direction behaved as registered."""
    tmp = tempfile.mkdtemp(prefix="d6rf5_floor_ctrl_")
    rc = 0
    print("D6RF5 ACCEPT_FLOOR_UNMOVED -- DRIVEN IN BOTH DIRECTIONS")
    print("  no `assert` statement appears in this file")
    print("  registered  primalMinResTol=%g  primalMinResTolDiff=%g  "
          "accept_floor=%g" % (PRIMAL_MIN_RES_TOL, PRIMAL_MIN_RES_TOL_DIFF,
                               ACCEPT_FLOOR))

    # ---- direction 1: THE UNMUTATED LOG MUST PASS --------------------------
    good = _synthetic_log(os.path.join(tmp, "unmutated.log"))
    m0 = md5_of(good)
    try:
        r = run_floor_control(os.path.join(tmp, "ctrl_ok"), good)
        ok1 = (r["state"] == EXERCISED_PASS
               and r["accept_floor_unmoved"] is True
               and r["reader_saw_the_plant"] is True
               and r["reader_saw_the_plant_by_plant"] == {"all": True,
                                                          "last": True}
               and r["original_unchanged"] is True
               and md5_of(good) == m0)
        print("  %-5s direction 1  UNMUTATED     state=%-14s "
              "accept_floor_unmoved=%s  reader_saw_the_plant=%s  "
              "occurrences=%d/%d  original_unchanged=%s"
              % ("OK" if ok1 else "FAIL", r["state"], r["accept_floor_unmoved"],
                 r["reader_saw_the_plant"], r["read"]["n_tol_occurrences"],
                 r["read"]["n_diff_occurrences"], r["original_unchanged"]))
    except AcceptFloorRefusal as e:
        ok1 = False
        print("  FAIL  direction 1  UNMUTATED     the control REFUSED a clean "
              "log -- %s" % str(e)[:300])
    if not ok1:
        rc = 1

    # ---- direction 2: EVERY PLANTED DRIFT MUST REFUSE ----------------------
    for label, kw in DRIFTS:
        slug = re.sub(r"[^A-Za-z0-9]+", "_", label)[:40]
        p = os.path.join(tmp, "drift_%s.log" % slug)
        _synthetic_log(p, tol=kw.get("tol", "1e-08"),
                       diff=kw.get("diff", "1000"))
        m_pre = md5_of(p)
        got, why = None, None
        try:
            run_floor_control(os.path.join(tmp, "ctrl_" + slug), p)
            got = "NO REFUSAL"
        except AcceptFloorRefusal as e:
            got = "REFUSED"
            try:
                why = json.loads(str(e))
            except ValueError:
                why = {}
        except Exception as e:                                # noqa: BLE001
            got = "RAISED %s" % type(e).__name__
        d = (why or {}).get("detail", {})
        reason_ok = ((why or {}).get("REFUSE") == "ACCEPT_FLOOR_MOVED"
                     and d.get("state") == EXERCISED_FAIL
                     and d.get("accept_floor_unmoved") is False
                     and bool(d.get("moved")))
        okd = (got == "REFUSED" and reason_ok and md5_of(p) == m_pre)
        print("  %-5s direction 2  %-98s outcome=%-9s "
              "reason_is_ACCEPT_FLOOR_MOVED=%s  moved=%s"
              % ("OK" if okd else "FAIL", label, got, reason_ok,
                 ",".join(sorted((d.get("moved") or {}).keys())) or "-"))
        if not okd:
            rc = 1

    # ---- direction 3: A BLIND READER MUST BE REFUSED, NOT TRUSTED ----------
    for name, fn in BLIND:
        p = _synthetic_log(os.path.join(tmp, "blind_%s.log" % name))
        m_pre = md5_of(p)
        got, why = None, None
        try:
            run_floor_control(os.path.join(tmp, "blind_ctrl_" + name), p,
                              reader=fn)
            got = "NO REFUSAL"
        except AcceptFloorRefusal as e:
            got = "REFUSED"
            try:
                why = json.loads(str(e))
            except ValueError:
                why = {}
        except Exception as e:                                # noqa: BLE001
            # A blind reader that dies of a KeyError has NOT demonstrated that
            # the control detects blindness.  Recorded as a FAIL of the DRIVE,
            # never counted as the control working.
            got = "RAISED %s" % type(e).__name__
        d = (why or {}).get("detail", {})
        reason_ok = ((why or {}).get("REFUSE") == "PLANT_ACCEPT_FLOOR"
                     and d.get("reader_saw_the_plant") is False
                     and d.get("state") == EXERCISED_FAIL)
        okb = (got == "REFUSED" and reason_ok and md5_of(p) == m_pre)
        print("  %-5s direction 3  BLIND READER  %-52s outcome=%-9s "
              "reason_is_PLANT_ACCEPT_FLOOR_with_reader_saw_the_plant_false=%s"
              % ("OK" if okb else "FAIL", name, got, reason_ok))
        if not okb:
            rc = 1

    # ---- direction 4: THE `NOT EXERCISED` TOKEN IS ITSELF EXERCISED --------
    ne = run_floor_control(os.path.join(tmp, "ctrl_absent"),
                           os.path.join(tmp, "does_not_exist.log"))
    ok4 = (ne["state"] == NOT_EXERCISED and ne["reader_saw_the_plant"] is None
           and ne["accept_floor_unmoved"] is None)
    print("  %-5s direction 4  ABSENT LOG    state=%-14s accept_floor_unmoved="
          "%s  (reported, NEVER counted as a pass, NEVER inferred from the "
          "absence of a failure)"
          % ("OK" if ok4 else "FAIL", ne["state"], ne["accept_floor_unmoved"]))
    if not ok4:
        rc = 1

    # ---- direction 5: A LOG WITH NO FLOOR AT ALL IS UNMEASURED, NOT UNMOVED -
    empty = os.path.join(tmp, "no_floor.log")
    with open(empty, "w") as fh:
        fh.write("Time = 1000\np initRes: 1.3e-05 finalRes: 1e-06 nIters: 1\n"
                 "End\nFinalising parallel run\n")
    got5, why5 = None, {}
    try:
        run_floor_control(os.path.join(tmp, "ctrl_nofloor"), empty)
        got5 = "NO REFUSAL"
    except AcceptFloorRefusal as e:
        got5 = "REFUSED"
        why5 = json.loads(str(e))
    ok5 = (got5 == "REFUSED" and why5.get("REFUSE") == "ACCEPT_FLOOR_READ"
           and why5["detail"].get("n_tol_occurrences") == 0)
    print("  %-5s direction 5  NO FLOOR IN THE LOG  outcome=%-9s "
          "reason_is_ACCEPT_FLOOR_READ_with_zero_occurrences=%s  "
          "(an absent floor is UNMEASURED, never UNMOVED)"
          % ("OK" if ok5 else "FAIL", got5, ok5))
    if not ok5:
        rc = 1

    # ---- direction 6: THE REAL D6RF3 LOG, SO THE READER IS SHOWN ON THE -----
    # ---- BYTES A CONTAINER ACTUALLY WROTE AND NOT ONLY ON A FIXTURE. -------
    if os.path.isfile(D6RF3_REAL_LOG):
        ro = os.path.join(tmp, "real_readonly_copy.log")
        shutil.copy2(D6RF3_REAL_LOG, ro)       # NEVER plant into the evidence
        try:
            rr = run_floor_control(os.path.join(tmp, "ctrl_real"), ro)
            ok6 = (rr["state"] == EXERCISED_PASS
                   and rr["accept_floor_unmoved"] is True
                   and rr["read"]["n_tol_occurrences"] == 3
                   and rr["read"]["n_diff_occurrences"] == 3)
            print("  %-5s direction 6  REAL D6RF3 CONTAINER LOG  state=%-14s "
                  "tol=%s diff=%s floor=%s occurrences=%d/%d"
                  % ("OK" if ok6 else "FAIL", rr["state"],
                     rr["read"]["primalMinResTol"], rr["read"]["primalMinResTolDiff"],
                     rr["read"]["accept_floor"], rr["read"]["n_tol_occurrences"],
                     rr["read"]["n_diff_occurrences"]))
        except AcceptFloorRefusal as e:
            ok6 = False
            print("  FAIL  direction 6  REAL D6RF3 CONTAINER LOG  REFUSED -- %s"
                  % str(e)[:300])
        if not ok6:
            rc = 1
        print("        source %s (copied read-only; the evidence log is never "
              "planted into)" % D6RF3_REAL_LOG)
    else:
        print("  %-5s direction 6  REAL D6RF3 CONTAINER LOG  %s -- the real-log "
              "exercise is NOT EXERCISED and is NOT counted as a pass"
              % (NOT_EXERCISED, D6RF3_REAL_LOG))

    print("  RESULT %s  (1 unmutated pass, %d planted drifts refused in BOTH "
          "senses, %d blind readers refused, 1 NOT EXERCISED token, 1 absent-"
          "floor refusal, 1 real-log exercise)"
          % ("ALL DIRECTIONS AS REGISTERED" if rc == 0 else "NOT AS REGISTERED",
             len(DRIFTS), len(BLIND)))
    return rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drive", action="store_true",
                    help="drive the control in both directions (no compute)")
    ap.add_argument("--log", help="run the control on a real container log")
    ap.add_argument("--ctrl-dir", default=None)
    a = ap.parse_args()
    if a.drive:
        return drive()
    if a.log:
        try:
            r = run_floor_control(a.ctrl_dir or tempfile.mkdtemp(
                prefix="d6rf5_floor_"), a.log)
        except AcceptFloorRefusal as e:
            sys.stderr.write("D6RF5_ACCEPT_FLOOR REFUSED %s\n" % e)
            return 2
        print(json.dumps(r, indent=1, sort_keys=True, default=str))
        return 0
    ap.print_help()
    return 64


if __name__ == "__main__":
    sys.exit(main())
