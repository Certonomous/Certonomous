#!/bin/bash
# SUBOFF A1h -- L1M SWEEP -- DETACHED LANDING GRADER.
#
# WHY IT LIVES HERE AND WHY ITS NAME IS FROZEN FOR ITS LIFE.
#   A running bash script that is UNLINKED survives (bash holds it on fd 255), but a
#   script OVERWRITTEN IN PLACE is fatal: bash re-reads lazily by byte offset and will
#   execute whatever bytes now sit at its saved offset.  Measured on this box tonight.
#   So: this file sits under the run tree, not in a scratchpad that is wiped, and
#   nothing may rewrite this path while it runs.  A change means a NEW filename.
#
# rc IS CAPTURED INSIDE THIS WRAPPER.  `setsid timeout cmd` exits 0 for every outcome,
# so an rc taken around the setsid line is always a lie.  This script IS the thing
# setsid launches and it writes every rc it sees to disk.
#
# IT GRADES; IT DOES NOT DECIDE.  The sole verdict comes from the frozen comparator
# named in the pre-registration 8; this wrapper waits, verifies that comparator against
# its committed blob, runs it, and files what it printed.  It invents no gate and it
# writes nothing into the seven cases.
set +u
REPO=/home/ubuntu/Certonomous
SWEEP=$REPO/verification/runs/navier_class/SUBOFF_A1H_DRIFT/L1M_SWEEP
OUTD=$REPO/verification/runs/navier_class/SUBOFF_A1H_DRIFT/L1M_GRADE
CMP=$REPO/cases/navier_class/SUBOFF_A1/grade_suboff_a1h.py
CMP_FROZEN_BLOB=13ac40d3746d9e22716a9bddb4714a8f19a0d4d6   # HEAD blob at 79b4de868
POINTS="BETA_m12 BETA_m08 BETA_m04 BETA_p00 BETA_p04 BETA_p08 BETA_p12"
LOG=$OUTD/LANDING.log
JSON=$OUTD/A1H_L1M_GRADE.json
WM=$OUTD/WINDOW_MEANS_REPORTED.json
DEADLINE=$(( $(date +%s) + 8*3600 ))

say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$LOG"; }

say "WATCHER START pid=$$ ppid=$PPID sweep=$SWEEP"
say "NOTE this wrapper is read-only on the seven cases and stops nothing (directive #17)"

# ---- 1. WAIT FOR ALL SEVEN TO LAND ------------------------------------------
# solve_a1h.sh writes solve_rc on EVERY exit path, after reconstructPar.  Waiting on
# the file rather than on a pid is deliberate: a pid check would go blind the moment
# the pid is recycled, and `pkill -f`-style pattern matching is banned on this box.
while :; do
  MISSING=""
  for p in $POINTS; do [ -f "$SWEEP/$p/solve_rc" ] || MISSING="$MISSING $p"; done
  if [ -z "$MISSING" ]; then say "ALL SEVEN HAVE solve_rc"; break; fi
  if [ "$(date +%s)" -ge "$DEADLINE" ]; then
    say "DEADLINE REACHED with points still unlanded:$MISSING -- grading anyway; the"
    say "comparator labels an unlanded point itself.  NOTHING WAS STOPPED."
    break
  fi
  sleep 60
done
say "settling 120 s so reconstructPar mtimes are stable"
sleep 120
for p in $POINTS; do
  say "  $p solve_rc=$(cat "$SWEEP/$p/solve_rc" 2>/dev/null || echo ABSENT) lastTime=$(tac "$SWEEP/$p/log.simpleFoam" 2>/dev/null | grep -m1 -E '^Time = ' || echo NONE)"
done

# ---- 2. RULE 2 -- THE FROZEN FILE MUST *BE* THE FILE THAT RAN -----------------
NOW_BLOB=$(cd "$REPO" && git hash-object "$CMP" 2>/dev/null)
say "comparator blob now=$NOW_BLOB frozen=$CMP_FROZEN_BLOB"
if [ "$NOW_BLOB" != "$CMP_FROZEN_BLOB" ]; then
  say "BLOCKED: the comparator on disk is NOT the blob frozen at the pre-registration"
  say "commit.  Rule 2.  No grade is produced and none may be believed."
  echo "BLOCKED comparator_blob_mismatch now=$NOW_BLOB frozen=$CMP_FROZEN_BLOB" > "$OUTD/LANDING.txt"
  echo "2" > "$OUTD/A1H_L1M_GRADE.rc"
  exit 2
fi

# ---- 3. THE FROZEN COMPARATOR.  rc CAPTURED HERE, INSIDE. --------------------
rm -rf "$OUTD/scratch"; mkdir -p "$OUTD/scratch"
python3 "$CMP" --run-root "$SWEEP" --scratch "$OUTD/scratch" --out "$JSON" \
        --end-time 3000 > "$OUTD/A1H_L1M_GRADE.stdout" 2> "$OUTD/A1H_L1M_GRADE.stderr"
RC=$?; echo "$RC" > "$OUTD/A1H_L1M_GRADE.rc"; say "comparator rc=$RC"

# ---- 4. REPORTED, NOT GRADED: the window means over the registered window -----
python3 "$OUTD/report_window_means.py" "$SWEEP" "$OUTD/scratch" "$WM" \
        > "$OUTD/WINDOW_MEANS.stdout" 2> "$OUTD/WINDOW_MEANS.stderr"
WRC=$?; echo "$WRC" > "$OUTD/WINDOW_MEANS.rc"; say "window-mean reader rc=$WRC"

# ---- 5. THE LANDING FILE.  Numbers and the comparator's own label, nothing added.
python3 - "$JSON" "$WM" "$RC" "$WRC" > "$OUTD/LANDING.txt" 2>> "$LOG" <<'PY'
import json, sys
j, w, rc, wrc = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
P = print
P("SUBOFF A1h -- L1M SWEEP -- LANDING RECORD")
P("prereg  verification/campaign/SUBOFF_A1h_FULL_DOMAIN_DRIFT_SWEEP_PREREGISTRATION.md")
P("grader  cases/navier_class/SUBOFF_A1/grade_suboff_a1h.py (prereg 8, frozen)")
P("comparator rc = %s   window-mean reader rc = %s" % (rc, wrc))
P("")
P("REGISTERED-PATH LIMB, STATED NOT HIDDEN: prereg 9 registers the seven points at")
P("  verification/runs/navier_class/SUBOFF_A1H_DRIFT/BETA_*  and says the comparator")
P("  'takes these seven paths and no others'.  These solves ran one level down, in")
P("  L1M_SWEEP/BETA_*, on MESH_FULL_L1M.  Addendum 1 records that the mirrored L1 mesh")
P("  carries A1b's refused determinant 8.6227045e-04 against a floor of 1.0e-03.")
P("  Both limbs are for the supervisor to weigh; this file only states them.")
P("")
try:
    d = json.load(open(j))
except Exception as e:
    P("NO COMPARATOR JSON: %s" % e); raise SystemExit(0)
P("COMPARATOR VERDICT: %s" % d.get("verdict", "(absent)"))
P("REASON: %s" % d.get("reason", "(absent)"))
P("")
P("STRICT COMPLETION (standing rule 4), per point:")
for b in ("-12","-8","-4","0","4","8","12"):
    c = d.get("completion", {}).get(b, {})
    P("  beta=%4s ok=%s rc=%s end_line=%s last==endTime=%s exec_count=%s fields=%s age_guard=%s last_Time=%s missing=%s"
      % (b, c.get("ok"), c.get("rc"), c.get("clause_end_line"),
         c.get("clause_last_eq_endTime"), c.get("clause_exec_count"),
         c.get("clause_fields"), c.get("clause_age_guard"), c.get("last_Time"),
         c.get("fields_missing")))
P("")
P("PER POINT at endTime (prereg 4.1), and the plateau over the registered 500-window:")
for b in ("-12","-8","-4","0","4","8","12"):
    p = d.get("points", {}).get(b, {})
    pl = p.get("plateau", {})
    P("  beta=%4s F_z=%s M_y=%s Y'=%s N'=%s hull_F_z=%s sail_F_z=%s plateau=%s drift=%s ceiling=%s"
      % (b, p.get("F_z_mesh"), p.get("M_y_mesh"), p.get("Yp"), p.get("Np"),
         p.get("F_z_hull"), p.get("F_z_sail"), pl.get("verdict"), pl.get("drift"),
         pl.get("ceiling")))
P("")
P("FIT over |beta| <= 8 (five points), prereg 5:")
P("  Y_v' = %s   band %s   Roddy(EXPERIMENT) %s   %s%% of Roddy"
  % (d.get("Y_v_prime"), d.get("band"), d.get("roddy_Y_v_prime_EXPERIMENT"),
     d.get("Y_v_prime_pct_of_roddy")))
P("  N_v' = %s   REPORTED NOT GRADED   Roddy(EXPERIMENT) %s"
  % (d.get("N_v_prime"), d.get("roddy_N_v_prime_EXPERIMENT")))
P("  beta=0 symmetry: Y'=%s N'=%s (ceiling 1e-4, prereg 4.3)"
  % (d.get("symmetry_Yp_at_beta0"), d.get("symmetry_Np_at_beta0")))
P("  NEUTRAL POINT: not registered by this act.  Prereg 10: 'no Z, no M, no neutral")
P("  point -- that is A1g's, on a body this one does not have.'  None is computed.")
P("")
P("REPORTED, NOT GRADED -- window means over the registered final-500 window:")
try:
    ww = json.load(open(w))
    P("  rule-3 plant: %s" % ww.get("rule3_plant"))
    for b in ("-12","-8","-4","0","4","8","12"):
        r = ww.get("points", {}).get(b, {})
        P("  beta=%4s mean F_z=%s mean M_y=%s mean hull F_z=%s mean sail F_z=%s Y'(mean)=%s N'(mean)=%s"
          % (b, r.get("F_z_total_mesh", {}).get("mean"),
             r.get("M_y_total_mesh", {}).get("mean"),
             r.get("F_z_hull_mesh", {}).get("mean"),
             r.get("F_z_sail_mesh", {}).get("mean"),
             r.get("Y_prime_from_window_mean_REPORTED"),
             r.get("N_prime_from_window_mean_REPORTED")))
except Exception as e:
    P("  window means unavailable: %s" % e)
PY
say "LANDING WRITTEN $OUTD/LANDING.txt"
say "WATCHER END"
exit 0
