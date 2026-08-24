#!/usr/bin/env python3
"""
F3 CONVERSION — the launcher, frozen with the pre-registration.

Re-runs the F3 supersonic exact-theory matrix into FRESH case directories under
`conversion_2026-08-24/runs/`, using the 2026-07-28 case generators and runners
BYTE-UNCHANGED (`make_*_case.py`, `run_*_case.py` in the parent directory). This
file adds only three things the completion rule needs and those scripts do not
write: `meta.json` (the generator's own returned geometry), `run_rc.txt` (the
launcher's exit code) and a per-run timing record.

BUDGET (standing rule 12). The cap is HARD: 39.5 core-minutes. Two independent
stops enforce it and neither grants a new budget:
  * a per-run wall cap, and
  * a global watchdog that terminates every live run the moment the cumulative
    core-minute total reaches the cap.
A wave whose predicted cost does not fit the remaining budget with 20% headroom
is NOT LAUNCHED, and its rows grade PENDING.

At most 2 runs are live at once — well under the 4-rank ceiling — deliberately,
to hold memory-bandwidth contention down so the core-minute total stays near its
prediction.
"""
import os
import sys
import json
import time
import signal
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
F3_ROOT = os.path.dirname(HERE)
RUNS = os.path.join(HERE, "runs")
sys.path.insert(0, F3_ROOT)

CAP_CORE_MIN = 39.5
CAP_CORE_S = CAP_CORE_MIN * 60.0
MAX_CONCURRENT = 2
WAVE_HEADROOM = 1.20

# (family, pair, level, predicted core-s)  -- predictions are the 2026-07-28
# record's own measured per-run core-seconds, cited in the pre-registration.
PRED = {
    ("cone", "M2.35_th10", "coarse"): 16.3,
    ("cone", "M2.35_th10", "medium"): 118.9,
    ("cone", "M2.35_th10", "fine"): 1072.7,
    ("wedge", "M2.0_th15", "coarse"): 6.1,
    ("wedge", "M2.0_th15", "medium"): 18.7,
    ("wedge", "M2.0_th15", "fine"): 146.4,
    ("wedge", "M3.0_th15", "fine"): 149.0,
    ("wedge", "M2.5_th10", "fine"): 148.1,
    ("diamond", "M2.0_eps7p125", "coarse"): 11.1,
    ("diamond", "M2.0_eps7p125", "medium"): 35.5,
    ("diamond", "M2.0_eps7p125", "fine"): 201.2,
    ("diamond", "M2.5_eps5", "fine"): 189.8,
}

# Launch order, frozen. Waves are ordered so that if the budget stops the line,
# what is lost last is the two single-grid band-only rows, never a grid triple.
WAVES = [
    [("cone", "M2.35_th10", "coarse"), ("cone", "M2.35_th10", "medium")],
    [("cone", "M2.35_th10", "fine"), ("wedge", "M2.0_th15", "coarse")],
    [("wedge", "M2.0_th15", "medium"), ("wedge", "M2.0_th15", "fine")],
    [("diamond", "M2.0_eps7p125", "coarse"), ("diamond", "M2.0_eps7p125", "medium")],
    [("diamond", "M2.0_eps7p125", "fine"), ("wedge", "M3.0_th15", "fine")],
    [("wedge", "M2.5_th10", "fine"), ("diamond", "M2.5_eps5", "fine")],
]

# Case parameters, frozen. beta_exact / cd_exact come from exact_theory.py and
# take no CFD input; they are used for domain sizing and for the diamond's own
# result.json, never as a gate reference (the gate references are frozen
# separately in grade_f3.py).
PARAMS = {
    ("wedge", "M2.0_th15"): dict(M=2.0, ang=15.0, beta=45.343616761855984),
    ("wedge", "M3.0_th15"): dict(M=3.0, ang=15.0, beta=32.240400182744665),
    ("wedge", "M2.5_th10"): dict(M=2.5, ang=10.0, beta=31.85059223127216),
    ("cone", "M2.35_th10"): dict(M=2.35, ang=10.0, beta=26.73671771893154),
    ("diamond", "M2.0_eps7p125"): dict(M=2.0, ang=7.125, beta=36.33311060432785,
                                       cd=0.036331061285517954),
    ("diamond", "M2.5_eps5"): dict(M=2.5, ang=5.0, beta=27.42266202135665,
                                   cd=0.01343027834624868),
}


def wall_cap(key):
    if key == ("cone", "M2.35_th10", "fine"):
        return 1500.0
    return max(120.0, 2.5 * PRED[key])


def case_dir(key):
    return os.path.join(RUNS, key[0], key[1], key[2])


# ---------------------------------------------------------------------------
# child: one run
# ---------------------------------------------------------------------------

def run_one_child(fam, pair, level):
    cd = case_dir((fam, pair, level))
    if os.path.exists(cd):
        # The completion rule's guard: refuse a case where 0/ or a time dir
        # already exists. This conversion always runs into a fresh directory.
        sys.stderr.write("REFUSED: %s already exists\n" % cd)
        return 3
    os.makedirs(cd)
    p = PARAMS[(fam, pair)]
    t0 = time.time()
    try:
        if fam == "wedge":
            from make_wedge_case import make_case
            from run_wedge_case import run_one
            meta = make_case(cd, p["M"], p["ang"], level, p["beta"])
            json.dump(meta, open(os.path.join(cd, "meta.json"), "w"), indent=2)
            run_one(cd, p["M"], p["ang"], level, p["beta"])
        elif fam == "cone":
            from make_cone_case import make_case
            from run_cone_case import run_one
            meta = make_case(cd, p["M"], p["ang"], level, p["beta"])
            json.dump(meta, open(os.path.join(cd, "meta.json"), "w"), indent=2)
            run_one(cd, p["M"], p["ang"], level, p["beta"])
        elif fam == "diamond":
            from make_diamond_case import make_case
            from run_diamond_case import run_one
            meta = make_case(cd, p["M"], p["ang"], level, p["beta"])
            json.dump(meta, open(os.path.join(cd, "meta.json"), "w"), indent=2)
            run_one(cd, p["M"], p["ang"], level, p["beta"], p["cd"])
        else:
            raise ValueError(fam)
        rc = 0
    except Exception as e:
        sys.stderr.write("FAILED %s/%s/%s: %r\n" % (fam, pair, level, e))
        rc = 1
    open(os.path.join(cd, "run_rc.txt"), "w").write("%d\n" % rc)
    json.dump(dict(wall_s=time.time() - t0, ranks=1),
              open(os.path.join(cd, "launch_timing.json"), "w"), indent=2)
    return rc


# ---------------------------------------------------------------------------
# parent: waves + budget watchdog
# ---------------------------------------------------------------------------

def main():
    os.makedirs(RUNS, exist_ok=True)
    ledger = dict(cap_core_min=CAP_CORE_MIN, runs={}, stopped_by=None)
    spent_s = 0.0

    for wi, wave in enumerate(WAVES, 1):
        pred_wave = sum(PRED[k] for k in wave)
        if spent_s + pred_wave * WAVE_HEADROOM > CAP_CORE_S:
            for k in wave:
                ledger["runs"]["/".join(k)] = dict(status="PENDING",
                                                   reason="budget: wave %d not launched" % wi)
            ledger["stopped_by"] = "budget check before wave %d" % wi
            continue

        procs = {}
        for k in wave[:MAX_CONCURRENT]:
            cmd = [sys.executable, os.path.abspath(__file__), "--one", k[0], k[1], k[2]]
            procs[k] = dict(p=subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                               stderr=subprocess.PIPE),
                            t0=time.time())
            print("[wave %d] launched %s" % (wi, "/".join(k)), flush=True)

        killed_budget = False
        while any(v["p"].poll() is None for v in procs.values()):
            time.sleep(5.0)
            live_s = sum(time.time() - v["t0"] for v in procs.values()
                         if v["p"].poll() is None)
            done_s = sum(v.get("wall", 0.0) for v in procs.values() if "wall" in v)
            for k, v in procs.items():
                if v["p"].poll() is not None and "wall" not in v:
                    v["wall"] = time.time() - v["t0"]
            if spent_s + live_s + done_s >= CAP_CORE_S:
                for k, v in procs.items():
                    if v["p"].poll() is None:
                        v["p"].send_signal(signal.SIGTERM)
                        v["killed"] = "budget"
                killed_budget = True
                ledger["stopped_by"] = "global watchdog reached the %.1f core-min cap" % CAP_CORE_MIN
                break
            for k, v in procs.items():
                if v["p"].poll() is None and (time.time() - v["t0"]) > wall_cap(k):
                    v["p"].send_signal(signal.SIGTERM)
                    v["killed"] = "wall cap %.0f s" % wall_cap(k)

        for k, v in procs.items():
            v["p"].wait()
            v.setdefault("wall", time.time() - v["t0"])
            spent_s += v["wall"]
            key = "/".join(k)
            ledger["runs"][key] = dict(
                status=("KILLED" if "killed" in v else
                        ("OK" if v["p"].returncode == 0 else "FAILED")),
                killed_reason=v.get("killed"),
                rc=v["p"].returncode,
                predicted_core_s=PRED[k], actual_core_s=round(v["wall"], 2),
                stderr_tail=(v["p"].stderr.read().decode()[-800:]
                             if v["p"].stderr else ""))
            print("[wave %d] %-40s %s  %.1f core-s (pred %.1f)  cum %.2f core-min"
                  % (wi, key, ledger["runs"][key]["status"], v["wall"], PRED[k],
                     spent_s / 60.0), flush=True)

        ledger["spent_core_min"] = round(spent_s / 60.0, 4)
        json.dump(ledger, open(os.path.join(HERE, "F3_CONVERSION_RUN_LEDGER.json"), "w"),
                  indent=2)
        if killed_budget:
            break

    ledger["spent_core_min"] = round(spent_s / 60.0, 4)
    ledger["cap_respected"] = spent_s <= CAP_CORE_S
    json.dump(ledger, open(os.path.join(HERE, "F3_CONVERSION_RUN_LEDGER.json"), "w"),
              indent=2)
    print("\nTOTAL %.4f core-min against a %.1f core-min cap (respected: %s)"
          % (spent_s / 60.0, CAP_CORE_MIN, ledger["cap_respected"]))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--one":
        sys.exit(run_one_child(sys.argv[2], sys.argv[3], sys.argv[4]))
    main()
