#!/usr/bin/env python3
"""VMFL019 comparator -- Transient flow near a wall set in motion (Stokes' first
/ Rayleigh problem).

Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p. 77.
Reference: H. Schlichting & K. Gersten, Boundary Layer Theory, 8th ed.,
pp. 126-127 -- the closed-form similarity solution
    u(y,t) = U * erfc( y / (2 sqrt(nu t)) ),   U = 0.01 m/s   (ANALYTIC).

The manual gives only a FIGURE (no discrete target row), so the gate is against
the analytic value directly -- category V (code verification).  Two probes,
u_x at (0.375, 0.05, 0.005) and (0.375, 0.10, 0.005), at endTime t = 5 s.

Roache triple refines SPACE (Ny) and TIME (dt) together, ratio 2:
L1 Ny=30 dt=0.05, L2 Ny=60 dt=0.025, L3 Ny=120 dt=0.0125; endTime 5 s.

Committed BEFORE the pre-registration that cites it and before any solver runs
(rule 2).  REFUSES (exit 2) rather than degrades.  Structure adapted from the
frozen VMFL005/VMFL050 comparators (planted-zero, strict completion, Roache).

    python3 grade_vmfl019.py            # grade
    python3 grade_vmfl019.py --selftest
    python3 grade_vmfl019.py --dryrun-reader <probeU_file>
"""

import glob, json, math, os, re, shutil, sys, tempfile

CASE = "VMFL019"
MANUAL_PAGE = "77"

RHO = 1000.0          # kg/m3   (manual p. 77)
MU = 1.0              # kg/m-s  (manual p. 77)
NU = MU / RHO         # m2/s -> 1e-3 (what icoFoam is given)
UWALL = 0.01          # m/s, moving-wall velocity
TEND = 5.0            # s
YPROBES = (0.05, 0.10)   # m, the two gate locations

TOL_GATE = 0.01       # THE GATE: relative, |u_lab - u_analytic|/u_analytic, finest level
FS = 1.25
RATIO = 2.0
PLANT = 1.234e-03     # m/s, planted-zero perturbation (on u_x of probe 0)
PLANT_TOL = 1e-12
EPS_ABS = 1e-12       # m/s: level-to-level difference below this is zero
STAG_TOL = 1e-3

# name -> (Ny, deltaT).  coarse -> fine, ratio 2 both ways.  n_steps = TEND/dt.
LEVELS = (("L1_30", 30, 0.05), ("L2_60", 60, 0.025), ("L3_120", 120, 0.0125))

PROBE_FO = "probesU"
RUN_ROOT = "/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL019"
OUT_JSON = os.path.join(RUN_ROOT, "GRADING_VMFL019.json")
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


def refuse(msg):
    print("REFUSE: " + msg, file=sys.stderr)
    sys.exit(2)


def n_steps(deltaT):
    n = TEND / deltaT
    if abs(n - round(n)) > 1e-9:
        refuse("endTime %g not an integer multiple of deltaT %g" % (TEND, deltaT))
    return int(round(n))


def u_analytic(y, t):
    return UWALL * math.erfc(y / (2.0 * math.sqrt(NU * t)))


# --- reader: OpenFOAM vector-probe file  "time (x y z) (x y z) ..." ----------
_VEC = re.compile(r"\(\s*([-+0-9eE.]+)\s+([-+0-9eE.]+)\s+([-+0-9eE.]+)\s*\)")


def read_probe_ux(path):
    """Return [(time, [ux_probe0, ux_probe1, ...]), ...] -- x-components only."""
    if not os.path.isfile(path):
        refuse("probe file does not exist: " + path)
    rows = []
    for line in open(path, errors="replace"):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        mtime = re.match(r"\s*([-+0-9eE.]+)", s)
        if not mtime:
            refuse("no leading time token in %s: %r" % (path, s))
        t = float(mtime.group(1))
        vecs = _VEC.findall(s)
        if not vecs:
            refuse("no parenthesised vectors in %s: %r" % (path, s))
        rows.append((t, [float(v[0]) for v in vecs]))
    if not rows:
        refuse("no data rows in " + path)
    return rows


def find_probe_file(level_dir):
    pat = os.path.join(level_dir, "postProcessing", PROBE_FO, "*", "U")
    hits = sorted(glob.glob(pat))
    if len(hits) != 1:
        refuse("expected exactly one probe U file for %s, found %d" % (PROBE_FO, len(hits)))
    return hits[0]


def ux_at_end(level_dir):
    path = find_probe_file(level_dir)
    rows = read_probe_ux(path)
    match = [ux for (t, ux) in rows if abs(t - TEND) < 1e-6]
    if len(match) != 1:
        refuse("expected exactly one row at t=%g in %s, found %d" % (TEND, path, len(match)))
    ux = match[0]
    if len(ux) != len(YPROBES):
        refuse("expected %d probes, got %d in %s" % (len(YPROBES), len(ux), path))
    return ux, os.path.relpath(path, RUN_ROOT)


# --- planted-zero (rule 3): plant on u_x of probe 0 --------------------------
def _plant_probe0(path, plant):
    lines = open(path).read().split("\n")
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        mt = re.match(r"\s*([-+0-9eE.]+)", s)
        if mt and abs(float(mt.group(1)) - TEND) < 1e-6:
            vecs = _VEC.findall(s)
            before = float(vecs[0][0])
            # rewrite the FIRST vector's x-component
            def repl(m, done=[False]):
                if done[0]:
                    return m.group(0)
                done[0] = True
                return "(%r %s %s)" % (before + plant, m.group(2), m.group(3))
            lines[i] = _VEC.sub(repl, line, count=1)
            open(path, "w").write("\n".join(lines))
            back = read_probe_ux(path)
            got = [ux for (t, ux) in back if abs(t - TEND) < 1e-6][0][0]
            if abs((got - before) - plant) > PLANT_TOL:
                raise RuntimeError("plant did not land: %r -> %r" % (before, got))
            return before, got
    raise RuntimeError("no row at t=%g in %s" % (TEND, path))


def planted_zero_control(level_dir):
    src = find_probe_file(level_dir)
    before = ux_at_end(level_dir)[0][0]
    tmp = tempfile.mkdtemp(prefix="vmfl019plant_")
    try:
        work = os.path.join(tmp, "U")
        shutil.copy(src, work)
        b, a = _plant_probe0(work, PLANT)
        got = [ux for (t, ux) in read_probe_ux(work) if abs(t - TEND) < 1e-6][0][0]
        moved = got - before
        return dict(passed=abs(moved - PLANT) <= PLANT_TOL, planted=PLANT,
                    reader_delta=moved, file=os.path.basename(src))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- strict completion (rule 4) ----------------------------------------------
def _time_dirs(level_dir):
    out = []
    for d in os.listdir(level_dir):
        if os.path.isdir(os.path.join(level_dir, d)) and re.fullmatch(r"\d+(\.\d+)?", d):
            out.append(d)
    return sorted(out, key=float)


def strict_completion(level_dir, deltaT):
    name = os.path.basename(level_dir)
    if not os.path.isdir(level_dir):
        refuse("%s: run directory does not exist" % name)
    rc_path = os.path.join(level_dir, "RUN_RC.txt")
    if not os.path.isfile(rc_path):
        refuse("%s: no RUN_RC.txt" % name)
    m = re.search(r"^rc=(-?\d+)$", open(rc_path).read(), re.M)
    if not m:
        refuse("%s: RUN_RC.txt carries no rc" % name)
    rc = int(m.group(1))
    if rc != 0:
        refuse("%s: rc = %d (clause 1)" % (name, rc))
    log = os.path.join(level_dir, "log.icoFoam")
    if not os.path.isfile(log):
        refuse("%s: no log.icoFoam" % name)
    text = open(log, errors="replace").read()
    if not re.search(r"^End\s*$", text, re.M):
        refuse("%s: no 'End' line (clause 2)" % name)
    times = _time_dirs(level_dir)
    if not times or abs(float(times[-1]) - TEND) > 1e-6:
        refuse("%s: last time %r, endTime %g (clause 3)" % (name, times[-1] if times else None, TEND))
    tdir = os.path.join(level_dir, times[-1])
    for f in ("U", "p"):
        if not os.path.isfile(os.path.join(tdir, f)):
            refuse("%s: field %s missing at endTime (clause 4)" % (name, f))
    n_exec = len(re.findall(r"^ExecutionTime = ", text, re.M))
    expect = n_steps(deltaT)
    if n_exec != expect:
        refuse("%s: %d ExecutionTime lines, expected %d = endTime/dt (clause 5)" % (name, n_exec, expect))
    marker = os.path.join(level_dir, "0", "U")
    if not os.path.isfile(marker):
        refuse("%s: no 0/U age-guard marker (clause 6)" % name)
    t_marker = os.path.getmtime(marker)
    for f in ("U", "p"):
        if not os.path.getmtime(os.path.join(tdir, f)) > t_marker:
            refuse("%s: endTime/%s NOT newer than 0/U -- AGE GUARD (clause 6)" % (name, f))
    return dict(rc=rc, endTime=float(times[-1]), n_exec=n_exec, expect_steps=expect,
                fields_at_endTime=["U", "p"], age_guard="fields newer than 0/U")


def levers(level_dir, ny):
    name = os.path.basename(level_dir)
    tp = os.path.join(level_dir, "constant", "transportProperties")
    m = re.search(r"^\s*nu\s+\[[^\]]*\]\s+([0-9eE.+-]+)\s*;", open(tp).read(), re.M)
    if not m:
        refuse("%s: nu not readable" % name)
    nu_ran = float(m.group(1))
    if abs(nu_ran - NU) / NU > 1e-6:
        refuse("%s: nu = %g in run, %g registered" % (name, nu_ran, NU))
    out = dict(nu=nu_ran)
    cm = os.path.join(level_dir, "log.checkMesh")
    if os.path.isfile(cm):
        ctext = open(cm, errors="replace").read()
        m2 = re.search(r"^\s*cells:\s+(\d+)", ctext, re.M)
        expect = 4 * ny
        if m2 and int(m2.group(1)) != expect:
            refuse("%s: checkMesh %s cells, expected 4*%d=%d" % (name, m2.group(1), ny, expect))
        out["mesh"] = dict(cells=int(m2.group(1)) if m2 else None, mesh_ok=("Mesh OK" in ctext))
    else:
        out["mesh"] = "unverifiable-from-logs"
    return out


def roache(f_coarse, f_med, f_fine, ratio=RATIO, fs=FS):
    d21 = f_med - f_fine
    d32 = f_coarse - f_med
    out = dict(f_coarse=f_coarse, f_med=f_med, f_fine=f_fine, d21=d21, d32=d32,
               ratio=ratio, fs=fs, p=None, R=None, gci_fine=None, f_extrapolated=None)
    if abs(d21) < EPS_ABS and abs(d32) < EPS_ABS:
        out["state"] = "EXACT"; return out
    if abs(d32) < EPS_ABS:
        out["state"] = "DIVERGENT"; out["why"] = "d32<EPS while d21 not"; return out
    R_ = d21 / d32
    out["R"] = R_
    if R_ < 0:
        out["state"] = "OSCILLATORY"; return out
    if abs(R_ - 1.0) <= STAG_TOL:
        out["state"] = "STAGNANT"; return out
    if R_ > 1.0:
        out["state"] = "DIVERGENT"; return out
    p = math.log(1.0 / R_) / math.log(ratio)
    out["p"] = p; out["state"] = "CONVERGING"
    denom = ratio ** p - 1.0
    if denom <= 0:
        out["state"] = "DIVERGENT"; out["why"] = "r^p-1<=0"; return out
    out["gci_fine"] = fs * abs(d21 / f_fine) / denom
    out["f_extrapolated"] = f_fine + (f_fine - f_med) / denom
    return out


def main():
    print("=" * 78)
    print("%s -- Transient flow near a wall set in motion (Stokes' first problem)" % CASE)
    print("Ansys FD Verification Manual 2026 R1, p. %s" % MANUAL_PAGE)
    print("reference: Schlichting & Gersten, Boundary Layer Theory 8th ed. (analytic erfc)")
    print("=" * 78)
    print("  nu = mu/rho = %.3e m2/s ; U_wall = %.3f m/s ; t = %.1f s" % (NU, UWALL, TEND))
    for y in YPROBES:
        print("  analytic u_x(y=%.2f, %.0f) = %.6e m/s" % (y, TEND, u_analytic(y, TEND)))

    results, completion = {}, {}
    for name, ny, dt in LEVELS:
        d = os.path.join(RUN_ROOT, name)
        completion[name] = strict_completion(d, dt)
        completion[name]["levers"] = levers(d, ny)
        ux, src = ux_at_end(d)
        results[name] = dict(ux=ux, src=src)

    fine = LEVELS[-1][0]
    pz = planted_zero_control(os.path.join(RUN_ROOT, fine))
    print("\nplanted-zero control on %s: %s" % (fine, json.dumps(pz)))
    if not pz["passed"]:
        refuse("planted-zero control failed: reader cannot see %g m/s planted" % PLANT)

    # Roache triple + gate per probe
    triples, gate = {}, {}
    for j, y in enumerate(YPROBES):
        fc = results[LEVELS[0][0]]["ux"][j]
        fm = results[LEVELS[1][0]]["ux"][j]
        ff = results[LEVELS[2][0]]["ux"][j]
        tr = roache(fc, fm, ff)
        ana = u_analytic(y, TEND)
        rel = abs(ff - ana) / abs(ana)
        triples["y=%.2f" % y] = tr
        gate["y=%.2f" % y] = dict(lab=ff, analytic=ana, rel=rel, ok=(rel <= TOL_GATE), state=tr["state"])

    all_conv = all(g["state"] == "CONVERGING" for g in gate.values())
    all_gate = all(g["ok"] for g in gate.values())
    if not all_conv:
        verdict = "NOT A RESULT"
        why = "grid triple not CONVERGING: " + ", ".join("%s %s" % (k, v["state"]) for k, v in gate.items())
    else:
        verdict = "PASS" if all_gate else "GATE FAIL"
        why = ("both probes within %.1f%% of the analytic erfc profile" % (TOL_GATE * 100)
               if all_gate else "; ".join("%s rel %.3f%% %s" % (k, v["rel"] * 100, "ok" if v["ok"] else "OUT")
                                          for k, v in gate.items()))
    assert verdict in VERDICTS

    print("\n--- gate: |u_lab - u_analytic|/u_analytic <= %.3f at %s ---" % (TOL_GATE, fine))
    for k in gate:
        g = gate[k]; tr = triples[k]
        print("  %s  u_lab %.6e  analytic %.6e  rel %.4f%%  %s  | Roache %s R %s p %s GCI %s" % (
            k, g["lab"], g["analytic"], g["rel"] * 100, "ok" if g["ok"] else "OUT", tr["state"],
            "n/a" if tr["R"] is None else "%.4f" % tr["R"],
            "n/a" if tr["p"] is None else "%.4f" % tr["p"],
            "n/a" if tr["gci_fine"] is None else "%.3e" % tr["gci_fine"]))
    print("\nVERDICT: %s -- %s" % (verdict, why))

    payload = dict(case=CASE, manual_page=MANUAL_PAGE, verdict=verdict, why=why,
                   nu=NU, Uwall=UWALL, tend=TEND, gate=gate, triples=triples,
                   levels=results, completion=completion, planted_zero=pz,
                   comparator=os.path.abspath(__file__))
    os.makedirs(RUN_ROOT, exist_ok=True)
    with open(OUT_JSON, "w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True, default=str)
    print("grading written to %s" % OUT_JSON)
    return 0


# --- selftest ----------------------------------------------------------------
def _write_probe(path, endvals):
    """endvals = [ux0, ux1]; writes a real vector-probe file with a ramp."""
    with open(path, "w") as fh:
        fh.write("# Probe 0 (0.375 0.05 0.005)\n# Probe 1 (0.375 0.1 0.005)\n")
        fh.write("#        Time\n")
        for i in range(1, 11):
            t = TEND * i / 10.0
            f = 0.5 + 0.5 * i / 10.0
            fh.write("%g\t(%r 0 0)\t(%r 0 0)\n" % (t, endvals[0] * f, endvals[1] * f))


def selftest():
    ok = True
    def check(label, cond, detail=""):
        nonlocal ok
        print("  [%s] %s%s" % ("PASS" if cond else "FAIL", label, "" if not detail else "  <- " + str(detail)))
        ok = ok and bool(cond)

    print("--- selftest: analytic erfc profile ---")
    check("u(0.05,5) ~ 6.1708e-3", abs(u_analytic(0.05, 5.0) - 6.170751e-3) < 1e-7, u_analytic(0.05, 5.0))
    check("u(0.10,5) ~ 3.1731e-3", abs(u_analytic(0.10, 5.0) - 3.173105e-3) < 1e-7, u_analytic(0.10, 5.0))
    check("nu == 1e-3", abs(NU - 1e-3) < 1e-15, NU)

    tmp = tempfile.mkdtemp(prefix="vmfl019self_")
    try:
        print("--- selftest: vector-probe reader ---")
        f = os.path.join(tmp, "U"); _write_probe(f, [6.17e-3, 3.17e-3])
        rows = read_probe_ux(f)
        check("reader parses 10 rows, 2 probes", len(rows) == 10 and len(rows[-1][1]) == 2, (len(rows), len(rows[-1][1])))
        end = [ux for (t, ux) in rows if abs(t - TEND) < 1e-6]
        check("reader recovers t=5 ux0", len(end) == 1 and abs(end[0][0] - 6.17e-3) < 1e-9, end)

        print("--- selftest: reader REFUSES a row with no vector (exit 2) ---")
        def refuses(fn):
            pid = os.fork()
            if pid == 0:
                os.dup2(os.open(os.devnull, os.O_WRONLY), 2)
                try: fn()
                except SystemExit as e: os._exit(e.code if isinstance(e.code, int) else 1)
                os._exit(0)
            _, st = os.waitpid(pid, 0)
            return os.WIFEXITED(st) and os.WEXITSTATUS(st) == 2
        bad = os.path.join(tmp, "bad"); open(bad, "w").write("5   0.006\n")
        check("no-vector row REFUSED exit 2", refuses(lambda: read_probe_ux(bad)))

        print("--- selftest: planted-zero on u_x of probe 0, and negative arm ---")
        work = os.path.join(tmp, "plantU"); _write_probe(work, [6.17e-3, 3.17e-3])
        before = [ux for (t, ux) in read_probe_ux(work) if abs(t - TEND) < 1e-6][0][0]
        _plant_probe0(work, PLANT)
        after = [ux for (t, ux) in read_probe_ux(work) if abs(t - TEND) < 1e-6][0][0]
        check("reader sees planted %g m/s" % PLANT, abs((after - before) - PLANT) <= PLANT_TOL, after - before)
        work2 = os.path.join(tmp, "npU"); _write_probe(work2, [6.17e-3, 3.17e-3])
        after2 = [ux for (t, ux) in read_probe_ux(work2) if abs(t - TEND) < 1e-6][0][0]
        check("unplanted copy unchanged", abs(after2 - before) < 1e-15)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("--- selftest: Roache classifier ---")
    fex, C = 6.17e-3, 1e-4
    t1 = roache(fex + C * 4, fex + C * 2, fex + C * 1)
    check("first-order -> CONVERGING p==1", t1["state"] == "CONVERGING" and abs(t1["p"] - 1.0) < 1e-9, t1["p"])
    check("Richardson recovers f_exact", abs(t1["f_extrapolated"] - fex) < 1e-9)
    t2 = roache(fex + C * 16, fex + C * 4, fex + C * 1)
    check("second-order -> p==2", t2["state"] == "CONVERGING" and abs(t2["p"] - 2.0) < 1e-9, t2["p"])
    check("divergent -> DIVERGENT", roache(1.0, 1.1, 1.4)["state"] == "DIVERGENT")
    check("oscillatory -> OSCILLATORY", roache(1.0, 1.2, 1.0)["state"] == "OSCILLATORY")
    check("identical -> EXACT", roache(2.5, 2.5, 2.5)["state"] == "EXACT")

    print("--- selftest: the gate can fail and can pass ---")
    ana = u_analytic(0.05, 5.0)
    check("+2%% is outside gate", abs(ana * 1.02 - ana) / ana > TOL_GATE)
    check("+0.5%% is inside gate", abs(ana * 1.005 - ana) / ana <= TOL_GATE)

    print("\nSELFTEST: %s" % ("all checks passed" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


def dryrun_reader(path):
    rows = read_probe_ux(path)
    print("dryrun-reader: parsed, %d rows, %d probes/row" % (len(rows), len(rows[-1][1])))
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--dryrun-reader" in sys.argv:
        i = sys.argv.index("--dryrun-reader")
        sys.exit(dryrun_reader(sys.argv[i + 1]))
    sys.exit(main())
