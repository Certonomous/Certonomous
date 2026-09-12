#!/usr/bin/env python3
"""Detached observer for K2h_L3. READ-ONLY on the case. Never signals the solver."""
import os,re,sys,time,json,subprocess
CASE="/home/ubuntu/Certonomous/verification/runs/F14-cooling-ladder/K2h_runs/K2h_L3"
LOG=os.path.join(CASE,"log.solve")
OUT=os.path.join(CASE,"WATCH.lane.K2h_L3.tsv")
PID=24659
ENDTIME=112.0
CAP_CORE_MIN=1260.0
POINT_CORE_MIN=420.0
RANKS=4
def alive(p):
    try: os.kill(p,0); return True
    except Exception: return False
def parse():
    """Split log at Build banners; return per-segment stats."""
    segs=[];cur=None
    with open(LOG,errors='replace') as f:
        for l in f:
            if l.startswith('Build  :'):
                cur={'T':[],'D':[],'E':[],'end':False,'bad':[]};segs.append(cur)
            if cur is None: continue
            if l.startswith('Time = '):
                try: cur['T'].append(float(l.split('=')[1]))
                except: pass
            elif l.startswith('deltaT = '):
                try: cur['D'].append(float(l.split('=')[1]))
                except: pass
            elif l.startswith('ExecutionTime = '):
                try: cur['E'].append(float(l.split('=')[1].split('s')[0]))
                except: pass
            elif l.startswith('End'):
                cur['end']=True
            else:
                ll=l.lower()
                if 'trapfpe' in ll or 'sigfpe' in ll or 'kinf' in ll or 'omegainf' in ll:
                    continue
                if ('nan' in ll or 'inf ' in ll or 'floating point exception' in ll
                    or 'segmentation' in ll or 'fatal' in ll or 'signal ' in ll
                    or 'diverg' in ll):
                    if len(cur['bad'])<200: cur['bad'].append(l.rstrip()[:300])
    return segs
# THE ACCUMULATOR'S REAL PATH, read out of OpenFOAM 2606's own source, NOT the
# path this lane's brief named.  `fieldAverage::writeAveragingProperties` ->
# `setProperty` -> `functionObjectList::createPropertiesDict` (functionObjectList.C
# :98-100) puts the state in <time>/uniform/functionObjects/functionObjectProperties.
# `<time>/uniform/fieldAverageProperties` DOES NOT EXIST in this version and a
# watcher looking for it would have escalated a FALSE absence at t=45.
#
# AND A PRESENCE TEST ON THAT FILE IS WORTHLESS: it exists from the first write
# at t=5, carrying the OTHER function objects' state.  What is counted here is
# the `dpAverage` BLOCK inside it -- the fieldAverage function object named in
# system/controlDict:39.
FA_REL = os.path.join("uniform", "functionObjects", "functionObjectProperties")
FA_FO  = "dpAverage"

def _has_block(path, key):
    try:
        txt = open(path, errors="replace").read()
    except OSError:
        return False
    return re.search(r"(?m)^\s*" + re.escape(key) + r"\s*$\s*\{", txt) is not None \
        or re.search(re.escape(key) + r"\s*\{", txt) is not None

def fa_ranks():
    r={}
    for i in range(RANKS):
        pd=os.path.join(CASE,f"processor{i}")
        hits=[]
        if os.path.isdir(pd):
            for d in os.listdir(pd):
                try: t=float(d)
                except: continue
                fp=os.path.join(pd,d,FA_REL)
                if os.path.exists(fp) and _has_block(fp, FA_FO):
                    hits.append(t)
        r[i]=sorted(hits)
    return r
def times_written():
    pd=os.path.join(CASE,"processor0"); out=[]
    if os.path.isdir(pd):
        for d in os.listdir(pd):
            try: out.append(float(d))
            except: pass
    return sorted(out)
hdr=("iso\tsolver_alive\tseg\tsim_t\tsteps_seg\texec_seg_s\tsps\tdeltaT\t"
     "core_min_total\tvs_point\tvs_cap\tfa_ranks\tlast_write\tnote\n")
if not os.path.exists(OUT) or os.path.getsize(OUT)==0:
    open(OUT,'w').write(hdr)
fa_escalated=False
while True:
    iso=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
    a=alive(PID)
    try: segs=parse()
    except Exception as e:
        open(OUT,'a').write(f"{iso}\t{a}\tPARSE_ERR\t\t\t\t\t\t\t\t\t\t\t{e}\n"); time.sleep(120); continue
    notes=[]
    tot_exec=sum((s['E'][-1] if s['E'] else 0.0) for s in segs)
    core_min=tot_exec*RANKS/60.0
    s=segs[-1] if segs else None
    simt=s['T'][-1] if (s and s['T']) else float('nan')
    nst=len(s['T']) if s else 0
    ex=s['E'][-1] if (s and s['E']) else 0.0
    sps=(ex/len(s['E'])) if (s and s['E']) else float('nan')
    dt=s['D'][-1] if (s and s['D']) else float('nan')
    fa=fa_ranks()
    tw=times_written()
    lastw=tw[-1] if tw else float('nan')
    nfa=[len(fa[i]) for i in range(RANKS)]
    # fieldAverage timeStart is 42 and writeControl is writeTime, so the
    # accumulator first lands at the t=45 WRITE, not at t=42. Only check once a
    # write at or past 45 exists, else the check is a false alarm by construction.
    if lastw==lastw and lastw>=45.0:
        if len(set(nfa))!=1 or nfa[0]==0:
            notes.append(f"FA_RANK_MISMATCH counts={nfa}")
            fa_escalated=True
    for seg in segs:
        if seg['bad']: notes.append("BADLINES="+str(len(seg['bad'])))
    if core_min>CAP_CORE_MIN: notes.append("CAP_CROSSED")
    if not a:
        ended=any(x['end'] for x in segs)
        notes.append("SOLVER_GONE_END" if ended else "SOLVER_GONE_NO_END")
    open(OUT,'a').write(
        f"{iso}\t{a}\t{len(segs)}\t{simt:.4f}\t{nst}\t{ex:.2f}\t{sps:.4f}\t{dt:.9f}\t"
        f"{core_min:.1f}\t{core_min/POINT_CORE_MIN:.2f}\t{core_min/CAP_CORE_MIN:.2f}\t"
        f"{','.join(map(str,nfa))}\t{lastw}\t{';'.join(notes) if notes else '-'}\n")
    if not a:
        break
    time.sleep(120)
