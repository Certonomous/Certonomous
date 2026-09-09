#!/usr/bin/env python3
"""PRD-E1 full-15 GRADED ladder scheduler (detached, PPID=1 survivable).

Launches the 5 U_s x 3 levels ACTIVE ladder into the (now-created) graded runs-home
verification/runs/navier_class/PRD/ with BOUNDED CONCURRENCY (cap 3), serial
(ranks=1, run_prd.sh as frozen -- no decomposePar), L3-first within each U_s so
whole per-U_s triples complete in order.  Pre-meshes all 15 upfront so the FROZEN
autograder (autograde_prd.py) can be armed immediately and discover all 15 (no
premature-grade race).  Tracks cumulative core-min and STOPS launching on the §9
9000 core-min cap (rule 12).  Per-solve hard timeouts = the frozen deadlines.
rc is captured INSIDE run_prd.sh's detached wrapper (never around setsid)."""
import glob, os, re, subprocess, sys, time

REPO = "/home/ubuntu/Certonomous"
CASE = REPO + "/cases/navier_class/PRD"
RUNS = REPO + "/verification/runs/navier_class/PRD"
BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
BUILD, RUN, AG = CASE + "/build_prd.py", CASE + "/run_prd.sh", CASE + "/autograde_prd.py"
US = [0.25, 0.50, 1.00, 2.00, 4.00]
LEVELS = ["L1", "L2", "L3"]
DEADLINE = {"L1": 200, "L2": 1400, "L3": 18000}   # frozen preflight deadlines, s
CAP, CAP_CORE_MIN = 3, 9000.0
LOG = RUNS + "/_scheduler.log"


def log(m):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), m)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def cname(u, lv): return "us%.2f_%s" % (u, lv)
def cdir(u, lv): return os.path.join(RUNS, cname(u, lv))
def status_p(u, lv): return os.path.join(cdir(u, lv), "STATUS." + cname(u, lv))


def premesh(u, lv):
    d = cdir(u, lv)
    subprocess.run([sys.executable, BUILD, "--emit", d, "--level", lv, "--us", str(u)],
                   capture_output=True)
    cmd = (". %s >/dev/null 2>&1; blockMesh -case %s >%s/log.blockMesh 2>&1 && "
           "topoSet -case %s >%s/log.topoSet 2>&1 && "
           "checkMesh -case %s >%s/log.checkMesh 2>&1"
           % (BASHRC, d, d, d, d, d, d))
    subprocess.run(["bash", "-c", cmd], capture_output=True)


def finished(u, lv):
    s = status_p(u, lv)
    return os.path.isfile(s) and "rc=" in open(s, errors="replace").read()


def launch_solve(u, lv):
    # run_prd.sh self-detaches (setsid) and returns fast; rc captured in its wrapper.
    subprocess.run(["bash", RUN, "--case-dir", cdir(u, lv), "--timeout",
                    str(DEADLINE[lv])], capture_output=True)


def core_min_finished():
    tot = 0.0
    for s in glob.glob(RUNS + "/us*/STATUS.*"):
        m = re.search(r"core_min=([0-9.]+)", open(s, errors="replace").read())
        if m:
            tot += float(m.group(1))
    return tot


def main():
    os.makedirs(RUNS, exist_ok=True)
    log("scheduler START pid=%d ppid=%d (PPID=1 => survives fleet death)"
        % (os.getpid(), os.getppid()))
    jobs = [(u, lv) for u in US for lv in LEVELS]

    for (u, lv) in jobs:
        premesh(u, lv)
        log("pre-meshed %s" % cname(u, lv))
    log("all 15 pre-meshed -- discoverable by the autograder")

    # arm the FROZEN autograder (self-detaches via its own detach_once -> PPID=1)
    subprocess.run([sys.executable, AG, "--watch", "--root", RUNS,
                    "--max-wait", "86400", "--interval", "60",
                    "--foam-bashrc", BASHRC], capture_output=True)
    time.sleep(2)
    agpid = subprocess.run(["pgrep", "-f", "autograde_prd.py --watch"],
                           capture_output=True, text=True).stdout.strip()
    log("autograder ARMED (detached) pids=[%s]" % agpid.replace("\n", ","))

    lvrank = {"L3": 0, "L2": 1, "L1": 2}
    pending = sorted(jobs, key=lambda j: (US.index(j[0]), lvrank[j[1]]))
    launched, launch_t = set(), {}
    while True:
        cm_fin = core_min_finished()
        running = [j for j in launched if not finished(*j)]
        now = time.time()
        cm_run = sum((now - launch_t.get(j, now)) / 60.0 for j in running)  # ranks=1
        if cm_fin + cm_run > CAP_CORE_MIN:
            log("CORE-MIN CAP OVERRUN %.1f (fin %.1f + run %.1f) > %d -- STOP "
                "launching new (rule 12; no new budget)"
                % (cm_fin + cm_run, cm_fin, cm_run, CAP_CORE_MIN))
            break
        while len(running) < CAP and pending:
            j = pending.pop(0)
            launch_solve(*j)
            launched.add(j); launch_t[j] = time.time()
            log("launched %s deadline=%ds (running now %d, core_min fin=%.1f)"
                % (cname(*j), DEADLINE[j[1]], len(running) + 1, cm_fin))
            running = [x for x in launched if not finished(*x)]
        if not pending and all(finished(*j) for j in jobs):
            log("ALL 15 solves FINISHED; core_min=%.1f" % core_min_finished())
            break
        time.sleep(30)
    log("scheduler EXIT; core_min=%.1f; autograder grades when all plateaued "
        "-> %s/gate_prd_e1.json" % (core_min_finished(), RUNS))


if __name__ == "__main__":
    main()
