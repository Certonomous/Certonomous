#!/usr/bin/env python3
"""P(rank 1) for the closure-challenge entry of record, by case-level bootstrap.

WHY THIS FILE EXISTS
--------------------
`campaign/PROBABILITY_OF_RANK_2026-08-10.md` computed P(rank 1) = 68% against a
FOUR-entry leaderboard and shipped no script, so when the board moved to six
entries on 2026-08-11 the figure could not be refreshed without re-deriving the
method from prose. It is re-derived here once, and committed, so the next board
move costs one fetch and one command.

WHAT IT DOES AND DOES NOT TOUCH
-------------------------------
* **Zero scoring calls. Zero solver.** It reads numbers already on disk and a
  board table typed into (or passed to) it. It never imports the eval package,
  never reads ground truth, and never writes to the scoring-call ledger.
* **It does not move the frozen benchmark pin.** `~/closure-challenge-benchmark`
  is pinned at `deb9155` because rung V1 needs a frozen SCORING reference. That
  clone scores; it does not rank. Board numbers for ranking come from the LIVE
  README, fetched, with the fetch time recorded — see `--board`.

USAGE
-----
    python3 sdk/scripts/probability_of_rank.py                 # live six-entry board (2026-08-11)
    python3 sdk/scripts/probability_of_rank.py --control       # positive control: the four-entry board
    python3 sdk/scripts/probability_of_rank.py --board b.json  # a freshly fetched board

`--board` takes JSON of the shape
    {"fetched": "<ISO8601 UTC>", "source": "<url>",
     "entrants": {"<name>": [c1, ..., c8], ...}}
with the eight per-case values in the order of CASES below. **State the fetch
time wherever the output is quoted**: a probability of rank is a claim about a
board at a moment, and the 2026-08-11 incident is what happens when it is not.

REFRESHING AFTER A BOARD MOVE
-----------------------------
    curl -sS https://raw.githubusercontent.com/rmcconke/closure-challenge-benchmark/main/README.md
then transcribe the leaderboard table into a --board file, run, and check that
section 0's reproduction check still passes for every row. If a row's eight
per-case values do not average to its published overall, do NOT proceed: the
transcription is wrong, or the board's columns have changed and the scores are
no longer like-for-like.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[2]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

CASES = [
    "alpha_15_13929_4048", "alpha_15_13929_2024", "alpha_05_4071_4048",
    "alpha_05_4071_2024", "AR_1_Ret_360", "AR_3_Ret_360",
    "AR_14_Ret_180", "NASA_2DWMH",
]

# The three cases whose predictions come from the one-seed PH model. The
# truth-free seed-spread bound on the overall is 0.0024
# (closure_challenge_stability_physicality_audit.md section 1).
SEED_DEPENDENT = [0, 1, 7]
SEED_BOUND_ON_OVERALL = 0.0024

# Our entry of record. Read from the scoring call's own machine record rather
# than transcribed, so it cannot drift from it.
OUR_RECORD = str(lab_paths.web_file("closure_challenge_round5_qcr.json"))

# The LIVE board, fetched 2026-08-11T23:33Z from
# raw.githubusercontent.com/rmcconke/closure-challenge-benchmark/main/README.md
# (sha256 1f124a8857a6b611832478879fc22ff353ee3308434b966849d4f29946d85c5b) and
# corroborated by a second fetch of the rendered project page. Recorded in
# campaign/BOARD_MOVED_2026-08-11.md.
LIVE_BOARD = {
    "fetched": "2026-08-11T23:33Z",
    "source": "raw.githubusercontent.com/rmcconke/closure-challenge-benchmark/main/README.md",
    "entrants": {
        "Yang":                            [0.0806, 0.1229, 0.0645, 0.0748, 0.0291, 0.0311, 0.0250, 0.0361],
        "Reissmann, Fang & Sandberg":      [0.0592, 0.1339, 0.0606, 0.0760, 0.0387, 0.0341, 0.0325, 0.0412],
        "Wu & Zhang":                      [0.0813, 0.1195, 0.0569, 0.0848, 0.0455, 0.0399, 0.0350, 0.0364],
        "Tian, Buchanan, Hickel & Dwight": [0.0432, 0.0998, 0.0744, 0.0960, 0.0623, 0.0553, 0.0527, 0.0294],
        "Liu, Wang, Zhao & Xiao":          [0.0600, 0.1308, 0.0613, 0.0769, 0.0875, 0.0805, 0.0548, 0.0377],
        "Montoya, Oulghelou & Cinnella":   [0.0680, 0.1364, 0.0591, 0.0882, 0.0895, 0.0866, 0.0487, 0.0464],
    },
    "published_overall": {
        "Yang": 0.0580, "Reissmann, Fang & Sandberg": 0.0595, "Wu & Zhang": 0.0624,
        "Tian, Buchanan, Hickel & Dwight": 0.0641, "Liu, Wang, Zhao & Xiao": 0.0737,
        "Montoya, Oulghelou & Cinnella": 0.0779,
    },
}

# The board as it stood when P(rank 1) = 68% was computed. Kept ONLY as the
# positive control that proves this script's method is the method that produced
# that figure. It is not a current statement about the world: two entrants are
# missing from it, one of them the leader.
CONTROL_BOARD_2026_08_10 = {
    "fetched": "board as read at benchmark commit deb91557 (2026-05-04) — SUPERSEDED, four entries",
    "source": "closure_eval/closure_eval_master_table.md section A",
    "entrants": {k: v for k, v in LIVE_BOARD["entrants"].items()
                 if k not in ("Yang", "Tian, Buchanan, Hickel & Dwight")},
    "published_overall": {k: v for k, v in LIVE_BOARD["published_overall"].items()
                          if k not in ("Yang", "Tian, Buchanan, Hickel & Dwight")},
}

B_MAIN, SEED_MAIN = 400_000, 20260810
N_OUTER, N_INNER, SEED_DOUBLE = 2_000, 4_000, 31415

# "Decided" means all three hold. Stated here so it can be argued with rather
# than inferred from the prose of whichever document quotes the output.
DECIDED_P, DECIDED_T, DECIDED_WINS = 0.98, 2.0, 7


def our_per_case(path: str = OUR_RECORD) -> np.ndarray:
    with open(path) as fh:
        rec = json.load(fh)["official_test_harness_result"]
    full = rec["round5_per_case_full"]
    vals = np.array([full[c] for c in CASES])
    stated = rec["round5_overall_full"]
    if abs(vals.mean() - stated) > 1e-12:
        raise SystemExit(
            f"our own record is internally inconsistent: the eight per-case values mean "
            f"{vals.mean()!r} but round5_overall_full says {stated!r}. Refusing to compute."
        )
    return vals


def wilson(p: float, n: int, z: float = 1.959963985) -> tuple[float, float]:
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return centre - half, centre + half


def p_rank1(ours: np.ndarray, others: np.ndarray, idx: np.ndarray) -> float:
    """Fraction of resamples in which no entrant's resampled mean is below ours."""
    ours_bs = ours[idx].mean(axis=1)
    oth_bs = others[:, idx].mean(axis=2)
    return float(((oth_bs < ours_bs[None, :]).sum(axis=0) == 0).mean())


def run(board: dict, ours: np.ndarray) -> dict:
    names = list(board["entrants"])
    OTH = np.array([board["entrants"][n] for n in names])
    pub = board.get("published_overall", {})
    out: dict = {"frame": {"fetched": board.get("fetched"), "source": board.get("source"),
                           "entries": len(names), "cases": len(CASES), "B": B_MAIN,
                           "seed": SEED_MAIN, "our_overall": float(ours.mean())}}

    print("=== 0. reproduction check: mean of the 8 published per-case values vs published overall ===")
    ok = True
    for n in names:
        m = float(np.mean(board["entrants"][n]))
        if n in pub:
            good = abs(round(m, 4) - pub[n]) < 5e-7
            ok &= good
            print(f"  {n:34s} mean={m:.6f}  published={pub[n]:.4f}  {'OK' if good else '*** MISMATCH ***'}")
        else:
            print(f"  {n:34s} mean={m:.6f}  (no published overall given)")
    if not ok:
        print("  REFUSING TO CONTINUE: a transcribed row does not reproduce its own published overall.")
        raise SystemExit(2)
    print(f"  {'ours (full precision, from record)':34s} mean={ours.mean():.15f}")

    print(f"\n=== 1. point standing ({len(names)} entries, board fetched {board.get('fetched')}) ===")
    for n in sorted(names, key=lambda k: np.mean(board["entrants"][k])):
        print(f"  {n:34s} {np.mean(board['entrants'][n]):.6f}   our margin {ours.mean()-np.mean(board['entrants'][n]):+.6f}")
    leader = min(names, key=lambda k: np.mean(board["entrants"][k]))
    point_rank = 1 + sum(np.mean(board["entrants"][n]) < ours.mean() for n in names)
    print(f"  ours {ours.mean():.6f}  ->  POINT RANK {point_rank}; leader is {leader}")
    out["point_rank"], out["leader"] = int(point_rank), leader

    rng = np.random.default_rng(SEED_MAIN)
    idx = rng.integers(0, len(CASES), size=(B_MAIN, len(CASES)))
    ours_bs = ours[idx].mean(axis=1)
    oth_bs = OTH[:, idx].mean(axis=2)
    rank = 1 + (oth_bs < ours_bs[None, :]).sum(axis=0)
    p1 = float((rank == 1).mean())
    lo, hi = wilson(p1, B_MAIN)
    print(f"\n=== 2. rank distribution, B={B_MAIN:,}, seed {SEED_MAIN} ===")
    for r in range(1, len(names) + 2):
        c = int((rank == r).sum())
        if c:
            print(f"  rank {r}: {100*c/B_MAIN:6.2f}%")
    print(f"  P(rank 1) = {100*p1:.1f}%   Monte-Carlo Wilson 95%: {100*lo:.2f}% - {100*hi:.2f}%")
    print("  (the Monte-Carlo interval says only that the resampling ran long enough. It is")
    print("   NOT an uncertainty about the world; the double bootstrap in section 5 is.)")
    out["p_rank1"], out["mc_wilson95"] = p1, [lo, hi]

    print("\n=== 3. pairwise, and which comparisons are decided ===")
    out["pairwise"] = {}
    for i, n in enumerate(names):
        d = ours - OTH[i]
        t = float(d.mean() / (d.std(ddof=1) / math.sqrt(len(CASES))))
        plead = float((ours_bs < oth_bs[i]).mean())
        wins = int((d < 0).sum())
        decided = plead >= DECIDED_P and abs(t) > DECIDED_T and wins >= DECIDED_WINS
        out["pairwise"][n] = {"overall": float(np.mean(board["entrants"][n])),
                              "margin": float(ours.mean() - np.mean(board["entrants"][n])),
                              "p_we_lead": plead, "t": t, "sd": float(d.std(ddof=1)),
                              "cases_won": wins, "decided": decided}
        print(f"  {n:34s} margin {ours.mean()-np.mean(board['entrants'][n]):+.6f}  P(we lead) {100*plead:5.1f}%  "
              f"t={t:+.3f}  sd={d.std(ddof=1):.6f}  won {wins}/8  "
              f"{'DECIDED' if decided else '** NOT STATISTICALLY DECIDED **'}")

    print(f"\n=== 4. leave-one-case-out (7-case bootstrap, B={B_MAIN:,}) ===")
    rng2 = np.random.default_rng(SEED_MAIN)
    out["loo"] = {}
    for k in range(len(CASES)):
        keep = [j for j in range(len(CASES)) if j != k]
        o7, O7 = ours[keep], OTH[:, keep]
        pr = 1 + sum(O7[i].mean() < o7.mean() for i in range(len(names)))
        p = p_rank1(o7, O7, rng2.integers(0, 7, size=(B_MAIN, 7)))
        marg = float(o7.mean() - O7[names.index(leader)].mean())
        out["loo"][CASES[k]] = {"point_rank": int(pr), "p_rank1": p, "margin_vs_leader": marg}
        print(f"  drop {CASES[k]:22s} margin vs leader {marg:+.6f}  point rank {pr}  P(rank 1) {100*p:5.1f}%")

    print(f"\n=== 5. double bootstrap, {N_OUTER:,} outer x {N_INNER:,} inner, seed {SEED_DOUBLE} ===")
    print("     THIS is the interval that must ship with the figure.")
    rng3 = np.random.default_rng(SEED_DOUBLE)
    outer = rng3.integers(0, len(CASES), size=(N_OUTER, len(CASES)))
    ps = np.empty(N_OUTER)
    for b in range(N_OUTER):
        ps[b] = p_rank1(ours[outer[b]], OTH[:, outer[b]],
                        rng3.integers(0, len(CASES), size=(N_INNER, len(CASES))))
    for lvl, q in (("68%", (16, 84)), ("95%", (2.5, 97.5))):
        a, b_ = np.percentile(ps, q)
        out[f"double{lvl.rstrip('%')}"] = [float(a), float(b_)]
        print(f"  {lvl} band: {100*a:.1f}% - {100*b_:.1f}%")
    print(f"  outer resamples giving P(rank 1) exactly 0: {100*float((ps == 0).mean()):.2f}%")

    print(f"\n=== 6. seed-spread bound +/-{SEED_BOUND_ON_OVERALL} on the overall, loaded on the 3 seed-dependent cases ===")
    out["seed"] = {}
    for lab, sgn in (("adverse", +1), ("as scored", 0), ("favourable", -1)):
        o = ours.copy()
        o[SEED_DEPENDENT] += sgn * SEED_BOUND_ON_OVERALL * len(CASES) / len(SEED_DEPENDENT)
        p = p_rank1(o, OTH, idx)
        pr = 1 + sum(np.mean(board["entrants"][n]) < o.mean() for n in names)
        out["seed"][lab] = {"overall": float(o.mean()), "p_rank1": p, "point_rank": int(pr)}
        print(f"  {lab:12s} overall {o.mean():.6f}  point rank {pr}  P(rank 1) {100*p:5.1f}%")

    print("\n=== 7. the sentence this output licenses ===")
    nd = [n for n, v in out["pairwise"].items() if not v["decided"]]
    dd = [n for n, v in out["pairwise"].items() if v["decided"]]
    lo95, hi95 = out["double95"]
    print(f"  P(rank 1) = {100*p1:.0f}%, which {len(CASES)} cases pin no tighter than "
          f"{100*lo95:.0f}-{100*hi95:.0f}% at 95%.")
    print(f"  NOT statistically decided ({len(nd)}): {'; '.join(nd)}")
    print(f"  Decided ({len(dd)}): {'; '.join(dd) if dd else '(none)'}")
    print(f"  Board: {len(names)} entries, fetched {board.get('fetched')}. Local scoring, "
          f"NOT an official placement; nothing has been submitted.")
    print("  The figure may NEVER be stated without its interval and its board.")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", help="JSON board file (see module docstring)")
    ap.add_argument("--control", action="store_true",
                    help="run the superseded FOUR-entry board as a positive control on the method")
    ap.add_argument("--json", help="write the full result dict here")
    args = ap.parse_args(argv)

    if args.control:
        board = CONTROL_BOARD_2026_08_10
        print("*** POSITIVE CONTROL: the superseded FOUR-entry board. This reproduces the")
        print("*** 2026-08-10 figure and is NOT a current statement about the standings.\n")
    elif args.board:
        with open(args.board) as fh:
            board = json.load(fh)
    else:
        board = LIVE_BOARD

    result = run(board, our_per_case())
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(result, fh, indent=1, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
