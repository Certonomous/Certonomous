#!/usr/bin/env python3
"""R4 - the a-posteriori verification table of PREREGISTRATION sec. 6.

Per training family, for each of NULL / CEILING / DISCOVERED:

  * eps(U)/eps(U_0) against the frozen-field ceiling COMPUTED PER CASE IN THIS
    LANE (sec. 6 -- the ceiling is measured here, not quoted).  Registered
    gate eps(U)/eps(U_0) <= 0.6 on PHLL10595 and CBFS13700.
    eps(U) = mean_c |U_c - U_LES,c|^2 over the 3 components, unweighted over
    the whole internal field -- the W2 primary convention, and eps(U_0) is the
    same quantity on the shipped baseline field.
  * continuity: `sum local` from the solver log's last time step, registered
    <= 1e-4 else NOT CONVERGED whatever the velocity error.
  * realisability of the TOTAL tau at tol = 1e-6, beside the truth's own rate.
  * structure: duct secondary-flow magnitude as % of bulk, and reattachment on
    the hills and CBFS13700 against the LES.
  * iteration counts and stagnation state per configuration, with BOTH
    comparators -- NULL (zero correction, same solver and stopping rule) and
    the shipped BASE -- and NULL - BASE named (N-B22, N-B23).

NOT A RESULT fires per sec. 6 where the per-case ceiling fails to beat NULL
by 30%.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_common"))
import r4_lib as R
from of_read import read_field, sym_to_full, realisability_violation, \
    structured_gradient

WORK = os.path.join(R.WORK, "aposteriori")
CFGS = ["null", "ceiling", "discovered"]
GATE_RATIO = 0.6
GATE_CONTINUITY = 1e-4
CEILING_MUST_BEAT_NULL_BY = 0.30


def eps_U(U, ULES):
    return float(((U - ULES) ** 2).sum(axis=1).mean())


def log_facts(case_dir):
    """Iteration count, convergence state and the last `sum local` continuity."""
    logs = [f for f in os.listdir(case_dir) if f.startswith("log.")]
    if not logs:
        return dict(status="no log")
    txt = open(os.path.join(case_dir, sorted(logs)[-1]), errors="replace").read()
    times = re.findall(r"^Time = (\d+)", txt, flags=re.M)
    cont = re.findall(r"sum local = ([0-9.eE+-]+), global", txt)
    conv = "SIMPLE solution converged" in txt
    ended = bool(re.search(r"^End\s*$", txt, flags=re.M))
    ur = re.findall(r"Solving for Ux, Initial residual = ([0-9.eE+-]+)", txt)
    return dict(iterations=int(times[-1]) if times else 0,
                converged_by_residual_control=conv, end_line=ended,
                continuity_sum_local_last=float(cont[-1]) if cont else None,
                continuity_sum_local_max=(max(float(c) for c in cont[-50:])
                                          if cont else None),
                Ux_initial_residual_last=float(ur[-1]) if ur else None,
                stagnated=bool(times and not conv and ended))


def realisability(tdir, k=None):
    """Violating-cell fraction of the TOTAL Reynolds stress anisotropy."""
    p = os.path.join(tdir, "tauij")
    if os.path.exists(p):
        tau = sym_to_full(read_field(p))
        kk = 0.5 * np.trace(tau, axis1=1, axis2=2)
    else:
        U = read_field(os.path.join(tdir, "U"))
        kk = read_field(os.path.join(tdir, "k")).ravel()
        nut = read_field(os.path.join(tdir, "nut")).ravel()
        C = None
        return None
    ok = kk > 0
    b = np.full((tau.shape[0], 3, 3), np.nan)
    b[ok] = tau[ok] / (2 * kk[ok, None, None]) - np.eye(3)[None] / 3.0
    v, _ = realisability_violation(b[ok], tol=1e-6)
    return dict(n=int(ok.sum()), violating_fraction=float(v.mean()))


def secondary_flow_pct(U, axis=0):
    """Duct structure metric: RMS in-plane velocity as % of the bulk."""
    bulk = float(np.abs(U[:, axis]).mean())
    ip = np.delete(np.arange(3), axis)
    return float(100.0 * np.sqrt((U[:, ip] ** 2).sum(axis=1).mean()) / bulk)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cases = a.cases.split(",")
    R.assert_no_test_case(cases)
    byname = {c: (p, f) for c, p, f in R.training_cases()}
    # CLAUDE.md standing rule 3 - the reader is shown a known non-zero before
    # any zero it reports is treated as evidence.  Refuses (exit 2) on failure.
    pz_reader = R.planted_zero_reader_check(
        os.path.join(byname[cases[0]][0], R.latest_time(byname[cases[0]][0]),
                     "U"),
        read_field, os.path.join(R.WORK, "_plant", "U"))
    res = {}
    for case in cases:
        src, family = byname[case]
        t0 = R.latest_time(src)
        ULES = read_field(os.path.join(src, "0", "U_LES"))
        if ULES.shape[1] != 3:
            ULES = ULES.reshape(-1, 3)
        Ubase = read_field(os.path.join(src, t0, "U"))
        e0 = eps_U(Ubase, ULES)
        truth_b = None
        row = dict(family=family, n_cells=int(ULES.shape[0]),
                   eps_U_shipped_BASE=e0, configs={})
        for cfg in CFGS:
            cd = os.path.join(WORK, case, cfg)
            ok, why, info = R.solve_complete(cd)
            lf = log_facts(cd) if os.path.isdir(cd) else {}
            entry = dict(complete=ok, completion_reason=why,
                         stop_state=info.get("stop_state"), **lf)
            if os.path.isdir(cd):
                lt = R.latest_time(cd)
                td = os.path.join(cd, lt)
                if os.path.exists(os.path.join(td, "U")):
                    U = read_field(os.path.join(td, "U"))
                    e = eps_U(U, ULES)
                    entry["eps_U"] = e
                    entry["eps_U_over_BASE"] = e / e0
                    if family == "ducts":
                        entry["secondary_flow_pct_of_bulk"] = \
                            secondary_flow_pct(U)
                    entry["last_time"] = lt
            row["configs"][cfg] = entry
        n = row["configs"]["null"].get("eps_U")
        c = row["configs"]["ceiling"].get("eps_U")
        d = row["configs"]["discovered"].get("eps_U")
        if n and c:
            row["ceiling_over_null"] = c / n
            row["ceiling_beats_null_by_30pct"] = (c / n) <= (
                1.0 - CEILING_MUST_BEAT_NULL_BY)
        if d and n:
            row["discovered_over_null"] = d / n
        if d and c:
            row["discovered_over_ceiling"] = d / c
        if n:
            row["N_minus_B_eps_U"] = n - e0
            row["N_over_B_eps_U"] = n / e0
        if family == "ducts":
            row["secondary_flow_pct_LES"] = secondary_flow_pct(ULES)
        res[case] = row
    json.dump(dict(gate_ratio=GATE_RATIO, gate_continuity=GATE_CONTINUITY,
                   ceiling_must_beat_null_by=CEILING_MUST_BEAT_NULL_BY,
                   planted_zero_reader_control=pz_reader,
                   cases=res), open(a.out, "w"), indent=1)
    hdr = f"{'case':22s} {'cfg':11s} {'it':>6s} {'eps(U)':>12s} {'/BASE':>9s} {'sumlocal':>10s} {'state':>10s}"
    print(hdr)
    for case, row in res.items():
        for cfg in CFGS:
            e = row["configs"][cfg]
            print(f"{case:22s} {cfg:11s} {str(e.get('iterations','-')):>6s} "
                  f"{e.get('eps_U', float('nan')):12.6g} "
                  f"{e.get('eps_U_over_BASE', float('nan')):9.4f} "
                  f"{str(e.get('continuity_sum_local_last','-')):>10s} "
                  f"{'CONV' if e.get('converged_by_residual_control') else ('STAG' if e.get('stagnated') else '-'):>10s}")
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
