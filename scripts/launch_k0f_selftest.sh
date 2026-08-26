#!/usr/bin/env bash
# ==========================================================================
# launch_k0f.sh SELFTEST -- the rc capture DRIVEN, not asserted.
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
set -u
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  ok    %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  FAIL  %s   %s\n' "$1" "${2:-}"; }

mkcase() {  # $1 = case name; a minimal case the pre-flight accepts
    d="$W/runs/$1"; mkdir -p "$d/0" "$d/constant" "$d/system"
    printf 'simulationType  RAS;\n\nRAS\n{\n    RASModel        kOmegaSST;\n    turbulence      on;\n}\n' \
        > "$d/constant/turbulenceProperties"
    printf 'solvers\n{\n    "(p_rgh|p_rghFinal)"\n    {\n    }\n    "(U|T|k|omega|epsilon)(Final)?"\n    {\n    }\n}\nrelaxationFactors\n{\n    equations\n    {\n        U               0.4;\n        T               0.6;\n        "(k|omega|epsilon)" 0.4;\n    }\n}\n' \
        > "$d/system/fvSolution"
    for f in T U p_rgh alphat nut k omega; do echo "internalField uniform 0;" > "$d/0/$f"; done
    echo "$d"
}

mksolver() {  # $1 = name, $2 = body
    printf '#!/usr/bin/env bash\n%s\n' "$2" > "$W/bin/$1"; chmod +x "$W/bin/$1"
}
mkdir -p "$W/bin"; export PATH="$W/bin:$PATH"

read_status() { grep -o "$2=[^ ]*" "$1" 2>/dev/null | head -1 | cut -d= -f2; }

echo "=========================================================================="
echo "launch_k0f.sh SELFTEST"
echo "=========================================================================="
echo "-- rc capture, FOREGROUND, four exit states driven for real"
for spec in "clean:exit 0:0:clean" \
            "nonzero:exit 7:7:SOLVER_NONZERO_EXIT" \
            "signal:kill -SEGV \$\$:139:KILLED_BY_SIGNAL_11" ; do
    name="${spec%%:*}"; rest="${spec#*:}"; body="${rest%%:*}"; rest="${rest#*:}"
    want_rc="${rest%%:*}"; want_note="${rest##*:}"
    d=$(mkcase "$name"); mksolver fakeFoam "$body"
    bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none --no-detach >/dev/null 2>&1
    st="$W/runs/STATUS.$name"
    got_rc=$(read_status "$st" rc); got_note=$(read_status "$st" note)
    if [ "$got_rc" = "$want_rc" ] && [ "$got_note" = "$want_note" ]; then
        ok "$name: STATUS rc=$got_rc note=$got_note"
    else bad "$name" "wanted rc=$want_rc note=$want_note, got rc=${got_rc:-<none>} note=${got_note:-<none>}"; fi
done

echo "-- cap expiry is DISTINGUISHABLE from a crash (rc=124, not 0, not 143)"
d=$(mkcase expiry); mksolver fakeFoam "sleep 30"
bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 1 --solver fakeFoam --foam-bashrc none --no-detach >/dev/null 2>&1
st="$W/runs/STATUS.expiry"
[ "$(read_status "$st" rc)" = "124" ] && ok "expiry: rc=124 note=$(read_status "$st" note)" \
    || bad "expiry" "got rc=$(read_status "$st" rc)"

echo "-- THE SETSID TRAP: DETACHED, a crashing solver must still record rc=7"
d=$(mkcase detached); mksolver fakeFoam "exit 7"
bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none >/dev/null 2>&1
st="$W/runs/STATUS.detached"
for _ in 1 2 3 4 5 6 7 8 9 10; do [ -f "$st" ] && break; sleep 0.5; done
got=$(read_status "$st" rc)
[ "$got" = "7" ] && ok "detached: STATUS rc=7 -- setsid did NOT swallow it" \
    || bad "detached" "got rc=${got:-<none>}; a bare 'setsid ... ; \$?' returns 0 here"

echo "-- the DETACHED run really was detached (new session id)"
d=$(mkcase session); mksolver fakeFoam 'ps -o sid= -p $$ > "$OLDPWD/sid.child" 2>/dev/null; exit 0'
( cd "$W" && bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none >/dev/null 2>&1 )
for _ in 1 2 3 4 5 6 7 8 9 10; do [ -f "$W/runs/STATUS.session" ] && break; sleep 0.5; done
mysid=$(ps -o sid= -p $$ | tr -d ' ')
csid=$(tr -d ' ' < "$W/sid.child" 2>/dev/null || echo "")
[ -n "$csid" ] && [ "$csid" != "$mysid" ] && ok "detached: child session $csid != this shell's $mysid" \
    || bad "detach" "child sid=${csid:-<unread>} this=$mysid"

echo "-- a PRE-FLIGHT refusal writes NO STATUS (nothing ran, so there is no rc)"
d=$(mkcase preflight); mv "$d/0/nut" "$d/0/nut.HIDDEN"; mksolver fakeFoam "exit 0"
bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none --no-detach >/dev/null 2>&1
rc=$?
[ ! -f "$W/runs/STATUS.preflight" ] && [ "$rc" = "2" ] \
    && ok "pre-flight: refused rc=2 and wrote NO STATUS" \
    || bad "pre-flight" "rc=$rc, STATUS exists=$([ -f "$W/runs/STATUS.preflight" ] && echo yes || echo no)"

echo "-- a MISSING 0/T refuses: the age guard would have no datum"
d=$(mkcase noT); rm -f "$d/0/T"; mksolver fakeFoam "exit 0"
bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --foam-bashrc none --no-detach >/dev/null 2>&1
[ "$?" = "2" ] && ok "no 0/T: refused rc=2" || bad "no 0/T" "did not refuse"

echo "-- ranks != 1 refuses (K0f is registered SERIAL)"
d=$(mkcase ranks); mksolver fakeFoam "exit 0"
bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 30 --ranks 4 --solver fakeFoam --no-detach >/dev/null 2>&1
[ "$?" = "2" ] && ok "ranks=4: refused rc=2" || bad "ranks=4" "did not refuse"


echo "-- NEGATIVE CONTROL: THE REAL SOLVER, ON THE REAL PATH, WITH NO FIXTURE --"
# THE ARM THAT WOULD HAVE CAUGHT K0f ATTEMPT 1 (seven cases, rc=127, wall=0).
# Every arm above installs a FAKE SOLVER ON PATH.  They prove the rc plumbing
# and they say NOTHING about whether this launcher can reach a real solver in a
# real environment -- A LAUNCHER SELFTEST THAT SUPPLIES ITS OWN FIXTURES IS
# TESTING THE LAUNCHER AGAINST ITSELF.  This arm supplies nothing.
REAL_SOLVER="buoyantBoussinesqSimpleFoam"
REAL_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
if [ -f "$REAL_BASHRC" ]; then
    rp=$( set +u; . "$REAL_BASHRC" >/dev/null 2>&1; command -v "$REAL_SOLVER" 2>/dev/null )
    [ -n "$rp" ] && ok "the REAL solver resolves after sourcing the REAL environment   [$rp]" \
        || bad "real solver" "sourcing $REAL_BASHRC did not put $REAL_SOLVER on PATH"
    # and the launcher itself must reach it: --no-detach, cap 0 is rejected, so
    # use a 1 s cap and accept ANY rc -- what is under test is that the solver
    # was FOUND, i.e. that rc is NOT 127 and STATUS records a solver_path.
    d=$(mkcase realenv)
    bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 1 --solver "$REAL_SOLVER" --no-detach >/dev/null 2>&1
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
bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 30 --solver definitelyNotASolver_k0f \
     --foam-bashrc none --no-detach >/dev/null 2>&1
rc=$?
[ "$rc" = "2" ] && [ ! -f "$W/runs/STATUS.unreachable" ] \
    && ok "unresolvable solver: refused rc=2 and wrote NO STATUS (never started != ran and failed)" \
    || bad "unreachable" "rc=$rc, STATUS exists=$([ -f "$W/runs/STATUS.unreachable" ] && echo yes || echo no)"

echo "-- and a MISSING environment file REFUSES rather than launching blind --"
d=$(mkcase noenv); mksolver fakeFoam "exit 0"
bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 30 --solver fakeFoam \
     --foam-bashrc /nonexistent/etc/bashrc --no-detach >/dev/null 2>&1
[ "$?" = "2" ] && ok "absent --foam-bashrc: refused rc=2" || bad "absent bashrc" "did not refuse"

echo "=========================================================================="
echo "  $PASS passed, $FAIL failed"
echo "=========================================================================="
[ "$FAIL" = "0" ] || exit 1
