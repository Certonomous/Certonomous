#!/usr/bin/env bash
# ===========================================================================
# d6r2c_fm11_prefreeze.sh -- THE THREE CLAUSES OF DAFOAM_CHARTER.md sec 22.4,
#                            DRIVEN, BEFORE THE FREEZE SHA.
# ===========================================================================
#
# The charter's clauses, and what each one is answered by here:
#
#   (a) EVERY INSTRUMENT NAMED IN THE FROZEN TABLE EXISTS AT ITS STATED md5.
#       This script READS THE REGISTRATION'S OWN TABLE -- it does not carry its
#       own list -- hashes every file the table names, and fails on a row whose
#       file is absent, whose md5 is missing, or whose md5 disagrees.  "A table
#       that is TRUE AS WRITTEN about files that do not exist is how the defect
#       survived" (L-579).
#
#   (b) THE CHECK DRIVES THE CLI THE LAUNCHER EMITS, NOT THE GRADED FUNCTION.
#       It asks the launcher for the EXACT grading command (--emit-grade-cmd)
#       and RUNS IT against a synthetic arm built here, and it lifts the
#       producer's argument vectors out of the EXACT container block
#       (--emit-cmd) and runs them through the producer's own argparse.  A
#       --selftest green against the graded function proves the function; the
#       FM9 grader's frozen command line could only ever return NOT A RESULT
#       and its selftest never saw it (L-595, L-570).
#
#   (c) EVERY CHANNEL A GATE READS HAS A WRITER THAT RAN.  It sweeps the FM11
#       instruments for readers of primal_residual.json -- the channel with
#       four readers, zero writers and zero files on disk whose default
#       conv[p] = True stood for every condition -- and requires ZERO.  Then it
#       shows, for each channel FM11's gates DO read, the writer that produces
#       it, and drives the grader's log limb against a log with no writer to
#       confirm it REFUSES rather than reading as zero failures.
#
# AND THREE THINGS THIS LAB REQUIRES OF EVERY GATE, DRIVEN FROM OUTSIDE THE
# INSTRUMENT THAT OWNS THEM:
#   * G-WALL is driven to its FAILING side with a planted point cloud;
#   * every verification constant is DERIVED in the same invocation and the
#     DERIVED value is the one used -- asserted by recomputing each from its
#     stated basis and comparing against what the instrument serves;
#   * no sanity anchor sits at a state where the quantity under test is
#     identically zero -- asserted on the D1 anchor, which is FM10's MEASURED
#     non-zero excess.
#
# IT FREEZES NOTHING AND LAUNCHES NOTHING.  It prints PASS or FAIL and exits.
# SUBMISSIONS PARKED (rule 7).
# ===========================================================================
set -uo pipefail

SRC=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C
REG="$SRC/PREREGISTRATION_FM11_MATCHED_LIFT.md"
LAUNCHER="$SRC/d6r2c_fm11_run_arm.sh"
rc=0
ok()   { echo "PREFREEZE ok   $*"; }
fail() { echo "PREFREEZE FAIL $*"; rc=1; }

echo "=== (a) EVERY INSTRUMENT IN THE FROZEN TABLE EXISTS AT ITS STATED md5 ==="
# The table is the registration's own section 6.  Rows are read out of it; this
# script carries NO list of its own, so a row added to the document is a row
# this check hashes, and a row this check cannot parse is a FAILURE, not a skip.
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
# the control, driven to its failing side: a row naming a file that is not there
PROBE="| \`d6r2c_fm11_does_not_exist.py\` | NOT BUILT | 00000000000000000000000000000000 |"
PF=$(printf '%s' "$PROBE" | sed -n 's/^| *`\([^`]*\)`.*/\1/p')
[ ! -f "$SRC/$PF" ] && ok "the row parser resolves a file name out of a table row, and would report this synthetic row as MISSING" \
  || fail "the synthetic probe row unexpectedly exists"

echo
echo "=== (b) THE CHECK DRIVES THE CLI THE LAUNCHER EMITS ======================"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
# ---- build a synthetic arm THE GRADER CAN ACTUALLY GRADE, from the grader's
# ---- own fixture builder, so the tree shape is the one the grader expects.
python3 - "$TMP" <<'PY' || fail "could not build the synthetic arm"
import os, sys, json
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C")
import d6r2c_fm11_grade as G
tmp = sys.argv[1]
root = os.path.join(tmp, "FM11"); os.makedirs(root)
on = {p: G.CL_TARGETS[p] for p in G.POINTS}
E  = {"cl04": 0.149286, "cl05": 0.151566, "cl06": 0.152398}
Jb = 0.0306416314389976151
Jo = Jb * (0.0230632595286777639 / Jb)
G._synth_arm(root, Jb, Jo, cl_base=on, cl_opt=on,
             cl_ez={p: G.CL_TARGETS[p] + 0.004 for p in G.POINTS},
             J_do=0.036964341844,
             cl_do={p: G.CL_TARGETS[p] + E[p] for p in G.POINTS})
G._synth_log(tmp, n_blocks=8, settled=True, name="FM11.log")
open(os.path.join(root, ".d6r2c_age_datum"), "w").write("0\n")
PY
# ---- ASK THE LAUNCHER FOR THE COMMAND.  Not a re-typed copy of it.
GRADE_CMD=$(bash "$LAUNCHER" --emit-grade-cmd FM11 "$TMP/FM11" 10.000 0 \
            "$TMP/FM11.log" "$TMP/FM11_GRADE.json")
echo "PREFREEZE the launcher emits: $GRADE_CMD"
# the synthetic tree has no real evals/FM10 record, so the two external anchors
# are switched to their SYNTHETIC form -- and NOTHING ELSE about the command is
# altered.  Every flag, and the order of every flag, is the launcher's.
RUN_CMD="$GRADE_CMD --evals SYNTHETIC --fm10-record SYNTHETIC"
OUT=$(eval "$RUN_CMD" 2>&1); GRC=$?
if [ $GRC -eq 0 ]; then ok "THE LAUNCHER'S OWN GRADING COMMAND RUNS AND RETURNS 0"
else fail "the launcher's own grading command exited $GRC:"; echo "$OUT"; fi
case "$OUT" in
  *"label=PASS"*) ok "... and it returns a real verdict, not NOT A RESULT by construction" ;;
  *) fail "the emitted command did not produce a PASS on a tree built to pass:"; echo "$OUT" ;;
esac
[ -f "$TMP/FM11_GRADE.json" ] && ok "... and it WROTE the verdict file the launcher names" \
  || fail "the emitted command wrote no verdict file"
# THE NEGATIVE, which is what makes the above non-vacuous: the same command with
# the arm directory removed must FAIL, not pass quietly.
rm -rf "$TMP/FM11/Zo"
eval "$RUN_CMD" >/dev/null 2>&1 && fail "the emitted command PASSED with half the arm deleted" \
  || ok "... and the same command REFUSES when a sub-arm is missing"

# ---- the producer's own argument vector, lifted from the emitted block -------
for SA in Zb Zo; do
  ARGS=$(bash "$LAUNCHER" --emit-cmd FM11 | tr '\n' ' ' | tr -d '\\' \
         | grep -oE "python d6r2c_fm11_states\.py [^|]*--sub-arm $SA [^|]*--x0 [^ ]+" | head -1)
  ARGS=${ARGS#python d6r2c_fm11_states.py }
  ARGS=$(printf '%s' "$ARGS" | sed "s|\"\$PWD\"|$TMP/FM11|")
  O=$(cd "$SRC" && python3 d6r2c_fm11_states.py --parse-only $ARGS 2>&1)
  case "$O" in
    *"PARSE_ONLY sub_arm=$SA"*) ok "the producer accepts the EXACT vector the container hands it for $SA" ;;
    *) fail "the producer rejected its own emitted vector for $SA:"; echo "$O" ;;
  esac
done
bash "$LAUNCHER" --emit-cmd FM11 | grep -q -- "--phase solve" \
  && fail "d6r2c_freshmesh.py --phase solve -- THE DOUBLE APPLICATION -- is still in the emitted block" \
  || ok "the emitted block never calls the producer whose double application made FM10 NOT A RESULT"

echo
echo "=== (c) EVERY CHANNEL A GATE READS HAS A WRITER THAT RAN =================="
FM11_FILES="d6r2c_fm11_states.py d6r2c_fm11_grade.py d6r2c_fm11_run_arm.sh"
# THE SWEEP LOOKS FOR THE SHAPE OF A READ, NOT FOR THE WORD.  A line that
# MENTIONS the channel while explaining why it was deleted is not a reader, and
# a sweep that cannot tell an explanation from a call site is reading an
# adjacent quantity (L-595) -- the very error this checklist exists to catch.
# A READ is `primal_residual` on a line that also opens, joins or stats a path.
read_sites() { grep -nE 'primal_residual.*(open\(|json\.load|os\.path\.join|isfile|exists)|(open\(|json\.load|os\.path\.join|isfile|exists).*primal_residual' "$1"; }
HITS=0
for f in $FM11_FILES; do
  H=$(read_sites "$SRC/$f" | wc -l); HITS=$((HITS + H))
done
[ "$HITS" -eq 0 ] && ok "ZERO live READ SITES for primal_residual.json in the FM11 instruments -- the channel is DELETED, not read more carefully" \
  || { fail "the FM11 instruments still carry $HITS read site(s) for primal_residual.json"; \
       for f in $FM11_FILES; do read_sites "$SRC/$f" | head -5; done; }
# THE CONTROL, DRIVEN TO ITS FAILING SIDE: the channel IS still read by the
# inherited producer, so the sweep is shown to be able to find a real one.
INH=$(read_sites "$SRC/d6r2c_freshmesh.py" | wc -l)
[ "$INH" -gt 0 ] && ok "the same sweep FINDS $INH real read site(s) in the inherited d6r2c_freshmesh.py -- it is not simply blind" \
  || fail "the sweep found no read site even in the file known to carry the channel"
# ... and it does NOT count a mere mention: the FM11 files mention it and are clean.
MENTIONS=0
for f in $FM11_FILES; do M=$(grep -c "primal_residual" "$SRC/$f"); MENTIONS=$((MENTIONS + M)); done
[ "$MENTIONS" -gt 0 ] && ok "the FM11 instruments MENTION the channel $MENTIONS times (explaining the deletion) and READ it $HITS times -- the sweep separates the two" \
  || fail "the FM11 instruments do not even document the deletion"
# the channel FM11's H4 limb DOES read, and the writer that produces it
FM10LOG=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM9-a2-wing-freshmesh-arrives/FM10_20260913T163543Z_1546115.log
if [ -f "$FM10LOG" ]; then
  NCD=$(grep -c "^CD: " "$FM10LOG")
  [ "$NCD" -gt 0 ] && ok "H4's channel has a WRITER THAT RAN: $NCD 'CD:' lines written by the solver itself in FM10's own arm log" \
    || fail "the arm log carries no CD series -- H4's channel has no writer either"
  python3 - "$FM10LOG" <<'PY' || fail "the log limb could not read a real arm log"
import sys
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C")
import d6r2c_fm11_grade as G
r = G.grade_log(sys.argv[1], 1.0e-5)
print("PREFREEZE ok   the log limb reads a REAL arm log: %d primal blocks, "
      "worst last-step relative CD change %.3e, all_settled=%s"
      % (r["n_primal_blocks"], r["worst_rel_change_last_step"], r["all_settled"]))
PY
else
  fail "FM10's arm log is not on disk -- the writer claim cannot be shown"
fi
# the limb REFUSES on an absent writer, rather than reading as zero failures
python3 - <<'PY' || fail "the log limb did not refuse an absent writer"
import sys
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C")
import d6r2c_fm11_grade as G
try:
    G.grade_log("/tmp/there-is-no-such-log-anywhere.log", 1.0e-5)
    print("PREFREEZE FAIL the log limb accepted an absent log"); sys.exit(1)
except G.Refusal as e:
    assert str(e).startswith("REFUSE_NO_ARM_LOG"), e
print("PREFREEZE ok   the log limb REFUSES an absent writer -- an absent source "
      "is NOT zero failures (rule 3)")
PY

echo
echo "=== THE GATES, DRIVEN TO THEIR FAILING SIDE FROM OUTSIDE THE INSTRUMENT ==="
python3 - <<'PY' || fail "an outside-driven control failed"
import sys
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C")
import d6r2c_fm11_states as P
import d6r2c_fm11_grade as G
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
# the smallest displacement it must still catch
tiny = list(gen)
tiny[4] = (tiny[4][0] + P.WALL_MOVE_TOL * 1.001, 0.0, 0.0)
if not P.wall_displacement(tiny, gen, ids)["pass"]:
    ok("G-WALL fails just above its own derived tolerance, so the tolerance is live")
else:
    no("G-WALL is insensitive at its own tolerance")

# ---- EVERY VERIFICATION CONSTANT DERIVED HERE, AND THE DERIVED VALUE USED ---
J0, Jf = 0.0306416314389976151, 0.0230632595286777639
want_band = G.BAND_FRACTION_OF_J0 * J0
want_Rdef = Jf / J0
want_ratio_band = want_Rdef * ((want_band / Jf) ** 2 + (want_band / J0) ** 2) ** 0.5
want_trim = G.CL_FINDING_TRIGGER / G.G3_MULTIPLE
want_settle = (want_band / J0) / G.SETTLE_MARGIN
want_tol = 4.0 * P.CGNS_UNIQUE_NODES * sys.float_info.epsilon * 1.0
rs = "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_opt_runScript.py"
want_nonorth = G.declared_max_nonorth(rs)

inh = {"J0": J0, "Jf": Jf, "J0_basis": "x", "Jf_basis": "x",
       "evals_md5": "x", "n_J0": 2, "n_Jf": 88}
E = {"cl04": 0.149286, "cl05": 0.151566, "cl06": 0.152398}
fm10 = {"E_star": E, "CL": {p: G.CL_TARGETS[p] + E[p] for p in G.POINTS},
        "J": 0.036964341844, "record": "x", "role": "x"}
import os, tempfile, shutil
tmp = tempfile.mkdtemp()
try:
    root = os.path.join(tmp, "FM11"); os.makedirs(root)
    on = {p: G.CL_TARGETS[p] for p in G.POINTS}
    G._synth_arm(root, J0, Jf, cl_base=on, cl_opt=on,
                 cl_ez={p: G.CL_TARGETS[p] + 0.004 for p in G.POINTS},
                 J_do=0.036964341844, cl_do=dict(fm10["CL"]))
    lg = G._synth_log(tmp, name="a.log")
    g = G.grade_fm11(arm_dir=root, datum_epoch=0, inherited=inh, fm10=fm10,
                     core_min=1.0, rc=0, runscript_path=rs, log_path=lg)
    d = g["derived_constants"]
    for name, want, got in (("FM_BAND_ABS", want_band, d["FM_BAND_ABS"]),
                            ("R_def", want_Rdef, d["R_def"]),
                            ("RATIO_BAND", want_ratio_band, d["RATIO_BAND"]),
                            ("TRIM_TOL", want_trim, d["TRIM_TOL"]),
                            ("CD_SETTLE_REL", want_settle, d["CD_SETTLE_REL"]),
                            ("MAX_NONORTH", want_nonorth, d["MAX_NONORTH_DECLARED"])):
        if abs(want - got) <= 1e-15 * max(1.0, abs(want)):
            ok("%s is DERIVED in the grading invocation and the derived value is "
               "the one used: %.12g" % (name, got))
        else:
            no("%s: the instrument serves %r, its stated basis gives %r"
               % (name, got, want))
    if abs(P.WALL_MOVE_TOL - want_tol) <= 0.0:
        ok("WALL_MOVE_TOL is DERIVED in the producer's invocation and used: %.6e"
           % P.WALL_MOVE_TOL)
    else:
        no("WALL_MOVE_TOL is not its own derivation")
    # ---- NO SANITY ANCHOR AT A STATE WHERE THE QUANTITY IS IDENTICALLY ZERO --
    if min(abs(v) for v in E.values()) > 1e-3:
        ok("D1's anchor E_star is FM10's MEASURED excess, min |E_star| = %.6f -- "
           "not a state where the quantity under test is identically zero"
           % min(abs(v) for v in E.values()))
    else:
        no("D1's anchor sits at a near-zero excess")
    if abs(fm10["J"]) > 0.0 and abs(want_Rdef - 1.0) > 0.1:
        ok("D2's anchor is FM10's MEASURED J = %.12g and G1's is R_def = %.9f, "
           "both non-degenerate" % (fm10["J"], want_Rdef))
    else:
        no("a headline anchor is degenerate")
    # ---- THE PLANTED CONTROL, run from outside the grader -------------------
    kw = dict(arm_dir=root, datum_epoch=0, inherited=inh, fm10=fm10,
              core_min=1.0, rc=0, runscript_path=rs, log_path=lg)
    pc = G.live_plant_check(kw, g["label"])
    if pc["all_seen"]:
        ok("the planted %.3e is SEEN in all %d channels it is planted into"
           % (G.PLANT, len(pc["plants"])))
    else:
        no("a planted perturbation was not seen")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
sys.exit(1 if bad else 0)
PY

echo
echo "=== THE INSTRUMENTS' OWN SELFTESTS, for completeness ====================="
for s in "python3 $SRC/d6r2c_fm11_states.py --selftest" \
         "python3 $SRC/d6r2c_fm11_grade.py --selftest" \
         "bash $LAUNCHER --selftest"; do
  O=$($s 2>&1 | tail -1)
  case "$O" in *PASS*) ok "$O" ;; *) fail "$O" ;; esac
done

echo
[ $rc -eq 0 ] && echo "D6R2C_FM11_PREFREEZE PASS" || echo "D6R2C_FM11_PREFREEZE FAIL"
exit $rc
