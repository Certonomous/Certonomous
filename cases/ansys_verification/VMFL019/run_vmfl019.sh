#!/usr/bin/env bash
# VMFL019 -- Stokes' first problem.  Builds the three-level space+time Roache
# family (L1 Ny=30 dt=0.05, L2 Ny=60 dt=0.025, L3 Ny=120 dt=0.0125) and launches
# each level DETACHED (setsid+nohup) with a wrapper that writes RUN_RC.txt and
# DONE.flag on completion (disk-recoverable, no agent needed).  A detached
# contention sampler writes CONTENTION.csv throughout.  Does NOT grade;
# grade_vmfl019.py is frozen separately and cited by sha in PREREGISTRATION.md.
# Guards: (1) no level dir pre-exists; (2) prereg committed at HEAD; (3) per-level
# wall timeout = cap, overrun STOPS the level.  Age-guard marker 0/U.
set -u -o pipefail

CASE_SRC="/home/ubuntu/Certonomous/cases/ansys_verification/VMFL019/case"
RUN_ROOT="/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL019"
PREREG="cases/ansys_verification/VMFL019/PREREGISTRATION.md"
CAP_CORE_MIN=9
RANKS=1
PERLEVEL_TIMEOUT=180     # s wall per level (=3 core-min at ranks=1); ~60x a ~3s clean solve
LEVELS="L1_30:30:0.05 L2_60:60:0.025 L3_120:120:0.0125"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"

refuse() { echo "REFUSE: $*" >&2; exit 2; }

cd /home/ubuntu/Certonomous || refuse "repository not found"
git cat-file -e "HEAD:${PREREG}" 2>/dev/null || refuse "pre-registration NOT committed at HEAD (rule 2)"
PREREG_SHA=$(git rev-parse "HEAD:${PREREG}")
echo "pre-registration frozen at blob ${PREREG_SHA}"

for spec in $LEVELS; do
  name="${spec%%:*}"
  [ -e "${RUN_ROOT}/${name}" ] && refuse "${RUN_ROOT}/${name} already exists"
done
mkdir -p "$RUN_ROOT" || refuse "cannot create ${RUN_ROOT}"

set +u; source "$FOAM_BASHRC" || refuse "cannot source ${FOAM_BASHRC}"; set -u
command -v icoFoam >/dev/null || refuse "icoFoam not on PATH"
command -v blockMesh >/dev/null || refuse "blockMesh not on PATH"

for spec in $LEVELS; do
  IFS=: read -r name NY DT <<< "$spec"
  d="${RUN_ROOT}/${name}"
  echo "=== building ${name}: Ny=${NY}, dt=${DT} ==="
  mkdir -p "$d" || refuse "cannot create $d"
  cp -r "${CASE_SRC}/0" "${CASE_SRC}/constant" "${CASE_SRC}/system" "$d/" || refuse "case copy failed"
  rm -f "$d/system/blockMeshDict.template" "$d/system/controlDict.template"
  sed -e "s/__NY__/${NY}/g" "${CASE_SRC}/system/blockMeshDict.template" > "$d/system/blockMeshDict" || refuse "blockMeshDict subst failed"
  grep -q "__N" "$d/system/blockMeshDict" && refuse "unsubstituted mesh placeholder in ${name}"
  sed -e "s/__DT__/${DT}/g" "${CASE_SRC}/system/controlDict.template" > "$d/system/controlDict" || refuse "controlDict subst failed"
  grep -q "__DT__" "$d/system/controlDict" && refuse "unsubstituted dt placeholder in ${name}"
  ( cd "$d" && blockMesh > log.blockMesh 2>&1 ); rc=$?
  [ $rc -eq 0 ] || refuse "${name}: blockMesh returned ${rc}"
  ( cd "$d" && checkMesh > log.checkMesh 2>&1 )
done

DONE_EXPECT=3
setsid nohup bash -c '
  RR="'"$RUN_ROOT"'"; end=$(( $(date +%s) + 1200 ))
  echo "utc,loadavg1,run_slash_total,ico_procs,top_pcpu" > "$RR/CONTENTION.csv"
  while :; do
    la=$(cut -d" " -f1 /proc/loadavg); rt=$(cut -d" " -f4 /proc/loadavg)
    np=$(ps -eo comm | grep -c "^icoFoam$" || true)
    tp=$(ps -eo pcpu,comm --sort=-pcpu | awk "\$2==\"icoFoam\"{print \$1; exit}"); [ -z "$tp" ] && tp=0
    echo "$(date -u +%FT%TZ),$la,$rt,$np,$tp" >> "$RR/CONTENTION.csv"
    n=$(ls "$RR"/*/DONE.flag 2>/dev/null | wc -l)
    [ "$n" -ge '"$DONE_EXPECT"' ] && break
    [ "$(date +%s)" -ge "$end" ] && break
    sleep 10
  done
  echo "sampler_stop utc=$(date -u +%FT%TZ) done_flags=$(ls "$RR"/*/DONE.flag 2>/dev/null | wc -l)" >> "$RR/CONTENTION.csv"
' > /dev/null 2>&1 &
echo "contention sampler pid=$!"

: > "${RUN_ROOT}/LAUNCH_MANIFEST.txt"
for spec in $LEVELS; do
  IFS=: read -r name NY DT <<< "$spec"
  d="${RUN_ROOT}/${name}"
  touch "$d/0/U"   # AGE-GUARD MARKER
  setsid nohup bash -c '
    d="'"$d"'"; RANKS='"$RANKS"'; PREREG_SHA="'"$PREREG_SHA"'"; name="'"$name"'"
    cd "$d" || exit 3
    t0=$(date +%s)
    timeout '"$PERLEVEL_TIMEOUT"' icoFoam > log.icoFoam 2>&1
    rc=$?
    t1=$(date +%s); wall=$(( t1 - t0 ))
    cm=$(awk "BEGIN{printf \"%.4f\", $wall*$RANKS/60.0}")
    printf "level=%s\nrc=%d\nwall_s=%d\nranks=%d\ncore_min=%s\nprereg_blob=%s\nutc=%s\n" \
      "$name" "$rc" "$wall" "$RANKS" "$cm" "$PREREG_SHA" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > RUN_RC.txt
    touch DONE.flag
  ' > /dev/null 2>&1 &
  pid=$!
  printf "level=%s pid=%d cwd=%s solver=icoFoam timeout_s=%d cap_core_min_total=%d prereg_blob=%s utc=%s\n" \
    "$name" "$pid" "$d" "$PERLEVEL_TIMEOUT" "$CAP_CORE_MIN" "$PREREG_SHA" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "${RUN_ROOT}/LAUNCH_MANIFEST.txt"
done
echo "VMFL019: all three levels launched detached. Grade when 3 DONE.flags exist:"
echo "  python3 cases/ansys_verification/VMFL019/grade_vmfl019.py"
