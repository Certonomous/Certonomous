#!/usr/bin/env bash
# Start the offline demo console. Git Bash on Windows, or any Linux/macOS shell.
#
#   bash run-demo.sh
#
# Stops with Ctrl+C. Needs nothing but Python 3.10 or newer.
set -u

cd "$(dirname "$0")" || exit 1

# Windows Git Bash usually has `python`; `py` is the Windows launcher; Linux
# and macOS have `python3`. Take whichever is really there and is new enough.
PY=""
for candidate in python3 python py; do
    if command -v "$candidate" >/dev/null 2>&1; then
        if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info>=(3,10) else 1)' >/dev/null 2>&1; then
            PY="$candidate"; break
        fi
    fi
done

if [ -z "$PY" ]; then
    echo "Could not find Python 3.10 or newer."
    echo
    echo "Install it from https://www.python.org/downloads/windows/ and tick"
    echo "\"Add python.exe to PATH\" in the installer, then close this window,"
    echo "open a new one, and run this again."
    exit 1
fi

echo "Using $("$PY" --version 2>&1)"
exec "$PY" replay_console.py
