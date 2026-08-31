#!/usr/bin/env bash
# Curriculum SO-3aR2 arm launcher -- NACA0012 INCOMPRESSIBLE (DASimpleFoam),
# ALPHA-MULTIPOINT.  Derived from curriculum_SO2a/so2a_run_arm.sh; every
# reference to SO-2a below its title is a CITATION OF THE PARENT, not a stale
# self-reference -- this line was one, and it survived the rename because the
# rename swept `SO2a` and the title spelled it `SO-2a`.
# drag-min-at-fixed-lift, the FD-VERIFIED GRADIENT RUNG of Sanaa's shape-
# optimisation ladder SO-1.  TWO ROWS (shipped + patched), adjoint X + central-FD
# table F on BOTH the objective CD and the equality constraint CL.
#
# DERIVED from `cases/dafoam/ladder-a/A1/curriculum_D15/d15_run_arm.sh`
# (md5 796a2de5b894e8fcdbfab99af6fbf09d) with the REGISTERED DELTAS listed in
# PREREGISTRATION.md section 7 and recorded in so3ar2_run_arm_DELTAS_from_d15.diff:
# item/root names; the INCOMPRESSIBLE tutorial as the source; forbidden roots
# extended with D15's, D16's, D17's, AV-1's and AV-2's; RANKS 1 ON EVERY ARM
# (DAFOAM_CHARTER.md section 5, serial before parallel); cpuset 9; the cap table;
# the staged instruments; the arm commands.  Container-printed strings (D4S_*)
# are inherited UNCHANGED so the grader greps what the launcher writes.
#
# THE AGE-GUARD DATUM IS RESOLVED BY EXISTENCE HERE TOO, AND ITS NAME IS RECORDED.
# AV-1 and AV-2 both returned NOT A RESULT on 2026-08-27 with every physics
# artefact intact because a frozen grader pinned the datum to the NAME `0/U` while
# this tutorial's `writeCompression on` rewrites it as `0/U.gz` on a serial arm.
# This launcher resolves the datum over BOTH names and writes the one it used to
# `.so3ar2_age_datum_ref` beside the epoch, so the grader is not left inferring it.
#
# CAP DISCIPLINE (the failure this file exists not to repeat).  A peer lane
# today registered a 3.0 core-min cap and its launcher enforced 6.0 by
# copy-forward with no assertion.  Here the caps are NOT arguments.  They are
# constants in the table below, the table is reproduced verbatim in
# PREREGISTRATION.md §8, this file's md5 is frozen there, and the launcher
# ASSERTS that the wall timeout it is about to enforce equals CAP_CORE_MIN*60/RANKS
# to the second.  A cap that disagrees aborts the arm before the container runs.
#
# `set -e` DOES NOT GATE at the top level of a harness Bash call and
# `( set -e; ... )` does not gate either.  Every step below gates explicitly
# with `|| { echo ABORT...; exit N; }`.
#
# 8.2: NO --rm, so `docker inspect .State.ExitCode/.State.OOMKilled` survives
# the arm and the KERNEL's verdict is read, not the harness's.
set -uo pipefail

# ===========================================================================
# THE LEDGER ROW IS EMITTED BY THIS FUNCTION AND BY NOTHING ELSE, AND THE
# COMPARATOR'S SELFTEST SOURCES IT.
#
# Sanaa's birth requirement, 2026-08-28: a planted control must be "written by
# the real producer's code, read through the real reader".  The ledger row's
# real producer is THIS FILE.  SO-1a's comparator selftest reproduced the row
# format in a Python constant (`ROWFMT`), so a launcher/reader divergence would
# have left the suite green and the reader blind on the real run.  Here
# `so3ar2_grade.py:_ledger_rows_via_launcher` runs
#     bash -c '. so3ar2_run_arm.sh --source-only; so3ar2_ledger_row ...'
# and every fixture row comes out of these bytes.  If this format and the
# reader's regex ever diverge, the fixture rows stop parsing and the suite
# fails LOUDLY instead of passing quietly.
#
# 21 positional arguments, in the order the row prints them.
# ===========================================================================
so3ar2_ledger_row() {
  echo "ARM=$1 ROW=$2 IMG=$3 DIGEST=$4 rc=$5 wall_s=$6 ranks=$7 core_min=$8 cap_core_min=$9 enforced_wall_s=${10} enforced_core_min=${11} memory=${12} inspect(exit,oomkilled)=[${13}] memavail_pre_GiB=${14} memavail_post_GiB=${15} cpuset=${16} delivered_cores_mean=[${17}] siblings_pre=[${18}] siblings_post=[${19}] log=${20} stamp=${21}"
}

# ===========================================================================
# THE REGISTERED TABLES LIVE ABOVE `--source-only`, AND THAT IS A SO-3aR2 DELTA.
#
# The parent defined cap_core_min/cap_memory/ranks_of and its cpuset BELOW the
# early return, so `--source-only` exposed the LEDGER ROW and nothing else.  A
# cross-file check therefore could not READ the launcher's registered values,
# and on 2026-08-31 a mutation drive MEASURED the consequence: changing CPUSET
# 14 -> 7 and the X-arm cap 15.0 -> 9.0 left the comparator's 91-unit suite
# fully GREEN, because the fixture passes those values in as ARGUMENTS from the
# COMPARATOR'S own constants and never reads the launcher's.
#
# These are PURE TABLES: they read nothing, write nothing, and abort nothing.
# Moving them above the early return exposes them to so3ar2_groot5_selftest.sh's
# (x) legs and changes no runtime behaviour -- EVERY GUARD, EVERY READ AND
# EVERY DESTRUCTIVE ACT REMAINS BELOW IT, which is the property the parent's
# comment is actually protecting.
# ===========================================================================

CPUSET=14   # see the placement disclosure below, at first use

cap_core_min() {
  case "$1" in
    MESH)     echo 5.0 ;;
    X-S|X-P)  echo 15.0 ;;
    F-S|F-P)  echo 40.0 ;;
    *)  echo "" ;;
  esac
}

cap_memory() {
  case "$1" in
    MESH|X-S|X-P|F-S|F-P) echo 12g ;;
    *) echo "" ;;
  esac
}

ranks_of() {
  case "$1" in
    MESH|X-S|X-P|F-S|F-P) echo 1 ;;
    *) echo "" ;;
  esac
}

row_of() {
  case "$1" in
    MESH)  echo SHIPPED ;;
    X-S)   echo SHIPPED ;;
    F-S)   echo SHIPPED ;;
    X-P)   echo PATCHED ;;
    F-P)   echo PATCHED ;;
    *)     echo "" ;;
  esac
}

# `--source-only` defines the functions and TABLES above and RETURNS.  It must come before
# every guard, every read and every destructive act, and it must not be
# reachable from a normal invocation: the launcher's first positional argument
# is an ARM NAME, and no arm is called `--source-only`.
if [ "${1:-}" = "--source-only" ]; then
  return 0 2>/dev/null || exit 0
fi

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
ITEM=SO3aR2
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR2-a1-naca0012-alpha-multipoint-gradient
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
#
# ---- SO-3aR2 REGISTERED DELTA, AND IT IS A REPAIR OF AN INHERITED FICTION.
# ---- The list this file was derived from was READ AGAINST THE DISK on
# ---- 2026-08-31 rather than trusted.  TWO of its SO entries name roots that DO
# ---- NOT EXIST -- `CURRICULUM-SO1b-a1-naca0012-dragmin-opt` and
# ---- `CURRICULUM-SO1c-a1-naca0012-postopt` -- while FOUR roots that DO exist,
# ---- and hold real evidence, were NOT PROTECTED AT ALL:
# ----   CURRICULUM-SO1bR-a1-naca0012-dragmin-opt      (SO-1b's actual successor)
# ----   CURRICULUM-SO1c-a1-naca0012-dragmin-npinv     (SO-1c, LIVE on this box)
# ----   CURRICULUM-SO2a-...-geometric-constraint-gradient
# ----   CURRICULUM-SO3aR2F-a1-naca0012-alpha-feasibility
# ---- SO-2a's root is the one THIS ITEM'S OWN PREREGISTRATION line 5 cites as
# ---- the MEASURED basis for SO-2a's PASS.
# ----
# ---- AND THE HONEST SIZE OF THE FINDING, because the first draft of this
# ---- comment OVERSTATED IT and the drive said so.  All four roots were ALREADY
# ---- refused -- at G-ROOT.1, not here -- because G-ROOT.1 requires BASE to
# ---- resolve to THIS ITEM'S registered root and refuses everything else.  It
# ---- was measured: each of the four was driven through this launcher and each
# ---- returned rc=3 `ABORT G-ROOT.1`.  G-ROOT.2 is therefore a SECOND LINE OF
# ---- DEFENCE THAT CANNOT FIRE WHILE G-ROOT.1 STANDS, and this repair does not
# ---- close a live hole.  What a stale list DOES cost is real but smaller: the
# ---- refusal message names WHOSE evidence was protected, and a list naming two
# ---- roots that do not exist while omitting four that do would say the wrong
# ---- thing, or nothing, on the day G-ROOT.1 is ever weakened or normalised
# ---- differently.  Recording the smaller true finding rather than the larger
# ---- false one is the point.
# ---- This is the SO-1b lesson in another costume: SO-1b pinned its dependency
# ---- BY GLOB, the glob could not match the successor artefact `SO1aR_grade_*`,
# ---- and it fired into a guaranteed outcome.  A GUARD PINNED TO A NAME THAT
# ---- MOVED PROTECTS NOTHING AND SAYS NOTHING WHILE IT FAILS.  The dead entries
# ---- are KEPT -- a name that is free today can be taken tomorrow, and keeping
# ---- them costs one string comparison each -- and the four live ones are ADDED.
# ---- so3ar2_groot5_selftest.sh drives every entry that is ON DISK and prints
# ---- `not_on_disk` beside the rest rather than reporting a refusal it did not
# ---- see.
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
/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-postopt
/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt
/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-dragmin-npinv
/home/ubuntu/certonomous-runs/CURRICULUM-SO2a-a1-naca0012-geometric-constraint-gradient
/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR2F-a1-naca0012-alpha-feasibility
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
# SO-3aR2 STAGE-2 PLACEMENT (PREREGISTRATION.md section 5: "cpuset fixed at Stage 2
# and DISCLOSED THERE AGAINST EVERY LIVE SIBLING'S REGISTERED SET").  cpuset 14,
# ONE core, because every arm runs at np = 1.  NOT core 0.
#
# THE DISCLOSURE, read rather than recalled, on this 16-core box:
#   SO-1c  holds 10 (MESH) and 10,11,12,13 (solver arms)  [so1c_run_arm.sh:172-178]
#   SO-2a  held  9                                        [so2a_run_arm.sh:178]
# 14 is disjoint from both, so SO-3aR2 does NOT inherit the parent's DISCLOSED
# OVERLAP with D4-SHIPPED's registered 5,6,7,9.  At np = 1 the grader's
# delivered-cores floor does not apply (so3ar2_grade.py g_placement: dl_ok is True
# when ARM_RANKS == 1), so an overlap would cost WALL TIME and could not fail G12
# -- but a disjoint placement is AVAILABLE here, and taking it is cheaper than
# reporting the exposure.  G12 compares this value against so3ar2_grade.py's
# CPUSET_REGISTERED, so the two cannot drift apart silently.

# For containerised MPI the conditioning variable is CONCURRENT CONTAINERS, not
# loadavg -- `uptime` will lie.  Censused before and after every arm.
container_census() {
  sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^so3ar2_" | tr '\n' ',' | sed 's/,$//'
}

# ---- REGISTERED CAP TABLE (PREREGISTRATION.md §4, verbatim) ---------------
# SO-3aR2's registered caps (PREREGISTRATION.md section 4).  THIS TABLE IS A
# COMMENT AND THE CODE BELOW IS THE AUTHORITY; the derivation inherited the
# PARENT's numbers here (5.0/10.0/10.0/25.0/25.0 at 4g) while the code already
# carried SO-3aR2's, so the two disagreed for a while and only the code was right.
# so3ar2_groot5_selftest.sh now PARSES BOTH and refuses if they diverge, because a
# comment table that contradicts its own code is what a reviewer in a hurry reads.
#   arm    ranks  core-min cap   in-container wall   memory cap
#   MESH     1        5.0            300 s             12g
#   X-S      1       15.0            900 s             12g
#   X-P      1       15.0            900 s             12g
#   F-S      1       40.0           2400 s             12g
#   F-P      1       40.0           2400 s             12g
# SECTION 5: 12 GiB per arm, RAISED from the family's 4 g convention with the
# arithmetic shown -- D13 MEASURED peak RSS 1.70 GiB for this 4,032-cell 2-D case
# at np = 1, and three DASolver instances in one process is bounded CRUDELY above
# by 3 x 1.70 ~ 5.1 GiB plus one shared mesh/FFD/IDWarp footprint.  That bound is
# [EXTRAPOLATED] and NOT a measurement -- no multipoint arm has ever run on this
# case -- so 12 g carries better than 2x headroom over it, and the item's own
# first arm MEASURES it.
# np = 1 ON EVERY ARM by registration: DAFOAM_CHARTER.md section 5 (serial before
# parallel), and A4's 16,600x decomposition effect is removed from the chain.

# ---- REGISTERED TOOLCHAIN, BY DIGEST, never by tag (DAFOAM_CHARTER §11) ---
# PATCHED IDWarp : dafoam-idwarp-rot:v1
#   sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
# SHIPPED (stock): dafoam/opt-packages:latest
#   sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
IMG_SHIPPED_DIGEST=sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc

# ---- FROZEN INSTRUMENT HASHES (PREREGISTRATION.md §7, verbatim) ----------
# ---- SECTION 18.3.  THE MOST DANGEROUS THING THE DERIVATION INHERITED.
# The parent carried MD5_RUNSCRIPT=0557da51... and MD5_XG=85b2a416... -- REAL
# md5s OF DIFFERENT FILES (SO-2a's runScript, which is a byte copy of the shipped
# tutorial, and so2a_xg.py).  Carried across a rename they would have kept the
# SHAPE of a legitimate pin while naming files that do not exist here.  A pin
# that LOOKS right is worse than one that is obviously unset: the sentinel below
# cannot match any md5 -- 32 hex digits is the shape of one and this string is not
# -- so `md5sum -c` FAILS CLOSED and this launcher refuses to stage rather than
# run against a mis-pinned instrument.
#
# THE PINS ARE SET ONCE, AT THE STAGE-2 AMENDMENT, FOR ALL NINE TOGETHER, and not
# before -- even though so3ar2_runScript.py and so3ar2_xf.py now exist and their md5s
# could be written here today.  A pin table filled in for the files that happen to
# exist, inside the executable that stages every arm, is the SO2a-DRIVER-DEF-1
# shape in the place it does the most damage: it would read agreement on every pin
# it holds while a file this launcher copies is still missing.  Existence is a
# DIFFERENT question from md5 agreement and cannot be inferred from any level of
# it.  so3ar2_chain_driver.sh:60-71 makes the same choice for the same reason.
# ---- STAGE-2 AMENDMENT, 2026-08-31: THE PINS ARE SET, ALL NINE TOGETHER.
# The fail-closed sentinel `MD5_UNSET` is REMOVED rather than left defined at
# 32 zeros, for two reasons.  It has no remaining consumer; and a dead constant
# whose VALUE is a well-formed md5 is a fail-open waiting to be re-used -- and it
# would be counted as a pin by the completeness leg that now compares
# pins-DECLARED against pins-DRIVEN.
MD5_RUNSCRIPT=d9ac0faf5b5e49d686db74db4cdbc1aa   # so3ar2_runScript.py
MD5_XF=d6e9117d5971b56fefc5f96d366acf74          # so3ar2_xf.py
# so3ar2_decomposeParDict is ADOPTED BYTE-IDENTICALLY from the parent (one line
# changed from the tutorial's: numberOfSubdomains 1), it EXISTS, and this is the
# value so3ar2_chain_driver.sh:70 already pins it at.  It is not a partial table: it
# is the one file whose bytes are unchanged from an already-frozen ancestor.
MD5_DECOMP=e6f1b0060944bc86d6dff56480ad2bd4

ARM="${1:-}"; IMG="${2:-}"
test -n "$ARM" || { echo "ABORT usage: so3ar2_run_arm.sh <MESH|X-S|F-S|X-P|F-P> <image>"; exit 64; }
test -n "$IMG" || { echo "ABORT usage: so3ar2_run_arm.sh <MESH|X-S|F-S|X-P|F-P> <image>"; exit 64; }
RANKS=$(ranks_of "$ARM"); test -n "$RANKS" || { echo "ABORT arm $ARM carries no registered rank count"; exit 64; }

# ---- G-ROOT.5 (ADDENDUM 2) -- A LIVE ARM IS NEVER RE-STAGED.  G-ROOT.1-.3
# ---- see only ledger rows; a queue-runner re-firing this launcher on a
# ---- RUNNING arm would pass them and reach `rm -rf "$WORK"` (the shape the
# ---- D7FR lane found at d7fr_run_arm.sh:319).  Two live readings, taken
# ---- BEFORE any destructive act:
# ----   (a) a RUNNING container carrying this item's prefix and this arm;
# ----   (b) a driver pidfile in the run root naming a LIVE pid that is not an
# ----       ancestor of this process (a second driver), or whose cwd is the
# ----       run root.  A stale pidfile (dead pid) does not block.
LIVE_SAME_ARM=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^so3ar2_${ARM}_" 2>/dev/null | grep "^so3ar2_${ARM}_" | head -3 | tr '\n' ',' | sed 's/,$//')
if [ -n "$LIVE_SAME_ARM" ]; then
  echo "ABORT G-ROOT.5 a RUNNING container already carries this item's prefix and arm: [$LIVE_SAME_ARM]"
  echo "  Re-staging would remove the live arm directory under it.  REFUSED."
  exit 3
fi
PIDFILE="$BASE/so3ar2_driver.pid"
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
echo "$MD5_RUNSCRIPT  $BASE/so3ar2_runScript.py"       | md5sum -c - || { echo "ABORT runScript md5"; exit 4; }
echo "$MD5_XF  $BASE/so3ar2_xf.py"                     | md5sum -c - || { echo "ABORT so3ar2_xf.py md5"; exit 4; }
echo "$MD5_DECOMP  $BASE/base/system/decomposeParDict" | md5sum -c - || { echo "ABORT decomposeParDict md5"; exit 4; }

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
# DAFOAM_CHARTER.md §11 makes the HASH the identity.  D15 REGISTERED DELTA: the
# row is carried in the ARM NAME (-S shipped, -P patched; MESH on shipped --
# mesh generation does not touch IDWarp), and a mismatch refuses.
# ---- THE ARM -> ROW MAPPING IS A REGISTERED TABLE OVER FULL ARM NAMES.
# The parent derived it from an ARM-NAME SUFFIX GLOB (`MESH|*-S)`), which is a
# coincidence of spelling and exactly the derivation the SO-1c post-mortem
# forbids: SO-1c died at its second arm because one of THREE call sites of a row
# label was repaired, and the scope had been set by a fence written in the
# singular.  A glob also cannot refuse an arm this item never declared -- `Q-S`
# would have matched `*-S` and been handed the SHIPPED row.  This table lists
# every DECLARED arm by its FULL NAME, so an undeclared arm falls through to the
# empty case and REFUSES, and it is the same mapping so3ar2_grade.py registers as
# ARM_ROW (MESH/X-S/F-S -> SHIPPED, X-P/F-P -> PATCHED).
WANT_ROW=$(row_of "$ARM")
test -n "$WANT_ROW" || {
  echo "ABORT arm $ARM carries no registered row.  SO-3aR2 declares MESH X-S F-S X-P F-P"
  echo "  and nothing else; a row is READ FROM THE TABLE, never derived from a name suffix."
  exit 64; }
test "$ROW" = "$WANT_ROW" || {
  echo "ABORT G-ROW arm $ARM is registered on the $WANT_ROW row; got ROW=$ROW ($IMG)."
  echo "  A row a run claims and a row it ran must be the same hash.  REFUSED."
  exit 4; }
echo "D4S_G_ROW_PASS row=$ROW digest=$GOT_DIGEST"
echo "D4_IMAGE_OK row=$ROW image=$IMG digest=$GOT_DIGEST"

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="so3ar2_${ARM}_${STAMP}"
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
  echo "$AGE_DATUM" > "$WORK/.so3ar2_age_datum"
  echo "$DATUM_NAME" > "$WORK/.so3ar2_age_datum_ref"
  echo "D4_G_COLD OK arm=$ARM age_datum_epoch=$AGE_DATUM datum_file=$DATUM_NAME resolved_by=EXISTENCE"
else
  test -d "$BASE/MESH" || { echo "ABORT arm $ARM expects an existing MESH/ from arm MESH"; exit 5; }
  test -f "$BASE/MESH/constant/polyMesh/boundary" || { echo "ABORT arm $ARM: MESH/ carries no constant/polyMesh/boundary"; exit 5; }
  { [ -f "$BASE/MESH/0/U" ] || [ -f "$BASE/MESH/0/U.gz" ]; } || { echo "ABORT arm $ARM: MESH/ carries neither 0/U nor 0/U.gz"; exit 5; }
  sudo -n rm -rf "$WORK" 2>/dev/null
  cp -a "$BASE/MESH" "$WORK" || { echo "ABORT stage copy from MESH"; exit 4; }
  rm -f "$WORK/so3ar2_cmd.sh" "$WORK/checkMesh.log" "$WORK/logMeshGeneration.txt" "$WORK/volumeMesh.xyz" "$WORK/surfaceMesh.xyz" "$WORK/.so3ar2_age_datum" "$WORK/.so3ar2_age_datum_ref" 2>/dev/null
  cp -a "$BASE/so3ar2_runScript.py" "$BASE/so3ar2_xf.py" "$WORK/" || { echo "ABORT stage instruments"; exit 4; }
  # ---- SO-3aR2 REGISTERED DELTA: ONE FULL CASE COPY PER OPERATING POINT ------
  # This is the whole repair.  SO-3aR gave three DAFoamBuilders no run_directory,
  # so three DASolvers renamed into one /mnt/X-S/0.0001 and the item died at arm
  # 2 of 5 [MEASURED, curriculum_SO3aR/RESULTS.md section 6].  D6R had already
  # solved it on A2 -- `d6r_run_arm.sh:313` stages mp04/ mp05/ mp06/, one per
  # point -- and A1 never carried it forward.  The names here are `mp0 mp1 mp2`
  # and MUST equal `so3ar2_runScript.py:RUN_DIRS`'s values; `so3ar2_collision_leg.py`
  # limb L4 drives that agreement and limb L4b proves the check able to fail.
  # The FFD and the instruments stay at the arm directory, which is the
  # container's working directory, so each point's `run_directory` holds a case
  # and nothing else.
  for mp in mp0 mp1 mp2; do
    cp -a "$BASE/MESH" "$WORK/$mp" || { echo "ABORT stage $mp copy from MESH"; exit 4; }
    rm -f "$WORK/$mp/so3ar2_cmd.sh" "$WORK/$mp/checkMesh.log" "$WORK/$mp/logMeshGeneration.txt" \
          "$WORK/$mp/volumeMesh.xyz" "$WORK/$mp/surfaceMesh.xyz" \
          "$WORK/$mp/.so3ar2_age_datum" "$WORK/$mp/.so3ar2_age_datum_ref" 2>/dev/null
    test -n "$(ls -d "$WORK/$mp"/processor* 2>/dev/null)" && { echo "ABORT G-COLD $mp processor* present"; exit 5; }
    for d in "$WORK/$mp"/*/; do
      n=$(basename "$d")
      case "$n" in 0|0.orig) ;; [0-9]*) echo "ABORT G-COLD $mp time dir present: $n"; exit 5 ;; esac
    done
    { [ -f "$WORK/$mp/0/U" ] || [ -f "$WORK/$mp/0/U.gz" ]; } || { echo "ABORT G-COLD $mp carries neither 0/U nor 0/U.gz"; exit 5; }
  done
  # COLD START, verified BEFORE the launch (D2 G8), and the AGE GUARD's datum:
  # 0/ is touched LAST at stage time, so every artifact the run produces must
  # be strictly newer than 0/U or it did not come from this run.
  for bad in "$WORK/reports" "$WORK/so3ar2_X.json" "$WORK/so3ar2_F.json" "$WORK/so3ar2_F.jsonl" "$WORK/so3ar2_X.jsonl" "$WORK/dRdWColoring_2.bin"; do
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
  echo "$AGE_DATUM" > "$WORK/.so3ar2_age_datum"
  echo "$DATUM_NAME" > "$WORK/.so3ar2_age_datum_ref"
  echo "SO3AR2_WRITE_COMPRESSION $(grep -a writeCompression "$WORK/system/controlDict" 2>/dev/null | head -1 | tr -d ';')"
  echo "D4_G_COLD OK arm=$ARM age_datum_epoch=$AGE_DATUM datum_file=$DATUM_NAME resolved_by=EXISTENCE"
  # ---- G-IC0's DATUM, PER POINT.  SO-3aR2 REGISTERED DELTA -------------------
  # The dafoam-supervisor MEASURED on D19, 2026-08-31T21:54Z, that DAFoam REWRITES
  # `0/U` IN THE CASE DIRECTORY DURING a SERIAL (ranks=1) run -- S1/0/U.gz mtime
  # 21:53:52, 43 s into a 51 s run, on the only ranks=1 arm.  Parallel arms write
  # into processor*/ and do not touch 0/.  DAFOAM_CHARTER.md section 6 already
  # records that pyDAFoam writes the primal end state back into the time-0
  # directory AT RUN END; D19 is the first time this lab dated it MID-RUN.
  # THE PER-POINT run_directory REPAIR DOES NOT CURE THIS AND IS NOT CLAIMED TO:
  # it stops three DASolvers renaming into ONE destination; it does nothing about
  # ONE DASolver rewriting the 0/ inside its OWN directory between evaluations,
  # and this item runs 34 declared evaluations per F arm at ranks=1.  So the datum
  # is stamped PER POINT here, LAST, and G-IC0 reads it.  Every point's 0/ carries
  # a stage-time mtime and a hash; an evaluation that started from a mutated 0/ is
  # a FINDING, and the gate is registered to report MEASURED or OPEN, never to
  # absorb it.
  for mp in mp0 mp1 mp2; do
    if   [ -f "$WORK/$mp/0/U" ];    then MPD=0/U
    elif [ -f "$WORK/$mp/0/U.gz" ]; then MPD=0/U.gz
    else echo "ABORT G-IC0 $mp neither 0/U nor 0/U.gz"; exit 5; fi
    touch "$WORK/$mp/0"/* || { echo "ABORT age-guard datum $mp"; exit 5; }
    MPE=$(stat -c '%Y' "$WORK/$mp/$MPD")
    echo "$MPE" > "$WORK/$mp/.so3ar2_age_datum"
    echo "$MPD" > "$WORK/$mp/.so3ar2_age_datum_ref"
    md5sum "$WORK/$mp/0"/* > "$WORK/$mp/.so3ar2_ic0_md5" 2>/dev/null || { echo "ABORT G-IC0 md5 $mp"; exit 5; }
    echo "SO3AR2_G_IC0_DATUM point=$mp age_datum_epoch=$MPE datum_file=$MPD n_ic_fields=$(wc -l < "$WORK/$mp/.so3ar2_ic0_md5")"
  done
fi

case "$ARM" in
  MESH)     CMD="bash preProcessing.sh && checkMesh > checkMesh.log 2>&1; echo SO3AR2_CHECKMESH_RC \$?; sha256sum constant/polyMesh/points* ; grep -a 'cells:' checkMesh.log" ;;
  X-S|X-P)  CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python so3ar2_xf.py -mode X" ;;
  F-S|F-P)  CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python so3ar2_xf.py -mode F" ;;
esac

# ---- ADDENDUM 2: the arm command goes to a FILE the container executes under
# ---- its OWN `timeout` at the registered cap wall (TMO), so the deadline is
# ---- INSIDE the container and survives every host shell.  `-k 60` escalates
# ---- TERM to KILL; the kernel exit code (124/137) is then the record.
CMDFILE="$WORK/so3ar2_cmd.sh"
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
     timeout -k 60 $TMO bash /mnt/$ARM/so3ar2_cmd.sh" > /dev/null 2>&1 \
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

# ---- G-IC0, MEASURED AFTER THE RUN AND REPORTED, NEVER GATED ---------------
# The dafoam-supervisor measured on D19 (2026-08-31T21:54Z) that DAFoam rewrites
# `0/U` in the case directory DURING a serial run -- S1/0/U.gz mtime 43 s into a
# 51 s run at ranks=1.  DAFOAM_CHARTER.md:237-239 already records the run-END
# write and makes the staged-copy pattern mandatory; D19's addition is dating it
# MID-RUN.  This item runs 34 declared evaluations per F arm at ranks=1, so the
# mechanism is LIVE here, and the per-point run_directory repair does NOT cure it
# (it stops three DASolvers sharing ONE destination; it says nothing about one
# DASolver rewriting the 0/ inside its own directory).
#
# THE EXPECTED MAGNITUDE IS SMALL AND IS REGISTERED AS SUCH, from the
# supervisor's own D19 instrument: eta_raw 1.3011e-10 and 9.6522e-11 across two
# arms, eta_floored false, against CD_baseline 0.0146 -- about 9e-9 relative.
# So this is REPORTED WITH ITS NUMBER and is NOT a launch blocker.  If this
# item's own eta comes back ORDERS larger than 1e-10 that is a FINDING and the
# item says so rather than absorbing it.
#
# The before-hashes were taken at stage time, LAST, so they date the intended
# initial condition.  Re-hashing here answers the question directly on disk
# rather than inferring it from a mtime alone.
if [ -d "$WORK/mp0" ]; then
  IC0="$BASE/${ARM}_IC0.json"
  {
    printf '{"arm": "%s", "row": "%s", "stamp": "%s", "gate": "G-IC0", "status": "REPORTED, NEVER GATED", "points": [' "$ARM" "$ROW" "$STAMP"
    sep=""
    for mp in mp0 mp1 mp2; do
      NB=0; NC=0; PRE="ABSENT"
      if [ -f "$WORK/$mp/.so3ar2_ic0_md5" ]; then
        PRE=$(cat "$WORK/$mp/.so3ar2_age_datum" 2>/dev/null)
        NB=$(wc -l < "$WORK/$mp/.so3ar2_ic0_md5")
        NC=$(md5sum -c "$WORK/$mp/.so3ar2_ic0_md5" 2>/dev/null | grep -c ': FAILED$')
      fi
      PM=$(stat -c '%Y' "$WORK/$mp/0" 2>/dev/null || echo 0)
      printf '%s{"point": "%s", "n_ic_fields": %s, "n_changed_during_run": %s, "stage_datum_epoch": "%s", "post_run_0_mtime_epoch": %s}' \
             "$sep" "$mp" "$NB" "$NC" "$PRE" "$PM"
      sep=", "
    done
    printf '], "note": "n_changed_during_run > 0 means DAFoam rewrote the initial condition inside that point private case copy during this arm -- the D19 mechanism, MEASURED here rather than assumed. It is reported with its count and never gates."}\n'
  } > "$IC0"
  echo "SO3AR2_G_IC0 arm=$ARM file=$(basename "$IC0") $(python3 -c "
import json
d=json.load(open('$IC0'))
print(' '.join('%s:%d/%d' % (p['point'], p['n_changed_during_run'], p['n_ic_fields']) for p in d['points']))
" 2>/dev/null)"
fi

CORE_MIN=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
MEMAVAIL_POST=$(python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))")
LEDGER="$BASE/ledger.txt"
{
  so3ar2_ledger_row "$ARM" "$ROW" "$IMG" "$GOT_DIGEST" "$rc" "$WALL" "$RANKS" "$CORE_MIN" "$CAP" "$TMO" "$BACKCHECK" "$MEM" "$INSPECT" "$MEMAVAIL_GIB" "$MEMAVAIL_POST" "$CPUSET" "$DELIVERED" "$SIBLINGS_PRE" "$SIBLINGS_POST" "$(basename "$LOG")" "$STAMP"
  grep -a "D4S_CONTAINER_UID\|D4S_IDWARP_SO_MD5\|D4S_DEADLINE_IN_CONTAINER_S" "$LOG" | head -3   # the strings the container prints
} | tee -a "$LEDGER"
test -s "$LOG" && touch "$LOG.ok.${STAMP}"   # L-252 provenance sentinel
echo "STAMP=$STAMP RC=$rc CORE_MIN=$CORE_MIN"
exit $rc
