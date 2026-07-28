#!/usr/bin/env python3
"""Extract surge-front (alpha.water=0.5 crossing) position vs time from an
interFoam 'sets' function-object sampling directory (postProcessing/frontTrack),
and non-dimensionalise against the Martin & Moyce (1952) convention used in
Xie (arXiv:2108.08769, Fig. 7): Z = x_front/a, T = t*sqrt(g/a).
"""
import sys, glob, os, math

a = 0.05715      # m, Martin & Moyce a = 2 1/4 in
g = 9.81         # m/s^2
T_of_t = lambda t: t * math.sqrt(g / a)

def front_x(path):
    xs, al = [], []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            xs.append(float(parts[0]))
            al.append(float(parts[1]))
    # walk until alpha drops through 0.5 (from water side to air side)
    front = None
    for i in range(len(xs) - 1):
        a0, a1 = al[i], al[i + 1]
        if (a0 - 0.5) * (a1 - 0.5) <= 0 and a0 != a1:
            # linear interpolation for the crossing
            frac = (0.5 - a0) / (a1 - a0)
            xc = xs[i] + frac * (xs[i + 1] - xs[i])
            front = xc  # keep updating -> last crossing = furthest front
    return front

def main(pp_dir):
    rows = []
    for d in sorted(glob.glob(os.path.join(pp_dir, "*")), key=lambda p: float(os.path.basename(p))):
        t = float(os.path.basename(d))
        f = glob.glob(os.path.join(d, "*alpha.water.xy"))
        if not f:
            continue
        xf = front_x(f[0])
        if xf is None:
            continue
        rows.append((t, T_of_t(t), xf / a))
    print("t(s)      T=t*sqrt(g/a)   Z=x_front/a")
    for t, T, Z in rows:
        print(f"{t:8.4f}  {T:10.4f}   {Z:8.4f}")
    return rows

if __name__ == "__main__":
    main(sys.argv[1])
