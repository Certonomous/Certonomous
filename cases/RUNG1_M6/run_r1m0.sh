#!/bin/bash
# =====================================================================================
# R1-M0 -- THE ONERA M6 ADMISSION PROBE.  DRIVER.
#
# Frozen registration: verification/campaign/RUNG1_M6_PREREGISTRATION.md §5,
# committed at c7f99bb1 (blob sha256 verified by the driver against the working file).
#
# THE QUESTION, IN THE REGISTRATION'S OWN WORDS (§5):
#   "DOES A pyHyp-GENERATED, WALL-RESOLVED ONERA M6 FAMILY CLEAR 70 DEGREES AT ALL?
#    NOBODY KNOWS.  IT HAS NEVER BEEN MEASURED."
#
# WHAT IT DOES: generate ONE coarse wall-resolved M6 with pyHyp, convert it, run
# checkMesh.  Patch identity is IRRELEVANT here -- non-orthogonality and skewness are
# CELL GEOMETRY -- so the cheapest converter is used (plot3dToFoam alone; no autoPatch,
# no createPatch, no renumberMesh) and NO FIDELITY CLAIM WHATEVER ATTACHES TO IT.
#
# LABEL, carried here so no reader of this script can mistake it (§5):
#   NO VERDICT OF THE FIXED VOCABULARY ATTACHES TO R1-M0.  It is an admissibility
#   measurement that gates a freeze.  IT GRADES NOTHING.  Neither outcome is a failure:
#   ">70" kills branches (a1)/(a2) and saves the ladder from a dead branch, which is a
#   real result; "<=70" discharges MESH_STANDARD §8.1's build-before-freeze.
#
# COST, REGISTERED AND NOT ALTERABLE HERE (§5):
#   estimate 2.0 core-min; HARD CAP 6.0 core-min = $0.0051 DERIVED;
#   structural enforcement `timeout 360` at 1 rank.  AN OVERRUN STOPS THE RUN.
#   It does not get a new budget (rule 12).
#
# DOCKER CREDENTIALS -- why every docker call is wrapped in `sg docker -c`:
#   supplementary group membership is fixed at process start, and the shared queue
#   daemon predates the docker-group grant, so every process it launches inherits a
#   group set without gid 113.  `sg docker -c` acquires it AT EXEC inside our own
#   driver, disturbing nothing else.  THE DAEMON IS NOT RESTARTED (shared
#   infrastructure carrying other teams' rows; a restart is the chief's call) and sudo
#   is NOT used (Sanaa's grant was a group membership, not root).
# =====================================================================================
set +u

RR=/home/ubuntu/Certonomous/verification/runs/RUNG1_M6_runs/M0_pyhyp_admission
LADDER=/home/ubuntu/Certonomous/verification/runs/RUNG1_M6_runs
CASE=/home/ubuntu/Certonomous/cases/RUNG1_M6
REPO=/home/ubuntu/Certonomous
CR=/home/ubuntu/certonomous-runs
IMG=dafoam-idwarp-rot:v1
CNAME=rung1_m6_m0_pyhyp
FOAM_BASHRC=/usr/lib/openfoam/openfoam2606/etc/bashrc

CAP_S=360                  # STRUCTURAL CAP: 1 rank x 360 s / 60 = 6.0 core-min (§5)
RANKS=1
S0=1.319e-06               # REQUESTED first-cell height.  AN INPUT.  NEVER A MEASUREMENT.
NDECK=93                   # pyHyp node count -> 92 cell layers
PREREG_COMMIT=c7f99bb1
PREREG_PATH=verification/campaign/RUNG1_M6_PREREGISTRATION.md

T0=$(date +%s)
say(){ echo "[$(date -u +%H:%M:%SZ)] $*"; }
rem(){ echo $(( CAP_S - ( $(date +%s) - T0 ) )); }
fail(){ say "STOP: $1"; mkdir -p "$RR" 2>/dev/null; echo "$1" > "$RR/STOPPED.txt"; exit "$2"; }

say "R1-M0 ONERA M6 admission probe -- driver start"
say "credential set: uid=$(id -u) gid=$(id -g) groups=$(id -G)"

# -------------------------------------------------------------------------------------
# 0.  THE RUN-ROOT GUARD (rule 4).  A guard refuses a case where the run root, or a `0`
#     or numeric time directory under it, already exists.  NOTHING IS WRITTEN ON REFUSAL.
# -------------------------------------------------------------------------------------
for p in "$RR" "$LADDER/L1" "$LADDER/L2" "$LADDER/L3"; do
  if [ -e "$p" ]; then
    say "REFUSE: a path registered ABSENT in prereg §11 already exists: $p"
    say "Nothing written.  This is reported to the supervisor, never run into."
    exit 3
  fi
done
mkdir -p "$RR/work" "$RR/controls" "$RR/foam/system" "$RR/foam/constant" || exit 3
date +%s > "$RR/RUN_ROOT_CREATED_EPOCH"
CREATED=$(cat "$RR/RUN_ROOT_CREATED_EPOCH")
say "run root created at epoch $CREATED: $RR"

# -------------------------------------------------------------------------------------
# 1.  THE FREEZE CHECK.  The grading path is fixed at the pre-registration commit
#     (rule 2): verify the frozen file IS the file that ran, by hashing the working file
#     against the committed blob.  A mismatch STOPS the run before any compute.
# -------------------------------------------------------------------------------------
WT_SHA=$(sha256sum "$REPO/$PREREG_PATH" | cut -d' ' -f1)
BLOB_SHA=$(cd "$REPO" && git cat-file -p "$PREREG_COMMIT:$PREREG_PATH" 2>/dev/null | sha256sum | cut -d' ' -f1)
say "prereg sha256 working=$WT_SHA committed($PREREG_COMMIT)=$BLOB_SHA"
{ echo "prereg_path=$PREREG_PATH"; echo "prereg_commit=$PREREG_COMMIT";
  echo "working_sha256=$WT_SHA"; echo "committed_blob_sha256=$BLOB_SHA"; } > "$RR/FREEZE_CHECK.txt"
[ -n "$BLOB_SHA" ] && [ "$WT_SHA" = "$BLOB_SHA" ] || \
  fail "FREEZE MISMATCH: the file on disk is not the file committed at $PREREG_COMMIT. No compute run." 6

# -------------------------------------------------------------------------------------
# 2.  PLANTED CONTROLS ON THE checkMesh READER -- rule 3 and prereg §9.  THESE RUN
#     BEFORE ANY COMPUTE, so a control failure costs zero core-minutes.
#
#     A ZERO -- OR ANY NUMBER -- FROM A READER NOT SHOWN ABLE TO SEE A NON-ZERO IS NOT
#     EVIDENCE.  The two §9 plants are C1/C2 (the `=` and `:` label forms; a reader
#     matching only `=` sees 745 of this box's 885 checkMesh logs and silently misses
#     exactly the 140 pathological ones) and C3 (Min volume != Max volume must give a
#     non-trivial derived ratio, never 1).
#
#     C4 IS THE ONE THAT MATTERS FOR THIS PROBE.  Its control artifact is a REAL
#     production log on this box whose numeric maximum is 84.6437 degrees and whose own
#     verdict line reads `Non-orthogonality check OK.`  A reader that takes the verdict
#     line records a 90-degree mesh as passing.  The control requires the reader to
#     report above_70 on it.
# -------------------------------------------------------------------------------------
CTL_EQ="$REPO/verification/runs/F16_runs/coarse/log.checkMesh"
CTL_CO="$REPO/verification/runs/F13_ONERA_M6_runs/mesh/m1/log.checkMesh"
cp "$CTL_EQ" "$RR/controls/control_eq_form.log" || fail "control (= form) copy failed" 4
cp "$CTL_CO" "$RR/controls/control_colon_form.log" || fail "control (: form) copy failed" 4
say "running the checkMesh reader's planted controls (§9) -- before any compute"
python3 "$CASE/read_checkmesh.py" \
  --selftest-eq    "$RR/controls/control_eq_form.log" \
  --selftest-colon "$RR/controls/control_colon_form.log" \
  --selftest-workdir "$RR/controls" \
  --controls-out "$RR/controls/CHECKMESH_CONTROLS.json" > "$RR/controls/checkmesh_controls.txt" 2>&1
CTL_RC=$?
[ $CTL_RC -eq 0 ] || fail "A PLANTED CONTROL ON THE checkMesh READER FAILED (rc=$CTL_RC). A control that fails is a finding and stops the measurement; it is not repaired by loosening the reading (§9)." 4
say "checkMesh reader controls: ALL PASS"

# -------------------------------------------------------------------------------------
# 3.  INPUT copied OUT of the read-only tree.  $CR is read from, never written to.
# -------------------------------------------------------------------------------------
SURF="$CR/A3-onera-m6-adjoint-coarse/surfaceMesh.cgns"
cp "$SURF" "$RR/work/surfaceMesh.cgns" || fail "surface input copy failed: $SURF" 3
sha256sum "$RR/work/surfaceMesh.cgns" > "$RR/work/surfaceMesh.cgns.sha256"
say "surface input copied (1,560-face coarsening); $CR untouched"

# -------------------------------------------------------------------------------------
# 4.  DOCKER PREFLIGHT -- both limbs recorded, because the bare failure would be silent.
# -------------------------------------------------------------------------------------
BARE_OUT=$(docker version --format '{{.Server.Version}}' 2>&1); BARE_RC=$?
SG_OUT=$(sg docker -c "docker version --format '{{.Server.Version}}'" 2>&1); SG_RC=$?
{ echo "bare_rc=$BARE_RC"; echo "bare_out=$BARE_OUT"; echo "sg_rc=$SG_RC"; echo "sg_out=$SG_OUT";
  echo "groups=$(id -G)"; echo "sg_groups=$(sg docker -c 'id -G' 2>&1)"; } > "$RR/DOCKER_PREFLIGHT.txt"
say "docker preflight: bare rc=$BARE_RC  sg rc=$SG_RC"
[ $SG_RC -eq 0 ] || fail "docker unreachable even through 'sg docker -c'. This grades THE PROBE'S ABILITY TO RUN and says nothing about the M6 or about 70 degrees." 5

# -------------------------------------------------------------------------------------
# 5.  THE pyHyp DECK.  Byte-identical to the M6S-P probe deck already run on this box
#     (verification/runs/M6S_runs/P_pyhyp_wall_resolved_probe/work/genWingMesh_M6S.py),
#     which is itself the stock dafoam-tutorials genWingMesh.py with three parameters
#     moved and no others: N 65 -> 93, s0 1.0e-4 -> 1.319e-06, and the 1,560-face
#     coarsened surface.  Smoothing parameters DELIBERATELY at stock.
#     This is the level §6 registers as branch (a2)'s COARSE: 143,520 cells.
# -------------------------------------------------------------------------------------
cat > "$RR/work/genWingMesh_R1M0.py" <<'PYG'
from pyhyp import pyHyp

fileName = "surfaceMesh.cgns"

options = {
    "inputFile": fileName,
    "fileType": "CGNS",
    "unattachedEdgesAreSymmetry": True,
    "outerFaceBC": "farfield",
    "autoConnect": True,
    "BC": {},
    "families": "wall",
    "N": 93,
    "s0": 1.319e-06,
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
# the container runs as dafoamuser (uid 1002); the mounted work dir is made writable to it
chmod 777 "$RR/work"

# -------------------------------------------------------------------------------------
# 6.  pyHyp.  rc captured IN THIS SHELL, IMMEDIATELY.  The driver already runs inside the
#     queue wrapper's detached shell, and `setsid timeout cmd` returns 0 for EVERY
#     outcome -- so the rc is taken inside, never around a setsid line.
# -------------------------------------------------------------------------------------
R=$(rem); [ "$R" -gt 0 ] || fail "structural cap ${CAP_S}s exhausted before pyHyp. AN OVERRUN STOPS THE RUN." 7
say "launching pyHyp under timeout ${R}s (remaining structural budget of ${CAP_S}s)"
P0=$(date +%s)
timeout ${R}s sg docker -c "docker run --rm --name $CNAME -u 1002:1002 \
  -v '$RR/work':/home/dafoamuser/mount -w /home/dafoamuser/mount $IMG \
  bash -c 'set +u; source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; python genWingMesh_R1M0.py'" \
  > "$RR/logMeshGeneration.txt" 2>&1
PYHYP_RC=$?
P1=$(date +%s); PYHYP_WALL=$((P1-P0))
sg docker -c "docker rm -f $CNAME" >/dev/null 2>&1
say "pyHyp rc=$PYHYP_RC wall=${PYHYP_WALL}s"
[ $PYHYP_RC -eq 124 ] && fail "pyHyp TIMED OUT at the structural cap. AN OVERRUN STOPS THE RUN; it does not get a new budget (rule 12)." 7
[ $PYHYP_RC -eq 0 ] || fail "pyHyp rc=$PYHYP_RC -- no grid generated, so NO non-orthogonality number exists and none may be attributed to this probe." 7
[ -s "$RR/work/volumeMesh.xyz" ] || fail "pyHyp returned 0 but wrote no grid. rc=0 IS NOT A RESULT WITHOUT THE ARTIFACT." 7

# -------------------------------------------------------------------------------------
# 7.  THE GRID READING, with its own planted controls (mutation read back off disk).
#     Gives an INDEPENDENT cell count -- checked against checkMesh's own in §9 below.
# -------------------------------------------------------------------------------------
python3 "$CASE/read_grid.py" --grid "$RR/work/volumeMesh.xyz" --requested-s0 "$S0" \
  --json-out "$RR/GRID_READBACK.json" --selftest-workdir "$RR/controls" \
  --controls-out "$RR/controls/GRID_CONTROLS.json" > "$RR/grid_readback.txt" 2>&1
GRID_RC=$?
[ $GRID_RC -eq 0 ] || fail "grid reader rc=$GRID_RC (4 = a planted control failed; 2 = grid absent). It refuses rather than degrades." 4
say "grid readback done; planted controls PASS"

# -------------------------------------------------------------------------------------
# 8.  CONVERSION.  THE CHEAPEST CONVERTER, AND NO FIDELITY CLAIM ATTACHES (§5).
#     plot3dToFoam ALONE: no autoPatch, no createPatch, no renumberMesh.  Patch identity
#     is irrelevant to a cell-geometry check.  Boundary NAMING is therefore meaningless
#     in this run and no downstream reader may use it.
# -------------------------------------------------------------------------------------
cat > "$RR/foam/system/controlDict" <<'FCD'
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application     checkMesh;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1;
deltaT          1;
writeControl    timeStep;
writeInterval   1;
purgeWrite      0;
writeFormat     ascii;
writePrecision  10;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;
FCD
# ATTEMPT 1 (2026-09-03 16:46Z) DIED HERE AND THE DEFECT WAS THIS DRIVER'S, NOT THE MESH'S.
# checkMesh in OpenFOAM v2606 constructs an fvMesh and therefore requires system/fvSchemes;
# attempt 1 wrote only controlDict and checkMesh exited 1 with
#   "FOAM FATAL ERROR: cannot find file .../system/fvSchemes"
# having produced NO geometry block, so NO non-orthogonality number existed and none was
# read.  The mesh itself was fine -- plot3dToFoam rc=0, points merged 169,911 -> 148,335.
# The three-dictionary set below was validated BEFORE attempt 2 was launched, on an
# UNRELATED 56-cell mesh (verification/runs/F16_runs/coarse), so that the fix was proven
# without reading any M6 answer outside the registered run.
# These two dictionaries are inert for a mesh check: no solver runs, nothing is discretised,
# and `divSchemes default none` guarantees no scheme choice here can influence a number.
cat > "$RR/foam/system/fvSchemes" <<'FVS'
FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
ddtSchemes          { default steadyState; }
gradSchemes         { default Gauss linear; }
divSchemes          { default none; }
laplacianSchemes    { default Gauss linear corrected; }
interpolationSchemes{ default linear; }
snGradSchemes       { default corrected; }
FVS
cat > "$RR/foam/system/fvSolution" <<'FVL'
FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers {}
FVL
# PREFLIGHT ASSERT: the class of failure that killed attempt 1 is now caught by the driver
# at zero compute instead of by the reader after the mesh has been paid for.
for d in controlDict fvSchemes fvSolution; do
  [ -s "$RR/foam/system/$d" ] || fail "system/$d missing or empty -- checkMesh would abort. This is the attempt-1 defect and it is refused before compute." 8
done

# rule 4's guard, applied to the converter's target: refuse a pre-existing `0` or time dir
for d in "$RR/foam"/[0-9]*; do
  [ -e "$d" ] && fail "a time directory already exists under the foam case: $d" 3
done

set +u; source "$FOAM_BASHRC" >/dev/null 2>&1
[ -n "$WM_PROJECT" ] || fail "OpenFOAM environment did not load from $FOAM_BASHRC" 8
say "OpenFOAM $WM_PROJECT_VERSION loaded"

R=$(rem); [ "$R" -gt 0 ] || fail "structural cap exhausted before plot3dToFoam. AN OVERRUN STOPS THE RUN." 7
C0=$(date +%s)
timeout ${R}s plot3dToFoam -noBlank -case "$RR/foam" "$RR/work/volumeMesh.xyz" \
  > "$RR/foam/log.plot3dToFoam" 2>&1
CONV_RC=$?
C1=$(date +%s); CONV_WALL=$((C1-C0))
say "plot3dToFoam rc=$CONV_RC wall=${CONV_WALL}s"
[ $CONV_RC -eq 124 ] && fail "plot3dToFoam TIMED OUT at the structural cap. AN OVERRUN STOPS THE RUN." 7
[ $CONV_RC -eq 0 ] || fail "plot3dToFoam rc=$CONV_RC -- no polyMesh, so no checkMesh number exists." 8
[ -s "$RR/foam/constant/polyMesh/points" ] || fail "plot3dToFoam returned 0 but wrote no polyMesh points." 8

# -------------------------------------------------------------------------------------
# 9.  checkMesh.  THE MEASUREMENT.
# -------------------------------------------------------------------------------------
R=$(rem); [ "$R" -gt 0 ] || fail "structural cap exhausted before checkMesh. AN OVERRUN STOPS THE RUN." 7
K0=$(date +%s)
timeout ${R}s checkMesh -case "$RR/foam" > "$RR/foam/log.checkMesh" 2>&1
CM_RC=$?
K1=$(date +%s); CM_WALL=$((K1-K0))
say "checkMesh rc=$CM_RC wall=${CM_WALL}s"
[ $CM_RC -eq 124 ] && fail "checkMesh TIMED OUT at the structural cap. AN OVERRUN STOPS THE RUN." 7
# NOTE: checkMesh's OWN EXIT CODE IS NOT THE MEASUREMENT AND IS NOT A GATE.  It is
# recorded and carried; the NUMBER is parsed from the log by the reader below.
# But a FOAM FATAL ERROR means checkMesh never reached the geometry block, so there is no
# number at all.  Named here so the failure reports itself instead of arriving as a bare
# reader refusal, which is how attempt 1 presented.
if grep -q "FOAM FATAL ERROR" "$RR/foam/log.checkMesh"; then
  say "checkMesh aborted with a FOAM FATAL ERROR -- NO geometry block, so NO non-orthogonality number exists and NONE may be attributed to this probe."
  grep -A3 "FOAM FATAL ERROR" "$RR/foam/log.checkMesh" | head -6
fi

python3 "$CASE/read_checkmesh.py" --log "$RR/foam/log.checkMesh" \
  --json-out "$RR/CHECKMESH_READING.json" > "$RR/checkmesh_reading.txt" 2>&1
READ_RC=$?
say "checkMesh reader rc=$READ_RC (0 = COMPLETE, 2 = ABSENT/INCOMPLETE -- refuses rather than degrades)"

# -------------------------------------------------------------------------------------
# 10. THE RESULT RECORD, its asserts, and the cost.
# -------------------------------------------------------------------------------------
T1=$(date +%s); WALL=$((T1-T0))
python3 - "$RR" "$PYHYP_RC" "$PYHYP_WALL" "$CONV_RC" "$CONV_WALL" "$CM_RC" "$CM_WALL" \
             "$READ_RC" "$WALL" "$RANKS" "$CAP_S" "$S0" "$CREATED" <<'PYS'
import json, math, os, sys
(rr, prc, pwall, crc, cwall, kmrc, kmwall, rrc, wall, ranks, cap_s, s0, created) = (
    sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]),
    int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8]), int(sys.argv[9]),
    int(sys.argv[10]), int(sys.argv[11]), float(sys.argv[12]), int(sys.argv[13]))

def load(p):
    try:
        return json.load(open(os.path.join(rr, p)))
    except Exception:
        return {}

cm = load("CHECKMESH_READING.json")
gr = load("GRID_READBACK.json")
cmc = load("controls/CHECKMESH_CONTROLS.json")
grc = load("controls/GRID_CONTROLS.json")

log = os.path.join(rr, "foam", "log.checkMesh")
grid = os.path.join(rr, "work", "volumeMesh.xyz")

# --- THE AGE GUARD, in the form this probe can carry.  R1-M0 runs no solver, so there is
# --- no 0/U to date the run against; the analogue is the run root's own creation stamp,
# --- written before anything else and read back here.  EVERY artifact the readings come
# --- off must be NEWER than it.  (M6S-P used the same construction.)
ages = {}
for name, p in (("log.checkMesh", log), ("volumeMesh.xyz", grid),
                ("logMeshGeneration.txt", os.path.join(rr, "logMeshGeneration.txt"))):
    ages[name] = (os.path.getmtime(p) > created) if os.path.exists(p) else False

cm_cells = cm.get("cells")
gr_cells = gr.get("cells_DERIVED_sum_(i-1)(j-1)(k-1)")

clauses = {
    "pyhyp_rc_zero": prc == 0,
    "plot3dToFoam_rc_zero": crc == 0,
    "checkmesh_log_present_and_COMPLETE": cm.get("state") == "COMPLETE",
    "checkmesh_reader_rc_zero": rrc == 0,
    "grid_exists_nonempty": os.path.exists(grid) and os.path.getsize(grid) > 0,
    "every_artifact_newer_than_run_root_creation": all(ages.values()),
    # ONE CONNECTED REGION.  If plot3dToFoam had failed to merge the nine PLOT3D blocks,
    # the block interfaces would be BOUNDARY faces and would drop out of the
    # non-orthogonality statistic entirely, making the number FALSELY OPTIMISTIC.
    "single_connected_region": cm.get("n_regions") == 1,
    # TWO INDEPENDENT INSTRUMENTS AGREE ON THE CELL COUNT: the PLOT3D block header
    # arithmetic and checkMesh's own census.
    "cell_count_agrees_between_grid_and_checkMesh": (
        cm_cells is not None and gr_cells is not None and cm_cells == gr_cells),
    "all_planted_controls_pass": bool(cmc.get("all_controls_pass")) and bool(grc.get("all_controls_pass")),
}

core_min = round(wall * ranks / 60.0, 4)
EST = 2.0
CAP = 6.0
RATE = 0.0513  # $/core-h, owner-stated; DERIVED not measured (COMPUTE_BUDGET_CHARTER §5)

# --- y+ INTENT.  A PRIORI, DERIVED FROM A FLAT-PLATE CORRELATION, AND NOT A MEASUREMENT.
# --- No solver has run, so no measured y+ exists and none is claimed.  §3 conditions.
T, P, MACH, RE, C = 288.15, 101325.0, 0.8395, 11.72e6, 0.64607
GAM, RGAS = 1.4, 287.058
a = math.sqrt(GAM * RGAS * T)
U = MACH * a
rho = P / (RGAS * T)
mu = rho * U * C / RE               # back-solved to DELIVER Re; not a property of air
cf = 0.026 / RE ** (1.0 / 7.0)      # flat-plate turbulent skin friction correlation
tau = cf * 0.5 * rho * U * U
utau = math.sqrt(tau / rho)
def yplus(h):
    return h * rho * utau / mu
h = gr.get("first_cell_height_m", {})

out = {
    "case": "R1-M0 -- ONERA M6 admission probe",
    "prereg": "verification/campaign/RUNG1_M6_PREREGISTRATION.md §5, commit c7f99bb1",
    "attempt": 2,
    "attempt_1_disclosure": (
        "ATTEMPT 1 (2026-09-03 16:46:31-16:47:26Z, 0.9167 core-min) IS PRESERVED IN FULL "
        "at verification/runs/RUNG1_M6_runs/M0_ATTEMPT1_ABORTED_missing_fvSchemes/. It "
        "produced a valid mesh (pyHyp rc 0, plot3dToFoam rc 0, 143,520 cells) but "
        "checkMesh aborted with `cannot find file system/fvSchemes` -- a DRIVER defect, "
        "not a mesh finding -- so it produced NO non-orthogonality number and none was "
        "read. Its 0.9167 core-min is NAMED AS WASTE in the calibration rows and is NOT "
        "absorbed into this attempt's actual/predicted ratio (COMPUTE_BUDGET_CHARTER §6). "
        "Attempt 2 regenerates from pyHyp rather than reusing attempt 1's grid, so that "
        "every artifact graded here is dated by this run's own age guard."),
    "LABEL": ("NO VERDICT OF THE FIXED VOCABULARY ATTACHES TO R1-M0. It is an "
              "admissibility measurement that gates a freeze (prereg §5). IT GRADES "
              "NOTHING. No PASS / GATE FAIL / NOT A RESULT is claimed or implied."),
    "NO_FIDELITY_CLAIM": ("The cheapest converter was used -- plot3dToFoam ALONE, no "
                          "autoPatch, no createPatch, no renumberMesh. Patch identity is "
                          "irrelevant to a cell-geometry check and boundary NAMING in "
                          "this case is meaningless. No fidelity claim attaches (§5)."),
    "rc": {"pyhyp": prc, "plot3dToFoam": crc, "checkMesh_exit_NOT_A_GATE": kmrc,
           "checkmesh_reader": rrc},
    "completion_clauses": clauses,
    "probe_complete": all(clauses.values()),
    "artifact_ages_vs_run_root_creation": ages,
    "run_root_created_epoch": created,

    # ---------------- THE MEASUREMENT ----------------
    "measurement": {
        "max_non_orthogonality_deg": cm.get("max_non_orthogonality_deg"),
        "avg_non_orthogonality_deg": cm.get("avg_non_orthogonality_deg"),
        "max_skewness": cm.get("max_skewness"),
        "severe_non_orth_faces_gt_70deg": cm.get("severe_non_orth_faces"),
        "max_aspect_ratio": cm.get("max_aspect_ratio"),
        "max_aspect_ratio_label_form": cm.get("max_aspect_ratio_label_form"),
        "aspect_ratio_flagged": cm.get("aspect_ratio_flagged"),
        "min_cell_volume": cm.get("min_cell_volume"),
        "max_cell_volume": cm.get("max_cell_volume"),
        "cell_volume_ratio_DERIVED": cm.get("cell_volume_ratio_DERIVED"),
        "geometric_directions": cm.get("geometric_directions"),
        "cells": cm_cells,
        "cells_INDEPENDENT_from_plot3d_header": gr_cells,
        "points": cm.get("points"),
        "faces": cm.get("faces"),
        "internal_faces": cm.get("internal_faces"),
        "boundary_faces_DERIVED": cm.get("boundary_faces_DERIVED"),
        "n_regions": cm.get("n_regions"),
        "HOW_READ": ("PARSED NUMERICALLY off `Mesh non-orthogonality Max:`. checkMesh's "
                     "own verdict line was CAPTURED AND DISCARDED -- measured on this "
                     "box, all 885 production checkMesh logs print `Non-orthogonality "
                     "check OK.`, including one at 84.6437 deg and committee grids at "
                     "89.71 / 89.94 / 90.00 / 89.98 deg."),
        "verdict_line_the_log_printed_IGNORED":
            cm.get("verdict_line_IGNORED_NEVER_A_GATE"),
    },

    # ---------------- WHICH REGISTERED OUTCOME (§5) ----------------
    "registered_outcome": (
        None if cm.get("max_non_orthogonality_deg") is None else (
            ("<=70: Gate A is satisfiable, MESH_STANDARD §8.1's build-before-freeze is "
             "discharged, and the RUNG1-M6 registration becomes FREEZABLE.")
            if cm["max_non_orthogonality_deg"] <= 70.0 else
            ("> 70: branches (a1)/(a2) are DEAD, snappy (§6 branch (b)) becomes the "
             "route, and §2.3's boundary question moves onto the critical path and goes "
             "to Sanaa. This is a real measurement that saves the ladder from a dead "
             "branch, NOT a failure."))),
    "skewness_vs_registered_4": cm.get("skewness_vs_4"),

    # ---------------- WALL RESOLUTION ----------------
    "wall_resolution": {
        "requested_s0_INPUT_NEVER_A_MEASUREMENT": s0,
        "achieved_first_cell_height_m_READ_BACK_FROM_THE_WRITTEN_GRID": h,
        "yplus_A_PRIORI_DERIVED_NOT_MEASURED": {
            "note": ("Flat-plate turbulent correlation Cf = 0.026 Re^(-1/7) at the §3 "
                     "conditions. NO SOLVER HAS RUN, so no measured y+ exists and none "
                     "is claimed. §3 registers the intent as y+ 0.25-1.0."),
            "U_inf_m_s": round(U, 4), "rho_inf": round(rho, 6),
            "mu_back_solved_to_deliver_Re": mu, "u_tau_m_s": round(utau, 5),
            "yplus_at_median_h": (round(yplus(h["median"]), 4) if h else None),
            "yplus_at_min_h": (round(yplus(h["min"]), 4) if h else None),
            "yplus_at_max_h": (round(yplus(h["max"]), 4) if h else None),
            "registered_intent": "0.25 - 1.0",
        },
    },

    # ---------------- COST, rule 12 ----------------
    "cost": {
        "unit": "core-minutes",
        "ranks": ranks,
        "driver_wall_s": wall,
        "per_step_wall_s": {"pyhyp": pwall, "plot3dToFoam": cwall, "checkMesh": kmwall},
        "actual_core_min": core_min,
        "estimate_core_min": EST,
        "cap_core_min": CAP,
        "structural_cap_timeout_s": cap_s,
        "ratio_actual_over_predicted": round(core_min / EST, 3),
        "fraction_of_cap": round(core_min / CAP, 4),
        "cap_approached": core_min > 0.5 * CAP,
        "stall_over_3600_wall_s": wall > 3600,
        "cost_basis": ("dollars DERIVED at the owner-stated c7a.4xlarge rate "
                       "$0.0513/core-h, reported-by-owner and NEVER measured -- the box "
                       "cannot read its own billing (COMPUTE_BUDGET_CHARTER.md §5). "
                       "GROSS: contention on the shared box is not separated out."),
        "derived_usd": round(core_min / 60.0 * RATE, 6),
    },
    "planted_controls": {
        "checkmesh_reader_all_pass": cmc.get("all_controls_pass"),
        "grid_reader_all_pass": grc.get("all_controls_pass"),
        "checkmesh_controls": cmc.get("controls"),
        "grid_controls": grc.get("controls"),
    },
}
json.dump(out, open(os.path.join(rr, "RESULT.json"), "w"), indent=2)
print(json.dumps({k: out[k] for k in
                  ("measurement", "registered_outcome", "completion_clauses",
                   "probe_complete", "cost")}, indent=2))
PYS

say "driver done: wall ${WALL}s at ${RANKS} rank = $(python3 -c "print(round($WALL/60.0,4))") core-min against the 6.0 cap"
exit $READ_RC
