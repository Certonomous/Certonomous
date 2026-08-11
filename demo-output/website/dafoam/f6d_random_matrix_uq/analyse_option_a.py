"""F6d Option A -- analysis, exactly as pre-registered in
campaign/F6D_OPTION_A_PREREGISTRATION.md (commit 08822fb2).

Metrics (pre-registered, not chosen after seeing data):
  reattachment  -- unmodified analyse.analyse_case, at every written snapshot
  settledness   -- peak-to-peak swing of the meanVelocityForce pressure gradient
                   over the final 500 iterations, normalised by median |pg| over
                   the second half of the CONTINUATION
  primary value -- mean reattachment over the final 2000 iterations of snapshots
  delta         -- primary value minus the published value at 4000

Thresholds, pre-registered: settled < 0.10; moved |delta| >= 1.0;
held |delta| < 0.5; 0.5-1.0 declared ambiguous in advance.
Validity gate: any control moving > 0.25 x/h => experiment VOID.
"""
import os
import re
import sys
import json
import glob
import statistics

F6D = '/home/ubuntu/Certonomous/demo-output/website/dafoam/f6d_random_matrix_uq'
ROOT = os.path.join(F6D, 'f6d_option_a')
sys.path.insert(0, F6D)
import analyse  # noqa: E402

MEMBERS = ['d0.2_s015', 'd0.2_s019', 'd0.2_s020', 'd0.2_s022', 'd0.2_s023',
           'd0.2_s036', 'd0.6_s000', 'd0.6_s007', 'd0.6_s011', 'd0.6_s021',
           'd0.6_s022', 'd0.6_s035', 'd0.6_s039']
CONTROLS = ['null', 'd0.2_s000', 'd0.2_s027']
RE_PG = re.compile(r'pressure gradient = ([0-9.eE+-]+)')

published = {}
_ag = json.load(open(os.path.join(F6D, 'aggregate_result.json')))
for k in ('d0.2', 'd0.6'):
    for m in _ag['random_matrix'][k]['members']:
        published[m['case']] = m['reattachment']
published['null'] = _ag['null_test']['all_admitted']['reattachment']['mean']


def settledness(case):
    log = os.path.join(ROOT, case, 'log.simpleFoam')
    if not os.path.isfile(log):
        return None
    pg = [float(m.group(1)) for line in open(log, errors='replace')
          for m in [RE_PG.search(line)] if m]
    if len(pg) < 600:
        return None
    scale = statistics.median(abs(x) for x in pg[len(pg) // 2:])
    last = pg[-500:]
    return (max(last) - min(last)) / scale if scale > 0 else None


def times_of(case):
    out = []
    for d in glob.glob(os.path.join(ROOT, case, '[0-9]*')):
        b = os.path.basename(d)
        if os.path.isdir(d) and re.fullmatch(r'\d+', b):
            out.append(int(b))
    return sorted(out)


def analyse_case(case):
    ts = [t for t in times_of(case) if t >= 4000]
    traj = []
    for t in ts:
        if not os.path.exists(os.path.join(ROOT, case, str(t), 'wallShearStress')):
            continue
        r = analyse.analyse_case(os.path.join(ROOT, case), t)
        traj.append((t, r.get('reattachment_x_over_h'), r.get('n_reversed_regions')))
    return traj


def main():
    rows = []
    for case in MEMBERS + CONTROLS:
        traj = analyse_case(case)
        s = settledness(case)
        tmax = traj[-1][0] if traj else None
        window = [r for (t, r, _) in traj if tmax and t > tmax - 2000 and r is not None]
        primary = statistics.mean(window) if window else None
        pub = published.get(case)
        delta = (primary - pub) if (primary is not None and pub is not None) else None
        rows.append(dict(case=case, kind='control' if case in CONTROLS else 'member',
                         n_snapshots=len(traj), last_time=tmax, settledness=s,
                         published_4000=pub, primary=primary, delta=delta,
                         traj=[(t, r) for (t, r, _) in traj]))
    json.dump(rows, open(os.path.join(F6D, 'option_a_result.json'), 'w'), indent=1)

    print(f"{'case':12s} {'kind':8s} {'snaps':>5s} {'lastT':>6s} {'settled':>8s} "
          f"{'pub4000':>8s} {'primary':>8s} {'delta':>7s}")
    for r in rows:
        f = lambda v, w, p: (f"{v:{w}.{p}f}" if v is not None else '-'.rjust(w))
        print(f"{r['case']:12s} {r['kind']:8s} {r['n_snapshots']:5d} "
              f"{str(r['last_time']):>6s} {f(r['settledness'],8,3)} "
              f"{f(r['published_4000'],8,3)} {f(r['primary'],8,3)} {f(r['delta'],7,3)}")

    # A control that has not actually CONTINUED yields delta == 0 trivially --
    # published value against itself. Reporting that as "holds" would be a pass
    # from an instrument that cannot see, which is the exact failure mode this
    # whole audit is about. A control counts only once it has run past 4000.
    print("\n--- VALIDITY GATE (pre-registered: any control moving > 0.25 x/h => VOID) ---")
    ran, notrun = [], []
    for r in rows:
        if r['kind'] != 'control':
            continue
        continued = (r['last_time'] or 0) > 4000 and r['n_snapshots'] >= 3
        (ran if continued else notrun).append(r)
    for r in ran:
        print(f"  {r['case']:12s} lastT={r['last_time']:>6} delta={r['delta']:+.3f}  "
              f"{'OK' if abs(r['delta']) <= 0.25 else 'BREACH'}")
    for r in notrun:
        print(f"  {r['case']:12s} lastT={str(r['last_time']):>6} "
              f"NOT YET CONTINUED -- carries no information, not a pass")
    if any(abs(r['delta']) > 0.25 for r in ran):
        print("  => EXPERIMENT VOID")
    elif len(ran) == len(CONTROLS):
        print("  => all 3 controls continued and held: experiment valid")
    else:
        print(f"  => VERDICT WITHHELD: only {len(ran)} of {len(CONTROLS)} controls "
              f"have continued; the gate cannot pass until all 3 have.")

    print("\n--- MEMBER CLASSIFICATION (pre-registered thresholds) ---")
    done = [r for r in rows if r['kind'] == 'member'
            and (r['last_time'] or 0) > 4000 and r['delta'] is not None]
    for r in done:
        d = r['delta']
        cls = 'MOVED' if abs(d) >= 1.0 else ('HELD' if abs(d) < 0.5 else 'AMBIGUOUS')
        direction = 'toward baseline' if d > 0 else 'away from baseline'
        st = ('settled' if (r['settledness'] is not None and r['settledness'] < 0.10)
              else 'NOT settled')
        print(f"  {r['case']:12s} delta={d:+.3f} {cls:9s} {direction:17s} {st}")
    print(f"  ({len(done)} of {len(MEMBERS)} members continued so far; "
          f"no verdict until all have finished)")


if __name__ == '__main__':
    main()
