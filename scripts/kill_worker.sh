#!/usr/bin/env bash
# On-camera sabotage: kill a live mission worker by index.
#
#   scripts/kill_worker.sh 2      # kill worker slot 2
#
# The running lab sees the marker on that worker's next unit of work, reports
# the loss in the transcript, reprovisions a fresh worker, and completes the
# mission with the correct numbers. The marker is cleared automatically by the
# recovery wave. Set CERTONOMOUS_SABOTAGE_DIR to override the marker location
# (must match the server's).
set -euo pipefail

if [[ $# -lt 1 || ! "$1" =~ ^[0-9]+$ ]]; then
  echo "usage: $0 <worker-index>   (e.g. $0 2)" >&2
  exit 2
fi

index="$1"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dir="${CERTONOMOUS_SABOTAGE_DIR:-$repo_root/mission-output/.sabotage}"
mkdir -p "$dir"
marker="$dir/kill-worker-$index"
: > "$marker"

echo "SABOTAGE armed: worker $index will be killed on its next task."
echo "  marker: $marker"
echo "  the lab will detect the loss, reprovision, and finish with correct numbers."
