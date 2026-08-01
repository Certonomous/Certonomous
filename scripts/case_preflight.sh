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
    LRR|SSG|*RSTM*)                     need_fields R epsilon ;;
    EBRSM)                              need_fields R epsilon f ;;   # f = elliptic blending fn
    laminar)                            ok "laminar -- no turbulence fields required" ;;
    "")                                 note "  (model undetermined; skipping field check)" ;;
    *)                                  note "  (model $MODEL not in table; skipping field check)" ;;
esac

# ---------------------------------------------------------------------------
# 2b. Every field the model TRANSPORTS needs a solver entry in fvSolution.
#     Having the field in 0/ is not enough. Missing entries produce
#     "Entry '<field>' not found in dictionary system/fvSolution/solvers" and
#     the run dies seconds in, after the queue wait. Cost this project four
#     failed EBRSM launches on 2026-07-29 before it was caught.
# ---------------------------------------------------------------------------
FVS=system/fvSolution
if [ -f "$FVS" ] && [ -n "$MODEL" ]; then
    case "$MODEL" in
        SpalartAllmaras|SA)                transported="nuTilda" ;;
        kOmegaSST|kOmega|SST|kOmegaSSTLM)  transported="k omega" ;;
        kEpsilon|realizableKE|LienCubicKE) transported="k epsilon" ;;
        LRR|SSG|*RSTM*)                    transported="R epsilon" ;;
        EBRSM)                             transported="R epsilon f" ;;
        *)                                 transported="" ;;
    esac
    # The key may sit alone on its line with the brace beneath it (the
    # tutorial layout) or share the line with the whole entry (the compact
    # layout this project's own generated cases use):
    #
    #     "(U|k|omega|epsilon|nuTilda)" { solver smoothSolver; ... }
    #
    # The original pattern anchored the key to end-of-line, so it saw only the
    # first layout and called the second MISSING. That is a false REFUSAL, not
    # a missed failure, and it fired on 2026-08-01 against the Ahmed case in
    # demo-output/website/campaign/W3_runs/kOmegaSST -- a case that had already
    # solved cleanly three times in this tree. A preflight that refuses a case
    # the machine has demonstrably run is worse than no preflight, because the
    # next person reaches for --force.
    #
    # The key must still be a KEY and not any old occurrence of the field name:
    # the search is scoped to the solvers{} block (so relaxationFactors and
    # SIMPLE cannot answer for it), and the key must be followed by end-of-line
    # or an opening brace. residualControl's own
    # `"(k|omega|epsilon|nuTilda)" 1e-4;` is followed by a tolerance, so it
    # cannot satisfy this check even if the scoping were removed.
    solvers_block=$(awk '
        /^[[:space:]]*solvers[[:space:]]*$/ {f=1; next}
        f && /^[[:space:]]*\{/ && d==0 {d=1; next}
        f && d {print; n=gsub(/\{/,"{"); m=gsub(/\}/,"}"); d+=n-m; if(d<=0) exit}
    ' "$FVS")
    for fld in $transported; do
        # match a bare entry or one inside a "(a|b|c)" regex group
        if printf '%s\n' "$solvers_block" | grep -qaE \
             "^[[:space:]]*(\"?\(?[A-Za-z|]*\<$fld\>[A-Za-z|]*\)?\"?)[[:space:]]*(\{.*)?$"; then
            ok "fvSolution has a solver entry covering '$fld'"
        else
            bad "model $MODEL transports '$fld' but fvSolution/solvers has NO entry covering it"
        fi
    done

    # -----------------------------------------------------------------------
    # 2c. residualControl must name a field the model actually transports.
    #     A gate that watches a field the model doesn't carry can never be
    #     satisfied, by construction -- the run isn't slow to converge, it
    #     has no stop criterion at all. Static, catchable before any compute
    #     is spent (see LESSONS.md L-21): D5's three Reynolds-stress-model
    #     duct cases inherited "residualControl { k; omega; }" from an
    #     eddy-viscosity template; none of LRR/SSG/EBRSM transports k or
    #     omega, so two runs ground on toward endTime=500000 for two-plus
    #     hours each, already converged, with no way to ever print their own
    #     convergence statement. This does not require every transported
    #     field to be gated (a case may deliberately gate a subset) -- only
    #     that the block isn't watching a field set with zero overlap with
    #     reality.
    # -----------------------------------------------------------------------
    if grep -qa "residualControl" "$FVS" && [ -n "$transported" ]; then
        rc_block=$(awk '/residualControl/{f=1} f{print} f && /}/{exit}' "$FVS")
        overlap=0
        for fld in $transported; do
            if echo "$rc_block" | grep -qE "\<$fld\>"; then
                overlap=1
            elif [ "$fld" = "R" ] && echo "$rc_block" | grep -qE "\<R(xx|xy|xz|yy|yz|zz)\>"; then
                # R (Reynolds-stress tensor) is often gated per-component in
                # residualControl, since that's the name each component is
                # solved and printed under (Rxx, Rxy, ...), not "R" itself.
                overlap=1
            fi
        done
        if [ "$overlap" = "1" ]; then
            ok "residualControl names at least one field '$MODEL' actually transports ($transported)"
        else
            bad "residualControl names NO field '$MODEL' actually transports (transported: $transported) -- this gate can never fire; the run will grind to endTime with no stop criterion regardless of how converged it is (L-21)"
        fi
    fi
fi

# ---------------------------------------------------------------------------
# 3. Field headers parse. A hand-written or sed-mangled header produces
#    "unexpected class name" at solver start, after the queue wait.
# ---------------------------------------------------------------------------
# A malformed SOLVER field is fatal. An unparseable EXTRA file in 0/ is only a
# warning: benchmark cases legitimately ship reference data alongside the solver
# fields (DNS/LES targets such as U_LES, k_LES, tauij_LES) which the solver never
# reads and which are not always in OpenFOAM field format. Failing on those was a
# false positive that would have blocked a legitimate launch.
is_solver_field() {
    case "$1" in
        U|p|p_rgh|T|k|omega|epsilon|nut|nuTilda|R|alpha*|phi|he|rho) return 0 ;;
        *) return 1 ;;
    esac
}
for f in 0/*; do
    [ -f "$f" ] || continue
    b=$(basename "$f")
    case "$b" in uniform) continue ;; esac
    problem=""
    grep -qa "FoamFile" "$f"          || problem="no FoamFile header"
    [ -z "$problem" ] && { grep -qa "class[[:space:]]"  "$f" || problem="header has no class entry"; }
    [ -z "$problem" ] && { grep -qa "object[[:space:]]" "$f" || problem="header has no object entry"; }
    if [ -z "$problem" ]; then
        obj=$(grep -a "object" "$f" | head -1 | awk '{print $2}' | tr -d ';')
        [ "$obj" = "$b" ] || problem="declares object '$obj' -- must match the filename"
    fi
    if [ -n "$problem" ]; then
        if is_solver_field "$b"; then bad "$f $problem"
        else note "  warn: $f $problem (not a solver field -- reference data, ignored)"; fi
    fi
done
ok "solver field headers parsed"

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
