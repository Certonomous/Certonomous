#!/bin/bash
# K0cR (X3) case builder.  Each case is a twin of an already-solved kEpsilon
# baseline.  The four changes are registered in K0cR_PREREGISTRATION.md 4.1 and
# NONE of them introduces a new number.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAD="$(cd "$HERE/.." && pwd)"

CASES="
R_sq_c|$LAD/K0cS_runs/S_KE_c
R_sq_f|$LAD/K0cS_runs/S_KE_f
R_tl_c|$LAD/K0cX_runs/X_hi_c_KE
R_tl_f|$LAD/K0cX_runs/X_hi_f_KE
"

for line in $CASES; do
    name=${line%%|*}; base=${line#*|}
    dst="$HERE/$name"

    # D410 guard
    if [ -d "$dst" ]; then
        tracked=$(cd "$dst" && git ls-files 2>/dev/null | wc -l | tr -d ' ')
        if [ "${tracked:-0}" -gt 0 ] && [ -z "${K0CR_ALLOW_DESTRUCTIVE:-}" ]; then
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
    sed -i 's/RASModel *kEpsilon;/RASModel        SSG;/' "$dst/constant/turbulenceProperties"
    grep -q 'SSG' "$dst/constant/turbulenceProperties" || { echo "REFUSE: model swap failed in $name"; exit 2; }

    # (2) 0/R, ISOTROPIC from the case's own k seed; boundaryField inherited
    #     from k, which already carries kqRWallFunction on every wall.
    python3 - "$dst" <<'PY'
import os, re, sys
d = sys.argv[1]
src = open(os.path.join(d, "0.orig", "k")).read()
m = re.search(r"internalField\s+uniform\s+([^;]+);", src)
assert m, "cannot read k internalField"
k = float(m.group(1))
rd = repr(2.0 / 3.0 * k)
val = f"({rd} 0 0 {rd} 0 {rd})"
out = src.replace("volScalarField", "volSymmTensorField")
out = re.sub(r"object\s+k;", "object      R;", out)
out = re.sub(r"dimensions\s+\[[^\]]*\];", "dimensions      [0 2 -2 0 0 0 0];", out)
out = re.sub(r"internalField\s+uniform\s+[^;]+;", f"internalField   uniform {val};", out)
assert "volSymmTensorField" in out and "object      R;" in out
for t in ("0.orig", "0"):
    open(os.path.join(d, t, "R"), "w").write(out)
print(f"    R isotropic from k={k:g} -> diag {rd}")
PY

    # (3) schemes: each new entry gets the SAME scheme as its counterpart
    python3 - "$dst/system/fvSchemes" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
a = "    div((nuEff*dev2(T(grad(U))))) Gauss linear;"
b = "    div(phi,epsilon) bounded Gauss limitedLinear 1;"
assert a in s and b in s, "anchor scheme missing"
assert "div(phi,R)" not in s and "div(R)" not in s
s = s.replace(a, a + "\n    div((nu*dev2(T(grad(U))))) Gauss linear;"
                    "\n    div(R)          Gauss linear;", 1)
s = s.replace(b, b + "\n    div(phi,R)      bounded Gauss limitedLinear 1;", 1)
open(p, "w").write(s)
PY

    # (4) solvers/relaxation: R joins the existing selectors, no new number
    python3 - "$dst/system/fvSolution" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
a = '"(U|T|k|omega|epsilon)"'
b = '"(k|omega|epsilon)" 0.4;'
assert a in s and b in s, "fvSolution selectors not found as expected"
s = s.replace(a, '"(U|T|k|omega|epsilon|R)"', 1)
s = s.replace(b, '"(k|omega|epsilon|R)" 0.4;', 1)
open(p, "w").write(s)
PY

    et=$(grep -E '^endTime' "$dst/system/controlDict" | awk '{print $2}' | tr -d ';')
    echo "built $name  <- $(basename "$base")  endTime=$et"
    { echo "case              $name"; echo "ssg_baseline      $base";
      sed -e 's/^case .*/# superseded/' -e 's/^model .*/model             SSG/' "$base/CASE.txt" | grep -v '^# superseded'; } > "$dst/CASE.txt"
done
echo "all cases built"
