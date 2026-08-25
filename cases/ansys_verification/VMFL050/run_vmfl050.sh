#!/usr/bin/env bash
# VMFL050 -- Transient heat conduction in a semi-infinite slab.  Builds the
# three-level space+time Roache family (L1 Nx=75 dt=2, L2 Nx=150 dt=1,
# L3 Nx=300 dt=0.5) and launches each level as a DETACHED solver (setsid+nohup)
# so it survives this lane being stopped.  It does NOT grade; grading is
# grade_vmfl050.py, frozen separately and cited by sha in PREREGISTRATION.md.
#
# Each level's solver is wrapped so that, with NO agent alive, it writes
# RUN_RC.txt (rc, wall, core-min) and DONE.flag on completion -- a later session
# establishes state from disk alone.  A detached contention sampler writes
# CONTENTION.csv (loadavg + /proc/loadavg running/total split + this case's
# solver %CPU) throughout, self-terminating when all three DONE.flags exist.
#
# GUARDS: (1) refuse if any level dir pre-exists (rule 4); (2) refuse if the
# pre-registration is not committed at HEAD (rule 2); (3) per-level wall timeout
# = cap; an overrun STOPS that level (rule 12).  Age-guard marker: 0/T, touched
# immediately before each solver launches.
set -u -o pipefail

CASE_SRC="/home/ubuntu/Certonomous/cases/ansys_verification/VMFL050/case"
RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL050"
PREREG="cases/ansys_verification/VMFL050/PREREGISTRATION.md"
CAP_CORE_MIN=8            # total cap; est ~0.2 core-min clean x ~40 slack for I/O contention
RANKS=1
PERLEVEL_TIMEOUT=160     # s wall per level (=2.67 core-min at ranks=1); ~80x the ~2s clean solve
LEVELS="L1_75:75:2 L2_150:150:1 L3_300:300:0.5"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

refuse() { echo "REFUSE: $*" >&2; exit 2; }

cd /home/ubuntu/Certonomous || refuse "repository not found"
git cat-file -e "HEAD:${PREREG}" 2>/dev/null || \
  refuse "the pre-registration is NOT committed at HEAD -- no solver may start (rule 2)"
PREREG_SHA=$(git rev-parse "HEAD:${PREREG}")
echo "pre-registration frozen at blob ${PREREG_SHA}"

for spec in $LEVELS; do
  name="${spec%%:*}"
  [ -e "${RUN_ROOT}/${name}" ] && refuse "${RUN_ROOT}/${name} already exists -- never run into an existing case"
done
mkdir -p "$RUN_ROOT" || refuse "cannot create ${RUN_ROOT}"

set +u; source "$FOAM_BASHRC" || refuse "cannot source ${FOAM_BASHRC}"; set -u
command -v laplacianFoam >/dev/null || refuse "laplacianFoam not on PATH"
command -v blockMesh >/dev/null || refuse "blockMesh not on PATH"

# build all three meshes first (foreground), then launch all solvers detached
for spec in $LEVELS; do
  IFS=: read -r name NX DT <<< "$spec"
  d="${RUN_ROOT}/${name}"
  echo "=== building ${name}: Nx=${NX}, dt=${DT} ==="
  mkdir -p "$d" || refuse "cannot create $d"
  cp -r "${CASE_SRC}/0" "${CASE_SRC}/constant" "${CASE_SRC}/system" "$d/" || refuse "case copy failed"
  rm -f "$d/system/blockMeshDict.template" "$d/system/controlDict.template"
  sed -e "s/__NX__/${NX}/g" "${CASE_SRC}/system/blockMeshDict.template" > "$d/system/blockMeshDict" || refuse "blockMeshDict subst failed"
  grep -q "__N" "$d/system/blockMeshDict" && refuse "unsubstituted mesh placeholder in ${name}"
  sed -e "s/__DT__/${DT}/g" "${CASE_SRC}/system/controlDict.template" > "$d/system/controlDict" || refuse "controlDict subst failed"
  grep -q "__DT__" "$d/system/controlDict" && refuse "unsubstituted dt placeholder in ${name}"
  ( cd "$d" && blockMesh > log.blockMesh 2>&1 ); rc=$?
  [ $rc -eq 0 ] || refuse "${name}: blockMesh returned ${rc}"
  ( cd "$d" && checkMesh > log.checkMesh 2>&1 )
done

# detached contention sampler (self-terminating on 3 DONE.flags or 1200 s)
DONE_EXPECT=3
setsid nohup bash -c '
  RR="'"$RUN_ROOT"'"; end=$(( $(date +%s) + 1200 ))
  echo "utc,loadavg1,run_slash_total,laplacian_procs,top_pcpu" > "$RR/CONTENTION.csv"
  while :; do
    la=$(cut -d" " -f1 /proc/loadavg); rt=$(cut -d" " -f4 /proc/loadavg)
    np=$(ps -eo comm | grep -c "^laplacianFoam$" || true)
    tp=$(ps -eo pcpu,comm --sort=-pcpu | awk "\$2==\"laplacianFoam\"{print \$1; exit}"); [ -z "$tp" ] && tp=0
    echo "$(date -u +%FT%TZ),$la,$rt,$np,$tp" >> "$RR/CONTENTION.csv"
    n=$(ls "$RR"/*/DONE.flag 2>/dev/null | wc -l)
    [ "$n" -ge '"$DONE_EXPECT"' ] && break
    [ "$(date +%s)" -ge "$end" ] && break
    sleep 10
  done
  echo "sampler_stop utc=$(date -u +%FT%TZ) done_flags=$(ls "$RR"/*/DONE.flag 2>/dev/null | wc -l)" >> "$RR/CONTENTION.csv"
' > /dev/null 2>&1 &
echo "contention sampler pid=$!"

# launch each level detached
: > "${RUN_ROOT}/LAUNCH_MANIFEST.txt"
for spec in $LEVELS; do
  IFS=: read -r name NX DT <<< "$spec"
  d="${RUN_ROOT}/${name}"
  touch "$d/0/T"   # AGE-GUARD MARKER, last thing before launch
  setsid nohup bash -c '
    d="'"$d"'"; RANKS='"$RANKS"'; PREREG_SHA="'"$PREREG_SHA"'"; name="'"$name"'"
    cd "$d" || exit 3
    t0=$(date +%s)
    timeout '"$PERLEVEL_TIMEOUT"' laplacianFoam > log.laplacianFoam 2>&1
    rc=$?
    t1=$(date +%s); wall=$(( t1 - t0 ))
    cm=$(awk "BEGIN{printf \"%.4f\", $wall*$RANKS/60.0}")
    printf "level=%s\nrc=%d\nwall_s=%d\nranks=%d\ncore_min=%s\nprereg_blob=%s\nutc=%s\n" \
      "$name" "$rc" "$wall" "$RANKS" "$cm" "$PREREG_SHA" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > RUN_RC.txt
    touch DONE.flag
  ' > /dev/null 2>&1 &
  pid=$!
  printf "level=%s pid=%d cwd=%s solver=laplacianFoam timeout_s=%d cap_core_min_total=%d prereg_blob=%s utc=%s\n" \
    "$name" "$pid" "$d" "$PERLEVEL_TIMEOUT" "$CAP_CORE_MIN" "$PREREG_SHA" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "${RUN_ROOT}/LAUNCH_MANIFEST.txt"
done
echo "VMFL050: all three levels launched detached. Grade when 3 DONE.flags exist:"
echo "  python3 cases/ansys_verification/VMFL050/grade_vmfl050.py"
