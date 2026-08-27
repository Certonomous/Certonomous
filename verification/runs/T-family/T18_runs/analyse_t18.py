#!/usr/bin/env python3
"""T18 -- the FROZEN comparator.  3-D transient conduction in a cube (T11c),
Bi = 1, Fo_end = 0.20, laplacianFoam, three levels N = 20/40/80 per half-side.

SOLID ONLY.  This rung earns `V` for 3-D TRANSIENT CONDUCTION and nothing else.
Its referent is EXACT, so under the upheld V/P ruling it can reach GATE REACHED
at best and can NEVER reach HOLDS: an analytic reference scores V, never P.

ROACHE FLOORS ARE IMPORTED (MESH_STANDARD.md section 10.5, chief ruling
01967a7b): STAGNANT_FLOOR and P_MIN come from scripts/roache_triple.py; this
file defines neither, the triple arithmetic is roache_triple.gci_equal, and the
registered JSON's copy of the floors must EQUAL the import or this REFUSES.

THE FINE VALUE IS GRADED, NEVER THE RICHARDSON EXTRAPOLATE.  The extrapolate is
carried in the JSON under the key `richardson_REPORTED_ONLY` and no verdict this
file emits is a function of it (the sign convention of the extrapolate is a known
live defect in this family, survivable only because it is display-only wherever
it lives; this comparator keeps it display-only).

L-342 FIELD CLASSES: this comparator refuses only on PHYSICS-CRITICAL facts
(DONE markers, the field on disk, the log's End line and residuals, the
registered specification and its own referent).  Infrastructure fields
(STATUS wall_s, capped, timeout_s, checkmesh_rc ...) are never read here.

NO `assert` (L-332).  Every refusal is sys.exit(2).  apply_gate() is the ONLY
function that writes a verdict, and it walks rule 5's order one way.

Exit: 0 graded, 2 REFUSAL.
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
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import exact_t18 as EX                                                  # noqa: E402
from roache_triple import STAGNANT_FLOOR, P_MIN, FS, gci_equal, PLANT   # noqa: E402

LEVELS = ("c", "m", "f")
CASES = {lv: "T18_CU_%s" % lv for lv in LEVELS}
CT_CASE = "T18_CU_f_CT"
REFINEMENT = 2.0
DIM = 3
EXIT_OK, EXIT_REFUSE = 0, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def load_registered(root=None):
    p = os.path.join(root or HERE, "T18_registered.json")
    if not os.path.isfile(p):
        refuse("no T18_registered.json -- the gate is not registered")
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


# ------------------------------------------------------------ THE READER
def read_field(case_dir, time, N):
    """THE PRODUCTION READER: a FLAT list of N^3 values of T at `time`, in
    blockMesh order (i fastest, then j, then k: index = k*N*N + j*N + i).
    Every graded number and the planted-zero control go through it."""
    p = os.path.join(case_dir, str(time), "T")
    if not os.path.isfile(p):
        return None
    txt = open(p).read()
    m = re.search(r"internalField\s+nonuniform[^(]*\(\s*(.*?)\n\)", txt, re.S)
    if not m:
        return None
    vals = [float(v) for v in m.group(1).split()]
    if len(vals) != N ** 3:
        refuse("%s holds %d values, registered N^3 = %d" % (p, len(vals), N ** 3))
    return vals


def idx(N, i, j, k):
    return k * N * N + j * N + i


def mean_of(F):
    """Arithmetic mean over cell centres.  The cells are equal in volume, so this
    is the volume mean of the DISCRETE field; against the CONTINUOUS mean it is
    the midpoint rule and carries its own O(1/N^2) error, which is COMPUTED and
    disclosed in the band ground (it is NOT mesh-independent)."""
    return sum(F) / len(F)


def _interp1(xs, th, x):
    if x <= xs[0]:
        s = (x - xs[0]) / (xs[1] - xs[0]); return th[0] + s * (th[1] - th[0])
    if x >= xs[-1]:
        s = (x - xs[-2]) / (xs[-1] - xs[-2]); return th[-2] + s * (th[-1] - th[-2])
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            s = (x - xs[i]) / (xs[i + 1] - xs[i]); return th[i] + s * (th[i + 1] - th[i])
    refuse("interpolation failed at %g" % x)


def theta_at(F, N, xs, ys, zs):
    """Separable linear interpolation (linear extrapolation past the last centre)
    to a FIXED (x*, y*, z*): the graded quantity is the same quantity on every
    level.  Interpolation error enters the triple and is disclosed."""
    cs = [(i + 0.5) / N for i in range(N)]
    line = []
    for k in range(N):
        col = []
        for j in range(N):
            col.append(_interp1(cs, [F[idx(N, i, j, k)] for i in range(N)], xs))
        line.append(_interp1(cs, col, ys))
    return _interp1(cs, line, zs)


def symmetry_witness(F, N):
    """The exact solution is invariant under any permutation of (x,y,z), and so
    is the discrete problem on this mesh.  W0 = the worst departure over the
    three transpositions -- a solver/reader sanity witness."""
    w = 0.0
    for i in range(N):
        for j in range(N):
            for k in range(N):
                a = F[idx(N, i, j, k)]
                w = max(w, abs(a - F[idx(N, j, i, k)]),
                        abs(a - F[idx(N, i, k, j)]),
                        abs(a - F[idx(N, k, j, i)]))
    return w


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
    """BOTH ARMS per reader, sized to the reader (L-340): POINT readers get a
    one-cell plant at the cell nearest their station (located by INDEX, never by
    value); the AVERAGING reader (G1, mean over N^3 cells) gets an ALL-CELL plant
    so the read moves by ~PLANT rather than PLANT/N^3.  Measured ladder.  Copies
    first; never writes into the case."""
    tmp = tempfile.mkdtemp(prefix="t18pz_")
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
            refuse("no DONE.%s -- the whole rung is graded or none of it is; mark_done_t18.py rules" % case)
    print("verifying the analytic reference before any comparison:")
    metas = {lv: case_meta(root, CASES[lv]) for lv in LEVELS}
    Bi = float(metas["f"]["Bi"]); Fo = float(metas["f"]["Fo_end"])
    for lv in LEVELS:
        if abs(float(metas[lv]["Bi"]) - Bi) > 0 or abs(float(metas[lv]["Fo_end"]) - Fo) > 1e-15:
            refuse("levels disagree on Bi/Fo_end: %s" % {k: (m["Bi"], m["Fo_end"]) for k, m in metas.items()})
        if abs(float(metas[lv]["valueFraction"]) - Bi / (Bi + 2.0 * int(metas[lv]["N"]))) > 1e-15:
            refuse("level %s valueFraction %s is not Bi/(Bi+2N) (L-341)" % (lv, metas[lv]["valueFraction"]))
    if abs(Bi - reg["physics"]["Bi"]) > 0 or abs(Fo - reg["physics"]["Fo_end"]) > 1e-15:
        refuse("case files (Bi=%g, Fo=%g) disagree with the registered physics %r" % (Bi, Fo, reg["physics"]))
    S = EX.verify(Bi, Fo)
    Ns = {lv: int(metas[lv]["N"]) for lv in LEVELS}
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
    w0 = {lv: symmetry_witness(fields[lv], Ns[lv]) for lv in LEVELS}
    w0_floor = reg["controls"]["W0"]["floor"]
    gate1_ok = all(tok[lv]["ok"] for lv in LEVELS) and all(w0[lv] <= w0_floor for lv in LEVELS)
    gate1_why = "; ".join([("%s: %s" % (lv, tok[lv]["why"])) for lv in LEVELS if not tok[lv]["ok"]] +
                          [("%s: W0 %.3e > %.1e" % (lv, w0[lv], w0_floor)) for lv in LEVELS if w0[lv] > w0_floor])
    print("  W0 permutation-symmetry witness: " + ", ".join("%s %.2e" % (lv, w0[lv]) for lv in LEVELS))

    Nf = Ns["f"]
    readers = (("G1", mean_of, list(range(Nf ** 3))),
               ("G2", lambda F: theta_at(F, Nf, 0.0, 0.0, 0.0), [idx(Nf, 0, 0, 0)]),
               ("G3", lambda F: theta_at(F, Nf, 1.0, 0.0, 0.0), [idx(Nf, Nf - 1, 0, 0)]))
    pz = planted_zero_control(dirs["f"], times["f"], Nf, readers)

    rows = []
    R = reg["graded_rows"]
    ROWS = (("G1", lambda F, N: mean_of(F), S.theta_mean(Fo)),
            ("G2", lambda F, N: theta_at(F, N, 0.0, 0.0, 0.0), S.theta(0.0, 0.0, 0.0, Fo)),
            ("G3", lambda F, N: theta_at(F, N, 1.0, 0.0, 0.0), S.theta(1.0, 0.0, 0.0, Fo)))
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
                         note=note, rel_deviation=(vals["f"] - ref) / ref))
        print("%-3s fine=%.10f ref=%.10f dev=%+.3e band=[%.7f, %.7f] triple=(%.8e, %.8e, %.8e) %s -> %s%s"
              % (rid, vals["f"], ref, (vals["f"] - ref) / ref, lo, hi, vals["c"], vals["m"], vals["f"],
                 fmt_tr(tr), verdict, (" [" + note + "]") if note else ""))
    ct_row = None
    if ct:
        d = os.path.join(root, CT_CASE)
        t = latest_time(d) if os.path.isdir(d) else None
        if t is not None and os.path.isfile(os.path.join(root, "DONE.%s" % CT_CASE)):
            Fct = read_field(d, t, Nf)
            g1 = rows[0]["value_fine"]
            ct_row = dict(case=CT_CASE, G1_fine=g1, G1_ct=mean_of(Fct), move_rel=(mean_of(Fct) - g1) / g1,
                          fraction_of_band=abs(mean_of(Fct) - g1) / (g1 * R["G1"]["band_rel"]))
            print("C-T temporal-bias control (REPORTED, never gated): G1 moves %+.3e relative = %.3f of the band"
                  % (ct_row["move_rel"], ct_row["fraction_of_band"]))
        else:
            print("C-T temporal-bias control: NOT RUN (no DONE.%s) -- REPORTED as absent, never gated" % CT_CASE)
    out = dict(rung="T18", scope="SOLID-ONLY 3-D transient conduction (T11c); NOT conjugate, NOT a flow case",
               ceiling="GATE REACHED at best -- the reference is EXACT, so this rung scores V and never P; "
                       "it can never reach HOLDS",
               Bi=Bi, Fo_end=Fo, N=Ns, refinement_ratio=REFINEMENT, dim=DIM, factor_of_safety=FS,
               floors=dict(STAGNANT_FLOOR=STAGNANT_FLOOR, P_MIN=P_MIN, source="scripts/roache_triple.py (imported)"),
               gate1=dict(ok=gate1_ok, why=gate1_why, time_integration=tok, W0=w0),
               planted_zero_controls=pz, rows=rows, C_T=ct_row)
    json.dump(out, open(json_out, "w"), indent=2)
    print("wrote %s" % json_out)
    return EXIT_OK


# ---------------------------------------------------------------- selftest
def _write_field(path, vals):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write("FoamFile{version 2.0; format ascii; class volScalarField; object T;}\n"
                          "dimensions [0 0 0 1 0 0 0];\ninternalField   nonuniform List<scalar> \n%d\n(\n%s\n)\n;\n"
                          "boundaryField{}\n" % (len(vals), "\n".join("%.17g" % v for v in vals)))


def _forge_case(root, lv, N, S, Fo, Bi, err=0.0, resid=1e-12, asym=0.0):
    """A forged level: the analytic field at cell centres plus a smooth
    second-order-shaped deviation err*(1+x*)(1+y*)(1+z*)/N^2 (so p = 2)."""
    case = "T18_CU_%s" % lv
    d = os.path.join(root, case)
    os.makedirs(os.path.join(d, "0"), exist_ok=True)
    open(os.path.join(d, "0", "T"), "w").write("x")
    open(os.path.join(d, "CASE.txt"), "w").write(
        "case=%s\nlevel=%s\nN=%d\ncells=%d\nBi=%g\nFo_end=%.17g\nvalueFraction=%.17g\nendTime=2\ndeltaT=0.0001\n"
        "ranks=1\ndecomposition=serial_1_rank_no_decomposition\n"
        % (case, lv, N, N ** 3, Bi, Fo, Bi / (Bi + 2.0 * N)))
    fv = [S.f((i + 0.5) / N, Fo) for i in range(N)]
    vals = []
    for k in range(N):
        zs = (k + 0.5) / N
        for j in range(N):
            ys = (j + 0.5) / N
            for i in range(N):
                xs = (i + 0.5) / N
                v = fv[i] * fv[j] * fv[k] * (1.0 + err * (1 + xs) * (1 + ys) * (1 + zs) / (N * N)) + asym * xs
                vals.append(v)
    _write_field(os.path.join(d, "2", "T"), vals)
    open(os.path.join(d, "log.solve"), "w").write(
        "".join("Solving for T, Initial residual = 1e-3, Final residual = %g, No Iterations 5\nExecutionTime = 1 s\n" % resid
                for _ in range(3)) + "End\n")
    open(os.path.join(root, "DONE.%s" % case), "w").write("done\n")


def selftest():
    import ast
    fails = []
    reg = load_registered()
    print("analyse_t18 selftest:")
    # (i) floors: a registered copy that differs from the import is refused
    fired = False
    tmpj = tempfile.mkdtemp(prefix="t18reg_")
    try:
        bad = dict(reg); bad["roache_floors"] = dict(reg["roache_floors"], P_MIN=0.5)
        json.dump(bad, open(os.path.join(tmpj, "T18_registered.json"), "w"))
        try:
            load_registered(tmpj)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
    finally:
        shutil.rmtree(tmpj, ignore_errors=True)
    print("  [%s] registered P_MIN mutated to 0.5 -> REFUSE (import %g / %g is the one number)"
          % ("ok " if fired else "FAIL", STAGNANT_FLOOR, P_MIN))
    if not fired:
        fails.append("floors")
    # (ii) rule 5 through apply_gate at the floors
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
    # (iii) the VALUE CONTROL on the REGISTERED ladder (20/40/80): a forged field
    # that is the analytic solution at cell centres must grade PASS with p = 2 --
    # the reader's own quadrature/interpolation error is part of the registered band.
    Bi, Fo = reg["physics"]["Bi"], reg["physics"]["Fo_end"]
    S = EX.verify(Bi, Fo, quiet=True)

    def run_forged(**kw):
        tmp = tempfile.mkdtemp(prefix="t18forge_")
        try:
            for lv, N in (("c", 20), ("m", 40), ("f", 80)):
                _forge_case(tmp, lv, N, S, Fo, Bi, **kw)
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
    code, res = run_forged(err=0.0)
    rows = {r["row"]: r for r in res["rows"]} if res else {}
    ok = (code == 0 and rows and all(rows[k]["verdict"] == "PASS" for k in ("G1", "G2", "G3"))
          and abs(rows["G1"]["observed_order"] - 2.0) < 5e-2
          and all(res["planted_zero_controls"][k]["status"] == "PASS" for k in ("G1", "G2", "G3")))
    print("  [%s] VALUE CONTROL: analytic field on the REGISTERED ladder grades G1/G2/G3 PASS, "
          "G1 p=%s; 3 planted controls PASS" % ("ok " if ok else "FAIL",
                                                ("%.4f" % rows["G1"]["observed_order"]) if rows else "?"))
    if not ok:
        fails.append("value-control")
    code, res = run_forged(resid=1e-8)
    ok = (code == 0 and res and all(r["verdict"] == "NOT A RESULT" for r in res["rows"]))
    print("  [%s] final residual 1e-8 > floor -> gate (1) -> NOT A RESULT x3" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("resid")
    code, res = run_forged(asym=1e-6)
    ok = (code == 0 and res and all(r["verdict"] == "NOT A RESULT" for r in res["rows"]) and not res["gate1"]["ok"])
    print("  [%s] permutation symmetry W0 broken by 1e-6 -> gate (1) -> NOT A RESULT x3" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("w0")
    code, res = run_forged(err=3.0)
    ok = (code == 0 and res and {r["row"]: r["verdict"] for r in res["rows"]}["G1"] == "GATE FAIL")
    print("  [%s] forged deviation 3.0/N^2 at f -> G1 outside its band -> GATE FAIL" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("gate-fail")
    # (iv) a BLIND reader must be refused by the planted-zero control
    global read_field
    real = read_field
    tmp = tempfile.mkdtemp(prefix="t18blind_")
    fired = False
    try:
        _forge_case(tmp, "f", 20, S, Fo, Bi)
        frozen = real(os.path.join(tmp, "T18_CU_f"), "2", 20)
        read_field = lambda d, t, N: frozen           # ignores the disk
        try:
            planted_zero_control(os.path.join(tmp, "T18_CU_f"), "2", 20,
                                 (("G1", mean_of, list(range(20 ** 3))),))
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
    finally:
        read_field = real
        shutil.rmtree(tmp, ignore_errors=True)
    print("  [%s] BLIND reader mutant (ignores the plant) -> planted-zero control REFUSES" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("blind")
    # (v) the live tree with no DONE markers refuses
    fired = False
    try:
        grade(HERE, os.path.join(tempfile.gettempdir(), "t18_never.json"), reg)
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
    ap.add_argument("--json", default=os.path.join(HERE, "gate_t18.json"))
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return grade(a.root, a.json, load_registered())


if __name__ == "__main__":
    sys.exit(main())
