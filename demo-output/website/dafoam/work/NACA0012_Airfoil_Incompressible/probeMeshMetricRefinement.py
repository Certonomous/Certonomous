#!/usr/bin/env python
"""
r6-airfoil-second-gradient-mechanism: does a mesh QUALITY METRIC (as opposed
to cell SIZE) get worse under refinement, localized near the leading edge --
the coordinator's named candidate ("a term whose linearisation error scales
with a mesh metric... rather than with cell size, so refining in one
direction worsens the metric even as cells get smaller")?

idx0/idx1 (A1's two flagged, non-warpDeriv, single-station shape DVs) sit at
the FFD's nearest interior chordwise control station to the leading edge
(x=0.245, see FFD/wingFFD.xyz: 5 chordwise stations at x=-0.01, 0.245, 0.5,
0.755, 1.01 -- idx0/idx1 are the upper/lower rows at the second station).
Their disagreement is step-independent and WORSENS under 3.65x mesh
refinement (PROOF.md 11.2: 11.9%/11.7% coarse -> 19.8%/14.5% refined) --
the opposite of ordinary discretization error.

This script requires NO container and NO solve: it reads the mesh geometry
that already exists on disk for both the coarse (this case, 4032 cells) and
refined (work_refined/NACA0012_Airfoil_Incompressible_refined, 14720 cells)
cases via stock OpenFOAM's own `checkMesh -writeAllFields` (pure mesh
geometry, solver-independent -- host OpenFOAM 2606 gives identical numbers
to the DAFoam container's own OpenFOAM build for a pure geometric quantity
on the same mesh files), then compares LEADING-EDGE-LOCALIZED cell
aspect ratio, non-orthogonality, and skewness, coarse vs refined.

Usage: run checkMesh -allGeometry -writeAllFields (and postProcess -func
writeCellCentres) in each mesh's own directory first (this script does not
invoke OpenFOAM itself, to keep it usable read-only against pre-computed
fields, exactly like probeWallBranch.py's own convention of separating the
solve/checkMesh step from the analysis step). Then:

    python probeMeshMetricRefinement.py <coarse_case_dir> <refined_case_dir>
"""
import sys
import gzip
import re


def _read_block(path):
    if path.endswith(".gz"):
        with gzip.open(path, "rt") as f:
            return f.read()
    with open(path) as f:
        return f.read()


def read_scalar_field(path):
    txt = _read_block(path)
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\n\(\n(.*?)\n\)\s*;", txt, re.S)
    n = int(m.group(1))
    vals = [float(x) for x in m.group(2).split("\n")]
    assert len(vals) == n, (len(vals), n)
    return vals


def read_vector_field(path):
    txt = _read_block(path)
    m = re.search(r"internalField\s+nonuniform\s+List<vector>\s*\n(\d+)\n\(\n(.*?)\n\)\s*;", txt, re.S)
    n = int(m.group(1))
    vecs = []
    for line in m.group(2).split("\n"):
        line = line.strip().strip("()")
        vecs.append(tuple(float(x) for x in line.split()))
    assert len(vecs) == n, (len(vecs), n)
    return vecs


def load(case_dir):
    import os

    def find(name):
        p0 = os.path.join(case_dir, "0", name)
        return p0 if os.path.exists(p0) else p0 + ".gz"

    nonOrtho = read_scalar_field(find("nonOrthoAngle"))
    aspect = read_scalar_field(find("cellAspectRatio"))
    skew = read_scalar_field(find("skewness"))
    C = read_vector_field(find("C"))
    return nonOrtho, aspect, skew, C


def band_stats(vals, C, xlo, xhi):
    idxs = [i for i, c in enumerate(C) if xlo <= c[0] < xhi]
    v = [vals[i] for i in idxs]
    return len(idxs), max(v), sum(v) / len(v)


def report(label, coarse, refined):
    nonOrtho_c, aspect_c, skew_c, C_c = coarse
    nonOrtho_r, aspect_r, skew_r, C_r = refined

    print("=== %s ===" % label)
    print("global max:  coarse   refined")
    print(
        "  nonOrtho   %8.3f %8.3f"
        % (max(nonOrtho_c), max(nonOrtho_r))
    )
    print("  aspect     %8.3f %8.3f" % (max(aspect_c), max(aspect_r)))
    print("  skewness   %8.3f %8.3f" % (max(skew_c), max(skew_r)))

    bands = [
        ("true LE nose        x in [-0.02, 0.05]", -0.02, 0.05),
        ("idx0/idx1 station   x in [0.20, 0.30] (FLAGGED, 9-16%, worsens)", 0.20, 0.30),
        ("idx2/idx3 station   x in [0.45, 0.55] (clean control)", 0.45, 0.55),
        ("idx4/idx5 station   x in [0.70, 0.80] (clean control)", 0.70, 0.80),
    ]
    for name, xlo, xhi in bands:
        n_c, max_c, mean_c = band_stats(aspect_c, C_c, xlo, xhi)
        n_r, max_r, mean_r = band_stats(aspect_r, C_r, xlo, xhi)
        print(
            "  ASPECT %-55s coarse: n=%4d max=%7.3f mean=%6.3f | refined: n=%4d max=%7.3f mean=%6.3f | max growth x%.3f"
            % (name, n_c, max_c, mean_c, n_r, max_r, mean_r, max_r / max_c)
        )
    for name, xlo, xhi in bands:
        n_c, max_c, mean_c = band_stats(nonOrtho_c, C_c, xlo, xhi)
        n_r, max_r, mean_r = band_stats(nonOrtho_r, C_r, xlo, xhi)
        print(
            "  NONORTHO %-53s coarse: n=%4d max=%7.3f mean=%6.3f | refined: n=%4d max=%7.3f mean=%6.3f | max growth x%.3f"
            % (name, n_c, max_c, mean_c, n_r, max_r, mean_r, max_r / max_c)
        )


if __name__ == "__main__":
    coarse_dir, refined_dir = sys.argv[1], sys.argv[2]
    coarse = load(coarse_dir)
    refined = load(refined_dir)
    report("A1 coarse (4032 cells) vs refined (14720 cells), LE-band mesh metrics", coarse, refined)
