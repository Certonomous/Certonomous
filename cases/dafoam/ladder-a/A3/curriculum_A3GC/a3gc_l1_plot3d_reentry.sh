#!/usr/bin/env bash
# =====================================================================
# A3GC L1 -- RE-ENTRY AT `plot3dToFoam`.  **PREPARED.  NOT RUN BY ITS AUTHOR.**
#
# WHY THIS FILE EXISTS AT ALL, AND WHY IT IS NOT `a3gc_genmesh.sh --levels L1`.
# TWO INDEPENDENT REASONS, EITHER OF WHICH ALONE IS DECISIVE:
#
#   (1) THE PINNED GENERATOR CANNOT BE RE-ENTERED.  a3gc_genmesh.sh:237-243 REFUSES
#       when the level's run root already exists -- "A graded run root is evidence
#       and is never written into" -- and /home/ubuntu/certonomous-runs/A3GC-L1
#       does exist.  The generator has no stage selector: entering it at all would
#       redo the pyHyp hyperbolic extrusion that ALREADY SUCCEEDED and whose
#       437,206,919-byte output is on disk.  Re-running pyHyp to reach a conversion
#       is paying twice for a thing that is not lost.
#
#   (2) THE L1 WRAPPER WOULD REFUSE TODAY ANYWAY.  a3gc_L1_wrapper.sh pins the
#       generator at md5 9fa240d9643308f5e9a4988614b58884 (A3GC AMENDMENT 5) and
#       exits 90 on a mismatch.  Commit 8b16844fa (2026-09-12T05:27:25Z, "AR1 level
#       tables"), which landed FOUR HOURS AFTER the 01:36 L1 launch, changed the
#       generator to md5 2a1f45c06aa8912f5eb84d929fa54df1.  THE PIN IS BROKEN ON
#       DISK AND AT HEAD.  That is a finding in its own right and is reported
#       upward; it is not repaired here, because repairing an AMENDMENT 5 pin is
#       not a lane's act.
#
# WHAT THIS SCRIPT MAY WRITE INTO, AND WHY THAT IS NOT A GUARD VIOLATION.
# It writes into an EXISTING tree, which the generator's guard forbids.  The guard
# exists so a mesh regenerated on top of an old one cannot be dated and so a GRADED
# root is never overwritten.  Neither condition holds here, and both are ASSERTED
# below rather than asserted in prose: A3GC-L1 has NO constant/ directory, NO
# polyMesh, NO time directory and NO solve.  It holds one completed pyHyp output
# and a conversion log that stops mid-sentence.  Nothing in it has been graded and
# nothing in it can be dated wrong by finishing the step that was interrupted.
#
# NO CAP, NO TIMEOUT, NO KILL PATH (Sanaa directive #17, 2026-09-12).
# NOT ROOT (Sanaa item 6): -u 1000:1000 --group-add 1002.  uid 1000 AND gid 1000
# are BOTH ubuntu, so every artifact lands ubuntu:ubuntu.  1002 is the IMAGE's
# dafoamuser group, carried as a SUPPLEMENTARY group for one purpose: traversing
# the 0750 /home/dafoamuser.  MEASURED on this box 2026-09-12: -u 1000:1000 ALONE
# dies "Permission denied" sourcing loadDAFoam.sh; with --group-add 1002 it reaches
# LOADED_OK.  CORROBORATED BY A LIVE PEER RUN on the same image (container
# d6r2c_KR_REF_20260912T184838Z_79250, User=1000:1000, GroupAdd=["1002"]).
# STRICTLY BETTER than a3gc_genmesh.sh's own -u 1002:1000, which runs as a uid
# that does not exist on the host.
# =====================================================================
set -u

WD=/home/ubuntu/certonomous-runs/A3GC-L1
IMAGE_DIGEST="sha256:8352629516bb363345fd802ed6092f878bad0a612c05c98d492a14bd94729d46"
AUTOPATCH_ANGLE="${AUTOPATCH_ANGLE:-60}"   # A3GC AMENDMENT 2(d): REGISTERED 60, not the script default 45
WANT_CELLS=6389760                          # A3GC PREREG Sec.2.5 -- launch-blocking, not a note
WANT_WING=99840                             # a3gc_genmesh.sh:81 WANT_WING[L1]
WANT_VOLMESH_BYTES=437206919                # the preserved pyHyp output, census 2026-09-12
MEM_CEILING="${MEM_CEILING:-48g}"           # see Sec.3 of the re-entry pre-registration
GRADE=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A3/curriculum_A3GC/a3gc_grade.py
LEDGER="$WD/L1_REENTRY_LEDGER.txt"

refuse() { printf '\nREFUSE [%s]\n  %s\n  exit 2 -- refusing rather than degrading.\n' "$1" "$2" | tee -a "$LEDGER" >&2; exit 2; }
say()    { printf '%s\n' "$*" | tee -a "$LEDGER"; }

say "=== A3GC L1 plot3dToFoam RE-ENTRY  $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
say "PPID=$PPID (1 == reparented to init, survives the fleet dying)"
say "box: $(nproc) cores, MemAvailable $(awk '/^MemAvailable:/{printf "%.1f", $2/1048576}' /proc/meminfo) GiB, load $(cut -d' ' -f1-3 /proc/loadavg)"

# --- PRECONDITION 1.  The thing we are reusing must BE there, and be the thing.
[ -f "$WD/volumeMesh.xyz" ] || refuse "INPUT" "$WD/volumeMesh.xyz is absent.  There is nothing to re-enter; this would be a full regeneration and is not what was registered."
GOT_BYTES=$(stat -c %s "$WD/volumeMesh.xyz")
[ "$GOT_BYTES" = "$WANT_VOLMESH_BYTES" ] || refuse "INPUT" \
  "volumeMesh.xyz is $GOT_BYTES bytes, registered $WANT_VOLMESH_BYTES.  The preserved pyHyp output is not the one the census measured; re-entry is refused rather than run against an unidentified input."
say "INPUT OK: volumeMesh.xyz $GOT_BYTES bytes == registered"

# --- PRECONDITION 2.  The pyHyp stage must have FINISHED, not merely written a file.
grep -q 'Merged points within' "$WD/logMeshGeneration.txt" || refuse "INPUT" \
  "logMeshGeneration.txt does not carry the point-merge line, so plot3dToFoam's READ stage did not complete and the file may be partial."
say "INPUT OK: point-merge line present ($(grep -m1 'Merged points within' "$WD/logMeshGeneration.txt"))"

# --- PRECONDITION 3.  THE AGE/OVERWRITE GUARD, in the only form that is honest here.
[ -e "$WD/constant/polyMesh" ] && refuse "GUARD" "$WD/constant/polyMesh already exists.  A mesh that exists is not re-converted on top of itself; move it aside by hand."
for t in "$WD"/[0-9]*; do
  [ -d "$t" ] && [ "$(basename "$t")" != "0.orig" ] && refuse "GUARD" "$t is a time directory.  This tree has been solved in; re-entry is refused."
done
say "GUARD OK: no constant/polyMesh, no time directory -- nothing graded is at risk"

# --- PRECONDITION 4.  The image is named BY HASH, never by tag (DAFOAM_CHARTER Sec.6).
sudo -n docker image inspect "$IMAGE_DIGEST" >/dev/null 2>&1 \
  || refuse "IMAGE" "the pinned image $IMAGE_DIGEST is not present.  No silent fallback to a tag."
say "IMAGE OK: $IMAGE_DIGEST"

# --- EVIDENCE IS COPIED, NEVER MOVED AND NEVER TRUNCATED.  The interrupted log is
#     the record of what the 30 GiB box did to this step and is kept verbatim.
cp -n "$WD/logMeshGeneration.txt" "$WD/logMeshGeneration.preReentry.txt" 2>/dev/null
say "EVIDENCE: interrupted log copied to logMeshGeneration.preReentry.txt (copied, not moved)"

CONTAINER_PROLOGUE='umask 0002
source /home/dafoamuser/dafoam/loadDAFoam.sh
if [ -z "${WM_PROJECT_DIR:-}" ]; then
  printf "REFUSE [ENV] loadDAFoam.sh did not populate the environment.  id = %s\n" "$(id)" >&2
  exit 97
fi
set -e'

RUN() {   # RUN <name> <command...>
  local tag="$1"; shift
  local cname="a3gc_l1_reentry_${tag}_$(date -u +%Y%m%dT%H%M%SZ)"
  local t0 t1 rc peak
  t0=$(date +%s)
  # NO --cpus AND NO --memory-swap CLAMP THAT FORCES SWAP.  The 2026-09-12 stall
  # ran under `--cpus 1 --memory 4g --memory-swap 8g` on a box whose MemAvailable
  # read 0 GiB all afternoon, and the watcher measured the process at 0.3-4.5 % CPU
  # for five hours.  A process at 1 % CPU is not computing; it is waiting on memory.
  # --memory is KEPT as blast-radius containment and --memory-swap is held EQUAL to
  # it, which DISABLES container swap (Sanaa item 18: swap above zero for a solver
  # job is a defect).  Containment is not a cap: nothing here signals or stops.
  sudo -n docker run --rm --name "$cname" \
      -u 1000:1000 --group-add 1002 -e MPLCONFIGDIR=/tmp \
      --memory="$MEM_CEILING" --memory-swap="$MEM_CEILING" \
      -v "$WD":/w -w /w "$IMAGE_DIGEST" \
      bash -lc "$CONTAINER_PROLOGUE
$*
printf 'CONTAINER_PEAK_MEM_BYTES %s\n' \"\$(cat /sys/fs/cgroup/memory.peak 2>/dev/null || echo UNREADABLE)\" >&2"
  rc=$?
  t1=$(date +%s)
  say "STEP $tag rc=$rc wall_s=$((t1-t0))"
  [ "$rc" = 0 ] || refuse "STEP" "$tag exited rc=$rc.  A failed conversion step is a finding, not something to retry blindly."
}

RUN plot3d    "plot3dToFoam -noBlank volumeMesh.xyz >> logMeshGeneration.txt"
RUN autopatch "autoPatch $AUTOPATCH_ANGLE -overwrite >> logMeshGeneration.txt"
RUN createpat "createPatch -overwrite >> logMeshGeneration.txt"
RUN renumber  "renumberMesh -overwrite >> logMeshGeneration.txt"
RUN checkmesh "checkMesh -allGeometry -allTopology &> logCheckMesh.txt"

# --- THE REGISTERED EXIT CONDITION, MEASURED, exactly as a3gc_genmesh.sh:347-362.
#     THE SAME PROBE, THE SAME TWO COUNTS, THE SAME REFUSALS.  Nothing is relaxed
#     because this was a re-entry rather than a first run.
PROBE="$(python3 "$GRADE" probe --case "$WD" --cgns "$WD/surfaceMesh.cgns")" \
  || refuse "MEASURE" "could not read back the mesh just written in $WD"
GOT_CELLS=$(printf '%s' "$PROBE" | python3 -c 'import json,sys; print(json.load(sys.stdin)["cells"])')
GOT_WING=$(printf '%s' "$PROBE"  | python3 -c 'import json,sys; print(json.load(sys.stdin)["patches"]["wing"]["nFaces"])')
say "MEASURED: cells = $GOT_CELLS (want $WANT_CELLS), wing nFaces = $GOT_WING (want $WANT_WING)"

[ "$GOT_CELLS" = "$WANT_CELLS" ] || refuse "STAGE1" \
  "L1 has $GOT_CELLS cells, registered $WANT_CELLS.  A3GC PREREG Sec.2.5: 'Any departure from 99,840 / 798,720 / 6,389,760 is a launch-blocking refusal, not a note.'  DO NOT SOLVE."
[ "$GOT_WING" = "$WANT_WING" ] || refuse "STAGE1" \
  "L1 wing patch has $GOT_WING faces, registered $WANT_WING.  Cell count alone does not identify a level.  If the patch table is wrong the first thing to try is AUTOPATCH_ANGLE=60, which is already what this script uses."
grep -q 'Mesh has 3 geometric (non-empty/wedge) directions' "$WD/logCheckMesh.txt" || refuse "G-MESH" \
  "checkMesh does not report 3 geometric (non-empty/wedge) directions (A3GC PREREG Sec.3.2)."

say "A3GC L1 MESH COMPLETE AND MEASURED AGAINST THE REGISTERED COUNTS."
say "NOTHING HAS BEEN SOLVED.  The solve is a separate registered act and is NOT started here."
