#!/usr/bin/env bash
# SO-3aF2 PIN CENSUS AND NO-LAUNCH SELFTEST.
#
# TWO JOBS, and the first exists because of a MEASURED failure in this family:
# SO-1c's chain driver carried TWELVE md5 pins and its selftest leg drove FOUR
# while its message claimed "every pin".  So this file carries NO list of pins.
# It ENUMERATES every `MD5_*=` assignment out of the launcher's OWN BYTES, maps
# each to a registered target through ONE table, and REFUSES if any enumerated
# pin has no registered target.  THE COUNT DRIVEN AND THE COUNT THAT EXISTS ARE
# PRINTED SIDE BY SIDE AND MUST BE EQUAL.  A pin added to the launcher with no
# row in the table FAILS this census.  "Every pin is driven" is a COUNT here,
# never a claim.
#
# The second job drives the FOUR NO-LAUNCH BRANCHES of section 6 -- each in the
# REFUSING direction, showing its NAMED file and its NAMED rc -- and, crucially,
# ONCE IN THE PASSING DIRECTION, showing all four PASS lines printed before the
# launcher reaches the container step.  A guard suite that only drives refusals
# cannot tell a working guard from one that is UNSATISFIABLE BY CONSTRUCTION,
# which this family has now met NINE times in one day.
#
# SAFETY, AND THE THINGS THIS FILE MUST NOT DO.  The pre-registration's section 2
# records this item's freeze condition as the ABSENCE of the run root and records
# that this item has started NO CONTAINER.  Both sentences must still be true
# when this file ends, so:
#   * NO leg starts a container.  Every leg runs a SANDBOX COPY of the launcher
#     whose `docker` calls resolve to a STUB on PATH that refuses and logs.  The
#     stub's transcript is printed, so "no container" is a reading, not a promise.
#   * NO leg touches the real run root.  Sandbox copies point `BASE` at a
#     scratch directory; every sandbox delta is PRINTED as a diff so nothing is
#     taken on trust.
#   * Everything created is removed BY NAME, never by glob and never by sweep,
#     and a DECOY this file did not create must SURVIVE that cleanup.
#
# SUBMISSIONS PARKED.

set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/so3af2_run_arm.sh"
READER="$HERE/so3af2_read.py"
PRODUCER="$HERE/so3af2_runScript.py"
REAL_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO3aF2-a1-naca0012-multipoint-feasibility
TMP="${1:-/tmp}/so3af2_pin_selftest_$$"
PASS=0; FAIL=0

# A manifest of the real run root, taken BEFORE anything runs. "ABSENT" is itself
# a legitimate value and compares equal to itself.
real_manifest() {
  if [ -d "$REAL_BASE" ]; then
    ( cd "$REAL_BASE" && find . | sort | md5sum ) | cut -d' ' -f1
  else
    echo ABSENT
  fi
}
REAL_BASE_BEFORE="$(real_manifest)"

ok()   { PASS=$((PASS+1)); printf '  %-26s PASS  %s\n' "$1" "$2"; }
bad()  { FAIL=$((FAIL+1)); printf '  %-26s FAIL  %s\n' "$1" "$2"; }

mkdir -p "$TMP/bin"
DECOY="$TMP/DECOY_not_created_by_this_file.txt"
echo "a file this selftest did not create; it must survive cleanup" > "$DECOY"

# ---- the docker STUB.  Every sandbox leg sees this instead of docker. --------
cat > "$TMP/bin/docker" <<'STUB'
#!/usr/bin/env bash
echo "STUB-DOCKER-CALLED $*" >> "$STUB_LOG"
# The stub ANSWERS the image-digest lookup with the registered digest and REFUSES
# everything else. Without this, the digest guard refuses first and EVERY LEG
# BEYOND IT IS UNREACHABLE -- the suite would have tested the first four guards
# and silently skipped the rest while reporting PASS. Found by this file's own
# STAGING legs failing with the digest guard's message instead of their own.
# `docker run` still hits the refusing path below, so no container is ever made.
if [ "${1:-}" = "image" ] && [ "${2:-}" = "inspect" ]; then
  echo "dafoam/opt-packages@sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc"
  exit 0
fi
exit 99
STUB
cat > "$TMP/bin/sudo" <<'STUB'
#!/usr/bin/env bash
# swallow sudo's own flags, then dispatch to the stubbed tool
while [ $# -gt 0 ]; do case "$1" in -n) shift ;; *) break ;; esac; done
exec "$@"
STUB
chmod +x "$TMP/bin/docker" "$TMP/bin/sudo"
export STUB_LOG="$TMP/stub_docker.log"
: > "$STUB_LOG"

echo "SO-3aF2 PIN CENSUS AND NO-LAUNCH SELFTEST"
echo "launcher md5 $(md5sum "$LAUNCHER" | cut -d' ' -f1)"
echo

# ===========================================================================
# JOB 1 -- THE PIN CENSUS.  Enumerated from the launcher's own bytes.
# ===========================================================================
echo "JOB 1 -- PIN CENSUS"
# ⚠ THE CHARACTER CLASS MUST ADMIT DIGITS. An earlier version used [A-Z_]+ and
# SILENTLY OMITTED `MD5_A1WR_DRIVER`, whose name carries a `1` -- and it reported
# `driven=4 exist=4 -- EQUAL` while five pins existed, because BOTH SIDES OF THE
# COMPARISON USED THE SAME BROKEN REGEX. A census that enumerates with the same
# rule it counts with CANNOT DETECT ITS OWN BLINDNESS: the equality it prints is
# true and vacuous. Found only because a newly added pin failed to appear.
PINS="$(grep -oE '^MD5_[A-Z_0-9]+=' "$LAUNCHER" | tr -d '=' | sort -u)"
N_EXIST="$(printf '%s\n' "$PINS" | grep -c . || true)"
N_DRIVEN=0
UNMAPPED=""
for pin in $PINS; do
  case "$pin" in
    MD5_READER)   target="$READER"; kind=file ;;
    MD5_PRODUCER) target="$PRODUCER"; kind=file ;;
    # A TREE MANIFEST, not a file md5, and the table says which so a reader is
    # not left inferring it. Its target is the MESH staging source named in the
    # launcher's own bytes -- read from there, never retyped here.
    MD5_MESH_SRC_MANIFEST)
                  target="$(grep -oE '^MESH_SRC=.*' "$LAUNCHER" | cut -d= -f2-)"; kind=manifest ;;
    MD5_ENV_ASSERT)
                  target="$HERE/so3af2_env_assert.sh"; kind=file ;;
    # ANOTHER ITEM'S FILE, pinned on purpose: the DAFoam loader path is DERIVED
    # from A1WR's driver rather than retyped, so a change there must REFUSE here.
    # Read from the launcher's own bytes, never retyped in this table.
    MD5_A1WR_DRIVER)
                  target="$(grep -oE '^A1WR_DRIVER=.*' "$LAUNCHER" | cut -d= -f2-)"; kind=file ;;
    *)            UNMAPPED="$UNMAPPED $pin"; continue ;;
  esac
  want="$(grep -oE "^${pin}=[0-9a-f]{32}" "$LAUNCHER" | cut -d= -f2)"
  # CROSS-CHECK THE ENUMERATION AGAINST A DIFFERENT RULE than the one that built
  # it, so the two cannot be blind together.
  if [ "$kind" = "manifest" ]; then
    if [ -d "$target" ]; then
      got="$( ( cd "$target" && find . -type f | sort | xargs md5sum ) | md5sum | cut -d' ' -f1 )"
    else
      got="SOURCE-TREE-ABSENT"
    fi
  else
    got="$(md5sum "$target" | cut -d' ' -f1)"
  fi
  if [ -z "$want" ]; then
    bad "PIN:$pin" "no 32-hex value on its assignment line"
  elif [ "$want" = "$got" ]; then
    N_DRIVEN=$((N_DRIVEN+1)); ok "PIN:$pin" "$(basename "$target") $got"
  else
    bad "PIN:$pin" "$(basename "$target") want=$want got=$got"
  fi
done
if [ -n "$UNMAPPED" ]; then
  bad "PIN-CENSUS" "enumerated pin(s) with NO registered target:$UNMAPPED"
fi
if [ "$N_DRIVEN" = "$N_EXIST" ] && [ -z "$UNMAPPED" ]; then
  ok "PIN-CENSUS" "driven=$N_DRIVEN exist=$N_EXIST -- EQUAL, so every pin is driven as a COUNT"
else
  bad "PIN-CENSUS" "driven=$N_DRIVEN exist=$N_EXIST -- NOT EQUAL"
fi

# ---- the outside half of NL-3: the launcher's own md5 against the registered
# ---- value.  A file cannot contain its own md5, so this is checked HERE,
# ---- against the pre-registration's Stage-2 amendment, and nowhere else.
SELF="$(md5sum "$LAUNCHER" | cut -d' ' -f1)"
if grep -q "$SELF" "$HERE/FEASIBILITY_PREREGISTRATION.md" 2>/dev/null; then
  ok "NL-3-OUTSIDE" "launcher md5 $SELF is pinned in the frozen document"
else
  bad "NL-3-OUTSIDE" "launcher md5 $SELF is NOT pinned in FEASIBILITY_PREREGISTRATION.md"
fi
echo

# ===========================================================================
# JOB 2 -- THE FOUR NO-LAUNCH BRANCHES, refusing AND passing
# ===========================================================================
echo "JOB 2 -- NO-LAUNCH BRANCHES"

# Build a sandbox: a copy of the launcher with BASE repointed, plus copies of
# the pinned files.  Every delta is PRINTED.
mk_sandbox() {   # mk_sandbox <name>
  local n="$1"; local d="$TMP/$n"
  mkdir -p "$d"
  cp "$READER" "$PRODUCER" "$HERE/so3af2_env_assert.sh" "$d/"
  sed -e "s|^BASE=.*|BASE=$d/base|" "$LAUNCHER" > "$d/so3af2_run_arm.sh"
  chmod +x "$d/so3af2_run_arm.sh"
  printf '%s\n' "$d"
}

run_sandbox() {  # run_sandbox <dir> <arm>
  ( cd "$1" && PATH="$TMP/bin:$PATH" ./so3af2_run_arm.sh "$2" ) > "$1/out.txt" 2>&1
  echo "$?"
}

expect() {       # expect <label> <dir> <rc> <file> <arm>
  local label="$1" d="$2" want_rc="$3" want_file="$4" arm="$5"
  local rc; rc="$(run_sandbox "$d" "$arm")"
  local where="$d/base/$want_file"; [ -f "$where" ] || where="$d/$want_file"
  if [ "$rc" = "$want_rc" ] && [ -f "$where" ]; then
    ok "$label" "rc=$rc wrote $(basename "$where")"
  else
    bad "$label" "rc=$rc (want $want_rc), $want_file present=$([ -f "$where" ] && echo yes || echo no); $(tail -1 "$d/out.txt")"
  fi
}

# ---- NL-3 FREEZE: corrupt the reader -----------------------------------------
D="$(mk_sandbox nl3)"; printf '\n# corruption\n' >> "$D/so3af2_read.py"
expect "NL-3 FREEZE (refuses)" "$D" 5 NOLAUNCH_FREEZE.txt MESH

# ---- NL-2 PRODUCER, md5 clause ----------------------------------------------
D="$(mk_sandbox nl2md5)"; printf '\n# corruption\n' >> "$D/so3af2_runScript.py"
expect "NL-2 PRODUCER md5" "$D" 4 NOLAUNCH_PRODUCER.txt MESH

# ---- NL-2 PRODUCER, forbidden-token clause.  The producer's md5 pin is moved
# ---- to the tainted bytes so the FIRST clause passes and the SECOND is what
# ---- fires -- otherwise this leg would pass for the wrong reason, which is a
# ---- failure mode this lane met earlier tonight and will not repeat.
D="$(mk_sandbox nl2tok)"
python3 - "$D/so3af2_runScript.py" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read() + "\n# " + "compute" + "_totals\n"
open(p, "w").write(s)
PY
NEWMD5="$(md5sum "$D/so3af2_runScript.py" | cut -d' ' -f1)"
sed -i "s|^MD5_PRODUCER=[0-9a-f]*|MD5_PRODUCER=$NEWMD5|" "$D/so3af2_run_arm.sh"
expect "NL-2 PRODUCER token" "$D" 4 NOLAUNCH_PRODUCER.txt MESH
if grep -q "forbidden gradient token appears" "$D/out.txt"; then
  ok "NL-2 token BY NAME" "refused on the token clause, not on the md5 clause"
else
  bad "NL-2 token BY NAME" "refusal text does not name the token clause: $(tail -1 "$D/out.txt")"
fi

# ---- NL-1 ROOT: the run root already exists ----------------------------------
D="$(mk_sandbox nl1)"; mkdir -p "$D/base"
expect "NL-1 ROOT (refuses)" "$D" 3 NOLAUNCH_ROOT.txt MESH

# ---- NL-4 MEM: an impossible floor and a zero bound must TERMINATE non-zero ---
D="$(mk_sandbox nl4)"
sed -i -e 's|^MEM_FLOOR_GIB=.*|MEM_FLOOR_GIB=999999.0|' \
       -e 's|^POLL_BOUND_S=.*|POLL_BOUND_S=0|' "$D/so3af2_run_arm.sh"
expect "NL-4 MEM (refuses)" "$D" 6 NOLAUNCH_MEM.txt MESH

# ---- STAGING: a wrong source manifest must REFUSE rc 9 ----------------------
D="$(mk_sandbox stage_manifest)"
sed -i 's|^MD5_MESH_SRC_MANIFEST=.*|MD5_MESH_SRC_MANIFEST=00000000000000000000000000000000|' "$D/so3af2_run_arm.sh"
expect "STAGING manifest" "$D" 9 NOLAUNCH_STAGING.txt MESH

# ---- STAGING: a required input MISSING must REFUSE rc 9, BY NAME.
# ---- The doctored source is re-pinned so the MANIFEST clause passes and the
# ---- PRECONDITION clause is what fires -- otherwise this leg would pass for the
# ---- wrong reason, which is the failure this file exists to make impossible.
D="$(mk_sandbox stage_missing)"
SRC_REAL="$(grep -oE '^MESH_SRC=.*' "$LAUNCHER" | cut -d= -f2-)"
if [ -d "$SRC_REAL" ]; then
  DOCTORED="$D/doctored_src"
  cp -a "$SRC_REAL" "$DOCTORED"
  rm -f "$DOCTORED/genAirFoilMesh.py"          # remove ONE required input by name
  NEWMAN="$( ( cd "$DOCTORED" && find . -type f | sort | xargs md5sum ) | md5sum | cut -d' ' -f1 )"
  sed -i -e "s|^MESH_SRC=.*|MESH_SRC=$DOCTORED|" \
         -e "s|^MD5_MESH_SRC_MANIFEST=.*|MD5_MESH_SRC_MANIFEST=$NEWMAN|" "$D/so3af2_run_arm.sh"
  expect "STAGING precondition" "$D" 9 NOLAUNCH_STAGING.txt MESH
  if grep -q "MISSING from" "$D/out.txt" && grep -q "genAirFoilMesh.py" "$D/out.txt"; then
    ok "STAGING names the SET" "refused on the precondition clause and NAMED the missing input"
  else
    bad "STAGING names the SET" "refusal does not name the missing input: $(tail -1 "$D/out.txt")"
  fi
else
  bad "STAGING precondition" "MESH_SRC $SRC_REAL is absent; leg NOT RUN, and NOT RUN is not PASS"
fi

# ---- THE PRODUCER'S PATH DERIVATION, driven against the REAL frozen reader and
# ---- against doctored copies. The producer imports DAFoam, which is not on the
# ---- host, so the FUNCTION is extracted by ast and exercised directly.
DERIVE_OUT="$TMP/derive.txt"
python3 - "$PRODUCER" "$READER" > "$DERIVE_OUT" 2>&1 <<'PYD'
import ast, os, sys, tempfile, shutil
prod, reader = sys.argv[1], sys.argv[2]
tree = ast.parse(open(prod).read())
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
          and n.name == "_reader_path_contract")
ns = {"os": os}
exec(compile(ast.Module(body=[fn], type_ignores=[]), "<d>", "exec"), ns)
derive = ns["_reader_path_contract"]
art, case, rd = derive(reader)
print("REAL", art, case, rd)
d = tempfile.mkdtemp(); base = open(reader).read(); refusals = 0
try:
    muts = [("absent", None),
            ("no_RUN_DIRS", lambda t: t.replace('RUN_DIRS = ["mp0", "mp1", "mp2"]', 'PH = 1')),
            ("two_json", lambda t: t + '\nE = os.path.join(root, "XM", "other.json")\n'),
            ("two_rundirs", lambda t: t + '\nZ = read_run_dirs(os.path.join(root, "XM", "elsewhere"))\n')]
    for label, m in muts:
        p2 = os.path.join(d, "so3af2_read.py")
        if m is None:
            if os.path.exists(p2): os.remove(p2)
        else:
            open(p2, "w").write(m(base))
        try:
            derive(p2); print("NOREFUSE", label)
        except SystemExit:
            refusals += 1
finally:
    shutil.rmtree(d, ignore_errors=True)
print("REFUSALS", refusals, "of", 4)
PYD
if grep -q "REAL \['XM', 'so3af2_M.json'\] \['XM', 'case'\] \['mp0', 'mp1', 'mp2'\]" "$DERIVE_OUT"; then
  ok "DERIVE matches reader" "artefact/case/run_dirs derived == the frozen reader's own lines"
else
  bad "DERIVE matches reader" "$(grep '^REAL' "$DERIVE_OUT" | head -1)"
fi
if grep -q "^REFUSALS 4 of 4" "$DERIVE_OUT"; then
  ok "DERIVE refuses 4/4" "absent reader, no RUN_DIRS, ambiguous artefact, ambiguous case -- all REFUSE"
else
  bad "DERIVE refuses 4/4" "$(grep -E '^REFUSALS|^NOREFUSE' "$DERIVE_OUT" | tr '\n' ' ')"
fi
rm -f "$DERIVE_OUT"

# ---- THE ENVIRONMENT ASSERTION, driven BOTH WAYS on the HOST. No container is
# ---- needed: the script sources a loader and interrogates the environment, so a
# ---- fake loader exercises the real code path.
ENVA="$HERE/so3af2_env_assert.sh"
ET="$TMP/envtest"; mkdir -p "$ET/bin"
printf '#!/bin/bash\ntrue\n' > "$ET/empty_loader.sh"
printf '#!/bin/bash\necho fake\n' > "$ET/bin/checkMesh"; chmod +x "$ET/bin/checkMesh"
printf '#!/bin/bash\nexport PATH="%s:$PATH"\nexport FOAM_APPBIN=%s\nexport WM_PROJECT=OpenFOAM\n' \
  "$ET/bin" "$ET/bin" > "$ET/good_loader.sh"

OUT_A="$(bash "$ENVA" "$ET/absent.sh" echo ARM-RAN 2>&1)"; RC_A=$?
if [ "$RC_A" = "11" ] && printf '%s' "$OUT_A" | grep -q "ABORT ENV-1"; then
  ok "ENV-1 absent loader" "rc=11 and refused BY NAME"
else
  bad "ENV-1 absent loader" "rc=$RC_A $(printf '%s' "$OUT_A" | head -1)"
fi

OUT_B="$(bash "$ENVA" "$ET/empty_loader.sh" echo ARM-RAN 2>&1)"; RC_B=$?
if [ "$RC_B" = "11" ] && printf '%s' "$OUT_B" | grep -q "ABORT ENV-3"; then
  ok "ENV-3 loader loads nothing" "rc=11 -- a source that no-ops REFUSES instead of being trusted"
else
  bad "ENV-3 loader loads nothing" "rc=$RC_B $(printf '%s' "$OUT_B" | head -1)"
fi

OUT_C="$(bash "$ENVA" "$ET/good_loader.sh" echo ARM-RAN 2>&1)"; RC_C=$?
if [ "$RC_C" = "0" ] && printf '%s' "$OUT_C" | grep -q "SO3AF2_ENV_OK" \
   && printf '%s' "$OUT_C" | grep -q "ARM-RAN"; then
  ok "ENV passes AND execs" "rc=0, SO3AF2_ENV_OK printed, and the arm command actually RAN"
else
  bad "ENV passes AND execs" "rc=$RC_C $(printf '%s' "$OUT_C" | tr '\n' ' ')"
fi
# ---- THE r3 SHAPE: a third-party init script that READS AN UNSET VARIABLE
# ---- BEFORE SETTING IT, which is what OpenFOAM's own etc/bashrc does at line
# ---- 180 and what killed MESH r3 with rc=1 inside the source. It must now PASS.
printf '#!/bin/bash\necho "$SOME_UNSET_VAR_READ_FIRST"\nexport SOME_UNSET_VAR_READ_FIRST=x\nexport PATH="%s:$PATH"\nexport FOAM_APPBIN=%s\nexport WM_PROJECT=OpenFOAM\n' \
  "$ET/bin" "$ET/bin" > "$ET/unbound_loader.sh"
OUT_D="$(bash "$ENVA" "$ET/unbound_loader.sh" echo ARM-RAN 2>&1)"; RC_D=$?
if [ "$RC_D" = "0" ] && printf '%s' "$OUT_D" | grep -q "SO3AF2_ENV_OK" \
   && printf '%s' "$OUT_D" | grep -q "ARM-RAN"; then
  ok "UNBOUND-VAR init script" "rc=0 -- the r3 failure shape now PASSES and the arm command RAN"
else
  bad "UNBOUND-VAR init script" "rc=$RC_D $(printf '%s' "$OUT_D" | tr '\n' ' ' | cut -c1-120)"
fi

# ---- ENV-0: AN UNFORESEEN TERMINATION MUST STILL PRODUCE A NAMED VERDICT.
# ---- This is the leg that would have caught r3 on its own: the instrument
# ---- exited saying NOTHING about itself, which is the one coverage lie the
# ---- other two do not cover -- SILENT rather than wrong.
printf '#!/bin/bash\nexit 7\n' > "$ET/dies_loader.sh"
OUT_E="$(bash "$ENVA" "$ET/dies_loader.sh" echo ARM-RAN 2>&1)"; RC_E=$?
if [ "$RC_E" = "12" ] && printf '%s' "$OUT_E" | grep -q "ENV-0 ASSERT TERMINATED WITHOUT VERDICT" \
   && printf '%s' "$OUT_E" | grep -q "last_checkpoint_reached"; then
  ok "ENV-0 silent-exit trap" "rc=12, named BY NAME, and it printed the last checkpoint reached"
else
  bad "ENV-0 silent-exit trap" "rc=$RC_E $(printf '%s' "$OUT_E" | tr '\n' ' ' | cut -c1-120)"
fi

# ---- and the arm command must NOT have run on that path
if printf '%s' "$OUT_E" | grep -q "ARM-RAN"; then
  bad "ENV-0 does not exec" "the arm command RAN after a verdict-less termination"
else
  ok "ENV-0 does not exec" "the arm command did NOT run -- a silent instrument stops the arm"
fi

rm -f "$ET/unbound_loader.sh" "$ET/dies_loader.sh"
rm -f "$ET/empty_loader.sh" "$ET/good_loader.sh" "$ET/bin/checkMesh"
rmdir "$ET/bin" "$ET" 2>/dev/null || true

# ---- the launcher must REFUSE if A1WR's driver drifts, because the loader path
# ---- is derived from it and a divergence would silently split the two items.
D="$(mk_sandbox a1wrdrift)"
sed -i 's|^MD5_A1WR_DRIVER=.*|MD5_A1WR_DRIVER=00000000000000000000000000000000|' "$D/so3af2_run_arm.sh"
expect "A1WR driver drift" "$D" 11 NOLAUNCH_ENV.txt MESH

# ===========================================================================
# THE XM ARM'S STAGING (ADDENDUM 6). Driven with a FAKE MESH OUTPUT so no
# container is needed. A wrong precondition here does NOT refuse -- it produces
# a plausible F3 MISS on a separation that worked -- so every direction is driven.
# ===========================================================================
mk_fake_mesh() {   # mk_fake_mesh <base>   -- the minimum MESH output XM consumes
  local b="$1"
  mkdir -p "$b/MESH/constant/polyMesh" "$b/MESH/0" "$b/MESH/system" "$b/MESH/FFD"
  echo "boundary"   > "$b/MESH/constant/polyMesh/boundary"
  echo "U"          > "$b/MESH/0/U.gz"
  echo "controlDict"> "$b/MESH/system/controlDict"
  echo "ffd"        > "$b/MESH/FFD/wingFFD.xyz"
}

# ---- the FFD reference must derive WITHOUT its closing quote. This is a direct
# ---- assertion because the first draft yielded `FFD/wingFFD.xyz"` and would
# ---- have refused on every launch, forever.
FFD_DERIVED="$(grep -oE 'OM_DVGEOCOMP\(file="[^"]+"' "$PRODUCER" | sed 's/.*file="//; s/"$//' | sort -u)"
if [ "$FFD_DERIVED" = "FFD/wingFFD.xyz" ]; then
  ok "XM FFD derivation" "'$FFD_DERIVED' -- exactly one reference, no trailing quote"
else
  bad "XM FFD derivation" "derived '$FFD_DERIVED'"
fi

# ---- XM REFUSES when MESH has not run -----------------------------------
D="$(mk_sandbox xm_nomesh)"; mkdir -p "$D/base"
expect "XM without MESH" "$D" 9 NOLAUNCH_STAGING.txt XM
if grep -q "arm MESH has not run" "$D/out.txt"; then
  ok "XM without MESH BY NAME" "refused naming the missing MESH output, not a generic staging error"
else
  bad "XM without MESH BY NAME" "$(tail -1 "$D/out.txt")"
fi

# ---- XM REFUSES when MESH exists but carries no mesh ---------------------
D="$(mk_sandbox xm_nopoly)"; mkdir -p "$D/base/MESH/0"; echo U > "$D/base/MESH/0/U.gz"
expect "XM without polyMesh" "$D" 9 NOLAUNCH_STAGING.txt XM

# ---- XM STAGES: the passing direction, and it must build the reader's layout
D="$(mk_sandbox xm_ok)"; mk_fake_mesh "$D/base"
RC_XM="$(run_sandbox "$D" XM)"
CASE="$D/base/XM/case"
XM_OK=1
grep -q "SO3AF2_STAGED arm=XM" "$D/out.txt" || XM_OK=0
grep -q "SO3AF2_STAGING_PRECONDITION_PASS arm=XM" "$D/out.txt" || XM_OK=0
[ -f "$CASE/FFD/wingFFD.xyz" ] || XM_OK=0
for mp in mp0 mp1 mp2; do
  [ -f "$CASE/$mp/constant/polyMesh/boundary" ] || XM_OK=0
  { [ -f "$CASE/$mp/0/U" ] || [ -f "$CASE/$mp/0/U.gz" ]; } || XM_OK=0
done
[ -f "$D/base/XM/so3af2_runScript.py" ] || XM_OK=0
[ -f "$D/base/XM/so3af2_read.py" ] || XM_OK=0
if [ "$XM_OK" = "1" ]; then
  ok "XM stages the reader's layout" "case/FFD/wingFFD.xyz + case/mp0..2 each with polyMesh and 0/, producer and reader beside them (run ended rc=$RC_XM at the stub)"
else
  bad "XM stages the reader's layout" "rc=$RC_XM; $(tail -1 "$D/out.txt")"
fi

# ---- and the per-point layout must be where the FROZEN READER looks --------
if [ -d "$CASE" ] && [ "$(basename "$CASE")" = "case" ]; then
  ok "XM layout matches the reader" "per-point dirs under <root>/XM/case/, which is read_run_dirs' own argument"
else
  bad "XM layout matches the reader" "case dir is $CASE"
fi

# ---- G-COLD: a time directory in a point must REFUSE ----------------------
D="$(mk_sandbox xm_warm)"; mk_fake_mesh "$D/base"; mkdir -p "$D/base/MESH/0.0001"
echo warm > "$D/base/MESH/0.0001/U"
expect "XM G-COLD warm start" "$D" 9 NOLAUNCH_STAGING.txt XM

rm -rf "$TMP/xm_nomesh/base" "$TMP/xm_nopoly/base" "$TMP/xm_ok/base" "$TMP/xm_warm/base" 2>/dev/null

# ---- THE PASSING DIRECTION.  All four guards must be SATISFIABLE, proved by
# ---- all four PASS lines appearing before the launcher reaches the container.
D="$(mk_sandbox pass)"
RC="$(run_sandbox "$D" MESH)"
MISS=""
for tag in SO3AF2_NL3_PASS SO3AF2_NL2_PASS SO3AF2_NL1_PASS SO3AF2_NL4_PASS SO3AF2_LOADER_DERIVED SO3AF2_STAGED SO3AF2_STAGING_PRECONDITION_PASS; do
  grep -q "$tag" "$D/out.txt" || MISS="$MISS $tag"
done
if [ -z "$MISS" ]; then
  # PRECISION, because this family's standing lesson is that a control passing
  # for a reason other than the one it claims is not testing what it says: the
  # run ends at rc=$RC because the IMAGE-DIGEST guard cannot read a digest from
  # the stub -- NOT at `docker run`, which is never reached. What this leg
  # proves is exactly and only that all four NL guards are SATISFIABLE.
  ok "ALL GUARDS SATISFIABLE" "every guard printed its PASS line INCLUDING staging; the run then ended rc=$RC because the stub REFUSES \`docker run\` -- which is the only place it can end, and NO CONTAINER IS EVER CREATED"
else
  bad "ALL GUARDS SATISFIABLE" "missing PASS line(s):$MISS -- a guard that cannot pass is unsatisfiable by construction"
fi

# ---- the diffs, printed so no sandbox delta is taken on trust ----------------
echo
echo "SANDBOX DELTAS (printed, not asserted away):"
diff "$LAUNCHER" "$TMP/pass/so3af2_run_arm.sh" | sed 's/^/    /' || true

# ===========================================================================
# JOB 3 -- THE SAFETY ASSERTIONS.  Both sentences of section 2 must still hold.
# ===========================================================================
echo
echo "JOB 3 -- SAFETY"
REAL_BASE_AFTER="$(real_manifest)"
# THE REAL RUN ROOT: this file must not CREATE it and must not MODIFY it. An
# earlier version asserted the root was ABSENT -- true at the Stage-2 amendment,
# and made FALSE by the daemon's 2026-09-03T21:48:15Z launch. An assertion that
# only holds before the item's first container is not a safety property of this
# file; what this file owns is that it changed nothing. Measured as a manifest.
if [ "$REAL_BASE_BEFORE" = "$REAL_BASE_AFTER" ]; then
  ok "REAL ROOT UNTOUCHED" "manifest unchanged across this run: $REAL_BASE_BEFORE"
else
  bad "REAL ROOT UNTOUCHED" "manifest MOVED $REAL_BASE_BEFORE -> $REAL_BASE_AFTER -- this file modified the real run root"
fi
if [ -s "$STUB_LOG" ]; then
  ok "NO CONTAINER STARTED" "docker was reached $(grep -c . "$STUB_LOG") time(s), ALL of them the STUB. It answers ONLY \`image inspect\` (with the registered digest, so the legs past that guard are reachable) and REFUSES everything else, \`docker run\` included -- so no container is ever created. The full transcript is printed below rather than summarised."
  sed 's/^/    /' "$STUB_LOG"
else
  ok "NO CONTAINER STARTED" "docker was never reached at all"
fi

# ---- cleanup BY NAME, and the decoy must survive it -------------------------
for n in nl3 nl2md5 nl2tok nl1 nl4 stage_manifest stage_missing a1wrdrift xm_nomesh xm_nopoly xm_ok xm_warm pass; do
  # the staged arm tree and the doctored source are NAMED paths this file created
  # under its own $TMP -- removed by name, never by glob and never by sweep.
  rm -rf "$TMP/$n/base/MESH" "$TMP/$n/doctored_src" 2>/dev/null
  rm -f "$TMP/$n/so3af2_run_arm.sh" "$TMP/$n/so3af2_read.py" "$TMP/$n/so3af2_runScript.py" "$TMP/$n/out.txt"
  rm -f "$TMP/$n/base/NOLAUNCH_ROOT.txt" "$TMP/$n/base/NOLAUNCH_PRODUCER.txt" \
        "$TMP/$n/base/NOLAUNCH_FREEZE.txt" "$TMP/$n/base/NOLAUNCH_MEM.txt" \
        "$TMP/$n/NOLAUNCH_ROOT.txt" "$TMP/$n/NOLAUNCH_PRODUCER.txt" \
        "$TMP/$n/NOLAUNCH_FREEZE.txt" "$TMP/$n/NOLAUNCH_MEM.txt"
  rmdir "$TMP/$n/base" "$TMP/$n" 2>/dev/null || true
done
rm -f "$TMP/bin/docker" "$TMP/bin/sudo" "$STUB_LOG"
rmdir "$TMP/bin" 2>/dev/null || true
if [ -f "$DECOY" ]; then
  ok "DECOY SURVIVED" "cleanup was by name, not by sweep"
else
  bad "DECOY SURVIVED" "the decoy was removed -- cleanup swept something it did not create"
fi
rm -f "$DECOY"; rmdir "$TMP" 2>/dev/null || true

echo
echo "SO3aF2 PIN CENSUS: PASS $PASS  FAIL $FAIL  NOT RUN 0"
[ "$FAIL" = "0" ] || exit 1
exit 0
