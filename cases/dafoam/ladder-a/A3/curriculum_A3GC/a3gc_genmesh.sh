#!/usr/bin/env bash
# =====================================================================
# a3gc_genmesh.sh -- **FROZEN by the dafoam-supervisor, 2026-09-11.**
#
# Stage 1 of A3GC: generate the three registered volume meshes
#
#     level  surface  surf.faces   N   wall-normal cells   volume cells
#     L3       c2        6,240     17        16               99,840
#     L2       c1       24,960     33        32              798,720
#     L1       c0       99,840     65        64            6,389,760
#
# (PREREGISTRATION.md Sec.2.3 / Sec.2.5, commit
#  085ab04ef9c7e5b18af5fad5a721040594274174).
#
# EXIT CONDITION, REGISTERED (Sec.6 stage 1): three levels at EXACTLY
# 99,840 / 798,720 / 6,389,760 cells.  "Any departure from 99,840 /
# 798,720 / 6,389,760 is a LAUNCH-BLOCKING REFUSAL, not a note."  This
# script measures the result and refuses (exit 2) on any other count.
# It does not solve; it does not touch any existing run root.
#
# SUBMISSIONS PARKED.  Nothing here sends anything anywhere.
# =====================================================================
set -euo pipefail

# --------------------------------------------------------------------
# THE IMAGE IS PINNED BY DIGEST, NEVER BY TAG.
# DAFOAM_CHARTER.md Sec.6: a version string is not an identity.
# PREREG Sec.2.2 names it; verified present on this box 2026-09-11:
#   docker image inspect dafoam-subpclu:v2 --format '{{.Id}}'
#     -> sha256:8352629516bb363345fd802ed6092f878bad0a612c05c98d492a14bd94729d46
# `cgns_utils` and pyHyp live ONLY inside it
# (/home/dafoamuser/dafoam/packages/miniconda3/{bin/cgns_utils,
#  lib/python3.10/site-packages/pyhyp}); neither is importable on the host.
# --------------------------------------------------------------------
IMAGE_DIGEST="sha256:8352629516bb363345fd802ed6092f878bad0a612c05c98d492a14bd94729d46"

# --------------------------------------------------------------------
# REGISTERED PARAMETERS -- each cites the section that fixed it
# --------------------------------------------------------------------
# Sec.2.3: the coarsening chain.  c0 is the source; c1/c2 are 1 and 2
#          passes of `cgns_utils coarsen`.  Every step is exactly 4.000.
#          *** NO LEVEL BEYOND c3 MAY EVER BE DESCRIBED AS A FACTOR-2
#          COARSENING OF THIS SURFACE (Sec.2.3), AND c3 ITSELF IS EXCLUDED
#          FROM THE FAMILY (Sec.2.4: it collapses the trailing edge to zero
#          thickness and is not the same discrete body). ***
declare -A COARSEN_PASSES=( [L3]=2 [L2]=1 [L1]=0 )
declare -A N_LAYERS=(       [L3]=17 [L2]=33 [L1]=65 )
declare -A WANT_CELLS=(     [L3]=99840 [L2]=798720 [L1]=6389760 )
declare -A WANT_WING=(      [L3]=6240  [L2]=24960  [L1]=99840   )

# Sec.2.6: s0 IS HELD FIXED AT 1.0e-4 ON ALL THREE LEVELS.
#   *** THIS IS DELIBERATE AND DISCLOSED.  DO NOT "FIX" IT TO SCALE WITH r. ***
#   Scaling s0 by r (4e-4 / 2e-4 / 1e-4) would be strictly systematic, and was
#   REJECTED: the shipped 399,360-cell solution runs useWallFunction True at
#   measured y+ min 5.69 / mean 33.75 / max 103.52, and scaling s0 by 4 on L3
#   puts y+ mean near 135 and max near 414 -- outside the range in which the
#   wall function is valid.  A strictly systematic family whose coarsest level
#   solves different wall physics is a worse instrument than a family with one
#   disclosed non-systematic direction.  The consequence, registered before the
#   run: the observed order p this family reports is a SURFACE-AND-OUTER-FIELD
#   ORDER, not a full-field order.
S0="1.0e-4"
MARCH_DIST="12.0"
CMAX="0.1"

# autoPatch feature angle.  The brief directs 45 (the A6 preProcessing.sh
# pattern).  *** MEASURED CAVEAT, READ BEFORE FIRST USE: the shipped M6 case
# used autoPatch 60, and its own log
# cases/dafoam/ladder-a/logs_A3/logMeshGeneration.txt:207 records
#   "Exec : autoPatch 60 -overwrite" -> auto0 6240 / auto1 8704 / auto2 6240,
# which is exactly the wing/sym/inout decomposition system/createPatchDict
# expects.  Whether 45 reproduces that decomposition on the M6 IS NOT
# MEASURED.  The post-check below refuses on any other patch table, and names
# 60 as the first thing to try. ***
AUTOPATCH_ANGLE="${AUTOPATCH_ANGLE:-45}"

# --------------------------------------------------------------------
usage() {
  cat <<USAGE
usage: $0 --source <c0.cgns> --template <case-dir> --out <parent-dir> [--levels "L3 L2 L1"] [--dry-run]

  --source    the c0 surface, /home/ubuntu/certonomous-runs/A3-onera-m6-transonic/m6_surfaceMesh_fine.cgns
              (2,535,424 B, md5 e6c853158d351de3f382ce5afa513997, PREREG Sec.2.1)
  --template  a case directory supplying system/ and 0.orig/ (the shipped M6 case)
  --out       parent directory for <out>/A3GC-L3, -L2, -L1.  Each must NOT exist.
  --dry-run   print the exact command sequence and exit 0 without running anything.
USAGE
}

SOURCE=""; TEMPLATE=""; OUT=""; LEVELS="L3 L2 L1"; DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --source)   SOURCE="$2"; shift 2;;
    --template) TEMPLATE="$2"; shift 2;;
    --out)      OUT="$2"; shift 2;;
    --levels)   LEVELS="$2"; shift 2;;
    --dry-run)  DRY=1; shift;;
    -h|--help)  usage; exit 0;;
    *) echo "REFUSE [ARGS] unknown argument: $1" >&2; usage >&2; exit 2;;
  esac
done
[ -n "$SOURCE" ] && [ -n "$TEMPLATE" ] && [ -n "$OUT" ] || { usage >&2; exit 2; }

refuse() { printf '\nREFUSE [%s]\n  %s\n  exit 2 -- refusing rather than degrading.\n' "$1" "$2" >&2; exit 2; }

if [ "$DRY" = 0 ]; then
  [ -r "$SOURCE" ]      || refuse "INPUT" "source surface not readable: $SOURCE"
  [ -d "$TEMPLATE/system" ] || refuse "INPUT" "template has no system/: $TEMPLATE"
  command -v docker >/dev/null || refuse "TOOL" "docker not on PATH"
  docker image inspect "$IMAGE_DIGEST" >/dev/null 2>&1 \
    || refuse "IMAGE" "the pinned image $IMAGE_DIGEST is not present.  The image is named by hash, never by tag (DAFOAM_CHARTER Sec.6); this script will not silently fall back to a tag."
fi

RUN() {   # RUN <workdir> <command...>   -- inside the pinned image, 1 cpu
  local wd="$1"; shift
  if [ "$DRY" = 1 ]; then
    printf '    docker run --rm --cpus=1 -v %s:/w -w /w %s bash -lc %q\n' "$wd" "$IMAGE_DIGEST" "$*"
  else
    docker run --rm --cpus=1 -u "$(id -u):$(id -g)" \
      -v "$wd":/w -w /w "$IMAGE_DIGEST" \
      bash -lc "source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1 || true; set -e; $*"
  fi
}

for LV in $LEVELS; do
  NP="${COARSEN_PASSES[$LV]}"; NL="${N_LAYERS[$LV]}"
  WD="$OUT/A3GC-$LV"
  printf '\n===== %s : %d coarsen pass(es), N = %d, s0 = %s =====\n' "$LV" "$NP" "$NL" "$S0"

  # --- the age/overwrite guard (CLAUDE.md rule 4): a guard refuses a case
  #     where 0 or a time directory already exists.  A graded run root is
  #     evidence and is never written into.
  if [ -e "$WD" ]; then
    if [ "$DRY" = 1 ]; then
      printf '    (dry-run) would REFUSE: %s already exists\n' "$WD"
    else
      refuse "GUARD" "$WD already exists.  A graded run root is evidence and is never written into, and a mesh regenerated on top of an old one cannot be dated.  Move it aside by hand or choose another --out."
    fi
  fi

  if [ "$DRY" = 1 ]; then
    printf '    mkdir -p %s && cp -r %s/system %s/0.orig %s/\n' "$WD" "$TEMPLATE" "$TEMPLATE" "$WD"
    printf '    cp %s %s/m6_surfaceMesh_fine.cgns\n' "$SOURCE" "$WD"
  else
    mkdir -p "$WD"
    cp -r "$TEMPLATE/system" "$WD/"
    [ -d "$TEMPLATE/0.orig" ] && cp -r "$TEMPLATE/0.orig" "$WD/"
    cp "$SOURCE" "$WD/m6_surfaceMesh_fine.cgns"
  fi

  # --- 1. cgns_utils coarsen, NP times, c0 -> surfaceMesh.cgns
  #        (the shipped case's own chain: first pass names the output, later
  #         passes coarsen in place -- PREREG Sec.2.3 / the case's
  #         preProcessing.sh lines 21-23.)
  if [ "$NP" -eq 0 ]; then
    CHAIN="cp m6_surfaceMesh_fine.cgns surfaceMesh.cgns"
  else
    CHAIN="cgns_utils coarsen m6_surfaceMesh_fine.cgns surfaceMesh.cgns"
    for _ in $(seq 2 "$NP"); do CHAIN="$CHAIN && cgns_utils coarsen surfaceMesh.cgns"; done
  fi
  RUN "$WD" "$CHAIN"

  # --- 2. genWingMesh.py -- pyHyp hyperbolic extrusion.
  #        Written per level because N is the only thing that moves;
  #        s0/marchDist/cMax are the registered constants above.
  if [ "$DRY" = 1 ]; then
    printf '    write %s/genWingMesh.py  with  "N": %d, "s0": %s, "marchDist": %s, "cMax": %s\n' \
      "$WD" "$NL" "$S0" "$MARCH_DIST" "$CMAX"
  else
    cat > "$WD/genWingMesh.py" <<PYEOF
"""A3GC level $LV -- pyHyp extrusion of surfaceMesh.cgns.
N = $NL (wall-normal layers; wall-normal CELLS = N-1 = $((NL-1))).
s0 = $S0 -- HELD FIXED ON ALL THREE LEVELS, deliberately (PREREG Sec.2.6).
Generated by a3gc_genmesh.sh.  Do not hand-edit; regenerate."""

from pyhyp import pyHyp

options = {
    "inputFile": "surfaceMesh.cgns",
    "fileType": "CGNS",
    "unattachedEdgesAreSymmetry": True,
    "outerFaceBC": "farfield",
    "autoConnect": True,
    "BC": {},
    "families": "wall",
    "N": $NL,
    "s0": $S0,
    "marchDist": $MARCH_DIST,
    "ps0": -1.0,
    "pGridRatio": -1.0,
    "cMax": $CMAX,
    "epsE": 1.0,
    "epsI": 2.0,
    "theta": 3.0,
    "volCoef": 0.25,
    "volBlend": 0.0005,
    "volSmoothIter": 100,
    "kspreltol": 1e-4,
}

hyp = pyHyp(options=options)
hyp.run()
hyp.writePlot3D("volumeMesh.xyz")
PYEOF
  fi

  # --- 3. extrude, convert, patch, renumber
  RUN "$WD" "python genWingMesh.py &> logMeshGeneration.txt"
  RUN "$WD" "plot3dToFoam -noBlank volumeMesh.xyz >> logMeshGeneration.txt"
  RUN "$WD" "autoPatch $AUTOPATCH_ANGLE -overwrite >> logMeshGeneration.txt"
  RUN "$WD" "createPatch -overwrite >> logMeshGeneration.txt"
  RUN "$WD" "renumberMesh -overwrite >> logMeshGeneration.txt"
  RUN "$WD" "checkMesh -allGeometry -allTopology &> logCheckMesh.txt"

  # --- 4. THE REGISTERED EXIT CONDITION, MEASURED
  if [ "$DRY" = 1 ]; then
    printf '    verify: cells == %d and wing nFaces == %d, else REFUSE\n' \
      "${WANT_CELLS[$LV]}" "${WANT_WING[$LV]}"
    continue
  fi
  GRADE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/a3gc_grade.py"
  PROBE="$(python3 "$GRADE" probe --case "$WD" --cgns "$WD/surfaceMesh.cgns")" || \
    refuse "MEASURE" "could not read back the mesh just written in $WD"
  GOT_CELLS=$(printf '%s' "$PROBE" | python3 -c 'import json,sys; print(json.load(sys.stdin)["cells"])')
  GOT_WING=$(printf '%s' "$PROBE"  | python3 -c 'import json,sys; print(json.load(sys.stdin)["patches"]["wing"]["nFaces"])')
  printf '  measured: cells = %s (want %s), wing nFaces = %s (want %s)\n' \
    "$GOT_CELLS" "${WANT_CELLS[$LV]}" "$GOT_WING" "${WANT_WING[$LV]}"

  [ "$GOT_CELLS" = "${WANT_CELLS[$LV]}" ] || refuse "STAGE1" \
    "$LV has $GOT_CELLS cells, registered ${WANT_CELLS[$LV]}.  PREREG Sec.2.5: 'Any departure from 99,840 / 798,720 / 6,389,760 is a launch-blocking refusal, not a note.'  DO NOT SOLVE."
  [ "$GOT_WING" = "${WANT_WING[$LV]}" ] || refuse "STAGE1" \
    "$LV wing patch has $GOT_WING faces, registered ${WANT_WING[$LV]}.  Cell count alone does not identify a level -- /home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse has EXACTLY 99,840 cells with 1,560 wing faces and is NOT the registered L3.  If the patch table is wrong, the first thing to try is AUTOPATCH_ANGLE=60, which is what the shipped M6 case used (logs_A3/logMeshGeneration.txt:207 -> auto0 6240 / auto1 8704 / auto2 6240)."

  grep -q 'Mesh has 3 geometric (non-empty/wedge) directions' "$WD/logCheckMesh.txt" || refuse "G-MESH" \
    "$LV: checkMesh does not report 3 geometric (non-empty/wedge) directions (PREREG Sec.3.2).  The line is cited by name in the record and must be present."
  printf '  %s OK\n' "$LV"
done

printf '\nAll requested levels generated and measured against the registered counts.\n'
printf 'NOTHING HAS BEEN SOLVED.  Stage 2 (G-SYS / G-MESH / G-COLD / G-PLANT /\n'
printf 'G-TOL / G-RES) and the freeze are the dafoam-supervisor'"'"'s acts.\n'
