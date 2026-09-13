#!/bin/bash
# DRIVAER R3 per-patch y+ probe.  Runs on a COPY; the graded tree is never written to.
# Two arms deliberately: the GENERIC postProcess (the known-blind negative control)
# and the SOLVER spelling.  Plus the CRM positive control re-driven fresh, so the
# reader is shown able to see a non-zero in the same session as the zero it reports.
set -uo pipefail
R=/home/ubuntu/Certonomous/verification/runs/navier_class/DRIVAER
SRC=$R/r2c_medium_blended_R3
P=$R/YPLUS_PROBE/r2c_medium_blended_R3
CRM=$R/YPLUS_PROBE/CRM_POSITIVE_CONTROL
LOG=$P/PROBE_RUN.log

# --- census of the graded tree BEFORE (proof it is not touched) ---
mkdir -p "$P"
census () { find "$1" -type f -printf '%P %s %T@\n' 2>/dev/null | sort | md5sum | cut -d' ' -f1; }
BEFORE=$(census "$SRC")

rm -rf "$P/10000" "$P/constant" "$P/system" "$P/0"
mkdir -p "$P"
cp -r "$SRC/system"   "$P/system"
mkdir -p "$P/constant"
cp    "$SRC/constant/transportProperties"  "$P/constant/"
cp    "$SRC/constant/turbulenceProperties" "$P/constant/"
cp -r "$SRC/constant/polyMesh"             "$P/constant/polyMesh"
cp -r "$SRC/10000"                         "$P/10000"
# the probe must PRODUCE y+, never read one lying about: assert none was copied in
if [ -e "$P/10000/yPlus" ]; then echo "REFUSE: a yPlus field was copied in; the probe would read its own input" ; exit 3; fi
# forceCoeffs functions would re-run on a postProcess pass; strip the include
sed -i 's/^ *#include *"forceCoeffs"/\/\/ probe: forceCoeffs include removed/' "$P/system/controlDict"

set +u; source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1; set -u
cd "$P"
{
echo "=== ARM 1 (NEGATIVE CONTROL): generic postProcess -- expected BLIND ==="
postProcess -func yPlus -time 10000 > "$P/log.yPlus" 2>&1; echo "generic rc=$?"
echo "=== ARM 2 (SOLVER SPELLING): simpleFoam -postProcess ==="
rm -f "$P/10000/yPlus"
simpleFoam -postProcess -func yPlus -time 10000 > "$P/log.yPlus2" 2>&1; echo "solver rc=$?"
} > "$LOG" 2>&1

# --- CRM positive control, re-driven fresh in THIS session ---
cd "$CRM"
rm -f "$CRM/4000/yPlus"
{
echo "=== CRM POSITIVE CONTROL, re-driven $(date -u +%FT%TZ) ==="
rhoSimpleFoam -postProcess -func yPlus -time 4000 > "$CRM/log.yPlus2.REDRIVEN_2026-09-13" 2>&1; echo "crm rc=$?"
} >> "$LOG" 2>&1

AFTER=$(census "$SRC")
{
echo "=== GRADED-TREE CENSUS ==="
echo "before=$BEFORE"
echo "after =$AFTER"
[ "$BEFORE" = "$AFTER" ] && echo "IDENTICAL -- graded tree not touched" || echo "DIFFERENT -- GRADED TREE WAS MODIFIED"
} >> "$LOG" 2>&1
echo PROBE_DONE
