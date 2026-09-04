#!/usr/bin/env python3
"""Ahmed 25 c3 draw-scatter, leg 1.

Pre-registration: campaign/R4_AHMED_TURN_DRAW_SCATTER_PREREGISTRATION.md,
commit e543bc5e, committed before any new mesh existed. Two replicate draws at
c3 (c3b, c3c); c4/c4b already exist. Leg 1 CANNOT declare SIGNAL (prereg §2);
it scores the Ground-2 increment-movement test (§3).
"""
from __future__ import annotations
import json, math, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/home/ubuntu/Certonomous"); sys.path.insert(0, str(REPO/"sdk"))
from workflows import tmr_verification as tv
from chief_engineer import lever_echo, mesh_certificate

# THE SOLVE-EVIDENCE GUARD.  Loaded BY EXPLICIT PATH rather than by putting
# `scripts/` on sys.path: this module must not be shadowable, and a guard that
# can be silently replaced is not a guard.  If it is missing this file refuses
# to run at all -- deleting without the guard IS the defect.  Pattern copied
# from verification/runs/GEN_ALT_runs/run_gen_alt.py:39-61 exactly, including
# the single-registration branch, which is load-bearing and not tidiness:
# loading the same file twice under two module objects gives
# SolveEvidencePresent two DISTINCT classes, and a caller's `except
# SolveEvidencePresent` then silently misses the refusal raised by the other
# copy -- the guard looks wired and is not.
#
# RUNS below is an ABSOLUTE LITERAL and never consults tmr_verification's
# _RUN_ROOT, so NO environment variable can redirect this file -- including
# inside a control that believes it has redirected it.  Anything testing this
# driver must rebind the module globals and refuse if the rebinding did not
# take; scripts/check_restage_guard_wiring.py does exactly that (control R4 B0).
import importlib.util as _ilu  # noqa: E402

_GUARD_PATH = REPO/"scripts"/"solve_evidence_guard.py"
if not _GUARD_PATH.is_file():
    raise RuntimeError(
        f"solve-evidence guard not found at {_GUARD_PATH}; refusing to run. "
        "This driver deletes its run directories under the shared run root, "
        "and without the guard those deletes are unconditional -- see the "
        "guard's docstring for the rung that paid for it.")
if "solve_evidence_guard" in sys.modules:
    solve_evidence_guard = sys.modules["solve_evidence_guard"]
else:
    _spec = _ilu.spec_from_file_location("solve_evidence_guard", _GUARD_PATH)
    solve_evidence_guard = _ilu.module_from_spec(_spec)
    sys.modules["solve_evidence_guard"] = solve_evidence_guard
    _spec.loader.exec_module(solve_evidence_guard)
safe_rmtree_for_restage = solve_evidence_guard.safe_rmtree_for_restage
refuse_if_solve_evidence = solve_evidence_guard.refuse_if_solve_evidence
SolveEvidencePresent = solve_evidence_guard.SolveEvidencePresent


def safe_restage(target) -> bool:
    """Delete `target` for a RE-STAGE, refusing if it -- or any directory ONE
    LEVEL INSIDE it -- holds solve evidence.  Returns True if anything was
    removed, False if there was nothing there.  There is no override.

    WHY THE EXTRA LEVEL, measured rather than assumed.  The guard scans its
    target for time directories > 0, `processor*/` time directories and
    `postProcessing/**/*.dat` with data rows.  It does NOT recurse into an
    arbitrary child.  A sibling driver in this same class,
    `F5c_runs/run_stage_a.py`, deletes `<root>/f5c-stageA-A1` while every field
    it holds lives one level down in `.../case/`, so the bare guard answered
    "no solve evidence found; safe to re-stage" for a directory carrying a
    completed 2,000-iteration solve.  Measured 2026-09-04 with
    `solve_evidence_guard.py --check`.  A guard that answers "safe" there is a
    decoration, so both drivers in this class check one level down as well.

    R4's own targets carry their physics at the top level -- `r4-ahmed-c3b`
    holds `203/` with six fields, the same time under processor0..3, and 203
    coefficient rows -- so the nested check is defence in depth here rather
    than the load-bearing part.  It is present so that a layout change cannot
    silently reopen the hole.
    """
    target = Path(target)
    if not target.exists():
        return False
    refuse_if_solve_evidence(target, action="restage")
    for child in sorted(p for p in target.iterdir() if p.is_dir()):
        refuse_if_solve_evidence(child, action="restage (nested one level)")
    return safe_rmtree_for_restage(target)


HERE = REPO/"demo-output/website/campaign/R4_runs"
RUNS = Path("/home/ubuntu/certonomous-runs")
TEMPLATE = HERE/"c3"
LOG = HERE/"c3_replicates_driver.log"
C3_CELLS, TOL, RANKS = 254911, 0.02, 4
C3_CD, C4_CD, C4B_CD = 0.073992743, 0.074882228, 0.074979080
PUBLISHED_INC = C4_CD - C3_CD
DRAWS = {"c3b": [(99,21,58),(100,21,57),(96,21,61)],
         "c3c": [(97,21,60),(96,21,61),(100,21,57)]}

def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")
def log(m):
    line=f"[{now()}] {m}"; print(line, flush=True)
    with LOG.open("a") as h: h.write(line+"\n")

def stage(name, div):
    r = RUNS/f"r4-ahmed-{name}"
    # WAS: shutil.rmtree(r, ignore_errors=True) -- unconditional, silent about
    # its own failures, and the FIRST statement of the staging function, so
    # "re-draw this replicate" was the same keystroke as "destroy whatever is
    # at that name" under the shared run root.  RE-STAGE site: refusal is FATAL
    # and deliberately not caught, because continuing here would copytree into
    # a directory that still exists.
    #
    # The L-42 reuse check in main() is NOT a substitute and this is why: it
    # skips re-staging only when BOTH `log.simpleFoam` and
    # `postProcessing/forceCoeffs1` are present.  A case whose solver log is
    # gone but whose fields are not -- exactly the `re2000` shape this guard
    # was written for -- falls straight through that check and reaches this
    # line.  Measured on disk 2026-09-04: `r4-ahmed-c3b` holds `203/` with
    # U k nut omega p phi, the same time under processor0..3, and a
    # coefficient series of 203 data rows ending at t = 203.
    safe_restage(r)

    def _ignore(_dir, names):
        # Time directories are PURELY numeric ("0", "220"); `0.orig` is not, and
        # must survive -- an earlier `[0-9]*` glob here matched it and deleted
        # the pristine fields. Named rather than globbed for that reason.
        out = set()
        for n in names:
            if n.isdigit() or n.startswith("processor") or n.startswith("log.") \
               or n in ("postProcessing", "polyMesh", "extendedFeatureEdgeMesh"):
                out.add(n)
        return out

    shutil.copytree(TEMPLATE, r, ignore=_ignore)
    # RAISE, not `assert`: `python3 -O` deletes assert statements outright, and
    # this file's two asserts were the only thing standing between a silently
    # mis-staged case and a solve.  F7's `make_dambreak.py` carried exactly
    # this defect and built a case at a resolution nobody asked for under -O.
    if not (r/"0.orig").is_dir():
        raise RuntimeError(f"{name}: 0.orig did not survive staging")
    b = r/"system"/"blockMeshDict"; t = b.read_text()
    import re
    t2,n = re.subn(r"\(\d+ \d+ \d+\) simpleGrading", f"({div[0]} {div[1]} {div[2]}) simpleGrading", t, 1)
    if n != 1:
        raise RuntimeError(f"{name}: no hex triple (substituted {n} times)")
    b.write_text(t2, newline="\n"); return r

def mesh(r, name):
    t0=time.monotonic()
    for a,l in ((["surfaceFeatureExtract"],"log.surfaceFeatureExtract"),
                (["blockMesh"],"log.blockMesh"),
                (["snappyHexMesh","-overwrite"],"log.snappyHexMesh"),
                (["checkMesh"],"log.checkMesh")):
        rc=tv._foam(a,r,l,timeout=2400)
        if rc.returncode!=0: raise RuntimeError(f"{name}: {a[0]} rc={rc.returncode}")
    cert=mesh_certificate.write_certificate(r/"constant",
        check_log_text=(r/"log.checkMesh").read_text(errors="replace"),
        generator=f"snappyHexMesh, Ahmed 25 c3 replicate {name}")
    if cert is None: raise RuntimeError(f"{name}: no certificate")
    log(f"{name}: meshed {cert['cells']} cells in {time.monotonic()-t0:.1f}s, {cert['verdict']}")
    return cert

def solve(r, name):
    ok,why = mesh_certificate.certificate_admits(r/"constant")
    log(f"{name}: G2 -> {ok} ({why})")
    if not ok: raise RuntimeError(f"{name}: mesh refused: {why}")
    # WAS: shutil.rmtree(r/"0", ignore_errors=True).  GENUINELY-NOT-EVIDENCE
    # RESET: `0/` is t = 0 and t = 0 is not evidence, so this must keep
    # deleting or the solve path is broken for every replicate.  It is routed
    # through the guard anyway for the two things `ignore_errors=True` took
    # away: a MIS-AIMED target (a wrong `r`, a layout change, `0` standing for
    # a case directory rather than a time directory) now REFUSES instead of
    # being erased, and a FAILED DELETE is now heard instead of swallowed.
    # `ignore_errors=True` is part of the defect and is not reproduced.
    safe_restage(r/"0"); shutil.copytree(r/"0.orig", r/"0")
    t0=time.monotonic()
    for a,l in ((["potentialFoam","-writephi"],"log.potentialFoam"),
                (["decomposePar","-force"],"log.decomposePar")):
        rc=tv._foam(a,r,l,timeout=1800)
        if rc.returncode!=0: raise RuntimeError(f"{name}: {a[0]} rc={rc.returncode}")
    rc=tv._foam(["mpirun","-np",str(RANKS),"simpleFoam","-parallel"],r,"log.simpleFoam",timeout=7200)
    wall=time.monotonic()-t0
    tv._foam(["reconstructPar","-latestTime"],r,"log.reconstructPar",timeout=1800)
    txt=(r/"log.simpleFoam").read_text(errors="replace")
    conv = "SIMPLE solution converged" in txt
    iters = txt.count("\nTime = ")
    ct=None
    import re
    for m in re.finditer(r"ClockTime = (\d+) s", txt): ct=float(m.group(1))
    log(f"{name}: {iters} iters, residualControl={'MET' if conv else 'NOT MET'}, "
        f"ClockTime {ct}s = {(ct or 0)*RANKS/60:.2f} core-min")
    return {"iterations":iters,"residual_control_met":conv,"clock_s":ct,
            "core_min":round((ct or 0)*RANKS/60,3),"wall_s":round(wall,1),
            "levers_verified_active":lever_echo.levers_verified_active(txt)}

def cd_of(r):
    dats=sorted((r/"postProcessing"/"forceCoeffs1").glob("*/coefficient*.dat"))
    hdr,rows=[],[]
    for p in dats:
        for line in p.read_text(errors="replace").splitlines():
            if line.startswith("#"):
                if "Time" in line and "Cd" in line: hdr=line.lstrip("#").split()
                continue
            q=line.split()
            if len(q)>1: rows.append([float(v) for v in q])
    i=hdr.index("Cd"); v=[x[i] for x in rows if len(x)>i]
    w=v[-max(1,int(round(len(v)*0.2))):]
    return sum(w)/len(w), len(v)

def main():
    log("Ahmed c3 draw-scatter leg 1 starting (prereg e543bc5e)")
    res={}
    for name,cands in DRAWS.items():
        att=[]
        for div in cands[:3]:
            done = RUNS/f"r4-ahmed-{name}"
            if (done/"log.simpleFoam").exists() and \
               (done/"postProcessing"/"forceCoeffs1").exists():
                # L-42: a rerun in place destroys the evidence its record needs.
                log(f"{name}: completed solve already on disk; not re-staging")
                c = mesh_certificate.read_certificate(done/"constant")
                cd,n = cd_of(done)
                res[name]={"draw_attempts":att,"certificate":c,"cd":cd,"rows":n,
                           "case":str(done),"reused":True,"core_min":0.0}
                log(f"{name}: Cd = {cd:.9f} (reused)"); break
            r=stage(name,div); c=mesh(r,name); cells=c["cells"]
            ok=abs((cells-C3_CELLS)/C3_CELLS)<=TOL
            att.append({"divisions":list(div),"cells":cells,
                        "deviation":(cells-C3_CELLS)/C3_CELLS,"admitted":ok,
                        "certificate_verdict":c["verdict"]})
            log(f"{name}: attempt {len(att)} {div} -> {cells} "
                f"({(cells-C3_CELLS)/C3_CELLS:+.2%}) {'ADMITTED' if ok else 'RE-DRAW'}")
            if ok:
                s=solve(r,name); cd,n=cd_of(r)
                res[name]={"draw_attempts":att,"certificate":c,"cd":cd,"rows":n,
                           "case":str(r),**s}
                log(f"{name}: Cd = {cd:.9f}"); break
        else:
            raise RuntimeError(f"{name}: re-draw allowance exhausted")
    c3s=[C3_CD]+[res[k]["cd"] for k in DRAWS]
    m3=sum(c3s)/len(c3s)
    s3=math.sqrt(sum((x-m3)**2 for x in c3s)/(len(c3s)-1))
    c4m=(C4_CD+C4B_CD)/2
    new_inc=c4m-m3
    ratio=new_inc/PUBLISHED_INC
    if ratio>=0.75 and new_inc>0: branch,reading="SURVIVES",("the Ahmed turn is not an artifact "
        "of a single draw; the B-52's failure mode is ABSENT here and the two bodies genuinely differ")
    elif ratio<0.50 or new_inc<=0: branch,reading="DISSOLVES",("the Ahmed turn joins the B-52's fate "
        "and the cross-family claim loses its last leg")
    else: branch,reading="PARTIAL","between 50% and 75% of the published increment; no branch claimed"
    out={"prereg":"campaign/R4_AHMED_TURN_DRAW_SCATTER_PREREGISTRATION.md",
         "prereg_commit":"e543bc5e","timestamp":now(),"leg":"1 of 2 (leg 2 NOT taken)",
         "c3_draws":{"original":C3_CD,**{k:res[k]["cd"] for k in DRAWS}},
         "c3_mean":m3,"s_c3":s3,"n_c3":len(c3s),
         "c4_mean_over_existing_pair":c4m,"s_c4_from_pair":abs(C4_CD-C4B_CD)/1.1284,
         "published_increment":PUBLISHED_INC,"reestimated_increment":new_inc,
         "ratio_to_published":ratio,"branch":branch,"reading":reading,
         "NOT_A_SIGNAL_VERDICT":("Leg 1 cannot declare SIGNAL (prereg section 2): at n_c3=3, "
            "n_c4=2 the 90% CI on T reaches only 2.26 against a 3.0 threshold. No T verdict "
            "is claimed here."),
         "runs":res,"cost_core_min":round(sum(res[k]["core_min"] for k in DRAWS),3)}
    (HERE/"c3_replicates_record.json").write_text(json.dumps(out,indent=2,sort_keys=True,default=str)+"\n")
    log(f"{branch}: published {PUBLISHED_INC:.4e} -> re-estimated {new_inc:.4e} "
        f"({ratio:.3f}x), s_c3={s3:.3e}")
    return 0

if __name__=="__main__": raise SystemExit(main())
