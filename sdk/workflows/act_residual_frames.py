"""Residual-evolution FRAMES: one run, several cuts, one set of axes.

Sanaa's instruction, 2026-09-13: *"since we have the residuals saved, i want to see
these residuals plotted that way we can see them go down in the demo … residual
curves plotted at different iterations so we can see their evolution"*.

A single residual figure shows where a run ENDED. A viewer stepping through frames
cut at 10, 25, 50, 75 and 100 % of the run sees the curves DESCEND, which is the
thing being claimed. The frames are only comparable if the axes do not move, so the
limits are computed ONCE from the complete series and pinned on every frame through
``act_plots_lib.residual_history(xlim=…, ylim=…)``. Without that each frame
autoscales to its own data, every frame looks identical, and the series shows
nothing at all.

Nothing here reads a solver or a log: it is handed the arrays the caller already
read, and it only decides where to cut them.
"""
from __future__ import annotations

import math
import os

FRACTIONS = (0.10, 0.25, 0.50, 0.75, 1.00)


def _finite_min(values):
    lo = None
    for v in values:
        if v is None or (isinstance(v, float) and (math.isnan(v) or v <= 0.0)):
            continue
        lo = v if lo is None else min(lo, v)
    return lo


def _finite_max(values):
    hi = None
    for v in values:
        if v is None or (isinstance(v, float) and math.isnan(v)):
            continue
        hi = v if hi is None else max(hi, v)
    return hi


def residual_frames(out_dir, stem, it, series, *, target=None,
                    fractions=FRACTIONS, final_name=None, decades_floor=1e-9):
    """Write one PNG per fraction, all on the SAME axes, and return their paths.

    ``final_name`` names the 100 % frame when the folder already has a figure by
    that name in its orders (e.g. ``m6_residuals.png``), so the ordered file keeps
    its name and the frames sit beside it.
    """
    from workflows.act_plots_lib import residual_history

    if not it or not series:
        raise ValueError("residual_frames was given no data to cut")
    n = len(it)
    lo = min(x for x in (_finite_min(v) for v in series.values()) if x is not None)
    hi = max(x for x in (_finite_max(v) for v in series.values()) if x is not None)
    if target:
        lo = min(lo, target)
    lo = max(lo, decades_floor)
    ylim = (lo * 0.5, hi * 2.0)
    xlim = (it[0], it[-1])

    out = []
    for f in fractions:
        k = max(2, int(round(n * f)))
        name = (final_name if (final_name and f >= 1.0)
                else "%s_f%02d.png" % (stem, int(round(f * 100))))
        p = residual_history(os.path.join(out_dir, name), it[:k],
                             series={key: v[:k] for key, v in series.items()},
                             target=target, xlim=xlim, ylim=ylim)
        out.append((f, str(p), it[k - 1]))
    return out
