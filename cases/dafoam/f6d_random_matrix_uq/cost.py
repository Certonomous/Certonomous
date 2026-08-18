"""F6d -- measured compute cost.  Reads each run's own final ExecutionTime
line; nothing estimated."""
import re, json, glob, os
from pathlib import Path
HERE = Path(__file__).resolve().parent
groups = {"signcheck (sign verification, 4 runs)": "signcheck/*/log.simpleFoam",
          "null test": "ens/null/log.simpleFoam",
          "prescribed corners": "ens/corner_*/log.simpleFoam",
          "live-model corners + sign demo": "signdemo/*/log.simpleFoam",
          "random matrix delta=0.2": "ens/d0.2_s*/log.simpleFoam",
          "random matrix delta=0.6": "ens/d0.6_s*/log.simpleFoam",
          "F6a hump corner recheck": "f6a_recheck/*/log.simpleFoam"}
out, total = {}, 0.0
for name, pat in groups.items():
    ts = []
    for f in sorted(HERE.glob(pat)):
        m = re.findall(r"ExecutionTime = ([0-9.]+) s", Path(f).read_text(errors="ignore"))
        if m:
            ts.append(float(m[-1]))
    if ts:
        out[name] = {"n_runs": len(ts), "core_seconds_total": round(sum(ts), 1),
                     "core_minutes_total": round(sum(ts) / 60.0, 2),
                     "core_seconds_per_run_median": round(sorted(ts)[len(ts)//2], 1)}
        total += sum(ts)
out["TOTAL_core_minutes"] = round(total / 60.0, 2)
out["note"] = ("All runs serial (1 core each), OpenFOAM v2606 simpleFoam. "
               "ExecutionTime is the solver's own reported CPU time, read from "
               "the last such line in each log.")
print(json.dumps(out, indent=2))
(HERE / "cost.json").write_text(json.dumps(out, indent=2))
