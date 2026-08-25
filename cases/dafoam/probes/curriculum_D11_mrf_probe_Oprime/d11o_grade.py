#!/usr/bin/env python3
"""
CURRICULUM D11-Oprime CAPABILITY PROBE grader (the omega re-buy, attempt three and last).  Frozen instrument.

Grades MRF / rotating-frame ADJOINT reachability on the installed DAFoam image
from artifacts on disk.  REFUSES (exit 2) rather than degrading.

The named failure mode this exists to catch is SILENTLY-ZERO MRF derivatives, so
a zero is treated as the EXPECTED output of a broken probe and never as a result
until the plant has been shown to move the reader.  The plant is on the MRF ZONE
itself (constant/MRFProperties `omega`), not somewhere else in the domain.

L-302 discipline: every list is asserted NON-EMPTY before it is iterated.

Exit codes: 0 verdict rendered; 2 REFUSAL.
"""
import json, os, sys, math, argparse

OMEGA_PLANT = "30.0"
OMEGA_INERT = "0.0"
FD_H = 1.0e-3
FLOOR_VALUE = 1.0e-12
FLOOR_PLANT_REL = 1.0e-6
CLEAN_TOL_REL = 1.0e-12
FLOOR_DERIV = 1.0e-12
FD_BAND_REL = 5.0e-2      # 5.0 % adjoint-vs-FD band, MRF ON


class Refusal(Exception):
    pass


def _finite(x):
    return isinstance(x, float) and math.isfinite(x)


def read_json(path):
    if not os.path.isfile(path):
        raise Refusal("artifact missing: %s" % path)
    with open(path) as f:
        return json.load(f)


def read_omega_from_disk(path, expect):
    """Plant read-back (CLAUDE.md rule 3): the planted omega must be visible ON DISK."""
    if not os.path.isfile(path):
        raise Refusal("plant read-back impossible, no such file: %s" % path)
    for line in open(path):
        s = line.strip()
        if s.startswith("omega") and s.endswith(";"):
            got = s.split()[1].rstrip(";")
            if got != expect:
                raise Refusal("plant read-back FAILED: %s carries omega %s, expected %s" % (path, got, expect))
            return got
    raise Refusal("plant read-back FAILED: no omega entry in %s" % path)


def grade(oP, o0, clean, fdp, fdm):
    g = {}

    if oP.get("status") != "COMPLETE":
        return "BLOCKED", {"G11-1": ("BLOCKED", "omegaP stage did not COMPLETE; status=%r" % oP.get("status"))}
    for nm, r in (("omegaP", oP), ("omega0", o0), ("clean", clean), ("fdp", fdp), ("fdm", fdm)):
        if not _finite(r.get("TPIn")):
            raise Refusal("TPIn in %s stage is not a finite float: %r" % (nm, r.get("TPIn")))
    tp_P, tp_0, tp_c = oP["TPIn"], o0["TPIn"], clean["TPIn"]
    if abs(tp_0) <= FLOOR_VALUE:
        g["G11-1"] = ("GATE FAIL", "|TPIn(omega=0)| = %.6e <= floor %.1e" % (abs(tp_0), FLOOR_VALUE))
        return "GATE FAIL", g
    g["G11-1"] = ("PASS", "MRF-active primal completed; TPIn(omega=%s) = %.10e, TPIn(omega=0) = %.10e"
                  % (OMEGA_PLANT, tp_P, tp_0))

    # ---- discrimination control on the SAME quantity that reaches the verdict
    clean_rel = abs(tp_c - tp_0) / abs(tp_0)
    if clean_rel > CLEAN_TOL_REL:
        raise Refusal("clean-copy control FAILED: an identical omega=0 re-run moved TPIn by "
                      "%.6e relative (tol %.1e); no plant response can be attributed"
                      % (clean_rel, CLEAN_TOL_REL))
    g["G11-2a"] = ("PASS", "clean copy reproduces omega=0 to %.3e relative (tol %.1e)" % (clean_rel, CLEAN_TOL_REL))

    # ---- G11-2  THE PLANT, ON THE MRF ZONE
    plant_rel = abs(tp_P - tp_0) / abs(tp_0)
    if plant_rel <= FLOOR_PLANT_REL:
        raise Refusal("PLANTED-ZERO REFUSAL: switching the MRF zone from omega=0 to omega=%s rad/s "
                      "moved TPIn by only %.6e relative (floor %.1e). The MRF term is not entering "
                      "the primal, so NO derivative measured here is evidence about MRF."
                      % (OMEGA_PLANT, plant_rel, FLOOR_PLANT_REL))
    g["G11-2b"] = ("PASS", "MRF-zone plant response %.6e relative > floor %.1e" % (plant_rel, FLOOR_PLANT_REL))

    # ---- G11-3  the MRF-active adjoint returns a non-zero derivative
    if "dTPIn_dpatchV" not in oP:
        return "BLOCKED", dict(g, **{"G11-3": ("BLOCKED", "no dTPIn_dpatchV key -- MRF-active adjoint never returned")})
    dP = oP["dTPIn_dpatchV"]
    if not isinstance(dP, list):
        raise Refusal("dTPIn_dpatchV is not a list: %r" % type(dP))
    if len(dP) == 0:
        raise Refusal("dTPIn_dpatchV is an EMPTY component set -- zero comparisons would be made")
    for i, v in enumerate(dP):
        if not _finite(v):
            g["G11-3"] = ("GATE FAIL", "component %d of the MRF-active adjoint is %r (NaN/inf)" % (i, v))
            return "GATE FAIL", g
    mx = max(abs(v) for v in dP)
    if mx <= FLOOR_DERIV:
        g["G11-3"] = ("GATE FAIL", "SILENTLY-ZERO MRF-frame adjoint: max |d(TPIn)/d(patchV)| = %.6e "
                                   "over %d components, <= floor %.1e" % (mx, len(dP), FLOOR_DERIV))
        return "GATE FAIL", g
    g["G11-3"] = ("PASS", "max |d(TPIn)/d(patchV)| = %.10e over %d components (values %s)"
                  % (mx, len(dP), ["%.10e" % v for v in dP]))

    # ---- G11-4  DIAGNOSTIC: the derivative is not bit-identical with MRF off.
    #      Necessary, NOT sufficient -- the base states differ too.  GATE FAIL fires
    #      ONLY on exact identity, which would mean the omega key reached nothing.
    d0 = o0.get("dTPIn_dpatchV")
    if not isinstance(d0, list) or len(d0) != len(dP):
        g["G11-4"] = ("NOT A RESULT", "omega=0 derivative absent or of different length; comparison not formed")
    else:
        if all(a == b for a, b in zip(dP, d0)):
            g["G11-4"] = ("GATE FAIL", "the MRF-active and MRF-inert adjoint derivatives are BIT-IDENTICAL "
                                       "(%s) while the primal responded -- the omega key reached nothing"
                          % ["%.10e" % v for v in dP])
            return "GATE FAIL", g
        num = math.sqrt(sum((a - b) ** 2 for a, b in zip(dP, d0)))
        den = math.sqrt(sum(b * b for b in d0))
        rel = num / den if den > FLOOR_VALUE else float("inf")
        g["G11-4"] = ("PASS", "adjoint differs between omega=%s and omega=0 by %.6e relative L2 "
                              "(DIAGNOSTIC: necessary, not sufficient -- the base states differ too)"
                      % (OMEGA_PLANT, rel))

    # ---- G11-5  linearisation consistency with MRF ON: adjoint vs central FD
    fd = (fdp["TPIn"] - fdm["TPIn"]) / (2.0 * FD_H)
    adj = dP[0]
    if abs(fd) <= FLOOR_VALUE:
        g["G11-5"] = ("NOT A RESULT", "central FD reference is %.6e <= floor %.1e; the ratio cannot be formed" % (fd, FLOOR_VALUE))
        return "NOT A RESULT", g
    err = abs(adj - fd) / abs(fd)
    if err > FD_BAND_REL:
        g["G11-5"] = ("GATE FAIL", "MRF-ON adjoint vs central FD: adj = %.10e, FD = %.10e, "
                                   "relative error %.6e > band %.3e" % (adj, fd, err, FD_BAND_REL))
        return "GATE FAIL", g
    g["G11-5"] = ("PASS", "MRF-ON adjoint vs central FD (h = %.1e): adj = %.10e, FD = %.10e, "
                          "relative error %.6e <= band %.3e" % (FD_H, adj, fd, err, FD_BAND_REL))
    return "GATE REACHED", g


def selftest():
    oP = {"status": "COMPLETE", "TPIn": 2.0, "dTPIn_dpatchV": [0.40, 0.01]}
    o0 = {"status": "COMPLETE", "TPIn": 1.0, "dTPIn_dpatchV": [0.20, 0.01]}
    cl = {"status": "COMPLETE", "TPIn": 1.0}
    fp = {"status": "COMPLETE", "TPIn": 2.0 + 0.40 * FD_H}
    fm = {"status": "COMPLETE", "TPIn": 2.0 - 0.40 * FD_H}
    v, _ = grade(oP, o0, cl, fp, fm)
    assert v == "GATE REACHED", "selftest A: healthy record did not reach the gate, got %r" % v

    try:  # MRF inert in the primal -> the plant moved nothing
        grade(dict(oP, TPIn=1.0), o0, cl, fp, fm)
        raise AssertionError("selftest B: inert-MRF plant did NOT refuse")
    except Refusal:
        pass

    v, _ = grade(dict(oP, dTPIn_dpatchV=[0.0, 0.0]), o0, cl, fp, fm)
    assert v == "GATE FAIL", "selftest C: silently-zero MRF adjoint did not GATE FAIL, got %r" % v

    try:
        grade(dict(oP, dTPIn_dpatchV=[]), o0, cl, fp, fm)
        raise AssertionError("selftest D: EMPTY component set did NOT refuse")
    except Refusal:
        pass

    v, _ = grade(oP, dict(o0, dTPIn_dpatchV=[0.40, 0.01]), cl, fp, fm)
    assert v == "GATE FAIL", "selftest E: bit-identical adjoints did not GATE FAIL, got %r" % v

    v, _ = grade(oP, o0, cl, {"status": "COMPLETE", "TPIn": 2.0 + 1.0 * FD_H},
                 {"status": "COMPLETE", "TPIn": 2.0 - 1.0 * FD_H})
    assert v == "GATE FAIL", "selftest F: adjoint-FD disagreement did not GATE FAIL, got %r" % v

    try:
        grade(oP, o0, {"status": "COMPLETE", "TPIn": 1.0 * (1 + 1e-6)}, fp, fm)
        raise AssertionError("selftest G: noisy clean copy did NOT refuse")
    except Refusal:
        pass
    print("D11-Oprime GRADER SELFTEST: 7/7 PASS (A healthy, B inert-MRF refuses, C zero-adjoint GATE FAIL, "
          "D empty-set refuses, E bit-identical GATE FAIL, F FD-disagreement GATE FAIL, G noisy-clean refuses)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/D11O")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    try:
        read_omega_from_disk(os.path.join(a.root, "omegaP", "constant", "MRFProperties"), OMEGA_PLANT)
        read_omega_from_disk(os.path.join(a.root, "omega0", "constant", "MRFProperties"), OMEGA_INERT)
        read_omega_from_disk(os.path.join(a.root, "clean", "constant", "MRFProperties"), OMEGA_INERT)
        oP = read_json(os.path.join(a.root, "omegaP", "d11o_omegaP.json"))
        o0 = read_json(os.path.join(a.root, "omega0", "d11o_omega0.json"))
        cl = read_json(os.path.join(a.root, "clean", "d11o_clean.json"))
        fp = read_json(os.path.join(a.root, "fdp", "d11o_fdp.json"))
        fm = read_json(os.path.join(a.root, "fdm", "d11o_fdm.json"))
        verdict, gates = grade(oP, o0, cl, fp, fm)
    except Refusal as e:
        print("D11-Oprime PROBE VERDICT: NOT A RESULT")
        print("GRADER REFUSED (exit 2): %s" % e)
        return 2
    for k in sorted(gates):
        print("  %-8s %-12s %s" % (k, gates[k][0], gates[k][1]))
    print("D11-Oprime PROBE VERDICT: %s" % verdict)
    return 0


if __name__ == "__main__":
    sys.exit(main())
