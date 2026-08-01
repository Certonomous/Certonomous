"""Settle-driven solve of one NASA-grid bump rung.

Reuses tmr_verification's settle criterion verbatim: settle_verdict drives
request_solver_stop; a rung that reaches its controlDict endTime unsettled is
recorded backstop-stopped, never converged. Usage:
    python3 run_rung.py <case> [--ranks N] [--extend ITERS]
--extend continues an unsettled run from latestTime by ITERS more iterations
(records the continuation; values are only ever quoted at settled states).
"""
import sys, json, subprocess, time, re
from pathlib import Path
sys.path.insert(0, '/home/ubuntu/Certonomous/sdk')
import workflows.tmr_verification as t
from stitch import stitched
def series_of(case):
    try: return stitched(case)[1]
    except Exception: return []

case = Path(sys.argv[1]).resolve()
ranks = 1
extend = 0
for i, a in enumerate(sys.argv):
    if a == '--ranks': ranks = int(sys.argv[i+1])
    if a == '--extend': extend = int(sys.argv[i+1])

ctrl = case / 'system' / 'controlDict'
text = ctrl.read_text()
if extend:
    cur_end = int(re.search(r'^endTime\s+(\d+);', text, re.M).group(1))
    new_end = cur_end + extend
    text = re.sub(r'^endTime\s+\d+;', f'endTime         {new_end};', text, count=1, flags=re.M)
    text = re.sub(r'^startFrom\s+\S+;', 'startFrom       latestTime;', text, count=1, flags=re.M)
    text = re.sub(r'^stopAt\s+\S+;', 'stopAt          endTime;', text, count=1, flags=re.M)
    ctrl.write_text(text)
    log_name = f'log.simpleFoam.extend{new_end}'
else:
    log_name = 'log.simpleFoam'

def foam(args, log, timeout=36000):
    with open(case/log, 'w') as fh:
        return subprocess.run(['openfoam2606', *args], cwd=case, stdout=fh,
                              stderr=subprocess.STDOUT, timeout=timeout).returncode

t0 = time.time()
if ranks > 1:
    (case/'system'/'decomposeParDict').write_text(
        'FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }\n'
        f'numberOfSubdomains {ranks};\nmethod scotch;\n')
    rc = foam(['decomposePar', '-force'] + (['-latestTime'] if extend else []), 'log.decomposePar')
    assert rc == 0, 'decomposePar failed'
    solver = subprocess.Popen(
        ['openfoam2606', 'mpirun', '-np', str(ranks), 'simpleFoam', '-parallel'],
        cwd=case, stdout=open(case/log_name, 'w'), stderr=subprocess.STDOUT)
else:
    solver = subprocess.Popen(['openfoam2606', 'simpleFoam'],
        cwd=case, stdout=open(case/log_name, 'w'), stderr=subprocess.STDOUT)

verdict = None
while solver.poll() is None:
    series = series_of(case)
    if series:
        verdict = t.settle_verdict(series)
        if verdict['settled']:
            if t.request_solver_stop(case):
                print(f"[{case.name}] settled at iteration {verdict['iterations']}: {verdict['reason']}; stop requested", flush=True)
            verdict['stop_requested'] = True
            break
    time.sleep(10.0)
solver.wait(timeout=1200)
wall = time.time() - t0
if ranks > 1:
    foam(['reconstructPar', '-latestTime'], 'log.reconstructPar')
series = series_of(case)
final = t.settle_verdict(series) if series else None
record = {
    'case': case.name, 'ranks': ranks, 'wall_seconds': round(wall, 1),
    'core_minutes': round(wall * ranks / 60.0, 2),
    'exit_code': solver.returncode, 'iterations': len(series),
    'cd_last': series[-1] if series else None,
    'settle': final, 'extended_to': extend and new_end or None,
}
out = case / ('record_extend.json' if extend else 'record.json')
if extend and (case/'record.json').exists():
    prev = json.loads((case/'record.json').read_text())
    record['previous'] = prev
    record['core_minutes_cumulative'] = record['core_minutes'] + prev.get('core_minutes_cumulative', prev['core_minutes'])
else:
    record['core_minutes_cumulative'] = record['core_minutes']
out.write_text(json.dumps(record, indent=2))
print(json.dumps(record, indent=2), flush=True)
