#!/usr/bin/env bash
# =====================================================================
# D8G L1-P R3 -- QUEUE LAUNCH WRAPPER.  **PREPARED, NEVER RUN BY THIS LANE.**
#
# SCOPE, and it is narrow on purpose (dafoam-supervisor, Sanaa's 2026-09-12
# priority shift): THE ADJOINT PRIMAL ONLY.  The CRM CL/CD/CM comparison against
# NTF/Ames with the DPW scatter is CFD'S REGISTERED RUN NOW, not this team's.
# This L1 exists to feed the adjoint.  NO DPW BAND, NO TUNNEL REFERENCE, AND THE
# BLOCKED COMPARISON VERDICT IS NOT REOPENED.
#
# scripts/queue_runner.py launches an ARGV and passes no environment; the arm
# launcher needs BASE.  This supplies a FRESH TIMESTAMPED BASE and nothing else.
# It adds no parameter, no resource flag, no cap and no timeout.
#
# ITEM 19: the runner is the only thing that launches.  Running this by hand does
# not make a case.
# =====================================================================
set -u
CASE_DIR=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A6/curriculum_D8G
ARM_SH="$CASE_DIR/d8g_run_arm.sh"
IMG="dafoam-idwarp-rot:v1"

# --- the launcher is PINNED to its ADDENDUM 11 re-freeze.  A wrapper that runs
#     whatever is at the path is not a wrapper, it is a hole.
PIN="c0fdb80ab60327f32531323b74097107"
GOT=$(md5sum "$ARM_SH" | awk '{print $1}')
[ "$GOT" = "$PIN" ] || { echo "REFUSE [PIN] d8g_run_arm.sh md5 $GOT != ADDENDUM 11 pin $PIN."; exit 90; }

# --- Sanaa item 6 and the evidence guard, asserted on EXECUTABLE LINES ONLY.
#     A whole-file grep for a defect's name fires on the COMMENT recording that
#     defect being fixed -- measured twice on this box tonight, on MP_A5R.
grep -qE '^[^#]*--user 0:0' "$ARM_SH" && { echo "REFUSE [ROOT] launcher still EXECUTES --user 0:0 (Sanaa item 6)."; exit 91; }
grep -qE '^[^#]*-u 1000:1000 --group-add 1002' "$ARM_SH" || { echo "REFUSE [ROOT] launcher lacks the measured non-root spelling."; exit 91; }
grep -qE '^[^#]*allow-run-as-root' "$ARM_SH" && { echo "REFUSE [ROOT] launcher still passes --allow-run-as-root to mpirun."; exit 91; }
grep -qE '^[^#]*rm -rf "\$WORK"' "$ARM_SH" && { echo "REFUSE [EVIDENCE] launcher still rm -rf's the arm run tree."; exit 92; }
grep -qE '(^|[^#[:alnum:]_])sudo[[:space:]]' <(grep -vE '^[[:space:]]*#' "$ARM_SH") && { echo "REFUSE [PRIV] an executable sudo has grown back."; exit 93; }

export BASE="/home/ubuntu/certonomous-runs/CURRICULUM-D8G-R3-a6-adjoint-primal-$(date -u +%Y%m%dT%H%M%SZ)"
[ -e "$BASE" ] && { echo "REFUSE [EVIDENCE] $BASE exists; a run root is never written into."; exit 6; }
echo "D8G L1-P R3 QUEUE LAUNCH  base=$BASE  arm=L1-P  img=$IMG  launcher_md5=$GOT"
exec bash "$ARM_SH" L1-P "$IMG"
