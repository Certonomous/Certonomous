#!/bin/bash
# Build a kOmegaSSTSparta model-propagation case from an existing
# static-field propagation case (cbfs_prop / ph_prop).
#   setup_sparta_case.sh <src_prop_case> <dst_case> <RTerms> <bDeltaTerms> \
#       <endTime> <writeInterval> [writeInitialCorrections]
# Terms strings use OpenFOAM list syntax, e.g. "( (1 0 0 0.93) )" or "( )".
set -euo pipefail
SRC=$1; DST=$2; RTERMS=$3; BTERMS=$4; ENDT=$5; WINT=$6; WIC=${7:-false}

rm -rf "$DST"
mkdir -p "$DST"
cp -r "$SRC/system" "$DST/system"
mkdir -p "$DST/constant"
cp "$SRC/constant/transportProperties" "$DST/constant/" 2>/dev/null || true
cp -r "$SRC/constant/polyMesh" "$DST/constant/polyMesh"
[ -f "$SRC/system/fvOptions" ] && true
mkdir -p "$DST/0"
for f in U p k omega nut phi V; do
    [ -f "$SRC/0/$f" ] && cp "$SRC/0/$f" "$DST/0/$f"
done

cat > "$DST/constant/turbulenceProperties" <<EOF
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      turbulenceProperties;
}

simulationType RAS;

RAS
{
    RASModel        kOmegaSSTSparta;
    turbulence      on;
    printCoeffs     on;

    kOmegaSSTSpartaCoeffs
    {
        RTerms          $RTERMS;
        bDeltaTerms     $BTERMS;
        writeInitialCorrections $WIC;
    }
}
EOF

# L-221 law: the model named above lives in libspartaTurbulenceModels.so, and this
# script INHERITS the libs entry from the source case rather than writing one. A
# missing entry would leave the stock model loaded, so assert it is present.
grep -q 'libspartaTurbulenceModels' "$DST/system/controlDict" || { echo "libs entry missing (kOmegaSSTSparta will not load): $DST/system/controlDict" >&2; exit 1; }

# endTime / writeInterval
sed -i "s/^endTime .*/endTime         $ENDT;/" "$DST/system/controlDict"
sed -i "s/^writeInterval .*/writeInterval   $WINT;/" "$DST/system/controlDict"
echo "case $DST ready: RTerms=$RTERMS bDeltaTerms=$BTERMS endTime=$ENDT"
