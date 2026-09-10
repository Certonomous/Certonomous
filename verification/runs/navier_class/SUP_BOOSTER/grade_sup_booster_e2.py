#!/usr/bin/env python3
"""grade_sup_booster_e2.py -- EXACT-tier grader for Navier-class Case-3 SUCCESSOR E2
(SUP_BOOSTER), the Taylor-Maccoll supersonic sharp cone.  Grades the CFD against the same
REGENERATED TM reference (taylor_maccoll_reference.py, blob 0a17270c); no external PDF.

E2 vs E1 (grade_sup_booster.py, frozen blob 3c8d418a): TWO changes, both confined to the
shock-angle path.
  (1) INSTRUMENT.  read_shock_angle now finds the shock by the FREESTREAM-DENSITY-BOUNDARY
      crossing (scan each radial column from the outside inward, shock = outermost r where rho
      exceeds the per-station freestream by SHOCK_EPS), replacing E1's max |d rho/dr| which
      near-wall clustering fooled into a non-apex-anchored line (E1 RUN VERDICT NOT A RESULT,
      refuse on C2).  It now ALSO returns the per-station local radial cell size at the located
      radius, from the single axial column nearest the station, so the locator increment can be
      measured rather than assumed.
  (2) GATING METHOD FOR C2 ONLY, per the verification-supervisor's ruling of 2026-09-09
      (commit 0e9c1bcb).  C2 is decoupled from the "both CONVERGING" Roache coupling and gated
      by value-in-band + a separate tighter consistency bound; see WHAT IT GRADES below.
      NO gate value, band, threshold or reference moves (ruling condition 2), C1's Roache path
      is untouched (condition 1), and no Roache instrument is applied to C2 (condition 8).
Everything else -- rule-3 planted-zero, rule-4 completion (p U T rho + age guard), C1's
rule-5 Roache/Celik + iterative plateau, the cone-Cp owner-cell plateau reader,
refuse-not-degrade, exit vocabulary -- is byte-identical to the vetted E1 grader.  Run on the
E2 mesh (gen_cone_mesh_e2.py, gentler radial grading) so the cone-surface Cp triple is
asymptotic/CONVERGING.  Gate bands unchanged from E1.

WHAT IT GRADES (both against the frozen TM reference JSON):
  * Gate C1  -- cone-surface pressure coefficient Cp_cone (the PRIMARY EXACT gate).  Decided
                ONLY through the Roache triple over the (coarse, medium, fine) grids: a
                non-CONVERGING triple is NOT A RESULT whatever the value (rule 5); a
                CONVERGING triple is PASS inside the pre-registered band else GATE FAIL,
                with the Celik Fs=1.25 GCI printed.  UNCHANGED.
  * Gate C2  -- conical shock angle beta (SECONDARY).  DECOUPLED from the Roache triple by
                the verification-supervisor's ruling
                `verification/campaign/SUP_BOOSTER_E2_C2_SHOCK_ANGLE_GATING_RULING_2026-09-09.md`
                (commit 0e9c1bcb, framing (ii) GRANTED, its 8 conditions binding), on the DMR
                Gate-P2 / F19 / F4S precedent: a captured shock's located radius is quantised
                by the cell size, so its Roache triple is systematically OSCILLATORY even for
                a correct solution and Richardson extrapolation is the WRONG INSTRUMENT.  C2
                is therefore gated as
                    ACCURACY     |beta_fine - beta_ref| <= BETA_BAND_DEG      (band unchanged)
                    CONSISTENCY  max|beta_i - beta_j|   <= BETA_CONS_DEG      (SEPARATE, TIGHTER)
                with beta_fine REPORTED WITH ITS SUB-CELL LOCATOR INCREMENT, and with the
                framing's own precondition enforced: if the fine-grid locator increment is not
                strictly below the band, C2 would be measuring locator resolution rather than
                accuracy, the registered framing does not hold, and C2 is NOT A RESULT.
                NO Roache triple, GCI, observed order or Richardson value is computed, printed
                or reported for C2 -- F4S forbidden-instrument discipline (ruling condition 8).
  Rung PASS still requires BOTH gates PASS (ruling condition 1): C2 cannot rescue a C1 failure.

NON-NEGOTIABLES BUILT IN:
  * RULE 3 planted-zero control.  Before any clean read is trusted, PLANT a known pressure
    perturbation into a cone owner-cell of a COPY of the finest field, read it back through
    the SAME cone-Cp reader, and REFUSE (exit 2) unless the reader's reported surface
    pressure moves by the planted amount.  A zero from a reader not shown able to see a
    non-zero is not evidence.
  * RULE 4 strict completion, per level: rc==0 (DONE marker or log 'End'); last time dir ==
    endTime (from the case controlDict); the physics fields THIS solver writes
    (p, U, T, rho) present at endTime; and every one of them NEWER than the case's own 0/T
    (age guard).  NB the thermal-family field list (p_rgh alphat nut k omega phi) does NOT
    apply -- this is an inviscid compressible Euler case; the enforced set is stated here
    and is p, U, T, rho.
  * REFUSE-NOT-DEGRADE: exit 2 on any missing / malformed / unreadable input or any control
    that does not behave.  exit 70 only for an internal defect of THIS grader (never a
    finding about a run).  exit 0 only when a verdict was actually produced.
  * Reads inputs only; writes at most one JSON report where the caller names it.  Sends
    nothing, commits nothing (rules 7, 16).

USAGE:
  python3 grade_sup_booster.py --coarse <dir> --medium <dir> --fine <dir> \
        --reference tm_reference_M2p0_tc15.json [--report out.json]
  python3 grade_sup_booster.py --selftest [--smoke <dir>]   # controls + Roache logic only
"""
import argparse, glob, gzip, json, math, os, re, shutil, subprocess, sys, tempfile

# ---- pre-registered gate parameters (frozen with the pre-registration) ----------------
PLANT_PA        = 1000.0     # Pa, planted-zero control perturbation (>> numerical noise, << signal)
CP_BAND         = 0.010      # Gate C1: |Cp_cfd - Cp_ref| <= CP_BAND  (~5% of Cp_ref=0.2022)
BETA_BAND_DEG   = 1.0        # Gate C2 ACCURACY: |beta_fine - beta_ref| <= 1.0 deg (UNCHANGED from E1)
BETA_CONS_DEG   = 0.60       # Gate C2 CONSISTENCY: max|beta_i - beta_j| over the three levels.
                             # A SEPARATE, TIGHTER, PRE-REGISTERED bound -- NOT the accuracy band
                             # (ruling condition 5: re-using +/-1.0 deg for both is toothless,
                             # since any three values within 1.0 deg of the reference are
                             # trivially within 2.0 deg of each other).  Derived from the
                             # fine-grid locator increment; the derivation and its three
                             # independent routes are in SUP_BOOSTER_E2_PREREGISTRATION.md section 3.
FS_CELIK        = 1.25       # Roache/Celik factor of safety
PLATEAU_TOL     = 0.005      # rule-5 clause-1: |dCp| between last two writes must be < this (else not iteratively converged)
TIP_TRIM        = 0.10       # drop the apex-most 10% of cone faces (conical singularity)
OUTLET_TRIM     = 0.05       # drop the outlet-most 5% of cone faces (outflow buffer)
GAMMA           = 1.4
P_INF           = 101325.0
M_INF           = 2.0
# shock-locator x-stations as fractions of cone length, in the self-similar mid region
SHOCK_STATIONS  = [0.35, 0.45, 0.55, 0.65, 0.75, 0.85]
STATION_HALFWIDTH = 0.02     # axial half-width of each station band, as a fraction of L.
                             # NARROWED from E1's 0.03 WITH A MEASURED BASIS, not tuned:
                             #   WHY NARROW.  The conical shock radius grows with x as
                             #   r_s = x tan(beta) = 0.6725 x, so a band of half-width w*L smears
                             #   the located radius over +/- w*L*0.6725.  At w=0.03 that is
                             #   +/-0.0201 m; at w=0.02 it is +/-0.0134 m.  Against the radial
                             #   cell size at the shock on the E2 FINE mesh (0.00495-0.00704 m,
                             #   from the blockMesh simpleGrading law, validated to 1% against the
                             #   E1 fine mesh on disk: predicted 0.00449-0.00799 vs measured
                             #   0.00445-0.00791), the smear is 5.1-8.1 cells at w=0.03 and
                             #   3.4-5.4 cells at w=0.02 -- a 33% reduction, exactly proportional.
                             #   The locator scans inward and stops at the FIRST crossing, so this
                             #   smear enters as a systematic OUTWARD bias of every located radius.
                             #   WHY NOT NARROWER.  The band must still hold >= 2 axial columns at
                             #   every station on the COARSEST grid, or the fit degenerates toward
                             #   a single column.  Measured on the coarse grid at w=0.02: 3,3,2,2,2,2
                             #   columns at the six stations -- exactly at the floor.  The axial cell
                             #   at the last station is 0.0223 m there, so w=0.015 would give a span
                             #   of 0.0296 m and could isolate ONE column.  0.02 is the narrowest
                             #   width that keeps every station multi-column on all three grids
                             #   (measured w=0.02 column counts: coarse 3-2, medium 5-2, fine 7-4).
                             # Measured 2026-09-10 by a cfd lab-lane on graded/{coarse,medium,fine}/15000.
SHOCK_EPS       = 0.03       # E2: density must exceed the per-station freestream by 3% to count
                             # as behind the shock.  The bracket is MEASURED, not asserted, on the
                             # three E1 graded solutions at endTime 15000 (same solver, same BCs,
                             # same axial mesh; E2 differs only in radial grading):
                             #   LOWER  freestream density scatter in the undisturbed outer column
                             #          (max |rho/rho_inf - 1| over cells at r >= 1.15 r_shock, all
                             #          six stations): coarse 1.9e-06, medium 8.5e-10, fine 0.0e+00.
                             #          The fine-grid ZERO was PLANTED-VERIFIED (rule 3): planting
                             #          1.234e-03 into one far-field cell made the same reader
                             #          report 1.234e-03.  SHOCK_EPS is >= 1.6e4x this floor.
                             #   UPPER  density rise just behind the shock foot, over all six
                             #          stations and all three levels: 18.2-21.5% (theory: the
                             #          normal-Mach relation at beta=33.9147 deg, M_inf=2 gives
                             #          19.6%).  Total compression to the cone surface, coarse
                             #          and medium: 37.3-37.8% (theory 37.8%).  SHOCK_EPS is
                             #          6.1x below the smallest measured shock jump and 12x
                             #          below the wall compression.
                             #          NOT USED AS A BOUND, but recorded: on the E1 FINE grid
                             #          the near-wall maximum reaches 89%, far above the 37.8%
                             #          cone-surface value.  That overshoot is E1's GR_RADIAL=12
                             #          near-wall pathology -- the very thing E2's gentler
                             #          grading targets -- and it lies inside the cone-surface
                             #          region, not at the shock, so it does not touch the
                             #          locator, which stops at the outermost crossing.
                             # Both bounds hold with margin.  Measured 2026-09-10 by a cfd lab-lane
                             # on verification/runs/navier_class/SUP_BOOSTER/graded/{coarse,medium,fine}/15000.

def refuse(msg):
    sys.stderr.write("REFUSE (exit 2): " + msg + "\n"); sys.exit(2)
def defect(msg):
    sys.stderr.write("INTERNAL DEFECT (exit 70): " + msg + "\n"); sys.exit(70)

# ---------------------------------------------------------------------------------------
# OpenFOAM ascii field / mesh parsing (reads only)
# ---------------------------------------------------------------------------------------
def _read(path):
    if os.path.exists(path):
        return open(path, "r", errors="replace").read()
    if os.path.exists(path + ".gz"):
        return gzip.open(path + ".gz", "rt", errors="replace").read()
    return None

def parse_internal_scalar(path):
    """Return (list_of_values, header_txt, span) for a nonuniform volScalarField internalField,
    or (uniform_value, ...) for a uniform one.  refuses if unreadable."""
    txt = _read(path)
    if txt is None:
        refuse(f"cannot read field {path}")
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\(", txt)
    if m:
        n = int(m.group(1))
        start = m.end()
        depth = 1; i = start
        while i < len(txt) and depth:
            if txt[i] == "(": depth += 1
            elif txt[i] == ")": depth -= 1
            i += 1
        body = txt[start:i-1]
        vals = [float(x) for x in body.split()]
        if len(vals) != n:
            refuse(f"{path}: header says {n} values, parsed {len(vals)}")
        return vals
    m = re.search(r"internalField\s+uniform\s+([-\deE.+]+)\s*;", txt)
    if m:
        return None  # uniform -> not gradeable as a field of cells here
    refuse(f"{path}: no parseable internalField")

def parse_boundary(case):
    """polyMesh/boundary -> {patch: (nFaces, startFace)}."""
    txt = _read(os.path.join(case, "constant/polyMesh/boundary"))
    if txt is None:
        refuse(f"no polyMesh/boundary in {case}")
    out = {}
    for m in re.finditer(r"(\w+)\s*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);", txt, re.S):
        out[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    if not out:
        refuse(f"no patches parsed from polyMesh/boundary in {case}")
    return out

def parse_owner(case):
    txt = _read(os.path.join(case, "constant/polyMesh/owner"))
    if txt is None:
        refuse(f"no polyMesh/owner in {case}")
    m = re.search(r"\n(\d+)\s*\(", txt)
    if not m:
        refuse(f"cannot find owner list header in {case}")
    n = int(m.group(1)); start = m.end()
    body = txt[start: txt.index(")", start)]
    own = [int(x) for x in body.split()]
    if len(own) != n:
        refuse(f"owner list: header {n}, parsed {len(own)}")
    return own

def cone_owner_cells(case):
    """Owner cell index of each cone-patch face (in blockMesh face order -- NOT assumed to be
    apex->base; cone_cells_sorted() imposes the spatial order used for trimming)."""
    bnd = parse_boundary(case)
    if "cone" not in bnd:
        refuse(f"no 'cone' patch in {case}")
    nF, sF = bnd["cone"]
    own = parse_owner(case)
    if sF + nF > len(own):
        refuse(f"cone faces [{sF},{sF+nF}) exceed owner list ({len(own)}) in {case}")
    return own[sF:sF+nF]

def cone_cells_sorted(case, time, Cx=None):
    """Cone owner cells SORTED by axial cell-centre Cx (ascending = apex->base), so the
    tip/outlet trim is spatially correct regardless of blockMesh face order (supervisor
    §3 hardening fix 1).  Cx may be passed in to avoid recomputing cell centres."""
    cells = cone_owner_cells(case)
    if Cx is None:
        Cx, _ = cell_centres(case, time)
    if any(c >= len(Cx) for c in cells):
        refuse(f"{case}: a cone owner-cell index exceeds the cell-centre field length")
    return sorted(cells, key=lambda c: Cx[c])

# ---------------------------------------------------------------------------------------
# cell centres (via OpenFOAM writeCellCentres, the analyse_t3 pattern)
# ---------------------------------------------------------------------------------------
def cell_centres(case, time):
    r = subprocess.run(["postProcess", "-func", "writeCellCentres", "-case", case,
                        "-time", str(time)], capture_output=True, text=True)
    if r.returncode != 0:
        refuse(f"writeCellCentres failed in {case} (rc {r.returncode})")
    Cx = parse_internal_scalar(os.path.join(case, str(time), "Cx"))
    Cy = parse_internal_scalar(os.path.join(case, str(time), "Cy"))
    if Cx is None or Cy is None:
        refuse(f"cell centres not readable in {case}/{time}")
    return Cx, Cy

# ---------------------------------------------------------------------------------------
# rule-4 strict completion
# ---------------------------------------------------------------------------------------
def read_endtime(case):
    txt = _read(os.path.join(case, "system/controlDict"))
    if txt is None:
        refuse(f"no controlDict in {case}")
    m = re.search(r"\bendTime\s+([-\deE.+]+)\s*;", txt)
    if not m:
        refuse(f"no endTime in {case}/system/controlDict")
    return float(m.group(1))

def time_dirs(case):
    ts = []
    for d in os.listdir(case):
        if re.fullmatch(r"\d+(\.\d+)?", d) and os.path.isdir(os.path.join(case, d)) and d != "0":
            ts.append(d)
    return sorted(ts, key=float)

def check_completion(case):
    endT = read_endtime(case)
    # rc / End
    logs = glob.glob(os.path.join(case, "log.rhoCentralFoam*")) + glob.glob(os.path.join(case, "log*rhoCentral*"))
    done = glob.glob(os.path.join(case, "DONE*"))
    ended = any("\nEnd\n" in (_read(l) or "") or (_read(l) or "").rstrip().endswith("End") for l in logs)
    if not (ended or done):
        refuse(f"{case}: no 'End' line in a rhoCentralFoam log and no DONE marker -- not complete")
    ts = time_dirs(case)
    if not ts:
        refuse(f"{case}: no time directories after 0")
    last = ts[-1]
    if abs(float(last) - endT) > 1e-9*max(1.0, abs(endT)):
        refuse(f"{case}: last time {last} != endTime {endT}")
    # fields present (this solver's physics set) + age guard vs 0/T
    zeroT = os.path.join(case, "0", "T")
    if not (os.path.exists(zeroT) or os.path.exists(zeroT + ".gz")):
        refuse(f"{case}: no 0/T to date the run (age guard cannot be applied)")
    base_mtime = os.path.getmtime(zeroT if os.path.exists(zeroT) else zeroT + ".gz")
    for fld in ("p", "U", "T", "rho"):
        fp = os.path.join(case, last, fld)
        real = fp if os.path.exists(fp) else (fp + ".gz" if os.path.exists(fp + ".gz") else None)
        if real is None:
            refuse(f"{case}: field {fld} missing at endTime {last}")
        if os.path.getmtime(real) <= base_mtime:
            refuse(f"{case}: field {fld}@{last} not newer than 0/T (age guard) -- stale result")
    return endT, last

# ---------------------------------------------------------------------------------------
# readers: cone-surface Cp  and  shock angle beta
# ---------------------------------------------------------------------------------------
def read_cone_pressure(case, time, p_path=None, Cx=None):
    """Trimmed mean of cone owner-cell pressure -> surface p.  Cone cells are sorted by axial
    position first (fix 1), then the apex-most TIP_TRIM and outlet-most OUTLET_TRIM fractions
    are dropped, leaving the self-similar plateau.  p_path overrides the field read (used by
    the planted-zero control to point at a perturbed copy)."""
    cells = cone_cells_sorted(case, time, Cx=Cx)
    pfile = p_path if p_path else os.path.join(case, str(time), "p")
    pv = parse_internal_scalar(pfile)
    if pv is None:
        refuse(f"{case}/{time}/p is uniform -- no field to grade")
    n = len(cells)
    lo = int(math.floor(TIP_TRIM * n)); hi = int(math.ceil((1.0 - OUTLET_TRIM) * n))
    sel = cells[lo:hi]
    if len(sel) < 3:
        refuse(f"{case}: too few cone faces ({n}) after trim to form a plateau mean")
    vals = [pv[c] for c in sel]
    return sum(vals) / len(vals), n

def cp_from_p(p_surface):
    return (p_surface / P_INF - 1.0) / (0.5 * GAMMA * M_INF * M_INF)

def read_shock_angle(case, time, Cx=None, Cy=None):
    """E2 ROBUST shock locator -- FREESTREAM-DENSITY-BOUNDARY crossing (replaces E1's
    max |d rho/dr|, which near-wall clustering fooled).  For each x-station, scan the radial
    column from the OUTSIDE (large r, undisturbed freestream) INWARD and take the shock as the
    OUTERMOST radius where density first rises above freestream by SHOCK_EPS.  This never
    reaches the clustered near-wall region, so near-wall shock-capture wiggles cannot be
    mistaken for the shock; it uses the KNOWN freestream state rather than a gradient extremum.
    Then least-squares fit r_s = m*x + b and REQUIRE the fit to pass near the apex.
    Cx/Cy may be passed in to avoid recomputing cell centres."""
    if Cx is None or Cy is None:
        Cx, Cy = cell_centres(case, time)
    rho = parse_internal_scalar(os.path.join(case, str(time), "rho"))
    if rho is None:
        refuse(f"{case}/{time}/rho uniform -- no shock to locate")
    if not (len(Cx) == len(Cy) == len(rho)):
        refuse(f"{case}/{time}: Cx/Cy/rho length mismatch")
    L = max(Cx)                     # cone length ~ max x
    xs, rs, drs = [], [], []
    for frac in SHOCK_STATIONS:
        x0 = frac * L
        sel = [i for i in range(len(Cx)) if abs(Cx[i] - x0) < STATION_HALFWIDTH * L and Cy[i] > 0]
        band = sorted((Cy[i], rho[i]) for i in sel)
        if len(band) < 5:
            continue
        # per-station LOCAL freestream = the OUTERMOST cell (r up to R_top > shock, so undisturbed).
        # Using the local outer cell -- not a global min -- is robust to any expansion region
        # elsewhere (e.g. a base/outlet corner where rho dips below freestream).
        rho_out = band[-1][1]
        thresh = rho_out * (1.0 + SHOCK_EPS)
        shock_r = None
        for r, rr in reversed(band):   # from OUTSIDE (large r) inward; first departure = shock foot
            if rr >= thresh:
                shock_r = r; break
        if shock_r is None:
            continue
        # LOCAL RADIAL CELL SIZE at the located radius -- the locator's own quantum, and the
        # input to the locator increment the C2 gate must report (ruling conditions 3 and 4).
        # It MUST come from ONE axial column: the station band spans several columns (measured
        # 2-7 on the graded family), and consecutive radii taken ACROSS columns are not a cell.
        # Cell centres inside a column share x to ~1e-6 while the axial cell is >= 5.7e-3, so a
        # 1e-4*L window isolates exactly one column.
        x_col = min((abs(Cx[i] - x0), Cx[i]) for i in sel)[1]
        col_r = sorted(Cy[i] for i in sel if abs(Cx[i] - x_col) < 1.0e-4 * L)
        if len(col_r) < 2:
            refuse(f"{case}/{time}: station x={x0:.4f} isolated < 2 radial cells in its own "
                   f"column -- the local radial cell size (locator increment) is not measurable")
        k = min(range(len(col_r)), key=lambda j: abs(col_r[j] - shock_r))
        if k == 0:
            dr = col_r[1] - col_r[0]
        elif k == len(col_r) - 1:
            dr = col_r[-1] - col_r[-2]
        else:
            dr = 0.5 * ((col_r[k+1] - col_r[k]) + (col_r[k] - col_r[k-1]))
        if not (dr > 0.0):
            refuse(f"{case}/{time}: station x={x0:.4f} gave a non-positive radial cell size {dr}")
        xs.append(x0); rs.append(shock_r); drs.append(dr)
    if len(xs) < 3:
        refuse(f"{case}/{time}: shock locator found < 3 usable stations")
    n = len(xs); sx = sum(xs); sr = sum(rs)
    sxx = sum(x*x for x in xs); sxr = sum(x*r for x, r in zip(xs, rs))
    m = (n*sxr - sx*sr) / (n*sxx - sx*sx)
    b = (sr - m*sx) / n
    if abs(b) > 0.05 * L:
        refuse(f"{case}/{time}: shock fit intercept {b:.4f} not near apex (>5% L) -- not a conical shock line")
    beta = math.degrees(math.atan(m))
    inc = locator_increment_deg(xs, drs, m)
    return beta, dict(stations_x=xs, stations_r=rs, stations_dr=drs, slope=m, intercept=b,
                      locator_increment_deg=inc["rms"],
                      locator_increment_single_station_deg=inc["single"],
                      locator_increment_correlated_worst_deg=inc["correlated_worst"])


def locator_increment_deg(xs, drs, m):
    """The SUB-CELL LOCATOR INCREMENT of beta, in degrees -- the angular quantum of this
    instrument, required beside beta_fine by ruling conditions 3 and 4.

    Each station's located radius is quantised by one local radial cell dr_i.  Propagating that
    quantum through the SAME least-squares slope the locator fits gives three figures; all are
    reported, and the REGISTERED increment is the rms one:

      rms               independent one-cell quantisation at every station, propagated in
                        quadrature -- sigma_m = sqrt(sum(((x_i-xbar) dr_i)^2)) / sum((x_i-xbar)^2).
                        THIS IS THE REGISTERED LOCATOR INCREMENT.  It is conservative: a genuine
                        quantisation error is uniform on [-dr/2, +dr/2] with standard deviation
                        dr/sqrt(12), so using the full dr_i overstates it by a factor ~3.5.
      single            one cell at ONE station, worst station -- the smallest honest quantum.
      correlated_worst  every station displaced one cell in the sign pattern that maximises the
                        slope change.  An adversarial conspiracy, not the instrument's
                        resolution; reported so nothing is hidden, NOT used for any gate.
    """
    n = len(xs)
    if n < 3 or len(drs) != n:
        defect(f"locator_increment_deg: {n} stations, {len(drs)} cell sizes")
    xbar = sum(xs) / n
    den = sum((x - xbar) ** 2 for x in xs)
    if den <= 0.0:
        defect("locator_increment_deg: degenerate station spread")
    def dbeta(dm):
        return math.degrees(math.atan(m + dm)) - math.degrees(math.atan(m))
    sig = math.sqrt(sum(((x - xbar) * d) ** 2 for x, d in zip(xs, drs))) / den
    single = max(dbeta(abs(x - xbar) * d / den) for x, d in zip(xs, drs))
    worst = sum(abs(x - xbar) * d for x, d in zip(xs, drs)) / den
    return dict(rms=dbeta(sig), single=single, correlated_worst=dbeta(worst))

# ---------------------------------------------------------------------------------------
# planted-zero control (rule 3)
# ---------------------------------------------------------------------------------------
def planted_zero_control(case, time):
    """Copy the endTime p field, add PLANT_PA to the FIRST cone owner-cell value, read the
    surface pressure back through read_cone_pressure, and require the reported plateau mean
    to rise (the reader must SEE a planted non-zero)."""
    cells = cone_cells_sorted(case, time)         # spatially sorted (fix 1), same order the reader trims
    n = len(cells)
    lo = int(math.floor(TIP_TRIM * n)); hi = int(math.ceil((1.0 - OUTLET_TRIM) * n))
    target_cell = cells[lo]                       # a cell that is INSIDE the trimmed plateau
    pfile = os.path.join(case, str(time), "p")
    txt = _read(pfile)
    if txt is None:
        refuse(f"planted control: cannot read {pfile}")
    base_mean, _ = read_cone_pressure(case, time)
    # write a perturbed copy: bump one internal value the reader will average
    pv = parse_internal_scalar(pfile)
    pv2 = list(pv); pv2[target_cell] += PLANT_PA
    work = tempfile.mkdtemp(prefix="sup_booster_plant_")
    try:
        pert = os.path.join(work, "p_perturbed")
        # rebuild the field file with the perturbed internal list
        head = txt[:txt.index("internalField")]
        tail = txt[txt.index("boundaryField"):]
        with open(pert, "w") as fh:
            fh.write(head)
            fh.write(f"internalField   nonuniform List<scalar>\n{len(pv2)}\n(\n")
            fh.write("\n".join(repr(v) for v in pv2))
            fh.write("\n)\n;\n\n")
            fh.write(tail)
        seen_mean, _ = read_cone_pressure(case, time, p_path=pert)
        delta = seen_mean - base_mean
        expected = PLANT_PA / (hi - lo)            # one bumped cell spread over the plateau mean
        ok = abs(delta - expected) < 0.05 * expected
        return dict(passed=bool(ok), planted_pa=PLANT_PA, target_cell=target_cell,
                    base_surface_p=base_mean, seen_surface_p=seen_mean,
                    reader_delta=delta, expected_delta=expected)
    finally:
        shutil.rmtree(work, ignore_errors=True)

# ---------------------------------------------------------------------------------------
# Roache triple gating + Celik GCI (rule 5)
# ---------------------------------------------------------------------------------------
def roache_triple(f1, f2, f3, h1, h2, h3):
    """f1=fine, f2=medium, f3=coarse; h1<h2<h3 representative grid sizes.
    Returns (classification, order p, gci_fine, extrapolated)."""
    e32 = f3 - f2; e21 = f2 - f1
    r21 = h2 / h1; r32 = h3 / h2
    if e21 == 0 or e32 == 0:
        return "STAGNANT", None, None, None
    ratio = e32 / e21
    if ratio <= 0:
        return "OSCILLATORY", None, None, None      # sign change -> non-monotone
    # Celik apparent order (fixed-point iteration on the standard formula)
    try:
        p = math.log(abs(ratio)) / math.log(r21)
        for _ in range(50):
            s = math.copysign(1.0, ratio)
            q = math.log((r21**p - s) / (r32**p - s)) if (r21**p - s) != 0 else 0.0
            p_new = abs(math.log(abs(ratio)) + q) / math.log(r21)
            if abs(p_new - p) < 1e-8:
                p = p_new; break
            p = p_new
    except (ValueError, ZeroDivisionError):
        return "DIVERGENT", None, None, None
    if not (0.1 < p < 6.0):
        return "DIVERGENT", p, None, None
    f_ext = (r21**p * f1 - f2) / (r21**p - 1.0)
    ea = abs(e21 / f1) if f1 != 0 else float("inf")
    gci_fine = FS_CELIK * ea / (r21**p - 1.0)
    return "CONVERGING", p, gci_fine, f_ext

def grade_gate(name, f_fine, f_med, f_coarse, h1, h2, h3, ref, band, unit):
    cls, p, gci, fext = roache_triple(f_fine, f_med, f_coarse, h1, h2, h3)
    out = dict(gate=name, value_fine=f_fine, value_medium=f_med, value_coarse=f_coarse,
               reference=ref, band=band, unit=unit, triple=cls, apparent_order_p=p,
               gci_fine=gci, richardson_extrap=fext)
    if cls != "CONVERGING":
        out["verdict"] = "NOT A RESULT"
        out["reason"] = f"grid triple is {cls}, not CONVERGING (rule 5)"
        return out
    inside = abs(f_fine - ref) <= band
    out["verdict"] = "PASS" if inside else "GATE FAIL"
    out["deviation"] = f_fine - ref
    return out


def grade_gate_shock_angle(name, b_fine, b_med, b_coarse, locinfo_fine, ref, band, b_cons, unit):
    """Gate C2 -- conical shock angle beta.  NOT a Roache gate, by the verification-supervisor's
    ruling of 2026-09-09 (commit 0e9c1bcb, framing (ii)).  No triple, no GCI, no observed order,
    no Richardson value is computed or emitted here: for a quantity whose located value is
    quantised by the cell size, Richardson extrapolation is the wrong instrument, and quoting it
    anyway is the F4S forbidden-instrument failure (ruling condition 8).

    Three measured things decide C2, and they are printed whatever the verdict:
      * beta_fine WITH its sub-cell locator increment                     (condition 3)
      * PRECONDITION: the accuracy band must strictly EXCEED that increment (condition 4).  If it
        does not, C2 is measuring locator resolution rather than accuracy, the registered framing
        does not hold, and the honest label is NOT A RESULT -- not a GATE FAIL, because the
        instrument, not the solution, is what failed.  Substituting a different gate at grade
        time is forbidden (rule 2), so the grader cannot repair this; it reports it.
      * ACCURACY    |beta_fine - ref| <= band        AND
        CONSISTENCY max|beta_i - beta_j| <= b_cons   (a SEPARATE, TIGHTER, pre-registered bound,
                                                      condition 5)
      -> PASS iff both hold, else GATE FAIL naming which one failed.
    """
    inc = locinfo_fine["locator_increment_deg"]
    betas = dict(fine=b_fine, medium=b_med, coarse=b_coarse)
    spread = max(betas.values()) - min(betas.values())
    out = dict(gate=name, gating_method="value-in-band + locator-increment consistency "
                                        "(NOT Roache; ruling 0e9c1bcb conditions 1-8)",
               value_fine=b_fine, value_medium=b_med, value_coarse=b_coarse,
               reference=ref, band=band, consistency_bound=b_cons, unit=unit,
               locator_increment_deg=inc,
               locator_increment_single_station_deg=locinfo_fine["locator_increment_single_station_deg"],
               locator_increment_correlated_worst_deg=locinfo_fine["locator_increment_correlated_worst_deg"],
               beta_fine_reported_as=f"{b_fine:.4f} +/- {inc:.4f} {unit} (locator increment)",
               band_exceeds_locator_increment=bool(inc < band),
               deviation=b_fine - ref, spread=spread)
    if not (inc < band):
        out["verdict"] = "NOT A RESULT"
        out["reason"] = (f"fine-grid locator increment {inc:.4f} {unit} is not below the "
                         f"accuracy band {band} {unit}: C2 would be measuring locator resolution, "
                         f"not accuracy, so the registered framing (ruling condition 4) does not "
                         f"hold and no verdict on the value is entitled")
        return out
    acc_ok = abs(b_fine - ref) <= band
    con_ok = spread <= b_cons
    out["accuracy_passed"] = bool(acc_ok)
    out["consistency_passed"] = bool(con_ok)
    if acc_ok and con_ok:
        out["verdict"] = "PASS"
        return out
    out["verdict"] = "GATE FAIL"
    why = []
    if not acc_ok:
        why.append(f"ACCURACY: |{b_fine:.4f} - {ref}| = {abs(b_fine-ref):.4f} > band {band}")
    if not con_ok:
        why.append(f"CONSISTENCY: max|beta_i - beta_j| = {spread:.4f} > B_cons {b_cons}")
    out["reason"] = "; ".join(why)
    return out

# ---------------------------------------------------------------------------------------
def grade_case(case):
    endT, last = check_completion(case)
    Cx, Cy = cell_centres(case, last)          # computed ONCE; nCells and both readers reuse it
    ncells = len(Cx)
    p_surf, nfaces = read_cone_pressure(case, last, Cx=Cx)
    cp = cp_from_p(p_surf)
    beta, locinfo = read_shock_angle(case, last, Cx=Cx, Cy=Cy)
    # rule-5 clause-1: iterative-plateau check on the graded quantity (cone Cp)
    ts = time_dirs(case)
    plateaued, cp_prev = True, None
    if len(ts) >= 2:
        pp, _ = read_cone_pressure(case, ts[-2], Cx=Cx)   # same mesh -> same cell centres
        cp_prev = cp_from_p(pp)
        plateaued = abs(cp - cp_prev) <= PLATEAU_TOL * abs(cp) if cp else False
    else:
        plateaued = False
    return dict(case=case, nCells=ncells, endTime=endT, last=last, cone_faces=nfaces,
                surface_p=p_surf, Cp_cone=cp, Cp_prev_write=cp_prev, beta_deg=beta,
                iteratively_plateaued=plateaued, shock_fit=locinfo)

def run_grade(args):
    ref = json.load(open(args.reference))["reference"]
    cp_ref = ref["Cp_cone"]; beta_ref = ref["beta_deg"]
    levels = {"fine": args.fine, "medium": args.medium, "coarse": args.coarse}
    if not all(levels.values()):
        refuse("all three of --coarse --medium --fine are required for the Roache triple")
    # RULE 3 control on the finest, before trusting any read
    ctrl = planted_zero_control(args.fine, check_completion(args.fine)[1])
    if not ctrl["passed"]:
        refuse(f"planted-zero control did not behave: {ctrl}")
    per = {name: grade_case(d) for name, d in levels.items()}
    # fix 2: tie the Roache r to the meshes ACTUALLY graded.  Representative grid size in 2-D
    # is h ~ 1/sqrt(nCells); the registered family is 2.25x cells per level (r = 1.5 in h).
    # ASSERT both step ratios are 1.5 to tolerance, else REFUSE -- the GCI is only valid on
    # the registered refinement family.
    nc = {k: per[k]["nCells"] for k in per}
    h = {k: 1.0 / math.sqrt(nc[k]) for k in nc}
    r_fm = h["medium"] / h["fine"]      # = sqrt(nCells_fine / nCells_medium)
    r_cm = h["coarse"] / h["medium"]    # = sqrt(nCells_medium / nCells_coarse)
    R_TOL = 0.08
    if not (abs(r_fm - 1.5) < R_TOL and abs(r_cm - 1.5) < R_TOL):
        refuse(f"graded meshes are not the registered 2.25x family: nCells={nc}, "
               f"h-ratios medium/fine={r_fm:.4f}, coarse/medium={r_cm:.4f} (want ~1.5) -- "
               f"the registered GCI r does not hold, cannot grade this triple")
    # rule-5 clause-1: a level not iteratively converged makes the whole triple NOT A RESULT
    not_plateaued = [n for n in per if not per[n]["iteratively_plateaued"]]
    if not_plateaued:
        report = dict(planted_zero_control=ctrl, per_level=per, reference=ref,
                      gates=[dict(gate=g, verdict="NOT A RESULT",
                                  reason=f"levels not iteratively plateaued (rule 5 clause 1): {not_plateaued}")
                             for g in ("C1 cone-surface Cp", "C2 shock angle beta")])
        print(json.dumps(report, indent=2))
        if args.report:
            json.dump(report, open(args.report, "w"), indent=2)
        return 0
    gate_cp = grade_gate("C1 cone-surface Cp", per["fine"]["Cp_cone"], per["medium"]["Cp_cone"],
                         per["coarse"]["Cp_cone"], h["fine"], h["medium"], h["coarse"], cp_ref, CP_BAND, "-")
    # C2 is NOT put through grade_gate: no h, no triple, no GCI reaches it (condition 8).
    gate_b = grade_gate_shock_angle("C2 shock angle beta", per["fine"]["beta_deg"],
                                    per["medium"]["beta_deg"], per["coarse"]["beta_deg"],
                                    per["fine"]["shock_fit"], beta_ref, BETA_BAND_DEG,
                                    BETA_CONS_DEG, "deg")
    for forbidden in ("triple", "apparent_order_p", "gci_fine", "richardson_extrap"):
        if forbidden in gate_b:                   # executable form of condition 8
            defect(f"C2 report carries the forbidden Roache instrument '{forbidden}'")
    report = dict(planted_zero_control=ctrl, per_level=per, grid=dict(nCells=nc, h=h,
                  r_medium_fine=r_fm, r_coarse_medium=r_cm), gates=[gate_cp, gate_b], reference=ref)
    print(json.dumps(report, indent=2))
    if args.report:
        json.dump(report, open(args.report, "w"), indent=2)
    verdicts = [gate_cp["verdict"], gate_b["verdict"]]
    return 0 if all(v in ("PASS", "GATE FAIL", "NOT A RESULT") for v in verdicts) else 70

def selftest_fail(check, detail):
    """Explicit selftest failure.  NOT an `assert`: under `python3 -O` / PYTHONOPTIMIZE every
    assert is compiled out, which made the whole self-check VOID under -O (measured 2026-09-10
    on this grader: a mutated expectation still printed SELFTEST OK and exited 0, certifying a
    mutated grader as sound).  Territory rule L-332 -- no assert in an instrument may carry a
    refusal, guard, control or gate; a selftest's assertions ARE the gate on the instrument."""
    sys.stderr.write(f"SELFTEST FAIL: {check}: {detail}\n")
    sys.exit(1)

def _selftest_build_cone_case(root):
    """Build a THROWAWAY OpenFOAM case (40x10 hex block, one 'cone' patch of 40 faces) inside a
    temp dir, so the rule-3 planted-zero control can be exercised through the REAL on-disk
    reader.  Touches no graded run root: nothing under verification/runs is read or written,
    and neither graded_e2/ nor E1's graded/ is opened.  Returns the case path."""
    case = os.path.join(root, "selftest_cone")
    for sub in ("system", "constant"):
        os.makedirs(os.path.join(case, sub))
    with open(os.path.join(case, "system/controlDict"), "w") as fh:
        fh.write("FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }\n"
                 "application rhoCentralFoam;\nstartFrom startTime;\nstartTime 0;\n"
                 "stopAt endTime;\nendTime 1;\ndeltaT 1;\nwriteControl timeStep;\nwriteInterval 1;\n")
    with open(os.path.join(case, "system/fvSchemes"), "w") as fh:
        fh.write("FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }\n"
                 "ddtSchemes { default Euler; }\ngradSchemes { default Gauss linear; }\n"
                 "divSchemes { default none; }\nlaplacianSchemes { default Gauss linear corrected; }\n"
                 "interpolationSchemes { default linear; }\nsnGradSchemes { default corrected; }\n")
    with open(os.path.join(case, "system/fvSolution"), "w") as fh:
        fh.write("FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }\n"
                 "solvers {}\n")
    with open(os.path.join(case, "system/blockMeshDict"), "w") as fh:
        fh.write("FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }\n"
                 "scale 1;\n"
                 "vertices ( (0 0 0) (1 0 0) (1 0.2 0) (0 0.2 0)\n"
                 "           (0 0 0.1) (1 0 0.1) (1 0.2 0.1) (0 0.2 0.1) );\n"
                 "blocks ( hex (0 1 2 3 4 5 6 7) (40 10 1) simpleGrading (1 1 1) );\n"
                 "edges ();\n"
                 "boundary\n(\n"
                 "    cone     { type wall;  faces ( (0 1 5 4) ); }\n"
                 "    farfield { type patch; faces ( (3 7 6 2) ); }\n"
                 "    inlet    { type patch; faces ( (0 4 7 3) ); }\n"
                 "    outlet   { type patch; faces ( (1 2 6 5) ); }\n"
                 "    frontAndBack { type empty; faces ( (0 3 2 1) (4 5 6 7) ); }\n"
                 ");\nmergePatchPairs ();\n")
    r = subprocess.run(["blockMesh", "-case", case], capture_output=True, text=True)
    if r.returncode != 0:
        selftest_fail("planted-zero control arm",
                      f"blockMesh failed on the throwaway selftest case (rc {r.returncode})")
    ncells = 40 * 10
    os.makedirs(os.path.join(case, "1"))
    with open(os.path.join(case, "1", "p"), "w") as fh:
        fh.write('FoamFile { version 2.0; format ascii; class volScalarField; location "1"; object p; }\n')
        fh.write("dimensions [1 -1 -2 0 0 0 0];\n")
        fh.write(f"internalField   nonuniform List<scalar>\n{ncells}\n(\n")
        fh.write("\n".join(repr(P_INF) for _ in range(ncells)))
        fh.write("\n)\n;\n\n")
        fh.write('boundaryField\n{\n    ".*" { type zeroGradient; }\n}\n')
    return case

def run_selftest(args):
    print("== Roache logic on a synthetic CONVERGING triple ==")
    g = grade_gate("selftest", 0.2025, 0.2050, 0.2100, 1.0, 1.5, 2.25, 0.20225, CP_BAND, "-")
    if g["triple"] != "CONVERGING":
        selftest_fail("synthetic CONVERGING triple: triple", g)
    if g["verdict"] != "PASS":
        selftest_fail("synthetic CONVERGING triple: verdict", g)
    print(f"  CONVERGING, p={g['apparent_order_p']:.3f}, GCI={g['gci_fine']:.3e}, verdict={g['verdict']}")
    print("== Roache logic on a synthetic OSCILLATORY triple (must be NOT A RESULT) ==")
    g2 = grade_gate("selftest2", 0.20, 0.22, 0.19, 1.0, 1.5, 2.25, 0.20225, CP_BAND, "-")
    if g2["verdict"] != "NOT A RESULT":
        selftest_fail("synthetic OSCILLATORY triple: verdict", g2)
    print(f"  {g2['triple']} -> {g2['verdict']}")
    print("== Roache logic on a synthetic CONVERGING-but-OUTSIDE-band triple (must be GATE FAIL) ==")
    g3 = grade_gate("selftest3", 0.250, 0.253, 0.259, 1.0, 1.5, 2.25, 0.20225, CP_BAND, "-")
    if g3["triple"] != "CONVERGING":
        selftest_fail("synthetic out-of-band triple: triple", g3)
    if g3["verdict"] != "GATE FAIL":
        selftest_fail("synthetic out-of-band triple: verdict", g3)
    print(f"  CONVERGING, dev={g3['deviation']:.4f} > band {CP_BAND} -> {g3['verdict']}")
    print("== C2 (shock angle) gating -- value-in-band + consistency, NO Roache (ruling 0e9c1bcb) ==")
    def _loc(inc):
        return dict(locator_increment_deg=inc, locator_increment_single_station_deg=inc*0.7,
                    locator_increment_correlated_worst_deg=inc*2.1)
    c2a = grade_gate_shock_angle("selftest C2 in-band+consistent", 33.85, 33.99, 33.70,
                                 _loc(0.57), 33.9147, BETA_BAND_DEG, BETA_CONS_DEG, "deg")
    if c2a["verdict"] != "PASS":
        selftest_fail("C2 in-band+consistent: verdict", c2a)
    print(f"  in band, spread {c2a['spread']:.4f} <= {BETA_CONS_DEG} -> {c2a['verdict']} "
          f"(beta reported as {c2a['beta_fine_reported_as']})")
    c2b = grade_gate_shock_angle("selftest C2 out-of-band", 35.50, 35.40, 35.60,
                                 _loc(0.57), 33.9147, BETA_BAND_DEG, BETA_CONS_DEG, "deg")
    if not (c2b["verdict"] == "GATE FAIL" and "ACCURACY" in c2b["reason"]):
        selftest_fail("C2 out-of-band: verdict/reason", c2b)
    print(f"  outside the band, spread OK -> {c2b['verdict']} ({c2b['reason']})")
    c2c = grade_gate_shock_angle("selftest C2 inconsistent", 33.85, 34.60, 33.20,
                                 _loc(0.57), 33.9147, BETA_BAND_DEG, BETA_CONS_DEG, "deg")
    if not (c2c["verdict"] == "GATE FAIL" and "CONSISTENCY" in c2c["reason"]):
        selftest_fail("C2 inconsistent: verdict/reason", c2c)
    print(f"  in band but spread {c2c['spread']:.4f} > {BETA_CONS_DEG} -> {c2c['verdict']}")
    c2d = grade_gate_shock_angle("selftest C2 locator too coarse", 33.85, 33.99, 33.70,
                                 _loc(1.30), 33.9147, BETA_BAND_DEG, BETA_CONS_DEG, "deg")
    if c2d["verdict"] != "NOT A RESULT":
        selftest_fail("C2 locator too coarse: verdict", c2d)
    print(f"  locator increment 1.30 deg >= band {BETA_BAND_DEG} deg -> {c2d['verdict']} "
          f"(condition-4 precondition fails)")
    print("== condition 8: NO Roache instrument may appear anywhere in a C2 report ==")
    for g in (c2a, c2b, c2c, c2d):
        for forbidden in ("triple", "apparent_order_p", "gci_fine", "richardson_extrap"):
            if forbidden in g:
                selftest_fail("condition 8: forbidden Roache instrument in a C2 report",
                              (forbidden, g))
    print("  no triple / apparent_order_p / gci_fine / richardson_extrap in any C2 report -- OK")
    print("== an OSCILLATORY beta triple no longer vetoes C2 (the spurious veto the ruling removes) ==")
    osc = grade_gate("beta-as-if-Roache", 33.85, 33.99, 33.70, 1.0, 1.5, 2.25, 33.9147, BETA_BAND_DEG, "deg")
    if not (osc["verdict"] == "NOT A RESULT" and osc["triple"] == "OSCILLATORY"):
        selftest_fail("beta-as-if-Roache: verdict/triple", osc)
    if c2a["verdict"] != "PASS":
        selftest_fail("beta-as-if-Roache: C2 comparison arm", c2a)
    print(f"  same three values: as a Roache triple -> {osc['triple']}/{osc['verdict']}; "
          f"under the registered C2 method -> {c2a['verdict']}")
    print("== rule-3 planted-zero control, exercised through the REAL reader (MANDATORY arm) ==")
    for tool in ("blockMesh", "postProcess"):
        if shutil.which(tool) is None:
            selftest_fail("planted-zero control arm",
                          f"'{tool}' is not on PATH, so the selftest cannot exercise the rule-3 "
                          f"control -- it therefore REFUSES to certify this grader (source the "
                          f"OpenFOAM bashrc first)")
    work = tempfile.mkdtemp(prefix="sup_booster_selftest_")
    try:
        case = _selftest_build_cone_case(work)
        ctrl = planted_zero_control(case, "1")
        print("  positive arm: " + json.dumps(ctrl))
        if not ctrl["passed"]:
            selftest_fail("planted-zero control POSITIVE arm",
                          f"the real reader did NOT see the planted {PLANT_PA} Pa: {ctrl}")
        if abs(ctrl["reader_delta"] - ctrl["expected_delta"]) >= 0.05 * ctrl["expected_delta"]:
            selftest_fail("planted-zero control POSITIVE arm",
                          f"reader_delta {ctrl['reader_delta']} does not match expected_delta "
                          f"{ctrl['expected_delta']}: {ctrl}")
        print(f"  reader saw the plant: delta={ctrl['reader_delta']:.6f} Pa vs expected "
              f"{ctrl['expected_delta']:.6f} Pa -- control ALIVE")
        # NEGATIVE arm: a control that cannot see its own plant must FAIL, never pass.  Blind the
        # reader by discarding the perturbed-copy path (the plant becomes a no-op as far as the
        # reader is concerned), then require passed=False.  Restored in the finally.
        real_reader = globals()["read_cone_pressure"]
        def _blind_reader(case_, time_, p_path=None, Cx=None):
            return real_reader(case_, time_, p_path=None, Cx=Cx)   # ignores the planted copy
        globals()["read_cone_pressure"] = _blind_reader
        try:
            neutered = planted_zero_control(case, "1")
        finally:
            globals()["read_cone_pressure"] = real_reader
        print("  negative arm (reader blinded to the plant): " + json.dumps(neutered))
        if neutered["passed"]:
            selftest_fail("planted-zero control NEGATIVE arm",
                          f"a reader that CANNOT see its own plant was still reported as passing "
                          f"-- the control is neutered and certifies nothing: {neutered}")
        if globals()["read_cone_pressure"] is not real_reader:
            selftest_fail("planted-zero control NEGATIVE arm",
                          "the real reader was not restored after the negative arm")
        print(f"  blinded reader delta={neutered['reader_delta']:.6f} Pa -> control correctly "
              f"reports passed=False (a neutered control is CAUGHT)")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    if args.smoke:
        print(f"== planted-zero control on smoke case {args.smoke} (real disk read) ==")
        ts = time_dirs(args.smoke)
        if not ts:
            refuse("smoke case has no time dirs for the control")
        ctrl = planted_zero_control(args.smoke, ts[-1])
        print("  " + json.dumps(ctrl))
        p_surf, nf = read_cone_pressure(args.smoke, ts[-1])
        print(f"  smoke cone-surface p (unconverged, sanity only) = {p_surf:.1f} Pa -> Cp = {cp_from_p(p_surf):.4f}"
              f"  over {nf} cone faces")
        if not ctrl["passed"]:
            refuse("planted-zero control FAILED on smoke case")
        print("  planted-zero control PASSED (reader sees the planted perturbation)")
    if args.shock_check:
        print(f"== E2 robust shock locator on {args.shock_check} (freestream-crossing) ==")
        ts = time_dirs(args.shock_check)
        beta, info = read_shock_angle(args.shock_check, ts[-1])
        print(f"  located beta = {beta:.3f} +/- {info['locator_increment_deg']:.4f} deg "
              f"(sub-cell locator increment)  (TM reference 33.9147 deg); "
              f"fit slope={info['slope']:.4f} intercept={info['intercept']:.5f}")
        print(f"  stations_r={[round(r,4) for r in info['stations_r']]}  "
              f"dr_at_shock={[round(d,5) for d in info['stations_dr']]}")
        print(f"  locator increment: rms(registered)={info['locator_increment_deg']:.4f} deg, "
              f"single-station={info['locator_increment_single_station_deg']:.4f} deg, "
              f"correlated-worst={info['locator_increment_correlated_worst_deg']:.4f} deg; "
              f"band {BETA_BAND_DEG} deg "
              f"{'EXCEEDS' if info['locator_increment_deg'] < BETA_BAND_DEG else 'DOES NOT EXCEED'} "
              f"the registered increment (ruling condition 4)")
    print("SELFTEST OK")
    return 0

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--coarse"); ap.add_argument("--medium"); ap.add_argument("--fine")
    ap.add_argument("--reference"); ap.add_argument("--report")
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--smoke")
    ap.add_argument("--shock-check", help="selftest: run the E2 robust locator on this graded case")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(run_selftest(args))
    if not (args.coarse and args.medium and args.fine and args.reference):
        refuse("need --coarse --medium --fine --reference (or --selftest)")
    sys.exit(run_grade(args))

if __name__ == "__main__":
    main()
