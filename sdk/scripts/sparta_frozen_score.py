#!/usr/bin/env python3
"""Score the SpaRTA step-1 reproduction against Table 1 of Schmelzer,
Dwight & Cinnella (2020).

Conventions are pre-registered in
demo-output/website/campaign/W2_SPARTA_PREREGISTRATION.md:
  primary   : unweighted cell mean over the whole internal field;
              eps(U) = mean_c |U_c - U_LES,c|^2 (3 components);
              eps(tau) = mean_c ||tau_c - tau_LES,c||_F^2, Frobenius,
              off-diagonals counted twice.
  secondary : cell-volume-weighted mean, and 6-unique-component tau mean.

All fields are read from solver-written plain-ascii OpenFOAM files (the
frozen driver re-writes the LES fields without #include macros, stepping
around the B2 Ofpp blocker).

Usage:
  sparta_frozen_score.py --les-dir <frozen-out-time-dir> \
      --baseline-u <file> --baseline-tau <file> \
      --recon-u <file> --recon-tau <file> [--volumes <file>] [--json out]
"""

import argparse
import json
import re
import sys

import numpy as np

NCOMP = {"scalar": 1, "vector": 3, "symmTensor": 6}


def read_of_field(path):
    """Read an ascii OpenFOAM volField internalField -> (N, ncomp) array."""
    with open(path) as fh:
        text = fh.read()
    m = re.search(
        r"internalField\s+nonuniform\s+List<(scalar|vector|symmTensor)>\s*"
        r"\n?\s*(\d+)\s*\n\(", text)
    if m is None:
        mu = re.search(
            r"internalField\s+uniform\s+(\(?[^;]+\)?);", text)
        if mu is None:
            raise ValueError(f"no internalField found in {path}")
        raise ValueError(f"uniform internalField in {path}; not supported")
    kind, n = m.group(1), int(m.group(2))
    start = m.end()  # position just after the opening '('
    depth = 1
    i = start
    while depth > 0:
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        i += 1
    body = text[start:i - 1]
    nums = np.array(
        body.replace("(", " ").replace(")", " ").split(), dtype=float)
    nc = NCOMP[kind]
    arr = nums.reshape(n, nc) if nc > 1 else nums.reshape(n, 1)
    return arr


def eps_vector(a, b, w=None):
    """Mean squared error of a vector field, all components summed."""
    d2 = ((a - b) ** 2).sum(axis=1)
    if w is None:
        return float(d2.mean())
    return float((d2 * w).sum() / w.sum())


def eps_symm(a, b, w=None, frobenius=True):
    """MSE of a symmTensor field. OpenFOAM order: xx xy xz yy yz zz."""
    d2 = (a - b) ** 2
    if frobenius:
        weights = np.array([1.0, 2.0, 2.0, 1.0, 2.0, 1.0])
        cell = (d2 * weights).sum(axis=1)
    else:
        cell = d2.mean(axis=1) * 6.0  # sum over the 6 unique components
    if w is None:
        return float(cell.mean())
    return float((cell * w).sum() / w.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--les-u", required=True)
    ap.add_argument("--les-tau", required=True)
    ap.add_argument("--les-k", default=None)
    ap.add_argument("--baseline-u", required=True)
    ap.add_argument("--baseline-tau", required=True)
    ap.add_argument("--recon-u", required=True)
    ap.add_argument("--recon-tau", required=True)
    ap.add_argument("--volumes", default=None)
    ap.add_argument("--json", default=None)
    ap.add_argument("--label", default="")
    args = ap.parse_args()

    u_les = read_of_field(args.les_u)
    tau_les = read_of_field(args.les_tau)
    u0 = read_of_field(args.baseline_u)
    tau0 = read_of_field(args.baseline_tau)
    u1 = read_of_field(args.recon_u)
    tau1 = read_of_field(args.recon_tau)
    vol = read_of_field(args.volumes)[:, 0] if args.volumes else None

    out = {"label": args.label, "n_cells": int(u_les.shape[0])}

    if args.les_k:
        k_les = read_of_field(args.les_k)[:, 0]
        trace_half = 0.5 * (tau_les[:, 0] + tau_les[:, 3] + tau_les[:, 5])
        denom = np.maximum(np.abs(k_les), 1e-12)
        out["k_vs_half_trace_tau_max_rel"] = float(
            np.max(np.abs(trace_half - k_les) / denom))
        out["k_vs_half_trace_tau_mean_rel"] = float(
            np.mean(np.abs(trace_half - k_les) / denom))

    for name, w in (("primary_unweighted", None),
                    ("secondary_volume_weighted", vol)):
        if name.startswith("secondary") and vol is None:
            continue
        eU0 = eps_vector(u0, u_les, w)
        eU1 = eps_vector(u1, u_les, w)
        eT0_f = eps_symm(tau0, tau_les, w, frobenius=True)
        eT1_f = eps_symm(tau1, tau_les, w, frobenius=True)
        eT0_6 = eps_symm(tau0, tau_les, w, frobenius=False)
        eT1_6 = eps_symm(tau1, tau_les, w, frobenius=False)
        out[name] = {
            "eps_U_baseline": eU0,
            "eps_U_recon": eU1,
            "ratio_U": eU1 / eU0,
            "eps_tau_baseline_frobenius": eT0_f,
            "eps_tau_recon_frobenius": eT1_f,
            "ratio_tau_frobenius": eT1_f / eT0_f,
            "eps_tau_baseline_6comp": eT0_6,
            "eps_tau_recon_6comp": eT1_6,
            "ratio_tau_6comp": eT1_6 / eT0_6,
        }

    print(json.dumps(out, indent=2))
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(out, fh, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())


def tau_without_bdelta(recon_tau_path, k_path, bdelta_path):
    """Diagnostic variant: tau with the bijDelta contribution removed,
    tau_nob = tauijRecon - 2 k bijDelta. Not the pre-registered metric."""
    tau = read_of_field(recon_tau_path)
    k = read_of_field(k_path)[:, 0:1]
    bd = read_of_field(bdelta_path)
    return tau - 2.0 * k * bd
