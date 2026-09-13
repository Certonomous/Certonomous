#!/usr/bin/env bash
# ===========================================================================
# d6r2c_fm12_run_arm.sh -- LAUNCHER for arm FM12 (the comparison at matched lift)
# ===========================================================================
#
# Registered by PREREGISTRATION_FM12_MATCHED_LIFT_PROVENANCE.md sections 2, 5, 6, 7
# and 8, and IN THE SAME COMMIT AS THAT DOCUMENT, BEFORE ANY CONTAINER STARTS
# (rule 2).
#
# A FORK OF d6r2c_fm11_run_arm.sh, WHOSE ARM WAS GRADED `BLOCKED` AT ITS FIRST
# STAGING STEP.  The BLOCK was a registration defect, not physics: the INHERITED
# `d6r2c_fm9_stage.py:95-100` raises `REFUSE_FRESH_IS_BASE` when the generated
# mesh equals the base mesh, and `Zb` is the state FOR WHICH THAT IDENTITY IS
# CORRECT.  FM12 changes FOUR things and nothing else:
#   (1) staging goes through `d6r2c_fm12_stage.py`, which gates `Zb` on
#       PROVENANCE (M0b) and `Zo` on DIFFERENCE FROM BASE (M0o).  M0o's
#       condition is FM11's, unweakened.  TWO gates, TWO refusal families, and
#       the grader REFUSES if either sub-arm is gated by the other's gate.
#   (2) the producer is handed `--datum-file`, because M0b's load-bearing limb
#       is CLAUDE.md rule 4's age guard applied to the mesh.
#   (3) the grader's external-anchor reader is repaired: FM11's `_J` tried the
#       keys ("obj","J","fun","weighted_CD") and the real record's key is
#       `obj.J`, a ONE-ELEMENT LIST -- so its emitted command REFUSED on the
#       very anchor it was written to read, and its pre-freeze check never saw
#       that because it ran the command with `--evals SYNTHETIC`.
#   (4) `R1` -- MESHER DETERMINISM ACROSS TIME -- is registered as a gate with
#       its own verdict, which never flips this arm's label.
# FM11'S FROZEN FILES ARE NOT EDITED.  This is a NEW registration.
#
# ITS OWN ANCESTOR, d6r2c_fm9_run_arm.sh (md5 recorded at the PIN block).  The
# guard bodies -- G-ROOT, G-BOX, G-FREEZE, G-DEPS, G-CPUSET, the busy sampler,
# the cpuset chooser and the rotator -- ARE THAT FILE'S BYTES, copied verbatim.
# Exactly three things were changed inside them and each is a label or a datum,
# never logic:
#   (i)   the printed token D6R2C_FM9_* became D6R2C_FM12_*;
#   (ii)  G-FREEZE's hardcoded instrument list became $PINNED_PY, so the list
#         the guard hashes and the list the pre-freeze check hashes are ONE list
#         (L-221/L-222);
#   (iii) the rotator walks $WORK/<sub-arm>/mp0*, because FM12's conditions sit
#         one level deeper than FM9's.
# seed_arm IS REPLACED, because FM12 seeds TWO SUB-ARMS rather than one arm.
#
# WHAT THIS ARM IS.  FM10 flew the three conditions at CL +0.1493/+0.1516/+0.1524
# above their registered targets -- THIRTY TIMES the registered finding trigger --
# because d6r2c_freshmesh.py:phase_solve re-applied `shape` and `twist` on a
# volume mesh ALREADY BUILT FROM THE DEFORMED SURFACE.  The cause class is
# PRODUCER and every mesh class was excluded by measurement (DAFOAM_CHARTER.md
# sec 22.3).  FM12 is the like-for-like evaluation FM10 failed to be: every solve
# at ZERO shape and ZERO twist, on a mesh generated for that shape, TRIMMED to
# the registered CL targets.
#
#   sub-arm Zb -- mesh extruded around surfaceMesh_base.cgns.  State Zb.
#   sub-arm Zo -- mesh extruded around the FFD-updated surface.  States Zo, Ez, Do.
#
# THE PHASE ORDER, AND WHY STAGING IS INSIDE THE PRODUCER.  FM9's launcher ran
# `stage` as its own process between `mesh` and `solve`.  FM12's producer stages
# the mesh ITSELF, at the top of run(), BEFORE prob.setup() is reached -- so the
# ordering guarantee ("the solver decomposes the mesh this arm generated") is a
# line of code inside the process that builds the model, not an assumption about
# what a previous process did.  The launcher therefore emits three commands per
# sub-arm, not four, and G-DEPS still stages d6r2c_fm9_stage.py because the
# producer imports it.
#
# NOTHING IS STOPPED BY THE CAP.  Sanaa's directive #17 (2026-09-12) is in force:
# a crossing is REPORTED, the row is graded NOT A RESULT, and the cap is never
# raised.  This file starts a container and waits; it kills nothing.
#
# SUBMISSIONS PARKED (rule 7).  This file sends nothing anywhere.
#
set -uo pipefail

ITEM=D6R2C-FM12
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM12-a2-wing-matched-lift-provenance
FM11_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM11-a2-wing-matched-lift
FM9_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM9-a2-wing-freshmesh-arrives
FM6_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER9R2-a2-wing-freshmesh-warmstart
AFTER_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER-a2-wing-decomposition-and-freshmesh
DEC4_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER8R2-a2-wing-decomposition-retrimmed
DEC7_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER8R3-a2-wing-gentler-layers
PARENT_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable
BASE="${BASE:-$REGISTERED_BASE}"
SRC=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C
FAMILY_DIR=/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing
SURFACE_SRC=/home/ubuntu/certonomous-runs/A2-mach-wing/surfaceMesh.cgns

# ---- the registered md5 pins (inherited, none of them chosen here) ----------
MD5_RUNSCRIPT=2f2ae43a627146cf8e0f065b035ada4b
MD5_GENWINGMESH=dab5e959187ab2e2bfb4e2c0ded0feb6
MD5_SURFACE=3050ea454c2d0304bafa2c1a80c53b76
MD5_EVALS=2c0b8143caad198cd2e21d8047986aa3
MD5_BASE_POINTS=0fb1935a9b8781b73ac4ccb136e3ec68
IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35

# THE CANONICAL STAGED PYTHON LIST (C6).  Referenced by seed_arm AND by G-DEPS;
# never re-spelled in either (L-221/L-222).  d6r2c_decomp.py is here because
# d6r2c_freshmesh.py imports it; d6r2c_dec5_decomp.py because the FM12 producer
# imports the trim, the governor and the frozen-model loader from it.
STAGED_PY="d6r2c_opt_runScript.py d6r2c_freshmesh.py d6r2c_decomp.py d6r2c_fm9_stage.py d6r2c_fm12_stage.py d6r2c_dec5_decomp.py d6r2c_fm12_states.py"
# THE FILES G-FREEZE PINS.  The grader is not staged into the arm -- it runs on
# the host after the container exits -- but its bytes are pinned all the same,
# because the cap this launcher prints comes out of it.
PINNED_PY="d6r2c_fm12_grade.py d6r2c_fm12_states.py d6r2c_fm12_stage.py d6r2c_fm9_stage.py d6r2c_freshmesh.py d6r2c_decomp.py d6r2c_dec5_decomp.py"
SUB_ARMS="Zb Zo"

RANKS=4
CPUSET=""
MEM_LIMIT=20g
MEM_FOOTPRINT_GB=17
RUN_UID=1000; RUN_GID=1000; EXTRA_GID=1002
CKPT_INTERVAL_S=1800

# THE CAP IS A PROPERTY OF THE ITEM, NOT OF THE ARM ID.  FM12R2 and FM12R3 are
# the registered re-run ids and carry THE IDENTICAL registered figure -- the same
# number looked up under another key.  THIS FILE DOES NOT CARRY THE FIGURE: it
# asks the grader, which derives it from the prediction.  A cap that exists as a
# literal in two files is two things that can drift, and in this family they did.
# NOTHING KILLS ON IT (Sanaa directive #17): a crossing is REPORTED, the row is
# graded NOT A RESULT, and the cap is never raised.
cap_core_min() {
  case "$1" in
    FM12|FM12R2|FM12R3) python3 "$SRC/d6r2c_fm12_grade.py" --print-cap "$1" 2>/dev/null ;;
    *) echo "" ;;
  esac
}

# ===========================================================================
# THE GRADING COMMAND HAS ONE SOURCE (charter 22.4 clause 2).
#
# The FM9 grader's frozen command line could only ever return NOT A RESULT: the
# launcher emitted `--log` and argparse rejected it, and the selftest never saw
# that because it called the graded FUNCTION and never went through main()
# (L-595, L-570).  The repair is structural.  This function is the ONLY place
# the grading command line exists.  The end-of-run banner prints it, and
# `--emit-grade-cmd` prints THE SAME STRING for the pre-freeze check to RUN.
# ===========================================================================
grade_cmd() {
  local ARM="$1" WORK="$2" CORE_MIN="$3" RC="$4" LOG="$5" OUT="$6"
  printf '%s' "python3 $SRC/d6r2c_fm12_grade.py --item $ARM --arm-dir $WORK \
--datum-file $WORK/.d6r2c_age_datum --core-min $CORE_MIN --rc $RC --log $LOG --out $OUT"
}

# ===========================================================================
# THE CONTAINER COMMAND BLOCK HAS ONE SOURCE TOO, for the same reason.
# `--emit-cmd` prints exactly what is written into the container, so the
# pre-freeze check drives THE PRODUCER'S OWN ARGUMENT VECTOR through argparse
# rather than a description of it.
# ===========================================================================
container_cmd() {
  local ARM="$1"
  cat <<CMD
set -uo pipefail
echo "D6R2C_FM12_DEADLINE_IN_CONTAINER_S: NONE"
rc=0
# ---- sub-arm Zb: the BASE geometry, meshed from the BASE surface.  There is no
# ---- deform phase here: the surface this mesh is extruded around is the family
# ---- script's own, unmodified, so nothing has to be applied to it.
cd /mnt/$ARM/Zb
[ \$rc -eq 0 ] && { python d6r2c_freshmesh.py --phase mesh --arm-dir "\$PWD" \\
    --genwingmesh genWingMesh.py --surface-out surfaceMesh_base.cgns || rc=\$?; }
[ \$rc -eq 0 ] && { mpirun -np $RANKS python d6r2c_fm12_states.py --arm-dir "\$PWD" \\
    --sub-arm Zb --runscript d6r2c_opt_runScript.py \\
    --evals d6r2c_evals_final.jsonl --x0 d6r2c_x0_final.json \\
    --datum-file /mnt/$ARM/.d6r2c_age_datum || rc=\$?; }
# ---- sub-arm Zo: the OPTIMISED geometry.  deform writes the FFD-updated
# ---- surface, mesh extrudes around it, and the producer then solves at ZERO
# ---- shape and ZERO twist -- because the mesh already carries the deformation.
cd /mnt/$ARM/Zo
[ \$rc -eq 0 ] && { mpirun -np $RANKS python d6r2c_freshmesh.py --phase deform --arm-dir "\$PWD" \\
    --runscript d6r2c_opt_runScript.py --evals d6r2c_evals_final.jsonl \\
    --base-dir "\$PWD" --omp-dir /mnt/parent/O_mp \\
    --surface-in surfaceMesh_base.cgns --surface-out surfaceMesh_final.cgns || rc=\$?; }
[ \$rc -eq 0 ] && { python d6r2c_freshmesh.py --phase mesh --arm-dir "\$PWD" \\
    --genwingmesh genWingMesh.py --surface-out surfaceMesh_final.cgns || rc=\$?; }
[ \$rc -eq 0 ] && { mpirun -np $RANKS python d6r2c_fm12_states.py --arm-dir "\$PWD" \\
    --sub-arm Zo --runscript d6r2c_opt_runScript.py \\
    --evals d6r2c_evals_final.jsonl --x0 d6r2c_x0_final.json \\
    --datum-file /mnt/$ARM/.d6r2c_age_datum || rc=\$?; }
echo "D6R2C_FM12_RC=\$rc"
exit \$rc
CMD
}

# ===========================================================================
# G-ROOT.1 -- BASE must be THIS item's registered run root, normalised
# ===========================================================================
guard_root() {
  local BASE_REAL REG_REAL forb
  BASE_REAL=$(realpath -m "$1"); REG_REAL=$(realpath -m "$REGISTERED_BASE")
  if [ "$BASE_REAL" != "$REG_REAL" ]; then
    echo "ABORT G-ROOT.1 BASE is not this item's registered run root."
    echo "  given: $BASE_REAL"; echo "  registered: $REG_REAL"; return 3
  fi
  # G-ROOT.2 -- the roots this file must NEVER write.  THE D6R2C ROOT IS FIRST
  # and is the reason the list exists here: it holds the GRADED O_mp artefacts
  # that O_mp_GRADE.json cites by path, and this item reads them, never writes.
  local FORBIDDEN="$PARENT_BASE
$FM11_BASE
$FM9_BASE
$AFTER_BASE
$DEC4_BASE
$FM6_BASE
/home/ubuntu/certonomous-runs/CURRICULUM-D6R2-a2-wing-multipoint-transonic
/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint
/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint
/home/ubuntu/certonomous-runs/A2-mach-wing
/home/ubuntu/dafoam-tutorials/MACH_Tutorial_Wing"
  while IFS= read -r forb; do
    [ -z "$forb" ] && continue
    if [ "$BASE_REAL" = "$(realpath -m "$forb")" ]; then
      echo "ABORT G-ROOT.2 BASE resolves to a root this item must never write: $forb"; return 3
    fi
  done <<< "$FORBIDDEN"
  # G-ROOT.3 -- the ledger must belong to this item and to no other
  if [ -f "$1/ledger.txt" ]; then
    local FOREIGN
    FOREIGN=$(grep -a "^ITEM=" "$1/ledger.txt" 2>/dev/null | grep -av "^ITEM=$ITEM$" | head -1)
    if [ -n "$FOREIGN" ]; then
      echo "ABORT G-ROOT.3 ledger at $1/ledger.txt carries another item: $FOREIGN"; return 3
    fi
  fi
  echo "D6R2C_FM12_G_ROOT_PASS item=$ITEM base=$BASE_REAL"
  return 0
}

md5_is() { [ "$(md5sum "$1" | cut -d' ' -f1)" = "$2" ]; }

# ===========================================================================
# THE CORES OTHER CONTAINERS HOLD, AND A CPUSET THAT AVOIDS THEM (E5, E6)
# ===========================================================================
occupied_cpus() {
  local c
  for c in $(sudo -n docker ps -q 2>/dev/null); do
    sudo -n docker inspect -f '{{.HostConfig.CpusetCpus}}' "$c" 2>/dev/null
  done | paste -sd, -
}

# BUSY_PCT -- AND THE HONEST HISTORY OF THIS NUMBER, because the first version
# of it was wrong and its own control said so before anything was frozen.
#
# FIRST CLAIM: sampling every core for 2.0 s on 2026-09-13 with zero containers
# running gave 37 cores at >=90% busy, 59 at <10%, and NOT ONE in between.  I
# registered BUSY_PCT = 50.0 as the midpoint of that empty band and wrote a
# control asserting that 1%, 50% and 99% must partition the box identically.
#
# THE CONTROL FAILED ON ITS FIRST RUN.  Over a 1.0 s window the same box gives
# 40 cores at >=1%, 38 at >=50% and 36 at >=99%.  THE BAND IS NOT EMPTY; it only
# looked empty at one interval.  A few cores are genuinely partially loaded, and
# a shorter sample catches them straddling.  So BUSY_PCT IS NOT A DERIVED
# SEPARATOR AND I WILL NOT CALL IT ONE.
#
# WHAT IT IS INSTEAD: this is a guard whose only action is TO REFUSE TO START,
# so its error should fall toward refusing.  BUSY_PCT = 1.0 is the conservative
# end -- any core doing measurable work is treated as occupied -- and it gives
# up on discriminating rather than pretending to.  IT COSTS NOTHING HERE: at 1%
# the box still showed 56 free cores against the 4 this arm needs.
BUSY_PCT=1.0
BUSY_INTERVAL=2.0

# classify_busy <snapA> <snapB> <pct>  -- prints the cores at or above pct.
# A PURE FUNCTION OVER TWO /proc/stat TEXTS, deliberately: that is what lets the
# selftest drive it with synthetic samples.  A reader that can only be pointed
# at the live box can only be tested against whatever the box happens to do.
classify_busy() {
  python3 - "$1" "$2" "$3" <<'BUSYPY'
import sys
def snap(p):
    d = {}
    for l in open(p):
        if l.startswith("cpu") and len(l) > 3 and l[3].isdigit():
            f = l.split(); c = int(f[0][3:]); v = [int(x) for x in f[1:]]
            d[c] = (sum(v), v[3] + v[4])       # total, idle+iowait
    return d
a, b, pct = snap(sys.argv[1]), snap(sys.argv[2]), float(sys.argv[3])
out = []
for c in sorted(a):
    if c not in b:
        continue
    dt = b[c][0] - a[c][0]; di = b[c][1] - a[c][1]
    if dt > 0 and 100.0 * (dt - di) / dt >= pct:
        out.append(c)
print(",".join(str(c) for c in out))
BUSYPY
}

# busy_cpus -- THE SECOND OCCUPANCY SOURCE, and the one that sees what docker
# cannot.  MEASURED 2026-09-13, minutes after DEC7 exited: `docker ps` was EMPTY
# and reported no occupied cores at all, while cores 1, 2 and 7 sat at 100%.
# The old hardcoded 2,3,4,5 would have put two ranks on core 2 AND THE DOCKER
# LIMB WOULD HAVE CALLED IT FREE.  Bare-metal mpirun from another team is
# invisible to the container daemon exactly as fleet agents are invisible to
# pgrep (L-41).  A guard that reads the container list is reading an ADJACENT
# QUANTITY; this one reads whether the core is actually running something.
busy_cpus() {
  local d; d=$(mktemp -d)
  cp /proc/stat "$d/a"; sleep "$BUSY_INTERVAL"; cp /proc/stat "$d/b"
  classify_busy "$d/a" "$d/b" "$BUSY_PCT"
  rm -rf "$d"
}

# free_cpuset <n_ranks> <occupied_csv> <nproc>  -- prints a cpuset or nothing.
# Taking the occupancy AS AN ARGUMENT is what lets the selftest drive it against
# a synthetic busy box; a function that reads the live daemon can only ever be
# tested against whatever the box happens to be doing.
free_cpuset() {
  python3 - "$1" "$2" "$3" <<'CPUPY'
import sys
k, occ_s, n = int(sys.argv[1]), sys.argv[2], int(sys.argv[3])
occ = set()
for tok in occ_s.split(","):
    tok = tok.strip()
    if not tok:
        continue
    if "-" in tok:
        a, b = tok.split("-", 1)
        if a.strip().isdigit() and b.strip().isdigit():
            occ.update(range(int(a), int(b) + 1))
    elif tok.isdigit():
        occ.add(int(tok))
free = [c for c in range(n) if c not in occ]
# leave cores 0 and 1 to the OS when there is any choice at all
pref = [c for c in free if c > 1] or free
if len(pref) < k:
    sys.exit(1)
print(",".join(str(c) for c in pref[:k]))
CPUPY
}

# G-CPUSET -- REFUSE TO START if the chosen cpuset touches a core already in use,
# by a container OR by anything else the busy sample can see.
# It never stops anything: it is a launch precondition, like G-BOX's load and
# swap limbs.  FM9 crossed its cap purely because this did not exist.
guard_cpuset() {
  local want="$1" occ="$2"
  python3 - "$want" "$occ" <<'CPUPY'
import sys
def expand(s):
    out = set()
    for tok in s.split(","):
        tok = tok.strip()
        if not tok:
            continue
        if "-" in tok:
            a, b = tok.split("-", 1)
            if a.strip().isdigit() and b.strip().isdigit():
                out.update(range(int(a), int(b) + 1))
        elif tok.isdigit():
            out.add(int(tok))
    return out
want, occ = expand(sys.argv[1]), expand(sys.argv[2])
clash = sorted(want & occ)
if clash:
    print("ABORT G-CPUSET the chosen cpuset %s intersects cores ALREADY IN USE -- "
          "by a running container, or measurably busy with no container at all: %s."
          % (sys.argv[1], clash))
    print("  A BOX-LEVEL LOAD AVERAGE CANNOT SEE THIS.  Eight MPI ranks on four "
          "cores halved another arm's throughput for fifteen minutes (ADDENDUM 1).")
    print("  This guard REFUSES TO START and stops nothing that is running.")
    sys.exit(1)
print("D6R2C_FM12_G_CPUSET_PASS cpuset=%s occupied=%s"
      % (sys.argv[1], sorted(occ) if occ else "none"))
CPUPY
}

# ===========================================================================
# G-DEPS (C7) -- EVERY LOCAL MODULE A STAGED FILE IMPORTS MUST ITSELF BE STAGED.
#
# A PIN PROVES WHAT A FILE IS, NOT WHAT IT NEEDS.  FM6 was launched with
# d6r2c_freshmesh.py pinned at its exact frozen md5 and died because the module
# it imports was not beside it.  The hash was correct and the arm was unrunnable.
#
# Takes the staged list as ARGUMENTS so the SELFTEST CAN DRIVE IT WITH A FILE
# REMOVED and require it to FAIL.  A check that cannot be seen to fail is not a
# check -- the same lesson this item's cap controls taught.
# ===========================================================================
guard_deps() {
  python3 - "$SRC" "$@" <<'DEPSPY'
import ast, os, sys
src, staged = sys.argv[1], sys.argv[2:]
stem = {os.path.splitext(f)[0] for f in staged}
missing, scanned = [], 0
for f in staged:
    if not f.endswith(".py"):
        continue
    p = os.path.join(src, f)
    if not os.path.isfile(p):
        print("ABORT G-DEPS staged file does not exist in SRC: %s" % f)
        sys.exit(1)
    scanned += 1
    tree = ast.parse(open(p).read(), p)
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            mods.add(node.module.split(".")[0])
    for m in sorted(mods):
        # LOCAL means "a file of that name sits in SRC" -- an image module is
        # not this launcher's to stage and is not its to vouch for.
        if os.path.isfile(os.path.join(src, m + ".py")) and m not in stem:
            missing.append("%s imports %s, which is NOT staged" % (f, m))
if missing:
    print("ABORT G-DEPS the staged set does not cover its own imports:")
    for x in missing:
        print("   " + x)
    sys.exit(1)
print("D6R2C_FM12_G_DEPS_PASS scanned=%d staged=%d" % (scanned, len(staged)))
DEPSPY
}

# ===========================================================================
# G-FREEZE -- the instruments that run ARE the frozen instruments.
# A2: THE GRADER IS PINNED TOO.
# ===========================================================================
guard_freeze() {
  local f got want bad=0
  md5_is "$SRC/d6r2c_opt_runScript.py" "$MD5_RUNSCRIPT" || {
    echo "ABORT G-FREEZE d6r2c_opt_runScript.py md5 mismatch"; bad=1; }
  md5_is "$FAMILY_DIR/genWingMesh.py" "$MD5_GENWINGMESH" || {
    echo "ABORT G-FREEZE the family script's mesh step md5 mismatch"; bad=1; }
  md5_is "$SURFACE_SRC" "$MD5_SURFACE" || {
    echo "ABORT G-FREEZE the family script's own surface md5 mismatch"; bad=1; }
  md5_is "$PARENT_BASE/O_mp/d6r2c_evals.jsonl" "$MD5_EVALS" || {
    echo "ABORT G-FREEZE the inherited O_mp record md5 mismatch -- the artefact this"
    echo "  registration pinned is not the artefact on disk"; bad=1; }
  md5_is "$PARENT_BASE/base/constant/polyMesh/points.gz" "$MD5_BASE_POINTS" || {
    echo "ABORT G-FREEZE the base mesh points md5 mismatch"; bad=1; }
  # the three instruments this registration froze, pinned by the PREREGISTRATION
  # THE INSTRUMENT LIST HAS ONE SOURCE: $PINNED_PY, which is also what the
  # pre-freeze check hashes.  A list spelled twice is two lists (L-221/L-222).
  for f in $PINNED_PY; do
    want=$(grep -m1 "^# PIN $f " "$0" | awk '{print $4}')
    [ -n "$want" ] || { echo "ABORT G-FREEZE no pin recorded for $f"; bad=1; continue; }
    got=$(md5sum "$SRC/$f" | cut -d' ' -f1)
    [ "$got" = "$want" ] || { echo "ABORT G-FREEZE $f md5=$got want=$want"; bad=1; }
  done
  [ $bad -eq 0 ] || return 4
  echo "D6R2C_FM12_G_FREEZE_PASS"
  return 0
}

# ===========================================================================
# BOX HYGIENE -- a LAUNCH PRECONDITION.  It refuses to START and never stops
# anything running (Sanaa item 18 read with her directive #17).
# ===========================================================================
guard_box() {
  local load1 nproc avail_gb swapoff
  load1=$(awk '{print $1}' /proc/loadavg); nproc=$(nproc)
  avail_gb=$(awk '/MemAvailable/{printf "%d", $2/1048576}' /proc/meminfo)
  awk -v l="$load1" -v n="$nproc" 'BEGIN{exit !(l>n)}' && {
    echo "ABORT G-BOX load1=$load1 > nproc=$nproc -- launch precondition, nothing is stopped"; return 3; }
  # ---- ADDENDUM 5 (2026-09-13): THE SWAP LIMB MEASURES WHAT HER ITEM 18 NAMES.
  # Sanaa's item 18: "swap use above zero FOR SOLVER JOBS is a defect."  The lab's
  # canonical implementation of that sentence is scripts/queue_runner.py
  # `swap_offenders()` (lines 915-943), which reads per-process VmSwap from
  # /proc/<pid>/status and counts SOLVER PROCESSES ONLY; gate E is defined at
  # line 102 as "any solver process has VmSwap > 0".
  #
  # THIS GUARD PREVIOUSLY READ `SwapTotal - SwapFree`, WHICH IS NOT THAT QUANTITY.
  # It counts a SwapCached slot that no process holds.  Measured 2026-09-13:
  # SwapTotal-SwapFree = 8 kB, SwapCached = 8 kB, 131 processes reporting VmSwap,
  # TOTAL 0 kB, NONE above zero, 551 GB available, load 43 of 96 -- and this guard
  # refused arm FM5 on it.
  #
  # THE THRESHOLD IS UNCHANGED AT > 0.  ONLY THE MEASURED QUANTITY MOVED.
  # The canonical function is CALLED, never re-spelled (L-221/L-222), so the two
  # cannot drift; and a guard that CANNOT MEASURE REFUSES rather than passing
  # quietly, which is the same discipline as dv_divisor_for().
  swapoff=$(python3 -c "
import sys
sys.path.insert(0, '/home/ubuntu/Certonomous/scripts')
from queue_runner import swap_offenders
for o in swap_offenders():
    print('%(pid)d %(name)s %(vmswap_kb)d' % o)
") || {
    echo "ABORT G-BOX cannot read the canonical swap gate (scripts/queue_runner.py"
    echo "  swap_offenders) -- a guard that cannot measure REFUSES rather than passes"; return 3; }
  if [ -n "$swapoff" ]; then
    echo "ABORT G-BOX solver processes holding swap (Sanaa item 18) -- launch precondition,"
    echo "  nothing is stopped.  THE OFFENDERS, NAMED:"
    echo "$swapoff" | while read -r p n k; do echo "    pid=$p name=$n VmSwap=${k} kB"; done
    return 3
  fi
  [ "$avail_gb" -lt "$MEM_FOOTPRINT_GB" ] && {
    echo "ABORT G-MEM MemAvailable=${avail_gb}G < declared footprint ${MEM_FOOTPRINT_GB}G"; return 3; }
  echo "D6R2C_FM12_G_BOX_PASS load1=$load1 nproc=$nproc solver_swap_offenders=0 avail_gb=$avail_gb"
  return 0
}


# ===========================================================================
# SEED -- TWO SUB-ARMS.  base/ copied read-only and HASHED, inputs staged BEFORE
# the age datum, and G-COLD refuses a sub-arm where 0 or a time dir exists.
# ===========================================================================
seed_arm() {
  local ARM="$1" WORK="$BASE/$ARM" SA SUB mp bad
  mkdir -p "$WORK" || return 5
  for SA in $SUB_ARMS; do
    SUB="$WORK/$SA"
    # G-COLD -- a guard refuses a case where 0 or a time dir already exists
    for bad in "$SUB/0" "$SUB/constant" "$SUB/mp04" "$SUB/d6r2c_fm12.jsonl"; do
      [ -e "$bad" ] && { echo "ABORT G-COLD $bad exists"; return 5; }
    done
    mkdir -p "$SUB" || return 5
    cp -a "$PARENT_BASE/base/." "$SUB/" || return 5
    md5_is "$SUB/constant/polyMesh/points.gz" "$MD5_BASE_POINTS" || {
      echo "ABORT G-SEED $SA seeded mesh is not the registered base mesh"; return 5; }
    # the three multipoint case copies the frozen runScript's lines 7-8 register
    for mp in mp04 mp05 mp06; do
      cp -a "$PARENT_BASE/base" "$SUB/$mp" || { echo "ABORT G-SEED stage $SA/$mp"; return 5; }
      test -z "$(ls -d "$SUB/$mp"/processor* 2>/dev/null)" || {
        echo "ABORT G-COLD $SA/$mp processor* present"; return 5; }
      md5_is "$SUB/$mp/constant/polyMesh/points.gz" "$MD5_BASE_POINTS" || {
        echo "ABORT G-SEED $SA/$mp is not the registered base mesh"; return 5; }
    done
    # inputs, staged BEFORE the age datum so the age guard dates them as INPUTS
    cp "$PARENT_BASE/O_mp/d6r2c_evals.jsonl" "$SUB/d6r2c_evals_final.jsonl" || return 5
    cp "$PARENT_BASE/O_mp/d6r2c_x0.json"     "$SUB/d6r2c_x0_final.json"     || return 5
    for f in $STAGED_PY; do
      cp "$SRC/$f" "$SUB/" || { echo "ABORT G-SEED stage $f into $SA"; return 5; }
    done
    cp "$SURFACE_SRC" "$SUB/surfaceMesh_base.cgns" || return 5
    cp "$FAMILY_DIR/genWingMesh.py" "$SUB/genWingMesh.py" || return 5
    md5_is "$SUB/genWingMesh.py" "$MD5_GENWINGMESH" || {
      echo "ABORT G-SEED the staged mesh step is not the family script's"; return 5; }
    test -f "$SUB/0/U" || { echo "ABORT G-COLD $SA/0/U missing after seed"; return 5; }
    echo "D6R2C_FM12_G_COLD_PASS arm=$ARM sub_arm=$SA"
  done
  # ONE age datum for the whole arm, touched LAST, after every input is staged.
  touch "$WORK/Zb/0/U"
  AGE_DATUM=$(stat -c '%Y' "$WORK/Zb/0/U")
  echo "$AGE_DATUM" > "$WORK/.d6r2c_age_datum"
  echo "D6R2C_FM12_G_COLD_PASS arm=$ARM age_datum_epoch=$AGE_DATUM sub_arms=$SUB_ARMS"
  return 0
}

# ===========================================================================
# THE CHECKPOINT ROTATOR (Sanaa Checkpoints item 1; the parent's L6).
# Every CKPT_INTERVAL_S wall, the arm's record + design vector + the latest
# primal time from every mp0*/processor* are copied to ckpt/<UTC>/.  THE LAST
# TWO ARE KEPT and older ones purged.
# ===========================================================================
rotator() {
  local WORK="$1"
  while :; do
    sleep "$CKPT_INTERVAL_S"
    [ -d "$WORK" ] || return 0
    local D="$WORK/ckpt/$(date -u +%Y%m%dT%H%M%SZ)"
    mkdir -p "$D"
    for sa in Zb Zo; do
      for f in d6r2c_fm12.jsonl d6r2c_fm9_stage.json h1.json mesh_rc.txt; do
        [ -f "$WORK/$sa/$f" ] && { mkdir -p "$D/$sa"; cp -a "$WORK/$sa/$f" "$D/$sa/" 2>/dev/null; }
      done
    done
    for mp in "$WORK"/*/mp0*; do
      [ -d "$mp" ] || continue
      for pr in "$mp"/processor*; do
        [ -d "$pr" ] || continue
        local latest
        latest=$(ls -1d "$pr"/[0-9]* 2>/dev/null | sort -t/ -k1 | tail -1)
        [ -n "$latest" ] && { SA=$(basename "$(dirname "$mp")"); \
          mkdir -p "$D/$SA/$(basename "$mp")/$(basename "$pr")"; \
          cp -a "$latest" "$D/$SA/$(basename "$mp")/$(basename "$pr")/" 2>/dev/null; }
      done
    done
    ls -1d "$WORK"/ckpt/* 2>/dev/null | sort | head -n -2 | xargs -r rm -rf
  done
}

# ===========================================================================
# MAIN
# ===========================================================================
ARM="${1:-}"; IMG="${2:-}"

# ---- THE TWO EMIT MODES.  They print THE EXACT STRINGS this file uses, and
# ---- they exist so the pre-freeze check can RUN them rather than read them.
if [ "$ARM" = "--emit-grade-cmd" ]; then
  grade_cmd "${2:-FM12}" "${3:-$BASE/FM12}" "${4:-0.000}" "${5:-0}" \
            "${6:-$BASE/FM12.log}" "${7:-$BASE/FM12_GRADE.json}"; echo; exit 0
fi
if [ "$ARM" = "--emit-cmd" ]; then container_cmd "${2:-FM12}"; exit 0; fi
if [ "$ARM" = "--print-staged" ]; then echo "$STAGED_PY"; exit 0; fi
if [ "$ARM" = "--print-pinned" ]; then echo "$PINNED_PY"; exit 0; fi

if [ "$ARM" = "--selftest" ]; then
  rc=0
  guard_root /tmp/definitely-not-the-root >/dev/null 2>&1 && { echo "SELFTEST FAIL G-ROOT.1 accepted a wrong root"; rc=1; } || echo "SELFTEST ok G-ROOT.1 refuses a wrong root"
  BASE_SAVE=$REGISTERED_BASE; REGISTERED_BASE=$PARENT_BASE
  guard_root "$PARENT_BASE" >/dev/null 2>&1 && { echo "SELFTEST FAIL G-ROOT.2 accepted the GRADED parent root"; rc=1; } || echo "SELFTEST ok G-ROOT.2 refuses the graded parent root"
  REGISTERED_BASE=$BASE_SAVE
  guard_root "$FM9_BASE" >/dev/null 2>&1 && { echo "SELFTEST FAIL G-ROOT.1 accepted FM10's OWN GRADED ROOT"; rc=1; } || echo "SELFTEST ok G-ROOT refuses FM10's root, whose artefacts this arm READS and must never write"
  guard_root "$FM11_BASE" >/dev/null 2>&1 && { echo "SELFTEST FAIL G-ROOT accepted FM11'S OWN BLOCKED ROOT"; rc=1; } || echo "SELFTEST ok G-ROOT refuses FM11's root -- FM11 is graded BLOCKED and its artefacts are this item's LIVE CONTROLS, which it READS and must never write"
  guard_freeze >/dev/null 2>&1 && echo "SELFTEST ok G-FREEZE passes on the frozen tree" || { echo "SELFTEST FAIL G-FREEZE rejected the frozen tree"; guard_freeze; rc=1; }
  # ---- THE CAP: one source, and the three registered arm ids agree ---------
  CAP11=$(cap_core_min FM12)
  [ -n "$CAP11" ] && echo "SELFTEST ok the cap comes from the grader: $CAP11 core-min" || { echo "SELFTEST FAIL no cap"; rc=1; }
  [ "$CAP11" = "$(cap_core_min FM12R2)" ] && [ "$CAP11" = "$(cap_core_min FM12R3)" ] \
    && echo "SELFTEST ok FM12R2 and FM12R3 carry the IDENTICAL registered cap -- a re-run id is the same number under another key" \
    || { echo "SELFTEST FAIL the re-run ids do not carry FM12's cap"; rc=1; }
  [ -z "$(cap_core_min FM13)" ] \
    && echo "SELFTEST ok FM13 -- FM11's re-run id -- gets NO cap here, so an arm registered by ANOTHER document cannot be launched by this one" \
    || { echo "SELFTEST FAIL this launcher answers for an arm id it does not register"; rc=1; }
  [ -z "$(cap_core_min FM99)" ] && echo "SELFTEST ok an unregistered arm id gets NO cap, and the launcher refuses to start on that" || { echo "SELFTEST FAIL an unregistered arm id was given a cap"; rc=1; }
  [ "$(grep -c '^CAP_CORE_MIN=[0-9]' "$0")" -eq 0 ] && echo "SELFTEST ok this launcher carries no cap literal of its own" || { echo "SELFTEST FAIL a cap literal is hardcoded here"; rc=1; }
  # ---- THE GRADING COMMAND: ONE SOURCE, and it is the one the banner prints -
  GC=$(grade_cmd FM12 /tmp/w 1.000 0 /tmp/l.log /tmp/o.json)
  case "$GC" in
    *"--item FM12"*) echo "SELFTEST ok the emitted grade command names the ARM, not a stale item id (L-570)" ;;
    *) echo "SELFTEST FAIL the grade command does not carry --item"; rc=1 ;;
  esac
  case "$GC" in
    *"--log /tmp/l.log"*) echo "SELFTEST ok the emitted grade command carries --log, which the FM9 launcher emitted and its grader rejected (L-595)" ;;
    *) echo "SELFTEST FAIL the grade command does not carry --log"; rc=1 ;;
  esac
  [ "$(bash "$0" --emit-grade-cmd FM12 /tmp/w 1.000 0 /tmp/l.log /tmp/o.json)" = "$GC" ] \
    && echo "SELFTEST ok --emit-grade-cmd prints EXACTLY what the run prints -- one source, so the checked command and the run command cannot drift" \
    || { echo "SELFTEST FAIL --emit-grade-cmd and grade_cmd disagree"; rc=1; }
  # every flag the emitted command uses must be a flag the grader accepts
  for FLAG in $(printf '%s\n' "$GC" | tr ' ' '\n' | grep '^--'); do
    python3 "$SRC/d6r2c_fm12_grade.py" --help 2>/dev/null | grep -q -- "$FLAG" \
      || { echo "SELFTEST FAIL the grader does not accept $FLAG"; rc=1; }
  done
  echo "SELFTEST ok every --flag in the emitted grade command is a flag the grader's own --help declares"
  # ---- THE CONTAINER COMMAND: the phase order, read out of what is EMITTED --
  PH=$(container_cmd FM12 | grep -oE "phase mesh|phase deform|--sub-arm Zb|--sub-arm Zo" | tr '\n' ' ')
  [ "$PH" = "phase mesh --sub-arm Zb phase deform phase mesh --sub-arm Zo " ] \
    && echo "SELFTEST ok the phase order is Zb(mesh,solve) then Zo(deform,mesh,solve)" \
    || { echo "SELFTEST FAIL the phase order is [$PH]"; rc=1; }
  container_cmd FM12 | grep -q -- "--phase solve" \
    && { echo "SELFTEST FAIL the FM10 solve phase -- THE ONE THAT APPLIES THE SHAPE TWICE -- is still in the command block"; rc=1; } \
    || echo "SELFTEST ok d6r2c_freshmesh.py --phase solve, the producer whose double application made FM10 NOT A RESULT, IS NOT CALLED BY THIS ARM"
  [ "$(bash "$0" --emit-cmd FM12)" = "$(container_cmd FM12)" ] \
    && echo "SELFTEST ok --emit-cmd prints EXACTLY the block written into the container" \
    || { echo "SELFTEST FAIL --emit-cmd and container_cmd disagree"; rc=1; }
  # ---- G-DEPS (C7), DRIVEN IN BOTH DIRECTIONS ------------------------------
  guard_deps $STAGED_PY >/dev/null 2>&1 \
    && echo "SELFTEST ok G-DEPS passes on the registered staged set" \
    || { echo "SELFTEST FAIL G-DEPS rejected the registered staged set"; guard_deps $STAGED_PY; rc=1; }
  if guard_deps d6r2c_fm12_states.py >/dev/null 2>&1; then
    echo "SELFTEST FAIL G-DEPS PASSED the producer with none of its libraries beside it"; rc=1
  else
    echo "SELFTEST ok G-DEPS FAILS when the producer is staged without the libraries it imports"
  fi
  case "$(guard_deps d6r2c_fm12_states.py 2>&1)" in
    *"d6r2c_fm12_states.py imports d6r2c_dec5_decomp"*)
      echo "SELFTEST ok G-DEPS names the missing module and the file that needs it" ;;
    *) echo "SELFTEST FAIL G-DEPS did not name the missing module"; rc=1 ;;
  esac
  # the staged list and the pinned list each have ONE source
  for f in $STAGED_PY; do
    [ "$(grep -c "^STAGED_PY=.*$f" "$0")" -ge 1 ] || { echo "SELFTEST FAIL $f is not in the canonical staged list"; rc=1; }
  done
  echo "SELFTEST ok every staged file is named in the one canonical list"
  case "$PINNED_PY" in
    *d6r2c_fm12_states.py*d6r2c_fm9_stage.py*) echo "SELFTEST ok G-FREEZE pins the producer and the reader it imports" ;;
    *) echo "SELFTEST FAIL the pinned list is incomplete"; rc=1 ;;
  esac
  for f in $PINNED_PY; do
    grep -q "^# PIN $f " "$0" || { echo "SELFTEST FAIL no PIN line for $f"; rc=1; }
  done
  echo "SELFTEST ok every pinned file has a PIN line in this launcher"
  # ---- G-CPUSET, driven on synthetic occupancy -----------------------------
  guard_cpuset "2,3,4,5" "2,3,4,5" >/dev/null 2>&1 && { echo "SELFTEST FAIL G-CPUSET ACCEPTED AN EXACT COLLISION"; rc=1; } || echo "SELFTEST ok G-CPUSET refuses an exact collision"
  guard_cpuset "4,5,6,7" "2,3,4,5" >/dev/null 2>&1 && { echo "SELFTEST FAIL G-CPUSET accepted a PARTIAL overlap"; rc=1; } || echo "SELFTEST ok G-CPUSET refuses a partial overlap"
  guard_cpuset "6,7,8,9" "4-8" >/dev/null 2>&1 && { echo "SELFTEST FAIL G-CPUSET is blind to the a-b range spelling"; rc=1; } || echo "SELFTEST ok G-CPUSET reads the 4-8 range spelling docker emits"
  guard_cpuset "2,3,4,5" "10,11,12,13" >/dev/null 2>&1 && echo "SELFTEST ok G-CPUSET PASSES a genuinely disjoint cpuset" || { echo "SELFTEST FAIL G-CPUSET refused a disjoint cpuset"; rc=1; }
  PICK=$(free_cpuset 4 "2,3,4,5" 16); guard_cpuset "$PICK" "2,3,4,5" >/dev/null 2>&1 && echo "SELFTEST ok what free_cpuset chooses is what G-CPUSET accepts" || { echo "SELFTEST FAIL the chooser and the guard disagree"; rc=1; }
  [ "$(grep -cE '^CPUSET=[0-9]' "$0")" -eq 0 ] && echo "SELFTEST ok no hardcoded cpuset assignment survives in this launcher" || { echo "SELFTEST FAIL a hardcoded CPUSET= assignment is still here"; rc=1; }
  # ---- the busy sampler, on synthetic /proc/stat samples --------------------
  SD=$(mktemp -d)
  printf 'cpu  0 0 0 0 0 0 0 0\ncpu0 100 0 0 1000 0 0 0 0\ncpu1 100 0 0 1000 0 0 0 0\ncpu2 100 0 0 1000 0 0 0 0\n' > "$SD/a"
  printf 'cpu  0 0 0 0 0 0 0 0\ncpu0 100 0 0 2000 0 0 0 0\ncpu1 1100 0 0 1000 0 0 0 0\ncpu2 600 0 0 1500 0 0 0 0\n' > "$SD/b"
  [ "$(classify_busy "$SD/a" "$SD/b" 50.0)" = "1,2" ] && echo "SELFTEST ok classify_busy reads a saturated and a half-loaded core as busy, an idle one as free" || { echo "SELFTEST FAIL classify_busy returned [$(classify_busy "$SD/a" "$SD/b" 50.0)]"; rc=1; }
  [ "$(classify_busy "$SD/a" "$SD/b" 99.0)" = "1" ] && echo "SELFTEST ok the reader discriminates by threshold" || { echo "SELFTEST FAIL classify_busy does not discriminate"; rc=1; }
  [ -z "$(classify_busy "$SD/a" "$SD/a" 50.0)" ] && echo "SELFTEST ok a zero interval yields no busy cores, never an invented one" || { echo "SELFTEST FAIL classify_busy invented busy cores"; rc=1; }
  rm -rf "$SD"
  # ---- THE PRODUCER'S OWN CLI, DRIVEN FROM THE EMITTED BLOCK ---------------
  # This is charter 22.4 clause 2 applied to the producer: the argument vector
  # checked is the one the container will run, lifted out of the emitted block
  # rather than re-typed here.
  for SA in $SUB_ARMS; do
    ARGS=$(container_cmd FM12 | tr '\n' ' ' | tr -d '\\' \
           | grep -oE "python d6r2c_fm12_states\.py [^|]*--sub-arm $SA [^|]*--x0 [^ ]+" | head -1)
    ARGS=${ARGS#python d6r2c_fm12_states.py }
    ARGS=$(printf '%s' "$ARGS" | sed 's|"\$PWD"|/tmp/fm12_selftest_arm|')
    OUT=$(cd "$SRC" && python3 d6r2c_fm12_states.py --parse-only $ARGS 2>&1)
    case "$OUT" in
      *"D6R2C_FM12_PARSE_ONLY sub_arm=$SA"*)
        echo "SELFTEST ok the producer accepts the EXACT argument vector the container will hand it for $SA" ;;
      *) echo "SELFTEST FAIL the producer rejected its own emitted argument vector for $SA:"; echo "$OUT"; rc=1 ;;
    esac
  done
  # and the negative: an argument vector the producer must REJECT
  (cd "$SRC" && python3 d6r2c_fm12_states.py --parse-only --sub-arm Zq >/dev/null 2>&1) \
    && { echo "SELFTEST FAIL the producer accepted an unregistered sub-arm"; rc=1; } \
    || echo "SELFTEST ok the producer REJECTS an unregistered sub-arm -- the parse check is not vacuous"
  [ "$rc" -eq 0 ] && echo "D6R2C_FM12_LAUNCH SELFTEST PASS" || echo "D6R2C_FM12_LAUNCH SELFTEST FAIL"
  exit $rc
fi

test -n "$ARM" || { echo "ABORT usage: d6r2c_fm12_run_arm.sh <FM12|FM12R2|FM12R3> <image>  |  --selftest  |  --emit-cmd  |  --emit-grade-cmd"; exit 64; }
case "$ARM" in FM12|FM12R2|FM12R3) ;; *) echo "ABORT arm $ARM is not registered by this document"; exit 64 ;; esac
test -n "$IMG" || { echo "ABORT image required, pinned by digest"; exit 64; }
case "$IMG" in *"$IMG_PATCHED_DIGEST"*) ;; *) echo "ABORT G-IMG image is not the registered digest"; exit 4 ;; esac

guard_root "$BASE" || exit $?
guard_box || exit $?
guard_freeze || exit $?
guard_deps $STAGED_PY || exit 4

OCC_DOCKER=$(occupied_cpus)
OCC_BUSY=$(busy_cpus)
OCC=$(printf '%s,%s' "$OCC_DOCKER" "$OCC_BUSY" | sed 's/^,//; s/,$//')
CPUSET=$(free_cpuset "$RANKS" "$OCC" "$(nproc)") || {
  echo "ABORT G-CPUSET no $RANKS cores are free (occupied: ${OCC:-none})."
  echo "  THE ARM DOES NOT START.  Sharing cores with a live arm cost DEC7 fifteen"
  echo "  minutes at half speed.  Wait for the box instead."
  exit 5; }
guard_cpuset "$CPUSET" "$OCC" || exit 5
echo "D6R2C_FM12_CPUSET arm=$ARM chosen=$CPUSET nproc=$(nproc)"
echo "D6R2C_FM12_CPUSET   by container: ${OCC_DOCKER:-none}"
echo "D6R2C_FM12_CPUSET   by ${BUSY_PCT}%-busy sample over ${BUSY_INTERVAL}s: ${OCC_BUSY:-none}"

CAP=$(cap_core_min "$ARM"); test -n "$CAP" || { echo "ABORT no registered cap for arm $ARM"; exit 64; }
echo "D6R2C_FM12_CAP arm=$ARM cap_core_min=$CAP source=d6r2c_fm12_grade.py --print-cap"
python3 "$SRC/d6r2c_fm12_grade.py" --print-cost
LIVE=$(sudo -n docker ps --format '{{.Names}}' --filter "name=^d6r2c_fm12_${ARM}_" 2>/dev/null | head -3 | tr '\n' ',')
[ -n "$LIVE" ] && { echo "ABORT G-LIVE arm $ARM already running: $LIVE"; exit 3; }
mkdir -p "$BASE" && echo "ITEM=$ITEM" >> "$BASE/ledger.txt"
seed_arm "$ARM" || exit $?

STAMP=$(date -u +%Y%m%dT%H%M%SZ)_$$
NAME="d6r2c_fm12_${ARM}_${STAMP}"
WORK="$BASE/$ARM"
LOG="$BASE/${ARM}_${STAMP}.log"

CMDFILE="$WORK/d6r2c_fm12_cmd.sh"
container_cmd "$ARM" > "$CMDFILE"
echo "D6R2C_FM12_CMD arm=$ARM md5=$(md5sum "$CMDFILE" | cut -d' ' -f1)"

T0=$(date +%s)
sudo -n docker run -d --name "$NAME" \
    --user ${RUN_UID}:${RUN_GID} --group-add ${EXTRA_GID} -e HOME=/tmp \
    --cpus=$RANKS --cpuset-cpus=$CPUSET --memory=$MEM_LIMIT --memory-swap=$MEM_LIMIT \
    --oom-score-adj=500 \
    -v "$BASE":/mnt -v "$PARENT_BASE":/mnt/parent:ro \
    -w "/mnt/$ARM" "$IMG" bash -lc \
    ". /home/dafoamuser/dafoam/loadDAFoam.sh && bash /mnt/$ARM/d6r2c_fm12_cmd.sh" \
    > /dev/null 2>&1 || { echo "ABORT docker run failed"; exit 6; }
echo "D6R2C_FM12_LAUNCHED name=$NAME arm=$ARM uid=${RUN_UID}:${RUN_GID}+${EXTRA_GID} ranks=$RANKS cpuset=$CPUSET"

rotator "$WORK" &
ROT=$!
sudo -n docker wait "$NAME" > "$WORK/.arm_rc.txt" 2>/dev/null
RC=$(cat "$WORK/.arm_rc.txt" 2>/dev/null || echo 255)
kill "$ROT" 2>/dev/null
sudo -n docker logs "$NAME" > "$LOG" 2>&1
T1=$(date +%s)
WALL=$((T1 - T0))
CORE_MIN=$(awk -v w="$WALL" -v r="$RANKS" 'BEGIN{printf "%.3f", w*r/60}')
ROOT_OWNED=$(find "$WORK" -newermt "@$(cat "$WORK/.d6r2c_age_datum")" \( -uid 0 -o -gid 0 \) 2>/dev/null | wc -l)
{
  echo "ITEM=$ITEM"
  echo "D6R2C_FM12_ROW arm=$ARM name=$NAME rc=$RC wall_s=$WALL core_min=$CORE_MIN cap=$CAP root_owned=$ROOT_OWNED log=$LOG"
} >> "$BASE/ledger.txt"
awk -v c="$CORE_MIN" -v cap="$CAP" 'BEGIN{exit !(c>cap)}' && \
  echo "D6R2C_FM12_CAP_CROSSED arm=$ARM core_min=$CORE_MIN cap=$CAP -- the row is graded NOT A RESULT and THE CAP IS NEVER RAISED" | tee -a "$BASE/ledger.txt"
echo "D6R2C_FM12_DONE arm=$ARM rc=$RC core_min=$CORE_MIN cap=$CAP root_owned=$ROOT_OWNED"
echo "NOW GRADE:  $(grade_cmd "$ARM" "$WORK" "$CORE_MIN" "$RC" "$LOG" "$BASE/${ARM}_GRADE.json")"
exit 0

# ---------------------------------------------------------------------------
# THE REGISTERED md5 PINS.  G-FREEZE reads these lines out of this file, over
# the ONE canonical list $PINNED_PY.
# d6r2c_freshmesh.py, d6r2c_decomp.py, d6r2c_fm9_stage.py and d6r2c_dec5_decomp.py
# ARE REUSED UNCHANGED, BYTE FOR BYTE -- deform, mesh, the OpenFOAM readers, the
# trim and the governor are the same bytes that ran FM10 and DEC7.
# d6r2c_fm9_stage.py IN PARTICULAR KEEPS ITS REFUSE_FRESH_IS_BASE EXACTLY WHERE
# IT IS: FM12 does not weaken that guard, it stops routing Zb through it.
# The three new instruments are the stager, the producer and the grader, and the
# ONE CHANGE -- two extrusion-evidence gates instead of one -- is in the stager.
# PIN d6r2c_fm12_grade.py 8f344aabff28fbba394821ca0f88f496
# PIN d6r2c_fm12_states.py 612fb2e6d60320e1f225a2e7555eb1d1
# PIN d6r2c_fm12_stage.py d0d969a925da7e7b04ff35f8f8bb2d75
# PIN d6r2c_fm9_stage.py ea6d180fda38a3980bbb275b86d192c1
# PIN d6r2c_freshmesh.py 1d15ce361673ca600d565280441b67e0
# PIN d6r2c_decomp.py 42ec0dd582584812a69129a474b2783e
# PIN d6r2c_dec5_decomp.py fb19791784ebb73747c2f6c466a0d174
# PIN d6r2c_fm11_run_arm.sh b6972fc3dca1f45ed487519f8119ce60   (the file this one forks)
