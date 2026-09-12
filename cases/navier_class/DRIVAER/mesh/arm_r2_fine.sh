#!/bin/bash
# DRIVAER r2_fine -- ARMED LAUNCHER on a MEMORY TRIGGER, spec chosen by the probe.
#
# NO CLOCK TRIGGER. NO SPEND TRIGGER. NO KILL PRIMITIVE OF ANY KIND.
# There is no `timeout`, no `ulimit`, no `kill` in this file. Sanaa has ruled four
# times that no run stops on time or budget. The ONLY condition is MemAvailable,
# which is a PHYSICS guard: it exists so an OOM killer does not select another
# team's multi-day job. Sanaa lifted caps; she did not add RAM.
#
# SPEC IS CHOSEN BY MEASUREMENT, NOT BY GUESS:
#   probe C1 PASSES  -> (b) spec  (relativeSizes false, absolute first layer)
#   probe C1 FAILS   -> current spec (the A1 graded dict, unmodified)
# Rebuilding fine at the current spec buys a Cd that is capped NOT A RESULT on
# arrival by the same Y1 mechanism that caps coarse -- y+ is proportional to
# h_surf, measured. Waiting minutes for the probe costs nothing and decides it.
#
# It NEVER deletes and NEVER reverts. An existing target root is a REFUSAL.
set -u
D=/home/ubuntu/Certonomous/verification/runs/navier_class/DRIVAER
C1=$D/LAYERFIX_C1_coarse_absoluteFirstLayer
BLK=$D/r2_fine_BLOCKED_deliberate_stop_20260912T022405Z
R=$D/r2_fine
CANON=/home/ubuntu/certonomous-runs/navier_class/DRIVAER/drivaerml_r7a5c094/run_466/drivaer_466.stl
STATUS=$D/R2_FINE_ARMED_STATUS.txt
NEED_GIB=14.60      # 10.60 projected peak + the 4 GiB headroom the family's guard keeps
HOLD=3              # the trigger must hold this many consecutive samples
POLL=60

say () { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" >> "$STATUS"; }
say "ARMED. target=$R need=${NEED_GIB} GiB sustained over $HOLD samples. NO clock or spend trigger; no kill primitive in this launcher."

[ -e "$R" ] && { say "REFUSE: $R exists. A guard is satisfied by MOVING a case, never by disabling the guard."; exit 2; }

# ---- 1. WAIT FOR THE PROBE, THEN READ ITS VERDICT FROM ITS OWN ARTIFACT ----------
while [ ! -f "$C1/RUN_RC" ]; do sleep 20; done
SPEC=$(python3 - "$C1" <<'PY'
import json, os, sys
c1 = sys.argv[1]
rc = open(os.path.join(c1, "RUN_RC")).read().strip()
if rc != "0":
    print("CURRENT|probe build rc=%s -- no measurement, (b) unproven, current spec" % rc); raise SystemExit
p = os.path.join(c1, "C1_MEASURED.json")
if not os.path.exists(p):
    print("CURRENT|probe produced no C1_MEASURED.json -- (b) unproven"); raise SystemExit
d = json.load(open(p))
l = d["layers"]; cov = 100.0 * l["extruded_faces"] / l["extrude_candidate_faces"]
y = d["yplus"]["layered_group"]["yplus_area_weighted_median"]
# THE REGISTERED FALSIFIER, APPLIED VERBATIM (DRIVAER_R2B_LAYER_PROBE_PREREGISTRATION.md sec.0)
f1 = cov < 50.0
f2 = not (30.0 <= y <= 300.0)
if f1 or f2:
    print("CURRENT|F1=%s F2=%s coverage=%.3f%% yplus=%.3f -- (b) IS DEAD, current spec" % (f1, f2, cov, y))
else:
    print("BSPEC|coverage=%.3f%% yplus=%.3f -- (b) HOLDS" % (cov, y))
PY
)
WHY=${SPEC#*|}; SPEC=${SPEC%%|*}
say "PROBE READ: spec=$SPEC ($WHY)"

# ---- 2. WAIT FOR MEMORY. THE ONLY TRIGGER. --------------------------------------
n=0; k=0
while :; do
  A=$(awk '/^MemAvailable:/{printf "%.2f", $2/1048576}' /proc/meminfo)
  if awk -v a="$A" -v n="$NEED_GIB" 'BEGIN{exit !(a>=n)}'; then k=$((k+1)); else k=0; fi
  n=$((n+1))
  [ $((n % 30)) -eq 1 ] && say "waiting: MemAvailable=${A} GiB need=${NEED_GIB} consecutive=${k}/${HOLD}"
  [ $k -ge $HOLD ] && { say "TRIGGER MET: MemAvailable=${A} GiB held ${HOLD} samples"; break; }
  sleep $POLL
done

# ---- 3. STAGE. The BLOCKED tree's system/ IS the verified fine staging. ----------
[ -e "$R" ] && { say "REFUSE at fire time: $R now exists"; exit 2; }
mkdir -p "$R/system" "$R/constant/triSurface"
cp "$BLK"/system/* "$R/system/"
ln -s "$CANON" "$R/constant/triSurface/drivaer_466.stl"   # SYMLINK, never a 142 MB copy
if [ "$SPEC" = "BSPEC" ]; then
  python3 - "$R/system/snappyHexMeshDict" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
for a, b in (("    relativeSizes       true;",  "    relativeSizes       false;"),
             ("    finalLayerThickness 0.5;",   "    firstLayerThickness 2.10e-3;"),
             ("    minThickness        0.02;",  "    minThickness        5.25e-4;")):
    assert s.count(a) == 1, ("anchor not unique or absent", a, s.count(a))
    s = s.replace(a, b)
open(p, "w").write(s)
PY
  diff -u "$BLK/system/snappyHexMeshDict" "$R/system/snappyHexMeshDict" > "$R/THE_ONE_CHANGE.diff"
  say "staged (b) spec: 3-line change applied, THE_ONE_CHANGE.diff written"
else
  say "staged CURRENT spec: snappyHexMeshDict byte-identical to the A1 graded dict"
fi
{ echo "spec=$SPEC"; echo "why=$WHY"; echo "staged_utc=$(date -u +%FT%TZ)"
  echo "MemAvailable_at_fire_GiB=$(awk '/^MemAvailable:/{printf "%.2f", $2/1048576}' /proc/meminfo)"
  echo "NOTE=NO clock cap and NO spend cap is armed anywhere in this launch path."
} > "$R/RUN_META.txt"

# ---- 4. BUILD. rc captured INSIDE. ----------------------------------------------
S=$(date +%s)
bash /home/ubuntu/Certonomous/cases/navier_class/DRIVAER/mesh/run_build.sh fine "$R" 1 \
     > "$R/launcher.out" 2>&1
RC=$?
E=$(date +%s); W=$((E-S))
echo "$RC" > "$R/RUN_RC"; echo "$W" > "$R/WALL_SECONDS.txt"
awk -v w="$W" 'BEGIN{printf "%.2f\n", w/60.0}' > "$R/CORE_MINUTES.txt"
say "BUILD DONE rc=$RC wall=${W}s"
if [ "$RC" = "0" ]; then
  python3 /home/ubuntu/Certonomous/cases/navier_class/DRIVAER/mesh/stage_r2_measure.py \
      --case "$R" --out "$R/R2_MEASURED.json" --yplus > "$R/MEASURE.out" 2>&1
  say "measured rc=$?"
fi
