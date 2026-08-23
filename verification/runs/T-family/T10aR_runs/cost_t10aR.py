#!/usr/bin/env python3
"""
T10a-R cost, actual vs the pre-registered prediction.

UNIT: core-minutes = wall_s * ranks / 60 (CLAUDE.md standing rule 12).  Every
case here is serial (ranks = 1), so core-seconds == WALL seconds, contention
included -- the same convention T10a_RESULTS.md section 8 used ("walls from
STATUS.* include contention from concurrent rungs").  CPU-share is reported
beside it because this lane ran nice 15 behind 12 nice-0/10 solvers from other
rungs and got 12-26 % of a core, but the wall figure is the one that counts.

Rate 0.0513 USD/core-h, owner-stated by Sanaa (CLAUDE.md rule 12): this is
reported-by-owner, NOT measured -- the box cannot read its own billing.
"""
import os
import re
import sys

D = os.path.dirname(os.path.abspath(__file__))
USD_PER_CORE_H = 0.0513
# from T10aR_PREREGISTRATION.md section 4, as registered
PRED = {"R_x": {"prep": 405, "solve": 7013}, "R_q": {"prep": 80, "solve": 389},
        "R_s": {"prep": 55, "solve": 700}}
PRED_TOTAL = sum(v["prep"] + v["solve"] for v in PRED.values())
STOP = 10 * PRED_TOTAL


def num(txt, pat, default=None):
    m = re.search(pat, txt)
    return float(m.group(1)) if m else default


def main():
    rows, total = [], 0.0
    for c in ("R_q", "R_s", "R_x"):
        bp = os.path.join(D, c, "BUILD.txt")
        sp = os.path.join(D, f"STATUS.{c}")
        if not os.path.isfile(bp):
            rows.append((c, None, None, None, "no BUILD.txt"))
            continue
        b = open(bp).read()
        prep = (num(b, r"blockMesh_rc\s+\d+\s+wall\s+([\d.]+)", 0)
                + num(b, r"checkMesh_rc\s+\d+\s+wall\s+([\d.]+)", 0)
                + num(b, r"viewFactorsGen_rc\s+\d+\s+wall\s+([\d.]+)", 0))
        prss = num(b, r"maxRSS_kB\s+(\d+)", 0) / 1048576
        if os.path.isfile(sp):
            s = open(sp).read()
            solve = num(s, r"wall=(\d+)", 0)
            srss = num(s, r"maxRSS_kB=(\d+)", 0) / 1048576
            note = "" if num(s, r"rc=(\d+)") == 0 else "rc != 0"
        else:
            solve, srss, note = None, 0.0, "PENDING (no STATUS)"
        rows.append((c, prep, solve, max(prss, srss), note))
        total += prep + (solve or 0)

    print(f"{'case':5s} {'prep s':>8s} {'solve s':>9s} {'total s':>9s} "
          f"{'pred s':>8s} {'x pred':>7s} {'peak GB':>8s}  note")
    for c, prep, solve, rss, note in rows:
        if prep is None:
            print(f"{c:5s} {'-':>8s} {'-':>9s} {'-':>9s} "
                  f"{PRED[c]['prep']+PRED[c]['solve']:8.0f} {'-':>7s} {'-':>8s}  {note}")
            continue
        t = prep + (solve or 0)
        p = PRED[c]["prep"] + PRED[c]["solve"]
        print(f"{c:5s} {prep:8.0f} {solve if solve is not None else -1:9.0f} "
              f"{t:9.0f} {p:8.0f} {t/p:7.2f} {rss:8.2f}  {note}")

    done = all(r[2] is not None for r in rows if r[1] is not None) and len(rows) == 3
    print(f"\nTOTAL SO FAR   {total:9.0f} core-s = {total/60:8.2f} core-min = "
          f"{total/3600:.3f} core-h = ${total/3600*USD_PER_CORE_H:.4f}")
    print(f"PREDICTED      {PRED_TOTAL:9.0f} core-s = {PRED_TOTAL/60:8.2f} core-min = "
          f"{PRED_TOTAL/3600:.3f} core-h = ${PRED_TOTAL/3600*USD_PER_CORE_H:.4f}")
    print(f"ratio          {total/PRED_TOTAL:9.2f} x")
    print(f"STOP THRESHOLD {STOP:9.0f} core-s = {STOP/3600:.1f} core-h = "
          f"${STOP/3600*USD_PER_CORE_H:.2f}  (10x, registered)")
    over = total > STOP
    print(f"\n{'*** OVER THE REGISTERED STOP THRESHOLD -- STOP THE RUN ***' if over else 'within the registered stop threshold'}"
          f"{'' if done else '   [INCOMPLETE: some case still running]'}")
    print("\nRate 0.0513 USD/core-h is OWNER-STATED (Sanaa), not measured: the box "
          "cannot read its\nown billing (COMPUTE_BUDGET_CHARTER section 5).  "
          "cost_basis = reported-by-owner.")
    return 2 if over else 0


if __name__ == "__main__":
    sys.exit(main())
