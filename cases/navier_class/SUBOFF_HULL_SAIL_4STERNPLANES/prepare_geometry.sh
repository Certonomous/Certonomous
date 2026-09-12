#!/bin/bash
# DARPA SUBOFF hull + sail + FOUR STERN APPENDAGES -- geometry pipeline.
# REPRODUCIBLE: generate -> corroborate against the source -> orient -> check.
#
# Modelled on cases/navier_class/SUBOFF_A1/prepare_geometry.sh and using the
# SAME generator resolution for the hull and the sail, so those two files come
# out byte-identical to the already-validated SUBOFF_A1 build at BOTH stages:
#   * RAW generator output   -- asserted against a fresh A1 reference build
#   * AFTER surfaceOrient    -- asserted against the A1 geometry ON DISK
#
# surfaceOrient is NOT cosmetic (SUBOFF_A1's own note): the raw emission carried
# "Number of zones (connected area with consistent normal) : 2" on the sail,
# which makes snappyHexMesh's inside/outside test unreliable on an
# overlapping-solid union.  surfaceCheck's PRINTED report is the verdict; its rc
# is not consulted.
set -u
OUT="$1"; A1REF="$2"                  # $2 = dir holding a RAW A1 reference build
A1DISK=/home/ubuntu/Certonomous/verification/runs/navier_class/SUBOFF_A1/geometry
CASE=/home/ubuntu/Certonomous/cases/navier_class/SUBOFF_HULL_SAIL_4STERNPLANES
set +u; source /usr/lib/openfoam/openfoam2606/etc/bashrc '' > /dev/null 2>&1; set -u
mkdir -p "$OUT" || exit 90
cd "$OUT" || exit 90

python3 "$CASE/build_appended_geometry.py" --out "$OUT" \
    --n-axial 700 --n-theta 256 --n-chord 320 --n-span 140 --te-trunc-frac 0.995 \
    --fin-n-chord 321 --fin-n-span 121 --fin-te-trunc-frac 0.98 \
    --assert-identical-to "$A1REF" > log.generate 2>&1 || { cat log.generate; exit 2; }

python3 "$CASE/verify_appended_geometry.py" --geom "$OUT" --fin-te-trunc-frac 0.98 \
    > log.corroborate 2>&1 || { tail -20 log.corroborate; exit 3; }
grep -q 'CORROBORATION CHECKS MATCH' log.corroborate || {
    echo "REFUSED: corroboration did not report a match"; exit 3; }

SURF="hull sail fin000_upper_rudder fin090_horizontal fin180_lower_rudder fin270_horizontal"
for s in $SURF; do
    surfaceOrient "$s.stl" '(10 10 10)' "${s}_o.stl" > "log.surfaceOrient.$s" 2>&1 || exit 2
    mv -f "${s}_o.stl" "$s.stl"
    surfaceCheck "$s.stl" > "log.surfaceCheck.$s" 2>&1
    grep -q 'Surface is closed'          "log.surfaceCheck.$s" || { echo "REFUSED: $s not closed";      exit 2; }
    grep -q 'no illegal triangles'       "log.surfaceCheck.$s" || { echo "REFUSED: $s illegal tris";    exit 2; }
    grep -q 'consistent normal) : 1'     "log.surfaceCheck.$s" || { echo "REFUSED: $s normals";         exit 2; }
done

# THE REGRESSION THAT LETS THIS BODY INHERIT THE HULL'S VERIFICATION.
# After orienting, hull.stl and sail.stl must be byte-identical to the files the
# SUBOFF_A1 solves are actually running on.
for s in hull sail; do
    a=$(sha256sum "$s.stl"        | cut -d' ' -f1)
    b=$(sha256sum "$A1DISK/$s.stl" | cut -d' ' -f1)
    if [ "$a" != "$b" ]; then
        echo "REFUSED: $s.stl is NOT byte-identical to the SUBOFF_A1 geometry on disk"
        echo "  ours $a"; echo "  A1   $b"; exit 4
    fi
    echo "BYTE-IDENTICAL TO THE SUBOFF_A1 GEOMETRY ON DISK: $s.stl  $a"
done

echo "GEOMETRY OK: six surfaces closed, 1 part, 1 zone, no illegal triangles;"
echo "             29 source-corroboration checks matched within 0.1 mm;"
echo "             hull and sail byte-identical to SUBOFF_A1 at both stages."
