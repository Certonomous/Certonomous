"""Shared plumbing for the four compressible validation acts (supersonic
wedge, supersonic cone, diamond airfoil, hypersonic cylinder).

The case-building and post-processing math is not re-derived here: it is
imported verbatim from the campaign evidence that already validated these
setups (``demo-output/website/campaign/F3_runs`` and ``F4_runs``). This
module adds only what those standalone scripts do not have: mesh- and
solve-level caching against ``chief_engineer.head_engineer``'s cache roots,
so a second run of the same body is warm without ever touching a number.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Callable

_HERE = Path(__file__).resolve()
_REPO = _HERE.parents[2]
F3_DIR = _REPO / "demo-output" / "website" / "campaign" / "F3_runs"
F4_DIR = _REPO / "demo-output" / "website" / "campaign" / "F4_runs"
for _d in (F3_DIR, F4_DIR):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

from chief_engineer.head_engineer import MESH_CACHE_ROOT, SOLVE_CACHE_ROOT

FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"


def sh(cmd: str, cwd: Path, logfile: Path | None = None) -> float:
    """Run one solver step through the OpenFOAM environment, exactly as the
    campaign scripts do — no WSL hop, this box runs the toolchain natively."""
    import subprocess

    full = f"source {FOAM_BASHRC} >/dev/null 2>&1; {cmd}"
    t0 = time.time()
    result = subprocess.run(["bash", "-c", full], cwd=str(cwd),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    if logfile:
        logfile.write_bytes(result.stdout)
    if result.returncode != 0:
        tail = result.stdout.decode(errors="replace").splitlines()[-25:]
        raise RuntimeError(f"command failed ({cmd}) rc={result.returncode}: "
                           + "\n".join(tail))
    return dt


def _safe(key: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", key)


def _cache_dir(root: str, key: str) -> Path:
    # A blank or all-punctuation key sanitizes to an empty string and would
    # otherwise resolve to ``root`` itself -- so a later ``shutil.rmtree`` on
    # that "entry" wipes the whole shared cache. Refuse it loudly instead.
    safe = _safe(str(key or "").strip())
    if not safe or safe.strip("_.") == "":
        raise ValueError(
            f"refusing a degenerate cache key {key!r} -- it would resolve "
            f"to the cache root itself")
    return Path(os.path.expanduser(root)) / safe


def _mesh_file(poly: Path, name: str) -> bool:
    """A polyMesh file may be written plain or gzipped; OpenFOAM reads both.

    Checking only for the plain name makes a gzipped mesh look absent, so the
    cache reports a miss and the act silently re-solves from cold -- which on
    a demo machine shows up as a five-second act suddenly taking minutes.
    Found in the DAFoam engine on a case shipping owner.gz; the same
    assumption was here."""
    return (poly / name).exists() or (poly / f"{name}.gz").exists()


def cached_mesh_available(key: str) -> bool:
    if os.environ.get("CERTONOMOUS_MESH_CACHE") == "0":
        return False
    poly = _cache_dir(MESH_CACHE_ROOT, key) / "polyMesh"
    return _mesh_file(poly, "points") and _mesh_file(poly, "owner")


def restore_cached_mesh(case_dir: Path, key: str) -> bool:
    """Copy a cached mesh into the case. True on a warm hit."""
    if not cached_mesh_available(key):
        return False
    cache = _cache_dir(MESH_CACHE_ROOT, key)
    dest = Path(case_dir) / "constant" / "polyMesh"
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(cache / "polyMesh", dest)
    return (dest / "points").exists()


def save_mesh_to_cache(case_dir: Path, key: str) -> None:
    if os.environ.get("CERTONOMOUS_MESH_CACHE") == "0":
        return
    src = Path(case_dir) / "constant" / "polyMesh"
    if not (src / "points").exists():
        return
    cache = _cache_dir(MESH_CACHE_ROOT, key)
    shutil.rmtree(cache, ignore_errors=True)
    cache.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, cache / "polyMesh")


def _time_dirs(case_dir: Path) -> list[str]:
    names = [p.name for p in Path(case_dir).iterdir()
             if p.is_dir() and re.fullmatch(r"[0-9]+\.?[0-9]*", p.name) and p.name != "0"]
    return sorted(names, key=float)


def cached_solve_available(key: str) -> bool:
    if os.environ.get("CERTONOMOUS_SOLVER_CACHE") == "0":
        return False
    cache = _cache_dir(SOLVE_CACHE_ROOT, key)
    return (cache / "DONE").exists()


def restore_cached_solve(case_dir: Path, key: str) -> bool:
    """Restore every cached post-t=0 time directory plus postProcessing.
    True on a warm hit; the parsing code that runs afterward is identical
    either way, so a warm result is never merely close, it is the same
    files read the same way."""
    if not cached_solve_available(key):
        return False
    cache = _cache_dir(SOLVE_CACHE_ROOT, key)
    case_dir = Path(case_dir)
    for entry in cache.iterdir():
        if entry.name in ("DONE",):
            continue
        dest = case_dir / entry.name
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(entry, dest)
    return True


def save_solve_to_cache(case_dir: Path, key: str) -> None:
    if os.environ.get("CERTONOMOUS_SOLVER_CACHE") == "0":
        return
    case_dir = Path(case_dir)
    times = _time_dirs(case_dir)
    if not times:
        return
    cache = _cache_dir(SOLVE_CACHE_ROOT, key)
    shutil.rmtree(cache, ignore_errors=True)
    cache.mkdir(parents=True, exist_ok=True)
    for t in times:
        shutil.copytree(case_dir / t, cache / t)
    pp = case_dir / "postProcessing"
    if pp.exists():
        shutil.copytree(pp, cache / "postProcessing")
    (cache / "DONE").write_text(times[-1])


def run_checkmesh(case_dir: Path, *, log_name: str = "log.checkMesh") -> dict[str, Any]:
    """Run checkMesh fresh every time (cheap; a handful of seconds) so the
    mesh-validity gate always reflects the mesh actually sitting in the case,
    warm-restored or freshly built alike."""
    case_dir = Path(case_dir)
    log_path = case_dir / log_name
    sh("checkMesh -noTopology", case_dir, log_path)
    text = log_path.read_text(errors="replace")
    stats: dict[str, Any] = {"mesh_ok": "Mesh OK" in text}
    for pattern, key in (
            (r"cells:\s+(\d+)", "cells"),
            (r"non-orthogonality Max:\s*([0-9.]+)", "max_non_orthogonality"),
            (r"Max non-orthogonality =\s*([0-9.]+)", "max_non_orthogonality"),
            (r"Max skewness =\s*([0-9.]+)", "max_skewness")):
        match = re.search(pattern, text)
        if match:
            stats[key] = float(match.group(1))
    return stats


def linfit_shock_angle(points: list[tuple[float, float]]) -> tuple[float | None, float | None]:
    """Shock-locus slope, as a fitted angle in degrees, plus its R^2 — the
    exact fit ``run_wedge_case.py``/``run_cone_case.py`` use inline."""
    import math

    import numpy as np

    if len(points) < 3:
        return None, None
    pts = np.array(points)
    xk, yk = pts[:, 0], pts[:, 1]
    design = np.vstack([xk, np.ones_like(xk)]).T
    slope, intercept = np.linalg.lstsq(design, yk, rcond=None)[0]
    beta_deg = math.degrees(math.atan(slope))
    predicted = slope * xk + intercept
    ss_res = float(np.sum((yk - predicted) ** 2))
    ss_tot = float(np.sum((yk - yk.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return beta_deg, r2


def comparison_plot(out_png: Path, *, xlabel: str, ylabel: str, title: str,
                    series: list[tuple[str, list[float], list[float], str]],
                    hline: tuple[float, str] | None = None) -> str | None:
    """One self-explanatory figure: measured points/curve against the closed
    form reference, axes labeled with units, no rolling-mean legend entry —
    every coefficient plot in this lab names its trace and its band only."""
    from chief_engineer import plot_theme as _t

    plt = _t._pyplot()
    if plt is None:
        return None
    fig, ax = plt.subplots(figsize=(9.6, 4.6), dpi=150)
    for label, xs, ys, style in series:
        if style == "points":
            ax.scatter(xs, ys, color=_t.LIVE, s=26, zorder=3, label=label)
        else:
            ax.plot(xs, ys, color=_t.LIVE, linewidth=2.0, label=label)
    if hline is not None:
        value, label = hline
        ax.axhline(value, color=_t.VALID, linewidth=1.6, linestyle="--", label=label)
    _t.style_axes(ax, xlabel, ylabel, title)
    leg = ax.legend(frameon=False, fontsize=10, labelcolor=_t.INK, loc="best")
    for text in leg.get_texts():
        text.set_color(_t.INK)
    fig.tight_layout()
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png)
    plt.close(fig)
    return str(out_png)


def mesh_and_solve(*, case_dir: Path, mesh_key: str, solve_key_fn: Callable[[int], str],
                   build_mesh: Callable[[], None], run_solve: Callable[[], None],
                   count_cells: Callable[[], int]) -> dict[str, Any]:
    """The generic cold/warm skeleton every body's act follows:

    1. Restore or build the mesh (cache keyed on body + condition + resolution).
    2. Count cells (deterministic from the resolution table -- never guessed).
    3. Restore or run the solve (cache keyed on the mesh key plus the cell
       count just counted, so a solve key can never be built before the mesh
       it describes has actually landed).

    Returns timing and warm/cold facts; the caller still owns parsing the
    physical result, which runs unconditionally over whatever now sits on
    disk so a warm answer and a cold answer read identical files identically.
    """
    case_dir = Path(case_dir)
    t0 = time.monotonic()
    mesh_warm = restore_cached_mesh(case_dir, mesh_key)
    if not mesh_warm:
        build_mesh()
        save_mesh_to_cache(case_dir, mesh_key)
    mesh_seconds = time.monotonic() - t0

    cells = count_cells()
    solve_key = solve_key_fn(cells)

    t1 = time.monotonic()
    solve_warm = restore_cached_solve(case_dir, solve_key)
    if not solve_warm:
        run_solve()
        save_solve_to_cache(case_dir, solve_key)
    solve_seconds = time.monotonic() - t1

    return {"cells": cells, "mesh_warm": mesh_warm, "solve_warm": solve_warm,
            "mesh_seconds": round(mesh_seconds, 2), "solve_seconds": round(solve_seconds, 2),
            "mesh_key": mesh_key, "solve_key": solve_key}
