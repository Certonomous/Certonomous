"""Stitch a rung's Cd history across restarts by ITERATION NUMBER (deduped),
reading every coefficient*.dat under forceCoeffs1. Returns settle verdict."""
import sys, glob, json
from pathlib import Path
sys.path.insert(0, '/home/ubuntu/Certonomous/sdk')
import workflows.tmr_verification as t

def stitched(case):
    rows = {}
    for f in glob.glob(str(Path(case)/'postProcessing'/'forceCoeffs1'/'*'/'coefficient*.dat')):
        for line in open(f):
            if line.startswith('#'): continue
            parts = line.split()
            if len(parts) < 2: continue
            try: it = int(parts[0]); cd = float(parts[1])
            except ValueError: continue
            rows[it] = cd  # later files overwrite; identical where they overlap
    its = sorted(rows)
    assert its == list(range(its[0], its[-1]+1)), 'gap in stitched iterations'
    return its, [rows[i] for i in its]

if __name__ == '__main__':
    case = sys.argv[1]
    its, series = stitched(case)
    v = t.settle_verdict(series)
    print(json.dumps({'case': case, 'first_it': its[0], 'last_it': its[-1],
                      'cd_last': series[-1], 'settle': v}, indent=1))
