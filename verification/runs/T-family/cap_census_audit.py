#!/usr/bin/env python3
"""cap_census_audit.py -- has any heat-transfer case ever exceeded a REGISTERED CAP?

Instrument of record for docs/campaigns/T-family/CAP_CENSUS_2026-08-27.md.
Written 2026-08-27 by a heat-transfer lane under the supervisor's cap-census order.

WHAT IT MEASURES
    ACTUAL core-minutes, from the case's own STATUS or DONE record: core_min if the
    record carries it, else wall x ranks / 60. MEASURED, never a monitor label.

WHAT COUNTS AS A CAP, AND WHAT NEVER DOES
    A cap is taken ONLY from
      (1) <rung>/*_registered.json  cases.<case>.cap_core_min, or
      (2) a launcher-written cap_core_min inside the run record itself, or
      (3) PROSE_CAP below -- a per-case figure transcribed from a pre-registration,
          each carrying the document and line it was read from.
    CAP_OVERRUN.txt is NEVER a cap source. It was measured on 2026-08-27 to quote a
    case's POINT ESTIMATE under the word "registered" (T4b_IJ_c: 710 s = point 11.84
    core-min, against an actual cap of 25), so a census built on that label would
    manufacture breaches out of mispredictions. A queue entry's cost_core_min_estimate
    is never a cap either, for the same reason.

WHY THE PLANTED ARMS EXIST (CLAUDE.md rule 3)
    This audit's headline is a ZERO. A zero from a reader never shown able to see a
    non-zero is not evidence. --selftest plants a known breach and a known sub-cap
    value and REFUSES unless the reader fires on the first and stays silent on the
    second.
"""
from __future__ import annotations
import json, os, re, glob, sys, argparse

ROOT = os.environ.get("CAP_AUDIT_ROOT", "/home/ubuntu/Certonomous")
TREES = ["verification/runs/T-family",
         "verification/runs/THERMAL_K0_runs",
         "verification/runs/F14-cooling-ladder"]
SKIP = re.compile(r'(attempt1|attempt2|_stale|_FAILED|CRASHED|\.attempt|crash_|__pycache__|queue_|PRESERVED)')
TOK = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)')

# --- per-case caps that exist ONLY as prose in a pre-registration. Each row is
# --- (cap_core_min, source document, line, verbatim table row). Transcribed, never derived.
K0F = "docs/campaigns/F14-cooling-ladder/K0f_PREREGISTRATION.md"
T5P = "docs/campaigns/T-family/T5_PREREGISTRATION.md"
PROSE_CAP = {
 ("K0f_runs","M1_c"):(435.00,K0F,1107,"| `M1_c`, `M2_c` | 435.00 | 26 100 |"),
 ("K0f_runs","M2_c"):(435.00,K0F,1107,"| `M1_c`, `M2_c` | 435.00 | 26 100 |"),
 ("K0f_runs","M1_m"):(852.70,K0F,1108,"| `M1_m`, `M2_m`, `B_hi`, `I_hi`, `M1_m_seed` | 852.70 | 51 161 |"),
 ("K0f_runs","M2_m"):(852.70,K0F,1108,"| `M1_m`, `M2_m`, `B_hi`, `I_hi`, `M1_m_seed` | 852.70 | 51 161 |"),
 ("K0f_runs","B_hi"):(852.70,K0F,1108,"| `M1_m`, `M2_m`, `B_hi`, `I_hi`, `M1_m_seed` | 852.70 | 51 161 |"),
 ("K0f_runs","I_hi"):(852.70,K0F,1108,"| `M1_m`, `M2_m`, `B_hi`, `I_hi`, `M1_m_seed` | 852.70 | 51 161 |"),
 ("K0f_runs","M1_m_seed"):(852.70,K0F,1108,"| `M1_m`, `M2_m`, `B_hi`, `I_hi`, `M1_m_seed` | 852.70 | 51 161 |"),
 ("K0f_runs","C_lam"):(639.50,K0F,1109,"| `C_lam` | 639.50 | 38 370 |"),
 ("K0f_runs","M1_f"):(1675.50,K0F,1110,"| **`M1_f`, `M2_f`** | **1 675.50** | **100 530** |"),
 ("K0f_runs","M2_f"):(1675.50,K0F,1110,"| **`M1_f`, `M2_f`** | **1 675.50** | **100 530** |"),
 ("T5_runs","X_2d"):(79.2,T5P,1430,"| X_2d | 26.4 | 79.2 | 4752 |"),
 ("T5_runs","T5_CUBE_c"):(136.8,T5P,1431,"| T5_CUBE_c, H_c | 45.6 | 136.8 | 8208 |"),
 ("T5_runs","H_c"):(136.8,T5P,1431,"| T5_CUBE_c, H_c | 45.6 | 136.8 | 8208 |"),
 ("T5_runs","T5_CUBE_m"):(1591.2,T5P,1432,"| T5_CUBE_m, P_m | 530.4 | 1591.2 | 95472 |"),
 ("T5_runs","P_m"):(1591.2,T5P,1432,"| T5_CUBE_m, P_m | 530.4 | 1591.2 | 95472 |"),
 ("T5_runs","L_m"):(1114.2,T5P,1433,"| L_m | 371.4 | 1114.2 | 66852 |"),
 ("T5_runs","S_m"):(1467.0,T5P,1434,"| S_m | 489.0 | 1467.0 | 88020 |"),
 ("T5_runs","T5_CUBE_f"):(6924.6,T5P,1435,"| T5_CUBE_f | 2308.2 | 6924.6 | 415476 |"),
}
# T9aH is DELIBERATELY ABSENT. Its pre-registration registers a cap of 5.00 core-min as
# "3.3x the prediction" on the row directly under "REGISTERED TOTAL PREDICTION <= 90 core-s"
# -- a RUNG TOTAL that does not decompose per case. Splitting it ten ways would be a guess,
# and a guessed cap is worse than a missing one. Reported as an exception, not transcribed.
RUNG_CAP = {"K0f_runs":(1745.40,"segment-1 total"),
            "T9aH_runs":(5.00,"rung total, does not decompose per case")}

# --- budget-instrument class of every rung with NO cap of any kind (the census's A/B/C).
# --- Class C is a stop threshold in NON-CAP VOCABULARY: functionally a cap, invisible to a
# --- cap_core_min sweep. Each carries the document and line the reading came from.
CLASS = {
 "E4_runs":      ("C","docs/campaigns/T-family/E4a_PREREGISTRATION.md",337,"10x stop-and-investigate threshold: 6.35 core-h ... per case, any run exceeding 10x its predicted"),
 "E4a2_runs":    ("C","docs/campaigns/T-family/E4a2_PREREGISTRATION.md",484,"10x stop-and-investigate threshold: 1.8472 core-h ... any run exceeding 10x its predicted wall is stopped"),
 "T10a_runs":    ("C","docs/campaigns/T-family/T10a_PREREGISTRATION.md",375,"prediction by more than 10x is stopped and investigated, not waited out"),
 "T10aR_runs":   ("C","docs/campaigns/T-family/T10aR_PREREGISTRATION.md",346,"The 10x stop-and-investigate threshold is 24.0 core-hours"),
 "T9aH_runs":    ("C","docs/campaigns/T-family/T9aH_PREREGISTRATION.md",543,"REGISTERED CAP | 3.3x the prediction | 300 core-s = 5.00 core-min -- a RUNG TOTAL that does not decompose per case, plus 'an overrun STOPS THE RUN'; costed and stop-bearing, so NOT class A, but not a per-case cap either"),
 "T9a_runs":     ("A","docs/campaigns/T-family/T9a_PREREGISTRATION.md",0,"no cost, no cap, no stop threshold: zero cost-bearing lines"),
 "T1_runs_T1c":  ("A","docs/campaigns/T-family/T1c_RESULTS.md",0,"no cost registration for the T1c arm: zero cost-bearing lines and no pre-registration"),
 "T1_runs_T1b":  ("B","docs/campaigns/T-family/T1b_L4_AMENDMENT.md",0,"costed (12 cost-bearing lines), no stop threshold"),
 "T3_runs":      ("B","docs/campaigns/T-family/T3_PREREGISTRATION.md",0,"costed, no stop threshold"),
 "T10aVF_runs":  ("B","docs/campaigns/T-family/T10aVF_PREREGISTRATION.md",0,"costed, no stop threshold (its '10x' is a tolerance, not a stop)"),
 "T10aR2_runs":  ("B","docs/campaigns/T-family/T10aR2_PREREGISTRATION.md",0,"costed; capped cases carry cap_core_min, these records do not"),
 "K0cG_runs":("B","docs/campaigns/F14-cooling-ladder/K0cG_PREREGISTRATION.md",0,"costed, no stop threshold"),
 "K0cP_runs":("B","docs/campaigns/F14-cooling-ladder/K0cP_PREREGISTRATION.md",0,"costed, no stop threshold"),
 "K0cQ_runs":("B","docs/campaigns/F14-cooling-ladder/K0cQ_PREREGISTRATION.md",0,"costed, no stop threshold"),
 "K0cR_runs":("B","docs/campaigns/F14-cooling-ladder/K0cR_PREREGISTRATION.md",0,"costed, no stop threshold"),
 "K0cS_runs":("B","docs/campaigns/F14-cooling-ladder/K0cS_PREREGISTRATION.md",0,"costed, no stop threshold"),
 "K0cX_runs":("B","docs/campaigns/F14-cooling-ladder/K0cX_PREREGISTRATION.md",0,"costed, no stop threshold"),
 "K0b_D403_rerun":("B","docs/campaigns/F14-cooling-ladder/K0b_D403_RERUN_PREREGISTRATION.md",0,"costed, no stop threshold"),
 "K0b_D406_repair":("B","docs/campaigns/F14-cooling-ladder/K0b_D406_REPAIR_PREREGISTRATION.md",0,"costed, no stop threshold"),
}
T1B_CASES = re.compile(r'^(R_\d+k|P_\d+k|W_\d+k|C_lam)')

# --- ALIASES. The same run is recorded twice on some rungs: once at rung level as
# --- STATUS.<case>, once inside the case directory under the launcher's internal id.
# --- The alias copies carry no cost. Counting them as separate cases would inflate the
# --- denominator and drop the real case into "no budget instrument at all", which is
# --- how they were first mis-classified. They fold onto their parent.
ALIAS = {"T5_C":"T5_CUBE_c","T5_F":"T5_CUBE_f","T5_M":"T5_CUBE_m","T5_H_c":"H_c",
         "T5_L_m":"L_m","T5_P_m":"P_m","T5_S_m":"S_m","T5_X_2d":"X_2d"}
def canonical(case):
    if case.startswith("K0f_EXT_"): return case[len("K0f_EXT_"):]
    return ALIAS.get(case, case)

# --- A cap binds CUMULATIVE spend, so a case's segments (base run + a registered ext)
# --- are SUMMED, never maxed. Within one segment the duplicate records are maxed.
SEG = re.compile(r'\.(ext[0-9]+)$')

def parse(path):
    try: txt = open(path, errors="replace").read()
    except Exception: return {}
    return {m.group(1): m.group(2) for m in TOK.finditer(txt)}

def num(d, *keys):
    for k in keys:
        if k in d:
            try: return float(d[k].rstrip('s'))
            except Exception: pass
    return None

def collect(root=None):
    root = root or ROOT
    regcap = {}
    for tree in TREES:
        for j in glob.glob(os.path.join(root, tree, "*", "*.json")):
            rung = os.path.basename(os.path.dirname(j))
            try: d = json.load(open(j))
            except Exception: continue
            if not isinstance(d, dict): continue
            cs = d.get("cases")
            if not isinstance(cs, dict): continue
            for c, v in cs.items():
                if isinstance(v, dict) and "cap_core_min" in v:
                    try: regcap[(rung, c)] = (float(v["cap_core_min"]), os.path.basename(j))
                    except Exception: pass
    recs = {}; segs = {}
    for tree in TREES:
        for dp, dns, fns in os.walk(os.path.join(root, tree)):
            rel = os.path.relpath(dp, root)
            if SKIP.search(rel): continue
            parts = rel.split(os.sep); rung = None
            for q in parts:
                if q.endswith(("_runs", "_rerun", "_repair", "_sensitivity")): rung = q
            if rung is None: rung = parts[-1]
            for fn in fns:
                if not (fn.startswith("STATUS") or fn.startswith("DONE")): continue
                if SKIP.search(fn): continue
                p = os.path.join(dp, fn)
                d = parse(p)
                case = d.get("case")
                if not case:
                    m = re.match(r'^(?:STATUS[0-9_a-z]*|DONE[0-9_a-z]*)\.(.+?)(?:\.ext[0-9]+)?$', fn)
                    if m: case = m.group(1)
                if not case: continue
                wall = num(d, "wall_s", "wall", "wall_seconds", "clock_seconds", "exec_seconds")
                ranks = num(d, "ranks") or 1.0
                cm = num(d, "core_min")
                if cm is None and wall is not None: cm = wall * ranks / 60.0
                seg = SEG.search(fn)
                seg = seg.group(1) if seg else "base"
                case = canonical(case)
                cand = dict(rung=rung, case=case, cm=cm, ranks=ranks,
                            timeout=num(d, "timeout_s"), cap=num(d, "cap_core_min"),
                            rc=d.get("rc"), capped=d.get("capped"),
                            f=os.path.relpath(p, root))
                sk = (rung, case, seg); cur = segs.get(sk)
                if cur is None: segs[sk] = cand
                else:
                    for fld in ("cap", "timeout"):
                        if cand[fld] is not None and cur[fld] is None: cur[fld] = cand[fld]
                    if cand["cm"] is not None and (cur["cm"] is None or cand["cm"] > cur["cm"]):
                        for fld in ("cap", "timeout"):
                            if cand[fld] is None: cand[fld] = cur[fld]
                        segs[sk] = cand
    for (rung, case, seg), v in segs.items():
        k = (rung, case); r = recs.get(k)
        if r is None:
            recs[k] = dict(v); recs[k]["segments"] = [seg]
        else:
            r["segments"].append(seg)
            if v["cm"] is not None: r["cm"] = (r["cm"] or 0.0) + v["cm"]
            for fld in ("cap", "timeout"):
                if v[fld] is not None and r[fld] is None: r[fld] = v[fld]
    return regcap, recs

def cap_for(k, r, regcap):
    if k in regcap: return regcap[k][0], "registered.json:" + regcap[k][1]
    if k in PROSE_CAP: return PROSE_CAP[k][0], "prose:%s:%d" % (os.path.basename(PROSE_CAP[k][1]), PROSE_CAP[k][2])
    if r["cap"] is not None: return r["cap"], "record cap_core_min"
    return None, None

def audit(regcap, recs, plant=None):
    if plant:
        tgt, factor = plant
        if tgt not in recs or not recs[tgt]["cm"]:
            raise SystemExit("PLANT FAILED TO ARM: %s -- refusing" % (tgt,))
        recs[tgt] = dict(recs[tgt]); recs[tgt]["cm"] *= factor
    breach, capped_n, uncapped = [], 0, []
    for k in sorted(recs):
        r = recs[k]; cap, src = cap_for(k, r, regcap)
        if cap is not None:
            capped_n += 1
            if r["cm"] is not None and r["cm"] > cap:
                breach.append((k, r["cm"], cap, src, r["capped"], r["rc"]))
        else:
            uncapped.append(k)
    return breach, capped_n, uncapped

def klass(rung, case):
    if rung == "T1_runs":
        return CLASS["T1_runs_T1b" if T1B_CASES.match(case) else "T1_runs_T1c"]
    return CLASS.get(rung, ("A", "-", 0, "no registration document located"))

def selftest():
    regcap, recs = collect()
    ok = True
    b0, _, _ = audit(regcap, recs)
    print("  control (no plant)          : %d breaches -- expect 0" % len(b0)); ok &= (len(b0) == 0)
    tgt = ("T16_runs", "T16_MC_m")
    b1, _, _ = audit(regcap, dict(recs), plant=(tgt, 2.0))
    hit = any(x[0] == tgt for x in b1)
    print("  planted x2.0 (446.8 vs 300) : reader %s -- expect FIRED" % ("FIRED" if hit else "BLIND")); ok &= hit
    b2, _, _ = audit(regcap, dict(recs), plant=(tgt, 1.2))
    miss = not any(x[0] == tgt for x in b2)
    print("  planted x1.2 (268.1 vs 300) : reader %s -- expect SILENT" % ("SILENT" if miss else "FIRED")); ok &= miss
    print("SELFTEST %s" % ("PASS" if ok else "FAIL -- the zero is NOT evidence"))
    return 0 if ok else 5

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest: sys.exit(selftest())
    regcap, recs = collect()
    breach, capped_n, uncapped = audit(regcap, recs)
    print("CAP CENSUS -- heat-transfer territory, %d case-records" % len(recs))
    print("  with a registered cap : %d" % capped_n)
    print("  with none             : %d" % len(uncapped))
    print("\nBREACHES (actual core-min > registered cap): %s" % ("NONE" if not breach else ""))
    for b in breach:
        print("  %s/%s actual %.3f > cap %.3f [%s]" % (b[0][0], b[0][1], b[1], b[2], b[3]))
    from collections import Counter
    cc = Counter(klass(r, c)[0] for (r, c) in uncapped)
    print("\nBUDGET-INSTRUMENT CLASS of the %d uncapped:" % len(uncapped))
    print("  A  no budget instrument at all        : %d" % cc["A"])
    print("  B  costed, no stop threshold          : %d" % cc["B"])
    print("  C  costed + stop threshold, non-cap   : %d" % cc["C"])
    byrung = {}
    for (r, c) in uncapped: byrung.setdefault((klass(r, c)[0], r), []).append(c)
    for (cl, r) in sorted(byrung): print("    %s  %-18s %3d" % (cl, r, len(byrung[(cl, r)])))
    print("\nRUNG-LEVEL CAPS (not per case):")
    for r, (v, note) in RUNG_CAP.items(): print("  %-12s %8.2f core-min  (%s)" % (r, v, note))
    fr = []
    for k in sorted(recs):
        cap, _ = cap_for(k, recs[k], regcap)
        if cap and recs[k]["cm"]: fr.append((recs[k]["cm"] / cap, k, recs[k]["cm"], cap))
    print("\nCLOSEST APPROACHES:")
    for f in sorted(fr, reverse=True)[:8]:
        print("  %.3fx %s/%s  %.3f of %.3f" % (f[0], f[1][0], f[1][1], f[2], f[3]))

if __name__ == "__main__":
    main()
