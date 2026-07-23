# Morning refresh — regenerate the website artifacts against the FINAL ledger.
#
# Run this near end of shift (or in the morning) after the mega-batch has
# accumulated its full count, so benchmarks + wall reflect the true numbers.
#
#   pwsh sdk/scripts/refresh_website_artifacts.ps1
#
# To also fill the speed benchmark, first edit the _SPEED dict in
# build_benchmarks.py with BG-1's measured NACA 4412 core-min / speedup.

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Push-Location (Join-Path $repo "sdk")
try {
    python scripts/build_benchmarks.py
    python scripts/build_wall.py
    python -m chief_engineer.lab_stats
} finally {
    Pop-Location
}
