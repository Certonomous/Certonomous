#!/usr/bin/env python3
"""Curriculum D8 producer -- generates an arm runScript.py from base/runScript.py.

FROZEN INSTRUMENT.  Registered in `PREREGISTRATION.md` s9 by md5.  Every edit
asserts its anchor count == 1 and dies otherwise: a producer that silently
matched zero anchors would emit the UNMODIFIED tutorial script and the arm would
run the wrong problem while looking correct (L-302's class).

Usage:  d8_gen_arm.py <armdir> [key=value ...]
keys:   endTime tolDiff minIters printInterval maxIter
"""
import os, sys, re

armdir = sys.argv[1]
kw = dict(a.split("=", 1) for a in sys.argv[2:])
endTime       = kw.get("endTime", "1000")
tolDiff       = kw.get("tolDiff", "1.0e4")
minIters      = kw.get("minIters", "1000")
printInterval = kw.get("printInterval", "10")
maxIter       = kw.get("maxIter", "3")

p = os.path.join(armdir, "runScript.py")
src = open(p).read()


def sub1(text, old, new, tag):
    n = text.count(old)
    assert n == 1, "ANCHOR %s count=%d (expected 1)" % (tag, n)
    return text.replace(old, new)


# --- E1: transonicPCOption 2 -> 1 (the value the graded A6 N=16 rows ran) ----
src = sub1(src, '"transonicPCOption": 2,', '"transonicPCOption": 1,', "E1")

# --- E2: primal acceptance gate + false-convergence exit + print interval ----
#   Without primalMinResTolDiff the A6 primal (556x short of primalMinResTol) is
#   rejected by DASolver::checkPrimalFailure() and EVERY primal raises
#   AnalysisError -- measured, rung_n16_np1/RESULTS.md s3.
#   minIters == endTime closes DASolver.C:188's -1e10 exit (N-D17).
_ins = ('"primalMinResTol": 1.0e-8,\n'
        '    "primalMinResTolDiff": %s,\n'
        '    "primalMinIters": %s,\n'
        '    "printInterval": %s,' % (tolDiff, minIters, printInterval))
src = sub1(src, '"primalMinResTol": 1.0e-8,', _ins, "E2")

# --- E3: TWIST-ONLY.  Remove the `shape` local FFD design variable. ----------
src = sub1(src, """        # select the FFD points to move
        pts = self.geometry.DVGeo.getLocalIndex(0)
        indexList = pts[:, :, :].flatten()
        PS = geo_utils.PointSelect("list", indexList)
        nShapes = self.geometry.nom_addLocalDV(dvName="shape", pointSelect=PS)
""", """        # D8 EDIT 3 (twist-only): the `shape` local FFD DV is NOT added.
""", "E3a")
src = sub1(src, '        self.dvs.add_output("shape", val=np.array([0] * nShapes))\n', "", "E3b")
src = sub1(src, '        self.connect("shape", "geometry.shape")\n', "", "E3c")
src = sub1(src, '        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)\n', "", "E3d")

# --- E4: the LE/TE constraints constrain LOCAL shape DVs, which no longer -----
#         exist.  Both the DVGeo registration and the add_constraint go.
src = sub1(src, """        # add the LE/TE constraints
        self.geometry.nom_add_LETEConstraint("lecon", volID=0, faceID="iLow")
        self.geometry.nom_add_LETEConstraint("tecon", volID=0, faceID="iHigh")
""", """        # D8 EDIT 4: LE/TE constraints act on local shape DVs; none exist here.
""", "E4a")
src = sub1(src, '        self.add_constraint("geometry.tecon", equals=0.0, scaler=1.0, linear=True)\n', "", "E4b")
src = sub1(src, '        self.add_constraint("geometry.lecon", equals=0.0, scaler=1.0, linear=True)\n', "", "E4c")

# --- E5: the registered IPOPT major cap --------------------------------------
src = sub1(src, '"max_iter": 100,', '"max_iter": %s,' % maxIter, "E5")

# --- E6/E7: the D8 task branches ---------------------------------------------
anchor = 'else:\n    print("task arg not found!")'
NEW = '''elif args.task == "optd8":
    import json
    try:
        _dv = prob.model.get_design_vars()
        _rs = prob.model.get_responses()
        if MPI.COMM_WORLD.rank == 0:
            print("D8_DVS %s" % sorted([(k, int(v.get("size", -1))) for k, v in _dv.items()]))
            print("D8_RESPONSES %s" % sorted([(k, int(v.get("size", -1))) for k, v in _rs.items()]))
    except Exception as _e:
        if MPI.COMM_WORLD.rank == 0:
            print("D8_DVS_ERR %r" % (_e,))
    prob.run_model()
    cd_cold = float(prob.get_val("scenario1.aero_post.CD")[0])
    cl_cold = float(prob.get_val("scenario1.aero_post.CL")[0])
    if MPI.COMM_WORLD.rank == 0:
        print("D8_COLD_CD %r" % cd_cold)
        print("D8_COLD_CL %r" % cl_cold)
    optFuncs.findFeasibleDesign(["scenario1.aero_post.CL"], ["patchV"], targets=[CL_target],
                                designVarsComp=[1], epsFD=[1.0e-1], tol=1.0e-3, maxIter=4)
    prob.run_model()
    cd_s = float(prob.get_val("scenario1.aero_post.CD")[0])
    cl_s = float(prob.get_val("scenario1.aero_post.CL")[0])
    dv_s = {"twist": [float(x) for x in prob.get_val("twist")],
            "patchV": [float(x) for x in prob.get_val("patchV")]}
    if MPI.COMM_WORLD.rank == 0:
        print("D8_START_CD %r" % cd_s)
        print("D8_START_CL %r" % cl_s)
        print("D8_START_DVS %s" % json.dumps(dv_s))
        open("/mnt/d8_start_dvs.json", "w").write(json.dumps({"CD": cd_s, "CL": cl_s, "dvs": dv_s}, indent=1))
    prob.run_driver()
    cd_f = float(prob.get_val("scenario1.aero_post.CD")[0])
    cl_f = float(prob.get_val("scenario1.aero_post.CL")[0])
    dv_f = {"twist": [float(x) for x in prob.get_val("twist")],
            "patchV": [float(x) for x in prob.get_val("patchV")]}
    if MPI.COMM_WORLD.rank == 0:
        print("D8_FINAL_CD %r" % cd_f)
        print("D8_FINAL_CL %r" % cl_f)
        print("D8_FINAL_DVS %s" % json.dumps(dv_f))
        open("/mnt/d8_dvs.json", "w").write(json.dumps({"CD": cd_f, "CL": cl_f, "dvs": dv_f}, indent=1))
    prob.set_val("twist", np.array(dv_f["twist"]))
    prob.set_val("patchV", np.array(dv_f["patchV"]))
    prob.run_model()
    cd_e = float(prob.get_val("scenario1.aero_post.CD")[0])
    if MPI.COMM_WORLD.rank == 0:
        print("D8_ADJPOINT_CD %r" % cd_e)
    _of = "scenario1.aero_post.CD"
    try:
        tot = prob.compute_totals(of=[_of], wrt=["twist", "patchV"])
    except Exception as _e1:
        if MPI.COMM_WORLD.rank == 0:
            print("D8_OF_FALLBACK %r" % (_e1,))
        _of = "scenario1.aero_post.functionals.CD"
        tot = prob.compute_totals(of=[_of], wrt=["twist", "patchV"])
    if MPI.COMM_WORLD.rank == 0:
        _out = {"CD": cd_e}
        for dvn in ("twist", "patchV"):
            row = np.atleast_1d(np.array(tot[(_of, dvn)]).ravel())
            _out[dvn] = [float(x) for x in row]
            for i, v in enumerate(row):
                print("ADJ_DERIV dv=%s idx=%d deriv=%r" % (dvn, i, float(v)))
        open("/mnt/d8_adj.json", "w").write(json.dumps(_out, indent=1))
    if MPI.COMM_WORLD.rank == 0:
        print("D8_OPT_ARM_COMPLETE")
elif args.task == "fdsub8":
    import json
    plan = json.loads(open("/mnt/fdplan.json").read())
    dvs0 = json.loads(open("/mnt/d8_dvs.json").read())["dvs"]
    for _k in sorted(dvs0):
        prob.set_val(_k, np.array(dvs0[_k]))
    prob.run_model()
    cd0 = float(prob.get_val("scenario1.aero_post.CD")[0])
    if MPI.COMM_WORLD.rank == 0:
        print("FD_BASELINE_CD %r" % cd0)
    base = {}
    for dv in sorted(set(p["dv"] for p in plan)):
        base[dv] = prob.get_val(dv).copy()
    for p in plan:
        dv, idx, step = p["dv"], int(p["idx"]), float(p["step"])
        vals = {}
        for sgn in (1.0, -1.0):
            x = base[dv].copy()
            x[idx] = x[idx] + sgn * step
            prob.set_val(dv, x)
            prob.run_model()
            vals[sgn] = float(prob.get_val("scenario1.aero_post.CD")[0])
            if MPI.COMM_WORLD.rank == 0:
                print("FD_POINT dv=%s idx=%d step=%r sgn=%+g CD=%r" % (dv, idx, step, sgn, vals[sgn]))
        prob.set_val(dv, base[dv].copy())
        d = (vals[1.0] - vals[-1.0]) / (2.0 * step)
        if MPI.COMM_WORLD.rank == 0:
            print("FD_DERIV dv=%s idx=%d step=%r deriv=%r" % (dv, idx, step, d))
    if MPI.COMM_WORLD.rank == 0:
        print("D8_FD_ARM_COMPLETE")
'''
src = sub1(src, anchor, NEW + anchor, "E6")

open(p, "w").write(src)

# --- E8: endTime in system/controlDict ---------------------------------------
cdp = os.path.join(armdir, "system", "controlDict")
cd = open(cdp).read()
n = len(re.findall(r"^endTime\s+1000;", cd, re.M))
assert n == 1, "ANCHOR E8 count=%d" % n
cd = re.sub(r"^endTime\s+1000;", "endTime         %s;" % endTime, cd, flags=re.M)
open(cdp, "w").write(cd)

print("D8_GEN OK arm=%s endTime=%s tolDiff=%s minIters=%s printInterval=%s maxIter=%s"
      % (armdir, endTime, tolDiff, minIters, printInterval, maxIter))
