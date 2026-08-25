#!/usr/bin/env python3
"""VMFL050 comparator -- Transient heat conduction in a semi-infinite slab.

Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p. 163.
Reference: F.P. Incropera et al., Introduction to Heat Transfer, 5th ed.,
Wiley, p. 287 (semi-infinite solid, constant surface heat flux -- ANALYTIC).

THIS FILE IS THE GRADING PATH.  Committed BEFORE the pre-registration that cites
it by sha and before any solver runs (CLAUDE.md rule 2).  It REFUSES (exit 2)
rather than degrades; every refusal names the clause.  Structure and controls
adapted from the frozen VMFL005 comparator (planted-zero, strict completion,
Roache triple, selftest, --dryrun-reader).

Two gate quantities, both at t = 120 s:
  * wallT  -- surfaceFieldValue areaAverage(T) on the heatedWall patch (the
    boundary temperature = analytic wall temperature).
  * probe150 -- probes cellPoint T at (0.15, 0.005, 0.005), 150 mm from the wall.

The Roache triple refines SPACE AND TIME TOGETHER (ratio 2): L1 Nx=75 dt=2,
L2 Nx=150 dt=1, L3 Nx=300 dt=0.5 -- so the triple measures the combined
space-time discretisation error and Richardson extrapolates toward the exact
analytic value.

    python3 grade_vmfl050.py                    # grade the run tree
    python3 grade_vmfl050.py --selftest         # synthetic, no solver
    python3 grade_vmfl050.py --dryrun-reader P  # parse a real file, row count only
"""

import glob, json, math, os, re, shutil, sys, tempfile

CASE = "VMFL050"
MANUAL_PAGE = "163"

# physical constants (manual p. 163)
K_COND = 401.0        # W/m-K
RHO = 8995.67         # kg/m3
CP = 381.0            # J/kg-K
QFLUX = 3.0e5         # W/m2
TI = 293.0            # K, initial/uniform
TEND = 120.0          # s
XPROBE = 0.15         # m
ALPHA = K_COND / (RHO * CP)   # m2/s thermal diffusivity == laplacianFoam DT

# manual Table .50.1 targets (Ansys Fluent column is context only)
MANUAL_WALL = 393.0        # K, THE GATE reference for the wall
MANUAL_P150 = 318.4        # K, THE GATE reference for the 150 mm point
FLUENT_WALL = 392.95       # context only, never the gate
FLUENT_P150 = 318.41       # context only, never the gate

TOL_GATE = 0.01            # THE GATE: relative, on the temperature RISE (T-TI),
                           # against the manual target, at the finest level
TOL_DIAG = 0.01            # diagnostic: relative rise vs the exact analytic value

FS = 1.25
RATIO = 2.0
PLANT = 1.234              # K, planted-zero perturbation
PLANT_TOL = 1e-9
EPS_ABS = 1e-9             # K: a level-to-level difference below this is zero
STAG_TOL = 1e-3            # |R-1| <= STAG_TOL => STAGNANT

# name -> (Nx, deltaT, n_steps=TEND/deltaT).  coarse -> fine, ratio 2 both ways.
LEVELS = (("L1_75", 75, 2.0), ("L2_150", 150, 1.0), ("L3_300", 300, 0.5))

WALL_FO = "wallT"
PROBE_FO = "probe150"
SFV_FILE = "surfaceFieldValue.dat"

RUN_ROOT = "/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL050"
OUT_JSON = os.path.join(RUN_ROOT, "GRADING_VMFL050.json")
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


def refuse(msg):
    print("REFUSE: " + msg, file=sys.stderr)
    sys.exit(2)


def n_steps(deltaT):
    n = TEND / deltaT
    if abs(n - round(n)) > 1e-9:
        refuse("endTime %g is not an integer multiple of deltaT %g" % (TEND, deltaT))
    return int(round(n))


# --- analytic reference (Incropera, constant surface heat flux) --------------
def T_analytic(x, t):
    a = 2.0 * QFLUX * math.sqrt(ALPHA * t / math.pi) / K_COND
    if x == 0.0:
        return TI + a
    return (TI + a * math.exp(-x * x / (4.0 * ALPHA * t))
            - (QFLUX * x / K_COND) * math.erfc(x / (2.0 * math.sqrt(ALPHA * t))))


# --- reader: a 2-column '# '-headed .dat/probe file (time, value) ------------
def read_series(path):
    if not os.path.isfile(path):
        refuse("series file does not exist: " + path)
    rows = []
    for line in open(path, errors="replace"):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) < 2:
            refuse("data row has %d columns, expected >= 2 (time value) in %s: %r"
                   % (len(parts), path, s))
        try:
            rows.append((float(parts[0]), float(parts[1])))
        except ValueError:
            refuse("unparseable data row in %s: %r" % (path, s))
    if not rows:
        refuse("no data rows in " + path)
    return rows


def find_wall_file(level_dir):
    pat = os.path.join(level_dir, "postProcessing", WALL_FO, "*", SFV_FILE)
    hits = sorted(glob.glob(pat))
    if len(hits) != 1:
        refuse("expected exactly one %s for %s, found %d" % (SFV_FILE, WALL_FO, len(hits)))
    return hits[0]


def find_probe_file(level_dir):
    pat = os.path.join(level_dir, "postProcessing", PROBE_FO, "*", "T")
    hits = sorted(glob.glob(pat))
    if len(hits) != 1:
        refuse("expected exactly one probe T file for %s, found %d" % (PROBE_FO, len(hits)))
    return hits[0]


def value_at_end(path):
    rows = read_series(path)
    match = [v for (t, v) in rows if abs(t - TEND) < 1e-6]
    if len(match) != 1:
        refuse("expected exactly one row at t=%g in %s, found %d" % (TEND, path, len(match)))
    return match[0]


def quantities(level_dir):
    wf = find_wall_file(level_dir)
    pf = find_probe_file(level_dir)
    return dict(wallT=value_at_end(wf), p150=value_at_end(pf),
                wall_src=os.path.relpath(wf, RUN_ROOT),
                probe_src=os.path.relpath(pf, RUN_ROOT))


# --- planted-zero control (rule 3) -------------------------------------------
def _plant(path, plant):
    lines = open(path).read().split("\n")
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) >= 2 and abs(float(parts[0]) - TEND) < 1e-6:
            before = float(parts[1])
            parts[1] = repr(before + plant)
            lines[i] = "\t".join(parts)
            open(path, "w").write("\n".join(lines))
            back = value_at_end(path)
            if abs((back - before) - plant) > PLANT_TOL:
                raise RuntimeError("plant did not land: %r -> %r" % (before, back))
            return before, back
    raise RuntimeError("no row at t=%g in %s" % (TEND, path))


def planted_zero_control(level_dir):
    out = {}
    for label, finder in (("wallT", find_wall_file), ("p150", find_probe_file)):
        src = finder(level_dir)
        before = value_at_end(src)
        tmp = tempfile.mkdtemp(prefix="vmfl050plant_")
        try:
            work = os.path.join(tmp, os.path.basename(src))
            shutil.copy(src, work)
            b, a = _plant(work, PLANT)
            seen = value_at_end(work)
            moved = seen - before
            out[label] = dict(passed=abs(moved - PLANT) <= PLANT_TOL,
                              planted=PLANT, reader_delta=moved,
                              file=os.path.basename(src))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return out


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
        refuse("%s: no RUN_RC.txt -- the run did not finish this level" % name)
    m = re.search(r"^rc=(-?\d+)$", open(rc_path).read(), re.M)
    if not m:
        refuse("%s: RUN_RC.txt carries no rc" % name)
    rc = int(m.group(1))
    if rc != 0:
        refuse("%s: rc = %d (strict completion clause 1)" % (name, rc))
    log = os.path.join(level_dir, "log.laplacianFoam")
    if not os.path.isfile(log):
        refuse("%s: no log.laplacianFoam" % name)
    text = open(log, errors="replace").read()
    if not re.search(r"^End\s*$", text, re.M):
        refuse("%s: no 'End' line in log (clause 2)" % name)
    times = _time_dirs(level_dir)
    if not times or abs(float(times[-1]) - TEND) > 1e-6:
        refuse("%s: last time is %r, endTime is %g (clause 3)"
               % (name, times[-1] if times else None, TEND))
    tdir = os.path.join(level_dir, times[-1])
    if not os.path.isfile(os.path.join(tdir, "T")):
        refuse("%s: field T missing at endTime (clause 4)" % name)
    n_exec = len(re.findall(r"^ExecutionTime = ", text, re.M))
    expect = n_steps(deltaT)
    if n_exec != expect:
        refuse("%s: %d ExecutionTime lines, expected %d = endTime/deltaT (clause 5)"
               % (name, n_exec, expect))
    marker = os.path.join(level_dir, "0", "T")
    if not os.path.isfile(marker):
        refuse("%s: no 0/T age-guard marker (clause 6)" % name)
    t_marker = os.path.getmtime(marker)
    t_f = os.path.getmtime(os.path.join(tdir, "T"))
    if not t_f > t_marker:
        refuse("%s: endTime/T (%.3f) is NOT newer than 0/T (%.3f) -- AGE GUARD (clause 6)"
               % (name, t_f, t_marker))
    return dict(rc=rc, endTime=float(times[-1]), n_exec=n_exec, expect_steps=expect,
                fields_at_endTime=["T"], age_guard="T newer than 0/T")


def levers(level_dir, nx):
    name = os.path.basename(level_dir)
    tp = os.path.join(level_dir, "constant", "transportProperties")
    m = re.search(r"^\s*DT\s+DT\s+\[[^\]]*\]\s+([0-9eE.+-]+)\s*;", open(tp).read(), re.M)
    if not m:
        refuse("%s: DT not readable from transportProperties" % name)
    dt_ran = float(m.group(1))
    if abs(dt_ran - ALPHA) / ALPHA > 1e-6:
        refuse("%s: DT = %g in the run, alpha = %g was registered" % (name, dt_ran, ALPHA))
    out = dict(DT=dt_ran)
    cm = os.path.join(level_dir, "log.checkMesh")
    if os.path.isfile(cm):
        ctext = open(cm, errors="replace").read()
        m2 = re.search(r"^\s*cells:\s+(\d+)", ctext, re.M)
        if m2 and int(m2.group(1)) != nx:
            refuse("%s: checkMesh reports %s cells, level is %d" % (name, m2.group(1), nx))
        out["mesh"] = dict(cells=int(m2.group(1)) if m2 else None, mesh_ok=("Mesh OK" in ctext))
    else:
        out["mesh"] = "unverifiable-from-logs"
    return out


# --- Roache triple (rule 5) --------------------------------------------------
def roache(f_coarse, f_med, f_fine, ratio=RATIO, fs=FS):
    d21 = f_med - f_fine
    d32 = f_coarse - f_med
    out = dict(f_coarse=f_coarse, f_med=f_med, f_fine=f_fine, d21=d21, d32=d32,
               ratio=ratio, fs=fs, p=None, R=None, gci_fine=None, f_extrapolated=None)
    if abs(d21) < EPS_ABS and abs(d32) < EPS_ABS:
        out["state"] = "EXACT"; return out
    if abs(d32) < EPS_ABS:
        out["state"] = "DIVERGENT"; out["why"] = "d32 below EPS_ABS while d21 is not"; return out
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


def _verdict_for(triple, lab_fine, manual_ref):
    """Given a CONVERGING/other triple and the finest value, return (verdict, why,
    rel_manual, gate_ok) for one quantity.  Gate is on the RISE (value-TI)."""
    rise_lab = lab_fine - TI
    rise_ref = manual_ref - TI
    rel = abs(rise_lab - rise_ref) / abs(rise_ref)
    gate_ok = rel <= TOL_GATE
    return rel, gate_ok


def main():
    print("=" * 78)
    print("%s -- Transient heat conduction in a semi-infinite slab" % CASE)
    print("Ansys FD Verification Manual 2026 R1, p. %s" % MANUAL_PAGE)
    print("reference: Incropera, Introduction to Heat Transfer 5th ed. (analytic)")
    print("=" * 78)
    print("  alpha = k/(rho*cp) = %.9e m2/s" % ALPHA)
    print("  analytic wall  T(0,120)    = %.6f K   (manual target %.1f)" % (T_analytic(0.0, TEND), MANUAL_WALL))
    print("  analytic 150mm T(0.15,120) = %.6f K   (manual target %.1f)" % (T_analytic(XPROBE, TEND), MANUAL_P150))

    results, completion = {}, {}
    for name, nx, dt in LEVELS:
        d = os.path.join(RUN_ROOT, name)
        completion[name] = strict_completion(d, dt)
        completion[name]["levers"] = levers(d, nx)
        results[name] = quantities(d)

    fine = LEVELS[-1][0]
    pz = planted_zero_control(os.path.join(RUN_ROOT, fine))
    print("\nplanted-zero control on %s: %s" % (fine, json.dumps(pz)))
    for label in ("wallT", "p150"):
        if not pz[label]["passed"]:
            refuse("planted-zero control failed on %s: the reader cannot see a "
                   "%g K planted difference; its numbers mean nothing" % (label, PLANT))

    # Roache triple per quantity
    tw = roache(results[LEVELS[0][0]]["wallT"], results[LEVELS[1][0]]["wallT"], results[LEVELS[2][0]]["wallT"])
    tp = roache(results[LEVELS[0][0]]["p150"], results[LEVELS[1][0]]["p150"], results[LEVELS[2][0]]["p150"])

    wall_fine = results[fine]["wallT"]
    p150_fine = results[fine]["p150"]
    rel_w, gate_w = _verdict_for(tw, wall_fine, MANUAL_WALL)
    rel_p, gate_p = _verdict_for(tp, p150_fine, MANUAL_P150)
    diag_w = abs((wall_fine - TI) - (T_analytic(0.0, TEND) - TI)) / abs(T_analytic(0.0, TEND) - TI)
    diag_p = abs((p150_fine - TI) - (T_analytic(XPROBE, TEND) - TI)) / abs(T_analytic(XPROBE, TEND) - TI)

    triples_converging = (tw["state"] == "CONVERGING" and tp["state"] == "CONVERGING")
    if not triples_converging:
        verdict = "NOT A RESULT"
        why = "grid triple not CONVERGING (wallT %s, p150 %s) (rule 5)" % (tw["state"], tp["state"])
    else:
        gate_ok = gate_w and gate_p
        verdict = "PASS" if gate_ok else "GATE FAIL"
        why = ("both quantities within %.1f%% of manual target on the rise" % (TOL_GATE * 100)
               if gate_ok else "wallT rel %.3f%% (%s), p150 rel %.3f%% (%s) vs %.1f%% gate"
               % (rel_w * 100, "ok" if gate_w else "OUT", rel_p * 100, "ok" if gate_p else "OUT", TOL_GATE * 100))
    assert verdict in VERDICTS

    print("\n--- gate: |rise_lab - rise_manual| / rise_manual <= %.3f at %s ---" % (TOL_GATE, fine))
    print("  wallT %10.6f K  manual %.1f  rise-rel %.4f%%  %s   (diag vs exact %.4f%%)"
          % (wall_fine, MANUAL_WALL, rel_w * 100, "ok" if gate_w else "OUT", diag_w * 100))
    print("  p150  %10.6f K  manual %.1f  rise-rel %.4f%%  %s   (diag vs exact %.4f%%)"
          % (p150_fine, MANUAL_P150, rel_p * 100, "ok" if gate_p else "OUT", diag_p * 100))
    for label, tr in (("wallT", tw), ("p150", tp)):
        print("  Roache %s: state %s  R %s  p %s  GCI_fine %s" % (
            label, tr["state"],
            "n/a" if tr["R"] is None else "%.6f" % tr["R"],
            "n/a" if tr["p"] is None else "%.4f" % tr["p"],
            "n/a" if tr["gci_fine"] is None else "%.4e" % tr["gci_fine"]))
    print("\nVERDICT: %s -- %s" % (verdict, why))

    payload = dict(case=CASE, manual_page=MANUAL_PAGE, verdict=verdict, why=why,
                   alpha=ALPHA,
                   gate=dict(tol=TOL_GATE,
                             wallT=dict(lab=wall_fine, manual=MANUAL_WALL, rise_rel=rel_w, ok=gate_w),
                             p150=dict(lab=p150_fine, manual=MANUAL_P150, rise_rel=rel_p, ok=gate_p)),
                   diagnostic=dict(tol=TOL_DIAG,
                                   exact_wall=T_analytic(0.0, TEND), rel_wall=diag_w,
                                   exact_p150=T_analytic(XPROBE, TEND), rel_p150=diag_p),
                   ansys_context=dict(fluent_wall=FLUENT_WALL, fluent_p150=FLUENT_P150),
                   triple_wallT=tw, triple_p150=tp, levels=results,
                   completion=completion, planted_zero=pz,
                   comparator=os.path.abspath(__file__))
    os.makedirs(RUN_ROOT, exist_ok=True)
    with open(OUT_JSON, "w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True, default=str)
    print("grading written to %s" % OUT_JSON)
    return 0


# --- selftest ----------------------------------------------------------------
def _write_sfv(path, endvalue):
    with open(path, "w") as fh:
        fh.write("# Region type : patch heatedWall\n")
        fh.write("# Faces : 1\n")
        fh.write("# Time            \tareaAverage(T)\n")
        for i in range(1, 21):
            t = int(round(TEND * i / 20))
            fh.write("%d\t%r\n" % (t, endvalue * (0.9 + 0.1 * i / 20)))


def selftest():
    ok = True
    def check(label, cond, detail=""):
        nonlocal ok
        print("  [%s] %s%s" % ("PASS" if cond else "FAIL", label, "" if not detail else "  <- " + str(detail)))
        ok = ok and bool(cond)

    print("--- selftest: analytic reference matches the manual targets ---")
    check("analytic wall  == 393 to the manual's 3 s.f.", abs(T_analytic(0.0, TEND) - MANUAL_WALL) < 0.5, T_analytic(0.0, TEND))
    check("analytic 150mm == 318.4 to the manual's 4 s.f.", abs(T_analytic(XPROBE, TEND) - MANUAL_P150) < 0.05, T_analytic(XPROBE, TEND))
    check("alpha == 1.17e-4 m2/s", abs(ALPHA - 1.17e-4) < 1e-9, ALPHA)

    tmp = tempfile.mkdtemp(prefix="vmfl050self_")
    try:
        print("--- selftest: reader on the real 2-column format ---")
        f = os.path.join(tmp, SFV_FILE)
        _write_sfv(f, 393.0)
        rows = read_series(f)
        check("reader parses 20 rows", len(rows) == 20, len(rows))
        check("value_at_end recovers t=120 row", abs(value_at_end(f) - 393.0) < 1e-9, value_at_end(f))

        print("--- selftest: reader REFUSES a one-column row (exit 2) ---")
        def refuses(fn):
            pid = os.fork()
            if pid == 0:
                os.dup2(os.open(os.devnull, os.O_WRONLY), 2)
                try: fn()
                except SystemExit as e: os._exit(e.code if isinstance(e.code, int) else 1)
                os._exit(0)
            _, st = os.waitpid(pid, 0)
            return os.WIFEXITED(st) and os.WEXITSTATUS(st) == 2
        bad = os.path.join(tmp, "bad.dat")
        open(bad, "w").write("# h\n120\n")
        check("one-column row REFUSED with exit 2", refuses(lambda: read_series(bad)))

        print("--- selftest: planted-zero positive arm and negative arm ---")
        work = os.path.join(tmp, "plant.dat"); _write_sfv(work, 393.0)
        before = value_at_end(work); _plant(work, PLANT); after = value_at_end(work)
        check("reader sees the planted %g K" % PLANT, abs((after - before) - PLANT) <= PLANT_TOL, after - before)
        work2 = os.path.join(tmp, "np.dat"); _write_sfv(work2, 393.0)
        check("unplanted copy unchanged", abs(value_at_end(work2) - before) < 1e-9)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("--- selftest: Roache classifier ---")
    fex, C = 393.0266, 0.05
    t1 = roache(fex + C * 4, fex + C * 2, fex + C * 1)
    check("first-order family -> CONVERGING, p==1", t1["state"] == "CONVERGING" and abs(t1["p"] - 1.0) < 1e-9, t1["p"])
    check("Richardson recovers f_exact", abs(t1["f_extrapolated"] - fex) < 1e-9, t1["f_extrapolated"])
    t2 = roache(fex + C * 16, fex + C * 4, fex + C * 1)
    check("second-order family -> CONVERGING, p==2", t2["state"] == "CONVERGING" and abs(t2["p"] - 2.0) < 1e-9, t2["p"])
    check("divergent -> DIVERGENT", roache(1.0, 1.1, 1.4)["state"] == "DIVERGENT")
    check("oscillatory -> OSCILLATORY", roache(1.0, 1.2, 1.0)["state"] == "OSCILLATORY")
    check("equal-step -> STAGNANT", roache(1.0, 1.1, 1.2)["state"] == "STAGNANT")
    check("identical -> EXACT", roache(2.5, 2.5, 2.5)["state"] == "EXACT")

    print("--- selftest: the gate can fail and can pass (on the rise) ---")
    rise_ref = MANUAL_WALL - TI
    lab_bad = TI + rise_ref * 1.02
    lab_good = TI + rise_ref * 1.005
    check("+2%% rise is outside the gate", abs((lab_bad - TI) - rise_ref) / rise_ref > TOL_GATE)
    check("+0.5%% rise is inside the gate", abs((lab_good - TI) - rise_ref) / rise_ref <= TOL_GATE)

    print("\nSELFTEST: %s" % ("all checks passed" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


def dryrun_reader(path):
    rows = read_series(path)
    print("dryrun-reader: parsed, %d rows" % len(rows))
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--dryrun-reader" in sys.argv:
        i = sys.argv.index("--dryrun-reader")
        sys.exit(dryrun_reader(sys.argv[i + 1]))
    sys.exit(main())
