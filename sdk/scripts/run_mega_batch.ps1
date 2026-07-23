# Launch the all-night mega-batch of REAL solver evaluations.
#
# Streams a deterministic, resumable sequence of OpenFOAM cylinder solves,
# VSPAERO wing polars, and reduced-order valve-cycle evaluations into a durable
# JSONL ledger. Safe to stop and restart — it resumes from the ledger. Stop it
# gracefully by creating the STOP sentinel next to the ledger.
#
#   pwsh sdk/scripts/run_mega_batch.ps1
#   # ... to stop: New-Item demo-output/website/mega-batch/STOP
#
# Honours the compute treaty: 4 workers max. Cylinder/wing cases are written
# under the repo work root (NOT the WSL study-* dirs) and deleted per-solve.

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)   # repo root
$env:CHIEF_ADAPTER       = "openfoam"
$env:OPENFOAM_RUN_PREFIX = "wsl -d Ubuntu -- openfoam2606"
$env:OPENVSP_RUN_PREFIX  = "wsl -d Ubuntu --"

$ledger = Join-Path $repo "demo-output/website/mega-batch/ledger.jsonl"
$work   = Join-Path $repo "demo-output/website/mega-batch/work"

Push-Location (Join-Path $repo "sdk")
try {
    python -m workflows.mega_batch `
        --ledger $ledger `
        --work-root $work `
        --workers 4 `
        --max-seconds ($args[0] ?? 43200)   # default 12h safety cap
} finally {
    Pop-Location
}
