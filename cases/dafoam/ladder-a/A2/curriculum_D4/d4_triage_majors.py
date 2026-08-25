"""D4 arm-F triage part 2 (diagnostic): what ARE the 125 rows that
d4_extract_endpoint.py calls majors?  Reads isMajor and iter from the history."""
import json, numpy as np
from pyoptsparse import History
h = History("/mnt/O/OptView.hst", flag="r")
v = h.getValues(major=True, scale=False)
vall = h.getValues(major=False, scale=False)
def col(d, k):
    return np.atleast_2d(np.array(d[k])).ravel()
out = {}
out["n_rows_major_True"] = int(np.atleast_2d(np.array(v['dvs.shape'])).shape[0])
out["n_rows_major_False"] = int(np.atleast_2d(np.array(vall['dvs.shape'])).shape[0])
for k in ("isMajor", "iter", "fail"):
    if k in v:
        a = col(v, k)
        out["major_True_"+k] = {"n": int(a.size), "unique": sorted(set(float(x) for x in a))[:12],
                                "n_unique": len(set(float(x) for x in a)),
                                "min": float(a.min()), "max": float(a.max())}
    if k in vall:
        a = col(vall, k)
        out["major_False_"+k] = {"n": int(a.size), "n_unique": len(set(float(x) for x in a)),
                                 "min": float(a.min()), "max": float(a.max()),
                                 "n_true": int(sum(1 for x in a if x))}
cl = col(v, 'scenario1.aero_post.functionals.CL')
it = col(v, 'iter') if 'iter' in v else None
out["CL_rows_exceeding_5e-4"] = int(sum(1 for c in cl if abs(c-0.5) > 5e-4))
if it is not None:
    # last CL per unique iter value
    last = {}
    for i, c in zip(it, cl):
        last[float(i)] = float(c)
    out["n_unique_iter"] = len(last)
    out["exceed_5e-4_over_last_per_iter"] = int(sum(1 for c in last.values() if abs(c-0.5) > 5e-4))
    out["max_absCLm05_last_per_iter"] = max(abs(c-0.5) for c in last.values())
    out["iter_of_worst"] = max(last, key=lambda k: abs(last[k]-0.5))
out["max_absCLm05_all_rows"] = max(abs(c-0.5) for c in cl)
print("D4_TRIAGE_MAJORS " + json.dumps(out, sort_keys=True, default=str))
