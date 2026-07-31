#!/usr/bin/env python3
"""F5c evidence figure: the wall-shear topology that the original detector
misread, and the convergence of x_r/H with outer iteration.

Left panel   -- Cf(x) on bottomWallDownstream for each mesh level, with the
                primary bubble shaded, the Driver & Seegmiller band marked,
                and the location the ORIGINAL (sign-inverted) detector
                returned marked separately, so the two readings of the same
                curve are visible side by side.
Right panel  -- x_r/H against outer iteration for each level, showing that
                the 2,000-8,000 iteration runs in the first pass were reading
                a number that had not settled.

Usage: plot_evidence.py OUT.png RUN_DIR [RUN_DIR ...]
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

X_R_REF, X_R_BAND = 6.26, 0.10
COLORS = {"coarse": "#4C72B0", "medium": "#DD8452", "fine": "#55A868"}


def main() -> int:
    out = Path(sys.argv[1])
    runs = [Path(p) for p in sys.argv[2:]]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13.5, 4.8))

    for rd in runs:
        rec = json.loads((rd / "record.json").read_text())
        prof = json.loads((rd / "wall_shear_profile.json").read_text())
        lvl = rec["level"]
        c = COLORS.get(lvl, "#8172B3")
        x = [p[0] for p in prof]
        cf = [p[1] for p in prof]
        ax.plot(x, cf, color=c, lw=1.6,
                label=f"{lvl} ({rec['cells']:,} cells), $x_r/H$={rec['x_r_over_h']:.2f}")
        r = rec["reattachment"]
        ax.plot([r["x_r_over_h"]], [0.0], "o", color=c, ms=7, zorder=5)
        if lvl == runs[0].name.split("_")[-1] or True:
            pass
        hist = [(t, v) for t, v in rec["x_r_over_h_history"] if v is not None]
        ax2.plot([h[0] for h in hist], [h[1] for h in hist], color=c, lw=1.6,
                 label=f"{lvl} ({rec['cells']:,} cells)")

    # Reference band and the two readings of the same curve.
    for a in (ax, ax2):
        a.axhspan(0, 0, color="none")
    ax.axvspan(X_R_REF - X_R_BAND, X_R_REF + X_R_BAND, color="#C44E52", alpha=0.25,
               label=f"Driver & Seegmiller 1985: $x_r/H$ = {X_R_REF} ± {X_R_BAND}")
    ax.axhline(0.0, color="0.4", lw=0.8)
    ax.set_xlim(0, 12)
    ax.set_xlabel("$x/H$ along bottomWallDownstream")
    ax.set_ylabel(r"$C_f = -\tau_x/(\tfrac{1}{2}U_{ref}^2)$   (>0 = forward flow)")
    ax.set_title("Wall-shear topology: corner eddy, primary bubble, reattachment")
    ax.legend(fontsize=8, loc="lower right")
    ax.annotate("secondary corner eddy\n(the original detector returned\nits downstream edge as $x_r$)",
                xy=(1.3, 0.0), xytext=(1.6, 0.0032), fontsize=8,
                arrowprops=dict(arrowstyle="->", color="0.35", lw=0.9), color="0.25")

    ax2.axhspan(X_R_REF - X_R_BAND, X_R_REF + X_R_BAND, color="#C44E52", alpha=0.25,
                label=f"reference {X_R_REF} ± {X_R_BAND}")
    ax2.axvspan(2000, 8000, color="0.85", alpha=0.7, zorder=0)
    ax2.annotate("iteration range used in the\nfirst pass (2,000-8,000)",
                 xy=(5000, 1.0), fontsize=8, ha="center", color="0.3")
    ax2.set_xlabel("SIMPLE outer iteration")
    ax2.set_ylabel("$x_r/H$")
    ax2.set_title("Gate quantity vs iteration count")
    ax2.legend(fontsize=8, loc="lower right")

    fig.suptitle("F5c backward-facing step vs Driver & Seegmiller (1985) — "
                 "corrected wall-shear sign convention", fontsize=11)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
