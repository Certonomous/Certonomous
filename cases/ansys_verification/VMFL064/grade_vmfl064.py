#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMFL064 -- Low Reynolds Number Flow in a Channel with Sudden Asymmetric Expansion.
Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p. 195/196.

GATE QUANTITY: non-dimensional reattachment length LR / s on the bottom wall
downstream of the step, s = 4.9 mm, origin at the step foot (x = 0).
The manual (p.195) fixes the definition: "Reattachment length is measured from the
reversal of the sign of the wall shear along the flow direction."

REFERENCE: LR/s = 5.0 (EXPERIMENTAL -- Armaly, Durst, Pereira & Schoenung, JFM 127
p.473, 1983; also Freitas, J. Fluids Eng. 117 p.208, 1995). Ansys Fluent's own
4.91 is CONTEXT ONLY and is never the gate.

CONTROLS (CLAUDE.md rules 3, 4, 5):
  * planted-zero  -- a known perturbation is planted into a COPY of the
                     wallShearStress file, read back FROM DISK, and the reader
                     REFUSES (exit 2) if it cannot see it.
  * strict completion -- see completion() ; the comparator REFUSES rather than
                     grading a partial run.
  * Roache triple -- LR/s across the three levels; anything not CONVERGING is
                     NOT A RESULT whatever the value.
  * OBSERVED-ORDER FLOOR (P_MIN, PRE-COMPUTE AMENDMENT 1) -- a triple whose
                     observed order p falls below P_MIN is NOT A RESULT and NO
                     GCI is printed. A near-1 error ratio is a STAGNANT family,
                     and ln(R)/ln(r) of it is a floating-point crumb that reads
                     as a valid, very small order. See
                     docs/ansys_verification/FINDING_p_floor.md sec.4. Driven by
                     a PLANTED CONTROL in the selftest AND in main().
  * CROSS-INSTRUMENT control -- LR is computed a SECOND, independent way (from the
                     sign change of near-wall streamwise velocity) and the two must
                     agree, else REFUSE. This exists because OpenFOAM's
                     wallShearStress sign convention is NOT self-evident (see
                     ORIENT below) and a silently inverted convention would place
                     the reattachment point inside the recirculation bubble.

Verdict vocabulary only: PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.
"""
import os, re, sys, json, math, shutil, tempfile

HERE     = os.path.dirname(os.path.abspath(__file__))
RUN_ROOT = os.path.join(HERE, "..", "..", "..",
                        "verification", "runs", "ansys_verification", "VMFL064")
LEVELS   = ["L1", "L2", "L3"]

S_STEP    = 0.0049          # step height, m (manual p.195)
REF_LRS   = 5.0             # target LR/s (EXPERIMENTAL)
TOL       = 0.10            # frozen band, relative; see PREREGISTRATION.md sec.5
ANSYS_LRS = 4.91            # context only, never the gate
PLANT     = 1.234e-03       # planted-zero perturbation, m2/s2
FS        = 1.25            # Roache safety factor
RATIO     = 2.0             # grid refinement ratio
# OBSERVED-ORDER FLOOR (PRE-COMPUTE AMENDMENT 1, 2026-08-26). An observed order
# below this is NOT A RESULT and NO GCI is quoted. FINDING_p_floor.md sec.4.
P_MIN     = 0.05

# OpenFOAM reports wallShearStress as -(nHat & devTau). On the y = 0 wall with the
# fluid above, the reported x-component therefore carries the OPPOSITE sign to the
# physical mu*du/dy. MEASURED on this very case, not assumed: in the recirculation
# bubble immediately behind the step the near-wall u_x is NEGATIVE while the
# reported wallShearStress.x is POSITIVE. ORIENT converts reported -> physical, and
# the cross-instrument control below REFUSES if this ever stops holding.
ORIENT = -1.0


# ----------------------------------------------------------------- readers ----
def _patch_block(text, patch):
    i = text.find("boundaryField")
    if i < 0:
        raise ValueError("no boundaryField")
    j = text.find(patch, i)
    if j < 0:
        raise ValueError("patch %s not found" % patch)
    k = text.find("{", j)
    depth, m = 0, k
    while m < len(text):
        if text[m] == "{":
            depth += 1
        elif text[m] == "}":
            depth -= 1
            if depth == 0:
                return text[k:m]
        m += 1
    raise ValueError("unterminated patch block")


def read_patch_scalar(path, patch):
    blk = _patch_block(open(path).read(), patch)
    m = re.search(r"nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\n?\s*\((.*?)\)\s*;", blk, re.S)
    if not m:
        raise ValueError("no nonuniform scalar list on %s in %s" % (patch, path))
    vals = [float(v) for v in m.group(2).split()]
    if len(vals) != int(m.group(1)):
        raise ValueError("scalar count mismatch")
    return vals


def read_patch_vector_x(path, patch):
    blk = _patch_block(open(path).read(), patch)
    m = re.search(r"nonuniform\s+List<vector>\s*\n?\s*(\d+)\s*\n?\s*\((.*)\)\s*;", blk, re.S)
    if not m:
        raise ValueError("no nonuniform vector list on %s in %s" % (patch, path))
    trip = re.findall(r"\(([^()]*)\)", m.group(2))
    if len(trip) != int(m.group(1)):
        raise ValueError("vector count mismatch: %d vs %d" % (len(trip), int(m.group(1))))
    return [float(t.split()[0]) for t in trip]


def read_internal_scalar(path):
    s = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\n?\s*\((.*?)\)\s*;", s, re.S)
    return [float(v) for v in m.group(2).split()]


def read_internal_vector_x(path):
    s = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<vector>\s*\n?\s*(\d+)\s*\n?\s*\((.*)\)\s*;", s, re.S)
    return [float(t.split()[0]) for t in re.findall(r"\(([^()]*)\)", m.group(2))]


# ------------------------------------------------------- the gate functional ---
def first_sign_change(xs, vals):
    """First crossing from reversed (negative) to forward (positive), linearly
    interpolated. Returns None if the profile never reverses or never recovers."""
    pairs = sorted(zip(xs, vals))
    xs = [p[0] for p in pairs]
    vs = [p[1] for p in pairs]
    if vs[0] >= 0.0:
        return None                      # no recirculation at all behind the step
    for i in range(1, len(vs)):
        if vs[i - 1] < 0.0 <= vs[i]:
            f = -vs[i - 1] / (vs[i] - vs[i - 1])
            return xs[i - 1] + f * (xs[i] - xs[i - 1])
    return None                          # reversed all the way to the outlet


def lr_from_wallshear(level_dir, t):
    tau_rep = read_patch_vector_x(os.path.join(level_dir, t, "wallShearStress"), "bottomWall")
    x       = read_patch_scalar(os.path.join(level_dir, t, "Cx"), "bottomWall")
    tau_phys = [ORIENT * v for v in tau_rep]
    return first_sign_change(x, tau_phys), x, tau_phys


def lr_from_nearwall_u(level_dir, t):
    """Independent instrument: the sign change of u_x in the first cell row above
    the wall. Different field, different discretisation, same physical event."""
    cx = read_internal_scalar(os.path.join(level_dir, t, "Cx"))
    cy = read_internal_scalar(os.path.join(level_dir, t, "Cy"))
    ux = read_internal_vector_x(os.path.join(level_dir, t, "U"))
    cand = [(cy[i], cx[i], ux[i]) for i in range(len(cx)) if cx[i] > 0.0]
    ymin = min(c[0] for c in cand)
    row  = [(c[1], c[2]) for c in cand if abs(c[0] - ymin) < 1e-12]
    return first_sign_change([r[0] for r in row], [r[1] for r in row])


# ------------------------------------------------------- planted-zero control --
def planted_zero(level_dir, t):
    """Plant a known perturbation into a COPY of the wallShearStress file, read it
    back FROM DISK, and prove the reader can see a non-zero before its zeros are
    believed (CLAUDE.md rule 3)."""
    src = os.path.join(level_dir, t, "wallShearStress")
    tmp = tempfile.mkdtemp(prefix="vmfl064_plant_")
    try:
        dst = os.path.join(tmp, "wallShearStress")
        shutil.copy(src, dst)
        base = read_patch_vector_x(dst, "bottomWall")
        txt  = open(dst).read()
        blk  = _patch_block(txt, "bottomWall")
        trip = re.findall(r"\(([^()]*)\)", blk)
        # perturb the FIRST face of the patch by a known amount
        old  = trip[0]
        parts = old.split()
        new  = "%.12g %s %s" % (float(parts[0]) + PLANT, parts[1], parts[2])
        newblk = blk.replace("(" + old + ")", "(" + new + ")", 1)
        open(dst, "w").write(txt.replace(blk, newblk, 1))
        seen = read_patch_vector_x(dst, "bottomWall")
        # SINGLE-POINT plant into a SINGLE-POINT reader (face 0 only) -- NOT an averaging
        # reader, so there is no 1/sqrt(N) dilution (L-340); the reader delta equals the plant.
        delta = seen[0] - base[0]
        ok = abs(delta - PLANT) < 1e-12
        # FALL-THROUGH REFUSAL (template Amendment 6a item 2): the only way this control
        # RETURNS is to have seen the plant. A blind reader REFUSES here, not merely in main.
        if not ok:
            raise SystemExit2("planted-zero control FAILED: planted %g into wallShearStress "
                              "bottomWall face 0, the reader moved by %g -- a reader not shown "
                              "able to see a non-zero cannot certify a zero (CLAUDE.md rule 3)"
                              % (PLANT, delta))
        return {"passed": True, "planted": PLANT, "reader_delta": delta,
                "file": "wallShearStress", "patch": "bottomWall"}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------- strict completion --
def completion(level_dir):
    """CLAUDE.md rule 4, adapted for a residualControl-terminated STEADY run and
    DECLARED THAT WAY IN THE FROZEN PRE-REGISTRATION (sec.6), not improvised here.

    For a steady SIMPLE solve the literal clause 'last time == endTime' would mean
    the solver ran out of clock WITHOUT converging -- the opposite of completion.
    The equivalent, and strictly stronger, clause is used instead:
        rc == 0
        an 'End' line in log.simpleFoam            (EXACT name -- never a log* glob,
                                                    which matches log.blockMesh first)
        'SIMPLE solution converged' present        (stopped on its own criterion)
        last Time  <  endTime                      (did NOT run out of clock)
        the declared fields present at that time
        ExecutionTime count == the iteration count
        age guard: fields newer than the case's own 0/U
    Any failed clause REFUSES (exit 2) rather than grading a partial run.
    """
    out = {}
    rcf = os.path.join(level_dir, "RUN_RC.txt")
    if not os.path.exists(rcf):
        raise SystemExit2("no RUN_RC.txt in %s -- rc is UNEVALUABLE from disk" % level_dir)
    rct = open(rcf).read()
    # Parse TOLERANTLY (template Amendment 5): the launcher writes `rc = 0` WITH spaces; a
    # reader requiring `rc=0` would find no match, fall back, and mis-grade a correct run.
    m = re.search(r"^\s*rc\s*=\s*(-?\d+)", rct, re.M)
    if not m:
        raise SystemExit2("RUN_RC.txt in %s has no rc= line" % level_dir)
    out["rc"] = int(m.group(1))
    if out["rc"] != 0:
        raise SystemExit2("rc=%d at %s (124 == the cap fired)" % (out["rc"], level_dir))

    log = os.path.join(level_dir, "log.simpleFoam")     # EXACT name, never a glob
    if not os.path.exists(log):
        raise SystemExit2("no log.simpleFoam in %s" % level_dir)
    lt = open(log).read()
    out["end_line"] = lt.count("\nEnd")
    if out["end_line"] < 1:
        raise SystemExit2("no End line in %s/log.simpleFoam" % level_dir)
    out["converged"] = ("SIMPLE solution converged" in lt)
    if not out["converged"]:
        raise SystemExit2("%s did not report SIMPLE convergence" % level_dir)

    times = [int(t) for t in re.findall(r"^Time = (\d+)", lt, re.M)]
    out["last_time"] = times[-1]
    out["n_exec"] = lt.count("ExecutionTime")
    if out["n_exec"] != out["last_time"]:
        raise SystemExit2("%s ExecutionTime count %d != last time %d"
                          % (level_dir, out["n_exec"], out["last_time"]))

    ctl = open(os.path.join(level_dir, "system", "controlDict")).read()
    out["endTime"] = float(re.search(r"^endTime\s+([0-9.eE+-]+)\s*;", ctl, re.M).group(1))
    if not (out["last_time"] < out["endTime"]):
        raise SystemExit2("%s reached endTime %g -- ran out of clock, did NOT converge"
                          % (level_dir, out["endTime"]))

    t = str(out["last_time"])
    out["time_dir"] = t
    for f in ("U", "p", "wallShearStress", "Cx", "Cy"):
        if not os.path.exists(os.path.join(level_dir, t, f)):
            raise SystemExit2("field %s missing at %s/%s" % (f, level_dir, t))
    z = os.path.getmtime(os.path.join(level_dir, "0", "U"))
    for f in ("U", "wallShearStress"):
        if not os.path.getmtime(os.path.join(level_dir, t, f)) > z:
            raise SystemExit2("AGE GUARD: %s/%s/%s is not newer than 0/U" % (level_dir, t, f))
    out["age_guard"] = "fields newer than 0/U"
    return out


class SystemExit2(SystemExit):
    def __init__(self, msg):
        sys.stderr.write("REFUSED (exit 2): %s\n" % msg)
        SystemExit.__init__(self, 2)


# ------------------------------------------------------------ Roache triple ----
def roache(f1, f2, f3, r=RATIO, fs=FS):
    """f1 coarse, f2 medium, f3 fine."""
    d32 = f3 - f2
    d21 = f2 - f1
    out = {"f_coarse": f1, "f_med": f2, "f_fine": f3, "ratio": r, "fs": fs,
           "d21": d21, "d32": d32}
    if d21 == 0.0 and d32 == 0.0:
        out["state"] = "EXACT"; out["p"] = None; out["gci_fine"] = None; return out
    if d21 == 0.0 or d32 == 0.0:
        out["state"] = "STAGNANT"; out["p"] = None; out["gci_fine"] = None; return out
    R = d32 / d21
    out["R"] = R
    if R < 0.0:
        out["state"] = "OSCILLATORY"; out["p"] = None; out["gci_fine"] = None; return out
    if R >= 1.0:
        out["state"] = "DIVERGENT"; out["p"] = None; out["gci_fine"] = None; return out
    p = math.log(abs(d21 / d32)) / math.log(r)
    out["p"] = p
    # OBSERVED-ORDER FLOOR (PRE-COMPUTE AMENDMENT 1). R = d32/d21 near 1 is a
    # STAGNANT family; ln(R)/ln(r) of it is a floating-point crumb that reads as a
    # valid, very small observed order, and a GCI computed from it is a number
    # with no meaning. Below the floor the triple is NOT A RESULT and NO GCI is
    # produced. FINDING_p_floor.md sec.4.
    if p < P_MIN:
        out["state"] = "STAGNANT"
        out["p_floor"] = P_MIN
        out["p_below_floor"] = True
        out["gci_fine"] = None
        out["f_extrapolated"] = None
        return out
    out["state"] = "CONVERGING"
    out["f_extrapolated"] = f3 + d32 / (r ** p - 1.0)
    out["gci_fine"] = fs * abs(d32 / f3) / (r ** p - 1.0)
    return out


# ------------------------------------------------- verdict (one path, shared) --
def verdict_for(tri, inside):
    """The ONE verdict path. main() grades through it and the planted p-floor
    control below DRIVES it, so the control exercises the code that actually
    decides, not a paraphrase of it. Vocabulary is fixed (CLAUDE.md rule 1)."""
    if tri["state"] != "CONVERGING":
        if tri.get("p_below_floor"):
            return ("NOT A RESULT",
                    "observed order p = %.6g is below the frozen floor P_MIN = %.3g; the "
                    "triple is %s and NO GCI is quoted (FINDING_p_floor.md sec.4)"
                    % (tri["p"], P_MIN, tri["state"]))
        return ("NOT A RESULT",
                "grid triple is %s, not CONVERGING (CLAUDE.md rule 5 step 2) -- "
                "NOT A RESULT whatever the value" % tri["state"])
    if inside:
        return ("GATE REACHED",
                "LR/s within %.3g of the experimental reference, triple CONVERGING. "
                "Ceiling is GATE REACHED, not PASS: see PREREGISTRATION.md sec.9." % TOL)
    return ("GATE FAIL", "LR/s outside the frozen %.3g band" % TOL)


# ------------------------------------- PLANTED CONTROL for the p-floor (rule 3 form) --
def p_floor_control():
    """PLANTED CONTROL for the observed-order floor (PRE-COMPUTE AMENDMENT 1).

    A floor nobody tests is a floor nobody has (FINDING_p_floor.md sec.4). This
    control PLANTS three constructed triples into the comparator's OWN roache()
    and OWN verdict_for(), and REFUSES (exit 2) if any is graded the wrong way:

      (a) the equally spaced triple (1.0, 1.1, 1.2) -- d21 == d32 exactly, R = 1,
          a family that is not converging at all. It must grade NOT A RESULT with
          NO GCI, EVEN THOUGH the fine value would sit inside the band.
      (b) a triple whose observed order is genuinely COMPUTED and lands below the
          floor (p = 0.01). This is the probe that drives the floor itself, since
          (a) is caught one step earlier by the ratio test -- a control that only
          fed (a) would leave the floor untested.
      (c) a triple with p = 0.5, comfortably ABOVE the floor: the floor must NOT
          fire, and a GCI MUST be produced. A floor that swallows real results is
          as bad as no floor.

    NO `assert` ANYWHERE: `python3 -O` strips asserts, so every branch below
    refuses with SystemExit2 (PREREGISTRATION.md sec.11).
    """
    def refuse(tag, detail):
        raise SystemExit2("P-FLOOR PLANTED CONTROL FAILED [%s]: %s (P_MIN = %.3g, "
                          "FINDING_p_floor.md sec.4)" % (tag, detail, P_MIN))

    out = {"P_MIN": P_MIN, "probes": {}}

    # (a) equally spaced -- the exact probe named in FINDING_p_floor.md sec.2
    tri_a = roache(1.0, 1.1, 1.2)
    v_a, _ = verdict_for(tri_a, True)
    out["probes"]["equally_spaced_1.0_1.1_1.2"] = {
        "state": tri_a["state"], "p": tri_a.get("p"), "gci_fine": tri_a.get("gci_fine"),
        "verdict": v_a}
    if v_a != "NOT A RESULT":
        refuse("equally-spaced (1.0, 1.1, 1.2)",
               "graded %r, expected NOT A RESULT; state %s" % (v_a, tri_a["state"]))
    if tri_a.get("gci_fine") is not None:
        refuse("equally-spaced (1.0, 1.1, 1.2)",
               "a GCI was produced (%r) for a non-converging triple" % (tri_a["gci_fine"],))
    if tri_a["state"] == "CONVERGING":
        refuse("equally-spaced (1.0, 1.1, 1.2)",
               "classified CONVERGING with p = %r -- the defect this floor exists for"
               % (tri_a.get("p"),))

    # (b) p genuinely computed and BELOW the floor: d32/d21 = r**-0.01 -> p = 0.01
    p_lo = 0.01
    tri_b = roache(1.0, 1.1, 1.1 + 0.1 * (RATIO ** (-p_lo)))
    v_b, _ = verdict_for(tri_b, True)
    out["probes"]["below_floor_p_0.01"] = {
        "state": tri_b["state"], "p": tri_b.get("p"), "gci_fine": tri_b.get("gci_fine"),
        "verdict": v_b}
    if tri_b.get("p") is None or abs(tri_b["p"] - p_lo) > 1e-9:
        refuse("below-floor probe", "constructed p = %.4g was not recovered (got %r)"
               % (p_lo, tri_b.get("p")))
    if not tri_b.get("p_below_floor"):
        refuse("below-floor probe", "p = %r is under P_MIN and the floor did NOT fire"
               % (tri_b.get("p"),))
    if v_b != "NOT A RESULT":
        refuse("below-floor probe", "graded %r, expected NOT A RESULT" % (v_b,))
    if tri_b.get("gci_fine") is not None:
        refuse("below-floor probe", "a GCI was produced (%r) below the floor"
               % (tri_b["gci_fine"],))

    # (c) p ABOVE the floor: the floor must not over-fire, and a GCI must exist.
    p_hi = 0.5
    tri_c = roache(1.0, 1.1, 1.1 + 0.1 * (RATIO ** (-p_hi)))
    v_c, _ = verdict_for(tri_c, True)
    out["probes"]["above_floor_p_0.5"] = {
        "state": tri_c["state"], "p": tri_c.get("p"), "gci_fine": tri_c.get("gci_fine"),
        "verdict": v_c}
    if tri_c["state"] != "CONVERGING" or tri_c.get("p_below_floor"):
        refuse("above-floor probe", "p = %r is above P_MIN and the floor fired anyway"
               % (tri_c.get("p"),))
    if tri_c.get("gci_fine") is None:
        refuse("above-floor probe", "no GCI for a converging triple above the floor")
    if v_c != "GATE REACHED":
        refuse("above-floor probe", "graded %r, expected GATE REACHED inside the band"
               % (v_c,))

    out["passed"] = True
    return out


# ------------------------------------------------------------------- selftest --
def selftest():
    ok = True
    def chk(c, name, got=""):
        nonlocal ok
        print("  [%s] %s  %s" % ("PASS" if c else "FAIL", name, got))
        ok = ok and c

    print("--- selftest: sign-change locator ---")
    chk(abs(first_sign_change([0, 1, 2, 3], [-2, -1, 1, 2]) - 1.5) < 1e-12,
        "linear interpolation of the crossing", first_sign_change([0,1,2,3],[-2,-1,1,2]))
    chk(first_sign_change([0, 1, 2], [1, 2, 3]) is None, "no recirculation -> None")
    chk(first_sign_change([0, 1, 2], [-1, -2, -3]) is None, "never recovers -> None")

    print("--- selftest: Roache classifier ---")
    chk(roache(1.0, 1.5, 1.75)["state"] == "CONVERGING", "first-order -> CONVERGING")
    chk(abs(roache(1.0, 1.5, 1.75)["p"] - 1.0) < 1e-9, "p == 1", roache(1.0,1.5,1.75)["p"])
    chk(roache(1.0, 1.25, 1.3125)["state"] == "CONVERGING", "second-order family")
    chk(abs(roache(1.0, 1.25, 1.3125)["p"] - 2.0) < 1e-9, "p == 2")
    chk(roache(1.0, 2.0, 4.0)["state"] == "DIVERGENT", "divergent -> DIVERGENT")
    chk(roache(1.0, 2.0, 1.5)["state"] == "OSCILLATORY", "oscillatory -> OSCILLATORY")
    chk(roache(2.0, 2.0, 2.0)["state"] == "EXACT", "identical -> EXACT")

    print("--- selftest: PLANTED CONTROL -- the observed-order floor P_MIN = %.3g ---" % P_MIN)
    # The control REFUSES (SystemExit2) on failure, so reaching the next line at all is
    # the evidence; the chk() below records the three probes it drove.
    pf = p_floor_control()
    chk(pf["passed"] and pf["probes"]["equally_spaced_1.0_1.1_1.2"]["verdict"] == "NOT A RESULT",
        "(1.0, 1.1, 1.2) -> NOT A RESULT, no GCI",
        "%s / gci=%r" % (pf["probes"]["equally_spaced_1.0_1.1_1.2"]["state"],
                         pf["probes"]["equally_spaced_1.0_1.1_1.2"]["gci_fine"]))
    chk(pf["probes"]["below_floor_p_0.01"]["verdict"] == "NOT A RESULT"
        and pf["probes"]["below_floor_p_0.01"]["gci_fine"] is None,
        "p = 0.01 (below floor) -> NOT A RESULT, no GCI",
        "p=%.4g" % pf["probes"]["below_floor_p_0.01"]["p"])
    chk(pf["probes"]["above_floor_p_0.5"]["verdict"] == "GATE REACHED"
        and pf["probes"]["above_floor_p_0.5"]["gci_fine"] is not None,
        "p = 0.5 (above floor) -> floor does NOT over-fire, GCI quoted",
        "p=%.4g" % pf["probes"]["above_floor_p_0.5"]["p"])

    print("--- selftest: the gate can FAIL and can PASS ---")
    chk(abs(5.0 - REF_LRS) / REF_LRS <= TOL, "exact reference is inside band")
    chk(abs(5.4 - REF_LRS) / REF_LRS <= TOL, "+8% is inside band")
    chk(not (abs(5.7 - REF_LRS) / REF_LRS <= TOL), "+14% is OUTSIDE band")
    chk(not (abs(4.2 - REF_LRS) / REF_LRS <= TOL), "-16% is OUTSIDE band")

    print("--- selftest: ORIENT is applied, not assumed away ---")
    chk(ORIENT == -1.0, "reported wallShearStress.x is inverted to physical")

    # ---- control coverage: the extraction and the controls are DRIVEN, not just described.
    # A mutation test breaks each control and confirms THIS selftest then fails (Amendment 6a).
    def _wss(patch, trips):
        body = "\n".join("(%.10g %.10g %.10g)" % t for t in trips)
        return ("FoamFile { version 2.0; format ascii; class volVectorField; object wallShearStress; }\n"
                "dimensions [0 2 -2 0 0 0 0];\ninternalField uniform (0 0 0);\n"
                "boundaryField {\n    %s { type calculated; value nonuniform List<vector> %d (\n%s\n); }\n}\n"
                % (patch, len(trips), body))
    def _cx(xs):
        vv = " ".join("%.10g" % v for v in xs)
        return ("FoamFile { version 2.0; format ascii; class volScalarField; object Cx; }\n"
                "dimensions [0 1 0 0 0 0 0];\ninternalField nonuniform List<scalar> %d ( %s );\n"
                "boundaryField {\n    bottomWall { type calculated; value nonuniform List<scalar> %d ( %s ); }\n}\n"
                % (len(xs), vv, len(xs), vv))
    def _cy(vals):
        return ("FoamFile { version 2.0; format ascii; class volScalarField; object Cy; }\n"
                "dimensions [0 1 0 0 0 0 0];\ninternalField nonuniform List<scalar> %d ( %s );\nboundaryField { }\n"
                % (len(vals), " ".join("%.10g" % v for v in vals)))
    def _u(trips):
        body = "\n".join("(%.10g %.10g %.10g)" % t for t in trips)
        return ("FoamFile { version 2.0; format ascii; class volVectorField; object U; }\n"
                "dimensions [0 1 -1 0 0 0 0];\ninternalField nonuniform List<vector> %d (\n%s\n);\nboundaryField { }\n"
                % (len(trips), body))
    def build_field(td, x_star, n=51):
        os.makedirs(td, exist_ok=True)
        xs = [(i + 0.5) * 0.1 / n for i in range(n)]
        # tau_phys = x - x_star; grader applies ORIENT=-1, so write tau_rep = x_star - x.
        open(os.path.join(td, "wallShearStress"), "w").write(_wss("bottomWall", [(x_star - x, 0.0, 0.0) for x in xs]))
        open(os.path.join(td, "Cx"), "w").write(_cx(xs))
        open(os.path.join(td, "Cy"), "w").write(_cy([1e-4] * n))
        open(os.path.join(td, "U"), "w").write(_u([(x - x_star, 0.0, 0.0) for x in xs]))
        return xs

    print("--- selftest: LR extraction on a CONSTRUCTED field whose answer is known ---")
    d = tempfile.mkdtemp(prefix="st064_")
    try:
        # x_star deliberately != 5.0*s, so a reader that returned the target would be caught.
        x_star = 6.0 * S_STEP
        build_field(os.path.join(d, "L1", "1000"), x_star)
        lr_tau, xs, taus = lr_from_wallshear(os.path.join(d, "L1"), "1000")
        lr_u = lr_from_nearwall_u(os.path.join(d, "L1"), "1000")
        dx = xs[1] - xs[0]
        chk(abs(lr_tau - x_star) < dx, "wall-shear LR == constructed x_star (LR/s=%.3f)" % (lr_tau / S_STEP), lr_tau)
        chk(abs(lr_u - x_star) < dx, "near-wall-u LR == constructed x_star", lr_u)
        chk(abs(lr_tau - lr_u) < 1e-9, "cross-instrument agreement is exact on the construction")
        # planted-zero SEES a plant (returns passed); a BLIND reader REFUSES (raises).
        pz = planted_zero(os.path.join(d, "L1"), "1000")
        chk(pz["passed"] and abs(pz["reader_delta"] - PLANT) < 1e-12, "planted-zero sees the plant (no dilution)")
        import builtins as _b
        global read_patch_vector_x
        _orig = read_patch_vector_x
        try:
            read_patch_vector_x = lambda p, patch: [0.0] * 51   # blind reader
            blind_refused = False
            try:
                planted_zero(os.path.join(d, "L1"), "1000")
            except SystemExit as ex:
                blind_refused = (ex.code == 2)
            chk(blind_refused, "planted-zero REFUSES (exit 2) a reader that cannot see the plant")
        finally:
            read_patch_vector_x = _orig
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("--- selftest: strict completion accepts a good run and REFUSES a bad rc ---")
    d = tempfile.mkdtemp(prefix="stc064_")
    try:
        def make_level(ld, rc, converged=True, endtime=5000, last=200):
            os.makedirs(os.path.join(ld, "system"), exist_ok=True)
            os.makedirs(os.path.join(ld, "0"), exist_ok=True)
            os.makedirs(os.path.join(ld, str(last)), exist_ok=True)
            open(os.path.join(ld, "RUN_RC.txt"), "w").write("rc = %d\nlevel = X\n" % rc)  # SPACES (Amendment 5)
            body = "".join("Time = %d\nExecutionTime = %d s\n" % (i, i) for i in range(1, last + 1))
            body += ("SIMPLE solution converged in %d iterations\n" % last if converged else "")
            body += "\nEnd\n"
            open(os.path.join(ld, "log.simpleFoam"), "w").write(body)
            open(os.path.join(ld, "system", "controlDict"), "w").write("endTime %d;\n" % endtime)
            build_field(os.path.join(ld, str(last)), 6.0 * S_STEP)  # writes U,Cx,Cy,wallShearStress
            open(os.path.join(ld, str(last), "p"), "w").write("p\n")
            zt = os.path.getmtime(os.path.join(ld, str(last), "U")) - 10
            open(os.path.join(ld, "0", "U"), "w").write("U0\n")
            os.utime(os.path.join(ld, "0", "U"), (zt, zt))
        good = os.path.join(d, "good"); make_level(good, 0)
        c = completion(good)
        chk(c["rc"] == 0 and c["converged"] and c["last_time"] == 200,
            "completion parses `rc = 0` (spaces) and accepts a converged run")
        bad = os.path.join(d, "bad"); make_level(bad, 1)
        refused = False
        try:
            completion(bad)
        except SystemExit as ex:
            refused = (ex.code == 2)
        chk(refused, "completion REFUSES (exit 2) rc != 0")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("\nSELFTEST: %s" % ("all checks passed" if ok else "FAILURES PRESENT"))
    return 0 if ok else 1


# ----------------------------------------------------------------------- main --
def main():
    root = os.path.normpath(RUN_ROOT)
    res = {"case": "VMFL064", "manual_page": "195/196",
           "reference": REF_LRS, "reference_kind": "EXPERIMENTAL (Armaly et al. 1983)",
           "ansys_context_only": ANSYS_LRS, "tol": TOL, "s_step": S_STEP,
           "comparator": os.path.abspath(__file__),
           "completion": {}, "levels": {}, "planted_zero": None}

    print("=" * 78)
    print("VMFL064 -- Low Re flow in a channel with sudden asymmetric expansion")
    print("Ansys FD Verification Manual 2026 R1, p. 195/196")
    print("reference: LR/s = %.4g  (EXPERIMENTAL -- Armaly, Durst, Pereira &" % REF_LRS)
    print("           Schoenung, JFM 127:473, 1983).  Ansys Fluent %.4g = CONTEXT ONLY" % ANSYS_LRS)
    print("=" * 78)

    # PLANTED CONTROL for the observed-order floor, driven on the FROZEN grading path
    # itself, before any level is read. It REFUSES (exit 2) rather than grading.
    res["p_floor_control"] = p_floor_control()
    print("p-floor planted control OK (P_MIN = %.3g): (1.0,1.1,1.2) -> %s, no GCI"
          % (P_MIN, res["p_floor_control"]["probes"]["equally_spaced_1.0_1.1_1.2"]["verdict"]))

    lrs = []
    for lv in LEVELS:
        d = os.path.join(root, lv)
        c = completion(d)
        res["completion"][lv] = c
        t = c["time_dir"]
        lr_tau, xs, taus = lr_from_wallshear(d, t)
        if lr_tau is None:
            raise SystemExit2("%s: wall shear never changes sign -- no reattachment found" % lv)
        lr_u = lr_from_nearwall_u(d, t)
        if lr_u is None:
            raise SystemExit2("%s: near-wall u_x never changes sign" % lv)
        dx = (xs[1] - xs[0]) if len(xs) > 1 else 0.0
        agree = abs(lr_tau - lr_u)
        if agree > 3.0 * dx:
            raise SystemExit2(
                "%s: CROSS-INSTRUMENT CONTROL FAILED -- wall-shear LR %.6f vs "
                "near-wall-u LR %.6f differ by %.6f > 3 cell widths (%.6f). The "
                "wallShearStress sign convention may have changed." % (lv, lr_tau, lr_u, agree, 3.0 * dx))
        res["levels"][lv] = {"LR_m": lr_tau, "LR_over_s": lr_tau / S_STEP,
                             "LR_crosscheck_m": lr_u, "crosscheck_delta_m": agree,
                             "cell_dx_m": dx, "time_dir": t, "n_wall_faces": len(xs)}
        lrs.append(lr_tau / S_STEP)
        print("  %-3s  LR/s = %.6f   (LR = %.6f m; cross-check %.6f m, delta %.2e, dx %.2e)"
              % (lv, lr_tau / S_STEP, lr_tau, lr_u, agree, dx))

    res["planted_zero"] = planted_zero(os.path.join(root, LEVELS[-1]),
                                       res["completion"][LEVELS[-1]]["time_dir"])
    print("\nplanted-zero control on %s: %s" % (LEVELS[-1], json.dumps(res["planted_zero"])))
    if not res["planted_zero"]["passed"]:
        raise SystemExit2("planted-zero control did NOT fire -- the reader is not shown able "
                          "to see a non-zero, so its numbers are not evidence")

    tri = roache(lrs[0], lrs[1], lrs[2])
    res["triple"] = tri
    fine = lrs[-1]
    res["lab_value"] = fine
    rel = abs(fine - REF_LRS) / abs(REF_LRS)
    res["rel_dev"] = rel
    inside = rel <= TOL

    print("\n--- Roache triple on LR/s (r = %.1f) ---" % RATIO)
    print("  %.6f / %.6f / %.6f  -> %s" % (lrs[0], lrs[1], lrs[2], tri["state"]))
    if tri["state"] == "CONVERGING":
        print("  observed order p = %.4f   GCI_fine (Fs = %.2f) = %.4f %%"
              % (tri["p"], FS, 100.0 * tri["gci_fine"]))
    elif tri.get("p_below_floor"):
        print("  observed order p = %.6g is BELOW the frozen floor P_MIN = %.3g -- the triple "
              "is reported\n  %s and NO GCI is quoted (FINDING_p_floor.md sec.4)."
              % (tri["p"], P_MIN, tri["state"]))
    else:
        print("  observed order: undefined for a %s triple; NO GCI is quoted." % tri["state"])

    print("\n--- gate: |LR/s - %.4g| / %.4g <= %.3g ---" % (REF_LRS, REF_LRS, TOL))
    print("  lab LR/s = %.6f   reference %.4g   rel dev %.4f %%   %s"
          % (fine, REF_LRS, 100.0 * rel, "inside band" if inside else "OUTSIDE band"))

    verdict, why = verdict_for(tri, inside)

    res["verdict"] = verdict
    res["why"] = why
    print("\nVERDICT: %s -- %s" % (verdict, why))

    out = os.path.join(root, "GRADING_VMFL064.json")
    with open(out, "w") as fh:
        json.dump(res, fh, indent=2, sort_keys=True)
    print("grading written to %s" % out)
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
