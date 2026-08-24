#!/usr/bin/env python3
"""
E4a comparator: fanPressure BC verification, exact operating-point class.

WHAT THIS FILE GRADES
---------------------
Every verdict is PASS or GATE FAIL against a prediction registered in
E4a_registered.json, written before any case directory existed.  A row whose
grid triple is not CONVERGING is NOT A RESULT (rule 5) and no GCI is quoted
on non-monotone values.  A case whose last two written checkpoints are not
value-for-value identical is not converged: every row that needs it is
NOT A RESULT (rule 5 order (1)).

THE IDENTITY (Charter 2a), from the ESI v2606 source, file:line
---------------------------------------------------------------
fanPressureFvPatchScalarField.cxx: dir = 2*direction-1 (:144, 'in' -> -1);
volFlowRate = dir*gSum(phip) on the volumetric branch (:149-151);
pdFan = fanCurve_->value(max(volFlowRate, 0)) (:189);
parent updateCoeffs(p0() - dir*pdFan, Up) (:201-205).
totalPressureFvPatchScalarField.cxx:191 (incompressible branch, p in m2/s2):
    p_f == p0p - 0.5*neg(phi_f)*|U_f|^2,   neg(s) = (s<0) ? 1 : 0
                                           (scalarImpl.H:262).
So at the final checkpoint, per fan-patch face:
    p_f = p0_env + dp(max(-sum(phi_fan),0)) - 0.5*neg(phi_f)*|U_f|^2
and this comparator evaluates the REGISTERED polynomial at the MEASURED patch
flow rate and compares to the MEASURED patch pressure, face by face.

FROZEN IMPORTS
--------------
T1_runs/analyse_t1c.py (gci: Fs 1.25, module nominal r 1.6).  Imported,
never copied, never edited; sha256 printed at every run.  Its R_REFINE is
redirected to the registered r = 1.5 IN THIS PROCESS ONLY by the restoring
context manager `with_ratio` (T10aR in_tree precedent); the selftest proves
restoration.  Its `richardson` carries the sign defect T9a s8.1 recorded;
the corrected form is a NEW INSTRUMENT here, both are printed side by side,
and no case-row verdict is a function of either (row D1 is a registered
prediction about the corrected diagnostic, T10aR RX5 class).

Exit codes: 0 every registered prediction met; 1 at least one GATE FAIL or
NOT A RESULT; 2 refusal.  This file refuses rather than degrades.
"""
import hashlib
import json
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
T1_DIR = os.path.join(os.path.dirname(HERE), "T1_runs")
sys.path.insert(0, T1_DIR)
import analyse_t1c as T1C                                  # noqa: E402 FROZEN

REG = json.load(open(os.path.join(HERE, "E4a_registered.json")))
ROWS = REG["rows"]
CASES = REG["cases"]
CURVES = REG["curves"]
PATCH = REG["patches"]
FS, R_REFINE = REG["grid"]["Fs"], REG["grid"]["r"]
END_TIME = REG["time"]["endTime"]
PLANT = REG["planted_control"]

PASS, GATE_REACHED, GATE_FAIL = "PASS", "GATE REACHED", "GATE FAIL"
NOT_A_RESULT, BLOCKED, PENDING = "NOT A RESULT", "BLOCKED", "PENDING"
EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

INSTRUMENTS = ("analyse_e4a.py", "E4a_registered.json", "build_e4a.py",
               "mark_done_e4a.py", "run_one_e4a.sh", "launch_e4a.sh")


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def provenance():
    print("provenance sha256 of every instrument this comparator uses:")
    for name in INSTRUMENTS:
        p = os.path.join(HERE, name)
        print(f"  {sha256_of(p)}  E4_runs/{name}")
    p = os.path.join(T1_DIR, "analyse_t1c.py")
    print(f"  {sha256_of(p)}  T1_runs/analyse_t1c.py (FROZEN import)")


# ---------------------------------------------------------------------------
# frozen-instrument contract, and the declared in-process ratio redirect
# ---------------------------------------------------------------------------
def frozen_contract():
    if T1C.FS != 1.25:
        refuse(f"frozen analyse_t1c.FS is {T1C.FS}, not 1.25")
    if T1C.R_REFINE != REG["grid"]["frozen_module_r"]:
        refuse(f"frozen analyse_t1c.R_REFINE is {T1C.R_REFINE}, not the "
               f"registered frozen_module_r {REG['grid']['frozen_module_r']}")


class with_ratio:
    """Redirect the frozen module's R_REFINE to the registered r for one
    call, restoring on exit.  The frozen FILE is never modified; only this
    process's imported module object, and only inside the `with`."""

    def __init__(self, r):
        self.r = r

    def __enter__(self):
        self.old = T1C.R_REFINE
        T1C.R_REFINE = self.r
        return self

    def __exit__(self, *a):
        T1C.R_REFINE = self.old
        return False


# ---------------------------------------------------------------------------
# NEW INSTRUMENT: sign-corrected Richardson (reported; graded only as D1's
# registered prediction-about-a-diagnostic, T10aR RX5 class)
# ---------------------------------------------------------------------------
def richardson_corrected(f_c, f_m, f_f, r):
    e21 = f_m - f_f
    e32 = f_c - f_m
    if e21 == 0.0 or e32 / e21 <= 0.0:
        return None
    p = math.log(abs(e32 / e21)) / math.log(r)
    if p <= 0.0:
        return None
    return f_f + (f_f - f_m) / (r ** p - 1.0)


# ---------------------------------------------------------------------------
# readers (the planted-zero control exercises exactly these)
# ---------------------------------------------------------------------------
FLOAT = r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?"


def _text(path):
    try:
        return open(path).read()
    except OSError as e:
        refuse(f"cannot read {path}: {e}")


def _block(txt, key):
    """Return the { } block following `key` at any depth (first match)."""
    m = re.search(r"\b" + re.escape(key) + r"\b", txt)
    if not m:
        return None
    i = txt.find("{", m.end())
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(txt)):
        if txt[j] == "{":
            depth += 1
        elif txt[j] == "}":
            depth -= 1
            if depth == 0:
                return txt[i + 1:j]
    return None


def _patch_block_opt(txt, patch):
    b = _block(txt, "boundaryField")
    if b is None:
        refuse("no boundaryField block")
    return _block(b, patch)


def _patch_block(txt, patch):
    pb = _patch_block_opt(txt, patch)
    if pb is None:
        refuse(f"no patch block '{patch}' in boundaryField")
    return pb


def _parse_value(block, want, nfaces=None):
    """Parse a 'value' entry.  want is 'scalar' or 'vector'.  Returns a list
    (vectors as 3-tuples).  A uniform entry needs nfaces to expand."""
    m = re.search(r"value\s+nonuniform\s+List<(scalar|vector)>\s*(\d+)\s*\(",
                  block)
    if m:
        if m.group(1) != want:
            refuse(f"value list is {m.group(1)}, expected {want}")
        n = int(m.group(2))
        body = block[m.end():]
        end = body.find(")") if want == "scalar" else None
        if want == "scalar":
            vals = [float(x) for x in re.findall(FLOAT, body[:end])]
        else:
            # vectors: take n '(x y z)' groups
            vals = []
            for g3 in re.finditer(r"\(\s*(" + FLOAT + r")\s+(" + FLOAT +
                                  r")\s+(" + FLOAT + r")\s*\)", body):
                vals.append(tuple(float(g3.group(k)) for k in (1, 2, 3)))
                if len(vals) == n:
                    break
        if len(vals) != n:
            refuse(f"value list declares {n} entries, parsed {len(vals)}")
        return vals
    m = re.search(r"value\s+uniform\s+\(\s*(" + FLOAT + r")\s+(" + FLOAT +
                  r")\s+(" + FLOAT + r")\s*\)\s*;", block)
    if m and want == "vector":
        if nfaces is None:
            refuse("uniform vector value needs the patch face count")
        v = tuple(float(m.group(k)) for k in (1, 2, 3))
        return [v] * nfaces
    m = re.search(r"value\s+uniform\s+(" + FLOAT + r")\s*;", block)
    if m and want == "scalar":
        if nfaces is None:
            refuse("uniform scalar value needs the patch face count")
        return [float(m.group(1))] * nfaces
    refuse(f"no parseable {want} 'value' entry in patch block")


def patch_values(field_path, patch, want, nfaces=None):
    return _parse_value(_patch_block(_text(field_path), patch), want, nfaces)


def internal_values(field_path, want):
    txt = _text(field_path)
    m = re.search(r"internalField\s+nonuniform\s+List<(scalar|vector)>\s*"
                  r"(\d+)\s*\(", txt)
    if m:
        n = int(m.group(2))
        body = txt[m.end():]
        if want == "scalar":
            end = body.find(")")
            vals = [float(x) for x in re.findall(FLOAT, body[:end])]
        else:
            vals = []
            for g3 in re.finditer(r"\(\s*(" + FLOAT + r")\s+(" + FLOAT +
                                  r")\s+(" + FLOAT + r")\s*\)", body):
                vals.append(tuple(float(g3.group(k)) for k in (1, 2, 3)))
                if len(vals) == n:
                    break
        if len(vals) != n:
            refuse(f"internalField declares {n}, parsed {len(vals)}")
        return vals
    m = re.search(r"internalField\s+uniform\s+", txt)
    if m:
        return "uniform"          # sufficient for equality comparison
    refuse(f"no parseable internalField in {field_path}")


def boundary_nfaces(case_dir):
    txt = _text(os.path.join(case_dir, "constant", "polyMesh", "boundary"))
    out = {}
    for m in re.finditer(r"(\w+)\s*\{([^{}]*)\}", txt):
        nm = re.search(r"nFaces\s+(\d+)\s*;", m.group(2))
        if nm:
            out[m.group(1)] = int(nm.group(1))
    if not out:
        refuse(f"no patches parsed from {case_dir}/constant/polyMesh/boundary")
    return out


def mesh_readback(name):
    """Refuse unless the built mesh is the registered one: patch face counts
    and domain extents (to 1e-12)."""
    spec = CASES[name]
    d = os.path.join(HERE, name)
    nf = boundary_nfaces(d)
    want = {PATCH["fan"]: spec["ny"], PATCH["outlet"]: spec["ny"],
            PATCH["walls"]: 2 * spec["nx"],
            PATCH["empty"]: 2 * spec["nx"] * spec["ny"]}
    for p, n in want.items():
        if nf.get(p) != n:
            refuse(f"{name}: patch {p} has {nf.get(p)} faces, registered {n}")
    txt = _text(os.path.join(d, "constant", "polyMesh", "points"))
    pts = re.findall(r"\(\s*(" + FLOAT + r")\s+(" + FLOAT + r")\s+(" + FLOAT
                     + r")\s*\)", txt)
    if not pts:
        refuse(f"{name}: no points parsed")
    xs = [float(p[0]) for p in pts]
    ys = [float(p[1]) for p in pts]
    zs = [float(p[2]) for p in pts]
    G = REG["geometry"]
    for got, wantv, ax in ((min(xs), 0.0, "x0"), (max(xs), G["L"], "x1"),
                           (min(ys), 0.0, "y0"), (max(ys), G["h"], "y1"),
                           (min(zs), 0.0, "z0"), (max(zs), G["t"], "z1")):
        if abs(got - wantv) > 1e-12:
            refuse(f"{name}: extent {ax} = {got!r}, registered {wantv!r}")


# ---------------------------------------------------------------------------
# registered physics
# ---------------------------------------------------------------------------
def curve_dp(curve_name, Q):
    """Replicates Function1Types::Polynomial::value (PolynomialEntry.C:147-160,
    y = sum coeff*x^exp) composed with fanPressure's max(Q,0) clamp
    (fanPressureFvPatchScalarField.cxx:189)."""
    x = max(Q, 0.0)
    return sum(c * x ** e for c, e in CURVES[curve_name]["coeffs"])


def exact_operating_point(curve_name):
    """Intersection of the registered curve with exact plane Poiseuille:
    k2 Q^2 + R Q - (p0_env + c0 - p_out) = 0 (registered arithmetic)."""
    c = CURVES[curve_name]
    coeffs = dict((int(e), v) for v, e in c["coeffs"])
    c0, k2 = coeffs.get(0, 0.0), -coeffs.get(2, 0.0)
    drive = c["p0_env"] + c0 - REG["p_out"]
    R = REG["R_exact"]
    if k2 == 0.0:
        return drive / R
    disc = R * R + 4.0 * k2 * drive
    return (-R + math.sqrt(disc)) / (2.0 * k2)


def identity_I1(p_faces, u_faces, phi_faces, curve_name, p0_env):
    """Max per-face residual of the BC's own assignment, plus Q and the
    outflow-face count.  Pure function so the selftest can mutate inputs."""
    Q = -sum(phi_faces)
    pd = curve_dp(curve_name, Q)
    worst = 0.0
    n_out = 0
    for pf, uf, ph in zip(p_faces, u_faces, phi_faces):
        neg = 1.0 if ph < 0.0 else 0.0
        n_out += 0 if ph < 0.0 else 1
        model = p0_env + pd - 0.5 * neg * (uf[0] ** 2 + uf[1] ** 2
                                           + uf[2] ** 2)
        worst = max(worst, abs(pf - model))
    return worst, Q, n_out


def grade_interval(value, lo, hi):
    if lo <= value <= hi:
        return PASS, ""
    return GATE_FAIL, ("high" if value > hi else "low")


def grade_triple(Qc, Qm, Qf, converged=(True, True, True)):
    """Rule 5, in its order.  The gate can only turn PASS/GATE FAIL into
    NOT A RESULT, never the reverse."""
    if not all(converged):
        return dict(verdict=NOT_A_RESULT,
                    reason="a level is not iteratively converged/plateaued",
                    triple=(Qc, Qm, Qf))
    with with_ratio(R_REFINE):
        g = T1C.gci(Qc, Qm, Qf)
    if g.get("state") != "CONVERGING":
        return dict(verdict=NOT_A_RESULT, reason=f"triple {g.get('state')}",
                    triple=(Qc, Qm, Qf), order=g.get("order"))
    lo, hi = ROWS["R1"]["interval"]
    v, side = grade_interval(g["order"], lo, hi)
    return dict(verdict=v, side=side, order=g["order"],
                GCI_pct=g["GCI_pct"], richardson_frozen=g["richardson"],
                richardson_corrected=richardson_corrected(Qc, Qm, Qf,
                                                          R_REFINE),
                triple=(Qc, Qm, Qf))


# ---------------------------------------------------------------------------
# case measurement
# ---------------------------------------------------------------------------
def time_dirs(case_dir):
    ts = []
    for e in os.listdir(case_dir):
        if re.fullmatch(r"[0-9]+(\.[0-9]+)?", e) and e != "0":
            ts.append(float(e))
    return sorted(ts)


def tdir(case_dir, t):
    return os.path.join(case_dir, f"{t:g}")


def read_patch_set(case_dir, t, name):
    nf = boundary_nfaces(case_dir)
    fan = PATCH["fan"]
    out = PATCH["outlet"]
    p = patch_values(os.path.join(tdir(case_dir, t), "p"), fan, "scalar",
                     nf[fan])
    u = patch_values(os.path.join(tdir(case_dir, t), "U"), fan, "vector",
                     nf[fan])
    phi = patch_values(os.path.join(tdir(case_dir, t), "phi"), fan, "scalar",
                       nf[fan])
    phi_out = patch_values(os.path.join(tdir(case_dir, t), "phi"), out,
                           "scalar", nf[out])
    if not (len(p) == len(u) == len(phi) == CASES[name]["ny"]):
        refuse(f"{name}: fan patch face count mismatch "
               f"({len(p)}/{len(u)}/{len(phi)} vs ny {CASES[name]['ny']})")
    return p, u, phi, phi_out


def field_signature(case_dir, t):
    """Every parsed value of p, U, phi at time t (internal + all boundary
    values), for the value-for-value convergence comparison."""
    sig = []
    nf = boundary_nfaces(case_dir)
    for fld, want in (("p", "scalar"), ("U", "vector"), ("phi", "scalar")):
        path = os.path.join(tdir(case_dir, t), fld)
        sig.append(internal_values(path, want))
        txt = _text(path)
        for patch in sorted(nf):
            pb = _patch_block_opt(txt, patch)
            if pb is not None and re.search(r"\bvalue\b", pb):
                sig.append(_parse_value(pb, want, nf[patch]))
    return sig


def converged(case_dir):
    ts = time_dirs(case_dir)
    if len(ts) < 2:
        return False, "fewer than two written checkpoints"
    a, b = ts[-2], ts[-1]
    if field_signature(case_dir, a) != field_signature(case_dir, b):
        return False, f"checkpoints {a:g} and {b:g} differ"
    return True, f"checkpoints {a:g} and {b:g} value-for-value identical"


# ---------------------------------------------------------------------------
# planted-zero control (rule 3; exact-float rule, T10aR SS2.2)
# ---------------------------------------------------------------------------
def plant_scalar(src, dst, patch, delta):
    """Copy src to dst perturbing face 0 of the patch 'value' by delta.
    Returns (old, planted) where planted is the float actually written."""
    txt = _text(src)
    pb = _patch_block(txt, patch)
    m = re.search(r"value\s+nonuniform\s+List<scalar>\s*\d+\s*\(", pb)
    if m:
        body = pb[m.end():]
        fm = re.search(FLOAT, body)
        old = float(fm.group(0))
        planted = old + delta
        new_body = body[:fm.start()] + repr(planted) + body[fm.end():]
        new_pb = pb[:m.end()] + new_body
    else:
        um = re.search(r"value\s+uniform\s+(" + FLOAT + r")\s*;", pb)
        if not um:
            refuse(f"plant target patch {patch} has no scalar value entry")
        old = float(um.group(1))
        planted = old + delta
        new_pb = pb[:um.start(1)] + repr(planted) + pb[um.end(1):]
    open(dst, "w").write(txt.replace(pb, new_pb, 1))
    return old, planted


def plant_vector(src, dst, patch, delta):
    txt = _text(src)
    pb = _patch_block(txt, patch)
    m = re.search(r"value\s+nonuniform\s+List<vector>\s*\d+\s*\(", pb)
    if m:
        body = pb[m.end():]
        fm = re.search(r"\(\s*(" + FLOAT + r")", body)
        old = float(fm.group(1))
        planted = old + delta
        new_body = body[:fm.start(1)] + repr(planted) + body[fm.end(1):]
        new_pb = pb[:m.end()] + new_body
    else:
        um = re.search(r"value\s+uniform\s+\(\s*(" + FLOAT + r")", pb)
        if not um:
            refuse(f"plant target patch {patch} has no vector value entry")
        old = float(um.group(1))
        planted = old + delta
        new_pb = pb[:um.start(1)] + repr(planted) + pb[um.end(1):]
    open(dst, "w").write(txt.replace(pb, new_pb, 1))
    return old, planted


def planted_zero_control(case_dir, name):
    """Plant into a SCRATCH COPY of the earlier checkpoint; read back through
    the same readers; require the recovered change to equal EXACTLY
    fl(old+plant)-old -- not the plant, and never within a tolerance.  No
    case tree is written to.  A failed plant is a REFUSAL, not a graded row."""
    ts = time_dirs(case_dir)
    if len(ts) < 2:
        refuse(f"{name}: no earlier checkpoint for the planted-zero control")
    t = ts[-2]
    nf = boundary_nfaces(case_dir)
    fan = PATCH["fan"]
    tmp = tempfile.mkdtemp(prefix="e4a_plant_")
    try:
        for fld, want, delta, planter in (
                ("p", "scalar", PLANT["p"], plant_scalar),
                ("phi", "scalar", PLANT["phi"], plant_scalar),
                ("U", "vector", PLANT["U"], plant_vector)):
            src = os.path.join(tdir(case_dir, t), fld)
            dst = os.path.join(tmp, fld)
            old, planted = planter(src, dst, fan, delta)
            orig = patch_values(src, fan, want, nf[fan])
            got = patch_values(dst, fan, want, nf[fan])
            o0 = orig[0] if want == "scalar" else orig[0][0]
            g0 = got[0] if want == "scalar" else got[0][0]
            expected = planted - o0          # fl(old+plant) - old
            if expected == 0.0:
                refuse(f"{name}: plant into {fld} vanished in float "
                       "(plant not visible at this scale)")
            if o0 != old:
                refuse(f"{name}: reader/plant disagree on the original "
                       f"{fld} value ({o0!r} vs {old!r})")
            if g0 - o0 != expected:
                refuse(f"{name}: planted-zero control FAILED on {fld}: "
                       f"recovered {g0 - o0!r}, expected {expected!r} exactly")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# grading
# ---------------------------------------------------------------------------
def dev_pct(value, exact):
    return 100.0 * (value - exact) / exact


def measure_case(name):
    d = os.path.join(HERE, name)
    if not os.path.isfile(os.path.join(HERE, f"DONE.{name}")):
        refuse(f"{name}: no DONE marker -- mark_done_e4a.py has not certified "
               "the strict completion rule (rule 4); refusing, not degrading")
    mesh_readback(name)
    planted_zero_control(d, name)
    conv, why = converged(d)
    p, u, phi, phi_out = read_patch_set(d, END_TIME, name)
    spec = CASES[name]
    c = CURVES[spec["curve"]]
    worst, Q, n_out = identity_I1(p, u, phi, spec["curve"], c["p0_env"])
    Q_out = sum(phi_out)
    imbal = abs(Q - Q_out) / max(abs(Q), 1e-300)
    return dict(name=name, converged=conv, conv_why=why, I1=worst, Q=Q,
                Q_out=Q_out, I2=imbal, n_outflow=n_out,
                exact=c["Q_exact"])


def main(argv):
    provenance()
    frozen_contract()
    results = {n: measure_case(n) for n in CASES}
    verdicts = {}
    any_fail = False

    def emit(row, verdict, detail):
        nonlocal any_fail
        verdicts[row] = verdict
        if verdict not in (PASS,):
            any_fail = True
        print(f"{row:4s} {verdict:14s} {detail}")

    print("\n=== registered rows ===")
    # I1
    worst_case = max(results.values(), key=lambda r: r["I1"])
    tol = ROWS["I1"]["tol_abs"]
    v = PASS if all(r["I1"] <= tol for r in results.values()) else GATE_FAIL
    emit("I1", v, f"max face residual {worst_case['I1']:.3e} m2/s2 "
                  f"(worst case {worst_case['name']}, tol {tol:.1e}); "
                  "convention-error signature would be ~1.1e-4")
    # I2
    tol2 = ROWS["I2"]["tol_rel"]
    worst2 = max(results.values(), key=lambda r: r["I2"])
    v = PASS if all(r["I2"] <= tol2 for r in results.values()) else GATE_FAIL
    emit("I2", v, f"max |Q_in-Q_out|/|Q_in| {worst2['I2']:.3e} "
                  f"(worst case {worst2['name']}, tol {tol2:.0e})")
    # P1
    bad_p1 = [n for n, r in results.items() if r["n_outflow"] > 0]
    p1_ok = not bad_p1
    emit("P1", PASS if p1_ok else GATE_FAIL,
         "no fan-patch outflow face in any case" if p1_ok
         else f"outflow faces on fan patch in {','.join(bad_p1)} -- "
              "G1/G2/N1/D1 lose their analytic referent")

    # R1
    conv_flags = tuple(results[n]["converged"] for n in ("F_c", "F_m", "F_f"))
    tri = grade_triple(results["F_c"]["Q"], results["F_m"]["Q"],
                       results["F_f"]["Q"], conv_flags)
    if tri["verdict"] == NOT_A_RESULT:
        emit("R1", NOT_A_RESULT,
             f"{tri['reason']}; triple {tri['triple']} "
             f"order {tri.get('order')}  (no GCI quoted)")
    else:
        emit("R1", tri["verdict"],
             f"observed p {tri['order']:.3f} in {ROWS['R1']['interval']}; "
             f"GCI(Fs=1.25) {tri['GCI_pct']:.3f} %; richardson "
             f"frozen {tri['richardson_frozen']:.9e} / corrected "
             f"{tri['richardson_corrected']:.9e}")

    # G1 / G2 / N1
    for row, cname in (("G1", "F_f"), ("G2", "S_f"), ("N1", "N_f")):
        r = results[cname]
        if not r["converged"]:
            emit(row, NOT_A_RESULT, f"{cname} not converged: {r['conv_why']}")
            continue
        if not p1_ok:
            emit(row, NOT_A_RESULT, "P1 violated: analytic referent void")
            continue
        d = dev_pct(r["Q"], r["exact"])
        lo, hi = ROWS[row]["interval_dev_pct"]
        v, side = grade_interval(d, lo, hi)
        emit(row, v, f"{cname} Q {r['Q']:.9e} m3/s, dev {d:+.3f} % vs "
                     f"pred {ROWS[row]['prediction_dev_pct']:+.3f} % "
                     f"in [{lo:+.2f},{hi:+.2f}] % {side}")

    # D1
    if tri["verdict"] == NOT_A_RESULT or not p1_ok:
        emit("D1", NOT_A_RESULT, "triple not CONVERGING or P1 violated")
    else:
        rc = tri["richardson_corrected"]
        d = dev_pct(rc, results["F_f"]["exact"])
        lo, hi = ROWS["D1"]["interval_dev_pct"]
        v, side = grade_interval(d, lo, hi)
        emit("D1", v, f"corrected Richardson {rc:.9e}, dev {d:+.3f} % in "
                      f"[{lo:+.2f},{hi:+.2f}] % {side} (diagnostic row; "
                      "grades no case)")

    print("\nZ1   (control)      planted-zero exact-float rule held for "
          "p, U, phi readers in every case (a failure would have refused)")
    for n, r in results.items():
        print(f"     {n}: converged={r['converged']} ({r['conv_why']}); "
              f"Q {r['Q']:.9e}")
    return EXIT_FAIL if any_fail else EXIT_OK


# ---------------------------------------------------------------------------
# selftest -- synthetic data only; touches no case tree
# ---------------------------------------------------------------------------
def _tri_solve(N, s=1.0):
    """Solve the discrete FV plane-channel system exactly as registered:
    interior u_{j-1}-2u_j+u_{j+1} = -s; wall cells u_2-3u_1 = -s and
    u_{N-1}-3u_N = -s.  Gaussian elimination, pure python."""
    a = [[0.0] * N for _ in range(N)]
    b = [-s] * N
    a[0][0], a[0][1] = -3.0, 1.0
    a[N - 1][N - 2], a[N - 1][N - 1] = 1.0, -3.0
    for j in range(1, N - 1):
        a[j][j - 1], a[j][j], a[j][j + 1] = 1.0, -2.0, 1.0
    for i in range(N):                      # partial-pivot elimination
        piv = max(range(i, N), key=lambda k: abs(a[k][i]))
        a[i], a[piv] = a[piv], a[i]
        b[i], b[piv] = b[piv], b[i]
        for k in range(i + 1, N):
            f = a[k][i] / a[i][i]
            for j in range(i, N):
                a[k][j] -= f * a[i][j]
            b[k] -= f * b[i]
    u = [0.0] * N
    for i in range(N - 1, -1, -1):
        u[i] = (b[i] - sum(a[i][j] * u[j] for j in range(i + 1, N))) / a[i][i]
    return u


def _synthetic_field_files(tmp, ny, p_vals, u_vals, phi_vals, phi_out):
    os.makedirs(os.path.join(tmp, "20000"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "constant", "polyMesh"), exist_ok=True)

    def slist(vals):
        return ("nonuniform List<scalar> %d ( " % len(vals)
                + " ".join(repr(v) for v in vals) + " )")

    def vlist(vals):
        return ("nonuniform List<vector> %d ( " % len(vals)
                + " ".join("( %r %r %r )" % v for v in vals) + " )")

    open(os.path.join(tmp, "20000", "p"), "w").write(
        "internalField uniform 0;\nboundaryField\n{\n"
        "  inlet { type fanPressure; value %s; }\n"
        "  outlet { type fixedValue; value uniform 0; }\n}\n"
        % slist(p_vals))
    open(os.path.join(tmp, "20000", "U"), "w").write(
        "internalField uniform (0 0 0);\nboundaryField\n{\n"
        "  inlet { type pressureInletOutletVelocity; value %s; }\n}\n"
        % vlist(u_vals))
    open(os.path.join(tmp, "20000", "phi"), "w").write(
        "internalField nonuniform List<scalar> 2 ( 1.0 2.0 );\n"
        "boundaryField\n{\n  inlet { type calculated; value %s; }\n"
        "  outlet { type calculated; value %s; }\n}\n"
        % (slist(phi_vals), slist(phi_out)))
    open(os.path.join(tmp, "constant", "polyMesh", "boundary"), "w").write(
        "2\n(\ninlet { type patch; nFaces %d; startFace 0; }\n"
        "outlet { type patch; nFaces %d; startFace 0; }\n)\n"
        % (ny, len(phi_out)))


def selftest():
    n = [0]

    def ok(cond, what):
        n[0] += 1
        if not cond:
            print(f"SELFTEST FAIL at check {n[0]}: {what}")
            sys.exit(EXIT_REFUSE)

    # 1-2 frozen contract and declared redirect with restoration
    ok(T1C.FS == 1.25 and T1C.R_REFINE == 1.6, "frozen contract")
    with with_ratio(1.5):
        inside = T1C.R_REFINE
    ok(inside == 1.5 and T1C.R_REFINE == 1.6, "with_ratio restores")

    # 3-5 exact operating points reproduce the registered exact values
    ok(abs(exact_operating_point("A") / 1.5e-7 - 1) < 1e-14, "Q*_A")
    ok(abs(exact_operating_point("B") / 1.0e-7 - 1) < 1e-14, "Q*_B")
    ok(abs(exact_operating_point("NULL") / 1.5e-7 - 1) < 1e-14, "Q*_NULL")

    # 6 curve evaluation matches Polynomial::value + the max(Q,0) clamp
    ok(curve_dp("A", -1.0) == 0.081 and
       abs(curve_dp("A", 1.5e-7) - 0.054) < 1e-15, "curve eval + clamp")

    # 7 the registered wall-discretisation law: discrete mean = exact*(1+2/N^2)
    for N in (8, 12, 18):
        u = _tri_solve(N)
        mean = sum(u) / N
        ok(abs(mean - (N * N + 2) / 12.0) < 1e-9,
           f"discrete channel law N={N}")

    # 10-12 identity: exact-by-construction, mutation flips it, neg branch
    ny, Q = 4, 1.5e-7
    phi = [-Q / ny] * ny
    pd = curve_dp("A", Q)
    u = [(0.01 * (i + 1), 0.0, 0.0) for i in range(ny)]
    p = [0.0 + pd - 0.5 * (uf[0] ** 2) for uf in u]
    worst, Qm, n_out = identity_I1(p, u, phi, "A", 0.0)
    ok(worst < 1e-15 and abs(Qm - Q) < 1e-22 and n_out == 0,
       "identity exact on constructed data")
    p_bad = list(p)
    p_bad[0] += 1e-6
    worst_bad, _, _ = identity_I1(p_bad, u, phi, "A", 0.0)
    ok(worst_bad > ROWS["I1"]["tol_abs"],
       "mutation control: corrupted p face flips I1")
    phi_o = list(phi)
    phi_o[2] = +Q / ny                       # one outflow face
    worst_o, _, n_o = identity_I1(
        [0.0 + curve_dp("A", -sum(phi_o))] + p[1:3]
        + [0.0 + curve_dp("A", -sum(phi_o))], u, phi_o, "A", 0.0)
    ok(n_o == 1, "neg branch counts the outflow face")

    # 13 the convention-error signature clears the tolerance by decades
    ok(0.5 * 0.015 ** 2 > 1000 * ROWS["I1"]["tol_abs"],
       "convention-error signature >> I1 tolerance")

    # 14-17 verdict paths on grade_interval
    ok(grade_interval(2.0, 1.6, 2.4)[0] == PASS, "PASS path")
    ok(grade_interval(2.5, 1.6, 2.4) == (GATE_FAIL, "high"), "GATE FAIL high")
    ok(grade_interval(1.5, 1.6, 2.4) == (GATE_FAIL, "low"), "GATE FAIL low")
    ok(grade_interval(1.6, 1.6, 2.4)[0] == PASS, "boundary is inside")

    # 18-19 triple: NOT A RESULT on OSCILLATORY, no GCI quoted
    t = grade_triple(1.0, 1.2, 1.1)
    ok(t["verdict"] == NOT_A_RESULT and "GCI_pct" not in t,
       "oscillatory triple -> NOT A RESULT, no GCI")
    # converging synthetic power law p=2 at r=1.5
    ex, A = 1.5e-7, 1e-9
    Qs = [ex + A * (1.5 ** 2) ** k for k in (2, 1, 0)]   # coarse, med, fine
    t = grade_triple(Qs[0], Qs[1], Qs[2])
    ok(t["verdict"] == PASS and abs(t["order"] - 2.0) < 1e-10,
       "power-law triple: p == 2, graded PASS")

    # 20 rule-5 order: unconverged level beats a CONVERGING triple
    t = grade_triple(Qs[0], Qs[1], Qs[2], converged=(True, False, True))
    ok(t["verdict"] == NOT_A_RESULT, "unconverged level -> NOT A RESULT")

    # 21 corrected Richardson recovers a clean power law; frozen form does not
    rc = richardson_corrected(Qs[0], Qs[1], Qs[2], 1.5)
    with with_ratio(1.5):
        rf = T1C.gci(Qs[0], Qs[1], Qs[2])["richardson"]
    ok(abs(rc - ex) < 1e-8 * ex and abs(rf - ex) > abs(rc - ex),
       "corrected vs frozen (sign-defect) Richardson")

    # 22-30 file readers, planted-zero exact-float rule, mutation via files
    tmp = tempfile.mkdtemp(prefix="e4a_selftest_")
    try:
        _synthetic_field_files(tmp, ny, p, u, phi, [Q / ny] * ny)
        nfp = boundary_nfaces(tmp)
        ok(nfp == {"inlet": ny, "outlet": ny}, "boundary nFaces parse")
        pr = patch_values(os.path.join(tmp, "20000", "p"), "inlet", "scalar",
                          ny)
        ur = patch_values(os.path.join(tmp, "20000", "U"), "inlet", "vector",
                          ny)
        fr = patch_values(os.path.join(tmp, "20000", "phi"), "inlet",
                          "scalar", ny)
        ok(pr == p and ur == u and fr == phi, "readers round-trip repr floats")
        # uniform expansion
        pu = patch_values(os.path.join(tmp, "20000", "p"), "outlet", "scalar",
                          3)
        ok(pu == [0.0, 0.0, 0.0], "uniform scalar expansion via nFaces")
        # identity through files, then a corrupted file flips it
        w, _, _ = identity_I1(pr, ur, fr, "A", 0.0)
        ok(w < 1e-15, "identity through the file readers")
        old, planted = plant_scalar(os.path.join(tmp, "20000", "p"),
                                    os.path.join(tmp, "p_bad"), "inlet", 1e-6)
        pb = patch_values(os.path.join(tmp, "p_bad"), "inlet", "scalar", ny)
        wb, _, _ = identity_I1(pb, ur, fr, "A", 0.0)
        ok(wb > ROWS["I1"]["tol_abs"],
           "mutation control THROUGH THE FILE READER flips I1")
        # I2 mutation: perturbed outlet phi flips the mass identity
        old2, _ = plant_scalar(os.path.join(tmp, "20000", "phi"),
                               os.path.join(tmp, "phi_bad"), "outlet", 1e-9)
        fo = patch_values(os.path.join(tmp, "phi_bad"), "outlet", "scalar",
                          ny)
        imb = abs(-sum(fr) - sum(fo)) / abs(sum(fr))
        ok(imb > ROWS["I2"]["tol_rel"], "mutation control flips I2")
        # planted-zero exact-float rule on all three readers
        for fld, want, delta, planter in (
                ("p", "scalar", PLANT["p"], plant_scalar),
                ("phi", "scalar", PLANT["phi"], plant_scalar),
                ("U", "vector", PLANT["U"], plant_vector)):
            src = os.path.join(tmp, "20000", fld)
            dst = os.path.join(tmp, fld + "_planted")
            o, pl = planter(src, dst, "inlet", delta)
            got = patch_values(dst, "inlet", want, ny)
            g0 = got[0] if want == "scalar" else got[0][0]
            o_read = patch_values(src, "inlet", want, ny)
            o0 = o_read[0] if want == "scalar" else o_read[0][0]
            ok(g0 - o0 == pl - o0 and pl - o0 != 0.0,
               f"planted-zero exact-float rule on {fld}")
        # an unplanted copy recovers exactly zero (the refusal the control
        # would raise is what rule 3 exists for)
        shutil.copy(os.path.join(tmp, "20000", "p"), os.path.join(tmp, "p_c"))
        pc = patch_values(os.path.join(tmp, "p_c"), "inlet", "scalar", ny)
        ok(pc[0] - pr[0] == 0.0, "unplanted copy recovers exactly zero")
        # convergence signature: identical vs one changed value
        sig_a = field_signature(tmp, 20000)
        shutil.copytree(os.path.join(tmp, "20000"),
                        os.path.join(tmp, "15000"))
        # NOTE: field_signature reads one time dir; equality across dirs
        sig_b = field_signature(tmp, 15000)
        ok(sig_a == sig_b, "identical checkpoints compare equal")
        plant_scalar(os.path.join(tmp, "15000", "p"),
                     os.path.join(tmp, "15000", "p"), "inlet", 1e-12)
        ok(field_signature(tmp, 15000) != sig_a,
           "a 1e-12 change breaks checkpoint equality")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # registered-json sanity: intervals well-formed, predictions inside
    for row in ("G1", "G2", "N1", "D1"):
        lo, hi = ROWS[row]["interval_dev_pct"]
        pr_ = ROWS[row]["prediction_dev_pct"]
        ok(lo < hi and lo <= pr_ <= hi, f"{row} interval/prediction sane")
    lo, hi = ROWS["R1"]["interval"]
    ok(lo < hi and lo <= ROWS["R1"]["prediction"] <= hi, "R1 interval sane")

    print(f"SELFTEST {n[0]}/{n[0]} OK")
    return EXIT_OK


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        provenance()
        frozen_contract()
        sys.exit(selftest())
    sys.exit(main(sys.argv))
