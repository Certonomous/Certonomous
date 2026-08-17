"""Render the pressure-painted NACA 0015 sail as a standalone website PNG.

Reads the solved body patch at full resolution (the ``body.vtp`` that
``foamToVTK -surfaceFields`` wrote inside the case) through the act's own
VTP reader (``chief_engineer.field_render._read_patch``), so every drawn
triangle carries the pressure of that exact face. Red where the flow
stagnates, blue where it accelerates, control-room dark theme.

The act's decimated ``*_field.json`` is NOT used here: its per-face values
lose geometric correspondence under the cluster decimation, which reads as
noise when painted (flagged in the delivery report).

    python scripts/render_painted_sail.py body.vtp [out.png]
"""

from __future__ import annotations

import sys
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer import plot_theme as t
from chief_engineer.field_render import _read_patch

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

REPO = SDK.parent
DEFAULT_OUT = lab_paths.PLOTS / "submarine_sail" / "painted_sail.png"


def main(argv: list[str]) -> int:
    vtp_path = Path(argv[0])
    out_png = Path(argv[1]) if len(argv) > 1 else DEFAULT_OUT
    out_png.parent.mkdir(parents=True, exist_ok=True)

    vertices, faces, values = _read_patch(vtp_path, "p")

    plt = t._pyplot()
    import matplotlib.colors as mcolors
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    # Robust display range, the same 2nd/98th percentile clip the act uses so
    # a single stagnation spike cannot flatten the surface to one colour.
    ordered = sorted(values)
    lo = ordered[max(0, int(0.02 * len(ordered)))]
    hi = ordered[min(len(ordered) - 1, int(0.98 * len(ordered)))]
    clipped = [min(hi, max(lo, v)) for v in values]

    # Diverging map centred on zero gauge pressure: red = stagnation (high),
    # blue = acceleration (low), neutral at the freestream reference.
    norm = mcolors.TwoSlopeNorm(vmin=min(lo, -1e-9), vcenter=0.0,
                                vmax=max(hi, 1e-9))
    cmap = plt.get_cmap("RdBu_r")

    tris = [[vertices[i] for i in face] for face in faces]
    fig = plt.figure(figsize=(12.8, 7.2), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor(t.BG)

    collection = Poly3DCollection(tris, linewidths=0.0, antialiased=False)
    collection.set_facecolor(cmap(norm(clipped)))
    ax.add_collection3d(collection)

    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]
    b_min = [min(xs), min(ys), min(zs)]
    b_max = [max(xs), max(ys), max(zs)]
    spans = [b_max[i] - b_min[i] for i in range(3)]
    ax.set_xlim(b_min[0], b_max[0])
    ax.set_ylim(b_min[1] - 0.2, b_max[1] + 0.2)     # air around the thin body
    ax.set_zlim(b_min[2], b_max[2])
    ax.set_box_aspect((spans[0], spans[1] + 0.4, spans[2]))
    ax.view_init(elev=16, azim=-148)   # leading edge and tip toward camera
    ax.set_axis_off()

    fig.suptitle("Submarine sail, surface pressure from the solve",
                 color=t.INK, fontsize=16, fontweight="bold", x=0.06,
                 ha="left", y=0.94, fontfamily="monospace")
    fig.text(0.06, 0.885,
             "NACA 0015 section  ·  chord 1.2 m  ·  span 1.8 m  ·  "
             "Re 6.0e6  ·  V 75 m/s  ·  k-omega SST",
             color=t.MUTED, fontsize=11, fontfamily="monospace")
    stag = max(values)
    fig.text(0.06, 0.16,
             f"stagnation peak  $p/\\rho$ = {stag:.0f} m$^2$/s$^2$"
             f"  ($\\approx V^2/2$ = {75.0 ** 2 / 2:.0f})",
             color=t.INK, fontsize=12, fontweight="bold", fontfamily="monospace")
    fig.text(0.06, 0.10,
             "red: stagnation, high pressure\nblue: accelerating flow, low pressure",
             color=t.MUTED, fontsize=10.5, fontfamily="monospace")

    mappable = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    mappable.set_array(clipped)
    cbar = fig.colorbar(mappable, ax=ax, shrink=0.55, pad=0.02, aspect=28)
    cbar.set_label("kinematic pressure  $p/\\rho$  [m$^2$/s$^2$]",
                   color=t.INK, fontsize=11, family="monospace")
    cbar.ax.tick_params(colors=t.MUTED, labelsize=9)
    cbar.outline.set_edgecolor(t.DIM)

    fig.savefig(out_png, facecolor=t.BG)
    plt.close(fig)
    print(f"wrote {out_png} ({len(faces)} faces painted)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
