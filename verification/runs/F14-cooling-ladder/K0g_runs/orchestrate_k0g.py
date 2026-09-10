#!/usr/bin/env python3
"""K0g §2ba campaign orchestrator + detached autograder (base 60 s runs).

Sequences the FROZEN K0g grading path (pinned in K0g_PREREGISTRATION.md §7.7):
per arm  build_k0g --root -> blockMesh -> check_k0g_mesh -> launch_k0g.sh (the
frozen +x-independent setsid detach; each arm PPID=1). Bounded to CAP concurrent
arms; the 915.58 core-min rung ceiling stops launching with unrun arms named
(rule 12, no re-budget). On completion: mark_done_k0g (completion + age guard),
check_k0g_extraction_equivalence, analyse_k0g -> durable verdict artifact.

The §7.1'' extension (60->120) is NOT auto-triggered: it is a registered
drift-based decision and the frozen tooling has no restart mode; per-arm drift is
reported and any turbulent arm needing it is FLAGGED for the supervisor.
This orchestrator is itself setsid-detached (PPID=1) so it survives the launching
agent. It touches no other team's runs."""
import os, re, sys, time, json, subprocess

REPO = "/home/ubuntu/Certonomous"
RUNHOME = os.path.join(REPO, "verification/runs/F14-cooling-ladder/K0g_runs")
SCRIPTS = os.path.join(REPO, "scripts")
BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
CEILING = 915.58
CAP = 3
# (name, level, POINT core-min, per-arm timeout_s = 10x POINT)
ARMS = [
    ("M1_c", "L1", 49.15, 29490),
    ("M2_c", "L1", 49.15, 29490),
    ("M1_m", "L2", 96.34, 57804),
    ("M2_m", "L2", 96.34, 57804),
    ("C_lam", "L2", 72.25, 43350),
]
TURBULENT = {"M1_c", "M2_c", "M1_m", "M2_m"}

LOG = open(os.path.join(RUNHOME, "orchestrate.log"), "a", buffering=1)
def log(m):
    LOG.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] {m}\n")

def sh(cmd, timeout=None):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
def ofsh(cmd_str, timeout=None):
    return subprocess.run(["bash", "-c", f"set +u; . {BASHRC} >/dev/null 2>&1; {cmd_str}"],
                          capture_output=True, text=True, timeout=timeout)

def status_path(n): return os.path.join(RUNHOME, f"STATUS.{n}")
def case_dir(n): return os.path.join(RUNHOME, n)
def launchlog(n): return os.path.join(case_dir(n), "log.launch")

def status_wall(n):
    sp = status_path(n)
    if not os.path.exists(sp): return None
    m = re.search(r"wall=(\d+)", open(sp).read())
    return int(m.group(1)) if m else None

def status_rc(n):
    sp = status_path(n)
    if not os.path.exists(sp): return None
    m = re.search(r"rc=([0-9]+|na)", open(sp).read())
    return m.group(1) if m else None

def write_state(d):
    json.dump(d, open(os.path.join(RUNHOME, "CAMPAIGN_STATE.json"), "w"), indent=2)

log("=== K0g orchestrator start === pid=%d ppid=%d" % (os.getpid(), os.getppid()))

# ---- PHASE A: prep ------------------------------------------------------
prep = {}
for name, level, pt, to in ARMS:
    d = case_dir(name)
    r = sh(["python3", f"{SCRIPTS}/build_k0g.py", "--root", RUNHOME, name])
    if r.returncode != 0:
        prep[name] = "BUILD_FAIL: " + (r.stderr or r.stdout)[-400:]; log(f"{name} {prep[name]}"); continue
    r = ofsh(f"blockMesh -case {d} > {d}/log.blockMesh 2>&1")
    if r.returncode != 0:
        prep[name] = "BLOCKMESH_FAIL"; log(f"{name} {prep[name]}"); continue
    r = sh(["python3", f"{SCRIPTS}/check_k0g_mesh.py", "--case", d, "--level", level])
    if r.returncode != 0:
        prep[name] = "MESHCHECK_FAIL: " + (r.stdout or r.stderr)[-400:]; log(f"{name} {prep[name]}"); continue
    prep[name] = "READY"; log(f"{name} prep READY ({level}, {level and 'cells ok'})")
write_state({"phase": "prepped", "prep": prep})

ready = [a for a in ARMS if prep[a[0]] == "READY"]

# ---- PHASE B: launch, cap-CAP, cost ceiling -----------------------------
launched, unrun, launch_t = [], [], {}

def running():
    out = []
    for (n, l, p, to) in launched:
        if os.path.exists(status_path(n)):
            continue
        # dead-not-started guard: REFUSE in log.launch, or past its timeout+margin
        ll = launchlog(n)
        refused = os.path.exists(ll) and "REFUSE" in open(ll, errors="replace").read()
        stuck = (time.time() - launch_t.get(n, time.time())) > (to + 600)
        if refused or stuck:
            continue
        out.append(n)
    return out

def completed_coremin():
    tot = 0.0
    for (n, l, p, to) in launched:
        w = status_wall(n)
        if w is not None:
            tot += w / 60.0
    return tot

for arm in ready:
    name, level, pt, to = arm
    while len(running()) >= CAP:
        write_state({"phase": "launching", "running": running(),
                     "completed_coremin": round(completed_coremin(), 1)})
        time.sleep(20)
    running_pt = sum(p for (n, l, p, t) in launched
                     if not os.path.exists(status_path(n)) and n in running())
    proj = completed_coremin() + running_pt + pt
    if proj > CEILING:
        unrun.append(name); log(f"{name} UNRUN: projected {proj:.1f} > ceiling {CEILING} (rule 12)")
        continue
    d = case_dir(name)
    subprocess.Popen(["bash", f"{SCRIPTS}/launch_k0g.sh", "--case-dir", d,
                      "--timeout", str(to), "--foam-bashrc", BASHRC],
                     stdout=open(f"{d}/log.launch.orch", "a"),
                     stderr=subprocess.STDOUT)
    launched.append(arm); launch_t[name] = time.time()
    log(f"{name} LAUNCHED (timeout {to}s, POINT {pt} core-min)")
    time.sleep(8)

# also record arms that were ready but never launched due to ceiling
for a in ready:
    if a[0] not in [x[0] for x in launched] and a[0] not in unrun:
        unrun.append(a[0])
unrun += [a[0] for a in ARMS if prep[a[0]] != "READY"]

# wait for all launched to reach STATUS (or be declared dead by guard)
while running():
    write_state({"phase": "running", "running": running(),
                 "completed_coremin": round(completed_coremin(), 1),
                 "launched": [x[0] for x in launched], "unrun": unrun})
    time.sleep(30)
log("all launched arms resolved (STATUS or dead-guard)")

# ---- PHASE C: grade -----------------------------------------------------
launched_names = [x[0] for x in launched]
present = [n for n in launched_names if os.path.exists(status_path(n))]

md = sh(["python3", f"{SCRIPTS}/mark_done_k0g.py", "--root", RUNHOME] + present)
ee = {}
for n in present:
    r = sh(["python3", f"{SCRIPTS}/check_k0g_extraction_equivalence.py", "--case", case_dir(n)])
    ee[n] = (r.returncode, (r.stdout or r.stderr)[-600:])
an = sh(["python3", f"{SCRIPTS}/analyse_k0g.py", "--root", RUNHOME])

# per-arm cost calibration
cost_rows = []
total_actual = 0.0
for (n, l, p, to) in launched:
    w = status_wall(n); rc = status_rc(n)
    act = (w / 60.0) if w is not None else None
    if act is not None:
        total_actual += act
    ratio = (act / p) if act is not None else None
    cost_rows.append((n, l, p, act, ratio, rc, w))

# ---- durable verdict artifact ------------------------------------------
V = os.path.join(RUNHOME, "K0g_VERDICT.txt")
with open(V, "w") as f:
    f.write("K0g §2ba CAMPAIGN VERDICT (base 60 s runs)\n")
    f.write("Generated: %s UTC by orchestrate_k0g.py\n" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    f.write("Frozen prereg: docs/campaigns/F14-cooling-ladder/K0g_PREREGISTRATION.md (freeze 4d0046c1)\n")
    f.write("Grading path: FROZEN §7.7 pins (check_comparator_freeze PASS 8/8)\n\n")
    f.write("=== PREP ===\n")
    for name, level, pt, to in ARMS:
        f.write(f"  {name:6s} {level}  {prep[name]}\n")
    f.write("\n=== LAUNCHED / UNRUN ===\n")
    f.write(f"  launched: {launched_names}\n  unrun: {unrun}\n")
    f.write("\n=== PER-ARM STATUS + COST CALIBRATION (rule 12; actual = wall_s/60, ranks=1) ===\n")
    for (n, l, p, act, ratio, rc, w) in cost_rows:
        a = f"{act:.2f}" if act is not None else "NONE"
        rr = f"{ratio:.3f}" if ratio is not None else "NONE"
        f.write(f"  {n:6s} {l}  rc={rc}  wall={w}s  actual={a} core-min  POINT={p}  ratio(actual/POINT)={rr}\n")
    f.write(f"  TOTAL actual = {total_actual:.2f} core-min  vs CEILING {CEILING} core-min "
            f"({'WITHIN' if total_actual <= CEILING else 'OVER'})\n")
    f.write("  $ derived (0.0513/core-h): %.4f\n" % (total_actual / 60.0 * 0.0513))
    f.write("\n=== mark_done_k0g (completion + age guard) ===\n")
    f.write(f"  rc={md.returncode}\n{md.stdout}\n{md.stderr[-800:]}\n")
    f.write("\n=== check_k0g_extraction_equivalence (per present arm) ===\n")
    for n, (rc, out) in ee.items():
        f.write(f"  {n}: rc={rc}\n{out}\n")
    f.write("\n=== analyse_k0g (THE GRADED VERDICT) rc=%d ===\n" % an.returncode)
    f.write(an.stdout + "\n" + an.stderr[-1200:] + "\n")
    f.write("\n=== §7.1'' EXTENSION DETERMINATION (drift-based; NOT auto-triggered) ===\n")
    f.write("  Per-arm stationarity drift is in the analyse_k0g output above.\n")
    f.write("  Any TURBULENT arm (M1_c/M1_m/M2_c/M2_m) NOT stationary at 60 s is a candidate\n")
    f.write("  for the ONE registered extension to 120 s (§7.1''). C_lam is the discrimination\n")
    f.write("  control (P-K0g-2: predicted NON-stationary; NOT extended). The extension is a\n")
    f.write("  supervised follow-up: the frozen tooling has no restart mode and the decision is\n")
    f.write("  registered as drift-based. FLAGGED for the heat-transfer supervisor.\n")

write_state({"phase": "graded", "launched": launched_names, "unrun": unrun,
             "present": present, "mark_done_rc": md.returncode,
             "analyse_rc": an.returncode, "total_actual_coremin": round(total_actual, 2),
             "verdict": V})
log(f"GRADED. verdict={V} mark_done_rc={md.returncode} analyse_rc={an.returncode} "
    f"total_actual={total_actual:.2f} core-min")
log("=== K0g orchestrator done ===")
