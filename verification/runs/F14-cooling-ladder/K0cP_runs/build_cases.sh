#!/bin/bash
# K0cP builder.  ONE dictionary scalar differs from each baseline: Prt.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAD="$(cd "$HERE/.." && pwd)"
CASES="
P021_sq_c|$LAD/K0cS_runs/S_KE_c|0.21
P021_sq_f|$LAD/K0cS_runs/S_KE_f|0.21
P102_sq_c|$LAD/K0cS_runs/S_KE_c|1.02
P102_sq_f|$LAD/K0cS_runs/S_KE_f|1.02
"
for line in $CASES; do
    name=${line%%|*}; rest=${line#*|}; base=${rest%%|*}; prt=${rest##*|}
    dst="$HERE/$name"
    if [ -d "$dst" ]; then
        tracked=$(cd "$dst" && git ls-files 2>/dev/null | wc -l | tr -d ' ')
        if [ "${tracked:-0}" -gt 0 ] && [ -z "${K0CP_ALLOW_DESTRUCTIVE:-}" ]; then
            echo "REFUSE: $dst holds $tracked TRACKED files"; exit 2
        fi
        rm -rf "$dst"
    fi
    [ -d "$base" ] || { echo "REFUSE: baseline $base missing"; exit 2; }
    mkdir -p "$dst"
    cp -r "$base/0.orig" "$dst/0.orig"; cp -r "$base/0.orig" "$dst/0"
    cp -r "$base/constant" "$dst/constant"; cp -r "$base/system" "$dst/system"
    python3 - "$dst/constant/transportProperties" "$prt" <<'PY'
import re, sys
p, prt = sys.argv[1], sys.argv[2]
s = open(p).read()
m = re.search(r"^(Prt\s+)([\d.eE+-]+);", s, re.M)
assert m, "Prt entry not found"
old = m.group(2)
s2 = s[:m.start()] + m.group(1) + prt + ";" + s[m.end():]
assert s2 != s
open(p, "w").write(s2)
print(f"    Prt {old} -> {prt}")
PY
    { echo "case              $name"; echo "prt_baseline      $base";
      sed -e 's/^case .*/# superseded/' -e "s/^Prt .*/Prt               $prt/" "$base/CASE.txt" \
        | grep -v '^# superseded'; } > "$dst/CASE.txt"
    echo "built $name <- $(basename $base) Prt=$prt"
done
echo "all cases built"
