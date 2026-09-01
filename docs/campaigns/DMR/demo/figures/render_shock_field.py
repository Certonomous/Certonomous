"""Render the density contour record for the shock-reflection display act.

WHY THIS EXISTS. The contour record retained with the runs
(``verification/runs/DMR_runs/dmr_density_contours_t0p2.png``) is a correct
scientific figure and is NOT usable on camera: its captions carry the case
directory names, the solver and flux-scheme names, the pre-registration
filename and a pointer to an internal record. DEMO STANDARD v2 R5 forbids
every one of those in user-visible text. This script re-renders the SAME
fields, off disk, with captions an engineer reads without a glossary.

THIS SCRIPT STARTS NO SOLVER. It reads three ASCII fields per rung at the
final written time and draws contours. It writes no case, changes nothing in
the run tree, and books no solver compute.

It also derives no graded quantity. The verified numbers this act reports come
from each rung's own ``locator_result.json``, which was written by the graded
locator run; nothing here recomputes a shock position, an error or a verdict.

    python3 render_shock_field.py            # writes the figure beside this file
    python3 render_shock_field.py --check     # read the fields, print shape, draw nothing
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np

_REL = Path("verification") / "runs" / "DMR_runs"


def _find_run_root() -> Path:
    """Locate the run tree by walking up from this file.

    The frozen record cites an older location that no longer exists on disk,
    so the path is taken from the filesystem and never from the record. The
    search is by walking up rather than by a fixed number of parents so moving
    this file inside the repository cannot silently point it at nothing.
    """
    for parent in Path(__file__).resolve().parents:
        candidate = parent / _REL
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(
        f"no {_REL} above {Path(__file__).resolve()}; the run tree this "
        f"figure is drawn from is not on disk")


# Resolved lazily so ``--help`` works from anywhere; every reader calls it.
RUN_ROOT = _find_run_root()

TIME = "0.2"

# (directory, nx, ny, caption). The cell counts are the mesh as built and are
# checked against the field length that is actually read, so a wrong pair
# raises instead of silently reshaping into nonsense.
RUNGS = (
    ("res60", 240, 60, "Coarse grid, 240 by 60 cells"),
    ("res120", 480, 120, "Fine grid, 480 by 120 cells"),
)

# Contour convention carried over from the retained record: 30 uniform levels
# over the structure range. The left strip is outside the field of view rather
# than annotated, so the axis states the range and nothing is hidden behind a
# caption.
N_LEVELS = 30
X_MIN_PLOT = 0.25

_HEADER = re.compile(r"internalField\s+nonuniform\s+List<scalar>\s*\n\s*(\d+)\s*\n\(",
                     re.S)


def read_scalar_field(path: Path) -> np.ndarray:
    """Read one ASCII OpenFOAM internal scalar field.

    Refuses rather than guesses: a uniform field, a binary field or a header
    this pattern does not match raises, because a silently wrong array here
    would draw a plausible picture of the wrong thing.
    """
    text = path.read_text(encoding="utf-8", errors="strict")
    match = _HEADER.search(text)
    if match is None:
        raise ValueError(
            f"{path} is not an ASCII nonuniform scalar list; this reader "
            f"refuses to guess at its contents")
    count = int(match.group(1))
    start = match.end()
    end = text.index("\n)", start)
    values = np.fromstring(text[start:end], sep="\n")
    if values.size != count:
        raise ValueError(
            f"{path} declares {count} values and yielded {values.size}")
    return values


def load_rung(name: str, nx: int, ny: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Cell-centre coordinates and density for one grid, on a (ny, nx) lattice.

    NO WRITE ORDER IS ASSUMED, and that is not caution for its own sake. These
    cases were solved on four ranks and reconstructed, and the reconstructed
    fields are NOT in x-fastest order: reading them with a bare reshape draws a
    picture of the wrong field, sliced by rank. Every value is therefore
    carried with its own cell centre and the lattice is built by sorting on
    (y, x).

    The result is then CHECKED to be a complete Cartesian lattice: the right
    number of distinct rows and columns, one value per node, and coordinates
    that vary in exactly one direction along each axis. A field that fails any
    of those raises rather than being drawn.
    """
    case = RUN_ROOT / name / TIME
    cx = read_scalar_field(case / "Cx")
    cy = read_scalar_field(case / "Cy")
    rho = read_scalar_field(case / "rho")
    if not (cx.size == cy.size == rho.size):
        raise ValueError(f"{name}: Cx, Cy and rho differ in length")
    if cx.size != nx * ny:
        raise ValueError(
            f"{name}: field holds {cx.size} cells, {nx} by {ny} expects "
            f"{nx * ny}")
    if np.unique(np.round(cx, 9)).size != nx or np.unique(np.round(cy, 9)).size != ny:
        raise ValueError(
            f"{name}: cell centres do not form a {nx} by {ny} lattice")
    order = np.lexsort((cx, cy))
    cx = cx[order].reshape(ny, nx)
    cy = cy[order].reshape(ny, nx)
    rho = rho[order].reshape(ny, nx)
    if not (np.allclose(cy, cy[:, :1]) and np.allclose(cx, cx[:1, :])):
        raise ValueError(
            f"{name}: sorted cell centres are still not a Cartesian lattice, "
            f"so this figure would misplace the field")
    return cx, cy, rho


#: The ONE typographic style shared with the jet-flap figures. Imported by
#: absolute path rather than copied, because three copies of an rcParams block
#: drift and the drift is invisible: a figure in the wrong font still looks
#: like a figure. Real ``text.usetex`` is NOT reachable on this box -- both
#: ``type1cm.sty`` and ``cm-super`` are absent and installing them is behind
#: root, which is Sanaa's alone -- so this registers the same Latin Modern
#: faces that pdflatex already sets the result sheet in, making the figure
#: typographically identical to the sheet it is cut next to.
_STYLE_MODULE = Path("/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap"
                     "/jf1_figure_style.py")


def _latin_modern_rc() -> dict:
    """Load the shared style, or REFUSE. Never fall back to a silent DejaVu."""
    import importlib.util

    if not _STYLE_MODULE.is_file():
        raise RuntimeError(
            f"{_STYLE_MODULE} is absent, so the shared Latin Modern style "
            f"cannot be applied. Refusing rather than drawing in whatever "
            f"serif matplotlib finds next: that figure would look finished "
            f"and ship in the wrong font, and only pdffonts would ever say so.")
    spec = importlib.util.spec_from_file_location("jf1_figure_style", _STYLE_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.latin_modern_rc()


def render(out_path: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Applied BEFORE the figure is created, so every artist inherits it.
    # ACCEPTANCE IS `pdffonts` OVER THE RENDERED PDF REQUIRING ZERO DejaVu
    # FACES -- never a read of this source. The source says what was intended;
    # only the embedded fonts say what shipped.
    plt.rcParams.update(_latin_modern_rc())

    fig, axes = plt.subplots(len(RUNGS), 1, figsize=(11.0, 6.6), sharex=True)
    for ax, (name, nx, ny, caption) in zip(axes, RUNGS):
        cx, cy, rho = load_rung(name, nx, ny)
        keep = cx[0, :] >= X_MIN_PLOT
        x = cx[:, keep]
        y = cy[:, keep]
        r = rho[:, keep]
        levels = np.linspace(float(r.min()), float(r.max()), N_LEVELS)
        ax.contour(x, y, r, levels=levels, colors="k", linewidths=0.45)
        ax.set_ylabel(r"$y$")
        ax.set_ylim(0.0, 1.0)
        ax.set_title(
            rf"{caption}. {N_LEVELS} density contours, "
            rf"$\rho \in [{r.min():.2f},\, {r.max():.2f}]$",
            fontsize=10, loc="left")
    axes[-1].set_xlabel(r"$x$")
    axes[-1].set_xlim(X_MIN_PLOT, 3.0)
    fig.suptitle(
        "Double Mach reflection: density at $t = 0.2$, two grid resolutions",
        fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=170)
    fig.savefig(out_path.with_suffix(".pdf"))
    plt.close(fig)
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="read the fields and report, draw nothing")
    parser.add_argument("--out", default=str(
        Path(__file__).resolve().parent / "dmr_density_contours.png"))
    args = parser.parse_args()
    if args.check:
        for name, nx, ny, _caption in RUNGS:
            cx, cy, rho = load_rung(name, nx, ny)
            print(f"{name}: {cx.shape} cells, rho in "
                  f"[{rho.min():.4f}, {rho.max():.4f}], "
                  f"x in [{cx.min():.5f}, {cx.max():.5f}]")
        return 0
    path = render(Path(args.out))
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
