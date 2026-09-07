#!/usr/bin/env python
"""Curriculum D6RF7 -- extract the optimiser's FINAL design point and the
per-major COMPOSITE OBJECTIVE from the pyOptSparse history FILE (`OptView.hst`),
never from stdout.  IT READS DESIGN VARIABLES AND `J` ONLY.

DERIVED FROM `curriculum_D6R/d6r_extract_endpoint.py`
(md5 `1743dd4232a7f06785f71be2f285f08d`, verified on disk before this file was
written) with ONE registered delta, which is the dafoam-supervisor's ruling on
`PREREGISTRATION.md` section 9 -- POSITION 1:

  * THE PER-POINT `CL`/`CD` BLOCK (`d6r_extract_endpoint.py:65-77`) IS DROPPED.
    It is the block that refuses when the history carries no `CD`, and
    `D6RF3-DEF-4` measured, by COMPLETE ENUMERATION of the registered source
    (`OptView.hst`, md5 `70fafa07bdee618fef13039433c01114`, 1,013 rows /
    1,007 iteration records / 863 rows carrying `funcs`), that **no `CD` appears
    in any structure of any record**.  A file that cannot contain the quantity
    is not a source for it.
  * THE GROUND FOR DROPPING IT RATHER THAN REPAIRING IT, MEASURED not assumed:
    `_final_CD_*` and `_final_CL_*` -- the only things the dropped block put
    into `d6r_endpoint_dvs.json` -- ARE READ BY NOTHING.  Zero references across
    every in-container instrument of this lineage.  The per-major `CD_<pt>`
    series was read by `d6rf2_grade.py:760` and `:792`; `PREREGISTRATION.md`
    section 2a re-points both to the FD baseline primal, so this file's output
    is not the grader's `CD` source and never was a viable one.
  * The DESIGN-VECTOR path (`:53-55`, `arr[-1,:]` over the five DV keys at
    `:25`) IS UNCHANGED, byte-for-byte in behaviour: it is exactly what the FD
    endpoint needs and `CD` played no part in constructing it.
  * `J` IS KEPT.  `R-RED` (REPORTED, NOT GATED) reads it, and section 3c
    requires that row to disclose non-finiteness rather than print a number
    derived from a `NaN`.
  * Product names are this item's own (`d6rf7_*`), not `D6R`'s.  A product
    registered under one name and written under another is `D6RF3-DEF-6`,
    measured in `D6RF2` and named in `PREREGISTRATION.md` section 1f.

WHAT THIS FILE DOES NOT CLAIM.  `arr[-1, :]` is the LAST row of the history.
`D6RF3-DEF-5` measured that row: index 1006, every `funcs` entry `NaN`, and 687
of the 863 `funcs` rows non-finite.  The design vector at that row is measured
to differ from the last FINITE major (index 998) by at most 4.46e-08
driver-scaled -- **that is a measurement about the DESIGN VECTOR and it repairs
nothing about `J`.**  `_final_J` is therefore expected to be non-finite on this
history, and the grader's section 3f finiteness clause is what handles it.
This file DOES NOT filter, drop or repair non-finite rows: an extractor that
silently chose a different row than the one it says it chooses would be a worse
defect than the one it fixed.

Refuses (exit 2) if the history is absent, has no major iterations, or does not
carry every design-variable key or the objective.

MPI log splicing on this exact case is MEASURED (A2 per_component_table 2.2,
commit 79679a84).  `OptView.hst` is written by rank 0 through pyOptSparse's own
History object and is immune to the stdout interleave.
"""
import json
import os
import sys

HST = "OptView.hst"
OUT = "d6rf7_endpoint_dvs.json"
HIST_OUT = "d6rf7_major_history.json"
KEYS = ("twist", "shape", "patchV_cl04", "patchV_cl05", "patchV_cl06")


def refuse(msg):
    sys.stderr.write("D6RF7_EXTRACT REFUSE %s\n" % msg)
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
    if len(hist["J"]) != n_major:
        refuse("per-major J len %d != n_major %d" % (len(hist["J"]), n_major))
    # THE DROPPED BLOCK, DISCLOSED ON THE ARTEFACT'S OWN FACE rather than left
    # to be inferred from an absence.  A successor reading this file must not
    # mistake "no CD key" for "CD was not looked for".
    dropped = ("d6r_extract_endpoint.py:65-77 (per-point CL/CD) IS DROPPED in "
               "this successor. D6RF3-DEF-4: complete enumeration of the "
               "registered OptView.hst found NO CD in any structure of any of "
               "1,007 records. CD_i(mp) for this item comes from "
               "PREREGISTRATION.md section 2a -- the FD baseline primal, "
               "d6rf7_fd_endpoint.json points.<pt>.CD -- and NOT from here.")
    out["_cd_block_dropped"] = dropped
    hist["_cd_block_dropped"] = dropped
    out["_extractor"] = "d6rf7_extract_endpoint.py"
    hist["_extractor"] = "d6rf7_extract_endpoint.py"
    with open(HIST_OUT, "w") as fh:
        json.dump(hist, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    sys.stdout.write("D6RF7_ENDPOINT_DVS_WRITTEN %s n_major_rows=%d n_shape=%d "
                     "history=%s\n"
                     % (OUT, n_major, len(out["shape"]), HIST_OUT))


if __name__ == "__main__":
    main()
