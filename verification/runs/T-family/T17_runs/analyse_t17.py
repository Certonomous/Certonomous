#!/usr/bin/env python3
"""T17 -- the FROZEN comparator.  Axisymmetric transient conduction in a finite
cylinder (T11d), Bi = 1, Fo_end = 0.20, laplacianFoam on a 1-degree WEDGE,
three levels N = 50/100/200 in BOTH the radial and the axial direction.

SOLID ONLY.  This rung earns `V` for AXISYMMETRIC TRANSIENT CONDUCTION and
nothing else.  Its referent is EXACT, so under the upheld V/P ruling it can
reach GATE REACHED at best and can NEVER reach HOLDS.

THE GEOMETRY IS COMPUTED HERE INDEPENDENTLY OF build_t17.py and cross-checked
against the `analytic_*_volume` values that build wrote into CASE.txt and, for
the fine level, against checkMesh's own Total/Min/Max volume (control C_GEOM).
The radial cell centre is the ANNULAR SECTOR CENTROID, not (j+1/2)dr; the
volume-weighted mean of that centroid is exactly (2/3)R for every N, and the
naive centroid fails that identity by 1/(6N^2) -- the control discriminates.

ROACHE FLOORS ARE IMPORTED (MESH_STANDARD.md section 10.5, chief ruling
01967a7b): STAGNANT_FLOOR and P_MIN come from scripts/roache_triple.py.

THE FINE VALUE IS GRADED, NEVER THE RICHARDSON EXTRAPOLATE.  The extrapolate is
carried under `richardson_REPORTED_ONLY` and no verdict here is a function of it.

NO `assert` (L-332).  Every refusal is sys.exit(2).  apply_gate() is the ONLY
function that writes a verdict.

Exit: 0 graded, 2 REFUSAL.
"""
import argparse
import json
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import exact_t17 as EX                                                  # noqa: E402
from roache_triple import STAGNANT_FLOOR, P_MIN, FS, gci_equal, PLANT   # noqa: E402

LEVELS = ("c", "m", "f")
CASES = {lv: "T17_CY_%s" % lv for lv in LEVELS}
CT_CASE = "T17_CY_f_CT"
REFINEMENT = 2.0
DIM = 2
EXIT_OK, EXIT_REFUSE = 0, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def load_registered(root=None):
    p = os.path.join(root or HERE, "T17_registered.json")
    if not os.path.isfile(p):
        refuse("no T17_registered.json -- the gate is not registered")
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
    return dict(re.findall(r"^([A-Za-z_]+)=(.*)$", open(p).read(), re.M))


def latest_time(case_dir):
    ts = [t for t in os.listdir(case_dir) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) and float(t) > 0]
    return max(ts, key=float) if ts else None


# ------------------------------------------------------- INDEPENDENT geometry
def r_star(j, N):
    """r*/R of radial cell j: the exact annular-sector centroid, NOT (j+1/2)/N."""
    r1, r2 = float(j) / N, float(j + 1) / N
    return (2.0 / 3.0) * (r2 ** 3 - r1 ** 3) / (r2 ** 2 - r1 ** 2)


def weight(j, N):
    """Cell volume up to a constant: (r2^2 - r1^2), uniform in the axial index."""
    return ((j + 1.0) / N) ** 2 - (float(j) / N) ** 2


def z_star(i, N):
    return (i + 0.5) / N


def check_geometry(meta, N, deg, Rm, Hm, tol=1e-8):
    """C_GEOM: this file's own volume model against the numbers build_t17.py wrote
    (which were themselves checked against checkMesh's Total/Min/Max volume), and
    the (2/3)R centroid identity."""
    h = math.radians(deg / 2.0)
    k = math.sin(h) * math.cos(h) * (Hm / N) * Rm * Rm
    vols = [k * weight(j, N) for j in range(N)]
    got = (sum(vols) * N, min(vols), max(vols))
    want = (float(meta["analytic_total_volume"]), float(meta["analytic_min_volume"]),
            float(meta["analytic_max_volume"]))
    for name, g, w in zip(("total", "min", "max"), got, want):
        if abs(g - w) > tol * abs(w):
            refuse("C_GEOM: this comparator's %s cell volume %.17g disagrees with the case's "
                   "registered %.17g by %.3e relative (> %.1e) -- the two geometry models differ"
                   % (name, g, w, abs(g - w) / abs(w), tol))
    num = sum(weight(j, N) * r_star(j, N) for j in range(N))
    den = sum(weight(j, N) for j in range(N))
    if abs(num / den - 2.0 / 3.0) > 1e-14:
        refuse("C_GEOM: the volume-weighted mean of the radial cell centre is %.17g, not the exact "
               "2/3 -- the centroid model is wrong (the naive (j+1/2)dr fails this by 1/(6N^2))"
               % (num / den))
    return dict(total_volume=got[0], min_volume=got[1], max_volume=got[2],
                centroid_identity=num / den)


# ------------------------------------------------------------ THE READER
def read_field(case_dir, time, N):
    """THE PRODUCTION READER: a FLAT list of N*N values of T at `time`, in
    blockMesh order for `(N N 1)` -- AXIAL index i fastest, then RADIAL index j:
    index = j*N + i.  Every graded number and the planted-zero control go
    through it."""
    p = os.path.join(case_dir, str(time), "T")
    if not os.path.isfile(p):
        return None
    txt = open(p).read()
    m = re.search(r"internalField\s+nonuniform[^(]*\(\s*(.*?)\n\)", txt, re.S)
    if not m:
        return None
    vals = [float(v) for v in m.group(1).split()]
    if len(vals) != N * N:
        refuse("%s holds %d values, registered N*N = %d" % (p, len(vals), N * N))
    return vals


def idx(N, i, j):
    return j * N + i


def volume_mean(F, N):
    """VOLUME-weighted mean over the wedge: the weight depends on the radial index
    only.  A plain arithmetic mean would over-weight the axis and is NOT what this
    reader does."""
    tot = 0.0
    den = 0.0
    for j in range(N):
        w = weight(j, N)
        tot += w * sum(F[idx(N, i, j)] for i in range(N))
        den += w * N
    return tot / den


def _interp1(xs, th, x):
    if x <= xs[0]:
        s = (x - xs[0]) / (xs[1] - xs[0]); return th[0] + s * (th[1] - th[0])
    if x >= xs[-1]:
        s = (x - xs[-2]) / (xs[-1] - xs[-2]); return th[-2] + s * (th[-1] - th[-2])
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            s = (x - xs[i]) / (xs[i + 1] - xs[i]); return th[i] + s * (th[i + 1] - th[i])
    refuse("interpolation failed at %g" % x)


def theta_at(F, N, rs, zs):
    """Separable linear interpolation (linear extrapolation past the last centre)
    to a FIXED (r*, z*).  The radial stations are the NON-UNIFORM sector centroids;
    the axial stations are uniform.  Interpolation error enters the triple and is
    disclosed."""
    zc = [z_star(i, N) for i in range(N)]
    rc = [r_star(j, N) for j in range(N)]
    ring = [_interp1(zc, [F[idx(N, i, j)] for i in range(N)], zs) for j in range(N)]
    return _interp1(rc, ring, rs)


def monotonicity_witness(F, N):
    """W0.  At Fo = 0.20 with Bi = 1 the exact field is strictly decreasing in
    BOTH r and z (the first radial eigenvalue 1.2558 is below the first zero of
    J0, and the first axial eigenvalue 0.8603 is below pi/2), and so is the
    discrete field.  W0 is the worst INCREASE found; a positive value means the
    solver or the reader has produced a field the physics forbids."""
    w = 0.0
    for j in range(N):
        for i in range(N - 1):
            w = max(w, F[idx(N, i + 1, j)] - F[idx(N, i, j)])
    for j in range(N - 1):
        for i in range(N):
            w = max(w, F[idx(N, i, j + 1)] - F[idx(N, i, j)])
    return w


def separability_defect(F, N):
    """REPORTED, NEVER GATED.  The CONTINUOUS solution is exactly the product
    C(r*)P(z*); backward Euler on the coupled operator is not exactly separable,
    so this is a diagnostic of how far the discrete solution departs from a rank-1
    product, measured as max |F_ij F_kl - F_il F_kj| / F_max^2 over a coarse
    sample of index quadruples."""
    step = max(1, N // 8)
    ii = list(range(0, N, step))
    jj = list(range(0, N, step))
    fmax = max(F)
    w = 0.0
    for a in ii:
        for b in ii:
            for c in jj:
                for d in jj:
                    w = max(w, abs(F[idx(N, a, c)] * F[idx(N, b, d)] - F[idx(N, a, d)] * F[idx(N, b, c)]))
    return w / (fmax * fmax)


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


def planted_zero_control(case_dir, time, N, readers):
    """BOTH ARMS per reader, sized to the reader (L-340).  Copies first; never
    writes into the case."""
    tmp = tempfile.mkdtemp(prefix="t17pz_")
    try:
        dst = os.path.join(tmp, os.path.basename(case_dir))
        shutil.copytree(case_dir, dst, symlinks=True)
        if os.path.realpath(dst).startswith(os.path.realpath(case_dir)):
            refuse("planted-zero control: scratch copy resolved INSIDE the case tree")
        base = read_field(dst, time, N)
        if base is None:
            refuse("planted-zero control: the reader returned nothing on the unplanted copy")
        again = read_field(dst, time, N)
        dneg = max(abs(a - b) for a, b in zip(base, again))
        if dneg != 0.0:
            refuse("planted-zero control NEGATIVE ARM FAILED: %.17g on identical bytes -- the reader is NOISY" % dneg)
        p = os.path.join(dst, str(time), "T")
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
                got = read_field(dst, time, N)
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
            if seen[PLANT] < 0.1 * PLANT:
                refuse("planted-zero control %s: the registered plant %.6g moved the read by only %.3g "
                       "(< 0.1 x plant; L-340 sizing) while %.6g was visible" % (name, PLANT, seen[PLANT], floor))
            out[name] = dict(status="PASS", plant=PLANT, cells_planted=len(idxs), recovered=seen[PLANT],
                             negative_arm=dneg, demonstrated_detection_floor=floor,
                             ladder={("%g" % k): v for k, v in seen.items()})
            print("planted-zero control %-3s PASS: plant %.6g in %d cell(s), recovered %.6g, floor %.1g"
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


def time_integration_ok(case_dir, resid_floor):
    log = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(log):
        return False, None, "no log.solve"
    body = open(log, errors="replace").read()
    fin = [float(m) for m in re.findall(r"Solving for T,.*?Final residual = ([0-9.eE+-]+)", body)]
    if not fin:
        return False, None, "no T solves in log.solve"
    worst = max(fin)
    if not re.search(r"^End\s*$", body, re.M):
        return False, worst, "no End line"
    if worst > resid_floor:
        return False, worst, "worst final residual %.3e > %.1e" % (worst, resid_floor)
    return True, worst, ""


# ---------------------------------------------------------------- the grade
def grade(root, json_out, reg, ct=True):
    for lv, case in CASES.items():
        if not os.path.isfile(os.path.join(root, "DONE.%s" % case)):
            refuse("no DONE.%s -- the whole rung is graded or none of it is; mark_done_t17.py rules" % case)
    print("verifying the analytic reference and the geometry before any comparison:")
    metas = {lv: case_meta(root, CASES[lv]) for lv in LEVELS}
    Bi = float(metas["f"]["Bi"]); Fo = float(metas["f"]["Fo_end"])
    Ns = {lv: int(metas[lv]["N"]) for lv in LEVELS}
    geom = {}
    for lv in LEVELS:
        m = metas[lv]
        if abs(float(m["Bi"]) - Bi) > 0 or abs(float(m["Fo_end"]) - Fo) > 1e-15:
            refuse("levels disagree on Bi/Fo_end: %s" % {k: (v["Bi"], v["Fo_end"]) for k, v in metas.items()})
        N = Ns[lv]
        if abs(float(m["valueFraction_axial"]) - Bi / (Bi + 2.0 * N)) > 1e-15:
            refuse("level %s axial valueFraction %s is not Bi/(Bi+2N) (L-341)" % (lv, m["valueFraction_axial"]))
        if float(m["valueFraction_radial"]) >= float(m["valueFraction_axial"]):
            refuse("level %s radial valueFraction is not below the axial one -- the outermost sector "
                   "centroid must lie inside (N-1/2)dr" % lv)
        if abs(float(m["wedge_deg"]) - reg["physics"]["wedge_deg"]) > 1e-15:
            refuse("level %s wedge angle %s is not the registered %g" % (lv, m["wedge_deg"], reg["physics"]["wedge_deg"]))
        geom[lv] = check_geometry(m, N, float(m["wedge_deg"]), float(m["R"]), float(m["Hhalf"]))
    if abs(Bi - reg["physics"]["Bi"]) > 0 or abs(Fo - reg["physics"]["Fo_end"]) > 1e-15:
        refuse("case files (Bi=%g, Fo=%g) disagree with the registered physics %r" % (Bi, Fo, reg["physics"]))
    print("  C_GEOM: volume model agrees with the case's registered volumes; centroid identity %.17g"
          % geom["f"]["centroid_identity"])
    S = EX.verify(Bi, Fo)
    if not (Ns["m"] == 2 * Ns["c"] and Ns["f"] == 2 * Ns["m"]):
        refuse("the ladder is not r = 2: %r" % Ns)

    dirs, times, tok = {}, {}, {}
    for lv, case in CASES.items():
        d = os.path.join(root, case)
        t = latest_time(d)
        if t is None:
            refuse("%s has no time directory beyond 0" % case)
        dirs[lv], times[lv] = d, t
        ok, worst, why = time_integration_ok(d, reg["controls"]["C_CONV"]["floor"])
        tok[lv] = dict(ok=ok, worst_final_residual=worst, why=why)
        print("  level %s: reached endTime, every step converged: %s%s" % (lv, ok, "" if ok else " [" + why + "]"))
    fields = {}
    for lv in LEVELS:
        F = read_field(dirs[lv], times[lv], Ns[lv])
        if F is None:
            refuse("could not read T on level %s -- a missing number is not a zero" % lv)
        fields[lv] = F
    w0 = {lv: monotonicity_witness(fields[lv], Ns[lv]) for lv in LEVELS}
    w0_floor = reg["controls"]["W0"]["floor"]
    sep = {lv: separability_defect(fields[lv], Ns[lv]) for lv in LEVELS}
    gate1_ok = all(tok[lv]["ok"] for lv in LEVELS) and all(w0[lv] <= w0_floor for lv in LEVELS)
    gate1_why = "; ".join([("%s: %s" % (lv, tok[lv]["why"])) for lv in LEVELS if not tok[lv]["ok"]] +
                          [("%s: W0 %.3e > %.1e" % (lv, w0[lv], w0_floor)) for lv in LEVELS if w0[lv] > w0_floor])
    print("  W0 monotonicity witness (worst INCREASE): " + ", ".join("%s %.2e" % (lv, w0[lv]) for lv in LEVELS))
    print("  separability defect (REPORTED, never gated): " + ", ".join("%s %.2e" % (lv, sep[lv]) for lv in LEVELS))

    Nf = Ns["f"]
    readers = (("G1", lambda F: volume_mean(F, Nf), list(range(Nf * Nf))),
               ("G2", lambda F: theta_at(F, Nf, 0.0, 0.0), [idx(Nf, 0, 0)]),
               ("G3", lambda F: theta_at(F, Nf, 1.0, 0.0), [idx(Nf, 0, Nf - 1)]))
    pz = planted_zero_control(dirs["f"], times["f"], Nf, readers)

    rows = []
    R = reg["graded_rows"]
    ROWS = (("G1", lambda F, N: volume_mean(F, N), S.theta_mean(Fo)),
            ("G2", lambda F, N: theta_at(F, N, 0.0, 0.0), S.theta(0.0, 0.0, Fo)),
            ("G3", lambda F, N: theta_at(F, N, 1.0, 0.0), S.theta(1.0, 0.0, Fo)))
    for rid, fn, ref in ROWS:
        if abs(ref - R[rid]["reference"]) > 1e-9:
            refuse("%s: derived reference %.10f != registered %.10f" % (rid, ref, R[rid]["reference"]))
        vals = {lv: fn(fields[lv], Ns[lv]) for lv in LEVELS}
        tr = triple_of(vals)
        band = R[rid]["band_rel"]
        lo, hi = ref * (1 - band), ref * (1 + band)
        verdict, bv, note = apply_gate(vals["f"], lo, hi, tr, gate1_ok, gate1_why)
        rows.append(dict(row=rid, quantity=R[rid]["quantity"], reference=ref, band=[lo, hi],
                         value_fine=vals["f"], triple=dict(zip(LEVELS, (vals["c"], vals["m"], vals["f"]))),
                         triple_state=tr["state"], observed_order=tr.get("order"), gci_pct=tr.get("GCI_pct"),
                         richardson_REPORTED_ONLY=tr.get("richardson"), band_verdict=bv, verdict=verdict,
                         note=note, rel_deviation=(vals["f"] - ref) / ref,
                         predicted_rel_deviation=R[rid].get("predicted_rel_deviation")))
        print("%-3s fine=%.10f ref=%.10f dev=%+.3e (predicted %+.3e) band=[%.8f, %.8f] "
              "triple=(%.8e, %.8e, %.8e) %s -> %s%s"
              % (rid, vals["f"], ref, (vals["f"] - ref) / ref, R[rid].get("predicted_rel_deviation", float("nan")),
                 lo, hi, vals["c"], vals["m"], vals["f"], fmt_tr(tr), verdict, (" [" + note + "]") if note else ""))
    ct_row = None
    if ct:
        d = os.path.join(root, CT_CASE)
        t = latest_time(d) if os.path.isdir(d) else None
        if t is not None and os.path.isfile(os.path.join(root, "DONE.%s" % CT_CASE)):
            Fct = read_field(d, t, Nf)
            g1 = rows[0]["value_fine"]
            gct = volume_mean(Fct, Nf)
            ct_row = dict(case=CT_CASE, G1_fine=g1, G1_ct=gct, move_rel=(gct - g1) / g1,
                          fraction_of_band=abs(gct - g1) / (g1 * R["G1"]["band_rel"]))
            print("C-T temporal-bias control (REPORTED, never gated): G1 moves %+.3e relative = %.3f of the band"
                  % (ct_row["move_rel"], ct_row["fraction_of_band"]))
        else:
            print("C-T temporal-bias control: NOT RUN (no DONE.%s) -- REPORTED as absent, never gated" % CT_CASE)
    out = dict(rung="T17",
               scope="SOLID-ONLY axisymmetric transient conduction in a finite cylinder (T11d); NOT conjugate, "
                     "NOT a flow case",
               ceiling="GATE REACHED at best -- the reference is EXACT, so this rung scores V and never P; "
                       "it can never reach HOLDS",
               Bi=Bi, Fo_end=Fo, N=Ns, wedge_deg=reg["physics"]["wedge_deg"], refinement_ratio=REFINEMENT,
               dim=DIM, factor_of_safety=FS,
               floors=dict(STAGNANT_FLOOR=STAGNANT_FLOOR, P_MIN=P_MIN, source="scripts/roache_triple.py (imported)"),
               geometry=geom, gate1=dict(ok=gate1_ok, why=gate1_why, time_integration=tok, W0=w0),
               separability_defect_REPORTED_ONLY=sep, planted_zero_controls=pz, rows=rows, C_T=ct_row)
    json.dump(out, open(json_out, "w"), indent=2)
    print("wrote %s" % json_out)
    return EXIT_OK


# ---------------------------------------------------------------- selftest
def _write_field(path, vals):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write("FoamFile{version 2.0; format ascii; class volScalarField; object T;}\n"
                          "dimensions [0 0 0 1 0 0 0];\ninternalField   nonuniform List<scalar> \n%d\n(\n%s\n)\n;\n"
                          "boundaryField{}\n" % (len(vals), "\n".join("%.17g" % v for v in vals)))


def _forge_case(root, lv, N, S, Fo, Bi, deg, Rm, Hm, err=0.0, resid=1e-12, bump=0.0, wedge=1.0):
    """A forged level: the analytic field at the registered cell stations
    (radial factor optionally evaluated at wedge*Fo to emulate the wedge bias),
    plus a smooth second-order deviation err*(1+r*)(1+z*)/N^2."""
    case = "T17_CY_%s" % lv
    d = os.path.join(root, case)
    os.makedirs(os.path.join(d, "0"), exist_ok=True)
    open(os.path.join(d, "0", "T"), "w").write("x")
    h = math.radians(deg / 2.0)
    k = math.sin(h) * math.cos(h) * (Hm / N) * Rm * Rm
    vols = [k * weight(j, N) for j in range(N)]
    open(os.path.join(d, "CASE.txt"), "w").write(
        "case=%s\nlevel=%s\nN=%d\ncells=%d\nBi=%g\nFo_end=%.17g\n"
        "valueFraction_axial=%.17g\nvalueFraction_radial=%.17g\nwedge_deg=%.17g\nR=%.17g\nHhalf=%.17g\n"
        "analytic_total_volume=%.17g\nanalytic_min_volume=%.17g\nanalytic_max_volume=%.17g\n"
        "endTime=2\ndeltaT=0.0001\nranks=1\ndecomposition=serial_1_rank_no_decomposition\n"
        % (case, lv, N, N * N, Bi, Fo, Bi / (Bi + 2.0 * N), 0.99 * Bi / (Bi + 2.0 * N), deg, Rm, Hm,
           sum(vols) * N, min(vols), max(vols)))
    Cv = [S.C(r_star(j, N), wedge * Fo) for j in range(N)]
    Pv = [S.P(z_star(i, N), Fo) for i in range(N)]
    vals = []
    for j in range(N):
        rs = r_star(j, N)
        for i in range(N):
            zs = z_star(i, N)
            vals.append(Cv[j] * Pv[i] * (1.0 + err * (1 + rs) * (1 + zs) / (N * N)) + bump * (rs * zs) ** 2)
    _write_field(os.path.join(d, "2", "T"), vals)
    open(os.path.join(d, "log.solve"), "w").write(
        "".join("Solving for T, Initial residual = 1e-3, Final residual = %g, No Iterations 5\nExecutionTime = 1 s\n" % resid
                for _ in range(3)) + "End\n")
    open(os.path.join(root, "DONE.%s" % case), "w").write("done\n")


def selftest():
    import ast
    fails = []
    reg = load_registered()
    print("analyse_t17 selftest:")
    fired = False
    tmpj = tempfile.mkdtemp(prefix="t17reg_")
    try:
        bad = dict(reg); bad["roache_floors"] = dict(reg["roache_floors"], P_MIN=0.5)
        json.dump(bad, open(os.path.join(tmpj, "T17_registered.json"), "w"))
        try:
            load_registered(tmpj)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
    finally:
        shutil.rmtree(tmpj, ignore_errors=True)
    print("  [%s] registered P_MIN mutated to 0.5 -> REFUSE" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("floors")
    # geometry: the naive centroid must be refused by C_GEOM's identity clause
    global r_star
    real_rstar = r_star
    fired = False
    try:
        r_star = lambda j, N: (j + 0.5) / N
        check_geometry(dict(analytic_total_volume="1", analytic_min_volume="1", analytic_max_volume="1"),
                       50, 1.0, 0.01, 0.01, tol=1e30)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    finally:
        r_star = real_rstar
    print("  [%s] NAIVE radial centroid (j+1/2)dr -> C_GEOM identity REFUSES" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("geom")
    # rule 5 through apply_gate at the floors
    ref = reg["graded_rows"]["G1"]["reference"]
    band = reg["graded_rows"]["G1"]["band_rel"]
    lo, hi = ref * (1 - band), ref * (1 + band)

    def ladder(p, e_f=2e-6):
        return dict(f=ref + e_f, m=ref + e_f * 2 ** p, c=ref + e_f * 4 ** p)
    for label, vals, want, want_gci in (
            ("healthy p=2.000", ladder(2.0), "PASS", True),
            ("p=0.51 (just above STAGNANT_FLOOR)", ladder(0.51), "PASS", True),
            ("p=0.49 (just below STAGNANT_FLOOR) -> STAGNANT", ladder(0.49), "NOT A RESULT", False),
            ("p=0.01 (below P_MIN) -> DEGENERATE", ladder(0.01), "NOT A RESULT", False),
            ("oscillatory", dict(c=ref + 1e-5, m=ref - 1e-5, f=ref + 5e-6), "NOT A RESULT", False),
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
    Bi, Fo = reg["physics"]["Bi"], reg["physics"]["Fo_end"]
    deg, Rm, Hm = reg["physics"]["wedge_deg"], reg["physics"]["R_m"], reg["physics"]["H_half_m"]
    S = EX.verify(Bi, Fo, quiet=True)
    wedge_bias = 1.0 / math.cos(math.radians(deg / 2.0)) ** 2

    def run_forged(**kw):
        tmp = tempfile.mkdtemp(prefix="t17forge_")
        try:
            for lv, N in (("c", 50), ("m", 100), ("f", 200)):
                _forge_case(tmp, lv, N, S, Fo, Bi, deg, Rm, Hm, **kw)
            out = os.path.join(tmp, "gate.json")
            code = None
            try:
                code = grade(tmp, out, reg)
            except SystemExit as e:
                code = e.code
            res = json.load(open(out)) if os.path.isfile(out) else None
            return code, res
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    # THE VALUE CONTROL: the analytic field at the registered stations, with the
    # radial factor carrying the registered sec^2(h) wedge bias -- exactly the
    # field this registration PREDICTS -- must grade PASS x3 with p = 2.
    code, res = run_forged(wedge=wedge_bias)
    rows = {r["row"]: r for r in res["rows"]} if res else {}
    ok = (code == 0 and rows and all(rows[k]["verdict"] == "PASS" for k in ("G1", "G2", "G3"))
          and abs(rows["G1"]["observed_order"] - 2.0) < 0.15
          and all(res["planted_zero_controls"][k]["status"] == "PASS" for k in ("G1", "G2", "G3")))
    print("  [%s] VALUE CONTROL: the PREDICTED field (analytic + sec^2(h) radial bias) on the registered "
          "ladder grades G1/G2/G3 PASS, G1 p=%s; 3 planted controls PASS"
          % ("ok " if ok else "FAIL", ("%.4f" % rows["G1"]["observed_order"]) if rows else "?"))
    if not ok:
        fails.append("value-control")
    # the NO-BIAS field (P5 loses) must still be inside every band -- the bands
    # were sized to survive that, and this control proves it rather than asserting it
    code, res = run_forged(wedge=1.0)
    rows2 = {r["row"]: r for r in res["rows"]} if res else {}
    ok = (code == 0 and rows2 and all(rows2[k]["verdict"] == "PASS" for k in ("G1", "G2", "G3")))
    print("  [%s] P5-LOSES CONTROL: the same field with NO wedge bias also grades PASS x3 "
          "(the bands survive the prediction being wrong)" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("p5-loses")
    code, res = run_forged(wedge=wedge_bias, resid=1e-8)
    ok = (code == 0 and res and all(r["verdict"] == "NOT A RESULT" for r in res["rows"]))
    print("  [%s] final residual 1e-8 > floor -> gate (1) -> NOT A RESULT x3" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("resid")
    code, res = run_forged(wedge=wedge_bias, bump=1.0)
    ok = (code == 0 and res and all(r["verdict"] == "NOT A RESULT" for r in res["rows"]) and not res["gate1"]["ok"])
    print("  [%s] a field increasing with r and z (monotonicity broken) -> gate (1) -> NOT A RESULT x3"
          % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("w0")
    code, res = run_forged(wedge=wedge_bias, err=6.0)
    ok = (code == 0 and res and {r["row"]: r["verdict"] for r in res["rows"]}["G1"] == "GATE FAIL")
    print("  [%s] forged deviation 6.0/N^2 at f -> G1 outside its band -> GATE FAIL" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("gate-fail")
    global read_field
    real = read_field
    tmp = tempfile.mkdtemp(prefix="t17blind_")
    fired = False
    try:
        _forge_case(tmp, "f", 50, S, Fo, Bi, deg, Rm, Hm)
        frozen = real(os.path.join(tmp, "T17_CY_f"), "2", 50)
        read_field = lambda d, t, N: frozen
        try:
            planted_zero_control(os.path.join(tmp, "T17_CY_f"), "2", 50,
                                 (("G1", lambda F: volume_mean(F, 50), list(range(2500))),))
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
    finally:
        read_field = real
        shutil.rmtree(tmp, ignore_errors=True)
    print("  [%s] BLIND reader mutant -> planted-zero control REFUSES" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("blind")
    fired = False
    try:
        grade(HERE, os.path.join(tempfile.gettempdir(), "t17_never.json"), reg)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] live tree, no DONE markers -> exit 2 REFUSE" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("live")
    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count in this file = %d (counter sees a planted assert: %d)"
          % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--json", default=os.path.join(HERE, "gate_t17.json"))
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return grade(a.root, a.json, load_registered())


if __name__ == "__main__":
    sys.exit(main())
