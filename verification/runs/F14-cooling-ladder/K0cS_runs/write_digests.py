#!/usr/bin/env python3
"""write_digests.py -- distil each K0cS case into committable artefacts.

    python3 write_digests.py

Writes per case:
  LOG_DIGEST.txt   solver log reduced to its header, its counts, its sha256
                   and its tail.  The raw logs run to 11 MB each and are not
                   committed; the digest carries the sha256 so the raw log a
                   re-run produces can be compared against the one that was
                   graded.
  MONITOR.tsv      the in-pass series the convergence verdict is taken on:
                   every sample in the final 400-iteration window, plus the
                   history every 500 iterations.

Same division K0cT_runs made, for the same reason: a run tree that commits
gigabytes is a run tree nobody clones, and one that commits nothing cannot be
audited.
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = ["S_SST_c", "S_SST_f", "S_KE_c", "S_KE_f", "S_LS_c", "S_LS_f",
         "C1_laminar", "C2_seed_d100", "C3_prt128", "C4_adiabatic"]
WINDOW = 400


def series(case_dir, sub, col):
    root = os.path.join(case_dir, "postProcessing", sub)
    if not os.path.isdir(root):
        return {}
    out = {}
    for d in os.listdir(root):
        for fn in os.listdir(os.path.join(root, d)):
            for line in open(os.path.join(root, d, fn)):
                if line.startswith("#"):
                    continue
                p = line.split()
                if len(p) > col:
                    try:
                        out[int(float(p[0]))] = float(p[col])
                    except ValueError:
                        pass
    return out


def main():
    for c in CASES:
        d = os.path.join(HERE, c)
        log = os.path.join(d, "log.solve")
        if not os.path.isfile(log):
            print(f"  {c}: no log.solve, skipped")
            continue
        raw = open(log, "rb").read()
        txt = raw.decode("utf8", "replace")
        iters = txt.count("\nTime = ")
        sha = hashlib.sha256(raw).hexdigest()
        head = txt[:txt.index("\nTime = ")] if "\nTime = " in txt else txt[:4000]
        tail = txt[-3000:]
        with open(os.path.join(d, "LOG_DIGEST.txt"), "w") as fh:
            fh.write(f"LOG_DIGEST for K0cS case {c}\n")
            fh.write("written by write_digests.py; the raw log.solve is NOT "
                     "committed (it is 5-11 MB per case)\n")
            fh.write("=" * 78 + "\n")
            fh.write(f"  bytes                   {len(raw)}\n")
            fh.write(f"  sha256                  {sha}\n")
            fh.write(f"  outer iterations        {iters}\n")
            for f in ("Ux", "Uy", "T", "k", "omega", "epsilon"):
                fh.write(f"  solves for {f:<12} {txt.count('Solving for ' + f)}\n")
            fh.write("=" * 78 + "\n")
            fh.write("HEADER, VERBATIM\n" + "-" * 78 + "\n")
            fh.write(head + "\n")
            fh.write("-" * 78 + "\nTAIL, VERBATIM (last 3000 chars)\n"
                     + "-" * 78 + "\n" + tail + "\n")

        hot = series(d, "hotFlux", 1)
        umax = series(d, "Uymax", 2)
        if hot:
            last = max(hot)
            with open(os.path.join(d, "MONITOR.tsv"), "w") as fh:
                fh.write(f"# {c}: in-pass monitor series, written by "
                         "write_digests.py\n")
                fh.write(f"# every sample in the final {WINDOW}-iteration "
                         "window (the window the convergence\n")
                fh.write("# verdict is taken on) plus the history every 500 "
                         "iterations\n")
                fh.write("# hotWall_int_snGradT is the areaNormalIntegrate of "
                         "grad(T) over the hot wall\n")
                fh.write("iteration\thotWall_int_snGradT\tUy_max_m_per_s\t"
                         "in_final_window\n")
                for it in sorted(hot):
                    inw = it >= last - WINDOW
                    if not inw and it % 500 != 0:
                        continue
                    fh.write(f"{it}\t{hot[it]:.9e}\t"
                             f"{umax.get(it, float('nan')):.9e}\t"
                             f"{'yes' if inw else 'no'}\n")
        print(f"  {c}: {iters} iterations, log {len(raw)/1e6:.1f} MB -> digest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
