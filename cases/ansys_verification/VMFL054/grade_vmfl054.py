#!/usr/bin/env python3
# =============================================================================
# VMFL054 comparator -- Laminar flow in a Trapezoidal Driven Cavity (VM2026R1 p.173).
#
# DRAFT (ansys-lane-opus48, claude-opus-4-8[1m]). NOT THE FREEZE COMMIT. The
# ansys-verification-supervisor performs the §3 check-4 freeze; this file is drafted
# for that read.
#
# WHAT THIS COMPARATOR GATES (this round, a-priori, figure-independent):
#   a GRID-CONVERGENCE (Roache) verification of u_x at the cavity geometric centre
#   (x=1.0, y=0.5) over an r=2 triple L1/L2/L3. The external Darr & Vanka (1991)
#   normalized-velocity PROFILE is the manual's reference; its values live ONLY in a
#   plotted figure (the .txt sidecar strips figures), so the validation limb is
#   DEFERRED and is NOT in the frozen gate this round (PREREGISTRATION.md sec.6/10).
#   THEREFORE THIS COMPARATOR NEVER EMITS `PASS`: at most `GATE REACHED` (the
#   grid-convergence gate met), else `GATE FAIL`, and `NOT A RESULT` if the triple
#   is not CONVERGING or a level is not iteratively converged (CLAUDE.md rule 5).
#
# THREE guards, each of which has bitten this lab, each REFUSING with exit 2:
#   (1) PLANTED-ZERO (rule 3), on BOTH readers the gate depends on -- the probe-file
#       reader AND the U-field reader. A known delta is planted into a COPY, read
#       back, and the control REFUSES if the reader cannot see it.
#   (2) STRICT COMPLETION (rule 4): the solver rc (persisted as RUN_RC by the driver),
#       an End line AND absence of a FOAM FATAL, latest-time fields present, the age
#       guard (fields NEWER than the case's own 0/), and iterative convergence. Any
#       failed limb REFUSES rather than grading a partial run.
#       TWO rule-4 limbs are DELIBERATELY INAPPLICABLE here and are NOT checked, by
#       design: `last time == endTime` and the `ExecutionTime` count. This is a
#       residualControl-terminated STEADY solve -- it stops when residuals fall below
#       the floor, at a time BEFORE endTime; requiring last==endTime would pass only a
#       run that never converged (ran out of clock). VMFL038/VMFL063 grade on exactly
#       this basis (supervisor's diff read, 2026-09-02).
#   (3) KNOWN-BAD INPUT: a corrupted probe file is fed to the reader and the reader
#       MUST refuse -- proving the guard can say no, not merely that it can say yes.
#
# Run `grade_vmfl054.py --selftest` to exercise all three guards with synthetic
# data (no graded solve needed); `grade_vmfl054.py <run_root>` to grade a real run.
# =============================================================================
import os, sys, re, shutil, tempfile, math

# ---- frozen constants (a-priori; never set from a run) ----------------------
GATE_POINT      = (1.0, 0.5)      # cavity geometric centre (trapezoid axis, mid-height)
R_REFINE        = 2.0             # grid refinement ratio
FS              = 1.25            # Roache GCI safety factor
P_OBS_LO        = 1.0             # a-priori observed-order band (formal order 2; a
P_OBS_HI        = 3.0             #   driven cavity has corner singularities -> generous)
GCI_FINE_MAX    = 0.05            # a-priori: 5 % fine-grid GCI to reach the gate
RESID_FLOOR     = 1.0e-6          # a-priori iterative-convergence floor (final residual)
K_PLANT         = 0.05            # plant magnitude as a fraction of |gate value|
PLANT_MIN_ABS   = 1.0e-12
FIELDS          = ("U", "p")

class SystemExit2(SystemExit):
    def __init__(self, msg): super().__init__(2); self.msg = msg
def refuse(msg):
    sys.stderr.write("REFUSE (exit 2): %s\n" % msg); raise SystemExit2(msg)

# ---- readers ----------------------------------------------------------------
def read_probe_ux(path):
    """The GATE reader. Parse an OpenFOAM `probes` output file, return u_x at the
    LAST (latest-time) data row. Refuses on anything it cannot parse unambiguously
    -- a reader that guesses can misread (guard 3 exercises this refusal)."""
    if not os.path.isfile(path):
        refuse("probe file absent: %s" % path)
    last = None
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            m = re.match(r"^([0-9eE+\-.]+)\s+\(\s*([0-9eE+\-.]+)\s+([0-9eE+\-.]+)\s+([0-9eE+\-.]+)\s*\)\s*$", s)
            if not m:
                refuse("probe line not parseable (a malformed/NaN row is a refusal, "
                       "not a guess): %r in %s" % (s, path))
            last = (float(m.group(1)), float(m.group(2)))   # (time, u_x)
    if last is None:
        refuse("probe file has no data row: %s" % path)
    return last[1]

def read_U_internal_x(path):
    """The physical-field reader: x-components of the U internalField vector list."""
    if not os.path.isfile(path):
        refuse("U field absent: %s" % path)
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<vector>\s*\n\s*(\d+)\s*\n\(\s*\n(.*?)\n\)\s*;", txt, re.S)
    if not m:
        refuse("U internalField is not a nonuniform vector list: %s" % path)
    xs = []
    for row in m.group(2).splitlines():
        row = row.strip()
        if not row: continue
        mm = re.match(r"^\(\s*([0-9eE+\-.]+)\s+([0-9eE+\-.]+)\s+([0-9eE+\-.]+)\s*\)$", row)
        if not mm:
            refuse("U internalField row not parseable: %r in %s" % (row, path))
        xs.append(float(mm.group(1)))
    if not xs:
        refuse("U internalField list is empty: %s" % path)
    return xs, m.span()

def latest_time_dir(level_dir):
    times = []
    for d in os.listdir(level_dir):
        full = os.path.join(level_dir, d)
        if os.path.isdir(full) and re.match(r"^[0-9]+(\.[0-9]+)?$", d) and d != "0":
            times.append((float(d), d, full))
    if not times:
        refuse("no numeric time dir (other than 0) in %s" % level_dir)
    return max(times)[1:]   # (name, path)

def current_probe_file(level_dir):
    """The gate reader's source. `probes` writes postProcessing/centreProbe/<startTime>/U;
    a RESTART adds a SECOND <time> subdir. A hardcoded '0/' would silently grade stale
    pre-restart data with no complaint, so enumerate the subdirs and REFUSE on ambiguity
    -- a reader that guesses can misread (line 55)."""
    base = os.path.join(level_dir, "postProcessing", "centreProbe")
    if not os.path.isdir(base):
        refuse("no postProcessing/centreProbe in %s" % level_dir)
    subs = sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)))
    if len(subs) == 0:
        refuse("centreProbe has no time subdir in %s" % level_dir)
    if len(subs) > 1:
        refuse("centreProbe has %d time subdirs %s in %s -- a restart wrote more than one; "
               "REFUSING rather than guessing which is current" % (len(subs), subs, level_dir))
    f = os.path.join(base, subs[0], "U")
    if not os.path.isfile(f):
        refuse("centreProbe/%s/U missing in %s" % (subs[0], level_dir))
    return f

# ---- planted-zero controls (rule 3) -----------------------------------------
def plant_probe(path):
    """Plant a known delta into a COPY of the probe file the gate reads; read it
    back; refuse if the reader does not see it."""
    base = read_probe_ux(path)
    plant = K_PLANT * abs(base)
    if plant < PLANT_MIN_ABS:
        refuse("planted-zero: |gate value| %.3g too small to size a plant against" % base)
    tmp = tempfile.mkdtemp(prefix="vmfl054_plant_probe_")
    try:
        dst = os.path.join(tmp, "U")
        lines = open(path).read().splitlines()
        out = []
        for line in lines:
            s = line.strip()
            m = re.match(r"^([0-9eE+\-.]+)\s+\(\s*([0-9eE+\-.]+)\s+([0-9eE+\-.]+)\s+([0-9eE+\-.]+)\s*\)\s*$", s)
            if m:
                out.append("%s (%.12g %s %s)" % (m.group(1), float(m.group(2)) + plant, m.group(3), m.group(4)))
            else:
                out.append(line)
        open(dst, "w").write("\n".join(out) + "\n")
        seen = read_probe_ux(dst)
        err = abs((seen - base) - plant)
        if not (err <= 1.0e-9 * max(abs(plant), 1.0)):
            refuse("planted-zero FAILED (probe reader): planted %.12g, read-back error %.3g "
                   "-- the gate reader cannot see a non-zero (rule 3)" % (plant, err))
        return {"reader": "probe", "plant": plant, "readback_error": err, "passed": True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def plant_U_field(path):
    """Plant a known delta into a COPY of the U internalField (the physical field);
    read it back; refuse if unseen."""
    xs, _ = read_U_internal_x(path)
    scale = max(abs(v) for v in xs)
    plant = K_PLANT * scale
    if plant < PLANT_MIN_ABS:
        refuse("planted-zero: U field max|u_x| %.3g too small to size a plant" % scale)
    tmp = tempfile.mkdtemp(prefix="vmfl054_plant_U_")
    try:
        dst = os.path.join(tmp, "U")
        txt = open(path).read()
        _, span = read_U_internal_x(path)
        block = txt[span[0]:span[1]]
        block2 = re.sub(r"\(\s*([0-9eE+\-.]+)\s+([0-9eE+\-.]+)\s+([0-9eE+\-.]+)\s*\)",
                        lambda mo: "(%.12g %s %s)" % (float(mo.group(1)) + plant, mo.group(2), mo.group(3)),
                        block)
        open(dst, "w").write(txt[:span[0]] + block2 + txt[span[1]:])
        seen, _ = read_U_internal_x(dst)
        if len(seen) != len(xs):
            refuse("planted-zero: U cell count changed across the plant")
        worst = max(abs((seen[i] - xs[i]) - plant) for i in range(len(xs)))
        if not (worst <= 1.0e-9 * max(abs(plant), 1.0)):
            refuse("planted-zero FAILED (U-field reader): planted %.12g, worst read-back error "
                   "%.3g -- the field reader cannot see a non-zero (rule 3)" % (plant, worst))
        return {"reader": "U_field", "plant": plant, "readback_error": worst, "passed": True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

# ---- strict completion (rule 4) ---------------------------------------------
def check_completion(level_dir):
    # rule-4 rc limb: the driver persists the solver rc as RUN_RC. Missing or nonzero
    # REFUSES. (last==endTime and the ExecutionTime count are deliberately inapplicable
    # to a residualControl-terminated steady solve -- see header -- and not checked.)
    rcf = os.path.join(level_dir, "RUN_RC")
    if not os.path.isfile(rcf):
        refuse("RUN_RC absent in %s -- cannot confirm solver rc==0 (rule 4)" % level_dir)
    rc = open(rcf).read().strip()
    if rc != "0":
        refuse("solver rc=%s (not 0) in %s (rule 4)" % (rc, level_dir))
    log = os.path.join(level_dir, "log.simpleFoam")
    if not os.path.isfile(log):
        refuse("no log.simpleFoam in %s" % level_dir)
    logtxt = open(log).read()
    if "FOAM FATAL" in logtxt:
        refuse("FOAM FATAL in %s -- solver errored (rule 4)" % log)
    if logtxt.count("\nEnd\n") < 1 and not logtxt.rstrip().endswith("End"):
        refuse("no 'End' line in %s -- run did not finish cleanly (rule 4)" % log)
    tname, tpath = latest_time_dir(level_dir)
    zero_mtime = os.path.getmtime(os.path.join(level_dir, "0", "U"))
    for f in FIELDS:
        fp = os.path.join(tpath, f)
        if not os.path.isfile(fp):
            refuse("field %s missing at latest time %s (rule 4)" % (f, tname))
        if not (os.path.getmtime(fp) > zero_mtime):
            refuse("age guard (rule 4): %s at time %s is NOT newer than the case's own 0/U "
                   "-- the time dir predates this run" % (f, tname))
    # iterative convergence: final Ux/p initial residual below the frozen floor.
    resids = re.findall(r"Solving for Ux, Initial residual = ([0-9eE+\-.]+)", logtxt)
    presids = re.findall(r"Solving for p, Initial residual = ([0-9eE+\-.]+)", logtxt)
    if not resids or not presids:
        refuse("no residual history in %s" % log)
    ux_last, p_last = float(resids[-1]), float(presids[-1])
    converged = (ux_last < RESID_FLOOR and p_last < RESID_FLOOR)
    return {"time": tname, "ux_resid": ux_last, "p_resid": p_last, "converged": converged}

# ---- Roache triple ----------------------------------------------------------
def roache(f1, f2, f3):
    """f1 coarse (L1), f2 med (L2), f3 fine (L3); r=2. Returns state + p + GCI."""
    d12, d23 = (f2 - f1), (f3 - f2)
    if abs(d23) < 1e-30:
        return {"state": "EXACT", "R": 0.0, "p": None, "gci_fine": None,
                "f": (f1, f2, f3), "note": "fine two levels identical -> no order"}
    R = d23 / d12 if abs(d12) > 1e-30 else float("inf")
    if not (0.0 < R < 1.0):
        state = "DIVERGENT" if abs(R) >= 1.0 else "OSCILLATORY"
        if R < 0: state = "OSCILLATORY"
        return {"state": state, "R": R, "p": None, "gci_fine": None, "f": (f1, f2, f3)}
    p = math.log(abs(d12 / d23)) / math.log(R_REFINE)
    gci = FS * abs(d23 / f3) / (R_REFINE ** p - 1.0) if abs(f3) > 1e-30 else None
    return {"state": "CONVERGING", "R": R, "p": p, "gci_fine": gci, "f": (f1, f2, f3)}

# ---- grade a real run -------------------------------------------------------
def grade(run_root):
    levels = ("L1", "L2", "L3")
    vals, comp = {}, {}
    for L in levels:
        ld = os.path.join(run_root, L)
        if not os.path.isdir(ld):
            refuse("level dir missing: %s" % ld)
        comp[L] = check_completion(ld)                     # guard 2 (rule 4)
        tname, tpath = latest_time_dir(ld)
        plant_U_field(os.path.join(tpath, "U"))            # guard 1b (rule 3, physical field)
        probe = current_probe_file(ld)                     # D3: enumerate, refuse on restart ambiguity
        plant_probe(probe)                                 # guard 1a (rule 3, gate reader)
        vals[L] = read_probe_ux(probe)
    # rule 5 step 1: every level iteratively converged, else NOT A RESULT
    for L in levels:
        if not comp[L]["converged"]:
            print("VERDICT: NOT A RESULT -- %s not iteratively converged "
                  "(Ux resid %.3g, p resid %.3g vs floor %.3g)"
                  % (L, comp[L]["ux_resid"], comp[L]["p_resid"], RESID_FLOOR))
            return 0
    tri = roache(vals["L1"], vals["L2"], vals["L3"])
    print("triple u_x(centre): L1=%.9g L2=%.9g L3=%.9g state=%s R=%.4g p=%s GCI_fine=%s"
          % (vals["L1"], vals["L2"], vals["L3"], tri["state"], tri["R"],
             ("%.4g" % tri["p"]) if tri["p"] is not None else "n/a",
             ("%.4g%%" % (100*tri["gci_fine"])) if tri["gci_fine"] is not None else "n/a"))
    if tri["state"] != "CONVERGING":
        print("VERDICT: NOT A RESULT -- Roache triple %s (rule 5 step 2)" % tri["state"])
        return 0
    ok = (P_OBS_LO <= tri["p"] <= P_OBS_HI) and (tri["gci_fine"] <= GCI_FINE_MAX)
    # NEVER PASS: external Darr & Vanka validation is deferred (figure-pending).
    print("VERDICT: %s -- grid-convergence gate %s (p in [%.1f,%.1f]? %s; GCI_fine<=%.1f%%? %s). "
          "PASS withheld: external Darr&Vanka validation deferred (figure digitization)."
          % ("GATE REACHED" if ok else "GATE FAIL",
             "MET" if ok else "NOT MET", P_OBS_LO, P_OBS_HI,
             P_OBS_LO <= tri["p"] <= P_OBS_HI, 100*GCI_FINE_MAX, tri["gci_fine"] <= GCI_FINE_MAX))
    return 0

# ---- selftest: exercise all three guards on synthetic data ------------------
def selftest():
    tmp = tempfile.mkdtemp(prefix="vmfl054_selftest_")
    ok = True
    try:
        # (a) probe plant fires on a live reader
        good = os.path.join(tmp, "probe_U")
        open(good, "w").write("# Probe 0 (1 0.5 0)\n# Time\n300 (-168.65 22.6 4.5e-17)\n")
        r = plant_probe(good); print("SELFTEST 1a probe planted-zero: PASS (%s)" % r)
        # (b) U-field plant fires
        uf = os.path.join(tmp, "U")
        open(uf, "w").write("internalField   nonuniform List<vector>\n3\n(\n(-168.6 1 0)\n(50 2 0)\n(10 -3 0)\n)\n;\n")
        r = plant_U_field(uf); print("SELFTEST 1b U-field planted-zero: PASS (%s)" % r)
        # (c) known-bad input MUST refuse
        bad = os.path.join(tmp, "probe_bad")
        open(bad, "w").write("# Probe 0\n# Time\n300 (nan garbage here\n")
        try:
            read_probe_ux(bad); print("SELFTEST 2 known-bad guard: FAIL -- reader did NOT refuse"); ok = False
        except SystemExit2:
            print("SELFTEST 2 known-bad guard: PASS -- reader refused (exit 2) on a corrupt row")
        # (d) Roache classifier on synthetic monotone + oscillatory triples
        tc = roache(10.0, 10.24, 10.29)
        print("SELFTEST 3a converging triple: state=%s p=%.4g GCI=%.4g%%"
              % (tc["state"], tc["p"], 100*tc["gci_fine"]))
        if tc["state"] != "CONVERGING": ok = False
        to = roache(10.0, 10.5, 10.1)
        print("SELFTEST 3b oscillatory triple: state=%s (expect OSCILLATORY)" % to["state"])
        if to["state"] != "OSCILLATORY": ok = False
        # ---- guard 2: STRICT COMPLETION arms (D2 -- the one guard with no test) ----
        import time as _t
        def mklevel(root, name, end=True, field_p=True, age_ok=True, rc="0"):
            ld = os.path.join(root, name); os.makedirs(os.path.join(ld, "0"))
            open(os.path.join(ld, "0", "U"), "w").write("x")
            t0 = _t.time(); os.utime(os.path.join(ld, "0", "U"), (t0, t0))
            td = os.path.join(ld, "100"); os.makedirs(td)
            open(os.path.join(td, "U"), "w").write("x")
            if field_p: open(os.path.join(td, "p"), "w").write("x")
            ft = t0 + (10 if age_ok else -10)   # field NEWER (ok) or OLDER (age violation) than 0/U
            os.utime(os.path.join(td, "U"), (ft, ft))
            if field_p: os.utime(os.path.join(td, "p"), (ft, ft))
            logtxt = "Solving for Ux, Initial residual = 1e-8\nSolving for p, Initial residual = 1e-9\n"
            if end: logtxt += "End\n"
            open(os.path.join(ld, "log.simpleFoam"), "w").write(logtxt)
            open(os.path.join(ld, "RUN_RC"), "w").write(rc)
            return ld
        def expect_refuse(label, **kw):
            nonlocal ok
            try:
                check_completion(mklevel(tmp, label, **kw))
                print("SELFTEST %s: FAIL -- check_completion did NOT refuse" % label); ok = False
            except SystemExit2:
                print("SELFTEST %s: PASS -- check_completion refused (exit 2)" % label)
        try:
            check_completion(mklevel(tmp, "4good"))
            print("SELFTEST 4good completion: PASS -- clean level accepted")
        except SystemExit2:
            print("SELFTEST 4good completion: FAIL -- refused a clean level"); ok = False
        expect_refuse("4a-noEnd", end=False)
        expect_refuse("4b-missingField", field_p=False)
        expect_refuse("4c-ageGuard", age_ok=False)
        expect_refuse("4d-rc", rc="1")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SELFTEST: %s" % ("ALL PASS" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    if len(sys.argv) != 2:
        sys.stderr.write("usage: grade_vmfl054.py <run_root> | --selftest\n"); sys.exit(64)
    try:
        sys.exit(grade(sys.argv[1]))
    except SystemExit2 as e:
        sys.exit(2)
