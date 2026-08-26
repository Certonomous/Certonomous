#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMFL064-R2 -- Low Reynolds Number Flow in a Channel with Sudden Asymmetric Expansion.
Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p. 195/196.
RE-REGISTRATION of VMFL064 (attempt 1, register row #29, NOT A RESULT) under
ANSYS_VERIFICATION_CHARTER sec.6: a NEW row that cites the old one and never
overwrites it.

WHAT CHANGED FROM ATTEMPT 1 -- THE READER, AND ONLY THE READER.
  attempt 1  grade_vmfl064.py  blob 0be9126cd6a3e3c860b98854a4e21ba1102edfdc
             first_sign_change(): returns None when the profile does not START
             negative, and main() REFUSES on None. On L3 the profile starts
             POSITIVE -- the finest mesh resolves a secondary counter-rotating
             CORNER VORTEX at the foot of the step -- so the frozen reader
             refused: "L3: wall shear never changes sign -- no reattachment
             found" (verification/runs/ansys_verification/VMFL064/
             GRADING_ATTEMPT_REFUSED.txt).
  R2 (here)  the PRIMARY reattachment is the LAST negative-to-positive sign
             change of the PHYSICAL bottom-wall shear inside the REGISTERED
             SEARCH WINDOW X_WIN_LO < x <= X_WIN_HI. A corner vortex adds sign
             changes UPSTREAM of the primary reattachment, never downstream of
             it, so the last crossing in the window is the primary one whether or
             not the corner eddy is resolved.

WHAT DID NOT CHANGE -- byte-identical to attempt 1 and cited by blob sha in
PREREGISTRATION.md sec."WHAT IS BYTE-IDENTICAL": the gate quantity (LR/s on
bottomWall), the reference (5.0, EXPERIMENTAL), the band (TOL = 0.10), the tier
ceiling (GATE REACHED), the mesh family (blockMeshDict.template blob
27cc03896bdd747279264b8051bec76179bfb516, L1/L2/L3 at r = 2), the cap (90
core-min running total), ORIENT, PLANT, FS, RATIO, P_MIN, and the Roache
classifier + verdict path.

CONTROLS (CLAUDE.md rules 3, 4, 5; L-332, L-340, L-342; FINDING_p_floor.md):
  * CORNER-VORTEX PLANTED CONTROL -- the control that DRIVES this repair. A
                     profile carrying a secondary corner vortex is CONSTRUCTED on
                     disk with a KNOWN primary reattachment x_star; the R2 reader
                     must return x_star, and the ATTEMPT-1 LOGIC run on the SAME
                     bytes must REFUSE. A fix nobody drives is a fix nobody has.
  * planted-zero  -- a known perturbation is planted into a COPY of the
                     wallShearStress file, read back FROM DISK, and the reader
                     REFUSES (exit 2) if it cannot see it. SINGLE-POINT plant into
                     a SINGLE-POINT reader, so no 1/sqrt(N) dilution (L-340).
  * strict completion with L-342 FIELD CLASSES -- physics-critical fields gate;
                     ABSENT infrastructure fields print NOT MEASURED and the grade
                     PROCEEDS. A dead poller can never void a run again.
  * Roache triple -- LR/s across the three levels; anything not CONVERGING is
                     NOT A RESULT whatever the value.
  * OBSERVED-ORDER FLOOR P_MIN = 0.05 with its own PLANTED CONTROL, driven in
                     --selftest AND in main() before any level is read.
  * CROSS-INSTRUMENT control -- LR is computed a SECOND, independent way (near-wall
                     streamwise velocity, same window, same last-crossing rule) and
                     the two must agree within 3 cell widths, else REFUSE.

NO `assert` ANYWHERE. `python3 -O` deletes every assert (L-332), so a refusal
written as one is a refusal OFFER the runner accepts or declines by a flag.
Every refusal here is SystemExit2 / sys.exit(2). `--selftest` is IDENTICAL under
`python3` and `python3 -O`.

Verdict vocabulary only: PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.
"""
import os, re, sys, json, math, shutil, tempfile

HERE     = os.path.dirname(os.path.abspath(__file__))
RUN_ROOT = os.path.join(HERE, "..", "..", "..",
                        "verification", "runs", "ansys_verification", "VMFL064-R2")
LEVELS   = ["L1", "L2", "L3"]

# --- BYTE-IDENTICAL to attempt 1 (blob 0be9126cd6a3e3c860b98854a4e21ba1102edfdc) ---
S_STEP    = 0.0049          # step height, m (manual p.195)
REF_LRS   = 5.0             # target LR/s (EXPERIMENTAL)
TOL       = 0.10            # frozen band, relative; UNCHANGED from attempt 1
ANSYS_LRS = 4.91            # context only, never the gate
PLANT     = 1.234e-03       # planted-zero perturbation, m2/s2
FS        = 1.25            # Roache safety factor
RATIO     = 2.0             # grid refinement ratio
P_MIN     = 0.05            # observed-order floor; FINDING_p_floor.md sec.4
ORIENT    = -1.0            # reported wallShearStress.x -> physical mu*du/dy

# --- NEW IN R2, AND THE ONLY NEW GATE-PATH CONSTANTS -------------------------
# THE REGISTERED SEARCH WINDOW for the primary reattachment, in metres from the
# step foot (x = 0). Frozen in PREREGISTRATION.md sec.5 BEFORE any R2 compute.
#   lower  0.0  -- the step foot itself; the window is OPEN at the lower end, so
#                  a crossing exactly at x = 0 is not a reattachment.
#   upper  0.05 m = 10.204 * s -- TWICE the experimental target (5*s = 0.0245 m)
#                  and HALF the 0.1 m downstream channel, so the window cannot be
#                  read as tuned to an answer (it spans double the reference) and
#                  cannot admit an outlet artefact (it stops 0.05 m short of the
#                  outlet). Justified a priori, never from a run.
X_WIN_LO = 0.0
X_WIN_HI = 0.05

# --- L-342 FIELD CLASSES (Sanaa 2026-08-26): "a bookkeeping failure invalidates
# the bookkeeping, never the physics artefacts". The gate reads PHYSICS-CRITICAL
# fields only. An ABSENT infrastructure field is reported NOT MEASURED, disclosed
# in the grading record, and the grade PROCEEDS. An infrastructure field that is
# PRESENT AND BAD (e.g. a recorded rc != 0) is still evidence of a failed solve
# and still REFUSES -- absence is not a licence, it is a disclosure.
FIELD_CLASSES = {
    "physics_critical": [
        "log.simpleFoam (End line, exact name -- never a log* glob)",
        "log.simpleFoam 'SIMPLE solution converged'",
        "log.simpleFoam Time / ExecutionTime counts",
        "system/controlDict endTime",
        "<t>/U, <t>/p, <t>/wallShearStress, <t>/Cx, <t>/Cy",
        "0/U (the age-guard datum)",
    ],
    "infrastructure": [
        "RUN_RC.<level> rc / wall_s / core_min / timeout_s (launcher bookkeeping)",
        "COST.txt (run-root cost roll-up)",
    ],
}


class SystemExit2(SystemExit):
    def __init__(self, msg):
        sys.stderr.write("REFUSED (exit 2): %s\n" % msg)
        SystemExit.__init__(self, 2)


# ----------------------------------------------------------------- readers ----
# Byte-identical to attempt 1; the R2 change is the SIGN-CHANGE LOCATOR below,
# not the file parsing.
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


# ------------------------------------------- THE ATTEMPT-1 LOCATOR, PRESERVED --
def legacy_first_sign_change(xs, vals):
    """THE ATTEMPT-1 LOGIC, kept VERBATIM (blob 0be9126c..., function
    `first_sign_change`) for ONE purpose: so the corner-vortex planted control can
    run it on the SAME constructed bytes and show that it REFUSES where the R2
    reader returns the primary length. It is NEVER on the R2 grading path.

    First crossing from reversed (negative) to forward (positive), linearly
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


def legacy_grade_path(xs, vals, tag="L3"):
    """The attempt-1 MAIN-PATH behaviour reproduced exactly: locate, and REFUSE
    (exit 2) on None. The control below drives THIS, not a paraphrase of it, so
    the refusal it demonstrates is the refusal that actually happened."""
    lr = legacy_first_sign_change(xs, vals)
    if lr is None:
        raise SystemExit2("%s: wall shear never changes sign -- no reattachment found" % tag)
    return lr


# ------------------------------------------------- THE R2 GATE FUNCTIONAL ------
def last_sign_change_in_window(xs, vals, x_lo=X_WIN_LO, x_hi=X_WIN_HI):
    """THE R2 READER. The PRIMARY reattachment is the LAST negative-to-positive
    crossing of the physical wall shear inside the registered window
    x_lo < x <= x_hi, linearly interpolated between the bracketing samples.

    WHY THE LAST, NOT THE FIRST. A secondary counter-rotating corner vortex sits
    at the FOOT of the step, INSIDE the primary bubble, and is resolved only on a
    fine enough mesh. It adds crossings UPSTREAM of the primary reattachment and
    it flips the sign the profile STARTS with -- which is exactly what voided
    attempt 1. It can never add a crossing DOWNSTREAM of the primary reattachment,
    because downstream of reattachment the near-wall flow is attached and forward.
    So the last negative-to-positive crossing in the window is the primary
    reattachment WHETHER OR NOT the corner eddy is resolved -- the same number on
    a coarse mesh that never sees the eddy and on a fine mesh that does.

    WHY A WINDOW. Without an upper bound, an outlet-region artefact would be
    'the last crossing'. X_WIN_HI is frozen at 0.05 m = 10.2*s, twice the
    reference and half the downstream channel (PREREGISTRATION.md sec.5).

    Returns None if there is NO negative-to-positive crossing in the window; the
    caller REFUSES on None rather than degrading."""
    pairs = sorted(zip(xs, vals))
    win = [p for p in pairs if x_lo < p[0] <= x_hi]
    if len(win) < 2:
        return None
    xw = [p[0] for p in win]
    vw = [p[1] for p in win]
    found = None
    for i in range(1, len(vw)):
        if vw[i - 1] < 0.0 <= vw[i]:
            f = -vw[i - 1] / (vw[i] - vw[i - 1])
            found = xw[i - 1] + f * (xw[i] - xw[i - 1])
    return found


def count_sign_changes_in_window(xs, vals, x_lo=X_WIN_LO, x_hi=X_WIN_HI):
    """Diagnostic ONLY -- reported beside every level so the corner vortex is
    VISIBLE in the record (2 crossings = the eddy is resolved, 1 = it is not).
    It gates nothing."""
    pairs = sorted(zip(xs, vals))
    win = [p for p in pairs if x_lo < p[0] <= x_hi]
    vw = [p[1] for p in win]
    neg_pos = sum(1 for i in range(1, len(vw)) if vw[i - 1] < 0.0 <= vw[i])
    pos_neg = sum(1 for i in range(1, len(vw)) if vw[i - 1] >= 0.0 > vw[i])
    return {"neg_to_pos": neg_pos, "pos_to_neg": pos_neg,
            "starts_positive": bool(vw and vw[0] >= 0.0)}


def wallshear_profile(level_dir, t):
    """Physical bottom-wall shear profile (x, tau_phys) at time t."""
    tau_rep = read_patch_vector_x(os.path.join(level_dir, t, "wallShearStress"), "bottomWall")
    x       = read_patch_scalar(os.path.join(level_dir, t, "Cx"), "bottomWall")
    return x, [ORIENT * v for v in tau_rep]


def lr_from_wallshear(level_dir, t):
    x, tau_phys = wallshear_profile(level_dir, t)
    return last_sign_change_in_window(x, tau_phys), x, tau_phys


def nearwall_u_profile(level_dir, t):
    cx = read_internal_scalar(os.path.join(level_dir, t, "Cx"))
    cy = read_internal_scalar(os.path.join(level_dir, t, "Cy"))
    ux = read_internal_vector_x(os.path.join(level_dir, t, "U"))
    cand = [(cy[i], cx[i], ux[i]) for i in range(len(cx)) if cx[i] > 0.0]
    ymin = min(c[0] for c in cand)
    row  = [(c[1], c[2]) for c in cand if abs(c[0] - ymin) < 1e-12]
    return [r[0] for r in row], [r[1] for r in row]


def lr_from_nearwall_u(level_dir, t):
    """Independent instrument: the sign change of u_x in the first cell row above
    the wall. Different field, different discretisation, same physical event --
    and the SAME last-crossing-in-window rule, because the corner vortex shows up
    in u_x exactly as it shows up in the wall shear."""
    xs, us = nearwall_u_profile(level_dir, t)
    return last_sign_change_in_window(xs, us)


# ------------------------------------------------------- planted-zero control --
def planted_zero(level_dir, t):
    """Plant a known perturbation into a COPY of the wallShearStress file, read it
    back FROM DISK, and prove the reader can see a non-zero before its zeros are
    believed (CLAUDE.md rule 3). Unchanged from attempt 1."""
    src = os.path.join(level_dir, t, "wallShearStress")
    tmp = tempfile.mkdtemp(prefix="vmfl064r2_plant_")
    try:
        dst = os.path.join(tmp, "wallShearStress")
        shutil.copy(src, dst)
        base = read_patch_vector_x(dst, "bottomWall")
        txt  = open(dst).read()
        blk  = _patch_block(txt, "bottomWall")
        trip = re.findall(r"\(([^()]*)\)", blk)
        old  = trip[0]
        parts = old.split()
        new  = "%.12g %s %s" % (float(parts[0]) + PLANT, parts[1], parts[2])
        newblk = blk.replace("(" + old + ")", "(" + new + ")", 1)
        open(dst, "w").write(txt.replace(blk, newblk, 1))
        seen = read_patch_vector_x(dst, "bottomWall")
        # SINGLE-POINT plant into a SINGLE-POINT reader (face 0 only) -- NOT an
        # averaging reader, so there is no 1/sqrt(N) dilution (L-340); the reader
        # delta equals the plant.
        delta = seen[0] - base[0]
        ok = abs(delta - PLANT) < 1e-12
        # FALL-THROUGH REFUSAL: the only way this control RETURNS is to have seen
        # the plant. A blind reader REFUSES here, not merely in main().
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
def completion(run_root, level):
    """CLAUDE.md rule 4, adapted for a residualControl-terminated STEADY run and
    DECLARED THAT WAY IN THE FROZEN PRE-REGISTRATION (sec.6), not improvised here,
    and split into L-342 FIELD CLASSES.

    PHYSICS-CRITICAL (these GATE; any failure REFUSES exit 2):
        an 'End' line in log.simpleFoam            (EXACT name -- never a log* glob,
                                                    which matches log.blockMesh first)
        'SIMPLE solution converged' present        (stopped on its own criterion)
        last Time  <  endTime                      (did NOT run out of clock; for a
                                                    steady solve 'last time == endTime'
                                                    would mean it ran out of clock
                                                    WITHOUT converging)
        ExecutionTime count == the iteration count
        the declared fields present at that time
        age guard: fields newer than the case's own 0/U

    INFRASTRUCTURE (L-342): RUN_RC.<level>, written by the launcher AFTER the
        solver exits. ABSENT -> rc is NOT MEASURED, disclosed, and the grade
        PROCEEDS on the physics artefacts, which are strictly the stronger
        evidence that the solver completed. PRESENT AND rc != 0 -> REFUSE, because
        a recorded non-zero rc is evidence about the SOLVER, not about the poller.
    """
    level_dir = os.path.join(run_root, level)
    out = {"level": level, "level_dir": level_dir}

    # ---- infrastructure class (never voids the run by its absence) ----
    rcf = os.path.join(run_root, "RUN_RC.%s" % level)
    out["rc_source"] = rcf
    if not os.path.exists(rcf):
        out["rc"] = None
        out["rc_status"] = "NOT MEASURED"
        out["rc_note"] = ("RUN_RC.%s absent -- INFRASTRUCTURE field (L-342). A bookkeeping "
                          "failure invalidates the bookkeeping, never the physics artefacts; "
                          "the grade proceeds on the physics-critical clauses below." % level)
    else:
        rct = open(rcf).read()
        # Parse TOLERANTLY: the launcher writes `rc = 0` WITH spaces; a reader
        # requiring `rc=0` would find no match and mis-grade a correct run.
        m = re.search(r"^\s*rc\s*=\s*(-?\d+)", rct, re.M)
        if not m:
            out["rc"] = None
            out["rc_status"] = "NOT MEASURED"
            out["rc_note"] = ("RUN_RC.%s present but carries no rc= line -- INFRASTRUCTURE "
                              "field (L-342), disclosed, grade proceeds." % level)
        else:
            out["rc"] = int(m.group(1))
            out["rc_status"] = "MEASURED"
            if out["rc"] != 0:
                raise SystemExit2("rc=%d recorded for %s (124 == the cap fired). A RECORDED "
                                  "non-zero rc is evidence about the SOLVER, not about the "
                                  "bookkeeping, and it still refuses (L-342)." % (out["rc"], level))
        for key in ("wall_s", "core_min", "timeout_s"):
            mm = re.search(r"^\s*%s\s*=\s*([0-9.eE+-]+)" % key, rct, re.M)
            out[key] = float(mm.group(1)) if mm else None

    # ---- physics-critical class (these gate) ----
    log = os.path.join(level_dir, "log.simpleFoam")     # EXACT name, never a glob
    if not os.path.exists(log):
        raise SystemExit2("PHYSICS-CRITICAL field missing: no log.simpleFoam in %s" % level_dir)
    lt = open(log).read()
    out["end_line"] = lt.count("\nEnd")
    if out["end_line"] < 1:
        raise SystemExit2("no End line in %s/log.simpleFoam" % level_dir)
    out["converged"] = ("SIMPLE solution converged" in lt)
    if not out["converged"]:
        raise SystemExit2("%s did not report SIMPLE convergence" % level_dir)

    times = [int(t) for t in re.findall(r"^Time = (\d+)", lt, re.M)]
    if not times:
        raise SystemExit2("no Time lines in %s/log.simpleFoam" % level_dir)
    out["last_time"] = times[-1]
    out["n_exec"] = lt.count("ExecutionTime")
    if out["n_exec"] != out["last_time"]:
        raise SystemExit2("%s ExecutionTime count %d != last time %d"
                          % (level_dir, out["n_exec"], out["last_time"]))

    cdp = os.path.join(level_dir, "system", "controlDict")
    if not os.path.exists(cdp):
        raise SystemExit2("PHYSICS-CRITICAL field missing: no system/controlDict in %s" % level_dir)
    ctl = open(cdp).read()
    out["endTime"] = float(re.search(r"^endTime\s+([0-9.eE+-]+)\s*;", ctl, re.M).group(1))
    if not (out["last_time"] < out["endTime"]):
        raise SystemExit2("%s reached endTime %g -- ran out of clock, did NOT converge"
                          % (level_dir, out["endTime"]))

    t = str(out["last_time"])
    out["time_dir"] = t
    for f in ("U", "p", "wallShearStress", "Cx", "Cy"):
        if not os.path.exists(os.path.join(level_dir, t, f)):
            raise SystemExit2("PHYSICS-CRITICAL field %s missing at %s/%s" % (f, level_dir, t))
    z = os.path.getmtime(os.path.join(level_dir, "0", "U"))
    for f in ("U", "wallShearStress"):
        if not os.path.getmtime(os.path.join(level_dir, t, f)) > z:
            raise SystemExit2("AGE GUARD: %s/%s/%s is not newer than 0/U" % (level_dir, t, f))
    out["age_guard"] = "fields newer than 0/U"
    return out


# ------------------------------------------------------------ Roache triple ----
def roache(f1, f2, f3, r=RATIO, fs=FS):
    """f1 coarse, f2 medium, f3 fine. Byte-identical to attempt 1."""
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
    # OBSERVED-ORDER FLOOR. R = d32/d21 near 1 is a STAGNANT family; ln(R)/ln(r)
    # of it is a floating-point crumb that reads as a valid, very small observed
    # order, and a GCI computed from it is a number with no meaning.
    # FINDING_p_floor.md sec.4.
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
    """The ONE verdict path. main() grades through it and the planted controls
    DRIVE it, so the controls exercise the code that actually decides, not a
    paraphrase of it. Vocabulary is fixed (CLAUDE.md rule 1)."""
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
                "Ceiling is GATE REACHED, not PASS: see PREREGISTRATION.md line 4." % TOL)
    return ("GATE FAIL", "LR/s outside the frozen %.3g band" % TOL)


# ----------------------------------------- constructed OpenFOAM field writers --
# Module level (not selftest-local) so main()'s controls use the SAME builders.
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


def write_profile(td, xs, tau_phys):
    """Write a constructed bottom-wall profile to disk in the SAME OpenFOAM form
    the solver writes, so the controls exercise the REAL file readers. The grader
    applies ORIENT = -1, so the file carries tau_rep = -tau_phys. u_x is written
    with the SAME sign structure (u and tau share sign at the wall)."""
    os.makedirs(td, exist_ok=True)
    open(os.path.join(td, "wallShearStress"), "w").write(
        _wss("bottomWall", [(-v, 0.0, 0.0) for v in tau_phys]))
    open(os.path.join(td, "Cx"), "w").write(_cx(xs))
    open(os.path.join(td, "Cy"), "w").write(_cy([1e-4] * len(xs)))
    open(os.path.join(td, "U"), "w").write(_u([(v, 0.0, 0.0) for v in tau_phys]))
    return xs


def _bfs_xs(n=256, length=0.1):
    """The x abscissae of an L3-shaped bottom wall: 256 downstream faces over
    0.1 m, i.e. dx = 3.906e-4 m -- the SAME dx the real L3 reported
    (RESULTS.md attempt 1: dx 3.91e-03/7.81e-04/3.91e-04 for L1/L2/L3)."""
    return [(i + 0.5) * length / n for i in range(n)]


def corner_vortex_profile(x_star, x_corner=7.0e-4, n=256):
    """A CONSTRUCTED bottom-wall shear profile carrying a SECONDARY CORNER VORTEX.

    tau_phys(x) = (x - x_corner) * (x - x_star):
        x < x_corner            -> POSITIVE (the counter-rotating corner eddy,
                                   forward near-wall flow at the step foot)
        x_corner < x < x_star   -> NEGATIVE (the primary recirculation bubble)
        x > x_star              -> POSITIVE (attached, forward)
    x_corner = 7.0e-4 m is where the real L3 crossing sat (attempt-1 RESULTS.md
    triage: faces at x = 1.95e-4 and 5.86e-4 POSITIVE, x = 9.77e-4 NEGATIVE), so
    this construction reproduces the measured L3 structure, not an invented one."""
    xs = _bfs_xs(n=n)
    return xs, [(x - x_corner) * (x - x_star) for x in xs]


def single_bubble_profile(x_star, n=256):
    """The attempt-1 L1/L2 structure: ONE bubble, NO corner eddy -- the profile
    starts negative and crosses once."""
    xs = _bfs_xs(n=n)
    return xs, [(x - x_star) for x in xs]


# --------------- PLANTED CONTROL THAT DRIVES THE R2 REPAIR (rule 3 form) -------
def corner_vortex_control():
    """THE CONTROL THAT DRIVES THE FIX. A repair nobody drives is a repair nobody
    has -- the same rule the p-floor control was built under (FINDING_p_floor.md
    sec.4), applied to the reader change that IS this re-registration.

    Four probes, all on bytes WRITTEN TO DISK and read back through the real
    OpenFOAM readers, all REFUSING (exit 2) on failure:

      (1) DRIVES THE FIX. A profile with a secondary corner vortex and a KNOWN
          primary reattachment x_star = 6*s (deliberately != the 5*s target, so a
          reader that returned the target would be caught). The R2 reader must
          return x_star; the ATTEMPT-1 LOGIC on the SAME BYTES must REFUSE with
          exit 2 and the attempt-1 message. If the old logic did NOT refuse, this
          control refuses -- because then the repair is not driven by anything.
      (2) CONSERVATIVE ON THE OLD SHAPE. On a single-bubble profile (no corner
          eddy -- the attempt-1 L1/L2 structure) the R2 reader and the attempt-1
          reader must return the SAME number, exactly. The change must not move a
          case the old reader could already grade.
      (3) THE WINDOW IS LOAD-BEARING. A spurious crossing planted DOWNSTREAM of
          X_WIN_HI must be ignored: the reader must still return x_star. Without
          the window, 'the last crossing' would be the planted artefact.
      (4) CROSS-INSTRUMENT. The near-wall-u instrument, run on the same
          constructed case, must return x_star too.
    """
    def refuse(tag, detail):
        raise SystemExit2("CORNER-VORTEX PLANTED CONTROL FAILED [%s]: %s "
                          "(window %.4g < x <= %.4g m; PREREGISTRATION.md line 5)"
                          % (tag, detail, X_WIN_LO, X_WIN_HI))

    out = {"x_win_lo": X_WIN_LO, "x_win_hi": X_WIN_HI, "probes": {}}
    x_star = 6.0 * S_STEP           # 0.0294 m -- NOT the 5*s reference
    d = tempfile.mkdtemp(prefix="vmfl064r2_cv_")
    try:
        # ---- (1) the corner-vortex profile: R2 reads it, attempt-1 refuses it --
        xs, tau = corner_vortex_profile(x_star)
        dx = xs[1] - xs[0]
        td = os.path.join(d, "cv", "1000")
        write_profile(td, xs, tau)
        x_disk, tau_disk = wallshear_profile(os.path.join(d, "cv"), "1000")
        lr_new = last_sign_change_in_window(x_disk, tau_disk)
        counts = count_sign_changes_in_window(x_disk, tau_disk)
        legacy_refused, legacy_code, legacy_lr = False, None, None
        try:
            legacy_lr = legacy_grade_path(x_disk, tau_disk, tag="CONTROL")
        except SystemExit as ex:
            legacy_refused, legacy_code = True, ex.code
        out["probes"]["corner_vortex"] = {
            "x_star": x_star, "x_corner": 7.0e-4, "dx": dx,
            "r2_reader_LR": lr_new,
            "r2_reader_LR_over_s": (lr_new / S_STEP) if lr_new is not None else None,
            "sign_changes": counts,
            "attempt1_refused": legacy_refused, "attempt1_exit_code": legacy_code,
            "attempt1_LR": legacy_lr}
        if not counts["starts_positive"]:
            refuse("corner vortex", "the constructed profile does not START POSITIVE, so it "
                                    "does not carry a corner vortex at all")
        if counts["neg_to_pos"] != 1 or counts["pos_to_neg"] != 1:
            refuse("corner vortex", "the constructed profile has %r sign changes, expected one "
                                    "of each (eddy end + reattachment)" % (counts,))
        if lr_new is None:
            refuse("corner vortex", "the R2 reader found NO reattachment on a profile that has "
                                    "one at x = %.6f m" % x_star)
        if abs(lr_new - x_star) > dx:
            refuse("corner vortex", "the R2 reader returned %.6f m, not the constructed %.6f m "
                                    "(dx = %.6f m)" % (lr_new, x_star, dx))
        if abs(lr_new - REF_LRS * S_STEP) < dx:
            refuse("corner vortex", "the R2 reader returned the REFERENCE (%.6f m) rather than "
                                    "the constructed %.6f m -- a reader that reports the target "
                                    "is not a reader" % (REF_LRS * S_STEP, x_star))
        if not legacy_refused:
            refuse("corner vortex", "the ATTEMPT-1 logic did NOT refuse this profile (it "
                                    "returned %r) -- then the R2 reader change is not driven by "
                                    "anything and this control is decorative" % (legacy_lr,))
        if legacy_code != 2:
            refuse("corner vortex", "the attempt-1 logic exited %r, not 2" % (legacy_code,))

        # ---- (2) conservative on a single-bubble (attempt-1 L1/L2) profile -----
        xs2, tau2 = single_bubble_profile(x_star)
        td2 = os.path.join(d, "sb", "1000")
        write_profile(td2, xs2, tau2)
        x2, t2 = wallshear_profile(os.path.join(d, "sb"), "1000")
        lr_new2 = last_sign_change_in_window(x2, t2)
        lr_old2 = legacy_first_sign_change(x2, t2)
        out["probes"]["single_bubble_agreement"] = {
            "r2_reader_LR": lr_new2, "attempt1_LR": lr_old2}
        if lr_old2 is None:
            refuse("single bubble", "the attempt-1 reader failed on a single-bubble profile -- "
                                    "the control construction is wrong, not the reader")
        if lr_new2 is None or abs(lr_new2 - lr_old2) > 1e-12:
            refuse("single bubble", "R2 reader %r != attempt-1 reader %r on a profile with NO "
                                    "corner vortex -- the change is not conservative"
                   % (lr_new2, lr_old2))

        # ---- (3) the registered window is load-bearing -------------------------
        xs3 = list(xs)
        tau3 = list(tau)
        # plant a spurious reversal-and-recovery ENTIRELY downstream of X_WIN_HI
        planted_at = None
        for i, x in enumerate(xs3):
            if X_WIN_HI + 0.005 <= x <= X_WIN_HI + 0.015:
                tau3[i] = -abs(tau3[i]) - 1.0
                planted_at = x
        if planted_at is None:
            refuse("window", "could not plant a downstream artefact -- the construction does "
                             "not reach past X_WIN_HI = %.4g m" % X_WIN_HI)
        td3 = os.path.join(d, "win", "1000")
        write_profile(td3, xs3, tau3)
        x3, t3 = wallshear_profile(os.path.join(d, "win"), "1000")
        lr_win = last_sign_change_in_window(x3, t3)
        lr_nowin = last_sign_change_in_window(x3, t3, X_WIN_LO, max(x3) + 1.0)
        out["probes"]["window_excludes_downstream_artefact"] = {
            "planted_reversal_up_to_x": planted_at,
            "LR_with_window": lr_win, "LR_without_window": lr_nowin}
        if lr_win is None or abs(lr_win - x_star) > dx:
            refuse("window", "with the registered window the reader returned %r, not the "
                             "constructed %.6f m" % (lr_win, x_star))
        if lr_nowin is None or abs(lr_nowin - x_star) <= dx:
            refuse("window", "removing the window did NOT change the answer (%r) -- then the "
                             "window is untested and this probe proves nothing" % (lr_nowin,))

        # ---- (4) the cross-instrument reader on the same construction ----------
        lr_u = lr_from_nearwall_u(os.path.join(d, "cv"), "1000")
        out["probes"]["cross_instrument"] = {"nearwall_u_LR": lr_u}
        if lr_u is None or abs(lr_u - x_star) > dx:
            refuse("cross-instrument", "near-wall-u reader returned %r, not the constructed "
                                       "%.6f m" % (lr_u, x_star))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    out["passed"] = True
    return out


# ------------------------------------- PLANTED CONTROL for the p-floor (rule 3 form) --
def p_floor_control():
    """PLANTED CONTROL for the observed-order floor. Unchanged from attempt 1.

    A floor nobody tests is a floor nobody has (FINDING_p_floor.md sec.4). This
    control PLANTS three constructed triples into the comparator's OWN roache()
    and OWN verdict_for(), and REFUSES (exit 2) if any is graded the wrong way:

      (a) the equally spaced triple (1.0, 1.1, 1.2) -- d21 == d32 exactly, R = 1,
          a family that is not converging at all. It must grade NOT A RESULT with
          NO GCI, EVEN THOUGH the fine value would sit inside the band.
      (b) a triple whose observed order is genuinely COMPUTED and lands below the
          floor (p = 0.01). This is the probe that drives the floor itself, since
          (a) is caught one step earlier by the ratio test.
      (c) a triple with p = 0.5, comfortably ABOVE the floor: the floor must NOT
          fire, and a GCI MUST be produced.

    NO `assert` ANYWHERE: `python3 -O` strips asserts (L-332), so every branch
    below refuses with SystemExit2.
    """
    def refuse(tag, detail):
        raise SystemExit2("P-FLOOR PLANTED CONTROL FAILED [%s]: %s (P_MIN = %.3g, "
                          "FINDING_p_floor.md sec.4)" % (tag, detail, P_MIN))

    out = {"P_MIN": P_MIN, "probes": {}}

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

    print("=== VMFL064-R2 comparator selftest ===")
    print("--- selftest: the R2 sign-change locator (LAST crossing in the window) ---")
    chk(abs(last_sign_change_in_window([0.001, 0.002, 0.003, 0.004], [-2, -1, 1, 2]) - 0.0025) < 1e-12,
        "linear interpolation of the crossing",
        last_sign_change_in_window([0.001, 0.002, 0.003, 0.004], [-2, -1, 1, 2]))
    chk(last_sign_change_in_window([0.001, 0.002, 0.003], [1, 2, 3]) is None,
        "no reversal anywhere -> None")
    chk(last_sign_change_in_window([0.001, 0.002, 0.003], [-1, -2, -3]) is None,
        "never recovers -> None")
    chk(abs(last_sign_change_in_window([0.001, 0.002, 0.003, 0.004, 0.005],
                                       [1.0, -1.0, 1.0, -1.0, 1.0]) - 0.0045) < 1e-12,
        "two crossings -> the LAST one is returned",
        last_sign_change_in_window([0.001, 0.002, 0.003, 0.004, 0.005], [1.0, -1.0, 1.0, -1.0, 1.0]))
    chk(last_sign_change_in_window([0.06, 0.07], [-1.0, 1.0]) is None,
        "a crossing entirely outside the window -> None")

    print("--- selftest: the attempt-1 locator, preserved for the control ---")
    chk(legacy_first_sign_change([0, 1, 2, 3], [-2, -1, 1, 2]) is not None,
        "attempt-1 reader still works on a profile that starts negative")
    chk(legacy_first_sign_change([0, 1, 2, 3], [2, -1, 1, 2]) is None,
        "attempt-1 reader returns None when the profile starts POSITIVE (the L3 refusal)")

    print("--- selftest: PLANTED CONTROL -- the corner vortex DRIVES the R2 repair ---")
    # The control REFUSES (SystemExit2) on failure, so reaching the next line at
    # all is the evidence; the chk()s below record the four probes it drove.
    cv = corner_vortex_control()
    pr = cv["probes"]
    chk(pr["corner_vortex"]["r2_reader_LR"] is not None
        and abs(pr["corner_vortex"]["r2_reader_LR"] - 6.0 * S_STEP) <= pr["corner_vortex"]["dx"],
        "R2 reader returns the PRIMARY length on a corner-vortex profile",
        "LR/s = %.6f (constructed 6.000000)" % pr["corner_vortex"]["r2_reader_LR_over_s"])
    chk(pr["corner_vortex"]["attempt1_refused"] and pr["corner_vortex"]["attempt1_exit_code"] == 2,
        "attempt-1 logic REFUSES (exit 2) on the SAME bytes -- the fix is driven",
        "exit %r" % pr["corner_vortex"]["attempt1_exit_code"])
    chk(pr["corner_vortex"]["sign_changes"]["starts_positive"]
        and pr["corner_vortex"]["sign_changes"]["neg_to_pos"] == 1,
        "the constructed profile really carries a corner vortex",
        json.dumps(pr["corner_vortex"]["sign_changes"], sort_keys=True))
    chk(abs(pr["single_bubble_agreement"]["r2_reader_LR"]
            - pr["single_bubble_agreement"]["attempt1_LR"]) < 1e-12,
        "on a single-bubble profile R2 == attempt 1 EXACTLY (change is conservative)",
        pr["single_bubble_agreement"]["r2_reader_LR"])
    chk(abs(pr["window_excludes_downstream_artefact"]["LR_with_window"] - 6.0 * S_STEP) < 4e-4
        and abs(pr["window_excludes_downstream_artefact"]["LR_without_window"] - 6.0 * S_STEP) > 4e-4,
        "the registered window excludes a downstream artefact that would otherwise win",
        "with %.6f / without %.6f" % (pr["window_excludes_downstream_artefact"]["LR_with_window"],
                                      pr["window_excludes_downstream_artefact"]["LR_without_window"]))
    chk(pr["cross_instrument"]["nearwall_u_LR"] is not None
        and abs(pr["cross_instrument"]["nearwall_u_LR"] - 6.0 * S_STEP) <= pr["corner_vortex"]["dx"],
        "near-wall-u instrument returns the same primary length",
        pr["cross_instrument"]["nearwall_u_LR"])

    print("--- selftest: Roache classifier (unchanged from attempt 1) ---")
    chk(roache(1.0, 1.5, 1.75)["state"] == "CONVERGING", "first-order -> CONVERGING")
    chk(abs(roache(1.0, 1.5, 1.75)["p"] - 1.0) < 1e-9, "p == 1", roache(1.0, 1.5, 1.75)["p"])
    chk(roache(1.0, 1.25, 1.3125)["state"] == "CONVERGING", "second-order family")
    chk(abs(roache(1.0, 1.25, 1.3125)["p"] - 2.0) < 1e-9, "p == 2")
    chk(roache(1.0, 2.0, 4.0)["state"] == "DIVERGENT", "divergent -> DIVERGENT")
    chk(roache(1.0, 2.0, 1.5)["state"] == "OSCILLATORY", "oscillatory -> OSCILLATORY")
    chk(roache(2.0, 2.0, 2.0)["state"] == "EXACT", "identical -> EXACT")

    print("--- selftest: PLANTED CONTROL -- the observed-order floor P_MIN = %.3g ---" % P_MIN)
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

    print("--- selftest: the gate can FAIL and can PASS (band UNCHANGED at %.3g) ---" % TOL)
    chk(abs(5.0 - REF_LRS) / REF_LRS <= TOL, "exact reference is inside band")
    chk(abs(5.4 - REF_LRS) / REF_LRS <= TOL, "+8% is inside band")
    chk(not (abs(5.7 - REF_LRS) / REF_LRS <= TOL), "+14% is OUTSIDE band")
    chk(not (abs(4.2 - REF_LRS) / REF_LRS <= TOL), "-16% is OUTSIDE band")

    print("--- selftest: ORIENT is applied, not assumed away ---")
    chk(ORIENT == -1.0, "reported wallShearStress.x is inverted to physical")

    print("--- selftest: LR extraction and planted-zero on a CONSTRUCTED field ---")
    d = tempfile.mkdtemp(prefix="st064r2_")
    try:
        x_star = 6.0 * S_STEP
        xs, tau = corner_vortex_profile(x_star)
        write_profile(os.path.join(d, "L1", "1000"), xs, tau)
        lr_tau, xr, taur = lr_from_wallshear(os.path.join(d, "L1"), "1000")
        lr_u = lr_from_nearwall_u(os.path.join(d, "L1"), "1000")
        dx = xr[1] - xr[0]
        chk(abs(lr_tau - x_star) < dx,
            "wall-shear LR == constructed x_star (LR/s = %.3f)" % (lr_tau / S_STEP), lr_tau)
        chk(abs(lr_u - x_star) < dx, "near-wall-u LR == constructed x_star", lr_u)
        chk(abs(lr_tau - lr_u) < 1e-9, "cross-instrument agreement is exact on the construction")
        pz = planted_zero(os.path.join(d, "L1"), "1000")
        chk(pz["passed"] and abs(pz["reader_delta"] - PLANT) < 1e-12,
            "planted-zero sees the plant (no dilution, L-340)")
        global read_patch_vector_x
        _orig = read_patch_vector_x
        try:
            read_patch_vector_x = lambda p, patch: [0.0] * 256   # blind reader
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

    print("--- selftest: strict completion, with L-342 FIELD CLASSES ---")
    d = tempfile.mkdtemp(prefix="stc064r2_")
    _cwd = os.getcwd()
    try:
        # chdir into the scratch root and grade a RELATIVE run root, so every
        # refusal message this block prints is DETERMINISTIC -- a mkdtemp path in
        # the output would make `--selftest` differ between two invocations and
        # destroy the byte-for-byte `python3` vs `python3 -O` comparison (L-332).
        os.chdir(d)
        def make_level(root, lvl, rc, converged=True, endtime=20000, last=200, write_rc=True):
            ld = os.path.join(root, lvl)
            os.makedirs(os.path.join(ld, "system"), exist_ok=True)
            os.makedirs(os.path.join(ld, "0"), exist_ok=True)
            os.makedirs(os.path.join(ld, str(last)), exist_ok=True)
            if write_rc:
                # SPACES around '=' -- the launcher's form; a reader requiring
                # `rc=0` would find no match and mis-grade a correct run.
                open(os.path.join(root, "RUN_RC.%s" % lvl), "w").write(
                    "rc = %d\nlevel = %s\nwall_s = 12\nranks = 1\ncore_min = 0.2\ntimeout_s = 5400\n"
                    % (rc, lvl))
            body = "".join("Time = %d\nExecutionTime = %d s\n" % (i, i) for i in range(1, last + 1))
            body += ("SIMPLE solution converged in %d iterations\n" % last if converged else "")
            body += "\nEnd\n"
            open(os.path.join(ld, "log.simpleFoam"), "w").write(body)
            open(os.path.join(ld, "system", "controlDict"), "w").write("endTime %d;\n" % endtime)
            xs, tau = corner_vortex_profile(6.0 * S_STEP)
            write_profile(os.path.join(ld, str(last)), xs, tau)
            open(os.path.join(ld, str(last), "p"), "w").write("p\n")
            zt = os.path.getmtime(os.path.join(ld, str(last), "U")) - 10
            open(os.path.join(ld, "0", "U"), "w").write("U0\n")
            os.utime(os.path.join(ld, "0", "U"), (zt, zt))

        make_level(".", "L1", 0)
        c = completion(".", "L1")
        chk(c["rc"] == 0 and c["rc_status"] == "MEASURED" and c["converged"] and c["last_time"] == 200,
            "completion parses `rc = 0` (spaces) and accepts a converged run")

        make_level(".", "L2", 1)
        refused = False
        try:
            completion(".", "L2")
        except SystemExit as ex:
            refused = (ex.code == 2)
        chk(refused, "completion REFUSES (exit 2) a RECORDED rc != 0")

        # L-342: the poller died and RUN_RC was never written. The physics
        # artefacts are intact, so the grade PROCEEDS with rc NOT MEASURED.
        make_level(".", "L3", 0, write_rc=False)
        c3 = completion(".", "L3")
        chk(c3["rc"] is None and c3["rc_status"] == "NOT MEASURED" and c3["last_time"] == 200,
            "L-342: ABSENT infrastructure field -> NOT MEASURED, disclosed, grade PROCEEDS",
            c3["rc_status"])

        # ... and a physics-critical field absent still REFUSES.
        os.remove(os.path.join("L3", "200", "wallShearStress"))
        phys_refused = False
        try:
            completion(".", "L3")
        except SystemExit as ex:
            phys_refused = (ex.code == 2)
        chk(phys_refused, "L-342: an absent PHYSICS-CRITICAL field still REFUSES (exit 2)")
    finally:
        os.chdir(_cwd)
        shutil.rmtree(d, ignore_errors=True)

    print("\nchecks run: see the PASS/FAIL lines above")
    print("SELFTEST: %s" % ("all checks passed" if ok else "FAILURES PRESENT"))
    return 0 if ok else 1


# ----------------------------------------------------------------------- main --
def main(argv):
    root = os.path.normpath(RUN_ROOT)
    if "--run-root" in argv:
        root = os.path.normpath(argv[argv.index("--run-root") + 1])

    res = {"case": "VMFL064-R2", "manual_page": "195/196",
           "supersedes_row": "register row #29 (VMFL064, NOT A RESULT) -- NOT overwritten",
           "reference": REF_LRS, "reference_kind": "EXPERIMENTAL (Armaly et al. 1983)",
           "ansys_context_only": ANSYS_LRS, "tol": TOL, "s_step": S_STEP,
           "search_window_m": [X_WIN_LO, X_WIN_HI],
           "field_classes": FIELD_CLASSES,
           "comparator": os.path.abspath(__file__),
           "run_root": root,
           "completion": {}, "levels": {}, "planted_zero": None}

    print("=" * 78)
    print("VMFL064-R2 -- Low Re flow in a channel with sudden asymmetric expansion")
    print("Ansys FD Verification Manual 2026 R1, p. 195/196")
    print("reference: LR/s = %.4g  (EXPERIMENTAL -- Armaly, Durst, Pereira &" % REF_LRS)
    print("           Schoenung, JFM 127:473, 1983).  Ansys Fluent %.4g = CONTEXT ONLY" % ANSYS_LRS)
    print("reader: LAST negative-to-positive wall-shear crossing in %.4g < x <= %.4g m"
          % (X_WIN_LO, X_WIN_HI))
    print("=" * 78)

    # PLANTED CONTROLS, driven on the FROZEN grading path itself, before any level
    # is read. Each REFUSES (exit 2) rather than grading.
    res["corner_vortex_control"] = corner_vortex_control()
    cvp = res["corner_vortex_control"]["probes"]["corner_vortex"]
    print("corner-vortex planted control OK: constructed LR/s = %.6f recovered by the R2 reader; "
          "\n  the attempt-1 logic REFUSED the same bytes with exit %d"
          % (cvp["r2_reader_LR_over_s"], cvp["attempt1_exit_code"]))
    res["p_floor_control"] = p_floor_control()
    print("p-floor planted control OK (P_MIN = %.3g): (1.0,1.1,1.2) -> %s, no GCI"
          % (P_MIN, res["p_floor_control"]["probes"]["equally_spaced_1.0_1.1_1.2"]["verdict"]))

    print("\nL-342 FIELD CLASSES: %d physics-critical, %d infrastructure "
          "(absent infrastructure -> NOT MEASURED, never a refusal)"
          % (len(FIELD_CLASSES["physics_critical"]), len(FIELD_CLASSES["infrastructure"])))

    lrs = []
    not_measured = []
    for lv in LEVELS:
        d = os.path.join(root, lv)
        c = completion(root, lv)
        res["completion"][lv] = c
        if c["rc_status"] != "MEASURED":
            not_measured.append("%s rc (%s)" % (lv, c["rc_source"]))
        t = c["time_dir"]
        lr_tau, xs, taus = lr_from_wallshear(d, t)
        if lr_tau is None:
            raise SystemExit2("%s: no negative-to-positive wall-shear crossing inside the "
                              "registered window %.4g < x <= %.4g m -- no reattachment found"
                              % (lv, X_WIN_LO, X_WIN_HI))
        lr_u = lr_from_nearwall_u(d, t)
        if lr_u is None:
            raise SystemExit2("%s: near-wall u_x never changes sign inside the window" % lv)
        counts = count_sign_changes_in_window(xs, taus)
        dx = (xs[1] - xs[0]) if len(xs) > 1 else 0.0
        agree = abs(lr_tau - lr_u)
        if agree > 3.0 * dx:
            raise SystemExit2(
                "%s: CROSS-INSTRUMENT CONTROL FAILED -- wall-shear LR %.6f vs "
                "near-wall-u LR %.6f differ by %.6f > 3 cell widths (%.6f). The "
                "wallShearStress sign convention may have changed." % (lv, lr_tau, lr_u, agree, 3.0 * dx))
        res["levels"][lv] = {"LR_m": lr_tau, "LR_over_s": lr_tau / S_STEP,
                             "LR_crosscheck_m": lr_u, "crosscheck_delta_m": agree,
                             "cell_dx_m": dx, "time_dir": t, "n_wall_faces": len(xs),
                             "sign_changes_in_window": counts,
                             "corner_vortex_resolved": bool(counts["starts_positive"])}
        lrs.append(lr_tau / S_STEP)
        print("  %-3s  LR/s = %.6f   (LR = %.6f m; cross-check %.6f m, delta %.2e, dx %.2e; "
              "crossings n2p=%d p2n=%d, corner vortex %s)"
              % (lv, lr_tau / S_STEP, lr_tau, lr_u, agree, dx,
                 counts["neg_to_pos"], counts["pos_to_neg"],
                 "RESOLVED" if counts["starts_positive"] else "not resolved"))

    if not_measured:
        print("\nNOT MEASURED (L-342 infrastructure, disclosed, grade proceeds): %s"
              % "; ".join(not_measured))
        res["not_measured"] = not_measured

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
        if tri["p"] > 2.3:
            print("  p_obs SUSPICIOUSLY HIGH (> formal p_f = 2): a warning, not a win.")
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

    out = os.path.join(root, "GRADING_VMFL064_R2.json")
    with open(out, "w") as fh:
        json.dump(res, fh, indent=2, sort_keys=True)
    print("grading written to %s" % out)
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main(sys.argv))
