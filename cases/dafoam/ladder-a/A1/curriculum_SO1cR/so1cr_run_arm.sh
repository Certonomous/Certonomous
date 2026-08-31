#!/usr/bin/env bash
# Curriculum SO-1cR arm launcher -- NACA0012 INCOMPRESSIBLE (DASimpleFoam),
# np-INVARIANCE OF THE GRADIENT **AT SO-1b's OPTIMUM**, ACROSS THE DECOMPOSITION
# **METHOD** AT FIXED np = 4, WITH THIS CONFIGURATION'S OWN FD TABLE BESIDE IT,
# ON TWO TOOLCHAIN ROWS.  The POST-OPTIMUM VERIFICATION rung of Sanaa's
# shape-optimisation ladder SO-1 (directives 2026-08-27T16:54Z section 4).
#
# DERIVED from `cases/dafoam/ladder-a/A1/curriculum_SO1a/so1a_run_arm.sh` with
# the REGISTERED DELTAS listed in PREREGISTRATION.md section 7 and recorded in
# so1cr_run_arm_DELTAS_from_so1a.diff:
#   * item/root names; forbidden roots extended with SO-1a's and SO-1b's;
#   * RANKS 4 ON EVERY SOLVER ARM (MESH stays at 1) -- the departure from SO-1a
#     and SO-1b that IS this item's subject, licensed by DAFOAM_CHARTER.md
#     section 5's "serial before parallel" now that SO-1a bought the serial
#     gradient and SO-1b bought the serial optimum;
#   * cpuset PER ARM (10 for MESH; 10,11,12,13 for the four np = 4 arms),
#     disjoint by registration from D6's 2,3,4,14, D4-SHIPPED's 5,6,7,9 and
#     SO-1a's / SO-1b's 9;
#   * TWO md5-pinned decomposeParDicts, overlaid PER ARM and re-asserted ON THE
#     OVERLAID COPY, because A4 measured a factor of 16,600 between `scotch` and
#     `simple 4x1x1` on one mesh at one np;
#   * G-OPTDEP -- an N arm consumes SO-1b's own-row optimum artefact or refuses;
#   * G-CAP-PREREG, inherited from SO-1b and re-pointed;
#   * G-CLOCK -- NEW, and the reason is at its own block below;
#   * the arm commands and the cap table.
# Container-printed strings (D4S_*) are inherited UNCHANGED so the grader greps
# what the launcher writes.
#
# THE AGE-GUARD DATUM IS RESOLVED BY EXISTENCE HERE TOO, AND ITS NAME IS RECORDED
# (the AV-1/AV-2 `0/U` vs `0/U.gz` defect).  AND THE AGE-CHECKED LIST CONTAINS
# ONLY WHAT THIS RUN PRODUCES: `so1b_E.json` is a STAGED INPUT, staged with
# `cp -a` BEFORE the age datum is touched, named in the pre-registration's
# STAGED INPUTS list, and EXCLUDED BY NAME from the grader's artefact list --
# `d4s_f3s_grade.py:61` listed the staged `OptView.hst` among its age-checked
# ARTEFACTS and made that clause unsatisfiable by construction, forcing
# D4S-F3S to NOT A RESULT with 19 of 20 gate readings passing.
#
# CAP DISCIPLINE.  The caps are NOT arguments.  They are constants in the table
# below, reproduced verbatim in PREREGISTRATION.md line 6's SO1CR-CAP-MANIFEST,
# and G-CAP-PREREG checks this launcher AGAINST THAT FROZEN LINE on two channels
# (disk, and `git show HEAD:`) before any container starts -- because SO-1a's
# D4_CAP_ASSERT checks the launcher against ITSELF by inverting its own
# arithmetic, and two numbers that agree with each other can both be wrong.
#
# `set -e` DOES NOT GATE at the top level of a harness Bash call and
# `( set -e; ... )` does not gate either.  Every step below gates explicitly
# with `|| { echo ABORT...; exit N; }`.
#
# 8.2: NO --rm, so `docker inspect .State.ExitCode/.State.OOMKilled` survives
# the arm and the KERNEL's verdict is read, not the harness's.
# the arm and the KERNEL's verdict is read, not the harness's.
set -uo pipefail

# ===========================================================================
# D4-LAUNCHER-DEF-1 -- THE DEFECT THIS FILE EXISTS NOT TO REPEAT.
#
# `curriculum_D4/d4_run_arm.sh` hardcodes BASE at the PATCHED item's run root
# (:25, no override), sets WORK="$BASE/$ARM" (:136) and runs an UNGUARDED
# `sudo -n rm -rf "$WORK"` (:139) for every arm except F.  Firing the SHIPPED
# row through it would have deleted
#   /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O
# -- 5,085 files, 384 MB, holding OptView.hst and opt_IPOPT.txt: THE ARTIFACTS
# D4's ACCEPTED `GATE REACHED` RESTS ON -- and appended its rows to the same
# ledger (:282), leaving two items interleaved in one file so that NEITHER row
# could be graded cleanly afterwards.  EIGHT launcher files in that directory
# carry the same hardcoded BASE.
#
# THE REPAIR IS NOT "CHANGE THE CONSTANT".  A constant that is merely different
# is one careless edit from being the same again.  The WRONG CONSTANT MUST
# REFUSE, and the guard below is DRIVEN AGAINST THE REAL D4 ROOT in
# `d4s_launcher_guard_selftest.sh` and shown to abort.  A guard not shown to
# fire is ceremony -- and this is the guard standing between a re-fire and
# 384 MB of irreplaceable graded evidence.
# ===========================================================================
ITEM=SO1cR
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO1cR-a1-naca0012-dragmin-npinv
BASE="${BASE:-$REGISTERED_BASE}"

# ---- G-ROOT.1 -- BASE must be THIS item's registered root, normalised, so a
# ---- trailing slash, a `.`, a `..` or a symlink cannot walk around the check.
BASE_REAL=$(realpath -m "$BASE")
REG_REAL=$(realpath -m "$REGISTERED_BASE")
if [ "$BASE_REAL" != "$REG_REAL" ]; then
  echo "ABORT G-ROOT.1 BASE is not this item's registered run root."
  echo "  given:      $BASE_REAL"
  echo "  registered: $REG_REAL"
  echo "  D4-LAUNCHER-DEF-1: a launcher pointed at another item's run root"
  echo "  deletes that item's graded arms.  REFUSED before any staging."
  exit 3
fi

# ---- G-ROOT.2 -- and NAME the roots that must never be written by this file,
# ---- so the abort says WHOSE evidence it just protected rather than only that
# ---- something did not match.  Explicit, because the specific message is what
# ---- a future reader in a hurry actually acts on.
FORBIDDEN_ROOTS="/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-R-a2-wing-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density
/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint
/home/ubuntu/certonomous-runs/CURRICULUM-D14-a2-wing-remesh
/home/ubuntu/certonomous-runs/CURRICULUM-D14M-a2-wing-remesh
/home/ubuntu/certonomous-runs/CURRICULUM-D7R-a3-m6-cdmin
/home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd
/home/ubuntu/certonomous-runs/CURRICULUM-D12R-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D12R2-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W2R-cylinder-unsteady
/home/ubuntu/certonomous-runs/CURRICULUM-D13-a1-basin-restart
/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic
/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic
/home/ubuntu/certonomous-runs/CURRICULUM-D17-cone-supersonic
/home/ubuntu/certonomous-runs/CURRICULUM-AV1-a1-naca0012-npinv
/home/ubuntu/certonomous-runs/CURRICULUM-AV2-a1-naca0012-duality
/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-a1-naca0012-dragmin-gradient
/home/ubuntu/certonomous-runs/CURRICULUM-SO1b-a1-naca0012-dragmin-opt
/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt
/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-dragmin-npinv
/home/ubuntu/certonomous-runs/A2-mach-wing
/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible
/home/ubuntu/dafoam-tutorials
/home/ubuntu/certonomous-runs
/home/ubuntu/Certonomous"
while IFS= read -r forb; do
  [ -z "$forb" ] && continue
  if [ "$BASE_REAL" = "$(realpath -m "$forb")" ]; then
    echo "ABORT G-ROOT.2 BASE resolves to ANOTHER ITEM'S RUN ROOT: $forb"
    echo "  That directory holds a graded row.  This launcher stages by"
    echo "  That launcher stages by removing the arm directory, so writing"
    echo "  there would destroy it.  REFUSED."
    exit 3
  fi
done <<< "$FORBIDDEN_ROOTS"

# ---- G-ROOT.3 -- the LEDGER must belong to this item and to no other.  A root
# ---- can be correct and its ledger still be a foreign one moved in.  D15
# ---- REGISTERED DELTA: this item BUYS BOTH ROWS, so a ROW=SHIPPED row is NOT
# ---- foreign here; only a foreign ITEM= line refuses.
if [ -f "$BASE/ledger.txt" ]; then
  FOREIGN_ITEM=$(grep -a "^ITEM=" "$BASE/ledger.txt" 2>/dev/null | grep -av "^ITEM=$ITEM$" | head -1)
  if [ -n "$FOREIGN_ITEM" ]; then
    echo "ABORT G-ROOT.3 the ledger at $BASE/ledger.txt carries another item: $FOREIGN_ITEM"
    echo "  Appending here would interleave two items' rows in one file and"
    echo "  neither row could be graded cleanly afterwards.  REFUSED."
    exit 3
  fi
fi
echo "D4S_G_ROOT_PASS item=$ITEM base=$BASE_REAL ledger_clean=yes"

# ---- REGISTERED CPU PLACEMENT (PREREGISTRATION.md §5b, verbatim) ---------
# `mpirun` inside a `--cpus=N` container binds rank 0 to the FIRST CORE OF THE
# HOST TOPOLOGY.  Concurrent containers then land on the same host core and
# throughput collapses as 1/N while the box reports itself idle -- MEASURED by
# the D13 lane 2026-08-25: affinity=0 on all three concurrent arms, 0.250 cores
# delivered against a 1.0-core quota, host 61 % idle, throughput moved 4x on a
# control that changed only the sibling count.  `--cpus=4` does NOT hand out
# four distinct cores.  So: PIN, and MEASURE the placement rather than infer it
# from the flag that was passed.
#
# SO-1cR REGISTERED DELTA (PREREGISTRATION.md section 5b): THE PLACEMENT IS
# PER-ARM, because this item is the FIRST in the SO ladder to run at np > 1 and
# MESH is still np = 1.  Registered: MESH on core 10; every N arm on 10,11,12,13
# -- FOUR DISTINCT cores for four ranks, which is the whole point of pinning
# (`--cpus=4` does NOT hand out four distinct cores; the D13 lane measured 0.250
# cores delivered against a 1.0-core quota with the box 61 % idle).
#
# DISJOINTNESS, CHECKED AGAINST THE REGISTERED PLACEMENTS OF EVERY LIVE OR
# QUEUED SIBLING RATHER THAN ASSUMED: D6 registers 2,3,4,14; D4-SHIPPED
# registers 5,6,7,9; SO-1a and SO-1b both register 9.  10-13 intersects NONE of
# them.  At np = 4 the grader's delivered-cores floor DOES apply (g_placement:
# dl_ok is True only when ARM_RANKS == 1), so an overlap here could fail G12 on
# contention rather than on physics -- which is exactly why the set is disjoint
# by registration and not by luck.
cpuset_of() {
  case "$1" in
    MESH)                    echo 10 ;;
    Ns-P|Ni-P|Ns-S|Ni-S)     echo 10,11,12,13 ;;
    *)                       echo "" ;;
  esac
}

# For containerised MPI the conditioning variable is CONCURRENT CONTAINERS, not
# loadavg -- `uptime` will lie.  Censused before and after every arm.
container_census() {
  sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^so1cr_" | tr '\n' ',' | sed 's/,$//'
}

# ---- REGISTERED DECOMPOSITION PER ARM (PREREGISTRATION.md section 2) ------
# `DAFOAM_CHARTER.md` section 5 forbids "describing a case as
# decomposition-invariant from one arm", so EACH ROW BUYS TWO: `scotch` (the
# DAFoam default, which A4 measured at 8.95 % against FD) and `simple 4x1x1`
# (which A4 measured at 0.00054 % on the same mesh, the same np and the same
# patched toolchain -- a factor of 16,600 between two decompositions of one
# mesh).  The dictionary is a FROZEN, md5-pinned file per decomposition, staged
# into the arm's own `system/`, and the instrument re-reads the method and the
# subdivision back out of the staged file and refuses on a disagreement.
decomp_of() {
  case "$1" in
    Ns-P|Ns-S) echo scotch ;;
    Ni-P|Ni-S) echo simple ;;
    MESH)      echo scotch ;;
    *)         echo "" ;;
  esac
}

# ---- REGISTERED CAP TABLE (PREREGISTRATION.md §4, verbatim) ---------------
#   arm    ranks  core-min cap   in-container wall   memory cap
#   MESH     1        5.0            300 s              4g
#   Ns-P     4       30.0            450 s              6g
#   Ni-P     4       30.0            450 s              6g
#   Ns-S     4       30.0            450 s              6g
#   Ni-S     4       30.0            450 s              6g
#   CEILING = 5.0 + 4 x 30.0 = 125.0 core-min, and the launcher ASSERTS the sum.
# SO-1cR COMMENT CORRECTION: SO-1c's copy of this table read `8g` on the four
# solver arms while its own executable `cap_memory` returned `6g` and its
# PREREGISTRATION.md section 2 registered `6g`.  The EXECUTABLE was right and the
# comment was stale; nothing about the run changes.  It is corrected here rather
# than carried, because a reader checking the cap by eye reads the table.
cap_core_min() {
  case "$1" in
    MESH)                 echo 5.0 ;;
    Ns-P|Ni-P|Ns-S|Ni-S)  echo 30.0 ;;
    *)  echo "" ;;
  esac
}
cap_memory() {
  case "$1" in
    MESH)                 echo 4g ;;
    Ns-P|Ni-P|Ns-S|Ni-S)  echo 6g ;;
    *) echo "" ;;
  esac
}
# 6g at np = 4 is AV-1's and AV-1R's REGISTERED figure for np = 4 on THIS mesh
# (`av1_run_arm.sh:173`, `av1r_chain_driver.sh:103`) -- the family's own
# like-for-like number on A1's 4,032 cells, INHERITED BY CITATION and not
# re-derived by a lane that has not measured it.  The chain driver's H5 floor of
# 8.0 GiB is AV-1's likewise (`av1_chain_driver.sh:45`).
# np = 4 ON EVERY SOLVER ARM by registration, and this is a DEPARTURE FROM
# SO-1a AND SO-1b THAT IS THE ITEM'S ENTIRE SUBJECT, not a convenience.
# `DAFOAM_CHARTER.md` section 5 says serial before parallel: SO-1a ran the
# serial gradient and SO-1b ran the serial optimisation, so the serial half is
# BOUGHT and this rung is the parallel half it licenses.  MESH stays at np = 1
# because mesh generation is not a decomposition question.
ranks_of() {
  case "$1" in
    MESH)                 echo 1 ;;
    Ns-P|Ni-P|Ns-S|Ni-S)  echo 4 ;;
    *) echo "" ;;
  esac
}

# ---- REGISTERED TOOLCHAIN, BY DIGEST, never by tag ----------------------
# `DAFOAM_CHARTER.md` SECTION 6: "Shipped and patched are always two rows, and
# toolchain identity is an image ID and a library hash, never a version string".
# SECTION 11 IS THE LESSONS-NUMBERING CLAUSE.  so1a_run_arm.sh:184 and
# SO1a_chain.json both cite this rule as section 11; that slip is inherited by
# NEITHER this file nor this item's document, and SO-1a's frozen files are not
# repaired for it (CLAUDE.md rule 6).
# PATCHED IDWarp : dafoam-idwarp-rot:v1
#   sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
# SHIPPED (stock): dafoam/opt-packages:latest
#   sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
IMG_SHIPPED_DIGEST=sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc

# ---- FROZEN INSTRUMENT HASHES (PREREGISTRATION.md §7, verbatim) ----------
MD5_RUNSCRIPT=0557da51f6f179f6de865144343c499f   # so1cr_runScript.py = byte copy of the shipped INCOMPRESSIBLE tutorial runScript.py
MD5_XN=1ffadf39206d5bb732dcfcf0288ba628                                # so1cr_xn.py (set at freeze)
MD5_DECOMP_SCOTCH=816f5ba44075fde47fa5db4269877bc8   # so1cr_decomposeParDict_scotch (numberOfSubdomains 4, method scotch)
MD5_DECOMP_SIMPLE=194c330803077f0ffa4341f468c09768   # so1cr_decomposeParDict_simple (numberOfSubdomains 4, method simple, n (4 1 1))

ARM="${1:-}"; IMG="${2:-}"
test -n "$ARM" || { echo "ABORT usage: so1cr_run_arm.sh <MESH|Ns-P|Ni-P|Ns-S|Ni-S> <image>"; exit 64; }
test -n "$IMG" || { echo "ABORT usage: so1cr_run_arm.sh <MESH|Ns-P|Ni-P|Ns-S|Ni-S> <image>"; exit 64; }
RANKS=$(ranks_of "$ARM"); test -n "$RANKS" || { echo "ABORT arm $ARM carries no registered rank count"; exit 64; }
CPUSET=$(cpuset_of "$ARM"); test -n "$CPUSET" || { echo "ABORT arm $ARM carries no registered cpu placement"; exit 64; }
DECOMP=$(decomp_of "$ARM"); test -n "$DECOMP" || { echo "ABORT arm $ARM carries no registered decomposition"; exit 64; }

# ---- G-ROOT.5 (ADDENDUM 2) -- A LIVE ARM IS NEVER RE-STAGED.  G-ROOT.1-.3
# ---- see only ledger rows; a queue-runner re-firing this launcher on a
# ---- RUNNING arm would pass them and reach `rm -rf "$WORK"` (the shape the
# ---- D7FR lane found at d7fr_run_arm.sh:319).  Two live readings, taken
# ---- BEFORE any destructive act:
# ----   (a) a RUNNING container carrying this item's prefix and this arm;
# ----   (b) a driver pidfile in the run root naming a LIVE pid that is not an
# ----       ancestor of this process (a second driver), or whose cwd is the
# ----       run root.  A stale pidfile (dead pid) does not block.
LIVE_SAME_ARM=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^so1cr_${ARM}_" 2>/dev/null | grep "^so1cr_${ARM}_" | head -3 | tr '\n' ',' | sed 's/,$//')
if [ -n "$LIVE_SAME_ARM" ]; then
  echo "ABORT G-ROOT.5 a RUNNING container already carries this item's prefix and arm: [$LIVE_SAME_ARM]"
  echo "  Re-staging would remove the live arm directory under it.  REFUSED."
  exit 3
fi
PIDFILE="$BASE/so1cr_driver.pid"
if [ -f "$PIDFILE" ]; then
  DPID=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$DPID" ] && kill -0 "$DPID" 2>/dev/null; then
    ANCESTOR=no; p=$$
    for _ in $(seq 1 64); do
      if [ "$p" = "$DPID" ]; then ANCESTOR=yes; break; fi
      p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ')
      if [ -z "$p" ] || [ "$p" = "0" ]; then break; fi
    done
    DCWD=$(readlink -f "/proc/$DPID/cwd" 2>/dev/null)
    if [ "$ANCESTOR" = "no" ] || [ "$DCWD" = "$(realpath -m "$BASE")" ]; then
      echo "ABORT G-ROOT.5 driver pidfile $PIDFILE names LIVE pid $DPID (ancestor_of_this_launcher=$ANCESTOR cwd=$DCWD)."
      echo "  Another driver owns this run root, or a process sits inside it.  REFUSED."
      exit 3
    fi
  fi
fi
echo "D4S_G_ROOT5_PASS arm=$ARM live_same_arm_containers=none driver_pidfile=$([ -f "$PIDFILE" ] && echo present_owner_is_ancestor_or_stale || echo absent)"

# ===========================================================================
# G-CAP-PREREG (INHERITED FROM SO-1b, RE-POINTED).  SO-1a's D4_CAP_ASSERT below
# checks this launcher AGAINST ITSELF: it derives the wall deadline from the cap
# and then inverts the arithmetic.  TWO NUMBERS THAT AGREE WITH EACH OTHER CAN
# BOTH BE WRONG.  G-CAP-PREREG checks the launcher against THE FROZEN
# PRE-REGISTRATION, on two independent channels:
#   (a) the SO1CR-CAP-MANIFEST line in the document ON DISK must name exactly the
#       caps this launcher would enforce, and a CEILING equal to their sum;
#   (b) the same line read from `git show HEAD:<path>` must be BYTE-IDENTICAL to
#       the one on disk, so a post-freeze worktree edit cannot move a cap under a
#       launcher that is about to spend on it.
# Channel (b) is INFRASTRUCTURE (L-342): unreadable -> NOT_MEASURED, REPORTED and
# never composed into a pass it did not earn; channel (a) binds regardless.
# This is the check that caught W3's 600-against-a-registered-900 before 563
# core-min were spent.  IT RUNS BEFORE `rm -rf "$WORK"` AND BEFORE `docker run`.
# ===========================================================================
PREREG="${PREREG:-/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_SO1cR/PREREGISTRATION.md}"
PREREG_REL=cases/dafoam/ladder-a/A1/curriculum_SO1cR/PREREGISTRATION.md
test -f "$PREREG" || { echo "ABORT G-CAP-PREREG the frozen pre-registration is absent: $PREREG"; exit 65; }
MAN_DISK=$(grep -a -o 'SO1CR-CAP-MANIFEST v1 [^>]*' "$PREREG" | head -1 | sed 's/ *-->$//;s/ *$//')
test -n "$MAN_DISK" || { echo "ABORT G-CAP-PREREG no SO1CR-CAP-MANIFEST line in $PREREG"; exit 65; }
MAN_HEAD=$(git show "HEAD:$PREREG_REL" 2>/dev/null | grep -a -o 'SO1CR-CAP-MANIFEST v1 [^>]*' | head -1 | sed 's/ *-->$//;s/ *$//')
if [ -z "$MAN_HEAD" ]; then
  MAN_HEAD_STATE=NOT_MEASURED
elif [ "$MAN_HEAD" = "$MAN_DISK" ]; then
  MAN_HEAD_STATE=AGREES
else
  echo "ABORT G-CAP-PREREG channel (b): the manifest on disk and at HEAD DIFFER."
  echo "  disk: [$MAN_DISK]"
  echo "  HEAD: [$MAN_HEAD]"
  echo "  A cap moved in the worktree after the freeze.  REFUSED before any container."
  exit 65
fi
man_field() { echo "$MAN_DISK" | tr ' ' '\n' | grep -a "^$1=" | head -1 | cut -d= -f2 ; }
CEIL_REG=$(man_field CEILING)
test -n "$CEIL_REG" || { echo "ABORT G-CAP-PREREG the manifest names no CEILING"; exit 65; }
CAP_SUM=0
for _a in MESH Ns-P Ni-P Ns-S Ni-S; do
  _mine=$(cap_core_min "$_a")
  case "$_a" in
    MESH) _key=MESH ;;
    Ns-P) _key=Ns-P ;;  Ni-P) _key=Ni-P ;;
    Ns-S) _key=Ns-S ;;  Ni-S) _key=Ni-S ;;
  esac
  _doc=$(man_field "$_key")
  test -n "$_doc" || { echo "ABORT G-CAP-PREREG the manifest names no cap for arm $_a"; exit 65; }
  if [ "$(python3 -c "print(1 if abs(float('$_mine')-float('$_doc'))>1e-9 else 0)")" = "1" ]; then
    echo "ABORT G-CAP-PREREG arm $_a: this launcher enforces $_mine core-min, the FROZEN document registers $_doc."
    echo "  The launcher does not get to move a registered cap.  REFUSED before any container."
    exit 65
  fi
  CAP_SUM=$(python3 -c "print('%.6f' % ($CAP_SUM + float('$_mine')))")
done
if [ "$(python3 -c "print(1 if abs(float('$CAP_SUM')-float('$CEIL_REG'))>1e-9 else 0)")" = "1" ]; then
  echo "ABORT G-CAP-PREREG the registered CEILING $CEIL_REG is not the sum of the registered caps ($CAP_SUM)."
  exit 65
fi
_RANKS_DOC=$(man_field RANKS_N)
if [ -n "$_RANKS_DOC" ] && [ "$ARM" != "MESH" ] && [ "$_RANKS_DOC" != "$RANKS" ]; then
  echo "ABORT G-CAP-PREREG arm $ARM runs at $RANKS ranks, the FROZEN document registers $_RANKS_DOC."
  echo "  A core-minute cap means nothing without the rank count it is divided by.  REFUSED."
  exit 65
fi
echo "SO1CR_G_CAP_PREREG_PASS arm=$ARM prereg=$PREREG head_channel=$MAN_HEAD_STATE sum_of_caps=$CAP_SUM ceiling=$CEIL_REG ranks=$RANKS manifest=[$MAN_DISK]"

CAP=$(cap_core_min "$ARM")
MEM=$(cap_memory "$ARM")
test -n "$CAP" || { echo "ABORT unknown arm $ARM -- no registered cap"; exit 64; }
test -n "$MEM" || { echo "ABORT unknown arm $ARM -- no registered memory cap"; exit 64; }

# THE ASSERTION.  The enforced wall timeout is DERIVED from the registered
# core-minute cap and the registered rank count, and is then re-checked
# against that cap by inverting the arithmetic.  There is no second number
# anywhere in this file that could drift from the first.
TMO=$(python3 -c "print(int(round($CAP*60.0/$RANKS)))") || { echo "ABORT tmo calc"; exit 65; }
BACKCHECK=$(python3 -c "print('%.6f' % ($TMO*$RANKS/60.0))") || { echo "ABORT backcheck"; exit 65; }
python3 -c "
import sys
cap, back = $CAP, $BACKCHECK
if abs(cap-back) > 0.02:
    sys.stderr.write('ABORT CAP MISMATCH registered=%r enforced=%r\n' % (cap, back)); sys.exit(1)
" || { echo "ABORT enforced cap != registered cap"; exit 65; }
echo "D4_CAP_ASSERT arm=$ARM registered_core_min=$CAP ranks=$RANKS enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM"

# ---- host state, read before ranks are claimed ---------------------------
MEMAVAIL_KB=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
MEMAVAIL_GIB=$(python3 -c "print('%.2f' % ($MEMAVAIL_KB/1048576.0))")
LOAD=$(awk '{print $1}' /proc/loadavg)
SIBLINGS_PRE=$(container_census)
echo "D4_HOST_PRE arm=$ARM MemAvailable_GiB=$MEMAVAIL_GIB load1=$LOAD cpuset=$CPUSET siblings_pre=[$SIBLINGS_PRE]"

test "$(stat -c '%a' "$BASE")" = "777" || { echo "ABORT L-251 run root mode $(stat -c '%a' "$BASE")"; exit 4; }

# ---- staged-instrument identity, re-asserted before EVERY launch ---------
echo "$MD5_RUNSCRIPT  $BASE/so1cr_runScript.py"                    | md5sum -c - || { echo "ABORT runScript md5"; exit 4; }
echo "$MD5_XN  $BASE/so1cr_xn.py"                                 | md5sum -c - || { echo "ABORT xn md5"; exit 4; }
echo "$MD5_DECOMP_SCOTCH  $BASE/so1cr_decomposeParDict_scotch"    | md5sum -c - || { echo "ABORT decomposeParDict_scotch md5"; exit 4; }
echo "$MD5_DECOMP_SIMPLE  $BASE/so1cr_decomposeParDict_simple"    | md5sum -c - || { echo "ABORT decomposeParDict_simple md5"; exit 4; }
# and the dictionary THIS arm will actually run under, resolved from the arm name
case "$DECOMP" in
  scotch) DECOMP_SRC="$BASE/so1cr_decomposeParDict_scotch" ;;
  simple) DECOMP_SRC="$BASE/so1cr_decomposeParDict_simple" ;;
  *) echo "ABORT arm $ARM resolved to an unregistered decomposition [$DECOMP]"; exit 4 ;;
esac
echo "SO1CR_DECOMP_SELECTED arm=$ARM decomposition=$DECOMP source=$DECOMP_SRC md5=$(md5sum "$DECOMP_SRC" | cut -d\  -f1)"

# ---- image identity by DIGEST, resolved from the local store -------------
GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
test -n "$GOT_DIGEST" || { echo "ABORT cannot read digest of $IMG"; exit 4; }
case "$IMG" in
  dafoam-idwarp-rot:v1)    WANT=$IMG_PATCHED_DIGEST; ROW=PATCHED ;;
  dafoam/opt-packages:latest) WANT=$IMG_SHIPPED_DIGEST; ROW=SHIPPED ;;
  *) echo "ABORT image $IMG is not a registered row"; exit 4 ;;
esac
test "$GOT_DIGEST" = "$WANT" || { echo "ABORT digest mismatch $IMG got=$GOT_DIGEST want=$WANT"; exit 4; }

# ---- G-ROW.  THE ROW A RUN CLAIMS AND THE ROW IT RAN MUST BE THE SAME HASH.
# DAFOAM_CHARTER.md SECTION 6 makes the HASH the identity.  D15 REGISTERED DELTA: the
# row is carried in the ARM NAME (-S shipped, -P patched; MESH on shipped --
# mesh generation does not touch IDWarp), and a mismatch refuses.
case "$ARM" in
  MESH|*-S) WANT_ROW=SHIPPED ;;
  *-P)      WANT_ROW=PATCHED ;;
  *)        WANT_ROW="" ;;
esac
test "$ROW" = "$WANT_ROW" || {
  echo "ABORT G-ROW arm $ARM is registered on the $WANT_ROW row; got ROW=$ROW ($IMG)."
  echo "  A row a run claims and a row it ran must be the same hash.  REFUSED."
  exit 4; }
echo "D4S_G_ROW_PASS row=$ROW digest=$GOT_DIGEST"
echo "D4_IMAGE_OK row=$ROW image=$IMG digest=$GOT_DIGEST"

# ===========================================================================
# G-OPTDEP.  AN N ARM CONSUMES SO-1b'S OPTIMUM FOR ITS OWN ROW AND FOR NO OTHER.
# The chain driver copies SO-1b's `so1b_E.json` for each row into
# `$BASE/optref/<ROW>/` before any arm runs; this guard refuses an arm whose own
# row's copy is absent or unparseable, BEFORE `rm -rf "$WORK"` and BEFORE
# `docker run`.  It is the G-EDEP form SO-1b uses between its own O and E arms,
# re-pointed across the item boundary.
#
# THE FILE IS A STAGED INPUT, NOT A PRODUCT, AND IS REGISTERED AS ONE.  It is
# named in the pre-registration's STAGED INPUTS list and is EXPLICITLY EXCLUDED
# from the grader's age-checked artefact list.  `d4s_f3s_grade.py:61` listed
# `OptView.hst` -- a staged input -- among its age-checked ARTEFACTS, making the
# age clause UNSATISFIABLE BY CONSTRUCTION and forcing D4S-F3S to NOT A RESULT
# with 19 of 20 gate readings passing.  An age guard must check only what the
# run PRODUCES.
# ===========================================================================
if [ "$ARM" != "MESH" ]; then
  OPTREF="$BASE/optref/$ROW/so1b_E.json"
  test -f "$OPTREF" || {
    echo "ABORT G-OPTDEP arm $ARM is on the $ROW row and $OPTREF is absent."
    echo "  SO-1cR verifies the gradient AT SO-1b's OPTIMUM; with no optimum there"
    echo "  is no design point to verify at.  REFUSED before any staging."
    exit 5; }
  # ---- SO-1cR REPAIR 1 of 3, BREAK 6 CALL SITE (2).  THE ROW LABEL IS A
  # ---- REGISTERED MAPPING, WRITTEN OUT IN FULL.
  # SO-1bR labels its per-row artefacts with the DIRECTORY SUFFIX ('P'/'S'),
  # never the row name.  SO-1c's amendment R8 repaired this comparison in the
  # CHAIN DRIVER and in the chain driver ONLY; this call site kept the equality
  # form, refused the real artefact in PREFLIGHT with rc=5, and stopped SO-1c's
  # chain at its second arm.  The mapping below is deliberately NOT derived as
  # `row[0]`: row[0] agrees with the producer only by the coincidence that
  # PATCHED and SHIPPED share first letters with P and S, and a check that is
  # true by coincidence has stopped being a check.
  # THE TWO LABEL SETS ARE DISJOINT, and that is what keeps the assertion doing
  # its job -- it exists to catch AN ARTEFACT SITTING IN THE WRONG DIRECTORY,
  # so a SHIPPED-row artefact staged under optref/PATCHED/ STILL REFUSES, and a
  # PATCHED-row artefact staged under optref/SHIPPED/ STILL REFUSES.
  python3 -c "
import json,sys
ROW_LABELS = {'PATCHED': ('PATCHED', 'P'), 'SHIPPED': ('SHIPPED', 'S')}
d=json.load(open('$OPTREF'))
for k in ('design_point','adjoint','identity','nprocs','row'):
    if k not in d: sys.stderr.write('G-OPTDEP %r absent from the optimum artefact\n'%k); sys.exit(1)
if int(d['nprocs'])!=1: sys.stderr.write('G-OPTDEP the comparison basis must be np=1, artefact says %r\n'%(d['nprocs'],)); sys.exit(1)
want = ROW_LABELS.get('$ROW')
if want is None: sys.stderr.write('G-OPTDEP %r is not a REGISTERED row\n'%('$ROW',)); sys.exit(1)
if d['row'] not in want:
    sys.stderr.write('G-OPTDEP artefact row %r is not a registered label for this arm row %r -- '
                     'the only labels REGISTERED for this row are %s.  The two rows\' label sets '
                     'are DISJOINT, so a swapped artefact cannot satisfy this.\n'
                     % (d['row'], '$ROW', ' or '.join(repr(x) for x in want)))
    sys.exit(1)
" || { echo "ABORT G-OPTDEP the optimum artefact for row $ROW is unparseable or is another row's. REFUSED."; exit 5; }
  echo "SO1CR_G_OPTDEP_PASS arm=$ARM row=$ROW optimum=$OPTREF"
fi

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="so1cr_${ARM}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"

# ---- stage a pristine copy for the arm ------------------------------------
# D15 REGISTERED DELTA: MESH stages from base/ (the tutorial's inputs, no mesh);
# every solver arm stages a COLD copy of the MESH arm's OUTPUT (mesh + 0/), so
# all four gradient arms run on ONE mesh generated once inside the SHIPPED image.
if [ "$ARM" = "MESH" ]; then
  sudo -n rm -rf "$WORK" 2>/dev/null
  cp -a "$BASE/base" "$WORK" || { echo "ABORT stage copy"; exit 4; }
  test -e "$WORK/constant/polyMesh" && { echo "ABORT G-COLD MESH: base/ already carries constant/polyMesh"; exit 5; }
  test -e "$WORK/0" && { echo "ABORT G-COLD MESH: base/ already carries 0/"; exit 5; }
  # DATUM BY EXISTENCE (AV-1/AV-2, 2026-08-27): accept either registered name and
  # RECORD the one used, so the grader is not left inferring it from a hard-coded
  # string that `writeCompression on` can invalidate.
  if   [ -f "$WORK/0.orig/U" ];    then DATUM_NAME=0.orig/U
  elif [ -f "$WORK/0.orig/U.gz" ]; then DATUM_NAME=0.orig/U.gz
  else echo "ABORT G-COLD neither 0.orig/U nor 0.orig/U.gz is present"; exit 5; fi
  touch "$WORK/0.orig"/* || { echo "ABORT age-guard datum"; exit 5; }
  AGE_DATUM=$(stat -c '%Y' "$WORK/$DATUM_NAME")
  echo "$AGE_DATUM" > "$WORK/.so1cr_age_datum"
  echo "$DATUM_NAME" > "$WORK/.so1cr_age_datum_ref"
  echo "D4_G_COLD OK arm=$ARM age_datum_epoch=$AGE_DATUM datum_file=$DATUM_NAME resolved_by=EXISTENCE"
else
  test -d "$BASE/MESH" || { echo "ABORT arm $ARM expects an existing MESH/ from arm MESH"; exit 5; }
  test -f "$BASE/MESH/constant/polyMesh/boundary" || { echo "ABORT arm $ARM: MESH/ carries no constant/polyMesh/boundary"; exit 5; }
  { [ -f "$BASE/MESH/0/U" ] || [ -f "$BASE/MESH/0/U.gz" ]; } || { echo "ABORT arm $ARM: MESH/ carries neither 0/U nor 0/U.gz"; exit 5; }
  sudo -n rm -rf "$WORK" 2>/dev/null
  cp -a "$BASE/MESH" "$WORK" || { echo "ABORT stage copy from MESH"; exit 4; }
  rm -f "$WORK/so1cr_cmd.sh" "$WORK/checkMesh.log" "$WORK/logMeshGeneration.txt" "$WORK/volumeMesh.xyz" "$WORK/surfaceMesh.xyz" "$WORK/.so1cr_age_datum" "$WORK/.so1cr_age_datum_ref" "$WORK/so1cr_N.json" "$WORK/so1cr_N.jsonl" "$WORK/so1b_E.json" 2>/dev/null
  cp -a "$BASE/so1cr_runScript.py" "$BASE/so1cr_xn.py" "$WORK/" || { echo "ABORT stage instruments"; exit 4; }
  # ---- THE ARM'S OWN DECOMPOSITION, OVERLAID AND RE-ASSERTED AFTER THE COPY.
  # `DAFOAM_CHARTER.md` section 5: the decomposition is a recorded datum of the
  # run, and DAFoam runs `decomposePar` itself at np > 1 from this dictionary
  # (`pyDAFoam.py:1454 runDecomposePar`), so THIS FILE is what the partition
  # comes from.  The md5 is re-checked ON THE OVERLAID COPY, not only on the
  # source: a copy that silently failed would otherwise leave the tutorial's own
  # dict in place and the arm would run a decomposition nobody registered.
  cp -a "$DECOMP_SRC" "$WORK/system/decomposeParDict" || { echo "ABORT overlay decomposeParDict"; exit 4; }
  case "$DECOMP" in
    scotch) echo "$MD5_DECOMP_SCOTCH  $WORK/system/decomposeParDict" | md5sum -c - || { echo "ABORT overlaid scotch dict md5"; exit 4; } ;;
    simple) echo "$MD5_DECOMP_SIMPLE  $WORK/system/decomposeParDict" | md5sum -c - || { echo "ABORT overlaid simple dict md5"; exit 4; } ;;
  esac
  echo "D4S_DECOMP_DICT arm=$ARM ranks=$RANKS decomposition=$DECOMP md5=$(md5sum "$WORK/system/decomposeParDict" | cut -d\  -f1)"
  # ---- THE STAGED INPUT.  `so1b_E.json` is SO-1b's artefact, copied in for the
  # ---- container to read.  IT IS AN INPUT, NOT A PRODUCT, and the grader's
  # ---- age-checked list EXCLUDES IT BY NAME (see the G-OPTDEP block above for
  # ---- the D4S-F3S defect this avoids).  `cp -a` preserves its mtime, which is
  # ---- OLDER than the age datum touched below -- exactly as a staged input
  # ---- should be, and exactly why it can never satisfy an age guard.
  cp -a "$OPTREF" "$WORK/so1b_E.json" || { echo "ABORT stage the optimum artefact"; exit 4; }
  echo "SO1CR_STAGED_INPUT arm=$ARM file=so1b_E.json row=$ROW md5=$(md5sum "$WORK/so1b_E.json" | cut -d\  -f1) mtime=$(stat -c %Y "$WORK/so1b_E.json") class=STAGED_INPUT_NOT_A_PRODUCT"
  # COLD START, verified BEFORE the launch (D2 G8), and the AGE GUARD's datum:
  # 0/ is touched LAST at stage time, so every artifact the run produces must
  # be strictly newer than 0/U or it did not come from this run.
  # G-COLD names ONLY files THIS ITEM'S RUN PRODUCES.  `so1b_E.json` is a staged
  # input and is deliberately ABSENT from this list -- it is present by design.
  for bad in "$WORK/reports" "$WORK/so1cr_N.json" "$WORK/so1cr_N.jsonl" "$WORK/dRdWColoring_2.bin"; do
    test -e "$bad" && { echo "ABORT G-COLD $bad exists"; exit 5; }
  done
  test -n "$(ls -d "$WORK"/processor* 2>/dev/null)" && { echo "ABORT G-COLD processor* present"; exit 5; }
  for d in "$WORK"/*/; do
    n=$(basename "$d")
    case "$n" in 0|0.orig) ;; [0-9]*) echo "ABORT G-COLD time dir present: $n"; exit 5 ;; esac
  done
  if   [ -f "$WORK/0/U" ];    then DATUM_NAME=0/U
  elif [ -f "$WORK/0/U.gz" ]; then DATUM_NAME=0/U.gz
  else echo "ABORT G-COLD neither 0/U nor 0/U.gz is present"; exit 5; fi
  touch "$WORK/0"/* || { echo "ABORT age-guard datum"; exit 5; }
  AGE_DATUM=$(stat -c '%Y' "$WORK/$DATUM_NAME")
  echo "$AGE_DATUM" > "$WORK/.so1cr_age_datum"
  echo "$DATUM_NAME" > "$WORK/.so1cr_age_datum_ref"
  echo "SO1CR_WRITE_COMPRESSION $(grep -a writeCompression "$WORK/system/controlDict" 2>/dev/null | head -1 | tr -d ';')"
  echo "D4_G_COLD OK arm=$ARM age_datum_epoch=$AGE_DATUM datum_file=$DATUM_NAME resolved_by=EXISTENCE"
fi

case "$ARM" in
  MESH)     CMD="bash preProcessing.sh && checkMesh > checkMesh.log 2>&1; echo SO1CR_CHECKMESH_RC \$?; sha256sum constant/polyMesh/points* ; grep -a 'cells:' checkMesh.log" ;;
  Ns-P|Ni-P|Ns-S|Ni-S)
            CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python so1cr_xn.py -mode N -optimum so1b_E.json" ;;
esac

# ---- ADDENDUM 2: the arm command goes to a FILE the container executes under
# ---- its OWN `timeout` at the registered cap wall (TMO), so the deadline is
# ---- INSIDE the container and survives every host shell.  `-k 60` escalates
# ---- TERM to KILL; the kernel exit code (124/137) is then the record.
CMDFILE="$WORK/so1cr_cmd.sh"
printf '%s\n' "$CMD" > "$CMDFILE" || { echo "ABORT cmd file"; exit 4; }
echo "D4S_CMDFILE arm=$ARM md5=$(md5sum "$CMDFILE" | cut -d' ' -f1) deadline_in_container_s=$TMO"
CPUSAMPLE="$BASE/${ARM}_${STAMP}.cpu.jsonl"
# DELIVERED CORES ARE MEASURED, NOT INFERRED FROM THE QUOTA FLAG.  This sampler
# polls the container's own cgroup cpu.stat and writes cores-delivered to a
# FILE.  It is a passive reader: it starts nothing, kills nothing, and its
# failure cannot change a verdict -- an absent sample file is reported as
# NOT_MEASURED, never as a passing placement gate.
(
  for _ in $(seq 1 100000); do
    cid=$(sudo -n docker ps -q --filter "name=^${NAME}$" 2>/dev/null | head -1)
    if [ -n "$cid" ]; then break; fi
    sleep 1
  done
  cg=""
  for cand in /sys/fs/cgroup/system.slice/docker-${cid}*.scope/cpu.stat \
              /sys/fs/cgroup/cpu/docker/${cid}*/cpuacct.usage; do
    if [ -e "$cand" ]; then cg="$cand"; break; fi
  done
  if [ -z "$cg" ]; then echo '{"delivered_cores":null,"note":"cgroup path not found"}' >> "$CPUSAMPLE"; exit 0; fi
  prev=""; prevt=""
  while sudo -n docker ps -q --filter "name=^${NAME}$" 2>/dev/null | grep -q .; do
    now=$(date +%s.%N)
    if [ "$(basename "$cg")" = "cpu.stat" ]; then
      u=$(awk '/^usage_usec/{print $2}' "$cg" 2>/dev/null)
      t=$(awk '/^throttled_usec/{print $2}' "$cg" 2>/dev/null)
      n=$(awk '/^nr_throttled/{print $2}' "$cg" 2>/dev/null)
    else
      u=$(( $(cat "$cg" 2>/dev/null || echo 0) / 1000 )); t=0; n=0
    fi
    if [ -n "$prev" ] && [ -n "$u" ]; then
      python3 -c "
import json,sys
du=($u-$prev)/1e6; dt=$now-$prevt
print(json.dumps({'t':round($now,2),'delivered_cores':round(du/dt,4) if dt>0 else None,'throttled_usec':$t,'nr_throttled':$n}))
" >> "$CPUSAMPLE" 2>/dev/null
    fi
    prev=$u; prevt=$now
    sleep 15
  done
) &
SAMPLER=$!

T0=$(date -u +%s)
# ===========================================================================
# rc CAPTURE IS CLOSED: `rc` is read from `docker inspect .State.ExitCode`,
# the KERNEL'S OWN RECORD; `.State.OOMKilled` from the SAME inspect; NO --rm
# until the record is read.  THE CAP LIVES INSIDE THE CONTAINER: `timeout -k 60
# $TMO` wraps the arm command file on the `docker run` line below, so the
# deadline survives every host shell (the D4-SHIPPED Addendum 2 form, inherited
# from d5_run_arm.sh unchanged).  The host poller REPORTS a crossing and
# hard-stops only at 4x cap, while this shell lives.
# ===========================================================================
sudo -n docker run -d --name "$NAME" \
    --user 0:0 --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$ARM" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D4S_CONTAINER_UID: \$(id -u) && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"D4S_IDWARP_IMPORTED_FROM:\",p); print(\"D4S_IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' && \
     echo D4S_DEADLINE_IN_CONTAINER_S: $TMO && \
     timeout -k 60 $TMO bash /mnt/$ARM/so1cr_cmd.sh" > /dev/null 2>&1 \
  || { echo "ABORT could not start container"; exit 4; }

# The cap is a RUNAWAY GUARD THAT REPORTS (Sanaa, 2026-08-25), not a budget
# rigor is trimmed to fit.  A crossing is written to the ledger and CONTINUES;
# the supervisor decides.  CEILING = 4 x CAP is a hard stop so a genuine
# runaway is still bounded -- WHILE THIS SHELL LIVES (the in-container timeout
# is the cap that survives shell death).
CEILING=$(python3 -c "print('%.1f' % (4.0*$CAP))")
echo "D4S_RUNAWAY_GUARD arm=$ARM cap_core_min=$CAP ceiling_core_min=$CEILING mode=report_then_stop_at_ceiling"
CAP_REPORTED=no; CEILING_HIT=no
while true; do
  RUNNING=$(sudo -n docker inspect --format '{{.State.Running}}' "$NAME" 2>/dev/null)
  NOW=$(date -u +%s); EL=$((NOW-T0))
  CM=$(python3 -c "print(round($EL*$RANKS/60.0,3))")
  if [ "$RUNNING" != "true" ]; then break; fi
  if [ "$CAP_REPORTED" = "no" ] && [ "$(python3 -c "print(1 if $CM > $CAP else 0)")" = "1" ]; then
    CAP_REPORTED=yes
    echo "D4S_CAP_CROSSED arm=$ARM core_min=$CM cap=$CAP ceiling=$CEILING action=REPORTED_RUN_CONTINUES supervisor_decides" | tee -a "$BASE/ledger.txt"
  fi
  if [ "$(python3 -c "print(1 if $CM > $CEILING else 0)")" = "1" ]; then
    CEILING_HIT=yes
    echo "D4S_CEILING_HIT arm=$ARM core_min=$CM ceiling=$CEILING action=HARD_STOP" | tee -a "$BASE/ledger.txt"
    sudo -n docker stop -t 30 "$NAME" >/dev/null 2>&1
    break
  fi
  sleep 10
done
sudo -n docker logs "$NAME" > "$LOG" 2>&1
# THE KERNEL'S VERDICT, read BEFORE the container is removed.
rc=$(sudo -n docker inspect --format '{{.State.ExitCode}}' "$NAME" 2>/dev/null)
test -n "$rc" || rc=125
T1=$(date -u +%s)
WALL=$((T1-T0))
kill $SAMPLER 2>/dev/null; wait $SAMPLER 2>/dev/null
SIBLINGS_POST=$(container_census)
DELIVERED=$(python3 -c "
import json,sys,os
p='$CPUSAMPLE'
if not os.path.exists(p): print('NOT_MEASURED'); sys.exit()
v=[]
thr=0
for line in open(p):
    try: d=json.loads(line)
    except Exception: continue
    if d.get('delivered_cores') is not None: v.append(d['delivered_cores'])
    thr=max(thr, d.get('nr_throttled') or 0)
print('%s n=%d max_nr_throttled=%d' % (('%.4f'%(sum(v)/len(v)) if v else 'NOT_MEASURED'), len(v), thr))
" 2>/dev/null)

# ---- the KERNEL's verdict, read BEFORE the container is removed (8.2) ----
INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
echo "$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}} {{.State.StartedAt}} {{.State.FinishedAt}} {{.HostConfig.CpusetCpus}} {{.HostConfig.Memory}}' "$NAME" 2>/dev/null) $GOT_DIGEST" > "$BASE/${ARM}_${STAMP}.inspect.txt"   # the surviving kernel record (the grader's L-342 fallback)
sudo -n docker rm "$NAME" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$LOG" "$WORK" 2>/dev/null

# ===========================================================================
# G-CLOCK -- THE CAP AND THE GRADE READ THE SAME FRAME, AND BOTH FRAMES ARE
# PRINTED.  THE DEFECT THIS BLOCK EXISTS TO REMOVE, MEASURED ON D6 BY A PEER
# LANE 2026-08-27 AND CONFIRMED PRESENT IN SO-1a AND SO-1b:
#
#   the cap is a `timeout -k 60 $TMO` INSIDE the container (the `docker run`
#   line above), while `WALL=$((T1-T0))` brackets `docker run -d` PLUS the image
#   start PLUS up to one full `sleep 10` of poll granularity ON THE HOST.  An arm
#   that runs exactly to its own registered deadline therefore records a HOST
#   wall ABOVE the cap and trips its own `within_cap` limb -- A GATE FAIL
#   MANUFACTURED BY THE MEASUREMENT FRAME, NOT BY THE RUN.  At 4 ranks the poll
#   granularity alone is 10 x 4 / 60 = 0.667 core-min of pure frame error.
#
# THE REPAIR IS NOT A WIDER CAP.  Silently widening a cap to absorb a frame
# error hides the error and spends the difference.  Instead BOTH frames are
# measured from records that already exist -- `.State.StartedAt` and
# `.State.FinishedAt` are the KERNEL's own container clock, written into
# `<ARM>_<stamp>.inspect.txt` above -- and the grader is registered to read:
#   * CORE_MIN_CONTAINER  -> the CAP GATE (G10), the frame the deadline lives in;
#   * CORE_MIN            -> the COST CLAIM, the frame the box is occupied in,
#                            which is the honest billing figure and is larger.
# The difference is written to the ledger as CLOCK_FRAME_DELTA_CORE_MIN and is
# this family's FIRST MEASUREMENT of the gap rather than an estimate of it.
# An unreadable container clock is INFRASTRUCTURE (L-342): CORE_MIN_CONTAINER
# reads NOT_MEASURED and the grader is registered to fall back to the HOST frame
# AND SAY SO -- never to pass a cap limb it could not evaluate.
# ===========================================================================
CORE_MIN=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
CSTART=$(sudo -n docker inspect --format '{{.State.StartedAt}}' "$NAME" 2>/dev/null)
CFIN=$(sudo -n docker inspect --format '{{.State.FinishedAt}}' "$NAME" 2>/dev/null)
CWALL=$(CSTART="$CSTART" CFIN="$CFIN" python3 -c "
import os, datetime
def p(t):
    t = (t or '').strip()
    if not t or t.startswith('0001-01-01'):
        return None
    if t.endswith('Z'):
        t = t[:-1]
    if '.' in t:
        h, f = t.split('.', 1)
        f = (f + '000000')[:6]
        t = h + '.' + f
    try:
        return datetime.datetime.fromisoformat(t)
    except Exception:
        return None
a = p(os.environ.get('CSTART'))
b = p(os.environ.get('CFIN'))
print('%.3f' % (b - a).total_seconds() if (a and b and b >= a) else 'NOT_MEASURED')
" 2>/dev/null)
test -n "$CWALL" || CWALL=NOT_MEASURED
if [ "$CWALL" = "NOT_MEASURED" ]; then
  CORE_MIN_CONTAINER=NOT_MEASURED
  CLOCK_DELTA=NOT_MEASURED
else
  CORE_MIN_CONTAINER=$(python3 -c "print(round($CWALL*$RANKS/60.0,3))")
  CLOCK_DELTA=$(python3 -c "print(round($CORE_MIN-$CORE_MIN_CONTAINER,3))")
fi
echo "SO1CR_G_CLOCK arm=$ARM host_wall_s=$WALL container_wall_s=$CWALL ranks=$RANKS host_core_min=$CORE_MIN container_core_min=$CORE_MIN_CONTAINER clock_frame_delta_core_min=$CLOCK_DELTA cap_core_min=$CAP enforced_in_container_wall_s=$TMO gate_frame=CONTAINER cost_frame=HOST"
MEMAVAIL_POST=$(python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))")
LEDGER="$BASE/ledger.txt"
{
  echo "ARM=$ARM ROW=$ROW DECOMP=$DECOMP IMG=$IMG DIGEST=$GOT_DIGEST rc=$rc wall_s=$WALL container_wall_s=$CWALL ranks=$RANKS core_min=$CORE_MIN core_min_container=$CORE_MIN_CONTAINER clock_frame_delta_core_min=$CLOCK_DELTA cap_core_min=$CAP enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM inspect(exit,oomkilled)=[$INSPECT] memavail_pre_GiB=$MEMAVAIL_GIB memavail_post_GiB=$MEMAVAIL_POST cpuset=$CPUSET delivered_cores_mean=[$DELIVERED] siblings_pre=[$SIBLINGS_PRE] siblings_post=[$SIBLINGS_POST] log=$(basename "$LOG") stamp=$STAMP"
  grep -a "D4S_CONTAINER_UID\|D4S_IDWARP_SO_MD5\|D4S_DEADLINE_IN_CONTAINER_S\|SO1CR_DECOMP " "$LOG" | head -4   # the strings the container prints
} | tee -a "$LEDGER"
test -s "$LOG" && touch "$LOG.ok.${STAMP}"   # L-252 provenance sentinel
echo "STAMP=$STAMP RC=$rc CORE_MIN=$CORE_MIN CORE_MIN_CONTAINER=$CORE_MIN_CONTAINER"
exit $rc
