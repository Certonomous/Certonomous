#!/usr/bin/env bash
# =============================================================================
# CURRICULUM D12 (proper) -- THE LAUNCHER.  FROZEN INSTRUMENT.
# Authored 2026-08-25 by dafoam `lab-lane` under SUPERVISOR_D12_RULINGS.md §3,
# which rules that the launcher is authored by the lane that fires it, subject to
# three binding conditions.  All three are implemented here and each is marked
# [RULING-3.1] / [RULING-3.2] / [RULING-3.3] at its site.
#
# THIS SCRIPT IS A PRODUCER, NOT AN AUDITOR.  It stages cases, launches containers
# and writes a MANIFEST.  It computes no graded quantity, applies no threshold and
# renders no verdict.  Every number that reaches a verdict is read off disk by the
# frozen comparator `d12r_grade.py`, which a different lane authored.
#
# -----------------------------------------------------------------------------
# WHY THIS FILE IS WRITTEN THE WAY IT IS -- D4-DEF-4, WHICH LANDED TODAY
# -----------------------------------------------------------------------------
# D4's endpoint was extracted in driver-SCALED units and applied as PHYSICAL.
# `shape`'s scaler was 10, so the mesh died and the corruption surfaced as a hard
# crash.  HAD THAT SCALER BEEN 1.0, every primal would have converged and every
# count-, plant- and order-based control downstream would have PASSED on a design
# point that was not the optimum.  THE FULLY ARMED INSTRUMENT SET WOULD HAVE
# CERTIFIED IT.
#
#   "A units error is invisible to every count-based, plant-based and order-based
#    control in this family's gate set.  They check THAT n components were
#    measured.  They never check WHERE."
#                       -- SUPERVISOR_D4DEF4_REPAIR_RULING.md §2
#
# So this launcher's central obligation is a WHERE-CONTROL [RULING-3.3]: for every
# stage that perturbs a design variable it writes the perturbation IT ACTUALLY
# APPLIED -- index, sign and magnitude, plus the full shape vector -- into the
# manifest, and the comparator reads that back off disk and REFUSES if it does not
# match the registered value.  A count of stages is not a witness of what was
# perturbed.
#
# -----------------------------------------------------------------------------
# WHAT THIS LAUNCHER DELIBERATELY DOES NOT DO [RULING-3.3, second half]
# -----------------------------------------------------------------------------
# IT DOES NOT CHOOSE A STEP.  The sweep's step list is computed by the FROZEN
# COMPARATOR in `--plan` mode and written to `step_plan.json`; phase 2 reads that
# file and does what it says.  The rule that selects the reference step h* stays
# in the comparator and is POSITIONAL OVER THE PLATEAU -- it never reads the
# adjoint.  That property is what made D10-F''s V-shaped error minimum an
# unforgeable corroboration, and it is not given up here.
#
# (G12R-4 sizes the RANGE of the sweep from |g| -- that is the pre-registration's
#  own registered arithmetic and is not the same thing as selecting h*.  The range
#  is sized from |g|; the reference step inside the plateau is positional.)
#
# -----------------------------------------------------------------------------
# INHERITED CONTAINER PATTERN (proven on this box)
#   L-251  --user 0:0 pinned
#   L-252  per-invocation STAMP; .ok.STAMP provenance sentinel
#   8.1    kernel-only stop: --memory == --memory-swap, --oom-score-adj=500, timeout
#   8.2    NO --rm, so `docker inspect .State.OOMKilled` survives the stage
#   --bind-to none, which avoided the measured 3.99x CPU-0 collision
# =============================================================================
set -uo pipefail

# ---------------------------------------------------------------- registration
# EVERY VALUE BELOW IS THE VALUE THE PRE-REGISTRATION NAMES.  None is a preference.
IMG_SHIPPED="dafoam/opt-packages:latest"
IMG_PATCHED="dafoam-idwarp-rot:v1"
ID_SHIPPED="sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc"
ID_PATCHED="sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"

BASE="${BASE:-/home/ubuntu/certonomous-runs/CURRICULUM-D12-cylinder-unsteady}"
TUT="${TUT:-/home/ubuntu/dafoam-tutorials/Cylinder}"
SRC="${SRC:-/home/ubuntu/Certonomous/cases/dafoam/curriculum_D12}"
RUNPY="$SRC/d12r_run_script.py"
GRADEPY="$SRC/d12r_grade.py"

# §6 REGISTERED CAP.  [RULING-3.1 context] The launcher ASSERTS its own cap against
# the value the pre-registration names -- closing the defect D12-E' §6.1 disclosed,
# where a copied-forward launcher enforced a cap its pre-registration did not name.
CAP_CORE_MIN_REGISTERED="600.0"
CAP_S8_REGISTERED="350.0"
CAP_CORE_MIN="${CAP_CORE_MIN:-600.0}"
CAP_S8="${CAP_S8:-350.0}"
MEMAVAIL_FLOOR_GIB="14.0"      # §G12R-8 registered floor
MEM_LIMIT="20g"                # §3 registered per-container limit

W_STEPS=300                    # §3.1 primary graded window, timesteps
DELTAT="1e-2"
TRANSIENT_DISCARD=300          # §3.1 first 300 steps of S2 discarded
S2_STEPS=2400                  # §3 diagnostic
ENV_STEPS="20 40 80"           # §G12R-8
# §S3b, added under RULING 4 (delta_pert).  Two probe steps a DECADE APART, frozen.
DPERT_HA="1.0e-6"
DPERT_HB="1.0e-5"
NSHAPES_EXPECTED=4

SPENT_CORE_MIN=0
SPENT_S8_CORE_MIN=0
STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$

usage () { echo "usage: $0 --phase {1|2|3} [--image {shipped|patched}]"; exit 3; }
PHASE=""; ROW="shipped"
while [ $# -gt 0 ]; do
  case "$1" in
    --phase) PHASE="$2"; shift 2;;
    --image) ROW="$2"; shift 2;;
    *) usage;;
  esac
done
[ -n "$PHASE" ] || usage

if [ "$ROW" = "shipped" ]; then IMG="$IMG_SHIPPED"; ID_EXPECT="$ID_SHIPPED"; SFX="";
elif [ "$ROW" = "patched" ]; then IMG="$IMG_PATCHED"; ID_EXPECT="$ID_PATCHED"; SFX="_p";
else usage; fi

ROOT="$BASE$SFX"
LEDGER="$ROOT/ledger.txt"
MANIFEST="$ROOT/manifest.jsonl"

# ============================================================ pre-flight asserts
# These run BEFORE a single core-minute is spent.  Each aborts; none warns.

# A1 -- the registered cap is the cap actually enforced (D12-E' §6.1's defect)
[ "$CAP_CORE_MIN" = "$CAP_CORE_MIN_REGISTERED" ] || {
  echo "ABORT: CAP_CORE_MIN is $CAP_CORE_MIN, the pre-registration names $CAP_CORE_MIN_REGISTERED"; exit 1; }
[ "$CAP_S8" = "$CAP_S8_REGISTERED" ] || {
  echo "ABORT: CAP_S8 is $CAP_S8, the pre-registration names $CAP_S8_REGISTERED"; exit 1; }

# A2 -- toolchain identity by IMAGE ID, never by tag (DAFOAM_CHARTER.md §11)
GOT_ID=$(sudo -n docker inspect --format '{{.Id}}' "$IMG" 2>/dev/null)
[ "$GOT_ID" = "$ID_EXPECT" ] || { echo "ABORT: $IMG id is '$GOT_ID', registered '$ID_EXPECT'"; exit 1; }

# A3 -- the instruments on disk ARE the committed blobs (CLAUDE.md rule 2's grading-path
# clause, EXECUTED and not asserted).  A mismatch aborts; it does not warn.
for f in "$RUNPY" "$GRADEPY"; do
  rel="${f#/home/ubuntu/Certonomous/}"
  d=$(md5sum "$f" | cut -d' ' -f1)
  b=$(cd /home/ubuntu/Certonomous && git show "HEAD:$rel" 2>/dev/null | md5sum | cut -d' ' -f1)
  [ "$d" = "$b" ] || { echo "ABORT: $rel md5 $d != committed blob $b"; exit 4; }
  echo "INSTRUMENT_VERIFIED $rel md5=$d"
done

# A4 -- SUPERVISOR'S AMENDED PRE-COMPUTE CHECK (RULINGS §2): every instrument the
# pre-registration names must EXIST, established by a predicate naming each file,
# WITH A PLANTED CONTROL proving the enumeration can return a name it should find.
# A "not found" from a predicate never shown able to find anything is not evidence.
PLANT_PROBE="d12r_run_script.py"      # known to exist; the planted control
missing=""
for want in d12r_run_script.py d12r_grade.py d12r_stage_and_run.sh; do
  if [ -f "$SRC/$want" ]; then found_any="$want"; else missing="$missing $want"; fi
done
[ -f "$SRC/$PLANT_PROBE" ] || { echo "ABORT: PLANTED CONTROL FAILED -- the predicate cannot see $PLANT_PROBE, which exists. A 'not found' from this loop would be meaningless."; exit 5; }
echo "INSTRUMENT_ENUMERATION_PLANT_OK saw $PLANT_PROBE"
[ -z "$missing" ] || { echo "ABORT: pre-registration names instruments that do not exist:$missing"; exit 5; }

# A5 -- the run-root guard.  A guard that refuses a case whose run directory already
# exists IS THE GUARD WORKING.  Phase 1 refuses a pre-existing root; phases 2 and 3
# REQUIRE it, because they continue a run they did not start.
if [ "$PHASE" = "1" ]; then
  [ -e "$ROOT" ] && { echo "REFUSE: run root already exists: $ROOT"; echo "A completed phase is not deleted to re-run it. Inspect it, do not clear it."; exit 6; }
  mkdir -p "$ROOT" || { echo "ABORT: cannot mkdir $ROOT"; exit 1; }
  chmod 777 "$ROOT"
  : > "$MANIFEST"
  { echo "ITEM=CURRICULUM-D12-proper"; echo "ROW=$ROW"; echo "IMAGE=$IMG"; echo "IMAGE_ID=$GOT_ID";
    echo "NP=1 numberOfSubdomains=1"; echo "W_STEPS=$W_STEPS deltaT=$DELTAT";
    echo "CAP_CORE_MIN=$CAP_CORE_MIN (registered $CAP_CORE_MIN_REGISTERED)";
    echo "CAP_S8=$CAP_S8 MEMAVAIL_FLOOR_GIB=$MEMAVAIL_FLOOR_GIB";
    echo "STAMP=$STAMP"; echo "STARTED_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } | tee -a "$LEDGER"
else
  [ -d "$ROOT" ] || { echo "ABORT: phase $PHASE continues a run that does not exist: $ROOT"; exit 6; }
  # recover cumulative spend from the ledger so the cap is CUMULATIVE ACROSS PHASES,
  # not per-phase.  A per-phase cap is not the cap the pre-registration registers.
  SPENT_CORE_MIN=$(awk -F'core_min=' '/^STAGE=/{split($2,a," "); s+=a[1]} END{printf "%.4f", s+0}' "$LEDGER")
  SPENT_S8_CORE_MIN=$(awk -F'core_min=' '/^STAGE=S8/{split($2,a," "); s+=a[1]} END{printf "%.4f", s+0}' "$LEDGER")
  echo "PHASE $PHASE RESUMING: cumulative spend so far $SPENT_CORE_MIN core-min (S8: $SPENT_S8_CORE_MIN)" | tee -a "$LEDGER"
fi

memavail_gib () { awk '/MemAvailable/{printf "%.4f", $2/1048576}' /proc/meminfo; }

json_escape () { python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$1"; }

# ============================================================ the stage runner
# $1 stage name     $2 task (run_model|compute_totals|opt|shell)
# $3 dvIndex        $4 dvDelta (STRING, passed as --dvDelta=<v>; see the run script's
#                    CLI note -- argparse's negative-number matcher does NOT accept
#                    exponent notation, so --name=value is the only safe form)
# $5 expected primal timesteps at this stage (for the rule-4 limbs), or 0 to skip
# $6 source of the initial `0` directory (an absolute path), or "-" for none
# $7 controlDict to install (absolute path), or "-" to leave as staged
# $8 extra shell command (task=shell only)
run_stage () {
  local STAGE="$1" TASK="$2" IDX="$3" DELTA="$4" NSTEP="$5" ZERO="$6" CDICT="$7" SHCMD="${8:-}"

  # ---- RUNAWAY GUARD.  Cost constraints are LIFTED (Sanaa 2026-08-25): this is a
  # ---- guard REPORTED TO THE SUPERVISOR, not a budget rigor is trimmed to fit.
  if python3 -c "import sys; sys.exit(0 if $SPENT_CORE_MIN >= $CAP_CORE_MIN else 1)"; then
    echo "RUNAWAY GUARD TRIPPED: $SPENT_CORE_MIN core-min >= cap $CAP_CORE_MIN; stage $STAGE NOT LAUNCHED" | tee -a "$LEDGER"
    return 9
  fi
  if [ "${STAGE:0:2}" = "S8" ] && python3 -c "import sys; sys.exit(0 if $SPENT_S8_CORE_MIN >= $CAP_S8 else 1)"; then
    echo "S8 SUB-CAP TRIPPED: $SPENT_S8_CORE_MIN core-min >= $CAP_S8; stage $STAGE NOT LAUNCHED" | tee -a "$LEDGER"
    return 9
  fi

  # ---- MEMORY IS A PHYSICAL CEILING, read IMMEDIATELY before the launch (§G12R-8).
  local MA; MA=$(memavail_gib)
  if python3 -c "import sys; sys.exit(0 if $MA < $MEMAVAIL_FLOOR_GIB else 1)"; then
    echo "STAGE=$STAGE BLOCKED memavail_GiB=$MA below registered floor $MEMAVAIL_FLOOR_GIB -- NOT LAUNCHED" | tee -a "$LEDGER"
    echo "{\"name\":\"$STAGE\",\"blocked\":true,\"memavail_GiB\":$MA}" >> "$MANIFEST"
    return 8
  fi

  local D="$ROOT/$STAGE" LOG="$ROOT/${STAGE}_${STAMP}.log" NAME="d12r_${STAGE}_${STAMP}"
  sudo -n rm -rf "$D" 2>/dev/null
  cp -a "$ROOT/mesh" "$D" || { echo "ABORT: stage $STAGE copy failed"; return 4; }
  [ "$CDICT" != "-" ] && { cp -a "$CDICT" "$D/system/controlDict" || { echo "ABORT: controlDict"; return 4; }; }
  if [ "$ZERO" != "-" ]; then
    sudo -n rm -rf "$D/0" 2>/dev/null
    cp -a "$ZERO" "$D/0" || { echo "ABORT: stage $STAGE initial-field copy from $ZERO failed"; return 4; }
    sudo -n rm -rf "$D/0/uniform" "$D/0/polyMesh" 2>/dev/null
  fi

  # ---- COLD-START GUARD (CLAUDE.md rule 4): no pre-existing time dir, no processor dirs.
  local COLD=1 ENDT
  ENDT=$(python3 -c "print(repr(round($NSTEP*float('$DELTAT'),8)))" 2>/dev/null)
  for bad in "$D/$ENDT" "$D/0.01"; do
    [ "$bad" = "$D/0" ] && continue
    [ -e "$bad" ] && { echo "COLDSTART FAIL: $bad exists"; COLD=0; }
  done
  [ -n "$(ls -d "$D"/processor* 2>/dev/null)" ] && { echo "COLDSTART FAIL: processor* present"; COLD=0; }
  [ $COLD -eq 1 ] || return 5

  # ---- AGE-GUARD DATUM (CLAUDE.md rule 4).  `0/U` is touched LAST at launch, so it
  # ---- dates the run allowed to produce the answer.  Every field at endTime must be
  # ---- NEWER than this.  The datum is recorded here and the check is made after.
  local AGE_DATUM=""
  if [ -f "$D/0/U" ]; then touch "$D/0/U"; AGE_DATUM=$(stat -c %Y "$D/0/U"); fi

  local T0 T1 WALL rc INSPECT CMD
  if [ "$TASK" = "shell" ]; then
    CMD="$SHCMD"
  else
    CMD="mpirun --allow-run-as-root --bind-to none -np 1 python d12r_run_script.py --task=$TASK --dvIndex=$IDX --dvDelta=$DELTA --out=d12r_${STAGE}.json"
  fi
  T0=$(date -u +%s)
  timeout 7200 sudo -n docker run --name "$NAME" \
      --user 0:0 --cpus=1 --memory=$MEM_LIMIT --memory-swap=$MEM_LIMIT --oom-score-adj=500 \
      -v "$ROOT":/mnt -w "/mnt/$STAGE" "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && $CMD" \
      > "$LOG" 2>&1
  rc=$?
  T1=$(date -u +%s); WALL=$((T1-T0))
  INSPECT=$(sudo -n docker inspect --format '{{.State.ExitCode}}|{{.State.OOMKilled}}' "$NAME" 2>/dev/null)
  sudo -n docker rm "$NAME" >/dev/null 2>&1
  sudo -n chown -R ubuntu:ubuntu "$LOG" "$D" 2>/dev/null

  local CM; CM=$(python3 -c "print(round($WALL/60.0,4))")
  SPENT_CORE_MIN=$(python3 -c "print(round($SPENT_CORE_MIN + $CM, 4))")
  [ "${STAGE:0:2}" = "S8" ] && SPENT_S8_CORE_MIN=$(python3 -c "print(round($SPENT_S8_CORE_MIN + $CM, 4))")
  test -s "$LOG" && touch "$LOG.ok.${STAMP}"

  # ================== THE MANIFEST ROW -- what the comparator will read ==========
  # Written by python so every field is typed and quoted correctly, and so the
  # WHERE-control [RULING-3.3] is read back FROM THE STAGE'S OWN JSON ON DISK rather
  # than echoed from the shell variables this function was called with.  Echoing the
  # arguments back would witness the launcher's INTENT; reading the JSON witnesses
  # what the run actually did.  Those are different claims and only the second one
  # is evidence.
  MANIFEST="$MANIFEST" python3 - "$D" "$STAGE" "$TASK" "$IDX" "$DELTA" "$NSTEP" "$rc" "$INSPECT" \
      "$LOG" "$AGE_DATUM" "$MA" "$CM" "$WALL" "$ENDT" <<'PYEOF'
import json, os, re, sys
(D, stage, task, idx, delta, nstep, rc, inspect, log,
 age_datum, ma, cm, wall, endt) = sys.argv[1:15]
row = {"name": stage, "task": task, "rc": int(rc), "wall_s": int(wall),
       "core_min": float(cm), "memavail_GiB": float(ma),
       "registered_dvIndex": int(idx), "registered_dvDelta": float(delta),
       "endTime": float(endt) if endt not in ("", "None") else None,
       "expected_steps": int(nstep)}
ec, _, oom = inspect.partition("|")
row["docker_exit"] = ec
row["oomkilled"] = oom

# ---- the stage's own JSON, read off disk -------------------------------------
jf = os.path.join(D, "d12r_%s.json" % stage)
if os.path.isfile(jf):
    with open(jf) as f:
        j = json.load(f)
    row["status"] = j.get("status")
    row["obj"] = j.get("obj")
    row["nShapes"] = j.get("nShapes")
    row["dobj_dshape"] = j.get("dobj_dshape")
    row["maxrss_GiB_after_primal"] = j.get("maxrss_GiB_after_primal")
    row["maxrss_GiB_after_adjoint"] = j.get("maxrss_GiB_after_adjoint")
    # ---------------- THE WHERE-CONTROL [RULING-3.3] --------------------------
    # The perturbation the run ACTUALLY APPLIED, taken from the shape vector the
    # run script wrote, NOT from this launcher's arguments.  index, sign and
    # magnitude are DERIVED FROM THE VECTOR, so a units error, a scaler error or
    # an off-by-one in the launcher shows up here as a mismatch the comparator
    # refuses on.  D4-DEF-4 is the reason this block exists.
    sv = j.get("shape")
    row["applied_shape_vector"] = sv
    if isinstance(sv, list):
        nz = [(i, v) for i, v in enumerate(sv) if v != 0.0]
        if len(nz) == 0:
            row["applied_index"], row["applied_sign"], row["applied_magnitude"] = None, "zero", 0.0
        elif len(nz) == 1:
            i, v = nz[0]
            row["applied_index"] = i
            row["applied_sign"] = "plus" if v > 0 else "minus"
            row["applied_magnitude"] = abs(v)
        else:
            # more than one non-zero component is NOT a partial derivative; recorded
            # as-is so the comparator refuses rather than the launcher hiding it
            row["applied_index"] = [i for i, _ in nz]
            row["applied_sign"] = "multiple"
            row["applied_magnitude"] = None
    row["applied_dvIndex_reported"] = j.get("dvIndex")
    row["applied_dvDelta_reported"] = j.get("dvDelta")
else:
    row["status"] = None

# ---- the log, read off disk: rule-4 limbs ------------------------------------
row["end_line_present"] = False
row["last_time"] = None
row["time_line_count"] = 0
row["execution_time_count"] = 0
row["obj_from_log"] = None
if os.path.isfile(log):
    with open(log, errors="replace") as f:
        txt = f.read()
    row["end_line_present"] = bool(re.search(r"^End\b", txt, re.M))
    times = re.findall(r"^Time = ([0-9.eE+-]+)", txt, re.M)
    row["time_line_count"] = len(times)
    if times:
        try:
            row["last_time"] = float(times[-1])
        except ValueError:
            pass
    row["execution_time_count"] = len(re.findall(r"ExecutionTime", txt))
    avgs = re.findall(r"average:\s*([0-9.eE+-]+)", txt)
    if avgs:
        try:
            row["obj_from_log"] = float(avgs[-1])
        except ValueError:
            pass

# ---- AGE GUARD (CLAUDE.md rule 4) --------------------------------------------
# Every field written at endTime must be NEWER than the case's own `0/U` datum,
# which was touched last at launch.  A stage where this fails is carrying a field
# it did not produce.
row["age_guard_ok"] = None
row["age_guard_detail"] = ""
if age_datum:
    try:
        datum = int(age_datum)
        et = row.get("endTime")
        cand = []
        if et is not None:
            for nm in (repr(et), ("%g" % et), str(et)):
                p = os.path.join(D, nm)
                if os.path.isdir(p):
                    cand.append(p)
                    break
        if cand:
            d0 = cand[0]
            fields = [os.path.join(d0, x) for x in os.listdir(d0)
                      if os.path.isfile(os.path.join(d0, x))]
            if fields:
                older = [os.path.basename(p) for p in fields
                         if int(os.path.getmtime(p)) < datum]
                row["age_guard_ok"] = (len(older) == 0)
                row["age_guard_detail"] = ("all %d fields at endTime newer than 0/U"
                                           % len(fields)) if not older else \
                                          ("STALE: " + ",".join(sorted(older)))
            else:
                row["age_guard_detail"] = "endTime dir present but holds no field files"
        else:
            row["age_guard_detail"] = "no endTime directory on disk"
    except Exception as exc:                                   # noqa: BLE001
        row["age_guard_detail"] = "age guard could not be evaluated: %r" % (exc,)

row["coldstart_ok"] = True     # asserted by the shell before launch; false => no row
with open(os.environ["MANIFEST"], "a") as f:
    f.write(json.dumps(row, sort_keys=True) + "\n")
print("STAGE=%s TASK=%s rc=%s wall_s=%s core_min=%s memavail=%s applied_index=%r "
      "applied_sign=%s applied_mag=%r inspect=[%s]"
      % (stage, task, rc, wall, cm, ma, row.get("applied_index"),
         row.get("applied_sign"), row.get("applied_magnitude"), inspect))
PYEOF
  tail -1 "$MANIFEST" >/dev/null 2>&1
  grep -a "^STAGE=$STAGE " /dev/null 2>/dev/null
  echo "STAGE=$STAGE TASK=$TASK rc=$rc wall_s=$WALL ranks=1 core_min=$CM memavail_GiB=$MA inspect=[$INSPECT] log=$(basename "$LOG")" | tee -a "$LEDGER"
  echo "SPENT_CORE_MIN=$SPENT_CORE_MIN of cap $CAP_CORE_MIN" | tee -a "$LEDGER"
  return $rc
}

# ============================================================ FIELD_B manifest
# §3.1: FIELD_B is the frozen initial condition of EVERY graded run in S3-S8.  Its
# per-file md5 manifest is written at creation and RE-ASSERTED before each stage; a
# mismatch is a REFUSAL, not a warning.
field_b_write_manifest () {
  ( cd "$ROOT/FIELD_B" && find . -type f -exec md5sum {} \; | sort -k2 ) > "$ROOT/FIELD_B.md5"
  echo "FIELD_B_MANIFEST_WRITTEN files=$(wc -l < "$ROOT/FIELD_B.md5")" | tee -a "$LEDGER"
}
field_b_assert () {
  [ -f "$ROOT/FIELD_B.md5" ] || { echo "ABORT: FIELD_B manifest absent"; exit 7; }
  local now; now=$(mktemp)
  ( cd "$ROOT/FIELD_B" && find . -type f -exec md5sum {} \; | sort -k2 ) > "$now"
  if ! diff -q "$ROOT/FIELD_B.md5" "$now" >/dev/null; then
    echo "REFUSE: FIELD_B md5 manifest MISMATCH -- the frozen initial condition changed" | tee -a "$LEDGER"
    diff "$ROOT/FIELD_B.md5" "$now" | head -20 | tee -a "$LEDGER"
    rm -f "$now"; exit 7
  fi
  rm -f "$now"
}

# ============================================================ PHASE 1
if [ "$PHASE" = "1" ]; then
  # ---- S0: mesh, once
  mkdir -p "$ROOT/mesh"
  cp -a "$TUT"/0_orig "$TUT"/FFD "$TUT"/constant "$TUT"/system "$TUT"/genMesh.py \
        "$TUT"/runPrimalSimple.py "$ROOT/mesh/" || { echo "ABORT: tutorial copy"; exit 1; }
  cp -a "$RUNPY" "$ROOT/mesh/" || { echo "ABORT: runscript copy"; exit 1; }
  cp -a "$TUT"/system/fvSchemes_pimple "$ROOT/mesh/system/fvSchemes"
  cp -a "$TUT"/system/fvSolution_pimple "$ROOT/mesh/system/fvSolution"
  MA=$(memavail_gib)
  T0=$(date -u +%s)
  timeout 900 sudo -n docker run --name "d12r_S0_${STAMP}" --user 0:0 --cpus=1 \
      -v "$ROOT":/mnt -w /mnt/mesh "$IMG" bash -lc \
      "source /home/dafoamuser/dafoam/loadDAFoam.sh && python genMesh.py && \
       plot3dToFoam -noBlank volumeMesh.xyz && autoPatch 30 -overwrite && \
       createPatch -overwrite && renumberMesh -overwrite && checkMesh -constant | tail -30" \
      > "$ROOT/S0_${STAMP}.log" 2>&1
  mrc=$?; T1=$(date -u +%s)
  sudo -n docker rm "d12r_S0_${STAMP}" >/dev/null 2>&1
  sudo -n chown -R ubuntu:ubuntu "$ROOT" 2>/dev/null
  [ $mrc -eq 0 ] || { echo "ABORT: S0 mesh rc=$mrc"; exit 1; }
  SPENT_CORE_MIN=$(python3 -c "print(round($((T1-T0))/60.0,4))")
  grep -a "^Global Cells\|^nCells" "$ROOT/S0_${STAMP}.log" | tee -a "$LEDGER"
  echo "STAGE=S0 TASK=mesh rc=0 wall_s=$((T1-T0)) ranks=1 core_min=$SPENT_CORE_MIN memavail_GiB=$MA" | tee -a "$LEDGER"
  sudo -n rm -rf "$ROOT/mesh/0" "$ROOT/mesh/processor"* 2>/dev/null

  # ---- S1: the tutorial's own spin-up chain, AT np=1 (registered).  Because np=1
  # ---- there are no processor dirs and no reconstructPar is needed -- the tutorial's
  # ---- own script runs this at np=4; the reduction to np=1 is the REGISTERED
  # ---- decomposition and is not a convenience.
  run_stage S1a shell 0 0.0 500 "$ROOT/mesh/0_orig" "$TUT/system/controlDict_simple" \
    "cp -r system/fvSchemes_simple system/fvSchemes && cp -r system/fvSolution_simple system/fvSolution && potentialFoam && mpirun --allow-run-as-root --bind-to none -np 1 python runPrimalSimple.py" \
    || echo "STAGE S1a NONZERO rc"
  [ -d "$ROOT/S1a/500" ] || { echo "ABORT: S1a produced no 500 directory"; exit 1; }
  run_stage S1b run_model 0 0.0 200 "$ROOT/S1a/500" "$TUT/system/controlDict_pimple_long" "" \
    || echo "STAGE S1b NONZERO rc"
  [ -d "$ROOT/S1b/10" ] || { echo "ABORT: S1b produced no t=10 directory (FIELD_A)"; exit 1; }
  cp -a "$ROOT/S1b/10" "$ROOT/FIELD_A"
  sudo -n rm -rf "$ROOT/FIELD_A/uniform" "$ROOT/FIELD_A/polyMesh" 2>/dev/null
  echo "FIELD_A_CREATED from S1b/10" | tee -a "$LEDGER"

  # ---- S2: the 2,400-step diagnostic at deltaT 1e-2 from FIELD_A
  python3 - "$TUT/system/controlDict_pimple" "$ROOT/cd_S2" "$(python3 -c "print($S2_STEPS*float('$DELTAT'))")" <<'PY'
import re, sys
src, dst, endt = sys.argv[1], sys.argv[2], sys.argv[3]
t = open(src).read()
t = re.sub(r"^endTime\s+\S+;", "endTime         %s;" % endt, t, flags=re.M)
open(dst, "w").write(t)
PY
  run_stage S2 run_model 0 0.0 $S2_STEPS "$ROOT/FIELD_A" "$ROOT/cd_S2" "" || echo "STAGE S2 NONZERO rc"

  # ---- FIELD_B := the S2 field at t = 3.00 (the first 300 steps are the registered
  # ---- transient discard), stripped, and FROZEN by md5 manifest.
  FB_T=$(python3 -c "print(repr(round($TRANSIENT_DISCARD*float('$DELTAT'),8)))")
  SRCB=""
  for nm in "$FB_T" "$(python3 -c "print('%g' % $FB_T)")"; do
    [ -d "$ROOT/S2/$nm" ] && { SRCB="$ROOT/S2/$nm"; break; }
  done
  [ -n "$SRCB" ] || { echo "ABORT: S2 has no t=$FB_T directory for FIELD_B"; exit 1; }
  cp -a "$SRCB" "$ROOT/FIELD_B"
  sudo -n rm -rf "$ROOT/FIELD_B/uniform" "$ROOT/FIELD_B/polyMesh" 2>/dev/null
  echo "FIELD_B_CREATED from $SRCB" | tee -a "$LEDGER"
  field_b_write_manifest

  # ---- the graded window's controlDict: W steps from FIELD_B
  python3 - "$TUT/system/controlDict_pimple" "$ROOT/cd_W" "$(python3 -c "print($W_STEPS*float('$DELTAT'))")" <<'PY'
import re, sys
src, dst, endt = sys.argv[1], sys.argv[2], sys.argv[3]
t = open(src).read()
t = re.sub(r"^endTime\s+\S+;", "endTime         %s;" % endt, t, flags=re.M)
open(dst, "w").write(t)
PY

  # ---- S3: delta_repeat, three identical run_model runs over W from FIELD_B
  for r in 1 2 3; do
    field_b_assert
    run_stage "S3_r$r" run_model 0 0.0 $W_STEPS "$ROOT/FIELD_B" "$ROOT/cd_W" "" || echo "STAGE S3_r$r NONZERO rc"
  done

  # ---- S3b: delta_pert, MEASURED for THIS configuration [RULING 4 / RULINGS §4].
  # ---- NEVER imported from D12-F': the floor is component-dependent, so it is a
  # ---- property of a configuration exactly as DAFOAM_CHARTER.md §5 says an FD
  # ---- reference is.  Two probe steps A DECADE APART on every component; the
  # ---- comparator solves the two-point system MODEL-FREE (it never reads the
  # ---- adjoint) to separate the linear response from the floor.
  for i in $(seq 0 $((NSHAPES_EXPECTED-1))); do
    for hs in "a:$DPERT_HA" "b:$DPERT_HB"; do
      TAG="${hs%%:*}"; H="${hs##*:}"
      field_b_assert
      run_stage "S3b_c${i}_${TAG}p" run_model "$i" "$H"  $W_STEPS "$ROOT/FIELD_B" "$ROOT/cd_W" "" || echo "STAGE S3b_c${i}_${TAG}p NONZERO rc"
      field_b_assert
      run_stage "S3b_c${i}_${TAG}m" run_model "$i" "-$H" $W_STEPS "$ROOT/FIELD_B" "$ROOT/cd_W" "" || echo "STAGE S3b_c${i}_${TAG}m NONZERO rc"
    done
  done

  # ---- S4: checkpoint envelope, compute_totals at n in {20,40,80}, TWO runs each
  for n in $ENV_STEPS; do
    python3 - "$TUT/system/controlDict_pimple" "$ROOT/cd_n$n" "$(python3 -c "print($n*float('$DELTAT'))")" <<'PY'
import re, sys
src, dst, endt = sys.argv[1], sys.argv[2], sys.argv[3]
t = open(src).read()
t = re.sub(r"^endTime\s+\S+;", "endTime         %s;" % endt, t, flags=re.M)
open(dst, "w").write(t)
PY
    for r in 1 2; do
      field_b_assert
      run_stage "S4_n${n}_r$r" compute_totals 0 0.0 $n "$ROOT/FIELD_B" "$ROOT/cd_n$n" "" || echo "STAGE S4_n${n}_r$r NONZERO rc"
    done
  done

  # ---- S5: the adjoint at the graded window
  field_b_assert
  run_stage S5 compute_totals 0 0.0 $W_STEPS "$ROOT/FIELD_B" "$ROOT/cd_W" "" || echo "STAGE S5 NONZERO rc"

  # ---- S7: the plant, and its unplanted clean-copy discrimination control
  field_b_assert
  run_stage S7_plant run_model 0 1.234e-03 $W_STEPS "$ROOT/FIELD_B" "$ROOT/cd_W" "" || echo "STAGE S7_plant NONZERO rc"
  field_b_assert
  run_stage S7_clean run_model 0 0.0       $W_STEPS "$ROOT/FIELD_B" "$ROOT/cd_W" "" || echo "STAGE S7_clean NONZERO rc"

  echo "PHASE1_COMPLETE spent=$SPENT_CORE_MIN core-min" | tee -a "$LEDGER"
  echo "NEXT: run the FROZEN COMPARATOR in --plan mode to produce step_plan.json, then --phase 2." | tee -a "$LEDGER"
  echo "  python3 $GRADEPY --manifest $MANIFEST --root $ROOT --plan" | tee -a "$LEDGER"
  exit 0
fi

# ============================================================ PHASE 2
# The sweep.  THE STEP LIST IS READ FROM step_plan.json, WHICH THE FROZEN COMPARATOR
# WROTE.  This launcher does not compute it, does not round it and does not choose
# among the steps [RULING-3.3].
if [ "$PHASE" = "2" ]; then
  PLAN="$ROOT/step_plan.json"
  [ -f "$PLAN" ] || { echo "ABORT: $PLAN absent -- run the comparator in --plan mode first"; exit 1; }
  PLAN_MD5=$(md5sum "$PLAN" | cut -d' ' -f1)
  echo "STEP_PLAN_MD5=$PLAN_MD5 (written by the comparator, not by this launcher)" | tee -a "$LEDGER"
  ADMISSIBLE=$(python3 -c "import json;print(json.load(open('$PLAN'))['admissible'])")
  if [ "$ADMISSIBLE" != "True" ]; then
    echo "NO ADMISSIBLE FD STEP AT THIS WINDOW -- the comparator's registered G12R-4 branch fired." | tee -a "$LEDGER"
    echo "Phase 2 is NOT LAUNCHED.  That is a RESULT, not a failure (see the pre-registration)." | tee -a "$LEDGER"
    exit 0
  fi
  STEPS=$(python3 -c "import json;print(' '.join(repr(s) for s in json.load(open('$PLAN'))['steps']))")
  echo "STEPS_FROM_PLAN=$STEPS" | tee -a "$LEDGER"
  k=0
  for H in $STEPS; do
    k=$((k+1))
    field_b_assert
    run_stage "S6_s${k}_p" run_model 0 "$H"  $W_STEPS "$ROOT/FIELD_B" "$ROOT/cd_W" "" || echo "STAGE S6_s${k}_p NONZERO rc"
    field_b_assert
    run_stage "S6_s${k}_m" run_model 0 "-$H" $W_STEPS "$ROOT/FIELD_B" "$ROOT/cd_W" "" || echo "STAGE S6_s${k}_m NONZERO rc"
  done
  echo "PHASE2_COMPLETE spent=$SPENT_CORE_MIN core-min" | tee -a "$LEDGER"
  echo "NEXT: comparator --plan2 to fix h* positionally over the plateau, then --phase 3." | tee -a "$LEDGER"
  exit 0
fi

# ============================================================ PHASE 3
# The trivial baseline at 10*h*, the 4-component vector FD at h*, and the
# optimisation.  h* COMES FROM THE COMPARATOR, chosen POSITIONALLY over the plateau
# WITHOUT READING THE ADJOINT [RULING-3.3].
if [ "$PHASE" = "3" ]; then
  PLAN2="$ROOT/step_plan2.json"
  [ -f "$PLAN2" ] || { echo "ABORT: $PLAN2 absent -- run the comparator in --plan2 mode first"; exit 1; }
  HSTAR=$(python3 -c "import json;print(repr(json.load(open('$PLAN2'))['h_star']))")
  HWRONG=$(python3 -c "import json;print(repr(json.load(open('$PLAN2'))['h_wrong']))")
  OPT_OK=$(python3 -c "import json;print(json.load(open('$PLAN2'))['optimisation_authorised'])")
  echo "H_STAR=$HSTAR H_WRONG=$HWRONG OPTIMISATION_AUTHORISED=$OPT_OK (all from the comparator)" | tee -a "$LEDGER"

  # S6b -- the registered trivial baseline at a DELIBERATELY WRONG step
  field_b_assert; run_stage S6b_p run_model 0 "$HWRONG"  $W_STEPS "$ROOT/FIELD_B" "$ROOT/cd_W" ""
  field_b_assert; run_stage S6b_m run_model 0 "-$HWRONG" $W_STEPS "$ROOT/FIELD_B" "$ROOT/cd_W" ""

  # S6c -- the 4-component vector FD at h*
  for i in $(seq 0 $((NSHAPES_EXPECTED-1))); do
    field_b_assert; run_stage "S6c_c${i}_p" run_model "$i" "$HSTAR"  $W_STEPS "$ROOT/FIELD_B" "$ROOT/cd_W" ""
    field_b_assert; run_stage "S6c_c${i}_m" run_model "$i" "-$HSTAR" $W_STEPS "$ROOT/FIELD_B" "$ROOT/cd_W" ""
  done

  # S8 -- the optimisation, ONLY if the comparator authorised it (G12R-11)
  if [ "$OPT_OK" = "True" ]; then
    field_b_assert
    run_stage S8 opt 0 0.0 $W_STEPS "$ROOT/FIELD_B" "$ROOT/cd_W" "" || echo "STAGE S8 NONZERO rc"
  else
    echo "S8 NOT LAUNCHED: the comparator did not authorise the optimisation (G12R-11)." | tee -a "$LEDGER"
    echo "D12's optimisation is NOT A RESULT, and the reason is in the grade output." | tee -a "$LEDGER"
  fi
  echo "PHASE3_COMPLETE spent=$SPENT_CORE_MIN core-min" | tee -a "$LEDGER"
  echo "TOTAL_SPENT_CORE_MIN=$SPENT_CORE_MIN CAP=$CAP_CORE_MIN" | tee -a "$LEDGER"
  echo "FINISHED_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LEDGER"
  exit 0
fi
usage
