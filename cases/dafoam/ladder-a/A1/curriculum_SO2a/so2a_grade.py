#!/usr/bin/env python3
"""CURRICULUM SO-2a -- THE FROZEN COMPARATOR.

Grades the geometric constraint family (thickness / volume / LE-radius) on
SO-1's NACA0012 case: the constraint VALUES against the tutorial's own
registered bounds, and the constraint JACOBIANS against a finite-difference
table, on TWO TOOLCHAIN ROWS, at np = 1.

Derived from `curriculum_SO1a/so1a_grade.py` (md5 6966d19eeccd275b45fe9a5492eef6d2)
with the deltas in `so2a_grade_DELTAS_from_so1a_grade.diff`.  Two of those
deltas are the point of the item and are stated here, at the top, because a
reader who reads nothing else must read these.

--------------------------------------------------------------------------
(I) C5 DOES NOT INHERIT THE BARE-SUBSTRING SCAN.  THE REPAIRED LOGIC IS PORTED
    FROM `curriculum_SO1c/so1c_grade.py` @ 42c7c8c3, WHICH IS THE ONLY PLACE IN
    THIS FAMILY WHERE IT IS CORRECT.
--------------------------------------------------------------------------
SO-1a's grader carries, at :122-125, the token `"Floating point exception"`
applied as a WHOLE-FILE SUBSTRING TEST.  OpenFOAM's standard startup banner is

    trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).

-- a notice that the solver is PROTECTED against the very failure the token
exists to detect.  SO-1a's run put that line at `MESH/checkMesh.log:18`; its
grader refused and published NOT A RESULT WITH ZERO GATES EVALUATED on a run
whose five arms were ALL rc = 0, and the refusal NAMED THE ARM LOG, a file
which contains the token ZERO times (verified on the surviving artefact by this
lane: `X-S_20260828T021855Z_1711422.log`, 690 lines, `trapFpe` count 0).

THE TOKEN IS NOT DELETED HERE, AND DELETING IT WOULD BE THE WORSE ERROR.
A missed SIGFPE is laundered into a result; a false hit costs a re-read.  So the
token STAYS in FATAL_TOKENS and the SCAN is repaired instead:

  * `fatal_token_sites()` scans PER FILE and LINE BY LINE, so a benign banner on
    line 18 can never suppress -- and can never impersonate -- a real crash on
    line 400, and every refusal names the FILE AND THE LINE that carries the hit.
  * `benign_reason()` is applied PER LINE with EXACTLY ONE exclusion,
    `^\\s*trapFpe:\\s`.
  * Every exclusion is COUNTED AND NAMED on the PASS record.  A suppression a
    reader cannot see is the same defect wearing the other hat.
  * `Foam::sigFpe::sigHandler` is added as an EXTRA POSITIVE token -- the one
    string OpenFOAM emits only when the handler has actually FIRED -- WITHOUT
    the `^` line anchor `sdk/chief_engineer/head_engineer.py:188` puts on it,
    because at np > 1 the realistic report is OpenMPI's `exited on signal 8
    (Floating point exception)`, which is not line-initial.

--------------------------------------------------------------------------
(II) THE BIRTH REQUIREMENT.  Sanaa, 2026-08-28, verbatim:
--------------------------------------------------------------------------
    "A control defined in terms of the thing it controls is not a control.  A
    planted control must travel the real production path -- written by the real
    producer's code, read through the real reader -- and prove the instrument
    sees a non-zero the same way reality would deliver one.  A control that
    empties the tuple it tests, or writes a schema the producer never emits,
    tests nothing and certifies blindness. ... rule 3's question -- 'was this
    reader ever shown able to see a non-zero through the real code path?' -- is
    now the birth requirement for every reader/comparator: no instrument grades
    anything until that answer is yes, demonstrated."

SEVEN readers here produce a graded number.  Each is named in `READERS`, each
carries the unit that BORE it, and `birth_record()` prints the register beside
the verdict.  Two of them read a ZERO as a PASS (G-STRUCT's Jacobian reader and
C5's log reader), which is exactly the reading rule 3 exists to distrust, so
each is driven in BOTH directions on REAL PRODUCER BYTES:

  * the X and F readers are driven on fixtures built by CALLING
    `so2a_xg.build_X_record` / `build_F_record` / `build_ctrl_row` /
    `build_fd_row` -- THE INSTRUMENT'S OWN WRITERS, the same functions its
    `main()` calls.  SO-1a's selftest wrote its F fixture with an inline
    `json.dump` of a hand-written dict; a key the instrument renamed would have
    left that fixture green and the reader blind.  Here the fixture CANNOT carry
    a key the producer does not emit, because the producer writes it.
  * the C5 log reader and the mesh-cells reader are driven on REAL OPENFOAM
    OUTPUT shipped beside this comparator in `reference/` -- SO-1a's own
    `MESH/checkMesh.log` (which carries the banner at line 18 and `cells: 4032`
    at line 39) and its `X-S` arm log (690 lines, banner count 0).  A crash line
    is planted INTO those real bytes and must be SEEN; the unplanted real bytes
    must NOT refuse.
  * the ledger reader is driven on rows emitted by SOURCING
    `so2a_run_arm.sh`'s own `so2a_ledger_row` function -- the launcher's code,
    not a copy of its format string.

WHERE A PRODUCER CANNOT BE DRIVEN, THE READER IS NAMED `NOT BORN` IN THE RECORD
AND THE COMPARATOR SAYS SO.  An honest gap is worth more than a fixture that
agrees with the reader by construction.

Exit 2 on any refusal.  A refusal is NOT A RESULT, never a degraded verdict.
"""

import ast
import io
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import so2a_xg as XG          # THE INSTRUMENT.  Its writers build every fixture.

# ---- REGISTERED CONSTANTS (PREREGISTRATION.md; the document governs) ----------------
ITEM = "SO2a"
BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-SO2a-a1-naca0012-geometric-constraint-gradient"
ARMS_REQUIRED = ["MESH", "X-S", "G-S", "X-P", "G-P"]
ARM_KIND = {"MESH": "SCRIPT", "X-S": "SOLVER", "G-S": "SOLVER", "X-P": "SOLVER", "G-P": "SOLVER"}
ARM_ROW = {"MESH": "SHIPPED", "X-S": "SHIPPED", "G-S": "SHIPPED", "X-P": "PATCHED", "G-P": "PATCHED"}
# np = 1 ON EVERY ARM by registration: DAFOAM_CHARTER.md section 5 (serial before
# parallel; a gradient verified at one np is a statement about THAT np).
ARM_RANKS = {"MESH": 1, "X-S": 1, "G-S": 1, "X-P": 1, "G-P": 1}
ARTEFACT = {"MESH": "checkMesh.log", "X-S": XG.OUT_X, "G-S": XG.OUT_F,
            "X-P": XG.OUT_X, "G-P": XG.OUT_F}
TERMINAL = {"X-S": XG.TERMINAL_X, "G-S": XG.TERMINAL_F,
            "X-P": XG.TERMINAL_X, "G-P": XG.TERMINAL_F}
ROW_OF = {"X-S": "S", "G-S": "S", "X-P": "P", "G-P": "P"}
# THE AGE-GUARD DATUM IS RESOLVED BY EXISTENCE, NEVER BY NAME.  SO-1a's five arms
# MEASURED the resolution on 2026-08-28: `0.orig/U` plain on MESH, `0/U.gz` -- the
# COMPRESSED twin -- on all four solver arms, exactly as `writeCompression on`
# (system/controlDict:27) produces at np = 1.  AV-1 and AV-2 both returned NOT A
# RESULT on that alone.  BOTH names are candidates; the one FOUND is recorded;
# NEITHER present is the only refusal, and it is DRIVEN.
DATUM_CANDIDATES = {"MESH": ("0.orig/U", "0.orig/U.gz"), "X-S": ("0/U", "0/U.gz"),
                    "G-S": ("0/U", "0/U.gz"), "X-P": ("0/U", "0/U.gz"), "G-P": ("0/U", "0/U.gz")}
DATUM_FILE = ".so2a_age_datum"
CONTROLDICT_REL = os.path.join("system", "controlDict")

# ---- C5.  See (I) at the top of this file.  PORTED FROM so1c_grade.py @ 42c7c8c3. --
FATAL_TOKENS = ("FOAM FATAL ERROR", "FOAM FATAL IO ERROR", "Segmentation fault",
                "SIGSEGV", "SIGKILL", "MPI_ABORT", "signal 9", "Signal 11",
                "Floating point exception",
                # the handler symbol: the ONE string OpenFOAM emits only when the
                # FPE handler has actually FIRED.  Its LINE ANCHOR is deliberately
                # NOT adopted -- see (I).
                "Foam::sigFpe::sigHandler")
BENIGN_LINE_PATTERNS = (
    (r"^\s*trapFpe:\s",
     "OpenFOAM sigFpe SETUP banner -- an ENABLEMENT NOTICE, not a crash"),
)
BENIGN_LINE_RE = tuple((re.compile(_p), _why) for _p, _why in BENIGN_LINE_PATTERNS)

CAPS = {"MESH": 5.0, "X-S": 12.0, "G-S": 25.0, "X-P": 12.0, "G-P": 25.0}
ITEM_CEILING_CORE_MIN = 79.0          # == sum(CAPS.values()), asserted in main()
PREDICTED_CORE_MIN = {"MESH": 0.19, "X-S": 1.5, "G-S": 3.0, "X-P": 1.5, "G-P": 3.0}
CELLS_EXPECTED = 4032

# ---- BAND D / BAND E / PLATEAU: INHERITED BY CITATION from SO-1a, which inherits
# ---- them from `curriculum_D4/PREREGISTRATION.md:82` and `D7FR:228-229`.  NOT
# ---- re-derived by a lane that has seen an answer.
FD_BAND_PCT = 5.0            # band D, per graded PAIR
AGG_BAND_PCT = 5.0           # band E, aggregate vector-relative, PER CONSTRAINT
PLATEAU_TOL_PCT = 10.0
NEAR_ZERO_ABS = 1.0e-14
# A pair whose FD reference is NEAR_ZERO or which has NO_PLATEAU is EXCLUDED, and
# every exclusion is counted and named.  A constraint needs at least this many
# GRADED pairs, and no more than this FRACTION of its candidates excluded, or it
# reads NOT A RESULT -- a gate that grades a quarter of its own Jacobian is not
# grading the Jacobian.
MIN_GRADED_PER_CONSTRAINT = 2
MAX_EXCLUDED_FRAC = 0.75

SHAPE_COMPONENTS = [("shape", 0), ("shape", 3), ("shape", 6), ("shape", 7)]
PATCHV_COMPONENTS = [("patchV", 1)]
COMPONENTS_REGISTERED = [[d, i] for (d, i) in SHAPE_COMPONENTS + PATCHV_COMPONENTS]
STEPS_REGISTERED = {"shape": [1.0e-2, 1.0e-3, 1.0e-4], "patchV": [1.0e-1, 1.0e-2, 1.0e-3]}

# ---- G-TB, THE REGISTERED TRIVIAL BASELINE (DAFOAM_CHARTER.md section 4) ----------
# NOT a step-based baseline, and that is a REGISTERED DECISION with a MEASURED
# reason, not an omission.  A geometric constraint is produced by pyGeo
# deterministically from the shape DV with NO iterative solve, so it is
# bit-repeatable and a step too SMALL (SO-1a's h = 1e-8) does NOT enter the
# subtractive-cancellation regime that makes SO-1a's baseline wrong; and
# `A_stepsize_study.md` measured the primal FAILING at h = 5e-2 and 1e-1 on this
# case, so a step too LARGE returns an EXCEPTION rather than a reading, and an
# errored probe is not a baseline.  BOTH DIRECTIONS OF A STEP-BASED BASELINE ARE
# UNAVAILABLE ON THIS QUANTITY.
#
# The substitute tests DISCRIMINATION rather than step: the adjoint vector over
# the four registered shape components is CYCLICALLY SHIFTED BY ONE and scored
# against the UNSHIFTED FD reference.  If the wrong pairing agrees as well as the
# right one, the gate is not telling components apart and its verdict is not
# evidence.  Gated on a RATIO, which needs no prior on coincidence rates:
#     G-TB PASS  iff  agg_shifted >= TB_MIN_RATIO * agg_unshifted, per constraint.
# TB_MIN_RATIO = 10.0 is the charter's own "an order of magnitude off".
TB_MIN_RATIO = 10.0
TB_MIN_ROWS = 1              # a constraint needs at least one output row with >= 2 graded pairs

# ---- G-CV, the CONSTRAINT'S OWN GATE: feasibility at the graded design ------------
# Bounds are the PRODUCER'S OWN, read from `so2a_runScript.py:176-178`:
#   add_constraint("geometry.thickcon", lower=0.5, upper=3.0)
#   add_constraint("geometry.volcon",   lower=1.0)
#   add_constraint("geometry.rcon",     lower=0.8)
# They are NOT re-derived here and NOT re-scaled.  FEAS_TOL is the tolerance the
# gate is stated to: a constraint sitting exactly ON its bound is SATISFIED.
CON_BOUNDS = {"thickcon": (0.5, 3.0), "volcon": (1.0, None), "rcon": (0.8, None)}
FEAS_TOL = 1.0e-9

CTRL_STEP = XG.CTRL_STEP
PLANT = XG.PLANT
CON_SIZES_EXPECTED = dict(XG.CON_SIZES_EXPECTED)
CON_NAMES = [n for n, _ in XG.CONSTRAINTS]

IMG_DIGEST = {"SHIPPED": "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc",
              "PATCHED": "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"}
SO_MD5 = {"SHIPPED": "f0fcb488e0e98156575cd19548e91663", "PATCHED": "85f59e87253e0a71a813f64ca6e4c425"}
CPUSET_REGISTERED = "9"
DELIVERED_CORES_FLOOR = 1.5

PRED = {"P2_con_baseline_band": (0.999, 1.001),
        "P4_patched_agg_max_pct": 1.0,
        "P5_divergence_max_pct": 1.0e-9,
        "P8_core_min_band": (5.5, 28.0), "P8b_mesh_wall_s_max": 120.0,
        "P10_X_arm_core_min_max": 3.0}

FIELDS_PHYSICS = ("rc_value", "oomkilled", "terminal_statement", "age_guard",
                  "no_fatal_token", "core_min", "cap_core_min", "DIGEST", "cpuset")
FIELDS_INFRASTRUCTURE = ("rc_record", "memavail_pre_GiB", "memavail_post_GiB", "delivered",
                         "siblings_pre", "siblings_post", "log", "wall_s")
NOT_MEASURED = "NOT_MEASURED"
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}

# ---- THE BIRTH REGISTER.  See (II).  Every reader that produces a graded number
# ---- is here, with the unit that bore it in BOTH directions.  A reader whose
# ---- producer cannot be driven is named NOT BORN and says why.
READERS = {
    "R1_read_ledger": {"produces": "core_min, rc, cpuset, DIGEST, oomkilled -> G1/G9/G10/G12",
                       "producer": "so2a_run_arm.sh:so2a_ledger_row",
                       "born_by": ["U40", "U41"], "born": True},
    "R2_fatal_token_sites": {"produces": "C5 site count -> G1 (READS A ZERO AS A PASS)",
                             "producer": "OpenFOAM / the arm shell, via reference/*.log",
                             "born_by": ["U50", "U51", "U52", "U53"], "born": True},
    "R3_read_mesh_cells": {"produces": "cell count -> G-M2",
                           "producer": "checkMesh, via reference/REAL_SO1a_MESH_checkMesh.log",
                           "born_by": ["U54", "U55"], "born": True},
    "R4_read_X": {"produces": "constraint Jacobian -> G5g, G-STRUCT (G-STRUCT READS A ZERO)",
                  "producer": "so2a_xg.build_X_record", "born_by": ["U56", "U57", "U58"], "born": True},
    "R5_read_F": {"produces": "FD derivative vectors -> G5g, G-TB",
                  "producer": "so2a_xg.build_F_record / build_fd_row / build_ctrl_row",
                  "born_by": ["U59", "U60"], "born": True},
    "R6_read_constraint_baseline": {"produces": "baseline constraint values -> G-CV, G-CDIM",
                                    "producer": "so2a_xg.build_X_record",
                                    "born_by": ["U61", "U62"], "born": True},
    "R7_arm_datum": {"produces": "age-guard mtime comparison -> G1/C4",
                     "producer": "the filesystem + the launcher's touch",
                     "born_by": ["U63", "U64"], "born": True},
}

# The suite's unit count, FROZEN.  Bumped DELIBERATELY from the 72 this lane first
# wrote to the 79 the finished suite drives, and the seven are named so the bump is
# not a rubber stamp: U40/U41 and U58 became named helpers after `open(p, "w")`
# was found truncating a file before its own `open(p).read()` ran (+0, restructured);
# U97 split into U97 (the AST detector's zero on this file) and U97b (the SAME
# detector's known positive on SO-1a's `fatal_tokens_in`), because a zero with no
# known positive beside it is a claim about the pattern (L-400); and U5, U26, U62,
# U75, U86, U91 and U92 were added while driving gates this lane had registered but
# not yet fired.  A count that drifts without a reason is how a suite loses a unit.
EXPECTED_UNITS = 79


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def count_asserts(path):
    """L-332: `python3 -O` strips `assert`, so an assert is not a guard.  Counted,
    with a planted one shown counted, rather than asserted absent."""
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


# ===================== R1: the ledger =================================================
LEDGER_RE = re.compile(
    r"ARM=(?P<ARM>\S+)\s+ROW=(?P<ROW>\S+)\s+IMG=(?P<IMG>\S+)\s+DIGEST=(?P<DIGEST>\S+)\s+"
    r"rc=(?P<rc>-?\d+)\s+wall_s=(?P<wall_s>\d+)\s+ranks=(?P<ranks>\d+)\s+"
    r"core_min=(?P<core_min>[\d.]+)\s+cap_core_min=(?P<cap>[\d.]+)\s+"
    r"enforced_wall_s=(?P<ewall>\d+)\s+enforced_core_min=(?P<ecore>[\d.]+)\s+"
    r"memory=(?P<mem>\S+)\s+inspect\(exit,oomkilled\)=\[(?P<inspect>[^\]]*)\]\s+"
    r"memavail_pre_GiB=(?P<mempre>\S+)\s+memavail_post_GiB=(?P<mempost>\S+)\s+"
    r"cpuset=(?P<cpuset>\S+)\s+delivered_cores_mean=\[(?P<delivered>[^\]]*)\]\s+"
    r"siblings_pre=\[(?P<sibpre>[^\]]*)\]\s+siblings_post=\[(?P<sibpost>[^\]]*)\]\s+"
    r"log=(?P<log>\S+)")


def _infra_float(v):
    if v is None or v == NOT_MEASURED:
        return None
    return float(v)


def read_ledger(path):
    if not os.path.isfile(path):
        refuse("ledger", {"absent": path})
    rows = {}
    for line in open(path, errors="replace"):
        if not line.startswith("ARM="):
            continue
        m = LEDGER_RE.search(line)
        if not m:
            refuse("ledger", {"row_unparseable": line.strip()[:300],
                              "note": "PRESENT-BUT-GARBAGE row: refused, never skipped"})
        g = m.groupdict()
        parts = g["inspect"].split()
        infra_nm = [k for k, v in (("memavail_pre_GiB", g["mempre"]), ("memavail_post_GiB", g["mempost"]),
                                   ("delivered", g["delivered"]), ("siblings_pre", g["sibpre"]),
                                   ("siblings_post", g["sibpost"]), ("log", g["log"]))
                    if v is None or NOT_MEASURED in str(v)]
        row = {"ARM": g["ARM"], "ROW": g["ROW"], "IMG": g["IMG"], "DIGEST": g["DIGEST"],
               "rc": int(g["rc"]), "wall_s": int(g["wall_s"]), "ranks": int(g["ranks"]),
               "core_min": float(g["core_min"]), "cap_core_min": float(g["cap"]),
               "enforced_core_min": float(g["ecore"]), "memory": g["mem"],
               # R-RC: `inspect(...)=[NOT_MEASURED ...]` is the rc RECORD being ABSENT
               # (infrastructure), carried as None so C1 applies the relaxation.
               "inspect_exit": (None if (not parts or parts[0] == NOT_MEASURED) else parts[0]),
               "oomkilled": (parts[1] if len(parts) > 1 else None),
               "memavail_pre_GiB": _infra_float(g["mempre"]), "memavail_post_GiB": _infra_float(g["mempost"]),
               "cpuset": g["cpuset"], "delivered": g["delivered"], "siblings_pre": g["sibpre"],
               "siblings_post": g["sibpost"], "log": g["log"], "source": "ledger_row",
               "infra_not_measured": infra_nm}
        if row["ARM"] in rows:
            refuse("ledger", {"duplicate_arm_row": row["ARM"],
                              "note": "two records for one run is the defect"})
        rows[row["ARM"]] = row
    return rows


def inspect_file_fallback(base, arm):
    """The surviving kernel record, when the ledger row's rc RECORD is absent."""
    best = None
    for fn in sorted(os.listdir(base)):
        if fn.startswith("%s_" % arm) and fn.endswith(".inspect.txt"):
            best = os.path.join(base, fn)
    if best is None:
        return None
    parts = open(best, errors="replace").read().split()
    if len(parts) < 2:
        return None
    return {"exit": parts[0], "oomkilled": parts[1], "file": os.path.basename(best)}


# ===================== R7: the age-guard datum ========================================
def read_write_compression(adir):
    p = os.path.join(adir, CONTROLDICT_REL)
    try:
        for line in open(p, errors="replace"):
            s = line.strip()
            if s.startswith("writeCompression"):
                return s.rstrip(";").split()[-1]
    except OSError:
        return None
    return None


def resolve_datum_ref(adir, arm, datum):
    """BY EXISTENCE, NEVER BY NAME.  Returns the resolution record or refuses only
    when NEITHER candidate name exists."""
    plain, gz = DATUM_CANDIDATES[arm]
    pp, pg = os.path.join(adir, plain), os.path.join(adir, gz)
    wc = read_write_compression(adir)
    if os.path.exists(pp):
        mt = int(os.path.getmtime(pp))
        return {"name": plain, "path": pp, "is_compressed_twin": False, "mtime": mt,
                "write_compression": wc, "mtime_rule": "the launcher touched it: must equal the datum",
                "ok": (mt == datum)}
    if os.path.exists(pg):
        mt = int(os.path.getmtime(pg))
        return {"name": gz, "path": pg, "is_compressed_twin": True, "mtime": mt,
                "write_compression": wc,
                "mtime_rule": "the solver wrote it AFTER the datum was taken: may only be NEWER",
                "ok": (mt >= datum)}
    refuse("G1", {"C4_age_datum_reference_absent_in_BOTH_names": [pp, pg], "arm": arm,
                  "write_compression": wc,
                  "note": "the ONLY refusal this resolution makes; AV-1/AV-2 died on the NAME"})


def arm_datum(base, arm):
    d = os.path.join(base, arm)
    p = os.path.join(d, DATUM_FILE)
    if not os.path.isfile(p):
        refuse("G1", {"age_datum_absent": p, "arm": arm})
    datum = int(open(p).read().strip())
    return d, datum, resolve_datum_ref(d, arm, datum)


NOT_A_GRADING_PATH = ("selftest", "_fix")


def whole_file_token_scan_sites(path):
    """THE SO-1a DEFECT SHAPE, DETECTED IN A FILE'S OWN AST.

    Positive signature: a function that references `FATAL_TOKENS` AND performs a
    membership test (`ast.In`) AND never splits the text into lines.  SO-1a's
    `fatal_tokens_in` is exactly that -- `[t for t in FATAL_TOKENS if t in text]`
    -- and it is the KNOWN POSITIVE this detector is proved against (U97b),
    because a sweep's zero is a claim about the pattern until a known positive
    makes it a claim about the code (L-400).

    `NOT_A_GRADING_PATH` excludes the selftest and its fixture builder BY NAME:
    they are not on any grading path, and a unit that asserts a token is present
    in a list is a membership test with no text in it.  The exclusion is narrow,
    named, and its cost is bounded -- the detector still reads every function
    that can reach a verdict.

    THIS REPLACES A REGEX.  This lane's first draft searched the source text for
    `"Floating point exception" in <name>` and reported a HIT -- on its own
    selftest's assertion `... in b_cm[0]["tokens"]`, and on `... in
    FATAL_TOKENS`.  The check was measuring its own pattern against its own
    units, not the grading path.  It is recorded here rather than quietly
    replaced."""
    tree = ast.parse(open(path).read())
    bad = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if fn.name in NOT_A_GRADING_PATH:
            continue
        if not any(isinstance(n, ast.Name) and n.id == "FATAL_TOKENS" for n in ast.walk(fn)):
            continue
        has_in = any(isinstance(c, ast.Compare) and any(isinstance(o, ast.In) for o in c.ops)
                     for c in ast.walk(fn))
        splits = any(isinstance(a, ast.Attribute) and a.attr == "splitlines"
                     for a in ast.walk(fn))
        if has_in and not splits:
            bad.append(fn.name)
    return bad


# ===================== R2: C5, the repaired token scan =================================
def benign_reason(line):
    """C5.  Why this ONE LINE is an enablement notice and not a crash, or None.
    Narrow by construction: see BENIGN_LINE_PATTERNS and (I) at the top."""
    for rx, why in BENIGN_LINE_RE:
        if rx.search(line):
            return why
    return None


def fatal_token_sites(text, source):
    """C5.  Scans LINE BY LINE and PER SOURCE FILE, returning (sites, benign).

    LINE BY LINE, because the test must tell a CRASH from an ENABLEMENT NOTICE
    and a whole-file substring test cannot.  Every token in FATAL_TOKENS is a
    single-line string, so splitting loses no match -- and that is DRIVEN, not
    asserted: a unit plants each token in turn and requires a refusal for each.

    PER SOURCE FILE, because the refusal must name the file that carries the hit.
    SO-1a's refusal named the ARM log while the token lived in `checkMesh.log`."""
    sites, benign = [], []
    for i, line in enumerate(text.splitlines(), 1):
        hit = [t for t in FATAL_TOKENS if t in line]
        if not hit:
            continue
        why = benign_reason(line)
        rec = {"file": source, "line": i, "tokens": hit, "text": line.strip()[:200]}
        if why:
            rec["why_benign"] = why
            benign.append(rec)
        else:
            sites.append(rec)
    return sites, benign


# ===================== R3: the mesh-cells reader ======================================
def read_mesh_cells(path):
    txt = open(path, errors="replace").read()
    m = re.search(r"^\s*cells:\s+(\d+)", txt, re.M)
    if not m:
        refuse("G-M2", {"cells_absent_in_checkMesh": path})
    return int(m.group(1))


# ===================== G1 =============================================================
def g_completion(base, rows):
    """The five rule-4 clauses, PRINTED INDIVIDUALLY per arm.

        C1 rc value          -- physics; the kernel's exit status
        C2 terminal marker   -- this item's `End` line (SOLVER) / `Mesh OK.` (SCRIPT)
        C3 artefact present  -- this item's `fields present`
        C4 age guard         -- the artefact strictly newer than the arm's own datum
        C5 no fatal token    -- REFUSES regardless of rc

    R-RC (Sanaa 2026-08-27 s0): the rc VALUE is physics, the rc RECORD is
    infrastructure.  When the record is absent from BOTH channels the rc VALUE
    reads NOT MEASURED **only when C2-C5 all hold**, and the implied rc = 0 is
    printed as an INFERENCE, never graded as a measurement."""
    out = {"arms": {}, "not_measured": {}, "rule4_clauses": {}, "datum_resolution": {},
           "rc_inferences": {}}
    for arm in ARMS_REQUIRED:
        r = rows.get(arm)
        if r is None:
            refuse("G1", {"ledger_row_absent": arm})
        cl = {}
        adir, datum, dres = arm_datum(base, arm)
        out["datum_resolution"][arm] = dres
        logname = r["log"]
        lp = os.path.join(base, logname)
        if not os.path.isfile(lp):
            refuse("G1", {"arm_log_absent": lp, "arm": arm})
        text = open(lp, errors="replace").read()
        r["log_text"] = text

        # ---- C3 artefact present ------------------------------------------------
        art = os.path.join(adir, ARTEFACT[arm])
        if not os.path.isfile(art):
            refuse("G1", {"C3_artefact_absent": art, "arm": arm})
        cl["C3_artefact_present"] = {"verdict": "PASS", "path": ARTEFACT[arm]}

        # ---- C4 age guard -------------------------------------------------------
        amt = int(os.path.getmtime(art))
        if not dres["ok"]:
            refuse("G1", {"C4_datum_reference_mtime_wrong": dres, "arm": arm})
        if amt <= datum:
            refuse("G1", {"C4_age_guard": {"artefact_mtime": amt, "datum": datum},
                          "arm": arm,
                          "note": "the artefact must be STRICTLY newer than the arm's own datum"})
        cl["C4_age_guard"] = {"verdict": "PASS", "artefact_mtime": amt, "datum": datum,
                              "datum_reference": dres["name"],
                              "is_compressed_twin": dres["is_compressed_twin"]}

        # ---- C2 terminal marker -------------------------------------------------
        kind = ARM_KIND[arm]
        if kind == "SOLVER":
            if TERMINAL[arm] not in text:
                refuse("G1", {"C2_terminal_marker_absent": TERMINAL[arm], "arm": arm,
                              "log": logname})
            cl["C2_terminal_marker"] = {"verdict": "PASS", "marker": TERMINAL[arm], "log": logname}
        else:
            mtext = open(art, errors="replace").read()
            if not re.search(r"^Mesh OK\.$", mtext, re.M):
                refuse("G1", {"C2_mesh_ok_absent": art, "arm": arm})
            cl["C2_terminal_marker"] = {"verdict": "PASS", "marker": "Mesh OK.",
                                        "log": ARTEFACT[arm]}

        # ---- C5 fatal token, REFUSES REGARDLESS OF rc ---------------------------
        # PER FILE and PER LINE.  `hay = text + artefact` discarded which file a
        # hit came from, which is why SO-1a's refusal named the arm log for a
        # token that only ever appeared in `checkMesh.log`.
        scanned = [logname]
        sites, benign = fatal_token_sites(text, logname)
        if kind == "SCRIPT":
            scanned.append(ARTEFACT[arm])
            s2, b2 = fatal_token_sites(open(art, errors="replace").read(), ARTEFACT[arm])
            sites += s2
            benign += b2
        if sites:
            refuse("G1", {"C5_fatal_token_in_arm_output": sorted({t for st in sites
                                                                  for t in st["tokens"]}),
                          "arm": arm, "log": logname, "files_scanned": scanned,
                          "token_sites": sites,
                          "note": ("a fatal token refuses at ANY rc; R-RC never launders a "
                                   "crash.  `token_sites` names the FILE AND LINE of every "
                                   "hit; `log` is the arm's own log and is NOT necessarily "
                                   "the file that carries the hit")})
        cl["C5_no_fatal_token"] = {"verdict": "PASS", "tokens_searched": list(FATAL_TOKENS),
                                   "files_scanned": scanned,
                                   "n_benign_lines_excluded": len(benign),
                                   "benign_lines_excluded": benign}

        # ---- OOMKilled (physics) -------------------------------------------------
        oom = str(r.get("oomkilled")).lower()
        if oom not in ("false", "true"):
            refuse("G1", {"oomkilled_unparseable": arm, "value": r.get("oomkilled"),
                          "note": "OOMKilled is a PHYSICS field and is not covered by R-RC"})
        if oom == "true":
            refuse("G1", {"oomkilled_true": arm, "note": "G11: an OOM kill is a refusal, never a re-fire"})

        # ---- C1 rc value, with R-RC ----------------------------------------------
        ke = r["inspect_exit"]
        if ke is None:
            fb = inspect_file_fallback(base, arm)
            if fb is not None:
                ke = fb["exit"]
                r["rc_record_source"] = fb["file"]
        if ke is None:
            # R-RC relaxes a MISSING record, never a positive reading of failure.
            if r["rc"] != 0:
                refuse("G1", {"C1_rc_record_absent_but_harness_rc_nonzero": r["rc"], "arm": arm,
                              "note": "R-RC relaxes a missing record, never a reading of failure"})
            cl["C1_rc_value"] = {"verdict": NOT_MEASURED,
                                 "note": "rc RECORD absent from BOTH channels; C2-C5 all hold"}
            out["rc_inferences"][arm] = {"inferred_rc": 0,
                                         "basis": "C2, C3, C4 and C5 all PASS and the harness rc reads 0",
                                         "status": "INFERENCE -- never graded as a measurement"}
            out["not_measured"].setdefault("rc_record", []).append(arm)
        else:
            if str(ke) != str(r["rc"]):
                refuse("G1", {"C1_harness_kernel_rc_disagree": {"harness": r["rc"], "kernel": ke},
                              "arm": arm})
            if int(ke) != 0:
                refuse("G1", {"C1_rc_nonzero": int(ke), "arm": arm})
            cl["C1_rc_value"] = {"verdict": "PASS", "rc": int(ke),
                                 "source": r.get("rc_record_source", "ledger_row")}
        out["rule4_clauses"][arm] = cl
        out["arms"][arm] = {"rc": r["rc"], "core_min": r["core_min"],
                            "infra_not_measured": r["infra_not_measured"]}
    return out


# ===================== R4/R5/R6: the artefact readers =================================
def _reshape(flat, n_out, where):
    if n_out <= 0 or len(flat) % n_out != 0:
        refuse(where, {"jacobian_not_reshapeable": {"len": len(flat), "n_out": n_out}})
    n_dv = len(flat) // n_out
    return [[float(v) for v in flat[i * n_dv:(i + 1) * n_dv]] for i in range(n_out)]


def read_constraint_baseline(rec, where):
    """R6.  The baseline constraint VALUES and their SIZES, from either artefact."""
    if rec.get("constraints") != CON_NAMES:
        refuse(where, {"constraints_not_registered": rec.get("constraints"),
                       "registered": CON_NAMES})
    base = {}
    for n in CON_NAMES:
        base[n] = [float(v) for v in rec["constraint_baseline"][n]]
    sizes = {n: int(rec["constraint_sizes"][n]) for n in CON_NAMES}
    for n in CON_NAMES:
        if len(base[n]) != sizes[n]:
            refuse(where, {"constraint_baseline_length_disagrees_with_recorded_size":
                           {"constraint": n, "len": len(base[n]), "size": sizes[n]}})
    return base, sizes


def read_X(path):
    """R4.  The constraint Jacobian, reshaped to (output index, dv index)."""
    j = json.load(open(path))
    base, sizes = read_constraint_baseline(j, "G-CV")
    jac = {}
    for n in CON_NAMES:
        jac[n] = {}
        for dv in ("shape", "patchV"):
            jac[n][dv] = _reshape(j["jacobian"][n][dv], sizes[n], "G5g")
    return {"con_base": base, "sizes": sizes, "jac": jac,
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"),
            "nprocs": j.get("nprocs"), "CD": float(j["CD_baseline"]), "CL": float(j["CL_baseline"]),
            "raw": j}


def read_F(path):
    """R5.  The FD table, keyed (dv, idx) -> step -> constraint -> vector."""
    j = json.load(open(path))
    if j.get("components_requested") != COMPONENTS_REGISTERED:
        refuse("G5g", {"components_requested_not_registered": j.get("components_requested"),
                       "registered": COMPONENTS_REGISTERED})
    if j.get("steps") != STEPS_REGISTERED:
        refuse("G5g", {"steps_not_registered": j.get("steps"), "registered": STEPS_REGISTERED})
    if j.get("tb_steps") is not None:
        refuse("G-TB", {"tb_steps_present": j.get("tb_steps"),
                        "note": ("this item registers NO step-based trivial baseline; a "
                                 "`tb_steps` block means the artefact is not this item's")})
    base, sizes = read_constraint_baseline(j, "G-CV")
    table, ctrl = {}, None
    for row in j["rows"]:
        if row.get("dv") == "CTRL":
            ctrl = row
            continue
        key = (row["dv"], int(row["idx"]))
        fd = {}
        for _k, v in (row.get("fd") or {}).items():
            if not v.get("ok"):
                fd[float(v["step"])] = {"ok": False}
                continue
            fd[float(v["step"])] = {"ok": True,
                                    "d": {n: [float(x) for x in v["d"][n]] for n in CON_NAMES}}
        table[key] = {"status": row.get("status"), "fd": fd}
    return {"table": table, "ctrl": ctrl, "con_base": base, "sizes": sizes,
            "eta": float(j["eta_used"]),
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"), "raw": j}


# ===================== rule 3: the live controls, at GRADE time =======================
def ctrl_control(F):
    """The INSTRUMENT's own planted control, re-read through the REAL reader.
    Both directions: every entry of `fd` must be EXACTLY 0.0, and entry 0 of
    `planted` must be EXACTLY PLANT/(2*step) for every constraint."""
    c = F["ctrl"]
    if c is None:
        refuse("CONTROL", {"ctrl_row_absent": True})
    want = PLANT / (2.0 * CTRL_STEP)
    # THE EMPTINESS CHECK COMES FIRST, BEFORE ANY INDEXING.  A control that
    # empties the tuple it tests must REFUSE, not raise -- and the first draft of
    # this function indexed `["d"][n][0]` in the same loop that collected the
    # zeros, so an emptied tuple crashed with an IndexError before it could be
    # refused.  A crash is not a verdict.
    for n in CON_NAMES:
        zf = c["fd"][repr(CTRL_STEP)]["d"].get(n)
        zp = c["planted"]["d"].get(n)
        if not zf or not zp:
            refuse("CONTROL", {"ctrl_tuple_EMPTY": {"constraint": n,
                                                    "n_zero_side": (0 if not zf else len(zf)),
                                                    "n_plant_side": (0 if not zp else len(zp))},
                               "note": ("a control that empties the tuple it tests certifies "
                                        "blindness -- Sanaa 2026-08-28")})
    zeros, plants = [], {}
    for n in CON_NAMES:
        zeros += [float(v) for v in c["fd"][repr(CTRL_STEP)]["d"][n]]
        plants[n] = float(c["planted"]["d"][n][0])
    bad0 = [v for v in zeros if v != 0.0]
    badp = {n: v for n, v in plants.items() if abs(v - want) > 1e-12 * abs(want)}
    if bad0 or badp:
        refuse("CONTROL", {"instrument_ctrl_not_seen": {"nonzero_in_zero_side": bad0[:5],
                                                        "planted": plants, "want": want}})
    return {"n_zero_entries_read": len(zeros), "planted_read": plants, "want": want,
            "both_directions": True}


def grader_plant_F(base, fpath, tag):
    """Write a copy with PLANT added to EVERY physical derivative entry, re-read it
    through the REAL reader, refuse unless every value moved by exactly PLANT."""
    j = json.load(open(fpath))
    for row in j["rows"]:
        if row.get("dv") == "CTRL":
            continue
        for v in (row.get("fd") or {}).values():
            if v.get("ok"):
                for n in CON_NAMES:
                    v["d"][n] = [repr(float(x) + PLANT) for x in v["d"][n]]
    cdir = os.path.join(base, "grader_controls")
    os.makedirs(cdir, exist_ok=True)
    cp = os.path.join(cdir, "F_%s_planted.json" % tag)
    json.dump(j, open(cp, "w"), indent=1, sort_keys=True)
    orig, back = read_F(fpath)["table"], read_F(cp)["table"]
    worst, n = 0.0, 0
    for key, row in orig.items():
        for s, v in row["fd"].items():
            if not v["ok"]:
                continue
            for cn in CON_NAMES:
                for a, b in zip(v["d"][cn], back[key]["fd"][s]["d"][cn]):
                    worst = max(worst, abs((b - a) - PLANT))
                    n += 1
    if n == 0 or worst > 1e-12:
        refuse("CONTROL", {"grader_plant_F_not_seen": {"n_values": n, "worst_residual": worst,
                                                       "plant": PLANT}})
    return {"grader_plant_F_seen": True, "n_values": n, "worst_residual": worst, "file": cp}


def grader_plant_X_struct(base, xpath, tag):
    """THE BIRTH OF THE ZERO-READER.  G-STRUCT PASSES ON A ZERO, which is exactly
    the reading rule 3 exists to distrust.  So: write a copy with PLANT added to
    ONE `patchV` Jacobian entry, re-read it through the REAL reader, and require
    G-STRUCT to FLIP to GATE FAIL on that copy while it PASSES on the original.
    A zero from a reader not shown able to see a non-zero is not evidence."""
    j = json.load(open(xpath))
    n0 = CON_NAMES[0]
    flat = list(j["jacobian"][n0]["patchV"])
    if not flat:
        refuse("CONTROL", {"grader_plant_X_target_EMPTY": n0,
                           "note": "the plant target must be a value the reader traverses"})
    flat[0] = repr(float(flat[0]) + PLANT)
    j["jacobian"][n0]["patchV"] = flat
    cdir = os.path.join(base, "grader_controls")
    os.makedirs(cdir, exist_ok=True)
    cp = os.path.join(cdir, "X_%s_struct_planted.json" % tag)
    json.dump(j, open(cp, "w"), indent=1, sort_keys=True)
    seen = read_X(cp)["jac"][n0]["patchV"][0][0]
    if abs(seen - (float(read_X(xpath)["jac"][n0]["patchV"][0][0]) + PLANT)) > 1e-12:
        refuse("CONTROL", {"grader_plant_X_not_seen_by_reader": {"read_back": seen, "plant": PLANT}})
    return {"grader_plant_X_seen": True, "read_back": seen, "constraint": n0, "file": cp,
            "note": "the G-STRUCT flip on this copy is asserted by the caller"}


def grader_plant_cells(base, cmpath):
    """R3's birth: the cells reader must read a DIFFERENT number off a changed
    real checkMesh log, not merely the expected one off the real log."""
    txt = open(cmpath, errors="replace").read()
    m = re.search(r"^\s*cells:\s+(\d+)", txt, re.M)
    if not m:
        refuse("CONTROL", {"grader_plant_cells_no_target": cmpath,
                           "note": "the plant must land on bytes the reader reads"})
    # The plant is OFFSET FROM WHAT IS ON DISK, so it is a real change whatever
    # the artefact holds -- a fixed constant collides with a fixture that already
    # carries it, and the collision reads as "no substitution" rather than as the
    # control it was.  This is NOT the reader defining its own target: the offset
    # is applied by `re.sub` to raw bytes and `want` is computed independently of
    # `read_mesh_cells`, which is the function under test.
    want = int(m.group(1)) + 7
    planted = re.sub(r"^(\s*cells:\s+)\d+", r"\g<1>%d" % want, txt, count=1, flags=re.M)
    if planted == txt:
        refuse("CONTROL", {"grader_plant_cells_no_substitution": cmpath})
    cdir = os.path.join(base, "grader_controls")
    os.makedirs(cdir, exist_ok=True)
    cp = os.path.join(cdir, "checkMesh_planted.log")
    open(cp, "w").write(planted)
    got = read_mesh_cells(cp)
    if got != want:
        refuse("CONTROL", {"grader_plant_cells_not_seen": {"read_back": got, "want": want}})
    return {"grader_plant_cells_seen": True, "read_back": got, "want": want,
            "on_disk_before_plant": int(m.group(1)), "file": cp}


def grader_plant_c5(base, rows):
    """R2's birth, BOTH DIRECTIONS, ON THE RUN'S OWN REAL LOG BYTES.
    (+) a real crash line planted into the arm's own text MUST be seen;
    (-) the same text unplanted must produce ZERO sites, and any benign banner in
        it must be COUNTED as excluded rather than silently dropped."""
    arm = ARMS_REQUIRED[1]
    text = rows[arm]["log_text"]
    neg_sites, neg_benign = fatal_token_sites(text, "REAL:%s" % rows[arm]["log"])
    if neg_sites:
        refuse("CONTROL", {"grader_plant_c5_negative_direction_failed": neg_sites[:3]})
    planted = text + "\n#1  Foam::sigFpe::sigHandler(int) at ??:?\n"
    pos_sites, _ = fatal_token_sites(planted, "REAL+PLANT:%s" % rows[arm]["log"])
    if len(pos_sites) != 1 or "Foam::sigFpe::sigHandler" not in pos_sites[0]["tokens"]:
        refuse("CONTROL", {"grader_plant_c5_positive_direction_failed": pos_sites[:3],
                           "note": "the reader was not shown able to see a real crash"})
    banner = "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).\n"
    b_sites, b_benign = fatal_token_sites(text + banner, "REAL+BANNER:%s" % rows[arm]["log"])
    if b_sites or len(b_benign) != 1:
        refuse("CONTROL", {"grader_plant_c5_banner_direction_failed":
                           {"sites": b_sites[:3], "n_benign": len(b_benign)}})
    return {"grader_plant_c5_seen": True, "arm": arm, "real_log": rows[arm]["log"],
            "n_lines_real": len(text.splitlines()),
            "negative_sites": 0, "positive_sites": 1, "banner_excluded_and_counted": 1}


# ===================== G-CDIM / G-CV ==================================================
def g_cdim(X, F):
    per = {}
    verdict = "PASS"
    for n in CON_NAMES:
        got_x, got_f, exp = X["sizes"][n], F["sizes"][n], CON_SIZES_EXPECTED[n]
        ok = (got_x == exp and got_f == exp)
        per[n] = {"size_X": got_x, "size_F": got_f, "expected": exp, "ok": ok}
        if not ok:
            verdict = "GATE FAIL"
    return {"per_constraint": per, "verdict": verdict,
            "expected_derived_from": ("the PRODUCER's own call arguments in so2a_runScript.py "
                                      "(nSpan=2, nChord=10 -> 20; volume -> 1; LE-radius nSpan=2 "
                                      "-> 2), never from a guess about pyGeo internals"),
            "note": ("a size mismatch is a GATE FAIL, not a refusal: the gradient grading "
                     "runs off the sizes ACTUALLY RECORDED, so a layout surprise does not "
                     "corrupt it")}


def g_constraint_values(X):
    """G-CV -- THE CONSTRAINT'S OWN GATE, in the only form this rung can buy it:
    feasibility at the GRADED DESIGN (the tutorial's baseline), to the stated
    tolerance.  Feasibility AT AN OPTIMUM is SO-2b's gate and cannot be
    registered until an optimum exists."""
    per, verdict = {}, "PASS"
    for n in CON_NAMES:
        lo, hi = CON_BOUNDS[n]
        vals = X["con_base"][n]
        worst_lo = min((v - lo) for v in vals) if lo is not None else None
        worst_hi = min((hi - v) for v in vals) if hi is not None else None
        viol = []
        for i, v in enumerate(vals):
            if lo is not None and v < lo - FEAS_TOL:
                viol.append({"index": i, "value": v, "bound": "lower", "limit": lo})
            if hi is not None and v > hi + FEAS_TOL:
                viol.append({"index": i, "value": v, "bound": "upper", "limit": hi})
        active = [i for i, v in enumerate(vals)
                  if (lo is not None and abs(v - lo) <= FEAS_TOL)
                  or (hi is not None and abs(v - hi) <= FEAS_TOL)]
        per[n] = {"lower": lo, "upper": hi, "n": len(vals),
                  "min": min(vals) if vals else None, "max": max(vals) if vals else None,
                  "margin_to_lower": worst_lo, "margin_to_upper": worst_hi,
                  "violations": viol, "indices_ACTIVE_at_a_bound": active,
                  "verdict": "GATE FAIL" if viol else "PASS"}
        if viol:
            verdict = "GATE FAIL"
    return {"per_constraint": per, "verdict": verdict, "feasibility_tolerance": FEAS_TOL,
            "bounds_source": "so2a_runScript.py:176-178, the PRODUCER's own add_constraint calls",
            "scope": ("feasibility AT THE GRADED DESIGN.  Feasibility AT AN OPTIMUM is SO-2b's "
                      "gate; no optimiser runs in this item")}


# ===================== G5g: the bright line ===========================================
def _pair_rows(X, F, cn, out_i):
    """The four registered shape components for one constraint output row, with
    each pair's adjoint value, FD reference and exclusion status."""
    out = []
    for dv, idx in SHAPE_COMPONENTS:
        rec = {"constraint": cn, "out_index": out_i, "dv": dv, "idx": idx}
        jrow = X["jac"][cn][dv]
        frow = F["table"].get((dv, idx))
        if out_i >= len(jrow) or idx >= len(jrow[out_i]) or frow is None:
            rec.update({"graded": False, "reason": "ABSENT"})
            out.append(rec)
            continue
        j = jrow[out_i][idx]
        rec["J_adj"] = j
        steps = sorted(STEPS_REGISTERED[dv], reverse=True)
        vals = [frow["fd"].get(s) for s in steps]
        if any(v is None or not v["ok"] for v in vals):
            rec.update({"graded": False, "reason": "FD_STEP_FAILED_OR_ABSENT"})
            out.append(rec)
            continue
        d = [v["d"][cn][out_i] for v in vals]
        ref = d[1]
        rec.update({"steps": steps, "d_fd": d, "d_ref": ref})
        if abs(ref) < NEAR_ZERO_ABS:
            rec.update({"graded": False, "reason": "NEAR_ZERO"})
            out.append(rec)
            continue
        nb = [abs(d[0] - ref) / abs(ref) * 100.0, abs(d[2] - ref) / abs(ref) * 100.0]
        rec["plateau_neighbour_pct"] = nb
        if min(nb) > PLATEAU_TOL_PCT:
            rec.update({"graded": False, "reason": "NO_PLATEAU"})
            out.append(rec)
            continue
        rel = abs(ref - j) / abs(ref) * 100.0
        flip = bool(ref * j < 0.0)
        rec.update({"graded": True, "rel_err_pct": rel, "sign_flip": flip,
                    "verdict": "GATE FAIL" if (flip or rel > FD_BAND_PCT) else "PASS"})
        out.append(rec)
    return out


def grade_constraint_jacobians(X, F):
    """G5g -- band D per graded PAIR, band E per CONSTRAINT.  Every excluded pair
    is COUNTED AND NAMED; a constraint that excludes more than MAX_EXCLUDED_FRAC
    of its candidates reads NOT A RESULT, because a gate that grades a quarter of
    its own Jacobian is not grading the Jacobian."""
    per, verdict = {}, "PASS"
    all_rows = {}
    for cn in CON_NAMES:
        rows, fd_v, adj_v = [], [], []
        n_cand = 0
        for i in range(X["sizes"][cn]):
            pr = _pair_rows(X, F, cn, i)
            rows.append(pr)
            n_cand += len(pr)
            for p in pr:
                if p.get("graded"):
                    fd_v.append(p["d_ref"])
                    adj_v.append(p["J_adj"])
        all_rows[cn] = rows
        flat = [p for pr in rows for p in pr]
        n_graded = len(fd_v)
        excl = {}
        for p in flat:
            if not p.get("graded"):
                excl[p["reason"]] = excl.get(p["reason"], 0) + 1
        c = {"n_candidate_pairs": n_cand, "n_graded_pairs": n_graded,
             "excluded_by_reason": excl,
             "excluded_frac": (round((n_cand - n_graded) / n_cand, 6) if n_cand else 1.0),
             "n_pass": sum(1 for p in flat if p.get("verdict") == "PASS"),
             "n_gate_fail": sum(1 for p in flat if p.get("verdict") == "GATE FAIL"),
             "sign_flips": sum(1 for p in flat if p.get("sign_flip")),
             "worst_rel_err_pct": (max([p["rel_err_pct"] for p in flat if p.get("graded")])
                                   if n_graded else None),
             "pairs": flat}
        if n_graded < MIN_GRADED_PER_CONSTRAINT or c["excluded_frac"] > MAX_EXCLUDED_FRAC:
            c.update({"verdict": "NOT A RESULT", "aggregate_rel_err_pct": None,
                      "reason": ("fewer than %d graded pairs" % MIN_GRADED_PER_CONSTRAINT
                                 if n_graded < MIN_GRADED_PER_CONSTRAINT
                                 else "more than %.0f %% of candidate pairs excluded"
                                      % (MAX_EXCLUDED_FRAC * 100))})
            per[cn] = c
            verdict = "NOT A RESULT"
            continue
        num = math.sqrt(sum((a - b) ** 2 for a, b in zip(fd_v, adj_v)))
        den = math.sqrt(sum(a ** 2 for a in fd_v))
        agg = num / den * 100.0 if den > 0 else None
        c["aggregate_rel_err_pct"] = agg
        band_d = c["n_gate_fail"] == 0
        band_e = agg is not None and agg <= AGG_BAND_PCT
        c["band_D"] = "PASS" if band_d else "GATE FAIL"
        c["band_E"] = "PASS" if band_e else "GATE FAIL"
        c["verdict"] = "PASS" if (band_d and band_e) else "GATE FAIL"
        per[cn] = c
        if c["verdict"] == "GATE FAIL" and verdict == "PASS":
            verdict = "GATE FAIL"
    return {"per_constraint": per, "verdict": verdict, "_rows": all_rows}


# ===================== G-STRUCT: the exact-zero gate ==================================
def g_struct(X, F, controls_seen):
    """d(geometric constraint)/d(patchV) == EXACTLY 0.0, on BOTH the adjoint and
    the FD side.  A geometric constraint is a function of the SHAPE alone; a
    non-zero here means the constraints are wired to the flow state and the
    model is not the one this record assumes.

    THIS GATE PASSES ON A ZERO.  It is composed ONLY when the planted control has
    shown the SAME readers seeing a NON-zero in the SAME run.  Rule 3 is a
    precondition of the gate, not a footnote beside it."""
    if not controls_seen:
        refuse("G-STRUCT", {"controls_not_seen": True,
                            "note": ("a zero from a reader not shown able to see a non-zero "
                                     "is not evidence; the gate is not composed")})
    adj_nz, fd_nz, n_adj, n_fd = [], [], 0, 0
    for cn in CON_NAMES:
        for i, row in enumerate(X["jac"][cn]["patchV"]):
            for k, v in enumerate(row):
                n_adj += 1
                if v != 0.0:
                    adj_nz.append({"constraint": cn, "out_index": i, "patchV_index": k,
                                   "J_adj": v})
        for dv, idx in PATCHV_COMPONENTS:
            frow = F["table"].get((dv, idx))
            if frow is None:
                refuse("G-STRUCT", {"fd_row_absent": [dv, idx]})
            for s in sorted(STEPS_REGISTERED[dv], reverse=True):
                v = frow["fd"].get(s)
                if v is None or not v["ok"]:
                    refuse("G-STRUCT", {"fd_step_absent_or_failed": {"dv": dv, "idx": idx,
                                                                     "step": s}})
                for i, x in enumerate(v["d"][cn]):
                    n_fd += 1
                    if x != 0.0:
                        fd_nz.append({"constraint": cn, "out_index": i, "dv": dv, "idx": idx,
                                      "step": s, "d_fd": x})
    if n_adj == 0 or n_fd == 0:
        refuse("G-STRUCT", {"empty_tuple": {"n_adjoint": n_adj, "n_fd": n_fd},
                            "note": "a gate over an empty tuple tests nothing"})
    verdict = "PASS" if (not adj_nz and not fd_nz) else "GATE FAIL"
    return {"verdict": verdict, "n_adjoint_entries_checked": n_adj, "n_fd_entries_checked": n_fd,
            "adjoint_nonzero": adj_nz[:10], "n_adjoint_nonzero": len(adj_nz),
            "fd_nonzero": fd_nz[:10], "n_fd_nonzero": len(fd_nz),
            "rule": "EXACTLY 0.0 on both sides; no tolerance, because the value is structural",
            "controls_precondition": "SATISFIED -- the planted control was seen in this run"}


# ===================== G-TB: the cyclic-shift trivial baseline ========================
def g_tb(g5):
    """The registered trivial baseline: CYCLIC SHIFT of the adjoint vector over the
    four registered shape components, scored against the UNSHIFTED FD reference.
    PASS iff the wrong pairing is at least TB_MIN_RATIO times worse.

    A ratio needs no prior on coincidence rates and directly measures the thing
    that matters: whether the gate can tell components apart at all."""
    per, verdict = {}, "PASS"
    for cn in CON_NAMES:
        d_u, j_u, j_s, n_rows_used, n_shift_pass = [], [], [], 0, 0
        for pr in g5["_rows"][cn]:
            g = [p for p in pr if p.get("graded")]
            if len(g) < 2:
                continue
            n_rows_used += 1
            D = [p["d_ref"] for p in g]
            J = [p["J_adj"] for p in g]
            S = J[-1:] + J[:-1]              # cyclic shift by one
            d_u += D
            j_u += J
            j_s += S
            for a, b in zip(D, S):
                if abs(a) >= NEAR_ZERO_ABS and abs(a - b) / abs(a) * 100.0 <= FD_BAND_PCT:
                    n_shift_pass += 1
        if n_rows_used < TB_MIN_ROWS:
            per[cn] = {"verdict": "NOT A RESULT", "n_rows_used": n_rows_used,
                       "reason": "no output row carries >= 2 graded pairs; the shift is undefined"}
            verdict = "NOT A RESULT"
            continue
        den = math.sqrt(sum(a ** 2 for a in d_u))
        agg_u = math.sqrt(sum((a - b) ** 2 for a, b in zip(d_u, j_u))) / den * 100.0
        agg_s = math.sqrt(sum((a - b) ** 2 for a, b in zip(d_u, j_s))) / den * 100.0
        if agg_u == 0.0:
            per[cn] = {"verdict": "NOT A RESULT", "agg_unshifted_pct": 0.0,
                       "agg_shifted_pct": agg_s,
                       "reason": "the unshifted aggregate is exactly 0.0; the ratio is undefined"}
            verdict = "NOT A RESULT"
            continue
        ratio = agg_s / agg_u
        v = "PASS" if ratio >= TB_MIN_RATIO else "GATE FAIL"
        per[cn] = {"verdict": v, "n_rows_used": n_rows_used, "n_pairs": len(d_u),
                   "agg_unshifted_pct": agg_u, "agg_shifted_pct": agg_s, "ratio": ratio,
                   "min_ratio": TB_MIN_RATIO,
                   "n_pairs_passing_band_D_under_the_SHIFT": n_shift_pass,
                   "frac_passing_under_shift": (round(n_shift_pass / len(d_u), 6) if d_u else None),
                   "reported_not_gated": "frac_passing_under_shift is REPORTED, never gated"}
        if v == "GATE FAIL" and verdict == "PASS":
            verdict = "GATE FAIL"
    return {"per_constraint": per, "verdict": verdict,
            "composition": ("COMPOSED ONLY ONTO A ROW WHOSE G5g VERDICT IS PASS -- see "
                            "compose_row.  Printed on every row regardless."),
            "baseline": ("CYCLIC-SHIFT (wrong-component).  A step-based baseline is "
                         "UNAVAILABLE on this quantity in BOTH directions and that is "
                         "registered with its measured reason -- see so2a_xg.py tb_note"),
            "consequence": ("the trivial baseline FAILS as registered, so the FD gate is "
                            "discriminating components" if verdict == "PASS" else
                            "the WRONG pairing agrees comparably: the gate is not measuring "
                            "what it claims and the G5g verdict for this row is WITHDRAWN to "
                            "NOT A RESULT (DAFOAM_CHARTER.md section 4)")}


def compose_row(g5, gtb, gstruct):
    """G-TB and G-STRUCT can only turn a PASS or a GATE FAIL INTO NOT A RESULT /
    GATE FAIL, never the reverse (the standing-rule-5 direction).

    G-TB IS COMPOSED ONLY ONTO A PASS, AND THAT IS REGISTERED.  The charter's
    clause is *"if the wrong step also passes, the gate is not measuring what it
    claims and THE VERDICT IT PRODUCED IS WITHDRAWN"* -- the verdict at issue is
    a PASS.  A row that already GATE FAILs on its own merits needs no trivial
    baseline to doubt it, and composing one there would convert a REAL gradient
    defect into NOT A RESULT and hide the finding: a large genuine error inflates
    the unshifted aggregate and so collapses the shift ratio by construction.
    G-TB's own verdict is PRINTED on every row either way; only its COMPOSITION
    is restricted.  This narrowing can never turn a NOT A RESULT into anything
    better, so the standing-rule-5 direction is preserved."""
    if g5["verdict"] == "NOT A RESULT":
        return "NOT A RESULT"
    if g5["verdict"] == "GATE FAIL" or gstruct["verdict"] == "GATE FAIL":
        return "GATE FAIL"
    if gtb["verdict"] in ("GATE FAIL", "NOT A RESULT"):
        return "NOT A RESULT"
    return "PASS"


# ===================== G9 / G10 / G12 =================================================
def g_toolchain(rows):
    out = {"per_arm": {}, "verdict": "PASS"}
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        row = ARM_ROW[arm]
        m = re.search(r"D4S_IDWARP_SO_MD5:\s*([0-9a-f]{32})", r.get("log_text", ""))
        printed = m.group(1) if m else None
        ok = (r.get("DIGEST") == IMG_DIGEST[row]) and (printed == SO_MD5[row])
        art_md5 = r.get("artefact_so_md5")
        if arm != "MESH":
            ok = ok and (art_md5 == SO_MD5[row])
        out["per_arm"][arm] = {"row": row, "digest": r.get("DIGEST"), "printed_so_md5": printed,
                               "artefact_so_md5": art_md5, "ok": bool(ok)}
        if not ok:
            out["verdict"] = "GATE FAIL"
    return out


def g_caps(rows):
    out = {"per_arm": {}, "verdict": "PASS", "total_core_min": 0.0,
           "ceiling": ITEM_CEILING_CORE_MIN, "not_measured": []}
    for arm in ARMS_REQUIRED:
        cm = rows[arm].get("core_min")
        if cm is None:
            out["not_measured"].append(arm)
            out["per_arm"][arm] = {"core_min": NOT_MEASURED, "cap": CAPS[arm]}
            continue
        out["total_core_min"] += cm
        crossed = cm > CAPS[arm]
        out["per_arm"][arm] = {"core_min": cm, "cap": CAPS[arm], "crossed": crossed,
                               "ratio_actual_over_predicted": round(cm / PREDICTED_CORE_MIN[arm], 4)}
        if crossed:
            out["verdict"] = "GATE FAIL"
    if out["total_core_min"] > ITEM_CEILING_CORE_MIN:
        out["verdict"] = "GATE FAIL"
    return out


def g_placement(rows):
    out = {"per_arm": {}, "verdict": "PASS", "not_measured": []}
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        cs_ok = r.get("cpuset") == CPUSET_REGISTERED
        m = re.match(r"\s*([\d.]+)\s+n=(\d+)", r.get("delivered") or "")
        dl = float(m.group(1)) if m else None
        if dl is None:
            out["not_measured"].append(arm)
        # At np = 1 the delivered-cores floor does not apply and is not composed.
        dl_ok = True if (dl is None or ARM_RANKS[arm] == 1) else dl >= DELIVERED_CORES_FLOOR
        out["per_arm"][arm] = {"cpuset": r.get("cpuset"),
                               "delivered_cores_mean": (dl if dl is not None else NOT_MEASURED)}
        if not (cs_ok and dl_ok):
            out["verdict"] = "GATE FAIL"
    return out


def birth_record():
    return {"requirement": ("Sanaa 2026-08-28: no instrument grades anything until 'was this "
                           "reader ever shown able to see a non-zero through the real code "
                           "path?' is answered YES, demonstrated"),
            "readers": READERS,
            "n_born": sum(1 for v in READERS.values() if v["born"]),
            "n_not_born": sum(1 for v in READERS.values() if not v["born"]),
            "not_born": [k for k, v in READERS.items() if not v["born"]]}


# ===================== the grade =======================================================
def grade(root):
    rows = read_ledger(os.path.join(root, "ledger.txt"))
    g1 = g_completion(root, rows)

    cmpath = os.path.join(root, "MESH", "checkMesh.log")
    cells = read_mesh_cells(cmpath)
    gm2 = "PASS" if cells == CELLS_EXPECTED else "GATE FAIL"

    X = {rk: read_X(os.path.join(root, arm, XG.OUT_X))
         for arm, rk in (("X-S", "S"), ("X-P", "P"))}
    F = {rk: read_F(os.path.join(root, arm, XG.OUT_F))
         for arm, rk in (("G-S", "S"), ("G-P", "P"))}
    rows["X-S"]["artefact_so_md5"] = X["S"]["so_md5"]
    rows["X-P"]["artefact_so_md5"] = X["P"]["so_md5"]
    rows["G-S"]["artefact_so_md5"] = F["S"]["so_md5"]
    rows["G-P"]["artefact_so_md5"] = F["P"]["so_md5"]

    # ---- rule 3, LIVE, on the real artefacts, BEFORE any gate is composed ----------
    controls = {"instrument_ctrl_S": ctrl_control(F["S"]),
                "instrument_ctrl_P": ctrl_control(F["P"]),
                "grader_plant_F_S": grader_plant_F(root, os.path.join(root, "G-S", XG.OUT_F), "S"),
                "grader_plant_F_P": grader_plant_F(root, os.path.join(root, "G-P", XG.OUT_F), "P"),
                "grader_plant_X_struct_S": grader_plant_X_struct(root, os.path.join(root, "X-S", XG.OUT_X), "S"),
                "grader_plant_X_struct_P": grader_plant_X_struct(root, os.path.join(root, "X-P", XG.OUT_X), "P"),
                "grader_plant_cells": grader_plant_cells(root, cmpath),
                "grader_plant_c5": grader_plant_c5(root, rows)}
    # THE ZERO-READER'S BIRTH, DRIVEN AT GRADE TIME: G-STRUCT must FLIP on the
    # planted copy.  If it does not, the gate cannot see a violation and is void.
    for rk, arm in (("S", "X-S"), ("P", "X-P")):
        cp = controls["grader_plant_X_struct_%s" % rk]["file"]
        flipped = g_struct(read_X(cp), F[rk], True)["verdict"]
        if flipped != "GATE FAIL":
            refuse("CONTROL", {"g_struct_did_not_flip_on_the_planted_copy": {"row": rk,
                                                                             "verdict": flipped},
                               "note": ("G-STRUCT passes on a zero; a zero from a gate not shown "
                                        "able to read a violation is not evidence")})
        controls["grader_plant_X_struct_%s" % rk]["g_struct_flipped_to"] = flipped

    g5 = {}
    for rk in ("S", "P"):
        j = grade_constraint_jacobians(X[rk], F[rk])
        tb = g_tb(j)
        st = g_struct(X[rk], F[rk], True)
        j_pub = {k: v for k, v in j.items() if k != "_rows"}
        g5[rk] = {"G5g_constraint_jacobians": j_pub, "G_TB_trivial_baseline": tb,
                  "G_STRUCT_flow_independence": st,
                  "row_verdict": compose_row(j, tb, st),
                  "eta_F": F[rk]["eta"]}

    gcv = g_constraint_values(X["S"])
    gcdim = g_cdim(X["S"], F["S"])
    gcdim_P = g_cdim(X["P"], F["P"])
    if gcdim_P["verdict"] != "PASS":
        gcdim["verdict"] = "GATE FAIL"
        gcdim["patched_row"] = gcdim_P

    # ---- divergence shipped-vs-patched on the constraint Jacobians -----------------
    div, worst_div = [], 0.0
    for cn in CON_NAMES:
        for dv, idx in SHAPE_COMPONENTS:
            a, b = X["S"]["jac"][cn][dv], X["P"]["jac"][cn][dv]
            for i in range(min(len(a), len(b))):
                if idx >= len(a[i]) or idx >= len(b[i]):
                    continue
                den = max(abs(a[i][idx]), abs(b[i][idx]), 1e-300)
                d = abs(a[i][idx] - b[i][idx]) / den * 100.0
                worst_div = max(worst_div, d)
                if d > 0.0:
                    div.append({"constraint": cn, "out_index": i, "dv": dv, "idx": idx,
                                "J_shipped": a[i][idx], "J_patched": b[i][idx],
                                "divergence_pct": d})
    div = sorted(div, key=lambda r: -r["divergence_pct"])[:20]

    g9, g10, g12 = g_toolchain(rows), g_caps(rows), g_placement(rows)

    # ---- predictions, scored, never adjusted --------------------------------------
    lo, hi = PRED["P2_con_baseline_band"]
    allv = [v for cn in CON_NAMES for v in X["S"]["con_base"][cn]]
    preds = {"P1_cells_4032": "HIT" if gm2 == "PASS" else "MISS",
             "P2_constraint_baselines_all_near_1": ("HIT" if allv and all(lo <= v <= hi for v in allv)
                                                    else "MISS"),
             "P3_G_CV_feasible_at_the_graded_design": "HIT" if gcv["verdict"] == "PASS" else "MISS"}
    pj = g5["P"]["G5g_constraint_jacobians"]
    aggs = [pj["per_constraint"][cn].get("aggregate_rel_err_pct") for cn in CON_NAMES]
    preds["P4_patched_row_constraint_jacobians_PASS"] = (
        "NOT_MEASURED" if pj["verdict"] == "NOT A RESULT" else
        ("HIT" if (pj["verdict"] == "PASS" and all(a is not None and a <= PRED["P4_patched_agg_max_pct"]
                                                   for a in aggs)) else "MISS"))
    sj = g5["S"]["G5g_constraint_jacobians"]
    preds["P5_SHIPPED_row_ALSO_PASS_and_divergence_is_zero"] = (
        "NOT_MEASURED" if sj["verdict"] == "NOT A RESULT" else
        ("HIT" if (sj["verdict"] == "PASS" and worst_div <= PRED["P5_divergence_max_pct"])
         else "MISS"))
    preds["P6_G_STRUCT_exact_zero_both_rows"] = (
        "HIT" if all(g5[rk]["G_STRUCT_flow_independence"]["verdict"] == "PASS"
                     for rk in ("S", "P")) else "MISS")
    preds["P7_G_TB_trivial_baseline_FAILS_as_registered_on_PATCHED"] = (
        "HIT" if g5["P"]["G_TB_trivial_baseline"]["verdict"] == "PASS" else "MISS")
    tot = g10["total_core_min"]
    preds["P8_total_core_min_band"] = (NOT_MEASURED if g10["not_measured"] else
                                       ("HIT" if PRED["P8_core_min_band"][0] <= tot <= PRED["P8_core_min_band"][1]
                                        else "MISS"))
    mw = rows["MESH"].get("wall_s")
    preds["P8b_mesh_wall_le_120s"] = (NOT_MEASURED if mw is None else
                                      ("HIT" if mw <= PRED["P8b_mesh_wall_s_max"] else "MISS"))
    solver_arms = [a for a in ARMS_REQUIRED if ARM_KIND[a] == "SOLVER"]
    dres = g1["datum_resolution"]
    preds["P9_age_datum_resolves_to_the_COMPRESSED_twin_on_every_solver_arm"] = (
        "HIT" if all(dres[a]["is_compressed_twin"] for a in solver_arms) else "MISS")
    xcm = [rows[a].get("core_min") for a in ("X-S", "X-P")]
    preds["P10_X_arm_cheap_no_flow_adjoint_per_constraint_row"] = (
        NOT_MEASURED if any(v is None for v in xcm) else
        ("HIT" if max(xcm) <= PRED["P10_X_arm_core_min_max"] else "MISS"))

    # ---- item verdict (composition registered in PREREGISTRATION.md section 3) -----
    rowv = (g5["S"]["row_verdict"], g5["P"]["row_verdict"])
    if "NOT A RESULT" in rowv:
        verdict = "NOT A RESULT"
    elif "GATE FAIL" in rowv + (gm2, gcv["verdict"], gcdim["verdict"], g9["verdict"],
                                g10["verdict"], g12["verdict"]):
        verdict = "GATE FAIL"
    else:
        verdict = "PASS"
    if verdict not in VOCAB:
        refuse("VOCAB", {"verdict": verdict})

    return {"item": "CURRICULUM-%s" % ITEM, "verdict": verdict,
            "rows": {"SHIPPED": g5["S"]["row_verdict"], "PATCHED": g5["P"]["row_verdict"]},
            "gates": {"G1_completion": "PASS", "G-M2_mesh_identity": gm2,
                      "G-CDIM_constraint_dimensions": gcdim,
                      "G-CV_constraint_feasibility": gcv,
                      "G5g_SHIPPED": g5["S"], "G5g_PATCHED": g5["P"],
                      "G6_dot_product_duality": ("NOT MEASURED -- the tutorial exposes no "
                                                 "dot-product/duality test; named, never composed"),
                      "G9_toolchain": g9, "G10_caps": g10, "G12_placement": g12},
            "mesh_cells": cells,
            "divergence_shipped_vs_patched": {"worst_pct": worst_div, "nonzero_pairs": div,
                                              "status": "REPORTED WITH ITS NUMBER, NEVER GATED"},
            "predictions": preds, "controls": controls, "birth_register": birth_record(),
            "completion": g1,
            "not_measured": {"G1": g1["not_measured"], "G10": g10["not_measured"],
                             "G12": g12["not_measured"]},
            "field_classes": {"physics": list(FIELDS_PHYSICS),
                              "infrastructure": list(FIELDS_INFRASTRUCTURE),
                              "rule": ("absent infrastructure -> NOT_MEASURED beside the verdict; "
                                       "absent physics -> REFUSE (L-342)")},
            "no_gci": "no grid family; standing rule 5 has no row; NO GCI IS QUOTED",
            "age_datum_resolution": g1["datum_resolution"],
            "rule4_clauses_per_arm": g1["rule4_clauses"],
            "rc_inferences": g1["rc_inferences"],
            "capability_grid_cell": ("2D . steady . incompressible -- gradients computed + "
                                     "FD-verified.  This item moves ONLY that column, and adds "
                                     "the GEOMETRIC CONSTRAINT Jacobians d(thickcon,volcon,rcon)"
                                     "/d(shape), which no record in this lab had FD-verified")}


# ===================== the fixture: BUILT BY THE INSTRUMENT'S OWN WRITERS ==============
REFDIR = os.path.join(_HERE, "reference")
REAL_CHECKMESH = os.path.join(REFDIR, "REAL_SO1a_MESH_checkMesh.log")
REAL_ARMLOG = os.path.join(REFDIR, "REAL_SO1a_X-S_arm.log")
LAUNCHER = os.path.join(_HERE, "so2a_run_arm.sh")

# A synthetic but STRUCTURED Jacobian: entry (constraint, output i, shape j) is
# distinct across BOTH indices, so a reader that collapses a dimension, and a
# trivial baseline that cannot tell components apart, both show up.
def _jval(cn, i, j):
    base = {"thickcon": 0.11, "volcon": 0.37, "rcon": 0.53}[cn]
    return base * (1.0 + 0.31 * i) * (1.0 + 0.79 * j) * (-1.0 if (i + j) % 3 == 0 else 1.0)


def _con_base(cn, n):
    return [1.0 for _ in range(n)]


def _ledger_rows_via_launcher(k):
    """R1's BIRTH: the fixture's ledger rows are emitted by SOURCING the LAUNCHER'S
    OWN `so2a_ledger_row` function -- the real producer's code -- not by a copy of
    its format string here.  If the launcher's format and this reader's regex ever
    diverge, this returns rows the reader cannot parse and the suite fails loudly.
    Returns None (and the caller records NOT BORN) if the launcher is absent."""
    if not os.path.isfile(LAUNCHER):
        return None
    lines = []
    for arm in ARMS_REQUIRED:
        ke = NOT_MEASURED if arm in k["rc_record"] else k["ke"].get(arm, k["rc"][arm])
        cmd = ('. %s --source-only >/dev/null 2>&1; '
               'so2a_ledger_row %s %s img %s %d 60 %d %s %s 600 %s 4g "%s %s" 20.00 %s %s '
               '"%s" "" "" %s x'
               % (LAUNCHER, arm, ARM_ROW[arm], IMG_DIGEST[ARM_ROW[arm]], k["rc"][arm],
                  ARM_RANKS[arm], k["cm"][arm], CAPS[arm], CAPS[arm], ke, k["oom"][arm],
                  k["mpost"], k["cs"][arm], k["dl"], "%s_x.log" % arm))
        p = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
        out = p.stdout.strip()
        if not out.startswith("ARM="):
            return None
        lines.append(out + "\n")
    return lines


def _fix(tmp, tweak=None):
    """Build a clean fixture.

    EVERY ARTEFACT IS WRITTEN BY `so2a_xg`'s OWN WRITERS and EVERY LEDGER ROW BY
    THE LAUNCHER'S OWN FUNCTION.  Nothing here hand-rolls a schema.  That is the
    birth requirement's structural half: a fixture cannot carry a key the producer
    does not emit, nor miss one it does."""
    k = {"rc": {a: 0 for a in ARMS_REQUIRED}, "ke": {}, "oom": {a: "false" for a in ARMS_REQUIRED},
         "cm": dict(PREDICTED_CORE_MIN), "cs": {a: CPUSET_REGISTERED for a in ARMS_REQUIRED},
         "so": {a: SO_MD5[ARM_ROW[a]] for a in ARMS_REQUIRED}, "cells": CELLS_EXPECTED,
         "err": {"S": {}, "P": {}},            # (cn, i, dv, idx) -> extra % error on the FD ref
         "flip": {"S": set(), "P": set()},     # (cn, i, dv, idx) FD reference sign-flipped
         "noplateau": {"S": set(), "P": set()},
         "nearzero": {"S": set(), "P": set()},
         "struct_nz_adj": {"S": None, "P": None},   # (cn, i, k) -> value, adjoint side
         "struct_nz_fd": {"S": None, "P": None},    # (cn, i) -> value, FD side
         "flat_jac": set(),                    # rows whose Jacobian is CONSTANT across shape idx
         "sizes": dict(CON_SIZES_EXPECTED),
         "terminal": {a: True for a in ARMS_REQUIRED}, "stale": set(), "ctrl": "ok",
         "mpost": "20.00", "drop_row": set(), "inspect_file": set(), "rc_record": set(),
         "fatal": {}, "real_log": {},
         "datum": {a: ("plain" if a == "MESH" else "gz") for a in ARMS_REQUIRED},
         "write_compression": "on", "con_base": {cn: None for cn in CON_NAMES},
         "dl": "0.99 n=10 max_nr_throttled=0", "ledger_via_launcher": True}
    if tweak:
        tweak(k)
    root = os.path.join(tmp, "root_%d" % int(time.time() * 1e6))
    os.makedirs(root)
    ident_of = {a: {"libidwarp_so_md5": k["so"][a], "idwarp_file": "/x/idwarp/__init__.py",
                    "write_compression": k["write_compression"]} for a in ARMS_REQUIRED}

    for arm in ARMS_REQUIRED:
        d = os.path.join(root, arm)
        tdir = "0.orig" if arm == "MESH" else "0"
        os.makedirs(os.path.join(d, tdir))
        os.makedirs(os.path.join(d, "system"), exist_ok=True)
        open(os.path.join(d, CONTROLDICT_REL), "w").write(
            "writeFormat     ascii;\nwriteCompression %s;\n" % k["write_compression"])
        plain = os.path.join(d, tdir, "U")
        open(plain, "w").write("U\n")
        t0 = int(os.path.getmtime(plain))
        open(os.path.join(d, DATUM_FILE), "w").write("%d\n" % t0)
        kind = k["datum"][arm]
        if kind == "gz":
            os.remove(plain)
            gz = plain + ".gz"
            open(gz, "w").write("U compressed\n")
            os.utime(gz, (t0 + 3, t0 + 3))
        elif kind == "none":
            os.remove(plain)

        log = "%s_x.log" % arm
        text = ("D4S_CONTAINER_UID: 0\nD4S_IDWARP_SO_MD5: %s\nD4S_DEADLINE_IN_CONTAINER_S: 600\n"
                % k["so"][arm])
        if arm in k["real_log"]:
            text += open(REAL_ARMLOG, errors="replace").read()

        if arm == "MESH":
            art = os.path.join(d, "checkMesh.log")
            # R3's negative direction runs on REAL checkMesh BYTES wherever the
            # fixture wants the registered count; only the count is substituted.
            real = open(REAL_CHECKMESH, errors="replace").read()
            open(art, "w").write(re.sub(r"^(\s*cells:\s+)\d+", r"\g<1>%d" % k["cells"], real,
                                        count=1, flags=re.M))
        else:
            rk = ROW_OF[arm]
            sizes = dict(k["sizes"])
            cb = {cn: (k["con_base"][cn] if k["con_base"][cn] is not None
                       else _con_base(cn, sizes[cn])) for cn in CON_NAMES}
            art = os.path.join(d, ARTEFACT[arm])
            if arm.startswith("X"):
                jac = {}
                for cn in CON_NAMES:
                    flat_s, flat_p = [], []
                    for i in range(sizes[cn]):
                        for jj in range(8):
                            v = _jval(cn, i, 0 if (cn, i) in k["flat_jac"] else jj)
                            flat_s.append(repr(v))
                        for kk in range(2):
                            nz = k["struct_nz_adj"][rk]
                            v = nz[3] if (nz and nz[0] == cn and nz[1] == i and nz[2] == kk) else 0.0
                            flat_p.append(repr(v))
                    jac[cn] = {"shape": flat_s, "patchV": flat_p}
                rec = XG.build_X_record(1, XG.PRODUCER_MD5, ident_of[arm], cb, sizes, jac,
                                        0.0209, 0.50, 1.23)
                json.dump(rec, open(art, "w"), indent=1, sort_keys=True)
            else:
                rows_ = []
                for dv, idx in SHAPE_COMPONENTS + PATCHV_COMPONENTS:
                    fd = {}
                    for s in STEPS_REGISTERED[dv]:
                        mid = sorted(STEPS_REGISTERED[dv])[1]
                        plus, minus = {}, {}
                        for cn in CON_NAMES:
                            pv, mv = [], []
                            for i in range(sizes[cn]):
                                if dv == "patchV":
                                    nz = k["struct_nz_fd"][rk]
                                    dref = nz[2] if (nz and nz[0] == cn and nz[1] == i) else 0.0
                                else:
                                    j = _jval(cn, i, 0 if (cn, i) in k["flat_jac"] else idx)
                                    e = k["err"][rk].get((cn, i, dv, idx), 0.5)
                                    dref = j * (1.0 + e / 100.0)
                                    if (cn, i, dv, idx) in k["flip"][rk]:
                                        dref = -dref
                                    if (cn, i, dv, idx) in k["nearzero"][rk]:
                                        dref = 0.0
                                    if s != mid:
                                        dref *= (1.5 if (cn, i, dv, idx) in k["noplateau"][rk]
                                                 else 1.01)
                                # a central difference of `dref` at step s
                                pv.append(dref * s)
                                mv.append(-dref * s)
                            plus[cn], minus[cn] = pv, mv
                        fd[repr(s)] = XG.build_fd_row(s, plus, minus)
                    rows_.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd})
                ctrl = XG.build_ctrl_row(cb)
                if k["ctrl"] == "dead":
                    for cn in CON_NAMES:
                        ctrl["planted"]["d"][cn] = [repr(0.0)] * sizes[cn]
                elif k["ctrl"] == "empty":
                    for cn in CON_NAMES:
                        ctrl["fd"][repr(CTRL_STEP)]["d"][cn] = []
                        ctrl["planted"]["d"][cn] = []
                elif k["ctrl"] == "absent":
                    ctrl = None
                if ctrl is not None:
                    rows_.append(ctrl)
                rec = XG.build_F_record(1, XG.PRODUCER_MD5, ident_of[arm], cb, cb, sizes, rows_,
                                        0.0, XG.ETA_FLOOR, True, 0.0209, 0.50,
                                        {"shape": [repr(0.0)] * 8, "patchV": [repr(10.0), repr(5.139)]})
                json.dump(rec, open(art, "w"), indent=1, sort_keys=True)
            if k["terminal"][arm]:
                text += TERMINAL[arm] + " ok\n"
        if arm in k["fatal"]:
            text += k["fatal"][arm] + "\n"
        os.utime(art, (t0 - 5, t0 - 5) if arm in k["stale"] else (t0 + 5, t0 + 5))
        open(os.path.join(root, log), "w").write(text)
        if arm in k["inspect_file"]:
            # THE SURVIVING KERNEL RECORD CARRIES THE REAL VALUE.  `rc_record`
            # suppresses the LEDGER row's field only -- that is what R-RC's
            # "absent from BOTH channels" means, and a fixture that blanked both
            # channels at once could never drive the FALLBACK it exists to test.
            ke = k["ke"].get(arm, k["rc"][arm])
            open(os.path.join(root, "%s_x.inspect.txt" % arm), "w").write(
                "%s %s 2026-08-28T00:00:00Z 2026-08-28T00:01:00Z %s 4294967296 %s\n"
                % (ke, k["oom"][arm], k["cs"][arm], IMG_DIGEST[ARM_ROW[arm]]))

    led = ["ITEM=SO2a\n", "STAGED stamp=x\n"]
    rows_out = _ledger_rows_via_launcher(k) if k["ledger_via_launcher"] else None
    if rows_out is None:
        READERS["R1_read_ledger"]["born"] = False
        READERS["R1_read_ledger"]["not_born_reason"] = (
            "so2a_run_arm.sh:so2a_ledger_row could not be sourced; the fixture fell back to a "
            "hand-written row, which cannot catch a launcher/reader format divergence")
        rows_out = [("ARM=%s ROW=%s IMG=img DIGEST=%s rc=%d wall_s=60 ranks=%d core_min=%s "
                     "cap_core_min=%s enforced_wall_s=600 enforced_core_min=%s memory=4g "
                     "inspect(exit,oomkilled)=[%s %s] memavail_pre_GiB=20.00 "
                     "memavail_post_GiB=%s cpuset=%s delivered_cores_mean=[%s] siblings_pre=[] "
                     "siblings_post=[] log=%s_x.log stamp=x\n")
                    % (a, ARM_ROW[a], IMG_DIGEST[ARM_ROW[a]], k["rc"][a], ARM_RANKS[a],
                       k["cm"][a], CAPS[a], CAPS[a],
                       NOT_MEASURED if a in k["rc_record"] else k["ke"].get(a, k["rc"][a]),
                       k["oom"][a], k["mpost"], k["cs"][a], k["dl"], a)
                    for a in ARMS_REQUIRED]
    for a, line in zip(ARMS_REQUIRED, rows_out):
        if a not in k["drop_row"]:
            led.append(line)
    open(os.path.join(root, "ledger.txt"), "w").write("".join(led))
    return root


# ===================== the selftest ===================================================
def selftest(tmp):
    n = 0
    fails = []

    def unit(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name)
        print("  [%s] %s" % ("OK " if cond else "BAD", name))

    def refused(root):
        try:
            grade(root)
            return False
        except Refusal:
            return True

    def tw(**kw):
        def f(k):
            for key, val in kw.items():
                if isinstance(val, dict) and isinstance(k.get(key), dict):
                    k[key].update(val)
                else:
                    k[key] = val
        return f

    # ---- A. the clean fixture -----------------------------------------------------
    r = grade(_fix(tmp))
    unit("U1 clean fixture -> item PASS, both rows PASS",
         r["verdict"] == "PASS" and r["rows"] == {"SHIPPED": "PASS", "PATCHED": "PASS"})
    unit("U2 clean fixture -> G-M2, G-CDIM, G-CV, G9, G10, G12 all PASS",
         r["gates"]["G-M2_mesh_identity"] == "PASS"
         and r["gates"]["G-CDIM_constraint_dimensions"]["verdict"] == "PASS"
         and r["gates"]["G-CV_constraint_feasibility"]["verdict"] == "PASS"
         and r["gates"]["G9_toolchain"]["verdict"] == "PASS"
         and r["gates"]["G10_caps"]["verdict"] == "PASS"
         and r["gates"]["G12_placement"]["verdict"] == "PASS")
    unit("U3 clean fixture -> G-STRUCT PASS on both rows over a NON-EMPTY tuple",
         all(r["gates"]["G5g_%s" % w]["G_STRUCT_flow_independence"]["verdict"] == "PASS"
             and r["gates"]["G5g_%s" % w]["G_STRUCT_flow_independence"]["n_adjoint_entries_checked"] > 0
             and r["gates"]["G5g_%s" % w]["G_STRUCT_flow_independence"]["n_fd_entries_checked"] > 0
             for w in ("SHIPPED", "PATCHED")))
    unit("U4 clean fixture -> G-TB PASS on every constraint, ratio >= 10",
         all(r["gates"]["G5g_%s" % w]["G_TB_trivial_baseline"]["verdict"] == "PASS"
             for w in ("SHIPPED", "PATCHED"))
         and all(r["gates"]["G5g_PATCHED"]["G_TB_trivial_baseline"]["per_constraint"][cn]["ratio"]
                 >= TB_MIN_RATIO for cn in CON_NAMES))
    unit("U5 clean fixture -> 23 candidate output rows graded, all three constraints have pairs",
         all(r["gates"]["G5g_PATCHED"]["G5g_constraint_jacobians"]["per_constraint"][cn]["n_graded_pairs"] > 0
             for cn in CON_NAMES)
         and sum(r["gates"]["G5g_PATCHED"]["G5g_constraint_jacobians"]["per_constraint"][cn]["n_candidate_pairs"]
                 for cn in CON_NAMES) == 4 * sum(CON_SIZES_EXPECTED.values()))
    unit("U6 clean fixture -> all predictions HIT (P1-P10), none MISS",
         all(v == "HIT" for v in r["predictions"].values()))
    unit("U7 divergence shipped-vs-patched is REPORTED and is 0.0 on the clean fixture",
         r["divergence_shipped_vs_patched"]["worst_pct"] == 0.0)
    unit("U8 the verdict is in the fixed vocabulary and no synonym appears",
         r["verdict"] in VOCAB and r["rows"]["SHIPPED"] in VOCAB and r["rows"]["PATCHED"] in VOCAB)
    unit("U9 G6 is NAMED as NOT MEASURED and is not composed into the verdict",
         "NOT MEASURED" in r["gates"]["G6_dot_product_duality"])
    unit("U10 no GCI is quoted (no grid family)", "NO GCI IS QUOTED" in r["no_gci"])
    unit("U11 the birth register lists all seven readers and names any NOT BORN",
         len(r["birth_register"]["readers"]) == 7
         and r["birth_register"]["n_born"] + r["birth_register"]["n_not_born"] == 7)
    unit("U12 R1 was BORN through the launcher's own so2a_ledger_row (not a copied format)",
         READERS["R1_read_ledger"]["born"] is True)

    # ---- B. G5g, the bright line, planted both ways --------------------------------
    r = grade(_fix(tmp, tw(err={"S": {("volcon", 0, "shape", 3): 9.0}})))
    unit("U20 PLANTED 9 % error on shipped volcon/shape[3] -> pair GATE FAIL, SHIPPED row "
         "GATE FAIL, item GATE FAIL",
         r["rows"]["SHIPPED"] == "GATE FAIL" and r["verdict"] == "GATE FAIL"
         and r["gates"]["G5g_SHIPPED"]["G5g_constraint_jacobians"]["per_constraint"]["volcon"]["n_gate_fail"] == 1)
    unit("U21 the SAME plant leaves the PATCHED row PASS -- the rows are independent",
         r["rows"]["PATCHED"] == "PASS")
    r = grade(_fix(tmp, tw(err={"S": {("volcon", 0, "shape", 3): 4.0}})))
    unit("U22 a 4 % error is INSIDE band D -> still PASS: the band is a threshold, not a mood",
         r["rows"]["SHIPPED"] == "PASS")
    r = grade(_fix(tmp, tw(flip={"S": {("rcon", 0, "shape", 6)}, "P": set()})))
    unit("U23 PLANTED sign flip -> GATE FAIL regardless of magnitude, flip COUNTED",
         r["rows"]["SHIPPED"] == "GATE FAIL"
         and r["gates"]["G5g_SHIPPED"]["G5g_constraint_jacobians"]["per_constraint"]["rcon"]["sign_flips"] == 1)
    r = grade(_fix(tmp, tw(noplateau={"S": {("rcon", 0, "shape", 6)}, "P": set()})))
    unit("U24 PLANTED no-plateau -> the pair is EXCLUDED and NAMED, not silently graded",
         r["gates"]["G5g_SHIPPED"]["G5g_constraint_jacobians"]["per_constraint"]["rcon"]
          ["excluded_by_reason"].get("NO_PLATEAU") == 1)
    r = grade(_fix(tmp, tw(nearzero={"S": {("volcon", 0, "shape", 0)}, "P": set()})))
    unit("U25 PLANTED near-zero FD reference -> EXCLUDED and NAMED as NEAR_ZERO",
         r["gates"]["G5g_SHIPPED"]["G5g_constraint_jacobians"]["per_constraint"]["volcon"]
          ["excluded_by_reason"].get("NEAR_ZERO") == 1)
    r = grade(_fix(tmp, tw(nearzero={"S": {("volcon", 0, "shape", 0), ("volcon", 0, "shape", 3),
                                           ("volcon", 0, "shape", 6)}, "P": set()})))
    unit("U26 3 of volcon's 4 pairs excluded (75 % is NOT > 75 %) -> still graded on 1 pair, "
         "but MIN_GRADED_PER_CONSTRAINT = 2 makes it NOT A RESULT",
         r["gates"]["G5g_SHIPPED"]["G5g_constraint_jacobians"]["per_constraint"]["volcon"]["verdict"] == "NOT A RESULT"
         and r["rows"]["SHIPPED"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT")
    unit("U27 a NOT A RESULT row makes the ITEM NOT A RESULT, never a GATE FAIL",
         r["verdict"] == "NOT A RESULT")

    # ---- C. G-TB, the cyclic-shift trivial baseline ---------------------------------
    r = grade(_fix(tmp, tw(flat_jac={("volcon", 0)})))
    unit("U30 A JACOBIAN ROW CONSTANT ACROSS THE SHAPE COMPONENTS -> the shift changes "
         "nothing, ratio -> 1, G-TB GATE FAIL",
         r["gates"]["G5g_PATCHED"]["G_TB_trivial_baseline"]["per_constraint"]["volcon"]["verdict"] == "GATE FAIL")
    unit("U31 a G-TB GATE FAIL WITHDRAWS the row to NOT A RESULT (charter s4 direction)",
         r["rows"]["PATCHED"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT")
    unit("U32 G-TB reports the SHIFT-PASSING FRACTION beside the ratio, and says it is not gated",
         "reported_not_gated" in r["gates"]["G5g_PATCHED"]["G_TB_trivial_baseline"]
          ["per_constraint"]["thickcon"])
    unit("U33 on the clean fixture the shift is at least 10x worse on EVERY constraint",
         all(grade(_fix(tmp))["gates"]["G5g_SHIPPED"]["G_TB_trivial_baseline"]
             ["per_constraint"][cn]["ratio"] >= TB_MIN_RATIO for cn in CON_NAMES))

    # ---- D. G-STRUCT, the exact-zero gate, and its birth ----------------------------
    r = grade(_fix(tmp, tw(struct_nz_adj={"S": ("volcon", 0, 1, 1.0e-9)})))
    unit("U34 A NON-ZERO d(volcon)/d(patchV) IN THE ADJOINT -> G-STRUCT GATE FAIL, even at 1e-9",
         r["gates"]["G5g_SHIPPED"]["G_STRUCT_flow_independence"]["verdict"] == "GATE FAIL"
         and r["gates"]["G5g_SHIPPED"]["G_STRUCT_flow_independence"]["n_adjoint_nonzero"] == 1)
    unit("U35 the same plant leaves the PATCHED row's G-STRUCT PASS",
         r["gates"]["G5g_PATCHED"]["G_STRUCT_flow_independence"]["verdict"] == "PASS")
    unit("U36 a G-STRUCT GATE FAIL makes the row GATE FAIL and the item GATE FAIL",
         r["rows"]["SHIPPED"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(struct_nz_fd={"P": ("rcon", 1, 3.0e-12)})))
    unit("U37 A NON-ZERO on the FD SIDE ALONE -> G-STRUCT GATE FAIL: both sides are checked",
         r["gates"]["G5g_PATCHED"]["G_STRUCT_flow_independence"]["verdict"] == "GATE FAIL"
         and r["gates"]["G5g_PATCHED"]["G_STRUCT_flow_independence"]["n_fd_nonzero"] > 0)

    # ---- E. rule 3 / the birth requirement, driven ----------------------------------
    def _u40():
        # NOTE, and it is a defect this lane committed and caught: the first draft
        # wrote `open(p, "w").write(open(p).read().replace(...))`.  Python builds
        # the writer BEFORE evaluating the argument, so the file was TRUNCATED and
        # the "read" returned "".  The unit failed loudly with a KeyError instead
        # of passing on an empty ledger -- which is the only reason it was caught.
        p = os.path.join(_fix(tmp), "ledger.txt")
        before = read_ledger(p)["G-S"]["core_min"]
        txt = open(p).read()
        txt2 = txt.replace("core_min=%s " % PREDICTED_CORE_MIN["G-S"], "core_min=7.777 ", 1)
        if txt2 == txt:
            return False
        open(p, "w").write(txt2)
        after = read_ledger(p)["G-S"]["core_min"]
        return before != 7.777 and after == 7.777

    unit("U40 (R1 +) the ledger reader reads back a CHANGED core_min off a row the "
         "LAUNCHER wrote, not merely the registered one", _u40())

    def _u41():
        root = _fix(tmp)
        open(os.path.join(root, "ledger.txt"), "a").write("ARM=G-S ROW=SHIPPED IMG=x nonsense\n")
        return refused(root)

    unit("U41 (R1 -) a PRESENT-BUT-GARBAGE ledger row REFUSES, never skips", _u41())
    real_cm = open(REAL_CHECKMESH, errors="replace").read()
    real_arm = open(REAL_ARMLOG, errors="replace").read()
    s_cm, b_cm = fatal_token_sites(real_cm, "REAL_checkMesh")
    s_arm, b_arm = fatal_token_sites(real_arm, "REAL_arm")
    unit("U50 (R2 -) THE DEFECT SO-1a DIED OF, ON THE REAL BYTES: SO-1a's own checkMesh.log "
         "carries the banner at line 18 and produces ZERO fatal sites and EXACTLY ONE "
         "counted benign exclusion",
         len(s_cm) == 0 and len(b_cm) == 1 and b_cm[0]["line"] == 18
         and "Floating point exception" in b_cm[0]["tokens"])
    unit("U51 (R2 -) SO-1a's REAL X-S arm log -- the file its refusal CITED -- carries the "
         "token ZERO times, which is why naming it was a reader defect",
         len(s_arm) == 0 and len(b_arm) == 0)
    unit("U52 (R2 +) a REAL SIGFPE STACK LINE planted into those same real bytes IS SEEN, "
         "with its file and line named",
         (lambda sp: len(sp) == 1 and sp[0]["file"] == "P"
          and "Foam::sigFpe::sigHandler" in sp[0]["tokens"])(
             fatal_token_sites(real_cm + "\n#1  Foam::sigFpe::sigHandler(int) at ??:?\n", "P")[0]))
    unit("U53 (R2 +) EVERY registered token is seen when planted on its own line -- the "
         "line split loses no match",
         all(len(fatal_token_sites(real_cm + "\nxx %s yy\n" % t, "P")[0]) == 1
             for t in FATAL_TOKENS if t != "Floating point exception")
         and len(fatal_token_sites(real_cm + "\nprocess exited on Floating point exception\n",
                                   "P")[0]) == 1)
    unit("U54 (R3 +) the cells reader reads the PLANTED count off REAL checkMesh bytes "
         "with the count changed -- it is not returning a constant",
         (lambda c: c["read_back"] == c["on_disk_before_plant"] + 7
                    and c["read_back"] != CELLS_EXPECTED)(
             grade(_fix(tmp))["controls"]["grader_plant_cells"]))
    unit("U55 (R3 -) the cells reader reads 4032 off the UNCHANGED real bytes",
         read_mesh_cells(REAL_CHECKMESH) == CELLS_EXPECTED)
    r = grade(_fix(tmp))
    unit("U56 (R4 +) the X reader reads back a PLANTED patchV Jacobian entry",
         r["controls"]["grader_plant_X_struct_S"]["grader_plant_X_seen"] is True)
    unit("U57 (R4 +) AND G-STRUCT FLIPS TO GATE FAIL ON THAT PLANTED COPY -- the zero-reader's "
         "birth, both directions, at GRADE TIME",
         r["controls"]["grader_plant_X_struct_S"]["g_struct_flipped_to"] == "GATE FAIL"
         and r["controls"]["grader_plant_X_struct_P"]["g_struct_flipped_to"] == "GATE FAIL")
    def _u58():
        root = _fix(tmp)
        p = os.path.join(root, "X-S", XG.OUT_X)
        j = json.load(open(p))
        j["jacobian"]["volcon"]["shape"].pop()
        json.dump(j, open(p, "w"))
        return refused(root)

    unit("U58 (R4 -) a Jacobian whose flat length is not divisible by the recorded size REFUSES",
         _u58())
    unit("U59 (R5 +) the F reader sees PLANT added to EVERY derivative entry of EVERY "
         "constraint, and the count of moved values is > 0",
         r["controls"]["grader_plant_F_S"]["n_values"] > 0
         and r["controls"]["grader_plant_F_S"]["worst_residual"] <= 1e-12)
    unit("U60 (R5 -) A DEAD PLANT IN THE INSTRUMENT'S CONTROL ROW REFUSES: the planted "
         "derivative reads 0.0 where PLANT/(2h) was written",
         refused(_fix(tmp, tw(ctrl="dead"))))
    unit("U61 (R6 +) the constraint-baseline reader sees a MOVED baseline: volcon at 0.4 "
         "VIOLATES its lower bound of 1.0 and G-CV GATE FAILs",
         (lambda rr: rr["gates"]["G-CV_constraint_feasibility"]["verdict"] == "GATE FAIL"
          and rr["verdict"] == "GATE FAIL"
          and rr["predictions"]["P3_G_CV_feasible_at_the_graded_design"] == "MISS")(
             grade(_fix(tmp, tw(con_base={"volcon": [0.4]})))))
    unit("U62 (R6 -) volcon EXACTLY ON its lower bound of 1.0 is SATISFIED to FEAS_TOL and "
         "is reported ACTIVE -- the tolerance is stated, not implied",
         r["gates"]["G-CV_constraint_feasibility"]["per_constraint"]["volcon"]["verdict"] == "PASS"
         and r["gates"]["G-CV_constraint_feasibility"]["per_constraint"]["volcon"]
              ["indices_ACTIVE_at_a_bound"] == [0])
    unit("U63 (R7 +) a STALE artefact -- older than the arm's own datum -- REFUSES",
         refused(_fix(tmp, tw(stale={"G-S"}))))
    unit("U64 (R7 -) the datum resolves to the COMPRESSED TWIN on a solver arm and to the "
         "PLAIN name on MESH, and both are RECORDED",
         r["age_datum_resolution"]["G-S"]["is_compressed_twin"] is True
         and r["age_datum_resolution"]["MESH"]["is_compressed_twin"] is False)
    unit("U65 (R7) datum absent in BOTH names REFUSES -- and ONLY then",
         refused(_fix(tmp, tw(datum={"G-S": "none"}))))
    unit("U66 A CONTROL THAT EMPTIES THE TUPLE IT TESTS IS REFUSED, NOT PASSED "
         "(Sanaa 2026-08-28)", refused(_fix(tmp, tw(ctrl="empty"))))
    unit("U67 the control row absent REFUSES", refused(_fix(tmp, tw(ctrl="absent"))))

    # ---- F. G1, the five rule-4 clauses, and R-RC -----------------------------------
    r = grade(_fix(tmp))
    unit("U70 the five rule-4 clauses are printed INDIVIDUALLY on every arm",
         all(set(r["rule4_clauses_per_arm"][a]) ==
             {"C1_rc_value", "C2_terminal_marker", "C3_artefact_present", "C4_age_guard",
              "C5_no_fatal_token"} for a in ARMS_REQUIRED))
    unit("U71 C5's PASS record COUNTS AND NAMES every benign exclusion -- SO-1a's checkMesh "
         "banner is excluded on the MESH arm and the count is 1, not 0",
         r["rule4_clauses_per_arm"]["MESH"]["C5_no_fatal_token"]["n_benign_lines_excluded"] == 1
         and r["rule4_clauses_per_arm"]["MESH"]["C5_no_fatal_token"]["benign_lines_excluded"][0]["line"] == 18)
    unit("U72 A REAL FATAL TOKEN AT rc = 0 REFUSES -- C5 never launders a crash",
         refused(_fix(tmp, tw(fatal={"G-S": "--> FOAM FATAL ERROR: something"}))))
    unit("U73 A REAL SIGFPE SITTING BESIDE THE BENIGN BANNER STILL REFUSES -- per-line, so "
         "line 18 cannot suppress line 400",
         refused(_fix(tmp, tw(fatal={"G-S": ("trapFpe: Floating point exception trapping "
                                             "enabled (FOAM_SIGFPE).\n#1  "
                                             "Foam::sigFpe::sigHandler(int) at ??:?")}))))
    unit("U74 THE BANNER ALONE, at rc = 0, DOES NOT REFUSE -- the SO-1a defect, driven",
         grade(_fix(tmp, tw(fatal={"G-S": "trapFpe: Floating point exception trapping "
                                          "enabled (FOAM_SIGFPE)."})))["verdict"] == "PASS")
    unit("U75 THE BANNER PLANTED INTO A REAL 690-LINE ARM LOG STILL DOES NOT REFUSE, and "
         "the exclusion is counted on that arm",
         (lambda rr: rr["verdict"] == "PASS"
          and rr["rule4_clauses_per_arm"]["G-S"]["C5_no_fatal_token"]["n_benign_lines_excluded"] == 1)(
             grade(_fix(tmp, tw(real_log={"G-S": True},
                                fatal={"G-S": "trapFpe: Floating point exception trapping "
                                              "enabled (FOAM_SIGFPE)."})))))
    unit("U76 a missing terminal marker REFUSES", refused(_fix(tmp, tw(terminal={"G-S": False}))))
    unit("U77 a non-zero rc REFUSES", refused(_fix(tmp, tw(rc={"G-S": 1}, ke={"G-S": 1}))))
    unit("U78 a harness/kernel rc DISAGREEMENT REFUSES", refused(_fix(tmp, tw(ke={"G-S": 1}))))
    unit("U79 OOMKilled true REFUSES (G11), never a re-fire",
         refused(_fix(tmp, tw(oom={"G-S": "true"}))))
    unit("U80 R-RC: the rc RECORD absent from BOTH channels while C2-C5 hold reads "
         "NOT MEASURED and prints the INFERENCE; the verdict is unchanged",
         (lambda rr: rr["verdict"] == "PASS"
          and rr["rule4_clauses_per_arm"]["G-S"]["C1_rc_value"]["verdict"] == NOT_MEASURED
          and rr["rc_inferences"]["G-S"]["inferred_rc"] == 0
          and "INFERENCE" in rr["rc_inferences"]["G-S"]["status"])(
             grade(_fix(tmp, tw(rc_record={"G-S"})))))
    unit("U81 R-RC: rc RECORD absent AND C2 fails -> REFUSAL, not a relaxation",
         refused(_fix(tmp, tw(rc_record={"G-S"}, terminal={"G-S": False}))))
    unit("U82 R-RC: rc RECORD absent but the HARNESS rc reads NON-ZERO -> REFUSAL. "
         "R-RC relaxes a missing record, never a positive reading of failure",
         refused(_fix(tmp, tw(rc_record={"G-S"}, rc={"G-S": 1}))))
    unit("U83 R-RC: the .inspect.txt FALLBACK supplies the record and C1 is a MEASUREMENT again",
         (lambda rr: rr["rule4_clauses_per_arm"]["G-S"]["C1_rc_value"]["verdict"] == "PASS"
          and rr["rule4_clauses_per_arm"]["G-S"]["C1_rc_value"]["source"].endswith(".inspect.txt"))(
             grade(_fix(tmp, tw(rc_record={"G-S"}, inspect_file={"G-S"})))))
    unit("U84 a missing ledger row REFUSES", refused(_fix(tmp, tw(drop_row={"G-S"}))))

    # ---- G. G-M2 / G-CDIM / G9 / G10 / G12 ------------------------------------------
    unit("U85 the wrong cell count -> G-M2 GATE FAIL and P1 MISS",
         (lambda rr: rr["gates"]["G-M2_mesh_identity"] == "GATE FAIL"
          and rr["predictions"]["P1_cells_4032"] == "MISS"
          and rr["verdict"] == "GATE FAIL")(grade(_fix(tmp, tw(cells=4033)))))
    unit("U86 a constraint size that is not the producer's own arguments -> G-CDIM GATE FAIL, "
         "and the gradient grading still runs on the ACTUAL size",
         (lambda rr: rr["gates"]["G-CDIM_constraint_dimensions"]["verdict"] == "GATE FAIL"
          and rr["gates"]["G5g_SHIPPED"]["G5g_constraint_jacobians"]["per_constraint"]["rcon"]
                ["n_candidate_pairs"] == 12)(
             grade(_fix(tmp, tw(sizes={"rcon": 3})))))
    unit("U87 the WRONG image digest on a row -> G9 GATE FAIL",
         (lambda rr: rr["gates"]["G9_toolchain"]["verdict"] == "GATE FAIL")(
             grade(_fix(tmp, tw(so={"X-P": SO_MD5["SHIPPED"]})))))
    unit("U88 a cap crossing -> G10 GATE FAIL, and the ratio actual/predicted is printed",
         (lambda rr: rr["gates"]["G10_caps"]["verdict"] == "GATE FAIL"
          and rr["gates"]["G10_caps"]["per_arm"]["G-S"]["ratio_actual_over_predicted"] > 1.0)(
             grade(_fix(tmp, tw(cm={"G-S": 26.0})))))
    unit("U89 the item ceiling equals the sum of the caps",
         abs(sum(CAPS.values()) - ITEM_CEILING_CORE_MIN) < 1e-9)
    unit("U90 the wrong cpuset -> G12 GATE FAIL",
         (lambda rr: rr["gates"]["G12_placement"]["verdict"] == "GATE FAIL")(
             grade(_fix(tmp, tw(cs={"G-S": "3"})))))
    unit("U91 at np = 1 the delivered-cores floor is NOT composed (0.99 < 1.5 and G12 PASSES)",
         grade(_fix(tmp))["gates"]["G12_placement"]["verdict"] == "PASS")
    unit("U92 P10 MISSES when the X arm costs more than the registered 3.0 core-min -- the "
         "flow-adjoint-per-constraint-row regime",
         grade(_fix(tmp, tw(cm={"X-S": 8.0})))["predictions"]
         ["P10_X_arm_cheap_no_flow_adjoint_per_constraint_row"] == "MISS")

    # ---- H. the comparator's own hygiene --------------------------------------------
    unit("U95 NO `assert` carries a guard in the comparator or the instrument (L-332)",
         count_asserts(__file__) == 0 and count_asserts(XG.__file__.replace(".pyc", ".py")) == 0)
    unit("U96 the assert counter is shown COUNTING a planted assert -- a zero from a counter "
         "not shown able to count is not evidence",
         (lambda p: (open(p, "w").write("assert 1 == 1\nx = 2\n"), count_asserts(p) == 1)[1])(
             os.path.join(tmp, "planted_assert.py")))
    unit("U97 (-) THE BARE-SUBSTRING SCAN IS GONE FROM EVERY GRADING PATH IN THIS FILE: "
         "the AST detector finds ZERO functions that test FATAL_TOKENS against unsplit text",
         whole_file_token_scan_sites(__file__) == [])
    _anc = os.path.join(os.path.dirname(_HERE), "curriculum_SO1a", "so1a_grade.py")
    unit("U97b (+) THE SAME DETECTOR, ON THE KNOWN POSITIVE: SO-1a's frozen grader is "
         "FLAGGED at `fatal_tokens_in` -- so U97's zero is a claim about the code, not "
         "about the pattern (L-400).  If the ancestor is not on disk the unit FAILS rather "
         "than passing on an unmeasured zero",
         os.path.isfile(_anc) and whole_file_token_scan_sites(_anc) == ["fatal_tokens_in"])
    unit("U98 the token is STILL REGISTERED (deleting it would blind C5 to a real SIGFPE)",
         "Floating point exception" in FATAL_TOKENS and "Foam::sigFpe::sigHandler" in FATAL_TOKENS)
    unit("U99 EXACTLY ONE benign exclusion is registered, and it is the trapFpe prefix",
         len(BENIGN_LINE_PATTERNS) == 1 and BENIGN_LINE_PATTERNS[0][0] == r"^\s*trapFpe:\s")
    unit("U100 DISARMING THE EXCLUSION REPRODUCES SO-1a's REFUSAL ON ITS OWN REAL BYTES -- "
         "the mutation control, with the token HARD-CODED here, not read from the constant",
         (lambda saved: (lambda: (globals().__setitem__("BENIGN_LINE_RE", ()),
                                  len(fatal_token_sites(
                                      "trapFpe: Floating point exception trapping enabled "
                                      "(FOAM_SIGFPE).\n", "M")[0]) == 1,
                                  globals().__setitem__("BENIGN_LINE_RE", saved))[1])())(BENIGN_LINE_RE))
    unit("U101 and the exclusion is BACK after the mutation -- the suite left no residue",
         len(fatal_token_sites("trapFpe: Floating point exception trapping enabled "
                               "(FOAM_SIGFPE).\n", "M")[0]) == 0)

    print("\nSELFTEST %d units, %d fail" % (n, len(fails)))
    for f in fails:
        print("  FAIL: %s" % f)
    if n != EXPECTED_UNITS:
        print("  UNIT COUNT %d != EXPECTED_UNITS %d -- the constant is bumped DELIBERATELY, "
              "with its reason, or the suite lost a unit" % (n, EXPECTED_UNITS))
        return 2
    return 0 if not fails else 2


def main():
    if sum(CAPS.values()) != ITEM_CEILING_CORE_MIN:
        refuse("REGISTRATION", {"ceiling_is_not_the_sum_of_caps":
                                {"sum": sum(CAPS.values()), "ceiling": ITEM_CEILING_CORE_MIN}})
    if "--selftest" in sys.argv:
        with tempfile.TemporaryDirectory() as tmp:
            return selftest(tmp)
    root = BASE
    for i, a in enumerate(sys.argv):
        if a == "--root" and i + 1 < len(sys.argv):
            root = sys.argv[i + 1]
    try:
        out = grade(root)
    except Refusal as exc:
        sys.stdout.write("NOT A RESULT -- the comparator REFUSED\n%s\n" % exc)
        return 2
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    p = os.path.join(root, "SO2a_grade_%s.json" % stamp)
    with open(p, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    sys.stdout.write("VERDICT %s  rows=%s  written=%s\n"
                     % (out["verdict"], out["rows"], p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
