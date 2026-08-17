#!/usr/bin/env python3
"""analyse_k0c.py -- grade the F14 K0c laminar rung against its specification.

    python3 analyse_k0c.py            # writes gate_k0c.json next to this file

Exit 0 = every graded row passed.  Exit 1 = at least one graded row failed.
Exit 2 = the analyser refused to grade (a control misbehaved, a case did not
converge, or the reference table could not be read from the specification).

THE REFERENCE VALUES ARE READ FROM THE SPECIFICATION, NOT TYPED IN HERE
----------------------------------------------------------------------
`REF_TABLE` below is empty at import.  It is filled by parsing Section 1.3 of

    docs/campaigns/F14-cooling-ladder/K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md

and the pass bands are parsed from Section 1.4 of the same file.  Nothing in
this script carries a benchmark number of its own.  Figures passed on without
their source are this lab's most repeated failure; a comparator that holds its
own copy of the reference is exactly that failure in code.  If the spec is
edited, this script grades against the edit, and if it cannot parse the spec it
exits 2 rather than fall back to anything.

The values so obtained are tier SECONDARY: read in Han and Xie (2019) Table 3,
attributed there to de Vahl Davis (1983), which is paywalled and was not read.
The spec says so and this script does not upgrade the tier.

WHAT IS GRADED, ON WHICH MESH
-----------------------------
Gate Section 1.4: deviation is evaluated ON THE FINE MESH of a two-mesh pair
with refinement factor >= 1.5 in each direction, coarse solved first, both
reported.  The coarse value is carried in every row of the output and a rung
result is never quoted without it.

WALL NUSSELT: TWO ESTIMATORS, AND WHICH ONE GRADES, DECLARED IN ADVANCE
----------------------------------------------------------------------
Both estimators are built from the RAW T CELL VALUES and the wall boundary
value.  Neither reads `grad(T)` back from disk.  That matters: this repo has a
measured 37 percent error from doing exactly that (scripts/heat_balance.py,
TRAP note) -- a `grad(T)` field written out and read back has lost the scheme's
snGrad wall correction on the boundary.

  Nu_2pt(y) = (T_wall - T_1) / (h/2) * L/dT
      The solver's own discrete wall flux on this orthogonal uniform mesh:
      `corrected` snGrad reduces to `uncorrected` when the face normal and the
      cell-centre line are parallel, which blockMesh guarantees here.  This is
      the flux that appears in the discrete energy balance.

  Nu_3pt(y) = (8 T_wall - 9 T_1 + T_2) / (3h) * L/dT
      One-sided quadratic through the wall value and the first two cell centres
      at h/2 and 3h/2; second-order accurate in h at the wall.

  DECLARED IN ADVANCE, and registered alongside CONTROL_PREDICTIONS.txt: the
  GRADED estimator is Nu_2pt.  It is the conservative one, it is the one the
  energy-balance row is about, and it needs no assumption beyond the mesh being
  orthogonal.  Nu_3pt is reported in every row as a discretisation sensitivity.
  Choosing between them after seeing which one passes would not be a gate.

THREE INDEPENDENT PATHS TO THE SAME NUMBER, AND WHICH TWO ARE THE CROSS-CHECK
-----------------------------------------------------------------------------
  1. Nu_2pt, from the raw T field written by the solver (this script).
  2. The `hotFlux`/`coldFlux` function objects, which the RUNNING SOLVER
     evaluated in-pass and printed into log.buoyantBoussinesqSimpleFoam, so
     they carry the scheme's snGrad correction from the solver's own code path.
  3. scripts/heat_balance.py, the standing check for this lab, which recomputes
     the same in-pass integral in watts through postProcess.

Path 1 against path 3 is the cross-check the snGrad trap demands, and it is
required to agree to better than 1e-6 relative or this script exits 2.  Path 2
is NOT used for that comparison: its function objects fire every 50 iterations,
so its last sample is up to 49 iterations older than the written field, and on
Ra1e3_m64 that offset alone read as 0.011 percent -- a sampling artefact that
would have been charged to the discretisation.  Path 2's job is the convergence
history and the in-log witness of each plant, where the offset does not matter.

CONVERGENCE IS A STATEMENT ABOUT THE GRADED QUANTITY, AND IT CAUGHT SOMETHING
-----------------------------------------------------------------------------
K0b ran 4000 iterations, never met its own residualControl, and its residuals
plateaued at ~1e-7.  A plateau is not a criterion.  Here the pass condition is
that Nu_avg, as printed by the running solver every 50 iterations, has a
PEAK-TO-PEAK SPREAD below 0.02 percent -- one fiftieth of the tightest band on
the gate -- over the last 400 outer iterations.  A case that fails that is
refused, not graded.

The spread is gated rather than the difference between the two endpoints
because Ra1e6_m192 approaches steady state as a decaying oscillation whose
period is about 400 outer iterations, the same length as the window, so an
endpoint test can be read at a phase where the ends agree while the quantity is
still swinging by ten times the band between them.  The spread cannot be
aliased that way and is never smaller than the endpoint difference; both are
reported.

It refused four of them.  Under K0b's relaxation factors every coarse mesh met
the criterion and every fine mesh missed it by two to three orders of magnitude
(2.19 / 3.98 / 4.67 percent, and 14.65 percent on the g=0 control), because an
under-relaxed SIMPLE outer loop moves the smooth modes at a rate that falls off
like 1/N^2.  Had the criterion been "the residuals stopped moving", all eight
meshes would have been graded and the Ra=1e3 pair would have reported a FINE
mesh further from the benchmark than its own COARSE mesh -- iteration error
masquerading as a mesh-convergence result.  Every case was therefore continued
from latestTime under accelerated factors (continue_cases.sh), and both logs
travel with the case.

CONTROLS
--------
Predictions were registered in CONTROL_PREDICTIONS.txt before any control
result was read; that file is reproduced into the JSON output so the prediction
and the outcome travel together.  C1, C2 and C3 are solved twins; C4 is a
comparator mutation and costs no compute; C5 was added after the convergence
refusal above and asks whether changing the relaxation factors changed the
answer rather than only the path to it.  Each control's KIND -- reachability or
recognition -- is recorded with its result.
"""

import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "..", "K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
HEAT_BALANCE = os.path.join(REPO, "scripts", "heat_balance.py")
FOAM_BASHRC = os.environ.get("FOAM_BASHRC",
                             "/usr/lib/openfoam/openfoam2606/etc/bashrc")

# physics, mirrored from build_cases.py and re-derived from each case's own
# dictionaries below so a mismatch is caught rather than inherited
L = 0.10
LZ = 0.01
GMAG = 9.81

GRADED_PAIRS = [
    (1e3, "Ra1e3_m32", "Ra1e3_m64"),
    (1e4, "Ra1e4_m40", "Ra1e4_m80"),
    (1e5, "Ra1e5_m64", "Ra1e5_m128"),
    (1e6, "Ra1e6_m128", "Ra1e6_m192"),
]
CONTROL_CASES = ["C1_Ra1e5_m128_g0", "C2_Ra1e5_m128_dT110", "C3_Ra1e5_m64_source"]


# ---------------------------------------------------------------------------
# the specification: reference values and pass bands
# ---------------------------------------------------------------------------

def read_spec():
    """Parse Section 1.3's reference table and Section 1.4's pass bands."""
    if not os.path.isfile(SPEC):
        raise SystemExit(f"REFUSE: gate specification not found at {SPEC}")
    txt = open(SPEC).read()

    ref = {}
    # rows of the form: | 1e3 | 3.649 | 3.697 | 1.118 | 1.505 | 0.692 |
    for m in re.finditer(
            r"^\|\s*(1e[3-6])\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*"
            r"([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*$", txt, re.M):
        ref[float(m.group(1))] = dict(
            u1max=float(m.group(2)), u2max=float(m.group(3)),
            Nu_avg=float(m.group(4)), Nu_max=float(m.group(5)),
            Nu_min=float(m.group(6)))
    if sorted(ref) != [1e3, 1e4, 1e5, 1e6]:
        raise SystemExit(
            "REFUSE: could not read the Section 1.3 reference table from the "
            f"specification; parsed Ra keys {sorted(ref)}. Nothing is graded "
            "against a value this script supplies itself.")

    # Bands, from the Section 1.4 table: | quantity | Ra scope | rule | why |
    # The rule cell cannot be matched as "text without a pipe": the energy row's
    # rule is literally `|Nu_hot - Nu_cold| / Nu_avg <= 0.5 percent`, absolute
    # value bars and all.  So only the first two cells are cut out and the whole
    # remainder of the line is searched for the FIRST `<= X percent`.  Rows in
    # other sections that survive the first two cuts carry no Ra scope and drop
    # out below.
    bands = {}
    for m in re.finditer(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|(.*)$", txt, re.M):
        quantities, scope, rule = m.group(1), m.group(2), m.group(3)
        v = re.search(r"<=\s*([\d.]+)\s*percent", rule)
        if not v:
            continue
        pct = float(v.group(1))
        if scope.strip() == "all":
            ras = [1e3, 1e4, 1e5, 1e6]
        else:
            ras = [float(x) for x in re.findall(r"1e[3-6]", scope)]
            if not ras:
                continue
        for q in [x.strip() for x in quantities.split(",")]:
            key = {"Energy balance": "energy_balance"}.get(q, q)
            for ra in ras:
                bands[(key, ra)] = pct

    needed = [("Nu_avg", r) for r in (1e3, 1e4, 1e5, 1e6)] \
        + [("Nu_max", r) for r in (1e3, 1e4, 1e5, 1e6)] \
        + [("Nu_min", r) for r in (1e3, 1e4, 1e5, 1e6)] \
        + [("u1max", r) for r in (1e3, 1e4, 1e5, 1e6)] \
        + [("u2max", r) for r in (1e3, 1e4, 1e5, 1e6)] \
        + [("energy_balance", r) for r in (1e3, 1e4, 1e5, 1e6)]
    missing = [k for k in needed if k not in bands]
    if missing:
        raise SystemExit(
            f"REFUSE: pass bands missing from the specification for {missing}. "
            "This script does not supply a band of its own.")
    return ref, bands


# ---------------------------------------------------------------------------
# OpenFOAM field reading
# ---------------------------------------------------------------------------

def foam(case, args):
    cmd = f'. "{FOAM_BASHRC}" >/dev/null 2>&1 && cd {case!r} && {args}'
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)


def read_internal(path):
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<(\w+)>\s*\n?\s*(\d+)\s*\n\((.*?)\n\)\s*;",
                  txt, re.S)
    if not m:
        u = re.search(r"internalField\s+uniform\s+([^;]+);", txt)
        if u:
            v = u.group(1).strip()
            if v.startswith("("):
                return ("uniform_vector", tuple(float(x) for x in v.strip("()").split()))
            return ("uniform_scalar", float(v))
        raise SystemExit(f"REFUSE: cannot parse internalField in {path}")
    kind, n, body = m.group(1), int(m.group(2)), m.group(3)
    nums = [float(x) for x in
            re.findall(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", body)]
    if kind == "vector":
        return [tuple(nums[3 * i:3 * i + 3]) for i in range(n)]
    return nums


def latest_time(case):
    ts = []
    for e in os.listdir(case):
        if os.path.isdir(os.path.join(case, e)):
            try:
                ts.append((float(e), e))
            except ValueError:
                pass
    if not ts:
        raise SystemExit(f"REFUSE: no time directories in {case}")
    return sorted(ts)[-1][1]


def cell_centres(case, t):
    r = foam(case, f"postProcess -func writeCellCentres -time {t} > log.cellCentres 2>&1")
    if r.returncode != 0:
        raise SystemExit(f"REFUSE: writeCellCentres failed in {case}")
    cx = read_internal(os.path.join(case, t, "Cx"))
    cy = read_internal(os.path.join(case, t, "Cy"))
    for f in ("C", "Cx", "Cy", "Cz"):
        try:
            os.remove(os.path.join(case, t, f))
        except OSError:
            pass
    return cx, cy


def read_case_scalar(case, rel, key):
    txt = open(os.path.join(case, rel)).read()
    m = re.search(rf"^\s*{re.escape(key)}\s+([^;]+);", txt, re.M)
    if not m:
        raise SystemExit(f"REFUSE: '{key}' not found in {case}/{rel}")
    return float(m.group(1).strip())


# ---------------------------------------------------------------------------
# the solver's own log: the in-pass Nusselt history and the imposed dT
# ---------------------------------------------------------------------------

LOG_FLUX = re.compile(r"areaNormalIntegrate\((\w+)\) of k0cGradT = ([\d.eE+-]+)")
LOG_TAVG = re.compile(r"areaAverage\((\w+)\) of T = ([\d.eE+-]+)")


def log_series(case):
    """The whole solve history, stage 1 then stage 2, as one continuous series.

    Every case here ran in two stages: stage 1 under K0b's relaxation factors
    and stage 2 continued from latestTime under accelerated ones (see
    continue_cases.sh for the measurement that forced it).  Both logs travel,
    both are read, and the series is continuous because stage 2 restarts from
    the field stage 1 left.
    """
    paths = [os.path.join(case, "log.buoyantBoussinesqSimpleFoam")]
    for stage in ("stage2", "stage3"):
        lp = os.path.join(case, f"log.buoyantBoussinesqSimpleFoam.{stage}")
        if os.path.isfile(lp):
            paths.append(lp)
    flux = {"hotWall": [], "coldWall": []}
    tavg = {"hotWall": [], "coldWall": []}
    fvoptions_lines = []
    n_ux = n_ux_zero = 0
    stage_bounds = []
    T_res_final = None
    residual_control_met = False
    for path in paths:
        start = len(flux["hotWall"])
        with open(path) as fh:
            for line in fh:
                m = LOG_FLUX.search(line)
                if m:
                    flux[m.group(1)].append(float(m.group(2)))
                    continue
                m = LOG_TAVG.search(line)
                if m:
                    tavg[m.group(1)].append(float(m.group(2)))
                    continue
                if "heatPlant" in line or "scalarSemiImplicitSource" in line:
                    fvoptions_lines.append(line.rstrip())
                m = re.search(r"Solving for Ux, Initial residual = ([\d.eE+-]+)", line)
                if m:
                    n_ux += 1
                    if float(m.group(1)) == 0.0:
                        n_ux_zero += 1
                    continue
                m = re.search(r"Solving for T, Initial residual = ([\d.eE+-]+)", line)
                if m:
                    T_res_final = float(m.group(1))
                if "solution converged" in line:
                    residual_control_met = True
        stage_bounds.append((os.path.basename(path), start,
                             len(flux["hotWall"])))
    return dict(flux=flux, tavg=tavg, fvoptions_log_lines=fvoptions_lines,
                n_Ux_solves=n_ux, n_Ux_zero_residual=n_ux_zero,
                momentum_identically_zero=(n_ux > 0 and n_ux_zero == n_ux),
                stages=stage_bounds, T_initial_residual_final=T_res_final,
                residual_control_met=residual_control_met)


# ---------------------------------------------------------------------------
# per-case measurement
# ---------------------------------------------------------------------------

def measure(name):
    case = os.path.join(HERE, name)
    t = latest_time(case)

    nu = read_case_scalar(case, "constant/transportProperties", "nu")
    Pr = read_case_scalar(case, "constant/transportProperties", "Pr")
    beta = read_case_scalar(case, "constant/transportProperties", "beta")
    alpha = nu / Pr

    gtxt = open(os.path.join(case, "constant", "g")).read()
    gy = float(re.search(r"value\s*\(\s*\S+\s+(\S+)", gtxt).group(1))
    gmag = abs(gy)

    # The wall temperatures are read from the field AT THE ANALYSED TIME, not
    # from 0.orig, because that is the boundary condition the solver actually
    # applied.  These are not always the same number.  Stage 1 wrote its restart
    # file at writePrecision 10, which truncated the intended hot-wall value
    # 300.005440811 to 300.0054408, and stage 2 restarted from that file -- so
    # from stage 2 onward the solver held a dT 1.1e-8 K below the intended one.
    # Physically that is a 1e-6 relative shift in Ra and matters to nothing.
    # Numerically it is the entire 5.78e-5 disagreement that was showing up in
    # the snGrad cross-check at Ra = 1e3, because the raw-cell estimator
    # subtracts the wall value from a cell value: 32 faces x 640 1/m x 1.1e-8 K
    # x 3.125e-5 m^2 = 7.0e-9, against an integral of 1.218e-4, is 5.78e-5
    # exactly.  Reading the wall value the solver held removes the artefact at
    # its source instead of budgeting for it in a tolerance.
    Torig = open(os.path.join(case, "0.orig", "T")).read()
    Th_intended = float(re.search(r"hotWall.*?value\s+uniform\s+([\d.eE+-]+)",
                                  Torig, re.S).group(1))
    Tc_intended = float(re.search(r"coldWall.*?value\s+uniform\s+([\d.eE+-]+)",
                                  Torig, re.S).group(1))
    Tnow = open(os.path.join(case, t, "T")).read()
    Th = float(re.search(r"hotWall.*?value\s+uniform\s+([\d.eE+-]+)",
                         Tnow, re.S).group(1))
    Tc = float(re.search(r"coldWall.*?value\s+uniform\s+([\d.eE+-]+)",
                         Tnow, re.S).group(1))
    dT = Th - Tc
    dT_intended = Th_intended - Tc_intended
    if abs(dT - dT_intended) > 1e-5 * dT_intended:
        raise SystemExit(
            f"REFUSE: {name}: the wall dT the solver held at t={t} is {dT} but "
            f"0.orig asked for {dT_intended}; that is more than a write-precision "
            "truncation and means the case is not the case it was built as")

    log = log_series(case)

    # ---- in-log witness: the dT the RUNNING solver actually used -------------
    if not log["tavg"]["hotWall"]:
        raise SystemExit(f"REFUSE: {name} log carries no wall-temperature "
                         "function-object output; the plant cannot be witnessed")
    dT_log = log["tavg"]["hotWall"][-1] - log["tavg"]["coldWall"][-1]
    if abs(dT_log - dT) > 1e-6 * max(1.0, dT):
        raise SystemExit(f"REFUSE: {name}: dT in 0.orig/T is {dT} but the solver "
                         f"reports {dT_log}")
    Ra_log = (gmag * beta * dT_log * L ** 3 / (nu * alpha)) if gmag > 0 else 0.0

    # ---- convergence, on the graded quantity --------------------------------
    A = L * LZ
    # The criterion is a fixed 400-iteration window (8 samples at interval 50),
    # not a fraction of the run: "Nu_avg has not moved by more than 0.02 percent
    # over the last 400 outer iterations" is a statement about the graded
    # quantity that means the same thing whatever the run length, whereas a
    # last-quarter window silently loosens as a run is extended.
    hist = [v / A * L / dT for v in log["flux"]["hotWall"]]
    if len(hist) < 9:
        raise SystemExit(f"REFUSE: {name}: only {len(hist)} Nusselt samples in the log")
    window = hist[-9:]
    conv_drift_pct = 100.0 * abs(hist[-1] - hist[-9]) / abs(hist[-1])
    # The endpoint difference alone is not enough, and Ra1e6_m192 is why.  Its
    # approach to steady state is a DECAYING OSCILLATION with a period of about
    # 400 outer iterations -- the same length as this window -- so an endpoint
    # test can be read at a phase where the two ends happen to agree while the
    # quantity is still swinging by ten times the band between them.  The
    # peak-to-peak spread over the same window cannot be aliased that way, it
    # is never smaller than the endpoint difference, and it is what the case is
    # actually gated on.
    conv_spread_pct = 100.0 * (max(window) - min(window)) / abs(hist[-1])
    conv_drift_lastquarter_pct = (
        100.0 * abs(hist[-1] - hist[int(0.75 * (len(hist) - 1))]) / abs(hist[-1]))
    Nu_avg_log_hot = hist[-1]
    Nu_avg_log_cold = -log["flux"]["coldWall"][-1] / A * L / dT

    # ---- raw-cell fields ----------------------------------------------------
    cx, cy = cell_centres(case, t)
    T = read_internal(os.path.join(case, t, "T"))
    U = read_internal(os.path.join(case, t, "U"))
    if isinstance(U, tuple):                      # uniform (0 0 0): the g=0 twin
        U = [U[1]] * len(T)
    n = len(T)
    xs = sorted(set(round(v, 9) for v in cx))
    ys = sorted(set(round(v, 9) for v in cy))
    nx, ny = len(xs), len(ys)
    xi = {v: i for i, v in enumerate(xs)}
    yi = {v: i for i, v in enumerate(ys)}
    gT = [[None] * nx for _ in range(ny)]
    gu = [[None] * nx for _ in range(ny)]
    gv = [[None] * nx for _ in range(ny)]
    for c in range(n):
        i, j = xi[round(cx[c], 9)], yi[round(cy[c], 9)]
        gT[j][i] = T[c]
        gu[j][i] = U[c][0]
        gv[j][i] = U[c][1]

    h = L / nx
    scale = L / dT

    # ---- wall Nusselt from RAW T CELLS, two estimators ----------------------
    nu_hot_2 = [(Th - gT[j][0]) / (0.5 * h) * scale for j in range(ny)]
    nu_hot_3 = [(8 * Th - 9 * gT[j][0] + gT[j][1]) / (3 * h) * scale for j in range(ny)]
    nu_cold_2 = [(gT[j][nx - 1] - Tc) / (0.5 * h) * scale for j in range(ny)]
    nu_cold_3 = [(-8 * Tc + 9 * gT[j][nx - 1] - gT[j][nx - 2]) / (3 * h) * scale
                 for j in range(ny)]
    mean = lambda a: sum(a) / len(a)

    # ---- the snGrad cross-check --------------------------------------------
    # path 1 (raw cells, here) against path 2 (in-pass, from the solver's log)
    # The cross-check is path 1 against path 3, NOT against the solver's log.
    # The log's function objects fire every 50 iterations, so the last logged
    # sample is up to 49 iterations older than the field that was written at the
    # end of the run; on Ra1e3_m64 that offset alone showed up as 0.011 percent
    # and would have made a sampling artefact look like a discretisation
    # disagreement.  scripts/heat_balance.py recomputes the same in-pass snGrad
    # integral through postProcess on the SAME written field, so the comparison
    # carries no time offset and the tolerance can be what it should be: 1e-6.
    # This is the check that catches the 37 percent snGrad trap.
    rc_hb, hb = heat_balance(name, 0.5)
    if hb is None:
        raise SystemExit(f"REFUSE: {name}: heat_balance.py produced no JSON "
                         f"(exit {rc_hb}); see audit/{name}.report.txt")
    k_cond = hb["properties"]["k_derived"]
    Q_hot = [q for q in hb["patches"] if q["patch"] == "hotWall"][0]
    Q_cold = [q for q in hb["patches"] if q["patch"] == "coldWall"][0]
    A_hot = Q_hot["area"]
    Nu_hb_hot = Q_hot["Q_in_W"] * L / (k_cond * dT * A_hot)
    Nu_hb_cold = -Q_cold["Q_in_W"] * L / (k_cond * dT * Q_cold["area"])

    xcheck = abs(mean(nu_hot_2) - Nu_hb_hot) / abs(Nu_hb_hot)
    if xcheck > 1e-6:
        raise SystemExit(
            f"REFUSE: {name}: the raw-cell wall flux ({mean(nu_hot_2):.9f}) and "
            f"scripts/heat_balance.py's in-pass snGrad integral "
            f"({Nu_hb_hot:.9f}) differ by {100*xcheck:.4f} percent. On an "
            "orthogonal uniform mesh these are the same discrete quantity; a "
            "disagreement means one of the two paths is not what it claims to be.")

    # ---- velocity extrema on the mid-planes ---------------------------------
    jm, im = ny // 2, nx // 2
    v_mid = [0.5 * (gv[jm - 1][i] + gv[jm][i]) for i in range(nx)]
    u_mid = [0.5 * (gu[j][im - 1] + gu[j][im]) for j in range(ny)]
    star = L / alpha
    u1max = max(u_mid) * star
    u2max = max(v_mid) * star

    # ---- core stratification.  MEASURED, NOT GRADED. ------------------------
    # Gate Section 1.4: "Core stratification, laminar rung: reference NOT
    # OBTAINED."  No number below is compared to anything.
    Tcol = [0.5 * (gT[j][im - 1] + gT[j][im]) for j in range(ny)]
    dy = L / ny
    S_cd = ((Tcol[jm] - Tcol[jm - 1]) / dy) * scale
    lo, hi = int(0.375 * ny), int(0.625 * ny)
    ysub = [(j + 0.5) * dy / L for j in range(lo, hi)]
    tsub = [(Tcol[j] - Tc) / dT for j in range(lo, hi)]
    mY, mT = mean(ysub), mean(tsub)
    S_fit = (sum((a - b) * (c - d) for a, b, c, d
                 in zip(ysub, [mY] * len(ysub), tsub, [mT] * len(tsub)))
             / sum((a - mY) ** 2 for a in ysub))

    return dict(
        case=name, time=t, mesh=[nx, ny],
        nu=nu, Pr=Pr, beta=beta, alpha=alpha, g=gmag,
        T_hot=Th, T_cold=Tc, dT_K=dT,
        dT_intended_K=dT_intended,
        dT_write_truncation_K=dT - dT_intended,
        dT_from_solver_log_K=dT_log, Ra_from_solver_log=Ra_log,
        beta_dT=beta * dT,
        Nu_avg=mean(nu_hot_2), Nu_max=max(nu_hot_2), Nu_min=min(nu_hot_2),
        Nu_avg_3pt=mean(nu_hot_3), Nu_max_3pt=max(nu_hot_3),
        Nu_min_3pt=min(nu_hot_3),
        Nu_avg_cold=mean(nu_cold_2), Nu_avg_cold_3pt=mean(nu_cold_3),
        Nu_avg_inpass_hot_lastlog=Nu_avg_log_hot,
        Nu_avg_inpass_cold_lastlog=Nu_avg_log_cold,
        Nu_avg_heat_balance_hot=Nu_hb_hot, Nu_avg_heat_balance_cold=Nu_hb_cold,
        raw_cell_vs_inpass_rel=xcheck,
        heat_balance_exit=rc_hb,
        heat_balance_imbalance_pct=hb["imbalance_pct"],
        heat_balance_Q_hot_W=Q_hot["Q_in_W"],
        heat_balance_Q_net_W=hb["Q_net_W"],
        heat_balance_k_W_per_mK=k_cond,
        boussinesq_ok=hb["boussinesq_ok"],
        energy_balance_pct=(100.0 * abs(Nu_hb_hot - Nu_hb_cold)
                            / (0.5 * abs(Nu_hb_hot + Nu_hb_cold))),
        u1max=u1max, u2max=u2max,
        Umax_ms=max(abs(x) for row in gu for x in row) if ny else 0.0,
        stratification_S_leastsq_mid25pct_UNGRADED=S_fit,
        stratification_S_central_difference_UNGRADED=S_cd,
        convergence_drift_pct=conv_drift_pct,
        convergence_spread_pct=conv_spread_pct,
        convergence_drift_lastquarter_pct=conv_drift_lastquarter_pct,
        T_initial_residual_final=log["T_initial_residual_final"],
        residual_control_met=log["residual_control_met"],
        solver_log_stages=log["stages"],
        n_log_samples=len(hist),
        momentum_identically_zero=log["momentum_identically_zero"],
        fvoptions_log_lines=log["fvoptions_log_lines"],
        wall_clock_s=cost_of(case),
    )


def cost_of(case):
    """Total single-core seconds for this case: stage 1 plus stage 2 plus 3.

    Reading only `wall_clock_s` would under-report every case, because stage 2
    is where most of the fine meshes' iterations were actually spent. A cost
    line that quietly omits the expensive half is worse than no cost line.
    """
    p = os.path.join(case, "COST.txt")
    if not os.path.isfile(p):
        return None
    txt = open(p).read()
    tot, seen = 0.0, False
    for key in ("wall_clock_s", "stage2_wall_clock_s", "stage3_wall_clock_s"):
        m = re.search(rf"^{key}\s+(\S+)", txt, re.M)
        if m:
            tot += float(m.group(1))
            seen = True
    return tot if seen else None


# ---------------------------------------------------------------------------
# scripts/heat_balance.py -- the standing check
# ---------------------------------------------------------------------------

def heat_balance(name, tol):
    case = os.path.join(HERE, name)
    out = os.path.join(HERE, "audit", f"{name}.json")
    rep = os.path.join(HERE, "audit", f"{name}.report.txt")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p = subprocess.run(
        [sys.executable, HEAT_BALANCE, case, "--tol", str(tol),
         "--length", str(L), "--json", out],
        capture_output=True, text=True)
    with open(rep, "w") as fh:
        fh.write(f"$ python3 scripts/heat_balance.py {name} --tol {tol} "
                 f"--length {L}\nexit status {p.returncode}\n\n"
                 + p.stdout + ("\n" + p.stderr if p.stderr else ""))
    return p.returncode, (json.load(open(out)) if os.path.isfile(out) else None)


# ---------------------------------------------------------------------------
# grading
# ---------------------------------------------------------------------------

def rel(q, ref):
    return 100.0 * abs(q - ref) / abs(ref)


def grade(fine, ra, ref, bands):
    """Rows for one Ra.  `fine` is the measurement dict of the FINE mesh."""
    rows = []
    for q in ("Nu_avg", "Nu_max", "Nu_min", "u1max", "u2max"):
        d = rel(fine[q], ref[ra][q])
        band = bands[(q, ra)]
        rows.append(dict(quantity=q, Ra=ra, reference=ref[ra][q],
                         solved=fine[q], deviation_pct=d, band_pct=band,
                         passed=bool(d <= band)))
    d = fine["energy_balance_pct"]
    band = bands[("energy_balance", ra)]
    rows.append(dict(quantity="energy_balance", Ra=ra, reference=0.0,
                     solved=d, deviation_pct=d, band_pct=band,
                     passed=bool(d <= band)))
    return rows


def mutate_check(fine, ra, ref, bands):
    """C4: perturb each solved value past its own band; that row and only that
    row must flip to FAIL."""
    base = grade(fine, ra, ref, bands)
    out = []
    for i, row in enumerate(base):
        q = row["quantity"]
        if q == "energy_balance":
            m = dict(fine, energy_balance_pct=bands[(q, ra)] * 1.5 + 1e-9)
        else:
            # push AWAY from the reference, so the perturbation cannot
            # accidentally walk a value that sits on the far side of the
            # reference back towards it
            sgn = 1.0 if fine[q] >= ref[ra][q] else -1.0
            m = dict(fine)
            m[q] = fine[q] * (1.0 + sgn * 1.5 * bands[(q, ra)] / 100.0)
        mg = grade(m, ra, ref, bands)
        flipped = [r["quantity"] for a, r in zip(base, mg)
                   if a["passed"] != r["passed"]]
        out.append(dict(Ra=ra, perturbed=q,
                        perturbation="band x1.5",
                        rows_that_changed=flipped,
                        row_flipped_to_fail=bool(
                            flipped == [q] and not mg[i]["passed"]),
                        base_row_passed=row["passed"]))
    return out


def main():
    ref, bands = read_spec()
    res = dict(
        gate_specification=os.path.relpath(os.path.abspath(SPEC), REPO),
        reference_tier="SECONDARY (Han and Xie 2019 Table 3, attributed to de "
                       "Vahl Davis 1983, which is paywalled and was not read)",
        reference_table_parsed_from_spec=ref,
        pass_bands_parsed_from_spec={f"{k[0]}@{k[1]:.0e}": v
                                     for k, v in sorted(bands.items(),
                                                        key=lambda x: str(x[0]))},
        graded_estimator="Nu_2pt (solver-consistent snGrad from raw T cells); "
                         "declared before the run, see this file's docstring",
        cases={}, gate_rows=[], controls={}, mutation_C4=[],
        stratification_UNGRADED={}, cost={})

    # ---- measure every case -------------------------------------------------
    order = [c for _, a, b in GRADED_PAIRS for c in (a, b)] + CONTROL_CASES
    for name in order:
        res["cases"][name] = measure(name)

    # ---- convergence gate ---------------------------------------------------
    # The refusal applies to the GRADED cases. A control twin is refused only
    # if it fails the spread criterion AND never met its own residualControl.
    # C3 is why: its planted source makes the hot-wall flux a near-cancellation
    # of two much larger numbers, so a solution that reached residualControl in
    # 352 iterations still shows 0.12 percent of relative wobble in a quantity
    # whose absolute wobble is tiny. Refusing it would be refusing the wrong
    # thing, and it grades nothing in any case.
    graded_case_names = {c for _, a, b in GRADED_PAIRS for c in (a, b)}
    bad = {}
    for n, c in res["cases"].items():
        if c["convergence_spread_pct"] <= 0.02:
            continue
        if n in graded_case_names or not c["residual_control_met"]:
            bad[n] = c["convergence_spread_pct"]
    res["convergence"] = {
        n: dict(spread_pct=c["convergence_spread_pct"],
                endpoint_drift_pct=c["convergence_drift_pct"],
                residual_control_met=c["residual_control_met"],
                graded=bool(n in graded_case_names))
        for n, c in res["cases"].items()}
    res["convergence_criterion"] = (
        "Nu_avg, as printed by the running solver's own in-pass function "
        "object every 50 iterations, has a PEAK-TO-PEAK SPREAD below 0.02 "
        "percent over the last 400 outer iterations of the case. 0.02 percent "
        "is one fiftieth of the tightest band on this gate. A fixed iteration "
        "window is used rather than a fraction of the run because a "
        "last-quarter window silently loosens as a run is extended. The spread "
        "is gated rather than the endpoint difference because Ra1e6_m192 "
        "approaches steady state as a decaying oscillation of period about 400 "
        "iterations, and an endpoint test over a 400-iteration window can be "
        "aliased by exactly that.")
    if bad:
        res["convergence_refusals"] = bad

    # ---- the gate -----------------------------------------------------------
    for ra, coarse, fine in GRADED_PAIRS:
        c, f = res["cases"][coarse], res["cases"][fine]
        for row in grade(f, ra, ref, bands):
            q = row["quantity"]
            row["coarse_mesh"] = coarse
            row["fine_mesh"] = fine
            row["coarse_value"] = (c["energy_balance_pct"]
                                   if q == "energy_balance" else c[q])
            row["coarse_deviation_pct"] = (
                c["energy_balance_pct"] if q == "energy_balance"
                else rel(c[q], ref[ra][q]))
            if q in ("Nu_avg", "Nu_max", "Nu_min"):
                row["fine_value_3pt_estimator"] = f[q + "_3pt"]
                row["fine_deviation_pct_3pt"] = rel(f[q + "_3pt"], ref[ra][q])
            res["gate_rows"].append(row)
        res["mutation_C4"] += mutate_check(f, ra, ref, bands)
        res["stratification_UNGRADED"][f"Ra={ra:.0e}"] = dict(
            fine_mesh=fine,
            S_leastsq_mid25pct=f["stratification_S_leastsq_mid25pct_UNGRADED"],
            S_central_difference=f["stratification_S_central_difference_UNGRADED"],
            coarse_mesh=coarse,
            S_leastsq_mid25pct_coarse=c["stratification_S_leastsq_mid25pct_UNGRADED"],
            status="MEASURED, NOT GRADED. Gate Section 1.4: the laminar core "
                   "stratification reference was NOT OBTAINED (de Vahl Davis "
                   "1983 and Le Quere 1991 both paywalled). There is nothing "
                   "to compare this to and it is not permitted to grade "
                   "anything against a number this agent produced itself.")

    # scripts/heat_balance.py, the standing check, was run once per case inside
    # measure(): its exit status, imbalance and per-patch watts are already in
    # res["cases"][name], and its printed report is in audit/<case>.report.txt.

    # ---- controls -----------------------------------------------------------
    c1 = res["cases"]["C1_Ra1e5_m128_g0"]
    rows_c1 = grade(c1, 1e5, ref, bands)
    res["controls"]["C1_g0"] = dict(
        kind="RECOGNITION (gross wrong physics); also demonstrates "
             "REACHABILITY of the comparator's FAIL branch",
        plant="constant/g set to (0 0 0) on an exact twin of the Ra=1e5 fine case",
        in_log_witness=dict(
            momentum_identically_zero=c1["momentum_identically_zero"],
            wall_dT_unchanged_K=c1["dT_from_solver_log_K"],
            note="the plant is witnessed by the solver's own Ux residuals being "
                 "exactly zero at every one of its solves, and by the wall "
                 "temperatures it prints being unchanged from the graded case, "
                 "which is what separates this plant from C2's"),
        Nu_avg=c1["Nu_avg"], Nu_max=c1["Nu_max"], Nu_min=c1["Nu_min"],
        u1max=c1["u1max"], u2max=c1["u2max"],
        rows=rows_c1,
        all_Nu_rows_failed=bool(not any(
            r["passed"] for r in rows_c1 if r["quantity"].startswith("Nu_"))),
        deviation_Nu_avg_pct=rel(c1["Nu_avg"], ref[1e5]["Nu_avg"]))

    c2 = res["cases"]["C2_Ra1e5_m128_dT110"]
    fine1e5 = res["cases"]["Ra1e5_m128"]
    rows_c2 = grade(c2, 1e5, ref, bands)
    res["controls"]["C2_Ra_plus_10pct"] = dict(
        kind="RECOGNITION at the gate's own scale: does the 1.0 percent Nu_avg "
             "band resolve a 10 percent error in the Rayleigh number?",
        plant="dT multiplied by exactly 1.10, i.e. Ra = 1.10e5",
        in_log_witness=dict(
            wall_dT_graded_case_K=fine1e5["dT_from_solver_log_K"],
            wall_dT_control_case_K=c2["dT_from_solver_log_K"],
            ratio=c2["dT_from_solver_log_K"] / fine1e5["dT_from_solver_log_K"],
            Ra_from_solver_log=c2["Ra_from_solver_log"],
            note="both numbers are area-averages printed by the RUNNING solver "
                 "every 50 iterations into log.buoyantBoussinesqSimpleFoam; a "
                 "plant living only in 0.orig/T would not move them"),
        Nu_avg=c2["Nu_avg"],
        shift_vs_graded_case_pct=100.0 * (c2["Nu_avg"] - fine1e5["Nu_avg"])
        / fine1e5["Nu_avg"],
        deviation_vs_reference_pct=rel(c2["Nu_avg"], ref[1e5]["Nu_avg"]),
        Nu_avg_row_failed=bool(not rows_c2[0]["passed"]),
        rows=rows_c2)

    c3 = res["cases"]["C3_Ra1e5_m64_source"]
    rc3 = c3["heat_balance_exit"]
    planted_W = 5.000e-03
    recovered_W = c3["heat_balance_Q_net_W"]
    res["controls"]["C3_planted_source"] = dict(
        kind="REACHABILITY of the energy-balance row, plus a stated limit on "
             "what that row can ever prove",
        plant=f"uniform volumetric source of {planted_W:.3e} W via fvOptions "
              "scalarSemiImplicitSource on T",
        in_log_witness=dict(
            fvoptions_lines_in_solver_log=c3["fvoptions_log_lines"],
            constructed_by_solver=bool(c3["fvoptions_log_lines"]),
            note="the solver echoes fvOptions at construction; a source present "
                 "in constant/fvOptions but not constructed would leave the log "
                 "empty here"),
        planted_W=planted_W, recovered_net_W=recovered_W,
        recovery_error_pct=(100.0 * (abs(recovered_W) - planted_W) / planted_W
                            if recovered_W else None),
        heat_balance_exit=rc3,
        heat_balance_imbalance_pct=c3["heat_balance_imbalance_pct"],
        energy_balance_row_pct=c3["energy_balance_pct"],
        energy_balance_row_failed=bool(
            c3["energy_balance_pct"] > bands[("energy_balance", 1e5)]),
        limit_of_this_row=(
            "On a SEALED, impermeable, steady cavity with no source the boundary "
            "heat balance is very nearly an identity: the discrete T equation "
            "conserves at every iteration, converged or not (K0b C3, W-2). The "
            "energy-balance row of this gate therefore has teeth only against "
            "conservation defects such as this planted source, and NONE against "
            "the failure modes the rung actually faces -- wrong Ra, wrong Pr, "
            "under-resolved boundary layers. It is reported because the "
            "specification requires it, and it is not counted as evidence that "
            "the physics is right."))

    # C5: did the relaxation change move the answer, or only the path to it?
    # Every case that ALREADY met the convergence criterion under the stage-1
    # factors is a witness. Their stage-1 values were snapshotted to
    # stage1_values.json before stage 2 overwrote the fields.
    s1path = os.path.join(HERE, "stage1_values.json")
    c5 = dict(
        kind="RECOGNITION of a confound: the stage-2 relaxation factors are a "
             "property of the path to the fixed point, not of the fixed point. "
             "This control asks whether that is true here rather than asserting "
             "it.",
        criterion_pct=0.02,
        note="witnesses are the cases that ALREADY met the convergence "
             "criterion at the end of stage 1, so any movement in their Nu_avg "
             "across the relaxation change is a change to the answer and not "
             "the completion of a convergence that had not happened.",
        witnesses={})
    if os.path.isfile(s1path):
        s1 = json.load(open(s1path))
        for n, v in s1.items():
            if n not in res["cases"] or v["convergence_drift_pct"] > 0.02:
                continue
            after = res["cases"][n]["Nu_avg"]
            shift = 100.0 * abs(after - v["Nu_avg"]) / abs(after)
            c5["witnesses"][n] = dict(
                Nu_avg_stage1=v["Nu_avg"], Nu_avg_final=after,
                shift_pct=shift, passed=bool(shift <= 0.02))
        # Every case that is NOT a witness says so, with its reason. The loop
        # above iterates the snapshot, so a case absent from the snapshot drops
        # out of C5 silently -- and two of them do, for reasons that are sound
        # but were invisible here until they were looked for. A filter nobody
        # can see is a filter nobody can question, so the filter reports itself
        # and the arithmetic is made to balance: witnesses + excluded == cases.
        for n, c in res["cases"].items():
            if n in c5["witnesses"]:
                continue
            if n not in s1:
                why = ("absent from stage1_values.json: no stage-1 measurement "
                       "was snapshotted for this case. Not data loss -- see "
                       "README.md, 'The two cases missing from "
                       "stage1_values.json'. Its stage-1 figures remain "
                       "recoverable from its committed solver log.")
            else:
                why = (f"stage-1 drift was {s1[n]['convergence_drift_pct']:.5f} "
                       "percent, above the 0.02 percent criterion, so it had "
                       "not converged under the stage-1 factors and any later "
                       "movement would be convergence rather than a change of "
                       "answer")
            c5.setdefault("excluded_from_witnesses", {})[n] = why
        c5["cases_total"] = len(res["cases"])
        c5["witness_count"] = len(c5["witnesses"])
        c5["excluded_count"] = len(c5.get("excluded_from_witnesses", {}))
        c5["accounting_balances"] = bool(
            c5["witness_count"] + c5["excluded_count"] == c5["cases_total"])
        c5["all_witnesses_passed"] = bool(
            c5["witnesses"] and all(w["passed"] for w in c5["witnesses"].values()))
    else:
        c5["all_witnesses_passed"] = None
        c5["note"] += "  stage1_values.json is missing; C5 could not be run."
    res["controls"]["C5_relaxation_invariance"] = c5

    res["controls"]["C4_comparator_mutation"] = dict(
        kind="REACHABILITY of every band in the gate table, individually",
        method="each solved value perturbed by 1.5x its own band; that row and "
               "only that row must flip to FAIL",
        rows=res["mutation_C4"],
        every_row_reachable=bool(all(m["row_flipped_to_fail"]
                                     for m in res["mutation_C4"])))

    # ---- cost ---------------------------------------------------------------
    tot = 0.0
    for n, c in res["cases"].items():
        if c["wall_clock_s"]:
            res["cost"][n] = dict(wall_clock_s=c["wall_clock_s"], cores=1,
                                  core_minutes=c["wall_clock_s"] / 60.0)
            tot += c["wall_clock_s"]
    res["cost"]["TOTAL"] = dict(core_seconds=tot, core_minutes=tot / 60.0,
                                note="single-core solves, so core-minutes is "
                                     "the sum of the per-case wall clocks. No "
                                     "monetary figure: there is no verified "
                                     "rate for this machine.")

    res["control_predictions_registered"] = open(
        os.path.join(HERE, "CONTROL_PREDICTIONS.txt")).read()

    failed = [r for r in res["gate_rows"] if not r["passed"]]
    res["verdict"] = dict(
        rows_total=len(res["gate_rows"]),
        rows_failed=len(failed),
        failed_rows=[f"{r['quantity']}@Ra={r['Ra']:.0e}" for r in failed],
        gate="PASS" if not failed else "FAIL")

    with open(os.path.join(HERE, "gate_k0c.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    write_markdown(res)

    emit(res)
    if bad:
        return 2
    return 0 if not failed else 1


def write_markdown(r):
    """Emit GATE_TABLE.md: every number in it comes from gate_k0c.json.

    It exists so that the narrative results document never retypes a figure.
    Transcription is how a number loses its source in this lab, and a table a
    human copies by hand is a transcription waiting to happen.
    """
    o = []
    o.append("<!-- GENERATED by analyse_k0c.py. Do not hand-edit: rerun the "
             "script. Every number here comes from gate_k0c.json. -->\n")
    o.append("## Gate table, F14 rung K0c laminar\n")
    o.append(f"Reference tier: {r['reference_tier']}.  \n"
             f"Reference values and pass bands parsed at run time out of "
             f"`{r['gate_specification']}`.  \n"
             f"Graded estimator: {r['graded_estimator']}.  \n"
             "Deviation is REL = 100 x |solved - reference| / |reference|, "
             "graded on the FINE mesh; the coarse mesh of the mandatory pair "
             "is carried in every row.\n")
    o.append("| Ra | quantity | reference | coarse mesh | coarse dev % | "
             "FINE mesh | **FINE dev %** | band % | verdict | 3-pt estimator | "
             "3-pt dev % |")
    o.append("| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | "
             "---: | ---: |")
    for row in r["gate_rows"]:
        three = (f"{row['fine_value_3pt_estimator']:.4f} | "
                 f"{row['fine_deviation_pct_3pt']:.3f}"
                 if "fine_value_3pt_estimator" in row else "n/a | n/a")
        refv = ("n/a (a defect, not a target)" if row["quantity"] == "energy_balance"
                else f"{row['reference']:.4f}")
        o.append(f"| {row['Ra']:.0e} | {row['quantity']} | {refv} | "
                 f"{row['coarse_value']:.4f} | {row['coarse_deviation_pct']:.3f} | "
                 f"{row['solved']:.4f} | **{row['deviation_pct']:.3f}** | "
                 f"{row['band_pct']:.1f} | "
                 f"{'PASS' if row['passed'] else '**FAIL**'} | {three} |")
    v = r["verdict"]
    o.append(f"\n**GATE {v['gate']}** — {v['rows_failed']} of {v['rows_total']} "
             "graded rows failed"
             + (f": {', '.join(v['failed_rows'])}." if v["failed_rows"] else "."))

    o.append("\n## Convergence, on the graded quantity\n")
    o.append(f"Criterion: {r['convergence_criterion']}\n")
    o.append("| case | peak-to-peak spread over last 400 iterations, % | "
             "endpoint drift, % | residualControl met | final T initial "
             "residual | mesh | wall clock s |")
    o.append("| --- | ---: | ---: | :---: | ---: | ---: | ---: |")
    for n, c in r["cases"].items():
        o.append(f"| {n} | {c['convergence_spread_pct']:.6f} | "
                 f"{c['convergence_drift_pct']:.6f} | "
                 f"{'yes' if c['residual_control_met'] else 'no'} | "
                 f"{c['T_initial_residual_final']:.2e} | "
                 f"{c['mesh'][0]}x{c['mesh'][1]} | "
                 f"{c['wall_clock_s'] if c['wall_clock_s'] else 0:.1f} |")

    o.append("\n## The snGrad cross-check\n")
    o.append("Path 1 (wall flux built from the raw T cells, this script) "
             "against path 3 (`scripts/heat_balance.py`, which recomputes the "
             "in-pass snGrad integral through postProcess on the same written "
             "field). Reading `grad(T)` back from disk instead is wrong by 37 "
             "percent on this case class.\n")
    o.append("| case | relative difference | heat_balance.py exit | "
             "imbalance % | Q_hot W |")
    o.append("| --- | ---: | ---: | ---: | ---: |")
    for n, c in r["cases"].items():
        o.append(f"| {n} | {c['raw_cell_vs_inpass_rel']:.2e} | "
                 f"{c['heat_balance_exit']} | "
                 f"{c['heat_balance_imbalance_pct']:.5f} | "
                 f"{c['heat_balance_Q_hot_W']:.6e} |")

    o.append("\n## Core stratification — MEASURED, NOT GRADED\n")
    o.append("The gate records that the laminar core stratification reference "
             "was **NOT OBTAINED**: no read source tabulates it and both "
             "candidate primaries are paywalled. These are measurements. "
             "There is nothing to compare them against, and a rung must never "
             "pass against a number the executing agent produced itself.\n")
    o.append("| Ra | fine mesh | S (least squares, mid 25% of height) | "
             "S (central difference at the centre) | coarse mesh S | status |")
    o.append("| ---: | --- | ---: | ---: | ---: | --- |")
    for k, s in r["stratification_UNGRADED"].items():
        o.append(f"| {k.split('=')[1]} | {s['fine_mesh']} | "
                 f"{s['S_leastsq_mid25pct']:+.4f} | "
                 f"{s['S_central_difference']:+.4f} | "
                 f"{s['S_leastsq_mid25pct_coarse']:+.4f} | UNGRADED |")

    o.append("\n## Cost\n")
    o.append("| case | wall clock s | cores | core-minutes |")
    o.append("| --- | ---: | ---: | ---: |")
    for n, c in r["cost"].items():
        if n == "TOTAL":
            continue
        o.append(f"| {n} | {c['wall_clock_s']:.1f} | {c['cores']} | "
                 f"{c['core_minutes']:.3f} |")
    t = r["cost"]["TOTAL"]
    o.append(f"| **TOTAL** | {t['core_seconds']:.1f} | 1 | "
             f"**{t['core_minutes']:.3f}** |")
    o.append(f"\n{t['note']}\n")

    with open(os.path.join(HERE, "GATE_TABLE.md"), "w") as fh:
        fh.write("\n".join(o) + "\n")


def emit(r):
    p = print
    p("=" * 96)
    p("K0c LAMINAR GATE -- de Vahl Davis square cavity, F14 cooling ladder")
    p(f"reference: {r['reference_tier']}")
    p(f"spec:      {r['gate_specification']}")
    p("=" * 96)
    p(f"{'Ra':>6} {'quantity':<15}{'reference':>11}{'coarse':>11}{'FINE':>11}"
      f"{'dev %':>9}{'band %':>8}  {'':<4}{'3pt est.':>10}{'3pt dev%':>9}")
    for row in r["gate_rows"]:
        p(f"{row['Ra']:>6.0e} {row['quantity']:<15}{row['reference']:>11.4f}"
          f"{row['coarse_value']:>11.4f}{row['solved']:>11.4f}"
          f"{row['deviation_pct']:>9.3f}{row['band_pct']:>8.1f}  "
          f"{'PASS' if row['passed'] else 'FAIL':<4}"
          + (f"{row['fine_value_3pt_estimator']:>10.4f}"
             f"{row['fine_deviation_pct_3pt']:>9.3f}"
             if "fine_value_3pt_estimator" in row else ""))
    p("-" * 96)
    p("convergence of Nu_avg over the last 400 outer iterations "
      "(criterion: peak-to-peak spread < 0.02 %):")
    for k, v in r["convergence"].items():
        p(f"    {k:<26} spread {v['spread_pct']:>9.5f} %"
          f"   endpoint drift {v['endpoint_drift_pct']:>9.5f} %"
          f"   residualControl {'met' if v['residual_control_met'] else 'NOT met'}"
          f"   {'GRADED' if v['graded'] else 'control'}")
    p("-" * 96)
    p("raw-cell wall flux vs the solver's in-pass snGrad integral "
      "(the trap cross-check):")
    for k, c in r["cases"].items():
        p(f"    {k:<26} rel. difference {c['raw_cell_vs_inpass_rel']:.3e}")
    p("-" * 96)
    p("CORE STRATIFICATION -- MEASURED, NOT GRADED (reference NOT OBTAINED):")
    for k, s in r["stratification_UNGRADED"].items():
        p(f"    {k}  S(least squares, mid 25%) = {s['S_leastsq_mid25pct']:+.4f}"
          f"   S(central difference) = {s['S_central_difference']:+.4f}"
          f"   [coarse mesh: {s['S_leastsq_mid25pct_coarse']:+.4f}]")
    p("-" * 96)
    p("CONTROLS")
    for k, c in r["controls"].items():
        p(f"  {k}  --  {c['kind']}")
    p("-" * 96)
    v = r["verdict"]
    p(f"  GATE {v['gate']}: {v['rows_failed']} of {v['rows_total']} rows failed"
      + (f"  ({', '.join(v['failed_rows'])})" if v["failed_rows"] else ""))
    p(f"  cost: {r['cost']['TOTAL']['core_minutes']:.3f} core-minutes")
    p("=" * 96)


if __name__ == "__main__":
    sys.exit(main())
