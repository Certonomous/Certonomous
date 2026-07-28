import sys
sys.path.insert(0, "/home/ubuntu/closure-challenge-pkg/src")
from pathlib import Path
from Ofpp import parse_internal_field
import numpy as np

HERE = Path("/home/ubuntu/Certonomous/demo-output/website/dafoam/ladder-b/duct_baseline/CBFS")
REF = Path("/home/ubuntu/closure-challenge-benchmark/data/CBFS")

coords_ours = parse_internal_field(str(HERE / "0" / "C"))
coords_ref = parse_internal_field(str(REF / "0" / "C"))
u_ours = parse_internal_field(str(HERE / "30000" / "U"))
u_ref = parse_internal_field(str(REF / "30000" / "U"))

print("cells ours:", coords_ours.shape[0], "ref:", coords_ref.shape[0])
print("max coord diff:", np.abs(coords_ours - coords_ref).max())

u_mag_ref = np.linalg.norm(u_ref, axis=1)
u_mag_diff = np.linalg.norm(u_ours - u_ref, axis=1)
scaled_mae = np.mean(u_mag_diff) / np.mean(u_mag_ref)
print("internal field scaled MAE (ours vs benchmark RANS baseline):", scaled_mae)

# also compare against LES reference tauij_LES/U_LES if present in 0/
try:
    u_les = parse_internal_field(str(REF / "0" / "U_LES"))
    mae_ours_vs_les = np.mean(np.linalg.norm(u_ours - u_les, axis=1)) / np.mean(np.linalg.norm(u_les, axis=1))
    mae_ref_vs_les = np.mean(np.linalg.norm(u_ref - u_les, axis=1)) / np.mean(np.linalg.norm(u_les, axis=1))
    print("ours vs LES scaled MAE:", mae_ours_vs_les)
    print("benchmark RANS baseline vs LES scaled MAE:", mae_ref_vs_les)
except Exception as e:
    print("LES comparison skipped:", e)
