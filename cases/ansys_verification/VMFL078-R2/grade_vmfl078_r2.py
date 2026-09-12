#!/usr/bin/env python3
# =============================================================================
# VMFL078-R2 COMPARATOR -- 3-D lid-driven CUBIC cavity, Re = 1000, FULL CUBE.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, printed pp.223-224.
#
# Frozen by  cases/ansys_verification/VMFL078-R2/VMFL078_R2_PREREGISTRATION.md
# Graded run verification/runs/ansys_verification/VMFL078-R2/
#
# FOUR LIMBS, all verdict-bearing, none "diagnostic only":
#   A  Roache triple on J at the MID-SPAN line, r=2, Fs=1.25.  Criteria carried
#      UNCHANGED from the committed VMFL078 PREREGISTRATION.md sec.6.
#   B  Agreement with the manual's Figure .78.2 at the MID-SPAN plane z=0.50,
#      on the SAME 18 abscissae, SAME u_ref, SAME U95, SAME B1/B2/B3 thresholds
#      as the committed VMFL078_LIMB_B_PREREGISTRATION.md (freeze
#      98ba5a532e30ecee4e6da3a61be8a7dcf2e4a8dc).  NOTHING re-chosen.
#   C  The SAME gate at the QUARTER-SPAN plane z=0.25.  This is the hypothesis
#      test; its thresholds are B's, not new ones.
#   D  Symmetry fidelity of the full cube: |u(z=0.25) - u(z=0.75)|.  DEMOTE-ONLY.
#
# NO ARGUMENT OF THIS FILE CHANGES A THRESHOLD.  Every number that decides a
# verdict is a literal below, cross-checked against limbB_band_table.json.
#
# The file contains NO `assert` (verified by its own AST guard) so that every
# control is live under `python3 -O` as well (L-332).
# =============================================================================
import argparse, ast, copy, glob, json, math, os, re, shutil, sys, tempfile

BAND_TABLE_REL = "cases/ansys_verification/VMFL078/figure_78_2/limbB_band_table.json"
LIMB_B_FREEZE  = "98ba5a532e30ecee4e6da3a61be8a7dcf2e4a8dc"

# ---- THE FROZEN BAND.  Lifted verbatim from VMFL078_LIMB_B_PREREGISTRATION.md
#      sec.5.1.  probe_index, y, u_ref (m/s), U95 (m/s).  NOT re-digitised.
BAND = [
    (  9, 0.04955, -0.219074, 0.026956), ( 19, 0.09905, -0.268669, 0.015580),
    ( 29, 0.14855, -0.247146, 0.017144), ( 39, 0.19805, -0.201566, 0.021337),
    ( 49, 0.24755, -0.151656, 0.020292), ( 60, 0.30200, -0.105835, 0.018298),
    ( 70, 0.35150, -0.072230, 0.015797), ( 80, 0.40100, -0.049907, 0.015731),
    ( 90, 0.45050, -0.031800, 0.015849), (100, 0.50000, -0.014191, 0.015675),
    (110, 0.54950, -0.000797, 0.015691), (120, 0.59900, +0.017061, 0.015696),
    (130, 0.64850, +0.029707, 0.016547), (140, 0.69800, +0.048313, 0.015585),
    (151, 0.75245, +0.070635, 0.015744), (161, 0.80195, +0.095123, 0.018303),
    (171, 0.85145, +0.124209, 0.015896), (181, 0.90095, +0.163260, 0.021784),
]
U_RMS95   = 0.017917     # B1: RMS of the 18 U95 above
B2_MIN    = 16           # B2: at least 16 of 18 inside their own U95
B3_UMIN   = -0.2687      # B3: digitised extremum value ...
B3_UTOL   = 0.0156       #     ... and its tolerance
B3_YMIN   = 0.0985       # B3: y of the digitised extremum ...
B3_YTOL   = 0.0336       #     ... and its tolerance
B3_WINDOW = (0.05, 0.20)
# ---- Limb A, carried UNCHANGED from VMFL078 PREREGISTRATION.md sec.6 ---------
A_P_LO, A_P_HI, A_GCI_MAX, A_FS, A_R = 1.0, 3.0, 5.0, 1.25, 2.0
# ---- Limb D -----------------------------------------------------------------
D_MAX_ASYM = 0.005       # m/s, max |u(0.25) - u(0.75)| over the 18 abscissae
LEVELS  = ("F1", "F2", "F3")
NPROBE  = 201
PLANES  = {"midspan": ("midspanProbe", 0.50), "quarter": ("quarterProbe", 0.25),
           "quarter75": ("quarter75Probe", 0.75)}
PLANT   = 1.234e-03


class Refuse(Exception):
    """The comparator refuses; it never degrades (exit 2)."""


def one_match(pattern):
    hits = sorted(glob.glob(pattern))
    if len(hits) != 1:
        raise Refuse("expected exactly one match for %s, found %d: %s" % (pattern, len(hits), hits))
    return hits[0]


def numeric_time_dirs(root):
    out = []
    for d in os.listdir(root):
        p = os.path.join(root, d)
        if os.path.isdir(p) and re.fullmatch(r"[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?", d):
            out.append((float(d), p))
    out.sort(key=lambda t: t[0])        # NUMERIC, never lexicographic (950 vs 2000)
    return out


def read_probe(path):
    """Return (locations, last data row).  Refuses on shape, count, NaN/Inf."""
    locs, row = [], None
    with open(path, errors="replace") as fh:
        for line in fh:
            if line.startswith("#"):
                m = re.match(r"#\s+Probe\s+(\d+)\s+\(([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\)", line)
                if m:
                    locs.append((float(m.group(2)), float(m.group(3)), float(m.group(4))))
                continue
            vecs = re.findall(r"\(([^)]*)\)", line)
            if len(vecs) == len(locs) and len(vecs) > 0:
                row = [float(v.split()[0]) for v in vecs]
    if len(locs) != NPROBE:
        raise Refuse("%s declares %d probe locations, registered %d" % (path, len(locs), NPROBE))
    if row is None:
        raise Refuse("%s has no data row carrying %d vectors" % (path, NPROBE))
    for v in row:
        if math.isnan(v) or math.isinf(v):
            raise Refuse("%s holds a NaN or Inf" % path)
    return locs, row


def check_locations(locs, z_expect):
    """Every probe must sit at x=0.5, the registered z, and the registered y."""
    for i, (x, y, z) in enumerate(locs):
        if abs(x - 0.5) > 1e-9:
            raise Refuse("probe %d sits at x=%r, registered 0.5" % (i, x))
        if abs(z - z_expect) > 1e-9:
            raise Refuse("probe %d sits at z=%r, registered %r" % (i, z, z_expect))
    for idx, y_reg, _u, _U in BAND:
        if abs(locs[idx][1] - y_reg) > 1e-9:
            raise Refuse("frozen probe index %d sits at y=%r, registered %r" % (idx, locs[idx][1], y_reg))


def check_band_table(repo):
    """The band literals above must equal the committed machine copy, or refuse."""
    p = os.path.join(repo, BAND_TABLE_REL)
    if not os.path.exists(p):
        raise Refuse("band table %s is absent -- the gate is not reconstructible" % p)
    tab = json.load(open(p))
    if len(tab) != len(BAND):
        raise Refuse("band table has %d rows, comparator literals have %d" % (len(tab), len(BAND)))
    for row, (idx, y, u, U) in zip(tab, BAND):
        if (row["probe_index"] != idx or abs(row["y"] - y) > 1e-12
                or abs(row["u_ref_mps"] - u) > 1e-12 or abs(row["U95_mps"] - U) > 1e-12):
            raise Refuse("band table row %r disagrees with the comparator literal %r"
                         % (row, (idx, y, u, U)))
    rms95 = math.sqrt(sum(U * U for _i, _y, _u, U in BAND) / len(BAND))
    if abs(rms95 - U_RMS95) > 5e-7:
        raise Refuse("U_RMS95 literal %r is not the RMS of the band (%r)" % (U_RMS95, rms95))


def check_controldict(level_dir):
    """The cellPoint fix and the 201 abscissae must be in the file that RAN."""
    cd = os.path.join(level_dir, "system", "controlDict")
    if not os.path.exists(cd):
        raise Refuse("no system/controlDict in %s" % level_dir)
    txt = open(cd, errors="replace").read()
    for probe, _z in PLANES.values():
        blk = re.search(r"^    %s\s*$(.*?)^    \}" % probe, txt, re.S | re.M)
        if blk is None:
            raise Refuse("controlDict in %s carries no %s block" % (level_dir, probe))
        body = blk.group(1)
        if "interpolationScheme cellPoint" not in body:
            raise Refuse("the cellPoint order-pollution fix is MISSING from %s in %s"
                         % (probe, level_dir))
        n = len(re.findall(r"^            \(0\.5 ", body, re.M))
        if n != NPROBE:
            raise Refuse("%s in %s carries %d locations, registered %d"
                         % (probe, level_dir, n, NPROBE))


def check_bc_provenance(level_dir):
    """R2's whole point: there must be NO symmetry patch, and SIX walls."""
    b = os.path.join(level_dir, "constant", "polyMesh", "boundary")
    if not os.path.exists(b):
        raise Refuse("no constant/polyMesh/boundary in %s" % level_dir)
    txt = open(b, errors="replace").read()
    if "symmetryPlane" in txt or "symmetry" in txt:
        raise Refuse("the mesh in %s carries a symmetry patch -- R2 is the FULL CUBE "
                     "and the removal of the symmetry plane IS the experiment" % level_dir)
    for patch in ("lid", "floor", "sideXmin", "sideXmax", "wallZmin", "wallZmax"):
        if not re.search(r"^\s*%s\s*$" % patch, txt, re.M):
            raise Refuse("patch %s is absent from the mesh in %s" % (patch, level_dir))
    u0 = os.path.join(level_dir, "0", "U")
    if not os.path.exists(u0):
        raise Refuse("no 0/U in %s" % level_dir)
    ut = open(u0, errors="replace").read()
    if not re.search(r"lid\s*\{\s*type\s+fixedValue;\s*value\s+uniform\s*\(1 0 0\)", ut):
        raise Refuse("0/U in %s does not drive the lid at (1 0 0)" % level_dir)
    for w in ("floor", "sideXmin", "sideXmax", "wallZmin", "wallZmax"):
        if not re.search(r"%s\s*\{\s*type\s+noSlip" % w, ut):
            raise Refuse("0/U in %s does not set %s to noSlip" % (level_dir, w))


def strict_completion(run_root, level, level_dir):
    """Rule 4.  Returns an info dict; refuses on a physics-field failure."""
    rc_path = os.path.join(run_root, "RUN_RC.%s" % level)
    info = {"rc": None, "rc_measured": False}
    if os.path.exists(rc_path):                       # L-342: infrastructure, not physics
        txt = open(rc_path, errors="replace").read()
        m = re.search(r"^rc = (\S+)$", txt, re.M)
        if m:
            info["rc"], info["rc_measured"] = int(m.group(1)), True
        info["state"] = (re.search(r"^state = (\S+)$", txt, re.M) or [None, "unknown"])[1] \
            if re.search(r"^state = (\S+)$", txt, re.M) else "unknown"
        m = re.search(r"^core_min = (\S+)$", txt, re.M)
        info["core_min"] = float(m.group(1)) if m else None
    log = os.path.join(level_dir, "log.simpleFoam")
    if not os.path.exists(log):
        raise Refuse("no log.simpleFoam in %s" % level_dir)
    lt = open(log, errors="replace").read()
    info["End_lines"] = len(re.findall(r"^End$", lt, re.M))
    info["converged_lines"] = lt.count("SIMPLE solution converged")
    times = re.findall(r"^Time = (\S+)$", lt, re.M)
    info["last_time"] = times[-1] if times else None
    info["n_exec"] = len(re.findall(r"^ExecutionTime = ", lt, re.M))
    if info["End_lines"] < 1:
        raise Refuse("%s has no End line -- the run did not finish" % log)
    if info["converged_lines"] < 1:
        raise Refuse("%s never printed 'SIMPLE solution converged' -- the level stopped on "
                     "the endTime iteration ceiling, not on residualControl; rule 5 limb 1"
                     % log)
    tds = numeric_time_dirs(level_dir)
    if not tds:
        raise Refuse("no numeric time directory in %s" % level_dir)
    t_last, d_last = tds[-1]
    if info["last_time"] is None or abs(float(info["last_time"]) - t_last) > 1e-9:
        raise Refuse("last log time %r != latest time directory %r in %s"
                     % (info["last_time"], t_last, level_dir))
    info["latest_time_dir"] = d_last
    zero_u = os.path.join(level_dir, "0", "U")
    for f in ("U", "p", "phi"):
        fp = os.path.join(d_last, f)
        if not os.path.exists(fp):
            raise Refuse("field %s missing at %s" % (f, d_last))
        if os.path.getmtime(fp) <= os.path.getmtime(zero_u):        # THE AGE GUARD
            raise Refuse("AGE GUARD: %s is not NEWER than %s -- this answer predates the "
                         "run allowed to produce it" % (fp, zero_u))
    info["age_guard"] = "PASSED"
    return info


def j_functional(locs, row):
    """J = sqrt( (1/(y_hi-y_lo)) * int u^2 dy ), trapezoid over the 201 abscissae."""
    ys = [l[1] for l in locs]
    s = 0.0
    for i in range(len(ys) - 1):
        s += 0.5 * (row[i] ** 2 + row[i + 1] ** 2) * (ys[i + 1] - ys[i])
    return math.sqrt(s / (ys[-1] - ys[0]))


def roache(f1, f2, f3):
    """f1 coarse, f2 medium, f3 fine.  Returns (state, p, gci_fine_pct)."""
    d21, d32 = f2 - f1, f3 - f2
    if d21 == 0.0 or d32 == 0.0:
        return "EXACT", None, None
    ratio = d32 / d21
    if ratio < 0:
        return "OSCILLATORY", None, None
    if ratio >= 1.0:
        return "DIVERGENT", None, None
    if ratio > 1.0 / (A_R ** 0.5):        # change barely shrinking
        state = "STAGNANT"
    else:
        state = "CONVERGING"
    p = math.log(abs(d21 / d32)) / math.log(A_R)
    eps = abs(d32 / f3) if f3 != 0 else float("inf")
    gci = 100.0 * A_FS * eps / (A_R ** p - 1.0)
    return state, p, gci


def grade_plane(row, locs):
    """The FROZEN limb-B arithmetic.  Used unchanged for limb B and limb C."""
    pts, n_in, sq = [], 0, 0.0
    for idx, y, u_ref, U95 in BAND:
        u = row[idx]
        d = u - u_ref
        inside = abs(d) <= U95
        n_in += 1 if inside else 0
        sq += d * d
        pts.append({"probe_index": idx, "y": y, "u_ours": u, "u_ref": u_ref,
                    "delta": d, "U95": U95, "inside": inside})
    rms = math.sqrt(sq / len(BAND))
    lo, hi = B3_WINDOW
    win = [(locs[i][1], row[i]) for i in range(NPROBE) if lo <= locs[i][1] <= hi]
    y_min, u_min = min(win, key=lambda t: t[1])[0], min(v for _y, v in win)
    b1 = rms <= U_RMS95
    b2 = n_in >= B2_MIN
    b3 = abs(u_min - B3_UMIN) <= B3_UTOL and abs(y_min - B3_YMIN) <= B3_YTOL
    return {"rms_delta_mps": rms, "n_inside": n_in, "n_points": len(BAND),
            "u_min_ours_mps": u_min, "y_min_ours_m": y_min,
            "B1": b1, "B2": b2, "B3": b3,
            "verdict": "PASS" if (b1 and b2 and b3) else "GATE FAIL",
            "failed_gates": [g for g, ok in (("B1", b1), ("B2", b2), ("B3", b3)) if not ok],
            "points": pts}


def planted_zero_control(probe_path, locs):
    """Rule 3.  A zero from a reader not shown able to see a non-zero is not evidence.
    The plant is written into the REAL BYTES of a COPY.  The graded tree is never
    written to.  Three legs: P1a the reader SEES it; P1b it MOVES the gate
    functional; P1c a BLIND writer leaves the functional UNMOVED."""
    idx = BAND[9][0]
    base_locs, base_row = read_probe(probe_path)
    base = grade_plane(base_row, base_locs)["rms_delta_mps"]
    tmp = tempfile.mkdtemp(prefix="vmfl078r2_plant_")
    try:
        # --- P1a / P1b: a REAL plant, written into the copied bytes -------------
        dst = os.path.join(tmp, "U")
        txt = open(probe_path, errors="replace").read()
        lines = txt.split("\n")
        di = max(i for i, l in enumerate(lines)
                 if not l.startswith("#") and len(re.findall(r"\(([^)]*)\)", l)) == NPROBE)
        vecs = re.findall(r"\(([^)]*)\)", lines[di])
        parts = vecs[idx].split()
        planted = float(parts[0]) + PLANT
        vecs[idx] = " ".join([repr(planted)] + parts[1:])
        stamp = lines[di].split("(")[0]
        lines[di] = stamp + " ".join("(%s)" % v for v in vecs)
        open(dst, "w").write("\n".join(lines))
        p_locs, p_row = read_probe(dst)
        seen = p_row[idx] - base_row[idx]
        if abs(seen - PLANT) > 1e-9:
            raise Refuse("PLANTED-ZERO P1a FAILED: the gate reader saw %r at index %d, "
                         "planted %r -- this reader cannot see a non-zero and its zeros "
                         "are not evidence" % (seen, idx, PLANT))
        for i in range(NPROBE):
            if i != idx and abs(p_row[i] - base_row[i]) > 1e-12:
                raise Refuse("PLANTED-ZERO FAILED: the plant at index %d LEAKED to index %d"
                             % (idx, i))
        moved = grade_plane(p_row, p_locs)["rms_delta_mps"]
        if abs(moved - base) <= 1e-12:
            raise Refuse("PLANTED-ZERO P1b FAILED: a %r m/s plant did NOT move the gate "
                         "functional (%r -> %r) -- the gate is blind to the data it grades"
                         % (PLANT, base, moved))
        # --- P1c: a BLIND writer (touches nothing) must leave it UNMOVED --------
        blind = os.path.join(tmp, "U_blind")
        shutil.copyfile(probe_path, blind)
        b_locs, b_row = read_probe(blind)
        if abs(grade_plane(b_row, b_locs)["rms_delta_mps"] - base) > 1e-12:
            raise Refuse("PLANTED-ZERO P1c FAILED: an UNMODIFIED copy moved the functional "
                         "-- the reader is not deterministic")
        return {"status": "PASSED", "plant_mps": PLANT, "plant_index": idx,
                "functional_clean": base, "functional_planted": moved}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def ast_guard():
    n = sum(1 for node in ast.walk(ast.parse(open(os.path.abspath(__file__)).read()))
            if isinstance(node, ast.Assert))
    if n != 0:
        raise Refuse("AST guard: this file carries %d assert statements; `python3 -O` would "
                     "delete them and every control in them (L-332)" % n)
    return "AST guard: ast.Assert count is 0 in this file"


# =============================================================================
def grade(run_root, out_path, repo):
    ast_guard()
    check_band_table(repo)
    res = {"case": "VMFL078-R2",
           "title": "3-D lid-driven cubic cavity, Re=1000, FULL CUBE (no symmetry plane)",
           "manual": "VM2026R1 pp.223-224 (PDF 237-238), Figure .78.2",
           "limb_b_band_inherited_from": LIMB_B_FREEZE,
           "levels": {}, "run_root": run_root}
    planes = {k: {} for k in PLANES}
    for lvl in LEVELS:
        d = os.path.join(run_root, lvl)
        if not os.path.isdir(d):
            raise Refuse("level directory %s is absent -- three levels are registered" % d)
        check_controldict(d)
        check_bc_provenance(d)
        info = strict_completion(run_root, lvl, d)
        res["levels"][lvl] = info
        for name, (probe, z) in PLANES.items():
            p = one_match(os.path.join(d, "postProcessing", probe, "*", "U"))
            locs, row = read_probe(p)
            check_locations(locs, z)
            planes[name][lvl] = {"path": p, "locs": locs, "row": row, "J": j_functional(locs, row)}

    # ---- rule 3, on the level and plane that limb B grades ---------------------
    res["planted_zero_control"] = planted_zero_control(planes["midspan"]["F3"]["path"],
                                                       planes["midspan"]["F3"]["locs"])

    # ---- LIMB A: Roache triple on J at the mid-span line ----------------------
    J = [planes["midspan"][l]["J"] for l in LEVELS]
    state, p, gci = roache(*J)
    if state != "CONVERGING":
        a_verdict = "NOT A RESULT"
    elif A_P_LO <= p <= A_P_HI and gci <= A_GCI_MAX:
        a_verdict = "PASS"
    else:
        a_verdict = "GATE FAIL"
    res["limb_A"] = {"functional": "J = sqrt(mean over y of u_x^2) on x=0.5, z=0.50",
                     "J_F1": J[0], "J_F2": J[1], "J_F3": J[2], "triple": state,
                     "observed_order_p": p, "GCI_fine_pct": gci,
                     "criteria": {"p_band": [A_P_LO, A_P_HI], "GCI_max_pct": A_GCI_MAX,
                                  "Fs": A_FS, "r": A_R},
                     "verdict": a_verdict}

    # ---- LIMB B (mid-span, PRIMARY) and LIMB C (quarter-span, HYPOTHESIS) -----
    for limb, plane in (("limb_B", "midspan"), ("limb_C", "quarter")):
        g = grade_plane(planes[plane]["F3"]["row"], planes[plane]["F3"]["locs"])
        g["plane"] = plane
        g["z"] = PLANES[plane][1]
        g["graded_level"] = "F3"
        g["probe_file"] = planes[plane]["F3"]["path"]
        g["thresholds"] = {"U_RMS95": U_RMS95, "B2_min_inside": B2_MIN,
                           "B3_u_min": B3_UMIN, "B3_u_tol": B3_UTOL,
                           "B3_y_min": B3_YMIN, "B3_y_tol": B3_YTOL}
        g["trend_F1_F2"] = {l: grade_plane(planes[plane][l]["row"], planes[plane][l]["locs"])
                            ["n_inside"] for l in ("F1", "F2")}
        res[limb] = g

    # ---- LIMB D: symmetry fidelity of the full cube (DEMOTE-ONLY) -------------
    a = planes["quarter"]["F3"]["row"]
    b = planes["quarter75"]["F3"]["row"]
    worst, worst_y = 0.0, None
    for idx, y, _u, _U in BAND:
        e = abs(a[idx] - b[idx])
        if e > worst:
            worst, worst_y = e, y
    d_ok = worst <= D_MAX_ASYM
    res["limb_D"] = {"metric": "max over the 18 graded abscissae of |u(z=0.25) - u(z=0.75)|",
                     "max_asymmetry_mps": worst, "at_y": worst_y,
                     "threshold_mps": D_MAX_ASYM, "verdict": "PASS" if d_ok else "GATE FAIL",
                     "meaning": ("the full cube's own solution IS mirror-symmetric about its "
                                 "mid-span, so VMFL078's half-domain symmetryPlane model was "
                                 "admissible" if d_ok else
                                 "the full cube's solution is NOT mirror-symmetric: the "
                                 "half-domain model of VMFL078 was INVALID and every number "
                                 "from it is NOT A RESULT")}

    # ---- the row verdict, and rule 5's one-way demotion -----------------------
    if not d_ok or a_verdict == "NOT A RESULT":
        row = "NOT A RESULT"
    else:
        row = res["limb_B"]["verdict"]
    res["row_verdict"] = row
    res["hypothesis_readout"] = hypothesis_readout(res)
    res["cost_core_min"] = {l: res["levels"][l].get("core_min") for l in LEVELS}
    with open(out_path, "w") as fh:
        json.dump(res, fh, indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items()
                      if k not in ("limb_B", "limb_C", "levels")}, indent=1, default=str))
    for limb in ("limb_B", "limb_C"):
        s = res[limb]
        print("%s  plane=%s z=%.2f  n_inside=%d/%d  RMS=%.6f  B1=%s B2=%s B3=%s  -> %s"
              % (limb, s["plane"], s["z"], s["n_inside"], s["n_points"], s["rms_delta_mps"],
                 s["B1"], s["B2"], s["B3"], s["verdict"]))
    print("ROW VERDICT: %s" % row)
    return 0


def hypothesis_readout(res):
    """The four outcomes, WRITTEN INTO THE PRE-REGISTRATION BEFORE THE RUN.
    This function selects among them; it does not invent a fifth after the fact."""
    b, c = res["limb_B"]["verdict"], res["limb_C"]["verdict"]
    if res["limb_D"]["verdict"] == "GATE FAIL":
        return ("OUTCOME 4 -- the full cube is NOT mirror-symmetric.  VMFL078's half-domain "
                "symmetryPlane model was invalid and every VMFL078 number is NOT A RESULT.  "
                "Neither the sampling-plane hypothesis nor its alternative is tested by this run.")
    if b == "PASS":
        return ("OUTCOME 1 -- the SYMMETRY PLANE WAS THE DEFECT.  The full cube agrees with "
                "Figure .78.2 at the mid-span, where the half domain did not.  The "
                "sampling-plane hypothesis is FALSIFIED; R2 supersedes VMFL078.")
    if b == "GATE FAIL" and c == "PASS":
        return ("OUTCOME 2 -- HYPOTHESIS SUPPORTED.  Removing the symmetry plane did NOT move "
                "the mid-span answer into the band, and the SAME gate passes at the "
                "quarter-span plane z=0.25 -- the mid-plane of the manual's half domain.  "
                "Our solve stands; the discrepancy is the SAMPLING PLANE of Figure .78.2.")
    return ("OUTCOME 3 -- BOTH DEAD.  Neither the mid-span nor the quarter-span plane agrees "
            "with Figure .78.2.  The sampling-plane hypothesis is FALSIFIED and so is the "
            "symmetry-plane hypothesis.  The cause is elsewhere and this run does not name it.")


# =============================================================================
def selftest():
    """Drives every control against synthetic data.  No run tree is read."""
    npass = nfail = 0
    def ck(label, fn):
        nonlocal npass, nfail
        try:
            fn(); print("  [PASS] %s" % label); npass += 1
        except Exception as e:                              # noqa: BLE001
            print("  [FAIL] %s :: %r" % (label, e)); nfail += 1

    print(ast_guard())
    def must_refuse(fn, frag):
        try:
            fn()
        except Refuse as e:
            if frag not in str(e):
                raise Exception("refused with the wrong reason: %r" % (str(e),))
            return
        raise Exception("did NOT refuse")

    tmp = tempfile.mkdtemp(prefix="vmfl078r2_st_")
    try:
        ys = [0.005 + i * 0.00495 for i in range(NPROBE)]
        def write_probe(path, vals, z=0.5, x=0.5, n=NPROBE):
            L = ["# Probe %d (%r %r %r)" % (i, x, ys[i], z) for i in range(n)]
            L.append("#  Time")
            L.append("   1921 " + " ".join("(%r 0 0)" % vals[i] for i in range(n)))
            open(path, "w").write("\n".join(L) + "\n")
            return path
        exact = [0.0] * NPROBE
        for idx, y, u, _U in BAND:
            exact[idx] = u
        p_exact = write_probe(os.path.join(tmp, "exact"), exact)

        _two = os.path.join(tmp, "twodir")
        os.makedirs(_two, exist_ok=True)
        open(os.path.join(_two, "a"), "w").write("a")
        open(os.path.join(_two, "b"), "w").write("b")
        ck("one_match REFUSES on two matches",
           lambda: must_refuse(lambda: one_match(os.path.join(_two, "*")), "expected exactly one"))
        ck("time dirs sort NUMERICALLY, not lexicographically", lambda: (
            os.makedirs(os.path.join(tmp, "td", "950"), exist_ok=True),
            os.makedirs(os.path.join(tmp, "td", "2000"), exist_ok=True),
            (_ for _ in ()).throw(Exception("2000 did not sort last"))
            if numeric_time_dirs(os.path.join(tmp, "td"))[-1][0] != 2000.0 else None)[-1])
        ck("read_probe REFUSES a wrong probe count",
           lambda: must_refuse(lambda: read_probe(write_probe(os.path.join(tmp, "short"),
                                                              exact, n=200)), "declares 200"))
        ck("read_probe REFUSES a NaN", lambda: must_refuse(
            lambda: read_probe(write_probe(os.path.join(tmp, "nan"),
                                           [float("nan")] * NPROBE)), "NaN or Inf"))
        ck("check_locations REFUSES a probe off its registered z",
           lambda: must_refuse(lambda: check_locations(read_probe(p_exact)[0], 0.25),
                               "registered 0.25"))
        ck("the band literals ARE the committed band table",
           lambda: check_band_table(os.environ["VMFL078R2_REPO"]))
        ck("U_RMS95 literal is the RMS of the 18 U95", lambda: check_band_table(
            os.environ["VMFL078R2_REPO"]))
        ck("a curve ON the reference scores 18/18 and PASSES", lambda: (
            (_ for _ in ()).throw(Exception("exact curve did not PASS"))
            if grade_plane(read_probe(p_exact)[1], read_probe(p_exact)[0])["n_inside"] != 18
            else None))
        off = list(exact)
        for idx, _y, _u, U in BAND:
            off[idx] += 3.0 * U
        p_off = write_probe(os.path.join(tmp, "off"), off)
        ck("a curve 3*U95 off scores 0/18 and GATE FAILs", lambda: (
            (_ for _ in ()).throw(Exception("a 3-sigma-off curve did not GATE FAIL"))
            if grade_plane(read_probe(p_off)[1], read_probe(p_off)[0])["verdict"] != "GATE FAIL"
            else None))
        ck("B2 threshold is 16, not a count of what was measured", lambda: (
            (_ for _ in ()).throw(Exception("B2_MIN moved")) if B2_MIN != 16 else None))
        ck("planted zero P1a: the gate reader SEES a 1.234e-03 plant",
           lambda: planted_zero_control(p_exact, read_probe(p_exact)[0]))
        ck("planted zero P1b: the plant MOVES the GATE FUNCTIONAL", lambda: (
            (_ for _ in ()).throw(Exception("functional did not move"))
            if planted_zero_control(p_exact, read_probe(p_exact)[0])["functional_planted"] ==
            planted_zero_control(p_exact, read_probe(p_exact)[0])["functional_clean"] else None))
        ck("planted zero REFUSES against a BLIND reader", lambda: must_refuse(
            lambda: _blind_reader_probe(p_exact), "PLANTED-ZERO P1a FAILED"))
        ck("BC provenance REFUSES a mesh that still carries a SYMMETRY patch",
           lambda: must_refuse(lambda: check_bc_provenance(_fake_level(tmp, sym=True)),
                               "carries a symmetry patch"))
        ck("BC provenance REFUSES a lid that is not driven at (1 0 0)",
           lambda: must_refuse(lambda: check_bc_provenance(_fake_level(tmp, lid=False)),
                               "does not drive the lid"))
        ck("check_controldict REFUSES a controlDict with the cellPoint fix DELETED",
           lambda: must_refuse(lambda: check_controldict(_fake_level(tmp, cellpoint=False)),
                               "cellPoint order-pollution fix is MISSING"))
        ck("check_controldict REFUSES a controlDict missing a registered probe block",
           lambda: must_refuse(lambda: check_controldict(_fake_level(tmp, quarter=False)),
                               "carries no quarterProbe block"))
        ck("Roache: a monotone shrinking triple is CONVERGING with p=2", lambda: (
            (_ for _ in ()).throw(Exception("not CONVERGING p=2"))
            if roache(1.0, 1.4, 1.5)[0] != "CONVERGING" or abs(roache(1.0, 1.4, 1.5)[1] - 2.0) > 1e-9
            else None))
        ck("Roache: a sign-flipping triple is OSCILLATORY", lambda: (
            (_ for _ in ()).throw(Exception("not OSCILLATORY"))
            if roache(1.0, 1.4, 1.2)[0] != "OSCILLATORY" else None))
        ck("Roache: a growing triple is DIVERGENT", lambda: (
            (_ for _ in ()).throw(Exception("not DIVERGENT"))
            if roache(1.0, 1.1, 1.5)[0] != "DIVERGENT" else None))
        ck("Roache: three identical values are EXACT", lambda: (
            (_ for _ in ()).throw(Exception("not EXACT"))
            if roache(1.0, 1.0, 1.0)[0] != "EXACT" else None))
        ck("rule 5 is ONE-WAY: a failing limb D demotes a PASSING limb B", lambda: (
            (_ for _ in ()).throw(Exception("limb D did not demote"))
            if hypothesis_readout({"limb_B": {"verdict": "PASS"}, "limb_C": {"verdict": "PASS"},
                                   "limb_D": {"verdict": "GATE FAIL"}})[:9] != "OUTCOME 4"
            else None))
        ck("the FOUR outcomes are the four written in the registration, no fifth", lambda: (
            (_ for _ in ()).throw(Exception("outcome map drifted")) if not (
                hypothesis_readout({"limb_B": {"verdict": "PASS"}, "limb_C": {"verdict": "GATE FAIL"},
                                    "limb_D": {"verdict": "PASS"}})[:9] == "OUTCOME 1"
                and hypothesis_readout({"limb_B": {"verdict": "GATE FAIL"}, "limb_C": {"verdict": "PASS"},
                                        "limb_D": {"verdict": "PASS"}})[:9] == "OUTCOME 2"
                and hypothesis_readout({"limb_B": {"verdict": "GATE FAIL"}, "limb_C": {"verdict": "GATE FAIL"},
                                        "limb_D": {"verdict": "PASS"}})[:9] == "OUTCOME 3") else None))
        ck("strict completion REFUSES a level that never printed the converged line",
           lambda: must_refuse(lambda: strict_completion(tmp, "F9", _fake_run(tmp, conv=False)),
                               "never printed 'SIMPLE solution converged'"))
        ck("AGE GUARD catches an answer OLDER than the case",
           lambda: must_refuse(lambda: strict_completion(tmp, "F8", _fake_run(tmp, old=True)),
                               "AGE GUARD"))
        e2e = _fake_tree(tmp)
        outp = os.path.join(tmp, "e2e.json")
        ck("END-TO-END grade() runs and writes a JSON verdict",
           lambda: grade(e2e, outp, os.environ["VMFL078R2_REPO"]))
        ck("END-TO-END the row verdict is drawn ONLY from the rule-1 vocabulary", lambda: (
            (_ for _ in ()).throw(Exception("verdict outside the vocabulary"))
            if json.load(open(outp))["row_verdict"] not in
            ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
            else None))
        ck("END-TO-END grade() REFUSES when a registered level directory is absent",
           lambda: must_refuse(lambda: grade(os.path.join(tmp, "nosuchtree"), outp,
                                             os.environ["VMFL078R2_REPO"]),
                               "is absent -- three levels are registered"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("")
    if nfail:
        print("SELFTEST: %d FAILED, %d passed" % (nfail, npass)); return 1
    print("SELFTEST: all checks passed (%d)" % npass); return 0


def _blind_reader_probe(path):
    """A reader that returns the CLEAN row whatever the file says.  The control must
    catch it -- that is the whole point of rule 3."""
    global read_probe
    real = read_probe
    clean = real(path)
    try:
        read_probe = lambda _p, _c=clean: (list(_c[0]), list(_c[1]))
        return planted_zero_control(path, clean[0])
    finally:
        read_probe = real


def _fake_level(tmp, sym=False, lid=True, cellpoint=True, quarter=True):
    import uuid
    d = os.path.join(tmp, "lvl" + uuid.uuid4().hex[:8])
    os.makedirs(os.path.join(d, "constant", "polyMesh"), exist_ok=True)
    os.makedirs(os.path.join(d, "system"), exist_ok=True)
    os.makedirs(os.path.join(d, "0"), exist_ok=True)
    patches = ["lid", "floor", "sideXmin", "sideXmax", "wallZmin", "wallZmax"]
    body = "".join("    %s\n    {\n        type            %s;\n    }\n"
                   % (p, "symmetryPlane" if (sym and p == "wallZmax") else "wall")
                   for p in patches)
    open(os.path.join(d, "constant", "polyMesh", "boundary"), "w").write("6\n(\n%s)\n" % body)
    u = "boundaryField\n{\n"
    u += "    lid          { type fixedValue; value uniform (1 0 0); }\n" if lid else \
         "    lid          { type fixedValue; value uniform (2 0 0); }\n"
    for w in ("floor", "sideXmin", "sideXmax", "wallZmin", "wallZmax"):
        u += "    %s { type noSlip; }\n" % w
    open(os.path.join(d, "0", "U"), "w").write(u + "}\n")
    ys = [0.005 + i * 0.00495 for i in range(NPROBE)]
    cd = "functions\n{\n"
    for name, z in (("midspanProbe", 0.5), ("quarterProbe", 0.25), ("quarter75Probe", 0.75)):
        if name == "quarterProbe" and not quarter:
            continue
        cd += "    %s\n    {\n        type probes;\n" % name
        if cellpoint or name != "midspanProbe":
            cd += "        interpolationScheme cellPoint;\n"
        cd += "        probeLocations\n        (\n"
        cd += "".join("            (0.5 %r %r)\n" % (y, z) for y in ys)
        cd += "        );\n    }\n"
    open(os.path.join(d, "system", "controlDict"), "w").write(cd + "}\n")
    return d


def _fake_tree(tmp):
    """A complete, synthetic three-level run tree.  Its NUMBERS ARE ARBITRARY: this
    control exercises the grade() PATH, not any physical claim."""
    import time, uuid
    root = os.path.join(tmp, "tree" + uuid.uuid4().hex[:8])
    ys = [0.005 + i * 0.00495 for i in range(NPROBE)]
    for k, lvl in enumerate(LEVELS):
        d = _fake_level(tmp)
        dst = os.path.join(root, lvl)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(d, dst)
        os.makedirs(os.path.join(dst, "100"), exist_ok=True)
        open(os.path.join(dst, "log.simpleFoam"), "w").write(
            "Time = 100\nExecutionTime = 1 s\nSIMPLE solution converged in 100 iterations\nEnd\n")
        past = time.time() - 3600
        os.utime(os.path.join(dst, "0", "U"), (past, past))
        for f in ("U", "p", "phi"):
            open(os.path.join(dst, "100", f), "w").write("x\n")
        for name, z in (("midspanProbe", 0.5), ("quarterProbe", 0.25), ("quarter75Probe", 0.75)):
            pd = os.path.join(dst, "postProcessing", name, "0")
            os.makedirs(pd, exist_ok=True)
            vals = [0.0] * NPROBE
            for idx, y, u, _U in BAND:
                vals[idx] = u + (0.002 * (k + 1) if name == "midspanProbe" else 0.0)
            L = ["# Probe %d (%r %r %r)" % (i, 0.5, ys[i], z) for i in range(NPROBE)]
            L.append("#  Time")
            L.append("   100 " + " ".join("(%r 0 0)" % v for v in vals))
            open(os.path.join(pd, "U"), "w").write("\n".join(L) + "\n")
        open(os.path.join(root, "RUN_RC.%s" % lvl), "w").write(
            "rc = 0\nstate = FINISHED\ncore_min = 1.0\n")
    return root


def _fake_run(tmp, conv=True, old=False):
    import time, uuid
    d = os.path.join(tmp, "run" + uuid.uuid4().hex[:8])
    os.makedirs(os.path.join(d, "0"), exist_ok=True)
    os.makedirs(os.path.join(d, "100"), exist_ok=True)
    open(os.path.join(d, "log.simpleFoam"), "w").write(
        "Time = 100\nExecutionTime = 1 s\n%sEnd\n"
        % ("SIMPLE solution converged in 100 iterations\n" if conv else ""))
    for f in ("U", "p", "phi"):
        open(os.path.join(d, "100", f), "w").write("x\n")
    open(os.path.join(d, "0", "U"), "w").write("x\n")
    if old:
        future = time.time() + 3600
        os.utime(os.path.join(d, "0", "U"), (future, future))
    else:
        past = time.time() - 3600
        os.utime(os.path.join(d, "0", "U"), (past, past))
    return d


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root")
    ap.add_argument("--out")
    ap.add_argument("--repo", default="/home/ubuntu/Certonomous")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        os.environ["VMFL078R2_REPO"] = a.repo
        sys.exit(selftest())
    if not a.run_root or not a.out:
        print("usage: --run-root <dir> --out <json>  |  --selftest"); sys.exit(64)
    try:
        sys.exit(grade(a.run_root, a.out, a.repo))
    except Refuse as e:
        print("REFUSED (exit 2): %s" % e); sys.exit(2)
