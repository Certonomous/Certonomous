#!/usr/bin/env python3
"""CBFS data forensics: benchmark packaging vs Bentaleb, Lardeau & Leschziner LES.

Zero-compute companion to W2_SPARTA_CBFS_DATA_FORENSICS.md. Three parts:

  1. provenance : download the NASA TMR hosting of the Bentaleb LES from the
     Internet Archive (the live TMR URL now redirects to a generic nasa.gov
     page), parse it, and diff it field-by-field against what the
     closure-challenge benchmark ships in data/CBFS/0/.
  2. recirc     : separation/reattachment of the source LES from its own
     wall-quantities file (checks against Bentaleb's published 0.83 / 4.36).
  3. scans      : the {T1} R-coefficient (OLS and Ridge, Eq. 20) recomputed
     from the already-extracted frozen fields under labelled transformations
     (trims, weightings, LES-published velocity derivatives). Pure arithmetic
     on fields already on disk -- no solver is run and no graded number is
     recomputed differently from the pre-registered convention.

Usage:
  cbfs_bentaleb_forensics.py [--cache DIR] [--bench DIR] [--frozen DIR/TIME]

Every download records its Wayback Machine snapshot timestamp so each claim
about the published LES is checkable.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import griddata

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sparta_frozen_score import read_of_field  # noqa: E402
from sparta_regression import build_basis      # noqa: E402

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

WAYBACK = [
    # (snapshot timestamp, original URL)
    ("20210318010556", "https://turbmodels.larc.nasa.gov/Other_LES_Data/curvedstep.html"),
    ("20210319094143", "https://turbmodels.larc.nasa.gov/Other_LES_Data/Curvedstep/curvedbackstep_vel_stress.dat.gz"),
    ("20210319004901", "https://turbmodels.larc.nasa.gov/Other_LES_Data/Curvedstep/curvedbackstep_vel_derivs.dat.gz"),
    ("20210319130840", "https://turbmodels.larc.nasa.gov/Other_LES_Data/Curvedstep/curvedbackstep_wallquantities.dat"),
    ("20161224182407", "http://turbmodels.larc.nasa.gov/Other_LES_Data/Curvedstep/README_p_vel_and_turb_curvedbackstep.txt"),
]

VEL_STRESS_VARS = ["x", "y", "p", "u", "v", "w",
                   "uu", "vv", "ww", "uv", "uw", "vw", "k"]
VEL_DERIV_VARS = ["x", "y", "dudx", "dudy", "dvdx", "dvdy", "dwdx", "dwdy"]
I_LES, J_LES = 768, 160
LAMBDA_R = 0.0316227766          # primary, as pre-registered


def fetch(cache):
    cache.mkdir(parents=True, exist_ok=True)
    for ts, url in WAYBACK:
        dst = cache / Path(url).name
        if not dst.exists():
            wb = f"https://web.archive.org/web/{ts}id_/{url}"
            print(f"fetching {dst.name} from snapshot {ts}")
            subprocess.run(["curl", "-sL", "--max-time", "120", wb, "-o", str(dst)],
                           check=True)
        if dst.suffix == ".gz" and not dst.with_suffix("").exists():
            subprocess.run(["gunzip", "-kf", str(dst)], check=True)


def parse_tecplot_block(path, names, idim, jdim):
    lines = Path(path).read_text().splitlines()
    istart = next(i for i, l in enumerate(lines)
                  if l.strip() and re.match(r"^[\s0-9eE\+\-\.]+$", l))
    data = np.fromstring("\n".join(lines[istart:]), sep=" ")
    assert data.size == len(names) * idim * jdim, (data.size, len(names))
    arrs = data.reshape(len(names), jdim, idim)
    return {n: arrs[i] for i, n in enumerate(names)}


def read_of_list(path, kind):
    txt = Path(path).read_text()
    m = re.search(r"nonuniform List<" + kind + r">\s*\n(\d+)\s*\(\s*\n(.*?)\n\)",
                  txt, re.S)
    n = int(m.group(1))
    body = m.group(2)
    if kind == "scalar":
        v = np.fromstring(body, sep="\n")
    else:
        v = np.fromstring(body.replace("(", " ").replace(")", " "), sep=" ")
        v = v.reshape(n, -1)
    assert v.shape[0] == n
    return v


def interp(les, names, tgt):
    pts = np.column_stack([les["x"].ravel(), les["y"].ravel()])
    out = {}
    for n in names:
        v = griddata(pts, les[n].ravel(), tgt, method="linear")
        bad = np.isnan(v)
        if bad.any():
            v[bad] = griddata(pts, les[n].ravel(), tgt[bad], method="nearest")
        out[n] = v
    return out


def provenance(cache, bench):
    les = parse_tecplot_block(cache / "curvedbackstep_vel_stress.dat",
                              VEL_STRESS_VARS, I_LES, J_LES)
    b0 = bench / "0"
    cx = read_of_list(b0 / "Cx", "scalar")
    cy = read_of_list(b0 / "Cy", "scalar")
    U = read_of_list(b0 / "interpolatedFields" / "U_internalField", "vector")
    k = read_of_list(b0 / "interpolatedFields" / "k_internalField", "scalar")
    tau = read_of_list(b0 / "interpolatedFields" / "tauij_internalField",
                       "symmTensor")
    p = read_of_list(b0 / "interpolatedFields" / "p_internalField", "scalar")
    tgt = np.column_stack([cx, cy])
    o = interp(les, ["u", "v", "k", "uu", "vv", "ww", "uv", "p"], tgt)
    print(f"LES extent x [{les['x'].min():.3f}, {les['x'].max():.3f}] "
          f"y [{les['y'].min():.3f}, {les['y'].max():.3f}]")
    print(f"benchmark cell centres x [{cx.min():.3f}, {cx.max():.3f}] "
          f"y [{cy.min():.3f}, {cy.max():.3f}]")
    pairs = [("Ux", U[:, 0], o["u"]), ("Uy", U[:, 1], o["v"]), ("k", k, o["k"]),
             ("tau_xx", tau[:, 0], o["uu"]), ("tau_xy", tau[:, 1], o["uv"]),
             ("tau_yy", tau[:, 3], o["vv"]), ("tau_zz", tau[:, 5], o["ww"]),
             ("p", p, o["p"])]
    for name, a, b in pairs:
        d = a - b
        print(f"  {name:7s} scaled MAE {np.abs(d).mean() / np.abs(b).max():.2e} "
              f"max|d| {np.abs(d).max():.2e} "
              f"slope {np.dot(a, b) / np.dot(b, b):.6f}")
    return les, cx, cy


def recirc(cache):
    rows = []
    for line in (cache / "curvedbackstep_wallquantities.dat").read_text().splitlines():
        line = line.strip()
        if line and line[0] in "-0123456789.":
            rows.append([float(v) for v in line.split()])
    w = np.array(rows)
    xw, tw = w[:, 0], w[:, 3]
    s = np.flatnonzero(np.sign(tw[:-1]) != np.sign(tw[1:]))
    for i in s:
        x0 = xw[i] - tw[i] * (xw[i + 1] - xw[i]) / (tw[i + 1] - tw[i])
        if abs(x0) < 12:
            print(f"  tau_w zero crossing at x/H = {x0:.3f}")


def scans(cache, frozen_dir, tdir, cx, cy, les):
    d = Path(frozen_dir) / str(tdir)
    k = read_of_field(d / "k")[:, 0]
    om = read_of_field(d / "omega")[:, 0]
    gradU = read_of_field(d / "grad(U)")
    y = read_of_field(d / "kDeficit")[:, 0]
    A, T, _, _ = build_basis(k, om, gradU)
    x = 2.0 * k * np.einsum("nij,nij->n", T[0], A)

    derivs = parse_tecplot_block(cache / "curvedbackstep_vel_derivs.dat",
                                 VEL_DERIV_VARS, I_LES, J_LES)
    g = interp(derivs, ["dudx", "dudy", "dvdx", "dvdy"],
               np.column_stack([cx, cy]))
    Ad = np.zeros((len(cx), 3, 3))
    Ad[:, 0, 0], Ad[:, 0, 1] = g["dudx"], g["dudy"]
    Ad[:, 1, 0], Ad[:, 1, 1] = g["dvdx"], g["dvdy"]
    tau_t = 1.0 / om
    Sd = 0.5 * tau_t[:, None, None] * (Ad + np.transpose(Ad, (0, 2, 1)))
    xd = 2.0 * k * np.einsum("nij,nij->n", Sd, Ad)

    def row(label, xx, m):
        xs, ys = xx[m], y[m]
        ols = xs @ ys / (xs @ xs)
        ridge = xs @ ys / (xs @ xs + LAMBDA_R)
        eps = np.mean((ys - ridge * xs) ** 2)
        print(f"  {label:44s} K={m.sum():5d} OLS={ols:.4f} "
              f"ridge={ridge:.4f} eps(R)={eps:.3e}")

    allm = np.ones_like(x, bool)
    print("candidate from frozen-solve gradient (pre-registered operator):")
    row("all cells (graded convention)", x, allm)
    row("top-boundary strip excluded (y < 8)", x, cy < 8)
    row("y < 9", x, cy < 9)
    for lab, m in [("top strip only (y > 9)", cy > 9),
                   ("8 < y < 9", (cy > 8) & (cy < 9))]:
        xs, ys = x[m], y[m]
        print(f"  {lab:44s} K={m.sum():5d} local OLS={xs @ ys / (xs @ xs):.4f} "
              f"share of sum(x^2)={xs @ xs / (x @ x):.3f}")
    print("candidate from the LES-published velocity derivatives:")
    row("all cells", xd, allm)
    row("top-boundary strip excluded (y < 8)", xd, cy < 8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="/tmp/cbfs_bentaleb_cache")
    ap.add_argument("--bench",
                    default="/home/ubuntu/closure-challenge-benchmark/data/CBFS")
    ap.add_argument("--frozen",
                    default=str(lab_paths.RUNS / "W2_sparta_runs"
                                / "cbfs_frozen"))
    ap.add_argument("--time", default="354")
    args = ap.parse_args()
    cache = Path(args.cache)
    fetch(cache)
    print("== 1. benchmark packaging vs NASA-hosted Bentaleb LES ==")
    les, cx, cy = provenance(cache, Path(args.bench))
    print("== 2. recirculation of the source LES (published: 0.83 / 4.36) ==")
    recirc(cache)
    print("== 3. labelled coefficient scans on the frozen fields ==")
    scans(cache, args.frozen, args.time, cx, cy, les)


if __name__ == "__main__":
    main()
