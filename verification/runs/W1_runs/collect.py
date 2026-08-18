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
# y+ is taken from the LATEST state, chosen by the Time written inside the file
# rather than by the directory name or by glob order. Three traps, all of them
# real and all of them hit on this ladder before this was written:
#   1. postProcessing directories are named for the run's START time, so
#      yPlus1/0/yPlus.dat holds the state at the END of the first run. Sorting
#      directory names does not sort states.
#   2. the previous loop globbed UNSORTED and kept the last parse, so filesystem
#      order decided which state was reported. That is how the medium rung came
#      to publish the y+ of iteration 5,000 beside a Cd from iteration 16,000.
#   3. OpenFOAM renames a function object's output to <name>_<time>.dat when the
#      file already exists on restart, exactly as it does for coefficient.dat
#      (stitch.py handles that case for the forces). yPlus1/10000/ on the medium
#      rung holds a header-only yPlus.dat beside the real yPlus_10000.dat.
def _latest_yplus(case_dir):
    best = None
    pattern = str(case_dir/'postProcessing'/'yPlus1'/'*'/'yPlus*.dat')
    for path in glob.glob(pattern):
        text = open(path).read()
        parsed = t.parse_yplus_dat(text, patch='bump')
        if not parsed:
            continue
        times = [float(ln.split()[0]) for ln in text.splitlines()
                 if ln.strip() and not ln.startswith('#')]
        if not times:
            continue
        stamp = max(times)
        if best is None or stamp > best[0]:
            best = (stamp, parsed, Path(path).relative_to(case_dir).as_posix())
    return best

yp_hit = _latest_yplus(case)
yp = yp_hit[1] if yp_hit else None
yp_time = yp_hit[0] if yp_hit else None
yp_source = yp_hit[2] if yp_hit else None
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
    # so a reader can check the y+ is the state the Cd beside it came from
    'yplus_time': yp_time, 'yplus_source': yp_source,
    'yplus_is_settled_state': (yp_time is not None and len(series) - yp_time < 1.0),
    'logs': [p.name for p in logs],
}
print(json.dumps(rec, indent=1))
Path(case/'collected.json').write_text(json.dumps(rec, indent=2))
