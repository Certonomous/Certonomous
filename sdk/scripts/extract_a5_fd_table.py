"""Extract the full per-component check_totals tables from OpenMDAO logs.

`check_totals` prints an aggregate norm AND, under `compact_print=False`, the
raw analytic and FD Jacobian rows. The lab's published A5 27-component table
was built from those rows. The patched counterpart has been sitting in
`W5-regrade/a5pl_patched_checktotals.log` since 2026-08-01 with only its
aggregate (2.2372%) ever read.

Usage:
    python3 extract_a5_fd_table.py <log> [<log> ...]

Prints, per (of, wrt) pair, the analytic and FD vectors and the per-component
relative error and sign agreement, and emits JSON on request via --json.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BLOCK = re.compile(
    r"Full Model: '(?P<of>[^']+)' wrt '(?P<wrt>[^']+)'\s*\n"
    r"\s*Analytic Magnitude:\s*(?P<anmag>[0-9.eE+-]+)\s*\n"
    r"\s*Fd Magnitude:\s*(?P<fdmag>[0-9.eE+-]+)[^\n]*\n"
    r"(?P<mid>.*?)"
    r"Raw Analytic Derivative \(Jfor\)\s*\n(?P<an>\[\[.*?\]\])\s*\n"
    r"\s*Raw FD Derivative \(Jfd\)\s*\n(?P<fd>\[\[.*?\]\])",
    re.S)
RELERR = re.compile(r"Relative Error \(Jan - Jfd\) / Jfd :\s*([0-9.eE+-]+)")
RANK = re.compile(r"MPI Rank (\d+)")


def _vec(text: str) -> list[float]:
    return [float(t) for t in re.findall(r"-?\d+\.\d+(?:[eE][+-]?\d+)?", text)]


def parse(path: Path) -> list[dict]:
    text = path.read_text(errors="replace")
    seen: dict[tuple[str, str], dict] = {}
    for m in BLOCK.finditer(text):
        key = (m.group("of"), m.group("wrt"))
        rank_m = RANK.search(m.group("mid"))
        rec = {
            "log": str(path), "of": key[0], "wrt": key[1],
            "analytic_magnitude": float(m.group("anmag")),
            "fd_magnitude": float(m.group("fdmag")),
            "aggregate_rel_err": (lambda r: float(r.group(1)) if r else None)(
                RELERR.search(m.group("mid"))),
            "mpi_rank": int(rank_m.group(1)) if rank_m else None,
            "analytic": _vec(m.group("an")),
            "fd": _vec(m.group("fd")),
        }
        # every rank prints the same rows; keep the first and assert agreement
        if key in seen:
            prev = seen[key]
            if prev["analytic"] != rec["analytic"] or prev["fd"] != rec["fd"]:
                rec["RANK_DISAGREEMENT"] = True
                seen[key] = rec
            continue
        seen[key] = rec
    return list(seen.values())


def grade(rec: dict, band_pct: float = 12.0) -> dict:
    rows = []
    for i, (a, f) in enumerate(zip(rec["analytic"], rec["fd"])):
        # An exactly-zero pair is agreement, not an infinite error. These occur
        # in the geometric-constraint rows, where whole DV columns are
        # structurally zero; scoring them 'inf' understates the pass count.
        if f == 0.0 and a == 0.0:
            rel = 0.0
        elif f == 0.0:
            rel = float("inf")
        else:
            rel = abs(a - f) / abs(f) * 100.0
        rows.append({"idx": i, "analytic": a, "fd": f, "rel_err_pct": rel,
                     "sign_match": (a > 0) == (f > 0),
                     "in_band": rel <= band_pct})
    rec["components"] = rows
    rec["n"] = len(rows)
    rec["n_in_band"] = sum(r["in_band"] for r in rows)
    rec["n_sign_flip"] = sum(not r["sign_match"] for r in rows)
    rec["worst"] = max(rows, key=lambda r: r["rel_err_pct"]) if rows else None
    rec["band_pct"] = band_pct
    return rec


def main(argv: list[str]) -> int:
    want_json = "--json" in argv
    paths = [Path(a) for a in argv if not a.startswith("--")]
    out = []
    for p in paths:
        for rec in parse(p):
            grade(rec)
            out.append(rec)
            if want_json:
                continue
            print("=" * 78)
            print(f"{p.name}   {rec['of']} wrt {rec['wrt']}   "
                  f"(rank {rec['mpi_rank']}, n={rec['n']})")
            print(f"  analytic magnitude {rec['analytic_magnitude']:.6e}   "
                  f"fd magnitude {rec['fd_magnitude']:.6e}   "
                  f"aggregate rel err {rec['aggregate_rel_err']}")
            print(f"  {rec['n_in_band']}/{rec['n']} within +/-{rec['band_pct']}%, "
                  f"{rec['n_sign_flip']} sign flip(s)")
            print(f"  {'idx':>4} {'analytic':>16} {'fd':>16} {'rel %':>12}  sign")
            for r in rec["components"]:
                print(f"  {r['idx']:>4} {r['analytic']:>16.8f} {r['fd']:>16.8f} "
                      f"{r['rel_err_pct']:>12.4f}  {'yes' if r['sign_match'] else 'NO'}")
    if want_json:
        print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
