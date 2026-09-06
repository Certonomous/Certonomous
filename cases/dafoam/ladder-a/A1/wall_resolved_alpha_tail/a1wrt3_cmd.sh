#!/usr/bin/env bash
# =============================================================================
# A1WRT3 -- THE IN-CONTAINER UNIT PROGRAM.
#
# A FILE, NOT AN INLINE HEREDOC (the SO-1b lesson, carried from `aoa_cmd.sh`
# and from `A1WRT/cmd.sh:8`).  THE REASON THIS FILE EXISTS AS A FILE IS THE
# REASON A1WRT2 COULD DELETE IT INVISIBLY: it was never a file there at all,
# it was three lines inlined into `docker run`, and a deletion of three inlined
# lines leaves no artefact whose absence anyone can gate.
#
# ---------------------------------------------------------------------------
# THIS FILE IS THE RESTORATION OF `/home/ubuntu/certonomous-runs/A1WRT/cmd.sh`
# UNDER THE 17-CLAUSE ACCOUNTING OF `A1WRT3_SUCCESSOR_DRAFT.md` section 2.
#
# WHERE THE DRAFT SAYS A CLAUSE IS *RESTORED*, ITS **EFFECT** IS RESTORED AND
# NOT ITS TEXT.  The variable names do not match across the seam: the launcher
# speaks `A1WRT3_*`, the producer reads `AOA_*`, AND NOT ONE NAME IS SHARED.
# **THE DELETED LAYER IS THE TRANSLATION.**  Two of the four names the producer
# needs -- `AOA_POINTS_JSON` and `AOA_ALPHA0` -- have NO launcher-side
# counterpart at all: one is a literal path, the other is the FIRST ELEMENT of
# a list the launcher passes whole.  A launcher that forwarded every `-e` it
# had would still have crashed at `runScript.py:51`.  Clause C13 below is the
# repair, and it is the centre of this item.
#
# CLAUSE MAP -- draft section 2, in file order.  Every clause of the deleted
# file is accounted for; the dispositions the reader most needs are these two:
#
#   C11  `rm -rf 0 && cp -r 0.orig 0`  -- **DELIBERATELY DROPPED AND IT MUST
#        NOT BE RESTORED.**  Executing it would destroy the staged `4000/`
#        continuation that the SEAM arm exists to read back, and would drive
#        `G-SEAM` to `GATE FAIL` FOR A REASON THAT IS NOT THE RESTART
#        MECHANISM -- manufacturing the exact false negative this item was
#        built to avoid.  Replaced by C11', which PRINTS what was not done.
#
#   C12  the `PROBE` -> `COLD` remap -- **DROPPED AND REPLACED BY A REFUSAL**,
#        not by silence.  A1WRT3 registers no PROBE arm, so the remap is
#        unreachable; in its place `test "$A1WRT3_MODE" = CONTINUED` else
#        exit 94.  A DROPPED TRANSLATION IS REPLACED BY A REFUSAL, NEVER BY
#        SILENCE.
#
#   C17  the exit status recomputed from `grep -c '^AOA_POINT_END '` --
#        **DROPPED AS A DEFECT, NOT AS A PREFERENCE.**  That marker prints for
#        a CRASHED point too, so A1WRT U1 scored EXEC=1 == DECLARED=1 and
#        exited 0 OVER ITS OWN PRODUCER'S rc=97.  Replaced by C17':
#        `exit "$SRC"` -- the producer's own rc, propagated, never recomputed.
#
# ---------------------------------------------------------------------------
# OUTPUT-STREAM SEPARATION (draft section 3.2), AND IT IS LOAD-BEARING.
# THIS FILE'S OWN ECHOES GO TO THE CONTAINER'S STDOUT, WHICH THE LAUNCHER
# CAPTURES AS `<ARM>/out/container.log`.  ONLY THE PRODUCER IS REDIRECTED, INTO
# `<ARM>/out/sweep.log` (C13).  Collapsing the two streams is what made the
# predecessor's wall-treatment guard unobservable, and the host side's
# count-pinned presence assertion on `A1WRT3_WALLTREAT_SCRIPT_OK` depends on
# this separation holding.
#
# ---------------------------------------------------------------------------
# REGISTERED SELFTEST ENTRY POINTS, AND WHY THEY ARE NOT A BACKDOOR.
#
# `CLAUDE.md` rule 3 requires every control to DRIVE THE REAL GATE FUNCTION.
# G-WALLTREAT clause 1 and G-ENVSEAM clause 2 live INSIDE this file, on the far
# side of a `docker run`, so a control that re-implements them in the selftest
# would be testing a copy -- the L-493 wrong-route shape.  This file therefore
# carries two argument-selected entry points that execute THE SAME CODE the run
# path executes, over bytes named on argv, and then exit:
#
#     a1wrt3_cmd.sh --selftest-walltreat <path>   -> runs C8 limbs (a)(b)(c)
#     a1wrt3_cmd.sh --selftest-envseam-c2 N=V...  -> runs G-ENVSEAM clause 2
#
# THE RUN PATH TAKES NO ARGUMENTS AND REFUSES IF GIVEN ANY (see RUN-PATH ARGV
# REFUSAL below).  Neither entry point can be reached by the container command,
# which invokes this file bare; neither writes anything; neither can weaken a
# gate, because each one IS the gate.
# =============================================================================
set -uo pipefail                                          # C1 -- and see below

# ---------------------------------------------------------------------------
# C1.  `set -uo pipefail` AND DELIBERATELY **NOT** `-e`.
# The absence of `-e` is restored AS AN ABSENCE, on purpose: this script MUST
# reach its own rc-propagation line (C17') rather than dying at the first
# non-zero.  With `-e` armed, C13's non-zero producer rc would kill the shell
# before C14 could capture `$?`, and the container would exit on the shell's
# status instead of the producer's -- reintroducing C17's defect by a different
# route.  RECORDED AS A DELIBERATE RESTORATION OF AN ABSENCE.
# ---------------------------------------------------------------------------

A1WRT3_PRODUCER=/run_root/runScript.py
A1WRT3_OUT=/mnt/out

# =============================================================================
# G-WALLTREAT CLAUSE 1 -- THE CONFIGURATION ASSERTION, PRE-SOLVER.
#
# It fires INSIDE the container, BEFORE `python` is invoked, and IT NAMES WHAT
# IT READ.  Draft section 3.1 records three defects in the predecessor's form
# (`A1WRT/cmd.sh:41-44`) and this function repairs each by a named limb:
#
#   (a) the POSITIVE, counted on LIVE lines only -- a commented mention is not
#       a configuration.
#   (b) the NEGATIVE.  `grep -q` for the positive alone is satisfied by a file
#       that ALSO carries a live `True`; such a file passed `cmd.sh:42` and ran
#       with wall functions.  Limb (b) closes it and control `W1b` drives it.
#   (c) IDENTITY.  The predecessor said "present in staged runScript" and never
#       said WHICH staged runScript -- and this family was MEASURED resolving
#       `runScript.py` by basename across 59 candidates in different run roots
#       and silently picking the wrong one.  Limb (c) prints the ABSOLUTE path,
#       the BYTE COUNT and the MD5 OF THE EXACT BYTES GREPPED, and the host
#       side asserts that md5 equals the pinned producer md5
#       `d48f48c5e2e41e86981acbf6feccb3c4`.
#       A GATE THAT REPORTS ON BYTES IT CANNOT IDENTIFY IS A GATE ON NOTHING,
#       so an md5 that cannot be computed REFUSES rather than being omitted.
#
# The pass line `A1WRT3_WALLTREAT_SCRIPT_OK` is asserted host-side to occur
# EXACTLY ONCE in that arm's own `container.log` (L-493: pin the count, not the
# appearance).  Its silence is therefore no longer indistinguishable from its
# success -- the A1ZE ADDENDUM C test that `cmd.sh:42-44` fails.
# =============================================================================
walltreat_clause1() {
  local target="$1" n_false n_true bytes md5

  test -f "$target" || {
    echo "A1WRT3_FATAL G-WALLTREAT c1: target absent at point of use: $target"
    return 98
  }

  # LIVE lines only.  `^[^#]*` cannot cross a `#`, so a commented mention --
  # and `runScript.py:10` IS one -- counts for neither limb.
  n_false="$(grep -cE '^[^#]*"useWallFunction"[[:space:]]*:[[:space:]]*False' "$target")"
  n_true="$(grep -cE '^[^#]*"useWallFunction"[[:space:]]*:[[:space:]]*True' "$target")"
  n_false="${n_false:-0}"; n_true="${n_true:-0}"

  bytes="$(wc -c < "$target" 2>/dev/null)"; bytes="${bytes:-UNMEASURED}"

  # Limb (c).  Two readers, then a REFUSAL -- never an omission.
  md5="$(md5sum "$target" 2>/dev/null | cut -d' ' -f1)"
  if [ -z "$md5" ]; then
    md5="$(python -c 'import hashlib,sys;print(hashlib.md5(open(sys.argv[1],"rb").read()).hexdigest())' "$target" 2>/dev/null)"
  fi
  if [ -z "$md5" ]; then
    echo "A1WRT3_FATAL G-WALLTREAT c1 limb (c): md5 of $target NOT COMPUTABLE -- neither md5sum nor python could read it; a gate on unidentifiable bytes is a gate on nothing"
    return 98
  fi

  # Limb (a) -- the positive, on live lines.
  if [ "$n_false" -lt 1 ]; then
    echo "A1WRT3_FATAL G-WALLTREAT c1 limb (a): no LIVE '\"useWallFunction\": False' in $target (live_false=$n_false live_true=$n_true bytes=$bytes md5=$md5)"
    return 98
  fi

  # Limb (b) -- the negative.  THE LIMB `cmd.sh` COULD NOT HAVE PASSED.
  if [ "$n_true" -ne 0 ]; then
    echo "A1WRT3_FATAL G-WALLTREAT c1 limb (b): $n_true LIVE '\"useWallFunction\": True' in $target beside $n_false False -- a wall-resolved item may not run wall functions (bytes=$bytes md5=$md5)"
    return 98
  fi

  echo "A1WRT3_WALLTREAT_SCRIPT_OK path=$target bytes=$bytes md5=$md5 live_false=$n_false live_true=$n_true"
  return 0
}

# =============================================================================
# G-ENVSEAM CLAUSE 2 -- CONTAINER-SIDE, DYNAMIC, AT THE POINT OF USE.
#
# Asserts that every `AOA_*` name the C13 translation is ABOUT TO SET is
# NON-EMPTY, after the translation is constructed and before `python` is
# invoked.  Exit 94, the C6 code, so the refusal vocabulary does not fork.
#
# NEITHER G-ENVSEAM CLAUSE ALONE SUFFICES AND THAT IS THE POINT.  Clause 1
# (host, static, pre-container) cannot see a translation that computes the
# wrong VALUE; clause 2 cannot run at all if the container never starts.  The
# defect that killed A1WRT2 at four seconds lived precisely in the gap.
#
# AN EMPTY VALUE IS NOT A PRESENT VALUE -- control `E4` drives exactly that.
# =============================================================================
envseam_clause2() {
  local pair name value n=0 bad=0
  for pair in "$@"; do
    name="${pair%%=*}"
    value="${pair#*=}"
    n=$((n + 1))
    if [ -z "$value" ]; then
      echo "A1WRT3_FATAL G-ENVSEAM c2: $name is EMPTY at the point of use -- an empty value is not a present value"
      bad=$((bad + 1))
    fi
  done
  if [ "$n" -eq 0 ]; then
    echo "A1WRT3_FATAL G-ENVSEAM c2: NOTHING WAS CHECKED -- zero name=value pairs reached the clause; a guard that checked nothing is not a guard that passed"
    return 94
  fi
  if [ "$bad" -ne 0 ]; then
    echo "A1WRT3_ENVSEAM_C2_FAIL checked=$n empty=$bad"
    return 94
  fi
  echo "A1WRT3_ENVSEAM_C2_OK checked=$n empty=0 -- every AOA_* value non-empty before python"
  return 0
}

# =============================================================================
# THE REGISTERED SELFTEST ENTRY POINTS.  See the header.  These run the SAME
# functions the run path runs, and then exit.
# =============================================================================
case "${1:-}" in
  --selftest-walltreat)
    test $# -eq 2 || { echo "A1WRT3_FATAL --selftest-walltreat takes exactly one path"; exit 2; }
    walltreat_clause1 "$2"; exit $?
    ;;
  --selftest-envseam-c2)
    shift
    envseam_clause2 "$@"; exit $?
    ;;
esac

# ---------------------------------------------------------------------------
# RUN-PATH ARGV REFUSAL.  The container command invokes this file BARE.  Any
# argv at this point is either a typo in the launcher or an attempt to reach a
# selftest entry point from the run path, and both are refused rather than
# ignored.  `A1WRT/cmd.sh` accepted and silently discarded argv.
# ---------------------------------------------------------------------------
test $# -eq 0 || { echo "A1WRT3_FATAL run path takes no arguments, got $#: $*"; exit 88; }

# ===========================================================================
# C0 -- THE CLAUSE `cmd.sh` DID NOT HAVE, ADDED BECAUSE ITS ABSENCE WAS
# MEASURED.  In A1WRT the outer layer sourced the loader and then immediately
# ran a python one-liner, so a broken loader failed loudly before `cmd.sh` was
# reached.  A CHECK THAT EXISTS ONLY AS A SIDE EFFECT OF AN UNRELATED
# ONE-LINER IS NOT A CHECK: measured 2026-09-05, `/bin/sh` AND `/bin/bash -lc`
# both report `python: command not found` on this image without the loader.
# Exit 89 is new and unused elsewhere in this family.
# ===========================================================================
command -v python >/dev/null 2>&1 || {
  echo "A1WRT3_FATAL python unresolved -- loader did not take"
  exit 89
}
echo "A1WRT3_PYTHON_OK $(command -v python)"

# C2 -- RESTORED, PATH ONLY.  A1WRT3 mounts the arm case at /mnt (as A1WRT2
# did) rather than /mnt/case.  SAME REFUSAL, SAME CODE.
cd /mnt || { echo "A1WRT3_FATAL cannot cd /mnt"; exit 90; }

# C3 -- RESTORED, retargeted to the A1WRT3 mount.  The producer present AT THE
# POINT OF USE.  This is casualty 3 of A1WRT2-DEF-ENVSEAM and it closes here.
test -f "$A1WRT3_PRODUCER" || {
  echo "A1WRT3_FATAL runScript absent at point of use: $A1WRT3_PRODUCER"
  exit 91
}

# C4' -- REPLACEMENT for C4 (`test -d 0.orig`).  A1WRT3's arms are CONTINUED
# from a staged `4000/`; `0.orig` is a cold-start artefact this item never
# uses, and retaining C4 would refuse a correctly-staged continued case.  C4'
# asserts the INVERSE, at the same exit code, so the refusal vocabulary does
# not fork.  This is the in-container limb of G-COLDSTART-SEAM.
test -d 4000 || {
  echo "A1WRT3_FATAL CONTINUED start state absent: 4000/ not present in $(pwd)"
  exit 92
}
test ! -d 0 || {
  echo "A1WRT3_FATAL a cold 0/ is shadowing the staged 4000/ in $(pwd) -- this arm continues, it does not cold-start"
  exit 92
}

# C5 -- RESTORED VERBATIM.
test -f constant/polyMesh/points.gz || {
  echo "A1WRT3_FATAL mesh absent at point of use"
  exit 93
}

# C6 -- RESTORED, retargeted to the A1WRT3_* launcher-side names.  The
# launcher-side names present AT THE POINT OF USE.  EXTENDED by G-ENVSEAM
# clause 2 below, which asserts the AOA_* side after the translation.
test -n "${A1WRT3_MODE:-}"   || { echo "A1WRT3_FATAL A1WRT3_MODE unset";   exit 94; }
test -n "${A1WRT3_ALPHAS:-}" || { echo "A1WRT3_FATAL A1WRT3_ALPHAS unset"; exit 94; }
test -n "${A1WRT3_TOL:-}"    || { echo "A1WRT3_FATAL A1WRT3_TOL unset";    exit 94; }
test -n "${A1WRT3_TMO:-}"    || { echo "A1WRT3_FATAL A1WRT3_TMO unset";    exit 94; }

# C7 -- RESTORED, retargeted to the arm's own out directory.
mkdir -p "$A1WRT3_OUT" || { echo "A1WRT3_FATAL cannot mkdir $A1WRT3_OUT"; exit 95; }

# C8 -- G-WALLTREAT CLAUSE 1, RESTORED, STRENGTHENED AND PROPERLY REGISTERED.
# Casualty 4, and the one that is not cosmetic: a wall-resolved run that
# silently uses wall functions is measuring something other than what it
# claims.  THE SOLVER NEVER STARTS IF THIS FAILS.
walltreat_clause1 "$A1WRT3_PRODUCER" || exit 98

# C9 -- RESTORED IN SHAPE.  FIRST_ALPHA is the SOLE SOURCE of `AOA_ALPHA0` --
# the value with NO launcher-side counterpart, and the immediate cause of the
# 2026-09-05 KeyError at `runScript.py:51`.
DECLARED=0
for A in $A1WRT3_ALPHAS; do DECLARED=$((DECLARED + 1)); done
FIRST_ALPHA="$(set -- $A1WRT3_ALPHAS; echo "$1")"

# C10 -- RESTORED and renamed.  The in-container provenance line.  It is now
# GATED: the host side pins the count of the C8 OK line, so this guard's
# silence is no longer indistinguishable from its success.
echo "A1WRT3_UNIT arm=${A1WRT3_ARM:-UNSET} mode=$A1WRT3_MODE declared=$DECLARED list=[$A1WRT3_ALPHAS] first=$FIRST_ALPHA tol=$A1WRT3_TOL tmo=$A1WRT3_TMO omp=${OMP_NUM_THREADS:-UNSET} utc=$(date -u +%Y-%m-%dT%H%M%SZ)"

# C11' -- REPLACEMENT for C11, THE ONE CLAUSE THAT MUST NOT BE RESTORED.
# `rm -rf 0 && cp -r 0.orig 0` is NOT executed here and MUST NOT BE: it would
# destroy the staged 4000/ this arm exists to read back and drive G-SEAM to
# GATE FAIL for a reason that has nothing to do with the restart mechanism.
# The positive statement of what was deliberately NOT done is PRINTED INTO THE
# RECORD rather than left as an absence, and the absence is RE-ASSERTED.
echo "A1WRT3_CONTINUED_START 0/ NOT reset -- this unit continues from 4000/ (A1WRT/cmd.sh:51-52 deliberately not restored)"
test ! -d 0 || {
  echo "A1WRT3_FATAL 0/ present after the continued-start declaration -- something reset the case"
  exit 92
}

# C12 -- THE DROPPED TRANSLATION, REPLACED BY A REFUSAL AND NOT BY SILENCE.
# `A1WR_MODE=PROBE -> COLD` is unreachable in A1WRT3, which registers no PROBE
# arm.  In its place, the refusal.
test "$A1WRT3_MODE" = "CONTINUED" || {
  echo "A1WRT3_FATAL mode '$A1WRT3_MODE' is not CONTINUED -- A1WRT3 registers no PROBE arm and the PROBE->COLD remap is DROPPED; a dropped translation is replaced by a refusal, never by silence"
  exit 94
}
MODE_FOR_LEDGER="$A1WRT3_MODE"

# ---------------------------------------------------------------------------
# THE TRANSLATION'S VALUES, COMPUTED ONCE.  C13 below sets the producer's
# environment FROM THESE AND FROM NOTHING ELSE, so what G-ENVSEAM clause 2
# checks is what `python` receives.
#
# >>> A1WRT3 C13 TRANSLATION BEGIN
# The names on the left of each `=` in this block are extracted from THIS FILE
# by `a1wrt3_instruments.py` and unioned with the `-e` array to form the set
# G-ENVSEAM clause 1 checks the producer against.  THE GATE READS THE FILE THAT
# RUNS.  Do not re-type this list anywhere.
AOA_MODE="$MODE_FOR_LEDGER"
AOA_ALPHAS="$A1WRT3_ALPHAS"
AOA_POINTS_JSON="$A1WRT3_OUT/points.json"
AOA_ALPHA0="$FIRST_ALPHA"
AOA_LEDGER="$A1WRT3_OUT/LEDGER.tsv"
A1WR_PRIMAL_TOL="$A1WRT3_TOL"
# <<< A1WRT3 C13 TRANSLATION END
# ---------------------------------------------------------------------------

# G-ENVSEAM CLAUSE 2, on the values just computed, BEFORE python.
envseam_clause2 \
  "AOA_MODE=$AOA_MODE" \
  "AOA_ALPHAS=$AOA_ALPHAS" \
  "AOA_POINTS_JSON=$AOA_POINTS_JSON" \
  "AOA_ALPHA0=$AOA_ALPHA0" \
  "AOA_LEDGER=$AOA_LEDGER" \
  "A1WR_PRIMAL_TOL=$A1WR_PRIMAL_TOL" \
  || exit 94

# ===========================================================================
# C13 -- THE AOA_* TRANSLATION.  **THIS IS THE REPAIR.**
#
# All six assignments exported into the producer's environment.  The two with
# NO launcher-side counterpart -- `AOA_POINTS_JSON` (a literal path) and
# `AOA_ALPHA0` (the FIRST ELEMENT of a list the launcher passes whole) -- are
# restored BY NAME.  A1WRT2 passed `-e OMP_NUM_THREADS=1` and nothing else and
# died at `runScript.py:51` in four seconds.
#
# `timeout -k 60 "$A1WRT3_TMO"` IS THE IN-CONTAINER DEADLINE AND IT IS THE CAP
# THAT SURVIVES THE DEATH OF EVERY AGENT.  A1WR's own kill is the argument: its
# driver was polling healthily at 02:24:58Z and the box went down seven seconds
# later.  A1WRT2 deleted `cmd.sh` and with it this deadline; this restores it.
#
# ONLY THE PRODUCER IS REDIRECTED.  This script's own lines stay on the
# container's stdout -- draft section 3.2, and the host-side count pin on
# `A1WRT3_WALLTREAT_SCRIPT_OK` depends on that separation.
# ===========================================================================
AOA_MODE="$AOA_MODE" \
AOA_ALPHAS="$AOA_ALPHAS" \
AOA_POINTS_JSON="$AOA_POINTS_JSON" \
AOA_ALPHA0="$AOA_ALPHA0" \
AOA_LEDGER="$AOA_LEDGER" \
A1WR_PRIMAL_TOL="$A1WR_PRIMAL_TOL" \
timeout -k 60 "$A1WRT3_TMO" \
  python "$A1WRT3_PRODUCER" -task sweep > "$A1WRT3_OUT/sweep.log" 2>&1
# C14 -- RESTORED AND MADE LOAD-BEARING.  In A1WRT, `SRC` was captured,
# printed and NEVER USED AGAIN.  Here it is the sole input to C17'.
SRC=$?
echo "A1WRT3_SWEEP_RC rc=$SRC log=$A1WRT3_OUT/sweep.log"

# C15 -- RESTORED AS REPORTED COUNTS ONLY, AND EXPLICITLY DEMOTED.
# THEY NEVER DECIDE AN EXIT STATUS.  That is C17's defect and C17 is dropped.
# `BCOK` is promoted into G-WALLTREAT clause 2 on the HOST, where it becomes a
# gated quantity instead of a printed one; the print here is for the reader.
EXEC="$(grep -c '^AOA_POINT_END ' "$A1WRT3_OUT/sweep.log" 2>/dev/null || true)"; EXEC="${EXEC:-0}"
CONV="$(grep -c 'satisfied the prescribed tolerance' "$A1WRT3_OUT/sweep.log" 2>/dev/null || true)"; CONV="${CONV:-0}"
BCOK="$(grep -c 'BCType=nutLowReWallFunction' "$A1WRT3_OUT/sweep.log" 2>/dev/null || true)"; BCOK="${BCOK:-0}"
echo "A1WRT3_COUNTS declared=$DECLARED point_end_markers=$EXEC converged_lines=$CONV walltreat_lines=$BCOK REPORTED_ONLY these counts decide nothing"

# ===========================================================================
# C17' -- THE PRODUCER'S OWN rc, PROPAGATED, NEVER RECOMPUTED FROM MARKERS.
#
# C17 recomputed the unit's status from `grep -c '^AOA_POINT_END '`, a marker
# that prints for a CRASHED point as well as a successful one, and so exited 0
# over its own producer's rc=97.  A1WRT2's host side refused that defect BY
# CONSTRUCTION; restoring `cmd.sh` re-opens the hole unless the replacement is
# registered here, AND IT IS.  This is the in-container limb of G-RC-HONEST.
# ===========================================================================
exit "$SRC"
