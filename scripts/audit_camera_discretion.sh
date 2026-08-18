#!/usr/bin/env bash
# audit_camera_discretion.sh -- flag recipe-level disclosure on camera surfaces.
#
# Enforces docs/DEMO_DISCRETION_CHARTER.md. The charter's line is:
#
#     The demo may withhold METHOD. It may never misstate RESULT.
#
# This script looks for the METHOD half only. It flags text that reads as a
# recipe a competitor could follow: internal paths, module and file names,
# library and version specifics, numeric solver settings, mesh construction
# steps, and narration of failed attempts. It never looks at a measured value,
# a band, a tier or a reference identity, and it must never be used to remove
# one.
#
# It is a REVIEW AID, not an auto-edit. Every hit is printed with the rule that
# caught it and why that rule exists, so a human judges it in context. Expect
# false positives: "the two shape groups" is fine, "gradient" is fine, and a
# published reference's identity is required to stay. A clean run is not a
# certificate; a noisy run is not a failure.
#
# Companion to scripts/audit_transcripts.sh, which polices the reuse vocabulary
# and the no-failures-on-camera rule. Run both before filming.
#
#   scripts/audit_camera_discretion.sh              # every camera surface
#   scripts/audit_camera_discretion.sh nasa-hump    # one act
#
# THIS GATE FAILS CLOSED. It already stated its reach -- `0 camera surface(s)
# scanned` -- and then exited 0 anyway, so `audit_camera_discretion.sh
# nasa-humpp` audited nothing and passed. Stating your reach and failing closed
# are different properties and this script had only the first: the number was
# on screen, and nothing downstream, including the exit code, was allowed to
# act on it. So the corpus is now resolved and counted BEFORE it is judged, an
# unusable corpus prints RED and exits 2 with no verdict line at all -- an
# instrument that read nothing has no opinion to offer -- and the reach that
# was already printed now carries its per-source breakdown, so a reader sees
# which of the three camera surfaces contributed zero instead of only the total.
#
# Exit codes:  0 = scanned >=1 surface per requested source        (green)
#              2 = corpus missing, empty, or an act that resolved
#                  no surface at all                              (RED, no verdict)
#
# Hits do NOT change the exit code, and that is deliberate rather than an
# oversight of the same class. Its companion audit_transcripts.sh exits 1 on a
# hit because its rules are hard bans on vocabulary. These rules are not: the
# header above promises false positives, the real corpus flags 16 surface/rule
# combinations today, and every one is a human judgement. An exit code that is
# permanently non-zero is an exit code nobody reads, which is how the reach line
# came to be printed and ignored in the first place. Read the hits.
#
# CONTROL HARNESS. The two paths below are overridable by environment so this
# gate can be pointed at a scratch corpus and shown to fire. Deliberately long,
# script-specific names: a gate that a stray exported `OUT` could silently
# repoint would be a fresh instance of the defect this comment describes.
#
#   CAMERA_AUDIT_ROOT=/scratch/copy bash scripts/audit_camera_discretion.sh
#   CAMERA_AUDIT_OUT=/scratch/empty bash scripts/audit_camera_discretion.sh act
set -u

ROOT=${CAMERA_AUDIT_ROOT:-/home/ubuntu/Certonomous}
OUT=${CAMERA_AUDIT_OUT:-$ROOT/mission-output}

# ---------------------------------------------------------------------------
# The rules. Each is a pattern plus the reason it exists, printed with the hit.
# ---------------------------------------------------------------------------

R_PATH='(/home/|\.\./|\bdemo-output/|\bmission-output/|\bsdk/|\bworkflows/|\bscripts/|\bdocs/|\bchief_engineer\b|\bladder-[ab]\b)'
W_PATH='internal path. Shows the competitor how the lab is laid out, and Katie has banned our own paths on any user-visible surface.'

R_MODULE='([A-Za-z0-9_]+\.(py|json|md|sh|stl|obj|yaml|yml|csv|jsonl|h5|dat)\b|\b[a-z_]+\.[a-z_]+\(\)|\bA[0-9]_[A-Za-z_]+|\bcontrolDict\b|\bfvSchemes\b|\bfvSolution\b|\bsnappyHexMeshDict\b)'
W_MODULE='module or artifact file name. A file name is a map of the internals; nothing on camera needs one.'

R_LIB='\b(DAFoam|dafoam|pyGeo|pygeo|pyOptSparse|pyoptsparse|IDWarp|idwarp|MACH-Aero|OpenFOAM|openfoam|Docker|docker|SNOPT|IPOPT|SLSQP|petsc|PETSc|mpi4py|numpy|scipy|matplotlib|paraview|ParaView|gmsh|CGNS|python[0-9. ]|v?[0-9]+\.[0-9]+\.[0-9]+)\b'
W_LIB='library, toolchain or version. Naming the stack is naming the recipe. The SOLVER may be named on camera (Katie requires it); its supporting toolchain may not.'

R_SETTING='\b(GMRES|ILU|AMG|preconditioner|preconditioned|restart [0-9]|fill level|relaxation factor|under-?relax[a-z]*|CFL [0-9]|Courant [0-9]|residual tolerance|tolerance of [0-9]|[0-9] ?ranks?\b|nCorrectors|nNonOrthogonal|maxIter|max iterations [0-9]|first[- ]order upwind|limitedLinear|linearUpwind|vanLeer|SIMPLE|PIMPLE|PISO|Rhie-?Chow|y\+ ?(of|=|target)|step of [0-9]|step [0-9]e-|[0-9]e-[0-9]+ (tolerance|step))\b'
W_SETTING='numeric solver setting or scheme. This is the recipe itself: the tuning a competitor would otherwise have to buy with their own compute.'

R_MESH='\b(snappyHexMesh|blockMesh|checkMesh|refinement level|refinementSurfaces|addLayers|prism layer[s]? of|layer expansion|castellated|inflation layer|boundary layer cells|cells across|mesh recipe|extrude[sd]? from)\b'
W_MESH='mesh construction recipe. How the grid was built is the most copyable thing in the lab.'

R_ATTEMPT='\b(first attempt|second attempt|third attempt|attempt [0-9]|retr(y|ied|ies)|we tried|tried (first|again|several)|after .{0,20}(diverged|failed|blew up)|diverged|blew up|crashed|did not converge|didn.t converge|failed to converge|first pass failed|initially|at first|originally|turned out to be wrong|the fix was|workaround|hack)\b'
W_ATTEMPT='narration of the sequence of things tried. The order of attempts is method, and a failed attempt on camera also breaks the no-failures rule.'

R_INTERNAL='\b(prompt|system prompt|routing|router|routed to|workflow|sub-?agent|LLM|model context|emit\(|event name|slug|M-[0-9]{4})\b'
W_INTERNAL='prompt or routing internals. How the lab decides what to run is not part of any claim it makes.'

RULES=(PATH MODULE LIB SETTING MESH ATTEMPT INTERNAL)

# ---------------------------------------------------------------------------
# The camera surfaces. Transcripts are what the act actually said; the HTML is
# what the room and the site actually showed.
#
# The closing lab report is the third surface and the easiest one to forget.
# It never lands in mission-output -- it is emitted live and drawn by the
# control room's own script -- so its Abstract, Methods, Uncertainty and Next
# investigations text is lifted straight out of each act's lab_report() call
# below. That Methods block is where recipe-level detail hides most reliably,
# because it reads like documentation rather than narration.
# ---------------------------------------------------------------------------

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

# Pull the four rendered report fields out of every workflow's lab_report()
# call. Source segments, so f-string placeholders survive as written; a
# placeholder is never itself a disclosure, and the surrounding prose is what
# this audit reads.
reports() {
    python3 - "$ROOT" "$WORK" <<'PY' 2>/dev/null
import ast, pathlib, sys
root, work = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
shown = ("abstract", "methods", "uncertainty", "next_investigations")
for path in sorted((root / "sdk" / "workflows").glob("*.py")):
    try:
        src = path.read_text()
        tree = ast.parse(src)
    except Exception:
        continue
    lines = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call)
                and getattr(node.func, "id", "") == "lab_report"):
            continue
        for kw in node.keywords:
            if kw.arg not in shown:
                continue
            seg = ast.get_source_segment(src, kw.value) or ""
            lines.append(f"[{kw.arg}] " + " ".join(seg.split()))
    if not lines:
        continue
    out = work / f"{path.stem}.report"
    out.write_text("\n".join(lines) + "\n")
    print(out)
PY
}

reports > /dev/null

# The three static pages are a fixed, known list rather than a glob, so an
# absent one is an absence this script can name. It used to skip them silently.
# R13 / batch 8 re-point: the two served pages moved to `web/`.  Re-pointed in
# the same commit as the move -- an ABSENT_PAGE here is a real absence this
# script names, so a stale spelling would report the pages missing rather than
# fail, which is the quiet direction.
PAGES=("$ROOT/web/closure.html"
       "$ROOT/web/benchmarks.html"
       "$ROOT/sdk/chief_engineer/control_room.html")

# ---------------------------------------------------------------------------
# Resolve the corpus BEFORE judging it, split by source. The total on its own
# is not enough: 36 surfaces with the closing reports missing and 36 with them
# present print the same number, and the closing report is the surface this
# file's own comment calls the easiest one to forget.
# ---------------------------------------------------------------------------
S_TRANS=(); S_REPORT=(); S_PAGE=()
UNRESOLVED=(); ABSENT_PAGE=(); SILENT_ACT=()
MODE=full

shopt -s nullglob
if [ "$#" -gt 0 ]; then
    MODE=acts
    for a in "$@"; do
        n=0
        for f in "$OUT/$a"/transcript.*; do
            [ -f "$f" ] || continue
            S_TRANS+=("$f"); n=$((n + 1))
        done
        f="$WORK/$(echo "$a" | tr '-' '_').report"
        if [ -f "$f" ]; then S_REPORT+=("$f"); n=$((n + 1)); fi
        [ "$n" -eq 0 ] && UNRESOLVED+=("$a")
    done
else
    for f in "$OUT"/*/transcript.*; do [ -f "$f" ] && S_TRANS+=("$f"); done
    for f in "$WORK"/*.report;      do [ -f "$f" ] && S_REPORT+=("$f"); done
    for f in "${PAGES[@]}"; do
        if [ -f "$f" ]; then S_PAGE+=("$f"); else ABSENT_PAGE+=("$f"); fi
    done
    for d in "$OUT"/*/; do
        t=("$d"transcript.*)
        [ "${#t[@]}" -eq 0 ] && SILENT_ACT+=("$(basename "$d")")
    done
fi
ACTDIRS=("$OUT"/*/)
WORKFLOWS=("$ROOT"/sdk/workflows/*.py)
shopt -u nullglob

ACTNAMES=()
for d in "${ACTDIRS[@]}"; do ACTNAMES+=("$(basename "$d")"); done

SURF=("${S_TRANS[@]}" "${S_REPORT[@]}" "${S_PAGE[@]}")

# How much vocabulary the verdict is entitled to claim it knows. Same method as
# audit_transcripts.sh: alternations plus one, per rule.
terms=0
for rule in "${RULES[@]}"; do
    pat="R_$rule"
    n=$(printf '%s' "${!pat}" | tr -cd '|' | wc -c)
    terms=$((terms + n + 1))
done

label() {
    case "$1" in
        */transcript.*) basename "$(dirname "$1")" ;;
        *.report)       echo "$(basename "$1" .report) closing report" ;;
        *)              basename "$1" ;;
    esac
}

# What the surface actually SHOWS. A transcript is already that. An HTML page is
# not: most of control_room.html is behaviour, and its script, style and comment
# blocks are no more on camera than this script is. They are stripped, with line
# numbers preserved so a hit can still be found in the file. Without this the
# audit drowns in its own source code and stops being read.
#
# KNOWN GAP, stated rather than hidden: stripping the script block also strips
# the template literals the control room renders its own labels from, so any
# fixed English the room draws in JavaScript is NOT audited here. Almost all
# on-camera wording comes from the acts and lands in the transcript or the
# closing report, both of which are covered; room chrome is not. Read
# control_room.html by eye before filming, or extend this function once that
# file is not held by another editor.
rendered() {
    case "$1" in
        *.html) awk '
            /<script/  { s=1 } /<style/ { y=1 }
            /<!--/     { c=1 }
            { line = $0
              if (s || y || c) line = ""
              print line }
            /<\/script>/ { s=0 } /<\/style>/ { y=0 } /-->/ { c=0 }
        ' "$1" ;;
        *) cat "$1" ;;
    esac
}

echo "Camera-discretion audit -- docs/DEMO_DISCRETION_CHARTER.md"
echo "Review aid. Every line below needs a human judgement; false positives are expected."
echo

# --- fail closed -----------------------------------------------------------
# Every arm below prints RED and exits 2 without a verdict. The old script
# printed `0 camera surface(s) scanned, 0 surface/rule combinations flagged`
# and exited 0 for all of them, which reads as a pass to anything that is not
# a human paying attention -- and, on a filming morning, to most humans too.
red() {
    echo "  RED: $1"
    shift
    for l in "$@"; do echo "       $l"; done
    echo
    echo "  No verdict. This gate did not read what it claims to cover and"
    echo "  therefore cannot clear filming."
    exit 2
}

if [ ! -d "$OUT" ]; then
    red "mission-output root does not exist -- $OUT" \
        "Every transcript surface lives under it. Nothing was scanned."
fi
if [ "${#UNRESOLVED[@]}" -gt 0 ]; then
    red "act name(s) resolved no camera surface: ${UNRESOLVED[*]}" \
        "Looked for $OUT/<act>/transcript.* and a closing report from" \
        "sdk/workflows/<act>.py. A misspelt act name lands here." \
        "Act directories that do exist: ${ACTNAMES[*]:-(none)}"
fi
if [ "$MODE" = full ]; then
    # In a full sweep all three sources are claimed as covered, so all three
    # must actually have delivered something. A source that contributed zero
    # is a class of camera surface that went unread under a green verdict.
    [ "${#S_TRANS[@]}" -eq 0 ] && red \
        "no act transcripts under $OUT" \
        "Looked for $OUT/*/transcript.*  (${#ACTDIRS[@]} act director(y/ies) present)"
    [ "${#S_REPORT[@]}" -eq 0 ] && red \
        "no closing lab reports could be extracted" \
        "Looked for lab_report() calls in $ROOT/sdk/workflows/*.py" \
        "(${#WORKFLOWS[@]} workflow file(s) present)." \
        "This is the surface most easily forgotten and it was not read."
    [ "${#ABSENT_PAGE[@]}" -gt 0 ] && red \
        "static camera page(s) absent: ${ABSENT_PAGE[*]}" \
        "These are a fixed list, not a glob. An absent one used to be skipped" \
        "in silence, leaving a page nobody audited under a green verdict."
fi
# Belt and braces: any path that leaves the corpus empty ends here rather than
# in a verdict, including one added later that forgets to check itself.
[ "${#SURF[@]}" -eq 0 ] && red "0 camera surfaces resolved" \
    "ROOT=$ROOT  OUT=$OUT"

hits=0
files=0
for f in "${SURF[@]}"; do
    [ -n "$f" ] || continue
    files=$((files + 1))
    name=$(label "$f")
    printed=0
    for rule in "${RULES[@]}"; do
        pat="R_$rule"; why="W_$rule"
        found=$(rendered "$f" | grep -nEi "${!pat}" 2>/dev/null | cut -c1-160)
        [ -n "$found" ] || continue
        if [ "$printed" -eq 0 ]; then echo "== $name"; printed=1; fi
        count=$(printf '%s\n' "$found" | wc -l)
        echo "  [$rule] $count line(s) -- ${!why}"
        printf '%s\n' "$found" | head -6 | sed 's/^/        /'
        [ "$count" -gt 6 ] && echo "        ... $((count - 6)) more"
        hits=$((hits + 1))
    done
    [ "$printed" -eq 1 ] && echo
done

echo "-----------------------------------------------------------------------"
# The reach travels with the verdict, broken down by source. A bare total reads
# the same whether a whole class of camera surface was covered or missed.
echo "  $files camera surface(s) scanned, $hits surface/rule combinations flagged."
echo "  Reach: ${#S_TRANS[@]} transcript(s) + ${#S_REPORT[@]} closing report(s) + ${#S_PAGE[@]} static page(s)," \
     "x ${#RULES[@]} rules (${terms} terms)."
if [ "${#SILENT_ACT[@]}" -gt 0 ]; then
    echo "  Unread: ${#ACTDIRS[@]} act director(y/ies) present, ${#SILENT_ACT[@]} with no transcript.* --"
    echo "          ${SILENT_ACT[*]}"
fi
echo
echo "  What this audit does NOT check, and must never be used to change:"
echo "    the measured value, its uncertainty band, the fidelity tier chip,"
echo "    what it was compared against and that reference's identity, and"
echo "    whether a gate passed. Those are the claim. They stay."

# Reached only after at least one surface was actually read. See the exit-code
# note in the header for why hits do not change this.
exit 0
