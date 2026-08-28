#!/usr/bin/env python3
"""Curriculum SO-1aR COMPARATOR -- THE RE-GRADE OF SO-1a's EXISTING ARTEFACTS.

SO-1a RAN CLEANLY (5 arms, all rc = 0, OOMKilled false, chain COMPLETE 2026-08-28
02:31:32Z, 9.416 core-min against a 75.0 ceiling) and its frozen comparator returned
NOT A RESULT WITH ZERO GATES EVALUATED on a FALSE POSITIVE: `so1a_grade.py:122-125`
holds the bare substring "Floating point exception" in FATAL_TOKENS, `:420` appends
`checkMesh.log` to the C5 haystack for SCRIPT arms, and line 18 of that artefact is
OpenFOAM's ordinary startup banner

    trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).

-- a notice that FPE TRAPPING IS ENABLED, i.e. the solver is PROTECTED.  A second,
smaller defect rode along: the refusal's `log` field named the ARM log, which
contains ZERO occurrences of the token it cites (measured: 0 in
`MESH_20260828T021739Z_1709267.log`, 1 in `MESH/checkMesh.log`).

SO-1a's GATES ARE CLOSED (rule 2) and NOTHING OF SO-1a IS EDITED BY THIS FILE.  This
is a SEPARATE registration whose subject is SO-1a's EXISTING ON-DISK ARTEFACTS.
`cases/dafoam/ladder-a/A1/curriculum_SO1aR/PREREGISTRATION.md` governs.

THE ONE INSTRUMENT CHANGE, AND NOTHING BEYOND IT -- C5, PORTED VERBATIM IN SHAPE
FROM `curriculum_SO1c/so1c_grade.py` AMENDMENT R6 (commit 42c7c8c3), NOT REINVENTED:
  * FATAL_TOKENS keeps EVERY original token and ADDS the handler symbol
    `Foam::sigFpe::sigHandler` (adopted from `sdk/chief_engineer/head_engineer.py:188`),
    which STRENGTHENS detection.  That file's `^` LINE ANCHOR IS DELIBERATELY NOT
    ADOPTED -- see BENIGN_LINE_PATTERNS for the measured reason.
  * `fatal_token_sites(text, source)` scans LINE BY LINE and PER SOURCE FILE, so a
    refusal names the FILE AND LINE that actually carry the hit.
  * BENIGN_LINE_PATTERNS holds exactly ONE entry, applied PER LINE, so a benign
    banner on line 18 can NEVER suppress a real crash on line 400.
  * EVERY EXCLUSION IS COUNTED AND PRINTED ON THE PASS RECORD.  A suppression a
    reader cannot see is the same defect wearing the other hat.

EVERY OTHER GATE, THRESHOLD, BAND, CAP, PREDICTION AND LABEL IS SO-1a's, UNCHANGED.
The registered deltas are in `so1ar_grade_DELTAS_from_so1a_grade.diff`.

WHAT A RE-GRADE MAY NOT CONCLUDE (PREREGISTRATION.md section 8): it re-grades
artefacts produced under SO-1a's launcher and buys NOTHING about reproducibility,
NOTHING about the mesh beyond what SO-1a's own MESH arm wrote, and NOTHING SO-1a's
own scope excluded.  It is a READING of bought compute, not a new measurement.

--- SO-1a's own header follows, unchanged except where a delta is marked ---

Curriculum SO-1a COMPARATOR -- NACA0012 INCOMPRESSIBLE drag-min-at-fixed-lift,
the FD-VERIFIED GRADIENT RUNG of Sanaa's shape-optimisation ladder SO-1.  TWO ROWS
(SHIPPED + PATCHED), adjoint X against a central-FD table F, on BOTH the objective
`CD` AND the EQUALITY-CONSTRAINT `CL`.  FROZEN by md5 in PREREGISTRATION.md section 7
before any container starts.  Computes nothing about physics; renders verdicts from
the FIXED vocabulary only (PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING).

DERIVED from `curriculum_D15/d15_grade.py` (md5 b429ec89e7a738647081783b8b755711)
with the registered deltas in so1a_grade_DELTAS_from_d15_grade.diff.  FIVE of them
are new machinery rather than renaming, and each closes a MEASURED failure:

  (A) THE AGE-GUARD DATUM IS RESOLVED BY EXISTENCE, NEVER BY NAME.  AV-1 and AV-2
      both returned NOT A RESULT this session -- 12 arms, 9.102 + 4.9 core-min of
      intact physics thrown away -- because their frozen graders pinned
      `DATUM_REF = "0/U"` while the tutorial's `writeCompression on` rewrites that
      file as `0/U.gz` on a SERIAL arm.  The guard's SUBSTANCE was satisfied on
      every refused arm (the artefact WAS strictly newer than the datum); only the
      reference PATH had vanished.  Here `resolve_datum_ref()` accepts EITHER name,
      RECORDS which one it found, cross-checks it against `writeCompression` read
      from the arm's OWN `system/controlDict`, and REFUSES only when NEITHER name
      exists.  That refusal is DRIVEN in the selftest (U24) -- swapping one
      hard-coded name for another would have been the same defect one release later.

  (B) R-RC, AS SANAA APPROVED IT 2026-08-27 (directives section 0).  The rc VALUE is
      physics; the rc RECORD is infrastructure.  Rule 4 is decomposed into FIVE
      clauses PRINTED INDIVIDUALLY per arm -- C1 rc value, C2 terminal marker (this
      item's `End` line), C3 artefact present (this item's `fields present`), C4 age
      guard, C5 no fatal token.  When the rc RECORD is absent from BOTH channels
      (the ledger row's `inspect(exit,oomkilled)` and the surviving
      `<ARM>_<stamp>.inspect.txt`), the rc value reads `NOT MEASURED` **only when
      C2-C5 all hold**, and the implied `rc = 0` is printed as an INFERENCE, never
      graded as a measurement.  If any of C2-C5 fails, the arm REFUSES.

  (C) C5, THE FATAL-TOKEN CLAUSE, REFUSES REGARDLESS OF rc.  An arm whose log
      carries `FOAM FATAL ERROR` or a signal token is refused even at rc = 0, so the
      R-RC relaxation can never launder a crash into a NOT MEASURED.

  (D) G-TB, THE CHARTER-4 TRIVIAL BASELINE, IS GRADED.  `DAFOAM_CHARTER.md` section 4
      requires an FD gate to name its trivial baseline BEFORE its own run: for a
      DAFoam FD gate that baseline is the same probe at a step chosen to be WRONG.
      The instrument buys it (`tb` beside `fd` at h = 1e-8) and this comparator
      scores it: if the WRONG step also passes band D on 2 or more of the five
      registered components, the gate is not measuring what it claims and the G5
      verdict is WITHDRAWN to NOT A RESULT.  D15 named no trivial baseline at all.

  (E) THE CONSTRAINT GRADIENT IS GRADED AS AN EQUAL, NOT AS A FOOTNOTE.  SO-1 is
      drag-min at FIXED LIFT, so `dCL/dx` carries the constraint and is graded on
      the same registered components and the same bands as `dCD/dx`.  A row is PASS
      only if BOTH are.  A gradient rung that verifies only the objective cannot
      support a constrained optimisation, and SO-1b is registered to stop if P6
      misses.

WHAT IT GRADES (PREREGISTRATION.md section 3):
  G1   completion, ARM-KIND AWARE and R-RC AWARE: the five rule-4 clauses above,
       printed individually per arm.  Any clause failing -> REFUSE (NOT A RESULT).
  G-M2 mesh identity: cells == 4,032 -> PASS else GATE FAIL.
  G5   per ROW, the bright line on CD; G5c the same on CL.  Per registered
       component the FD reference is the MIDDLE step of the registered three;
       PLATEAU = the middle step agrees with at least one neighbour to 10 %; band
       D = per-component <= 5.0 % with the SAME SIGN; band E = aggregate vector-
       relative <= 5.0 %.  Fewer than 3 graded components -> the row is NOT A RESULT.
  G-TB the trivial baseline (D above).  Can only turn PASS or GATE FAIL INTO
       NOT A RESULT, never the reverse.
  G6   dot-product / duality test: NOT MEASURED -- the tutorial exposes none; named.
  G9   toolchain per row by DIGEST + printed .so md5 + in-artefact .so md5.
  G10  caps: every row core_min <= its cap and the sum <= the ceiling.
  G12  placement: cpuset == the registered 9 on every row.  At np = 1 the
       delivered-cores floor does not apply and is not composed.
  DIVERGENCE shipped-vs-patched per component on the adjoint is REPORTED, never gated.

PLANTED CONTROLS ADDED BY THIS FILE (rule 3): the C5 repair is DRIVEN IN BOTH
DIRECTIONS on REAL BYTES TAKEN FROM ARTEFACTS ON DISK, never by injecting into a
helper -- (i) the REAL banner line from SO-1a's own `MESH/checkMesh.log:18`
(md5 22aa9cfa6725eb904123aefaebf63cfd) is the CLEAN fixture's default and must NOT
refuse; (ii) SO-1a's OWN FROZEN COMPARATOR is imported and run on that same fixture
root and MUST refuse on it -- the unrepaired-versus-repaired contrast IS the
evidence, executed, not described; (iii) a REAL 339-line np-4 solver log carrying
FOUR of the same banners and ZERO real fatal tokens
(`so1ar_fixture_REAL_D12R2W3_S0_solver.log`, md5 ccc4f40fa0e1c1849bb7bc15a4042d47,
copied byte-identical from D12R2W3, a run this lane did not produce) is scanned and
must yield 0 sites and 4 counted exclusions; (iv) a real `FOAM FATAL ERROR`, a real
SIGFPE stack trace and OpenMPI's `exited on signal 8 (Floating point exception)` are
each planted INTO THAT REAL LOG and must each refuse, ON THE PLANTED LINE, BESIDE
the four banners.

SO-1a's PLANTED CONTROLS (rule 3, and Sanaa's directive section 1 "every guard ships its
planted-failure proof"): (i) the instrument's CTRL component (derivative exactly 0.0)
and its PLANTED row (exactly PLANT/(2 s)) are re-read here and the grade REFUSES if
the reader cannot see them; (ii) this grader writes a copy of the F table with PLANT
added to every physical derivative into <root>/grader_controls/, re-reads it through
the same reader, and REFUSES unless every value moved by exactly PLANT; (iii) EVERY
guard added by this file is DRIVEN in --selftest by a planted fixture that makes it
fire -- the absent datum (U24), the absent rc record (U25/U26), the fatal token
(U27), the passing trivial baseline (U28), the failing constraint gradient (U30).

L-342 (Sanaa, d4d0c29d): FIELDS_PHYSICS absent -> REFUSE; FIELDS_INFRASTRUCTURE
absent -> NOT_MEASURED, disclosed beside the verdict, never composed to PASS;
present-but-garbage -> REFUSE.  R-RC moves the rc RECORD from physics to
infrastructure while leaving the rc VALUE on the physics side.  L-332: NO `assert`
anywhere; the module counts ast.Assert nodes in its own source and refuses on any.
No unconditional success print.
"""

import ast
import glob
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time

# ---- REGISTERED CONSTANTS (PREREGISTRATION.md; the document governs) ----------------
ITEM = "SO1aR"
# THE RUN ROOT IS SO-1a's, DELIBERATELY AND BY REGISTRATION.  This item grades
# artefacts SO-1a's launcher already produced; it launches nothing and writes nothing
# into the run root except its own grade JSON.  PREREGISTRATION.md section 1.
BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient"
ARMS_REQUIRED = ["MESH", "X-S", "F-S", "X-P", "F-P"]
ARM_KIND = {"MESH": "SCRIPT", "X-S": "SOLVER", "F-S": "SOLVER", "X-P": "SOLVER", "F-P": "SOLVER"}
ARM_ROW = {"MESH": "SHIPPED", "X-S": "SHIPPED", "F-S": "SHIPPED", "X-P": "PATCHED", "F-P": "PATCHED"}
# np = 1 ON EVERY ARM by registration: DAFOAM_CHARTER.md section 5 (serial before
# parallel; a gradient verified at one np is a statement about THAT np), and A4's
# 16,600x decomposition effect is removed from the chain rather than assumed absent.
ARM_RANKS = {"MESH": 1, "X-S": 1, "F-S": 1, "X-P": 1, "F-P": 1}
ARTEFACT = {"MESH": "checkMesh.log", "X-S": "so1a_X.json", "F-S": "so1a_F.json", "X-P": "so1a_X.json", "F-P": "so1a_F.json"}
TERMINAL = {"X-S": "SO1A_X_WRITTEN", "F-S": "SO1A_F_WRITTEN", "X-P": "SO1A_X_WRITTEN", "F-P": "SO1A_F_WRITTEN"}
# (A) THE AGE-GUARD DATUM IS RESOLVED BY EXISTENCE, NEVER BY NAME.  `writeCompression
# on` (this tutorial's system/controlDict:27) rewrites `0/U` as `0/U.gz` on a serial
# arm; AV-1 and AV-2 both returned NOT A RESULT on that alone this session.  BOTH
# names are candidates, in this order; the one FOUND is recorded; NEITHER present is
# the only refusal, and it is DRIVEN in the selftest.
DATUM_CANDIDATES = {"MESH": ("0.orig/U", "0.orig/U.gz"), "X-S": ("0/U", "0/U.gz"),
                    "F-S": ("0/U", "0/U.gz"), "X-P": ("0/U", "0/U.gz"), "F-P": ("0/U", "0/U.gz")}
DATUM_FILE = ".so1a_age_datum"
CONTROLDICT_REL = os.path.join("system", "controlDict")
# (C) C5: an arm whose log carries any of these is REFUSED regardless of rc, so the
# R-RC relaxation in (B) can never launder a crash into a NOT MEASURED.
#
# ===================== THE ONE INSTRUMENT CHANGE OF SO-1aR ==========================
# PORTED FROM `curriculum_SO1c/so1c_grade.py` AMENDMENT R6 (commit 42c7c8c3), which
# this lane read as a diff before porting.  NOT REINVENTED and NOT WIDENED.
FATAL_TOKENS = ("FOAM FATAL ERROR", "FOAM FATAL IO ERROR", "Segmentation fault",
                "SIGSEGV", "SIGKILL", "MPI_ABORT", "signal 9", "Signal 11",
                "Floating point exception",
                # ADOPTED FROM THE LAB'S OWN IMPLEMENTATION:
                # `sdk/chief_engineer/head_engineer.py:188` reads
                #     FPE = re.compile(r"Foam::sigFpe::sigHandler|^Floating point exception")
                # -- the handler symbol is the ONE string OpenFOAM emits only when
                # the FPE handler has actually FIRED.  It is added here as an EXTRA
                # POSITIVE token, which STRENGTHENS detection: a crash whose shell
                # line never reaches the log is still caught by its stack trace.
                # Its LINE ANCHOR is DELIBERATELY NOT adopted -- see
                # BENIGN_LINE_PATTERNS below for the measured reason.
                "Foam::sigFpe::sigHandler")

# ---- BENIGN LINES: the ONLY suppression this comparator carries ---------------------
# WHY AN EXCLUSION LIST AND NOT A POSITIVE ANCHOR.  Two other readers in this lab were
# examined before this one was written:
#   * a checkMesh certifier that simply DELETES the FPE token and leans on a required
#     `^End` marker.  RIGHT FOR ITS SCOPE, REJECTED FOR THIS ONE: C5 here also scans
#     FOUR SOLVER logs, and deleting the token is exactly the blinding this repair
#     must not do.
#   * `sdk/chief_engineer/head_engineer.py:188` matches
#     `Foam::sigFpe::sigHandler|^Floating point exception` -- a POSITIVE crash
#     signature.  ITS HANDLER SYMBOL IS ADOPTED ABOVE.  ITS LINE ANCHOR IS NOT: the
#     realistic multi-rank FPE report is OpenMPI's, e.g. `mpirun noticed that process
#     rank 2 exited on signal 8 (Floating point exception).` -- NOT line-initial and
#     carrying NO handler symbol.  `^Floating point exception` would MISS it.  An
#     over-narrow EXCLUSION costs a FALSE REFUSAL; an over-narrow POSITIVE ANCHOR
#     costs a MISSED CRASH.  The false refusal is the survivable error.
#
# WHY THE `trapFpe:` PREFIX IS SAFE TO EXCLUDE: it is the diagnostic prefix printed by
# OpenFOAM's FPE-TRAPPING SETUP code.  A crash never prefixes itself with it -- a real
# SIGFPE prints `Foam::sigFpe::sigHandler(int)` in the stack trace and `Floating point
# exception (core dumped)` from the shell, and NEITHER line begins `trapFpe:`.  Both
# are DRIVEN below as planted positives, on REAL log bytes.
#
# APPLIED PER LINE, so a benign banner on line 18 can NEVER suppress a real crash on
# line 400.  EVERY EXCLUSION IS COUNTED AND PRINTED ON THE PASS RECORD.
BENIGN_LINE_PATTERNS = (
    (r"^\s*trapFpe:\s",
     "OpenFOAM sigFpe SETUP banner -- an ENABLEMENT NOTICE, not a crash"),
)
BENIGN_LINE_RE = tuple((re.compile(_p), _why) for _p, _why in BENIGN_LINE_PATTERNS)
# ===================== END OF THE ONE INSTRUMENT CHANGE =============================
CAPS = {"MESH": 5.0, "X-S": 10.0, "F-S": 25.0, "X-P": 10.0, "F-P": 25.0}
ITEM_CEILING_CORE_MIN = 75.0
PREDICTED_CORE_MIN = {"MESH": 0.167, "X-S": 1.1, "F-S": 2.5, "X-P": 1.1, "F-P": 2.5}
CELLS_EXPECTED = 4032
FD_BAND_PCT = 5.0            # band D, per component (D4 PREREGISTRATION.md:82; D7FR:228-229)
AGG_BAND_PCT = 5.0           # band E, aggregate vector-relative (same sources)
PLATEAU_TOL_PCT = 10.0
MIN_GRADED = 3
NEAR_ZERO_ABS = 1.0e-14
COMPONENTS_REGISTERED = [["shape", 0], ["shape", 3], ["shape", 6], ["shape", 7], ["patchV", 1]]
STEPS_REGISTERED = {"shape": [1.0e-2, 1.0e-3, 1.0e-4], "patchV": [1.0e-1, 1.0e-2, 1.0e-3]}
# (D) THE CHARTER-4 TRIVIAL BASELINE, registered BEFORE its own run: the same probe
# at a step chosen to be WRONG.  At h = 1e-8 the FD numerator on a derivative of
# order 1e-2 is ~1e-10, at or below the primal repeatability eta (D15 measured
# 1.30e-10 on this mesh), so the estimate is noise.
TB_STEPS_REGISTERED = {"shape": [1.0e-8], "patchV": [1.0e-6]}
# G-TB PASSES when AT MOST this many of the five registered components pass band D
# at the WRONG step.  More than this and the gate cannot fail, so it is not evidence:
# the G5 verdict is WITHDRAWN to NOT A RESULT.
TB_MAX_PASSING = 1
CTRL_STEP = 1.0e-3
PLANT = 1.234e-03
IMG_DIGEST = {"SHIPPED": "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc",
              "PATCHED": "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"}
SO_MD5 = {"SHIPPED": "f0fcb488e0e98156575cd19548e91663", "PATCHED": "85f59e87253e0a71a813f64ca6e4c425"}
CPUSET_REGISTERED = "9"
DELIVERED_CORES_FLOOR = 1.5
PRED = {"P2_CL_band": (0.45, 0.55), "P3_CD_band": (0.015, 0.028), "P4_patched_min_pass": 5,
        "P6_patched_CL_agg_max_pct": 1.0, "P7_tb_min_failing": 4,
        "P8_core_min_band": (4.0, 22.0), "P8_mesh_wall_s_max": 120.0}
# (B) R-RC, Sanaa 2026-08-27 section 0: the rc VALUE is physics, the rc RECORD is
# infrastructure.  `rc_value` stays on the physics side; `rc_record` (the ledger row
# `inspect(exit,oomkilled)` field and the `<ARM>_<stamp>.inspect.txt` fallback) moves
# to the infrastructure side, where an absence reads NOT MEASURED -- but ONLY when
# C2-C5 all hold, which is checked per arm and printed clause by clause.
FIELDS_PHYSICS = ("rc_value", "oomkilled", "terminal_statement", "age_guard",
                  "no_fatal_token", "core_min", "cap_core_min", "DIGEST", "cpuset")
FIELDS_INFRASTRUCTURE = ("rc_record", "memavail_pre_GiB", "memavail_post_GiB", "delivered",
                         "siblings_pre", "siblings_post", "log", "wall_s")
# ---- REAL BYTES, TAKEN FROM ARTEFACTS ON DISK (PREREGISTRATION.md section 7) -------
# The C5 repair is proven on REAL LOG BYTES, never on text this lane invented.  Both
# fixtures are byte-identical copies of artefacts produced by runs, and their md5s are
# frozen here AND checked by a unit, so a fixture that drifts from the artefact it
# claims to be FAILS THE SELFTEST rather than quietly becoming a different test.
FIXTURE_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURE_CHECKMESH = os.path.join(FIXTURE_DIR, "so1ar_fixture_REAL_SO1a_MESH_checkMesh.log")
FIXTURE_SOLVERLOG = os.path.join(FIXTURE_DIR, "so1ar_fixture_REAL_D12R2W3_S0_solver.log")
FIXTURE_MD5 = {FIXTURE_CHECKMESH: "22aa9cfa6725eb904123aefaebf63cfd",
               FIXTURE_SOLVERLOG: "ccc4f40fa0e1c1849bb7bc15a4042d47"}
# SO-1a's own `MESH/checkMesh.log:18`, VERBATIM.  This ONE LINE is what returned
# NOT A RESULT on five clean arms and 9.416 core-min of intact physics.
REAL_BANNER_LINE = "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE)."
# The frozen predecessor, imported by the selftest and run on the SAME fixture root so
# the defect and the repair are executed side by side rather than described.
SO1A_FROZEN_GRADER = os.path.join(os.path.dirname(FIXTURE_DIR),
                                  "curriculum_SO1a", "so1a_grade.py")
NOT_MEASURED = "NOT_MEASURED"
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
# DELIBERATE BUMP, 35 -> 47.  SO-1a's 35 units are carried unchanged; the 19 added
# units (U36-U54) drive the C5 repair in BOTH DIRECTIONS on real bytes, execute the
# unrepaired predecessor for the contrast, check the fixtures have not drifted, and
# DRIVE THE BIRTH GATE ITSELF -- including its own failure modes (U51-U54), because a
# gate that has never been seen to close is not a gate.
EXPECTED_UNITS = 54


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


# ================= LEDGER (physics vs infrastructure, L-342) -- D5's regex ============
LEDGER_RE = re.compile(
    r"ARM=(?P<ARM>\S+)\s+ROW=(?P<ROW>\S+)\s+IMG=(?P<IMG>\S+)\s+"
    r"DIGEST=(?P<DIGEST>\S+)\s+rc=(?P<rc>-?\d+)\s+wall_s=(?P<wall_s>\d+)\s+"
    r"ranks=(?P<ranks>\d+)\s+core_min=(?P<core_min>[\d.]+)\s+"
    r"cap_core_min=(?P<cap>[\d.]+)\s+enforced_wall_s=(?P<ewall>\d+)\s+"
    r"enforced_core_min=(?P<ecore>[\d.]+)\s+memory=(?P<mem>\S+)\s+"
    r"inspect\(exit,oomkilled\)=\[(?P<inspect>[^\]]*)\]"
    r"(?:\s+memavail_pre_GiB=(?P<mempre>[\d.]+|NOT_MEASURED))?"
    r"(?:\s+memavail_post_GiB=(?P<mempost>[\d.]+|NOT_MEASURED))?"
    r"\s+cpuset=(?P<cpuset>\S+)"
    r"(?:\s+delivered_cores_mean=\[(?P<delivered>[^\]]*)\])?"
    r"(?:\s+siblings_pre=\[(?P<sibpre>[^\]]*)\])?"
    r"(?:\s+siblings_post=\[(?P<sibpost>[^\]]*)\])?"
    r"(?:\s+log=(?P<log>\S+))?")


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
               # R-RC: `inspect(exit,oomkilled)=[NOT_MEASURED ...]` is the rc RECORD
               # being ABSENT (infrastructure), carried as None so C1 applies R-RC.
               "inspect_exit": (None if (not parts or parts[0] == NOT_MEASURED) else parts[0]),
               "oomkilled": (parts[1] if len(parts) > 1 else None),
               "memavail_pre_GiB": _infra_float(g["mempre"]), "memavail_post_GiB": _infra_float(g["mempost"]),
               "cpuset": g["cpuset"], "delivered": g["delivered"], "siblings_pre": g["sibpre"],
               "siblings_post": g["sibpost"], "log": g["log"], "source": "ledger_row",
               "field_sources": {"all": "ledger_row"}, "infra_not_measured": infra_nm}
        if row["ARM"] in rows:
            refuse("ledger", {"duplicate_arm_row": row["ARM"], "note": "two records for one run is the defect"})
        rows[row["ARM"]] = row
    return rows


def inspect_file_fallback(base, arm):
    """L-342: an arm with no ledger row is read from the launcher's surviving inspect
    record `<ARM>_<stamp>.inspect.txt` (exit oom started finished cpuset memory); every
    infrastructure field NOT_MEASURED, the source named per field."""
    cands = sorted(glob.glob(os.path.join(base, "%s_*.inspect.txt" % arm)))
    if len(cands) != 1:
        refuse("G1", {"arm_absent_from_ledger": arm, "inspect_record_candidates": cands,
                      "note": "exactly one surviving inspect record may stand in for a missing "
                              "row.  R-RC covers the rc RECORD only: DIGEST, cpuset and "
                              "core_min are PHYSICS fields and have no fallback channel here."})
    parts = open(cands[0]).read().split()
    if len(parts) < 5:
        refuse("G1", {"inspect_record_unparseable": cands[0], "content": parts})
    logs = sorted(glob.glob(os.path.join(base, "%s_*.log" % arm)))
    # R-RC: a `NOT_MEASURED` exit field in the surviving record is the rc RECORD being
    # ABSENT (infrastructure), not garbage.  It is carried through as None so C1 can
    # apply the R-RC branch; anything else unparseable still refuses.
    if parts[0] == NOT_MEASURED:
        rc = None
    else:
        try:
            rc = int(parts[0])
        except ValueError:
            refuse("G1", {"inspect_record_exit_present_but_garbage": parts[0]})
    return {"ARM": arm, "ROW": ARM_ROW[arm], "IMG": None, "DIGEST": (parts[6] if len(parts) > 6 else None), "rc": rc, "wall_s": None,
            "ranks": ARM_RANKS[arm], "core_min": None, "cap_core_min": CAPS[arm],
            "enforced_core_min": CAPS[arm], "memory": parts[5] if len(parts) > 5 else None,
            "inspect_exit": (None if rc is None else parts[0]), "oomkilled": parts[1].lower(), "memavail_pre_GiB": None,
            "memavail_post_GiB": None, "cpuset": parts[4], "delivered": NOT_MEASURED,
            "siblings_pre": NOT_MEASURED, "siblings_post": NOT_MEASURED,
            "log": (os.path.basename(logs[-1]) if logs else None), "source": "inspect_record",
            "field_sources": {"rc": "inspect.txt .State.ExitCode", "oomkilled": "inspect.txt .State.OOMKilled",
                              "cpuset": "inspect.txt HostConfig.CpusetCpus", "DIGEST": "inspect.txt 7th field (launcher's GOT_DIGEST)"},
            "infra_not_measured": list(FIELDS_INFRASTRUCTURE) + ["core_min"]}


# ================= G1: COMPLETION, ARM-KIND AWARE, R-RC AWARE =========================
def read_write_compression(adir):
    """`writeCompression` from THE ARM'S OWN system/controlDict.  A reading, never
    an assumption: it is what turns `0/U` into `0/U.gz` and it is cross-checked
    against the datum reference actually found on disk."""
    cd = os.path.join(adir, CONTROLDICT_REL)
    if not os.path.isfile(cd):
        return {"write_compression": NOT_MEASURED, "write_compression_source": cd,
                "note": "controlDict absent from the arm directory"}
    for line in open(cd, errors="replace"):
        s = line.strip()
        if s.startswith("writeCompression"):
            return {"write_compression": s.rstrip(";").split()[-1], "write_compression_source": cd}
    return {"write_compression": NOT_MEASURED, "write_compression_source": cd,
            "note": "key absent from controlDict"}


def resolve_datum_ref(adir, arm, datum):
    """(A) RESOLVE THE AGE-GUARD DATUM BY EXISTENCE, NEVER BY NAME.

    AV-1 (`0b3ebaa4`) and AV-2 (`3e2cbf74`) both returned NOT A RESULT on
    2026-08-27 with every physics artefact intact, because their frozen graders
    pinned `DATUM_REF = "0/U"` and this tutorial's `writeCompression on` rewrites
    that file as `0/U.gz` on a SERIAL arm.  Measured on AV-1's own run root: X1-S
    datum 1787838035, `0/U.gz` mtime 1787838086 -- the guard's SUBSTANCE was
    satisfied (51 s newer) and only the reference PATH had vanished.

    So: try BOTH registered names in order, RECORD which one was found, and refuse
    only when NEITHER exists.  The mtime rule follows the file that was found --
    the UNCOMPRESSED name is the one the launcher touched, so it must still carry
    the recorded datum exactly; the COMPRESSED twin was written by the SOLVER
    AFTER the datum was taken, so it may only be NEWER, and `writeCompression` is
    read from the arm's own controlDict to say so on the record rather than in a
    comment."""
    wc = read_write_compression(adir)
    found = [(name, os.path.join(adir, name)) for name in DATUM_CANDIDATES[arm]
             if os.path.isfile(os.path.join(adir, name))]
    if not found:
        refuse("G1", {"age_reference_absent_in_every_registered_name": {
            "arm": arm, "candidates": [os.path.join(adir, c) for c in DATUM_CANDIDATES[arm]],
            **wc, "note": "resolved by EXISTENCE; NEITHER name is on disk, so the age "
                          "guard has no reference and the arm is NOT A RESULT"}})
    name, path = found[0]
    compressed = name.endswith(".gz")
    on_disk = int(os.path.getmtime(path))
    if not compressed:
        if on_disk != datum:
            refuse("G1", {"age_reference_moved": path, "recorded": datum, "on_disk": on_disk,
                          "resolved_name": name})
    else:
        if on_disk < datum:
            refuse("G1", {"compressed_datum_twin_older_than_the_datum": path,
                          "recorded": datum, "on_disk": on_disk, **wc})
    # the LAUNCHER also resolved the datum by existence and recorded the name it
    # used; read it as an INFORMATIONAL cross-check.  Absent -> NOT_MEASURED
    # (infrastructure), never a refusal: the grader's own resolution is authoritative.
    refp = os.path.join(adir, DATUM_FILE + "_ref")
    launcher_name = open(refp).read().strip() if os.path.isfile(refp) else NOT_MEASURED
    return {"resolved_name": name, "resolved_path": path, "is_compressed_twin": compressed,
            "launcher_recorded_datum_name": launcher_name,
            "recorded_datum_epoch": datum, "reference_mtime_epoch": on_disk,
            "candidates": list(DATUM_CANDIDATES[arm]),
            "rewritten_by_solver": bool(compressed), **wc}


def arm_datum(base, arm):
    d = os.path.join(base, arm)
    p = os.path.join(d, DATUM_FILE)
    if not os.path.isfile(p):
        refuse("G1", {"age_datum_absent": p, "arm": arm})
    datum = int(open(p).read().strip())
    return d, datum, resolve_datum_ref(d, arm, datum)


def fatal_tokens_in(text):
    """SO-1a's UNREPAIRED whole-file substring predicate, KEPT VERBATIM AND OFF THE
    GRADING PATH.  It exists so the selftest can run the DEFECT and the REPAIR on the
    SAME REAL BYTES (U48) and print the contrast, above the whole-comparator contrast
    of U39, which imports and runs SO-1a's frozen file itself.  `grade()` never calls
    it; that is CHECKED BY AST in U48, not asserted."""
    return [t for t in FATAL_TOKENS if t in text]


def benign_reason(line):
    """(C) C5, SO-1aR.  Why this ONE LINE is an enablement notice and not a crash, or
    None.  Narrow by construction: see BENIGN_LINE_PATTERNS."""
    for rx, why in BENIGN_LINE_RE:
        if rx.search(line):
            return why
    return None


def fatal_token_sites(text, source):
    """(C) C5, SO-1aR.  Scans LINE BY LINE and PER SOURCE FILE, returning
    (sites, benign).  Any site REFUSES regardless of rc, so the R-RC relaxation in
    (B) can never launder a crash into a NOT MEASURED.

    LINE BY LINE, because the token test must be able to tell a CRASH from an
    ENABLEMENT NOTICE and a whole-file substring test cannot -- that is precisely
    what returned NOT A RESULT on SO-1a's five clean arms.  Every token in
    FATAL_TOKENS is a single-line string, so splitting loses no match -- and that is
    DRIVEN, not asserted: one unit plants each token in turn and requires a refusal
    for every one.

    PER SOURCE FILE, because the refusal must name the file that carries the hit.
    SO-1a's refusal named the ARM log while the token lived in `checkMesh.log`,
    pointing a reader at a file that does not contain the token it cites."""
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


def g_completion(base, rows):
    """The five rule-4 clauses, PRINTED INDIVIDUALLY per arm (Sanaa 2026-08-27 s0):

        C1 rc value          -- physics; the kernel's exit status
        C2 terminal marker   -- this item's `End` line (SOLVER) / `Mesh OK.` (SCRIPT)
        C3 artefact present  -- this item's `fields present`
        C4 age guard         -- the artefact strictly newer than the arm's own datum
        C5 no fatal token    -- REFUSES regardless of rc

    R-RC: the rc RECORD is INFRASTRUCTURE.  When it is absent from BOTH channels the
    rc VALUE reads NOT MEASURED **only when C2-C5 all hold**, and the implied rc = 0
    is printed as an INFERENCE, never graded as a measurement."""
    out = {"arms": {}, "not_measured": {}, "rule4_clauses": {}, "datum_resolution": {},
           "rc_inferences": {}}
    for arm in ARMS_REQUIRED:
        r = rows.get(arm)
        if r is None:
            r = inspect_file_fallback(base, arm)
            rows[arm] = r
        kind = ARM_KIND[arm]
        cl = {}

        # ---- C4 age guard (needs the datum before the artefact is judged) --------
        adir, datum, dres = arm_datum(base, arm)
        out["datum_resolution"][arm] = dres

        # ---- C3 artefact present -------------------------------------------------
        art = os.path.join(adir, ARTEFACT[arm])
        if not os.path.isfile(art):
            refuse("G1", {"C3_artefact_absent": art, "arm": arm})
        cl["C3_artefact_present"] = {"verdict": "PASS", "artefact": ARTEFACT[arm]}
        art_mtime = os.path.getmtime(art)
        if art_mtime <= datum:
            refuse("G1", {"C4_artefact_not_newer_than_datum": art, "arm": arm, "datum": datum,
                          "artefact_mtime": art_mtime, "datum_resolution": dres,
                          "note": "age guard, rule 4"})
        cl["C4_age_guard"] = {"verdict": "PASS", "artefact_mtime_epoch": int(art_mtime),
                              "datum_epoch": datum, "reference": dres["resolved_name"],
                              "reference_resolved_by": "EXISTENCE over %s" % (dres["candidates"],),
                              "write_compression": dres.get("write_compression")}

        # ---- the arm log, needed by C2 and C5 ------------------------------------
        logname = r.get("log")
        logpath = os.path.join(base, logname) if logname else None
        text = ""
        if logpath and os.path.isfile(logpath):
            text = open(logpath, errors="replace").read()
        r["log_text"] = text

        # ---- C2 terminal marker ---------------------------------------------------
        if kind == "SOLVER":
            if not logpath or not os.path.isfile(logpath):
                refuse("G1", {"C2_log_absent": logname, "arm": arm,
                              "note": "the terminal marker lives in the log; a missing log is a FAILED clause"})
            if TERMINAL[arm] not in text:
                refuse("G1", {"C2_terminal_marker_absent": TERMINAL[arm], "arm": arm, "log": logname})
            cl["C2_terminal_marker"] = {"verdict": "PASS", "marker": TERMINAL[arm], "log": logname}
        else:
            mtext = open(art, errors="replace").read()
            if not re.search(r"^Mesh OK\.$", mtext, re.M):
                refuse("G1", {"C2_mesh_ok_absent": art, "arm": arm})
            cl["C2_terminal_marker"] = {"verdict": "PASS", "marker": "Mesh OK.", "log": ARTEFACT[arm]}

        # ---- C5 fatal token, REFUSES REGARDLESS OF rc ------------------------------
        # SO-1aR: scanned PER FILE and PER LINE.  SO-1a's `hay = text + artefact`
        # discarded BOTH which file a hit came from AND whether the hit was a crash
        # or OpenFOAM's `trapFpe:` enablement banner.  It refused all five clean arms.
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

        # ---- OOMKilled (physics, unchanged) ----------------------------------------
        oom = str(r.get("oomkilled")).lower()
        if oom not in ("false", "true"):
            refuse("G1", {"oomkilled_unparseable": arm, "value": r.get("oomkilled"),
                          "note": "OOMKilled is a PHYSICS field and is not covered by R-RC"})
        if oom != "false":
            refuse("G1", {"arm": arm, "oomkilled": oom, "note": "rule 4"})

        # ---- C1 rc VALUE, under R-RC -----------------------------------------------
        ke = r.get("inspect_exit")
        kernel_rc = None
        if ke is not None:
            try:
                kernel_rc = int(ke)
            except (TypeError, ValueError):
                refuse("G1", {"rc_record_present_but_garbage": arm, "value": ke,
                              "note": "PRESENT-BUT-GARBAGE refuses; only ABSENT reads NOT MEASURED (L-342)"})
        if kernel_rc is None and r.get("rc") not in (None, 0):
            refuse("G1", {"rc_record_absent_but_harness_rc_nonzero": arm, "harness_rc": r.get("rc"),
                          "note": "R-RC relaxes the rc RECORD, never a POSITIVE reading of failure"})
        if kernel_rc is None:
            # THE rc RECORD IS ABSENT FROM BOTH CHANNELS.  R-RC: NOT MEASURED, and only
            # because C2-C5 above all passed -- each of them is in `cl` and printed.
            cl["C1_rc_value"] = {
                "verdict": NOT_MEASURED, "rc_record": "ABSENT from both the ledger row's "
                "inspect(exit,oomkilled) and <ARM>_<stamp>.inspect.txt",
                "rc_inferred": 0,
                "inference_basis": ["C2_terminal_marker", "C3_artefact_present",
                                    "C4_age_guard", "C5_no_fatal_token"],
                "note": "R-RC (Sanaa 2026-08-27 s0): the rc RECORD is infrastructure; the "
                        "implied rc = 0 is an INFERENCE from C2-C5 and is NEVER graded as a "
                        "measurement.  Had any of C2-C5 failed, this arm would have REFUSED."}
            out["rc_inferences"][arm] = cl["C1_rc_value"]
            out["not_measured"].setdefault(arm, []).append("rc_record")
        else:
            harness_rc = r.get("rc")
            if harness_rc is not None and kernel_rc != harness_rc:
                refuse("G1", {"rc_disagreement": arm, "kernel": kernel_rc, "harness": harness_rc})
            if kernel_rc != 0:
                refuse("G1", {"C1_rc_value_nonzero": arm, "kernel_rc": kernel_rc,
                              "note": "a run that fails any clause is not done (rule 4)"})
            cl["C1_rc_value"] = {"verdict": "PASS", "kernel_rc": kernel_rc,
                                 "source": "docker inspect .State.ExitCode (MEASURED)"}

        out["rule4_clauses"][arm] = cl
        out["arms"][arm] = {"kind": kind, "rc_value": cl["C1_rc_value"]["verdict"],
                            "oomkilled": oom, "artefact": ARTEFACT[arm],
                            "source": r["source"], "field_sources": r["field_sources"]}
        if r.get("infra_not_measured"):
            out["not_measured"].setdefault(arm, []).extend(r["infra_not_measured"])
    return out


# ================= readers with planted controls ======================================
def read_cells(cm_txt):
    """DELTA 3.  The cell-count reader, EXTRACTED TO A NAME so the birth battery can
    drive THE SAME reader the grading path uses instead of a copy of it.  A control
    that re-implements the reader it controls tests the copy, not the instrument."""
    return re.search(r"^\s*cells:\s+(\d+)", cm_txt, re.M)


def read_X(path):
    j = json.load(open(path))
    adj = {}
    for of in ("CD", "CL"):
        adj[of] = {dv: [float(v) for v in j["adjoint"][of][dv]] for dv in ("shape", "patchV")}
    return {"CD": float(j["CD_baseline"]), "CL": float(j["CL_baseline"]), "adjoint": adj,
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"), "nprocs": j.get("nprocs")}


def read_F(path):
    j = json.load(open(path))
    if j.get("tb_steps") is not None and j.get("tb_steps") != TB_STEPS_REGISTERED:
        refuse("G-TB", {"tb_steps_not_registered": j.get("tb_steps"), "registered": TB_STEPS_REGISTERED,
                        "note": "the trivial baseline is fixed at the freeze (DAFOAM_CHARTER section 4)"})
    if j.get("components_requested") != COMPONENTS_REGISTERED:
        refuse("G5", {"components_requested_not_registered": j.get("components_requested"),
                      "registered": COMPONENTS_REGISTERED})
    table, ctrl = {}, None
    for row in j["rows"]:
        if row.get("dv") == "CTRL":
            ctrl = row
            continue
        key = (row["dv"], int(row["idx"]))
        fd = {}
        for k, v in (row.get("fd") or {}).items():
            fd[float(v["step"])] = {"ok": bool(v.get("ok")),
                                    "dCD": (float(v["dCD"]) if v.get("ok") else None),
                                    "dCL": (float(v["dCL"]) if v.get("ok") else None)}
        tb = {}
        for k, v in (row.get("tb") or {}).items():
            tb[float(v["step"])] = {"ok": bool(v.get("ok")),
                                    "dCD": (float(v["dCD"]) if v.get("ok") else None),
                                    "dCL": (float(v["dCL"]) if v.get("ok") else None)}
        table[key] = {"status": row.get("status"), "fd": fd, "tb": tb}
    return {"table": table, "ctrl": ctrl, "CD": float(j["CD_baseline"]), "eta": float(j["eta_used"]),
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"), "raw": j}


def ctrl_control(F):
    c = F["ctrl"]
    if c is None:
        refuse("CONTROL", {"ctrl_row_absent": True})
    zero = float(c["fd"][repr(CTRL_STEP)]["dCD"])
    plant = float(c["planted"]["dCD"])
    want = PLANT / (2.0 * CTRL_STEP)
    if zero != 0.0 or abs(plant - want) > 1e-12 * abs(want):
        refuse("CONTROL", {"instrument_ctrl_not_seen": {"zero": zero, "planted": plant, "want": want}})
    return {"instrument_ctrl_zero": zero, "instrument_ctrl_planted": plant, "want": want}


def grader_plant_control(base, fpath, tag):
    """Write a copy with PLANT added to every physical dCD, re-read it through read_F,
    refuse unless every value moved by exactly PLANT."""
    j = json.load(open(fpath))
    for row in j["rows"]:
        if row.get("dv") == "CTRL":
            continue
        for v in (row.get("fd") or {}).values():
            if v.get("ok"):
                v["dCD"] = repr(float(v["dCD"]) + PLANT)
    # SO-1aR DELTA 2 (WRITE PATH, NOT A GRADING CHANGE, disclosed in
    # PREREGISTRATION.md section 6).  A re-grade runs a SECOND comparator against a
    # run root a FIRST comparator already owns.  SO-1a's control path was
    # `<root>/grader_controls/`; writing there would let a re-grade overwrite a
    # predecessor's control artefact in a preserved run root.  Namespaced by ITEM so
    # the two can never collide and an auditor can see which comparator wrote what.
    cdir = os.path.join(base, "grader_controls_%s" % ITEM)
    os.makedirs(cdir, exist_ok=True)
    cp = os.path.join(cdir, "F_%s_planted.json" % tag)
    json.dump(j, open(cp, "w"), indent=1, sort_keys=True)
    orig, back = read_F(fpath)["table"], read_F(cp)["table"]
    worst = 0.0
    n = 0
    for key, row in orig.items():
        for s, v in row["fd"].items():
            if v["ok"]:
                worst = max(worst, abs((back[key]["fd"][s]["dCD"] - v["dCD"]) - PLANT))
                n += 1
    if n == 0 or worst > 1e-12:
        refuse("CONTROL", {"grader_plant_not_seen": {"n_values": n, "worst_residual": worst, "plant": PLANT}})
    return {"grader_plant_seen": True, "n_values": n, "worst_residual": worst, "file": cp}


# ================= G5: the bright line, per row, per objective =======================
def grade_components(X, F, of):
    key_d = "dCD" if of == "CD" else "dCL"
    comps, graded_fd, graded_adj = [], [], []
    for dv, idx in COMPONENTS_REGISTERED:
        j = X["adjoint"][of][dv][idx] if idx < len(X["adjoint"][of][dv]) else None
        row = F["table"].get((dv, idx))
        c = {"dv": dv, "idx": idx, "J_adj": j}
        if row is None or j is None:
            c.update({"verdict": "NOT A RESULT", "reason": "ABSENT"})
            comps.append(c)
            continue
        steps = sorted(STEPS_REGISTERED[dv], reverse=True)
        vals = [row["fd"].get(s) for s in steps]
        if any(v is None or not v["ok"] for v in vals):
            c.update({"verdict": "NOT A RESULT", "reason": "FD_STEP_FAILED_OR_ABSENT",
                      "steps_present": sorted(row["fd"])})
            comps.append(c)
            continue
        d = [v[key_d] for v in vals]
        ref = d[1]
        c.update({"steps": steps, "d_fd": d, "d_ref": ref})
        if abs(ref) < NEAR_ZERO_ABS:
            c.update({"verdict": "NOT A RESULT", "reason": "NEAR_ZERO"})
            comps.append(c)
            continue
        nb = [abs(d[0] - ref) / abs(ref) * 100.0, abs(d[2] - ref) / abs(ref) * 100.0]
        c["plateau_neighbour_pct"] = nb
        if min(nb) > PLATEAU_TOL_PCT:
            c.update({"verdict": "NOT A RESULT", "reason": "NO_PLATEAU"})
            comps.append(c)
            continue
        rel = abs(ref - j) / abs(ref) * 100.0
        flip = bool(ref * j < 0.0)
        c.update({"rel_err_pct": rel, "sign_flip": flip})
        c["verdict"] = "GATE FAIL" if (flip or rel > FD_BAND_PCT) else "PASS"
        graded_fd.append(ref)
        graded_adj.append(j)
        comps.append(c)
    n_graded = len(graded_fd)
    out = {"objective": of, "components": comps, "n_graded": n_graded,
           "n_pass": sum(1 for c in comps if c.get("verdict") == "PASS"),
           "n_gate_fail": sum(1 for c in comps if c.get("verdict") == "GATE FAIL"),
           "n_not_a_result": sum(1 for c in comps if c.get("verdict") == "NOT A RESULT"),
           "sign_flips": sum(1 for c in comps if c.get("sign_flip"))}
    if n_graded < MIN_GRADED:
        out.update({"verdict": "NOT A RESULT", "aggregate_rel_err_pct": None,
                    "reason": "fewer than %d graded components" % MIN_GRADED})
        return out
    num = math.sqrt(sum((a - b) ** 2 for a, b in zip(graded_fd, graded_adj)))
    den = math.sqrt(sum(a ** 2 for a in graded_fd))
    agg = num / den * 100.0
    out["aggregate_rel_err_pct"] = agg
    band_d_ok = out["n_gate_fail"] == 0
    band_e_ok = agg <= AGG_BAND_PCT
    out["band_D"] = "PASS" if band_d_ok else "GATE FAIL"
    out["band_E"] = "PASS" if band_e_ok else "GATE FAIL"
    out["verdict"] = "PASS" if (band_d_ok and band_e_ok) else "GATE FAIL"
    return out


def grade_tb(X, F, of="CD"):
    """(D) G-TB -- THE CHARTER-4 TRIVIAL BASELINE, SCORED.

    `DAFOAM_CHARTER.md` section 4: *"A finite-difference gate whose verdict is
    counted as evidence names its trivial baseline in the preregistration, before
    its own run.  For a DAFoam FD gate that baseline is the same probe at a step
    chosen to be wrong ... If the wrong step also passes, the gate is not measuring
    what it claims and the verdict it produced is withdrawn."*

    Registered wrong step: h = 1e-8 (`shape`) / 1e-6 (`patchV`), five orders below
    the registered middle step, in the subtractive-cancellation regime.  A probe
    that ERRORED counts as FAILING -- an unevaluable estimate is not agreement."""
    key_d = "dCD" if of == "CD" else "dCL"
    comps, n_pass = [], 0
    for dv, idx in COMPONENTS_REGISTERED:
        j = X["adjoint"][of][dv][idx] if idx < len(X["adjoint"][of][dv]) else None
        row = F["table"].get((dv, idx))
        c = {"dv": dv, "idx": idx, "J_adj": j}
        if row is None or j is None:
            c.update({"tb_verdict": "GATE FAIL", "reason": "ABSENT"}); comps.append(c); continue
        s = TB_STEPS_REGISTERED[dv][0]
        v = (row.get("tb") or {}).get(s)
        if v is None or not v["ok"] or v[key_d] is None:
            c.update({"tb_step": s, "tb_verdict": "GATE FAIL", "reason": "TB_PROBE_FAILED_OR_ABSENT"})
            comps.append(c); continue
        d = v[key_d]
        if abs(d) < NEAR_ZERO_ABS:
            c.update({"tb_step": s, "d_tb": d, "tb_verdict": "GATE FAIL", "reason": "NEAR_ZERO"})
            comps.append(c); continue
        rel = abs(d - j) / abs(d) * 100.0
        flip = bool(d * j < 0.0)
        inside = (not flip) and rel <= FD_BAND_PCT
        c.update({"tb_step": s, "d_tb": d, "rel_err_pct": rel, "sign_flip": flip,
                  "tb_verdict": "PASS" if inside else "GATE FAIL"})
        if inside:
            n_pass += 1
        comps.append(c)
    verdict = "PASS" if n_pass <= TB_MAX_PASSING else "GATE FAIL"
    return {"objective": of, "components": comps, "n_passing_band_D_at_the_WRONG_step": n_pass,
            "max_allowed": TB_MAX_PASSING, "verdict": verdict,
            "consequence": ("the trivial baseline FAILS as registered, so the FD gate is "
                            "measuring the step" if verdict == "PASS" else
                            "the WRONG step also passes: the gate is not measuring what it "
                            "claims and the G5 verdict for this row is WITHDRAWN to NOT A RESULT "
                            "(DAFOAM_CHARTER.md section 4)")}


def compose_row(g_cd, g_cl, g_tb=None):
    # G-TB can only turn a PASS or a GATE FAIL INTO NOT A RESULT, never the reverse
    # (the standing-rule-5 direction, applied to the trivial baseline).
    if g_tb is not None and g_tb["verdict"] == "GATE FAIL":
        return "NOT A RESULT"
    if "NOT A RESULT" in (g_cd["verdict"], g_cl["verdict"]):
        return "NOT A RESULT"
    if "GATE FAIL" in (g_cd["verdict"], g_cl["verdict"]):
        return "GATE FAIL"
    return "PASS"


# ================= G9 / G10 / G12 ======================================================
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
    out = {"per_arm": {}, "verdict": "PASS", "total_core_min": 0.0, "ceiling": ITEM_CEILING_CORE_MIN, "not_measured": []}
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        cm = r.get("core_min")
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
        d = r.get("delivered")
        dl = None
        m = re.match(r"\s*([\d.]+)\s+n=(\d+)", d or "")
        if m:
            dl = float(m.group(1))
        if dl is None:
            out["not_measured"].append(arm)
        dl_ok = True if (dl is None or ARM_RANKS[arm] == 1) else dl >= DELIVERED_CORES_FLOOR
        out["per_arm"][arm] = {"cpuset": r.get("cpuset"), "delivered_cores_mean": (dl if dl is not None else NOT_MEASURED)}
        if not (cs_ok and dl_ok):
            out["verdict"] = "GATE FAIL"
    return out


# ================= the grade ==========================================================
def grade(root):
    rows = read_ledger(os.path.join(root, "ledger.txt"))
    g1 = g_completion(root, rows)
    # ---- MESH identity
    cm_txt = open(os.path.join(root, "MESH", "checkMesh.log"), errors="replace").read()
    m = read_cells(cm_txt)
    if not m:
        refuse("G-M2", {"cells_absent_in_checkMesh": True})
    cells = int(m.group(1))
    gm2 = "PASS" if cells == CELLS_EXPECTED else "GATE FAIL"
    # ---- rows
    X = {"S": read_X(os.path.join(root, "X-S", "so1a_X.json")), "P": read_X(os.path.join(root, "X-P", "so1a_X.json"))}
    F = {"S": read_F(os.path.join(root, "F-S", "so1a_F.json")), "P": read_F(os.path.join(root, "F-P", "so1a_F.json"))}
    rows["X-S"]["artefact_so_md5"] = X["S"]["so_md5"]; rows["X-P"]["artefact_so_md5"] = X["P"]["so_md5"]
    rows["F-S"]["artefact_so_md5"] = F["S"]["so_md5"]; rows["F-P"]["artefact_so_md5"] = F["P"]["so_md5"]
    controls = {"S": ctrl_control(F["S"]), "P": ctrl_control(F["P"]),
                "grader_plant_S": grader_plant_control(root, os.path.join(root, "F-S", "so1a_F.json"), "S"),
                "grader_plant_P": grader_plant_control(root, os.path.join(root, "F-P", "so1a_F.json"), "P")}
    g5 = {}
    for rk in ("S", "P"):
        cd = grade_components(X[rk], F[rk], "CD")
        cl = grade_components(X[rk], F[rk], "CL")
        tb = grade_tb(X[rk], F[rk], "CD")
        g5[rk] = {"G5_CD": cd, "G5c_CL": cl, "G_TB_trivial_baseline": tb,
                  "row_verdict": compose_row(cd, cl, tb),
                  "CD_baseline": X[rk]["CD"], "CL_baseline": X[rk]["CL"], "eta_F": F[rk]["eta"]}
    # ---- divergence shipped vs patched on the adjoint (reported with its number)
    div = []
    for dv, idx in COMPONENTS_REGISTERED:
        a, b = X["S"]["adjoint"]["CD"][dv], X["P"]["adjoint"]["CD"][dv]
        if idx < len(a) and idx < len(b):
            den = max(abs(a[idx]), abs(b[idx]), 1e-300)
            div.append({"dv": dv, "idx": idx, "J_shipped": a[idx], "J_patched": b[idx],
                        "divergence_pct": abs(a[idx] - b[idx]) / den * 100.0})
    g9, g10, g12 = g_toolchain(rows), g_caps(rows), g_placement(rows)
    # ---- predictions, scored never adjusted
    preds = {"P1_cells_4032": "HIT" if gm2 == "PASS" else "MISS",
             "P2_CL_baseline_in_band": "HIT" if PRED["P2_CL_band"][0] <= X["S"]["CL"] <= PRED["P2_CL_band"][1] else "MISS",
             "P3_CD_baseline_in_band": "HIT" if PRED["P3_CD_band"][0] <= X["S"]["CD"] <= PRED["P3_CD_band"][1] else "MISS",
             "P4_patched_row_CD_PASS_5of5": "HIT" if (g5["P"]["G5_CD"]["verdict"] == "PASS" and g5["P"]["G5_CD"]["n_pass"] >= PRED["P4_patched_min_pass"]) else "MISS"}
    s6 = [c for c in g5["S"]["G5_CD"]["components"] if c["dv"] == "shape" and c["idx"] == 6]
    preds["P5_shipped_shape6_outside_band_D_or_flipped"] = "HIT" if (s6 and s6[0].get("verdict") == "GATE FAIL") else ("NOT_MEASURED" if (s6 and s6[0].get("verdict") == "NOT A RESULT") else "MISS")
    # P6 IS THE POINT OF SO-1a: the CONSTRAINT gradient must be as good as the
    # objective's, or SO-1b cannot be registered as a CONSTRAINED optimisation.
    pcl = g5["P"]["G5c_CL"]
    preds["P6_patched_row_CL_constraint_gradient_PASS"] = (
        "NOT_MEASURED" if pcl["verdict"] == "NOT A RESULT" else
        ("HIT" if (pcl["verdict"] == "PASS" and pcl["n_pass"] >= PRED["P4_patched_min_pass"]
                   and (pcl["aggregate_rel_err_pct"] or 0.0) <= PRED["P6_patched_CL_agg_max_pct"]) else "MISS"))
    tbP = g5["P"]["G_TB_trivial_baseline"]
    n_tb_fail = len(COMPONENTS_REGISTERED) - tbP["n_passing_band_D_at_the_WRONG_step"]
    preds["P7_trivial_baseline_fails_ge4_of_5_on_PATCHED"] = "HIT" if n_tb_fail >= PRED["P7_tb_min_failing"] else "MISS"
    # P9 is a prediction about the DEFECT THAT KILLED AV-1 AND AV-2 THIS SESSION,
    # scored mechanically off the datum resolution rather than asserted in prose.
    solver_arms = [a for a in ARMS_REQUIRED if ARM_KIND[a] == "SOLVER"]
    dres = g1["datum_resolution"]
    preds["P9_age_datum_resolves_to_the_COMPRESSED_twin_on_every_solver_arm"] = (
        "HIT" if all(dres[a]["is_compressed_twin"] for a in solver_arms) else "MISS")
    tot = g10["total_core_min"]
    if g10["not_measured"]:
        preds["P8_total_core_min_band"] = NOT_MEASURED
    else:
        preds["P8_total_core_min_band"] = "HIT" if PRED["P8_core_min_band"][0] <= tot <= PRED["P8_core_min_band"][1] else "MISS"
    mw = rows["MESH"].get("wall_s")
    preds["P8b_mesh_wall_le_120s"] = NOT_MEASURED if mw is None else ("HIT" if mw <= PRED["P8_mesh_wall_s_max"] else "MISS")
    # ---- item verdict (composition registered here)
    if "NOT A RESULT" in (g5["S"]["row_verdict"], g5["P"]["row_verdict"]):
        verdict = "NOT A RESULT"
    elif "GATE FAIL" in (g5["S"]["row_verdict"], g5["P"]["row_verdict"], gm2, g9["verdict"], g10["verdict"], g12["verdict"]):
        verdict = "GATE FAIL"
    else:
        verdict = "PASS"
    if verdict not in VOCAB:
        refuse("VOCAB", {"verdict": verdict})
    return {"item": "CURRICULUM-%s" % ITEM, "verdict": verdict,
            "rows": {"SHIPPED": g5["S"]["row_verdict"], "PATCHED": g5["P"]["row_verdict"]},
            "gates": {"G1_completion": "PASS", "G-M2_mesh_identity": gm2, "G5_SHIPPED": g5["S"], "G5_PATCHED": g5["P"],
                      "G_TB_SHIPPED": g5["S"]["G_TB_trivial_baseline"], "G_TB_PATCHED": g5["P"]["G_TB_trivial_baseline"],
                      "G6_dot_product_duality": "NOT MEASURED -- the tutorial exposes no dot-product/duality test; named, never composed",
                      "G9_toolchain": g9, "G10_caps": g10, "G12_placement": g12},
            "mesh_cells": cells, "divergence_shipped_vs_patched_CD": div, "predictions": preds,
            "controls": controls, "completion": g1,
            "not_measured": {"G1": g1["not_measured"], "G10": g10["not_measured"], "G12": g12["not_measured"]},
            "field_classes": {"physics": list(FIELDS_PHYSICS), "infrastructure": list(FIELDS_INFRASTRUCTURE),
                              "rule": "absent infrastructure -> NOT_MEASURED beside the verdict; absent physics -> REFUSE (L-342)"},
            "no_gci": "no grid family; standing rule 5 has no row; NO GCI IS QUOTED",
            "age_datum_resolution": g1["datum_resolution"],
            "rule4_clauses_per_arm": g1["rule4_clauses"],
            "rc_inferences": g1["rc_inferences"],
            "capability_grid_cell": "2D . steady . incompressible -- gradients computed + FD-verified; "
                                    "this item moves ONLY that column, and adds the CONSTRAINT gradient "
                                    "dCL/dx which no A1 record had verified before it"}


# ================= selftest: planted fixtures, counted against a FROZEN unit count ======
ROWFMT = ("ARM={arm} ROW={row} IMG={img} DIGEST={dig} rc={rc} wall_s={wall} ranks={ranks} core_min={cm} "
          "cap_core_min={cap} enforced_wall_s=600 enforced_core_min={cap} memory=4g inspect(exit,oomkilled)=[{ke} {oom}] "
          "memavail_pre_GiB=20.00 memavail_post_GiB={mpost} cpuset={cs} delivered_cores_mean=[{dl}] "
          "siblings_pre=[] siblings_post=[] log={log} stamp=x\n")



# ============================ THE BIRTH REQUIREMENT ==================================
# Sanaa, 2026-08-28T17:01Z, verbatim: "A control defined in terms of the thing it
# controls is not a control.  A planted control must travel the real production path
# -- written by the real producer's code, read through the real reader -- and prove
# the instrument sees a non-zero the same way reality would deliver one.  A control
# that empties the tuple it tests, or writes a schema the producer never emits, tests
# nothing and certifies blindness.  Companion rule canonized: rule 3's question --
# 'was this reader ever shown able to see a non-zero through the real code path?' --
# is now the birth requirement for every reader/comparator: no instrument grades
# anything until that answer is yes, demonstrated."
#
# THIS IS ENFORCED IN CODE, NOT PROMISED IN A DOCUMENT.  `main()` runs `birth(root)`
# BEFORE `grade(root)` and REFUSES the whole item if any leg fails.  Every leg below
# reads an artefact WRITTEN BY THE REAL PRODUCER through THE REAL READER; the one leg
# whose producer cannot be driven on this box is named NOT BORN and its reader is
# BARRED from contributing a graded number rather than papered over with a hand-built
# fixture.
#
# PRINTING DISCIPLINE: the legs that touch the FD and adjoint tables report COUNTS AND
# BOOLEANS ONLY, never a derivative value.  The birth battery must not leak the
# answers to this item's own predictions (PREREGISTRATION.md section 4a).
SO1A_RUN_ARM = os.path.join(os.path.dirname(SO1A_FROZEN_GRADER), "so1a_run_arm.sh")
PRODUCER_ROW_ANCHOR = 'echo "ARM=$ARM ROW=$ROW IMG=$IMG'


def producer_ledger_row(rc, inspect, arm="X-S", row="SHIPPED", cpuset="9"):
    """Emit ONE ledger row BY EXECUTING THE REAL PRODUCER'S OWN `echo` STATEMENT,
    lifted from the FROZEN `so1a_run_arm.sh` by exact content match (never by line
    number, which drifts).  This is what kills the AV2R failure mode: a fixture that
    writes a schema the producer never emits cannot arise, because the producer is
    what writes it.  Returns (line, source_line_number)."""
    src = open(SO1A_RUN_ARM, errors="replace").read().splitlines()
    hits = [(i + 1, ln) for i, ln in enumerate(src) if PRODUCER_ROW_ANCHOR in ln]
    if len(hits) != 1:
        return None, len(hits)
    lineno, stmt = hits[0]
    env = dict(os.environ)
    env.update({"ARM": arm, "ROW": row, "IMG": "img", "GOT_DIGEST": IMG_DIGEST[row],
                "rc": str(rc), "WALL": "60", "RANKS": "1", "CORE_MIN": "1.0",
                "CAP": str(CAPS[arm]), "TMO": "600", "BACKCHECK": str(CAPS[arm]),
                "MEM": "4g", "INSPECT": inspect, "MEMAVAIL_GIB": "20.00",
                "MEMAVAIL_POST": "20.00", "CPUSET": cpuset,
                "DELIVERED": "0.99 n=3 max_nr_throttled=0", "SIBLINGS_PRE": "",
                "SIBLINGS_POST": "", "LOG": "/x/%s_x.log" % arm, "STAMP": "x"})
    out = subprocess.run(["bash", "-c", stmt.strip()], env=env, capture_output=True,
                         text=True)
    if out.returncode != 0 or not out.stdout.strip():
        return None, lineno
    return out.stdout.strip() + "\n", lineno


def birth(root, workdir):
    """Every reader that contributes a graded number, driven ON THE REAL ARTEFACTS
    THIS ITEM WILL GRADE.  Returns (ok, legs).  ok is False if ANY leg fails; the
    caller must then refuse to grade."""
    os.makedirs(workdir, exist_ok=True)
    legs, ok = [], True

    def leg(name, born, detail):
        nonlocal ok
        legs.append({"leg": name, "born": bool(born), "detail": detail})
        if not born:
            ok = False

    # B1 -- the LEDGER reader, on the REAL ledger written by so1a_run_arm.sh --------
    lp = os.path.join(root, "ledger.txt")
    rows = read_ledger(lp) if os.path.isfile(lp) else {}
    cms = {a: (rows.get(a) or {}).get("core_min") for a in ARMS_REQUIRED}
    b1 = (set(rows) >= set(ARMS_REQUIRED)
          and all(isinstance(cms[a], float) and cms[a] > 0.0 for a in ARMS_REQUIRED)
          and all((rows[a] or {}).get("DIGEST") == IMG_DIGEST[ARM_ROW[a]] for a in ARMS_REQUIRED))
    leg("B1_ledger_reader_on_the_real_ledger", b1,
        {"producer": "so1a_run_arm.sh (the real run, 2026-08-28)", "reader": "read_ledger",
         "artefact": "ledger.txt", "arms_read": sorted(rows),
         "nonzero_seen": "every core_min > 0", "core_min_total": round(sum(
             v for v in cms.values() if isinstance(v, float)), 3)})

    # B2 -- the NON-ZERO rc, EMITTED BY THE REAL PRODUCER'S OWN echo ----------------
    # No crashed container exists on this box, so the non-zero rc cannot come from a
    # real run.  It is therefore produced by RUNNING THE PRODUCER'S OWN STATEMENT,
    # which is the closest thing to reality that exists without burning compute -- and
    # it proves producer and reader agree on the SCHEMA, not merely on this lane's
    # transcription of it.
    for _rc, _ins, _tag in ((1, "1 false", "rc_nonzero"), (0, "0 true", "oomkilled_true")):
        line, meta = producer_ledger_row(_rc, _ins)
        got = {}
        if line:
            fp = os.path.join(workdir, "birth_ledger_%s.txt" % _tag)
            open(fp, "w").write("ITEM=SO1a\n" + line)
            got = (read_ledger(fp).get("X-S") or {})
        want_rc, want_exit, want_oom = _rc, _ins.split()[0], _ins.split()[1]
        b2 = bool(line) and str(got.get("rc")) == str(want_rc) \
            and str(got.get("inspect_exit")) == want_exit \
            and str(got.get("oomkilled")).lower() == want_oom
        leg("B2_%s_seen_through_the_producers_own_emitter" % _tag, b2,
            {"producer": "so1a_run_arm.sh:%s, THE ACTUAL echo STATEMENT, executed" % meta,
             "reader": "read_ledger", "planted": {"rc": want_rc, "inspect": _ins},
             "read_back": {"rc": got.get("rc"), "inspect_exit": got.get("inspect_exit"),
                           "oomkilled": got.get("oomkilled")}})

    # B3 -- the INSPECT-FILE FALLBACK: NOT BORN, and therefore BARRED ---------------
    # Its producer is a `docker inspect` command; driving it needs a container, and
    # this item launches none.  Every `.inspect.txt` on this box records exit 0, so
    # NO REAL NON-ZERO RECORD EXISTS to birth it with.  Rather than paper it with a
    # hand-built file, the reader is declared NOT BORN and BARRED: if any arm were
    # MISSING from the ledger, the grading path would fall back to it, so the birth
    # requirement is met by proving THE FALLBACK IS NOT NEEDED for this root.
    b3 = set(rows) >= set(ARMS_REQUIRED)
    leg("B3_inspect_fallback_NOT_BORN_and_not_needed", b3,
        {"reader": "inspect_file_fallback", "born": False,
         "reason": ("its producer is `docker inspect`, which cannot be driven without "
                    "launching a container; and no non-zero-exit .inspect.txt exists "
                    "anywhere on this box to birth it from a real run"),
         "bar": ("BARRED from contributing a graded number.  This leg passes only "
                 "because all five arms carry ledger rows, so the fallback is never "
                 "reached on this root; if a row were missing this item would REFUSE "
                 "rather than grade through an unborn reader"),
         "arms_with_ledger_rows": sorted(rows)})

    # B4 -- the AGE DATUM and DATUM REFERENCE, on the REAL arm directories ----------
    ages = {}
    b4 = True
    for a in ARMS_REQUIRED:
        try:
            d, datum, ref = arm_datum(root, a)
            art = os.path.join(d, ARTEFACT[a])
            delta = int(os.path.getmtime(art)) - datum
            ages[a] = {"datum_gt_0": datum > 0, "resolved_name": ref.get("resolved_name"),
                       "artefact_minus_datum_s": delta, "strictly_newer": delta > 0}
            b4 = b4 and datum > 0 and delta > 0
        except Exception as e:                                     # noqa: BLE001
            ages[a] = {"error": str(e)}; b4 = False
    leg("B4_age_datum_and_datum_reference_on_the_real_arms", b4,
        {"producer": "so1a_run_arm.sh (datum) + the solver's own time-0 write (reference)",
         "reader": "arm_datum + resolve_datum_ref", "per_arm": ages,
         "nonzero_seen": "a real epoch datum and a strictly positive age delta on every arm"})

    # B5 -- writeCompression, on the REAL controlDicts ------------------------------
    wc = {}
    for a in ARMS_REQUIRED:
        _w = read_write_compression(os.path.join(root, a))
        # the reader returns {value, source}; the SOURCE PATH is reduced to its
        # arm-relative form so a birth record is comparable between roots
        wc[a] = {"write_compression": _w.get("write_compression"),
                 "source_rel": os.path.relpath(_w.get("write_compression_source", ""), root)
                 if _w.get("write_compression_source") else None}
    leg("B5_write_compression_reader_on_the_real_controlDicts",
        all(v["write_compression"] in ("on", "off") and v["source_rel"] for v in wc.values()),
        {"producer": "the tutorial's own system/controlDict, staged by preProcessing.sh",
         "reader": "read_write_compression", "per_arm": wc,
         "nonzero_seen": "a real keyword VALUE read out of every arm's own controlDict, "
                         "with the file it came from named"})

    # B6 -- the CELL-COUNT reader (DELTA 3), on the REAL checkMesh.log --------------
    cmp_path = os.path.join(root, "MESH", "checkMesh.log")
    mm = read_cells(open(cmp_path, errors="replace").read()) if os.path.isfile(cmp_path) else None
    leg("B6_cell_count_reader_on_the_real_checkMesh_log",
        bool(mm) and int(mm.group(1)) > 0,
        {"producer": "OpenFOAM checkMesh, in the SHIPPED container", "reader": "read_cells",
         "artefact": "MESH/checkMesh.log", "nonzero_seen": "a positive integer cell count",
         "value_withheld": "the count itself is NOT printed here -- P1 is a registered "
                           "prediction and the birth battery must not leak it"})

    # B7/B8 -- the ADJOINT and FD readers, on the REAL producer's own artefacts -----
    # COUNTS AND BOOLEANS ONLY.  No derivative value is printed.
    nz = {}
    b78 = True
    for a in ("X-S", "X-P"):
        try:
            Xr = read_X(os.path.join(root, a, ARTEFACT[a]))
            n = sum(1 for of in ("CD", "CL") for dv in Xr["adjoint"][of]
                    for v in Xr["adjoint"][of][dv] if v != 0.0)
            nz[a] = {"nonzero_adjoint_entries": n, "so_md5_present": bool(Xr["so_md5"]),
                     "nprocs": Xr["nprocs"]}
            b78 = b78 and n > 0
        except Exception as e:                                     # noqa: BLE001
            nz[a] = {"error": str(e)}; b78 = False
    leg("B7_adjoint_reader_on_the_real_X_artefacts", b78,
        {"producer": "so1a_xf.py -mode X, in the real containers", "reader": "read_X",
         "per_arm": nz, "nonzero_seen": "a counted number of non-zero adjoint entries",
         "values_withheld": "no derivative value is printed"})

    fz = {}
    b8 = True
    Fs = {}
    for a in ("F-S", "F-P"):
        try:
            Fr = read_F(os.path.join(root, a, ARTEFACT[a]))
            Fs[a] = Fr
            nfd = sum(1 for k in Fr["table"] for v in Fr["table"][k]["fd"].values()
                      if v["ok"] and v["dCD"] not in (None, 0.0))
            ntb = sum(1 for k in Fr["table"] for v in Fr["table"][k]["tb"].values()
                      if v["ok"] and v["dCD"] not in (None, 0.0))
            ncl = sum(1 for k in Fr["table"] for v in Fr["table"][k]["fd"].values()
                      if v["ok"] and v["dCL"] not in (None, 0.0))
            fz[a] = {"components": len(Fr["table"]), "nonzero_fd_dCD": nfd,
                     "nonzero_fd_dCL": ncl, "nonzero_tb_dCD": ntb,
                     "ctrl_row_present": Fr["ctrl"] is not None}
            b8 = b8 and nfd > 0 and ncl > 0 and ntb > 0 and Fr["ctrl"] is not None
        except Exception as e:                                     # noqa: BLE001
            fz[a] = {"error": str(e)}; b8 = False
    leg("B8_FD_table_reader_on_the_real_F_artefacts", b8,
        {"producer": "so1a_xf.py -mode F, in the real containers", "reader": "read_F",
         "per_arm": fz,
         "nonzero_seen": "counted non-zero central-FD dCD, dCL and trivial-baseline entries",
         "values_withheld": ("no derivative value and no plateau structure is printed -- "
                             "R4 is a registered prediction of this item")})

    # B9 -- THE CANONICAL RULE-3 CONTROL: the plant WRITTEN BY THE REAL PRODUCER
    #       DURING THE REAL RUN, read back through the real reader.  This is the one
    #       leg where the plant genuinely travelled the production path end to end:
    #       `so1a_xf.py` inserted PLANT into the CTRL row inside the container.
    cz = {}
    b9 = True
    for a in ("F-S", "F-P"):
        try:
            cz[a] = ctrl_control(Fs[a])
            b9 = b9 and cz[a]["instrument_ctrl_zero"] == 0.0
        except Exception as e:                                     # noqa: BLE001
            cz[a] = {"error": str(e)}; b9 = False
    leg("B9_producer_written_plant_read_back_through_the_real_reader", b9,
        {"producer": "so1a_xf.py, WHICH INSERTED THE PLANT DURING THE REAL RUN",
         "reader": "read_F + ctrl_control", "per_arm": cz,
         "nonzero_seen": ("the CTRL row's planted derivative reads exactly "
                          "PLANT/(2*ctrl_step) while its unplanted twin reads 0.0 -- "
                          "the reader is shown seeing a non-zero AND a zero, from the "
                          "same file, through the same code path")})

    # B10 -- the GRADER-LEVEL plant, applied to the REAL artefacts ------------------
    gz = {}
    b10 = True
    for a, tag in (("F-S", "S"), ("F-P", "P")):
        try:
            gz[a] = grader_plant_control(workdir, os.path.join(root, a, ARTEFACT[a]),
                                         "birth_%s" % tag)
            b10 = b10 and gz[a]["grader_plant_seen"] and gz[a]["n_values"] > 0
        except Exception as e:                                     # noqa: BLE001
            gz[a] = {"error": str(e)}; b10 = False
    leg("B10_grader_plant_on_the_real_artefacts", b10,
        {"reader": "read_F", "per_arm": {a: {k: v for k, v in (gz[a] or {}).items()
                                             if k != "file"} for a in gz},
         "nonzero_seen": "every physical dCD moves by exactly PLANT when re-read",
         "written_to": ("a WORKDIR OUTSIDE the run root during --birth, so the "
                        "battery mutates nothing it grades")})

    # B11 -- the C5 SCANNER, on every REAL log this item will grade -----------------
    c5 = {}
    for a in ARMS_REQUIRED:
        r = rows.get(a) or {}
        files = []
        lg = r.get("log")
        if lg and os.path.isfile(os.path.join(root, lg)):
            files.append((lg, os.path.join(root, lg)))
        if ARM_KIND[a] == "SCRIPT":
            files.append((ARTEFACT[a], os.path.join(root, a, ARTEFACT[a])))
        si, be = 0, 0
        for nm, fp in files:
            _s, _b = fatal_token_sites(open(fp, errors="replace").read(), nm)
            si += len(_s); be += len(_b)
        c5[a] = {"files_scanned": [f[0] for f in files], "real_sites": si,
                 "benign_excluded": be}
    leg("B11_C5_scanner_on_every_real_log_this_item_will_grade", True,
        {"producer": "the real containers", "reader": "fatal_token_sites", "per_arm": c5,
         "nonzero_seen": ("the SAME scanner is shown refusing on real crash bytes in "
                          "selftest units U41-U44 and U47; here it is shown reading the "
                          "REAL artefacts and reporting its exclusions COUNTED"),
         "note": "counts only; this leg renders no verdict"})

    return ok, legs

def graded(root, workdir):
    """THE ONLY GRADING ENTRY POINT.  The birth requirement is ENFORCED HERE: if any
    reader that contributes a graded number has not been shown able to see a non-zero
    through the real code path, this REFUSES and NOTHING is graded.  Sanaa 2026-08-28:
    "no instrument grades anything until that answer is yes, demonstrated"."""
    os.makedirs(workdir, exist_ok=True)
    ok, legs = birth(root, workdir)
    if not ok:
        refuse("BIRTH", {"birth_requirement_not_met": [l["leg"] for l in legs if not l["born"]],
                         "legs": legs,
                         "note": ("a reader not shown able to see a non-zero through the "
                                  "real code path may not grade.  NOTHING was graded.")})
    r = grade(root)
    r["birth"] = {"verdict": "BORN", "n_legs": len(legs), "legs": legs}
    return r


def _fix(tmp, tweak=None):
    """Build a clean fixture; `tweak` mutates the dict of knobs before writing.

    NEW KNOBS, one per NEW GUARD, so every guard this comparator adds is DRIVEN
    to fire rather than asserted to exist (Sanaa 2026-08-27 s1, L-314 standard):
      `datum`      per arm: "plain" | "gz" | "none"  -- (A) datum by existence
      `rc_record`  set of arms whose kernel exit is written NOT_MEASURED -- (B) R-RC
      `fatal`      arm -> token injected into the arm log -- (C) C5
      `tb_pass`    per row, set of components whose WRONG step AGREES -- (D) G-TB
      `err_cl`     per row, planted CL error, so (E) the constraint gradient is
                   shown able to fail INDEPENDENTLY of the objective
    """
    k = {"rc": {a: 0 for a in ARMS_REQUIRED}, "ke": {}, "oom": {a: "false" for a in ARMS_REQUIRED},
         "cm": dict(PREDICTED_CORE_MIN), "cs": {a: CPUSET_REGISTERED for a in ARMS_REQUIRED},
         "so": {a: SO_MD5[ARM_ROW[a]] for a in ARMS_REQUIRED}, "cells": CELLS_EXPECTED,
         "err": {"S": {}, "P": {}}, "err_cl": {"S": {}, "P": {}},
         "flip": {"S": set(), "P": set()}, "noplateau": {"S": set(), "P": set()},
         "tb_pass": {"S": set(), "P": set()},
         "terminal": {a: True for a in ARMS_REQUIRED}, "stale": set(), "ctrl_ok": True, "mpost": "20.00",
         "drop_row": set(), "inspect_file": set(), "rc_record": set(), "fatal": {},
         # SO-1aR knobs.  `banner` puts SO-1a's OWN REAL banner line into the MESH
         # artefact and is ON BY DEFAULT, because that is what the real artefact
         # carries; `fatal_art` injects into the ARTEFACT (which is where SO-1a's
         # false positive lived and where its `fatal` knob could not reach);
         # `log_extra` appends arbitrary REAL log bytes to an arm log.
         "banner": True, "fatal_art": {}, "log_extra": {},
         # DEFAULT: the SOLVER arms resolve to the COMPRESSED twin, which is what
         # `writeCompression on` at np = 1 actually produces (AV-1 measured it).
         "datum": {a: ("plain" if a == "MESH" else "gz") for a in ARMS_REQUIRED},
         "write_compression": "on",
         "dl": "1.99 n=10 max_nr_throttled=0", "CL": 0.50, "CD": 0.0209}
    if tweak:
        tweak(k)
    root = os.path.join(tmp, "root_%d" % int(time.time() * 1e6))
    os.makedirs(root)
    led = ["ITEM=SO1a\n", "STAGED stamp=x\n"]
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
            # the SOLVER rewrote time-0 compressed AFTER the datum was taken: the
            # plain name is gone, the twin is NEWER.  This is AV-1's measurement.
            os.remove(plain)
            gz = plain + ".gz"
            open(gz, "w").write("U compressed\n")
            os.utime(gz, (t0 + 3, t0 + 3))
        elif kind == "none":
            os.remove(plain)
        log = "%s_x.log" % arm
        so = k["so"][arm]
        text = "D4S_CONTAINER_UID: 0\nD4S_IDWARP_SO_MD5: %s\nD4S_DEADLINE_IN_CONTAINER_S: 600\n" % so
        if arm == "MESH":
            art = os.path.join(d, "checkMesh.log")
            # LAID OUT LIKE THE REAL ARTEFACT: the banner is an EARLY line (real file:
            # line 18 of 99) and `Mesh OK.` is at the end, so a planted crash appended
            # after it sits BELOW the banner exactly as a real crash would.
            head = (REAL_BANNER_LINE + "\n") if k["banner"] else ""
            open(art, "w").write(head + "Mesh stats\n    cells:            %d\n\nMesh OK.\n"
                                 % k["cells"] + k["fatal_art"].get(arm, ""))
            text += "SO1A_CHECKMESH_RC 0\n"
        else:
            rk = "S" if arm.endswith("-S") else "P"
            art = os.path.join(d, ARTEFACT[arm])
            ident = {"libidwarp_so_md5": so, "idwarp_file": "/x/idwarp/__init__.py",
                     "write_compression": k["write_compression"]}
            J = {"shape": [-0.011, 0.02, -0.03, 0.041, 0.05, -0.06, 0.007, -0.008], "patchV": [0.0, 0.0123]}
            if arm.startswith("X"):
                adj = {"CD": {dv: [repr(v) for v in J[dv]] for dv in J},
                       "CL": {dv: [repr(v * 10.0) for v in J[dv]] for dv in J}}
                json.dump({"item": "SO1a", "mode": "X", "identity": ident, "nprocs": 1, "CD_baseline": repr(k["CD"]),
                           "CL_baseline": repr(k["CL"]), "adjoint": adj}, open(art, "w"))
            else:
                rows_ = []
                for dv, idx in COMPONENTS_REGISTERED:
                    j = J[dv][idx]
                    e = k["err"][rk].get((dv, idx), 0.5)          # default 0.5 % error on CD
                    ecl = k["err_cl"][rk].get((dv, idx), 0.5)     # default 0.5 % error on CL
                    dref = j * (1.0 + e / 100.0)
                    dref_cl = j * 10.0 * (1.0 + ecl / 100.0)
                    if (dv, idx) in k["flip"][rk]:
                        dref = -dref
                    fd = {}
                    for s in STEPS_REGISTERED[dv]:
                        scale = 1.0 if s == sorted(STEPS_REGISTERED[dv])[1] else 1.01
                        if (dv, idx) in k["noplateau"][rk]:
                            scale = 1.0 if s == sorted(STEPS_REGISTERED[dv])[1] else 1.5
                        fd[repr(s)] = {"step": s, "ok": True, "dCD": repr(dref * scale), "dCL": repr(dref_cl * scale),
                                       "CD_plus": repr(0.0), "CD_minus": repr(0.0), "CL_plus": repr(0.0), "CL_minus": repr(0.0)}
                    # the TRIVIAL BASELINE row: by DEFAULT the WRONG step is noise
                    # (200 % off), which is the registered expectation; `tb_pass`
                    # plants the failure mode -- a wrong step that AGREES.
                    tbs = TB_STEPS_REGISTERED[dv][0]
                    tbmul = 1.001 if (dv, idx) in k["tb_pass"][rk] else 3.0
                    tb = {repr(tbs): {"step": tbs, "ok": True, "dCD": repr(j * tbmul),
                                      "dCL": repr(j * 10.0 * tbmul), "CD_plus": repr(0.0),
                                      "CD_minus": repr(0.0), "CL_plus": repr(0.0), "CL_minus": repr(0.0)}}
                    rows_.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd, "tb": tb})
                planted = PLANT / (2.0 * CTRL_STEP) if k["ctrl_ok"] else 0.0
                rows_.append({"dv": "CTRL", "idx": 0, "status": "CONTROL",
                              "fd": {repr(CTRL_STEP): {"step": CTRL_STEP, "ok": True, "dCD": repr(0.0), "dCL": repr(0.0)}},
                              "planted": {"step": CTRL_STEP, "plant": PLANT, "dCD": repr(planted), "ok": True}})
                json.dump({"item": "SO1a", "mode": "F", "identity": ident, "components_requested": COMPONENTS_REGISTERED,
                           "steps": STEPS_REGISTERED, "tb_steps": TB_STEPS_REGISTERED,
                           "CD_baseline": repr(k["CD"]), "CL_baseline": repr(k["CL"]), "eta_used": repr(1e-9),
                           "rows": rows_}, open(art, "w"))
            if k["terminal"][arm]:
                text += TERMINAL[arm] + " ok\n"
        if arm in k["fatal"]:
            text += k["fatal"][arm] + "\n"
        if arm in k["log_extra"]:
            text += k["log_extra"][arm]
        os.utime(art, (t0 - 5, t0 - 5) if arm in k["stale"] else (t0 + 5, t0 + 5))
        open(os.path.join(root, log), "w").write(text)
        ke = NOT_MEASURED if arm in k["rc_record"] else k["ke"].get(arm, k["rc"][arm])
        if arm in k["inspect_file"]:
            open(os.path.join(root, "%s_x.inspect.txt" % arm), "w").write("%s %s 2026-08-27T00:00:00Z 2026-08-27T00:01:00Z %s 4294967296 %s\n" % (ke, k["oom"][arm], k["cs"][arm], IMG_DIGEST[ARM_ROW[arm]]))
        if arm in k["drop_row"]:
            continue
        led.append(ROWFMT.format(arm=arm, row=ARM_ROW[arm], img="img", dig=IMG_DIGEST[ARM_ROW[arm]], rc=k["rc"][arm],
                                 wall=60, ranks=ARM_RANKS[arm], cm=k["cm"][arm], cap=CAPS[arm], ke=ke, oom=k["oom"][arm],
                                 mpost=k["mpost"], cs=k["cs"][arm], dl=k["dl"], log=log))
    open(os.path.join(root, "ledger.txt"), "w").write("".join(led))
    return root


def selftest(tmp):
    n = 0; fails = []

    def unit(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name)
        print("  [%s] %s" % ("OK " if cond else "BAD", name))

    def refused(root):
        try:
            grade(root); return False
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
    r = grade(_fix(tmp))
    unit("U1 clean fixture -> item PASS, both rows PASS, G-M2/G9/G10/G12 PASS",
         r["verdict"] == "PASS" and r["rows"] == {"SHIPPED": "PASS", "PATCHED": "PASS"} and r["gates"]["G-M2_mesh_identity"] == "PASS"
         and r["gates"]["G9_toolchain"]["verdict"] == "PASS" and r["gates"]["G10_caps"]["verdict"] == "PASS" and r["gates"]["G12_placement"]["verdict"] == "PASS")
    unit("U2 clean fixture -> P1-P4, P6, P7, P8, P8b, P9 HIT; P5 MISS (shape[6] clean by construction)",
         all(r["predictions"][k] == "HIT" for k in (
             "P1_cells_4032", "P2_CL_baseline_in_band", "P3_CD_baseline_in_band",
             "P4_patched_row_CD_PASS_5of5", "P6_patched_row_CL_constraint_gradient_PASS",
             "P7_trivial_baseline_fails_ge4_of_5_on_PATCHED",
             "P9_age_datum_resolves_to_the_COMPRESSED_twin_on_every_solver_arm",
             "P8_total_core_min_band", "P8b_mesh_wall_le_120s"))
         and r["predictions"]["P5_shipped_shape6_outside_band_D_or_flipped"] == "MISS")
    unit("U19 grader-level plant SEEN on both F tables (rule 3)", r["controls"]["grader_plant_S"]["grader_plant_seen"] and r["controls"]["grader_plant_P"]["grader_plant_seen"] and r["controls"]["S"]["instrument_ctrl_zero"] == 0.0)
    r = grade(_fix(tmp, tw(err={"S": {("shape", 3): 7.0}})))
    unit("U3 PLANTED 7 % error on shipped shape[3] -> component GATE FAIL, SHIPPED row GATE FAIL, item GATE FAIL",
         r["rows"]["SHIPPED"] == "GATE FAIL" and r["verdict"] == "GATE FAIL" and r["gates"]["G5_SHIPPED"]["G5_CD"]["n_gate_fail"] == 1)
    r = grade(_fix(tmp, tw(flip={"S": {("shape", 6)}, "P": set()})))
    unit("U4 PLANTED sign flip on shipped shape[6] -> flip counted, SHIPPED GATE FAIL, P5 HIT, PATCHED PASS",
         r["gates"]["G5_SHIPPED"]["G5_CD"]["sign_flips"] == 1 and r["rows"]["SHIPPED"] == "GATE FAIL" and r["predictions"]["P5_shipped_shape6_outside_band_D_or_flipped"] == "HIT" and r["rows"]["PATCHED"] == "PASS")
    r = grade(_fix(tmp, tw(noplateau={"S": {("shape", 0)}, "P": set()})))
    c0 = [c for c in r["gates"]["G5_SHIPPED"]["G5_CD"]["components"] if c["idx"] == 0 and c["dv"] == "shape"][0]
    unit("U5 PLANTED no-plateau on one component -> that component NOT A RESULT, row still PASS on 4 graded",
         c0["verdict"] == "NOT A RESULT" and c0["reason"] == "NO_PLATEAU" and r["rows"]["SHIPPED"] == "PASS" and r["gates"]["G5_SHIPPED"]["G5_CD"]["n_graded"] == 4)
    r = grade(_fix(tmp, tw(noplateau={"P": {("shape", 0), ("shape", 3), ("shape", 6)}, "S": set()})))
    unit("U6 three no-plateau components on PATCHED -> 2 graded < 3 -> row NOT A RESULT, item NOT A RESULT",
         r["rows"]["PATCHED"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT")
    unit("U7 rc=1 on X-P -> REFUSAL", refused(_fix(tmp, tw(rc={"X-P": 1}, ke={"X-P": 1}))))
    unit("U8 OOMKilled=true on F-S -> REFUSAL", refused(_fix(tmp, tw(oom={"F-S": "true"}))))
    unit("U9 terminal marker absent in F-P log -> REFUSAL", refused(_fix(tmp, tw(terminal={"F-P": False}))))
    unit("U10 artefact OLDER than the age datum (X-S) -> REFUSAL (rule 4)", refused(_fix(tmp, tw(stale={"X-S"}))))
    unit("U11 instrument CTRL planted row broken -> REFUSAL (a reader not shown to see a non-zero)", refused(_fix(tmp, tw(ctrl_ok=False))))
    r = grade(_fix(tmp, tw(so={"X-P": SO_MD5["SHIPPED"]})))
    unit("U12 X-P carrying the SHIPPED .so md5 -> G9 GATE FAIL, item GATE FAIL", r["gates"]["G9_toolchain"]["verdict"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(cm={"F-S": 26.0})))
    unit("U13 F-S core_min 26.0 > cap 25.0 -> G10 GATE FAIL", r["gates"]["G10_caps"]["verdict"] == "GATE FAIL" and r["gates"]["G10_caps"]["per_arm"]["F-S"]["crossed"])
    r = grade(_fix(tmp, tw(cs={"X-S": "4,14"})))
    unit("U14 X-S on cpuset 4,14 (registered 9) -> G12 GATE FAIL", r["gates"]["G12_placement"]["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(cells=4033)))
    unit("U15 cells 4033 -> G-M2 GATE FAIL, P1 MISS", r["gates"]["G-M2_mesh_identity"] == "GATE FAIL" and r["predictions"]["P1_cells_4032"] == "MISS")
    r = grade(_fix(tmp, tw(mpost="NOT_MEASURED", dl="NOT_MEASURED")))
    unit("U16 absent infrastructure fields -> verdict unchanged PASS, NOT_MEASURED named beside it (L-342)",
         r["verdict"] == "PASS" and r["not_measured"]["G1"].get("X-S") and "X-S" in r["not_measured"]["G12"])
    unit("U17 harness rc 0 vs kernel exit 1 disagreement -> REFUSAL", refused(_fix(tmp, tw(ke={"F-P": 1}))))
    unit("U18 ledger row absent, no inspect record -> REFUSAL", refused(_fix(tmp, tw(drop_row={"F-P"}))))
    r = grade(_fix(tmp, tw(drop_row={"F-P"}, inspect_file={"F-P"})))
    unit("U20 ledger row absent, ONE inspect record -> read from it, source named, core_min NOT_MEASURED, verdict PASS",
         r["verdict"] == "PASS" and r["completion"]["arms"]["F-P"]["source"] == "inspect_record" and "F-P" in r["not_measured"]["G10"])
    # SO-1aR delta: the PRODUCER of the artefacts being re-graded is SO-1a's frozen
    # `so1a_xf.py`, which lives in SO-1a's directory, not this one.  Checking IT is
    # exactly right for a re-grade -- this item produces nothing.
    here = os.path.dirname(SO1A_FROZEN_GRADER)
    unit("U21 ast.Assert count = 0 in so1ar_grade.py (this file) and in the PRODUCER "
         "so1a_xf.py that wrote the artefacts being re-graded (L-332)",
         count_asserts(os.path.abspath(__file__)) == 0 and count_asserts(os.path.join(here, "so1a_xf.py")) == 0)
    p = os.path.join(tmp, "planted_assert.py")
    open(p, "w").write("x = 1\nassert x == 1\n")
    unit("U22 the assert counter sees a planted assert (=1)", count_asserts(p) == 1)

    # ================= (A) THE AGE-GUARD DATUM, RESOLVED BY EXISTENCE ================
    r = grade(_fix(tmp))
    solver = [a for a in ARMS_REQUIRED if ARM_KIND[a] == "SOLVER"]
    unit("U23 (A) every solver arm's datum resolves to the COMPRESSED twin 0/U.gz -- the "
         "AV-1/AV-2 configuration -- guard PASSES, the resolved name and writeCompression "
         "are recorded, P9 HIT",
         all(r["age_datum_resolution"][a]["resolved_name"] == "0/U.gz" for a in solver)
         and all(r["age_datum_resolution"][a]["is_compressed_twin"] for a in solver)
         and all(r["age_datum_resolution"][a]["write_compression"] == "on" for a in solver)
         and r["age_datum_resolution"]["MESH"]["resolved_name"] == "0.orig/U"
         and r["verdict"] == "PASS"
         and r["predictions"]["P9_age_datum_resolves_to_the_COMPRESSED_twin_on_every_solver_arm"] == "HIT")
    unit("U24 (A) DRIVEN CONTROL -- the datum is GENUINELY ABSENT in BOTH registered names "
         "on X-S -> REFUSAL (a name swap would not have caught this)",
         refused(_fix(tmp, tw(datum={"X-S": "none"}))))
    r = grade(_fix(tmp, tw(datum={a: "plain" for a in ARMS_REQUIRED}, write_compression="off")))
    unit("U25 (A) writeCompression off -> the datum resolves to the PLAIN 0/U, guard PASSES, "
         "verdict unchanged PASS, P9 MISS (scored, never adjusted)",
         all(r["age_datum_resolution"][a]["resolved_name"] == "0/U" for a in solver)
         and r["verdict"] == "PASS"
         and r["predictions"]["P9_age_datum_resolves_to_the_COMPRESSED_twin_on_every_solver_arm"] == "MISS")

    # ================= (B) R-RC, AND (C) THE FATAL-TOKEN CLAUSE =====================
    r = grade(_fix(tmp, tw(rc_record={"F-P"})))
    unit("U26 (B) R-RC -- the rc RECORD is absent on F-P while C2-C5 all hold -> rc value "
         "NOT MEASURED, rc=0 printed as an INFERENCE with its basis named, verdict unchanged PASS",
         r["verdict"] == "PASS"
         and r["rule4_clauses_per_arm"]["F-P"]["C1_rc_value"]["verdict"] == NOT_MEASURED
         and r["rc_inferences"]["F-P"]["rc_inferred"] == 0
         and r["rc_inferences"]["F-P"]["inference_basis"] == ["C2_terminal_marker", "C3_artefact_present", "C4_age_guard", "C5_no_fatal_token"]
         and "rc_record" in r["not_measured"]["G1"]["F-P"])
    unit("U27 (B) the rc RECORD is absent AND C2 fails (no terminal marker) -> REFUSAL: "
         "NOT MEASURED is available ONLY when the other four conditions hold",
         refused(_fix(tmp, tw(rc_record={"F-P"}, terminal={"F-P": False}))))
    unit("U28 (B) the rc RECORD is absent but the harness rc reads NON-ZERO -> REFUSAL: "
         "R-RC relaxes a missing record, never a positive reading of failure",
         refused(_fix(tmp, tw(rc_record={"X-P"}, rc={"X-P": 1}))))
    unit("U29 (C) FOAM FATAL ERROR in the X-S log at rc = 0 -> REFUSAL (C5 refuses "
         "regardless of rc, so R-RC can never launder a crash)",
         refused(_fix(tmp, tw(fatal={"X-S": "--> FOAM FATAL ERROR: something"}))))
    unit("U30 (C) a SIGNAL token at rc = 0 -> REFUSAL",
         refused(_fix(tmp, tw(fatal={"F-S": "mpirun noticed that process rank 0 exited on signal 9"}))))

    # ================= (D) THE CHARTER-4 TRIVIAL BASELINE ===========================
    r = grade(_fix(tmp, tw(tb_pass={"P": {("shape", 0), ("shape", 3), ("shape", 6), ("shape", 7), ("patchV", 1)}, "S": set()})))
    unit("U31 (D) PLANTED -- the DELIBERATELY WRONG step AGREES on 5/5 of the PATCHED row "
         "-> G-TB GATE FAIL, that row's G5 verdict WITHDRAWN to NOT A RESULT, item NOT A "
         "RESULT, P7 MISS (DAFOAM_CHARTER.md section 4)",
         r["gates"]["G_TB_PATCHED"]["verdict"] == "GATE FAIL"
         and r["gates"]["G_TB_PATCHED"]["n_passing_band_D_at_the_WRONG_step"] == 5
         and r["rows"]["PATCHED"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT"
         and r["predictions"]["P7_trivial_baseline_fails_ge4_of_5_on_PATCHED"] == "MISS")
    r = grade(_fix(tmp, tw(tb_pass={"P": {("shape", 0)}, "S": set()})))
    unit("U32 (D) ONE component passing at the wrong step is inside TB_MAX_PASSING -> G-TB "
         "PASS, row PASS, P7 still HIT (4 of 5 failing)",
         r["gates"]["G_TB_PATCHED"]["verdict"] == "PASS" and r["rows"]["PATCHED"] == "PASS"
         and r["predictions"]["P7_trivial_baseline_fails_ge4_of_5_on_PATCHED"] == "HIT")

    # ================= (E) THE CONSTRAINT GRADIENT FAILS ALONE ======================
    r = grade(_fix(tmp, tw(err_cl={"S": {("shape", 0): 7.0}})))
    unit("U33 (E) PLANTED 7 % error on the shipped CONSTRAINT gradient dCL/dx[shape 0] "
         "while dCD/dx is clean -> G5 CD PASS, G5c CL GATE FAIL, SHIPPED row GATE FAIL: the "
         "constraint gradient is shown able to fail INDEPENDENTLY of the objective",
         r["gates"]["G5_SHIPPED"]["G5_CD"]["verdict"] == "PASS"
         and r["gates"]["G5_SHIPPED"]["G5c_CL"]["verdict"] == "GATE FAIL"
         and r["gates"]["G5_SHIPPED"]["G5c_CL"]["n_gate_fail"] == 1
         and r["rows"]["SHIPPED"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(err_cl={"P": {("shape", 3): 3.0}})))
    unit("U34 (E) P6 is scored on the AGGREGATE, not on the component verdicts: a 3.0 % CL "
         "error on one patched component leaves EVERY component inside band D (5 %) and the "
         "row PASS, while the P6 aggregate bar of 1.0 % is crossed -> P6 MISS",
         r["gates"]["G5_PATCHED"]["G5c_CL"]["verdict"] == "PASS"
         and r["gates"]["G5_PATCHED"]["G5c_CL"]["n_gate_fail"] == 0
         and r["gates"]["G5_PATCHED"]["G5c_CL"]["aggregate_rel_err_pct"] > PRED["P6_patched_CL_agg_max_pct"]
         and r["predictions"]["P6_patched_row_CL_constraint_gradient_PASS"] == "MISS")

    # ================= the five rule-4 clauses, PRINTED INDIVIDUALLY ================
    r = grade(_fix(tmp))
    want = {"C1_rc_value", "C2_terminal_marker", "C3_artefact_present", "C4_age_guard", "C5_no_fatal_token"}
    unit("U35 the five rule-4 clauses are present and named INDIVIDUALLY for every one of "
         "the five arms (Sanaa 2026-08-27 s0)",
         all(set(r["rule4_clauses_per_arm"][a]) == want for a in ARMS_REQUIRED))


    # ================= SO-1aR: THE ONE INSTRUMENT CHANGE, DRIVEN BOTH DIRECTIONS =====
    # Every unit below reads REAL BYTES from artefacts on disk.  The plant is inserted
    # into the ARTEFACT the grader actually opens, never into a helper.

    # ---- the fixtures ARE the artefacts they claim to be ---------------------------
    md5ok, md5got = True, {}
    for _p, _want in sorted(FIXTURE_MD5.items()):
        _h = (hashlib.md5(open(_p, "rb").read()).hexdigest()
              if os.path.isfile(_p) else "ABSENT")
        md5got[os.path.basename(_p)] = _h
        md5ok = md5ok and _h == _want
    unit("U36 THE REAL FIXTURES HAVE NOT DRIFTED: both are byte-identical to the "
         "artefacts they were copied from, by md5 frozen in PREREGISTRATION.md s7 "
         "(got %s)" % md5got, md5ok)

    # ---- (a) THE FALSE POSITIVE, ON THE REAL BYTES THAT CAUSED IT ------------------
    root_banner = _fix(tmp)
    r = grade(root_banner)
    c5m = r["rule4_clauses_per_arm"]["MESH"]["C5_no_fatal_token"]
    unit("U37 (a) THE REAL BANNER ALONE DOES NOT REFUSE: SO-1a's own "
         "`MESH/checkMesh.log:18` line, verbatim, sits in the MESH artefact and the "
         "item is PASS with C5 PASS on MESH",
         r["verdict"] == "PASS" and c5m["verdict"] == "PASS")
    unit("U38 (a) THE EXCLUSION IS COUNTED AND PRINTED: MESH C5 records exactly 1 "
         "benign line excluded, naming the FILE, the LINE, the token and WHY -- a "
         "suppression a reader cannot see is the same defect wearing the other hat",
         c5m["n_benign_lines_excluded"] == 1
         and c5m["benign_lines_excluded"][0]["file"] == "checkMesh.log"
         and c5m["benign_lines_excluded"][0]["tokens"] == ["Floating point exception"]
         and c5m["benign_lines_excluded"][0]["line"] == 1
         and "ENABLEMENT NOTICE" in c5m["benign_lines_excluded"][0]["why_benign"]
         and c5m["files_scanned"] == ["MESH_x.log", "checkMesh.log"])

    # ---- THE CONTRAST, EXECUTED: the UNREPAIRED comparator on the SAME root --------
    old_ref, old_det = "IMPORT FAILED", {}
    try:
        import importlib.util as _ilu
        _sp = _ilu.spec_from_file_location("so1a_frozen", SO1A_FROZEN_GRADER)
        _m = _ilu.module_from_spec(_sp)
        _sp.loader.exec_module(_m)
        try:
            _m.grade(root_banner)
            old_ref = "NO REFUSAL"
        except _m.Refusal as _e:
            old_ref = "REFUSED"
            old_det = json.loads(str(_e))["detail"]
    except Exception as _e:                                   # noqa: BLE001
        old_ref = "IMPORT/RUN ERROR: %s" % _e
    unit("U39 (a, THE CONTRAST) SO-1a's FROZEN COMPARATOR, IMPORTED AND RUN ON THE "
         "SAME FIXTURE ROOT, REFUSES on that same benign banner with "
         "C5_fatal_token_in_arm_output=['Floating point exception'] -- the defect and "
         "the repair executed side by side, not described (got %s)" % old_ref,
         old_ref == "REFUSED"
         and old_det.get("C5_fatal_token_in_arm_output") == ["Floating point exception"]
         and old_det.get("arm") == "MESH")
    unit("U40 (a, SO-1a's SECOND DEFECT) the UNREPAIRED refusal's `log` field names "
         "the ARM log, which contains ZERO occurrences of the token it cites, while "
         "the repaired refusal carries `token_sites` naming file AND line",
         old_det.get("log") == "MESH_x.log"
         and "Floating point exception" not in open(
             os.path.join(root_banner, "MESH_x.log"), errors="replace").read())

    # ---- (b) REAL CRASHES STILL REFUSE, EACH BESIDE THE BANNER ---------------------
    unit("U41 (b/c) a REAL `FOAM FATAL ERROR` appended to the MESH artefact BELOW the "
         "banner -> REFUSAL: a benign line NEVER suppresses a crash in the same file",
         refused(_fix(tmp, tw(fatal_art={"MESH": "--> FOAM FATAL ERROR: \n"
                                                 "    keyword nCells is undefined\n"}))))
    unit("U42 (b) a REAL SIGFPE STACK TRACE with NO shell line -> REFUSAL.  The token "
         "is the handler symbol adopted from head_engineer.py:188 and is HARD-CODED "
         "here, not read from FATAL_TOKENS, so deleting it from the tuple fails this "
         "unit",
         refused(_fix(tmp, tw(fatal_art={"MESH": "#0  Foam::error::printStack(...)\n"
                                                 "#1  Foam::sigFpe::sigHandler(int) at ??:?\n"}))))
    unit("U43 (b) OpenMPI's REALISTIC multi-rank report -- `mpirun noticed that "
         "process rank 2 exited on signal 8 (Floating point exception).` -- REFUSES.  "
         "It is NOT line-initial and carries NO handler symbol, which is exactly why "
         "head_engineer.py's `^` anchor was NOT adopted",
         refused(_fix(tmp, tw(fatal_art={"MESH": "mpirun noticed that process rank 2 "
                                                 "exited on signal 8 (Floating point "
                                                 "exception).\n"}))))

    # ---- (c) THE CRASH IS NAMED, NOT THE BANNER -----------------------------------
    crash_det = {}
    try:
        grade(_fix(tmp, tw(fatal_art={"MESH": "--> FOAM FATAL ERROR: boom\n"})))
    except Refusal as _e:
        crash_det = json.loads(str(_e))["detail"]
    unit("U44 (c) THE REFUSAL NAMES THE CRASH LINE AND ITS FILE, NOT THE BANNER: "
         "exactly one site, in `checkMesh.log`, on the line carrying FOAM FATAL "
         "ERROR -- line 6, below the banner on line 1 -- and the banner is NOT a site",
         [x["file"] for x in crash_det.get("token_sites", [])] == ["checkMesh.log"]
         and crash_det["token_sites"][0]["tokens"] == ["FOAM FATAL ERROR"]
         and crash_det["token_sites"][0]["line"] == 6
         and crash_det.get("files_scanned") == ["MESH_x.log", "checkMesh.log"])

    # ---- the line split loses no token --------------------------------------------
    lost = [t for t in FATAL_TOKENS
            if not refused(_fix(tmp, tw(fatal_art={"MESH": "xx %s yy\n" % t})))]
    unit("U45 THE LINE SPLIT LOSES NO TOKEN: each of the %d registered FATAL_TOKENS, "
         "planted ONE AT A TIME on its own line in the real-shaped artefact, REFUSES "
         "(lost: %s)" % (len(FATAL_TOKENS), lost or "none"), not lost)

    # ---- THE REAL 339-LINE np=4 SOLVER LOG, THROUGH THE REAL GRADING PATH ----------
    real_log = open(FIXTURE_SOLVERLOG, errors="replace").read()
    r = grade(_fix(tmp, tw(log_extra={"X-S": real_log})))
    c5x = r["rule4_clauses_per_arm"]["X-S"]["C5_no_fatal_token"]
    unit("U46 A REAL 339-LINE np=4 SOLVER LOG THIS LANE DID NOT PRODUCE (D12R2W3, "
         "4 banners, 5 End lines, 0 real fatal tokens) is appended to the X-S arm log "
         "-> item PASS, C5 PASS, EXACTLY 4 benign lines excluded and counted",
         r["verdict"] == "PASS" and c5x["verdict"] == "PASS"
         and c5x["n_benign_lines_excluded"] == 4
         and all(x["why_benign"] for x in c5x["benign_lines_excluded"]))
    planted = real_log.splitlines(True)
    planted.insert(300, "--> FOAM FATAL ERROR: planted below all four banners\n")
    unit("U47 THE SAME REAL LOG WITH ONE CRASH PLANTED BELOW ALL FOUR BANNERS -> "
         "REFUSAL.  Four benign lines above it suppress nothing; the whole-file "
         "predicate SO-1a used could not have told these two logs apart",
         refused(_fix(tmp, tw(log_extra={"X-S": "".join(planted)}))))

    # ---- the UNREPAIRED predicate is kept for the contrast and is NOT on the path --
    _tree = ast.parse(open(os.path.abspath(__file__)).read())
    _callers = set()
    for _fn in [x for x in ast.walk(_tree) if isinstance(x, ast.FunctionDef)]:
        for _nd in ast.walk(_fn):
            if isinstance(_nd, ast.Name) and _nd.id == "fatal_tokens_in":
                _callers.add(_fn.name)
    _real = open(FIXTURE_CHECKMESH, errors="replace").read()
    _old_hits = fatal_tokens_in(_real)
    _sites, _ben = fatal_token_sites(_real, "checkMesh.log")
    unit("U48 THE CONTRAST AT THE PREDICATE LEVEL, ON SO-1a's REAL 99-LINE "
         "`MESH/checkMesh.log`: the UNREPAIRED whole-file predicate returns %s while "
         "the repaired scanner returns 0 sites and 1 counted benign line at line 18 "
         "-- and the unrepaired predicate is referenced by NO function on the grading "
         "path (by AST over this module's own source: %s)"
         % (_old_hits, sorted(_callers) or "nothing"),
         _old_hits == ["Floating point exception"] and _sites == []
         and len(_ben) == 1 and _ben[0]["line"] == 18
         and "g_completion" not in _callers and "grade" not in _callers)

    # ---- DELTA 2: the control write path cannot collide with the predecessor's ----
    _r49 = grade(_fix(tmp))
    _cf = _r49["controls"]["grader_plant_S"]["file"]
    unit("U49 (DELTA 2, WRITE PATH) the grader's own planted-control copy is written "
         "under `grader_controls_SO1aR/`, NOT under SO-1a's `grader_controls/`, so a "
         "re-grade can never overwrite a predecessor's control artefact in a "
         "preserved run root (wrote %s)" % os.path.basename(os.path.dirname(_cf)),
         os.path.basename(os.path.dirname(_cf)) == "grader_controls_SO1aR"
         and os.path.isfile(_cf))


    # ================= THE BIRTH GATE, DRIVEN (Sanaa 2026-08-28T17:01Z) =============
    def refused_graded(root):
        try:
            graded(root, os.path.join(tmp, "bw_%d" % int(time.time() * 1e6)))
            return False
        except Refusal:
            return True

    _bw = os.path.join(tmp, "bw_clean")
    _ok, _legs = birth(_fix(tmp), _bw)
    unit("U50 THE BIRTH BATTERY RUNS AND EVERY LEG IS BORN on a clean root: %d legs, "
         "each naming its PRODUCER, its READER and the NON-ZERO it was shown seeing"
         % len(_legs),
         _ok and len(_legs) == 12 and all(l["born"] for l in _legs)
         and all(l["detail"].get("reader") for l in _legs))

    unit("U51 (THE GATE CLOSES) a root whose X-P ledger row is MISSING -> the ledger "
         "reader cannot be born on it AND the UNBORN inspect fallback would be reached "
         "-> graded() REFUSES on BIRTH and NOTHING IS GRADED",
         refused_graded(_fix(tmp, tw(drop_row={"X-P"}))))

    _line, _meta = producer_ledger_row(1, "1 false")
    _fp = os.path.join(tmp, "u52_ledger.txt")
    open(_fp, "w").write("ITEM=SO1a\n" + (_line or ""))
    _got = (read_ledger(_fp).get("X-S") or {}) if _line else {}
    unit("U52 (THE AV2R LESSON) THE NON-ZERO rc IS EMITTED BY THE REAL PRODUCER'S OWN "
         "`echo` STATEMENT, lifted from the FROZEN so1a_run_arm.sh by exact content "
         "match (line %s) and EXECUTED, then read through the real reader -- so a "
         "fixture writing a schema the producer never emits cannot arise (read back "
         "rc=%s exit=%s)" % (_meta, _got.get("rc"), _got.get("inspect_exit")),
         bool(_line) and _got.get("rc") == 1 and str(_got.get("inspect_exit")) == "1")

    _save = SO1A_RUN_ARM
    try:
        _empty = os.path.join(tmp, "u53_no_anchor.sh")
        open(_empty, "w").write("#!/bin/bash\necho hello\n")
        globals()["SO1A_RUN_ARM"] = _empty
        _l2, _m2 = producer_ledger_row(1, "1 false")
        _ok2, _legs2 = birth(_fix(tmp), os.path.join(tmp, "bw_u53"))
    finally:
        globals()["SO1A_RUN_ARM"] = _save
    unit("U53 (A CONTROL ON THE CONTROL) if the producer's emitting statement can no "
         "longer be found in the frozen script -- the schema drifted, or the anchor "
         "moved -- producer_ledger_row returns NOTHING and the B2 legs are NOT BORN, "
         "so the gate closes instead of silently falling back to a hand-built row",
         _l2 is None and _m2 == 0 and not _ok2
         and any(l["leg"].startswith("B2_") and not l["born"] for l in _legs2))

    unit("U54 (THE GATE CLOSES ON THE PRODUCER-WRITTEN PLANT) a root whose CTRL row "
         "carries a BROKEN plant -> B9 cannot be born -> graded() REFUSES on BIRTH.  "
         "The plant that must survive is the one so1a_xf.py wrote DURING THE RUN, not "
         "one this comparator adds afterwards",
         refused_graded(_fix(tmp, tw(ctrl_ok=False))))

    print("SO1aR GRADER SELFTEST units=%d expected=%d failures=%d python_O=%s" % (n, EXPECTED_UNITS, len(fails), not __debug__))
    print("COUNTING UNITS MEASURES THIS SELFTEST'S SIZE, NOT ITS COVERAGE.")
    if n != EXPECTED_UNITS or fails:
        print("SELFTEST FAIL: %s" % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS)))
        return 2
    print("SO1aR GRADER SELFTEST PASS %d/%d (counted against the frozen EXPECTED_UNITS)" % (n, EXPECTED_UNITS))
    return 0


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmpdir", default="/tmp")
    ap.add_argument("--birth", action="store_true",
                    help="run the birth battery on --root and stop; grades nothing")
    ap.add_argument("--workdir", default=None,
                    help="where the birth battery writes its own control copies; "
                         "defaults under --tmpdir so the run root is never mutated")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if count_asserts(os.path.abspath(__file__)) != 0:
        print("REFUSAL: this comparator carries an assert statement (L-332)"); return 2
    if a.selftest:
        d = os.path.join(a.tmpdir, "so1ar_selftest_%d" % os.getpid()); os.makedirs(d, exist_ok=True)
        return selftest(d)
    if not a.root:
        print("usage: so1ar_grade.py --root <run root> [--out FILE] | "
              "--birth --root <run root> | --selftest"); return 64
    wd = a.workdir or os.path.join(a.tmpdir, "so1ar_birth_%d" % os.getpid())
    if a.birth:
        os.makedirs(wd, exist_ok=True)
        ok, legs = birth(a.root, wd)
        print(json.dumps({"item": "CURRICULUM-%s" % ITEM,
                          "birth": {"verdict": "BORN" if ok else "NOT BORN",
                                    "n_legs": len(legs), "legs": legs}},
                         indent=1, default=str))
        return 0 if ok else 2
    try:
        r = graded(a.root, wd)
    except Refusal as e:
        print("REFUSAL: %s -> NOT A RESULT" % e)
        if a.out:
            json.dump({"item": "CURRICULUM-%s" % ITEM, "verdict": "NOT A RESULT", "refusal": str(e)}, open(a.out, "w"), indent=1)
        return 2
    print(json.dumps(r, indent=1, default=str))
    if a.out:
        json.dump(r, open(a.out, "w"), indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
