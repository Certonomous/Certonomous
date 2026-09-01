#!/usr/bin/env bash
# A1WR STAGE 0 -- build L1/L2/L3.  Runs INSIDE the DAFoam container.
# Governed by A1WR_PREREGISTRATION.md v1.1 (amendment 1).
# ---------------------------------------------------------------------------
# DO NOT set -u BEFORE SOURCING loadDAFoam.sh, AND DO NOT SWALLOW ITS STDERR.
# MEASURED on this image: OpenFOAM-v2506/etc/bashrc line 180 dereferences
# WM_PROJECT_DIR while it is unbound.  Under `set -u` that aborts the shell at
# rc 127 -- and the lab's usual defensive idiom
#     set -uo pipefail
#     source .../loadDAFoam.sh >/dev/null 2>&1
# sends the ONLY diagnostic to /dev/null, so the script dies at line 5 with
# rc 1, an empty log and no message.  A wrapper capturing rc around this would
# read a genuine refusal as an infrastructure blip.  Source first, with stderr
# VISIBLE, then turn -u on.
# ---------------------------------------------------------------------------
# AND DO NOT PIPE THE SOURCE EITHER: `source ... | tail` runs it in a SUBSHELL,
# so every exported variable dies with that subshell and the parent sees an
# unloaded environment.  The env-assert below caught exactly that.  Redirect to
# a FILE, which keeps the source in the current shell and still keeps the
# message.
set -o pipefail
source /home/dafoamuser/dafoam/loadDAFoam.sh > /mnt/log.loadDAFoam 2>&1
set -u
test -n "${WM_PROJECT_VERSION:-}" || { echo "S0_FATAL OpenFOAM env not loaded"; exit 89; }
echo "S0_ENV WM_PROJECT_VERSION=$WM_PROJECT_VERSION"
cd /mnt || { echo "S0_FATAL cannot cd /mnt"; exit 90; }

# ---- point-of-use asserts (a startup-only assert is how a valid path becomes
# ---- a silent failure on every later use) -----------------------------------
test -f a1wr_genmesh.py            || { echo "S0_FATAL generator absent at point of use"; exit 91; }
test -f profiles/NACA0012PS.profile || { echo "S0_FATAL PS profile absent at point of use"; exit 91; }
test -f profiles/NACA0012SS.profile || { echo "S0_FATAL SS profile absent at point of use"; exit 91; }

# ---- G-MESHFAM limb 1: the generator selfcheck MUST pass before any build ----
echo "S0_SELFCHECK_BEGIN"
python a1wr_genmesh.py --selfcheck
SC=$?
echo "S0_SELFCHECK_RC=$SC"
[ $SC -eq 0 ] || { echo "S0_REFUSE generator selfcheck did not pass -- no mesh is built"; exit 2; }

GROWTH_CEILING=1.35

for L in L1 L2 L3; do
  echo "===== S0_LEVEL_BEGIN $L ====="
  cd /mnt/$L || { echo "S0_FATAL cannot cd $L"; exit 90; }

  # rule 4 guard: refuse a level that already carries a mesh
  if [ -e constant/polyMesh ]; then
    echo "S0_REFUSE $L already has constant/polyMesh -- inspect, do not overwrite"; exit 6
  fi

  python /mnt/a1wr_genmesh.py --level $L --outdir . --profiles /mnt/profiles 2>&1 | tee log.genmesh
  GRC=${PIPESTATUS[0]}
  echo "S0_GENMESH_RC_$L=$GRC"
  [ $GRC -eq 0 ] || { echo "S0_FATAL genmesh failed for $L"; exit 3; }

  # ---- the registered growth-ratio ceiling, APPLIED HERE, before the solve ----
  G=$(grep -oE "impliedGrowthRatio=[0-9.]+" log.genmesh | tail -1 | cut -d= -f2)
  echo "S0_GROWTH_$L=$G ceiling=$GROWTH_CEILING"
  awk -v g="$G" -v c="$GROWTH_CEILING" 'BEGIN{ if (g+0 > c+0) exit 1; else exit 0 }' \
    || { echo "S0_REFUSE $L growth ratio $G exceeds registered ceiling $GROWTH_CEILING"; exit 4; }

  plot3dToFoam -noBlank volumeMesh.xyz > log.plot3dToFoam 2>&1 || { echo "S0_FATAL plot3dToFoam $L"; exit 3; }
  autoPatch 30 -overwrite            > log.autoPatch     2>&1 || { echo "S0_FATAL autoPatch $L";     exit 3; }
  createPatch -overwrite             > log.createPatch   2>&1 || { echo "S0_FATAL createPatch $L";   exit 3; }
  renumberMesh -overwrite            > log.renumberMesh  2>&1 || { echo "S0_FATAL renumberMesh $L";  exit 3; }
  checkMesh                          > log.checkMesh     2>&1
  echo "S0_CHECKMESH_RC_$L=$?"

  # ---- MEASURED, not assumed: cell count, patch set, and the wall-typed patch.
  # createPatchDict builds `wing` from auto2/auto3 produced by `autoPatch 30`.
  # A finer mesh can yield a DIFFERENT number of auto patches, which would leave
  # `wing` missing or mistyped and make useWallFunction:False a SILENT no-op.
  NC=$(grep -oE "^ *cells: *[0-9]+" log.checkMesh | grep -oE "[0-9]+" | tail -1)
  echo "S0_NCELLS_$L=$NC"
  echo "S0_AUTOPATCH_$L=$(grep -cE '^ *auto[0-9]+' log.autoPatch || true)"
  echo "--- S0_BOUNDARY_$L ---"
  python - <<'PYEOF'
import re, gzip, os
p = "constant/polyMesh/boundary"
raw = gzip.open(p + ".gz", "rt").read() if os.path.exists(p + ".gz") else open(p).read()
body = raw[raw.rindex("//", 0, raw.index("(")) if False else 0:]
names = re.findall(r"^\s{4}(\w+)\s*$\s*\{([^}]*)\}", raw, re.M)
wall_ok = False
for n, blk in names:
    m = re.search(r"type\s+(\w+)", blk)
    f = re.search(r"nFaces\s+(\d+)", blk)
    t = m.group(1) if m else "?"
    print("  PATCH %-12s type=%-10s nFaces=%s" % (n, t, f.group(1) if f else "?"))
    if n == "wing" and t == "wall":
        wall_ok = True
print("  S0_WING_IS_TYPE_WALL=%s" % ("YES" if wall_ok else "NO"))
PYEOF
  echo "===== S0_LEVEL_END $L ====="
  cd /mnt
done
echo "S0_ALL_LEVELS_BUILT"
