"""Validation harness for closure_mesh_recon.py.

Checks, in order, before any reconstructed field is trusted for use in
training/inference:

  1. Cell centres/volumes reconstructed purely from mesh geometry
     (points/faces/owner/neighbour) match the benchmark's own shipped C
     and V fields, on a DUCT case (which ships both).
  2. Green-Gauss gradU reconstructed from mesh geometry + the RANS U field
     matches the benchmark's own shipped gradU, on a periodic-hills
     TRAINING case (never a test case) that ships gradU.
  3. Nearest-wall-face-centre wall-distance reconstruction matches the
     benchmark's own shipped walldist, on the same periodic-hills case.

No ground truth (U_LES) is touched anywhere in this script.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

_SDK = Path(__file__).resolve().parent
sys.path.insert(0, str(_SDK))
import closure_mesh_recon as mr

_DEFAULT_BENCHMARK_DIR = Path.home() / "closure-challenge-benchmark"
_DEFAULT_EVAL_PKG_DIR = Path.home() / "closure-challenge-pkg"
BENCHMARK_DIR = Path(os.environ.get("CLOSURE_BENCHMARK_DIR", str(_DEFAULT_BENCHMARK_DIR)))
EVAL_PKG_DIR = Path(os.environ.get("CLOSURE_EVAL_PKG_DIR", str(_DEFAULT_EVAL_PKG_DIR)))


def check_1_cell_geometry():
    print("=== CHECK 1: cell centres/volumes reconstruction vs shipped C/V (DUCT AR_1_Ret_360) ===")
    case_dir = BENCHMARK_DIR / "data" / "DUCT" / "AR_1_Ret_360"
    from Ofpp import parse_internal_field
    C_shipped = parse_internal_field(str(case_dir / "constant" / "C"))
    V_shipped = parse_internal_field(str(case_dir / "constant" / "V"))

    mesh = mr.Mesh(case_dir)
    C_recon, V_recon = mr.reconstruct_cell_centres_vols(mesh)

    assert C_recon.shape[0] == C_shipped.shape[0] == mesh.num_cell

    c_err = np.linalg.norm(C_recon - C_shipped, axis=1)
    c_scale = np.linalg.norm(C_shipped, axis=1).mean()
    v_err = np.abs(V_recon - V_shipped)

    print(f"  n_cell={mesh.num_cell}")
    print(f"  C: max |err| = {c_err.max():.3e}, mean |err| = {c_err.mean():.3e}, "
          f"(coord scale ~ {c_scale:.3e})")
    print(f"  V: max |err| = {v_err.max():.3e}, mean |err| = {v_err.mean():.3e}, "
          f"sum(V_recon)={V_recon.sum():.6e} sum(V_shipped)={V_shipped.sum():.6e}")
    ok = c_err.max() < 1e-6 * max(c_scale, 1.0) and v_err.max() < 1e-9
    print(f"  VERDICT: {'PASS' if ok else 'FAIL'}")
    return ok


def check_2_and_3_gradu_walldist():
    print("\n=== CHECK 2/3: Green-Gauss gradU + wall-distance vs shipped ground truth "
          "(PH TRAINING case alpha_05_7071_3036, never a test/val case) ===")
    from Ofpp import parse_internal_field
    case_dir = BENCHMARK_DIR / "data" / "Parm_PH_29" / "alpha_05" / "alpha_05_7071_3036"
    t = case_dir / "20000"

    U = parse_internal_field(str(t / "U"))
    gradU_shipped = parse_internal_field(str(t / "gradU"))
    walldist_shipped = parse_internal_field(str(t / "walldist"))

    mesh = mr.Mesh(case_dir)
    C_recon, V_recon = mr.reconstruct_cell_centres_vols(mesh)

    u_boundary = mr.read_vector_boundary_field(t / "U", list(mesh.boundary.keys()))
    gradU_recon = mr.green_gauss_grad_u(mesh, U, C_recon, V_recon, u_boundary)

    diff = gradU_recon - gradU_shipped
    fro_err = np.linalg.norm(diff, axis=1)
    fro_true = np.linalg.norm(gradU_shipped, axis=1)
    rel_err = fro_err / np.maximum(fro_true, 1e-8)
    # Pooled relative error (avoids blowup at near-zero-gradient cells)
    pooled_rel = fro_err.sum() / fro_true.sum()
    r2 = 1.0 - np.sum(diff ** 2) / np.sum((gradU_shipped - gradU_shipped.mean(axis=0)) ** 2)

    print(f"  n_cell={mesh.num_cell}")
    print(f"  gradU: pooled relative Frobenius error = {pooled_rel:.4f}")
    print(f"  gradU: median per-cell relative error = {np.median(rel_err):.4f}, "
          f"90th pct = {np.percentile(rel_err, 90):.4f}")
    print(f"  gradU: R^2 (all 9 components pooled) = {r2:.4f}")
    corr = np.corrcoef(gradU_recon.ravel(), gradU_shipped.ravel())[0, 1]
    print(f"  gradU: Pearson correlation (all 9 components pooled) = {corr:.4f}")
    gradu_ok = pooled_rel < 0.35 and corr > 0.85

    wall_patch_names = [n for n, m in mesh.boundary.items() if m["type"] == "wall"]
    print(f"  wall patches used: {wall_patch_names}")
    walldist_recon = mr.compute_wall_distance(mesh, C_recon, wall_patch_names)
    wd_err = np.abs(walldist_recon - walldist_shipped)
    wd_scale = walldist_shipped.mean()
    wd_corr = np.corrcoef(walldist_recon, walldist_shipped)[0, 1]
    print(f"  walldist: mean |err| = {wd_err.mean():.4e} (mean walldist scale {wd_scale:.4e}), "
          f"max |err| = {wd_err.max():.4e}")
    print(f"  walldist: Pearson correlation = {wd_corr:.4f}")
    walldist_ok = wd_corr > 0.98 and wd_err.mean() < 0.15 * wd_scale

    print(f"  VERDICT gradU: {'PASS' if gradu_ok else 'FAIL'}")
    print(f"  VERDICT walldist: {'PASS' if walldist_ok else 'FAIL'}")
    return gradu_ok, walldist_ok


def main():
    if str(EVAL_PKG_DIR / "src") not in sys.path:
        sys.path.insert(0, str(EVAL_PKG_DIR / "src"))
    ok1 = check_1_cell_geometry()
    ok2, ok3 = check_2_and_3_gradu_walldist()
    print(f"\n=== SUMMARY: geometry={ok1} gradU={ok2} walldist={ok3} ===")


if __name__ == "__main__":
    main()
