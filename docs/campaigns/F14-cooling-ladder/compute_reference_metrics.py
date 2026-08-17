#!/usr/bin/env python3
"""Recompute the K0c turbulent-rung reference metrics from the Betts and Bokhari
ERCOFTAC Case 079 data files kept in reference-data/betts_bokhari/.

Every number in the K0c gate table that is marked DERIVED comes out of this
script and nowhere else. Run it from this directory:

    python3 compute_reference_metrics.py

Definitions used here and in the gate spec:
- theta = (T - T_c,plate) / dT, with dT = 19.6 K (lo) and 39.9 K (hi) as stated
  on the ERCOFTAC case page. T_c,plate is not needed for the stratification
  slope, which is computed on T directly and normalised by dT.
- Core stratification S = d(theta)/d(y/H), least-squares fit over the mid-width
  temperatures at y/H = 0.30, 0.40, 0.50, 0.60, 0.70, mid-width taken as
  x = 38.0 mm by linear interpolation in each profile file.
- Mid-height velocity extrema are the extreme values of the tabulated mean
  vertical velocity at y/H = 0.50, z = 0; no interpolation beyond the samples.
"""
import numpy as np
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "reference-data", "betts_bokhari")
H_MM = 2180.0  # cavity height, mm (2.18 m per ERCOFTAC case page)


def load(fn):
    xs, vs = [], []
    with open(os.path.join(DATA, fn)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            p = line.split()
            try:
                xs.append(float(p[0]))
                vs.append(float(p[1]))
            except ValueError:
                continue
    return np.array(xs), np.array(vs)


def mid_T(fn, xmid=38.0):
    x, T = load(fn)
    return float(np.interp(xmid, x, T))


def main():
    for suf, dT, label in (("lo", 19.6, "Ra=0.86e6"), ("hi", 39.9, "Ra=1.43e6")):
        print(f"== {label} (dT = {dT} K)")
        ys, Ts = [], []
        for yh, yval in (("30", 0.30), ("40", 0.40), ("50", 0.50),
                         ("60", 0.60), ("70", 0.70)):
            T = mid_T(f"mt_z0_{yh}_{suf}.dat")
            ys.append(yval)
            Ts.append(T)
            print(f"  y/H={yval:.2f}  T(x=38mm) = {T:.2f} C")
        ys, Ts = np.array(ys), np.array(Ts)
        A = np.vstack([ys, np.ones_like(ys)]).T
        (slope, icpt), res, *_ = np.linalg.lstsq(A, Ts, rcond=None)
        rms = float(np.sqrt(np.mean((A @ np.array([slope, icpt]) - Ts) ** 2)))
        S = slope / dT
        print(f"  fit dT/d(y/H) = {slope:.3f} K per unit y/H, rms residual {rms:.2f} K")
        print(f"  S = d(theta)/d(y/H) = {S:.4f}   (delta_S from residual ~ {rms/ (0.4*dT):.3f})")
        x, v = load(f"mv_z0_50_{suf}.dat")
        imax, imin = int(np.argmax(v)), int(np.argmin(v))
        asym = abs(abs(v[imax]) - abs(v[imin])) / max(abs(v[imax]), abs(v[imin]))
        print(f"  V_max = {v[imax]:+.3f} m/s at x = {x[imax]:.1f} mm")
        print(f"  V_min = {v[imin]:+.3f} m/s at x = {x[imin]:.1f} mm")
        print(f"  antisymmetry defect |{'|Vmax|-|Vmin|'}| / max = {100*asym:.1f} %")
        xr, vr = load(f"fvv_z0_50_{suf}.dat")
        print(f"  rms v' peak = {vr.max():.3f} m/s at x = {xr[int(np.argmax(vr))]:.1f} mm")


if __name__ == "__main__":
    main()
