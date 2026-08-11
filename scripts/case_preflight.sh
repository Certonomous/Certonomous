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
NARGS=$#
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

# ---------------------------------------------------------------------------
# VERDICT PLUMBING, AND WHY IT IS NOT JUST `echo` (D11 rank 1, 2026-08-11).
#
# `--quiet` is not one mode among several -- it is the ONLY mode production
# ever uses. `launch_solve.sh` invokes this script exactly one way,
# `"$PF" "$CASE" --quiet`, so anything routed through `note()` is, in
# production, routed to nowhere. The old PASS line was a `note`. The result:
# on every clean launch this gate emitted zero bytes, and zero bytes is also
# what a gate that never ran emits. Those two must never look alike.
#
# So there are now three channels, not two:
#   note()    detail, verbose only          -- may be silent
#   ok()      a check that RAN and passed   -- counted always, printed verbose
#   bad()     a check that RAN and failed   -- counted always, printed ALWAYS
#   say()     the verdict                   -- printed ALWAYS, both modes
# and `fail` became a COUNT rather than a flag so the verdict can state how
# many of the checks that ran came back red.
#
# THE DISTINCTION THIS FILE EXISTS TO DRAW. "I looked and found no problems"
# and "I had nothing to look at" are different facts and now have different
# exit codes. Section 0 below is what makes the second one reachable: before
# this, an empty directory ran every check, matched nothing, tripped nothing,
# and printed `PREFLIGHT PASS`. Reproduced firsthand on 2026-08-11: exit 0,
# zero bytes of output, on a directory containing nothing at all.
fail=0
checks=0
groups=""
note() { [ "$QUIET" = "1" ] || echo "$@"; }
say()  { echo "$@"; }
bad()  { checks=$((checks+1)); fail=$((fail+1)); echo "  FAIL: $*"; }
ok()   { checks=$((checks+1)); note "  ok:   $*"; }
grp()  { groups="${groups:+$groups,}$1"; }

# A refusal that happens BEFORE we have a case to stand in. These cannot use
# the normal verdict tail because there is nothing to report a reach over --
# so each states, in its own words, that nothing was inspected.
nothing_to_inspect() {
    echo "  FAIL: $1"
    say "PREFLIGHT FAIL -- 1 check ran, 1 failed [structure] -- case: ${CASE}"
    say "  NOTHING WAS INSPECTED. This is a refusal, not a clean bill of health:"
    say "  a preflight that cannot find its input has not checked anything."
    exit 1
}

# ---------------------------------------------------------------------------
# 0. STRUCTURE -- does this directory contain a case at all?
#
# Every check from section 1 down is written as "look for a known defect and
# complain if you find it". That shape has exactly one blind spot, and it is
# the expensive one: a directory with nothing in it presents no defect to any
# of them, so all of them pass, and their silence composes into a green. The
# fix is not another defect check. It is to enumerate what a valid case MUST
# CONTAIN and require each element positively -- the one question whose
# answer cannot be faked by absence.
#
# WHAT IS REQUIRED AND HOW THE LIST WAS CHOSEN. Not from taste: the list was
# checked against every case directory named by the 146 completion records in
# demo-output/website/solve_registry. Of the 78 that still exist, 76 carry
# every element below, and the two that do not are the two that were never
# cases (see the exposure note in the commit). A requirement that fires on a
# case this machine has demonstrably run would be a false refusal, and this
# file already learned at line ~120 what those cost.
#
#   constant/, system/          every OpenFOAM application reads both
#   system/controlDict          nothing whatsoever runs without it
#   system/fvSchemes            required to discretise
#   system/fvSolution           required to solve (and section 2b reads it)
#   a field source              0/, 0.orig/, a numeric time dir (a restart --
#                               three F9 cases legitimately have no 0/), or
#                               processor*/ (already decomposed)
# ---------------------------------------------------------------------------
[ "$NARGS" -gt 0 ] || nothing_to_inspect \
    "no case directory given -- refusing to guess at the working directory. Pass the case explicitly."
case "$CASE" in --*) nothing_to_inspect \
    "first argument is the option '$CASE', not a case directory -- refusing to guess at the working directory. Usage: case_preflight.sh <case_dir> [--model M] [--quiet]" ;; esac
[ -e "$CASE" ] || nothing_to_inspect "case path does not exist: $CASE"
[ -d "$CASE" ] || nothing_to_inspect "case path is not a directory: $CASE"
{ [ -r "$CASE" ] && [ -x "$CASE" ]; } || nothing_to_inspect \
    "case dir is not readable/traversable: $CASE"
cd "$CASE" || nothing_to_inspect "cannot enter case dir: $CASE"
CASE_ABS=$(pwd)
note "preflight: $CASE_ABS"
grp structure

if [ -z "$(ls -A 2>/dev/null)" ]; then
    bad "case directory is EMPTY -- there is nothing here to launch. An empty
        directory used to pass this gate silently; it is now a refusal."
else
    ok "case directory is non-empty"
fi

for d in constant system; do
    if [ -d "$d" ]; then ok "required directory $d/ present"
    else bad "required directory $d/ is MISSING -- this is not an OpenFOAM case directory"; fi
done
for f in system/controlDict system/fvSchemes system/fvSolution; do
    if [ -s "$f" ]; then ok "required dictionary $f present and non-empty"
    elif [ -f "$f" ]; then bad "required dictionary $f is EMPTY"
    else bad "required dictionary $f is MISSING"; fi
done

# Field source. Accepts four shapes so a legitimate restart or an already
# decomposed case is not refused; requires that at least one of them exists,
# so a case with no field data anywhere is not.
n0=0
for d in 0 0.orig; do
    [ -d "$d" ] || continue
    for f in "$d"/*; do [ -f "$f" ] && n0=$((n0+1)); done
done
ntime=0
for d in */; do
    b=${d%/}
    case "$b" in ''|*[!0-9.]*) continue ;; esac
    [ -d "$b" ] && ntime=$((ntime+1))
done
nproc0=0
for d in processor*/; do [ -d "$d" ] && nproc0=$((nproc0+1)); done
if [ "$n0" -gt 0 ]; then
    ok "field source: $n0 file(s) in 0/ and/or 0.orig/"
elif { [ -d 0 ] || [ -d 0.orig ]; } && [ "$ntime" -le 1 ] && [ "$nproc0" = "0" ]; then
    bad "0/ and/or 0.orig/ exist but contain NO field files, and there is no
        other time directory or processor* to read fields from"
elif [ "$ntime" -gt 0 ]; then
    ok "field source: $ntime numeric time director(ies) (restart -- no 0/ needed)"
elif [ "$nproc0" -gt 0 ]; then
    ok "field source: $nproc0 processor* director(ies) (already decomposed)"
else
    bad "NO field data of any kind -- no 0/, no 0.orig/, no numeric time
        directory, no processor*. There is nothing here for a solver to read."
fi

# Structure is a precondition, not a peer. If it failed, every check below
# would be reading a directory that is not a case, and their answers would be
# noise dressed as evidence -- so stop here and say which stage stopped.
if [ "$fail" != "0" ]; then
    say "PREFLIGHT FAIL -- $checks checks ran, $fail failed [$groups] -- case: $CASE_ABS"
    say "  STOPPED AT STRUCTURE: this directory is missing elements every case must"
    say "  have, so the model, field, header, patch and resource checks were NOT run."
    say "  Do not launch. A green from the remaining checks would have meant nothing."
    exit 1
fi

# ---------------------------------------------------------------------------
# 1. Stale decomposition. THE trap: processor* dirs copied along with a case
#    still hold the PREVIOUS run's fields. A model swap then fails with
#    "cannot open file / unexpected class name" that points nowhere useful,
#    or the solver silently reads the wrong state.
# ---------------------------------------------------------------------------
grp decomposition
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
grp model/fields
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
    grp fvSolution
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
grp headers
n_hdr=0        # files actually opened and parsed
n_solver=0     # of those, how many are solver fields (the ones that matter)
for f in 0/*; do
    [ -f "$f" ] || continue
    b=$(basename "$f")
    case "$b" in uniform) continue ;; esac
    n_hdr=$((n_hdr+1))
    is_solver_field "$b" && n_solver=$((n_solver+1))
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
# The count is the point. "headers parsed" with no number attached reads
# identically whether it parsed forty files or zero, and zero is exactly the
# state this gate was blind to.
if [ "$n_hdr" -gt 0 ]; then
    ok "solver field headers parsed ($n_hdr file(s) examined in 0/, $n_solver of them solver fields)"
    [ "$n_solver" -gt 0 ] || bad "0/ holds $n_hdr file(s) but NOT ONE is a recognised solver
        field (U, p, T, k, omega, epsilon, nut, nuTilda, R, alpha*, phi, he, rho)
        -- nothing here is a field a solver would read"
elif [ "$ntime" -gt 0 ] || [ "$nproc0" -gt 0 ]; then
    ok "no 0/ to parse; fields come from a time directory or processor* (checked at section 0)"
else
    bad "no field files were examined at all -- there is no 0/ to parse"
fi

# ---------------------------------------------------------------------------
# 4. Boundary patches in 0/ match the mesh. A renamed or missing patch is a
#    fatal IO error only after the solver starts.
# ---------------------------------------------------------------------------
B=constant/polyMesh/boundary
if [ -f "$B" ]; then
    mesh_patches=$(awk '/^\(/{f=1;next} /^\)/{f=0} f && /^[[:space:]]+[A-Za-z_][A-Za-z0-9_]*$/{gsub(/[[:space:]]/,"");print}' "$B" | sort -u)
    npatch=$(echo "$mesh_patches" | grep -c . || true)
    grp patches
    # Same class as the empty case, one level down: if the parse yields zero
    # patch names, the loop below iterates over nothing, complains about
    # nothing, and the old `ok` line reported "checked against mesh (0
    # patches)" -- a green produced by having read nothing. Either the mesh
    # really has no patches (not a runnable mesh) or the parse failed against
    # this file's layout (the check did not run). Both are red.
    if [ "${npatch:-0}" -lt 1 ]; then
        bad "$B exists but NO patch names could be read from it -- either the mesh
        has no boundary patches or this check could not parse the file. Either
        way the patch check did not actually run; it is not a pass."
    fi
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
grp resources
avail_gb=$(awk '/MemAvailable/ {printf "%.1f", $2/1048576}' /proc/meminfo)
disk_gb=$(df -BG --output=avail . | tail -1 | tr -dc '0-9')
awk -v m="$avail_gb" 'BEGIN{exit !(m+0 < 6)}' && bad "MemAvailable ${avail_gb} GB is under the 6 GB floor -- wait, do not launch" || ok "MemAvailable ${avail_gb} GB"
[ "${disk_gb:-0}" -lt 20 ] && bad "free disk ${disk_gb} GB under the 20 GB floor" || ok "free disk ${disk_gb} GB"

# ---------------------------------------------------------------------------
# THE VERDICT, WHICH STATES ITS OWN REACH.
#
# Both outcomes print in both modes -- `--quiet` makes this terse, never
# absent. A gate whose only failure mode is invisible in the one mode
# production uses is not a gate, and this one was: `launch_solve.sh` calls it
# exactly one way, with --quiet, and the PASS line used to be routed through
# `note()` and therefore suppressed. 146 completion records were taken with
# this gate emitting nothing on success.
#
# The counts are the reach. "PASS" alone cannot be told apart from a pass over
# an empty directory; "PASS -- 17 checks ran" can. If that number is small,
# the case gave the gate little to check, and the reader can see that from the
# verdict alone instead of having to re-derive it.
if [ "$fail" = "0" ]; then
    say "PREFLIGHT PASS -- $checks checks ran, 0 failed [$groups] -- case: $CASE_ABS"
    exit 0
fi
say "PREFLIGHT FAIL -- $checks checks ran, $fail failed [$groups] -- case: $CASE_ABS"
say "  Do not launch until the above are fixed."
exit 1
