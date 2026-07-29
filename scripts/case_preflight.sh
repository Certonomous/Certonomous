#!/usr/bin/env bash
# case_preflight.sh -- executable checks that must pass before any OpenFOAM or
# DAFoam case is launched.
#
#   ./case_preflight.sh <case_dir> [--model SA|SST|kEpsilon|laminar] [--quiet]
#   exit 0 = clear to launch, exit 1 = do not launch
#
# WHY THIS EXISTS (D11). Every check below corresponds to a lesson this project
# had already WRITTEN DOWN and then walked into anyway. The stale-processor trap
# was documented after Ladder A1 lost a run to it; the supervisor hit the exact
# same trap debugging B3 several hours later. A prose lesson did not prevent the
# repeat. An executable check does.
#
# Every future lesson of this class ships as a line in here, not a paragraph in
# LESSONS.md.
set -u

CASE="${1:-.}"
MODEL=""
QUIET=0
shift || true
while [ $# -gt 0 ]; do
    case "$1" in
        --model) MODEL="${2:-}"; shift 2 ;;
        --quiet) QUIET=1; shift ;;
        *) shift ;;
    esac
done

fail=0
note() { [ "$QUIET" = "1" ] || echo "$@"; }
bad()  { echo "  FAIL: $*"; fail=1; }
ok()   { note "  ok:   $*"; }

[ -d "$CASE" ] || { echo "FAIL: case dir not found: $CASE"; exit 1; }
cd "$CASE" || exit 1
note "preflight: $(pwd)"

# ---------------------------------------------------------------------------
# 1. Stale decomposition. THE trap: processor* dirs copied along with a case
#    still hold the PREVIOUS run's fields. A model swap then fails with
#    "cannot open file / unexpected class name" that points nowhere useful,
#    or the solver silently reads the wrong state.
# ---------------------------------------------------------------------------
if ls -d processor* >/dev/null 2>&1; then
    nproc_dirs=$(ls -d processor* 2>/dev/null | wc -l)
    # Any field in 0/ that is missing from processor0/0/ means stale decomposition.
    stale=0
    if [ -d processor0/0 ]; then
        for f in 0/*; do
            b=$(basename "$f")
            case "$b" in uniform|*.orig) continue ;; esac
            [ -e "processor0/0/$b" ] || { bad "processor dirs are STALE -- 0/$b has no counterpart in processor0/0/. Run: rm -rf processor*"; stale=1; break; }
        done
    else
        bad "processor* dirs exist but processor0/0 does not -- inconsistent decomposition. Run: rm -rf processor*"
        stale=1
    fi
    [ "$stale" = "0" ] && ok "decomposition consistent ($nproc_dirs processor dirs)"
else
    ok "no processor dirs (will decompose fresh)"
fi

# ---------------------------------------------------------------------------
# 2. Turbulence model vs fields actually present. SA needs nuTilda; SST/kOmega
#    need k and omega; kEpsilon needs k and epsilon. Swapping the model without
#    creating its transported variable is a silent setup error that surfaces
#    much later as a segfault.
# ---------------------------------------------------------------------------
TP=constant/turbulenceProperties
if [ -z "$MODEL" ] && [ -f "$TP" ]; then
    if grep -qa "simulationType[[:space:]]*laminar" "$TP"; then
        MODEL=laminar
    else
        MODEL=$(grep -aE "RASModel|LESModel" "$TP" | head -1 | awk '{print $2}' | tr -d ';')
    fi
fi
note "  model: ${MODEL:-<undetermined>}"

need_fields() {
    for f in "$@"; do
        if [ -f "0/$f" ] || [ -f "0.orig/$f" ]; then ok "field 0/$f present"
        else bad "model $MODEL requires 0/$f and it is MISSING"; fi
    done
}
case "$MODEL" in
    SpalartAllmaras|SA)                 need_fields nuTilda nut ;;
    kOmegaSST|kOmega|SST|kOmegaSSTLM)   need_fields k omega nut ;;
    kEpsilon|realizableKE|LienCubicKE)  need_fields k epsilon nut ;;
    LRR|SSG|EBRSM|*RSTM*)               need_fields R k epsilon ;;
    laminar)                            ok "laminar -- no turbulence fields required" ;;
    "")                                 note "  (model undetermined; skipping field check)" ;;
    *)                                  note "  (model $MODEL not in table; skipping field check)" ;;
esac

# ---------------------------------------------------------------------------
# 3. Field headers parse. A hand-written or sed-mangled header produces
#    "unexpected class name" at solver start, after the queue wait.
# ---------------------------------------------------------------------------
for f in 0/*; do
    [ -f "$f" ] || continue
    case "$(basename "$f")" in uniform) continue ;; esac
    grep -qa "FoamFile" "$f"        || { bad "$f has no FoamFile header"; continue; }
    grep -qa "class[[:space:]]" "$f" || { bad "$f header has no class entry"; continue; }
    grep -qa "object[[:space:]]" "$f" || { bad "$f header has no object entry"; continue; }
    obj=$(grep -a "object" "$f" | head -1 | awk '{print $2}' | tr -d ';')
    [ "$obj" = "$(basename "$f")" ] || bad "$f declares object '$obj' -- must match the filename"
done
ok "field headers parsed"

# ---------------------------------------------------------------------------
# 4. Boundary patches in 0/ match the mesh. A renamed or missing patch is a
#    fatal IO error only after the solver starts.
# ---------------------------------------------------------------------------
B=constant/polyMesh/boundary
if [ -f "$B" ]; then
    mesh_patches=$(awk '/^\(/{f=1;next} /^\)/{f=0} f && /^[[:space:]]+[A-Za-z_][A-Za-z0-9_]*$/{gsub(/[[:space:]]/,"");print}' "$B" | sort -u)
    npatch=$(echo "$mesh_patches" | grep -c . || true)
    for f in 0/*; do
        [ -f "$f" ] || continue
        grep -qa "boundaryField" "$f" || continue
        for p in $mesh_patches; do
            grep -qa "^[[:space:]]*$p" "$f" || grep -qa "\"\.\*\"\|\".*\"" "$f" || bad "$f has no entry for mesh patch '$p'"
        done
    done
    ok "boundary patches checked against mesh ($npatch patches)"
else
    note "  (no polyMesh/boundary yet -- mesh not generated, skipping patch check)"
fi

# ---------------------------------------------------------------------------
# 5. Disk and memory headroom. This box has been taken down twice by memory
#    exhaustion; a case that cannot possibly fit should not start.
# ---------------------------------------------------------------------------
avail_gb=$(awk '/MemAvailable/ {printf "%.1f", $2/1048576}' /proc/meminfo)
disk_gb=$(df -BG --output=avail . | tail -1 | tr -dc '0-9')
awk -v m="$avail_gb" 'BEGIN{exit !(m+0 < 6)}' && bad "MemAvailable ${avail_gb} GB is under the 6 GB floor -- wait, do not launch" || ok "MemAvailable ${avail_gb} GB"
[ "${disk_gb:-0}" -lt 20 ] && bad "free disk ${disk_gb} GB under the 20 GB floor" || ok "free disk ${disk_gb} GB"

if [ "$fail" = "0" ]; then
    note "PREFLIGHT PASS -- clear to launch"
    exit 0
fi
echo "PREFLIGHT FAIL -- do not launch until the above are fixed"
exit 1
