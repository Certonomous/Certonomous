#!/usr/bin/env python3
"""APPARATUS DEMONSTRATION -- NOT AN RC4 RUN, AND IT ASSERTS NO RC4 GATE VERDICT.

THIS IS NOT COMPUTE AGAINST RC4's GATES.  It launches no solver, builds no RC4
case, writes nothing under RC4's registered run root, and never calls
`rc4_score.score_all`, `rc4_score.verdict`, `rc4_score.gate_arithmetic` or
`rc4_score.cut`.  Those four absences are checked by an `ast` parse of THIS FILE
by `--selftest`, so the claim is executable rather than a promise.

Registration: RC4_PREFLIGHT_apparatus/PREREGISTRATION.md.  It refuses until that
document is frozen.  It does not read, and cannot clear, RC4's own freeze token.

WHAT IT MEASURES -- TWO CHANNELS ON THE SAME PRESERVED ROW, NEITHER REPLACING
THE OTHER
--------------------------------------------------------------------------
  channel R  the RECONSTRUCTION reader RC4's continuity screen actually
             consults: `divU_rms_over_gradscale` as returned by
             `rc4_score.score_row`, called UNMODIFIED.  L-512: the committed
             tool's INPUT is scoped to a read-only scratch assembly of a
             preserved row's own bytes; its TRANSFORM is not reimplemented, and
             the number reported is the very dict key `rc4_score.py:430` reads.
  channel P  the PRODUCER's own continuity channel -- OpenFOAM's
             `time step continuity errors : sum local`, `fvc::div(phi)` from
             `continuityErrs.H` -- parsed from ONE NAMED log artifact per row.
             NEVER a glob (L-... `grep ... log.* | tail -1` is a coin flip).
             This is the INDEPENDENT WITNESS.

Channel P is the solver's own arithmetic on its own flux field.  Channel R is a
structured-gradient reconstruction from cell centres, documented in
`_common/sst_baseline_metrics.py:114-116` as validated to 0.5-1.0% interior
rel-L2.  Where the two disagree by orders of magnitude the question of WHICH is
measuring continuity is an instrument question, and this module exists to make it
measurable rather than arguable.

THE FLOOR READING.  On an UNCORRECTED baseline row the correction fields are
identically zero, so the physical continuity error is whatever the producer says
it is -- and whatever channel R returns there is channel R's NOISE FLOOR on that
mesh.  A registered bar below that floor is not strict; it is blind.  This module
reports the floor and compares it with RC4's registered bars.  IT MOVES NO BAR.

CONTROLS (standing rule 3), all refusals, every one demonstrated firing:
  * channel R plant: a known divergence is written into a scratch copy of `U`
    with `rc4_score.swap_internal_vector` UNMODIFIED, and the module REFUSES
    unless the reader's metric MOVES -- a value from a reader not shown able to
    return a different one is not evidence;
  * channel R determinism: the same row read twice must agree exactly;
  * channel P plant: the parser must return DIFFERENT values from two different
    named logs, and must find ZERO continuity lines in a log that has none;
  * channel P absence: a named log carrying no continuity line REFUSES; a
    missing log REFUSES.  A missing channel is not a zero.
  * RC4's run root must be ABSENT before and after, and the prober must be shown
    able to see a directory that DOES exist in the same invocation.

NO `ast.Assert` CARRIES ANY REFUSAL, GUARD OR CONTROL.  `--selftest` parses this
file and requires zero.
"""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CLOSURE = os.path.dirname(HERE)
COMMON = os.path.join(CLOSURE, "_common")
RC4 = os.path.join(CLOSURE, "RC4_kaandorp_propagation_repair")
R4 = os.path.join(CLOSURE, "R4_sparta_build")
for _p in (HERE, COMMON, RC4, R4):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from of_read import read_field                                     # noqa: E402
import r4_lib                                                      # noqa: E402
import sst_baseline_metrics as SB                                  # noqa: E402
import rc4_score as S                                              # noqa: E402
import build_rc4_cases as B                                        # noqa: E402

PREREG = os.path.join(HERE, "PREREGISTRATION.md")
UNFROZEN_TOKEN = "PREFLIGHT_FREEZE_PENDING"

# The pre-flight's OWN scratch root.  Deliberately shares NO prefix with RC4's
# registered run root, so no glob written against one can ever reach the other.
PREFLIGHT_ROOT = "/home/ubuntu/closure-data/preflight_cbfs_continuity"
RC4_RUN_ROOT = "/home/ubuntu/closure-data/rc4"          # = build_rc4_cases.ROOT's parent
RC4_ROOT_CONTROL = "/home/ubuntu/closure-data/r4"       # a directory that DOES exist

BENCH = "/home/ubuntu/closure-challenge-benchmark/data"
KAAN = "/home/ubuntu/closure-data/aposteriori/kaandorp"

# Every artifact NAMED.  No glob, no `log.*`, no discovery.  `time` is left None
# and resolved by `r4_lib.latest_time`, the same accessor `score_row` uses, so
# the reader and this table cannot disagree about which time directory is read.
ROWS = {
    "CBFS13700__NULL": {
        "case": os.path.join(KAAN, "CBFS13700__NULL"),
        "log": os.path.join(KAAN, "CBFS13700__NULL", "log.run"),
        "tag": "CBFS13700", "src": os.path.join(BENCH, "CBFS"), "fam": "cbfs",
        "role": "UNCORRECTED BASELINE -- the floor reading for the CBFS mesh",
    },
    "CBFS13700__TRUTHR": {
        "case": os.path.join(KAAN, "CBFS13700__TRUTHR"),
        "log": os.path.join(KAAN, "CBFS13700__TRUTHR", "log.run"),
        "tag": "CBFS13700", "src": os.path.join(BENCH, "CBFS"), "fam": "cbfs",
        "role": "the row whose reader continuity is hardcoded at rc4_score.py:683",
    },
    "AR_1_Ret_360__NULL": {
        "case": os.path.join(KAAN, "AR_1_Ret_360__NULL"),
        "log": os.path.join(KAAN, "AR_1_Ret_360__NULL", "log.run"),
        "tag": "AR_1_Ret_360", "src": os.path.join(BENCH, "DUCT", "AR_1_Ret_360"),
        "fam": "duct",
        "role": "CROSS-GEOMETRY CONTROL -- the duct baseline, where the two "
                "channels are expected to AGREE in order of magnitude",
    },
    "AR_1_Ret_360__TRUTHR": {
        "case": os.path.join(KAAN, "AR_1_Ret_360__TRUTHR"),
        "log": os.path.join(KAAN, "AR_1_Ret_360__TRUTHR", "log.run"),
        "tag": "AR_1_Ret_360", "src": os.path.join(BENCH, "DUCT", "AR_1_Ret_360"),
        "fam": "duct",
        "role": "CROSS-GEOMETRY CONTROL -- the duct repaired row",
    },
}

# The registered bars, READ FROM RC4's OWN MODULE, never retyped here, so this
# module cannot drift from the thresholds it is comparing against and cannot be
# read as declaring bars of its own.
BINDING_BAR = S.CONTINUITY_BINDING       # 1e-3
SECOND_BAR = S.CONTINUITY_SECOND         # 1e-4

# Registered outcome classes, section 4 of the pre-flight registration.  Fixed.
CLASSES = ("R-INSIDE-BAR", "PHYSICS-NONCONVERGENCE", "READER-FLOOR-DOMINATED",
           "NOT A RESULT")

# The producer channel's line, one compiled pattern, anchored on the solver's
# own wording.
CONT_RE = re.compile(
    r"^time step continuity errors : sum local = ([-0-9.eE+]+), "
    r"global = ([-0-9.eE+]+), cumulative = ([-0-9.eE+]+)", re.M)

PLANT_SCALE = 1.234e-02      # the planted divergence's amplitude, relative
PLANT_MIN_MOVE = 1e-9        # channel R must move by at least this, or refuse
FIELDS_R = ("U", "k", "nut", "kDeficit")
SOLVER_TOLERANCE = 1e-9      # section 4: "at solver tolerance" means P below this


def refuse(msg):
    sys.stderr.write("PREFLIGHT REFUSED (sys.exit 2): " + str(msg) + "\n")
    sys.stderr.flush()
    raise SystemExit(2)


def refuse_if_unfrozen(prereg_path=PREREG):
    """This pre-flight's own registration, made executable.  Independent of
    RC4's: it reads a DIFFERENT file and a DIFFERENT token, and clearing one
    cannot clear the other."""
    if not os.path.exists(prereg_path):
        refuse("pre-flight registration absent: " + prereg_path)
    if UNFROZEN_TOKEN in open(prereg_path, errors="replace").read():
        refuse("the pre-flight registration is DRAFT/UNFROZEN ("
               + UNFROZEN_TOKEN + " still in " + prereg_path
               + "); nothing may be measured against it")
    return True


def rc4_root_absent_or_refuse():
    """RC4 MUST HAVE HAD ZERO COMPUTE, and the prober must be shown able to see.

    A "not found" from a probe never shown able to find anything is not
    evidence, so the control is checked in the SAME call.
    """
    if not os.path.isdir(RC4_ROOT_CONTROL):
        refuse("the run-root prober's CONTROL path " + RC4_ROOT_CONTROL
               + " does not exist, so an ABSENT reading on "
               + RC4_RUN_ROOT + " would be from a prober not shown able to see "
               "anything.  Standing rule 3: plant the zero")
    if os.path.exists(RC4_RUN_ROOT):
        refuse("RC4's registered run root " + RC4_RUN_ROOT + " EXISTS.  RC4 has "
               "had compute, its gates are CLOSED, and this pre-flight's whole "
               "premise -- that it runs before RC4's first compute and cannot "
               "close its gates -- is false")
    return {"rc4_run_root": RC4_RUN_ROOT, "absent": True,
            "control_path": RC4_ROOT_CONTROL, "control_exists": True}


# ------------------------------------------------- channel P, the producer
def channel_P(log_path):
    """The solver's OWN continuity error, from ONE NAMED log.  Never a glob.

    Returns the FINAL `sum local` and the line count.  A named log with no
    continuity line REFUSES: a missing channel is not a zero, and a reader that
    cannot see the channel cannot report it absent.
    """
    if not os.path.exists(log_path):
        refuse("channel P: the named log artifact is absent: " + str(log_path))
    txt = open(log_path, errors="replace").read()
    hits = CONT_RE.findall(txt)
    if not hits:
        refuse("channel P: " + log_path + " carries NO "
               "'time step continuity errors' line.  The producer channel is "
               "ABSENT for this row, which is not the same as the producer "
               "reporting zero, and no value is invented for it")
    last = hits[-1]
    return {"log": log_path, "n_lines": len(hits),
            "sum_local": float(last[0]), "global": float(last[1]),
            "cumulative": float(last[2]),
            "sum_local_first": float(hits[0][0])}


def channel_P_lines(log_path):
    """Line count only, and it does NOT refuse -- the control needs a reader
    that can legitimately report zero hits on a log that has none."""
    if not os.path.exists(log_path):
        return 0
    return len(CONT_RE.findall(open(log_path, errors="replace").read()))


# ---------------------------------------- channel R, the reconstruction reader
def assemble_read_only(row, dst):
    """A scratch case `rc4_score.score_row` can open, from a preserved row's OWN
    bytes.  `copy2`, so real mtimes carry over and nothing is re-dated.

    `score_row` reads `<latest>/{U,k,nut,kDeficit}` and `0/bijDelta`.  The
    preserved rows carry `bijDelta` at the solved time, not at `0`, so it is
    copied to `0/bijDelta` -- which is faithful for these rows and is REPORTED
    per row (`bijDelta_max_abs`) rather than assumed, because for an UNCORRECTED
    baseline it must be identically zero and the reader would otherwise be
    handed a correction the row did not run.
    """
    case = row["case"]
    lt = r4_lib.latest_time(case)
    if lt == "0":
        refuse("channel R: " + case + " has no non-zero time directory")
    src_t = os.path.join(case, lt)
    os.makedirs(os.path.join(dst, lt), exist_ok=True)
    os.makedirs(os.path.join(dst, "0"), exist_ok=True)
    for f in FIELDS_R:
        p = os.path.join(src_t, f)
        if not os.path.exists(p):
            refuse("channel R: " + p + " absent, so the reader cannot be run on "
                   "this row and no number is reported for it")
        shutil.copy2(p, os.path.join(dst, lt, f))
    bd = os.path.join(src_t, "bijDelta")
    if not os.path.exists(bd):
        refuse("channel R: " + bd + " absent; score_row opens 0/bijDelta")
    shutil.copy2(bd, os.path.join(dst, "0", "bijDelta"))
    return dst, lt


def channel_R(row, bench, scratch):
    """`rc4_score.score_row`, UNMODIFIED.  Returns the reader's continuity keys.

    The keys returned are the very keys RC4's screen consults: `continuity_ok`
    at `rc4_score.py:303` is what `rc4_score.py:430` reads.  Nothing is
    recomputed here, so this module cannot disagree with the screen about what
    the reader says.
    """
    case, lt = assemble_read_only(row, scratch)
    full = S.score_row(row["tag"], case, bench)
    bd = np.asarray(read_field(os.path.join(case, "0", "bijDelta")),
                    float).reshape(-1)
    return {"time": lt,
            "divU_rms_over_gradscale": full["divU_rms_over_gradscale"],
            "continuity_ok": full["continuity_ok"],
            "continuity_inside_1e4": full["continuity_inside_1e4"],
            "n_cells": full["n_cells"],
            "bijDelta_max_abs": float(np.abs(bd).max()),
            "kDeficit_rms": full["kDeficit_rms"]}


def plant_control_R(row, bench, scratch):
    """DIRECTION A: can channel R return a DIFFERENT number at all?

    A known divergence is planted into a scratch copy of `U` -- each component
    scaled by `1 + PLANT_SCALE * i / n`, which changes `div(U)` by construction
    -- written back with `rc4_score.swap_internal_vector` UNMODIFIED, and the
    reader is re-run on the planted case.  REFUSES unless the metric MOVES.

    DIRECTION B: the same unplanted row read twice must agree EXACTLY, so a
    "moved" reading is not the reader being nondeterministic.
    """
    clean = os.path.join(scratch, "clean")
    a = channel_R(row, bench, clean)
    b = channel_R(row, bench, os.path.join(scratch, "clean_again"))
    if a["divU_rms_over_gradscale"] != b["divU_rms_over_gradscale"]:
        refuse("channel R DIRECTION B: the reader is not deterministic on "
               + row["case"] + " (" + repr(a["divU_rms_over_gradscale"]) + " vs "
               + repr(b["divU_rms_over_gradscale"]) + "); a move under the plant "
               "would then prove nothing")
    planted = os.path.join(scratch, "planted")
    shutil.copytree(clean, planted)
    up = os.path.join(planted, a["time"], "U")
    U = np.asarray(read_field(up), float).reshape(-1, 3)
    n = U.shape[0]
    fac = 1.0 + PLANT_SCALE * (np.arange(n, dtype=float) / max(n - 1, 1))
    S.swap_internal_vector(up, up, U * fac[:, None])
    full = S.score_row(row["tag"], planted, bench)
    moved = abs(full["divU_rms_over_gradscale"] - a["divU_rms_over_gradscale"])
    if moved <= PLANT_MIN_MOVE:
        refuse("channel R DIRECTION A: a planted divergence of relative "
               "amplitude " + repr(PLANT_SCALE) + " moved the reader's metric by "
               "only " + repr(moved) + " (<= " + repr(PLANT_MIN_MOVE) + ").  The "
               "reader is not shown able to see a change, so its value on this "
               "row is not evidence.  Standing rule 3")
    return {"clean": a["divU_rms_over_gradscale"],
            "planted": full["divU_rms_over_gradscale"], "moved_by": moved,
            "deterministic": True, "plant_scale": PLANT_SCALE,
            "verdict": "PASS"}


# ------------------------------------------------------------ the comparison
def classify(rows):
    """Section 4's registered outcome classes, in the registered order.

    RETURNS ONE OF `CLASSES` ABOUT THE PRE-FLIGHT'S OWN QUESTION.  It is NOT an
    RC4 verdict, it grades no RC4 gate, and no label here can be read as one.
    """
    base = rows.get("CBFS13700__NULL")
    duct = rows.get("AR_1_Ret_360__NULL")
    if base is None or duct is None:
        return "NOT A RESULT", ["the registered baseline row or the duct "
                                "cross-geometry control is missing"]
    R = base["R"]["divU_rms_over_gradscale"]
    P = base["P"]["sum_local"]
    why = ["CBFS baseline: channel R = %.6g, channel P = %.6g, ratio R/P = %.3g"
           % (R, P, R / P if P else float("inf")),
           "duct baseline control: channel R = %.6g, channel P = %.6g"
           % (duct["R"]["divU_rms_over_gradscale"], duct["P"]["sum_local"])]
    if R < BINDING_BAR:
        why.append("the reader's floor on the CBFS baseline is INSIDE the "
                   "registered binding bar " + repr(BINDING_BAR))
        return "R-INSIDE-BAR", why
    if P >= SOLVER_TOLERANCE:
        why.append("the producer's own channel also reports %.6g, at or above "
                   "the registered solver-tolerance figure %.6g, so the "
                   "continuity error is the SOLVER'S and not the reader's"
                   % (P, SOLVER_TOLERANCE))
        return "PHYSICS-NONCONVERGENCE", why
    why.append("the producer's own channel reports %.6g, BELOW the registered "
               "solver-tolerance figure %.6g, while the reader's floor on the "
               "same uncorrected row is %.6g -- above the binding bar %.6g and "
               "above the second reading %.6g"
               % (P, SOLVER_TOLERANCE, R, BINDING_BAR, SECOND_BAR))
    return "READER-FLOOR-DOMINATED", why


def measure(out_path=None):
    """The one measuring entry point.  Refuses while the pre-flight is DRAFT."""
    refuse_if_unfrozen()
    root_before = rc4_root_absent_or_refuse()
    os.makedirs(PREFLIGHT_ROOT, exist_ok=True)
    scratch = tempfile.mkdtemp(prefix="preflight_", dir=PREFLIGHT_ROOT)
    out = {"apparatus_demonstration": True,
           "asserts_no_rc4_gate_verdict": True,
           "rc4_run_root_before": root_before,
           "binding_bar_read_from": "rc4_score.CONTINUITY_BINDING",
           "binding_bar": BINDING_BAR, "second_bar": SECOND_BAR,
           "solver_tolerance_figure": SOLVER_TOLERANCE, "rows": {}}
    try:
        for name in sorted(ROWS):
            row = ROWS[name]
            bench = SB.load_case(row["tag"], row["src"], row["fam"])
            sub = os.path.join(scratch, name)
            os.makedirs(sub)
            rec = {"role": row["role"],
                   "P": channel_P(row["log"]),
                   "R": channel_R(row, bench, os.path.join(sub, "read")),
                   "R_plant_control": plant_control_R(
                       row, bench, os.path.join(sub, "plant"))}
            rec["ratio_R_over_P"] = (rec["R"]["divU_rms_over_gradscale"]
                                     / rec["P"]["sum_local"]
                                     if rec["P"]["sum_local"] else None)
            out["rows"][name] = rec
        out["outcome_class"], out["reasons"] = classify(out["rows"])
        if out["outcome_class"] not in CLASSES:
            refuse("outcome class " + repr(out["outcome_class"])
                   + " is not in the registered set " + str(CLASSES))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    out["rc4_run_root_after"] = rc4_root_absent_or_refuse()
    print("PRE-FLIGHT OUTCOME CLASS: " + out["outcome_class"]
          + "   (an apparatus finding; NOT an RC4 verdict)")
    for r in out["reasons"]:
        print("  " + r)
    if out_path:
        json.dump(out, open(out_path, "w"), indent=1, default=str)
    return out


# ---------------------------------------------------------------- selftest
def _fires(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except SystemExit as e:
        return int(e.code or 0) == 2
    return False


FORBIDDEN = ("score_all", "verdict", "gate_arithmetic", "cut", "ceiling_for",
             "run_solve", "run_campaign", "build")


def _no_gate_calls():
    """Executable proof that this module CANNOT close an RC4 gate or launch a
    solve: an `ast` parse of itself, requiring that no call anywhere reaches
    RC4's grading or launching entry points."""
    tree = ast.parse(open(os.path.abspath(__file__)).read())
    bad = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        nm = f.attr if isinstance(f, ast.Attribute) else (
            f.id if isinstance(f, ast.Name) else "")
        if nm in FORBIDDEN:
            bad.append((getattr(node, "lineno", -1), nm))
    return bad


def selftest():
    ok = []

    def note(name, passed, detail=""):
        ok.append((name, bool(passed), detail))

    tree = ast.parse(open(os.path.abspath(__file__)).read())
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    note("ast.Assert count == 0", n_assert == 0, "counted " + str(n_assert))

    bad = _no_gate_calls()
    note("this module calls NO RC4 grading or launching entry point -- checked "
         "by ast parse of itself, not asserted in prose",
         not bad, "forbidden calls found: " + repr(bad))
    note("the forbidden-call sweep is not blind: it FINDS a planted call",
         [n for _, n in _no_gate_calls_on(
             "def _x():\n    S.gate_arithmetic(1, 2)\n")] == ["gate_arithmetic"])

    note("this module REFUSES while its OWN registration is DRAFT/UNFROZEN",
         _fires(refuse_if_unfrozen))
    note("it REFUSES a measurement while DRAFT, at the entry point",
         _fires(measure))
    note("its DRAFT token is NOT RC4's token, so clearing one cannot clear the "
         "other", UNFROZEN_TOKEN != B.UNFROZEN_TOKEN
         and UNFROZEN_TOKEN not in B.UNFROZEN_TOKEN
         and B.UNFROZEN_TOKEN not in UNFROZEN_TOKEN,
         repr(UNFROZEN_TOKEN) + " vs " + repr(B.UNFROZEN_TOKEN))
    note("the pre-flight scratch root shares NO prefix with RC4's run root, so "
         "no glob against one can reach the other",
         not PREFLIGHT_ROOT.startswith(RC4_RUN_ROOT)
         and not RC4_RUN_ROOT.startswith(PREFLIGHT_ROOT)
         and "rc4" not in os.path.basename(PREFLIGHT_ROOT),
         PREFLIGHT_ROOT)
    note("the registered bars are READ from rc4_score, not retyped here",
         BINDING_BAR is S.CONTINUITY_BINDING
         and SECOND_BAR is S.CONTINUITY_SECOND,
         "binding %.0e, second %.0e" % (BINDING_BAR, SECOND_BAR))

    root = rc4_root_absent_or_refuse()
    note("RC4's registered run root is ABSENT, with the prober shown able to "
         "see a directory that DOES exist in the same call",
         root["absent"] and root["control_exists"],
         RC4_RUN_ROOT + " absent; " + RC4_ROOT_CONTROL + " exists")

    # ---- channel P, both directions, on REAL preserved logs.
    real = ROWS["CBFS13700__NULL"]["log"]
    real2 = ROWS["CBFS13700__TRUTHR"]["log"]
    if os.path.exists(real) and os.path.exists(real2):
        p1, p2 = channel_P(real), channel_P(real2)
        note("channel P reads the producer's own continuity channel from ONE "
             "NAMED log and returns DIFFERENT values on two different logs -- "
             "so it is not returning a constant",
             p1["sum_local"] != p2["sum_local"]
             and p1["n_lines"] != p2["n_lines"],
             "%d lines vs %d lines" % (p1["n_lines"], p2["n_lines"]))
    else:
        note("the preserved logs channel P names are on disk", False,
             "missing " + real + " or " + real2)
    tmp = tempfile.mkdtemp(prefix="preflight_selftest_")
    try:
        empty = os.path.join(tmp, "log.nochannel")
        open(empty, "w").write("Time = 1\nsomething else entirely\nEnd\n")
        note("channel P REFUSES a named log carrying no continuity line -- a "
             "MISSING channel is not a zero", _fires(channel_P, empty))
        note("channel P REFUSES a log that is not there at all",
             _fires(channel_P, os.path.join(tmp, "absent.log")))
        note("the line counter can legitimately report ZERO on a log with none, "
             "and NON-ZERO on one with them -- so the refusal above is a "
             "judgement about this log, not a blind reader",
             channel_P_lines(empty) == 0
             and channel_P_lines(real) > 0 if os.path.exists(real) else False,
             "0 on the synthetic log, %d on the real one"
             % channel_P_lines(real))
        one = os.path.join(tmp, "log.one")
        open(one, "w").write(
            "time step continuity errors : sum local = 1.5e-13, "
            "global = -2e-17, cumulative = 3e-11\n")
        note("channel P parses the solver's line format exactly, on a "
             "single-line specimen", channel_P(one)["sum_local"] == 1.5e-13)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    note("the registered outcome classes are a fixed closed set of 4",
         len(CLASSES) == 4 and "NOT A RESULT" in CLASSES, str(CLASSES))

    root2 = rc4_root_absent_or_refuse()
    note("RC4's run root is STILL absent after every selftest arm, control "
         "still firing", root2["absent"] and root2["control_exists"])

    width = max(len(n) for n, _, _ in ok)
    for name, passed, detail in ok:
        print(("  %-" + str(width) + "s  %s%s")
              % (name, "PASS" if passed else "FAIL",
                 ("   [" + detail + "]") if detail else ""))
    bad_names = [n for n, p, _ in ok if not p]
    if bad_names:
        sys.stderr.write("SELFTEST FAILED: " + "; ".join(bad_names) + "\n")
        raise SystemExit(1)
    print("preflight_two_channel selftest: %d/%d PASS" % (len(ok), len(ok)))
    return 0


def _no_gate_calls_on(text):
    """The forbidden-call sweep, applied to a STRING, so the sweep itself can be
    shown to find a planted violation."""
    out = []
    for node in ast.walk(ast.parse(text)):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        nm = f.attr if isinstance(f, ast.Attribute) else (
            f.id if isinstance(f, ast.Name) else "")
        if nm in FORBIDDEN:
            out.append((getattr(node, "lineno", -1), nm))
    return out


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--measure" in argv:
        i = argv.index("--measure")
        out = argv[i + 1] if len(argv) > i + 1 else None
        measure(out)
        return 0
    sys.stderr.write("usage: preflight_two_channel.py --selftest "
                     "| --measure [out.json]\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
