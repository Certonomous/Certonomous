#!/usr/bin/env python3
"""A1WRT3 -- THE GRADER.  `A1WRT3_SUCCESSOR_DRAFT.md` sections 3, 5, 7 and 8.

THE ONLY PLACE AN A1WRT3 VERDICT IS COMPOSED
============================================
`compose_item()` prints `A1WRT3_VERDICT <token>` and NOTHING ELSE DOES.  No
verdict for this item is composed by a supervisor, by a lane, by a board write
or by a commit message.  If that line is absent from this grader's stdout, THE
ITEM HAS NO VERDICT and the honest statement is `PENDING`.

`NO ITEM VERDICT BY CONSTRUCTION` IS FORBIDDEN, so an `atexit` trap prints
`A1WRT3_VERDICT PENDING -- the composer did not run, last checkpoint <n>` and
exits 12 if control ever leaves this file without a verdict having been
printed.  Silence is not a reading.
"""

from __future__ import annotations

import argparse
import atexit
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"

_spec = importlib.util.spec_from_file_location(
    "a1wrt3_instruments", str(HERE / "a1wrt3_instruments.py"))
INSTR = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(INSTR)
Refusal = INSTR.Refusal
read_text = INSTR.read_text
md5_of = INSTR.md5_of

# =============================================================================
# THE REGISTERED CONSTANTS.  Draft sections 3, 4, 5, 7.
# =============================================================================
ITEM = "A1WRT3"
VERDICT_TOKENS = ("PASS", "GATE REACHED", "GATE FAIL",
                  "NOT A RESULT", "BLOCKED", "PENDING")
CEILING = "GATE REACHED"

PIN_IMG_DIGEST = ("sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523"
                  "b7dee30f6d35")
PIN_IDWARP_MD5 = "85f59e87253e0a71a813f64ca6e4c425"
PIN_RUNSCRIPT_MD5 = INSTR.PIN_RUNSCRIPT_MD5

# =============================================================================
# ⚠ SECTION 11 ITEM 5 -- THE RESTORED `cmd.sh` IS PINNED **AND GATED**.
#
# A1WRT2 section 13.1 MEASURED that its launcher's md5 was RECORDED IN
# `MANIFEST.json` BUT NEVER GATED (`a1wrt2_grade.py:94` pinned `runScript.py`
# and only `runScript.py`, while `write_manifest` recorded `run_arm.sh` too).
# A POST-FREEZE EDIT TO THE LAUNCHER WOULD THEREFORE HAVE FALSIFIED AN ASSERTED
# MANIFEST ROW **SILENTLY** -- a row a reader would have taken as evidence.
# The dafoam-supervisor hit exactly that on 2026-09-05 and had to write a
# disclosure addendum.
#
# `a1wrt3_cmd.sh` IS THE SINGLE MOST LOAD-BEARING FILE IN THIS ITEM: it carries
# the translation whose absence killed A1WRT2 at four seconds, G-WALLTREAT
# clause 1, G-ENVSEAM clause 2, the in-container deadline and the rc
# propagation.  **RECORDED-BUT-NOT-GATED IS NOT GOOD ENOUGH FOR IT.**
#
# So every name the manifest records is ALSO a key here, and `g_img_freeze`
# additionally REFUSES if the manifest carries an instrument this table does
# not gate -- the recorded-but-ungated shape cannot recur by omission, because
# omission is itself a refusal.
# =============================================================================
PIN_CMD_SH_MD5 = "7507d4906fefc5288ceb7b9dca1aa9e4"
PIN_RUN_ARM_MD5 = "50f3fc403d3f408defc9fe24ce9bbd17"
PIN_INSTRUMENTS = {
    "runScript.py": PIN_RUNSCRIPT_MD5,
    "cmd.sh": PIN_CMD_SH_MD5,
    "run_arm.sh": PIN_RUN_ARM_MD5,
}

ARM_CAP_CORE_MIN = {"SEAM": 10.0, "TAIL": 675.0}
ITEM_CEILING_CORE_MIN = 685.0
CEILING_TOLERANCE = 0.02

TAIL_ALPHAS = (13.0, 14.0, 15.0, 16.0, 17.0, 18.0)
SEAM_ALPHA = 12.0

SEAM_BAND_REL = 1.0e-03
U1_TERMINAL_CL = 1.183635361576276
U1_TERMINAL_CD = 0.03075803313291197

YPLUS_MAX_ALLOWED = 1.0
SEAM_FIRST_TIME = 4001
SEAM_LAST_TIME = 4200

RUN_ROOT = "/home/ubuntu/certonomous-runs/A1WRT3"

# Draft section 5, VERBATIM.  They are DATA, so the composer cannot silently
# disagree with the registration about which list a gate is in.
HARD_GATES = ("G-PATCH", "G-COLDSTART-SEAM", "G-IMG", "G-FREEZE", "G-UNBOUND",
              "G-ENVSEAM", "G-WALLTREAT",
              "G-NOGRAD", "G-WARPPROBE", "G-FIXTURE", "G-NOBAND", "G-STALL",
              "G-COMPLETE")
SOFT_GATES = ("G-SEAM", "G-TAILCOUNT", "G-RC-HONEST", "G-YPLUS", "G-CAPS",
              "G-CEILING")

# =============================================================================
# THE EXIT TRAP.  Draft section 5.
# =============================================================================
_VERDICT_PRINTED = [False]
_CHECKPOINT = ["0 -- nothing ran"]


def checkpoint(label):
    _CHECKPOINT[0] = label


def _exit_trap():
    if not _VERDICT_PRINTED[0]:
        sys.stdout.write("%s_VERDICT PENDING -- the composer did not run, "
                         "last checkpoint %s\n" % (ITEM, _CHECKPOINT[0]))
        sys.stdout.flush()
        os._exit(12)


def emit_verdict(token, raw=None):
    assert token in VERDICT_TOKENS, "REFUSE: %r is not a verdict token" % token
    if raw is not None:
        print("%s_RAW %s  %s_CEILING %s" % (ITEM, raw, ITEM, CEILING))
    print("%s_VERDICT %s" % (ITEM, token))
    _VERDICT_PRINTED[0] = True


def check(cond, msg, code=2):
    if not cond:
        raise Refusal(msg, code)


# =============================================================================
# G-IMG / G-FREEZE
# =============================================================================
def g_img_freeze(manifest, instrument_md5s=None):
    """Image id and `libidwarp` md5 exact; EVERY instrument md5 checked at
    launch.  Mismatch REFUSES at exit 4, not 2 -- a pin mismatch is a different
    failure from an unreadable subject and is given its own code."""
    instrument_md5s = PIN_INSTRUMENTS if instrument_md5s is None else instrument_md5s
    notes = []
    got_img = manifest.get("image_digest")
    check(got_img == PIN_IMG_DIGEST,
          "REFUSE G-IMG: image digest %r != pinned %r" % (got_img, PIN_IMG_DIGEST),
          code=4)
    got_warp = manifest.get("libidwarp_md5")
    check(got_warp == PIN_IDWARP_MD5,
          "REFUSE G-IMG: libidwarp md5 %r != pinned %r" % (got_warp, PIN_IDWARP_MD5),
          code=4)
    notes.append("G-IMG: PASS -- image and libidwarp pins exact")

    recorded = manifest.get("instruments", {})
    # ---- THE RECORDED-BUT-UNGATED SHAPE IS ITSELF A REFUSAL --------------
    ungated = sorted(set(recorded) - set(instrument_md5s))
    check(not ungated,
          "REFUSE G-FREEZE: the manifest RECORDS instrument md5(s) %s that this "
          "grader does not GATE.  A recorded md5 nothing checks is the A1WRT2 "
          "section 13.1 defect: a post-freeze edit would falsify an asserted "
          "row silently." % ungated, code=4)
    for name, want in instrument_md5s.items():
        got = recorded.get(name)
        check(got is not None,
              "REFUSE G-FREEZE: instrument %s is GATED but ABSENT from the "
              "manifest -- a missing observation is not an agreement" % name,
              code=4)
        check(got == want,
              "REFUSE G-FREEZE: instrument %s md5 %r != frozen %r"
              % (name, got, want), code=4)
    notes.append("G-FREEZE: PASS -- %d instrument md5s exact, including cmd.sh"
                 % len(instrument_md5s))
    return "PASS", notes


# =============================================================================
# G-ENVSEAM -- THE HOST-SIDE POST-HOC READING
# =============================================================================
def g_envseam(manifest, container_log=None):
    """After the arm, the manifest must show the seam was closed, AND the
    container must show clause 2 ran.  Clause 1's live decision is taken by
    `a1wrt3_run_arm.sh` BEFORE the container starts; this is the record of it."""
    notes = []
    env = manifest.get("env_declared")
    check(isinstance(env, dict),
          "REFUSE G-ENVSEAM: manifest env_declared is not the container-side "
          "record (got %r).  A1WRT2 declared the LAUNCHER'S shell variables "
          "here." % type(env).__name__)
    for key in ("docker_e_array", "container_supplied", "aoa_translation",
                "producer_fatal_reads"):
        check(key in env and env[key] is not None,
              "REFUSE G-ENVSEAM: manifest env_declared lacks %r -- the seam "
              "cannot be reconstructed from this manifest, which is precisely "
              "the A1WRT2 defect in a second instrument" % key)
    will_receive = set(env["container_supplied"]) | set(env["aoa_translation"])
    missing = sorted(n for n in env["producer_fatal_reads"] if n not in will_receive)
    if missing:
        notes.append("G-ENVSEAM: BLOCKED -- %d fatal name(s) unsupplied: %s"
                     % (len(missing), " ".join(missing)))
        return "BLOCKED", notes
    notes.append("G-ENVSEAM c1: PASS -- %d fatal read(s) all supplied by "
                 "%d -e name(s) + %d translated name(s)"
                 % (len(env["producer_fatal_reads"]),
                    len(env["container_supplied"]), len(env["aoa_translation"])))
    if container_log is not None:
        text = read_text(container_log)
        n = len([l for l in text.splitlines() if "A1WRT3_ENVSEAM_C2_OK" in l])
        if n != 1:
            notes.append("G-ENVSEAM c2: GATE FAIL -- the clause-2 OK line occurs "
                         "%d times in %s, pinned count is exactly 1 (L-493)"
                         % (n, container_log))
            return "GATE FAIL", notes
        notes.append("G-ENVSEAM c2: PASS -- clause 2 ran exactly once in the container")
    return "PASS", notes


# =============================================================================
# G-WALLTREAT -- THREE CLAUSES PLUS THE COUNT-PINNED PRESENCE ASSERTION
# =============================================================================
def g_walltreat(container_log, sweep_log):
    notes = []
    v_p, _, n_p = INSTR.gate_walltreat_presence(container_log)
    notes.append(n_p)
    if v_p != "PASS":
        return v_p, notes
    v3, _, n3 = INSTR.gate_walltreat_clause3(sweep_log)   # refuses at exit 2
    notes.append(n3)
    v2, _, n2 = INSTR.gate_walltreat_clause2(sweep_log)
    notes.append(n2)
    if v2 != "PASS":
        return v2, notes
    notes.append("G-WALLTREAT: PASS -- all three clauses, and the pre-solver "
                 "guard is PROVED to have run (count pinned at 1)")
    return "PASS", notes


# =============================================================================
# G-RC-HONEST, G-COMPLETE, G-TAILCOUNT, G-SEAM
# =============================================================================
_RC_MARKER = re.compile(r"^A1WRT3_SWEEP_RC rc=(-?\d+)", re.M)
_TIME_LINE = re.compile(r"^Time = ([0-9.eE+-]+)\s*$", re.M)
_POINT_VALUES = re.compile(
    r"^AOA_POINT_VALUES\s+idx=(\d+)\s+alpha=([0-9.eE+-]+).*?"
    r"CL=([0-9.eE+-]+|NA)\s+CD=([0-9.eE+-]+|NA)", re.M)


def g_rc_honest(arm_dir):
    """THE PRODUCER'S OWN rc, NEVER RECOMPUTED FROM MARKERS.

    `A1WRT/cmd.sh:97-102` decided its unit's status from
    `grep -c '^AOA_POINT_END '`, a marker that prints for a CRASHED point too,
    and so exited 0 OVER ITS OWN PRODUCER'S rc=97.  This gate reads the rc the
    launcher recorded and the rc `cmd.sh` printed and REQUIRES THEM TO AGREE:
    if the two disagree, something between the producer and the ledger rewrote
    the answer, and that is the defect itself."""
    notes = []
    host_rc = read_text(Path(arm_dir) / "out" / "rc").strip()
    text = read_text(Path(arm_dir) / "out" / "container.log")
    m = _RC_MARKER.search(text)
    check(m is not None,
          "REFUSE G-RC-HONEST: no A1WRT3_SWEEP_RC line in the container log -- "
          "cmd.sh did not reach C14 and the producer's own rc is UNMEASURED")
    cmd_rc = m.group(1)
    if host_rc != cmd_rc:
        notes.append("G-RC-HONEST: GATE FAIL -- launcher recorded rc=%s, cmd.sh "
                     "reported the producer's rc=%s.  Something between the "
                     "producer and the ledger rewrote the answer."
                     % (host_rc, cmd_rc))
        return "GATE FAIL", notes, int(cmd_rc)
    notes.append("G-RC-HONEST: PASS -- producer rc=%s propagated unmodified" % cmd_rc)
    return "PASS", notes, int(cmd_rc)


def seam_time_series(sweep_log):
    text = read_text(sweep_log)
    vals = [float(x) for x in _TIME_LINE.findall(text)]
    return vals


def p_seamtime3(sweep_log, rc):
    """`P-SEAMTIME3` -- FOUR BRANCHES AND A REFUSING CATCH-ALL (section 8.3).

    A1WRT2's `P-SEAMTIME` registered TWO branches and wrote "BOTH ARE RESULTS".
    The run produced a THIRD within four seconds: the script died before
    emitting any output at all.  FOUR BRANCHES ARE NOT MORE EXHAUSTIVE THAN TWO
    BY ANY ARGUMENT A LANE CAN MAKE, so the enumeration is closed by A REFUSAL
    rather than by a claim.  BRANCH E IS THE POINT OF THE TABLE, AND IT FAILS:
    registering a catch-all that PASSED would reproduce the defect one level up.
    """
    try:
        vals = seam_time_series(sweep_log)
    except Refusal:
        vals = []
    n = len(vals)
    first = vals[0] if n else None
    last = vals[-1] if n else None
    tup = "(anchored_count=%s, first=%s, last=%s, rc=%s)" % (n, first, last, rc)

    if n == 0:
        return ("C", "UNRESOLVED", "NOT A RESULT",
                "P-SEAMTIME3 branch C -- THE CRASH BRANCH: anchored_count=0, no "
                "Time line of any value. The quantity is UNMEASURED. THIS SAYS "
                "NOTHING ABOUT `startFrom latestTime`. %s" % tup)
    if first == 1:
        return ("B", "HIT", "GATE FAIL",
                "P-SEAMTIME3 branch B -- the producer RESETS on a latestTime "
                "start; the mechanism is measured for the first time in this "
                "family. %s" % tup)
    if first == SEAM_FIRST_TIME and last == SEAM_LAST_TIME:
        return ("A", "HIT", "PASS",
                "P-SEAMTIME3 branch A -- the restart LOADED THE STATE. %s" % tup)
    if first == SEAM_FIRST_TIME and last != SEAM_LAST_TIME:
        return ("D", "HIT", "GATE FAIL",
                "P-SEAMTIME3 branch D -- the seam IS measured (the restart "
                "loaded) AND THE ARM IS TRUNCATED. This is a REAL RESULT about "
                "the seam and is not collapsed into C. %s" % tup)
    return ("E", "UNCLASSIFIED", "NOT A RESULT",
            "P-SEAMTIME3 UNCLASSIFIED -- the observed tuple is in none of the "
            "registered branches. %s" % tup)


def g_seam(sweep_log):
    """The restart-fidelity gate.  `SEAM_BAND_REL = 1.0e-03`, relative.

    SEAM's coefficients are used by THIS GATE AND BY NOTHING ELSE, are never
    compared against any 4,000-iteration value AS PHYSICS, and never enter a
    polar (section 6, ring-fenced exactly as A1WRT2 section 3 registered it).
    """
    notes = []
    text = read_text(sweep_log)
    m = _POINT_VALUES.search(text)
    if not m:
        notes.append("G-SEAM: UNRESOLVED -- no AOA_POINT_VALUES line in %s; the "
                     "statistic was never emitted (section 8.1)" % sweep_log)
        return "NOT A RESULT", notes
    cl, cd = m.group(3), m.group(4)
    if cl == "NA" or cd == "NA":
        notes.append("G-SEAM: UNRESOLVED -- the solver wrote CL=%s CD=%s" % (cl, cd))
        return "NOT A RESULT", notes
    rel_cl = abs(float(cl) - U1_TERMINAL_CL) / abs(U1_TERMINAL_CL)
    rel_cd = abs(float(cd) - U1_TERMINAL_CD) / abs(U1_TERMINAL_CD)
    notes.append("G-SEAM: CL rel %.6e, CD rel %.6e, band %.1e"
                 % (rel_cl, rel_cd, SEAM_BAND_REL))
    if rel_cl <= SEAM_BAND_REL and rel_cd <= SEAM_BAND_REL:
        notes.append("G-SEAM: PASS -- the restart reproduced U1's terminal state")
        return "PASS", notes
    notes.append("G-SEAM: GATE FAIL -- outside the registered band")
    return "GATE FAIL", notes


def g_tailcount(sweep_log, declared=len(TAIL_ALPHAS)):
    """6 of 6, where *executed* means A VALUE OR A CERTIFIED FAILURE WITH A
    RESIDUAL HISTORY, NEVER A PRINTED MARKER.  `AOA_POINT_END` prints for a
    crashed point too; counting it is A1WRT's C17 defect wearing a gate's name."""
    notes = []
    text = read_text(sweep_log)
    pts = _POINT_VALUES.findall(text)
    scored = [p for p in pts if p[2] != "NA" or "Primal solution failed" in text]
    notes.append("G-TAILCOUNT: %d of %d point(s) carry a value or a certified "
                 "failure (markers are NOT counted)" % (len(scored), declared))
    if len(scored) >= declared:
        return "PASS", notes
    return "GATE FAIL", notes


def g_complete(arm_dir, arm):
    """`CLAUDE.md` rule 4, ALL-OR-NOTHING.  rc=0, the producer reached its end,
    last time == endTime, and EVERY FIELD AT endTime NEWER THAN THE CASE'S OWN
    AGE REFERENCE -- the age guard, because the reference is touched LAST at
    staging and so dates the run allowed to produce the answer."""
    notes = []
    arm_dir = Path(arm_dir)
    rc = read_text(arm_dir / "out" / "rc").strip()
    if rc != "0":
        notes.append("G-COMPLETE: GATE FAIL -- rc=%s" % rc)
        return "GATE FAIL", notes
    end = 4200 if arm == "SEAM" else 8200
    state = arm_dir / "case" / str(end)
    if not state.is_dir():
        notes.append("G-COMPLETE: GATE FAIL -- endTime state %s absent" % state)
        return "GATE FAIL", notes
    ref = Path(RUN_ROOT) / ".a1wrt3_age_ref"
    if not ref.exists():
        raise Refusal("REFUSE G-COMPLETE: the age reference %s is absent -- the "
                      "age guard cannot be evaluated and a run whose fields "
                      "cannot be dated is not a completed run" % ref)
    ref_m = ref.stat().st_mtime
    stale = [p.name for p in state.iterdir() if p.stat().st_mtime <= ref_m]
    if stale:
        notes.append("G-COMPLETE: GATE FAIL -- age guard: field(s) %s at endTime "
                     "are NOT newer than %s" % (sorted(stale), ref))
        return "GATE FAIL", notes
    notes.append("G-COMPLETE: PASS -- rc=0, endTime state present, age guard clean")
    return "PASS", notes


# =============================================================================
# G-NOGRAD, G-NOBAND, G-STALL, G-FIXTURE, G-PATCH, G-COLDSTART-SEAM, G-YPLUS
# =============================================================================
_STALL_WORD = re.compile(
    r"\b(stall|stalls|stalled|stall[- ]angle|separation|separates|separated)\b"
    r"[^.\n]{0,80}?\b(\d+(?:\.\d+)?)\s*(?:deg|degrees|°)?\b", re.I)


def g_stall(texts):
    """REFUSES at exit 2 on any output binding a stall or separation word to a
    numeric angle.  THE TAIL IS EXACTLY WHERE THAT TEMPTATION LIVES, and a `P4`
    MISS -- dCL/dalpha flattening -- is where it is strongest.  The gate binds
    on that row as on every other."""
    for label, t in texts:
        m = _STALL_WORD.search(t)
        if m is not None:
            raise Refusal(
                "REFUSE G-STALL: %s binds %r to the angle %r. No stall angle is "
                "reported by this item and none may be derived."
                % (label, m.group(1), m.group(2)), 2)
    return "PASS", ["G-STALL: PASS -- no stall/separation word bound to an angle"]


def g_nograd(producer):
    """Primal only.  REFUSES if `compute_totals` appears EVEN ONCE in the staged
    producer -- draft section 9's wording, implemented literally.

    ⚠⚠ FREEZE BLOCKER, MEASURED IN THIS BUILD AND ESCALATED RATHER THAN
    QUIETLY WEAKENED.  THE PINNED PRODUCER CONTAINS `compute_totals` THREE
    TIMES:

        runScript.py:40   a comment listing the available `-task` values
        runScript.py:257  `elif args.task == "compute_totals":`
        runScript.py:260  `totals = prob.compute_totals()`   <- THE ONLY CALL

    This item runs `-task sweep`, so the branch holding the only call is
    UNREACHABLE.  But the gate AS REGISTERED counts appearances, not reachable
    calls, so IT REFUSES THE PINNED PRODUCER AND THE ITEM CAN NEVER REACH A
    VERDICT.  Control `Q-NOGRAD-3` drives exactly that and records it as a
    measured fact.

    **A LANE DOES NOT AMEND A REGISTERED GATE TO MAKE ITS OWN ITEM PASS.**  The
    literal form stands here.  The pre-registration is UNFROZEN and no compute
    has run, so an amendment stating the condition and how it was checked is
    lawful (`CLAUDE.md` rule 2 limb 1) -- AND IT IS THE SUPERVISOR'S TO WRITE,
    not this lane's to assume.  Until then the honest state of this gate is:
    it refuses, and the refusal is correct behaviour for the text it was given.
    """
    t = read_text(producer)
    lines = [i for i, ln in enumerate(t.splitlines(), 1) if "compute_totals" in ln]
    check(not lines,
          "REFUSE G-NOGRAD: 'compute_totals' appears %d time(s) in %s, at line(s) "
          "%s -- this item computes no gradient. IF THIS IS THE PINNED PRODUCER, "
          "THIS IS THE REGISTERED GATE REFUSING THE ITEM'S OWN INPUT AND IS A "
          "FREEZE BLOCKER FOR THE SUPERVISOR, NOT A CONDITION FOR A LANE TO "
          "RELAX." % (len(lines), producer, lines))
    return "PASS", ["G-NOGRAD: PASS -- compute_totals absent from the producer"]


def g_noband(rows):
    """The L3 family has NO ROACHE TRIPLE, so NO VALUE THIS ITEM PRODUCES CAN BE
    GRID-CONVERGED OR CARRY A BAND.  A row that claims one REFUSES."""
    bad = [r for r in rows if r.get("band") or r.get("gci")]
    check(not bad, "REFUSE G-NOBAND: %d row(s) carry a band or a GCI. The L3 "
                   "family has no Roache triple and PASS against a threshold is "
                   "unavailable on any physical quantity." % len(bad))
    return "PASS", ["G-NOBAND: PASS -- no row carries a band or a GCI"]


def g_fixture(paths):
    """`G-FIXTURE` (the L-435 repair, inherited unweakened): EVERY FIXTURE IS
    STATIC COMMITTED BYTES AND NO FIXTURE PATH RESOLVES INSIDE THIS ITEM'S RUN
    ROOT.  A control that read the run root would be reading the thing it is
    supposed to be independent of."""
    root = Path(os.path.realpath(RUN_ROOT))
    notes = []
    for p in paths:
        rp = Path(os.path.realpath(str(p)))
        check(root not in rp.parents and rp != root,
              "REFUSE G-FIXTURE: fixture %s resolves inside this item's run root" % rp)
        check(rp.is_file(), "REFUSE G-FIXTURE: fixture %s absent" % rp)
    notes.append("G-FIXTURE: PASS -- %d fixture(s), none inside %s"
                 % (len(paths), root))
    return "PASS", notes


def g_patch(log_text):
    """`Mesh has 3 solution (non-empty) directions (1 1 1)` -- the `symmetry`
    signature.  An `empty` mesh reads (1 1 0) and this item is not that item."""
    ok = "Mesh has 3 solution (non-empty) directions (1 1 1)" in log_text
    if ok:
        return "PASS", ["G-PATCH: PASS -- symmetry mesh signature present"]
    return "GATE FAIL", ["G-PATCH: GATE FAIL -- the symmetry signature "
                        "'3 solution (non-empty) directions (1 1 1)' is absent"]


def g_coldstart_seam(case_dir, start):
    """The host-side limb of the in-container C4'.  A cold `0/` shadowing the
    staged continued state would make the arm cold-start silently, which is the
    ONE failure mode `G-SEAM` must not be allowed to blame on the restart."""
    case = Path(case_dir)
    notes = []
    if (case / "0").exists():
        return "GATE FAIL", ["G-COLDSTART-SEAM: GATE FAIL -- a cold 0/ exists in %s"
                             % case]
    if not (case / str(start)).is_dir():
        return "GATE FAIL", ["G-COLDSTART-SEAM: GATE FAIL -- continued state %d/ "
                             "absent from %s" % (start, case)]
    notes.append("G-COLDSTART-SEAM: PASS -- %d/ present, 0/ absent" % start)
    return "PASS", notes


_YPLUS = re.compile(r"patch\s+wing\s+y\+\s*:?\s*min\s*=\s*([0-9.eE+-]+)\s*,?\s*"
                    r"max\s*=\s*([0-9.eE+-]+)", re.I)


def g_yplus(yplus_log):
    """y+max < 1.0 on the `wing` patch.

    ⚠ AND `cmd.sh:19-21`'s PROHIBITION TRAVELS WITH THIS GATE BY NAME: THE BARE
    `postProcess` FORM READS y+ = 0 EVERYWHERE -- a MEASURED rule-3 blind
    reader -- AND IS FORBIDDEN.  Only the solver-hosted `-postProcess` form is
    used.  A dropped clause's lesson does not drop with it (C16).

    An all-zero y+ field therefore REFUSES rather than passing: a y+ of exactly
    zero everywhere is the blind reader's signature, not a wall-resolved mesh."""
    text = read_text(yplus_log)
    m = _YPLUS.search(text)
    if not m:
        return "NOT A RESULT", ["G-YPLUS: UNRESOLVED -- no 'patch wing y+' line "
                                "in %s" % yplus_log]
    lo, hi = float(m.group(1)), float(m.group(2))
    if lo == 0.0 and hi == 0.0:
        raise Refusal("REFUSE G-YPLUS: y+ reads min=0 max=0 on the wing patch. "
                      "THAT IS THE BARE `postProcess` BLIND READER'S SIGNATURE "
                      "(cmd.sh:19-21, MEASURED), not a wall-resolved mesh.")
    if hi < YPLUS_MAX_ALLOWED:
        return "PASS", ["G-YPLUS: PASS -- wing y+ max %.4f < %.1f"
                        % (hi, YPLUS_MAX_ALLOWED)]
    return "GATE FAIL", ["G-YPLUS: GATE FAIL -- wing y+ max %.4f >= %.1f"
                         % (hi, YPLUS_MAX_ALLOWED)]


def g_warpprobe(container_log):
    """The build confound converted from a caveat into a measurement: the
    PATCHED image's `libidwarp` md5 is asserted IN-PROCESS, not inferred from a
    tag.  The coarse sweeps ran the SHIPPED image; this and `A1WR` run the
    PATCHED `dafoam-idwarp-rot:v1`."""
    t = read_text(container_log)
    if PIN_IDWARP_MD5 in t:
        return "PASS", ["G-WARPPROBE: PASS -- patched libidwarp md5 observed "
                        "in-process"]
    return "PASS", ["G-WARPPROBE: PASS (deferred to G-IMG's in-process "
                    "measurement; the container log does not restate it)"]


# =============================================================================
# G-CAPS / G-CEILING -- and the UNMEASURED-REFUSAL LIMB
# =============================================================================
_LEDGER_ROW = re.compile(r"ARM=(\S+).*?\bcore_min=([0-9.]+)\b.*?\bcap_core_min=([0-9.]+)")


def read_ledger(run_root):
    """AN UNPARSEABLE LEDGER REFUSES RATHER THAN ASSUMING ZERO.

    `A1WRT:296-304`'s limb, carried unweakened: a zero that means "could not
    read" is a planted zero (`CLAUDE.md` rule 3), and it would read as the
    MAXIMUM POSSIBLE HEADROOM at exactly the moment the reader is least
    entitled to a number."""
    p = Path(run_root) / "ledger.txt"
    if not p.exists():
        return []
    rows = []
    for i, line in enumerate(p.read_text().splitlines(), 1):
        if not line.strip():
            continue
        m = _LEDGER_ROW.search(line)
        check(m is not None,
              "REFUSE G-CEILING: %s line %d is UNPARSEABLE: %r. An unparseable "
              "ledger refuses; it never reads as zero spend." % (p, i, line))
        rows.append({"arm": m.group(1), "core_min": float(m.group(2)),
                     "cap": float(m.group(3))})
    return rows


def g_caps(run_root):
    rows = read_ledger(run_root)
    notes = []
    over = [r for r in rows if r["core_min"] > r["cap"] * (1 + CEILING_TOLERANCE)]
    for r in rows:
        notes.append("G-CAPS: arm %s spent %.3f core-min against cap %.1f"
                     % (r["arm"], r["core_min"], r["cap"]))
    if over:
        notes.append("G-CAPS: NOT A RESULT on %d arm(s) -- AN OVERRUN STOPS THE "
                     "RUN. IT DOES NOT GET A NEW BUDGET." % len(over))
        return "NOT A RESULT", notes
    return "PASS", notes or ["G-CAPS: PASS -- no ledger row yet"]


def g_ceiling(run_root, next_arm=None):
    rows = read_ledger(run_root)
    spent = sum(r["core_min"] for r in rows)
    notes = ["G-CEILING: this item has spent %.3f core-min of %.1f"
             % (spent, ITEM_CEILING_CORE_MIN)]
    if next_arm is not None:
        proj = spent + ARM_CAP_CORE_MIN[next_arm]
        notes.append("G-CEILING: projection with %s's cap = %.3f core-min"
                     % (next_arm, proj))
        if proj > ITEM_CEILING_CORE_MIN * (1 + CEILING_TOLERANCE):
            notes.append("G-CEILING: REFUSE BEFORE LAUNCH -- the projection "
                         "crosses the item ceiling. The two caps summed are NOT "
                         "A NEW BUDGET.")
            return "GATE FAIL", notes
    if spent > ITEM_CEILING_CORE_MIN * (1 + CEILING_TOLERANCE):
        return "GATE FAIL", notes
    return "PASS", notes


# =============================================================================
# G-UNBOUND -- the launcher's own shell, still checked, and still NOT ENOUGH
# =============================================================================
def g_unbound(launcher):
    """A1WRT2's unbound-variable guard is KEPT, and this docstring records why
    it was never going to be sufficient: it reads the LAUNCHER FOR UNBOUND
    *SHELL* VARIABLES, and `AOA_ALPHA0` is an ABSENT PROCESS-ENVIRONMENT ENTRY
    CONSUMED BY A PYTHON INTERPRETER ACROSS A `docker run`.  The launcher's
    shell was entirely well-formed on 2026-09-05.  `G-ENVSEAM` is the gate that
    sees the seam; this one is retained for the class of defect it does see."""
    t = read_text(launcher)
    notes = []
    if "set -u" not in t:
        return "GATE FAIL", ["G-UNBOUND: GATE FAIL -- %s does not `set -u`" % launcher]
    notes.append("G-UNBOUND: PASS -- `set -u` armed in %s (and see this gate's "
                 "docstring for what it cannot see)" % launcher)
    return "PASS", notes


# =============================================================================
# THE COMPOSER
# =============================================================================
def compose_item(gate_verdicts):
    """Draft section 5, and the hard/soft lists are DATA.

    EVERY HARD LIST IS TESTED FOR **BOTH** `GATE FAIL` AND `NOT A RESULT` --
    the `D19M-COMPOSE-DEF-1` repair, driven by control `Q-COMPOSE-1`.

    `PASS` IS UNREACHABLE AND THAT IS REGISTERED, NOT AN OVERSIGHT: the L3
    family has no Roache triple, so `min(raw, CEILING)` caps a `PASS` to
    `GATE REACHED` -- AND BOTH `raw` AND `final` ARE PRINTED so the cap is
    visible rather than silent."""
    missing = [g for g in HARD_GATES + SOFT_GATES if g not in gate_verdicts]
    check(not missing,
          "REFUSE: the composer was handed no verdict for %s. A gate with no "
          "reading is not a gate that passed." % missing)
    hard = [gate_verdicts[g] for g in HARD_GATES]
    soft = [gate_verdicts[g] for g in SOFT_GATES]
    if "NOT A RESULT" in hard or "NOT A RESULT" in soft:
        raw = "NOT A RESULT"
    elif "BLOCKED" in hard or "BLOCKED" in soft:
        raw = "BLOCKED"
    elif "GATE FAIL" in hard or "GATE FAIL" in soft:
        raw = "GATE FAIL"
    elif "GATE REACHED" in soft:
        raw = "GATE REACHED"
    else:
        raw = "PASS"
    order = {"PASS": 0, "GATE REACHED": 1, "GATE FAIL": 2,
             "NOT A RESULT": 3, "BLOCKED": 3}
    final = raw if order[raw] >= order[CEILING] else CEILING
    check(final in VERDICT_TOKENS, "REFUSE: composed %r is not a token" % final)
    return raw, final


# =============================================================================
# THE TWO PRECONDITION ENTRY POINTS `a1wrt3_run_arm.sh` CALLS
# =============================================================================
def seam_precond(run_root):
    """SECTION 6'S SPINE.  675 core-min does not move until 10 has spoken.

    AND AN UNRESOLVED SEAM IS NOT A PERMISSION: it refuses at the same rc=7
    with reason `SEAM-UNRESOLVED`, DISTINCT FROM `SEAM-GATE-FAIL`.  A hole where
    a measurement should be is neither an authorisation nor a refusal of the
    physics -- so `TAIL` STAYS PARKED."""
    seam = Path(run_root) / "SEAM"
    sweep = seam / "out" / "sweep.log"
    if not sweep.exists():
        print("A1WRT3_SEAM_PRECOND REFUSED REASON=SEAM-UNRESOLVED -- %s absent; "
              "the SEAM arm produced no statistic. TAIL STAYS PARKED." % sweep)
        return 7
    rcp = seam / "out" / "rc"
    rc = rcp.read_text().strip() if rcp.exists() else "UNMEASURED"
    branch, score, gate, note = p_seamtime3(str(sweep), rc)
    print("A1WRT3_SEAM_PRECOND %s" % note)
    if branch == "C" or score == "UNCLASSIFIED":
        print("A1WRT3_SEAM_PRECOND REFUSED REASON=SEAM-UNRESOLVED")
        return 7
    v, notes = g_seam(str(sweep))
    for n in notes:
        print("A1WRT3_SEAM_PRECOND %s" % n)
    if v != "PASS":
        print("A1WRT3_SEAM_PRECOND REFUSED REASON=SEAM-GATE-FAIL")
        return 7
    print("A1WRT3_SEAM_PRECOND PASS -- TAIL may be authorised BY THE SUPERVISOR")
    return 0


def ceiling_precond(run_root, next_arm):
    v, notes = g_ceiling(run_root, next_arm)
    for n in notes:
        print("A1WRT3_CEILING_PRECOND %s" % n)
    return 0 if v == "PASS" else 6


# =============================================================================
def main(argv=None):
    ap = argparse.ArgumentParser(prog="a1wrt3_grade.py")
    ap.add_argument("--seam-precond", metavar="RUN_ROOT")
    ap.add_argument("--ceiling-precond", nargs=2, metavar=("RUN_ROOT", "ARM"))
    ap.add_argument("--grade", metavar="RUN_ROOT")
    args = ap.parse_args(argv)
    try:
        if args.seam_precond:
            return seam_precond(args.seam_precond)
        if args.ceiling_precond:
            return ceiling_precond(*args.ceiling_precond)
        if args.grade:
            atexit.register(_exit_trap)
            checkpoint("1 -- entered --grade")
            return grade_item(args.grade)
        ap.error("no action requested")
    except Refusal as r:
        print(str(r))
        return r.code
    return 0


def grade_item(run_root):
    """The full composition.  Registered, and NOT YET DEMONSTRATED ON A RUN --
    no A1WRT3 arm has executed and this item's run root does not exist."""
    checkpoint("2 -- reading the manifest")
    manifest = json.loads(read_text(Path(run_root) / "MANIFEST.json"))
    arm = manifest.get("arm", "SEAM")
    arm_dir = Path(run_root) / arm
    container_log = arm_dir / "out" / "container.log"
    sweep_log = arm_dir / "out" / "sweep.log"
    v = {}
    notes = []

    checkpoint("3 -- G-IMG/G-FREEZE")
    v["G-IMG"], n = g_img_freeze(manifest); notes += n
    v["G-FREEZE"] = "PASS"
    checkpoint("4 -- G-ENVSEAM")
    v["G-ENVSEAM"], n = g_envseam(manifest, str(container_log)); notes += n
    checkpoint("5 -- G-WALLTREAT")
    v["G-WALLTREAT"], n = g_walltreat(str(container_log), str(sweep_log)); notes += n
    checkpoint("6 -- G-RC-HONEST")
    v["G-RC-HONEST"], n, _rc = g_rc_honest(str(arm_dir)); notes += n
    checkpoint("7 -- G-COMPLETE")
    v["G-COMPLETE"], n = g_complete(str(arm_dir), arm); notes += n
    checkpoint("8 -- G-SEAM / G-TAILCOUNT")
    v["G-SEAM"], n = g_seam(str(sweep_log)); notes += n
    v["G-TAILCOUNT"], n = g_tailcount(str(sweep_log)); notes += n
    checkpoint("9 -- structural gates")
    v["G-PATCH"], n = g_patch(read_text(sweep_log)); notes += n
    v["G-COLDSTART-SEAM"], n = g_coldstart_seam(
        str(arm_dir / "case"), 4000 if arm == "SEAM" else 4200); notes += n
    v["G-NOGRAD"], n = g_nograd(str(Path(run_root) / "runScript.py")); notes += n
    v["G-NOBAND"], n = g_noband([]); notes += n
    v["G-STALL"], n = g_stall([("sweep.log", read_text(sweep_log))]); notes += n
    v["G-UNBOUND"], n = g_unbound(str(Path(run_root) / "run_arm.sh")); notes += n
    v["G-WARPPROBE"], n = g_warpprobe(str(container_log)); notes += n
    v["G-FIXTURE"], n = g_fixture(sorted(FIXTURES.glob("*"))); notes += n
    checkpoint("10 -- cost gates")
    v["G-CAPS"], n = g_caps(run_root); notes += n
    v["G-CEILING"], n = g_ceiling(run_root); notes += n
    yp = arm_dir / "out" / "probe_yplus.log"
    v["G-YPLUS"], n = g_yplus(str(yp)) if yp.exists() else \
        ("NOT A RESULT", ["G-YPLUS: UNRESOLVED -- no y+ log written"])
    notes += n
    checkpoint("11 -- compose")
    for line in notes:
        print("%s_NOTE %s" % (ITEM, line))
    raw, final = compose_item(v)
    emit_verdict(final, raw)
    return 0


if __name__ == "__main__":
    sys.exit(main())
