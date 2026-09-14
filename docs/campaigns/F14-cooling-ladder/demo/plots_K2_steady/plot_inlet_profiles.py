#!/usr/bin/env python3
"""Draw k2_inlet_profiles.png from the CSV `render_round3.py` samples.

Separate from the sampler because matplotlib under pvpython fails inside its bundled
freetype on this axes; under plain python3 the same call works.
"""
import csv, os, sys
REPO = "/home/ubuntu/Certonomous"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "sdk"))
from workflows.act_plots_lib import _plt, _finish, PALETTE, RED

rows = list(csv.reader(open(os.path.join(HERE, "k2_inlet_profiles.csv"))))[1:]
per = {}
for r in rows:
    per.setdefault(int(r[0]), []).append((float(r[1]), float(r[2])))
plt = _plt()
fig, ax = plt.subplots(figsize=(6.4, 4.6))
for (k, v), col in zip(sorted(per.items()), PALETTE):
    v.sort()
    ax.plot([t for _, t in v], [z for z, _ in v], color=col, lw=1.6,
            label=r"$R_{%d}$" % k)
ax.axvline(27.0, color=RED, lw=1, ls="--", label=r"$T_{\lim}=27\ ^{\circ}\mathrm{C}$")
ax.set_xlim(15.0, 28.0)
ax.set_xlabel(r"$T_{\mathrm{in}}$  [°C]")
ax.set_ylabel(r"$z$  [m]")
ax.legend(loc="upper right", ncol=2)
_finish(fig, os.path.join(HERE, "k2_inlet_profiles.png"))
print("drew k2_inlet_profiles.png from %d racks, %d samples each"
      % (len(per), len(next(iter(per.values())))))
