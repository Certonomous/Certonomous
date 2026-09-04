#!/bin/bash
# M6SR BUILD-PATH CHECK -- the controls for Amendment 14 audit item 38, and the standing
# executable evidence for item 39.
#
# WHAT THIS FILE IS.  cases/M6SR/build_m6sr_l1.sh is the sole producer of the L1 mesh --
# Gate A's third level, and with it 88 % of the registered ladder.  Item 38 was the last
# thing between B1 and that mesh:
#
#   ITEM 38  the driver created `$RR/$LEVEL/system` and then MOUNTED AND WORKED IN
#            `$RR/$LEVEL/work`, which had NO `system/`.  Every one of B3's four utilities
#            constructs a `Foam::Time` from `<case>/system/controlDict` first.  MEASURED at
#            the driver's exact mount and -w shape on the pinned digest, with a real plot3d
#            block so the failure is the case files and not a missing input:
#              inner rc 1, `cannot find file "/home/dafoamuser/mount/system/controlDict"`.
#            It FAILS CLOSED at exit 6 and it has never fired: no run root exists.
#            REPAIRED by staging FOUR sha256-pinned dictionaries into `work/system/` --
#            COPIED from a read-only tree, never authored here.  Section 8's SOLE case-file
#            writer is `write_m6sr_case.py` and this driver still writes no case file.
#
#   THE CHAIN, WHICH IS WHY "one missing file" WAS AN UNDER-READING.  Each absence PREEMPTS
#   the next: controlDict -> fvSchemes -> fvSolution -> createPatchDict.  `createPatchDict`
#   IS genuinely needed, and it is what turns `auto0..auto5` into `wing`/`inout`/`sym` --
#   without it the boundary carries ZERO symmetry patches and Section 7 aborts at exit 8.
#   B5 below proves both limbs.
#
#   ITEM 39  an outer `timeout` IS NOT A CAP ON A CONTAINER.  🔴 STRUCK BY QUOTE, 2026-09-04:
#            ~~"REPORTED, NOT REPAIRED;"~~ **REPAIRED** in both drivers -- see
#            `check_m6sr_cap_binds.sh`, which drives the three repaired limbs against real
#            containers.  C6 below is UNCHANGED and still PASSES: it probes a BARE `timeout`
#            directly, never the driver's helper, so what it pins is the PLATFORM FACT that
#            makes the repair necessary, not the driver's old shape.  It keeps the
#            measurement executable rather than only written down.
#
# WHY IT IS COUPLED TO THE DRIVER'S OWN TEXT.  This check does NOT re-type the repaired
# constructs.  It EXTRACTS them from build_m6sr_l1.sh and runs those, so a mutation to the
# driver drives this suite RED.  A suite that re-typed the fix would stay green after the
# driver stopped doing it.
#
# AND EVERY COUPLING ASSERTION READS A COMMENT-STRIPPED VIEW.  That is not style, it is
# forced: the driver's item-38 header block quotes `controlDict`, `fvSchemes`, `fvSolution`
# and `createPatchDict` many times over, so a plain grep for any of them over the whole file
# is satisfied by the SENTENCE DESCRIBING THE FIX rather than by the fix.  C1' measures that
# gap rather than asserting it.
#
# RULE 3, THE PLANTED CONTROL.  Every negative limb is worthless unless the same reader is
# shown reading a success.  C4 runs the driver's OWN extracted B3 command chain in the real
# pinned container and requires inner rc 0 and a Section-7-clean boundary; only that positive
# licenses the refusals beside it.  The image is the REAL PINNED DIGEST, never a mock.
#
# NO SOLVER RUNS HERE, AND NO pyHyp MARCH.  The mesh is a 3x3x3 plot3d block written by this
# file; the containers live seconds.  Nothing is written under verification/runs/.
#
# USAGE:  check_m6sr_build_path.sh [--controls]     (both forms run the same checks)
# EXIT:   0 all checks passed;  1 a check FAILED;  2 the suite REFUSED (plant unseen /
#         preconditions absent) -- a refusal is NEVER reported as a pass.

set +u
set +e

HERE=$(cd -- "$(dirname -- "$0")" && pwd)
DRIVER="$HERE/build_m6sr_l1.sh"
IMG_PINNED=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35
DICT_SRC=/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-coarse/system
WORK=$(mktemp -d -t m6sr_build_check.XXXXXX) || { echo "REFUSE: no scratch dir"; exit 2; }
trap 'rm -rf "$WORK"' EXIT

PASS=0; FAIL=0
ok(){   PASS=$((PASS+1)); printf '  PASS  %s\n' "$1"; }
bad(){  FAIL=$((FAIL+1)); printf '  FAIL  %s\n' "$1"; }
# THE REFUSAL GOES TO stderr, AND THAT IS LOAD-BEARING.  `refuse` inside `$( )` exits only the
# SUBSHELL, and with its message on stdout it would be CAPTURED AS THE VALUE -- a defect that
# has already made three mutations in this campaign die of the wrong cause.  Every extraction
# below is additionally `|| exit 2`.
refuse(){ printf 'REFUSE: %s\n' "$1" >&2; exit 2; }

CONTAINER_S=0

# ---------------------------------------------------------------------------------------
# 0.  PRECONDITIONS.  Each is a REFUSAL, never a skip that prints green.
# ---------------------------------------------------------------------------------------
[ -f "$DRIVER" ] || refuse "the driver under test is ABSENT: $DRIVER"
DOCKER_BIN=$(command -v docker 2>/dev/null)
[ -n "$DOCKER_BIN" ] || refuse "docker does not resolve on PATH"
"$DOCKER_BIN" inspect --format '{{.Id}}' "$IMG_PINNED" >/dev/null 2>&1 \
  || refuse "the PINNED IMAGE $IMG_PINNED is not on this daemon. This suite does NOT fall back to a mock: a mock proves nothing about what a real OpenFOAM binary demands of a real bind mount."
for D in controlDict fvSchemes fvSolution createPatchDict; do
  [ -f "$DICT_SRC/$D" ] || refuse "the pinned mesh-stage dictionary source is ABSENT: $DICT_SRC/$D (read-only tree)"
done

CODE="$WORK/driver_code.sh"
grep -vE '^[[:space:]]*#' "$DRIVER" > "$CODE"
[ -s "$CODE" ] || refuse "stripping comments left no code -- the extraction is broken"

extract_fn(){ awk -v f="$1" '$0 ~ "^"f"\\(\\)\\{" {p=1} p {print} p && /^\}/ {exit}' "$DRIVER"; }
extract_line(){
  local n; n=$(grep -cE "$1" "$CODE")
  [ "$n" = "1" ] || refuse "expected exactly ONE code line matching /$1/ in $DRIVER, found $n. This suite EXECUTES the driver's own line; it will not substitute its own."
  grep -E "$1" "$CODE"
}

# T0.  THE SUITE'S OWN REFUSAL MECHANISM IS PLANTED AND READ BACK BEFORE ANYTHING RESTS ON IT.
_X=$(extract_line '^__M6SR_NO_SUCH_CODE_LINE__' 2>/dev/null); _XRC=$?
{ [ "$_XRC" = "2" ] && [ -z "$_X" ]; } \
  || refuse "THE SUITE'S OWN REFUSAL MECHANISM IS BROKEN: an unmatchable extraction returned rc '$_XRC' and value '${_X:-<empty>}'. It must return rc 2 and NOTHING. A refusal captured as a VALUE is not a refusal."
echo "refusal mechanism: an unmatchable extraction returns rc 2 and no value (planted, read back)"

# ---------------------------------------------------------------------------------------
# C1.  COUPLING -- THE FOUR CALL SITES AND THE FOUR PINS ARE IN THE DRIVER'S **CODE**.
# ---------------------------------------------------------------------------------------
for D in controlDict fvSchemes fvSolution createPatchDict; do
  extract_line "^stage_mesh_dict[[:space:]]+$D[[:space:]]" >/dev/null || exit 2
done
ok "C1 the driver's CODE calls stage_mesh_dict exactly once for each of controlDict, fvSchemes, fvSolution, createPatchDict"

for P in MS_SHA_CONTROLDICT MS_SHA_FVSCHEMES MS_SHA_FVSOLUTION MS_SHA_CREATEPATCHDICT; do
  L=$(extract_line "^$P=[0-9a-f]{64}\$") || exit 2
  eval "$L"
done
ok "C1' the driver's CODE carries four 64-hex pins as PLAIN ASSIGNMENTS -- not \${VAR:-default} forms, so nothing in the environment can move them"

# C1''  THE COMMENT TRAP, MEASURED RATHER THAN ASSERTED.  If the stripped and unstripped
# counts were equal, comment-stripping would be doing nothing and C1 would prove nothing.
RAW_N=$(grep -c 'createPatchDict' "$DRIVER"); CODE_N=$(grep -c 'createPatchDict' "$CODE")
[ "$RAW_N" -gt "$CODE_N" ] \
  && ok "C1'' comment-stripping is load-bearing here: 'createPatchDict' appears $RAW_N times in the driver and only $CODE_N times in its CODE. A whole-file grep would be satisfied by the prose describing the fix" \
  || bad "C1'' comment-stripping changed nothing ($RAW_N vs $CODE_N) -- either the driver has no explanatory comment or the stripper is broken; in both cases C1's coupling is weaker than it looks"

# The mesh-stage source is pinned as a plain assignment too.
SRC_LINE=$(extract_line '^M6SR_MESHSTAGE_SRC=') || exit 2
ok "C1''' the mesh-stage source tree is pinned in CODE: $(echo "$SRC_LINE" | cut -c1-80)"

# ---------------------------------------------------------------------------------------
# C2.  THE DRIVER'S OWN stage_mesh_dict(), EXTRACTED AND RUN.  CLEAN LIMB.
# ---------------------------------------------------------------------------------------
{ extract_line '^sha_of\(\)' || exit 2
  extract_line '^abort\(\)'  || exit 2
  echo; extract_fn stage_mesh_dict; } > "$WORK/fns.sh"
grep -q '^stage_mesh_dict(){' "$WORK/fns.sh" \
  || refuse "could not extract stage_mesh_dict() from $DRIVER -- an empty extraction would make every test below vacuously green"
bash -n "$WORK/fns.sh" || refuse "the extracted functions do not parse"

CD_SHA=$(sha256sum -- "$DICT_SRC/controlDict"     | cut -d' ' -f1)
FS_SHA=$(sha256sum -- "$DICT_SRC/fvSchemes"       | cut -d' ' -f1)
FL_SHA=$(sha256sum -- "$DICT_SRC/fvSolution"      | cut -d' ' -f1)
CP_SHA=$(sha256sum -- "$DICT_SRC/createPatchDict" | cut -d' ' -f1)
{ [ "$CD_SHA" = "$MS_SHA_CONTROLDICT" ] && [ "$FS_SHA" = "$MS_SHA_FVSCHEMES" ] \
  && [ "$FL_SHA" = "$MS_SHA_FVSOLUTION" ] && [ "$CP_SHA" = "$MS_SHA_CREATEPATCHDICT" ]; } \
  || refuse "the driver's four pins do not match the four files on disk at $DICT_SRC. The suite REFUSES rather than test a pin against itself."
ok "C2 the driver's four pins match the four read-only source files, hashed independently here"

stage_into(){        # stage_into <destdir> [<extra shell to run first>]
  local dest="$1" pre="$2"
  mkdir -p "$dest/work/system"
  ( . "$WORK/fns.sh"
    RR="$dest"; LEVEL=.; M6SR_MESHSTAGE_SRC="$DICT_SRC"
    eval "$pre"
    stage_mesh_dict controlDict     "$MS_SHA_CONTROLDICT"
    stage_mesh_dict fvSchemes       "$MS_SHA_FVSCHEMES"
    stage_mesh_dict fvSolution      "$MS_SHA_FVSOLUTION"
    stage_mesh_dict createPatchDict "$MS_SHA_CREATEPATCHDICT" ) 2>&1
}

CLEAN="$WORK/clean"
OUT=$(stage_into "$CLEAN"); RC=$?
N_STAGED=$(ls "$CLEAN/work/system" 2>/dev/null | wc -l)
{ [ "$RC" = "0" ] && [ "$N_STAGED" = "4" ]; } \
  && ok "C2' CLEAN LIMB: the driver's own stage_mesh_dict() staged 4/4 dictionaries, rc 0 -- this positive is what licenses every refusal below" \
  || bad "C2' the clean limb did not stage 4 files cleanly (rc '$RC', $N_STAGED files): ${OUT:0:160}"
BACK=$(sha256sum -- "$CLEAN/work/system/createPatchDict" 2>/dev/null | cut -d' ' -f1)
[ "$BACK" = "$MS_SHA_CREATEPATCHDICT" ] \
  && ok "C2'' and the staged createPatchDict READ BACK FROM DISK hashes the pinned $MS_SHA_CREATEPATCHDICT" \
  || bad "C2'' the staged createPatchDict read back as '${BACK:-ABSENT}'"

# ---------------------------------------------------------------------------------------
# C3.  THE MUTATION BATTERY.  Each mutation is applied to THE DRIVER'S OWN EXTRACTED CODE.
#      HOW each mutant dies is asserted, not merely THAT it died -- two suites in this
#      campaign killed mutants for the wrong reason and only "how" exposed it.
# ---------------------------------------------------------------------------------------
mutate_and_run(){    # mutate_and_run <sed-expr> <destdir>
  local sed_expr="$1" dest="$2"
  sed -E "$sed_expr" "$WORK/fns.sh" > "$WORK/fns_mut.sh"
  cmp -s "$WORK/fns.sh" "$WORK/fns_mut.sh" \
    && { echo "__MUTATION_WAS_A_NO_OP__"; return 99; }
  bash -n "$WORK/fns_mut.sh" || { echo "__MUTANT_DOES_NOT_PARSE__"; return 98; }
  mkdir -p "$dest/work/system"
  ( . "$WORK/fns_mut.sh"
    RR="$dest"; LEVEL=.; M6SR_MESHSTAGE_SRC="$DICT_SRC"
    stage_mesh_dict createPatchDict "$MS_SHA_CREATEPATCHDICT" ) 2>&1
}

# M-A  the pin is altered.  Must die at exit 10 naming the MISMATCH, at the SOURCE hash.
OUT=$( ( . "$WORK/fns.sh"; RR="$WORK/mA"; LEVEL=.; M6SR_MESHSTAGE_SRC="$DICT_SRC"
         mkdir -p "$WORK/mA/work/system"
         stage_mesh_dict createPatchDict 0000000000000000000000000000000000000000000000000000000000000000 ) 2>&1 ); RC=$?
{ [ "$RC" = "10" ] && printf '%s' "$OUT" | grep -q 'MESH-STAGE DICTIONARY MISMATCH'; } \
  && ok "M-A a wrong pin dies at exit $RC on the SOURCE hash comparison: 'MESH-STAGE DICTIONARY MISMATCH'" \
  || bad "M-A expected exit 10 and 'MESH-STAGE DICTIONARY MISMATCH'; got rc '$RC' / '${OUT:0:140}'"

# M-B  the source tree is gone.  Must die at exit 10 naming ABSENT, BEFORE any hashing.
OUT=$( ( . "$WORK/fns.sh"; RR="$WORK/mB"; LEVEL=.; M6SR_MESHSTAGE_SRC="$WORK/no_such_tree"
         mkdir -p "$WORK/mB/work/system"
         stage_mesh_dict createPatchDict "$MS_SHA_CREATEPATCHDICT" ) 2>&1 ); RC=$?
{ [ "$RC" = "10" ] && printf '%s' "$OUT" | grep -q 'is ABSENT'; } \
  && ok "M-B an absent source dies at exit $RC on the EXISTENCE check ('is ABSENT'), not later on an empty hash" \
  || bad "M-B expected exit 10 and 'is ABSENT'; got rc '$RC' / '${OUT:0:140}'"

# M-C  THE COPY IS MADE A NO-OP.  This is the mutation that proves the read-back is not
#      decoration: nothing else in the function would notice.
OUT=$(mutate_and_run 's|^([[:space:]]*)cp -- "\$src" "\$dst"|\1true|' "$WORK/mC"); RC=$?
{ [ "$RC" = "10" ] && printf '%s' "$OUT" | grep -q 'READ BACK FROM DISK'; } \
  && ok "M-C a copy that silently does nothing dies at exit $RC on the DESTINATION READ-BACK -- the only check in the function that could see it" \
  || bad "M-C expected exit 10 and 'READ BACK FROM DISK'; got rc '$RC' / '${OUT:0:140}'"

# M-D  THE READ-BACK IS MADE TO RE-HASH THE **SOURCE**, with the copy still a no-op.  This is
#      the plausible way to write the check wrong, and it is the one that would still print
#      green while nothing had been staged.  The mutant MUST go green -- that is the finding.
#      (An earlier form of this mutation renamed $dst and was a NO-OP as a control, because the
#      copy and the read-back share $dst and simply moved together.  Recorded, not hidden.)
OUT=$(mutate_and_run 's|^([[:space:]]*)cp -- "\$src" "\$dst"|\1true|; s|back=\$\(sha_of "\$dst"\)|back=$(sha_of "$src")|' "$WORK/mD"); RC=$?
{ [ "$RC" = "0" ] && [ ! -f "$WORK/mD/work/system/createPatchDict" ]; } \
  && ok "M-D a read-back that re-hashes the SOURCE returns rc $RC with NOTHING staged -- i.e. it would certify a no-op copy. The driver's read-back hashes \$dst, and M-C shows that is what catches it" \
  || bad "M-D expected the source-hashing mutant to pass vacuously (rc 0, nothing staged); got rc '$RC' / '${OUT:0:140}'"

# M-E  THE READ-BACK ITSELF IS DELETED, with the copy still a no-op.  The suite must go from
#      RED to GREEN -- which is what proves M-C died of the read-back and not of something else.
OUT=$(mutate_and_run 's|^([[:space:]]*)cp -- "\$src" "\$dst"|\1true|; s|^([[:space:]]*)\[ "\$back" = "\$want" \]|\1[ 1 = 1 ]|' "$WORK/mE"); RC=$?
{ [ "$RC" = "0" ] && [ ! -f "$WORK/mE/work/system/createPatchDict" ]; } \
  && ok "M-E with the read-back removed the SAME no-op copy returns rc 0 and stages NOTHING -- so M-C's red was the read-back's doing and nothing else's" \
  || bad "M-E expected rc 0 with no file staged; got rc '$RC' / '${OUT:0:140}'"

# ---------------------------------------------------------------------------------------
# C4.  THE DEFECT AND THE REPAIR, IN THE REAL PINNED CONTAINER, AT THE DRIVER'S EXACT MOUNT.
# ---------------------------------------------------------------------------------------
mk_block(){          # a real 3x3x3 plot3d block, so a failure is the CASE FILES, not the input
  python3 - "$1" <<'PY'
import sys
n=3
pts=[(i,j,k) for k in range(n) for j in range(n) for i in range(n)]
with open(sys.argv[1],"w") as f:
    f.write("1\n%d %d %d\n"%(n,n,n))
    for c in range(3):
        f.write(" ".join("%.6f"%(p[c]*1.0) for p in pts)+"\n")
PY
  chmod 666 "$1"
  # The container writes constant/polyMesh as uid 1002.  Unlinking a file needs write on its
  # DIRECTORY, so the directory is created here, mode 777, or this suite's own cleanup trap
  # cannot remove what the container leaves -- measured: 16 `Permission denied` lines.
  mkdir -p "$(dirname -- "$1")/constant/polyMesh" && chmod 777 "$(dirname -- "$1")/constant" "$(dirname -- "$1")/constant/polyMesh"
}

in_container(){      # in_container <tag> <workdir> <cap_s> <cmd> -> echoes "<outer> <inner>"
  local tag="$1" w="$2" tmo="$3" cmd="$4" n rc inner t0 t1
  n="m6bc_${tag}_$$"; t0=$(date +%s)
  timeout -k 10s "${tmo}"s "$DOCKER_BIN" run --rm --name "$n" -u 1002:1002 \
      -v "$w":/home/dafoamuser/mount -w /home/dafoamuser/mount "$IMG_PINNED" \
      bash -c "set +u; source /home/dafoamuser/dafoam/loadDAFoam.sh >/dev/null 2>&1; $cmd; echo \"WRAPPER_RC=\$?\" > RC_${tag}.txt" \
      > "$WORK/log.$tag" 2>&1
  rc=$?
  "$DOCKER_BIN" rm -f "$n" >/dev/null 2>&1     # THE MECHANISM THAT ACTUALLY BINDS (item 39)
  t1=$(date +%s); CONTAINER_S=$((CONTAINER_S + t1 - t0))
  inner=ABSENT; [ -f "$w/RC_${tag}.txt" ] && inner=$(cut -d= -f2 "$w/RC_${tag}.txt")
  rm -f "$w/RC_${tag}.txt"
  echo "$rc $inner"
}

# THE DRIVER'S OWN B3 COMMAND CHAIN, EXTRACTED -- not a re-typed copy of it.
CHAIN=$(sed -n '/run_in_container mesh/,/renumberMesh -overwrite"/p' "$CODE" \
        | tr '\n' ' ' | sed -E 's/.*"(plot3dToFoam.*renumberMesh -overwrite)".*/\1/' \
        | sed 's/\\ */ /g' | tr -s ' ')
case "$CHAIN" in
  plot3dToFoam*renumberMesh\ -overwrite) : ;;
  *) refuse "could not extract B3's command chain from the driver's CODE (got '${CHAIN:0:80}'). This suite runs the DRIVER'S chain; it will not substitute its own." ;;
esac
CHAIN_T=${CHAIN//volumeMesh.xyz/tiny.xyz}
[ "$CHAIN_T" != "$CHAIN" ] || refuse "the extracted chain does not name volumeMesh.xyz, so the substitution to a test block did nothing"
echo "B3 chain under test, extracted from the driver: $CHAIN_T"

# ---- C4a  THE DEFECT.  work/ with a real block and NO system/ at all.
W1="$WORK/nodicts/work"; mkdir -p "$W1"; chmod -R 777 "$WORK/nodicts"; mk_block "$W1/tiny.xyz"
read -r O1 I1 <<<"$(in_container nodicts "$W1" 120 "$CHAIN_T")"
{ [ "$I1" = "1" ] && grep -q 'cannot find file "/home/dafoamuser/mount/system/controlDict"' "$WORK/log.nodicts"; } \
  && ok "C4a THE DEFECT REPRODUCED at the driver's exact mount: inner rc $I1, 'cannot find file \"/home/dafoamuser/mount/system/controlDict\"' -- and it FAILS CLOSED" \
  || bad "C4a expected inner rc 1 naming system/controlDict; got outer $O1 inner $I1"

# ---- C4b  THE REPAIR.  Same mount, dictionaries staged by the DRIVER'S OWN function.
W2="$WORK/staged/work"
OUT=$(stage_into "$WORK/staged"); RC=$?
[ "$RC" = "0" ] || refuse "the driver's stage_mesh_dict() failed on the C4b tree (rc $RC): ${OUT:0:160}"
chmod -R 777 "$WORK/staged"; chmod 755 "$W2/system"; chmod 644 "$W2"/system/*
mk_block "$W2/tiny.xyz"
read -r O2 I2 <<<"$(in_container staged "$W2" 180 "$CHAIN_T")"
[ "$I2" = "0" ] \
  && ok "C4b THE REPAIR, KNOWN-POSITIVE: the driver's own B3 chain returns inner rc $I2 in the real pinned container with the four staged dictionaries -- this is what licenses C4a and C5a" \
  || bad "C4b the repaired chain did not return inner rc 0 (outer $O2 inner $I2): $(grep -m1 -A1 'FOAM FATAL' "$WORK/log.staged" | tail -1)"

# ---- C4c  SECTION 7's SCREEN, RUN WITH THE DRIVER'S OWN COUNTING LINES.
BND="$W2/constant/polyMesh/boundary"
if [ -f "$BND" ]; then
  eval "$(extract_line '^N_WALL=')"  ; eval "$(extract_line '^N_SYMM=')"
  eval "$(extract_line '^N_PATCH=')"
  { [ "$N_WALL" -eq 1 ] && [ "$N_SYMM" -ge 1 ] && [ "$N_PATCH" -ge 1 ] \
    && ! grep -q 'type[[:space:]]\+empty;' "$BND"; } \
    && ok "C4c and the boundary the repaired chain produced PASSES Section 7's screen, counted by the driver's own lines: wall $N_WALL, symmetry $N_SYMM, patch $N_PATCH, no 'empty'" \
    || bad "C4c Section 7's screen does not pass on the produced boundary: wall $N_WALL, symmetry $N_SYMM, patch $N_PATCH"
else
  bad "C4c the repaired chain produced no constant/polyMesh/boundary"
fi

# ---------------------------------------------------------------------------------------
# C5.  createPatchDict SPECIFICALLY -- THE RESIDUAL THE PRIOR PASS COULD NOT SETTLE, BECAUSE
#      THE MISSING-MESH AND MISSING-fvSchemes ERRORS PREEMPTED THE QUESTION TWICE OVER.
# ---------------------------------------------------------------------------------------
W3="$WORK/three/work"; mkdir -p "$W3/system"; chmod -R 777 "$WORK/three"
cp -- "$DICT_SRC/controlDict" "$DICT_SRC/fvSchemes" "$DICT_SRC/fvSolution" "$W3/system/"
chmod 644 "$W3"/system/*; mk_block "$W3/tiny.xyz"
read -r O3 I3 <<<"$(in_container three "$W3" 120 "$CHAIN_T")"
{ [ "$I3" != "0" ] && grep -q 'cannot find file "/home/dafoamuser/mount/system/createPatchDict"' "$WORK/log.three"; } \
  && ok "C5a createPatchDict IS GENUINELY NEEDED: with the other three present and it absent, inner rc $I3 and 'cannot find file \".../system/createPatchDict\"'. The question is settled by supplying everything ahead of it" \
  || bad "C5a expected a non-zero inner rc naming createPatchDict; got outer $O3 inner $I3"

B3B="$W3/constant/polyMesh/boundary"
if [ -f "$B3B" ]; then
  S_SYMM=$(grep -c 'type[[:space:]]\+symmetry;' "$B3B")
  [ "$S_SYMM" -eq 0 ] \
    && ok "C5b and it is not a formality: without the dict the boundary carries $S_SYMM symmetry patches, so Section 7's screen would abort at exit 8. WITH it (C4c) the same screen reads wall $N_WALL / symmetry $N_SYMM / patch $N_PATCH" \
    || bad "C5b expected 0 symmetry patches without createPatchDict; found $S_SYMM"
else
  bad "C5b no boundary file was produced without createPatchDict, so the claim about the screen cannot be checked"
fi

# ---------------------------------------------------------------------------------------
# C6.  ITEM 39, KEPT EXECUTABLE.  An outer `timeout` does not bound a container it started.
#      🔴 STRUCK BY QUOTE, 2026-09-04: ~~"REPORTED, NOT REPAIRED"~~ -- the DRIVERS are now
#      REPAIRED (`timeout -k` + an unconditional kill + a 124/137 branch).  THIS CHECK IS
#      DELIBERATELY UNCHANGED: it probes a BARE `timeout`, not the driver's helper, so it pins
#      the PLATFORM FACT the repair exists to work around.  It FAILS ONLY if that fact stops
#      reproducing -- in which case the repair's shape must be re-argued from scratch.
# ---------------------------------------------------------------------------------------
N="m6bc_cap_$$"; T0=$(date +%s)
timeout 3s "$DOCKER_BIN" run --rm --name "$N" -u 1002:1002 "$IMG_PINNED" \
    bash -c 'for i in $(seq 1 12); do sleep 1; done' >/dev/null 2>&1
CAPRC=$?; T1=$(date +%s); CAPW=$((T1-T0))
T2=$(date +%s); "$DOCKER_BIN" rm -f "$N" >/dev/null 2>&1; T3=$(date +%s)
CONTAINER_S=$((CONTAINER_S + T3 - T0))
{ [ "$CAPRC" = "124" ] && [ "$CAPW" -ge 10 ]; } \
  && ok "C6 ITEM 39 REPRODUCES: a 3 s \`timeout\` on a 12 s container returned rc $CAPRC after $CAPW WALL SECONDS. The cap REPORTS the overrun; it does not STOP it. Rule 12's 'an overrun stops the run' is not delivered by this mechanism" \
  || bad "C6 item 39 did not reproduce (rc '$CAPRC', wall ${CAPW}s). If a bare timeout now bounds a container, the driver's cap comment must be re-measured before it is believed"
ok "C6' and what DOES end a container is 'docker rm -f' on the recorded name: $((T3-T2)) wall s"

# ---------------------------------------------------------------------------------------
LEFT=$("$DOCKER_BIN" ps -a --filter "name=m6bc_" --format '{{.Names}}' | tr '\n' ' ')
[ -z "$LEFT" ] \
  && ok "SWEEP no container this suite started is left on the daemon" \
  || bad "SWEEP containers left behind: $LEFT"

echo
echo "container wall spent by this suite: ${CONTAINER_S}s at 1 rank ($(python3 -c "print(round($CONTAINER_S/60.0,3))") core-min)"
echo "checks passed: $PASS   FAILED: $FAIL"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
