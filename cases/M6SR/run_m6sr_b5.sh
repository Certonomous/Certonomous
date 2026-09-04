#!/bin/bash
# M6SR SOLVE DRIVER -- steps B4 and B5a/B5b/B5c of
# verification/campaign/M6SR_PREREGISTRATION.md.
#
# WHAT THIS FILE IS.  Amendment 10 item 10 records, measured, that "NO REGISTERED ARTIFACT
# RUNS `B5a`, `B5b` OR `B5c` -- 607.63 of 615.24 core-min, 98.8 % of the ladder -- AND NONE
# OF SECTION 8's CASE FILES EXISTS", and that in consequence "a queue row cannot be written
# today: its `launch_cmd` has no target for `B5`".  THIS FILE IS THAT TARGET.
#
# It also produces B4's `log.checkMesh`, which likewise had no producer: the registered
# build driver cases/M6SR/build_m6sr_l1.sh covers B1/B2/B3 only and its own closing line
# reads "THIS DRIVER GRADES NOTHING".
#
# IT IS A SOLVER DRIVER, NOT A GRADER.  It computes no gate, applies no threshold and
# prints no verdict.  Standing rule 2 fixes the GRADING path at the pre-registration
# commit; this file runs the solver and cases/M6SR/analyse_m6sr.py grades what it produced.
# NOTHING HERE MAY EVER GRADE.
#
# SECTIONS OF THE REGISTRATION IMPLEMENTED HERE:
#   Section 2.4   the per-step CAPS in core-minutes.  🔴 STRUCK BY QUOTE, 2026-09-04, ITEM 39:
#                 ~~"the per-step CAPS in core-minutes, enforced STRUCTURALLY by `timeout`."~~
#                 `timeout` was MEASURED NOT TO BOUND A CONTAINER IT STARTED (a 3 s cap on a
#                 60 s container returned rc 124 after 61 WALL SECONDS; an unbounded payload
#                 never returned at all).  The caps ARE now enforced -- by `timeout -k` + an
#                 UNCONDITIONAL `docker kill` on the recorded name + an overrun branch
#                 accepting 124 AND 137 -- but NOT by `timeout`, and by no one limb alone.
#                 B5a/B5b/B5c caps are PER-LEVEL rows (31.0 / 163.0 / 1630.0).  B4's 2.0 is
#                 ONE row for "checkMesh x3", so it is a RUNNING budget across the three
#                 levels, tracked on disk and refused when exhausted.
#   Section 3.2   `hierarchical` decomposition; `scotch` is NOT used.
#   Section 7     the ill-posedness screen.  AMENDMENT 20, ITEM 47: this driver now RUNS
#                 THE SCREEN ITSELF at new step `B4s` -- after B4's checkMesh, before the
#                 case writer and the solver -- via
#                 `cases/M6SR/analyse_m6sr.py --section7-screen --level --case`, and a
#                 BLOCKED level REFUSES the solve at exit 11 naming the clause and its
#                 measured value against its threshold, a REFUSAL at exit 12.
#                 BEFORE AMENDMENT 20 THIS LINE DESCRIBED SOMETHING WEAKER AND IT IS NOT
#                 QUIETLY REPLACED -- what it said was true and was ALL there was:
#                 "the driver REFUSES patch types it did not expect, through the case
#                 writer's CH1 classification", i.e. condition 1 only, enforced by another
#                 file, with conditions 2-5 consulted by NOTHING on the launch path.
#   Section 8     every case file, written by cases/M6SR/write_m6sr_case.py.
#   Section 8.6   the launcher REFUSES a case where `0` or any time directory exists, and
#                 the strict all-or-nothing completion rule is EVALUATED (never graded) here.
#   Section 9.2   execution and assertion mechanics -- every line of it, below.
#   Section 9.3   rule 12's estimate-versus-actual, owed at EVERY step.
#   Section 18    AMENDMENT 12 -- THE INSTRUMENT IS PINNED, AND THE GRADING PATH IS
#                 REHEARSED BEFORE THE RUN IS PAID FOR.  Three new refusals, all at ZERO
#                 SOLVER COST:
#                   exit 7  the running image's DIGEST, or the resolved solver binary's
#                           PATH / VERSION / sha256, does not match the pinned one.
#                   exit 8  the GRADING path's planted controls do not pass, so a solve
#                           would be ungradable after it was paid for.
#                   exit 9  the run root is not the one Section 9's frozen path table
#                           registers, so producer and reader would use different trees.
#   AMENDMENT 12 AUDIT, ITEMS 28 AND 30 -- REPAIRED IN THIS FILE (see Section 1 and
#                 Section 2 for each defect stated with its measurement and its controls).
#                 Item 28: the container call was correct ONLY on the `sg docker -c` branch;
#                 BARE_RC is 0 on this box, so the LIVE branch had never been exercised.
#                 Item 30: the case directory was not writable by the container's uid at B4,
#                 and item 28 was MASKING it -- fixing 28 alone does NOT fix 30.
#                 NEITHER EVER MIS-RAN ANYTHING: both failed closed at exit 6.
#
#   ITEM 31, FOUND WHILE REPAIRING THOSE TWO -- REPORTED, NOT REPAIRED HERE.
#                 With 28 and 30 repaired, B4's checkMesh reaches the container, writes its
#                 log, and STILL returns inner rc 1:
#                     --> FOAM FATAL ERROR: cannot find file "/case/system/controlDict"
#                 `system/controlDict` is written by cases/M6SR/write_m6sr_case.py, which
#                 this driver invokes in the SOLVE phase (Section 4) -- AFTER B4.  So B4 runs
#                 checkMesh against a case that has a mesh and no system directory.  MEASURED:
#                 with the case written first, the SAME checkMesh under the SAME two repairs
#                 returns inner rc 0 and a 3330-byte log ending `Mesh OK.` / `End`, so there
#                 is no FOURTH failure behind it -- the chain is exactly three deep.
#                 IT IS NOT REPAIRED HERE ON PURPOSE.  The fix is to write Section 8's case
#                 before B4 rather than after it, and that is a change to the REGISTERED STEP
#                 ORDER (Sections 4, 8, 8.6), not to the launch path.  This driver is also
#                 forbidden from writing a controlDict of its own -- Section 1 above: "This
#                 driver writes NO case file of its own -- there is ONE writer and it is that
#                 one" -- so no repair is available inside this file's own authority.
#                 IT FAILS CLOSED at exit 6, and Gate A reads a fatal-error log as ABSENT,
#                 never as clean.
#
#   ITEM 32  -- REPAIRED HERE, AND IT IS THE ONE OF THE FOUR THAT DID **NOT** FAIL CLOSED.
#   (registered as item 34; see THE NUMBERING CROSSWALK below)
#
#            THE DEFECT, STATED EXACTLY.  run_in_container() sent the OUTER wrapper's
#            stdout+stderr to `$CASE/log.$tag`.  For the B5 steps that is a wrapper log with a
#            name of its own (log.B5a) and the registered artifacts are written separately
#            (log.rhoSimpleFoam, log.decomposePar).  For B4 the tag IS `checkMesh`, so the
#            outer redirect target and the inner command's output file were THE SAME PATH --
#            `$CASE/log.checkMesh` -- and Gate A reads that file.  The host shell opens it with
#            O_TRUNC and HOLDS THE FD AT OFFSET 0 for the life of the docker client, while the
#            container opens the SAME inode through the bind mount with its own fd.  Anything
#            the docker client then writes -- its own diagnostics, or the container's unredirected
#            stdout, which the client streams back -- lands AT OFFSET 0 and overwrites the head.
#
#            MEASURED ON THE PINNED DIGEST, NOT ARGUED (2026-09-04, scratch tree, no run root):
#              * synthetic: container wrote 65 bytes through the mount, client then emitted a
#                20-byte line -> file 65 bytes, first 20 REPLACED, remainder byte-intact.
#              * REAL checkMesh on the L3 mesh, same shape: log.checkMesh 3330 bytes, the first
#                20 bytes of the OpenFOAM banner replaced by the client's line, and
#                analyse_m6sr.read_checkmesh() on that file returned state=READ,
#                max_non_orthogonality_deg 61.49376508, max_skewness 2.306553794,
#                max_aspect_ratio 608.2069422, `Mesh OK.` and `End` intact.
#                THE CORRUPTED FILE WOULD HAVE GRADED GATE A CLEAN.  A1 and A2 read within
#                threshold off a head-corrupted artifact and NOTHING ANNOUNCED IT.
#            WHY IT IS WORSE THAN THE OTHER THREE: items 28, 30 and 31 all fail closed at exit 6.
#            This one corrupted the HEAD of a graded artifact while leaving the numeric maxima
#            near the END intact and parseable, so it read CLEAN rather than ABSENT.  It did not
#            fire in any measured run -- no run root exists -- so this is PREVENTION, not the
#            repair of a live corruption.
#
#            THE REPAIR, AND WHY IT MAKES THE COLLISION IMPOSSIBLE RATHER THAN UNLIKELY.
#            The container's ONLY view of this filesystem is `-v "$CASE":/case`.  A path that is
#            not under $CASE therefore cannot be opened by any process inside the container,
#            WHATEVER NAME the inner command uses -- the two writers are separated by MOUNT
#            TOPOLOGY, not by a naming convention that a future tag could break.  The wrapper's
#            log is moved OUT OF THE MOUNT to `$RR/_wrapper_logs/$LEVEL/log.$tag`, and
#            run_in_container REFUSES (exit 6) before starting the container if that target is
#            $CASE or anything under it.  MEASURED after the repair, same real checkMesh:
#            log.checkMesh 3330 bytes with its head `/*------...` intact, and the client's
#            20-byte line alone in the wrapper log.
#            `cases/M6SR/build_m6sr_l1.sh` is ALREADY immune for exactly this reason and was
#            checked: it mounts `$RR/$LEVEL/work` and writes its wrapper log one level above it.
#            SECOND, INDEPENDENT GUARD (Section 3): B4 now asserts that log.checkMesh BEGINS
#            with the OpenFOAM banner, so a head overwrite from any future source is a REFUSAL
#            and not a clean grade.  That assertion is only safe because the image is pinned by
#            digest -- the banner is fixed by the pin.
#
#   THE NUMBERING CROSSWALK, BECAUSE THE TWO COUNTERS COLLIDE.
#            M6SR_PREREGISTRATION.md runs ONE GLOBAL item counter and its §18.8 already spends
#            31 and 32 on different findings (31 = the container carries more rhoSimpleFoam
#            binaries than item 26 counted; 32 = §9's frozen path table registers two executables
#            and the ladder runs seven).  The board's "item 31" and "item 32" are NOT those.  In
#            the registration they are numbered from the tail:
#                board item 31 (step order)   == registration ITEM 33
#                board item 32 (shared path)  == registration ITEM 34
#            Both names are kept here so neither reader is stranded.
#
#                 A registration that pins `case_2308.dat` and a points sha256 but not the
#                 solver binary is pinning the DATA AND NOT THE INSTRUMENT.  The container
#                 carries THREE `rhoSimpleFoam` binaries (v2506, and OpenFOAM-AD's ADF and
#                 ADR builds) and the box a FOURTH (native openfoam2606); `M6SR_IMAGE` could
#                 previously swap the whole tree between the freeze and the run.
#
# SECTION 9.2, BINDING, AND EACH LINE OF IT IS OBSERVED HERE:
#   * ASSERTIONS DO NOT GATE.  No `assert`, no bare `set -e`.  Every check is
#     `... || { echo "ABORT: <what>"; exit N; }`.  A guard set that is assert-based is one
#     interpreter flag from absent (L-475).
#   * SHAS ARE READ BACK BY SUBJECT LINE, never by position in a batch (L-479).
#   * `setsid timeout cmd` EXITS 0 FOR EVERY OUTCOME.  rc is captured INSIDE the wrapper
#     and written to a file; it is never taken from around the wrapper line.
#   * `grep ... log.* | tail -1` IS A COIN FLIP under multi-file output.  Every reading in
#     this file names ONE artifact by explicit path.
#   * RANKS ARE TAKEN FROM THE SOLVER LOG'S OWN BANNER, NEVER FROM decomposeParDict.  That
#     file can post-date the run, and the banner's FIRST occurrence is not necessarily the
#     primal's -- so this driver reads EVERY `nProcs` line in the ONE named solver log and
#     REFUSES if they are not all equal, and if they do not equal what it asked for.
#
# THE RANK-BASIS TRAP, CARRIED FORWARD FROM AMENDMENT 8 AND NOT RE-LITIGATED HERE.
# Section 2.4's solve rate 3.40e-8 core-min/cell/iteration is a FOUR-RANK measurement
# (`nProcs : 4` in the primal banner of A3-onera-m6-transonic/run_model_run3.log).  B5b
# runs at 8 ranks and B5c at 16, so the registered estimate applies a 4-rank rate at 2x and
# 4x the ranks and thereby ASSUMES PERFECT STRONG SCALING.  Real efficiency below 1 makes
# the actual core-minutes RISE, not fall.  This driver does not change a registered number;
# it records the measured core-minutes and the measured rank count side by side so the
# Section 9.3 calibration row can attribute the miss.
#
# COST.  Unit: core-minutes (wall s x ranks / 60).  Dollars are DERIVED, NOT MEASURED, at
# the owner-stated c7a.4xlarge $0.0513/core-h -- the box cannot read its own billing, so any
# dollar figure originating here is REPORTED-BY-OWNER.  AN OVERRUN STOPS THE RUN; it does
# not get a new budget.  🔴 STRUCK BY QUOTE, 2026-09-04, ITEM 39: ~~"Every cap below is
# enforced by `timeout`, so an overrun is structural rather than a matter of somebody
# noticing."~~  MEASURED FALSE AS WRITTEN.  `timeout` bounds the docker CLIENT, not the
# CONTAINER, and without `-k` it does not even bound the client: it WAITS.  Every cap below is
# enforced by THREE limbs together -- `timeout -k` on the client, an UNCONDITIONAL `docker
# kill` on the recorded container name, and an overrun branch accepting 124 AND 137 -- and an
# overrun IS now structural rather than a matter of somebody noticing.
#
# NOTHING UNDER /home/ubuntu/certonomous-runs/ IS WRITTEN, MOVED OR DELETED.  L3's and L2's
# meshes are COPIED OUT of that tree; every product is written under the run root.
#
# SUBMISSIONS ARE PARKED (standing rule 7).  This driver sends nothing anywhere.
#
# USAGE:  run_m6sr_b5.sh <L3|L2|L1> [stage|solve|all]

set +u
set +e

LEVEL="$1"
PHASE="${2:-all}"

RR=${M6SR_RUN_ROOT:-/home/ubuntu/Certonomous/verification/runs/M6SR_runs}
CR=/home/ubuntu/certonomous-runs
CASES=/home/ubuntu/Certonomous/cases/M6SR
IMG=${M6SR_IMAGE:-dafoam-idwarp-rot:v1}
RATE_USD_PER_CORE_H=0.0513

# ---------------------------------------------------------------------------------------
# AMENDMENT 12 RULING 1 -- THE PINNED INSTRUMENT.  These are NOT `${VAR:-default}` forms and
# NOTHING IN THE ENVIRONMENT CAN CHANGE THEM.  `M6SR_IMAGE` above may still NAME any image;
# it can no longer SELECT one, because the digest below must match or the driver aborts at
# exit 7 before a single core-minute is spent.
#
# HOW EACH VALUE WAS OBTAINED (recorded, because a pin whose provenance is not stated is a
# number somebody typed):
#   digest  `docker inspect dafoam-idwarp-rot:v1` -> `.Id`, which on this daemon
#           (docker 29.1.3, storage driver overlayfs) is the OCI IMAGE MANIFEST digest:
#           `.Descriptor` reads mediaType application/vnd.oci.image.manifest.v1+json,
#           size 2301, digest identical to `.Id`, and `.RepoDigests` carries the same value.
#           CAVEAT, STATED: it is NOT corroborated against a registry.  The image was built
#           on this box (Created 2026-08-21T16:09:52Z) and no registry copy was consulted.
#   version `WM_PROJECT_VERSION` inside the container after sourcing loadDAFoam.sh, and
#           `META-INFO/api-info` reading `api=2506  patch=0`.
#   path    `command -v rhoSimpleFoam` inside that container, after the same source.
#   sha256  `sha256sum` of that resolved path, inside that container.
M6SR_PINNED_IMAGE_REF=dafoam-idwarp-rot:v1
M6SR_PINNED_IMAGE_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
M6SR_PINNED_OF_FORK="ESI OpenFOAM (openfoam.com), NOT the OpenFOAM Foundation fork"
M6SR_PINNED_OF_VERSION=v2506
M6SR_PINNED_SOLVER_PATH=/home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506/platforms/linux64GccDPInt32Opt/bin/rhoSimpleFoam
M6SR_PINNED_SOLVER_SHA256=d9a2a45664f519e9f6b4c34741a4c414517889b4cfbe7764b2237ebf9a01369c

say(){ echo "[$(date -u +%H:%M:%SZ)] $*"; }
abort(){ echo "ABORT: $1"; mkdir -p "$RR/$LEVEL" 2>/dev/null; echo "$1" > "$RR/$LEVEL/STOPPED.txt" 2>/dev/null; exit "${2:-1}"; }

# sha256 of ONE named file.  L-479: never a batch, never read back by position.
sha_of(){ sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }

# ---------------------------------------------------------------------------------------
# 0.  THE LEVEL TABLE.  Section 2.2 / 2.4 / 8.5.  Nothing here is chosen by this driver.
# ---------------------------------------------------------------------------------------
case "$LEVEL" in
  L3) CELLS=99840   ; END_TIME=3000 ; RANKS=4  ; CAP_B5=31.0   ; EST_B5=10.18
      MESH_SRC="$CR/A3-onera-m6-adjoint-coarse/constant/polyMesh" ; STEP=B5a ;;
  L2) CELLS=399360  ; END_TIME=4000 ; RANKS=8  ; CAP_B5=163.0  ; EST_B5=54.31
      MESH_SRC="$CR/.mesh-cache/onera_m6/polyMesh"               ; STEP=B5b ;;
  L1) CELLS=1597440 ; END_TIME=5000 ; RANKS=16 ; CAP_B5=1630.0 ; EST_B5=543.13
      MESH_SRC="$RR/L1/constant/polyMesh"                        ; STEP=B5c ;;
  *)  echo "ABORT: level must be one of L3 L2 L1; got '${LEVEL:-<empty>}'"; exit 2 ;;
esac
case "$PHASE" in
  stage|solve|all) : ;;
  *) echo "ABORT: phase must be one of stage solve all; got '$PHASE'"; exit 2 ;;
esac

CASE="$RR/$LEVEL"
CAP_B4_TOTAL=2.0                       # Section 2.4: ONE row, "checkMesh x3", for all levels
B4_LEDGER="$RR/B4_SPENT_COREMIN.txt"

say "M6SR solve driver -- level $LEVEL ($STEP), phase $PHASE"
say "run root: $RR   (nothing under $CR is written)"
say "schedule: $CELLS cells, endTime $END_TIME, $RANKS ranks, cap $CAP_B5 core-min (est $EST_B5)"

# ---------------------------------------------------------------------------------------
# 1.  REFUSALS BEFORE ANY WORK.
# ---------------------------------------------------------------------------------------
[ -x "$CASES/write_m6sr_case.py" ] || [ -f "$CASES/write_m6sr_case.py" ] \
  || abort "the registered case writer $CASES/write_m6sr_case.py is ABSENT. This driver writes NO case file of its own -- there is ONE writer and it is that one." 3

# Section 8.6: the launcher REFUSES a case where `0` or any time directory already exists.
if [ -d "$CASE" ]; then
  [ -d "$CASE/0" ] && abort "$CASE/0 already exists. The age guard dates the run from the case's own 0/U, so a pre-existing 0/ makes standing rule 4 unprovable. REFUSED (Section 8.6)." 4
  for D in "$CASE"/[0-9]*; do
    [ -d "$D" ] && abort "a time directory already exists: $D. REFUSED (Section 8.6)." 4
  done
fi

mkdir -p "$CASE" || abort "could not create $CASE" 3

# Docker preflight, BOTH limbs recorded, because the bare failure would be silent.
BARE_OUT=$(docker version --format '{{.Server.Version}}' 2>&1); BARE_RC=$?
SG_OUT=$(sg docker -c "docker version --format '{{.Server.Version}}'" 2>&1); SG_RC=$?
{ echo "bare_rc=$BARE_RC"; echo "bare_out=$BARE_OUT"
  echo "sg_rc=$SG_RC";     echo "sg_out=$SG_OUT"
  echo "groups=$(id -G)"; } > "$CASE/DOCKER_PREFLIGHT.txt"
if [ $SG_RC -ne 0 ] && [ $BARE_RC -ne 0 ]; then
  abort "docker unreachable both bare and through 'sg docker -c'. This grades THE DRIVER'S ABILITY TO RUN and nothing about the M6 -- BLOCKED, not GATE FAIL." 5
fi
# WHICH BRANCH THIS BOX TAKES IS RECORDED IN THE RUN'S OWN OUTPUT, not merely printed to a
# terminal nobody keeps.  Amendment 12 item 28's defect survived precisely because no artifact
# ever distinguished the two branches: BARE_RC is 0 on this box, so the `sg docker -c` branch
# has NEVER been exercised here and the bare branch was the broken one.  A later reader must
# be able to tell which invocation produced a given run without re-deriving it from the box's
# group membership months afterwards.
if [ $BARE_RC -eq 0 ]; then DOCKER_BRANCH=bare; else DOCKER_BRANCH=sg; fi
HOST_UID=$(id -u); HOST_GID=$(id -g)
# `timeout` execs a PROGRAM.  It cannot exec the shell builtin `command`, so the resolved
# path is taken ONCE here rather than written as `timeout ...s command docker ...`, which was
# MEASURED to return rc 127 (`timeout: failed to run command 'command'`).  That rc is not 124
# and would not have been read as a cap overrun -- it would have aborted at exit 6 with a
# misleading cause.
DOCKER_BIN=$(command -v docker 2>/dev/null)
[ "$DOCKER_BRANCH" != "bare" ] || [ -n "$DOCKER_BIN" ] \
  || abort "the bare-docker branch was selected (bare rc=$BARE_RC) but 'docker' does not resolve on PATH, so there is no program for \`timeout\` to exec. This driver will not guess a path." 5
{ echo "branch=$DOCKER_BRANCH"
  echo "docker_bin=$DOCKER_BIN"
  echo "host_uid=$HOST_UID"
  echo "host_gid=$HOST_GID"
  echo "container_user=1002:1002 (dafoamuser) plus supplementary group $HOST_GID (item 30)"; } \
  >> "$CASE/DOCKER_PREFLIGHT.txt"
echo "$DOCKER_BRANCH" > "$CASE/DOCKER_BRANCH.txt"
say "docker reachable (bare rc=$BARE_RC, sg rc=$SG_RC); invocation branch '$DOCKER_BRANCH'${DOCKER_BIN:+ via $DOCKER_BIN}"

# ---------------------------------------------------------------------------------------
# 1b.  AMENDMENT 12 RULING 1 -- THE SOLVER IS PINNED, AND THE PIN REFUSES BEFORE IT SPENDS.
#
#      THIS HELPER PASSES ARGV, and quotes with `printf %q` on the `sg` branch.  It is the
#      form that was always correct; run_in_container() below now uses the same form.
# ---------------------------------------------------------------------------------------
docker_q(){
  if [ "$DOCKER_BRANCH" = "bare" ]; then command docker "$@"; return $?; fi
  local q; q=$(printf ' %q' "$@")
  sg docker -c "docker$q"
}

# ---------------------------------------------------------------------------------------
# AMENDMENT 12 ITEM 28 -- REPAIRED HERE.  THE DEFECT, STATED EXACTLY.
#
# The frozen driver built its container call as `$DRUN "docker run ..."`.  On the `sg` branch
# ($DRUN = `sg docker -c`) that is correct: the string is one shell command for `sg` to run.
# On the BARE branch ($DRUN = `docker`) it expands to `docker "docker run ..."` -- the whole
# command as a SINGLE ARGUMENT to the docker client.  MEASURED with the exact expansion:
# rc 1, `docker: unknown command: docker docker run ...`.  Control, same string through
# `sg docker -c`: rc 0, `INSIDE_OK`.
#
# WHY IT SURVIVED: `BARE_RC` is 0 on this box, so the driver was correct ONLY on the branch
# this box does NOT take.  The live branch had never been exercised.
# WHAT IT DID NOT DO: it failed CLOSED -- run_in_container aborts at exit 6 on a non-zero
# inner rc -- so no step was ever silently mis-run and no artifact was ever produced by an
# invocation this driver did not intend.
#
# THE REPAIR, correct on BOTH branches, MEASURED on the pinned digest:
#   bare : timeout ...s "$DOCKER_BIN" "$@"                      -> rc 0 / INSIDE_OK
#   sg   : timeout ...s sg docker -c "docker$(printf ' %q' ...)" -> rc 0 / INSIDE_OK
# The argv form cannot be mis-quoted because nothing re-parses it; the `sg` form is quoted by
# `printf %q`, exactly as docker_q() above already was.
#
# 🔴 STRUCK BY QUOTE, 2026-09-04, ITEM 39: ~~"THE CAP SURVIVES THE REPAIR, and this was
# measured rather than assumed: a container sleeping 30 s under a 5 s cap returns rc 124 on
# BOTH branches, so run_in_container's `rc -eq 124 -> abort ... 6` overrun path (rule 12, AN
# OVERRUN STOPS THE RUN) still fires."~~
# THE rc IS RIGHT AND THE INFERENCE IS WRONG.  rc 124 ARRIVES, but only AFTER the container has
# run to completion -- MEASURED: a 3 s cap on a 60 s container returned rc 124 after 61 WALL
# SECONDS, and under an UNBOUNDED payload the wrapper NEVER RETURNED AT ALL (the container was
# still `Up` four minutes later at 100.45 % CPU).  A branch that fires after the spend REPORTS
# an overrun; it does not STOP one, and `B5c`'s cap is 1,630 core-min.
#
# ITEM 39 REPAIRED HERE (2026-09-04).  THE GRACE BETWEEN `timeout`'s SIGTERM AND ITS SIGKILL.
# `timeout` SIGTERMs the docker CLIENT; the client proxies to the container's `bash -c`, which
# is waiting on a foreground child and does not act; `timeout` THEN WAITS.  `-k` is what makes
# the CLIENT return; the UNCONDITIONAL `docker kill` in run_in_container() is what ends the
# CONTAINER.  NEITHER LIMB ALONE IS A CAP.
# ---------------------------------------------------------------------------------------
CAP_KILL_GRACE_S=5

docker_timeout_q(){
  local tmo="$1"; shift
  if [ "$DOCKER_BRANCH" = "bare" ]; then
    timeout -k "${CAP_KILL_GRACE_S}"s "${tmo}"s "$DOCKER_BIN" "$@"
    return $?
  fi
  local q
  q=$(printf ' %q' "$@")
  timeout -k "${CAP_KILL_GRACE_S}"s "${tmo}"s sg docker -c "docker$q"
  return $?
}

T0P=$(date +%s)
RESOLVED_DIGEST=$(docker_q inspect --format '{{.Id}}' "$IMG" 2>/dev/null)
[ -n "$RESOLVED_DIGEST" ] \
  || abort "the image '$IMG' does not resolve to a digest on this daemon. An unresolvable image is a REFUSAL, never a fallback to whatever else is on the box (Amendment 12 Ruling 1)." 7
[ "$RESOLVED_DIGEST" = "$M6SR_PINNED_IMAGE_DIGEST" ] \
  || abort "IMAGE DIGEST MISMATCH. '$IMG' resolves to $RESOLVED_DIGEST; the registration pins $M6SR_PINNED_IMAGE_DIGEST ($M6SR_PINNED_IMAGE_REF). \$M6SR_IMAGE may NAME an image; it may not SELECT one. Every version-dependent finding in this registration -- the div(phi,Ekp) term, the turbulenceProperties/RASModel spelling, solverInfo-vs-residuals -- was measured INSIDE the pinned image and is worth nothing under a different one. REFUSED AT ZERO SOLVER COST." 7

# The container is henceforth addressed BY DIGEST, never by the tag.  A tag can be re-pointed
# between this check and the run; a digest cannot.  Verified on this daemon that `docker run`
# accepts a bare digest (rc 0) and rejects an unknown one (rc 125).
IMG_PINNED="$M6SR_PINNED_IMAGE_DIGEST"

# ---- THE INSTRUMENT ITSELF, not merely its wrapper.  The pinned image carries THREE
#      `rhoSimpleFoam` binaries; only one of them is the registered one.
PROBE_OUT=$(docker_q run --rm -u 1002:1002 "$IMG_PINNED" bash -lc 'set +u; source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; B=$(command -v rhoSimpleFoam); printf "VER=%s\nBIN=%s\nSHA=%s\nAPI=%s\n" "$WM_PROJECT_VERSION" "$B" "$(sha256sum "$B" 2>/dev/null | cut -d" " -f1)" "$(cat "$WM_PROJECT_DIR/META-INFO/api-info" 2>/dev/null | tr "\n" ";")"' 2>&1)
PROBE_RC=$?
P_VER=$(printf '%s\n' "$PROBE_OUT" | sed -n 's/^VER=//p')
P_BIN=$(printf '%s\n' "$PROBE_OUT" | sed -n 's/^BIN=//p')
P_SHA=$(printf '%s\n' "$PROBE_OUT" | sed -n 's/^SHA=//p')
P_API=$(printf '%s\n' "$PROBE_OUT" | sed -n 's/^API=//p')
T1P=$(date +%s)
echo "$((T1P-T0P))" > "$CASE/WALL_B5p.txt"

[ "$PROBE_RC" -eq 0 ] && [ -n "$P_VER" ] && [ -n "$P_BIN" ] && [ -n "$P_SHA" ] \
  || abort "the solver probe inside the pinned image failed (rc $PROBE_RC). A probe that returns nothing is a REFUSAL, never an assumption that the right binary is there. Output: $PROBE_OUT" 7
[ "$P_VER" = "$M6SR_PINNED_OF_VERSION" ] \
  || abort "OPENFOAM VERSION MISMATCH: the image reports WM_PROJECT_VERSION='$P_VER'; the registration pins '$M6SR_PINNED_OF_VERSION'. REFUSED." 7
[ "$P_BIN" = "$M6SR_PINNED_SOLVER_PATH" ] \
  || abort "SOLVER BINARY PATH MISMATCH: PATH resolves rhoSimpleFoam to '$P_BIN'; the registration pins '$M6SR_PINNED_SOLVER_PATH'. The pinned image also carries OpenFOAM-AD's ADF and ADR builds of a binary with the SAME NAME, so a path this driver did not expect is a DIFFERENT SOLVER wearing the right name. REFUSED." 7
[ "$P_SHA" = "$M6SR_PINNED_SOLVER_SHA256" ] \
  || abort "SOLVER BINARY sha256 MISMATCH at the pinned path: read $P_SHA, pinned $M6SR_PINNED_SOLVER_SHA256. REFUSED." 7

{ echo "{"
  echo "  \"pinned_by\": \"M6SR_PREREGISTRATION.md Section 18 (Amendment 12, Ruling 1)\","
  echo "  \"image_ref_named\": \"$IMG\","
  echo "  \"image_ref_pinned\": \"$M6SR_PINNED_IMAGE_REF\","
  echo "  \"image_digest_resolved\": \"$RESOLVED_DIGEST\","
  echo "  \"image_digest_pinned\": \"$M6SR_PINNED_IMAGE_DIGEST\","
  echo "  \"digest_kind\": \"OCI image manifest digest, read as docker inspect .Id; NOT corroborated against a registry\","
  echo "  \"openfoam_fork\": \"$M6SR_PINNED_OF_FORK\","
  echo "  \"openfoam_version\": \"$P_VER\","
  echo "  \"openfoam_api_info\": \"$P_API\","
  echo "  \"solver_binary\": \"$P_BIN\","
  echo "  \"solver_binary_sha256\": \"$P_SHA\","
  echo "  \"container_run_target\": \"the DIGEST, never the tag -- a tag can be re-pointed between the check and the run\","
  echo "  \"B5p_preflight_wall_s\": $((T1P-T0P)),"
  echo "  \"B5p_UNBUDGETED\": \"Section 2.4's cost table has no row for a pin preflight. It is REPORTED ON ITS OWN LINE at 1 rank and is NOT folded into any registered row and NOT absorbed into any ratio (Section 9.3).\""
  echo "}"; } > "$CASE/SOLVER_PIN.json"
say "solver pin VERIFIED: $M6SR_PINNED_OF_VERSION at $P_BIN (sha256 ${P_SHA:0:16}...), image $RESOLVED_DIGEST"
say "  step B5p (pin preflight): $((T1P-T0P)) wall s at 1 rank -- UNBUDGETED in Section 2.4, reported on its own line"

# ---------------------------------------------------------------------------------------
# 1c.  AMENDMENT 12 -- THE GRADING PATH IS REHEARSED BEFORE THE RUN IS PAID FOR.
#
#      The defect this closes, stated exactly: this driver already refuses on the CASE
#      WRITER's --selftest, but nothing here ever ran the COMPARATOR's --controls.  So a
#      comparator refusal blocked GRADING and not the LAUNCH, and B5a+B5b+B5c -- 607.63 of
#      Section 2.4's 615.24 core-min, 98.8 % of the ladder -- could be spent in full and
#      then be ungradable.  It is the SOLVER_RC class again and it has the same fix:
#      rehearse the grading path before spending on the run.
#
#      SCOPE, NAMED SO NO READER HAS TO INFER IT: this gate guards the phases that reach the
#      SOLVER (`solve`, `all`).  Phase `stage` alone is NOT gated -- it runs checkMesh, which
#      is not a solver, and gating it would leave Gate A with no log at all to read.  Both
#      interpreters are run because Section 9.2 binds every comparator to `python3 -O`
#      parity, and a gate that only holds under one flag is one flag from absent (L-475).
# ---------------------------------------------------------------------------------------
if [ "$PHASE" = "solve" ] || [ "$PHASE" = "all" ]; then
  T0G=$(date +%s)
  python3    "$CASES/analyse_m6sr.py" --controls > "$CASE/log.comparator_controls"    2>&1; CRC=$?
  python3 -O "$CASES/analyse_m6sr.py" --controls > "$CASE/log.comparator_controls_O" 2>&1; CRC_O=$?
  T1G=$(date +%s)
  echo "$((T1G-T0G))" > "$CASE/WALL_B5g.txt"
  say "grading-path rehearsal: analyse_m6sr.py --controls rc=$CRC (python3) / rc=$CRC_O (python3 -O), $((T1G-T0G)) wall s at 1 rank -- step B5g, UNBUDGETED in Section 2.4"
  [ "$CRC" -eq "$CRC_O" ] \
    || abort "the comparator's controls return rc $CRC under python3 and rc $CRC_O under python3 -O. Section 9.2 requires byte-identical refusals under both; a grading path that changes with an interpreter flag is not a frozen grading path (L-475, L-332). REFUSED AT ZERO SOLVER COST." 8
  [ "$CRC" -eq 0 ] \
    || abort "the GRADING path's planted controls did not pass (rc $CRC; see $CASE/log.comparator_controls). A solve launched now would spend up to $CAP_B5 core-min at this level and then be UNGRADABLE -- 607.63 of Section 2.4's 615.24 core-min across the ladder. A zero from a reader not shown able to see a non-zero is not evidence (rule 3), and neither is a PASS. REFUSED AT ZERO SOLVER COST." 8
  say "grading-path rehearsal: ALL REGISTERED CONTROLS PASSED under both interpreters"
fi

# ---------------------------------------------------------------------------------------
# 1d.  AMENDMENT 12 -- THE RUN ROOT IS PINNED TOO.  Item 29: `M6SR_RUN_ROOT` is a SECOND,
#      INDEPENDENT env-var divergence of exactly item 26's class.  This driver honours it;
#      cases/M6SR/analyse_m6sr.py reads NO environment at all (its REPO is derived from
#      __file__ and it takes --run-root), so an operator who exports M6SR_RUN_ROOT without
#      passing a matching --run-root sends the PRODUCER and the READER to different trees.
#      It fails closed -- the comparator finds no case and refuses -- but a pin that only
#      holds because the other side happens to refuse is not a pin.
#
#      WHY THIS CHECK IS ORDERED LAST OF THE THREE, STATED SO IT READS AS A CHOICE AND NOT
#      AN OVERSIGHT: all three refusals above are at ZERO SOLVER COST and precede `stage`,
#      so their order is free.  Placed FIRST, this one would make the image pin and the
#      grading-path rehearsal UNREHEARSABLE anywhere except inside
#      verification/runs/M6SR_runs/, the directory whose ABSENCE is this registration's own
#      rule-2 freeze proof.  Placed last, every new refusal above it can be exercised in a
#      scratch tree and this one then stops the run before a single core-minute is spent.
# ---------------------------------------------------------------------------------------
M6SR_REGISTERED_RUN_ROOT=/home/ubuntu/Certonomous/verification/runs/M6SR_runs
echo "$RR" > "$CASE/RUN_ROOT_USED.txt"
[ "$RR" = "$M6SR_REGISTERED_RUN_ROOT" ] \
  || abort "RUN ROOT MISMATCH: this driver was pointed at '$RR' (via \$M6SR_RUN_ROOT); Section 9's frozen path table registers '$M6SR_REGISTERED_RUN_ROOT'. The comparator reads NO environment and defaults to the registered path, so a solve written here would be graded from THERE -- producer and reader in different trees. An export without a matching --run-root is a REFUSAL, not a grade. REFUSED AT ZERO SOLVER COST." 9

# ---------------------------------------------------------------------------------------
# 2.  THE CONTAINER WRAPPER.  rc IS CAPTURED INSIDE (Section 9.2) -- `setsid timeout cmd`
#     exits 0 for every outcome, so an rc taken from around the wrapper line is meaningless.
#     🔴 STRUCK BY QUOTE, 2026-09-04, ITEM 39 REPAIR: ~~"The cap is enforced by `timeout` and
#     AN OVERRUN STOPS THE RUN."~~  MEASURED FALSE as written -- `timeout` alone REPORTED an
#     overrun after the fact and never stopped one.  The cap is now enforced by THREE limbs
#     together: `timeout -k` on the client, an UNCONDITIONAL `docker kill` on the recorded
#     container name, and an overrun branch accepting 137 as well as 124.  An overrun now
#     stops the run -- including `B5c`'s 1,630 core-min row.
# ---------------------------------------------------------------------------------------
run_in_container(){
  local tag="$1" tmo="$2" ranks="$3" cmd="$4"
  local t0 t1 rc wall inner wdir wlog cname
  # ITEM 32 (registration item 34) REPAIRED: THE WRAPPER'S LOG LEAVES THE BIND MOUNT.
  # The container sees exactly one host path -- $CASE, mounted at /case, below.  A wrapper log
  # OUTSIDE $CASE therefore cannot be opened from inside the container by ANY name, so the
  # host's fd and the inner command's fd can never address one inode.  This is topology, not
  # naming: it holds for every present and future tag, including tag == checkMesh.
  wdir="$RR/_wrapper_logs/$LEVEL"
  wlog="$wdir/log.$tag"
  # AND IT IS ENFORCED, not merely intended.  If a later edit ever puts the wrapper log back
  # inside the mount this REFUSES before the container starts, rather than producing a
  # plausible, gradeable, head-corrupted artifact.  `$CASE` is the literal -v source below, so
  # this tests the mount and not a copy of it.
  case "$wlog" in
    "$CASE"|"$CASE"/*)
      abort "the wrapper log '$wlog' is INSIDE the bind mount '$CASE'. The host holds that fd at offset 0 for the life of the docker client while the container writes the same inode through the mount, so a client write lands at offset 0 and overwrites the HEAD of the file. For tag 'checkMesh' that file is the artifact Gate A grades, and a head-corrupted checkMesh log reads CLEAN (measured: state=READ with all three maxima parseable), not ABSENT. REFUSED before the container is started." 6 ;;
  esac
  mkdir -p "$wdir" || abort "could not create the wrapper-log directory $wdir. The wrapper's output has nowhere to go that is outside the bind mount, and this driver does NOT fall back to a path inside it (item 32/34)." 6
  # THE CONTAINER NAME IS BOUND TO A VARIABLE AND RECORDED BEFORE THE RUN (item 39), because
  # the kill below must be able to aim at it WITHOUT having to trust anything the client
  # returned.  The name is written OUTSIDE the bind mount, beside the wrapper log, for the
  # same item-32/34 reason that log lives there.
  cname="m6sr_${tag}_$$"
  echo "$cname" > "$wdir/CONTAINER_NAME.$tag"
  t0=$(date +%s)
  # ITEM 28 REPAIRED: argv, through docker_timeout_q, correct on BOTH branches.
  # ITEM 30 REPAIRED: `-u 1002:1002` is UNCHANGED -- the container keeps dafoamuser as its
  # primary identity, so every Amendment 12 pin measurement taken under that user still
  # describes the running process -- and it gains exactly ONE supplementary group, the host
  # group that already owns $CASE.  See Section 3's `chmod g+rwX`, which is the other half.
  docker_timeout_q "$tmo" run --rm --name "$cname" -u 1002:1002 \
      --group-add "$HOST_GID" \
      -v "$CASE":/case -w /case "$IMG_PINNED" \
      bash -c "set +u; source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; $cmd; echo \"WRAPPER_RC=\$?\" > RC_${tag}.txt" \
      > "$wlog" 2>&1
  rc=$?
  t1=$(date +%s); wall=$((t1-t0))
  # ⚠ THE KILL IS UNCONDITIONAL, AND THAT IS THE WHOLE POINT.  It is NOT guarded by the rc,
  # because the entire item-39 finding is that THE CLIENT'S RETURN TELLS YOU NOTHING ABOUT THE
  # CONTAINER: a client killed by `timeout -k` returns while its container is still `Up` at
  # 100 % CPU.  `kill` then `rm -f`, both on the RECORDED name, both rc-ignored -- on the happy
  # path `--rm` has already reaped the container and both are harmless no-ops.  At L1 the
  # container behind this name holds 16 ranks on a 1.59744 Mcell solve.
  docker_q kill "$cname" >/dev/null 2>&1
  docker_q rm -f "$cname" >/dev/null 2>&1
  # THE INNER rc, read from the file the wrapper wrote, BY EXPLICIT PATH -- never from $?
  # around the timeout line, and never by `grep log.* | tail -1`.
  inner="ABSENT"
  [ -f "$CASE/RC_${tag}.txt" ] && inner=$(cut -d= -f2 "$CASE/RC_${tag}.txt")
  # THE BRANCH IS RECORDED PER STEP, not only once in the preflight: item 28 was a defect
  # that lived on exactly one branch, so a step's rc is not readable without knowing which
  # invocation produced it.
  echo "$tag outer_rc=$rc inner_rc=$inner wall_s=$wall timeout_s=$tmo grace_s=$CAP_KILL_GRACE_S container=$cname ranks=$ranks docker_branch=$DOCKER_BRANCH container_user=1002:1002+g$HOST_GID wrapper_log=$wlog" \
      >> "$CASE/STEP_RC.txt"
  echo "$wall" > "$CASE/WALL_${tag}.txt"
  echo "$inner" > "$CASE/INNER_RC_${tag}.txt"
  say "$tag: outer rc=$rc  INNER rc=$inner  wall=${wall}s  cap=${tmo}s  ranks=$ranks"
  # WHICH rcs MEAN AN OVERRUN, AND WHAT EACH ONE MEANS -- stated here because item 28/35 was
  # exactly the failure of an rc that was not 124 not reading as a cap overrun:
  #   124 = `timeout` reached the cap, sent SIGTERM, and the docker client EXITED ON IT.
  #   137 = 128+9.  The client did NOT exit on SIGTERM, so `timeout -k` SIGKILLed it at
  #         cap+grace.  ⚠ THIS IS THE NORMAL rc FOR A CONTAINERISED OVERRUN ON THIS BOX --
  #         measured: `timeout -k 5s 3s` on a 120 s container returned in 8 s with rc 137,
  #         NOT 124.  A branch testing only 124 MISSES EVERY REAL OVERRUN and falls through
  #         to the inner-rc check, aborting at exit 6 with a misleading cause.
  # ⚠ HONEST AMBIGUITY, NOT PAPERED OVER: 137 can ALSO be a SIGKILL from elsewhere (an OOM
  # kill of the client) rather than from `-k`.  Both readings STOP THE RUN, so this branch is
  # safe either way, and `wall` vs `cap` is printed so a reader can tell them apart: a cap
  # overrun has wall >= cap, a foreign SIGKILL has wall << cap.
  if [ "$rc" -eq 124 ] || [ "$rc" -eq 137 ]; then
    abort "$tag hit its cap of ${tmo} wall s at $ranks ranks (outer rc=$rc after ${wall}s; 124=client exited on SIGTERM at the cap, 137=client SIGKILLed by 'timeout -k' at cap+${CAP_KILL_GRACE_S}s). The container '$cname' was killed unconditionally. AN OVERRUN STOPS THE RUN. It does not get a new budget (rule 12)." 6
  fi
  [ "$inner" = "0" ] || abort "$tag inner rc=$inner (outer $rc). A non-zero rc inside the container is a FAILED STEP, whatever the outer wrapper returned." 6
}

# ---------------------------------------------------------------------------------------
# 3.  PHASE `stage` -- the mesh into the run root, its published hash, and B4's checkMesh.
#
#     CHOICE CH12 (recorded in CASE_PROVENANCE.json): the mesh is COPIED in.  L3's and L2's
#     meshes live under $CR, which is READ ONLY, and a solver writes into its own case.  The
#     comparator's _discover_levels() already rules for exactly this: "An in-run-root copy,
#     once it exists, SUPERSEDES the read-only source."
#
#     SUPERVISOR ITEM, REPORTED AND NOT ABSORBED: Section 2.4's cost table has NO ROW for
#     staging L3's and L2's pre-existing meshes into the run root.  B3 covers the L1 build
#     only.  The staging cost is measured and reported below on its own line as `B3s`; it is
#     NOT folded into any registered row and it is NOT absorbed into a ratio (Section 9.3).
# ---------------------------------------------------------------------------------------
if [ "$PHASE" = "stage" ] || [ "$PHASE" = "all" ]; then
  if [ -d "$CASE/constant/polyMesh" ]; then
    say "stage: $CASE/constant/polyMesh already present; NOT overwritten"
  else
    [ -d "$MESH_SRC" ] || abort "the level's mesh source is ABSENT: $MESH_SRC. An absent mesh is a REFUSAL, never an empty level. (L1's mesh is built by cases/M6SR/build_m6sr_l1.sh -- run B1/B2/B3 first.)" 3
    T0S=$(date +%s)
    mkdir -p "$CASE/constant" || abort "could not create $CASE/constant" 3
    cp -a -- "$MESH_SRC" "$CASE/constant/polyMesh" || abort "mesh copy-out of $MESH_SRC failed" 3
    T1S=$(date +%s)
    echo "$((T1S-T0S))" > "$CASE/WALL_stage.txt"
    say "stage: copied $MESH_SRC -> $CASE/constant/polyMesh in $((T1S-T0S))s (step B3s, UNBUDGETED in Section 2.4)"
  fi

  # The points-stream sha, PUBLISHED here so Gate A's family-identity proof reads the same
  # bytes at the copy that it would have read at the source.  Hashed on the DECOMPRESSED
  # stream (Section 1.4): a gzip hash also encodes the compressor's settings and mtime.
  PSHA=$(python3 -c "
import sys
sys.path.insert(0, '$CASES')
import analyse_m6sr as A
print(A.points_stream_sha('$CASE/constant/polyMesh'))
" 2>"$CASE/log.pointshash.err")
  [ -n "$PSHA" ] || abort "could not compute the decompressed points-stream sha of $CASE/constant/polyMesh (see $CASE/log.pointshash.err). A missing hash is a REFUSAL, never a fallback." 3
  echo "$PSHA" > "$CASE/points_stream.sha256"
  say "stage: points-stream sha256 $PSHA  -- PUBLISHED for Gate A item A5"

  # ---------------------------------------------------------------------------------------
  # AMENDMENT 12 ITEM 30 -- REPAIRED HERE, AND NOT WITH `chmod 777`.
  #
  # THE DEFECT, STATED EXACTLY.  `mkdir -p "$CASE"` above runs as the HOST user (MEASURED:
  # uid 1000 gid 1000, umask 0002 -> mode 775 ubuntu:ubuntu) and the container runs
  # `-u 1002:1002` (MEASURED: dafoamuser inside the pinned image).  Neither the uid nor the
  # gid matches, so the container held only `other` = r-x on the case directory.  MEASURED on
  # the pinned digest with this driver's own mount: `bash: log.checkMesh: Permission denied`,
  # inner rc 1, log.checkMesh ABSENT.  The frozen driver's `chmod -R 777 "$CASE"` sits in the
  # SOLVE phase (Section 4), AFTER this step, so it could never help B4.
  #
  # IT WAS MASKED BY ITEM 28 AND IS INDEPENDENT OF IT.  Repairing item 28 alone would have
  # let the launch path get further and then fail here, and the next reader would have been
  # debugging a "new" bug that was present all along.  Both are repaired in one pass for
  # that reason.
  #
  # WHY NOT `chmod 777`.  A NARROWER FIX WAS MEASURED TO WORK, so the blunt one is not taken.
  # The repair is two halves, and NEITHER HALF WORKS ALONE -- both were measured as negative
  # controls against the real pinned image:
  #   (i)  `chmod g+rwX "$CASE"` -- THE CASE DIRECTORY ONLY.  Group only, NOT world; NOT
  #        recursive.  Set EXPLICITLY rather than inherited: this box's umask 0002 already
  #        yields 775, but under a 022 umask `mkdir -p` yields 755 and the group bit would be
  #        absent, so a fix resting on the umask would be a fix resting on an accident.
  #        MEASURED without half (ii): Permission denied.
  #   (ii) `--group-add $HOST_GID` on the container (in run_in_container above).  uid 1002
  #        keeps dafoamuser as its PRIMARY identity, so nothing measured under `-u 1002:1002`
  #        for the Amendment 12 pin is invalidated; it gains exactly one supplementary group,
  #        the one that already owns this directory.  MEASURED without half (i), on a 755
  #        directory: Permission denied.
  # WITH BOTH: inner rc 0 and a 3330-byte log.checkMesh ending `Mesh OK.` / `End`, carrying
  # the named numeric maxima Gate A reads.  `constant/polyMesh` is NOT touched -- it arrives
  # world-readable from `cp -a` and checkMesh only READS it, which was measured too.
  #
  # THE SOLVE-PHASE `chmod -R 777` IS NEITHER MOVED NOR REMOVED.  Section 4's later steps
  # (decomposePar, the solver, reconstructPar) write processor*/ and time directories and are
  # outside this repair.  HONEST CONSEQUENCE, RECORDED RATHER THAN DISCOVERED: once this step
  # succeeds, log.checkMesh and RC_checkMesh.txt are owned 1002:1002, so the later
  # `chmod -R 777` cannot chmod those two files and will silently skip them (its stderr is
  # already discarded).  Nothing re-writes either file -- the guard below skips checkMesh
  # when its log exists, and the solve step writes RC_<STEP>.txt under a different name -- so
  # this has no functional effect, but it is stated so no reader has to rediscover it.
  # ---------------------------------------------------------------------------------------
  chmod g+rwX "$CASE" 2>/dev/null
  CASE_GRP_OK=$(python3 -c "
import os, stat, sys
m = os.stat('$CASE').st_mode
sys.stdout.write('1' if (m & stat.S_IWGRP) and (m & stat.S_IXGRP) else '0')
" 2>/dev/null)
  [ "$CASE_GRP_OK" = "1" ] \
    || abort "$CASE is not group-writable+searchable after chmod g+rwX (mode $(stat -c '%a' "$CASE" 2>/dev/null), owner $(stat -c '%u:%g' "$CASE" 2>/dev/null)). The container runs as uid 1002 with supplementary group $HOST_GID and would fail to write log.checkMesh -- Gate A reads NAMED NUMERIC MAXIMA off that file and an absent one reads ABSENT, never clean. REFUSED before the container is started, rather than after it fails." 6
  { echo "case_dir_mode=$(stat -c '%a' "$CASE" 2>/dev/null)"
    echo "case_dir_owner=$(stat -c '%u:%g' "$CASE" 2>/dev/null)"
    echo "container_user=1002:1002"
    echo "container_supplementary_group=$HOST_GID"
    echo "fix=chmod g+rwX on the case dir ONLY (not 777, not recursive) + --group-add"; } \
    > "$CASE/CASE_PERMISSIONS.txt"
  say "B4 preflight: $CASE mode $(stat -c '%a' "$CASE" 2>/dev/null), container uid 1002 + supplementary group $HOST_GID (item 30 repair; NOT chmod 777)"

  # ---- B4's checkMesh.  Section 2.4 gives ONE row (cap 2.0 core-min) for "checkMesh x3",
  # so the cap is a RUNNING budget across the three levels, tracked on disk.
  if [ -f "$CASE/log.checkMesh" ]; then
    say "stage: $CASE/log.checkMesh already present; checkMesh NOT re-run"
  else
    SPENT=$(cat "$B4_LEDGER" 2>/dev/null); [ -n "$SPENT" ] || SPENT=0
    TMO_B4=$(python3 -c "
rem = $CAP_B4_TOTAL - $SPENT
print(int(rem * 60) if rem > 0 else 0)")
    [ "$TMO_B4" -gt 0 ] || abort "B4's registered cap of $CAP_B4_TOTAL core-min is EXHAUSTED ($SPENT core-min already spent across levels). AN OVERRUN STOPS THE RUN; it does not get a new budget (rule 12)." 6
    say "B4: checkMesh, remaining budget $(python3 -c "print(round($CAP_B4_TOTAL - $SPENT, 4))") core-min -> ${TMO_B4}s at 1 rank"
    run_in_container checkMesh "$TMO_B4" 1 "checkMesh -constant > log.checkMesh 2>&1"
    W4=$(cat "$CASE/WALL_checkMesh.txt" 2>/dev/null || echo 0)
    python3 -c "
spent = $SPENT + $W4 * 1 / 60.0
open('$B4_LEDGER', 'w').write('%.6f\n' % spent)
print('B4 ledger: %.6f core-min spent of $CAP_B4_TOTAL' % spent)"
    [ -s "$CASE/log.checkMesh" ] || abort "checkMesh produced no log.checkMesh. Gate A reads NAMED NUMERIC MAXIMA off that file; an absent checkMesh log reads ABSENT and NEVER reads clean (Section 5, L-459)." 6
    # ---- ITEM 32 (registration item 34), SECOND AND INDEPENDENT GUARD: THE HEAD OF THE
    # GRADED ARTIFACT.  The first guard is topological (the wrapper log is outside the mount);
    # this one reads the file that was actually produced.  It exists because the failure mode
    # is a HEAD overwrite that leaves the maxima near the END intact -- "the numbers parsed"
    # is exactly what would let a corrupted log through, so the numbers are not the check.
    # MEASURED both ways on the pinned digest: a clean log begins `/*-` (the OpenFOAM banner);
    # the same log under the shared-path shape began `CLIENT_NOISE_LINE_X` and still returned
    # every maximum Gate A reads.  Safe as a check only because the image is pinned by digest,
    # which fixes the banner; an unpinned image would make this a guess.
    CM_HEAD=$(head -c 3 "$CASE/log.checkMesh" 2>/dev/null)
    [ "$CM_HEAD" = "/*-" ] \
      || abort "$CASE/log.checkMesh does not begin with the OpenFOAM banner (first 3 bytes read '${CM_HEAD:-<nothing>}'). checkMesh under the pinned digest ALWAYS opens with '/*-'. Some other writer reached the head of a GRADED artifact. Gate A's maxima live near the END of this file and would still parse, so this refuses on the HEAD and not on the numbers: a head-corrupted checkMesh log reads CLEAN, and that is worse than absent. REFUSED." 6
  fi
fi

[ "$PHASE" = "stage" ] && { say "stage complete for $LEVEL. THIS DRIVER GRADES NOTHING."; exit 0; }

# ---------------------------------------------------------------------------------------
# 4.  PHASE `solve` -- Section 8's case files, then $STEP.
# ---------------------------------------------------------------------------------------
[ -d "$CASE/constant/polyMesh" ] || abort "$CASE/constant/polyMesh is ABSENT; run phase 'stage' first." 3

# ---------------------------------------------------------------------------------------
# 4a.  STEP `B4s` -- SECTION 7's ILL-POSEDNESS SCREEN, ON THE LAUNCH PATH.
#      AMENDMENT 20, ITEM 47, ON THE SUPERVISOR'S EXPRESS RULING.
#
#      THE DEFECT THIS CLOSES, STATED EXACTLY.  Section 7 calls itself "THE ONE THING THAT
#      BLOCKS", says its five conditions are "Checked per level BEFORE launch" and that a
#      failure "BLOCKEDs the level".  Until this amendment THIS DRIVER NEVER ASKED GATE A
#      ANYTHING: it invoked cases/M6SR/analyse_m6sr.py exactly twice, at the grading-path
#      rehearsal above, BOTH TIMES as `--controls`, and never once as `--gate-a`.  Amendment
#      19 wired conditions 2-5 into gate_a() and made them GRADEABLE.  It did not make them
#      BLOCK A LAUNCH.  A supervisor ordering a launch on the strength of Section 7 would
#      have been relying on a screen the launcher does not run.  THE SUPERVISOR'S RULING:
#      "Section 7's screen must be consulted BY THE LAUNCH PATH, and a BLOCKED Gate A must
#      REFUSE the solve."
#
#      WHY HERE AND NOWHERE ELSE.  Section 7's conditions are read from checkMesh output and
#      from the boundary file, so the screen can only run AFTER B4's checkMesh has produced
#      `log.checkMesh` -- which is why this sits below the `stage` exit and not above it.
#      It sits ABOVE the case writer, so a BLOCKED level costs not even the case files.
#      Phase `stage` alone is deliberately NOT gated: gating it would leave the screen with
#      no checkMesh log to read, which is the same reasoning Amendment 12 recorded for the
#      grading-path rehearsal.
#
#      WHY A PER-LEVEL SCREEN AND NOT `--gate-a`.  `--gate-a` grades the FAMILY -- A4 needs
#      the exact registered cell triple, A5 three distinct points streams, A6 the ratio at
#      every level.  This driver runs ONE LEVEL AT A TIME, so `--gate-a` here would fail
#      family clauses that say nothing about well-posedness and would refuse a LAWFUL
#      launch.  Section 7's own words are "Checked PER LEVEL"; `--section7-screen` is that,
#      and it calls the SAME functions gate_a() calls (control C30 drives both paths on one
#      level and requires them to agree clause for clause).
#
#      THE EXIT CODES ARE DISTINCT, AND THE TWO FINDINGS ARE NOT CONFLATED.
#        exit 11  the LEVEL is BLOCKED -- a statement about the mesh.  The message NAMES the
#                 clause and its measured value against its threshold; it is never a bare
#                 verdict string.
#        exit 12  the comparator REFUSED (its rc 2), or returned an rc this driver does not
#                 recognise, or was killed by the cap below.  A REFUSAL is a statement about
#                 THIS DOCUMENT or THE INSTRUMENT -- an unregistered level, a createPatchDict
#                 that moved off its pin, an absent mesh -- and it is REPORTED AS A REFUSAL
#                 AND NEVER CONVERTED INTO `BLOCKED`.
#      STANDING RULE 5's ONE-WAY DOOR: this screen can only turn a launch OFF.  There is no
#      branch below in which anything other than rc 0 lets the solve proceed.
#
#      🔴 THE CONTAINER-CAP CLASS (ITEM 39) CANNOT DEFEAT THIS, AND THE REASON IS STRUCTURAL.
#      Item 39 measured that an outer `timeout` does NOT bound a container: the docker client
#      returns while the container it started keeps running under dockerd, outside the
#      timeout's process group.  THIS SCREEN STARTS NO CONTAINER.  It is a host `python3`
#      reading two files, so it is an ordinary child in this shell's own process group and
#      `timeout -k` does bound it.  `cases/M6SR/check_m6sr_launch_path.sh` asserts on the
#      EXTRACTED TEXT of this function that it contains no `docker` token and no
#      `run_in_container` call, so the claim is machine-checked and not merely written here.
#      And the failure direction is closed either way: a timeout returns 124/137, which is
#      not 0, and the `*)` branch below refuses the launch.
# ---------------------------------------------------------------------------------------
section7_launch_screen(){
  local lvl="$1" case_dir="$2" out rc blk
  out="$case_dir/log.section7_screen"
  timeout -k 5 120 python3 "$CASES/analyse_m6sr.py" --section7-screen \
      --level "$lvl" --case "$case_dir" > "$out" 2>&1
  rc=$?
  case "$rc" in
    0)
      say "B4s: SECTION 7 SCREEN PASSED for $lvl -- all five conditions, per level, BEFORE the solve (see $out)"
      ;;
    11)
      blk=$(grep '^SECTION7_BLOCKED_CLAUSE:' "$out" 2>/dev/null | tr '\n' ' ')
      [ -n "$blk" ] || blk="(the comparator returned 11 but printed no clause line; treated as BLOCKED regardless -- an unreadable refusal is still a refusal)"
      abort "SECTION 7 SCREEN: $lvl is BLOCKED and the solve WILL NOT START. Section 7 is the one thing that blocks and its conditions are checked per level BEFORE launch. THE CLAUSE(S) THAT BLOCKED, WITH THE MEASURED VALUE AGAINST THE THRESHOLD: $blk Full record: $out. A BLOCKED level is not a GATE FAIL and is not softened: the mesh cannot be shown well-posed, so nothing is spent on solving it." 11
      ;;
    2)
      abort "SECTION 7 SCREEN: the comparator REFUSED (exit 2) for $lvl. A REFUSAL IS NOT A 'BLOCKED' AND IS NOT REPORTED AS ONE -- BLOCKED is a statement about the MESH, a refusal is a statement about THIS DOCUMENT or THIS INSTRUMENT (an unregistered level, a createPatchDict that moved off its pinned sha256, an absent mesh). Standing rule 5's direction applies: this screen may only turn a launch OFF, never manufacture a pass, so the refusal STOPS the launch. See $out. THE FIX IS AN AMENDMENT or a repair to the instrument, never a weaker screen." 12
      ;;
    124|137)
      abort "SECTION 7 SCREEN: the screen was killed by its own 120 s cap (rc $rc) for $lvl. It is a host python3 process, not a container, so the cap DOES bind it (item 39's finding is about containers). A screen that did not finish has not passed, and this REFUSES the launch. See $out." 12
      ;;
    *)
      abort "SECTION 7 SCREEN: the comparator returned rc $rc for $lvl, which this driver does not recognise (0 = PASS, 11 = BLOCKED, 2 = REFUSAL, 124/137 = capped). AN UNRECOGNISED rc IS A REFUSAL, NEVER A PASS -- a screen whose result cannot be read has not been passed. See $out." 12
      ;;
  esac
}

section7_launch_screen "$LEVEL" "$CASE"

# The case writer carries Section 8 and REFUSES on any precondition it cannot satisfy.  Its
# own planted controls must fire before it is trusted to have written what it says it wrote
# (rule 3): a writer whose plant did not fire is not evidence about the case it produced.
python3 "$CASES/write_m6sr_case.py" --selftest > "$CASE/log.writer_controls" 2>&1
WRC=$?
[ "$WRC" -eq 0 ] || abort "the case writer's PLANTED CONTROLS did not fire (rc $WRC; see $CASE/log.writer_controls). A case written by a writer whose plant did not fire is not evidence (rule 3). REFUSED." 6
say "case writer: ALL PLANTED CONTROLS FIRED (see $CASE/log.writer_controls)"

python3 "$CASES/write_m6sr_case.py" --case "$CASE" --level "$LEVEL" \
    > "$CASE/log.write_case" 2>&1
WRC=$?
[ "$WRC" -eq 0 ] || abort "the case writer REFUSED or failed (rc $WRC; see $CASE/log.write_case). Section 8's case files were NOT written and there is nothing to solve." 6
[ -f "$CASE/0/U" ] || abort "the case writer returned 0 but $CASE/0/U is absent. REFUSED." 70
say "case written: Section 8's seven 0/ fields, fvSchemes, fvSolution, constant/, controlDict, decomposeParDict, sampleDict"
say "case provenance and EVERY CHOICE MADE: $CASE/CASE_PROVENANCE.json"

# uid 1002 inside the container must be able to write the case it solves.
chmod -R 777 "$CASE" 2>/dev/null

# ---- $STEP.  Cap from Section 2.4's own per-level row, converted at THIS step's ranks.
TMO_B5=$(python3 -c "print(int($CAP_B5 * 60.0 / $RANKS))")
say "$STEP: decomposePar + mpirun -np $RANKS rhoSimpleFoam -parallel + reconstructPar"
say "$STEP: cap $CAP_B5 core-min at $RANKS ranks -> ${TMO_B5} wall s.  AN OVERRUN STOPS THE RUN."

# ONE named solver log.  `log.rhoSimpleFoam` is the artifact Section 8.6's completion rule
# and Section 5.1's residual reducer both read, so it carries the SOLVER and nothing else --
# decomposePar and reconstructPar write their own logs.  This is what makes the nProcs
# banner reading unambiguous.
run_in_container "$STEP" "$TMO_B5" "$RANKS" \
  "decomposePar -force > log.decomposePar 2>&1 && \
   mpirun -np $RANKS rhoSimpleFoam -parallel > log.rhoSimpleFoam 2>&1; \
   SOLVER_RC=\$?; echo \$SOLVER_RC > SOLVER_RC.txt; \
   reconstructPar -latestTime > log.reconstructPar 2>&1; \
   exit \$SOLVER_RC"

# ---------------------------------------------------------------------------------------
# 5.  THE RANK READING.  Section 9.2 and Amendment 8: RANKS COME FROM THE SOLVER LOG'S OWN
#     BANNER, NEVER FROM system/decomposeParDict, and the banner's FIRST occurrence is not
#     necessarily the primal's -- so EVERY occurrence in the ONE named log is read and they
#     must ALL agree.
# ---------------------------------------------------------------------------------------
[ -f "$CASE/log.rhoSimpleFoam" ] || abort "$CASE/log.rhoSimpleFoam is ABSENT after the solve step. The completion rule and G2's reducer both read that ONE artifact; without it there is nothing to grade." 6

# THE SECOND ARTIFACT THE COMPLETION RULE READS.  Section 8.6's clauses `rc_zero` and
# `rc_read_from_SOLVER_RC_not_around_setsid` (analyse_m6sr.py::completion_clauses) read
# $CASE/SOLVER_RC.txt, and NOTHING above asserts it: `run_in_container` checks the WRAPPER's
# rc from RC_${STEP}.txt, which is a DIFFERENT file written by a DIFFERENT echo.  The inner
# command exits with $SOLVER_RC whether or not the `echo ... > SOLVER_RC.txt` before it
# succeeded, so a full-cap solve can land with the log present, the wrapper rc 0, and the
# rc file ABSENT -- and be found ungradable only at grading time, after the whole spend.
# ASSERTED HERE, AT ZERO FURTHER SOLVER COST.  It FAILS CLOSED and prints what is missing:
# this driver does NOT create the file and does NOT synthesise an rc.  A FABRICATED rc IS
# WORSE THAN AN ABSENT ONE -- it would turn an unrecorded crash into a silent `rc_zero`.
[ -f "$CASE/SOLVER_RC.txt" ] || abort "$CASE/SOLVER_RC.txt is ABSENT after the solve step. Section 8.6's completion clauses rc_zero and rc_read_from_SOLVER_RC_not_around_setsid read THAT file by explicit path; the wrapper rc in $CASE/RC_${STEP}.txt is a different artifact and does not stand in for it. This driver WILL NOT write it and WILL NOT synthesise an rc: a fabricated rc is worse than an absent one. The level is UNGRADABLE as it stands. REFUSED." 6
[ -s "$CASE/SOLVER_RC.txt" ] || abort "$CASE/SOLVER_RC.txt exists but is EMPTY after the solve step (0 bytes) -- the write was interrupted mid-flight. An empty rc file reads as no rc at all through completion_clauses, and this driver does not repair it. REFUSED." 6
say "$STEP: SOLVER_RC.txt present, recorded rc=$(cat "$CASE/SOLVER_RC.txt")  -- the artifact Section 8.6's completion clauses read"

RANKS_SEEN=$(python3 -c "
import re, sys
txt = open('$CASE/log.rhoSimpleFoam', errors='replace').read()
vals = sorted({int(m) for m in re.findall(r'^nProcs\s*:\s*(\d+)', txt, re.M)})
sys.stdout.write(','.join(str(v) for v in vals))
")
say "$STEP: nProcs values in the solver log's banner(s): [${RANKS_SEEN:-none}]"
[ -n "$RANKS_SEEN" ] || abort "no 'nProcs' banner line in $CASE/log.rhoSimpleFoam. Ranks are READ FROM THE BANNER and never from decomposeParDict; a log with no banner is a REFUSAL, not an assumption of $RANKS." 6
case "$RANKS_SEEN" in
  *,*) abort "the solver log carries DISAGREEING nProcs values [$RANKS_SEEN]. Amendment 8's own basis defect was exactly this -- the file's FIRST nProcs match was 'nProcs : 1' while the primal ran at 4. A log this reader cannot resolve to one rank count is a REFUSAL." 6 ;;
esac
[ "$RANKS_SEEN" = "$RANKS" ] || abort "the solver log's banner reads nProcs = $RANKS_SEEN but this step asked for $RANKS. The COST BASIS is the banner's count, so a mismatch invalidates the core-minute figure. REFUSED." 6
echo "$RANKS_SEEN" > "$CASE/RANKS_FROM_BANNER.txt"

# ---------------------------------------------------------------------------------------
# 6.  SECTION 8.6's STRICT COMPLETION RULE -- EVALUATED, NEVER GRADED.  The verdict belongs
#     to cases/M6SR/analyse_m6sr.py, which is the frozen grading path.  This driver reports
#     the clauses so an operator learns at the drop path rather than at grading time.
# ---------------------------------------------------------------------------------------
python3 -c "
import json, sys
sys.path.insert(0, '$CASES')
import analyse_m6sr as A
cl = A.completion_clauses('$CASE', $END_TIME)
print('COMPLETION CLAUSES (Section 8.6) -- REPORTED BY THE DRIVER, GRADED BY THE COMPARATOR')
for k, v in cl.items():
    print('  %-52s %s' % (k, v))
json.dump(cl, open('$CASE/COMPLETION_CLAUSES.json', 'w'), indent=2)
" 2>&1 | tee "$CASE/log.completion"

# ---------------------------------------------------------------------------------------
# 7.  RULE 12's ESTIMATE-VERSUS-ACTUAL, OWED AT EVERY STEP (Section 9.3).  A completion
#     report without this comparison is INCOMPLETE.  Waste is named SEPARATELY and is never
#     absorbed into the ratio.  RANKS COME FROM THE BANNER.
# ---------------------------------------------------------------------------------------
W_STAGE=$(cat "$CASE/WALL_stage.txt"     2>/dev/null || echo 0)
W_CHECK=$(cat "$CASE/WALL_checkMesh.txt" 2>/dev/null || echo 0)
W_SOLVE=$(cat "$CASE/WALL_$STEP.txt"     2>/dev/null || echo 0)

python3 - "$CASE" "$LEVEL" "$STEP" "$W_STAGE" "$W_CHECK" "$W_SOLVE" "$RANKS_SEEN" \
         "$CELLS" "$END_TIME" "$EST_B5" "$CAP_B5" <<'PYC'
import json, sys
case, level, step = sys.argv[1], sys.argv[2], sys.argv[3]
w_stage, w_check, w_solve = (int(x) for x in sys.argv[4:7])
ranks, cells, end_time = int(sys.argv[7]), int(sys.argv[8]), int(sys.argv[9])
est_b5, cap_b5 = float(sys.argv[10]), float(sys.argv[11])

act_solve = round(w_solve * ranks / 60.0, 4)
act_check = round(w_check * 1 / 60.0, 4)
act_stage = round(w_stage * 1 / 60.0, 4)
rate = (act_solve / (cells * end_time)) if cells and end_time else None

out = {
    "level": level, "step": step, "cells": cells, "end_time": end_time,
    "ranks_FROM_SOLVER_LOG_BANNER": ranks,
    "ranks_NOT_taken_from": "system/decomposeParDict -- that file can post-date the run "
                            "(Section 9.2, Amendment 8)",
    "calibration": {
        step: {"estimate_core_min": est_b5, "cap_core_min": cap_b5,
               "actual_core_min": act_solve,
               "ratio_actual_over_predicted": (round(act_solve / est_b5, 3)
                                               if est_b5 else None),
               "within_cap": act_solve <= cap_b5},
        "B4_checkMesh_this_level": {
            "actual_core_min": act_check,
            "note": "Section 2.4 gives ONE B4 row (cap 2.0 core-min) for checkMesh x3; the "
                    "running total across levels is in <run_root>/B4_SPENT_COREMIN.txt"},
        "B3s_mesh_staging": {
            "actual_core_min": act_stage,
            "UNBUDGETED": "Section 2.4's cost table has NO ROW for staging L3's and L2's "
                          "pre-existing meshes into the run root. B3 covers the L1 build "
                          "only. This figure is REPORTED ON ITS OWN LINE and is NOT folded "
                          "into any registered row and NOT absorbed into any ratio "
                          "(Section 9.3, COMPUTE_BUDGET_CHARTER 6)."},
    },
    "measured_solve_rate_core_min_per_cell_per_iteration": rate,
    "registered_rate_and_its_basis": {
        "value": 3.40e-8,
        "basis_ranks": 4,
        "why_it_matters": "The registered rate is a FOUR-RANK measurement "
                          "(A3-onera-m6-transonic/run_model_run3.log, nProcs : 4 in the "
                          "primal banner). Applying it at 8 or 16 ranks ASSUMES PERFECT "
                          "STRONG SCALING; real efficiency below 1 makes core-minutes "
                          "RISE. The ratio above is the measurement of that assumption.",
    },
    "attribution": "UNATTRIBUTED at driver exit -- contention / waste / misprediction is a "
                   "reading a human makes against the box's own load record. Waste is named "
                   "SEPARATELY and is NEVER absorbed into the ratio (Section 9.3).",
    "cost_basis": "core-minutes = wall s x ranks / 60, ranks from the SOLVER LOG BANNER. "
                  "Dollars are DERIVED, NOT MEASURED, at the owner-stated c7a.4xlarge "
                  "$0.0513/core-h -- the box cannot read its own billing "
                  "(COMPUTE_BUDGET_CHARTER.md 5), so any dollar figure originating here is "
                  "REPORTED-BY-OWNER.",
    "derived_usd_this_level": round((act_solve + act_check + act_stage) / 60.0 * 0.0513, 6),
    "L_HONEST": ("This is a SURFACE-REFINEMENT SENSITIVITY STUDY. Its GCI is a "
                 "SURFACE-REFINEMENT BAND and a LOWER BOUND on total discretisation "
                 "uncertainty. It is NOT an observed order of accuracy, and it is NOT the "
                 "family band Sanaa named as her first deliverable."),
}
json.dump(out, open(case + "/SOLVE_RESULT.json", "w"), indent=2)
print(json.dumps(out, indent=2))
PYC

say "$STEP complete for $LEVEL."
say "Gate P's producer wrote: $CASE/postProcessing/sampleDict/$END_TIME/wingSurface/"
say "NEXT: B0 is Gate GF, B4 is Gate A and B6 is Gate G + Gate P, all in cases/M6SR/analyse_m6sr.py."
say "THIS DRIVER GRADES NOTHING. B4s SCREENED Section 7 per level and REFUSED or let the solve start; it applied no band, computed no gate and printed no verdict of its own."
exit 0
