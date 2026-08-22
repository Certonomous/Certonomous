#!/bin/bash
# K0cQ (X2) case builder.  Every case is a twin of an already-solved baseline.
# Changes from the baseline, and NOTHING else:
#   1. RASModel kOmegaSST -> kOmegaSSTQCR
#   2. a top-level libs entry loading the QCR library
#   3. div(qcrStress) Gauss linear, the same scheme the linear stress term uses
#   4. for the Z arms only, kOmegaSSTQCRCoeffs { Ccr1 0; }
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAD="$(cd "$HERE/.." && pwd)"
ROOT="$(cd "$LAD/../../.." && pwd)"          # repo root, for scripts/foam_libs.py
[ -f "$ROOT/scripts/foam_libs.py" ] || { echo "REFUSE: $ROOT/scripts/foam_libs.py is missing"; exit 2; }

# case            baseline                        Ccr1
CASES="
Q_sq_c|$LAD/K0cS_runs/S_SST_c|0.3
Q_sq_f|$LAD/K0cS_runs/S_SST_f|0.3
Q_tl_c|$LAD/K0cX_runs/X_hi_c_SST|0.3
Q_tl_f|$LAD/K0cX_runs/X_hi_f_SST|0.3
Z_sq_c|$LAD/K0cS_runs/S_SST_c|0
Z_tl_c|$LAD/K0cX_runs/X_hi_c_SST|0
"

for line in $CASES; do
    name=${line%%|*}; rest=${line#*|}; base=${rest%%|*}; ccr1=${rest##*|}
    dst="$HERE/$name"

    # D410 guard: never delete a directory that holds committed work.
    if [ -d "$dst" ]; then
        tracked=$(cd "$dst" && git ls-files 2>/dev/null | wc -l | tr -d ' ')
        if [ "${tracked:-0}" -gt 0 ] && [ -z "${K0CQ_ALLOW_DESTRUCTIVE:-}" ]; then
            echo "REFUSE: $dst holds $tracked TRACKED files and this script would delete them."
            exit 2
        fi
        rm -rf "$dst"
    fi

    [ -d "$base" ] || { echo "REFUSE: baseline $base is missing"; exit 2; }
    mkdir -p "$dst"
    cp -r "$base/0.orig" "$dst/0.orig"
    cp -r "$base/0.orig" "$dst/0"
    cp -r "$base/constant" "$dst/constant"
    cp -r "$base/system"   "$dst/system"

    # (1) model
    sed -i 's/RASModel *kOmegaSST;/RASModel        kOmegaSSTQCR;/' "$dst/constant/turbulenceProperties"
    grep -q 'kOmegaSSTQCR' "$dst/constant/turbulenceProperties" || { echo "REFUSE: model swap failed in $name"; exit 2; }

    # (4) coefficient, only where it is not the published default
    if [ "$ccr1" = "0" ]; then
        python3 - "$dst/constant/turbulenceProperties" <<'PY'
import re,sys
p=sys.argv[1]; s=open(p).read()
s2=re.sub(r"(RAS\s*\{)", r"\1\n    kOmegaSSTQCRCoeffs\n    {\n        Ccr1            0;\n    }\n", s, count=1)
assert s2!=s, "could not insert kOmegaSSTQCRCoeffs"
open(p,"w").write(s2)
PY
    fi

    # (2) library.  L-221 / H-7: inserted-with-assert through the shared helper,
    # NEVER a blind `>>` append.  The append this replaced was correct only
    # because these baselines happen to carry no top-level libs entry; against a
    # baseline that does, it silently produces TWO entries -- a duplicate
    # dictionary key, not a longer list -- and the grep that guarded it passes
    # anyway, because grep cannot tell one entry from two.  ensure_libs merges
    # to the union, then RE-READS THE FILE FROM DISK and asserts.
    python3 "$ROOT/scripts/foam_libs.py" ensure "$dst/system/controlDict" \
        libkOmegaSSTQCRTurbulenceModels.so \
        || { echo "REFUSE: libs insert failed in $dst/system/controlDict"; exit 2; }

    # (3) scheme for the QCR stress divergence
    python3 - "$dst/system/fvSchemes" <<'PY'
import sys
p=sys.argv[1]; s=open(p).read()
anchor="    div((nuEff*dev2(T(grad(U))))) Gauss linear;"
assert anchor in s, "anchor scheme not found"
assert "div(qcrStress)" not in s
open(p,"w").write(s.replace(anchor, anchor+"\n    div(qcrStress) Gauss linear;",1))
PY

    et=$(grep -E '^endTime' "$dst/system/controlDict" | awk '{print $2}' | tr -d ';')
    echo "built $name  <- $(basename "$base")  Ccr1=$ccr1  endTime=$et"
    { echo "case=$name"; echo "baseline=$base"; echo "Ccr1=$ccr1"; echo "endTime=$et"; } > "$dst/CASE.txt"
done
echo "all cases built"
