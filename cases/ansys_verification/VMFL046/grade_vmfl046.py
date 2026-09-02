#!/usr/bin/env python3
# =============================================================================
# VMFL046 comparator -- Supersonic flow with a normal shock in a CD nozzle (p.155).
# DRAFT (ansys-lane-opus48). NOT THE FREEZE COMMIT.
#
# GATE (a-priori; the smoke's numbers were NOT used to set any constant below -- rule 2,
# the VMFL029 lesson). The reference is the INVISCID quasi-1D Euler solution
# (quasi1d_reference.py) for the frozen contour + back-pressure; the case solved is
# VISCOUS 2-D compressible NS. Under Amendment 1.6 / VERIFICATION_CHARTER 2h.6.1
# (sameness of model) that DIFFERENCE caps the verdict at GATE REACHED unless the
# supervisor rules the models "the same" for the centreline-Mach quantity. THEREFORE
# THIS COMPARATOR NEVER EMITS PASS: at most GATE REACHED, else GATE FAIL, else
# NOT A RESULT (rule 5). First-order upwind is the frozen scheme (the higher-order
# scheme diverges on negative-T at the shock, this lab's VMFL017), so the observed
# Roache order is expected ~1 and the bands below reflect that a-priori, not the run.
#
# Three guards, each REFUSING exit 2: (1) planted-zero on BOTH readers the gate uses
# (the centreline sample reader AND the T-field reader); (2) strict completion (rule 4:
# rc via RUN_RC, End + no FOAM FATAL, fields present, age guard, iterative convergence;
# last==endTime and ExecutionTime-count are deliberately inapplicable to a
# residualControl-terminated steady solve); (3) known-bad input refusal. Exercise all:
#   grade_vmfl046.py --selftest   |   grade_vmfl046.py <run_root>
# =============================================================================
import os, sys, re, shutil, tempfile, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quasi1d_reference as q

# ---- frozen constants (a-priori; NEVER from a run) --------------------------
GAMMA = 1.4
R_GAS = 287.0                      # J/kg-K, air (Cp 1004.5, molWeight 28.96)
# Contour frozen in blockMeshDict.template: throat x=0.5, in/throat area 2, exit/throat 3.
NOZ_L, NOZ_XT = 2.0, 0.5
AR_IN, AR_EXIT = 2.0, 3.0          # area ratios wrt throat
P0_ABS, PEXIT_ABS = 301325.0, 176325.0   # inlet total / outlet static (documented op. pressure)
# Gate station: pre-shock, chosen from the ANALYTICAL shock location (a-priori computable
# from contour+back-pressure), NOT from the CFD smoke. Analytical shock ~x=1.25, so 0.9
# is safely pre-shock supersonic and smooth.
M_GATE_X        = 0.9
R_REFINE        = 2.0
FS              = 1.25
P_OBS_LO        = 0.5              # first-order upwind -> formal order ~1; generous band
P_OBS_HI        = 2.5
GCI_FINE_MAX    = 0.15            # DEMOTE-ONLY secondary (§21.3): may turn PASS->GATE FAIL,
                                 # NEVER license a PASS; contaminated-loose (built after coarse
                                 # numbers seen), so a secondary that does NOT fire is NOT
                                 # evidence of quality.
SHOCK_TOL       = 0.05           # PRIMARY: shock location within 5% of analytical (the only
                                 # a-priori-clean limb comparing this solve to the reference;
                                 # model-form bound 0.18-0.63% << 5%, §12.2 SAME per v1.18)
MACH_DEV_TOL    = 0.10           # DEMOTE-ONLY secondary (§21.3), same caveat as GCI_FINE_MAX
# CONVERGENCE (charter v1.17/v1.18 §22.5): the gate-quantity PLATEAU replaces the residual
# floor. delta_M = |1.882125 - 1.8817| = §18's reference-reproduction spread (generator vs
# NACA-1135), measured for §18 BEFORE the production run, so uncontaminated by it. Iteration
# noise below the reference's own uncertainty cannot move a verdict that compares to it.
DELTA_M         = 4.25e-4        # Mach; plateau threshold, BINDING incl. if it fails -> LTS
W_PLATEAU       = 500            # iterations between the two samples the plateau compares
K_PLANT         = 0.05
PLANT_MIN_ABS   = 1.0e-12
FIELDS          = ("U", "T", "p")

class SystemExit2(SystemExit):
    def __init__(self, msg): super().__init__(2); self.msg = msg
def refuse(msg):
    sys.stderr.write("REFUSE (exit 2): %s\n" % msg); raise SystemExit2(msg)

# ---- analytical reference for THIS contour (built once, a-priori) ------------
def analytical_profile(nx=201):
    xs = [NOZ_L*i/(nx-1) for i in range(nx)]
    it = min(range(nx), key=lambda i: abs(xs[i]-NOZ_XT))
    def h(x):
        return (AR_IN + (1.0-AR_IN)*(x/NOZ_XT)) if x <= NOZ_XT \
               else (1.0 + (AR_EXIT-1.0)*(x-NOZ_XT)/(NOZ_L-NOZ_XT))
    ar = [h(x)/h(NOZ_XT) for x in xs]
    M, s = q.mach_distribution(ar, it, PEXIT_ABS/P0_ABS)
    return xs, M, xs[s]

def interp(xs, ys, x0):
    if x0 <= xs[0]: return ys[0]
    if x0 >= xs[-1]: return ys[-1]
    for i in range(len(xs)-1):
        if xs[i] <= x0 <= xs[i+1]:
            t = (x0-xs[i])/(xs[i+1]-xs[i]); return ys[i]*(1-t)+ys[i+1]*t
    return ys[-1]

# ---- readers ----------------------------------------------------------------
def read_centreline(path):
    """The GATE reader. Parse the sampled centreline (raw .xy: columns x T Ux Uy Uz),
    return [(x, Mach)]. Refuses on any unparseable/NaN row -- a reader that guesses can
    misread (guard 3)."""
    if not os.path.isfile(path):
        refuse("centreline sample absent: %s" % path)
    out = []
    for line in open(path):
        s = line.strip()
        if not s or s.startswith("#"): continue
        p = s.split()
        if len(p) != 5:
            refuse("centreline row has %d cols, expected 5 (x T Ux Uy Uz): %r in %s" % (len(p), s, path))
        try:
            x, T, ux, uy, uz = (float(v) for v in p)
        except ValueError:
            refuse("centreline row not numeric (NaN/garbage is a refusal, not a guess): %r in %s" % (s, path))
        if T <= 0.0:
            refuse("centreline T<=0 (%.6g) at x=%.4g -- unphysical, refusing rather than sqrt(neg)" % (T, x))
        U = math.sqrt(ux*ux+uy*uy+uz*uz); a = math.sqrt(GAMMA*R_GAS*T)
        out.append((x, U/a))
    if len(out) < 10:
        refuse("centreline has %d usable rows (<10): %s" % (len(out), path))
    return out

def read_T_internal(path):
    if not os.path.isfile(path): refuse("T field absent: %s" % path)
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n\s*(\d+)\s*\n\(\s*\n(.*?)\n\)\s*;", txt, re.S)
    if not m: refuse("T internalField is not a nonuniform scalar list: %s" % path)
    vals = []
    for row in m.group(2).splitlines():
        row = row.strip()
        if not row: continue
        try: vals.append(float(row))
        except ValueError: refuse("T internalField row not parseable: %r in %s" % (row, path))
    if not vals: refuse("T internalField empty: %s" % path)
    return vals, m.span()

def latest_time_dir(level_dir):
    times = [(float(d), d, os.path.join(level_dir, d)) for d in os.listdir(level_dir)
             if os.path.isdir(os.path.join(level_dir, d)) and re.match(r"^[0-9]+(\.[0-9]+)?$", d) and d != "0"]
    if not times: refuse("no numeric time dir (other than 0) in %s" % level_dir)
    return max(times)[1:]

def centreline_history(level_dir):
    """The centreline sample is written every W_PLATEAU iterations; return the full history
    [(time, path)] sorted by time, so the comparator can test the M(0.9) plateau over the
    last W_PLATEAU-iteration window (§22.5)."""
    base = os.path.join(level_dir, "postProcessing", "centreline")
    if not os.path.isdir(base): refuse("no postProcessing/centreline in %s" % level_dir)
    hist = []
    for d in os.listdir(base):
        p = os.path.join(base, d, "line_T_U.xy")
        if re.match(r"^[0-9]+(\.[0-9]+)?$", d) and os.path.isfile(p):
            hist.append((float(d), p))
    hist.sort()
    if len(hist) < 2:
        refuse("centreline history has %d samples (<2); the plateau needs the last two "
               "W_PLATEAU-apart samples (§22.5): %s" % (len(hist), base))
    return hist

def plateau_and_gate(level_dir):
    """Return (plateau_ok, dM_window, M_gate, x_shock) from the last two centreline samples.
    Convergence (§22.5): |M(0.9)_last - M(0.9)_{last-W}| < DELTA_M. The two samples must be
    exactly W_PLATEAU apart (writeInterval == W_PLATEAU), else refuse rather than guess."""
    hist = centreline_history(level_dir)
    t_last, p_last = hist[-1]; t_prev, p_prev = hist[-2]
    if abs((t_last - t_prev) - W_PLATEAU) > 1e-6:
        refuse("last two centreline samples are %g apart, expected W_PLATEAU=%g (§22.5): %s"
               % (t_last - t_prev, W_PLATEAU, level_dir))
    cl_last = read_centreline(p_last); cl_prev = read_centreline(p_prev)
    M_last = interp([x for x,_ in cl_last], [m for _,m in cl_last], M_GATE_X)
    M_prev = interp([x for x,_ in cl_prev], [m for _,m in cl_prev], M_GATE_X)
    dM = abs(M_last - M_prev)
    return (dM < DELTA_M), dM, M_last, shock_location(cl_last), p_last

# ---- planted-zero controls (rule 3) -----------------------------------------
def plant_centreline(path):
    """Plant a known velocity delta into a COPY of the centreline sample; the reader must
    see the resulting Mach rise. Refuses if it cannot."""
    base = read_centreline(path)
    ig = min(range(len(base)), key=lambda i: abs(base[i][0]-M_GATE_X))
    base_M = base[ig][1]
    plant_ux = K_PLANT * 300.0     # a fixed velocity plant (m/s), reader-sized
    tmp = tempfile.mkdtemp(prefix="vmfl046_plant_c_")
    try:
        dst = os.path.join(tmp, "line_T_U.xy"); out = []
        for line in open(path):
            s = line.strip()
            if not s or s.startswith("#"): out.append(line.rstrip("\n")); continue
            p = s.split()
            if len(p) == 5:
                p[2] = "%.10g" % (float(p[2]) + plant_ux)   # bump Ux
            out.append("\t".join(p))
        open(dst, "w").write("\n".join(out)+"\n")
        seen = read_centreline(dst)
        seen_M = seen[ig][1]
        if not (seen_M > base_M + 1e-9):
            refuse("planted-zero FAILED (centreline reader): Ux+%.3g did not raise Mach at x=%.2f "
                   "(%.6g -> %.6g) -- the gate reader cannot see a non-zero (rule 3)" % (plant_ux, M_GATE_X, base_M, seen_M))
        return {"reader": "centreline", "plant_ux": plant_ux, "M_base": base_M, "M_seen": seen_M, "passed": True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def plant_T_field(path):
    vals, span = read_T_internal(path)
    scale = max(abs(v) for v in vals); plant = K_PLANT*scale
    if plant < PLANT_MIN_ABS: refuse("planted-zero: T field scale %.3g too small" % scale)
    tmp = tempfile.mkdtemp(prefix="vmfl046_plant_T_")
    try:
        # Rebuild the internalField block deterministically from the parsed values (a
        # regex bump would also hit the COUNT line and corrupt the list header).
        dst = os.path.join(tmp, "T"); txt = open(path).read()
        bumped = [v + plant for v in vals]
        newblock = ("internalField   nonuniform List<scalar>\n%d\n(\n%s\n)\n;"
                    % (len(bumped), "\n".join("%.10g" % v for v in bumped)))
        open(dst, "w").write(txt[:span[0]] + newblock + txt[span[1]:])
        seen, _ = read_T_internal(dst)
        if len(seen) != len(vals): refuse("planted-zero: T cell count changed across the plant")
        worst = max(abs((seen[i]-vals[i]) - plant) for i in range(len(vals)))
        if not (worst <= 1e-6*max(abs(plant),1.0)):
            refuse("planted-zero FAILED (T-field reader): planted %.6g, worst read-back error %.3g (rule 3)" % (plant, worst))
        return {"reader": "T_field", "plant": plant, "readback_error": worst, "passed": True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---- strict completion (rule 4) ---------------------------------------------
def check_completion(level_dir):
    rcf = os.path.join(level_dir, "RUN_RC")
    if not os.path.isfile(rcf): refuse("RUN_RC absent in %s (rule 4 rc limb)" % level_dir)
    rc = open(rcf).read().strip()
    if rc != "0": refuse("solver rc=%s (not 0) in %s (rule 4)" % (rc, level_dir))
    log = os.path.join(level_dir, "log.rhoSimpleFoam")
    if not os.path.isfile(log): refuse("no log.rhoSimpleFoam in %s" % level_dir)
    logtxt = open(log).read()
    if "FOAM FATAL" in logtxt: refuse("FOAM FATAL in %s (rule 4)" % log)
    if logtxt.count("\nEnd\n") < 1 and not logtxt.rstrip().endswith("End"):
        refuse("no 'End' line in %s (rule 4)" % log)
    tname, tpath = latest_time_dir(level_dir)
    zero_mtime = os.path.getmtime(os.path.join(level_dir, "0", "T"))
    for f in FIELDS:
        fp = os.path.join(tpath, f)
        if not os.path.isfile(fp): refuse("field %s missing at latest time %s (rule 4)" % (f, tname))
        if not (os.path.getmtime(fp) > zero_mtime):
            refuse("age guard (rule 4): %s at %s is NOT newer than the case's own 0/T" % (f, tname))
    # last time == endTime: with residualControl removed the run goes to endTime, so this
    # rule-4 limb NOW APPLIES (it did not for the residualControl-terminated VMFL054). endTime
    # is read from the level's own controlDict that ran.
    cd = os.path.join(level_dir, "system", "controlDict")
    if not os.path.isfile(cd): refuse("no system/controlDict in %s (rule 4 endTime limb)" % level_dir)
    m = re.search(r"^\s*endTime\s+([0-9.eE+\-]+)\s*;", open(cd).read(), re.M)
    if not m: refuse("endTime not found in %s" % cd)
    endt = float(m.group(1))
    if abs(float(tname) - endt) > 1e-6:
        refuse("last time %s != endTime %g (rule 4): run stopped early / did not reach endTime" % (tname, endt))
    ux = re.findall(r"Solving for Ux, Initial residual = ([0-9eE+\-.]+)", logtxt)
    pr = re.findall(r"Solving for p, Initial residual = ([0-9eE+\-.]+)", logtxt)
    er = re.findall(r"Solving for e, Initial residual = ([0-9eE+\-.]+)", logtxt)
    if not (ux and pr and er): refuse("incomplete residual history in %s" % log)
    # residuals are a DIAGNOSTIC only now (convergence is the M(0.9) plateau, §22.5), reported
    # beside the verdict; they are NOT a gate (the steady-shock limit cycle floors them ~1e-4).
    return {"time": tname, "path": tpath, "ux": float(ux[-1]), "p": float(pr[-1]), "e": float(er[-1])}

def shock_location(cl):
    xs = [x for x, _ in cl]; Ma = [m for _, m in cl]
    drops = [(Ma[i]-Ma[i+1], xs[i+1]) for i in range(len(Ma)-1)]
    return max(drops)[1]

def roache(f1, f2, f3):
    d12, d23 = (f2-f1), (f3-f2)
    if abs(d23) < 1e-30: return {"state": "EXACT", "R": 0.0, "p": None, "gci": None, "f": (f1,f2,f3)}
    R = d23/d12 if abs(d12) > 1e-30 else float("inf")
    if not (0.0 < R < 1.0):
        return {"state": "OSCILLATORY" if R < 0 else "DIVERGENT", "R": R, "p": None, "gci": None, "f": (f1,f2,f3)}
    p = math.log(abs(d12/d23))/math.log(R_REFINE)
    gci = FS*abs(d23/f3)/(R_REFINE**p - 1.0) if abs(f3) > 1e-30 else None
    return {"state": "CONVERGING", "R": R, "p": p, "gci": gci, "f": (f1,f2,f3)}

# ---- grade ------------------------------------------------------------------
def grade(run_root):
    xa, Ma, x_shock_an = analytical_profile()
    M_an_gate = interp(xa, Ma, M_GATE_X)
    levels = ("L1", "L2", "L3"); Mgate = {}; xshock = {}; plat = {}; dM = {}
    for L in levels:
        ld = os.path.join(run_root, L)
        if not os.path.isdir(ld): refuse("level dir missing: %s" % ld)
        check_completion(ld)                                   # rule 4 (rc/End/fields/age/last==endTime)
        tname, tpath = latest_time_dir(ld)
        plant_T_field(os.path.join(tpath, "T"))                # guard 1b (physical field)
        plat[L], dM[L], Mgate[L], xshock[L], samp = plateau_and_gate(ld)  # §22.5 plateau + gate reads
        plant_centreline(samp)                                 # guard 1a (gate reader)
    # CONVERGENCE (§22.5): every level's M(0.9) plateaued within DELTA_M over W_PLATEAU, else
    # NOT A RESULT and the case goes to the pre-committed LTS fallback (no loosened floor).
    for L in levels:
        if not plat[L]:
            print("VERDICT: NOT A RESULT -- %s M(0.9) plateau |dM|=%.3g over %d iters NOT < delta_M=%.3g "
                  "(§22.5); go to the pre-committed LTS fallback, no loosened floor." % (L, dM[L], W_PLATEAU, DELTA_M))
            return 0
    tri = roache(Mgate["L1"], Mgate["L2"], Mgate["L3"])
    dev = abs(Mgate["L3"] - M_an_gate)/abs(M_an_gate)
    sdev = abs(xshock["L3"] - x_shock_an)/abs(x_shock_an)
    print("M(x=%.2f): L1=%.4f L2=%.4f L3=%.4f (plateau |dM| %.2g/%.2g/%.2g < %.2g) analytical=%.4f fine-dev=%.2f%%"
          % (M_GATE_X, Mgate["L1"], Mgate["L2"], Mgate["L3"], dM["L1"], dM["L2"], dM["L3"], DELTA_M, M_an_gate, 100*dev))
    print("triple: state=%s R=%.4g p=%s GCI=%s | shock L3 x=%.3f vs analytical %.3f (%.2f%%)"
          % (tri["state"], tri["R"], ("%.3f"%tri["p"]) if tri["p"] else "n/a",
             ("%.3g%%"%(100*tri["gci"])) if tri["gci"] else "n/a", xshock["L3"], x_shock_an, 100*sdev))
    if tri["state"] != "CONVERGING":
        print("VERDICT: NOT A RESULT -- Roache triple %s (rule 5 step 2)" % tri["state"]); return 0
    # PRIMARY gate (a-priori-clean): CONVERGING triple + shock location <= 5%. PASS is AVAILABLE
    # (§12.2 re-ruled SAME, v1.18: model-form bounds 0.107%/0.18-0.63% << bands, budgeted).
    primary_ok = (sdev <= SHOCK_TOL)
    # SECONDARIES are DEMOTE-ONLY (§21.3): they can turn a PASS into GATE FAIL, never license one.
    p_ok  = (P_OBS_LO <= tri["p"] <= P_OBS_HI)
    gci_ok = (tri["gci"] is not None and tri["gci"] <= GCI_FINE_MAX)
    mdev_ok = (dev <= MACH_DEV_TOL)
    secondary_fired = not (p_ok and gci_ok and mdev_ok)
    if primary_ok and not secondary_fired:
        verdict = "PASS"
    else:
        verdict = "GATE FAIL"
    print("VERDICT: %s -- primary(shock<=%.0f%%)=%s [p in[%.1f,%.1f]=%s, GCI<=%.0f%%=%s, Mdev<=%.0f%%=%s]. "
          "Secondaries are DEMOTE-ONLY and contaminated-loose: a secondary that does NOT fire is NOT "
          "evidence of quality (§21.3). Model-form difference budgeted, §12.2 SAME (v1.18)."
          % (verdict, 100*SHOCK_TOL, primary_ok, P_OBS_LO, P_OBS_HI, p_ok,
             100*GCI_FINE_MAX, gci_ok, 100*MACH_DEV_TOL, mdev_ok))
    return 0

# ---- selftest ---------------------------------------------------------------
def selftest():
    tmp = tempfile.mkdtemp(prefix="vmfl046_selftest_"); ok = True
    try:
        # reference instrument sanity (delegates to its own richer selftest elsewhere)
        xa, Ma, xsh = analytical_profile()
        print("SELFTEST 0 analytical profile: maxM=%.3f shock_x=%.3f (built a-priori)" % (max(Ma), xsh))
        ok = ok and (2.0 < max(Ma) < 2.4) and (0.8 < xsh < 1.6)
        # 1a centreline plant
        good = os.path.join(tmp, "line_T_U.xy")
        open(good, "w").write("# x T Ux Uy Uz\n0.9\t300\t500\t0\t0\n1.0\t280\t560\t0\t0\n1.5\t400\t150\t0\t0\n"
                              + "".join("%.3f\t320\t%d\t0\t0\n" % (0.1*i, 400+i) for i in range(15)))
        r = plant_centreline(good); print("SELFTEST 1a centreline plant: PASS (%s)" % r); ok = ok and r["passed"]
        # 1b T-field plant
        tf = os.path.join(tmp, "T")
        open(tf, "w").write("internalField   nonuniform List<scalar>\n4\n(\n300\n450\n380\n500\n)\n;\n")
        r = plant_T_field(tf); print("SELFTEST 1b T-field plant: PASS (%s)" % r); ok = ok and r["passed"]
        # 2 known-bad
        bad = os.path.join(tmp, "bad.xy"); open(bad, "w").write("# x T U\n0.9 nan garbage row here now\n")
        try: read_centreline(bad); print("SELFTEST 2 known-bad: FAIL -- did not refuse"); ok = False
        except SystemExit2: print("SELFTEST 2 known-bad: PASS -- refused (exit 2)")
        # 3 Roache classifier
        tc = roache(1.80, 1.90, 1.94); print("SELFTEST 3a converging: state=%s p=%s" % (tc["state"], ("%.3f"%tc["p"]) if tc["p"] else "n/a")); ok = ok and tc["state"]=="CONVERGING"
        to = roache(1.9, 2.1, 1.95); print("SELFTEST 3b oscillatory: state=%s" % to["state"]); ok = ok and to["state"]=="OSCILLATORY"
        # 4 completion BAD arms (now incl. the last==endTime limb)
        import time as _t
        def mklevel(name, end=True, field=True, age_ok=True, rc="0", et="100"):
            ld=os.path.join(tmp,name); os.makedirs(os.path.join(ld,"0")); os.makedirs(os.path.join(ld,"system"))
            open(os.path.join(ld,"system","controlDict"),"w").write("endTime         %s;\n"%et)
            open(os.path.join(ld,"0","T"),"w").write("x"); t0=_t.time(); os.utime(os.path.join(ld,"0","T"),(t0,t0))
            td=os.path.join(ld,"100"); os.makedirs(td)   # time dir is 100
            for f in ("U","T","p"):
                if f=="p" and not field: continue
                open(os.path.join(td,f),"w").write("x")
            ft=t0+(10 if age_ok else -10)
            for f in ("U","T","p"):
                fp=os.path.join(td,f)
                if os.path.exists(fp): os.utime(fp,(ft,ft))
            lg="Solving for Ux, Initial residual = 1e-8\nSolving for p, Initial residual = 1e-9\nSolving for e, Initial residual = 1e-8\n"
            if end: lg+="End\n"
            open(os.path.join(ld,"log.rhoSimpleFoam"),"w").write(lg); open(os.path.join(ld,"RUN_RC"),"w").write(rc)
            return ld
        def expect_refuse(label,**kw):
            nonlocal ok
            try: check_completion(mklevel(label,**kw)); print("SELFTEST %s: FAIL -- did not refuse"%label); ok=False
            except SystemExit2: print("SELFTEST %s: PASS -- refused (exit 2)"%label)
        try: check_completion(mklevel("4good")); print("SELFTEST 4good: PASS -- clean level accepted")
        except SystemExit2: print("SELFTEST 4good: FAIL -- refused a clean level"); ok=False
        expect_refuse("4a-noEnd", end=False); expect_refuse("4b-missingField", field=False)
        expect_refuse("4c-ageGuard", age_ok=False); expect_refuse("4d-rc", rc="1")
        expect_refuse("4e-endTimeMismatch", et="200")   # time dir 100 != endTime 200
        # 5 PLATEAU arms (§22.5): two centreline samples W_PLATEAU apart; converged iff |dM|<DELTA_M
        def mkhist(name, dM):
            ld=os.path.join(tmp,name); base=os.path.join(ld,"postProcessing","centreline")
            for t,shift in ((500,0.0),(1000,dM)):   # M(0.9) differs by dM between the two samples
                d=os.path.join(base,str(t)); os.makedirs(d)
                rows="".join("%.3f\t300\t%.6f\t0\t0\n"%(0.002+0.005*i, (560.0+shift if abs((0.002+0.005*i)-0.9)<0.003 else 400.0)) for i in range(400))
                open(os.path.join(d,"line_T_U.xy"),"w").write("# x T Ux Uy Uz\n"+rows)
            return ld
        # a plant of 0 dM -> plateau ok; a big velocity shift -> |dM|>DELTA_M -> not converged
        pk_ok,_,_,_,_ = plateau_and_gate(mkhist("5a", 0.0))
        print("SELFTEST 5a plateau (identical samples): converged=%s (expect True)"%pk_ok); ok = ok and pk_ok
        pk_no,dmv,_,_,_ = plateau_and_gate(mkhist("5b", 50.0))
        print("SELFTEST 5b plateau (|dM|=%.3g > %.3g): converged=%s (expect False)"%(dmv,DELTA_M,pk_no)); ok = ok and (not pk_no)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SELFTEST: %s" % ("ALL PASS" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest": sys.exit(selftest())
    if len(sys.argv) != 2: sys.stderr.write("usage: grade_vmfl046.py <run_root> | --selftest\n"); sys.exit(64)
    try: sys.exit(grade(sys.argv[1]))
    except SystemExit2: sys.exit(2)
