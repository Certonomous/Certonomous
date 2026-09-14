#!/usr/bin/env python3
"""The operator indices, recomputed on the GRADED transient fine level K2h_L3.

    python3 docs/campaigns/F14-cooling-ladder/demo/plots_K2_transient/make_k2t_indices.py

Reads `110/TMean` -- the mean over the registered 42 -> 112 s window, written at the
last written time -- through the frozen `foam_patch_reader.area_average`, on the
run's own patches. This run has NO mdot-weighted inlet function objects (its
postProcessing holds dp_tile and dp_return only), so the patch average on
rack{i}_in is the inlet definition, as SIDECAR.md states.
"""
import csv, os, sys, hashlib
REPO="/home/ubuntu/Certonomous"
sys.path.insert(0, os.path.join(REPO,"verification/runs/F14-cooling-ladder/K2g_runs"))
import foam_patch_reader as FR
R=os.path.join(REPO,"verification/runs/F14-cooling-ladder/K2h_runs/K2h_L3")
OUT=os.path.join(REPO,"docs/campaigns/F14-cooling-ladder/demo/plots_K2_transient")
K=273.15; T=110; F="TMean"
def A(p): return FR.area_average(R,T,F,p)[0]
Tsup=A("tile"); Tret=A("return")
rows=[]
for i in range(4):
    Tin=A("rack%d_in"%i); Tout=A("rack%d_out"%i)
    rec=100.0*(Tin-Tsup)/(Tout-Tsup); cap=100.0-rec
    rci=100.0 if (Tin-K)<=27.0 else max(0.0,100.0*(1-(Tin-K-27.0)/5.0))
    rows.append(["rack %d"%(i+1),Tin-K,Tout-K,rci,cap,rec,Tout-Tin])
dT=sum(r[6] for r in rows)/4.0
rti=100.0*(Tret-Tsup)/dT
hot=max(rows,key=lambda r:r[1]); spread=hot[1]-min(r[1] for r in rows)
with open(os.path.join(OUT,"k2t_indices.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["rack","T_inlet_degC","T_outlet_degC","RCI_high_pct","capture_index_pct","recirculation_pct","dT_rack_K"]); w.writerows(rows)
with open(os.path.join(OUT,"k2t_indices_room.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["T_supply_degC","T_return_degC","room_rise_K","RTI_pct","hottest_inlet_degC","hottest_rack","spread_K"])
    w.writerow([Tsup-K,Tret-K,Tret-Tsup,rti,hot[1],hot[0],spread])
print("supply %.3f  return %.3f  rise %.3f  RTI %.2f"%(Tsup-K,Tret-K,Tret-Tsup,rti))
for r in rows: print("%s  in %.3f  out %.3f  cap %.2f  rec %.2f  dT %.3f"%(r[0],r[1],r[2],r[4],r[5],r[6]))
print("hottest %s %.3f  spread %.3f"%(hot[0],hot[1],spread))
h=hashlib.sha256(open(os.path.join(R,"110","TMean"),"rb").read()).hexdigest()
print("TMean sha256",h)
