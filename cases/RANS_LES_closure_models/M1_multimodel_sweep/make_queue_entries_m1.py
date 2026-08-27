"""
Generate the 78 M1 queue entries into QUEUE_ENTRIES_DRAFT/.

THESE ARE DRAFTS.  `prereg_commit` is the literal PENDING_SUPERVISOR_FREEZE, so
every entry FAILS `scripts/queue_entry_check.py` at check 1 (SCHEMA: the field
must be a 40-character lowercase hex sha) and could not reach check 2.  NOTHING
HERE CAN LAUNCH.

They are written to QUEUE_ENTRIES_DRAFT/ and NOT to verification/queue/closure/,
because a valid entry in the live queue directory is picked up and LAUNCHED by a
cron-restarted daemon within about 60 seconds.

After the supervisor freezes PREREGISTRATION.md:
    python3 make_queue_entries_m1.py --prereg-commit <40-hex> --enqueued-by <who>
then inspect, then copy into verification/queue/closure/.

Cell counts are read from each benchmark case's own polyMesh/owner header at
generation time.  Nothing here is typed from a table.
"""
import argparse, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = "/home/ubuntu/closure-challenge-benchmark/data"
RUN_ROOT = "/home/ubuntu/closure-data/multimodel_sweep"
PREREG_PATH = "cases/RANS_LES_closure_models/M1_multimodel_sweep/PREREGISTRATION.md"
RUNNER = os.path.join(HERE, "run_m1.sh")
ARMS = ("kOmegaSST_null", "kOmega")
EXCLUDED = ("NASA_2DWMH",)

CAP_ITER = 20000
RATE_POINT = 3.30e-6      # s per cell-iteration, measured, RESULTS.md:393-396
RATE_CEIL = 4.010e-6      # s per cell-iteration, measured ceiling
CAP_MARGIN = 1.20         # over the MEASURED ceiling; two cases are outside the
                          # 3,025-21,000-cell range the envelope was measured over
RATE_USD = 0.0513         # owner-stated $/core-h.  DERIVED, never measured.
MEM_GB = 1.0              # ESTIMATED, not measured (PREREGISTRATION section 10)


def inventory():
    out = {}
    for dp, _d, _f in os.walk(BENCH):
        if os.path.basename(dp) != "polyMesh":
            continue
        root = os.path.dirname(os.path.dirname(dp))
        if not (os.path.isdir(os.path.join(root, "0"))
                and os.path.isdir(os.path.join(root, "system"))):
            continue
        cid = os.path.basename(root)
        if cid in EXCLUDED:
            continue
        head = open(os.path.join(root, "constant", "polyMesh", "owner"),
                    errors="replace").read(4000)
        m = re.search(r"nCells:\s*(\d+)", head)
        if not m:
            raise SystemExit(f"REFUSE: no nCells note in {root}/constant/polyMesh/owner")
        out[cid] = int(m.group(1))
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--prereg-commit", default="PENDING_SUPERVISOR_FREEZE")
    ap.add_argument("--enqueued-by", default="PENDING_SUPERVISOR_ENQUEUE")
    ap.add_argument("--out", default=os.path.join(HERE, "QUEUE_ENTRIES_DRAFT"))
    a = ap.parse_args(argv[1:])
    if a.prereg_commit != "PENDING_SUPERVISOR_FREEZE" and \
            not re.fullmatch(r"[0-9a-f]{40}", a.prereg_commit):
        raise SystemExit("REFUSE: --prereg-commit must be a 40-character lowercase "
                         "hex sha (an abbreviated sha is ambiguous and a freeze "
                         "cannot rest on an ambiguous referent)")
    inv = inventory()
    if len(inv) != 39:
        raise SystemExit(f"REFUSE: inventory yields {len(inv)} cases, registration "
                         f"names 39")
    os.makedirs(a.out, exist_ok=True)
    tot_est = tot_cap = 0.0
    n = 0
    for cid in sorted(inv):
        cells = inv[cid]
        est = cells * CAP_ITER * RATE_POINT / 60.0
        cap = cells * CAP_ITER * RATE_CEIL * CAP_MARGIN / 60.0
        timeout_s = int(math.ceil(cap * 60.0))     # ranks = 1
        for arm in ARMS:
            cwd = os.path.join(RUN_ROOT, arm, cid)
            entry = {
                "team": "closure",
                "case_id": f"M1_{arm}__{cid}",
                "prereg_commit": a.prereg_commit,
                "prereg_path": PREREG_PATH,
                "launch_cmd": ["/bin/bash", RUNNER,
                               "--case-dir", cwd,
                               "--arm", arm,
                               "--timeout-s", str(timeout_s),
                               "--cap-core-min", f"{cap:.3f}"],
                "cwd": cwd,
                "ranks": 1,
                "cost_core_min_estimate": round(est, 3),
                "cost_basis": (
                    f"derived: {cells} cells x {CAP_ITER} iterations x "
                    f"{RATE_POINT * 1e6:.2f} us per cell-iteration (MEASURED on this "
                    f"box on these meshes, Kaandorp2020_TBRF/aposteriori/"
                    f"RESULTS.md:393-396) / 60 = {est:.3f} core-min at ranks 1; "
                    f"${est / 60.0 * RATE_USD:.4f} at the owner-stated "
                    f"${RATE_USD}/core-h, reported-by-owner and DERIVED, not measured "
                    f"(COMPUTE_BUDGET_CHARTER section 5: this box cannot read its own "
                    f"billing)"),
                "memory_floor_gb": MEM_GB,
                "enqueued_by": a.enqueued_by,
                "cap_core_min_registered": round(cap, 3),
                "_m1_notes": {
                    "cells": cells,
                    "iterations": CAP_ITER,
                    "memory_floor_basis": "ESTIMATED, not measured -- no resident-set "
                                          "size was measured for these cases",
                    "age_guard_state": "0.orig present after staging; NO 0/ and NO "
                                       "numeric time directory",
                    "rule5": "standing rule 5 does not apply: one mesh per case, no "
                             "grid triple, no GCI",
                    "status_written_at_exit": "run_m1.sh writes STATUS (rc, wall_s, "
                                              "core_min, timestamps) atomically at "
                                              "exit; rc is captured INSIDE the wrapper",
                },
            }
            fn = os.path.join(a.out, f"M1_{arm}__{cid}.json")
            json.dump(entry, open(fn, "w"), indent=2, sort_keys=True)
            n += 1
            tot_est += est
            tot_cap += cap
    readme = os.path.join(a.out, "README.md")
    open(readme, "w").write(
        "# DRAFT -- NOT FROZEN, NOT COMMITTED, NO COMPUTE AUTHORISED\n\n"
        "# M1 queue entries -- DRAFTS, NOT ENQUEUED\n\n"
        f"{n} entries, {len(inv)} cases x {len(ARMS)} arms.\n\n"
        f"- registered ESTIMATE: **{tot_est:.1f} core-min** "
        f"({tot_est / 60:.2f} core-h, ${tot_est / 60 * RATE_USD:.2f} DERIVED)\n"
        f"- registered CAP:      **{tot_cap:.1f} core-min** "
        f"({tot_cap / 60:.2f} core-h, ${tot_cap / 60 * RATE_USD:.2f} DERIVED)\n\n"
        "**`prereg_commit` is the literal `PENDING_SUPERVISOR_FREEZE`.** Every entry\n"
        "therefore FAILS `scripts/queue_entry_check.py` check 1 (SCHEMA requires a\n"
        "40-character lowercase hex sha) and never reaches check 2. Nothing here can\n"
        "launch.\n\n"
        "**These are NOT in `verification/queue/closure/` on purpose.** A valid entry\n"
        "there is picked up and LAUNCHED by a cron-restarted daemon within ~60 s.\n\n"
        "`enqueued_by` is `PENDING_SUPERVISOR_ENQUEUE`: no one has performed\n"
        "`SUPERVISION_CHARTER.md` section 3 check 4 for these, and the drafting lane\n"
        "does not claim it. **Enqueueing is not authorisation**\n"
        "(`QUEUE_ENTRY_STANDARD.md` section 1).\n\n"
        "Regenerate after the freeze:\n\n"
        "    python3 make_queue_entries_m1.py --prereg-commit <40-hex> \\\n"
        "        --enqueued-by <who>\n")
    print(f"wrote {n} entries to {a.out}")
    print(f"  estimate {tot_est:.1f} core-min  ({tot_est / 60:.2f} core-h)")
    print(f"  cap      {tot_cap:.1f} core-min  ({tot_cap / 60:.2f} core-h)")
    print(f"  prereg_commit = {a.prereg_commit}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
