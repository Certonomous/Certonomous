"""Collect one settled rung's numbers, every one citing a file on disk."""
import sys, json, glob
from pathlib import Path
sys.path.insert(0, '/home/ubuntu/Certonomous/sdk')
import workflows.tmr_verification as t
from stitch import stitched

case = Path(sys.argv[1]).resolve()
series = stitched(case)[1]
verdict = t.settle_verdict(series)
logs = sorted(case.glob('log.simpleFoam*'), key=lambda p: (len(p.name), p.name))
last_log = logs[-1]
split = t.parse_force_split(last_log.read_text(errors='replace'))
yp = None
for f in glob.glob(str(case/'postProcessing'/'yPlus1'/'*'/'yPlus.dat')):
    yp = t.parse_yplus_dat(open(f).read(), patch='bump') or yp
cf075 = None
for f in sorted(glob.glob(str(case/'postProcessing'/'wallCf'/'*'/'*.raw'))):
    prof = t.parse_wall_shear_raw(open(f).read())
    if prof:
        cf075 = t.cf_at(prof, t.BUMP_CF_STATION)
rec = {
    'case': case.name, 'iterations': len(series),
    'cd': series[-1], 'settle': verdict,
    'cd_split_last_log_block': split,
    'yplus_bump': yp, 'cf_at_0p75': cf075,
    'logs': [p.name for p in logs],
}
print(json.dumps(rec, indent=1))
Path(case/'collected.json').write_text(json.dumps(rec, indent=2))
