#!/usr/bin/env python3
r"""CASE PROTOCOL -- STAGE 3 SMOKE.  Reusable; first instance SUBOFF.

AUTHORITY.  CASE_PROTOCOL_CHARTER v1.0 section 3, verbatim:
    "Coarsest level, a registered fraction of the iterations or time (typically 5 to 10
     percent), residual and force or temperature monitors on.  PREDICTIONS REGISTERED
     BEFORE IT STARTS: residual behavior, first-iteration cost, the sign and order of the
     graded quantity.  Exit condition: residuals falling, no bounds violated, monitors
     alive, cost per iteration within the estimate's band, predictions met.  PASS MEANS
     THE FULL RUN LAUNCHES AUTOMATICALLY.  Fail means ONE registered change from the
     escalation ladder for the failed prediction's class, then smoke again.  TWO failed
     smokes on the same cause: climb one rung (mesh, then numerics, then model).  THREE
     failures on the same cause: the case is parked as NOT A RESULT with the cause class
     and the three actions tried, the lesson is written, and the supervisor moves on."

THE PREDICTION FILE IS WRITTEN AND HASHED BEFORE THE SOLVER STARTS, and the hash is
re-verified after.  That freeze is the whole evidentiary content of a prediction: it
proves the prediction could not have been chosen to fit the answer (standing rule 2).
--predict writes it and REFUSES if it already exists; --run refuses if it does not.  The
two are separate invocations so no single process can both write and grade a prediction.

AUTO-LAUNCH IS OFF BY DEFAULT.  Section 3 says a pass launches the full run
automatically; --on-pass is how that is wired, and it is NOT supplied unless the
supervisor's check-4 (pre-registration committed before compute) has been done.  A script
that launches compute because a check went green has taken a decision reserved elsewhere.
"""
import argparse, glob, hashlib, json, os, re, subprocess, sys, time
from datetime import datetime, timezone

def sha256_text(t): return hashlib.sha256(t.encode()).hexdigest()
def utc(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def read_series(case, pattern, column_name):
    dats = sorted(glob.glob(os.path.join(case, pattern)))
    if not dats: return None, None
    dat = dats[-1]
    hdr, rows = None, []
    for l in open(dat, errors="replace"):
        if l.startswith("#"): hdr = l
        elif l.strip(): rows.append(l.split())
    if hdr is None: return dat, None
    cols = hdr.lstrip("#").split()
    ci = cols.index(column_name) if column_name in cols else 1
    return dat, [(float(r[0]), float(r[ci])) for r in rows if len(r) > ci]

def residual_series(case, field):
    logs = sorted(glob.glob(os.path.join(case, "log.*")))
    if not logs: return None
    txt = open(logs[-1], errors="replace").read()
    out = []
    for b in re.split(r"\nTime = ", txt)[1:]:
        m = re.match(r"(\d+)", b)
        h = re.findall(r"Solving for %s,\s*Initial residual\s*=\s*([-\d.eE+]+)" % field, b)
        if m and h:
            out.append((int(m.group(1)), float(h[0])))   # FIRST solve of the iteration:
    return out                                           # the one the SIMPLE loop tests

def cmd_predict(a, prof):
    if os.path.exists(a.predictions):
        sys.stderr.write("REFUSE: %s already exists; a prediction is written ONCE and is "
                         "never rewritten after a run exists\n" % a.predictions); return 2
    p = prof["smoke"]["predictions"]
    doc = dict(case=prof["case_id"], stage=3, written_utc=utc(),
               level=prof["smoke_level"], fraction=prof["smoke"]["fraction"],
               iterations=prof["smoke"]["iterations"], predictions=p,
               registered_before_any_smoke_solver_started=True)
    body = json.dumps(doc, indent=2, sort_keys=True)
    open(a.predictions, "w").write(body)
    open(a.predictions + ".sha256", "w").write(sha256_text(body) + "\n")
    print("STAGE 3 | PREDICT| REGISTERED   | %d prediction(s) frozen at %s | sha256 %s"
          % (len(p), a.predictions, sha256_text(body)[:16]))
    return 0

def cmd_run(a, prof):
    if not os.path.exists(a.predictions):
        sys.stderr.write("REFUSE: no frozen prediction file at %s -- section 3 requires "
                         "predictions registered BEFORE the smoke starts\n" % a.predictions)
        return 2
    body = open(a.predictions).read()
    want = open(a.predictions + ".sha256").read().strip()
    if sha256_text(body) != want:
        sys.stderr.write("REFUSE: prediction file has been edited since it was frozen "
                         "(sha256 %s != %s)\n" % (sha256_text(body)[:16], want[:16])); return 2
    doc = json.loads(body); preds = doc["predictions"]
    case = a.smoke_case
    t0 = time.time()
    ran = None
    if not a.no_launch:
        env = os.environ.copy()
        rc = prof.get("solver", {}).get("bashrc")
        if rc:
            q = subprocess.run(["bash", "-c", ". %s >/dev/null 2>&1 && env -0" % rc],
                               capture_output=True, text=True, timeout=120)
            if q.returncode == 0:
                env = {k: v for k, v in (kv.split("=", 1) for kv in q.stdout.split("\0") if "=" in kv)}
        log = os.path.join(case, "log.smoke")
        with open(log, "w") as lf:
            p = subprocess.run([prof["solver"]["binary"], "-case", case], stdout=lf,
                               stderr=subprocess.STDOUT, env=env,
                               timeout=prof["smoke"].get("timeout_s", 3600))
        ran = p.returncode            # rc FROM THE PROCESS
    wall = time.time() - t0

    res = residual_series(case, prof["smoke"].get("residual_field", "p"))
    dat, ser = read_series(case, prof["smoke"]["series_glob"], prof["smoke"]["series_column"])
    n_it = prof["smoke"]["iterations"]
    checks = {}

    if res:
        half = len(res) // 2
        first = sum(v for _, v in res[:half]) / max(half, 1)
        last = sum(v for _, v in res[half:]) / max(len(res) - half, 1)
        checks["residuals_falling"] = dict(state="PASS" if last < first else "FAIL",
                                           first_half_mean=first, second_half_mean=last,
                                           ratio=last / first if first else None)
    else:
        checks["residuals_falling"] = dict(state="COULD-NOT-RUN", why="no residual series parsed")

    logs = sorted(glob.glob(os.path.join(case, "log.*")))
    if logs:
        txt = open(logs[-1], errors="replace").read()
        nb = len(re.findall(r"[Bb]ounding ", txt))
        checks["no_bounds_violated"] = dict(state="PASS" if nb <= preds.get("max_bounding_events", 0)
                                            else "FAIL", bounding_events=nb,
                                            allowed=preds.get("max_bounding_events", 0))
    if ser:
        v = ser[-1][1]
        sgn = preds.get("graded_sign")
        lo, hi = preds.get("graded_order_of_magnitude", [None, None])
        ok_sign = (sgn is None) or (v > 0 if sgn == "+" else v < 0)
        ok_mag = (lo is None) or (lo <= abs(v) <= hi)
        checks["graded_sign_and_order"] = dict(state="PASS" if (ok_sign and ok_mag) else "FAIL",
                                               value=v, predicted_sign=sgn,
                                               predicted_order=[lo, hi], artifact=dat)
    else:
        checks["graded_sign_and_order"] = dict(state="COULD-NOT-RUN", why="no graded series")

    per_it = wall / n_it if n_it else None
    band = preds.get("cost_per_iteration_s_band")
    if per_it is not None and band:
        checks["cost_per_iteration"] = dict(state="PASS" if band[0] <= per_it <= band[1] else "FAIL",
                                            measured_s=per_it, predicted_band_s=band,
                                            core_min=round(wall * prof.get("ranks", 1) / 60.0, 3))
    if ran is not None:
        checks["rc_from_process"] = dict(state="PASS" if ran == 0 else "FAIL", rc=ran,
                                         source="subprocess.CompletedProcess.returncode")

    states = [c["state"] for c in checks.values()]
    overall = ("COULD-NOT-RUN" if "COULD-NOT-RUN" in states else
               "FAIL" if "FAIL" in states else "PASS")
    failed = [k for k, c in checks.items() if c["state"] == "FAIL"]

    hist_p = a.history or os.path.join(case, "SMOKE_HISTORY.json")
    hist = json.load(open(hist_p)) if os.path.exists(hist_p) else []
    cause = prof["smoke"].get("cause_class_of", {}).get(failed[0], failed[0]) if failed else None
    hist.append(dict(utc=utc(), overall=overall, failed=failed, cause_class=cause,
                     action_taken=a.action_taken))
    json.dump(hist, open(hist_p, "w"), indent=2)
    same = [h for h in hist if h.get("cause_class") == cause and cause]

    if overall == "PASS":
        nxt = ("STAGE 4 LAUNCHES (section 3: 'pass means the full run launches automatically') "
               "-- this script does NOT launch it unless --on-pass is given, because launching "
               "compute is gated on the supervisor's check-4, not on a green check")
    elif len(same) == 1:
        nxt = ("ONE registered change from the escalation ladder for cause class '%s', then "
               "smoke again: %s" % (cause, prof["smoke"].get("ladder", {}).get(cause, "<no ladder registered for this class -- register one; a missing entry is 'class default, first use', it never waits>")))
    elif len(same) == 2:
        nxt = ("SECOND failure on cause class '%s': CLIMB ONE RUNG -- mesh, then numerics, "
               "then model -- register the successor and continue" % cause)
    else:
        nxt = ("THIRD failure on cause class '%s': PARK THE CASE AS **NOT A RESULT** with the "
               "cause class and the three actions tried (%s); write the lesson; move to the "
               "next case" % (cause, [h.get("action_taken") for h in same]))

    for k, c in checks.items():
        print("STAGE 3 | %-24s | %-13s | %s" % (k, c["state"],
              " ".join("%s=%s" % (x, y) for x, y in c.items() if x != "state")))
    print("STAGE 3 | EXIT | %-13s | %d failed, %d prior smoke(s) on cause '%s', %.1f s wall"
          % (overall, len(failed), len(same) - 1 if same else 0, cause, wall))
    print("STAGE 3 | NEXT | %s" % nxt)

    rep = dict(stage=3, case=prof["case_id"], overall=overall, checks=checks,
               failed=failed, cause_class=cause, smokes_on_this_cause=len(same),
               next_action=nxt, predictions_sha256=want, history=hist_p)
    if a.report: json.dump(rep, open(a.report, "w"), indent=2)
    if overall == "PASS" and a.on_pass:
        print("STAGE 3 | LAUNCH| auto-launching stage 4: %s" % a.on_pass)
        subprocess.Popen(["bash", a.on_pass], start_new_session=True)
    return 0 if overall == "PASS" else 1 if overall == "FAIL" else 2

def main():
    ap = argparse.ArgumentParser(description="CASE PROTOCOL stage 3 smoke")
    ap.add_argument("mode", choices=["predict", "run"])
    ap.add_argument("--profile", required=True)
    ap.add_argument("--predictions", required=True)
    ap.add_argument("--smoke-case")
    ap.add_argument("--history"); ap.add_argument("--report")
    ap.add_argument("--action-taken", default=None,
                    help="the ONE registered change applied before this smoke")
    ap.add_argument("--no-launch", action="store_true",
                    help="grade an already-run smoke case without starting a solver")
    ap.add_argument("--on-pass", help="stage-4 launcher to run on PASS; omit and nothing launches")
    a = ap.parse_args()
    prof = json.load(open(a.profile))
    if a.mode == "predict": return cmd_predict(a, prof)
    if not a.smoke_case:
        sys.stderr.write("REFUSE: --smoke-case is required for run\n"); return 2
    return cmd_run(a, prof)

if __name__ == "__main__":
    sys.exit(main())
