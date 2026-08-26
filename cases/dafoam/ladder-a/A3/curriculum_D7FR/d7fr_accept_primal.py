#!/usr/bin/env python
"""Curriculum D7F -- THE ACCEPTANCE PRIMAL.  LIMIT 1 of the D7-DEF-4 ruling.

ONE primal at the CORRECTED design point.  Its `CD` is compared against arm O's
IPOPT objective `2.3048932443550496e-02` by `d7fr_accept_compare.py`, on a band
registered BEFORE this ran.

WHY IT EXISTS AND WHAT IT IS ALLOWED TO DECIDE.  The D7-DEF-4 diagnosis is
internally consistent -- a pinned variable reading back at exactly its scaler,
components outside their own bounds, and `scale=True`/`scale=False`
returning identical values in the container.  INTERNAL CONSISTENCY IS NOT
ENOUGH.  The supervisor made the reproduction a PRECONDITION of the freeze:

  * it reproduces inside the registered band  -> the diagnosis is proved by an
    instrument that grades nothing, the repair is frozen, arms F-S and F-P run;
  * it does not reproduce                     -> THE DIAGNOSIS IS WRONG, the
    repair is WITHDRAWN, the FD arms stay BLOCKED and a second finding is recorded.
    The band is NOT widened and the correction is NOT adjusted until it fits.
    That is exactly what 2d.1 forbids: nothing a verdict depends on may be
    repaired on the authority of the verdict it produces.

DESIGN RULES, all of them inherited from the FROZEN `d7_fd_endpoint.py` because
the point is to run the SAME model, not a lookalike:
  * The model definition is NOT COPIED.  This file reads `d7_opt_runScript.py`,
    asserts its md5, splits it at the literal anchor `# OpenMDAO setup`, and
    execs the header.  The daOptions, the Top class, the DVs and the constraints
    are the producer's own bytes.
  * EVERY graded number is written to a FILE by rank 0 with fsync and is never
    recovered from stdout.  MPI log splicing on this exact case is MEASURED
    (A2 per_component_table/RESULTS.md 2.2, commit 79679a84).
  * The design point is read from `d7_endpoint_dvs_PHYSICAL.json` and this file
    REFUSES unless that artifact declares `_units == "PHYSICAL"`.  Applying a
    driver-scaled vector as physical is the defect under test; an instrument
    built to test it must not be able to commit it.

WHAT THIS FILE DOES NOT DO.  It computes NO gradient, NO finite difference and
NO FD table.  It is not arm F and it does not cross the bright line.  It answers
exactly one question: at the corrected design point, what is CD.
"""
import hashlib
import json
import os
import sys
import time

PRODUCER = "d7_opt_runScript.py"
PRODUCER_MD5 = "e43902ed2cfc99022c6e21e075f88695"
ANCHOR = "# OpenMDAO setup"
DVS = "d7_endpoint_dvs_PHYSICAL.json"
OUT = "d7fr_accept_primal.json"


def refuse(msg):
    sys.stderr.write("D7FR_ACCEPT REFUSE %s\n" % msg)
    sys.exit(2)


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def main():
    if os.path.exists(OUT):
        refuse("%s already exists -- an answer file present BEFORE the run that "
               "must produce it is the exact shape of a false result" % OUT)

    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        refuse("producer md5 %s != frozen %s" % (got, PRODUCER_MD5))

    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        refuse("anchor %r appears %d times" % (ANCHOR, src.count(ANCHOR)))
    header = src.split(ANCHOR)[0]

    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "d4_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    Top = ns["Top"]

    if not os.path.isfile(DVS):
        refuse("%s absent -- run d4_endpoint_physical.py first" % DVS)
    with open(DVS) as fh:
        dvs = json.load(fh)
    if dvs.get("_units") != "PHYSICAL":
        refuse("%s declares _units=%r; this instrument refuses anything that is "
               "not PHYSICAL" % (DVS, dvs.get("_units")))
    for key in ("twist", "shape", "patchV"):
        if key not in dvs:
            refuse("%s missing design variable %s" % (DVS, key))

    prob = om.Problem()
    prob.model = Top()
    prob.setup(mode="rev")
    for key in ("twist", "shape", "patchV"):
        prob.set_val(key, np.array(dvs[key], dtype=float))

    CD = "scenario1.aero_post.CD"
    CL = "scenario1.aero_post.CL"

    t0 = time.time()
    prob.run_model()
    wall = time.time() - t0
    cd = float(prob.get_val(CD)[0])
    cl = float(prob.get_val(CL)[0])

    if rank == 0:
        out = {
            "kind": "d7fr_acceptance_primal",
            "CD": cd, "CD_repr": repr(cd),
            "CL": cl, "CL_repr": repr(cl),
            "wall_s": round(wall, 3),
            "ranks": int(MPI.COMM_WORLD.size),
            "producer_md5": got,
            "dv_source": os.path.abspath(DVS),
            "dv_source_md5": md5_of(DVS),
            "dv_units": dvs.get("_units"),
            "dv_scalers_applied": dvs.get("_scalers_applied"),
            "dv_preimage_md5": dvs.get("_preimage_md5"),
            "n_twist": len(dvs["twist"]), "n_shape": len(dvs["shape"]),
            "n_patchV": len(dvs["patchV"]),
            "endpoint_final_CD_from_history": dvs.get("_final_CD"),
            "endpoint_final_CL_from_history": dvs.get("_final_CL"),
        }
        with open(OUT, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        sys.stdout.write("D7FR_ACCEPT_PRIMAL_WRITTEN %s CD=%r CL=%r wall_s=%.1f\n"
                         % (OUT, cd, cl, wall))
        sys.stdout.flush()
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
