#!/usr/bin/env python3
"""
CURRICULUM D10 CAPABILITY PROBE grader.  Frozen instrument.

Grades thermal-objective (`wallHeatFlux`) reachability on the installed DAFoam
image from artifacts on disk.  REFUSES (exit 2) rather than degrading.

L-302 discipline, applied deliberately: every list this grader iterates is
asserted NON-EMPTY before the loop, and the discrimination control measures the
SAME quantity that reaches the verdict.  A gate whose component set is empty is
NOT A RESULT, never PASS.

Verdict vocabulary is fixed: PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING.

Exit codes: 0 verdict rendered; 2 REFUSAL (grader could not measure).
"""
import json, os, sys, math, argparse

PLANTED_T = "294.384"     # 293.15 + 1.234 K, planted into the plant stage's 0/T
BASE_T = "293.15"
FLOOR_VALUE = 1.0e-12     # |HFX| must exceed this
FLOOR_PLANT_REL = 1.0e-6  # relative HFX response to the plant must exceed this
CLEAN_TOL_REL = 1.0e-12   # unplanted clean copy must reproduce base to this
FLOOR_DERIV = 1.0e-12     # max |d(HFX)/d(patchV)| must exceed this


class Refusal(Exception):
    pass


def _finite(x):
    return isinstance(x, float) and math.isfinite(x)


def read_json(path):
    if not os.path.isfile(path):
        raise Refusal("artifact missing: %s" % path)
    with open(path) as f:
        return json.load(f)


def read_plant_from_disk(tfile, expect):
    """Plant read-back (CLAUDE.md rule 3): the planted value must be visible ON DISK."""
    if not os.path.isfile(tfile):
        raise Refusal("plant read-back impossible, no such file: %s" % tfile)
    txt = open(tfile).read()
    if ("uniform %s;" % expect) not in txt:
        raise Refusal("plant read-back FAILED: %s does not carry 'uniform %s;'" % (tfile, expect))
    return expect


def grade(base, plant, clean):
    """Returns (verdict, gates dict).  Raises Refusal when it cannot measure."""
    g = {}

    # ---- G10-1  the thermal function was constructed and a value reached disk
    if base.get("status") != "COMPLETE":
        return "BLOCKED", {"G10-1": ("BLOCKED", "base stage did not COMPLETE; status=%r" % base.get("status"))}
    if "HFX" not in base:
        return "BLOCKED", {"G10-1": ("BLOCKED", "no HFX key in base record -- wallHeatFlux not constructed")}
    g["G10-1"] = ("PASS", "wallHeatFlux constructed; HFX present in base record")

    hfx_b = base["HFX"]
    hfx_p = plant.get("HFX")
    hfx_c = clean.get("HFX")
    for nm, v in (("base", hfx_b), ("plant", hfx_p), ("clean", hfx_c)):
        if not _finite(v):
            raise Refusal("HFX in %s stage is not a finite float: %r" % (nm, v))

    # ---- G10-3a  DISCRIMINATION CONTROL: the unplanted clean copy reproduces base
    #      (measured on the SAME quantity that reaches the verdict -- HFX)
    denom = abs(hfx_b)
    if denom <= FLOOR_VALUE:
        # a zero baseline makes every relative test meaningless
        g["G10-2"] = ("GATE FAIL", "|HFX_base| = %.6e <= floor %.1e" % (denom, FLOOR_VALUE))
        return "GATE FAIL", g
    g["G10-2"] = ("PASS", "HFX_base = %.10e, finite and above floor %.1e" % (hfx_b, FLOOR_VALUE))

    clean_rel = abs(hfx_c - hfx_b) / denom
    if clean_rel > CLEAN_TOL_REL:
        raise Refusal(
            "clean-copy control FAILED: unplanted re-run moved HFX by %.6e relative "
            "(tol %.1e); a plant response cannot be attributed" % (clean_rel, CLEAN_TOL_REL))
    g["G10-3a"] = ("PASS", "clean copy reproduces base to %.3e relative (tol %.1e)" % (clean_rel, CLEAN_TOL_REL))

    # ---- G10-3b  PLANTED CONTROL: HFX must SEE a known perturbation of T
    plant_rel = abs(hfx_p - hfx_b) / denom
    if plant_rel <= FLOOR_PLANT_REL:
        raise Refusal(
            "PLANTED-ZERO REFUSAL: a +1.234 K plant in 0/T moved HFX by only %.6e "
            "relative (floor %.1e). The reader has not been shown able to see a "
            "non-zero, so no HFX number here is evidence." % (plant_rel, FLOOR_PLANT_REL))
    g["G10-3b"] = ("PASS", "plant response %.6e relative > floor %.1e (HFX_plant = %.10e)"
                   % (plant_rel, FLOOR_PLANT_REL, hfx_p))

    # ---- G10-4  the thermal objective reaches the ADJOINT
    if "dHFX_dpatchV" not in base:
        return "BLOCKED", dict(g, **{"G10-4": ("BLOCKED", "no dHFX_dpatchV key -- adjoint never returned")})
    d = base["dHFX_dpatchV"]
    if not isinstance(d, list):
        raise Refusal("dHFX_dpatchV is not a list: %r" % type(d))
    # L-302: NON-EMPTINESS is asserted BEFORE the loop, not inferred from key presence
    if len(d) == 0:
        raise Refusal("dHFX_dpatchV is an EMPTY component set -- zero comparisons would be made")
    for i, v in enumerate(d):
        if not _finite(v):
            g["G10-4"] = ("GATE FAIL", "component %d of d(HFX)/d(patchV) is %r (NaN/inf)" % (i, v))
            return "GATE FAIL", g
    mx = max(abs(v) for v in d)
    if mx <= FLOOR_DERIV:
        g["G10-4"] = ("GATE FAIL",
                      "SILENTLY-ZERO thermal adjoint: max |d(HFX)/d(patchV)| = %.6e over %d "
                      "components, <= floor %.1e" % (mx, len(d), FLOOR_DERIV))
        return "GATE FAIL", g
    g["G10-4"] = ("PASS", "max |d(HFX)/d(patchV)| = %.10e over %d components (values %s)"
                  % (mx, len(d), ["%.10e" % v for v in d]))

    return "GATE REACHED", g


def selftest():
    """Proves the controls can refuse AND can pass -- a control that cannot fail is not one."""
    good_b = {"status": "COMPLETE", "HFX": 1.0e3, "dHFX_dpatchV": [1.0, 2.0]}
    good_p = {"status": "COMPLETE", "HFX": 1.1e3}
    good_c = {"status": "COMPLETE", "HFX": 1.0e3}
    v, _ = grade(good_b, good_p, good_c)
    assert v == "GATE REACHED", "selftest A: healthy record did not reach the gate, got %r" % v

    # blind objective: plant moved nothing
    try:
        grade(good_b, {"status": "COMPLETE", "HFX": 1.0e3}, good_c)
        raise AssertionError("selftest B: blind-objective plant did NOT refuse")
    except Refusal:
        pass

    # silently-zero adjoint
    v, g = grade({"status": "COMPLETE", "HFX": 1.0e3, "dHFX_dpatchV": [0.0, 0.0]}, good_p, good_c)
    assert v == "GATE FAIL", "selftest C: zero adjoint did not GATE FAIL, got %r" % v

    # EMPTY component set -- the L-302 trap
    try:
        grade({"status": "COMPLETE", "HFX": 1.0e3, "dHFX_dpatchV": []}, good_p, good_c)
        raise AssertionError("selftest D: EMPTY component set did NOT refuse")
    except Refusal:
        pass

    # noisy clean copy
    try:
        grade(good_b, good_p, {"status": "COMPLETE", "HFX": 1.0e3 * (1 + 1e-6)})
        raise AssertionError("selftest E: noisy clean copy did NOT refuse")
    except Refusal:
        pass

    # missing function -> BLOCKED
    v, _ = grade({"status": "COMPLETE"}, good_p, good_c)
    assert v == "BLOCKED", "selftest F: absent HFX did not map to BLOCKED, got %r" % v
    print("D10 GRADER SELFTEST: 6/6 PASS (A healthy, B blind-plant refuses, C zero-adjoint "
          "GATE FAIL, D empty-set refuses, E noisy-clean refuses, F absent-function BLOCKED)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D10")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    try:
        # plant read-back FROM DISK, before anything is graded
        read_plant_from_disk(os.path.join(a.root, "plant", "0", "T"), PLANTED_T)
        read_plant_from_disk(os.path.join(a.root, "base", "0", "T"), BASE_T)
        read_plant_from_disk(os.path.join(a.root, "clean", "0", "T"), BASE_T)
        base = read_json(os.path.join(a.root, "base", "d10_base.json"))
        plant = read_json(os.path.join(a.root, "plant", "d10_plant.json"))
        clean = read_json(os.path.join(a.root, "clean", "d10_clean.json"))
        verdict, gates = grade(base, plant, clean)
    except Refusal as e:
        print("D10 PROBE VERDICT: NOT A RESULT")
        print("GRADER REFUSED (exit 2): %s" % e)
        return 2
    for k in sorted(gates):
        print("  %-8s %-12s %s" % (k, gates[k][0], gates[k][1]))
    print("D10 PROBE VERDICT: %s" % verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
