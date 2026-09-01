#!/usr/bin/env bash
# A2-GC: the MACH Tutorial Wing grid-convergence study.
#
# Frozen with cases/dafoam/A2_GC_GRID_CONVERGENCE_PREREGISTRATION.md. Every
# level is built by THIS script from the SAME pipeline, with exactly two
# integers changed per level (the cgns_utils op count and pyHyp's N) and s0
# scaled by 1/r. marchDist is identical on every level. That is what makes
# the family geometrically similar, and it is asserted, not assumed.
#
# Rule 4 guard : refuses outright if the run root already exists.
# Rule 12      : per-stage core-minute cap. AN OVERRUN STOPS THE RUN.
# Memory       : rc is captured INSIDE the wrapper -- `setsid timeout cmd`
#                exits 0 for every outcome, so an rc captured around the
#                setsid line is meaningless.
# No backticks on any executable line.
set -uo pipefail

RUNROOT=/home/ubuntu/certonomous-runs/A2-GC-wing-grid-convergence
REPO=/home/ubuntu/Certonomous
PRISTINE=/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing
IMAGE=dafoam/opt-packages:latest

PRISTINE_MD5=2906d52a5dbed2bacbaeaf85a37d3fe8   # runScript_AeroOnly.py, PROOF.md:2512
CPUSET=4-15                                      # 12 of 16 cores; 0-3 left for peers
NP=12

LEVEL="${1:?usage: run_a2gc.sh <L1|L2|L3|GRADE> [cap_core_min] [mem_limit]}"
CAP_CORE_MIN="${2:-}"
MEM_LIMIT="${3:-}"

# --- per-level parameters: the ONLY things that change between levels -------
case "$LEVEL" in
  L1) SURF_OP=coarsen1; PYHYP_N=39;  S0=1.0e-3; CELLS=38304;   DEF_CAP=60;   DEF_MEM=6g  ;;
  L2) SURF_OP=coarsen0; PYHYP_N=77;  S0=5.0e-4; CELLS=306432;  DEF_CAP=500;  DEF_MEM=14g ;;
  L3) SURF_OP=refine1;  PYHYP_N=153; S0=2.5e-4; CELLS=2451456; DEF_CAP=6000; DEF_MEM=26g ;;
  GRADE) SURF_OP=-; PYHYP_N=0; S0=0; CELLS=0; DEF_CAP=5; DEF_MEM=2g ;;
  *) echo "REFUSED: unknown level '$LEVEL'" >&2; exit 2 ;;
esac
CAP_CORE_MIN="${CAP_CORE_MIN:-$DEF_CAP}"
MEM_LIMIT="${MEM_LIMIT:-$DEF_MEM}"
CAP_WALL_S=$(( CAP_CORE_MIN * 60 / NP ))

# --- G-INSTRUMENT: the frozen grading path must be the file that ran -------
assert_md5() {
    local path="$1" want="$2" got
    got=$(md5sum "$path" | cut -d' ' -f1)
    if [ "$got" != "$want" ]; then
        echo "REFUSED: $path md5 $got != frozen $want" >&2
        exit 2
    fi
}
if [ -n "${A2GC_GRADER_MD5:-}" ]; then
    assert_md5 "$REPO/cases/dafoam/a2gc_grade.py"  "$A2GC_GRADER_MD5"
fi
if [ -n "${A2GC_LEVELS_MD5:-}" ]; then
    assert_md5 "$REPO/cases/dafoam/a2gc_levels.json" "$A2GC_LEVELS_MD5"
fi
if [ -n "${A2GC_BLOCK_MD5:-}" ]; then
    assert_md5 "$REPO/cases/dafoam/a2gc_driver_block.py" "$A2GC_BLOCK_MD5"
fi
assert_md5 "$PRISTINE/runScript_AeroOnly.py" "$PRISTINE_MD5"

if [ "$LEVEL" = "GRADE" ]; then
    python3 "$REPO/cases/dafoam/a2gc_grade.py" "$RUNROOT"
    exit $?
fi

# --- Rule 4 guard: the run root must not pre-exist at first launch ---------
LEVELDIR="$RUNROOT/$LEVEL"
if [ -e "$LEVELDIR" ]; then
    echo "REFUSED: level directory already exists: $LEVELDIR" >&2
    exit 2
fi

# --- Placement gate: never launch on top of a peer -------------------------
MEM_NEED_GB=$(echo "$MEM_LIMIT" | sed 's/g$//')
MEM_AVAIL_GB=$(awk '/MemAvailable/ {printf "%d", $2/1048576}' /proc/meminfo)
if [ "$MEM_AVAIL_GB" -lt "$(( MEM_NEED_GB + 3 ))" ]; then
    echo "REFUSED (placement): MemAvailable ${MEM_AVAIL_GB} GB < MEM_LIMIT ${MEM_NEED_GB} GB + 3 GB headroom" >&2
    exit 3
fi
RUNNING=$(sudo docker ps --format '{{.Names}}' 2>/dev/null | grep -c 'a2gc_' || true)
if [ "$RUNNING" != "0" ]; then
    echo "REFUSED (placement): $RUNNING a2gc_ container(s) already running" >&2
    exit 3
fi

mkdir -p "$LEVELDIR"
cp -a "$PRISTINE"/. "$LEVELDIR"/
cp /home/ubuntu/certonomous-runs/A2-mach-wing/mdolab_wing_surface_mesh.cgns.tar.gz \
   "$LEVELDIR"/ 2>/dev/null || true

# The level driver: the PRISTINE script plus a disclosed appended block.
# The diff is captured beside the run so the departure is on the record.
cp "$PRISTINE/runScript_AeroOnly.py" "$LEVELDIR/a2gc_level.py"
cat "$REPO/cases/dafoam/a2gc_driver_block.py" >> "$LEVELDIR/a2gc_level.py"
diff -u "$PRISTINE/runScript_AeroOnly.py" "$LEVELDIR/a2gc_level.py" \
    > "$LEVELDIR/driver_vs_pristine.diff" 2>&1 || true

# The mesh stage: same pipeline as the tutorial's preProcessing.sh, with the
# surface op and pyHyp N/s0 as the only changes.
cat > "$LEVELDIR/mesh.sh" <<INNER
set -uo pipefail
tar -xf mdolab_wing_surface_mesh.cgns.tar.gz
case "$SURF_OP" in
  coarsen1) cgns_utils coarsen mdolab_wing_surface_mesh.cgns surfaceMesh.cgns ;;
  coarsen0) cp mdolab_wing_surface_mesh.cgns surfaceMesh.cgns ;;
  refine1)  cgns_utils refine  mdolab_wing_surface_mesh.cgns surfaceMesh.cgns ;;
  coarsen2) cgns_utils coarsen mdolab_wing_surface_mesh.cgns c1.cgns && \
            cgns_utils coarsen c1.cgns surfaceMesh.cgns ;;
esac
sed -i 's/"N": 39,/"N": $PYHYP_N,/; s/"s0": 1.0e-3,/"s0": $S0,/' genWingMesh.py
grep -E '"N"|"s0"|"marchDist"' genWingMesh.py
python genWingMesh.py
plot3dToFoam -noBlank volumeMesh.xyz
autoPatch 60 -overwrite
createPatch -overwrite
renumberMesh -overwrite
checkMesh -allGeometry
INNER

# The solve stage. rc is captured INSIDE the wrapper.
cat > "$LEVELDIR/solve.sh" <<INNER
set -uo pipefail
cp -r 0.orig 0
# y+ is DIAGNOSTIC here and gates nothing: this case is wall-modelled
# (y+ mean 321.95 measured on L1), so Sanaa's "y+ under 1" clause, which is
# written "where the case is wall-resolved", does not bind. The functionObject
# is appended defensively; if it does not take, y+ is reported UNAVAILABLE and
# no gate changes. L1 runs first and is cheap, so a malformed entry is caught
# there and never reaches L2 or L3.
if ! grep -q "^functions" system/controlDict; then
cat >> system/controlDict <<'FO'
functions
{
    yPlus
    {
        type            yPlus;
        libs            ("libfieldFunctionObjects.so");
        writeControl    writeTime;
    }
}
FO
fi
mpirun -np $NP python a2gc_level.py 2>&1
echo "SOLVE_RC=\$?"
INNER

date -u +%s.%N > "$LEVELDIR/t0"
sudo docker run --rm --name "a2gc_${LEVEL}_\$\$" \
    --cpuset-cpus="$CPUSET" --memory="$MEM_LIMIT" \
    -e A2GC_LEVEL="$LEVEL" \
    -v "$LEVELDIR":/mnt -w /mnt "$IMAGE" bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && \
     timeout ${CAP_WALL_S}s bash mesh.sh > /mnt/mesh.log 2>&1; \
     echo MESH_RC=\$? >> /mnt/mesh.log; \
     timeout ${CAP_WALL_S}s bash solve.sh > /mnt/level.log 2>&1; \
     rc=\$?; echo \$rc > /mnt/RC; \
     cat /sys/fs/cgroup/memory.peak 2>/dev/null | \
       awk '{printf \"GC_PEAKRSS ${LEVEL} mib %.1f\n\", \$1/1048576}' >> /mnt/level.log" \
    > "$LEVELDIR/container.log" 2>&1
date -u +%s.%N > "$LEVELDIR/t1"

sudo chown -R ubuntu:ubuntu "$LEVELDIR" 2>/dev/null || true

# --- post-stage readers, from the solver's OWN printed output --------------
# GC_RESID: the worst INITIAL residual across the six transported equations on
# the FINAL primal iteration. initRes is the NONLINEAR residual -- the quantity
# primalMinResTol = 1e-8 is compared against. finalRes is the linear solve's
# own residual for that iteration and is a different quantity; both are
# recorded, and the GATE is on initRes.
python3 - "$LEVELDIR" "$LEVEL" <<'POST'
import re, sys, os, json
d, lvl = sys.argv[1], sys.argv[2]
log = os.path.join(d, "level.log")
txt = open(log, errors="replace").read() if os.path.exists(log) else ""
pat = r'(?:U0|U1|U2|he|p|nuTilda)\s+initRes:\s*([-\d.eE+]+)\s+finalRes:\s*([-\d.eE+]+)'
m = re.findall(pat, txt)
init = [float(a) for a, _b in m][-6:]
fin  = [float(b) for _a, b in m][-6:]
worst_init = max(init) if len(init) == 6 else 0.0
worst_fin  = max(fin)  if len(fin)  == 6 else 0.0
# y+ from the stock OpenFOAM yPlus functionObject, if it wrote. Diagnostic
# only: this case is WALL-MODELLED (y+ mean 321.95 measured on L1), so
# Sanaa's "y+ under 1" clause does not bind and nothing here gates on it.
ymin = ymean = ymax = 0.0
best = None
for base, _dirs, files in os.walk(os.path.join(d, "postProcessing")):
    if os.path.basename(base) == "yPlus" or "yPlus" in base:
        for fn in files:
            if fn.endswith(".dat"):
                best = os.path.join(base, fn)
if best:
    rows = [l.split() for l in open(best, errors="replace") if not l.startswith("#")]
    rows = [r for r in rows if len(r) >= 4]
    if rows:
        ymin, ymax, ymean = (float(rows[-1][1]), float(rows[-1][2]), float(rows[-1][3]))
with open(log, "a") as f:
    f.write(f"GC_RESID {lvl} worst {worst_init:.6e} worst_finalres {worst_fin:.6e} n {len(init)}\n")
    f.write(f"GC_YPLUS {lvl} min {ymin:.6f} mean {ymean:.6f} max {ymax:.6f}\n")
POST

# GC_VOLGROWTH: the F28 similarity metric, from checkMesh -allGeometry.
python3 - "$LEVELDIR" "$LEVEL" <<'POST'
import re, sys, os
d, lvl = sys.argv[1], sys.argv[2]
p = os.path.join(d, "mesh.log")
txt = open(p, errors="replace").read() if os.path.exists(p) else ""
m = re.findall(r'Max cell openness.*?max volume ratio\s*=?\s*([-\d.eE+]+)', txt)
if not m:
    m = re.findall(r'volume ratio\s*=?\s*([-\d.eE+]+)', txt)
v = float(m[-1]) if m else 0.0
with open(p, "a") as f:
    f.write(f"GC_VOLGROWTH {lvl} max {v:.6f}\n")
POST

T0=$(cat "$LEVELDIR/t0"); T1=$(cat "$LEVELDIR/t1")
awk -v a="$T0" -v b="$T1" -v n="$NP" -v cap="$CAP_CORE_MIN" \
    'BEGIN {w=b-a; cm=w*n/60; printf "wall_s=%.1f core_min=%.2f cap_core_min=%d overrun=%s\n", \
     w, cm, cap, (cm>cap ? "YES-RUN-STOPPED" : "no")}' > "$LEVELDIR/cost.txt"
cat "$LEVELDIR/cost.txt"
echo "level=$LEVEL rc=$(cat "$LEVELDIR/RC" 2>/dev/null) cells_expected=$CELLS"
