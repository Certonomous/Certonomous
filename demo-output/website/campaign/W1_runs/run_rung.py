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
from chief_engineer import lever_echo
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

def _echo(fh, args):
    """Write the LEVER-ECHO block, if this argument vector actually runs a
    solver, for the directory the process will run in.

    `case` is the same object passed to `cwd=` below, so the echoed directory
    and the executing directory cannot disagree -- that is the whole of L-45,
    and it is a property of the code rather than a promise. The shared
    predicate (`lever_echo.echo_if_solver`) decides what counts as a solve, so
    a utility launch and a `-postProcess` invocation correctly get nothing.
    """
    block = lever_echo.echo_if_solver(args, case)
    if block:
        fh.write(block)
        fh.flush()


def foam(args, log, timeout=36000):
    with open(case/log, 'w') as fh:
        _echo(fh, args)
        return subprocess.run(['openfoam2606', *args], cwd=case, stdout=fh,
                              stderr=subprocess.STDOUT, timeout=timeout).returncode


def _solver_stdout(args):
    """The solver log, opened and echoed into before the child is spawned."""
    fh = open(case/log_name, 'w')
    _echo(fh, args)
    return fh

t0 = time.time()
if ranks > 1:
    (case/'system'/'decomposeParDict').write_text(
        'FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }\n'
        f'numberOfSubdomains {ranks};\nmethod scotch;\n')
    rc = foam(['decomposePar', '-force'] + (['-latestTime'] if extend else []), 'log.decomposePar')
    assert rc == 0, 'decomposePar failed'
    solve_args = ['openfoam2606', 'mpirun', '-np', str(ranks), 'simpleFoam', '-parallel']
    solver = subprocess.Popen(solve_args, cwd=case,
        stdout=_solver_stdout(solve_args), stderr=subprocess.STDOUT)
else:
    solve_args = ['openfoam2606', 'simpleFoam']
    solver = subprocess.Popen(solve_args, cwd=case,
        stdout=_solver_stdout(solve_args), stderr=subprocess.STDOUT)

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
# Chain the cumulative cost through the PREVIOUS EXTENSION when there is one,
# not through the first run. Reading record.json here made every extension
# report "first run + me" and silently drop every extension in between: the
# medium bump rung ran four times for 1892.8 s of solver time (31.55 core-min)
# and its record claimed 17.88, because extend12000 and extend15000 were never
# in any total. A rung that is restarted twice is exactly the rung whose cost
# nobody is watching, so this is the one place the arithmetic must not skip.
prev_path = case/'record_extend.json'
if not (extend and prev_path.exists()):
    prev_path = case/'record.json'
if extend and prev_path.exists():
    prev = json.loads(prev_path.read_text())
    record['previous'] = prev
    record['previous_record'] = prev_path.name
    record['core_minutes_cumulative'] = record['core_minutes'] + prev.get('core_minutes_cumulative', prev['core_minutes'])
else:
    record['core_minutes_cumulative'] = record['core_minutes']
# The driver's wall clock is not the solver's clock. Record both, so a rung
# whose cumulative was dropped, or which shared the box, is visible without
# re-reading the logs.
try:
    import re as _re
    solver_s = 0.0
    for _log in sorted(case.glob('log.simpleFoam*')):
        _m = _re.findall(r'ExecutionTime = ([0-9.]+) s', _log.read_text(errors='replace'))
        if _m:
            solver_s += float(_m[-1])
    record['solver_execution_core_minutes_all_logs'] = round(solver_s * ranks / 60.0, 2)
except OSError:
    record['solver_execution_core_minutes_all_logs'] = None
out.write_text(json.dumps(record, indent=2))
print(json.dumps(record, indent=2), flush=True)
