#!/usr/bin/env python3
# =============================================================================
# VMFL054-R3 comparator -- Laminar flow in a Trapezoidal Driven Cavity (VM2026R1 p.173).
#
# DRAFT (ansys-lane-opus, running as claude-opus-4-8). NOT THE FREEZE COMMIT until the
# ansys-verification-supervisor performs the personal §3 check-4 diff re-read; this file
# is drafted for that read. Adapted from the R2 comparator grade_vmfl054_r2.py (blob
# 0e9f3fe14fb7f8713bed0a68ad34454697350a60, which was byte-identical to R1's).
#
# WHY R3 (what changes from R2, a-priori, before any field existed):
#   R2 graded u_x(centre) on the r=2 triple L1/L2/L3 = 40/80/160 and landed a monotone
#   CONVERGING triple with observed order p = 3.438 -- ABOVE the frozen ceiling 3.0 --
#   at GCI_fine 0.01067 %. Verdict GATE FAIL (order limb), PREDICTED in the freeze. A
#   3-point estimate at a small second difference (d21 = -1.499, d32 = -0.138) CANNOT
#   distinguish genuine super-2nd-order convergence from a PRE-ASYMPTOTIC artefact of
#   near-cancelling leading error terms (R2 register row #53; R1 PREREGISTRATION §10.2).
#   R3 adds a 4TH finer level L4 = 320x320 (r=2) so the order can be read on the FINEST
#   triple L2/L3/L4 -- closer to the asymptotic range -- and a 4-POINT diagnostic reports
#   whether the observed order is SETTLING toward the nominal 2 as h->0.
#
# THE GATE IS UNCHANGED FROM R2 (frozen a-priori; never set from a run):
#   observed order p in [1.0, 3.0] AND fine-grid GCI <= 5 % (Fs = 1.25), BOTH REQUIRED.
#   THE BAND IS NOT WIDENED (L-487 anti-circularity; R2 register #53). The physical
#   justification for [1.0, 3.0] is unchanged: the formal order of the bounded-linear
#   convection + linear diffusion discretisation is 2, and a driven cavity carries corner
#   singularities that can DEPRESS the observed order below 2 -- so [1.0, 3.0] brackets
#   the nominal 2 with generous margin on BOTH sides. A p above 3.0 is therefore NOT a
#   comfortable "the scheme superconverges, widen the band" reading: it is a GATE FAIL,
#   and if it PERSISTS on the finest triple L2/L3/L4 that is a genuine finding that the
#   ceiling may be mis-specified for this functional -- a question ESCALATED to the
#   supervisor, NEVER rescued here by widening (rule 2, gates closed at the freeze).
#
# THE GRADED-TRIPLE SELECTION RULE (a-priori, FIXED before any run -- anti-fitting):
#   The graded triple is GRADED_TRIPLE = (L2, L3, L4): the THREE FINEST levels, named
#   here before compute. It is NOT chosen after the run from whichever of {(L1,L2,L3),
#   (L2,L3,L4)} happens to converge -- selecting the triple after seeing the answer would
#   be gate-fitting (rule 2). If the fixed finest triple is not CONVERGING (rule 5), the
#   verdict is NOT A RESULT; there is NO fallback to a coarser triple to rescue a value.
#   (L1,L2,L3) is retained ONLY as the 4-point diagnostic's coarse leg.
#
# THIS COMPARATOR NEVER EMITS `PASS` (unchanged from R1/R2). The external Darr & Vanka
#   (1991) validation limb is DEFERRED -- the manual states the reference only as plotted
#   curves (Figures .38.2/.38.3; the .txt sidecar strips figures), and the BC-direction
#   modelling choice is capped at GATE REACHED by the standing R1 Ruling 1. So the most
#   this grid-convergence gate can reach is `GATE REACHED`, else `GATE FAIL`, else
#   `NOT A RESULT` (rule 5). Whether R3 should be allowed to promote GATE REACHED -> PASS
#   is a supervisor question flagged in the pre-registration, NOT decided in these bytes.
#
# FOUR guards, each REFUSING with exit 2, each of which has bitten this lab:
#   (1) PLANTED-ZERO (rule 3), on BOTH readers the gate depends on -- the probe-file
#       gate reader AND the U-field reader. A known delta is planted into a COPY, read
#       back, and the control REFUSES if the reader cannot see it. The gate reduction is a
#       DIRECT read of one scalar (u_x at one point, cellPoint-interpolated) and of a full
#       per-element field list -- neither is a sum/mean/ptp/max over a set, so neither
#       cancels nor absorbs a plant (L-487): the plant is the value itself, read back by
#       identity, and the U-field arm checks EVERY element moved (worst-element identity).
#   (2) STRICT COMPLETION (rule 4): solver rc (persisted as RUN_RC), an End line AND
#       absence of FOAM FATAL, latest-time fields present, the age guard (fields NEWER
#       than the case's own 0/), and iterative convergence. Any failed limb REFUSES.
#       `last time == endTime` and the `ExecutionTime` count are DELIBERATELY INAPPLICABLE
#       to a residualControl-terminated steady solve (it stops when residuals fall, BEFORE
#       endTime) and are NOT checked -- same basis as R1/R2, VMFL038/VMFL063.
#   (3) KNOWN-BAD INPUT: a corrupted probe row is fed to the reader, which MUST refuse.
#   (4) GATE-BLIND PHYSICAL RANGE (new in R3): u_x at the centre of a cavity driven at
#       |U_wall| = 400 m/s must be physically bounded and non-collapsed. A value outside
#       [PHYS_UX_MIN_ABS, PHYS_UX_MAX] REFUSES -- this catches a nonphysical/garbage read
#       (a NaN-parsed-as-0, a units error, a divergent blow-up) BEFORE it can masquerade
#       as a grid-convergence datum. It is GATE-BLIND: it references neither the order band
#       nor the GCI, only physical plausibility, so it cannot fit the gate.
#
# Run `grade_vmfl054_r3.py --selftest` to exercise every guard and the 4-point diagnostic
# on synthetic data; `grade_vmfl054_r3.py <run_root>` to grade a real run.
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
LEVELS          = ("L1", "L2", "L3", "L4")   # R3: four r=2 levels 40/80/160/320
GRADED_TRIPLE   = ("L2", "L3", "L4")         # FIXED a-priori: the three FINEST levels
DIAG_TRIPLE     = ("L1", "L2", "L3")         # 4-point diagnostic coarse leg (NOT graded)
# gate-blind physical-range guard: |U_wall| = 400 m/s; centre u_x must be bounded/non-zero
PHYS_UX_MAX     = 800.0           # 2 x lid speed -- a physically generous ceiling
PHYS_UX_MIN_ABS = 1.0            # a collapsed/near-zero centre velocity is nonphysical here

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
    -- a reader that guesses can misread."""
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
    back; refuse if the reader does not see it. The gate reduction is a DIRECT read of
    one scalar, so the plant is the value itself, seen by identity (L-487: no set-wide
    sum/ptp/max to cancel or absorb it)."""
    base = read_probe_ux(path)
    plant = K_PLANT * abs(base)
    if plant < PLANT_MIN_ABS:
        refuse("planted-zero: |gate value| %.3g too small to size a plant against" % base)
    tmp = tempfile.mkdtemp(prefix="vmfl054r3_plant_probe_")
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
    read it back; refuse if unseen. The field reader returns a per-cell list, so the arm
    checks EVERY element moved by exactly plant (worst-element identity; no reduction that
    could cancel/absorb -- L-487)."""
    xs, _ = read_U_internal_x(path)
    scale = max(abs(v) for v in xs)
    plant = K_PLANT * scale
    if plant < PLANT_MIN_ABS:
        refuse("planted-zero: U field max|u_x| %.3g too small to size a plant" % scale)
    tmp = tempfile.mkdtemp(prefix="vmfl054r3_plant_U_")
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

# ---- gate-blind physical-range guard (rule: refuse garbage before grading it) -----
def check_physical_range(ux, level):
    """GATE-BLIND: refuse a centre u_x that is nonphysical for a cavity driven at 400 m/s
    -- collapsed to ~0, or blown up past 2x the lid speed. References NEITHER the order
    band NOR the GCI, so it cannot fit the gate; it only rejects a garbage read."""
    if not math.isfinite(ux):
        refuse("physical-range (gate-blind): %s u_x is not finite (%r)" % (level, ux))
    if abs(ux) < PHYS_UX_MIN_ABS:
        refuse("physical-range (gate-blind): %s u_x=%.6g collapsed below |%.3g| -- "
               "a centre velocity this small is nonphysical for a 400 m/s lid" % (level, ux, PHYS_UX_MIN_ABS))
    if abs(ux) > PHYS_UX_MAX:
        refuse("physical-range (gate-blind): %s u_x=%.6g exceeds %.3g (2x lid speed) -- "
               "a blow-up, not a grid-convergence datum" % (level, ux, PHYS_UX_MAX))
    return True

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
    """f1 coarse, f2 med, f3 fine; r=2. Returns state + p + GCI. (Used on the graded
    finest triple L2/L3/L4 AND on the diagnostic coarse triple L1/L2/L3.)"""
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

def four_point_diagnostic(f1, f2, f3, f4):
    """DIAGNOSTIC ONLY -- moves NO gate quantity. With 4 monotone r=2 levels, report the
    coarse-triple order p123 = p(L1,L2,L3) and the fine-triple order p234 = p(L2,L3,L4),
    and whether the observed order is SETTLING toward the nominal 2 as h->0 (i.e. the fine
    triple's order is nearer 2 than the coarse triple's). This is what disambiguates a
    genuine >2 order from a pre-asymptotic artefact -- but the VERDICT rests on the graded
    finest triple alone."""
    lo = roache(f1, f2, f3)
    hi = roache(f2, f3, f4)
    p123 = lo["p"]; p234 = hi["p"]
    settling = None
    if p123 is not None and p234 is not None:
        settling = abs(p234 - 2.0) < abs(p123 - 2.0)   # fine triple closer to nominal 2?
    return {"p123": p123, "p234": p234, "lo_state": lo["state"], "hi_state": hi["state"],
            "settling_toward_2": settling}

# ---- grade a real run -------------------------------------------------------
def grade(run_root):
    vals, comp = {}, {}
    for L in LEVELS:
        ld = os.path.join(run_root, L)
        if not os.path.isdir(ld):
            refuse("level dir missing: %s" % ld)
        comp[L] = check_completion(ld)                     # guard 2 (rule 4)
        tname, tpath = latest_time_dir(ld)
        plant_U_field(os.path.join(tpath, "U"))            # guard 1b (rule 3, physical field)
        probe = current_probe_file(ld)                     # enumerate, refuse on restart ambiguity
        plant_probe(probe)                                 # guard 1a (rule 3, gate reader)
        vals[L] = read_probe_ux(probe)
        check_physical_range(vals[L], L)                   # guard 4 (gate-blind physical range)
    # rule 5 step 1: every level iteratively converged, else NOT A RESULT
    for L in LEVELS:
        if not comp[L]["converged"]:
            print("VERDICT: NOT A RESULT -- %s not iteratively converged "
                  "(Ux resid %.3g, p resid %.3g vs floor %.3g)"
                  % (L, comp[L]["ux_resid"], comp[L]["p_resid"], RESID_FLOOR))
            return 0

    # 4-point DIAGNOSTIC (moves no gate): is the observed order settling toward 2?
    diag = four_point_diagnostic(vals["L1"], vals["L2"], vals["L3"], vals["L4"])
    print("u_x(centre) levels: L1=%.9g L2=%.9g L3=%.9g L4=%.9g"
          % (vals["L1"], vals["L2"], vals["L3"], vals["L4"]))
    print("4-POINT DIAGNOSTIC (not a gate): p(L1,L2,L3)=%s [%s]  p(L2,L3,L4)=%s [%s]  settling_toward_2=%s"
          % (("%.4g" % diag["p123"]) if diag["p123"] is not None else "n/a", diag["lo_state"],
             ("%.4g" % diag["p234"]) if diag["p234"] is not None else "n/a", diag["hi_state"],
             diag["settling_toward_2"]))

    # GRADED triple = the three FINEST levels, FIXED a-priori (no fallback search).
    gf = tuple(vals[L] for L in GRADED_TRIPLE)
    tri = roache(*gf)
    print("GRADED triple (%s) u_x(centre): %s state=%s R=%.4g p=%s GCI_fine=%s"
          % ("/".join(GRADED_TRIPLE),
             " ".join("%.9g" % v for v in gf), tri["state"], tri["R"],
             ("%.4g" % tri["p"]) if tri["p"] is not None else "n/a",
             ("%.4g%%" % (100*tri["gci_fine"])) if tri["gci_fine"] is not None else "n/a"))
    if tri["state"] != "CONVERGING":
        print("VERDICT: NOT A RESULT -- graded (finest) Roache triple %s (rule 5 step 2). "
              "NO fallback to a coarser triple (anti-fitting, rule 2)." % tri["state"])
        return 0
    p_ok   = (P_OBS_LO <= tri["p"] <= P_OBS_HI)
    gci_ok = (tri["gci_fine"] <= GCI_FINE_MAX)
    ok = p_ok and gci_ok
    # NEVER PASS: external Darr & Vanka validation deferred (figure-pending) + BC-direction cap.
    print("VERDICT: %s -- grid-convergence gate %s (p in [%.1f,%.1f]? %s; GCI_fine<=%.1f%%? %s). "
          "PASS withheld: external Darr&Vanka validation deferred (figure digitization) and "
          "the BC-direction cap stands (R1 Ruling 1)."
          % ("GATE REACHED" if ok else "GATE FAIL",
             "MET" if ok else "NOT MET", P_OBS_LO, P_OBS_HI, p_ok, 100*GCI_FINE_MAX, gci_ok))
    if not p_ok and gci_ok and tri["p"] > P_OBS_HI:
        print("NOTE: order limb FAILS ABOVE the ceiling on the FINEST triple. This is NOT a "
              "band-widening trigger (rule 2). It is a finding that the observed order genuinely "
              "exceeds %.1f as h->0; the 'is the ceiling right?' question is for the supervisor, "
              "not this comparator." % P_OBS_HI)
    return 0

# ---- selftest: exercise every guard + the 4-point diagnostic on synthetic data ----
def selftest():
    tmp = tempfile.mkdtemp(prefix="vmfl054r3_selftest_")
    ok = True
    n = 0
    try:
        # (1a) probe plant fires on a live reader
        good = os.path.join(tmp, "probe_U")
        open(good, "w").write("# Probe 0 (1 0.5 0)\n# Time\n300 (-168.65 22.6 4.5e-17)\n")
        r = plant_probe(good); n += 1; print("SELFTEST 1a probe planted-zero: PASS (%s)" % r)
        # (1b) U-field plant fires
        uf = os.path.join(tmp, "U")
        open(uf, "w").write("internalField   nonuniform List<vector>\n3\n(\n(-168.6 1 0)\n(50 2 0)\n(10 -3 0)\n)\n;\n")
        r = plant_U_field(uf); n += 1; print("SELFTEST 1b U-field planted-zero: PASS (%s)" % r)
        # (2) known-bad input MUST refuse
        bad = os.path.join(tmp, "probe_bad")
        open(bad, "w").write("# Probe 0\n# Time\n300 (nan garbage here\n")
        try:
            read_probe_ux(bad); print("SELFTEST 2 known-bad guard: FAIL -- reader did NOT refuse"); ok = False
        except SystemExit2:
            n += 1; print("SELFTEST 2 known-bad guard: PASS -- reader refused (exit 2) on a corrupt row")
        # (3a/3b) gate-blind physical-range guard: good value accepted, garbage refused
        try:
            check_physical_range(-164.75, "L4"); n += 1
            print("SELFTEST 3a physical-range good value: PASS -- accepted -164.75")
        except SystemExit2:
            print("SELFTEST 3a physical-range good value: FAIL -- refused a physical value"); ok = False
        for lbl, v in (("3b-collapsed", 0.0), ("3c-blowup", 5.0e3), ("3d-naninf", float("nan"))):
            try:
                check_physical_range(v, lbl)
                print("SELFTEST %s physical-range garbage: FAIL -- did NOT refuse %r" % (lbl, v)); ok = False
            except SystemExit2:
                n += 1; print("SELFTEST %s physical-range garbage: PASS -- refused (exit 2) %r" % (lbl, v))
        # (4a) Roache classifier: converging + oscillatory
        tc = roache(10.0, 10.24, 10.29)
        n += 1; print("SELFTEST 4a converging triple: state=%s p=%.4g GCI=%.4g%%"
                      % (tc["state"], tc["p"], 100*tc["gci_fine"]))
        if tc["state"] != "CONVERGING": ok = False
        to = roache(10.0, 10.5, 10.1)
        n += 1; print("SELFTEST 4b oscillatory triple: state=%s (expect OSCILLATORY)" % to["state"])
        if to["state"] != "OSCILLATORY": ok = False
        # (5a) 4-point diagnostic: order settling toward 2 (fine triple nearer nominal)
        #   coarse triple superconvergent-looking (p123~3.4), fine triple relaxes toward 2.
        d = four_point_diagnostic(-163.116, -164.615, -164.753, -164.788)
        n += 1
        print("SELFTEST 5a 4-point diagnostic (settling): p123=%.4g p234=%.4g settling=%s"
              % (d["p123"], d["p234"], d["settling_toward_2"]))
        if d["p123"] is None or d["p234"] is None: ok = False
        # (5b) 4-point diagnostic: order NOT settling -- p234 moves AWAY from 2 (persistence /
        #   worsening superconvergence on the finer triple; the honest label is settling=False).
        d2 = four_point_diagnostic(-160.0, -164.0, -164.7, -164.75)
        n += 1
        print("SELFTEST 5b 4-point diagnostic (persistence): p123=%.4g p234=%.4g settling=%s (expect False)"
              % (d2["p123"], d2["p234"], d2["settling_toward_2"]))
        if d2["settling_toward_2"] is not False: ok = False
        # ---- guard 2: STRICT COMPLETION arms ----
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
            nonlocal ok, n
            try:
                check_completion(mklevel(tmp, label, **kw))
                print("SELFTEST %s: FAIL -- check_completion did NOT refuse" % label); ok = False
            except SystemExit2:
                n += 1; print("SELFTEST %s: PASS -- check_completion refused (exit 2)" % label)
        try:
            check_completion(mklevel(tmp, "6good"))
            n += 1; print("SELFTEST 6good completion: PASS -- clean level accepted")
        except SystemExit2:
            print("SELFTEST 6good completion: FAIL -- refused a clean level"); ok = False
        expect_refuse("6a-noEnd", end=False)
        expect_refuse("6b-missingField", field_p=False)
        expect_refuse("6c-ageGuard", age_ok=False)
        expect_refuse("6d-rc", rc="1")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SELFTEST: %s  (%d/%d arms passed)" % ("ALL PASS" if ok else "FAILURES ABOVE", n, n))
    return 0 if ok else 1

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    if len(sys.argv) != 2:
        sys.stderr.write("usage: grade_vmfl054_r3.py <run_root> | --selftest\n"); sys.exit(64)
    try:
        sys.exit(grade(sys.argv[1]))
    except SystemExit2 as e:
        sys.exit(2)
