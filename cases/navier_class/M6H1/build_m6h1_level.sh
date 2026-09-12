#!/bin/bash
# M6H1 BUILD DRIVER — one level of the hyperbolic (C/O) family, surface to OpenFOAM mesh.
#
# WHAT THIS FILE IS.  `cases/navier_class/M6H1/` held five grading instruments and NO
# executable route: no mesh generator, no surface→PLOT3D step, no case writer, no solve
# driver.  A `launch_cmd` naming a script that does not exist is recorded LAUNCHED and then
# dies, because the runner's exec check only verifies that `cwd` exists.  This is the
# generator half of that route.  **It builds a mesh.  It runs NO solver.**
#
# PATTERN TAKEN FROM `cases/M6SR/build_m6sr_l1.sh`, WHICH IS HARDENED AND WHOSE SCARS ARE
# WORTH INHERITING.  M6SR is the same route on different numbers; the numbers here come
# from `verification/campaign/M6H1_PREREGISTRATION.md` and from nowhere else.
#
# §9.2-CLASS MECHANICS, OBSERVED HERE LINE BY LINE:
#   * ASSERTIONS DO NOT GATE.  There is no `assert` and no bare `set -e` in this file.
#     Every check is `... || { echo "ABORT: <what>"; exit N; }`.  A guard set that is
#     entirely assert-based is one interpreter flag away from absent (L-475).
#   * `setsid timeout cmd` EXITS 0 FOR EVERY OUTCOME.  Every rc in this file is captured
#     INSIDE the wrapper that ran the command and written to a file; none is taken from
#     around a `setsid` or a `docker run` line.
#   * SHAS ARE READ BACK BY SUBJECT LINE, one named file per invocation, never by position
#     in a batch (L-479).
#   * `grep ... log.* | tail -1` IS A COIN FLIP under multi-file output (L-559 family).
#     Every reading here names ONE artifact by explicit path.
#   * `pkill` and pattern-`pgrep` are BANNED (L-559).  Containers are stopped by their
#     recorded name and by nothing else.
#
# WHAT IT REFUSES, AT ZERO COST, BEFORE ANY COMPUTE:
#   1. an image whose DIGEST is not the pinned one — a tag can be re-pointed between the
#      check and the run; a digest cannot;
#   2. a pyHyp, plot3dToFoam, autoPatch, createPatch or renumberMesh whose path+sha256 is
#      not the pinned one — this driver BUILDS THE MESH THE GATES GRADE, so a pin on the
#      solver alone pins half the instrument;
#   3. a level directory that already holds `0`, a time directory, or a previous
#      `volumeMesh.xyz` — rule 4's guard, applied to the build;
#   4. a surface that does not pass H-G0, graded by the frozen instrument and not by this
#      driver's opinion;
#   5. a march whose pyHyp Min Quality clause does not PASS, graded by the frozen
#      instrument — because pyHyp EXITS 0 ON A MESH THAT IS ENTIRELY NaN (§14.5), and
#      every rule-4 completion clause is satisfied by such a run.
#
# COST.  Unit: core-minutes (wall s × ranks ÷ 60).  Every step here runs at 1 rank —
# pyHyp is serial and so are the OpenFOAM mesh utilities.  Dollars are DERIVED, NOT
# MEASURED, at the owner-stated c7a.4xlarge $0.0513/core-h: this box cannot read its own
# billing (`COMPUTE_BUDGET_CHARTER` §5), so any dollar figure originating here is
# REPORTED-BY-OWNER.  §9 registers ≈ 25 core-min for the H-L1 build; the measured surface
# step is 0.14 s and the measured march is minutes, so that estimate is expected to be
# high by orders and the estimate-versus-actual row is owed to `docs/COST_CALIBRATION.md`
# at completion (rule 12).  **No cap kills any run** — Sanaa's standing ruling, §9.
#
# SUBMISSIONS ARE PARKED (rule 7).  This driver sends nothing anywhere.
# ==========================================================================================
set -u
set -o pipefail

LEVEL="${1:-}"
REPO="${2:-/home/ubuntu/Certonomous}"
case "$LEVEL" in
  L1|L2|L3) ;;
  *) echo "usage: build_m6h1_level.sh <L1|L2|L3> [repo_root]"; exit 64;;
esac

# ---------------------------------------------------------------- REGISTERED / PINNED
# §4, and NOT movable from the environment.
declare -A NORMAL_N=( [L1]=97 [L2]=129 [L3]=161 )
S0=1.6540e-6                 # §4, HELD ACROSS LEVELS on purpose: it fixes y+ (§14.2)
MARCH_DIST=16.152            # §4, 25 x MAC 0.64607
# pyHyp's cMax is a BUILD parameter, not a registered one.  0.1 is the DAFoam tutorial's,
# tuned for its own s0 = 1e-4 — sixty times coarser at the wall than ours — and it does NOT
# transfer: measured 37 bad layers at 0.1, 2 at 1.0, 13 at 3.0, everything else registered.
# L-566: an inherited parameter is a parameter nobody has checked.
CMAX=1.0

PINNED_IMAGE_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
PINNED_IMAGE_REF=dafoam-idwarp-rot:v1

# path <space> sha256 — one file per line, read back BY SUBJECT LINE below.
read -r -d '' PINS <<'EOP'
python /home/dafoamuser/dafoam/packages/miniconda3/bin/python ae1e0962caeb115196918c6d6d6c55611e92dc580c2796f47f0e9a812377a8fe
pyhyp_module /home/dafoamuser/dafoam/packages/miniconda3/lib/python3.10/site-packages/pyhyp/__init__.py ae747e8b269ef2cf654ae8caebf1e4baabf255f289a877a09f26a0ed8599b7ef
pyhyp_hyp_so /home/dafoamuser/dafoam/packages/miniconda3/lib/python3.10/site-packages/pyhyp/hyp.so 53744d52dbb56ef82f7894ec2573c82d1501ff4acf96f8cfe8767335c7317def
plot3dToFoam /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506/platforms/linux64GccDPInt32Opt/bin/plot3dToFoam f455b4372636c6bf0fbd9fa82caf304f02e15be34f39693fbc68e566ac9cb040
autoPatch /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506/platforms/linux64GccDPInt32Opt/bin/autoPatch 88b07730b457ade414c884a1566eb457685833672ab755ca6f21f715626e15d6
createPatch /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506/platforms/linux64GccDPInt32Opt/bin/createPatch fec27bfceff73a6968b431dd791ba81ecf50729f22072eeb6f765106b059835f
renumberMesh /home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506/platforms/linux64GccDPInt32Opt/bin/renumberMesh 6a7a2278ac33390e931cb5b82f71055e60a5e10d40c080df4270e70e6ae43efd
EOP

RUN_ROOT="$REPO/verification/runs/M6H1_runs"
LVL="$RUN_ROOT/$LEVEL"
GEN="$REPO/cases/navier_class/M6H1/make_m6h1_surface.py"
IG0="$REPO/cases/navier_class/M6H1/measure_te_base.py"
IG1Q="$REPO/cases/navier_class/M6H1/read_min_quality.py"
IG1C="$REPO/cases/navier_class/M6H1/read_cell_count.py"

say(){ echo "[$(date -u +%H:%M:%SZ)] $*"; }
abort(){ echo "ABORT: $1"; exit "${2:-1}"; }

# ---------------------------------------------------------------- 0. the instruments exist
for f in "$GEN" "$IG0" "$IG1Q" "$IG1C"; do
  [ -f "$f" ] || abort "missing instrument or generator: $f. THE GRADING PATH IS PART OF THE BUILD; a build whose graders are absent produces an ungradeable mesh." 2
done

# ---------------------------------------------------------------- 1. the run root guard
# Rule 4's guard applied to the build: a level directory that already holds a mesh is NOT
# overwritten, because the next reader cannot tell which run produced what is in it.
if [ -e "$LVL" ]; then
  for stale in 0 constant/polyMesh volumeMesh.xyz pyhyp.log; do
    [ -e "$LVL/$stale" ] && abort "$LVL/$stale already exists. This driver REFUSES a level directory that already holds a build. Move it aside with a name that says why it was preserved; nothing here deletes anything." 3
  done
fi
mkdir -p "$LVL" || abort "cannot create $LVL" 3
date -u +%s > "$LVL/LEVEL_CREATED_EPOCH"

# ---------------------------------------------------------------- 2. docker reachable
DRUN_MODE=""
if docker version --format '{{.Server.Version}}' >/dev/null 2>&1; then
  DRUN_MODE=bare
elif sg docker -c "docker version --format '{{.Server.Version}}'" >/dev/null 2>&1; then
  DRUN_MODE=sg
else
  abort "docker unreachable both bare and through 'sg docker -c'. This grades THE DRIVER'S ABILITY TO RUN and nothing about the M6 — BLOCKED, not GATE FAIL." 5
fi
# M6SR item 35: on the sg branch the whole command is ONE STRING for sg to run; on the bare
# branch it must NOT be re-quoted into a single argument.  The two branches are written out
# separately rather than through a variable that expands correctly on only one of them.
drun(){
  if [ "$DRUN_MODE" = bare ]; then docker "$@"; else
    local q; q=$(printf ' %q' "$@"); sg docker -c "docker$q"; fi
}
say "docker reachable via $DRUN_MODE"

# ---------------------------------------------------------------- 3. image digest pin
RESOLVED=$(drun image inspect --format '{{index .RepoDigests 0}}' "$PINNED_IMAGE_REF" 2>/dev/null | sed 's/.*@//')
[ "$RESOLVED" = "$PINNED_IMAGE_DIGEST" ] \
  || abort "IMAGE DIGEST MISMATCH. '$PINNED_IMAGE_REF' resolves to '${RESOLVED:-ABSENT}'; this driver pins $PINNED_IMAGE_DIGEST. A TAG CAN BE RE-POINTED BETWEEN THE CHECK AND THE RUN; A DIGEST CANNOT. REFUSED AT ZERO COST." 10
IMG="$PINNED_IMAGE_DIGEST"
say "image digest VERIFIED: $RESOLVED"

# ---------------------------------------------------------------- 4. binary pins
# Read back BY SUBJECT LINE: one named file per invocation, never by position in a batch.
OBS="$LVL/BUILD_PIN_OBSERVED.txt"; : > "$OBS"
while read -r tag path want; do
  [ -n "$tag" ] || continue
  got=$(drun run --rm -u 1002:1002 "$IMG" bash -lc "sha256sum '$path' 2>/dev/null | cut -d' ' -f1" 2>/dev/null | tr -d '\r\n')
  echo "$tag $path ${got:-ABSENT}" >> "$OBS"
  [ "$got" = "$want" ] || abort "PIN MISMATCH for $tag at $path: observed '${got:-ABSENT}', pinned '$want'. This driver BUILDS THE MESH THE GATES GRADE — a different binary is a different mesh. REFUSED AT ZERO COST. Observed set written to $OBS." 10
done <<< "$PINS"
say "all $(grep -c . "$OBS") binary pins VERIFIED"

# ---------------------------------------------------------------- 5. B1 — the surface
T0=$SECONDS
python3 "$GEN" "$LEVEL" "$REPO" "$LVL/mesh" > "$LVL/log.make_surface" 2>&1
rc=$?
echo "MAKE_SURFACE_RC=$rc" > "$LVL/make_surface_rc.txt"
[ "$rc" -eq 0 ] || abort "the surface generator exited $rc; see $LVL/log.make_surface. Its own build-time self-checks REFUSE rather than write a surface they cannot vouch for." 6
SURF_XYZ="$LVL/mesh/m6h1_surface_${LEVEL}.xyz"
SURF_STL="$LVL/mesh/m6h1_surface_${LEVEL}.stl"
[ -s "$SURF_XYZ" ] && [ -s "$SURF_STL" ] || abort "the generator exited 0 but $SURF_XYZ or $SURF_STL is missing or empty. AN EXIT CODE IS NOT AN ARTIFACT." 6
say "B1 surface built in $((SECONDS-T0)) s -> $SURF_XYZ"

# ---------------------------------------------------------------- 6. H-G0, BY THE INSTRUMENT
python3 "$IG0" "$SURF_STL" > "$LVL/log.H-G0" 2>&1
g0=$?
echo "H_G0_RC=$g0" > "$LVL/H-G0_rc.txt"
case "$g0" in
  0) say "H-G0 PASS (all three registered clauses) — see $LVL/log.H-G0" ;;
  1) abort "H-G0 GATE FAIL on the generated surface. The level is BLOCKED and NOTHING IS MARCHED. Reported, not adjusted; see $LVL/log.H-G0." 7 ;;
  *) abort "H-G0's instrument REFUSED (rc $g0) — its planted controls did not establish that it can see a known non-zero, so its verdict would not be evidence. See $LVL/log.H-G0." 7 ;;
esac

# ---------------------------------------------------------------- 7. B2 — the pyHyp march
cat > "$LVL/mesh/march.py" <<PYEOF
import sys, time, traceback
from pyhyp import pyHyp
opts = {
    "inputFile": "m6h1_surface_${LEVEL}.xyz", "fileType": "PLOT3D",
    "unattachedEdgesAreSymmetry": True, "outerFaceBC": "farfield",
    "autoConnect": True, "BC": {}, "families": "wall",
    "N": ${NORMAL_N[$LEVEL]},          # M6H1 section 4
    "s0": ${S0},                        # M6H1 section 4, HELD ACROSS LEVELS
    "marchDist": ${MARCH_DIST},         # M6H1 section 4, 25 MAC
    "ps0": -1.0, "pGridRatio": -1.0, "cMax": ${CMAX},
    "epsE": 1.0, "epsI": 2.0, "theta": 3.0,
    "volCoef": 0.25, "volBlend": 0.0005, "volSmoothIter": 100, "kspreltol": 1e-4,
}
t0 = time.time()
try:
    h = pyHyp(options=opts); h.run(); h.writePlot3D("volumeMesh.xyz")
    print("MARCH_WROTE wall=%.1f s" % (time.time() - t0)); sys.exit(0)
except Exception:
    traceback.print_exc(); print("MARCH_RAISED"); sys.exit(7)
PYEOF
cat > "$LVL/mesh/run_march.sh" <<'SHEOF'
#!/bin/bash
set +u
source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1
cd /work
T0=$SECONDS
python march.py > pyhyp.log 2>&1
RC=$?
# rc CAPTURED INSIDE THE WRAPPER, never from around the docker line.
echo "PYHYP_RC=$RC"                       >  pyhyp_rc.txt
echo "PYHYP_WALL_S=$(( SECONDS - T0 ))"   >> pyhyp_rc.txt
echo "PYHYP_RC_WRITTEN_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> pyhyp_rc.txt
SHEOF
chmod 0777 "$LVL/mesh/run_march.sh" "$LVL/mesh/march.py" 2>/dev/null
chmod 0777 "$LVL/mesh" 2>/dev/null
T1=$SECONDS
drun run --rm --name "m6h1_${LEVEL}_march" -u 1002:1002 -v "$LVL/mesh:/work" -w /work \
    "$IMG" bash -lc "/work/run_march.sh" > "$LVL/log.docker_march" 2>&1
say "B2 pyHyp container returned after $((SECONDS-T1)) s (THE CONTAINER'S rc IS NOT THE MARCH'S rc)"
[ -f "$LVL/mesh/pyhyp_rc.txt" ] || abort "no pyhyp_rc.txt: the wrapper did not complete, so the march's own exit status is UNKNOWN. A container that returned is not a march that ran." 8
grep -q '^PYHYP_RC=0$' "$LVL/mesh/pyhyp_rc.txt" \
  || abort "pyHyp exited non-zero: $(grep '^PYHYP_RC=' "$LVL/mesh/pyhyp_rc.txt"). See $LVL/mesh/pyhyp.log." 8
[ -s "$LVL/mesh/volumeMesh.xyz" ] || abort "PYHYP_RC=0 but volumeMesh.xyz is missing or empty." 8

# ---------------------------------------------------------------- 8. H-G1 pyHyp CLAUSE
# 🔴 THIS IS NOT A FORMALITY.  MEASURED (section 14.5): pyHyp EXITED 0, WROTE 83,642,151
# BYTES, AND PRODUCED A MESH THAT WAS ENTIRELY NaN.  Every rule-4 completion clause is
# satisfied by such a run.  Nothing else in the gate stack catches it.
python3 "$IG1Q" "$LVL/mesh/pyhyp.log" > "$LVL/log.H-G1_pyhyp" 2>&1
g1=$?
echo "H_G1_PYHYP_RC=$g1" > "$LVL/H-G1_pyhyp_rc.txt"
case "$g1" in
  0) say "H-G1 pyHyp clause PASS — Min Quality > 0 at every marched layer" ;;
  1) abort "H-G1 pyHyp clause: NOT A RESULT for this level. The march produced a mesh with a non-positive Min Quality and pyHyp reported success. Reported, not adjusted; see $LVL/log.H-G1_pyhyp. NOTHING IS CONVERTED." 9 ;;
  *) abort "H-G1's pyHyp instrument REFUSED (rc $g1); its verdict would not be evidence. See $LVL/log.H-G1_pyhyp." 9 ;;
esac

say "BUILD REACHED THE END OF ITS IMPLEMENTED STEPS."
cat <<'NOTE'

NOT YET IMPLEMENTED IN THIS DRIVER, AND SAID HERE RATHER THAN LEFT TO BE DISCOVERED:
  B3  plot3dToFoam -> autoPatch -> createPatch -> renumberMesh, and the system/ dictionaries
      those four need.  M6SR measured that createPatch requires system/createPatchDict and
      that createPatch and renumberMesh build an fvMesh and therefore read fvSchemes and
      fvSolution, while plot3dToFoam and autoPatch need controlDict alone.  Those
      dictionaries have to be staged for M6H1 with their own shas pinned, and THEY DECIDE
      THE PATCH NAMES, which section 7's screen judges.
  B4  checkMesh and the H-G1 checkMesh clause via read_cell_count.py.
  B5  the case writer and the rhoSimpleFoam driver.  NO SOLVER RUNS FROM THIS FILE.
A driver that stopped silently here would look like a build that succeeded.
NOTE
exit 0
