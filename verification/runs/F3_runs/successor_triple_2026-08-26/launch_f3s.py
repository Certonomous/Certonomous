#!/usr/bin/env python3
"""
F3 SUCCESSOR -- THE LAUNCHER. Eight runs, serial, cap checked INCREMENTALLY.

Authorised by cfd-supervisor 2026-08-26 against the pre-registration frozen at
5891db27. Compute itself is pre-authorised under CLAUDE.md rule 12 (this rung is
$0.0151 derived, far under the $25 per-run ceiling Sanaa set on 2026-08-21).

WHAT THIS LAUNCHER WILL NOT DO
  * It will not total the cap only at the end. That is F4's defect -- a post-hoc
    audit wearing a guard's name -- and this rung partly exists to not repeat it.
    The cap is checked BEFORE and AFTER every run: sixteen evaluations for eight
    runs, one of them before any compute at all.
  * It will not swallow a non-zero rc. Every run writes its own RC.txt.
  * It will not take a load figure from a message. It measures the box itself,
    in its own invocation, from /proc/stat -- never loadavg, which read 10-15 on
    this box tonight while true utilisation was 19%.
  * It will not grade. Grading happens separately, after all eight have landed
    and the completion rule has been applied to each.
"""
import os
import re
import sys
import json
import time
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/ubuntu/Certonomous"
RUNS = os.path.join(HERE, "runs")
PREREG_COMMIT = "5891db27"

CAP_CORE_S = 1059.24                 # frozen Annex B: 17.6541 core-min
RANKS = 1

# (tag, family, pair, level, per-run cap core-s, instrumented)
# CONTROL ARMS FIRST, deliberately: the bit-identity control gates the whole
# rung, so if it fails we stop having spent ~340 core-s instead of ~880.
ORDER = [
    ("armA_M3.0_th15_fine_UNINSTRUMENTED", "wedge", "M3.0_th15", "fine", 201.87, False),
    ("armB_M3.0_th15_fine_INSTRUMENTED",   "wedge", "M3.0_th15", "fine", 232.14, True),
    ("wedge_M2.5_th10_coarse",   "wedge",   "M2.5_th10", "coarse",   9.50, True),
    ("wedge_M2.5_th10_medium",   "wedge",   "M2.5_th10", "medium",  29.45, True),
    ("wedge_M2.5_th10_fine",     "wedge",   "M2.5_th10", "fine",   230.74, True),
    ("diamond_M2.5_eps5_coarse", "diamond", "M2.5_eps5", "coarse",  14.18, True),
    ("diamond_M2.5_eps5_medium", "diamond", "M2.5_eps5", "medium",  45.65, True),
    ("diamond_M2.5_eps5_fine",   "diamond", "M2.5_eps5", "fine",   295.71, True),
]

# F3's recorded values for the control case. Bit-identity, not "close".
F3_RECORD = dict(p_wall_mean=2.821769172727273, beta_deg=31.931111435642887)


def log(msg):
    line = "[%s] %s" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg)
    print(line, flush=True)
    with open(os.path.join(HERE, "LAUNCH_LOG.txt"), "a") as f:
        f.write(line + "\n")


def cpu_busy_pct(window=3.0):
    """Measured HERE, in this invocation. /proc/stat delta, never loadavg."""
    def snap():
        with open("/proc/stat") as f:
            p = f.readline().split()[1:]
        v = [float(x) for x in p]
        return sum(v), v[3] + (v[4] if len(v) > 4 else 0.0)   # total, idle+iowait
    t0, i0 = snap()
    time.sleep(window)
    t1, i1 = snap()
    dt, di = t1 - t0, i1 - i0
    return 100.0 * (1.0 - di / dt) if dt > 0 else float("nan")


def clocktime_from_log(path):
    """ClockTime, NEVER ExecutionTime: the latter excludes startup, meshing and
    sampling. Substituting it moved an F6d calibration ratio across 1.0 tonight,
    in the flattering direction."""
    if not os.path.exists(path):
        return None
    last = None
    for m in re.finditer(r"ClockTime = (\d+(?:\.\d+)?) s",
                         open(path, errors="replace").read()):
        last = float(m.group(1))
    return last


def main():
    os.makedirs(RUNS, exist_ok=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                          stdout=subprocess.PIPE).stdout.decode().strip()
    busy = cpu_busy_pct()
    launch = dict(utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                  head=head, prereg_commit=PREREG_COMMIT,
                  cpu_busy_pct_measured_here=round(busy, 2),
                  method="/proc/stat delta over 3.0 s (NOT loadavg)",
                  cap_core_s=CAP_CORE_S, ranks=RANKS, n_runs=len(ORDER))
    json.dump(launch, open(os.path.join(HERE, "LAUNCH_LOAD.txt"), "w"), indent=2)
    open(os.path.join(HERE, "LAUNCH_HEAD.txt"), "w").write(head + "\n")
    log("LAUNCH head=%s prereg=%s cpu_busy=%.2f%% cap=%.2f core-s"
        % (head[:8], PREREG_COMMIT, busy, CAP_CORE_S))

    ledger = dict(cap_core_s=CAP_CORE_S, prereg_commit=PREREG_COMMIT,
                  launch=launch, runs={}, stopped_by=None, spent_core_s=0.0)
    spent = 0.0

    for tag, fam, pair, lvl, pcap, inst in ORDER:
        # ---- ENFORCEMENT POINT 1: BEFORE the run --------------------------
        if spent + pcap > CAP_CORE_S:
            ledger["stopped_by"] = ("cap check BEFORE %s: %.2f spent + %.2f "
                                    "predicted > %.2f cap" % (tag, spent, pcap, CAP_CORE_S))
            ledger["runs"][tag] = dict(status="PENDING", reason=ledger["stopped_by"])
            log("HALT (before %s): %s" % (tag, ledger["stopped_by"]))
            break

        case_dir = os.path.join(RUNS, fam, pair, lvl) if "arm" not in tag \
            else os.path.join(RUNS, "_control", tag)
        log("START %s -> %s (per-run cap %.2f core-s)" % (tag, case_dir, pcap))
        t0 = time.time()
        p = subprocess.run(
            [sys.executable, os.path.join(HERE, "run_f3s.py"), case_dir, fam, pair, lvl]
            + ([] if inst else ["uninstrumented"]),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        wall = time.time() - t0
        core_s = wall * RANKS

        os.makedirs(case_dir, exist_ok=True)
        open(os.path.join(case_dir, "RC.txt"), "w").write("%d\n" % p.returncode)
        open(os.path.join(case_dir, "runner_stdout.txt"), "wb").write(p.stdout)

        spent += core_s
        ledger["spent_core_s"] = round(spent, 2)
        entry = dict(status="OK" if p.returncode == 0 else "FAILED",
                     rc=p.returncode, predicted_core_s=pcap,
                     actual_core_s=round(core_s, 2),
                     clocktime_s=clocktime_from_log(os.path.join(case_dir, "log.rhoCentralFoam")),
                     cumulative_core_s=round(spent, 2), case_dir=case_dir)
        ledger["runs"][tag] = entry
        json.dump(ledger, open(os.path.join(HERE, "RUN_LEDGER.json"), "w"), indent=2)
        log("DONE  %s rc=%d actual=%.2f core-s (pred %.2f) ClockTime=%s cumulative=%.2f/%.2f"
            % (tag, p.returncode, core_s, pcap, entry["clocktime_s"], spent, CAP_CORE_S))

        if p.returncode != 0:
            ledger["stopped_by"] = "%s returned rc=%d" % (tag, p.returncode)
            log("HALT: %s. A non-zero rc is visible, not swallowed. tail:\n%s"
                % (ledger["stopped_by"], p.stdout.decode(errors="replace")[-600:]))
            break

        # ---- ENFORCEMENT POINT 2: AFTER the run ---------------------------
        if spent > CAP_CORE_S:
            ledger["stopped_by"] = ("cap check AFTER %s: %.2f spent > %.2f cap"
                                    % (tag, spent, CAP_CORE_S))
            log("HALT (after %s): %s" % (tag, ledger["stopped_by"]))
            break

        # ---- the bit-identity control, evaluated the moment arm B lands ----
        if tag.startswith("armB"):
            verdict = bit_identity(ledger)
            ledger["bit_identity"] = verdict
            json.dump(ledger, open(os.path.join(HERE, "RUN_LEDGER.json"), "w"), indent=2)
            log("BIT-IDENTITY: %s -- %s" % (verdict["verdict"], verdict["why"]))
            if verdict["verdict"] != "PROCEED":
                ledger["stopped_by"] = "bit-identity control: " + verdict["why"]
                break

    ledger["cap_respected"] = spent <= CAP_CORE_S
    ledger["spent_core_min"] = round(spent / 60.0, 4)
    json.dump(ledger, open(os.path.join(HERE, "RUN_LEDGER.json"), "w"), indent=2)
    log("END spent=%.2f core-s = %.4f core-min; cap_respected=%s; stopped_by=%s"
        % (spent, spent / 60.0, ledger["cap_respected"], ledger["stopped_by"]))
    return 0


def bit_identity(ledger):
    """Two arms. A single arm would confound 'instrumentation perturbs the solve'
    with 'the solver is not bit-reproducible across re-runs'."""
    def load(tag):
        cd = ledger["runs"].get(tag, {}).get("case_dir")
        rj = os.path.join(cd, "result.json") if cd else None
        return json.load(open(rj)) if rj and os.path.exists(rj) else None
    A = load("armA_M3.0_th15_fine_UNINSTRUMENTED")
    B = load("armB_M3.0_th15_fine_INSTRUMENTED")
    if A is None or B is None:
        return dict(verdict="STOP", why="a control arm produced no result.json")
    out = dict(armA={k: A.get(k) for k in ("p_wall_mean", "beta_computed_deg")},
               armB={k: B.get(k) for k in ("p_wall_mean", "beta_computed_deg")},
               f3_record=F3_RECORD)
    a_ok = (A.get("p_wall_mean") == F3_RECORD["p_wall_mean"]
            and A.get("beta_computed_deg") == F3_RECORD["beta_deg"])
    b_ok = (B.get("p_wall_mean") == A.get("p_wall_mean")
            and B.get("beta_computed_deg") == A.get("beta_computed_deg"))
    if not a_ok:
        out.update(verdict="STOP",
                   why=("arm A does not reproduce F3's recorded values, so this "
                        "case is not bit-reproducible across re-runs on this box "
                        "and build. The control cannot attribute anything: it "
                        "cannot separate instrumentation from non-reproducibility."))
    elif not b_ok:
        out.update(verdict="STOP",
                   why=("arm A reproduces F3 exactly but arm B differs from arm A: "
                        "THE INSTRUMENTATION CHANGED THE EXPERIMENT."))
    else:
        out.update(verdict="PROCEED",
                   why=("arm A == F3's record and arm B == arm A, bitwise. "
                        "Instrumentation is an observation, not an intervention."))
    return out


if __name__ == "__main__":
    sys.exit(main())
