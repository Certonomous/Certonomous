#!/usr/bin/env python3
"""a1wrt2_stage.py -- the A1WRT2 arm STAGER.  NOT FROZEN.  NOT PINNED.

THIS FILE STAGES NOTHING IN ITS CURRENT STATE unless it is given an explicit
`--run-root`, and the REGISTERED run root `/home/ubuntu/certonomous-runs/A1WRT2`
DOES NOT EXIST.  It launches no container, spends no core-minute and drops no
queue entry.  `A1WRT2_SUCCESSOR_DRAFT.md` section 11 lists what is owed before
this item may freeze and what is owed after that before it may be enqueued;
neither is this file's to grant.  SUBMISSIONS PARKED (`CLAUDE.md` rule 7).

WHAT IT IS FOR
--------------
Draft section 3 registers both arms as CONTINUED, not cold: `SEAM` continues
`A1WRT` U1's `4000/` state, `TAIL` continues `SEAM`'s.  Draft section 4's HARD
gate `G-COLDSTART-SEAM` reads the STAGED tree back off disk and refuses unless
the continuation actually arrived.  This file is what puts it there, and every
step below exists because a NAMED, MEASURED failure in this family put it there.

THE FIVE DEFECTS THIS FILE EXISTS NOT TO REPEAT
-----------------------------------------------
(1) `D6RF`'s IN-PLACE STAGING -- staging that writes into the directory whose
    contents are the graded answer.  Step (2) refuses if the destination exists
    at all, step (1) refuses if the destination and the source are the same tree
    or nested either way, and steps (4)/(6) census the SOURCE before and after
    the copy and refuse if a single entry or a witness (mtime, size) moved.  A
    graded root is never mutated by this file; it is only ever read.

(2) `A1WRT`'s `rc 127` ABORT -- the original abort path expanded `$FFD_SRC` and
    `$MD5_FFD`, which were defined nowhere, so under `set -u` the REFUSAL ITSELF
    died at 127 and printed NO abort message, on an item whose entire discipline
    is that every refusal names itself.  Two independent defences here, because
    one of them is static and could be wrong about reachability:
      (a) `g_unbound_py()` -- the same question `a1wrt2_grade.g_unbound` asks of
          a shell launcher ("is every name bound before it is read?"), asked of
          THIS file with `symtable`, and run over this file's own bytes BEFORE
          any staging happens.  A `NameError` inside an abort branch is exactly
          the Python spelling of the `rc 127` class.
      (b) EVERY abort site is DRIVEN by the selftest, or is DECLARED undrivable
          with its reason, and the two sets are asserted to partition the sites
          the AST actually finds.  A static check can be wrong about which line
          runs; an executed abort cannot.  `ABORT_SITES_UNDRIVABLE` is part of
          the freeze and a new undriven abort makes the selftest refuse.
    HONEST LIMIT, STATED: `g_unbound_py` is a scope analysis, not a type
    checker.  It sees an unbound NAME.  It does not see an abort that formats a
    bound name with the wrong `%` arity, and no static check here claims to.

(3) `D4S-F3S-AGE-DEF-1` -- a staged INPUT graded under the clause meant for
    PRODUCTS.  `cp -a` / `copy2` preserve mtimes, so a staged file can never
    post-date the launch and an age clause pointed at one is unsatisfiable by
    construction.  WHICH SIDE THIS FILE IS ON, stated because the brief asks and
    because the answer is not obvious: the age datum is a DEDICATED SENTINEL
    (`.a1wrt2_age_ref`) created in THIS ITEM'S RUN ROOT and touched LAST, after
    every copy, every removal and every decompression -- the run-root-stamped
    form the family measured to be safe -- and NOT a copied file, whose mtime
    preservation is exactly what defeats an age guard.  Three clauses, and they
    are complementary rather than duplicates:
      * `STAGED_INPUTS` and `PRODUCTS` are declared disjoint, and the disjointness
        is asserted at import time, not assumed;
      * every staged input is asserted NOT NEWER than the datum;
      * every PRODUCT name is asserted ABSENT from the staged tree when staging
        ends, so a product can only ever appear by being produced, and will then
        be strictly newer than the datum by construction rather than by hope.

(4) `writeCompression on` -- MEASURED, `A1WRT/alpha12_symmetry/system/controlDict:12`,
    and the source `4000/` on disk carries `U.gz`, not `U`.  `a1wrt2_grade.py`'s
    `g_coldstart_seam` reads `case/4000/U` as text and requires the token
    `nonuniform` in it.  A tree staged with the compressed fields left as they
    are would refuse that HARD gate on a perfectly good continuation.  Step (8)
    decompresses the staged time directory, preserving each file's mtime, and
    THEN drives the REAL `g_coldstart_seam` over the staged result -- so the
    coupling between this stager and that gate is a driven measurement here and
    not an assumption in either file.

(5) `a1wr_cmd.sh:51` -- `rm -rf 0 && cp -r 0.orig 0`, unconditional, printing
    `A1WR_COLD_START`.  The inherited command script COLD-STARTS every unit, and
    `A1WRT`'s own `system/controlDict` carries `startFrom startTime; startTime 0`.
    Neither can produce the CONTINUED arm this item registers.  THIS FILE CANNOT
    REPAIR THAT and does not pretend to: `a1wr_cmd.sh` is another item's frozen
    instrument (draft section 11 item 8) and a lane editing it would break two
    freezes.  What it does instead is make the failure LOUD AND EARLY:
      * step (7) removes `0/` AND `0.orig/` from the copy, so `a1wr_cmd.sh:32`'s
        own `test -d 0.orig` refuses with its NAMED `exit 92` before a single
        core-minute is spent, instead of silently resetting the state and
        producing a cold run that the ledger would record as a restart;
      * step (9) REFUSES, named, unless the staged `system/controlDict` declares
        a continuation.  It does NOT author one: no instrument in draft section
        11's list derives a CONTINUED controlDict, and inventing one inside a
        stager would be registering a gate's implementation where no reviewer
        would look for it.  The gap is surfaced, not filled.

NOTHING HERE IS FILED, SENT, UPLOADED, POSTED OR REGISTERED ANYWHERE.
"""

from __future__ import annotations

import argparse
import ast
import builtins
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import symtable
import sys
import tempfile
import time
from pathlib import Path

# =============================================================================
# REGISTERED CONSTANTS.  Draft sections 3 and 4.
# =============================================================================

ITEM = "A1WRT2"

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]

# The pins are IMPORTED from the grader, never retyped.  A retyped pin is a
# second copy that can drift, and the drift is silent until an item fails on a
# hash nobody can locate.
sys.path.insert(0, str(HERE))
import a1wrt2_grade as G                                            # noqa: E402

PIN_RUNSCRIPT_MD5 = G.PIN_RUNSCRIPT_MD5
REGISTERED_RUN_ROOT = G.RUN_ROOT

# The producer lives in ANOTHER ITEM'S directory and is inherited unchanged by
# md5 (draft section 3).  It is named here as a path, so the instrument-table
# extraction (`a1wrt2_instruments.py`, DAFOAM_CHARTER section 18.3) derives it
# rather than depending on anyone remembering that it is a dependency at all --
# a dependency in a sibling item's directory is exactly the shape `SO2a` missed.
PRODUCER_SRC = REPO / "cases/dafoam/ladder-a/A1/wall_resolved_aoa_polar/a1wr_runScript_incomp.py"
LAUNCHER_SRC = HERE / "a1wrt2_run_arm.sh"

# Draft section 3: SEAM continues A1WRT U1's 4000/.
SEAM_SRC_DEFAULT = "/home/ubuntu/certonomous-runs/A1WRT/alpha12_symmetry"
SEAM_SRC_TIME = "4000"

# ---- THE CONTINUATION controlDict, AS A COMMITTED STATIC FIXTURE ------------
# ⚠ ADDED 2026-09-05.  Draft section 11.3.2 measured that NOTHING in the
# registered set produced a CONTINUED `system/controlDict`: the string
# `controlDict` occurs 0 times in the frozen producer and 0 times in the
# launcher, and clause (9) below REFUSES rather than authors one.  The real
# staging source carries `startFrom startTime; startTime 0`, so clause (9)'s
# own predicate -- imported and driven against those real bytes -- returned
# False and aborted CONTROLDICT_NOT_CONTINUED at code 5, FOR BOTH ARMS.  The
# item could not have staged anything.
#
# THE REPAIR KEEPS CLAUSE (9)'s STANCE EXACTLY.  The stager still does not
# AUTHOR a start condition; it stages a REVIEWABLE, COMMITTED, md5-PINNED
# artefact and then asserts over the staged bytes as before.  Clause (9)'s
# stated reason -- that a silently authored start condition would be "a
# registered gate where no reviewer would look for it" -- is satisfied by
# putting the bytes where a reviewer does look: in the freeze commit.
# ⚠ THE TWO FIXTURES ARE BOUND THROUGH `FIXTURES / "<literal>"`, AND THE FORM IS
# LOAD-BEARING.  `a1wrt2_instruments.py` resolves module-level `HERE`/`FIXTURES`
# joins out of the AST; a path assembled from a dict VALUE is DYNAMIC and never
# enters the instrument table.  Written first as `"fixtures/..." ` strings inside
# the dict, these two files were staged and md5-asserted by the stager while the
# extraction table reported `15 present, 0 ABSENT` WITHOUT THEM -- which is draft
# section 11 item 2's stated failure mode word for word: *"an md5-agreement
# control can read 8 of 8 while a dependency the frozen code executes is
# absent."*  This is the same lesson `a1wrt2_run_arm.sh`'s MANIFEST producer
# records: WRITE IT IN THE FORM THE EXTRACTOR READS DIRECTLY, rather than
# widening the extractor to follow an inference a reader cannot check.
FIXTURES = HERE / "fixtures"
CONTROLDICT_SEAM = FIXTURES / "controlDict_SEAM_continued"
CONTROLDICT_TAIL = FIXTURES / "controlDict_TAIL_continued"
CONTROLDICT_FIXTURE = {
    "SEAM": (CONTROLDICT_SEAM, "ddcedcff52df02e9aa8d64ffd504ebdf"),
    "TAIL": (CONTROLDICT_TAIL, "b81adcc9d4062fa8b121bff0baab22fc"),
}

ARMS = ("SEAM", "TAIL")

# ---- the two DISJOINT lists the age clause is built on ----------------------
# Run-root relative.  A name in PRODUCTS is a name the RUN must create and the
# age clause grades STRICTLY NEWER than the datum.  A name in STAGED_INPUTS is
# carried in by this file, is never produced, and is graded by the INVERSE
# clause: NOT NEWER than the datum.  The two clauses are complementary and
# jointly exhaustive over the registered names.
#
# `SEAM/out/rc` IS IN THIS LIST AND `a1wrt2_grade.grade()` DOES NOT READ IT.
# The instrument-table extraction surfaced that asymmetry: `grade()` reads
# `root/"TAIL"/"out"/"rc"` and never the SEAM arm's own rc, while the grader's
# happy-path fixture builds `SEAM/out/rc` anyway.  Draft section 4.1 is about
# exactly this shape one item earlier -- `A1WRT`'s `G-COMPLETE` was evaluated on
# `tail_empty` alone and *"U1's rule-4 completion was never gated by anything"* --
# and the same asymmetry is here, in the successor written to repair it.  The
# name is DECLARED as a product because the SEAM arm genuinely writes one; making
# a gate read it is the grader's business and the supervisor's call, and is
# reported rather than taken by this lane.
PRODUCTS = (
    "MANIFEST.json",
    "ledger.txt",
    "SEAM/out/sweep.log",
    "SEAM/out/rc",
    "TAIL/out/sweep.log",
    "TAIL/out/rc",
    "TAIL/out/warp_probe.json",
)
STAGED_INPUTS = (
    "run_arm.sh",
    "runScript.py",
)

# =============================================================================
# THE REGISTERED DEFERRAL REGISTRY.  Draft section 11 item 1a, added by the
# dafoam-supervisor's 2026-09-04 section 11.1 amendment.
#
# A name here is a gate input that NOTHING IN THE REGISTERED SET PRODUCES, kept
# LEGAL only by naming what would produce it, why it is deferred, and -- the
# clause that does the work -- WHAT REFUSES IF IT IS ABSENT AT GRADE TIME.
# `a1wrt2_instruments.producer_trace` reads this dict out of this file's AST and
# REFUSES on an entry missing any of the three keys: a deferral without a
# refusal is a hole, and a hole with a name is still a hole.
#
# ⚠ THERE IS EXACTLY ONE ENTRY AND IT COSTS THIS ITEM A REGISTERED DISCHARGE.
# `TAIL/out/warp_probe.json` is `G-WARPPROBE`'s only input, and draft section
# 7.2 registers that gate as the instrument that DISCHARGES
# `DAFOAM_CHARTER.md` section 6's two-row (shipped vs patched) obligation --
# *"with the probe output cited as the discharge"*.  Measured in the 2026-09-04
# invocation, over three named files:
#
#     `warp_probe` in a1wr_runScript_incomp.py (the frozen producer)   0
#     `warp_probe` in a1wr_cmd.sh              (the frozen container)  0
#     `warp_probe` in a1wrt2_run_arm.sh        (this item's launcher)  0
#
# so the ONLY writer anywhere is `a1wrt2_grade.py:1380`, inside
# `_build_happy_root`, WHICH IS THE SELFTEST FIXTURE BUILDER.  The item was one
# freeze away from discharging a CHARTER OBLIGATION with a number only its own
# test fixture could ever produce.
#
# IT CANNOT BE REPAIRED BY THIS LANE AND THE REASON IS A RULE, NOT A
# DIFFICULTY: emitting the probe means counting `warper_init` / `warper_jacvec`
# calls from inside the running process, which means editing
# `a1wr_runScript_incomp.py` -- ANOTHER ITEM'S FROZEN INSTRUMENT
# (`CLAUDE.md` rule 6).  It is REPORTED, NOT REPAIRED.
#
# CONSEQUENCE, STATED RATHER THAN LEFT TO BE DISCOVERED AT THE FREEZE:
# **draft section 7.2's DISCHARGE IS NOT AVAILABLE AS THIS ITEM STANDS.**  The
# two-row obligation BINDS unless a successor writes the producer.  The gate
# still exists and still refuses; what it can no longer do is DISCHARGE.
DEFERRED_PRODUCERS = {
    "TAIL/out/warp_probe.json": {
        "producer": "NONE IN THE REGISTERED SET.  It would have to be emitted "
                    "from inside the running process by the staged producer "
                    "`a1wr_runScript_incomp.py`, which is `A1WR`'s FROZEN "
                    "instrument (md5 d48f48c5e2e41e86981acbf6feccb3c4) and is "
                    "inherited by this item unchanged.  Writing it here would "
                    "break two freezes, so it is reported, not repaired.",
        "why_deferred": "measured 2026-09-04: `warp_probe` occurs 0 times in "
                        "a1wr_runScript_incomp.py, 0 times in a1wr_cmd.sh and "
                        "0 times in a1wrt2_run_arm.sh; the only write in the "
                        "repository is a1wrt2_grade.py:1380, inside the "
                        "selftest fixture builder `_build_happy_root`.",
        "refuses_if_absent": "a1wrt2_grade.grade() reads it through "
                             "`read_text`, which calls `check(path.exists())` "
                             "and raises Refuse(code=2).  An absent probe is a "
                             "REFUSAL and an item-level `NOT A RESULT`, never "
                             "a passing G-WARPPROBE.  Driven by the control "
                             "`Q-DEFERRAL-warpprobe-absent-refuses`.",
    },
}
# The per-arm case trees this file creates.  Declared as a tuple of string
# literals because `a1wrt2_instruments.py` reads these three tuples OUT OF THIS
# FILE'S AST and checks them against the run-root names the GRADER extracts from
# its own source -- so "does the stager make what the grader reads?" is a
# measurement over two files' bytes, not a claim either file makes about itself.
STAGED_CASE_DIRS = (
    "SEAM/case",
    "TAIL/case",
)

AGE_REF = ".a1wrt2_age_ref"

# Names dropped from the COPY.  `0/` and `0.orig/` are dropped for the reason in
# defect (5); the rest are the source run's own outputs, which would otherwise
# sit in this item's run root looking like this item's answers.
CARRYOVER_DROP = (
    "0", "0.orig", "out", "reports", "postProcessing", "mphys.html",
    ".a1wrt_age_datum", AGE_REF,
)

# Abort sites this selftest CANNOT drive, each with the reason it cannot.  The
# selftest asserts that the abort sites the AST finds are exactly the driven
# ones plus these -- so a NEW undriven abort refuses, which is the whole point.
ABORT_SITES_UNDRIVABLE = {
    "SOURCE_CHANGED":
        "fires only if the source tree is mutated by another process BETWEEN "
        "the two censuses.  Driving it would require a test-only hook inside "
        "the staging path, and a branch that exists only for the selftest is a "
        "branch the graded run does not execute.",
    "CARRYOVER_SURVIVES":
        "a post-condition re-read after a successful `rmtree`/`unlink`; it can "
        "only fire on a filesystem fault, which this box cannot inject.",
    "PRODUCT_PRESENT_IN_STAGE":
        "same shape: re-read after removal, reachable only on a filesystem "
        "fault.  It is kept because it is the clause that makes 'a product can "
        "only appear by being produced' true rather than assumed.",
    "COPY_FAILED":
        "requires the copy itself to raise (out of space, permission fault). "
        "Not injectable here without running as another user.",
    "ZERO_DIR_SURVIVES":
        "the SECOND, narrower re-read of the two names that matter most, taken "
        "after CARRYOVER_SURVIVES has already passed.  Reachable only if a "
        "successful removal leaves the entry behind.  It is kept, undriven and "
        "declared, because it is the clause a reader of a future diff will look "
        "for when asking whether 0.orig/ can come back.",
    "MANIFEST_SELFCHECK":
        "the manifest is written and read back in the same function; making the "
        "read-back disagree needs a test-only hook between the write and the "
        "read, and a branch that exists only for the selftest is a branch the "
        "graded run does not execute.",
}


class Refuse(Exception):
    """A refusal carrying its own exit code and its own NAME."""

    def __init__(self, token: str, message: str, code: int = 5):
        super().__init__(message)
        self.token = token
        self.code = code


def abort(token: str, message: str, code: int = 5) -> None:
    """EVERY refusal in this file goes through here, so every refusal NAMES
    ITSELF.  `A1WRT`'s original abort died before it could print anything; this
    one cannot, because the token is a required positional argument and the
    message is formatted by the caller before the call is made."""
    raise Refuse(token, message, code)


def say(lines: list, text: str) -> None:
    lines.append(text)
    print(text)


# =============================================================================
# `g_unbound_py` -- defect (2)(a).  The Python spelling of `G-UNBOUND`.
# =============================================================================

_BUILTINS = frozenset(dir(builtins)) | {"__file__", "__name__", "__doc__",
                                        "__debug__", "__spec__", "__package__",
                                        "__loader__", "__builtins__"}


def _scope_bound(sc: symtable.SymbolTable) -> set:
    out = set()
    for s in sc.get_symbols():
        if s.is_assigned() or s.is_parameter() or s.is_imported():
            out.add(s.get_name())
    return out


def g_unbound_py(source: str, filename: str = "<a1wrt2_stage>") -> tuple:
    """Every name READ in this module is bound before it can be read.

    The shell gate `a1wrt2_grade.g_unbound` asks exactly this question of a
    launcher's `$VAR` expansions under `set -u`.  A Python file cannot be read by
    that gate -- it has no `$` expansions and no `set -u` -- and pretending
    otherwise would be a control that reports on a question it never asked.  So
    the QUESTION is ported rather than the reader, and the port is stated as a
    port.  A name referenced at module or function scope, resolving to the
    global scope, that is never bound at module scope and is not a builtin, is a
    `NameError` waiting on whichever branch reaches it first -- and in `A1WRT`
    the branch that reached it first was the ABORT.

    Returns ("PASS"|"BLOCKED", notes)."""
    try:
        top = symtable.symtable(source, filename, "exec")
    except SyntaxError as e:
        return "BLOCKED", ["G-UNBOUND-PY: BLOCKED -- %s does not parse: %s"
                           % (filename, e)]
    module_bound = _scope_bound(top)
    findings = []

    def walk(sc: symtable.SymbolTable, path: str) -> None:
        for s in sc.get_symbols():
            name = s.get_name()
            if not s.is_referenced():
                continue
            if s.is_local() or s.is_parameter() or s.is_imported():
                continue
            if s.is_free():          # closure over an enclosing function scope
                continue
            if name in module_bound or name in _BUILTINS:
                continue
            findings.append(
                "%s: name %r is read but never bound at module scope and is "
                "not a builtin -- a NameError on whichever branch reaches it "
                "first, which in A1WRT was the ABORT itself" % (path, name))
        for child in sc.get_children():
            walk(child, "%s.%s" % (path, child.get_name()))

    walk(top, "<module>")
    if findings:
        return "BLOCKED", ["G-UNBOUND-PY: BLOCKED -- the stager does not run"] \
            + ["  " + f for f in findings]
    return "PASS", ["G-UNBOUND-PY: PASS -- every name read is bound before it "
                    "can be read, in every scope"]


def abort_sites(source: str) -> set:
    """Every abort TOKEN this file can raise, read out of its own AST.

    Enumerated rather than listed, for the reason `DAFOAM_CHARTER.md` section
    18.3 gives about instrument tables: a list written from memory always can
    miss the site its author had not yet written; a list derived from the code
    cannot."""
    tree = ast.parse(source)
    out = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "abort"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)):
            out.add(node.args[0].value)
    return out


# =============================================================================
# THE STAGING STEPS
# =============================================================================


def md5_of(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def _census(root: Path) -> tuple:
    """(entry count, witness (mtime, size) table) over the SOURCE.  Read twice,
    before and after the copy, and compared -- so `D6RF`'s in-place staging
    class cannot pass unnoticed even if some later step reached for the source
    with a write."""
    n = 0
    wit = {}
    for dirpath, dirnames, filenames in os.walk(root):
        n += len(dirnames) + len(filenames)
        for f in filenames:
            fp = Path(dirpath) / f
            rel = str(fp.relative_to(root))
            try:
                st = fp.stat()
            except OSError:
                continue
            wit[rel] = (int(st.st_mtime), st.st_size)
    return n, wit


def _iter_files(root: Path):
    for dirpath, _d, filenames in os.walk(root):
        for f in filenames:
            yield Path(dirpath) / f


def stage(arm: str, run_root: Path, src: Path, out: list) -> dict:
    """Stage one arm.  Returns the manifest dict.  Every step refuses by NAME."""
    if arm not in ARMS:
        abort("USAGE", "arm %r is not one of %s" % (arm, list(ARMS)), 64)

    dst_arm = run_root / arm
    dst_case = dst_arm / "case"

    # ---- (1) G-ROOT.  This item's root only, and never the source's. --------
    rr = os.path.realpath(str(run_root))
    ss = os.path.realpath(str(src))
    if rr != os.path.realpath(REGISTERED_RUN_ROOT) and not os.environ.get(
            "A1WRT2_STAGE_ALLOW_ALT_ROOT"):
        abort("ROOT_NOT_REGISTERED",
              "run root %s is not the registered %s.  A stager that will write "
              "anywhere is a stager that will one day write into a graded root."
              % (rr, REGISTERED_RUN_ROOT), 3)
    if rr == ss:
        abort("ROOT_EQUALS_SOURCE",
              "the run root and the staging source are the same tree (%s).  "
              "That is D6RF's in-place staging defect exactly." % rr, 3)
    if rr.startswith(ss + os.sep) or ss.startswith(rr + os.sep):
        # SEAM's own case is a legitimate source for TAIL, and it lives INSIDE
        # this run root -- so the nesting rule is stated as the narrow one it
        # has to be, rather than as a blanket that would forbid the registered
        # chain and then be switched off by whoever hit it first.
        if not (arm == "TAIL" and ss == os.path.realpath(str(run_root / "SEAM" / "case"))):
            abort("ROOT_NESTED",
                  "run root %s and source %s are nested, and the source is not "
                  "the registered SEAM->TAIL continuation" % (rr, ss), 3)
    say(out, "%s_STAGE_%s (1) G-ROOT OK run_root=%s src=%s" % (ITEM, arm, rr, ss))

    # ---- (2) THE DESTINATION MUST NOT EXIST.  Never mutate a graded root. ---
    if dst_case.exists():
        abort("DEST_EXISTS",
              "destination %s already exists.  Refusing to overwrite evidence: "
              "a stager that overwrites is a stager that can silently re-stage "
              "a graded arm between the run and the grade." % dst_case, 5)
    say(out, "%s_STAGE_%s (2) destination %s does not exist" % (ITEM, arm, dst_case))

    # ---- (3) THE SOURCE MUST BE CONTINUABLE. --------------------------------
    if not src.is_dir():
        abort("SOURCE_ABSENT", "staging source %s is absent" % src, 5)
    tdir = src / SEAM_SRC_TIME if arm == "SEAM" else _latest_time_dir(src)
    if tdir is None or not tdir.is_dir():
        abort("SOURCE_NOT_CONTINUABLE",
              "no continuation time directory under %s.  This item's arms are "
              "registered CONTINUED (draft section 3); there is nothing to "
              "continue FROM, and a cold start here would be a second variable "
              "against the alpha 0..12 body the tail exists to extend." % src, 5)
    ufield = None
    for cand in (tdir / "U", tdir / "U.gz"):
        if cand.exists():
            ufield = cand
            break
    if ufield is None:
        abort("SOURCE_NOT_CONTINUABLE",
              "time directory %s carries neither U nor U.gz -- it is not a "
              "solved state" % tdir, 5)
    say(out, "%s_STAGE_%s (3) continuation state %s (%s)"
        % (ITEM, arm, tdir, ufield.name))

    # ---- (4) CENSUS THE SOURCE BEFORE. --------------------------------------
    n0, wit0 = _census(src)
    say(out, "%s_STAGE_%s (4) source census entries=%d files=%d"
        % (ITEM, arm, n0, len(wit0)))

    # ---- (5) COPY, NEVER MOVE, mtimes PRESERVED. ----------------------------
    dst_case.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(str(src), str(dst_case), symlinks=True,
                        copy_function=shutil.copy2)
    except Exception as e:                                       # noqa: BLE001
        abort("COPY_FAILED", "copy %s -> %s failed: %s" % (src, dst_case, e), 4)
    say(out, "%s_STAGE_%s (5) copied, mtime semantics = copy2, PRESERVE"
        % (ITEM, arm))

    # ---- (6) CENSUS THE SOURCE AFTER.  It must not have moved. --------------
    n1, wit1 = _census(src)
    if n0 != n1 or wit0 != wit1:
        moved = sorted(set(wit0) ^ set(wit1)) or sorted(
            k for k in wit0 if wit0.get(k) != wit1.get(k))
        abort("SOURCE_CHANGED",
              "the SOURCE tree changed during staging (entries %d -> %d; first "
              "differing: %s).  The source of a continuation is a graded "
              "artefact and this file only ever reads it."
              % (n0, n1, moved[:3]), 5)
    say(out, "%s_STAGE_%s (6) SOURCE INTACT: %d entries, %d witnesses unchanged"
        % (ITEM, arm, n1, len(wit1)))

    # ---- (7) SIBLING PROTECTION, and the cold-start drop. -------------------
    dropped = []
    for name in CARRYOVER_DROP:
        p = dst_case / name
        # SYMLINKS FIRST, and the order is load-bearing.  `copytree(symlinks=
        # True)` reproduces a symlinked `0 -> ../somewhere` as a symlink, and
        # `Path.is_dir()` follows it, so a `rmtree` here would raise OSError and
        # the refusal would leave this file as an UNNAMED traceback -- the
        # A1WRT `rc 127` class with a different spelling.
        if p.is_symlink():
            p.unlink()
            dropped.append(name + "@")
        elif p.is_dir():
            shutil.rmtree(str(p))
            dropped.append(name + "/")
        elif p.exists():
            p.unlink()
            dropped.append(name)
    for p in list(dst_case.glob("*.log")) + list(dst_case.glob("log.*")):
        p.unlink()
        dropped.append(p.name)
    for name in CARRYOVER_DROP:
        if (dst_case / name).exists():
            abort("CARRYOVER_SURVIVES",
                  "carry-over %s survives in the copy at %s"
                  % (name, dst_case / name), 5)
    if (dst_case / "0").exists() or (dst_case / "0.orig").exists():
        abort("ZERO_DIR_SURVIVES",
              "0/ or 0.orig/ survives in the staged copy.  G-COLDSTART-SEAM "
              "refuses a continued arm that also carries 0/, and a surviving "
              "0.orig/ lets a1wr_cmd.sh:51 (`rm -rf 0 && cp -r 0.orig 0`) "
              "resurrect a cold start that the ledger would then record as a "
              "restart.", 5)
    say(out, "%s_STAGE_%s (7) dropped %d carry-overs: %s"
        % (ITEM, arm, len(dropped), " ".join(sorted(dropped)) or "(none)"))
    say(out, "%s_STAGE_%s (7) 0/ and 0.orig/ are ABSENT from the copy -- "
             "a1wr_cmd.sh:32's own `test -d 0.orig` now refuses at its NAMED "
             "exit 92 BEFORE any compute, instead of cold-starting silently"
        % (ITEM, arm))

    # ---- (8) DECOMPRESS the staged time directory.  Defect (4). -------------
    staged_t = dst_case / tdir.name
    ndec = 0
    for gz in sorted(staged_t.glob("*.gz")):
        plain = staged_t / gz.name[:-3]
        st = gz.stat()
        try:
            with gzip.open(str(gz), "rb") as fh:
                data = fh.read()
        except Exception as e:                                   # noqa: BLE001
            abort("DECOMPRESS_FAILED",
                  "staged field %s does not decompress: %s.  A field that "
                  "cannot be read is not a continuation state." % (gz, e), 4)
        plain.write_bytes(data)
        os.utime(str(plain), (st.st_atime, st.st_mtime))
        gz.unlink()
        ndec += 1
    say(out, "%s_STAGE_%s (8) decompressed %d fields in %s, mtimes PRESERVED "
             "(writeCompression on -- A1WRT/alpha12_symmetry/system/"
             "controlDict:12 -- and g_coldstart_seam reads case/%s/U as text)"
        % (ITEM, arm, ndec, staged_t.name, tdir.name))

    uplain = staged_t / "U"
    if not uplain.exists():
        abort("STAGED_U_NOT_NONUNIFORM",
              "staged %s is absent after decompression" % uplain, 5)
    if "nonuniform" not in uplain.read_text(errors="replace"):
        abort("STAGED_U_NOT_NONUNIFORM",
              "staged %s carries a UNIFORM internalField.  A uniform U means "
              "the state did not stage and the arm would silently cold-start; "
              "every point in it would have to be withdrawn as a tail."
              % uplain, 5)

    # ---- (8b) THE CONTINUATION controlDict, STAGED FROM A COMMITTED, PINNED
    #           FIXTURE.  Added 2026-09-05; see CONTROLDICT_FIXTURE above.
    #           This runs BEFORE clause (9) so that clause (9) still ASSERTS
    #           over staged bytes and still refuses if they are not a
    #           continuation -- the assertion is not weakened, it is finally
    #           given something to assert over.
    cd_src, cd_md5 = CONTROLDICT_FIXTURE[arm]
    cd_rel = cd_src.name
    if not cd_src.exists():
        abort("CONTROLDICT_FIXTURE_ABSENT",
              "the registered continuation controlDict fixture %s is absent.  "
              "Nothing else in the registered set produces one (draft section "
              "11.3.2: `controlDict` occurs 0 times in the frozen producer and "
              "0 times in the launcher), so without it this arm cannot stage."
              % cd_src, 5)
    got_cd = md5_of(cd_src)
    if got_cd != cd_md5:
        abort("CONTROLDICT_FIXTURE_MD5",
              "the continuation controlDict fixture %s has md5 %s, registered "
              "%s.  A start condition that can drift is a start condition no "
              "freeze pins." % (cd_src, got_cd, cd_md5), 5)
    (dst_case / "system").mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(cd_src), str(dst_case / "system" / "controlDict"))
    say(out, "%s_STAGE_%s (8b) continuation controlDict staged from %s md5=%s"
        % (ITEM, arm, cd_rel, got_cd))

    # ---- (9) THE CONTINUATION PRECONDITION.  Asserted, NOT authored. --------
    cd = dst_case / "system" / "controlDict"
    if not cd.exists():
        abort("CONTROLDICT_NOT_CONTINUED",
              "staged %s is absent -- the start condition of a CONTINUED arm "
              "cannot be read, so it cannot be shown to be a continuation" % cd,
              5)
    cdt = cd.read_text(errors="replace")
    continued = ("latestTime" in cdt) or _startTime_is(cdt, tdir.name)
    if not continued:
        abort("CONTROLDICT_NOT_CONTINUED",
              "staged system/controlDict declares neither `startFrom "
              "latestTime` nor `startTime %s`.  A1WRT's own controlDict carries "
              "`startFrom startTime; startTime 0` (MEASURED), which would COLD "
              "START this arm while the ledger recorded it as a restart.  This "
              "file REFUSES rather than authoring a controlDict: no instrument "
              "in draft section 11 derives a CONTINUED one, and a stager that "
              "quietly wrote a solver's start condition would be implementing a "
              "registered gate where no reviewer would look for it."
              % tdir.name, 5)
    say(out, "%s_STAGE_%s (9) controlDict declares a continuation from %s"
        % (ITEM, arm, tdir.name))

    # ---- (10) THE RUN-ROOT STAGED INPUTS, md5-asserted against the GRADER's
    #           own pin.  These are what `grade()` reads as root/run_arm.sh and
    #           root/runScript.py, so they are staged INPUTS and are graded by
    #           the INVERSE age clause, never as products (D4S-F3S-AGE-DEF-1).
    if not (run_root / "run_arm.sh").exists():
        if not LAUNCHER_SRC.exists():
            abort("SOURCE_ABSENT", "launcher %s absent" % LAUNCHER_SRC, 5)
        shutil.copy2(str(LAUNCHER_SRC), str(run_root / "run_arm.sh"))
    if not (run_root / "runScript.py").exists():
        if not PRODUCER_SRC.exists():
            abort("SOURCE_ABSENT", "producer %s absent" % PRODUCER_SRC, 5)
        shutil.copy2(str(PRODUCER_SRC), str(run_root / "runScript.py"))
    got = md5_of(run_root / "runScript.py")
    if got != PIN_RUNSCRIPT_MD5:
        abort("PIN_MISMATCH",
              "staged runScript.py md5 %s != the grader's pinned %s.  The tail "
              "would not be comparable to the alpha 0..12 body it extends."
              % (got, PIN_RUNSCRIPT_MD5), 4)
    say(out, "%s_STAGE_%s (10) staged inputs run_arm.sh, runScript.py "
             "(md5 %s == a1wrt2_grade.PIN_RUNSCRIPT_MD5, IMPORTED not retyped)"
        % (ITEM, arm, got))

    # ---- (11) NO PRODUCT NAME MAY EXIST YET. --------------------------------
    for name in PRODUCTS:
        p = run_root / name
        if p.exists():
            abort("PRODUCT_PRESENT_IN_STAGE",
                  "registered product %s already exists in the run root before "
                  "the run.  A product that predates the run cannot be shown to "
                  "be this run's answer." % p, 5)
    say(out, "%s_STAGE_%s (11) zero of %d registered products exist yet"
        % (ITEM, arm, len(PRODUCTS)))

    # ---- (12) THE AGE REFERENCE, TOUCHED LAST.  Defect (3). -----------------
    ref = run_root / AGE_REF
    ref.write_text("")
    now = time.time()
    os.utime(str(ref), (now, now))
    datum = int(ref.stat().st_mtime)
    (run_root / (".a1wrt2_stage_%s_copy_epoch" % arm)).write_text("%d\n" % datum)
    say(out, "%s_STAGE_%s (12) AGE DATUM %d from %s, TOUCHED LAST -- a "
             "RUN-ROOT sentinel nothing in the container writes, not a copied "
             "file whose preserved mtime is what defeats an age guard"
        % (ITEM, arm, datum, AGE_REF))

    newer = []
    for fp in _iter_files(dst_case):
        if int(fp.stat().st_mtime) > datum:
            newer.append(str(fp.relative_to(run_root)))
    for name in STAGED_INPUTS:
        p = run_root / name
        if p.exists() and int(p.stat().st_mtime) > datum:
            newer.append(name)
    if newer:
        abort("STAGED_INPUT_NEWER_THAN_DATUM",
              "%d staged file(s) are NEWER than the age datum, first: %s.  A "
              "staged input that post-dates the datum is indistinguishable from "
              "a product and would be graded by the wrong clause -- which is "
              "D4S-F3S-AGE-DEF-1 with the sign flipped."
              % (len(newer), newer[:3]), 5)
    say(out, "%s_STAGE_%s (12) VERIFIED: every staged file is NOT NEWER than "
             "the datum; every PRODUCT name is absent, so a product can only "
             "appear by being produced" % (ITEM, arm))

    # ---- (13) THE STAGED-INPUT MANIFEST, self-checked. ----------------------
    rows = []
    for name in STAGED_INPUTS:
        p = run_root / name
        if not p.exists():
            abort("SOURCE_ABSENT", "registered staged input %s absent" % p, 5)
        rows.append({"name": name, "dst_md5": md5_of(p),
                     "dst_mtime": int(p.stat().st_mtime),
                     "produced_by_this_item": False})
    man = {"item": ITEM, "arm": arm, "src": str(src), "time_dir": tdir.name,
           "age_datum": datum, "age_ref": AGE_REF,
           "decompressed_fields": ndec,
           "dropped_carryovers": sorted(dropped),
           "staged_inputs": rows,
           "products_expected": list(PRODUCTS)}
    mp = run_root / (".a1wrt2_staged_inputs_%s.json" % arm)
    mp.write_text(json.dumps(man, indent=2, sort_keys=True) + "\n")
    back = json.loads(mp.read_text())
    bad = [r["name"] for r in back["staged_inputs"]
           if r["dst_mtime"] > back["age_datum"]]
    if bad or back["age_datum"] != datum:
        abort("MANIFEST_SELFCHECK",
              "staged-input manifest self-check FAILED: %r" % (bad,), 5)
    say(out, "%s_STAGE_%s (13) staged-input manifest written and read back: "
             "%s (n=%d, datum=%d)" % (ITEM, arm, mp.name, len(rows), datum))

    say(out, "%s_STAGE_%s READY -- NOTHING WAS LAUNCHED, NO CONTAINER STARTED, "
             "NO CORE-MINUTE SPENT" % (ITEM, arm))
    return man


def _startTime_is(text: str, want: str) -> bool:
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("startTime"):
            tok = s.rstrip(";").split()
            if len(tok) >= 2:
                try:
                    if float(tok[1]) == float(want):
                        return True
                except ValueError:
                    pass
    return False


def _latest_time_dir(case: Path):
    best, bestv = None, None
    for p in case.iterdir():
        if not p.is_dir():
            continue
        try:
            v = float(p.name)
        except ValueError:
            continue
        if v <= 0.0:
            continue
        if bestv is None or v > bestv:
            best, bestv = p, v
    return best


# =============================================================================
# ENTRY POINT
# =============================================================================


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="A1WRT2 stager.  NOT FROZEN.")
    ap.add_argument("--arm", choices=list(ARMS))
    ap.add_argument("--run-root", default=REGISTERED_RUN_ROOT)
    ap.add_argument("--src", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    # THE UNBOUND PRECONDITION RUNS FIRST, OVER THIS FILE'S OWN BYTES, BEFORE
    # ANY STAGING.  Defect (2)(a).
    v, notes = g_unbound_py(Path(__file__).read_text(errors="replace"),
                            Path(__file__).name)
    for n in notes:
        print(n)
    if v != "PASS":
        print("%s_STAGE ABORT G-UNBOUND-PY -- the stager does not run and "
              "nothing is staged" % ITEM)
        return 6

    if a.selftest:
        return selftest()

    if not a.arm:
        ap.error("--arm is required unless --selftest")

    run_root = Path(a.run_root)
    src = Path(a.src) if a.src else (
        Path(SEAM_SRC_DEFAULT) if a.arm == "SEAM"
        else run_root / "SEAM" / "case")
    run_root.mkdir(parents=True, exist_ok=True)
    out = []
    try:
        stage(a.arm, run_root, src, out)
    except Refuse as e:
        print("%s_STAGE_ABORT_%s rc=%d -- %s" % (ITEM, e.token, e.code, e))
        return e.code
    return 0


# =============================================================================
# === SELFTEST BOUNDARY ===
# Everything below is the selftest.  `Q-NOASSERT` audits this file's AST and
# requires ZERO `assert` statements ANYWHERE -- above and below this line -- so
# every guard here survives `python3 -O`.  A guard that disappears under an
# optimisation flag is not a guard.
# =============================================================================

_CONTROL_LOG: list = []
_DRIVEN_ABORTS: set = set()


def _control(name: str, expect: str, fn) -> None:
    state, detail = "NOT EXERCISED", ""
    try:
        detail = fn()
        state = "EXERCISED-FAIL" if expect == "fail" else "EXERCISED-PASS"
    except Refuse as e:
        state, detail = "NOT EXERCISED", "control itself refused: %s" % e
    except Exception as e:                                       # noqa: BLE001
        state, detail = "NOT EXERCISED", "control raised %s: %s" % (
            type(e).__name__, e)
    _CONTROL_LOG.append((name, expect, state, detail))
    print("CONTROL %-34s %-15s %s" % (name, state, detail))
    if state == "NOT EXERCISED":
        raise Refuse("CONTROL_NOT_EXERCISED",
                     "control %s did not reach its %s direction -- %s"
                     % (name, expect, detail), 1)


def _must(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def _mk_source(where: Path, *, compressed=True, with_zero=True,
               uniform_U=False, continued=True, tname="4000") -> Path:
    """A synthetic A1WRT-shaped source: the same directory names, the same
    compressed fields, the same `0/` + `0.orig/` pair and the same controlDict
    keys as the REAL /home/ubuntu/certonomous-runs/A1WRT/alpha12_symmetry, so
    the controls drive the real code paths rather than a simplified one.

    The parameter is `where` and NOT `root`.  `a1wrt2_instruments.py` folds a
    parameter literally named `root` or `run_root` as the RUN ROOT, and this
    fixture builder is not one; the extractor surfaced the collision as a
    spurious run-root row and the fix belongs here rather than as a special case
    inside the extractor."""
    src = where / "src"
    (src / tname / "polyMesh").mkdir(parents=True)
    (src / "constant" / "polyMesh").mkdir(parents=True)
    (src / "system").mkdir(parents=True)
    if with_zero:
        (src / "0").mkdir()
        (src / "0").joinpath("U").write_text("internalField uniform (1 0 0);\n")
        (src / "0.orig").mkdir()
        (src / "0.orig").joinpath("U").write_text(
            "internalField uniform (1 0 0);\n")
    (src / "out").mkdir()
    (src / "out" / "sweep.log").write_text("source run output\n")
    (src / "mphys.html").write_text("<html></html>\n")
    (src / "log.checkMesh").write_text("mesh log\n")
    body = ("internalField   uniform (0.98 0.04 0);\n" if uniform_U else
            "internalField   nonuniform List<vector>\n3\n(\n"
            "(0.9987 0.0421 0)\n(0.9981 0.0433 0)\n(0.9975 0.0440 0)\n)\n;\n")
    for fname, txt in (("U", body), ("p", "internalField nonuniform 3(1 2 3);\n"),
                       ("nut", "internalField nonuniform 3(1 2 3);\n")):
        if compressed:
            with gzip.open(str(src / tname / (fname + ".gz")), "wb") as fh:
                fh.write(txt.encode())
        else:
            (src / tname / fname).write_text(txt)
    (src / tname / "polyMesh" / "points").write_text("points\n")
    (src / "constant" / "polyMesh" / "points").write_text("points\n")
    start = ("startFrom       latestTime;\nstartTime       %s;\n" % tname
             if continued else "startFrom       startTime;\nstartTime       0;\n")
    (src / "system" / "controlDict").write_text(
        start + "stopAt endTime;\nendTime 4200;\nwriteCompression on;\n")
    # Every staged file is made OLD, exactly as a real `cp -a` from a run that
    # finished yesterday would leave them.  A datum taken after the copy must
    # still be newer than all of them.
    old = time.time() - 86400
    for p in list(_iter_files(src)):
        os.utime(str(p), (old, old))
    return src


def _run_stage(arm, run_root, src) -> tuple:
    """Drive the REAL `stage()`.  Returns (token_or_None, lines)."""
    out = []
    os.environ["A1WRT2_STAGE_ALLOW_ALT_ROOT"] = "1"
    try:
        stage(arm, run_root, src, out)
        return None, out
    except Refuse as e:
        _DRIVEN_ABORTS.add(e.token)
        return e.token, out


def _leg_happy() -> None:
    """SELFTEST-SUCCESS-PATH, driven FIRST.  Every registration in this family
    that was never driven end-to-end against 'what does this print if everything
    goes right?' rehearsed only its refusals."""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        src = _mk_source(tmp)
        rr = tmp / "runroot"
        rr.mkdir()

        def go():
            tok, lines = _run_stage("SEAM", rr, src)
            _must(tok is None, "happy path refused with %s" % tok)
            _must((rr / "SEAM" / "case" / "4000" / "U").exists(),
                  "4000/U absent after staging")
            _must(not (rr / "SEAM" / "case" / "4000" / "U.gz").exists(),
                  "U.gz survived decompression")
            _must(not (rr / "SEAM" / "case" / "0").exists(), "0/ survived")
            _must(not (rr / "SEAM" / "case" / "0.orig").exists(),
                  "0.orig/ survived")
            return "staged %d lines, 4000/U present, 0/ and 0.orig/ gone" % len(lines)

        _control("stage/happy-path-stages", "pass", go)

        # The REAL hard gate, driven over the REAL staged bytes.  This is the
        # measurement that binds this stager to `G-COLDSTART-SEAM`: if the
        # decompression step were removed, THIS control would refuse.
        def gate():
            v, _n = G.g_coldstart_seam(rr / "SEAM" / "case")
            _must(v == "PASS", "g_coldstart_seam returned %s" % v)
            return "a1wrt2_grade.g_coldstart_seam -> PASS on the staged tree"

        _control("stage/real-G-COLDSTART-SEAM-passes", "pass", gate)

        # And the negative direction of that same binding: a tree staged WITHOUT
        # the decompression step (the compressed fields left as OpenFOAM wrote
        # them) makes the real gate REFUSE.  So the coupling is measured in both
        # directions rather than asserted in a comment.
        def gate_neg():
            alt = tmp / "nodecomp" / "case"
            alt.mkdir(parents=True)
            shutil.copytree(str(src / "4000"), str(alt / "4000"))
            try:
                G.g_coldstart_seam(alt)
            except G.Refuse as e:
                return "compressed-only tree -> REFUSE: %s" % str(e)[:70]
            raise ValueError("g_coldstart_seam accepted a compressed-only tree")

        _control("stage/real-gate-refuses-undecompressed", "fail", gate_neg)

        # The age clause, read off the manifest this run actually wrote.
        def age():
            man = json.loads(
                (rr / ".a1wrt2_staged_inputs_SEAM.json").read_text())
            datum = man["age_datum"]
            newest = max(int(p.stat().st_mtime)
                         for p in _iter_files(rr / "SEAM" / "case"))
            _must(newest <= datum,
                  "a staged file (mtime %d) post-dates the datum %d"
                  % (newest, datum))
            _must(set(PRODUCTS).isdisjoint(set(STAGED_INPUTS)),
                  "PRODUCTS and STAGED_INPUTS overlap")
            for name in PRODUCTS:
                _must(not (rr / name).exists(),
                      "product %s exists before the run" % name)
            return ("datum=%d newest staged=%d delta=%ds; 0 of %d products "
                    "present" % (datum, newest, datum - newest, len(PRODUCTS)))

        _control("stage/age-datum-postdates-staging", "pass", age)

        # The SEAM -> TAIL chain, which is the one nesting case the G-ROOT rule
        # has to admit.  It is driven, so the exception cannot be a story.
        def chain():
            (rr / "SEAM" / "case" / "4200").mkdir()
            (rr / "SEAM" / "case" / "4200" / "U").write_text(
                "internalField   nonuniform List<vector>\n1\n((1 0 0))\n;\n")
            (rr / "SEAM" / "case" / "system" / "controlDict").write_text(
                "startFrom latestTime;\nstartTime 4200;\nendTime 8200;\n")
            old = time.time() - 3600
            for p in _iter_files(rr / "SEAM" / "case"):
                os.utime(str(p), (old, old))
            tok, _l = _run_stage("TAIL", rr, rr / "SEAM" / "case")
            _must(tok is None, "TAIL staging refused with %s" % tok)
            _must((rr / "TAIL" / "case" / "4200" / "U").exists(),
                  "TAIL 4200/U absent")
            return "TAIL staged from SEAM/case (the admitted nesting case)"

        _control("stage/SEAM-to-TAIL-chain", "pass", chain)

    # A SYMLINKED `0` -- the shape that would have made the carry-over drop
    # raise an UNNAMED OSError instead of refusing by name.  Driven on real
    # bytes, in the PASS direction: staging must succeed and `0@` must be gone.
    with tempfile.TemporaryDirectory() as td2:
        tmp2 = Path(td2)
        src2 = _mk_source(tmp2, with_zero=False)
        (tmp2 / "elsewhere").mkdir()
        (tmp2 / "elsewhere" / "U").write_text("internalField uniform (1 0 0);\n")
        os.symlink(str(tmp2 / "elsewhere"), str(src2 / "0"))
        rr2 = tmp2 / "runroot"
        rr2.mkdir()

        def symlinked():
            tok, _l = _run_stage("SEAM", rr2, src2)
            _must(tok is None, "a symlinked 0/ refused with %s" % tok)
            _must(not (rr2 / "SEAM" / "case" / "0").is_symlink(),
                  "the symlinked 0 survived")
            _must((tmp2 / "elsewhere" / "U").exists(),
                  "the symlink target was followed and deleted")
            return "symlinked 0/ dropped as a link; its target untouched"

        _control("stage/symlinked-zero-dropped-safely", "pass", symlinked)


def _leg_refusals() -> None:
    """Every abort site that CAN be driven, driven -- because a static scope
    check can be wrong about which branch runs, and an executed abort cannot."""

    def drive(name, want_token, build, arm="SEAM", root_name="runroot"):
        def fn():
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td)
                rr = tmp / root_name
                rr.mkdir()
                src = build(tmp, rr)
                tok, _l = _run_stage(arm, rr, src)
                _must(tok == want_token,
                      "expected %s, got %s" % (want_token, tok))
                return "-> A1WRT2_STAGE_ABORT_%s" % tok
        _control(name, "fail", fn)

    drive("abort/source-absent", "SOURCE_ABSENT",
          lambda tmp, rr: tmp / "no_such_source")

    def _nozero(tmp, rr):
        s = _mk_source(tmp)
        shutil.rmtree(str(s / "4000"))
        return s
    drive("abort/source-not-continuable", "SOURCE_NOT_CONTINUABLE", _nozero)

    def _exists(tmp, rr):
        s = _mk_source(tmp)
        (rr / "SEAM" / "case").mkdir(parents=True)
        return s
    drive("abort/dest-exists", "DEST_EXISTS", _exists)

    def _same(tmp, rr):
        s = _mk_source(tmp)
        shutil.rmtree(str(rr))
        shutil.copytree(str(s), str(rr))
        return rr
    drive("abort/root-equals-source", "ROOT_EQUALS_SOURCE", _same)

    def _nested(tmp, rr):
        s = _mk_source(tmp)
        inner = rr / "inner"
        shutil.copytree(str(s), str(inner))
        return inner
    drive("abort/root-nested", "ROOT_NESTED", _nested)

    def _uniform(tmp, rr):
        return _mk_source(tmp, uniform_U=True)
    drive("abort/uniform-U-refuses", "STAGED_U_NOT_NONUNIFORM", _uniform)

    # ⚠ THIS CONTROL CHANGED MEANING ON 2026-09-05 AND THE OLD FORM IS RECORDED
    # RATHER THAN QUIETLY REPLACED.  Until clause (8b) existed, the staged
    # controlDict came from the SOURCE tree, so a non-continued SOURCE was what
    # clause (9) refused -- and that is what `_cold` planted.  Clause (8b) now
    # OVERWRITES the copied controlDict with a committed, md5-pinned fixture, so
    # a non-continued source can no longer reach clause (9) at all and `_cold`
    # stopped firing.  **That is the repair working, not the control failing:**
    # draft section 11.3.2 measured that the real source's controlDict is
    # `startFrom startTime; startTime 0`, so under the old code EVERY REAL RUN
    # took the `_cold` path and BOTH ARMS ABORTED.
    #
    # THE REMAINING FAILURE MODE IS DIFFERENT AND IS WHAT IS NOW DRIVEN: someone
    # edits the fixture to a non-continued start condition AND re-pins its md5.
    # The pin cannot catch that -- it agrees by construction -- so clause (9) is
    # the only thing between a re-pinned fixture and a silent cold start.  It is
    # driven here with exactly that: a fixture whose bytes are wrong and whose
    # md5 is right.
    def _cold_fixture(tmp, rr):
        src = _mk_source(tmp)
        bad = tmp / "bad_controlDict"
        bad.write_text("startFrom       startTime;\nstartTime       0;\n"
                       "stopAt endTime;\nendTime 4200;\n")
        CONTROLDICT_FIXTURE["SEAM"] = (bad, md5_of(bad))
        return src

    def _restore_fixture():
        CONTROLDICT_FIXTURE["SEAM"] = (CONTROLDICT_SEAM,
                                       "ddcedcff52df02e9aa8d64ffd504ebdf")
    try:
        drive("abort/controldict-not-continued", "CONTROLDICT_NOT_CONTINUED",
              _cold_fixture)
    finally:
        _restore_fixture()

    # -- (8b)'s OWN TWO REFUSALS, driven.  A fixture that is absent, and one
    #    whose bytes have drifted from the registered pin.
    def _cd_absent(tmp, rr):
        src = _mk_source(tmp)
        # ⚠ THE ABSENT PATH IS A TEMPDIR PATH, NOT `FIXTURES / "<literal>"`, AND
        # THE EXTRACTOR IS WHY.  Written first as a literal under `fixtures/`,
        # `a1wrt2_instruments.py` DERIVED IT AS A DEPENDENCY and the table came
        # back `17 present, 1 ABSENT`, rc=5 -- correctly, because a literal join
        # under the item directory is indistinguishable from a real one.  The
        # repair is to stop naming a repo file that must not exist, NOT to teach
        # the extractor to ignore one: a checker taught to skip a class of path
        # is a checker with a hole shaped like that class.  A tempdir path is
        # genuinely not a repository dependency, so nothing is being hidden.
        CONTROLDICT_FIXTURE["SEAM"] = (tmp / "no_such_controlDict", "0" * 32)
        return src
    try:
        drive("abort/controldict-fixture-absent", "CONTROLDICT_FIXTURE_ABSENT",
              _cd_absent)
    finally:
        _restore_fixture()

    def _cd_md5(tmp, rr):
        src = _mk_source(tmp)
        CONTROLDICT_FIXTURE["SEAM"] = (CONTROLDICT_SEAM, "f" * 32)
        return src
    try:
        drive("abort/controldict-fixture-md5", "CONTROLDICT_FIXTURE_MD5",
              _cd_md5)
    finally:
        _restore_fixture()

    def _corrupt(tmp, rr):
        s = _mk_source(tmp)
        (s / "4000" / "U.gz").write_bytes(b"this is not gzip at all")
        return s
    drive("abort/corrupt-gz-refuses", "DECOMPRESS_FAILED", _corrupt)

    def _pin(tmp, rr):
        s = _mk_source(tmp)
        (rr / "runScript.py").write_text("# not the pinned producer\n")
        return s
    drive("abort/pin-mismatch", "PIN_MISMATCH", _pin)

    def _newer(tmp, rr):
        s = _mk_source(tmp)
        # A staged file dated in the FUTURE is the age-guard defeat with the
        # sign flipped: it post-dates a datum taken after the copy and would be
        # graded as a product.
        fut = time.time() + 7200
        os.utime(str(s / "4000" / "U.gz"), (fut, fut))
        return s
    drive("abort/staged-input-newer-than-datum",
          "STAGED_INPUT_NEWER_THAN_DATUM", _newer)

    def _root(tmp, rr):
        s = _mk_source(tmp)
        os.environ.pop("A1WRT2_STAGE_ALLOW_ALT_ROOT", None)
        return s

    def fn_root():
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            rr = tmp / "runroot"
            rr.mkdir()
            s = _mk_source(tmp)
            os.environ.pop("A1WRT2_STAGE_ALLOW_ALT_ROOT", None)
            out = []
            try:
                stage("SEAM", rr, s, out)
            except Refuse as e:
                _DRIVEN_ABORTS.add(e.token)
                _must(e.token == "ROOT_NOT_REGISTERED",
                      "expected ROOT_NOT_REGISTERED, got %s" % e.token)
                return "-> A1WRT2_STAGE_ABORT_ROOT_NOT_REGISTERED"
            finally:
                os.environ["A1WRT2_STAGE_ALLOW_ALT_ROOT"] = "1"
            raise ValueError("an unregistered run root was accepted")

    _control("abort/root-not-registered", "fail", fn_root)

    def fn_usage():
        out = []
        try:
            stage("NOPE", Path("/tmp"), Path("/tmp"), out)
        except Refuse as e:
            _DRIVEN_ABORTS.add(e.token)
            _must(e.token == "USAGE", "expected USAGE, got %s" % e.token)
            return "-> A1WRT2_STAGE_ABORT_USAGE"
        raise ValueError("an unregistered arm was accepted")

    _control("abort/unknown-arm", "fail", fn_usage)


def _leg_unbound() -> None:
    """`g_unbound_py` in BOTH directions, and the second direction is the real
    `A1WRT` shape: a name that exists ONLY inside an abort branch."""

    def neg():
        v, _n = g_unbound_py(Path(__file__).read_text(errors="replace"),
                             Path(__file__).name)
        _must(v == "PASS", "this stager reads BLOCKED: %s" % _n)
        return "this file -> PASS"

    _control("unbound-py/this-file-passes", "pass", neg)

    def pos():
        # THE `A1WRT` rc-127 SHAPE, TRANSLATED.  `FFD_SRC` and `MD5_FFD` were
        # referenced only by the abort path and defined nowhere; under `set -u`
        # the refusal itself died at 127 and printed nothing.
        planted = (
            "def stage_it(ok):\n"
            "    if not ok:\n"
            "        raise SystemExit('ABORT ffd %s md5 %s' % (FFD_SRC, MD5_FFD))\n"
            "    return 0\n")
        v, notes = g_unbound_py(planted, "<planted_a1wrt_rc127>")
        _must(v == "BLOCKED", "the planted rc-127 shape read %s" % v)
        _must(any("FFD_SRC" in n for n in notes), "FFD_SRC not named")
        _must(any("MD5_FFD" in n for n in notes), "MD5_FFD not named")
        return "planted A1WRT rc-127 shape -> BLOCKED, both names reported"

    _control("unbound-py/planted-rc127-blocks", "fail", pos)

    def mutated():
        # The same question asked of THIS file's REAL bytes with one binding
        # removed, so the positive control is not only synthetic.
        src = Path(__file__).read_text(errors="replace")
        cut = src.replace("AGE_REF = \".a1wrt2_age_ref\"", "", 1)
        _must(cut != src, "the mutation did not change the bytes")
        v, notes = g_unbound_py(cut, "<this_file_minus_AGE_REF>")
        _must(v == "BLOCKED", "removing a real binding read %s" % v)
        _must(any("AGE_REF" in n for n in notes), "AGE_REF not named")
        return "this file minus one real binding -> BLOCKED, AGE_REF named"

    _control("unbound-py/real-binding-removed-blocks", "fail", mutated)

    def syntax():
        v, _n = g_unbound_py("def broken(:\n", "<unparseable>")
        _must(v == "BLOCKED", "unparseable source read %s" % v)
        return "unparseable source -> BLOCKED, not silently PASS"

    _control("unbound-py/unparseable-blocks", "fail", syntax)


def _leg_coverage() -> None:
    """The abort sites the AST finds must be exactly the driven ones plus the
    DECLARED undrivable ones.  This is what stops a new, silent abort path from
    entering the file after the freeze."""

    def cov():
        sites = abort_sites(Path(__file__).read_text(errors="replace"))
        undriven = sites - _DRIVEN_ABORTS - set(ABORT_SITES_UNDRIVABLE)
        stale = set(ABORT_SITES_UNDRIVABLE) - sites
        _must(not undriven,
              "abort sites present but neither driven nor declared undrivable: "
              "%s" % sorted(undriven))
        _must(not stale,
              "declared-undrivable tokens that no longer exist: %s"
              % sorted(stale))
        return ("%d abort sites: %d DRIVEN, %d DECLARED-UNDRIVABLE, 0 undriven"
                % (len(sites), len(sites & _DRIVEN_ABORTS),
                   len(ABORT_SITES_UNDRIVABLE)))

    _control("coverage/every-abort-site-accounted", "pass", cov)

    def noassert():
        src = Path(__file__).read_text(errors="replace")
        n = len([x for x in ast.walk(ast.parse(src))
                 if isinstance(x, ast.Assert)])
        _must(n == 0, "%d assert statements found; they vanish under -O" % n)
        planted = ast.parse(src + "\ndef _p():\n    assert 1 == 1\n")
        m = len([x for x in ast.walk(planted) if isinstance(x, ast.Assert)])
        _must(m == 1, "the auditor cannot see a planted assert (saw %d)" % m)
        return "ast.Assert = 0 in this file; auditor sees 1 when one is planted"

    _control("noassert/zero-and-shown-able-to-see-one", "pass", noassert)

    def disjoint():
        _must(set(PRODUCTS).isdisjoint(set(STAGED_INPUTS)),
              "PRODUCTS and STAGED_INPUTS overlap -- D4S-F3S-AGE-DEF-1")
        return ("PRODUCTS n=%d and STAGED_INPUTS n=%d are disjoint"
                % (len(PRODUCTS), len(STAGED_INPUTS)))

    _control("lists/products-and-inputs-disjoint", "pass", disjoint)


def _leg_norun() -> None:
    """The registered run root MUST NOT exist, checked BY EXECUTION.  Draft
    section 11 item 4's condition -- named as the directory that does not exist,
    and checked rather than asserted.  This lane checks it; it is the
    supervisor's to check again in the freezing shell, and a lane's check is not
    a substitute for that one."""

    def norun():
        p = Path(REGISTERED_RUN_ROOT)
        exists = p.exists()
        return ("%s exists=%s (checked by execution in this invocation; the "
                "freeze-shell check is the supervisor's)"
                % (REGISTERED_RUN_ROOT, exists))

    _control("norun/registered-run-root-checked", "pass", norun)


def selftest() -> int:
    print("%s_STAGE SELFTEST -- host python, NO container, NO compute, NO "
          "queue drop, NOT FROZEN" % ITEM)
    print("python %s   optimisation flag active: %s"
          % (sys.version.split()[0],
             "-O (asserts disabled)" if not __debug__ else "none"))
    legs = (("SELFTEST-SUCCESS-PATH", _leg_happy),
            ("SELFTEST-REFUSALS", _leg_refusals),
            ("SELFTEST-UNBOUND-PY", _leg_unbound),
            ("SELFTEST-COVERAGE", _leg_coverage),
            ("SELFTEST-NORUN", _leg_norun))
    try:
        for name, fn in legs:
            print("")
            print("---- %s ----" % name)
            fn()
    except (Refuse, ValueError) as e:
        print("%s_STAGE_SELFTEST FAILED -- %s" % (ITEM, e))
        return 1
    n_fail = len([c for c in _CONTROL_LOG if c[2] == "EXERCISED-FAIL"])
    n_pass = len([c for c in _CONTROL_LOG if c[2] == "EXERCISED-PASS"])
    n_not = len([c for c in _CONTROL_LOG if c[2] == "NOT EXERCISED"])
    print("")
    print("%s_STAGE_SELFTEST legs=%d controls=%d EXERCISED-FAIL=%d "
          "EXERCISED-PASS=%d NOT-EXERCISED=%d"
          % (ITEM, len(legs), len(_CONTROL_LOG), n_fail, n_pass, n_not))
    if n_not:
        print("%s_STAGE_SELFTEST REFUSED -- NOT EXERCISED is never a pass" % ITEM)
        return 1
    print("%s_STAGE_SELFTEST OK -- every control driven in a NAMED direction, "
          "the SUCCESS PATH first, and every abort site driven or declared"
          % ITEM)
    return 0


if __name__ == "__main__":
    sys.exit(main())
