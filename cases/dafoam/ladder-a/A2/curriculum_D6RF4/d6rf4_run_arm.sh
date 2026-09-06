#!/usr/bin/env bash
# Curriculum D6RF4 arm launcher -- ONE ARM, P_conv: the CONVERGENCE PROBE.
#
# DERIVED from curriculum_D6RF3/d6rf3_run_arm.sh (md5
# 58684b91f6aced35f500fc947517a8e4) with the REGISTERED DELTAS of
# D6RF4 PREREGISTRATION.md sections 4, 5 and 8.2, enumerated in
# d6rf4_run_arm_DELTAS_from_d6rf3.diff beside this file:
#   A  ONE registered arm, P_conv, cap 54.00 core-min, deadline 720 s.  F_mp
#      and REF_off are NOT REGISTERED here and this launcher REFUSES them by
#      NAME rather than by falling through an unknown-arm default.
#   B  THE TIGHTENED fvSolution IS INSTALLED AT STAGING (S9), at all four
#      locations the tree carries, with the PRE-IMAGE md5 asserted at every one
#      before the write and the POST-IMAGE md5 asserted after it.  A site whose
#      pre-image is not D6RF3's own fvSolution ABORTS: this arm may only
#      tighten the file D6RF3 actually ran, never some other file.
#   C  THREE LEGS IN ONE CONTAINER (section 8.2).  L1 and L2 at the TIGHTENED
#      fvSolution, L3 at D6RF3's ORIGINAL one -- falsifier F5.  The swap
#      between L2 and L3 is done by the container script, and EVERY install
#      prints `D6RF4_FVSOLUTION_INSTALLED leg=<L> md5=<m> sites=<n>` into the
#      log, so the grader can assert that each leg ran the fvSolution it was
#      registered to run instead of taking the launcher's word for it.
#   D  `primalMinResTol` AND `primalMinResTolDiff` ARE NOT TOUCHED ANYWHERE IN
#      THIS FILE, and the launcher ASSERTS that on its own bytes before it
#      stages anything.  The accept floor stays 1e-08 x 1000 = 1.0e-05, and
#      d6rf4_accept_floor_control.py reads both values back out of the log this
#      launcher produces and REFUSES the grading if either has moved.
#   E  G-FREEZE.  THIS LAUNCHER REFUSES TO RUN WHILE `PERMISSION` HOLDS THE
#      PLACEHOLDER TOKEN, and refuses again if `PERMISSION` is neither the
#      placeholder nor a 40-hex sha.  The freeze and the enqueue belong to the
#      dafoam-supervisor.  "Do not launch" is an exit code here rather than a
#      sentence in a report.
#      THIS LINE DOES NOT STATE WHAT `PERMISSION` CURRENTLY HOLDS, DELIBERATELY.
#      A first screen that asserts "the permission is unset" becomes the item's
#      most-read false statement the moment the freeze fills it, and a reader
#      trusts the header long after the value has moved.  The MECHANISM is
#      described here; the VALUE is read from line ~79 and from the
#      `permission=` field of every `D6RF4_STAGE` line the launcher writes.
#      G-FREEZE IS DRIVEN IN BOTH DIRECTIONS BY `d6rf4_launcher_guard_drive.py`,
#      which plants each `PERMISSION` value into a NEUTERED COPY and checks the
#      REASON TOKEN rather than the rc -- so the control keeps firing after the
#      freeze, when reading the live value would prove nothing.
#
# ITS OWN PARENT, for the chain: curriculum_D6R/d6r_run_arm.sh (md5
# 243f0f631719edf7ae354410276b3cfd)
# with the registered deltas of D6RF PREREGISTRATION.md ADDENDUM 1.  Everything
# not named there is D6R's shape.  THE DELTAS, enumerated:
#   1  two arms, not four; caps 480.0 / 190.0 (section 4d), deadlines 7110/2760
#   2  F_mp gets ITS OWN ARM DIRECTORY, staged as a COPY of D6R's O_mp with the
#      optimiser's output time directories DROPPED (section 2a, S1-S8).  D6R ran
#      F_mp IN PLACE inside O_mp/ -- D6RF-DEF-2, which is D4's arm F2, rc=1 at
#      56 s on `renameSolution ... already exists`.
#   3  THE UNITS GATE, at both of its call sites (rule 14) -- D6RF-DEF-1
#   4  FORBIDDEN_ROOTS ENUMERATED FROM DISK at launch rather than carried as a
#      frozen list, with D6R's preserved root named explicitly at the head
#   5  exactly ONE executable `rm -rf`, targeting $BASE/REF_off and nothing else;
#      F_mp REFUSES on a pre-existing arm directory instead of removing it
#
# `set -e` DOES NOT GATE at the top level of a harness Bash call and
# `( set -e; ... )` does not gate either.  Every step below gates explicitly
# with `|| { echo ABORT...; exit N; }`.
#
# NO --rm, so `docker inspect .State.ExitCode/.State.OOMKilled` survives the arm
# and the KERNEL's verdict is read, not the harness's.
#
# REGISTERED EXIT CODES:
#   0   the arm's own rc, from docker inspect .State.ExitCode
#   3   G-ROOT refusal (wrong base, a forbidden root, a live arm, a live driver)
#   4   identity / staging failure (an md5, the image digest, a copy)
#   5   G-COLD or a section 2a staging assertion
#   7   UNITS REFUSAL, HOST SIDE -- distinct, and never a default
#   64  usage / unknown arm
#   65  cap arithmetic
#   8   G-DELIVERY REFUSAL -- an instrument this launcher WILL read at
#       $WORK was never staged there, or the delivery derivation could not
#       be performed.  DISTINCT from 4: `rc=4` on a bare `md5sum -c` says
#       an md5 failed and says nothing about DELIVERY.
#   77  UNITS REFUSAL, IN CONTAINER (arrives as the container's own ExitCode)
set -uo pipefail

ITEM=D6RF4
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6RF4-a2-wing-convergence-probe
BASE="${BASE:-$REGISTERED_BASE}"
# ============================ G-FREEZE ====================================
# `CLAUDE.md` rule 2 puts the freeze BEFORE any compute, and the freeze is the
# pre-registration's entire evidentiary content.  A launcher that would run
# without one turns "do not enqueue yet" into a sentence in a report; this
# turns it into an exit code.
#
# EXACTLY ONE FIELD IS FILLED AT THE FREEZE: `PERMISSION`, on the line below,
# which the dafoam-supervisor sets to the pre-registration's freeze sha.
#
# THE ASSIGNMENT IS ASSERTED UNIQUE.  `MD5_ANCHOR_GATE` was assigned twice in
# this file's first draft and the STALE value came second -- in shell the LAST
# assignment wins, so the stale one would have won and aborted staging at rc 4.
# A field a human edits by searching for its name is exactly where that
# recurs, so the count is PINNED here rather than the appearance trusted.
PERMISSION=NOT_FROZEN
PERM_ASSIGNMENTS=$(grep -cE '^PERMISSION=' "${BASH_SOURCE[0]}" || true)
case "$PERM_ASSIGNMENTS" in ''|*[!0-9]*) PERM_ASSIGNMENTS=UNMEASURED ;; esac
if [ "$PERM_ASSIGNMENTS" != "1" ]; then
  echo "ABORT G-FREEZE-UNIQUE PERMISSION is assigned $PERM_ASSIGNMENTS time(s)"
  echo "  in this launcher.  In shell the LAST assignment wins, so a second one"
  echo "  silently overrides the freeze field and the launcher would run under"
  echo "  a permission nobody read.  Pin the count, not the appearance."
  grep -nE '^PERMISSION=' "${BASH_SOURCE[0]}"
  exit 3
fi
# THE PLACEHOLDER LIMB.  Fires while the item is unfrozen.
if [ "$PERMISSION" = "NOT_FROZEN" ]; then
  echo "ABORT G-FREEZE this item is NOT FROZEN.  PERMISSION is still the"
  echo "  placeholder token NOT_FROZEN, so no pre-registration sha has been"
  echo "  written into this launcher."
  echo "  CLAUDE.md rule 2: the gate, threshold, cap and label are committed"
  echo "  BEFORE the solver starts, and the freeze is the document's entire"
  echo "  evidentiary content.  THE FREEZE AND THE ENQUEUE BELONG TO THE"
  echo "  dafoam-supervisor AND ARE NOT TAKEN BY A LANE."
  echo "  NO CONTAINER IS CREATED.  NO DIRECTORY IS TOUCHED."
  exit 3
fi
# THE SHAPE LIMB, AND IT IS THE LIMB THAT SURVIVES THE FREEZE.  Once the
# placeholder is replaced, the limb above can never fire again -- so a control
# that only had that limb would go silent at exactly the moment the field
# started mattering.  This one refuses anything that is not a 40-hex sha:
# a truncated paste, a short sha, a branch name, a date, an empty edit.
case "$PERMISSION" in
  *[!0-9a-f]*|"") BAD=yes ;;
  *) BAD=no ;;
esac
if [ "$BAD" = "yes" ] || [ "${#PERMISSION}" -ne 40 ]; then
  echo "ABORT G-FREEZE-SHAPE PERMISSION is '$PERMISSION' (${#PERMISSION} chars),"
  echo "  which is neither the placeholder NOT_FROZEN nor a 40-hex commit sha."
  echo "  A half-filled freeze field is not a freeze.  REFUSED before any"
  echo "  staging; NO CONTAINER IS CREATED."
  exit 3
fi
echo "D6RF4_G_FREEZE_PASS permission=$PERMISSION assignments=$PERM_ASSIGNMENTS shape=40hex"
# THE ESCAPE HATCH IS GONE.  An earlier draft honoured an environment variable
# that bypassed the limb above, so any caller who set it could launch an
# unfrozen item -- and this lane's own guard drive USED it, which is precisely
# how such a hatch stays in a file.  G-FREEZE is now driven by planting values
# into a NEUTERED COPY (d6rf4_launcher_guard_drive.py), so nothing needs to
# bypass the live gate and the gate has no bypass to offer.

BASE_REAL=$(realpath -m "$BASE")
REG_REAL=$(realpath -m "$REGISTERED_BASE")
D6R_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint
D4_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin
RUNS_DIR=/home/ubuntu/certonomous-runs

# ---- G-ROOT.2a -- THE NAMED HEAD, AND IT IS TESTED FIRST ON PURPOSE.
# D6R's preserved root is THIS item's READ-ONLY SOURCE, so it is the one wrong
# base a reader is most likely to supply, and the abort must SAY WHOSE evidence
# it just protected rather than emit the generic refusal.  Ordering matters:
# G-ROOT.1 below would catch this base too, with a message that names nothing.
# A guard that fires with the wrong message is a guard nobody learns from.
if [ "$BASE_REAL" = "$(realpath -m "$D6R_ROOT")" ]; then
  echo "ABORT G-ROOT.2a BASE resolves to D6R'S PRESERVED RUN ROOT: $D6R_ROOT"
  echo "  That directory holds arm O_mp's 2,257.933 core-min of GRADED evidence"
  echo "  (ledger.txt ARM=O_mp rc=0) and is THIS ITEM'S READ-ONLY SOURCE for"
  echo "  F_mp's OptView.hst.  This launcher stages by copying OUT of it and, for"
  echo "  REF_off, by removing an arm directory.  Writing there would destroy the"
  echo "  evidence this item depends on.  REFUSED."
  exit 3
fi

# ---- G-ROOT.1 -- BASE must be THIS item's registered root, normalised, so a
# ---- trailing slash, a `.`, a `..` or a symlink cannot walk around the check.
if [ "$BASE_REAL" != "$REG_REAL" ]; then
  echo "ABORT G-ROOT.1 BASE is not this item's registered run root."
  echo "  given:      $BASE_REAL"
  echo "  registered: $REG_REAL"
  echo "  D4-LAUNCHER-DEF-1: a launcher pointed at another item's run root"
  echo "  deletes that item's graded arms.  REFUSED before any staging."
  # AND NAME IT, if the given base is a run root this box actually holds.
  if [ -d "$RUNS_DIR" ] && [ -d "$BASE_REAL" ]; then
    case "$BASE_REAL" in
      "$RUNS_DIR"/*) echo "  THE ROOT JUST PROTECTED: $BASE_REAL -- it holds another item's rows." ;;
    esac
  fi
  exit 3
fi

# ---- G-ROOT.2 -- the belt to G-ROOT.1's braces.  THE LIST IS ENUMERATED FROM
# DISK AT EVERY LAUNCH, never carried forward: D6's own frozen list named roots
# that DO NOT EXIST and omitted eleven that do, and an inert entry in a list
# whose whole job is to NAME whose evidence was protected is exactly the class
# of defect this lab records.  Reading the directory cannot go stale.
if [ -d "$RUNS_DIR" ]; then
  while IFS= read -r forb; do
    [ -z "$forb" ] && continue
    [ "$forb" = "$REG_REAL" ] && continue
    if [ "$BASE_REAL" = "$forb" ]; then
      echo "ABORT G-ROOT.2 BASE resolves to ANOTHER ITEM'S RUN ROOT: $forb"
      echo "  That directory holds a graded row.  This launcher stages by"
      echo "  removing the arm directory, so writing there would destroy it.  REFUSED."
      exit 3
    fi
  done <<< "$(find "$RUNS_DIR" -maxdepth 1 -mindepth 1 -type d -exec realpath -m {} \; 2>/dev/null)"
fi

# ---- G-ROOT.3 -- the LEDGER must belong to this item and to no other.
if [ -f "$BASE/ledger.txt" ]; then
  FOREIGN_ITEM=$(grep -a "^ITEM=" "$BASE/ledger.txt" 2>/dev/null | grep -av "^ITEM=$ITEM$" | head -1)
  if [ -n "$FOREIGN_ITEM" ]; then
    echo "ABORT G-ROOT.3 the ledger at $BASE/ledger.txt carries another item: $FOREIGN_ITEM"
    echo "  Appending here would interleave two items' rows in one file.  REFUSED."
    exit 3
  fi
  if grep -aq "ROW=SHIPPED" "$BASE/ledger.txt" 2>/dev/null; then
    echo "ABORT G-ROOT.3 the ledger at $BASE/ledger.txt already carries SHIPPED rows."
    echo "  This launcher writes the PATCHED row only (D6R's registered delta,"
    echo "  the row D4 was GRADED on, C-97).  REFUSED."
    exit 3
  fi
fi
echo "D6RF4_G_ROOT_PASS item=$ITEM base=$BASE_REAL ledger_clean=yes"

RANKS=4
# ---- REGISTERED CPU PLACEMENT (PREREGISTRATION.md section 4g) -------------
# `mpirun` inside a `--cpus=N` container binds rank 0 to the FIRST CORE OF THE
# HOST TOPOLOGY; concurrent containers land on the same core (MEASURED by the
# D13 lane 2026-08-25).  So: PIN, and MEASURE the placement.  2,3,4,14 is D6R's
# set, measured DISJOINT at freeze from the only live container on this box
# (cpuset 1).  Core 0 is the default landing core the defect names; not used.
CPUSET=2,3,4,14

container_census() {
  sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -v "^d6rf4_" | tr '\n' ',' | sed 's/,$//'
}

# ---- D6RF4 REGISTERED CAP TABLE (PREREGISTRATION.md section 8.2) ---------
#   P_conv  17.90 core-min estimate =
#       L1  cl04 baseline primal, TIGHTENED fvSolution   1.3140 x 6 = 7.884
#       L2  cl04 baseline_repeat, TIGHTENED              1.3140 x 6 = 7.884
#       L3  cl04 baseline primal, ORIGINAL fvSolution    1.3140 x 1 = 1.314
#           container frame, ONE container for all three  2.067-1.314 = 0.800
#   The 1.3140 core-min basis is MEASURED: D6RF3's own ExecutionTime 19.71 s at
#   ranks 4.  The x6 multiplier is DERIVED from section 1.3's measured
#   per-sweep reduction factors and is registered as an UPPER BOUND; L1 and L3
#   are the same primal at the two settings in the same container, so their
#   measured ExecutionTime ratio IS the multiplier and section 8.3 owes that
#   comparison at completion.
#   CAP by max(3.0 x estimate, 1.25 x (4/3) x estimate) -- the MAX of two
#   risks, NEVER their product:  max(53.70, 29.83) -> 54.00
#   arm       estimate    cap      deadline(s)   compute window (core-min)
#   P_conv      17.90     54.00       720             54.00
#   THE REACHABILITY IDENTITY IS EXACT: 54.00 x 60 / 4 = 810.0 s and
#   720 + 90 = 810.0 s, residual +0.0e+00 -- neither stopping condition is
#   decorative.
#
# ---- THE PARENT'S CAP TABLE, KEPT FOR THE LINEAGE ------------------------
# BOTH ARMS ANCHORED ON MEASUREMENTS OF THE PROGRAMS THEY ACTUALLY RUN.
#   F_mp    155.70 core-min  =  D4 arm F3 (47.267 MEASURED, f3_ledger.txt, the
#                               only FD-endpoint arm that has ever succeeded
#                               here) x the MEASURED multipoint factor 3.2949
#                               (= D6RACC2 ACC_mp 119.933 / D4 P2 36.4)
#   REF_off  60.07 core-min  =  the multipoint findFeasibleDesign trim MEASURED
#                               at 833 s in D6R's own O_mp log (line 2115 ->
#                               ClockTime = 833 s at line 10842) x 4/60 = 55.53,
#                               plus one closing multipoint primal 4.54
# CAPS by max(3.0 x estimate, 1.25 x (4/3) x estimate) -- the MAX of two risks,
# NEVER their product:  F_mp max(467.1, 259.5) -> 480.0
#                       REF_off max(180.2, 100.1) -> 190.0
#   arm      estimate    cap      deadline(s)   compute window (core-min)
#   F_mp      155.70    480.0        7110            480.0
#   REF_off    60.07    190.0        2760            190.0
# D6R registered REF_off at a 40.0 cap and a 510 s deadline against a program
# MEASURED at 55.53 core-min / 833 s -- D6RF-DEF-3.  It could not have finished.
cap_core_min() {
  case "$1" in
    P_conv)  echo 54.00 ;;
    *)  echo "" ;;
  esac
}
# MEMORY: 20g, NEVER 8g.  The D4-SHIPPED ACC arm was OOM-killed by its 8g cgroup
# (rc=137, 16:56:28Z 2026-08-26), and D6RACC2 measured OOMKilled=false for the
# identical multipoint program at 20g, so 20g is a MEASURED floor, not a guess.
cap_memory() {
  case "$1" in
    P_conv) echo 20g ;;
    *) echo "" ;;
  esac
}

# ---- REGISTERED TOOLCHAIN, BY DIGEST, never by tag (DAFOAM_CHARTER 6) -----
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
IMG_SHIPPED_DIGEST=sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc

# ---- FROZEN INSTRUMENT HASHES (PREREGISTRATION.md sections 7a and 7b) -----
MD5_RUNSCRIPT6=137539e0a99be27f27fdb69e063b2a87
MD5_FD=06ac0a171bde0ac3b17192f1819fa0ca
MD5_EXTRACT6=c5aace65e1830fddace55e1bac2761c9
MD5_LOCUS6=341189ca866f302a7e1bba8eefad3a57
MD5_PHYS6=ca75db3e036b9f4e7cfca6462037c021
MD5_UNITS=8ee53841aed3dfd10f2cf414be39518a
MD5_ANCHOR_GATE=f5a5216a557ff8c34ac084c96feabc39
# THE TWO fvSolution FILES, AND THE WHOLE ITEM TURNS ON THEM.
# ORIGINAL is BYTE-IDENTICAL to the file D6RF3's F_mp arm actually ran
# (verified against the run tree when it was staged into the item directory).
# TIGHT is derived from it by SEVEN semantic edits, every one in the
# strictly-harder direction, each justified in the file's own comments by a
# ratio measured at Time = 1000.
MD5_FVSOL_TIGHT=0ac5bd00c63b9109d22a8e73b0795aa4
MD5_FVSOL_ORIG=9e2669956be778acf7e7d8aa67a90ff6
# The FOUR locations the staged tree carries this file at.  ENUMERATED, and
# S9 asserts it found exactly this many -- a loop that can iterate zero times
# asserts its own trip count.
FVSOL_SITES="system mp04/system mp05/system mp06/system"
# ---- THE FIVE CONSTANTS BELOW ARE ASSIGNED AND NEVER USED, and that is
# ---- SAID rather than left for a reader to discover.
# They pinned instruments the deleted REF_off branch staged: d4_extract_endpoint,
# d4_opt_runScript, d4_endpoint_locus, d4_endpoint_physical and D4's OptView.hst.
# They are KEPT, not deleted, because `d4_opt_runScript.py` is still read by the
# GRADER as G-DVL's D4-side reference (d6rf4_grade.py CROSS_ITEM), so its md5
# stays useful to a reader comparing the two files, and because a successor that
# restores a REF_off arm needs the pins rather than a fresh guess.
# THE SWEEP THAT FOUND THEM ALSO ASKED THE OTHER QUESTION -- variables USED but
# never ASSIGNED, which expand to the empty string and make an md5 check pass
# vacuously -- and found NONE.  That is the direction that could have hurt.
MD5_EXTRACT4=ee7d3c99fd716da23779cb651961918e
MD5_RUNSCRIPT4=2906d52a5dbed2bacbaeaf85a37d3fe8
MD5_LOCUS4=e63df1845771c3e67457443918f5b82e
MD5_PHYS4=74c35c80bb4d395cf8939d851bc6b3f9
# D4's PATCHED optimiser history, staged READ-ONLY into REF_off/ as OptView.hst
MD5_D4_HST=0d956d6ccbc010402915710f662d3b11
D4_HST_SRC="$D4_ROOT/O/OptView.hst"
# THE UNDEFORMED REFERENCE MESH.  Section 2a S3: the double-deformation confound
# that killed D4's arm F is eliminated BY MEASUREMENT, not by assumption.
# `MD5_ANCHOR_GATE` WAS ASSIGNED HERE TOO, and this second assignment carried
# D6RF3's value `e823689c...` while the block above carries D6RF4's.  IN SHELL
# THE LAST ASSIGNMENT WINS, so the STALE one would have won and S6's staged-
# instrument md5 check would have aborted the arm at rc 4 -- a launch spent to
# discover a duplicated variable.  Caught before the freeze by the md5 refresh
# REFUSING on a variable that appears twice as an assignment, which is why that
# refresh asserts a hit count of exactly one rather than substituting blind.
MD5_REF_MESH=0fb1935a9b8781b73ac4ccb136e3ec68

ARM="${1:-}"; IMG="${2:-}"
test -n "$ARM" || { echo "ABORT usage: d6rf4_run_arm.sh <P_conv> <image>"; exit 64; }
test -n "$IMG" || { echo "ABORT usage: d6rf4_run_arm.sh <P_conv> <image>"; exit 64; }
# THE ARM GUARD IS AN EQUALITY, NOT A PREFIX MATCH.  AND THE TWO ARMS THIS
# ITEM DOES NOT REGISTER ARE REFUSED BY NAME, with the reason, rather than
# falling through the generic unknown-arm branch: a reader who types `F_mp`
# here is asking for D6RF3's arm and deserves to be told which item owns it.
case "$ARM" in
  P_conv) : ;;
  F_mp|REF_off)
     echo "ABORT arm '$ARM' belongs to D6RF3, not to this item."
     echo "  D6RF4 registers ONE arm, P_conv (PREREGISTRATION.md section 8.2):"
     echo "  the full F_mp FD arm prices at 934 core-min at the tightened"
     echo "  settings and it is not defensible to buy a 934 core-min arm to"
     echo "  learn a 17.9 core-min fact.  Buying it is a SUCCESSOR's item,"
     echo "  priced FROM P_conv's measurement.  REFUSED."
     exit 64 ;;
  *) echo "ABORT arm '$ARM' is not this item's ONE REGISTERED arm (P_conv)."
     echo "  A second arm is a separate item with its own registration.  REFUSED."
     exit 64 ;;
esac

# ---- G-ACCEPT-FLOOR.  THE ACCEPT FLOOR IS NOT TOUCHED BY THIS LAUNCHER,
# ---- ASSERTED ON ITS OWN BYTES BEFORE ANYTHING IS STAGED
# ---- (PREREGISTRATION.md section 7 instrument 4).
#
# This is the HOST-SIDE half of ACCEPT_FLOOR_UNMOVED.  The grader reads the two
# values back out of the container log; this asserts the LAUNCHER never wrote
# them in the first place, so a drift cannot enter through the staging path.
# It greps ITS OWN BYTES, so it cannot go stale against an edit of this file.
#
# AND IT CARRIES A PLANTED CONTROL, because a check that reports "no
# assignments found" from a pattern that can never match anything is a planted
# zero (CLAUDE.md rule 3).  The line below IS a real assignment in the
# OpenFOAM/daOptions form, deliberately left in this file and marked with the
# sentinel; the check must SEE it (raw count >= 1) and must EXCLUDE it
# (filtered count == 0).  Both numbers are printed.
#   PLANTED CONTROL, DO NOT REMOVE:  primalMinResTolDiff 1e12;   ACCEPT_FLOOR_PLANT
ACCEPT_FLOOR_PLANT_TAG=ACCEPT_FLOOR_PLANT
AF_PAT='primalMinResTol(Diff)?[[:space:]]+[0-9][0-9.eE+-]*[[:space:]]*;'
AF_RAW=$(grep -cE "$AF_PAT" "${BASH_SOURCE[0]}" || true)
AF_REAL=$(grep -E "$AF_PAT" "${BASH_SOURCE[0]}" | grep -vc "$ACCEPT_FLOOR_PLANT_TAG" || true)
case "$AF_RAW" in ''|*[!0-9]*) AF_RAW=UNMEASURED ;; esac
case "$AF_REAL" in ''|*[!0-9]*) AF_REAL=UNMEASURED ;; esac
if [ "$AF_RAW" = "UNMEASURED" ] || [ "$AF_REAL" = "UNMEASURED" ]; then
  echo "ABORT G-ACCEPT-FLOOR the self-scan is UNMEASURED (raw=$AF_RAW real=$AF_REAL)."
  echo "  An unmeasured scan is not a clean scan.  REFUSED."
  exit 3
fi
if [ "$AF_RAW" -lt 1 ]; then
  echo "ABORT G-ACCEPT-FLOOR the planted control was NOT SEEN (raw=$AF_RAW)."
  echo "  The pattern cannot match a real assignment, so a zero from it is not"
  echo "  evidence that this launcher sets nothing (CLAUDE.md rule 3).  REFUSED."
  exit 3
fi
if [ "$AF_REAL" -ne 0 ]; then
  echo "ABORT G-ACCEPT-FLOOR this launcher SETS primalMinResTol or"
  echo "  primalMinResTolDiff at $AF_REAL site(s) that are not the planted"
  echo "  control.  D6RF4 tightens the linear-solver stopping rule at an"
  echo "  UNCHANGED acceptance bar; moving the bar is widening a gate to fit"
  echo "  and is ESCALATED TO SANAA AND UNRULED.  REFUSED before any staging."
  grep -nE "$AF_PAT" "${BASH_SOURCE[0]}" | grep -v "$ACCEPT_FLOOR_PLANT_TAG"
  exit 3
fi
echo "D6RF4_G_ACCEPT_FLOOR_PASS planted_control_seen=$AF_RAW real_assignments=$AF_REAL -- the launcher sets neither primalMinResTol nor primalMinResTolDiff; the accept floor stays 1e-08 x 1000 = 1.0e-05"

# ---- G-ROOT.5 -- A LIVE ARM IS NEVER RE-STAGED.  Two live readings, BEFORE
# ---- any destructive act.
LIVE_SAME_ARM=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^d6rf4_${ARM}_" 2>/dev/null | grep "^d6rf4_${ARM}_" | head -3 | tr '\n' ',' | sed 's/,$//')
if [ -n "$LIVE_SAME_ARM" ]; then
  echo "ABORT G-ROOT.5 a RUNNING container already carries this item's prefix and arm: [$LIVE_SAME_ARM]"
  echo "  Re-staging would remove the live arm directory under it.  REFUSED."
  exit 3
fi
PIDFILE="$BASE/d6rf4_driver.pid"
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
    if [ "$ANCESTOR" = "no" ] || [ "$DCWD" = "$BASE_REAL" ]; then
      echo "ABORT G-ROOT.5 driver pidfile $PIDFILE names LIVE pid $DPID (ancestor_of_this_launcher=$ANCESTOR cwd=$DCWD)."
      echo "  Another driver owns this run root, or a process sits inside it.  REFUSED."
      exit 3
    fi
  fi
fi
echo "D6RF4_G_ROOT5_PASS arm=$ARM live_same_arm_containers=none driver_pidfile=$([ -f "$PIDFILE" ] && echo present_owner_is_ancestor_or_stale || echo absent)"

CAP=$(cap_core_min "$ARM")
MEM=$(cap_memory "$ARM")
test -n "$CAP" || { echo "ABORT unknown arm $ARM -- no registered cap"; exit 64; }
test -n "$MEM" || { echo "ABORT unknown arm $ARM -- no registered memory cap"; exit 64; }

# ===========================================================================
# THE CAP FRAME.  D6-CAP-FRAME-1 (L-371) is repaired the D4S-F3SR way and the
# cap DOES NOT MOVE -- the enforced deadline moves DOWN by a bounded allowance.
# THE D19T IDENTITY IS EXECUTED HERE, EVERY LAUNCH, AND `TMO > 0` IS ASSERTED:
# D19T was frozen, md5-pinned, gate-checked and launched TWICE and no check ever
# executed its own cap arithmetic -- `int(CAP*60/RANKS) - 60` gave its MESH arm
# TMO = 0 s and no D19T arm could ever run.
# THIS LINEAGE'S REGISTERED RESERVE IS 90, NOT 60.  All three lineage constants
# are recorded in PREREGISTRATION.md section 4e so a successor does not read the
# difference as drift:  D6R/D6RF 90 (d6r_run_arm.sh:251);  A1/D19 60
# (d19o_run_arm.sh:153);  SO3 180 (so3_run_arm.sh:208).  90 is the stricter of
# the two this lineage could take, and it is the one registered.
FRAME_ALLOWANCE_S=90
KILL_GRACE_S=60
# THE ASSERTION INVERTS AND RE-ADDS THE ALLOWANCE, so no edit to it can silently
# widen the cap: (TMO + FRAME_ALLOWANCE_S) * RANKS / 60 == CAP.
TMO=$(python3 -c "print(int(round($CAP*60.0/$RANKS)) - $FRAME_ALLOWANCE_S)") || { echo "ABORT tmo calc"; exit 65; }
test "$TMO" -gt 0 || { echo "ABORT D19T IDENTITY: frame allowance ${FRAME_ALLOWANCE_S}s consumes the whole ${CAP} core-min cap at $RANKS ranks; TMO=$TMO"; exit 65; }
BACKCHECK=$(python3 -c "print('%.6f' % (($TMO+$FRAME_ALLOWANCE_S)*$RANKS/60.0))") || { echo "ABORT backcheck"; exit 65; }
python3 -c "
import sys
cap, back = $CAP, $BACKCHECK
if abs(cap-back) > 0.02:
    sys.stderr.write('ABORT CAP MISMATCH registered=%r enforced_plus_allowance=%r\n' % (cap, back)); sys.exit(1)
" || { echo "ABORT enforced cap + frame allowance != registered cap"; exit 65; }
echo "D6RF4_CAP_FRAME arm=$ARM registered_core_min=$CAP ranks=$RANKS deadline_in_container_s=$TMO frame_allowance_s=$FRAME_ALLOWANCE_S kill_grace_s=$KILL_GRACE_S worst_case_host_core_min=$BACKCHECK enforced_in_frame=container graded_in_frame=host_bracket_T0_T1"
echo "D4_CAP_ASSERT arm=$ARM registered_core_min=$CAP ranks=$RANKS enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM"

# ---- host state, read before ranks are claimed ---------------------------
MEMAVAIL_KB=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
MEMAVAIL_GIB=$(python3 -c "print('%.2f' % ($MEMAVAIL_KB/1048576.0))")
LOAD=$(awk '{print $1}' /proc/loadavg)
SIBLINGS_PRE=$(container_census)
echo "D6RF4_HOST_PRE arm=$ARM MemAvailable_GiB=$MEMAVAIL_GIB load1=$LOAD cpuset=$CPUSET siblings_pre=[$SIBLINGS_PRE]"

test "$(stat -c '%a' "$BASE")" = "777" || { echo "ABORT L-251 run root mode $(stat -c '%a' "$BASE")"; exit 4; }

# ---- staged-instrument identity, re-asserted before EVERY launch ---------
echo "$MD5_RUNSCRIPT6  $BASE/d6rf4_opt_runScript.py" | md5sum -c - || { echo "ABORT d6rf4_opt_runScript.py md5"; exit 4; }
echo "$MD5_FD  $BASE/d6rf4_fd_endpoint.py"           | md5sum -c - || { echo "ABORT d6rf4_fd_endpoint.py md5"; exit 4; }
echo "$MD5_EXTRACT6  $BASE/d6rf4_extract_endpoint.py"| md5sum -c - || { echo "ABORT d6rf4_extract_endpoint.py md5"; exit 4; }
echo "$MD5_LOCUS6  $BASE/d6rf4_endpoint_locus.py"   | md5sum -c - || { echo "ABORT d6rf4_endpoint_locus.py md5"; exit 4; }
echo "$MD5_PHYS6  $BASE/d6rf4_endpoint_physical.py" | md5sum -c - || { echo "ABORT d6rf4_endpoint_physical.py md5"; exit 4; }
echo "$MD5_UNITS  $BASE/d6rf4_units_assert.py"      | md5sum -c - || { echo "ABORT d6rf4_units_assert.py md5"; exit 4; }
echo "$MD5_ANCHOR_GATE  $BASE/d6rf4_anchor_gate.py" | md5sum -c - || { echo "ABORT d6rf4_anchor_gate.py md5"; exit 4; }
# THE TWO fvSolution FILES, ASSERTED AT $BASE BEFORE EITHER IS INSTALLED.
echo "$MD5_FVSOL_TIGHT  $BASE/d6rf4_fvSolution_TIGHT" | md5sum -c - || { echo "ABORT d6rf4_fvSolution_TIGHT md5 -- THE TIGHTENED STOPPING RULE IS THE WHOLE ITEM"; exit 4; }
echo "$MD5_FVSOL_ORIG  $BASE/d6rf4_fvSolution_D6RF3_ORIGINAL" | md5sum -c - || { echo "ABORT d6rf4_fvSolution_D6RF3_ORIGINAL md5 -- falsifier F5 must run the file D6RF3 ACTUALLY RAN"; exit 4; }
test "$MD5_FVSOL_TIGHT" != "$MD5_FVSOL_ORIG" || { echo "ABORT the tightened and original fvSolution are THE SAME FILE; F5 would not be a wrong setting and this item would test nothing"; exit 4; }

# ---- image identity by DIGEST, resolved from the local store -------------
GOT_DIGEST=$(sudo -n docker image inspect --format '{{index .RepoDigests 0}}' "$IMG" 2>/dev/null | sed 's/.*@//')
test -n "$GOT_DIGEST" || { echo "ABORT cannot read digest of $IMG"; exit 4; }
case "$IMG" in
  dafoam-idwarp-rot:v1)       WANT=$IMG_PATCHED_DIGEST; ROW=PATCHED ;;
  dafoam/opt-packages:latest) WANT=$IMG_SHIPPED_DIGEST; ROW=SHIPPED ;;
  *) echo "ABORT image $IMG is not a registered row"; exit 4 ;;
esac
test "$GOT_DIGEST" = "$WANT" || { echo "ABORT digest mismatch $IMG got=$GOT_DIGEST want=$WANT"; exit 4; }
test "$ROW" = "PATCHED" || {
  echo "ABORT G-ROW D6RF is registered PATCHED-ONLY (the row D4 was GRADED on, C-97); got ROW=$ROW ($IMG)."
  echo "  The SHIPPED row is NOT bought here; a second row is a separate item."
  exit 4; }
echo "D6RF4_G_ROW_PASS row=$ROW digest=$GOT_DIGEST"

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d6rf4_${ARM}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"
STAGE_EVID="$BASE/${ARM}_STAGING_EVIDENCE.txt"

# ===========================================================================
# STAGING.  PREREGISTRATION.md section 2a, frozen BEFORE this file was written.
# Every step aborts the arm rather than degrading, and prints its own evidence
# line into $STAGE_EVID.
# ===========================================================================
stage_say() { echo "$*"; echo "$*" >> "$STAGE_EVID"; }
: > "$STAGE_EVID"
stage_say "D6RF4_STAGE arm=$ARM utc=$(date -u +%Y%m%dT%H%M%SZ) base=$BASE_REAL permission=$PERMISSION"

# ===========================================================================
# FIELD PRESENCE -- `U` OR `U.gz`, AND AN ABORT THAT SAYS WHAT IT ACTUALLY FOUND.
# REPAIR REGISTERED IN ADDENDUM 3, on the dafoam-supervisor's crash triage of
# F_mp's rc=5 abort.
#
# THE DEFECT.  OpenFOAM's `writeCompression on` makes `decomposePar` write the
# DECOMPOSED fields gzipped while the RECONSTRUCTED ones stay plain.  MEASURED on
# D6R's own source: `O_mp/mp04/0/` holds `T U alphat nuTilda nut p`, and
# `O_mp/mp04/processor0/0/` holds `T.gz U.gz alphat.gz nuTilda.gz nut.gz p.gz`.
# The S5 assertion tested `processor0/0/U` -- the uncompressed name -- and
# aborted `rc=5` saying the file "was dropped".  NOTHING WAS DROPPED: the
# directory and all six fields were intact; the sweep had done exactly the right
# thing and the assertion meant to CONFIRM it stated a falsehood about the
# filesystem in its own abort message, sending its reader hunting a destructive
# bug that does not exist.
#
# IT IS THE MIRROR OF THE S4 DEFECT ADDENDUM 2 REPAIRED.  S4 could pass
# VACUOUSLY on a pair of false zeros; this one FAILS SPURIOUSLY and asserts a
# deletion that did not happen.  Same root in both: the guard's evidence line did
# not correspond to what was on disk.
#
# WHY NO DRIVE CAUGHT IT: the self-tests built FIXTURES, and a fixture creates the
# file under the name the test expects.  ADDENDUM 3's legs are therefore pointed
# at D6R's REAL directories on disk for the positive case (section A3.3).
# ===========================================================================
field_path() {   # $1 = directory, $2 = field name (with or without .gz)
  local d="$1" n="${2%.gz}"
  [ -d "$d" ] || return 1
  if   [ -f "$d/$n" ];     then echo "$d/$n";     return 0
  elif [ -f "$d/$n.gz" ];  then echo "$d/$n.gz";  return 0
  fi
  return 1
}
field_present() { field_path "$1" "$2" >/dev/null 2>&1; }
assert_field() { # $1 label, $2 directory, $3 field, $4 why-it-matters
  local p
  p=$(field_path "$2" "$3") && { stage_say "$1 OK $3 present as $(basename "$p") in $2"; return 0; }
  # THE ABORT DISTINGUISHES THE TWO CASES AND PRINTS WHAT IT ACTUALLY FOUND.
  if [ ! -d "$2" ]; then
    stage_say "ABORT $1 THE DIRECTORY IS ABSENT: $2"
    stage_say "  This is a missing directory, NOT a missing field.  $4"
  else
    stage_say "ABORT $1 the directory $2 EXISTS but holds NEITHER '${3%.gz}' NOR '${3%.gz}.gz'."
    stage_say "  WHAT IS ACTUALLY THERE (up to 20 entries): [$(ls -A "$2" 2>/dev/null | head -20 | tr '\n' ' ')]"
    stage_say "  $4"
  fi
  exit 5
}

if [ "$ARM" = "P_conv" ]; then
  # ------------------------------------------------------------------ S1
  SRC="$D6R_ROOT/O_mp"
  test -d "$SRC" || { stage_say "ABORT S1 source absent: $SRC"; exit 5; }
  test -f "$SRC/OptView.hst" || { stage_say "ABORT S1 no OptView.hst under $SRC -- there is no endpoint to read"; exit 5; }
  # THE DESTINATION MUST BE ABSENT.  P_conv has NO `rm -rf`: a re-fire finds a
  # stale arm directory and REFUSES rather than removing 1.1 GB that may hold a
  # partial result.  Recovery is an explicit archive (`mv`), never an implicit
  # delete -- the S-29 pattern.
  if [ -e "$WORK" ]; then
    stage_say "ABORT S1 $WORK already exists.  P_conv does not remove an arm directory."
    stage_say "  A re-fire needs the partial root ARCHIVED by mv, not deleted here."
    exit 5
  fi
  stage_say "D6RF4_STAGE_P_conv (S1) OK src=$SRC exists, OptView.hst present, dst=$WORK does not exist"
  # ------------------------------------------------------------------ S3
  # THE DOUBLE-DEFORMATION CONFOUND, ELIMINATED BY MEASUREMENT.  D4's arm F died
  # on `Mesh quality error!`; its F3 repair recorded the same md5 on both sides.
  # S3 named `points.gz` explicitly -- the SAME assumption as S5's, in the other
  # direction.  It happens to hold on this case family (constant/polyMesh IS
  # gzipped), but a tree written without compression would abort here saying the
  # reference mesh is absent when it is present under the plain name.  Swept in
  # ADDENDUM 3 so the repair has no unrepaired call site (rule 14).
  BASE_MESH=$(field_path "$BASE/base/constant/polyMesh" points) || \
    assert_field "S3 base reference mesh" "$BASE/base/constant/polyMesh" points \
      "The undeformed reference mesh is this arm's md5 anchor; without it the double-deformation confound cannot be eliminated by measurement."
  BASE_MESH_MD5=$(md5sum "$BASE_MESH" | cut -d' ' -f1)
  test "$BASE_MESH_MD5" = "$MD5_REF_MESH" || { stage_say "ABORT S3 base reference mesh md5 $BASE_MESH_MD5 != registered $MD5_REF_MESH"; exit 5; }
  for mp in mp04 mp05 mp06; do
    MP_MESH=$(field_path "$SRC/$mp/constant/polyMesh" points) || \
      assert_field "S3 $mp reference mesh" "$SRC/$mp/constant/polyMesh" points \
        "The undeformed reference mesh must be md5-equal to base's or the FD perturbation warps from an already-deformed mesh."
    M=$(md5sum "$MP_MESH" | cut -d' ' -f1)
    test "$M" = "$MD5_REF_MESH" || {
      stage_say "ABORT S3 $mp reference mesh md5 $M != registered $MD5_REF_MESH"
      stage_say "  The source's UNDEFORMED reference mesh has MOVED, so an FD"
      stage_say "  perturbation would warp from an already-deformed mesh -- the"
      stage_say "  double-deformation confound that killed D4's arm F.  REFUSED."
      exit 5; }
  done
  stage_say "D6RF4_STAGE_P_conv (S3) OK undeformed reference mesh md5 $MD5_REF_MESH on base and on mp04 mp05 mp06 -- double-deformation confound eliminated by MEASUREMENT"
  # ------------------------------------------------------------------ S4
  # ===================================================================
  # EVERY COUNT BELOW ASSERTS ITS OWN TRIP COUNT.  A guard that compares
  # two reads of the same path passes VACUOUSLY when both reads fail: an
  # unreadable or mistyped path gives `0` twice, `0 = 0` holds, and the
  # step announces SOURCE INTACT having counted nothing.  That is the
  # planted-zero failure in a bash guard (CLAUDE.md rule 3's principle;
  # the same discipline `control_bounds` already applies in
  # d6rf4_endpoint_locus.py -- "a loop that can iterate zero times asserts
  # its own trip count").  So: a failed read reports UNMEASURED, never 0,
  # and a zero count REFUSES.
  # REPAIR REGISTERED IN ADDENDUM 2, on the dafoam-supervisor's check-1
  # diff read of this file.
  # ===================================================================
  count_src_entries() {   # $1 = directory, $2 = glob suffix ('' = every entry)
    if [ ! -d "$1" ] || [ ! -r "$1" ]; then echo UNMEASURED; return 0; fi
    local n
    if [ -z "${2:-}" ]; then
      n=$(ls -A -- "$1" 2>/dev/null | wc -l) || { echo UNMEASURED; return 0; }
    else
      n=$(ls -d -- "$1"/$2 2>/dev/null | wc -l) || { echo UNMEASURED; return 0; }
    fi
    case "$n" in ''|*[!0-9]*) echo UNMEASURED ;; *) echo "$n" ;; esac
  }
  SRC_HST_MD5=$(md5sum "$SRC/OptView.hst" | cut -d' ' -f1)
  SRC_TIMEDIRS=$(count_src_entries "$SRC/mp04/processor0" "")
  stage_say "D6RF4_STAGE_P_conv (S4) source pre-copy: OptView.hst md5=$SRC_HST_MD5, entries under mp04/processor0 = $SRC_TIMEDIRS"
  case "$SRC_TIMEDIRS" in
    UNMEASURED)
      stage_say "ABORT S4 the source count is UNMEASURED -- $SRC/mp04/processor0 is absent or unreadable."
      stage_say "  A comparison of two UNMEASURED reads would pass vacuously and announce"
      stage_say "  SOURCE INTACT having counted nothing.  This guard asserts its own trip count."
      exit 5 ;;
    0)
      stage_say "ABORT S4 the source count is ZERO under $SRC/mp04/processor0."
      stage_say "  A guard whose before and after both read 0 cannot detect a change."
      exit 5 ;;
  esac
  cp -a "$SRC" "$WORK" || { stage_say "ABORT S4 stage copy of $SRC failed"; exit 4; }
  COPY_EPOCH=$(date -u +%s); echo "$COPY_EPOCH" > "$WORK/.d6rf4_copy_epoch"
  POST_HST_MD5=$(md5sum "$SRC/OptView.hst" | cut -d' ' -f1)
  POST_TIMEDIRS=$(count_src_entries "$SRC/mp04/processor0" "")
  test "$POST_HST_MD5" = "$SRC_HST_MD5" || { stage_say "ABORT S4 SOURCE CHANGED during the copy: OptView.hst md5 $SRC_HST_MD5 -> $POST_HST_MD5"; exit 5; }
  case "$POST_TIMEDIRS" in
    UNMEASURED|0)
      stage_say "ABORT S4 the post-copy source count is $POST_TIMEDIRS -- the comparison cannot be made."
      exit 5 ;;
  esac
  test "$POST_TIMEDIRS" = "$SRC_TIMEDIRS" || { stage_say "ABORT S4 SOURCE CHANGED during the copy: mp04/processor0 entries $SRC_TIMEDIRS -> $POST_TIMEDIRS"; exit 5; }
  stage_say "D6RF4_STAGE_P_conv (S4) OK cp -a (mtimes PRESERVED), copy_epoch=$COPY_EPOCH, SOURCE INTACT after the copy -- and the comparison COUNTED $SRC_TIMEDIRS entries on both sides, so it cannot have passed on a pair of false zeros"
  # ------------------------------------------------------------------ S5
  # DROP THE OPTIMISER'S OUTPUTS FROM THE COPY.  D6RF-DEF-2: pyDAFoam's
  # renameSolution refuses to move onto an existing directory -- D4's arm F2,
  # rc=1 at 56 s.  `0` is KEPT (initial fields and the restart state); so are
  # constant/, system/, FFD/, dRdWColoring_4.bin and OptView.hst.
  # `0` and `0.orig` are KEPT and must never match: `0.orig` carries letters, so
  # the numeric test below excludes it, and `0` is excluded by name.  A bare
  # `0.*` glob would have deleted `0.orig` -- the pristine initial-condition
  # backup -- which is why the test is a NAME TEST and not a glob.
  is_time_dir() {
    case "$1" in
      0|"") return 1 ;;
      *[!0-9.]*) return 1 ;;
      *.*.*) return 1 ;;
      *) return 0 ;;
    esac
  }
  count_time_dirs() {   # $1 = the tree to count under
    local n=0 d b
    for d in "$1"/mp04/* "$1"/mp05/* "$1"/mp06/* \
             "$1"/mp04/processor*/* "$1"/mp05/processor*/* "$1"/mp06/processor*/*; do
      [ -d "$d" ] || continue
      b=$(basename "$d")
      is_time_dir "$b" && n=$((n+1))
    done
    echo "$n"
  }
  BEFORE_DROP=$(count_time_dirs "$WORK")
  DROPPED=0
  for d in "$WORK"/mp04/* "$WORK"/mp05/* "$WORK"/mp06/* \
           "$WORK"/mp04/processor*/* "$WORK"/mp05/processor*/* "$WORK"/mp06/processor*/*; do
    [ -d "$d" ] || continue
    is_time_dir "$(basename "$d")" || continue
    rm -rf "$d" || { stage_say "ABORT S5 could not drop $d"; exit 5; }
    DROPPED=$((DROPPED+1))
  done
  for mp in mp04 mp05 mp06; do
    rm -rf "$WORK/$mp/postProcessing" 2>/dev/null
  done
  rm -rf "$WORK/reports" 2>/dev/null
  rm -rf "$WORK/postProcessing" 2>/dev/null
  rm -f  "$WORK/mphys.html" "$WORK/opt_IPOPT.txt" "$WORK/d6rf4_cmd.sh" 2>/dev/null
  REMAIN=$(count_time_dirs "$WORK")
  test "$REMAIN" -eq 0 || { stage_say "ABORT S5 $REMAIN output time directories remain in the COPY (required 0, dropped $DROPPED of $BEFORE_DROP)"; exit 5; }
  # `0` and `0.orig` SURVIVED, and that is asserted rather than assumed.
  for mp in mp04 mp05 mp06; do
    assert_field "S5 $mp/0" "$WORK/$mp/0" U \
      "The RECONSTRUCTED initial fields are KEPT, not swept -- is_time_dir() excludes '0' by name."
    test -d "$WORK/$mp/0.orig" || { stage_say "ABORT S5 $mp/0.orig was dropped -- the pristine backup is KEPT, not swept"; exit 5; }
    # THE SITE THAT ABORTED rc=5 ON THE FIRST FIRE.  decomposePar writes these
    # GZIPPED under writeCompression; the reconstructed sibling above is plain.
    assert_field "S5 $mp/processor0/0" "$WORK/$mp/processor0/0" U \
      "The DECOMPOSED restart state is KEPT, not swept.  These fields are gzipped on this case family (U.gz), which the predecessor's plain-name test could not see."
  done
  # AND THE SOURCE IS ASSERTED INTACT: D6R's evidence is not touched.
  # This is a POSITIVE assertion (`> 1`), so unlike S4's comparison it cannot
  # pass on a false zero -- a failed read gives 0 and 0 is not > 1, so it
  # refuses.  The UNMEASURED report is added for SYMMETRY and honesty of the
  # record, not because the comparison errs unsafely: a reader is entitled to
  # know the difference between "the source has been emptied" and "the count
  # could not be taken."
  SRC_REMAIN=$(count_src_entries "$SRC/mp04/processor0" "0.*")
  case "$SRC_REMAIN" in
    UNMEASURED)
      stage_say "ABORT S5 SOURCE INTACT assertion UNMEASURED: $SRC/mp04/processor0 is absent or unreadable, so this lane cannot say whether D6R's evidence is intact.  REFUSED rather than reported as 0."
      exit 5 ;;
  esac
  test "$SRC_REMAIN" -gt 1 || { stage_say "ABORT S5 SOURCE INTACT assertion FAILED: only $SRC_REMAIN pseudo-time dirs remain under $SRC/mp04/processor0 (required > 1) -- D6R's evidence may have been touched"; exit 5; }
  test -f "$WORK/OptView.hst" || { stage_say "ABORT S5 OptView.hst was dropped from the copy"; exit 5; }
  test -f "$WORK/mp04/dRdWColoring_4.bin" || { stage_say "ABORT S5 the cached colouring was dropped from the copy -- the cap is priced with it present"; exit 5; }
  stage_say "D6RF4_STAGE_P_conv (S5) OK dropped $DROPPED of $BEFORE_DROP output time directories from the COPY, $REMAIN remain (required 0); 0/, 0.orig/ and processor*/0/ KEPT and asserted; OptView.hst and dRdWColoring_4.bin KEPT; SOURCE INTACT ($SRC_REMAIN pseudo-time dirs still under $SRC/mp04/processor0)"
  # ------------------------------------------------------------------ S6
  cp -a "$BASE/d6rf4_extract_endpoint.py" "$BASE/d6rf4_fd_endpoint.py" \
        "$BASE/d6rf4_opt_runScript.py" "$BASE/d6rf4_endpoint_locus.py" \
        "$BASE/d6rf4_endpoint_physical.py" "$BASE/d6rf4_units_assert.py" \
        "$BASE/d6rf4_anchor_gate.py" \
        "$BASE/d6rf4_fvSolution_TIGHT" "$BASE/d6rf4_fvSolution_D6RF3_ORIGINAL" \
        "$WORK/" || { stage_say "ABORT S6 stage instruments"; exit 4; }
  { echo "$MD5_EXTRACT6  $WORK/d6rf4_extract_endpoint.py"
    echo "$MD5_FD  $WORK/d6rf4_fd_endpoint.py"
    echo "$MD5_RUNSCRIPT6  $WORK/d6rf4_opt_runScript.py"
    echo "$MD5_LOCUS6  $WORK/d6rf4_endpoint_locus.py"
    echo "$MD5_PHYS6  $WORK/d6rf4_endpoint_physical.py"
    echo "$MD5_UNITS  $WORK/d6rf4_units_assert.py"
    echo "$MD5_ANCHOR_GATE  $WORK/d6rf4_anchor_gate.py"
    echo "$MD5_FVSOL_TIGHT  $WORK/d6rf4_fvSolution_TIGHT"
    echo "$MD5_FVSOL_ORIG  $WORK/d6rf4_fvSolution_D6RF3_ORIGINAL"; } | md5sum -c - || { stage_say "ABORT S6 staged instrument md5 in the arm directory"; exit 4; }
  # `d6rf4_ref_off.py` IS NOT STAGED: `REF_off` is not a registered arm here,
  # and G-ANCHOR's READERS tuple was reduced to one reader to match, so a copy
  # of it in $WORK would be a file nothing reads and the delivery closure's
  # dangling check would have to be told to ignore it.  Named, not silent.
  stage_say "D6RF4_STAGE_P_conv (S6) OK SEVEN instruments and BOTH fvSolution files staged, every md5 asserted on BOTH sides of the copy; d6rf4_ref_off.py DELIBERATELY NOT STAGED (REF_off is not registered at this freeze)"
  # ------------------------------------------------------------------ S7
  UNITS_RUNSCRIPT=d6rf4_opt_runScript.py
  DVFILE=d6rf4_endpoint_dvs.json
  for p in d6rf4_endpoint_dvs_PHYSICAL.json d6rf4_endpoint_dvs_DRIVERSCALED.json \
           d6rf4_endpoint_dvs.json d6rf4_major_history.json d6rf4_fd_endpoint.json \
           d6rf4_fd_endpoint.jsonl d6rf4_f5_endpoint.json d6rf4_f5_endpoint.jsonl \
           d6rf4_fd_endpoint.json.partial d6rf4_f5_endpoint.json.partial; do
    rm -f "$WORK/$p"
  done
  stage_say "D6RF4_STAGE_P_conv (S7) OK this arm's registered products swept from the copy, INCLUDING the `.partial` temporaries the DEF-7 incremental writer renames from -- a stale `.partial` is a half-written product wearing a product's name"

  # ------------------------------------------------------------------ S9
  # ============ THE TIGHTENED STOPPING RULE IS INSTALLED HERE ============
  # THE ONE THING D6RF4 CHANGES ABOUT THE PRIMAL, and it is installed with the
  # PRE-IMAGE asserted at every site.  This arm may only tighten THE FILE
  # D6RF3 ACTUALLY RAN: a site whose pre-image md5 is not $MD5_FVSOL_ORIG is a
  # site carrying some other fvSolution, and overwriting it would make the
  # comparison to D6RF3 meaningless.  ABORT, never overwrite blind.
  #
  # THE LOOP ASSERTS ITS OWN TRIP COUNT.  A `for` over a path list that
  # happens to match nothing installs nothing and prints success -- the
  # planted-zero failure in a bash guard.  The count is compared against the
  # ENUMERATED $FVSOL_SITES, and zero REFUSES.
  FVSOL_EXPECT=$(echo $FVSOL_SITES | wc -w)
  FVSOL_DONE=0
  for sd in $FVSOL_SITES; do
    tgt="$WORK/$sd/fvSolution"
    test -f "$tgt" || { stage_say "ABORT S9 fvSolution absent at $tgt -- the tightened stopping rule cannot be installed where there is no file to replace"; exit 5; }
    PRE=$(md5sum "$tgt" | cut -d' ' -f1)
    test "$PRE" = "$MD5_FVSOL_ORIG" || {
      stage_say "ABORT S9 PRE-IMAGE MISMATCH at $tgt"
      stage_say "  on disk  : $PRE"
      stage_say "  expected : $MD5_FVSOL_ORIG (the file D6RF3's F_mp arm ACTUALLY RAN)"
      stage_say "  This site carries some OTHER fvSolution.  Tightening it would"
      stage_say "  make G-SOLN's comparison to D6RF3 meaningless, because the two"
      stage_say "  runs would differ in more than the stopping rule.  REFUSED."
      exit 5; }
    cp -a "$WORK/d6rf4_fvSolution_TIGHT" "$tgt" || { stage_say "ABORT S9 install failed at $tgt"; exit 4; }
    POST=$(md5sum "$tgt" | cut -d' ' -f1)
    test "$POST" = "$MD5_FVSOL_TIGHT" || { stage_say "ABORT S9 POST-IMAGE at $tgt is $POST, not $MD5_FVSOL_TIGHT -- the copy did not land intact"; exit 4; }
    FVSOL_DONE=$((FVSOL_DONE+1))
    stage_say "D6RF4_STAGE_P_conv (S9) site $sd  pre=$PRE -> post=$POST"
  done
  test "$FVSOL_DONE" -ge 1 || { stage_say "ABORT S9 the install loop ran ZERO times.  A loop that installs nothing and reports success is a planted zero."; exit 5; }
  test "$FVSOL_DONE" = "$FVSOL_EXPECT" || { stage_say "ABORT S9 installed $FVSOL_DONE of an ENUMERATED $FVSOL_EXPECT sites"; exit 5; }
  # THE READ-BACK, FROM DISK, OVER THE WHOLE TREE AND NOT OVER THE LIST.
  # Asserting the list against itself would be tautological; this asks the
  # DISK whether any fvSolution anywhere under $WORK is still the loose one.
  STRAGGLERS=$(find "$WORK" -name fvSolution -not -path '*/processor*' -exec md5sum {} \; 2>/dev/null | grep -c "^$MD5_FVSOL_ORIG " || true)
  case "$STRAGGLERS" in ''|*[!0-9]*) STRAGGLERS=UNMEASURED ;; esac
  test "$STRAGGLERS" = "0" || { stage_say "ABORT S9 READ-BACK: $STRAGGLERS fvSolution file(s) under $WORK still carry the LOOSE md5 $MD5_FVSOL_ORIG (or the scan was $STRAGGLERS).  Some leg would silently run D6RF3's stopping rule."; exit 5; }
  FOUND_TIGHT=$(find "$WORK" -name fvSolution -not -path '*/processor*' -exec md5sum {} \; 2>/dev/null | grep -c "^$MD5_FVSOL_TIGHT " || true)
  stage_say "D6RF4_STAGE_P_conv (S9) OK tightened fvSolution installed at $FVSOL_DONE of $FVSOL_EXPECT ENUMERATED sites, pre-image asserted = $MD5_FVSOL_ORIG at every one; READ-BACK over the whole tree found $FOUND_TIGHT tight and 0 loose"
else
  # ---------------------------------------------------------------------
  # UNREACHABLE, AND KEPT AS A BRANCH ON PURPOSE.
  # The arm guard above already refuses every arm but `P_conv`, so control
  # cannot arrive here.  The branch is retained for TWO reasons and both are
  # mechanical: G-DELIVERY's derivation locates the arm branch BY PATTERN and
  # asserts exactly one opener with an `else`/`fi` at column 0 -- deleting the
  # branch would make that guard REFUSE-SHAPE -- and a successor that adds a
  # second arm has the shape to add it into, with the branch-awareness the
  # closure needs already in place.  A branch that cannot run is not a cost;
  # a guard that cannot find its shape is.
  # D6RF3's REF_off staging lived here, 44 lines, and is NOT carried: this
  # item does not register that arm, does not price it and does not buy it.
  stage_say "ABORT UNREACHABLE arm='$ARM' reached the non-P_conv staging branch"
  stage_say "  The arm guard should have refused this before any staging.  If"
  stage_say "  this line is ever printed, the guard and the branch disagree and"
  stage_say "  the launcher is not doing what it says.  REFUSED."
  exit 64
fi

# ===========================================================================
# G-DELIVERY -- EVERY INSTRUMENT THIS FILE WILL READ AT $WORK IS PRESENT THERE.
#
# THE DEFECT THIS EXISTS FOR, 2026-09-03T22:13:11Z.  D6RF4 launched and aborted
# 70 s later at rc 4 on `md5sum: .../F_mp/d6rf4_anchor_gate.py: No such file or
# directory`.  G-ANCHOR is an excellent gate; it was simply never staged where
# this launcher looks for it.  TEN SIBLING INSTRUMENTS ARE COPIED INTO $WORK AND
# THAT ONE WAS MISSED -- a pattern applied correctly everywhere except one
# neighbour, where the neighbours are entries in a list.  BOTH ARMS WERE
# AFFECTED, not just F_mp: the reference at :623/:624 is UNCONDITIONAL, outside
# the arm branch, so REF_off would have failed identically.
#
# WHY THIS IS DERIVED AND NOT A LIST.  A hand-written list of required files is
# what produced the defect; a second hand-written list would produce the next
# one.  THE LAUNCHER ALREADY STATES WHAT IT NEEDS -- every `$WORK/<file>` it
# md5-checks or executes IS the requirement -- so the set is READ OUT OF THIS
# FILE'S OWN BYTES at run time rather than maintained as a parallel copy of the
# answer.  Same shape as a1wrt_controldict.py deriving A1WR's controlDict from
# A1WR's own heredoc instead of retyping it.
#
# IT IS BRANCH-AWARE, and it stays branch-aware even though this freeze
# registers ONE arm: references inside the `if [ "$ARM" = "P_conv" ]` block are
# P_conv's, references inside its `else` are the UNREACHABLE branch's, and
# references outside both are required by EVERY arm.  The branch is located BY
# PATTERN, never by line number.  Keeping the awareness on a one-arm item is
# deliberate -- a successor that adds a second arm inherits a guard that
# already knows the difference instead of one that has to be taught it.
#
# AND IT FAILS CLOSED IN THREE WAYS, because a derivation that quietly finds
# nothing is indistinguishable from one that found nothing wrong (rule 3):
#   - the arm branch cannot be located          -> REFUSE, do not guess
#   - the derived required set is EMPTY          -> REFUSE; a reader that
#     requires nothing has not proved delivery, it has failed to read
#   - any required file is absent from $WORK     -> REFUSE, NAMING each missing
#     file and the directory it was expected in.  `rc=4` on a bare `md5sum -c`
#     told a reader nothing about delivery, which is why this rc is its own.
# ===========================================================================
# --- the derivation, run as a function so it can be re-run as a READ-BACK ----
derive_delivery() {
  python3 - "${BASH_SOURCE[0]}" "$ARM" "$WORK" <<'PYEOF'
import ast, re, sys, pathlib
self_path, arm, work = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
src = pathlib.Path(self_path).read_text(errors="replace").splitlines()
PYNAME = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9_.-]*\.py$')

# ---- LEVEL 0: what THIS LAUNCHER md5-checks or executes at $WORK ------------
opens = [i for i, l in enumerate(src, 1)
         if re.match(r'^if \[ "\$ARM" = "P_conv" \]; then\s*$', l)]
if len(opens) != 1:
    print("REFUSE-SHAPE expected exactly 1 arm-branch opener in %s, found %d "
          "-- the launcher's shape has MOVED and this guard will not guess"
          % (self_path, len(opens))); sys.exit()
o = opens[0]
els = next((i for i, l in enumerate(src, 1) if i > o and l == "else"), None)
fin = next((i for i, l in enumerate(src, 1) if els and i > els and l == "fi"), None)
if not els or not fin:
    print("REFUSE-SHAPE could not locate the arm branch's else/fi at column 0 "
          "(if@%s else@%s fi@%s)" % (o, els, fin)); sys.exit()
pm = re.compile(r'echo "\$MD5_\w+\s+\$WORK/([A-Za-z0-9_.]+)"')
pe = re.compile(r'python3 "\$WORK/([A-Za-z0-9_.]+)"')
req = set()
for i, l in enumerate(src, 1):
    for p in (pm, pe):
        m = p.search(l)
        if not m:
            continue
        region = "P_conv" if o < i < els else ("UNREACHABLE" if els < i < fin else "BOTH")
        if region in ("BOTH", arm):
            req.add(m.group(1))
if not req:
    print("REFUSE-EMPTY the derivation found ZERO level-0 instruments for arm=%s. "
          "A guard that requires nothing has not proved delivery, it has failed "
          "to read." % arm); sys.exit()
level0 = len(req)

def declared_py(path):
    """MODULE-LEVEL .py filename constants, from the file's OWN bytes via ast.

    This is how an instrument states what it will itself open at $WORK --
    READERS, PRODUCER, EXTRACTOR, RUNSCRIPT, STAGED_PRODUCER and anything of
    that shape.  Read by ast from the source, never by a pattern maintained
    here, so a new constant of the same shape is picked up without editing
    this guard."""
    try:
        tree = ast.parse(path.read_text(errors="replace"), filename=str(path))
    except SyntaxError:
        return None
    out = set()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        v, vals = node.value, []
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            vals = [v.value]
        elif isinstance(v, (ast.Tuple, ast.List, ast.Set)):
            vals = [e.value for e in v.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        out |= {x for x in vals if PYNAME.match(x)}
    return out

# ---- CLOSE OVER THE PRODUCT, TO A FIXED POINT ------------------------------
# One level catches what the launcher names.  The 22:55:46Z abort was two
# levels down: d6rf4_ref_off.py is named ONLY by d6rf4_anchor_gate.py's own
# READERS tuple, which the launcher never mentions.  A detection catches the
# level you thought of; a closure catches the level you did not.
ROUNDS = 8
for _ in range(ROUNDS):
    grew = set()
    for name in sorted(req):
        f = work / name
        if not f.is_file():
            continue
        d = declared_py(f)
        if d is None:
            print("REFUSE-UNPARSEABLE %s is not parseable Python, so what it "
                  "opens at $WORK cannot be derived -- UNMEASURED, not assumed "
                  "empty" % name); sys.exit()
        grew |= d
    if grew <= req:
        break
    req |= grew
else:
    print("REFUSE-NONCONVERGENT the requirement closure did not settle in %d "
          "rounds for arm=%s -- REFUSED rather than silently stopping at the "
          "bound, because a set truncated at a depth is not a closure" % (ROUNDS, arm))
    sys.exit()

# ---- (A) every DERIVED requirement is present ------------------------------
missing = sorted(n for n in req if not (work / n).is_file())
if missing:
    print("MISSING %d of %d required instrument(s) absent from %s: %s"
          % (len(missing), len(req), work, " ".join(missing))); sys.exit()

# ---- (B) COMPLETENESS, AND IT IS NOT THE FIXED POINT RESTATED --------------
# Asserting the closure against itself would be tautological.  This asserts a
# property of the DISK: every .py actually staged in $WORK -- including files
# that arrived with the base copy and were never in the derived set -- must
# reference only .py files that are ALSO present.  It can fire, and on the
# 22:55:46Z state it does: d6rf4_anchor_gate.py -> d6rf4_ref_off.py, absent.
dangling = []
for f in sorted(work.glob("*.py")):
    d = declared_py(f)
    if d is None:
        continue
    for target in sorted(d):
        if not (work / target).is_file():
            dangling.append("%s -> %s" % (f.name, target))
if dangling:
    print("REFUSE-DANGLING %d staged instrument reference(s) point at a file "
          "absent from %s: %s" % (len(dangling), work, "; ".join(dangling)))
    sys.exit()

print("OK %d required instruments (%d level-0, %d by closure) derived, all "
      "present, and no staged instrument references an absent file: %s"
      % (len(req), level0, len(req) - level0, " ".join(sorted(req))))
PYEOF
}

DELIVERY=$(derive_delivery)
# ---- STAGE what the closure requires and the hand list did not deliver -----
# $BASE is the md5-verified source: d6rf4_chain_driver.sh asserts all twelve
# instrument md5s there before any arm runs.  The arm-side copy is asserted
# BYTE-IDENTICAL to it with `cmp`, so the requirement is met from verified
# bytes and never from a second hand list.
case "$DELIVERY" in
  MISSING*)
    NEED=$(printf '%s' "$DELIVERY" | sed 's/.*: //')
    stage_say "D6RF4_G_DELIVERY closure requires files the arm list did not stage: $NEED"
    for f in $NEED; do
      test -f "$BASE/$f" || { stage_say "ABORT G-DELIVERY $f is required at \$WORK and is ABSENT FROM \$BASE TOO -- it was never staged into the run root, so no verified copy exists to deliver"; exit 8; }
      cp -a "$BASE/$f" "$WORK/$f" || { stage_say "ABORT G-DELIVERY could not stage $f into $WORK"; exit 8; }
      cmp -s "$BASE/$f" "$WORK/$f" || { stage_say "ABORT G-DELIVERY staged $f is NOT byte-identical to the md5-verified copy in \$BASE -- the copy did not land intact"; exit 8; }
      stage_say "D6RF4_G_DELIVERY staged $f from \$BASE, asserted byte-identical"
    done
    # THE READ-BACK: the same derivation, again, on the new disk state.
    DELIVERY=$(derive_delivery) ;;
esac
case "$DELIVERY" in
  OK\ *) stage_say "D6RF4_G_DELIVERY $DELIVERY" ;;
  MISSING*)
    stage_say "ABORT G-DELIVERY arm=$ARM -- $DELIVERY"
    stage_say "  Still absent after staging from \$BASE.  NO CONTAINER IS CREATED."
    exit 8 ;;
  REFUSE-DANGLING*)
    stage_say "ABORT G-DELIVERY arm=$ARM -- $DELIVERY"
    stage_say "  A staged instrument names a file that is not there.  This is the"
    stage_say "  22:55:46Z class, caught BEFORE the gate rather than by its traceback."
    exit 8 ;;
  *)
    stage_say "ABORT G-DELIVERY arm=$ARM -- the delivery derivation could not be"
    stage_say "  performed, so delivery is UNMEASURED and is NOT reported as clean."
    stage_say "  $DELIVERY"
    exit 8 ;;
esac

# ===========================================================================
# THE UNITS GATE, CALL SITE 1 OF 2 (CLAUDE.md rule 14 -- a lesson is not applied
# until EVERY call site asserts it).  HOST SIDE, at staging: if an endpoint
# design-variable file survived the product sweep above, it is graded HERE and
# a refusal is rc 7, distinct.  A MISSING MARKER IS A REFUSAL, NEVER A DEFAULT.
# ===========================================================================
if [ -e "$WORK/$DVFILE" ]; then
  stage_say "D6RF4_UNITS_CALLSITE_1 arm=$ARM an endpoint artefact SURVIVED the sweep: $WORK/$DVFILE -- grading it before anything else runs"
  python3 "$WORK/d6rf4_units_assert.py" "$WORK/$DVFILE" --runscript "$WORK/$UNITS_RUNSCRIPT"
  UR=$?
  if [ "$UR" -ne 0 ]; then
    stage_say "ABORT UNITS (call site 1, host) arm=$ARM file=$WORK/$DVFILE assert_rc=$UR"
    stage_say "  A design vector that cannot prove it is PHYSICAL is never handed"
    stage_say "  to the mesh deformer.  D4 arm F: no marker, 62 of 96 shape"
    stage_say "  components outside [-1,1], max |value| 6.024592, rc=1 at 15 s."
    exit 7
  fi
else
  stage_say "D6RF4_UNITS_CALLSITE_1 arm=$ARM no endpoint artefact survived the sweep (expected on a first fire); call site 2 grades the one the wrapper writes"
fi


# ===========================================================================
# G-ANCHOR -- INVOKED HERE, AT STAGING, BEFORE ANY CONTAINER.
# PREREGISTRATION.md section 3.  D6RF-BLOCKING-1 is the reason: BOTH consumers
# refused honestly on `count != 1`, but nothing checked whether the producer
# could SATISFY them -- so an unrunnable registration became a launch instead of
# a defect found before compute.  The gate is run over the arm directory's OWN
# staged bytes, so it checks what the container will actually read.
# A refusal here is rc 3 and NO CONTAINER IS CREATED.
# ===========================================================================
echo "$MD5_ANCHOR_GATE  $WORK/d6rf4_anchor_gate.py" | md5sum -c - || { stage_say "ABORT G-ANCHOR gate md5"; exit 4; }
python3 "$WORK/d6rf4_anchor_gate.py" --work-dir "$WORK" || {
  stage_say "ABORT G-ANCHOR arm=$ARM -- a reader that splits the producer on a sentinel"
  stage_say "  cannot be shown that sentinel is unique in the bytes it will read."
  stage_say "  THIS IS THE D6RF-BLOCKING-1 CLASS, REFUSED BEFORE A CONTAINER RATHER"
  stage_say "  THAN AFTER ONE.  See the gate's own refusal line above."
  exit 3; }
stage_say "D6RF4_G_ANCHOR OK arm=$ARM -- every anchor-scoped reader's sentinel is unique in the producer it will read, and the header it yields carries every symbol it execs"
# ---- THE AGE DATUM IS WRITTEN LAST (section 2a S8, CLAUDE.md rule 4) ------
touch "$WORK/0"/* || { stage_say "ABORT S8 age-guard datum"; exit 5; }
# THE MOST DANGEROUS OF THE FOUR SITES, AND IT FAILED SILENTLY RATHER THAN LOUDLY.
# The predecessor read `stat -c %Y "$WORK/0/U"` by the plain name.  On a tree whose
# `0/` is gzipped, `stat` prints an error to stderr and returns EMPTY -- so
# AGE_DATUM would be the empty string, `.d4_age_datum` would hold a blank line, and
# the arm command would carry `--age-datum ` with no value.  The physical wrapper
# would then refuse, so it fails safe -- but LATE, and with a message about the
# wrapper rather than about the datum.  Here it is resolved by name and ASSERTED
# to be a non-empty integer before it is used.
AGE_SRC=$(field_path "$WORK/0" U) || \
  assert_field "S8 age datum" "$WORK/0" U \
    "The age datum is read from this file's mtime; every registered product must be strictly newer than it (CLAUDE.md rule 4)."
AGE_DATUM=$(stat -c '%Y' "$AGE_SRC")
case "$AGE_DATUM" in
  ''|*[!0-9]*) stage_say "ABORT S8 the age datum read from $AGE_SRC is not an integer: '$AGE_DATUM'"
               stage_say "  An empty or non-numeric datum makes the age guard unenforceable, and rule 4's age guard is PHYSICS."
               exit 5 ;;
esac
echo "$AGE_DATUM" > "$WORK/.d4_age_datum"
stage_say "D6RF4_G_COLD OK arm=$ARM age_datum_epoch=$AGE_DATUM (every registered product must be strictly newer)"

# ===========================================================================
# THE ARM COMMAND.  THE UNITS GATE IS CALL SITE 2 OF 2 AND IT SITS BETWEEN THE
# WRAPPER THAT WRITES THE DESIGN VECTOR AND THE mpirun THAT CONSUMES IT.  `&&`
# chaining means a units refusal (rc 77) propagates as the container's own
# ExitCode and THE MESH IS NEVER TOUCHED.
# ===========================================================================
# THREE LEGS, ONE CONTAINER (PREREGISTRATION.md section 8.2).  The container
# frame is bought once and amortised across all three, which is why the cost
# table carries `2.067 - 1.314 = 0.800` core-min of frame and not three frames.
#
# THE fvSolution SWAP IS THE ONLY THING THAT DIFFERS BETWEEN L1/L2 AND L3, and
# every install PRINTS its md5 and its site count into the log, so the grader
# can ASSERT that each leg ran the file it was registered to run rather than
# taking this launcher's word for it.  `install_fvsol` REFUSES on a zero site
# count: a swap that swapped nothing would silently run L3 at the TIGHT
# settings, and F5 would then "fail to fail" for a bookkeeping reason.
#
# `&&` CHAINING THROUGHOUT, so a units refusal (rc 77) propagates as the
# container's own ExitCode and THE MESH IS NEVER TOUCHED.  L3 is chained too:
# `d6rf4_fd_endpoint.py --mode F5_loose` catches DAFoam's post-`End` refusal
# itself and exits 0, because that refusal is F5's DATUM and not the arm
# failing -- and it does so WITHOUT MOVING THE ACCEPT FLOOR.
read -r -d '' CMD_PCONV <<'LEGEOF' || true
set -o pipefail
install_fvsol() {           # $1 = source file in $PWD, $2 = expected md5, $3 = leg
  n=0
  for sd in system mp04/system mp05/system mp06/system; do
    [ -f "$sd/fvSolution" ] || { echo "D6RF4_LEG_ABORT leg=$3 no fvSolution at $sd"; return 5; }
    cp -a "$1" "$sd/fvSolution" || { echo "D6RF4_LEG_ABORT leg=$3 install failed at $sd"; return 5; }
    got=$(md5sum "$sd/fvSolution" | cut -d' ' -f1)
    [ "$got" = "$2" ] || { echo "D6RF4_LEG_ABORT leg=$3 post-image $got != $2 at $sd"; return 5; }
    n=$((n+1))
  done
  [ "$n" -ge 1 ] || { echo "D6RF4_LEG_ABORT leg=$3 installed ZERO sites -- a swap that swapped nothing"; return 5; }
  echo "D6RF4_FVSOLUTION_INSTALLED leg=$3 md5=$2 sites=$n file=$1"
  return 0
}
python d6rf4_endpoint_physical.py --age-datum __AGE_DATUM__ && \
python d6rf4_units_assert.py d6rf4_endpoint_dvs.json --runscript d6rf4_opt_runScript.py && \
install_fvsol d6rf4_fvSolution_TIGHT __MD5_TIGHT__ L1_L2 && \
mpirun --allow-run-as-root -np __RANKS__ --bind-to core --report-bindings -x PYTHONPATH \
  python d6rf4_fd_endpoint.py --mode P_conv && \
install_fvsol d6rf4_fvSolution_D6RF3_ORIGINAL __MD5_ORIG__ L3 && \
mpirun --allow-run-as-root -np __RANKS__ --bind-to core --report-bindings -x PYTHONPATH \
  python d6rf4_fd_endpoint.py --mode F5_loose
LEGEOF
case "$ARM" in
  P_conv)
    CMD=$(printf '%s' "$CMD_PCONV" \
          | sed -e "s|__AGE_DATUM__|$AGE_DATUM|g" \
                -e "s|__MD5_TIGHT__|$MD5_FVSOL_TIGHT|g" \
                -e "s|__MD5_ORIG__|$MD5_FVSOL_ORIG|g" \
                -e "s|__RANKS__|$RANKS|g") ;;
esac
case "$CMD" in
  *__AGE_DATUM__*|*__MD5_TIGHT__*|*__MD5_ORIG__*|*__RANKS__*)
    echo "ABORT the arm command still carries an unsubstituted placeholder;"
    echo "  a container would run with a literal __TOKEN__ where a value belongs."
    exit 4 ;;
esac
case "$CMD" in
  *d6rf4_units_assert.py*) : ;;
  *) echo "ABORT the arm command for $ARM does not invoke the units gate; call site 2 is missing (rule 14)"; exit 7 ;;
esac
# THE THREE LEGS ARE ASSERTED PRESENT IN THE COMMAND, BY NAME.  A cost table
# that prices three legs and a command that runs two is the shape a reader
# cannot see and a ledger cannot report.
for need in "--mode P_conv" "--mode F5_loose" \
            "install_fvsol d6rf4_fvSolution_TIGHT" \
            "install_fvsol d6rf4_fvSolution_D6RF3_ORIGINAL"; do
  case "$CMD" in
    *"$need"*) : ;;
    *) echo "ABORT the arm command for $ARM does not contain '"'"'$need'"'"'; the"
       echo "  registered three-leg program is not what would run.  REFUSED."
       exit 4 ;;
  esac
done
echo "D6RF4_CMD_LEGS_PRESENT arm=$ARM legs=L1,L2(--mode P_conv) L3(--mode F5_loose) fvSolution_swaps=2"

CMDFILE="$WORK/d6rf4_cmd.sh"
printf '%s\n' "$CMD" > "$CMDFILE" || { echo "ABORT cmd file"; exit 4; }
echo "D6RF4_CMDFILE arm=$ARM md5=$(md5sum "$CMDFILE" | cut -d' ' -f1) deadline_in_container_s=$TMO units_gate=present"

CPUSAMPLE="$BASE/${ARM}_${STAMP}.cpu.jsonl"
# DELIVERED CORES ARE MEASURED, NOT INFERRED FROM THE QUOTA FLAG.  Passive
# reader; an absent sample file is reported NOT_MEASURED, never as a pass.
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
      # A TRANSIENTLY UNREADABLE cgroup file is UNMEASURED, never 0.  The
      # predecessor's `|| echo 0` let a failed read contribute a zero CPU
      # sample; that drags `delivered_cores` DOWN, so it errs toward GATE FAIL
      # rather than toward a false pass -- but a zero that means "could not
      # read" is still a planted zero, and the `-n "$u"` guard below already
      # knows how to skip a sample it does not have.
      raw=$(cat "$cg" 2>/dev/null)
      case "$raw" in
        ''|*[!0-9]*) u=""; echo '{"delivered_cores":null,"note":"cgroup read UNMEASURED this tick"}' >> "$CPUSAMPLE" ;;
        *) u=$(( raw / 1000 )) ;;
      esac
      t=0; n=0
    fi
    if [ -n "$prev" ] && [ -n "$u" ]; then
      python3 -c "
import json
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
# rc CAPTURE IS CLOSED (docker inspect, no --rm).  The CAP lives INSIDE the
# container (`timeout -k 60 $TMO`) and survives shell death.  NOTHING here reads
# `$?` of a setsid or timeout line -- the setsid parent returns 0 for every
# outcome, which is why the rc is taken from the kernel below.
sudo -n docker run -d --name "$NAME" \
    --user 0:0 --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM --memory-swap=$MEM --oom-score-adj=500 \
    -v "$BASE":/mnt -w "/mnt/$(basename "$WORK")" "$IMG" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     echo D4S_CONTAINER_UID: \$(id -u) && \
     python -c 'import idwarp,os,hashlib; p=idwarp.__file__; so=os.path.join(os.path.dirname(p),\"libidwarp.so\"); print(\"D4S_IDWARP_IMPORTED_FROM:\",p); print(\"D4S_IDWARP_SO_MD5:\",hashlib.md5(open(so,\"rb\").read()).hexdigest())' && \
     echo D4S_DEADLINE_IN_CONTAINER_S: $TMO && \
     timeout -k $KILL_GRACE_S $TMO bash /mnt/$(basename "$WORK")/d6rf4_cmd.sh" > /dev/null 2>&1 \
  || { echo "ABORT could not start container"; exit 4; }

# The cap is a RUNAWAY GUARD THAT REPORTS (Sanaa, 2026-08-25); the CEILING is
# the fleet safety stop (Sanaa, 2026-09-03 ~21:00Z): far above the estimate, not
# the estimate itself, and it stops the run gracefully regardless of trend.
CEILING=$(python3 -c "print('%.1f' % (3.0*$CAP))")
echo "D6RF4_RUNAWAY_GUARD arm=$ARM cap_core_min=$CAP ceiling_core_min=$CEILING mode=report_then_graceful_stop_at_ceiling"
CAP_REPORTED=no; CEILING_HIT=no
while true; do
  RUNNING=$(sudo -n docker inspect --format '{{.State.Running}}' "$NAME" 2>/dev/null)
  NOW=$(date -u +%s); EL=$((NOW-T0))
  CM=$(python3 -c "print(round($EL*$RANKS/60.0,3))")
  if [ "$RUNNING" != "true" ]; then break; fi
  if [ "$CAP_REPORTED" = "no" ] && [ "$(python3 -c "print(1 if $CM > $CAP else 0)")" = "1" ]; then
    CAP_REPORTED=yes
    echo "D6RF4_CAP_CROSSED arm=$ARM core_min=$CM cap=$CAP ceiling=$CEILING action=REPORTED_RUN_CONTINUES supervisor_decides" | tee -a "$BASE/ledger.txt"
  fi
  if [ "$(python3 -c "print(1 if $CM > $CEILING else 0)")" = "1" ]; then
    CEILING_HIT=yes
    echo "D6RF4_CEILING_HIT arm=$ARM core_min=$CM ceiling=$CEILING action=GRACEFUL_STOP" | tee -a "$BASE/ledger.txt"
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
v=[]; thr=0
for line in open(p):
    try: d=json.loads(line)
    except Exception: continue
    if d.get('delivered_cores') is not None: v.append(d['delivered_cores'])
    thr=max(thr, d.get('nr_throttled') or 0)
print('%s n=%d max_nr_throttled=%d' % (('%.4f'%(sum(v)/len(v)) if v else 'NOT_MEASURED'), len(v), thr))
" 2>/dev/null)

INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' "$NAME" 2>/dev/null)
# THE CONTAINER'S OWN KERNEL CLOCK, in the same inspect and BEFORE the rm.  This
# is the frame the deadline is ENFORCED in; WALL (T0..T1) is the frame the cap
# is GRADED in.  Recording both SEPARATES them instead of conflating them, and
# the grader BINDS the difference at G-CAPS.  Absent -> NOT_MEASURED
# (INFRASTRUCTURE, L-342); the gate then falls back to the HOST bracket alone,
# which is the STRICTER reading, so the fallback can never turn a failing cap
# into a pass.
CSTART=$(sudo -n docker inspect --format '{{.State.StartedAt}}' "$NAME" 2>/dev/null)
CFIN=$(sudo -n docker inspect --format '{{.State.FinishedAt}}' "$NAME" 2>/dev/null)
CWALL=$(python3 -c "
import datetime
def p(s):
    s = s.strip().replace('Z', '+00:00')
    i = s.find('.')
    if i >= 0:
        j = i + 1
        while j < len(s) and s[j].isdigit():
            j += 1
        if j - i > 7:
            s = s[:i + 7] + s[j:]
    return datetime.datetime.fromisoformat(s)
try:
    print(int(round((p('$CFIN') - p('$CSTART')).total_seconds())))
except Exception:
    print('NOT_MEASURED')
" 2>/dev/null)
test -n "$CWALL" || CWALL=NOT_MEASURED
echo "D6RF4_CONTAINER_CLOCK arm=$ARM started_at=$CSTART finished_at=$CFIN container_wall_s=$CWALL host_wall_s_bracket_T0_T1=$WALL"
sudo -n docker rm "$NAME" >/dev/null 2>&1
sudo -n chown -R ubuntu:ubuntu "$LOG" "$WORK" 2>/dev/null

# A UNITS REFUSAL IN THE CONTAINER IS NAMED ON THE RECORD, not left as a bare
# exit code a reader has to look up.
if [ "$rc" = "77" ]; then
  echo "D6RF4_UNITS_REFUSAL_IN_CONTAINER arm=$ARM rc=77 -- call site 2 refused the design vector; THE MESH WAS NEVER TOUCHED.  See $(basename "$LOG") for the failing check." | tee -a "$BASE/ledger.txt"
fi

CORE_MIN=$(python3 -c "print(round($WALL*$RANKS/60.0,3))")
MEMAVAIL_POST=$(python3 -c "print('%.2f' % ($(awk '/MemAvailable/{print $2}' /proc/meminfo)/1048576.0))")
LEDGER="$BASE/ledger.txt"
{
  echo "ARM=$ARM ROW=$ROW IMG=$IMG DIGEST=$GOT_DIGEST rc=$rc wall_s=$WALL ranks=$RANKS core_min=$CORE_MIN cap_core_min=$CAP enforced_wall_s=$TMO enforced_core_min=$BACKCHECK memory=$MEM inspect(exit,oomkilled)=[$INSPECT] container_wall_s=$CWALL frame_allowance_s=$FRAME_ALLOWANCE_S memavail_GiB=$MEMAVAIL_GIB memavail_pre_GiB=$MEMAVAIL_GIB memavail_post_GiB=$MEMAVAIL_POST cpuset=$CPUSET delivered_cores_mean=[$DELIVERED] siblings_pre=[$SIBLINGS_PRE] siblings_post=[$SIBLINGS_POST] ceiling_hit=$CEILING_HIT log=$(basename "$LOG") stamp=$STAMP"
  grep -a "D4S_CONTAINER_UID\|D4S_IDWARP_SO_MD5\|D4S_DEADLINE_IN_CONTAINER_S\|D6RF4_UNITS_PASS" "$LOG" | head -4
} | tee -a "$LEDGER"
test -s "$LOG" && touch "$LOG.ok.${STAMP}"   # L-252 provenance sentinel
echo "STAMP=$STAMP RC=$rc CORE_MIN=$CORE_MIN"
exit $rc
