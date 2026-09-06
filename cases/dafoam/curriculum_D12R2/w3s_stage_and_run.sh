#!/bin/bash
# =============================================================================
# w3s_stage_and_run.sh -- THE W3S ARM A (`GSCAN`) LAUNCHER.  ONE LEG PER INVOCATION.
#
# UPDATED 2026-09-06.  THIS SCREEN USED TO SAY "IT LAUNCHES NOTHING", that the container
# invocation sat behind a `LAUNCH_ENABLED` of `0`, and that `W3S_PREREGISTRATION_DRAFT.md`
# was UNFROZEN and carried no committed sha.  ALL THREE SENTENCES ARE NOW FALSE and are
# replaced rather than left standing -- a stale claim on a file's first screen is exactly
# what a reader trusts, and this file can now start a container.
#
# THE CURRENT STATE, AND IT IS THE OPPOSITE OF THE OLD ONE:
#   - `W3S_PREREGISTRATION_DRAFT.md` IS FROZEN at `e1070c02` and this file's `PREREG_COMMIT`
#     records that sha, filled BY THE `dafoam-supervisor` (B3).  PREFLIGHT 0 now PASSES.
#   - `LAUNCH_ENABLED` IS `1`, RAISED BY THE SUPERVISOR as the enqueue act.  NO LANE MAY
#     RAISE IT AND NONE DID.
#   - THEREFORE THIS FILE LAUNCHES CONTAINERS.  `--selftest` still spends ZERO COMPUTE and
#     starts no container: both its launch-gate directions are driven against MUTATED COPIES
#     against a FRESH root, where the leg body's `FIELD_B is absent` refusal sits ahead of
#     every `docker run`.  THE SELFTEST'S ZERO-COMPUTE PROPERTY IS A PROPERTY OF ITS
#     FIXTURES, NOT OF A DISABLED FLAG, and that distinction is now the whole of the safety
#     argument.
#
# Under `SUPERVISION_CHARTER.md` sec.3 check 4 the *pre-registration committed before
# compute* check is the `dafoam-supervisor`'s own and may not be delegated.  This file still
# cannot discharge it and does not try to; it records that the supervisor did.
#
# -----------------------------------------------------------------------------
# WHY THIS FILE EXISTS AT ALL, WHICH IS NOT "TO RUN THE SOLVER"
# -----------------------------------------------------------------------------
# `w3s_grade.py` DEMANDS a manifest contract nothing on this box produced: a per-row `leg`
# key, a per-row `W`, and one `W_STEPS_<LEG>=` ledger line per leg.  Its gates -- N1, N2,
# N3, N4, N6, N7 -- read exactly those.  A GATE FED BY NOTHING IS WORSE THAN A MISSING
# GATE, BECAUSE IT REPORTS.  That is the defect that blocked `A1WRT2`'s freeze: two HARD
# gates there read `MANIFEST.json`, whose only writer turned out to be the selftest's own
# fixture builder.  This launcher, with `w3s_stage_record.py`, is the producer, and
# `--producer-trace` proves the binding MECHANICALLY by extracting the keys the frozen
# comparator reads out of the comparator's own AST and refusing if any has no producer.
#
# -----------------------------------------------------------------------------
# THE TWO LEG VOCABULARIES.  THEY ARE DIFFERENT AND THEY ARE NAMED.
# -----------------------------------------------------------------------------
#   COST LEGS      SETUP A0 A1 A2   what the registered caps price and what the cumulative
#                                   item-ceiling guard is asserted against.
#                                   5.0 + 100.0 + 70.0 + 155.0 = 330.0 EXACTLY, and the
#                                   sum is CHECKED HERE rather than trusted from a table.
#   MANIFEST LEGS  A0 A1 A2         what `w3s_grade._w_from_record_gscan` enumerates.
# The four setup stages run ONCE and feed all three windows from the same `FIELD_B`.  Their
# rows are filed under manifest leg `A0`: emitting them three times would be three records
# of one execution, and a fifth leg name would trip the comparator's N2.  Every row carries
# `cost_leg` as well, so the artefact states both vocabularies instead of leaving one in
# prose.
#
# -----------------------------------------------------------------------------
# ARM A IS STRUCTURALLY BARRED FROM `admissible: true`, AND THIS FILE CARRIES BAR-0
# -----------------------------------------------------------------------------
# Arm A omits S2b, S3, S3b, S4 and S7, so `delta_repeat` and `delta_pert` are NOT MEASURED
# and `delta_eff` cannot be formed.  `delta_eff` is a MAXIMUM, and removing a term from a
# maximum can only LOWER `h_min` -- i.e. move TOWARD `admissible: true`.  The comparator
# already refuses a step plan on gscan data at three depths (BAR-1 the sizing entry point,
# BAR-2 `--plan` on a multi-leg manifest, BAR-3 the emitted object walked for a
# re-introduced plan).  BAR-0 is this file's: THE LAUNCHER MUST NOT BE ABLE TO ASK.
# `bar0_no_step_plan_request` reads THIS FILE'S OWN SOURCE and refuses if a `--plan`,
# `--plan2` or `--plan3` token appears anywhere in it outside the guard and its comment.
# Driven in BOTH directions in `--selftest`, against a planted positive fixture.
#
# -----------------------------------------------------------------------------
# EVERY RESOURCE GUARD STATES WHAT A BLOCK DISCARDS (DAFOAM_CHARTER sec.18.7 Req 1 & 3)
# -----------------------------------------------------------------------------
# W3 died of exactly the omission this section repairs.  It registered
# `MEMAVAIL_FLOOR_GIB = 14.0` and did not state the guard's RESPONSE; the response was
# BLOCK-AND-CONTINUE, and a sustained condition discarded 20 of 33 declared stages -- 60.6 %
# of the program -- while the launcher printed `PHASE1_COMPLETE` and exited 0.  The loss was
# recorded PERFECTLY in two artefacts and NOTHING READ IT.
#
#   GUARD                RESPONSE                     WHAT ONE BLOCK DISCARDS
#   item ceiling         REFUSE BEFORE THE LEG, rc=6  the leg, and the arm (a three-point
#                                                     comparison has no partial answer)
#   in-leg budget        REFUSE BEFORE THE STAGE via  the leg, and the arm
#                        a shortened `timeout`, rc=6
#   MemAvailable floor   WAIT AND RE-POLL under a     nothing, while the wait holds; at the
#                        BOUNDED registered deadline; bound, the leg and the arm
#                        AT THE BOUND, TERMINATE rc=6
#   cold start           REFUSE BEFORE THE STAGE, rc=5 the leg, and the arm
#   age sentinel         REFUSE AFTER THE STAGE, rc=2  the leg, and the arm
#
# THERE IS NO BLOCK-AND-CONTINUE ANYWHERE IN THIS FILE.  Every guard either waits or
# terminates with a NON-ZERO rc, and NO call site consumes a non-zero rc into `|| echo`.
# W3's floor branch `return 8`ed into `run_stage ... || echo "STAGE X NONZERO rc"`, which
# ate it; that shape is absent here and `--selftest` drives its absence over this file's
# own source.
#
# THE MEMORY WAIT IS ATTACHED TO THE TRANSIENT QUANTITY, WHICH IS THE W3 FINDING.
# W3 put the bounded WAIT on the sum of registered caps -- a quantity that changes only
# when a container starts or stops -- and a one-shot BLOCK on live `MemAvailable`, which
# changes second by second.  A guard is correct only when its FORM matches the BEHAVIOUR
# of the quantity it watches.  Here the wait is on `MemAvailable`.
#
# `MEMAVAIL_POLL_S = 30` and `MEMAVAIL_WAIT_BOUND_S = 3600` WERE lane-proposed and carried
# by no document.  They are now REGISTERED in `W3S_PREREGISTRATION_DRAFT.md` sec.12.2,
# together with the guard's RESPONSE and the fraction a block discards -- the
# `dafoam-supervisor`'s ruling 4 of 2026-09-04, which put the choice as REGISTER THEM OR
# REMOVE THEM.  A launcher is not a registration, and a threshold enforced here and written
# nowhere is the `L-239` / DAFOAM_CHARTER sec.13-PROPOSAL shape running the other way.
#
# TWO CEILING GUARDS EXIST AND BOTH ARE KEPT, BY RULING 5, AND THE DIFFERENCE IS REGISTERED
# (draft sec.12.3) RATHER THAN INCIDENTAL.  `w3s_chain_driver.sh` asserts the ceiling with
# `w3s_grade.py --cumulative-item-ceiling` BEFORE each leg; this launcher asserts it with
# the committed `_common/item_ceiling_guard.py`.  They agree in five driven directions and
# differ BY DESIGN on ONE: an ABSENT ledger is FRESH 0.0 to the grader and UNMEASURED to
# the `_common` guard.  That is why this launcher BOOTSTRAPS the ledger -- and why the
# bootstrap itself refuses rc=65 rather than zeroing a root that already holds artefacts.
# A successor reading the disagreement as a defect and "fixing" the safer one would remove
# the UNMEASURED limb that is the whole point of the `_common` guard.
#
# -----------------------------------------------------------------------------
# THE MTIME QUESTION, ANSWERED RATHER THAN AVOIDED
# -----------------------------------------------------------------------------
# THIS ITEM STAGES WITH `cp -a`, WHICH PRESERVES mtimes.  A copied field therefore carries
# the SOURCE's mtime, and a datum taken from a copied file is exactly what a preserved
# mtime defeats.  So the age datum is NOT a copied file: it is a DEDICATED RUN-ROOT
# SENTINEL `.w3s_age_ref.<cost_leg>_<stage>`, created and TOUCHED LAST -- after every copy
# and after every cold-start assertion, immediately before the container starts.  That is
# `a1wrt2_stage.py:587-596`'s form, adopted because it is the one this family measured to
# be safe.  Two positive assertions come with it and both are recorded IN THE ROW:
#   (i)  NOTHING STAGED POST-DATES THE DATUM -- the preserved-mtime hazard actually
#        occurring, and it refuses;
#   (ii) THE SENTINEL DID NOT MOVE -- its mtime after the stage must equal the datum,
#        because a datum that shifted under the run cannot date the run.
# The parent launcher's datum is the staged `0/U` itself, `touch`ed after staging.  That
# works, and it is NOT what is used here: a datum inside the case directory is a datum the
# solver's own mount can reach, and (i) cannot be asked of it at all -- the file whose
# mtime you are validating is the file you set.
#
# -----------------------------------------------------------------------------
# WHAT IS INHERITED UNEDITED, AND FROM WHERE
# -----------------------------------------------------------------------------
#   d12y_w3_stage_and_run.sh  8a92f3f84f72d6806a2e5c5df88d82ef  the stage pipeline's shape;
#                             the FATAL/SIGNAL token list is READ OUT OF IT at runtime by
#                             `w3s_stage_record.py`, never copied.
#   d12y_grade_w3.py          3950d30fd09c9b56213a02f5e9864e20  FROZEN, UNEDITED; its
#                             `g0_completion` IS this launcher's rule-4 assertion, called.
#   d12y_run_script.py        2790c39a09cd458d5a3263d7f1811da5  UNCHANGED.
#   ../_common/item_ceiling_guard.py                            the cumulative ceiling
#                             guard, CALLED, never re-implemented and never ported from
#                             `d6rf_chain_driver.sh`, which fails open two ways.
#
# NOTHING HERE IS FILED, SENT, UPLOADED, REGISTERED, POSTED OR COMMENTED (CLAUDE.md rule
# 7).  SUBMISSIONS REMAIN PARKED.
# =============================================================================
set -uo pipefail

# --- 0 UNTIL THE FREEZE AND THE ENQUEUE LAND.  NO LANE MAY RAISE THIS. --------
LAUNCH_ENABLED=1            # RAISED 2026-09-06 BY THE dafoam-supervisor as the enqueue act (addendum 14). Lines 911/996/1006 are PROSE about the 0 state, deliberately untouched.

ITEM="W3S"
ARM="GSCAN"
# `W3S_BASE` exists for ONE reason and it is stated rather than left to be discovered: the
# md5-DRIFT plant in `--selftest` runs a MUTATED COPY of this file out of a temp directory,
# and without an overridable base that copy would resolve every instrument path into the
# temp directory and fail on EXISTENCE -- so the drift direction would never be driven and
# BOTH pin plants would pass FOR THE SAME WRONG REASON.  Found by reading this file's own
# selftest rather than by trusting its green.  It is not a hole: an override pointed at a
# tree whose instruments do not hash to the pins fails CLOSED at PREFLIGHT 1.
BASE="${W3S_BASE:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"

RECORD="$BASE/w3s_stage_record.py"
GRADER="$BASE/w3s_grade.py"
PARENT_GRADER="$BASE/d12y_grade_w3.py"
PARENT_LAUNCHER="$BASE/d12y_w3_stage_and_run.sh"
RUNPY="$BASE/d12y_run_script.py"
CEILING_GUARD="$BASE/../_common/item_ceiling_guard.py"

# ---- PINS.  Bumped IN THE SAME COMMIT as the files they pin (the D8R-DRIVER-DEF-1 /
# ---- 2026-08-28T02:15:29Z death: a driver whose pins lag its instruments by one commit
# ---- aborts every run and blames the wrong file).
MD5_RECORD="093ac4ed34a51fdd2eb46d09333a99b5"
MD5_GRADER="3a3ee623fa48cc1d81517638485f376b"
MD5_PARENT_GRADER="3950d30fd09c9b56213a02f5e9864e20"
MD5_PARENT_LAUNCHER="8a92f3f84f72d6806a2e5c5df88d82ef"
MD5_RUNPY="2790c39a09cd458d5a3263d7f1811da5"

# ---- THE FREEZE.  Empty until `dafoam-supervisor` freezes the pre-registration and
# ---- records the sha here, IN THE FREEZE COMMIT.  Empty means this launcher refuses.
PREREG_COMMIT="e1070c022678efe3a27f6dc75391380225a30380"  # filled 2026-09-06 BY THE dafoam-supervisor -- B3, the launcher's OWN freeze field, separate from the driver's
PREREG_FILE="$BASE/W3S_PREREGISTRATION_DRAFT.md"

# =============================================================================
# THE REGISTRATION.  Every constant below is drawn from W3S_PREREGISTRATION_DRAFT.md
# sec.2, sec.3.1 and sec.6.6, or is inherited from W3_PREREGISTRATION.md unchanged.
# =============================================================================
ROOT_DEFAULT="/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3S-GSCAN-cylinder-unsteady"
TUT="${TUT:-/home/ubuntu/dafoam-tutorials/Cylinder}"

IMG_SHIPPED="dafoam/opt-packages:latest"
ID_SHIPPED="sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc"

# --- cost legs and their registered caps (draft sec.6.6).  SUM CHECKED, NOT TRUSTED. ---
COST_LEGS="SETUP A0 A1 A2"
CAP_SETUP="5.0"
CAP_A0="100.0"
CAP_A1="70.0"
CAP_A2="115.0"
ITEM_CEILING_CORE_MIN="290.0"

# --- manifest legs and their registered windows (draft sec.3.1) ---
W_A0=2000        # the FRESH-ROOT REPEAT of the W3 anchor -- the FS-0 gating control
W_A1=1400        # brackets below the W*|g| peak
W_A2=2600        # brackets above it.  AMENDED 2026-09-04 from 3000, BEFORE FIRST COMPUTE
                 # (condition: the Arm A run root does not exist; checked).  W=3000's
                 # WORST-CASE wall is 7436 s -- 236 s OUTSIDE the 7200 s stage bound, not
                 # inside it.  The draft's "18.6 % worst residual" is
                 # (model-measured)/measured; a timeout needs (measured-model)/model,
                 # which is +22.91 %.  At W=2600 the worst-case wall is 6431 s, 12.0 %
                 # inside the bound.  The gscan span narrows 1400-3000 (2.14x) to
                 # 1400-2600 (1.86x) and that is a real, stated cost.

# --- inherited unchanged from W3_PREREGISTRATION.md sec.0 and sec.5 ---
DELTAT="1e-2"
TRANSIENT_DISCARD=300
NSHAPES_EXPECTED=4
MEMAVAIL_FLOOR_GIB="14.0"        # NOT LOWERED
MEM_LIMIT="8g"
CPUSET_CPUS="${CPUSET_CPUS:-1}"  # np=1, numberOfSubdomains=1
STAGE_TMO_S=7200                 # the inherited per-stage wall bound
S0_TMO_S=900                     # the inherited mesh-stage bound

# --- LANE-PROPOSED, NOT YET REGISTERED ANYWHERE.  See the header's flagged block. ---
MEMAVAIL_POLL_S=30
MEMAVAIL_WAIT_BOUND_S=3600

STAMP="$(date -u +%Y%m%dT%H%M%SZ)_$$"

# =============================================================================
say()  { echo "${ITEM}_LAUNCHER $*"; }
note() { echo "${ITEM}_LAUNCHER $*" | tee -a "$LEDGER" >/dev/null 2>&1 || true; \
         echo "${ITEM}_LAUNCHER $*"; }

usage() {
  echo "usage: $0 --leg {SETUP|A0|A1|A2} [--root PATH] [--guards-only]" >&2
  echo "       $0 --selftest [--tmpdir DIR]" >&2
  echo "       $0 --producer-trace" >&2
  exit 64
}

leg_cap() {
  case "$1" in
    SETUP) echo "$CAP_SETUP" ;;
    A0)    echo "$CAP_A0" ;;
    A1)    echo "$CAP_A1" ;;
    A2)    echo "$CAP_A2" ;;
    *)     echo "" ;;
  esac
}

leg_window() {
  case "$1" in
    SETUP|A0) echo "$W_A0" ;;
    A1)       echo "$W_A1" ;;
    A2)       echo "$W_A2" ;;
    *)        echo "" ;;
  esac
}

declared_stages() {
  case "$1" in
    SETUP)   echo "S0 S1a S1b S2a" ;;
    A0|A1|A2) echo "S5" ;;
    *)       echo "" ;;
  esac
}

memavail_gib() {
  awk '/^MemAvailable:/ {printf "%.4f", $2/1048576}' /proc/meminfo
}

# =============================================================================
# BAR-0 -- THE LAUNCHER MUST NOT BE ABLE TO ASK FOR A STEP PLAN
# =============================================================================
# Arm A drops terms from a MAXIMUM and therefore cannot legitimately size a step.  The
# comparator refuses a plan request at three depths; this is the fourth, on the asking
# side.  It reads THIS FILE'S OWN SOURCE, because a rule about what a file may contain is
# checkable only against the file.  The guard's own lines and the header prose are excluded
# by an anchored marker so the guard is not tripped by its own name.
#
# THE EXEMPTION IS NARROW, EXPLICIT AND COUNTED.  Comment lines are excluded (a rule about
# what a file may EXECUTE cannot be enforced against its own prose), and a line may carry
# the literal `BAR0_EXEMPT` with a stated reason.  There is EXACTLY ONE such line in this
# file -- the selftest's drive of the comparator's BAR-2 refusal, which REQUESTS a plan in
# order to WATCH IT BE REFUSED.  `bar0_exemption_count` is asserted to be 1 in
# `--selftest`, so a future edit that quietly adds a second exemption is caught.
bar0_no_step_plan_request() {
  local target="${1:-${BASH_SOURCE[0]}}"
  local hits
  hits="$(grep -n -e '--plan' "$target" 2>/dev/null `# BAR0_EXEMPT E1: the guard's own pattern` \
          | grep -v -E '^[0-9]+:[[:space:]]*#' \
          | grep -v 'BAR0_EXEMPT' || true)"
  if [ -n "$hits" ]; then
    echo "BLOCKED"
    return 0
  fi
  echo "PASS"
}

# THE FOUR EXEMPTIONS, ENUMERATED SO GROWTH IS VISIBLE.  `--selftest` asserts the count is
# exactly 4 and PRINTS the exempted lines, so a fifth cannot be added quietly.
#   E1  bar0_no_step_plan_request's own grep pattern
#   E2  this counter's own grep pattern
#   E3  the selftest's PLANTED POSITIVE fixture, which must contain a real request so the
#       guard can be shown REFUSING one
#   E4  the selftest's drive of the COMPARATOR's BAR-2 refusal -- it requests a plan in
#       order to watch the comparator refuse it, and never consumes one
bar0_exemption_count() {
  # `grep -c` PRINTS 0 AND EXITS 1 on no match, so `grep -c ... || echo 0` emits TWO
  # lines.  That is the same shape that made `finalize_leg`'s executed count `0\n0`, and
  # it is avoided here the same way: `wc -l`, which always prints a number and exits 0.
  local target="${1:-${BASH_SOURCE[0]}}"
  grep -E -e '--plan.*BAR0_EXEMPT' "$target" 2>/dev/null | wc -l | tr -d ' '
  # BAR0_EXEMPT E2: this counter's own pattern is on the grep line above
}

# THE W3 SHAPE, READ OUT OF THIS FILE'S OWN SOURCE.  `d12y_w3_stage_and_run.sh:362-365`
# `return 8`s on the memory floor and EVERY phase-1 call site is
# `run_stage ... || echo "STAGE X NONZERO rc"`, which CONSUMES the non-zero; the loop
# completes, `PHASE1_COMPLETE` prints and the launcher exits 0.  Nothing in the execution
# path ever reported a failure.  This reader finds that shape.  Comment lines are excluded
# and one line is exempt: the selftest's planted positive, which must contain the shape so
# the reader can be shown able to SEE it.
noblock_swallowed_rc_count() {
  local target="${1:-${BASH_SOURCE[0]}}"
  grep -n -E '\|\|[[:space:]]*echo[[:space:]]+"?STAGE' "$target" 2>/dev/null \
    | grep -v -E '^[0-9]+:[[:space:]]*#' \
    | grep -v 'NOBLOCK_EXEMPT' \
    | wc -l | tr -d ' '
}

# =============================================================================
# PREFLIGHT 0 -- THE FREEZE.  FIRST, AND UNCONDITIONAL.
# =============================================================================
preflight_freeze() {
  if [ -z "$PREREG_COMMIT" ]; then
    say "ABORT NOT_FROZEN: PREREG_COMMIT is empty. $(basename "$PREREG_FILE") carries no"
    say "  committed sha, so no gate, threshold, cap or label in it is frozen (CLAUDE.md"
    say "  rule 2). The pre-registration-committed-before-compute check is the"
    say "  supervisor's own and may not be delegated (SUPERVISION_CHARTER.md sec.3"
    say "  check 4). NOTHING LAUNCHES."
    return 70
  fi
  if ! git -C "$BASE" cat-file -e \
       "${PREREG_COMMIT}:cases/dafoam/curriculum_D12R2/$(basename "$PREREG_FILE")" \
       2>/dev/null; then
    say "ABORT FREEZE_UNVERIFIABLE: $PREREG_COMMIT does not carry the pre-registration blob."
    return 70
  fi
  return 0
}

# =============================================================================
# PREFLIGHT 1 -- INSTRUMENT IDENTITY.  EXISTENCE FIRST AND SEPARATELY, THEN md5.
# DAFOAM_CHARTER.md sec.18.3: an md5-agreement control over a subset can read agreement on
# every pin it holds while a dependency the frozen code EXECUTES is absent -- SO2a froze a
# memory gate whose implementing script was not in the freeze commit, and its own md5
# control still read `eight of eight AGREE`.
# =============================================================================
preflight_instruments() {
  local rc=0 f
  # (1) EXISTENCE, over EVERY file this launcher executes or imports, INCLUDING the ones
  #     that carry no md5 pin.  Asked first and asked separately.
  for f in "$RECORD" "$GRADER" "$PARENT_GRADER" "$PARENT_LAUNCHER" "$RUNPY" \
           "$CEILING_GUARD"; do
    if [ ! -f "$f" ]; then
      say "ABORT MISSING_INSTRUMENT $f -- a dependency this launcher EXECUTES is not on"
      say "  disk. Existence is asserted BEFORE any md5 (DAFOAM_CHARTER.md sec.18.3)."
      rc=4
    fi
  done
  [ "$rc" -eq 0 ] || return $rc
  # (2) ONLY THEN, the md5s.
  local pair want got
  for pair in "$GRADER:$MD5_GRADER" "$PARENT_GRADER:$MD5_PARENT_GRADER" \
              "$PARENT_LAUNCHER:$MD5_PARENT_LAUNCHER" "$RUNPY:$MD5_RUNPY" \
              "$RECORD:$MD5_RECORD"; do
    f="${pair%:*}"; want="${pair##*:}"
    if [ "$want" = "PIN_AT_FREEZE" ]; then
      say "PIN_UNSET $(basename "$f") md5=$(md5sum "$f" | cut -d' ' -f1) -- the pin is"
      say "  set in the FREEZE COMMIT, in the same commit as the file it pins. Until then"
      say "  PREFLIGHT 0 refuses and nothing reaches this line on a launch path."
      rc=4
      continue
    fi
    got="$(md5sum "$f" | cut -d' ' -f1)"
    if [ "$got" != "$want" ]; then
      say "ABORT MD5_DRIFT $(basename "$f") is $got, pinned $want"
      rc=4
    fi
  done
  return $rc
}

# =============================================================================
# PREFLIGHT 2 -- THE REGISTRATION SELF-CHECK.  A registration whose parts exceed its
# whole is a defect found here or not at all (draft sec.6.6).
# =============================================================================
preflight_registration() {
  local leg="$1" cap sum
  cap="$(leg_cap "$leg")"
  if [ -z "$cap" ]; then
    say "ABORT UNREGISTERED_LEG $leg -- the registered cost legs are $COST_LEGS"
    return 64
  fi
  # The sum is computed IN PYTHON and answered on an EXIT CODE.  No cap ever reaches a
  # shell arithmetic context (item_ceiling_guard.py defect (3): an empty $SPENT made
  # `( $SPENT + $ACAP )` Python's UNARY PLUS and a guard passed with real spend dropped).
  sum="$(python3 -c "
import sys
caps = {'SETUP': $CAP_SETUP, 'A0': $CAP_A0, 'A1': $CAP_A1, 'A2': $CAP_A2}
tot = sum(caps.values())
sys.stdout.write('%.6f' % tot)
sys.exit(0 if abs(tot - $ITEM_CEILING_CORE_MIN) < 1e-9 else 1)
")"
  if [ $? -ne 0 ]; then
    say "ABORT REGISTRATION_INCONSISTENT: the registered leg caps sum to $sum, not the"
    say "  registered item ceiling $ITEM_CEILING_CORE_MIN. A registration whose parts do"
    say "  not equal its whole is a defect found here or not at all."
    return 64
  fi
  # ---- RULING 3 (dafoam-supervisor, 2026-09-04): A REGISTERED CAP THAT EXCEEDS ITS OWN
  # ---- TIMEOUT REFUSES TO FREEZE.  `cap x 60 / ranks < wall_bound`, for EVERY leg.
  # ---- Called, not re-implemented: the arithmetic lives in the AST-audited producer where
  # ---- it is driven under python3 and python3 -O, and its planted control is THIS ITEM'S
  # ---- OWN WITHDRAWN A2 CAP -- 155.0 core-min = 9300 s against a 7200 s bound.
  python3 "$RECORD" --cap-reachability >/dev/null 2>&1
  if [ $? -ne 0 ]; then
    say "ABORT DEAD_LEVER: a registered cap exceeds the wall bound that guards the same"
    say "  work, so the timeout binds first and the cap can NEVER bind. It is a registered"
    say "  number no execution path can reach. Full census:"
    python3 "$RECORD" --cap-reachability
    return 64
  fi
  say "REGISTRATION OK leg=$leg cap=$cap; caps sum to $sum == ceiling $ITEM_CEILING_CORE_MIN;"
  say "  every cap is REACHABLE inside its own wall bound (cap x 60 / ranks < wall_bound)"
  return 0
}

# =============================================================================
# PREFLIGHT 3 -- THE LEDGER BOOTSTRAP, AND THE ONE PLACE `UNMEASURED` MUST BE PRESERVED
# =============================================================================
# `item_ceiling_guard.py` reads an ABSENT ledger as UNMEASURED and REFUSES, which is right
# and is the limb `d6rf` and `a1wrt` both lack.  Taken literally it also makes a FIRST leg
# unlaunchable forever, so this launcher creates the ledger before the census -- and that
# creation is ITSELF guarded, because writing an empty ledger into a root that already
# holds stage artefacts would convert real, unrecorded spend into a measured zero, which is
# precisely the planted zero the guard exists to refuse.
ledger_bootstrap() {
  local root="$1"
  local led="$root/ledger.txt"
  if [ -f "$led" ]; then
    return 0
  fi
  if [ -d "$root" ]; then
    local artefacts
    artefacts="$(ls -1 "$root" 2>/dev/null | grep -c -E '\.log$|^manifest\.jsonl$' || true)"
    if [ "${artefacts:-0}" != "0" ]; then
      say "ABORT UNMEASURED: $root holds $artefacts stage artefact(s) and NO ledger."
      say "  Spend that happened and was not recorded is UNMEASURED, not zero, and this"
      say "  launcher will not manufacture a zero by writing a fresh ledger over it."
      return 65
    fi
  fi
  mkdir -p "$root" || { say "ABORT could not create $root"; return 4; }
  {
    echo "ITEM=$ITEM ARM=$ARM"
    echo "PREREG=$(basename "$PREREG_FILE") PREREG_COMMIT=${PREREG_COMMIT:-UNFROZEN}"
    echo "IMAGE=$IMG_SHIPPED IMAGE_ID=$ID_SHIPPED ROW=shipped"
    echo "NP=1 numberOfSubdomains=1 deltaT=$DELTAT"
    echo "COST_LEGS=$COST_LEGS ITEM_CEILING_CORE_MIN=$ITEM_CEILING_CORE_MIN"
    echo "CAPS SETUP=$CAP_SETUP A0=$CAP_A0 A1=$CAP_A1 A2=$CAP_A2"
    echo "DECLARED_STAGES total=7 SETUP=4 A0=1 A1=1 A2=1"
    echo "STAMP=$STAMP STARTED_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "NOTE no bare W_STEPS= line is written: this root runs THREE windows and a"
    echo "NOTE single-window claim would be false. The per-leg W_STEPS_<LEG>= lines are"
    echo "NOTE the record, and w3s_grade reads exactly those."
  } >> "$led"
  say "LEDGER_BOOTSTRAPPED $led"
  return 0
}

# =============================================================================
# THE CUMULATIVE ITEM-CEILING GUARD.  CALLED, NEVER RE-IMPLEMENTED.
# The caller branches on the EXIT CODE AND NOTHING ELSE.  Its stdout is teed to the ledger
# as a durable record; it is never captured into a variable and re-tested arithmetically,
# because doing so re-creates the fail-open the guard was written against.
# =============================================================================
item_ceiling_guard() {
  local leg="$1" root="$2" cap rc
  cap="$(leg_cap "$leg")"
  python3 "$CEILING_GUARD" --check \
      --ledger "$root/ledger.txt" --cap "$cap" --ceiling "$ITEM_CEILING_CORE_MIN" \
      --row-prefix 'LEG=' --field 'core_min' --label "${ITEM}/${leg}" \
      2>&1 | tee -a "$root/ledger.txt"
  rc=${PIPESTATUS[0]}
  case "$rc" in
    0)  say "ITEM_CEILING leg=$leg WITHIN_CEILING" ;;
    65) say "ABORT ITEM_CEILING leg=$leg REFUSED -- either the projection clears the"
        say "  $ITEM_CEILING_CORE_MIN core-min ceiling or the prior spend is UNMEASURED."
        say "  An overrun STOPS the run; it does not get a new budget (CLAUDE.md rule 12)."
        say "  A zero that means 'could not read' is a planted zero and is never assumed."
        rc=6 ;;
    64) say "ABORT ITEM_CEILING leg=$leg USAGE -- the guard refused its own inputs"
        rc=64 ;;
    *)  say "ABORT ITEM_CEILING_GUARD_ITSELF_FAILED leg=$leg rc=$rc"
        rc=65 ;;
  esac
  return $rc
}

# =============================================================================
# THE MemAvailable FLOOR.  WAIT AND RE-POLL, BOUNDED, THEN TERMINATE.
# NEVER BLOCK-AND-CONTINUE.  This is DAFOAM_CHARTER.md sec.18.7 Requirement 3 and it is
# the whole W3 finding: the form of a guard must match the BEHAVIOUR of the quantity it
# watches, and live `MemAvailable` is the transient one.
# =============================================================================
memavail_wait_or_terminate() {
  local stage="$1" leg="$2" root="$3"
  local waited=0 ma
  while : ; do
    ma="$(memavail_gib)"
    if python3 -c "import sys; sys.exit(0 if $ma >= $MEMAVAIL_FLOOR_GIB else 1)"; then
      [ "$waited" -gt 0 ] && \
        echo "MEMAVAIL_CLEARED stage=$stage leg=$leg after ${waited}s at ${ma} GiB" \
          >> "$root/ledger.txt"
      echo "$ma"
      return 0
    fi
    if [ "$waited" -ge "$MEMAVAIL_WAIT_BOUND_S" ]; then
      echo "MEMAVAIL_BOUND_REACHED stage=$stage leg=$leg waited=${waited}s of ${MEMAVAIL_WAIT_BOUND_S}s memavail_GiB=${ma} floor=$MEMAVAIL_FLOOR_GIB" \
        >> "$root/ledger.txt"
      # A GUARD THAT REFUSES MUST LEAVE THE SAME TRACE IN BOTH ARTIFACTS (W2R-DEF-1).
      python3 "$RECORD" --emit-blocked-row --root "$root" --cost-leg "$leg" \
              --stage "$stage" --blocked-by "memavail_floor_bound" --memavail "$ma" \
              >/dev/null
      say "ABORT MEMAVAIL_BOUND leg=$leg stage=$stage -- ${ma} GiB stayed below the"
      say "  registered ${MEMAVAIL_FLOOR_GIB} GiB floor for the whole ${MEMAVAIL_WAIT_BOUND_S}s bound."
      say "  THE LEG TERMINATES rc=6. It does NOT continue to the next stage: a resource"
      say "  condition that cannot be waited out stops the item, it does not quietly buy"
      say "  a smaller one (DAFOAM_CHARTER.md sec.18.7 Requirement 3)."
      return 6
    fi
    echo "MEMAVAIL_WAIT stage=$stage leg=$leg waited=${waited}s of ${MEMAVAIL_WAIT_BOUND_S}s memavail_GiB=${ma} floor=$MEMAVAIL_FLOOR_GIB" \
      >> "$root/ledger.txt"
    sleep "$MEMAVAIL_POLL_S"
    waited=$((waited + MEMAVAIL_POLL_S))
  done
}

# =============================================================================
# THE STAGE TIMEOUT.  The registered leg cap, turned into a process that executes it.
# The value is validated WHOLE before it reaches a command line; it never enters a shell
# arithmetic context.
# =============================================================================
stage_timeout_for() {
  local leg="$1" root="$2" bound="$3" out rc
  out="$(python3 "$RECORD" --stage-timeout --root "$root" --cost-leg "$leg" \
         --bound-s "$bound" 2>/dev/null)"
  rc=$?
  if [ "$rc" -ne 0 ]; then
    return 6
  fi
  case "$out" in
    ''|*[!0-9]*) return 6 ;;
  esac
  echo "$out"
  return 0
}

# =============================================================================
# THE LEG FINALIZER.  The `LEG=` spend row is written on EVERY exit path, including a
# failing one, so a leg that dies mid-flight leaves its spend MEASURED rather than
# UNMEASURED -- and so the next leg's prospective ceiling census can see it.
# =============================================================================
finalize_leg() {
  local leg="$1" root="$2" rc="$3"
  local declared executed blocked spent wall vj counts
  declared="$(declared_stages "$leg" | wc -w)"
  # ONE call, captured to a file, THEN parsed.  The first draft of this function piped
  # `--verify-leg` into a parser under `set -o pipefail` with an `|| echo 0` fallback: the
  # pipeline inherited the verifier's rc=6, the fallback fired ON TOP of a parser that had
  # already printed, and `executed` came back as the two-line string `0\n0`.  Found by
  # this file's own selftest, and recorded rather than quietly repaired -- it is the same
  # class as `item_ceiling_guard.py` defect (3): a number that reached a context able to
  # mangle it.
  vj="$(mktemp)"
  python3 "$RECORD" --verify-leg --root "$root" --cost-leg "$leg" > "$vj" 2>/dev/null
  counts="$(python3 -c "
import json, sys
try:
    d = json.load(open('$vj'))
    sys.stdout.write('%d %d' % (d['executed_count'], d['blocked_count']))
except Exception:
    sys.stdout.write('UNMEASURED UNMEASURED')
")"
  rm -f "$vj"
  executed="${counts%% *}"
  blocked="${counts##* }"
  spent="$(python3 -c "
import sys, os
sys.path.insert(0, '$BASE')
import importlib.util
spec = importlib.util.spec_from_file_location('rec', '$RECORD')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
v, note = m.leg_spent_from_disk('$root', '$leg')
sys.stdout.write('UNMEASURED' if v is None else repr(v))
")"
  if [ "$spent" = "UNMEASURED" ]; then
    say "LEG_FINALIZE leg=$leg SPEND UNMEASURED -- no LEG= row is written, because a"
    say "  fabricated number is worse than an absent one and the next leg's ceiling"
    say "  census must see UNMEASURED and refuse."
    return 65
  fi
  case "$executed" in ''|*[!0-9]*) executed="UNMEASURED" ;; esac
  case "$blocked"  in ''|*[!0-9]*) blocked="UNMEASURED"  ;; esac
  if [ "$executed" = "UNMEASURED" ] || [ "$blocked" = "UNMEASURED" ]; then
    say "LEG_FINALIZE leg=$leg COUNTS UNMEASURED -- the verifier's output could not be"
    say "  read, so neither the executed nor the blocked count is known and no LEG= row"
    say "  is written. A count that means 'could not read' is a planted zero."
    return 65
  fi
  wall="$(python3 -c "print(int(round($spent*60)))")"
  python3 "$RECORD" --leg-spend-line --cost-leg "$leg" --rc "$rc" --wall-s "$wall" \
          --core-min "$spent" --declared "$declared" --executed "$executed" \
          --blocked "$blocked" >> "$root/ledger.txt" || return 65
  # DAFOAM_CHARTER.md sec.18.7 Requirement 4: BOTH counts, and NO success-reading token
  # over a program that did not complete.
  if [ "$rc" -eq 0 ] && [ "$executed" = "$declared" ] && [ "$blocked" = "0" ]; then
    say "LEG_COMPLETE leg=$leg declared=$declared executed=$executed blocked=$blocked spent=$spent core-min"
  else
    say "LEG_NOT_A_RESULT leg=$leg declared=$declared executed=$executed blocked=$blocked rc=$rc spent=$spent core-min"
    say "  A run whose executed count is below its declared count is NEVER reported by a"
    say "  token that reads as success (DAFOAM_CHARTER.md sec.18.7 Requirement 4). W3"
    say "  printed PHASE1_COMPLETE after blocking 20 of 33 declared stages and exited 0."
  fi
  return 0
}

# =============================================================================
# --selftest : every guard driven in BOTH directions, on host shell, ZERO COMPUTE.
# Every control prints EXERCISED-PASS / EXERCISED-FAIL / NOT EXERCISED, and NOT EXERCISED
# is never counted as a pass and never inferred from the absence of a failure.
# =============================================================================
N_PASS=0; N_FAIL=0; N_NOT=0
ctl() {  # name state detail
  printf 'EXERCISED-%-40s %-14s %s\n' "$1" "$2" "${3:-}"
  case "$2" in
    EXERCISED-PASS) N_PASS=$((N_PASS+1)) ;;
    EXERCISED-FAIL) N_FAIL=$((N_FAIL+1)) ;;
    *)              N_NOT=$((N_NOT+1)) ;;
  esac
}
expect_rc() {  # name want cmd...
  local name="$1" want="$2"; shift 2
  local rc
  "$@" >/dev/null 2>&1; rc=$?
  if [ "$rc" = "$want" ]; then
    ctl "$name" "EXERCISED-PASS" "rc=$rc (expected $want)"
  else
    ctl "$name" "EXERCISED-FAIL" "rc=$rc, expected $want"
  fi
}
expect_rc_and_text() {  # name want_rc want_text cmd...
  # THE RC ALONE IS NOT THE CONTROL.  Two different defects can both refuse at rc=4, and a
  # control that cannot tell them apart is measuring the presence of a refusal, not the
  # reason for one.
  local name="$1" want="$2" text="$3"; shift 3
  local out rc
  out="$("$@" 2>&1)"; rc=$?
  if [ "$rc" = "$want" ] && printf '%s' "$out" | grep -q -- "$text"; then
    ctl "$name" "EXERCISED-PASS" "rc=$rc and the refusal names $text"
  else
    ctl "$name" "EXERCISED-FAIL" "rc=$rc (want $want), refusal did not name $text"
  fi
}
expect_out() {  # name want cmd...
  local name="$1" want="$2"; shift 2
  local out
  out="$("$@" 2>/dev/null)"
  if [ "$out" = "$want" ]; then
    ctl "$name" "EXERCISED-PASS" "observed=$out expected=$want"
  else
    ctl "$name" "EXERCISED-FAIL" "observed=$out expected=$want"
  fi
}

selftest() {
  TD="$(mktemp -d)"
  trap 'rm -rf "${TD:-}"' EXIT
  echo "${ITEM}_LAUNCHER SELFTEST -- host shell, NO container, NO compute, LAUNCH_ENABLED=$LAUNCH_ENABLED"
  echo "------------------------------------------------------------------------------"

  # ---- 1. the freeze and the pins, BOTH DIRECTIONS.  The negative direction is driven
  # ---- against MUTATED COPIES of this file, because a pin control that can only ever
  # ---- pass is a pin control nobody has shown to be one.
  # THE CONTROL THAT USED TO STAND HERE READ THE LIVE `PREREG_COMMIT` AND REQUIRED IT
  # EMPTY (`FREEZE-refuses-while-PREREG_COMMIT-empty`, rc=70).  The supervisor's B3 fill --
  # this launcher's OWN freeze field, distinct from the driver's -- REMOVED ITS PREMISE, so
  # it is replaced rather than left standing on a condition that can no longer occur: a
  # control whose premise is gone is a control that cannot fail, and a green from one means
  # nothing.  THIS IS THE THIRD CONTROL IN THIS ITEM KILLED BY THE SAME ACT CLASS, and the
  # general finding is recorded in `w3s_CONTROL_REPLANT_2026-09-06.diff`: EVERY LIVE-READING
  # CONTROL IN A PRE-FREEZE ITEM IS A CONTROL THE FREEZE ITSELF DESTROYS.
  #
  # THE REASON TOKEN IS CHECKED, NOT THE RC.  Both refusals return 70, and a control that
  # cannot tell NOT_FROZEN from FREEZE_UNVERIFIABLE is measuring the presence of a refusal
  # rather than the reason for one -- the same repair the two pin controls below carry.
  sed 's|^PREREG_COMMIT=.*|PREREG_COMMIT=""|' \
      "${BASH_SOURCE[0]}" > "$TD/freeze_empty.sh"
  expect_rc_and_text "FREEZE-PLANT-an-EMPTY-PREREG_COMMIT-REFUSES-with-NOT_FROZEN" 70 \
    "NOT_FROZEN" \
    env W3S_BASE="$BASE" bash "$TD/freeze_empty.sh" --freeze-only
  sed 's|^PREREG_COMMIT=.*|PREREG_COMMIT="0000000000000000000000000000000000000000"|' \
      "${BASH_SOURCE[0]}" > "$TD/freeze_bogus.sh"
  expect_rc_and_text "FREEZE-PLANT-a-sha-with-no-prereg-blob-REFUSES-with-FREEZE_UNVERIFIABLE" \
    70 "FREEZE_UNVERIFIABLE" \
    env W3S_BASE="$BASE" bash "$TD/freeze_bogus.sh" --freeze-only
  # ---- AND THE POSITIVE DIRECTION, which the old control could never have had, because it
  # ---- required the opposite: the LIVE sha must actually carry the pre-registration blob.
  expect_rc "FREEZE-the-LIVE-sha-carries-the-pre-registration-blob" 0 preflight_freeze
  expect_rc "PINS-agree-on-disk-today" 0 preflight_instruments
  # THE TWO PIN DIRECTIONS MUST REFUSE FOR TWO DIFFERENT REASONS, and the reason is
  # checked, not the rc alone.  The first draft of these two controls both passed at rc=4
  # -- and BOTH were failing on MISSING_INSTRUMENT, because the mutated copies resolved
  # their instrument paths into the temp directory.  The md5-drift limb was never driven
  # and its green meant nothing.  `W3S_BASE` and the reason token are the repair.
  sed 's|^MD5_GRADER=.*|MD5_GRADER="00000000000000000000000000000000"|' \
      "${BASH_SOURCE[0]}" > "$TD/pins_drift.sh"
  expect_rc_and_text "PINS-PLANT-a-drifted-md5-REFUSES-with-MD5_DRIFT" 4 "MD5_DRIFT" \
    env W3S_BASE="$BASE" bash "$TD/pins_drift.sh" --pins-only-loud
  sed 's|^RECORD="\$BASE/w3s_stage_record.py"|RECORD="$BASE/no_such_producer.py"|' \
      "${BASH_SOURCE[0]}" > "$TD/pins_absent.sh"
  expect_rc_and_text "PINS-PLANT-an-ABSENT-file-REFUSES-with-MISSING_INSTRUMENT" 4 \
    "MISSING_INSTRUMENT" \
    env W3S_BASE="$BASE" bash "$TD/pins_absent.sh" --pins-only-loud
  expect_rc "PINS-this-file-unmutated-PASSES-pins-only" 0 \
    bash "${BASH_SOURCE[0]}" --pins-only
  local n_exec
  n_exec="$(grep -c -E '^\s+for f in "\$RECORD"' "${BASH_SOURCE[0]}" || true)"
  if [ "$n_exec" = "1" ]; then
    ctl "PINS-existence-loop-runs-BEFORE-the-md5-loop" "EXERCISED-PASS" \
        "one existence loop, ahead of the md5 loop (DAFOAM_CHARTER sec.18.3)"
  else
    ctl "PINS-existence-loop-runs-BEFORE-the-md5-loop" "EXERCISED-FAIL" \
        "found $n_exec existence loops"
  fi

  # ---- 2. BAR-0, BOTH DIRECTIONS
  expect_out "BAR0-this-launcher-may-not-ask-for-a-plan" "PASS" \
    bar0_no_step_plan_request "${BASH_SOURCE[0]}"
  printf '#!/bin/bash\npython3 grade.py --plan --manifest m.jsonl\n' > "$TD/bar0_positive.sh"  # BAR0_EXEMPT E3: the planted positive MUST carry a real request or the guard is never shown refusing one
  expect_out "BAR0-PLANT-a-launcher-that-asks-is-BLOCKED" "BLOCKED" \
    bar0_no_step_plan_request "$TD/bar0_positive.sh"
  printf '#!/bin/bash\npython3 grade.py --gscan --manifest m.jsonl\n' > "$TD/bar0_negative.sh"
  expect_out "BAR0-a-gscan-only-launcher-PASSES" "PASS" \
    bar0_no_step_plan_request "$TD/bar0_negative.sh"
  expect_out "BAR0-EXACTLY-4-enumerated-exemptions-E1-E4" "4" \
    bar0_exemption_count "${BASH_SOURCE[0]}"

  # ---- 3. NO BLOCK-AND-CONTINUE ANYWHERE IN THIS FILE.  The W3 shape, read out of the
  # ---- source: a guard's non-zero return consumed by `|| echo`.
  expect_out "NOBLOCK-this-file-carries-0-swallowed-stage-rcs" "0" \
    noblock_swallowed_rc_count "${BASH_SOURCE[0]}"
  printf '%s\n' 'run_stage S5 || echo "STAGE S5 NONZERO rc"' > "$TD/swallow_positive.sh"  # NOBLOCK_EXEMPT: the planted positive MUST carry the shape or the reader's zero is not evidence
  expect_out "NOBLOCK-PLANT-the-reader-CAN-see-the-W3-shape" "1" \
    noblock_swallowed_rc_count "$TD/swallow_positive.sh"
  # MEASURED against the md5-pinned parent: `d12y_w3_stage_and_run.sh` carries the
  # swallowing shape on 14 EXECUTABLE lines.  That is the W3 defect in situ, and it is
  # what makes this reader's 0 above evidence rather than an absence.
  expect_out "NOBLOCK-the-PARENT-launcher-carries-the-shape-14-times" "14" \
    noblock_swallowed_rc_count "$PARENT_LAUNCHER"

  # ---- 4. the registration self-check
  expect_rc "REG-caps-sum-EXACTLY-to-the-ceiling" 0 preflight_registration A0
  expect_rc "REG-an-unregistered-leg-refuses-rc64" 64 preflight_registration A9
  expect_rc "REG-every-registered-cap-is-REACHABLE-inside-its-wall-bound" 0 \
    python3 "$RECORD" --cap-reachability
  expect_out "REG-A2s-new-cap-6900s-is-inside-the-7200s-bound" "True" \
    python3 -c "
import importlib.util, json, subprocess, sys
out = subprocess.run([sys.executable, '$RECORD', '--cap-reachability'],
                     capture_output=True, text=True).stdout
b = json.loads(out)
print([r for r in b['legs'] if r['leg'] == 'A2'][0]['reachable'])
"

  # ---- 5. the ledger bootstrap, and the UNMEASURED direction it must preserve
  expect_rc "BOOTSTRAP-a-fresh-root-gets-a-ledger" 0 ledger_bootstrap "$TD/fresh"
  if [ -f "$TD/fresh/ledger.txt" ]; then
    ctl "BOOTSTRAP-the-ledger-is-actually-on-disk" "EXERCISED-PASS" "$TD/fresh/ledger.txt"
  else
    ctl "BOOTSTRAP-the-ledger-is-actually-on-disk" "EXERCISED-FAIL" "no ledger written"
  fi
  if grep -q '^NOTE no bare W_STEPS= line is written' "$TD/fresh/ledger.txt" 2>/dev/null; then
    ctl "BOOTSTRAP-no-bare-W_STEPS-claim-in-a-3-window-root" "EXERCISED-PASS" \
        "the single-window claim is refused in writing"
  else
    ctl "BOOTSTRAP-no-bare-W_STEPS-claim-in-a-3-window-root" "EXERCISED-FAIL" "note absent"
  fi
  mkdir -p "$TD/orphan"; : > "$TD/orphan/S5_x.log"
  expect_rc "BOOTSTRAP-REFUSES-to-zero-a-root-with-orphan-logs" 65 \
    ledger_bootstrap "$TD/orphan"

  # ---- 6. the cumulative item-ceiling guard, through the COMMITTED _common instrument
  expect_rc "CEILING-a-bootstrapped-fresh-root-is-a-real-zero" 0 \
    item_ceiling_guard SETUP "$TD/fresh"
  mkdir -p "$TD/over"
  {
    echo "ITEM=$ITEM"
    python3 "$RECORD" --leg-spend-line --cost-leg A0 --rc 0 --wall-s 12000 \
            --core-min 200.0 --declared 1 --executed 1 --blocked 0
  } > "$TD/over/ledger.txt"
  expect_rc "CEILING-200.0-plus-A2s-115.0-cap-exceeds-290.0" 6 \
    item_ceiling_guard A2 "$TD/over"
  mkdir -p "$TD/malformed"
  echo "LEG=A0 rc=0 core_min=1.2.3" > "$TD/malformed/ledger.txt"
  expect_rc "CEILING-a-malformed-core_min-is-UNMEASURED-not-1.2" 6 \
    item_ceiling_guard A0 "$TD/malformed"
  mkdir -p "$TD/under"
  {
    echo "ITEM=$ITEM"
    python3 "$RECORD" --leg-spend-line --cost-leg SETUP --rc 0 --wall-s 105 \
            --core-min 1.75 --declared 4 --executed 4 --blocked 0
  } > "$TD/under/ledger.txt"
  expect_rc "CEILING-1.75-plus-A0s-100.0-cap-is-WITHIN" 0 \
    item_ceiling_guard A0 "$TD/under"
  expect_rc "CEILING-an-ABSENT-ledger-REFUSES-it-is-not-a-zero" 6 \
    item_ceiling_guard A0 "$TD/never_made"

  # ---- 6b. TWO CEILING READERS SEE THIS LEDGER, AND THEY MUST AGREE.
  # `w3s_chain_driver.sh` asserts the ceiling with `w3s_grade.py
  # --cumulative-item-ceiling`; this launcher asserts it with the committed
  # `_common/item_ceiling_guard.py`.  They are DIFFERENT INSTRUMENTS with different
  # readers, and a ledger format that satisfies one and not the other would give the item
  # two answers about its own budget.  So both are driven over the SAME files here, and
  # the one place their designs differ -- an ABSENT ledger, which the `_common` guard
  # calls UNMEASURED and the grader calls FRESH -- is driven explicitly rather than left
  # to be discovered.  The teed `ITEM_CEILING ...` lines the `_common` guard writes into
  # the ledger carry `spent_core_min=` / `cap_core_min=` / `proj_core_min=`, none of which
  # has a word boundary before `core_min`, so NEITHER reader counts them as spend.  That
  # is checked here, not assumed.
  expect_rc "XGUARD-the-graders-ceiling-reads-our-LEG-rows-too" 0 \
    python3 "$GRADER" --cumulative-item-ceiling --leg A0 --root "$TD/under" \
            --tmpdir "$TD"
  expect_rc "XGUARD-the-graders-ceiling-REFUSES-the-same-overrun" 6 \
    python3 "$GRADER" --cumulative-item-ceiling --leg A2 --root "$TD/over" --tmpdir "$TD"
  expect_rc "XGUARD-the-graders-ceiling-REFUSES-the-same-malformed-token" 65 \
    python3 "$GRADER" --cumulative-item-ceiling --leg A0 --root "$TD/malformed" \
            --tmpdir "$TD"
  expect_rc "XGUARD-a-teed-ITEM_CEILING-line-is-NOT-counted-as-spend" 0 \
    python3 "$GRADER" --cumulative-item-ceiling --leg A0 --root "$TD/fresh" \
            --tmpdir "$TD"
  mkdir -p "$TD/orphan2"; : > "$TD/orphan2/S5_x.log"
  expect_rc "XGUARD-both-readers-REFUSE-a-root-with-orphan-logs-and-no-ledger" 65 \
    python3 "$GRADER" --cumulative-item-ceiling --leg A0 --root "$TD/orphan2" \
            --tmpdir "$TD"

  # ---- 7. the in-leg budget -> timeout converter
  # Ruling 3's consequence: every cap is now REACHABLE, so the CAP binds first on a fresh
  # leg and the 7200 s stage bound is a backstop.  A2's 115.0 core-min = 6900 s.
  expect_out "BUDGET-a-fresh-A2-leg-is-CAP-bound-at-6900s" "6900" \
    stage_timeout_for A2 "$TD/fresh" "$STAGE_TMO_S"
  expect_out "BUDGET-the-wall-bound-STILL-wins-when-it-is-smaller" "1000" \
    stage_timeout_for A2 "$TD/fresh" 1000
  mkdir -p "$TD/thin"
  {
    echo "ITEM=$ITEM"
    python3 "$RECORD" --stage-detail-line --stage S5 --cost-leg A2 --rc 0 \
            --wall-s 6600 --core-min 110.0 --memavail 20.0 --log x.log
  } > "$TD/thin/ledger.txt"
  expect_out "BUDGET-a-thin-remainder-SHORTENS-the-timeout-to-300s" "300" \
    stage_timeout_for A2 "$TD/thin" "$STAGE_TMO_S"
  mkdir -p "$TD/spent"
  {
    echo "ITEM=$ITEM"
    python3 "$RECORD" --stage-detail-line --stage S5 --cost-leg A2 --rc 0 \
            --wall-s 6900 --core-min 115.0 --memavail 20.0 --log x.log
  } > "$TD/spent/ledger.txt"
  expect_rc "BUDGET-an-exhausted-leg-REFUSES-rc6-no-new-budget" 6 \
    stage_timeout_for A2 "$TD/spent" "$STAGE_TMO_S"

  # ---- 8. THE PRODUCER TRACE.  Every artefact key the frozen comparator reads must have
  # ---- a producer in the registered set.
  expect_rc "TRACE-every-consumed-key-has-a-producer" 0 \
    python3 "$RECORD" --producer-trace
  expect_rc "TRACE-the-record-producer-carries-0-ast.Assert" 0 \
    python3 "$RECORD" --assert-audit
  expect_rc "TRACE-the-record-producer-carries-0-ast.Assert-under--O" 0 \
    python3 -O "$RECORD" --assert-audit
  expect_rc "TRACE-the-comparator-carries-0-ast.Assert" 0 \
    python3 "$GRADER" --assert-audit
  expect_rc "TRACE-the-comparator-still-imports-the-FROZEN-parent" 0 \
    python3 "$GRADER" --parent-check

  # ---- 9. THE PER-LEG RULE-4 ASSERTION, over a fixture this launcher's own producer made
  local FX
  FX="$(python3 "$RECORD" --fixture --dir "$TD/fx" --fs0 hit --fs1 miss \
        | python3 -c "import json,sys; print(json.load(sys.stdin)['root'])")"
  expect_rc "RULE4-SETUP-leg-passes-the-FROZEN-parents-own-gate" 0 \
    python3 "$RECORD" --verify-leg --root "$FX" --cost-leg SETUP
  expect_rc "RULE4-A0-leg-passes" 0 python3 "$RECORD" --verify-leg --root "$FX" --cost-leg A0
  expect_rc "RULE4-A2-leg-passes" 0 python3 "$RECORD" --verify-leg --root "$FX" --cost-leg A2
  expect_rc "RULE4-the-FROZEN-comparator-GRADES-this-manifest" 0 \
    python3 "$GRADER" --gscan --manifest "$FX/manifest.jsonl" --root "$FX" --tmpdir "$TD"
  expect_rc "RULE4-BAR-2-refuses-a-plan-request-on-this-manifest" 2 \
    python3 "$GRADER" --plan2 --manifest "$FX/manifest.jsonl" --root "$FX"  # BAR0_EXEMPT E4: REQUESTS a plan in order to WATCH THE COMPARATOR REFUSE IT; never consumes one

  # ---- 10. the leg finalizer: both counts, and no success token over a truncation
  local OUT
  OUT="$(finalize_leg SETUP "$FX" 0 2>&1)"
  case "$OUT" in
    *LEG_COMPLETE*declared=4*executed=4*)
      ctl "FINALIZE-a-complete-leg-reports-BOTH-counts" "EXERCISED-PASS" \
          "declared=4 executed=4" ;;
    *) ctl "FINALIZE-a-complete-leg-reports-BOTH-counts" "EXERCISED-FAIL" "$OUT" ;;
  esac
  local FXT
  FXT="$(python3 - "$RECORD" "$TD/fxt" <<'PYX'
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("rec", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print(m.build_fixture(sys.argv[2], fs0="hit", fs1="miss",
                      blocked_stage=("S5", "A2"))["root"])
PYX
)"
  OUT="$(finalize_leg A2 "$FXT" 6 2>&1)"
  case "$OUT" in
    *LEG_NOT_A_RESULT*declared=1*executed=0*blocked=1*)
      ctl "FINALIZE-a-truncated-leg-NEVER-says-COMPLETE" "EXERCISED-PASS" \
          "declared=1 executed=0 blocked=1, token is LEG_NOT_A_RESULT" ;;
    *) ctl "FINALIZE-a-truncated-leg-NEVER-says-COMPLETE" "EXERCISED-FAIL" "$OUT" ;;
  esac
  case "$OUT" in
    *LEG_COMPLETE*) ctl "FINALIZE-no-success-token-on-a-truncated-leg" "EXERCISED-FAIL" \
                        "a COMPLETE token appeared over a truncated program" ;;
    *) ctl "FINALIZE-no-success-token-on-a-truncated-leg" "EXERCISED-PASS" \
           "the W3 PHASE1_COMPLETE shape is absent" ;;
  esac
  expect_rc "FINALIZE-the-blocked-leg-is-rc6-at-verify-leg" 6 \
    python3 "$RECORD" --verify-leg --root "$FXT" --cost-leg A2

  # ---- 11. THE LAUNCH GATE, BOTH DIRECTIONS, PLANTED.
  # THE CONTROL THAT USED TO STAND HERE READ THE LIVE `LAUNCH_ENABLED` AND REQUIRED IT 0.
  # The supervisor's enqueue raised it to 1, which REMOVED ITS PREMISE, so it is replaced
  # rather than left standing on a condition that can no longer occur -- a control whose
  # premise is gone is a control that cannot fail, and a green from one means nothing.
  # (Same reasoning, same words, as the driver applied to its own PREFLIGHT-1 control.)
  #
  # The replacement PLANTS the flag into MUTATED COPIES of this file and drives the gate in
  # BOTH directions, exactly as the two pin controls above are driven, so it fires BEFORE
  # AND AFTER an enqueue and never reads the live value.
  #
  # THE COPIES ALSO CARRY A PLANTED FREEZE SHA -- `HEAD` at test time, a FIXTURE and not a
  # freeze record -- because PREFLIGHT 0 sits AHEAD of the launch gate and would otherwise
  # refuse first.  A control that stops at an earlier guard has not driven the one it names;
  # that is the same defect the two pin controls above were repaired for.
  #
  # NEITHER DIRECTION CAN REACH A CONTAINER, and that is a property of the fixture rather
  # than an assumption: the root is a FRESH temp dir, so the A-leg body's first act is the
  # `FIELD_B is absent` refusal at rc=4, which sits BEFORE every `docker run` in this file.
  # That refusal is therefore the DISCRIMINATOR -- it appears when the gate lets through and
  # is absent when the gate refuses, and the ONLY difference between the two copies is the
  # one flag.
  local HEADSHA GATE_OUT
  HEADSHA="$(git -C "$BASE" rev-parse HEAD 2>/dev/null || echo NONE)"
  sed -e 's|^LAUNCH_ENABLED=.*|LAUNCH_ENABLED=0|' \
      -e "s|^PREREG_COMMIT=.*|PREREG_COMMIT=\"$HEADSHA\"|" \
      "${BASH_SOURCE[0]}" > "$TD/gate_off.sh"
  GATE_OUT="$(env W3S_BASE="$BASE" bash "$TD/gate_off.sh" --leg A0 --root "$TD/gate_off_root" 2>&1)"
  rc=$?
  if [ "$rc" = "0" ] \
     && printf '%s' "$GATE_OUT" | grep -q "NOT_LAUNCHING" \
     && ! printf '%s' "$GATE_OUT" | grep -q "FIELD_B is absent"; then
    ctl "LAUNCH-GATE-PLANT-0-REFUSES-before-the-leg-body" "EXERCISED-PASS" \
        "rc=0, NOT_LAUNCHING printed, leg body never entered"
  else
    ctl "LAUNCH-GATE-PLANT-0-REFUSES-before-the-leg-body" "EXERCISED-FAIL" \
        "rc=$rc, NOT_LAUNCHING/leg-body discrimination failed"
  fi
  sed -e 's|^LAUNCH_ENABLED=.*|LAUNCH_ENABLED=1|' \
      -e "s|^PREREG_COMMIT=.*|PREREG_COMMIT=\"$HEADSHA\"|" \
      "${BASH_SOURCE[0]}" > "$TD/gate_on.sh"
  GATE_OUT="$(env W3S_BASE="$BASE" bash "$TD/gate_on.sh" --leg A0 --root "$TD/gate_on_root" 2>&1)"
  rc=$?
  if [ "$rc" = "4" ] \
     && ! printf '%s' "$GATE_OUT" | grep -q "NOT_LAUNCHING" \
     && printf '%s' "$GATE_OUT" | grep -q "FIELD_B is absent"; then
    ctl "LAUNCH-GATE-PLANT-1-LETS-THROUGH-into-the-leg-body" "EXERCISED-PASS" \
        "rc=4 at the FIELD_B refusal, which is BEFORE every docker run: the gate is live, not dead code"
  else
    ctl "LAUNCH-GATE-PLANT-1-LETS-THROUGH-into-the-leg-body" "EXERCISED-FAIL" \
        "rc=$rc, the gate did not let a planted 1 through to the leg body"
  fi

  echo "------------------------------------------------------------------------------"
  echo "${ITEM}_LAUNCHER SELFTEST controls=$((N_PASS+N_FAIL+N_NOT)) EXERCISED-PASS=$N_PASS EXERCISED-FAIL=$N_FAIL NOT-EXERCISED=$N_NOT"
  if [ "$N_FAIL" -ne 0 ] || [ "$N_NOT" -ne 0 ] || [ "$N_PASS" -eq 0 ]; then
    echo "${ITEM}_LAUNCHER SELFTEST REFUSED -- NOT EXERCISED is never a pass and is never"
    echo "  inferred from the absence of a failure."
    return 1
  fi
  echo "${ITEM}_LAUNCHER SELFTEST PASS $N_PASS/$N_PASS"
  return 0
}

# =============================================================================
# ARGUMENTS
# =============================================================================
LEG=""
ROOT="$ROOT_DEFAULT"
SELFTEST=0
GUARDS_ONLY=0
PINS_ONLY=0
FREEZE_ONLY=0
TRACE=0
TD=""
TMPDIR_ARG="${TMPDIR:-/tmp}"
while [ $# -gt 0 ]; do
  case "$1" in
    --leg)            LEG="${2:-}"; shift 2 ;;
    --root)           ROOT="${2:-}"; shift 2 ;;
    --selftest)       SELFTEST=1; shift ;;
    --guards-only)    GUARDS_ONLY=1; shift ;;
    --pins-only)      PINS_ONLY=1; shift ;;
    --pins-only-loud) PINS_ONLY=2; shift ;;
    --freeze-only)    FREEZE_ONLY=1; shift ;;
    --producer-trace) TRACE=1; shift ;;
    --tmpdir)         TMPDIR_ARG="${2:-}"; shift 2 ;;
    *)                usage ;;
  esac
done
LEDGER="$ROOT/ledger.txt"
MANIFEST="$ROOT/manifest.jsonl"

if [ "$TRACE" = "1" ]; then
  exec python3 "$RECORD" --producer-trace
fi
if [ "$FREEZE_ONLY" = "1" ]; then
  # PREFLIGHT 0 ALONE, so the planted freeze controls can be driven against MUTATED COPIES
  # of this file WITHOUT PREFLIGHT 1's md5s refusing first -- a mutated copy has, by
  # construction, a different md5 than anything pinned, and a control that refuses for the
  # WRONG REASON is not a control.  It launches nothing: no path from here reaches a leg.
  preflight_freeze; exit $?
fi
if [ "$PINS_ONLY" != "0" ]; then
  # PREFLIGHT 1 alone, so the pin controls can be driven in BOTH directions against
  # mutated copies of this file WITHOUT PREFLIGHT 0 refusing first.  It launches nothing
  # and it does not bypass the freeze: no path from here reaches a container.
  # `--pins-only-loud` keeps the refusal text, so a control can check WHICH refusal fired
  # rather than merely that one did.
  if [ "$PINS_ONLY" = "2" ]; then
    preflight_instruments; exit $?
  fi
  preflight_instruments >/dev/null 2>&1; exit $?
fi
if [ "$SELFTEST" = "1" ]; then
  selftest; exit $?
fi
[ -n "$LEG" ] || usage

# =============================================================================
# THE GUARDS.  ALL OF THEM, BEFORE ANYTHING ELSE, AND BEFORE ANY CONTAINER.
# =============================================================================
[ "$(bar0_no_step_plan_request)" = "PASS" ] || {
  say "ABORT BAR-0: this launcher carries a step-plan request. Arm A drops delta_repeat"
  say "  and delta_pert from delta_eff, delta_eff is a MAXIMUM, and removing a term from"
  say "  a maximum can only LOWER h_min -- toward \`admissible: true\`. Arm A may not size"
  say "  a step and this launcher may not ask for one."
  exit 2
}
preflight_freeze       || exit $?
preflight_instruments  || exit $?
preflight_registration "$LEG" || exit $?
ledger_bootstrap "$ROOT" || exit $?
item_ceiling_guard "$LEG" "$ROOT" || exit $?

if [ "$GUARDS_ONLY" = "1" ]; then
  say "GUARDS_ONLY leg=$LEG -- every guard driven, nothing launched"
  exit 0
fi

if [ "$LAUNCH_ENABLED" != "1" ]; then
  say "NOT_LAUNCHING leg=$LEG -- LAUNCH_ENABLED=0."
  say "  W3S is NOT FROZEN, NOT PINNED and NOT ENQUEUED, and its pre-registration is a"
  say "  DRAFT with no evidentiary force (sec.10 lists seven unticked boxes). The"
  say "  supervisor's SUPERVISION_CHARTER.md sec.3 checks 1 and 4 are NOT DELEGABLE and"
  say "  no lane performs them on the supervisor's behalf. Enqueueing is not"
  say "  authorisation. NO LANE RAISES THIS FLAG."
  exit 0
fi

# =============================================================================
# THE LEG BODY.  UNREACHABLE while LAUNCH_ENABLED=0.  Written out in full so the freeze
# reads the program it is freezing, not a promise of one.
# =============================================================================

# ---- a controlDict with a substituted endTime, read back rather than assumed ----------
mk_cd() {  # $1 template  $2 out  $3 endTime
  python3 - "$1" "$2" "$3" <<'PYCD'
import re, sys
src, dst, endt = sys.argv[1], sys.argv[2], sys.argv[3]
t = open(src).read()
t = re.sub(r"^endTime\s+\S+;", "endTime         %s;" % endt, t, flags=re.M)
open(dst, "w").write(t)
PYCD
}

# ---- THE STAGE RUNNER --------------------------------------------------------------
# $1 stage  $2 cost leg  $3 task  $4 stage_kind  $5 expected steps  $6 source `0` dir
# $7 controlDict  $8 extra shell command (task=shell only)
#
# EVERY GUARD RETURNS NON-ZERO AND THAT NON-ZERO PROPAGATES.  There is no `|| echo` on any
# call site in this file and `--selftest` reads this file's own source to prove it.
run_stage() {
  local STAGE="$1" CLEG="$2" TASK="$3" KIND="$4" NSTEP="$5" ZERO="$6" CDICT="$7"
  local SHCMD="${8:-}"
  local D="$ROOT/$STAGE" LOG="$ROOT/${STAGE}_${STAMP}.log"
  local NAME="w3s_${STAGE}_${STAMP}"

  # --- the MemAvailable floor: WAIT AND RE-POLL, BOUNDED, THEN TERMINATE ---
  local MA
  MA="$(memavail_wait_or_terminate "$STAGE" "$CLEG" "$ROOT")" || return 6

  # --- the registered leg cap, turned into a wall the OS will enforce ---
  local TMO BOUND=$STAGE_TMO_S
  [ "$STAGE" = "S0" ] && BOUND=$S0_TMO_S
  TMO="$(stage_timeout_for "$CLEG" "$ROOT" "$BOUND")" || {
    say "ABORT IN_LEG_BUDGET leg=$CLEG stage=$STAGE -- no budget remains under the"
    say "  registered $(leg_cap "$CLEG") core-min leg cap. An overrun STOPS the run; it"
    say "  does not get a new budget (CLAUDE.md rule 12)."
    return 6
  }
  echo "STAGE_TIMEOUT stage=$STAGE leg=$CLEG timeout_s=$TMO bound_s=$BOUND" >> "$LEDGER"

  # --- staging.  `cp -a` PRESERVES mtimes, which is why the age datum is not a copy. ---
  sudo -n rm -rf "$D" 2>/dev/null
  cp -a "$ROOT/mesh" "$D" || { say "ABORT stage $STAGE mesh copy failed"; return 4; }
  if [ "$CDICT" != "-" ]; then
    cp -a "$CDICT" "$D/system/controlDict" || { say "ABORT controlDict"; return 4; }
  fi
  if [ "$ZERO" != "-" ]; then
    sudo -n rm -rf "$D/0" 2>/dev/null
    cp -a "$ZERO" "$D/0" || { say "ABORT stage $STAGE initial-field copy"; return 4; }
    sudo -n rm -rf "$D/0/uniform" "$D/0/polyMesh" 2>/dev/null
  fi

  # --- endTime and the step count READ FROM THE controlDict THAT IS ACTUALLY STAGED ---
  local ENDT NSTEP_ACTUAL
  read -r ENDT NSTEP_ACTUAL <<< "$(python3 - "$D/system/controlDict" <<'PYCD2'
import re, sys
t = open(sys.argv[1]).read()
def grab(k):
    m = re.search(r"^\s*%s\s+([0-9.eE+-]+)\s*;" % k, t, re.M)
    return float(m.group(1)) if m else None
et, dt = grab("endTime"), grab("deltaT")
n = int(round(et / dt)) if (et is not None and dt not in (None, 0.0)) else 0
print(repr(et if et is not None else 0.0), n)
PYCD2
)"
  [ -n "$ENDT" ] || { say "ABORT could not read endTime from $STAGE/system/controlDict"; return 4; }
  if [ "$NSTEP" != "0" ] && [ "$NSTEP" != "$NSTEP_ACTUAL" ]; then
    say "ABORT stage $STAGE registered $NSTEP steps, its staged controlDict gives"
    say "  $NSTEP_ACTUAL (endTime=$ENDT). The registration and the thing that would run"
    say "  have diverged and the stage is NOT LAUNCHED."
    return 4
  fi
  NSTEP="$NSTEP_ACTUAL"

  # --- COLD START.  A guard refuses a case where a time dir already exists (rule 4). ---
  local COLD=1 bad
  for bad in "$D/$ENDT" "$D/0.01"; do
    [ "$bad" = "$D/0" ] && continue
    [ -e "$bad" ] && { say "COLDSTART FAIL: $bad exists"; COLD=0; }
  done
  [ -n "$(ls -d "$D"/processor* 2>/dev/null)" ] && { say "COLDSTART FAIL: processor*"; COLD=0; }
  [ "$COLD" -eq 1 ] || return 5

  # --- THE AGE SENTINEL, CREATED AND TOUCHED LAST.  See the header's mtime section. ---
  local SENTINEL="$ROOT/.w3s_age_ref.${CLEG}_${STAGE}"
  : > "$SENTINEL"
  touch "$SENTINEL"
  local AGE_DATUM; AGE_DATUM="$(stat -c %Y "$SENTINEL")"
  echo "AGE_DATUM stage=$STAGE leg=$CLEG sentinel=$(basename "$SENTINEL") mtime=$AGE_DATUM staging=cp-a-mtimes-PRESERVED datum=RUN-ROOT-SENTINEL-NOT-A-COPY" \
    >> "$LEDGER"
  # (i) NOTHING STAGED MAY POST-DATE THE DATUM.  This is the preserved-mtime hazard
  #     actually occurring and it refuses BEFORE the container starts.
  local POSTDATING
  # REPAIRED 2026-09-06 (W3S-DEF-AGE-1).  WAS: `-newermt "@$AGE_DATUM"`, and that is a
  # SUB-SECOND TRUNCATION, not a comparison.  `$AGE_DATUM` comes from `stat -c %Y`, which
  # is WHOLE SECONDS, and `-newermt "@N"` means STRICTLY AFTER N.000000000 -- so every
  # file staged in the SAME WALL-CLOCK SECOND as the sentinel was accused of post-dating a
  # sentinel it PRECEDES.  Measured on the 02:50:52Z refusal: the sentinel
  # `.w3s_age_ref.SETUP_S2a` stands at 1788663109.804247776 and the accused
  # `S2a/system/controlDict` at 1788663109.683474790 -- the file is 120.772986 ms OLDER.
  # S0/S1a/S1b passed only because their sentinels happened to straddle a second boundary,
  # so this was a RACE and re-firing unrepaired would have been a lottery.
  # `-newer "$SENTINEL"` compares FULL-PRECISION mtimes directly and truncates nothing; it
  # is strictly more faithful to the registered condition at :125-126 and :1190, which says
  # POST-DATE and not "falls in the same second or later".  No gate, band, threshold, cap
  # or label moves: this variable is read at the two lines below and NOWHERE else, feeds no
  # manifest row, and produces no number.  The row's own `age_staged_postdating` is
  # recomputed independently by `w3s_stage_record.py` and is NOT touched by this repair.
  POSTDATING="$(find "$D" -type f -newer "$SENTINEL" 2>/dev/null | head -5)"
  if [ -n "$POSTDATING" ]; then
    say "ABORT AGE_STAGING: staged file(s) POST-DATE the age sentinel:"
    printf '  %s\n' $POSTDATING
    # SINGLE-QUOTED, and that is the repair, not a style choice.  This line previously read
    # `say "  `cp -a` preserves mtimes, ..."` -- BACKTICKS INSIDE DOUBLE QUOTES ARE COMMAND
    # SUBSTITUTION, so printing this refusal EXECUTED `cp -a` with no operands and the
    # message went out with the words `cp -a` REPLACED BY THE COMMAND'S EMPTY STDOUT.  That
    # is the `cp: missing file operand` in `launcher.queue.out`.  It survived because `cp`
    # with no operands fails loudly and changes nothing; a quoted span naming a command
    # that DOES something would have injected its effect and left no scar.
    say '  `cp -a` preserves mtimes, so a staged file newer than the datum would let a'
    say '  field this run did not produce pass the age guard. REFUSED.'
    return 2
  fi

  # --- THE CONTAINER ---
  local T0 T1 WALL rc INSPECT CMD CM
  if [ "$TASK" = "shell" ]; then
    CMD="$SHCMD"
  else
    CMD="mpirun --allow-run-as-root --bind-to none -np 1 python d12y_run_script.py --task=$TASK --dvIndex=0 --dvDelta=0.0 --out=d12y_${STAGE}.json"
  fi
  T0="$(date -u +%s)"
  timeout "$TMO" sudo -n docker run --name "$NAME" \
      --user 0:0 --cpus=1 --cpuset-cpus="$CPUSET_CPUS" \
      --memory=$MEM_LIMIT --memory-swap=$MEM_LIMIT --oom-score-adj=500 \
      -v "$ROOT":/mnt -w "/mnt/$STAGE" "$IMG_SHIPPED" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && $CMD" \
      > "$LOG" 2>&1
  rc=$?
  T1="$(date -u +%s)"; WALL=$((T1-T0))
  INSPECT="$(sudo -n docker inspect --format '{{.State.ExitCode}}|{{.State.OOMKilled}}' "$NAME" 2>/dev/null)"
  sudo -n docker rm "$NAME" >/dev/null 2>&1
  sudo -n chown -R ubuntu:ubuntu "$LOG" "$D" "$SENTINEL" 2>/dev/null
  CM="$(python3 -c "print(round($WALL/60.0,4))")"

  # --- THE MANIFEST ROW.  ONE PRODUCER, and every field read off disk. ---
  python3 "$RECORD" --emit-row --root "$ROOT" --cost-leg "$CLEG" --stage "$STAGE" \
      --task "$TASK" --stage-kind "$KIND" --expected-steps "$NSTEP" --rc "$rc" \
      --wall-s "$WALL" --core-min "$CM" --memavail "$MA" --endtime "$ENDT" \
      --stage-dir "$D" --log "$LOG" --age-datum "$AGE_DATUM" \
      --age-sentinel "$SENTINEL" --docker-inspect "$INSPECT" \
      --dv-index 0 --dv-delta 0.0 \
      --dv-units "FFD shape-function DV, dimensionless driver units (scaler 10, bounds +/-1)" \
      --coldstart-ok 1 || { say "ABORT the manifest row could not be written for $STAGE"; return 2; }

  # --- the stage-detail ledger line.  DELIBERATELY NOT SPEND-SHAPED (see the record
  # --- producer): the leg's single `LEG=` row is the spend row and nothing double-counts.
  python3 "$RECORD" --stage-detail-line --stage "$STAGE" --cost-leg "$CLEG" --rc "$rc" \
      --wall-s "$WALL" --core-min "$CM" --memavail "$MA" --log "$LOG" >> "$LEDGER"

  return $rc
}

# ---- THE COST LEGS ------------------------------------------------------------------
LEG_RC=0

if [ "$LEG" = "SETUP" ]; then
  # --- S0: the mesh.  A bootstrap stage: it CANNOT call run_stage, because run_stage
  # --- begins by copying `$ROOT/mesh`, which is the thing S0 creates.  D12R2-DEF-3 is
  # --- that this ordering left the bootstrap row unwritten; the row is written here.
  mkdir -p "$ROOT/mesh"
  cp -a "$TUT"/0_orig "$TUT"/FFD "$TUT"/constant "$TUT"/system "$TUT"/genMesh.py \
        "$TUT"/runPrimalSimple.py "$ROOT/mesh/" || { say "ABORT tutorial copy"; exit 4; }
  cp -a "$RUNPY" "$ROOT/mesh/" || { say "ABORT runscript copy"; exit 4; }
  cp -a "$TUT"/system/fvSchemes_pimple "$ROOT/mesh/system/fvSchemes"
  cp -a "$TUT"/system/fvSolution_pimple "$ROOT/mesh/system/fvSolution"

  S0_MA="$(memavail_wait_or_terminate S0 SETUP "$ROOT")" || { finalize_leg SETUP "$ROOT" 6; exit 6; }
  S0_TMO="$(stage_timeout_for SETUP "$ROOT" "$S0_TMO_S")" || { finalize_leg SETUP "$ROOT" 6; exit 6; }
  S0_SENTINEL="$ROOT/.w3s_age_ref.SETUP_S0"
  : > "$S0_SENTINEL"; touch "$S0_SENTINEL"
  S0_DATUM="$(stat -c %Y "$S0_SENTINEL")"
  echo "AGE_DATUM stage=S0 leg=SETUP sentinel=$(basename "$S0_SENTINEL") mtime=$S0_DATUM" >> "$LEDGER"
  S0_T0="$(date -u +%s)"
  timeout "$S0_TMO" sudo -n docker run --name "w3s_S0_${STAMP}" --user 0:0 --cpus=1 \
      --cpuset-cpus="$CPUSET_CPUS" -v "$ROOT":/mnt -w /mnt/mesh "$IMG_SHIPPED" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && python genMesh.py && \
       plot3dToFoam -noBlank volumeMesh.xyz && autoPatch 30 -overwrite && \
       createPatch -overwrite && renumberMesh -overwrite && checkMesh -constant | tail -30" \
      > "$ROOT/S0_${STAMP}.log" 2>&1
  S0_RC=$?
  S0_T1="$(date -u +%s)"
  S0_INSPECT="$(sudo -n docker inspect --format '{{.State.ExitCode}}|{{.State.OOMKilled}}' "w3s_S0_${STAMP}" 2>/dev/null)"
  sudo -n docker rm "w3s_S0_${STAMP}" >/dev/null 2>&1
  sudo -n chown -R ubuntu:ubuntu "$ROOT" 2>/dev/null
  S0_CM="$(python3 -c "print(round($((S0_T1-S0_T0))/60.0,4))")"
  python3 "$RECORD" --emit-row --root "$ROOT" --cost-leg SETUP --stage S0 --task mesh \
      --stage-kind mesh --rc "$S0_RC" --wall-s "$((S0_T1-S0_T0))" --core-min "$S0_CM" \
      --memavail "$S0_MA" --stage-dir "$ROOT/mesh" --log "$ROOT/S0_${STAMP}.log" \
      --age-datum "$S0_DATUM" --age-sentinel "$S0_SENTINEL" \
      --docker-inspect "$S0_INSPECT" --dv-units "none (mesh)" --coldstart-ok 1 \
      || { say "ABORT S0 manifest row"; finalize_leg SETUP "$ROOT" 2; exit 2; }
  python3 "$RECORD" --stage-detail-line --stage S0 --cost-leg SETUP --rc "$S0_RC" \
      --wall-s "$((S0_T1-S0_T0))" --core-min "$S0_CM" --memavail "$S0_MA" \
      --log "$ROOT/S0_${STAMP}.log" >> "$LEDGER"
  if [ "$S0_RC" -ne 0 ]; then
    say "ABORT S0 rc=$S0_RC"; finalize_leg SETUP "$ROOT" "$S0_RC"; exit "$S0_RC"
  fi
  sudo -n rm -rf "$ROOT/mesh/0" "$ROOT/mesh/processor"* 2>/dev/null

  # --- S1a: the tutorial's own spin-up, at np=1 (the REGISTERED decomposition) ---
  run_stage S1a SETUP shell steady 500 "$ROOT/mesh/0_orig" \
    "$TUT/system/controlDict_simple" \
    "cp -r system/fvSchemes_simple system/fvSchemes && cp -r system/fvSolution_simple system/fvSolution && potentialFoam && mpirun --allow-run-as-root --bind-to none -np 1 python runPrimalSimple.py"
  LEG_RC=$?
  [ "$LEG_RC" -eq 0 ] || { finalize_leg SETUP "$ROOT" "$LEG_RC"; exit "$LEG_RC"; }
  [ -d "$ROOT/S1a/500" ] || { say "ABORT S1a produced no 500 directory"; finalize_leg SETUP "$ROOT" 4; exit 4; }

  run_stage S1b SETUP run_model unsteady 200 "$ROOT/S1a/500" \
    "$TUT/system/controlDict_pimple_long" ""
  LEG_RC=$?
  [ "$LEG_RC" -eq 0 ] || { finalize_leg SETUP "$ROOT" "$LEG_RC"; exit "$LEG_RC"; }
  [ -d "$ROOT/S1b/10" ] || { say "ABORT S1b produced no t=10 directory (FIELD_A)"; finalize_leg SETUP "$ROOT" 4; exit 4; }
  cp -a "$ROOT/S1b/10" "$ROOT/FIELD_A"
  sudo -n rm -rf "$ROOT/FIELD_A/uniform" "$ROOT/FIELD_A/polyMesh" 2>/dev/null

  # --- S2a: the transient discard.  Its endTime IS the discard point, so FIELD_B is a
  # --- FINAL-time write (11 fields) and not an intermediate per-step write (4 fields).
  mk_cd "$TUT/system/controlDict_pimple" "$ROOT/cd_S2a" \
        "$(python3 -c "print($TRANSIENT_DISCARD*float('$DELTAT'))")"
  run_stage S2a SETUP run_model unsteady "$TRANSIENT_DISCARD" "$ROOT/FIELD_A" \
    "$ROOT/cd_S2a" ""
  LEG_RC=$?
  [ "$LEG_RC" -eq 0 ] || { finalize_leg SETUP "$ROOT" "$LEG_RC"; exit "$LEG_RC"; }
  FB_T="$(python3 -c "print(repr(round($TRANSIENT_DISCARD*float('$DELTAT'),8)))")"
  SRCB=""
  for nm in "$FB_T" "$(python3 -c "print('%g' % $FB_T)")"; do
    [ -d "$ROOT/S2a/$nm" ] && { SRCB="$ROOT/S2a/$nm"; break; }
  done
  [ -n "$SRCB" ] || { say "ABORT S2a has no t=$FB_T directory for FIELD_B"; finalize_leg SETUP "$ROOT" 4; exit 4; }
  cp -a "$SRCB" "$ROOT/FIELD_B"
  sudo -n rm -rf "$ROOT/FIELD_B/uniform" "$ROOT/FIELD_B/polyMesh" 2>/dev/null
  ( cd "$ROOT/FIELD_B" && find . -type f | sort | xargs md5sum ) > "$ROOT/FIELD_B.md5"
  echo "FIELD_B_CREATED from $SRCB files=$(wc -l < "$ROOT/FIELD_B.md5")" >> "$LEDGER"

else
  # --- A0 / A1 / A2: ONE adjoint each, all three from the SAME frozen FIELD_B. ---
  W="$(leg_window "$LEG")"
  [ -d "$ROOT/FIELD_B" ] || { say "ABORT leg=$LEG: FIELD_B is absent -- the SETUP leg has not run"; exit 4; }
  [ -f "$ROOT/FIELD_B.md5" ] || { say "ABORT leg=$LEG: FIELD_B.md5 is absent"; exit 4; }
  NOW="$(mktemp)"
  ( cd "$ROOT/FIELD_B" && find . -type f | sort | xargs md5sum ) > "$NOW"
  if ! diff -q "$ROOT/FIELD_B.md5" "$NOW" >/dev/null; then
    say "ABORT leg=$LEG: FIELD_B md5 manifest MISMATCH -- the frozen initial condition"
    say "  changed between legs, so the three windows are NOT the same measurement."
    rm -f "$NOW"; exit 2
  fi
  rm -f "$NOW"
  # THE PER-LEG WINDOW RECORD.  Written BEFORE the stage, so a leg that dies still leaves
  # a record of the window it was launched at, and w3s_grade's N7 has something to read.
  python3 "$RECORD" --w-steps-line --cost-leg "$LEG" --deltat "$DELTAT" >> "$LEDGER" \
    || { say "ABORT could not write the per-leg W_STEPS line"; exit 2; }
  mk_cd "$TUT/system/controlDict_pimple" "$ROOT/cd_W_$LEG" \
        "$(python3 -c "print($W*float('$DELTAT'))")"
  run_stage S5 "$LEG" compute_totals unsteady "$W" "$ROOT/FIELD_B" "$ROOT/cd_W_$LEG" ""
  LEG_RC=$?
fi

# =============================================================================
# THE PER-LEG RULE-4 ASSERTION AND THE FINALIZER.  Both run on EVERY path.
# =============================================================================
python3 "$RECORD" --verify-leg --root "$ROOT" --cost-leg "$LEG" | tee -a "$LEDGER"
VERIFY_RC=${PIPESTATUS[0]}
finalize_leg "$LEG" "$ROOT" "$LEG_RC"
FINAL_RC=$?

if [ "$LEG_RC" -ne 0 ]; then exit "$LEG_RC"; fi
if [ "$VERIFY_RC" -ne 0 ]; then exit "$VERIFY_RC"; fi
if [ "$FINAL_RC" -ne 0 ]; then exit "$FINAL_RC"; fi
say "LEG_OK leg=$LEG root=$ROOT"
say "NEXT: after every leg, the FROZEN comparator grades the scan --"
say "  python3 $GRADER --gscan --manifest $MANIFEST --root $ROOT"
say "  Arm A grades NO admissibility and sizes NO step; asking it to is refused at four"
say "  depths (BAR-0 here, BAR-1/2/3 in the comparator)."
exit 0
