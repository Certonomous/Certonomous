#!/usr/bin/env python3
"""Curriculum SO-2MR COMPARATOR -- NACA0012 INCOMPRESSIBLE, the FD-VERIFIED
PITCHING-MOMENT GRADIENT RUNG.  TWO ROWS (SHIPPED + PATCHED), adjoint X against a
central-FD table G, on the NEW functional `CMZ`.  FROZEN by md5 in the driver
before any container starts.  Computes nothing about physics; renders verdicts
from the FIXED vocabulary only (PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING).

DERIVED from `curriculum_SO1a/so1a_grade.py` (md5 6966d19eeccd275b45fe9a5492eef6d2)
with the registered deltas in so2mr_grade_DELTAS_from_so1a_grade.diff.  SIX of them
are new machinery rather than renaming, and each closes a MEASURED failure:

  (A) THE ROW LABEL IS DERIVED FROM ONE REGISTERED TABLE AND FROM NOTHING ELSE
      (standing rule 14; L-221/L-222).  THIRTY MINUTES BEFORE THIS FILE WAS
      WRITTEN, SO-1c DIED AT ITS SECOND ARM because SO-1bR labelled per-row
      artefacts `P`/`S` while SO-1c's consumers compared against
      `PATCHED`/`SHIPPED`; amendment R8 repaired ONE call site and there were
      THREE.  SO-1a's own grader carries the same shape (`rk = "S" if
      arm.endswith("-S") else "P"`, so1a_grade.py:897, and `g5["S"]` / `g5["P"]`
      at :752-762).  Here:
        * `ROW_OF_ARM` is the ONE registration.  `row_of()` is the ONLY function
          that subscripts it, and `audit_row_label_sites()` REFUSES if a SECOND
          subscript site appears anywhere in this file.
        * the short spellings `S` and `P` DO NOT EXIST.  Row-keyed dicts are keyed
          by the row LABELS themselves.
        * `ARM_LABELS` and `ROW_LABELS` are DISJOINT sets, checked, so an artefact
          or a ledger field carrying an arm name where a row label belongs
          REFUSES rather than resolving to something.
        * every FORBIDDEN derivation (`endswith("-S")`, `arm.split`, `row[0]`, a
          bare `"S"`/`"P"` literal, a conditional expression choosing between
          them) is detected in this file's own source and DRIVEN to fire on a
          PLANTED bad site, so a NEW unrepaired call site cannot appear silently.

  (B) C5 IS SCANNED PER FILE AND PER LINE, NEVER AS A WHOLE-FILE SUBSTRING TEST.
      `so1a_grade.py:122-125` scans `token in text` over the WHOLE arm log, so a
      single benign line anywhere refuses the arm and the offending line is never
      named.  Here `fatal_scan()` walks FILE by FILE and LINE by LINE, applies
      EXACTLY ONE registered benign exclusion (`^\\s*trapFpe:\\s`), COUNTS AND
      NAMES every exclusion on the record, and adds `Foam::sigFpe::sigHandler` as
      an extra positive token.  The forbidden whole-file shape is detected by an
      AST pass over this file's own source, DRIVEN IN BOTH DIRECTIONS: zero on
      this file, and >= 1 on a planted source that contains it.

  (C) THE GRADED FUNCTIONAL IS `CMZ`, AND ITS VALUE IS GATED BEFORE ITS JACOBIAN.
      G-CMV bands the baseline moment coefficient at |CMZ| <= 0.02 (symmetric
      section, quarter-chord reference).  A mis-declared reference point, axis or
      scale cannot sit inside that band.  Non-finite or absent -> NOT A RESULT.

  (D) G-NZ, THE STRUCTURAL NON-ZERO, IS THE MIRROR OF SO-2a's EXACT-ZERO GATE.
      `d(CMZ)/d(patchV[1])` must be NON-zero on BOTH sides.  A BLIND READER --
      wrong key, wrong slice, empty tuple -- FAILS this gate instead of passing
      it, which is the whole reason it is worth having, and it is DRIVEN that way
      in the selftest.

  (E) THE PLATEAU IS PROVED PER PAIR AND EVERY EXCLUSION IS COUNTED AND NAMED.
      Fewer than MIN_GRADED graded pairs on a row, or more than
      MAX_EXCLUDED_PCT of candidates excluded, reads NOT A RESULT: a gate that
      grades a quarter of its own Jacobian is not grading the Jacobian.

  (F) THE PLANTED CONTROLS RUN IN BOTH DIRECTIONS, IN THE SAME INVOCATION AS THE
      VERDICT THEY LICENSE (standing rule 3; PREREGISTRATION.md section 7).
      Direction A: the instrument's CTRL tuple is re-read FROM DISK and the
      grader writes and re-reads its own planted copy of the G table.
      Direction B: a copy of the REAL X artefact with PLANT added to one
      d(CMZ)/d(shape) entry must make G5m read GATE FAIL, and a copy with
      d(CMZ)/d(patchV[1]) forced to 0.0 must make G-NZ read GATE FAIL.  A gate
      never shown failing is not known to be load-bearing (L-314).

G-TB IS COMPOSED ONLY ONTO A ROW WHOSE G5m IS ALREADY `PASS`.  SO-2a's first
draft composed it onto every row, and a driven unit showed that would turn a real
GATE FAIL -- the most valuable output this rung can produce, and the registered
prediction for the SHIPPED row -- into NOT A RESULT.  A comparator that converts
findings into refusals is worse than one that refuses too often.

L-342 (Sanaa): FIELDS_PHYSICS absent -> REFUSE; FIELDS_INFRASTRUCTURE absent ->
NOT_MEASURED, disclosed beside the verdict, never composed to PASS;
present-but-garbage -> REFUSE.  The grader's OWN rc is INFRASTRUCTURE and is
never the verdict.  L-332: NO `assert` anywhere; this module counts ast.Assert
nodes in its own source and refuses on any.  No unconditional success print.

REGISTERED READ LOCATIONS -- named EXPLICITLY, never hunted for.  A read that
goes looking until it finds something will always find something, so every nested
location this comparator touches is written out here and nowhere is a key sought
by recursive descent:
    X artefact   j["CMZ_baseline"], j["CD_baseline"], j["CL_baseline"]
                 j["adjoint"][<output>][<dv>][<index>]
                 j["identity"]["libidwarp_so_md5"], j["nprocs"]
    G artefact   j["components_requested"], j["steps"], j["tb_steps"]
                 j["control_outputs"], j["eta_used"], j["CMZ_baseline"]
                 j["rows"][k]["dv"|"idx"|"status"]
                 j["rows"][k]["fd"][<repr(step)>][<d-key>|"ok"]
                 j["rows"][k]["tb"][<repr(step)>][<d-key>|"ok"]
                 j["rows"][CTRL]["fd"][<repr(CTRL_STEP)>][<control output>]
                 j["rows"][CTRL]["planted"][<control output>]
    ledger row   the LEDGER_RE named groups, and nothing outside them
    mesh         MESH/checkMesh.log, the line matching ^\\s*cells:\\s+(\\d+)
"""

import ast
import glob
import json
import math
import os
import re
import shutil
import sys
import time

# ---- REGISTERED CONSTANTS (PREREGISTRATION.md; the document governs) ----------------
ITEM = "SO2MR"
BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-SO2MR-a1-naca0012-moment-gradient"

# =====================================================================================
# (A) THE ONE REGISTERED IDENTIFIER MAPPING.  RULE 14.
#
# ARM_LABELS and ROW_LABELS are DISJOINT.  ROW_OF_ARM is the ONLY bridge between
# them and `row_of()` is the ONLY function that subscripts it.  Nothing in this
# file derives a row from a suffix, a split, a first character or a conditional
# expression, and `audit_row_label_sites()` proves that by reading this file's own
# bytes -- driven against a PLANTED bad site so the zero is evidence.
# =====================================================================================
ARM_LABELS = ("MESH", "X-S", "G-S", "X-P", "G-P")
ROW_LABELS = ("SHIPPED", "PATCHED")
ROW_OF_ARM = {"MESH": "SHIPPED", "X-S": "SHIPPED", "G-S": "SHIPPED",
              "X-P": "PATCHED", "G-P": "PATCHED"}
# The two GRADIENT arm pairs, per row: (X arm, G arm).  Registered as a table for
# the same reason -- so no consumer reconstructs "the X arm of the patched row".
ARMS_OF_ROW = {"SHIPPED": ("X-S", "G-S"), "PATCHED": ("X-P", "G-P")}
FORBIDDEN_ROW_DERIVATIONS = (
    (r'endswith\(\s*[\'"]-S[\'"]', "arm-suffix test endswith('-S')"),
    (r'endswith\(\s*[\'"]-P[\'"]', "arm-suffix test endswith('-P')"),
    (r'\barm\s*\.\s*split\s*\(', "arm.split(...) -- a row reconstructed from a name"),
    (r'\brow\s*\[\s*0\s*\]', "row[0] -- a label derived from a coincidence of spelling"),
    (r'[\'"]S[\'"]\s+if\b', "conditional expression choosing the short spelling 'S'"),
    (r'[\'"]P[\'"]\s+if\b', "conditional expression choosing the short spelling 'P'"),
    (r'\[\s*[\'"]S[\'"]\s*\]', "subscript by the short spelling 'S'"),
    (r'\[\s*[\'"]P[\'"]\s*\]', "subscript by the short spelling 'P'"),
    (r'ARM_ROW\b', "the SO-1a name ARM_ROW -- superseded by ROW_OF_ARM"),
)
ROW_OF_ARM_SUBSCRIPT_RE = re.compile(r"ROW_OF_ARM\s*\[")
ROW_OF_ARM_SUBSCRIPTS_ALLOWED = 1          # exactly one, inside row_of()

ARM_KIND = {"MESH": "SCRIPT", "X-S": "SOLVER", "G-S": "SOLVER", "X-P": "SOLVER", "G-P": "SOLVER"}
# np = 1 ON EVERY ARM by registration: DAFOAM_CHARTER.md section 5 (serial before
# parallel; a gradient verified at one np is a statement about THAT np).
ARM_RANKS = {"MESH": 1, "X-S": 1, "G-S": 1, "X-P": 1, "G-P": 1}
ARTEFACT = {"MESH": "checkMesh.log", "X-S": "so2mr_X.json", "G-S": "so2mr_F.json",
            "X-P": "so2mr_X.json", "G-P": "so2mr_F.json"}
TERMINAL = {"X-S": "SO2MR_X_WRITTEN", "G-S": "SO2MR_F_WRITTEN",
            "X-P": "SO2MR_X_WRITTEN", "G-P": "SO2MR_F_WRITTEN"}
# THE AGE-GUARD DATUM IS RESOLVED BY EXISTENCE, NEVER BY NAME (SO-1a delta (A);
# AV-1/AV-2 died on that alone).  BOTH names are candidates, in this order.
DATUM_CANDIDATES = {"MESH": ("0.orig/U", "0.orig/U.gz"), "X-S": ("0/U", "0/U.gz"),
                    "G-S": ("0/U", "0/U.gz"), "X-P": ("0/U", "0/U.gz"),
                    "G-P": ("0/U", "0/U.gz")}
DATUM_FILE = ".so2mr_age_datum"
CONTROLDICT_REL = os.path.join("system", "controlDict")

# ---- (B) C5: PER FILE, PER LINE, with EXACTLY ONE registered benign exclusion -------
FATAL_TOKENS = ("FOAM FATAL ERROR", "FOAM FATAL IO ERROR", "Segmentation fault",
                "SIGSEGV", "SIGKILL", "MPI_ABORT", "signal 9", "Signal 11",
                "Floating point exception", "Foam::sigFpe::sigHandler")
# The ONE benign exclusion, registered at PREREGISTRATION.md section 5 G1 C5.
# `trapFpe: ...` is OpenFOAM's own start-up banner announcing that floating-point
# trapping is ENABLED; it is not a report that anything trapped.  Every line it
# excludes is COUNTED AND NAMED on the record.
BENIGN_EXCLUSION_PATTERNS = ((r"^\s*trapFpe:\s", "OpenFOAM start-up banner: FPE trapping enabled"),)
BENIGN_EXCLUSIONS = tuple((re.compile(p), why) for p, why in BENIGN_EXCLUSION_PATTERNS)
# The FORBIDDEN whole-file substring shape (so1a_grade.py:122-125), detected by AST
# over this file's own source and driven in BOTH directions.
WHOLE_FILE_TEXT_NAMES = ("text", "hay", "mtext", "content", "blob", "whole", "alltext")
TOKEN_LOOP_NAMES = ("t", "tok", "token")

CAPS = {"MESH": 5.0, "X-S": 12.0, "G-S": 25.0, "X-P": 12.0, "G-P": 25.0}
ITEM_CEILING_CORE_MIN = 79.0
PREDICTED_CORE_MIN = {"MESH": 0.20, "X-S": 1.50, "G-S": 3.60, "X-P": 1.50, "G-P": 3.50}
CELLS_EXPECTED = 4032
FD_BAND_PCT = 5.0            # band D, per graded PAIR (D4:82; D7FR:228-229, by citation)
AGG_BAND_PCT = 5.0           # band E, aggregate vector-relative (same sources)
PLATEAU_TOL_PCT = 10.0
MIN_GRADED = 2               # PREREGISTRATION.md section 6
MAX_EXCLUDED_PCT = 75.0      # PREREGISTRATION.md section 6
NEAR_ZERO_ABS = 1.0e-14
COMPONENTS_REGISTERED = [["shape", 0], ["shape", 3], ["shape", 6], ["shape", 7], ["patchV", 1]]
STEPS_REGISTERED = {"shape": [1.0e-2, 1.0e-3, 1.0e-4], "patchV": [1.0e-1, 1.0e-2, 1.0e-3]}
TB_STEPS_REGISTERED = {"shape": [1.0e-8], "patchV": [1.0e-8]}
# RULING 1 (dafoam-supervisor, 2026-08-31).  BEFORE: {"shape": [1e-8], "patchV":
# [1e-6]}.  AFTER: 1e-8 on BOTH, which is what PREREGISTRATION.md section 5 (G-TB)
# and section 8 (P6) FREEZE for all five components; 1e-6 appears nowhere in that
# document.  The 1e-6 was carried forward from SO-1a's real artefact (tb_steps
# {'patchV': [1e-06], 'shape': [1e-08]}), which is where the fixture's tb block
# comes from -- so the FIXTURE is repaired at the same registered location rather
# than the DOCUMENT being amended to fit the code.  No threshold moves.
TB_MAX_PASSING = 1
CTRL_STEP = 1.0e-3
# ---- DIRECTION A's plant.  ABSOLUTE, and absolute is CORRECT here: direction A
# ---- asks whether a reader can see a NON-ZERO where the reference is EXACTLY
# ---- 0.0, so a fixed known magnitude read back to 1e-12 is the whole test.  It
# ---- crosses no band and is asked to cross none.  Carried from SO-2M unchanged,
# ---- and it is the value so2mr_xm.py writes (cross-checked by selftest S1).
PLANT = 1.234e-03

# =====================================================================================
# DIRECTION B's PLANT **RULE** -- SO-2MR's ONE SUBSTANTIVE DELTA FROM SO-2M
# =====================================================================================
# SO-2M registered direction B's plant as the SAME ABSOLUTE 1.234e-03 and its frozen
# comparator then REFUSED (grader_rc=2, item NOT A RESULT) after a clean five-arm
# chain, verbatim:
#
#   REFUSE CONTROL -- G5m_did_NOT_flip_to_GATE_FAIL_under_the_planted_copy
#   d_ref = -0.04976246220706002, plant = 0.001234,
#   plant_needed_to_cross_band_D = 0.002488123110353001,
#   plant_is_sufficient = false, live_verdict PASS, planted_verdict PASS,
#   flipped false, planted_component ["shape", 6], row PATCHED
#
# THE COMPARATOR WAS RIGHT AND IS NOT REPAIRED HERE.  It refused rather than report
# a PASS from a gate it had not shown able to GATE FAIL -- standing rule 3 at full
# strength.  What was wrong was the SIZE of the plant, and the transferable root
# cause is this: AN ABSOLUTE PLANT MAGNITUDE DOES NOT PORT ACROSS FUNCTIONALS.  The
# same 1.234e-03 is 33.76 % of the CD-scale reference SO2a and SO-1cR plant against
# (|d_ref| ~ 0.00365546) and sails across a 5 % band; against CMZ's reference, ~14x
# larger, it is 2.4798 % and cannot cross a 5 % band by construction.
#
# THE RULE, FIXED AT FREEZE AND NOT CHOSEN AFTER SEEING AN ANSWER.  For the target
# graded pair i with FD reference d_ref_i and adjoint value J_i:
#
#     P_i = FLIP_PLANT_K * (FD_BAND_PCT / 100) * |d_ref_i|          (MAGNITUDE)
#     s_i = +1 if J_i >= d_ref_i else -1                            (SIGN)
#     J_i' = J_i + s_i * P_i
#
# s_i moves J_i AWAY from d_ref_i, so |d_ref_i - J_i'| = |d_ref_i - J_i| + P_i
# EXACTLY -- no cancellation is possible from ANY live position.  Hence
#
#     rel_planted = rel_live + FLIP_PLANT_K * FD_BAND_PCT >= FLIP_PLANT_K * FD_BAND_PCT
#
# and with FLIP_PLANT_K = 2.0 that is >= 10.0 % against a 5.0 % band: the planted
# copy crosses band D BY CONSTRUCTION, with 100 % margin, on every row, at every
# functional scale, whatever the live agreement happens to be.
#
# THIS IS NOT FITTING THE CONTROL TO THE DATA.  The plant's PURPOSE is to
# demonstrate that the gate CAN read GATE FAIL.  A plant too small to cross the
# band demonstrates nothing and is a control in name only.  Scaling it to the band
# is making it do its job.  It moves NO gate, NO threshold, NO band and NO
# acceptance criterion: band D stays 5.0 %, band E stays 5.0 %, every registered
# verdict of every row is computed from the LIVE artefact exactly as SO-2M computed
# it, and the planted copy is never any row's verdict.
FLIP_PLANT_K = 2.0


def flip_plant(d_ref, j_adj):
    """The registered direction-B plant for one graded pair: magnitude by the band
    rule, sign AWAY from the FD reference.  Returns (magnitude, signed_value,
    band_crossing_threshold)."""
    need = FD_BAND_PCT / 100.0 * abs(d_ref)
    mag = FLIP_PLANT_K * need
    sign = 1.0 if j_adj >= d_ref else -1.0
    return mag, sign * mag, need

# ---- the OUTPUT vocabulary, mirroring so2mr_xm.py's registration ----------------------
OUTPUTS = ("CD", "CL", "CMZ")
DKEY_OF_OUTPUT = {"CD": "dCD", "CL": "dCL", "CMZ": "dCMZ"}
GRADED_OUTPUT = "CMZ"
CONTROL_OUTPUTS = ("dCMZ", "dCD", "dCL")
# G-CMV, PREREGISTRATION.md section 5: the moment functional's own VALUE gate,
# banded BEFORE it is read.
CMZ_BASELINE_ABS_MAX = 0.02
# G-NZ, PREREGISTRATION.md section 5: the structural NON-zero on d(CMZ)/d(aoa).
NZ_DV, NZ_IDX, NZ_ABS_MIN = "patchV", 1, 1.0e-8

IMG_DIGEST = {"SHIPPED": "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc",
              "PATCHED": "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"}
SO_MD5 = {"SHIPPED": "f0fcb488e0e98156575cd19548e91663", "PATCHED": "85f59e87253e0a71a813f64ca6e4c425"}
CPUSET_REGISTERED = "9"
DELIVERED_CORES_FLOOR = 1.5
MEMORY_REGISTERED = "4g"                      # G11, PREREGISTRATION.md section 5
PRED = {"P2_CMZ_abs_max": CMZ_BASELINE_ABS_MAX, "P6_tb_min_failing": 4}

FIELDS_PHYSICS = ("rc_value", "oomkilled", "terminal_statement", "age_guard",
                  "no_fatal_token", "core_min", "cap_core_min", "DIGEST", "cpuset")
FIELDS_INFRASTRUCTURE = ("rc_record", "memavail_pre_GiB", "memavail_post_GiB", "delivered",
                         "siblings_pre", "siblings_post", "log", "wall_s")
NOT_MEASURED = "NOT_MEASURED"
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
G6_SENTENCE = ("NOT MEASURED -- AV-2 measured that seeding forward mode makes the primal "
               "FAIL on this exact case on BOTH images (curriculum_AV2/RESULTS.md section 2, "
               "5/5 rows AnalysisError(... Primal solution failed!)).  The reason is a "
               "measurement, not an omission (DAFOAM_CHARTER.md section 2).")
NO_GCI_SENTENCE = ("THERE IS NO GRID FAMILY IN THIS ITEM -- one mesh, 4,032 cells, no "
                   "refinement triple.  NO GCI IS QUOTED and no row may carry one "
                   "(standing rule 5).")
EXPECTED_UNITS = 80   # SO-2M's 74 (itself 66 +3 TB0/TB1/TB2 +5 E1/E2/E3/M1/M2), PLUS
                      # EXACTLY 6 for the direction-B plant-rule sufficiency legs:
                      # B0 / B0b / B0c / B0d (known positive, repair, sign rule, algebra)
                      # and B3 / B4 (driven RED on K, and the restore asserted).
                      # 74 + 6 = 80 and that is the whole arithmetic -- SO-2M's own
                      # +3/+5 are INSIDE its 74 and are NOT added again here.  Legs are
                      # ADDED, none removed, none weakened.


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


# =====================================================================================
# (A) THE ONE BRIDGE, AND THE AUDIT THAT PROVES IT IS THE ONLY ONE
# =====================================================================================
def row_of(arm):
    """THE ONLY function in this file that turns an ARM label into a ROW label.

    Every other consumer calls this.  `audit_row_label_sites()` refuses if a
    second `ROW_OF_ARM[` subscript appears anywhere in this file's bytes, which is
    what makes "every call site uses the registered mapping" a reading rather than
    a claim.  A label that is not an arm REFUSES -- it is never coerced, and
    because ARM_LABELS and ROW_LABELS are disjoint, handing this a ROW label
    (the swapped-artefact case) refuses too."""
    if arm not in ROW_OF_ARM:
        refuse("ROW_LABEL", {"not_a_registered_arm": arm, "arm_labels": list(ARM_LABELS),
                             "row_labels": list(ROW_LABELS),
                             "note": "standing rule 14: a row label is derived from "
                                     "ROW_OF_ARM and from nothing else.  The label sets are "
                                     "DISJOINT, so a swapped artefact refuses here."})
    return ROW_OF_ARM[arm]


def executable_lines(path):
    """Return the source with every COMMENT and every PROSE STRING blanked out,
    line numbering preserved.  Inline string literals used as OPERANDS are KEPT.

    A row-label sweep that reads raw bytes cannot tell a CALL SITE from a
    DOCSTRING that quotes one, and this file's own prose quotes the forbidden
    shapes on purpose in order to name them.  A sweep that blanks EVERY string
    goes too far the other way -- the forbidden shapes are ABOUT string literals
    (`'S' if ...`), so blanking them would buy R1's zero by blinding the sweep to
    exactly the code it hunts.  So: comments go, and so do strings that stand
    ALONE AS A STATEMENT (module, class and function docstrings, and bare string
    expressions); every other literal survives.  BOTH directions are driven in the
    selftest -- a forbidden shape in a comment or a docstring must NOT count, the
    same shape in code MUST."""
    import io
    import tokenize
    src = open(path, errors="replace").read()
    lines = src.split("\n")
    grid = [list(l) for l in lines]
    spans = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                spans.append((tok.start, tok.end))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return lines
    try:
        tree = ast.parse(src)
    except SyntaxError:
        tree = None
    if tree is not None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                    and isinstance(node.value.value, str):
                v = node.value
                spans.append(((v.lineno, v.col_offset), (v.end_lineno, v.end_col_offset)))
    for (r0, c0), (r1, c1) in spans:
        for r in range(r0, r1 + 1):
            if r - 1 >= len(grid):
                break
            row = grid[r - 1]
            a = c0 if r == r0 else 0
            b = c1 if r == r1 else len(row)
            for i in range(a, min(b, len(row))):
                row[i] = " "
    return ["".join(r) for r in grid]


def audit_row_label_sites(path):
    """READ THIS FILE'S OWN EXECUTABLE LINES and report every place a row label
    could be produced.  Returns the forbidden derivations found (with line numbers
    and the reason each is forbidden) and the count of `ROW_OF_ARM[` subscript
    sites.

    THE POINT (standing rule 14, and SO-1c's death 30 minutes before this file was
    written): repairing ONE call site is not applying a lesson.  This audit FAILS
    when a NEW unrepaired site appears, and it is DRIVEN against a PLANTED bad
    site in the selftest so its zero is evidence rather than blindness."""
    src = executable_lines(path)
    forbidden, subs = [], []
    in_registry = False
    for ln, line in enumerate(src, 1):
        # the registry TUPLE itself carries the forbidden patterns as data; it is
        # the one place they may appear, and it is bounded by explicit markers.
        if "FORBIDDEN_ROW_DERIVATIONS = (" in line:
            in_registry = True
        if in_registry:
            if line.startswith(")"):
                in_registry = False
            continue
        if ROW_OF_ARM_SUBSCRIPT_RE.search(line):
            subs.append({"line": ln, "text": line.strip()[:160]})
        for pat, why in FORBIDDEN_ROW_DERIVATIONS:
            if re.search(pat, line):
                forbidden.append({"line": ln, "pattern": pat, "why": why,
                                  "text": line.strip()[:160]})
    ok = (not forbidden) and len(subs) == ROW_OF_ARM_SUBSCRIPTS_ALLOWED
    return {"file": os.path.basename(path), "forbidden": forbidden,
            "row_of_arm_subscript_sites": subs,
            "row_of_arm_subscript_count": len(subs),
            "row_of_arm_subscripts_allowed": ROW_OF_ARM_SUBSCRIPTS_ALLOWED,
            "arm_labels": list(ARM_LABELS), "row_labels": list(ROW_LABELS),
            "label_sets_disjoint": not (set(ARM_LABELS) & set(ROW_LABELS)),
            "scan_mode": "EXECUTABLE LINES ONLY (comments and string literals blanked "
                         "by tokenize, line numbers preserved)",
            "verdict": "OK" if ok else "FORBIDDEN_SITE_PRESENT"}


# =====================================================================================
# (B) THE FORBIDDEN WHOLE-FILE SUBSTRING SCAN, DETECTED BY AST, DRIVEN BOTH WAYS
# =====================================================================================
def whole_file_substring_scans(path):
    """Return every `<token> in <whole-file-text>` comparison in a source file.

    so1a_grade.py:122-125 is exactly this shape and it killed SO-1a's grade: one
    benign line anywhere in a 217 kB log refuses the arm, and the offending line
    is never named.  This detector is run on THIS file (must be zero) and on a
    PLANTED source that contains the shape (must be non-zero) in the same
    selftest, so the zero is a reading."""
    tree = ast.parse(open(path, errors="replace").read())
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare) or len(node.ops) != 1:
            continue
        if not isinstance(node.ops[0], ast.In):
            continue
        left, right = node.left, node.comparators[0]
        if isinstance(left, ast.Name) and isinstance(right, ast.Name):
            if left.id in TOKEN_LOOP_NAMES and right.id in WHOLE_FILE_TEXT_NAMES:
                hits.append({"line": node.lineno, "token_var": left.id, "text_var": right.id})
    return hits


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path, errors="replace").read()))
               if isinstance(n, ast.Assert))


def instrument_constants(path):
    """Read so2mr_xm.py's OWN declared constants out of its source, by AST.

    THE FIXTURE-BLINDNESS PROBLEM, closed here.  A grader selftest whose positive
    fixture is hand-authored from what the READER expects proves only that the
    gate reads the shape the fixture writes and the fixture writes the shape the
    gate reads -- a 51-leg suite in this family was blind to a schema break for
    exactly that reason.  So: the positive fixture is built from a REAL producer
    artefact, and the KEY VOCABULARY is cross-checked against the INSTRUMENT's own
    bytes rather than against this comparator's constants."""
    tree = ast.parse(open(path, errors="replace").read())
    want = {"OUTPUTS", "DKEY_OF_OUTPUT", "GRADED_OUTPUT", "CONTROL_OUTPUTS",
            "COMPONENTS", "STEPS", "TB_STEPS", "CTRL_STEP", "PLANT",
            "OUT_X", "OUT_F", "PRODUCER_MD5", "ITEM"}
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in want:
                try:
                    out[name] = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    pass
    return out


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
        # RULE 14: the ROW field the LAUNCHER wrote is CHECKED against the one
        # registration, never trusted and never used to derive anything.  A ledger
        # carrying an ARM label in the ROW field refuses here -- the label sets are
        # disjoint precisely so that swap cannot resolve.
        if g["ARM"] not in ROW_OF_ARM:
            refuse("ledger", {"row_for_unregistered_arm": g["ARM"], "arm_labels": list(ARM_LABELS)})
        want_row = row_of(g["ARM"])
        if g["ROW"] != want_row:
            refuse("ledger", {"ROW_field_disagrees_with_the_registered_mapping": {
                "arm": g["ARM"], "ledger_ROW": g["ROW"], "registered": want_row,
                "row_labels": list(ROW_LABELS), "arm_labels": list(ARM_LABELS)},
                "note": "standing rule 14: one registration, disjoint label sets, and a "
                        "swapped artefact refuses instead of resolving"})
        row = {"ARM": g["ARM"], "ROW": want_row, "IMG": g["IMG"], "DIGEST": g["DIGEST"],
               "rc": int(g["rc"]), "wall_s": int(g["wall_s"]), "ranks": int(g["ranks"]),
               "core_min": float(g["core_min"]), "cap_core_min": float(g["cap"]),
               "enforced_core_min": float(g["ecore"]), "memory": g["mem"],
               "inspect_exit": (None if (not parts or parts[0] == NOT_MEASURED) else parts[0]),
               "oomkilled": (parts[1] if len(parts) > 1 else None),
               "memavail_pre_GiB": _infra_float(g["mempre"]), "memavail_post_GiB": _infra_float(g["mempost"]),
               "cpuset": g["cpuset"], "delivered": g["delivered"], "siblings_pre": g["sibpre"],
               "siblings_post": g["sibpost"], "log": g["log"], "source": "ledger_row",
               "field_sources": {"all": "ledger_row"}, "infra_not_measured": infra_nm}
        if row["ARM"] in rows:
            refuse("ledger", {"duplicate_arm_row": row["ARM"],
                              "note": "two records for one run is the defect"})
        rows[row["ARM"]] = row
    return rows


def inspect_file_fallback(base, arm):
    """L-342: an arm with no ledger row is read from the launcher's surviving
    inspect record `<ARM>_<stamp>.inspect.txt`; every infrastructure field
    NOT_MEASURED, the source named per field."""
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
    if parts[0] == NOT_MEASURED:
        rc = None
    else:
        try:
            rc = int(parts[0])
        except ValueError:
            refuse("G1", {"inspect_record_exit_present_but_garbage": parts[0]})
    return {"ARM": arm, "ROW": row_of(arm), "IMG": None,
            "DIGEST": (parts[6] if len(parts) > 6 else None), "rc": rc, "wall_s": None,
            "ranks": ARM_RANKS[arm], "core_min": None, "cap_core_min": CAPS[arm],
            "enforced_core_min": CAPS[arm], "memory": parts[5] if len(parts) > 5 else None,
            "inspect_exit": (None if rc is None else parts[0]),
            "oomkilled": parts[1].lower(), "memavail_pre_GiB": None,
            "memavail_post_GiB": None, "cpuset": parts[4], "delivered": NOT_MEASURED,
            "siblings_pre": NOT_MEASURED, "siblings_post": NOT_MEASURED,
            "log": (os.path.basename(logs[-1]) if logs else None), "source": "inspect_record",
            "field_sources": {"rc": "inspect.txt .State.ExitCode",
                              "oomkilled": "inspect.txt .State.OOMKilled",
                              "cpuset": "inspect.txt HostConfig.CpusetCpus",
                              "DIGEST": "inspect.txt 7th field (launcher's GOT_DIGEST)"},
            "infra_not_measured": list(FIELDS_INFRASTRUCTURE) + ["core_min"]}


# ================= G1: COMPLETION, ARM-KIND AWARE, R-RC AWARE =========================
def read_write_compression(adir):
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
    """RESOLVE THE AGE-GUARD DATUM BY EXISTENCE, NEVER BY NAME (SO-1a delta (A))."""
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


def fatal_scan(files):
    """(B) C5, PER FILE AND PER LINE.

    `files` is an ordered list of (name, text).  Returns (hits, exclusions).  Each
    hit names the FILE, the LINE NUMBER, the TOKEN and the line itself, so a
    refusal says what was found and where.  Each exclusion is COUNTED AND NAMED on
    the record -- an exclusion nobody can see is a hole, not an exclusion."""
    hits, exclusions = [], []
    for name, text in files:
        for ln, line in enumerate(text.split("\n"), 1):
            excluded = None
            for pat, why in BENIGN_EXCLUSIONS:
                if pat.search(line):
                    excluded = {"file": name, "line": ln, "pattern": pat.pattern, "why": why,
                                "text": line.strip()[:160]}
                    break
            if excluded is not None:
                exclusions.append(excluded)
                continue
            for tok in FATAL_TOKENS:
                if line.find(tok) >= 0:
                    hits.append({"file": name, "line": ln, "token": tok,
                                 "text": line.strip()[:160]})
    return hits, exclusions


def g_completion(base, rows):
    """The five rule-4 clauses, PRINTED INDIVIDUALLY per arm (Sanaa 2026-08-27 s0):
        C1 rc value / C2 terminal marker / C3 artefact present / C4 age guard /
        C5 no fatal token, scanned PER FILE AND PER LINE."""
    out = {"arms": {}, "not_measured": {}, "rule4_clauses": {}, "datum_resolution": {},
           "rc_inferences": {}, "c5_exclusions": {}, "c5_exclusion_count": 0}
    for arm in ARM_LABELS:
        r = rows.get(arm)
        if r is None:
            r = inspect_file_fallback(base, arm)
            rows[arm] = r
        kind = ARM_KIND[arm]
        cl = {}

        adir, datum, dres = arm_datum(base, arm)
        out["datum_resolution"][arm] = dres

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

        logname = r.get("log")
        logpath = os.path.join(base, logname) if logname else None
        logtext = ""
        if logpath and os.path.isfile(logpath):
            logtext = open(logpath, errors="replace").read()
        r["log_text"] = logtext

        if kind == "SOLVER":
            if not logpath or not os.path.isfile(logpath):
                refuse("G1", {"C2_log_absent": logname, "arm": arm,
                              "note": "the terminal marker lives in the log; a missing log "
                                      "is a FAILED clause"})
            if TERMINAL[arm] not in logtext:
                refuse("G1", {"C2_terminal_marker_absent": TERMINAL[arm], "arm": arm,
                              "log": logname})
            cl["C2_terminal_marker"] = {"verdict": "PASS", "marker": TERMINAL[arm], "log": logname}
        else:
            mtext = open(art, errors="replace").read()
            if not re.search(r"^Mesh OK\.$", mtext, re.M):
                refuse("G1", {"C2_mesh_ok_absent": art, "arm": arm})
            cl["C2_terminal_marker"] = {"verdict": "PASS", "marker": "Mesh OK.",
                                        "log": ARTEFACT[arm]}

        # ---- C5, PER FILE AND PER LINE -------------------------------------------
        scan_files = [(logname or "<no log>", logtext)]
        if kind == "SCRIPT":
            scan_files.append((ARTEFACT[arm], open(art, errors="replace").read()))
        hits, exclusions = fatal_scan(scan_files)
        out["c5_exclusions"][arm] = exclusions
        out["c5_exclusion_count"] += len(exclusions)
        if hits:
            refuse("G1", {"C5_fatal_token_in_arm_output": hits, "arm": arm,
                          "files_scanned": [n for n, _ in scan_files],
                          "benign_exclusions_applied": exclusions,
                          "note": "a fatal token refuses at ANY rc; R-RC never launders a "
                                  "crash.  Scanned per file and per line, so the offending "
                                  "LINE is named."})
        cl["C5_no_fatal_token"] = {"verdict": "PASS", "tokens_searched": list(FATAL_TOKENS),
                                   "files_scanned": [n for n, _ in scan_files],
                                   "benign_exclusions_applied": exclusions,
                                   "benign_exclusion_count": len(exclusions),
                                   "scan_mode": "PER FILE AND PER LINE (never a whole-file "
                                                "substring test)"}

        oom = str(r.get("oomkilled")).lower()
        if oom not in ("false", "true"):
            refuse("G1", {"oomkilled_unparseable": arm, "value": r.get("oomkilled"),
                          "note": "OOMKilled is a PHYSICS field and is not covered by R-RC"})
        if oom != "false":
            refuse("G1", {"arm": arm, "oomkilled": oom,
                          "note": "G11 OOM HARD: an OOMKilled arm is a G1 refusal, never a "
                                  "re-fire (PREREGISTRATION.md section 5)"})

        ke = r.get("inspect_exit")
        kernel_rc = None
        if ke is not None:
            try:
                kernel_rc = int(ke)
            except (TypeError, ValueError):
                refuse("G1", {"rc_record_present_but_garbage": arm, "value": ke,
                              "note": "PRESENT-BUT-GARBAGE refuses; only ABSENT reads "
                                      "NOT MEASURED (L-342)"})
        if kernel_rc is None and r.get("rc") not in (None, 0):
            refuse("G1", {"rc_record_absent_but_harness_rc_nonzero": arm,
                          "harness_rc": r.get("rc"),
                          "note": "R-RC relaxes the rc RECORD, never a POSITIVE reading "
                                  "of failure"})
        if kernel_rc is None:
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
        out["arms"][arm] = {"kind": kind, "row": row_of(arm),
                            "rc_value": cl["C1_rc_value"]["verdict"],
                            "oomkilled": oom, "artefact": ARTEFACT[arm],
                            "source": r["source"], "field_sources": r["field_sources"]}
        if r.get("infra_not_measured"):
            out["not_measured"].setdefault(arm, []).extend(r["infra_not_measured"])
    return out


# ================= readers -- REGISTERED LOCATIONS ONLY ==============================
def read_X(path):
    """Every location is written out in the module docstring's REGISTERED READ
    LOCATIONS table.  No key is sought by recursive descent: a read that goes
    looking until it finds something will always find something."""
    j = json.load(open(path))
    adj = {}
    for of in OUTPUTS:
        if of not in (j.get("adjoint") or {}):
            refuse("SCHEMA", {"adjoint_block_absent_for_output": of,
                              "present": sorted((j.get("adjoint") or {}).keys()),
                              "file": path, "registered_outputs": list(OUTPUTS)})
        adj[of] = {}
        for dv in ("shape", "patchV"):
            if dv not in j["adjoint"][of]:
                refuse("SCHEMA", {"adjoint_dv_absent": [of, dv], "file": path})
            adj[of][dv] = [float(v) for v in j["adjoint"][of][dv]]
    base = {}
    for of in OUTPUTS:
        k = "%s_baseline" % of
        if k not in j:
            refuse("SCHEMA", {"baseline_key_absent": k, "file": path,
                              "present": sorted(j.keys())})
        base[of] = float(j[k])
        if not math.isfinite(base[of]):
            refuse("G-CMV" if of == GRADED_OUTPUT else "SCHEMA",
                   {"baseline_not_finite": {of: j[k]}, "file": path})
    return {"baseline": base, "adjoint": adj,
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"),
            "nprocs": j.get("nprocs"), "raw": j}


def read_F(path):
    j = json.load(open(path))
    if j.get("tb_steps") is not None and j.get("tb_steps") != TB_STEPS_REGISTERED:
        refuse("G-TB", {"tb_steps_not_registered": j.get("tb_steps"),
                        "registered": TB_STEPS_REGISTERED,
                        "note": "the trivial baseline is fixed at the freeze "
                                "(DAFOAM_CHARTER section 4)"})
    if j.get("components_requested") != COMPONENTS_REGISTERED:
        refuse("G5m", {"components_requested_not_registered": j.get("components_requested"),
                       "registered": COMPONENTS_REGISTERED})
    if j.get("control_outputs") is not None and list(j["control_outputs"]) != list(CONTROL_OUTPUTS):
        refuse("CONTROL", {"control_tuple_not_registered": j.get("control_outputs"),
                           "registered": list(CONTROL_OUTPUTS)})
    dkey = DKEY_OF_OUTPUT[GRADED_OUTPUT]
    table, ctrl = {}, None
    for row in j["rows"]:
        if row.get("dv") == "CTRL":
            ctrl = row
            continue
        key = (row["dv"], int(row["idx"]))
        fd, tb = {}, {}
        for block, dest in (("fd", fd), ("tb", tb)):
            for _, v in (row.get(block) or {}).items():
                ok = bool(v.get("ok"))
                if ok and dkey not in v:
                    refuse("SCHEMA", {"graded_d_key_absent_at_a_registered_location": dkey,
                                      "block": block, "dv": row["dv"], "idx": row["idx"],
                                      "keys_present": sorted(v.keys()), "file": path,
                                      "note": "the registered location is "
                                              "rows[k][%r][repr(step)][%r]" % (block, dkey)})
                dest[float(v["step"])] = {"ok": ok,
                                          "d": (float(v[dkey]) if ok else None)}
        table[key] = {"status": row.get("status"), "fd": fd, "tb": tb}
    if "%s_baseline" % GRADED_OUTPUT not in j:
        refuse("SCHEMA", {"baseline_key_absent": "%s_baseline" % GRADED_OUTPUT, "file": path})
    return {"table": table, "ctrl": ctrl,
            "baseline": float(j["%s_baseline" % GRADED_OUTPUT]),
            "eta": float(j["eta_used"]),
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"), "raw": j}


# ================= PLANTED CONTROLS -- BOTH DIRECTIONS ================================
def ctrl_control(F):
    """DIRECTION A, half one: the instrument's own CTRL tuple, re-read FROM DISK.

    The tuple must be the REGISTERED one and must be traversed IN FULL: an empty
    or short container would be 'seen' by a broken reader too, so it refuses."""
    c = F["ctrl"]
    if c is None:
        refuse("CONTROL", {"ctrl_row_absent": True})
    got = list(c.get("control_outputs") or ())
    if got != list(CONTROL_OUTPUTS):
        refuse("CONTROL", {"ctrl_tuple_not_registered": got, "registered": list(CONTROL_OUTPUTS),
                           "note": "a control that EMPTIES or SHORTENS the traversed tuple "
                                   "is REFUSED (PREREGISTRATION.md section 7A)"})
    step_key = repr(CTRL_STEP)
    zeros = [float(c["fd"][step_key][k]) for k in CONTROL_OUTPUTS]
    plants = [float(c["planted"][k]) for k in CONTROL_OUTPUTS]
    want = PLANT / (2.0 * CTRL_STEP)
    bad = None
    if len(zeros) != len(CONTROL_OUTPUTS) or len(plants) != len(CONTROL_OUTPUTS):
        bad = "tuple emptied or short"
    elif any(z != 0.0 for z in zeros):
        bad = "the unplanted control is not exactly zero"
    elif abs(plants[0] - want) > 1e-12 * abs(want):
        bad = "entry 0 does not carry the plant"
    elif any(p != 0.0 for p in plants[1:]):
        bad = "a COMPANION entry moved under the plant"
    if bad is not None:
        refuse("CONTROL", {"instrument_ctrl_not_seen": {
            "problem": bad, "tuple": list(CONTROL_OUTPUTS), "zeros": zeros,
            "planted": plants, "want_entry0": want}})
    return {"tuple": list(CONTROL_OUTPUTS), "zeros": zeros, "planted": plants,
            "want_entry0": want, "direction": "A -- the reader is shown able to see a NON-ZERO"}


def grader_plant_control(base, fpath, row_label):
    """DIRECTION A, half two: the GRADER writes its own planted copy of the G
    table, re-reads it through the SAME reader, and refuses unless every physical
    derivative moved by exactly PLANT."""
    j = json.load(open(fpath))
    dkey = DKEY_OF_OUTPUT[GRADED_OUTPUT]
    for row in j["rows"]:
        if row.get("dv") == "CTRL":
            continue
        for v in (row.get("fd") or {}).values():
            if v.get("ok"):
                v[dkey] = repr(float(v[dkey]) + PLANT)
    cdir = os.path.join(base, "grader_controls")
    os.makedirs(cdir, exist_ok=True)
    cp = os.path.join(cdir, "G_%s_planted.json" % row_label)
    json.dump(j, open(cp, "w"), indent=1, sort_keys=True)
    orig, back = read_F(fpath)["table"], read_F(cp)["table"]
    worst, n = 0.0, 0
    for key, row in orig.items():
        for s, v in row["fd"].items():
            if v["ok"]:
                worst = max(worst, abs((back[key]["fd"][s]["d"] - v["d"]) - PLANT))
                n += 1
    if n == 0 or worst > 1e-12:
        refuse("CONTROL", {"grader_plant_not_seen": {"n_values": n, "worst_residual": worst,
                                                     "plant": PLANT, "d_key": dkey}})
    return {"grader_plant_seen": True, "n_values": n, "worst_residual": worst, "file": cp,
            "d_key": dkey, "direction": "A -- the grader's own reader is shown able to see a plant"}


def flip_control_g5m(base, xpath, X, F, live, row_label):
    """DIRECTION B, half one (PREREGISTRATION.md section 7): a copy of the REAL X
    artefact with the RULE-SIZED plant applied to ONE d(CMZ)/d(shape) entry must
    read GATE FAIL.

    WHICH ENTRY: the GRADED `shape` pair with the SMALLEST |d_ref|, ties broken by
    the smaller index.  This selection is carried from SO-2M UNCHANGED so that the
    only registered delta is the plant's SIZE and SIGN.  Under SO-2M's absolute
    plant the choice mattered -- the smallest reference was where an absolute plant
    had its best chance.  Under SO-2MR's RULE the choice does not affect
    sufficiency at all, because the plant is sized to whichever reference is
    chosen.  That the selection has become irrelevant IS the repair.

    THE PLANT IS SUFFICIENT BY CONSTRUCTION AND THE CODE ASSERTS IT RATHER THAN
    HOPING: `P > need` is re-derived here from this row's own numbers and REFUSES
    if it does not hold.  With FLIP_PLANT_K = 2.0 the assertion is P = 2*need and
    can only fail if the registered K were moved below 1; THIS FILE'S OWN freeze-time
    selftest leg B3 (`_drive_k_red`, which moves K to 0.5 and requires the refusal to
    be PLANT_NOT_SUFFICIENT_BY_CONSTRUCTION BY NAME) drives it RED by doing exactly
    that.  There is no separate sufficiency script and this docstring does not name
    one: the leg travels in the same frozen bytes as the assertion it drives."""
    cands = [c for c in live["components"]
             if c.get("dv") == "shape" and c.get("verdict") in ("PASS", "GATE FAIL")
             and c.get("d_ref") is not None]
    if not cands or live["verdict"] == "NOT A RESULT":
        # A `NOT A RESULT` row LICENSES NOTHING, so there is no verdict here for a
        # control to license and no graded pair to plant into.  Recorded as NOT
        # DEMONSTRATED with its reason -- never as a control that passed, and never
        # as a refusal that would convert an exclusion finding into a second one.
        return {"direction": "B -- the GATE is shown to FLIP under a plant",
                "row": row_label, "demonstrated": False,
                "reason": ("the row is already NOT A RESULT and licenses no verdict"
                           if live["verdict"] == "NOT A RESULT"
                           else "no graded d(CMZ)/d(shape) pair survives to plant into"),
                "live_verdict": live["verdict"],
                "n_graded": live.get("n_graded"), "exclusions": live.get("exclusions_named")}
    target = min(cands, key=lambda c: (abs(c["d_ref"]), c["idx"]))
    j = json.load(open(xpath))
    idx = target["idx"]
    d_ref, j_live = target["d_ref"], float(target["J_adj"])
    mag, signed, need = flip_plant(d_ref, j_live)

    # THE SUFFICIENCY ASSERTION, RE-DERIVED FROM THIS ROW'S OWN NUMBERS AND
    # REFUSING IF IT DOES NOT HOLD.  A control whose plant cannot cross the band
    # is a control in name only, and shipping one is the defect SO-2M died of.
    if not mag > need:
        refuse("CONTROL", {"PLANT_NOT_SUFFICIENT_BY_CONSTRUCTION": {
            "row": row_label, "planted_component": [target["dv"], idx],
            "d_ref": d_ref, "band_D_pct": FD_BAND_PCT, "K": FLIP_PLANT_K,
            "plant_magnitude": mag, "plant_needed_to_cross_band_D": need,
            "rule": "P = K * (band_D/100) * |d_ref|, sign AWAY from d_ref"},
            "note": "PREREGISTRATION.md section 7 direction B registers the plant as a "
                    "RULE relative to the reference it must perturb.  A registered K "
                    "at or below 1 makes the plant unable to cross band D by "
                    "construction, and the control REFUSES rather than reporting a "
                    "PASS from a gate it has not shown able to GATE FAIL."})

    vals = list(j["adjoint"][GRADED_OUTPUT]["shape"])
    vals[idx] = repr(j_live + signed)
    j["adjoint"][GRADED_OUTPUT]["shape"] = vals
    cdir = os.path.join(base, "grader_controls")
    os.makedirs(cdir, exist_ok=True)
    cp = os.path.join(cdir, "X_%s_g5m_planted.json" % row_label)
    json.dump(j, open(cp, "w"), indent=1, sort_keys=True)
    Xp = read_X(cp)
    planted = grade_components(Xp, F)
    pc = [c for c in planted["components"]
          if c["dv"] == target["dv"] and c["idx"] == idx]
    rec = {"direction": "B -- the GATE is shown to FLIP under a RULE-SIZED plant",
           "row": row_label, "demonstrated": True, "file": cp,
           "planted_component": [target["dv"], idx],
           "d_ref": d_ref, "J_adj_live": j_live,
           "plant_rule": "P = K * (band_D/100) * |d_ref|, K = %g, sign AWAY from d_ref"
                         % FLIP_PLANT_K,
           "plant_K": FLIP_PLANT_K, "plant_magnitude": mag, "plant_signed": signed,
           "plant_needed_to_cross_band_D": need,
           "plant_is_sufficient": mag > need,
           "plant_margin_ratio": mag / need if need > 0 else None,
           "rel_err_pct_live": target.get("rel_err_pct"),
           "rel_err_pct_planted": (pc[0].get("rel_err_pct") if pc else None),
           "pair_verdict_live": target.get("verdict"),
           "pair_verdict_planted": (pc[0].get("verdict") if pc else None),
           "live_verdict": live["verdict"], "planted_verdict": planted["verdict"],
           "flipped": live["verdict"] != planted["verdict"]}
    # THE PAIR must go GATE FAIL -- that is the demonstration.  The ROW must then
    # read GATE FAIL too, because a row carrying a GATE FAIL pair cannot pass band
    # D.  On a row whose LIVE verdict is already GATE FAIL the row does not
    # "flip", and `flipped` records that honestly; the PAIR-level flip is the
    # evidence and it is asserted on every row either way.
    if not pc or pc[0].get("verdict") != "GATE FAIL" or planted["verdict"] != "GATE FAIL":
        refuse("CONTROL", {"G5m_did_NOT_flip_to_GATE_FAIL_under_the_planted_copy": rec,
                           "note": "PREREGISTRATION.md section 7 direction B REFUSES unless "
                                   "the planted PAIR and the planted ROW both read GATE "
                                   "FAIL on the copy.  The plant is sized by the registered "
                                   "RULE relative to this pair's own d_ref, so a miss here "
                                   "is a defect in the READER, not in the plant's size."})
    return rec


def flip_control_gnz(base, xpath, X, row_label):
    """DIRECTION B, half two: a copy of the REAL X artefact with
    d(CMZ)/d(patchV[1]) FORCED TO 0.0 must make G-NZ read GATE FAIL.

    This is the mirror of SO-2a's exact-zero gate: a BLIND READER FAILS G-NZ
    instead of passing it, and this control is what proves the gate can fail."""
    j = json.load(open(xpath))
    vals = list(j["adjoint"][GRADED_OUTPUT][NZ_DV])
    vals[NZ_IDX] = repr(0.0)
    j["adjoint"][GRADED_OUTPUT][NZ_DV] = vals
    cdir = os.path.join(base, "grader_controls")
    os.makedirs(cdir, exist_ok=True)
    cp = os.path.join(cdir, "X_%s_gnz_zeroed.json" % row_label)
    json.dump(j, open(cp, "w"), indent=1, sort_keys=True)
    Xz = read_X(cp)
    live_adj = X["adjoint"][GRADED_OUTPUT][NZ_DV][NZ_IDX]
    zero_adj = Xz["adjoint"][GRADED_OUTPUT][NZ_DV][NZ_IDX]
    verdict = "PASS" if abs(zero_adj) > NZ_ABS_MIN else "GATE FAIL"
    rec = {"direction": "B -- G-NZ is shown to FLIP when the aoa entry is forced to zero",
           "row": row_label, "file": cp, "entry": [NZ_DV, NZ_IDX],
           "live_adjoint": live_adj, "zeroed_adjoint": zero_adj,
           "threshold": NZ_ABS_MIN, "planted_verdict": verdict}
    if verdict != "GATE FAIL":
        refuse("CONTROL", {"G_NZ_did_NOT_flip_to_GATE_FAIL_when_the_aoa_entry_was_zeroed": rec})
    return rec


# ================= G5m: the bright line, per row, on CMZ ==============================
def grade_components(X, F):
    """G5m on d(CMZ)/d(shape, patchV), PER PAIR and PER AGGREGATE.

    THE PLATEAU IS PROVED PER PAIR, NOT ASSERTED ONCE FOR THE ITEM
    (DAFOAM_CHARTER.md section 2; PREREGISTRATION.md section 6).  EVERY EXCLUSION
    IS COUNTED AND NAMED.  Fewer than MIN_GRADED graded pairs, or more than
    MAX_EXCLUDED_PCT of candidates excluded, reads NOT A RESULT."""
    of = GRADED_OUTPUT
    comps, graded_fd, graded_adj, exclusions = [], [], [], []
    for dv, idx in COMPONENTS_REGISTERED:
        adj_vec = X["adjoint"][of][dv]
        j = adj_vec[idx] if idx < len(adj_vec) else None
        row = F["table"].get((dv, idx))
        c = {"dv": dv, "idx": idx, "J_adj": j}

        def exclude(reason, **extra):
            c.update({"verdict": "NOT A RESULT", "reason": reason, **extra})
            exclusions.append({"dv": dv, "idx": idx, "reason": reason})
            comps.append(c)

        if row is None or j is None:
            exclude("ABSENT")
            continue
        steps = sorted(STEPS_REGISTERED[dv], reverse=True)
        vals = [row["fd"].get(s) for s in steps]
        if any(v is None or not v["ok"] for v in vals):
            exclude("FD_STEP_FAILED_OR_ABSENT", steps_present=sorted(row["fd"]))
            continue
        d = [v["d"] for v in vals]
        ref = d[1]                                    # the MIDDLE of the registered three
        c.update({"steps": steps, "d_fd": d, "d_ref": ref})
        if abs(ref) < NEAR_ZERO_ABS:
            exclude("NEAR_ZERO")
            continue
        nb = [abs(d[0] - ref) / abs(ref) * 100.0, abs(d[2] - ref) / abs(ref) * 100.0]
        c["plateau_neighbour_pct"] = nb
        if min(nb) > PLATEAU_TOL_PCT:
            exclude("NO_PLATEAU")
            continue
        rel = abs(ref - j) / abs(ref) * 100.0
        flip = bool(ref * j < 0.0)
        c.update({"rel_err_pct": rel, "sign_flip": flip})
        c["verdict"] = "GATE FAIL" if (flip or rel > FD_BAND_PCT) else "PASS"
        graded_fd.append(ref)
        graded_adj.append(j)
        comps.append(c)
    n_cand = len(COMPONENTS_REGISTERED)
    n_graded = len(graded_fd)
    excluded_pct = len(exclusions) / float(n_cand) * 100.0
    out = {"objective": of, "components": comps, "n_candidates": n_cand,
           "n_graded": n_graded,
           "n_pass": sum(1 for c in comps if c.get("verdict") == "PASS"),
           "n_gate_fail": sum(1 for c in comps if c.get("verdict") == "GATE FAIL"),
           "n_not_a_result": sum(1 for c in comps if c.get("verdict") == "NOT A RESULT"),
           "sign_flips": sum(1 for c in comps if c.get("sign_flip")),
           "exclusions_named": exclusions, "n_excluded": len(exclusions),
           "excluded_pct": excluded_pct,
           "min_graded_required": MIN_GRADED, "max_excluded_pct": MAX_EXCLUDED_PCT}
    if n_graded < MIN_GRADED:
        out.update({"verdict": "NOT A RESULT", "aggregate_rel_err_pct": None,
                    "reason": "fewer than %d graded pairs" % MIN_GRADED})
        return out
    if excluded_pct > MAX_EXCLUDED_PCT:
        out.update({"verdict": "NOT A RESULT", "aggregate_rel_err_pct": None,
                    "reason": "more than %.0f %% of candidate pairs excluded "
                              "(a gate that grades a quarter of its own Jacobian is not "
                              "grading the Jacobian)" % MAX_EXCLUDED_PCT})
        return out
    num = math.sqrt(sum((a - b) ** 2 for a, b in zip(graded_fd, graded_adj)))
    den = math.sqrt(sum(a ** 2 for a in graded_fd))
    agg = num / den * 100.0
    out["aggregate_rel_err_pct"] = agg
    out["aggregate_is"] = ("the VECTOR-RELATIVE norm AS PRINTED; never compared against the "
                           "DAFoam papers' per-component average (DAFOAM_CHARTER.md section 2)")
    band_d_ok = out["n_gate_fail"] == 0
    band_e_ok = agg <= AGG_BAND_PCT
    out["band_D"] = "PASS" if band_d_ok else "GATE FAIL"
    out["band_E"] = "PASS" if band_e_ok else "GATE FAIL"
    out["verdict"] = "PASS" if (band_d_ok and band_e_ok) else "GATE FAIL"
    return out


def grade_cmv(X):
    """G-CMV: the moment functional's own VALUE gate, banded before it is read."""
    v = X["baseline"][GRADED_OUTPUT]
    if not math.isfinite(v):
        return {"value": v, "verdict": "NOT A RESULT",
                "reason": "CMZ non-finite (PREREGISTRATION.md section 5)"}
    return {"value": v, "sign": ("+" if v >= 0 else "-"), "abs": abs(v),
            "band_abs_max": CMZ_BASELINE_ABS_MAX,
            "verdict": "PASS" if abs(v) <= CMZ_BASELINE_ABS_MAX else "GATE FAIL",
            "why_this_band": "symmetric NACA0012 about the quarter chord: thin-airfoil "
                             "theory puts Cm_c/4 at zero and viscosity slightly off it; the "
                             "band is loose enough to survive viscosity and tight enough "
                             "that a mis-declared reference point, axis or scale cannot sit "
                             "inside it"}


def grade_nz(X, F):
    """G-NZ: the STRUCTURAL non-zero on d(CMZ)/d(aoa), on BOTH sides.

    A reader that returns zeros because it read the wrong key, the wrong slice or
    an empty tuple FAILS this gate rather than passing it."""
    adj_vec = X["adjoint"][GRADED_OUTPUT][NZ_DV]
    j = adj_vec[NZ_IDX] if NZ_IDX < len(adj_vec) else None
    row = F["table"].get((NZ_DV, NZ_IDX))
    steps = sorted(STEPS_REGISTERED[NZ_DV], reverse=True)
    fd_mid = None
    if row is not None:
        v = row["fd"].get(steps[1])
        if v is not None and v["ok"]:
            fd_mid = v["d"]
    adj_ok = j is not None and abs(j) > NZ_ABS_MIN
    fd_ok = fd_mid is not None and abs(fd_mid) > NZ_ABS_MIN
    return {"entry": [NZ_DV, NZ_IDX], "adjoint": j, "fd_middle_step": fd_mid,
            "threshold_abs_min": NZ_ABS_MIN, "adjoint_nonzero": adj_ok, "fd_nonzero": fd_ok,
            "verdict": "PASS" if (adj_ok and fd_ok) else "GATE FAIL",
            "why": "CMZ is a FLOW functional, so d(CMZ)/d(aoa) must be non-zero on BOTH "
                   "sides.  This is the MIRROR of SO-2a's exact-zero G-STRUCT: a BLIND "
                   "READER FAILS it rather than passing it."}


def grade_tb(X, F):
    """G-TB, the DAFOAM_CHARTER section 4 trivial baseline, on the GRADED functional."""
    of = GRADED_OUTPUT
    comps, n_pass = [], 0
    for dv, idx in COMPONENTS_REGISTERED:
        adj_vec = X["adjoint"][of][dv]
        j = adj_vec[idx] if idx < len(adj_vec) else None
        row = F["table"].get((dv, idx))
        c = {"dv": dv, "idx": idx, "J_adj": j}
        if row is None or j is None:
            c.update({"tb_verdict": "GATE FAIL", "reason": "ABSENT"}); comps.append(c); continue
        s = TB_STEPS_REGISTERED[dv][0]
        v = (row.get("tb") or {}).get(s)
        if v is None or not v["ok"] or v["d"] is None:
            c.update({"tb_step": s, "tb_verdict": "GATE FAIL",
                      "reason": "TB_PROBE_FAILED_OR_ABSENT"}); comps.append(c); continue
        d = v["d"]
        if abs(d) < NEAR_ZERO_ABS:
            c.update({"tb_step": s, "d_tb": d, "tb_verdict": "GATE FAIL",
                      "reason": "NEAR_ZERO"}); comps.append(c); continue
        rel = abs(d - j) / abs(d) * 100.0
        flip = bool(d * j < 0.0)
        inside = (not flip) and rel <= FD_BAND_PCT
        c.update({"tb_step": s, "d_tb": d, "rel_err_pct": rel, "sign_flip": flip,
                  "tb_verdict": "PASS" if inside else "GATE FAIL"})
        if inside:
            n_pass += 1
        comps.append(c)
    verdict = "PASS" if n_pass <= TB_MAX_PASSING else "GATE FAIL"
    return {"objective": of, "components": comps,
            "n_passing_band_D_at_the_WRONG_step": n_pass, "max_allowed": TB_MAX_PASSING,
            "verdict": verdict,
            "consequence": ("the trivial baseline FAILS as registered, so the FD gate is "
                            "measuring the step" if verdict == "PASS" else
                            "the WRONG step also passes: the gate is not measuring what it "
                            "claims and the G5m verdict for this row is WITHDRAWN to "
                            "NOT A RESULT (DAFOAM_CHARTER.md section 4)")}


def compose_row(g5m, g_tb):
    """THE REGISTERED COMPOSITION (PREREGISTRATION.md section 5).

    G-TB IS COMPOSED ONLY ONTO A ROW WHOSE G5m IS ALREADY `PASS`.  A row that
    already GATE FAILs needs no trivial baseline to doubt it, and composing one
    there would convert a REAL GRADIENT DEFECT -- the registered prediction for
    the SHIPPED row, and the most valuable output this rung can produce -- into
    NOT A RESULT and hide the finding.  G-TB's own verdict is printed on every
    row either way.  This restriction was paid for by SO-2a section 7.4."""
    if g5m["verdict"] == "PASS" and g_tb["verdict"] == "GATE FAIL":
        return "NOT A RESULT"
    return g5m["verdict"]


# ================= G9 / G10 / G11 / G12 ================================================
def g_toolchain(rows):
    out = {"per_arm": {}, "verdict": "PASS"}
    for arm in ARM_LABELS:
        r = rows[arm]
        rl = row_of(arm)
        m = re.search(r"D4S_IDWARP_SO_MD5:\s*([0-9a-f]{32})", r.get("log_text", ""))
        printed = m.group(1) if m else None
        ok = (r.get("DIGEST") == IMG_DIGEST[rl]) and (printed == SO_MD5[rl])
        art_md5 = r.get("artefact_so_md5")
        if arm != "MESH":
            ok = ok and (art_md5 == SO_MD5[rl])
        out["per_arm"][arm] = {"row": rl, "digest": r.get("DIGEST"), "printed_so_md5": printed,
                               "artefact_so_md5": art_md5, "ok": bool(ok)}
        if not ok:
            out["verdict"] = "GATE FAIL"
    out["identity_is"] = "an image DIGEST and a library HASH, never a version string"
    return out


def g_caps(rows):
    out = {"per_arm": {}, "verdict": "PASS", "total_core_min": 0.0,
           "ceiling": ITEM_CEILING_CORE_MIN, "not_measured": []}
    for arm in ARM_LABELS:
        r = rows[arm]
        cm = r.get("core_min")
        if cm is None:
            out["not_measured"].append(arm)
            out["per_arm"][arm] = {"core_min": NOT_MEASURED, "cap": CAPS[arm]}
            continue
        out["total_core_min"] += cm
        crossed = cm > CAPS[arm]
        out["per_arm"][arm] = {"core_min": cm, "cap": CAPS[arm], "crossed": crossed,
                               "predicted_core_min": PREDICTED_CORE_MIN[arm],
                               "ratio_actual_over_predicted": round(cm / PREDICTED_CORE_MIN[arm], 4)}
        if crossed:
            out["verdict"] = "GATE FAIL"
    if out["total_core_min"] > ITEM_CEILING_CORE_MIN:
        out["verdict"] = "GATE FAIL"
    out["cost_basis"] = ("core-minutes MEASURED from the ledger; dollars are DERIVED at "
                         "$0.0513/core-h (c7a.4xlarge, REPORTED-BY-OWNER) and are NOT "
                         "MEASURED -- the box cannot read its own billing "
                         "(COMPUTE_BUDGET_CHARTER.md section 5)")
    out["dollars_derived_not_measured"] = round(out["total_core_min"] / 60.0 * 0.0513, 6)
    return out


def mem_bytes(v):
    """Normalise a memory cap to BYTES.

    The LEDGER row carries docker's own `4g` string; the surviving inspect record
    carries `.HostConfig.Memory`, which is the SAME cap in BYTES (4294967296).
    Comparing the two as strings makes an arm read GATE FAIL for a difference of
    NOTATION -- exactly the class of defect that killed AV-1 and AV-2 on `0/U`
    versus `0/U.gz`.  So both sides are normalised and compared as numbers, and an
    unparseable value reads None (NOT_MEASURED) rather than a failing gate."""
    if v is None:
        return None
    t = str(v).strip().lower()
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([kmgt]?)b?", t)
    if not m:
        return None
    mult = {"": 1, "k": 1024, "m": 1024 ** 2, "g": 1024 ** 3, "t": 1024 ** 4}[m.group(2)]
    return int(float(m.group(1)) * mult)


def g_memory(rows):
    """G11 -- OOM HARD.  The memory cap is registered at 4g on every arm and an
    OOMKilled arm is a G1 refusal, never a re-fire.  Here the CAP ITSELF is read
    back from the ledger row and checked, so a launcher that ran at a different
    cap is caught rather than assumed."""
    out = {"per_arm": {}, "verdict": "PASS", "not_measured": []}
    for arm in ARM_LABELS:
        mem = rows[arm].get("memory")
        got = mem_bytes(mem)
        want = mem_bytes(MEMORY_REGISTERED)
        if got is None:
            out["not_measured"].append(arm)
            out["per_arm"][arm] = {"memory": NOT_MEASURED, "memory_raw": mem,
                                   "registered": MEMORY_REGISTERED}
            continue
        ok = got == want
        out["per_arm"][arm] = {"memory": mem, "memory_bytes": got,
                               "registered": MEMORY_REGISTERED, "registered_bytes": want,
                               "ok": ok}
        if not ok:
            out["verdict"] = "GATE FAIL"
    return out


def g_placement(rows):
    out = {"per_arm": {}, "verdict": "PASS", "not_measured": []}
    for arm in ARM_LABELS:
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
        out["per_arm"][arm] = {"cpuset": r.get("cpuset"),
                               "delivered_cores_mean": (dl if dl is not None else NOT_MEASURED)}
        if not (cs_ok and dl_ok):
            out["verdict"] = "GATE FAIL"
    out["note"] = ("at np = 1 the delivered-cores floor does not apply and is REPORTED as a "
                   "number, NOT_MEASURED where absent (PREREGISTRATION.md section 5 G12)")
    return out


# ================= the grade ==========================================================
def grade(root):
    here = os.path.dirname(os.path.abspath(__file__))
    self_path = os.path.abspath(__file__)
    # (A) and (B): the two source audits run BEFORE any verdict and REFUSE, so a
    # comparator carrying an unrepaired call site cannot produce a number at all.
    audit = audit_row_label_sites(self_path)
    if audit["verdict"] != "OK":
        refuse("RULE14", {"row_label_audit": audit,
                          "note": "standing rule 14: a lesson is not applied until EVERY call "
                                  "site asserts it.  SO-1c's amendment R8 repaired one of "
                                  "three."})
    wfs = whole_file_substring_scans(self_path)
    if wfs:
        refuse("C5", {"whole_file_substring_scan_present": wfs,
                      "note": "the shape at so1a_grade.py:122-125 is forbidden here "
                              "(PREREGISTRATION.md section 5 G1 C5)"})

    rows = read_ledger(os.path.join(root, "ledger.txt"))
    g1 = g_completion(root, rows)

    cm_txt = open(os.path.join(root, "MESH", "checkMesh.log"), errors="replace").read()
    m = re.search(r"^\s*cells:\s+(\d+)", cm_txt, re.M)
    if not m:
        refuse("G-M2", {"cells_absent_in_checkMesh": True})
    cells = int(m.group(1))
    gm2 = "PASS" if cells == CELLS_EXPECTED else "GATE FAIL"

    # ---- per ROW, via the ONE registered arm table ---------------------------------
    X, F, xpath, fpath = {}, {}, {}, {}
    for rl in ROW_LABELS:
        xarm, garm = ARMS_OF_ROW[rl]
        xpath[rl] = os.path.join(root, xarm, ARTEFACT[xarm])
        fpath[rl] = os.path.join(root, garm, ARTEFACT[garm])
        X[rl] = read_X(xpath[rl])
        F[rl] = read_F(fpath[rl])
        rows[xarm]["artefact_so_md5"] = X[rl]["so_md5"]
        rows[garm]["artefact_so_md5"] = F[rl]["so_md5"]

    controls = {"instrument_ctrl": {}, "grader_plant": {},
                "flip_G5m": {}, "flip_G_NZ": {}}
    gates_row = {}
    for rl in ROW_LABELS:
        controls["instrument_ctrl"][rl] = ctrl_control(F[rl])
        controls["grader_plant"][rl] = grader_plant_control(root, fpath[rl], rl)
        g5m = grade_components(X[rl], F[rl])
        gcmv = grade_cmv(X[rl])
        gnz = grade_nz(X[rl], F[rl])
        gtb = grade_tb(X[rl], F[rl])
        # DIRECTION B runs in the SAME INVOCATION as the verdict it licenses.
        controls["flip_G5m"][rl] = flip_control_g5m(root, xpath[rl], X[rl], F[rl], g5m, rl)
        controls["flip_G_NZ"][rl] = flip_control_gnz(root, xpath[rl], X[rl], rl)
        gates_row[rl] = {"G5m": g5m, "G_CMV": gcmv, "G_NZ": gnz,
                         "G_TB_trivial_baseline": gtb,
                         "row_verdict": compose_row(g5m, gtb),
                         "CMZ_baseline": X[rl]["baseline"][GRADED_OUTPUT],
                         "CD_baseline": X[rl]["baseline"]["CD"],
                         "CL_baseline": X[rl]["baseline"]["CL"],
                         "eta_G": F[rl]["eta"]}

    # ---- divergence shipped vs patched on d(CMZ)/dx: REPORTED, NEVER GATED ---------
    div = []
    for dv, idx in COMPONENTS_REGISTERED:
        a = X["SHIPPED"]["adjoint"][GRADED_OUTPUT][dv]
        b = X["PATCHED"]["adjoint"][GRADED_OUTPUT][dv]
        if idx < len(a) and idx < len(b):
            den = max(abs(a[idx]), abs(b[idx]), 1e-300)
            div.append({"dv": dv, "idx": idx, "J_shipped": a[idx], "J_patched": b[idx],
                        "divergence_pct": abs(a[idx] - b[idx]) / den * 100.0})

    g9, g10, g11, g12 = g_toolchain(rows), g_caps(rows), g_memory(rows), g_placement(rows)

    # ---- registered falsifiers, SCORED never adjusted ------------------------------
    preds = {}
    cmz_s = gates_row["SHIPPED"]["CMZ_baseline"]
    preds["P1_CMZ_evaluates_and_is_finite_on_both_rows"] = (
        "HIT" if all(math.isfinite(gates_row[rl]["CMZ_baseline"]) for rl in ROW_LABELS) else "MISS")
    preds["P2_CMZ_baseline_inside_the_registered_band"] = (
        "HIT" if all(gates_row[rl]["G_CMV"]["verdict"] == "PASS" for rl in ROW_LABELS) else "MISS")
    dcmz_daoa = abs(X["PATCHED"]["adjoint"][GRADED_OUTPUT][NZ_DV][NZ_IDX])
    dcl_daoa = abs(X["PATCHED"]["adjoint"]["CL"][NZ_DV][NZ_IDX])
    preds["P3_dCMZ_daoa_nonzero_and_smaller_than_dCL_daoa"] = (
        "HIT" if (gates_row["PATCHED"]["G_NZ"]["verdict"] == "PASS" and dcmz_daoa < dcl_daoa)
        else "MISS")
    preds["P3_numbers"] = {"abs_dCMZ_daoa_PATCHED": dcmz_daoa, "abs_dCL_daoa_PATCHED": dcl_daoa}
    preds["P4_PATCHED_row_G5m_PASSES"] = (
        "NOT_MEASURED" if gates_row["PATCHED"]["G5m"]["verdict"] == "NOT A RESULT" else
        ("HIT" if gates_row["PATCHED"]["G5m"]["verdict"] == "PASS" else "MISS"))
    preds["P5_SHIPPED_row_G5m_GATE_FAILS"] = (
        "NOT_MEASURED" if gates_row["SHIPPED"]["G5m"]["verdict"] == "NOT A RESULT" else
        ("HIT" if gates_row["SHIPPED"]["G5m"]["verdict"] == "GATE FAIL" else "MISS"))
    tb_fail = {rl: len(COMPONENTS_REGISTERED)
                   - gates_row[rl]["G_TB_trivial_baseline"]["n_passing_band_D_at_the_WRONG_step"]
               for rl in ROW_LABELS}
    preds["P6_trivial_baseline_fails_at_least_4_of_5_on_each_row"] = (
        "HIT" if all(tb_fail[rl] >= PRED["P6_tb_min_failing"] for rl in ROW_LABELS) else "MISS")
    preds["P6_numbers"] = tb_fail

    # ---- ITEM VERDICT, the composition registered at PREREGISTRATION.md section 5 ---
    row_verdicts = {rl: gates_row[rl]["row_verdict"] for rl in ROW_LABELS}
    other_gates = [gm2, g9["verdict"], g10["verdict"], g11["verdict"], g12["verdict"]]
    for rl in ROW_LABELS:
        other_gates.extend([gates_row[rl]["G_CMV"]["verdict"], gates_row[rl]["G_NZ"]["verdict"]])
    if "NOT A RESULT" in list(row_verdicts.values()) + other_gates:
        verdict = "NOT A RESULT"
    elif "GATE FAIL" in list(row_verdicts.values()) + other_gates:
        verdict = "GATE FAIL"
    else:
        verdict = "PASS"
    if verdict not in VOCAB:
        refuse("VOCAB", {"verdict": verdict})

    return {"item": "CURRICULUM-%s" % ITEM, "verdict": verdict, "rows": row_verdicts,
            "gates": {"G1_completion": "PASS", "G-M2_mesh_identity": gm2,
                      "per_row": gates_row,
                      "G6_dot_product_duality_and_complex_step": G6_SENTENCE,
                      "G9_toolchain": g9, "G10_caps": g10, "G11_memory": g11,
                      "G12_placement": g12},
            "mesh_cells": cells,
            "divergence_shipped_vs_patched_dCMZ": div,
            "divergence_note": "REPORTED with its number and NEVER GATED "
                               "(PREREGISTRATION.md section 5)",
            "predictions": preds, "controls": controls,
            "rule14_row_label_audit": audit,
            "c5_whole_file_substring_scans": wfs,
            "c5_benign_exclusions": g1["c5_exclusions"],
            "c5_benign_exclusion_count": g1["c5_exclusion_count"],
            "completion": g1,
            "not_measured": {"G1": g1["not_measured"], "G10": g10["not_measured"],
                             "G11": g11["not_measured"], "G12": g12["not_measured"]},
            "field_classes": {"physics": list(FIELDS_PHYSICS),
                              "infrastructure": list(FIELDS_INFRASTRUCTURE),
                              "rule": "absent infrastructure -> NOT_MEASURED beside the "
                                      "verdict; absent physics -> REFUSE (L-342).  The "
                                      "GRADER'S OWN rc is INFRASTRUCTURE and is never the "
                                      "verdict."},
            "no_gci": NO_GCI_SENTENCE,
            "age_datum_resolution": g1["datum_resolution"],
            "rule4_clauses_per_arm": g1["rule4_clauses"],
            "rc_inferences": g1["rc_inferences"],
            "capability_grid_cell": "2D . steady . incompressible -- gradients computed + "
                                    "FD-verified; this item moves ONLY that column and adds "
                                    "the MOMENT functional CMZ, which no A1 record had "
                                    "FD-verified before it",
            "instrument_cross_check": instrument_constants(os.path.join(here, "so2mr_xm.py"))
                                      if os.path.isfile(os.path.join(here, "so2mr_xm.py")) else None}


# =====================================================================================
# SELFTEST.  The POSITIVE path is built FROM A REAL PRODUCER ARTEFACT; the REFUSAL
# branches keep synthetic fixtures.
#
# WHY THAT SPLIT.  A 51-leg suite in this family was blind to a schema break
# because its positive fixture was hand-authored from what its READER expected: it
# proved the gate reads the shape the fixture writes and the fixture writes the
# shape the gate reads, and nothing else.  So the positive fixture here is SO-1a's
# REAL on-disk so1a_X.json / so1a_F.json -- written by a real instrument inside a
# real container on this box -- with the CMZ keys ADDED at the registered
# locations, and the key vocabulary CROSS-CHECKED against so2mr_xm.py's OWN bytes.
# Refusal branches stay synthetic because a refusal fixture must be able to carry
# a defect a real artefact never carries.
# =====================================================================================
REAL_PARENT_X = ("/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient"
                 "/X-S/so1a_X.json")
REAL_PARENT_F = ("/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient"
                 "/F-S/so1a_F.json")
# The fixture's CMZ derivatives are the REAL CL derivatives scaled by this factor.
# It is a FIXTURE CONSTANT, not a physical claim: the fixture exists to exercise
# the reader's traversal of the REAL SCHEMA, and every key, nesting level and
# repr() convention it carries came off disk rather than out of this file.
#
# TWO SCALES, AND WHY BOTH ARE KEPT AFTER THE PLANT RULE REPLACED THE ABSOLUTE.
# SO-2M kept two scales because its ABSOLUTE plant could fire at one and not the
# other: its leg B1 DROVE the CL-class scale and MEASURED its own frozen control
# refusing, at zero core-min, before the chain ever ran -- and the freeze correctly
# forbade repairing the number, so the finding was recorded and the item went to
# compute knowing this could happen.  It did happen, on the real d_ref, at
# 6.25 core-min.
#
# SO-2MR keeps BOTH SCALES FOR THE OPPOSITE REASON: they are now the portability
# test of the RULE.  The two scales differ by a factor of 50 and span the two
# measured classes on this exact case -- SO-1a's real |d(CL)/d(shape)| runs
# 0.462 .. 3.157 over the four registered shape components (X-S/so1a_X.json) and
# |d(CD)/d(shape)| runs 0.0035 .. 0.0124.  A plant sized by the RULE must flip the
# gate at BOTH, and legs B1/B1b assert exactly that.  An absolute plant cannot: the
# whole defect is that 1.234e-03 is 33.76 % of the CD-scale reference and 2.4798 %
# of the CMZ one.
#   * FIXTURE_CMZ_PHYSICAL is the CL-class scale, where SO-2M's absolute plant was
#     MEASURED unable to cross band D.  Leg B1 drives it and the RULE-SIZED plant
#     flips the gate there.
#   * FIXTURE_CMZ_FROM_CL is the small scale SO-2M needed to exercise the machinery
#     at all.  It is named as a chosen scale, never as a physical claim.
FIXTURE_CMZ_FROM_CL = 0.005
FIXTURE_CMZ_PHYSICAL = 0.25
# SO-2M's OWN RECORDED NUMBERS, quoted from
# /home/ubuntu/certonomous-runs/CURRICULUM-SO2M-a1-naca0012-moment-gradient/
# SO2M_grade_20260831T195531Z.json.  They are the KNOWN POSITIVE for the
# sufficiency legs: a rule that cannot reproduce SO-2M's refusal from SO-2M's own
# d_ref has not been shown able to see the defect it exists to prevent.
SO2M_RECORDED_D_REF = -0.04976246220706002
SO2M_RECORDED_PLANT = 0.001234
SO2M_RECORDED_NEED = 0.002488123110353001
ROWFMT = ("ARM={arm} ROW={row} IMG={img} DIGEST={dig} rc={rc} wall_s={wall} ranks={ranks} "
          "core_min={cm} cap_core_min={cap} enforced_wall_s=600 enforced_core_min={cap} "
          "memory={mem} inspect(exit,oomkilled)=[{ke} {oom}] memavail_pre_GiB=20.00 "
          "memavail_post_GiB={mpost} cpuset={cs} delivered_cores_mean=[{dl}] "
          "siblings_pre=[] siblings_post=[] log={log} stamp=x\n")


def _augment_real_X(j, adj_err_pct=None, flip=(), nz_zero=False, cmz_base=None,
                    cmz_scale=None):
    """Add the SO-2MR keys to a REAL SO-1a X artefact, at the REGISTERED locations."""
    j = json.loads(json.dumps(j))
    sc = FIXTURE_CMZ_FROM_CL if cmz_scale is None else cmz_scale
    cl_shape = [float(v) for v in j["adjoint"]["CL"]["shape"]]
    cl_pv = [float(v) for v in j["adjoint"]["CL"]["patchV"]]
    cmz_shape = [v * sc for v in cl_shape]
    cmz_pv = [v * sc for v in cl_pv]
    if nz_zero:
        cmz_pv[NZ_IDX] = 0.0
    j["adjoint"]["CMZ"] = {"shape": [repr(v) for v in cmz_shape],
                           "patchV": [repr(v) for v in cmz_pv]}
    j["CMZ_baseline"] = repr(-0.0031 if cmz_base is None else cmz_base)
    j["outputs"] = list(OUTPUTS)
    j["graded_output"] = GRADED_OUTPUT
    j["item"] = ITEM
    return j


def _augment_real_F(j, xj, err_pct=0.5, err_by_comp=None, flip=(), noplateau=(),
                    tb_pass=(), ctrl_ok=True, ctrl_tuple=None, drop_dkey=False,
                    fd_fail=(), cmz_base=None, tb_steps=None):
    """Add the SO-2MR keys to a REAL SO-1a F artefact, at the REGISTERED locations.

    The FD table is made consistent with the X artefact's CMZ adjoint so the clean
    fixture reads PASS: every d(CMZ) entry is the adjoint value nudged by
    `err_pct`.  The SCHEMA -- rows list, per-step dicts keyed by repr(step), the
    tb block, the identity block, the repr() string convention -- is the REAL
    artefact's and is not re-created here."""
    j = json.loads(json.dumps(j))
    err_by_comp = err_by_comp or {}
    adj = {dv: [float(v) for v in xj["adjoint"]["CMZ"][dv]] for dv in ("shape", "patchV")}
    for row in j["rows"]:
        dv = row.get("dv")
        if dv == "CTRL":
            step_key = repr(CTRL_STEP)
            tup = list(CONTROL_OUTPUTS if ctrl_tuple is None else ctrl_tuple)
            row["control_outputs"] = tup
            for k in tup:
                row["fd"][step_key][k] = repr(0.0)
            planted = {"step": CTRL_STEP, "plant": PLANT, "ok": True,
                       "moved_entry": tup[0] if tup else None, "control_outputs": tup}
            for i, k in enumerate(tup):
                planted[k] = repr((PLANT / (2.0 * CTRL_STEP) if ctrl_ok else 0.0)
                                  if i == 0 else 0.0)
            row["planted"] = planted
            continue
        idx = int(row["idx"])
        j_adj = adj[dv][idx]
        e = err_by_comp.get((dv, idx), err_pct)
        dref = j_adj * (1.0 + e / 100.0)
        if (dv, idx) in flip:
            dref = -dref
        mid = sorted(STEPS_REGISTERED[dv])[1]
        for skey, v in (row.get("fd") or {}).items():
            s = float(v["step"])
            if (dv, idx) in fd_fail:
                v["ok"] = False
                v.pop(DKEY_OF_OUTPUT[GRADED_OUTPUT], None)
                continue
            if (dv, idx) in noplateau:
                scale = 1.0 if abs(s - mid) < 1e-30 else 1.5
            else:
                scale = 1.0 if abs(s - mid) < 1e-30 else 1.01
            v[DKEY_OF_OUTPUT[GRADED_OUTPUT] if not drop_dkey else "dCmz"] = repr(dref * scale)
            v["CMZ_plus"] = repr(0.0)
            v["CMZ_minus"] = repr(0.0)
        tbs = TB_STEPS_REGISTERED[dv][0]
        tbmul = 1.001 if (dv, idx) in tb_pass else 3.0
        # RULING 1.  The REAL parent artefact's tb block is keyed at SO-1a's OWN
        # trivial-baseline step -- patchV 1e-6, read off disk.  THIS item registers
        # h = 1e-8 on all five components, so the fixture is RE-KEYED AT THE
        # REGISTERED LOCATION: the outer repr(step) key AND the inner "step" field,
        # which is the one read_F actually parses (float(v["step"])).  The registered
        # step is not bent to the parent's; the parent's block is moved to it.
        tb_new = {}
        for _skey, v in (row.get("tb") or {}).items():
            v = dict(v)
            v["step"] = tbs
            v[DKEY_OF_OUTPUT[GRADED_OUTPUT] if not drop_dkey else "dCmz"] = repr(j_adj * tbmul)
            v["CMZ_plus"] = repr(0.0)
            v["CMZ_minus"] = repr(0.0)
            tb_new[repr(tbs)] = v
        row["tb"] = tb_new
    j["CMZ_baseline"] = repr(-0.0031 if cmz_base is None else cmz_base)
    j["CMZ_baseline_repeat"] = j["CMZ_baseline"]
    # RULING 1: the parent artefact declares SO-1a's tb_steps; this item's producer
    # declares THIS item's.  Set at the registered location.  Leg TB0 below drives
    # read_F REFUSING when this field carries the OLD 1e-6, so this assignment is
    # not a way of walking past the check -- it is the check's positive control.
    if tb_steps is None:
        j["tb_steps"] = {dv: list(v) for dv, v in TB_STEPS_REGISTERED.items()}
    else:
        j["tb_steps"] = tb_steps
    j["outputs"] = list(OUTPUTS)
    j["graded_output"] = GRADED_OUTPUT
    j["d_key_of_output"] = dict(DKEY_OF_OUTPUT)
    j["control_outputs"] = list(CONTROL_OUTPUTS if ctrl_tuple is None else ctrl_tuple)
    j["item"] = ITEM
    return j


def _real_fixture(tmp, tweak=None):
    """Build a run root whose X and G artefacts are the REAL SO-1a artefacts,
    augmented at the registered locations.  `tweak` mutates the knob dict."""
    if not (os.path.isfile(REAL_PARENT_X) and os.path.isfile(REAL_PARENT_F)):
        return None
    k = {"rc": {a: 0 for a in ARM_LABELS}, "ke": {},
         "oom": {a: "false" for a in ARM_LABELS},
         "cm": dict(PREDICTED_CORE_MIN), "cs": {a: CPUSET_REGISTERED for a in ARM_LABELS},
         "mem": {a: MEMORY_REGISTERED for a in ARM_LABELS},
         "so": {a: SO_MD5[row_of(a)] for a in ARM_LABELS}, "cells": CELLS_EXPECTED,
         "err": {rl: {} for rl in ROW_LABELS}, "err_pct": {rl: 0.5 for rl in ROW_LABELS},
         "flip": {rl: () for rl in ROW_LABELS}, "noplateau": {rl: () for rl in ROW_LABELS},
         "fd_fail": {rl: () for rl in ROW_LABELS}, "tb_pass": {rl: () for rl in ROW_LABELS},
         "tb_steps": {rl: None for rl in ROW_LABELS},
         "nz_zero": {rl: False for rl in ROW_LABELS}, "cmz_base": {rl: -0.0031 for rl in ROW_LABELS},
         "cmz_scale": {rl: FIXTURE_CMZ_FROM_CL for rl in ROW_LABELS},
         "ctrl_ok": {rl: True for rl in ROW_LABELS}, "ctrl_tuple": {rl: None for rl in ROW_LABELS},
         "drop_dkey": {rl: False for rl in ROW_LABELS},
         "terminal": {a: True for a in ARM_LABELS}, "stale": set(), "mpost": "20.00",
         "drop_row": set(), "inspect_file": set(), "rc_record": set(), "fatal": {},
         "ledger_row_label": {}, "datum": {a: ("plain" if a == "MESH" else "gz") for a in ARM_LABELS},
         "write_compression": "on", "dl": "1.99 n=10 max_nr_throttled=0"}
    if tweak:
        tweak(k)
    rawX = json.load(open(REAL_PARENT_X))
    rawF = json.load(open(REAL_PARENT_F))
    root = os.path.join(tmp, "real_%d" % int(time.time() * 1e6))
    os.makedirs(root)
    led = ["ITEM=%s\n" % ITEM, "STAGED stamp=x\n"]
    for arm in ARM_LABELS:
        rl = row_of(arm)
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
        so = k["so"][arm]
        text = ("D4S_CONTAINER_UID: 0\nD4S_IDWARP_SO_MD5: %s\n"
                "D4S_DEADLINE_IN_CONTAINER_S: 600\ntrapFpe: Floating point exception "
                "trapping enabled (FOAM_SIGFPE).\n" % so)
        art = os.path.join(d, ARTEFACT[arm])
        if arm == "MESH":
            open(art, "w").write("Mesh stats\n    cells:            %d\n\nMesh OK.\n" % k["cells"])
            text += "SO2MR_CHECKMESH_RC 0\n"
        else:
            ident = dict(rawX.get("identity") or {})
            ident["libidwarp_so_md5"] = so
            ident["write_compression"] = k["write_compression"]
            if arm.startswith("X"):
                jx = _augment_real_X(rawX, nz_zero=k["nz_zero"][rl], cmz_base=k["cmz_base"][rl],
                                     cmz_scale=k["cmz_scale"][rl])
                jx["identity"] = ident
                json.dump(jx, open(art, "w"), indent=1, sort_keys=True)
            else:
                jx = _augment_real_X(rawX, nz_zero=k["nz_zero"][rl], cmz_base=k["cmz_base"][rl],
                                     cmz_scale=k["cmz_scale"][rl])
                jf = _augment_real_F(rawF, jx, err_pct=k["err_pct"][rl],
                                     err_by_comp=k["err"][rl], flip=k["flip"][rl],
                                     noplateau=k["noplateau"][rl], tb_pass=k["tb_pass"][rl],
                                     ctrl_ok=k["ctrl_ok"][rl], ctrl_tuple=k["ctrl_tuple"][rl],
                                     drop_dkey=k["drop_dkey"][rl], fd_fail=k["fd_fail"][rl],
                                     cmz_base=k["cmz_base"][rl], tb_steps=k["tb_steps"][rl])
                jf["identity"] = ident
                json.dump(jf, open(art, "w"), indent=1, sort_keys=True)
            if k["terminal"][arm]:
                text += TERMINAL[arm] + " ok\n"
        if arm in k["fatal"]:
            text += k["fatal"][arm] + "\n"
        os.utime(art, (t0 - 5, t0 - 5) if arm in k["stale"] else (t0 + 5, t0 + 5))
        open(os.path.join(root, log), "w").write(text)
        ke = NOT_MEASURED if arm in k["rc_record"] else k["ke"].get(arm, k["rc"][arm])
        if arm in k["inspect_file"]:
            open(os.path.join(root, "%s_x.inspect.txt" % arm), "w").write(
                "%s %s 2026-08-31T00:00:00Z 2026-08-31T00:01:00Z %s 4294967296 %s\n"
                % (ke, k["oom"][arm], k["cs"][arm], IMG_DIGEST[rl]))
        if arm in k["drop_row"]:
            continue
        led.append(ROWFMT.format(arm=arm, row=k["ledger_row_label"].get(arm, rl), img="img",
                                 dig=IMG_DIGEST[rl], rc=k["rc"][arm], wall=60,
                                 ranks=ARM_RANKS[arm], cm=k["cm"][arm], cap=CAPS[arm],
                                 mem=k["mem"][arm], ke=ke, oom=k["oom"][arm], mpost=k["mpost"],
                                 cs=k["cs"][arm], dl=k["dl"], log=log))
    open(os.path.join(root, "ledger.txt"), "w").write("".join(led))
    return root


def _drive_k_red(root, k_red=0.5):
    """SINGLE MUTATION, driven RED: move the REGISTERED K -- and nothing else --
    below 1, grade the SAME clean fixture that grades PASS at the registered K, and
    require the refusal to be PLANT_NOT_SUFFICIENT_BY_CONSTRUCTION BY NAME.

    `refused()` alone would be satisfied by ANY refusal, and a red that is accepted
    without being attributed cannot tell a working assertion from an unrelated
    crash.  K is restored in a `finally` so a failure inside cannot leave the module
    mutated, and the restore is asserted here AND again by leg B4 from outside."""
    global FLIP_PLANT_K
    keep = FLIP_PLANT_K
    kinds, other = None, None
    try:
        FLIP_PLANT_K = k_red
        try:
            grade(root)
        except Refusal as exc:
            kinds = list(json.loads(str(exc)).get("detail", {}).keys())
        except Exception as exc:                      # pragma: no cover
            other = "%s: %s" % (type(exc).__name__, exc)
    finally:
        FLIP_PLANT_K = keep
    return (FLIP_PLANT_K == keep and keep > 1.0 and other is None
            and kinds is not None
            and "PLANT_NOT_SUFFICIENT_BY_CONSTRUCTION" in kinds)


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
        if root is None:
            return False
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

    here = os.path.dirname(os.path.abspath(__file__))
    self_path = os.path.abspath(__file__)

    # ============ (A) RULE 14 -- THE ROW-LABEL SWEEP, DRIVEN BOTH DIRECTIONS ==========
    a = audit_row_label_sites(self_path)
    unit("R1 (rule 14) THIS comparator carries ZERO forbidden row-label derivations and "
         "EXACTLY ONE ROW_OF_ARM subscript site -- the one inside row_of()",
         a["verdict"] == "OK" and a["forbidden"] == []
         and a["row_of_arm_subscript_count"] == ROW_OF_ARM_SUBSCRIPTS_ALLOWED)
    unit("R2 (rule 14) the ARM and ROW label sets are DISJOINT, so a swapped artefact "
         "cannot resolve to something", a["label_sets_disjoint"])
    planted_src = os.path.join(tmp, "planted_row_derivation.py")
    open(planted_src, "w").write(
        "ROW_OF_ARM = {}\n"
        "def bad(arm):\n"
        "    rk = 'S' if arm.endswith('-S') else 'P'\n"
        "    return ROW_OF_ARM[arm], rk\n")
    pa = audit_row_label_sites(planted_src)
    unit("R3 (rule 14) PLANTED BAD SITE: a source deriving a row from an arm-name suffix "
         "test and a conditional short spelling -- SO-1c's exact defect -- is CAUGHT.  The "
         "sweep is a READING, not a blind zero (%d hits)" % len(pa["forbidden"]),
         pa["verdict"] != "OK" and len(pa["forbidden"]) >= 2
         and any("endswith" in h["pattern"] for h in pa["forbidden"])
         and any("if" in h["pattern"] for h in pa["forbidden"]))
    commented = os.path.join(tmp, "commented_row_derivation.py")
    open(commented, "w").write(
        "ROW_OF_ARM = {}\n"
        "# a COMMENT that quotes rk = 'S' if arm.endswith('-S') else 'P'\n"
        "def row_of(arm):\n"
        "    \"\"\"a DOCSTRING that quotes arm.endswith('-S') and row[0].\"\"\"\n"
        "    return ROW_OF_ARM[arm]\n")
    ca = audit_row_label_sites(commented)
    unit("R3b (rule 14) DRIVEN CONTROL, the OTHER direction: the SAME shapes written in a "
         "COMMENT and in a DOCSTRING are NOT counted, while R3 shows the shapes written in "
         "CODE are -- so R1's zero is a reading of executable lines and is not bought by a "
         "sweep that blinds itself to the literals it hunts",
         ca["verdict"] == "OK" and ca["forbidden"] == []
         and ca["row_of_arm_subscript_count"] == 1)
    planted2 = os.path.join(tmp, "planted_second_site.py")
    open(planted2, "w").write(
        "ROW_OF_ARM = {}\n"
        "def row_of(arm):\n    return ROW_OF_ARM[arm]\n"
        "def elsewhere(arm):\n    return ROW_OF_ARM[arm]\n")
    p2 = audit_row_label_sites(planted2)
    unit("R4 (rule 14) PLANTED SECOND CALL SITE: a NEW unrepaired ROW_OF_ARM subscript "
         "outside row_of() is caught by COUNT (2 > 1) -- SO-1c's amendment R8 repaired one "
         "of three and this leg is what makes that impossible here",
         p2["verdict"] != "OK" and p2["row_of_arm_subscript_count"] == 2)
    unit("R5 (rule 14) row_of() REFUSES a label that is not a registered arm, and REFUSES "
         "a ROW label handed where an ARM belongs (the swapped-artefact direction)",
         _raises(lambda: row_of("F-S")) and _raises(lambda: row_of("SHIPPED")))

    # ============ (B) THE FORBIDDEN WHOLE-FILE SUBSTRING SCAN, BOTH DIRECTIONS ========
    unit("C1 (C5) THIS comparator contains ZERO whole-file substring scans",
         whole_file_substring_scans(self_path) == [])
    planted_wfs = os.path.join(tmp, "planted_wholefile.py")
    open(planted_wfs, "w").write(
        "TOKENS = ('a',)\ndef f(text):\n    return [t for t in TOKENS if t in text]\n")
    unit("C2 (C5) PLANTED: the AST detector sees a `t in text` whole-file scan in a "
         "planted source -- C1's zero is a reading, not blindness",
         len(whole_file_substring_scans(planted_wfs)) == 1)
    hits, excl = fatal_scan([("a.log", "trapFpe: Floating point exception trapping enabled\n"
                                       "ok line\n")])
    unit("C3 (C5) the ONE registered benign exclusion fires on OpenFOAM's trapFpe banner, "
         "the line is NAMED and COUNTED, and no fatal hit is produced",
         hits == [] and len(excl) == 1 and excl[0]["line"] == 1
         and "trapFpe" in excl[0]["pattern"])
    hits2, excl2 = fatal_scan([("a.log", "ok\n--> FOAM FATAL ERROR: boom\n")])
    unit("C4 (C5) PLANTED POSITIVE: a real FOAM FATAL ERROR on line 2 is caught and the "
         "LINE NUMBER is named -- so C3's zero is not the scanner failing to see anything",
         len(hits2) == 1 and hits2[0]["line"] == 2 and hits2[0]["token"] == "FOAM FATAL ERROR")
    hits3, _ = fatal_scan([("a.log", "Foam::sigFpe::sigHandler(int) at ??:?\n")])
    unit("C5u (C5) the EXTRA positive token Foam::sigFpe::sigHandler is caught -- it is a "
         "REPORT that a trap fired, not the banner saying trapping is on",
         len(hits3) == 1 and hits3[0]["token"] == "Foam::sigFpe::sigHandler")

    # ============ L-332 and the instrument cross-check ================================
    unit("L1 ast.Assert count = 0 in so2mr_grade.py and so2mr_xm.py",
         count_asserts(self_path) == 0
         and count_asserts(os.path.join(here, "so2mr_xm.py")) == 0)
    p = os.path.join(tmp, "planted_assert.py")
    open(p, "w").write("x = 1\nassert x == 1\n")
    unit("L2 PLANTED: the assert counter sees a planted assert (=1)", count_asserts(p) == 1)
    ic = instrument_constants(os.path.join(here, "so2mr_xm.py"))
    unit("S1 (schema) the INSTRUMENT's own declared key vocabulary, read out of "
         "so2mr_xm.py's bytes by AST, EQUALS this comparator's registered vocabulary -- "
         "two files, read independently, rather than one file agreeing with itself",
         list(ic.get("OUTPUTS") or ()) == list(OUTPUTS)
         and ic.get("DKEY_OF_OUTPUT") == DKEY_OF_OUTPUT
         and list(ic.get("CONTROL_OUTPUTS") or ()) == list(CONTROL_OUTPUTS)
         and ic.get("GRADED_OUTPUT") == GRADED_OUTPUT
         and ic.get("CTRL_STEP") == CTRL_STEP and ic.get("PLANT") == PLANT
         and ic.get("ITEM") == ITEM)
    unit("S2 (schema) the INSTRUMENT's registered components and steps EQUAL this "
         "comparator's, and its artefact names EQUAL the ones this comparator opens",
         [list(c) for c in (ic.get("COMPONENTS") or [])] == COMPONENTS_REGISTERED
         and ic.get("STEPS") == STEPS_REGISTERED and ic.get("TB_STEPS") == TB_STEPS_REGISTERED
         and ic.get("OUT_X") == ARTEFACT["X-S"] and ic.get("OUT_F") == ARTEFACT["G-S"])

    # ============ THE POSITIVE PATH, FROM A REAL PRODUCER ARTEFACT ====================
    have_real = os.path.isfile(REAL_PARENT_X) and os.path.isfile(REAL_PARENT_F)
    unit("F0 (schema) the REAL parent artefacts are on disk and are the positive fixture's "
         "source: %s and %s" % (REAL_PARENT_X, REAL_PARENT_F), have_real)
    r = grade(_real_fixture(tmp))
    unit("F1 clean REAL-derived fixture -> item PASS, both rows PASS, G-M2/G9/G10/G11/G12 PASS",
         r["verdict"] == "PASS" and r["rows"] == {"SHIPPED": "PASS", "PATCHED": "PASS"}
         and r["gates"]["G-M2_mesh_identity"] == "PASS"
         and r["gates"]["G9_toolchain"]["verdict"] == "PASS"
         and r["gates"]["G10_caps"]["verdict"] == "PASS"
         and r["gates"]["G11_memory"]["verdict"] == "PASS"
         and r["gates"]["G12_placement"]["verdict"] == "PASS")
    unit("F2 the clean fixture's C5 scan APPLIED and NAMED the benign trapFpe exclusion on "
         "every one of the five arms and still produced no fatal hit (count %d)"
         % r["c5_benign_exclusion_count"],
         r["c5_benign_exclusion_count"] == len(ARM_LABELS)
         and all(len(r["c5_benign_exclusions"][a]) == 1 for a in ARM_LABELS))
    unit("F3 G-CMV reads the baseline CMZ, bands it and PASSES on both rows; G-NZ PASSES "
         "on both rows with the aoa entry non-zero on BOTH sides",
         all(r["gates"]["per_row"][rl]["G_CMV"]["verdict"] == "PASS" for rl in ROW_LABELS)
         and all(r["gates"]["per_row"][rl]["G_NZ"]["verdict"] == "PASS" for rl in ROW_LABELS))
    unit("F4 (rule 3, direction A) the instrument CTRL tuple is re-read FROM DISK on both "
         "rows: all three entries exactly 0.0 unplanted, entry 0 exactly PLANT/(2 s) "
         "planted, companions still exactly 0.0",
         all(r["controls"]["instrument_ctrl"][rl]["zeros"] == [0.0, 0.0, 0.0]
             and abs(r["controls"]["instrument_ctrl"][rl]["planted"][0]
                     - PLANT / (2.0 * CTRL_STEP)) < 1e-15
             and r["controls"]["instrument_ctrl"][rl]["planted"][1:] == [0.0, 0.0]
             for rl in ROW_LABELS))
    unit("F5 (rule 3, direction A) the GRADER's own planted copy of each G table is "
         "re-read through the same reader and every value moved by exactly PLANT",
         all(r["controls"]["grader_plant"][rl]["grader_plant_seen"]
             and r["controls"]["grader_plant"][rl]["worst_residual"] <= 1e-12
             for rl in ROW_LABELS))
    unit("F6 (rule 3, DIRECTION B) G5m FLIPPED to GATE FAIL on a planted copy of the REAL "
         "X artefact, on both rows, in the SAME invocation as the verdict it licenses, and "
         "the PLANT WAS SUFFICIENT BY CONSTRUCTION on every row (margin ratio %g)"
         % FLIP_PLANT_K,
         all(r["controls"]["flip_G5m"][rl]["demonstrated"]
             and r["controls"]["flip_G5m"][rl]["planted_verdict"] == "GATE FAIL"
             and r["controls"]["flip_G5m"][rl]["pair_verdict_planted"] == "GATE FAIL"
             and r["controls"]["flip_G5m"][rl]["plant_is_sufficient"]
             and abs(r["controls"]["flip_G5m"][rl]["plant_margin_ratio"] - FLIP_PLANT_K) < 1e-12
             and r["controls"]["flip_G5m"][rl]["flipped"] for rl in ROW_LABELS))
    unit("F7 (rule 3, DIRECTION B) G-NZ FLIPPED to GATE FAIL when the aoa entry was forced "
         "to 0.0, on both rows -- the gate is shown load-bearing (L-314)",
         all(r["controls"]["flip_G_NZ"][rl]["planted_verdict"] == "GATE FAIL"
             for rl in ROW_LABELS))
    # ---- (B) THE PLANT RULE: SUFFICIENCY BY CONSTRUCTION, DRIVEN BOTH WAYS ----------
    # THE KNOWN POSITIVE FIRST.  A rule that cannot reproduce SO-2M's recorded
    # refusal from SO-2M's own recorded d_ref has not been shown able to see the
    # defect it exists to prevent, and every GREEN below it would be unearned.
    _need_so2m = FD_BAND_PCT / 100.0 * abs(SO2M_RECORDED_D_REF)
    unit("B0 (KNOWN POSITIVE) this comparator's band arithmetic, applied to SO-2M's OWN "
         "recorded d_ref = %.17g, reproduces SO-2M's recorded band-crossing threshold "
         "%.17g to 1e-15, and SO-2M's registered ABSOLUTE plant %.6g is only %.4f %% of "
         "|d_ref| -- it CANNOT cross a %.1f %% band.  SO-2M's refusal is re-derived here, "
         "not quoted."
         % (SO2M_RECORDED_D_REF, SO2M_RECORDED_NEED, SO2M_RECORDED_PLANT,
            SO2M_RECORDED_PLANT / abs(SO2M_RECORDED_D_REF) * 100.0, FD_BAND_PCT),
         abs(_need_so2m - SO2M_RECORDED_NEED) <= 1e-15
         and not SO2M_RECORDED_PLANT > _need_so2m)
    _mag_so2m, _sgn_so2m, _n2 = flip_plant(SO2M_RECORDED_D_REF, 0.0)
    unit("B0b (THE REPAIR, ON THE SAME NUMBER) the SO-2MR RULE applied to that SAME d_ref "
         "gives P = %.17g, which EXCEEDS the threshold by a factor of exactly %g.  The "
         "number SO-2M could not clear, SO-2MR clears by construction."
         % (_mag_so2m, FLIP_PLANT_K),
         _mag_so2m > _n2 and abs(_mag_so2m / _n2 - FLIP_PLANT_K) < 1e-12
         and abs(_n2 - SO2M_RECORDED_NEED) <= 1e-15)
    unit("B0c (THE SIGN RULE) the plant moves the adjoint entry AWAY from d_ref from EITHER "
         "side, so no cancellation is possible: sign is -1 when J < d_ref and +1 when "
         "J >= d_ref, and |d_ref - J'| = |d_ref - J| + P exactly in both cases",
         flip_plant(-1.0, -2.0)[1] < 0.0 and flip_plant(-1.0, 0.0)[1] > 0.0
         and all(abs(abs(-1.0 - (jv + flip_plant(-1.0, jv)[1]))
                     - (abs(-1.0 - jv) + flip_plant(-1.0, jv)[0])) < 1e-15
                 for jv in (-2.0, -1.05, -1.0, -0.95, 0.0, 3.0)))
    unit("B0d (THE ALGEBRA THE RULE RESTS ON) rel_planted = rel_live + K*band, so the "
         "planted relative error is at least %.1f %% against a %.1f %% band from ANY live "
         "position -- %.0f %% margin, and K > 1 is what makes it sound"
         % (FLIP_PLANT_K * FD_BAND_PCT, FD_BAND_PCT,
            (FLIP_PLANT_K - 1.0) * 100.0),
         FLIP_PLANT_K > 1.0
         and all(abs((abs(dr - (jv + flip_plant(dr, jv)[1])) / abs(dr) * 100.0)
                     - (abs(dr - jv) / abs(dr) * 100.0 + FLIP_PLANT_K * FD_BAND_PCT)) < 1e-9
                 for dr, jv in ((-0.04976246220706002, -0.0395364315201953),
                                (0.00365546, 0.00370),
                                (2.5, 2.4), (2.5, 2.6))))
    unit("B1 (DIRECTION B, PORTABILITY) at the CL-CLASS scale -- the scale at which SO-2M's "
         "ABSOLUTE plant was MEASURED unable to cross band D, and at which SO-2M's own leg "
         "B1 recorded the comparator REFUSING -- the RULE-SIZED plant FLIPS the gate on "
         "both rows and the item grades through to a verdict",
         (lambda rr: rr is not None and rr["verdict"] in VOCAB
          and all(rr["controls"]["flip_G5m"][rl]["planted_verdict"] == "GATE FAIL"
                  and rr["controls"]["flip_G5m"][rl]["pair_verdict_planted"] == "GATE FAIL"
                  and rr["controls"]["flip_G5m"][rl]["plant_is_sufficient"]
                  for rl in ROW_LABELS))(
             grade(_real_fixture(tmp, tw(cmz_scale={rl: FIXTURE_CMZ_PHYSICAL
                                                    for rl in ROW_LABELS})))))
    _bar = FD_BAND_PCT / 100.0 * abs(FIXTURE_CMZ_PHYSICAL
                                     * min(abs(float(v)) for v in
                                           json.load(open(REAL_PARENT_X))["adjoint"]["CL"]["shape"]))
    unit("B2 (DIRECTION B, THE ARITHMETIC THAT KILLED SO-2M) at that scale the plant needed "
         "to cross band D is %.6g and SO-2M's registered ABSOLUTE plant was %.6g -- a "
         "factor of %.1f short.  SO-2MR's RULE plant at the same reference is %.6g, a "
         "factor of %g OVER.  Same machinery, same band, sufficient plant."
         % (_bar, PLANT, _bar / PLANT, FLIP_PLANT_K * _bar, FLIP_PLANT_K),
         _bar > PLANT and FLIP_PLANT_K * _bar > _bar)
    unit("B3 (DIRECTION B, DRIVEN RED) with FLIP_PLANT_K temporarily moved BELOW 1 the "
         "plant can no longer cross band D and the comparator REFUSES "
         "PLANT_NOT_SUFFICIENT_BY_CONSTRUCTION -- the sufficiency assertion is shown "
         "LOAD-BEARING rather than merely present (L-314)",
         _drive_k_red(_real_fixture(tmp)))
    unit("B4 (DIRECTION B, RESTORED) FLIP_PLANT_K is back at its registered %g after the "
         "RED drive and the clean fixture grades PASS again -- the RED leg left no residue"
         % FLIP_PLANT_K,
         FLIP_PLANT_K == 2.0 and grade(_real_fixture(tmp))["verdict"] == "PASS")
    unit("F8 P1 and P2 HIT on the clean fixture; the aggregate is NAMED as the "
         "vector-relative norm as printed; NO GCI is quoted anywhere",
         r["predictions"]["P1_CMZ_evaluates_and_is_finite_on_both_rows"] == "HIT"
         and r["predictions"]["P2_CMZ_baseline_inside_the_registered_band"] == "HIT"
         and "VECTOR-RELATIVE" in r["gates"]["per_row"]["SHIPPED"]["G5m"]["aggregate_is"]
         and "NO GCI IS QUOTED" in r["no_gci"])
    unit("F9 G6 is printed as the SENTENCE beside the verdict, never as a value, and names "
         "AV-2's measurement as its reason",
         r["gates"]["G6_dot_product_duality_and_complex_step"].startswith("NOT MEASURED")
         and "AV-2" in r["gates"]["G6_dot_product_duality_and_complex_step"])
    unit("F10 the DIVERGENCE shipped-vs-patched on d(CMZ)/dx is REPORTED with a number for "
         "every registered component and is NEVER GATED",
         len(r["divergence_shipped_vs_patched_dCMZ"]) == len(COMPONENTS_REGISTERED)
         and "NEVER GATED" in r["divergence_note"])

    # ============ SCHEMA BREAKS, on the REAL-DERIVED fixture ==========================
    unit("S3 (schema) PLANTED SCHEMA BREAK: the graded d-key renamed dCMZ -> dCmz at its "
         "registered location -> REFUSAL.  This is the leg a fixture hand-authored from "
         "the reader's expectations could not have",
         refused(_real_fixture(tmp, tw(drop_dkey={"SHIPPED": True}))))
    unit("S4 (schema) PLANTED: the instrument's control tuple shortened to one entry -> "
         "REFUSAL (an EMPTIED tuple is seen by a broken reader too)",
         refused(_real_fixture(tmp, tw(ctrl_tuple={"PATCHED": ["dCMZ"]}))))
    unit("S5 (schema) PLANTED: the CTRL planted entry broken -> REFUSAL (a reader not "
         "shown able to see a non-zero)",
         refused(_real_fixture(tmp, tw(ctrl_ok={"SHIPPED": False}))))

    # ============ G5m, THE PLATEAU AND THE EXCLUSION ACCOUNTING ======================
    r = grade(_real_fixture(tmp, tw(err={"SHIPPED": {("shape", 3): 7.0}})))
    unit("G1u PLANTED 7 % error on the shipped d(CMZ)/d(shape[3]) -> that pair GATE FAIL, "
         "SHIPPED row GATE FAIL, item GATE FAIL -- the REGISTERED PREDICTED OUTCOME shape",
         r["rows"]["SHIPPED"] == "GATE FAIL" and r["verdict"] == "GATE FAIL"
         and r["gates"]["per_row"]["SHIPPED"]["G5m"]["n_gate_fail"] == 1
         and r["predictions"]["P5_SHIPPED_row_G5m_GATE_FAILS"] == "HIT")
    r = grade(_real_fixture(tmp, tw(flip={"SHIPPED": (("shape", 6),)})))
    unit("G2u PLANTED sign flip on shipped shape[6] -> counted as a flip, GATE FAIL "
         "whatever its magnitude",
         r["gates"]["per_row"]["SHIPPED"]["G5m"]["sign_flips"] == 1
         and r["rows"]["SHIPPED"] == "GATE FAIL" and r["rows"]["PATCHED"] == "PASS")
    r = grade(_real_fixture(tmp, tw(noplateau={"SHIPPED": (("shape", 0),)})))
    c0 = [c for c in r["gates"]["per_row"]["SHIPPED"]["G5m"]["components"]
          if c["dv"] == "shape" and c["idx"] == 0][0]
    unit("G3u PLANTED no-plateau on ONE pair -> that pair NOT A RESULT with reason "
         "NO_PLATEAU, the exclusion COUNTED AND NAMED, row still PASS on 4 graded pairs",
         c0["verdict"] == "NOT A RESULT" and c0["reason"] == "NO_PLATEAU"
         and r["gates"]["per_row"]["SHIPPED"]["G5m"]["n_excluded"] == 1
         and {"dv": "shape", "idx": 0, "reason": "NO_PLATEAU"}
             in r["gates"]["per_row"]["SHIPPED"]["G5m"]["exclusions_named"]
         and r["rows"]["SHIPPED"] == "PASS"
         and r["gates"]["per_row"]["SHIPPED"]["G5m"]["n_graded"] == 4)
    r = grade(_real_fixture(tmp, tw(noplateau={"PATCHED": (("shape", 0), ("shape", 3),
                                                           ("shape", 6), ("shape", 7))})))
    unit("G4u PLANTED four excluded pairs on PATCHED -> 80 %% > 75 %% excluded -> row "
         "NOT A RESULT, item NOT A RESULT, every exclusion named (%d), and the DIRECTION-B "
         "control on that row is recorded NOT DEMONSTRATED with its reason rather than "
         "either passing silently or refusing -- a NOT A RESULT row licenses no verdict"
         % r["gates"]["per_row"]["PATCHED"]["G5m"]["n_excluded"],
         r["rows"]["PATCHED"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT"
         and r["gates"]["per_row"]["PATCHED"]["G5m"]["n_excluded"] == 4
         and r["gates"]["per_row"]["PATCHED"]["G5m"]["excluded_pct"] == 80.0
         and r["controls"]["flip_G5m"]["PATCHED"]["demonstrated"] is False
         and r["controls"]["flip_G5m"]["SHIPPED"]["demonstrated"] is True)
    r = grade(_real_fixture(tmp, tw(fd_fail={"SHIPPED": (("shape", 0),)})))
    unit("G5u a FAILED FD primal EXCLUDES its pair with reason "
         "FD_STEP_FAILED_OR_ABSENT, counted and named, row still graded on the rest",
         any(e["reason"] == "FD_STEP_FAILED_OR_ABSENT"
             for e in r["gates"]["per_row"]["SHIPPED"]["G5m"]["exclusions_named"])
         and r["gates"]["per_row"]["SHIPPED"]["G5m"]["n_graded"] == 4)

    # ============ G-CMV, G-NZ, G-TB =================================================
    r = grade(_real_fixture(tmp, tw(cmz_base={"SHIPPED": -0.31})))
    unit("V1 (G-CMV) PLANTED |CMZ| = 0.31 outside the registered band 0.02 -> G-CMV "
         "GATE FAIL, item GATE FAIL, P2 MISS -- and the VALUE and SIGN are printed either way",
         r["gates"]["per_row"]["SHIPPED"]["G_CMV"]["verdict"] == "GATE FAIL"
         and r["verdict"] == "GATE FAIL"
         and r["predictions"]["P2_CMZ_baseline_inside_the_registered_band"] == "MISS"
         and r["gates"]["per_row"]["SHIPPED"]["G_CMV"]["sign"] == "-")
    r = grade(_real_fixture(tmp, tw(nz_zero={"SHIPPED": True})))
    unit("V2 (G-NZ) PLANTED BLIND READER: d(CMZ)/d(patchV[1]) reads 0.0 on BOTH sides of "
         "the shipped row -> G-NZ GATE FAIL, item GATE FAIL.  A blind reader FAILS this "
         "gate instead of passing it, which is the whole reason it is worth having and is "
         "the OPPOSITE failure direction from SO-2a's exact-zero G-STRUCT.",
         r["gates"]["per_row"]["SHIPPED"]["G_NZ"]["verdict"] == "GATE FAIL"
         and r["gates"]["per_row"]["SHIPPED"]["G_NZ"]["adjoint_nonzero"] is False
         and r["gates"]["per_row"]["SHIPPED"]["G_NZ"]["fd_nonzero"] is False
         and r["verdict"] == "GATE FAIL")
    r = grade(_real_fixture(tmp, tw(tb_pass={"PATCHED": (("shape", 0), ("shape", 3),
                                                          ("shape", 6), ("shape", 7),
                                                          ("patchV", 1))})))
    unit("T1 (G-TB) PLANTED -- the DELIBERATELY WRONG step AGREES on 5/5 of a row whose "
         "G5m is PASS -> G-TB GATE FAIL, that row WITHDRAWN to NOT A RESULT, P6 MISS",
         r["gates"]["per_row"]["PATCHED"]["G_TB_trivial_baseline"]["verdict"] == "GATE FAIL"
         and r["rows"]["PATCHED"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT"
         and r["predictions"]["P6_trivial_baseline_fails_at_least_4_of_5_on_each_row"] == "MISS")
    r = grade(_real_fixture(tmp, tw(tb_pass={"SHIPPED": (("shape", 0), ("shape", 3),
                                                          ("shape", 6), ("shape", 7),
                                                          ("patchV", 1))},
                                    err={"SHIPPED": {("shape", 3): 7.0}})))
    unit("T2 (G-TB, THE RESTRICTION SO-2a PAID FOR) a row whose G5m already GATE FAILs "
         "keeps its GATE FAIL even when G-TB fails on it: composing G-TB there would turn "
         "a REAL GRADIENT DEFECT -- this item's registered prediction -- into NOT A RESULT "
         "and hide the finding.  G-TB's own verdict is still PRINTED on that row.",
         r["rows"]["SHIPPED"] == "GATE FAIL"
         and r["gates"]["per_row"]["SHIPPED"]["G_TB_trivial_baseline"]["verdict"] == "GATE FAIL"
         and r["verdict"] == "GATE FAIL")
    r = grade(_real_fixture(tmp, tw(tb_pass={"PATCHED": (("shape", 0),)})))
    unit("T3 (G-TB) ONE component passing at the wrong step is inside TB_MAX_PASSING -> "
         "G-TB PASS, row PASS, P6 still HIT (4 of 5 failing)",
         r["gates"]["per_row"]["PATCHED"]["G_TB_trivial_baseline"]["verdict"] == "PASS"
         and r["rows"]["PATCHED"] == "PASS"
         and r["predictions"]["P6_trivial_baseline_fails_at_least_4_of_5_on_each_row"] == "HIT")

    # ==== RULING 1 (2026-08-31) DRIVEN: the trivial-baseline step is 1e-8 on ALL ====
    # ==== FIVE components, and that constant is shown LOAD-BEARING in both       ====
    # ==== directions.  Before this repair the code carried patchV 1e-6, inherited ====
    # ==== from SO-1a's real artefact and registered NOWHERE in this item's frozen ====
    # ==== document.  The document was NOT amended to fit the code.               ====
    unit("TB0 (RULING 1, REFUSAL DIRECTION) an F artefact declaring the PRE-REPAIR "
         "tb_steps {shape:[1e-8], patchV:[1e-6]} is REFUSED by read_F -- so the "
         "registered 1e-8 is enforced against the producer and is not merely written "
         "down.  Reverting TB_STEPS_REGISTERED to 1e-6 turns this leg RED.",
         refused(_real_fixture(tmp, tw(tb_steps={"SHIPPED": {"shape": [1.0e-8],
                                                             "patchV": [1.0e-6]}}))))
    r = grade(_real_fixture(tmp))
    tbc = {(c["dv"], c["idx"]): c for c in
           r["gates"]["per_row"]["PATCHED"]["G_TB_trivial_baseline"]["components"]}
    unit("TB1 (RULING 1, POSITIVE DIRECTION) the patchV[1] trivial-baseline probe is "
         "FOUND AND GRADED at the registered step 1e-8 -- tb_step reads 1e-08 and the "
         "reason is NOT TB_PROBE_FAILED_OR_ABSENT, so the repaired step is a location "
         "the reader actually reaches rather than a constant nothing looks up",
         tbc[("patchV", 1)].get("tb_step") == 1.0e-8
         and tbc[("patchV", 1)].get("reason") != "TB_PROBE_FAILED_OR_ABSENT"
         and tbc[("patchV", 1)]["tb_verdict"] == "GATE FAIL"
         and all(c.get("tb_step") == 1.0e-8 for c in tbc.values()))
    r = grade(_real_fixture(tmp, tw(tb_pass={"PATCHED": (("patchV", 1),)})))
    unit("TB2 (RULING 1) the SAME patchV[1] probe at 1e-8 reads PASS when the wrong "
         "step is made to AGREE -- so TB1's GATE FAIL is a reading of the number and "
         "not a stuck verdict from a missing key (1 of 5 passing, inside TB_MAX_PASSING)",
         r["gates"]["per_row"]["PATCHED"]["G_TB_trivial_baseline"]
          ["n_passing_band_D_at_the_WRONG_step"] == 1
         and [c for c in r["gates"]["per_row"]["PATCHED"]["G_TB_trivial_baseline"]
              ["components"] if c["dv"] == "patchV"][0]["tb_verdict"] == "PASS"
         and r["gates"]["per_row"]["PATCHED"]["G_TB_trivial_baseline"]["verdict"] == "PASS")

    # ==== RULING 2 (2026-08-31): BAND E AND THE MIN_GRADED FLOOR ARE SHOWN ABLE ====
    # ==== TO FAIL.  Both constants previously survived deliberate mutation with  ====
    # ==== the suite still green (AGG_BAND_PCT 5.0 -> 500.0 and MIN_GRADED 2 -> 0 ====
    # ==== both left 66/66), i.e. HALF OF G5m's BRIGHT LINE WAS WIRED AND NEVER   ====
    # ==== EXERCISED (L-314).  A band that cannot fail is not a band.             ====
    r = grade(_real_fixture(tmp))
    g5c = r["gates"]["per_row"]["PATCHED"]["G5m"]
    unit("E1 (band E, the PASSING direction) the clean fixture's AGGREGATE "
         "vector-relative error is %.6f %% and band_E reads PASS strictly inside the "
         "registered 5.0 %%" % g5c["aggregate_rel_err_pct"],
         g5c["band_E"] == "PASS" and g5c["aggregate_rel_err_pct"] < 5.0
         and g5c["aggregate_rel_err_pct"] > 0.0)
    r = grade(_real_fixture(tmp, tw(err_pct={"SHIPPED": 20.0})))
    g5e = r["gates"]["per_row"]["SHIPPED"]["G5m"]
    unit("E2 (band E, THE FAILING direction -- THIS LEG IS THE MUTATION DETECTOR) a "
         "20 %% planted error on every graded pair of the shipped row puts the "
         "AGGREGATE at %.4f %%, ABOVE the registered 5.0 %%, and band_E reads GATE "
         "FAIL.  Widening AGG_BAND_PCT to 500.0 flips this to PASS and turns this leg "
         "RED, which is the property the mutation previously did not have."
         % g5e["aggregate_rel_err_pct"],
         g5e["band_E"] == "GATE FAIL"
         and g5e["aggregate_rel_err_pct"] > AGG_BAND_PCT
         and g5e["aggregate_rel_err_pct"] > 5.0
         and g5e["aggregate_rel_err_pct"] < 500.0
         and r["rows"]["SHIPPED"] == "GATE FAIL")
    _per_pair = [c["rel_err_pct"] for c in g5e["components"] if c.get("rel_err_pct") is not None]
    unit("E3 (band E, THE STRUCTURAL READING, MEASURED NOT ASSERTED) the aggregate "
         "(%.4f %%) is <= the LARGEST per-pair relative error (%.4f %%) on the same "
         "fixture.  Bands D and E share a denominator convention, so the l2 aggregate "
         "is bounded by the worst pair and band E at the SAME 5.0 %% threshold can "
         "never be the SOLE cause of a GATE FAIL.  Band E is a confirmation, not an "
         "independent gate -- STATED, not hidden behind E2's green."
         % (g5e["aggregate_rel_err_pct"], max(_per_pair)),
         bool(_per_pair) and g5e["aggregate_rel_err_pct"] <= max(_per_pair) + 1.0e-9)
    r = grade(_real_fixture(tmp, tw(noplateau={"SHIPPED": (("shape", 0), ("shape", 3),
                                                           ("shape", 6), ("shape", 7))})))
    g5m1 = r["gates"]["per_row"]["SHIPPED"]["G5m"]
    unit("M1 (MIN_GRADED, THE FAILING direction -- THIS LEG IS THE MUTATION DETECTOR) "
         "four of five pairs excluded NO_PLATEAU leaves ONE graded pair, and the row "
         "reads NOT A RESULT with the reason naming THE MINIMUM-GRADED-PAIRS FLOOR "
         "specifically.  Lowering MIN_GRADED to 0 makes the excluded-percentage clause "
         "bind instead, the reason changes, and this leg goes RED.",
         g5m1["verdict"] == "NOT A RESULT" and g5m1["n_graded"] == 1
         and g5m1["aggregate_rel_err_pct"] is None
         and g5m1["reason"].startswith("fewer than %d graded pairs" % MIN_GRADED)
         and g5m1["min_graded_required"] == MIN_GRADED
         and r["rows"]["SHIPPED"] == "NOT A RESULT")
    r = grade(_real_fixture(tmp, tw(noplateau={"SHIPPED": (("shape", 0), ("shape", 3),
                                                           ("shape", 6))})))
    g5m2 = r["gates"]["per_row"]["SHIPPED"]["G5m"]
    unit("M2 (MIN_GRADED, the PASSING direction) THREE exclusions leave exactly TWO "
         "graded pairs -- the floor itself -- and grading PROCEEDS to an aggregate "
         "(%s) instead of refusing.  So M1's refusal is a reading of the COUNT and not "
         "a row that refuses whenever anything is excluded.  Together with M1 this "
         "also MEASURES that with five candidates the floor is reachable only at "
         "80 %% exclusion, i.e. it is subsumed by MAX_EXCLUDED_PCT = %.0f %% and can "
         "never bind alone -- STATED, not hidden."
         % (g5m2["aggregate_rel_err_pct"] is not None, MAX_EXCLUDED_PCT),
         g5m2["n_graded"] == 2 and g5m2["excluded_pct"] == 60.0
         and g5m2["verdict"] in ("PASS", "GATE FAIL")
         and g5m2["aggregate_rel_err_pct"] is not None
         and g5m1["excluded_pct"] == 80.0)

    # ============ G1, the five clauses, R-RC, and the infrastructure split ===========
    unit("A1u rc=1 on X-P -> REFUSAL", refused(_real_fixture(tmp, tw(rc={"X-P": 1}, ke={"X-P": 1}))))
    unit("A2u OOMKilled=true on G-S -> REFUSAL (G11 OOM HARD, never a re-fire)",
         refused(_real_fixture(tmp, tw(oom={"G-S": "true"}))))
    unit("A3u terminal marker absent in G-P log -> REFUSAL",
         refused(_real_fixture(tmp, tw(terminal={"G-P": False}))))
    unit("A4u artefact OLDER than the age datum (X-S) -> REFUSAL (rule 4 age guard)",
         refused(_real_fixture(tmp, tw(stale={"X-S"}))))
    unit("A5u the age datum GENUINELY ABSENT in BOTH registered names on X-S -> REFUSAL "
         "(a name swap would not have caught this; AV-1/AV-2)",
         refused(_real_fixture(tmp, tw(datum={"X-S": "none"}))))
    r = grade(_real_fixture(tmp, tw(datum={a: "plain" for a in ARM_LABELS},
                                    write_compression="off")))
    unit("A6u writeCompression off -> the datum resolves to the PLAIN 0/U by EXISTENCE, "
         "guard PASSES, verdict unchanged PASS",
         all(r["age_datum_resolution"][a]["resolved_name"] == "0/U"
             for a in ARM_LABELS if a != "MESH")
         and r["verdict"] == "PASS")
    unit("A7u FOAM FATAL ERROR in the X-S log at rc = 0 -> REFUSAL (C5 refuses regardless "
         "of rc, so R-RC can never launder a crash)",
         refused(_real_fixture(tmp, tw(fatal={"X-S": "--> FOAM FATAL ERROR: something"}))))
    unit("A8u a SIGNAL token at rc = 0 -> REFUSAL",
         refused(_real_fixture(tmp, tw(fatal={"G-S": "mpirun noticed that process rank 0 "
                                                     "exited on signal 9"}))))
    r = grade(_real_fixture(tmp, tw(rc_record={"G-P"})))
    unit("A9u R-RC: the rc RECORD absent on G-P while C2-C5 all hold -> rc value "
         "NOT MEASURED, rc=0 printed as an INFERENCE with its basis named, verdict PASS",
         r["verdict"] == "PASS"
         and r["rule4_clauses_per_arm"]["G-P"]["C1_rc_value"]["verdict"] == NOT_MEASURED
         and r["rc_inferences"]["G-P"]["rc_inferred"] == 0
         and "rc_record" in r["not_measured"]["G1"]["G-P"])
    unit("A10u R-RC: the rc RECORD absent AND C2 failing -> REFUSAL: NOT MEASURED is "
         "available ONLY when the other four clauses hold",
         refused(_real_fixture(tmp, tw(rc_record={"G-P"}, terminal={"G-P": False}))))
    unit("A11u R-RC: the rc RECORD absent but the harness rc NON-ZERO -> REFUSAL",
         refused(_real_fixture(tmp, tw(rc_record={"X-P"}, rc={"X-P": 1}))))
    unit("A12u harness rc 0 vs kernel exit 1 -> REFUSAL",
         refused(_real_fixture(tmp, tw(ke={"G-P": 1}))))
    unit("A13u ledger row absent and no inspect record -> REFUSAL",
         refused(_real_fixture(tmp, tw(drop_row={"G-P"}))))
    r = grade(_real_fixture(tmp, tw(drop_row={"G-P"}, inspect_file={"G-P"})))
    unit("A14u ledger row absent, ONE inspect record -> read from it, source named, "
         "core_min NOT_MEASURED, verdict PASS (L-342 infrastructure)",
         r["verdict"] == "PASS" and r["completion"]["arms"]["G-P"]["source"] == "inspect_record"
         and "G-P" in r["not_measured"]["G10"])
    r = grade(_real_fixture(tmp, tw(mpost="NOT_MEASURED", dl="NOT_MEASURED")))
    unit("A15u absent INFRASTRUCTURE fields -> verdict unchanged PASS, NOT_MEASURED named "
         "beside it, never composed into it (L-342)",
         r["verdict"] == "PASS" and r["not_measured"]["G1"].get("X-S")
         and "X-S" in r["not_measured"]["G12"])
    r = grade(_real_fixture(tmp))
    want_clauses = {"C1_rc_value", "C2_terminal_marker", "C3_artefact_present",
                    "C4_age_guard", "C5_no_fatal_token"}
    unit("A16u the five rule-4 clauses are present and named INDIVIDUALLY for every one of "
         "the five arms",
         all(set(r["rule4_clauses_per_arm"][a]) == want_clauses for a in ARM_LABELS))

    # ============ RULE 14 AT THE LEDGER, and G9/G10/G11/G12 =========================
    unit("R6 (rule 14) a ledger whose ROW field carries the OTHER row's label for X-P -> "
         "REFUSAL: the ROW field is CHECKED against the one registration, never trusted",
         refused(_real_fixture(tmp, tw(ledger_row_label={"X-P": "SHIPPED"}))))
    unit("R7 (rule 14) a ledger whose ROW field carries an ARM label where a ROW label "
         "belongs -> REFUSAL, because the two label sets are DISJOINT",
         refused(_real_fixture(tmp, tw(ledger_row_label={"G-S": "G-S"}))))
    r = grade(_real_fixture(tmp, tw(so={"X-P": SO_MD5["SHIPPED"]})))
    unit("N1 X-P carrying the SHIPPED .so md5 -> G9 GATE FAIL, item GATE FAIL",
         r["gates"]["G9_toolchain"]["verdict"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
    r = grade(_real_fixture(tmp, tw(cm={"G-S": 26.0})))
    unit("N2 G-S core_min 26.0 > cap 25.0 -> G10 GATE FAIL, and the actual/predicted ratio "
         "is printed per arm (rule 12 calibration)",
         r["gates"]["G10_caps"]["verdict"] == "GATE FAIL"
         and r["gates"]["G10_caps"]["per_arm"]["G-S"]["crossed"]
         and r["gates"]["G10_caps"]["per_arm"]["G-S"]["ratio_actual_over_predicted"] > 1.0)
    unit("N3 the five registered caps sum EXACTLY to the registered ceiling 79.0 -- a "
         "ceiling that is not the sum of its caps could not pass this leg",
         abs(sum(CAPS.values()) - ITEM_CEILING_CORE_MIN) < 1e-9)
    r = grade(_real_fixture(tmp, tw(mem={"X-S": "8g"})))
    unit("N4 (G11) X-S run at 8g against the registered 4g -> G11 GATE FAIL: the cap the "
         "launcher ACTUALLY enforced is read back, not assumed",
         r["gates"]["G11_memory"]["verdict"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
    r = grade(_real_fixture(tmp, tw(cs={"X-S": "4,14"})))
    unit("N4b (G11) the LEDGER's `4g` and the inspect record's byte form 4294967296 are "
         "the SAME cap and are compared as NUMBERS, while 8g and a garbage string are not -- "
         "a gate must not fail an arm for a difference of NOTATION (the AV-1/AV-2 class)",
         mem_bytes("4g") == 4294967296 and mem_bytes("4294967296") == 4294967296
         and mem_bytes("8g") != mem_bytes("4g") and mem_bytes("not-a-size") is None)
    unit("N5 (G12) X-S on cpuset 4,14 against the registered 9 -> G12 GATE FAIL",
         r["gates"]["G12_placement"]["verdict"] == "GATE FAIL")
    r = grade(_real_fixture(tmp, tw(cells=4033)))
    unit("N6 (G-M2) cells 4033 -> G-M2 GATE FAIL",
         r["gates"]["G-M2_mesh_identity"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")

    print("SO2MR GRADER SELFTEST units=%d expected=%d failures=%d python_O=%s"
          % (n, EXPECTED_UNITS, len(fails), not __debug__))
    if n != EXPECTED_UNITS or fails:
        print("SELFTEST FAIL: %s" % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS)))
        return 2
    print("SO2MR GRADER SELFTEST PASS %d/%d (counted against the frozen EXPECTED_UNITS)"
          % (n, EXPECTED_UNITS))
    return 0


def _raises(fn):
    try:
        fn()
        return False
    except Refusal:
        return True


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmpdir", default="/tmp")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if count_asserts(os.path.abspath(__file__)) != 0:
        print("REFUSAL: this comparator carries an assert statement (L-332)")
        return 2
    if a.selftest:
        d = os.path.join(a.tmpdir, "so2mr_selftest_%d" % os.getpid())
        os.makedirs(d, exist_ok=True)
        try:
            return selftest(d)
        finally:
            shutil.rmtree(d, ignore_errors=True)
    if not a.root:
        print("usage: so2mr_grade.py --root <run root> [--out FILE] | --selftest")
        return 64
    try:
        r = grade(a.root)
    except Refusal as e:
        print("REFUSAL: %s -> NOT A RESULT" % e)
        if a.out:
            json.dump({"item": "CURRICULUM-%s" % ITEM, "verdict": "NOT A RESULT",
                       "refusal": str(e)}, open(a.out, "w"), indent=1)
        return 2
    print(json.dumps(r, indent=1, default=str))
    if a.out:
        json.dump(r, open(a.out, "w"), indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
