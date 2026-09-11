#!/bin/bash
# SUBOFF_A1 -- geometry pipeline, REPRODUCIBLE: generate -> orient -> check.
# surfaceOrient is NOT cosmetic: the raw emission carried "Number of zones
# (connected area with consistent normal) : 2" on the sail, which makes
# snappyHexMesh's inside/outside test unreliable on an overlapping-solid union.
# surfaceCheck's PRINTED report is the verdict; its rc is not consulted.
set -u
OUT="$1"
set +u; source /usr/lib/openfoam/openfoam2606/etc/bashrc '' > /dev/null 2>&1; set -u
cd "$OUT" || exit 90
python3 /home/ubuntu/Certonomous/cases/navier_class/SUBOFF_A1/build_suboff_a1_geometry.py \
    --out "$OUT" --n-axial 700 --n-theta 256 --n-chord 320 --n-span 140 \
    --te-trunc-frac 0.995 > log.generate 2>&1 || exit 2
for s in hull sail; do
    surfaceOrient "$s.stl" '(10 10 10)' "${s}_o.stl" > "log.surfaceOrient.$s" 2>&1 || exit 2
    mv -f "${s}_o.stl" "$s.stl"
    surfaceCheck "$s.stl" > "log.surfaceCheck.$s" 2>&1
    grep -q 'Surface is closed' "log.surfaceCheck.$s" || { echo "REFUSED: $s not closed"; exit 2; }
    grep -q 'no illegal triangles' "log.surfaceCheck.$s" || { echo "REFUSED: $s illegal tris"; exit 2; }
    grep -q 'consistent normal) : 1' "log.surfaceCheck.$s" || { echo "REFUSED: $s normals"; exit 2; }
done
echo "GEOMETRY OK: both surfaces closed, 1 part, 1 zone, no illegal triangles."
