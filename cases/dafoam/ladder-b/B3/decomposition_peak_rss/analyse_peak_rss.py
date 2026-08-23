#!/usr/bin/env python3
"""
B3 decomposition peak-RSS: THE GRADING PATH, frozen at the pre-registration commit.

Registered in PREREGISTRATION.md in this directory. Every band, every archived digit
and every verdict rule below is fixed HERE, before any arm of the re-run exists, so
that no threshold can be chosen to fit an answer (standing rule 2).

It grades six rows -- M0 identity, M1 planted control, M2/M3 the two peak bands,
M4 ordering, M5 no-OOM -- and it REFUSES (exit 2) rather than degrade when the
evidence it needs is absent (standing rule 4).

M0 IS THE LOAD-BEARING ROW. The product of this item is a memory number ATTACHED to
an already-graded row. If the re-run does not reproduce the graded arm's converged
digits, the re-run is a variant and its peak does not attach: M0 turns the item into
NOT A RESULT for the attachment question, and the peak is reported as belonging to
the re-run arm alone. A gate may only turn a PASS or GATE FAIL INTO NOT A RESULT,
never the reverse (standing rule 5, the same ordering).

usage: analyse_peak_rss.py <run-root>
exit 0 = graded (read the verdicts), 2 = refusal, 3 = a graded row is GATE FAIL
"""
import datetime as dt
import json
import os
import re
import sys

EXIT_OK, EXIT_REFUSE, EXIT_FAIL = 0, 2, 3
GIB = 1073741824.0
CAP_BYTES = 12 * 1024**3          # the --memory=12g container cap
MAX_GAP_S = 5.0                   # registered watcher cadence requirement
MIN_SAMPLES = 30                  # a peak from a handful of samples is not a peak

# ---------------------------------------------------------------------------
# FROZEN: the archived digits of the graded arms, from
#   cases/dafoam/ladder-b/B3/decomposition_np4/RESULTS.md section 2 and
#   /home/ubuntu/certonomous-runs/B3-decomposition-np4/grading.json
# The re-run must reproduce every one of these.
# ---------------------------------------------------------------------------
ARMS = {
    "D_serial": {
        "np": 1,
        "iterations": 163,
        "reason": 2,
        "obj": "1.5279275989724403e-02",
        "grad": ("21000", "1.4557054356e-05", "-4.694385e-07", "1.915505e-06"),
        "iter0_residual": "7.091589775454e-04",
        # registered bands, GiB
        "band_tree_rss": (5.5, 9.0),
        "band_mem_peak": (6.0, 11.0),
    },
    "D_simple2": {
        "np": 4,
        "iterations": 766,
        "reason": 2,
        "obj": "1.5279278602317540e-02",
        "grad": ("21000", "1.4558490322e-05", "-4.694298e-07", "1.915990e-06"),
        "iter0_residual": "7.091590381747e-04",
        "band_tree_rss": (6.0, 11.0),
        "band_mem_peak": (8.0, 12.0),
    },
}
BANNER = "DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU"

RE_DONE = re.compile(r"Total iterations:\s*(\d+)\.\s*PetscConvergedReason:\s*(-?\d+)")
RE_OBJ = re.compile(r"OBJ varianceU:\s*(\S+)")
RE_GRAD = re.compile(r"GRAD n=(\d+) norm=(\S+) min=(\S+) max=(\S+)")
RE_ITER0 = re.compile(r"Main iteration 0 KSP Residual norm (\S+)")
RE_SAMPLE = re.compile(
    r"^(\S+) SAMPLE MEM_PEAK_B=\s*(\d+) MEM_CURRENT_B=\s*(\d+) "
    r"TREE_RSS_KB=\s*(\d+) NPIDS=\s*(\d+) MEMAVAIL_KB=\s*(\d+) PROCS=\[(.*)\]\s*$")
RE_TS = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
# The in-container read of memory.peak taken AFTER mpirun exits (see
# PREREGISTRATION.md section 4, disclosed departure 2). The external sampler can
# only see the peak up to its last tick before teardown; this line is exact at exit.
RE_INCONT_PEAK = re.compile(r"CGROUP_PEAK_BYTES=(\d+)")


def refuse(msg):
    print("analyse_peak_rss: REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def secs(ts):
    if not RE_TS.match(ts):
        return None
    return dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").timestamp()


def read_watch(path):
    """Return the peak record for one arm's watcher log, or refuse."""
    if not os.path.exists(path):
        refuse("watcher log absent: %s -- no peak was measured" % path)
    rows, aborted = [], False
    for line in open(path, errors="replace"):
        if " ABORT " in line or " KILL_ISSUED " in line:
            aborted = True
        m = RE_SAMPLE.match(line.strip())
        if m:
            rows.append(dict(ts=m.group(1), mem_peak_b=int(m.group(2)),
                             mem_current_b=int(m.group(3)),
                             tree_rss_kb=int(m.group(4)), npids=int(m.group(5)),
                             memavail_kb=int(m.group(6)), procs=m.group(7)))
    if len(rows) < MIN_SAMPLES:
        refuse("%s holds %d samples, fewer than the registered minimum %d"
               % (path, len(rows), MIN_SAMPLES))
    gaps = []
    for a, b in zip(rows, rows[1:]):
        ta, tb = secs(a["ts"]), secs(b["ts"])
        if ta is not None and tb is not None:
            gaps.append(tb - ta)
    max_gap = max(gaps) if gaps else None
    top_rss = max(rows, key=lambda r: r["tree_rss_kb"])
    top_peak = max(r["mem_peak_b"] for r in rows)
    # which process carried the peak: largest hwm in the peak-RSS sample
    biggest = None
    for tok in top_rss["procs"].split():
        parts = tok.split(":")
        if len(parts) == 4 and parts[3].startswith("hwm"):
            hwm = int(parts[3][3:])
            if biggest is None or hwm > biggest[1]:
                biggest = (tok, hwm)
    return dict(samples=len(rows), max_gap_s=max_gap, aborted=aborted,
                tree_rss_peak_gib=top_rss["tree_rss_kb"] / 1048576.0,
                tree_rss_peak_ts=top_rss["ts"],
                tree_rss_peak_npids=top_rss["npids"],
                tree_rss_peak_procs=top_rss["procs"].strip(),
                dominant_process=(biggest[0] if biggest else None),
                dominant_process_hwm_gib=(biggest[1] / 1048576.0 if biggest else None),
                mem_peak_gib=top_peak / GIB, mem_peak_bytes=top_peak,
                min_memavail_kb=min(r["memavail_kb"] for r in rows))


def read_solver(path):
    if not os.path.exists(path):
        refuse("solver log absent: %s" % path)
    txt = open(path, errors="replace").read()
    done = RE_DONE.search(txt)
    obj = RE_OBJ.search(txt)
    grad = RE_GRAD.search(txt)
    it0 = RE_ITER0.search(txt)
    icp = RE_INCONT_PEAK.search(txt)
    return dict(iterations=int(done.group(1)) if done else None,
                reason=int(done.group(2)) if done else None,
                obj=obj.group(1) if obj else None,
                grad=tuple(grad.groups()) if grad else None,
                iter0_residual=it0.group(1) if it0 else None,
                banner=(BANNER in txt), end_line=bool(done),
                incontainer_peak_bytes=int(icp.group(1)) if icp else None)


def main():
    if len(sys.argv) != 2:
        refuse("usage: analyse_peak_rss.py <run-root>")
    root = sys.argv[1]

    # ---- M1, the planted control. Standing rule 3: a peak from an instrument not
    # ---- shown able to see a known peak is not evidence. REFUSE, do not degrade.
    vpath = os.path.join(root, "selftest", "selftest_verdict.txt")
    if not os.path.exists(vpath):
        refuse("no planted-control verdict at %s -- the watcher was never shown able "
               "to see a peak it did not choose; every number below would be "
               "uncontrolled" % vpath)
    vtxt = open(vpath, errors="replace").read().strip()
    if "PASS" not in vtxt:
        refuse("planted control did not PASS: %r" % vtxt)

    out = {"selftest": vtxt, "arms": {}, "graded": {}}
    ledger = {}
    lpath = os.path.join(root, "ledger.csv")
    if os.path.exists(lpath):
        for line in open(lpath):
            f = line.strip().split(",")
            if len(f) >= 7 and f[0] in ARMS:
                ledger[f[0]] = dict(rc=f[4], wall_s=f[5], core_min=f[6])

    for arm, ref in ARMS.items():
        w = read_watch(os.path.join(root, "logs", arm + "_rss.log"))
        s = read_solver(os.path.join(root, "logs", arm + ".log"))
        grad_path = os.path.join(root, arm, "cbfs_beta_grad.npy")
        run_path = os.path.join(root, arm, "runScript.py")
        # age guard: the gradient artefact must POSTDATE the staged run script,
        # i.e. it was produced by the run allowed to produce it, not carried in.
        age_ok = (os.path.exists(grad_path) and os.path.exists(run_path)
                  and os.path.getmtime(grad_path) > os.path.getmtime(run_path))
        # The authoritative peak is the LARGER of the external sampler's last
        # monotone reading and the in-container read taken after mpirun exited.
        # Both are recorded; neither is discarded.
        w["mem_peak_sampler_gib"] = w["mem_peak_gib"]
        if s["incontainer_peak_bytes"]:
            w["mem_peak_incontainer_gib"] = s["incontainer_peak_bytes"] / GIB
            if s["incontainer_peak_bytes"] > w["mem_peak_bytes"]:
                w["mem_peak_bytes"] = s["incontainer_peak_bytes"]
                w["mem_peak_gib"] = s["incontainer_peak_bytes"] / GIB
        else:
            w["mem_peak_incontainer_gib"] = None
        out["arms"][arm] = dict(watch=w, solver=s, ledger=ledger.get(arm),
                                gradient_artefact=os.path.exists(grad_path),
                                age_guard=age_ok)

    # ---- M0: identity with the graded arms -------------------------------------
    m0 = {}
    for arm, ref in ARMS.items():
        s = out["arms"][arm]["solver"]
        checks = {
            "reason": s["reason"] == ref["reason"],
            "iterations": s["iterations"] == ref["iterations"],
            "objective": s["obj"] == ref["obj"],
            "gradient_line": s["grad"] == ref["grad"],
            "iter0_residual": s["iter0_residual"] == ref["iter0_residual"],
            "sublu_banner": s["banner"] is True,
            "end_line": s["end_line"] is True,
            "gradient_artefact": out["arms"][arm]["gradient_artefact"],
            "age_guard": out["arms"][arm]["age_guard"],
        }
        m0[arm] = dict(checks=checks, measured=s, archived=ref,
                       all_identical=all(checks.values()))
    identity_ok = all(v["all_identical"] for v in m0.values())
    out["graded"]["M0"] = dict(
        quantity="re-run reproduces every archived digit of the graded arm",
        detail=m0,
        verdict="PASS" if identity_ok else "NOT A RESULT")

    def band_row(arm, key, bandkey, label):
        v = out["arms"][arm]["watch"][key]
        lo, hi = ARMS[arm][bandkey]
        ok = lo <= v <= hi
        return dict(quantity=label, arm=arm, value_gib=round(v, 4),
                    band_gib=[lo, hi],
                    verdict=("PASS" if ok else "GATE FAIL") if identity_ok
                            else "NOT A RESULT")

    out["graded"]["M2a"] = band_row("D_simple2", "tree_rss_peak_gib",
                                    "band_tree_rss", "D_simple2 peak tree RSS")
    out["graded"]["M2b"] = band_row("D_simple2", "mem_peak_gib",
                                    "band_mem_peak", "D_simple2 cgroup memory.peak")
    out["graded"]["M3a"] = band_row("D_serial", "tree_rss_peak_gib",
                                    "band_tree_rss", "D_serial peak tree RSS")
    out["graded"]["M3b"] = band_row("D_serial", "mem_peak_gib",
                                    "band_mem_peak", "D_serial cgroup memory.peak")

    # ---- M4: ordering, np=4 above np=1 on BOTH instruments ----------------------
    o4 = out["arms"]["D_simple2"]["watch"]
    o1 = out["arms"]["D_serial"]["watch"]
    ord_ok = (o4["tree_rss_peak_gib"] > o1["tree_rss_peak_gib"]
              and o4["mem_peak_gib"] > o1["mem_peak_gib"])
    out["graded"]["M4"] = dict(
        quantity="peak(np=4, simple) > peak(np=1) on tree RSS AND memory.peak",
        tree_rss=[round(o4["tree_rss_peak_gib"], 4), round(o1["tree_rss_peak_gib"], 4)],
        mem_peak=[round(o4["mem_peak_gib"], 4), round(o1["mem_peak_gib"], 4)],
        verdict=("PASS" if ord_ok else "GATE FAIL") if identity_ok else "NOT A RESULT")

    # ---- M5: no OOM, and the peak is a free peak rather than a cap-limited one ---
    m5 = {}
    for arm in ARMS:
        w = out["arms"][arm]["watch"]
        led = out["arms"][arm]["ledger"]
        m5[arm] = dict(rc=(led or {}).get("rc"), aborted_by_watcher=w["aborted"],
                       mem_peak_bytes=w["mem_peak_bytes"], cap_bytes=CAP_BYTES,
                       below_cap=w["mem_peak_bytes"] < CAP_BYTES,
                       max_gap_s=w["max_gap_s"], samples=w["samples"],
                       cadence_ok=(w["max_gap_s"] is not None
                                   and w["max_gap_s"] <= MAX_GAP_S))
    m5_ok = all(v["rc"] == "0" and v["below_cap"] and not v["aborted_by_watcher"]
                and v["cadence_ok"] for v in m5.values())
    out["graded"]["M5"] = dict(
        quantity="rc=0, memory.peak strictly below the 12 GiB cap, no watcher abort, "
                 "sample cadence <= %.0f s" % MAX_GAP_S,
        detail=m5,
        verdict=("PASS" if m5_ok else "GATE FAIL") if identity_ok else "NOT A RESULT")

    with open(os.path.join(root, "peak_rss.json"), "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)

    print("=" * 78)
    print("B3 decomposition peak RSS -- graded against the frozen bands")
    print("=" * 78)
    print("planted control: %s" % vtxt)
    for arm in ARMS:
        w = out["arms"][arm]["watch"]
        print("\n%-10s np=%d  samples=%d  max_gap=%ss" %
              (arm, ARMS[arm]["np"], w["samples"], w["max_gap_s"]))
        print("  peak tree RSS   %8.3f GiB  at %s  (%d pids)" %
              (w["tree_rss_peak_gib"], w["tree_rss_peak_ts"], w["tree_rss_peak_npids"]))
        print("  dominant proc   %s  VmHWM %.3f GiB" %
              (w["dominant_process"], w["dominant_process_hwm_gib"] or -1))
        print("  memory.peak     %8.3f GiB  (cgroup v2 kernel high-water; sampler %.3f, "
              "in-container %s)" % (w["mem_peak_gib"], w["mem_peak_sampler_gib"],
                                    ("%.3f" % w["mem_peak_incontainer_gib"])
                                    if w["mem_peak_incontainer_gib"] else "unread"))
        print("  procs at peak   %s" % w["tree_rss_peak_procs"])
    print("\n%-5s %-58s %s" % ("row", "quantity", "verdict"))
    fails = 0
    for k in ("M0", "M2a", "M2b", "M3a", "M3b", "M4", "M5"):
        r = out["graded"][k]
        extra = ""
        if "value_gib" in r:
            extra = "  %.3f GiB in [%.1f, %.1f]" % (r["value_gib"], *r["band_gib"])
        print("%-5s %-58s %s%s" % (k, r["quantity"][:58], r["verdict"], extra))
        if r["verdict"] == "GATE FAIL":
            fails += 1
    print("\nwritten: %s" % os.path.join(root, "peak_rss.json"))
    sys.exit(EXIT_FAIL if fails else EXIT_OK)


if __name__ == "__main__":
    main()
