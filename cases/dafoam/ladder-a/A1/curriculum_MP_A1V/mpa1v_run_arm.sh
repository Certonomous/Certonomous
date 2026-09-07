#!/usr/bin/env bash
# Curriculum MP-A1V arm launcher -- NACA0012 INCOMPRESSIBLE (DASimpleFoam),
# ALPHA-MULTIPOINT FD-VERIFICATION (ride).  DERIVED from curriculum_MP_A1/
# mpa1_run_arm.sh with the DELTAS in mpa1v_run_arm_DELTAS_from_mpa1.diff: arms
# MESH/FV-S/FV-P (FD-verification only, no O/X arm); the FD arm's xopt is RIDDEN
# from MP-A1's frozen run root (MPA1_BASE, read-only); pins fixpointed to mpa1v_*;
# cpuset 12.  The line below is a CITATION OF THE MP-A1/SO-2a lineage, not a stale
# reference to SO-2a below its title is a CITATION OF THE PARENT, not a stale
# self-reference -- this line was one, and it survived the rename because the
# rename swept `SO2a` and the title spelled it `SO-2a`.
# drag-min-at-fixed-lift, the FD-VERIFIED GRADIENT RUNG of Sanaa's shape-
# optimisation ladder SO-1.  TWO ROWS (shipped + patched), adjoint X + central-FD
# table F on BOTH the objective CD and the equality constraint CL.
#
# DERIVED from `cases/dafoam/ladder-a/A1/curriculum_D15/d15_run_arm.sh`
# (md5 796a2de5b894e8fcdbfab99af6fbf09d) with the REGISTERED DELTAS listed in
# PREREGISTRATION.md section 7 and recorded in mpa1_run_arm_DELTAS_from_d15.diff:
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
# `.mpa1_age_datum_ref` beside the epoch, so the grader is not left inferring it.
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
# `mpa1_grade.py:_ledger_rows_via_launcher` runs
#     bash -c '. mpa1_run_arm.sh --source-only; mpa1_ledger_row ...'
# and every fixture row comes out of these bytes.  If this format and the
# reader's regex ever diverge, the fixture rows stop parsing and the suite
# fails LOUDLY instead of passing quietly.
#
# 21 positional arguments, in the order the row prints them.
# ===========================================================================
mpa1_ledger_row() {
  echo "ARM=$1 ROW=$2 IMG=$3 DIGEST=$4 rc=$5 wall_s=$6 ranks=$7 core_min=$8 cap_core_min=$9 enforced_wall_s=${10} enforced_core_min=${11} memory=${12} inspect(exit,oomkilled)=[${13}] memavail_pre_GiB=${14} memavail_post_GiB=${15} cpuset=${16} delivered_cores_mean=[${17}] siblings_pre=[${18}] siblings_post=[${19}] log=${20} stamp=${21}"
}

# ===========================================================================
# THE REGISTERED TABLES LIVE ABOVE `--source-only`, AND THAT IS A MP-A1 DELTA.
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
# Moving them above the early return exposes them to mpa1_groot5_selftest.sh's
# (x) legs and changes no runtime behaviour -- EVERY GUARD, EVERY READ AND
# EVERY DESTRUCTIVE ACT REMAINS BELOW IT, which is the property the parent's
# comment is actually protecting.
# ===========================================================================

CPUSET=12   # FREE core chosen at authoring (only d9succ/15 live; 12 in 1 registered set,
           # not 0, not 15, not T4d).  Re-confirm occupancy at launch.  Provisional to freeze;
           # re-read then; NOT core 0, NOT 15/D9successor, NOT T4d's).  G12 gates this
           # against mpa1v_grade.py:CPUSET_REGISTERED, so the two cannot drift apart.

cap_core_min() {
  case "$1" in
    MESH)       echo 5.0 ;;
    FV-S|FV-P)  echo 14.0 ;;
    *)  echo "" ;;
  esac
}

cap_memory() {
  case "$1" in
    MESH|FV-S|FV-P) echo 12g ;;
    *) echo "" ;;
  esac
}

# ---- np = 1 ON EVERY ARM, AND THIS IS A HARD DESIGN CONSTRAINT, NOT A DEFAULT.
# SO-3aR2's capability cell says in terms that it establishes "NOTHING about
# Mach, an optimum, or np != 1", and `DAFOAM_CHARTER.md` section 5 forbids
# carrying an FD reference across np: *"A gradient verified at one np is a
# statement about that np and is never carried to another."*  MP-A1's FD
# inheritance from SO-3aR2 is VOID at any other rank count, so the table below is
# not a performance choice -- it is the condition on the inheritance.  A4's
# 16,600x decomposition effect (np=4 scotch 8.95 % against np=4 simple 4x1x1
# 0.00054 % on ONE mesh) is what a np != 1 arm would readmit.
ranks_of() {
  case "$1" in
    MESH|FV-S|FV-P) echo 1 ;;
    *) echo "" ;;
  esac
}

row_of() {
  case "$1" in
    MESH)   echo SHIPPED ;;
    FV-S)   echo SHIPPED ;;
    FV-P)   echo PATCHED ;;
    *)      echo "" ;;
  esac
}

# ---- THE ENDPOINT ARMS' SOURCE OF THE OPTIMUM, AS A REGISTERED TABLE OVER FULL
# ---- ARM NAMES.  `DAFOAM_CHARTER.md` section 9 requires the FD check AT THE
# ---- FINAL DESIGN POINT, so XE/FE must read the design vector the O arm on
# ---- THEIR OWN ROW produced.  Reading the other row's optimum would compare a
# ---- PATCHED gradient against a SHIPPED design and the number would be about
# ---- neither -- and it is exactly the shape that killed SO-1c, where one call
# ---- site of a row label was repaired and two were not.  This is a TABLE over
# ---- full names, never a suffix derivation: `Q-S` falls through to empty and
# ---- the caller refuses.
# RIDE: the FD arm's optimum comes from MP-A1's frozen O arm (under MPA1_BASE), by
# ROW.  FV-S rides MP-A1's SHIPPED optimum (O-S), FV-P the PATCHED (O-P).  A TABLE
# over full names; an arm not in it gets empty and is refused.
xopt_arm_of() {
  case "$1" in
    FV-S)  echo O-S ;;
    FV-P)  echo O-P ;;
    *)     echo "" ;;
  esac
}

# ===========================================================================
# THE C-188 CAP FRAME -- THE REPAIR, AND WHY EQUALITY WAS THE DEFECT.
#
# THE DEFECT, MEASURED IN THIS FILE'S OWN ANCESTOR.  `so3ar2_run_arm.sh:404`
# reads, verbatim:
#
#     TMO=$(python3 -c "print(int(round($CAP*60.0/$RANKS)))")
#     BACKCHECK=$(python3 -c "print('%.6f' % ($TMO*$RANKS/60.0))")
#     ... if abs(cap-back) > 0.02: ABORT
#
# The in-container deadline is set to consume the ENTIRE registered cap and the
# backcheck ASSERTS THAT EQUALITY.  But the deadline is enforced INSIDE the
# container while the ledger measures HOST-FRAME wall -- `T0` is taken before
# `docker run` and `T1` after `docker logs` -- and `timeout -k 60` adds up to 60
# further seconds of kill grace after the deadline fires.  So an arm that REACHES
# its deadline records `core_min > cap` BY CONSTRUCTION.  Not by accident, not
# under load: by construction, every time.
#
# THAT IS C-188 EXACTLY.  `docs/COST_CALIBRATION.md` C-188: D6's `O_mp` arm was
# given a 2,000.0 core-min cap at ranks = 4, so TMO = 30,000 s; it reached the
# deadline and the ledger recorded **30,008 s wall = 2,000.533 core-min against a
# 2,000.0 cap**.  An 8-second host-frame overhead turned a correctly-bounded run
# into a recorded overrun, and `CLAUDE.md` rule 12 says an overrun STOPS THE RUN.
#
# WHY SO-3aR2 NEVER WOKE IT: its five arms finished at 12 % of cap
# (`ratio_actual_over_predicted` 0.58-0.88 against caps 2-5x the prediction), so
# no arm ever reached its deadline.  AN OPTIMISATION RUN TO CONVERGENCE IS
# PRECISELY THE ARM SHAPE THAT REACHES ITS DEADLINE, which is why the repair
# lands here and not in the gradient rung.
#
# THE REPAIR: reserve the host-frame margin BEFORE deriving the deadline, and
# make the backcheck an INEQUALITY over the whole frame rather than an equality
# over the container's half of it.
#
#     TMO = floor(CAP*60/RANKS) - CAP_MARGIN_S
#     assert (TMO + CAP_MARGIN_S) * RANKS / 60 <= CAP
#
# `floor` rather than `round`, because `round` can round UP and hand back the
# fraction of a second the margin just reserved.
#
# CAP_MARGIN_S = 180 IS REGISTERED HERE, BEFORE ANY COMPUTE, and it is composed
# rather than guessed: 60 s of `timeout -k` kill grace, plus the container start,
# the `loadDAFoam.sh` source and the `idwarp` import (all of which run OUTSIDE the
# in-container `timeout` and INSIDE the host-frame wall), plus `docker logs` and
# `docker inspect` at teardown.  C-188's measured host-frame overhead on the
# non-grace path was 8 s, so 180 s carries better than 2x headroom over the worst
# case 60 + 8.
#
# AND THE BRANCH THAT REFUSES, because a margin is not free.  An arm whose cap is
# smaller than the margin cannot be enforced in the host frame AT ALL, and a
# negative deadline is not a smaller budget -- it is a launcher that would pass a
# negative number to `timeout`.  `CAP_MIN_TMO_S` is the floor below which this
# launcher REFUSES TO START, and the registered remedy is to RAISE THE CAP in the
# pre-registration, never to lower the margin: lowering the margin is exactly the
# move that re-creates C-188.
#
# A CAP IS A CEILING, NOT A PREDICTION.  MESH's cap is 5.0 core-min while its
# prediction is 0.19; the cap exists to bound a runaway and the prediction is
# what `CLAUDE.md` rule 12's estimate-versus-actual ratio is taken against.  The
# margin is charged to the ceiling, not to the prediction.
# ===========================================================================
CAP_MARGIN_S=180        # host-frame reserve: kill grace + start + preamble + teardown
CAP_KILL_GRACE_S=60     # the `-k` value on the in-container `timeout`
CAP_MIN_TMO_S=60        # below this an arm is unrunnable under its cap; RAISE THE CAP

# Prints the enforced in-container deadline in seconds, or exits 1 with nothing
# on stdout when the cap cannot carry the margin.  A pure function: it reads
# nothing and writes nothing, so the selftest can drive it directly.
tmo_for() {
  python3 -c "
import math, sys
cap = float('$1'); ranks = int('$2'); margin = int('$CAP_MARGIN_S')
tmo = int(math.floor(cap * 60.0 / ranks)) - margin
if tmo < int('$CAP_MIN_TMO_S'):
    sys.exit(1)
print(tmo)"
}

# Prints the enforced HOST-FRAME core-minutes and exits non-zero if they exceed
# the registered cap.  THE INEQUALITY IS THE REPAIR: the ancestor asserted
# equality on the container's half of the frame and therefore asserted the
# overrun into existence.
capframe_backcheck() {
  python3 -c "
import sys
tmo = int('$1'); ranks = int('$2'); cap = float('$3')
enforced = (tmo + int('$CAP_MARGIN_S')) * ranks / 60.0
print('%.6f' % enforced)
sys.exit(0 if enforced <= cap + 1e-9 else 1)"
}

# THE ANCESTOR'S FORM, KEPT AS AN EXECUTABLE QUOTATION so the red leg can drive
# the defect rather than describe it.  It is never called on a launch path -- the
# `--source-only` guard below is what lets the selftest reach it.
tmo_for_C188_DEFECTIVE_FORM() {
  python3 -c "print(int(round(float('$1') * 60.0 / int('$2'))))"
}

# `--source-only` defines the functions and TABLES above and RETURNS.  It must come before
# every guard, every read and every destructive act, and it must not be
# reachable from a normal invocation: the launcher's first positional argument
# is an ARM NAME, and no arm is called `--source-only`.
if [ "${1:-}" = "--source-only" ]; then
  return 0 2>/dev/null || exit 0
fi

# ---- THE NOT_FROZEN PERMISSION GATE.  Placed AFTER the --source-only return so
# ---- the selftest can still source the functions above, and BEFORE every guard,
# ---- read and destructive act below.  This item is a DRAFT and is NOT FROZEN;
# ---- CLAUDE.md rule 2 forbids compute before the freeze.  While a `NOT_FROZEN`
# ---- sentinel sits beside this launcher a real arm invocation REFUSES to stage
# ---- or launch, before it touches a run root.  The freeze act removes it.
MPA1_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -e "$MPA1_HERE/NOT_FROZEN" ]; then
  echo "MPA1_REFUSE_NOT_FROZEN a NOT_FROZEN sentinel is present beside mpa1_run_arm.sh:" >&2
  echo "  this pre-registration is NOT frozen; CLAUDE.md rule 2 forbids compute before the" >&2
  echo "  freeze.  REFUSED.  (The freeze act removes the sentinel.)" >&2
  exit 70
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
ITEM=MPA1V
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-MP-A1V-a1-naca0012-multipoint-fixedlift-fdverify-directDVcentral
BASE="${BASE:-$REGISTERED_BASE}"
# RIDE (PREREGISTRATION 1.1, O-1): MP-A1V's FD arms are verified at MP-A1's
# DEMONSTRATED final design.  MPA1_BASE is MP-A1's frozen run root, READ-ONLY, and
# is used ONLY to source mpa1_xopt.json for the ride (G-XOPT below).  It is NOT this
# item's registered root; the G-ROOT.1 guard still binds BASE to REGISTERED_BASE.
MPA1_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-MP-A1-a1-naca0012-alpha-multipoint-fixedlift-optimisation

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
# ---- MP-A1 REGISTERED DELTA, AND IT IS A REPAIR OF A FICTION THIS FAMILY HAS NOW
# ---- CARRIED THROUGH THREE GENERATIONS.  A MECHANICAL RENAME MOVES TOKENS; IT
# ---- CANNOT MAKE PROSE TRUE.
# ----
# ---- WHAT WAS MEASURED, 2026-09-01, by `test -d` against the disk rather than by
# ---- reading the ancestor's comment:
# ----   * SO-3aR's list carried `CURRICULUM-SO3aRF-a1-naca0012-alpha-feasibility`
# ----     (`so3ar_run_arm.sh:228`).  THAT DIRECTORY DOES NOT EXIST.
# ----   * SO-3aR2's derivation renamed the token to
# ----     `CURRICULUM-SO3aR2F-a1-naca0012-alpha-feasibility`
# ----     (`so3ar2_run_arm.sh:228`).  THAT DIRECTORY DOES NOT EXIST EITHER.
# ----   * The real feasibility run root, on disk with real evidence in it, is
# ----     `CURRICULUM-SO3aF-a1-naca0012-alpha-feasibility`, and NEITHER ancestor
# ----     protected it.
# ----   * `so3ar2_run_arm.sh:174-178` describes that entry, in terms, as one of
# ----     "FOUR roots that DO exist, and hold real evidence".  Three of the four
# ----     do; that one does not, and did not when the sentence was written.  The
# ----     sentence was TRUE OF MP-A1a's ROOT and was carried across two renames
# ----     that each moved the token and left the claim standing.
# ----   * The two DEAD entries the ancestor's comment names --
# ----     `CURRICULUM-SO1b-a1-naca0012-dragmin-opt` and
# ----     `CURRICULUM-SO1c-a1-naca0012-postopt` -- are STILL ABSENT, so that half
# ----     of the ancestor's finding stands and is re-confirmed here.
# ----
# ---- WHAT THIS FILE DOES ABOUT IT.  `CURRICULUM-SO3aF-...` is ADDED under its
# ---- real name; the three gradient-rung roots of this item's own ancestry --
# ---- MP-A1a, SO-3aR and SO-3aR2 -- are ADDED, because SO-3aR2's holds a GRADED,
# ---- CLOSED record (item GATE FAIL, graded 2026-08-31T23:02:21Z) and this
# ---- launcher's staging path begins `rm -rf "$WORK"`.  The renamed ghost
# ---- `CURRICULUM-MP-A1F-...` is KEPT, because a name that is free today can be
# ---- taken tomorrow and keeping it costs one string comparison -- but it is
# ---- named here as A GHOST and is no longer described as a root that exists.
# ----
# ---- AND THE HONEST SIZE OF THE FINDING, which is smaller than it looks and is
# ---- stated at its true size rather than at its most alarming one.  Every one of
# ---- these roots is ALREADY refused at G-ROOT.1, not here, because G-ROOT.1
# ---- requires BASE to resolve to THIS ITEM'S registered root and refuses
# ---- everything else.  G-ROOT.2 IS A SECOND LINE OF DEFENCE THAT CANNOT FIRE
# ---- WHILE G-ROOT.1 STANDS, and none of this closed a live hole.  What a stale
# ---- list costs is real but smaller: the refusal message names WHOSE evidence
# ---- was just protected, and a message naming a directory that does not exist
# ---- says the wrong thing on the day G-ROOT.1 is weakened or normalised
# ---- differently.  Recording the smaller true finding rather than the larger
# ---- false one is the point -- and that sentence, unlike the one above it, was
# ---- carried forward because it was RE-CHECKED, not because it was inherited.
# ---- `mpa1_run_arm_selftest.sh` leg (r6) drives every entry in this list against
# ---- the disk and prints `GHOST` beside the ones that are not there, so the next
# ---- derivation inherits a measurement instead of a claim.
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
/home/ubuntu/certonomous-runs/CURRICULUM-MP-A1F-a1-naca0012-alpha-feasibility
/home/ubuntu/certonomous-runs/CURRICULUM-SO3aF-a1-naca0012-alpha-feasibility
/home/ubuntu/certonomous-runs/CURRICULUM-SO3a-a1-naca0012-alpha-multipoint-gradient
/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR-a1-naca0012-alpha-multipoint-gradient
/home/ubuntu/certonomous-runs/CURRICULUM-SO3aR2-a1-naca0012-alpha-multipoint-gradient
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
# MP-A1 STAGE-2 PLACEMENT (PREREGISTRATION.md section 5: "cpuset fixed at Stage 2
# and DISCLOSED THERE AGAINST EVERY LIVE SIBLING'S REGISTERED SET").  cpuset 14,
# ONE core, because every arm runs at np = 1.  NOT core 0.
#
# THE DISCLOSURE, read rather than recalled, on this 16-core box:
#   SO-1c  holds 10 (MESH) and 10,11,12,13 (solver arms)  [so1c_run_arm.sh:172-178]
#   SO-2a  held  9                                        [so2a_run_arm.sh:178]
# 14 is disjoint from both, so MP-A1 does NOT inherit the parent's DISCLOSED
# OVERLAP with D4-SHIPPED's registered 5,6,7,9.  At np = 1 the grader's
# delivered-cores floor does not apply (mpa1_grade.py g_placement: dl_ok is True
# when ARM_RANKS == 1), so an overlap would cost WALL TIME and could not fail G12
# -- but a disjoint placement is AVAILABLE here, and taking it is cheaper than
# reporting the exposure.  G12 compares this value against mpa1_grade.py's
# CPUSET_REGISTERED, so the two cannot drift apart silently.

# For containerised MPI the conditioning variable is CONCURRENT CONTAINERS, not
# loadavg -- `uptime` will lie.  Censused before and after every arm.
container_census() {
  sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^mpa1_" | tr '\n' ',' | sed 's/,$//'
}

# ---- REGISTERED CAP TABLE (PREREGISTRATION.md §4, verbatim) ---------------
# MP-A1's registered caps (PREREGISTRATION.md section 4).  THIS TABLE IS A
# COMMENT AND THE CODE BELOW IS THE AUTHORITY; the derivation inherited the
# PARENT's numbers here (5.0/10.0/10.0/25.0/25.0 at 4g) while the code already
# carried MP-A1's, so the two disagreed for a while and only the code was right.
# mpa1_groot5_selftest.sh now PARSES BOTH and refuses if they diverge, because a
# comment table that contradicts its own code is what a reviewer in a hurry reads.
# AND THE WALL COLUMN IS THE **REPAIRED** ONE.  Every `in-container wall` below
# is `floor(cap*60/ranks) - CAP_MARGIN_S`, NOT `cap*60/ranks`: the 180 s host-
# frame margin is charged to the CEILING here so the ledger cannot record
# `core_min > cap` on an arm that reaches its deadline.  See the C-188 CAP FRAME
# block.  `mpa1_run_arm_selftest.sh` leg (r2) PARSES this comment and the code and
# refuses if they diverge, because a comment table that contradicts its own code
# is what a reviewer in a hurry reads.
#   arm    ranks  core-min cap   in-container wall (=cap*60/ranks, C-188 frame in code)   memory cap
#   MESH     1        5.0            (see code)                                            12g
#   FV-S     1       14.0            (see code)                                            12g
#   FV-P     1       14.0            (see code)                                            12g
#   (MP-A1V: no O arm, no X arm -- both RIDDEN; the FD caps carry MP-A1's proven
#    FE cap 14.0 for divergence headroom.  Item ceiling 33.0 = 5.0+14.0+14.0, the
#    authority for which is mpa1v_grade.py:ITEM_CEILING_CORE_MIN, asserted in main().)
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
# before -- even though mpa1_runScript.py and mpa1_xf.py now exist and their md5s
# could be written here today.  A pin table filled in for the files that happen to
# exist, inside the executable that stages every arm, is the SO2a-DRIVER-DEF-1
# shape in the place it does the most damage: it would read agreement on every pin
# it holds while a file this launcher copies is still missing.  Existence is a
# DIFFERENT question from md5 agreement and cannot be inferred from any level of
# it.  mpa1_chain_driver.sh:60-71 makes the same choice for the same reason.
# ---- STAGE-2 AMENDMENT, 2026-08-31: THE PINS ARE SET, ALL NINE TOGETHER.
# The fail-closed sentinel `MD5_UNSET` is REMOVED rather than left defined at
# 32 zeros, for two reasons.  It has no remaining consumer; and a dead constant
# whose VALUE is a well-formed md5 is a fail-open waiting to be re-used -- and it
# would be counted as a pin by the completeness leg that now compares
# pins-DECLARED against pins-DRIVEN.
MD5_RUNSCRIPT=bb3ba3a61b19dc8564e247cdb11e9147   # mpa1v_runScript.py (staged AS mpa1_runScript.py)
MD5_XF=ea53c04314f20c438de233101d5ce84d          # mpa1v_xf.py
# mpa1_decomposeParDict is ADOPTED BYTE-IDENTICALLY from the parent (one line
# changed from the tutorial's: numberOfSubdomains 1), it EXISTS, and this is the
# value mpa1_chain_driver.sh:70 already pins it at.  It is not a partial table: it
# is the one file whose bytes are unchanged from an already-frozen ancestor.
MD5_DECOMP=e6f1b0060944bc86d6dff56480ad2bd4

ARM="${1:-}"; IMG="${2:-}"
test -n "$ARM" || { echo "ABORT usage: mpa1v_run_arm.sh <MESH|FV-S|FV-P> <image>"; exit 64; }
test -n "$IMG" || { echo "ABORT usage: mpa1v_run_arm.sh <MESH|FV-S|FV-P> <image>"; exit 64; }
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
LIVE_SAME_ARM=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^mpa1_${ARM}_" 2>/dev/null | grep "^mpa1_${ARM}_" | head -3 | tr '\n' ',' | sed 's/,$//')
if [ -n "$LIVE_SAME_ARM" ]; then
  echo "ABORT G-ROOT.5 a RUNNING container already carries this item's prefix and arm: [$LIVE_SAME_ARM]"
  echo "  Re-staging would remove the live arm directory under it.  REFUSED."
  exit 3
fi
PIDFILE="$BASE/mpa1_driver.pid"
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

# THE ASSERTION, IN ITS C-188-REPAIRED FORM.  The enforced in-container deadline
# reserves the host-frame margin FIRST, and the backcheck is an INEQUALITY over
# the WHOLE frame -- deadline plus margin -- rather than an equality over the
# container's half of it.  See the CAP FRAME block above for the measurement that
# earned each of these three lines.
TMO=$(tmo_for "$CAP" "$RANKS") || {
  echo "ABORT C-188 CAP FRAME arm=$ARM cap=$CAP core-min at ranks=$RANKS leaves an"
  echo "  enforceable in-container deadline below ${CAP_MIN_TMO_S}s once the ${CAP_MARGIN_S}s host-frame"
  echo "  margin is reserved (kill grace ${CAP_KILL_GRACE_S}s + container start + preamble + teardown)."
  echo "  THE REGISTERED REMEDY IS TO RAISE THE CAP IN THE PRE-REGISTRATION."
  echo "  Lowering the margin is the move that re-creates C-188 and is REFUSED here."
  exit 65; }
BACKCHECK=$(capframe_backcheck "$TMO" "$RANKS" "$CAP") || {
  echo "ABORT C-188 CAP FRAME backcheck arm=$ARM enforced host-frame core-min=$BACKCHECK exceeds cap=$CAP"
  exit 65; }
# THE DEFECTIVE FORM, COMPUTED AND PRINTED BESIDE THE REPAIRED ONE ON EVERY
# LAUNCH.  It is never used.  It is printed so the ledger and the arm log carry,
# for every arm this item ever runs, the number the ancestor would have enforced
# and the host-frame overrun it would have recorded -- so a reader can see the
# repair working rather than read that it was made.
OLD_TMO=$(tmo_for_C188_DEFECTIVE_FORM "$CAP" "$RANKS")
OLD_WORST=$(python3 -c "print('%.6f' % (($OLD_TMO + $CAP_KILL_GRACE_S + 8) * $RANKS / 60.0))")
NEW_WORST=$(python3 -c "print('%.6f' % (($TMO + $CAP_KILL_GRACE_S + 8) * $RANKS / 60.0))")
echo "D4_CAP_ASSERT arm=$ARM registered_core_min=$CAP ranks=$RANKS enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM margin_s=$CAP_MARGIN_S"
echo "MPA1_C188_FRAME arm=$ARM repaired_tmo_s=$TMO ancestor_tmo_s=$OLD_TMO"
echo "MPA1_C188_FRAME arm=$ARM worst_case_host_core_min repaired=$NEW_WORST ancestor=$OLD_WORST cap=$CAP overhead_s=8_MEASURED_C188 kill_grace_s=$CAP_KILL_GRACE_S"

# ---- host state, read before ranks are claimed ---------------------------
MEMAVAIL_KB=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
MEMAVAIL_GIB=$(python3 -c "print('%.2f' % ($MEMAVAIL_KB/1048576.0))")
LOAD=$(awk '{print $1}' /proc/loadavg)
SIBLINGS_PRE=$(container_census)
echo "D4_HOST_PRE arm=$ARM MemAvailable_GiB=$MEMAVAIL_GIB load1=$LOAD cpuset=$CPUSET siblings_pre=[$SIBLINGS_PRE]"

test "$(stat -c '%a' "$BASE")" = "777" || { echo "ABORT L-251 run root mode $(stat -c '%a' "$BASE")"; exit 4; }

# ---- staged-instrument identity, re-asserted before EVERY launch ---------
echo "$MD5_RUNSCRIPT  $BASE/mpa1_runScript.py"       | md5sum -c - || { echo "ABORT runScript md5"; exit 4; }
echo "$MD5_XF  $BASE/mpa1v_xf.py"                    | md5sum -c - || { echo "ABORT mpa1v_xf.py md5"; exit 4; }
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
# empty case and REFUSES, and it is the same mapping mpa1_grade.py registers as
# ARM_ROW (MESH/O-S/XE-S/FE-S -> SHIPPED, O-P/XE-P/FE-P -> PATCHED).
WANT_ROW=$(row_of "$ARM")
test -n "$WANT_ROW" || {
  echo "ABORT arm $ARM carries no registered row.  MP-A1 declares MESH O-S XE-S FE-S O-P XE-P FE-P"
  echo "  and nothing else; a row is READ FROM THE TABLE, never derived from a name suffix."
  exit 64; }
test "$ROW" = "$WANT_ROW" || {
  echo "ABORT G-ROW arm $ARM is registered on the $WANT_ROW row; got ROW=$ROW ($IMG)."
  echo "  A row a run claims and a row it ran must be the same hash.  REFUSED."
  exit 4; }
echo "D4S_G_ROW_PASS row=$ROW digest=$GOT_DIGEST"
echo "D4_IMAGE_OK row=$ROW image=$IMG digest=$GOT_DIGEST"

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="mpa1_${ARM}_${STAMP}"
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
  echo "$AGE_DATUM" > "$WORK/.mpa1_age_datum"
  echo "$DATUM_NAME" > "$WORK/.mpa1_age_datum_ref"
  echo "D4_G_COLD OK arm=$ARM age_datum_epoch=$AGE_DATUM datum_file=$DATUM_NAME resolved_by=EXISTENCE"
else
  test -d "$BASE/MESH" || { echo "ABORT arm $ARM expects an existing MESH/ from arm MESH"; exit 5; }
  test -f "$BASE/MESH/constant/polyMesh/boundary" || { echo "ABORT arm $ARM: MESH/ carries no constant/polyMesh/boundary"; exit 5; }
  { [ -f "$BASE/MESH/0/U" ] || [ -f "$BASE/MESH/0/U.gz" ]; } || { echo "ABORT arm $ARM: MESH/ carries neither 0/U nor 0/U.gz"; exit 5; }
  sudo -n rm -rf "$WORK" 2>/dev/null
  cp -a "$BASE/MESH" "$WORK" || { echo "ABORT stage copy from MESH"; exit 4; }
  rm -f "$WORK/mpa1_cmd.sh" "$WORK/checkMesh.log" "$WORK/logMeshGeneration.txt" "$WORK/volumeMesh.xyz" "$WORK/surfaceMesh.xyz" "$WORK/.mpa1_age_datum" "$WORK/.mpa1_age_datum_ref" 2>/dev/null
  # `mpa1_stall.py` is staged INTO THE ARM because the producer imports it inside
  # the container to write its own stall reading; `mpa1_age_guard.py` is NOT
  # staged into the arm -- it runs on the HOST, against the arm directory, and a
  # guard living inside the thing it guards is one `rm -rf` from being absent.
  cp -a "$BASE/mpa1_runScript.py" "$BASE/mpa1v_xf.py" "$BASE/mpa1v_stall.py" "$WORK/" \
    || { echo "ABORT stage instruments"; exit 4; }
  # ---- MP-A1 REGISTERED DELTA: ONE FULL CASE COPY PER OPERATING POINT ------
  # This is the whole repair.  SO-3aR gave three DAFoamBuilders no run_directory,
  # so three DASolvers renamed into one /mnt/X-S/0.0001 and the item died at arm
  # 2 of 5 [MEASURED, curriculum_SO3aR/RESULTS.md section 6].  D6R had already
  # solved it on A2 -- `d6r_run_arm.sh:313` stages mp04/ mp05/ mp06/, one per
  # point -- and A1 never carried it forward.  The names here are `mp0 mp1 mp2`
  # and MUST equal `mpa1_runScript.py:RUN_DIRS`'s values; `mpa1_collision_leg.py`
  # limb L4 drives that agreement and limb L4b proves the check able to fail.
  # The FFD and the instruments stay at the arm directory, which is the
  # container's working directory, so each point's `run_directory` holds a case
  # and nothing else.
  for mp in mp0 mp1 mp2; do
    cp -a "$BASE/MESH" "$WORK/$mp" || { echo "ABORT stage $mp copy from MESH"; exit 4; }
    rm -f "$WORK/$mp/mpa1_cmd.sh" "$WORK/$mp/checkMesh.log" "$WORK/$mp/logMeshGeneration.txt" \
          "$WORK/$mp/volumeMesh.xyz" "$WORK/$mp/surfaceMesh.xyz" \
          "$WORK/$mp/.mpa1_age_datum" "$WORK/$mp/.mpa1_age_datum_ref" 2>/dev/null
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
  for bad in "$WORK/reports" "$WORK/mpa1_X.json" "$WORK/mpa1_F.json" "$WORK/mpa1_F.jsonl" "$WORK/mpa1_X.jsonl" \
             "$WORK/mpa1_O.json" "$WORK/mpa1_xopt.json" "$WORK/opt_IPOPT.txt" "$WORK/MPA1_STALL_ABORT" \
             "$WORK/dRdWColoring_2.bin"; do
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
  echo "$AGE_DATUM" > "$WORK/.mpa1_age_datum"
  echo "$DATUM_NAME" > "$WORK/.mpa1_age_datum_ref"
  echo "MPA1_WRITE_COMPRESSION $(grep -a writeCompression "$WORK/system/controlDict" 2>/dev/null | head -1 | tr -d ';')"
  echo "D4_G_COLD OK arm=$ARM age_datum_epoch=$AGE_DATUM datum_file=$DATUM_NAME resolved_by=EXISTENCE"
  # ---- G-IC0's DATUM, PER POINT.  MP-A1 REGISTERED DELTA -------------------
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
    echo "$MPE" > "$WORK/$mp/.mpa1_age_datum"
    echo "$MPD" > "$WORK/$mp/.mpa1_age_datum_ref"
    md5sum "$WORK/$mp/0"/* > "$WORK/$mp/.mpa1_ic0_md5" 2>/dev/null || { echo "ABORT G-IC0 md5 $mp"; exit 5; }
    echo "MPA1_G_IC0_DATUM point=$mp age_datum_epoch=$MPE datum_file=$MPD n_ic_fields=$(wc -l < "$WORK/$mp/.mpa1_ic0_md5")"
  done

  # ---- G-XOPT.  THE ENDPOINT ARMS READ THEIR OWN ROW'S OPTIMUM, BY TABLE. ----
  # `DAFOAM_CHARTER.md` section 9: *"Every optimisation reports a finite-
  # difference check of the gradient AT ITS FINAL DESIGN POINT, not only at the
  # baseline."*  The charter's stated reason is THIS toolchain: the IDWarp
  # rotation defect is GUARANTEED to fire at the undeformed baseline
  # (`axisMag = 1e-15 < tol = sqrt(eps)` makes branch 0 certain at every
  # non-corner surface node) and its second regime behaves DIFFERENTLY just above
  # the threshold -- 1e-5 rad -> 4.1e-08, 1e-6 -> 6.7e-05, 5e-8 -> 1.2e-02
  # (`ROOTCAUSE_getRotationMatrix3d.md` sections 1.6, 6.4).  A gradient verified
  # at iteration 0 IS NOT VERIFIED at iteration 47, and the two regimes are on
  # opposite sides of the guard.  SO-3aR2 supplies iteration 0 ONLY.
  #
  # THE ROW MUST MATCH.  An endpoint FD on the PATCHED row that read the SHIPPED
  # optimum would compare a patched gradient against a design neither toolchain
  # produced.  `xopt_arm_of` is a TABLE over FULL arm names -- never a suffix
  # derivation -- and an arm not in it gets an empty answer and is refused.
  XOPT_ARM=$(xopt_arm_of "$ARM")
  if [ -n "$XOPT_ARM" ]; then
    # RIDE: the optimum is MP-A1's frozen mpa1_xopt.json, read READ-ONLY from
    # MPA1_BASE (MP-A1V runs no O arm).  The row stamped inside it is checked below.
    XOPT_SRC="$MPA1_BASE/$XOPT_ARM/mpa1_xopt.json"
    test -f "$XOPT_SRC" || {
      echo "ABORT G-XOPT arm $ARM needs MP-A1's ridden final design from arm $XOPT_ARM,"
      echo "  and $XOPT_SRC does not exist under MPA1_BASE.  The endpoint FD check"
      echo "  section 9 requires cannot be run against a design that was never produced."
      exit 5; }
    # THE ROW STAMPED INSIDE THE ARTEFACT MUST BE THIS ARM'S ROW.  Reading the
    # filename is not a check: the file could have been copied.  The producer
    # writes `row` into the JSON and it is compared against `row_of "$ARM"`.
    XOPT_ROW=$(python3 -c "
import json,sys
try: d=json.load(open('$XOPT_SRC'))
except Exception as e: sys.stderr.write(str(e)+'\n'); sys.exit(1)
print(d.get('row',''))" 2>/dev/null)
    test "$XOPT_ROW" = "$(row_of "$ARM")" || {
      echo "ABORT G-XOPT $XOPT_SRC is stamped row=[$XOPT_ROW] but arm $ARM is registered"
      echo "  on row [$(row_of "$ARM")].  An endpoint gradient must be verified at the"
      echo "  design point ITS OWN toolchain produced.  REFUSED."
      exit 5; }
    cp -a "$XOPT_SRC" "$WORK/mpa1_xopt.json" || { echo "ABORT G-XOPT stage copy"; exit 4; }
    XOPT_SHA=$(sha256sum "$WORK/mpa1_xopt.json" | cut -d' ' -f1)
    echo "MPA1_G_XOPT arm=$ARM row=$XOPT_ROW source_arm=$XOPT_ARM sha256=$XOPT_SHA n_dv=$(python3 -c "
import json; print(len(json.load(open('$WORK/mpa1_xopt.json')).get('shape',[])))")"
  fi

  # ---- THE MANIFEST AGE GUARD IS PINNED HERE, POST-STAGE AND PRE-LAUNCH. -----
  # `CLAUDE.md` rule 4's age guard dates a run from the case's own `0/T` on the
  # premise that it is touched last at launch.  THAT PREMISE IS FALSE HERE and
  # the falsity is MEASURED, not argued: the dafoam-supervisor measured on D19,
  # 2026-08-31T21:54Z, that DAFoam rewrites `0/U` in the case directory DURING a
  # ranks=1 run, and the rewrite also lands under `processor*/0/`.  The datum
  # form above (datum by EXISTENCE over both names, `is_compressed_twin`
  # recorded) already handles that and is CARRIED UNCHANGED.
  #
  # WHAT IS ADDED: a manifest by NAME AND CONTENT HASH, from
  # `cases/dafoam/a2b2r_age_guard.py`.  A COUNT IS NOT AN IDENTITY -- D19's count
  # clause passed 9-to-9 while SIX of the nine FILENAMES had changed (`T` ->
  # `T.gz`) under `writeCompression on`.  The write-target exclusion is ENFORCING
  # rather than descriptive: it is derived from the SAME enumeration the pinning
  # loop consumes, in one pass, so a record can never assert an exclusion the
  # code does not honour.  `mpa1_age_guard.py` leg (a3) proves a disagreement
  # between the two REFUSES.
  test -f "$BASE/mpa1_age_guard.py" || { echo "ABORT age guard instrument absent: $BASE/mpa1_age_guard.py"; exit 4; }
  python3 "$BASE/mpa1_age_guard.py" pin "$WORK" "$WORK/.mpa1_manifest.json" \
    || { echo "ABORT age-guard manifest pin failed for arm $ARM"; exit 5; }
fi

# ---- THE ARM COMMANDS.  A TABLE OVER FULL ARM NAMES; an undeclared arm leaves
# ---- CMD empty and is refused below.
case "$ARM" in
  MESH)       CMD="bash preProcessing.sh && checkMesh > checkMesh.log 2>&1; echo MPA1V_CHECKMESH_RC \$?; sha256sum constant/polyMesh/points* ; grep -a 'cells:' checkMesh.log" ;;
  FV-S|FV-P)  CMD="mpirun --allow-run-as-root -np $RANKS --bind-to core --report-bindings -x PYTHONPATH python mpa1v_xf.py -mode F -xopt mpa1_xopt.json" ;;
esac
test -n "${CMD:-}" || {
  echo "ABORT arm $ARM carries no registered command.  MP-A1V declares"
  echo "  MESH FV-S FV-P and nothing else (no O arm, no X arm -- both RIDDEN)."
  exit 64; }

# ---- ADDENDUM 2: the arm command goes to a FILE the container executes under
# ---- its OWN `timeout` at the registered cap wall (TMO), so the deadline is
# ---- INSIDE the container and survives every host shell.  `-k 60` escalates
# ---- TERM to KILL; the kernel exit code (124/137) is then the record.
CMDFILE="$WORK/mpa1_cmd.sh"
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
     timeout -k 60 $TMO bash /mnt/$ARM/mpa1_cmd.sh" > /dev/null 2>&1 \
  || { echo "ABORT could not start container"; exit 4; }

# ===========================================================================
# THE STALL WATCHDOG -- THE REGISTERED NUMERICAL STOP, ARMED ON THE O ARMS ONLY.
#
# `CLAUDE.md` rule 12: an overrun STOPS THE RUN.  The in-container deadline
# already bounds the spend, but a wall clock cannot tell the record WHY the run
# ended, and `DAFOAM_CHARTER.md` section 9 makes that a VERDICT difference.  This
# watchdog reads IPOPT's own iteration table through the frozen detector and
# stops the container when a REGISTERED numerical condition fires:
#
#   A. mpa1_stall.N_STALL (=8) consecutive majors with alpha_pr < 1e-3
#   B. dual infeasibility NON-DECREASING over 8 consecutive majors
#
# MEASURED ON C-188'S OWN ARTEFACT: condition A fires at major 34 of D6's 65,
# which is a 48 % saving on that run.  Across all 33 gradable IPOPT logs on this
# box condition A fires on exactly 2 -- both known stalls -- and on none of the
# 7 that ended `Maximum Number of Iterations Exceeded`, because A CAP IS NOT A
# STALL.  Condition B has NEVER fired on real evidence and is reported
# `NOT EXERCISED`, never as a passing control.
#
# IT IS A READER THAT CAN STOP, AND NOTHING ELSE.  It writes a marker and calls
# `docker stop`; it never edits an artefact, never touches a verdict, and its own
# failure cannot turn a stall into a pass -- an absent marker is reported
# NOT_MEASURED by the grader, and the grader RE-READS `opt_IPOPT.txt` itself.
# THE STOP IS NOT THE GATE.  Mapping a stall to `GATE REACHED` or `NOT A RESULT`
# is section 9's and lives in `mpa1_grade.py`; a watchdog that also graded could
# launder a stop into a pass by relabelling it here.
# ===========================================================================
STALL_MARKER="$WORK/MPA1_STALL_ABORT"
STALLDOG=""
case "$ARM" in
  O-S|O-P)
    if [ -f "$BASE/mpa1_stall.py" ]; then
      (
        while sudo -n docker ps -q --filter "name=^${NAME}$" 2>/dev/null | grep -q .; do
          sleep 30
          [ -f "$WORK/opt_IPOPT.txt" ] || continue
          VERD=$(python3 "$BASE/mpa1_stall.py" scan "$WORK/opt_IPOPT.txt" 2>/dev/null \
                 | python3 -c "
import sys, json
try: d = json.load(sys.stdin)
except Exception: print('READ_FAILED'); raise SystemExit
print('%s %s %s %s' % (d['stall'], d['stop_at_major'],
      d['condition_A_alpha_pr_run']['fired'], d['condition_B_inf_du_nondecreasing']['fired']))" 2>/dev/null)
          case "$VERD" in
            STALL\ *)
              set -- $VERD
              printf 'MPA1_STALL_ABORT arm=%s stop_at_major=%s condition_A=%s condition_B=%s n_stall_window=8 alpha_pr_min=1e-3 stamp=%s\n' \
                     "$ARM" "$2" "$3" "$4" "$(date -u +%Y%m%dT%H%M%SZ)" > "$STALL_MARKER"
              echo "MPA1_STALL_ABORT arm=$ARM stop_at_major=$2 condition_A=$3 condition_B=$4 action=DOCKER_STOP" | tee -a "$BASE/ledger.txt"
              sudo -n docker stop -t 30 "$NAME" >/dev/null 2>&1
              break ;;
          esac
        done
      ) &
      STALLDOG=$!
      echo "MPA1_STALLDOG arm=$ARM armed=yes pid=$STALLDOG poll_s=30 detector=$BASE/mpa1_stall.py"
    else
      # AN ABSENT WATCHDOG IS DECLARED, NEVER SILENTLY SKIPPED.  A guard whose
      # absence is invisible is worse than one that never fired.
      echo "MPA1_STALLDOG arm=$ARM armed=NO reason=detector_absent_at_$BASE/mpa1_stall.py -- THE STALL STOP IS NOT ARMED FOR THIS ARM"
    fi ;;
  *) echo "MPA1_STALLDOG arm=$ARM armed=no reason=not_an_optimisation_arm" ;;
esac

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
if [ -n "$STALLDOG" ]; then kill "$STALLDOG" 2>/dev/null; wait "$STALLDOG" 2>/dev/null; fi
if [ -f "$STALL_MARKER" ]; then
  echo "MPA1_STALL_FIRED arm=$ARM $(cat "$STALL_MARKER")"
else
  echo "MPA1_STALL_NOT_FIRED arm=$ARM -- the registered stall conditions did not fire; this is REPORTED, not read as convergence"
fi
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
      if [ -f "$WORK/$mp/.mpa1_ic0_md5" ]; then
        PRE=$(cat "$WORK/$mp/.mpa1_age_datum" 2>/dev/null)
        NB=$(wc -l < "$WORK/$mp/.mpa1_ic0_md5")
        NC=$(md5sum -c "$WORK/$mp/.mpa1_ic0_md5" 2>/dev/null | grep -c ': FAILED$')
      fi
      PM=$(stat -c '%Y' "$WORK/$mp/0" 2>/dev/null || echo 0)
      printf '%s{"point": "%s", "n_ic_fields": %s, "n_changed_during_run": %s, "stage_datum_epoch": "%s", "post_run_0_mtime_epoch": %s}' \
             "$sep" "$mp" "$NB" "$NC" "$PRE" "$PM"
      sep=", "
    done
    printf '], "note": "n_changed_during_run > 0 means DAFoam rewrote the initial condition inside that point private case copy during this arm -- the D19 mechanism, MEASURED here rather than assumed. It is reported with its count and never gates."}\n'
  } > "$IC0"
  echo "MPA1_G_IC0 arm=$ARM file=$(basename "$IC0") $(python3 -c "
import json
d=json.load(open('$IC0'))
print(' '.join('%s:%d/%d' % (p['point'], p['n_changed_during_run'], p['n_ic_fields']) for p in d['points']))
" 2>/dev/null)"
fi

# ---- THE MANIFEST AGE GUARD, VERIFIED POST-RUN.  Its reading is written to a
# ---- FILE the grader reads; the launcher does NOT convert it into a verdict and
# ---- does NOT abort on it, because a bookkeeping refusal must never void
# ---- physics (Sanaa's universal rule, 2026-08-26).  The grader splits the
# ---- physics clauses from the infrastructure ones and this is the grader's
# ---- input, not its conclusion.
AGE_OUT="$BASE/${ARM}_ageguard.txt"
if [ -f "$WORK/.mpa1_manifest.json" ] && [ -f "$BASE/mpa1_age_guard.py" ]; then
  DATUM_REF_FILE="$WORK/$(cat "$WORK/.mpa1_age_datum_ref" 2>/dev/null)"
  ARTS=""
  for a in "$WORK/mpa1_X.json" "$WORK/mpa1_F.json" "$WORK/mpa1_O.json" "$WORK/mpa1_xopt.json" "$WORK/checkMesh.log"; do
    [ -f "$a" ] && ARTS="$ARTS $a"
  done
  python3 "$BASE/mpa1_age_guard.py" verify "$WORK" "$WORK/.mpa1_manifest.json" \
          "$DATUM_REF_FILE" $ARTS > "$AGE_OUT" 2>&1
  echo "MPA1_AGE_GUARD arm=$ARM rc=$? file=$(basename "$AGE_OUT") first_line=[$(head -1 "$AGE_OUT" 2>/dev/null)]"
else
  echo "MPA1_AGE_GUARD arm=$ARM rc=NOT_RUN reason=manifest_or_instrument_absent -- REPORTED as NOT_MEASURED, never as a pass" | tee "$AGE_OUT"
fi

CORE_MIN=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
MEMAVAIL_POST=$(python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))")
LEDGER="$BASE/ledger.txt"
{
  mpa1_ledger_row "$ARM" "$ROW" "$IMG" "$GOT_DIGEST" "$rc" "$WALL" "$RANKS" "$CORE_MIN" "$CAP" "$TMO" "$BACKCHECK" "$MEM" "$INSPECT" "$MEMAVAIL_GIB" "$MEMAVAIL_POST" "$CPUSET" "$DELIVERED" "$SIBLINGS_PRE" "$SIBLINGS_POST" "$(basename "$LOG")" "$STAMP"
  grep -a "D4S_CONTAINER_UID\|D4S_IDWARP_SO_MD5\|D4S_DEADLINE_IN_CONTAINER_S" "$LOG" | head -3   # the strings the container prints
} | tee -a "$LEDGER"
test -s "$LOG" && touch "$LOG.ok.${STAMP}"   # L-252 provenance sentinel
echo "STAMP=$STAMP RC=$rc CORE_MIN=$CORE_MIN"
exit $rc
