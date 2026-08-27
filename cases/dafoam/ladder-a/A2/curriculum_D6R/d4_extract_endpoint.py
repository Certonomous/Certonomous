#!/usr/bin/env python
"""Curriculum D4 -- extract the optimiser's FINAL design point from the
pyOptSparse history FILE (`OptView.hst`), never from stdout.

MPI log splicing on this exact case is MEASURED (A2 per_component_table §2.2,
commit 79679a84).  `OptView.hst` is written by rank 0 through pyOptSparse's own
History object and is immune to the stdout interleave that corrupts the printed
derivative blocks.

Writes `d4_endpoint_dvs.json`.  Refuses (exit 2) if the history is absent, has
no major iterations, or does not carry all three design-variable keys.
"""
import json
import os
import sys

HST = "OptView.hst"
OUT = "d4_endpoint_dvs.json"
KEYS = ("twist", "shape", "patchV")


def refuse(msg):
    sys.stderr.write("D4_EXTRACT REFUSE %s\n" % msg)
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
    # objective / constraint at the same row, for cross-checking the grader
    for name in keys:
        if name.endswith("CD") or name.endswith("CL"):
            a = np.atleast_2d(np.array(values[name], dtype=float))
            out["_final_" + name.split(".")[-1]] = float(a[-1, :].ravel()[0])
    # ---- the FULL per-major history, for the CL-feasibility gate ----------
    hist = {"_source": os.path.abspath(HST), "_n_major_rows": n_major}
    for name in keys:
        short = name.split(".")[-1]
        if short in ("CD", "CL"):
            a = np.atleast_2d(np.array(values[name], dtype=float))
            hist[short] = [float(v) for v in a[:, 0].ravel()]
            hist["_key_" + short] = name
    for req in ("CD", "CL"):
        if req not in hist:
            refuse("per-major %s absent from history; keys=%s" % (req, keys))
    if len(hist["CD"]) != n_major or len(hist["CL"]) != n_major:
        refuse("per-major arrays len CD=%d CL=%d != n_major=%d"
               % (len(hist["CD"]), len(hist["CL"]), n_major))
    with open("d4_major_history.json", "w") as fh:
        json.dump(hist, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())

    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    sys.stdout.write("D4_ENDPOINT_DVS_WRITTEN %s n_major_rows=%d n_shape=%d "
                     "history=d4_major_history.json\n"
                     % (OUT, n_major, len(out["shape"])))


if __name__ == "__main__":
    main()
