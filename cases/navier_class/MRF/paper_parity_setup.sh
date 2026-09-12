#!/bin/bash
# paper_parity_setup.sh -- build a READ-ONLY work copy of each ET8000 level so
# that writeCellCentres/writeCellVolumes can run WITHOUT writing anything into
# the graded run tree (rule-4 age guard: nothing new lands in the graded 8000/).
# constant/ and 8000/ are populated with SYMLINKS to the originals; only C*, V
# are created, and they are created in the WORK time dir.
SRC=/home/ubuntu/Certonomous/verification/runs/navier_class/MRF/R2/ET8000
WRK=/home/ubuntu/Certonomous/verification/runs/navier_class/MRF/R2/PAPER_PARITY/work
source /usr/lib/openfoam/openfoam2606/etc/bashrc || true
set -eo pipefail
for L in coarse medium fine; do
  W=$WRK/$L
  rm -rf "$W"; mkdir -p "$W/constant" "$W/system" "$W/8000"
  for f in "$SRC/$L"/constant/*; do ln -s "$f" "$W/constant/$(basename "$f")"; done
  for f in "$SRC/$L"/8000/*;     do [ -d "$f" ] || ln -s "$f" "$W/8000/$(basename "$f")"; done
  cp "$SRC/$L"/system/fvSchemes "$SRC/$L"/system/fvSolution "$W/system/"
  cat > "$W/system/controlDict" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application     simpleFoam;
startFrom       startTime;
startTime       8000;
stopAt          endTime;
endTime         8000;
deltaT          1;
writeControl    timeStep;
writeInterval   1;
writeFormat     ascii;
writePrecision  10;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
EOF
  ( cd "$W" && postProcess -time 8000 -func writeCellCentres > log.writeCellCentres 2>&1 \
             && postProcess -time 8000 -func writeCellVolumes > log.writeCellVolumes 2>&1 )
  echo "$L: $(ls "$W"/8000 | tr '\n' ' ')"
done

# --- appended 2026-09-12: grad(U) for the turbulence-production figure (Reid Fig. 19).
# turbulenceFields(G) REFUSES under bare postProcess -- it cannot find a registered
# momentum transport model -- so G is built from grad(U) instead, as
#   G = 2 * nut * (S:S),  S = symm(grad U),
# and that definition is printed on the figure rather than implied.
for L in coarse medium fine; do
  ( cd "$WRK/$L" && postProcess -time 8000 -func 'grad(U)' > log.gradU 2>&1 && echo "$L grad(U) ok" )
done
