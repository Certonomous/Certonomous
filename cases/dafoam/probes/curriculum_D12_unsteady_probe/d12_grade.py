#!/usr/bin/env python3
"""
CURRICULUM D12 CAPABILITY PROBE grader.  Frozen instrument.

Grades unsteady-adjoint (`DAPimpleFoam`, unsteadyAdjoint mode timeAccurate)
reachability on the installed DAFoam image from artifacts on disk, and reports the
checkpoint-storage envelope (RAM AND disk).  REFUSES (exit 2) rather than degrading.

L-302 discipline: every list is asserted NON-EMPTY before it is iterated.

Exit codes: 0 verdict rendered; 2 REFUSAL.
"""
import json, os, sys, math, argparse, re

PLANT_SHAPE = 1.234e-03
END_TIME = "0.05"
FLOOR_VALUE = 1.0e-12
FLOOR_PLANT_REL = 1.0e-9
CLEAN_TOL_REL = 1.0e-12
FLOOR_DERIV = 1.0e-12


class Refusal(Exception):
    pass


def _finite(x):
    return isinstance(x, float) and math.isfinite(x)


def read_json(path):
    if not os.path.isfile(path):
        raise Refusal("artifact missing: %s" % path)
    with open(path) as f:
        return json.load(f)


def completion_evidence(root, stage):
    """Strict-completion elements available to this probe (CLAUDE.md rule 4)."""
    logs = sorted(f for f in os.listdir(root) if f.startswith(stage + "_") and f.endswith(".log"))
    if not logs:
        raise Refusal("no stage log for %s -- completion cannot be established" % stage)
    txt = open(os.path.join(root, logs[-1]), errors="replace").read()
    has_end = bool(re.search(r"^End\s*$", txt, re.M))
    endtime_dir = os.path.isdir(os.path.join(root, stage, END_TIME))
    return {"log": logs[-1], "End_line": has_end, "endTime_dir_%s" % END_TIME: endtime_dir}


def grade(base, plant, clean, ledger_rows):
    g = {}

    # ---- kernel's own verdict first: the named failure mode is storage explosion
    oom = [r for r in ledger_rows if r.get("oomkilled") == "true"]
    if oom:
        return "BLOCKED", {"G12-4": ("BLOCKED", "OOMKilled true on stage(s) %s -- the checkpoint "
                                                "envelope is exceeded at probe scale"
                                     % [r["stage"] for r in oom])}

    if base.get("status") != "COMPLETE":
        return "BLOCKED", {"G12-1": ("BLOCKED", "base stage did not COMPLETE; status=%r" % base.get("status"))}
    for nm, r in (("base", base), ("plant", plant), ("clean", clean)):
        if not _finite(r.get("obj")):
            raise Refusal("obj (time-averaged CD) in %s stage is not a finite float: %r" % (nm, r.get("obj")))
    ob, op, oc = base["obj"], plant["obj"], clean["obj"]
    if abs(ob) <= FLOOR_VALUE:
        g["G12-1"] = ("GATE FAIL", "|obj| = %.6e <= floor %.1e" % (abs(ob), FLOOR_VALUE))
        return "GATE FAIL", g
    g["G12-1"] = ("PASS", "DAPimpleFoam unsteady primal completed; time-averaged CD = %.10e" % ob)

    clean_rel = abs(oc - ob) / abs(ob)
    if clean_rel > CLEAN_TOL_REL:
        raise Refusal("clean-copy control FAILED: an unplanted re-run moved the time-averaged "
                      "objective by %.6e relative (tol %.1e); no plant response can be attributed"
                      % (clean_rel, CLEAN_TOL_REL))
    g["G12-3a"] = ("PASS", "clean copy reproduces base to %.3e relative (tol %.1e)" % (clean_rel, CLEAN_TOL_REL))

    ps = plant.get("shape")
    if not isinstance(ps, list) or len(ps) == 0:
        raise Refusal("plant stage recorded no shape vector -- the plant cannot be read back")
    if abs(ps[0] - PLANT_SHAPE) > 1e-15:
        raise Refusal("plant read-back FAILED: plant stage shape[0] on disk is %r, expected %r"
                      % (ps[0], PLANT_SHAPE))
    plant_rel = abs(op - ob) / abs(ob)
    if plant_rel <= FLOOR_PLANT_REL:
        raise Refusal("PLANTED-ZERO REFUSAL: a %.4e plant in shape[0] moved the time-averaged "
                      "objective by only %.6e relative (floor %.1e). The objective has not been "
                      "shown able to see the design variable, so no derivative here is evidence."
                      % (PLANT_SHAPE, plant_rel, FLOOR_PLANT_REL))
    g["G12-3b"] = ("PASS", "plant response %.6e relative > floor %.1e (obj_plant = %.10e)"
                   % (plant_rel, FLOOR_PLANT_REL, op))

    if "dobj_dshape" not in base:
        return "BLOCKED", dict(g, **{"G12-2": ("BLOCKED", "no dobj_dshape key -- the unsteady adjoint never returned")})
    d = base["dobj_dshape"]
    if not isinstance(d, list):
        raise Refusal("dobj_dshape is not a list: %r" % type(d))
    if len(d) == 0:
        raise Refusal("dobj_dshape is an EMPTY component set -- zero comparisons would be made")
    for i, v in enumerate(d):
        if not _finite(v):
            g["G12-2"] = ("GATE FAIL", "component %d of d(obj)/d(shape) is %r (NaN/inf)" % (i, v))
            return "GATE FAIL", g
    mx = max(abs(v) for v in d)
    if mx <= FLOOR_DERIV:
        g["G12-2"] = ("GATE FAIL", "SILENTLY-ZERO unsteady adjoint: max |d(obj)/d(shape)| = %.6e over "
                                   "%d components, <= floor %.1e" % (mx, len(d), FLOOR_DERIV))
        return "GATE FAIL", g
    g["G12-2"] = ("PASS", "max |d(obj)/d(shape)| = %.10e over %d components (values %s)"
                  % (mx, len(d), ["%.10e" % v for v in d]))
    return "GATE REACHED", g


def parse_ledger(path):
    rows = []
    if not os.path.isfile(path):
        return rows
    for line in open(path):
        if not line.startswith("STAGE="):
            continue
        r = {}
        m = re.search(r"STAGE=(\S+)", line)
        r["stage"] = m.group(1) if m else "?"
        m = re.search(r"oomkilled\)=\[(\d+) (\w+)\]", line)
        if m:
            r["exitcode"], r["oomkilled"] = m.group(1), m.group(2)
        for k in ("wall_s", "core_min", "du_before_B", "du_after_B", "du_delta_B", "rc"):
            m = re.search(k + r"=(-?[\d.]+)", line)
            if m:
                r[k] = m.group(1)
        rows.append(r)
    return rows


def selftest():
    lr = [{"stage": "base", "oomkilled": "false"}]
    b = {"status": "COMPLETE", "obj": 1.5, "dobj_dshape": [0.1, -0.2, 0.3, 0.05]}
    p = {"status": "COMPLETE", "obj": 1.6, "shape": [PLANT_SHAPE, 0, 0, 0]}
    c = {"status": "COMPLETE", "obj": 1.5, "shape": [0, 0, 0, 0]}
    v, _ = grade(b, p, c, lr)
    assert v == "GATE REACHED", "selftest A: healthy record did not reach the gate, got %r" % v
    try:
        grade(b, dict(p, obj=1.5), c, lr); raise AssertionError("selftest B: blind objective did NOT refuse")
    except Refusal:
        pass
    v, _ = grade(dict(b, dobj_dshape=[0.0] * 4), p, c, lr)
    assert v == "GATE FAIL", "selftest C: zero unsteady adjoint did not GATE FAIL, got %r" % v
    try:
        grade(dict(b, dobj_dshape=[]), p, c, lr); raise AssertionError("selftest D: EMPTY set did NOT refuse")
    except Refusal:
        pass
    v, _ = grade(dict(b, dobj_dshape=[float("nan")] * 4), p, c, lr)
    assert v == "GATE FAIL", "selftest E: NaN adjoint did not GATE FAIL, got %r" % v
    v, _ = grade(b, p, c, [{"stage": "base", "oomkilled": "true"}])
    assert v == "BLOCKED", "selftest F: OOMKilled did not map to BLOCKED, got %r" % v
    try:
        grade(b, dict(p, shape=[0.0, 0, 0, 0]), c, lr); raise AssertionError("selftest G: bad plant read-back did NOT refuse")
    except Refusal:
        pass
    v, _ = grade({"status": "COMPLETE", "obj": 1.5}, p, c, lr)
    assert v == "BLOCKED", "selftest H: absent adjoint did not map to BLOCKED, got %r" % v
    print("D12 GRADER SELFTEST: 8/8 PASS (A healthy, B blind-plant refuses, C zero-adjoint GATE FAIL, "
          "D empty-set refuses, E NaN GATE FAIL, F OOMKilled BLOCKED, G bad plant read-back refuses, "
          "H absent adjoint BLOCKED)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D12")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    rows = parse_ledger(os.path.join(a.root, "ledger.txt"))
    try:
        base = read_json(os.path.join(a.root, "base", "d12_base.json"))
        plant = read_json(os.path.join(a.root, "plant", "d12_plant.json"))
        clean = read_json(os.path.join(a.root, "clean", "d12_clean.json"))
        ce = completion_evidence(a.root, "base")
        verdict, gates = grade(base, plant, clean, rows)
    except Refusal as e:
        print("D12 PROBE VERDICT: NOT A RESULT")
        print("GRADER REFUSED (exit 2): %s" % e)
        return 2
    for k in sorted(gates):
        print("  %-8s %-12s %s" % (k, gates[k][0], gates[k][1]))
    print("  completion evidence (base): %s" % ce)
    print("  ENVELOPE maxrss_GiB_after_primal  = %s" % base.get("maxrss_GiB_after_primal"))
    print("  ENVELOPE maxrss_GiB_after_adjoint = %s" % base.get("maxrss_GiB_after_adjoint"))
    for r in rows:
        print("  ENVELOPE stage=%-6s du_delta_B=%s oomkilled=%s core_min=%s"
              % (r.get("stage"), r.get("du_delta_B"), r.get("oomkilled"), r.get("core_min")))
    print("D12 PROBE VERDICT: %s" % verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
