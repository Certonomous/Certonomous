#!/usr/bin/env bash
# =====================================================================
# a3gc_run_selftest.sh -- **DRAFT, NOT FROZEN.**
#
# Proves a3gc_run.sh SATISFIES THE FROZEN COMPARATOR'S CONTRACT.  It does
# not assert it; it builds a case with the runner, fabricates a completed
# solve on top of it, and hands it to the REAL FROZEN a3gc_grade.py.
#
#   *** NO COMPUTE.  Every solve is FABRICATED.  Nothing here runs DAFoam,
#   docker or a solver, and no number it prints is a lab measurement. ***
#
#   *** A SUITE THAT PASSES PROVES NOTHING UNTIL IT IS SEEN TO FAIL.
#   Section M mutates the runner and requires a NAMED unit to go BAD. ***
#
# SUBMISSIONS PARKED.
# Usage: bash a3gc_run_selftest.sh [scratch-dir]
# =====================================================================
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN="$HERE/a3gc_run.sh"
GRADE="$HERE/a3gc_grade.py"
PY="${PYTHON:-python3}"
SCRATCH="${1:-${TMPDIR:-/tmp}/a3gc_run_selftest.$$}"
mkdir -p "$SCRATCH"
PROBE_DIR="/home/ubuntu/certonomous-runs/A3GC-mesh-family-probe"
S_C2="$PROBE_DIR/s_c2.cgns"

NPASS=0; NFAIL=0; FAILED=()
ok()  { NPASS=$((NPASS+1)); printf '  [PASS] %s\n' "$1"; }
bad() { NFAIL=$((NFAIL+1)); FAILED+=("$1"); printf '  [FAIL] %s\n' "$1"; }
head1(){ printf '\n== %s ==\n' "$1"; }
expect_rc(){ local w="$1" n="$2"; shift 2; local o r; o="$("$@" 2>&1)"; r=$?
  if [ "$r" = "$w" ]; then ok "$n (rc=$r)"; else bad "$n (wanted rc=$w, got rc=$r)"
    printf '%s\n' "$o" | tail -8 | sed 's/^/        | /'; fi; }
expect_out(){ local rx="$1" n="$2"; shift 2; local o; o="$("$@" 2>&1)"
  if printf '%s' "$o" | grep -qE "$rx"; then ok "$n"; else bad "$n (no match /$rx/)"
    printf '%s\n' "$o" | tail -8 | sed 's/^/        | /'; fi; }
expect_no_out(){ local rx="$1" n="$2"; shift 2; local o; o="$("$@" 2>&1)"
  if printf '%s' "$o" | grep -qE "$rx"; then bad "$n (matched /$rx/ and must not)"
  else ok "$n"; fi; }
expect_refusal(){ local c="$1" n="$2"; shift 2; local o r; o="$("$@" 2>&1)"; r=$?
  if [ "$r" = 2 ] && printf '%s' "$o" | grep -qE "REFUSE \[$c\]"; then ok "$n (rc=2, REFUSE [$c])"
  else bad "$n (wanted rc=2 AND REFUSE [$c]; got rc=$r)"
    printf '%s\n' "$o" | tail -8 | sed 's/^/        | /'; fi; }
filecheck(){ if [ "$2" = "$3" ]; then ok "$1"; else bad "$1 (expected=$2 got=$3)"; fi; }

printf '=====================================================================\n'
printf 'A3GC RUNNER SELFTEST (DRAFT)\nrunner   : %s\ngrader   : %s (md5 %s)\nscratch  : %s\n' \
  "$RUN" "$GRADE" "$(md5sum "$GRADE" | cut -d' ' -f1)" "$SCRATCH"
printf '=====================================================================\n'

# --- a fake genmesh OUTPUT: the layout a3gc_genmesh.sh really leaves behind,
#     INCLUDING the three files that collide with find_log's globs.
mkgenmesh() { "$PY" - "$@" <<'GPY'
import gzip, os, shutil, sys
B = ("// SYNTHETIC TEST FIXTURE from a3gc_run_selftest.sh.  NOT A MEASUREMENT.\n")
def build(root, ncells, nwing, surf, template):
    d = os.path.join(root, "constant", "polyMesh"); os.makedirs(d, exist_ok=True)
    with gzip.open(os.path.join(d, "owner.gz"), "wb") as fh:
        fh.write((B + 'FoamFile\n{\n version 2.0;\n note "nPoints:%d  nCells:%d  '
                 'nFaces:%d  nInternalFaces:%d";\n class labelList;\n object owner;\n}\n'
                 % (ncells + 1, ncells, ncells * 3, ncells * 3)).encode())
    t = B + "FoamFile\n{\n version 2.0;\n object boundary;\n}\n\n3\n(\n"
    for nm, ty, nf in (("wing", "wall", nwing), ("inout", "patch", nwing), ("sym", "symmetry", 8704)):
        t += "    %s\n    {\n        type %s;\n        nFaces %d;\n        startFace 1;\n    }\n" % (nm, ty, nf)
    open(os.path.join(d, "boundary"), "w").write(t + ")\n")
    shutil.copy(surf, os.path.join(root, "surfaceMesh.cgns"))
    # *** THE THREE COLLIDING ARTIFACTS a3gc_genmesh.sh really leaves. ***
    for nm in ("logMeshGeneration.txt", "checkMesh_plain.log",
               "checkMesh_allGeometry_allTopology.log"):
        open(os.path.join(root, nm), "w").write(B + "mesh provenance\n")
    os.makedirs(os.path.join(root, "system"), exist_ok=True)
if __name__ == "__main__":
    exec(sys.argv[1])
GPY
}
# --- a template with the 0.orig the runner cold-starts from
TPL="$SCRATCH/template"; mkdir -p "$TPL/0.orig"
for f in T U p alphat nut nuTilda; do printf 'placeholder initial condition\n' > "$TPL/0.orig/$f"; done

# --- fabricate a COMPLETED solve on top of a prepared case (NO COMPUTE)
fake_solve() { "$PY" - "$@" <<'FPY'
import os, re, sys, time
def run(wd, cd_hist, cl_hist, endtime=6000, printInterval=100, rc=0,
        end=True, write_end=True, last_time=None):
    L = ["// SYNTHETIC FABRICATED SOLVE.  NOT A MEASUREMENT.  No solver ran.",
         "DAFoam option dictionary: ", "{", "    solverName      DARhoSimpleCFoam;",
         "    primalMinResTol 1e-08;", "    printInterval   %d;" % printInterval,
         "    primalMinResTolDiff 100;", "}", "", "Starting time loop", ""]
    n = len(cd_hist)
    for i, (cd, cl) in enumerate(zip(cd_hist, cl_hist)):
        t = 1 if i == 0 else i * printInterval
        if last_time is not None and i == n - 1:
            t = last_time
        L.append("Time = %d" % t); L.append("")
        for eq in ("U0", "U1", "U2", "he", "p"):
            L.append("%s initRes: 1e-07 finalRes: 1e-08 nIters: 2" % eq)
        L.append("nuTilda initRes: 1e-07 finalRes: 1e-08 nIters: 3")
        L.append("CD: %.17g final: %.17g" % (cd, cd))
        L.append("CL: %.17g final: %.17g" % (cl, cl))
        L.append("ExecutionTime = %.2f s  ClockTime = %d s" % (20.0 * (i + 1), 20 * (i + 1)))
        L.append("")
    if end: L.append("End")
    open(os.path.join(wd, "primal.log"), "w").write("\n".join(L) + "\n")
    open(os.path.join(wd, "primal.log.rc"), "w").write("%d\n" % rc)
    if write_end:
        e = os.path.join(wd, str(endtime)); os.makedirs(e, exist_ok=True)
        for f in sorted(os.listdir(os.path.join(wd, "0"))):
            open(os.path.join(e, f), "w").write("// FABRICATED field at t=%d\n" % endtime)
def flat(v, n=12, j=1e-9): return [v + j * ((-1) ** i) for i in range(n)]
if __name__ == "__main__":
    exec(sys.argv[1])
FPY
}

# =====================================================================
head1 "Q -- THE QUARANTINE (AMENDMENT 3 G-QUARANTINE).  Tried three ways round."
# =====================================================================
# If the runner ever reads the feasibility probe, the probe was FIRST COMPUTE
# retroactively and AMENDMENT 3 -- and the freeze resting on it -- falls.
expect_refusal 'QUARANTINE' "Q1 --root inside the probe is REFUSED" \
  bash "$RUN" --level L3 --root /home/ubuntu/certonomous-runs/A3GC-meshgen-probe --dry-run
expect_refusal 'QUARANTINE' "Q2 --template inside the probe is REFUSED" \
  bash "$RUN" --level L3 --root "$SCRATCH" --template /home/ubuntu/certonomous-runs/A3GC-meshgen-probe/L3 --dry-run
expect_refusal 'QUARANTINE' "Q3 a probe path anywhere in --root is REFUSED" \
  bash "$RUN" --level L2 --root /home/ubuntu/certonomous-runs/A3GC-meshgen-probe/sub --dry-run
expect_out 'would retroactively make the probe|FIRST COMPUTE' \
  "Q4 the refusal says WHY, so nobody re-enables it to save mesh time" \
  bash "$RUN" --level L3 --root /home/ubuntu/certonomous-runs/A3GC-meshgen-probe --dry-run

# =====================================================================
head1 "P -- PREPARE writes what the FROZEN comparator reads"
# =====================================================================
R="$SCRATCH/runs"; mkdir -p "$R"
mkgenmesh 'build(sys.argv[2], 99840, 6240, sys.argv[3], sys.argv[4])' "$R/A3GC-L3" "$S_C2" "$TPL"
expect_rc 0 "P0 prepare succeeds on a registered L3" \
  bash "$RUN" --level L3 --root "$R" --template "$TPL" --stage prepare

# ---- the three traps, each checked in the file the runner actually wrote
expect_out 'primalMinResTol.*1\.0e-8' \
  "P1 runScript carries 1.0e-8, NOT the shipped 1.0e-6 (G-TOL refuses anything else)" \
  cat "$R/A3GC-L3/runScript_a3gc.py"
expect_no_out '"primalMinResTol": 1\.0e-6' \
  "P2 the shipped 1.0e-6 is never ASSIGNED (the docstring names it only to warn)" \
  cat "$R/A3GC-L3/runScript_a3gc.py"
expect_out '^endTime         6000;' \
  "P3 controlDict endTime is 6000, NOT the shipped 1500" cat "$R/A3GC-L3/system/controlDict"
expect_out '^numberOfSubdomains 4;' \
  "P4 decomposeParDict is np=4 for L3 (Sec.5), NOT the shipped 2" \
  cat "$R/A3GC-L3/system/decomposeParDict"

# ---- G-COMPLETE clause 3 needs this file to EXIST
filecheck "P5 system/controlDict exists (clause 3 REFUSES without it)" yes \
  "$([ -f "$R/A3GC-L3/system/controlDict" ] && echo yes || echo no)"

# ---- clause 4: writeInterval must divide endTime or endTime writes NO fields
expect_out '^writeInterval   2000;' "P6 writeInterval 2000 divides endTime 6000 exactly" \
  cat "$R/A3GC-L3/system/controlDict"

# ---- THE find_log COLLISION, REPAIRED.  Measured: a3gc_genmesh.sh leaves THREE
#      files matching `log*` or `*.log`, so find_log would REFUSE for ambiguity.
filecheck "P7 ZERO find_log candidates after prepare -- genmesh's 3 are cleared and no log exists yet" 0 \
  "$(ls -1 "$R/A3GC-L3" | grep -cE '^log|\.log$')"
filecheck "P8 and the mesh provenance was MOVED, not deleted" 3 \
  "$(ls -1 "$R/A3GC-L3/meshgen" 2>/dev/null | wc -l)"

# ---- THE AGE-GUARD ORDERING IS PRODUCED, NOT HOPED FOR
filecheck "P9 0/T is STRICTLY newer than every other 0-field -- it dates the run allowed to answer" T \
  "$("$PY" -c "
import os,sys
d=sys.argv[1]
m={f:os.stat(os.path.join(d,f)).st_mtime for f in os.listdir(d)}
t=m.pop('T')
print('T' if all(t>v for v in m.values()) else 'NOT-STRICTLY-NEWEST')
" "$R/A3GC-L3/0")"

# =====================================================================
head1 "E -- END TO END: the FROZEN comparator grades what the runner built"
# =====================================================================
# The strongest unit in this file.  The runner prepares all three levels; a
# COMPLETED solve is FABRICATED on top (no compute); the REAL FROZEN
# a3gc_grade.py grades it.  If G-COMPLETE refuses this, the runner does not
# satisfy the contract and that is a finding, not a test to relax.
for spec in "L3:99840:6240" "L2:798720:24960" "L1:6389760:99840"; do
  IFS=: read -r lv nc nw <<<"$spec"
  [ -d "$R/A3GC-$lv" ] || mkgenmesh "build(sys.argv[2], $nc, $nw, sys.argv[3], sys.argv[4])" "$R/A3GC-$lv" "$S_C2" "$TPL"
  bash "$RUN" --level "$lv" --root "$R" --template "$TPL" --stage prepare >/dev/null 2>&1
done
# distinct surfaces so G-SYS limb 3 / G-NEST see a real family
cp "$PROBE_DIR/s_c1.cgns" "$R/A3GC-L2/surfaceMesh.cgns"
cp "$PROBE_DIR/m6_surfaceMesh_fine.cgns" "$R/A3GC-L1/surfaceMesh.cgns"
fake_solve 'run(sys.argv[2], flat(0.0239956), flat(0.3181159), last_time=6000)' "$R/A3GC-L3"
fake_solve 'run(sys.argv[2], flat(0.0231956), flat(0.3141159), last_time=6000)' "$R/A3GC-L2"
fake_solve 'run(sys.argv[2], flat(0.0229956), flat(0.3131159), last_time=6000)' "$R/A3GC-L1"
filecheck "E0 exactly ONE find_log candidate once solved (genmesh left 3; find_log refuses on >=2)" 1 "$(ls -1 "$R/A3GC-L3" | grep -cE '^log|[.]log$')"
EE=( --l3 "$R/A3GC-L3" --l2 "$R/A3GC-L2" --l1 "$R/A3GC-L1" --log-name primal.log )
expect_out 'G-COMPLETE: all six clauses hold for L3' \
  "E1 ALL SIX G-COMPLETE CLAUSES HOLD on a case this runner built" "$PY" "$GRADE" grade "${EE[@]}"
expect_out '1 rc == 0 +OK' "E2 clause 1: the rc artifact is where the comparator looks" "$PY" "$GRADE" grade "${EE[@]}"
expect_out '3 last time == endTime +OK +last printed Time = 6000, controlDict endTime = 6000' \
  "E3 clause 3: the runner's controlDict endTime matches the log's last Time" "$PY" "$GRADE" grade "${EE[@]}"
expect_out '4 fields at endTime +OK' "E4 clause 4: every 0-field is present at endTime" "$PY" "$GRADE" grade "${EE[@]}"
expect_out '6 AGE GUARD +OK +all [0-9]+ endTime field\(s\) NEWER than' \
  "E5 clause 6: THE AGE-GUARD ORDERING THE RUNNER PRODUCED SURVIVES GRADING" "$PY" "$GRADE" grade "${EE[@]}"
expect_out 'accept floor \(PRODUCT, N-D43\) = 1e-06' \
  "E6 G-TOL accepts the runner's registered 1e-8 x 100" "$PY" "$GRADE" grade "${EE[@]}"
expect_out 'VERDICT  CD triple +: PASS' "E7 and the triple grades" "$PY" "$GRADE" grade "${EE[@]}"
# find_log with NO --log-name must now be unambiguous, which is the whole point of P7
expect_out 'G-COMPLETE: all six clauses hold for L3' \
  "E8 and find_log resolves WITHOUT --log-name (the genmesh collision is gone)" \
  "$PY" "$GRADE" grade --l3 "$R/A3GC-L3" --l2 "$R/A3GC-L2" --l1 "$R/A3GC-L1"

# =====================================================================
head1 "G -- PREPARE REFUSES what it must"
# =====================================================================
mkgenmesh 'build(sys.argv[2], 12345, 6240, sys.argv[3], sys.argv[4])' "$SCRATCH/bad/A3GC-L3" "$S_C2" "$TPL"
expect_refusal 'PREPARE' "G1 a wrong cell count is a LAUNCH-BLOCKING refusal (Sec.2.5)" \
  bash "$RUN" --level L3 --root "$SCRATCH/bad" --template "$TPL" --stage prepare
mkgenmesh 'build(sys.argv[2], 99840, 1560, sys.argv[3], sys.argv[4])' "$SCRATCH/imp/A3GC-L3" "$S_C2" "$TPL"
expect_refusal 'PREPARE' "G2 the 99,840-cell IMPOSTOR (wing 1560) is refused on face count" \
  bash "$RUN" --level L3 --root "$SCRATCH/imp" --template "$TPL" --stage prepare
mkdir -p "$R/A3GC-L3/1000"
expect_refusal 'PREPARE' "G3 a stray time directory REFUSES (Sec.3.3 G-COLD, no clean-up-and-proceed)" \
  bash "$RUN" --level L3 --root "$R" --template "$TPL" --stage prepare
rmdir "$R/A3GC-L3/1000"
expect_refusal 'ARGS' "G4 an unknown level is refused" bash "$RUN" --level L9 --root "$R" --dry-run
expect_refusal 'PREPARE' "G5 a missing case dir refuses and names genmesh, never the probe" \
  bash "$RUN" --level L2 --root "$SCRATCH/nothing" --template "$TPL" --stage prepare

# =====================================================================
head1 "W -- THE rc IS CAPTURED INSIDE THE DETACHED WRAPPER"
# =====================================================================
bash "$RUN" --level L3 --root "$R" --template "$TPL" --stage launch --dry-run >/dev/null 2>&1
W="$R/A3GC-L3/_a3gc_wrapper.sh"
filecheck "W1 the wrapper exists" yes "$([ -f "$W" ] && echo yes || echo no)"
expect_out 'rc=\$\?' "W2 the wrapper captures \$? INSIDE itself" cat "$W"
expect_no_out 'setsid' "W3 and the wrapper itself contains NO setsid -- the rc is not taken around it" cat "$W"
expect_out 'setsid nohup' "W4 the DETACHMENT is in the runner, outside the rc capture" grep -n 'setsid' "$RUN"
expect_out 'primal\.log\.rc' "W5 the rc lands exactly where the frozen comparator looks" cat "$W"
expect_out 'EXITS 0 FOR EVERY OUTCOME' \
  "W6 the runner records WHY, so nobody 'simplifies' it back" grep -A2 'setsid timeout' "$RUN"

# =====================================================================
head1 "M -- MUTATION CONTROLS: each removes one guarantee and NAMES its catcher"
# =====================================================================
MUT="$SCRATCH/mutants"; mkdir -p "$MUT"
# A mutant resolves its grader from its OWN directory (BASH_SOURCE), so without
# this it refuses at "the frozen comparator could not read ..." BEFORE reaching
# the guarantee under test -- a mutation control that dies early proves nothing.
# SYMLINK, never copy: every mutant must resolve the ONE frozen file.
ln -sf "$GRADE" "$MUT/a3gc_grade.py"
mutate() { "$PY" - "$RUN" "$MUT/$1.sh" "$2" "$3" <<'MPY'
import sys
src, dst, old, new = sys.argv[1:5]
s = open(src, encoding="utf-8").read()
n = s.count(old)
if n != 1:
    sys.stderr.write("MUTATOR REFUSE: pattern occurs %d times, not once\n" % n); sys.exit(3)
open(dst, "w", encoding="utf-8").write(s.replace(old, new))
MPY
}
mut_must_fail() { local tag="$1" catcher="$2" rx="$3"; shift 3
  if [ ! -s "$MUT/$tag.sh" ]; then bad "M-$tag mutator built nothing (planted-zero guard)"; return; fi
  if cmp -s "$RUN" "$MUT/$tag.sh"; then bad "M-$tag mutant IDENTICAL to the original"; return; fi
  local o; o="$("$@" 2>&1)"
  if printf '%s' "$o" | grep -qE "$rx"; then
    bad "M-$tag THE SUITE FAILED TO FAIL: [$catcher] still matches /$rx/"
    printf '%s\n' "$o" | tail -6 | sed 's/^/        | /'
  else ok "M-$tag mutation caught; the catcher is [$catcher]"; fi; }

# M1 THE TOLERANCE TRAP REINSTATED -- the single most expensive defect available:
#    three complete solves, all three refused by the frozen G-TOL at grading.
mutate TOLERANCE-REVERTED 'PRIMAL_MIN_RES_TOL="1.0e-8"' 'PRIMAL_MIN_RES_TOL="1.0e-6"' \
  && { rm -rf "$SCRATCH/m1"; mkgenmesh 'build(sys.argv[2], 99840, 6240, sys.argv[3], sys.argv[4])' "$SCRATCH/m1/A3GC-L3" "$S_C2" "$TPL"
       bash "$MUT/TOLERANCE-REVERTED.sh" --level L3 --root "$SCRATCH/m1" --template "$TPL" --stage prepare >/dev/null 2>&1
       mut_must_fail TOLERANCE-REVERTED 'P1/P2' '"primalMinResTol": 1\.0e-8' \
         cat "$SCRATCH/m1/A3GC-L3/runScript_a3gc.py"; }
expect_out '"primalMinResTol": 1\.0e-6' \
  "M1b the mutant is SEEN to ASSIGN the shipped tolerance that G-TOL refuses" \
  cat "$SCRATCH/m1/A3GC-L3/runScript_a3gc.py"

# M2 THE QUARANTINE DISABLED -- the probe would be consumed.
mutate QUARANTINE-OFF "    *\"\$QUARANTINED\"*)" "    'never-matches-anything')" \
  && mut_must_fail QUARANTINE-OFF 'Q1/Q2/Q3' 'REFUSE \[QUARANTINE\]' \
       bash "$MUT/QUARANTINE-OFF.sh" --level L3 --root /home/ubuntu/certonomous-runs/A3GC-meshgen-probe --dry-run

# M3 THE find_log COLLISION LEFT UNREPAIRED -- genmesh's three artifacts stay and
#    the comparator refuses the case for log ambiguity.
mutate LOGS-NOT-MOVED '      mv -f "$f" "$WD/meshgen/"' '      : # MUTATION: left in place' \
  && { rm -rf "$SCRATCH/m3"; mkgenmesh 'build(sys.argv[2], 99840, 6240, sys.argv[3], sys.argv[4])' "$SCRATCH/m3/A3GC-L3" "$S_C2" "$TPL"
       bash "$MUT/LOGS-NOT-MOVED.sh" --level L3 --root "$SCRATCH/m3" --template "$TPL" --stage prepare >/dev/null 2>&1
       mut_must_fail LOGS-NOT-MOVED 'P7/E8' '^1$' \
         sh -c "ls -1 '$SCRATCH/m3/A3GC-L3' | grep -cE '^log|\.log\$'"; }

# M4 THE AGE-GUARD ORDERING REMOVED -- 0/T is no longer touched last.
mutate AGE-ORDER-REMOVED '    touch "$WD/0/T"  # *** LAST.  This timestamps the run allowed to answer. ***' \
  '    : # MUTATION: 0/T no longer touched last' \
  && { rm -rf "$SCRATCH/m4"; mkgenmesh 'build(sys.argv[2], 99840, 6240, sys.argv[3], sys.argv[4])' "$SCRATCH/m4/A3GC-L3" "$S_C2" "$TPL"
       bash "$MUT/AGE-ORDER-REMOVED.sh" --level L3 --root "$SCRATCH/m4" --template "$TPL" --stage prepare >/dev/null 2>&1
       mut_must_fail AGE-ORDER-REMOVED 'P9' '^T$' \
         sh -c "'$PY' -c \"
import os,sys
d=sys.argv[1]
m={f:os.stat(os.path.join(d,f)).st_mtime for f in os.listdir(d)}
t=m.pop('T')
print('T' if all(t>v for v in m.values()) else 'NOT-STRICTLY-NEWEST')
\" '$SCRATCH/m4/A3GC-L3/0'"; }

# M5 writeInterval STOPS DIVIDING endTime -- endTime would write NO FIELDS and
#    G-COMPLETE clause 4 would correctly call a finished run incomplete.
mutate WRITEINTERVAL-INDIVISIBLE 'WRITE_INTERVAL="2000"' 'WRITE_INTERVAL="700"' \
  && { rm -rf "$SCRATCH/m5"; mkgenmesh 'build(sys.argv[2], 99840, 6240, sys.argv[3], sys.argv[4])' "$SCRATCH/m5/A3GC-L3" "$S_C2" "$TPL"
       mut_must_fail WRITEINTERVAL-INDIVISIBLE 'the runner own guard' '^writeInterval' \
         sh -c "bash '$MUT/WRITEINTERVAL-INDIVISIBLE.sh' --level L3 --root '$SCRATCH/m5' --template '$TPL' --stage prepare 2>&1; cat '$SCRATCH/m5/A3GC-L3/system/controlDict' 2>/dev/null"; }
expect_out 'write NO FIELDS' \
  "M5b and the runner's own refusal explains the consequence" \
  sh -c "bash '$MUT/WRITEINTERVAL-INDIVISIBLE.sh' --level L3 --root '$SCRATCH/m5' --template '$TPL' --stage prepare 2>&1"

# M6 THE rc CAPTURED AROUND setsid INSTEAD OF INSIDE -- the defect the comparator's
#    own refusal text warns about: `setsid timeout cmd` exits 0 for every outcome.
mutate RC-AROUND-SETSID 'rc=\$?' 'rc=0  # MUTATION: not the real exit code' \
  && { rm -rf "$SCRATCH/m6"; mkgenmesh 'build(sys.argv[2], 99840, 6240, sys.argv[3], sys.argv[4])' "$SCRATCH/m6/A3GC-L3" "$S_C2" "$TPL"
       bash "$MUT/RC-AROUND-SETSID.sh" --level L3 --root "$SCRATCH/m6" --template "$TPL" --stage all --dry-run >/dev/null 2>&1
       mut_must_fail RC-AROUND-SETSID 'W2' 'rc=\$\?' cat "$SCRATCH/m6/A3GC-L3/_a3gc_wrapper.sh"; }

printf '\n=====================================================================\n'
printf 'RUNNER SELFTEST   passed=%d   failed=%d\n' "$NPASS" "$NFAIL"
if [ "$NFAIL" -ne 0 ]; then printf 'FAILED:\n'; for t in "${FAILED[@]}"; do printf '  - %s\n' "$t"; done; fi
printf 'scratch kept at %s\n' "$SCRATCH"
printf '=====================================================================\n'
[ "$NFAIL" -eq 0 ]
