#!/usr/bin/env python3
"""Render the frozen comparator's JSON as the landing record.  It ADDS NO JUDGEMENT:
every label printed is copied from the comparator, which is the only grading path."""
import json, sys
j, w, rc, wrc = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
P = print
P("SUBOFF A1h -- L1M SWEEP -- LANDING RECORD")
P("prereg  verification/campaign/SUBOFF_A1h_FULL_DOMAIN_DRIFT_SWEEP_PREREGISTRATION.md")
P("grader  cases/navier_class/SUBOFF_A1/grade_suboff_a1h.py (prereg 8, frozen 79b4de868,")
P("        blob 13ac40d3746d9e22716a9bddb4714a8f19a0d4d6 -- verified before it ran)")
P("comparator rc = %s   window-mean reader rc = %s" % (rc, wrc))
P("")
P("TWO LIMBS STATED, NOT HIDDEN, AND NEITHER IS THIS FILE'S TO WEIGH:")
P("  (1) prereg 9 registers the seven points at .../SUBOFF_A1H_DRIFT/BETA_* and says the")
P("      comparator 'takes these seven paths and no others'. These solves ran one level")
P("      down, in L1M_SWEEP/BETA_*.")
P("  (2) they ran on MESH_FULL_L1M. Addendum 1 records the mirrored L1 determinant as")
P("      8.6227045e-04 against A1b's floor of 1.0e-03, and that mirrorMesh preserved it.")
P("")
try:
    d = json.load(open(j))
except Exception as e:
    P("NO COMPARATOR JSON: %s" % e); raise SystemExit(0)
P("COMPARATOR VERDICT: %s" % d.get("verdict", "(absent)"))
P("REASON: %s" % d.get("reason", "(absent)"))
P("")
P("STRICT COMPLETION (standing rule 4), per point, every channel:")
for b in ("-12","-8","-4","0","4","8","12"):
    c = d.get("completion", {}).get(b, {})
    P("  beta=%4s ok=%s rc=%s End_line=%s last==endTime=%s exec_count=%s fields=%s age_guard=%s last_Time=%s missing=%s"
      % (b, c.get("ok"), c.get("rc"), c.get("clause_end_line"), c.get("clause_last_eq_endTime"),
         c.get("clause_exec_count"), c.get("clause_fields"), c.get("clause_age_guard"),
         c.get("last_Time"), c.get("fields_missing")))
P("")
P("PER POINT at endTime (prereg 4.1) and the plateau over the registered 500-window:")
for b in ("-12","-8","-4","0","4","8","12"):
    p = d.get("points", {}).get(b, {}); pl = p.get("plateau", {})
    P("  beta=%4s %s F_z=%s M_y=%s Y'=%s N'=%s hull_F_z=%s sail_F_z=%s plateau=%s drift=%s ceiling=%s"
      % (b, p.get("status",""), p.get("F_z_mesh"), p.get("M_y_mesh"), p.get("Yp"), p.get("Np"),
         p.get("F_z_hull"), p.get("F_z_sail"), pl.get("verdict"), pl.get("drift"), pl.get("ceiling")))
P("")
P("FIT over |beta| <= 8 (five points), prereg 5:")
P("  Y_v' = %s   band %s   Roddy(EXPERIMENT) %s   %s %% of Roddy"
  % (d.get("Y_v_prime"), d.get("band"), d.get("roddy_Y_v_prime_EXPERIMENT"), d.get("Y_v_prime_pct_of_roddy")))
P("  N_v' = %s   REPORTED NOT GRADED   Roddy(EXPERIMENT) %s"
  % (d.get("N_v_prime"), d.get("roddy_N_v_prime_EXPERIMENT")))
P("  beta=0 symmetry: Y'=%s N'=%s (ceiling 1e-4, prereg 4.3)"
  % (d.get("symmetry_Yp_at_beta0"), d.get("symmetry_Np_at_beta0")))
P("  NEUTRAL POINT: none. Prereg 10: 'no Z, no M, no neutral point -- that is A1g's, on a")
P("  body this one does not have.' The act does not register one and none is computed.")
P("")
P("REPORTED, NOT GRADED -- window means over the registered final-500 window:")
try:
    ww = json.load(open(w))
    P("  rule-3 plant: %s" % ww.get("rule3_plant"))
    for b in ("-12","-8","-4","0","4","8","12"):
        r = ww.get("points", {}).get(b, {})
        g = lambda k: (r.get(k) or {}).get("mean")
        P("  beta=%4s n=%s t_last=%s meanF_z=%s meanM_y=%s mean_hullF_z=%s mean_sailF_z=%s Y'(mean)=%s N'(mean)=%s"
          % (b, (r.get("F_z_total_mesh") or {}).get("n"), (r.get("F_z_total_mesh") or {}).get("t_last"),
             g("F_z_total_mesh"), g("M_y_total_mesh"), g("F_z_hull_mesh"), g("F_z_sail_mesh"),
             r.get("Y_prime_from_window_mean_REPORTED"), r.get("N_prime_from_window_mean_REPORTED")))
except Exception as e:
    P("  window means unavailable: %s" % e)
