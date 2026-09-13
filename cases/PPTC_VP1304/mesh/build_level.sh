#!/bin/bash
# PPTC VP1304 -- build ONE family level from the admitted CAD tessellation.
#
#   build_level.sh <STL> <CASEDIR> <RATIO> <MESH_RANKS> <LEVELNAME>
#
# Meshing is NOT a case: Sanaa's run-rules item 19 ("the runner is the only thing that
# launches") governs SOLVER launches.  The solve that follows this script IS queued.
#
# Every rc is captured and checked INSIDE this script.  `set -e` is NOT used, because a
# silent early exit is indistinguishable from a stage that never ran; each stage is checked
# explicitly and the script says which one failed.
set -u
STL="$1"; CASE="$2"; RATIO="$3"; RANKS="$4"; LEVEL="$5"
REPO=/home/ubuntu/Certonomous
MESH="$REPO/cases/PPTC_VP1304/mesh"

step() { echo; echo "=== [$(date -u +%H:%M:%SZ)] $* ==="; }
die()  { echo "BUILD FAILED at: $*"; echo "BUILD_RC=1 stage=$*" >> "$CASE/BUILD_STATUS"; exit 1; }

# OpenFOAM's own bashrc reads unset variables (etc/bashrc:184 WM_PROJECT_DIR), so `set -u`
# aborts the SOURCE, not the solver -- and the abort message goes wherever stderr is
# pointing, which on a detached launch is a file nobody reads. Nounset is lifted for the
# source and restored immediately, and the result is CHECKED rather than assumed.
# AND `set --` FIRST. openfoam2606/etc/bashrc:204 forwards "$@" to etc/config.sh/setup,
# which puts it in FOAM_SETTINGS and evaluates it. Sourced from a script, "$@" is THE
# CALLING SCRIPT'S OWN ARGUMENTS -- so the first argument gets EXECUTED. Measured here:
# the STL path was run as a shell script, 140,000 lines of "vertex: command not found".
# It does not fail loudly; it runs your argument. The args are already saved in named
# variables above, so clearing the positional parameters costs nothing.
set --
set +u
source /usr/lib/openfoam/openfoam2606/etc/bashrc
ENV_RC=$?
set -u
[ $ENV_RC -eq 0 ] && [ -n "${WM_PROJECT_DIR:-}" ] || die "openfoam bashrc (rc=$ENV_RC)"

mkdir -p "$CASE" || die "mkdir case"
: > "$CASE/BUILD_STATUS"
echo "stl=$STL ratio=$RATIO ranks=$RANKS level=$LEVEL start=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    >> "$CASE/BUILD_STATUS"

# --- 1. THE TESSELLATION GATE, PER LEVEL AND PER PATCH ---------------------------------
# Registered in MESH_PIPELINE_RECORD.md ADDENDUM B.4: the family is authorised by this check
# run against the PRODUCED STL, not by a probe and not by a prediction.  It exits 2 rather
# than warning.  Its verdict is recorded here whatever it is.
step "tessellation adequacy -- the produced STL, per level per patch"
python3 "$MESH/check_tessellation_adequacy.py" --stl "$STL" 2>&1 | tee "$CASE/log.tessGate"
TESS_RC=${PIPESTATUS[0]}
echo "tess_gate_rc=$TESS_RC" >> "$CASE/BUILD_STATUS"

# --- 2. patch split, scaled to metres by make_stl.py's registered 1e-3 ------------------
step "patch split -- five registered patches (amendment 2)"
mkdir -p "$CASE/constant/triSurface" || die "mkdir triSurface"
python3 "$MESH/make_stl.py" --in "$STL" --outdir "$CASE/constant/triSurface" \
    > "$CASE/log.makeSTL" 2>&1 || die "make_stl.py (see log.makeSTL)"
tail -20 "$CASE/log.makeSTL"

# --- 3. background sector mesh ---------------------------------------------------------
# MESHING-ONLY dictionaries.  blockMesh, snappyHexMesh, topoSet and checkMesh all refuse
# without a system/controlDict, and the SOLVER's controlDict does not exist yet -- it is
# written by make_case.py AFTER the mesh, because its rank count and endTime depend on the
# cell count this stage produces.  These three are overwritten by make_case.py and none of
# them reaches the solver.
step "meshing-only dictionaries (overwritten by make_case.py after the mesh exists)"
mkdir -p "$CASE/system"
cat > "$CASE/system/controlDict" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application     blockMesh;
startFrom       startTime;  startTime 0;
stopAt          endTime;    endTime   1;
deltaT          1;
writeControl    timeStep;   writeInterval 1;
writeFormat     ascii;      writePrecision 8;
timeFormat      general;    runTimeModifiable false;
EOF
cat > "$CASE/system/fvSchemes" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
gradSchemes { default Gauss linear; }
divSchemes { default none; }
laplacianSchemes { default Gauss linear corrected; }
EOF
cat > "$CASE/system/fvSolution" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers {}
EOF

step "background sector blockMesh, family ratio $RATIO"
python3 "$MESH/make_blockmesh.py" --case "$CASE" --ratio "$RATIO" \
    > "$CASE/log.makeBlockMesh" 2>&1 || die "make_blockmesh.py"
( cd "$CASE" && blockMesh > log.blockMesh 2>&1 ) || die "blockMesh (see log.blockMesh)"
grep -q "^End" "$CASE/log.blockMesh" || die "blockMesh wrote no End line"

# --- 4. feature edges ------------------------------------------------------------------
# REGISTERED, MESH_PIPELINE_RECORD ADDENDUM E.3: the CAD carries ONE root-to-tip curve per
# blade and the smp'11 sheet says the trailing edge is sharp, so THE LEADING EDGE HAS NO CAD
# EDGE and surfaceFeatureExtract cannot extract it on any tessellation at any includedAngle.
# LE resolution in this family comes from SURFACE REFINEMENT LEVEL ALONE.  Stated here so no
# reader of the dictionary infers otherwise.
step "surfaceFeatureExtract -- TE and tip edges only; the LE has no CAD edge and cannot be extracted"
cat > "$CASE/system/surfaceFeatureExtractDict" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object surfaceFeatureExtractDict; }
blades.stl         { extractionMethod extractFromSurface; includedAngle 150;
                     subsetFeatures { nonManifoldEdges no; openEdges yes; } writeObj no; }
hub.stl            { extractionMethod extractFromSurface; includedAngle 150;
                     subsetFeatures { nonManifoldEdges no; openEdges yes; } writeObj no; }
cap.stl            { extractionMethod extractFromSurface; includedAngle 150;
                     subsetFeatures { nonManifoldEdges no; openEdges yes; } writeObj no; }
shaft.stl          { extractionMethod extractFromSurface; includedAngle 150;
                     subsetFeatures { nonManifoldEdges no; openEdges yes; } writeObj no; }
shaftExtension.stl { extractionMethod extractFromSurface; includedAngle 150;
                     subsetFeatures { nonManifoldEdges no; openEdges yes; } writeObj no; }
EOF
( cd "$CASE" && surfaceFeatureExtract > log.surfaceFeatureExtract 2>&1 ) \
    || die "surfaceFeatureExtract"
for p in blades hub cap shaft shaftExtension; do
    [ -s "$CASE/constant/triSurface/$p.eMesh" ] || die "no $p.eMesh produced"
done

# --- 5. snappyHexMesh ------------------------------------------------------------------
step "snappyHexMeshDict, family ratio $RATIO"
python3 "$MESH/make_snappy.py" --case "$CASE" --ratio "$RATIO" \
    > "$CASE/log.makeSnappy" 2>&1 || die "make_snappy.py"
tail -12 "$CASE/log.makeSnappy"

step "snappyHexMesh on $RANKS ranks"
cat > "$CASE/system/decomposeParDict" <<EOF
FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
numberOfSubdomains $RANKS;
method          scotch;
EOF
# stdbuf -oL: a BLOCK-buffered log makes a slow phase look identical to a hang, and this
# lane wasted minutes on exactly that ambiguity. Line-buffered, the phase is always visible.
#
# RANKS=1 takes the SERIAL path, and that is not a formality. Parallel snappyHexMesh
# rebalances whenever the load imbalance exceeds maxLoadUnbalance, and every rebalance makes
# every rank rebuild its search structures over a multi-million-triangle surface. While the
# mesh is still small -- tens of thousands of cells through the feature-refinement
# iterations -- that cost dwarfs the refinement itself. Serial pays none of it.
if [ "$RANKS" = "1" ]; then
    ( cd "$CASE" && stdbuf -oL snappyHexMesh -overwrite > log.snappyHexMesh 2>&1 )
    SNAPPY_RC=$?
else
( cd "$CASE" && decomposePar -force > log.decomposePar.mesh 2>&1 ) || die "decomposePar (mesh)"
( cd "$CASE" && stdbuf -oL mpirun -np "$RANKS" snappyHexMesh -overwrite -parallel \
    > log.snappyHexMesh 2>&1 )
SNAPPY_RC=$?
fi
echo "snappy_rc=$SNAPPY_RC" >> "$CASE/BUILD_STATUS"
[ $SNAPPY_RC -eq 0 ] || die "snappyHexMesh rc=$SNAPPY_RC (see log.snappyHexMesh)"
grep -q "^End" "$CASE/log.snappyHexMesh" || die "snappyHexMesh wrote no End line"

if [ "$RANKS" != "1" ]; then
    ( cd "$CASE" && reconstructParMesh -constant > log.reconstructParMesh 2>&1 ) \
        || die "reconstructParMesh"
    rm -rf "$CASE"/processor*
fi

# --- 6. the MRF cellZone, from the REGISTERED cylinder of section 6.2 -------------------
step "topoSet -- MRF cellZone (1.3 D diameter, +-0.5 D axial)"
( cd "$CASE" && topoSet > log.topoSet 2>&1 ) || die "topoSet (see log.topoSet)"
grep -q "^End" "$CASE/log.topoSet" || die "topoSet wrote no End line"

# --- 7. checkMesh, with the per-cell fields the volume-growth gate needs ----------------
step "checkMesh -allGeometry -allTopology -writeAllFields"
( cd "$CASE" && checkMesh -allGeometry -allTopology -writeAllFields > log.checkMesh 2>&1 )
grep -q "^End" "$CASE/log.checkMesh" || die "checkMesh wrote no End line"

# --- 8. birth certificate, every gate with its measured value ---------------------------
step "BIRTH CERTIFICATE -- pre-registration section 6.5"
python3 "$MESH/birth_certificate.py" --case "$CASE" --level "$LEVEL" --ratio "$RATIO" \
    2>&1 | tee "$CASE/BIRTH_CERTIFICATE.txt"
BC_RC=${PIPESTATUS[0]}
echo "birth_certificate_rc=$BC_RC" >> "$CASE/BUILD_STATUS"
echo "BUILD_RC=0 end=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$CASE/BUILD_STATUS"
echo
echo "MESH BUILT. birth certificate rc=$BC_RC (0 admissible, 3 a gate failed, 2 refused)"
exit 0
