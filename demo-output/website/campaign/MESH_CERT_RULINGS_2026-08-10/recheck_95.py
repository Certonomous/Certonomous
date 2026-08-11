#!/usr/bin/env python3
"""Fresh checkMesh against all 95 retrospectively-minted certificates.

Chief-approved 2026-08-10 (~7 core-min). The 6 carrying the log-older-than-points
ordering flag were run FIRST and showed no drift; this covers the remaining 89
and re-records the 6 for completeness.

Handles both layouts: a normal case (<case>/constant/birth_certificate.json with
a sibling system/) and a bare mesh-cache entry (polyMesh with no case around it),
which gets a minimal throwaway case built for it -- checkMesh needs controlDict,
fvSchemes and fvSolution or it FATAL-errors and produces no cell count.
"""
from __future__ import annotations
import json, os, shutil, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, '/home/ubuntu/Certonomous/sdk')
from chief_engineer.mesh_certificate import parse_check_log, points_sha256

RUNS=Path('/home/ubuntu/certonomous-runs')
OUT=Path('/home/ubuntu/Certonomous/demo-output/website/campaign/MESH_CERT_RULINGS_2026-08-10')
TMP=Path('/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad/recheck95')
TMP.mkdir(parents=True, exist_ok=True)
HDR='FoamFile { version 2.0; format ascii; class dictionary; object %s; }\n'
CD=HDR%'controlDict'+"application checkMesh; startFrom startTime; startTime 0; stopAt endTime;\nendTime 1; deltaT 1; writeControl timeStep; writeInterval 1;\n"
FS=HDR%'fvSchemes'+"ddtSchemes{default steadyState;} gradSchemes{default Gauss linear;}\ndivSchemes{default none;} laplacianSchemes{default Gauss linear corrected;}\ninterpolationSchemes{default linear;} snGradSchemes{default corrected;}\n"
FV=HDR%'fvSolution'+"solvers{} relaxationFactors{}\n"

def case_for(cert_path: Path, i: int):
    root=cert_path.parent                      # dir holding polyMesh
    if root.name=='constant' and (root.parent/'system'/'controlDict').exists():
        return root.parent, None
    tmp=TMP/f'case_{i}'
    shutil.rmtree(tmp, ignore_errors=True)
    (tmp/'system').mkdir(parents=True); (tmp/'constant').mkdir()
    os.symlink(root/'polyMesh', tmp/'constant'/'polyMesh')
    (tmp/'system'/'controlDict').write_text(CD)
    (tmp/'system'/'fvSchemes').write_text(FS)
    (tmp/'system'/'fvSolution').write_text(FV)
    return tmp, tmp

def main():
    # DOCKET B2, 2026-08-11. This loop used to `continue` past a certificate it
    # could not read, and the record below then published an agreement rate
    # over a population one smaller than the one on disk, with nothing anywhere
    # saying so. Injected: two certificates, one truncated mid-JSON -> the
    # record read total 1, agree 1, and named the skipped file nowhere. A
    # CERTIFICATE THAT COULD NOT BE READ IS NOT A CERTIFICATE THAT AGREES; it
    # is the same third verdict the checkMesh_did_not_run bucket below already
    # gives the inner loop, which is why the fix is that bucket's twin rather
    # than a new idea. The committed recheck_95_record.json PREDATES this fix
    # and states no unreadable count: the population was re-counted by hand on
    # 2026-08-11 at 127 birth certificates, 0 unparseable, 95 retrospective, so
    # the blind spot did not bite that run -- but the run could not have said
    # so itself, which is the whole finding.
    certs=[]; unreadable=[]; found=0
    for p in RUNS.rglob('birth_certificate.json'):
        found+=1
        try: d=json.loads(p.read_text())
        except Exception as e:
            unreadable.append({'path':str(p),'error':f'{type(e).__name__}: {e}',
                               'note':'NOT counted as agreeing, and not in the '
                                      'denominator of any figure below'})
            continue
        if d.get('provenance')=='retrospective-from-archived-log': certs.append((p,d))
    certs.sort(key=lambda x: str(x[0]))
    unreadable.sort(key=lambda r: r['path'])
    print(f"birth certificates found: {found} | unreadable: {len(unreadable)} | "
          f"retrospective: {len(certs)}", flush=True)
    for row in unreadable:
        print(f"  UNREADABLE {row['path']}: {row['error']}", flush=True)
    rows=[]; t0=time.monotonic()
    for i,(p,cert) in enumerate(certs):
        case,tmp=case_for(p,i)
        try:
            r=subprocess.run(['openfoam2606','checkMesh'],cwd=case,capture_output=True,text=True,timeout=1800)
            log=r.stdout+r.stderr
        except Exception as e:
            log=f"HARNESS FAILURE: {e}"
        (TMP/f'{i:03d}.log').write_text(log)
        fresh=parse_check_log(log)
        # A checkMesh that did not run states no cell count. parse_check_log
        # returns verdict 'clean' on such a log, so cells is the real guard --
        # the same guard write_certificate relies on. Never call that agreement.
        ran = fresh.get('cells') is not None
        agree = ran and cert['verdict']==fresh.get('verdict') and cert['cells']==fresh.get('cells')
        rows.append({'mesh':str(p.parent),'cert_verdict':cert['verdict'],'cert_cells':cert['cells'],
                     'fresh_verdict':fresh.get('verdict') if ran else None,
                     'fresh_cells':fresh.get('cells'),
                     'checkMesh_ran':ran,'agree':agree,
                     'hash_matches':points_sha256(p.parent/'polyMesh')==cert['points_sha256'],
                     'log':f'{i:03d}.log'})
        if tmp: shutil.rmtree(tmp, ignore_errors=True)
        if (i+1)%10==0: print(f"  {i+1}/{len(certs)}  {time.monotonic()-t0:.0f}s", flush=True)
    ok=[r for r in rows if r['agree']]
    dr=[r for r in rows if r['checkMesh_ran'] and not r['agree']]
    nr=[r for r in rows if not r['checkMesh_ran']]
    bad=[r for r in rows if not r['hash_matches']]
    summary={'total':len(rows),'agree':len(ok),'drift':len(dr),'checkMesh_did_not_run':len(nr),
             'points_hash_mismatch':len(bad),'wall_s':round(time.monotonic()-t0,1),
             'core_min':round((time.monotonic()-t0)/60,2),
             # The denominator, stated. `total` is what was CHECKED; it is not
             # what was found, and the difference has a name and a list.
             'certificates_found':found,
             'certificates_unreadable':len(unreadable),
             'unreadable_rows':unreadable,
             'frame':(f"{found} birth_certificate.json under {RUNS} by rglob; "
                      f"{len(unreadable)} could not be parsed and are excluded "
                      f"from every figure here; {len(certs)} of the remainder "
                      f"carry provenance retrospective-from-archived-log and "
                      f"are the denominator of agree/drift/hash-mismatch. "
                      f"AN UNREADABLE CERTIFICATE IS NOT AN AGREEING ONE."),
             'drift_rows':dr,'did_not_run_rows':nr,'hash_mismatch_rows':bad,'rows':rows}
    (OUT/'recheck_95_record.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(f"\nAGREE {len(ok)} | DRIFT {len(dr)} | checkMesh-did-not-run {len(nr)} | "
          f"hash-mismatch {len(bad)} | UNREADABLE {len(unreadable)} | "
          f"{summary['core_min']} core-min", flush=True)
    # A run that could not read a certificate has not verified 100% of
    # anything, and says so in its own exit status rather than only in a field
    # a reader has to go looking for.
    return 0 if not unreadable else 2

if __name__=='__main__': raise SystemExit(main())
