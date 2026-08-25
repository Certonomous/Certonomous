#!/usr/bin/env python
"""Curriculum D7 -- extract the optimiser's FINAL design point and the FULL
per-major history from the pyOptSparse history FILE (`OptView.hst`).

NEVER from stdout.  MPI log splicing on this ladder is MEASURED
(A2/per_component_table/RESULTS.md sec.2.2, commit 79679a84): four ranks
interleave on one stdout and sever arrays mid-number.  `OptView.hst` is written
by rank 0 through pyOptSparse's own History object and is immune to that.

Writes `d7_endpoint_dvs.json` and `d7_major_history.json`.  REFUSES (exit 2)
rather than degrading -- CLAUDE.md rule 4.  Derived from the proven
`A2/curriculum_D4/d4_extract_endpoint.py` with D7's key names and D7's
registered DV sizes asserted.
"""
import json
import os
import sys

HST = "OptView.hst"
OUT = "d7_endpoint_dvs.json"
HISTOUT = "d7_major_history.json"
KEYS = ("twist", "shape", "patchV")
# PREREGISTRATION.md sec.1 -- registered DV sizes, asserted not assumed.
SIZES = {"twist": 5, "shape": 120, "patchV": 2}


def refuse(msg):
    sys.stderr.write("D7_EXTRACT REFUSE %s\n" % msg)
    sys.exit(2)


def main():
    if not os.path.isfile(HST):
        refuse("history file %s absent" % HST)
    if os.path.getsize(HST) == 0:
        refuse("history file %s is empty" % HST)
    from pyoptsparse import History
    import numpy as np
    h = History(HST, flag="r")
    values = h.getValues(major=True, scale=False)
    keys = sorted(values.keys())
    have = {}
    for k in KEYS:
        cand = [c for c in keys if c == k or c.endswith("." + k)]
        if not cand:
            refuse("design variable %r absent from history; keys=%s" % (k, keys))
        have[k] = cand[0]
    n_major = int(np.atleast_2d(np.array(values[have["shape"]])).shape[0])
    if n_major < 1:
        refuse("history carries %d major iterations" % n_major)

    out = {"_source": os.path.abspath(HST), "_n_major_rows": n_major,
           "_history_keys": keys}
    for k in KEYS:
        arr = np.atleast_2d(np.array(values[have[k]], dtype=float))
        vals = [float(v) for v in arr[-1, :].ravel()]
        # SIZE ASSERTION.  A DV vector of the wrong length would silently move
        # every named component in PREREGISTRATION.md sec.6 onto a different
        # physical quantity while keeping its label.
        if len(vals) != SIZES[k]:
            refuse("endpoint %s has %d components, registered %d"
                   % (k, len(vals), SIZES[k]))
        out[k] = vals
    for name in keys:
        short = name.split(".")[-1]
        if short in ("CD", "CL"):
            a = np.atleast_2d(np.array(values[name], dtype=float))
            out["_final_" + short] = float(a[-1, :].ravel()[0])

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

    for path, obj in ((HISTOUT, hist), (OUT, out)):
        with open(path, "w") as fh:
            json.dump(obj, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
    sys.stdout.write("D7_ENDPOINT_DVS_WRITTEN %s n_major_rows=%d n_shape=%d "
                     "n_twist=%d n_patchV=%d history=%s\n"
                     % (OUT, n_major, len(out["shape"]), len(out["twist"]),
                        len(out["patchV"]), HISTOUT))


if __name__ == "__main__":
    main()
