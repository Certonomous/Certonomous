#!/usr/bin/env python3
"""write_monitor_tsv.py -- freeze each case's in-pass monitor series into a
committable file.  F14 rung K0c-T.

    python3 write_monitor_tsv.py

WHY THIS EXISTS.  The convergence verdict on this rung is a PEAK-TO-PEAK SPREAD
over the last 400 outer iterations of the series the RUNNING SOLVER printed --
`docs/physics_rules.yaml` thermal block.  Those series live in
`<case>/postProcessing/`, and the repository's `.gitignore` carries a blanket
`**/postProcessing/` rule, so the committed archive of the LAMINAR rung shows no
series at all.  A peak-to-peak spread quoted against a series a reader cannot
open is a number with no evidence behind it.

So each case's three monitored quantities are written here as one small TSV:
every sample in the final 400-iteration window (the window the verdict is taken
on), plus the whole history decimated to every 500 iterations so the approach is
visible too.  This file is generated, never hand-edited, and the generator is
committed beside it.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "_a", os.path.join(os.path.dirname(os.path.abspath(__file__)), "analyse_k0ct.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = ["T_lo_c", "T_lo_f", "T_hi_c", "T_hi_f", "M_hi_f_LS",
         "C1_hi_c_laminar", "C2_hi_c_Ra130", "B_hi_c_adiabatic", "S_hi_c_seed100"]
WINDOW = 400
DECIMATE = 500


def main():
    for c in CASES:
        case = os.path.join(HERE, c)
        dT = float(A.case_txt(case, "dT").split()[0])
        hot = dict(A.series(case, "hotFlux", 1))
        uy = dict(A.series(case, "Uymax", 2))
        probes = [dict(A.series(case, "coreT", 1 + i)) for i in range(len(A.PROBE_YH))]
        its = sorted(set(hot) & set(uy) & set.intersection(*[set(p) for p in probes]))
        last = its[-1]
        keep = [i for i in its if i > last - WINDOW - 1e-9 or i % DECIMATE == 0]
        with open(os.path.join(case, "MONITOR.tsv"), "w") as fh:
            fh.write(f"# {c}: in-pass monitor series, written by write_monitor_tsv.py\n")
            fh.write(f"# every sample in the final {WINDOW}-iteration window (the window the\n")
            fh.write(f"# convergence verdict is taken on) plus the history every {DECIMATE} iterations\n")
            fh.write("# S = least-squares d(theta)/d(y/H) over the five mid-width probes at\n")
            fh.write(f"#     y/H = {A.PROBE_YH}, theta = (T - T_cold)/dT, dT = {dT} K\n")
            fh.write("iteration\thotWall_int_snGradT\tS\tUy_max_m_per_s\tin_final_window\n")
            for i in keep:
                S = A.least_squares_slope(list(A.PROBE_YH),
                                          [p[i] for p in probes]) / dT
                fh.write(f"{int(i)}\t{hot[i]:.9e}\t{S:.9f}\t{uy[i]:.9e}\t"
                         f"{'yes' if i > last - WINDOW - 1e-9 else 'no'}\n")
        print(f"{c:<18} {len(keep):>5} rows, last iteration {int(last)}")


if __name__ == "__main__":
    main()
