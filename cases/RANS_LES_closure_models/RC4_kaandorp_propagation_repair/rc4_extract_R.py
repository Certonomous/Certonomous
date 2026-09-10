#!/usr/bin/env python3
"""RC4 gate P-1 -- R-EXTRACTION VALIDITY.  Runs FIRST.  Zero compute for the
three preserved cases.

Registration: cases/RANS_LES_closure_models/RC4_kaandorp_propagation_repair/
PREREGISTRATION.md -- section 1.7 (the defect found at drafting), section 5 P-1
(the gate), section 6.1 (no ast.Assert), section 9.1 (the extraction's cost)
section 10 (the anti-gaming register) and section 11 (this module's registered
job and its registered refusals).

THE GATE, verbatim from section 5
---------------------------------
  "The frozen-RANS extraction must reproduce the `k` it was extracted from:
   relative L2 drift of recovered `k` from `k_data` <= 0.05, on the sign branch
   the extraction actually used."

  "Read from the extraction log, not recomputed."

  "Registered consequence: a case failing P-1 is BLOCKED -- its T-bR row is not
   run, and its number is never quoted as a ceiling.  If fewer than 2 of the 3
   in-scope cases survive P-1, RC4 as a whole returns BLOCKED -- it does not
   rescale the denominator and report a PASS on one case."

WHICH BRANCH "THE EXTRACTION ACTUALLY USED"
-------------------------------------------
`kCorrectiveFrozenFoam` prints the L-26 sign experiment for BOTH conventions at
the foot of its log, as two lines of the form

    RScale = +1: relative L2 drift of recovered k from k_data = 3.62632e-05
    RScale = -1: relative L2 drift of recovered k from k_data = 0.993315

The branch the extraction used is the one that reproduces `k_data`, i.e. the
one with the SMALLER drift, and section 10 fixes the choice that way: "one sign
convention chosen by the P-1 drift criterion before any propagation run, and
recorded".  That is a criterion about the EXTRACTION'S INTERNAL CONSISTENCY,
never about agreement with the velocity reference -- section 10 forbids
"choosing the R sign convention because one of them gives a better U_rms" and
this module never sees a U_rms.

ONE NAMED ARTIFACT PER CHECK.  Every drift reading names its log file
explicitly.  No glob is fed to `tail`: `grep` on this box is ugrep, a glob has
no defined last member, and a "last log" read that way is a coin flip.

REGISTERED REFUSALS (section 11), every one a sys.exit(2), never an assert:
  * the drift line absent from a log,
  * drift > 0.05 on a case being propagated.

NOTHING IS LAUNCHED.  `AR_3_Ret_360` has no extraction on disk and section 9.1
budgets 60 wall s for one; the builder and runner for it are here, and both
refuse while the registration carries PENDING_SUPERVISOR_FREEZE.

REUSE, SCOPED (L-512): `r4_lib.frozen_complete` (R4_sparta_build/r4_lib.py:272)
is the lab's frozen strict-completion rule for a `kCorrectiveFrozenFoam`
extraction, which is exactly the run this module produces.  It is reused
UNMODIFIED, is neither edited nor reimplemented, and its new use is exercised
in both directions by `--selftest`.  `r4_lib.latest_time` likewise.
"""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CLOSURE = os.path.dirname(HERE)
COMMON = os.path.join(CLOSURE, "_common")
R4 = os.path.join(CLOSURE, "R4_sparta_build")
for _p in (HERE, COMMON, R4):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from of_read import read_field, sym_to_full                  # noqa: E402
import sst_baseline_metrics as SB                            # noqa: E402
import r4_lib                                                # noqa: E402
import build_rc4_cases as B                                  # noqa: E402

DRIFT_MAX = 0.05             # section 5 P-1, FIXED.  Never widened.
MIN_CASES = 2                # "fewer than 2 of the 3 in-scope cases" -> BLOCKED
N_INSCOPE = 3
FROZEN_MODEL = "kOmegaSSTFrozen"
FROZEN_SOLVER = "kCorrectiveFrozenFoam"
EXTRACT_TIMEOUT_S = 1800
FOAM = "source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1"

# The preserved extractions, ONE NAMED LOG EACH (section 1.7).
PRESERVED = "/home/ubuntu/closure-data/aposteriori/kaandorp"
PRESERVED_LOGS = {
    "AR_1_Ret_360": os.path.join(PRESERVED, "AR_1_Ret_360__FROZENEXTRACT",
                                 "log.frozen"),
    "CBFS13700": os.path.join(PRESERVED, "CBFS13700__FROZENEXTRACT",
                              "log.frozen"),
    "PHLL10595": os.path.join(PRESERVED, "PHLL10595__FROZENEXTRACT",
                              "log.frozen"),
}
# AR_3_Ret_360 has no extraction on disk; RC4 must run one (section 1.7, 9.1).
RC4_EXTRACT_ROOT = B.ROOT


def refuse(msg):
    sys.stderr.write("RC4 REFUSED (sys.exit 2): " + str(msg) + "\n")
    sys.stderr.flush()
    raise SystemExit(2)


DRIFT_RE = re.compile(
    r"^\s*RScale\s*=\s*([+-]?1)\s*:\s*relative L2 drift of recovered k from "
    r"k_data\s*=\s*([0-9.eE+-]+)\s*$", re.M)


def extraction_log_path(tag, root=RC4_EXTRACT_ROOT):
    """The ONE named log this case's P-1 reading is taken from."""
    if tag in PRESERVED_LOGS:
        return PRESERVED_LOGS[tag]
    return os.path.join(root, tag + "__FROZENEXTRACT", "log.frozen")


def read_drift(log_path):
    """Both sign branches' k-reproduction drift, read from ONE named log.

    Registered refusal: the drift line absent from a log.
    """
    if not os.path.exists(log_path):
        refuse("P-1: extraction log absent: " + log_path
               + ".  P-1 is read from the extraction log, not recomputed, so "
               "an absent log is not a small drift -- it is no reading at all")
    txt = open(log_path, errors="replace").read()
    found = {}
    for sign, val in DRIFT_RE.findall(txt):
        key = "+1" if sign.lstrip("+") == "1" else "-1"
        found[key] = float(val)
    missing = [s for s in ("+1", "-1") if s not in found]
    if missing:
        refuse("P-1: the 'relative L2 drift of recovered k from k_data' line "
               "is absent from " + log_path + " for RScale branch(es) "
               + ", ".join(missing) + "; nothing in this log gates the "
               "extraction and the case cannot be admitted on faith")
    return found


def p1_reading(tag, log_path=None, root=RC4_EXTRACT_ROOT):
    """One case's P-1 reading.  Records the branch, as section 10 requires."""
    path = log_path or extraction_log_path(tag, root)
    d = read_drift(path)
    branch = "+1" if d["+1"] <= d["-1"] else "-1"
    used = d[branch]
    other = d["-1" if branch == "+1" else "+1"]
    return {"case": tag, "log": path, "drift_plus1": d["+1"],
            "drift_minus1": d["-1"], "branch_used": branch,
            "drift_used": used,
            "drift_ratio_other_over_used": (other / used) if used else None,
            "threshold": DRIFT_MAX, "admitted": bool(used <= DRIFT_MAX)}


def p1_gate(tags, root=RC4_EXTRACT_ROOT, propagating=None, logs=None):
    """Apply P-1 across the in-scope cases.

    `propagating` is the set of cases whose T-bR row is about to be built or
    run.  Registered refusal: drift > 0.05 on a case being propagated.
    """
    logs = logs or {}
    readings = {}
    for tag in tags:
        readings[tag] = p1_reading(tag, logs.get(tag), root)
    admitted = sorted(t for t in readings if readings[t]["admitted"])
    blocked = sorted(t for t in readings if not readings[t]["admitted"])
    for tag in sorted(propagating or ()):
        r = readings.get(tag)
        if r is None:
            refuse("P-1: " + tag + " is being propagated with no P-1 reading "
                   "at all; P-1 runs FIRST")
        if not r["admitted"]:
            refuse("P-1: " + tag + " is being propagated with a k-reproduction "
                   "drift of %.6g on the %s branch, above the registered %.3g "
                   "(log %s).  An extracted R that cannot reproduce the k it "
                   "was extracted from is not a usable reference; the case is "
                   "BLOCKED and its number is never quoted as a ceiling"
                   % (r["drift_used"], r["branch_used"], DRIFT_MAX, r["log"]))
    out = {"readings": readings, "admitted": admitted, "blocked": blocked,
           "n_admitted": len(admitted), "min_cases": MIN_CASES,
           "n_inscope": N_INSCOPE,
           "item_blocked": len(admitted) < MIN_CASES,
           "threshold": DRIFT_MAX}
    for tag in sorted(readings):
        r = readings[tag]
        print("[P-1] %-14s drift(%s) = %.6g  (other branch %.6g)  <= %.3g : %s"
              % (tag, r["branch_used"], r["drift_used"],
                 r["drift_plus1"] if r["branch_used"] == "-1"
                 else r["drift_minus1"], DRIFT_MAX,
                 "ADMITTED" if r["admitted"] else "BLOCKED"))
    if out["item_blocked"]:
        print("[P-1] only %d of %d in-scope cases survive P-1; RC4 as a whole "
              "returns BLOCKED.  The denominator is NOT rescaled (section 5)"
              % (len(admitted), N_INSCOPE))
    return out


# ---------------------------------------- the extraction RC4 must still run
def build_extraction_case(tag, root=RC4_EXTRACT_ROOT, check_freeze=True):
    """Build the frozen-RANS extraction case for a case with no extraction.

    Re-implemented from the method of Kaandorp2020_TBRF/aposteriori/frozen_R.py
    (which section 11 forbids this item to edit, and whose libs guard at :79 is
    an `assert` that section 6.1 forbids).  Nothing is launched here.
    """
    if check_freeze:
        B.refuse_if_unfrozen()
    src, t0 = B.require_bench_fields(tag)
    d = SB.load_case(tag, src, B.CASES[tag][1])
    case = os.path.join(root, tag + "__FROZENEXTRACT")
    B.guard_no_existing_times(case)
    shutil.rmtree(case, ignore_errors=True)
    shutil.copytree(src, case)
    for junk in ("postProcessing", "convergencePlots", "dynamicCode", "VTK"):
        shutil.rmtree(os.path.join(case, junk), ignore_errors=True)
    td = os.path.join(case, t0)
    _swap_internal(os.path.join(td, "U"), np.asarray(d["U_LES"], float), 3)
    _swap_internal(os.path.join(td, "k"), np.asarray(d["k_LES"], float), 1)
    tau = np.asarray(d["tau_LES"], float)
    rows = "\n".join("(" + " ".join("%.17g" % c for c in r) + ")" for r in tau)
    open(os.path.join(td, "tauij"), "w").write(
        "FoamFile { version 2.0; format ascii; class volSymmTensorField; "
        "object tauij; }\ndimensions      [0 2 -2 0 0 0 0];\n"
        "internalField   nonuniform List<symmTensor>\n" + str(len(tau))
        + "\n(\n" + rows + "\n)\n;\n" + B.patch_bcs(case, 6))
    cd = os.path.join(case, "system", "controlDict")
    s = open(cd).read()
    s = re.sub(r"^\s*libs.*$", "", s, flags=re.M)
    s = re.sub(r"startTime\s+\S+;", "", s)
    s = re.sub(r"startFrom\s+\w+;",
               "startFrom       startTime;\nstartTime       " + t0 + ";", s)
    s = re.sub(r"endTime\s+\S+;",
               "endTime         " + str(int(t0) + 5000) + ";", s)
    s = re.sub(r"writeInterval\s+\S+;", "writeInterval   5000;", s)
    s = re.sub(r"functions\s*\{.*?\n\}", "functions\n{\n}", s, flags=re.S)
    open(cd, "w").write(s)
    B.set_libs_or_refuse(cd, (B.SPARTA_LIB,))     # L-222: EVERY call site checks
    tp = os.path.join(case, "constant", "turbulenceProperties")
    open(tp, "w").write(re.sub(r"RASModel\s+\w+\s*;",
                               "RASModel        " + FROZEN_MODEL + ";",
                               open(tp).read()))
    return case, t0


def _swap_internal(path, vals, ncomp):
    s = open(path).read()
    if "internalField" not in s or "boundaryField" not in s:
        refuse("not an OpenFOAM field file: " + path)
    i, j = s.index("internalField"), s.index("boundaryField")
    a = np.asarray(vals, float)
    if ncomp == 1:
        rows = "\n".join("%.17g" % v for v in a.reshape(-1))
        typ = "scalar"
    else:
        rows = "\n".join("(" + " ".join("%.17g" % c for c in r) + ")"
                         for r in a.reshape(-1, ncomp))
        typ = "vector" if ncomp == 3 else "symmTensor"
    n = a.reshape(-1, ncomp).shape[0] if ncomp > 1 else a.reshape(-1).shape[0]
    body = ("internalField   nonuniform List<" + typ + ">\n" + str(n)
            + "\n(\n" + rows + "\n)\n;\n\n")
    open(path, "w").write(s[:i] + body + s[j:])


def run_extraction(tag, root=RC4_EXTRACT_ROOT):
    """Run one frozen-RANS extraction.  Refuses while RC4 is DRAFT/UNFROZEN.

    This is the ONLY function in the module that starts a process, and it
    cannot be reached without the freeze: `build_extraction_case` refuses
    first, and so does this.

    AMENDMENT A2: this launch is BOOKED INTO THE CAMPAIGN WALL ACCUMULATOR.
    Section 9.2 registers the accumulator as "campaign-level" and states the
    arithmetic it exists to stop -- "9 solves plus AN EXTRACTION at 3,600 s of
    per-solve timeout would otherwise permit 36,000 s".  An accumulator that
    books the nine solves and not the extraction is not campaign-level, so the
    extraction's timeout is likewise `min(1800, cap - spent)` and its wall time
    lands in the same ledger.  `rc4_run` is imported HERE rather than at module
    scope because `rc4_run` imports this module.
    """
    B.refuse_if_unfrozen()
    import rc4_run as RUN                                     # noqa: PLC0415
    bud = RUN.budget_or_refuse(root, label=tag + " frozen-RANS extraction")
    eff = min(int(EXTRACT_TIMEOUT_S), int(bud["effective_timeout_s"]))
    case, t0 = build_extraction_case(tag, root)
    t = time.time()
    subprocess.run(
        FOAM + "; cd " + case + " && timeout " + str(eff) + " "
        + FROZEN_SOLVER + " -case . > log.frozen 2>&1; echo $? > rc",
        shell=True, executable="/bin/bash")
    wall = round(time.time() - t, 1)
    if not os.path.exists(os.path.join(case, "rc")):
        refuse("the " + tag + " extraction recorded NO EXIT STATUS at "
               + os.path.join(case, "rc") + ".  A missing rc is not rc = 0, and "
               "the wrapper's own return code is 0 for every outcome")
    rc = open(os.path.join(case, "rc")).read().strip()
    RUN.book(root, tag, "FROZENEXTRACT", wall, kind="extraction")
    ok, reason, info = r4_lib.frozen_complete(case)
    if not ok:
        refuse("the " + tag + " extraction is not COMPLETE by the lab's frozen "
               "completion rule (r4_lib.frozen_complete): " + reason)
    return {"case": case, "tag": tag, "rc": rc, "wall_s": wall,
            "effective_timeout_s": eff, "budget": bud,
            "core_minutes": wall * B.RANKS / 60.0, "completion": info}


def extracted_kdeficit_path(tag, root=RC4_EXTRACT_ROOT):
    """The ONE named kDeficit file P-1 admitted, for build_rc4_cases to copy."""
    case = (os.path.join(PRESERVED, tag + "__FROZENEXTRACT")
            if tag in PRESERVED_LOGS
            else os.path.join(root, tag + "__FROZENEXTRACT"))
    if not os.path.isdir(case):
        refuse("no extraction directory for " + tag + ": " + case)
    lt = r4_lib.latest_time(case)
    if lt == "0":
        refuse("the " + tag + " extraction wrote no non-zero time directory: "
               + case)
    p = os.path.join(case, lt, B.KDEFICIT)
    if not os.path.exists(p):
        refuse("the " + tag + " extraction wrote no kDeficit at " + p
               + "; there is no R to propagate")
    return p


# ---------------------------------------------------------------- selftest
def _fires(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except SystemExit as e:
        return int(e.code or 0) == 2
    return False


def _log(path, plus=None, minus=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = ["Settle verification: L2(R) moved 1e-06%  [SETTLED]",
             "Writing fields at iteration 647",
             "L-26 sign experiment: re-solving the k equation"]
    if plus is not None:
        lines.append("  RScale = +1: relative L2 drift of recovered k from "
                     "k_data = " + repr(plus))
    if minus is not None:
        lines.append("  RScale = -1: relative L2 drift of recovered k from "
                     "k_data = " + repr(minus))
    lines.append("End")
    open(path, "w").write("\n".join(lines) + "\n")
    return path


def selftest():
    ok = []

    def note(name, passed, detail=""):
        ok.append((name, bool(passed), detail))

    tree = ast.parse(open(os.path.abspath(__file__)).read())
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    note("ast.Assert count == 0", n_assert == 0, "counted " + str(n_assert))

    # ---- the REAL preserved logs, one named artifact each.  The numbers must
    # match section 1.7's table exactly, which is what makes this a reading of
    # the artifact and not of the document.
    want = {"AR_1_Ret_360": (3.62632e-05, 0.993315),
            "CBFS13700": (4.85518438281052e-07, 0.974810497433794),
            "PHLL10595": (0.065849156661484, 0.998788240427244)}
    for tag, (wp, wm) in want.items():
        p = PRESERVED_LOGS[tag]
        if not os.path.exists(p):
            note("preserved extraction log present for " + tag, False, p)
            continue
        r = p1_reading(tag)
        note("P-1 reads " + tag + " from its named log and matches section "
             "1.7 to the digit",
             r["drift_plus1"] == wp and r["drift_minus1"] == wm,
             "+1 %.6g  -1 %.6g  branch %s" % (r["drift_plus1"],
                                              r["drift_minus1"],
                                              r["branch_used"]))
    r1 = p1_reading("AR_1_Ret_360")
    note("P-1 ADMITS AR_1_Ret_360 (3.63e-05 <= 0.05)", r1["admitted"])
    rc = p1_reading("CBFS13700")
    note("P-1 ADMITS CBFS13700 (4.86e-07 <= 0.05)", rc["admitted"])
    rp = p1_reading("PHLL10595")
    note("P-1 BLOCKS PHLL10595 (0.0658 > 0.05) -- the defect section 1.7 found "
         "and no predecessor gated on", not rp["admitted"],
         "drift %.6g" % rp["drift_used"])
    note("P-1 records the sign branch the extraction used, and it is +1 on "
         "every preserved case",
         r1["branch_used"] == "+1" and rc["branch_used"] == "+1"
         and rp["branch_used"] == "+1")

    tmp = tempfile.mkdtemp(prefix="rc4_p1_selftest_")
    try:
        note("read_drift FIRES on an absent log",
             _fires(read_drift, os.path.join(tmp, "nolog")))
        note("read_drift FIRES when the +1 drift line is absent",
             _fires(read_drift, _log(os.path.join(tmp, "l1"), minus=0.99)))
        note("read_drift FIRES when the -1 drift line is absent",
             _fires(read_drift, _log(os.path.join(tmp, "l2"), plus=1e-5)))
        note("read_drift FIRES on a log with neither line",
             _fires(read_drift, _log(os.path.join(tmp, "l3"))))
        good = _log(os.path.join(tmp, "l4"), plus=1e-5, minus=0.9)
        d = read_drift(good)
        note("read_drift reads both branches from a well-formed log",
             d["+1"] == 1e-5 and d["-1"] == 0.9)
        flipped = _log(os.path.join(tmp, "l5"), plus=0.9, minus=1e-5)
        note("the branch used is the one that reproduces k_data, whichever "
             "sign that is",
             p1_reading("X", flipped)["branch_used"] == "-1")

        bad = _log(os.path.join(tmp, "l6"), plus=0.30, minus=0.99)
        note("P-1 FIRES (sys.exit 2) when a case being PROPAGATED has a drift "
             "above 0.05",
             _fires(p1_gate, ["X"], tmp, {"X"}, {"X": bad}))
        note("P-1 does NOT fire for the same case when it is not being "
             "propagated -- it is recorded BLOCKED instead",
             p1_gate(["X"], tmp, None, {"X": bad})["blocked"] == ["X"])
        note("P-1 FIRES when a case is propagated with no reading at all",
             _fires(p1_gate, [], tmp, {"Y"}, {}))

        g = p1_gate(["A", "B", "C"], tmp, None,
                    {"A": _log(os.path.join(tmp, "a"), plus=1e-5, minus=0.9),
                     "B": _log(os.path.join(tmp, "b"), plus=1e-4, minus=0.9),
                     "C": bad})
        note("two of three admitted -> the item is not BLOCKED",
             g["n_admitted"] == 2 and not g["item_blocked"])
        g2 = p1_gate(["A", "B", "C"], tmp, None,
                     {"A": _log(os.path.join(tmp, "a2"), plus=1e-5, minus=0.9),
                      "B": bad, "C": bad})
        note("one of three admitted -> RC4 as a whole is BLOCKED, and the "
             "denominator is not rescaled",
             g2["n_admitted"] == 1 and g2["item_blocked"])
        note("P-1 admits a case at exactly the 0.05 bar",
             p1_reading("Z", _log(os.path.join(tmp, "edge"), plus=DRIFT_MAX,
                                  minus=0.9))["admitted"])
        note("P-1 blocks a case just above the 0.05 bar",
             not p1_reading("Z", _log(os.path.join(tmp, "edge2"),
                                      plus=0.050001,
                                      minus=0.9))["admitted"])

        # ---- the scoped reuse of r4_lib.frozen_complete, both directions.
        exc = os.path.join(tmp, "extract_ok")
        _fake_extraction(exc, settled=True)
        okf, reason, info = r4_lib.frozen_complete(exc)
        note("r4_lib.frozen_complete PASSES a synthetic settled extraction "
             "(the scoped reuse, exercised)", okf, reason)
        exc2 = os.path.join(tmp, "extract_bad")
        _fake_extraction(exc2, settled=False)
        note("r4_lib.frozen_complete REJECTS an extraction that did not settle",
             not r4_lib.frozen_complete(exc2)[0])

        note("extracted_kdeficit_path FIRES when there is no extraction "
             "directory", _fires(extracted_kdeficit_path, "AR_3_Ret_360", tmp))
        note("build_extraction_case REFUSES while RC4 is DRAFT/UNFROZEN",
             _fires(build_extraction_case, "AR_3_Ret_360", tmp, True))
        note("run_extraction REFUSES while RC4 is DRAFT/UNFROZEN -- nothing "
             "in this module can start a solver",
             _fires(run_extraction, "AR_3_Ret_360", tmp))
        note("AR_3_Ret_360 genuinely has no extraction on disk, as section 1.7 "
             "states", not os.path.isdir(os.path.join(
                 PRESERVED, "AR_3_Ret_360__FROZENEXTRACT")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    width = max(len(n) for n, _, _ in ok)
    for name, passed, detail in ok:
        print(("  %-" + str(width) + "s  %s%s")
              % (name, "PASS" if passed else "FAIL",
                 ("   [" + detail + "]") if detail else ""))
    bad_names = [n for n, p, _ in ok if not p]
    if bad_names:
        sys.stderr.write("SELFTEST FAILED: " + "; ".join(bad_names) + "\n")
        raise SystemExit(1)
    print("rc4_extract_R selftest: %d/%d PASS" % (len(ok), len(ok)))
    return 0


def _fake_extraction(case, settled=True):
    """A synthetic kCorrectiveFrozenFoam case, complete or not, for exercising
    the frozen helper in both directions."""
    os.makedirs(os.path.join(case, "0"))
    td = os.path.join(case, "647")
    os.makedirs(td)
    open(os.path.join(case, "rc"), "w").write("0\n")
    lines = ["Time = 1",
             "CONVERGED (settle criterion) at iteration 647",
             "Settle verification: L2(R) moved 3.9349e-06% over the 108 "
             "verification iterations  [" + ("SETTLED" if settled
                                             else "NOT SETTLED") + "]",
             "Writing fields at iteration 647",
             "  RScale = +1: relative L2 drift of recovered k from k_data = 1e-05",
             "  RScale = -1: relative L2 drift of recovered k from k_data = 0.99",
             "End"]
    open(os.path.join(case, "log.frozen"), "w").write("\n".join(lines) + "\n")
    for f in ("U", "k", "omega", "nut", "bijDelta", "kDeficit", "bijData",
              "grad(U)"):
        open(os.path.join(case, "0", f), "w").write("0\n")
        p = os.path.join(td, f)
        open(p, "w").write("0\n")
        t0 = os.path.getmtime(os.path.join(case, "0", f))
        os.utime(p, (t0 + 60, t0 + 60))
    return case


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--p1" in argv:
        B.refuse_if_unfrozen()
        g = p1_gate(sorted(B.CASES))
        print(json.dumps({k: v for k, v in g.items() if k != "readings"},
                         indent=1))
        return 0
    if "--run-extraction" in argv:
        i = argv.index("--run-extraction")
        tag = argv[i + 1] if len(argv) > i + 1 else "AR_3_Ret_360"
        print(json.dumps(run_extraction(tag), indent=1, default=str))
        return 0
    sys.stderr.write("usage: rc4_extract_R.py --selftest | --p1 | "
                     "--run-extraction <case>\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
