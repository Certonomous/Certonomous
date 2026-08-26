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
    bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --no-detach >/dev/null 2>&1
    st="$W/runs/STATUS.$name"
    got_rc=$(read_status "$st" rc); got_note=$(read_status "$st" note)
    if [ "$got_rc" = "$want_rc" ] && [ "$got_note" = "$want_note" ]; then
        ok "$name: STATUS rc=$got_rc note=$got_note"
    else bad "$name" "wanted rc=$want_rc note=$want_note, got rc=${got_rc:-<none>} note=${got_note:-<none>}"; fi
done

echo "-- cap expiry is DISTINGUISHABLE from a crash (rc=124, not 0, not 143)"
d=$(mkcase expiry); mksolver fakeFoam "sleep 30"
bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 1 --solver fakeFoam --no-detach >/dev/null 2>&1
st="$W/runs/STATUS.expiry"
[ "$(read_status "$st" rc)" = "124" ] && ok "expiry: rc=124 note=$(read_status "$st" note)" \
    || bad "expiry" "got rc=$(read_status "$st" rc)"

echo "-- THE SETSID TRAP: DETACHED, a crashing solver must still record rc=7"
d=$(mkcase detached); mksolver fakeFoam "exit 7"
bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 30 --solver fakeFoam >/dev/null 2>&1
st="$W/runs/STATUS.detached"
for _ in 1 2 3 4 5 6 7 8 9 10; do [ -f "$st" ] && break; sleep 0.5; done
got=$(read_status "$st" rc)
[ "$got" = "7" ] && ok "detached: STATUS rc=7 -- setsid did NOT swallow it" \
    || bad "detached" "got rc=${got:-<none>}; a bare 'setsid ... ; \$?' returns 0 here"

echo "-- the DETACHED run really was detached (new session id)"
d=$(mkcase session); mksolver fakeFoam 'ps -o sid= -p $$ > "$OLDPWD/sid.child" 2>/dev/null; exit 0'
( cd "$W" && bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 30 --solver fakeFoam >/dev/null 2>&1 )
for _ in 1 2 3 4 5 6 7 8 9 10; do [ -f "$W/runs/STATUS.session" ] && break; sleep 0.5; done
mysid=$(ps -o sid= -p $$ | tr -d ' ')
csid=$(tr -d ' ' < "$W/sid.child" 2>/dev/null || echo "")
[ -n "$csid" ] && [ "$csid" != "$mysid" ] && ok "detached: child session $csid != this shell's $mysid" \
    || bad "detach" "child sid=${csid:-<unread>} this=$mysid"

echo "-- a PRE-FLIGHT refusal writes NO STATUS (nothing ran, so there is no rc)"
d=$(mkcase preflight); mv "$d/0/nut" "$d/0/nut.HIDDEN"; mksolver fakeFoam "exit 0"
bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --no-detach >/dev/null 2>&1
rc=$?
[ ! -f "$W/runs/STATUS.preflight" ] && [ "$rc" = "2" ] \
    && ok "pre-flight: refused rc=2 and wrote NO STATUS" \
    || bad "pre-flight" "rc=$rc, STATUS exists=$([ -f "$W/runs/STATUS.preflight" ] && echo yes || echo no)"

echo "-- a MISSING 0/T refuses: the age guard would have no datum"
d=$(mkcase noT); rm -f "$d/0/T"; mksolver fakeFoam "exit 0"
bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 30 --solver fakeFoam --no-detach >/dev/null 2>&1
[ "$?" = "2" ] && ok "no 0/T: refused rc=2" || bad "no 0/T" "did not refuse"

echo "-- ranks != 1 refuses (K0f is registered SERIAL)"
d=$(mkcase ranks); mksolver fakeFoam "exit 0"
bash "$SELF/launch_k0f.sh" --case-dir "$d" --timeout 30 --ranks 4 --solver fakeFoam --no-detach >/dev/null 2>&1
[ "$?" = "2" ] && ok "ranks=4: refused rc=2" || bad "ranks=4" "did not refuse"

echo "=========================================================================="
echo "  $PASS passed, $FAIL failed"
echo "=========================================================================="
[ "$FAIL" = "0" ] || exit 1
