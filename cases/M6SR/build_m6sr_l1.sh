#!/bin/bash
# M6SR BUILD DRIVER -- steps B1, B2 and B3 of verification/campaign/M6SR_PREREGISTRATION.md.
#
# WHAT THIS FILE IS.  Section 9 of the frozen registration registers the build driver at
# exactly this path, and Section 9.1 RULES that it is "written and committed BEFORE the
# freeze, so the freeze can pin their blob shas".  NOTHING THAT GRADES IS EVER FILED INSIDE
# A RUN ROOT; this driver and the comparator both live under cases/M6SR/.
#
# SECTIONS OF THE REGISTRATION IMPLEMENTED HERE:
#   Section 2.2   the 24,960-face surface is the PUBLISHED TUTORIAL'S OWN INTERMEDIATE,
#                 produced by ONE invocation of the tutorial's own first `coarsen` line on
#                 the tutorial's own master file at a pinned hash.  Nothing is interpolated,
#                 refined or synthesised.
#   Section 2.2   the three normal-direction parameters s0 = 1.0e-4, N = 65, marchDist =
#                 12.0 are IDENTICAL to both existing levels and this driver moves NONE of
#                 them.  r = 1.167442 and cells/wing_faces = 64 hold BY CONSTRUCTION.
#   Section 2.4   the per-step CAPS in core-minutes, enforced STRUCTURALLY by `timeout`.
#   Section 7     the ill-posedness screen: the driver REFUSES a level whose patch names it
#                 did not expect.
#   Section 8.5   autoPatch/createPatch/renumberMesh, and `scotch` is NOT used.
#   Section 8.6   the launcher REFUSES a case where `0` or any time directory exists.
#   Section 9.2   execution and assertion mechanics -- every one of them, below.
#
# SECTION 9.2, BINDING, AND EACH LINE OF IT IS OBSERVED HERE:
#   * ASSERTIONS DO NOT GATE.  There is no `assert` and no bare `set -e` in this file.
#     Every check is `... || { echo "ABORT: <what>"; exit N; }`.  Basis: a guard set that
#     is entirely assert-based is one interpreter flag from absent (L-475).
#   * SHAS ARE READ BACK BY SUBJECT LINE, never by position in a `sha256sum` batch (L-479).
#     See sha_of() below: it hashes ONE named file per invocation.
#   * `setsid timeout cmd` EXITS 0 FOR EVERY OUTCOME.  rc is captured INSIDE the wrapper and
#     written to a file; it is never taken from around the `setsid` line.
#   * `grep ... log.* | tail -1` IS A COIN FLIP under multi-file output.  Every reading in
#     this file names ONE artifact by explicit path.
#
# COST.  Unit: core-minutes (wall s x ranks / 60).  Dollars are DERIVED, NOT MEASURED, at
# the owner-stated c7a.4xlarge $0.0513/core-h -- the box cannot read its own billing, so any
# dollar figure originating here is REPORTED-BY-OWNER.  AN OVERRUN STOPS THE RUN; it does
# not get a new budget.  Every cap below is enforced by `timeout`, so an overrun is
# structural rather than a matter of somebody noticing.
#
# NOTHING UNDER /home/ubuntu/certonomous-runs/ IS WRITTEN, MOVED OR DELETED.  The master
# surface is COPIED OUT of that tree and every product is written under the run root.
#
# SUBMISSIONS ARE PARKED (standing rule 7).  This driver sends nothing anywhere.
#
# =======================================================================================
# AMENDMENT 12 AUDIT, ITEMS 35, 36 AND 37 -- REPAIRED IN THIS FILE (2026-09-04).
# All three were MEASURED and REPORTED by an earlier pass (registration Section 19.5) and
# left unrepaired; this pass repairs them.  Each is stated with its measurement below and
# each carries a control that was run against the REAL PINNED DIGEST, never a mock.
#
# ITEM 35 -- ITEM 28's EXACT DEFECT, IN THIS FILE, AND IT COST 88 % OF THE LADDER.
#   THE DEFECT.  The frozen driver selected `DRUN="docker"` when bare docker works and then
#   built the container call as `timeout ...s $DRUN "docker run ..."`.  On the `sg` branch
#   ($DRUN = `sg docker -c`) that is correct -- the string is one shell command for `sg` to
#   run.  On the BARE branch it expands to `docker "docker run ..."`, the whole command as a
#   SINGLE ARGUMENT to the docker client.
#   MEASURED with this driver's exact expansion, on the pinned digest:
#       rc 1, `docker: unknown command: docker docker run --rm --name m6sr_probe_... `,
#       and RC_<tag>.txt ABSENT, so `inner` reads ABSENT.
#   CONTROL, the identical string through `sg docker -c`:  rc 0, `INSIDE_OK`.
#   WHY IT SURVIVED: BARE_RC is 0 on this box, so this driver was correct ONLY on the branch
#   this box does NOT take.  The live branch had never been exercised.
#   WHAT IT COST: B1, B2 and B3 could not run, so the L1 mesh could not be built, so Gate A
#   had no third level and B5c -- 543.13 core-min of registered estimate, 88 % of the ladder
#   -- was UNREACHABLE.  WHAT IT DID NOT DO: it failed CLOSED (exit 6 on a non-zero inner rc)
#   and it NEVER FIRED -- no run root exists.  This is prevention, not a live repair.
#
#   THE REPAIR, AND THE TRAP INSIDE THE OBVIOUS FIX.  `timeout` execs a PROGRAM.  It cannot
#   exec the shell builtin `command`, so the tempting `timeout ...s command docker ...` was
#   MEASURED to return rc 127 -- `timeout: failed to run command 'command'` -- which is NOT
#   124 and would therefore NOT have read as a cap overrun; it would have aborted at exit 6
#   with a misleading cause.  The resolved binary is therefore captured ONCE, into
#   $DOCKER_BIN, and docker_timeout_q() below passes ARGV on the bare branch and quotes with
#   `printf %q` on the `sg` branch.  MEASURED on the pinned digest, both branches:
#       bare : timeout ...s "$DOCKER_BIN" run ... -> rc 0 / INSIDE_OK
#       sg   : timeout ...s sg docker -c "docker$(printf ' %q' ...)" -> rc 0 / INSIDE_OK
#   AND THE CAP STILL BITES, measured rather than assumed -- a container sleeping 30 s under
#   a 5 s cap returns rc 124 on BOTH branches, so run_in_container's `rc -eq 124 -> abort 6`
#   overrun path (rule 12, AN OVERRUN STOPS THE RUN) still fires after the repair.
#   THE BRANCH TAKEN IS RECORDED IN THE RUN'S OWN OUTPUT ($RR/$LEVEL/DOCKER_BRANCH.txt and
#   DOCKER_PREFLIGHT.txt), because item 28's defect survived precisely because no artifact
#   ever distinguished the two branches.
#
# ITEM 36 -- THE SOLVER PIN DID NOT COVER THE THING THAT BUILDS THE MESH GATE A GRADES.
#   Amendment 12 Ruling 1's image pin lived ONLY in cases/M6SR/run_m6sr_b5.sh.  This file had
#   ZERO digest checks, so $M6SR_IMAGE could still SELECT the image for B1/B2/B3 -- the steps
#   that BUILD the mesh Gate A grades.  A pin on the solver that leaves the mesh builder
#   unpinned pins HALF THE INSTRUMENT.  The pin is registered and enforced below, at ZERO
#   COST, and the container is addressed BY DIGEST so the tag-repoint TOCTOU is closed
#   (measured on this daemon: `docker run` accepts a bare digest, rc 0, and rejects an
#   unknown one, rc 125).
#   WHICH BINARIES THIS DRIVER ACTUALLY INVOKES -- pinned by RESOLVED PATH and sha256, not
#   by digest alone.  It does NOT invoke rhoSimpleFoam and it does NOT invoke ugrid_to_foam:
#       B1  cgns_utils                                   (conda console script)
#       B2  python  +  the pyhyp module and its compiled hyp.so   (NOT a standalone binary)
#       B3  plot3dToFoam, autoPatch, createPatch, renumberMesh    (ESI OpenFOAM v2506)
#   MEASURED, AND IT DIFFERS FROM THE SOLVER'S CASE -- STATED SO NOBODY INHERITS AN ARGUMENT
#   THAT DOES NOT TRANSFER: the pinned image carries THREE `rhoSimpleFoam` (the v2506 build
#   plus OpenFOAM-AD's ADF and ADR builds), which is why Ruling 1 had to pin the solver's
#   PATH as well as the digest.  A whole-filesystem census inside the pinned image returns
#   EXACTLY ONE file for each of plot3dToFoam, autoPatch, createPatch, renumberMesh and
#   cgns_utils.  So the path pin here is NOT disambiguating a name collision -- it is holding
#   PATH resolution to the registered tree -- and that is a measurement, not an inheritance.
#
#   EXIT CODE, AND WHY IT IS NOT THE SIBLING'S 7.  run_m6sr_b5.sh uses exit 7 for its pin
#   refusal.  THIS FILE ALREADY USES exit 7 for a PHYSICS FINDING (the condemned 390-face
#   surface, the wrong pyHyp face count) and exit 8 for Section 7's patch screen.  Overloading
#   either would change what an existing code means, so the instrument-pin refusal here is
#   exit 10 and the run-root refusal is exit 9 (unused here, and 9 is §18.6's own code).
#   THE EXISTING EXIT VOCABULARY OF THIS FILE IS UNCHANGED.
#
# ITEM 37 -- $M6SR_RUN_ROOT WAS HONOURED WITH NO §18.6-CLASS REFUSAL.  Item 29's class, in
#   the builder.  cases/M6SR/analyse_m6sr.py reads NO environment at all, so an operator who
#   exports M6SR_RUN_ROOT without passing a matching --run-root builds the mesh in one tree
#   and grades from another.  Refused below at exit 9, matching §18.6's shape.
#   IT IS ORDERED LAST OF THE NEW REFUSALS ON PURPOSE, and this is a choice, not an oversight:
#   placed first it would make the image pin and the binary pin UNREHEARSABLE anywhere except
#   inside verification/runs/M6SR_runs/, the directory whose ABSENCE is this registration's
#   own rule-2 freeze proof.  Placed last, everything above it can be exercised in a scratch
#   tree and this one then stops the run before a single core-minute is spent.
#
# REFUSAL MECHANICS, CHECKED BEFORE ANY RED WAS TRUSTED.  A `refuse()` called inside `$( )`
# exits only the SUBSHELL, and with its message on stdout it is CAPTURED AS THE VALUE -- a
# defect that has already made three mutations die of the wrong cause in this campaign.
# EVERY abort() call site in this file, new and pre-existing, was read: none is inside a
# command substitution, a pipeline, or a `while read` fed by a pipe.  The new binary-pin
# check deliberately uses a FILE DIFF rather than a loop, so there is no loop body that could
# become a subshell and swallow an abort.
# =======================================================================================

set +u
set +e

RR=${M6SR_RUN_ROOT:-/home/ubuntu/Certonomous/verification/runs/M6SR_runs}
CR=/home/ubuntu/certonomous-runs
MASTER="$CR/A3-onera-m6-transonic/m6_surfaceMesh_fine.cgns"
MASTER_SHA=197efa09d838b276a8967da9532d9c4d57edca18cb777bd640257606d2d83327
IMG=${M6SR_IMAGE:-dafoam-idwarp-rot:v1}
LEVEL=L1

# ---------------------------------------------------------------------------------------
# ITEM 36 -- THE PINNED BUILD INSTRUMENT.  These are NOT `${VAR:-default}` forms and NOTHING
# IN THE ENVIRONMENT CAN CHANGE THEM.  `M6SR_IMAGE` above may still NAME an image; it can no
# longer SELECT one, because the digest below must match or this driver aborts at exit 10
# before a single core-minute is spent.
#
# HOW EACH VALUE WAS OBTAINED, because a pin whose provenance is not stated is a number
# somebody typed (all measured 2026-09-04, in a scratch tree, no run root):
#   digest    `docker inspect dafoam-idwarp-rot:v1` -> `.Id`.  IDENTICAL to the digest
#             Amendment 12 Ruling 1 pins in run_m6sr_b5.sh, so the builder and the solver are
#             now demonstrably the same instrument.  CAVEAT, STATED: it is NOT corroborated
#             against a registry; the image was built on this box and no registry copy was
#             consulted.
#   version   `WM_PROJECT_VERSION` inside that container after sourcing loadDAFoam.sh: v2506.
#   paths     `command -v <name>` inside that container, after the same source.
#   sha256    `sha256sum` of each resolved path, inside that container.
#   pyhyp     `pyhyp.__file__` and the compiled `hyp.so` beside it -- B2 runs `python
#             genWingMesh.py`, so the marching engine is a MODULE, not a binary on PATH, and
#             pinning `python` alone would pin the interpreter and not the instrument.
M6SR_PINNED_IMAGE_REF=dafoam-idwarp-rot:v1
M6SR_PINNED_IMAGE_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
M6SR_PINNED_OF_FORK="ESI OpenFOAM (openfoam.com), NOT the OpenFOAM Foundation fork"
M6SR_PINNED_OF_VERSION=v2506
M6SR_PINNED_PYHYP_VERSION=2.6.1
M6SR_PINNED_CGNSUTILS_VERSION=2.6.0

# The pinned table of EVERY executable and module this driver invokes, as
# "<name> <resolved path> <sha256>".  Compared as a whole file against the container's own
# report; see Section 1c.  ONE diff, ONE refusal, NO loop that could become a subshell.
read -r -d '' M6SR_PINNED_BUILD_BINARIES <<'PINTBL'
PIN autoPatch /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506/platforms/linux64GccDPInt32Opt/bin/autoPatch 88b07730b457ade414c884a1566eb457685833672ab755ca6f21f715626e15d6
PIN cgns_utils /home/dafoamuser/dafoam/packages/miniconda3/bin/cgns_utils 5c8f0e7501e42d32e87af43150715efc194906c7565c2af982b4a49aab731109
PIN createPatch /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506/platforms/linux64GccDPInt32Opt/bin/createPatch fec27bfceff73a6968b431dd791ba81ecf50729f22072eeb6f765106b059835f
PIN plot3dToFoam /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506/platforms/linux64GccDPInt32Opt/bin/plot3dToFoam f455b4372636c6bf0fbd9fa82caf304f02e15be34f39693fbc68e566ac9cb040
PIN pyhyp_hyp_so /home/dafoamuser/dafoam/packages/miniconda3/lib/python3.10/site-packages/pyhyp/hyp.so 53744d52dbb56ef82f7894ec2573c82d1501ff4acf96f8cfe8767335c7317def
PIN pyhyp_module /home/dafoamuser/dafoam/packages/miniconda3/lib/python3.10/site-packages/pyhyp/__init__.py ae747e8b269ef2cf654ae8caebf1e4baabf255f289a877a09f26a0ed8599b7ef
PIN python /home/dafoamuser/dafoam/packages/miniconda3/bin/python ae1e0962caeb115196918c6d6d6c55611e92dc580c2796f47f0e9a812377a8fe
PIN renumberMesh /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506/platforms/linux64GccDPInt32Opt/bin/renumberMesh 6a7a2278ac33390e931cb5b82f71055e60a5e10d40c080df4270e70e6ae43efd
PINTBL

# Section 2.4 caps, in core-minutes, and the wall-second timeout each one implies at the
# rank count that step actually runs at.  pyHyp runs 1 rank; every step here is serial.
RANKS=1
CAP_B1_COREMIN=1.0    ; TMO_B1=60
CAP_B2_COREMIN=70.0   ; TMO_B2=4200
CAP_B3_COREMIN=3.0    ; TMO_B3=180

EST_B1=0.05 ; EST_B2=7.04 ; EST_B3=0.29
RATE_USD_PER_CORE_H=0.0513

say(){ echo "[$(date -u +%H:%M:%SZ)] $*"; }
abort(){ echo "ABORT: $1"; mkdir -p "$RR/$LEVEL" 2>/dev/null; echo "$1" > "$RR/$LEVEL/STOPPED.txt" 2>/dev/null; exit "${2:-1}"; }

# sha256 of ONE named file.  L-479: never a batch, never read back by position.
sha_of(){ sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }

# ---------------------------------------------------------------------------------------
# 0.  REFUSALS BEFORE ANY WORK.  Section 8.6 and Section 7.
# ---------------------------------------------------------------------------------------
say "M6SR build driver -- B1/B2/B3 for level $LEVEL"
say "run root: $RR   (nothing under $CR is written)"

[ -f "$MASTER" ] || abort "the pinned surface master is ABSENT: $MASTER" 3
GOT=$(sha_of "$MASTER")
[ -n "$GOT" ] || abort "could not hash the surface master; a missing hash is a REFUSAL, never a fallback" 3
[ "$GOT" = "$MASTER_SHA" ] || abort "surface master sha256 $GOT != pinned $MASTER_SHA -- Section 2.2 pins this file and admits no substitute" 3
say "surface master hash VERIFIED against the pinned $MASTER_SHA"

# Section 8.6: the launcher REFUSES a case where `0` or any time directory already exists.
if [ -d "$RR/$LEVEL" ]; then
  [ -d "$RR/$LEVEL/0" ] && abort "$RR/$LEVEL/0 already exists. The age guard dates the run from the case's own 0/ directory, so a pre-existing 0/ makes rule 4 unprovable. REFUSED." 4
  for D in "$RR/$LEVEL"/[0-9]*; do
    [ -d "$D" ] && abort "a time directory already exists: $D. REFUSED (Section 8.6)." 4
  done
  [ -d "$RR/$LEVEL/constant/polyMesh" ] && abort "$RR/$LEVEL/constant/polyMesh already exists. This driver BUILDS the mesh; it never overwrites one. REFUSED." 4
fi

mkdir -p "$RR/$LEVEL/work" "$RR/$LEVEL/constant" "$RR/$LEVEL/system" || abort "could not create the run root" 3
date -u +%s > "$RR/RUN_ROOT_CREATED_EPOCH" 2>/dev/null

# Docker preflight, BOTH limbs recorded, because the bare failure would be silent.
BARE_OUT=$(docker version --format '{{.Server.Version}}' 2>&1); BARE_RC=$?
SG_OUT=$(sg docker -c "docker version --format '{{.Server.Version}}'" 2>&1); SG_RC=$?
{ echo "bare_rc=$BARE_RC"; echo "bare_out=$BARE_OUT"
  echo "sg_rc=$SG_RC";     echo "sg_out=$SG_OUT"
  echo "groups=$(id -G)"; } > "$RR/$LEVEL/DOCKER_PREFLIGHT.txt"
if [ $SG_RC -ne 0 ] && [ $BARE_RC -ne 0 ]; then
  abort "docker unreachable both bare and through 'sg docker -c'. This grades THE DRIVER'S ABILITY TO RUN and nothing about the M6 -- BLOCKED, not GATE FAIL." 5
fi
# ITEM 35, PART 1.  WHICH BRANCH THIS BOX TAKES IS RECORDED IN THE RUN'S OWN OUTPUT, not
# merely printed to a terminal nobody keeps.  Item 28's defect -- and this file's item 35 --
# survived precisely because no artifact ever distinguished the two branches: BARE_RC is 0 on
# this box, so the `sg docker -c` branch has NEVER been exercised here and the bare branch was
# the broken one.  A later reader must be able to tell which invocation produced a given run
# without re-deriving it from the box's group membership months afterwards.
if [ $BARE_RC -eq 0 ]; then DOCKER_BRANCH=bare; else DOCKER_BRANCH=sg; fi
# `timeout` execs a PROGRAM.  It cannot exec the shell builtin `command`, so the resolved path
# is taken ONCE here rather than written as `timeout ...s command docker ...`, which was
# MEASURED to return rc 127 (`timeout: failed to run command 'command'`).  That rc is NOT 124
# and would not have been read as a cap overrun; it would have aborted at exit 6 with a
# misleading cause.
DOCKER_BIN=$(command -v docker 2>/dev/null)
[ "$DOCKER_BRANCH" != "bare" ] || [ -n "$DOCKER_BIN" ] \
  || abort "the bare-docker branch was selected (bare rc=$BARE_RC) but 'docker' does not resolve on PATH, so there is no program for \`timeout\` to exec. This driver will not guess a path." 5
{ echo "branch=$DOCKER_BRANCH"
  echo "docker_bin=$DOCKER_BIN"
  echo "host_uid=$(id -u)"
  echo "host_gid=$(id -g)"; } >> "$RR/$LEVEL/DOCKER_PREFLIGHT.txt"
echo "$DOCKER_BRANCH" > "$RR/$LEVEL/DOCKER_BRANCH.txt"
say "docker reachable (bare rc=$BARE_RC, sg rc=$SG_RC); invocation branch '$DOCKER_BRANCH'${DOCKER_BIN:+ via $DOCKER_BIN}"

# ---------------------------------------------------------------------------------------
# ITEM 35, PART 2.  THE TWO INVOCATION HELPERS.  BOTH PASS ARGV on the bare branch and quote
# with `printf %q` on the `sg` branch, so neither can be mis-parsed by a second shell.  The
# argv form cannot be mis-quoted because nothing re-parses it.
# ---------------------------------------------------------------------------------------
docker_q(){
  if [ "$DOCKER_BRANCH" = "bare" ]; then "$DOCKER_BIN" "$@"; return $?; fi
  local q; q=$(printf ' %q' "$@")
  sg docker -c "docker$q"
  return $?
}
docker_timeout_q(){
  local tmo="$1"; shift
  if [ "$DOCKER_BRANCH" = "bare" ]; then
    timeout "${tmo}"s "$DOCKER_BIN" "$@"
    return $?
  fi
  local q; q=$(printf ' %q' "$@")
  timeout "${tmo}"s sg docker -c "docker$q"
  return $?
}

# ---------------------------------------------------------------------------------------
# 1b.  ITEM 36 -- THE BUILD INSTRUMENT IS PINNED, AND THE PIN REFUSES BEFORE IT SPENDS.
#      Everything here is at ZERO COST against Section 2.4's B1/B2/B3 rows: it is one
#      `docker inspect` and one short container probe, reported on their own line as step
#      B0p, UNBUDGETED, and NEVER folded into any registered row (Section 9.3).
# ---------------------------------------------------------------------------------------
T0P=$(date +%s)
RESOLVED_DIGEST=$(docker_q inspect --format '{{.Id}}' "$IMG" 2>/dev/null)
[ -n "$RESOLVED_DIGEST" ] \
  || abort "the image '$IMG' does not resolve to a digest on this daemon. An unresolvable image is a REFUSAL, never a fallback to whatever else is on the box (Amendment 12 Ruling 1)." 10
[ "$RESOLVED_DIGEST" = "$M6SR_PINNED_IMAGE_DIGEST" ] \
  || abort "IMAGE DIGEST MISMATCH. '$IMG' resolves to $RESOLVED_DIGEST; this driver pins $M6SR_PINNED_IMAGE_DIGEST ($M6SR_PINNED_IMAGE_REF). \$M6SR_IMAGE may NAME an image; it may not SELECT one. This driver BUILDS THE MESH GATE A GRADES -- a pin on the solver alone pins half the instrument. REFUSED AT ZERO COST." 10

# The container is henceforth addressed BY DIGEST, never by the tag.  A tag can be re-pointed
# between this check and the run; a digest cannot.  Verified on this daemon that `docker run`
# accepts a bare digest (rc 0) and rejects an unknown one (rc 125).
IMG_PINNED="$M6SR_PINNED_IMAGE_DIGEST"

# THE INSTRUMENT ITSELF, not merely its wrapper.  The container reports its OWN resolution of
# every executable and module B1/B2/B3 invoke; the report is compared AS A WHOLE FILE against
# the pinned table.  A diff, not a loop -- a `while read` fed by a pipe would run its body in
# a SUBSHELL, where an abort exits only that subshell and its message becomes the value.
PROBE_OUT=$(docker_q run --rm -u 1002:1002 "$IMG_PINNED" bash -lc 'set +u; source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1
echo "VER=$WM_PROJECT_VERSION"
for b in autoPatch cgns_utils createPatch plot3dToFoam python renumberMesh; do
  p=$(command -v "$b" 2>/dev/null)
  echo "PIN $b ${p:-ABSENT} $(sha256sum "$p" 2>/dev/null | cut -d" " -f1)"
done
PH=$(python -c "import pyhyp; print(pyhyp.__file__)" 2>/dev/null | tail -1)
echo "PIN pyhyp_module ${PH:-ABSENT} $(sha256sum "$PH" 2>/dev/null | cut -d" " -f1)"
HS="$(dirname "${PH:-/nonexistent/x}")/hyp.so"
echo "PIN pyhyp_hyp_so $HS $(sha256sum "$HS" 2>/dev/null | cut -d" " -f1)"
echo "PYHYP_VER=$(python -c "import pyhyp; print(pyhyp.__version__)" 2>/dev/null | tail -1)"
echo "CGNSU_VER=$(python -c "import cgnsutilities; print(cgnsutilities.__version__)" 2>/dev/null | tail -1)"' 2>&1)
PROBE_RC=$?
T1P=$(date +%s)
echo "$((T1P-T0P))" > "$RR/$LEVEL/WALL_B0p.txt"

P_VER=$(printf '%s\n' "$PROBE_OUT" | sed -n 's/^VER=//p' | tail -1)
P_PYHYP=$(printf '%s\n' "$PROBE_OUT" | sed -n 's/^PYHYP_VER=//p' | tail -1)
P_CGNSU=$(printf '%s\n' "$PROBE_OUT" | sed -n 's/^CGNSU_VER=//p' | tail -1)
printf '%s\n' "$PROBE_OUT" > "$RR/$LEVEL/BUILD_PIN_PROBE.txt"
printf '%s\n' "$PROBE_OUT" | grep '^PIN ' | LC_ALL=C sort > "$RR/$LEVEL/BUILD_PIN_OBSERVED.txt"
printf '%s\n' "$M6SR_PINNED_BUILD_BINARIES" | grep '^PIN ' | LC_ALL=C sort > "$RR/$LEVEL/BUILD_PIN_EXPECTED.txt"

[ "$PROBE_RC" -eq 0 ] && [ -n "$P_VER" ] \
  || abort "the build-instrument probe inside the pinned image failed (rc $PROBE_RC). A probe that returns nothing is a REFUSAL, never an assumption that the right binaries are there. See $RR/$LEVEL/BUILD_PIN_PROBE.txt" 10
[ "$P_VER" = "$M6SR_PINNED_OF_VERSION" ] \
  || abort "OPENFOAM VERSION MISMATCH: the image reports WM_PROJECT_VERSION='$P_VER'; this driver pins '$M6SR_PINNED_OF_VERSION' ($M6SR_PINNED_OF_FORK). REFUSED." 10
[ "$P_PYHYP" = "$M6SR_PINNED_PYHYP_VERSION" ] \
  || abort "pyHyp VERSION MISMATCH: the image reports '$P_PYHYP'; this driver pins '$M6SR_PINNED_PYHYP_VERSION'. B2's march IS pyHyp, so a different pyHyp is a different L1 mesh. REFUSED." 10
[ "$P_CGNSU" = "$M6SR_PINNED_CGNSUTILS_VERSION" ] \
  || abort "cgnsutilities VERSION MISMATCH: the image reports '$P_CGNSU'; this driver pins '$M6SR_PINNED_CGNSUTILS_VERSION'. B1's `coarsen` IS cgns_utils, so a different one is a different 24,960-face surface. REFUSED." 10

PIN_DIFF=$(diff -u "$RR/$LEVEL/BUILD_PIN_EXPECTED.txt" "$RR/$LEVEL/BUILD_PIN_OBSERVED.txt" 2>&1)
[ -z "$PIN_DIFF" ] \
  || abort "BUILD BINARY PIN MISMATCH -- the container's own resolution of the executables and modules B1/B2/B3 invoke does not match the pinned table. A binary this driver did not expect, at a path this driver did not expect, BUILDS A DIFFERENT MESH under the right name. REFUSED AT ZERO COST. diff (expected vs observed): $PIN_DIFF" 10

{ echo "{"
  echo "  \"pinned_by\": \"cases/M6SR/build_m6sr_l1.sh, Amendment 12 audit item 36\","
  echo "  \"scope\": \"the BUILD instrument -- B1/B2/B3. Amendment 12 Ruling 1 pinned only the SOLVE instrument, in run_m6sr_b5.sh.\","
  echo "  \"image_ref_named\": \"$IMG\","
  echo "  \"image_ref_pinned\": \"$M6SR_PINNED_IMAGE_REF\","
  echo "  \"image_digest_resolved\": \"$RESOLVED_DIGEST\","
  echo "  \"image_digest_pinned\": \"$M6SR_PINNED_IMAGE_DIGEST\","
  echo "  \"digest_kind\": \"OCI image manifest digest, read as docker inspect .Id; NOT corroborated against a registry\","
  echo "  \"openfoam_fork\": \"$M6SR_PINNED_OF_FORK\","
  echo "  \"openfoam_version\": \"$P_VER\","
  echo "  \"pyhyp_version\": \"$P_PYHYP\","
  echo "  \"cgnsutilities_version\": \"$P_CGNSU\","
  echo "  \"binaries_invoked\": \"B1 cgns_utils; B2 python + pyhyp module + hyp.so; B3 plot3dToFoam, autoPatch, createPatch, renumberMesh. This driver invokes NO solver and NO ugrid_to_foam.\","
  echo "  \"binary_name_census_in_image\": \"whole-filesystem count is 1 for each of cgns_utils, plot3dToFoam, autoPatch, createPatch, renumberMesh -- UNLIKE rhoSimpleFoam, of which the image carries THREE. The path pin here holds PATH resolution to the registered tree; it is not disambiguating a name collision.\","
  echo "  \"container_run_target\": \"the DIGEST, never the tag -- a tag can be re-pointed between the check and the run\","
  echo "  \"docker_invocation_branch\": \"$DOCKER_BRANCH\","
  echo "  \"docker_bin\": \"$DOCKER_BIN\","
  echo "  \"B0p_preflight_wall_s\": $((T1P-T0P)),"
  echo "  \"B0p_UNBUDGETED\": \"Section 2.4's cost table has no row for a pin preflight. It is REPORTED ON ITS OWN LINE at 1 rank and is NOT folded into any registered row and NOT absorbed into any ratio (Section 9.3).\""
  echo "}"; } > "$RR/$LEVEL/BUILD_PIN.json"
say "build instrument pin VERIFIED: image $RESOLVED_DIGEST, OpenFOAM $P_VER, pyHyp $P_PYHYP, cgnsutilities $P_CGNSU, all 8 pinned paths+sha256 matched"
say "  step B0p (pin preflight): $((T1P-T0P)) wall s at 1 rank -- UNBUDGETED in Section 2.4, reported on its own line"

# ---------------------------------------------------------------------------------------
# 1c.  ITEM 37 -- THE RUN ROOT IS PINNED TOO.  Item 29's class, in the builder.  This driver
#      honours $M6SR_RUN_ROOT; cases/M6SR/analyse_m6sr.py reads NO environment at all (its
#      REPO is derived from __file__ and it takes --run-root), so an operator who exports
#      M6SR_RUN_ROOT without passing a matching --run-root BUILDS THE MESH IN ONE TREE AND
#      GRADES FROM ANOTHER.  It fails closed -- the comparator finds no case and refuses --
#      but a pin that only holds because the other side happens to refuse is not a pin.
#      ORDERED LAST OF THE NEW REFUSALS ON PURPOSE; see the header for why.
# ---------------------------------------------------------------------------------------
M6SR_REGISTERED_RUN_ROOT=/home/ubuntu/Certonomous/verification/runs/M6SR_runs
echo "$RR" > "$RR/$LEVEL/RUN_ROOT_USED.txt"
[ "$RR" = "$M6SR_REGISTERED_RUN_ROOT" ] \
  || abort "RUN ROOT MISMATCH: this driver was pointed at '$RR' (via \$M6SR_RUN_ROOT); Section 9's frozen path table registers '$M6SR_REGISTERED_RUN_ROOT'. The comparator reads NO environment and defaults to the registered path, so an L1 mesh built here would be graded from THERE -- producer and reader in different trees. An export without a matching --run-root is a REFUSAL, not a grade. REFUSED AT ZERO COST." 9

cp -- "$MASTER" "$RR/$LEVEL/work/m6_surfaceMesh_fine.cgns" || abort "master copy-out failed" 3
chmod 777 "$RR/$LEVEL/work" || abort "could not make the work directory writable to the container uid" 3

# One helper for every containerised step.  rc IS CAPTURED INSIDE THE WRAPPER (Section 9.2)
# -- `setsid timeout cmd` exits 0 for every outcome, so an rc taken from around the setsid
# line is meaningless.  The cap is enforced by `timeout` and an overrun STOPS THE RUN.
run_in_container(){
  local tag="$1" tmo="$2" cmd="$3"
  local t0 t1 rc wall
  t0=$(date +%s)
  # ITEM 35 REPAIRED: argv, through docker_timeout_q, correct on BOTH branches -- and the
  # image is addressed by DIGEST ($IMG_PINNED), never by the tag $IMG.  The cap is still
  # enforced by `timeout` and rc 124 still reaches the overrun path below (measured on both
  # branches: a 30 s container under a 5 s cap returns 124).
  docker_timeout_q "$tmo" run --rm --name "m6sr_${tag}_$$" -u 1002:1002 \
      -v "$RR/$LEVEL/work":/home/dafoamuser/mount -w /home/dafoamuser/mount "$IMG_PINNED" \
      bash -c "set +u; source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; $cmd; echo \"WRAPPER_RC=\$?\" > RC_${tag}.txt" \
      > "$RR/$LEVEL/log.$tag" 2>&1
  rc=$?
  t1=$(date +%s); wall=$((t1-t0))
  docker_q rm -f "m6sr_${tag}_$$" >/dev/null 2>&1
  # THE INNER rc, read from the file the wrapper wrote, by explicit path -- never from $?
  # around the timeout/setsid line, and never by `grep log.* | tail -1`.
  local inner="ABSENT"
  [ -f "$RR/$LEVEL/work/RC_${tag}.txt" ] && inner=$(cut -d= -f2 "$RR/$LEVEL/work/RC_${tag}.txt")
  echo "$tag outer_rc=$rc inner_rc=$inner wall_s=$wall timeout_s=$tmo" \
      >> "$RR/$LEVEL/STEP_RC.txt"
  say "$tag: outer rc=$rc  INNER rc=$inner  wall=${wall}s  cap=${tmo}s"
  if [ "$rc" -eq 124 ]; then
    abort "$tag exceeded its structural cap of ${tmo} wall s. AN OVERRUN STOPS THE RUN. It does not get a new budget (rule 12)." 6
  fi
  [ "$inner" = "0" ] || abort "$tag inner rc=$inner (outer $rc). A non-zero rc inside the container is a FAILED STEP, whatever the outer wrapper returned." 6
  echo "$wall" > "$RR/$LEVEL/WALL_${tag}.txt"
}

# ---------------------------------------------------------------------------------------
# B1.  `cgns_utils coarsen` master -> the 24,960-face surface.  ONE CALL.  Cap 1.0 core-min.
#
# Section 2.2, read verbatim from the published tutorial's own preProcessing.sh lines 21-23:
#     # coarsen the surface mesh two times
#     cgns_utils coarsen m6_surfaceMesh_fine.cgns surfaceMesh.cgns
#     cgns_utils coarsen surfaceMesh.cgns
# The FIRST call emits 24,960 faces.  This driver makes THAT call and stops.  The tutorial's
# SECOND call -- which would emit the 6,240 the existing L2 was built on -- is NOT made.
# ---------------------------------------------------------------------------------------
say "B1: cgns_utils coarsen (ONE call), cap ${CAP_B1_COREMIN} core-min"
run_in_container coarsen "$TMO_B1" \
  "cgns_utils coarsen m6_surfaceMesh_fine.cgns surfaceMesh.cgns"

[ -f "$RR/$LEVEL/work/surfaceMesh.cgns" ] || abort "B1 produced no surfaceMesh.cgns" 6
SURF_SHA=$(sha_of "$RR/$LEVEL/work/surfaceMesh.cgns")
[ -n "$SURF_SHA" ] || abort "could not hash the coarsened surface" 6
echo "$SURF_SHA" > "$RR/$LEVEL/work/surfaceMesh.cgns.sha256"
say "B1: 24,960-face surface sha256 $SURF_SHA  -- PUBLISHED here as Gate A item A7 requires"

# Gate A item A8: the CONDEMNED 390-face surface must appear in NO level (Section 1.3).
CONDEMNED=aab44d4174d598bf8a9531def9607409099a3711832cac67f9d93538240b2326
[ "$SURF_SHA" = "$CONDEMNED" ] && abort "the coarsened surface IS the condemned 390-face surface ($CONDEMNED). Section 1.3 condemns it and the MECHANISM IS NOT ESTABLISHED. NOT A RESULT." 7

# ---------------------------------------------------------------------------------------
# B2.  pyHyp march, 24,960 x 64.  Cap 70.0 core-min.
#
# EVERY option below is byte-identical to the existing levels' own genWingMesh.py.  THE
# THREE PARAMETERS THAT SET THE NORMAL DIRECTION -- s0 = 1.0e-4, N = 65, marchDist = 12.0 --
# ARE UNCHANGED, which is what makes r = 1.167442 and cells/wing_faces = 64 hold at all
# three levels BY CONSTRUCTION rather than by argument (Section 2.2, Section 6).
# ---------------------------------------------------------------------------------------
cat > "$RR/$LEVEL/work/genWingMesh.py" <<'PYG'
"""M6SR L1 deck.  The three normal-direction parameters are IDENTICAL to both existing
levels (s0 = 1.0e-4, N = 65, marchDist = 12.0).  ONLY THE SURFACE DIFFERS -- that is the
whole of this family's refinement, and it is why Section 6's clause L-HONEST reads as it
does: the wall-normal discretisation is IDENTICAL across the family, so the family refines
2 of 3 directions and its GCI is a LOWER BOUND."""
from pyhyp import pyHyp

options = {
    "inputFile": "surfaceMesh.cgns",
    "fileType": "CGNS",
    "unattachedEdgesAreSymmetry": True,
    "outerFaceBC": "farfield",
    "autoConnect": True,
    "BC": {},
    "families": "wall",
    "N": 65,
    "s0": 1.0e-4,
    "marchDist": 12.0,
    "ps0": -1.0,
    "pGridRatio": -1.0,
    "cMax": 0.1,
    "epsE": 1.0,
    "epsI": 2.0,
    "theta": 3.0,
    "volCoef": 0.25,
    "volBlend": 0.0005,
    "volSmoothIter": 100,
    "kspreltol": 1e-4,
}

hyp = pyHyp(options=options)
hyp.run()
hyp.writePlot3D("volumeMesh.xyz")
PYG

say "B2: pyHyp march 24,960 x 64, cap ${CAP_B2_COREMIN} core-min (est ${EST_B2})"
run_in_container pyhyp "$TMO_B2" "python genWingMesh.py"

[ -s "$RR/$LEVEL/work/volumeMesh.xyz" ] || abort "B2 produced no volumeMesh.xyz" 6
# The face count is read from pyHyp's OWN banner in ONE named log, by explicit path.
FACES=$(grep -m1 'Total Faces:' "$RR/$LEVEL/log.pyhyp" | tr -dc '0-9')
[ "$FACES" = "24960" ] || abort "pyHyp read $FACES surface faces; Section 2.2 registers 24,960. A different count is a FINDING, never something to proceed past." 7
say "B2: pyHyp banner reads Total Faces: $FACES -- the registered 24,960"

# ---------------------------------------------------------------------------------------
# B3.  plot3dToFoam + autoPatch 60 + createPatch + renumberMesh.  Cap 3.0 core-min.
#      Section 8.5: `scotch` is NOT used anywhere in this campaign.
# ---------------------------------------------------------------------------------------
say "B3: plot3dToFoam + autoPatch 60 + createPatch + renumberMesh, cap ${CAP_B3_COREMIN} core-min"
run_in_container mesh "$TMO_B3" \
  "plot3dToFoam -noBlank volumeMesh.xyz && autoPatch 60 -overwrite && \
   createPatch -overwrite && renumberMesh -overwrite"

# ---------------------------------------------------------------------------------------
# 4.  SECTION 7's ILL-POSEDNESS SCREEN.  THE DRIVER REFUSES A LEVEL WHOSE PATCH NAMES IT
#     DID NOT EXPECT.  Section 7 states this in terms: "The new L1's patch names are
#     produced by `autoPatch 60` + `createPatch` and are NOT predicted here -- a driver
#     assuming one name set across levels would silently mis-apply boundary conditions."
# ---------------------------------------------------------------------------------------
BND="$RR/$LEVEL/work/constant/polyMesh/boundary"
[ -f "$BND" ] || abort "B3 produced no constant/polyMesh/boundary; Section 7's screen cannot run and the level is BLOCKED, not passed" 7

N_WALL=$(grep -c 'type[[:space:]]\+wall;'     "$BND")
N_SYMM=$(grep -c 'type[[:space:]]\+symmetry;' "$BND")
N_PATCH=$(grep -c 'type[[:space:]]\+patch;'   "$BND")
say "B3: patch types -- wall $N_WALL, symmetry $N_SYMM, patch $N_PATCH"
[ "$N_WALL"  -eq 1 ] || abort "Section 7: exactly one patch typed 'wall' is required; found $N_WALL. BLOCKED." 8
[ "$N_SYMM"  -ge 1 ] || abort "Section 7: a symmetry plane typed 'symmetry' is required (NEVER 'empty', NEVER 'wall'); found $N_SYMM. RUNG1_M6's M0 was a closed all-wall box and a branch-killing decision was taken off a mesh that could never have been solved. BLOCKED." 8
[ "$N_PATCH" -ge 1 ] || abort "Section 7: a farfield typed 'patch' is required; found $N_PATCH. BLOCKED." 8

grep -q 'type[[:space:]]\+empty;' "$BND" && abort "Section 7: a patch is typed 'empty'. That is never acceptable for this configuration's symmetry plane. BLOCKED." 8

mv "$RR/$LEVEL/work/constant/polyMesh" "$RR/$LEVEL/constant/polyMesh" \
  || abort "could not move the built polyMesh out of the container work directory" 3

# ---------------------------------------------------------------------------------------
# 5.  RULE 12's ESTIMATE-VERSUS-ACTUAL, OWED AT EVERY STEP (Section 9.3).  A completion
#     report without this comparison is INCOMPLETE.  Waste is named SEPARATELY and is never
#     absorbed into the ratio.
# ---------------------------------------------------------------------------------------
W1=$(cat "$RR/$LEVEL/WALL_coarsen.txt" 2>/dev/null || echo 0)
W2=$(cat "$RR/$LEVEL/WALL_pyhyp.txt"   2>/dev/null || echo 0)
W3=$(cat "$RR/$LEVEL/WALL_mesh.txt"    2>/dev/null || echo 0)

python3 - "$RR/$LEVEL" "$W1" "$W2" "$W3" "$RANKS" "$SURF_SHA" <<'PYC'
import json, sys
d, w1, w2, w3, ranks, surf = sys.argv[1], *[int(x) for x in sys.argv[2:5]], int(sys.argv[5]), sys.argv[6]
est = {"B1": 0.05, "B2": 7.04, "B3": 0.29}
cap = {"B1": 1.0,  "B2": 70.0, "B3": 3.0}
act = {"B1": round(w1 * ranks / 60.0, 4),
       "B2": round(w2 * ranks / 60.0, 4),
       "B3": round(w3 * ranks / 60.0, 4)}
rows = {}
for k in est:
    rows[k] = {
        "estimate_core_min": est[k], "cap_core_min": cap[k],
        "actual_core_min": act[k], "ranks": ranks,
        "ratio_actual_over_predicted": (round(act[k] / est[k], 3) if est[k] else None),
        "within_cap": act[k] <= cap[k],
        "attribution": "UNATTRIBUTED at driver exit -- contention / waste / misprediction "
                       "is a reading a human makes against the box's own load record. Waste "
                       "is named SEPARATELY and is NEVER absorbed into the ratio (Section 9.3).",
    }
total_act = round(sum(act.values()), 4)
out = {
    "step": "B1+B2+B3", "level": "L1",
    "surface_sha256_24960_PUBLISHED": surf,
    "calibration": rows,
    "total_actual_core_min": total_act,
    "total_estimate_core_min": round(sum(est.values()), 4),
    "cost_basis": ("dollars DERIVED at the owner-stated c7a.4xlarge rate $0.0513/core-h, "
                   "REPORTED-BY-OWNER and NEVER measured -- the box cannot read its own "
                   "billing (COMPUTE_BUDGET_CHARTER.md 5)"),
    "derived_usd": round(total_act / 60.0 * 0.0513, 6),
    "calibration_questions_this_ladder_answers": [
        "Which pyHyp basis was right -- the log-interpolated 2.644e-4, L1's average "
        "3.796e-4, or L1's marginal 8.676e-4 s/face-layer? (Section 9.3)",
        "Was the x2.0 superlinear allowance on B5c too small, right, or too large? "
        "(Section 9.3) -- NOT answered by this driver, which runs no solve.",
    ],
    "L_HONEST": ("This is a SURFACE-REFINEMENT SENSITIVITY STUDY. Its GCI is a "
                 "SURFACE-REFINEMENT BAND and a LOWER BOUND on total discretisation "
                 "uncertainty. It is NOT an observed order of accuracy, and it is NOT the "
                 "family band Sanaa named as her first deliverable."),
}
json.dump(out, open(d + "/BUILD_RESULT.json", "w"), indent=2)
print(json.dumps(out, indent=2))
PYC

say "B1/B2/B3 complete. Mesh at $RR/$LEVEL/constant/polyMesh"
say "NEXT: B4 is Gate A and B0 is Gate GF, both in cases/M6SR/analyse_m6sr.py. THIS DRIVER GRADES NOTHING."
exit 0
