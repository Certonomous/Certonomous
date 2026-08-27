#!/usr/bin/env python
"""Curriculum D6 -- extract the optimiser's FINAL design point and the per-major
history from the pyOptSparse history FILE (`OptView.hst`), never from stdout.

DERIVED FROM curriculum_D4/d4_extract_endpoint.py (md5 ee7d3c99fd716da23779cb651961918e)
with the REGISTERED DELTAS of D6: the design-variable keys are twist, shape and
the three per-point patchV_cl04 / patchV_cl05 / patchV_cl06 (D4's extractor
matches `patchV` by exact name or `.patchV` suffix and REFUSES D6's history);
the per-major history carries the composite objective J and CL/CD for each of
the three points.  Writes `d6r_endpoint_dvs.json` and `d6r_major_history.json`.
Refuses (exit 2) if the history is absent, has no major iterations, or does not
carry every key.

MPI log splicing on this exact case is MEASURED (A2 per_component_table 2.2,
commit 79679a84).  `OptView.hst` is written by rank 0 through pyOptSparse's own
History object and is immune to the stdout interleave.
"""
import json
import os
import sys

HST = "OptView.hst"
OUT = "d6r_endpoint_dvs.json"
HIST_OUT = "d6r_major_history.json"
KEYS = ("twist", "shape", "patchV_cl04", "patchV_cl05", "patchV_cl06")
POINTS = ("cl04", "cl05", "cl06")


def refuse(msg):
    sys.stderr.write("D6R_EXTRACT REFUSE %s\n" % msg)
    sys.exit(2)


def main():
    if not os.path.isfile(HST):
        refuse("history file %s absent" % HST)
    from pyoptsparse import History
    h = History(HST, flag="r")
    values = h.getValues(major=True, scale=False)
    keys = sorted(values.keys())
    have = {}
    for k in KEYS:
        cand = [c for c in keys if c == k or c.endswith("." + k)]
        if not cand:
            refuse("design variable %r absent from history; keys=%s" % (k, keys))
        have[k] = cand[0]
    import numpy as np
    n_major = int(np.atleast_2d(np.array(values[have["shape"]])).shape[0])
    if n_major < 1:
        refuse("history carries %d major iterations" % n_major)
    out = {"_source": os.path.abspath(HST), "_n_major_rows": n_major,
           "_history_keys": keys}
    for k in KEYS:
        arr = np.atleast_2d(np.array(values[have[k]], dtype=float))
        out[k] = [float(v) for v in arr[-1, :].ravel()]
    hist = {"_source": os.path.abspath(HST), "_n_major_rows": n_major}
    # the composite objective
    jk = [c for c in keys if c == "obj.J" or c.endswith(".J") or c == "J"]
    if not jk:
        refuse("objective J absent from history; keys=%s" % keys)
    a = np.atleast_2d(np.array(values[jk[0]], dtype=float))
    hist["J"] = [float(v) for v in a[:, 0].ravel()]
    hist["_key_J"] = jk[0]
    out["_final_J"] = hist["J"][-1]
    # per-point CL and CD
    for pt in POINTS:
        for q in ("CL", "CD"):
            ck = [c for c in keys if c.startswith(pt + ".") and c.endswith("." + q)]
            if not ck:
                refuse("per-major %s for %s absent from history; keys=%s" % (q, pt, keys))
            a = np.atleast_2d(np.array(values[ck[0]], dtype=float))
            hist["%s_%s" % (q, pt)] = [float(v) for v in a[:, 0].ravel()]
            hist["_key_%s_%s" % (q, pt)] = ck[0]
            out["_final_%s_%s" % (q, pt)] = hist["%s_%s" % (q, pt)][-1]
            if len(hist["%s_%s" % (q, pt)]) != n_major:
                refuse("per-major %s_%s len %d != n_major %d"
                       % (q, pt, len(hist["%s_%s" % (q, pt)]), n_major))
    if len(hist["J"]) != n_major:
        refuse("per-major J len %d != n_major %d" % (len(hist["J"]), n_major))
    with open(HIST_OUT, "w") as fh:
        json.dump(hist, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    sys.stdout.write("D6R_ENDPOINT_DVS_WRITTEN %s n_major_rows=%d n_shape=%d history=%s\n"
                     % (OUT, n_major, len(out["shape"]), HIST_OUT))


if __name__ == "__main__":
    main()
