#!/usr/bin/env python3
"""T19b -- the FROZEN comparator.  Fully developed laminar forced convection
between PARALLEL PLATES, Re_Dh = 100, Pr = 0.71, buoyantBoussinesqSimpleFoam
with `simulationType laminar` and beta = 0, three levels ny = 20/40/80 across
the full gap (r = 2 in both directions), two wall arms.

THIS RUNG EARNS `V` FOR FORCED CONVECTION, LAMINAR, 2-D and nothing else.  Its
referent is EXACT/derived, so under the upheld V/P ruling it can reach GATE
REACHED at best and can NEVER reach HOLDS.

ROACHE FLOORS ARE IMPORTED (MESH_STANDARD.md section 10.5): STAGNANT_FLOOR and
P_MIN come from scripts/roache_triple.py; this file defines neither.

THE FINE VALUE IS GRADED, NEVER THE RICHARDSON EXTRAPOLATE.

NO `assert` (L-332).  Every refusal is sys.exit(2).  apply_gate() is the ONLY
function that writes a verdict.

Exit: 0 graded, 2 REFUSAL.

============================================================================
WHAT T19b CHANGES FROM analyse_t19.py, AND WHAT IT DOES NOT
============================================================================
NOT ONE GATE, THRESHOLD, BAND, FLOOR, CAP OR LABEL MOVES, and that is enforced
mechanically rather than promised: this file loads T19's OWN frozen
`T19_registered.json` FROM T19_runs BY EXPLICIT PATH, pinned by sha256, and
imports T19's OWN frozen `exact_t19.py` the same way.  The gate file is not
copied, not edited and not re-derived; if either parent file's bytes differ from
the pin, this comparator REFUSES rather than grades.

THE ONE REPAIR is to the SELFTEST.  analyse_t19.py:691-694 drove its limb
"live tree, no DONE markers -> exit 2 REFUSE" by calling `grade(HERE, ...)`,
where HERE is the LIVE T19_runs directory.  It passed only because nothing had
been marked DONE -- a D574-class false green, and worse than stale: once DONE
markers exist that limb runs the real grading path against a live run tree as a
side effect of its own selftest.

The replacement adopts T20_PREREGISTRATION.md section 10.1's registered S8
clause: NO SELFTEST LIMB MAY READ, STAT OR GLOB A LIVE RUN TREE, and the
invariance is MEASURED, not promised.  Three independent detectors, each with a
planted control, enforce it:
  (S8a) the whole limb set runs TWICE in one invocation -- once against a
        synthetic run root that is EMPTY, once against one FULLY POPULATED with
        six cases, time directories, STATUS and DONE markers -- and the two
        result structures must be BYTE-IDENTICAL;
  (S8b) a filesystem WATCHER records every read under the run root while the
        limbs execute and must record ZERO.  Rule 3: the watcher is PLANTED
        first, with a deliberate read it must see, and only then reset -- a zero
        from a watcher not shown able to see a non-zero is not evidence;
  (S8c) a second watcher over T19_runs, allowing ONLY the two pinned parent
        instruments, so that the FALSIFICATION SPECIMEN (P_q_c/828, P_Ts_c/541)
        is measured to be untouched rather than asserted to be.
  (S8d) a source-level detector: the name `HERE` does not occur anywhere inside
        the selftest functions, with a planted control proving the detector sees
        one when it is there.
============================================================================
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
EXIT_OK, EXIT_REFUSE = 0, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# --------- THE PARENT'S FROZEN INSTRUMENTS, BY EXPLICIT PATH AND PINNED -------
# T19b does not copy, restate or re-derive a single registered number.  It grades
# against T19's OWN frozen gate file and T19's OWN frozen analytic referent, both
# loaded from T19_runs by absolute path and both pinned by sha256.  A digest that
# does not reproduce is a REFUSAL, never a warning: it is the only mechanism by
# which "no gate moved" can be a measurement rather than a claim.
PARENT = os.path.join(os.path.dirname(HERE), "T19_runs")
REG_PATH = os.path.join(PARENT, "T19_registered.json")
REG_SHA256 = "84b3652a5187f04efeddb5b14cc91b2d1c5d9952b7608243bdd0078773a040b4"
EXACT_PATH = os.path.join(PARENT, "exact_t19.py")
EXACT_SHA256 = "aeaae65c9e849c8a40d9594e412e3a1bc63ebe79274f5bc704837570cf52545d"


def sha256_of(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def pin(path, want, what):
    if not os.path.isfile(path):
        refuse("the frozen parent instrument %s is missing at %s -- T19b grades against T19's "
               "own frozen files and will not substitute a copy" % (what, path))
    got = sha256_of(path)
    if got != want:
        refuse("%s at %s has sha256 %s but T19b pins %s -- the file that would run is NOT the "
               "frozen file, so no gate can be shown to be unmoved" % (what, path, got, want))
    return got


pin(EXACT_PATH, EXACT_SHA256, "exact_t19.py")
sys.path.insert(0, PARENT)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import exact_t19 as EX                                                  # noqa: E402
from roache_triple import STAGNANT_FLOOR, P_MIN, FS, gci_equal, PLANT   # noqa: E402

LEVELS = ("c", "m", "f")
TS_CASES = {lv: "P_Ts_%s" % lv for lv in LEVELS}
Q_CASES = {lv: "P_q_%s" % lv for lv in LEVELS}
REFINEMENT = 2.0
DIM = 2


def load_registered(root=None):
    p = os.path.join(root, "T19_registered.json") if root else REG_PATH
    if not os.path.isfile(p):
        refuse("no T19_registered.json -- the gate is not registered")
    if root is None:
        pin(p, REG_SHA256, "T19_registered.json")
    reg = json.load(open(p))
    fl = reg.get("roache_floors", {})
    if fl.get("STAGNANT_FLOOR") != STAGNANT_FLOOR or fl.get("P_MIN") != P_MIN:
        refuse("registered floors %r disagree with the imported roache_triple STAGNANT_FLOOR=%r "
               "P_MIN=%r (MESH_STANDARD 10.5: one name, one number)" % (fl, STAGNANT_FLOOR, P_MIN))
    return reg


def case_meta(root, case):
    p = os.path.join(root, case, "CASE.txt")
    if not os.path.isfile(p):
        refuse("no CASE.txt for %s" % case)
    return dict(re.findall(r"^([A-Za-z_0-9]+)=(.*)$", open(p).read(), re.M))


def latest_time(case_dir):
    ts = [t for t in os.listdir(case_dir) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) and float(t) > 0]
    return max(ts, key=float) if ts else None


def two_latest_times(case_dir):
    ts = sorted([t for t in os.listdir(case_dir) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) and float(t) > 0],
                key=float)
    if len(ts) < 2:
        return (ts[-1] if ts else None), None
    return ts[-1], ts[-2]


# ------------------------------------------------------------ THE READERS
def read_scalar(case_dir, time, name, ncells):
    """FLAT list of ncells values, blockMesh order for (nx ny 1): i (axial)
    fastest, then j (transverse).  index = j*nx + i."""
    p = os.path.join(case_dir, str(time), name)
    if not os.path.isfile(p):
        return None
    txt = open(p).read()
    m = re.search(r"internalField\s+nonuniform[^(]*\(\s*(.*?)\n\)", txt, re.S)
    if not m:
        return None
    vals = [float(v) for v in m.group(1).split()]
    if len(vals) != ncells:
        refuse("%s holds %d values, registered nx*ny = %d" % (p, len(vals), ncells))
    return vals


def read_ux(case_dir, time, ncells):
    """The AXIAL component of U, same ordering."""
    p = os.path.join(case_dir, str(time), "U")
    if not os.path.isfile(p):
        return None
    txt = open(p).read()
    m = re.search(r"internalField\s+nonuniform[^(]*\(\s*(.*?)\n\)\s*;", txt, re.S)
    if not m:
        return None
    trip = re.findall(r"\(\s*([0-9eE.+-]+)\s+([0-9eE.+-]+)\s+([0-9eE.+-]+)\s*\)", m.group(1))
    if len(trip) != ncells:
        refuse("%s holds %d vectors, registered nx*ny = %d" % (p, len(trip), ncells))
    return [float(t[0]) for t in trip]


def column(F, nx, ny, i):
    return [F[j * nx + i] for j in range(ny)]


def station_columns(nx, L, x_s):
    """The station is registered ON A CELL FACE, so the two adjacent columns
    straddle it and a linear interpolation is their mean.  Refuses otherwise."""
    k = x_s / (L / nx)
    if abs(k - round(k)) > 1e-9:
        refuse("the station %g is not on a cell face for nx=%d" % (x_s, nx))
    k = int(round(k))
    if k < 1 or k > nx - 1:
        refuse("the station column index %d is outside the mesh" % k)
    return k - 1, k


def bulk_mean(u, T):
    s = sum(u)
    if s == 0.0:
        refuse("the mass flux at the station is zero -- a missing number is not a zero")
    return sum(u[j] * T[j] for j in range(len(u))) / s


def nu_at_column(T, u, meta, arm):
    """Nusselt number from ONE column.  Returns (Nu_mean, Nu_lo, Nu_hi)."""
    Dh = float(meta["Dh"])
    dy = float(meta["dy"])
    delta = 0.5 * dy
    Tm = bulk_mean(u, T)
    if arm == "Ts":
        Tw = float(meta["T_wall"])
        nlo = ((Tw - T[0]) / delta) * Dh / (Tw - Tm)
        nhi = ((Tw - T[-1]) / delta) * Dh / (Tw - Tm)
    else:
        g = float(meta["dTdn_wall"])
        nlo = g * Dh / ((T[0] + g * delta) - Tm)
        nhi = g * Dh / ((T[-1] + g * delta) - Tm)
    return 0.5 * (nlo + nhi), nlo, nhi


def f_Re_from_pressure(p_rgh, u, nx, ny, i0, i1, meta):
    """f.Re from the AXIAL PRESSURE GRADIENT between the two station columns --
    second order in dy, unlike a one-sided wall-shear estimate, which is first
    order.  p_rgh is kinematic (m2/s2) in this solver."""
    dx = float(meta["dx"])
    Dh = float(meta["Dh"])
    nu = float(meta["nu"])
    p0 = sum(column(p_rgh, nx, ny, i0)) / ny
    p1 = sum(column(p_rgh, nx, ny, i1)) / ny
    dpdx = (p1 - p0) / dx
    ubar = sum(u) / len(u)
    f = (-dpdx) * Dh / (0.5 * ubar * ubar)
    return f * (ubar * Dh / nu), ubar


def f_Re_from_wall_shear(u, meta):
    """REPORTED, NEVER GRADED: the first-order wall-shear route, carried beside
    the graded pressure route as a consistency diagnostic."""
    dy = float(meta["dy"])
    Dh = float(meta["Dh"])
    ubar = sum(u) / len(u)
    tau_lo = u[0] / (0.5 * dy)
    tau_hi = u[-1] / (0.5 * dy)
    tau = 0.5 * (tau_lo + tau_hi)          # du/dy at the wall, one-sided, O(dy)
    return 8.0 * tau * Dh / ubar


def symmetry_witness(F):
    n = len(F)
    return max(abs(F[j] - F[n - 1 - j]) for j in range(n))


# ------------------------------------------- rule 3: planted-zero control
def _plant_lines(p):
    lines = open(p).read().splitlines(True)
    start = None
    for i, ln in enumerate(lines):
        if "internalField" in ln and "nonuniform" in ln:
            for j in range(i, min(i + 5, len(lines))):
                if lines[j].strip() == "(":
                    start = j + 1
                    break
            break
    if start is None:
        refuse("planted-zero control: could not locate internalField STRUCTURALLY")
    return lines, start


def planted_zero_control(case_dir, time, field_name, ncells, readers):
    """BOTH ARMS per reader, sized to the reader (L-340).  Copies first; never
    writes into the case.  `readers` are (name, fn(flat_list), [cell indices])."""
    tmp = tempfile.mkdtemp(prefix="t19pz_")
    try:
        dst = os.path.join(tmp, os.path.basename(case_dir))
        shutil.copytree(case_dir, dst, symlinks=True)
        if os.path.realpath(dst).startswith(os.path.realpath(case_dir)):
            refuse("planted-zero control: scratch copy resolved INSIDE the case tree")
        base = read_scalar(dst, time, field_name, ncells)
        if base is None:
            refuse("planted-zero control: the reader returned nothing on the unplanted copy")
        again = read_scalar(dst, time, field_name, ncells)
        dneg = max(abs(a - b) for a, b in zip(base, again))
        if dneg != 0.0:
            refuse("planted-zero control NEGATIVE ARM FAILED: %.17g on identical bytes -- the reader is NOISY" % dneg)
        p = os.path.join(dst, str(time), field_name)
        out = {}
        for name, fn, idxs in readers:
            lines, start = _plant_lines(p)
            orig = list(lines)
            before = {k: float(lines[start + k].strip()) for k in idxs}
            ref = fn(base)
            seen, floor = {}, None
            for mag in (1.0, 1e-1, 1e-2, PLANT, 1e-4, 1e-5, 1e-6, 1e-7):
                for k in idxs:
                    lines[start + k] = "%.17g\n" % (before[k] + mag)
                open(p, "w").write("".join(lines))
                got = read_scalar(dst, time, field_name, ncells)
                if got is None:
                    refuse("planted-zero control %s: reader returned nothing at plant %.3g" % (name, mag))
                d = abs(fn(got) - ref)
                seen[mag] = d
                if d > 0.0:
                    floor = mag
            open(p, "w").write("".join(orig))
            if floor is None:
                refuse("planted-zero control %s POSITIVE ARM FAILED: no plant magnitude was visible "
                       "-- the reader is BLIND" % name)
            # SIZING (L-340).  T14's rule "the read must move by at least 0.1 x the
            # plant" transfers only when the read has the SAME UNITS as the plant.
            # Here the readers return a Nusselt number and f.Re while the plant is a
            # temperature or a kinematic pressure, so the transferable statement is:
            # the REGISTERED plant must be VISIBLE, and the demonstrated detection
            # floor must be at or below it.
            if seen[PLANT] == 0.0:
                refuse("planted-zero control %s: the REGISTERED plant %.6g moved the read by exactly "
                       "zero, while %.6g was visible -- the reader cannot see a perturbation of the "
                       "registered size" % (name, PLANT, floor))
            if floor > PLANT:
                refuse("planted-zero control %s: the demonstrated detection floor %.3g is COARSER than "
                       "the registered plant %.6g" % (name, floor, PLANT))
            out[name] = dict(status="PASS", plant=PLANT, cells_planted=len(idxs), recovered=seen[PLANT],
                             negative_arm=dneg, demonstrated_detection_floor=floor,
                             ladder={("%g" % k): v for k, v in seen.items()})
            print("planted-zero control %-6s PASS: plant %.6g in %d cell(s), moved the read by %.6g, floor %.1g"
                  % (name, PLANT, len(idxs), seen[PLANT], floor))
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------- rule 5: the gate
def triple_of(vals):
    return gci_equal(vals["c"], vals["m"], vals["f"], REFINEMENT, DIM, fs=FS)


def apply_gate(value, lo, hi, tr, gate1_ok, gate1_why):
    """The ONLY function that writes a verdict.  Rule 5's fixed order, one way.
    `value` is ALWAYS the FINE value; the extrapolate is never passed in."""
    bv = "PASS" if lo <= value <= hi else "GATE FAIL"
    if not gate1_ok:
        return "NOT A RESULT", bv, "gate (1): " + gate1_why
    if tr["state"] != "CONVERGING":
        p = tr.get("order")
        return ("NOT A RESULT", bv, "gate (2): triple is %s%s -- rule 5 makes a triple that is not CONVERGING "
                "NOT A RESULT whatever its value says (STAGNANT_FLOOR=%g, P_MIN=%g)"
                % (tr["state"], (" (p = %.3e)" % p) if p is not None else "", STAGNANT_FLOOR, P_MIN))
    return bv, bv, ""


def fmt_tr(tr):
    p, g = tr.get("order"), tr.get("GCI_pct")
    return "%s p=%s GCI=%s" % (tr["state"], ("%.4f" % p) if p is not None else "n/a",
                               ("%.4e%%" % g) if g is not None else "REFUSED")


def residuals_reported(case_dir):
    """The last reported INITIAL and FINAL residuals of Ux, T and p_rgh.
    REPORTED, NEVER GATED.  An absolute residual floor is NOT the gate-(1)
    criterion for this rung, and the reason is on the record: T1c ran the same
    solver for the same 30 000 iterations and "the solver's own residualControl
    never tripped on any of the six cases and the offending case's T residual was
    an unremarkable 4e-05, so this was caught by comparing written fields, not by
    reading residuals" (build_t1c.py:57-63).  Gate (1) here is the PLATEAU test
    below, which compares the graded quantity between the last two writes -- the
    check that actually caught T1c's iteration-count defect.  An End line is a
    completion conjunct and is checked by mark_done_t19.py, not here.

    T19b CORRECTION, AND IT IS THE WHOLE MORAL OF THIS RUNG.  The sentence above
    is T19's, carried over verbatim because the DECISION it justifies -- an
    absolute residual floor is not this rung's gate -- is unchanged and may not
    be changed.  But the T1c fact it rests on was BORROWED and never measured on
    T19, and on T19 IT WAS FALSE: with build_t19.py:211's residualControl in
    place the solver's own control tripped on both cases that ran, at 828 and
    541 iterations against endTime 30000.  T19b removes the setting from the
    CASE (build_t19b.py) so that the borrowed condition is made TRUE by
    construction instead of assumed.  The borrow is now guarded, not deleted."""
    log = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(log):
        return None, "no log.solve"
    body = open(log, errors="replace").read()
    out = {}
    for fld in ("Ux", "T", "p_rgh"):
        r = re.findall(r"Solving for %s,\s*Initial residual = ([0-9.eE+-]+),\s*"
                       r"Final residual = ([0-9.eE+-]+)" % re.escape(fld), body)
        if not r:
            return None, "no %s solves in log.solve" % fld
        out[fld] = dict(last_initial=float(r[-1][0]), last_final=float(r[-1][1]), n_solves=len(r))
    if not re.search(r"^End\s*$", body, re.M):
        return out, "no End line"
    return out, ""


# ---------------------------------------------------------------- the grade
def _quantities_at(d, t, nx, ny, meta, arm):
    n = nx * ny
    T = read_scalar(d, t, "T", n)
    P = read_scalar(d, t, "p_rgh", n)
    U = read_ux(d, t, n)
    if T is None or P is None or U is None:
        return None
    i0, i1 = station_columns(nx, float(meta["L"]), float(meta["x_station"]))
    cols = []
    for i in (i0, i1):
        Tc, Uc = column(T, nx, ny, i), column(U, nx, ny, i)
        cols.append(dict(T=Tc, U=Uc, nu=nu_at_column(Tc, Uc, meta, arm),
                         symT=symmetry_witness(Tc), symU=symmetry_witness(Uc)))
    uc = [0.5 * (cols[0]["U"][j] + cols[1]["U"][j]) for j in range(ny)]
    fre, ubar = f_Re_from_pressure(P, uc, nx, ny, i0, i1, meta)
    return dict(T=T, P=P, U=U, i0=i0, i1=i1, uc=uc,
                Nu=0.5 * (cols[0]["nu"][0] + cols[1]["nu"][0]),
                Nu_lo=0.5 * (cols[0]["nu"][1] + cols[1]["nu"][1]),
                Nu_hi=0.5 * (cols[0]["nu"][2] + cols[1]["nu"][2]),
                fRe=fre, ubar=ubar,
                symT=max(c["symT"] for c in cols), symU=max(c["symU"] for c in cols),
                fRe_wall_shear_REPORTED=f_Re_from_wall_shear(uc, meta))


def read_case(root, case, arm):
    meta = case_meta(root, case)
    nx, ny = int(meta["nx"]), int(meta["ny"])
    d = os.path.join(root, case)
    t, tprev = two_latest_times(d)
    if t is None:
        refuse("%s has no time directory beyond 0" % case)
    q = _quantities_at(d, t, nx, ny, meta, arm)
    if q is None:
        refuse("could not read T / p_rgh / U on %s -- a missing number is not a zero" % case)
    # THE PLATEAU TEST (gate (1)): the same reader applied to the PREVIOUS write.
    plateau = None
    if tprev is not None:
        qp = _quantities_at(d, tprev, nx, ny, meta, arm)
        if qp is not None:
            plateau = dict(t_last=t, t_prev=tprev,
                           d_Nu=abs(q["Nu"] - qp["Nu"]) / abs(q["Nu"]),
                           d_fRe=abs(q["fRe"] - qp["fRe"]) / abs(q["fRe"]))
    res, res_why = residuals_reported(d)
    out = dict(meta=meta, dir=d, time=t, time_prev=tprev, nx=nx, ny=ny, ncells=nx * ny,
               plateau=plateau, residuals_REPORTED_ONLY=res, residuals_note=res_why)
    out.update(q)
    return out


def grade(root, json_out, reg, quiet_ref=False):
    allc = list(TS_CASES.values()) + list(Q_CASES.values())
    for case in allc:
        if not os.path.isfile(os.path.join(root, "DONE.%s" % case)):
            refuse("no DONE.%s -- the whole rung is graded or none of it is; mark_done_t19.py rules" % case)
    print("verifying the analytic reference before any comparison:")
    ref = EX.verify(quiet=quiet_ref)
    for key, got in (("fRe", ref["fRe_plates"]), ("Nu_H", ref["Nu_H_plates"]), ("Nu_T", ref["Nu_T_plates"])):
        want = reg["graded_rows"][{"fRe": "G1", "Nu_H": "G2", "Nu_T": "G3"}[key]]["reference"]
        if abs(got - want) > 1e-7 * abs(want):
            refuse("%s: derived reference %.10f != registered %.10f" % (key, got, want))

    ts = {lv: read_case(root, TS_CASES[lv], "Ts") for lv in LEVELS}
    qq = {lv: read_case(root, Q_CASES[lv], "q") for lv in LEVELS}
    nyv = {lv: ts[lv]["ny"] for lv in LEVELS}
    if not (nyv["m"] == 2 * nyv["c"] and nyv["f"] == 2 * nyv["m"]):
        refuse("the ladder is not r = 2: %r" % nyv)

    gate1_fail = []
    itr = {}
    pl_floor = reg["controls"]["C_PLATEAU"]["floor"]
    for lv in LEVELS:
        for tag, C in (("Ts", ts[lv]), ("q", qq[lv])):
            key = "%s_%s" % (tag, lv)
            pl = C["plateau"]
            if pl is None:
                itr[key] = dict(ok=False, plateau=None, residuals=C["residuals_REPORTED_ONLY"],
                                why="only ONE time directory: the plateau test cannot be evaluated")
                gate1_fail.append("%s: only one time directory, C_PLATEAU cannot be evaluated" % key)
                continue
            worst = max(pl["d_Nu"], pl["d_fRe"])
            ok = worst <= pl_floor
            itr[key] = dict(ok=ok, plateau=pl, residuals=C["residuals_REPORTED_ONLY"],
                            why="" if ok else "C_PLATEAU: the graded quantities moved %.3e between "
                                              "writes %s and %s, above the floor %.1e"
                                              % (worst, pl["t_prev"], pl["t_last"], pl_floor))
            if not ok:
                gate1_fail.append("%s: %s" % (key, itr[key]["why"]))
    sym_floor = reg["controls"]["C_SYM"]["floor_T"], reg["controls"]["C_SYM"]["floor_U"]
    for lv in LEVELS:
        for tag, C in (("Ts", ts[lv]), ("q", qq[lv])):
            if C["symT"] > sym_floor[0]:
                gate1_fail.append("%s %s: C_SYM T %.3e > %.1e" % (tag, lv, C["symT"], sym_floor[0]))
            if C["symU"] > sym_floor[1]:
                gate1_fail.append("%s %s: C_SYM U %.3e > %.1e" % (tag, lv, C["symU"], sym_floor[1]))
    mass = {}
    for lv in LEVELS:
        for tag, C in (("Ts", ts[lv]), ("q", qq[lv])):
            u0 = float(C["meta"]["U0"])
            d = abs(C["ubar"] - u0) / u0
            mass["%s_%s" % (tag, lv)] = d
            if d > reg["controls"]["C_MASS"]["floor"]:
                gate1_fail.append("%s %s: C_MASS |ubar/U0 - 1| %.3e > %.1e"
                                  % (tag, lv, d, reg["controls"]["C_MASS"]["floor"]))
    ident = {}
    for lv in LEVELS:
        d = abs(ts[lv]["fRe"] - qq[lv]["fRe"]) / abs(qq[lv]["fRe"])
        ident[lv] = d
        if d > reg["controls"]["C_ID"]["floor"]:
            gate1_fail.append("%s: C_ID f.Re differs between the two arms by %.3e > %.1e (beta = 0 makes "
                              "the hydrodynamics identical)" % (lv, d, reg["controls"]["C_ID"]["floor"]))
    gate1_ok = not gate1_fail
    gate1_why = "; ".join(gate1_fail)
    print("  gate (1): C_PLATEAU %s; C_SYM T %s; C_MASS %s; C_ID %s"
          % ("ok" if all(v["ok"] for v in itr.values()) else "FAILED",
             ", ".join("%s %.1e" % (lv, ts[lv]["symT"]) for lv in LEVELS),
             ", ".join("%s %.1e" % (k, v) for k, v in sorted(mass.items())),
             ", ".join("%s %.1e" % (lv, ident[lv]) for lv in LEVELS)))

    Cf = qq["f"]
    nyf, nxf = Cf["ny"], Cf["nx"]
    i0, i1 = Cf["i0"], Cf["i1"]
    # SIZED TO THE READER (L-340).  A UNIFORM plant across the whole station
    # column is INVISIBLE to the Nusselt reader by construction: Nu is built from
    # (T_wall - T_bulk), and a constant added to every cell in the column shifts
    # the wall value and the bulk mean by the same amount.  Measured: a whole-column
    # plant moved the read by 1.9e-13, i.e. round-off.  The plant therefore goes
    # into the SINGLE NEAR-WALL CELL at the downstream station column, located
    # structurally by index, where it moves the wall gradient without moving the
    # bulk mean by more than 1/ny of itself.
    st_idx = [0 * nxf + i1]
    pz = planted_zero_control(
        Cf["dir"], Cf["time"], "T", Cf["ncells"],
        (("Nu_H", lambda F: nu_at_column(column(F, nxf, nyf, i1), column(Cf["U"], nxf, nyf, i1),
                                         Cf["meta"], "q")[0], st_idx),))
    pzp = planted_zero_control(
        Cf["dir"], Cf["time"], "p_rgh", Cf["ncells"],
        (("fRe", lambda F: f_Re_from_pressure(F, [0.5 * (Cf["U"][j * nxf + i0] + Cf["U"][j * nxf + i1])
                                                  for j in range(nyf)], nxf, nyf, i0, i1, Cf["meta"])[0],
          [j * nxf + i1 for j in range(nyf)]),))
    pz.update(pzp)

    rows = []
    R = reg["graded_rows"]
    ROWS = (("G1", ref["fRe_plates"], {lv: qq[lv]["fRe"] for lv in LEVELS}),
            ("G2", ref["Nu_H_plates"], {lv: qq[lv]["Nu"] for lv in LEVELS}),
            ("G3", ref["Nu_T_plates"], {lv: ts[lv]["Nu"] for lv in LEVELS}))
    for rid, rf, vals in ROWS:
        tr = triple_of(vals)
        band = R[rid]["band_rel"]
        lo, hi = rf * (1 - band), rf * (1 + band)
        verdict, bv, note = apply_gate(vals["f"], lo, hi, tr, gate1_ok, gate1_why)
        rows.append(dict(row=rid, quantity=R[rid]["quantity"], reference=rf, band=[lo, hi],
                         value_fine=vals["f"], triple=dict(vals), triple_state=tr["state"],
                         observed_order=tr.get("order"), gci_pct=tr.get("GCI_pct"),
                         richardson_REPORTED_ONLY=tr.get("richardson"), band_verdict=bv,
                         verdict=verdict, note=note, rel_deviation=(vals["f"] - rf) / rf,
                         predicted_rel_deviation=R[rid].get("predicted_rel_deviation")))
        print("%-3s fine=%.8f ref=%.8f dev=%+.3e (predicted %+.3e) band=[%.6f, %.6f] "
              "triple=(%.8f, %.8f, %.8f) %s -> %s%s"
              % (rid, vals["f"], rf, (vals["f"] - rf) / rf,
                 R[rid].get("predicted_rel_deviation", float("nan")), lo, hi,
                 vals["c"], vals["m"], vals["f"], fmt_tr(tr), verdict, (" [" + note + "]") if note else ""))
    out = dict(rung="T19b",
               supersedes="T19",
               gate_source=dict(
                   path=REG_PATH, sha256=REG_SHA256,
                   note="T19's OWN frozen T19_registered.json, loaded by explicit path and pinned. "
                        "No gate, threshold, band, floor, cap or label is defined, copied or "
                        "re-derived by T19b; DEAD_LEVER_AUDIT.md 21.2 forbids moving one and none "
                        "moves. The repair is to the CASE (build_t19b.py drops residualControl)."),
               referent_source=dict(path=EXACT_PATH, sha256=EXACT_SHA256,
                                    note="T19's OWN frozen exact_t19.py, unmodified"),
               scope="FORCED CONVECTION, LAMINAR, 2-D: fully developed parallel-plate channel; "
                     "NOT turbulent, NOT 3-D, NOT conjugate; the entrance region is solved but not graded",
               ceiling="GATE REACHED at best -- the reference is EXACT/derived, so this rung scores V and "
                       "never P; it can never reach HOLDS",
               Re=float(Cf["meta"]["Re"]), Pr=float(Cf["meta"]["Pr"]),
               x_station=float(Cf["meta"]["x_station"]), x_plus=float(Cf["meta"]["x_plus"]),
               ny=nyv, refinement_ratio=REFINEMENT, dim=DIM, factor_of_safety=FS,
               floors=dict(STAGNANT_FLOOR=STAGNANT_FLOOR, P_MIN=P_MIN, source="scripts/roache_triple.py (imported)"),
               gate1=dict(ok=gate1_ok, why=gate1_why, plateau_and_residuals=itr, C_MASS=mass, C_ID=ident,
                          C_SYM={("%s_%s" % (t, lv)): dict(T=C["symT"], U=C["symU"])
                                 for lv in LEVELS for t, C in (("Ts", ts[lv]), ("q", qq[lv]))}),
               Nu_wall_asymmetry_REPORTED_ONLY={lv: dict(lo=qq[lv]["Nu_lo"], hi=qq[lv]["Nu_hi"]) for lv in LEVELS},
               fRe_wall_shear_route_REPORTED_ONLY={lv: qq[lv]["fRe_wall_shear_REPORTED"] for lv in LEVELS},
               planted_zero_controls=pz, rows=rows)
    json.dump(out, open(json_out, "w"), indent=2)
    print("wrote %s" % json_out)
    return EXIT_OK


# ---------------------------------------------------------------- selftest
def _wf(path, vals, vector=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if vector:
        body = "\n".join("(%.17g 0 0)" % v for v in vals)
        cls = "volVectorField"
    else:
        body = "\n".join("%.17g" % v for v in vals)
        cls = "volScalarField"
    open(path, "w").write("FoamFile{version 2.0; format ascii; class %s; object f;}\n"
                          "dimensions [0 0 0 0 0 0 0];\ninternalField   nonuniform List<x> \n%d\n(\n%s\n)\n;\n"
                          "boundaryField{}\n" % (cls, len(vals), body))


def _forge(root, name, nx, ny, arm, err=1.0, resid=1e-10, asym=0.0, bad_mass=0.0, drift=0.0):
    """A forged case carrying the EXACT fully developed profiles at cell centres
    plus an O(1/ny^2) perturbation on the pressure gradient."""
    import math
    d = os.path.join(root, name)
    os.makedirs(os.path.join(d, "0"), exist_ok=True)
    open(os.path.join(d, "0", "T"), "w").write("x")
    b, Dh, nu, Pr, Re = 0.02, 0.04, 1.5e-05, 0.71, 100.0
    U0 = Re * nu / Dh
    L, x_s = 30.0 * Dh, 20.0 * Dh
    dx, dy = L / nx, b / ny
    a = b / 2.0
    T_in, T_wall, g = 300.0, 400.0, 500.0
    open(os.path.join(d, "CASE.txt"), "w").write(
        "case=%s\nnx=%d\nny=%d\ncells=%d\ndx=%.17g\ndy=%.17g\nb_gap=%.17g\nDh=%.17g\nL=%.17g\n"
        "x_station=%.17g\nnu=%.17g\nPr=%.17g\nRe=%.17g\nU0=%.17g\nT_in=%.17g\nT_wall=%.17g\n"
        "dTdn_wall=%.17g\nendTime=30000\ndeltaT=1\nx_plus=%.17g\nranks=1\n"
        % (name, nx, ny, nx * ny, dx, dy, b, Dh, L, x_s, nu, Pr, Re, U0, T_in, T_wall, g,
           x_s / (Dh * Re * Pr)))
    yc = [(j + 0.5) * dy for j in range(ny)]
    xi = [abs(y - a) / a for y in yc]
    sgn = [(y - a) / a for y in yc]          # SIGNED, for the antisymmetry arm
    u = [U0 * EX.u_over_ubar(x, 0) for x in xi]
    # A REAL SOLVE CONSERVES MASS DISCRETELY: the cell-centre sum of u times dy is
    # exactly the inlet flux.  Sampling the CONTINUOUS parabola at cell centres does
    # not (the midpoint rule leaves 1/(2 ny^2), measured 1.25e-03 at ny = 20), so the
    # forge normalises -- otherwise the forge, not the comparator, would be what
    # C_MASS is measuring.
    scale = U0 / (sum(u) / ny)
    u = [v * scale * (1.0 + bad_mass) for v in u]
    # exact fully developed temperature shapes
    if arm == "q":
        # T(xi) = T_ref + (g a) * 1.5(xi^2/2 - xi^4/12) ... shape only; the constant is irrelevant
        Tv = [T_in + g * a * 1.5 * (x * x / 2.0 - x ** 4 / 12.0) + asym * sgn[j]
              for j, x in enumerate(xi)]
    else:
        M = 4000
        h = 1.0 / M
        xc = [(i + 0.5) * h for i in range(M)]
        U = [EX.u_over_ubar(x, 0) for x in xc]
        lo = [0.0] * M; di = [0.0] * M; up = [0.0] * M
        for i in range(M):
            left = 1.0 / h if i > 0 else 0.0
            right = (1.0 / h) if i < M - 1 else 1.0 / (0.5 * h)
            lo[i] = -left; up[i] = (-right if i < M - 1 else 0.0); di[i] = left + right
        v = [1.0] * M; lam = 0.0
        for _ in range(400):
            rhs = [U[i] * v[i] for i in range(M)]
            x = EX._thomas(lo, di, up, rhs)
            nrm = max(abs(t) for t in x)
            x = [t / nrm for t in x]
            nl = 1.0 / nrm
            if abs(nl - lam) <= 1e-15 * abs(nl):
                v = x; lam = nl; break
            v, lam = x, nl

        def psi(q):
            i = min(M - 2, max(0, int(q * M - 0.5)))
            s = (q - xc[i]) / (xc[i + 1] - xc[i])
            return v[i] + s * (v[i + 1] - v[i])
        amp = T_in - T_wall
        Tv = [T_wall + amp * psi(x) + asym * sgn[j] for j, x in enumerate(xi)]
    # pressure: exactly the gradient that makes f.Re = 96(1 + err/ny^2)
    ubar = sum(u) / ny
    fre_target = 96.0 * (1.0 + err / (ny * ny))
    fD = fre_target / (ubar * Dh / nu)
    dpdx = -fD * 0.5 * ubar * ubar / Dh
    P = [dpdx * ((i + 0.5) * dx) for j in range(ny) for i in range(nx)]
    T = [Tv[j] for j in range(ny) for i in range(nx)]
    Uf = [u[j] for j in range(ny) for i in range(nx)]
    for nm, vals, vec in (("T", T, False), ("p_rgh", P, False), ("U", Uf, True)):
        _wf(os.path.join(d, "30000", nm), vals, vec)
    # the PREVIOUS write, so the C_PLATEAU test has something to compare against.
    # `drift` scales the pressure field at 28000, which moves f.Re between writes.
    for nm, vals, vec in (("T", T, False), ("p_rgh", [v * (1.0 + drift) for v in P], False), ("U", Uf, True)):
        _wf(os.path.join(d, "28000", nm), vals, vec)
    open(os.path.join(d, "log.solve"), "w").write(
        "".join("Solving for Ux, Initial residual = 1e-3, Final residual = %g, No Iterations 5\n"
                "Solving for T, Initial residual = 1e-3, Final residual = %g, No Iterations 5\n"
                "Solving for p_rgh, Initial residual = 1e-3, Final residual = %g, No Iterations 5\n"
                "ExecutionTime = 1 s\n" % (resid, resid, resid) for _ in range(3)) + "End\n")
    open(os.path.join(root, "DONE.%s" % name), "w").write("done\n")


class _RootWatch(object):
    """S8b/S8c -- RULE 3 APPLIED TO THE SELFTEST ITSELF.

    Records every filesystem READ under `root` for the duration of the `with`
    block, by replacing the seven call routes through which this comparator can
    reach a run tree: builtins.open, os.listdir, os.scandir, os.path.isfile,
    os.path.isdir, os.path.exists and glob.glob.  Paths in `allow` are permitted
    and are not counted.  The originals are restored in __exit__, and nesting is
    LIFO-safe.

    A ZERO FROM THIS WATCHER IS NOT EVIDENCE UNTIL THE WATCHER HAS BEEN SHOWN
    ABLE TO SEE A NON-ZERO, so selftest() plants a deliberate read it must
    record, checks the record, and only then clears it.
    """

    def __init__(self, root, allow=()):
        self.root = os.path.abspath(root)
        self.allow = set(os.path.abspath(a) for a in allow)
        self.hits = []
        self._saved = None
        self._in = False

    def _note(self, p):
        if self._in:
            return
        self._in = True
        try:
            if isinstance(p, bytes):
                p = p.decode("utf-8", "replace")
            if not isinstance(p, str):
                p = os.fspath(p)
            ap = os.path.abspath(p)
            if (ap == self.root or ap.startswith(self.root + os.sep)) and ap not in self.allow:
                self.hits.append(ap)
        except Exception:
            pass
        finally:
            self._in = False

    def __enter__(self):
        import builtins
        import glob as _glob
        self._saved = (builtins.open, os.listdir, os.scandir, os.path.isfile,
                       os.path.isdir, os.path.exists, _glob.glob)
        w = self

        def wrap(fn):
            def g(path, *a, **k):
                if isinstance(path, (str, bytes)) or hasattr(path, "__fspath__"):
                    w._note(path)
                return fn(path, *a, **k)
            return g
        builtins.open = wrap(self._saved[0])
        os.listdir = wrap(self._saved[1])
        os.scandir = wrap(self._saved[2])
        os.path.isfile = wrap(self._saved[3])
        os.path.isdir = wrap(self._saved[4])
        os.path.exists = wrap(self._saved[5])
        _glob.glob = wrap(self._saved[6])
        return self

    def __exit__(self, *exc):
        import builtins
        import glob as _glob
        (builtins.open, os.listdir, os.scandir, os.path.isfile,
         os.path.isdir, os.path.exists, _glob.glob) = self._saved
        return False


def _here_refs_in_selftest(src=None):
    """S8d -- the SOURCE-LEVEL detector.  Counts references to the name `HERE`
    inside the selftest functions.  analyse_t19.py:691 held exactly ONE --
    `grade(HERE, ...)`, HERE being the LIVE T19_runs directory -- and that single
    reference is the whole defect T19b repairs.  The count must be 0 here, and
    selftest() drives this same function on a PLANTED source to show it returns
    a non-zero when the reference is present."""
    import ast as _a
    tree = _a.parse(src if src is not None else open(__file__).read())
    n = 0
    for node in _a.walk(tree):
        if isinstance(node, _a.FunctionDef) and node.name in ("_limbs", "selftest",
                                                              "_populate_run_root"):
            for sub in _a.walk(node):
                if isinstance(sub, _a.Name) and sub.id == "HERE":
                    n += 1
    return n


def _populate_run_root(root):
    """S8a pass B: a run root FULLY POPULATED at the registered ladder -- all six
    case directories, `0/`, the 28000 and 30000 writes, the three registered
    fields, log.solve, STATUS.<case> and DONE.<case>.  Nothing in the limb set is
    allowed to notice."""
    for lv, (nx, ny) in (("c", (120, 20)), ("m", (240, 40)), ("f", (480, 80))):
        for arm, pre in (("Ts", "P_Ts_"), ("q", "P_q_")):
            nm = pre + lv
            _forge(root, nm, nx, ny, arm)
            with open(os.path.join(root, "STATUS.%s" % nm), "w") as fh:
                fh.write("case=%s\nrc=0\nwall_s=1\nranks=1\ncore_min=0.017\nnote=synthetic\n" % nm)


def _limbs(reg, run_root):
    """THE WHOLE LIMB SET.  Every limb forges its own synthetic tree in a scratch
    directory it creates and removes.  `run_root` is handed in ONLY so that S8
    can MEASURE invariance: no limb may read, stat or glob it, and the two
    watchers plus _here_refs_in_selftest() enforce that rather than promise it.

    Returns the outcome structure S8a compares between the two passes: the list
    of failed limb labels, and the (exit code, verdict vector) of every forged
    grading run."""
    import ast
    fails = []
    probe = []
    fired = False
    tmpj = tempfile.mkdtemp(prefix="t19reg_")
    try:
        bad = dict(reg); bad["roache_floors"] = dict(reg["roache_floors"], P_MIN=0.5)
        json.dump(bad, open(os.path.join(tmpj, "T19_registered.json"), "w"))
        try:
            load_registered(tmpj)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
    finally:
        shutil.rmtree(tmpj, ignore_errors=True)
    print("  [%s] registered P_MIN mutated to 0.5 -> REFUSE" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("floors")
    ref = reg["graded_rows"]["G1"]["reference"]
    band = reg["graded_rows"]["G1"]["band_rel"]
    lo, hi = ref * (1 - band), ref * (1 + band)

    def ladder(p, e_f=0.002):
        return dict(f=ref + e_f, m=ref + e_f * 2 ** p, c=ref + e_f * 4 ** p)
    for label, vals, want, want_gci in (
            ("healthy p=2.000", ladder(2.0), "PASS", True),
            ("p=0.51 (just above STAGNANT_FLOOR)", ladder(0.51), "PASS", True),
            ("p=0.49 (just below STAGNANT_FLOOR) -> STAGNANT", ladder(0.49), "NOT A RESULT", False),
            ("p=0.01 (below P_MIN) -> DEGENERATE", ladder(0.01), "NOT A RESULT", False),
            ("oscillatory", dict(c=ref + 0.01, m=ref - 0.01, f=ref + 0.005), "NOT A RESULT", False),
            ("divergent", ladder(-1.0), "NOT A RESULT", False),
            ("exact (e21 = 0)", dict(c=ref, m=ref, f=ref), "NOT A RESULT", False),
            ("healthy p=2 but fine OUTSIDE the band", ladder(2.0, e_f=ref * band * 1.5), "GATE FAIL", True),
            ("gate (1) failed -> NOT A RESULT whatever the triple", ladder(2.0), "NOT A RESULT", True)):
        tr = triple_of(vals)
        g1ok = "gate (1)" not in label
        v, bv, note = apply_gate(vals["f"], lo, hi, tr, g1ok, "forced")
        ok = (v == want) and ((tr.get("GCI_pct") is not None) == want_gci)
        print("  [%s] %-52s %s -> %s" % ("ok " if ok else "FAIL", label, fmt_tr(tr), v))
        if not ok:
            fails.append(label)

    def run_forged(**kw):
        tmp = tempfile.mkdtemp(prefix="t19forge_")
        try:
            for lv, (nx, ny) in (("c", (120, 20)), ("m", (240, 40)), ("f", (480, 80))):
                _forge(tmp, "P_Ts_%s" % lv, nx, ny, "Ts", **kw)
                _forge(tmp, "P_q_%s" % lv, nx, ny, "q", **kw)
            out = os.path.join(tmp, "gate.json")
            code = None
            try:
                code = grade(tmp, out, reg, quiet_ref=True)
            except SystemExit as e:
                code = e.code
            res = json.load(open(out)) if os.path.isfile(out) else None
            return code, res
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    code, res = run_forged()
    probe.append(("value-control", code, [r["verdict"] for r in res["rows"]] if res else None))
    rows = {r["row"]: r for r in res["rows"]} if res else {}
    ok = (code == 0 and rows and all(rows[k]["verdict"] == "PASS" for k in ("G1", "G2", "G3"))
          and all(abs(rows[k]["observed_order"] - 2.0) < 0.2 for k in ("G1", "G2", "G3"))
          and all(v["status"] == "PASS" for v in res["planted_zero_controls"].values()))
    print("  [%s] VALUE CONTROL: the EXACT fully developed profiles on the registered ladder grade "
          "G1/G2/G3 PASS with p = %s / %s / %s; both planted controls PASS"
          % ("ok " if ok else "FAIL",
             *( ["%.3f" % rows[k]["observed_order"] for k in ("G1", "G2", "G3")] if rows else ["?"] * 3)))
    if not ok:
        fails.append("value-control")
    code, res = run_forged(drift=1e-3)
    probe.append(("plateau", code, [r["verdict"] for r in res["rows"]] if res else None))
    ok = (code == 0 and res and all(r["verdict"] == "NOT A RESULT" for r in res["rows"]))
    print("  [%s] C_PLATEAU broken (f.Re moved 1e-3 between the last two writes) -> gate (1) "
          "-> NOT A RESULT x3" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("plateau")
    code, res = run_forged(asym=1.0)
    probe.append(("sym", code, [r["verdict"] for r in res["rows"]] if res else None))
    ok = (code == 0 and res and all(r["verdict"] == "NOT A RESULT" for r in res["rows"]) and not res["gate1"]["ok"])
    print("  [%s] C_SYM broken (a field antisymmetric about the mid-plane) -> gate (1) -> NOT A RESULT x3"
          % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("sym")
    code, res = run_forged(bad_mass=1e-3)
    probe.append(("mass", code, [r["verdict"] for r in res["rows"]] if res else None))
    ok = (code == 0 and res and all(r["verdict"] == "NOT A RESULT" for r in res["rows"]))
    print("  [%s] C_MASS broken (bulk velocity 0.1 percent off U0) -> gate (1) -> NOT A RESULT x3"
          % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("mass")
    code, res = run_forged(err=30.0)
    probe.append(("gate-fail", code, [r["verdict"] for r in res["rows"]] if res else None))
    ok = (code == 0 and res and {r["row"]: r["verdict"] for r in res["rows"]}["G1"] == "GATE FAIL")
    print("  [%s] forged f.Re perturbation 30/ny^2 -> G1 outside its band -> GATE FAIL" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("gate-fail")
    # ------------------------------------------------------------------------
    # THE REPAIRED LIMB.  analyse_t19.py:691 read
    #     grade(HERE, os.path.join(tempfile.gettempdir(), "t19_never.json"), reg)
    # with HERE the LIVE T19_runs directory.  That limb passed only because no
    # DONE marker existed, and the day one did it would have driven the real
    # grading path across a live run tree as a side effect of a selftest.
    #
    # The replacement forges its own tree and is STRICTLY STRONGER than the
    # original: the six cases are fully readable and complete, and ONLY the DONE
    # markers are removed -- so the refusal is ATTRIBUTABLE to the DONE check
    # rather than to the absence of any case at all, which is all the parent's
    # empty live tree ever demonstrated.  It also asserts NO json was written.
    fired, wrote, ncases = False, True, 0
    tmp = tempfile.mkdtemp(prefix="t19b_nodone_")
    try:
        for lv, (nx, ny) in (("c", (120, 20)), ("m", (240, 40)), ("f", (480, 80))):
            _forge(tmp, "P_Ts_%s" % lv, nx, ny, "Ts")
            _forge(tmp, "P_q_%s" % lv, nx, ny, "q")
        for f in os.listdir(tmp):
            if f.startswith("DONE."):
                os.remove(os.path.join(tmp, f))
        ncases = len([f for f in os.listdir(tmp) if f.startswith("P_")])
        out = os.path.join(tmp, "t19b_never.json")
        try:
            grade(tmp, out, reg)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
        wrote = os.path.isfile(out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ok = fired and not wrote and ncases == 6
    print("  [%s] SYNTHETIC tree, %d complete cases but NO DONE markers -> exit 2 REFUSE and no "
          "gate json written (S8: no limb touches a live run tree)" % ("ok " if ok else "FAIL", ncases))
    if not ok:
        fails.append("no-DONE-refusal")
    probe.append(("no-DONE-refusal", fired, wrote, ncases))
    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count in this file = %d (counter sees a planted assert: %d)"
          % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")
    return dict(fails=fails, probe=probe)


def selftest():
    """S8, driven.  The limb set runs TWICE in one invocation against two
    synthetic run roots -- one EMPTY, one FULLY POPULATED -- under two filesystem
    watchers, and the two outcome structures must be byte-identical."""
    reg = load_registered()
    print("analyse_t19b selftest -- the limb set runs TWICE (S8: empty vs fully populated run "
          "root) and the two outcomes must be byte-identical:")
    results, watched = {}, {}
    for tag, populate in (("A/EMPTY-run-root", False), ("B/POPULATED-run-root", True)):
        rr = tempfile.mkdtemp(prefix="t19b_rr_")
        try:
            if populate:
                _populate_run_root(rr)
            npop = len(os.listdir(rr))
            print("-- pass %s (%d entries in the synthetic run root) --" % (tag, npop))
            with _RootWatch(PARENT, allow=(REG_PATH, EXACT_PATH)) as pw, _RootWatch(rr) as rw:
                # RULE 3.  Plant a read each watcher MUST see before its zero is
                # allowed to mean anything.  Both probe paths are chosen NOT to
                # exist, so nothing is learned about either tree -- only about
                # the watchers.
                os.path.isfile(os.path.join(rr, "DONE.PLANTED_PROBE_NOT_A_CASE"))
                os.path.isfile(os.path.join(PARENT, "P_q_c", "PLANTED_PROBE_NOT_A_FILE"))
                planted = (len(rw.hits), len(pw.hits))
                rw.hits, pw.hits = [], []
                res = _limbs(reg, rr)
            results[tag] = res
            watched[tag] = dict(planted=planted, rr_hits=sorted(set(rw.hits)),
                                parent_hits=sorted(set(pw.hits)), npop=npop)
        finally:
            shutil.rmtree(rr, ignore_errors=True)

    fails = list(results["A/EMPTY-run-root"]["fails"])
    for lbl in results["B/POPULATED-run-root"]["fails"]:
        if lbl not in fails:
            fails.append(lbl)
    print("S8 -- the invariance and access measurements:")

    a = json.dumps(results["A/EMPTY-run-root"], sort_keys=True)
    b = json.dumps(results["B/POPULATED-run-root"], sort_keys=True)
    ok = (a == b)
    print("  [%s] S8a INVARIANCE: the outcome structure over an EMPTY run root (0 entries) is "
          "BYTE-IDENTICAL to the one over a FULLY POPULATED run root (%d entries, six complete "
          "cases with DONE markers)" % ("ok " if ok else "FAIL", watched["B/POPULATED-run-root"]["npop"]))
    if not ok:
        fails.append("S8a-invariance")
        print("      A: %s\n      B: %s" % (a[:400], b[:400]))

    ok = all(watched[t]["planted"][0] >= 1 and watched[t]["planted"][1] >= 1 for t in watched)
    print("  [%s] S8b/S8c PLANTED CONTROL (rule 3): a deliberate read under each watched root was "
          "SEEN -- run-root watcher %s, T19_runs watcher %s (pass A); a zero from a watcher not "
          "shown able to see a non-zero would not be evidence"
          % ("ok " if ok else "FAIL", watched["A/EMPTY-run-root"]["planted"][0],
             watched["A/EMPTY-run-root"]["planted"][1]))
    if not ok:
        fails.append("S8-planted-control")

    ok = all(not watched[t]["rr_hits"] for t in watched)
    print("  [%s] S8b: NO limb read, listed or stat-ed the run root in either pass (%d + %d "
          "recorded reads)" % ("ok " if ok else "FAIL", len(watched["A/EMPTY-run-root"]["rr_hits"]),
                               len(watched["B/POPULATED-run-root"]["rr_hits"])))
    if not ok:
        fails.append("S8b-run-root-touched")
        print("      touched: %s" % watched["A/EMPTY-run-root"]["rr_hits"][:6])

    ok = all(not watched[t]["parent_hits"] for t in watched)
    print("  [%s] S8c: NO limb read anything under T19_runs beyond the two PINNED instruments -- "
          "the FALSIFICATION SPECIMEN (P_q_c/828, P_Ts_c/541) is measured untouched, not asserted "
          "untouched (%d recorded reads)"
          % ("ok " if ok else "FAIL", len(watched["A/EMPTY-run-root"]["parent_hits"])))
    if not ok:
        fails.append("S8c-parent-touched")
        print("      touched: %s" % watched["A/EMPTY-run-root"]["parent_hits"][:6])

    n_here = _here_refs_in_selftest()
    n_planted = _here_refs_in_selftest("def _limbs(reg, run_root):\n    return grade(HERE, run_root)\n")
    ok = (n_here == 0 and n_planted == 1)
    print("  [%s] S8d: `HERE` references inside the selftest functions = %d (the SAME detector on a "
          "planted `grade(HERE, ...)` source returns %d, so the zero is planted, not blind) -- "
          "analyse_t19.py:691 held exactly one" % ("ok " if ok else "FAIL", n_here, n_planted))
    if not ok:
        fails.append("S8d-here-detector")

    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--json", default=os.path.join(HERE, "gate_t19b.json"))
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return grade(a.root, a.json, load_registered())


if __name__ == "__main__":
    sys.exit(main())
