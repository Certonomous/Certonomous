#!/usr/bin/env python3
"""Curriculum SO-1a COMPARATOR -- NACA0012 INCOMPRESSIBLE drag-min-at-fixed-lift,
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
ITEM = "SO1a"
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
FATAL_TOKENS = ("FOAM FATAL ERROR", "FOAM FATAL IO ERROR", "Segmentation fault",
                "SIGSEGV", "SIGKILL", "MPI_ABORT", "signal 9", "Signal 11",
                "Floating point exception")
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
NOT_MEASURED = "NOT_MEASURED"
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
EXPECTED_UNITS = 35


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
    # ---- MESH identity
    cm_txt = open(os.path.join(root, "MESH", "checkMesh.log"), errors="replace").read()
    m = re.search(r"^\s*cells:\s+(\d+)", cm_txt, re.M)
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
            open(art, "w").write("Mesh stats\n    cells:            %d\n\nMesh OK.\n" % k["cells"])
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
    here = os.path.dirname(os.path.abspath(__file__))
    unit("U21 ast.Assert count = 0 in so1a_grade.py and so1a_xf.py", count_asserts(os.path.abspath(__file__)) == 0 and count_asserts(os.path.join(here, "so1a_xf.py")) == 0)
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

    print("SO1a GRADER SELFTEST units=%d expected=%d failures=%d python_O=%s" % (n, EXPECTED_UNITS, len(fails), not __debug__))
    if n != EXPECTED_UNITS or fails:
        print("SELFTEST FAIL: %s" % (fails or "unit count %d != %d" % (n, EXPECTED_UNITS)))
        return 2
    print("SO1a GRADER SELFTEST PASS %d/%d (counted against the frozen EXPECTED_UNITS)" % (n, EXPECTED_UNITS))
    return 0


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
        d = os.path.join(a.tmpdir, "so1a_selftest_%d" % os.getpid()); os.makedirs(d, exist_ok=True)
        return selftest(d)
    if not a.root:
        print("usage: so1a_grade.py --root <run root> [--out FILE] | --selftest"); return 64
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
