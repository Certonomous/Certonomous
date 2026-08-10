#!/usr/bin/env python3
"""Ahmed 25 c3 leg 2: two more draws -> n = 4.

Pre-registration: campaign/R4_AHMED_C3_LEG2_PREREGISTRATION.md, commit
f4dec659, committed before any new mesh existed.

Mesh five candidates, screen on DELIVERED CELLS (before any Cd exists), solve
the two admitted draws closest to c3's 254,911. Scores R = s(without most
extreme)/s(all four) against the simulation-calibrated bar 0.28, then the
branch on WHICH draw is extreme.
"""
from __future__ import annotations
import json, math, re, shutil, sys, time
from datetime import datetime, timezone
from pathlib import Path

REPO=Path("/home/ubuntu/Certonomous"); sys.path.insert(0,str(REPO/"sdk"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_c3_replicates import (stage, mesh, solve, cd_of, C3_CELLS, TOL,
                               C3_CD, C4_CD, C4B_CD, PUBLISHED_INC, log, now, RUNS)

HERE=REPO/"demo-output/website/campaign/R4_runs"
CANDIDATES=[(99,21,59),(98,21,60),(97,21,59),(99,21,60),(100,21,59)]
C3B_CD=0.079827008
R_BAR=0.28

def sd(v):
    m=sum(v)/len(v); return math.sqrt(sum((x-m)**2 for x in v)/(len(v)-1))

def main():
    log("Ahmed c3 LEG 2 starting (prereg f4dec659): mesh 5, screen, solve 2")
    meshed=[]
    for i,div in enumerate(CANDIDATES):
        name=f"c3s{i}"
        r=stage(name,div); c=mesh(r,name); cells=c["cells"]
        dev=(cells-C3_CELLS)/C3_CELLS; ok=abs(dev)<=TOL
        meshed.append({"name":name,"divisions":list(div),"cells":cells,
                       "deviation":dev,"admitted":ok,"case":str(r),
                       "certificate":c})
        log(f"{name} {div} -> {cells} ({dev:+.2%}) {'ADMITTED' if ok else 'refused'}")
    admitted=sorted([m for m in meshed if m["admitted"]],
                    key=lambda m: abs(m["cells"]-C3_CELLS))
    log(f"admitted {len(admitted)} of {len(meshed)}")
    chosen=admitted[:2]
    for m in chosen:
        r=Path(m["case"]); m.update(solve(r,m["name"]))
        cd,n=cd_of(r); m["cd"]=cd; m["rows"]=n
        log(f"{m['name']}: Cd = {cd:.9f}")
        for f,dst in (("log.checkMesh",f"{m['name']}.log.checkMesh"),
                      ("constant/birth_certificate.json",f"{m['name']}.birth_certificate.json")):
            s=r/f
            if s.exists(): shutil.copy2(s, HERE/dst)

    draws={"c3_original":C3_CD,"c3b":C3B_CD}
    for m in chosen: draws[m["name"]]=m["cd"]
    vals=list(draws.values()); names=list(draws.keys()); n=len(vals)
    out={"prereg":"campaign/R4_AHMED_C3_LEG2_PREREGISTRATION.md",
         "prereg_commit":"f4dec659","timestamp":now(),
         "meshed_candidates":[{k:v for k,v in m.items() if k!="certificate"} for m in meshed],
         "draws":draws,"n_c3":n}
    if n>=3:
        s_all=sd(vals)
        mean=sum(vals)/n
        ex=max(range(n), key=lambda i: abs(vals[i]-mean))
        s_wo=sd([v for i,v in enumerate(vals) if i!=ex])
        R=s_wo/s_all
        extreme=names[ex]
        if R<=R_BAR:
            branch="B1" if extreme=="c3_original" else "B2"
            fault=("the PUBLISHED NUMBER: the recipe is not especially draw-sensitive and the "
                   "ladder's c3 entry is an unlucky draw") if branch=="B1" else \
                  ("the RECIPE: the published c3 is representative and the excursion is a state "
                   "the recipe occasionally lands in -- a bimodality that must travel on the "
                   "ladder's face. NOT an exoneration")
        else:
            branch, fault = "B3", ("BOTH: no single draw at this rung is trustworthy and the "
                   "increment cannot be read from single draws at all")
        c4m=(C4_CD+C4B_CD)/2; m3=sum(vals)/n; inc=c4m-m3; ratio=inc/PUBLISHED_INC
        mv=("SURVIVES" if (ratio>=0.75 and inc>0) else
            "DISSOLVES" if (ratio<0.50 or inc<=0) else "PARTIAL")
        out.update({"s_c3_all":s_all,"s_c3_without_extreme":s_wo,"R":R,"R_bar":R_BAR,
                    "extreme_draw":extreme,"branch":branch,"fault":fault,
                    "c3_mean":m3,"c4_mean":c4m,"reestimated_increment":inc,
                    "published_increment":PUBLISHED_INC,"ratio_to_published":ratio,
                    "increment_movement_branch":mv,
                    "NOT_A_SIGNAL_VERDICT":("T is not computed: the c4 CI leg was "
                        "deliberately not taken (prereg section 6).")})
        log(f"n={n} s_all={s_all:.4e} s_wo={s_wo:.4e} R={R:.3f} extreme={extreme} "
            f"-> {branch}; increment {inc:+.4e} ({ratio:.3f}x) -> {mv}")
    else:
        out["branch"]="SHORTFALL"
        out["fault"]=f"only {n} draws available; fewer than two candidates admitted"
        log(f"SHORTFALL: n={n}")
    (HERE/"c3_leg2_record.json").write_text(json.dumps(out,indent=2,sort_keys=True,default=str)+"\n")
    return 0

if __name__=="__main__": raise SystemExit(main())
