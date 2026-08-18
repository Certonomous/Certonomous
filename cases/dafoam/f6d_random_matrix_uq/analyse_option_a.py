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

#: Snapshots whose field data on disk was written by a process OTHER than the
#: run that owns the case, established per-snapshot in
#: campaign/F6D_COLLISION_INDEPENDENCE_CHECK.md §2.
#:
#: THE NOTE LIVES IN THE GENERATOR, NOT IN THE JSON. Hand-patching a derived
#: output leaves the generator free to erase the patch on its next run, which is
#: the failure mode this lab has already paid for once. Everything the JSON says
#: about contamination is emitted from here.
#:
#: THE POINT IS LABELLED, NOT DROPPED. It is real data with a known writer. A
#: labelled point can be used, excluded, or argued with; a missing one is a hole
#: no downstream reader can interpret, and deleting it would destroy the record
#: of what happened. Consumers that require single-writer provenance should
#: filter on this key -- they cannot do that against a silent deletion.
CONTAMINATED_SNAPSHOTS = {
    ('d0.2_s000', 7500): {
        'writer': 'duplicate solver (PID 204435), not this run',
        'mechanism':
            "a second simpleFoam was launched on this case at 02:54:51 while the "
            "run's own solver was mid-flight. `startFrom latestTime` made the "
            "duplicate restart from the survivor's own 7000/ snapshot, so it was "
            "a FORK, not a repeat: it competed for the same snapshot filenames. "
            "It reached Time 7500 and completely overwrote the 7500/ directory "
            "the survivor had written 22 s earlier.",
        'evidence':
            "(a) stored gradient in 7500/uniform/momentumSourceProperties is "
            "0.00759741462064012, the duplicate's logged value, not the "
            "survivor's 0.0084247934089418; (b) 7500/ directory mtime 02:55:05.02 "
            "is OLDER than every file inside it (02:55:27.88) -- the signature of "
            "a complete in-place overwrite, and the only time directory in this "
            "case where that holds; (c) the duplicate's own function-object "
            "directory postProcessing/wallShearStress/7000/ records exactly one "
            "write event, at Time 7500; (d) the survivor's own wallShearStress.dat "
            "disagrees with the field on disk at 7500 and at no other time.",
        'survivor_value_recoverable': False,
        'survivor_value_note':
            "The survivor's own reattachment at 7500 is GONE, not merely "
            "unlabelled: its fields were overwritten in place and no copy exists "
            "anywhere in the archive. It cannot be reconstructed. It is only "
            "bounded by its neighbours (6.358 at 7000, 5.940 at 8000) and by the "
            "survivor's own recorded wall-shear extrema at 7500, which lie on a "
            "smooth trend.",
        'also_contaminated':
            "postProcessing/singleGraph_x0..x8/7500/ -- all nine profile files "
            "carry the same overwrite signature (dirs 02:55:05, files 02:55:27). "
            "Any profile comparison at t=7500 is against the duplicate's flow.",
        'affects_pre_registered_metrics': False,
        'what_does_not_move':
            "NOTHING REPORTED MOVES, and this is measured rather than asserted. "
            "t=7500 lies outside every pre-registered metric window: the primary "
            "value at the 13500 cut reads 12000-13500, the primary value at "
            "completion reads 14500-16000, delta is primary minus the published "
            "4000 baseline (md5-identical to the untouched ens/ tree), and "
            "settledness reads the last 500 iterations. The gate number "
            "reproduces exactly at -0.8313 at the 13500 cut, delta at completion "
            "is -0.4906, and both breach the 0.25 threshold -- so THE VOID IS "
            "UNAFFECTED and the completion value stands. Recomputing settledness "
            "from the survivor's log segment alone gives 0.3392 against the "
            "shipped 0.3401, a 0.27 % change. This snapshot enters exactly one "
            "pre-registered thing: metric 1 is 'reattachment at EACH written "
            "snapshot', so the published trajectory below is not purely "
            "single-writer at this one point.",
    },
}


def contamination_for(case, traj):
    """The contamination block emitted onto *case*'s row, or None.

    Emitted per row so it travels with the data a consumer actually reads --
    a caveat in a separate document reaches nobody.
    """
    hits = {t: v for (c, t), v in CONTAMINATED_SNAPSHOTS.items() if c == case}
    if not hits:
        return None
    return {
        'contaminated_times': sorted(hits),
        'contaminated_points': [[t, r] for (t, r) in traj if t in hits],
        'traj_is_single_writer': False,
        'guidance':
            "Points listed in contaminated_times were written by another "
            "process. Do not consume this trajectory as single-writer output "
            "without filtering them; do not silently drop them either -- say "
            "which points were removed.",
        'detail': {str(t): hits[t] for t in sorted(hits)},
    }

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
        pairs = [(t, r) for (t, r, _) in traj]
        row = dict(case=case, kind='control' if case in CONTROLS else 'member',
                   n_snapshots=len(traj), last_time=tmax, settledness=s,
                   published_4000=pub, primary=primary, delta=delta,
                   traj=pairs)
        contam = contamination_for(case, pairs)
        if contam is not None:
            row['contamination'] = contam
        rows.append(row)
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
    # The contamination has to be visible to whoever RUNS this, not only to
    # whoever reads the JSON, because the person re-deriving the product is the
    # one most likely to consume the trajectory next.
    print("\n--- SNAPSHOT PROVENANCE (not all of this trajectory is this run's) ---")
    flagged = [r for r in rows if 'contamination' in r]
    if not flagged:
        print("  every snapshot in every trajectory was written by its own run")
    for r in flagged:
        c = r['contamination']
        seen = {t for (t, _) in r['traj']}
        missing = [t for t in c['contaminated_times'] if t not in seen]
        for t, val in c['contaminated_points']:
            print(f"  {r['case']:12s} t={t:<6d} reattachment={val:.6f}  "
                  f"WRITTEN BY {c['detail'][str(t)]['writer']}")
        print(f"  {'':12s} -> enters no pre-registered metric window; the "
              f"reported primary, delta and settledness are unaffected, and the "
              f"VOID stands.")
        print(f"  {'':12s} -> the survivor's own value at these times is "
              f"OVERWRITTEN AND UNRECOVERABLE, not merely unlabelled.")
        if missing:
            # The register names a time this trajectory does not contain: the
            # register has drifted from the data, and a stale provenance note is
            # worse than none. Say so loudly rather than emitting it silently.
            print(f"  {'':12s} !! REGISTER DRIFT: contaminated time(s) {missing} "
                  f"are not in this trajectory -- re-check "
                  f"CONTAMINATED_SNAPSHOTS against the archive.")

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
