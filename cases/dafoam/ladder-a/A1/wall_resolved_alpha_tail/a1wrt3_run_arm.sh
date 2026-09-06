#!/usr/bin/env bash
# =============================================================================
# A1WRT3 -- THE HOST-SIDE ARM LAUNCHER.
# `A1WRT3_SUCCESSOR_DRAFT.md` sections 4, 6 and 7.
#
# LAUNCH_ENABLED IS 0 AND NO LANE RAISES IT.  Raising it is the enqueue act and
# it belongs to the `dafoam-supervisor` (A1WRT2 section 13.1).  This file
# refuses to start a container while it is 0.  *"That it would trip no gate is
# a reason to say it, not to do it."*
#
# THE TWO-LAYER CONTAINER COMMAND IS RESTORED.  The outer layer (this file)
# sources `loadDAFoam.sh` and invokes `bash /run_root/cmd.sh`; the inner layer
# (`a1wrt3_cmd.sh`) does the preflight, THE TRANSLATION and the rc discipline.
# A1WRT2 transcribed the innermost command, deleted `cmd.sh`, and passed
# `-e OMP_NUM_THREADS=1` AND NOTHING ELSE against a producer that reads four
# fatal names from `os.environ`.  It died in four seconds.
# =============================================================================
set -uo pipefail

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ITEM="A1WRT3"
RUN_ROOT="/home/ubuntu/certonomous-runs/A1WRT3"
LEDGER="$RUN_ROOT/ledger.txt"
MANIFEST_PATH="$RUN_ROOT/MANIFEST.json"
INSTR="$BASE/a1wrt3_instruments.py"
GRADER="$BASE/a1wrt3_grade.py"
CMD_SRC="$BASE/a1wrt3_cmd.sh"

IMG="dafoam-idwarp-rot:v1"
DAFOAM_LOADER="/home/dafoamuser/dafoam/loadDAFoam.sh"

# Section 7.3.  REGISTERED CONSTANTS, and the in-container deadline is the one
# that survives the death of every agent.
declare -A ARM_CAP=([SEAM]=10.0 [TAIL]=675.0)
declare -A ARM_TMO=([SEAM]=900 [TAIL]=41400)
declare -A ARM_ALPHAS=([SEAM]="12" [TAIL]="13 14 15 16 17 18")
ITEM_CEILING=685.0
PRIMAL_TOL="1.0e-8"

# =============================================================================
# LAUNCH_ENABLED -- SECTION 11 ITEM 10.  THE SUPERVISOR'S LEVER, NOT A LANE'S.
# =============================================================================
LAUNCH_ENABLED=0

die() { echo "${ITEM}_FATAL $*" >&2; exit "${2:-1}"; }

# =============================================================================
# ===  THE SINGLE `-e` ARRAY.  SECTION 4.1, AND IT IS A CONSTRUCTION        ===
# ===  REQUIREMENT RATHER THAN AN IMPLEMENTATION DETAIL.                    ===
# =============================================================================
# THIS ARRAY IS BUILT ONCE.  `G-ENVSEAM` clause 1 consumes it by expanding
# `"${DOCKER_ENV[@]}"`; `docker run` consumes it by expanding
# `"${DOCKER_ENV[@]}"`.  THE SAME ARRAY, IN THE SAME SHELL, AT TWO EXPANSION
# POINTS -- NOT A LIST THE GATE KEEPS BESIDE A LIST THE LAUNCHER KEEPS.
#
# WHY THAT IS THE WHOLE POINT: two lists drift, and the gate would then
# certify a correspondence between two things NEITHER OF WHICH IS WHAT RUNS --
# the L-493 wrong-route shape in its most literal form.  There is no second
# list here to drift from, and `a1wrt3_instruments.py` carries no literal
# environment-name list either: it reads the `AOA_*` half out of
# `a1wrt3_cmd.sh` between that file's registered translation markers.
#
# AND THE IDENTITY IS PINNED ACROSS THE GAP, NOT ASSUMED.  `env_sig` is taken
# immediately BEFORE the gate and again immediately BEFORE `docker run`, and
# the two must be equal.  Same-variable is not the same claim as
# same-at-both-moments; an edit between the two expansions would otherwise let
# a gated array and a launched array differ while every line still read
# `"${DOCKER_ENV[@]}"`.
# -----------------------------------------------------------------------------
build_docker_env() {
  local arm="$1"
  DOCKER_ENV=(
    -e "OMP_NUM_THREADS=1"
    -e "A1WRT3_ARM=$arm"
    -e "A1WRT3_MODE=CONTINUED"
    -e "A1WRT3_ALPHAS=${ARM_ALPHAS[$arm]}"
    -e "A1WRT3_TOL=$PRIMAL_TOL"
    -e "A1WRT3_TMO=${ARM_TMO[$arm]}"
  )
}

env_sig() {
  # A stable signature of the array's exact contents, in order.
  printf '%s\n' "${DOCKER_ENV[@]}" | md5sum | cut -d' ' -f1
}

# =============================================================================
# G-ENVSEAM CLAUSE 1 -- HOST-SIDE, STATIC, **BEFORE THE CONTAINER STARTS**.
#
# Any fatal name the producer reads and the container will not receive =>
# BLOCKED, and the container does not start.  Section 8.2's `P6` predicts this
# returns CLEAN on the first attempt; a MISS means the repair is incomplete and
# THE ITEM STOPS AT `BLOCKED` BEFORE SPENDING ANYTHING, which is the entire
# purpose of putting the gate in front of the container rather than behind it.
# =============================================================================
gate_envseam_clause1() {
  local producer="$1" cmd_sh="$2" rc out
  out="$(python3 "$INSTR" --gate-envseam \
          --producer "$producer" \
          --cmd-sh "$cmd_sh" \
          --docker-env "${DOCKER_ENV[@]}" 2>&1)"
  rc=$?
  printf '%s\n' "$out"
  return $rc
}

# =============================================================================
# THE MANIFEST -- SECTION 11 ITEM 6.
#
# **IT DECLARES THE CONTAINER'S ENVIRONMENT, NOT THE LAUNCHER'S.**
# A1WRT2's `env_declared` listed `A1WRT2_RUN_ROOT`, `A1WRT2_STATUS_DIR` and
# `BASH_SOURCE` -- THE LAUNCHER'S OWN SHELL ENVIRONMENT, THE WRONG SIDE OF THE
# BOUNDARY.  That is `A1WRT2-DEF-ENVSEAM` showing up a second time in a second
# instrument: the same blindness as the unbound-variable guard, which read the
# launcher's shell while the defect lived in a python process across a
# `docker run`.  DECLARE WHAT CROSSES THE BOUNDARY.
#
# So `env_declared` here has three parts and every one of them is EXTRACTED,
# never re-typed:
#   `docker_e_array`     -- the `-e` array itself, verbatim, as passed;
#   `container_supplied` -- name -> value, parsed out of that same array;
#   `aoa_translation`    -- the `AOA_*` names `a1wrt3_cmd.sh`'s C13 block sets,
#                           read out of the staged `cmd.sh` that will run;
#   `producer_fatal_reads` -- what the producer will actually consume.
# A reader of this manifest can reconstruct BOTH SIDES OF THE SEAM from it.
# That was impossible from A1WRT2's manifest, and the crash is the proof.
# =============================================================================
write_manifest() {
  local arm="$1" dig="$2" warp="$3" sig="$4"
  mkdir -p "$RUN_ROOT"
  python3 - "$RUN_ROOT" "$arm" "$IMG" "$dig" "$warp" "$sig" "$INSTR" \
           "${DOCKER_ENV[@]}" > "$MANIFEST_PATH" <<'PYEOF'
import hashlib, importlib.util, json, os, sys
run_root, arm, img, dig, warp, sig, instr = sys.argv[1:8]
docker_env = sys.argv[8:]

spec = importlib.util.spec_from_file_location("a1wrt3_instruments", instr)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def md5(p):
    with open(p, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()

# The OBSERVED side of G-FREEZE: md5s measured off the STAGED files, IN THE RUN
# ROOT, never off the item directory.  Hashing the item directory would certify
# a file the container never saw -- a freeze check on the wrong copy.
inst = {}
for name in ("runScript.py", "cmd.sh", "run_arm.sh"):
    p = os.path.join(run_root, name)
    if os.path.exists(p):
        inst[name] = md5(p)

supplied = mod.supplied_from_docker_env(docker_env)
cmd_sh = os.path.join(run_root, "cmd.sh")
xlat = mod.translation_names(cmd_sh) if os.path.exists(cmd_sh) else None
prod = os.path.join(run_root, "runScript.py")
if os.path.exists(prod):
    reads, unres = mod.extract_env_reads(prod)
    fatal = sorted({r["name"] for r in reads if r["kind"] == "FATAL"})
    defaulted = sorted({r["name"] for r in reads if r["kind"] == "DEFAULTED"})
else:
    fatal = defaulted = None

sys.stdout.write(json.dumps({
    "item": "A1WRT3", "arm": arm, "run_root": run_root,
    "image": img,
    # MEASURED, never copied from the registered pin.  "UNMEASURED" here makes
    # G-IMG refuse at exit 4; it must never read as agreement.
    "image_digest": dig, "libidwarp_md5": warp,
    "instruments": inst,
    "env_declared": {
        "_what": ("THE CONTAINER'S environment, both sides of the seam. "
                  "A1WRT2 declared the LAUNCHER'S shell variables here and "
                  "that was the same defect in a second instrument."),
        "docker_e_array": docker_env,
        "docker_e_array_md5": sig,
        "container_supplied": supplied,
        "aoa_translation": xlat,
        "producer_fatal_reads": fatal,
        "producer_defaulted_reads": defaulted,
    },
}, indent=1, sort_keys=True) + "\n")
PYEOF
  test -s "$MANIFEST_PATH" || die "manifest not written to $MANIFEST_PATH" 2
  echo "${ITEM}_MANIFEST written $MANIFEST_PATH (env_sig=$sig)" >&2
}

append_ledger_row() {
  local arm="$1" rc="$2" wall="$3" ranks="$4" cap="$5" cm
  mkdir -p "$RUN_ROOT"
  cm="$(python3 -c "print('%.3f' % ($wall * $ranks / 60.0))")"
  echo "ARM=$arm ROW=PATCHED IMG=$IMG rc=$rc wall_s=$wall ranks=$ranks core_min=$cm cap_core_min=$cap mode=CONTINUED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$LEDGER"
  echo "${ITEM}_LEDGER_ROW arm=$arm rc=$rc core_min=$cm cap=$cap"
}

# =============================================================================
# THE CEILING GUARD, WITH THE `A1WRT:296-304` UNMEASURED-REFUSAL LIMB CARRIED
# UNWEAKENED.  It sums THIS ITEM'S OWN ledger spend, adds the next arm's cap,
# and REFUSES BEFORE THAT ARM LAUNCHES if the projection crosses 685.0.
#
# AN UNPARSEABLE LEDGER REFUSES RATHER THAN ASSUMING ZERO, because a zero that
# means "could not read" is a planted zero (`CLAUDE.md` rule 3) and it would
# read as the maximum possible headroom at exactly the moment the reader is
# least entitled to a number.
# =============================================================================
ceiling_guard() {
  local arm="$1" out rc
  out="$(python3 "$GRADER" --ceiling-precond "$RUN_ROOT" "$arm" 2>&1)"; rc=$?
  printf '%s\n' "$out"
  return $rc
}

# =============================================================================
# THE SEAM PRECONDITION -- SECTION 6, AND IT IS THE ITEM'S SPINE.
# `TAIL` DOES NOT LAUNCH UNTIL `SEAM` HAS PRODUCED A VERDICT.  675 core-min
# does not move until 10 has spoken.
#
# AND AN UNRESOLVED SEAM IS NOT A PERMISSION.  `SEAM` UNRESOLVED refuses at the
# same rc=7 with reason `SEAM-UNRESOLVED`, DISTINCT from `SEAM-GATE-FAIL`: an
# unresolved prediction *"is not a permission and is not a refusal either; it
# is a hole where a measurement should be."*
# =============================================================================
seam_precondition_guard() {
  local out rc
  out="$(python3 "$GRADER" --seam-precond "$RUN_ROOT" 2>&1)"; rc=$?
  printf '%s\n' "$out"
  if [ "$rc" -ne 0 ]; then
    echo "${ITEM}_TAIL_REFUSED rc=7 reason=$(printf '%s' "$out" | sed -n 's/.*REASON=\([A-Z-]*\).*/\1/p' | tail -1)"
    return 7
  fi
  return 0
}

measure_image_pins() {
  local img="$1" dig warp
  dig="$(docker image inspect --format '{{index .RepoDigests 0}}' "$img" 2>/dev/null | sed 's/^.*@//')"
  [ -n "$dig" ] || dig="$(docker image inspect --format '{{.Id}}' "$img" 2>/dev/null)"
  [ -n "$dig" ] || dig="UNMEASURED"
  warp="$(docker run --rm --entrypoint /bin/bash "$img" -lc \
          "source $DAFOAM_LOADER >/dev/null 2>&1; md5sum \$(python -c 'import idwarp,os;print(os.path.dirname(idwarp.__file__))')/libidwarp.so 2>/dev/null | cut -d' ' -f1" 2>/dev/null)"
  [ -n "$warp" ] || warp="UNMEASURED"
  echo "$dig $warp"
}

refuse_unmeasured_pins() {
  local arm="$1" dig="$2" warp="$3"
  [ "$dig" != "UNMEASURED" ] || die "G-IMG: image digest UNMEASURED for arm $arm -- an unmeasured pin never reads as agreement" 4
  [ "$warp" != "UNMEASURED" ] || die "G-IMG: libidwarp md5 UNMEASURED for arm $arm" 4
}

# =============================================================================
# THE ARM BODY
# =============================================================================
run_arm() {
  local arm="$1" rc t0 t1 sig_gate sig_launch dig_warp
  local arm_case="$RUN_ROOT/$arm/case" arm_out="$RUN_ROOT/$arm/out"

  case "$arm" in SEAM|TAIL) ;; *) die "unknown arm '$arm'" 2 ;; esac

  [ "$LAUNCH_ENABLED" = "1" ] || die \
    "LAUNCH_ENABLED=0 -- raising it is the enqueue act and it is the dafoam-supervisor's. No lane raises it." 3

  if [ "$arm" = "TAIL" ]; then
    seam_precondition_guard || exit 7
  fi
  ceiling_guard "$arm" || exit 6

  mkdir -p "$arm_out"
  test -f "$RUN_ROOT/cmd.sh" || die "staged cmd.sh absent -- run a1wrt3_stage.py first" 2
  test -f "$RUN_ROOT/runScript.py" || die "staged producer absent" 2

  # ---- THE ARRAY IS BUILT ONCE, HERE. ------------------------------------
  build_docker_env "$arm"
  sig_gate="$(env_sig)"

  # ---- G-ENVSEAM CLAUSE 1, ON THAT ARRAY, BEFORE ANYTHING STARTS ---------
  if ! gate_envseam_clause1 "$RUN_ROOT/runScript.py" "$RUN_ROOT/cmd.sh"; then
    echo "${ITEM}_GATE G-ENVSEAM BLOCKED -- THE CONTAINER DOES NOT START. Zero compute spent."
    exit 9
  fi

  dig_warp="$(measure_image_pins "$IMG")"
  refuse_unmeasured_pins "$arm" "${dig_warp% *}" "${dig_warp#* }"
  write_manifest "$arm" "${dig_warp% *}" "${dig_warp#* }" "$sig_gate"

  # ---- THE IDENTITY PIN ACROSS THE GAP ----------------------------------
  sig_launch="$(env_sig)"
  [ "$sig_launch" = "$sig_gate" ] || die \
    "the -e array CHANGED between G-ENVSEAM clause 1 ($sig_gate) and docker run ($sig_launch). The gated array and the launched array are not the same array." 9

  t0="$(date +%s)"
  # ---- THE TWO-LAYER CONTAINER COMMAND, RESTORED -------------------------
  # The outer layer sources the loader (whose absence made A1WRT2's 2026-09-04
  # arm bodies unable to start a solver at all) and hands control to the inner
  # layer.  ONLY `cmd.sh` redirects the producer; the container's own stdout is
  # `container.log`, and G-WALLTREAT's count-pinned presence assertion reads it.
  timeout "${ARM_TMO[$arm]}" docker run --rm --user 0:0 --cpuset-cpus="0" --memory=8g \
    "${DOCKER_ENV[@]}" \
    -v "$arm_case:/mnt" -v "$RUN_ROOT:/run_root" \
    "$IMG" /bin/bash -lc "source $DAFOAM_LOADER && bash /run_root/cmd.sh" \
    > "$arm_out/container.log" 2>&1
  rc=$?
  # THE PRODUCER'S OWN rc, PROPAGATED BY `cmd.sh`'s C17', RECORDED HERE, AND
  # NEVER RECOMPUTED FROM MARKERS.
  echo "$rc" > "$arm_out/rc"
  t1="$(date +%s)"
  append_ledger_row "$arm" "$rc" "$((t1 - t0))" 1 "${ARM_CAP[$arm]}"
  return 0
}

usage() { echo "usage: $0 --arm {SEAM|TAIL}" >&2; exit 2; }

# =============================================================================
# THE MAIN GUARD, AND IT IS PART OF THE SECTION 4.1 DISCIPLINE.
#
# `a1wrt3_selftest.py` SOURCES this file to obtain `build_docker_env` and then
# reads the array THIS LAUNCHER BUILDS.  Control `E2` therefore drives
# G-ENVSEAM clause 1 against THE REAL LAUNCHER'S REAL ARRAY -- not against an
# array the control types out for itself, which would be the second list
# section 4.1 rejects, reappearing inside the control that is supposed to prove
# there is no second list.
#
# Sourcing must therefore not launch anything, and this guard is what makes
# that true.
# =============================================================================
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  ARM=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --arm) ARM="${2:-}"; shift 2 ;;
      *) usage ;;
    esac
  done
  [ -n "$ARM" ] || usage
  run_arm "$ARM"
fi
