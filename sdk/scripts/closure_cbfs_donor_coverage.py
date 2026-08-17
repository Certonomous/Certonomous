#!/usr/bin/env python3
"""Does CBFS actually cover the NASA hump better than the periodic hills do?

    taskset -c 0-1 python3 sdk/scripts/closure_cbfs_donor_coverage.py

WHY THIS EXISTS
---------------
`closure_challenge_C6_hump_decision.md` (2026-08-01) withdrew the lab's
standing claim that "no alternative training-family model exists for
NASA_2DWMH". That withdrawal is right: `CBFS13700`, the curved backward-facing
step, ships as TRAINING data, and the pre-registered argument that picked the
periodic-hill model compared periodic hills against ducts only and never named
CBFS. The benchmark permits fitting on it, and so does the challenge preprint
(section 2.1, verified verbatim 2026-08-02: "You can train on similar flows to
the test cases").

But that document argued Route B on FLOW TOPOLOGY alone -- CBFS and the hump
are both two-dimensional smooth-wall flows that separate and reattach -- and
it never checked the one mechanism this lab has actually PROVEN binds its
models. Round 4 established it on the ducts: `Re_y` reaches 1.85x and 2.07x
its trained maximum on the two ducts the entry trails and 0.90x on the one it
leads, and a gradient-boosted tree cannot extrapolate. Topological similarity
is not the same claim as feature coverage, and this lab has already been
burned once by a plausible physical story that the numbers did not support.

THIS SCRIPT ASKS THE MEASURABLE VERSION OF THE QUESTION. Not "is CBFS more
hump-like?" but "would a CBFS-trained model be extrapolating on the hump any
less than the periodic-hill model already is?" Both donors are measured the
same way against the same target, on the same 7 features the entry actually
uses.

WHAT IS READ, AND WHAT IS NOT
-----------------------------
* NASA_2DWMH: `2000/{C,U,k,omega,walldist}` and `constant/polyMesh` only, with
  gradU reconstructed by Green-Gauss from mesh geometry. This is exactly what
  `train_closure_extended_correction._reconstruct_nasa_fields` already does
  and what `closure_criterion_on_test_features.py` already did.
  **`0/U_LES`, `0/k_LES` and `0/tauij_LES` are NEVER opened.** The scoring key
  is not touched, and no `closure_challenge.score()` or `evaluate_by_case()`
  call is made anywhere in this file -- it does not import the eval package.
* CBFS: `0/C`, `30000/{U,k,omega}` and `constant/polyMesh`, with BOTH gradU
  and walldist reconstructed (CBFS ships neither, same as the DUCT family).
  CBFS's own `0/U_LES` is legal to read -- it is a training case -- and is
  still not read here, because a coverage measurement does not need it and a
  file not opened cannot be argued about.
* The 21 periodic-hill TRAINING cases: as the entry already loads them.
  The 4 PH validation and 4 PH test cases are not loaded at all.

No model is fitted. Nothing is scored. This is feature aggregation and
interval arithmetic, and its whole output is a table.

Writes demo-output/website/closure_challenge_cbfs_donor_coverage.json.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

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

_SDK = Path(__file__).resolve().parents[1]
_REPO = _SDK.parent
_OUT = lab_paths.web_file("closure_challenge_cbfs_donor_coverage.json")

sys.path.insert(0, str(Path(__file__).resolve().parent))
import closure_mesh_recon as mr                       # noqa: E402
import train_closure_periodic_hill_correction as ph   # noqa: E402
import train_closure_extended_correction as ext       # noqa: E402

BENCHMARK_DIR = ph.BENCHMARK_DIR

# The scoring key, named so that a reader can grep for it and confirm no line
# below opens any of them.
_FORBIDDEN_ON_THE_TARGET = ("U_LES", "k_LES", "p_LES", "tauij_LES")


def _parse_internal_field():
    """The same OpenFOAM reader the entry uses, from the same place.

    `apply_closure_ph_gate.py` takes it from `Ofpp`; this takes it from the
    same module so the two cannot read the same file differently.
    """
    from Ofpp import parse_internal_field
    return parse_internal_field


def _cbfs_fields(parse_internal_field):
    """CBFS: C in 0/, U/k/omega in the solved time dir, gradU and walldist
    both reconstructed. Modelled directly on
    `train_closure_extended_correction._reconstruct_duct_fields`, which
    faces the identical situation and was validated before being trusted."""
    d = BENCHMARK_DIR / "data" / "CBFS"
    t = d / "30000"
    C = parse_internal_field(str(d / "0" / "C"))
    U = parse_internal_field(str(t / "U"))
    k = parse_internal_field(str(t / "k"))
    omega = parse_internal_field(str(t / "omega"))
    nu = ext._read_nu_duct_or_nasa(d)

    mesh = mr.Mesh(d)
    C_recon, V_recon = mr.reconstruct_cell_centres_vols(mesh)
    assert C_recon.shape[0] == C.shape[0] == U.shape[0], "CBFS: mesh/field size mismatch"
    u_boundary = mr.read_vector_boundary_field(t / "U", list(mesh.boundary.keys()))
    gradU = mr.green_gauss_grad_u(mesh, U, C_recon, V_recon, u_boundary)
    wall_patches = [n for n, m in mesh.boundary.items() if m["type"] == "wall"]
    walldist = mr.compute_wall_distance(mesh, C_recon, wall_patches)
    return dict(C=C, U=U, gradU=gradU, k=k, omega=omega, walldist=walldist, nu=nu)


def _reynolds_from_comment(path: Path) -> str | None:
    """The benchmark states each case's Reynolds number as a trailing comment
    on the nu line. Quoted, not inferred."""
    try:
        text = path.read_text()
    except OSError:
        return None
    m = re.search(r"nu\s*\[[^\]]*\]\s*[0-9eE+\-.]+\s*;[ \t]*//[ \t]*(.+)", text)
    if not m:
        return None
    stated = m.group(1).strip()
    # NASA_2DWMH's nu line carries no Reynolds comment, and a loose regex
    # happily returns the file's asterisk footer instead. A banner is not a
    # measurement; return nothing rather than publish one.
    if not re.search(r"[0-9]", stated) or set(stated) <= set("*/ "):
        return None
    return stated


def _regime(X: np.ndarray) -> dict:
    """A donor's trained regime, per feature: the hard interval its cells span
    and a robust p1/p99 interior, so the verdict does not hinge on one cell."""
    return {
        "min": X.min(axis=0).tolist(),
        "max": X.max(axis=0).tolist(),
        "p1": np.percentile(X, 1, axis=0).tolist(),
        "p99": np.percentile(X, 99, axis=0).tolist(),
    }


def _coverage(target: np.ndarray, reg: dict) -> dict:
    """How far outside a donor's regime the target sits, per feature.

    `frac_outside` is the share of target cells beyond the donor's hard
    [min,max]; `reach` is how far the target's own p99 (or p1, whichever side
    it exceeds) goes past the donor's edge, as a multiple of the donor's
    half-range. Both are computed the same way for every donor, so the two
    columns are comparable to each other -- which is the entire point.
    """
    lo = np.array(reg["min"])
    hi = np.array(reg["max"])
    frac = ((target < lo) | (target > hi)).mean(axis=0)
    span = np.maximum(hi - lo, 1e-30)
    t99 = np.percentile(target, 99, axis=0)
    t01 = np.percentile(target, 1, axis=0)
    over = np.maximum((t99 - hi) / span, (lo - t01) / span)
    return {"frac_outside": frac.tolist(), "reach_beyond_edge_in_spans": over.tolist()}


def main() -> int:
    pif = _parse_internal_field()
    names = ph.FEATURE_NAMES

    hump_dir = BENCHMARK_DIR / "data" / "NASA_2DWMH"
    cbfs_dir = BENCHMARK_DIR / "data" / "CBFS"

    print("[data] periodic-hill donor: 21 training cases")
    ph_parts = []
    for c in ph._PH_TRAIN:
        f = ph._load_rans_fields(c, pif)
        ph_parts.append(ph.build_features(f["gradU"], f["k"], f["omega"],
                                          f["walldist"], f["U"], f["nu"]))
    X_ph = np.concatenate(ph_parts, axis=0)
    print(f"       {len(ph._PH_TRAIN)} cases, {X_ph.shape[0]:,} cells")

    print("[data] CBFS donor: 1 training case, gradU and walldist reconstructed")
    fc = _cbfs_fields(pif)
    X_cbfs = ph.build_features(fc["gradU"], fc["k"], fc["omega"],
                               fc["walldist"], fc["U"], fc["nu"])
    print(f"       1 case, {X_cbfs.shape[0]:,} cells, nu={fc['nu']:.6g}")

    print("[data] target: NASA_2DWMH, RANS fields and mesh only, no ground truth")
    fh = ext._reconstruct_nasa_fields("NASA_2DWMH", pif)
    X_hump = ph.build_features(fh["gradU"], fh["k"], fh["omega"],
                               fh["walldist"], fh["U"], fh["nu"])
    print(f"       {X_hump.shape[0]:,} cells, nu={fh['nu']:.6g}")

    reg_ph, reg_cbfs = _regime(X_ph), _regime(X_cbfs)
    cov_ph = _coverage(X_hump, reg_ph)
    cov_cbfs = _coverage(X_hump, reg_cbfs)

    n_out_ph = sum(1 for v in cov_ph["frac_outside"] if v > 0)
    n_out_cbfs = sum(1 for v in cov_cbfs["frac_outside"] if v > 0)

    print("\n=== hump coverage, per feature ===")
    print(f"{'feature':<10} {'PH out':>9} {'CBFS out':>9} {'PH reach':>10} {'CBFS reach':>11}  better")
    rows = []
    for i, nm in enumerate(names):
        pf, cf = cov_ph["frac_outside"][i], cov_cbfs["frac_outside"][i]
        pr, cr = cov_ph["reach_beyond_edge_in_spans"][i], cov_cbfs["reach_beyond_edge_in_spans"][i]
        better = "CBFS" if cf < pf - 1e-12 else ("PH" if pf < cf - 1e-12 else "tie")
        rows.append({"feature": nm, "frac_outside_ph": pf, "frac_outside_cbfs": cf,
                     "reach_ph": pr, "reach_cbfs": cr, "better_donor": better})
        print(f"{nm:<10} {pf:>9.4f} {cf:>9.4f} {pr:>10.3g} {cr:>11.3g}  {better}")

    wins_cbfs = sum(1 for r in rows if r["better_donor"] == "CBFS")
    wins_ph = sum(1 for r in rows if r["better_donor"] == "PH")

    # The plain physical fact the topology argument left out, quoted from the
    # benchmark's own transportProperties comments rather than paraphrased.
    re_cbfs = _reynolds_from_comment(cbfs_dir / "constant" / "transportProperties")
    re_hump = _reynolds_from_comment(hump_dir / "constant" / "transportProperties")

    verdict = (
        f"On the hump, {n_out_ph} of 7 features fall outside the periodic-hill "
        f"donor's trained range and {n_out_cbfs} of 7 fall outside CBFS's. CBFS "
        f"is the better donor on {wins_cbfs} of 7 features and the periodic hills "
        f"on {wins_ph}."
    )
    print("\n=== verdict ===")
    print(verdict)

    record = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": ("Test the premise of Route B in closure_challenge_C6_hump_decision.md "
                    "section 5 -- that CBFS13700 is a better training donor for NASA_2DWMH "
                    "than the periodic hills -- against feature coverage, which is the "
                    "mechanism this lab has proven binds its models, rather than against "
                    "flow topology, which is what that document argued from."),
        "leakage_statement": {
            "target_ground_truth_read": False,
            "forbidden_files_on_the_target": list(_FORBIDDEN_ON_THE_TARGET),
            "closure_challenge_score_call_made": False,
            "eval_package_imported_for_scoring": False,
            "model_fitted": False,
            "note": ("NASA_2DWMH is read for 2000/{C,U,k,omega,walldist} and its polyMesh "
                     "only, with gradU reconstructed by Green-Gauss -- the identical read "
                     "set that round 2 and closure_criterion_on_test_features.py already "
                     "use. CBFS's own U_LES is legal to read (it is a training case) and "
                     "is still not read, because a coverage measurement does not need it."),
        },
        "features": names,
        "donors": {
            "periodic_hills_21_train": {
                "cases": ph._PH_TRAIN, "n_cases": len(ph._PH_TRAIN),
                "n_cells": int(X_ph.shape[0]), "regime": reg_ph,
            },
            "CBFS13700": {
                "cases": ["CBFS"], "n_cases": 1,
                "n_cells": int(X_cbfs.shape[0]), "nu": fc["nu"],
                "reynolds_as_stated_by_the_benchmark": re_cbfs,
                "gradU_and_walldist": "reconstructed from mesh geometry; ships neither",
                "regime": reg_cbfs,
            },
        },
        "target": {
            "case": "NASA_2DWMH", "n_cells": int(X_hump.shape[0]), "nu": fh["nu"],
            "reynolds_as_stated_by_the_benchmark": re_hump,
        },
        "coverage": {"periodic_hills_21_train": cov_ph, "CBFS13700": cov_cbfs},
        "per_feature": rows,
        "summary": {
            "n_features_outside_ph_range": n_out_ph,
            "n_features_outside_cbfs_range": n_out_cbfs,
            "features_where_cbfs_covers_better": wins_cbfs,
            "features_where_ph_covers_better": wins_ph,
            "cbfs_training_cells": int(X_cbfs.shape[0]),
            "ph_training_cells": int(X_ph.shape[0]),
            "training_cell_ratio_ph_over_cbfs": float(X_ph.shape[0]) / float(X_cbfs.shape[0]),
        },
        "verdict": verdict,
    }
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"\n[write] {_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
