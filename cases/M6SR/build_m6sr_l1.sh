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

set +u
set +e

RR=${M6SR_RUN_ROOT:-/home/ubuntu/Certonomous/verification/runs/M6SR_runs}
CR=/home/ubuntu/certonomous-runs
MASTER="$CR/A3-onera-m6-transonic/m6_surfaceMesh_fine.cgns"
MASTER_SHA=197efa09d838b276a8967da9532d9c4d57edca18cb777bd640257606d2d83327
IMG=${M6SR_IMAGE:-dafoam-idwarp-rot:v1}
LEVEL=L1

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
if [ $BARE_RC -eq 0 ]; then DRUN="docker"; else DRUN="sg docker -c"; fi
say "docker reachable (bare rc=$BARE_RC, sg rc=$SG_RC); using '$DRUN'"

cp -- "$MASTER" "$RR/$LEVEL/work/m6_surfaceMesh_fine.cgns" || abort "master copy-out failed" 3
chmod 777 "$RR/$LEVEL/work" || abort "could not make the work directory writable to the container uid" 3

# One helper for every containerised step.  rc IS CAPTURED INSIDE THE WRAPPER (Section 9.2)
# -- `setsid timeout cmd` exits 0 for every outcome, so an rc taken from around the setsid
# line is meaningless.  The cap is enforced by `timeout` and an overrun STOPS THE RUN.
run_in_container(){
  local tag="$1" tmo="$2" cmd="$3"
  local t0 t1 rc wall
  t0=$(date +%s)
  timeout "${tmo}"s $DRUN "docker run --rm --name m6sr_${tag}_$$ -u 1002:1002 \
      -v '$RR/$LEVEL/work':/home/dafoamuser/mount -w /home/dafoamuser/mount $IMG \
      bash -c 'set +u; source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; \
               $cmd; echo \"WRAPPER_RC=\$?\" > RC_${tag}.txt'" \
      > "$RR/$LEVEL/log.$tag" 2>&1
  rc=$?
  t1=$(date +%s); wall=$((t1-t0))
  $DRUN "docker rm -f m6sr_${tag}_$$" >/dev/null 2>&1
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
