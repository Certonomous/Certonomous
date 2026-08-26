#!/usr/bin/env python3
# =============================================================================
# VMFL076 -- Forced Convection Over a Flat Plate (Ansys VM2026R1 p.219).
# THE COMPARATOR.  Frozen at the pre-registration commit; the launcher re-proves
# on disk that this file IS the blob committed at HEAD before any solver starts.
#
# AMENDMENT 6 COMPLIANCE: there is NO `assert` in this file. Every refusal,
# guard, control and gate is an explicit `refuse(...)` -> sys.exit(2) or a
# `raise`, so `python3 -O` cannot strip it.
# AMENDMENT 6a COMPLIANCE: every control function ends in a fall-through
# refuse(...) on its not-caught path, so the ONLY way to return is to have
# passed; and no success line is printed outside a passing branch.
# =============================================================================
import glob
import math
import os
import re
import sys
import tempfile

# ----------------------------------------------------------------- vocabulary
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


def refuse(code, msg):
    sys.stdout.write("REFUSED[%s]: %s\n" % (code, msg))
    sys.stdout.flush()
    sys.exit(2)


def emit(verdict):
    # CLAUDE.md rule 1's enforcement point. Explicit, NOT an assert (Amendment 6).
    if verdict not in VERDICTS:
        refuse("V0", "verdict %r is outside the fixed vocabulary %r" % (verdict, VERDICTS))
    return verdict


# ------------------------------------------- THE MANUAL'S OWN INPUTS, p.219 --
RHO, MU, CP, K_COND = 900.0, 0.01, 42.6, 142.0
U_INF, T_INF, T_WALL, L_PLATE = 1.0, 300.0, 350.0, 1.0
NU = MU / RHO                      # 1/90000 m2/s
ALPHA = K_COND / (RHO * CP)        # 1/270  m2/s
PR = MU * CP / K_COND              # 0.003

# ------------------------------------------------------- THE FROZEN GATE ----
X_GATE = 0.75                      # m, a blockMesh FACE at every level
Y_LO, Y_HI, N_LINE = 0.0, 0.5, 201 # the fixed sample line
MIN_LINE_POINTS = 195
TOL_A = 0.03                       # Gate A: relative band on the profile integral
TOL_B = 0.010                      # Gate B: absolute band on max |dTheta|
RATIO = 2.0                        # grid refinement ratio
FS = 1.25                          # Roache factor of safety
PLATEAU_ITERS = 1000               # FIXED window, in SIMPLE iterations
PLATEAU_MIN_N = 12
PLATEAU_PP = 2.0e-4                # peak-to-peak / mean
PLATEAU_TREND = 1.0e-4             # |slope*window| / mean
PLANT_DT = 1.234                   # K, the planted perturbation (rule 3)

# classical constants used as CONTROLS on the ODE solver (not as the reference)
BLASIUS_FPP0 = 0.33205733621519630
BLASIUS_BETA = 1.7207876575
# THE LOAD-BEARING FINDING of the pre-freeze groundwork, locked into the
# instrument: the low-Pr SLUG/erfc shortcut sqrt(Pr/pi) is 4.9549 % away from
# the exact similarity solution and MUST NOT be the reference.
SLUG_GAP_PCT = 4.954869
SLUG_GAP_TOL = 0.01

_S0 = 30.0
_H = 1.0e-4


# =============================================================================
#  THE REFERENCE -- the Sparrow & Gregg similarity solution, EVALUATED here.
#  Blasius   f''' + (1/2) f f''   = 0,  f(0)=f'(0)=0, f'(inf)=1
#  Energy    th'' + (Pr/2) f th'  = 0,  th(0)=0, th(inf)=1
#  th(eta) = INT_0^eta exp(-(Pr/2) INT_0^s f) ds / INT_0^inf (same)
#  Head 0..30 by RK4 at h=1e-4; tail 30..inf ANALYTIC via math.erfc, because
#  f -> eta - beta there so INT f = (eta-beta)^2/2 + C exactly.
# =============================================================================
def _march(fpp0, s_end, h=_H, dense=False):
    F = f = fp = 0.0
    fpp = fpp0
    n = int(round(s_end / h))
    Fs = [0.0] if dense else None
    for _ in range(n):
        def d(F_, f_, fp_, fpp_):
            return (f_, fp_, fpp_, -0.5 * f_ * fpp_)
        k1 = d(F, f, fp, fpp)
        k2 = d(F + h / 2 * k1[0], f + h / 2 * k1[1], fp + h / 2 * k1[2], fpp + h / 2 * k1[3])
        k3 = d(F + h / 2 * k2[0], f + h / 2 * k2[1], fp + h / 2 * k2[2], fpp + h / 2 * k2[3])
        k4 = d(F + h * k3[0], f + h * k3[1], fp + h * k3[2], fpp + h * k3[3])
        F += h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        f += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        fp += h / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
        fpp += h / 6 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
        if dense:
            Fs.append(F)
    return F, f, fp, fpp, Fs


class Similarity(object):
    def __init__(self, pr=PR):
        lo, hi = 0.30, 0.35
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if _march(mid, 12.0, 1.0e-3)[2] < 1.0:
                lo = mid
            else:
                hi = mid
        self.fpp0 = 0.5 * (lo + hi)
        F0, f0, _, _, Fs = _march(self.fpp0, _S0, dense=True)
        self.beta = _S0 - f0
        self.pr = pr
        a = pr / 2.0
        self.a = a
        self.C = F0 - 0.5 * (_S0 - self.beta) ** 2
        self.SQ = math.sqrt(math.pi / (2.0 * a))
        cum = [0.0] * len(Fs)
        prev = math.exp(-a * Fs[0])
        acc = 0.0
        for i in range(1, len(Fs)):
            cur = math.exp(-a * Fs[i])
            acc += 0.5 * _H * (prev + cur)
            cum[i] = acc
            prev = cur
        self.cum = cum
        self.head = cum[-1]
        self.total = self.head + self._tail(_S0)
        self.thp0 = 1.0 / self.total

    def _tail(self, s):
        return math.exp(-self.a * self.C) * self.SQ * math.erfc((s - self.beta) * math.sqrt(self.a / 2.0))

    def theta(self, eta):
        if eta <= 0.0:
            return 0.0
        if eta < _S0:
            i = int(round(eta / _H))
            if i >= len(self.cum):
                i = len(self.cum) - 1
            return self.cum[i] / self.total
        return (self.head + (self._tail(_S0) - self._tail(eta))) / self.total

    def theta_excess(self, eta):
        """Theta = (T - T_inf)/(T_wall - T_inf) = 1 - theta.  1 at the wall, 0 far."""
        return 1.0 - self.theta(eta)


_SIM = None


def similarity():
    global _SIM
    if _SIM is None:
        _SIM = Similarity()
    return _SIM


# =============================================================================
#  THE ESTIMATOR -- reads the sampled gate line back OFF DISK.
# =============================================================================
def read_gate_line(path):
    """Return (ys, Ts) read from an OpenFOAM raw sampledSets file."""
    if not os.path.isfile(path):
        refuse("E1", "gate-line file does not exist: %s" % path)
    ys, ts = [], []
    fh = open(path, "r")
    try:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            if len(parts) < 2:
                refuse("E2", "gate-line row %r in %s has fewer than 2 columns" % (s, path))
            try:
                ys.append(float(parts[0]))
                ts.append(float(parts[-1]))
            except ValueError:
                refuse("E3", "gate-line row %r in %s is not numeric" % (s, path))
    finally:
        fh.close()
    if len(ys) < MIN_LINE_POINTS:
        refuse("E4", "gate line %s returned %d points, below the registered floor %d"
               % (path, len(ys), MIN_LINE_POINTS))
    grid = [Y_LO + (Y_HI - Y_LO) * i / (N_LINE - 1) for i in range(N_LINE)]
    for y in ys:
        if min(abs(y - g) for g in grid) > 1.0e-9:
            refuse("E5", "gate line %s carries y = %.12g, which is not one of the "
                         "registered %d fixed points" % (path, y, N_LINE))
    for i in range(1, len(ys)):
        if not (ys[i] > ys[i - 1]):
            refuse("E6", "gate line %s is not monotone in y at index %d" % (path, i))
    return ys, ts


def theta_profile(ts):
    """Normalised temperature excess Theta = (T - T_inf)/(T_wall - T_inf)."""
    return [(t - T_INF) / (T_WALL - T_INF) for t in ts]


def theta_integral(ys, ts):
    """THE GATE SCALAR: trapezoidal INT Theta dy over the fixed sample points [m]."""
    th = theta_profile(ts)
    tot = 0.0
    for i in range(1, len(ys)):
        tot += 0.5 * (ys[i] - ys[i - 1]) * (th[i] + th[i - 1])
    return tot


def reference_profile(ys, x=X_GATE):
    sc = math.sqrt(NU * x / U_INF)
    sim = similarity()
    return [sim.theta_excess(y / sc) for y in ys]


def reference_integral(ys, x=X_GATE):
    """The SAME discrete functional applied to the exact profile on the SAME
    points, so the quadrature error is identical on both sides and cancels."""
    th = reference_profile(ys, x)
    tot = 0.0
    for i in range(1, len(ys)):
        tot += 0.5 * (ys[i] - ys[i - 1]) * (th[i] + th[i - 1])
    return tot


def max_abs_profile_dev(ys, ts, x=X_GATE):
    lab = theta_profile(ts)
    ref = reference_profile(ys, x)
    best, besty = -1.0, None
    for i in range(len(ys)):
        d = abs(lab[i] - ref[i])
        if d > best:
            best, besty = d, ys[i]
    return best, besty


# =============================================================================
#  RULE 4 -- STRICT COMPLETION, with the age guard.
# =============================================================================
REQUIRED_FIELDS = ("T", "U", "p")


def _resolve(path):
    """Amendment 5 item 4: a field is X or X.gz."""
    if os.path.isfile(path):
        return path
    if os.path.isfile(path + ".gz"):
        return path + ".gz"
    return None


def _read_record(path):
    """Amendment 5 item 2: tolerant parse, DEFAULTING TO THE REFUSING VALUE."""
    d = {}
    if os.path.isfile(path):
        for line in open(path, "r"):
            m = re.match(r"(\w+)\s*=\s*(.*)", line.strip())
            if m:
                d[m.group(1)] = m.group(2).strip()
    return d


def completion_check(level_dir, end_time):
    rec = _read_record(os.path.join(level_dir, "RUN_RC.txt"))
    rc = rec.get("rc", "1")
    if rc != "0":
        refuse("C1", "%s: RUN_RC.txt reports rc = %s (default on an unparseable record "
                     "is the REFUSING value)" % (level_dir, rc))
    logs = glob.glob(os.path.join(level_dir, "log.simpleFoam"))
    if len(logs) != 1:
        refuse("C2", "%s: expected exactly one log.simpleFoam, found %d" % (level_dir, len(logs)))
    txt = open(logs[0], "r", errors="replace").read()
    if "\nEnd\n" not in txt and not txt.rstrip().endswith("End"):
        refuse("C3", "%s: the solver log carries no End line" % level_dir)
    times = re.findall(r"^Time = ([0-9.eE+-]+)\s*$", txt, flags=re.M)
    if not times:
        refuse("C4", "%s: the solver log carries no Time = lines" % level_dir)
    last = float(times[-1])
    if abs(last - end_time) > 1e-9:
        refuse("C5", "%s: last time %.12g != endTime %.12g" % (level_dir, last, end_time))
    nexec = len(re.findall(r"^ExecutionTime = ", txt, flags=re.M))
    if nexec != int(end_time):
        refuse("C6", "%s: ExecutionTime count %d != endTime %d" % (level_dir, nexec, int(end_time)))
    tdir = os.path.join(level_dir, str(int(end_time)))
    if not os.path.isdir(tdir):
        refuse("C7", "%s: no field directory at endTime %d" % (level_dir, int(end_time)))
    ref0 = _resolve(os.path.join(level_dir, "0", "T"))
    if ref0 is None:
        refuse("C8", "%s: the case's own 0/T is missing -- the age guard has no datum" % level_dir)
    t0 = os.path.getmtime(ref0)
    for f in REQUIRED_FIELDS:
        p = _resolve(os.path.join(tdir, f))
        if p is None:
            refuse("C9", "%s: required field %r is MISSING at endTime %d" % (level_dir, f, int(end_time)))
        if not (os.path.getmtime(p) > t0):
            refuse("C10", "AGE GUARD: %s at endTime is NOT newer than the case's own 0/T "
                          "-- it cannot have been produced by this run" % p)
    return True


# =============================================================================
#  AMENDMENT 4 -- the plateau / settling clause.
# =============================================================================
def plateau(times, values, end_time):
    # AMENDMENT 4 item 4, THE NULL-RANGE REFUSAL, applied where it discriminates.
    # A dead reader and a perfectly converged solve give the same null WINDOW, so
    # the null-range refusal is placed on the WHOLE SAMPLED SERIES: if the reader
    # saw no variation ANYWHERE across this run, it is refused. Having been shown
    # able to see this run's own motion, a null window is then convergence and is
    # recorded as such (n_distinct is printed beside it).
    if len(values) < 2:
        refuse("S0", "PLATEAU: fewer than two samples in the whole series")
    if max(values) == min(values):
        refuse("S2", "PLATEAU NULL RANGE: the estimator saw NO variation at all "
                     "across the whole sampled series (%d identical samples) -- a "
                     "dead series and a converged one look the same to a tolerance"
               % len(values))
    lo = end_time - PLATEAU_ITERS
    win = [(t, v) for t, v in zip(times, values) if t >= lo - 1e-9]
    n = len(win)
    if n < PLATEAU_MIN_N:
        refuse("S1", "PLATEAU CANNOT_TELL: only %d samples in the fixed window "
                     "[%g, %g], below the registered floor %d" % (n, lo, end_time, PLATEAU_MIN_N))
    vs = [v for _, v in win]
    lo_v, hi_v = min(vs), max(vs)
    mean = sum(vs) / n
    if mean == 0.0:
        refuse("S4", "PLATEAU: the window mean is exactly zero; a relative "
                     "settling statistic is undefined")
    pp = (hi_v - lo_v) / abs(mean)
    ts = [t for t, _ in win]
    tbar = sum(ts) / n
    vbar = mean
    num = sum((t - tbar) * (v - vbar) for t, v in win)
    den = sum((t - tbar) ** 2 for t in ts)
    if den == 0.0:
        refuse("S5", "PLATEAU: all samples in the window share one time stamp")
    slope = num / den
    trend = abs(slope * (max(ts) - min(ts))) / abs(mean)
    ok = (pp <= PLATEAU_PP) and (trend <= PLATEAU_TREND)
    return ok, n, pp, trend, len(set(vs))


# =============================================================================
#  RULE 5 -- Roache triple gating.
# =============================================================================
def roache(f1, f2, f3, ratio=RATIO, fs=FS):
    """f1 coarse, f2 medium, f3 fine."""
    e21 = f2 - f1
    e32 = f3 - f2
    if e21 == 0.0 and e32 == 0.0:
        return dict(cls="EXACT", p=None, gci=None, e21=e21, e32=e32, R=None)
    if e21 == 0.0:
        return dict(cls="DIVERGENT", p=None, gci=None, e21=e21, e32=e32, R=None)
    R = e32 / e21
    if R < 0.0:
        return dict(cls="OSCILLATORY", p=None, gci=None, e21=e21, e32=e32, R=R)
    if R >= 1.0:
        return dict(cls="DIVERGENT", p=None, gci=None, e21=e21, e32=e32, R=R)
    if R > 0.99:
        return dict(cls="STAGNANT", p=None, gci=None, e21=e21, e32=e32, R=R)
    p = math.log(abs(e21) / abs(e32)) / math.log(ratio)
    gci = fs * abs(e32 / f3) / (ratio ** p - 1.0)
    return dict(cls="CONVERGING", p=p, gci=gci, e21=e21, e32=e32, R=R)


# =============================================================================
#  CONTROLS.  Every one ends in a fall-through refuse(...) (Amendment 6a).
# =============================================================================
def _synthetic_line(offset=0.0, flat=None):
    """Build a synthetic gate-line file body on the registered fixed grid."""
    grid = [Y_LO + (Y_HI - Y_LO) * i / (N_LINE - 1) for i in range(N_LINE)]
    ref = reference_profile(grid)
    rows = []
    for y, th in zip(grid, ref):
        t = T_INF + th * (T_WALL - T_INF) if flat is None else flat
        rows.append("%.12g %.12g" % (y, t + offset))
    return "\n".join(rows) + "\n"


_TMPDIR = None


def _tmpdir():
    """Control fixtures live in a process-private temp dir, never in the
    repository beside the frozen instrument."""
    global _TMPDIR
    if _TMPDIR is None:
        _TMPDIR = tempfile.mkdtemp(prefix="vmfl076_selftest_")
    return _TMPDIR


def _write_tmp(name, body):
    d = _tmpdir()
    p = os.path.join(d, name)
    fh = open(p, "w")
    fh.write(body)
    fh.close()
    return p


def control_reference_blasius():
    sim = similarity()
    if abs(sim.fpp0 - BLASIUS_FPP0) > 1e-8:
        refuse("R1", "BLASIUS CONTROL FAILED: f''(0) = %.12g against the classical "
                     "%.12g" % (sim.fpp0, BLASIUS_FPP0))
    if abs(sim.beta - BLASIUS_BETA) > 1e-6:
        refuse("R2", "BLASIUS CONTROL FAILED: displacement constant beta = %.12g "
                     "against the classical %.12g" % (sim.beta, BLASIUS_BETA))
    if sim.thp0 <= 0.0:
        refuse("R3", "REFERENCE CONTROL FAILED: theta'(0) = %.12g is not positive" % sim.thp0)
    return True


def control_slug_shortcut_is_not_the_reference():
    """THE LOAD-BEARING FINDING, locked into the instrument. If anyone ever swaps
    the exact similarity solution for the obvious low-Pr slug/erfc shortcut, this
    control fires and the comparator refuses."""
    sim = similarity()
    slug = math.sqrt(PR / math.pi)
    gap = 100.0 * (1.0 - sim.thp0 / slug)
    if abs(gap - SLUG_GAP_PCT) > SLUG_GAP_TOL:
        refuse("R4", "SLUG-SHORTCUT CONTROL FAILED: the exact similarity theta'(0) = "
                     "%.12g sits %.6f %% from the slug asymptote sqrt(Pr/pi) = %.12g, "
                     "against the registered %.6f %%. The reference in use is NOT the "
                     "one this case froze." % (sim.thp0, gap, slug, SLUG_GAP_PCT))
    if gap < 1.0:
        refuse("R5", "SLUG-SHORTCUT CONTROL FAILED: the exact solution and the slug "
                     "shortcut are within 1 %% of each other, which contradicts the "
                     "frozen finding that the shortcut is unusable here")
    return True


def control_plant_offset():
    """RULE 3, the planted-zero control. A known perturbation is planted into the
    file ON DISK, read back, and the estimator must move by EXACTLY the predicted
    amount. It refuses if the reader cannot see it."""
    clean = _write_tmp("clean.xy", _synthetic_line())
    ys0, ts0 = read_gate_line(clean)
    i0 = theta_integral(ys0, ts0)
    planted = _write_tmp("planted.xy", _synthetic_line(offset=PLANT_DT))
    ys1, ts1 = read_gate_line(planted)
    i1 = theta_integral(ys1, ts1)
    predicted = (PLANT_DT / (T_WALL - T_INF)) * (ys0[-1] - ys0[0])
    seen = i1 - i0
    if abs(seen - predicted) > 1e-12:
        refuse("P1", "PLANTED CONTROL FAILED: %.6g K was planted into every row of "
                     "%s; the estimator must move by %.12g m and moved by %.12g m"
               % (PLANT_DT, planted, predicted, seen))
    if seen == 0.0:
        refuse("P2", "PLANTED CONTROL FAILED: the estimator did not move at all "
                     "against a planted %.6g K" % PLANT_DT)
    return True


def control_plant_nonzero_into_a_zero_reader():
    """A zero from a reader not shown able to see a non-zero is not evidence."""
    flat = _write_tmp("flat.xy", _synthetic_line(flat=T_INF))
    ys, ts = read_gate_line(flat)
    izero = theta_integral(ys, ts)
    if izero != 0.0:
        refuse("P3", "PLANTED CONTROL FAILED: a line held at T_inf everywhere must "
                     "integrate to EXACTLY zero and gave %.12g" % izero)
    body = _synthetic_line(flat=T_INF).split("\n")
    grid = [Y_LO + (Y_HI - Y_LO) * i / (N_LINE - 1) for i in range(N_LINE)]
    j = 40
    body[j] = "%.12g %.12g" % (grid[j], T_INF + PLANT_DT)
    spiked = _write_tmp("spiked.xy", "\n".join(body))
    ys2, ts2 = read_gate_line(spiked)
    ispike = theta_integral(ys2, ts2)
    if ispike <= 0.0:
        refuse("P4", "PLANTED CONTROL FAILED: a single %.6g K spike planted at row %d "
                     "was INVISIBLE to the estimator (it still read %.12g). A zero "
                     "from this reader would not be evidence." % (PLANT_DT, j, ispike))
    dy = grid[1] - grid[0]
    expect = (PLANT_DT / (T_WALL - T_INF)) * dy
    if abs(ispike - expect) > 1e-12:
        refuse("P5", "PLANTED CONTROL FAILED: the single-spike integral %.12g does "
                     "not equal the predicted %.12g" % (ispike, expect))
    return True


def control_roache_classifier():
    # f_i = f_exact + A h_i^p with h = 4, 2, 1 (relative) and p = 2 exactly.
    fe, A, p_true = 1.0, 1.0e-4, 2.0
    f1 = fe + A * 16.0
    f2 = fe + A * 4.0
    f3 = fe + A * 1.0
    r = roache(f1, f2, f3)
    if r["cls"] != "CONVERGING":
        refuse("K1", "ROACHE CONTROL FAILED: an exactly-2nd-order triple classified "
                     "as %s" % r["cls"])
    if abs(r["p"] - p_true) > 1e-9:
        refuse("K2", "ROACHE CONTROL FAILED: p_obs = %.12g on an exactly-2nd-order "
                     "triple" % r["p"])
    if roache(1.0, 1.1, 1.3)["cls"] != "DIVERGENT":
        refuse("K3", "ROACHE CONTROL FAILED: a widening triple was not DIVERGENT")
    if roache(1.0, 1.1, 1.05)["cls"] != "OSCILLATORY":
        refuse("K4", "ROACHE CONTROL FAILED: a sign-flipping triple was not OSCILLATORY")
    if roache(1.0, 1.0, 1.0)["cls"] != "EXACT":
        refuse("K5", "ROACHE CONTROL FAILED: an identical triple was not EXACT")
    return True


def control_plateau_refuses():
    ts = [i * 50 for i in range(1, 41)]
    end = 2000
    grow = [1.0 + 1.0e-2 * (t / float(end)) for t in ts]
    ok, n, pp, tr, nd = plateau(ts, grow, end)
    if ok:
        refuse("K6", "PLATEAU CONTROL FAILED: a monotonically GROWING series was "
                     "accepted as settled (pp=%.3e trend=%.3e n=%d)" % (pp, tr, n))
    # AMENDMENT 4 item 4: a series with no variation AT ALL must refuse.
    flat = [1.0] * len(ts)
    hit = []
    try:
        plateau(ts, flat, end)
    except SystemExit as e:
        hit.append(e.code)
    if hit != [2]:
        refuse("K7", "PLATEAU CONTROL FAILED: a NULL-RANGE series did not refuse "
                     "(exit codes seen: %r)" % hit)
    # ... and the CORRECT-RUN direction: a series that moved and then froze in the
    # settling window is CONVERGENCE and must be ACCEPTED, not refused. Amendment 5a:
    # a check that refuses correct runs fails in the unsafe-for-progress direction.
    settled = [1.0 + 1.0e-2 * max(0.0, (1000.0 - t) / 1000.0) for t in ts]
    ok2, n2, pp2, tr2, nd2 = plateau(ts, settled, end)
    if not ok2:
        refuse("K7b", "PLATEAU CONTROL FAILED: a series that moved early and is "
                      "EXACTLY frozen through the whole settling window was refused "
                      "(pp=%.3e trend=%.3e n=%d distinct=%d)" % (pp2, tr2, n2, nd2))
    if nd2 != 1:
        refuse("K7c", "PLATEAU CONTROL FAILED: the frozen-window fixture reports %d "
                      "distinct values, expected 1" % nd2)
    hit2 = []
    try:
        plateau(ts[-3:], [1.0, 1.001, 1.0009], end)
    except SystemExit as e:
        hit2.append(e.code)
    if hit2 != [2]:
        refuse("K8", "PLATEAU CONTROL FAILED: a window below the %d-sample floor did "
                     "not refuse (exit codes seen: %r)" % (PLATEAU_MIN_N, hit2))
    return True


def control_completion_refuses():
    d = os.path.join(_tmpdir(), "emptylevel")
    if not os.path.isdir(d):
        os.makedirs(d)
    hit = []
    try:
        completion_check(d, 1000)
    except SystemExit as e:
        hit.append(e.code)
    if hit != [2]:
        refuse("K9", "COMPLETION CONTROL FAILED: an EMPTY level directory did not "
                     "refuse (exit codes seen: %r)" % hit)
    return True


def control_vocabulary_guard():
    hit = []
    try:
        emit("FAIL")
    except SystemExit as e:
        hit.append(e.code)
    if hit != [2]:
        refuse("K10", "VOCABULARY CONTROL FAILED: the bare verdict 'FAIL' was not "
                      "refused (exit codes seen: %r). Under python3 -O an assert-based "
                      "guard would have vanished here." % hit)
    if emit("GATE REACHED") != "GATE REACHED":
        refuse("K11", "VOCABULARY CONTROL FAILED: a legal verdict was not returned")
    return True


def control_reader_sees_a_short_line():
    grid = [Y_LO + (Y_HI - Y_LO) * i / (N_LINE - 1) for i in range(N_LINE)]
    rows = ["%.12g %.12g" % (grid[i], T_INF) for i in range(50)]
    short = _write_tmp("short.xy", "\n".join(rows) + "\n")
    hit = []
    try:
        read_gate_line(short)
    except SystemExit as e:
        hit.append(e.code)
    if hit != [2]:
        refuse("K12", "READER CONTROL FAILED: a 50-point gate line passed the %d-point "
                      "floor (exit codes seen: %r)" % (MIN_LINE_POINTS, hit))
    off = ["%.12g %.12g" % (g + 1.0e-4, T_INF) for g in grid]
    offp = _write_tmp("offgrid.xy", "\n".join(off) + "\n")
    hit2 = []
    try:
        read_gate_line(offp)
    except SystemExit as e:
        hit2.append(e.code)
    if hit2 != [2]:
        refuse("K13", "READER CONTROL FAILED: an OFF-GRID gate line was accepted "
                      "(exit codes seen: %r)" % hit2)
    return True


def control_reference_matches_itself():
    grid = [Y_LO + (Y_HI - Y_LO) * i / (N_LINE - 1) for i in range(N_LINE)]
    clean = _write_tmp("clean2.xy", _synthetic_line())
    ys, ts = read_gate_line(clean)
    ilab = theta_integral(ys, ts)
    iref = reference_integral(ys)
    if abs(ilab - iref) / abs(iref) > 1e-9:
        refuse("K14", "SYNTHETIC CONTROL FAILED: a gate line built FROM the reference "
                      "graded %.12g against a reference of %.12g" % (ilab, iref))
    dev, _ = max_abs_profile_dev(ys, ts)
    if dev > 1e-9:
        refuse("K15", "SYNTHETIC CONTROL FAILED: max |dTheta| = %.3e against the "
                      "reference the line was built from" % dev)
    if len(grid) != N_LINE:
        refuse("K16", "SYNTHETIC CONTROL FAILED: the registered grid is not %d points" % N_LINE)
    return True


CONTROLS = (
    ("reference/blasius", control_reference_blasius),
    ("reference/slug-shortcut-rejected", control_slug_shortcut_is_not_the_reference),
    ("rule3/plant-offset", control_plant_offset),
    ("rule3/plant-nonzero-into-zero", control_plant_nonzero_into_a_zero_reader),
    ("rule5/roache-classifier", control_roache_classifier),
    ("amend4/plateau-refuses", control_plateau_refuses),
    ("rule4/completion-refuses", control_completion_refuses),
    ("rule1/vocabulary-guard", control_vocabulary_guard),
    ("reader/floor-and-grid", control_reader_sees_a_short_line),
    ("synthetic/reference-identity", control_reference_matches_itself),
)


def selftest():
    passed = 0
    for name, fn in CONTROLS:
        got = fn()
        if got is not True:
            refuse("X1", "CONTROL %s did not return True (returned %r) -- a control "
                         "that can return without passing is not a control" % (name, got))
        passed += 1
        sys.stdout.write("  control %-38s PASSED\n" % name)
    if passed != len(CONTROLS):
        refuse("X2", "only %d of %d controls ran" % (passed, len(CONTROLS)))
    sim = similarity()
    sys.stdout.write("  f''(0)      = %.12f\n" % sim.fpp0)
    sys.stdout.write("  beta        = %.10f\n" % sim.beta)
    sys.stdout.write("  theta'(0)   = %.12f   (Nu_x/sqrt(Re_x))\n" % sim.thp0)
    sys.stdout.write("  slug gap    = %.6f %% (registered %.6f %%)\n"
                     % (100.0 * (1.0 - sim.thp0 / math.sqrt(PR / math.pi)), SLUG_GAP_PCT))
    grid = [Y_LO + (Y_HI - Y_LO) * i / (N_LINE - 1) for i in range(N_LINE)]
    sys.stdout.write("  I_ref       = %.12e m  (trapz over the %d fixed points at x = %g m)\n"
                     % (reference_integral(grid), N_LINE, X_GATE))
    # Amendment 6a item 1: this claim is UNREACHABLE unless every control above
    # returned True -- each of them exits(2) on its own failing path.
    sys.stdout.write("SELFTEST GREEN: %d/%d controls passed.\n" % (passed, len(CONTROLS)))
    return 0


# =============================================================================
#  GRADING
# =============================================================================
def _sample_times(level_dir):
    root = os.path.join(level_dir, "postProcessing", "sampleLine")
    if not os.path.isdir(root):
        refuse("G1", "%s: no postProcessing/sampleLine directory -- the gate line was "
                     "never sampled" % level_dir)
    out = []
    for name in os.listdir(root):
        d = os.path.join(root, name)
        if not os.path.isdir(d):
            continue
        try:
            t = float(name)
        except ValueError:
            continue
        hits = sorted(glob.glob(os.path.join(d, "gateLine*T*.xy")))
        if len(hits) != 1:
            refuse("G2", "%s: expected exactly one gateLine T file, found %d"
                   % (d, len(hits)))
        out.append((t, hits[0]))
    if not out:
        refuse("G3", "%s: postProcessing/sampleLine holds no time directories" % level_dir)
    out.sort()
    return out


def _verify_frozen_station(level_dir):
    cd = os.path.join(level_dir, "system", "controlDict")
    if not os.path.isfile(cd):
        refuse("G4", "%s: system/controlDict is missing; the gate station cannot be "
                     "proved" % level_dir)
    txt = open(cd, "r").read()
    if not re.search(r"start\s*\(\s*0\.75\s+0\s+0\.025\s*\)", txt):
        refuse("G5", "%s: system/controlDict does not carry the frozen gate line "
                     "start (0.75 0 0.025)" % level_dir)
    if not re.search(r"end\s*\(\s*0\.75\s+0\.5\s+0\.025\s*\)", txt):
        refuse("G6", "%s: system/controlDict does not carry the frozen gate line "
                     "end (0.75 0.5 0.025)" % level_dir)
    if not re.search(r"nPoints\s+%d\s*;" % N_LINE, txt):
        refuse("G7", "%s: system/controlDict does not carry nPoints %d" % (level_dir, N_LINE))
    return True


def grade_level(level_dir, end_time):
    completion_check(level_dir, end_time)
    _verify_frozen_station(level_dir)
    series = _sample_times(level_dir)
    times, vals = [], []
    for t, path in series:
        ys, ts = read_gate_line(path)
        times.append(t)
        vals.append(theta_integral(ys, ts))
    ok, n, pp, trend, ndist = plateau(times, vals, end_time)
    last_path = series[-1][1]
    ys, ts = read_gate_line(last_path)
    if abs(times[-1] - end_time) > 1e-9:
        refuse("G8", "%s: the last sampled time %g is not endTime %g"
               % (level_dir, times[-1], end_time))
    i_lab = theta_integral(ys, ts)
    i_ref = reference_integral(ys)
    dev, devy = max_abs_profile_dev(ys, ts)
    return dict(dir=level_dir, ys=ys, n_window=n, n_distinct=ndist, pp=pp, trend=trend, settled=ok,
                i_lab=i_lab, i_ref=i_ref, dev=dev, devy=devy, npts=len(ys))


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if len(argv) < 3:
        sys.stdout.write("usage: grade_vmfl076.py <runroot> L1:endTime L2:endTime L3:endTime\n")
        sys.stdout.write("       grade_vmfl076.py --selftest\n")
        return 2
    for name, fn in CONTROLS:
        if fn() is not True:
            refuse("X3", "control %s did not pass before grading" % name)
    runroot = argv[0]
    levels = []
    for spec in argv[1:4]:
        nm, et = spec.split(":")
        levels.append((nm, int(et)))
    res = [grade_level(os.path.join(runroot, nm), et) for nm, et in levels]

    for a in range(1, 3):
        if len(res[a]["ys"]) != len(res[0]["ys"]):
            refuse("G9", "levels return %d and %d gate-line points -- the three levels "
                         "are NOT measuring the same functional and may not be compared"
                   % (len(res[0]["ys"]), len(res[a]["ys"])))
        for i in range(len(res[0]["ys"])):
            if abs(res[a]["ys"][i] - res[0]["ys"][i]) > 1e-12:
                refuse("G10", "level %s gate-line y[%d] = %.15g differs from level %s "
                              "%.15g" % (res[a]["dir"], i, res[a]["ys"][i], res[0]["dir"],
                                         res[0]["ys"][i]))

    sim = similarity()
    sys.stdout.write("VMFL076 GRADING\n")
    sys.stdout.write("  reference theta'(0) = %.12f (similarity ODE, evaluated here)\n" % sim.thp0)
    sys.stdout.write("  gate station x      = %g m ; %d fixed sample points\n"
                     % (X_GATE, res[0]["npts"]))
    for (nm, et), r in zip(levels, res):
        sys.stdout.write("  %-4s I_lab = %.12e m   I_ref = %.12e m   rel = %+.6f %%   "
                         "max|dTheta| = %.4e at y = %g   n_window = %d  n_distinct = %d  "
                         "pp = %.3e  trend = %.3e  settled = %s\n"
                         % (nm, r["i_lab"], r["i_ref"],
                            100.0 * (r["i_lab"] - r["i_ref"]) / r["i_ref"],
                            r["dev"], r["devy"], r["n_window"], r["n_distinct"],
                            r["pp"], r["trend"], r["settled"]))

    unsettled = [nm for (nm, _), r in zip(levels, res) if not r["settled"]]
    tri = roache(res[0]["i_lab"], res[1]["i_lab"], res[2]["i_lab"])
    sys.stdout.write("  Roache triple: class = %s  R = %s  p_obs = %s  GCI_fine = %s\n"
                     % (tri["cls"],
                        "n/a" if tri["R"] is None else "%.6f" % tri["R"],
                        "n/a" if tri["p"] is None else "%.4f" % tri["p"],
                        "n/a" if tri["gci"] is None else "%.4e" % tri["gci"]))

    fine = res[2]
    rel = abs(fine["i_lab"] - fine["i_ref"]) / abs(fine["i_ref"])
    sys.stdout.write("  GATE A |I_lab - I_ref|/I_ref = %.6f %%  against band %.4f %%\n"
                     % (100.0 * rel, 100.0 * TOL_A))
    sys.stdout.write("  GATE B max|dTheta|           = %.6e     against band %.6e\n"
                     % (fine["dev"], TOL_B))

    if unsettled:
        verdict = emit("NOT A RESULT")
        sys.stdout.write("VERDICT: %s -- levels not plateaued: %s\n" % (verdict, ", ".join(unsettled)))
        return 1
    if tri["cls"] != "CONVERGING":
        verdict = emit("NOT A RESULT")
        sys.stdout.write("VERDICT: %s -- the grid triple is %s, not CONVERGING (rule 5). "
                         "I_lab = %.12e / %.12e / %.12e m\n"
                         % (verdict, tri["cls"], res[0]["i_lab"], res[1]["i_lab"], res[2]["i_lab"]))
        return 1
    if rel <= TOL_A and fine["dev"] <= TOL_B:
        verdict = emit("GATE REACHED")
        sys.stdout.write("VERDICT: %s -- both frozen gates met at the finest level.\n" % verdict)
        return 0
    verdict = emit("GATE FAIL")
    sys.stdout.write("VERDICT: %s -- Gate A %s, Gate B %s.\n"
                     % (verdict, "met" if rel <= TOL_A else "MISSED",
                        "met" if fine["dev"] <= TOL_B else "MISSED"))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
