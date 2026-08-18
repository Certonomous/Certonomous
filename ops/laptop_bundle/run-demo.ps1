# Start the offline demo console from PowerShell.
#
#   .\run-demo.ps1
#
# If PowerShell refuses to run it ("running scripts is disabled"), use this
# instead -- it does the same thing without changing any policy:
#
#   python replay_console.py
#
# Stops with Ctrl+C. Needs nothing but Python 3.10 or newer.

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

function Find-Python {
    foreach ($candidate in @('python', 'py', 'python3')) {
        $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        # `py` needs -3 to pick a Python 3; the others are already specific.
        $probeArgs = if ($candidate -eq 'py') { @('-3', '-c') } else { @('-c') }
        $script = 'import sys; raise SystemExit(0 if sys.version_info>=(3,10) else 1)'
        & $candidate @probeArgs $script 2>$null
        if ($LASTEXITCODE -eq 0) {
            return @{ Exe = $candidate; Pre = $(if ($candidate -eq 'py') { @('-3') } else { @() }) }
        }
    }
    return $null
}

$py = Find-Python
if ($null -eq $py) {
    Write-Host "Could not find Python 3.10 or newer."
    Write-Host ""
    Write-Host "Install it from https://www.python.org/downloads/windows/ and tick"
    Write-Host '"Add python.exe to PATH" in the installer, then close this window,'
    Write-Host "open a new one, and run this again."
    exit 1
}

& $py.Exe @($py.Pre) '--version'
& $py.Exe @($py.Pre) 'replay_console.py'
