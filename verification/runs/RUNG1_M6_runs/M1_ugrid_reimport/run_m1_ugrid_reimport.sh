#!/bin/bash
# R1-M1 -- UGRID RE-IMPORT of the M6I nested family, as an ADMISSIBILITY MEASUREMENT.
#
#   THIS IS NOT A GRADED RUN AND NO VERDICT OF THE FIXED VOCABULARY ATTACHES TO IT.
#   No solver is launched by this script.  It converts and inspects only.
#
# WHY THIS EXISTS.  The M6I family was imported into OpenFOAM once before, through
# plot3dToFoam, from wing_strct.N.ufmt.  That route DESTROYS PATCH IDENTITY: it produced
# ONE patch, `defaultFaces` type wall, 27,648 faces on L1 -- the wing, the symmetry plane
# and the 100-chord farfield all lumped into a single wall.  RUNG0_MESH_IMPORT_PREREGISTRATION
# section 4 records exactly that and drops Plot3D for it.
#
#   The SAME generator run also wrote wing_strct.N.lb8.ugrid, which carries the boundary
#   faces AND their tags, and wing_strct.N.mapbc names the three parts:
#       1  4000 wing      -> OpenFOAM wall
#       2  6662 symmetry  -> OpenFOAM symmetry   (NOT empty, NOT wall)
#       3  5050 farfield  -> OpenFOAM patch
#   So the UGRID route recovers the boundary identity the Plot3D route threw away.
#
#   AND IT MAY CHANGE THE QUALITY NUMBERS.  The .lb8.ugrid header declares PRISMS at the
#   rounded tip (12,288 on L1) alongside 970,752 hexes.  plot3dToFoam, reading a purely
#   structured file, cannot express a prism: it emitted those cells as COLLAPSED
#   (degenerate) hexahedra.  A collapsed hex has a zero-area face whose normal is
#   ill-defined; a prism does not.  Whether the M6I family's 87.66-87.75 deg maximum
#   non-orthogonality is a property of the TOPOLOGY or an artefact of the COLLAPSED-HEX
#   IMPORT has never been measured.  This script measures it.
#
# L-459 DISCIPLINE, ENFORCED HERE.  checkMesh prints "Non-orthogonality check OK." two lines
# below a max of 88.889 deg, and its closing "Failed N mesh checks" counts a DIFFERENT check.
# Nothing downstream of this script may read a verdict string.  The reader below parses the
# NUMERIC "Mesh non-orthogonality Max:" value and records the verdict lines in a field whose
# name says they are not a gate.
#
# COST.  Converter rate 0.203 core-min/Mcell, MEASURED, re-derived in
# RUNG0_MESH_IMPORT_PREREGISTRATION section 5 from cases/committee-grids/measurements.jsonl.
#   convert  1.12128 Mcell x 0.203              = 0.228 core-min
#   checkMesh at 1x the converter rate          = 0.228 core-min
#   +22% contention band                        = 0.56 core-min ESTIMATE
#   CAP 6.0 core-min (10.7x headroom) -- an overrun STOPS the run, it does not get a new budget.
# Structural enforcement: `timeout 360` per stage at 1 rank.  Dollars are DERIVED at
# $0.0513/core-h and are never measured on this box (COMPUTE_BUDGET_CHARTER section 5).
set -u
RUNS="$(cd "$(dirname "$0")" && pwd)"
MESH=/home/ubuntu/Certonomous/verification/runs/M6I_runs/mesh
CONV=/home/ubuntu/Certonomous/cases/committee-grids/ugrid_to_foam.py
COST="$RUNS/COST.tsv"

[ -f "$CONV" ] || { echo "CONVERTER ABSENT: $CONV"; exit 1; }

printf 'stage\twall_s\tranks\tcore_min\trc\n' > "$COST"
t0=$(date +%s)
timed () {  # timed <name> <ranks> -- cmd...
  local name="$1" ranks="$2"; shift 3
  local s; s=$(date +%s); "$@"; local rc=$?; local w=$(( $(date +%s) - s ))
  printf '%s\t%d\t%d\t%s\t%d\n' "$name" "$w" "$ranks" \
    "$(python3 -c "print(round($w*$ranks/60,4))")" "$rc" >> "$COST"
  return $rc
}

# OpenFOAM's bashrc references unset variables, so `set -u` is lifted across the source
# and restored immediately after (docs/OPENFOAM.md re-scope note: non-login shell, the
# environment must be sourced in the SAME invocation as the launch).
set +u
# shellcheck disable=SC1090
source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
set -u
command -v checkMesh >/dev/null || { echo "NO OPENFOAM: checkMesh not on PATH"; exit 1; }

for n in 3 2 1; do
  C="$RUNS/L${n}_ugrid"
  UG="$MESH/wing_strct.${n}.lb8.ugrid"
  MB="$MESH/wing_strct.${n}.mapbc"
  [ -f "$UG" ] || { echo "MISSING $UG"; exit 1; }
  [ -f "$MB" ] || { echo "MISSING $MB"; exit 1; }
  # Rule 4 guard: refuse a case directory that already exists.
  [ -e "$C" ] && { echo "REFUSING: $C already exists (guard)"; exit 1; }
  mkdir -p "$C/system"

  # ALL THREE dictionaries.  checkMesh builds an fvMesh; the prior driver in this family
  # wrote only controlDict and checkMesh aborted with
  #   cannot find file ".../system/fvSchemes"
  # -- preserved at verification/runs/RUNG1_M6_runs/M0_ATTEMPT1_ABORTED_missing_fvSchemes/.
  printf 'FoamFile{version 2.0;format ascii;class dictionary;object controlDict;}\napplication none;\nstartFrom startTime;\nstartTime 0;\nstopAt endTime;\nendTime 1;\ndeltaT 1;\nwriteControl timeStep;\nwriteInterval 1;\n' > "$C/system/controlDict"
  printf 'FoamFile{version 2.0;format ascii;class dictionary;object fvSchemes;}\nddtSchemes{default steadyState;}\ngradSchemes{default Gauss linear;}\ndivSchemes{default none;}\nlaplacianSchemes{default Gauss linear corrected;}\nsnGradSchemes{default corrected;}\n' > "$C/system/fvSchemes"
  printf 'FoamFile{version 2.0;format ascii;class dictionary;object fvSolution;}\nsolvers{}\n' > "$C/system/fvSolution"

  timed "ugrid_to_foam_L${n}" 1 -- timeout 360 nice -n 15 \
      python3 "$CONV" "$UG" "$MB" "$C" > "$C/log.ugrid_to_foam" 2>&1 \
      || { echo "CONVERT FAILED L${n} (see $C/log.ugrid_to_foam)"; continue; }

  ( cd "$C" && timed "checkMesh_L${n}" 1 -- timeout 360 nice -n 15 \
      checkMesh > log.checkMesh 2>&1 )
done

printf 'TOTAL\t%d\t1\t%s\t0\n' "$(( $(date +%s) - t0 ))" \
  "$(python3 -c "print(round(($(date +%s)-$t0)/60,4))")" >> "$COST"
echo "M1 RE-IMPORT COMPLETE"
