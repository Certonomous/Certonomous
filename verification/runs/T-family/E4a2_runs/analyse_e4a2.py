#!/usr/bin/env python3
"""
E4a2 comparator -- successor rung to E4a.  fanPressure BC verification, exact
operating-point class.

WHAT IS NEW HERE, AND IT IS ONE THING
-------------------------------------
E4a registered an iterative-convergence gate of BIT-IDENTITY: every parsed
value of p, U and phi identical between the last two written checkpoints
(analyse_e4a.py:411-418).  It did not close on any of the five cases -- the
fields still moved in their last written digit -- and rule 5 order (1) voided
five registered rows (E4a_RESULTS.md sections 1 and 5).  E4a2 RE-REGISTERS
THAT GATE AND ONLY THAT GATE, as a bounded floor on a relative field change
plus a not-growing plateau reading over a retained series:

  C1 SUSTAINED FLOOR   r_k <= 1e-8 for each of the last three intervals
  C2 NOT GROWING       the log10(r_k) fit over the last third is not GROWING

The physics, geometry, curves, exact operating points, the section 1.5 error
derivation and rows I1/I2/P1/R1/G1/G2/N1/D1/Z1 with their intervals and
falsifiers are CARRIED OVER UNCHANGED and are asserted DEEP-EQUAL to E4a's
committed registered json at every invocation.

FROZEN IMPORTS -- imported, never copied, never edited, sha256 verified
----------------------------------------------------------------------
E4_runs/analyse_e4a.py  (a9f31c3f...): the exact-operating-point solver, the
    curve evaluator, identity_I1, the p/U/phi readers, boundary_nfaces,
    mesh_readback, read_patch_set, the planted-zero planters and control,
    grade_interval, grade_triple, dev_pct, richardson_corrected, with_ratio,
    time_dirs/tdir, and the selftest's discrete channel solver _tri_solve.
E4_runs/E4a_registered.json (bb363d02...): the carried-over rows' source.
T1_runs/analyse_t1c.py (60893b28...): gci at Fs = 1.25, reached through the
    frozen E4a module, with its declared in-process r redirect.
Every hash is the blob committed at 628e29c4 and is re-verified on disk here;
a mismatch is a REFUSAL.  Where a frozen function resolves paths from its own
module-level HERE, it is reused through the restoring `in_dir` redirect (the
with_ratio / T10aR in_tree precedent) rather than re-implemented.

NEW INSTRUMENTS, declared: numeric_signature (a numeric, not textual, field
signature), rel_change_series, gate_converged, classify_series, _linfit, the
in_dir redirect, and the X1 reproduction control.

Exit codes: 0 every registered prediction met; 1 at least one GATE FAIL or
NOT A RESULT; 2 refusal.  This file refuses rather than degrades.
"""
import sys
sys.dont_write_bytecode = True          # no __pycache__ in any frozen tree

import hashlib                                                     # noqa: E402
import json                                                        # noqa: E402
import math                                                        # noqa: E402
import os                                                          # noqa: E402
import re                                                          # noqa: E402
import shutil                                                      # noqa: E402
import tempfile                                                    # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TFAM = os.path.dirname(HERE)
E4_DIR = os.path.join(TFAM, "E4_runs")
sys.path.insert(0, E4_DIR)
import analyse_e4a as E4A                             # noqa: E402  FROZEN
T1C = E4A.T1C                                         # FROZEN, via E4A

REG = json.load(open(os.path.join(HERE, "E4a2_registered.json")))
ROWS = REG["rows"]
CASES = REG["cases"]
CURVES = REG["curves"]
PATCH = REG["patches"]
END_TIME = REG["time"]["endTime"]
GATE = REG["convergence_gate"]
FLOOR = GATE["floor_rel"]
SUSTAIN = GATE["sustained_intervals"]
FIT_R2_MIN = GATE["fit_r2_min"]
FIT_SLOPE = GATE["fit_slope_decades_per_1000"]
FIT_FLOOR = GATE["fit_floor_rel"]
SPREAD_TOL = GATE["spread_tol"]
MIN_CKPT = GATE["min_checkpoints"]
CUM_TOL = GATE["cum_tol_rel"]
XC = REG["reproduction_control"]
CONV_FIELDS = (("p", "scalar"), ("U", "vector"), ("phi", "scalar"))

PASS, GATE_REACHED, GATE_FAIL = "PASS", "GATE REACHED", "GATE FAIL"
NOT_A_RESULT, BLOCKED, PENDING = "NOT A RESULT", "BLOCKED", "PENDING"
EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

LOCAL = ("analyse_e4a2.py", "E4a2_registered.json", "build_e4a2.py",
         "mark_done_e4a2.py", "run_one_e4a2.sh", "launch_e4a2.sh")


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
    print("provenance sha256 -- this rung's own instruments:")
    for name in LOCAL:
        print(f"  {sha256_of(os.path.join(HERE, name))}  E4a2_runs/{name}")
    print("provenance sha256 -- FROZEN imports (registered table, "
          "blobs committed at 628e29c4):")
    for rel in REG["frozen_instruments"]:
        print(f"  {sha256_of(os.path.join(TFAM, rel))}  {rel}")


# ---------------------------------------------------------------------------
# refusals that must fire before any number is produced
# ---------------------------------------------------------------------------
class in_dir:
    """Redirect a frozen module's HERE to THIS rung's run tree for one block,
    restoring on exit.  The frozen FILE is never modified; only this process's
    imported module object, and only inside the `with`.  Precedent: E4a's own
    with_ratio, and T10aR's in_tree."""

    def __init__(self, mod, path):
        self.mod, self.path = mod, path

    def __enter__(self):
        self.old = self.mod.HERE
        self.mod.HERE = self.path
        return self

    def __exit__(self, *a):
        self.mod.HERE = self.old
        return False


def frozen_contract():
    if HERE == E4A.HERE:
        refuse("this comparator resolves to E4a's own run tree")
    for rel, want in REG["frozen_instruments"].items():
        got = sha256_of(os.path.join(TFAM, rel))
        if got != want:
            refuse(f"frozen instrument {rel} hashes {got}, registered {want}")
    for k in REG["carried_over_keys"]:
        if REG[k] != E4A.REG[k]:
            refuse(f"carried-over key '{k}' differs from E4a's registered json "
                   "-- the rows this rung claims to carry unchanged are not "
                   "unchanged")
    if T1C.FS != 1.25:
        refuse(f"frozen analyse_t1c.FS is {T1C.FS}, not 1.25")
    if T1C.R_REFINE != REG["grid"]["frozen_module_r"]:
        refuse(f"frozen analyse_t1c.R_REFINE is {T1C.R_REFINE}, not the "
               f"registered {REG['grid']['frozen_module_r']}")
    if REG["time"]["writeInterval"] >= REG["time"]["endTime"]:
        refuse("writeInterval is not strictly < endTime (L-140)")


# ---------------------------------------------------------------------------
# NEW INSTRUMENT: numeric field signature and the relative-change series
# ---------------------------------------------------------------------------
def _flat(vals, want):
    out = []
    for v in vals:
        if want == "vector":
            out.extend(v)
        else:
            out.append(v)
    return out


def numeric_signature(case_dir, t):
    """Ordered flat list of EVERY parsed numeric value of each convergence
    field at time t: internalField first, then every boundary patch carrying a
    'value' entry, patches in sorted order, vector components flattened.  Uses
    the FROZEN readers; unlike E4a's field_signature this is numeric, so a
    magnitude can be taken from it."""
    nf = E4A.boundary_nfaces(case_dir)
    sig = {}
    for fld, want in CONV_FIELDS:
        path = os.path.join(E4A.tdir(case_dir, t), fld)
        txt = E4A._text(path)
        iv = E4A.internal_values(path, want)
        if iv == "uniform":
            m = re.search(r"internalField\s+uniform\s+([^;]*);", txt)
            if not m:
                refuse(f"{path}: uniform internalField without a value")
            vals = [float(x) for x in re.findall(E4A.FLOAT, m.group(1))]
        else:
            vals = _flat(iv, want)
        for patch in sorted(nf):
            pb = E4A._patch_block_opt(txt, patch)
            if pb is not None and re.search(r"\bvalue\b", pb):
                vals.extend(_flat(E4A._parse_value(pb, want, nf[patch]), want))
        sig[fld] = vals
    return sig


def rel_change_series(case_dir, name):
    """The registered r_k series over every consecutive retained-checkpoint
    pair.  Normalised by each field's PEAK MAGNITUDE at the last checkpoint
    (<= its range, so conservative against T3's registered 'fraction of the
    field's range' form)."""
    ts = [int(t) if float(t).is_integer() else t for t in E4A.time_dirs(case_dir)]
    if len(ts) < MIN_CKPT:
        refuse(f"{name}: {len(ts)} retained checkpoints, registered minimum "
               f"{MIN_CKPT} -- refusing, not degrading")
    last = numeric_signature(case_dir, ts[-1])
    scale = {}
    for fld, _ in CONV_FIELDS:
        if not last[fld]:
            refuse(f"{name}: field {fld} parsed empty at {ts[-1]}")
        s = max(abs(v) for v in last[fld])
        if s == 0.0:
            refuse(f"{name}: field {fld} is identically zero at {ts[-1]}; the "
                   "relative change has no denominator")
        scale[fld] = s
    series = []
    prev = numeric_signature(case_dir, ts[0])
    for k in range(1, len(ts)):
        cur = last if k == len(ts) - 1 else numeric_signature(case_dir, ts[k])
        per = {}
        for fld, _ in CONV_FIELDS:
            a, b = prev[fld], cur[fld]
            if len(a) != len(b):
                refuse(f"{name}: field {fld} has {len(a)} values at {ts[k-1]} "
                       f"and {len(b)} at {ts[k]} -- structural mismatch")
            per[fld] = max(abs(x - y) for x, y in zip(a, b)) / scale[fld]
        series.append((ts[k], max(per.values()), per))
        prev = cur
    return ts, series, scale


def _linfit(xs, ys):
    """Least-squares slope and R^2.  Zero variance in ys returns R^2 = 0.0:
    no trend is detectable, which classifies FLOOR."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0.0:
        return 0.0, 0.0
    slope = sxy / sxx
    r2 = 0.0 if syy == 0.0 else (sxy * sxy) / (sxx * syy)
    return slope, r2


def classify_series(series):
    """T3 ext1 section 2 style, on the registered fit window.  Reported
    diagnostic; the only part of it that gates is the GROWING flag (C2)."""
    n = max(4, len(series) // 3)
    tail = series[-n:]
    xs = [float(s[0]) for s in tail]
    ys = [math.log10(max(s[1], FIT_FLOOR)) for s in tail]
    slope, r2 = _linfit(xs, ys)
    dec1000 = slope * 1000.0
    vals = sorted(s[1] for s in tail)
    lo = max(vals[int(round(0.05 * (len(vals) - 1)))], FIT_FLOOR)
    hi = max(vals[int(round(0.95 * (len(vals) - 1)))], FIT_FLOOR)
    spread = hi / lo
    growing = (r2 >= FIT_R2_MIN and dec1000 >= FIT_SLOPE)
    if r2 >= FIT_R2_MIN and dec1000 <= -FIT_SLOPE:
        cls = "DECAYING"
    elif growing:
        cls = "GROWING"
    elif spread > SPREAD_TOL:
        cls = "LIMIT CYCLE"
    else:
        cls = "FLOOR"
    return dict(cls=cls, growing=growing, slope_dec_per_1000=dec1000, r2=r2,
                spread=spread, window=n)


def q_series(case_dir, name, ts):
    """Q(t) = -sum(phi) over the fan patch at every retained checkpoint, read
    with the FROZEN reader -- the same quantity every graded row uses."""
    nf = E4A.boundary_nfaces(case_dir)
    fan = PATCH["fan"]
    out = []
    for t in ts:
        phi = E4A.patch_values(os.path.join(E4A.tdir(case_dir, t), "phi"),
                               fan, "scalar", nf[fan])
        out.append((t, -sum(phi)))
    return out


def gate_c3(qs, end_time=None):
    """C3: a FIELD-SPACE DISTANCE on the graded target across half the run.
    C1/C2 are change criteria and L-243 is explicit that change bounds nothing
    about distance to a fixed point; this clause is the remedy."""
    end_time = END_TIME if end_time is None else end_time
    tK, qK = qs[-1]
    if qK == 0.0:
        refuse("C3: Q is exactly zero at endTime; no relative distance exists")
    half = end_time / 2.0
    tH, qH = min(qs[:-1], key=lambda z: abs(float(z[0]) - half))
    cum = abs(qK - qH) / abs(qK)
    return cum <= CUM_TOL, dict(t_half=tH, q_half=qH, q_end=qK, cum=cum)


def gate_converged(series, qs=None):
    """The registered gate.  C1 sustained floor AND C2 not growing AND C3
    graded-quantity stationarity."""
    r = [s[1] for s in series]
    last = r[-SUSTAIN:]
    c1 = max(last) <= FLOOR
    cl = classify_series(series)
    c2 = not cl["growing"]
    first = None
    for t, rk, _ in series:
        if rk <= FLOOR:
            first = t
            break
    if qs is None:
        c3, c3d = True, None
    else:
        c3, c3d = gate_c3(qs)
    why = []
    if not c1:
        why.append(f"C1 sustained floor FAILS: max r over the last {SUSTAIN} "
                   f"intervals {max(last):.3e} > floor {FLOOR:.1e}")
    if not c2:
        why.append(f"C2 not-growing FAILS: fit over the last {cl['window']} "
                   f"intervals is GROWING ({cl['slope_dec_per_1000']:+.5f} "
                   f"decades/1000 it, R2 {cl['r2']:.3f})")
    if not c3:
        why.append(f"C3 graded-quantity stationarity FAILS: "
                   f"|Q({c3d['t_half']})-Q(end)|/|Q(end)| = {c3d['cum']:.3e} > "
                   f"cum_tol {CUM_TOL:.1e}")
    if c1 and c2 and c3:
        why.append(f"C1 max r over the last {SUSTAIN} intervals {max(last):.3e} "
                   f"<= floor {FLOOR:.1e}; C2 fit {cl['slope_dec_per_1000']:+.5f} "
                   f"decades/1000 it (R2 {cl['r2']:.3f}), class {cl['cls']}"
                   + ("" if c3d is None else
                      f"; C3 |dQ| over half the run {c3d['cum']:.3e} <= "
                      f"{CUM_TOL:.1e}"))
    return (c1 and c2 and c3), dict(c1=c1, c2=c2, c3=c3, c3d=c3d,
                                    r_last=r[-1], last=last,
                                    first_crossing=first, cls=cl,
                                    why="; ".join(why))


# ---------------------------------------------------------------------------
# case measurement
# ---------------------------------------------------------------------------
def measure_case(name):
    d = os.path.join(HERE, name)
    if not os.path.isfile(os.path.join(HERE, f"DONE.{name}")):
        refuse(f"{name}: no DONE marker -- mark_done_e4a2.py has not certified "
               "the strict completion rule (rule 4); refusing, not degrading")
    with in_dir(E4A, HERE):
        E4A.mesh_readback(name)                       # FROZEN
        E4A.planted_zero_control(d, name)             # FROZEN (Z1, rule 3)
        p, u, phi, phi_out = E4A.read_patch_set(d, END_TIME, name)   # FROZEN
    if E4A.HERE != E4_DIR:
        refuse("in_dir did not restore the frozen module's HERE")
    ts, series, scale = rel_change_series(d, name)
    qs = q_series(d, name, ts)
    conv, gd = gate_converged(series, qs)
    spec = CASES[name]
    c = CURVES[spec["curve"]]
    worst, Q, n_out = E4A.identity_I1(p, u, phi, spec["curve"],
                                      c["p0_env"])    # FROZEN
    Q_out = sum(phi_out)
    imbal = abs(Q - Q_out) / max(abs(Q), 1e-300)
    dev = E4A.dev_pct(Q, c["Q_exact"])                # FROZEN
    return dict(name=name, converged=conv, gate=gd, series=series, qs=qs,
                checkpoints=ts, scale=scale, I1=worst, Q=Q, Q_out=Q_out,
                I2=imbal, n_outflow=n_out, exact=c["Q_exact"], dev=dev)


def reproduction_control(results):
    """X1.  GRADES NOTHING and produces NO verdict; it can only REFUSE.  Its
    threshold is calibrated so that genuine iteration drift trips C1 first, so
    X1 can only fire on gross non-reproduction."""
    for n, r in results.items():
        want = XC["e4a_dev_pct"][n]
        gap = abs(r["dev"] - want)
        if gap > XC["tol_pp"]:
            refuse(f"X1 reproduction control FAILED on {n}: dev {r['dev']:+.4f} "
                   f"% vs E4a's {want:+.4f} %, gap {gap:.4f} pp > "
                   f"{XC['tol_pp']} pp.  Same meshes, same BCs, same solver: "
                   "this is a non-reproduction, not a physics disagreement, "
                   "and the rung refuses rather than grades.")


# ---------------------------------------------------------------------------
# grading
# ---------------------------------------------------------------------------
def main(argv):
    provenance()
    frozen_contract()
    results = {n: measure_case(n) for n in CASES}
    reproduction_control(results)
    verdicts = {}
    any_fail = False

    def emit(row, verdict, detail):
        nonlocal any_fail
        verdicts[row] = verdict
        if verdict not in (PASS,):
            any_fail = True
        print(f"{row:4s} {verdict:14s} {detail}")

    print("\n=== convergence gate (the one row this rung re-registers) ===")
    for n in CASES:
        r = results[n]
        g = r["gate"]
        print(f"  {n:5s} converged={r['converged']}  r_last {g['r_last']:.3e} "
              f"(floor {FLOOR:.1e})  first crossing at "
              f"{g['first_crossing']}  class {g['cls']['cls']} "
              f"(slope {g['cls']['slope_dec_per_1000']:+.5f} dec/1000, "
              f"R2 {g['cls']['r2']:.3f}, p95/p05 {g['cls']['spread']:.2f})")
        print(f"        {g['why']}")

    print("\n=== registered rows (carried over from E4a unchanged) ===")
    tol = ROWS["I1"]["tol_abs"]
    worst_case = max(results.values(), key=lambda r: r["I1"])
    v = PASS if all(r["I1"] <= tol for r in results.values()) else GATE_FAIL
    emit("I1", v, f"max face residual {worst_case['I1']:.3e} m2/s2 "
                  f"(worst case {worst_case['name']}, tol {tol:.1e}); "
                  "convention-error signature would be ~1.1e-4")
    tol2 = ROWS["I2"]["tol_rel"]
    worst2 = max(results.values(), key=lambda r: r["I2"])
    v = PASS if all(r["I2"] <= tol2 for r in results.values()) else GATE_FAIL
    emit("I2", v, f"max |Q_in-Q_out|/|Q_in| {worst2['I2']:.3e} "
                  f"(worst case {worst2['name']}, tol {tol2:.0e})")
    bad_p1 = [n for n, r in results.items() if r["n_outflow"] > 0]
    p1_ok = not bad_p1
    emit("P1", PASS if p1_ok else GATE_FAIL,
         "no fan-patch outflow face in any case" if p1_ok
         else f"outflow faces on fan patch in {','.join(bad_p1)} -- "
              "G1/G2/N1/D1 lose their analytic referent")

    conv_flags = tuple(results[n]["converged"] for n in ("F_c", "F_m", "F_f"))
    tri = E4A.grade_triple(results["F_c"]["Q"], results["F_m"]["Q"],
                           results["F_f"]["Q"], conv_flags)      # FROZEN
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

    for row, cname in (("G1", "F_f"), ("G2", "S_f"), ("N1", "N_f")):
        r = results[cname]
        if not r["converged"]:
            emit(row, NOT_A_RESULT,
                 f"{cname} not converged: {r['gate']['why']}")
            continue
        if not p1_ok:
            emit(row, NOT_A_RESULT, "P1 violated: analytic referent void")
            continue
        lo, hi = ROWS[row]["interval_dev_pct"]
        v, side = E4A.grade_interval(r["dev"], lo, hi)            # FROZEN
        emit(row, v, f"{cname} Q {r['Q']:.9e} m3/s, dev {r['dev']:+.3f} % vs "
                     f"pred {ROWS[row]['prediction_dev_pct']:+.3f} % "
                     f"in [{lo:+.2f},{hi:+.2f}] % {side}")

    if tri["verdict"] == NOT_A_RESULT or not p1_ok:
        emit("D1", NOT_A_RESULT, "triple not CONVERGING or P1 violated")
    else:
        rc = tri["richardson_corrected"]
        dv = E4A.dev_pct(rc, results["F_f"]["exact"])
        lo, hi = ROWS["D1"]["interval_dev_pct"]
        v, side = E4A.grade_interval(dv, lo, hi)
        emit("D1", v, f"corrected Richardson {rc:.9e}, dev {dv:+.3f} % in "
                      f"[{lo:+.2f},{hi:+.2f}] % {side} (diagnostic row; "
                      "grades no case)")

    print("\nZ1   (control)      planted-zero exact-float rule held for "
          "p, U, phi readers in every case (a failure would have refused)")
    print("X1   (control)      reproduction against E4a within "
          f"{XC['tol_pp']} pp in every case (a failure would have refused); "
          "grades nothing, is not a prediction")
    for n, r in results.items():
        print(f"     {n}: dev {r['dev']:+.4f} % (E4a {XC['e4a_dev_pct'][n]:+.4f} "
              f"%, gap {abs(r['dev']-XC['e4a_dev_pct'][n]):.4f} pp); "
              f"Q {r['Q']:.9e}")

    print("\n=== r_k series (reported diagnostic; grades nothing) ===")
    for n, r in results.items():
        s = " ".join(f"{t}:{rk:.2e}" for t, rk, _ in r["series"])
        print(f"  {n}: {s}")
    print("\n=== Q(t) distance to endTime (reported diagnostic; C3's input) ===")
    for n, r in results.items():
        qK = r["qs"][-1][1]
        s = " ".join(f"{t}:{abs(q-qK)/abs(qK):.2e}" for t, q in r["qs"])
        print(f"  {n}: {s}")
    return EXIT_FAIL if any_fail else EXIT_OK


# ---------------------------------------------------------------------------
# selftest -- synthetic data only; touches no case tree
# ---------------------------------------------------------------------------
def _series(vals, t0=2000, dt=2000):
    return [(t0 + i * dt, v, {}) for i, v in enumerate(vals)]


def selftest():
    n = [0]

    def ok(cond, what):
        n[0] += 1
        if not cond:
            print(f"SELFTEST FAIL at check {n[0]}: {what}")
            sys.exit(EXIT_REFUSE)

    # --- provenance, redirects, carry-over ---------------------------------
    ok(T1C.FS == 1.25 and T1C.R_REFINE == 1.6, "frozen t1c contract")
    with E4A.with_ratio(1.5):
        inside = T1C.R_REFINE
    ok(inside == 1.5 and T1C.R_REFINE == 1.6, "frozen with_ratio restores")
    with in_dir(E4A, HERE):
        red = E4A.HERE
    ok(red == HERE and E4A.HERE == E4_DIR, "in_dir redirects and restores")
    ok(HERE != E4A.HERE, "this rung's tree is not E4a's tree")
    for k in REG["carried_over_keys"]:
        ok(REG[k] == E4A.REG[k], f"carried-over key {k} deep-equals E4a's")
    for rel, want in REG["frozen_instruments"].items():
        ok(sha256_of(os.path.join(TFAM, rel)) == want,
           f"frozen instrument {rel} hashes as registered")

    # --- carried-over physics, through the frozen functions -----------------
    ok(abs(E4A.exact_operating_point("A") / 1.5e-7 - 1) < 1e-14, "Q*_A")
    ok(abs(E4A.exact_operating_point("B") / 1.0e-7 - 1) < 1e-14, "Q*_B")
    ok(abs(E4A.exact_operating_point("NULL") / 1.5e-7 - 1) < 1e-14, "Q*_NULL")
    ok(E4A.curve_dp("A", -1.0) == 0.081 and
       abs(E4A.curve_dp("A", 1.5e-7) - 0.054) < 1e-15, "curve eval + clamp")
    for N in (8, 12, 18):
        u = E4A._tri_solve(N)
        ok(abs(sum(u) / N - (N * N + 2) / 12.0) < 1e-9,
           f"discrete channel law N={N}")

    # --- identity and its mutation controls ---------------------------------
    ny, Q = 4, 1.5e-7
    phi = [-Q / ny] * ny
    pd = E4A.curve_dp("A", Q)
    uu = [(0.01 * (i + 1), 0.0, 0.0) for i in range(ny)]
    p = [0.0 + pd - 0.5 * (uf[0] ** 2) for uf in uu]
    worst, Qm, n_out = E4A.identity_I1(p, uu, phi, "A", 0.0)
    ok(worst < 1e-15 and abs(Qm - Q) < 1e-22 and n_out == 0,
       "identity exact on constructed data")
    p_bad = list(p)
    p_bad[0] += 1e-6
    ok(E4A.identity_I1(p_bad, uu, phi, "A", 0.0)[0] > ROWS["I1"]["tol_abs"],
       "mutation control: corrupted p face flips I1")
    phi_o = list(phi)
    phi_o[2] = +Q / ny
    ok(E4A.identity_I1(p[:1] + p[1:3] + p[3:], uu, phi_o, "A", 0.0)[2] == 1,
       "neg branch counts the outflow face")
    ok(0.5 * 0.015 ** 2 > 1000 * ROWS["I1"]["tol_abs"],
       "convention-error signature >> I1 tolerance")

    # --- every verdict path -------------------------------------------------
    ok(E4A.grade_interval(2.0, 1.6, 2.4)[0] == PASS, "PASS path")
    ok(E4A.grade_interval(2.5, 1.6, 2.4) == (GATE_FAIL, "high"),
       "GATE FAIL high")
    ok(E4A.grade_interval(1.5, 1.6, 2.4) == (GATE_FAIL, "low"), "GATE FAIL low")
    ok(E4A.grade_interval(1.6, 1.6, 2.4)[0] == PASS, "boundary is inside")
    t = E4A.grade_triple(1.0, 1.2, 1.1)
    ok(t["verdict"] == NOT_A_RESULT and "GCI_pct" not in t,
       "oscillatory triple -> NOT A RESULT, no GCI key present")
    ex, A = 1.5e-7, 1e-9
    Qs = [ex + A * (1.5 ** 2) ** k for k in (2, 1, 0)]
    t = E4A.grade_triple(*Qs)
    ok(t["verdict"] == PASS and abs(t["order"] - 2.0) < 1e-10,
       "power-law triple: p == 2, graded PASS")
    ok(E4A.grade_triple(*Qs, converged=(True, False, True))["verdict"]
       == NOT_A_RESULT,
       "rule 5 order: unconverged level beats a CONVERGING triple")
    rc = E4A.richardson_corrected(Qs[0], Qs[1], Qs[2], 1.5)
    with E4A.with_ratio(1.5):
        rf = T1C.gci(*Qs)["richardson"]
    ok(abs(rc - ex) < 1e-8 * ex and abs(rf - ex) > abs(rc - ex),
       "corrected vs frozen (sign-defect) Richardson")

    # --- THE NEW GATE -------------------------------------------------------
    # C1/C2 both hold: flat at a floor three decades inside
    flat = _series([1e-11, 9e-12, 1.1e-11] * 6)
    conv, g = gate_converged(flat)
    ok(conv and g["c1"] and g["c2"], "gate PASSES on a flat sub-floor series")
    ok(g["first_crossing"] == flat[0][0],
       "first crossing reported at the first interval under the floor")
    # C1 fails: the last interval sits above the floor
    up = _series([1e-11] * 15 + [3e-8])
    conv, g = gate_converged(up)
    ok((not conv) and (not g["c1"]), "gate FAILS C1 when r exceeds the floor")
    # C1 fails on SUSTAIN: one lucky final interval cannot pass
    lucky = _series([1e-11] * 13 + [5e-8, 5e-8, 1e-11])
    conv, g = gate_converged(lucky)
    ok((not conv) and (not g["c1"]),
       "gate FAILS: one interval under the floor is not a sustained floor")
    # C2 fails: a clean geometric climb, still entirely UNDER the floor
    climb = _series([1e-13 * (10 ** (0.25 * i)) for i in range(16)])
    ok(max(v for _, v, _ in climb) <= FLOOR, "the climbing series stays "
       "under the floor, so only C2 can catch it")
    conv, g = gate_converged(climb)
    ok((not conv) and g["c1"] and (not g["c2"]),
       "gate FAILS C2: a growing change under the floor is not converged")
    ok(g["cls"]["cls"] == "GROWING", "climbing series classifies GROWING")
    # C3: the field-space distance clause
    qs_ok = [(2000 * (i + 1), 1.5e-7 * (1 + 1e-11 * (-1) ** i))
             for i in range(30)]
    c3, c3d = gate_c3(qs_ok, end_time=60000)
    ok(c3 and c3d["t_half"] == 30000,
       "C3 passes on a stationary Q series and picks the mid-run checkpoint")
    # a target still marching at 9e-9 per interval -- INSIDE the floor,
    # so C1/C2 cannot see it; over half the run it accumulates past cum_tol
    qs_bad = [(2000 * (i + 1), 1.5e-7 * (1 + 9e-9 * (30 - i)))
              for i in range(30)]
    c3b, c3bd = gate_c3(qs_bad, end_time=60000)
    ok((not c3b) and c3bd["cum"] > CUM_TOL,
       "C3 FAILS on a Q still marching, even though each step is tiny")
    step = abs(qs_bad[-1][1] - qs_bad[-2][1]) / abs(qs_bad[-1][1])
    ok(step < FLOOR and not c3b,
       "C3 catches a case whose PER-INTERVAL change is inside the floor while "
       "its graded target is still moving -- exactly L-243's damping trap, "
       "which C1 and C2 cannot see")
    conv, g = gate_converged(_series([1e-11] * 16), qs_bad)
    ok((not conv) and g["c1"] and g["c2"] and (not g["c3"]),
       "gate FAILS on C3 alone: change stationary, target not")
    # classification paths
    dec = _series([1e-6 * (10 ** (-0.25 * i)) for i in range(16)])
    ok(classify_series(dec)["cls"] == "DECAYING", "DECAYING classified")
    ok(classify_series(_series([1e-11, 1.05e-11] * 8))["cls"] == "FLOOR",
       "FLOOR classified (no trend, tight spread)")
    lc = classify_series(_series([1e-11, 5e-10] * 8))
    ok(lc["cls"] == "LIMIT CYCLE" and lc["spread"] > SPREAD_TOL,
       "LIMIT CYCLE classified by p95/p05 spread")
    ok(classify_series(_series([0.0] * 16))["cls"] == "FLOOR",
       "an all-zero series is a FLOOR, not a fit error")
    # E4a's own last three F_c intervals bounce 1.54x and must NOT be growth
    e4a_fc = _series([7.707e-10, 4.919e-10, 1.189e-09] * 5)
    conv, g = gate_converged(e4a_fc)
    ok(conv and g["cls"]["cls"] in ("FLOOR", "LIMIT CYCLE"),
       "E4a's measured F_c bounce passes the gate (bounce at a floor is not "
       "growth) -- the E4a defect is not repeated in a new costume")

    # --- the floor arithmetic, recomputed from the registered numbers -------
    n_fan = max(c["ny"] for c in CASES.values())
    ok(n_fan == 18, "n_fan for the bound is the largest registered ny")
    dQ_rel = n_fan * FLOOR
    ok(abs(dQ_rel - 1.8e-7) < 1e-12, "|dQ|/|Q| bound = n_fan * floor = 1.8e-7")
    dev_pp = 100.0 * dQ_rel
    narrow = min(min(abs(ROWS[r]["prediction_dev_pct"] - ROWS[r]
                         ["interval_dev_pct"][0]),
                     abs(ROWS[r]["interval_dev_pct"][1] -
                         ROWS[r]["prediction_dev_pct"]))
                 for r in ("G1", "G2", "N1", "D1"))
    ok(abs(narrow - 0.117) < 1e-9, "narrowest graded dev half-width is D1's "
       "0.117 pp")
    ok(narrow / dev_pp > 1000.0,
       "the floor moves any graded dev row by >3 decades less than its "
       "narrowest half-width")
    # R1 binds: order sensitivity from the CARRIED-OVER section 1.5 arithmetic
    Qe = CURVES["A"]["Q_exact"]
    dev_c, dev_m, dev_f = 1.366, 0.497, 0.111          # section 1.5 net central
    e21 = Qe * (dev_m - dev_f) / 100.0
    e32 = Qe * (dev_c - dev_m) / 100.0
    lnr = math.log(REG["grid"]["r"])
    ok(abs(math.log(e32 / e21) / lnr - 2.0) < 5e-3,
       "section 1.5's arithmetic reproduces the registered order 2.00")
    S_p = (1.0 / (e32 * lnr) + (1.0 / e32 + 1.0 / e21) / lnr
           + 1.0 / (e21 * lnr))
    dQ = dQ_rel * Qe
    dp_order = S_p * dQ
    half = (ROWS["R1"]["interval"][1] - ROWS["R1"]["interval"][0]) / 2.0
    ok(abs(half - 0.4) < 1e-12, "R1 half-width is 0.40")
    ok(half / dp_order > 1000.0,
       "the floor moves R1's observed order by >3 decades less than its "
       "half-width (this is the BINDING bound on the floor)")
    ok(half / (S_p * Qe * n_fan * 1.3e-8) < 1000.0,
       "a floor of 1.3e-8 would NOT clear three decades on R1 -- the floor "
       "sits at the top of its admissible window, not chosen loosely")
    # C3's tolerance, recomputed from the registered numbers
    dQc = CUM_TOL * Qe
    ok(narrow / (100.0 * CUM_TOL) > 1000.0,
       "cum_tol moves any graded dev row by >3 decades less than its "
       "narrowest half-width")
    ok(half / (S_p * dQc) > 1000.0,
       "cum_tol moves R1's observed order by >3 decades less than its "
       "half-width (R1 binds here too)")
    ok(CUM_TOL / 3.886e-10 > 100.0,
       "cum_tol is >100x above E4a's worst measured |Q(t)-Q(end)|/|Q(end)| "
       "(3.886e-10, F_c at 5000)")
    # the write-precision floor
    ok(FLOOR / 1e-11 >= 1000.0,
       "the floor sits >=3 decades above the writePrecision-12 last-place "
       "quantum, so it cannot be reading ascii flicker")
    # feasibility, from E4a's measurement (cited, not derived from)
    ok(FLOOR / 1.189e-9 > 8.0,
       "the floor is >8x above E4a's worst measured r (1.189e-9, F_c phi)")
    # I1's disclosed weakening
    k2 = -dict((int(e), v) for v, e in CURVES["A"]["coeffs"])[2]
    lag = 2.0 * k2 * Qe * dQ
    ok(lag < ROWS["I1"]["tol_abs"],
       "the flux-lag bound under this floor is inside I1's carried tolerance")
    ok(0.5 * 0.015 ** 2 / lag > 1e4,
       "the convention-error signature is >4 decades above the flux-lag bound, "
       "so I1 still does the job it exists for")

    # --- file readers, planted zero, mutation through the readers -----------
    tmp = tempfile.mkdtemp(prefix="e4a2_selftest_")
    try:
        E4A._synthetic_field_files(tmp, ny, p, uu, phi, [Q / ny] * ny)
        ok(E4A.boundary_nfaces(tmp) == {"inlet": ny, "outlet": ny},
           "boundary nFaces parse")
        pr = E4A.patch_values(os.path.join(tmp, "20000", "p"), "inlet",
                              "scalar", ny)
        ur = E4A.patch_values(os.path.join(tmp, "20000", "U"), "inlet",
                              "vector", ny)
        fr = E4A.patch_values(os.path.join(tmp, "20000", "phi"), "inlet",
                              "scalar", ny)
        ok(pr == p and ur == uu and fr == phi, "readers round-trip repr floats")
        ok(E4A.identity_I1(pr, ur, fr, "A", 0.0)[0] < 1e-15,
           "identity through the file readers")
        E4A.plant_scalar(os.path.join(tmp, "20000", "p"),
                         os.path.join(tmp, "p_bad"), "inlet", 1e-6)
        pb = E4A.patch_values(os.path.join(tmp, "p_bad"), "inlet", "scalar", ny)
        ok(E4A.identity_I1(pb, ur, fr, "A", 0.0)[0] > ROWS["I1"]["tol_abs"],
           "mutation control THROUGH THE FILE READER flips I1")
        E4A.plant_scalar(os.path.join(tmp, "20000", "phi"),
                         os.path.join(tmp, "phi_bad"), "outlet", 1e-9)
        fo = E4A.patch_values(os.path.join(tmp, "phi_bad"), "outlet", "scalar",
                              ny)
        ok(abs(-sum(fr) - sum(fo)) / abs(sum(fr)) > ROWS["I2"]["tol_rel"],
           "mutation control flips I2")
        for fld, want, delta, planter in (
                ("p", "scalar", REG["planted_control"]["p"], E4A.plant_scalar),
                ("phi", "scalar", REG["planted_control"]["phi"],
                 E4A.plant_scalar),
                ("U", "vector", REG["planted_control"]["U"], E4A.plant_vector)):
            src = os.path.join(tmp, "20000", fld)
            dst = os.path.join(tmp, fld + "_planted")
            o, pl = planter(src, dst, "inlet", delta)
            got = E4A.patch_values(dst, "inlet", want, ny)
            g0 = got[0] if want == "scalar" else got[0][0]
            o_read = E4A.patch_values(src, "inlet", want, ny)
            o0 = o_read[0] if want == "scalar" else o_read[0][0]
            ok(g0 - o0 == pl - o0 and pl - o0 != 0.0,
               f"planted-zero exact-float rule on {fld}")
        shutil.copy(os.path.join(tmp, "20000", "p"), os.path.join(tmp, "p_c"))
        pc = E4A.patch_values(os.path.join(tmp, "p_c"), "inlet", "scalar", ny)
        ok(pc[0] - pr[0] == 0.0, "unplanted copy recovers exactly zero")
        # numeric_signature and the relative change, through real files
        sig = numeric_signature(tmp, 20000)
        ok(len(sig["p"]) == 1 + ny + ny and len(sig["U"]) == 3 * (1 + ny)
           and len(sig["phi"]) == 2 + 2 * ny,
           "numeric_signature counts internal + boundary values")
        shutil.copytree(os.path.join(tmp, "20000"),
                        os.path.join(tmp, "18000"))
        a = numeric_signature(tmp, 18000)
        b = numeric_signature(tmp, 20000)
        ok(all(a[f] == b[f] for f, _ in CONV_FIELDS),
           "identical checkpoints give an identical numeric signature")
        scale = max(abs(v) for v in b["p"])
        E4A.plant_scalar(os.path.join(tmp, "18000", "p"),
                         os.path.join(tmp, "18000", "p"), "inlet",
                         1e-9 * scale)
        a2 = numeric_signature(tmp, 18000)
        d = max(abs(x - y) for x, y in zip(a2["p"], b["p"])) / scale
        ok(abs(d - 1e-9) < 1e-12,
           "a planted 1e-9 relative change is recovered by the r_k reader")
        ok(d <= FLOOR, "and 1e-9 relative is INSIDE the registered floor -- "
           "the reader can see a change the gate tolerates")
        E4A.plant_scalar(os.path.join(tmp, "18000", "p"),
                         os.path.join(tmp, "18000", "p"), "inlet",
                         1e-7 * scale)
        a3 = numeric_signature(tmp, 18000)
        d3 = max(abs(x - y) for x, y in zip(a3["p"], b["p"])) / scale
        ok(d3 > FLOOR, "a 1e-7 relative plant is OUTSIDE the floor -- the "
           "reader is shown able to see a gate-failing change (rule 3's "
           "principle applied to the new gate)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # --- registered intervals contain their predictions ---------------------
    for row in ("G1", "G2", "N1", "D1"):
        lo, hi = ROWS[row]["interval_dev_pct"]
        pr_ = ROWS[row]["prediction_dev_pct"]
        ok(lo < hi and lo <= pr_ <= hi, f"{row} interval contains its "
                                        "prediction")
    lo, hi = ROWS["R1"]["interval"]
    ok(lo < hi and lo <= ROWS["R1"]["prediction"] <= hi,
       "R1 interval contains its prediction")
    ok(REG["time"]["writeInterval"] < REG["time"]["endTime"],
       "writeInterval strictly < endTime (L-140)")
    ok(REG["time"]["endTime"] // REG["time"]["writeInterval"] >= MIN_CKPT,
       "the registered controlDict produces at least the minimum checkpoints")
    ok(XC["tol_pp"] > 0 and "interval" not in XC and "prediction" not in XC,
       "X1 carries no interval and no prediction: it can only refuse")

    print(f"SELFTEST {n[0]}/{n[0]} OK")
    return EXIT_OK


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        provenance()
        sys.exit(selftest())
    sys.exit(main(sys.argv))
