#!/usr/bin/env bash
# ===========================================================================
# d6r2c_fm13_prefreeze.sh -- THE THREE CLAUSES OF DAFOAM_CHARTER.md sec 22.4,
#                            DRIVEN, BEFORE THE FREEZE SHA.
# ===========================================================================
#
#   (a) EVERY INSTRUMENT NAMED IN THE FROZEN TABLE EXISTS AT ITS STATED md5.
#       This script READS THE REGISTRATION'S OWN TABLE -- it carries no list of
#       its own -- hashes every file the table names, and fails on a row whose
#       file is absent, whose md5 is missing, or whose md5 disagrees.  "A table
#       that is TRUE AS WRITTEN about files that do not exist is how the defect
#       survived" (L-579).
#
#   (b) THE CHECK DRIVES THE EXACT CLI THE LAUNCHER EMITS, AGAINST THE REAL
#       ANCHOR FILES.  ***THIS CLAUSE IS TIGHTER THAN FM11's AND THAT IS THE
#       POINT.***  FM11's clause (b) asked the launcher for the command and then
#       ran it with `--evals SYNTHETIC --fm10-record SYNTHETIC`: IT DROVE THE
#       COMMAND LINE AND NOT THE DATA THE COMMAND LINE READS.  That is L-595
#       surviving its own lesson, and it hid a live defect -- the grader's `_J`
#       could not read `obj.J` out of the real record and would have REFUSED
#       `REFUSE_NO_J_IN_RECORD` on the very anchor it was written for.
#
#       FOR FM12: the emitted command is run VERBATIM, with NOT ONE FLAG
#       ALTERED, so it reads the REAL `d6r2c_evals.jsonl` and the REAL FM10
#       record through the launcher's own defaults.  The synthetic-anchor form
#       is run too, as an ADDITIONAL case, and is reported SEPARATELY.  If the
#       real anchors make the check slow, it runs anyway.
#
#   (c) EVERY CHANNEL A GATE READS HAS A WRITER THAT RAN.  `primal_residual.json`
#       -- four readers, zero writers, zero files on disk, default True -- stays
#       DELETED from these instruments, asserted by a sweep that is itself driven
#       to its failing side.  H4 reads the ARM LOG, whose writer is the solver.
#
# AND THE GATES THIS ARM ADDS, EACH DRIVEN FROM OUTSIDE THE INSTRUMENT THAT
# OWNS IT, AND EACH AGAINST THE REAL ARTIFACTS WHERE THEY EXIST:
#   * M0b and M0o are driven to their FAILING SIDES on FM11's own disk;
#   * R1 is driven at zero and at a planted non-zero;
#   * G-WALL is driven to its failing side with a planted point cloud;
#   * every verification constant is DERIVED in the same invocation and the
#     DERIVED value is the one used.
#
# IT FREEZES NOTHING AND LAUNCHES NOTHING.  It prints PASS or FAIL and exits.
# SUBMISSIONS PARKED (rule 7).
# ===========================================================================
set -uo pipefail

SRC=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C
REG="$SRC/PREREGISTRATION_FM13_GUARDED_WRITE.md"
LAUNCHER="$SRC/d6r2c_fm13_run_arm.sh"
DEFORM="$SRC/d6r2c_fm13_deform.py"
CORRUPT=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM12-a2-wing-matched-lift-provenance/FM12/Zo/surfaceMesh_final.cgns
GOOD=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM12-a2-wing-matched-lift-provenance/FM12/Zo/surfaceMesh_base.cgns
IMG=dafoam-idwarp-rot:v1
REAL_EVALS=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/O_mp/d6r2c_evals.jsonl
REAL_FM10=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM9-a2-wing-freshmesh-arrives/FM10/d6r2c_freshmesh.json
rc=0
ok()   { echo "PREFREEZE ok   $*"; }
fail() { echo "PREFREEZE FAIL $*"; rc=1; }

echo "=== (a) EVERY INSTRUMENT IN THE FROZEN TABLE EXISTS AT ITS STATED md5 ==="
TABLE=$(awk '/^## 6\./{f=1} f&&/^## 7\./{f=0} f' "$REG" | grep -E '^\| *`[a-zA-Z0-9_.]+` *\|')
N_ROWS=$(printf '%s\n' "$TABLE" | grep -c . )
[ "$N_ROWS" -ge 6 ] || fail "the instrument table has only $N_ROWS parsable rows"
while IFS= read -r row; do
  [ -z "$row" ] && continue
  F=$(printf '%s' "$row" | sed -n 's/^| *`\([^`]*\)`.*/\1/p')
  M=$(printf '%s' "$row" | grep -oE '[0-9a-f]{32}' | head -1)
  if [ -z "$F" ]; then fail "a table row names no file: $row"; continue; fi
  if [ ! -f "$SRC/$F" ]; then fail "$F is named in the frozen table AND DOES NOT EXIST"; continue; fi
  if [ -z "$M" ]; then fail "$F is in the table with NO md5 -- this is the L-579 defect exactly"; continue; fi
  G=$(md5sum "$SRC/$F" | cut -d' ' -f1)
  if [ "$G" = "$M" ]; then ok "$F exists at its stated md5 $M"
  else fail "$F md5 on disk $G, table says $M"; fi
done <<< "$TABLE"
PROBE="| \`d6r2c_fm13_does_not_exist.py\` | NOT BUILT | 00000000000000000000000000000000 |"
PF=$(printf '%s' "$PROBE" | sed -n 's/^| *`\([^`]*\)`.*/\1/p')
[ ! -f "$SRC/$PF" ] && ok "the row parser resolves a file name out of a table row, and would report this synthetic row as MISSING" \
  || fail "the synthetic probe row unexpectedly exists"
# and the pinned list in the launcher is the list the table carries -- ONE list
for f in $(bash "$LAUNCHER" --print-pinned); do
  printf '%s\n' "$TABLE" | grep -q "\`$f\`" \
    && ok "the launcher's pinned $f is a row of the frozen table" \
    || fail "the launcher pins $f and the frozen table does not name it"
done

echo
echo "=== (b1) THE EMITTED CLI, VERBATIM, AGAINST THE **REAL** ANCHOR FILES ===="
echo "     This is the clause FM11 had and did not honour.  No flag is altered."
[ -f "$REAL_EVALS" ] && ok "the real optimiser record is on disk: $REAL_EVALS" \
  || fail "the real optimiser record is NOT on disk -- clause (b) cannot be honoured"
[ -f "$REAL_FM10" ] && ok "the real FM10 record is on disk: $REAL_FM10" \
  || fail "the real FM10 record is NOT on disk -- clause (b) cannot be honoured"

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
# The ARM TREE must be synthetic -- the run has not happened and cannot have.
# THE ANCHORS ARE NOT.  The tree is built from the values READ OUT OF THE REAL
# ANCHORS IN THIS INVOCATION, so the command below reads real files through the
# launcher's own defaults and still lands on a decidable verdict.
python3 - "$TMP" "$REAL_EVALS" "$REAL_FM10" <<'PY' || fail "could not build the synthetic arm from the REAL anchors"
import os, sys, json
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C")
import d6r2c_fm13_grade as G
tmp, evals, fm10p = sys.argv[1], sys.argv[2], sys.argv[3]
inh = G.load_inherited(evals)            # THE REAL RECORD, through the real reader
f10 = G.load_fm10(fm10p)                 # THE REAL FM10 RECORD
root = os.path.join(tmp, "FM13"); os.makedirs(root)
on = {p: G.CL_TARGETS[p] for p in G.POINTS}
Jb = inh["J0"]
Jo = Jb * (inh["Jf"] / inh["J0"])        # R_fresh sits on R_def exactly
G._synth_arm(root, Jb, Jo, cl_base=on, cl_opt=on,
             cl_ez={p: G.CL_TARGETS[p] + 0.004 for p in G.POINTS},
             J_do=f10["J"], cl_do=dict(f10["CL"]))
G._synth_log(tmp, n_blocks=8, settled=True, name="FM13.log")
open(os.path.join(root, ".d6r2c_age_datum"), "w").write("0\n")
print("PREFREEZE ok   the arm tree is built from the REAL anchors read in this "
      "invocation: J0=%.17g Jf=%.17g R_def=%.12f FM10 J=%.12g"
      % (inh["J0"], inh["Jf"], inh["Jf"] / inh["J0"], f10["J"]))
PY

GRADE_CMD=$(bash "$LAUNCHER" --emit-grade-cmd FM13 "$TMP/FM13" 10.000 0 \
            "$TMP/FM13.log" "$TMP/FM13_GRADE.json")
echo "PREFREEZE the launcher emits: $GRADE_CMD"
# ---- RUN IT VERBATIM.  NOT ONE FLAG ADDED, NOT ONE SUBSTITUTED. -------------
OUT=$(eval "$GRADE_CMD" 2>&1); GRC=$?
if [ $GRC -eq 0 ]; then ok "(b1) THE LAUNCHER'S OWN GRADING COMMAND RUNS **VERBATIM, AGAINST THE REAL ANCHORS** AND RETURNS 0"
else fail "(b1) the launcher's own grading command, run verbatim against the real anchors, exited $GRC:"; echo "$OUT"; fi
case "$OUT" in
  *"label=PASS"*) ok "(b1) ... and it returns a real verdict on real anchors, not NOT A RESULT by construction" ;;
  *) fail "(b1) the emitted command did not produce a PASS on a tree built from the real anchors to pass:"; echo "$OUT" ;;
esac
case "$OUT" in
  *"R_def=0.752677271"*) ok "(b1) ... and R_def READ OUT OF THE REAL RECORD is 0.752677271 -- the registered anchor, reproduced by the command that will grade this arm" ;;
  *) fail "(b1) the emitted command did not reproduce R_def from the real record"; echo "$OUT" ;;
esac
[ -f "$TMP/FM13_GRADE.json" ] && ok "(b1) ... and it WROTE the verdict file the launcher names" \
  || fail "(b1) the emitted command wrote no verdict file"
# THE NEGATIVE THAT MAKES (b1) NON-VACUOUS: FM11's reader, on the same real
# file, CANNOT find J -- so the green above is the repair working and not the
# check being blind.
python3 - "$REAL_EVALS" <<'PY' || fail "(b1) the FM11-reader negative did not run"
import json, sys
f = {}
for line in open(sys.argv[1]):
    r = json.loads(line)
    if r.get("kind") == "F" and r.get("n") is not None:
        f[int(r["n"])] = r
fu = f[88].get("funcs") or {}
old = [k for k in ("obj", "J", "fun", "weighted_CD") if k in fu]
new = [k for k in ("obj.J", "obj", "J", "fun", "weighted_CD") if k in fu]
cd  = [k for k in fu if k.endswith("CD")]
assert old == [], old
assert new == ["obj.J"], new
assert cd == [], cd
print("PREFREEZE ok   (b1) THE NEGATIVE: on this same REAL record FM11's key "
      "chain finds NOTHING (%r) and carries no per-condition CD (%r), so its "
      "emitted command could only REFUSE_NO_J_IN_RECORD.  FM12's chain finds "
      "%r.  The (b1) green above is the repair, not blindness." % (old, cd, new))
PY
# and the arm-shape negative: the same verbatim command with a sub-arm deleted
rm -rf "$TMP/FM13/Zo"
eval "$GRADE_CMD" >/dev/null 2>&1 && fail "(b1) the emitted command PASSED with half the arm deleted" \
  || ok "(b1) ... and the same verbatim command REFUSES when a sub-arm is missing"

echo
echo "=== (b2) THE SAME CLI ON SYNTHETIC ANCHORS -- AN **ADDITIONAL** CASE ====="
echo "     Reported separately.  This is the case FM11 ran as its ONLY case."
TMP2=$(mktemp -d)
python3 - "$TMP2" <<'PY' || fail "(b2) could not build the synthetic arm"
import os, sys
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C")
import d6r2c_fm13_grade as G
root = os.path.join(sys.argv[1], "FM13"); os.makedirs(root)
on = {p: G.CL_TARGETS[p] for p in G.POINTS}
Jb = 0.0306416314389976151
Jo = Jb * (0.0230632595286777639 / Jb)
G._synth_arm(root, Jb, Jo, cl_base=on, cl_opt=on,
             cl_ez={p: G.CL_TARGETS[p] + 0.004 for p in G.POINTS},
             J_do=0.036964341844,
             cl_do={p: G.CL_TARGETS[p] + v for p, v in
                    (("cl04", 0.149286), ("cl05", 0.151566), ("cl06", 0.152398))})
G._synth_log(sys.argv[1], n_blocks=8, settled=True, name="FM13.log")
open(os.path.join(root, ".d6r2c_age_datum"), "w").write("0\n")
PY
GC2=$(bash "$LAUNCHER" --emit-grade-cmd FM13 "$TMP2/FM13" 10.000 0 \
      "$TMP2/FM13.log" "$TMP2/FM13_GRADE.json")
O2=$(eval "$GC2 --evals SYNTHETIC --fm10-record SYNTHETIC" 2>&1); R2=$?
if [ $R2 -eq 0 ]; then
  case "$O2" in
    *"label=PASS"*) ok "(b2) the same command with SYNTHETIC anchors also returns PASS -- reported as an ADDITIONAL case, never as the only one" ;;
    *) fail "(b2) synthetic-anchor run returned no PASS"; echo "$O2" ;;
  esac
else fail "(b2) synthetic-anchor run exited $R2"; echo "$O2"; fi
rm -rf "$TMP2"

echo
echo "=== (b3.0) THE **GUARDED DEFORM PRODUCER'S** VECTOR, FROM THE EMITTED BLOCK ="
DARGS=$(bash "$LAUNCHER" --emit-cmd FM13 | tr '\n' ' ' | tr -d '\\' \
        | grep -oE "python d6r2c_fm13_deform\.py --phase deform [^|]*--surface-out [^ ]+" | head -1)
if [ -n "$DARGS" ]; then
  ok "the emitted block runs the GUARDED producer on the deform phase: ${DARGS:0:70}..."
else
  fail "the emitted block does not run d6r2c_fm13_deform.py --phase deform"
fi
bash "$LAUNCHER" --emit-cmd FM13 | grep -q "d6r2c_freshmesh.py --phase deform" \
  && fail "the UNGUARDED collective write d6r2c_freshmesh.py --phase deform is still emitted" \
  || ok "d6r2c_freshmesh.py --phase deform -- the unguarded collective write that BLOCKED FM12 -- is NOT emitted"
# and the producer must REFUSE a phase it is not registered for
O=$(cd "$SRC" && python3 d6r2c_fm13_deform.py --phase solve 2>&1)
case "$O" in *REFUSE_PHASE*) ok "the guarded producer REFUSES --phase solve; it is registered for deform only" ;;
             *) fail "the guarded producer did not refuse an unregistered phase: $O" ;; esac

echo "=== (b3) THE PRODUCER'S OWN ARGUMENT VECTOR, LIFTED FROM THE EMITTED BLOCK"
for SA in Zb Zo; do
  ARGS=$(bash "$LAUNCHER" --emit-cmd FM13 | tr '\n' ' ' | tr -d '\\' \
         | grep -oE "python d6r2c_fm12_states\.py [^|]*--sub-arm $SA [^|]*--datum-file [^ ]+" | head -1)
  ARGS=${ARGS#python d6r2c_fm12_states.py }
  ARGS=$(printf '%s' "$ARGS" | sed "s|\"\$PWD\"|$TMP/FM13|")
  O=$(cd "$SRC" && python3 d6r2c_fm12_states.py --parse-only $ARGS 2>&1)
  case "$O" in
    *"PARSE_ONLY sub_arm=$SA"*) ok "(b3) the producer accepts the EXACT vector the container hands it for $SA" ;;
    *) fail "(b3) the producer rejected its own emitted vector for $SA:"; echo "$O" ;;
  esac
  case "$O" in
    *"datum_file=/mnt/FM13/.d6r2c_age_datum"*) ok "(b3) ... and that vector CARRIES the age datum M0b's load-bearing limb needs" ;;
    *) fail "(b3) the emitted vector for $SA carries no --datum-file"; echo "$O" ;;
  esac
done
# THE NEGATIVE: the producer REFUSES to run with no datum, rather than defaulting
O=$(cd "$SRC" && python3 d6r2c_fm12_states.py --arm-dir "$TMP/FM13" --sub-arm Zb 2>&1)
case "$O" in
  *REFUSE_NO_DATUM_FILE*) ok "(b3) the producer REFUSES to run with no age datum -- a provenance gate with no clock is not a gate" ;;
  *) fail "(b3) the producer did not refuse a missing datum:"; echo "$O" ;;
esac
bash "$LAUNCHER" --emit-cmd FM13 | grep -q -- "--phase solve" \
  && fail "d6r2c_freshmesh.py --phase solve -- THE DOUBLE APPLICATION -- is still in the emitted block" \
  || ok "the emitted block never calls the producer whose double application made FM10 NOT A RESULT"

echo
echo "=== (c) EVERY CHANNEL A GATE READS HAS A WRITER THAT RAN =================="
FM12_FILES="d6r2c_fm12_states.py d6r2c_fm13_grade.py d6r2c_fm12_stage.py d6r2c_fm13_run_arm.sh d6r2c_fm13_deform.py"
read_sites() { grep -nE 'primal_residual.*(open\(|json\.load|os\.path\.join|isfile|exists)|(open\(|json\.load|os\.path\.join|isfile|exists).*primal_residual' "$1"; }
HITS=0
for f in $FM12_FILES; do
  H=$(read_sites "$SRC/$f" | wc -l); HITS=$((HITS + H))
done
[ "$HITS" -eq 0 ] && ok "ZERO live READ SITES for primal_residual.json in the FM13 instruments -- the channel is DELETED, not read more carefully" \
  || { fail "the FM13 instruments still carry $HITS read site(s) for primal_residual.json"; \
       for f in $FM12_FILES; do read_sites "$SRC/$f" | head -5; done; }
INH=$(read_sites "$SRC/d6r2c_freshmesh.py" | wc -l)
[ "$INH" -gt 0 ] && ok "the same sweep FINDS $INH real read site(s) in the inherited d6r2c_freshmesh.py -- it is not simply blind" \
  || fail "the sweep found no read site even in the file known to carry the channel"
FM10LOG=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM9-a2-wing-freshmesh-arrives/FM10_20260913T163543Z_1546115.log
if [ -f "$FM10LOG" ]; then
  NCD=$(grep -c "^CD: " "$FM10LOG")
  [ "$NCD" -gt 0 ] && ok "H4's channel has a WRITER THAT RAN: $NCD 'CD:' lines written by the solver itself in FM10's own arm log" \
    || fail "the arm log carries no CD series -- H4's channel has no writer either"
  python3 - "$FM10LOG" <<'PY' || fail "the log limb could not read a real arm log"
import sys
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C")
import d6r2c_fm13_grade as G
r = G.grade_log(sys.argv[1], 1.0e-5)
print("PREFREEZE ok   the log limb reads a REAL arm log: %d primal blocks, "
      "worst last-step relative CD change %.3e, all_settled=%s"
      % (r["n_primal_blocks"], r["worst_rel_change_last_step"], r["all_settled"]))
PY
else
  fail "FM10's arm log is not on disk -- the writer claim cannot be shown"
fi
python3 - <<'PY' || fail "the log limb did not refuse an absent writer"
import sys
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C")
import d6r2c_fm13_grade as G
try:
    G.grade_log("/tmp/there-is-no-such-log-anywhere.log", 1.0e-5)
    print("PREFREEZE FAIL the log limb accepted an absent log"); sys.exit(1)
except G.Refusal as e:
    assert str(e).startswith("REFUSE_NO_ARM_LOG"), e
print("PREFREEZE ok   the log limb REFUSES an absent writer -- an absent source "
      "is NOT zero failures (rule 3)")
PY

echo
echo "=== M0b AND M0o, EACH DRIVEN TO ITS FAILING SIDE ON THE REAL DISK ========"
LIVE=$(python3 "$SRC/d6r2c_fm12_stage.py" --live-controls 2>&1)
echo "$LIVE" | grep -E '^LIVE '
case "$LIVE" in
  *"LIVE CONTROLS PASS"*) ok "M0b and M0o are each driven to BOTH sides against the artifacts FM11 left on disk" ;;
  *) fail "the live controls did not pass:"; echo "$LIVE" ;;
esac
# and the two gates are shown to be TWO, from outside the file that owns them
python3 - <<'PY' || fail "the two-gate separation could not be shown"
import sys
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C")
import d6r2c_fm12_stage as S
assert S.gate_m0b is not S.gate_m0o
src = open(S.__file__).read()
exe = "\n".join(l for l in src.split("def self"+"test():",1)[0].splitlines()
                if not l.lstrip().startswith("#"))
assert "REFUSE_M0O_MESH_IS_BASE" in exe and "REFUSE_M0B_STALE_ARTIFACT" in exe
assert "REFUSE_FRESH"+"_IS_BASE" not in exe, "the fused inherited refusal is raised here"
print("PREFREEZE ok   M0b and M0o are two distinct callables with two distinct "
      "refusal families, and the inherited fused refusal is raised by neither")
PY

echo
echo "=== THE GATES, DRIVEN TO THEIR FAILING SIDE FROM OUTSIDE THE INSTRUMENT ==="
python3 - "$REAL_EVALS" "$REAL_FM10" <<'PY' || fail "an outside-driven control failed"
import sys
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C")
import d6r2c_fm12_states as P
import d6r2c_fm13_grade as G
bad = 0

def ok(m):   print("PREFREEZE ok   " + m)
def no(m):
    global bad
    bad += 1
    print("PREFREEZE FAIL " + m)

# ---- G-WALL, driven from OUTSIDE the producer, with a planted cloud --------
gen = [(float(i), 0.0, 0.0) for i in range(50)]
ids = [4, 9, 17]
if P.wall_displacement(list(gen), gen, ids)["pass"]:
    ok("G-WALL passes an unmoved wall")
else:
    no("G-WALL failed an unmoved wall")
moved = list(gen)
moved[9] = (moved[9][0] + P.PLANT, 0.0, 0.0)
r = P.wall_displacement(moved, gen, ids)
if not r["pass"] and r["at_global_point"] == 9:
    ok("G-WALL DRIVEN TO ITS FAILING SIDE from outside the producer: it sees the "
       "planted %.3e at the point it was planted on" % P.PLANT)
else:
    no("G-WALL did NOT see a planted wall displacement")
tiny = list(gen)
tiny[4] = (tiny[4][0] + P.WALL_MOVE_TOL * 1.001, 0.0, 0.0)
if not P.wall_displacement(tiny, gen, ids)["pass"]:
    ok("G-WALL fails just above its own derived tolerance, so the tolerance is live")
else:
    no("G-WALL is insensitive at its own tolerance")

# ---- EVERY VERIFICATION CONSTANT DERIVED HERE, FROM THE **REAL** ANCHORS ----
inh = G.load_inherited(sys.argv[1])
fm10 = G.load_fm10(sys.argv[2])
J0, Jf = inh["J0"], inh["Jf"]
want_band = G.BAND_FRACTION_OF_J0 * J0
want_Rdef = Jf / J0
want_ratio_band = want_Rdef * ((want_band / Jf) ** 2 + (want_band / J0) ** 2) ** 0.5
want_trim = G.CL_FINDING_TRIGGER / G.G3_MULTIPLE
want_settle = (want_band / J0) / G.SETTLE_MARGIN
want_tol = 4.0 * P.CGNS_UNIQUE_NODES * sys.float_info.epsilon * 1.0
rs = "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_opt_runScript.py"
want_nonorth = G.declared_max_nonorth(rs)

import os, tempfile, shutil
tmp = tempfile.mkdtemp()
try:
    root = os.path.join(tmp, "FM13"); os.makedirs(root)
    on = {p: G.CL_TARGETS[p] for p in G.POINTS}
    G._synth_arm(root, J0, Jf, cl_base=on, cl_opt=on,
                 cl_ez={p: G.CL_TARGETS[p] + 0.004 for p in G.POINTS},
                 J_do=fm10["J"], cl_do=dict(fm10["CL"]))
    lg = G._synth_log(tmp, name="a.log")
    g = G.grade_fm12(arm_dir=root, datum_epoch=0, inherited=inh, fm10=fm10,
                     core_min=1.0, rc=0, runscript_path=rs, log_path=lg)
    d = g["derived_constants"]
    for name, want, got in (("FM_BAND_ABS", want_band, d["FM_BAND_ABS"]),
                            ("R_def", want_Rdef, d["R_def"]),
                            ("RATIO_BAND", want_ratio_band, d["RATIO_BAND"]),
                            ("TRIM_TOL", want_trim, d["TRIM_TOL"]),
                            ("CD_SETTLE_REL", want_settle, d["CD_SETTLE_REL"]),
                            ("MAX_NONORTH", want_nonorth, d["MAX_NONORTH_DECLARED"])):
        if abs(want - got) <= 1e-15 * max(1.0, abs(want)):
            ok("%s is DERIVED in the grading invocation FROM THE REAL ANCHORS, "
               "and the derived value is the one used: %.12g" % (name, got))
        else:
            no("%s: the instrument serves %r, its stated basis gives %r"
               % (name, got, want))
    if abs(P.WALL_MOVE_TOL - want_tol) <= 0.0:
        ok("WALL_MOVE_TOL is DERIVED in the producer's invocation and used: %.6e"
           % P.WALL_MOVE_TOL)
    else:
        no("WALL_MOVE_TOL is not its own derivation")
    # ---- R1, DRIVEN AT ZERO AND AT A PLANTED NON-ZERO ----------------------
    if g["R1"] and g["R1_verdict"] == "PASS":
        ok("R1 PASSES at exactly zero, and carries its OWN verdict line")
    else:
        no("R1 did not pass on a zero-difference arm")
    if g["label"] == "PASS":
        ok("...and R1's verdict does NOT flip the arm's label, exactly as registered")
    else:
        no("R1 flipped the arm's label")
    # ---- NO SANITY ANCHOR AT A STATE WHERE THE QUANTITY IS IDENTICALLY ZERO --
    E = fm10["E_star"]
    if min(abs(v) for v in E.values()) > 1e-3:
        ok("D1's anchor E_star is FM10's MEASURED excess, min |E_star| = %.6f -- "
           "not a state where the quantity under test is identically zero"
           % min(abs(v) for v in E.values()))
    else:
        no("D1's anchor sits at a near-zero excess")
    if abs(fm10["J"]) > 0.0 and abs(want_Rdef - 1.0) > 0.1:
        ok("D2's anchor is FM10's MEASURED J = %.12g and G1's is R_def = %.9f, "
           "both non-degenerate, both READ FROM THE REAL RECORDS"
           % (fm10["J"], want_Rdef))
    else:
        no("a headline anchor is degenerate")
    # ---- THE PLANTED CONTROL, run from outside the grader -------------------
    kw = dict(arm_dir=root, datum_epoch=0, inherited=inh, fm10=fm10,
              core_min=1.0, rc=0, runscript_path=rs, log_path=lg)
    pc = G.live_plant_check(kw, g["label"])
    if pc["all_seen"]:
        ok("the planted %.3e is SEEN in all %d channels it is planted into, "
           "including M0b and R1" % (G.PLANT, len(pc["plants"])))
    else:
        no("a planted perturbation was not seen")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
sys.exit(1 if bad else 0)
PY

echo
echo "=== THE COST, RE-DERIVED FROM ITS OWN ANCHORS IN THIS INVOCATION ========="
python3 - <<'PY' || fail "the cost figures are not their own derivation"
import json, statistics, sys
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C")
import d6r2c_fm13_grade as G
d7 = ("/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER8R3-a2-wing-gentler-"
      "layers/DEC7/d6r2c_dec5.jsonl")
st = {}
for l in open(d7):
    r = json.loads(l)
    if r.get("kind") == "STATE":
        st[r["state"]] = r["wall_s"]
E = ("/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-"
     "transonic-restartable/O_mp/d6r2c_evals.jsonl")
gr = [json.loads(l)["eval_wall_s"] for l in open(E)
      if json.loads(l).get("kind") == "G"]
bad = 0
def say(n, m):
    print("PREFREEZE ok   %s: %s" % (n, m))
def no(n, m):
    global bad
    bad += 1
    print("PREFREEZE FAIL %s: %s" % (n, m))

# THE REGISTERED ANCHORS ARE STATED ROUNDINGS OF THE RAW RECORD VALUES, and
# this check asserts THE ROUNDING, printing the raw figure beside it.  Two of
# them are rounded UP on purpose -- the conservative direction for a prediction
# -- and that is asserted as a DIRECTION, not waved through as "close enough".
def rounded(n, reg, raw, dp):
    if round(raw, dp) == reg:
        say(n, "registered %s = raw %.9g rounded to %d dp" % (reg, raw, dp))
    else:
        no(n, "registered %r, raw %r rounds to %r" % (reg, raw, round(raw, dp)))

def rounded_up(n, reg, raw, limit):
    if reg >= raw and (reg - raw) < limit:
        say(n, "registered %s >= raw %.9g, rounded UP by %.4f s -- the "
               "conservative direction for a prediction" % (reg, raw, reg - raw))
    else:
        no(n, "registered %r is not a conservative rounding of raw %r" % (reg, raw))

def exact(n, a, b):
    if a == b:
        say(n, "%s, derived here from its own anchor" % (a,))
    else:
        no(n, "instrument %r, anchor %r" % (a, b))

rounded("OBJ_EVAL_WALL_S (DEC7 STATE O)", G.OBJ_EVAL_WALL_S, st["O"], 1)
# ---- ZB_TRIM_WALL_S IS RE-ANCHORED, AND THE RE-ANCHOR IS DERIVED HERE -------
# FM12's own Zb FOOTER is the new anchor.  The OLD anchor (DEC7 STATE B) is
# still read, and is asserted to be KNOWN TOO LARGE for this state -- named,
# never quietly dropped.
import json as _json
_ZBF = ("/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM12-a2-wing-matched-lift-provenance"
        "/FM12/Zb/d6r2c_fm12.jsonl")
_foot = None; _st = None
for _l in open(_ZBF):
    _l = _l.strip()
    if not _l: continue
    _r = _json.loads(_l)
    if _r.get("kind") == "FOOTER" and _r.get("sub_arm") == "Zb": _foot = _r
    if _r.get("kind") == "STATE" and _r.get("state") == "Zb": _st = _r
if _foot is None:
    print("PREFREEZE FAIL the Zb re-anchor's own record is not on disk"); bad = True
else:
    _zb_wall = _foot["wall_s"]
    _derived = round(_zb_wall - G.MESH_OVERHEAD_WALL_S - G.MODEL_LOAD_WALL_S, 3)
    if abs(G.ZB_TRIM_WALL_S - _derived) <= 5e-4:
        print("PREFREEZE ok   ZB_TRIM_WALL_S RE-ANCHORED ON MEASUREMENT: registered %.3f = "
              "FM12's own Zb FOOTER wall %.3f s minus MESH_OVERHEAD %.1f and MODEL_LOAD %.1f"
              % (G.ZB_TRIM_WALL_S, _zb_wall, G.MESH_OVERHEAD_WALL_S, G.MODEL_LOAD_WALL_S))
    else:
        print("PREFREEZE FAIL ZB_TRIM_WALL_S registered %.3f, derived %.3f from FM12's Zb FOOTER"
              % (G.ZB_TRIM_WALL_S, _derived)); bad = True
    _old = round(st["B"], 1)
    _zb_registered_total = 676.8
    if _old > G.ZB_TRIM_WALL_S:
        print("PREFREEZE ok   THE OLD ANCHOR IS NAMED, NOT DROPPED: DEC7 STATE B is %.1f s, "
              "%.2fx the re-anchored %.3f s, and is KNOWN TOO LARGE for this state"
              % (_old, _old / G.ZB_TRIM_WALL_S, G.ZB_TRIM_WALL_S))
    else:
        print("PREFREEZE FAIL the old DEC7 anchor is not larger than the re-anchored value"); bad = True
    if _st is not None and _st.get("n_trim_evals") is not None:
        print("PREFREeZE".replace("PREFREeZE","PREFREEZE") +
              " ok   THE CAUSE IS MEASURED, NOT GUESSED: FM12's Zb trim closed in %d evaluations, "
              "and the %.2fx speedup over the %.1f s registered for the whole sub-arm follows from that"
              % (_st["n_trim_evals"], _zb_registered_total / _zb_wall, _zb_registered_total))
    else:
        print("PREFREEZE FAIL the Zb STATE record carries no n_trim_evals"); bad = True
rounded("ZO_TRIM_WALL_S (DEC7 STATE S)", G.ZO_TRIM_WALL_S, st["S"], 1)
rounded("GRAD_EVAL_WALL_S (O_mp median of %d G records)" % len(gr),
        G.GRAD_EVAL_WALL_S, statistics.median(gr), 3)
rounded_up("MESH_OVERHEAD_WALL_S (FM10 arm wall 160 - solve 71.847)",
           G.MESH_OVERHEAD_WALL_S, 160.0 - 71.847, 0.1)
rounded_up("MODEL_LOAD_WALL_S (DEC7 FOOTER 5918.862 - sum of its states)",
           G.MODEL_LOAD_WALL_S, 5918.862008810043 - sum(st.values()), 0.1)
exact("core-min per objective evaluation", round(G.CORE_MIN_PER_OBJ_EVAL, 3), 5.447)
exact("core-min per gradient evaluation", round(G.CORE_MIN_PER_GRAD_EVAL, 3), 11.863)
exact("gradient evaluations IN THIS ARM (registered so the zero is VISIBLE)",
      G.N_GRAD_EVALS_THIS_ARM, 0)
exact("prediction core-min", G.PREDICTION_CORE_MIN, 188.628)
exact("cap core-min (3.00x)", G.CAP_CORE_MIN, 565.884)
# and the reduction is ENTIRELY the re-anchored Zb term, asserted rather than asserted-in-prose
_fm12_pred = 222.853
_delta = round((676.8 - _foot["wall_s"]) * G.RANKS / 60.0, 3) if _foot else None
if _delta is not None and abs((_fm12_pred - G.PREDICTION_CORE_MIN) - _delta) <= 0.01:
    print("PREFREEZE ok   the whole %.3f core-min reduction from FM12's %.3f is the re-anchored Zb term "
          "and nothing else" % (_fm12_pred - G.PREDICTION_CORE_MIN, _fm12_pred))
else:
    print("PREFREEZE FAIL the prediction moved by something other than the Zb re-anchor"); bad = True
print("PREFREEZE ok   dollars DERIVED at $%.4f/core-h, NOT MEASURED (the box "
      "cannot read its own billing): prediction $%.4f, cap $%.4f"
      % (G.RATE_USD_PER_CORE_H,
         G.PREDICTION_CORE_MIN / 60.0 * G.RATE_USD_PER_CORE_H,
         G.CAP_CORE_MIN / 60.0 * G.RATE_USD_PER_CORE_H))
# FM12's CALIBRATION ROW, against FM12's OWN registered prediction, read from
# FM12's ledger rather than retyped.
FM12_PRED, FM12_CAP, FM12_ACTUAL = 222.853, 668.559, 17.933
_led = ("/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM12-a2-wing-matched-lift-provenance"
        "/ledger.txt")
_cm = None
try:
    for _l in open(_led):
        if "D6R2C_FM12_ROW" in _l:
            for _t in _l.split():
                if _t.startswith("core_min="): _cm = float(_t.split("=", 1)[1])
except OSError:
    pass
if _cm is None or abs(_cm - FM12_ACTUAL) > 5e-4:
    print("PREFREEZE FAIL FM12's actual is not %.3f in its own ledger (read %r)" % (FM12_ACTUAL, _cm))
    bad = True
else:
    print("PREFREEZE ok   FM12 CALIBRATION, actual READ FROM ITS OWN LEDGER: predicted %.3f core-min, "
          "cap %.3f, actual %.3f, ratio %.6f, CAP NOT CROSSED -- ATTRIBUTED TO THE Zo REFUSAL, NOT TO "
          "MISPREDICTION (Zo carried 2400.3 s of the 3342.8 s prediction and never reached a solve). "
          "NAMED SEPARATELY and NOT folded into that ratio: Zb's 4.14x speedup, which is genuine "
          "calibration information and is what ZB_TRIM_WALL_S is re-anchored on."
          % (FM12_PRED, FM12_CAP, FM12_ACTUAL, FM12_ACTUAL / FM12_PRED))
sys.exit(1 if bad else 0)
PY

echo
echo "=== THE WRITE GUARD, DRIVEN IN THE PINNED IMAGE AGAINST REAL ARTIFACTS ==="
# ---------------------------------------------------------------------------
# C1 -- THE KNOWN-BAD CONTROL, AND IT IS **NOT SYNTHETIC**: the 8192-byte CGNS
#       arm FM12 actually produced when four ranks raced one path.  A guard that
#       has never said no is not a guard.
# C3 -- the POSITIVE control, so the guard is not merely refusing everything.
# C2 -- the PLANTED content control (CLAUDE.md rule 3), driven to its failing
#       side AND to its passing side.
# The three run INSIDE THE PINNED IMAGE because cgnsutilities lives there.
# ---------------------------------------------------------------------------
if [ ! -f "$CORRUPT" ]; then
  fail "C1 the preserved 8192-byte FM12 artifact is NOT ON DISK -- it is the evidence and the known-bad control"
elif ! sudo -n docker image inspect "$IMG" >/dev/null 2>&1; then
  fail "C1/C2/C3 the pinned image $IMG is not available; the controls CANNOT be driven and no green may be claimed"
else
  SZ=$(stat -c%s "$CORRUPT")
  [ "$SZ" = "8192" ] && ok "C1 the preserved corrupt artifact is on disk at its recorded 8192 bytes" \
                     || fail "C1 the preserved artifact is $SZ bytes, not the recorded 8192"
  CD=$(dirname "$CORRUPT")
  OUT=$(sudo -n docker run --rm --cpuset-cpus=90 -e HOME=/tmp \
        -v "$SRC":/src:ro -v "$CD":/zo:ro "$IMG" bash -lc '
          . /home/dafoamuser/dafoam/loadDAFoam.sh
          cp /src/d6r2c_fm13_deform.py /src/d6r2c_freshmesh.py /tmp/ && cd /tmp
          python d6r2c_fm13_deform.py --check-known-bad /zo/surfaceMesh_final.cgns; echo "C1_RC=$?"
          python d6r2c_fm13_deform.py --check-good     /zo/surfaceMesh_base.cgns;  echo "C3_RC=$?"
          cp /zo/surfaceMesh_base.cgns /tmp/clean.cgns
          python d6r2c_fm13_deform.py --plant-control  /tmp/clean.cgns;            echo "C2_RC=$?"
        ' 2>&1)
  case "$OUT" in *"REFUSE_CGNS_SHORT_WRITE"*) ok "C1 the guard REFUSED the real 8192-byte corrupt CGNS (REFUSE_CGNS_SHORT_WRITE)" ;;
                 *) fail "C1 the guard did NOT refuse the real corrupt artifact"; printf '%s\n' "$OUT" | tail -20 ;; esac
  case "$OUT" in *"C1_RC=0"*) : ;; *) fail "C1 control returned non-zero" ;; esac
  case "$OUT" in *"GUARD ACCEPTED blocks=9 points=1215"*) ok "C3 the guard ACCEPTED a correct 114688-byte CGNS -- it is not refusing everything" ;;
                 *) fail "C3 the guard refused a correct CGNS" ;; esac
  case "$OUT" in *"the reader SEES the plant"*) ok "C2 the content reader SEES a 1.234e-03 m plant -- rule 3, the zero is not from a blind reader" ;;
                 *) fail "C2 the content reader could NOT see the plant" ;; esac
  case "$OUT" in *"REFUSE_CGNS_CONTENT"*) ok "C2 limb 4 REFUSED a full-size, readable file whose coordinates are not the ones computed" ;;
                 *) fail "C2 limb 4 did not refuse planted content" ;; esac
  case "$OUT" in *"limb 4 refuses a MISMATCH, not merely any file"*) ok "C2 limb 4 ACCEPTS the same file against its own md5 -- it refuses a mismatch, not every file" ;;
                 *) fail "C2 limb 4 refuses even a matching expectation" ;; esac
fi

# ---------------------------------------------------------------------------
# C4 -- THE UNGUARDED PATH.  Registered result: 12 of 12 trials failed, sizes
#       12288..114688, and FIVE produced the FULL CORRECT 114688 bytes.
#       *** THE CAVEAT IS PART OF THE CHECK, NOT A FOOTNOTE. ***
# ---------------------------------------------------------------------------
echo "=== C4 THE UNGUARDED PATH -- WHAT WAS MEASURED, AND WHAT WAS NOT ========="
echo "PREFREEZE note C4 MEASURED 2026-09-13: 12 of 12 trials at 4 ranks failed; sizes 12288..114688 bytes;"
echo "PREFREEZE note FIVE OF TWELVE produced the FULL CORRECT 114688 bytes, and one such output READ CLEANLY"
echo "PREFREEZE note with 9 blocks / 1215 points and coordinates IDENTICAL to the input to 0.0 exactly."
echo "PREFREEZE note SO A SIZE-AND-READABILITY ASSERTION WOULD HAVE PASSED 5 OF 12 RACED WRITES."
echo "PREFREEZE note The assertion is registered as the TRUNCATION net.  The RANK-0 GUARD is the fix."
echo "PREFREEZE note C4 barrier-synchronises the ranks, which MAXIMISES collision; it does NOT measure the"
echo "PREFREEZE note real run's rate.  THE INTERMITTENCY IS INFERRED FROM ONE SUCCESS (FM10) AND ONE"
echo "PREFREEZE note FAILURE (FM12), NOT MEASURED OVER REPEATS.  No rate or probability may be quoted."
grep -q "NOT MEASURED OVER REPEATS" "$REG" \
  && ok "C4b the intermittency caveat is IN THE FROZEN TEXT, not only in this script" \
  || fail "C4b the frozen registration does not carry the intermittency caveat"
grep -q "FIVE OF TWELVE RACED WRITES PRODUCED THE FULL, CORRECT 114,688 BYTES" "$REG" \
  && ok "C4a the measured limit of this arm's own instrument is IN THE FROZEN TEXT" \
  || fail "C4a the frozen registration does not carry the C4a finding"

echo "=== THE INSTRUMENTS' OWN SELFTESTS, for completeness ====================="
for s in "python3 $SRC/d6r2c_fm12_stage.py --selftest" \
         "python3 $SRC/d6r2c_fm12_states.py --selftest" \
         "python3 $SRC/d6r2c_fm13_grade.py --selftest" \
         "python3 $SRC/d6r2c_fm13_deform.py --selftest" \
         "bash $LAUNCHER --selftest"; do
  O=$($s 2>&1 | tail -1)
  case "$O" in *PASS*) ok "$O" ;; *) fail "$O" ;; esac
done

echo
[ $rc -eq 0 ] && echo "D6R2C_FM13_PREFREEZE PASS" || echo "D6R2C_FM13_PREFREEZE FAIL"
exit $rc
