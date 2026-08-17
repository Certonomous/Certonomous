import sys, os, json, numpy as np

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

def lasttime(c):
    ts=[int(d) for d in os.listdir(c) if d.isdigit() and d!='0']
    return str(max(ts))

def caseUbar(c):
    d=dict()
    for ln in open(f'{c}/caseDef'):
        p=ln.split('//')[0].split()
        if len(p)>=2: d[p[0]]=p[1].rstrip(';')
    return float(d['Re_b'])*float(d['nu'])/float(d['h'])

rows={}
for case,(sd,qd) in {
  'AR_1_Ret_180':('sst','sst_qcr'),
  'AR_3_Ret_180':('AR_3_Ret_180_sst','AR_3_Ret_180_qcr'),
  'AR_5_Ret_180':('AR_5_Ret_180_sst','AR_5_Ret_180_qcr'),
  'AR_10_Ret_180':('AR_10_Ret_180_sst','AR_10_Ret_180_qcr')}.items():
    Ubar=caseUbar(sd)
    Ules=read_of_vector_field(f'{sd}/0/U_LES')
    den=np.mean(np.linalg.norm(Ules,axis=1))
    r={'Ubar_ms':Ubar,'n_cells':int(Ules.shape[0])}
    secles=np.hypot(Ules[:,1],Ules[:,2])
    r['ref_sec_rms_pct_Ubar']=float(100*np.sqrt(np.mean(secles**2))/Ubar)
    for tag,d in (('sst',sd),('qcr',qd)):
        U=read_of_vector_field(f'{d}/{lasttime(d)}/U')
        sec=np.hypot(U[:,1],U[:,2])
        r[f'{tag}_sec_rms_pct_Ubar']=float(100*np.sqrt(np.mean(sec**2))/Ubar)
        # challenge-form metric: mean(||dU||_2)/mean(||U_true||_2), all cells
        r[f'{tag}_scaledMAE']=float(np.mean(np.linalg.norm(U-Ules,axis=1))/den)
        a=U[:,1:3].ravel(); b=Ules[:,1:3].ravel()
        r[f'{tag}_inplane_r']=float(np.corrcoef(a,b)[0,1]) if a.std()>0 else 0.0
        r[f'{tag}_inplane_rms_ratio']=float(np.sqrt(np.mean(a**2))/np.sqrt(np.mean(b**2)))
    r['scaledMAE_delta']=r['qcr_scaledMAE']-r['sst_scaledMAE']
    r['scaledMAE_pct_change']=100*r['scaledMAE_delta']/r['sst_scaledMAE']
    rows[case]=r
print(json.dumps(rows,indent=2))
json.dump(rows,open('eval_battery.json','w'),indent=2)
print()
print(f"{'case':16s} {'SST sec%':>9s} {'QCR sec%':>9s} {'ref sec%':>9s} {'SST sMAE':>9s} {'QCR sMAE':>9s} {'change':>8s} {'r':>6s}")
for k,v in rows.items():
    print(f"{k:16s} {v['sst_sec_rms_pct_Ubar']:9.2e} {v['qcr_sec_rms_pct_Ubar']:9.4f} {v['ref_sec_rms_pct_Ubar']:9.4f} {v['sst_scaledMAE']:9.4f} {v['qcr_scaledMAE']:9.4f} {v['scaledMAE_pct_change']:7.1f}% {v['qcr_inplane_r']:6.3f}")
