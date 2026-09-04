#!/usr/bin/env python3
"""a1wrt2_grade.py -- the A1WRT2 grading instrument.  NOT FROZEN.  NOT PINNED.

WHAT THIS FILE IS FOR, IN ONE SENTENCE
--------------------------------------
`A1WRT2_SUCCESSOR_DRAFT.md` section 1 registers that this item's success is
called `GATE REACHED` and that it is emitted by `compose_item()` here, whose
last statement prints the single line `A1WRT2_VERDICT <token>` and nothing else.
THREE items in this family registered a composition and never wrote one:

  * `SO3aF2`  -- a LABEL-SET gap: its frozen section 5 registered only `BLOCKED`
                 and `NOT A RESULT`, two failure tokens and no success token.
  * `A1WRT`   -- an IMPLEMENTATION gap: it registered `Verdict ceiling: GATE
                 REACHED` and named `compose_item` / `verdict_before_ceiling`,
                 and `a1wrt_read.py` carries `compose_item` 0 times against 16
                 `def` sites.
  * `A1WR`    -- the same, `a1wr_read.py`, 0 against 11 `def` sites; masked all
                 along because A1WR failed on other grounds.

The generalisation, and the reason this file is shaped the way it is: NO
REGISTRATION IN THIS FAMILY WAS EVER DRIVEN END-TO-END AGAINST THE QUESTION
"WHAT DOES THIS INSTRUMENT PRINT IF EVERYTHING GOES RIGHT?"  Every one of them
rehearsed its refusals.  None rehearsed its success.  A selftest suite that only
exercises failure paths certifies that an item can DECLINE, not that it can
ANSWER.  `SELFTEST-SUCCESS-PATH` below is that missing leg and it is driven
FIRST, before any refusal leg, so it can never become the one that got skipped.

THREE PROPERTIES THE SUPERVISOR READS THIS FILE FOR
---------------------------------------------------
1. `compose_item()` exists, is arithmetic and not prose, and every HARD list is
   tested for BOTH `GATE FAIL` AND `NOT A RESULT` -- the `D19M-COMPOSE-DEF-1`
   repair (`d19m_grade.py:1533-1554`), carried here as a DRIVEN CONTROL
   (`Q-COMPOSE-1`) and not as a comment.
2. `NO ITEM VERDICT BY CONSTRUCTION` is FORBIDDEN and the forbidding is in code:
   an EXIT trap on normal exit, `SIGTERM`, `SIGINT` and `SIGHUP` prints
   `A1WRT2_VERDICT PENDING -- the composer did not run, last checkpoint <n>`
   and exits 12 rather than falling silent.  Driven by `SELFTEST-EXIT-TRAP`,
   which kills a real subprocess mid-grade.
   HONEST LIMIT, STATED AND NOT ARGUED AWAY: `SIGKILL` is not trappable by any
   process on any POSIX system.  A `SIGKILL`ed grade prints nothing, and no code
   in this file can change that.  The trap covers normal exit, uncaught
   exception, `sys.exit`, and the three catchable signals.
3. ZERO `assert` statements outside the selftest section -- this file contains
   ZERO anywhere, so the count is 0 under `python3` and 0 under `python3 -O`,
   and the selftest is identical under both flags.  A guard that disappears
   under an optimisation flag is not a guard.  `Q-NOASSERT` audits this file's
   own AST and is shown able to see a planted `assert`.

WHAT THIS FILE MAY NOT CONCLUDE (draft section 10, inherited unweakened)
------------------------------------------------------------------------
`PASS` IS UNREACHABLE BY CONSTRUCTION.  The L3 family has no Roache triple, so
no value carries a band and none is grid-converged (`G-NOBAND`); the ceiling
`GATE REACHED` caps a composed `PASS` and BOTH `raw` and `final` are printed so
the cap is visible.  NO STALL ANGLE IS REPORTED AND NONE MAY BE DERIVED
(`G-STALL` refuses at exit 2).  `P4` (`dCL/dalpha` positive to alpha=18) is
registered UNHEDGED and this lane PREDICTS IT WILL MISS.

NOTHING HERE IS FILED, SENT, UPLOADED, POSTED OR REGISTERED ANYWHERE
(`CLAUDE.md` rule 7).  SUBMISSIONS PARKED.  NO COMPUTE WAS SPENT WRITING IT.
"""

from __future__ import annotations

import argparse
import ast
import atexit
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

# =============================================================================
# THE REGISTERED CONSTANTS.  Draft sections 3, 4, 5.
# =============================================================================

ITEM = "A1WRT2"
VERDICT_TOKENS = ("PASS", "GATE REACHED", "GATE FAIL",
                  "NOT A RESULT", "BLOCKED", "PENDING")
CEILING = "GATE REACHED"

# Draft section 3, inherited by md5, nothing about the build moves.
PIN_IMG_DIGEST = ("sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523"
                  "b7dee30f6d35")
PIN_IDWARP_MD5 = "85f59e87253e0a71a813f64ca6e4c425"
PIN_RUNSCRIPT_MD5 = "d48f48c5e2e41e86981acbf6feccb3c4"
# The EXPECTED side of G-FREEZE.  It is a REGISTERED CONSTANT and is never read
# out of the manifest the run itself wrote -- an md5 table that the graded
# artefact supplies is not a freeze check, it is the artefact grading itself.
PIN_INSTRUMENTS = {"runScript.py": PIN_RUNSCRIPT_MD5}

# Draft section 5.4.
ARM_CAP_CORE_MIN = {"SEAM": 10.0, "TAIL": 675.0}
ITEM_CEILING_CORE_MIN = 685.0
CEILING_TOLERANCE = 0.02          # d6rf's float-noise limb, ported

# Draft section 3: the declared tail.
TAIL_ALPHAS = (13.0, 14.0, 15.0, 16.0, 17.0, 18.0)
SEAM_ALPHA = 12.0

# Draft section 4, `G-SEAM`.  The band is the `A1WR`/`A1WRT` R1 band 1.0e-03.
# The registered known-positive miss is 6.013254e-03 -- 6.0x the band -- so the
# control's failing direction is not marginal against its own threshold.
SEAM_BAND_REL = 1.0e-03
U1_TERMINAL_CL = 1.183635361576276
U1_TERMINAL_CD = 0.03075803313291197

# Draft section 4, `G-YPLUS`: wall-resolved means y+ max < 1.0 everywhere.
YPLUS_MAX_ALLOWED = 1.0
YPLUS_BLIND_MIN_ITERS = 200

# This item's own run root.  It does not exist and MUST NOT exist at freeze.
RUN_ROOT = "/home/ubuntu/certonomous-runs/A1WRT2"

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"

# The hard and soft lists, VERBATIM from draft section 1.  They are data, so the
# composer cannot silently disagree with the registration about which is which.
HARD_GATES = ("G-PATCH", "G-COLDSTART-SEAM", "G-IMG", "G-FREEZE", "G-UNBOUND",
              "G-NOGRAD", "G-WARPPROBE", "G-FIXTURE", "G-NOBAND", "G-STALL")
SOFT_GATES = ("G-SEAM", "G-TAILCOUNT", "G-RC-HONEST", "G-YPLUS", "G-CAPS",
              "G-CEILING")

# =============================================================================
# REFUSAL, AND THE `check` THAT REPLACES `assert`
# =============================================================================


class Refuse(Exception):
    """A refusal carrying its own exit code.  Comparators refuse rather than
    degrade (`CLAUDE.md` rule 4)."""

    def __init__(self, message: str, code: int = 2):
        super().__init__(message)
        self.code = code


def check(condition: bool, message: str, code: int = 2) -> None:
    """`assert` with the one property `assert` lacks: it survives `python3 -O`.

    THERE ARE ZERO `assert` STATEMENTS IN THIS FILE, INCLUDING IN THE SELFTEST.
    `Q-NOASSERT` audits that from this file's own AST and is shown able to see a
    planted one, so the zero is not a zero from a reader never shown able to
    return non-zero (`CLAUDE.md` rule 3)."""
    if not condition:
        raise Refuse(message, code)


# =============================================================================
# THE EXIT TRAP.  `NO ITEM VERDICT BY CONSTRUCTION` IS FORBIDDEN, IN CODE.
# =============================================================================

_CHECKPOINTS: list[str] = []
_VERDICT_EMITTED = False
_TRAP_ARMED = False


def checkpoint(name: str) -> None:
    """Record where the grade got to, so the trap can say WHERE it stopped.

    `A1ZE` ADDENDUM C's general test, adopted here for every guard: can the code
    path distinguish "the check ran and found nothing" from "the check did not
    run"?  A trap that could only say PENDING could not."""
    _CHECKPOINTS.append(name)


def _trap(*_args) -> None:
    """Print the item's outcome even when the outcome is 'neither'.

    `SO3aF2` ADDENDUM 4 section A4.4, ported by name: an instrument must always
    say which of its outcomes occurred, INCLUDING 'neither'.  `A1WRT` reached
    the end of both units and said nothing at all; that outcome is registered
    here as FORBIDDEN, and this function is the forbidding."""
    global _VERDICT_EMITTED
    if _VERDICT_EMITTED:
        return
    _VERDICT_EMITTED = True
    n = len(_CHECKPOINTS)
    where = _CHECKPOINTS[-1] if _CHECKPOINTS else "none reached"
    sys.stdout.write("%s_TRAP the composer did not run; checkpoints reached "
                     "%d, last was %s\n" % (ITEM, n, where))
    sys.stdout.write("%s_VERDICT PENDING -- the composer did not run, "
                     "last checkpoint %d\n" % (ITEM, n))
    sys.stdout.flush()
    os._exit(12)


def arm_trap() -> None:
    """Arm the trap on normal exit AND on the three catchable kill signals.

    `SIGKILL` is not trappable and is not claimed to be."""
    global _TRAP_ARMED
    if _TRAP_ARMED:
        return
    _TRAP_ARMED = True
    atexit.register(_trap)
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        try:
            signal.signal(sig, _trap)
        except (OSError, ValueError, AttributeError):
            # A platform without the signal, or a non-main thread.  The trap is
            # WEAKER here and that is stated rather than hidden.
            sys.stdout.write("%s_TRAP WARNING could not install handler for "
                             "%s\n" % (ITEM, sig))


def emit_verdict(token: str) -> None:
    """The ONLY place in this repository that may print an A1WRT2 verdict.

    Draft section 1, verbatim: "No verdict for this item is composed by a
    supervisor, by a lane, by a board write or by a commit message."  One line,
    nothing else on it."""
    global _VERDICT_EMITTED
    check(token in VERDICT_TOKENS,
          "REFUSE: %r is not one of the six registered tokens" % (token,))
    _VERDICT_EMITTED = True
    print("%s_VERDICT %s" % (ITEM, token))


# =============================================================================
# THE COMPOSER.  Draft section 1, registered AS ARITHMETIC.
# =============================================================================

# How optimistic each token is.  The ceiling caps DOWNWARD only: it can turn a
# PASS into a GATE REACHED and can never turn anything into something better.
# That is `CLAUDE.md` rule 5's direction, made structural instead of trusted.
#
# ============================================================================
# REQUIRED DISCLOSURE -- TWO ORDERINGS COEXIST IN THIS FILE AND THEY DISAGREE.
# ============================================================================
# This file contains TWO orderings of the six tokens and they are NOT the same
# ordering:
#
#   (i)  the COMPOSER'S HAND-ORDERED CHAIN in `compose_item`:
#          NOT A RESULT -> BLOCKED -> GATE FAIL -> GATE REACHED -> PASS
#   (ii) the `_OPTIMISM` ORDINAL below:
#          PASS 5, GATE REACHED 4, GATE FAIL 3, NOT A RESULT 2, BLOCKED 1,
#          PENDING 0
#
# THEY DISAGREE ON THE `NOT A RESULT` / `BLOCKED` PAIR.  The chain tests
# `NOT A RESULT` FIRST, so it wins when both are present.  The ordinal makes
# `BLOCKED` (1) the LESS optimistic of the two, so a composition written as
# `min` over `_OPTIMISM` would answer `BLOCKED` on the same input.  MEASURED,
# this drafting invocation, with both planted into hard gates:
#     chain            -> NOT A RESULT
#     min(_OPTIMISM)   -> BLOCKED
#
# (a) `_OPTIMISM` IS USED BY `cap_to_ceiling` AND BY NOTHING ELSE.  It is not
#     the composition's ordering and must never be mistaken for it.
# (b) WITH THE REGISTERED CEILING `GATE REACHED` (4), `cap_to_ceiling` MOVES
#     ONLY `PASS`.  Every other token is identity -- MEASURED across all six:
#     PASS -> GATE REACHED; GATE REACHED, GATE FAIL, NOT A RESULT, BLOCKED and
#     PENDING all pass through untouched.  SO THE ORDINAL'S ENTIRE ORDERING
#     BELOW 4 IS NEVER EXERCISED BY THIS ITEM.
# (c) THE CHAIN, NOT THE ORDINAL, IS THE COMPOSITION'S AUTHORITY.  Anyone who
#     moves the ceiling, or who rewrites the composition as `min` over this
#     ordinal, MUST reconcile the two FIRST -- they would otherwise inherit a
#     live disagreement with no test between it and a wrong verdict.
#
# THIS IS NOT A BUG AND IT IS DISCLOSED ANYWAY, because an unexercised ordering
# is an untested one, and this one sits inside the function whose entire job is
# to enforce a direction.  `Q-COMPOSE-5-ordering` below composes with BOTH
# tokens present and pins the chain's answer, so the disagreement is OBSERVED
# BY A TEST rather than latent.  Raised by the dafoam-supervisor's
# SUPERVISION_CHARTER section 3 check 1 diff read, 2026-09-04, and verified
# independently by this lane before being written down.
_OPTIMISM = {"PASS": 5, "GATE REACHED": 4, "GATE FAIL": 3,
             "NOT A RESULT": 2, "BLOCKED": 1, "PENDING": 0}


def cap_to_ceiling(raw: str, ceiling: str = CEILING) -> str:
    """`final = min(raw, CEILING)` of draft section 1, written so 'min' cannot
    be read as string comparison."""
    check(raw in _OPTIMISM, "REFUSE: uncappable token %r" % (raw,))
    check(ceiling in _OPTIMISM, "REFUSE: unknown ceiling %r" % (ceiling,))
    return ceiling if _OPTIMISM[raw] > _OPTIMISM[ceiling] else raw


def compose_item(hard: dict, soft: dict, ceiling: str = CEILING) -> tuple:
    """THE FUNCTION THREE ITEMS REGISTERED BY NAME AND NONE OF THEM WROTE.

    Returns `(raw, final, notes)`.  `raw` is the composition before the ceiling
    and `final` is after it; BOTH are printed by the caller, which is what
    `verdict_before_ceiling` was supposed to do in `A1WRT` and `A1WR`.

    `hard` and `soft` are {gate name: verdict token}.  The keys are checked
    against the REGISTERED lists so a gate cannot be quietly dropped from the
    composition by being omitted from the dict.
    """
    missing_h = [g for g in HARD_GATES if g not in hard]
    missing_s = [g for g in SOFT_GATES if g not in soft]
    check(not missing_h,
          "REFUSE: hard gates absent from the composition: %s" % (missing_h,))
    check(not missing_s,
          "REFUSE: soft gates absent from the composition: %s" % (missing_s,))
    extra = [g for g in list(hard) + list(soft)
             if g not in HARD_GATES and g not in SOFT_GATES]
    check(not extra,
          "REFUSE: gates not in the registration entered the composition: %s"
          % (extra,))

    hv = [hard[g] for g in HARD_GATES]
    sv = [soft[g] for g in SOFT_GATES]
    bad = [v for v in hv + sv if v not in VERDICT_TOKENS]
    check(not bad, "REFUSE: gate emitted a token outside the six: %s" % (bad,))

    # ---- BOTH TOKENS, ON BOTH LISTS.  `D19M-COMPOSE-DEF-1`. -----------------
    # The defect being repaired: the hard list was examined for "GATE FAIL"
    # ONLY, so a hard gate reporting "NOT A RESULT" -- a gate that could not
    # read its own subject -- fell through to `PASS` and was then capped to
    # `GATE REACHED`.  That INVERTS rule 5: a gate may turn a PASS into a NOT A
    # RESULT and never the reverse.  `Q-COMPOSE-1` DRIVES this branch with
    # `NOT A RESULT` planted in one hard gate and asserts the composed token is
    # `NOT A RESULT` and NOT `GATE REACHED`.
    if "NOT A RESULT" in hv or "NOT A RESULT" in sv:
        raw = "NOT A RESULT"
    elif "BLOCKED" in hv or "BLOCKED" in sv:
        raw = "BLOCKED"
    elif "GATE FAIL" in hv or "GATE FAIL" in sv:
        raw = "GATE FAIL"
    elif "GATE REACHED" in sv:
        raw = "GATE REACHED"
    else:
        raw = "PASS"

    final = cap_to_ceiling(raw, ceiling)
    check(final in VERDICT_TOKENS,
          "REFUSE: composed token %r is outside the six" % (final,))

    notes = ["%s_COMPOSE hard=%s" % (ITEM, {g: hard[g] for g in HARD_GATES}),
             "%s_COMPOSE soft=%s" % (ITEM, {g: soft[g] for g in SOFT_GATES}),
             "%s_COMPOSE raw=%s ceiling=%s final=%s%s"
             % (ITEM, raw, ceiling, final,
                "   <-- THE CEILING CAPPED THIS" if final != raw else "")]
    if raw == "PASS":
        notes.append(
            "%s_COMPOSE NOTE raw=PASS is capped because the L3 family has no "
            "Roache triple: no value here is grid-converged and none carries a "
            "band (G-NOBAND).  PASS is unreachable BY REGISTRATION, not by "
            "accident." % ITEM)
    return raw, final, notes


# =============================================================================
# READERS
# =============================================================================

RE_DIRECTIONS = re.compile(
    r"^\s*Mesh has (\d+) solution \(non-empty\) directions \((\d) (\d) (\d)\)",
    re.M)
RE_TIME = re.compile(r"^Time = (\d+)\s*$", re.M)
RE_CL = re.compile(r"^CL:\s*([-+0-9.eE]+)", re.M)
RE_CD = re.compile(r"^CD:\s*([-+0-9.eE]+)", re.M)
RE_YPLUS = re.compile(
    r"^yPlus min:\s*([-+0-9.eE]+)\s+max:\s*([-+0-9.eE]+)\s+mean:\s*"
    r"([-+0-9.eE]+)", re.M)
RE_POINT_BEGIN = re.compile(
    r"^AOA_POINT_BEGIN idx=(\d+) alpha=([-+0-9.]+)", re.M)
RE_POINT_VALUES = re.compile(
    r"^AOA_POINT_VALUES idx=(\d+) alpha=([-+0-9.]+) CL=(\S+) CD=(\S+)"
    r"(?: wall_s=(\S+))?(?: err=(.*))?$", re.M)
RE_POINT_END = re.compile(r"^AOA_POINT_END idx=(\d+)", re.M)
RE_SWEEP_END = re.compile(
    r"^AOA_SWEEP_END n_declared=(\d+) n_executed=(\d+)", re.M)
RE_SWEEP_TRUNC = re.compile(
    r"^AOA_SWEEP_TRUNCATED n_declared=(\d+) n_executed=(\d+)", re.M)
# THE TOKEN IS CAPTURED WHOLE AND THEN PARSED.  A character-class regex like
# `([0-9.]+)` or `([0-9]+\.?[0-9]*)` turns a MALFORMED token into a plausible
# number instead of a refusal: on `core_min=1.2.3` the first reads `1.2.3` and
# raises where nothing catches it, and the second silently reads `1.2`.
# MEASURED, this drafting invocation, on a two-row fixture ledger whose true
# spend is unknowable: this reader's earlier `([0-9]+\.?[0-9]*)` form returned
# a confident 101.200.  The honest answer is UNMEASURED.
RE_LEDGER_CORE_MIN = re.compile(r"\bcore_min=(\S+)")
RE_LEDGER_ARM = re.compile(r"\bARM=(\S+)")


def read_text(path: Path) -> str:
    check(path.exists(), "REFUSE: required artefact absent: %s" % path)
    return path.read_text(errors="replace")


def md5_of(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def split_points(text: str) -> list:
    """Split a sweep log into per-alpha segments, in file order."""
    starts = [(m.start(), int(m.group(1)), float(m.group(2)))
              for m in RE_POINT_BEGIN.finditer(text)]
    out = []
    for i, (pos, idx, alpha) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
        out.append({"idx": idx, "alpha": alpha, "text": text[pos:end]})
    return out


# =============================================================================
# THE GATES.  Every one is a real function the controls drive on real bytes.
# =============================================================================


def g_patch(sweep_text: str) -> tuple:
    """Draft section 4.  Anything but `3 solution (non-empty) directions
    (1 1 1)` REFUSES at exit 2.

    Closed by measurement (draft section 2.1): DAFoam's `DACheckGeometry.C:278`
    rejects `nGeometricD < 3` unconditionally, so `empty` is not a physics
    choice this family may make -- it is a toolchain refusal.  `symmetry` is
    therefore the ONLY admissible identity, which INVERTS `A1WRT`'s premise."""
    m = RE_DIRECTIONS.search(sweep_text)
    check(m is not None,
          "REFUSE G-PATCH: the solver never printed its solution-direction "
          "count.  A blind channel is not a pass.")
    n, a, b, c = int(m.group(1)), m.group(2), m.group(3), m.group(4)
    got = "%d (%s %s %s)" % (n, a, b, c)
    check(got == "3 (1 1 1)",
          "REFUSE G-PATCH: solver reports %s, not 3 (1 1 1).  This is the "
          "measured DAFoam refusal of `empty` on a one-cell-thick mesh "
          "(DACheckGeometry.C:278), not a gradeable outcome." % got)
    return "PASS", ["G-PATCH: PASS -- solver reports %s" % got]


def g_coldstart_seam(case_dir: Path) -> tuple:
    """The INVERSE of `A1WR`'s `G-COLDSTART`, inverted deliberately: `A1WRT`
    asserted `0/` uniform for a COLD start; this asserts a CONTINUED start
    actually carries a field.  A uniform `U` at `4000/` means the state did not
    stage, and that is exactly the `A1WRT` section 2.2 mechanism (pyDAFoam
    renaming a converged solution back into `0/`) reaching a CONTINUED arm."""
    staged = case_dir / "4000" / "U"
    check(staged.exists(),
          "REFUSE G-COLDSTART-SEAM: the staged 4000/U is absent at %s -- the "
          "continuation asset did not stage." % staged)
    zero = case_dir / "0"
    check(not zero.exists(),
          "REFUSE G-COLDSTART-SEAM: %s exists.  A continued arm that also "
          "carries a 0/ directory cannot be shown to have started from 4000/."
          % zero)
    body = staged.read_text(errors="replace")
    check("nonuniform" in body,
          "REFUSE G-COLDSTART-SEAM: staged 4000/U internalField is not "
          "nonuniform.  A uniform U means the state did not stage; the arm "
          "would be silently cold-starting and every point in it would be "
          "withdrawn as a tail.")
    return "PASS", ["G-COLDSTART-SEAM: PASS -- 4000/U nonuniform, 0/ absent"]


def g_img_freeze(manifest: dict, instrument_md5s: dict) -> tuple:
    """Image id and `libidwarp` md5 exact; every instrument md5 checked at
    launch.  Mismatch REFUSES at exit 4, not 2 -- a pin mismatch is a different
    failure from an unreadable subject and is given its own code so the two
    cannot be confused in a ledger."""
    notes = []
    got_img = manifest.get("image_digest")
    check(got_img == PIN_IMG_DIGEST,
          "REFUSE G-IMG: image digest %r != pinned %r"
          % (got_img, PIN_IMG_DIGEST), code=4)
    got_warp = manifest.get("libidwarp_md5")
    check(got_warp == PIN_IDWARP_MD5,
          "REFUSE G-IMG: libidwarp md5 %r != pinned %r"
          % (got_warp, PIN_IDWARP_MD5), code=4)
    notes.append("G-IMG: PASS -- image and libidwarp pins exact")
    for name, want in instrument_md5s.items():
        got = manifest.get("instruments", {}).get(name)
        check(got == want,
              "REFUSE G-FREEZE: instrument %s md5 %r != frozen %r"
              % (name, got, want), code=4)
    notes.append("G-FREEZE: PASS -- %d instrument md5s exact"
                 % len(instrument_md5s))
    return "PASS", notes


# ---- G-UNBOUND ------------------------------------------------------------

# ASSIGNMENT RECOGNITION IS DELIBERATELY PERMISSIVE, AND THE ASYMMETRY IS THE
# REASON.  Failing to recognise an assignment BLOCKS a correct launcher; over-
# recognising one at worst misses a flag that `set -u` itself would still catch
# at runtime.  A gate whose false positives stop good launches is worse than one
# whose false negatives leave the shell's own guard to fire.
#
# THIS WAS NOT A DESIGN CHOICE MADE IN ADVANCE.  An earlier form matched only
# `^\s*NAME=`, and driving it over this item's own launcher blocked it on
# `$rc` and `$want` -- both assigned, one by `local name="$1" want="$2"` (a
# SECOND assignment on the line) and one by `... && rc=0 || rc=$?` (an
# assignment that is not at the start of the line).  Neither form was in the
# original enumeration, which is exactly the failure mode
# `DAFOAM_CHARTER.md` section 18.3 names for a list written from memory.
_ASSIGN_NAMELIST = re.compile(
    r"^\s*(?:local|declare|typeset|readonly|export)\s+((?:-\w+\s+)*)(.*)$")
_ASSIGN_ANYWHERE = re.compile(
    r"(?:^|[\s;&|(])([A-Za-z_][A-Za-z0-9_]*)\+?=")
_ASSIGN_PATTERNS = (
    re.compile(r"^\s*read\s+(?:-\w+\s+)*([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"^\s*for\s+([A-Za-z_][A-Za-z0-9_]*)\s+in\b"),
)


def _assignments_on(line: str, masked: str):
    """Every name this line binds, in any of the forms this family's launchers
    actually use."""
    names = set()
    m = _ASSIGN_NAMELIST.match(masked)
    if m:
        for tok in m.group(2).split():
            nm = tok.split("=", 1)[0]
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nm):
                names.add(nm)
    for am in _ASSIGN_ANYWHERE.finditer(masked):
        names.add(am.group(1))
    for pat in _ASSIGN_PATTERNS:
        pm = pat.match(line)
        if pm:
            names.add(pm.group(1))
    return names
# `${VAR:-x}`, `${VAR:=x}`, `${VAR:?x}`, `${VAR+x}`, `${#VAR}` are all
# explicitly guarded against unset and are NOT flagged; the suffix is captured
# so the guarded forms can be recognised rather than assumed absent.
_EXPANSION = re.compile(
    r"\$\{([A-Za-z_][A-Za-z0-9_]*)([^}]*)\}"   # ${VAR}, ${VAR:-x}, ${VAR[0]}
    r"|\$([A-Za-z_][A-Za-z0-9_]*)")            # $VAR
_GUARDED_SUFFIX = (":-", ":=", ":?", ":+", "-", "+", "?", "=")


def _shell_scan(line: str):
    """One pass over a shell line, returning what a text-matching reader cannot
    know: where COMMANDS begin, and which characters are inside quotes.

    THIS FUNCTION EXISTS BECAUSE THE GATE FIRED ON ITS OWN LAUNCHER.  Driving
    `G-UNBOUND` over `a1wrt2_run_arm.sh` in this drafting invocation, the gate
    reported `line 216: set +u fence opened and NEVER closed` -- and line 216 is

        echo "  its first assignment under set -u, or an unclosed set +u fence."

    a quoted DIAGNOSTIC MESSAGE, not a shell directive.  A guard that reads the
    words `set +u` inside a string as a fence is reading TEXT, not CODE, and
    would have blocked every launch of a launcher whose only sin was explaining
    itself.  The same class in the other direction: `'$NOT_A_VAR'` in SINGLE
    quotes is not an expansion at all and must not be flagged.

    Returns (command_start_indices, masked_line, unclosed_quote).  In
    `masked_line` single-quoted spans are blanked -- no expansion happens there
    -- while double-quoted spans are KEPT, because expansions inside double
    quotes are real.
    """
    cmd_starts, masked = [], []
    quote = None
    esc = False
    at_cmd_start = True
    for i, ch in enumerate(line):
        if esc:
            masked.append(" ")
            esc = False
            continue
        if ch == "\\" and quote != "'":
            esc = True
            masked.append(" ")
            continue
        if quote is None:
            if ch in ('"', "'"):
                quote = ch
                masked.append(" ")
                continue
            if ch == "#" and (i == 0 or line[i - 1].isspace()):
                masked.extend(" " * (len(line) - i))
                break
            if at_cmd_start and not ch.isspace():
                cmd_starts.append(i)
                at_cmd_start = False
            if ch in ";&|(){":
                at_cmd_start = True
            masked.append(ch)
        else:
            if ch == quote:
                quote = None
                masked.append(" ")
                continue
            masked.append(" " if quote == "'" else ch)
    return cmd_starts, "".join(masked), quote


def _set_u_directive(line: str, cmd_starts):
    """Return 'on', 'off' or None for a `set` directive in COMMAND POSITION.

    A `set` that is not the first word of a command -- the one inside a quoted
    echo, the one in a comment, the one in a filename -- is not a directive and
    is not treated as one."""
    for i in cmd_starts:
        m = re.match(r"set\s+((?:[-+][A-Za-z]+\s*)+)", line[i:])
        if not m:
            continue
        state = None
        for word in m.group(1).split():
            if "u" in word[1:]:
                state = "on" if word[0] == "-" else "off"
        if state:
            return state
    return None
_SHELL_GIVEN = {
    "HOME", "PATH", "PWD", "OLDPWD", "USER", "LOGNAME", "SHELL", "IFS",
    "HOSTNAME", "TMPDIR", "LANG", "LC_ALL", "TERM", "BASH_SOURCE", "FUNCNAME",
    "RANDOM", "SECONDS", "LINENO", "BASHPID", "PPID", "UID", "EUID", "OSTYPE",
}


def g_unbound(shell_text: str, env_declared=()) -> tuple:
    """Draft section 8.  Every `$VAR` expansion in the launcher, under `set -u`,
    assigned before first use.  Any expansion reachable before its first
    assignment REFUSES the launch, `BLOCKED`.

    An enumeration derived from the code cannot have the failure mode a list
    written from memory always can (`DAFOAM_CHARTER.md` section 18.3's
    extraction principle), applied to shell variables rather than to files.

    ALSO flags a `set +u` fence that is opened and never closed -- the failure
    mode the fence itself introduces.  A gate that only hunted unassigned
    expansions would read the unclosed-fence fixture as CLEAN."""
    known = set(_SHELL_GIVEN) | set(env_declared)
    lines = shell_text.splitlines()
    fence_open_at = None
    u_ever_on = False
    u_active = False
    findings = []
    for ln, line in enumerate(lines, 1):
        if line.strip().startswith("#"):
            continue
        cmd_starts, masked, _q = _shell_scan(line)
        directive = _set_u_directive(line, cmd_starts)
        if directive == "on":
            u_active, u_ever_on, fence_open_at = True, True, None
            continue
        if directive == "off":
            if u_active:
                fence_open_at = ln
            u_active = False
            continue
        if u_active:
            for m in _EXPANSION.finditer(masked):
                name = m.group(1) or m.group(3)
                suffix = m.group(2) or ""
                if not name:
                    continue
                if suffix.startswith(_GUARDED_SUFFIX):
                    # `${VAR:-default}` and friends are explicitly guarded
                    # against unset and are LEGAL under `set -u`.  Flagging
                    # them would forbid the correct construction.
                    continue
                if name not in known:
                    findings.append(
                        "line %d: $%s expanded before any assignment, under an "
                        "active `set -u`" % (ln, name))
        known |= _assignments_on(line, masked)
    if fence_open_at is not None:
        findings.append(
            "line %d: `set +u` fence opened and NEVER closed -- every "
            "expansion after it, including the container invocation, runs with "
            "the guard disabled" % fence_open_at)
    if not u_ever_on:
        findings.append(
            "the launcher never enables `set -u` in command position at all, "
            "so no expansion in it is guarded and an unset variable would "
            "expand to the empty string instead of aborting")
    if findings:
        return "BLOCKED", ["G-UNBOUND: BLOCKED -- the launcher does not run"] \
            + ["  " + f for f in findings]
    return "PASS", ["G-UNBOUND: PASS -- every expansion assigned before first "
                    "use, no fence left open"]


def g_nograd(producer_text: str) -> tuple:
    """Draft section 7.1.  The STRUCTURAL half of the no-gradient promise:
    `compute_totals` appears 0 times in the staged producer.  An exemption
    argued in prose is worth nothing, so `DAFOAM_CHARTER.md` section 2's FD-table
    obligation is made checkable instead of argued.  If a successor ever adds an
    adjoint arm this fires and the obligation attaches BEFORE a core-minute is
    spent."""
    n = producer_text.count("compute_totals")
    if n:
        return "BLOCKED", [
            "G-NOGRAD: BLOCKED -- `compute_totals` appears %d times in the "
            "staged producer.  This item registered NO gradient, so the "
            "DAFOAM_CHARTER section 2 FD-table obligation now ATTACHES and the "
            "launch does not proceed." % n]
    return "PASS", ["G-NOGRAD: PASS -- `compute_totals` 0 times in the staged "
                    "producer (positive control: the planted copy reads 1)"]


def g_warpprobe(probe: dict) -> tuple:
    """Draft section 7.2.  `DAFOAM_CHARTER.md` section 6's two-row obligation is
    DISCHARGED BY A MEASUREMENT or it BINDS.  A version string is not an
    identity and neither is a plausible story."""
    init = probe.get("warper_init")
    jac = probe.get("warper_jacvec")
    check(init is not None and jac is not None,
          "REFUSE G-WARPPROBE: the probe output is missing a key; a blind "
          "channel cannot discharge a charter obligation.")
    if init == 0 and jac == 0:
        return "PASS", [
            "G-WARPPROBE: PASS -- warper_init=0 warper_jacvec=0.  The patched "
            "IDWarp library is provably NOT in the chain of any number this "
            "item produces, so the shipped/patched distinction cannot move a "
            "value and the section 6 two-row obligation is DISCHARGED, with "
            "this probe output cited as the discharge.  The ledger line still "
            "reads ROW=PATCHED, because that is what ran."]
    return "GATE FAIL", [
        "G-WARPPROBE: GATE FAIL -- warper_init=%r warper_jacvec=%r.  The "
        "patched library IS in the chain, so a SHIPPED-image arm is now OWED "
        "before any number from this item enters a record: ~227.85 core-min, "
        "cap 675.0, as a NEW item with its own registration, NOT under this "
        "item's ceiling." % (init, jac)]


def g_fixture(paths, run_root: str = RUN_ROOT) -> tuple:
    """The L-435 repair, inherited unweakened.  Every control fixture is static
    committed bytes AND no fixture path resolves inside this item's run root.
    A control reading live run bytes is not a control: it moves with the thing
    it is supposed to be independent of."""
    root = os.path.realpath(run_root)
    notes = []
    for p in paths:
        rp = os.path.realpath(str(p))
        # CONTAINMENT IS CHECKED BEFORE EXISTENCE, AND THE ORDER IS THE POINT.
        # Driven the other way round, the live-fixture control refused with
        # "fixture absent" -- because this item's run root does not exist yet --
        # so it passed for a reason that had nothing to do with the limb it was
        # written to exercise.  A red with an innocent explanation is the
        # easiest failure to wave through, and a control that fires for the
        # wrong reason is not a control.  The live-fixture control now asserts
        # the refusal REASON, not merely that a refusal happened.
        check(not (rp == root or rp.startswith(root + os.sep)),
              "REFUSE G-FIXTURE: fixture %s resolves INSIDE this item's run "
              "root %s.  A live fixture is not a fixture." % (rp, root))
        check(os.path.exists(rp),
              "REFUSE G-FIXTURE: fixture absent: %s" % rp)
        notes.append("  %s  md5 %s" % (os.path.basename(rp),
                                       md5_of(Path(rp))))
    return "PASS", ["G-FIXTURE: PASS -- %d fixtures, all static and all outside "
                    "%s" % (len(notes), root)] + notes


# ---- G-STALL and G-NOBAND: gates on this instrument's OWN output ----------

_STALL_WORD = (r"stall(?:s|ed|ing)?|separat(?:e|es|ed|ing|ion)|"
               r"break[- ]?down|detach(?:es|ed|ment)?")
_ANGLE = (r"(?:[-+]?\d+(?:\.\d+)?\s*(?:deg\b|degs\b|degree|degrees|°)"
          r"|(?:alpha|aoa|α|AoA)\s*[=:]?\s*[-+]?\d+(?:\.\d+)?)")
_BIND = r"(?:\bat\b|\bof\b|\bnear\b|\bonset\b|\bbegins\b|\boccurs\b|\bis\b|=)"
# FORWARD binding (word ... bind ... angle) gets a 60-char window: that is the
# shape the temptation actually takes -- "stall at 15 degrees".
_STALL_FWD = re.compile(
    r"(?:%s)[^.\n]{0,60}?%s[^.\n]{0,20}?(?:%s)" % (_STALL_WORD, _BIND, _ANGLE),
    re.I)
# REVERSE binding (angle ... word) gets only 20 chars.  The registered honest
# caveats put the angle before the word with a LONG gap -- draft section 9's
# "alpha 13...18 is at or past the onset of significant separation" has ~43
# characters between them -- so the narrow reverse window clears them.  BOTH
# directions of that behaviour are DRIVEN as named controls; the window is
# MEASURED to clear the caveats, not assumed to.
_STALL_REV = re.compile(
    r"(?:%s)[^.\n]{0,20}?(?:%s)" % (_ANGLE, _STALL_WORD), re.I)


def g_stall(output_lines) -> tuple:
    """Draft sections 4 and 10.  NO STALL ANGLE IS REPORTED AND NONE MAY BE
    DERIVED.  Any output binding a stall or separation word to a numeric angle
    REFUSES at exit 2.

    The tail alpha 13...18 is EXACTLY where that temptation lives, and a `P4`
    MISS is a statement about a series of numbers from a model draft section 10
    registers as INVALID in this regime.  So the gate binds on the prediction
    rows as on every other line."""
    for line in output_lines:
        if line.lstrip().startswith("#"):
            continue
        for rx, which in ((_STALL_FWD, "forward"), (_STALL_REV, "reverse")):
            m = rx.search(line)
            if m:
                raise Refuse(
                    "REFUSE G-STALL (%s binding): this item's output binds a "
                    "stall/separation word to a numeric angle: %r.  2-D steady "
                    "RANS with SA past the onset of significant separation is "
                    "not a valid model of the flow at ANY resolution, so no "
                    "stall angle may be reported or derived."
                    % (which, m.group(0)[:120]))
    return "PASS", ["G-STALL: PASS -- %d output lines carry no stall/angle "
                    "binding" % len(output_lines)]


_BAND_WORDS = re.compile(
    r"grid[- ]converged|grid[- ]convergence index|\bGCI\b|"
    r"within the band|inside the band|asymptotic range|"
    r"Richardson[- ]extrapolat", re.I)


def g_noband(output_lines) -> tuple:
    """Draft section 4.  No output presents a value as grid-converged or inside
    a band.  The L3 family has no Roache triple, so a band would be a claim the
    evidence cannot carry (`CLAUDE.md` rule 5)."""
    for line in output_lines:
        if line.lstrip().startswith("#"):
            continue
        if "G-NOBAND" in line or "no value" in line.lower():
            continue
        m = _BAND_WORDS.search(line)
        if m:
            raise Refuse(
                "REFUSE G-NOBAND: this item's output presents a value as "
                "grid-converged or banded (%r).  The L3 family has NO Roache "
                "triple; PASS against a threshold is unavailable on any "
                "physical quantity here." % m.group(0))
    return "PASS", ["G-NOBAND: PASS -- %d output lines present no value as "
                    "grid-converged or banded" % len(output_lines)]


# ---- the soft gates ------------------------------------------------------


def g_seam(observed_text: str, reference_text: str,
           band: float = SEAM_BAND_REL) -> tuple:
    """Draft section 4.  `SEAM`'s coefficients at its FIRST print after the
    restart against U1's terminal state.  Inside band -> PASS; outside ->
    GATE FAIL, and the finding is THE RESTART DID NOT LOAD THE STATE.

    This is the item's FALSIFIER: if `G-SEAM` fails, the tail is not a
    continuation of `A1WR`'s polar and every point in it is withdrawn as a tail.

    The control drives this same function against the REAL U1-vs-A1WR bytes,
    whose CL relative difference is 6.013254e-03 -- 6.0x the band -- and
    against U1-vs-U1, whose difference is exactly 0.  The zero limb is only
    believed BECAUSE the non-zero limb is driven on the same reader
    (`CLAUDE.md` rule 3)."""
    obs_cl = [float(x) for x in RE_CL.findall(observed_text)]
    obs_cd = [float(x) for x in RE_CD.findall(observed_text)]
    ref_cl = _terminal_coeff(reference_text, "CL")
    ref_cd = _terminal_coeff(reference_text, "CD")
    check(obs_cl and obs_cd,
          "REFUSE G-SEAM: no CL/CD print in the observed segment.")
    check(ref_cl is not None and ref_cd is not None,
          "REFUSE G-SEAM: no CL/CD in the reference.")
    o_cl, o_cd = obs_cl[-1], obs_cd[-1]
    rel_cl = abs(o_cl - ref_cl) / abs(ref_cl)
    rel_cd = abs(o_cd - ref_cd) / abs(ref_cd)
    notes = ["G-SEAM: observed CL %.15g CD %.15g" % (o_cl, o_cd),
             "        reference CL %.15g CD %.15g" % (ref_cl, ref_cd),
             "        rel CL %.6e  rel CD %.6e  band %.1e"
             % (rel_cl, rel_cd, band)]
    if rel_cl <= band and rel_cd <= band:
        return "PASS", notes + ["G-SEAM: PASS -- the restart loaded the state"]
    return "GATE FAIL", notes + [
        "G-SEAM: GATE FAIL -- the restart did NOT load the state.  The tail is "
        "not a continuation of A1WR's polar and every point in it is WITHDRAWN "
        "as a tail (the item's registered falsifier)."]


def _terminal_coeff(text: str, which: str):
    """Last CL or CD in a sweep-log segment, or a tsv row's column."""
    rx = RE_CL if which == "CL" else RE_CD
    vals = [float(x) for x in rx.findall(text)]
    if vals:
        return vals[-1]
    col = 1 if which == "CL" else 2
    for line in reversed(text.splitlines()):
        if line.strip().startswith("#") or not line.strip():
            continue
        parts = line.split()
        if len(parts) > col:
            try:
                return float(parts[col])
            except ValueError:
                continue
    return None


def g_tailcount(sweep_text: str, declared) -> tuple:
    """Draft sections 4 and 4.1.  DECLARED vs EXECUTED, where EXECUTED means a
    point that produced a VALUE or a CERTIFIED FAILURE WITH A RESIDUAL HISTORY
    -- NEVER a printed marker.

    THIS GATE EXISTS BECAUSE A LIVE DEFECT SWALLOWED A TRUNCATION.
    `a1wr_cmd.sh:96-102` decides the unit's exit status from
    `grep -c '^AOA_POINT_END '`, and `AOA_POINT_END` is printed for a point that
    CRASHED as well as for one that succeeded.  `A1WRT` U1 therefore scored
    EXEC=1 == DECLARED=1 and exited 0, discarding its own producer's rc=97 --
    landing a completion-shaped ledger row (`A1WRT/ledger.txt:3`,
    `rc=0 ... point_end_markers=1`) for a unit whose producer declared
    `AOA_SWEEP_TRUNCATED n_declared=1 n_executed=0` and whose coefficients read
    `CL=NA CD=NA`.

    The control drives THIS function on those REAL bytes and requires it to
    read executed=0, NOT 1.  `a1wr_cmd.sh` is another item's FROZEN instrument
    and carries this defect: it is REPORTED to the supervisor, NOT EDITED."""
    trunc = RE_SWEEP_TRUNC.search(sweep_text)
    sweep_end = RE_SWEEP_END.search(sweep_text)
    markers = len(RE_POINT_END.findall(sweep_text))
    executed = []
    for m in RE_POINT_VALUES.finditer(sweep_text):
        alpha = float(m.group(2))
        cl, cd = m.group(3), m.group(4)
        err = (m.group(6) or "").strip()
        if cl not in ("NA", "nan", "None") and cd not in ("NA", "nan", "None"):
            executed.append((alpha, "value"))
        elif err and "residual" in sweep_text.lower():
            # A certified failure WITH a residual history still counts as
            # executed -- the point ran and the solver said what happened.
            executed.append((alpha, "certified failure"))
    notes = ["G-TAILCOUNT: declared=%d  AOA_POINT_END markers=%d  "
             "executed(value or certified failure)=%d"
             % (len(declared), markers, len(executed))]
    if markers != len(executed):
        notes.append(
            "  MARKER/EXECUTION DISAGREEMENT: %d markers vs %d executed.  The "
            "markers are NOT the count; `AOA_POINT_END` is printed for a "
            "crashed point too (draft section 4.1)."
            % (markers, len(executed)))
    if trunc:
        n_dec, n_exec = int(trunc.group(1)), int(trunc.group(2))
        notes.append("  PRODUCER SAYS TRUNCATED: n_declared=%d n_executed=%d "
                     "-- the producer's own word, not recomputed"
                     % (n_dec, n_exec))
        return "GATE FAIL", notes + [
            "G-TAILCOUNT: GATE FAIL -- the producer declared the sweep NOT a "
            "completion.  executed=%d of %d." % (n_exec, n_dec)]
    if sweep_end is None:
        return "NOT A RESULT", notes + [
            "G-TAILCOUNT: NOT A RESULT -- no AOA_SWEEP_END line; the count is "
            "unreadable and an unreadable count is not a zero."]
    n_exec_producer = int(sweep_end.group(2))
    if n_exec_producer != len(executed):
        notes.append("  PRODUCER n_executed=%d disagrees with this reader's %d "
                     "-- the DISAGREEMENT is reported, not resolved silently"
                     % (n_exec_producer, len(executed)))
    got = sorted(a for a, _ in executed)
    want = sorted(float(a) for a in declared)
    if got == want:
        return "PASS", notes + ["G-TAILCOUNT: PASS -- %d of %d, every declared "
                                "alpha certified one way or the other"
                                % (len(want), len(want))]
    gap = [a for a in want if a not in got]
    return "GATE FAIL", notes + [
        "G-TAILCOUNT: GATE FAIL -- %d of %d; missing alpha: %s.  A missing "
        "point on a polar is a lie by omission."
        % (len(got), len(want), gap)]


def g_rc_honest(rc_text, declared_n: int, executed_n: int) -> tuple:
    """Draft section 4.  The unit's rc AS THE PRODUCER SET IT, propagated, never
    recomputed from markers.  An absent rc artefact REFUSES at exit 2 -- a
    missing rc is not a zero rc, and `A1WRT`'s ledger is the proof that the
    difference matters."""
    check(rc_text is not None,
          "REFUSE G-RC-HONEST: the rc artefact is absent.  A missing rc is NOT "
          "rc=0; recomputing it from markers is the `a1wr_cmd.sh:96-102` defect "
          "this gate exists to refuse.")
    try:
        rc = int(str(rc_text).strip())
    except ValueError:
        raise Refuse("REFUSE G-RC-HONEST: rc artefact %r is not an integer"
                     % (rc_text,))
    if rc != 0:
        return "GATE FAIL", [
            "G-RC-HONEST: GATE FAIL -- producer rc=%d.  CLAUDE.md rule 4's rc "
            "clause: a run is done only if rc=0, and this rc is propagated "
            "from the producer, NOT recomputed from AOA_POINT_END markers."
            % rc]
    if executed_n != declared_n:
        return "GATE FAIL", [
            "G-RC-HONEST: GATE FAIL -- producer rc=0 but executed %d of %d "
            "declared.  A zero rc on a truncated sweep is the swallowed-rc "
            "class (DAFOAM_CHARTER section 18.7 Requirement 4)."
            % (executed_n, declared_n)]
    return "PASS", ["G-RC-HONEST: PASS -- producer rc=0 and %d of %d executed"
                    % (executed_n, declared_n)]


def g_yplus(sweep_text: str) -> tuple:
    """Draft section 4.  Measured y+ on the `wing` patch, every alpha.  y+max >=
    1.0 anywhere -> GATE FAIL.  A blind channel on a point that ran >= 200
    iterations REFUSES: a point with no y+ reading is not a point with a good
    y+ reading.  THE MESH IS NOT RE-CUT ON A FAILURE -- that would be a gate
    moved to fit an answer."""
    pts = split_points(sweep_text) or [{"idx": 0, "alpha": float("nan"),
                                        "text": sweep_text}]
    worst, notes, seen = 0.0, [], 0
    for p in pts:
        rows = RE_YPLUS.findall(p["text"])
        iters = len(RE_TIME.findall(p["text"]))
        if not rows:
            check(iters < YPLUS_BLIND_MIN_ITERS,
                  "REFUSE G-YPLUS: alpha %.2f ran %d iterations and printed NO "
                  "y+ line.  A blind channel on a point that ran is not a pass."
                  % (p["alpha"], iters))
            notes.append("  alpha %.2f: no y+ line, but only %d iterations "
                         "(< %d) -- reported, not passed"
                         % (p["alpha"], iters, YPLUS_BLIND_MIN_ITERS))
            continue
        seen += 1
        mx = max(float(r[1]) for r in rows)
        worst = max(worst, mx)
        notes.append("  alpha %.2f: y+ max %.6g over %d prints"
                     % (p["alpha"], mx, len(rows)))
    check(seen > 0, "REFUSE G-YPLUS: no y+ reading anywhere in the sweep.")
    if worst >= YPLUS_MAX_ALLOWED:
        return "GATE FAIL", notes + [
            "G-YPLUS: GATE FAIL -- y+ max %.6g >= %.1f.  The mesh is NOT "
            "re-cut: the wall-resolved claim simply does not hold here."
            % (worst, YPLUS_MAX_ALLOWED)]
    return "PASS", notes + ["G-YPLUS: PASS -- y+ max %.6g < %.1f across %d "
                            "points" % (worst, YPLUS_MAX_ALLOWED, seen)]


def _ledger_spend(ledger_text: str) -> dict:
    """core-min per arm from this item's own ledger.  ANY read or parse failure
    is UNMEASURED and REFUSES at 65; it NEVER reads as zero.

    THIS IS THE ONE LIMB THE REST OF THE FAMILY GETS WRONG, AND THE FAILURE IS
    MEASURED RATHER THAN ASSERTED.  Driving `d6rf_chain_driver.sh:128-141`'s
    exact `spent_core_min` body in this drafting invocation:

      * ledger ABSENT      -> it prints `0.000`.  `except IOError: pass` makes
        "could not read" indistinguishable from "nothing spent" -- a planted
        zero inside the guard's own input (`CLAUDE.md` rule 3).
      * ledger with `core_min=1.2.3` -> its `([0-9.]+)` regex matches the whole
        malformed token, `float()` raises a ValueError NOTHING catches, and
        `$SPENT` comes back EMPTY.  The driver then evaluates
        `PROJ=$(python3 -c "print('%.3f' % ($SPENT + $ACAP))")`, which with an
        empty SPENT is `( + 480.0)` -- Python's UNARY PLUS -- so `PROJ` is a
        well-formed `480.000` and the guard PASSES, having silently dropped
        100.0 core-min of recorded spend to zero.
        (Refinement to the report that reached this lane: the comparison does
        NOT fail and PROJ is NOT empty.  It is worse than that -- the guard
        proceeds on a confidently wrong number, and under `set -e` an errored
        comparison would at least have been noisy.)

    `a1wrt_run_unit.sh:297-305` is the only file in this family that gets it
    right, and this reader keeps that limb as the PRIMARY rather than the
    extra."""
    per = {}
    rows = 0
    for line in ledger_text.splitlines():
        m = RE_LEDGER_CORE_MIN.search(line)
        if not m:
            continue
        tok = m.group(1)
        a = RE_LEDGER_ARM.search(line)
        arm = a.group(1) if a else "UNATTRIBUTED"
        try:
            val = float(tok)
        except ValueError:
            raise Refuse("REFUSE: ledger core_min token %r is UNMEASURABLE.  "
                         "An unknown prior spend plus this arm's cap cannot be "
                         "SHOWN to fit under the ceiling, so this refuses "
                         "rather than reading a prefix of it as a number."
                         % tok, code=65)
        if val != val or val in (float("inf"), float("-inf")):
            raise Refuse("REFUSE: ledger core_min token %r is not finite"
                         % tok, code=65)
        per[arm] = per.get(arm, 0.0) + val
        rows += 1
    if rows == 0 and ledger_text.strip():
        raise Refuse("REFUSE: the ledger has content but carries NO parseable "
                     "core_min row.  That is UNMEASURED, not zero.", code=65)
    check(rows > 0,
          "REFUSE: the ledger carries no parseable core_min row.  An "
          "unmeasured spend cannot be shown to fit under the ceiling.",
          code=65)
    return per


def g_caps(ledger_text: str) -> tuple:
    """Draft section 5.4.  Measured core-min per arm against the registered
    caps.  A cap-stop makes the affected points NOT A RESULT: an overrun stops
    the run, it does not get a new budget (`CLAUDE.md` rule 12)."""
    per = _ledger_spend(ledger_text)
    notes, over = [], []
    for arm, cap in sorted(ARM_CAP_CORE_MIN.items()):
        spent = per.get(arm, 0.0)
        notes.append("  arm %s: %.3f core-min of cap %.1f" % (arm, spent, cap))
        if spent > cap + CEILING_TOLERANCE:
            over.append("%s (%.3f > %.1f)" % (arm, spent, cap))
    unattr = per.get("UNATTRIBUTED", 0.0)
    if unattr:
        notes.append("  UNATTRIBUTED %.3f core-min -- ledger rows carrying no "
                     "ARM=; counted against the ceiling, never dropped"
                     % unattr)
    if over:
        return "NOT A RESULT", notes + [
            "G-CAPS: NOT A RESULT -- cap-stop on %s.  The affected points are "
            "NOT A RESULT whatever their values." % ", ".join(over)]
    return "GATE REACHED", notes + [
        "G-CAPS: GATE REACHED -- every arm inside its registered cap"]


def g_ceiling(ledger_text: str) -> tuple:
    """Draft section 6, the READING half.  The ENFORCING half lives in
    `a1wrt2_run_arm.sh` and runs BEFORE the container starts -- because the
    runner's own cap is advisory, inert and off by construction
    (`docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md`, D539), so an overrun it
    reports is one it could never stop.  A ceiling that nothing compares
    anything to is a number, not an instrument."""
    per = _ledger_spend(ledger_text)
    total = sum(per.values())
    line = ("%s_SPEND_CENSUS total_core_min=%.3f item_ceiling=%.1f"
            % (ITEM, total, ITEM_CEILING_CORE_MIN))
    if total > ITEM_CEILING_CORE_MIN + CEILING_TOLERANCE:
        return "GATE FAIL", [line, "G-CEILING: GATE FAIL -- %.3f core-min > "
                            "the registered %.1f ceiling.  An overrun stops "
                            "the run; it does not get a new budget."
                            % (total, ITEM_CEILING_CORE_MIN)]
    return "GATE REACHED", [line, "G-CEILING: GATE REACHED -- %.3f of %.1f"
                            % (total, ITEM_CEILING_CORE_MIN)]


# =============================================================================
# THE GRADE.  Reads a run root, drives every gate, composes, emits.
# =============================================================================


def grade(root: Path) -> tuple:
    """Returns (output_lines, raw, final).  Every checkpoint is recorded so the
    EXIT trap can say WHERE it stopped, and the composer runs LAST."""
    out, hard, soft = [], {}, {}

    def run(name, fn, *a, **kw):
        checkpoint(name)
        v, notes = fn(*a, **kw)
        out.extend(notes)
        (hard if name in HARD_GATES else soft)[name] = v
        return v

    checkpoint("open-run-root")
    seam_log = read_text(root / "SEAM" / "out" / "sweep.log")
    tail_log = read_text(root / "TAIL" / "out" / "sweep.log")
    manifest = json.loads(read_text(root / "MANIFEST.json"))
    ledger = read_text(root / "ledger.txt")

    out.append("=== %s GRADE ===" % ITEM)
    out.append("run root: %s" % root)

    run("G-PATCH", g_patch, seam_log + "\n" + tail_log)
    run("G-COLDSTART-SEAM", g_coldstart_seam, root / "SEAM" / "case")

    checkpoint("G-IMG/G-FREEZE")
    v, notes = g_img_freeze(manifest, PIN_INSTRUMENTS)
    out.extend(notes)
    hard["G-IMG"] = v
    hard["G-FREEZE"] = v

    run("G-UNBOUND", g_unbound, read_text(root / "run_arm.sh"),
        manifest.get("env_declared", []))
    run("G-NOGRAD", g_nograd, read_text(root / "runScript.py"))
    run("G-WARPPROBE", g_warpprobe,
        json.loads(read_text(root / "TAIL" / "out" / "warp_probe.json")))
    run("G-FIXTURE", g_fixture, REGISTERED_FIXTURES)

    seam_pts = split_points(seam_log)
    seam_seg = seam_pts[0]["text"] if seam_pts else seam_log
    run("G-SEAM", g_seam, seam_seg,
        "CD: %.17g\nCL: %.17g\n" % (U1_TERMINAL_CD, U1_TERMINAL_CL))

    checkpoint("G-TAILCOUNT")
    vt, notes = g_tailcount(tail_log, TAIL_ALPHAS)
    out.extend(notes)
    soft["G-TAILCOUNT"] = vt
    n_exec = len([1 for m in RE_POINT_VALUES.finditer(tail_log)
                  if m.group(3) not in ("NA", "nan", "None")])

    run("G-RC-HONEST", g_rc_honest,
        read_text(root / "TAIL" / "out" / "rc"), len(TAIL_ALPHAS), n_exec)
    run("G-YPLUS", g_yplus, tail_log)
    run("G-CAPS", g_caps, ledger)
    run("G-CEILING", g_ceiling, ledger)

    # G-STALL and G-NOBAND gate THIS INSTRUMENT'S OWN OUTPUT, so they run last,
    # over everything printed above them.  The tail is exactly where the
    # temptation lives, so the gate reads the words this grader itself wrote.
    run("G-STALL", g_stall, out)
    run("G-NOBAND", g_noband, out)

    checkpoint("compose")
    raw, final, notes = compose_item(hard, soft)
    out.extend(notes)
    return out, raw, final


REGISTERED_FIXTURES = [
    FIXTURES / "g_unbound_positive.sh",
    FIXTURES / "g_unbound_negative.sh",
    FIXTURES / "g_unbound_fenced_ok.sh",
    FIXTURES / "g_unbound_fence_unclosed.sh",
    FIXTURES / "g_patch_empty_real.log",
    FIXTURES / "g_patch_symmetry_real.log",
    FIXTURES / "g_tailcount_u1_truncated_real.log",
    FIXTURES / "g_seam_u1_terminal_real.log",
    FIXTURES / "g_seam_a1wr_reference_real.tsv",
]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="A1WRT2 grader.  NOT FROZEN.")
    ap.add_argument("--selftest", action="store_true",
                    help="drive every control; SELFTEST-SUCCESS-PATH first")
    ap.add_argument("--root", help="run root to grade")
    ap.add_argument("--hang-at", default=None,
                    help="internal: stop at this checkpoint and wait, so the "
                         "EXIT trap can be driven by a real kill")
    a = ap.parse_args(argv)

    arm_trap()

    if a.hang_at:
        checkpoint("open-run-root")
        checkpoint(a.hang_at)
        sys.stdout.write("%s_HANGING at %s\n" % (ITEM, a.hang_at))
        sys.stdout.flush()
        signal.pause()
        return 0

    if a.selftest:
        rc = selftest()
        if rc != 0:
            emit_verdict("NOT A RESULT")
            return rc
        if not a.root:
            _VERDICT_EMITTED_MARK()
            print("%s_SELFTEST OK -- controls only, no run root graded" % ITEM)
            emit_verdict("PENDING")
            return 0

    if not a.root:
        emit_verdict("PENDING")
        return 0
    root = Path(a.root)
    if not root.is_dir():
        print("%s_NOTE run root absent: %s" % (ITEM, root))
        emit_verdict("PENDING")
        return 0

    try:
        out, raw, final = grade(root)
    except Refuse as e:
        print("%s_REFUSED -- %s" % (ITEM, e))
        emit_verdict("NOT A RESULT")
        return e.code
    for line in out:
        print(line)
    emit_verdict(final)
    return 0


def _VERDICT_EMITTED_MARK() -> None:
    """No-op placeholder kept so the selftest-only path reads in the same shape
    as the graded path.  It changes nothing."""
    return None


# =============================================================================
# === SELFTEST BOUNDARY ===
# Everything BELOW this line is the selftest.  `Q-NOASSERT` audits this file's
# AST for `assert` statements ABOVE it and requires 0; this file happens to
# carry 0 BELOW it as well, so the selftest is byte-identical in behaviour
# under `python3` and under `python3 -O`.
# =============================================================================

_CONTROL_LOG: list[tuple] = []


def _control(name: str, expect: str, fn) -> None:
    """Drive one control and record EXERCISED-PASS / EXERCISED-FAIL / NOT
    EXERCISED beside it.

    `expect` is the DIRECTION the control must drive the gate in:
      "fail"  -> the control must make the gate report its failing outcome;
                 recorded EXERCISED-FAIL.
      "pass"  -> the control must make the gate report its passing outcome;
                 recorded EXERCISED-PASS.
    A control that does not reach its expected direction makes the whole
    selftest refuse.  `NOT EXERCISED` is never counted as a pass and is never
    inferred from the absence of a failure -- `A1WRT`'s `G-PATCHPAIR`
    short-circuited on an absent side and its planted controls' silence was
    indistinguishable from their success."""
    state, detail = "NOT EXERCISED", ""
    try:
        detail = fn()
        state = "EXERCISED-FAIL" if expect == "fail" else "EXERCISED-PASS"
    except Refuse as e:
        state = "NOT EXERCISED"
        detail = "control itself refused: %s" % e
    except Exception as e:                                   # noqa: BLE001
        state = "NOT EXERCISED"
        detail = "control raised %s: %s" % (type(e).__name__, e)
    _CONTROL_LOG.append((name, expect, state, detail))
    print("CONTROL %-28s %-15s %s" % (name, state, detail))
    if state == "NOT EXERCISED":
        raise Refuse("REFUSE: control %s did not reach its %s direction -- %s"
                     % (name, expect, detail))


def _must(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def _fx(name: str) -> str:
    return (FIXTURES / name).read_text(errors="replace")


# ---- the synthetic-but-realistic HAPPY-PATH run root ----------------------


def _build_happy_root(tmp: Path) -> Path:
    """A complete, realistic A1WRT2 run root in which EVERY GATE PASSES.

    The print shapes are copied from the REAL `A1WRT` U1 sweep log -- the
    `Mesh has 3 solution (non-empty) directions (1 1 1)` line, the
    `CD: ... final: ...` / `CL: ... final: ...` pair, the
    `yPlus min: ... max: ... mean: ...` line, and the `AOA_POINT_*` markers --
    so the happy path exercises the SAME regexes the real bytes will."""
    root = tmp / "A1WRT2_happy"
    for arm in ("SEAM", "TAIL"):
        (root / arm / "out").mkdir(parents=True)
    (root / "SEAM" / "case" / "4000").mkdir(parents=True)
    (root / "SEAM" / "case" / "4000" / "U").write_text(
        "internalField   nonuniform List<vector>\n130304\n(\n"
        "(0.9987 0.0421 0)\n(0.9981 0.0433 0)\n)\n;\n")

    head = ("Create mesh for time = 0\n\n"
            "Checking geometry...\n"
            "    Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)\n"
            "    Mesh has 3 solution (non-empty) directions (1 1 1)\n"
            "    Overall domain bounding box (-49.5 -49.5 -0.05) "
            "(50.5 49.5 0.05)\n\n")

    def block(t, cl, cd, yp):
        return ("Time = %d\n\n"
                "nuTilda initRes: 4.11e-07 finalRes: 2.8e-08 nIters: 4\n"
                "Bounding nuTilda>1e-16\n"
                "CD: %.17g final: %.17g\n"
                "CL: %.17g final: %.17g\n"
                "yPlus min: 0.000173062240383547 max: %.17g mean: "
                "0.008997723990605227\n"
                "ExecutionTime = %.2f s  ClockTime = %d s\n\n"
                % (t, cd, cd, cl, cl, yp, t * 0.46178, int(t * 0.47)))

    # SEAM: 200 iterations continued from 4000, reproducing U1's terminal state
    # to well inside the 1.0e-03 band.  The last print is what G-SEAM reads.
    seam = [head, "AOA_POINT_BEGIN idx=0 alpha=12.0000000000\n"]
    for i, t in enumerate((4100, 4200)):
        seam.append(block(t, U1_TERMINAL_CL * (1 + 2.0e-5 * (2 - i)),
                          U1_TERMINAL_CD * (1 + 1.0e-5 * (2 - i)), 0.0387))
    seam += ["AOA_POINT_VALUES idx=0 alpha=12.0000000000 CL=%.15g CD=%.15g "
             "wall_s=95.1 err=NONE\n" % (U1_TERMINAL_CL, U1_TERMINAL_CD),
             "AOA_POINT_END idx=0 alpha=12.0000000000\n",
             "AOA_SWEEP_END n_declared=1 n_executed=1 json=/mnt/out/points.json\n",
             "End\n"]
    (root / "SEAM" / "out" / "sweep.log").write_text("".join(seam))
    (root / "SEAM" / "out" / "rc").write_text("0\n")

    # TAIL: all six declared alphas execute and are certified.
    tail = [head]
    cl = 1.20
    for i, alpha in enumerate(TAIL_ALPHAS):
        cl += 0.05 - 0.004 * i
        cd = 0.031 + 0.004 * i
        tail.append("AOA_POINT_BEGIN idx=%d alpha=%.10f\n" % (i, alpha))
        for t in (100, 2000, 4000):
            tail.append(block(t, cl, cd, 0.0387 + 0.004 * i))
        tail.append("AOA_POINT_VALUES idx=%d alpha=%.10f CL=%.12f CD=%.12f "
                    "wall_s=1848.3 err=NONE\n" % (i, alpha, cl, cd))
        tail.append("AOA_POINT_END idx=%d alpha=%.10f\n" % (i, alpha))
    tail.append("AOA_SWEEP_END n_declared=6 n_executed=6 "
                "json=/mnt/out/points.json\n")
    tail.append("End\n")
    (root / "TAIL" / "out" / "sweep.log").write_text("".join(tail))
    (root / "TAIL" / "out" / "rc").write_text("0\n")
    for arm in ("SEAM", "TAIL"):
        (root / arm / "out" / "warp_probe.json").write_text(
            '{"warper_init": 0, "warper_jacvec": 0}\n')

    (root / "runScript.py").write_text(
        "# staged producer, primal only, undeformed geometry\n"
        "from mphys.multipoint import Multipoint\n"
        "prob.run_model()\n")
    (root / "run_arm.sh").write_text(
        "#!/bin/sh\nset -u\nARM=SEAM\nIMG=dafoam-idwarp-rot:v1\n"
        'echo "launching $ARM on $IMG"\n')
    (root / "MANIFEST.json").write_text(json.dumps({
        "image_digest": PIN_IMG_DIGEST,
        "libidwarp_md5": PIN_IDWARP_MD5,
        "env_declared": ["OMP_NUM_THREADS", "STAGED_ROOT"],
        "instruments": {"runScript.py": PIN_RUNSCRIPT_MD5},
    }, indent=1))
    (root / "ledger.txt").write_text(
        "ITEM=A1WRT2\n"
        "ARM=SEAM ROW=PATCHED IMG=dafoam-idwarp-rot:v1 rc=0 wall_s=190 "
        "ranks=1 core_min=3.167 cap_core_min=10.0 mode=CONTINUED\n"
        "ARM=TAIL ROW=PATCHED IMG=dafoam-idwarp-rot:v1 rc=0 wall_s=13380 "
        "ranks=1 core_min=223.000 cap_core_min=675.0 mode=CONTINUED\n")
    return root


def _st_success_path() -> int:
    """SELFTEST-SUCCESS-PATH -- THE LEG THIS FAMILY HAS NEVER RUN.

    Three items in this family produced no expressible verdict.  Not one of
    them was ever driven end-to-end against "what does this instrument PRINT if
    everything goes right?"  This leg asks exactly that, on a synthetic-but-
    realistic run root in which every gate passes, and it REQUIRES a success
    token on stdout.  It is driven FIRST, before any refusal leg, so it can
    never be the one that got skipped."""
    print("")
    print("=== SELFTEST-SUCCESS-PATH "
          "==================================================")
    print("The end-to-end HAPPY PATH.  Every gate passes.  This leg exists "
          "because")
    print("SO3aF2, A1WRT and A1WR each rehearsed their refusals and none "
          "rehearsed")
    print("its success -- and all three ended with nothing to say.")
    with tempfile.TemporaryDirectory(prefix="a1wrt2_happy_") as td:
        root = _build_happy_root(Path(td))
        out, raw, final = grade(root)
        for line in out:
            print("  " + line)
        _must(final == "GATE REACHED",
              "SELFTEST-SUCCESS-PATH: final is %r, not the REGISTERED SUCCESS "
              "LABEL `GATE REACHED`" % final)
        # WHICH BRANCH OF THE REGISTERED ARITHMETIC A GREEN RUN TAKES, MEASURED
        # AND NOT ASSUMED.  Driving this leg for the first time established
        # something the registration's prose does not say: `G-CAPS` and
        # `G-CEILING` emit `GATE REACHED` on their SUCCESS path -- "the arm fit
        # its registered cap" is not a PASS against a physical threshold -- so a
        # fully green run enters draft section 1's
        #     elif "GATE REACHED" in soft:  raw = "GATE REACHED"
        # branch, and `raw` is ALREADY at the ceiling.  The cap is therefore a
        # NO-OP on the real happy path, which is not a defect but IS a fact the
        # supervisor should have rather than a claim that the cap "is visible"
        # in a case where it never moves anything.
        # The OTHER branch -- raw=PASS capped DOWN to GATE REACHED -- is
        # reachable only when every soft gate emits PASS, and is driven
        # separately and by name in `Q-COMPOSE-2`.  Both branches are live.
        _must(raw in ("PASS", "GATE REACHED"),
              "SELFTEST-SUCCESS-PATH: a green run composed raw=%r" % raw)
        branch = ("raw=PASS, CAPPED DOWN by the ceiling"
                  if raw == "PASS" else
                  "raw=GATE REACHED via the `GATE REACHED in soft` branch "
                  "(G-CAPS/G-CEILING); the ceiling is a NO-OP here, and "
                  "Q-COMPOSE-2 drives the capping branch separately")
        print("  SELFTEST-SUCCESS-PATH: composition branch taken -- %s"
              % branch)

        # And now the property that actually matters: the process PRINTS it.
        # Grading in-process proves the composition; only a subprocess proves
        # the EMISSION, which is the thing all three predecessors lacked.
        outer = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--root", str(root)],
            capture_output=True, text=True, timeout=180)
        printed = [ln for ln in outer.stdout.splitlines()
                   if ln.startswith("%s_VERDICT " % ITEM)]
        _must(len(printed) == 1,
              "SELFTEST-SUCCESS-PATH: expected exactly one %s_VERDICT line on "
              "stdout, got %d.  THIS IS THE PREDECESSORS' DEFECT: a registered "
              "success label with no line that prints it."
              % (ITEM, len(printed)))
        _must(printed[0] == "%s_VERDICT GATE REACHED" % ITEM,
              "SELFTEST-SUCCESS-PATH: the emitted line is %r" % printed[0])
        _must(outer.returncode == 0,
              "SELFTEST-SUCCESS-PATH: rc %d on a fully passing run"
              % outer.returncode)
        print("  SELFTEST-SUCCESS-PATH: THE INSTRUMENT PRINTED %r  (rc %d)"
              % (printed[0], outer.returncode))
        print("  SELFTEST-SUCCESS-PATH: raw=%s  ceiling=%s  final=%s  -- BOTH "
              "raw and final are printed on every path, which is what "
              "`verdict_before_ceiling` was registered to do in A1WRT and "
              "A1WR and never did." % (raw, CEILING, final))
    print("=== SELFTEST-SUCCESS-PATH PASSED "
          "===========================================")
    return 0


def _st_exit_trap() -> int:
    """SELFTEST-EXIT-TRAP -- `NO ITEM VERDICT BY CONSTRUCTION` is FORBIDDEN, and
    the forbidding is DRIVEN, not registered.

    A real subprocess is started, allowed to reach a checkpoint mid-grade, and
    then KILLED with SIGTERM.  It must print `PENDING` and exit 12 rather than
    fall silent -- which is precisely what `A1WRT` did after running both its
    units."""
    print("")
    print("=== SELFTEST-EXIT-TRAP "
          "=====================================================")
    me = str(Path(__file__).resolve())
    results = []
    for sig, label in ((signal.SIGTERM, "SIGTERM"), (signal.SIGINT, "SIGINT")):
        p = subprocess.Popen(
            [sys.executable, me, "--hang-at", "G-YPLUS"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Wait for the process to actually be inside the grade before killing,
        # so the kill lands MID-GRADE and not before the trap is armed.
        line = p.stdout.readline()
        _must("%s_HANGING" % ITEM in line,
              "SELFTEST-EXIT-TRAP: the child never reached its checkpoint "
              "(got %r)" % line)
        p.send_signal(sig)
        rest, _err = p.communicate(timeout=60)
        rc = p.returncode
        verdict = [ln for ln in rest.splitlines()
                   if ln.startswith("%s_VERDICT " % ITEM)]
        _must(rc == 12,
              "SELFTEST-EXIT-TRAP: %s gave rc %d, not 12" % (label, rc))
        _must(len(verdict) == 1,
              "SELFTEST-EXIT-TRAP: %s printed %d verdict lines, not 1 -- "
              "SILENCE IS THE FORBIDDEN OUTCOME" % (label, len(verdict)))
        _must(verdict[0].startswith(
            "%s_VERDICT PENDING -- the composer did not run, last checkpoint "
            % ITEM),
            "SELFTEST-EXIT-TRAP: %s printed %r" % (label, verdict[0]))
        results.append((label, rc, verdict[0]))
        print("  killed mid-grade with %s -> rc %d, printed %r"
              % (label, rc, verdict[0]))

    # The NEGATIVE direction: a process that DOES reach its composer must NOT
    # fire the trap.  Without this limb a trap that fired unconditionally would
    # also pass the positive limb.
    with tempfile.TemporaryDirectory(prefix="a1wrt2_trapneg_") as td:
        root = _build_happy_root(Path(td))
        ok = subprocess.run([sys.executable, me, "--root", str(root)],
                            capture_output=True, text=True, timeout=180)
        _must(ok.returncode == 0 and "PENDING" not in ok.stdout,
              "SELFTEST-EXIT-TRAP negative limb: the trap fired on a run that "
              "DID reach its composer (rc %d)" % ok.returncode)
        print("  negative limb: a run that reaches its composer exits 0 and "
              "prints no PENDING -- the trap is not unconditional")

    # HONEST LIMIT, PRINTED SO IT IS ON THE RECORD RATHER THAN IMPLIED.
    print("  LIMIT: SIGKILL is not trappable by any process on any POSIX "
          "system.")
    print("         A SIGKILLed grade prints nothing and NO code in this file "
          "can")
    print("         change that.  The trap covers normal exit, uncaught "
          "exception,")
    print("         sys.exit, SIGTERM, SIGINT and SIGHUP -- and nothing more.")
    print("=== SELFTEST-EXIT-TRAP PASSED (%d signals driven) "
          "===========================" % len(results))
    return 0


def _st_compose() -> int:
    """Q-COMPOSE-1..4, draft section 4."""
    green_h = {g: "PASS" for g in HARD_GATES}
    green_s = {g: "PASS" for g in SOFT_GATES}

    def q1():
        h = dict(green_h)
        h["G-PATCH"] = "NOT A RESULT"
        raw, final, _ = compose_item(h, dict(green_s))
        _must(raw == "NOT A RESULT" and final == "NOT A RESULT",
              "Q-COMPOSE-1: NOT A RESULT in a HARD gate composed to raw=%r "
              "final=%r.  This is D19M-COMPOSE-DEF-1 alive again: a hard gate "
              "that could not read its subject falling through to PASS and "
              "being capped to GATE REACHED." % (raw, final))
        return "hard G-PATCH=NOT A RESULT -> raw=%s final=%s (NOT GATE " \
               "REACHED)" % (raw, final)
    _control("Q-COMPOSE-1", "fail", q1)

    def q1b():
        # The SAME defect reached through a hard GATE FAIL, so both tokens the
        # repair added are driven and not just the headline one.
        h = dict(green_h)
        h["G-NOGRAD"] = "GATE FAIL"
        raw, final, _ = compose_item(h, dict(green_s))
        _must(raw == "GATE FAIL" and final == "GATE FAIL",
              "Q-COMPOSE-1b: hard GATE FAIL composed to %r/%r" % (raw, final))
        return "hard G-NOGRAD=GATE FAIL -> raw=%s final=%s" % (raw, final)
    _control("Q-COMPOSE-1b", "fail", q1b)

    def q2():
        raw, final, notes = compose_item(dict(green_h), dict(green_s))
        _must(raw == "PASS", "Q-COMPOSE-2: raw=%r not PASS" % raw)
        _must(final == "GATE REACHED",
              "Q-COMPOSE-2: final=%r not GATE REACHED" % final)
        _must(any("raw=PASS" in n and "final=GATE REACHED" in n
                  for n in notes),
              "Q-COMPOSE-2: the cap is not VISIBLE in the printed notes")
        return "all gates PASS -> raw=%s final=%s, both printed" % (raw, final)
    _control("Q-COMPOSE-2", "pass", q2)

    def q3():
        h = dict(green_h)
        h["G-IMG"] = "MOSTLY FINE"
        try:
            compose_item(h, dict(green_s))
        except Refuse as e:
            return "token outside the six -> REFUSE(%d): %s" % (e.code, e)
        raise ValueError("Q-COMPOSE-3: a token outside the six did NOT refuse")
    _control("Q-COMPOSE-3", "fail", q3)

    def q3b():
        h = dict(green_h)
        del h["G-STALL"]
        try:
            compose_item(h, dict(green_s))
        except Refuse as e:
            return "a gate DROPPED from the composition -> REFUSE: %s" % e
        raise ValueError("Q-COMPOSE-3b: a dropped hard gate did NOT refuse")
    _control("Q-COMPOSE-3b", "fail", q3b)

    def q4():
        # Q4 is driven for real by SELFTEST-EXIT-TRAP; here the cap direction is
        # checked in isolation so `cap_to_ceiling` cannot silently invert.
        _must(cap_to_ceiling("PASS") == "GATE REACHED", "cap did not cap PASS")
        _must(cap_to_ceiling("GATE FAIL") == "GATE FAIL",
              "cap DEGRADED a GATE FAIL -- the ceiling may only cap downward")
        _must(cap_to_ceiling("NOT A RESULT") == "NOT A RESULT",
              "cap moved a NOT A RESULT -- rule 5's direction is inverted")
        return "cap: PASS->GATE REACHED, GATE FAIL and NOT A RESULT unmoved"
    _control("Q-COMPOSE-4-cap", "pass", q4)

    def q5():
        """Q-COMPOSE-5-ordering -- PIN THE DISAGREEMENT BETWEEN THE TWO
        ORDERINGS SO IT IS OBSERVED BY A TEST RATHER THAN LATENT.

        See the disclosure block at `_OPTIMISM`.  The composer's hand-ordered
        chain and the `_OPTIMISM` ordinal disagree on the
        `NOT A RESULT`/`BLOCKED` pair.  This control composes with BOTH present
        and asserts the CHAIN's answer, and it also computes what a
        `min`-over-`_OPTIMISM` composition WOULD have said, so the divergence
        is written down by a driven test and not only by a comment.  It changes
        no logic."""
        h = dict(green_h)
        h["G-PATCH"] = "NOT A RESULT"
        h["G-IMG"] = "BLOCKED"
        raw, final, _ = compose_item(h, dict(green_s))
        _must(raw == "NOT A RESULT" and final == "NOT A RESULT",
              "Q-COMPOSE-5: with BOTH NOT A RESULT and BLOCKED present the "
              "chain answered %r/%r; the registered chain tests NOT A RESULT "
              "FIRST, so NOT A RESULT must win." % (raw, final))
        present = set(h.values()) | set(green_s.values())
        ordinal_would_say = min(present, key=lambda t: _OPTIMISM[t])
        _must(ordinal_would_say == "BLOCKED",
              "Q-COMPOSE-5: the ordinal's answer moved to %r.  If the two "
              "orderings have been reconciled, this control and the "
              "disclosure at _OPTIMISM must both be updated deliberately, not "
              "silently." % ordinal_would_say)
        # (b) of the disclosure, MEASURED rather than asserted: under the
        # registered ceiling the ordinal's sub-ceiling order is unexercised.
        moved = [t for t in VERDICT_TOKENS if cap_to_ceiling(t) != t]
        _must(moved == ["PASS"],
              "Q-COMPOSE-5: cap_to_ceiling moves %s under the registered "
              "ceiling, not PASS alone -- the ordinal's sub-ceiling ordering "
              "is now EXERCISED and the disagreement is no longer harmless."
              % moved)
        return ("chain says %s; min(_OPTIMISM) would say %s; exposure is ZERO "
                "-- cap_to_ceiling moves only %s under ceiling %r"
                % (raw, ordinal_would_say, moved[0], CEILING))
    _control("Q-COMPOSE-5-ordering", "fail", q5)
    return 0


def _st_gate_controls() -> int:
    """Every gate that reads a number, driven in BOTH directions, on real bytes
    where real bytes exist."""

    # ---- G-FIXTURE first: it certifies the other controls' inputs ----------
    def fx_ok():
        v, _n = g_fixture(REGISTERED_FIXTURES)
        _must(v == "PASS", "G-FIXTURE rejected its own registered fixtures")
        return "%d registered fixtures, all static, all outside %s" \
               % (len(REGISTERED_FIXTURES), RUN_ROOT)
    _control("G-FIXTURE/static", "pass", fx_ok)

    def fx_live():
        live = os.path.join(RUN_ROOT, "TAIL", "out", "sweep.log")
        try:
            g_fixture([live])
        except Refuse as e:
            _must("resolves INSIDE this item's run root" in str(e),
                  "G-FIXTURE: the live-fixture control refused for the WRONG "
                  "REASON (%r).  This item's run root does not exist, so an "
                  "existence check placed first would make this control pass "
                  "without ever exercising the containment limb." % str(e))
            return "a fixture pointed INSIDE the run root -> REFUSE, and the " \
                   "refusal REASON is containment, not absence"
        raise ValueError("G-FIXTURE: a live fixture did NOT refuse")
    _control("G-FIXTURE/live-refuses", "fail", fx_live)

    def fx_absent():
        try:
            g_fixture(["/nonexistent/definitely/not/here.log"])
        except Refuse as e:
            _must("fixture absent" in str(e),
                  "G-FIXTURE: an absent fixture refused for the wrong reason "
                  "(%r)" % str(e))
            return "a fixture that does not exist -> REFUSE on absence, a " \
                   "DIFFERENT limb from containment and driven separately"
        raise ValueError("G-FIXTURE: an absent fixture did NOT refuse")
    _control("G-FIXTURE/absent-refuses", "fail", fx_absent)

    # ---- G-PATCH: REAL MEASURED KNOWN-POSITIVE, at zero compute -----------
    def patch_fail():
        try:
            g_patch(_fx("g_patch_empty_real.log"))
        except Refuse as e:
            _must(e.code == 2, "G-PATCH refused with code %d, not 2" % e.code)
            return "REAL A1WRT tail_empty bytes '2 (1 1 0)' -> REFUSE exit 2"
        raise ValueError("G-PATCH: the real `empty` bytes did NOT refuse")
    _control("G-PATCH/real-empty", "fail", patch_fail)

    def patch_pass():
        v, _n = g_patch(_fx("g_patch_symmetry_real.log"))
        _must(v == "PASS", "G-PATCH read the real symmetry bytes as %r" % v)
        return "REAL A1WRT U1 bytes '3 (1 1 1)' -> PASS"
    _control("G-PATCH/real-symmetry", "pass", patch_pass)

    def patch_blind():
        try:
            g_patch("Time = 1\nCL: 1.0\n")
        except Refuse:
            return "no direction line at all -> REFUSE (a blind channel is " \
                   "not a pass)"
        raise ValueError("G-PATCH: a blind channel did NOT refuse")
    _control("G-PATCH/blind-refuses", "fail", patch_blind)

    # ---- G-SEAM: REAL MEASURED KNOWN-POSITIVE, at zero compute -------------
    def seam_fail():
        v, notes = g_seam(_fx("g_seam_u1_terminal_real.log"),
                          _fx("g_seam_a1wr_reference_real.tsv"))
        _must(v == "GATE FAIL",
              "G-SEAM read the REAL U1-vs-A1WR miss as %r, not GATE FAIL" % v)
        rel = [n for n in notes if "rel CL" in n][0].strip()
        _must("6.013254e-03" in rel,
              "G-SEAM computed %r; the registered measured miss is "
              "6.013254e-03" % rel)
        return "REAL U1 vs REAL A1WR alpha=12 -> GATE FAIL, %s" % rel
    _control("G-SEAM/real-miss", "fail", seam_fail)

    def seam_pass():
        v, _n = g_seam(_fx("g_seam_u1_terminal_real.log"),
                       _fx("g_seam_u1_terminal_real.log"))
        _must(v == "PASS", "G-SEAM read U1 against itself as %r" % v)
        return "REAL U1 vs itself -> PASS.  This zero is believed ONLY " \
               "because the same reader returned 6.013254e-03 above."
    _control("G-SEAM/real-self", "pass", seam_pass)

    # ---- G-TAILCOUNT: the swallowed truncation, on REAL bytes --------------
    def tail_real():
        v, notes = g_tailcount(_fx("g_tailcount_u1_truncated_real.log"), (12.0,))
        _must(v == "GATE FAIL",
              "G-TAILCOUNT read the REAL truncated bytes as %r" % v)
        joined = " ".join(notes)
        _must("markers=1" in joined,
              "G-TAILCOUNT did not report the marker count: %s" % joined)
        _must("executed(value or certified failure)=0" in joined,
              "G-TAILCOUNT read executed != 0 on bytes whose producer said "
              "n_executed=0: %s" % joined)
        return "REAL A1WRT U1: 1 AOA_POINT_END marker, executed=0 -> GATE " \
               "FAIL (a1wr_cmd.sh:96-102 scored this run rc=0)"
    _control("G-TAILCOUNT/real-swallowed", "fail", tail_real)

    def tail_pass():
        with tempfile.TemporaryDirectory() as td:
            root = _build_happy_root(Path(td))
            v, _n = g_tailcount(
                (root / "TAIL" / "out" / "sweep.log").read_text(), TAIL_ALPHAS)
        _must(v == "PASS", "G-TAILCOUNT read a full 6/6 sweep as %r" % v)
        return "6 of 6 declared alphas executed -> PASS"
    _control("G-TAILCOUNT/full-sweep", "pass", tail_pass)

    def tail_unreadable():
        v, _n = g_tailcount("Time = 1\n", TAIL_ALPHAS)
        _must(v == "NOT A RESULT",
              "G-TAILCOUNT read an unreadable count as %r, not NOT A RESULT"
              % v)
        return "no AOA_SWEEP_END -> NOT A RESULT (an unreadable count is not " \
               "a zero)"
    _control("G-TAILCOUNT/unreadable", "fail", tail_unreadable)

    # ---- G-RC-HONEST -------------------------------------------------------
    def rc_fail():
        v, _n = g_rc_honest("97", 6, 6)
        _must(v == "GATE FAIL", "G-RC-HONEST read rc=97 as %r" % v)
        return "producer rc=97 propagated -> GATE FAIL"
    _control("G-RC-HONEST/rc97", "fail", rc_fail)

    def rc_absent():
        try:
            g_rc_honest(None, 6, 6)
        except Refuse as e:
            _must(e.code == 2, "G-RC-HONEST refused with %d" % e.code)
            return "rc artefact ABSENT -> REFUSE exit 2 (a missing rc is not " \
                   "rc=0)"
        raise ValueError("G-RC-HONEST: an absent rc did NOT refuse")
    _control("G-RC-HONEST/absent", "fail", rc_absent)

    def rc_swallow():
        v, _n = g_rc_honest("0", 6, 1)
        _must(v == "GATE FAIL",
              "G-RC-HONEST read rc=0 on a 1-of-6 sweep as %r" % v)
        return "rc=0 on a TRUNCATED sweep -> GATE FAIL (the swallowed-rc class)"
    _control("G-RC-HONEST/rc0-truncated", "fail", rc_swallow)

    def rc_pass():
        v, _n = g_rc_honest("0", 6, 6)
        _must(v == "PASS", "G-RC-HONEST read a clean rc as %r" % v)
        return "producer rc=0, 6 of 6 -> PASS"
    _control("G-RC-HONEST/clean", "pass", rc_pass)

    # ---- G-UNBOUND: static committed fixtures, four directions ------------
    def ub_pos():
        v, notes = g_unbound(_fx("g_unbound_positive.sh"))
        _must(v == "BLOCKED", "G-UNBOUND read the positive fixture as %r" % v)
        _must(any("MISSING_PIN" in n for n in notes),
              "G-UNBOUND blocked but did not name MISSING_PIN")
        return "fixtures/g_unbound_positive.sh -> BLOCKED, $MISSING_PIN named"
    _control("G-UNBOUND/positive", "fail", ub_pos)

    def ub_neg():
        v, _n = g_unbound(_fx("g_unbound_negative.sh"))
        _must(v == "PASS", "G-UNBOUND read the negative fixture as %r" % v)
        return "fixtures/g_unbound_negative.sh (same file + the assignment) " \
               "-> PASS"
    _control("G-UNBOUND/negative", "pass", ub_neg)

    def ub_fence_ok():
        v, _n = g_unbound(_fx("g_unbound_fenced_ok.sh"))
        _must(v == "PASS",
              "G-UNBOUND flagged the SO3aF2 A4.3 repaired fence as %r -- that "
              "would forbid the one construction that makes sourcing a foreign "
              "init script legal" % v)
        return "set +u / source / set -u fence around $WM_PROJECT_DIR -> PASS"
    _control("G-UNBOUND/fence-repaired", "pass", ub_fence_ok)

    def ub_fence_open():
        v, notes = g_unbound(_fx("g_unbound_fence_unclosed.sh"))
        _must(v == "BLOCKED",
              "G-UNBOUND read an UNCLOSED fence as %r" % v)
        _must(any("NEVER closed" in n for n in notes),
              "G-UNBOUND blocked the unclosed fence for the wrong reason: %s"
              % notes)
        return "set +u opened and never closed -> BLOCKED (the failure mode " \
               "the fence itself introduces)"
    _control("G-UNBOUND/fence-unclosed", "fail", ub_fence_open)

    def ub_guarded():
        v, _n = g_unbound('#!/bin/sh\nset -u\necho "${MAYBE:-default}"\n')
        _must(v == "PASS",
              "G-UNBOUND flagged ${VAR:-default}, which is legal under set -u")
        return "${VAR:-default} is guarded and correctly NOT flagged"
    _control("G-UNBOUND/guarded-default", "pass", ub_guarded)

    def ub_quoted_fence():
        # THE FALSE POSITIVE THE GATE ACTUALLY PRODUCED, kept as a permanent
        # control.  Driven over `a1wrt2_run_arm.sh` in this drafting
        # invocation, an earlier text-matching form of this gate reported
        # `line 216: set +u fence opened and NEVER closed` -- and line 216 is a
        # quoted `echo` that MENTIONS the words while explaining the gate.  A
        # guard that reads TEXT rather than CODE blocks a launcher whose only
        # fault is documenting itself.
        v, notes = g_unbound(
            '#!/bin/sh\nset -u\nX=1\n'
            'echo "  under set -u, or an unclosed set +u fence."\n'
            'echo "$X"\n')
        _must(v == "PASS",
              "G-UNBOUND read `set +u` INSIDE A QUOTED STRING as a real fence "
              "directive: %s" % notes)
        return "the words `set +u` inside a quoted echo are NOT a fence -- " \
               "command position and quoting are both honoured"
    _control("G-UNBOUND/quoted-not-a-fence", "pass", ub_quoted_fence)

    def ub_single_quoted():
        v, _n = g_unbound("#!/bin/sh\nset -u\necho 'literal $NOT_A_VAR here'\n")
        _must(v == "PASS",
              "G-UNBOUND flagged $NOT_A_VAR inside SINGLE quotes, where no "
              "expansion happens at all")
        return "'$NOT_A_VAR' in single quotes is not an expansion and is NOT " \
               "flagged"
    _control("G-UNBOUND/single-quoted", "pass", ub_single_quoted)

    def ub_double_quoted_is_real():
        # The NEGATIVE of the limb above: an expansion inside DOUBLE quotes IS
        # real and must still be caught, or the quote-awareness would have
        # blinded the gate rather than sharpened it.
        v, notes = g_unbound('#!/bin/sh\nset -u\necho "value is $MISSING_ONE"\n')
        _must(v == "BLOCKED",
              "G-UNBOUND missed an expansion inside DOUBLE quotes -- the "
              "quote handling has blinded it")
        _must(any("MISSING_ONE" in n for n in notes), "wrong variable named")
        return '"$MISSING_ONE" in DOUBLE quotes IS an expansion -> BLOCKED'
    _control("G-UNBOUND/double-quoted-caught", "fail", ub_double_quoted_is_real)

    def ub_never_set_u():
        v, notes = g_unbound('#!/bin/sh\nX=1\necho "$X"\necho "$Y"\n')
        _must(v == "BLOCKED",
              "G-UNBOUND passed a launcher that never enables set -u at all")
        _must(any("never enables" in n for n in notes),
              "G-UNBOUND blocked for the wrong reason: %s" % notes)
        return "a launcher with NO `set -u` anywhere -> BLOCKED (nothing in " \
               "it is guarded, so an unset variable expands to empty rather " \
               "than aborting)"
    _control("G-UNBOUND/no-set-u-at-all", "fail", ub_never_set_u)

    def ub_assign_forms():
        # The two forms that blocked this item's own launcher, kept as a
        # permanent control so a future edit to the recogniser cannot lose them.
        v, notes = g_unbound(
            '#!/bin/sh\nset -u\n'
            'f() {\n  local name="$1" want="$2"\n  local out rc\n'
            '  out=$(true) && rc=0 || rc=$?\n'
            '  echo "$name $want $out $rc"\n}\n')
        _must(v == "PASS",
              "G-UNBOUND blocked on a multi-assignment `local` or a mid-line "
              "`&& rc=0` -- both are assignments: %s" % notes)
        return "`local a=1 b=2`, bare `local out rc`, and `... && rc=0 || " \
               "rc=$?` are all recognised as assignments"
    _control("G-UNBOUND/assignment-forms", "pass", ub_assign_forms)

    def ub_still_catches():
        # The NEGATIVE of the permissiveness above: widening the recogniser
        # must not have blinded the gate.  A genuinely unassigned variable in a
        # file FULL of assignments is still caught.
        v, notes = g_unbound(
            '#!/bin/sh\nset -u\n'
            'f() {\n  local name="$1" want="$2"\n  local out rc\n'
            '  out=$(true) && rc=0 || rc=$?\n'
            '  echo "$name $want $out $rc $GENUINELY_UNSET"\n}\n')
        _must(v == "BLOCKED",
              "G-UNBOUND missed a genuinely unassigned variable after the "
              "assignment recogniser was widened")
        _must(any("GENUINELY_UNSET" in n for n in notes),
              "wrong variable named: %s" % notes)
        return "a genuinely unassigned $GENUINELY_UNSET among many real " \
               "assignments -> still BLOCKED"
    _control("G-UNBOUND/widening-did-not-blind", "fail", ub_still_catches)

    def ub_this_launcher():
        # The instrument this gate guards, read by the gate itself.
        v, notes = g_unbound((HERE / "a1wrt2_run_arm.sh").read_text(),
                             ["A1WRT2_RUN_ROOT", "A1WRT2_STATUS_DIR",
                              "GUARDS_ONLY", "BASH_SOURCE"])
        _must(v == "PASS",
              "G-UNBOUND blocks THIS ITEM'S OWN LAUNCHER: %s" % notes)
        return "a1wrt2_run_arm.sh itself -> PASS"
    _control("G-UNBOUND/this-launcher", "pass", ub_this_launcher)

    # ---- G-NOGRAD ----------------------------------------------------------
    clean_producer = "prob.run_model()\nprob.model.add_subsystem('geo', g)\n"

    def ng_fail():
        v, notes = g_nograd(clean_producer + "totals = prob.compute_totals()\n")
        _must(v == "BLOCKED", "G-NOGRAD read a planted compute_totals as %r"
              % v)
        _must(any("1 times" in n for n in notes),
              "G-NOGRAD did not report the planted count: %s" % notes)
        return "compute_totals planted into a static copy -> BLOCKED, and the " \
               "DAFOAM_CHARTER section 2 FD-table obligation ATTACHES"
    _control("G-NOGRAD/planted", "fail", ng_fail)

    def ng_pass():
        v, _n = g_nograd(clean_producer)
        _must(v == "PASS", "G-NOGRAD read a clean producer as %r" % v)
        return "the same copy with the plant removed -> PASS"
    _control("G-NOGRAD/clean", "pass", ng_pass)

    # ---- G-WARPPROBE -------------------------------------------------------
    def wp_fail():
        v, notes = g_warpprobe({"warper_init": 0, "warper_jacvec": 1})
        _must(v == "GATE FAIL", "G-WARPPROBE read jacvec=1 as %r" % v)
        _must(any("SHIPPED" in n for n in notes),
              "G-WARPPROBE failed without naming the owed SHIPPED arm")
        return "warper_jacvec=1 planted -> GATE FAIL and a SHIPPED-image arm " \
               "becomes OWED"
    _control("G-WARPPROBE/planted", "fail", wp_fail)

    def wp_pass():
        v, _n = g_warpprobe({"warper_init": 0, "warper_jacvec": 0})
        _must(v == "PASS", "G-WARPPROBE read a clean probe as %r" % v)
        return "restored to {0,0} -> PASS, section 6 two-row obligation " \
               "DISCHARGED BY MEASUREMENT"
    _control("G-WARPPROBE/restored", "pass", wp_pass)

    def wp_blind():
        try:
            g_warpprobe({"warper_init": 0})
        except Refuse:
            return "a probe missing a key -> REFUSE (a blind channel cannot " \
                   "discharge a charter obligation)"
        raise ValueError("G-WARPPROBE: a blind probe did NOT refuse")
    _control("G-WARPPROBE/blind", "fail", wp_blind)

    # ---- G-COLDSTART-SEAM --------------------------------------------------
    def cs_uniform():
        with tempfile.TemporaryDirectory() as td:
            case = Path(td) / "case"
            (case / "4000").mkdir(parents=True)
            (case / "4000" / "U").write_text(
                "internalField   uniform (1 0 0);\n")
            try:
                g_coldstart_seam(case)
            except Refuse as e:
                _must("not nonuniform" in str(e),
                      "G-COLDSTART-SEAM: the uniform-U control refused for "
                      "the WRONG REASON: %r" % str(e))
                return "uniform U planted at 4000/ -> REFUSE, reason cited is " \
                       "the uniform field (the A1WRT section 2.2 mechanism)"
        raise ValueError("G-COLDSTART-SEAM: a uniform U did NOT refuse")
    _control("G-COLDSTART-SEAM/uniform", "fail", cs_uniform)

    def cs_zero_present():
        with tempfile.TemporaryDirectory() as td:
            case = Path(td) / "case"
            (case / "4000").mkdir(parents=True)
            (case / "4000" / "U").write_text("internalField nonuniform ...\n")
            (case / "0").mkdir()
            try:
                g_coldstart_seam(case)
            except Refuse as e:
                # The REASON is asserted: this case dir also carries a valid
                # nonuniform 4000/U, so a refusal citing the staged state would
                # mean this limb was never exercised.
                _must("exists" in str(e) and str(case / "0") in str(e),
                      "G-COLDSTART-SEAM: the 0/-present control refused for "
                      "the WRONG REASON: %r" % str(e))
                return "a 0/ directory present beside a VALID nonuniform " \
                       "4000/U -> REFUSE, and the reason cited is the 0/ dir"
        raise ValueError("G-COLDSTART-SEAM: a present 0/ did NOT refuse")
    _control("G-COLDSTART-SEAM/zero-present", "fail", cs_zero_present)

    def cs_ok():
        with tempfile.TemporaryDirectory() as td:
            case = Path(td) / "case"
            (case / "4000").mkdir(parents=True)
            (case / "4000" / "U").write_text(
                "internalField   nonuniform List<vector>\n2\n((1 0 0)(2 0 0))\n")
            v, _n = g_coldstart_seam(case)
        _must(v == "PASS", "G-COLDSTART-SEAM read a staged state as %r" % v)
        return "nonuniform 4000/U, no 0/ -> PASS"
    _control("G-COLDSTART-SEAM/staged", "pass", cs_ok)

    # ---- G-IMG / G-FREEZE --------------------------------------------------
    good_manifest = {"image_digest": PIN_IMG_DIGEST,
                     "libidwarp_md5": PIN_IDWARP_MD5}

    def img_fail():
        bad = dict(good_manifest)
        bad["libidwarp_md5"] = "0" * 32
        try:
            g_img_freeze(bad, {})
        except Refuse as e:
            _must(e.code == 4, "G-IMG refused with %d, not 4" % e.code)
            return "one pin perturbed -> REFUSE exit 4"
        raise ValueError("G-IMG: a perturbed pin did NOT refuse")
    _control("G-IMG/perturbed-pin", "fail", img_fail)

    def freeze_fail():
        try:
            g_img_freeze(dict(good_manifest, instruments={}),
                         {"runScript.py": PIN_RUNSCRIPT_MD5})
        except Refuse as e:
            _must(e.code == 4, "G-FREEZE refused with %d, not 4" % e.code)
            return "an instrument md5 absent from the manifest -> REFUSE exit 4"
        raise ValueError("G-FREEZE: a missing instrument md5 did NOT refuse")
    _control("G-FREEZE/missing-md5", "fail", freeze_fail)

    def img_pass():
        v, _n = g_img_freeze(
            dict(good_manifest,
                 instruments={"runScript.py": PIN_RUNSCRIPT_MD5}),
            {"runScript.py": PIN_RUNSCRIPT_MD5})
        _must(v == "PASS", "G-IMG/G-FREEZE read exact pins as %r" % v)
        return "pins restored -> PASS"
    _control("G-IMG/exact-pins", "pass", img_pass)

    # ---- G-YPLUS -----------------------------------------------------------
    def yp_fail():
        text = ("AOA_POINT_BEGIN idx=0 alpha=13.0\nTime = 100\n"
                "yPlus min: 0.0002 max: 1.4 mean: 0.5\n")
        v, _n = g_yplus(text)
        _must(v == "GATE FAIL", "G-YPLUS read y+max 1.4 as %r" % v)
        return "y+ max 1.4 planted -> GATE FAIL (the mesh is NOT re-cut)"
    _control("G-YPLUS/planted-1.4", "fail", yp_fail)

    def yp_blind():
        text = "AOA_POINT_BEGIN idx=0 alpha=13.0\n" + "Time = 1\n" * 250
        try:
            g_yplus(text)
        except Refuse:
            return "250 iterations and NO y+ line -> REFUSE (a blind channel " \
                   "on a point that ran is not a pass)"
        raise ValueError("G-YPLUS: a blind channel did NOT refuse")
    _control("G-YPLUS/blind-refuses", "fail", yp_blind)

    def yp_pass():
        v, _n = g_yplus(_fx("g_seam_u1_terminal_real.log"))
        _must(v == "PASS", "G-YPLUS read the REAL U1 y+ line as %r" % v)
        return "REAL A1WRT U1 bytes, y+ max 0.0386621 -> PASS"
    _control("G-YPLUS/real-u1", "pass", yp_pass)

    # ---- G-CAPS and G-CEILING (the reading half) ---------------------------
    def caps_fail():
        v, _n = g_caps("ITEM=A1WRT2\nARM=SEAM core_min=44.0\n")
        _must(v == "NOT A RESULT", "G-CAPS read a 44.0 > 10.0 overrun as %r"
              % v)
        return "fixture ledger row 44.0 core-min over SEAM's 10.0 cap -> NOT " \
               "A RESULT"
    _control("G-CAPS/over-cap", "fail", caps_fail)

    def caps_pass():
        v, _n = g_caps("ITEM=A1WRT2\nARM=SEAM core_min=3.10\n"
                       "ARM=TAIL core_min=224.75\n")
        _must(v == "GATE REACHED", "G-CAPS read an in-cap ledger as %r" % v)
        return "3.10 + 224.75 inside both caps -> GATE REACHED"
    _control("G-CAPS/in-cap", "pass", caps_pass)

    def ceil_fail():
        v, _n = g_ceiling("ARM=SEAM core_min=10.0\nARM=TAIL core_min=680.0\n")
        _must(v == "GATE FAIL", "G-CEILING read 690.0 > 685.0 as %r" % v)
        return "fixture ledger summing 690.0 > the 685.0 ceiling -> GATE FAIL"
    _control("G-CEILING/over", "fail", ceil_fail)

    def ceil_pass():
        v, notes = g_ceiling("ARM=SEAM core_min=3.10\nARM=TAIL core_min=224.75\n")
        _must(v == "GATE REACHED", "G-CEILING read 227.85 as %r" % v)
        _must(any("SPEND_CENSUS" in n for n in notes),
              "G-CEILING passed WITHOUT printing the census -- the guard's "
              "silence would then be indistinguishable from its success")
        return "227.85 of 685.0 -> GATE REACHED, census printed on the " \
               "PASSING path too"
    _control("G-CEILING/under", "pass", ceil_pass)

    def ceil_unmeasured():
        try:
            g_ceiling("ITEM=A1WRT2\nno parseable rows here\n")
        except Refuse as e:
            _must(e.code == 65, "unmeasured ledger refused with %d" % e.code)
            return "a ledger with CONTENT but no parseable core_min row -> " \
                   "REFUSE exit 65, never a zero"
        raise ValueError("G-CEILING: an unmeasured ledger did NOT refuse")
    _control("G-CEILING/unmeasured", "fail", ceil_unmeasured)

    def ceil_malformed():
        # THE CASE THAT ACTUALLY HAPPENS, and the one `d6rf_chain_driver.sh`
        # fails open on.  Driven with a REAL prior spend on the first row, so a
        # reader that silently drops it would be visible as a wrong number
        # rather than as a missing one.
        led = "ARM=SEAM core_min=100.0\nARM=TAIL core_min=1.2.3\n"
        try:
            g_ceiling(led)
        except Refuse as e:
            _must(e.code == 65,
                  "a malformed core_min refused with %d, not 65" % e.code)
            _must("UNMEASURABLE" in str(e),
                  "the malformed-token control refused for the wrong reason: "
                  "%r" % str(e))
            return "core_min=1.2.3 beside a real 100.0 -> REFUSE exit 65.  " \
                   "d6rf's reader returns EMPTY here and its driver's " \
                   "`( + cap)` unary plus turns that into a clean projection " \
                   "with the 100.0 silently dropped."
        raise ValueError("G-CEILING: a malformed core_min token did NOT refuse")
    _control("G-CEILING/malformed-token", "fail", ceil_malformed)

    def ceil_absent_is_zero():
        # The NEGATIVE direction of the same limb: an ABSENT ledger is a
        # legitimate zero -- no arm has run -- and must NOT be conflated with
        # an unreadable one.  Without this limb a reader that refused on
        # everything would also pass the three refusal controls above.
        v, _n = g_ceiling("ARM=SEAM core_min=0.0\n")
        _must(v == "GATE REACHED", "a zero-spend ledger read as %r" % v)
        return "a ledger recording a genuine 0.0 -> GATE REACHED, NOT a " \
               "refusal; 'nothing spent' and 'could not read' stay distinct"
    _control("G-CEILING/genuine-zero", "pass", ceil_absent_is_zero)

    # ---- G-STALL and G-NOBAND, both directions, on REGISTERED text ---------
    def stall_fwd():
        try:
            g_stall(["the section shows stall at 15 degrees"])
        except Refuse:
            return "'stall at 15 degrees' -> REFUSE exit 2"
        raise ValueError("G-STALL: a forward binding did NOT refuse")
    _control("G-STALL/forward", "fail", stall_fwd)

    def stall_rev():
        try:
            g_stall(["at 15 degrees it stalls"])
        except Refuse:
            return "'at 15 degrees it stalls' -> REFUSE exit 2"
        raise ValueError("G-STALL: a reverse binding did NOT refuse")
    _control("G-STALL/reverse", "fail", stall_rev)

    def stall_alpha():
        try:
            g_stall(["separation onset at alpha 14"])
        except Refuse:
            return "'separation onset at alpha 14' -> REFUSE exit 2"
        raise ValueError("G-STALL: an alpha-form binding did NOT refuse")
    _control("G-STALL/alpha-form", "fail", stall_alpha)

    honest = [
        "A non-converged point is not evidence of separation -- it is "
        "evidence that the steady solver stopped converging.",
        "2-D steady RANS with SA past the onset of significant separation is "
        "not a valid model of the flow at any resolution.",
        "NACA0012 at alpha 13...18 is at or past the onset of significant "
        "separation, and dCL/dalpha should flatten and then reverse.",
        "A converged high-alpha point is not evidence of attached flow.",
        "G-TAILCOUNT: PASS -- 6 of 6, every declared alpha certified one way "
        "or the other",
    ]

    def stall_honest():
        v, _n = g_stall(honest)
        _must(v == "PASS",
              "G-STALL FIRED on the item's own registered honest caveat text. "
              "A gate that refuses its own scope section would make every "
              "grade exit 2, which is a defect and not a strictness.")
        return "%d registered section-9/10 caveat lines, incl. the one with " \
               "'alpha 13...18' and 'separation' in it -> NOT flagged" \
               % len(honest)
    _control("G-STALL/honest-caveats", "pass", stall_honest)

    def noband_fail():
        try:
            g_noband(["the tail value is grid-converged at 3 levels"])
        except Refuse:
            return "'grid-converged' planted -> REFUSE exit 2"
        raise ValueError("G-NOBAND: a band claim did NOT refuse")
    _control("G-NOBAND/planted", "fail", noband_fail)

    def noband_pass():
        v, _n = g_noband(honest)
        _must(v == "PASS", "G-NOBAND fired on honest caveat text")
        return "the same caveat lines -> NOT flagged"
    _control("G-NOBAND/honest", "pass", noband_pass)
    return 0


def _st_noassert() -> int:
    """Q-NOASSERT -- this file's own AST, audited, with a live positive control.

    The family requirement: ZERO `ast.Assert` nodes outside the selftest,
    because `assert` vanishes under `python3 -O` and a guard that disappears
    under an optimisation flag is not a guard.  This file carries zero
    ANYWHERE, so the selftest behaves identically under both flags -- which is
    why the two counts the supervisor asks for can match at all."""
    src = Path(__file__).resolve().read_text()
    tree = ast.parse(src)
    boundary = None
    for i, line in enumerate(src.splitlines(), 1):
        if line.startswith("# === SELFTEST BOUNDARY ==="):
            boundary = i
            break
    if boundary is None:
        raise Refuse("Q-NOASSERT: the SELFTEST BOUNDARY marker is missing")
    nodes = [n for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    above = [n for n in nodes if n.lineno < boundary]
    below = [n for n in nodes if n.lineno >= boundary]

    def na_pos():
        planted = src.replace("REGISTERED_FIXTURES = [",
                              "assert True  # PLANTED CONTROL\n"
                              "REGISTERED_FIXTURES = [", 1)
        n = len([x for x in ast.walk(ast.parse(planted))
                 if isinstance(x, ast.Assert)])
        _must(n == 1,
              "Q-NOASSERT: the auditor read %d asserts in a copy carrying "
              "exactly one PLANTED assert -- the auditor is BLIND and its "
              "zero is worthless" % n)
        return "a planted `assert` in a copy of this file is SEEN (count 1)"
    _control("Q-NOASSERT/positive", "fail", na_pos)

    def na_real():
        _must(len(above) == 0,
              "Q-NOASSERT: %d ast.Assert nodes ABOVE the selftest boundary "
              "(lines %s).  They vanish under python3 -O."
              % (len(above), [n.lineno for n in above]))
        _must(len(below) == 0,
              "Q-NOASSERT: %d ast.Assert nodes below the boundary; this file "
              "registers ZERO anywhere so the selftest is identical under -O"
              % len(below))
        return "this file: 0 above the boundary (line %d), 0 below, %d total" \
               % (boundary, len(nodes))
    _control("Q-NOASSERT/this-file", "pass", na_real)
    return 0


def selftest() -> int:
    """Drive every control.  SELFTEST-SUCCESS-PATH runs FIRST, by design."""
    print("%s SELFTEST -- host python, NO compute, NO container, NO queue "
          "drop, NOT FROZEN" % ITEM)
    print("python %s   optimisation flag active: %s"
          % (sys.version.split()[0], "-O (asserts disabled)"
             if not __debug__ else "none (asserts enabled)"))
    legs = (("SELFTEST-SUCCESS-PATH", _st_success_path),
            ("SELFTEST-EXIT-TRAP", _st_exit_trap),
            ("SELFTEST-COMPOSE", _st_compose),
            ("SELFTEST-GATE-CONTROLS", _st_gate_controls),
            ("SELFTEST-NOASSERT", _st_noassert))
    try:
        for name, fn in legs:
            print("")
            print("---- %s ----" % name)
            fn()
    except (Refuse, ValueError) as e:
        print("%s_SELFTEST FAILED -- %s" % (ITEM, e))
        return 1
    n_fail = len([c for c in _CONTROL_LOG if c[2] == "EXERCISED-FAIL"])
    n_pass = len([c for c in _CONTROL_LOG if c[2] == "EXERCISED-PASS"])
    n_not = len([c for c in _CONTROL_LOG if c[2] == "NOT EXERCISED"])
    print("")
    print("%s_SELFTEST legs=%d controls=%d EXERCISED-FAIL=%d "
          "EXERCISED-PASS=%d NOT-EXERCISED=%d"
          % (ITEM, len(legs), len(_CONTROL_LOG), n_fail, n_pass, n_not))
    if n_not:
        print("%s_SELFTEST REFUSED -- NOT EXERCISED is never counted as a pass"
              % ITEM)
        return 1
    print("%s_SELFTEST OK -- every control driven in a NAMED direction, and "
          "the SUCCESS PATH was driven FIRST" % ITEM)
    return 0


if __name__ == "__main__":
    sys.exit(main())
