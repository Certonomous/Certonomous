import sys, re, json, numpy as np

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[3]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402
sys.path.insert(0, str(lab_paths.DAFOAM / "ladder-b" / "duct_baseline"))
from duct_secondary_flow import read_of_vector_field

Ubar = 37.5  # fvOptions meanVelocityForce target, Re_b*nu/h = 2500*1.5e-5/1e-3

def vols(case):
    # cell volumes via writeCellVolumes would need a rerun; use uniform weights
    # and report both normalisations honestly instead.
    return None

out={}
Ules = read_of_vector_field('sst/0/U_LES')
sec_les = np.hypot(Ules[:,1],Ules[:,2])
for c in ['sst','sst_qcr']:
    U = read_of_vector_field(f'{c}/401/U')
    sec = np.hypot(U[:,1],U[:,2])
    out[c]={
     'n_cells':int(U.shape[0]),
     'sec_rms_ms':float(np.sqrt(np.mean(sec**2))),
     'sec_max_ms':float(sec.max()),
     'sec_rms_pct_Ubar375':float(100*np.sqrt(np.mean(sec**2))/Ubar),
     'sec_max_pct_Ubar375':float(100*sec.max()/Ubar),
     'Ux_mean_ms':float(U[:,0].mean()),
     # component-wise MAE of the in-plane vector against the reference field
     'inplane_MAE_vs_LES_ms':float(np.mean(np.abs(U[:,1:3]-Ules[:,1:3]))),
     'inplane_MAE_vs_LES_pct_Ubar':float(100*np.mean(np.abs(U[:,1:3]-Ules[:,1:3]))/Ubar),
     'streamwise_MAE_vs_LES_ms':float(np.mean(np.abs(U[:,0]-Ules[:,0]))),
     'streamwise_MAE_vs_LES_pct_Ubar':float(100*np.mean(np.abs(U[:,0]-Ules[:,0]))/Ubar),
     'full_U_MAE_vs_LES_pct_Ubar':float(100*np.mean(np.abs(U-Ules))/Ubar),
    }
out['reference_LES']={
 'sec_rms_ms':float(np.sqrt(np.mean(sec_les**2))),
 'sec_max_ms':float(sec_les.max()),
 'sec_rms_pct_Ubar375':float(100*np.sqrt(np.mean(sec_les**2))/Ubar),
 'sec_max_pct_Ubar375':float(100*sec_les.max()/Ubar),
 'Ux_mean_ms':float(Ules[:,0].mean()),
}
# correlation of the in-plane field direction/magnitude
Uq = read_of_vector_field('sst_qcr/401/U')
a=Uq[:,1:3].ravel(); b=Ules[:,1:3].ravel()
out['sst_qcr']['inplane_pearson_r_vs_LES']=float(np.corrcoef(a,b)[0,1])
out['sst_qcr']['inplane_rms_ratio_vs_LES']=float(np.sqrt(np.mean(a**2))/np.sqrt(np.mean(b**2)))
print(json.dumps(out,indent=2))
json.dump(out,open('falsifier_result.json','w'),indent=2)
