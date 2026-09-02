#!/bin/bash
# M6S-P -- pyHyp wall-resolved feasibility probe, ONERA M6.  DRIVER.
#
# This file is a COPY under the probe's own run root (prereg §8).  It writes NOTHING under
# /home/ubuntu/dafoam-tutorials/ or /home/ubuntu/certonomous-runs/; both are read from and
# copied out of, never written to.
#
# Frozen registration:
#   verification/campaign/M6S_P_PYHYP_WALL_RESOLVED_PROBE_PREREGISTRATION.md
#   blob 8fad9c6019174c235c79ac9948796c9c60b381b8, amendment 1 at commit 87a6364f.
#
# LABEL, carried here so no reader of this script can mistake it (prereg header and §1.1):
#   FEASIBILITY PROBE.  NO GATE, NO THRESHOLD, NO VERDICT of the fixed vocabulary attaches
#   to any number it produces.  It can KILL option 3; it CANNOT clear it.  It runs no
#   plot3dToFoam, no checkMesh and no solver, so it produces NO non-orthogonality number
#   and none may be attributed to it.
#
# DOCKER CREDENTIALS -- why every docker call is wrapped in `sg docker -c`:
#   supplementary group membership is fixed at process start.  The shared queue daemon
#   (pid 1645, started 15:20:07Z) predates the docker-group grant, so its Groups line is
#   `4 24 27 30 105 1000` -- no 113 -- and every process it launches inherits that set.
#   `sg docker -c` acquires gid 113 AT EXEC, inside our own driver, disturbing nothing
#   else.  The daemon is NOT restarted (shared infrastructure, other teams' rows) and sudo
#   is NOT used (Sanaa's grant was a group membership, not root).
set +u

RR=/home/ubuntu/Certonomous/verification/runs/M6S_runs/P_pyhyp_wall_resolved_probe
CR=/home/ubuntu/certonomous-runs
IMG=dafoam-idwarp-rot:v1
CNAME=m6s_p_pyhyp_probe
TIMEOUT_S=900            # STRUCTURAL cap: 1 rank x 900 s / 60 = 15.0 core-min (§9.2)
RANKS=1
T0=$(date +%s)
say(){ echo "[$(date -u +%H:%M:%SZ)] $*"; }
fail(){ say "STOP: $1"; echo "$1" > "$RR/STOPPED.txt"; exit "$2"; }

say "M6S-P pyHyp wall-resolved feasibility probe -- driver start"
say "run root: $RR"
say "launched credential set: uid=$(id -u) gid=$(id -g) groups=$(id -G)"
mkdir -p "$RR/work" "$RR/controls" || exit 3

# --------------------------------------------------------------------------------------
# 0.  Inputs copied OUT of the read-only tree (§8, §10).  Nothing under $CR is written.
# --------------------------------------------------------------------------------------
cp "$CR/A3-onera-m6-adjoint-coarse/surfaceMesh.cgns"       "$RR/work/surfaceMesh.cgns"       || fail "surface input copy failed" 3
cp "$CR/A3-onera-m6-adjoint-vcoarse/logMeshGeneration.txt" "$RR/controls/controlA_vcoarse.txt" || fail "control A copy failed" 3
cp "$CR/A3-onera-m6-sweep-n8_10920/logMeshGeneration.txt"  "$RR/controls/controlB_n8.txt"      || fail "control B copy failed" 3
say "inputs copied out; $CR untouched"

# --------------------------------------------------------------------------------------
# 1.  §5 PLANTED CONTROLS -- rule 3.  ALL must pass BEFORE the probe's readings count.
#     Control C is built by truncating a COPY of control A inside this run root.
# --------------------------------------------------------------------------------------
python3 - "$RR/controls/controlA_vcoarse.txt" "$RR/controls/controlC_truncated.txt" <<'PYC'
import sys, re
NUM = re.compile(r"^[-+]?[0-9]*\.?[0-9]+([EeDd][-+]?[0-9]+)?$")
src, dst = sys.argv[1], sys.argv[2]
keep, seen = [], 0
for l in open(src, errors="replace").read().split("\n"):
    s = l.strip(); f = s.split()
    if s and not s.startswith("#") and len(f) == 14 and all(NUM.match(x) for x in f):
        seen += 1
        if seen > 30:
            continue           # trailing table rows REMOVED -- §5 Control C
    keep.append(l)
open(dst, "w").write("\n".join(keep))
print("control C built: 30 of 64 data rows retained")
PYC
[ $? -eq 0 ] || fail "control C construction failed" 4

say "running the three registered controls (§5)"
python3 "$RR/run_controls.py" "$RR/controls/controlA_vcoarse.txt" "$RR/controls/controlB_n8.txt" \
        "$RR/controls/controlC_truncated.txt" "$RR/controls/CONTROLS.json"
CTL_RC=$?
[ $CTL_RC -eq 0 ] || fail "A PLANTED CONTROL FAILED (rc=$CTL_RC). A control that fails is a finding and stops the probe; it is not repaired by loosening the reading (§5)." 4
say "controls: ALL PASS"

# --------------------------------------------------------------------------------------
# 2.  DOCKER PREFLIGHT -- both limbs recorded, because the bare failure would be silent.
# --------------------------------------------------------------------------------------
BARE_OUT=$(docker version --format '{{.Server.Version}}' 2>&1); BARE_RC=$?
SG_OUT=$(sg docker -c "docker version --format '{{.Server.Version}}'" 2>&1); SG_RC=$?
say "docker preflight: bare rc=$BARE_RC out='$(echo "$BARE_OUT" | tr '\n' ' ' | cut -c1-90)'"
say "docker preflight: sg   rc=$SG_RC out='$(echo "$SG_OUT" | tr '\n' ' ' | cut -c1-90)'"
{ echo "bare_rc=$BARE_RC"; echo "bare_out=$BARE_OUT"; echo "sg_rc=$SG_RC"; echo "sg_out=$SG_OUT";
  echo "groups=$(id -G)"; echo "sg_groups=$(sg docker -c 'id -G' 2>&1)"; } > "$RR/DOCKER_PREFLIGHT.txt"
[ $SG_RC -eq 0 ] || fail "docker unreachable even through 'sg docker -c' -- prereg §6 BLOCKED; this grades the PROBE'S ABILITY TO RUN and nothing about the M6 or option 3." 5
[ $BARE_RC -eq 0 ] && say "NOTE: the BARE docker call also succeeded -- the launched credential set already carries gid 113, contrary to the daemon reading; reported, not hidden."

# --------------------------------------------------------------------------------------
# 3.  The pyHyp input deck.  EVERY option byte-identical to genWingMesh.py as it stands,
#     except the three §2 registers: N 65 -> 93, s0 1.0e-4 -> 1.319e-06, and the input
#     surface is the 1,560-face coarsening.  Smoothing parameters DELIBERATELY at stock.
# --------------------------------------------------------------------------------------
cat > "$RR/work/genWingMesh_M6S.py" <<'PYG'
"""M6S-P probe deck.  Derived from /home/ubuntu/dafoam-tutorials/Onera_M6_Wing/genWingMesh.py
(read-only parameter source, prereg §10).  Three parameters move and no others:
  N        65      -> 93     (pyHyp node count; 92 cell layers against the stock 64)
  s0       1.0e-4  -> 1.319e-06   (REQUESTED; registered as an INPUT, never a measurement)
  surface  6,240-face fine -> the 1,560-face coarsening
"""
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

# the container runs as dafoamuser (uid 1002; the dafoam tree is unreadable to uid 1000),
# so the mounted work directory -- owned by ubuntu -- is made writable to it.
chmod 777 "$RR/work"

# --------------------------------------------------------------------------------------
# 4.  THE PROBE.  pyHyp ALONE.  No plot3dToFoam, no checkMesh, no solver (§3).
#     rc captured in THIS shell, immediately -- the driver already runs inside the queue
#     wrapper's detached shell, and `setsid timeout cmd` returns 0 for every outcome.
# --------------------------------------------------------------------------------------
say "launching pyHyp under timeout ${TIMEOUT_S}s (structural 15.0 core-min cap)"
P0=$(date +%s)
timeout ${TIMEOUT_S}s sg docker -c "docker run --rm --name $CNAME -u 1002:1002 \
  -v '$RR/work':/home/dafoamuser/mount -w /home/dafoamuser/mount $IMG \
  bash -c 'set +u; source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; python genWingMesh_M6S.py'" \
  > "$RR/logMeshGeneration.txt" 2>&1
PYHYP_RC=$?
P1=$(date +%s); PYHYP_WALL=$((P1-P0))
sg docker -c "docker rm -f $CNAME" >/dev/null 2>&1
say "pyHyp rc=$PYHYP_RC wall=${PYHYP_WALL}s"
if [ $PYHYP_RC -eq 124 ]; then
  say "TIMEOUT at ${TIMEOUT_S}s. AN OVERRUN STOPS THE RUN. It does not get a new budget (§9.2)."
fi

# --------------------------------------------------------------------------------------
# 5.  READINGS -- the amended completion clause, and the POSITIONAL column-9 instrument.
# --------------------------------------------------------------------------------------
python3 "$RR/read_pyhyp_log.py" --log "$RR/logMeshGeneration.txt" --expect-levels 93 \
        --json-out "$RR/READINGS.json" > "$RR/READINGS.txt" 2>&1
READ_RC=$?
say "reader rc=$READ_RC (0 = table COMPLETE at 92 rows, 2 = ABSENT or INCOMPLETE; refuses rather than degrades)"

T1=$(date +%s); WALL=$((T1-T0))
python3 - "$RR" "$PYHYP_RC" "$PYHYP_WALL" "$READ_RC" "$WALL" "$RANKS" "$TIMEOUT_S" <<'PYS'
import json, os, sys
rr, prc, pwall, rrc, wall, ranks, tmo = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])
grid = os.path.join(rr, "work", "volumeMesh.xyz")
try:
    rd = json.load(open(os.path.join(rr, "READINGS.json")))
except Exception:
    rd = {"state": "ABSENT"}
created = 0
try:
    created = int(open(os.path.join(rr, "RUN_ROOT_CREATED_EPOCH")).read().strip())
except Exception:
    pass
log = os.path.join(rr, "logMeshGeneration.txt")
log_mtime = os.path.getmtime(log) if os.path.exists(log) else 0
clauses = {
    "rc_zero": prc == 0,
    "grid_exists_nonempty": os.path.exists(grid) and os.path.getsize(grid) > 0,
    "header_Grid_Ratio_line": rd.get("header_grid_ratio_raw") is not None,
    "stacked_Min_Min__Quality_Volume_pair": rd.get("stacked_header_pairs", 0) >= 1,
    "ninety_two_rows_levels_2_to_93": rd.get("n_data_rows") == 92 and rd.get("levels_contiguous_2_to_N") is True,
    "artifacts_newer_than_run_root_creation": log_mtime > created > 0,
}
core_min = round(wall * ranks / 60.0, 3)
out = {
    "probe": "M6S-P pyHyp wall-resolved feasibility probe",
    "prereg_blob": "8fad9c6019174c235c79ac9948796c9c60b381b8",
    "prereg_amended_commit": "87a6364f",
    "LABEL": ("FEASIBILITY PROBE -- NO GATE, NO THRESHOLD, NO VERDICT of the fixed vocabulary "
              "attaches to any number here. It can KILL option 3; it CANNOT clear it (prereg 1.1). "
              "No checkMesh number exists and none may be attributed to this probe."),
    "pyhyp_rc": prc,
    "pyhyp_wall_s": pwall,
    "reader_rc": rrc,
    "completion_clauses_4_1": clauses,
    "probe_ran_at_all": all(clauses.values()),
    "grid_path": grid,
    "grid_bytes": os.path.getsize(grid) if os.path.exists(grid) else 0,
    "readings": {
        "reading_1_min_quality_minimum_raw": rd.get("min_quality_min_raw"),
        "reading_1_min_quality_minimum_level": rd.get("min_quality_min_level"),
        "reading_1_min_quality_all_positive": rd.get("min_quality_all_positive"),
        "reading_1_n_negative_levels": rd.get("min_quality_n_negative_levels"),
        "reading_1_first_negative_raw": rd.get("min_quality_first_negative_raw"),
        "reading_1_first_negative_level": rd.get("min_quality_first_negative_level"),
        "reading_1b_min_volume_minimum_raw": rd.get("min_volume_min_raw"),
        "reading_1b_min_volume_negative_anywhere": rd.get("min_volume_negative_anywhere"),
        "reading_2a_header_grid_ratio_raw": rd.get("header_grid_ratio_raw"),
        "reading_2b_last_level_march_distance_raw": rd.get("last_level_march_distance_raw"),
        "reading_2b_march_closed_on_12.0": rd.get("march_closed"),
        "reading_2b_fraction_of_requested_marchDist": rd.get("march_fraction_of_target"),
        "reading_3_achieved_first_cell_height_raw": rd.get("level2_march_distance_raw"),
        "reading_3_requested_s0_INPUT_NOT_A_MEASUREMENT": 1.319e-06,
        "reading_4_pyhyp_last_level_cpu_s": rd.get("last_level_cpu_s"),
        "table_state": rd.get("state"),
        "n_data_rows": rd.get("n_data_rows"),
    },
    "cost": {
        "unit": "core-minutes",
        "ranks": ranks,
        "driver_wall_s": wall,
        "actual_core_min": core_min,
        "estimate_core_min": 0.11,
        "cap_core_min": 15.0,
        "structural_cap_timeout_s": tmo,
        "ratio_actual_over_predicted": round(core_min / 0.11, 2) if core_min else 0.0,
        "cost_basis": ("dollars DERIVED at the owner-stated c7a.4xlarge rate $0.0513/core-h, "
                       "reported-by-owner and NEVER measured -- the box cannot read its own "
                       "billing (COMPUTE_BUDGET_CHARTER.md 5)"),
        "derived_usd": round(core_min / 60.0 * 0.0513, 6),
    },
}
json.dump(out, open(os.path.join(rr, "RESULT.json"), "w"), indent=2)
print(json.dumps(out, indent=2))
PYS

say "driver done: total wall ${WALL}s = $(python3 -c "print(round($WALL/60.0,3))") core-min against the 15.0 cap"
exit $PYHYP_RC
