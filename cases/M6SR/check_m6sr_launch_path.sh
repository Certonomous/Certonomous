#!/bin/bash
# M6SR LAUNCH-PATH CHECK -- the controls for Amendment 12 audit items 28 and 30, and the
# standing evidence for item 31.
#
# WHAT THIS FILE IS.  cases/M6SR/run_m6sr_b5.sh carried two defects that between them made
# Gate A unreachable, and the first MASKED the second:
#
#   ITEM 28  run_in_container() built its call as `$DRUN "docker run ..."`.  On the
#            `sg docker -c` branch that is one shell command and is correct.  On the BARE
#            branch it is `docker "docker run ..."` -- the whole command as ONE ARGUMENT.
#            MEASURED: rc 1, `docker: unknown command: docker docker run ...`.
#            `BARE_RC` is 0 on this box, so the driver was correct ONLY on the branch this
#            box does NOT take, and the live branch had never been exercised.
#
#   ITEM 30  the case directory is created by the HOST user (uid 1000 gid 1000, umask 0002
#            -> 775 ubuntu:ubuntu) and the container runs `-u 1002:1002`.  MEASURED:
#            `Permission denied`, inner rc 1, log.checkMesh ABSENT.  The driver's
#            `chmod -R 777` sits in the SOLVE phase, AFTER B4, so it never helped B4.
#            THIS IS INDEPENDENT OF ITEM 28 AND FIXING 28 DOES NOT FIX 30.
#
#   ITEM 31  with 28 and 30 repaired, checkMesh reaches the container and STILL returns
#   (reg 33) inner rc 1: `cannot find file "/case/system/controlDict"`.  Section 8's case is
#            written in the SOLVE phase, AFTER B4.  REPORTED, NOT REPAIRED -- the fix is a
#            change to the REGISTERED STEP ORDER, not to the launch path.
#
#   ITEM 32  the outer wrapper's redirect target and B4's inner output file were THE SAME PATH
#   (reg 34) -- `$CASE/log.checkMesh` -- because the tag IS `checkMesh`.  The host held that fd
#            at offset 0 while the container wrote the same inode through the bind mount, so a
#            host-side write landed at offset 0 and OVERWROTE THE HEAD of the artifact Gate A
#            grades, leaving the maxima near the END intact.  MEASURED: the corrupted 3330-byte
#            log still returned state=READ with every maximum Gate A reads.  IT DID NOT FAIL
#            CLOSED.  REPAIRED in the driver by moving the wrapper's log OUT OF THE BIND MOUNT
#            (topology, not naming) plus a refusal if it ever returns; T5 below is the control.
#
#   THE NUMBERING.  `M6SR_PREREGISTRATION.md` runs one GLOBAL item counter and its §18.8
#   already spends 31 and 32 on different findings.  The board's 31 and 32 are registered there
#   as 33 and 34.  Both numbers are carried above so neither reader is stranded.
#
# WHY IT IS COUPLED TO THE DRIVER'S OWN TEXT.  This check does NOT re-type the repaired
# constructs.  It EXTRACTS them from run_m6sr_b5.sh and runs those.  A mutation to the driver
# therefore drives this suite RED -- which is the only thing that makes a green here mean
# anything about the driver rather than about this file.
#
# RULE 3, THE PLANTED CONTROL.  Every negative limb below is worthless unless the same reader
# can be shown reading a SUCCESS.  So T1 plants a per-run sentinel, has the CONTAINER write
# it, and reads it back OFF DISK; if the sentinel cannot be seen the suite REFUSES (exit 2)
# rather than reporting the negatives as evidence.
#
# THE IMAGE IS THE REAL PINNED DIGEST, NOT A MOCK.  A mock proves nothing about a defect
# whose whole content is what a real container may write into a real bind mount.
#
# NO SOLVER RUNS HERE.  checkMesh on an already-built mesh and a container `echo`; no
# rhoSimpleFoam, no queue row, no write anywhere under verification/runs/.
#
#   ITEM 47  Section 7 called itself "THE ONE THING THAT BLOCKS" and said its five conditions
#            are "Checked per level BEFORE launch", while NOTHING ON THE LAUNCH PATH CONSULTED
#            GATE A AT ALL: the driver invoked the comparator exactly twice, both times as
#            `--controls`.  Amendment 19 made conditions 2-5 GRADEABLE; it did not make them
#            BLOCK A LAUNCH.  REPAIRED in the driver by step `B4s` (exit 11 BLOCKED / 12
#            REFUSAL) and T6 below is the control: FOUR MUTANTS, ONE PER CLAUSE, each driven
#            through the DRIVER'S OWN EXTRACTED SCREEN FUNCTION, plus THE CLEAN TWIN, which
#            must still reach the solver line.  Without the clean twin the four mutants prove
#            only that something failed.
#
#   ITEM 48  Section 19.3 RULED, pre-compute, that Section 8's case is written BEFORE `B4` as
#            step `B3c`.  Section 19.8 costed it and two later amendments called it "not moved
#            and not redefined".  MEASURED: `B3c` existed in the registration and IN NO
#            EXECUTABLE -- the writer ran only in the SOLVE phase, after B4, which is exactly
#            the placement Section 19.3.1 measured as inner rc 1, no `log.checkMesh`, and
#            therefore no Gate A and no `B4s`.  REPAIRED by SPLITTING the write: `B3c` writes
#            `constant/` + `system/` at stage time, `B3z` writes `0/` at solve time.  THE SPLIT
#            IS NOT TIDINESS -- moving the whole write up would have laid `0/U` at stage time
#            and made rule 4's age guard PASS UNCONDITIONALLY.  T7 is the ordering control; the
#            behavioural half is W6/W7 in `write_m6sr_case.py --selftest`.
#
# USAGE:  check_m6sr_launch_path.sh [--controls]      -- everything, T1..T7
#         check_m6sr_launch_path.sh --section7-only   -- T0 + T6 + T7 ONLY, NO CONTAINER
# EXIT:   0 all checks passed;  1 a check FAILED;  2 the suite REFUSED (plant unseen /
#         preconditions absent) -- a refusal is NEVER reported as a pass.
#
# ⚠ WHAT `--section7-only` IS AND IS NOT.  It exists because T1..T5 start a REAL container on
# the pinned digest and item 47's repair can be exercised with no container at all -- the
# screen is a host `python3` reading two files.  IT IS NOT A WAY TO PRINT GREEN WHILE SKIPPING
# TESTS: it names, on stdout, exactly which tests it did not run and why, it is never the
# default, and it cannot report a pass for anything it skipped.  A caller who wants the item
# 28/30/31/32 evidence must run the suite with no flag.

set +u
set +e

MODE=all
case "$1" in
  --section7-only) MODE=section7-only ;;
  --controls|"")   MODE=all ;;
  *) echo "usage: $0 [--controls | --section7-only]" >&2; exit 2 ;;
esac

HERE=$(cd -- "$(dirname -- "$0")" && pwd)
DRIVER="$HERE/run_m6sr_b5.sh"
IMG_PINNED=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
MESH_SRC=/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse/constant/polyMesh
WORK=$(mktemp -d -t m6sr_launch_check.XXXXXX) || { echo "REFUSE: no scratch dir"; exit 2; }
trap 'rm -rf "$WORK"' EXIT

PASS=0; FAIL=0
ok(){   PASS=$((PASS+1)); printf '  PASS  %s\n' "$1"; }
bad(){  FAIL=$((FAIL+1)); printf '  FAIL  %s\n' "$1"; }
# THE REFUSAL GOES TO **stderr**, AND THAT IS LOAD-BEARING, NOT COSMETIC.  MEASURED DEFECT
# REPAIRED HERE (2026-09-04): `refuse` inside `$( )` exits only the SUBSHELL, so with the
# message on stdout `X=$(extract_line …)` CAPTURED THE REFUSAL TEXT AS X and the suite carried
# on.  Three mutations that DELETED an extracted line from the driver were still killed -- but
# downstream, by an `eval` of that text, reporting "the driver's head reader did not separate
# them" when the truth was "the driver's head reader is GONE".  A control that fails for the
# wrong reason names the wrong defect, and the next reader debugs the wrong file.  On stderr
# the text can never become a value, and every extraction below is `|| exit 2`.
refuse(){ printf 'REFUSE: %s\n' "$1" >&2; exit 2; }

# ---------------------------------------------------------------------------------------
# 0.  PRECONDITIONS.  Each is a REFUSAL, never a skip that prints green.
# ---------------------------------------------------------------------------------------
[ -f "$DRIVER" ] || refuse "the driver under test is ABSENT: $DRIVER"
[ -d "$MESH_SRC" ] || refuse "the L3 mesh source is ABSENT: $MESH_SRC (read-only tree)"
# THE CONTAINER PRECONDITIONS ARE REQUIRED ONLY BY THE TESTS THAT START A CONTAINER.  In
# `--section7-only` they are not checked because nothing that runs will use them -- and the
# tests that need them are not run either, so nothing is being skipped silently.
if [ "$MODE" != "section7-only" ]; then
  DOCKER_BIN=$(command -v docker 2>/dev/null)
  [ -n "$DOCKER_BIN" ] || refuse "docker does not resolve on PATH"
  docker inspect --format '{{.Id}}' "$IMG_PINNED" >/dev/null 2>&1 \
    || refuse "the PINNED IMAGE $IMG_PINNED is not on this daemon. This suite does NOT fall back to a mock: a mock proves nothing here."
  BARE_OUT=$(docker version --format '{{.Server.Version}}' 2>&1); BARE_RC=$?
  if [ $BARE_RC -eq 0 ]; then DOCKER_BRANCH=bare; else DOCKER_BRANCH=sg; fi
fi

# ---------------------------------------------------------------------------------------
# 1.  EXTRACT THE REPAIRED CONSTRUCTS FROM THE DRIVER ITSELF.
#     Function bodies are taken by their `name(){` .. `}` boundaries; the extraction is then
#     REQUIRED to be non-empty and to parse, because a silently empty extraction would make
#     every test below vacuously green.
# ---------------------------------------------------------------------------------------
# EVERY EXTRACTION AND EVERY COUPLING ASSERTION READS THE DRIVER'S **CODE**, NOT ITS PROSE.
# This is not a stylistic preference, it is a repaired defect in THIS FILE: the first version
# of these checks asserted the driver still contained `chmod g+rwX "$CASE"` with a plain grep
# over the whole file, and a MUTATION THAT DELETED THAT LINE FROM THE CODE STILL PASSED --
# because the driver's own EXPLANATORY COMMENT quotes the same string.  The control was being
# satisfied by the sentence describing the fix instead of by the fix.  Full-comment lines are
# stripped here so an assertion cannot be met by a comment.
CODE="$WORK/driver_code.sh"
grep -vE '^[[:space:]]*#' "$DRIVER" > "$CODE"
[ -s "$CODE" ] || refuse "stripping comments left no code -- the extraction is broken"

extract_fn(){ awk -v f="$1" '$0 ~ "^"f"\\(\\)\\{" {p=1} p {print} p && /^\}/ {exit}' "$DRIVER"; }

# Pull exactly ONE code line matching a pattern, so the suite EXECUTES the driver's own text
# rather than a re-typed copy of it.  Zero matches or several are both REFUSALS: a re-typed
# copy would keep passing after the driver stopped doing the thing.
extract_line(){
  local n; n=$(grep -cE "$1" "$CODE")
  [ "$n" = "1" ] || refuse "expected exactly ONE code line matching /$1/ in $DRIVER, found $n. This suite EXECUTES the driver's own line; it will not substitute its own."
  grep -E "$1" "$CODE"
}

# T0.  THE SUITE'S OWN REFUSAL MECHANISM IS PLANTED AND READ BACK BEFORE ANYTHING RESTS ON IT.
# Every coupling assertion below is `X=$(extract_line …) || exit 2`, which is only a refusal if
# an unmatchable pattern really does yield rc 2 AND NO VALUE.  Rule 3 applied to the machinery
# rather than to the measurement: a refuser not shown able to refuse is not a refuser.
_X=$(extract_line '^__M6SR_NO_SUCH_CODE_LINE__' 2>/dev/null); _XRC=$?
{ [ "$_XRC" = "2" ] && [ -z "$_X" ]; } \
  || refuse "THE SUITE'S OWN REFUSAL MECHANISM IS BROKEN: an unmatchable extraction returned rc '$_XRC' and value '${_X:-<empty>}'. It must return rc 2 and NOTHING. A refusal captured as a VALUE is not a refusal -- it becomes the thing the caller then evaluates. Every coupling assertion below rests on this, so the suite REFUSES rather than run them."
echo "refusal mechanism: an unmatchable extraction returns rc 2 and no value (planted, read back)"

{ extract_fn docker_q; echo; extract_fn docker_timeout_q; echo; extract_fn run_in_container; } \
  > "$WORK/fns.sh"
for F in docker_q docker_timeout_q run_in_container; do
  grep -q "^$F(){" "$WORK/fns.sh" || refuse "could not extract $F() from $DRIVER -- an empty extraction would make this suite vacuously green"
done
bash -n "$WORK/fns.sh" || refuse "the extracted functions do not parse"

# ITEM 30, HALF (ii): the container's supplementary group.  The GID IS TAKEN FROM THE
# DRIVER'S OWN ASSIGNMENT and evaluated here -- not recomputed as `id -g`.  A suite that
# computed its own gid would stay green after the driver started passing a wrong one, and a
# mutation setting the driver's HOST_GID to 65534 DID survive an earlier version of this file
# for exactly that reason.
HOST_GID_LINE=$(extract_line '^HOST_UID=\$\(id -u\); HOST_GID=') || exit 2
eval "$HOST_GID_LINE"
[ -n "$HOST_GID" ] || refuse "the driver's HOST_GID assignment evaluated to nothing"
grep -qE -- '--group-add "\$HOST_GID"' "$CODE" \
  || refuse "the driver's CODE no longer passes \`--group-add \"\$HOST_GID\"\`; this suite would be testing something the driver does not do"

# ITEM 30, HALF (i): the case-directory chmod.  The DRIVER'S OWN LINE is extracted and run,
# so deleting it from the driver stops this suite rather than leaving it green.
CHMOD_LINE=$(extract_line '^[[:space:]]*chmod g\+rwX "\$CASE"') || exit 2
apply_case_perm(){ CASE="$1"; eval "$CHMOD_LINE"; }

echo "docker branch on this box: $DOCKER_BRANCH (bare rc=$BARE_RC), host gid $HOST_GID (from the driver's own assignment)"

say(){ :; }
abort(){ echo "ABORT: $1" >> "$CASE/.abort"; exit "${2:-1}"; }

# ITEM 32's REPAIR puts the wrapper's log at `$RR/_wrapper_logs/$LEVEL/log.$tag`, so the
# extracted function needs a run root and a level.  BOTH ARE SCRATCH.  $WORK/rr is NOT
# verification/runs/M6SR_runs -- this suite never writes into the registered run root, whose
# ABSENCE is this registration's own rule-2 freeze proof.
RR="$WORK/rr"; LEVEL=probe
mkdir -p "$RR" || refuse "could not create the scratch run root $RR"
. "$WORK/fns.sh"

# =======================================================================================
# T6  ITEM 47 -- THE LAUNCH PATH ITSELF REFUSES.  FOUR MUTANTS AND THE CLEAN TWIN.
#
# WHAT IS BEING PROVED, AND WHAT WOULD NOT HAVE BEEN ENOUGH.  Amendment 19 already proved
# that `gate_a()` RETURNS `BLOCKED` for each of Section 7's conditions 2-5 (controls
# C25-C28).  THAT IS NOT THIS.  This drives THE DRIVER'S OWN `section7_launch_screen()`,
# extracted from run_m6sr_b5.sh's code, against a level planted to fail each clause, and
# requires that THE SOLVE DOES NOT START -- observed as the ABSENCE of a marker that stands
# in for the solver invocation.
#
# THE NEGATIVE TWIN IS WHAT MAKES THE POSITIVES MEAN ANYTHING (standing rule 3).  An absent
# marker proves nothing unless the same harness has been shown able to PRODUCE one, so a
# CLEAN level is driven through the identical path and MUST reach the marker.  A screen
# wired to refuse unconditionally would pass all four mutants and fail here.
#
# THE MARKER IS A STAND-IN AND IS LABELLED AS ONE.  It is not rhoSimpleFoam; no solver runs
# in this suite.  What makes the stand-in load-bearing is T6f, which asserts on the DRIVER'S
# OWN comment-stripped code that the screen's invocation sits AFTER B4's checkMesh and
# BEFORE the real `mpirun ... rhoSimpleFoam` line.  Position in the real file plus behaviour
# in the harness is the pair; neither alone would do.
# =======================================================================================
echo
echo "=== T6  ITEM 47.  A BLOCKED SECTION 7 SCREEN REFUSES THE SOLVE ON THE LAUNCH PATH ==="

extract_fn section7_launch_screen > "$WORK/s7fn.sh"
grep -q '^section7_launch_screen(){' "$WORK/s7fn.sh" \
  || refuse "could not extract section7_launch_screen() from $DRIVER -- an empty extraction would make every T6 limb vacuously green"
bash -n "$WORK/s7fn.sh" || refuse "the extracted section7_launch_screen() does not parse"

# T6a  THE CONTAINER-CAP CLASS (ITEM 39) CANNOT REACH THIS SCREEN.  Item 39 measured that an
# outer `timeout` does not bound a CONTAINER, because the client returns while dockerd keeps
# the container alive outside the timeout's process group.  The bound on this screen is that
# it starts no container at all, and that is asserted on the extracted TEXT rather than
# claimed in a comment -- comments are stripped from $CODE for exactly this reason.
S7_CODE=$(grep -vE '^[[:space:]]*#' "$WORK/s7fn.sh")
case "$S7_CODE" in
  *docker*|*run_in_container*)
    bad "T6a the screen's code mentions docker or run_in_container, so item 39's unbounded-container class reaches it and the 120 s cap is not a cap" ;;
  *)
    ok "T6a the screen starts NO CONTAINER (no 'docker', no 'run_in_container' in its extracted code), so it is an ordinary child of this shell's process group and \`timeout -k\` does bound it -- item 39's finding is about containers and does not reach here" ;;
esac
case "$S7_CODE" in
  *"timeout -k 5 120 python3"*)
    ok "T6a' and it IS capped: the driver's own line is \`timeout -k 5 120 python3\`, with -k so a process ignoring SIGTERM is still killed" ;;
  *) bad "T6a' the screen's code carries no \`timeout -k 5 120 python3\` cap" ;;
esac
case "$S7_CODE" in
  *"124|137)"*) ok "T6a'' and a capped screen FAILS CLOSED: rc 124/137 is an explicit refusal branch, not a fall-through" ;;
  *) bad "T6a'' the screen has no 124/137 branch, so a timeout would fall to an unhandled rc" ;;
esac

# ---- THE FIXTURES.  Built by the COMPARATOR'S OWN registered fixture writer and planted with
# the COMPARATOR'S OWN registered plant constants, imported from the module.  Re-typing either
# here would let this suite stay green after the comparator's fixtures or plants changed.
python3 - "$WORK/s7cases" "$HERE" <<'PYEOF' || refuse "could not build the Section 7 launch-path fixtures"
import os, sys
root, here = sys.argv[1], sys.argv[2]
sys.path.insert(0, here)
import analyse_m6sr as A

CLEAN_NAMES = [("wing", "wall"), ("inout", "patch"), ("sym", "symmetry")]
WRONG = [(A.PLANT_S7_WRONG_NAMES[0], "wall"), (A.PLANT_S7_WRONG_NAMES[1], "patch"),
         (A.PLANT_S7_WRONG_NAMES[2], "symmetry")]
cm = A._S7_CLEAN_CM
plants = {
    "clean": (cm, CLEAN_NAMES),
    "a10":   (cm.replace("Boundary openness (2.99162e-17 4.31794e-16 -8.22572e-16)",
                         "Boundary openness (2.99162e-17 %.6e -8.22572e-16)"
                         % A.PLANT_S7_OPENNESS), CLEAN_NAMES),
    "a11":   (cm.replace("Number of regions: 1 (OK).",
                         "Number of regions: %d (OK)." % A.PLANT_S7_N_REGIONS), CLEAN_NAMES),
    "a12":   (cm.replace("Min volume = 1.17547e-10.",
                         "Min volume = %.6e." % A.PLANT_S7_MIN_VOLUME), CLEAN_NAMES),
    "a13":   (cm, WRONG),
}
for tag, (text, names) in plants.items():
    d = os.path.join(root, tag)
    pm = os.path.join(d, "constant", "polyMesh")
    os.makedirs(pm, exist_ok=True)
    A._write(os.path.join(d, "log.checkMesh"), text)
    A._write(os.path.join(pm, "boundary"),
             A._s7_boundary_text(names, A.A4_CELLS[1] // A.A6_CELLS_PER_WING_FACE))
    A._write(os.path.join(pm, "points"), "1\n(\n(0.0 0.0 0.0)\n)\n")
print("fixtures written under", root)
PYEOF

# ---- THE DRIVER-SHAPED HARNESS.  The screen, then the line that stands for the solve.  The
# extracted `abort` exits, so the marker is reached ONLY if the screen returned.
CASES="$HERE"
. "$WORK/s7fn.sh"
drive(){   # $1 = fixture tag, $2 = level id.  -> rc; SOLVER_STARTED iff the solve was reached
  local d="$WORK/s7cases/$1"
  rm -f "$d/SOLVER_STARTED" "$d/.abort"
  ( CASE="$d"; LEVEL="$2"
    section7_launch_screen "$2" "$d"
    : > "$d/SOLVER_STARTED"        # STANDS FOR the solver line; no solver runs in this suite
  ) > "$d/harness.out" 2>&1
  return $?
}

# ---- T6b  THE NEGATIVE TWIN, FIRST, because the four positives are worthless without it.
drive clean L2; T6_CLEAN_RC=$?
if [ "$T6_CLEAN_RC" = "0" ] && [ -f "$WORK/s7cases/clean/SOLVER_STARTED" ]; then
  ok "T6b THE CLEAN TWIN STILL REACHES THE SOLVER LINE: the screen returned rc 0 and the marker standing for the solve was written. The four refusals below are therefore refusals of a SPECIFIC defect and not of everything"
else
  bad "T6b the clean level did NOT reach the solver line (rc '$T6_CLEAN_RC', marker $( [ -f "$WORK/s7cases/clean/SOLVER_STARTED" ] && echo present || echo ABSENT )). Every T6c limb below is WITHOUT EVIDENTIAL VALUE while this fails: a screen that refuses everything refuses the mutants too"
fi

# ---- T6c  THE FOUR MUTANTS.  Each must (i) exit 11, (ii) leave NO solver marker, and
# (iii) name ITS OWN clause with the measured value against the threshold -- not a bare
# verdict string, which is the specific thing the supervisor's ruling forbids.
for M in a10:S7_C2_boundary_openness_le_1e-12 \
         a11:S7_C3_number_of_regions_equals_1 \
         a12:S7_C4_min_cell_volume_strictly_positive \
         a13:S7_C5_patch_names_match_the_registered_per_level_set; do
  TAG=${M%%:*}; CLAUSE=${M#*:}
  drive "$TAG" L2; RC=$?
  D="$WORK/s7cases/$TAG"
  MARK=$( [ -f "$D/SOLVER_STARTED" ] && echo PRESENT || echo ABSENT )
  MSG=$(cat "$D/.abort" 2>/dev/null)
  NAMED=no
  case "$MSG" in *"$CLAUSE"*) NAMED=yes ;; esac
  # THE VALUE-AGAINST-THRESHOLD REQUIREMENT.  A13 is a NAME set, so it names both sets rather
  # than a value and a threshold; the other three must carry both.
  QUANT=no
  case "$TAG" in
    a13) case "$MSG" in *"expected="*) case "$MSG" in *"actual="*) QUANT=yes ;; esac ;; esac ;;
    *)   case "$MSG" in *"value="*) case "$MSG" in *"threshold="*|*"test="*|*"required="*) QUANT=yes ;; esac ;; esac ;;
  esac
  if [ "$RC" = "11" ] && [ "$MARK" = "ABSENT" ] && [ "$NAMED" = "yes" ] && [ "$QUANT" = "yes" ]; then
    ok "T6c/$TAG THE SOLVE DID NOT START: exit 11, no solver marker, and the refusal NAMES $CLAUSE with its measured value against its threshold"
  else
    bad "T6c/$TAG expected exit 11 with no solver marker and a message naming $CLAUSE quantitatively; got rc '$RC', marker $MARK, clause named=$NAMED, value-vs-threshold=$QUANT. Message: ${MSG:-<none>}"
  fi
done

# ---- T6d  A REFUSAL IS A REFUSAL AND IS NOT CONVERTED INTO `BLOCKED`.  An unregistered level
# is a statement about THE DOCUMENT, not about any mesh, and it must stop the launch under its
# OWN code.  Driven on the CLEAN fixture, so the only thing that differs is the level id.
drive clean L0_NOT_A_REGISTERED_LEVEL; T6D_RC=$?
T6D_MSG=$(cat "$WORK/s7cases/clean/.abort" 2>/dev/null)
T6D_MARK=$( [ -f "$WORK/s7cases/clean/SOLVER_STARTED" ] && echo PRESENT || echo ABSENT )
case "$T6D_MSG" in *"REFUSAL IS NOT A 'BLOCKED'"*) T6D_NAMED=yes ;; *) T6D_NAMED=no ;; esac
{ [ "$T6D_RC" = "12" ] && [ "$T6D_MARK" = "ABSENT" ] && [ "$T6D_NAMED" = "yes" ]; } \
  && ok "T6d an UNREGISTERED level stops the launch at exit 12 -- a DIFFERENT code from BLOCKED's 11 -- and the message says in terms that a refusal is not a BLOCKED. The solve did not start" \
  || bad "T6d expected exit 12, no solver marker and a refusal message; got rc '$T6D_RC', marker $T6D_MARK, named=$T6D_NAMED"
rm -f "$WORK/s7cases/clean/SOLVER_STARTED"

# ---- T6e  AND THE CLEAN TWIN AGAIN AFTER THE MUTANTS, on the SAME harness, so the four
# refusals cannot be an artifact of the harness degrading as it goes.
drive clean L2; T6E_RC=$?
{ [ "$T6E_RC" = "0" ] && [ -f "$WORK/s7cases/clean/SOLVER_STARTED" ]; } \
  && ok "T6e the clean twin STILL reaches the solver line after all five refusals -- the harness did not simply stop working" \
  || bad "T6e the clean twin no longer reaches the solver line (rc '$T6E_RC') -- the refusals above may be harness decay, not screening"

# ---- T6f  THE STEP ORDER, ASSERTED ON THE DRIVER'S OWN COMMENT-STRIPPED CODE.  This is what
# makes T6b/T6e's marker a stand-in for the SOLVE and not merely for the next line of a test.
S7_CALL_LN=$(grep -n '^section7_launch_screen "\$LEVEL" "\$CASE"' "$CODE" | cut -d: -f1)
CHECKMESH_LN=$(grep -n 'run_in_container checkMesh' "$CODE" | cut -d: -f1)
# THE CODE CARRIES MORE THAN ONE `mpirun ... rhoSimpleFoam` LINE, so the EARLIEST is taken --
# the strictest reading, and the only one that means "before ANY solver invocation".  A
# `tail -1` here would have compared against the LAST one and passed a screen sitting between
# two solver lines.  The count is reported so a reader is not left guessing which was used.
SOLVER_ALL=$(grep -n 'mpirun -np \$RANKS rhoSimpleFoam' "$CODE" | cut -d: -f1 | sort -n)
SOLVER_N=$(printf '%s\n' "$SOLVER_ALL" | grep -c '[0-9]')
SOLVER_LN=$(printf '%s\n' "$SOLVER_ALL" | head -1)
if [ -z "$S7_CALL_LN" ] || [ -z "$CHECKMESH_LN" ] || [ -z "$SOLVER_LN" ]; then
  bad "T6f could not locate all three of the screen call ('${S7_CALL_LN:-none}'), B4's checkMesh ('${CHECKMESH_LN:-none}') and the solver line ('${SOLVER_LN:-none}') in the driver's code"
elif [ "$CHECKMESH_LN" -lt "$S7_CALL_LN" ] && [ "$S7_CALL_LN" -lt "$SOLVER_LN" ]; then
  ok "T6f THE SCREEN SITS BETWEEN THEM IN THE DRIVER'S OWN CODE: checkMesh at code line $CHECKMESH_LN < the screen at $S7_CALL_LN < the EARLIEST of $SOLVER_N \`mpirun ... rhoSimpleFoam\` lines, at $SOLVER_LN. Section 7 is read from checkMesh output, so it CANNOT run earlier, and it refuses before a core-minute of solve is spent"
else
  bad "T6f the ordering is wrong: checkMesh $CHECKMESH_LN, screen $S7_CALL_LN, solver $SOLVER_LN"
fi

# ---- T6g  AND THE SCREEN IS ACTUALLY CALLED, exactly once, at top level.
S7_CALLS=$(grep -c '^section7_launch_screen "\$LEVEL" "\$CASE"' "$CODE")
[ "$S7_CALLS" = "1" ] \
  && ok "T6g the driver's code calls the screen exactly once at top level -- item 47 was a screen that existed and was never invoked, so 'defined' is not the test" \
  || bad "T6g expected exactly one top-level call to section7_launch_screen, found $S7_CALLS"

# =======================================================================================
# T7  ITEM 48 -- THE RULED STEP ORDER, AND THE GUARD THAT KEEPS THE AGE GUARD NON-VACUOUS.
#
# Section 19.3 ruled `B3` -> `B3c` -> `B4` -> `B5` and NOTHING IMPLEMENTED IT: `B3c` existed
# in the registration, in its cost table and in two later amendments' disclaimers, and in no
# executable.  Amendment 21 places it -- but SPLIT, because moving the WHOLE case write up
# would have laid `0/U` at stage time and made rule 4's age guard PASS UNCONDITIONALLY.
#
# THIS LIMB IS THE ORDERING AND THE GUARD, ON THE DRIVER'S OWN CODE.  The BEHAVIOURAL half
# -- that `pre-check` writes no `0/` and `zero` lays the anchor last -- is controls W6 and W7
# in `write_m6sr_case.py --selftest`, driven on a real mesh, and is NOT duplicated here.
# =======================================================================================
echo
echo "=== T7  ITEM 48.  THE RULED STEP ORDER B3c -> B4 -> B4s -> B3z -> SOLVER ==="
ln_of(){ grep -n "$1" "$CODE" | cut -d: -f1 | sort -n | head -1; }
L_B3C=$(ln_of 'phase pre-check')
L_B4=$(ln_of 'run_in_container checkMesh')
L_B4S=$(ln_of '^section7_launch_screen "\$LEVEL" "\$CASE"')
L_B3Z=$(ln_of 'phase zero')
L_SOLVE=$(ln_of 'mpirun -np \$RANKS rhoSimpleFoam')
if [ -z "$L_B3C" ] || [ -z "$L_B4" ] || [ -z "$L_B4S" ] || [ -z "$L_B3Z" ] || [ -z "$L_SOLVE" ]; then
  bad "T7a could not locate all five steps in the driver's code: B3c='${L_B3C:-none}' B4='${L_B4:-none}' B4s='${L_B4S:-none}' B3z='${L_B3Z:-none}' solver='${L_SOLVE:-none}'"
elif [ "$L_B3C" -lt "$L_B4" ] && [ "$L_B4" -lt "$L_B4S" ] && [ "$L_B4S" -lt "$L_B3Z" ] && [ "$L_B3Z" -lt "$L_SOLVE" ]; then
  ok "T7a THE RULED ORDER HOLDS IN THE DRIVER'S OWN CODE: B3c $L_B3C < B4 checkMesh $L_B4 < B4s $L_B4S < B3z $L_B3Z < solver $L_SOLVE. B3c is what gives checkMesh a system/ to read; B3z is DELIBERATELY last so rule 4's anchor dates the launch being graded"
else
  bad "T7a the ruled order is broken: B3c $L_B3C, B4 $L_B4, B4s $L_B4S, B3z $L_B3Z, solver $L_SOLVE"
fi

# ---- T7b  B3c MUST NOT write 0/, and the driver REFUSES if it ever does.  This is the
# anti-vacuity guard: a 0/U written at stage time predates every field the solve writes, so
# rule 4's age guard would pass unconditionally while still reporting green.
if grep -qE '^[[:space:]]*\[ -d "\$CASE/0" \][[:space:]]*\\?$' "$CODE" \
   && grep -q 'B3c wrote \$CASE/0' "$CODE"; then
  ok "T7b the driver carries its own refusal if B3c ever writes 0/ -- the anti-vacuity guard is in the CODE, not only in a comment (comments are stripped from \$CODE)"
else
  bad "T7b the driver's code carries no refusal against B3c writing 0/; a future edit could make rule 4's age guard vacuous with nothing to stop it"
fi

# ---- T7c  THE TWO PHASES ARE THE ONE REGISTERED WRITER, not a second one.
W_INVOKE=$(grep -c 'write_m6sr_case.py' "$CODE")
W_PRE=$(grep -c 'write_m6sr_case.py.*--phase pre-check' "$CODE")
W_ZERO=$(grep -c 'write_m6sr_case.py.*--phase zero' "$CODE")
W_ALL=$(grep -c 'write_m6sr_case.py.*--phase all' "$CODE")
# THE PHASE NAMES ARE CHECKED, NOT MERELY THE PRESENCE OF `--phase`.  `--phase all` at B3c
# would write 0/ AT STAGE TIME and make rule 4's age guard vacuous -- the exact substitution
# this split exists to prevent -- and it would satisfy a test that only counted `--phase`.
if [ "$W_PRE" = "1" ] && [ "$W_ZERO" = "1" ] && [ "$W_ALL" = "0" ]; then
  ok "T7c both case writes go through the ONE registered writer, as EXACTLY ONE --phase pre-check and EXACTLY ONE --phase zero, with NO --phase all on the launch path (of $W_INVOKE total references). Section 8's single-writer rule is unbroken and the vacuity substitution is excluded by name"
else
  bad "T7c expected exactly one --phase pre-check, one --phase zero and NO --phase all; found pre-check=$W_PRE zero=$W_ZERO all=$W_ALL. A --phase all at B3c would lay 0/U at stage time and make rule 4's age guard pass unconditionally"
fi

if [ "$MODE" = "section7-only" ]; then
  echo
  echo "SECTION-7-ONLY MODE.  NOT RUN, AND NAMED RATHER THAN SILENTLY SKIPPED:"
  echo "  T1  the container known-positive plant (items 28/30)      -- REQUIRES A CONTAINER"
  echo "  T2  the bare-branch argv defect (item 28)                 -- REQUIRES A CONTAINER"
  echo "  T3  the case-permission halves (item 30)                  -- REQUIRES A CONTAINER"
  echo "  T4  the missing-controlDict chain (item 31)               -- REQUIRES A CONTAINER"
  echo "  T5  the graded-artifact head corruption (item 32/34)      -- REQUIRES A CONTAINER"
  echo "THIS MODE REPORTS NOTHING ABOUT THOSE FIVE. A pass here is a pass for T0, T6 and T7 ONLY."
  echo
  echo "checks passed: $PASS   FAILED: $FAIL"
  [ "$FAIL" -eq 0 ] || exit 1
  exit 0
fi

# ---------------------------------------------------------------------------------------
# 2.  CASE BUILDERS.
# ---------------------------------------------------------------------------------------
mk_mesh_only(){ # $1=dir  $2=umask -- a case with a mesh and NO system/ (what B4 sees today)
  rm -rf "$1"; ( umask "$2"; mkdir -p "$1/constant" ) || return 1
  cp -a -- "$MESH_SRC" "$1/constant/polyMesh"; }
mk_complete(){  # $1=dir  $2=umask -- mesh AND Section 8's case files
  mk_mesh_only "$1" "$2" || return 1
  python3 "$HERE/write_m6sr_case.py" --case "$1" --level L3 > "$1/log.write_case" 2>&1; }

echo
echo "=== T1  KNOWN-POSITIVE (rule 3).  The container CAN run and CAN write. ==="
# The plant is generated per run so a stale file cannot supply it.
PLANT="M6SR-PLANT-$$-$(date +%s%N)"
CASE="$WORK/t1"
mk_complete "$CASE" 0002 || refuse "could not build the complete case for T1"
apply_case_perm "$CASE"
( run_in_container checkMesh 300 1 \
    "checkMesh -constant > log.checkMesh 2>&1; echo '$PLANT' > PLANT_READBACK.txt" ) >/dev/null 2>&1
T1_INNER=$(cat "$CASE/INNER_RC_checkMesh.txt" 2>/dev/null)
T1_SEEN=$(cat "$CASE/PLANT_READBACK.txt" 2>/dev/null)
[ "$T1_SEEN" = "$PLANT" ] \
  || refuse "THE PLANT WAS NOT SEEN. The container was asked to write '$PLANT' into \$CASE and this reader read '${T1_SEEN:-<nothing>}' back off disk. A reader not shown able to see a success cannot be trusted to report a failure, so every negative limb below is WITHOUT EVIDENTIAL VALUE and this suite REFUSES rather than printing them (standing rule 3)."
echo "  plant seen off disk: $T1_SEEN"
[ "$T1_INNER" = "0" ] && ok "T1a container ran and returned inner rc 0" \
                      || bad "T1a expected inner rc 0, got '${T1_INNER:-ABSENT}'"
[ -s "$CASE/log.checkMesh" ] && ok "T1b log.checkMesh written ($(wc -c < "$CASE/log.checkMesh") bytes) by uid $(stat -c '%u' "$CASE/log.checkMesh")" \
                             || bad "T1b log.checkMesh ABSENT or empty"
grep -q '^Mesh OK\.' "$CASE/log.checkMesh" 2>/dev/null \
  && ok "T1c log.checkMesh reports 'Mesh OK.' -- Gate A has numeric maxima to read" \
  || bad "T1c log.checkMesh does not report 'Mesh OK.'"
grep -q "docker_branch=$DOCKER_BRANCH" "$CASE/STEP_RC.txt" 2>/dev/null \
  && ok "T1d the invocation branch is RECORDED in the run's own STEP_RC.txt" \
  || bad "T1d the invocation branch is NOT recorded in STEP_RC.txt"
# The wrapper-log path is taken FROM THE DRIVER'S OWN RECORD, never recomputed here: a suite
# that recomputed it would keep passing after the driver started writing somewhere else.
T1_WLOG=$(sed -n 's/.*[[:space:]]wrapper_log=\([^[:space:]]*\).*/\1/p' "$CASE/STEP_RC.txt" 2>/dev/null | tail -1)
[ -n "$T1_WLOG" ] && ok "T1e the driver RECORDS where it put the wrapper log: $T1_WLOG" \
                  || bad "T1e STEP_RC.txt carries no wrapper_log= field, so nothing states where the outer wrapper's output went"
case "$T1_WLOG" in
  "$CASE"|"$CASE"/*) bad "T1f the wrapper log is INSIDE the bind mount $CASE -- item 32's collision is reachable" ;;
  "") bad "T1f no wrapper-log path to test" ;;
  *) ok "T1f the wrapper log is OUTSIDE the bind mount $CASE, so no container write can address that inode" ;;
esac

echo
echo "=== T2  ITEM 28.  The FROZEN form is broken on the branch this box takes. ==="
if [ "$DOCKER_BRANCH" = "bare" ]; then
  DRUN=docker
  OUT=$(timeout 60s $DRUN "docker run --rm -u 1002:1002 $IMG_PINNED bash -c 'echo INSIDE_OK'" 2>&1); RC=$?
  { [ $RC -ne 0 ] && printf '%s' "$OUT" | grep -q 'unknown command'; } \
    && ok "T2a frozen \$DRUN form on the bare branch FAILS as recorded (rc $RC, 'unknown command')" \
    || bad "T2a frozen form did NOT fail as item 28 records (rc $RC): $OUT"
else
  ok "T2a SKIPPED-BY-BRANCH: this box is on the '$DOCKER_BRANCH' branch, where the frozen form was already correct"
fi
OUT=$(docker_timeout_q 60 run --rm -u 1002:1002 "$IMG_PINNED" bash -c 'echo INSIDE_OK' 2>&1); RC=$?
{ [ $RC -eq 0 ] && [ "$OUT" = "INSIDE_OK" ]; } \
  && ok "T2b REPAIRED form works on the '$DOCKER_BRANCH' branch (rc 0, INSIDE_OK)" \
  || bad "T2b repaired form failed on the '$DOCKER_BRANCH' branch (rc $RC): $OUT"
docker_timeout_q 5 run --rm -u 1002:1002 "$IMG_PINNED" bash -c 'sleep 30' >/dev/null 2>&1
[ $? -eq 124 ] && ok "T2c the structural cap still BITES through the repaired form (rc 124), so the exit-6 overrun path survives" \
               || bad "T2c a 30 s container under a 5 s cap did not return 124 -- rule 12's structural cap is not enforced"

echo
echo "=== T3  ITEM 30.  Each half of the repair is NECESSARY. ==="
CASE="$WORK/t3a"; mk_mesh_only "$CASE" 0002
docker_timeout_q 120 run --rm -u 1002:1002 -v "$CASE":/case -w /case "$IMG_PINNED" \
    bash -c 'echo probe > log.perm' >/dev/null 2>&1
[ -f "$CASE/log.perm" ] && bad "T3a the container wrote into a 775 host-owned dir with NO --group-add -- item 30's premise is wrong" \
                        || ok "T3a chmod-only (no --group-add): container CANNOT write -- half (ii) is necessary"
CASE="$WORK/t3b"; mk_mesh_only "$CASE" 0022
docker_timeout_q 120 run --rm -u 1002:1002 --group-add "$HOST_GID" -v "$CASE":/case -w /case "$IMG_PINNED" \
    bash -c 'echo probe > log.perm' >/dev/null 2>&1
[ -f "$CASE/log.perm" ] && bad "T3b the container wrote into a 755 dir with only --group-add -- half (i) would be unnecessary" \
                        || ok "T3b group-add-only on a 755 dir: container CANNOT write -- half (i) is necessary"
CASE="$WORK/t3c"; mk_mesh_only "$CASE" 0022; apply_case_perm "$CASE"
docker_timeout_q 120 run --rm -u 1002:1002 --group-add "$HOST_GID" -v "$CASE":/case -w /case "$IMG_PINNED" \
    bash -c 'echo probe > log.perm' >/dev/null 2>&1
[ -f "$CASE/log.perm" ] && ok "T3c BOTH halves, hostile umask 022: container CAN write -- the repair does not rest on the umask" \
                        || bad "T3c both halves under umask 022 still could not write"

echo
echo "=== T4  ITEM 31.  Reported, not repaired -- and there is no FOURTH failure behind it. ==="
CASE="$WORK/t4"; mk_mesh_only "$CASE" 0002; apply_case_perm "$CASE"
( run_in_container checkMesh 300 1 "checkMesh -constant > log.checkMesh 2>&1" ) >/dev/null 2>&1
T4_INNER=$(cat "$CASE/INNER_RC_checkMesh.txt" 2>/dev/null)
{ [ "$T4_INNER" = "1" ] && grep -q 'cannot find file .*system/controlDict' "$CASE/log.checkMesh" 2>/dev/null; } \
  && ok "T4a mesh-only case (what B4 sees TODAY): inner rc 1, log names system/controlDict -- item 31 is REAL and is an ORDERING defect" \
  || bad "T4a expected inner rc 1 naming system/controlDict; got inner '${T4_INNER:-ABSENT}'"
# T1 already ran the SAME step on a COMPLETE case and got inner rc 0 with 'Mesh OK.', which
# is the other limb: nothing further stands between B4 and a clean log once the case exists.
[ "$T1_INNER" = "0" ] \
  && ok "T4b same step, case written first: inner rc 0 -- NO FOURTH failure sits behind item 31" \
  || bad "T4b the complete-case limb did not return 0, so a fourth failure may sit behind item 31"

echo
echo "=== T5  ITEM 32 (registration item 34).  THE ONE THAT DID NOT FAIL CLOSED. ==="
# THE SHAPE: two writers, one path.  The container writes $CASE/log.checkMesh through the bind
# mount; the host shell holds an O_TRUNC fd on the SAME inode at offset 0 for the life of the
# docker client, so anything the client emits -- including the container's own UNREDIRECTED
# stdout, which the client streams back -- lands at OFFSET 0 and overwrites the HEAD.
#
# WHY EVERY ASSERTION BELOW IS ON THE HEAD AND NOT ON THE NUMBERS.  Gate A's named maxima and
# the `Mesh OK.` / `End` markers sit near the END of a checkMesh log and SURVIVE the overwrite
# untouched.  A control that asked "do the maxima still parse?" is precisely the control this
# defect passes.  So T5a REQUIRES the head to be seen corrupted, and T5b REQUIRES it intact.
#
# NEITHER LIMB IS A SOLVER RUN and neither touches B4's ledger: these are checkMesh invocations
# in $WORK, and $RR here is a scratch directory, not verification/runs/M6SR_runs.
NOISE="M6SR-CLIENT-NOISE-$$-$(date +%s%N)"
cm_maxima(){ python3 -c "
import sys
sys.path.insert(0, '$HERE')
import analyse_m6sr as A
d = A.read_checkmesh('$1')
print('%s|%s|%s' % (d.get('state'), d.get('max_non_orthogonality_deg'), d.get('max_skewness')))
" 2>/dev/null; }

# ---- T5a  THE KNOWN-POSITIVE, AND HERE THE KNOWN-POSITIVE IS THE CORRUPTION ITSELF.
# This limb deliberately re-creates the PRE-REPAIR shape.  It is typed here rather than
# extracted because the driver no longer contains it -- that is what the repair means -- and it
# is the only way to show that THIS reader can SEE a corrupted head.  If the head comes back
# intact, T5b's "the head is intact" says nothing, so the suite REFUSES rather than print it.
CASE="$WORK/t5a"; mk_complete "$CASE" 0002 || refuse "could not build the complete case for T5a"
apply_case_perm "$CASE"
{ docker_timeout_q 300 run --rm -u 1002:1002 --group-add "$HOST_GID" \
    -v "$CASE":/case -w /case "$IMG_PINNED" \
    bash -c "set +u; source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; checkMesh -constant > log.checkMesh 2>&1; printf '%s\n' '$NOISE'" ; } \
  > "$CASE/log.checkMesh" 2>&1
T5A_HEAD=$(head -c 3 "$CASE/log.checkMesh" 2>/dev/null)
T5A_FIRST=$(head -c ${#NOISE} "$CASE/log.checkMesh" 2>/dev/null)
T5A_GRADE=$(cm_maxima "$CASE/log.checkMesh")
[ "$T5A_FIRST" = "$NOISE" ] \
  || refuse "THE CORRUPTION COULD NOT BE REPRODUCED. The host-side writer's line '$NOISE' was expected AT OFFSET 0 of $CASE/log.checkMesh and the first ${#NOISE} bytes read '${T5A_FIRST:-<nothing>}'. A reader not shown able to see the corruption cannot be trusted to certify its absence, so T5b would be WITHOUT EVIDENTIAL VALUE and this suite REFUSES rather than printing it (standing rule 3)."
ok "T5a shared-path shape REPRODUCED on the pinned digest: the host-side line landed at OFFSET 0 and replaced the first ${#NOISE} bytes of the graded artifact"
case "$T5A_GRADE" in
  READ\|[0-9]*\|[0-9]*)
    ok "T5a' AND THE CORRUPTED FILE STILL GRADES: analyse_m6sr.read_checkmesh() returns state|max_non_orth|max_skew = $T5A_GRADE. It reads CLEAN, not ABSENT -- this is why the head is the assertion" ;;
  *) bad "T5a' the corrupted file did not grade ($T5A_GRADE); item 32's danger claim is not reproduced by the real reader" ;;
esac

# ---- T5b  THE REPAIR, THROUGH THE DRIVER'S OWN EXTRACTED FUNCTION.
CASE="$WORK/t5b"; mk_complete "$CASE" 0002 || refuse "could not build the complete case for T5b"
apply_case_perm "$CASE"
( run_in_container checkMesh 300 1 \
    "checkMesh -constant > log.checkMesh 2>&1; printf '%s\n' '$NOISE'" ) >/dev/null 2>&1
T5B_WLOG=$(sed -n 's/.*[[:space:]]wrapper_log=\([^[:space:]]*\).*/\1/p' "$CASE/STEP_RC.txt" 2>/dev/null | tail -1)
# NON-VACUITY FIRST.  If the host-side writer emitted nothing ANYWHERE, "the head is intact" is
# a statement about a collision that never happened.  The plant must be shown to have landed.
grep -q -- "$NOISE" "$T5B_WLOG" 2>/dev/null \
  || refuse "THE PLANTED HOST-SIDE WRITE WAS NOT SEEN. '$NOISE' was expected in the wrapper log the driver names in STEP_RC.txt ('${T5B_WLOG:-<no path recorded>}') and is not there. Both writers must be shown to have run, or 'the graded file's head is intact' is vacuous. REFUSED (standing rule 3)."
ok "T5b both writers ran: the container's checkMesh AND the host-side line, which landed in $T5B_WLOG"
T5B_HEAD=$(head -c 3 "$CASE/log.checkMesh" 2>/dev/null)
[ "$T5B_HEAD" = "/*-" ] \
  && ok "T5b' THE GRADED FILE'S HEAD IS INTACT: $CASE/log.checkMesh still opens with the OpenFOAM banner" \
  || bad "T5b' THE HEAD OF THE GRADED ARTIFACT WAS OVERWRITTEN: first 3 bytes read '${T5B_HEAD:-<nothing>}', not '/*-'. The maxima near the end of the file may well still parse -- that is exactly the failure this check exists to catch."
head -c 400 "$CASE/log.checkMesh" 2>/dev/null | grep -q -- "$NOISE" \
  && bad "T5b'' the host-side line appears in the first 400 bytes of the GRADED artifact" \
  || ok "T5b'' the host-side line appears NOWHERE in the graded artifact's head"
T5B_GRADE=$(cm_maxima "$CASE/log.checkMesh")
case "$T5B_GRADE" in
  READ\|[0-9]*\|[0-9]*) ok "T5b''' and it is a REAL checkMesh log, not an empty one passing a head test: $T5B_GRADE" ;;
  *) bad "T5b''' the repaired log does not grade ($T5B_GRADE) -- the head test above may be passing on a file with no content" ;;
esac
case "$T5B_WLOG" in
  "$CASE"|"$CASE"/*) bad "T5b'''' the wrapper log is inside the bind mount, so the separation is by name only" ;;
  *) ok "T5b'''' the wrapper log is OUTSIDE the bind mount -- the two writers are separated by MOUNT TOPOLOGY, not by a naming convention" ;;
esac

# ---- T5c  THE STRUCTURAL REFUSAL IS EXERCISED, NOT GREPPED.  Force the driver's own computed
# wrapper target back inside the mount and require it to REFUSE before starting a container.
CASE="$WORK/t5c"; mk_mesh_only "$CASE" 0002; apply_case_perm "$CASE"
( RR="$CASE"; LEVEL=x; run_in_container checkMesh 60 1 "true" ) >/dev/null 2>&1; T5C_RC=$?
{ [ "$T5C_RC" = "6" ] && grep -q 'INSIDE the bind mount' "$CASE/.abort" 2>/dev/null; } \
  && ok "T5c a wrapper target inside the mount REFUSES at exit 6 before the container starts -- the collision is closed for every future tag, not just for checkMesh" \
  || bad "T5c expected exit 6 and an 'INSIDE the bind mount' refusal; got rc '$T5C_RC'"

# ---- T5d  COUPLING TO THE DRIVER'S CODE, comment-stripped (see the note at section 1).
grep -qE '>[[:space:]]*"\$CASE/log\.\$tag"' "$CODE" \
  && bad "T5d the driver's CODE still sends the wrapper to \$CASE/log.\$tag -- the defect is back" \
  || ok "T5d the driver's CODE no longer sends the wrapper to \$CASE/log.\$tag"
if extract_line '^[[:space:]]*> "\$wlog" 2>&1$' >/dev/null 2>&1; then
  ok "T5d' the driver's CODE sends the wrapper to exactly ONE out-of-mount target"
else
  bad "T5d' the driver's CODE does not carry exactly one \`> \"\$wlog\"\` redirect"
fi

# ---- T5e  THE DRIVER'S SECOND GUARD -- ITS OWN head reader, extracted and run on BOTH files.
CM_LINE=$(extract_line '^[[:space:]]*CM_HEAD=\$\(head -c 3') || exit 2
CASE="$WORK/t5a"; eval "$CM_LINE"; T5E_BAD="$CM_HEAD"
CASE="$WORK/t5b"; eval "$CM_LINE"; T5E_GOOD="$CM_HEAD"
{ [ "$T5E_BAD" != "/*-" ] && [ "$T5E_GOOD" = "/*-" ]; } \
  && ok "T5e the driver's OWN B4 head reader separates the two files (corrupt '$T5E_BAD' vs clean '$T5E_GOOD'), so its refusal is not vacuous in either direction" \
  || bad "T5e the driver's head reader did not separate them (corrupt '$T5E_BAD', clean '$T5E_GOOD')"

echo
echo "checks passed: $PASS   FAILED: $FAIL"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
