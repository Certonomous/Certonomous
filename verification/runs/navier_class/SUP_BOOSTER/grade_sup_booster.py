#!/usr/bin/env python3
"""grade_sup_booster.py -- EXACT-tier grader for Navier-class Case-3 (SUP_BOOSTER), the
Taylor-Maccoll supersonic sharp cone.  Grades the CFD against the REGENERATED TM reference
(taylor_maccoll_reference.py); no external PDF.

WHAT IT GRADES (both against the frozen TM reference JSON):
  * Gate C1  -- cone-surface pressure coefficient Cp_cone (the primary EXACT gate);
  * Gate C2  -- conical shock angle beta (secondary), by a density-gradient locator fitted
                through the apex.
  Both are decided ONLY through the Roache triple over the (coarse, medium, fine) grids:
  a non-CONVERGING triple is NOT A RESULT whatever the value (rule 5); a CONVERGING triple
  is PASS inside the pre-registered band else GATE FAIL, with the Celik Fs=1.25 GCI printed.

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
BETA_BAND_DEG   = 1.0        # Gate C2: |beta_cfd - beta_ref| <= 1.0 deg
FS_CELIK        = 1.25       # Roache/Celik factor of safety
PLATEAU_TOL     = 0.005      # rule-5 clause-1: |dCp| between last two writes must be < this (else not iteratively converged)
TIP_TRIM        = 0.10       # drop the apex-most 10% of cone faces (conical singularity)
OUTLET_TRIM     = 0.05       # drop the outlet-most 5% of cone faces (outflow buffer)
GAMMA           = 1.4
P_INF           = 101325.0
M_INF           = 2.0
# shock-locator x-stations as fractions of cone length, in the self-similar mid region
SHOCK_STATIONS  = [0.35, 0.45, 0.55, 0.65, 0.75, 0.85]

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
    """Density-gradient shock locator: at each x-station find the radius of max |d rho/dr|,
    then least-squares fit r_s = m*x + b and REQUIRE the fit to pass near the apex.
    Cx/Cy may be passed in to avoid recomputing cell centres."""
    if Cx is None or Cy is None:
        Cx, Cy = cell_centres(case, time)
    rho = parse_internal_scalar(os.path.join(case, str(time), "rho"))
    if rho is None:
        refuse(f"{case}/{time}/rho uniform -- no shock to locate")
    if not (len(Cx) == len(Cy) == len(rho)):
        refuse(f"{case}/{time}: Cx/Cy/rho length mismatch")
    L = max(Cx)                     # cone length ~ max x
    xs, rs = [], []
    for frac in SHOCK_STATIONS:
        x0 = frac * L
        band = [i for i in range(len(Cx)) if abs(Cx[i] - x0) < 0.03 * L and Cy[i] > 0]
        if len(band) < 5:
            continue
        band.sort(key=lambda i: Cy[i])
        best_g, best_r = -1.0, None
        for j in range(1, len(band)):
            a, b = band[j-1], band[j]
            dr = Cy[b] - Cy[a]
            if dr <= 0:
                continue
            g = abs(rho[b] - rho[a]) / dr
            if g > best_g:
                best_g, best_r = g, 0.5 * (Cy[a] + Cy[b])
        if best_r is not None:
            xs.append(x0); rs.append(best_r)
    if len(xs) < 3:
        refuse(f"{case}/{time}: shock locator found < 3 usable stations")
    n = len(xs); sx = sum(xs); sr = sum(rs)
    sxx = sum(x*x for x in xs); sxr = sum(x*r for x, r in zip(xs, rs))
    m = (n*sxr - sx*sr) / (n*sxx - sx*sx)
    b = (sr - m*sx) / n
    if abs(b) > 0.05 * L:
        refuse(f"{case}/{time}: shock fit intercept {b:.4f} not near apex (>5% L) -- not a conical shock line")
    return math.degrees(math.atan(m)), dict(stations_x=xs, stations_r=rs, slope=m, intercept=b)

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
    gate_b = grade_gate("C2 shock angle beta", per["fine"]["beta_deg"], per["medium"]["beta_deg"],
                        per["coarse"]["beta_deg"], h["fine"], h["medium"], h["coarse"], beta_ref, BETA_BAND_DEG, "deg")
    report = dict(planted_zero_control=ctrl, per_level=per, grid=dict(nCells=nc, h=h,
                  r_medium_fine=r_fm, r_coarse_medium=r_cm), gates=[gate_cp, gate_b], reference=ref)
    print(json.dumps(report, indent=2))
    if args.report:
        json.dump(report, open(args.report, "w"), indent=2)
    verdicts = [gate_cp["verdict"], gate_b["verdict"]]
    return 0 if all(v in ("PASS", "GATE FAIL", "NOT A RESULT") for v in verdicts) else 70

def run_selftest(args):
    print("== Roache logic on a synthetic CONVERGING triple ==")
    g = grade_gate("selftest", 0.2025, 0.2050, 0.2100, 1.0, 1.5, 2.25, 0.20225, CP_BAND, "-")
    assert g["triple"] == "CONVERGING", g
    assert g["verdict"] == "PASS", g
    print(f"  CONVERGING, p={g['apparent_order_p']:.3f}, GCI={g['gci_fine']:.3e}, verdict={g['verdict']}")
    print("== Roache logic on a synthetic OSCILLATORY triple (must be NOT A RESULT) ==")
    g2 = grade_gate("selftest2", 0.20, 0.22, 0.19, 1.0, 1.5, 2.25, 0.20225, CP_BAND, "-")
    assert g2["verdict"] == "NOT A RESULT", g2
    print(f"  {g2['triple']} -> {g2['verdict']}")
    print("== Roache logic on a synthetic CONVERGING-but-OUTSIDE-band triple (must be GATE FAIL) ==")
    g3 = grade_gate("selftest3", 0.250, 0.253, 0.259, 1.0, 1.5, 2.25, 0.20225, CP_BAND, "-")
    assert g3["triple"] == "CONVERGING", g3
    assert g3["verdict"] == "GATE FAIL", g3
    print(f"  CONVERGING, dev={g3['deviation']:.4f} > band {CP_BAND} -> {g3['verdict']}")
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
    print("SELFTEST OK")
    return 0

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--coarse"); ap.add_argument("--medium"); ap.add_argument("--fine")
    ap.add_argument("--reference"); ap.add_argument("--report")
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--smoke")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(run_selftest(args))
    if not (args.coarse and args.medium and args.fine and args.reference):
        refuse("need --coarse --medium --fine --reference (or --selftest)")
    sys.exit(run_grade(args))

if __name__ == "__main__":
    main()
