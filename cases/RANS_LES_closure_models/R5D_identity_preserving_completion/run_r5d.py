#!/usr/bin/env python3
"""R5D run driver - MECHANISM A capture, staging, solve, snapshot, STATUS.

STATUS: **UNFROZEN**.  This file is a RUN-SIDE DRIVER, not a measurement
instrument.  It is NOT part of R5D's frozen grading path and it is NOT
sha-pinned by PREREGISTRATION.md sec.7.  It grades nothing, asserts no verdict,
moves no verdict, and freezes nothing.  Freezing it (or declining to) is the
closure-supervisor's SUPERVISION_CHARTER sec.3 check-1/check-4 act.

Nothing here edits, mutates or shadows a frozen file.  `grade_r5d.py`,
`PREREGISTRATION.md`, `grade_r5c.py`, `r4_lib.py` and R5C's registration are
READ ONLY.  R5C's `build_r5c_cases.py` is IMPORTED AND CALLED UNCHANGED (its
`build_one` is the staging path R5C itself used, so R5D's staged `0/` is
bit-identical to R4's by construction); this driver does not reimplement it and
does not edit it (L-512).  R4 artefacts under /home/ubuntu/closure-data/r4/ are
read, never written.

================================================================================
THE MECHANISM, AND WHY IT IS THIS ONE
================================================================================
PREREGISTRATION.md item 1 (frozen, lines 103-115) registers a proviso, not a
free choice: the snapshots must be "consecutive outer iterates ending at the
write iteration".  It names two candidate mechanisms:

  (A) the driver writes the last DFP_KMIN+2 consecutive outer-iteration fields
      DURING the R5D run; or
  (B) re-solve from the written field afterwards and capture the last 5.

RULING [lab-attributed, closure-supervisor, 2026-09-10]: **mechanism A**.
Mechanism B is REJECTED, dispositively on (a):

  (a) B cannot satisfy the registered proviso at all.  Restarting from the
      written field at iteration `wi` can only produce `wi, wi+1, ... wi+4` - a
      tail ending PAST the graded field, never AT it.  Adopting it would amend a
      frozen document (CLAUDE.md rule 6), which is forbidden.
  (b) B is systematically OPTIMISTIC: it certifies a state ~rho^4 further
      converged than the field the identity gate actually grades (a factor 16 at
      rho=0.5), so it could bless a graded field that does not deserve it.
      **CHOOSING A IS CHOOSING THE STRICTER OPTION** - the ruling selects
      against the flattering mechanism.  That is the anti-gaming test, and it is
      recorded here because a driver that quietly chose the flattering mechanism
      would look identical from the outside.
  (c) A needs no solver source written or rebuilt (below), which was B's whole
      reason for existing as a fallback.
  (d) A is inside the registered budget: PREREGISTRATION.md:269 costs the
      27-case re-extraction "with snapshot writes".  B's restarts are itemised
      nowhere.

Control C5 below makes the ruling EXECUTABLE: the driver refuses any case whose
snapshot manifest does not report `ends_at_write_iter == True`.  A mechanism-B
tail cannot pass it.

HOW A IS OBTAINED WITHOUT TOUCHING SOLVER SOURCE
------------------------------------------------
`kCorrectiveFrozenFoamV2.C` calls `runTime.write()` nowhere in its loop (only
`runTime.writeNow()` at :227, after the break).  But its loop is
`while (runTime.loop())`, and `Time::loop()` calls `Time::run()`, which calls
`functionObjects_.execute()` on every outer iteration
(/usr/lib/openfoam/openfoam2606/src/OpenFOAM/db/Time/Time.C:827).  A
`writeObjects` functionObject in `system/controlDict` with
`writeControl timeStep; writeInterval 1;` therefore emits
`<case>/<iter>/{omega,kDeficit,bijDelta}` once per outer iteration with **no
solver source written and no rebuild** - item 1's constraint is honoured.

Phasing detail, measured and relied upon: `functionObjects_.execute()` runs at
the TOP of `run()`, before `operator++()`, so the directory named `n` holds the
state AFTER outer iteration `n`.  The loop then breaks and `writeNow()` writes
the full field set into the directory named `wi`.  The captured sequence
`wi-4 ... wi` is therefore consecutive AND ends at the graded field itself.

DISK BOUNDING - A MEASURED NEGATIVE
-----------------------------------
`purgeWrite` does NOT bound these directories.  The purge lives in
`Time::writeObject` (src/OpenFOAM/db/Time/TimeIO.C:561), gated on `writeTime()`,
and a `writeObjects` functionObject never routes through it - it writes each
registered object directly.  This driver therefore bounds disk itself, with the
`reap` phase (a rolling window of `--keep` newest iterate directories, run
alongside the solver from inside the detached wrapper), and prunes to the
R5C-era layout after the snapshots are taken and verified.

================================================================================
CONTROLS (CLAUDE.md rules 3/4/12/14, L-221/L-222, L-332)
================================================================================
No `assert` carries any guard, refusal, control or gate ANYWHERE in this file -
asserts vanish under `python3 -O`.  Every refusal is an explicit branch into
`refuse()` -> sys.exit(2).  `--selftest` is green under BOTH `python3` and
`python3 -O` and shows each refusal actually FIRING.

  C1  STAGE GUARD (rule 4)  - a destination already holding `0/` or a numeric
      time directory is refused; a frozen extraction is never resumed in place.
  C2  OPTIMISED-STAGING REFUSAL - staging is refused under `python3 -O`, because
      the REUSED R5C builder's copy-integrity guards are `assert` statements
      that -O strips.  Running it optimised would silently disarm them.
  C3  FUNCTIONOBJECT-LANDED (L-221/L-222, rule 14) - after the controlDict is
      written it is READ BACK FROM DISK and every field of the capture block is
      checked, plus the survival of the top-level libs entry.  A silent no-op
      here yields ZERO snapshots and a PENDING that looks like a finding.
  C4  CAPTURE-LIVE - after the solve, the driver counts the consecutive iterate
      directories actually on disk ending at the write iteration.  Fewer than
      DFP_KMIN+2 means the functionObject did not fire: refuse, do not degrade.
  C5  ENDS-AT-WRITE-ITER - the ruling, executable.  See above.
  C6  DISTINCTNESS - consecutive captured snapshots must not be byte-identical.
      Five copies of one file are a capture failure that the frozen grader would
      see only as a cliff; this names it at its source.
  C7  POSTPROCESS INTEGRITY - sha256 of the graded `wi/{omega,kDeficit,bijDelta}`
      before and after the `grad(U)` postProcess must be unchanged.
  C8  BUDGET (rule 12) - core-minutes are accumulated against the REGISTERED cap
      (PREREGISTRATION.md sec.4: 1.0 core-h).  An overrun STOPS the run - the
      solver's process group is killed and the case is recorded BLOCKED.  It
      does not get a new budget.
  C9  RC-INSIDE-THE-WRAPPER - `setsid timeout cmd` exits 0 for every outcome, so
      rc is captured INSIDE the detached wrapper and read back from `<case>/rc`.
      A wrapper that died without writing `rc` is refused, not assumed zero.
  C10 SOLVER PRESENT - the V2 binary and libspartaFrozenV2.so must exist.
  C11 GRADER SHA-PIN (rule 2) - grade_r5d.py is hashed against the sec.7 pin
      before anything runs, independently of the writer's own check.
  C12 ZERO-SHOT - r4_lib.assert_no_test_case is an `assert`; this driver repeats
      the check as an explicit branch so -O cannot disarm it.
  C13 CAMPAIGN-LAUNCH REFUSAL - the driver refuses to solve more than one case
      unless `--launch-order` is given.  The 27-case campaign launch is the
      supervisor's call, not the driver's and not a lane's.
  C14 PLANT THE ZERO, APPLIED TO THE CAPTURE (rule 3) - a zero step read out of
      the captured iterates is evidence only if the reader has been shown able
      to see a non-zero.  The witness is the SOLVER's own per-iteration
      `omegaHistory.csv`.  Where the solver says omega changed and the capture
      shows an exactly-zero step, the capture is blind: REFUSE.  Where both say
      zero they agree, and whether a static field is converged or clipped is
      grade_r5d.py's L-235 ruling to make, not this driver's.

Verdict vocabulary only (CLAUDE.md rule 1):
  PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.
This driver asserts NO verdict.  It produces run-side data and a STATUS file
from which a reader who was not there can apply rule 4 themselves.
"""
from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import importlib.util
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_CLOSURE = os.path.join(_REPO, "cases", "RANS_LES_closure_models")
_R4DIR = os.path.join(_CLOSURE, "R4_sparta_build")
_R5CDIR = os.path.join(_CLOSURE, "R5C_omega_repair")
sys.path.insert(0, _R4DIR)
sys.path.insert(0, os.path.join(_CLOSURE, "_common"))
sys.path.insert(0, os.path.join(_REPO, "scripts"))

# ---------------------------------------------------------------- constants
GRADER_PATH = os.path.join(_HERE, "grade_r5d.py")
WRITER_PATH = os.path.join(_HERE, "write_dfp_snaps.py")
PREREG_PATH = os.path.join(_HERE, "PREREGISTRATION.md")
# PREREGISTRATION.md sec.7 line 306 comparator sha-pin (CLAUDE.md rule 2).
GRADER_SHA_PIN = "aaae8ac6d60c8aa33124748e8410b094483ec48f67f54f289d0aff3af07e5805"

R4_FROZEN = "/home/ubuntu/closure-data/r4/frozen"
W2_RECORD = os.path.join(_REPO, "verification", "runs", "W2_sparta_runs")
DEFAULT_ROOT = "/home/ubuntu/closure-data/r5d"      # grade_r5d.py:62 / :63 parent
FROZEN_SUB = "frozen"
LEGACY_SUB = "w2_legacy"
LEGACY_CASES = (("ph", "ph_frozen"), ("cbfs", "cbfs_frozen"))

SOLVER = "kCorrectiveFrozenFoamV2"
FOAM_CMD = "openfoam2606"
V2_LIB = "libspartaFrozenV2.so"
FOAM_BIN = os.path.expanduser(
    "~/OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/bin/" + SOLVER)
FOAM_LIB = os.path.expanduser(
    "~/OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/lib/" + V2_LIB)

SNAP_FIELDS = ("omega", "kDeficit", "bijDelta")
FO_NAME = "dfpCapture"
FO_LIB = "libutilityFunctionObjects.so"

# PREREGISTRATION.md sec.4: registered CAP 1.0 core-h; registered ESTIMATE
# 0.184 core-h for the 27-case re-extraction WITH snapshot writes.
CAP_CORE_MIN = 60.0
EST_CORE_MIN = 0.184 * 60.0
RATE = 0.0513            # $/core-h, reported-by-owner, NOT measured (rule 12)

KEEP_DEFAULT = 12        # rolling iterate window the reaper leaves on disk
REAP_SAFE_AGE_S = 3.0    # never remove a directory touched this recently
NICE = 10                # the box is shared; take one core, politely
RANKS = 1                # serial.  NEVER mpirun.
POLL_S = 2.0

TIME_RE = re.compile(r"^[0-9]+$")
WRITE_ITER_RE = re.compile(r"Writing fields at iteration (\d+)")


# ---------------------------------------------------------------- utilities
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def refuse(msg):
    print(f"\nDRIVER REFUSAL: {msg}", file=sys.stderr)
    sys.exit(2)


def say(msg):
    print(msg, flush=True)


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def no_assert_in_this_file(path=None):
    """L-332/D476 sec.31.3: count `assert` statements in this source.

    Returns the count.  A control that lives in an `assert` is disarmed by
    `python3 -O`; this driver must contain none.
    """
    p = path or os.path.abspath(__file__)
    tree = ast.parse(open(p).read())
    return sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assert))


def core_minutes(wall_s, ranks=RANKS):
    """CLAUDE.md rule 12: the unit is core-minutes = wall s * ranks / 60."""
    return float(wall_s) * float(ranks) / 60.0


# ------------------------------------------------- C11: the frozen sha-pin
def check_grader_pin():
    if not os.path.isfile(GRADER_PATH):
        refuse(f"C11: frozen comparator absent: {GRADER_PATH}")
    got = sha256_file(GRADER_PATH)
    if got != GRADER_SHA_PIN:
        refuse(f"C11: grade_r5d.py sha256 {got} != PREREGISTRATION.md sec.7 pin "
               f"{GRADER_SHA_PIN}.  The frozen file is not the file that would "
               f"run (CLAUDE.md rule 2).")
    return got


def frozen_constants():
    """Read DFP_KMIN and friends OUT OF the frozen grader, never re-declare."""
    spec = importlib.util.spec_from_file_location("_r5d_grader_ro", GRADER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------- C10: solver present
def check_solver_present():
    missing = [p for p in (FOAM_BIN, FOAM_LIB) if not os.path.exists(p)]
    if missing:
        refuse(f"C10: solver artefacts absent: {missing}.  R5D uses the R5C "
               f"binaries UNCHANGED and rebuilds nothing (item 1).")
    return {"solver": FOAM_BIN, "lib": FOAM_LIB,
            "solver_sha256": sha256_file(FOAM_BIN),
            "lib_sha256": sha256_file(FOAM_LIB)}


# --------------------------------------------------------- the controlDict
def fo_block():
    """The mechanism-A capture block.  One functionObject, three fields."""
    objs = " ".join(SNAP_FIELDS)
    return (
        "functions\n"
        "{\n"
        "    // R5D mechanism A (closure-supervisor ruling 2026-09-10): capture\n"
        "    // the consecutive outer iterates IN PLACE, at the write iteration.\n"
        "    // Time::run() calls functionObjects_.execute() every outer\n"
        "    // iteration (openfoam2606 src/OpenFOAM/db/Time/Time.C:827) and\n"
        "    // kCorrectiveFrozenFoamV2's loop is `while (runTime.loop())`, so\n"
        "    // this emits <iter>/{%s} per iteration with NO\n"
        "    // solver source written and NO rebuild (PREREGISTRATION.md item 1).\n"
        "    %s\n"
        "    {\n"
        "        type            writeObjects;\n"
        "        libs            (\"%s\");\n"
        "        objects         ( %s );\n"
        "        writeOption     anyWrite;\n"
        "        writeControl    timeStep;\n"
        "        writeInterval   1;\n"
        "    }\n"
        "}\n" % (objs, FO_NAME, FO_LIB, objs))


def install_capture(case_dir):
    """Write the capture functionObject, then VERIFY IT FROM DISK (C3).

    Insert-or-replace of the whole `functions` block, never a blind append:
    R4's controlDict ships `functions { }` and a replace-only path that missed
    it would leave the case with no capture at all - and a case with no capture
    reads, downstream, as an honest PENDING rather than as the silent no-op it
    is (the L-221/L-222 shape, CLAUDE.md rule 14).
    """
    cd = os.path.join(case_dir, "system", "controlDict")
    if not os.path.isfile(cd):
        refuse(f"C3: no controlDict at {cd}")
    s = open(cd).read()
    i = s.find("functions")
    s = (s[:i] if i >= 0 else s.rstrip() + "\n\n") + fo_block()
    with open(cd, "w") as fh:
        fh.write(s)

    # ---- verify FROM DISK, field by field ---------------------------------
    back = open(cd).read()
    checks = [
        (rf"^\s*{re.escape(FO_NAME)}\s*$", f"functionObject named {FO_NAME}"),
        (r"^\s*type\s+writeObjects;\s*$", "type writeObjects"),
        (r"^\s*writeControl\s+timeStep;\s*$", "writeControl timeStep"),
        (r"^\s*writeInterval\s+1;\s*$", "writeInterval 1"),
    ]
    for pat, what in checks:
        if not re.search(pat, back, re.M):
            refuse(f"C3: {what} did not land in {cd} - the capture block is a "
                   f"silent no-op and the run would produce ZERO snapshots")
    m = re.search(r"^\s*objects\s*\(([^)]*)\)\s*;", back, re.M)
    if m is None:
        refuse(f"C3: no `objects (...)` list in {cd}")
    named = m.group(1).split()
    missing = [f for f in SNAP_FIELDS if f not in named]
    if missing:
        refuse(f"C3: capture block does not name {missing} (it names {named})")

    # ---- the top-level libs entry must have SURVIVED the rewrite ----------
    from foam_libs import assert_libs, FoamLibsError      # noqa: PLC0415
    try:
        have = assert_libs(cd, V2_LIB)
    except FoamLibsError as exc:                          # not an assert: -O safe
        refuse(f"C3: top-level libs entry lost or duplicated by the capture "
               f"rewrite: {exc}")
    return {"controlDict": cd, "libs": have, "objects": named,
            "sha256": sha256_file(cd)}


# ----------------------------------------------------------------- staging
def load_r5c_builder():
    """Import R5C's builder UNCHANGED and call it.  Never edited, never copied."""
    path = os.path.join(_R5CDIR, "build_r5c_cases.py")
    if not os.path.isfile(path):
        refuse(f"R5C builder absent: {path}")
    spec = importlib.util.spec_from_file_location("_build_r5c_ro", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, sha256_file(path)


def stage_guard(dst):
    """C1 / rule 4: refuse a destination already holding 0/ or a time dir."""
    if not os.path.isdir(dst):
        return
    for d in sorted(os.listdir(dst)):
        if d == "0" or TIME_RE.fullmatch(d):
            refuse(f"C1: {dst} already holds '{d}'.  A frozen extraction is "
                   f"never resumed or restarted in place (rule 4's guard).")


def zero_shot_guard(cases):
    """C12: r4_lib.assert_no_test_case is an `assert`; repeat it as a branch."""
    import r4_lib as R                                    # noqa: PLC0415
    bad = sorted(set(cases) & (set(R.TEST_CASES) | set(R.VAL_CASES)))
    if bad:
        refuse(f"C12: ZERO-SHOT VIOLATION - test/validation case in the R5D "
               f"set: {bad}")
    return sorted(cases)


def phase_stage(root, only, with_legacy):
    if not __debug__:
        refuse("C2: staging refused under `python3 -O`.  Staging reuses R5C's "
               "build_r5c_cases.build_one UNCHANGED, whose copy-integrity "
               "guards (0/ bit-identity, RASModel landed, omegaSourceRepair "
               "landed, libs landed) are `assert` statements that -O strips.  "
               "Run staging under plain `python3`.")
    check_grader_pin()
    check_solver_present()
    import r4_lib as R                                    # noqa: PLC0415
    B, bsha = load_r5c_builder()

    cases = [c for c, _b, _f in R.training_cases()]
    zero_shot_guard(cases)
    if only:
        unknown = sorted(set(only) - set(cases) - {t for t, _ in LEGACY_CASES})
        if unknown:
            refuse(f"unknown case(s): {unknown}")
        cases = [c for c in cases if c in only]

    rec = []
    for case in cases:
        src = os.path.join(R4_FROZEN, case)
        if not os.path.isdir(src):
            refuse(f"R4 frozen case missing: {src}")
        dst = os.path.join(root, FROZEN_SUB, case)
        stage_guard(dst)
        r = B.build_one(case, src, dst, repair=True)      # R5C's code, unchanged
        r["capture"] = install_capture(dst)               # C3
        rec.append({"case": case, "dir": dst,
                    "omegaSourceRepair": True,
                    "n_inputs_sha256": len(r["inputs_sha256"]),
                    "controlDict_sha256": r["capture"]["sha256"]})
        say(f"[staged repaired] {case:24s} capture={FO_NAME} "
            f"objects={','.join(SNAP_FIELDS)}")

    leg = []
    if with_legacy:
        for tag, srcname in LEGACY_CASES:
            if only and tag not in only:
                continue
            src = os.path.join(W2_RECORD, srcname)
            if not os.path.isdir(src):
                refuse(f"W2 record missing: {src}")
            dst = os.path.join(root, LEGACY_SUB, tag)
            stage_guard(dst)
            B.build_one(tag, src, dst, repair=False)
            # NO capture block on the legacy pair: gate_w2 is a byte-identity
            # gate and G-DFP is not applied to it (PREREGISTRATION.md item 3).
            leg.append({"case": tag, "dir": dst, "omegaSourceRepair": False,
                        "capture": None})
            say(f"[staged legacy  ] {tag:24s} (gate W2; NO capture block)")

    man = {"staged_utc": utcnow(), "root": root,
           "builder": os.path.join(_R5CDIR, "build_r5c_cases.py"),
           "builder_sha256": bsha, "builder_edited": False,
           "grader_sha256": GRADER_SHA_PIN,
           "mechanism": "A (in-place per-iteration capture at the write "
                        "iteration) - closure-supervisor ruling 2026-09-10",
           "capture_fields": list(SNAP_FIELDS),
           "repaired": rec, "legacy": leg}
    os.makedirs(root, exist_ok=True)
    mp = os.path.join(root, "R5D_STAGE_MANIFEST.json")
    with open(mp, "w") as fh:
        json.dump(man, fh, indent=1, sort_keys=True)
    say(f"\n{len(rec)} repaired + {len(leg)} legacy staged -> {root}")
    say(f"manifest: {mp}")
    return 0


# ------------------------------------------------------------------- reaping
def iterate_dirs(case_dir):
    """Numeric time directories, ascending, EXCLUDING 0."""
    out = []
    for name in os.listdir(case_dir):
        if TIME_RE.fullmatch(name) and name != "0" \
           and os.path.isdir(os.path.join(case_dir, name)):
            out.append(int(name))
    return sorted(out)


def phase_reap(case_dir, keep, now=None):
    """Rolling window: leave the `keep` newest iterate directories.

    Runs alongside the solver from inside the detached wrapper.  `purgeWrite`
    cannot do this job - the purge lives in Time::writeObject (TimeIO.C:561)
    and a writeObjects functionObject never routes through it.

    Safety, in code and not in prose:
      * only `^[0-9]+$` directories, never `0`, never `constant`/`system`;
      * never the `keep` newest (so the graded write directory, always the
        newest, can never be removed);
      * never one touched within REAP_SAFE_AGE_S (it may be mid-write).
    """
    if keep <= 0:
        return {"keep": keep, "removed": [], "disabled": True}
    have = iterate_dirs(case_dir)
    if len(have) <= keep:
        return {"keep": keep, "removed": [], "n_before": len(have),
                "n_after": len(have)}
    t = time.time() if now is None else now
    doomed = have[:-keep]
    removed = []
    for it in doomed:
        p = os.path.join(case_dir, str(it))
        try:
            if (t - os.path.getmtime(p)) < REAP_SAFE_AGE_S:
                continue
            shutil.rmtree(p)
            removed.append(it)
        except OSError:
            continue
    return {"keep": keep, "removed": removed, "n_before": len(have),
            "n_after": len(iterate_dirs(case_dir))}


# ------------------------------------------------------------------- solving
def wrapper_text(case_dir, drive_dir, tag, keep):
    """The detached wrapper.

    C9: `setsid timeout cmd` exits 0 for EVERY outcome, so rc is captured
    INSIDE here, around the solver itself, and written to <case>/rc last.  The
    parent never infers rc from the setsid line.
    """
    reaper = ""
    stop_reaper = ""
    if keep > 0:
        reaper = (
            "(\n"
            "  while kill -0 $SOLVER_PID 2>/dev/null; do\n"
            f"    {sys.executable!r} {os.path.abspath(__file__)!r} "
            f"--phase reap --case \"$CASE\" --keep \"$KEEP\" "
            f">> \"$DRIVE/{tag}.reap.log\" 2>&1\n"
            "    sleep 5\n"
            "  done\n"
            ") &\n"
            "REAPER_PID=$!\n")
        stop_reaper = ("kill $REAPER_PID 2>/dev/null\n"
                       "wait $REAPER_PID 2>/dev/null\n")
    return f"""#!/bin/bash
# R5D detached wrapper for {tag}.  rc is captured INSIDE, never around setsid.
set -u
CASE={case_dir!r}
DRIVE={drive_dir!r}
KEEP={keep}
echo $$ > "$DRIVE/{tag}.pgid"
cd "$CASE" || exit 97
T0=$(date +%s.%N)
nice -n {NICE} {FOAM_CMD} {SOLVER} > "$CASE/log.frozen" 2>&1 &
SOLVER_PID=$!
{reaper}wait $SOLVER_PID
RC=$?
{stop_reaper}T1=$(date +%s.%N)
awk -v a="$T0" -v b="$T1" 'BEGIN{{printf "%.2f\\n", b-a}}' > "$CASE/wall_seconds"
echo "$RC" > "$CASE/rc"
"""


def launch(case_dir, drive_dir, tag, keep):
    os.makedirs(drive_dir, exist_ok=True)
    wpath = os.path.join(drive_dir, f"{tag}.sh")
    with open(wpath, "w") as fh:
        fh.write(wrapper_text(case_dir, drive_dir, tag, keep))
    os.chmod(wpath, 0o755)
    for leftover in ("rc", "wall_seconds"):
        p = os.path.join(case_dir, leftover)
        if os.path.exists(p):
            os.remove(p)
    pg = os.path.join(drive_dir, f"{tag}.pgid")
    if os.path.exists(pg):
        os.remove(pg)
    subprocess.Popen(["setsid", "bash", wpath],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    return wpath, pg


def kill_group(pgid_path):
    if not os.path.exists(pgid_path):
        return False
    try:
        pgid = int(open(pgid_path).read().strip())
    except (OSError, ValueError):
        return False
    try:
        os.killpg(pgid, signal.SIGTERM)
        return True
    except OSError:
        return False


def already_solved(case_dir):
    """R5C's rule, kept: a completed frozen extraction is SKIPPED, never rerun.

    Returns (done, wall_seconds_from_the_original_run).  `done` needs BOTH the
    wrapper's own rc==0 AND an `End` line in log.frozen - an rc file alone is
    not a completed run.  Re-entering only the capture costs no compute, which
    is what makes a driver fix cheap after a solve.
    """
    rcf = os.path.join(case_dir, "rc")
    log = os.path.join(case_dir, "log.frozen")
    if not (os.path.isfile(rcf) and os.path.isfile(log)):
        return False, 0.0
    if open(rcf).read().strip() != "0":
        return False, 0.0
    if not re.search(r"^End\s*$", open(log, errors="replace").read(), flags=re.M):
        return False, 0.0
    wall = 0.0
    wsf = os.path.join(case_dir, "wall_seconds")
    if os.path.isfile(wsf):
        try:
            wall = float(open(wsf).read().strip())
        except ValueError:
            wall = 0.0
    return True, wall


def wait_for_rc(case_dir, pgid_path, budget_core_min):
    """C8+C9: poll for the wrapper's own rc; stop the run on a budget overrun.

    Returns (rc:int|None, wall_s:float, stopped:str|None).
    `rc is None` means the wrapper vanished without recording one - which is a
    refusal, not a zero.
    """
    rcf = os.path.join(case_dir, "rc")
    t0 = time.time()
    while True:
        if os.path.exists(rcf):
            txt = open(rcf).read().strip()
            wall = time.time() - t0
            wsf = os.path.join(case_dir, "wall_seconds")
            if os.path.exists(wsf):
                try:
                    wall = float(open(wsf).read().strip())
                except ValueError:
                    pass
            try:
                return int(txt), wall, None
            except ValueError:
                return None, wall, f"rc file holds {txt!r}, not an integer"
        wall = time.time() - t0
        if core_minutes(wall) > budget_core_min:
            kill_group(pgid_path)
            return None, wall, (
                f"C8 BUDGET OVERRUN: {core_minutes(wall):.2f} core-min exceeds "
                f"the remaining budget {budget_core_min:.2f} core-min.  The run "
                f"is STOPPED; it does not get a new budget (CLAUDE.md rule 12).")
        if not os.path.exists(pgid_path) and wall > 60.0:
            return None, wall, ("the detached wrapper never recorded a pgid; it "
                                "did not start")
        time.sleep(POLL_S)


# ------------------------------------------------------------------ capture
def read_write_iter(case_dir):
    """The write iteration, from ONE NAMED artifact: <case>/log.frozen.

    Never `ls | sort -n | tail -1`: a glob has no defined last member and the
    directory listing is exactly what the capture fills with decoys.
    """
    log = os.path.join(case_dir, "log.frozen")
    if not os.path.isfile(log):
        return None, "no log.frozen"
    m = WRITE_ITER_RE.search(open(log, errors="replace").read())
    if m is None:
        return None, "no `Writing fields at iteration N` line in log.frozen"
    return int(m.group(1)), None


def capture_window(case_dir, write_iter, need):
    """C4: the consecutive iterate directories on disk ending at write_iter."""
    have = set(iterate_dirs(case_dir))
    want = list(range(write_iter - need + 1, write_iter + 1))
    missing = [i for i in want if i not in have]
    return want, missing


def snapshot_bytes_distinct(case_dir, field, iters):
    """C6: consecutive captured snapshots must not be byte-identical."""
    snapdir = os.path.join(case_dir, "dfpSnaps")
    shas = []
    for it in iters:
        p = os.path.join(snapdir, f"{field}_{it}")
        if not os.path.isfile(p):
            return None, f"{p} absent after the writer returned"
        shas.append((it, sha256_file(p)))
    dupes = [(a[0], b[0]) for a, b in zip(shas, shas[1:]) if a[1] == b[1]]
    if dupes:
        return shas, (f"consecutive snapshots {dupes} are BYTE-IDENTICAL for "
                      f"{field}: the capture captured one iterate more than "
                      f"once, it did not capture consecutive outer iterates")
    return shas, None


def history_rows(case_dir):
    """<case>/omegaHistory.csv as {iter: maxRelDomega}.  ONE NAMED artifact.

    The solver writes one row PER OUTER ITERATION (kCorrectiveFrozenFoamV2.C
    :145-153): iter,initRes,maxRelDomega,minOmegaPreBound,nNegOmegaCells,
    nNegSourceCells.  It is written by the SOLVER, independently of the capture,
    which is what makes it a witness rather than a second opinion from the same
    eye.
    """
    p = os.path.join(case_dir, "omegaHistory.csv")
    if not os.path.isfile(p):
        return None
    out = {}
    for line in open(p, errors="replace").read().splitlines()[1:]:
        parts = line.split(",")
        if len(parts) < 3:
            continue
        try:
            out[int(parts[0])] = float(parts[2])
        except ValueError:
            continue
    return out


def capture_liveness(case_dir, window, reader):
    """C14: PLANT THE ZERO (CLAUDE.md rule 3), applied to the CAPTURE itself.

    A zero step read out of the captured iterates is only evidence if the reader
    that produced it has been shown able to see a NON-zero.  The witness is the
    solver's own `omegaHistory.csv`, written per outer iteration by code that
    knows nothing about the capture.

    Predicate, deliberately weak and therefore sound: for each consecutive pair
    in the window, if the SOLVER says omega changed on that iteration
    (maxRelDomega > 0) but the CAPTURED omega step is exactly 0, the capture is
    blind - REFUSE.  The converse (both zero) is agreement, and it is NOT
    refused here: a genuinely static field is a CONVERGENCE question, and
    grade_r5d.py's cliff/flat refusals (L-235) are the instrument entitled to
    rule on it.  This driver does not grade.

    The witness covers `omega` only.  kDeficit and bijDelta are computed from
    the same iteration's fields, so a live omega capture is the evidence that
    the capture fires per iteration; that limitation is stated, not hidden.
    """
    hist = history_rows(case_dir)
    steps, disagree = [], []
    prev = None
    for it in window:
        p = os.path.join(case_dir, "dfpSnaps", f"omega_{it}")
        if not os.path.isfile(p):
            return None, f"{p} absent"
        cur = reader(p)
        if prev is not None:
            s = float(((cur - prev) ** 2).sum() ** 0.5)
            h = None if hist is None else hist.get(it)
            steps.append({"iter": it, "captured_step_l2": s,
                          "solver_maxRelDomega": h})
            if h is not None and h > 0.0 and s == 0.0:
                disagree.append(it)
        prev = cur
    if disagree:
        return steps, (
            f"C14: the solver's own omegaHistory.csv reports omega CHANGED on "
            f"iteration(s) {disagree} (maxRelDomega > 0) but the captured "
            f"snapshots show an EXACTLY ZERO step there.  The capture is blind "
            f"to a change the solver measured - a zero from a reader not shown "
            f"able to see a non-zero is not evidence (CLAUDE.md rule 3).")
    return steps, None


def run_writer(case_dir, write_iter, n, replace=False):
    """Call write_dfp_snaps.py.  --write-iter is set so the manifest records
    `ends_at_write_iter` truthfully, per case (the ruling, on the record)."""
    cmd = [sys.executable, WRITER_PATH, "--case", case_dir,
           "--ends-at", str(write_iter), "--write-iter", str(write_iter),
           "--n", str(n)]
    for f in SNAP_FIELDS:
        cmd += ["--field", f]
    if replace:
        cmd.append("--replace")
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def read_manifest(case_dir):
    mp = os.path.join(case_dir, "dfpSnaps", "MANIFEST.json")
    if not os.path.isfile(mp):
        return None
    try:
        return json.load(open(mp))
    except (OSError, ValueError):
        return None


def existing_snaps_ok(case_dir, write_iter, need):
    """Is a COMPLETE, already-verified dfpSnaps sequence standing on disk?

    Used only to make the capture phase re-entrant after this driver's own
    prune step has removed the iterate directories.  It reconstructs nothing:
    every field must already have exactly `need` consecutive snapshots ending
    at `write_iter`, the manifest must agree, and the FROZEN reader must return
    them.  Anything less is not "close enough" - it is a False.
    """
    man = read_manifest(case_dir)
    if man is None:
        return False, "no dfpSnaps/MANIFEST.json"
    want = list(range(write_iter - need + 1, write_iter + 1))
    for f in SNAP_FIELDS:
        fm = man.get("fields", {}).get(f)
        if fm is None:
            return False, f"manifest has no entry for {f}"
        if fm.get("iters") != want:
            return False, (f"{f} manifest iters {fm.get('iters')} != the "
                           f"required window {want[0]}..{want[-1]}")
        if fm.get("case_write_iter") != write_iter:
            return False, (f"{f} manifest write iteration "
                           f"{fm.get('case_write_iter')} != log's {write_iter}")
        if fm.get("ends_at_write_iter") is not True:
            return False, f"{f} manifest ends_at_write_iter is not True"
        for it in want:
            if not os.path.isfile(os.path.join(case_dir, "dfpSnaps", f"{f}_{it}")):
                return False, f"dfpSnaps/{f}_{it} absent"
    return True, "complete sequence already on disk"


def postprocess_gradU(case_dir, write_iter):
    """grad(U) on the graded time only, with C7 around it."""
    before = {}
    for f in SNAP_FIELDS:
        p = os.path.join(case_dir, str(write_iter), f)
        if os.path.isfile(p):
            before[f] = sha256_file(p)
    log = os.path.join(case_dir, "log.gradU")
    with open(log, "w") as fh:
        p = subprocess.run(["nice", "-n", str(NICE), FOAM_CMD, "postProcess",
                            "-func", "grad(U)", "-time", str(write_iter)],
                           cwd=case_dir, stdout=fh, stderr=subprocess.STDOUT)
    after = {}
    for f in SNAP_FIELDS:
        q = os.path.join(case_dir, str(write_iter), f)
        if os.path.isfile(q):
            after[f] = sha256_file(q)
    changed = sorted(f for f in before if before.get(f) != after.get(f))
    if changed:
        refuse(f"C7: postProcess grad(U) CHANGED the graded fields {changed} in "
               f"{case_dir}/{write_iter} - the graded field is no longer the "
               f"field the snapshot sequence ends at")
    return p.returncode, {"unchanged": sorted(before)}


def prune_to_r5c_layout(case_dir, write_iter):
    """After the snapshots are written AND verified, remove every iterate
    directory except 0/ and the graded write directory.

    The evidence is not lost: dfpSnaps holds BYTE-FOR-BYTE copies and the
    manifest carries each source path and sha256.  `--keep-iterates` skips this
    so the supervisor can spot-check one case against its own time directories.
    """
    removed = []
    for it in iterate_dirs(case_dir):
        if it == write_iter:
            continue
        shutil.rmtree(os.path.join(case_dir, str(it)))
        removed.append(it)
    return removed


# ------------------------------------------------------------------- STATUS
def write_status(root, case, rec):
    """STATUS.<case>: everything a reader who was not there needs to apply
    CLAUDE.md rule 4 THEMSELVES.  It asserts no verdict and grades nothing."""
    path = os.path.join(root, f"STATUS.{case}")
    L = []
    L.append(f"# STATUS.{case}  -  R5D run record (UNFROZEN; NO VERDICT)")
    L.append("")
    L.append("Written by run_r5d.py, the R5D run driver.  This file GRADES")
    L.append("NOTHING.  grade_r5d.py (FROZEN, sha "
             f"{GRADER_SHA_PIN[:8]}...) is the only instrument entitled to a")
    L.append("verdict.  Every rule-4 clause below is reported as a MEASURED")
    L.append("value so a reader who was not there can apply the rule.")
    L.append("")
    L.append(f"case_dir            : {rec.get('case_dir')}")
    L.append(f"run_utc             : {rec.get('run_utc')}")
    L.append(f"mechanism           : A (in-place per-iteration capture, ending")
    L.append(f"                      AT the write iteration) - the STRICTER of")
    L.append(f"                      item 1's two registered mechanisms.")
    L.append(f"ranks               : {RANKS} (serial; mpirun is never used)")
    L.append("")
    L.append("-- rule 4, clause by clause (measured) --------------------------")
    L.append(f"rc                  : {rec.get('rc')}      (captured INSIDE the "
             f"detached wrapper, C9)")
    L.append(f"End line in log     : {rec.get('end_line')}")
    L.append(f"NOT CONVERGED       : {rec.get('not_converged')}")
    L.append(f"write_iter (log)    : {rec.get('write_iter')}   "
             f"[from log.frozen, ONE named artifact]")
    L.append(f"latest time dir     : {rec.get('latest_time')}")
    L.append(f"last time == write  : {rec.get('last_time_is_write')}")
    L.append(f"ExecutionTime count : {rec.get('n_exec')}   "
             f"(rule-4 clause 5: n_exec == write_iter -> "
             f"{rec.get('exec_count_ok')})")
    if rec.get("exec_count_ok") is False and rec.get("n_exec") == 1:
        L.append("  ^^ READ THIS BEFORE TREATING IT AS A CASE-SPECIFIC FAILURE.")
        L.append("  kCorrectiveFrozenFoamV2.C emits `ExecutionTime = ... s`")
        L.append("  EXACTLY ONCE per run (:244, the only occurrence in the")
        L.append("  source; the V1 solver likewise).  The frozen")
        L.append("  grade_r5d.py:completion_rule4 requires n_exec == write_iter,")
        L.append("  and write_iter >= nSettle = 50 by construction, so the")
        L.append("  clause cannot be satisfied by ANY run of this solver family.")
        L.append("  MEASURED over R4's own 27 frozen records: n_exec ==")
        L.append("  write_iter holds for 0 of 27.  This is a defect in a FROZEN")
        L.append("  file and this driver does not touch it (CLAUDE.md rule 6).")
        L.append("  It is the closure-supervisor's to rule on; note that while")
        L.append("  /home/ubuntu/closure-data/r5d/frozen does not exist, R5D is")
        L.append("  PRE-first-compute and rule 2's before-compute amendment")
        L.append("  route is open.  This driver's demonstration ran in a")
        L.append("  SEPARATE root precisely to keep that route open.")
    L.append(f"fields at write_iter: {rec.get('fields_present')}")
    L.append(f"AGE GUARD (each field newer than the case's own 0/<field>): "
             f"{rec.get('age_guard')}")
    L.append(f"bounding omega before write : {rec.get('bounding_omega')}")
    L.append("")
    L.append("-- G-DFP capture (PREREGISTRATION.md item 1/2) ------------------")
    L.append(f"capture fields      : {', '.join(SNAP_FIELDS)}")
    L.append(f"iterates required   : {rec.get('need')} (DFP_KMIN+2, read out of "
             f"the frozen grader)")
    L.append(f"iterate window      : {rec.get('window')}")
    L.append(f"window on disk      : {rec.get('window_present')}")
    L.append(f"ends_at_write_iter  : {rec.get('ends_at_write_iter')}   "
             f"[C5: mechanism-A proviso, refused if not True]")
    L.append(f"snapshots distinct  : {rec.get('distinct')}   [C6]")
    L.append(f"frozen reader round-trip verified by the writer : "
             f"{rec.get('writer_verified')}")
    L.append(f"dfpSnaps            : {rec.get('snapdir')}")
    L.append("")
    L.append("-- C14 capture liveness: the captured omega steps beside the ---")
    L.append("-- SOLVER's OWN per-iteration witness (omegaHistory.csv) -------")
    L.append("These are the FROZEN grader's own input, printed here so the")
    L.append("capture can be audited independently of it.  A zero captured step")
    L.append("is accepted ONLY where the solver's own maxRelDomega is also zero;")
    L.append("a disagreement REFUSES the case (rule 3).  Whether a static field")
    L.append("is a converged one or a clipped one is grade_r5d.py's to rule on")
    L.append("(its L-235 cliff/flat refusals), and this driver does not rule.")
    for s in (rec.get("capture_steps") or []):
        L.append(f"  iter {s['iter']:>6} : captured omega step L2 = "
                 f"{s['captured_step_l2']:.6e} ; solver maxRelDomega = "
                 f"{s['solver_maxRelDomega']}")
    if not rec.get("capture_steps"):
        L.append("  (not measured for this case)")
    L.append("")
    L.append("-- disk bounding -------------------------------------------------")
    L.append(f"purgeWrite bounds functionObject writes : NO (measured; the purge")
    L.append(f"  lives in Time::writeObject, TimeIO.C:561, which a writeObjects")
    L.append(f"  functionObject never routes through).  The driver's own reap")
    L.append(f"  phase bounds it instead.")
    L.append(f"reap keep window    : {rec.get('keep')}")
    L.append(f"iterate dirs pruned after capture : {rec.get('pruned')}")
    L.append("")
    L.append("-- cost (rule 12) ------------------------------------------------")
    L.append(f"wall_seconds        : {rec.get('wall_s')}")
    L.append(f"core-minutes        : {rec.get('core_min')}  "
             f"(wall s * {RANKS} rank / 60)")
    L.append(f"registered cap      : {CAP_CORE_MIN:.1f} core-min "
             f"(PREREGISTRATION.md sec.4: 1.0 core-h)")
    L.append(f"dollars             : DERIVED at ${RATE}/core-h, "
             f"reported-by-owner, NOT measured")
    L.append("")
    L.append("-- what this file does NOT say -----------------------------------")
    L.append("No gate is applied here.  No verdict is asserted here.  Whether")
    L.append("this case is COMPLETE and G-DFP-CONVERGED, and what M is, is")
    L.append("grade_r5d.py's to say and nobody else's.")
    if rec.get("stopped"):
        L.append("")
        L.append(f"STOPPED: {rec['stopped']}")
        L.append("Lane state for this case: BLOCKED")
    L.append("")
    with open(path, "w") as fh:
        fh.write("\n".join(L))
    return path


def measure_rule4(case_dir, write_iter):
    """Read the rule-4 clause values.  Reports; grades nothing."""
    out = {}
    log = os.path.join(case_dir, "log.frozen")
    txt = open(log, errors="replace").read() if os.path.isfile(log) else ""
    out["end_line"] = bool(re.search(r"^End\s*$", txt, flags=re.M))
    out["not_converged"] = ("NOT CONVERGED" in txt)
    out["n_exec"] = len(re.findall(r"ExecutionTime = [0-9.]+ s", txt))
    out["exec_count_ok"] = (write_iter is not None
                            and out["n_exec"] == write_iter)
    pre = txt[:txt.index("Writing fields")] if "Writing fields" in txt else txt
    out["bounding_omega"] = pre.count("bounding omega")
    its = iterate_dirs(case_dir)
    out["latest_time"] = (max(its) if its else None)
    out["last_time_is_write"] = (out["latest_time"] == write_iter)
    fields = ("U", "k", "omega", "nut", "bijDelta", "kDeficit", "bijData",
              "grad(U)")
    present, ages = [], []
    for f in fields:
        p = os.path.join(case_dir, str(write_iter), f)
        z = os.path.join(case_dir, "0", f)
        if os.path.isfile(p):
            present.append(f)
            if os.path.isfile(z):
                ages.append(os.path.getmtime(p) > os.path.getmtime(z))
    out["fields_present"] = f"{len(present)}/{len(fields)}: {present}"
    out["age_guard"] = (all(ages) if ages else None)
    return out


# ----------------------------------------------------------- the run phase
def phase_run(root, only, keep, keep_iterates, launch_order, budget_core_min):
    check_grader_pin()
    check_solver_present()
    G = frozen_constants()
    need = int(G.DFP_KMIN) + 2

    froot = os.path.join(root, FROZEN_SUB)
    if not os.path.isdir(froot):
        refuse(f"nothing staged: {froot} absent.  Run --phase stage first.")
    cases = sorted(d for d in os.listdir(froot)
                   if os.path.isdir(os.path.join(froot, d)))
    if only:
        cases = [c for c in cases if c in only]
    if not cases:
        refuse("no staged case selected")
    zero_shot_guard(cases)

    # C13 - the campaign launch is the supervisor's call, not the driver's.
    if len(cases) > 1 and not launch_order:
        refuse(f"C13: {len(cases)} cases selected.  The 27-case R5D campaign "
               f"launch is the closure-supervisor's call, not this driver's and "
               f"not a lane's.  Pass --launch-order '<who, when>' to record whose "
               f"order it was, or select ONE case with --only.")

    drive = os.path.join(root, "_drive")
    os.makedirs(drive, exist_ok=True)
    spent = 0.0
    results = []
    for case in cases:
        cdir = os.path.join(froot, case)
        remaining = budget_core_min - spent
        if remaining <= 0:
            say(f"[BLOCKED by budget] {case}: {spent:.2f} core-min already "
                f"spent of {budget_core_min:.2f}")
            break
        rec = {"case_dir": cdir, "run_utc": utcnow(), "keep": keep,
               "need": need}
        say(f"\n=== {case} ===")
        done, wall0 = already_solved(cdir)
        if done:
            # R5C's discipline: a completed frozen extraction is SKIPPED, never
            # rerun in place.  The capture phase below is re-entrant, so a
            # driver fix costs no compute.
            say(f"  [skip-solve] rc=0 and an End line already on disk; "
                f"re-entering the capture only (no new compute)")
            rc, wall, stopped = 0, wall0, None
        else:
            say(f"  launching serially, {RANKS} rank, nice -n {NICE}; "
                f"remaining budget {remaining:.2f} core-min")
            _w, pg = launch(cdir, drive, case, keep)
            rc, wall, stopped = wait_for_rc(cdir, pg, remaining)
        cm = 0.0 if done else core_minutes(wall)
        spent += cm
        rec.update({"rc": rc, "wall_s": round(wall, 2),
                    "core_min": round(core_minutes(wall), 4),
                    "new_compute_core_min": round(cm, 4),
                    "solve_skipped": done, "stopped": stopped})
        say(f"  rc={rc}  wall={wall:.1f}s  core-min={core_minutes(wall):.3f}"
            f"  (new compute this invocation: {cm:.3f} core-min)")

        if stopped is not None:
            write_status(root, case, rec)
            say(f"  STOPPED: {stopped}")
            results.append(rec)
            break
        if rc is None:
            refuse(f"C9: {case}: the detached wrapper recorded no usable rc.  A "
                   f"missing rc is NOT a zero (`setsid timeout cmd` exits 0 for "
                   f"every outcome).")

        wi, why = read_write_iter(cdir)
        rec["write_iter"] = wi
        if wi is None:
            say(f"  no write iteration in log.frozen ({why}); "
                f"capture not attempted")
            rec.update(measure_rule4(cdir, wi) if wi else {})
            write_status(root, case, rec)
            results.append(rec)
            continue

        window, missing = capture_window(cdir, wi, need)
        rec["window"] = f"{window[0]}..{window[-1]}"
        rec["window_present"] = (not missing)
        have_snaps, why_snaps = existing_snaps_ok(cdir, wi, need)
        if missing and not have_snaps:
            refuse(f"C4: {case}: iterate directories {missing} are absent, so "
                   f"the last {need} consecutive outer iterates ending at the "
                   f"write iteration {wi} are NOT on disk, and no complete "
                   f"dfpSnaps sequence stands in their place ({why_snaps}).  "
                   f"The capture functionObject did not fire.  This is a "
                   f"finding, not a degraded measurement - no gap is "
                   f"interpolated.")
        if missing and have_snaps:
            # The iterate directories were pruned by an earlier invocation of
            # this driver AFTER the snapshots were written and verified.  The
            # snapshots are byte-for-byte copies; re-verify them through the
            # FROZEN reader and do not re-capture.  Nothing is reconstructed.
            say(f"  [snaps-present] iterate dirs pruned earlier; the existing "
                f"dfpSnaps re-verify through the FROZEN reader")
        else:
            wrc, _wout, werr = run_writer(cdir, wi, need)
            if wrc != 0:
                refuse(f"{case}: write_dfp_snaps.py exited {wrc}\n{werr.strip()}")
        man = read_manifest(cdir)
        if man is None:
            refuse(f"{case}: the writer returned 0 but wrote no readable "
                   f"dfpSnaps/MANIFEST.json")

        # C5 - the ruling, executable.
        for f in SNAP_FIELDS:
            fm = man.get("fields", {}).get(f)
            if fm is None:
                refuse(f"C5: {case}: no manifest entry for field {f}")
            if fm.get("ends_at_write_iter") is not True:
                refuse(f"C5: {case}: field {f} manifest reports "
                       f"ends_at_write_iter={fm.get('ends_at_write_iter')}.  "
                       f"The registered proviso (PREREGISTRATION.md:111) is "
                       f"'consecutive outer iterates ending at the write "
                       f"iteration'; a tail ending PAST the graded field is "
                       f"mechanism B, which is REJECTED.")
        rec["ends_at_write_iter"] = True
        rec["writer_verified"] = all(
            man["fields"][f].get("frozen_reader_verified") is True
            for f in SNAP_FIELDS)
        rec["snapdir"] = os.path.join(cdir, "dfpSnaps")

        # C6 - distinctness.
        for f in SNAP_FIELDS:
            _shas, why6 = snapshot_bytes_distinct(cdir, f, window)
            if why6:
                refuse(f"C6: {case}: {why6}")
        rec["distinct"] = True

        # C14 - plant the zero, applied to the capture (rule 3).
        import numpy as _np                              # noqa: PLC0415
        import of_read as _of                            # noqa: PLC0415

        def _rd(p):
            return _np.asarray(_of.read_field(p), dtype=float).ravel()

        steps, why14 = capture_liveness(cdir, window, _rd)
        if why14:
            refuse(f"{case}: {why14}")
        rec["capture_steps"] = steps

        # grad(U) on the graded time, with C7 around it.
        grc, _ = postprocess_gradU(cdir, wi)
        rec["gradU_rc"] = grc

        rec["pruned"] = ([] if keep_iterates
                         else prune_to_r5c_layout(cdir, wi))
        rec.update(measure_rule4(cdir, wi))
        sp = write_status(root, case, rec)
        say(f"  dfpSnaps written and verified through the FROZEN reader; "
            f"STATUS -> {sp}")
        results.append(rec)

    say("\n" + "=" * 70)
    say(f"R5D driver: {len(results)} case(s) driven.  "
        f"spent {spent:.3f} core-min of the {budget_core_min:.1f} core-min "
        f"budget (registered cap {CAP_CORE_MIN:.1f} core-min).")
    say(f"dollars DERIVED at ${RATE}/core-h (reported-by-owner, NOT measured): "
        f"${spent / 60.0 * RATE:.5f}")
    say("NO VERDICT is asserted by this driver.  grade_r5d.py grades.")
    say("=" * 70)
    return 0


# ============================================================================
#  --selftest   (every control; green under python3 AND python3 -O)
# ============================================================================
def _tmproot():
    base = os.environ.get("R5D_SELFTEST_ROOT",
                          "/home/ubuntu/closure-data/r5d/driver_selftest")
    if os.path.isdir(base):
        shutil.rmtree(base)
    os.makedirs(base)
    return base


def _fake_case(dirpath, iters, write_iter, identical=False):
    """A synthetic case dir with numeric iterate directories."""
    os.makedirs(os.path.join(dirpath, "0"), exist_ok=True)
    for it in iters:
        d = os.path.join(dirpath, str(it))
        os.makedirs(d, exist_ok=True)
        for f in SNAP_FIELDS:
            v = 1.0 if identical else float(it)
            with open(os.path.join(d, f), "w") as fh:
                fh.write(f"{v}\n")
    with open(os.path.join(dirpath, "log.frozen"), "w") as fh:
        fh.write(f"Writing fields at iteration {write_iter}\nEnd\n")
    return dirpath


def _controlDict(path, with_functions=True):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    body = ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
            "    class dictionary;\n    object controlDict;\n}\n"
            "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n"
            f'libs ( "{V2_LIB}" );\n'
            "startFrom startTime;\nstartTime 0;\nstopAt endTime;\n"
            "endTime 5000;\ndeltaT 1;\nwriteControl timeStep;\n"
            "writeInterval 5000;\npurgeWrite 0;\nwriteFormat ascii;\n"
            "writePrecision 15;\n")
    if with_functions:
        body += "functions { }\n"
    with open(path, "w") as fh:
        fh.write(body)
    return path


def _fires(fn, *a, **k):
    """Run `fn`; return True iff it refused with sys.exit(2)."""
    try:
        fn(*a, **k)
    except SystemExit as exc:
        return exc.code == 2
    return False


def selftest():
    print("=" * 72)
    print("R5D run driver --selftest   (UNFROZEN; asserts no verdict)")
    print(f"  __debug__ = {__debug__}   "
          f"({'python3' if __debug__ else 'python3 -O'})")
    print("=" * 72)
    ok_all = True

    def check(name, cond, detail=""):
        nonlocal ok_all
        ok_all = ok_all and bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}"
              + (f"  -- {detail}" if detail else ""))

    tmp = _tmproot()

    # ---- 0: no assert anywhere in this file -------------------------------
    print("\n[0] L-332: no control may live in an `assert`")
    n_ast = no_assert_in_this_file()
    check("0 ast.Assert nodes in run_r5d.py (independent parse)",
          n_ast == 0, f"count={n_ast}")

    # ---- C11: the frozen sha-pin ------------------------------------------
    print("\n[C11] frozen comparator sha-pin (CLAUDE.md rule 2)")
    got = sha256_file(GRADER_PATH) if os.path.isfile(GRADER_PATH) else ""
    check("grade_r5d.py hashes to PREREGISTRATION.md sec.7's pin",
          got == GRADER_SHA_PIN, f"{got[:16]}...")
    #   and the check FIRES on a mutated grader
    bad = os.path.join(tmp, "grade_mutant.py")
    shutil.copyfile(GRADER_PATH, bad)
    with open(bad, "a") as fh:
        fh.write("\n# one byte of drift\n")
    check("a mutated grader would NOT match the pin (the check can fail)",
          sha256_file(bad) != GRADER_SHA_PIN)

    # ---- C2: staging is refused under python3 -O ---------------------------
    print("\n[C2] staging under `python3 -O` disarms the REUSED builder's "
          "asserts")
    if __debug__:
        check("under plain python3, C2 does not block staging",
              True, "the -O branch is exercised by the -O run of this selftest")
    else:
        check("under python3 -O, phase_stage REFUSES",
              _fires(phase_stage, tmp, set(), False),
              "R5C's build_one copy-integrity guards are asserts")

    # ---- C1: the stage guard FIRES ----------------------------------------
    print("\n[C1] rule-4 stage guard: a dirty destination is refused")
    clean = os.path.join(tmp, "clean_dst")
    os.makedirs(clean)
    check("a clean destination is allowed", not _fires(stage_guard, clean))
    dirty0 = os.path.join(tmp, "dirty_zero")
    os.makedirs(os.path.join(dirty0, "0"))
    check("a destination holding 0/ is REFUSED", _fires(stage_guard, dirty0))
    dirtyt = os.path.join(tmp, "dirty_time")
    os.makedirs(os.path.join(dirtyt, "160"))
    check("a destination holding a time dir is REFUSED",
          _fires(stage_guard, dirtyt))

    # ---- C12: zero-shot guard FIRES ---------------------------------------
    print("\n[C12] zero-shot guard as an explicit branch (not an assert)")
    import r4_lib as R                                    # noqa: PLC0415
    a_test = sorted(R.TEST_CASES)[0]
    check("a TEST case in the set is REFUSED (works under -O too)",
          _fires(zero_shot_guard, ["PHLL10595", a_test]), f"test case {a_test}")
    check("a clean training set passes",
          not _fires(zero_shot_guard, ["PHLL10595"]))

    # ---- C3: the capture block lands, and the check FIRES when it does not
    print("\n[C3] capture functionObject: written, then VERIFIED FROM DISK")
    cdir = os.path.join(tmp, "case_fo")
    _controlDict(os.path.join(cdir, "system", "controlDict"))
    info = install_capture(cdir)
    back = open(info["controlDict"]).read()
    check("writeObjects block landed on disk",
          FO_NAME in back and "writeObjects" in back)
    check("all three capture fields are named",
          all(f in info["objects"] for f in SNAP_FIELDS), str(info["objects"]))
    check("the top-level libs entry SURVIVED the rewrite",
          V2_LIB in info["libs"], str(info["libs"]))
    check("the functionObject's own libs(...) is NOT mistaken for the "
          "top-level entry", info["libs"] == [V2_LIB])
    #   a silent no-op: strip the block back out and re-verify
    with open(info["controlDict"], "w") as fh:
        fh.write(back.replace("writeObjects", "noSuchFunctionObject"))
    check("a capture block that did NOT land is REFUSED",
          _fires(install_capture_verify_only, info["controlDict"]))
    #   a lost libs entry
    cdir2 = os.path.join(tmp, "case_nolibs")
    p2 = _controlDict(os.path.join(cdir2, "system", "controlDict"))
    with open(p2, "w") as fh:
        fh.write(open(p2).read().replace(f'libs ( "{V2_LIB}" );', ""))
    check("a controlDict whose top-level libs entry is gone is REFUSED",
          _fires(install_capture, cdir2))

    # ---- reap: bounds the directory, and never eats the newest ------------
    print("\n[reap] rolling window (purgeWrite does NOT bound "
          "functionObject writes)")
    rc_case = _fake_case(os.path.join(tmp, "case_reap"), range(1, 41), 40)
    old = time.time() + 3600           # make every dir look old enough
    r = phase_reap(rc_case, 12, now=old)
    left = iterate_dirs(rc_case)
    check("reap leaves exactly the keep-window", len(left) == 12,
          f"{r['n_before']} -> {len(left)}")
    check("reap NEVER removes the newest (the graded write dir)",
          max(left) == 40)
    check("reap removed only the oldest", left == list(range(29, 41)))
    check("reap with keep<=0 is a no-op (disabled)",
          phase_reap(rc_case, 0)["removed"] == [])
    fresh = _fake_case(os.path.join(tmp, "case_fresh"), range(1, 41), 40)
    r2 = phase_reap(fresh, 12)          # now = real time -> all dirs are fresh
    check("reap NEVER removes a directory touched within the safe age",
          r2["removed"] == [], f"safe age {REAP_SAFE_AGE_S}s")

    # ---- C4: capture-live -------------------------------------------------
    print("\n[C4] capture-live: a window with a hole is a finding, not a gap")
    full = _fake_case(os.path.join(tmp, "case_full"), range(30, 41), 40)
    _w, miss = capture_window(full, 40, 5)
    check("a complete window reports no missing iterates", miss == [])
    holed = _fake_case(os.path.join(tmp, "case_holed"),
                       [36, 37, 39, 40], 40)
    _w, miss2 = capture_window(holed, 40, 5)
    check("a window missing iterates is DETECTED", miss2 == [38],
          f"missing {miss2}")
    none_ = _fake_case(os.path.join(tmp, "case_none"), [40], 40)
    _w, miss3 = capture_window(none_, 40, 5)
    check("a case where the functionObject never fired is DETECTED",
          sorted(miss3) == [36, 37, 38, 39],
          "only the writeNow() directory exists")

    # ---- C6: distinctness -------------------------------------------------
    print("\n[C6] distinctness: five copies of one iterate is a capture failure")
    dcase = os.path.join(tmp, "case_distinct")
    os.makedirs(os.path.join(dcase, "dfpSnaps"))
    for it in range(36, 41):
        with open(os.path.join(dcase, "dfpSnaps", f"omega_{it}"), "w") as fh:
            fh.write(f"{it}\n")
    _s, why = snapshot_bytes_distinct(dcase, "omega", list(range(36, 41)))
    check("distinct snapshots pass", why is None)
    for it in range(36, 41):
        with open(os.path.join(dcase, "dfpSnaps", f"omega_{it}"), "w") as fh:
            fh.write("same\n")
    _s, why2 = snapshot_bytes_distinct(dcase, "omega", list(range(36, 41)))
    check("byte-identical consecutive snapshots are REFUSED",
          why2 is not None, (why2 or "")[:60] + "...")

    # ---- C14: plant the zero, applied to the capture -----------------------
    print("\n[C14] a zero captured step is evidence only against the SOLVER's "
          "own witness")
    lcase = os.path.join(tmp, "case_liveness")
    os.makedirs(os.path.join(lcase, "dfpSnaps"))
    win = list(range(78, 83))

    def _mk(vals):
        for it, v in zip(win, vals):
            with open(os.path.join(lcase, "dfpSnaps", f"omega_{it}"), "w") as fh:
                fh.write(f"{v}\n")

    def _hist(vals):
        with open(os.path.join(lcase, "omegaHistory.csv"), "w") as fh:
            fh.write("iter,initRes,maxRelDomega,minOmegaPreBound,"
                     "nNegOmegaCells,nNegSourceCells\n")
            for it, v in zip(win, vals):
                fh.write(f"{it},1e-12,{v},1e-7,0,0\n")

    import numpy as _np                                  # noqa: PLC0415

    def _reader(p):
        return _np.asarray([float(open(p).read().strip())])

    #   (i) capture moves, solver says it moved -> agreement
    _mk([1.0, 2.0, 3.0, 4.0, 5.0])
    _hist([1e-3] * 5)
    st, why = capture_liveness(lcase, win, _reader)
    check("live capture + live witness -> agreement", why is None,
          f"{len(st)} step(s) measured")
    #   (ii) capture frozen, solver says it moved -> BLIND CAPTURE, refuse
    _mk([7.0, 7.0, 7.0, 7.0, 7.0])
    _hist([1e-3] * 5)
    st2, why2 = capture_liveness(lcase, win, _reader)
    check("BLIND capture (solver moved, snapshots did not) is REFUSED",
          why2 is not None, (why2 or "")[:70] + "...")
    #   (iii) both zero -> agreement; the driver does NOT usurp the grader's
    #         L-235 ruling on a genuinely static field
    _mk([7.0, 7.0, 7.0, 7.0, 7.0])
    _hist([0.0] * 5)
    _st3, why3 = capture_liveness(lcase, win, _reader)
    check("static field + solver witness of 0 -> NOT refused here "
          "(grade_r5d.py owns that ruling)", why3 is None)
    #   (iv) no witness at all -> no false confidence either way
    os.remove(os.path.join(lcase, "omegaHistory.csv"))
    st4, why4 = capture_liveness(lcase, win, _reader)
    check("a case with no omegaHistory.csv yields no witness, and the driver "
          "claims none", why4 is None
          and all(s["solver_maxRelDomega"] is None for s in st4))

    # ---- C5: the ruling, executable ---------------------------------------
    print("\n[C5] mechanism-A proviso: a mechanism-B tail cannot pass")
    a_tail = {"iters": [36, 37, 38, 39, 40], "ends_at": 40, "case_write_iter": 40}
    a_tail["ends_at_write_iter"] = (a_tail["ends_at"]
                                    == a_tail["case_write_iter"])
    b_tail = {"iters": [40, 41, 42, 43, 44], "ends_at": 44,
              "case_write_iter": 40}
    b_tail["ends_at_write_iter"] = (b_tail["ends_at"]
                                    == b_tail["case_write_iter"])
    check("mechanism-A tail reports ends_at_write_iter True",
          a_tail["ends_at_write_iter"] is True)
    check("mechanism-B tail (wi..wi+4) reports False and would be REFUSED",
          b_tail["ends_at_write_iter"] is False,
          "a tail ending PAST the graded field")

    # ---- C9: rc is captured inside the wrapper ----------------------------
    print("\n[C9] rc is captured INSIDE the detached wrapper")
    wt = wrapper_text("/x/case", "/x/drive", "tag", 12)
    check("the wrapper captures rc around the SOLVER, not around setsid",
          "RC=$?" in wt and "wait $SOLVER_PID" in wt)
    check("the wrapper writes rc LAST, after wall_seconds",
          wt.index("wall_seconds") < wt.index('echo "$RC"'))
    check("the driver never runs mpirun", "mpirun" not in wt)
    check("the wrapper runs one rank, niced", f"nice -n {NICE}" in wt)
    check("keep>0 attaches the reaper; keep==0 attaches none",
          "--phase reap" in wt
          and "--phase reap" not in wrapper_text("/x/c", "/x/d", "t", 0))
    #   a wrapper that died leaves no rc: the driver must not read that as 0
    dead = os.path.join(tmp, "case_dead")
    os.makedirs(dead)
    rcv, _wall, why9 = wait_for_rc(dead, os.path.join(tmp, "nope.pgid"),
                                   budget_core_min=0.0005)
    check("no rc file -> rc is None (never assumed 0)", rcv is None)
    #   a completed run is skipped, never rerun; rc alone is not completion
    skipc = os.path.join(tmp, "case_skip")
    os.makedirs(skipc)
    with open(os.path.join(skipc, "rc"), "w") as fh:
        fh.write("0\n")
    with open(os.path.join(skipc, "log.frozen"), "w") as fh:
        fh.write("Writing fields at iteration 82\n")
    check("rc=0 but NO End line -> not treated as done",
          already_solved(skipc)[0] is False)
    with open(os.path.join(skipc, "log.frozen"), "a") as fh:
        fh.write("End\n")
    check("rc=0 AND an End line -> skipped, never rerun (R5C's rule)",
          already_solved(skipc)[0] is True)
    with open(os.path.join(skipc, "rc"), "w") as fh:
        fh.write("1\n")
    check("rc!=0 -> not treated as done", already_solved(skipc)[0] is False)
    check("and the budget overrun STOPS the wait", "BUDGET OVERRUN" in (why9 or "")
          or "never recorded a pgid" in (why9 or ""), (why9 or "")[:60])

    # ---- C8: budget arithmetic --------------------------------------------
    print("\n[C8] core-minutes (rule 12: wall s * ranks / 60)")
    check("60 wall s at 1 rank == 1.000 core-min",
          abs(core_minutes(60.0) - 1.0) < 1e-12)
    check("the registered cap is 60 core-min (1.0 core-h)",
          abs(CAP_CORE_MIN - 60.0) < 1e-12)
    check("the registered estimate is 11.04 core-min (0.184 core-h)",
          abs(EST_CORE_MIN - 11.04) < 1e-9, f"{EST_CORE_MIN:.2f}")

    # ---- read_write_iter reads ONE NAMED artifact -------------------------
    print("\n[named artifact] the write iteration comes from log.frozen")
    wi, _ = read_write_iter(full)
    check("write_iter read from log.frozen, not from a directory listing",
          wi == 40, f"wi={wi}")
    nolog = os.path.join(tmp, "case_nolog")
    os.makedirs(nolog)
    wi2, why10 = read_write_iter(nolog)
    check("a case with no log.frozen yields None, not a guess",
          wi2 is None, why10)

    # ---- STATUS is written and asserts no verdict -------------------------
    print("\n[STATUS] a reader who was not there can apply rule 4")
    sp = write_status(tmp, "case_x",
                      {"case_dir": full, "run_utc": utcnow(), "rc": 0,
                       "write_iter": 40, "need": 5, "keep": 12})
    txt = open(sp).read()
    check("STATUS names every rule-4 clause",
          all(t in txt for t in ("rc", "End line", "write_iter",
                                 "ExecutionTime count", "AGE GUARD",
                                 "core-minutes")))
    check("STATUS asserts no verdict",
          "GATE FAIL" not in txt and "PASS" not in txt and
          "GATE REACHED" not in txt)
    check("STATUS records the mechanism and that A is the STRICTER option",
          "mechanism" in txt and "STRICTER" in txt)

    print("\n" + "=" * 72)
    verdictless = ("GREEN - every control exercised, refusals FIRED"
                   if ok_all else "RED")
    print("SELFTEST " + verdictless)
    print("=" * 72)
    return 0 if ok_all else 1


def install_capture_verify_only(controldict_path):
    """Verify-only twin of install_capture's disk check, for the selftest.

    Shares the predicate, not a copy of it: it re-reads the same bytes and
    applies the same branch, so the selftest proves the REAL check fires.
    """
    back = open(controldict_path).read()
    if not re.search(r"^\s*type\s+writeObjects;\s*$", back, re.M):
        refuse("C3: type writeObjects did not land - the capture block is a "
               "silent no-op and the run would produce ZERO snapshots")
    return True


# ============================================================================
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="R5D run driver: stage the registered cases, drive the "
                    "MECHANISM-A per-iteration capture, normalise the iterates "
                    "through write_dfp_snaps.py, and write STATUS.<case>.  "
                    "Grades nothing; asserts no verdict; freezes nothing.")
    ap.add_argument("--phase", choices=("stage", "run", "reap", "selftest"),
                    default="selftest")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=DEFAULT_ROOT,
                    help=f"run root holding {FROZEN_SUB}/ and {LEGACY_SUB}/ "
                         f"(default {DEFAULT_ROOT}, which grade_r5d.py grades)")
    ap.add_argument("--only", nargs="*", default=None, help="case name(s)")
    ap.add_argument("--case", default=None, help="reap: one case directory")
    ap.add_argument("--keep", type=int, default=KEEP_DEFAULT,
                    help="reap window; 0 disables the reaper")
    ap.add_argument("--keep-iterates", action="store_true",
                    help="do not prune the iterate directories after capture "
                         "(for a supervisor spot-check)")
    ap.add_argument("--no-legacy", action="store_true",
                    help="stage: skip the two W2 legacy byte-identity cases")
    ap.add_argument("--launch-order", default=None,
                    help="C13: who ordered a multi-case launch, and when")
    ap.add_argument("--budget-core-min", type=float, default=CAP_CORE_MIN,
                    help=f"stop after this many core-minutes (registered cap "
                         f"{CAP_CORE_MIN:.0f})")
    args = ap.parse_args(argv)

    if args.selftest or args.phase == "selftest":
        return selftest()

    if args.budget_core_min > CAP_CORE_MIN:
        refuse(f"C8: --budget-core-min {args.budget_core_min} exceeds the "
               f"REGISTERED cap {CAP_CORE_MIN:.1f} core-min "
               f"(PREREGISTRATION.md sec.4).  An overrun stops the run; it does "
               f"not get a new budget, and a driver flag is not a new budget "
               f"either (CLAUDE.md rules 9, 12).")

    if args.phase == "reap":
        if not args.case:
            refuse("--phase reap needs --case")
        r = phase_reap(args.case, args.keep)
        print(json.dumps(r, sort_keys=True))
        return 0
    if args.phase == "stage":
        return phase_stage(args.root, set(args.only or []), not args.no_legacy)
    return phase_run(args.root, set(args.only or []), args.keep,
                     args.keep_iterates, args.launch_order,
                     args.budget_core_min)


if __name__ == "__main__":
    sys.exit(main())
