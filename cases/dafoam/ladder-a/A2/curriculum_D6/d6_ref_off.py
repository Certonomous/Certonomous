#!/usr/bin/env python
"""Curriculum D6 -- REF_off: D4's PATCHED optimum geometry re-trimmed to the
off-design CL targets 0.4 and 0.6 (and re-checked at 0.5) by findFeasibleDesign
on each point's patchV (AoA) ONLY -- no shape or twist change.  This is the
off-design reference that makes "single-point dominance" measurable (G-D6-1).

  * The model is the producer's own bytes: d6_opt_runScript.py is read, its md5
    asserted, split at the literal anchor `# OpenMDAO setup`, and the header
    exec'd -- so the three scenarios, the composite J and the DVs are exactly
    the ones O_mp optimises.
  * D4's endpoint DVs come from d4_endpoint_dvs.json, written by D4's own
    unmodified extractor from D4's OptView.hst staged read-only into this arm
    directory (md5-asserted by the launcher).  twist and shape are set to D4's
    endpoint; every patchV_cl0k starts at D4's endpoint AoA.
  * findFeasibleDesign solves CL(cl04)=0.4, CL(cl05)=0.5, CL(cl06)=0.6 on
    patchV_cl04 / patchV_cl05 / patchV_cl06 (component 1, the AoA) at once,
    the multipoint form; the trimmed CD at every point is written to a FILE by
    rank 0 (d6_ref_off.json), never recovered from stdout.
  * CONSISTENCY CHECK, recorded not gated: CD(cl05) after the re-trim should
    reproduce D4's CD_f = 2.1125978108239574e-02 to the trim tolerance; the
    difference is written beside it for the grader to report.
"""
import hashlib
import json
import os
import sys
import time

PRODUCER = "d6_opt_runScript.py"
PRODUCER_MD5 = "ae4b0305f0395b0047f1ce042d4956a5"
ANCHOR = "# OpenMDAO setup"
D4_ENDPOINT = "d4_endpoint_dvs.json"
OUT = "d6_ref_off.json"
CD_F_D4_RECORDED = 2.1125978108239574e-02


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def refuse(msg):
    sys.stderr.write("D6_REF_OFF REFUSE %s\n" % msg)
    sys.exit(2)


def main():
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
    ns = {"__name__": "d6_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    Top, OptFuncs = ns["Top"], ns["OptFuncs"]
    POINTS, CL_TARGETS, daOptions, U0 = ns["POINTS"], ns["CL_TARGETS"], ns["daOptions"], ns["U0"]

    if not os.path.isfile(D4_ENDPOINT):
        refuse("%s absent (D4's extractor must run first)" % D4_ENDPOINT)
    with open(D4_ENDPOINT) as fh:
        d4 = json.load(fh)
    for k in ("twist", "shape", "patchV"):
        if k not in d4:
            refuse("D4 endpoint file missing %s" % k)

    prob = om.Problem()
    prob.model = Top()
    prob.setup(mode="rev")
    optFuncs = OptFuncs([daOptions] * len(POINTS), prob)

    prob.set_val("twist", np.array(d4["twist"], dtype=float))
    prob.set_val("shape", np.array(d4["shape"], dtype=float))
    aoa_d4 = float(d4["patchV"][1])
    for pt in POINTS:
        prob.set_val("patchV_" + pt, np.array([U0, aoa_d4], dtype=float))

    t0 = time.time()
    optFuncs.findFeasibleDesign(["%s.aero_post.CL" % pt for pt in POINTS],
                                ["patchV_" + pt for pt in POINTS],
                                targets=[CL_TARGETS[pt] for pt in POINTS],
                                designVarsComp=[1] * len(POINTS))
    prob.run_model()
    wall = time.time() - t0

    res = {"producer_md5": got, "d4_endpoint_source": d4.get("_source"),
           "n_shape": len(d4["shape"]), "n_twist": len(d4["twist"]), "aoa_d4_start": aoa_d4,
           "J": repr(float(prob.get_val("obj.J")[0])), "trim_wall_s": round(wall, 3), "points": {}}
    for pt in POINTS:
        cd = float(prob.get_val("%s.aero_post.CD" % pt)[0])
        cl = float(prob.get_val("%s.aero_post.CL" % pt)[0])
        aoa = float(prob.get_val("patchV_" + pt)[1])
        res["points"][pt] = {"CL_target": CL_TARGETS[pt], "CL": repr(cl), "CD": repr(cd), "aoa": repr(aoa),
                             "CL_residual": repr(cl - CL_TARGETS[pt])}
    res["consistency_CD_cl05_minus_D4_CD_f"] = repr(float(res["points"]["cl05"]["CD"]) - CD_F_D4_RECORDED)
    if rank == 0:
        with open(OUT, "w") as fh:
            json.dump(res, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        sys.stdout.write("D6_REF_OFF_WRITTEN %s\n" % OUT)
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
