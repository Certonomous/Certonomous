#!/usr/bin/env python3
"""Curriculum SO-1cR COMPARATOR -- NACA0012 INCOMPRESSIBLE drag-min-at-fixed-lift,
the POST-OPTIMUM VERIFICATION RUNG of Sanaa's shape-optimisation ladder SO-1
(directives 2026-08-27T16:54Z section 4, third step of the per-case pattern).

np-INVARIANCE OF THE GRADIENT **AT SO-1b's OPTIMUM**, ACROSS THE DECOMPOSITION
**METHOD** AT FIXED np = 4, WITH THIS CONFIGURATION'S OWN FD TABLE BESIDE IT, ON
TWO TOOLCHAIN ROWS.  FROZEN by md5 in PREREGISTRATION.md section 7 before any
container starts.  Computes nothing about physics; renders verdicts from the
FIXED vocabulary only (PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING).

DERIVED from `curriculum_SO1a/so1a_grade.py` with the registered deltas in
`so1cr_grade_DELTAS_from_so1a_grade.diff`.  SO-1a's machinery is inherited
VERBATIM where it is unchanged -- the ledger regex and its physics/infrastructure
split, the five rule-4 clauses printed individually per arm, R-RC, C5's
fatal-token refusal regardless of rc, the age datum resolved BY EXISTENCE over
both registered names, `grade_components`, `grade_tb`, and the L-342 field
classes.  SEVEN THINGS ARE NEW, AND EACH IS THE REASON THE RUNG EXISTS OR CLOSES
A MEASURED DEFECT:

  (A) G-NP -- np-INVARIANCE AT THE OPTIMUM, ON A BAND THIS LANE DID NOT CHOOSE.
      `docs/dafoam/ADJOINT_VERIFICATION_STANDARD.md` section 3 defines the check
      and FREEZES the band: `s_J <= 2.2e-5`, `s_g <= 1.0e-3` against the SERIAL
      reference, ZERO per-component sign flips on components with
      `|g_1,i| >= 1e-14`.  THOSE THREE NUMBERS ARE INHERITED BY CITATION AND ARE
      NOT RE-DERIVED HERE.  Their provenance is the family's own measurement:
      B3 measured the serial-vs-np4 gradient floor at 1.1-1.7e-4, so the band is
      6x the measured floor; the lab's partition-reproducibility upper bound on
      a converged quantity is 2.2e-5 (`PARALLEL_GATE_DOCTRINE.md:38, :194-198`, commit `fd9bf1b6`).
      NOTE THE SIZE: `s_g <= 1.0e-3` IS **50x TIGHTER** THAN BAND D (5 %), and a
      lane that reached for band D here would have registered a gate 50x too
      loose to see the effect it exists to find.
      THE SERIAL REFERENCE IS SO-1b's OWN np = 1 GRADIENT AT x*, READ FROM DISK
      AND NEVER RECOMPUTED, on TWO channels (the value the instrument carried
      forward, and this comparator's own independent read of the same source);
      a disagreement REFUSES.

  (B) G-METHOD -- THE HALF OF THE STANDARD'S OWN DEFINITION NOBODY HAS BOUGHT.
      Standard section 3 defines np-invariance as varying np "AND, AT FIXED np,
      ACROSS `scotch` / `simple` / `hierarchical`".  AV-1 and AV-1R buy the np
      sweep at FIXED `scotch` and say so in their own section 8 ("nothing about
      the `simple` or `hierarchical` decompositions").  A4 measured `scotch`
      8.95 % against `simple 4x1x1` 0.00054 % at ONE np on ONE mesh -- a factor
      of 16,600 -- so the METHOD axis is where the family's largest measured
      decomposition effect lives, and no A1 rung has ever varied it.  G-METHOD
      grades `scotch` against `simple` at fixed np = 4 on the SAME band.

  (C) G5N -- AN FD TABLE AT np = 4, WHICH IS WHAT MAKES THIS A VERDICT.  AV-1's
      own section 8 states the hole in its own gate: "A wrong treatment could
      still pass G-NP by producing the same wrong gradient at every np -- which
      is why this rung is not an FD verdict".  That is L-38 exactly
      (decomposition-invariance is not correctness).  Each arm here therefore
      buys ITS OWN central-FD table at ITS OWN decomposition and is graded
      against it on band D / band E, because `DAFOAM_CHARTER.md` section 5 makes
      an FD reference part of a CONFIGURATION and never carries one across np --
      the W4_IDX16 carrying failure the charter names.

  (D) G-MESHID -- "THE SAME MESH" IS ASSERTED, NOT ASSUMED.  The standard defines
      the check as the same gradient at the same design point "ON THE SAME MESH
      and image".  SO-1cR regenerates its own mesh rather than reading one across
      a run root, so mesh identity is not free: the `points` sha256 this item's
      MESH arm printed must equal the one SO-1b's MESH arm printed.  An
      inequality is a MESH-REGENERATION-DETERMINISM finding and makes the
      comparison ungradeable -- `NOT A RESULT`, never waved through.

  (E) G-CLOCK -- THE CAP GATE AND THE COST CLAIM READ DIFFERENT FRAMES, ON
      PURPOSE, AND BOTH ARE PRINTED.  A peer lane measured on D6 2026-08-27, and
      this lane confirmed present in SO-1a and SO-1b, that the cap is a
      `timeout` INSIDE the container while `core_min` is a wall bracketed around
      `docker run` ON THE HOST -- so an arm stopped exactly at its own registered
      deadline records a wall ABOVE the cap and trips its own cap limb: A GATE
      FAIL MANUFACTURED BY THE MEASUREMENT FRAME, NOT BY THE RUN.  At 4 ranks the
      poll granularity alone is 0.667 core-min.  The repair here is NOT a wider
      cap: G10 grades `core_min_container` (the kernel's own
      `StartedAt`/`FinishedAt`, the frame the deadline lives in) and the COST is
      claimed on `core_min` (the host frame, the frame the box is occupied in
      and the larger of the two).  Both are printed with their difference.  An
      unreadable container clock is INFRASTRUCTURE: G10 falls back to the HOST
      frame AND SAYS SO, never passing a limb it could not evaluate.

  (F) G-XSTAR -- AN IDENTITY ASSERTION, DELIBERATELY NOT A GATE ON THE DESIGN
      VECTOR.  D13 / C-71 measured this problem's design vector NON-UNIQUE and
      its drag UNIQUE: 15 of 15 restart pairs DIFFERENT on design, 0 of 15 on
      drag.  So no verdict here rests on a design vector.  G-XSTAR asserts only
      that the point THIS run solved at is byte-for-byte the point SO-1b bought,
      which is a provenance check on a consumed input, not a physical claim.

  (G) THE AGE-CHECKED LIST CONTAINS ONLY WHAT THIS RUN PRODUCES.
      `d4s_f3s_grade.py:61` listed `OptView.hst` -- a STAGED INPUT -- among its
      age-checked ARTEFACTS, making that clause UNSATISFIABLE BY CONSTRUCTION and
      forcing D4S-F3S to NOT A RESULT with 19 of 20 gate readings passing.  This
      item stages `so1b_E.json` into every solver arm; it is named in
      STAGED_INPUTS below, EXCLUDED BY NAME from ARTEFACT, and its exclusion is
      driven in the selftest rather than asserted in prose.

WHAT IT GRADES (PREREGISTRATION.md section 3):
  G1        completion, ARM-KIND AWARE and R-RC AWARE -- SO-1a's five clauses.
  G-M2      mesh identity: cells == 4,032 -> PASS else GATE FAIL.
  G-MESHID  the `points` sha256 equals SO-1b's -> else NOT A RESULT.
  G-DECOMP  every arm's artefact names the decomposition it was registered for,
            and `nprocs` == 4 == the dictionary's numberOfSubdomains -> else REFUSE.
  G-XSTAR   the design point solved == SO-1b's x* for that row -> else REFUSE.
  G-NP      per arm, against SO-1b's np = 1 serial reference at x*.
  G-METHOD  per row, `scotch` against `simple` at fixed np = 4.
  G5N/G5cN  per arm, the bright line on CD and on CL against THIS arm's own FD.
  G-TB      the charter-4 trivial baseline at the wrong step, per arm.
  G9/G10/G12  toolchain, caps (CONTAINER frame), placement (per-arm cpuset).
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
ITEM = "SO1cR"
BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-SO1cR-a1-naca0012-dragmin-npinv"
SO1B_BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-SO1b-a1-naca0012-dragmin-opt"
ARMS_REQUIRED = ["MESH", "Ns-P", "Ni-P", "Ns-S", "Ni-S"]
ARMS_SOLVER = ["Ns-P", "Ni-P", "Ns-S", "Ni-S"]
ARM_KIND = {"MESH": "SCRIPT", "Ns-P": "SOLVER", "Ni-P": "SOLVER", "Ns-S": "SOLVER", "Ni-S": "SOLVER"}
ARM_ROW = {"MESH": "SHIPPED", "Ns-P": "PATCHED", "Ni-P": "PATCHED", "Ns-S": "SHIPPED", "Ni-S": "SHIPPED"}
ARM_ROWKEY = {"Ns-P": "P", "Ni-P": "P", "Ns-S": "S", "Ni-S": "S"}
ROW_ARMS = {"P": ["Ns-P", "Ni-P"], "S": ["Ns-S", "Ni-S"]}
# ---- SO-1cR REPAIR 2 of 3, BREAK 6 CALL SITE (3).  THE ROW LABEL IS A REGISTERED
# ---- MAPPING, WRITTEN OUT IN FULL, AND IT IS THE SAME MAPPING THE CHAIN DRIVER
# ---- AND THE LAUNCHER USE.
# SO-1bR labels its per-row artefacts with the DIRECTORY SUFFIX ('P'/'S'), never
# the row name.  SO-1c's amendment R8 repaired the comparison in the chain driver
# alone; G-XSTAR below kept the equality form and would have refused the REAL
# artefact at GRADING even had the launcher's copy of the same break not stopped
# the chain first.  The mapping is deliberately NOT derived as `row[0]`: row[0]
# agrees with the producer only by the coincidence that PATCHED and SHIPPED share
# first letters with P and S, and a check true by coincidence has stopped being a
# check -- it would silently accept a row labelled 'PORPOISE' under PATCHED.
# THE TWO LABEL SETS ARE DISJOINT.  That disjointness is the assertion's whole
# point: it exists to catch AN ARTEFACT SITTING IN THE WRONG DIRECTORY, so a
# SHIPPED artefact staged under optref/PATCHED/ still refuses and vice versa.
ROW_LABELS = {"PATCHED": ("PATCHED", "P"), "SHIPPED": ("SHIPPED", "S")}
# NOT an `assert`: this module registers `ast.Assert == 0` (U49/U50) and its own
# selftest runs under `python3 -O`, which STRIPS `assert` -- a disjointness check
# that vanishes under the optimiser is not a check.  This raises at import,
# before any grading path can run.
if set(ROW_LABELS["PATCHED"]) & set(ROW_LABELS["SHIPPED"]):
    raise SystemExit("SO1CR_GRADE REFUSE ROW_LABELS: the two rows' label sets MUST be "
                     "DISJOINT or the row assertion stops being a check")
# THE DECOMPOSITION AXIS.  `DAFOAM_CHARTER.md` section 5 forbids describing a case
# as decomposition-invariant from ONE arm, so each row buys both methods.
ARM_DECOMP = {"Ns-P": "scotch", "Ni-P": "simple", "Ns-S": "scotch", "Ni-S": "simple"}
DECOMP_SIMPLE_N = ["4", "1", "1"]
ARM_RANKS = {"MESH": 1, "Ns-P": 4, "Ni-P": 4, "Ns-S": 4, "Ni-S": 4}
REGISTERED_NPROCS = 4
ARTEFACT = {"MESH": "checkMesh.log", "Ns-P": "so1cr_N.json", "Ni-P": "so1cr_N.json",
            "Ns-S": "so1cr_N.json", "Ni-S": "so1cr_N.json"}
# ---- STAGED INPUTS.  NAMED, AND EXCLUDED FROM THE AGE-CHECKED LIST BY NAME.
# The D4S-F3S defect (`d4s_f3s_grade.py:61`) put a staged input among the
# age-checked ARTEFACTS and made that clause unsatisfiable by construction.  An
# age guard checks only what the run PRODUCES; this list is what it must NEVER
# check, and the selftest drives the exclusion rather than trusting this comment.
STAGED_INPUTS = ("so1b_E.json", "so1cr_runScript.py", "so1cr_xn.py",
                 os.path.join("system", "decomposeParDict"))
TERMINAL = {"Ns-P": "SO1CR_N_WRITTEN", "Ni-P": "SO1CR_N_WRITTEN",
            "Ns-S": "SO1CR_N_WRITTEN", "Ni-S": "SO1CR_N_WRITTEN"}
DATUM_CANDIDATES = {"MESH": ("0.orig/U", "0.orig/U.gz"), "Ns-P": ("0/U", "0/U.gz"),
                    "Ni-P": ("0/U", "0/U.gz"), "Ns-S": ("0/U", "0/U.gz"),
                    "Ni-S": ("0/U", "0/U.gz")}
DATUM_FILE = ".so1cr_age_datum"
CONTROLDICT_REL = os.path.join("system", "controlDict")
DECOMPDICT_REL = os.path.join("system", "decomposeParDict")

FATAL_TOKENS = ("FOAM FATAL ERROR", "FOAM FATAL IO ERROR", "Segmentation fault",
                "SIGSEGV", "SIGKILL", "MPI_ABORT", "signal 9", "Signal 11",
                "Floating point exception",
                # ADOPTED FROM THE LAB'S OWN IMPLEMENTATION, AMENDMENT R6:
                # `sdk/chief_engineer/head_engineer.py:188` reads
                #     FPE = re.compile(r"Foam::sigFpe::sigHandler|^Floating point exception")
                # -- the handler symbol is the ONE string OpenFOAM emits only when
                # the FPE handler has actually FIRED.  It is added here as an extra
                # POSITIVE token, which STRENGTHENS detection: a crash whose shell
                # line never reaches the log is still caught by its stack trace.
                # Its LINE ANCHOR is DELIBERATELY NOT adopted -- see
                # BENIGN_LINE_PATTERNS below for the measured reason.
                "Foam::sigFpe::sigHandler")

# ---- C5's BENIGN-LINE EXCLUSION.  AMENDMENT R6, 2026-08-28.  ------------------
# THE DEFECT THIS REMOVES, NAMED: `"Floating point exception"` as a BARE
# SUBSTRING matches OpenFOAM's STANDARD STARTUP BANNER
#     `trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).`
# -- a notice that the solver is PROTECTED against the very failure the token
# exists to detect.  SO-1a's grader (`so1a_grade.py`, the byte-identical site)
# refused on exactly that line, `MESH/checkMesh.log:18`, and published NOT A
# RESULT WITH ZERO GATES EVALUATED on a run whose five arms were all rc = 0.
#
# THE TOKEN IS NOT DELETED.  Deleting it would blind C5 to a real SIGFPE crash,
# which is the WORSE error direction: a missed crash is laundered into a result,
# a false hit only costs a re-read.  It is EXCLUDED PER LINE instead, and the
# exclusion is written as a NARROW list of ENABLEMENT NOTICES rather than as a
# positive "crash signature", because a crash spelling this lane has not seen
# would slip through a positive pattern while an over-narrow exclusion only
# costs a false refusal.
#
# TWO LAB IMPLEMENTATIONS WERE READ BEFORE THIS ONE WAS WRITTEN, AND THE CHOICE
# BETWEEN THEM IS MEASURED, NOT PREFERRED:
#   * `sdk/chief_engineer/mesh_certificate.py:73` DELETES the FPE and segfault
#     tokens outright (`_FATAL = -->\s*FOAM FATAL(?:\s+IO)?\s+ERROR|FOAM exiting`)
#     and leans on a REQUIRED `^End` marker to catch a silent crash, calibrated on
#     105 real checkMesh logs.  RIGHT FOR ITS SCOPE, REJECTED FOR THIS ONE: that
#     module certifies checkMesh only, where a crash cannot be an MPI abort.  C5
#     here also scans FOUR np = 4 SOLVER logs, and deleting the token is exactly
#     the blinding this amendment must not do.
#   * `sdk/chief_engineer/head_engineer.py:188` matches
#     `Foam::sigFpe::sigHandler|^Floating point exception` -- a POSITIVE crash
#     signature.  ITS HANDLER SYMBOL IS ADOPTED ABOVE.  ITS LINE ANCHOR IS NOT,
#     and the reason is this item's own regime: at np = 4 the realistic FPE report
#     is OpenMPI's, e.g. `mpirun noticed that process rank 2 exited on signal 8
#     (Floating point exception).` -- NOT line-initial, and carrying no handler
#     symbol.  `^Floating point exception` would MISS it.  An EXCLUSION list is
#     therefore used instead of a positive anchor: a crash spelling this lane has
#     not seen slips through a positive pattern, while an over-narrow exclusion
#     only costs a false refusal, and a false refusal is the survivable error.
#
# WHY THE `trapFpe:` PREFIX IS SAFE TO EXCLUDE: it is the diagnostic prefix
# printed by OpenFOAM's FPE-TRAPPING SETUP code.  A crash never prefixes itself
# with it -- a real SIGFPE prints `Foam::sigFpe::sigHandler(int)` in the stack
# trace and `Floating point exception (core dumped)` from the shell, and NEITHER
# line begins `trapFpe:`.  Both of those are DRIVEN as planted positives.
#
# EVERY EXCLUSION IS COUNTED AND PRINTED ON THE PASS RECORD.  A suppression a
# reader cannot see is the same defect wearing the other hat.
BENIGN_LINE_PATTERNS = (
    (r"^\s*trapFpe:\s",
     "OpenFOAM sigFpe SETUP banner -- an ENABLEMENT NOTICE, not a crash"),
)
BENIGN_LINE_RE = tuple((re.compile(_p), _why) for _p, _why in BENIGN_LINE_PATTERNS)
CAPS = {"MESH": 5.0, "Ns-P": 30.0, "Ni-P": 30.0, "Ns-S": 30.0, "Ni-S": 30.0}
ITEM_CEILING_CORE_MIN = 125.0          # == sum(CAPS.values()), asserted in main()
PREDICTED_CORE_MIN = {"MESH": 0.167, "Ns-P": 10.0, "Ni-P": 10.0, "Ns-S": 10.0, "Ni-S": 10.0}
CELLS_EXPECTED = 4032

# ---- BAND D / BAND E / PLATEAU: the FD bands, INHERITED BY CITATION from
# ---- SO-1a and SO-1b, which inherit them from `curriculum_D4/PREREGISTRATION.md:82`
# ---- and `D7FR:228-229`.  BYTE-IDENTICAL to SO-1a's.  NOT re-derived here.
FD_BAND_PCT = 5.0            # band D, per component
AGG_BAND_PCT = 5.0           # band E, aggregate vector-relative
PLATEAU_TOL_PCT = 10.0
MIN_GRADED = 3
NEAR_ZERO_ABS = 1.0e-14

# ---- THE np-INVARIANCE BAND, INHERITED BY CITATION from
# ---- `docs/dafoam/ADJOINT_VERIFICATION_STANDARD.md` section 3's own band table
# ---- (the same three numbers AV-1 and AV-1R registered).  NOT re-derived by a
# ---- lane that has not measured them, and DELIBERATELY NOT band D: `s_g` here
# ---- is 50x TIGHTER than 5 %, which is the whole reason the gate can see an
# ---- effect the FD band would hide.
S_J_BAND = 2.2e-5            # objective spread, the lab's partition-reproducibility bound
S_G_BAND = 1.0e-3            # gradient L2 spread vs the serial reference (6x B3's measured floor)
SIGN_FLIP_MAX = 0            # VERIFICATION_CHARTER.md:845

COMPONENTS_REGISTERED = [["shape", 0], ["shape", 3], ["shape", 6], ["shape", 7], ["patchV", 1]]
STEPS_REGISTERED = {"shape": [1.0e-2, 1.0e-3, 1.0e-4], "patchV": [1.0e-1, 1.0e-2, 1.0e-3]}
TB_STEPS_REGISTERED = {"shape": [1.0e-8], "patchV": [1.0e-6]}
TB_MAX_PASSING = 1
CTRL_STEP = 1.0e-3
PLANT = 1.234e-03
IMG_DIGEST = {"SHIPPED": "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc",
              "PATCHED": "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"}
SO_MD5 = {"SHIPPED": "f0fcb488e0e98156575cd19548e91663",
          "PATCHED": "85f59e87253e0a71a813f64ca6e4c425"}
CPUSET_REGISTERED = {"MESH": "10", "Ns-P": "10,11,12,13", "Ni-P": "10,11,12,13",
                     "Ns-S": "10,11,12,13", "Ni-S": "10,11,12,13"}
DELIVERED_CORES_FLOOR = 3.0            # 0.75 x 4 ranks, AV-1's rule at this rank count

PRED = {
    "PI_core_min_band": (22.0, 80.0),
    "P_mesh_wall_s_max": 120.0,
    "P_tb_min_failing": 4,
    "P_min_pass_components": 4,
}

FIELDS_PHYSICS = ("rc_value", "oomkilled", "terminal_statement", "age_guard",
                  "no_fatal_token", "core_min", "cap_core_min", "DIGEST", "cpuset")
FIELDS_INFRASTRUCTURE = ("rc_record", "memavail_pre_GiB", "memavail_post_GiB", "delivered",
                         "siblings_pre", "siblings_post", "log", "wall_s",
                         "core_min_container", "clock_frame_delta_core_min")
NOT_MEASURED = "NOT_MEASURED"
VOCAB = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}
EXPECTED_UNITS = 72          # 53 at SO-1c's v1.0 freeze; +12 by AMENDMENT R6, 2026-08-28,
                             # DELIBERATELY BUMPED with the ten units named in the
                             # amendment.  A silent bump is the same defect as a
                             # silently lost unit.
                             # SO-1cR: 65 -> 72, the SEVEN units U66-U72 named in
                             # this item's §7 -- BREAK 6's row label driven at the
                             # grader's own call site: the producer's label, the
                             # other registered label, BOTH SWAP DIRECTIONS, an
                             # unregistered label, and the disjointness of the two
                             # label sets asserted rather than trusted from prose.
                             # THIS GUARD CAUGHT THE ADDITION (rc=2) BEFORE THE
                             # BUMP, which is what it is for.
class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read())) if isinstance(n, ast.Assert))


# ================= LEDGER (physics vs infrastructure, L-342) -- D5's regex ============
LEDGER_RE = re.compile(
    r"ARM=(?P<ARM>\S+)\s+ROW=(?P<ROW>\S+)\s+DECOMP=(?P<DECOMP>\S+)\s+IMG=(?P<IMG>\S+)\s+"
    r"DIGEST=(?P<DIGEST>\S+)\s+rc=(?P<rc>-?\d+)\s+wall_s=(?P<wall_s>\d+)\s+"
    r"container_wall_s=(?P<container_wall_s>[\d.]+|NOT_MEASURED)\s+"
    r"ranks=(?P<ranks>\d+)\s+core_min=(?P<core_min>[\d.]+)\s+"
    r"core_min_container=(?P<core_min_container>[\d.]+|NOT_MEASURED)\s+"
    r"clock_frame_delta_core_min=(?P<clock_delta>-?[\d.]+|NOT_MEASURED)\s+"
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
                                   ("siblings_post", g["sibpost"]), ("log", g["log"]),
                                   ("core_min_container", g["core_min_container"]),
                                   ("clock_frame_delta_core_min", g["clock_delta"]))
                    if v is None or NOT_MEASURED in str(v)]
        row = {"ARM": g["ARM"], "ROW": g["ROW"], "IMG": g["IMG"], "DIGEST": g["DIGEST"],
               "rc": int(g["rc"]), "wall_s": int(g["wall_s"]), "ranks": int(g["ranks"]),
               "core_min": float(g["core_min"]), "cap_core_min": float(g["cap"]),
               # ---- G-CLOCK.  BOTH FRAMES ARE CARRIED.  `core_min` is the HOST
               # frame (the wall bracketed around `docker run` plus the poller's
               # granularity) and is the COST claim; `core_min_container` is the
               # KERNEL's own container clock and is the frame the in-container
               # `timeout` deadline actually lives in, so it is the CAP GATE's
               # frame.  Grading a container-enforced cap in the host frame is how
               # an arm stopped exactly at its own deadline fails its own cap limb.
               "core_min_container": (None if g["core_min_container"] in (None, NOT_MEASURED)
                                      else float(g["core_min_container"])),
               "container_wall_s": (None if g["container_wall_s"] in (None, NOT_MEASURED)
                                    else float(g["container_wall_s"])),
               "clock_frame_delta_core_min": (None if g["clock_delta"] in (None, NOT_MEASURED)
                                              else float(g["clock_delta"])),
               "DECOMP": g["DECOMP"],
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


def _container_wall_s(started, finished):
    """The KERNEL's own container clock, parsed from `docker inspect`'s RFC3339
    stamps.  This is the frame the in-container `timeout` deadline lives in, and
    therefore the frame the cap gate must be graded in (G-CLOCK).  Unparseable ->
    None, reported as NOT_MEASURED, never silently replaced by the host frame."""
    import datetime

    def p(t):
        t = (t or "").strip()
        if not t or t.startswith("0001-01-01"):
            return None
        if t.endswith("Z"):
            t = t[:-1]
        if "." in t:
            h, f = t.split(".", 1)
            t = h + "." + (f + "000000")[:6]
        try:
            return datetime.datetime.fromisoformat(t)
        except ValueError:
            return None
    a, b = p(started), p(finished)
    if a is None or b is None or b < a:
        return None
    return round((b - a).total_seconds(), 3)


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
    # ---- G-CLOCK, ON THE FALLBACK CHANNEL TOO.  The surviving inspect record
    # carries `.State.StartedAt` and `.State.FinishedAt` as fields 3 and 4, so the
    # CONTAINER frame -- the frame the cap deadline lives in -- survives even when
    # the ledger row does not.  The HOST frame does not survive, and is not guessed.
    cwall = _container_wall_s(parts[2] if len(parts) > 2 else None,
                              parts[3] if len(parts) > 3 else None)
    cmc = None if cwall is None else round(cwall * ARM_RANKS[arm] / 60.0, 3)
    return {"ARM": arm, "ROW": ARM_ROW[arm], "DECOMP": ARM_DECOMP.get(arm),
            "IMG": None, "DIGEST": (parts[6] if len(parts) > 6 else None), "rc": rc, "wall_s": None,
            "container_wall_s": cwall, "core_min_container": cmc,
            "clock_frame_delta_core_min": None,
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


def benign_reason(line):
    """(C) C5, AMENDMENT R6.  Why this ONE LINE is an enablement notice and not a
    crash, or None.  Narrow by construction: see BENIGN_LINE_PATTERNS."""
    for rx, why in BENIGN_LINE_RE:
        if rx.search(line):
            return why
    return None


def fatal_token_sites(text, source):
    """(C) C5, AMENDMENT R6.  Scans LINE BY LINE and PER SOURCE FILE, returning
    (sites, benign).  Any site REFUSES regardless of rc, so the R-RC relaxation in
    (B) can never launder a crash into a NOT MEASURED.

    LINE BY LINE, because the token test must be able to tell a CRASH from an
    ENABLEMENT NOTICE and a whole-file substring test cannot.  Every token in
    FATAL_TOKENS is a single-line string, so splitting loses no match -- and that
    is DRIVEN, not asserted: one unit plants each token in turn and requires a
    refusal for every one.

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
        # AMENDMENT R6: scanned PER FILE and PER LINE.  `hay = text + artefact`
        # discarded which file a hit came from, which is why SO-1a's refusal named
        # the arm log for a token that only ever appeared in `checkMesh.log`.
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
def read_N(path):
    """One artefact per arm carries BOTH the analytic gradient at np = 4 AND that
    configuration's OWN central-FD table.  SO-1a split these into an X arm and an
    F arm because they answer two questions at one design point; here they MUST
    share a process, because `DAFOAM_CHARTER.md` section 5 makes an FD reference
    part of a CONFIGURATION and never carries one across np.  Returns the two
    views `grade_components` expects, plus everything the new gates read."""
    j = json.load(open(path))
    if j.get("tb_steps") is not None and j.get("tb_steps") != TB_STEPS_REGISTERED:
        refuse("G-TB", {"tb_steps_not_registered": j.get("tb_steps"), "registered": TB_STEPS_REGISTERED,
                        "note": "the trivial baseline is fixed at the freeze (DAFOAM_CHARTER section 4)"})
    if j.get("components_requested") != COMPONENTS_REGISTERED:
        refuse("G5N", {"components_requested_not_registered": j.get("components_requested"),
                       "registered": COMPONENTS_REGISTERED})
    if j.get("steps") is not None and j.get("steps") != STEPS_REGISTERED:
        refuse("G5N", {"steps_not_registered": j.get("steps"), "registered": STEPS_REGISTERED})
    adj = {}
    for of in ("CD", "CL"):
        adj[of] = {dv: [float(v) for v in j["adjoint"][of][dv]] for dv in ("shape", "patchV")}
    ref = j.get("adjoint_np1_reference")
    if not ref:
        refuse("G-NP", {"np1_reference_absent_from_artefact": path,
                        "note": "the serial reference is SO-1b's np = 1 gradient at x*; "
                                "without it there is nothing to be invariant against"})
    ref_adj = {}
    for of in ("CD", "CL"):
        ref_adj[of] = {dv: [float(v) for v in ref[of][dv]] for dv in ("shape", "patchV")}
    table, ctrl = {}, None
    for row in j["rows"]:
        if row.get("dv") == "CTRL":
            ctrl = row
            continue
        key = (row["dv"], int(row["idx"]))
        fd, tb = {}, {}
        for _k, v in (row.get("fd") or {}).items():
            fd[float(v["step"])] = {"ok": bool(v.get("ok")),
                                    "dCD": (float(v["dCD"]) if v.get("ok") else None),
                                    "dCL": (float(v["dCL"]) if v.get("ok") else None)}
        for _k, v in (row.get("tb") or {}).items():
            tb[float(v["step"])] = {"ok": bool(v.get("ok")),
                                    "dCD": (float(v["dCD"]) if v.get("ok") else None),
                                    "dCL": (float(v["dCL"]) if v.get("ok") else None)}
        table[key] = {"status": row.get("status"), "fd": fd, "tb": tb}
    X = {"CD": float(j["CD_optimum"]), "CL": float(j["CL_optimum"]), "adjoint": adj,
         "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"), "nprocs": j.get("nprocs")}
    F = {"table": table, "ctrl": ctrl, "CD": float(j["CD_optimum"]), "eta": float(j["eta_used"]),
         "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5"), "raw": j}
    meta = {"nprocs": j.get("nprocs"), "row": j.get("row"),
            "decomposition": j.get("decomposition") or {},
            "design_point": j.get("design_point") or {},
            "np1_reference": ref_adj, "np1_nprocs": j.get("adjoint_np1_nprocs"),
            "np1_source": j.get("adjoint_np1_source"),
            "so_md5": (j.get("identity") or {}).get("libidwarp_so_md5")}
    return X, F, meta


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


def grader_plant_control(base, npath, tag):
    """Write a copy with PLANT added to every physical dCD, re-read it through the
    SAME reader, and refuse unless every value moved by exactly PLANT.  A zero from
    a reader not shown able to see a non-zero is not evidence (rule 3)."""
    j = json.load(open(npath))
    for row in j["rows"]:
        if row.get("dv") == "CTRL":
            continue
        for v in (row.get("fd") or {}).values():
            if v.get("ok"):
                v["dCD"] = repr(float(v["dCD"]) + PLANT)
    cdir = os.path.join(base, "grader_controls")
    os.makedirs(cdir, exist_ok=True)
    cp = os.path.join(cdir, "N_%s_planted.json" % tag)
    json.dump(j, open(cp, "w"), indent=1, sort_keys=True)
    orig, back = read_N(npath)[1]["table"], read_N(cp)[1]["table"]
    worst, n = 0.0, 0
    for key, row in orig.items():
        for s, v in row["fd"].items():
            if v["ok"]:
                worst = max(worst, abs((back[key]["fd"][s]["dCD"] - v["dCD"]) - PLANT))
                n += 1
    if n == 0 or worst > 1e-12:
        refuse("CONTROL", {"grader_plant_not_seen": {"n_values": n, "worst_residual": worst, "plant": PLANT}})
    return {"grader_plant_seen": True, "n_values": n, "worst_residual": worst, "file": cp}


def grader_np_control(base, npath, tag):
    """AND THE SAME DISCIPLINE ON THE np-INVARIANCE READER, WHICH IS THIS ITEM'S
    HEADLINE GATE.  A copy of the artefact with the np = 1 reference SCALED BY
    1 + 10 x S_G_BAND is graded through the same `g_npinv`, and the control
    REFUSES unless that copy reads GATE FAIL.  A gate that has never been shown to
    fail on a planted disagreement is not a gate -- and this is the reader whose
    PASS would otherwise be the item's whole claim."""
    j = json.load(open(npath))
    factor = 1.0 + 10.0 * S_G_BAND
    for of in ("CD", "CL"):
        for dv in ("shape", "patchV"):
            j["adjoint_np1_reference"][of][dv] = [repr(float(v) * factor)
                                                  for v in j["adjoint_np1_reference"][of][dv]]
    cdir = os.path.join(base, "grader_controls")
    os.makedirs(cdir, exist_ok=True)
    cp = os.path.join(cdir, "N_%s_np_planted.json" % tag)
    json.dump(j, open(cp, "w"), indent=1, sort_keys=True)
    _x, _f, meta = read_N(cp)
    probe = g_npinv(_x, meta, "PLANTED")
    if probe["verdict"] != "GATE FAIL":
        refuse("CONTROL", {"np_gate_did_not_fire_on_a_planted_disagreement": {
            "scaled_reference_by": factor, "band": S_G_BAND, "read": probe["verdict"],
            "note": "a reader not shown able to see a disagreement cannot certify agreement"}})
    return {"np_plant_seen": True, "scaled_by": factor, "read": probe["verdict"], "file": cp}


# ================= G-NP / G-METHOD -- np-INVARIANCE AT THE OPTIMUM ====================
def _concat(adjoint, of):
    return list(adjoint[of]["shape"]) + list(adjoint[of]["patchV"])


def _spread(a, b):
    """s = ||a - b||2 / ||b||2, with `b` the REFERENCE.  The standard's own
    definition (ADJOINT_VERIFICATION_STANDARD.md section 3); never averaged
    across configurations, never symmetrised."""
    if len(a) != len(b):
        return None, None
    num = math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
    den = math.sqrt(sum(y * y for y in b))
    if den <= 0.0:
        return None, None
    return num / den, den


def _sign_flips(a, b):
    """Per-component sign disagreement, on components whose REFERENCE magnitude is
    at or above NEAR_ZERO_ABS.  Smaller ones are NAMED AND SKIPPED rather than
    counted, because the sign of a number at the noise floor is not a measurement
    (VERIFICATION_CHARTER.md:845)."""
    flips, skipped = [], []
    for i, (x, y) in enumerate(zip(a, b)):
        if abs(y) < NEAR_ZERO_ABS:
            skipped.append({"index": i, "reference": y})
            continue
        if (x > 0) != (y > 0) and x != 0.0:
            flips.append({"index": i, "reference": y, "measured": x})
    return flips, skipped


def g_npinv(X, meta, arm):
    """G-NP: this arm's np = 4 analytic gradient against SO-1b's np = 1 SERIAL
    reference AT THE SAME DESIGN POINT.  The band is inherited BY CITATION from
    ADJOINT_VERIFICATION_STANDARD.md section 3 and is NOT band D -- it is 50x
    tighter, which is the only reason it can see A4's measured effect."""
    out = {"arm": arm, "decomposition": ARM_DECOMP.get(arm),
           "nprocs": meta.get("nprocs"), "reference_nprocs": meta.get("np1_nprocs"),
           "reference_source": meta.get("np1_source"),
           "band_s_g": S_G_BAND, "band_s_j": S_J_BAND, "sign_flip_max": SIGN_FLIP_MAX,
           "band_provenance": ("ADJOINT_VERIFICATION_STANDARD.md section 3 band table; "
                               "inherited by citation, NOT re-derived; 6x B3's measured "
                               "1.1-1.7e-4 floor and 50x tighter than band D"),
           "per_objective": {}}
    if meta.get("np1_nprocs") != 1:
        out["verdict"] = "NOT A RESULT"
        out["reason"] = "SERIAL_REFERENCE_IS_NOT_np1"
        return out
    worst = 0.0
    verdict = "PASS"
    for of in ("CD", "CL"):
        a = _concat(X["adjoint"], of)
        b = _concat(meta["np1_reference"], of)
        s_g, norm = _spread(a, b)
        flips, skipped = _sign_flips(a, b)
        row = {"s_g": s_g, "reference_norm": norm, "n_components": len(b),
               "sign_flips": flips, "near_zero_skipped": skipped,
               "per_component": []}
        for dv, idx in COMPONENTS_REGISTERED:
            off = 0 if dv == "shape" else len(X["adjoint"][of]["shape"])
            i = off + idx
            if i < len(a) and i < len(b):
                den = max(abs(b[i]), NEAR_ZERO_ABS)
                row["per_component"].append(
                    {"dv": dv, "idx": idx, "np4": a[i], "np1": b[i],
                     "abs_rel_diff": abs(a[i] - b[i]) / den})
        if s_g is None:
            row["verdict"] = "NOT A RESULT"
            row["reason"] = "LENGTH_MISMATCH_OR_ZERO_REFERENCE"
            verdict = "NOT A RESULT"
        else:
            worst = max(worst, s_g)
            row["verdict"] = "PASS" if (s_g <= S_G_BAND and len(flips) <= SIGN_FLIP_MAX) else "GATE FAIL"
            if row["verdict"] == "GATE FAIL" and verdict != "NOT A RESULT":
                verdict = "GATE FAIL"
        out["per_objective"][of] = row
    out["worst_s_g"] = worst
    out["verdict"] = verdict
    return out


def g_objective_spread(X, ref_scalars, arm):
    """The objective beside the gradient, as the standard requires.  `s_J` is
    graded on its OWN band (2.2e-5), which is far tighter than the gradient's --
    B3 measured 2.9e-7 -- so an objective that moves under decomposition is a
    louder finding than a gradient that does."""
    out = {"arm": arm, "band_s_j": S_J_BAND, "per_objective": {}, "verdict": "PASS"}
    for of in ("CD", "CL"):
        ref = ref_scalars.get(of)
        got = X[of]
        if ref is None:
            out["per_objective"][of] = {"verdict": NOT_MEASURED, "np4": got, "np1": None}
            continue
        den = max(abs(ref), NEAR_ZERO_ABS)
        s_j = abs(got - ref) / den
        v = "PASS" if s_j <= S_J_BAND else "GATE FAIL"
        out["per_objective"][of] = {"np4": got, "np1": ref, "s_J": s_j, "verdict": v}
        if v == "GATE FAIL":
            out["verdict"] = "GATE FAIL"
    return out


def g_method(N, rowkey):
    """G-METHOD: `scotch` against `simple 4x1x1` AT FIXED np = 4, on the SAME band.
    This is the half of ADJOINT_VERIFICATION_STANDARD.md section 3's own definition
    ("and, at fixed np, across scotch / simple / hierarchical") that AV-1 and AV-1R
    disclaim in their own section 8, and it is the axis on which A4 measured a
    factor of 16,600 between two decompositions of ONE mesh at ONE np."""
    a_arm, b_arm = ROW_ARMS[rowkey]          # scotch, simple -- in that registered order
    out = {"row": rowkey, "scotch_arm": a_arm, "simple_arm": b_arm,
           "band_s_g": S_G_BAND, "per_objective": {}, "verdict": "PASS",
           "reference_convention": ("`simple 4x1x1` is the REFERENCE limb and `scotch` "
                                    "the graded limb, fixed here before the run: A4 "
                                    "measured `simple 4x1x1` at 0.00054 % against FD and "
                                    "`scotch` at 8.95 %, so the cleaner limb is the "
                                    "reference.  The convention is registered, not chosen "
                                    "after the numbers arrive.")}
    Xs, Xi = N[a_arm][0], N[b_arm][0]
    for of in ("CD", "CL"):
        s_g, norm = _spread(_concat(Xs["adjoint"], of), _concat(Xi["adjoint"], of))
        flips, skipped = _sign_flips(_concat(Xs["adjoint"], of), _concat(Xi["adjoint"], of))
        if s_g is None:
            out["per_objective"][of] = {"verdict": "NOT A RESULT", "reason": "LENGTH_MISMATCH"}
            out["verdict"] = "NOT A RESULT"
            continue
        v = "PASS" if (s_g <= S_G_BAND and len(flips) <= SIGN_FLIP_MAX) else "GATE FAIL"
        out["per_objective"][of] = {"s_g_scotch_vs_simple": s_g, "reference_norm": norm,
                                    "sign_flips": flips, "near_zero_skipped": skipped,
                                    "verdict": v}
        if v == "GATE FAIL" and out["verdict"] != "NOT A RESULT":
            out["verdict"] = "GATE FAIL"
    return out


# ================= G-DECOMP / G-XSTAR / G-MESHID ======================================
def g_decomp(meta, arm):
    """`DAFOAM_CHARTER.md` section 5 forbids "a parallel gradient table with no
    decomposition column".  HERE THE COLUMN IS A GATE: the artefact must name the
    method it was registered for, the subdivision for `simple`, and an `nprocs`
    that agrees with the dictionary's own `numberOfSubdomains`.  A disagreement
    REFUSES -- a gradient that cannot name its decomposition is not a result."""
    d = meta.get("decomposition") or {}
    want = ARM_DECOMP[arm]
    got = d.get("decomp_method")
    n = d.get("decomp_n_subdomains")
    if got != want:
        refuse("G-DECOMP", {"arm": arm, "registered_method": want, "artefact_method": got,
                            "source": d.get("decomp_source")})
    if n != REGISTERED_NPROCS or meta.get("nprocs") != REGISTERED_NPROCS:
        refuse("G-DECOMP", {"arm": arm, "registered_nprocs": REGISTERED_NPROCS,
                            "dict_numberOfSubdomains": n, "mpi_nprocs": meta.get("nprocs"),
                            "note": "cross-asserted on two sources; two numbers from one "
                                    "source can both be wrong"})
    if want == "simple" and list(d.get("decomp_simple_n") or []) != DECOMP_SIMPLE_N:
        refuse("G-DECOMP", {"arm": arm, "registered_simple_n": DECOMP_SIMPLE_N,
                            "artefact_simple_n": d.get("decomp_simple_n"),
                            "note": "section 5: for `simple` the SUBDIVISION is part of the "
                                    "disclosure, not only the method name"})
    return {"arm": arm, "method": got, "n_subdomains": n,
            "simple_n": d.get("decomp_simple_n"), "mpi_nprocs": meta.get("nprocs"),
            "source": d.get("decomp_source"), "verdict": "PASS"}


def g_xstar(root, meta, arm):
    """G-XSTAR is a PROVENANCE assertion on a CONSUMED INPUT, and is deliberately
    NOT a gate on the design vector as a result.  D13 / C-71 measured this
    problem's design vector NON-UNIQUE and its drag UNIQUE -- 15 of 15 restart
    pairs DIFFERENT on design, 0 of 15 on drag -- so no verdict in this item rests
    on a design vector.  What is asserted is only that the point THIS arm solved
    at is the point SO-1b bought, read back from the staged copy in this item's
    own run root and compared on the exact float repr."""
    rowkey = ARM_ROWKEY[arm]
    src = os.path.join(root, "optref", ARM_ROW[arm], "so1b_E.json")
    if not os.path.isfile(src):
        refuse("G-XSTAR", {"arm": arm, "staged_optimum_absent": src})
    ref = json.load(open(src))
    want = ref.get("design_point") or {}
    got = meta.get("design_point") or {}
    for dv in ("shape", "patchV"):
        w = [str(v) for v in (want.get(dv) or [])]
        g = [str(v) for v in (got.get(dv) or [])]
        if not w or w != g:
            refuse("G-XSTAR", {"arm": arm, "dv": dv, "so1b_x_star": w, "solved_at": g,
                               "note": "this arm did not solve at the point SO-1b bought"})
    want_labels = ROW_LABELS.get(ARM_ROW[arm])
    if want_labels is None:
        refuse("G-XSTAR", {"arm": arm, "unregistered_row": ARM_ROW[arm]})
    if ref.get("row") not in want_labels:
        refuse("G-XSTAR", {"arm": arm, "staged_artefact_row": ref.get("row"),
                           "arm_row": ARM_ROW[arm],
                           "registered_labels": list(want_labels),
                           "note": "a row is an image hash, never a directory name; the only "
                                   "labels REGISTERED for this row are those listed, and the two "
                                   "rows' label sets are DISJOINT so a swapped artefact cannot "
                                   "satisfy this"})
    return {"arm": arm, "row": ARM_ROW[arm], "rowkey": rowkey, "source": src,
            "n_shape": len(want.get("shape") or []), "n_patchV": len(want.get("patchV") or []),
            "verdict": "PASS",
            "note": "IDENTITY ASSERTION ON A CONSUMED INPUT -- not a gate on the design vector"}


def _points_sha(text):
    return sorted(set(re.findall(r"\b([0-9a-f]{64})\b\s+\S*constant/polyMesh/points", text)))


def g_meshid(root):
    """G-MESHID.  ADJOINT_VERIFICATION_STANDARD.md section 3 defines the check as
    the same gradient at the same design point "ON THE SAME MESH and image".  This
    item regenerates its own mesh rather than reading one across a run root, so
    mesh identity IS NOT FREE and IS NOT ASSUMED.  An inequality is a
    MESH-REGENERATION-DETERMINISM finding and makes the whole comparison
    ungradeable: NOT A RESULT, with both digests printed."""
    # ---- AMENDMENT R6, 2026-08-28.  UNIQUENESS REFUSAL, NOT A BETTER SORT. -----
    # THE DEFECT THIS REMOVES: the loop below used to be
    #     `for cand in sorted(glob.glob(...)): mine_src = cand`
    # -- a LAST-WINS reduction of a multi-member set to one member by an ordering
    # that is not the physics' ordering.  Its partner on the reference side was
    # `so1cr_chain_driver.sh`'s `grep ... MESH_*.log | head -4`, effectively a
    # FIRST-WINS pick over the same file shape in SO-1b's root, and under ugrep
    # multi-file output order is a RACE, so it is not even reliably first.
    #
    # AND THE FAILURE TEXT WAS ALREADY WRITTEN AS A PHYSICS CLAIM.  A misread
    # reference published as `MESH_REGENERATION_IS_NOT_DETERMINISTIC` -- fluent,
    # quotable and wrong.  So every REFUSAL below is a NOT A RESULT that names
    # itself a READER CONDITION and never borrows that sentence; the physics
    # sentence is emitted only where the comparison actually ran on ONE
    # unambiguous sha on each side.
    #
    # THE SELECTION IS RECORDED WHETHER OR NOT IT REFUSES: which file was chosen,
    # the full candidate list, and the sha count on each side.
    mine_log = os.path.join(root, "MESH", "checkMesh.log")
    cands = sorted(glob.glob(os.path.join(root, "MESH_*.log")))
    ref_path = os.path.join(root, "optref", "so1b_mesh_points_sha256.txt")
    out = {"this_item_points_sha256": [], "so1b_points_sha256": [],
           "reference_file": ref_path,
           "mesh_log_candidates": cands,
           "n_mesh_log_candidates": len(cands),
           "mesh_log_selected": None,
           "note": ("the standard defines np-invariance ON THE SAME MESH; this item "
                    "regenerates the mesh, so identity is asserted, not assumed")}

    def reader_refusal(reason):
        out["verdict"] = "NOT A RESULT"
        out["cause_class"] = "READER_CONDITION_NOT_A_MESH_FINDING"
        out["reason"] = reason
        return out

    if len(cands) > 1:
        return reader_refusal(
            "MESH_LOG_SELECTION_IS_AMBIGUOUS -- READER CONDITION, NOT A MESH FINDING: "
            "%d files match MESH_*.log in this run root (%s).  THIS COMPARATOR REFUSES "
            "TO PICK ONE: a multi-member set reduced to one member by an ordering that "
            "is not the physics' ordering is a FINDING, not something to resolve by "
            "sorting" % (len(cands), ", ".join(os.path.basename(c) for c in cands)))
    mine_src = cands[0] if cands else None
    mine_txt = ""
    if mine_src and os.path.isfile(mine_src):
        out["mesh_log_selected"] = mine_src
        mine_txt = open(mine_src, errors="replace").read()
    elif os.path.isfile(mine_log):
        out["mesh_log_selected"] = mine_log
        mine_txt = open(mine_log, errors="replace").read()
    mine = _points_sha(mine_txt)
    ref_txt = open(ref_path, errors="replace").read() if os.path.isfile(ref_path) else ""
    ref = _points_sha(ref_txt)
    out["this_item_points_sha256"] = mine
    out["so1b_points_sha256"] = ref
    out["n_this_item_sha"] = len(mine)
    out["n_reference_sha"] = len(ref)
    if not mine:
        out["verdict"] = "NOT A RESULT"
        out["reason"] = "THIS_ITEM_PRINTED_NO_POINTS_SHA256"
        return out
    if not ref:
        out["verdict"] = "NOT A RESULT"
        out["reason"] = ("SO1B_MESH_FINGERPRINT_ABSENT -- mesh identity is a PHYSICS "
                         "precondition of this comparison, so an unknown reference is "
                         "NOT A RESULT, never a pass")
        return out
    if len(mine) != 1:
        return reader_refusal(
            "THIS_ITEM_PRINTED_%d_DISTINCT_POINTS_SHA256 -- READER CONDITION, NOT A MESH "
            "FINDING: %s names more than one mesh, so there is no single 'this item's "
            "mesh' to compare and the comparator REFUSES rather than choose one"
            % (len(mine), out["mesh_log_selected"]))
    if len(ref) != 1:
        return reader_refusal(
            "SO1B_REFERENCE_CARRIES_%d_DISTINCT_POINTS_SHA256 -- READER CONDITION, NOT A "
            "MESH FINDING: %s names more than one mesh.  THIS IS THE CASE THE DRIVER'S "
            "`head -4` USED TO MANUFACTURE, and before AMENDMENT R6 it published under "
            "this gate's mesh-regeneration-determinism sentence -- a reader defect wearing "
            "a physics finding.  THAT SENTENCE IS DELIBERATELY NOT REPEATED HERE, not even "
            "to explain itself: a downstream reader greps the reason string" % (len(ref), ref_path))
    out["verdict"] = "PASS" if set(mine) == set(ref) else "GATE FAIL"
    if out["verdict"] == "GATE FAIL":
        out["cause_class"] = "MESH_FINDING"
        out["reason"] = ("MESH_REGENERATION_IS_NOT_DETERMINISTIC -- the two runs did not "
                         "produce the same mesh, so 'the same mesh' does not hold and the "
                         "np-invariance comparison is not the one the standard defines")
    return out


def g_clock(rows):
    """G-CLOCK reports both frames and their measured difference.  It renders NO
    verdict of its own: the cap gate reads the CONTAINER frame (G10) and the cost
    claim reads the HOST frame, and this block exists so the gap is a MEASUREMENT
    in the record rather than an estimate in a comment."""
    out = {"per_arm": {}, "not_measured": [],
           "gate_frame": "CONTAINER (docker .State.StartedAt/.FinishedAt)",
           "cost_frame": "HOST (wall bracketed around `docker run` + poll granularity)",
           "why": ("an in-container `timeout` deadline enforced at CAP*60/ranks records a "
                   "HOST wall above the cap by the container start plus up to one poll "
                   "interval; grading that in the host frame manufactures a GATE FAIL the "
                   "run did not earn.  The cap is NOT widened to absorb it.")}
    deltas = []
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        h, c = r.get("core_min"), r.get("core_min_container")
        d = None if (h is None or c is None) else round(h - c, 3)
        if c is None:
            out["not_measured"].append(arm)
        if d is not None:
            deltas.append(d)
        out["per_arm"][arm] = {"host_core_min": h if h is not None else NOT_MEASURED,
                               "container_core_min": c if c is not None else NOT_MEASURED,
                               "delta_core_min": d if d is not None else NOT_MEASURED,
                               "ranks": ARM_RANKS[arm]}
    out["max_delta_core_min"] = max(deltas) if deltas else NOT_MEASURED
    out["sum_delta_core_min"] = round(sum(deltas), 3) if deltas else NOT_MEASURED
    return out


# ================= G9 / G10 / G12 ======================================================
def g_toolchain(rows, meta_by_arm):
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
    # ---- G-ROWX ACROSS THE ITEM BOUNDARY: the two arms of one row must share a
    # ---- library hash, and it must be the hash of the SO-1b artefact they read.
    # ---- A row is an image hash, never a directory name.
    for rk, arms in ROW_ARMS.items():
        hashes = {a: (meta_by_arm.get(a) or {}).get("so_md5") for a in arms}
        want = SO_MD5[ARM_ROW[arms[0]]]
        out["per_arm"].setdefault("_G-ROWX_%s" % rk, {})
        out["per_arm"]["_G-ROWX_%s" % rk] = {"arms": hashes, "registered": want,
                                             "ok": all(h == want for h in hashes.values())}
        if not out["per_arm"]["_G-ROWX_%s" % rk]["ok"]:
            out["verdict"] = "GATE FAIL"
    return out


def g_caps(rows):
    """G10 GRADES THE CONTAINER FRAME, WHICH IS THE FRAME THE CAP IS ENFORCED IN
    (G-CLOCK).  The HOST frame is carried beside it as the COST claim -- it is the
    larger figure and the honest one for occupancy -- and is NEVER the limb.  When
    the container clock is unreadable the gate FALLS BACK TO THE HOST FRAME AND
    SAYS SO: a limb that could not be evaluated in its own frame is reported, not
    passed."""
    out = {"per_arm": {}, "verdict": "PASS",
           "total_core_min_host_COST": 0.0, "total_core_min_container_GATE": 0.0,
           "ceiling": ITEM_CEILING_CORE_MIN, "not_measured": [], "frame_fallbacks": []}
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        host = r.get("core_min")
        cont = r.get("core_min_container")
        if host is None and cont is None:
            out["not_measured"].append(arm)
            out["per_arm"][arm] = {"core_min_host": NOT_MEASURED, "core_min_container": NOT_MEASURED,
                                   "cap": CAPS[arm]}
            continue
        if cont is None:
            gate_value, frame = host, "HOST_FALLBACK"
            out["frame_fallbacks"].append(arm)
        else:
            gate_value, frame = cont, "CONTAINER"
        if host is not None:
            out["total_core_min_host_COST"] += host
        out["total_core_min_container_GATE"] += gate_value
        crossed = gate_value > CAPS[arm]
        out["per_arm"][arm] = {
            "core_min_host": host if host is not None else NOT_MEASURED,
            "core_min_container": cont if cont is not None else NOT_MEASURED,
            "gate_value": gate_value, "gate_frame": frame, "cap": CAPS[arm], "crossed": crossed,
            "ratio_actual_over_predicted": (round(host / PREDICTED_CORE_MIN[arm], 4)
                                            if host is not None else NOT_MEASURED)}
        if crossed:
            out["verdict"] = "GATE FAIL"
    if out["total_core_min_container_GATE"] > ITEM_CEILING_CORE_MIN:
        out["verdict"] = "GATE FAIL"
    return out


def g_placement(rows):
    out = {"per_arm": {}, "verdict": "PASS", "not_measured": []}
    for arm in ARMS_REQUIRED:
        r = rows[arm]
        cs_ok = r.get("cpuset") == CPUSET_REGISTERED[arm]
        d = r.get("delivered")
        dl = None
        m = re.match(r"\s*([\d.]+)\s+n=(\d+)", d or "")
        if m:
            dl = float(m.group(1))
        if dl is None:
            out["not_measured"].append(arm)
        # AT np = 4 THE DELIVERED-CORES FLOOR APPLIES.  SO-1a and SO-1b ran every
        # arm at np = 1, where it does not; this item is the first in the ladder
        # where an overlapping cpuset could cost RANKS rather than only wall time,
        # which is why 10-13 is disjoint from every registered sibling placement.
        dl_ok = True if (dl is None or ARM_RANKS[arm] == 1) else dl >= DELIVERED_CORES_FLOOR
        out["per_arm"][arm] = {"cpuset": r.get("cpuset"), "registered": CPUSET_REGISTERED[arm],
                               "ranks": ARM_RANKS[arm],
                               "delivered_cores_mean": (dl if dl is not None else NOT_MEASURED),
                               "floor_applies": ARM_RANKS[arm] > 1,
                               "floor": DELIVERED_CORES_FLOOR}
        if not (cs_ok and dl_ok):
            out["verdict"] = "GATE FAIL"
    return out


def compose_arm(g_np, g_sj, g_cd, g_cl, g_tb):
    """PER-ARM COMPOSITION.  G-TB can only turn a PASS or a GATE FAIL INTO NOT A
    RESULT, never the reverse -- the standing-rule-5 direction applied to the
    trivial baseline.  G-NP and G5N are peers: an arm is PASS only if its gradient
    is BOTH decomposition-invariant AND FD-verified at its own np, because AV-1's
    own section 8 records that G-NP alone can be passed by a gradient that is
    equally wrong at every np (L-38)."""
    if g_tb is not None and g_tb["verdict"] == "GATE FAIL":
        return "NOT A RESULT"
    vs = (g_np["verdict"], g_sj["verdict"], g_cd["verdict"], g_cl["verdict"])
    if "NOT A RESULT" in vs:
        return "NOT A RESULT"
    if "GATE FAIL" in vs:
        return "GATE FAIL"
    return "PASS"


def compose_row(arm_verdicts, method_verdict):
    vs = list(arm_verdicts) + [method_verdict]
    if "NOT A RESULT" in vs:
        return "NOT A RESULT"
    if "GATE FAIL" in vs:
        return "GATE FAIL"
    return "PASS"
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


# ================= the grade ==========================================================
def grade(root):
    rows = read_ledger(os.path.join(root, "ledger.txt"))
    g1 = g_completion(root, rows)
    # ---- MESH identity, on TWO channels: the cell count, and the mesh's own
    # ---- fingerprint against SO-1b's.  The standard defines this comparison "on
    # ---- the same mesh", so a matching cell count is necessary and not sufficient.
    cm_txt = open(os.path.join(root, "MESH", "checkMesh.log"), errors="replace").read()
    m = re.search(r"^\s*cells:\s+(\d+)", cm_txt, re.M)
    if not m:
        refuse("G-M2", {"cells_absent_in_checkMesh": True})
    cells = int(m.group(1))
    gm2 = "PASS" if cells == CELLS_EXPECTED else "GATE FAIL"
    gmeshid = g_meshid(root)

    # ---- the four np = 4 arms
    N, meta_by_arm = {}, {}
    for arm in ARMS_SOLVER:
        X, F, meta = read_N(os.path.join(root, arm, ARTEFACT[arm]))
        N[arm] = (X, F, meta)
        meta_by_arm[arm] = meta
        rows[arm]["artefact_so_md5"] = meta["so_md5"]

    gdecomp = {arm: g_decomp(N[arm][2], arm) for arm in ARMS_SOLVER}
    gxstar = {arm: g_xstar(root, N[arm][2], arm) for arm in ARMS_SOLVER}

    controls = {}
    for arm in ARMS_SOLVER:
        controls[arm] = ctrl_control(N[arm][1])
    controls["grader_plant_Ns-P"] = grader_plant_control(root, os.path.join(root, "Ns-P", ARTEFACT["Ns-P"]), "Ns-P")
    controls["grader_plant_Ni-S"] = grader_plant_control(root, os.path.join(root, "Ni-S", ARTEFACT["Ni-S"]), "Ni-S")
    controls["grader_np_plant_Ns-P"] = grader_np_control(root, os.path.join(root, "Ns-P", ARTEFACT["Ns-P"]), "Ns-P")

    # ---- the SERIAL SCALARS at x*, read INDEPENDENTLY of the instrument.  The
    # ---- instrument carried the np = 1 gradient forward; this comparator reads the
    # ---- SAME SOURCE itself, and a disagreement between the two channels REFUSES.
    ref_scalars, ref_grad = {}, {}
    for rk, row_name in (("P", "PATCHED"), ("S", "SHIPPED")):
        src = os.path.join(root, "optref", row_name, "so1b_E.json")
        if not os.path.isfile(src):
            refuse("G-NP", {"staged_serial_reference_absent": src})
        j = json.load(open(src))
        ref_scalars[rk] = {"CD": float(j["CD_baseline"]), "CL": float(j["CL_baseline"])}
        ref_grad[rk] = {of: {dv: [float(v) for v in j["adjoint"][of][dv]]
                             for dv in ("shape", "patchV")} for of in ("CD", "CL")}
    for arm in ARMS_SOLVER:
        rk = ARM_ROWKEY[arm]
        carried = N[arm][2]["np1_reference"]
        for of in ("CD", "CL"):
            for dv in ("shape", "patchV"):
                a = [repr(v) for v in carried[of][dv]]
                b = [repr(v) for v in ref_grad[rk][of][dv]]
                if a != b:
                    refuse("G-NP", {"channel_disagreement": True, "arm": arm, "of": of, "dv": dv,
                                    "instrument_carried": a, "comparator_read": b,
                                    "note": "the instrument's copy of the serial reference and "
                                            "the comparator's own read of the same file DISAGREE"})

    gnp = {arm: g_npinv(N[arm][0], N[arm][2], arm) for arm in ARMS_SOLVER}
    gsj = {arm: g_objective_spread(N[arm][0], ref_scalars[ARM_ROWKEY[arm]], arm) for arm in ARMS_SOLVER}
    g5cd = {arm: grade_components(N[arm][0], N[arm][1], "CD") for arm in ARMS_SOLVER}
    g5cl = {arm: grade_components(N[arm][0], N[arm][1], "CL") for arm in ARMS_SOLVER}
    gtb = {arm: grade_tb(N[arm][0], N[arm][1], "CD") for arm in ARMS_SOLVER}
    gmethod = {rk: g_method(N, rk) for rk in ("P", "S")}

    arm_verdict = {arm: compose_arm(gnp[arm], gsj[arm], g5cd[arm], g5cl[arm], gtb[arm])
                   for arm in ARMS_SOLVER}
    row_verdict = {rk: compose_row([arm_verdict[a] for a in ROW_ARMS[rk]], gmethod[rk]["verdict"])
                   for rk in ("P", "S")}

    g9 = g_toolchain(rows, meta_by_arm)
    g10 = g_caps(rows)
    g12 = g_placement(rows)
    gclock = g_clock(rows)

    # ---- DIVERGENCE shipped-vs-patched at fixed decomposition: REPORTED with its
    # ---- number, per component, and NEVER gated.  W-2: an identity may be
    # ---- reported and never gated on.
    div = []
    for decomp, (a_arm, b_arm) in (("scotch", ("Ns-S", "Ns-P")), ("simple", ("Ni-S", "Ni-P"))):
        for dv, idx in COMPONENTS_REGISTERED:
            a = N[a_arm][0]["adjoint"]["CD"][dv]
            b = N[b_arm][0]["adjoint"]["CD"][dv]
            if idx < len(a) and idx < len(b):
                den = max(abs(a[idx]), abs(b[idx]), 1e-300)
                div.append({"decomposition": decomp, "dv": dv, "idx": idx,
                            "J_shipped": a[idx], "J_patched": b[idx],
                            "divergence_pct": abs(a[idx] - b[idx]) / den * 100.0})

    # ---- PREDICTIONS, scored mechanically, never adjusted -----------------------
    preds = {"P_A_cells_4032": "HIT" if gm2 == "PASS" else "MISS",
             "P_MESHID_same_mesh_as_SO1b": ("HIT" if gmeshid["verdict"] == "PASS"
                                            else (NOT_MEASURED if gmeshid["verdict"] == "NOT A RESULT"
                                                  else "MISS"))}
    # P-1: the SCOTCH arms are PREDICTED OUTSIDE the band on at least one row.
    scotch_fail = [a for a in ("Ns-P", "Ns-S") if gnp[a]["verdict"] == "GATE FAIL"]
    scotch_nar = [a for a in ("Ns-P", "Ns-S") if gnp[a]["verdict"] == "NOT A RESULT"]
    preds["P_1_scotch_outside_s_g_band_on_at_least_one_row"] = (
        NOT_MEASURED if scotch_nar else ("HIT" if scotch_fail else "MISS"))
    # P-2: the SIMPLE arms are PREDICTED INSIDE the band on BOTH rows.
    simple_v = [gnp[a]["verdict"] for a in ("Ni-P", "Ni-S")]
    preds["P_2_simple_4x1x1_inside_s_g_band_on_both_rows"] = (
        NOT_MEASURED if "NOT A RESULT" in simple_v else ("HIT" if set(simple_v) == {"PASS"} else "MISS"))
    # P-4: shape[6] -- the LE component -- carries the largest per-component share
    # of the scotch disagreement.  idx6 carries 82.7 % of A1's squared-error norm.
    def _worst_component(arm):
        pc = (gnp[arm]["per_objective"].get("CD") or {}).get("per_component") or []
        if not pc:
            return None
        return max(pc, key=lambda c: c["abs_rel_diff"])
    w6 = [_worst_component(a) for a in ("Ns-P", "Ns-S")]
    preds["P_4_shape6_is_the_largest_scotch_component"] = (
        NOT_MEASURED if any(w is None for w in w6)
        else ("HIT" if all(w["dv"] == "shape" and w["idx"] == 6 for w in w6) else "MISS"))
    # P-5: the OBJECTIVE stays inside its own far tighter band on every arm.
    sjv = [gsj[a]["verdict"] for a in ARMS_SOLVER]
    preds["P_5_objective_inside_s_J_band_on_every_arm"] = "HIT" if set(sjv) == {"PASS"} else "MISS"
    # P-6: the PATCHED SIMPLE arm is FD-verified; the PATCHED SCOTCH arm is not.
    pi, ps = g5cd["Ni-P"], g5cd["Ns-P"]
    preds["P_6_patched_simple_FD_PASS_and_patched_scotch_NOT"] = (
        NOT_MEASURED if "NOT A RESULT" in (pi["verdict"], ps["verdict"])
        else ("HIT" if (pi["verdict"] == "PASS" and pi["n_pass"] >= PRED["P_min_pass_components"]
                        and ps["verdict"] != "PASS") else "MISS"))
    # P-7: the SHIPPED rows fail band D at shape[6] at BOTH decompositions.
    def _c6(arm):
        c = [x for x in g5cd[arm]["components"] if x["dv"] == "shape" and x["idx"] == 6]
        return c[0] if c else None
    s6 = [_c6("Ns-S"), _c6("Ni-S")]
    preds["P_7_shipped_shape6_outside_band_D_at_both_decompositions"] = (
        NOT_MEASURED if any(c is None or c.get("verdict") == "NOT A RESULT" for c in s6)
        else ("HIT" if all(c["verdict"] == "GATE FAIL" for c in s6) else "MISS"))
    # P-TB: the trivial baseline FAILS on at least 4 of 5 on every arm.
    tb_fail_ok = all((len(COMPONENTS_REGISTERED) - gtb[a]["n_passing_band_D_at_the_WRONG_step"])
                     >= PRED["P_tb_min_failing"] for a in ARMS_SOLVER)
    preds["P_TB_trivial_baseline_fails_ge4_of_5_on_every_arm"] = "HIT" if tb_fail_ok else "MISS"
    # P-I: the item's total cost, on the COST frame (host), inside the band.
    if g10["not_measured"]:
        preds["P_I_total_core_min_band"] = NOT_MEASURED
    else:
        tot = g10["total_core_min_host_COST"]
        preds["P_I_total_core_min_band"] = ("HIT" if PRED["PI_core_min_band"][0] <= tot <= PRED["PI_core_min_band"][1]
                                            else "MISS")
    mw = rows["MESH"].get("wall_s")
    preds["P_mesh_wall_le_120s"] = NOT_MEASURED if mw is None else (
        "HIT" if mw <= PRED["P_mesh_wall_s_max"] else "MISS")
    # P-CLOCK: the HOST frame exceeds the CONTAINER frame on every arm, and the
    # margin is the family's FIRST MEASUREMENT of the gap rather than an estimate.
    deltas = [v["delta_core_min"] for v in gclock["per_arm"].values()
              if v["delta_core_min"] != NOT_MEASURED]
    preds["P_CLOCK_host_frame_exceeds_container_frame_on_every_arm"] = (
        NOT_MEASURED if len(deltas) < len(ARMS_REQUIRED) else ("HIT" if all(d >= 0 for d in deltas) else "MISS"))
    # P-3: THE DESIGN-POINT CLAIM -- the rung's own reason.  It is scored against
    # AV-1R's BASELINE np-invariance number, which may not exist.  REGISTERED NOW
    # so an absent reference cannot later become a silent pass: it reads
    # NOT_MEASURED with the reason named, and is NEVER inferred from anything else.
    preds["P_3_s_g_larger_at_the_optimum_than_at_the_baseline"] = NOT_MEASURED
    p3_note = ("AV-1R's baseline np-invariance figure is the comparison basis and is "
               "NOT read by this comparator: AV-1R is a separate registration whose "
               "grade artefact lives in its own run root, and this item does not "
               "depend on it.  The number needed is `s_g(np=4 scotch)` at the "
               "BASELINE, per row.  It is reported beside this item's optimum figure "
               "by hand at closure, or the prediction stands NOT_MEASURED.  It is "
               "REGISTERED as NOT_MEASURED here so an absent reference cannot become "
               "a silent HIT.")

    # ---- ITEM VERDICT, composition registered here ------------------------------
    vs = (row_verdict["P"], row_verdict["S"])
    if "NOT A RESULT" in vs or gmeshid["verdict"] == "NOT A RESULT":
        verdict = "NOT A RESULT"
    elif ("GATE FAIL" in vs
          or "GATE FAIL" in (gm2, gmeshid["verdict"], g9["verdict"], g10["verdict"], g12["verdict"])):
        verdict = "GATE FAIL"
    else:
        verdict = "PASS"
    if verdict not in VOCAB:
        refuse("VOCAB", {"verdict": verdict})

    return {
        "item": "CURRICULUM-%s" % ITEM, "verdict": verdict,
        "rows": {"PATCHED": row_verdict["P"], "SHIPPED": row_verdict["S"]},
        "arms": {a: arm_verdict[a] for a in ARMS_SOLVER},
        "gates": {
            "G1_completion": "PASS",
            "G-M2_mesh_identity": gm2,
            "G-MESHID_same_mesh_as_SO1b": gmeshid,
            "G-DECOMP": gdecomp,
            "G-XSTAR": gxstar,
            "G-NP_np_invariance_at_the_optimum": gnp,
            "G-NP_objective_spread": gsj,
            "G-METHOD_scotch_vs_simple_at_fixed_np4": gmethod,
            "G5N_CD": g5cd, "G5cN_CL": g5cl, "G_TB_trivial_baseline": gtb,
            "G-CLOCK_two_frames": gclock,
            "G6_dot_product_duality": ("NOT MEASURED -- the tutorial exposes no "
                                       "dot-product/duality test and AV-2 measured forward-AD "
                                       "seeding FAILING the primal on this exact case on BOTH "
                                       "images; named, never composed"),
            "G9_toolchain": g9, "G10_caps": g10, "G12_placement": g12},
        "band_provenance": {
            "s_g": ("1.0e-3 -- ADJOINT_VERIFICATION_STANDARD.md section 3 band table, "
                    "inherited BY CITATION, 6x B3's measured 1.1-1.7e-4 floor and 50x "
                    "TIGHTER than band D; reaching for band D here would have registered "
                    "a gate 50x too loose to see A4's measured 8.95e-2"),
            "s_J": "2.2e-5 -- PARALLEL_GATE_DOCTRINE.md:38, :194-198, same source",
            "band_D_E_plateau": ("5.0 / 5.0 / 10.0 -- curriculum_D4/PREREGISTRATION.md:82 and "
                                 "D7FR:228-229 via SO-1a and SO-1b, byte-identical, not re-derived")},
        "mesh_cells": cells,
        "divergence_shipped_vs_patched_CD_at_fixed_decomposition": div,
        "predictions": preds, "P_3_note": p3_note,
        "controls": controls, "completion": g1,
        "cost": {"frame": "HOST -- the box is occupied for the host wall, so the COST claim "
                          "uses it and it is the LARGER of the two frames",
                 "total_core_min": g10["total_core_min_host_COST"],
                 "gate_frame_total_core_min": g10["total_core_min_container_GATE"],
                 "dollars_note": ("dollars are DERIVED at $0.0513/core-h REPORTED-BY-OWNER and "
                                  "are never called measured: the box cannot read its own "
                                  "billing (COMPUTE_BUDGET_CHARTER.md section 5)")},
        "not_measured": {"G1": g1["not_measured"], "G10": g10["not_measured"],
                         "G12": g12["not_measured"], "G-CLOCK": gclock["not_measured"]},
        "field_classes": {"physics": list(FIELDS_PHYSICS), "infrastructure": list(FIELDS_INFRASTRUCTURE),
                          "rule": "absent infrastructure -> NOT_MEASURED beside the verdict; "
                                  "absent physics -> REFUSE (L-342), as amended by R-RC"},
        "staged_inputs_excluded_from_the_age_guard": list(STAGED_INPUTS),
        "no_gci": "no grid family; standing rule 5 has no row; NO GCI IS QUOTED",
        "no_improvement_percentage": ("this item quotes NO improvement percentage, so G-D7R has "
                                      "no row here; and NOTHING here lifts SO-1b's own "
                                      "SUPPRESSED_BY_G_D7R -- only SO-1b's attribution artefact can"),
        "age_datum_resolution": g1["datum_resolution"],
        "rule4_clauses_per_arm": g1["rule4_clauses"],
        "rc_inferences": g1["rc_inferences"],
        "capability_grid_cell": (
            "2D . steady . incompressible -- gradients computed + FD-verified, np-INVARIANCE "
            "column.  AV-1/AV-1R supply the np sweep at fixed `scotch` and carry NO FD table, "
            "so by their own section 8 they move no grid verdict.  THIS item varies the "
            "decomposition METHOD at fixed np -- the other half of the standard's own section 3 "
            "definition -- AT AN OPTIMUM rather than a baseline, and buys an FD table at np = 4, "
            "which is what makes it a verdict rather than a spot check (L-38: "
            "decomposition-invariance is not correctness)"),
    }
# ================= selftest: planted fixtures, counted against a FROZEN unit count ======
ROWFMT = ("ARM={arm} ROW={row} DECOMP={dec} IMG={img} DIGEST={dig} rc={rc} wall_s={wall} "
          "container_wall_s={cwall} ranks={ranks} core_min={cm} core_min_container={cmc} "
          "clock_frame_delta_core_min={cd} cap_core_min={cap} enforced_wall_s=450 "
          "enforced_core_min={cap} memory=6g inspect(exit,oomkilled)=[{ke} {oom}] "
          "memavail_pre_GiB=20.00 memavail_post_GiB={mpost} cpuset={cs} delivered_cores_mean=[{dl}] "
          "siblings_pre=[] siblings_post=[] log={log} stamp=x\n")

# The np = 1 SERIAL REFERENCE the fixture writes into `optref/<ROW>/so1b_E.json`.
# Every arm's np = 4 gradient is built FROM this by a per-arm perturbation, so the
# fixture's np-invariance is a knob and not an accident.
J_REF = {"shape": [-0.011, 0.02, -0.03, 0.041, 0.05, -0.06, 0.007, -0.008],
         "patchV": [0.0, 0.0123]}
XSTAR = {"shape": [repr(0.001 * (i + 1)) for i in range(8)],
         "patchV": [repr(10.0), repr(1.13)]}


def _fix(tmp, tweak=None):
    """Build a clean fixture; `tweak` mutates the dict of knobs before writing.

    ONE KNOB PER NEW GUARD, so every guard this comparator adds is DRIVEN to fire
    rather than asserted to exist (Sanaa 2026-08-27 section 1; the L-314 standard):
      `np_err`     arm -> relative perturbation of the np = 4 gradient  -- G-NP
      `np_flip`    arm -> set of flat indices sign-flipped               -- G-NP
      `sj_err`     arm -> relative perturbation of CD/CL at the optimum  -- s_J
      `method`     arm -> extra perturbation applied to `simple` only    -- G-METHOD
      `decomp`     arm -> method name written into the artefact          -- G-DECOMP
      `nprocs`     arm -> nprocs written into the artefact               -- G-DECOMP
      `simple_n`   the subdivision written for the `simple` arms         -- G-DECOMP
      `xstar`      arm -> a design point that differs from SO-1b's       -- G-XSTAR
      `meshsha`    "same" | "differ" | "absent"                          -- G-MESHID
      `cmc`        arm -> container-frame core-min (None = NOT_MEASURED) -- G-CLOCK / G10
      `ref_np`     the nprocs written into the STAGED reference          -- G-NP
      `carried`    arm -> perturbation of the CARRIED reference only     -- G-NP channels
      `staged_stale` arms whose STAGED so1b_E.json is OLDER than the datum -- the
                   D4S-F3S class: a staged input must never be age-checked
    plus SO-1a's inherited knobs (datum / rc_record / fatal / tb_pass / err / flip /
    noplateau / stale / ctrl_ok / drop_row / inspect_file / cells / cs / so / cm).
    """
    k = {"rc": {a: 0 for a in ARMS_REQUIRED}, "ke": {}, "oom": {a: "false" for a in ARMS_REQUIRED},
         "cm": dict(PREDICTED_CORE_MIN),
         # THE CONTAINER FRAME IS SMALLER THAN THE HOST FRAME BY CONSTRUCTION in the
         # clean fixture, which is the physical truth the G-CLOCK block records: the
         # host wall brackets the container start and the poller's granularity ON TOP
         # of the container's own life.  3 % is the fixture's stand-in for that gap.
         "cmc": {a: round(PREDICTED_CORE_MIN[a] * 0.97, 3) for a in ARMS_REQUIRED},
         "cs": {a: CPUSET_REGISTERED[a] for a in ARMS_REQUIRED},
         "so": {a: SO_MD5[ARM_ROW[a]] for a in ARMS_REQUIRED}, "cells": CELLS_EXPECTED,
         "err": {a: {} for a in ARMS_SOLVER}, "err_cl": {a: {} for a in ARMS_SOLVER},
         "flip": {a: set() for a in ARMS_SOLVER}, "noplateau": {a: set() for a in ARMS_SOLVER},
         "tb_pass": {a: set() for a in ARMS_SOLVER},
         "np_err": {a: 0.0 for a in ARMS_SOLVER}, "np_flip": {a: set() for a in ARMS_SOLVER},
         "sj_err": {a: 0.0 for a in ARMS_SOLVER},
         "decomp": {a: ARM_DECOMP[a] for a in ARMS_SOLVER},
         "nprocs": {a: REGISTERED_NPROCS for a in ARMS_SOLVER},
         "simple_n": list(DECOMP_SIMPLE_N),
         "xstar": {}, "carried": {a: 0.0 for a in ARMS_SOLVER}, "ref_np": 1,
         "meshsha": "same", "staged_stale": set(),
         # ---- AMENDMENT R6 knobs.  ONE KNOB PER NEW REFUSAL. ------------------
         # `cm_extra`      text PREPENDED to the MESH arm's checkMesh.log  -- C5
         # `dup_mesh_log`  a SECOND MESH_*.log in the run root             -- G-MESHID
         # `ref_dup`       a SECOND distinct sha in SO-1b's fingerprint    -- G-MESHID
         "cm_extra": "", "dup_mesh_log": False, "ref_dup": False,
         # ---- SO-1cR REPAIR 3 of 3, BREAK 6 CALL SITE (4) -- THE FIXTURE ITSELF.
         # SO-1c's fixture wrote the staged optref artefact with the FULL row name
         # ("PATCHED"/"SHIPPED").  THE REAL PRODUCER, SO-1bR, WRITES THE DIRECTORY
         # SUFFIX ('P'/'S') -- verified on disk at
         # CURRICULUM-SO1bR-.../E-P/so1b_E.json row='P' and E-S/... row='S'.
         # So G-XSTAR's row limb was only ever exercised against a label the real
         # world does not produce: the leg was GREEN IN FIXTURE AND WOULD HAVE
         # REFUSED IN PRODUCTION.  A fixture that disagrees with its producer does
         # not merely fail to catch the break -- it CONCEALS it, and that is why
         # 53 green units saw nothing.
         # The default is now the PRODUCTION label.  The knob drives the other
         # registered label, and BOTH SWAP DIRECTIONS, and an unregistered label.
         #   "produced"   -> 'P' / 'S'            (what SO-1bR actually writes)
         #   "fullname"   -> 'PATCHED'/'SHIPPED'  (also registered; must PASS)
         #   "swapped"    -> the OTHER row's produced label; must REFUSE
         #   "swapped_full" -> the OTHER row's full name; must REFUSE
         #   any other string -> written verbatim; an unregistered label must REFUSE
         "optref_row_label": "produced",
         "terminal": {a: True for a in ARMS_REQUIRED}, "stale": set(), "ctrl_ok": True,
         "mpost": "20.00", "drop_row": set(), "inspect_file": set(), "rc_record": set(),
         "fatal": {},
         "datum": {a: ("plain" if a == "MESH" else "gz") for a in ARMS_REQUIRED},
         "write_compression": "on",
         "dl": "3.90 n=10 max_nr_throttled=0", "CL": 0.50, "CD": 0.01753}
    if tweak:
        tweak(k)
    root = os.path.join(tmp, "root_%d" % int(time.time() * 1e6))
    os.makedirs(root)

    # ---- the STAGED INPUTS from SO-1b, in this item's own run root -------------
    OTHER_ROW = {"PATCHED": "SHIPPED", "SHIPPED": "PATCHED"}
    for rowname in ("PATCHED", "SHIPPED"):
        od = os.path.join(root, "optref", rowname)
        os.makedirs(od)
        # SO-1cR: the label the fixture writes is now the PRODUCER'S label by
        # default, and the knob drives both swap directions.  See the knob comment.
        _lab = k["optref_row_label"]
        if _lab == "produced":
            row_label = ROW_LABELS[rowname][1]
        elif _lab == "fullname":
            row_label = ROW_LABELS[rowname][0]
        elif _lab == "swapped":
            row_label = ROW_LABELS[OTHER_ROW[rowname]][1]
        elif _lab == "swapped_full":
            row_label = ROW_LABELS[OTHER_ROW[rowname]][0]
        else:
            row_label = _lab
        adj = {"CD": {dv: [repr(v) for v in J_REF[dv]] for dv in J_REF},
               "CL": {dv: [repr(v * 10.0) for v in J_REF[dv]] for dv in J_REF}}
        json.dump({"item": "SO1b", "mode": "E", "row": row_label,
                   "nprocs": k["ref_np"],
                   "identity": {"libidwarp_so_md5": SO_MD5[rowname]},
                   "design_point": {dv: list(XSTAR[dv]) for dv in XSTAR},
                   "adjoint": adj,
                   "CD_baseline": repr(k["CD"]), "CL_baseline": repr(k["CL"])},
                  open(os.path.join(od, "so1b_E.json"), "w"))
    mesh_sha = "a" * 64
    ref_sha = mesh_sha if k["meshsha"] == "same" else ("b" * 64)
    if k["meshsha"] != "absent":
        _ref_lines = "%s  constant/polyMesh/points\n" % ref_sha
        if k["ref_dup"]:
            # WHAT THE DRIVER'S `head -4` USED TO PRODUCE when SO-1b's root held
            # more than one MESH_*.log: a reference naming TWO meshes.
            _ref_lines += "%s  constant/polyMesh/points\n" % ("d" * 64)
        open(os.path.join(root, "optref", "so1b_mesh_points_sha256.txt"), "w").write(
            _ref_lines)
    else:
        open(os.path.join(root, "optref", "so1b_mesh_points_sha256.txt"), "w").write("")

    led = ["ITEM=SO1cR\n", "STAGED stamp=x\n"]
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
        text = "D4S_CONTAINER_UID: 0\nD4S_IDWARP_SO_MD5: %s\nD4S_DEADLINE_IN_CONTAINER_S: 450\n" % so
        if arm == "MESH":
            art = os.path.join(d, "checkMesh.log")
            open(art, "w").write(
                k["cm_extra"]
                + "Mesh stats\n    cells:            %d\n\nMesh OK.\n" % k["cells"])
            text += "SO1CR_CHECKMESH_RC 0\n%s  constant/polyMesh/points\n" % mesh_sha
        else:
            art = os.path.join(d, ARTEFACT[arm])
            ident = {"libidwarp_so_md5": so, "idwarp_file": "/x/idwarp/__init__.py",
                     "write_compression": k["write_compression"]}
            # ---- THE STAGED INPUT, written into the arm directory.  Its mtime is
            # deliberately OLDER than the age datum on the default path, because
            # that is what `cp -a` of an input produces -- and the age guard must
            # STILL PASS, since a staged input is not in the age-checked list.
            sj = json.load(open(os.path.join(root, "optref", ARM_ROW[arm], "so1b_E.json")))
            json.dump(sj, open(os.path.join(d, "so1b_E.json"), "w"))
            os.utime(os.path.join(d, "so1b_E.json"), (t0 - 60, t0 - 60))
            # ---- the np = 4 gradient, built FROM the serial reference
            # The np = 4 gradient is the serial reference times (1 + np_err).  With
            # np_err = 0 on both arms of a row the two decompositions are identical
            # and G-METHOD reads zero; perturbing ONE arm moves BOTH the np axis and
            # the method axis, which is the physical truth and is what U13 drives.
            mul = 1.0 + k["np_err"][arm]
            J4 = {dv: [v * mul for v in J_REF[dv]] for dv in J_REF}
            flat_shape_n = len(J_REF["shape"])
            for fi in k["np_flip"][arm]:
                if fi < flat_shape_n:
                    J4["shape"][fi] = -J4["shape"][fi]
                else:
                    J4["patchV"][fi - flat_shape_n] = -J4["patchV"][fi - flat_shape_n]
            adj = {"CD": {dv: [repr(v) for v in J4[dv]] for dv in J4},
                   "CL": {dv: [repr(v * 10.0) for v in J4[dv]] for dv in J4}}
            ref_adj = {"CD": {dv: [repr(v * (1.0 + k["carried"][arm])) for v in J_REF[dv]] for dv in J_REF},
                       "CL": {dv: [repr(v * 10.0 * (1.0 + k["carried"][arm])) for v in J_REF[dv]] for dv in J_REF}}
            rows_ = []
            for dv, idx in COMPONENTS_REGISTERED:
                j = J4[dv][idx]
                e = k["err"][arm].get((dv, idx), 0.5)
                ecl = k["err_cl"][arm].get((dv, idx), 0.5)
                dref = j * (1.0 + e / 100.0)
                dref_cl = j * 10.0 * (1.0 + ecl / 100.0)
                if (dv, idx) in k["flip"][arm]:
                    dref = -dref
                fd = {}
                for s in STEPS_REGISTERED[dv]:
                    scale = 1.0 if s == sorted(STEPS_REGISTERED[dv])[1] else 1.01
                    if (dv, idx) in k["noplateau"][arm]:
                        scale = 1.0 if s == sorted(STEPS_REGISTERED[dv])[1] else 1.5
                    fd[repr(s)] = {"step": s, "ok": True, "dCD": repr(dref * scale),
                                   "dCL": repr(dref_cl * scale), "CD_plus": repr(0.0),
                                   "CD_minus": repr(0.0), "CL_plus": repr(0.0), "CL_minus": repr(0.0)}
                tbs = TB_STEPS_REGISTERED[dv][0]
                tbmul = 1.001 if (dv, idx) in k["tb_pass"][arm] else 3.0
                tb = {repr(tbs): {"step": tbs, "ok": True, "dCD": repr(j * tbmul),
                                  "dCL": repr(j * 10.0 * tbmul), "CD_plus": repr(0.0),
                                  "CD_minus": repr(0.0), "CL_plus": repr(0.0), "CL_minus": repr(0.0)}}
                rows_.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd, "tb": tb})
            planted = PLANT / (2.0 * CTRL_STEP) if k["ctrl_ok"] else 0.0
            rows_.append({"dv": "CTRL", "idx": 0, "status": "CONTROL",
                          "fd": {repr(CTRL_STEP): {"step": CTRL_STEP, "ok": True,
                                                   "dCD": repr(0.0), "dCL": repr(0.0)}},
                          "planted": {"step": CTRL_STEP, "plant": PLANT, "dCD": repr(planted), "ok": True}})
            dp = k["xstar"].get(arm) or {dv: list(XSTAR[dv]) for dv in XSTAR}
            decomp_rec = {"decomp_method": k["decomp"][arm],
                          "decomp_n_subdomains": k["nprocs"][arm],
                          "decomp_simple_n": (list(k["simple_n"]) if k["decomp"][arm] == "simple" else None),
                          "decomp_source": os.path.join(d, DECOMPDICT_REL)}
            # SO-1cR: the instrument PROPAGATES the staged artefact's own row label
            # (`so1cr_xn.py`: `row = opt["row"]`), so the fixture propagates it too
            # rather than substituting the full name.  A fixture that writes a label
            # its own producer never writes is what hid BREAK 6 for three amendments.
            json.dump({"item": "SO1cR", "mode": "N", "row": sj.get("row"), "identity": ident,
                       "nprocs": k["nprocs"][arm], "decomposition": decomp_rec,
                       "design_point": dp,
                       "components_requested": COMPONENTS_REGISTERED,
                       "steps": STEPS_REGISTERED, "tb_steps": TB_STEPS_REGISTERED,
                       "CD_optimum": repr(k["CD"] * (1.0 + k["sj_err"][arm])),
                       "CL_optimum": repr(k["CL"] * (1.0 + k["sj_err"][arm])),
                       "CD_optimum_repeat": repr(k["CD"]), "CL_optimum_repeat": repr(k["CL"]),
                       "eta_used": repr(1e-10),
                       "adjoint": adj, "adjoint_np1_reference": ref_adj,
                       "adjoint_np1_nprocs": k["ref_np"],
                       "adjoint_np1_source": os.path.join(root, "optref", ARM_ROW[arm], "so1b_E.json"),
                       "rows": rows_}, open(art, "w"))
            if k["terminal"][arm]:
                text += TERMINAL[arm] + " ok\n"
            text += "SO1CR_DECOMP method=%s n_subdomains=%s\n" % (k["decomp"][arm], k["nprocs"][arm])
        if arm in k["fatal"]:
            text += k["fatal"][arm] + "\n"
        os.utime(art, (t0 - 5, t0 - 5) if arm in k["stale"] else (t0 + 5, t0 + 5))
        open(os.path.join(root, log), "w").write(text)
        ke = NOT_MEASURED if arm in k["rc_record"] else k["ke"].get(arm, k["rc"][arm])
        cmc = k["cmc"][arm]
        cwall = NOT_MEASURED if cmc is None else round(cmc * 60.0 / ARM_RANKS[arm], 3)
        cmc_s = NOT_MEASURED if cmc is None else cmc
        cd_s = NOT_MEASURED if cmc is None else round(k["cm"][arm] - cmc, 3)
        if arm in k["inspect_file"]:
            open(os.path.join(root, "%s_x.inspect.txt" % arm), "w").write(
                "%s %s 2026-08-27T00:00:00Z 2026-08-27T00:01:00Z %s 6442450944 %s\n"
                % (ke, k["oom"][arm], k["cs"][arm], IMG_DIGEST[ARM_ROW[arm]]))
        if arm in k["drop_row"]:
            continue
        led.append(ROWFMT.format(arm=arm, row=ARM_ROW[arm], dec=ARM_DECOMP.get(arm, "scotch"),
                                 img="img", dig=IMG_DIGEST[ARM_ROW[arm]], rc=k["rc"][arm],
                                 wall=60, cwall=cwall, ranks=ARM_RANKS[arm], cm=k["cm"][arm],
                                 cmc=cmc_s, cd=cd_s, cap=CAPS[arm], ke=ke, oom=k["oom"][arm],
                                 mpost=k["mpost"], cs=k["cs"][arm], dl=k["dl"], log=log))
    if k["dup_mesh_log"]:
        # A SECOND `MESH_*.log` in the run root -- what a re-run of the MESH arm
        # leaves behind.  It carries a DIFFERENT points sha256, so the ambiguity is
        # MATERIAL: which file is read decides the G-MESHID verdict.
        open(os.path.join(root, "MESH_second.log"), "w").write(
            "SO1CR_CHECKMESH_RC 0\n%s  constant/polyMesh/points\n" % ("c" * 64))
    open(os.path.join(root, "ledger.txt"), "w").write("".join(led))
    return root


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

    here = os.path.dirname(os.path.abspath(__file__))

    # ---- the clean fixture ---------------------------------------------------
    r = grade(_fix(tmp))
    unit("U1 clean fixture -> item PASS; both rows PASS; every arm PASS",
         r["verdict"] == "PASS" and set(r["rows"].values()) == {"PASS"}
         and set(r["arms"].values()) == {"PASS"})
    unit("U2 clean fixture -> G-M2, G-MESHID, G-METHOD (both rows), G9, G10, G12 all PASS",
         r["gates"]["G-M2_mesh_identity"] == "PASS"
         and r["gates"]["G-MESHID_same_mesh_as_SO1b"]["verdict"] == "PASS"
         and r["gates"]["G-METHOD_scotch_vs_simple_at_fixed_np4"]["P"]["verdict"] == "PASS"
         and r["gates"]["G-METHOD_scotch_vs_simple_at_fixed_np4"]["S"]["verdict"] == "PASS"
         and r["gates"]["G9_toolchain"]["verdict"] == "PASS"
         and r["gates"]["G10_caps"]["verdict"] == "PASS"
         and r["gates"]["G12_placement"]["verdict"] == "PASS")
    unit("U3 the np-INVARIANCE BAND IN THE ARTEFACT IS THE STANDARD'S, NOT BAND D: "
         "s_g == 1.0e-3, s_J == 2.2e-5, and s_g is EXACTLY 50x tighter than band D "
         "expressed as a fraction (5.0 % -> 5.0e-2)",
         r["gates"]["G-NP_np_invariance_at_the_optimum"]["Ns-P"]["band_s_g"] == 1.0e-3
         and r["gates"]["G-NP_np_invariance_at_the_optimum"]["Ns-P"]["band_s_j"] == 2.2e-5
         and abs((FD_BAND_PCT / 100.0) / S_G_BAND - 50.0) < 1e-9)
    unit("U4 band D / band E / plateau are BYTE-IDENTICAL to SO-1a's inherited constants",
         (FD_BAND_PCT, AGG_BAND_PCT, PLATEAU_TOL_PCT) == (5.0, 5.0, 10.0))

    # ---- G-NP, the headline gate ---------------------------------------------
    r = grade(_fix(tmp, tw(np_err={"Ns-P": 0.05})))
    unit("U5 PLANTED 5 % np=4-vs-np=1 disagreement on the PATCHED scotch arm -> G-NP GATE "
         "FAIL, that arm GATE FAIL, the PATCHED row GATE FAIL, item GATE FAIL",
         r["gates"]["G-NP_np_invariance_at_the_optimum"]["Ns-P"]["verdict"] == "GATE FAIL"
         and r["arms"]["Ns-P"] == "GATE FAIL" and r["rows"]["PATCHED"] == "GATE FAIL"
         and r["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(np_err={"Ns-P": 5.0e-4})))
    unit("U6 a disagreement of 5e-4 -- INSIDE the 1.0e-3 band -- still PASSES: the gate "
         "discriminates, it does not merely refuse",
         r["gates"]["G-NP_np_invariance_at_the_optimum"]["Ns-P"]["verdict"] == "PASS"
         and r["verdict"] == "PASS")
    r = grade(_fix(tmp, tw(np_err={"Ns-P": 2.0e-3})))
    unit("U7 a disagreement of 2e-3 -- JUST OUTSIDE the band -- FAILS.  The band's two "
         "sides are both driven, so it is a threshold and not a direction",
         r["gates"]["G-NP_np_invariance_at_the_optimum"]["Ns-P"]["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(np_flip={"Ns-S": {6}})))
    unit("U8 PLANTED SIGN FLIP at flat index 6 on the SHIPPED scotch arm -> flip counted, "
         "G-NP GATE FAIL even though the magnitude is unchanged",
         len(r["gates"]["G-NP_np_invariance_at_the_optimum"]["Ns-S"]["per_objective"]["CD"]["sign_flips"]) == 1
         and r["gates"]["G-NP_np_invariance_at_the_optimum"]["Ns-S"]["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(sj_err={"Ni-P": 1.0e-3})))
    unit("U9 PLANTED 1e-3 OBJECTIVE spread -> s_J GATE FAIL on its own far tighter band "
         "(2.2e-5) with the gradient untouched",
         r["gates"]["G-NP_objective_spread"]["Ni-P"]["verdict"] == "GATE FAIL"
         and r["gates"]["G-NP_np_invariance_at_the_optimum"]["Ni-P"]["verdict"] == "PASS"
         and r["arms"]["Ni-P"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(sj_err={"Ni-P": 1.0e-5})))
    unit("U10 an objective spread of 1e-5 is INSIDE 2.2e-5 and PASSES",
         r["gates"]["G-NP_objective_spread"]["Ni-P"]["verdict"] == "PASS")
    unit("U11 REFUSAL when the staged serial reference is not np = 1 -- the comparison "
         "basis must be the serial arm, never another parallel one",
         refused(_fix(tmp, tw(ref_np=2))))
    unit("U12 CHANNEL DISAGREEMENT: the instrument's carried copy of the serial reference "
         "differs from the comparator's own read of the same file -> REFUSAL",
         refused(_fix(tmp, tw(carried={"Ns-P": 1.0e-6}))))

    # ---- G-METHOD -------------------------------------------------------------
    r = grade(_fix(tmp, tw(np_err={"Ns-S": 5.0e-3})))
    unit("U13 a scotch arm 5e-3 from the serial reference is ALSO 5e-3 from its `simple` "
         "twin -> G-METHOD GATE FAIL on the SHIPPED row: the METHOD axis fires "
         "independently of the np axis",
         r["gates"]["G-METHOD_scotch_vs_simple_at_fixed_np4"]["S"]["verdict"] == "GATE FAIL"
         and r["rows"]["SHIPPED"] == "GATE FAIL")
    r = grade(_fix(tmp))
    unit("U14 G-METHOD names `simple 4x1x1` as the REFERENCE limb and the convention is "
         "registered in the artefact, not chosen after the numbers",
         r["gates"]["G-METHOD_scotch_vs_simple_at_fixed_np4"]["P"]["simple_arm"] == "Ni-P"
         and "registered, not chosen" in r["gates"]["G-METHOD_scotch_vs_simple_at_fixed_np4"]["P"]["reference_convention"])

    # ---- G-DECOMP -------------------------------------------------------------
    unit("U15 an arm whose artefact names the WRONG decomposition method -> REFUSAL "
         "(a gradient that cannot name its decomposition is not a result)",
         refused(_fix(tmp, tw(decomp={"Ni-P": "scotch"}))))
    unit("U16 an artefact whose nprocs is 2 where 4 is registered -> REFUSAL, cross-asserted "
         "against the dictionary's own numberOfSubdomains",
         refused(_fix(tmp, tw(nprocs={"Ns-S": 2}))))
    unit("U17 a `simple` arm whose SUBDIVISION is (2 2 1) not (4 1 1) -> REFUSAL: for "
         "`simple` the subdivision is part of the disclosure, not only the method name",
         refused(_fix(tmp, tw(simple_n=["2", "2", "1"]))))
    r = grade(_fix(tmp))
    unit("U18 the clean artefact RECORDS the decomposition column section 5 requires "
         "(method, n_subdomains and, for `simple`, the subdivision)",
         r["gates"]["G-DECOMP"]["Ns-P"]["method"] == "scotch"
         and r["gates"]["G-DECOMP"]["Ni-S"]["simple_n"] == DECOMP_SIMPLE_N
         and all(r["gates"]["G-DECOMP"][a]["n_subdomains"] == 4 for a in ARMS_SOLVER))

    # ---- G-XSTAR --------------------------------------------------------------
    unit("U19 an arm that solved at a DIFFERENT design point from SO-1b's x* -> REFUSAL",
         refused(_fix(tmp, tw(xstar={"Ns-P": {"shape": [repr(9.9)] * 8,
                                              "patchV": [repr(10.0), repr(1.13)]}}))))
    r = grade(_fix(tmp))
    unit("U20 G-XSTAR labels itself an IDENTITY ASSERTION ON A CONSUMED INPUT, not a gate "
         "on the design vector -- D13 measured the design vector non-unique 15/15",
         "not a gate on the design vector" in r["gates"]["G-XSTAR"]["Ns-P"]["note"])

    # ---- SO-1cR: BREAK 6, THE ROW LABEL, DRIVEN AT THE GRADER'S OWN CALL SITE.
    # SO-1c's fixture wrote the FULL row name into the staged artefact.  SO-1bR
    # writes the DIRECTORY SUFFIX.  The default fixture now writes what the
    # PRODUCER writes, so U1..U20 above already exercise G-XSTAR against the
    # REAL label -- which the equality form refuses (driven as a mutation in the
    # amendment, and the reason SO-1c's 53 green units saw nothing).
    r = grade(_fix(tmp, tw(optref_row_label="produced")))
    unit("U66 THE PRODUCER'S OWN LABEL PASSES.  The staged artefact carries row='P'/'S' -- "
         "exactly what SO-1bR writes to E-P/E-S, verified on disk -- and G-XSTAR PASSES on "
         "every solver arm.  SO-1c's equality form REFUSED this, in preflight and again at "
         "grading; this is the state the item died in",
         r["verdict"] == "PASS"
         and all(r["gates"]["G-XSTAR"][a]["verdict"] == "PASS" for a in ARMS_SOLVER))
    unit("U67 AND THE REGISTERED LABEL IS READ BACK, NOT INFERRED: the artefact's row is the "
         "PRODUCED suffix and the arm's registered row is the FULL name, and BOTH are named "
         "in the gate's own record",
         all(r["gates"]["G-XSTAR"][a]["row"] == ARM_ROW[a] for a in ARMS_SOLVER)
         and all(r["gates"]["G-XSTAR"][a]["rowkey"] == ARM_ROWKEY[a] for a in ARMS_SOLVER))
    r = grade(_fix(tmp, tw(optref_row_label="fullname")))
    unit("U68 THE OTHER REGISTERED LABEL ALSO PASSES.  row='PATCHED'/'SHIPPED' is the second "
         "member of each row's registered set, so an artefact written by a producer that "
         "labels by row NAME is accepted too -- the mapping accepts BOTH and invents NEITHER",
         r["verdict"] == "PASS"
         and all(r["gates"]["G-XSTAR"][a]["verdict"] == "PASS" for a in ARMS_SOLVER))
    # ---- THE SWAP, BOTH DIRECTIONS.  This is why the two label sets must stay
    # ---- DISJOINT: the assertion exists to catch AN ARTEFACT SITTING IN THE
    # ---- WRONG DIRECTORY, and a mapping that accepted `row[0]` generically, or
    # ---- that accepted any label, would wave both of these through.
    unit("U69 SWAP DIRECTION 1 -- a SHIPPED artefact staged under optref/PATCHED/ (and a "
         "PATCHED artefact under optref/SHIPPED/) STILL REFUSES.  The label sets are DISJOINT, "
         "so no swapped artefact can satisfy the assertion",
         refused(_fix(tmp, tw(optref_row_label="swapped"))))
    unit("U70 SWAP DIRECTION 2 -- the same swap by FULL NAME rather than by suffix STILL "
         "REFUSES.  A repair that fixed only the suffix form would pass this and be wrong",
         refused(_fix(tmp, tw(optref_row_label="swapped_full"))))
    unit("U71 AN UNREGISTERED LABEL REFUSES.  row='PORPOISE' shares its first letter with "
         "PATCHED, so a check derived as `row[0]` would ACCEPT it -- which is the whole reason "
         "the mapping is written out in full and is not derived",
         refused(_fix(tmp, tw(optref_row_label="PORPOISE"))))
    unit("U72 THE TWO REGISTERED LABEL SETS ARE DISJOINT, asserted arithmetically rather than "
         "trusted from the comment beside them -- if they ever intersect, a swapped artefact "
         "becomes acceptable and the gate silently stops being a check",
         set(ROW_LABELS["PATCHED"]).isdisjoint(set(ROW_LABELS["SHIPPED"]))
         and set(ROW_LABELS) == {"PATCHED", "SHIPPED"}
         and set(ARM_ROW.values()) <= set(ROW_LABELS))
    r = grade(_fix(tmp))

    # ---- G-MESHID -------------------------------------------------------------
    r = grade(_fix(tmp, tw(meshsha="differ")))
    unit("U21 this item's mesh `points` sha256 DIFFERS from SO-1b's -> G-MESHID GATE FAIL "
         "and item GATE FAIL: 'the same mesh' is asserted, not assumed",
         r["gates"]["G-MESHID_same_mesh_as_SO1b"]["verdict"] == "GATE FAIL"
         and r["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(meshsha="absent")))
    unit("U22 SO-1b's mesh fingerprint ABSENT -> NOT A RESULT, never a pass: mesh identity "
         "is a PHYSICS precondition of the comparison the standard defines",
         r["gates"]["G-MESHID_same_mesh_as_SO1b"]["verdict"] == "NOT A RESULT"
         and r["verdict"] == "NOT A RESULT")

    # ---- G5N: the FD verdict at np = 4, which is what AV-1 cannot supply -------
    r = grade(_fix(tmp, tw(err={"Ns-S": {("shape", 3): 7.0}})))
    unit("U23 PLANTED 7 % FD error on the SHIPPED scotch arm -> that component GATE FAIL, "
         "the arm GATE FAIL, item GATE FAIL -- WITH G-NP still PASSING, which is exactly "
         "the hole AV-1's own section 8 says G-NP alone cannot close",
         r["gates"]["G5N_CD"]["Ns-S"]["verdict"] == "GATE FAIL"
         and r["gates"]["G-NP_np_invariance_at_the_optimum"]["Ns-S"]["verdict"] == "PASS"
         and r["arms"]["Ns-S"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(err_cl={"Ni-P": {("shape", 0): 7.0}})))
    unit("U24 PLANTED 7 % error on the CONSTRAINT gradient only -> G5cN GATE FAIL with "
         "G5N (CD) still PASS: the constraint gradient fails independently",
         r["gates"]["G5cN_CL"]["Ni-P"]["verdict"] == "GATE FAIL"
         and r["gates"]["G5N_CD"]["Ni-P"]["verdict"] == "PASS")
    r = grade(_fix(tmp, tw(noplateau={"Ns-P": {("shape", 0), ("shape", 3), ("shape", 6)}})))
    unit("U25 three no-plateau components on one arm -> 2 graded < 3 -> that arm's G5N "
         "NOT A RESULT, row NOT A RESULT, item NOT A RESULT",
         r["gates"]["G5N_CD"]["Ns-P"]["verdict"] == "NOT A RESULT"
         and r["verdict"] == "NOT A RESULT")

    # ---- G-TB, the charter-4 trivial baseline ---------------------------------
    r = grade(_fix(tmp, tw(tb_pass={"Ni-S": {("shape", 0), ("shape", 3), ("shape", 6),
                                             ("shape", 7), ("patchV", 1)}})))
    unit("U26 the DELIBERATELY WRONG step AGREES on 5/5 of one arm -> G-TB GATE FAIL and "
         "that arm's verdict WITHDRAWN to NOT A RESULT (rule-5 direction)",
         r["gates"]["G_TB_trivial_baseline"]["Ni-S"]["verdict"] == "GATE FAIL"
         and r["arms"]["Ni-S"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT")
    r = grade(_fix(tmp, tw(tb_pass={"Ni-S": {("shape", 0)}})))
    unit("U27 ONE component passing at the wrong step is inside TB_MAX_PASSING -> G-TB "
         "PASS, arm PASS: the gate has a registered tolerance, not a hair trigger",
         r["gates"]["G_TB_trivial_baseline"]["Ni-S"]["verdict"] == "PASS"
         and r["arms"]["Ni-S"] == "PASS")

    # ---- G-CLOCK and G10 -- the frame defect ----------------------------------
    r = grade(_fix(tmp, tw(cm={"Ns-P": 30.4}, cmc={"Ns-P": 29.9})))
    unit("U28 THE DEFECT THIS GATE EXISTS TO REMOVE: an arm whose HOST core-min (30.4) is "
         "ABOVE its 30.0 cap while its CONTAINER core-min (29.9) is inside -> G10 PASSES, "
         "because the cap is enforced in the container frame and is graded there",
         r["gates"]["G10_caps"]["verdict"] == "PASS"
         and r["gates"]["G10_caps"]["per_arm"]["Ns-P"]["gate_frame"] == "CONTAINER"
         and r["gates"]["G10_caps"]["per_arm"]["Ns-P"]["core_min_host"] == 30.4)
    r = grade(_fix(tmp, tw(cm={"Ns-P": 31.5}, cmc={"Ns-P": 30.8})))
    unit("U29 AND THE CAP STILL BITES: container core-min 30.8 above the 30.0 cap -> G10 "
         "GATE FAIL.  The frame was corrected, the cap was NOT widened",
         r["gates"]["G10_caps"]["verdict"] == "GATE FAIL"
         and r["gates"]["G10_caps"]["per_arm"]["Ns-P"]["crossed"])
    r = grade(_fix(tmp, tw(cmc={"Ni-S": None})))
    unit("U30 an UNREADABLE container clock -> G10 falls back to the HOST frame AND SAYS "
         "SO, and the arm is named in the fallback list: a limb that could not be "
         "evaluated in its own frame is reported, never silently passed",
         "Ni-S" in r["gates"]["G10_caps"]["frame_fallbacks"]
         and r["gates"]["G10_caps"]["per_arm"]["Ni-S"]["gate_frame"] == "HOST_FALLBACK"
         and "Ni-S" in r["gates"]["G-CLOCK_two_frames"]["not_measured"])
    r = grade(_fix(tmp))
    unit("U31 the COST claim uses the HOST frame and the CAP GATE uses the CONTAINER "
         "frame, and the two totals are BOTH reported with their difference",
         r["cost"]["frame"].startswith("HOST")
         and r["gates"]["G10_caps"]["total_core_min_host_COST"] > r["gates"]["G10_caps"]["total_core_min_container_GATE"]
         and r["gates"]["G-CLOCK_two_frames"]["max_delta_core_min"] != NOT_MEASURED)

    # ---- G1, R-RC, the age datum, and THE STAGED-INPUT EXCLUSION --------------
    unit("U32 rc=1 on one arm -> REFUSAL", refused(_fix(tmp, tw(rc={"Ns-P": 1}, ke={"Ns-P": 1}))))
    unit("U33 OOMKilled=true -> REFUSAL", refused(_fix(tmp, tw(oom={"Ni-S": "true"}))))
    unit("U34 terminal marker absent -> REFUSAL", refused(_fix(tmp, tw(terminal={"Ni-P": False}))))
    unit("U35 artefact OLDER than the age datum -> REFUSAL (rule 4)",
         refused(_fix(tmp, tw(stale={"Ns-S"}))))
    unit("U36 FOAM FATAL ERROR at rc = 0 -> REFUSAL (C5 refuses regardless of rc)",
         refused(_fix(tmp, tw(fatal={"Ns-P": "FOAM FATAL ERROR"}))))
    unit("U37 harness rc 0 vs kernel exit 1 -> REFUSAL", refused(_fix(tmp, tw(ke={"Ni-P": 1}))))
    r = grade(_fix(tmp, tw(rc_record={"Ni-S"})))
    unit("U38 (R-RC) the rc RECORD absent while C2-C5 all hold -> rc value NOT MEASURED, "
         "the implied rc = 0 written as an INFERENCE, verdict unchanged PASS",
         r["verdict"] == "PASS" and any("Ni-S" in str(x) for x in r["rc_inferences"]))
    unit("U39 (R-RC) the rc RECORD absent AND the terminal marker missing -> REFUSAL: "
         "R-RC relaxes a missing record, never a positive reading of failure",
         refused(_fix(tmp, tw(rc_record={"Ni-S"}, terminal={"Ni-S": False}))))
    # ---- THE D4S-F3S CLASS, DRIVEN.  The staged `so1b_E.json` in every arm
    # ---- directory is OLDER than the age datum by construction (`cp -a` keeps the
    # ---- source mtime).  If it were in the age-checked list the age clause would
    # ---- be UNSATISFIABLE BY CONSTRUCTION and every arm would refuse.  It is not,
    # ---- and this unit proves the exclusion rather than trusting the comment.
    root = _fix(tmp)
    stamps = []
    for a in ARMS_SOLVER:
        sp = os.path.join(root, a, "so1b_E.json")
        dp = os.path.join(root, a, DATUM_FILE)
        stamps.append(os.path.getmtime(sp) < float(open(dp).read().strip()))
    r = grade(root)
    unit("U40 THE D4S-F3S CLASS: the STAGED so1b_E.json is OLDER than the age datum on "
         "every solver arm, and the item still PASSES -- an age guard checks only what "
         "the run PRODUCES, and the staged input is excluded BY NAME",
         all(stamps) and r["verdict"] == "PASS"
         and "so1b_E.json" in r["staged_inputs_excluded_from_the_age_guard"])
    r = grade(_fix(tmp, tw(datum={"Ns-P": "gz", "Ni-P": "gz", "Ns-S": "gz", "Ni-S": "gz"})))
    unit("U41 (AV-1/AV-2) every solver arm's datum resolves to the COMPRESSED twin 0/U.gz "
         "and the guard PASSES -- the defect that cost AV-1 and AV-2 their items",
         r["verdict"] == "PASS"
         and all(r["age_datum_resolution"][a]["is_compressed_twin"] for a in ARMS_SOLVER))
    unit("U42 (AV-1/AV-2) the datum GENUINELY ABSENT in BOTH registered names -> REFUSAL: "
         "resolution by existence still refuses when neither name exists",
         refused(_fix(tmp, tw(datum={"Ns-P": "none"}))))

    # ---- controls, toolchain, placement, and the assert census ----------------
    r = grade(_fix(tmp))
    unit("U43 BOTH grader-level plants are SEEN -- the FD plant on two arms AND the "
         "np-INVARIANCE plant, which shows THE HEADLINE GATE ITSELF able to fail",
         r["controls"]["grader_plant_Ns-P"]["grader_plant_seen"]
         and r["controls"]["grader_plant_Ni-S"]["grader_plant_seen"]
         and r["controls"]["grader_np_plant_Ns-P"]["np_plant_seen"]
         and r["controls"]["grader_np_plant_Ns-P"]["read"] == "GATE FAIL"
         and r["controls"]["Ns-P"]["instrument_ctrl_zero"] == 0.0)
    unit("U44 the instrument CTRL planted row broken -> REFUSAL (a reader not shown able "
         "to see a non-zero is not evidence)",
         refused(_fix(tmp, tw(ctrl_ok=False))))
    r = grade(_fix(tmp, tw(so={"Ns-P": SO_MD5["SHIPPED"]})))
    unit("U45 a PATCHED arm carrying the SHIPPED library hash -> G9 GATE FAIL (G-ROWX: a "
         "row is an image hash, never a directory name)",
         r["gates"]["G9_toolchain"]["verdict"] == "GATE FAIL" and r["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(cs={"Ni-P": "4,14"})))
    unit("U46 an arm off its registered per-arm cpuset -> G12 GATE FAIL",
         r["gates"]["G12_placement"]["verdict"] == "GATE FAIL")
    r = grade(_fix(tmp, tw(dl="2.10 n=10 max_nr_throttled=0")))
    unit("U47 delivered cores 2.10 below the 3.0 floor AT np = 4 -> G12 GATE FAIL.  The "
         "floor did not apply in SO-1a or SO-1b, where every arm was np = 1",
         r["gates"]["G12_placement"]["verdict"] == "GATE FAIL"
         and r["gates"]["G12_placement"]["per_arm"]["Ns-P"]["floor_applies"])
    r = grade(_fix(tmp, tw(cells=4033)))
    unit("U48 cells 4033 -> G-M2 GATE FAIL and P_A MISS",
         r["gates"]["G-M2_mesh_identity"] == "GATE FAIL"
         and r["predictions"]["P_A_cells_4032"] == "MISS")
    unit("U49 ast.Assert count = 0 in so1cr_grade.py and so1cr_xn.py (L-332)",
         count_asserts(os.path.abspath(__file__)) == 0
         and count_asserts(os.path.join(here, "so1cr_xn.py")) == 0)
    p = os.path.join(tmp, "planted_assert.py")
    open(p, "w").write("def f(x):\n    assert x\n")
    unit("U50 the assert counter SEES a planted assert (=1) -- a counter never shown "
         "counting is not a counter", count_asserts(p) == 1)
    unit("U51 the registered CEILING equals the sum of the registered caps",
         abs(sum(CAPS.values()) - ITEM_CEILING_CORE_MIN) < 1e-9)
    unit("U52 P_3 (the design-point claim) is registered NOT_MEASURED with its reason, so "
         "an absent AV-1R baseline can never become a silent HIT",
         r["predictions"]["P_3_s_g_larger_at_the_optimum_than_at_the_baseline"] == NOT_MEASURED
         and "cannot become" in r["P_3_note"])
    # ---- U53 RECORDS A WEAKNESS IN THIS SUITE RATHER THAN HIDING IT.  The mutation
    # ---- control `SIGN_FLIP_MAX 0 -> 9` flips NO unit, so as a mutant it PROVES
    # ---- NOTHING and is reported as such.  The reason is structural and is measured
    # ---- here, not asserted: a sign flip on any component above the near-zero floor
    # ---- necessarily moves `s_g` far beyond 1.0e-3 (the fixture's smallest non-zero
    # ---- component, shape[6] = 0.007 against a reference norm of ~0.107, gives
    # ---- s_g ~ 0.13 -- 130x the band), so the flip limb can never be the SOLE cause
    # ---- of a GATE FAIL and is not independently load-bearing.  IT IS KEPT because
    # ---- ADJOINT_VERIFICATION_STANDARD.md section 3 registers it and because it NAMES
    # ---- the failure mode in the record -- a reader sees "sign flip at index 6"
    # ---- rather than only "s_g = 0.13" -- but this item does not claim it as an
    # ---- independent gate.
    r_flip = grade(_fix(tmp, tw(np_flip={"Ns-S": {6}})))
    gnp_s = r_flip["gates"]["G-NP_np_invariance_at_the_optimum"]["Ns-S"]["per_objective"]["CD"]
    unit("U53 THE SIGN-FLIP LIMB IS NOT INDEPENDENTLY LOAD-BEARING, AND THIS UNIT SAYS SO: "
         "the planted flip drives s_g to >10x the band on its own, so `SIGN_FLIP_MAX "
         "0 -> 9` is an INERT MUTATION that proves nothing.  The limb is kept because "
         "the standard registers it and because it NAMES the failure mode",
         len(gnp_s["sign_flips"]) == 1 and gnp_s["s_g"] > 10.0 * S_G_BAND)


    # =========================================================================
    # AMENDMENT R6, 2026-08-28 -- U54..U63.  TWO READER DEFECTS, EACH DRIVEN IN
    # BOTH DIRECTIONS.  Appended rather than interleaved so no frozen unit label
    # is renumbered.
    # =========================================================================

    # ---- C5: the benign banner MUST NOT be flagged, the real crash MUST be ----
    # THE PLANT IS TAKEN FROM THE ARTEFACT, NOT INVENTED.  This is line 18 of
    # SO-1a's real `MESH/checkMesh.log`, the line its grader refused on.  Where
    # that run root is on the box, the literal is CROSS-ASSERTED against it
    # byte-for-byte and the unit says whether it was.
    TRAPFPE = "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE)."
    SO1A_CM = ("/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient"
               "/MESH/checkMesh.log")
    xcheck = "NOT CROSS-ASSERTED (SO-1a's run root is not on this box)"
    if os.path.isfile(SO1A_CM):
        _lines = open(SO1A_CM, errors="replace").read().splitlines()
        xcheck = ("CROSS-ASSERTED byte-identical to %s:18" % SO1A_CM
                  if len(_lines) > 17 and _lines[17] == TRAPFPE
                  else "CROSS-ASSERT FAILED against %s:18" % SO1A_CM)
    FOAM_FATAL = ("\n--> FOAM FATAL ERROR: \nCannot find patchField entry for lowerWall\n\n"
                  "    From function void Foam::GeometricField<...>::readField(...)\nFOAM exiting\n")
    SIGFPE_CRASH = ("#0  Foam::error::printStack(Foam::Ostream&) at ??:?\n"
                    "#1  Foam::sigFpe::sigHandler(int) at ??:?\n"
                    "#2  ? in /lib/x86_64-linux-gnu/libc.so.6\n"
                    "Floating point exception (core dumped)\n")

    def refusal_detail(root):
        try:
            grade(root)
            return None
        except Refusal as exc:
            return json.loads(str(exc))["detail"]

    r = grade(_fix(tmp, tw(cm_extra=TRAPFPE + "\n")))
    c5 = r["rule4_clauses_per_arm"]["MESH"]["C5_no_fatal_token"]
    unit("U54 THE DEFECT R6 REMOVES, DRIVEN: OpenFOAM's STARTUP BANNER `trapFpe: Floating "
         "point exception trapping enabled (FOAM_SIGFPE).` -- a notice that the solver is "
         "PROTECTED -- planted into checkMesh.log is NOT flagged and the item still reads "
         "PASS.  BEFORE THIS AMENDMENT THIS EXACT LINE REFUSED WITH ZERO GATES EVALUATED, "
         "which is what SO-1a's grader did on a clean 5-arm run.  The plant is %s"
         % xcheck,
         r["verdict"] == "PASS" and "CROSS-ASSERT FAILED" not in xcheck)

    unit("U55 THE SUPPRESSION IS NOT SILENT: the PASS record counts exactly ONE excluded "
         "benign line, names the FILE it came from (checkMesh.log, NOT the arm log) and "
         "prints WHY it is benign",
         c5 is not None and c5["n_benign_lines_excluded"] == 1
         and c5["benign_lines_excluded"][0]["file"] == "checkMesh.log"
         and "ENABLEMENT NOTICE" in c5["benign_lines_excluded"][0]["why_benign"]
         and set(c5["files_scanned"]) == {"MESH_x.log", "checkMesh.log"})

    unit("U56 AND THE OTHER DIRECTION: a REAL `FOAM FATAL ERROR` block in the SAME "
         "artefact -- the SCRIPT-arm path that fired on SO-1a -- STILL REFUSES",
         refused(_fix(tmp, tw(cm_extra=FOAM_FATAL))))

    unit("U57 THE EXCLUSION IS PER LINE, NOT PER FILE: a REAL SIGFPE crash "
         "(`Foam::sigFpe::sigHandler(int)` + `Floating point exception (core dumped)`) "
         "SITTING BESIDE the benign banner in one file STILL REFUSES.  This is the unit "
         "that proves the repair did not simply blind C5 to SIGFPE",
         refused(_fix(tmp, tw(cm_extra=TRAPFPE + "\n" + SIGFPE_CRASH))))

    det = refusal_detail(_fix(tmp, tw(cm_extra=FOAM_FATAL)))
    unit("U58 THE SECOND, SMALLER DEFECT: the refusal NAMES THE FILE AND LINE of every "
         "hit, and the named file is `checkMesh.log`.  SO-1a's refusal named the ARM log "
         "for a token that appears nowhere in it -- a reader sent to the wrong file",
         det is not None and det["token_sites"]
         and all(st["file"] == "checkMesh.log" for st in det["token_sites"])
         and all(isinstance(st["line"], int) and st["line"] > 0 for st in det["token_sites"])
         and "NOT necessarily" in det["note"])

    lost = [t for t in FATAL_TOKENS
            if not refused(_fix(tmp, tw(cm_extra="a real crash line: %s\n" % t)))]
    unit("U59 THE LINE SPLIT LOSES NO TOKEN: each of the %d registered FATAL_TOKENS, "
         "planted ALONE on a line that is not an enablement notice, STILL REFUSES.  A "
         "scanner rewritten from whole-file to line-by-line is measured, not assumed"
         % len(FATAL_TOKENS), not lost)

    unit("U65 THE ADOPTED HANDLER SYMBOL IS INDEPENDENTLY LOAD-BEARING, AND THIS UNIT "
         "IS WHY IT IS NOT DECORATION: a stack trace whose ONLY fatal string is "
         "`Foam::sigFpe::sigHandler(int)` -- an FPE crash whose shell line never reached "
         "the log -- REFUSES.  The token is HARD-CODED here, not read from FATAL_TOKENS, "
         "so removing it from that tuple FLIPS THIS UNIT.  U59 alone could not: it is "
         "defined in terms of the tuple, so a mutation that empties the tuple also "
         "empties U59's loop, and the mutation measured INERT before this unit existed",
         refused(_fix(tmp, tw(cm_extra="#0  Foam::error::printStack(Foam::Ostream&) at ??:?\n"
                                       "#1  Foam::sigFpe::sigHandler(int) at ??:?\n"))))

    # THE STRONGEST NEGATIVE FIXTURE IS ONE NOBODY BUILT.  A live W3 stage log,
    # 339 lines, FOUR banner hits and FIVE `End` lines -- a clean completed stage
    # that the bare-substring test would have refused.  The supervisor stopped that
    # run over this defect at 16:33:52Z on 2026-08-28.  READ-ONLY; never modified.
    W3_LOG = ("/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady"
              "/S0_20260828T162848Z_1898005.log")
    if os.path.isfile(W3_LOG):
        w3 = open(W3_LOG, errors="replace").read()
        w3_banners = sum(1 for ln in w3.splitlines()
                         if any(t in ln for t in FATAL_TOKENS))
        r = grade(_fix(tmp, tw(cm_extra=w3)))
        c5w = r["rule4_clauses_per_arm"]["MESH"]["C5_no_fatal_token"]
        unit("U64 A REAL, UNCONSTRUCTED OPENFOAM LOG -- %s, %d lines, %d banner lines, "
             "5 `End` lines, ZERO real fatal tokens -- planted whole into checkMesh.log "
             "STILL READS PASS, with all %d benign lines counted and named.  The banner "
             "is not a corner case: closure measured it on 63 of 70 archived logs, 57 of "
             "them cleanly completed, so a scanner that refuses on it refuses on almost "
             "every log the lab holds"
             % (os.path.basename(W3_LOG), len(w3.splitlines()), w3_banners, w3_banners),
             r["verdict"] == "PASS" and w3_banners == 4
             and c5w["n_benign_lines_excluded"] == w3_banners)
    else:
        unit("U64 NOT DRIVEN ON THE REAL LOG: %s is not on this box.  The synthetic "
             "banner plant (U54) is driven and CROSS-ASSERTED against SO-1a's own "
             "checkMesh.log where present; this unit is recorded as not driven rather "
             "than quietly passed" % W3_LOG, False)

    # ---- G-MESHID: uniqueness refusal, and the pre-written physics sentence ----
    r = grade(_fix(tmp, tw(dup_mesh_log=True)))
    mid = r["gates"]["G-MESHID_same_mesh_as_SO1b"]
    unit("U60 TWO files match MESH_*.log in the run root -> NOT A RESULT labelled a READER "
         "CONDITION, with BOTH candidates named.  BEFORE THIS AMENDMENT the last-wins loop "
         "SILENTLY PICKED ONE and the item read PASS -- an ambiguity resolved in favour of "
         "a pass",
         mid["verdict"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT"
         and mid["cause_class"] == "READER_CONDITION_NOT_A_MESH_FINDING"
         and mid["n_mesh_log_candidates"] == 2
         and "MESH_REGENERATION_IS_NOT_DETERMINISTIC" not in mid["reason"])

    r = grade(_fix(tmp, tw(ref_dup=True)))
    mid = r["gates"]["G-MESHID_same_mesh_as_SO1b"]
    unit("U61 THE :934 DEFECT, DRIVEN: SO-1b's fingerprint carrying TWO distinct sha256s -- "
         "what the driver's `head -4` produced from a multi-log root -- now reads NOT A "
         "RESULT, READER CONDITION.  BEFORE THIS AMENDMENT IT PUBLISHED AS "
         "`MESH_REGENERATION_IS_NOT_DETERMINISTIC` AND GATE FAIL: a reader defect wearing "
         "a fluent physics sentence",
         mid["verdict"] == "NOT A RESULT" and r["verdict"] == "NOT A RESULT"
         and mid["cause_class"] == "READER_CONDITION_NOT_A_MESH_FINDING"
         and mid["n_reference_sha"] == 2
         and "MESH_REGENERATION_IS_NOT_DETERMINISTIC" not in mid["reason"])

    r = grade(_fix(tmp, tw(meshsha="differ")))
    mid = r["gates"]["G-MESHID_same_mesh_as_SO1b"]
    unit("U62 AND THE REPAIR DOES NOT BLUNT THE GATE: ONE candidate, ONE sha each side, "
         "MISMATCHED -> GATE FAIL with the PHYSICS sentence and cause_class MESH_FINDING.  "
         "The physics reason is now emitted ONLY where the comparison actually ran",
         mid["verdict"] == "GATE FAIL" and mid["cause_class"] == "MESH_FINDING"
         and "MESH_REGENERATION_IS_NOT_DETERMINISTIC" in mid["reason"]
         and mid["n_this_item_sha"] == 1 and mid["n_reference_sha"] == 1)

    r = grade(_fix(tmp))
    mid = r["gates"]["G-MESHID_same_mesh_as_SO1b"]
    unit("U63 THE NON-MISMATCH IS NOT FLAGGED, AND THE SELECTION IS ON THE RECORD: one "
         "candidate, PASS, with the CHOSEN FILE and the FULL CANDIDATE LIST printed beside "
         "the verdict -- a selection a reader cannot see is not a selection",
         mid["verdict"] == "PASS" and mid["n_mesh_log_candidates"] == 1
         and os.path.basename(mid["mesh_log_selected"]) == "MESH_x.log"
         and mid["mesh_log_candidates"] == [mid["mesh_log_selected"]])

    print("\nSO1cR grader selftest: %d units, %d fail" % (n, len(fails)))
    for f in fails:
        print("  FAIL: %s" % f)
    if n != EXPECTED_UNITS:
        print("REFUSAL: unit count %d != frozen EXPECTED_UNITS %d "
              "(a suite that silently loses a unit is not a suite)" % (n, EXPECTED_UNITS))
        return 2
    return 0 if not fails else 1


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
    if abs(sum(CAPS.values()) - ITEM_CEILING_CORE_MIN) > 1e-9:
        print("REFUSAL: the registered CEILING %r is not the sum of the registered caps %r"
              % (ITEM_CEILING_CORE_MIN, sum(CAPS.values())))
        return 2
    if a.selftest:
        d = os.path.join(a.tmpdir, "so1cr_selftest_%d" % os.getpid())
        os.makedirs(d, exist_ok=True)
        return selftest(d)
    if not a.root:
        print("usage: so1cr_grade.py --root <run root> [--out FILE] | --selftest")
        return 64
    try:
        r = grade(a.root)
    except Refusal as e:
        print("REFUSAL: %s -> NOT A RESULT" % e)
        if a.out:
            json.dump({"item": "CURRICULUM-%s" % ITEM, "verdict": "NOT A RESULT", "refusal": str(e)},
                      open(a.out, "w"), indent=1)
        return 2
    print(json.dumps(r, indent=1, default=str))
    if a.out:
        json.dump(r, open(a.out, "w"), indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
