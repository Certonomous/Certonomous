#!/usr/bin/env bash
# =============================================================================
# F28 -- DRIVEN CONTROL ON THE `run_f28.sh` GUARD-VIRGIN WIRING.
#
# WHAT THIS EXISTS TO PROVE.  On 2026-08-31 this team certified, twice at
# supervisor level, a guard that was PERMANENTLY BLIND: a regex matched a banner
# comment, the refusal branch was unreachable, and nobody noticed until somebody
# RAN it (commit 9c223449).  So the wiring of section 11.1's virgin-case guard
# into the launcher is not offered as a diff to be read.  It is DRIVEN: the
# refusal is made to FIRE on directories built dirty on purpose, the pass is
# made to fire on a virgin one, and the load-bearing POSITION of the call is
# tested by executing the launcher's own assemble fragment against a mutated
# twin in which the call sits one statement later.
#
# WHAT IT DRIVES.  Not a re-typed copy.  It extracts, from
# `run_f28_candidate.sh` itself:
#   * the whole `guard_virgin_section_11_1` function, verbatim;
#   * the assemble fragment from `PHASE="assemble"` through the `mkdir -p
#     "$RUN_DIR/system" ...` statement, verbatim;
# and executes both.  The extracted text is printed with its md5 so the reader
# can hash the source and see it is the same text.
#
# WHERE IT WRITES.  One scratch tree, named at the top, plus `mktemp -d` probe
# directories created and removed by the function under test.  IT WRITES
# NOTHING UNDER `verification/runs/` AND LIMB 20 MEASURES THAT.
#
# NO SOLVER IS LAUNCHED.  NO GIT OPERATION IS PERFORMED.
# =============================================================================
set -o pipefail

REPO="/home/ubuntu/Certonomous"
CASE_DIR="$REPO/cases/F28_DUCTED_ACTUATOR_DISK"
LAUNCHER="$CASE_DIR/run_f28_candidate.sh"
GOOD_COMPARATOR="$CASE_DIR/analyse_f28_candidate.py"
INSTALLED_COMPARATOR="$CASE_DIR/analyse_f28.py"
RUNS_DIR="$REPO/verification/runs/F28_runs"

SCRATCH="/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad/f28_guardwire"

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); printf 'PASS  %s\n' "$*"; }
bad()  { FAIL=$((FAIL+1)); printf 'FAIL  %s\n' "$*"; }
note() { printf '      %s\n' "$*"; }

# --- fixture -----------------------------------------------------------------
[ -f "$LAUNCHER" ] || { echo "BLOCKED: no launcher under test at $LAUNCHER"; exit 2; }
[ -f "$GOOD_COMPARATOR" ] || { echo "BLOCKED: no comparator at $GOOD_COMPARATOR"; exit 2; }

# The scratch tree is rebuilt each run.  `rm -rf` here is confined to a path
# this script names in full, under the scratchpad, and nothing in it is a run
# record; the launcher itself gains no `rm -rf` (see run_f28_candidate.sh).
case "$SCRATCH" in
  */scratchpad/f28_guardwire) ;;
  *) echo "BLOCKED: refusing to clear an unexpected scratch path: $SCRATCH"; exit 2;;
esac
rm -rf "$SCRATCH"
mkdir -p "$SCRATCH" || { echo "BLOCKED: cannot create $SCRATCH"; exit 2; }

echo "=============================================================================="
echo "F28 GUARD-VIRGIN WIRING -- DRIVEN CONTROL"
echo "launcher under test : $LAUNCHER  (md5 $(md5sum "$LAUNCHER" | cut -d' ' -f1))"
echo "live launcher       : $CASE_DIR/run_f28.sh  (md5 $(md5sum "$CASE_DIR/run_f28.sh" | cut -d' ' -f1))"
echo "scratch             : $SCRATCH"
echo "=============================================================================="

# --- extract the function VERBATIM from the launcher under test --------------
awk '/^guard_virgin_section_11_1\(\) \{$/,/^\}$/' "$LAUNCHER" > "$SCRATCH/fn.sh"
head -1 "$SCRATCH/fn.sh" | grep -qx 'guard_virgin_section_11_1() {' \
  && tail -1 "$SCRATCH/fn.sh" | grep -qx '}' \
  && grep -q 'rc_zero=\$?' "$SCRATCH/fn.sh" \
  && grep -q 'rc_time=\$?' "$SCRATCH/fn.sh" \
  && grep -q 'rc_virgin=\$?' "$SCRATCH/fn.sh" \
  && grep -q 'rc_target=\$?' "$SCRATCH/fn.sh" \
  || { echo "BLOCKED: could not extract guard_virgin_section_11_1 intact from $LAUNCHER"; exit 2; }
note "extracted function : $(wc -l < "$SCRATCH/fn.sh") lines, md5 $(md5sum "$SCRATCH/fn.sh" | cut -d' ' -f1)"

# --- extract the ASSEMBLE FRAGMENT verbatim ----------------------------------
awk '/^PHASE="assemble"$/,/^  \|\| abort "cannot create \$RUN_DIR"$/' "$LAUNCHER" \
  > "$SCRATCH/assemble_fragment.sh"
grep -qx 'guard_virgin_section_11_1 "$RUN_DIR"' "$SCRATCH/assemble_fragment.sh" \
  && grep -q 'mkdir -p "\$RUN_DIR/system"' "$SCRATCH/assemble_fragment.sh" \
  || { echo "BLOCKED: could not extract the assemble fragment intact"; exit 2; }
note "assemble fragment  : $(wc -l < "$SCRATCH/assemble_fragment.sh") lines, md5 $(md5sum "$SCRATCH/assemble_fragment.sh" | cut -d' ' -f1)"

# The MUTATED TWIN: identical text, with the guard call moved to AFTER the
# `mkdir` statement.  Group D runs BOTH fragments over BOTH case states: if the
# real one is really measuring POSITION, the twin must lose the ability to
# DISCRIMINATE -- same verdict for the dirty case and the virgin one -- because
# the `mkdir` between them creates `$RUN_DIR/0` in the launcher's own hand.
grep -vx 'guard_virgin_section_11_1 "$RUN_DIR"' "$SCRATCH/assemble_fragment.sh" \
  > "$SCRATCH/assemble_fragment_mutant.sh"
printf 'guard_virgin_section_11_1 "$RUN_DIR"\n' >> "$SCRATCH/assemble_fragment_mutant.sh"

# --- extract the PREFLIGHT FRAGMENT verbatim ---------------------------------
awk '/^if \[ "\$PREFLIGHT" = "1" \]; then$/,/^fi$/' "$LAUNCHER" \
  > "$SCRATCH/preflight_fragment.sh"
grep -qx '  guard_virgin_section_11_1 "$RUN_DIR"' "$SCRATCH/preflight_fragment.sh" \
  && grep -q 'PREFLIGHT COMPLETE AT ZERO COMPUTE' "$SCRATCH/preflight_fragment.sh" \
  || { echo "BLOCKED: could not extract the preflight fragment intact"; exit 2; }
note "preflight fragment : $(wc -l < "$SCRATCH/preflight_fragment.sh") lines, md5 $(md5sum "$SCRATCH/preflight_fragment.sh" | cut -d' ' -f1)"

# --- the harness that hosts the extracted function ---------------------------
cat > "$SCRATCH/drive.sh" <<'DRIVE'
#!/usr/bin/env bash
set -o pipefail
REPO="$1"; TARGET="$2"; FRAGMENT="${3:-}"
CASE_ID="F28_DUCTED_ACTUATOR_DISK"
PHASE="harness-phase-sentinel"
PREFLIGHT=1          # so a sourced preflight fragment takes its own branch;
                     # the assemble fragment never reads this variable.
abort() { echo "ABORT: $*" >&2; exit 1; }
# shellcheck disable=SC1090
. "$FN_SH"
if [ -n "$FRAGMENT" ]; then
  RUN_DIR="$TARGET"
  # shellcheck disable=SC1090
  . "$FRAGMENT"
  echo "FRAGMENT COMPLETED; RUN_DIR/system exists = $([ -d "$RUN_DIR/system" ] && echo yes || echo no)"
  exit 0
fi
guard_virgin_section_11_1 "$TARGET"
echo "GUARD RETURNED; PHASE=$PHASE"
DRIVE
chmod +x "$SCRATCH/drive.sh"
export FN_SH="$SCRATCH/fn.sh"

# --- fake repos, one per comparator flavour ----------------------------------
mkrepo() {   # mkrepo <name> <src|MISSING|NOEXEC|BLIND|ALWAYS2>
  # THE THREE `local`s ARE ON THREE LINES ON PURPOSE.  `local a=$1 d=$a` expands
  # EVERY argument BEFORE the builtin assigns any of them, so `$a` there is the
  # OLD value -- measured here: the fixture built itself under `repo_` with an
  # empty name while every path handed to the harness said `repo_good`, and ten
  # limbs went red for a reason that had nothing to do with the guard.
  local name="$1"
  local kind="$2"
  local d="$SCRATCH/repo_$name/cases/F28_DUCTED_ACTUATOR_DISK"
  mkdir -p "$d"
  case "$kind" in
    MISSING) : ;;
    BLIND)   printf '#!/usr/bin/env python3\nimport sys\nprint("guard says fine")\nsys.exit(0)\n' > "$d/analyse_f28.py"; chmod +x "$d/analyse_f28.py";;
    ALWAYS2) printf '#!/usr/bin/env python3\nimport sys\nsys.stderr.write("nope\\n")\nsys.exit(2)\n' > "$d/analyse_f28.py"; chmod +x "$d/analyse_f28.py";;
    NOEXEC)  cp "$GOOD_COMPARATOR" "$d/analyse_f28.py"; chmod -x "$d/analyse_f28.py";;
    *)       cp "$kind" "$d/analyse_f28.py"; chmod +x "$d/analyse_f28.py";;
  esac
  echo "$SCRATCH/repo_$name"
}
R_GOOD=$(mkrepo good "$GOOD_COMPARATOR")
R_INST=$(mkrepo installed "$INSTALLED_COMPARATOR")
R_MISS=$(mkrepo missing MISSING)
R_NOX=$(mkrepo noexec NOEXEC)
R_BLIND=$(mkrepo blind BLIND)
R_A2=$(mkrepo always2 ALWAYS2)

mkcase() {   # mkcase <name> <virgin|zero|time|frac|absent>
  local d="$SCRATCH/cases/$1"
  case "$2" in
    absent) echo "$d"; return;;
    virgin) mkdir -p "$d";;
    zero)   mkdir -p "$d/0";   printf 'stale\n' > "$d/0/U";;
    time)   mkdir -p "$d/1500"; printf 'stale\n' > "$d/1500/U";;
    frac)   mkdir -p "$d/0.5";;
  esac
  echo "$d"
}

RUN_N=0
run() {   # run <repo> <target> [fragment] -> rc, stdout+stderr in $OUT
  # A FRESH FILE PER CALL.  A shared output path is a reader that can be made
  # to answer about the wrong invocation, and L14/L15 hold one across two runs.
  RUN_N=$((RUN_N+1))
  OUT="$SCRATCH/out.$RUN_N.txt"
  "$SCRATCH/drive.sh" "$1" "$2" "${3:-}" > "$OUT" 2>&1
  RC=$?
}

probe_count() { find "${TMPDIR:-/tmp}" -maxdepth 1 -name 'f28_guard_probe.*' 2>/dev/null | wc -l; }
runs_fingerprint() { [ -d "$RUNS_DIR" ] && find "$RUNS_DIR" | sort | md5sum | cut -d' ' -f1 || echo "ABSENT"; }

RUNS_BEFORE=$(runs_fingerprint)
PROBES_BEFORE=$(probe_count)

echo
echo "--- GROUP A: THE REFUSAL MUST ACTUALLY FIRE -------------------------------"

run "$R_GOOD" "$(mkcase c_zero zero)"
if [ "$RC" != "0" ] && grep -q 'SECTION 11.1: THE VIRGIN-CASE GUARD REFUSED' "$OUT" \
   && grep -q 'a `0` directory already exists' "$OUT"; then
  ok "L1  stale \`0/\` -> launcher aborts (rc=$RC) with the section 11.1 reason"
else
  bad "L1  stale \`0/\` did NOT reach abort with the section 11.1 reason (rc=$RC)"; sed -n '1,12p' "$OUT"
fi

run "$R_GOOD" "$(mkcase c_time time)"
if [ "$RC" != "0" ] && grep -q 'SECTION 11.1: THE VIRGIN-CASE GUARD REFUSED' "$OUT" \
   && grep -q "time directory '1500' already exists" "$OUT"; then
  ok "L2  stale time dir \`1500/\` -> launcher aborts (rc=$RC) with the section 11.1 reason"
else
  bad "L2  stale \`1500/\` did NOT reach abort with the section 11.1 reason (rc=$RC)"; sed -n '1,12p' "$OUT"
fi

run "$R_GOOD" "$(mkcase c_frac frac)"
if [ "$RC" != "0" ] && grep -q 'SECTION 11.1: THE VIRGIN-CASE GUARD REFUSED' "$OUT"; then
  ok "L3  fractional time dir \`0.5/\` -> launcher aborts (rc=$RC)"
else
  bad "L3  fractional \`0.5/\` did not abort (rc=$RC)"; sed -n '1,12p' "$OUT"
fi

echo
echo "--- GROUP B: AND THE PASS MUST ALSO FIRE (a guard that always refuses is"
echo "             as worthless as one that never does) --------------------------"

run "$R_GOOD" "$(mkcase c_virgin virgin)"
if [ "$RC" = "0" ] && grep -q 'VIRGIN' "$OUT" && grep -q 'GUARD RETURNED' "$OUT"; then
  ok "L4  virgin case -> guard passes (rc=$RC) and the launcher proceeds"
else
  bad "L4  virgin case did not pass (rc=$RC)"; sed -n '1,12p' "$OUT"
fi

run "$R_GOOD" "$(mkcase c_absent absent)"
if [ "$RC" = "0" ] && grep -q 'GUARD RETURNED' "$OUT"; then
  ok "L5  NON-EXISTENT \$RUN_DIR -- the NORMAL case at this point -> passes (rc=$RC)"
else
  bad "L5  a non-existent \$RUN_DIR did not pass; the guard errors on the normal case (rc=$RC)"; sed -n '1,20p' "$OUT"
fi

if grep -q 'PHASE=harness-phase-sentinel' "$OUT"; then
  ok "L6  PHASE is restored to the caller's value on the passing path"
else
  bad "L6  PHASE was not restored after a passing guard"
fi

echo
echo "--- GROUP C: THE GUARD ITSELF IS UNDER CONTROL (rule 3 applied to a guard) -"

run "$R_BLIND" "$(mkcase c_v2 virgin)"
if [ "$RC" != "0" ] && grep -q 'THE SECTION 11.1 GUARD IS BLIND' "$OUT"; then
  ok "L7  a comparator that returns 0 on a dirty probe -> launcher aborts BLIND (rc=$RC)"
else
  bad "L7  a BLIND comparator was accepted (rc=$RC)"; sed -n '1,12p' "$OUT"
fi

run "$R_A2" "$(mkcase c_v3 virgin)"
if [ "$RC" != "0" ] && grep -q 'CANNOT DISTINGUISH' "$OUT"; then
  ok "L8  a comparator that refuses everything -> launcher aborts CANNOT DISTINGUISH (rc=$RC)"
else
  bad "L8  a refuse-everything comparator was accepted (rc=$RC)"; sed -n '1,12p' "$OUT"
fi

run "$R_INST" "$(mkcase c_v4 virgin)"
if [ "$RC" != "0" ] && grep -q 'CANNOT DISTINGUISH' "$OUT"; then
  ok "L9  the SUPERSEDED installed comparator (no \`--guard-virgin\` entry point)"
  note "    -> launcher aborts CANNOT DISTINGUISH (rc=$RC): the wiring FAILS CLOSED"
  note "       until the candidate is installed, and does not read its usage-error"
  note "       exit 2 as a refusal."
else
  bad "L9  the superseded comparator was accepted (rc=$RC)"; sed -n '1,12p' "$OUT"
fi

run "$R_MISS" "$(mkcase c_v5 virgin)"
if [ "$RC" != "0" ] && grep -q 'has no instrument' "$OUT"; then
  ok "L10 comparator absent -> launcher aborts 'no instrument' (rc=$RC)"
else
  bad "L10 an absent comparator was accepted (rc=$RC)"; sed -n '1,12p' "$OUT"
fi

run "$R_NOX" "$(mkcase c_v6 virgin)"
if [ "$RC" != "0" ] && grep -q 'has no instrument' "$OUT"; then
  ok "L11 comparator not executable -> launcher aborts 'no instrument' (rc=$RC)"
else
  bad "L11 a non-executable comparator was accepted (rc=$RC)"; sed -n '1,12p' "$OUT"
fi

echo
echo "--- GROUP D: THE POSITION IS LOAD-BEARING, AND THIS TEST CAN SEE IT --------"
echo "    Read as a 2x2.  What a guard is FOR is DISCRIMINATION: refuse the dirty"
echo "    case, pass the virgin one.  The four limbs below run the launcher's OWN"
echo "    assemble fragment, and a mutated twin with the call moved one statement"
echo "    later, over both case states.  The real fragment discriminates; the twin"
echo "    returns REFUSE for both, because the \`mkdir\` on the line between them"
echo "    has created \`\$RUN_DIR/0\` in the launcher's own hand and the guard is"
echo "    then reading the launcher's footprint instead of the case's history."

D1=$(mkcase c_pos_dirty zero)
run "$R_GOOD" "$D1" "$SCRATCH/assemble_fragment.sh"
if [ "$RC" != "0" ] && grep -q 'SECTION 11.1: THE VIRGIN-CASE GUARD REFUSED' "$OUT" \
   && [ ! -d "$D1/system" ]; then
  ok "L12 REAL fragment,  DIRTY case  -> REFUSE (rc=$RC), and \$RUN_DIR/system was"
  note "    never created: the launcher wrote nothing into the case it refused."
else
  bad "L12 the real fragment did not refuse a dirty case (rc=$RC, system present=$([ -d "$D1/system" ] && echo yes || echo no))"; sed -n '1,12p' "$OUT"
fi

D2=$(mkcase c_pos_virgin virgin)
run "$R_GOOD" "$D2" "$SCRATCH/assemble_fragment.sh"
if [ "$RC" = "0" ] && [ -d "$D2/system" ] && [ -d "$D2/0" ]; then
  ok "L13 REAL fragment,  VIRGIN case -> PASS (rc=$RC), and the assemble mkdir ran"
  note "    (\`system/\` and \`0/\` both created).  The guard does not block real work."
else
  bad "L13 the real fragment did not pass a virgin case (rc=$RC)"; sed -n '1,12p' "$OUT"
fi

D3=$(mkcase c_mut_dirty zero)
run "$R_GOOD" "$D3" "$SCRATCH/assemble_fragment_mutant.sh"
MUT_DIRTY_RC=$RC
D4=$(mkcase c_mut_virgin virgin)
run "$R_GOOD" "$D4" "$SCRATCH/assemble_fragment_mutant.sh"
MUT_VIRGIN_RC=$RC
MUT_VIRGIN_OUT="$OUT"

if [ "$MUT_VIRGIN_RC" != "0" ] && grep -q 'SECTION 11.1: THE VIRGIN-CASE GUARD REFUSED' "$MUT_VIRGIN_OUT"; then
  ok "L14 MUTANT fragment, VIRGIN case -> REFUSE (rc=$MUT_VIRGIN_RC).  A guard one"
  note "    statement later refuses a case that was CLEAN when the launcher opened"
  note "    it, because \`mkdir -p \"\$RUN_DIR/0\"\` on the preceding line made it"
  note "    dirty.  Its \`0/\` is the launcher's own footprint, and \`\$RUN_DIR/0/\`"
  note "    exists here: $([ -d "$D4/0" ] && echo yes || echo no)."
else
  bad "L14 the mutant did not refuse a virgin case (rc=$MUT_VIRGIN_RC); the twin is not the mutation intended"; sed -n '1,12p' "$MUT_VIRGIN_OUT"
fi

if [ "$MUT_DIRTY_RC" != "0" ] && [ "$MUT_VIRGIN_RC" != "0" ]; then
  ok "L15 THE DISCRIMINATION LIMB.  Real fragment: dirty -> refuse, virgin -> pass."
  note "    Mutant fragment: dirty -> rc=$MUT_DIRTY_RC, virgin -> rc=$MUT_VIRGIN_RC --"
  note "    THE SAME ANSWER FOR BOTH.  The moved guard's output is independent of"
  note "    the case's true prior state, so it carries no information about it: it"
  note "    is not a guard that fires less often, it is a guard that has stopped"
  note "    measuring.  L12/L13 therefore measure POSITION, not mere presence, and"
  note "    the insertion point immediately after \`PHASE=\"assemble\"\` is where the"
  note "    registered guard has something left to see."
else
  bad "L15 the mutant did NOT return the same verdict for both states (dirty rc=$MUT_DIRTY_RC, virgin rc=$MUT_VIRGIN_RC); re-derive what position buys before trusting L12"
fi

echo
# SINGLE QUOTES ON THE NEXT TWO LINES.  A backtick inside a DOUBLE-quoted echo
# is command substitution: `--preflight` was RUN, the banner printed with a hole
# in it and the shell said "--preflight: command not found" in the middle of a
# suite that still reported 21/21.
echo '--- GROUP D2: `--preflight` IS GUARDED TOO, AND AT ZERO COMPUTE ------------'
echo '    `--preflight` documents itself as running EVERY GUARD and stopping at zero'
echo "    compute.  A guard preflight does not run is a guard preflight cannot"
echo "    discover broken -- the failure would surface at phase=assemble on the"
echo "    gated run instead.  Its branch also creates \$RUN_DIR itself, so the call"
echo "    precedes that mkdir for the same reason it precedes the assemble one."

P1=$(mkcase c_pre_dirty zero)
run "$R_GOOD" "$P1" "$SCRATCH/preflight_fragment.sh"
if [ "$RC" != "0" ] && grep -q 'SECTION 11.1: THE VIRGIN-CASE GUARD REFUSED' "$OUT" \
   && ! grep -q 'PREFLIGHT COMPLETE' "$OUT"; then
  ok "L16 REAL preflight fragment, DIRTY case -> REFUSE (rc=$RC) and preflight"
  note "    never reported complete.  The wiring is found broken at ZERO COMPUTE."
else
  bad "L16 the preflight fragment did not refuse a dirty case (rc=$RC)"; sed -n '1,12p' "$OUT"
fi

P2=$(mkcase c_pre_virgin virgin)
run "$R_GOOD" "$P2" "$SCRATCH/preflight_fragment.sh"
if [ "$RC" = "0" ] && grep -q 'PREFLIGHT COMPLETE AT ZERO COMPUTE' "$OUT" \
   && [ -d "$P2" ] && [ ! -d "$P2/0" ]; then
  ok "L17 REAL preflight fragment, VIRGIN case -> PASS (rc=$RC), preflight completes,"
  note "    \$RUN_DIR exists and carries NO \`0/\`: preflight leaves a case a later"
  note "    gated run's own guard will still accept."
else
  bad "L17 the preflight fragment did not pass a virgin case cleanly (rc=$RC)"; sed -n '1,12p' "$OUT"
fi

run "$R_INST" "$(mkcase c_pre_inst virgin)" "$SCRATCH/preflight_fragment.sh"
if [ "$RC" != "0" ] && grep -q 'CANNOT DISTINGUISH' "$OUT"; then
  ok "L18 preflight with the SUPERSEDED comparator -> aborts at zero compute (rc=$RC)."
  note "    This is the whole argument for guarding preflight: today's tree fails"
  note "    HERE instead of at phase=assemble on the gated run."
else
  bad "L18 preflight did not catch the superseded comparator (rc=$RC)"; sed -n '1,12p' "$OUT"
fi

echo
echo "--- GROUP E: FOOTPRINT ----------------------------------------------------"

PROBES_AFTER=$(probe_count)
if [ "$PROBES_AFTER" = "$PROBES_BEFORE" ]; then
  ok "L19 the guard's own probe directories are torn down: ${TMPDIR:-/tmp}/f28_guard_probe.* count $PROBES_BEFORE -> $PROBES_AFTER"
else
  bad "L19 probe directories leaked: $PROBES_BEFORE -> $PROBES_AFTER"
fi

RUNS_AFTER=$(runs_fingerprint)
if [ "$RUNS_AFTER" = "$RUNS_BEFORE" ]; then
  ok "L20 nothing was written under $RUNS_DIR (tree fingerprint unchanged: $RUNS_BEFORE)"
else
  bad "L20 THIS SELFTEST TOUCHED $RUNS_DIR ($RUNS_BEFORE -> $RUNS_AFTER)"
fi

# L21 CARRIES ITS OWN PLANT, AND IT EARNED IT.  A bare `grep -q 'rm -rf'` over
# this launcher matched the COMMENT that says "NO `rm -rf` IS ADDED TO THIS
# FILE" -- the launcher was clean and the check said dirty.  That is precisely
# the 9c223449 defect: a pattern matching a banner rather than code, only in the
# other direction.  So the check strips comments first, and it is PLANTED: a
# copy with a real `rm -rf` line must come back dirty, or the check is blind and
# its clean verdict on the launcher is worth nothing (CLAUDE.md rule 3).
rmrf_code() { sed -e 's/#.*$//' "$1" | grep -q 'rm -rf'; }
cp "$LAUNCHER" "$SCRATCH/launcher_planted.sh"
printf 'rm -rf "$RUN_DIR"\n' >> "$SCRATCH/launcher_planted.sh"
if rmrf_code "$SCRATCH/launcher_planted.sh"; then
  if rmrf_code "$LAUNCHER"; then
    bad "L21 the launcher under test contains \`rm -rf\` IN CODE, which its own header forbids"
  else
    ok "L21 no \`rm -rf\` in the launcher's CODE; the planted copy came back dirty,"
    note "    so the clean reading is a reading and not a blind zero.  (A bare grep"
    note "    on the raw text goes red here -- on the launcher's own comment saying"
    note "    it adds none.  That is the 9c223449 failure mode, inverted.)"
  fi
else
  bad "L21 THE CHECK IS BLIND: it did not see a planted \`rm -rf\`; its clean verdict on the launcher is not evidence"
fi

echo
echo "=============================================================================="
echo "PASS $PASS   FAIL $FAIL"
echo "NOT A RESULT in the gate sense: this is an INSTRUMENT CONTROL on a launcher"
echo "guard.  No solver ran, no case was graded, no verdict is issued here."
echo "=============================================================================="
[ "$FAIL" = "0" ] || exit 1
exit 0
