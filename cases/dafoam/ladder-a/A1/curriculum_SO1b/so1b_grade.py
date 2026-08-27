#!/usr/bin/env python3
"""Curriculum SO-1b COMPARATOR -- NACA0012 INCOMPRESSIBLE drag-min-at-fixed-lift,
the FD-VERIFIED GRADIENT RUNG of Sanaa's shape-optimisation ladder SO-1.  TWO ROWS
(SHIPPED + PATCHED), adjoint X against a central-FD table F, on BOTH the objective
`CD` AND the EQUALITY-CONSTRAINT `CL`.  FROZEN by md5 in PREREGISTRATION.md section 7
before any container starts.  Computes nothing about physics; renders verdicts from
the FIXED vocabulary only (PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING).

DERIVED from `curriculum_D15/d15_grade.py` (md5 b429ec89e7a738647081783b8b755711)
with the registered deltas in so1b_grade_DELTAS_from_d15_grade.diff.  FIVE of them
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

PLANTED CONTROLS (rule 3, and Sanaa's directive section 1 "every guard ships its
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
import json
import math
import os
import re
import sys
import time

# ---- REGISTERED CONSTANTS (PREREGISTRATION.md; the document governs) ----------------
ITEM = "SO1b"
BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-SO1b-a1-naca0012-dragmin-opt"
# ARM ORDER IS THE CHAIN ORDER AND IT IS REGISTERED: the PATCHED row runs FIRST,
# because it is the row whose gradients SO-1a verifies and therefore the row whose
# optimum is the control for the shipped one run beside it.
ARMS_REQUIRED = ["MESH", "O-P", "E-P", "O-S", "E-S"]
ARM_KIND = {"MESH": "SCRIPT", "O-P": "SOLVER", "E-P": "SOLVER", "O-S": "SOLVER", "E-S": "SOLVER"}
ARM_ROW = {"MESH": "SHIPPED", "O-P": "PATCHED", "E-P": "PATCHED", "O-S": "SHIPPED", "E-S": "SHIPPED"}
ARM_MODE = {"O-P": "O", "O-S": "O", "E-P": "E", "E-S": "E"}
E_OF_ROW = {"P": "E-P", "S": "E-S"}
O_OF_ROW = {"P": "O-P", "S": "O-S"}
# np = 1 ON EVERY ARM by registration: DAFOAM_CHARTER.md section 5 (serial before
# parallel; a gradient verified at one np is a statement about THAT np), and A4's
# 16,600x decomposition effect is removed from the chain rather than assumed absent.
ARM_RANKS = {"MESH": 1, "O-P": 1, "E-P": 1, "O-S": 1, "E-S": 1}
ARTEFACT = {"MESH": "checkMesh.log", "O-P": "so1b_O.json", "E-P": "so1b_E.json",
            "O-S": "so1b_O.json", "E-S": "so1b_E.json"}
TERMINAL = {"O-P": "SO1B_O_WRITTEN", "E-P": "SO1B_E_WRITTEN",
            "O-S": "SO1B_O_WRITTEN", "E-S": "SO1B_E_WRITTEN"}
# (A) THE AGE-GUARD DATUM IS RESOLVED BY EXISTENCE, NEVER BY NAME.  `writeCompression
# on` (this tutorial's system/controlDict:27) rewrites `0/U` as `0/U.gz` on a serial
# arm; AV-1 and AV-2 both returned NOT A RESULT on that alone this session.  BOTH
# names are candidates, in this order; the one FOUND is recorded; NEITHER present is
# the only refusal, and it is DRIVEN in the selftest.
DATUM_CANDIDATES = {"MESH": ("0.orig/U", "0.orig/U.gz"), "O-P": ("0/U", "0/U.gz"),
                    "E-P": ("0/U", "0/U.gz"), "O-S": ("0/U", "0/U.gz"), "E-S": ("0/U", "0/U.gz")}
DATUM_FILE = ".so1b_age_datum"
CONTROLDICT_REL = os.path.join("system", "controlDict")
# (C) C5: an arm whose log carries any of these is REFUSED regardless of rc, so the
# R-RC relaxation in (B) can never launder a crash into a NOT MEASURED.
FATAL_TOKENS = ("FOAM FATAL ERROR", "FOAM FATAL IO ERROR", "Segmentation fault",
                "SIGSEGV", "SIGKILL", "MPI_ABORT", "signal 9", "Signal 11",
                "Floating point exception")
CAPS = {"MESH": 5.0, "O-P": 25.0, "E-P": 30.0, "O-S": 25.0, "E-S": 30.0}
ITEM_CEILING_CORE_MIN = 115.0                # == sum(CAPS.values()), asserted in main()
PREDICTED_CORE_MIN = {"MESH": 0.167, "O-P": 6.0, "E-P": 4.0, "O-S": 6.0, "E-S": 4.0}

# ---- THE OPTIMISER, REGISTERED BEFORE ANY CONTAINER STARTS -------------------------
# NONCONVERGENCE_STANDARD.md (7ffd6c73) anti-gaming clause, ABSOLUTE: answer-changing
# choices are never selected by agreement with the reference.  Optimiser settings
# enter that class the moment they are chosen by looking at the answer, so they are
# fixed here and in so1b_of.py and nowhere else.
OPTIMIZER_REGISTERED = "IPOPT"
MAX_ITER_REGISTERED = 30
OPT_TOL_REGISTERED = 1.0e-5
CONSTR_VIOL_TOL_REGISTERED = 1.0e-5
# DAFOAM_CHARTER.md section 9: PASS requires the OPTIMISER'S OWN convergence
# statement.  This is the exact string IPOPT prints when it has one.
IPOPT_CONVERGED_LINE = "EXIT: Optimal Solution Found."
# ...and the REGISTERED INTERMEDIATE THRESHOLD that makes GATE REACHED available to
# a run stopped by the iteration bound or the container deadline.  Section 9 gives
# GATE REACHED only "where a registered intermediate threshold was met"; without one
# registered IN ADVANCE the only other verdict is NOT A RESULT.
GATE_REACHED_CL_RESIDUAL_MAX = 1.0e-3        # 100x the optimiser's own constr_viol_tol
GATE_REACHED_REQUIRES_CD_BELOW_REFERENCE = True

# ---- THE POST-OPTIMUM CONSTRAINT CHECK (G-CL) --------------------------------------
# A drag reduction bought by quietly shedding lift is not a result.  The re-solve at
# the optimum must put CL back on its target within this tolerance or the row is
# NOT A RESULT WHATEVER THE DRAG DID.  1e-4 is 10x the optimiser's own
# constr_viol_tol and ~6 orders above the measured primal repeatability eta
# (D15 measured eta 1.30e-10 on this mesh), so it is neither noise-limited nor slack.
CL_TARGET = 0.5
CL_RESIDUAL_MAX = 1.0e-4

# ---- THE 23 GEOMETRIC CONSTRAINT ROWS (G-GEO), from the producer's own bounds ------
# so1b_runScript.py: thickcon lower 0.5 upper 3.0 (2 span x 10 chord = 20 rows),
# volcon lower 1.0 (1 row), rcon lower 0.8 (2 rows).  D1 measured all 23 in bound at
# its optimum and used the same 1e-6 slack on the bound; D13 measured 23/23 likewise.
GEO_BOUNDS = {"geometry.thickcon": (0.5, 3.0, 20),
              "geometry.volcon": (1.0, None, 1),
              "geometry.rcon": (0.8, None, 2)}
GEO_SLACK = 1.0e-6
GEO_ROWS_EXPECTED = 23

# ---- G-D7R, THE ATTRIBUTION GATE ---------------------------------------------------
# Sanaa's directives 2026-08-27T16:54Z section 4: "no improvement % quoted before its
# mechanism is decomposed (shape vs AoA vs operating point)".  This is a GATE, not a
# caveat: if the decomposition artefact is missing or incomplete the grader emits
# D7R_SUPPRESSED in place of every percentage and the row is NOT A RESULT.
ATTRIBUTION_FILE = "attribution.json"
ATTRIBUTION_POINTS_REQUIRED = ("A0", "A", "B", "C", "D")
D7R_SUPPRESSED = "SUPPRESSED_BY_G_D7R -- no improvement percentage is reported until the mechanism is decomposed"
# C' (the optimum shape re-trimmed to CL_target) must coincide with D (the optimum) to
# within this, or the optimum was not feasible and the feasibility reading says so.
CPRIME_VS_D_CD_MAX = 1.0e-4
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
# ---- PREDICTIONS, frozen here, scored HIT/MISS and NEVER adjusted -------------------
# The tight ones are anchored on MEASURED values from this exact problem: D1
# (curriculum_D1/RESULTS.md) and D13 (C-71, five perturbed starts).
PRED = {
    "PA_cells": 4032,
    "PB_CD_trimmed_band": (0.02090, 0.02100),        # D1's own registered band; D1 measured 0.020943920630946831
    "PB_CL_trimmed_max_residual": 1.0e-4,
    "PC_patched_majors_band": (6, 20),               # D1 11; D13 9,9,10,10,11 (C-71)
    "PD_patched_CD_opt_band": (0.0175273, 0.0175285),  # D1 0.017527899854535338; D13's five spanned 0.017527829..0.017528033
    "PD_patched_improvement_pct_band": (16.0, 16.7),   # D1 measured 16.310321 % against CD_feasible
    "PG_CL_residual_max": 1.0e-4,
    "PJ_tb_min_failing": 4,
    "PI_core_min_band": (11.0, 58.0),
    "P_mesh_wall_s_max": 120.0,
}
# (B) R-RC, Sanaa 2026-08-27 section 0: the rc VALUE is physics, the rc RECORD is
# infrastructure.  `rc_value` stays on the physics side; `rc_record` (the ledger row
# `inspect(exit,oomkilled)` field and the `<ARM>_<stamp>.inspect.txt` fallback) moves
# to the infrastructure side, where an absence reads NOT MEASURED -- but ONLY when
# C2-C5 all hold, which is checked per arm and printed clause by clause.
FIELDS_PHYSICS = ("rc_value", "oomkilled", "terminal_statement", "age_guard",
                  "no_fatal_token", "core_min", "cap_core_min", "DIGEST", "cpuset")
FIELDS_INFRASTRUCTURE = ("rc_record", "memavail_pre_GiB", "memavail_post_GiB", "delivered",
                         "siblings_pre", "siblings_post", "log", "wall_s")
NOT_MEASURED = "NOT_MEASURED"
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
EXPECTED_UNITS = 49


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
    """(C) C5.  Returns the tokens found.  Any hit REFUSES regardless of rc, so the
    R-RC relaxation in (B) can never launder a crash into a NOT MEASURED."""
    return [t for t in FATAL_TOKENS if t in text]


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
        hay = text + (open(art, errors="replace").read() if kind == "SCRIPT" else "")
        hits = fatal_tokens_in(hay)
        if hits:
            refuse("G1", {"C5_fatal_token_in_arm_output": hits, "arm": arm, "log": logname,
                          "note": "a fatal token refuses at ANY rc; R-RC never launders a crash"})
        cl["C5_no_fatal_token"] = {"verdict": "PASS", "tokens_searched": list(FATAL_TOKENS)}

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


# In SO-1b BOTH readers above read the SAME artefact: `so1b_E.json` carries the
# adjoint AND the central-difference table, because both are measured at the SAME
# FINAL DESIGN POINT in one arm (DAFOAM_CHARTER.md section 9).  The two functions
# stay separate so SO-1a's proven parsing is inherited unchanged rather than merged.
read_endpoint_adjoint = read_X
read_endpoint_fd = read_F


def read_O(path):
    """The optimisation artefact.  This reader NEVER decides convergence."""
    j = json.load(open(path))
    if j.get("max_iter_registered") != MAX_ITER_REGISTERED:
        refuse("G-ITER", {"max_iter_in_artefact": j.get("max_iter_registered"),
                          "registered": MAX_ITER_REGISTERED,
                          "note": "the iteration bound is frozen at the pre-registration commit"})
    if j.get("optimizer") != OPTIMIZER_REGISTERED:
        refuse("G-OPT", {"optimizer_in_artefact": j.get("optimizer"),
                         "registered": OPTIMIZER_REGISTERED})
    ip = j.get("ipopt") or {}
    return {"raw": j, "ipopt": ip,
            "exit_line": ip.get("exit_line"), "majors": ip.get("majors"),
            "CD_cold": float(j["CD_cold"]), "CL_cold": float(j["CL_cold"]),
            "CD_trimmed": float(j["CD_trimmed"]), "CL_trimmed": float(j["CL_trimmed"]),
            "CD_opt": float(j["CD_opt"]), "CL_opt": float(j["CL_opt"]),
            "shape_opt": [float(v) for v in j["shape_opt"]],
            "patchV_opt": [float(v) for v in j["patchV_opt"]],
            "patchV_trimmed": [float(v) for v in j["patchV_trimmed"]],
            "cons_opt": j.get("cons_opt") or {},
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5")}


def read_ipopt_independently(adir):
    """DAFOAM_CHARTER.md section 9's channel-independence rule, instrumented.

    The instrument reports IPOPT's EXIT line; this function re-reads
    `opt_IPOPT.txt` from disk WITHOUT going through the instrument.  Two channels
    that disagree mean the artefact is not a reading of the run, and that REFUSES.
    An ABSENT opt_IPOPT.txt is reported as absent -- never defaulted to converged.
    """
    path = os.path.join(adir, "opt_IPOPT.txt")
    out = {"path": path, "present": os.path.exists(path), "exit_line": None, "majors": None}
    if not out["present"]:
        return out
    txt = open(path, errors="replace").read()
    ex = re.findall(r"^(EXIT:.*)$", txt, re.M)
    it = re.findall(r"^Number of Iterations\.*:\s*(\d+)\s*$", txt, re.M)
    if ex:
        out["exit_line"] = ex[-1].strip()
    if it:
        out["majors"] = int(it[-1])
    return out


def g_optimiser(O, indep, arm):
    """G-OPT -- DAFOAM_CHARTER.md section 9, applied literally.

    "An optimisation run is graded PASS only if the optimiser itself printed a
    convergence statement against its own tolerance.  A run stopped by a wall
    clock, an iteration cap or a budget is GATE REACHED where a registered
    intermediate threshold was met and NOT A RESULT otherwise -- never PASS, and
    never described by the size of the improvement it reached."

    This function returns one of PASS / GATE REACHED / NOT A RESULT and never
    looks at the improvement.
    """
    out = {"arm": arm, "exit_line_instrument": O["exit_line"],
           "exit_line_independent": indep["exit_line"],
           "majors": O["majors"], "majors_independent": indep["majors"],
           "max_iter_registered": MAX_ITER_REGISTERED,
           "opt_IPOPT_present": indep["present"]}
    # channel disagreement is a REFUSAL, not a verdict
    if indep["present"] and indep["exit_line"] != O["exit_line"]:
        refuse("G-OPT", {"channel_disagreement": True, "instrument": O["exit_line"],
                         "independent": indep["exit_line"], "arm": arm})
    if indep["present"] and indep["majors"] != O["majors"]:
        refuse("G-OPT", {"majors_disagreement": True, "instrument": O["majors"],
                         "independent": indep["majors"], "arm": arm})
    if not indep["present"]:
        out["verdict"] = "NOT A RESULT"
        out["why"] = ("opt_IPOPT.txt is absent: the optimiser printed no statement this "
                      "grader can read, and section 9 forbids using the word converged of "
                      "such a run")
        return out
    conv = (O["exit_line"] == IPOPT_CONVERGED_LINE)
    hit_bound = (O["majors"] is not None and O["majors"] >= MAX_ITER_REGISTERED)
    out["converged_statement_present"] = conv
    out["hit_iteration_bound"] = hit_bound
    if conv and not hit_bound:
        out["verdict"] = "PASS"
        out["why"] = "the optimiser printed its own convergence statement inside the registered bound"
        return out
    # the registered intermediate threshold -- registered BEFORE compute, section 9
    cl_res = abs(O["CL_opt"] - CL_TARGET)
    below = (O["CD_opt"] < O["CD_trimmed"]) if GATE_REACHED_REQUIRES_CD_BELOW_REFERENCE else True
    out["intermediate_threshold"] = {"CL_residual": cl_res,
                                     "CL_residual_max": GATE_REACHED_CL_RESIDUAL_MAX,
                                     "CD_below_trimmed_reference": below}
    if cl_res <= GATE_REACHED_CL_RESIDUAL_MAX and below:
        out["verdict"] = "GATE REACHED"
        out["why"] = ("stopped without a convergence statement, but the REGISTERED "
                      "intermediate threshold held; never PASS and never described by the "
                      "size of the improvement (section 9)")
    else:
        out["verdict"] = "NOT A RESULT"
        out["why"] = ("stopped without a convergence statement and the registered "
                      "intermediate threshold did not hold")
    return out


def g_cl(E, arm):
    """G-CL -- THE POST-OPTIMUM CONSTRAINT CHECK.

    The re-solve at the optimum must put CL back on target within the registered
    tolerance.  A drag reduction bought by quietly shedding lift is not a result,
    so a failure here is NOT A RESULT whatever the drag did.
    """
    cl = float(E["raw"]["CL_baseline"])
    res = abs(cl - CL_TARGET)
    ok = res <= CL_RESIDUAL_MAX
    return {"arm": arm, "CL_at_re_solve": cl, "CL_target": CL_TARGET,
            "residual": res, "residual_max": CL_RESIDUAL_MAX,
            "verdict": "PASS" if ok else "NOT A RESULT",
            "why": ("the equality constraint is satisfied at the re-solve" if ok else
                    "the optimum does not hold the lift the constraint exists to hold; "
                    "the drag figure is not a result whatever it says")}


def g_geo(E, arm):
    """G-GEO -- the 23 geometric constraint rows at the optimum, by their own bounds."""
    cons = (E["raw"].get("cons_at_optimum") or {})
    rows, bad, n = [], [], 0
    for key, (lo, hi, cnt) in GEO_BOUNDS.items():
        vals = cons.get(key)
        if not isinstance(vals, list):
            return {"arm": arm, "verdict": "NOT A RESULT", "rows_seen": n,
                    "why": "constraint family %s absent or unreadable at the optimum" % key,
                    "raw": cons}
        if len(vals) != cnt:
            return {"arm": arm, "verdict": "NOT A RESULT", "rows_seen": n,
                    "why": "constraint family %s has %d rows, %d registered" % (key, len(vals), cnt)}
        for i, v in enumerate(vals):
            x = float(v)
            n += 1
            ok = (x >= lo - GEO_SLACK) and (hi is None or x <= hi + GEO_SLACK)
            rows.append({"family": key, "i": i, "value": x, "lower": lo, "upper": hi, "in_bound": ok})
            if not ok:
                bad.append(rows[-1])
    return {"arm": arm, "rows": rows, "rows_seen": n, "rows_expected": GEO_ROWS_EXPECTED,
            "rows_out_of_bound": bad,
            "verdict": ("PASS" if (not bad and n == GEO_ROWS_EXPECTED) else "GATE FAIL"),
            "slack": GEO_SLACK}


def g_d7r(adir, O, arm):
    """G-D7R -- THE ATTRIBUTION GATE.  A GATE, NOT A CAVEAT.

    Sanaa's directives 2026-08-27T16:54Z section 4: "no improvement % quoted before
    its mechanism is decomposed (shape vs AoA vs operating point)".  Operationally:
    unless the decomposition artefact exists and is complete, this grader emits
    D7R_SUPPRESSED in place of EVERY improvement percentage and the row is
    NOT A RESULT.  The percentage is never a gate input either way -- section 9
    forbids grading an optimisation by the size of its improvement.
    """
    path = os.path.join(adir, ATTRIBUTION_FILE)
    out = {"arm": arm, "path": path, "present": os.path.exists(path)}
    if not out["present"]:
        out["verdict"] = "NOT A RESULT"
        out["improvement_percent_vs_reference"] = D7R_SUPPRESSED
        out["improvement_percent_vs_cold"] = D7R_SUPPRESSED
        out["why"] = "the attribution artefact is absent; no percentage is reported"
        return out
    A = json.load(open(path))
    pts = A.get("points") or {}
    missing = [k for k in ATTRIBUTION_POINTS_REQUIRED if k not in pts]
    bad = []
    for k in ATTRIBUTION_POINTS_REQUIRED:
        r = pts.get(k) or {}
        for f in ("CD", "CL"):
            try:
                x = float(r[f])
            except Exception:                                     # noqa: BLE001
                bad.append("%s.%s" % (k, f)); continue
            if not (x == x and abs(x) != float("inf")):
                bad.append("%s.%s_nonfinite" % (k, f))
    op = A.get("operating_point_channel") or {}
    op_moved = bool(op.get("moved"))
    out.update({"points_missing": missing, "points_bad": bad,
                "operating_point_moved": op_moved,
                "operating_point": op,
                "naive_one_factor": A.get("naive_one_factor"),
                "matched_lift": A.get("matched_lift"),
                "trim_channel": A.get("trim_channel"),
                "reference": A.get("reference")})
    if missing or bad or op_moved:
        out["verdict"] = "NOT A RESULT"
        out["improvement_percent_vs_reference"] = D7R_SUPPRESSED
        out["improvement_percent_vs_cold"] = D7R_SUPPRESSED
        out["why"] = ("the decomposition is incomplete" if (missing or bad) else
                      "the operating point MOVED, which this registration asserts it cannot; "
                      "the third D7R channel is not identically zero and the item's own "
                      "assumption is falsified")
        return out
    out["verdict"] = "PASS"
    out["improvement_percent_vs_reference"] = A.get("improvement_percent_vs_reference")
    out["improvement_percent_vs_cold"] = A.get("improvement_percent_vs_cold")
    # the ONE reading D7R exists to force into the same sentence as the percentage
    try:
        nf = A["naive_one_factor"]
        d_aoa, d_shape = abs(float(nf["dCD_aoa"])), abs(float(nf["dCD_shape"]))
        out["aoa_channel_larger_than_shape_channel"] = bool(d_aoa >= d_shape)
        out["dCL_aoa"] = float(nf["dCL_aoa"])
        out["dCL_shape"] = float(nf["dCL_shape"])
        out["mechanism_sentence"] = (
            "naive one-factor channels: dCD_aoa=%r (dCL_aoa=%r), dCD_shape=%r (dCL_shape=%r), "
            "interaction=%r.  At MATCHED LIFT the angle of attack is a DEPENDENT variable, so "
            "the matched-lift decomposition has one flow channel (shape) plus the trim; the "
            "naive AoA channel sheds the lift the constraint exists to hold and is reported "
            "to show why it is not an attribution."
            % (nf["dCD_aoa"], nf["dCL_aoa"], nf["dCD_shape"], nf["dCL_shape"], nf["dCD_interaction"]))
    except Exception as exc:                                      # noqa: BLE001
        out["mechanism_sentence"] = "UNREADABLE %r" % (exc,)
    # feasibility cross-check: C' (optimum shape re-trimmed) should coincide with D
    try:
        dcp = A["matched_lift"].get("feasibility_check_Cprime_vs_D")
        out["Cprime_vs_D_dCD"] = (None if dcp is None else float(dcp))
        out["Cprime_vs_D_within_tolerance"] = (
            None if dcp is None else bool(abs(float(dcp)) <= CPRIME_VS_D_CD_MAX))
    except Exception:                                             # noqa: BLE001
        out["Cprime_vs_D_dCD"] = None
    return out


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
    cdir = os.path.join(base, "grader_controls")
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
    # ---- MESH identity (P1): a different mesh is a different item
    cm_txt = open(os.path.join(root, "MESH", "checkMesh.log"), errors="replace").read()
    m = re.search(r"^\s*cells:\s+(\d+)", cm_txt, re.M)
    if not m:
        refuse("G-M2", {"cells_absent_in_checkMesh": True})
    cells = int(m.group(1))
    gm2 = "PASS" if cells == CELLS_EXPECTED else "GATE FAIL"

    O, E, Efd, gopt, gcl, ggeo, gd7r, gtb, g5cd, g5cl = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
    for rk in ("P", "S"):
        oarm, earm = O_OF_ROW[rk], E_OF_ROW[rk]
        odir, edir = os.path.join(root, oarm), os.path.join(root, earm)
        O[rk] = read_O(os.path.join(odir, "so1b_O.json"))
        indep = read_ipopt_independently(odir)
        gopt[rk] = g_optimiser(O[rk], indep, oarm)
        E[rk] = read_endpoint_adjoint(os.path.join(edir, "so1b_E.json"))
        Efd[rk] = read_endpoint_fd(os.path.join(edir, "so1b_E.json"))
        rows[oarm]["artefact_so_md5"] = O[rk]["so_md5"]
        rows[earm]["artefact_so_md5"] = E[rk]["so_md5"]
        # G-ROWX AT THE GRADER: the O artefact and the E artefact of one row must have
        # been produced by the SAME library.  The instrument checks this too; a row is
        # an image hash, and a second reading of it costs nothing.
        if O[rk]["so_md5"] != E[rk]["so_md5"] or O[rk]["so_md5"] != SO_MD5[ARM_ROW[oarm]]:
            refuse("G-ROWX", {"row": rk, "O_so_md5": O[rk]["so_md5"], "E_so_md5": E[rk]["so_md5"],
                              "registered": SO_MD5[ARM_ROW[oarm]]})
        gcl[rk] = g_cl(Efd[rk], earm)
        ggeo[rk] = g_geo(Efd[rk], earm)
        gd7r[rk] = g_d7r(edir, O[rk], earm)
        # the FINAL-DESIGN-POINT FD gate (DAFOAM_CHARTER.md section 9), on the SAME
        # five components SO-1a registered at the BASELINE
        g5cd[rk] = grade_components(E[rk], Efd[rk], "CD")
        g5cl[rk] = grade_components(E[rk], Efd[rk], "CL")
        gtb[rk] = grade_tb(E[rk], Efd[rk], "CD")

    controls = {"P": ctrl_control(Efd["P"]), "S": ctrl_control(Efd["S"]),
                "grader_plant_P": grader_plant_control(root, os.path.join(root, "E-P", "so1b_E.json"), "P"),
                "grader_plant_S": grader_plant_control(root, os.path.join(root, "E-S", "so1b_E.json"), "S")}

    # ---- ROW COMPOSITION, registered here -------------------------------------------
    # A row is PASS only when the optimiser's own statement says converged AND the
    # endpoint gradient stands AND the constraint is held at the re-solve AND the
    # mechanism is decomposed.  G-OPT can only ever lower the row.
    row_verdict = {}
    for rk in ("P", "S"):
        fd_row = compose_row(g5cd[rk], g5cl[rk], gtb[rk])       # SO-1a's composition, inherited
        parts = [fd_row, gcl[rk]["verdict"], gd7r[rk]["verdict"], gopt[rk]["verdict"], ggeo[rk]["verdict"]]
        if "NOT A RESULT" in parts:
            v = "NOT A RESULT"
        elif "GATE FAIL" in parts:
            v = "GATE FAIL"
        elif "GATE REACHED" in parts:
            v = "GATE REACHED"
        else:
            v = "PASS"
        row_verdict[rk] = v

    # ---- divergence shipped vs patched, at the OPTIMUM: reported, never gated -------
    div = []
    for dv, idx in COMPONENTS_REGISTERED:
        a_, b_ = E["S"]["adjoint"]["CD"][dv], E["P"]["adjoint"]["CD"][dv]
        if idx < len(a_) and idx < len(b_):
            den = max(abs(a_[idx]), abs(b_[idx]), 1e-300)
            div.append({"dv": dv, "idx": idx, "J_shipped": a_[idx], "J_patched": b_[idx],
                        "divergence_pct": abs(a_[idx] - b_[idx]) / den * 100.0})
    g9, g10, g12 = g_toolchain(rows), g_caps(rows), g_placement(rows)

    # ---- PREDICTIONS, scored mechanically, never adjusted ---------------------------
    P = O["P"]
    preds = {"PA_cells_4032": "HIT" if gm2 == "PASS" else "MISS"}
    preds["PB_CD_trimmed_in_D1_band"] = ("HIT" if PRED["PB_CD_trimmed_band"][0] <= P["CD_trimmed"] <= PRED["PB_CD_trimmed_band"][1] else "MISS")
    preds["PB_CL_trimmed_on_target"] = ("HIT" if abs(P["CL_trimmed"] - CL_TARGET) <= PRED["PB_CL_trimmed_max_residual"] else "MISS")
    preds["PC_patched_optimiser_converged_in_band"] = (
        "HIT" if (gopt["P"]["verdict"] == "PASS" and P["majors"] is not None
                  and PRED["PC_patched_majors_band"][0] <= P["majors"] <= PRED["PC_patched_majors_band"][1]) else "MISS")
    preds["PD_patched_CD_opt_reproduces_D1"] = (
        "HIT" if PRED["PD_patched_CD_opt_band"][0] <= P["CD_opt"] <= PRED["PD_patched_CD_opt_band"][1] else "MISS")
    imp = gd7r["P"].get("improvement_percent_vs_reference")
    if isinstance(imp, str) and imp.startswith("SUPPRESSED"):
        preds["PD_patched_improvement_reproduces_D1"] = NOT_MEASURED
    else:
        try:
            iv = float(imp)
            preds["PD_patched_improvement_reproduces_D1"] = (
                "HIT" if PRED["PD_patched_improvement_pct_band"][0] <= iv <= PRED["PD_patched_improvement_pct_band"][1] else "MISS")
        except Exception:                                          # noqa: BLE001
            preds["PD_patched_improvement_reproduces_D1"] = NOT_MEASURED
    # PE: the endpoint FD disagreement at shape[6] on the SHIPPED row DIFFERS from the
    # BASELINE reading SO-1a measures.  DAFOAM_CHARTER.md section 9's own argument:
    # IDWarp's defect has two regimes on opposite sides of its axisMag guard, and a
    # gradient verified at iteration 0 is not verified at the optimum.  Scored here as
    # a NUMBER; the comparison against SO-1a's baseline reading is made in the record.
    s6 = [c for c in g5cd["S"]["components"] if c["dv"] == "shape" and c["idx"] == 6]
    preds["PE_shipped_shape6_endpoint_rel_err_pct"] = (s6[0].get("rel_err_pct") if s6 else NOT_MEASURED)
    preds["PE_shipped_shape6_endpoint_verdict"] = (s6[0].get("verdict") if s6 else NOT_MEASURED)
    # PF: the SHIPPED optimum is not better than the PATCHED one
    preds["PF_shipped_CD_opt_not_below_patched"] = (
        "HIT" if O["S"]["CD_opt"] >= O["P"]["CD_opt"] else "MISS")
    preds["PF_shipped_CD_opt"] = O["S"]["CD_opt"]
    preds["PF_patched_CD_opt"] = O["P"]["CD_opt"]
    preds["PG_CL_held_at_re_solve_both_rows"] = (
        "HIT" if all(gcl[rk]["verdict"] == "PASS" for rk in ("P", "S")) else "MISS")
    # PH: the naive AoA channel is LARGER than the naive shape channel -- predicted
    # HIT, and the reason the matched-lift decomposition exists
    preds["PH_naive_aoa_channel_larger_than_shape_on_PATCHED"] = (
        NOT_MEASURED if gd7r["P"]["verdict"] != "PASS" else
        ("HIT" if gd7r["P"].get("aoa_channel_larger_than_shape_channel") else "MISS"))
    n_tb_fail = len(COMPONENTS_REGISTERED) - gtb["P"]["n_passing_band_D_at_the_WRONG_step"]
    preds["PJ_trivial_baseline_fails_ge4_of_5_on_PATCHED"] = "HIT" if n_tb_fail >= PRED["PJ_tb_min_failing"] else "MISS"
    solver_arms = [a_ for a_ in ARMS_REQUIRED if ARM_KIND[a_] == "SOLVER"]
    dres = g1["datum_resolution"]
    preds["PK_age_datum_resolves_to_the_COMPRESSED_twin_on_every_solver_arm"] = (
        "HIT" if all(dres[a_]["is_compressed_twin"] for a_ in solver_arms) else "MISS")
    tot = g10["total_core_min"]
    preds["PI_total_core_min_band"] = (NOT_MEASURED if g10["not_measured"] else
        ("HIT" if PRED["PI_core_min_band"][0] <= tot <= PRED["PI_core_min_band"][1] else "MISS"))
    mw = rows["MESH"].get("wall_s")
    preds["P_mesh_wall_le_120s"] = NOT_MEASURED if mw is None else ("HIT" if mw <= PRED["P_mesh_wall_s_max"] else "MISS")

    # ---- ITEM VERDICT, composition registered here ----------------------------------
    vs = (row_verdict["P"], row_verdict["S"])
    if "NOT A RESULT" in vs:
        verdict = "NOT A RESULT"
    elif "GATE FAIL" in vs or "GATE FAIL" in (gm2, g9["verdict"], g10["verdict"], g12["verdict"]):
        verdict = "GATE FAIL"
    elif "GATE REACHED" in vs:
        verdict = "GATE REACHED"
    else:
        verdict = "PASS"
    if verdict not in VOCAB:
        refuse("VOCAB", {"verdict": verdict})

    return {"item": "CURRICULUM-%s" % ITEM, "verdict": verdict,
            "rows": {"PATCHED": row_verdict["P"], "SHIPPED": row_verdict["S"]},
            "gates": {
                "G1_completion": "PASS",
                "G-M2_mesh_identity": gm2,
                "G-OPT_PATCHED": gopt["P"], "G-OPT_SHIPPED": gopt["S"],
                "G-CL_PATCHED": gcl["P"], "G-CL_SHIPPED": gcl["S"],
                "G-GEO_PATCHED": ggeo["P"], "G-GEO_SHIPPED": ggeo["S"],
                "G-D7R_PATCHED": gd7r["P"], "G-D7R_SHIPPED": gd7r["S"],
                "G5E_CD_PATCHED": g5cd["P"], "G5E_CL_PATCHED": g5cl["P"],
                "G5E_CD_SHIPPED": g5cd["S"], "G5E_CL_SHIPPED": g5cl["S"],
                "G_TB_PATCHED": gtb["P"], "G_TB_SHIPPED": gtb["S"],
                "G6_dot_product_duality": ("NOT MEASURED -- the tutorial exposes no dot-product/duality "
                                           "test and AV-2 measured forward-AD seeding FAILING the primal "
                                           "on this exact case on BOTH images; named, never composed"),
                "G9_toolchain": g9, "G10_caps": g10, "G12_placement": g12},
            "optimum": {rk: {"CD_cold": O[rk]["CD_cold"], "CL_cold": O[rk]["CL_cold"],
                             "CD_trimmed": O[rk]["CD_trimmed"], "CL_trimmed": O[rk]["CL_trimmed"],
                             "CD_opt": O[rk]["CD_opt"], "CL_opt": O[rk]["CL_opt"],
                             "aoa_trimmed_deg": O[rk]["patchV_trimmed"][1],
                             "aoa_opt_deg": O[rk]["patchV_opt"][1],
                             "shape_opt": O[rk]["shape_opt"],
                             "majors": O[rk]["majors"], "exit_line": O[rk]["exit_line"]}
                        for rk in ("P", "S")},
            "improvement": {rk: {"vs_reference_pct": gd7r[rk].get("improvement_percent_vs_reference"),
                                 "vs_cold_pct": gd7r[rk].get("improvement_percent_vs_cold"),
                                 "mechanism": gd7r[rk].get("mechanism_sentence"),
                                 "gate": gd7r[rk]["verdict"]}
                            for rk in ("P", "S")},
            "mesh_cells": cells, "divergence_shipped_vs_patched_CD_at_optimum": div,
            "predictions": preds, "controls": controls, "completion": g1,
            "not_measured": {"G1": g1["not_measured"], "G10": g10["not_measured"], "G12": g12["not_measured"]},
            "field_classes": {"physics": list(FIELDS_PHYSICS), "infrastructure": list(FIELDS_INFRASTRUCTURE),
                              "rule": "absent infrastructure -> NOT_MEASURED beside the verdict; absent physics -> REFUSE (L-342)"},
            "no_gci": "no grid family; standing rule 5 has no row; NO GCI IS QUOTED",
            "age_datum_resolution": g1["datum_resolution"],
            "rule4_clauses_per_arm": g1["rule4_clauses"],
            "rc_inferences": g1["rc_inferences"],
            "section_9_note": ("DAFOAM_CHARTER.md section 9: no row is PASS without the optimiser's own "
                               "convergence statement; no verdict here is derived from the size of an "
                               "improvement; and every row carries a finite-difference check of the "
                               "gradient AT ITS FINAL DESIGN POINT."),
            "capability_grid_cell": ("2D . steady . incompressible -- OPTIMIZATION CONVERGED.  This item "
                                     "moves that column, on TWO ROWS: D1 and D13 bought the PATCHED optimum "
                                     "of this problem and D1's SHIPPED arm was BLOCKED before any solve, so "
                                     "the shipped optimum of A1 has never existed")}


# ================= selftest: planted fixtures, counted against a FROZEN unit count ======
ROWFMT = ("ARM={arm} ROW={row} IMG={img} DIGEST={dig} rc={rc} wall_s={wall} ranks={ranks} core_min={cm} "
          "cap_core_min={cap} enforced_wall_s=600 enforced_core_min={cap} memory=4g inspect(exit,oomkilled)=[{ke} {oom}] "
          "memavail_pre_GiB=20.00 memavail_post_GiB={mpost} cpuset={cs} delivered_cores_mean=[{dl}] "
          "siblings_pre=[] siblings_post=[] log={log} stamp=x\n")


def _fix(tmp, tweak=None):
    """Build a clean SO-1b fixture; `tweak` mutates the dict of knobs before writing.

    ONE KNOB PER GUARD.  Every guard this comparator carries is DRIVEN to fire on a
    planted fixture and then shown NOT to fire on the clean one -- a guard that has
    never been seen to fail is not known to work (standing rule 3; L-314).  The knobs
    SO-1a registered are inherited unchanged; the NEW ones are:
      `ipopt`      per row: "optimal" | "maxiter" | "none"  -- (F) G-OPT / section 9
      `majors`     per row -- the iteration bound
      `no_optfile` set of rows whose opt_IPOPT.txt is absent
      `disagree`   per row: "exit" | "majors" -- the two-channel refusal
      `bad_maxiter`/`bad_optimizer` sets of rows -- G-ITER / G-OPT artefact drift
      `cl_opt`     per row: the CL at the RE-SOLVE -- (G) G-CL, the constraint check
      `geo`        per row: "ok" | "out" | "absent" | "short" -- (H) G-GEO
      `attr`       per row: "ok" | "absent" | "missing" | "opmoved" -- (I) G-D7R
    """
    k = {"rc": {a_: 0 for a_ in ARMS_REQUIRED}, "ke": {}, "oom": {a_: "false" for a_ in ARMS_REQUIRED},
         "cm": dict(PREDICTED_CORE_MIN), "cs": {a_: CPUSET_REGISTERED for a_ in ARMS_REQUIRED},
         "so": {a_: SO_MD5[ARM_ROW[a_]] for a_ in ARMS_REQUIRED}, "cells": CELLS_EXPECTED,
         "err": {"S": {}, "P": {}}, "err_cl": {"S": {}, "P": {}},
         "flip": {"S": set(), "P": set()}, "noplateau": {"S": set(), "P": set()},
         "tb_pass": {"S": set(), "P": set()},
         "terminal": {a_: True for a_ in ARMS_REQUIRED}, "stale": set(), "ctrl_ok": True,
         "mpost": "20.00", "drop_row": set(), "inspect_file": set(), "rc_record": set(), "fatal": {},
         "datum": {a_: ("plain" if a_ == "MESH" else "gz") for a_ in ARMS_REQUIRED},
         "write_compression": "on",
         "dl": "1.99 n=10 max_nr_throttled=0",
         # ---- the OPTIMISATION knobs ------------------------------------------------
         "ipopt": {"P": "optimal", "S": "optimal"},
         "majors": {"P": 11, "S": 14},
         "no_optfile": set(), "disagree": {}, "bad_maxiter": set(), "bad_optimizer": set(),
         "CD_cold": {"P": 0.020910510006792161, "S": 0.020910510006792161},
         "CL_cold": {"P": 0.499, "S": 0.499},
         "CD_trim": {"P": 0.020943920630946831, "S": 0.020943920630946831},
         "CD_opt": {"P": 0.017527899854535338, "S": 0.0189},
         "CL_opt": {"P": 0.5, "S": 0.5},
         "aoa_trim": {"P": 5.13918623195176, "S": 5.13918623195176},
         "aoa_opt": {"P": 1.13, "S": 1.30},
         "U_opt": {"P": 10.0, "S": 10.0},
         # ---- the ENDPOINT knobs ----------------------------------------------------
         "cl_resolve": {"P": 0.5, "S": 0.5},
         "geo": {"P": "ok", "S": "ok"},
         "attr": {"P": "ok", "S": "ok"},
         "CD": 0.0175279, "CL": 0.5}
    if tweak:
        tweak(k)
    root = os.path.join(tmp, "root_%d" % int(time.time() * 1e6))
    os.makedirs(root)
    led = ["ITEM=SO1b\n", "STAGED stamp=x\n"]

    def geo_block(kind):
        if kind == "absent":
            return {"geometry.volcon": [repr(1.000000017320)], "geometry.rcon": [repr(0.800000261506)] * 2}
        thick = [repr(0.500000126)] * 20
        vol = [repr(1.000000017320)]
        rc = [repr(0.800000261506)] * 2
        if kind == "out":
            thick[7] = repr(0.4)           # below the registered 0.5 floor
        if kind == "short":
            thick = thick[:19]
        return {"geometry.thickcon": thick, "geometry.volcon": vol, "geometry.rcon": rc}

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
        so = k["so"][arm]
        text = "D4S_CONTAINER_UID: 0\nD4S_IDWARP_SO_MD5: %s\nD4S_DEADLINE_IN_CONTAINER_S: 1500\n" % so
        if arm == "MESH":
            art = os.path.join(d, "checkMesh.log")
            open(art, "w").write("Mesh stats\n    cells:            %d\n\nMesh OK.\n" % k["cells"])
            text += "SO1B_CHECKMESH_RC 0\n"
        else:
            rk = "P" if arm.endswith("-P") else "S"
            art = os.path.join(d, ARTEFACT[arm])
            ident = {"libidwarp_so_md5": so, "idwarp_file": "/x/idwarp/__init__.py",
                     "write_compression": k["write_compression"]}
            J = {"shape": [-0.011, 0.02, -0.03, 0.041, 0.05, -0.06, 0.007, -0.008],
                 "patchV": [0.0, 0.0123]}
            if ARM_MODE[arm] == "O":
                exits = {"optimal": IPOPT_CONVERGED_LINE,
                         "maxiter": "EXIT: Maximum Number of Iterations Exceeded.",
                         "none": None}
                ex = exits[k["ipopt"][rk]]
                mj = k["majors"][rk]
                ip = {"ipopt_file": os.path.join(d, "opt_IPOPT.txt"), "exit_line": ex,
                      "majors": mj, "n_exit_lines": (1 if ex else 0), "readable": True}
                json.dump({"item": "SO1b", "mode": "O", "row": rk, "identity": ident, "nprocs": 1,
                           "optimizer": ("SLSQP" if rk in k["bad_optimizer"] else OPTIMIZER_REGISTERED),
                           "opt_settings": {"max_iter": MAX_ITER_REGISTERED},
                           "max_iter_registered": (99 if rk in k["bad_maxiter"] else MAX_ITER_REGISTERED),
                           "CD_cold": repr(k["CD_cold"][rk]), "CL_cold": repr(k["CL_cold"][rk]),
                           "CD_trimmed": repr(k["CD_trim"][rk]), "CL_trimmed": repr(0.5),
                           "patchV_trimmed": [repr(10.0), repr(k["aoa_trim"][rk])],
                           "CD_opt": repr(k["CD_opt"][rk]), "CL_opt": repr(k["CL_opt"][rk]),
                           "shape_opt": [repr(v) for v in J["shape"]],
                           "patchV_opt": [repr(k["U_opt"][rk]), repr(k["aoa_opt"][rk])],
                           "cons_opt": geo_block("ok"), "driver_wall_s": 300.0,
                           "ipopt": ip}, open(art, "w"))
                if rk not in k["no_optfile"]:
                    dis = k["disagree"].get(rk)
                    fex = ("EXIT: Restoration Failed." if dis == "exit" else ex)
                    fmj = (mj + 5 if dis == "majors" else mj)
                    body = ""
                    if fex:
                        body += "%s\n" % fex
                    body += "Number of Iterations....: %d\n" % fmj
                    open(os.path.join(d, "opt_IPOPT.txt"), "w").write(body)
            else:
                rows_ = []
                for dv, idx in COMPONENTS_REGISTERED:
                    j = J[dv][idx]
                    e = k["err"][rk].get((dv, idx), 0.5)
                    ecl = k["err_cl"][rk].get((dv, idx), 0.5)
                    dref = j * (1.0 + e / 100.0)
                    dref_cl = j * 10.0 * (1.0 + ecl / 100.0)
                    if (dv, idx) in k["flip"][rk]:
                        dref = -dref
                    fd = {}
                    for st in STEPS_REGISTERED[dv]:
                        scale = 1.0 if st == sorted(STEPS_REGISTERED[dv])[1] else 1.01
                        if (dv, idx) in k["noplateau"][rk]:
                            scale = 1.0 if st == sorted(STEPS_REGISTERED[dv])[1] else 1.5
                        fd[repr(st)] = {"step": st, "ok": True, "dCD": repr(dref * scale),
                                        "dCL": repr(dref_cl * scale), "CD_plus": repr(0.0),
                                        "CD_minus": repr(0.0), "CL_plus": repr(0.0), "CL_minus": repr(0.0)}
                    tbs = TB_STEPS_REGISTERED[dv][0]
                    tbmul = 1.001 if (dv, idx) in k["tb_pass"][rk] else 3.0
                    tb = {repr(tbs): {"step": tbs, "ok": True, "dCD": repr(j * tbmul),
                                      "dCL": repr(j * 10.0 * tbmul), "CD_plus": repr(0.0),
                                      "CD_minus": repr(0.0), "CL_plus": repr(0.0), "CL_minus": repr(0.0)}}
                    rows_.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd, "tb": tb})
                planted = PLANT / (2.0 * CTRL_STEP) if k["ctrl_ok"] else 0.0
                rows_.append({"dv": "CTRL", "idx": 0, "status": "CONTROL",
                              "fd": {repr(CTRL_STEP): {"step": CTRL_STEP, "ok": True,
                                                       "dCD": repr(0.0), "dCL": repr(0.0)}},
                              "planted": {"step": CTRL_STEP, "plant": PLANT, "dCD": repr(planted), "ok": True}})
                adj = {"CD": {dv: [repr(v) for v in J[dv]] for dv in J},
                       "CL": {dv: [repr(v * 10.0) for v in J[dv]] for dv in J}}
                json.dump({"item": "SO1b", "mode": "E", "row": rk, "identity": ident, "nprocs": 1,
                           "components_requested": COMPONENTS_REGISTERED,
                           "steps": STEPS_REGISTERED, "tb_steps": TB_STEPS_REGISTERED,
                           "CD_baseline": repr(k["CD"]), "CL_baseline": repr(k["cl_resolve"][rk]),
                           "eta_used": repr(1e-9), "CL_target": repr(CL_TARGET),
                           "cons_at_optimum": geo_block(k["geo"][rk]),
                           "adjoint": adj, "rows": rows_}, open(art, "w"))
                # ---- the D7R attribution artefact -------------------------------
                mode = k["attr"][rk]
                if mode != "absent":
                    cdA0, cdA = k["CD_cold"][rk], k["CD_trim"][rk]
                    cdD = k["CD_opt"][rk]
                    cdB, cdC = 0.0091, 0.0242         # AoA alone drops drag AND sheds lift; shape alone raises both
                    pts = {"A0": {"CD": repr(cdA0), "CL": repr(0.499)},
                           "A": {"CD": repr(cdA), "CL": repr(0.5)},
                           "B": {"CD": repr(cdB), "CL": repr(0.11)},
                           "C": {"CD": repr(cdC), "CL": repr(0.83)},
                           "D": {"CD": repr(cdD), "CL": repr(k["cl_resolve"][rk])}}
                    if mode == "missing":
                        pts.pop("B")
                    nf = {"dCD_total": repr(cdD - cdA), "dCD_aoa": repr(cdB - cdA),
                          "dCD_shape": repr(cdC - cdA),
                          "dCD_interaction": repr((cdD - cdA) - (cdB - cdA) - (cdC - cdA)),
                          "dCL_aoa": repr(0.11 - 0.5), "dCL_shape": repr(0.83 - 0.5),
                          "dCL_total": repr(0.0)}
                    json.dump({"item": "SO1b", "row": rk, "points": pts, "naive_one_factor": nf,
                               "matched_lift": {"dCD_shape_matched": repr(cdD - cdA),
                                                "dCD_aoa_matched": repr(0.0),
                                                "feasibility_check_Cprime_vs_D": repr(1.0e-9)},
                               "trim_channel": {"dCD_trim": repr(cdA - cdA0)},
                               "reference": {"name": "A_trimmed_shape0_aoaT", "CD": repr(cdA)},
                               "operating_point_channel": {"U0_registered": repr(10.0),
                                                           "U_at_optimum": repr(10.5 if mode == "opmoved" else 10.0),
                                                           "moved": (mode == "opmoved"),
                                                           "dCD_operating_point": repr(0.0)},
                               "improvement_percent_vs_reference": repr(-100.0 * (cdD - cdA) / cdA),
                               "improvement_percent_vs_cold": repr(-100.0 * (cdD - cdA0) / cdA0)},
                              open(os.path.join(d, ATTRIBUTION_FILE), "w"))
            if k["terminal"][arm]:
                text += TERMINAL[arm] + " ok\n"
        if arm in k["fatal"]:
            text += k["fatal"][arm] + "\n"
        os.utime(art, (t0 - 5, t0 - 5) if arm in k["stale"] else (t0 + 5, t0 + 5))
        open(os.path.join(root, log), "w").write(text)
        ke = NOT_MEASURED if arm in k["rc_record"] else k["ke"].get(arm, k["rc"][arm])
        if arm in k["inspect_file"]:
            open(os.path.join(root, "%s_x.inspect.txt" % arm), "w").write(
                "%s %s 2026-08-27T00:00:00Z 2026-08-27T00:01:00Z %s 4294967296 %s\n"
                % (ke, k["oom"][arm], k["cs"][arm], IMG_DIGEST[ARM_ROW[arm]]))
        if arm in k["drop_row"]:
            continue
        led.append(ROWFMT.format(arm=arm, row=ARM_ROW[arm], img="img", dig=IMG_DIGEST[ARM_ROW[arm]],
                                 rc=k["rc"][arm], wall=60, ranks=ARM_RANKS[arm], cm=k["cm"][arm],
                                 cap=CAPS[arm], ke=ke, oom=k["oom"][arm], mpost=k["mpost"],
                                 cs=k["cs"][arm], dl=k["dl"], log=log))
    open(os.path.join(root, "ledger.txt"), "w").write("".join(led))
    return root


def selftest(tmp):
    """PLANTED-FAILURE PROOF, every guard driven to fire and then shown not to.

    A unit that asserts a string built from the same constant it checks is weak,
    not evidence, so every unit below plants a CONDITION into the fixture and reads
    the verdict back through the SAME code path a real run uses.  The count is
    frozen at EXPECTED_UNITS and checked in main(): a deleted unit is a failure.
    """
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

    # ================= the clean fixture, and what it must say ====================
    r = grade(_fix(tmp))
    unit("U1 clean fixture -> item PASS; both rows PASS; G-M2/G9/G10/G12 PASS",
         r["verdict"] == "PASS" and r["rows"] == {"PATCHED": "PASS", "SHIPPED": "PASS"}
         and r["gates"]["G-M2_mesh_identity"] == "PASS"
         and r["gates"]["G9_toolchain"]["verdict"] == "PASS"
         and r["gates"]["G10_caps"]["verdict"] == "PASS"
         and r["gates"]["G12_placement"]["verdict"] == "PASS")
    unit("U2 clean fixture -> G-OPT PASS on both rows with the optimiser's OWN statement",
         r["gates"]["G-OPT_PATCHED"]["verdict"] == "PASS"
         and r["gates"]["G-OPT_SHIPPED"]["verdict"] == "PASS"
         and r["gates"]["G-OPT_PATCHED"]["exit_line_instrument"] == IPOPT_CONVERGED_LINE)
    unit("U3 clean fixture -> G-CL PASS, G-GEO PASS with 23 rows on both rows",
         all(r["gates"]["G-CL_%s" % w]["verdict"] == "PASS" for w in ("PATCHED", "SHIPPED"))
         and all(r["gates"]["G-GEO_%s" % w]["verdict"] == "PASS"
                 and r["gates"]["G-GEO_%s" % w]["rows_seen"] == GEO_ROWS_EXPECTED
                 for w in ("PATCHED", "SHIPPED")))
    unit("U4 clean fixture -> G-D7R PASS and the improvement percentage IS REPORTED "
         "(the POSITIVE control: suppression is not unconditional)",
         r["gates"]["G-D7R_PATCHED"]["verdict"] == "PASS"
         and not str(r["improvement"]["P"]["vs_reference_pct"]).startswith("SUPPRESSED")
         and float(r["improvement"]["P"]["vs_reference_pct"]) > 0.0)
    unit("U5 clean fixture -> the predictions anchored on D1/D13 measured values HIT",
         all(r["predictions"][k] == "HIT" for k in (
             "PA_cells_4032", "PB_CD_trimmed_in_D1_band", "PB_CL_trimmed_on_target",
             "PC_patched_optimiser_converged_in_band", "PD_patched_CD_opt_reproduces_D1",
             "PD_patched_improvement_reproduces_D1", "PG_CL_held_at_re_solve_both_rows",
             "PF_shipped_CD_opt_not_below_patched", "PJ_trivial_baseline_fails_ge4_of_5_on_PATCHED",
             "PK_age_datum_resolves_to_the_COMPRESSED_twin_on_every_solver_arm",
             "PI_total_core_min_band", "P_mesh_wall_le_120s")))
    unit("U6 clean fixture -> PH HIT: the NAIVE AoA channel is larger than the naive shape "
         "channel, which is WHY the matched-lift decomposition exists",
         r["predictions"]["PH_naive_aoa_channel_larger_than_shape_on_PATCHED"] == "HIT"
         and r["gates"]["G-D7R_PATCHED"]["dCL_aoa"] < -0.3)
    unit("U7 grader-level plant SEEN on both endpoint tables (rule 3)",
         r["controls"]["grader_plant_P"]["grader_plant_seen"]
         and r["controls"]["grader_plant_S"]["grader_plant_seen"]
         and r["controls"]["P"]["instrument_ctrl_zero"] == 0.0)
    unit("U8 the five rule-4 clauses are printed INDIVIDUALLY for every arm",
         all(set(("C1_rc_value", "C2_terminal_marker", "C3_artefact_present",
                  "C4_age_guard", "C5_no_fatal_token"))
             <= set(r["rule4_clauses_per_arm"][a_]) for a_ in ARMS_REQUIRED))

    # ================= G-OPT: DAFOAM_CHARTER section 9, driven ====================
    r = grade(_fix(tmp, tw(ipopt={"P": "none"}, majors={"P": 30})))
    unit("U9 PATCHED optimiser prints NO convergence statement but the REGISTERED "
         "intermediate threshold holds -> GATE REACHED, never PASS (section 9)",
         r["gates"]["G-OPT_PATCHED"]["verdict"] == "GATE REACHED"
         and r["rows"]["PATCHED"] == "GATE REACHED" and r["verdict"] == "GATE REACHED")
    r = grade(_fix(tmp, tw(ipopt={"P": "none"}, majors={"P": 30}, CL_opt={"P": 0.62})))
    unit("U10 no convergence statement AND the intermediate threshold FAILS -> NOT A RESULT",
         r["gates"]["G-OPT_PATCHED"]["verdict"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT")
    r = grade(_fix(tmp, tw(ipopt={"P": "maxiter"}, majors={"P": 30})))
    unit("U11 optimiser stopped AT the registered iteration bound -> not PASS",
         r["gates"]["G-OPT_PATCHED"]["verdict"] != "PASS"
         and r["gates"]["G-OPT_PATCHED"]["hit_iteration_bound"] is True)
    unit("U12 opt_IPOPT.txt ABSENT -> NOT A RESULT, never a default to converged",
         grade(_fix(tmp, tw(no_optfile={"S"})))["gates"]["G-OPT_SHIPPED"]["verdict"] == "NOT A RESULT")
    unit("U13 the instrument's EXIT line disagrees with opt_IPOPT.txt -> REFUSAL",
         refused(_fix(tmp, tw(disagree={"P": "exit"}))))
    unit("U14 the instrument's major count disagrees with opt_IPOPT.txt -> REFUSAL",
         refused(_fix(tmp, tw(disagree={"S": "majors"}))))
    unit("U15 max_iter in the O artefact != the registered bound -> REFUSAL (G-ITER)",
         refused(_fix(tmp, tw(bad_maxiter={"P"}))))
    unit("U16 optimizer in the O artefact != the registered optimizer -> REFUSAL (G-OPT)",
         refused(_fix(tmp, tw(bad_optimizer={"S"}))))

    # ================= G-CL: the post-optimum constraint check ====================
    r = grade(_fix(tmp, tw(cl_resolve={"P": 0.4988})))
    unit("U17 the re-solve at the optimum sheds lift (|CL-0.5| = 1.2e-3 > 1e-4) -> "
         "G-CL NOT A RESULT and the ROW is NOT A RESULT WHATEVER THE DRAG DID",
         r["gates"]["G-CL_PATCHED"]["verdict"] == "NOT A RESULT"
         and r["rows"]["PATCHED"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT")
    r = grade(_fix(tmp, tw(cl_resolve={"P": 0.50005})))
    unit("U18 a CL residual of 5e-5 is INSIDE the registered tolerance -> G-CL PASS "
         "(the gate is shown able to pass as well as to fail)",
         r["gates"]["G-CL_PATCHED"]["verdict"] == "PASS" and r["rows"]["PATCHED"] == "PASS")

    # ================= G-GEO: the 23 geometric rows ===============================
    r = grade(_fix(tmp, tw(geo={"S": "out"})))
    unit("U19 one thickness row below its registered floor -> G-GEO GATE FAIL",
         r["gates"]["G-GEO_SHIPPED"]["verdict"] == "GATE FAIL"
         and len(r["gates"]["G-GEO_SHIPPED"]["rows_out_of_bound"]) == 1)
    unit("U20 a whole constraint family absent at the optimum -> NOT A RESULT",
         grade(_fix(tmp, tw(geo={"P": "absent"})))["gates"]["G-GEO_PATCHED"]["verdict"] == "NOT A RESULT")
    unit("U21 a constraint family with the wrong ROW COUNT -> NOT A RESULT",
         grade(_fix(tmp, tw(geo={"P": "short"})))["gates"]["G-GEO_PATCHED"]["verdict"] == "NOT A RESULT")

    # ================= G-D7R: the attribution GATE ================================
    r = grade(_fix(tmp, tw(attr={"P": "absent"})))
    unit("U22 attribution artefact ABSENT -> percentage SUPPRESSED and row NOT A RESULT",
         str(r["improvement"]["P"]["vs_reference_pct"]).startswith("SUPPRESSED")
         and str(r["improvement"]["P"]["vs_cold_pct"]).startswith("SUPPRESSED")
         and r["rows"]["PATCHED"] == "NOT A RESULT")
    r = grade(_fix(tmp, tw(attr={"S": "missing"})))
    unit("U23 attribution missing ONE of the five registered points -> SUPPRESSED, NOT A RESULT",
         str(r["improvement"]["S"]["vs_reference_pct"]).startswith("SUPPRESSED")
         and r["gates"]["G-D7R_SHIPPED"]["points_missing"] == ["B"]
         and r["rows"]["SHIPPED"] == "NOT A RESULT")
    r = grade(_fix(tmp, tw(attr={"P": "opmoved"})))
    unit("U24 the OPERATING POINT moved, which this item asserts it cannot -> SUPPRESSED, "
         "NOT A RESULT, and the falsified assumption is named",
         r["gates"]["G-D7R_PATCHED"]["operating_point_moved"] is True
         and str(r["improvement"]["P"]["vs_reference_pct"]).startswith("SUPPRESSED")
         and r["rows"]["PATCHED"] == "NOT A RESULT")

    # ================= the endpoint FD gate (section 9's mandatory check) =========
    r = grade(_fix(tmp, tw(err={"S": {("shape", 3): 7.0}})))
    unit("U25 PLANTED 7 % endpoint error on shipped shape[3] -> component GATE FAIL, "
         "SHIPPED row GATE FAIL, item GATE FAIL",
         r["rows"]["SHIPPED"] == "GATE FAIL" and r["verdict"] == "GATE FAIL"
         and r["gates"]["G5E_CD_SHIPPED"]["n_gate_fail"] == 1)
    r = grade(_fix(tmp, tw(flip={"S": {("shape", 6)}, "P": set()})))
    unit("U26 PLANTED sign flip at the OPTIMUM on shipped shape[6] -> flip counted, "
         "SHIPPED GATE FAIL, PATCHED still PASS",
         r["gates"]["G5E_CD_SHIPPED"]["sign_flips"] == 1
         and r["rows"]["SHIPPED"] == "GATE FAIL" and r["rows"]["PATCHED"] == "PASS"
         and r["predictions"]["PE_shipped_shape6_endpoint_verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(err_cl={"P": {("shape", 0): 9.0}})))
    unit("U27 the CONSTRAINT gradient fails ALONE at the optimum while the objective is "
         "clean -> the row falls on G5E_CL, which the objective could not have caught",
         r["gates"]["G5E_CL_PATCHED"]["verdict"] == "GATE FAIL"
         and r["gates"]["G5E_CD_PATCHED"]["verdict"] == "PASS"
         and r["rows"]["PATCHED"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(noplateau={"S": {("shape", 0)}, "P": set()})))
    c0 = [c for c in r["gates"]["G5E_CD_SHIPPED"]["components"] if c["idx"] == 0 and c["dv"] == "shape"][0]
    unit("U28 PLANTED no-plateau -> that component NOT A RESULT, row still PASS on 4 graded",
         c0["verdict"] == "NOT A RESULT" and c0["reason"] == "NO_PLATEAU"
         and r["rows"]["SHIPPED"] == "PASS" and r["gates"]["G5E_CD_SHIPPED"]["n_graded"] == 4)
    r = grade(_fix(tmp, tw(noplateau={"P": {("shape", 0), ("shape", 3), ("shape", 6)}, "S": set()})))
    unit("U29 three no-plateau components -> 2 graded < 3 -> row NOT A RESULT",
         r["rows"]["PATCHED"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT")
    r = grade(_fix(tmp, tw(tb_pass={"P": {("shape", 0), ("shape", 3), ("shape", 6),
                                          ("shape", 7), ("patchV", 1)}, "S": set()})))
    unit("U30 the WRONG step agrees on 5 of 5 at the optimum -> G-TB GATE FAIL and the "
         "row's endpoint verdict is WITHDRAWN to NOT A RESULT (charter section 4)",
         r["gates"]["G_TB_PATCHED"]["verdict"] == "GATE FAIL"
         and r["rows"]["PATCHED"] == "NOT A RESULT")

    # ================= G1 / rule 4 / R-RC / L-342, inherited and re-driven ========
    unit("U31 rc=1 on E-P -> REFUSAL", refused(_fix(tmp, tw(rc={"E-P": 1}, ke={"E-P": 1}))))
    unit("U32 OOMKilled=true on O-S -> REFUSAL", refused(_fix(tmp, tw(oom={"O-S": "true"}))))
    unit("U33 terminal marker absent in E-S log -> REFUSAL", refused(_fix(tmp, tw(terminal={"E-S": False}))))
    unit("U34 artefact OLDER than the age datum (O-P) -> REFUSAL (rule 4 age guard)",
         refused(_fix(tmp, tw(stale={"O-P"}))))
    unit("U35 instrument CTRL planted row broken -> REFUSAL", refused(_fix(tmp, tw(ctrl_ok=False))))
    unit("U36 FOAM FATAL ERROR in an arm log at rc=0 -> REFUSAL regardless of rc",
         refused(_fix(tmp, tw(fatal={"E-P": "FOAM FATAL ERROR"}))))
    unit("U37 a signal token in an arm log at rc=0 -> REFUSAL regardless of rc",
         refused(_fix(tmp, tw(fatal={"O-S": "Segmentation fault"}))))
    unit("U38 ledger row absent for one arm -> REFUSAL", refused(_fix(tmp, tw(drop_row={"E-S"}))))
    r = grade(_fix(tmp, tw(rc_record={"O-P"}, inspect_file=set())))
    unit("U39 R-RC: rc RECORD absent while C2-C5 all hold -> C1 NOT MEASURED, the implied "
         "rc=0 printed as an INFERENCE, the verdict unchanged",
         r["verdict"] == "PASS"
         and r["rule4_clauses_per_arm"]["O-P"]["C1_rc_value"]["verdict"] == NOT_MEASURED
         and r["rc_inferences"]["O-P"]["rc_inferred"] == 0
         and "rc_record" in r["not_measured"]["G1"]["O-P"])
    unit("U40 R-RC: rc RECORD absent AND the terminal marker missing -> REFUSAL",
         refused(_fix(tmp, tw(rc_record={"O-P"}, terminal={"O-P": False}))))
    unit("U41 R-RC: rc RECORD absent while the harness rc reads NON-ZERO -> REFUSAL "
         "(R-RC relaxes a missing record, never a positive reading of failure)",
         refused(_fix(tmp, tw(rc_record={"E-S"}, rc={"E-S": 1}))))

    # ================= the age datum by EXISTENCE (AV-1/AV-2) =====================
    r = grade(_fix(tmp, tw(datum={"O-P": "plain", "E-P": "plain", "O-S": "plain", "E-S": "plain"})))
    unit("U42 the datum resolves to the PLAIN name on every solver arm -> accepted, PK MISS",
         r["verdict"] == "PASS"
         and r["predictions"]["PK_age_datum_resolves_to_the_COMPRESSED_twin_on_every_solver_arm"] == "MISS")
    unit("U43 NEITHER 0/U nor 0/U.gz present -> REFUSAL (the only datum refusal)",
         refused(_fix(tmp, tw(datum={"E-P": "none"}))))

    # ================= G-M2 / G-ROWX / G9 / G10 / G12 =============================
    r = grade(_fix(tmp, tw(cells=4033)))
    unit("U44 a different cell count -> G-M2 GATE FAIL and PA MISS (a different mesh is a "
         "different item)", r["gates"]["G-M2_mesh_identity"] == "GATE FAIL"
         and r["predictions"]["PA_cells_4032"] == "MISS" and r["verdict"] == "GATE FAIL")
    unit("U45 G-ROWX: the E arm of a row carrying the OTHER row's library md5 -> REFUSAL",
         refused(_fix(tmp, tw(so={"E-P": SO_MD5["SHIPPED"]}))))
    r = grade(_fix(tmp, tw(cm={"O-S": 26.0})))
    unit("U46 O-S core_min 26.0 > its registered cap 25.0 -> G10 GATE FAIL",
         r["gates"]["G10_caps"]["verdict"] == "GATE FAIL"
         and r["gates"]["G10_caps"]["per_arm"]["O-S"]["crossed"])
    r = grade(_fix(tmp, tw(cs={"E-S": "4,14"})))
    unit("U47 an arm off the registered cpuset -> G12 GATE FAIL",
         r["gates"]["G12_placement"]["verdict"] == "GATE FAIL")

    # ================= the instrument's own AST, and this file's ==================
    here = os.path.dirname(os.path.abspath(__file__))
    inst = os.path.join(here, "so1b_of.py")
    n_grade = count_asserts(os.path.abspath(__file__))
    n_inst = count_asserts(inst) if os.path.exists(inst) else -1
    unit("U48 ZERO `assert` statements in this comparator AND in so1b_of.py (L-332)",
         n_grade == 0 and n_inst == 0)
    planted = os.path.join(tmp, "planted_assert.py")
    open(planted, "w").write("def f(x):\n    assert x > 0\n    return x\n")
    unit("U49 the assert COUNTER is shown counting a planted assert (a counter never seen "
         "counting is not evidence)", count_asserts(planted) == 1)

    print("\nUNITS %d/%d  FAILS %d" % (n - len(fails), n, len(fails)))
    for f in fails:
        print("  FAILED: %s" % f)
    if n != EXPECTED_UNITS:
        print("REFUSAL: unit count %d != frozen EXPECTED_UNITS %d" % (n, EXPECTED_UNITS))
        return 2
    return 0 if not fails else 2


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmpdir", default="/tmp")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if count_asserts(os.path.abspath(__file__)) != 0:
        print("REFUSAL: this comparator carries an assert statement (L-332)"); return 2
    if a.selftest:
        d = os.path.join(a.tmpdir, "so1b_selftest_%d" % os.getpid()); os.makedirs(d, exist_ok=True)
        return selftest(d)
    if not a.root:
        print("usage: so1b_grade.py --root <run root> [--out FILE] | --selftest"); return 64
    try:
        r = grade(a.root)
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
