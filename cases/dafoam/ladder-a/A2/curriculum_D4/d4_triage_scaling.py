"""D4 arm-F CRASH TRIAGE (diagnostic only -- writes NO graded number).
Measures pyOptSparse History.getValues() scale-flag polarity against the
registered DV scalers, using the PINNED variable patchV[0] as the control:
runScript sets lower=upper=U0=100.0, so its physical value CANNOT be anything
other than 100.0.  Whatever the history returns for it names the convention."""
import json
from pyoptsparse import History
h = History("/mnt/O/OptView.hst", flag="r")
out = {}
for flag in (False, True):
    v = h.getValues(major=True, scale=flag)
    rec = {}
    for k in v:
        if k.split(".")[-1] in ("shape", "twist", "patchV"):
            import numpy as np
            a = np.atleast_2d(np.array(v[k], dtype=float))[-1, :].ravel()
            rec[k] = {"n": int(a.size), "max_abs": float(abs(a).max()),
                      "first3": [float(x) for x in a[:3]]}
    out["scale=%s" % flag] = rec
try:
    info = h.getDVInfo()
    out["dvinfo"] = {k: {kk: (vv if isinstance(vv, (int, float, str, bool, type(None))) else str(vv))
                         for kk, vv in d.items() if kk in ("scale", "lower", "upper", "value", "name")}
                     for k, d in info.items()}
except Exception as e:
    out["dvinfo_error"] = repr(e)[:300]
print("D4_TRIAGE_SCALING " + json.dumps(out, sort_keys=True, default=str))
