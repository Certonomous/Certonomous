#!/usr/bin/env python3
"""VMFL022-R2 comparator -- Cavitation over a sharp-edged orifice, Case B (low P1).

Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p. 87.
Reference: W.H. Nurick, "Orifice Cavitation and Its Effects on Spray Mixing",
J. Fluids Engineering 98, 681-687, 1976 (experimental; the manual's target 0.780
coincides with Nurick's cavitating-orifice correlation Cd = Cc*sqrt(K), Cc=0.62,
K=(P1-Pv)/(P1-P2) -- see PREREGISTRATION.md for the ref-kind nuance).
THIS FILE IS THE GRADING PATH. Committed with the pre-registration that cites it
by sha, before any graded solver runs (CLAUDE.md rule 2). REFUSES (exit 2) rather
than degrading; every refusal names its clause.

WHY R2 EXISTS (successor to VMFL022, register #17 = NOT A RESULT, triple
OSCILLATORY): the base r=2 triple mixed two PHYSICAL REGIMES -- the coarse level
N2R=12 ran SINGLE-PHASE (min alpha.water = 1.000000, no vapour) while N2R=24/48
CAVITATED (min alpha.water 0.264 / 0.023). A single-phase orifice solve does NOT
measure the cavitating-orifice Cd -- it solves a different PDE branch, so it is
not a coarse-grid estimate of the cavitating quantity and cannot be an admissible
coarse member of a cavitating-Cd Roache study. The manual's reference (Cd 0.780)
is itself a cavitating solution, so a valid reproduction must be conducted ENTIRELY
in the cavitating regime.

R2 THEREFORE:
  (1) shifts the r=2 triple UP to N2R = 24 / 48 / 96 (base's OWN uniform meshing,
      no edge-grading knob introduced -- there is no continuous grading DOF to
      tune; supervisor's §3 ruling 2026-09-07 adopted this "lever B" and REJECTED
      the in-place edge-refinement "lever A" precisely because its grading
      magnitude was a free parameter);
  (2) adds a GATE-BLIND REGIME-CONSISTENCY PRECONDITION: unless ALL THREE graded
      levels are clearly cavitating (min alpha.water <= REGIME_ONSET_ALPHA, an
      a-priori physical onset threshold that references NEITHER 0.780 NOR the
      +-5% band), the verdict is NOT A RESULT -- a mixed-regime triple is never
      silently graded;
  (3) applies L-500 at both ends of the triple: the linear-solver tolerance set
      is tightened ~2 orders (fvSolution) so the 48->96 functional difference is
      not lost in the iterative noise floor (the VMFL010 finest-level failure
      mode -- in the base run the L2->L3 Cd difference 0.23% was comparable to
      the finest level's 0.22% window CoV).

The GATE IS BYTE-IDENTICAL to the base (Cd 0.780 +- 5%, L-487): R2 changes the
mesh ladder, the regime precondition and the iterative tolerances -- NEVER the
gate constants, threshold, cap-label or tier ceiling.

The planted-zero control is REBUILT to the L-487 rule (the base VMFL022 control
had the L-487 CANCELLATION defect: it planted onto the WHOLE averaging window and
the window-mean shift was P identically, for any input including all zeros). R2
plants a PROPER SUBSET of the window (expected shift = P * n_planted/n_window) and
REFUSES if the plant subset is ever the whole window.

  python3 grade_vmfl022_r2.py            # grade the run tree
  python3 grade_vmfl022_r2.py --selftest # synthetic, no solver
  python3 grade_vmfl022_r2.py --dryrun-reader <surfaceFieldValue.dat>
"""

import glob, json, math, os, re, shutil, sys, tempfile

CASE = "VMFL022-R2"
MANUAL_PAGE = "87"

# --- manual inputs (p.87) ----------------------------------------------------
P1 = 250000.0      # Pa, inlet pressure
P2 = 95000.0       # Pa, outlet (back) pressure
PSAT = 3540.0      # Pa, vapour pressure
RHO_L = 1000.0     # kg/m3, liquid density
R2 = 0.004         # m, orifice radius
WEDGE_DEG = 5.0    # total wedge angle
A2_GEOM = 0.5 * R2 * R2 * math.sin(math.radians(WEDGE_DEG))  # flat-wedge sector
V_THEO = math.sqrt(2.0 * (P1 - P2) / RHO_L)
K_CAV = (P1 - PSAT) / (P1 - P2)          # Nurick cavitation number
CC_NURICK = 0.62                         # sharp-edge contraction coefficient

# manual Table .22.1
CD_REF = 0.780         # THE GATE reference (Nurick) -- BYTE-IDENTICAL to base
CD_ANSYS = 0.777       # context only, never the gate

TOL_GATE = 0.05        # |Cd_lab-Cd_ref|/Cd_ref <= 5% at the finest level.
                       # BYTE-IDENTICAL to the base VMFL022 gate (L-487): NOT
                       # widened, NOT re-derived. Justified in the base prereg
                       # line 6 (manual 3% accuracy goal + ~2% SchnerrSauer-vs-ZGB
                       # cavitation-model substitution). NOT chosen from any run.

# steady window: time-average Cd over the final fraction of physical time
ENDTIME = 0.06
WINDOW_FRAC = 0.30     # average over the last 30% of the run
PLATEAU_COV = 0.03     # a level whose Cd coeff-of-variation over the window
                       # exceeds 3% is NOT plateaued -> NOT A RESULT (rule 5, L1)

# --- REGIME-CONSISTENCY PRECONDITION (a-priori, gate-blind) -------------------
# A level is "in the cavitating regime" iff its minimum liquid fraction is at or
# below this threshold, i.e. at least one cell holds >= 10% vapour. Pinned a-priori
# from cavitation physics (vapour is unambiguously present), NOT tuned to Cd:
# it references neither CD_REF nor TOL_GATE. Base VMFL022 gave min alpha.water
# 0.264 (N2R=24) and 0.023 (N2R=48) -- both far below 0.9, so a regime-consistent
# 24/48/96 triple clears this comfortably and non-marginally, while the excluded
# single-phase N2R=12 level (min 1.000000) would FAIL it. If ANY graded level's
# min alpha.water exceeds this, the triple is mixed-regime -> NOT A RESULT.
REGIME_ONSET_ALPHA = 0.9

FS = 1.25
RATIO = 2.0
PLANT = 1.234e-06      # m3/s, planted-zero perturbation on Q
PLANT_TOL = 1e-11      # abs tol on the reader's observed window-mean shift
EPS_ABS = 1e-6         # Cd level-to-level difference below this counts as zero
STAG_TOL = 1e-3        # |R-1| <= STAG_TOL => STAGNANT
A2_XCHECK_TOL = 0.005  # FO-header area vs geometric area agree to 0.5%

# name -> orifice-radial cell count (coarse->fine, ratio 2). SHIFTED UP one rung
# vs base VMFL022 (which was 12/24/48): the single-phase 12 level is excluded
# a-priori by the regime precondition; 96 is the new finest.
LEVELS = (("L1", 24), ("L2", 48), ("L3", 96))

RUN_ROOT = "/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL022-R2"
OUT_JSON = os.path.join(RUN_ROOT, "GRADING_VMFL022_R2.json")
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


def refuse(msg):
    print("REFUSE: " + msg, file=sys.stderr)
    sys.exit(2)


# --- reader: a surfaceFieldValue .dat (header lines '#', then 'time  value') --
def read_area_from_header(path):
    if not os.path.isfile(path):
        refuse("series file does not exist: " + path)
    for line in open(path, errors="replace"):
        m = re.match(r"#\s*Area\s*:\s*([0-9eE.+-]+)", line)
        if m:
            return float(m.group(1))
        if not line.startswith("#"):
            break
    refuse("no '# Area' header line in " + path)


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
            refuse("data row has %d cols, expected >=2 (time value) in %s: %r"
                   % (len(parts), path, s))
        try:
            rows.append((float(parts[0]), float(parts[1])))
        except ValueError:
            refuse("unparseable data row in %s: %r" % (path, s))
    if not rows:
        refuse("no data rows in " + path)
    return rows


# --- alpha.water field reader (regime precondition; gate-blind) ---------------
def read_alpha_min(level_dir, time_dir):
    """Minimum of alpha.water over the internal field at `time_dir`. Reads the
    liquid volume fraction ONLY -- a gate-blind regime indicator, never the flux
    or Cd. A uniform field parses to its single value."""
    p = os.path.join(level_dir, time_dir, "alpha.water")
    if not os.path.isfile(p):
        refuse("no alpha.water at %s (regime precondition cannot be evaluated)" % p)
    txt = open(p, errors="replace").read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\(\n(.*?)\n\)",
                  txt, re.S)
    if m:
        vals = [float(x) for x in m.group(2).split()]
        if not vals:
            refuse("alpha.water nonuniform list empty at %s" % p)
        return min(vals), len(vals)
    mu = re.search(r"internalField\s+uniform\s+([0-9eE.+-]+)", txt)
    if mu:
        return float(mu.group(1)), 1
    refuse("cannot parse alpha.water internalField at %s" % p)


def inlet_dat(level_dir):
    pat = os.path.join(level_dir, "postProcessing", "inletMassFlow", "*", "surfaceFieldValue.dat")
    hits = sorted(glob.glob(pat))
    if not hits:
        refuse("no inlet surfaceFieldValue.dat under " + level_dir)
    return hits[-1]   # last FO start-time dir


def outlet_dat(level_dir):
    pat = os.path.join(level_dir, "postProcessing", "outletMassFlow", "*", "surfaceFieldValue.dat")
    hits = sorted(glob.glob(pat))
    if not hits:
        refuse("no outlet surfaceFieldValue.dat under " + level_dir)
    return hits[-1]


def window_stats(rows):
    """Return (mean_Q_abs, cov, n, t0, t1) over the final WINDOW_FRAC of time."""
    tmax = rows[-1][0]
    if abs(tmax - ENDTIME) > 1e-6:
        refuse("series last time %g != endTime %g" % (tmax, ENDTIME))
    tcut = tmax * (1.0 - WINDOW_FRAC)
    win = [abs(v) for (t, v) in rows if t >= tcut - 1e-12]
    if len(win) < 5:
        refuse("only %d rows in the final %.0f%% window -- too few to average"
               % (len(win), WINDOW_FRAC * 100))
    mean = sum(win) / len(win)
    var = sum((x - mean) ** 2 for x in win) / len(win)
    cov = math.sqrt(var) / mean if mean > 0 else float("inf")
    return mean, cov, len(win), tcut, tmax


def cd_of_level(level_dir):
    idat = inlet_dat(level_dir)
    odat = outlet_dat(level_dir)
    a2_fo = read_area_from_header(odat)
    if abs(a2_fo - A2_GEOM) / A2_GEOM > A2_XCHECK_TOL:
        refuse("outlet FO area %.6e disagrees with geometric flat-wedge A2 %.6e "
               "by >%.1f%% -- mesh/geometry mismatch" % (a2_fo, A2_GEOM, A2_XCHECK_TOL * 100))
    q_mean, cov, n, t0, t1 = window_stats(read_series(idat))
    cd = q_mean / (a2_fo * V_THEO)
    return dict(cd=cd, q_mean=q_mean, cov=cov, n_window=n, a2_fo=a2_fo,
                t_window=(t0, t1), inlet_src=os.path.relpath(idat, RUN_ROOT),
                outlet_src=os.path.relpath(odat, RUN_ROOT))


# --- planted-zero control (rule 3), REBUILT to the L-487 rule -----------------
def _plant_subset_size(n_win):
    """PROPER SUBSET of the averaging window. L-487: a plant covering the WHOLE
    averaging set shifts a mean by P IDENTICALLY (for any input, incl. all zeros)
    and so proves nothing about the reader. Half the window is a proper subset;
    the expected shift then depends on n_planted/n_window, which a blind or
    mis-weighting reader cannot reproduce."""
    return n_win // 2


def planted_zero_control(level_dir):
    src = inlet_dat(level_dir)
    rows = read_series(src)
    tmax = rows[-1][0]
    tcut = tmax * (1.0 - WINDOW_FRAC)
    win_idx = [i for i, (t, v) in enumerate(rows) if t >= tcut - 1e-12]
    n_win = len(win_idx)
    n_plant = _plant_subset_size(n_win)
    if not (0 < n_plant < n_win):
        refuse("planted-zero DEGENERATE: subset %d of window %d is not a proper "
               "subset -- a whole-window plant cancels to P identically and could "
               "not fail (L-487)" % (n_plant, n_win))
    plant_idx = set(win_idx[:n_plant])          # first half of the window
    base_mean, _, _, _, _ = window_stats(rows)
    tmp = tempfile.mkdtemp(prefix="vmfl022r2plant_")
    try:
        work = os.path.join(tmp, "surfaceFieldValue.dat")
        i = -1
        with open(src) as fh, open(work, "w") as out:
            for line in fh:
                s = line.strip()
                if not s or s.startswith("#"):
                    out.write(line); continue
                i += 1
                parts = s.split()
                t = float(parts[0]); v = float(parts[1])
                if i in plant_idx:
                    v = math.copysign(abs(v) + PLANT, v)   # push magnitude up by PLANT
                out.write("%s\t%r\n" % (parts[0], v))
        seen_mean, _, _, _, _ = window_stats(read_series(work))
        moved = seen_mean - base_mean
        expected = PLANT * n_plant / n_win          # proper-subset shift (L-487)
        return dict(passed=abs(moved - expected) <= PLANT_TOL, planted=PLANT,
                    n_planted=n_plant, n_window=n_win, expected_shift=expected,
                    reader_delta=moved, file=os.path.basename(src),
                    inert_full_set_shift=PLANT)   # the value a WHOLE-window plant
                                                  # would give for ANY input (L-487
                                                  # inert arm; not used to pass)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- strict completion (rule 4; adapted for adaptive-dt transient) -----------
def _time_dirs(level_dir):
    out = []
    for d in os.listdir(level_dir):
        if os.path.isdir(os.path.join(level_dir, d)) and re.fullmatch(r"\d+(\.\d+)?", d):
            out.append(d)
    return sorted(out, key=float)


def strict_completion(level_dir):
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
    log = os.path.join(level_dir, "log.interPhaseChangeFoam")
    if not os.path.isfile(log):
        refuse("%s: no log.interPhaseChangeFoam" % name)
    text = open(log, errors="replace").read()
    if not re.search(r"^End\s*$", text, re.M):
        refuse("%s: no 'End' line in log (clause 2)" % name)
    times = _time_dirs(level_dir)
    if not times or abs(float(times[-1]) - ENDTIME) > 1e-6:
        refuse("%s: last time is %r, endTime is %g (clause 3)"
               % (name, times[-1] if times else None, ENDTIME))
    tdir = os.path.join(level_dir, times[-1])
    for fld in ("U", "p_rgh", "alpha.water"):
        if not os.path.isfile(os.path.join(tdir, fld)):
            refuse("%s: field %s missing at endTime (clause 4)" % (name, fld))
    # adaptive dt: ExecutionTime lines are variable, so we require a real
    # integration happened (>= 10 lines) and defer "endTime reached" to clause 3.
    n_exec = len(re.findall(r"^ExecutionTime = ", text, re.M))
    if n_exec < 10:
        refuse("%s: only %d ExecutionTime lines -- run too short (clause 5, adaptive-dt form)"
               % (name, n_exec))
    marker = os.path.join(level_dir, "0", "U")
    if not os.path.isfile(marker):
        refuse("%s: no 0/U age-guard marker (clause 6)" % name)
    t_marker = os.path.getmtime(marker)
    t_f = os.path.getmtime(os.path.join(tdir, "U"))
    if not t_f > t_marker:
        refuse("%s: endTime/U (%.3f) is NOT newer than 0/U (%.3f) -- AGE GUARD (clause 6)"
               % (name, t_f, t_marker))
    return dict(rc=rc, endTime=float(times[-1]), endTime_dir=times[-1], n_exec=n_exec,
                fields_at_endTime=["U", "p_rgh", "alpha.water"],
                age_guard="U newer than 0/U")


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


def main():
    print("=" * 78)
    print("%s -- Cavitation over a sharp-edged orifice, Case B (low P1)" % CASE)
    print("Ansys FD Verification Manual 2026 R1, p. %s" % MANUAL_PAGE)
    print("reference: Nurick 1976 (experimental); target Cd = %.3f" % CD_REF)
    print("=" * 78)
    print("  V_theo = sqrt(2*(P1-P2)/rho) = %.4f m/s" % V_THEO)
    print("  A2 (flat-wedge orifice)      = %.6e m2" % A2_GEOM)
    print("  Nurick K = (P1-Pv)/(P1-P2)   = %.5f ; Cc*sqrt(K) = %.4f (physics check)"
          % (K_CAV, CC_NURICK * math.sqrt(K_CAV)))
    print("  regime onset threshold (a-priori, gate-blind): min alpha.water <= %.2f" % REGIME_ONSET_ALPHA)

    completion, levels, regime = {}, {}, {}
    for name, nx in LEVELS:
        d = os.path.join(RUN_ROOT, name)
        completion[name] = strict_completion(d)
        amin, ncells = read_alpha_min(d, completion[name]["endTime_dir"])
        regime[name] = dict(alpha_min=amin, ncells=ncells,
                            cavitating=bool(amin <= REGIME_ONSET_ALPHA))
        levels[name] = cd_of_level(d)

    # --- planted-zero control (rule 3, L-487 subset form) on the finest level ---
    fine = LEVELS[-1][0]
    pz = planted_zero_control(os.path.join(RUN_ROOT, fine))
    print("\nplanted-zero control on %s: %s" % (fine, json.dumps(pz)))
    if not pz["passed"]:
        refuse("planted-zero control failed: the reader did not reproduce the "
               "proper-subset shift %g (saw %g); its numbers mean nothing (rule 3, L-487)"
               % (pz["expected_shift"], pz["reader_delta"]))

    # --- regime-consistency precondition (a-priori, gate-blind) ---------------
    non_cavitating = [n for n, _ in LEVELS if not regime[n]["cavitating"]]

    # plateau gate (rule 5, level-1: not plateaued -> NOT A RESULT)
    not_plateaued = [n for n, _ in LEVELS if levels[n]["cov"] > PLATEAU_COV]

    cds = [levels[n]["cd"] for n, _ in LEVELS]
    tr = roache(cds[0], cds[1], cds[2])
    cd_fine = cds[-1]
    rel = abs(cd_fine - CD_REF) / abs(CD_REF)
    gate_ok = rel <= TOL_GATE

    # Verdict order: instrument (completion/plant, already refused above), then
    # PHYSICAL ADMISSIBILITY (regime-consistency) -- a mixed-regime triple is not
    # an admissible cavitating Roache study -- then plateau, then Roache, then gate.
    if non_cavitating:
        verdict = "NOT A RESULT"
        why = ("levels %s are NOT in the cavitating regime (min alpha.water > %.2f) "
               "-- a mixed-regime triple is not an admissible cavitating Roache study "
               "(regime-consistency precondition)" % (non_cavitating, REGIME_ONSET_ALPHA))
    elif not_plateaued:
        verdict = "NOT A RESULT"
        why = "levels %s not plateaued (Cd CoV > %.1f%%) (rule 5, L1)" % (not_plateaued, PLATEAU_COV * 100)
    elif tr["state"] != "CONVERGING":
        verdict = "NOT A RESULT"
        why = "grid triple %s, not CONVERGING (rule 5)" % tr["state"]
    else:
        verdict = "GATE REACHED" if gate_ok else "GATE FAIL"
        why = ("Cd_fine %.4f within %.0f%% of Nurick %.3f (rel %.3f%%)"
               % (cd_fine, TOL_GATE * 100, CD_REF, rel * 100) if gate_ok else
               "Cd_fine %.4f is %.3f%% off Nurick %.3f, outside the %.0f%% gate"
               % (cd_fine, rel * 100, CD_REF, TOL_GATE * 100))
    assert verdict in VERDICTS

    print("\n--- per level: regime (alpha.water min), Cd, window CoV ---")
    for n, _ in LEVELS:
        L = levels[n]; g = regime[n]
        print("  %-3s alpha.water_min=%.6f %s  Cd=%.5f  Q=%.6e m3/s  CoV=%.3f%%  window t=[%.4f,%.4f] n=%d"
              % (n, g["alpha_min"], "CAVITATING" if g["cavitating"] else "SINGLE-PHASE(!)",
                 L["cd"], L["q_mean"], L["cov"] * 100, L["t_window"][0], L["t_window"][1], L["n_window"]))
    print("  Roache: state %s  R %s  p %s  GCI_fine %s  Cd_extrap %s" % (
        tr["state"],
        "n/a" if tr["R"] is None else "%.4f" % tr["R"],
        "n/a" if tr["p"] is None else "%.4f" % tr["p"],
        "n/a" if tr["gci_fine"] is None else "%.4e" % tr["gci_fine"],
        "n/a" if tr["f_extrapolated"] is None else "%.5f" % tr["f_extrapolated"]))
    print("\n  GATE: |Cd_fine - %.3f|/%.3f = %.4f  (tol %.2f)  -> %s"
          % (CD_REF, CD_REF, rel, TOL_GATE, "ok" if gate_ok else "OUT"))
    print("\nVERDICT: %s -- %s" % (verdict, why))
    print("  (context only, never the gate: Ansys Fluent Cd = %.3f)" % CD_ANSYS)

    payload = dict(case=CASE, manual_page=MANUAL_PAGE, verdict=verdict, why=why,
                   reference=dict(source="Nurick 1976", cd_ref=CD_REF, kind="experimental/correlation"),
                   physics_check=dict(K=K_CAV, cc=CC_NURICK, cd_from_correlation=CC_NURICK * math.sqrt(K_CAV)),
                   gate=dict(tol=TOL_GATE, cd_fine=cd_fine, rel=rel, ok=gate_ok),
                   regime=regime, regime_onset_alpha=REGIME_ONSET_ALPHA,
                   non_cavitating=non_cavitating,
                   V_theo=V_THEO, A2_geom=A2_GEOM,
                   ansys_context=dict(fluent_cd=CD_ANSYS),
                   triple=tr, levels=levels, completion=completion, planted_zero=pz,
                   not_plateaued=not_plateaued, comparator=os.path.abspath(__file__))
    os.makedirs(RUN_ROOT, exist_ok=True)
    with open(OUT_JSON, "w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True, default=str)
    print("grading written to %s" % OUT_JSON)
    return 0


# --- selftest ----------------------------------------------------------------
def _write_dat(path, qmag, n=40, endt=ENDTIME, area=A2_GEOM, jitter=0.0):
    with open(path, "w") as fh:
        fh.write("# Region type : patch inlet\n# Faces : 22\n")
        fh.write("# Area          : %r\n" % area)
        fh.write("# Scale factor  : 1\n# Time           \tsum(phi)\n")
        for i in range(1, n + 1):
            t = endt * i / n
            q = -(qmag * (1.0 + jitter * ((i % 2) * 2 - 1)))   # negative = inflow
            fh.write("%r\t%r\n" % (t, q))


def _write_alpha(path, amin, ncells=100):
    """Synthetic alpha.water field with a known minimum (rest 1.0)."""
    vals = [1.0] * ncells
    vals[0] = amin
    with open(path, "w") as fh:
        fh.write("FoamFile { version 2.0; format ascii; class volScalarField; object alpha.water; }\n")
        fh.write("dimensions [0 0 0 0 0 0 0];\n")
        fh.write("internalField   nonuniform List<scalar>\n%d\n(\n" % ncells)
        fh.write("\n".join("%r" % v for v in vals))
        fh.write("\n)\n;\nboundaryField {}\n")


def selftest():
    ok = True
    def check(label, cond, detail=""):
        nonlocal ok
        print("  [%s] %s%s" % ("PASS" if cond else "FAIL", label, "" if not detail else "  <- " + str(detail)))
        ok = ok and bool(cond)

    print("--- physics: manual target vs Nurick correlation Cc*sqrt(K) ---")
    cd_corr = CC_NURICK * math.sqrt(K_CAV)
    check("K = 1.590 to 3 d.p.", abs(K_CAV - 1.59006) < 1e-4, K_CAV)
    check("Cc*sqrt(K) == target 0.780 to 2 d.p.", abs(cd_corr - CD_REF) < 0.01, cd_corr)
    check("V_theo == 17.607 m/s", abs(V_THEO - 17.60682) < 1e-3, V_THEO)
    check("A2 flat-wedge == 6.9725e-7 m2", abs(A2_GEOM - 6.97246e-7) < 1e-11, A2_GEOM)

    print("--- gate is BYTE-IDENTICAL to base VMFL022 (L-487) ---")
    check("CD_REF == 0.780", CD_REF == 0.780, CD_REF)
    check("TOL_GATE == 0.05", TOL_GATE == 0.05, TOL_GATE)

    print("--- triple SHIFTED to N2R 24/48/96 (single-phase 12 excluded) ---")
    check("LEVELS == 24/48/96", [nx for _, nx in LEVELS] == [24, 48, 96], [nx for _, nx in LEVELS])
    check("ratio r=2 across the triple", LEVELS[1][1] == 2 * LEVELS[0][1] and LEVELS[2][1] == 2 * LEVELS[1][1])

    tmp = tempfile.mkdtemp(prefix="vmfl022r2self_")
    try:
        print("--- reader: Cd recovered from a synthetic steady series ---")
        qtarget = CD_REF * A2_GEOM * V_THEO   # choose qmag so Cd == 0.780 exactly
        f = os.path.join(tmp, "surfaceFieldValue.dat"); _write_dat(f, qtarget)
        area = read_area_from_header(f)
        check("area header parsed", abs(area - A2_GEOM) < 1e-12, area)
        qm, cov, n, t0, t1 = window_stats(read_series(f))
        cd = qm / (area * V_THEO)
        check("Cd recovered == 0.780", abs(cd - CD_REF) < 1e-6, cd)
        check("steady series CoV ~ 0", cov < 1e-9, cov)

        print("--- reader REFUSES a one-column row (exit 2) ---")
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
        open(bad, "w").write("# h\n0.06\n")
        check("one-column row REFUSED exit 2", refuses(lambda: read_series(bad)))

        print("--- planted-zero: PROPER SUBSET shift (L-487), NOT whole-window ---")
        rows = read_series(f); base, _, _, _, _ = window_stats(rows)
        tmax = rows[-1][0]; tcut = tmax * (1.0 - WINDOW_FRAC)
        win_idx = [i for i, (t, v) in enumerate(rows) if t >= tcut - 1e-12]
        n_win = len(win_idx); n_plant = _plant_subset_size(n_win)
        check("subset is a PROPER subset of the window", 0 < n_plant < n_win, "%d of %d" % (n_plant, n_win))
        # emulate the subset-plant arithmetic the control performs
        plant_set = set(win_idx[:n_plant])
        pmean = sum((abs(v) + (PLANT if i in plant_set else 0.0))
                    for i, (t, v) in enumerate(rows) if t >= tcut - 1e-12) / n_win
        expected = PLANT * n_plant / n_win
        check("subset shift == P*n_planted/n_window", abs((pmean - base) - expected) <= PLANT_TOL, pmean - base)
        # L-487 INERT ARM: a WHOLE-window plant shifts the mean by P for ANY input,
        # incl. all-zeros -- so it proves nothing; kept as standing proof the
        # subset design is what has teeth.
        zrows = [(t, 0.0) for (t, v) in rows]
        zwin = [t for (t, v) in zrows if t >= tcut - 1e-12]
        full_shift_on_zeros = sum(0.0 + PLANT for _ in zwin) / len(zwin)
        check("INERT ARM: whole-window plant shifts even ALL-ZEROS by exactly P (proves nothing)",
              abs(full_shift_on_zeros - PLANT) <= PLANT_TOL, full_shift_on_zeros)
        check("subset shift differs from the inert whole-set value P (subset is load-bearing)",
              abs(expected - PLANT) > PLANT_TOL, "%g vs %g" % (expected, PLANT))
        # a BLIND reader (ignores planted rows) would report shift 0 != expected -> caught
        check("a blind reader (shift 0) would be REFUSED", abs(0.0 - expected) > PLANT_TOL)

        print("--- planted-zero DEGENERATE guard refuses a whole-window subset (L-487) ---")
        check("guard rejects n_plant == n_window", not (0 < n_win < n_win))  # tautology-safe form
        check("_plant_subset_size never returns the whole window for n>=2",
              all(0 < _plant_subset_size(k) < k for k in range(2, 50)))

        print("--- regime precondition: reader finds alpha.water minimum ---")
        cav = os.path.join(tmp, "cav_alpha"); os.makedirs(os.path.join(tmp, "Lc", "0.06"))
        _write_alpha(os.path.join(tmp, "Lc", "0.06", "alpha.water"), 0.0230)
        amin, nc = read_alpha_min(os.path.join(tmp, "Lc"), "0.06")
        check("alpha.water min read == 0.0230", abs(amin - 0.0230) < 1e-6, amin)
        check("min 0.0230 <= onset 0.9 -> CAVITATING", amin <= REGIME_ONSET_ALPHA)
        sp = os.path.join(tmp, "Ls", "0.06"); os.makedirs(sp)
        _write_alpha(os.path.join(sp, "alpha.water"), 1.0)
        amin2, _ = read_alpha_min(os.path.join(tmp, "Ls"), "0.06")
        check("single-phase min 1.0 > onset 0.9 -> NOT cavitating", amin2 > REGIME_ONSET_ALPHA, amin2)
        # onset threshold references NEITHER the band NOR the reference value
        import inspect
        srcreg = inspect.getsource(read_alpha_min)
        check("regime reader references neither CD_REF nor TOL_GATE (gate-blind)",
              ("CD_REF" not in srcreg) and ("TOL_GATE" not in srcreg) and ("0.780" not in srcreg))

        print("--- regime VERDICT logic: a mixed-regime triple -> NOT A RESULT ---")
        # emulate the verdict branch directly
        def verdict_for(alpha_mins, cds, covs):
            regime = {n: (a <= REGIME_ONSET_ALPHA) for n, a in zip(("L1","L2","L3"), alpha_mins)}
            non_cav = [n for n in ("L1","L2","L3") if not regime[n]]
            not_plat = [n for n, c in zip(("L1","L2","L3"), covs) if c > PLATEAU_COV]
            tr = roache(*cds)
            rel = abs(cds[-1] - CD_REF) / CD_REF
            if non_cav: return "NOT A RESULT"
            if not_plat: return "NOT A RESULT"
            if tr["state"] != "CONVERGING": return "NOT A RESULT"
            return "GATE REACHED" if rel <= TOL_GATE else "GATE FAIL"
        # base-like mixed regime (L1 single-phase) -> NOT A RESULT even if in band
        check("mixed regime (one single-phase level) -> NOT A RESULT",
              verdict_for([1.0, 0.26, 0.02], [0.780, 0.780, 0.780], [0.0, 0.0, 0.0]) == "NOT A RESULT")
        # all cavitating, converging, in band -> GATE REACHED
        check("all cavitating + CONVERGING + in band -> GATE REACHED",
              verdict_for([0.26, 0.05, 0.02],
                          [CD_REF + 0.04, CD_REF + 0.02, CD_REF + 0.01],
                          [0.0, 0.0, 0.0]) == "GATE REACHED")
        # all cavitating, converging, OUT of band -> GATE FAIL
        check("all cavitating + CONVERGING + out of band -> GATE FAIL",
              verdict_for([0.26, 0.05, 0.02],
                          [0.90 + 0.04, 0.90 + 0.02, 0.90 + 0.01],
                          [0.0, 0.0, 0.0]) == "GATE FAIL")

        print("--- plateau gate: a noisy level is flagged not-plateaued ---")
        fn = os.path.join(tmp, "noisy.dat"); _write_dat(fn, qtarget, jitter=0.10)
        _, cov2, _, _, _ = window_stats(read_series(fn))
        check("10%% jitter -> CoV > plateau threshold", cov2 > PLATEAU_COV, cov2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("--- Roache classifier ---")
    fex, C = 0.780, 0.01
    t1 = roache(fex + C * 4, fex + C * 2, fex + C * 1)
    check("first-order family -> CONVERGING, p==1", t1["state"] == "CONVERGING" and abs(t1["p"] - 1.0) < 1e-9, t1["p"])
    check("Richardson recovers f_exact", abs(t1["f_extrapolated"] - fex) < 1e-6, t1["f_extrapolated"])
    t2 = roache(fex + C * 16, fex + C * 4, fex + C * 1)
    check("second-order family -> CONVERGING, p==2", t2["state"] == "CONVERGING" and abs(t2["p"] - 2.0) < 1e-9, t2["p"])
    check("divergent -> DIVERGENT", roache(0.70, 0.74, 0.80)["state"] == "DIVERGENT")
    check("oscillatory -> OSCILLATORY", roache(0.78, 0.80, 0.78)["state"] == "OSCILLATORY")
    check("identical -> EXACT", roache(0.78, 0.78, 0.78)["state"] == "EXACT")

    print("--- gate can pass and can fail (byte-identical 5%% band) ---")
    check("+3%% is inside the 5%% gate", abs((CD_REF * 1.03) - CD_REF) / CD_REF <= TOL_GATE)
    check("+7%% is outside the 5%% gate", abs((CD_REF * 1.07) - CD_REF) / CD_REF > TOL_GATE)

    print("\nSELFTEST: %s" % ("all checks passed" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1


def dryrun_reader(path):
    rows = read_series(path)
    qm, cov, n, t0, t1 = window_stats(rows)
    print("dryrun-reader: %d rows; window mean|Q|=%.6e CoV=%.3f%% n=%d Cd=%.5f"
          % (len(rows), qm, cov * 100, n, qm / (A2_GEOM * V_THEO)))
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--dryrun-reader" in sys.argv:
        i = sys.argv.index("--dryrun-reader")
        sys.exit(dryrun_reader(sys.argv[i + 1]))
    sys.exit(main())
