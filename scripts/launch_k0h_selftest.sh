#!/usr/bin/env bash
# ==========================================================================
# launch_k0h.sh SELFTEST -- the rc capture DRIVEN, not asserted.
#
# A launcher that has never been shown to write a NON-ZERO rc is a planted
# zero with no control (standing rule 3).  Every arm below drives a REAL
# process to a REAL exit state through the REAL launcher and reads the rc back
# out of the STATUS file on disk.
#
# THE ARM THAT MATTERS MOST IS THE DETACHED ONE.  `setsid timeout ... ; $?`
# returns 0 for a crashed child (measured on this box), so a detached launcher
# that has only ever been tested in the foreground proves nothing about the
# path it will actually run on.
# ==========================================================================
# ========================================================================
# K0h DERIVATION BLOCK -- READ THIS BEFORE THE DIFF.
#
# This file is a DERIVATION of the FROZEN K0g instrument
#     scripts/launch_k0g_selftest.sh
#     git blob f7594e00d9caff1f22c2ecfa4598f0b80de1807f
# registered at docs/campaigns/F14-cooling-ladder/K0h_PREREGISTRATION.md
# section 7.7.  THE K0g ANCESTOR IS NOT EDITED (standing rule 6); this
# file was written from its HEAD BLOB, not from the worktree.
#
# THE DERIVATION IS MECHANICALLY CHECKABLE.  Outside this block every
# byte of this file is the ancestor's bytes under the UNCONDITIONAL
# substitution
#     k0g -> k0h ,  K0g -> K0h ,  K0G -> K0H
# and NOTHING ELSE.  There is no functional change in this file.
#
# CONSEQUENCE OF AN UNCONDITIONAL RENAME, DISCLOSED RATHER THAN
# SMOOTHED.  A historical note below that now reads "K0h attempt 1",
# "measured on K0h" or similar describes an event that happened under
# K0g, this file's ancestor.  NO HISTORICAL CLAIM IN THIS FILE IS A K0h
# MEASUREMENT.  K0h HAS RUN NO COMPUTE: no
# verification/runs/F14-cooling-ladder/K0h_runs/ exists, and none may be
# created until the supervisor FREEZES the pre-registration by sha.
#
# PROVENANCE PINS -- DECLARATIVE AND PRINT-ONLY.  They gate nothing and
# no code branches on them.  GRADING_PATH_FREEZE_COMMIT is the DRAFT
# placeholder "PIN-AT-FREEZE"; THE SUPERVISOR SETS IT AT FREEZE and no
# lane, and no run, sets it.
# ========================================================================
GRADING_PATH_FREEZE_COMMIT="PIN-AT-FREEZE"   # SUPERVISOR SETS THIS AT FREEZE
SELF_REL="scripts/launch_k0h_selftest.sh"
export GRADING_PATH_FREEZE_COMMIT SELF_REL

set -u
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  ok    %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  FAIL  %s   %s\n' "$1" "${2:-}"; }

mkcase() {  # $1 = case name; a minimal case the pre-flight accepts
    # STAGED AS THE BUILDER STAGES: `0.orig/`, and NO `0/`.
    # THIS FIXTURE CHANGE IS PART OF THE REPAIR, NOT COSMETIC.  It used to
    # create `0/` directly, which is a case NO REPAIRED BUILDER PRODUCES and
    # which clause 7 must now REFUSE.  A fixture that cannot occur in
    # production tests the launcher against itself.
    d="$W/runs/$1"; mkdir -p "$d/0.orig" "$d/constant" "$d/system"
    printf 'simulationType  RAS;\n\nRAS\n{\n    RASModel        kOmegaSST;\n    turbulence      on;\n}\n' \
        > "$d/constant/turbulenceProperties"
    printf 'solvers\n{\n    "(p_rgh|p_rghFinal)"\n    {\n    }\n    "(U|T|k|omega|epsilon)(Final)?"\n    {\n    }\n}\nrelaxationFactors\n{\n    equations\n    {\n        U               0.4;\n        T               0.6;\n        "(k|omega|epsilon)" 0.4;\n    }\n}\n' \
        > "$d/system/fvSolution"
    for f in T U p_rgh alphat nut k omega; do echo "internalField uniform 0;" > "$d/0.orig/$f"; done
    echo "$d"
}

dirty_zero() {   # $1 = case name: a case a REPAIRED launcher must REFUSE --
    # a pre-existing `0/`, as an interrupted or already-started run leaves.
    # Its fields are VALID so that with the guard stripped the case really can
    # launch: a negative control whose case fails for some OTHER reason proves
    # nothing about the guard.
    d=$(mkcase "$1"); cp -r "$d/0.orig" "$d/0"; echo "$d"
}

dirty_time() {   # $1 = case name: a pre-existing NUMERIC TIME directory,
    # as a stray write from an earlier process leaves.  No `0/`.
    d=$(mkcase "$1"); mkdir -p "$d/60"; echo "internalField uniform 0;" > "$d/60/T"; echo "$d"
}

# THE NEGATIVE-CONTROL LAUNCHER: this file's own launcher with the clause-7
# call sites DELETED.  Built by an exact line-range delete of the two guard
# blocks, and THE STRIP IS ITSELF VERIFIED BELOW -- a "guard removed" control
# that silently removed nothing would pass for the wrong reason and would be
# the very failure this whole section exists to catch.
#
# THE SECOND EDIT, DISCLOSED RATHER THAN BURIED.  The copy lives in $W, and
# `launch_k0h.sh` resolves its helper scripts through
# `SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` -- which in a copy
# resolves to $W, where `build_k0h.py` does not exist.  MEASURED, not assumed:
# the first version of this control refused with rc=2 on every dirty case, and
# the refusal came from the PRE-FLIGHT failing to find `build_k0h.py`, NOT from
# the guard.  It would have read as "the guard still fires" -- a negative
# control that appears to confirm the thing it is supposed to refute.  So the
# copy also has its `SELF` pinned to the real scripts directory, and the arms
# below assert that the copy differs from the original in EXACTLY these two
# ways and no other.
UNGUARDED="$W/launch_k0h_UNGUARDED.sh"
sed -e '/^if ! python3 "\$SELF\/mark_done_k0h.py" --root "\$ROOT" --launch-guard "\$CASE"; then$/,/^fi$/d' \
    -e "s|^SELF=\"\$(cd \"\$(dirname \"\${BASH_SOURCE\[0\]}\")\" && pwd)\"$|SELF=\"$SELF\"|" \
    "$SELF/launch_k0h.sh" > "$UNGUARDED"

mksolver() {  # $1 = name, $2 = body
    printf '#!/usr/bin/env bash\n%s\n' "$2" > "$W/bin/$1"; chmod +x "$W/bin/$1"
}
mkdir -p "$W/bin"; export PATH="$W/bin:$PATH"

read_status() { grep -o "$2=[^ ]*" "$1" 2>/dev/null | head -1 | cut -d= -f2; }

echo "=========================================================================="
echo "launch_k0h.sh SELFTEST"
echo "=========================================================================="
echo "-- rc capture, FOREGROUND, four exit states driven for real"
for spec in "clean:exit 0:0:clean" \
            "nonzero:exit 7:7:SOLVER_NONZERO_EXIT" \
            "signal:kill -SEGV \$\$:139:KILLED_BY_SIGNAL_11" ; do
    name="${spec%%:*}"; rest="${spec#*:}"; body="${rest%%:*}"; rest="${rest#*:}"
    want_rc="${rest%%:*}"; want_note="${rest##*:}"
    d=$(mkcase "$name"); mksolver fakeFoam "$body"
    bash "$SELF/launch_k0h.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none --no-detach >/dev/null 2>&1
    st="$W/runs/STATUS.$name"
    got_rc=$(read_status "$st" rc); got_note=$(read_status "$st" note)
    if [ "$got_rc" = "$want_rc" ] && [ "$got_note" = "$want_note" ]; then
        ok "$name: STATUS rc=$got_rc note=$got_note"
    else bad "$name" "wanted rc=$want_rc note=$want_note, got rc=${got_rc:-<none>} note=${got_note:-<none>}"; fi
done

echo "-- cap expiry is DISTINGUISHABLE from a crash (rc=124, not 0, not 143)"
d=$(mkcase expiry); mksolver fakeFoam "sleep 30"
bash "$SELF/launch_k0h.sh" --case-dir "$d" --timeout 1 --solver fakeFoam --foam-bashrc none --no-detach >/dev/null 2>&1
st="$W/runs/STATUS.expiry"
[ "$(read_status "$st" rc)" = "124" ] && ok "expiry: rc=124 note=$(read_status "$st" note)" \
    || bad "expiry" "got rc=$(read_status "$st" rc)"

echo "-- THE SETSID TRAP: DETACHED, a crashing solver must still record rc=7"
d=$(mkcase detached); mksolver fakeFoam "exit 7"
bash "$SELF/launch_k0h.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none >/dev/null 2>&1
st="$W/runs/STATUS.detached"
for _ in 1 2 3 4 5 6 7 8 9 10; do [ -f "$st" ] && break; sleep 0.5; done
got=$(read_status "$st" rc)
[ "$got" = "7" ] && ok "detached: STATUS rc=7 -- setsid did NOT swallow it" \
    || bad "detached" "got rc=${got:-<none>}; a bare 'setsid ... ; \$?' returns 0 here"

echo "-- the DETACHED run really was detached (new session id)"
d=$(mkcase session); mksolver fakeFoam 'ps -o sid= -p $$ > "$OLDPWD/sid.child" 2>/dev/null; exit 0'
( cd "$W" && bash "$SELF/launch_k0h.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none >/dev/null 2>&1 )
for _ in 1 2 3 4 5 6 7 8 9 10; do [ -f "$W/runs/STATUS.session" ] && break; sleep 0.5; done
mysid=$(ps -o sid= -p $$ | tr -d ' ')
csid=$(tr -d ' ' < "$W/sid.child" 2>/dev/null || echo "")
[ -n "$csid" ] && [ "$csid" != "$mysid" ] && ok "detached: child session $csid != this shell's $mysid" \
    || bad "detach" "child sid=${csid:-<unread>} this=$mysid"

echo "-- a PRE-FLIGHT refusal writes NO STATUS (nothing ran, so there is no rc)"
d=$(mkcase preflight); mv "$d/0.orig/nut" "$d/0.orig/nut.HIDDEN"; mksolver fakeFoam "exit 0"
bash "$SELF/launch_k0h.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none --no-detach >/dev/null 2>&1
rc=$?
[ ! -f "$W/runs/STATUS.preflight" ] && [ "$rc" = "2" ] \
    && ok "pre-flight: refused rc=2 and wrote NO STATUS" \
    || bad "pre-flight" "rc=$rc, STATUS exists=$([ -f "$W/runs/STATUS.preflight" ] && echo yes || echo no)"

echo "-- a MISSING T refuses: the age guard would have no datum"
# WHICH CHECK NOW FIRES, STATED RATHER THAN LEFT AMBIGUOUS.  Before the
# clause-7 repair the builder wrote `0/` and this arm deleted `0/T`, so
# section 3's `[ -f "$CASE_DIR/0/T" ]` was the plausible refuser.  After the
# repair the case is staged as `0.orig/` and `0/` is created by the launcher,
# so deleting `0.orig/T` is caught EARLIER, by the consumer-side pre-flight --
# `T` is in every registered completion set and is never solver-generated.
# Both refuse rc=2 and neither writes a STATUS, so the arm's VERDICT is
# unchanged; its ATTRIBUTION is not, and the arm asserts the reason it is
# actually getting rather than the one it used to get.
d=$(mkcase noT); rm -f "$d/0.orig/T"; mksolver fakeFoam "exit 0"
err=$(bash "$SELF/launch_k0h.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none --no-detach 2>&1 >/dev/null)
rc=$?
if [ "$rc" = "2" ] && [ ! -f "$W/runs/STATUS.noT" ]; then
    ok "no T: refused rc=2 and wrote NO STATUS   [reason: $(printf '%s' "$err" | grep -o 'completeness assertion\|no 0/T' | head -1)]"
else
    bad "no T" "rc=$rc, STATUS exists=$([ -f "$W/runs/STATUS.noT" ] && echo yes || echo no)"
fi
# AND section 3's own datum check is still driven, on the one input that
# reaches it: `0.orig/T` present (so the pre-flight passes) but unreadable as
# a file after the stage.  Without this arm section 3 would become a SECOND
# dead lever -- a guard kept in the file that no input can fire -- which is
# exactly the defect this whole change set repairs.
d=$(mkcase noT2); mksolver fakeFoam "exit 0"
rm -f "$d/0.orig/T"; mkdir -p "$d/0.orig/T"          # a DIRECTORY named T
err=$(bash "$SELF/launch_k0h.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none --no-detach 2>&1 >/dev/null)
rc=$?
[ "$rc" = "2" ] && ok "0/T not a regular file: refused rc=2 (section 3's age-guard datum check is reachable, not a second dead lever)" \
                || bad "0/T not a file" "rc=$rc -- section 3's check may be unreachable"

echo "-- ranks != 1 refuses (K0h is registered SERIAL)"
d=$(mkcase ranks); mksolver fakeFoam "exit 0"
bash "$SELF/launch_k0h.sh" --case-dir "$d" --timeout 30 --ranks 4 --solver fakeFoam --no-detach >/dev/null 2>&1
[ "$?" = "2" ] && ok "ranks=4: refused rc=2" || bad "ranks=4" "did not refuse"


echo "-- NEGATIVE CONTROL: THE REAL SOLVER, ON THE REAL PATH, WITH NO FIXTURE --"
# THE ARM THAT WOULD HAVE CAUGHT K0h ATTEMPT 1 (seven cases, rc=127, wall=0).
# Every arm above installs a FAKE SOLVER ON PATH.  They prove the rc plumbing
# and they say NOTHING about whether this launcher can reach a real solver in a
# real environment -- A LAUNCHER SELFTEST THAT SUPPLIES ITS OWN FIXTURES IS
# TESTING THE LAUNCHER AGAINST ITSELF.  This arm supplies nothing.
REAL_SOLVER="buoyantBoussinesqPimpleFoam"
REAL_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
if [ -f "$REAL_BASHRC" ]; then
    rp=$( set +u; . "$REAL_BASHRC" >/dev/null 2>&1; command -v "$REAL_SOLVER" 2>/dev/null )
    [ -n "$rp" ] && ok "the REAL solver resolves after sourcing the REAL environment   [$rp]" \
        || bad "real solver" "sourcing $REAL_BASHRC did not put $REAL_SOLVER on PATH"
    # and the launcher itself must reach it: --no-detach, cap 0 is rejected, so
    # use a 1 s cap and accept ANY rc -- what is under test is that the solver
    # was FOUND, i.e. that rc is NOT 127 and STATUS records a solver_path.
    d=$(mkcase realenv)
    bash "$SELF/launch_k0h.sh" --case-dir "$d" --timeout 1 --solver "$REAL_SOLVER" --no-detach >/dev/null 2>&1
    st="$W/runs/STATUS.realenv"
    grc=$(read_status "$st" rc); gsp=$(read_status "$st" solver_path)
    if [ -f "$st" ] && [ "$grc" != "127" ] && [ -n "$gsp" ] && [ "$gsp" != "unresolved" ]; then
        ok "the LAUNCHER reaches the real solver: rc=$grc (not 127), solver_path recorded"
    else
        bad "launcher/real solver" "rc=${grc:-<none>} solver_path=${gsp:-<none>} -- 127 or an empty path means the environment is not reaching the solver"
    fi
else
    bad "real solver" "$REAL_BASHRC absent -- this arm cannot be run, and a skipped arm is NOT a passed arm"
fi

echo "-- and the REFUSAL half: an unreachable solver REFUSES and writes NO STATUS --"
d=$(mkcase unreachable)
bash "$SELF/launch_k0h.sh" --case-dir "$d" --timeout 30 --solver definitelyNotASolver_k0h \
     --foam-bashrc none --no-detach >/dev/null 2>&1
rc=$?
[ "$rc" = "2" ] && [ ! -f "$W/runs/STATUS.unreachable" ] \
    && ok "unresolvable solver: refused rc=2 and wrote NO STATUS (never started != ran and failed)" \
    || bad "unreachable" "rc=$rc, STATUS exists=$([ -f "$W/runs/STATUS.unreachable" ] && echo yes || echo no)"

echo "-- and a MISSING environment file REFUSES rather than launching blind --"
d=$(mkcase noenv); mksolver fakeFoam "exit 0"
bash "$SELF/launch_k0h.sh" --case-dir "$d" --timeout 30 --solver fakeFoam \
     --foam-bashrc /nonexistent/etc/bashrc --no-detach >/dev/null 2>&1
[ "$?" = "2" ] && ok "absent --foam-bashrc: refused rc=2" || bad "absent bashrc" "did not refuse"

# =========================================================================
# CLAUSE 7 -- THE LAUNCH GUARD -- DRIVEN THROUGH THE LAUNCH PATH.
#
# WHY THESE ARMS EXIST AND WHY THEY LOOK LIKE THIS.
# `mark_done_k0h.py` has carried a clause-7 selftest since it was written, and
# it PASSED throughout the entire period in which clause 7 had NO CALL SITE
# ANYWHERE.  It passed because it drove `launch_guard()` DIRECTLY, as a
# function.  Calling the function directly IS the defect: it proves the rule is
# written down, and says nothing about whether anything applies it.  Every arm
# below therefore invokes `launch_k0h.sh` -- the real launch path, with the
# real argument parsing, the real detach decision and the real ordering.
# =========================================================================
echo "-- CLAUSE 7: the launch guard, DRIVEN THROUGH launch_k0h.sh --"

# ---- the strip that makes the negative control possible is verified FIRST --
# COUNT EXECUTABLE CALL SITES, NOT MENTIONS.  The first version of this arm
# counted every line containing the flag and reported 3 guarded / 1 stripped,
# because a COMMENT in launch_k0h.sh names the flag in order to describe the
# defect.  It called a correct strip broken.  A census instrument that counts
# prose as code is the same class of error as a guard that is never called.
n_guarded=$(grep -c '^[^#]*--launch-guard' "$SELF/launch_k0h.sh" || true)
n_stripped=$(grep -c '^[^#]*--launch-guard' "$UNGUARDED" || true)
if [ "$n_guarded" -ge 2 ] && [ "$n_stripped" = "0" ]; then
    ok "the UNGUARDED control launcher really is unguarded: $n_guarded EXECUTABLE call site(s) in launch_k0h.sh, 0 after the strip"
else
    bad "unguarded strip" "guarded=$n_guarded stripped=$n_stripped -- the negative control below would be meaningless"
fi
# and the copy must differ ONLY by the guard blocks and the pinned SELF line.
n_only_removed=$(diff "$SELF/launch_k0h.sh" "$UNGUARDED" | grep -c '^[<>]' || true)
n_self=$(grep -c "^SELF=\"$SELF\"$" "$UNGUARDED" || true)
if [ "$n_only_removed" = "10" ] && [ "$n_self" = "1" ]; then
    ok "the UNGUARDED copy differs by EXACTLY the 2 guard blocks (8 lines) + the pinned SELF line (1 removed, 1 added) = 10"
else
    bad "unguarded diff" "diff lines=$n_only_removed (expected 10), pinned SELF lines=$n_self (expected 1) -- the control is not the launcher-minus-the-guard"
fi
# and it must differ ONLY by those lines: a strip that broke the file would
# make every negative-control arm fail for the wrong reason.
if bash -n "$UNGUARDED" 2>/dev/null; then
    ok "the UNGUARDED control launcher is still syntactically valid bash"
else
    bad "unguarded syntax" "the strip broke the file"
fi

# ---- ARM 1: A CLEAN CASE LAUNCHES, and the stage really happened ----------
d=$(mkcase clause7_clean); mksolver fakeFoam "exit 0"
bash "$SELF/launch_k0h.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none --no-detach >/dev/null 2>&1
rc=$?
if [ "$rc" = "0" ] && [ -f "$W/runs/STATUS.clause7_clean" ]; then
    ok "CLEAN (0.orig/, no 0/): LAUNCHED, rc=0, STATUS written"
else
    bad "clause7 clean" "rc=$rc, STATUS exists=$([ -f "$W/runs/STATUS.clause7_clean" ] && echo yes || echo no)"
fi
[ -f "$d/0/T" ] && ok "CLEAN: the launcher STAGED 0/ from 0.orig/ (0/T exists, and the builder wrote none)" \
                || bad "clause7 stage" "no 0/T after launch -- the stage did not run"
[ -d "$d/0.orig" ] && ok "CLEAN: 0.orig/ is left in place, so a re-stage is possible and the provenance is not destroyed" \
                   || bad "clause7 0.orig" "0.orig/ vanished"

# ---- ARM 2: A PRE-EXISTING 0/ IS REFUSED, exit 2, NO STATUS --------------
d=$(dirty_zero clause7_dirty0); mksolver fakeFoam "exit 0"
bash "$SELF/launch_k0h.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none --no-detach >/dev/null 2>&1
rc=$?
if [ "$rc" = "2" ] && [ ! -f "$W/runs/STATUS.clause7_dirty0" ]; then
    ok "DIRTY 0/: REFUSED rc=2 and wrote NO STATUS (nothing ran, so no rc is invented)"
else
    bad "clause7 dirty 0/" "rc=$rc, STATUS exists=$([ -f "$W/runs/STATUS.clause7_dirty0" ] && echo yes || echo no)"
fi

# ---- ARM 3: A PRE-EXISTING NUMERIC TIME DIRECTORY IS REFUSED ------------
d=$(dirty_time clause7_dirtyT); mksolver fakeFoam "exit 0"
bash "$SELF/launch_k0h.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none --no-detach >/dev/null 2>&1
rc=$?
if [ "$rc" = "2" ] && [ ! -f "$W/runs/STATUS.clause7_dirtyT" ]; then
    ok "DIRTY 60/: REFUSED rc=2 and wrote NO STATUS"
else
    bad "clause7 dirty time dir" "rc=$rc, STATUS exists=$([ -f "$W/runs/STATUS.clause7_dirtyT" ] && echo yes || echo no)"
fi

# ---- ARM 4: THE NEGATIVE CONTROL.  THE SAME DIRTY CASES, GUARD REMOVED, --
# ---- MUST LAUNCH.  This is what proves the GUARD is what refused above,  --
# ---- and not something incidental to a dirty case.  A control shown only --
# ---- in its silent direction is not a control.                           --
d=$(dirty_zero clause7_nc_dirty0); mksolver fakeFoam "exit 0"
bash "$UNGUARDED" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none --no-detach >/dev/null 2>&1
rc=$?
if [ "$rc" = "0" ] && [ -f "$W/runs/STATUS.clause7_nc_dirty0" ]; then
    ok "NEGATIVE CONTROL, dirty 0/: with the guard REMOVED the SAME case LAUNCHES (rc=0, STATUS written) -- the guard is what refused ARM 2"
else
    bad "NEGATIVE CONTROL dirty 0/" "rc=$rc, STATUS exists=$([ -f "$W/runs/STATUS.clause7_nc_dirty0" ] && echo yes || echo no) -- ARM 2's refusal is NOT attributable to the guard"
fi

d=$(dirty_time clause7_nc_dirtyT); mksolver fakeFoam "exit 0"
bash "$UNGUARDED" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none --no-detach >/dev/null 2>&1
rc=$?
if [ "$rc" = "0" ] && [ -f "$W/runs/STATUS.clause7_nc_dirtyT" ]; then
    ok "NEGATIVE CONTROL, dirty 60/: with the guard REMOVED the SAME case LAUNCHES -- the guard is what refused ARM 3"
else
    bad "NEGATIVE CONTROL dirty 60/" "rc=$rc, STATUS exists=$([ -f "$W/runs/STATUS.clause7_nc_dirtyT" ] && echo yes || echo no) -- ARM 3's refusal is NOT attributable to the guard"
fi

# ---- ARM 5: AN ABSENT 0.orig/ REFUSES rather than launching an unbuilt case
d=$(mkcase clause7_no_orig); rm -rf "$d/0.orig"; mksolver fakeFoam "exit 0"
bash "$SELF/launch_k0h.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none --no-detach >/dev/null 2>&1
rc=$?
if [ "$rc" = "2" ] && [ ! -f "$W/runs/STATUS.clause7_no_orig" ]; then
    ok "NO 0.orig/: REFUSED rc=2 -- an unbuilt case is not launched and no age-guard datum is invented"
else
    bad "clause7 no 0.orig" "rc=$rc"
fi

# ---- ARM 6: THE DETACHED PATH IS GUARDED TOO.  orchestrate_k0h.py starts ---
# ---- the launcher detached; a guard only on the foreground path would be ---
# ---- absent from the ONLY path production uses.                           ---
d=$(dirty_zero clause7_detached); mksolver fakeFoam "exit 0"
bash "$SELF/launch_k0h.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none >/dev/null 2>&1
rc=$?
if [ "$rc" = "2" ] && [ ! -f "$W/runs/STATUS.clause7_detached" ]; then
    ok "DETACHED path, dirty 0/: REFUSED rc=2 SYNCHRONOUSLY, before the fork -- the caller sees it"
else
    bad "clause7 detached" "rc=$rc, STATUS exists=$([ -f "$W/runs/STATUS.clause7_detached" ] && echo yes || echo no)"
fi

echo "=========================================================================="
echo "  $PASS passed, $FAIL failed"
echo "=========================================================================="
[ "$FAIL" = "0" ] || exit 1
