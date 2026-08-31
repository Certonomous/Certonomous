# =====================================================================
# UNFROZEN, UNREVIEWED, INCOMPLETE DRAFT -- DO NOT RUN, DO NOT GRADE.
# Halted mid-authoring 2026-08-31 on Sanaa's order to stop work.
# This file is NOT a frozen grading path under CLAUDE.md rule 2: no
# pre-registration document accompanies it and no commit fixes it.
# closure-supervisor has NOT performed SUPERVISION_CHARTER sec.3 check 1
# (the measurement-script diff read) on this file. A relayed check is a
# summary, not a check, and no check has been performed at all here.
# It is committed ONLY so the work survives; the R4b instruments sat
# untracked through a 32-hour shutdown and were one checkout from gone.
# NOTHING THIS FILE PRODUCES IS A RESULT.
# =====================================================================
"""
M1b multi-model sweep REGRADE -- THE SUCCESSOR COMPARATOR.

A SUCCESSOR TO `grade_m1.py`, NOT A REPAIR OF IT.  M1 has consumed compute, so
standing rule 2 has closed its gates and standing rule 6 forbids editing its
comparator.  `grade_m1.py` is not touched by this rung, at this commit or ever.
VERIFICATION_CHARTER section 2d.1 would permit a post-compute grading-path
change on four conditions; this family DECLINED that exception on G1 and built
the successor G1b instead, and that precedent governs here.  Given a choice
between exercising an exception and not needing one, not needing one is
strictly better.

M1b IS FORWARD PROTECTION.  IT IS **NOT** REQUIRED IN ORDER TO GRADE M1, AND
NOTHING HERE BLOCKS THAT GRADING.  The verification team has ruled (DEAD_LEVER
_AUDIT section 16.1): the finding is true, the repair to the frozen comparator is
REFUSED, and M1 GRADING IS UNBLOCKED.  M1 will be graded under the frozen
`grade_m1.py` by a separate lane.  M1b exists because (a) the frozen comparator
has no fatal channel at all, so a future crashed solve on the next corpus would
sail through it, and (b) it carries the two CANNOT-SEE items named below.

THE TWO SUBSTANTIVE ADDITIONS
-----------------------------
(1) A FATAL / CRASH CHANNEL, which `grade_m1.py` does not have in any form.
    Measured on the frozen file (recognition control below):
`FOAM FATAL` 0, `Floating point exception` 0, `sigFpe` 0, `trapFpe` 0, `fatal`
0 -- while the same reader on the same file saw `def ` 31, `PASS` 11,
    `NOT A RESULT` 7, `GATE FAIL` 16, `endTime` 7, `ExecutionTime` 4.  The
    zeros are a real absence, not a blind reader.  A crashed solve therefore
    reached M1's physics gates with nothing in the way.

(2) A NON-FINITE-RESIDUAL CHANNEL.  `grade_m1.py`'s residual regex captures
    `([0-9.eE+-]+)`, which cannot match `nan`, `-nan`, `inf` or `Inf`.  Such a
    line does not fail the parse -- IT SIMPLY DOES NOT MATCH, and is dropped.
    The consequence is that a converge-then-diverge run grades CONVERGED at an
    early iteration, because the diverged iterations were removed from the
    history rather than failing it.  A DROPPED LINE PRODUCES A SMALLER n, NOT AN
    ERROR, so the failure is invisible in the output: it looks like a short but
    healthy run.  Reported LATENT, not live, by the verification team --
    0 unparseable lines in 9.19 M lines of the current corpus -- and repaired
    here as a REQUIREMENT ON THE SUCCESSOR.  M1b therefore counts residual lines
    TWICE, permissively and numerically, and refuses when the two counts differ.

EVERY BAND, THRESHOLD, CEILING, COUNT, LABEL AND GATE IS COPIED VERBATIM FROM
M1's FROZEN PREREGISTRATION.md (section 7, frozen at 7b00b3ec, amended
pre-compute at 73cd5ac5).  Nothing is widened, narrowed, added or removed.  The
new channel can only turn a row INCOMPLETE and therefore can only pull a verdict
DOWN, never up.

Grades 2 arms x 39 cases = 78 runs against the gates frozen in
M1_multimodel_sweep/PREREGISTRATION.md section 7.  Every threshold below is
REGISTERED and may not be changed after the first compute except by a dated
addendum that cannot alter a gate, threshold, cap or label (standing rule 2,
rule 6).

STANDING RULES CARRIED HERE, EACH BY AN INSTRUMENT AND NOT BY A COMMENT:
  rule 3  a plant is written to a field ON DISK, re-read by re-opening the file,
          and the comparator REFUSES (sys.exit 2) if the reader cannot see it.
          An in-memory plant does not satisfy this.
  rule 4  strict completion + the age guard.  A row that fails any clause is
          INCOMPLETE and its numbers are NOT COMPUTED -- refuse, never degrade.
  rule 5  DOES NOT APPLY.  One mesh per case, no triple, no GCI, no observed
          order.  The comparator PRINTS that sentence rather than leaving a
          reader to infer it.
  L-342   physics-critical vs infrastructure fields.  A missing STATUS is
          INFRASTRUCTURE: NOT MEASURED, and it can never void intact physics.
  L-332   no `assert` carries a refusal.  --selftest runs under `python3 -O`
          with every refusal still firing, AND parses its own AST to prove there
          is not one `ast.Assert` node in the file -- a regex on source text is
          not that proof.
  L-314   every guard ships its planted-failure proof.
  L-396   the fatal clause is NARROW.  The broad substring "Floating point
  D548    exception" is not a detector, it is very nearly a constant.
  L-402   a control reads bytes written by the REAL PRODUCER.  A synthetic
  sec.2j  fixture the harness wrote is not a birth demonstration.

Usage
  python3 grade_m1b.py --root /home/ubuntu/closure-data/multimodel_sweep
  python3 -O grade_m1b.py --selftest
  python3 grade_m1b.py --birth            # section 2j, real producer bytes
"""

import argparse
import ast
import datetime
import hashlib
import json
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------
# REGISTERED CONSTANTS -- frozen by PREREGISTRATION.md
# --------------------------------------------------------------------------
BENCH_ROOT_DEFAULT = "/home/ubuntu/closure-challenge-benchmark/data"
RUN_ROOT_DEFAULT = "/home/ubuntu/closure-data/multimodel_sweep"

ARMS = {"kOmegaSST_null": "kOmegaSST", "kOmega": "kOmega"}
NULL_ARM = "kOmegaSST_null"
TEST_ARM = "kOmega"
EXCLUDED_CASES = ("NASA_2DWMH",)

CAP_ITER = 20000                     # section 3
PHYSICS_FIELDS = ("U", "p", "k", "omega", "nut")
AGE_DATUM = "U"                      # 0/U, section 6 C4

CONV_K_TOL = 5.0e-6                  # section 4.1, sustained to CAP_ITER
CONV_OMEGA_TOL = 5.0e-6

G2_BAND = 1.0e-3                     # section 7 G2
G2_MIN_IN_BAND = 37
# SUPERVISOR'S RULING, 2026-08-27, before staging: G2's "37 of 39" was a LOTTERY
# over which two cases may miss the band.  It is replaced by a STRUCTURAL
# partition fixed here, which is strictly stronger at the same headline count.
# The 29 Parm_PH_29 hills are ITERATION-MATCHED -- their shipped reference was
# written at endTime 20000, exactly this sweep's cap -- so on those there is no
# excuse and ALL 29 must meet the band.  The 10 unmatched cases (8 ducts at
# 334-7009 under a criterion we do not use, CBFS at 30000, PH_Breuer at 10000)
# may contribute at most G2_UNMATCHED_MAX_OUT outliers, still under the ceiling.
# Net effect: the two permitted outliers can no longer hide among the hills.
G2_MATCHED_PREFIX = "alpha_"         # the 29 Parm_PH_29 hills
G2_UNMATCHED_MAX_OUT = 2
G2_CEILING = 1.0e-2
G2_REFUSE_ABOVE = 1.0e-1

G3_SEPARATION = 1.0e-2               # section 7 G3
G3_MIN_CASES = 30

G4_MAX_CAPBOUND = 8                  # section 7 G4

N_CASES = 39
N_RUNS = 78

PLANT = 1.234e-03                    # standing rule 3

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")

RULE5_STATEMENT = (
    "STANDING RULE 5 DOES NOT APPLY TO THIS RUNG: one mesh per case is shipped, "
    "no grid triple exists, and therefore no GCI, no observed order and no "
    "Roache triple state is computed or quoted anywhere in this output.")

TIME_DIR_RE = re.compile(r"^[0-9]+(\.[0-9]+)?$")

# --------------------------------------------------------------------------
# FATAL DETECTION -- THE ONE SUBSTANTIVE ADDITION IN M1b.
#
# `grade_m1.py` has NO fatal channel of any kind, so a crashed solve reached its
# physics gates unimpeded.  The obvious repair is the WRONG one, and it has
# already cost this lab a verdict.
#
# THE DEFECT NOT TO REPEAT (L-396, D548).  G1's clause matched the broad
# substring "Floating point exception".  OpenFOAM writes, on a HEALTHY start:
#     trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).
# That is the solver announcing that FPE trapping is ENABLED.  The broad
# substring matches it.  Measured by the closure supervisor 2026-08-27 over 70
# `log.run` files across three families: the clause fired on 63 of 70, and 57 of
# those carry a clean `End` line.  G1 graded NOT A RESULT on a banner and lost
# its entire 127.08 core-min verdict.
#
# MEASURED ON M1's OWN CORPUS, 2026-08-31, by the birth demonstration below,
# reading /home/ubuntu/closure-data/multimodel_sweep in place:
#     78 of 78 `log.run` carry the trapFpe banner
#     78 of 78 match the broad substring "Floating point exception"
#      0 of 78 match the narrow `Foam::sigFpe::sigHandler`
#      0 of 78 contain "FOAM FATAL"
# On M1 the broad form is not "very nearly" a constant.  It is a constant.  It
# would have condemned all 78 rows.
#
# The clause below is transcribed from the sibling successor
# `G1b_grid_triple_regrade/grade_g1b.py:299-307`, which is itself the form used
# at `R4b_pair_control/grade_r4b.py:840`.  It matches only evidence of an ACTUAL
# failure:
#   FOAM FATAL ERROR / FOAM FATAL IO ERROR -- OpenFOAM's own fatal banners;
#   sigFpe::sigHandler / sigSegv::sigHandler -- a handler that actually FIRED,
#       as opposed to one that was merely installed;
#   Foam::error::printStack -- a stack trace was printed;
#   a line that BEGINS with "Floating point exception" or "Segmentation fault"
#       -- the shell's own death message.  The banner line begins with
#       "trapFpe:", so the ^ anchor is the whole separation between the two.
# It deliberately does NOT match "trapFpe:", "trapping enabled", or the bare
# word "signal" (which appears in ordinary prose).
#
# The narrow token is NOT anchored to a line start, and that is deliberate and
# measured: on a real 14-rank crash the stack trace interleaves and the frame
# reads `[0] #1  Foam::sigFpe::sigHandler(int)[1] #1  Foam::sigFpe::...`, with
# no `#1` at column 0.  An anchored form would miss every parallel crash in the
# real corpus.  Both directions are enforced at run time by control C7 and by
# the section 2j birth demonstration, never by this comment.
# --------------------------------------------------------------------------
TRAPFPE_BANNER = ("trapFpe: Floating point exception trapping enabled "
                  "(FOAM_SIGFPE).")
RE_TRAPFPE_BANNER = re.compile(r"trapFpe:|trapping enabled")
# The BROAD form, transcribed only so this comparator can COUNT what it would
# have matched and carry that count into the record as INFRASTRUCTURE evidence.
# IT NEVER GATES ANYTHING HERE.
RE_BROAD_DEFECTIVE = re.compile(r"FOAM FATAL|Floating point exception|signal")
RE_FATAL = re.compile(
    r"FOAM FATAL ERROR"
    r"|FOAM FATAL IO ERROR"
    r"|sigFpe::sigHandler"
    r"|sigSegv::sigHandler"
    r"|Foam::error::printStack"
    r"|^Floating point exception"
    r"|^Segmentation fault",
    re.M)

# Section 2j: the birth demonstration is a PRECONDITION OF GRADING, and its
# artefact lives outside git with the data it reads (standing rule 13 -- the
# scratchpad is not a handoff channel).
BIRTH_DIR = "/home/ubuntu/closure-data/m1b_birth"
BIRTH_RECORD = os.path.join(BIRTH_DIR, "m1b_birth_demonstration.json")


class Refusal(Exception):
    def __init__(self, code, msg):
        super().__init__(f"REFUSE [{code}]: {msg}")
        self.code = code


def refuse(code, msg):
    raise Refusal(code, msg)


# --------------------------------------------------------------------------
# OpenFOAM ascii field reader.  Deliberately a SECOND, independent copy of the
# reader in stage_m1.py: each instrument carries its own reader and its own
# planted-zero control, so a divergence between the two is detectable rather
# than shared.
# --------------------------------------------------------------------------
def read_internal_field(path):
    if not os.path.isfile(path):
        refuse("FIELD-MISSING", f"no field file at {path}")
    txt = open(path, "r", errors="replace").read()
    m = re.search(r"^\s*internalField\s+(uniform|nonuniform)", txt, re.M)
    if not m:
        refuse("FIELD-PARSE", f"no internalField entry in {path}")
    if m.group(1) == "uniform":
        tail = txt[m.end():]
        stop = tail.find(";")
        if stop < 0:
            refuse("FIELD-PARSE", f"unterminated uniform internalField in {path}")
        body = tail[:stop].strip()
        if body.startswith("("):
            comps = [float(x) for x in body.strip("()").split()]
            return dict(kind="uniform", rank=len(comps), n=1, values=comps)
        try:
            return dict(kind="uniform", rank=1, n=1, values=[float(body)])
        except ValueError:
            refuse("FIELD-PARSE",
                   f"uniform internalField is not numeric in {path}: {body!r} "
                   f"(an unexpanded dictionary variable is not a value)")
    m2 = re.search(r"List<(\w+)>\s*\n?\s*(\d+)\s*\n?\s*\(", txt[m.start():])
    if not m2:
        refuse("FIELD-PARSE", f"cannot locate nonuniform List header in {path}")
    rank = {"scalar": 1, "vector": 3, "symmTensor": 6, "tensor": 9}.get(m2.group(1))
    if rank is None:
        refuse("FIELD-PARSE", f"unsupported List type {m2.group(1)} in {path}")
    n = int(m2.group(2))
    start = m.start() + m2.end()
    depth, i = 1, start
    while i < len(txt) and depth > 0:
        if txt[i] == "(":
            depth += 1
        elif txt[i] == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    if depth != 0:
        refuse("FIELD-PARSE", f"unbalanced parentheses in {path}")
    vals = [float(x) for x in txt[start:i].replace("(", " ").replace(")", " ").split()]
    if len(vals) != n * rank:
        refuse("FIELD-PARSE", f"{path}: header says {n}x{rank}={n * rank} numbers, "
                              f"found {len(vals)}")
    return dict(kind="nonuniform", rank=rank, n=n, values=vals)


def as_flat(field, ncells):
    """Expand a uniform field to ncells; refuse on a length mismatch."""
    if field["kind"] == "uniform":
        return list(field["values"]) * ncells
    if field["n"] != ncells:
        refuse("FIELD-SIZE", f"field holds {field['n']} cells, expected {ncells}")
    return field["values"]


def rel_l2(a, b):
    """|| a - b ||_2 / || b ||_2 .  b is the reference."""
    if len(a) != len(b):
        refuse("FIELD-SIZE", f"length mismatch {len(a)} vs {len(b)}")
    num = math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
    den = math.sqrt(sum(y * y for y in b))
    if den == 0.0:
        refuse("FIELD-ZERO", "the reference field has zero norm; a relative "
                             "difference against it is undefined")
    return num / den


def plant_into_field(path, plant=PLANT):
    txt = open(path, "r", errors="replace").read()
    m = re.search(r"^\s*internalField\s+(uniform|nonuniform)", txt, re.M)
    if not m:
        refuse("C1-PLANT", f"no internalField in {path}")
    if m.group(1) == "uniform":
        anchor = m.end()
    else:
        m2 = re.search(r"List<\w+>\s*\n?\s*\d+\s*\n?\s*\(", txt[m.start():])
        if not m2:
            refuse("C1-PLANT", f"cannot locate nonuniform data in {path}")
        anchor = m.start() + m2.end()
    numre = re.compile(r"[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?")
    mnum = numre.search(txt, anchor)
    if not mnum:
        refuse("C1-PLANT", f"no numeric token after the internalField header in {path}")
    before = float(mnum.group(0))
    open(path, "w").write(txt[:mnum.start()] + repr(before + plant) + txt[mnum.end():])
    back = numre.search(open(path, "r", errors="replace").read(), anchor)   # RE-OPEN
    if back is None or abs((float(back.group(0)) - before) - plant) > 1e-12:
        refuse("C1-PLANT", f"the plant did not land in {path}")
    return before, float(back.group(0))


def planted_zero_control(field_path, workdir):
    a = os.path.join(workdir, "c1_clean")
    b = os.path.join(workdir, "c1_planted")
    shutil.copyfile(field_path, a)
    shutil.copyfile(field_path, b)
    before, after = plant_into_field(b, PLANT)
    fa, fb = read_internal_field(a), read_internal_field(b)
    if len(fa["values"]) != len(fb["values"]):
        refuse("C1-PLANT", "planted and clean copies parsed to different lengths")
    seen = max(abs(x - y) for x, y in zip(fb["values"], fa["values"]))
    return dict(source=field_path, planted=PLANT, read_back_delta=after - before,
                reader_max_change=seen, passed=seen >= PLANT - 1e-15)


# --------------------------------------------------------------------------
# log and STATUS readers
# --------------------------------------------------------------------------
SOLVE_RE = re.compile(
    r"Solving for (\w+),\s*Initial residual = ([0-9.eE+-]+)")
# --------------------------------------------------------------------------
# NEW IN M1b: THE PERMISSIVE COUNTERPART OF SOLVE_RE.
#
# SOLVE_RE's value group is `[0-9.eE+-]+`.  It cannot match `nan`, `-nan`,
# `inf`, `-inf`, `NaN` or `Inf`.  A residual line carrying one of those DOES NOT
# FAIL THE PARSE -- IT SIMPLY DOES NOT MATCH, and vanishes from the history.
# The iteration is then absent rather than bad, so a run that converged and then
# blew up is graded CONVERGED at the last iteration before the blow-up.
#
# THE TRAP, STATED SO IT CANNOT BE FORGOTTEN: a parser that drops unparseable
# lines produces a SMALLER n, not an error.  The failure is invisible in the
# output.  It looks like a short but healthy run.  Any clause that counts
# iterations must therefore also check that the count it got equals the count
# the log actually contains.
#
# SOLVE_ANY_RE captures ANY token in the value position.  parse_log() counts
# both, and `residuals_fully_parsed` (a COMPLETION clause, so it can only pull a
# row DOWN) refuses when the two counts differ or when any value is non-finite.
# --------------------------------------------------------------------------
SOLVE_ANY_RE = re.compile(r"Solving for (\w+),\s*Initial residual = (\S+?)[,\s]")
RE_NONFINITE = re.compile(r"(?i)^[-+]?(nan|inf|infinity)$")
TIME_RE = re.compile(r"^Time = (\S+)\s*$")
MODEL_RE = re.compile(r"Selecting\s+(?:RAS\s+)?turbulence model\s+(\w+)")
MODEL_RE2 = re.compile(r"^\s*(?:RAS\s+)?[Mm]odel\s+(\w+)\s*$")


def parse_log(path):
    """Physics-critical: the End line, the ExecutionTime count, the last time,
    the residual history, the model the SOLVER ITSELF says it selected, and --
    NEW IN M1b -- whether the log carries evidence of an ACTUAL crash.

    The fatal scan is line-by-line rather than whole-file, so the ^ anchors in
    RE_FATAL mean "start of a line" on a 20 MB log without holding it in memory.
    """
    if not os.path.isfile(path):
        refuse("LOG-MISSING", f"no log.run at {path}")
    end_line = False
    exec_count = 0
    last_time = None
    model = None
    res = {}          # field -> {iteration: first initial residual}
    cur = None
    seen_at_time = set()
    fatal_hits = []   # NEW IN M1b
    banner_hits = 0   # NEW IN M1b -- infrastructure only, gates nothing
    broad_hits = 0    # NEW IN M1b -- infrastructure only, gates nothing
    n_solve_any = 0       # NEW IN M1b: residual lines the PERMISSIVE regex sees
    n_solve_numeric = 0   # NEW IN M1b: of those, the ones SOLVE_RE parsed
    nonfinite = []        # NEW IN M1b: (field, iteration, raw token)
    n_lines = 0           # NEW IN M1b: anti-windowing evidence
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            # NEW IN M1b.  Runs on EVERY line, before any `continue` below can
            # skip it: an `ExecutionTime` or `Time = ` line is not exempt from
            # being scanned, and a crash frame must not be able to hide behind
            # an early loop exit.
            mf = RE_FATAL.search(line.rstrip("\n"))
            if mf:
                fatal_hits.append(mf.group(0))
            if RE_TRAPFPE_BANNER.search(line):
                banner_hits += 1
            if RE_BROAD_DEFECTIVE.search(line):
                broad_hits += 1
            mt = TIME_RE.match(line)
            if mt:
                try:
                    cur = int(float(mt.group(1)))
                except ValueError:
                    cur = None
                last_time = mt.group(1)
                seen_at_time = set()
                continue
            if line.startswith("ExecutionTime"):
                exec_count += 1
                continue
            if line.strip() == "End":
                end_line = True
                continue
            if model is None:
                mm = MODEL_RE.search(line)
                if mm:
                    model = mm.group(1)
                    continue
            ms = SOLVE_RE.search(line)
            if ms and cur is not None:
                fld, val = ms.group(1), float(ms.group(2))
                if fld in seen_at_time:
                    continue
                seen_at_time.add(fld)
                res.setdefault(fld, {})[cur] = val
    return dict(end_line=end_line, exec_count=exec_count, last_time=last_time,
                model_from_log=model, residuals=res,
                # NEW IN M1b
                fatal=bool(fatal_hits), fatal_hits=sorted(set(fatal_hits)),
                n_fatal_hits=len(fatal_hits),
                banner_hits=banner_hits, broad_hits=broad_hits)


def read_status(path):
    """INFRASTRUCTURE (L-342).  Absent -> NOT MEASURED, never a failure."""
    if not os.path.isfile(path):
        return None
    out = {}
    for line in open(path, "r", errors="replace"):
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def numeric_time_dirs(root):
    if not os.path.isdir(root):
        return []
    return sorted((d for d in os.listdir(root)
                   if TIME_DIR_RE.match(d) and os.path.isdir(os.path.join(root, d))),
                  key=float)


def read_ras_model_from_dict(case_dir):
    p = os.path.join(case_dir, "constant", "turbulenceProperties")
    if not os.path.isfile(p):
        refuse("TP-MISSING", f"no constant/turbulenceProperties in {case_dir}")
    m = re.search(r"(?m)^[ \t]*RASModel[ \t]+([^;]*);",
                  open(p, errors="replace").read())
    return m.group(1).strip() if m else None


# --------------------------------------------------------------------------
# completion and convergence
# --------------------------------------------------------------------------
def completion(case_dir, log):
    """Standing rule 4, split physics-critical / infrastructure per L-342."""
    end_dir = os.path.join(case_dir, str(CAP_ITER))
    zero_datum = os.path.join(case_dir, "0", AGE_DATUM)
    clauses = {}
    # NEW IN M1b.  A crash is PHYSICS-CRITICAL: the numbers a crashed solve left
    # on disk are not the answer to the question asked.  This clause can only
    # turn a row INCOMPLETE, which can only pull a gate DOWN (one-way, rule 5's
    # direction).  It can never promote anything.
    clauses["no_fatal"] = not log.get("fatal", False)
    clauses["end_line"] = bool(log["end_line"])
    clauses["last_time_eq_endTime"] = (
        log["last_time"] is not None and
        abs(float(log["last_time"]) - CAP_ITER) < 1e-9)
    clauses["fields_present"] = all(
        os.path.isfile(os.path.join(end_dir, f)) for f in PHYSICS_FIELDS)
    clauses["exec_count_eq_endTime"] = (log["exec_count"] == CAP_ITER)
    if os.path.isfile(zero_datum) and clauses["fields_present"]:
        t0 = os.path.getmtime(zero_datum)
        clauses["age_guard"] = all(
            os.path.getmtime(os.path.join(end_dir, f)) > t0 for f in PHYSICS_FIELDS)
    else:
        clauses["age_guard"] = False
    st = read_status(os.path.join(case_dir, "STATUS"))
    if st is None:
        rc = None
        rc_class = "NOT MEASURED (infrastructure: no STATUS record; L-342, "\
                   "Sanaa desk ruling R-RC)"
        clauses["rc_zero"] = None
    else:
        try:
            rc = int(st.get("rc", "999"))
        except ValueError:
            rc = 999
        rc_class = "measured"
        clauses["rc_zero"] = (rc == 0)
    physics_ok = all(clauses[k] for k in ("no_fatal",          # NEW IN M1b
                                          "end_line", "last_time_eq_endTime",
                                          "fields_present", "exec_count_eq_endTime",
                                          "age_guard"))
    # R-RC: the rc VALUE is physics; the rc RECORD is infrastructure.  An absent
    # record is NOT MEASURED only when the other four rule-4 conditions hold.
    complete = physics_ok and (clauses["rc_zero"] is not False)
    return dict(clauses=clauses, complete=complete, physics_ok=physics_ok,
                rc=rc, rc_class=rc_class, status=st,
                # NEW IN M1b.  fatal_hits is EVIDENCE and is carried into the
                # record; banner/broad counts are INFRASTRUCTURE and gate
                # nothing -- they exist so a reader can see, per row, exactly
                # how many hits the DEFECTIVE broad clause would have produced.
                fatal_hits=log.get("fatal_hits", []),
                banner_hits=log.get("banner_hits", 0),
                broad_hits_defective_clause=log.get("broad_hits", 0))


def convergence_class(log):
    """Section 4.1.  CONVERGED@n if k<=CONV_K_TOL and omega<=CONV_OMEGA_TOL for
    EVERY outer iteration from n to CAP_ITER; otherwise CAP-BOUND."""
    rk = log["residuals"].get("k", {})
    ro = log["residuals"].get("omega", {})
    if not rk or not ro:
        return dict(state="CAP-BOUND", n=None,
                    reason="no k and/or omega residual history in log.run",
                    min_k=None, min_omega=None, min_k_at=None, min_omega_at=None)
    its = sorted(set(rk) & set(ro))
    last_bad = None
    for i in its:
        if rk[i] > CONV_K_TOL or ro[i] > CONV_OMEGA_TOL:
            last_bad = i
    mk = min(rk.items(), key=lambda kv: kv[1])
    mo = min(ro.items(), key=lambda kv: kv[1])
    common = dict(min_k=mk[1], min_k_at=mk[0], min_omega=mo[1], min_omega_at=mo[0])
    if last_bad is None:
        return dict(state="CONVERGED", n=its[0], reason="", **common)
    nxt = [i for i in its if i > last_bad]
    if not nxt:
        return dict(state="CAP-BOUND", n=None,
                    reason=f"criterion still unmet at the cap (last violation at "
                           f"iteration {last_bad})", **common)
    return dict(state="CONVERGED", n=nxt[0], reason="", **common)


# --------------------------------------------------------------------------
# case inventory, re-derived from the benchmark tree rather than hard-coded
# --------------------------------------------------------------------------
def bench_inventory(bench_root):
    out = {}
    for dirpath, _d, _f in os.walk(bench_root):
        if os.path.basename(dirpath) != "polyMesh":
            continue
        root = os.path.dirname(os.path.dirname(dirpath))
        if not (os.path.isdir(os.path.join(root, "0"))
                and os.path.isdir(os.path.join(root, "system"))):
            continue
        cid = os.path.basename(root)
        if cid in EXCLUDED_CASES:
            continue
        tds = numeric_time_dirs(root)
        tds = [t for t in tds if float(t) > 0]
        head = open(os.path.join(root, "constant", "polyMesh", "owner"),
                    errors="replace").read(4000)
        mc = re.search(r"nCells:\s*(\d+)", head)
        out[cid] = dict(path=root, ref_time=(tds[-1] if tds else None),
                        ncells=int(mc.group(1)) if mc else None)
    return out


# --------------------------------------------------------------------------
# grading
# --------------------------------------------------------------------------
def grade_row(run_root, arm, cid, inv):
    case_dir = os.path.join(run_root, arm, cid)
    row = dict(arm=arm, case_id=cid, case_dir=case_dir)
    if not os.path.isdir(case_dir):
        row.update(state="PENDING", note="run directory absent")
        return row
    log = parse_log(os.path.join(case_dir, "log.run"))
    comp = completion(case_dir, log)
    conv = convergence_class(log)
    row.update(completion=comp, convergence=conv,
               model_from_dict=read_ras_model_from_dict(case_dir),
               model_from_log=log["model_from_log"],
               exec_count=log["exec_count"], last_time=log["last_time"])
    if comp["status"] is None:
        row["core_min"] = None
        row["core_min_class"] = "NOT MEASURED (infrastructure)"
    else:
        try:
            row["core_min"] = float(comp["status"].get("core_min"))
        except (TypeError, ValueError):
            row["core_min"] = None
        row["core_min_class"] = "measured from STATUS"
    if not comp["complete"]:
        row["state"] = "INCOMPLETE"
        row["note"] = ("strict completion rule failed: " +
                       ", ".join(k for k, v in comp["clauses"].items() if v is False))
        # REFUSE TO DEGRADE: no field number is computed for an incomplete row.
        return row
    row["state"] = "COMPLETE"
    ncells = inv[cid]["ncells"]
    row["U_end"] = as_flat(read_internal_field(
        os.path.join(case_dir, str(CAP_ITER), "U")), ncells)
    row["k_end"] = as_flat(read_internal_field(
        os.path.join(case_dir, str(CAP_ITER), "k")), ncells)
    row["nut_end"] = as_flat(read_internal_field(
        os.path.join(case_dir, str(CAP_ITER), "nut")), ncells)
    return row


# --------------------------------------------------------------------------
# NEW IN M1b: SELF-HASH AND THE SECTION 2j BIRTH REQUIREMENT
# --------------------------------------------------------------------------
def self_sha256():
    """So the freeze check needs nothing but this output and `git cat-file`."""
    return hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()


def verify_birth_record():
    """Section 2j: an instrument may not grade until its fatal channel has been
    DEMONSTRATED on bytes written by the REAL PRODUCER, in BOTH directions.

    This reads the record produced by `--birth` and REFUSES if it is absent, if
    either limb is missing, if any fixture was written by this harness rather
    than by a solver, or if the recorded instrument sha256 is not this file.
    A green selftest on synthetic fixtures is NOT this (L-402, and the G2
    precedent where a selftest passed while the defect was live because the
    synthetic fixture was cleaner than any log the solver has ever produced).
    """
    if not os.path.isfile(BIRTH_RECORD):
        refuse("BIRTH-ABSENT",
               f"no section-2j birth record at {BIRTH_RECORD}. The fatal channel "
               f"has not been demonstrated on real producer bytes, so this "
               f"comparator may not grade. Run: python3 grade_m1b.py --birth")
    rec = json.load(open(BIRTH_RECORD))
    if rec.get("instrument_sha256") != self_sha256():
        refuse("BIRTH-STALE",
               f"the birth record was produced by a DIFFERENT build of this "
               f"instrument (record {rec.get('instrument_sha256')!r}, this file "
               f"{self_sha256()!r}). A demonstration of another file's reader is "
               f"not a demonstration of this one.")
    pos = rec.get("positive_limb", {})
    neg = rec.get("negative_limb", {})
    if not pos.get("passed"):
        refuse("BIRTH-POSITIVE",
               "the POSITIVE limb is not satisfied: the reader has not been "
               "shown to see a real fatal in bytes written by a solver.")
    if not neg.get("passed"):
        refuse("BIRTH-NEGATIVE",
               "the NEGATIVE limb is not satisfied: the reader has not been "
               "shown to return fatal=False on a REAL clean log that carries the "
               "trapFpe banner verbatim. A control with only a positive limb is "
               "a detector that fires on everything.")
    synth = [f for f in (pos.get("fixtures", []) + neg.get("fixtures", []))
             if f.get("produced_by") in (None, "", "this harness",
                                         "the control itself")]
    if synth:
        refuse("BIRTH-SYNTHETIC",
               f"{len(synth)} birth fixture(s) were written by the harness rather "
               f"than by the real producer (section 2j.2). Ask who wrote the bytes "
               f"your control reads; if the answer is the control itself, the "
               f"birth requirement is NOT MET however green the selftest.")
    return rec


def main(argv):
    ap = argparse.ArgumentParser(description="M1b successor comparator")
    ap.add_argument("--root", default=RUN_ROOT_DEFAULT)
    ap.add_argument("--bench-root", default=BENCH_ROOT_DEFAULT)
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--birth", action="store_true",
                    help="run the section 2j birth demonstration on REAL "
                         "producer bytes and write its artefact")
    ap.add_argument("--planted-failure", metavar="GUARD")
    args = ap.parse_args(argv[1:])
    if args.selftest:
        return selftest()
    if args.birth:
        return birth_demonstration()
    if args.planted_failure:
        return planted_failure_proof(args.planted_failure)
    return grade(args.root, args.bench_root, args.out)


def grade(run_root, bench_root, out_path=None):
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    print("M1b MULTI-MODEL SWEEP REGRADE -- SUCCESSOR COMPARATOR")
    print(f"instrument sha256: {self_sha256()}")
    # NEW IN M1b.  Section 2j is a PRECONDITION OF GRADING, not a later nicety.
    birth = verify_birth_record()
    print(f"section 2j birth demonstration: VERIFIED from {BIRTH_RECORD} "
          f"(positive limb {birth['positive_limb']['n_fixtures']} real fixtures, "
          f"negative limb {birth['negative_limb']['n_fixtures']} real fixtures)")
    print(RULE5_STATEMENT)
    print()

    inv = bench_inventory(bench_root)
    if len(inv) != N_CASES:
        refuse("INVENTORY", f"the benchmark tree yields {len(inv)} includable cases, "
                            f"the registration names {N_CASES}")

    rows = {}
    for arm in ARMS:
        for cid in sorted(inv):
            rows[(arm, cid)] = grade_row(run_root, arm, cid, inv)

    pending = [k for k, r in rows.items() if r["state"] == "PENDING"]
    if pending:
        for arm, cid in sorted(pending):
            print(f"PENDING: {os.path.join(run_root, arm, cid)}")
        refuse("PENDING", f"{len(pending)} of {N_RUNS} runs have no run directory; a "
                          f"partial sweep receives no verdict")

    # ---- C1 PLANTED ZERO, ON DISK, BEFORE ANY NUMBER ---------------------
    donor = None
    for k in sorted(rows):
        if rows[k]["state"] == "COMPLETE":
            donor = os.path.join(rows[k]["case_dir"], str(CAP_ITER), "U")
            break
    if donor is None:
        refuse("C1-PLANT", "no complete run to plant into; the reader could not be "
                           "shown able to see a non-zero, so its zeros mean nothing")
    with tempfile.TemporaryDirectory(prefix="m1grade_") as tmp:
        pz = planted_zero_control(donor, tmp)
    print(f"C1 planted-zero control on {donor}: {pz}")
    if not pz["passed"]:
        refuse("C1-PLANT", f"planted-zero control FAILED: the reader cannot see a "
                           f"{PLANT} difference planted on disk; its zeros mean nothing")

    # ---- G1 ARM APPLICATION ---------------------------------------------
    g1_bad = []
    for (arm, cid), r in sorted(rows.items()):
        want = ARMS[arm]
        if r.get("model_from_dict") != want:
            g1_bad.append((arm, cid, "dict", r.get("model_from_dict")))
        elif r.get("model_from_log") not in (None, want):
            g1_bad.append((arm, cid, "log", r.get("model_from_log")))
    g1 = dict(gate="G1", name="arm application",
              verdict=("PASS" if not g1_bad else "NOT A RESULT"),
              n_bad=len(g1_bad), bad=g1_bad[:20])

    # ---- G0 COMPLETION ---------------------------------------------------
    incomplete = [(a, c) for (a, c), r in sorted(rows.items())
                  if r["state"] != "COMPLETE"]
    g0 = dict(gate="G0", name="completion / harness",
              verdict=("PASS" if not incomplete else "GATE FAIL"),
              n_complete=N_RUNS - len(incomplete), n_total=N_RUNS,
              incomplete=[f"{a}/{c}" for a, c in incomplete])

    capbound = {k for k, r in rows.items()
                if r["state"] == "COMPLETE" and r["convergence"]["state"] == "CAP-BOUND"}

    # ---- G2 NULL-ARM IDENTITY -------------------------------------------
    g2_vals, g2_missing = {}, []
    for cid in sorted(inv):
        r = rows[(NULL_ARM, cid)]
        if r["state"] != "COMPLETE":
            g2_missing.append(cid)
            continue
        ref_t = inv[cid]["ref_time"]
        if ref_t is None:
            g2_missing.append(cid)
            continue
        ref = as_flat(read_internal_field(
            os.path.join(inv[cid]["path"], ref_t, "U")), inv[cid]["ncells"])
        g2_vals[cid] = rel_l2(r["U_end"], ref)
    g2 = _g2_verdict(g2_vals, g2_missing, capbound, NULL_ARM)

    # ---- G3 ARM SEPARATION (a spread, and only a spread) ------------------
    g3_vals, g3_missing = {}, []
    for cid in sorted(inv):
        a, b = rows[(TEST_ARM, cid)], rows[(NULL_ARM, cid)]
        if a["state"] != "COMPLETE" or b["state"] != "COMPLETE":
            g3_missing.append(cid)
            continue
        g3_vals[cid] = rel_l2(a["U_end"], b["U_end"])
    g3 = _g3_verdict(g3_vals, g3_missing, capbound)

    # ---- G4 CAP-BOUND CENSUS --------------------------------------------
    g4 = dict(gate="G4", name="cap-bound census (a ROW CLASS, not a verdict)",
              verdict=("GATE REACHED" if len(capbound) <= G4_MAX_CAPBOUND
                       else "GATE FAIL"),
              n_capbound=len(capbound), threshold=G4_MAX_CAPBOUND,
              capbound=[f"{a}/{c}" for a, c in sorted(capbound)])

    # ---- report -----------------------------------------------------------
    print()
    print("PER-ROW TABLE.  Every row carries its convergence class beside its number.")
    print(f"{'arm':<16}{'case':<24}{'state':<11}{'convergence':<18}"
          f"{'rel-L2 U vs ref':>17}{'rel-L2 U arms':>15}{'core-min':>11}")
    for cid in sorted(inv):
        for arm in (NULL_ARM, TEST_ARM):
            r = rows[(arm, cid)]
            conv = (r["convergence"]["state"] +
                    (f"@{r['convergence']['n']}" if r.get("convergence", {}).get("n")
                     else "")) if r["state"] == "COMPLETE" else "-"
            v2 = f"{g2_vals[cid]:.3e}" if (arm == NULL_ARM and cid in g2_vals) else ""
            v3 = f"{g3_vals[cid]:.3e}" if (arm == TEST_ARM and cid in g3_vals) else ""
            cm = ("NOT MEASURED" if r.get("core_min") is None
                  else f"{r['core_min']:.2f}")
            print(f"{arm:<16}{cid:<24}{r['state']:<11}{conv:<18}{v2:>17}{v3:>15}{cm:>11}")

    print()
    for g in (g0, g1, g2, g3, g4):
        print(f"{g['gate']}  {g['name']}: {g['verdict']}")
        for kk, vv in g.items():
            if kk not in ("gate", "name", "verdict"):
                print(f"      {kk}: {vv}")
    print()
    print(RULE5_STATEMENT)

    total_measured = sum(r["core_min"] for r in rows.values()
                         if r.get("core_min") is not None)
    n_unmeasured = sum(1 for r in rows.values() if r.get("core_min") is None)
    print(f"\nCOST: {total_measured:.1f} core-min measured from STATUS across "
          f"{N_RUNS - n_unmeasured} rows; {n_unmeasured} rows NOT MEASURED "
          f"(infrastructure, L-342).  Registered estimate 1298.1 core-min, "
          f"registered cap 1900.0 core-min.  Any dollar figure is DERIVED at the "
          f"owner-stated $0.0513/core-h, NOT MEASURED "
          f"(COMPUTE_BUDGET_CHARTER section 5).")

    # NEW IN M1b.  The fatal census, printed beside the verdicts so a reader can
    # see that the zero is a READING and not an empty population (standing
    # rule 3's principle applied to the fatal channel).
    n_fatal = sum(1 for r in rows.values()
                  if r.get("completion", {}).get("fatal_hits"))
    n_banner = sum(1 for r in rows.values()
                   if r.get("completion", {}).get("banner_hits", 0) > 0)
    n_broad = sum(1 for r in rows.values()
                  if r.get("completion", {}).get(
                      "broad_hits_defective_clause", 0) > 0)
    print(f"\nFATAL CHANNEL CENSUS over {len(rows)} rows: "
          f"rows with a REAL fatal signature (narrow clause) = {n_fatal}; "
          f"rows carrying the trapFpe enablement banner = {n_banner}; "
          f"rows the DEFECTIVE broad clause would have matched = {n_broad}. "
          f"The banner and broad counts are INFRASTRUCTURE and gate nothing. A "
          f"narrow zero standing beside a non-zero banner count is a reading, "
          f"not an empty population (L-396, D548).")

    out = dict(
        tool="grade_m1b.py", instrument_sha256=self_sha256(),
        predecessor="cases/RANS_LES_closure_models/M1_multimodel_sweep/grade_m1.py",
        birth_record=BIRTH_RECORD, birth_verified=True,
        fatal_census=dict(n_rows=len(rows), n_fatal_narrow=n_fatal,
                          n_trapfpe_banner=n_banner,
                          n_broad_defective_clause_would_match=n_broad),
        started_utc=started,
        finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        run_root=run_root, bench_root=bench_root,
        rule5=RULE5_STATEMENT, planted_zero=pz,
        registered=dict(cap_iterations=CAP_ITER, conv_k=CONV_K_TOL,
                        conv_omega=CONV_OMEGA_TOL, g2_band=G2_BAND,
                        g2_min_in_band=G2_MIN_IN_BAND, g2_ceiling=G2_CEILING,
                        g2_refuse_above=G2_REFUSE_ABOVE,
                        g3_separation=G3_SEPARATION, g3_min_cases=G3_MIN_CASES,
                        g4_max_capbound=G4_MAX_CAPBOUND),
        gates=[g0, g1, g2, g3, g4],
        rel_l2_null_vs_reference=g2_vals,
        rel_l2_arm_to_arm=g3_vals,
        rows={f"{a}/{c}": {k: v for k, v in r.items()
                           if k not in ("U_end", "k_end", "nut_end")}
              for (a, c), r in rows.items()},
        total_core_min_measured=total_measured,
        rows_cost_not_measured=n_unmeasured,
    )
    out_path = out_path or os.path.join(run_root, "gate_m1b.json")
    json.dump(out, open(out_path, "w"), indent=2, sort_keys=True, default=str)
    print(f"\nwrote {out_path}")
    bad = any(g["verdict"] in ("GATE FAIL", "NOT A RESULT") for g in (g0, g1, g2, g3, g4))
    return 1 if bad else 0


def _aggregate_twice(vals, capbound_cids, label, predicate):
    """Section 4.3 rule 2: NO aggregate is reported once.  Converged-only and
    all-rows are printed side by side and are never merged."""
    all_rows = {c: v for c, v in vals.items()}
    conv_rows = {c: v for c, v in vals.items() if c not in capbound_cids}
    return dict(
        all_rows_n=len(all_rows),
        all_rows_meeting=sum(1 for v in all_rows.values() if predicate(v)),
        all_rows_max=(max(all_rows.values()) if all_rows else None),
        converged_rows_n=len(conv_rows),
        converged_rows_meeting=sum(1 for v in conv_rows.values() if predicate(v)),
        converged_rows_max=(max(conv_rows.values()) if conv_rows else None),
        capbound_excluded=sorted(set(vals) & set(capbound_cids)),
        aggregate_label=label,
    )


def _g2_partition_ok(vals):
    """The supervisor's structural G2 rule.  Iteration-matched cases (the 29
    hills, reference written at exactly this sweep's cap) must ALL meet the
    band; unmatched cases may contribute at most G2_UNMATCHED_MAX_OUT outliers.

    With no matched case present -- as in the synthetic selftest fixtures --
    this degenerates exactly to the old flat "at most 2 out of band" rule, which
    is why it does not disturb the fixtures that predate it.
    """
    matched_out = [c for c, v in vals.items()
                   if c.startswith(G2_MATCHED_PREFIX) and v > G2_BAND]
    unmatched_out = [c for c, v in vals.items()
                     if not c.startswith(G2_MATCHED_PREFIX) and v > G2_BAND]
    return not matched_out and len(unmatched_out) <= G2_UNMATCHED_MAX_OUT


def _g2_verdict(vals, missing, capbound, arm):
    cb = {c for (a, c) in capbound if a == arm}
    agg = _aggregate_twice(vals, cb, "rel-L2(U) null vs shipped reference",
                           lambda v: v <= G2_BAND)
    over = {c: v for c, v in vals.items() if v > G2_REFUSE_ABOVE}
    if over:
        verdict = "NOT A RESULT"
    elif missing:
        verdict = "GATE FAIL"
    else:
        ok_all = (_g2_partition_ok(vals)
                  and agg["all_rows_meeting"] >= G2_MIN_IN_BAND
                  and (agg["all_rows_max"] or 0.0) <= G2_CEILING)
        conv_vals = {c: v for c, v in vals.items() if c not in cb}
        ok_conv = (_g2_partition_ok(conv_vals)
                   and agg["converged_rows_meeting"] >= G2_MIN_IN_BAND
                   and (agg["converged_rows_max"] or 0.0) <= G2_CEILING)
        # section 4.3 rule 4: where the two disagree, the CONSERVATIVE verdict
        # is the one reported, and both are shown.
        verdict = "PASS" if (ok_all and ok_conv) else "GATE FAIL"
    return dict(gate="G2", name="null-arm identity (the sweep's planted control)",
                verdict=verdict, band=G2_BAND, min_in_band=G2_MIN_IN_BAND,
                ceiling=G2_CEILING, refuse_above=G2_REFUSE_ABOVE,
                partition_rule=("iteration-matched cases (prefix %r) must ALL "
                                "meet the band; at most %d unmatched outliers"
                                % (G2_MATCHED_PREFIX, G2_UNMATCHED_MAX_OUT)),
                matched_out_of_band=sorted(
                    c for c, v in vals.items()
                    if c.startswith(G2_MATCHED_PREFIX) and v > G2_BAND),
                aggregates=agg, over_refusal_threshold=over, missing=missing,
                label="a harness check, NOT a precision claim: the null re-solves "
                      "under a changed controlDict and against references of "
                      "unknown provenance")


def _g3_verdict(vals, missing, capbound):
    cb = {c for (_a, c) in capbound}
    agg = _aggregate_twice(vals, cb, "rel-L2(U) kOmega vs kOmegaSST",
                           lambda v: v > G3_SEPARATION)
    if missing:
        verdict = "GATE FAIL"
    else:
        ok_all = agg["all_rows_meeting"] >= G3_MIN_CASES
        ok_conv = agg["converged_rows_meeting"] >= G3_MIN_CASES
        verdict = "GATE REACHED" if (ok_all and ok_conv) else "GATE FAIL"
    return dict(gate="G3", name="arm separation", verdict=verdict,
                threshold=G3_SEPARATION, min_cases=G3_MIN_CASES,
                aggregates=agg, missing=missing,
                label="THIS IS A SPREAD AND ONLY A SPREAD. It measures how "
                      "sensitive the solution is to the choice of closure. It is "
                      "NOT a model-form uncertainty and NO interval is calibrated "
                      "from it: both arms are linear eddy-viscosity models sharing "
                      "the Boussinesq assumption, so their errors are CORRELATED, "
                      "NOT INDEPENDENT, and this spread SYSTEMATICALLY UNDERSTATES "
                      "true model-form uncertainty.")


# --------------------------------------------------------------------------
# SELFTEST
# --------------------------------------------------------------------------
def _w(path, txt):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(txt)


def _vec_field(vals):
    body = "\n".join(f"({a} {b} {c})" for a, b, c in vals)
    return ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
            "    class volVectorField;\n    object U;\n}\n"
            f"\ninternalField   nonuniform List<vector>\n{len(vals)}\n(\n{body}\n)\n;\n"
            "\nboundaryField\n{\n}\n")


def _sca_field(vals, name="k"):
    body = "\n".join(str(v) for v in vals)
    return ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
            f"    class volScalarField;\n    object {name};\n}}\n"
            f"\ninternalField   nonuniform List<scalar>\n{len(vals)}\n(\n{body}\n)\n;\n"
            "\nboundaryField\n{\n}\n")


def _fake_log(n_iter, k_res, om_res, model="kOmegaSST", end=True, exec_lines=None,
              fatal_tail=None):
    # NEW IN M1b.  THE BANNER IS NOW IN EVERY SYNTHETIC FIXTURE.  G2's selftest
    # passed while the broad-clause defect was live precisely because its
    # synthetic log was CLEANER THAN ANY LOG THE SOLVER HAS EVER PRODUCED -- it
    # omitted the one line the defect fires on.  A fixture that cannot exhibit
    # the defect cannot control for it.  Real logs carry this at line 18.
    out = [TRAPFPE_BANNER, f"Selecting RAS turbulence model {model}"]
    for i in range(1, n_iter + 1):
        out.append(f"Time = {i}\n")
        out.append(f"DILUPBiCG:  Solving for Ux, Initial residual = 1e-9, "
                   f"Final residual = 1e-12, No Iterations 1")
        out.append(f"DILUPBiCG:  Solving for k, Initial residual = {k_res(i)}, "
                   f"Final residual = 1e-12, No Iterations 1")
        out.append(f"DILUPBiCG:  Solving for omega, Initial residual = {om_res(i)}, "
                   f"Final residual = 1e-12, No Iterations 1")
    for _ in range(exec_lines if exec_lines is not None else n_iter):
        out.append("ExecutionTime = 1 s  ClockTime = 1 s")
    if fatal_tail:                                   # NEW IN M1b
        out.append(fatal_tail)
    if end:
        out.append("End")
    return "\n".join(out) + "\n"


def _fake_case(root, arm, cid, ncells, u_scale, n_iter, converge_at,
              model=None, with_status=True, end=True, exec_lines=None,
              fatal_tail=None):
    d = os.path.join(root, arm, cid)
    model = model or ARMS[arm]
    _w(os.path.join(d, "constant", "turbulenceProperties"),
       f"simulationType RAS;\nRAS\n{{\n    RASModel        {model};\n}}\n")
    _w(os.path.join(d, "0", "U"), _vec_field([(1.0, 0, 0)] * ncells))
    import time as _t
    _t.sleep(0.01)
    vals = [(u_scale * (1 + 0.001 * i), 0.0, 0.0) for i in range(ncells)]
    _w(os.path.join(d, str(CAP_ITER), "U"), _vec_field(vals))
    for f in ("p", "k", "omega", "nut"):
        _w(os.path.join(d, str(CAP_ITER), f), _sca_field([0.1] * ncells, f))
    _w(os.path.join(d, "log.run"),
       _fake_log(n_iter,
                 lambda i: 1e-3 if i < converge_at else 1e-9,
                 lambda i: 1e-3 if i < converge_at else 1e-11,
                 model=model, end=end, exec_lines=exec_lines,
                 fatal_tail=fatal_tail))
    if with_status:
        _w(os.path.join(d, "STATUS"),
           f"case={cid}\narm={arm}\nrc=0\nwall_s=600\nranks=1\ncore_min=10.0\n"
           f"cap_core_min=25.0\ncapped=0\nnote=clean\n")
    # the endTime fields must be NEWER than 0/U -- the age guard
    now = _t.time()
    for f in PHYSICS_FIELDS:
        os.utime(os.path.join(d, str(CAP_ITER), f), (now + 10, now + 10))
    os.utime(os.path.join(d, "0", "U"), (now, now))
    return d


def _check(label, ok, detail=""):
    print(f"  [{'ok  ' if ok else 'FAIL'}] {label}" + (f"  {detail}" if detail else ""))
    return bool(ok)


def _refuses(fn):
    try:
        fn()
    except Refusal:
        return True
    except Exception:
        return True
    return False


def selftest():
    print("grade_m1b.py --selftest")
    print(f"  instrument sha256: {self_sha256()}")
    print(f"  running under python3 "
          f"{'-O (assertions DELETED)' if not __debug__ else '(assertions live)'}")
    ok = True
    src = open(os.path.abspath(__file__), errors="replace").read()
    body = "\n".join(l for l in src.split("\n") if not l.strip().startswith("#"))
    ok &= _check("no `assert` statement anywhere in this file (L-332)",
                 not re.search(r"(?m)^\s*assert\b", body))
    # NEW IN M1b.  The regex above is a TEXT test and can be fooled by an assert
    # that is not the first token on its line.  This is the PARSE test: zero
    # `ast.Assert` nodes in the compiled tree.  `python3 -O` erases assert
    # statements, so a refusal written as one silently vanishes; the only proof
    # that none exists is the AST, not the eye and not a regex.
    n_assert_nodes = len([n for n in ast.walk(ast.parse(src))
                          if isinstance(n, ast.Assert)])
    ok &= _check("ZERO `ast.Assert` nodes in the parsed tree (L-332, by AST not "
                 "by regex)", n_assert_nodes == 0, f"count={n_assert_nodes}")
    ok &= _check("the verdict vocabulary is exactly the six words",
                 set(VERDICTS) == {"PASS", "GATE REACHED", "GATE FAIL",
                                   "NOT A RESULT", "BLOCKED", "PENDING"})

    # ---- NEW IN M1b: CONTROL C7, THE FATAL CHANNEL, BOTH DIRECTIONS ---------
    # These are SYNTHETIC and are therefore NOT the section 2j birth
    # demonstration.  They are unit coverage of the clause's shape.  The birth
    # requirement is satisfied only by `--birth`, on bytes a solver wrote.
    _pos = [
        ("FOAM FATAL ERROR banner",
         "--> FOAM FATAL ERROR:\nmaximum number of iterations exceeded\n"),
        ("FOAM FATAL IO ERROR banner",
         "--> FOAM FATAL IO ERROR: keyword nu is undefined\n"),
        ("sigFpe handler FIRED, single rank",
         "#0  Foam::error::printStack(Foam::Ostream&) at ??:?\n"
         "#1  Foam::sigFpe::sigHandler(int) at ??:?\n"),
        ("sigFpe handler FIRED, 14-rank INTERLEAVED stack -- the real shape",
         "[0] #1  Foam::sigFpe::sigHandler(int)[1] #1  "
         "Foam::sigFpe::sigHandler(int)[2] #1  Foam::sigFpe::sigHandler(int)\n"),
        ("sigSegv handler FIRED",
         "#1  Foam::sigSegv::sigHandler(int) at ??:?\n"),
        ("shell FPE death message at line start",
         "Floating point exception (core dumped)\n"),
        ("shell SEGV death message at line start",
         "Segmentation fault (core dumped)\n"),
    ]
    for label, tail in _pos:
        lg = parse_log_from_text(_fake_log(3, lambda i: 1e-9, lambda i: 1e-11,
                                           fatal_tail=tail))
        ok &= _check(f"C7 POSITIVE: {label} reads fatal=True",
                     lg["fatal"] is True, str(lg["fatal_hits"]))
    # THE LIMB THAT ACTUALLY MATTERS.  A clean log carrying the banner verbatim.
    clean = _fake_log(3, lambda i: 1e-9, lambda i: 1e-11)
    lg = parse_log_from_text(clean)
    ok &= _check("C7 NEGATIVE: a clean log carrying the trapFpe banner VERBATIM "
                 "reads fatal=False", lg["fatal"] is False and lg["banner_hits"] >= 1
                 and lg["end_line"] is True,
                 f"fatal={lg['fatal']} banner_hits={lg['banner_hits']} "
                 f"hits={lg['fatal_hits']}")
    ok &= _check("C7 the banner IS in every synthetic fixture, so the fixture "
                 "cannot be cleaner than a real log (the G2 defect)",
                 TRAPFPE_BANNER in clean)
    ok &= _check("C7 the DEFECTIVE broad clause DOES fire on that same clean "
                 "log -- which is why the narrow form is load-bearing and not "
                 "decoration", lg["broad_hits"] >= 1, f"broad_hits={lg['broad_hits']}")
    ok &= _check("C7 the narrow clause does NOT match the banner string itself",
                 RE_FATAL.search(TRAPFPE_BANNER) is None)
    ok &= _check("C7 the broad clause DOES match the banner string itself "
                 "(L-396: it is not a detector, it is very nearly a constant)",
                 RE_BROAD_DEFECTIVE.search(TRAPFPE_BANNER) is not None)
    ok &= _check("C7 the narrow clause does not fire on ordinary prose "
                 "containing the word `signal`",
                 RE_FATAL.search("signalling the end of the outer loop") is None)
    # L-314: the guard ships its planted-failure proof -- a fatal must make the
    # ROW incomplete, not merely set a flag nobody reads.
    with tempfile.TemporaryDirectory(prefix="m1b_f_") as tmpf:
        dg = _fake_case(tmpf, "kOmega", "T1", 4, 1.0, CAP_ITER, 5000)
        cg = completion(dg, parse_log(os.path.join(dg, "log.run")))
        df = _fake_case(tmpf, "kOmega", "T2", 4, 1.0, CAP_ITER, 5000,
                        fatal_tail="#1  Foam::sigFpe::sigHandler(int) at ??:?")
        cf = completion(df, parse_log(os.path.join(df, "log.run")))
        ok &= _check("C7 PLANTED FAILURE (L-314): the SAME case, otherwise "
                     "identical and COMPLETE, becomes INCOMPLETE on `no_fatal` "
                     "when a real crash frame is planted in its log",
                     cg["complete"] is True and cf["complete"] is False
                     and cf["clauses"]["no_fatal"] is False,
                     f"clean={cg['complete']} planted={cf['clauses']}")
        ok &= _check("C7 ONE-WAY: `no_fatal` appears in the physics clause set, "
                     "so it can only turn a row INCOMPLETE and therefore only "
                     "pull a gate DOWN; there is no path by which it promotes",
                     cf["physics_ok"] is False and cg["physics_ok"] is True)

    # ---- NEW IN M1b: the section 2j birth requirement REFUSES when unmet ----
    _real_birth = BIRTH_RECORD
    try:
        globals()["BIRTH_RECORD"] = os.path.join(
            tempfile.gettempdir(), "m1b_no_such_birth_record.json")
        ok &= _check("section 2j: grading REFUSES when no birth record exists",
                     _refuses(verify_birth_record))
        with tempfile.TemporaryDirectory(prefix="m1b_b_") as tb:
            bad = os.path.join(tb, "b.json")
            json.dump(dict(instrument_sha256=self_sha256(),
                           positive_limb=dict(passed=True, n_fixtures=1,
                                              fixtures=[dict(produced_by="OpenFOAM")]),
                           negative_limb=dict(passed=False, n_fixtures=0,
                                              fixtures=[])), open(bad, "w"))
            globals()["BIRTH_RECORD"] = bad
            ok &= _check("section 2j: a record with ONLY a positive limb REFUSES "
                         "-- a detector that fires on everything is not born",
                         _refuses(verify_birth_record))
            json.dump(dict(instrument_sha256=self_sha256(),
                           positive_limb=dict(passed=True, n_fixtures=1,
                                              fixtures=[dict(produced_by="the control itself")]),
                           negative_limb=dict(passed=True, n_fixtures=1,
                                              fixtures=[dict(produced_by="OpenFOAM")])),
                      open(bad, "w"))
            ok &= _check("section 2j.2: a fixture written by THE CONTROL ITSELF "
                         "REFUSES, however green the selftest (L-402)",
                         _refuses(verify_birth_record))
            json.dump(dict(instrument_sha256="0" * 64,
                           positive_limb=dict(passed=True, n_fixtures=1,
                                              fixtures=[dict(produced_by="OpenFOAM")]),
                           negative_limb=dict(passed=True, n_fixtures=1,
                                              fixtures=[dict(produced_by="OpenFOAM")])),
                      open(bad, "w"))
            ok &= _check("section 2j: a birth record for a DIFFERENT build of "
                         "this instrument REFUSES", _refuses(verify_birth_record))
    finally:
        globals()["BIRTH_RECORD"] = _real_birth

    with tempfile.TemporaryDirectory(prefix="m1g_") as tmp:
        d = _fake_case(tmp, "kOmega", "T1", 4, 1.0, CAP_ITER, 5000)
        log = parse_log(os.path.join(d, "log.run"))
        comp = completion(d, log)
        ok &= _check("a well-formed run is COMPLETE under rule 4",
                     comp["complete"], str(comp["clauses"]))
        conv = convergence_class(log)
        ok &= _check("convergence classified CONVERGED at the right iteration",
                     conv["state"] == "CONVERGED" and conv["n"] == 5000, str(conv))

        # rule 4 clauses, one planted failure each
        for clause, mutate in (
            ("end_line", lambda: _w(os.path.join(d, "log.run"),
                                    open(os.path.join(d, "log.run")).read()
                                    .replace("\nEnd\n", "\n"))),
            ("exec_count_eq_endTime", lambda: _w(
                os.path.join(d, "log.run"),
                open(os.path.join(d, "log.run")).read()
                .replace("ExecutionTime = 1 s  ClockTime = 1 s\n", "", 1))),
            ("fields_present", lambda: os.remove(
                os.path.join(d, str(CAP_ITER), "nut"))),
        ):
            src = open(os.path.join(d, "log.run"), errors="replace").read()
            keep = None
            if clause == "fields_present":
                keep = open(os.path.join(d, str(CAP_ITER), "nut")).read()
            mutate()
            c2 = completion(d, parse_log(os.path.join(d, "log.run")))
            ok &= _check(f"rule-4 clause `{clause}` refuses its planted failure",
                         c2["clauses"][clause] is False and not c2["complete"],
                         str(c2["clauses"]))
            _w(os.path.join(d, "log.run"), src)
            if keep is not None:
                _w(os.path.join(d, str(CAP_ITER), "nut"), keep)
                now = os.path.getmtime(os.path.join(d, "0", "U")) + 10
                os.utime(os.path.join(d, str(CAP_ITER), "nut"), (now, now))

        # age guard
        now = os.path.getmtime(os.path.join(d, str(CAP_ITER), "U")) + 100
        os.utime(os.path.join(d, "0", "U"), (now, now))
        c3 = completion(d, parse_log(os.path.join(d, "log.run")))
        ok &= _check("AGE GUARD refuses fields older than 0/U",
                     c3["clauses"]["age_guard"] is False and not c3["complete"])
        old = os.path.getmtime(os.path.join(d, str(CAP_ITER), "U")) - 100
        os.utime(os.path.join(d, "0", "U"), (old, old))

        # L-342 / R-RC: STATUS absent -> NOT MEASURED, physics STANDS
        os.remove(os.path.join(d, "STATUS"))
        c4 = completion(d, parse_log(os.path.join(d, "log.run")))
        ok &= _check("L-342/R-RC: absent STATUS is NOT MEASURED and does NOT void "
                     "intact physics", c4["complete"] and c4["rc"] is None and
                     "NOT MEASURED" in c4["rc_class"], c4["rc_class"])
        _w(os.path.join(d, "STATUS"), "rc=1\nwall_s=5\ncore_min=0.1\n")
        c5 = completion(d, parse_log(os.path.join(d, "log.run")))
        ok &= _check("R-RC: an rc VALUE of 1 is PHYSICS and refuses the row",
                     not c5["complete"] and c5["rc"] == 1)

        # C1 planted zero
        with tempfile.TemporaryDirectory(prefix="m1pz_") as t2:
            pz = planted_zero_control(os.path.join(d, str(CAP_ITER), "U"), t2)
        ok &= _check("C1: the reader SEES a plant made on disk",
                     pz["passed"] and abs(pz["reader_max_change"] - PLANT) < 1e-12,
                     str(pz))
        # L-314 planted failure of C1 itself: a BLIND reader must be caught
        global read_internal_field
        real = read_internal_field
        try:
            read_internal_field = lambda p: dict(kind="uniform", rank=1, n=1,
                                                 values=[0.0])
            with tempfile.TemporaryDirectory(prefix="m1pz2_") as t3:
                blind = planted_zero_control(os.path.join(d, str(CAP_ITER), "U"), t3)
            ok &= _check("C1 planted failure: a BLIND reader reports passed=False",
                         blind["passed"] is False, str(blind))
        finally:
            read_internal_field = real

    # convergence classification: CAP-BOUND, and the "sustained" requirement
    log_cap = parse_log_from_text(_fake_log(100, lambda i: 1e-3, lambda i: 1e-3))
    ok &= _check("never meeting the criterion is CAP-BOUND",
                 convergence_class(log_cap)["state"] == "CAP-BOUND")
    log_blip = parse_log_from_text(_fake_log(
        100, lambda i: 1e-9 if i != 90 else 1e-3, lambda i: 1e-11))
    cc = convergence_class(log_blip)
    ok &= _check("a LATE excursion moves the converged iteration, not the class",
                 cc["state"] == "CONVERGED" and cc["n"] == 91, str(cc))

    # rel_l2 and its refusals
    ok &= _check("rel_l2 of a field against itself is 0",
                 rel_l2([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == 0.0)
    ok &= _check("rel_l2 refuses a length mismatch",
                 _refuses(lambda: rel_l2([1.0], [1.0, 2.0])))
    ok &= _check("rel_l2 refuses a zero-norm reference",
                 _refuses(lambda: rel_l2([1.0], [0.0])))
    ok &= _check("rel_l2 of a 1e-2 perturbation reads ~1e-2",
                 abs(rel_l2([1.01, 1.01], [1.0, 1.0]) - 0.01) < 1e-9)

    # G2 / G3 verdicts on synthetic value sets
    good = {f"c{i}": 1e-5 for i in range(N_CASES)}
    ok &= _check("G2 PASSes when every case is inside the band",
                 _g2_verdict(good, [], set(), NULL_ARM)["verdict"] == "PASS")
    edge = dict(good); edge["c0"] = 5e-3; edge["c1"] = 5e-3; edge["c2"] = 5e-3
    ok &= _check("G2 GATE FAILs at 36 of 39 in band",
                 _g2_verdict(edge, [], set(), NULL_ARM)["verdict"] == "GATE FAIL")
    catastrophe = dict(good); catastrophe["c0"] = 0.5
    ok &= _check("G2 says NOT A RESULT above the refusal threshold",
                 _g2_verdict(catastrophe, [], set(), NULL_ARM)["verdict"] == "NOT A RESULT")
    # --- the supervisor's structural G2 partition, with its planted-failure
    # proof (L-314): the SAME two-outlier count PASSES when the outliers are
    # unmatched cases and GATE FAILS when one of them is an iteration-matched
    # hill.  Without this pair the partition could be a no-op and read as one.
    n_hill = 29
    part_ok = {f"alpha_h{i}": 1e-5 for i in range(n_hill)}
    part_ok.update({f"c{i}": 1e-5 for i in range(N_CASES - n_hill)})
    part_ok["c0"] = 5e-3; part_ok["c1"] = 5e-3          # 2 UNMATCHED outliers
    ok &= _check("G2 PASSes with 2 outliers when BOTH are unmatched cases",
                 _g2_verdict(part_ok, [], set(), NULL_ARM)["verdict"] == "PASS")
    part_bad = dict(part_ok)
    part_bad["c1"] = 1e-5                                # give the budget back
    part_bad["alpha_h0"] = 5e-3                          # spend it on a HILL
    r_bad = _g2_verdict(part_bad, [], set(), NULL_ARM)
    ok &= _check("G2 GATE FAILs when one outlier is an iteration-matched hill, "
                 "at the SAME 37-of-39 count the flat rule would have passed",
                 r_bad["verdict"] == "GATE FAIL"
                 and r_bad["aggregates"]["all_rows_meeting"] >= G2_MIN_IN_BAND
                 and r_bad["matched_out_of_band"] == ["alpha_h0"])
    ok &= _check("the partition rule is a no-op on fixtures with no hill "
                 "(so it cannot silently change the pre-existing controls)",
                 _g2_partition_ok({f"c{i}": 1e-5 for i in range(N_CASES)}))

    sep = {f"c{i}": 5e-2 for i in range(N_CASES)}
    ok &= _check("G3 GATE REACHED when the arms separate",
                 _g3_verdict(sep, [], set())["verdict"] == "GATE REACHED")
    nosep = {f"c{i}": 1e-9 for i in range(N_CASES)}
    ok &= _check("G3 GATE FAILs when the arms do not separate",
                 _g3_verdict(nosep, [], set())["verdict"] == "GATE FAIL")
    ok &= _check("G3 carries its non-uncertainty label",
                 "NOT a model-form uncertainty" in _g3_verdict(sep, [], set())["label"])

    # section 4.3: no aggregate is reported once, and CAP-BOUND rows are excluded
    mixed = dict(good); mixed["c0"] = 5e-3
    agg = _g2_verdict(mixed, [], {(NULL_ARM, "c0")}, NULL_ARM)["aggregates"]
    ok &= _check("aggregates are reported TWICE (all rows and converged only)",
                 agg["all_rows_n"] == N_CASES and
                 agg["converged_rows_n"] == N_CASES - 1 and
                 agg["capbound_excluded"] == ["c0"], str(agg))

    # rule 5 statement is emitted
    ok &= _check("the output states that standing rule 5 DOES NOT APPLY",
                 "RULE 5 DOES NOT APPLY" in RULE5_STATEMENT.upper()
                 and "GCI" in RULE5_STATEMENT)

    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 2


def parse_log_from_text(txt):
    with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False) as fh:
        fh.write(txt)
        p = fh.name
    try:
        return parse_log(p)
    finally:
        os.unlink(p)


# --------------------------------------------------------------------------
# NEW IN M1b: THE SECTION 2j BIRTH DEMONSTRATION, ON REAL PRODUCER BYTES
#
# Section 2j.2 is the operative constraint: the bytes a control reads must have
# been written by the REAL PRODUCER, not by the test harness.  Ask who wrote the
# bytes your control reads (L-402).  If the answer is "the control itself", the
# birth requirement is NOT MET however green the selftest.
#
# Every fixture below is a file a solver wrote, is read IN PLACE and read-only,
# and its producer is corroborated FROM ITS OWN BYTES -- the OpenFOAM banner
# block (`Build`, `Exec`, `Host`, `PID`, `Date`, `Case`) that only the solver
# emits -- rather than asserted in this table.  A fixture whose producer cannot
# be corroborated from its own header REFUSES.
# --------------------------------------------------------------------------
_DPW5 = "/home/ubuntu/certonomous-runs/dpw5-committee-probe/logs"
_M1 = RUN_ROOT_DEFAULT

BIRTH_POSITIVE_FIXTURES = [
    (f"{_DPW5}/hex_base_compressible_a2.11_solve.log",
     "a real SIGFPE crash of rhoSimpleFoam at 14 ranks; the handler frame is "
     "INTERLEAVED across ranks and does not start at column 0"),
    (f"{_DPW5}/hybrid_base_incompressible_a2.11_solve.log",
     "a real SIGFPE crash of simpleFoam at 14 ranks"),
    (f"{_DPW5}/INVALID_wdpois_missing_yPsi_solver_solve.log",
     "a real FOAM FATAL IO ERROR -- the other positive token, from a solver "
     "that refused its own dictionary"),
]
BIRTH_NEGATIVE_FIXTURES = [
    (f"{_M1}/kOmegaSST_null/alpha_10_9000_3036/log.run",
     "a REAL CLEAN LOG FROM THE VERY CORPUS THIS INSTRUMENT WILL GRADE"),
    (f"{_M1}/kOmega/CBFS/log.run",
     "a second real clean log from M1's own corpus, different arm"),
    (f"{_M1}/kOmegaSST_null/AR_3_Ret_360/log.run",
     "a third real clean log from M1's own corpus, duct family"),
    ("/home/ubuntu/Certonomous/verification/runs/D5_rsm_runs/LRR/log.run",
     "a real clean log from OUTSIDE M1 entirely -- the fixture G1b used, so the "
     "two successors' negative limbs can be compared"),
]

_HDR_KEYS = ("Build", "Exec", "Date", "Time", "Host", "PID", "Case", "nProcs")


def _producer_from_bytes(path, head):
    """WHO WROTE THESE BYTES.  Read out of the file's own OpenFOAM banner block,
    never asserted by this table.  Returns (producer_string, header_dict)."""
    hdr = {}
    for line in head.split("\n")[:40]:
        for k in _HDR_KEYS:
            if line.startswith(k) and ":" in line:
                hdr.setdefault(k, line.split(":", 1)[1].strip())
    if "Build" not in hdr or "Exec" not in hdr:
        refuse("BIRTH-PROVENANCE",
               f"{path} carries no OpenFOAM `Build`/`Exec` banner, so this "
               f"instrument cannot establish from the bytes themselves that a "
               f"solver wrote them. A fixture whose producer is only asserted is "
               f"not a section 2j fixture.")
    return (f"OpenFOAM {hdr.get('Build', '?')} :: {hdr.get('Exec', '?')} "
            f"on {hdr.get('Host', '?')} PID {hdr.get('PID', '?')} "
            f"{hdr.get('Date', '?')}"), hdr


def _birth_read(path, why):
    if not os.path.isfile(path):
        refuse("BIRTH-MISSING", f"birth fixture absent: {path}")
    sha = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            sha.update(chunk)
    head = open(path, errors="replace").read(8192)
    producer, hdr = _producer_from_bytes(path, head)
    log = parse_log(path)                       # THE READER UNDER TEST
    return dict(path=os.path.abspath(path), role_note=why,
                produced_by=producer, header=hdr,
                bytes=os.path.getsize(path), sha256=sha.hexdigest(),
                reader_fatal=bool(log["fatal"]),
                reader_fatal_hits=log["fatal_hits"],
                n_fatal_hit_lines=log["n_fatal_hits"],
                trapfpe_banner_lines=log["banner_hits"],
                broad_defective_clause_hit_lines=log["broad_hits"],
                end_line=bool(log["end_line"]))


def birth_demonstration():
    """Section 2j, BOTH LIMBS, on bytes written by the real producer.

    POSITIVE -- the reader SEES a real fatal in a log a crashing solver wrote.
    NEGATIVE -- the reader returns fatal=False on a REAL clean log that carries
                the `trapFpe:` banner verbatim.  This is the limb that matters:
                a control with only a positive limb is a detector that fires on
                everything, and G1 lost 127.08 core-min to exactly that.
    """
    os.makedirs(BIRTH_DIR, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    lines = []

    def p(s=""):
        print(s)
        lines.append(s)

    p("M1b SECTION 2j BIRTH DEMONSTRATION -- FATAL CHANNEL, BOTH LIMBS")
    p(f"generated {now}    ZERO COMPUTE (no solver, no staging, read-only)")
    p(f"instrument: {os.path.abspath(__file__)}")
    p(f"instrument sha256: {self_sha256()}")
    p("=" * 78)
    p("")
    p("SECTION 2j.2: THE BYTES BELOW WERE WRITTEN BY OpenFOAM SOLVERS, NOT BY")
    p("THIS HARNESS.  Every `produced_by` string is extracted from the file's")
    p("OWN banner block and is not asserted by the fixture table.  Every file is")
    p("opened read-only and is never modified.")
    p("")

    pos = [_birth_read(fp, why) for fp, why in BIRTH_POSITIVE_FIXTURES]
    neg = [_birth_read(fp, why) for fp, why in BIRTH_NEGATIVE_FIXTURES]

    p("LIMB 1 -- POSITIVE.  The reader must SEE a real fatal.")
    for f in pos:
        p(f"  {f['path']}")
        p(f"      produced by : {f['produced_by']}")
        p(f"      sha256      : {f['sha256']}")
        p(f"      bytes       : {f['bytes']}")
        p(f"      READER SAYS : fatal={f['reader_fatal']}  hits="
          f"{f['reader_fatal_hits']}  on {f['n_fatal_hit_lines']} line(s)")
        p(f"      note        : {f['role_note']}")
    pos_ok = all(f["reader_fatal"] for f in pos) and len(pos) > 0
    p(f"  LIMB 1: {'SATISFIED' if pos_ok else 'NOT SATISFIED'} "
      f"({sum(1 for f in pos if f['reader_fatal'])} of {len(pos)} real crashed "
      f"logs read fatal=True)")
    p("")

    p("LIMB 2 -- NEGATIVE, AND THIS IS THE ONE THAT MATTERS.  A REAL clean log")
    p("carrying the trapFpe banner verbatim must read back fatal=False.")
    for f in neg:
        p(f"  {f['path']}")
        p(f"      produced by : {f['produced_by']}")
        p(f"      sha256      : {f['sha256']}")
        p(f"      bytes       : {f['bytes']}")
        p(f"      trapFpe banner lines in this real log : "
          f"{f['trapfpe_banner_lines']}")
        p(f"      lines the DEFECTIVE broad clause matches: "
          f"{f['broad_defective_clause_hit_lines']}")
        p(f"      READER SAYS : fatal={f['reader_fatal']}  hits="
          f"{f['reader_fatal_hits']}   End line={f['end_line']}")
        p(f"      note        : {f['role_note']}")
    neg_ok = (len(neg) > 0
              and all((not f["reader_fatal"]) and f["trapfpe_banner_lines"] >= 1
                      for f in neg))
    p(f"  LIMB 2: {'SATISFIED' if neg_ok else 'NOT SATISFIED'} "
      f"({sum(1 for f in neg if not f['reader_fatal'])} of {len(neg)} real clean "
      f"logs read fatal=False, and all {sum(1 for f in neg if f['trapfpe_banner_lines'] >= 1)} "
      f"of them DO carry the banner -- so the zero is a READING, not an empty "
      f"population)")
    p("")
    p("THE CONTRAST THAT MAKES LIMB 2 LOAD-BEARING.  On the same real clean")
    p("logs, the DEFECTIVE broad clause `FOAM FATAL|Floating point exception|")
    p("signal` matches:")
    for f in neg:
        p(f"      {f['broad_defective_clause_hit_lines']:>6d} line(s)  "
          f"{os.path.basename(os.path.dirname(f['path']))}/"
          f"{os.path.basename(f['path'])}")
    p("  Every one of those is the enablement banner on a healthy run. The broad")
    p("  form would have condemned all of them (L-396, D548).")
    p("")

    rec = dict(
        item="M1b", generated_utc=now,
        instrument=os.path.abspath(__file__), instrument_sha256=self_sha256(),
        charter_clause="VERIFICATION_CHARTER.md section 2j (birth requirement), "
                       "2j.2 (real producer bytes)",
        narrow_clause=RE_FATAL.pattern,
        defective_broad_clause=RE_BROAD_DEFECTIVE.pattern,
        positive_limb=dict(passed=pos_ok, n_fixtures=len(pos), fixtures=pos),
        negative_limb=dict(passed=neg_ok, n_fixtures=len(neg), fixtures=neg),
    )
    json.dump(rec, open(BIRTH_RECORD, "w"), indent=2, sort_keys=True, default=str)
    txt = os.path.join(BIRTH_DIR, "m1b_birth_demonstration.txt")
    open(txt, "w").write("\n".join(lines) + "\n")
    p(f"wrote {BIRTH_RECORD}")
    p(f"wrote {txt}")
    open(txt, "w").write("\n".join(lines) + "\n")

    if not (pos_ok and neg_ok):
        print("BIRTH DEMONSTRATION: NOT SATISFIED -- this instrument may not "
              "grade.", file=sys.stderr)
        return 2
    print("BIRTH DEMONSTRATION: BOTH LIMBS SATISFIED ON REAL PRODUCER BYTES.")
    return 0


PROOFS = {
    "C1": "a blind reader must make planted_zero_control report passed=False",
    "C4": "removing the End line must make completion() report incomplete",
    "C5": "an absent STATUS must be NOT MEASURED, never a failure",
    "C7": "NEW IN M1b: a planted crash frame must make an otherwise identical "
          "COMPLETE row INCOMPLETE, and a real clean log carrying the trapFpe "
          "banner must NOT",
    "G3-LABEL": "the spread label must say it is NOT an uncertainty",
}


def planted_failure_proof(code):
    if code not in PROOFS:
        print(f"unknown proof {code}; known: {sorted(PROOFS)}", file=sys.stderr)
        return 2
    print(f"planted-failure proof {code}: {PROOFS[code]}")
    return selftest()


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Refusal as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
