#!/usr/bin/env python3
"""F7a R1 figure: surge-front convergence and the bed-friction mechanism."""
import glob
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SC = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = sys.argv[2] if len(sys.argv) > 2 else "F7a_R1_convergence.png"

MM = [(3.90, 6.00), (4.49, 7.00), (5.17, 8.00), (5.91, 9.00),
      (6.70, 10.00), (7.72, 11.00), (8.58, 12.00), (9.53, 13.00)]
REF_SIM = [(-0.017, 0.998), (0.846, 1.437), (1.537, 2.332), (2.228, 3.252),
           (2.919, 4.326), (3.783, 5.583), (4.474, 6.678), (5.165, 7.669),
           (5.855, 8.648), (6.546, 9.640), (7.237, 10.564), (7.928, 11.380),
           (8.619, 12.221), (9.310, 13.003)]


def load(tag):
    p = os.path.join(SC, "m_%s.json" % tag)
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    rows = []
    for r in d["rows"]:
        z = r.get("Z_0.02")
        # stop the trace once the surge reaches the far wall at Z=15: past that
        # point the "furthest downward crossing" is no longer the surge toe.
        if z is None or z > 14.4:
            break
        rows.append((r["T"], z))
    return rows


fig, ax = plt.subplots(1, 2, figsize=(12.5, 5.2))

# ---- panel 1: isotropic mesh ladder -------------------------------------
iso = [("res8_base", "a/8", "#c6dbef"), ("res16_base", "a/16", "#9ecae1"),
       ("res32_base", "a/32", "#4292c6"), ("res64_base", "a/64", "#08519c")]
for tag, lab, c in iso:
    r = load(tag)
    if r:
        ax[0].plot([x[0] for x in r], [x[1] for x in r], "-", color=c,
                   lw=1.8, label="interFoam dx=dy=%s" % lab)
ax[0].plot([p[0] for p in REF_SIM], [p[1] for p in REF_SIM], "--",
           color="#2ca25f", lw=1.8, label="reference sim (Leakey et al., inviscid, a/16)")
ax[0].plot([p[0] for p in MM], [p[1] for p in MM], "kx", ms=9, mew=2,
           label="Martin & Moyce (1952) experiment")
ax[0].set_title("Isotropic refinement: converges, but not to the data")

# ---- panel 2: vertical (film) refinement + friction switch --------------
yl = [("res32_base", "dx=a/32, dy=a/32", "#fdae6b"),
      ("res32y64_base", "dx=a/32, dy=a/64", "#f16913"),
      ("res32y128_base", "dx=a/32, dy=a/128", "#a63603"),
      ("res32y256_base", "dx=a/32, dy=a/256", "#7f2704")]
for tag, lab, c in yl:
    r = load(tag)
    if r:
        ax[1].plot([x[0] for x in r], [x[1] for x in r], "-", color=c, lw=1.8,
                   label="no-slip floor, " + lab)
r = load("res32y128_slip")
if r:
    ax[1].plot([x[0] for x in r], [x[1] for x in r], ":", color="#a63603", lw=2.2,
               label="SLIP floor, dx=a/32, dy=a/128")
ax[1].plot([p[0] for p in REF_SIM], [p[1] for p in REF_SIM], "--",
           color="#2ca25f", lw=1.8, label="reference sim (inviscid)")
ax[1].plot([p[0] for p in MM], [p[1] for p in MM], "kx", ms=9, mew=2,
           label="Martin & Moyce (1952) experiment")
ax[1].set_title("Resolving the bed boundary layer under the film moves it back")

for a_ in ax:
    a_.set_xlabel(r"$T = t\sqrt{g/a}$")
    a_.set_ylabel(r"$Z = x_{\rm front}/a$")
    a_.set_xlim(0, 9.8)
    a_.set_ylim(1, 15)
    a_.grid(alpha=0.3)
    a_.legend(fontsize=8, loc="upper left")

fig.suptitle("F7a dam break (Martin & Moyce a=2.25 in) — front position, "
             "depth-integrated metric at h=0.02a", fontsize=11)
fig.tight_layout()
fig.savefig(OUT, dpi=150)
print("wrote", OUT)
