#!/usr/bin/env python3
# ===========================================================================
# grade_vmfl007.py -- the comparator for VMFL007, Non-Newtonian Flow in a Pipe
# (Ansys Fluid Dynamics Verification Manual, Release 2026 R1, printed p. 29).
#
# FROZEN AT THE PRE-REGISTRATION COMMIT.  The grading path is fixed there and
# `--verify-frozen <commitish>` hashes this file against the committed blob.
#
# THIS COMPARATOR FIXES A CLASS FAULT IN HOW THE REPO ROOT IS DERIVED.
# MEASURED, and stated at exactly its measured size -- neither more nor less.
# Seven comparators exist under cases/ansys_verification/.  THREE derive no root
# at all (VMFL001, VMFL001-R2, VMFL005 use only abspath(__file__)).  FOUR do,
# in two flavours, and BOTH flavours are LATENT -- each behaves CORRECTLY on this
# box today, and NO verdict this team has issued is affected:
#
#   (a) HARDCODED -- grade_vmfl045.py:59, grade_vmfl045_r2.py:59,
#       grade_vmfl051.py:62 all carry  REPO = "/home/ubuntu/Certonomous"  and use
#       it as a genuine path root (RUN_ROOT, OUT_JSON, `git -C REPO`).  Correct
#       here; wrong in a worktree, a clone, or after a move -- and wrong
#       SILENTLY, because every path built from it still looks plausible.
#
#   (b) DEPTH-COUNTED -- grade_vmfl003.py:937 passes
#       dirname(dirname(dirname(here))) as the `cwd` of a git subprocess.  That
#       expression evaluates to <repo>/cases, which is NOT the repo root -- it is
#       one level short at that file's depth.  IT IS NEVERTHELESS CORRECT IN
#       EFFECT, because git resolves its repository from any subdirectory, so the
#       value is only ever used somewhere its wrongness cannot show.  The defect
#       is in what the idiom would do if reused as a path root, not in what it
#       does.  Saying more than that would overstate it.
#
# WHAT IS COMMON TO BOTH, and what is actually fixed here: neither form is ever
# CHECKED against anything, so neither can fail loudly.  HERE the root is ASKED
# FOR -- `git rev-parse --show-toplevel`, run with cwd set to THIS FILE'S OWN
# DIRECTORY -- and then CHECKED: this file must lie inside the returned root, at
# the relative path this file declares, and be the SAME INODE.  A mismatch
# REFUSES (exit 2).  Depth is never counted and no path is ever hardcoded.
# ===========================================================================
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

# ---------------------------------------------------------------------------
# 0.  THE REPO ROOT -- asked for, then checked.
# ---------------------------------------------------------------------------
SELF_REL = "cases/ansys_verification/VMFL007/grade_vmfl007.py"


class Refusal(Exception):
    pass


def refuse(clause, msg):
    raise Refusal("[%s] %s" % (clause, msg))


def _repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=here, stderr=subprocess.STDOUT)
    except Exception as e:
        refuse("R0", "git rev-parse --show-toplevel failed from %r: %s" % (here, e))
    root = out.decode().strip()
    if not root or not os.path.isdir(root):
        refuse("R0", "repo root %r is not a directory" % root)
    # THE CHECK the existing comparators do not have: this file must actually
    # be at SELF_REL inside that root.  Same inode, not merely the same string.
    want = os.path.join(root, SELF_REL)
    got = os.path.abspath(__file__)
    if not os.path.exists(want):
        refuse("R0", "repo root %r does not contain %s" % (root, SELF_REL))
    if not os.path.samefile(want, got):
        refuse("R0", "this file is %r but %s in the repo root is a DIFFERENT "
                     "file -- the root derivation is wrong" % (got, SELF_REL))
    return root


try:
    REPO = _repo_root()
except Refusal as _e:
    # A root that cannot be established is a refusal, not a traceback.
    print("REFUSE: %s" % _e, file=sys.stderr)
    sys.exit(2)
except Exception as _e:                      # git absent, not a repo, ...
    print("REFUSE: [R0] cannot establish the repository root: %s" % _e,
          file=sys.stderr)
    sys.exit(2)
RUN_ROOT = os.path.join(REPO, "verification/runs/ansys_verification/VMFL007")
OUT_JSON = os.path.join(RUN_ROOT, "GRADING_VMFL007.json")

# ---------------------------------------------------------------------------
# 1.  THE MANUAL.  Printed p. 29; PDF p. 43.  Read off the page, nothing else.
# ---------------------------------------------------------------------------
MANUAL_PAGE = "29 (printed); 43 (PDF)"
MANUAL_REFERENCE = ("W. F. Hughes and J. A. Brighton, Schaum's Outline of Theory "
                    "and Problems of Fluid Dynamics, McGraw-Hill, New York, 1991")
MANUAL_TARGET_KPA = 60.52          # "Pressure Drop, kPa | Target | 60.52"
MANUAL_TARGET = 60520.0            # Pa.  THE GATE REFERENCE.
MANUAL_TARGET_HALFWIDTH = 5.0      # Pa; the target is printed to 4 figures.

# Ansys's own reported values -- CONTEXT, never the gate (charter section 5.1).
ANSYS_CONTEXT = {"Fluent_Pa": 60410.0, "Fluent_ratio": 0.998,
                 "CFX_Pa": 61520.0, "CFX_ratio": 1.0165,
                 "archive_srp_inlet_Pa": 60498.203}

# Manual material properties and geometry, p. 29.
RHO = 1000.0        # kg/m3   "Density = 1000 kg/m3"
K_DYN = 10.0        # Pa.s^n  "k = 10"   -- DYNAMIC consistency index
N_IDX = 0.4         # -       "n = 0.4"
D_PIPE = 0.0025     # m       "Pipe diameter = 0.0025 m"
L_PIPE = 0.1        # m       "Pipe length = 0.1 m"
V_MEAN = 2.0        # m/s     "average velocity of 2 m/s"
R_PIPE = D_PIPE / 2.0

# ---------------------------------------------------------------------------
# 2.  THE CLOSED FORM.  Rabinowitsch-Mooney for a fully developed laminar
#     power-law pipe flow.  DIAGNOSTIC ONLY -- never the gate.
# ---------------------------------------------------------------------------
def closed_form():
    apparent = 8.0 * V_MEAN / D_PIPE                    # 6400 1/s
    corr = (3.0 * N_IDX + 1.0) / (4.0 * N_IDX)          # 1.375
    gamma_w = corr * apparent                           # 8800 1/s
    tau_w = K_DYN * gamma_w ** N_IDX                    # Pa
    dp = 4.0 * L_PIPE * tau_w / D_PIPE                  # Pa
    re_gen = 8.0 * RHO * V_MEAN ** 2 / tau_w
    return apparent, corr, gamma_w, tau_w, dp, re_gen


(APPARENT, CORR, GAMMA_W, TAU_W, DP_EXACT, RE_GEN) = closed_form()

# Frozen to full double precision so a later edit to closed_form() is caught.
TAU_W_FROZEN = 378.2623086489655
DP_EXACT_FROZEN = 60521.96938383448
RE_GEN_FROZEN = 84.59737930087186

# ---------------------------------------------------------------------------
# 3.  THE WEDGE MODELLING BIAS -- charter v1.4 Clause A, N-AV9.
#     For a PRESSURE-DROP gate the governing term is sec(t/2) - 1, the RATIO of
#     the wall-arc deficit to the area deficit, NOT sin(t)/t on its own.
#     From the fully developed force balance dp*A = tau_w*P*L:
#         true sector  P/A = 2/R ;  flat wedge  P/A = 2/(R cos(t/2))
#     so the modelled dp is HIGH by sec(t/2).  AZIMUTHAL: no refinement removes it.
# ---------------------------------------------------------------------------
WEDGE_TOTAL_DEG = 1.0
_t = math.radians(WEDGE_TOTAL_DEG)
WEDGE_AREA_RATIO = math.sin(_t) / _t                       # 0.9999492312032947
WEDGE_ARC_RATIO = math.sin(_t / 2) / (_t / 2)              # 0.9999873076558379
WEDGE_DP_BIAS = 1.0 / math.cos(_t / 2) - 1.0               # +3.807838573699485e-05
WEDGE_DP_BIAS_FROZEN = 3.807838573699485e-05
DP_EXACT_WEDGE = DP_EXACT_FROZEN * (1.0 + WEDGE_DP_BIAS_FROZEN)
# The solver's own inlet-patch area must equal the flat-wedge formula.
WEDGE_PATCH_AREA = 0.5 * R_PIPE ** 2 * math.sin(_t)        # 1.363469252912774e-08
WEDGE_PATCH_AREA_TOL = 1e-9                                # relative

# ---------------------------------------------------------------------------
# 4.  THE GATE AND THE DIAGNOSTICS.  Justified in PREREGISTRATION.md section 5.
# ---------------------------------------------------------------------------
TOL_GATE = 0.005        # 0.5 % of MANUAL_TARGET.  THE GATE.  [60217.4, 60822.6] Pa
TOL_DIAG_EXACT = 0.0025     # D1: 0.25 % of DP_EXACT_FROZEN.  DIAGNOSTIC.
TOL_DIAG_WEDGE = 0.0015     # D2: 0.15 % of DP_EXACT_WEDGE.   DIAGNOSTIC.

# ---------------------------------------------------------------------------
# 5.  THE UNIT CONVERSIONS -- both are factors of 1000, in OPPOSITE directions.
#     Neither is a comment; both are asserted below (clauses S3, S5).
#       k_OF  = K_DYN / RHO  = 0.01     kinematic, into constant/transportProperties
#       dp_Pa = RHO * dp_foam           simpleFoam's p is kinematic p/rho
# ---------------------------------------------------------------------------
K_OF = K_DYN / RHO          # 0.01
K_OF_FROZEN = 0.01
NU_MIN_DICT = 1e-08         # the dictionary's floor -- must never bind
NU_MAX_DICT = 1.0           # the dictionary's ceiling -- must never bind
NU_WALL_EXACT = K_OF_FROZEN * GAMMA_W ** (N_IDX - 1.0)   # 4.298435325556426e-05
# Band on min(nu) at endTime.  The minimum sits in the wall cell, ABOVE the
# continuum wall value and approaching it as N_r grows: 4.433e-05 / 4.365e-05 /
# 4.331e-05 predicted at L1/L2/L3.  This band is a factor of ~2 either side and
# is still 465x above what the WRONG powerLaw class would give.
NU_MIN_BAND = (2.0e-05, 8.0e-05)
# THE TRAP, quantified: laminarModels::generalizedNewtonianViscosityModels::
# powerLaw has NO `k` key -- it multiplies nu0 from the transport model.  Seeded
# from a Newtonian nu0 = 1e-05 (which is exactly the leftover constant in the
# archive's own material blob) it would give min(nu) ~ 4.30e-08 and dp ~ 3819 Pa.
NU_MIN_IF_WRONG_CLASS = 4.298435325556426e-08
NU_MAX_CEILING = 0.5 * NU_MAX_DICT   # max(nu) must stay well under the clip

# The inlet profile, asserted on two independent channels.
U_MAX_PROFILE = V_MEAN * (3.0 * N_IDX + 1.0) / (N_IDX + 1.0)   # 3.142857142857143
PROFILE_EXPONENT = (N_IDX + 1.0) / N_IDX                        # 3.5
UMAX_BAND = (3.10, 3.15)     # a UNIFORM 2 m/s inlet reads 2.0000 and FAILS this
Q_REL_TOL = 0.01             # |sum(phi)| vs V_MEAN * patch area

# ---------------------------------------------------------------------------
# 6.  STRICT COMPLETION (CLAUDE.md rule 4) AND ITERATIVE CONVERGENCE.
# ---------------------------------------------------------------------------
ENDTIME = 10000              # SIMPLE iterations, IDENTICAL at every level
WRITEINTERVAL = 5000
REQUIRED_FIELDS = ("U", "p", "phi", "nu")
AGE_MARKER = os.path.join("0", "U")   # touched LAST at launch; the age guard

# Plateau, in MONITOR_STANDARD S13's 1.12 form -- adopted deliberately, and it
# is TIGHTER in the way that matters than the absolute fraction-of-run clause
# frozen in grade_vmfl051.py / grade_vmfl045_r2.py.  Two departures from those:
#   (a) a FIXED window, not a fraction of the run: "a fraction-of-run window
#       silently loosens as a run is extended, so the same case passes by being
#       run longer" (S13; charter v1.4 disclosure 1 says a NEW registration
#       should gate on a fixed window and say so -- this one does);
#   (b) normalised by THE RANGE THE SERIES SPANNED OVER THE WHOLE RUN, not by
#       its mean.  A criterion normalised by the mean measures the OFFSET on any
#       quantity that carries one, and dp carries a large one.
PLATEAU_WINDOW = 1000        # fixed, final iterations
PLATEAU_STRIDE = 100         # -> 11 samples, above S13's floor of 9
PLATEAU_MIN_SAMPLES = 9
PLATEAU_TOL_FRAC_OF_RANGE = 2.0e-4       # 0.02 % -- S13's threshold
PLATEAU_NULL_RANGE_PA = 1.0              # S13 null-variation clause: a series
                                         # that never resolvably MOVED is
                                         # CANNOT_TELL, never a pass.

# Residual BACKSTOP -- deliberately looser than VMFL001's, and the reason is
# stated rather than hidden.  VMFL001 run 1 was refused NOT A RESULT because its
# L3 final Ux/Uy initial residual measured 1.19876e-06 against a frozen < 1e-6
# (COVERAGE_ROWS.md row 1).  N-AV5 records that the fixed-iteration residual
# degrades sharply and NOT by a constant factor with cell count.  A residual
# threshold at a round number is therefore a lottery, not a convergence
# criterion.  HERE the PLATEAU above is the primary, binding convergence clause
# -- it measures whether THE GRADED ANSWER has stopped moving -- and these
# numbers are a backstop against a solve that stalls at a wrong plateau.
# BOTH bind: failing either is NOT A RESULT.
RESID_UX_MAX = 1.0e-05
RESID_P_MAX = 1.0e-04

# ---------------------------------------------------------------------------
# 7.  ROACHE (CLAUDE.md rule 5).
#     N-AV10's axial-only constraint is scoped to WALL FUNCTIONS in turbulent
#     flow.  VMFL007 is LAMINAR with NO wall function, so it does not apply and
#     the triple refines RADIALLY as well as axially -- a genuine G column.
# ---------------------------------------------------------------------------
FS = 1.25
RATIO = 2.0
EPS_ABS = 1e-9               # Pa; a level-to-level difference below this is zero
STAG_TOL = 1e-3

LEVELS = (  # name, nx, nr, cells
    ("L1_25x25", 25, 25, 625),
    ("L2_50x50", 50, 50, 2500),
    ("L3_100x100", 100, 100, 10000),
)
GATE_LEVEL = "L3_100x100"    # the gate is applied to the FINE level

# THE OBSERVED ORDER, DECLARED BEFORE THE FACT.
# Formal order of the scheme is 2 (Gauss linear, corrected snGrad, steadyState).
# EXPECTED: p in [1.0, 2.5].  BELOW 2 is expected and has a named cause -- the
# power-law viscosity is SINGULAR on the axis, nu(r) ~ r^-1.5 as r -> 0, so the
# truncation error near the axis involves derivatives of nu that do not converge
# at the scheme's formal rate.  What reaches dp is dominated by the wall region,
# so the effect on dp should be modest, but the direction is downward.
# ABOVE THE FORMAL ORDER IS **SUSPICIOUS, NOT GOOD**: an observed order above 2
# means the triple is NOT in the asymptotic range and the GCI it produces does
# not bound anything.  Both of this team's compressible cases were bitten by
# exactly this (VMFL045-R2 measured p = 3.3862).  It is printed as SUSPICIOUS
# beside the verdict and it does NOT by itself change the verdict.
ORDER_EXPECTED = (1.0, 2.5)
ORDER_FORMAL = 2.0
ORDER_SUSPICIOUS_ABOVE = 2.5

# ---------------------------------------------------------------------------
# 8.  PLANTED-ZERO CONTROLS (CLAUDE.md rule 3).  A zero from a reader not shown
#     able to see a non-zero is not evidence.  Each plants into a COPY, reads it
#     back FROM DISK, and REFUSES if the reader cannot see it.
# ---------------------------------------------------------------------------
PLANT_DAT = 1.234e-03        # into a copy of surfaceFieldValue.dat (kinematic p)
PLANT_DAT_TOL = 1e-12
PLANT_FIELD = 7.77e-02       # into a copy of the endTime nu field
PLANT_FIELD_TOL = 1e-9

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")

# THE TIER CEILING, DECLARED IN ADVANCE (charter section 6; COVERAGE_ROWS.md).
#   V -- available.  The reference IS the exact closed form and the manual's
#        printed target agrees with it to +0.0033 %.  V is earned only if the
#        Richardson extrapolate lands ON it (N-AV7: a small GCI does NOT license
#        the V column), so it is measured, not assumed.
#   G -- available.  Laminar, no wall function, radial refinement legitimate.
#   P -- NOT AVAILABLE.  The reference is CLOSED-FORM / EXACT (category 1),
#        which buys V and never P.
# CEILING: GATE REACHED.  HOLDS is not claimable on this case.  GATE REACHED is
# a SUCCESS condition for this team, not a shortfall.
TIER_CEILING = "GATE REACHED"
REFERENCE_KIND = "CLOSED-FORM / EXACT (category 1)"


# ===========================================================================
# READERS
# ===========================================================================
def read_fo_dat(path):
    """Parse an OpenFOAM surfaceFieldValue/volFieldValue .dat file."""
    if not os.path.exists(path):
        refuse("R1", "monitor file missing: %s" % path)
    rows, cols, area, ncells, nfaces = [], None, None, None, None
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                body = s.lstrip("#").strip()
                if body.lower().startswith("area"):
                    area = float(body.split(":", 1)[1] if ":" in body
                                 else body.split()[-1])
                elif body.lower().startswith("faces"):
                    nfaces = int(float(body.split()[-1]))
                elif body.lower().startswith("cells"):
                    ncells = int(float(body.split()[-1]))
                elif body.startswith("Time"):
                    cols = body.split()[1:]
                continue
            # data row: time, then values (which may be (a b c) vectors)
            toks = s.replace("(", " ").replace(")", " ").split()
            try:
                vals = [float(t) for t in toks]
            except ValueError:
                refuse("R1", "unparseable row in %s: %r" % (path, s))
            rows.append(vals)
    if not rows:
        refuse("R1", "no data rows in %s" % path)
    return {"rows": rows, "cols": cols, "area": area,
            "nfaces": nfaces, "ncells": ncells, "path": path}


def series_at(dat, iteration):
    for r in dat["rows"]:
        if abs(r[0] - iteration) < 0.5:
            return r
    refuse("R1", "iteration %s absent from %s" % (iteration, dat["path"]))


_NONUNIFORM_RE = re.compile(
    r"internalField\s+nonuniform\s+List<scalar>\s*\n\s*(\d+)\s*\n\s*\(", re.M)
_UNIFORM_RE = re.compile(r"internalField\s+uniform\s+([-+0-9.eE]+)\s*;")


def read_foam_scalar_field(path):
    if not os.path.exists(path):
        refuse("R2", "field file missing: %s" % path)
    txt = open(path).read()
    m = _NONUNIFORM_RE.search(txt)
    if m:
        n = int(m.group(1))
        start = m.end()
        end = txt.index(")", start)
        vals = [float(v) for v in txt[start:end].split()]
        if len(vals) != n:
            refuse("R2", "%s declares %d values, holds %d" % (path, n, len(vals)))
        return vals
    m = _UNIFORM_RE.search(txt)
    if m:
        return [float(m.group(1))]
    refuse("R2", "no internalField in %s" % path)


def plant_into_scalar_field(src, dst, delta):
    """Copy src to dst adding delta to the FIRST internal value."""
    txt = open(src).read()
    m = _NONUNIFORM_RE.search(txt)
    if not m:
        refuse("R2", "cannot plant into %s (not a nonuniform list)" % src)
    start = m.end()
    end = txt.index(")", start)
    body = txt[start:end].split()
    body[0] = repr(float(body[0]) + delta)
    open(dst, "w").write(txt[:start] + "\n" + "\n".join(body) + "\n" + txt[end:])


def plant_into_dat(src, dst, delta, col):
    """Copy src to dst adding delta to column `col` of the LAST data row."""
    lines = open(src).read().splitlines(True)
    last = None
    for i, ln in enumerate(lines):
        if ln.strip() and not ln.strip().startswith("#"):
            last = i
    if last is None:
        refuse("R1", "no data row to plant into in %s" % src)
    toks = lines[last].split()
    toks[col] = repr(float(toks[col]) + delta)
    lines[last] = "\t".join(toks) + "\n"
    open(dst, "w").write("".join(lines))


# ===========================================================================
# ROACHE
# ===========================================================================
def roache(f1, f2, f3, ratio=RATIO, fs=FS, eps=EPS_ABS, stag=STAG_TOL):
    """f1 coarse, f2 medium, f3 fine."""
    d21 = f2 - f1
    d32 = f3 - f2
    out = {"f_coarse": f1, "f_medium": f2, "f_fine": f3,
           "d21": d21, "d32": d32, "ratio_used": ratio,
           "order": None, "gci_fine": None, "extrapolated": None,
           "state": None, "R": None}
    if abs(d21) <= eps and abs(d32) <= eps:
        out["state"] = "EXACT"
        return out
    if abs(d21) <= eps or abs(d32) <= eps:
        out["state"] = "EXACT"
        return out
    R = d32 / d21
    out["R"] = R
    if R < 0:
        out["state"] = "OSCILLATORY"
        return out
    if abs(R - 1.0) <= stag:
        out["state"] = "STAGNANT"
        return out
    if R > 1.0:
        out["state"] = "DIVERGENT"
        return out
    p = math.log(abs(d21 / d32)) / math.log(ratio)
    out["order"] = p
    out["state"] = "CONVERGING"
    out["extrapolated"] = f3 + d32 / (ratio ** p - 1.0)
    if f3 != 0.0:
        e_a = abs(d32 / f3)
        out["gci_fine"] = fs * e_a / (ratio ** p - 1.0)
    return out


# ===========================================================================
# GRADING
# ===========================================================================
def level_dir(name):
    return os.path.join(RUN_ROOT, name)


def strict_completion(name):
    """CLAUDE.md rule 4 -- every clause, refuse (exit 2) on any failure."""
    d = level_dir(name)
    c = {}
    rcf = os.path.join(d, "RUN_RC.txt")
    if not os.path.exists(rcf):
        refuse("C1", "%s: RUN_RC.txt missing" % name)
    rc_txt = open(rcf).read()
    m = re.search(r"rc\s*=\s*(-?\d+)", rc_txt)
    if not m:
        refuse("C1", "%s: no rc= line in RUN_RC.txt" % name)
    c["rc"] = int(m.group(1))
    if c["rc"] != 0:
        refuse("C1", "%s: rc = %d" % (name, c["rc"]))

    log = os.path.join(d, "log.simpleFoam")
    if not os.path.exists(log):
        refuse("C2", "%s: log.simpleFoam missing" % name)
    txt = open(log).read()

    if not re.search(r"^End\s*$", txt, re.M):
        refuse("C2", "%s: no End line" % name)
    c["end_line"] = True

    times = [int(t) for t in re.findall(r"^Time = (\d+)\s*$", txt, re.M)]
    if not times:
        refuse("C3", "%s: no Time = lines" % name)
    c["last_time"] = times[-1]
    if c["last_time"] != ENDTIME:
        refuse("C3", "%s: last time %d != endTime %d" % (name, c["last_time"], ENDTIME))

    c["execution_time_count"] = len(re.findall(r"^ExecutionTime = ", txt, re.M))
    if c["execution_time_count"] != ENDTIME:
        refuse("C4", "%s: %d ExecutionTime lines != endTime %d"
               % (name, c["execution_time_count"], ENDTIME))

    end_dir = os.path.join(d, str(ENDTIME))
    if not os.path.isdir(end_dir):
        refuse("C5", "%s: no %d/ directory" % (name, ENDTIME))
    missing = [f for f in REQUIRED_FIELDS if not os.path.exists(os.path.join(end_dir, f))]
    if missing:
        refuse("C5", "%s: fields missing at endTime: %s" % (name, missing))
    c["fields"] = list(REQUIRED_FIELDS)

    # THE AGE GUARD.  0/U is touched LAST at launch, so it dates the run that
    # was allowed to produce the answer.  Every endTime field must be NEWER.
    marker = os.path.join(d, AGE_MARKER)
    if not os.path.exists(marker):
        refuse("C6", "%s: age marker %s missing" % (name, AGE_MARKER))
    t0 = os.path.getmtime(marker)
    ages = {}
    for f in REQUIRED_FIELDS:
        tf = os.path.getmtime(os.path.join(end_dir, f))
        ages[f] = tf - t0
        if tf <= t0:
            refuse("C6", "%s: %d/%s is NOT newer than %s (delta %.3f s)"
                   % (name, ENDTIME, f, AGE_MARKER, tf - t0))
    c["age_guard_deltas_s"] = ages

    # MONITOR_STANDARD S8 EXEMPTION, MEASURED RATHER THAN CLAIMED.  A steady
    # SIMPLE run prints no Courant number at all, so S8 has nothing to read.
    # That is asserted against the artifact, not assumed from the solver name.
    c["courant_lines"] = len(re.findall(r"Courant Number", txt))
    if c["courant_lines"] != 0:
        refuse("C7", "%s: %d 'Courant Number' lines in a STEADY run -- S8 applies "
                     "and this comparator does not read it"
               % (name, c["courant_lines"]))

    # ---- the SETUP asserts: WHICH powerLaw class actually ran ----
    if "Selecting incompressible transport model powerLaw" not in txt:
        refuse("S1", "%s: log does not say 'Selecting incompressible transport "
                     "model powerLaw' -- the transport model is not class A" % name)
    if "Selecting laminar stress model Stokes" not in txt:
        refuse("S2", "%s: log does not say 'Selecting laminar stress model Stokes'" % name)
    if "generalizedNewtonian" in txt:
        refuse("S2", "%s: 'generalizedNewtonian' appears in the log -- the WRONG "
                     "powerLaw class (no `k` key, nu0 from the transport model) "
                     "was instantiated" % name)
    c["transport_model"] = "viscosityModels::powerLaw (class A, keys k/n/nuMin/nuMax)"
    c["laminar_model"] = "Stokes (nuEff == nu() from the transport model)"

    # the dictionary this run actually consumed
    tp = os.path.join(d, "constant", "transportProperties")
    if not os.path.exists(tp):
        refuse("S3", "%s: constant/transportProperties missing" % name)
    tptxt = open(tp).read()
    got_k = re.search(r"^\s*k\s+([-+0-9.eE]+)\s*;", tptxt, re.M)
    got_n = re.search(r"^\s*n\s+([-+0-9.eE]+)\s*;", tptxt, re.M)
    if not got_k or not got_n:
        refuse("S3", "%s: k or n absent from transportProperties" % name)
    c["k_dict"] = float(got_k.group(1))
    c["n_dict"] = float(got_n.group(1))
    if abs(c["k_dict"] - K_OF_FROZEN) > 1e-15:
        refuse("S3", "%s: transportProperties k = %r, expected the KINEMATIC "
                     "k/rho = %r (the manual's k = %g is DYNAMIC; using it raw "
                     "inflates dp by 1000^n = 15.85x)"
               % (name, c["k_dict"], K_OF_FROZEN, K_DYN))
    if abs(c["n_dict"] - N_IDX) > 1e-15:
        refuse("S3", "%s: transportProperties n = %r != %r" % (name, c["n_dict"], N_IDX))
    if "transportModel" not in tptxt or "powerLaw" not in tptxt:
        refuse("S3", "%s: transportProperties does not select powerLaw" % name)
    return c


def convergence(name, dp_series, dp_range):
    """Iterative convergence: the S13-form plateau (primary) + a residual backstop."""
    d = level_dir(name)
    txt = open(os.path.join(d, "log.simpleFoam")).read()
    out = {}

    # --- residual backstop: the LAST initial residual of each equation ---
    ux = re.findall(r"Solving for Ux, Initial residual = ([-+0-9.eE]+)", txt)
    pr = re.findall(r"Solving for p, Initial residual = ([-+0-9.eE]+)", txt)
    if not ux or not pr:
        refuse("V1", "%s: no residual lines in the log" % name)
    out["resid_Ux_final"] = float(ux[-1])
    out["resid_p_final"] = float(pr[-1])
    if out["resid_Ux_final"] > RESID_UX_MAX:
        refuse("V1", "%s: final Ux initial residual %.6e > %.1e"
               % (name, out["resid_Ux_final"], RESID_UX_MAX))
    if out["resid_p_final"] > RESID_P_MAX:
        refuse("V1", "%s: final p initial residual %.6e > %.1e"
               % (name, out["resid_p_final"], RESID_P_MAX))

    # --- the plateau, MONITOR_STANDARD S13 1.12 form ---
    lo = ENDTIME - PLATEAU_WINDOW
    win = [(it, v) for (it, v) in dp_series
           if it > lo and (it - lo) % PLATEAU_STRIDE == 0]
    out["plateau_samples"] = len(win)
    if len(win) < PLATEAU_MIN_SAMPLES:
        refuse("V2", "%s: %d plateau samples < %d -- CANNOT_TELL, never a pass"
               % (name, len(win), PLATEAU_MIN_SAMPLES))
    vals = [v for (_, v) in win]
    ptp = max(vals) - min(vals)
    out["plateau_ptp_Pa"] = ptp
    out["run_range_Pa"] = dp_range
    # S13's null-variation clause, in its CORRECTED 1.12 form: a quantity that
    # never resolvably MOVED is CANNOT_TELL, never a pass.
    if dp_range < PLATEAU_NULL_RANGE_PA:
        refuse("V2", "%s: the graded series spanned only %.6e Pa over the whole "
                     "run -- it never resolvably moved; CANNOT_TELL, never a pass"
               % (name, dp_range))
    out["plateau_frac_of_range"] = ptp / dp_range
    if out["plateau_frac_of_range"] > PLATEAU_TOL_FRAC_OF_RANGE:
        refuse("V2", "%s: plateau peak-to-peak %.6e Pa is %.6f %% of the range the "
                     "series spanned (%.6e Pa), above %.4f %%"
               % (name, ptp, 100 * out["plateau_frac_of_range"], dp_range,
                  100 * PLATEAU_TOL_FRAC_OF_RANGE))
    return out


def setup_asserts(name, comp):
    """The asserts that prove WHICH model ran and that no clip bound."""
    d = level_dir(name)
    pp = os.path.join(d, "postProcessing")
    out = {}

    # inlet patch area == the flat-wedge formula (N-AV9, measured not assumed)
    q = read_fo_dat(os.path.join(pp, "QInlet", "0", "surfaceFieldValue.dat"))
    if q["area"] is None:
        refuse("S4", "%s: QInlet monitor carries no Area header" % name)
    out["inlet_area_m2"] = q["area"]
    rel = abs(q["area"] - WEDGE_PATCH_AREA) / WEDGE_PATCH_AREA
    out["inlet_area_rel_dev"] = rel
    if rel > WEDGE_PATCH_AREA_TOL:
        refuse("S4", "%s: inlet area %.15e != flat-wedge 0.5 R^2 sin(t) = %.15e "
                     "(rel %.3e)" % (name, q["area"], WEDGE_PATCH_AREA, rel))

    # the inlet profile: MEAN (sum(phi)) and SHAPE (max Ux)
    row = series_at(q, ENDTIME)
    out["Q_inlet_m3s"] = row[1]
    q_pred = V_MEAN * q["area"]
    out["Q_rel_dev"] = abs(abs(row[1]) - q_pred) / q_pred
    if out["Q_rel_dev"] > Q_REL_TOL:
        refuse("S5", "%s: inlet volumetric flow |%.9e| deviates %.4f %% from "
                     "V*A = %.9e -- the mean is not 2 m/s"
               % (name, row[1], 100 * out["Q_rel_dev"], q_pred))
    um = read_fo_dat(os.path.join(pp, "UmaxInlet", "0", "surfaceFieldValue.dat"))
    urow = series_at(um, ENDTIME)
    out["Umax_inlet_x"] = urow[1]
    if not (UMAX_BAND[0] <= urow[1] <= UMAX_BAND[1]):
        refuse("S5", "%s: max inlet Ux = %.9f outside %r -- the fully developed "
                     "power-law profile (peak %.9f) was NOT applied; a UNIFORM "
                     "%g m/s inlet reads %g and is what this clause exists to catch"
               % (name, urow[1], UMAX_BAND, U_MAX_PROFILE, V_MEAN, V_MEAN))

    # WHICH powerLaw class, read off the VISCOSITY FIELD rather than the log
    nmin = read_fo_dat(os.path.join(pp, "nuMinAll", "0", "volFieldValue.dat"))
    nmax = read_fo_dat(os.path.join(pp, "nuMaxAll", "0", "volFieldValue.dat"))
    out["nu_min"] = series_at(nmin, ENDTIME)[1]
    out["nu_max"] = series_at(nmax, ENDTIME)[1]
    if not (NU_MIN_BAND[0] <= out["nu_min"] <= NU_MIN_BAND[1]):
        refuse("S6", "%s: min(nu) = %.9e outside %r.  The continuum wall value "
                     "for k_OF = %g is %.9e; the WRONG powerLaw class seeded "
                     "from a Newtonian nu0 = 1e-05 would read ~%.3e."
               % (name, out["nu_min"], NU_MIN_BAND, K_OF_FROZEN,
                  NU_WALL_EXACT, NU_MIN_IF_WRONG_CLASS))
    # the clips must never have bound -- the archive runs with BOTH Fluent
    # viscosity limits set to zero (`non-newtonian-power-law 10 0.4 0 0`)
    if out["nu_max"] >= NU_MAX_CEILING:
        refuse("S7", "%s: max(nu) = %.9e is at or above %.3e -- the nuMax = %g "
                     "clip is in play and this run departs from the archive, "
                     "which disables both viscosity limits"
               % (name, out["nu_max"], NU_MAX_CEILING, NU_MAX_DICT))
    if out["nu_min"] <= NU_MIN_DICT * 10:
        refuse("S7", "%s: min(nu) = %.9e is within 10x of the nuMin = %g clip"
               % (name, out["nu_min"], NU_MIN_DICT))
    out["clips_bound"] = False
    return out


def gate_series(name):
    """dp_Pa as a function of iteration, from the two patch monitors."""
    d = level_dir(name)
    pp = os.path.join(d, "postProcessing")
    pin = read_fo_dat(os.path.join(pp, "pInlet", "0", "surfaceFieldValue.dat"))
    pout = read_fo_dat(os.path.join(pp, "pOutlet", "0", "surfaceFieldValue.dat"))
    bo = {int(round(r[0])): r[1] for r in pout["rows"]}
    ser = []
    for r in pin["rows"]:
        it = int(round(r[0]))
        if it in bo:
            ser.append((it, RHO * (r[1] - bo[it])))   # <-- the p/rho conversion
    if not ser:
        refuse("R1", "%s: inlet and outlet monitors share no iteration" % name)
    return ser, pin, pout


def control_pz1(name):
    """PLANT into a COPY of the gate .dat, read it back FROM DISK."""
    src = os.path.join(level_dir(name), "postProcessing", "pInlet", "0",
                       "surfaceFieldValue.dat")
    tmp = tempfile.mkdtemp(prefix="vmfl007_pz1_")
    try:
        dst = os.path.join(tmp, "surfaceFieldValue.dat")
        before = read_fo_dat(src)["rows"][-1][1]
        plant_into_dat(src, dst, PLANT_DAT, 1)
        after = read_fo_dat(dst)["rows"][-1][1]
        seen = after - before
        if abs(seen - PLANT_DAT) > PLANT_DAT_TOL:
            refuse("PZ1", "the .dat reader could not see a planted %.6e "
                          "(read back %.6e) -- it has produced no number"
                   % (PLANT_DAT, seen))
        return {"planted": PLANT_DAT, "seen": seen, "fired": True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_pz2(name):
    """PLANT into a COPY of the endTime nu field, read it back FROM DISK."""
    src = os.path.join(level_dir(name), str(ENDTIME), "nu")
    tmp = tempfile.mkdtemp(prefix="vmfl007_pz2_")
    try:
        dst = os.path.join(tmp, "nu")
        before = read_foam_scalar_field(src)[0]
        plant_into_scalar_field(src, dst, PLANT_FIELD)
        after = read_foam_scalar_field(dst)[0]
        seen = after - before
        if abs(seen - PLANT_FIELD) > PLANT_FIELD_TOL:
            refuse("PZ2", "the field reader could not see a planted %.6e "
                          "(read back %.6e)" % (PLANT_FIELD, seen))
        return {"planted": PLANT_FIELD, "seen": seen, "fired": True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_pz3():
    """PLANT into the ARITHMETIC: the gate must FAIL a wrong value, and a
    non-converging triple must yield NO GCI.  A gate that cannot fail is not
    a gate."""
    out = {}
    wrong = MANUAL_TARGET * (1.0 + 2.0 * TOL_GATE)
    out["wrong_value_Pa"] = wrong
    out["wrong_value_rejected"] = abs(wrong - MANUAL_TARGET) / MANUAL_TARGET > TOL_GATE
    if not out["wrong_value_rejected"]:
        refuse("PZ3", "a value %.1f Pa (2x the tolerance out) did NOT fail the gate"
               % wrong)
    # the WRONG viscosity class, as a real negative arm
    dp_wrong_class = DP_EXACT_FROZEN * (1e-05 / K_OF_FROZEN) ** N_IDX
    out["wrong_class_Pa"] = dp_wrong_class
    if abs(dp_wrong_class - MANUAL_TARGET) / MANUAL_TARGET <= TOL_GATE:
        refuse("PZ3", "the WRONG powerLaw class (%.1f Pa) would PASS the gate"
               % dp_wrong_class)
    dp_unconverted = DP_EXACT_FROZEN * (1000.0 ** N_IDX)
    out["unconverted_k_Pa"] = dp_unconverted
    if abs(dp_unconverted - MANUAL_TARGET) / MANUAL_TARGET <= TOL_GATE:
        refuse("PZ3", "an UNCONVERTED k (%.1f Pa) would PASS the gate" % dp_unconverted)
    r = roache(1.0, 1.2, 1.0)
    out["nonconverging_gci_is_none"] = r["gci_fine"] is None
    if r["gci_fine"] is not None:
        refuse("PZ3", "a non-converging triple produced a GCI of %r" % r["gci_fine"])
    out["fired"] = True
    return out


def grade():
    res = {"case": "VMFL007",
           "title": "Non-Newtonian Flow in a Pipe",
           "manual_page": MANUAL_PAGE,
           "manual_reference": MANUAL_REFERENCE,
           "reference_kind": REFERENCE_KIND,
           "tier_ceiling": TIER_CEILING,
           "manual_target_Pa": MANUAL_TARGET,
           "ansys_context": ANSYS_CONTEXT,
           "closed_form": {"tau_w_Pa": TAU_W, "dp_Pa": DP_EXACT,
                           "Re_generalised": RE_GEN,
                           "dp_Pa_frozen": DP_EXACT_FROZEN,
                           "dp_wedge_corrected_Pa": DP_EXACT_WEDGE},
           "wedge_bias": {"total_angle_deg": WEDGE_TOTAL_DEG,
                          "area_ratio_sin_t_over_t": WEDGE_AREA_RATIO,
                          "arc_ratio": WEDGE_ARC_RATIO,
                          "dp_bias_sec_half_t_minus_1": WEDGE_DP_BIAS,
                          "dp_bias_pct": 100 * WEDGE_DP_BIAS,
                          "sign": "HIGH -- the modelled dp is biased UP",
                          "removable_by_refinement": False},
           "gate": {"tol": TOL_GATE, "reference_Pa": MANUAL_TARGET,
                    "band_Pa": [MANUAL_TARGET * (1 - TOL_GATE),
                                MANUAL_TARGET * (1 + TOL_GATE)]},
           "levels": {}}

    # the closed form must not have drifted from the frozen constants
    if abs(TAU_W - TAU_W_FROZEN) > 1e-9 or abs(DP_EXACT - DP_EXACT_FROZEN) > 1e-6:
        refuse("F1", "closed_form() no longer reproduces the frozen constants")
    if abs(WEDGE_DP_BIAS - WEDGE_DP_BIAS_FROZEN) > 1e-15:
        refuse("F1", "the wedge bias no longer reproduces its frozen constant")

    vals = []
    for (name, nx, nr, cells) in LEVELS:
        lv = {"nx": nx, "nr": nr, "cells": cells}
        lv["completion"] = strict_completion(name)
        ser, pin, pout = gate_series(name)
        allv = [v for (_, v) in ser]
        rng = max(allv) - min(allv)
        lv["convergence"] = convergence(name, ser, rng)
        lv["setup"] = setup_asserts(name, lv["completion"])
        dp = dict(ser)[ENDTIME]
        lv["dp_Pa"] = dp
        lv["dev_vs_manual_pct"] = 100 * (dp - MANUAL_TARGET) / MANUAL_TARGET
        lv["dev_vs_exact_pct"] = 100 * (dp - DP_EXACT_FROZEN) / DP_EXACT_FROZEN
        lv["dev_vs_exact_wedge_pct"] = 100 * (dp - DP_EXACT_WEDGE) / DP_EXACT_WEDGE
        res["levels"][name] = lv
        vals.append(dp)

    res["controls"] = {"PZ1": control_pz1(GATE_LEVEL),
                       "PZ2": control_pz2(GATE_LEVEL),
                       "PZ3": control_pz3()}

    tri = roache(vals[0], vals[1], vals[2])
    res["roache"] = tri
    if tri["order"] is not None:
        tri["order_expected_band"] = list(ORDER_EXPECTED)
        tri["order_formal"] = ORDER_FORMAL
        tri["order_suspicious"] = tri["order"] > ORDER_SUSPICIOUS_ABOVE
        tri["order_below_expected"] = tri["order"] < ORDER_EXPECTED[0]

    dp_gate = res["levels"][GATE_LEVEL]["dp_Pa"]
    res["graded_level"] = GATE_LEVEL
    res["graded_value_Pa"] = dp_gate
    rel = abs(dp_gate - MANUAL_TARGET) / MANUAL_TARGET
    res["gate"]["deviation_rel"] = rel
    res["gate"]["deviation_pct"] = 100 * (dp_gate - MANUAL_TARGET) / MANUAL_TARGET
    res["gate"]["inside"] = rel <= TOL_GATE

    # DIAGNOSTICS, never the gate.
    d1 = abs(dp_gate - DP_EXACT_FROZEN) / DP_EXACT_FROZEN
    d2 = abs(dp_gate - DP_EXACT_WEDGE) / DP_EXACT_WEDGE
    res["diagnostics"] = {
        "D1_vs_exact": {"reference_Pa": DP_EXACT_FROZEN, "tol": TOL_DIAG_EXACT,
                        "deviation_rel": d1, "inside": d1 <= TOL_DIAG_EXACT,
                        "role": "DIAGNOSTIC ONLY -- never the gate"},
        "D2_vs_exact_wedge_corrected": {
            "reference_Pa": DP_EXACT_WEDGE, "tol": TOL_DIAG_WEDGE,
            "deviation_rel": d2, "inside": d2 <= TOL_DIAG_WEDGE,
            "role": "DIAGNOSTIC ONLY -- isolates DISCRETISATION from the known "
                    "azimuthal wedge bias, which no refinement removes"},
    }

    # ---- THE VERDICT.  Rule 5 order: the triple can only turn a PASS or a
    # GATE FAIL INTO NOT A RESULT, never the reverse. ----
    if tri["state"] != "CONVERGING":
        res["verdict"] = "NOT A RESULT"
        res["verdict_reason"] = ("grid triple is %s, not CONVERGING (rule 5 step 2)"
                                 % tri["state"])
    else:
        res["verdict"] = "PASS" if res["gate"]["inside"] else "GATE FAIL"
        res["verdict_reason"] = (
            "triple CONVERGING at observed order %.6f, GCI_fine %.6f %%; "
            "gate %s" % (tri["order"], 100 * (tri["gci_fine"] or 0.0),
                         "met" if res["gate"]["inside"] else "MISSED"))
    if res["verdict"] not in VERDICTS:
        refuse("Z1", "verdict %r is outside the fixed vocabulary" % res["verdict"])

    # V column: earned only if the extrapolate lands ON the exact solution
    # (N-AV7 -- a small GCI does NOT license it).
    if tri["state"] == "CONVERGING" and tri["extrapolated"] is not None:
        ex = tri["extrapolated"]
        res["V_column"] = {
            "extrapolate_Pa": ex,
            "vs_exact_pct": 100 * (ex - DP_EXACT_FROZEN) / DP_EXACT_FROZEN,
            "vs_exact_wedge_pct": 100 * (ex - DP_EXACT_WEDGE) / DP_EXACT_WEDGE,
            "note": "the extrapolate is compared to BOTH the true-circle exact "
                    "value and the wedge-corrected one; the wedge bias is "
                    "azimuthal and survives extrapolation",
        }
    return res


# ===========================================================================
def report(res):
    P = print
    P("=" * 74)
    P("VMFL007 -- Non-Newtonian Flow in a Pipe (manual p. %s)" % MANUAL_PAGE)
    P("=" * 74)
    P("reference kind : %s" % res["reference_kind"])
    P("tier ceiling   : %s   (P column unavailable for a closed-form reference)"
      % res["tier_ceiling"])
    P("manual target  : %.1f Pa (60.52 kPa, printed to 4 figures, +/- %.1f Pa)"
      % (MANUAL_TARGET, MANUAL_TARGET_HALFWIDTH))
    P("closed form    : %.10f Pa   (tau_w = %.10f Pa, Re_gen = %.6f)"
      % (res["closed_form"]["dp_Pa"], res["closed_form"]["tau_w_Pa"],
         res["closed_form"]["Re_generalised"]))
    P("wedge bias     : %+.10f %% HIGH, sec(t/2)-1 at t = %.1f deg -- AZIMUTHAL, "
      "no refinement removes it" % (res["wedge_bias"]["dp_bias_pct"],
                                    res["wedge_bias"]["total_angle_deg"]))
    P("")
    P("%-12s %7s %16s %12s %12s %12s" %
      ("level", "cells", "dp (Pa)", "vs manual", "vs exact", "vs wedge-exact"))
    for (name, nx, nr, cells) in LEVELS:
        lv = res["levels"][name]
        P("%-12s %7d %16.6f %11.5f%% %11.5f%% %11.5f%%" %
          (name, cells, lv["dp_Pa"], lv["dev_vs_manual_pct"],
           lv["dev_vs_exact_pct"], lv["dev_vs_exact_wedge_pct"]))
    P("")
    t = res["roache"]
    P("Roache triple  : %s   ratio %.1f   Fs %.2f" % (t["state"], RATIO, FS))
    if t["order"] is not None:
        flag = ""
        if t.get("order_suspicious"):
            flag = "   <-- SUSPICIOUS: ABOVE the formal order %.1f, so the triple " \
                   "is NOT asymptotic and this GCI bounds nothing" % ORDER_FORMAL
        elif t.get("order_below_expected"):
            flag = "   <-- below the declared band; the axis viscosity " \
                   "singularity nu ~ r^-1.5 is the named candidate"
        P("  observed order p = %.6f (declared band %r, formal %.1f)%s"
          % (t["order"], list(ORDER_EXPECTED), ORDER_FORMAL, flag))
        P("  GCI_fine = %.6f %%   extrapolate = %.6f Pa"
          % (100 * t["gci_fine"], t["extrapolated"]))
    else:
        P("  no GCI is quoted: the triple is not CONVERGING")
    P("")
    for k in ("PZ1", "PZ2", "PZ3"):
        P("control %s     : FIRED" % k)
    P("")
    g = res["gate"]
    P("GATE           : |dp - %.1f| / %.1f <= %.4f   band [%.2f, %.2f] Pa"
      % (MANUAL_TARGET, MANUAL_TARGET, TOL_GATE, g["band_Pa"][0], g["band_Pa"][1]))
    P("  graded level %s  dp = %.6f Pa   deviation %+.6f %%"
      % (res["graded_level"], res["graded_value_Pa"], g["deviation_pct"]))
    for k, d in res["diagnostics"].items():
        P("  %-32s dev %+.6f %%  tol %.4f %%  %s  [%s]"
          % (k, 100 * d["deviation_rel"], 100 * d["tol"],
             "inside" if d["inside"] else "OUTSIDE", d["role"]))
    P("")
    P("VERDICT        : %s" % res["verdict"])
    P("  %s" % res["verdict_reason"])
    P("=" * 74)


def verify_frozen(commitish):
    """Hash this file against the committed blob (CLAUDE.md rule 2)."""
    with open(os.path.abspath(__file__), "rb") as fh:
        disk = fh.read()
    try:
        blob = subprocess.check_output(
            ["git", "-C", REPO, "cat-file", "blob", "%s:%s" % (commitish, SELF_REL)])
    except subprocess.CalledProcessError as e:
        print("REFUSE: cannot read %s:%s -- %s" % (commitish, SELF_REL, e),
              file=sys.stderr)
        return 2
    if disk != blob:
        print("REFUSE: the file on disk is NOT the file committed at %s" % commitish,
              file=sys.stderr)
        return 2
    print("frozen OK: %s == %s:%s (%d bytes)" % (SELF_REL, commitish, SELF_REL, len(disk)))
    return 0


# ===========================================================================
def selftest():
    ok = [0]
    bad = [0]

    def check(what, cond, extra=""):
        if cond:
            ok[0] += 1
            print("  ok   %s %s" % (what, extra))
        else:
            bad[0] += 1
            print("  FAIL %s %s" % (what, extra))

    print("[A] the repo root is derived, not hardcoded, and is CHECKED")
    check("REPO came from git rev-parse --show-toplevel", os.path.isdir(REPO), REPO)
    check("this file really is at %s inside it" % SELF_REL,
          os.path.samefile(os.path.join(REPO, SELF_REL), os.path.abspath(__file__)))
    # The header comment QUOTES the defect it fixes, so a naive substring test
    # flags this file for describing the bug.  The real property is that no
    # EXECUTABLE line carries a hardcoded root.
    _bad = "/home/" + "ubuntu/Certonomous"
    _code = [ln for ln in open(os.path.abspath(__file__)).read().splitlines()
             if _bad in ln and not ln.lstrip().startswith("#")]
    check("no hardcoded absolute repo path on any EXECUTABLE line",
          not _code, "%d code lines carry one" % len(_code))

    print("")
    print("[B] the closed form, re-derived against the frozen constants")
    check("tau_w", abs(TAU_W - TAU_W_FROZEN) < 1e-9, "%.10f Pa" % TAU_W)
    check("dp exact", abs(DP_EXACT - DP_EXACT_FROZEN) < 1e-6, "%.10f Pa" % DP_EXACT)
    check("Re generalised", abs(RE_GEN - RE_GEN_FROZEN) < 1e-9, "%.8f" % RE_GEN)
    check("the manual's printed 60.52 kPa is the exact answer to 4 figures",
          abs(DP_EXACT - MANUAL_TARGET) / MANUAL_TARGET < 1e-4,
          "%+.7f %%" % (100 * (DP_EXACT - MANUAL_TARGET) / MANUAL_TARGET))
    check("the flow is firmly laminar", RE_GEN < 2100, "Re_gen = %.4f" % RE_GEN)

    print("")
    print("[C] the wedge bias -- sec(t/2)-1, NOT sin(t)/t")
    check("dp bias is sec(t/2)-1", abs(WEDGE_DP_BIAS - WEDGE_DP_BIAS_FROZEN) < 1e-18,
          "%+.10f %%" % (100 * WEDGE_DP_BIAS))
    check("it is NOT the area deficit", abs(WEDGE_DP_BIAS - (1 - WEDGE_AREA_RATIO)) > 1e-8,
          "area deficit is %.10f %%" % (100 * (1 - WEDGE_AREA_RATIO)))
    check("bias = arc deficit / area deficit ratio, to machine precision",
          abs(WEDGE_ARC_RATIO / WEDGE_AREA_RATIO - (1 + WEDGE_DP_BIAS)) < 1e-15)
    check("the bias sits BELOW the reference's own rounding half-width",
          WEDGE_DP_BIAS < MANUAL_TARGET_HALFWIDTH / MANUAL_TARGET,
          "%.6f %% < %.6f %%" % (100 * WEDGE_DP_BIAS,
                                 100 * MANUAL_TARGET_HALFWIDTH / MANUAL_TARGET))
    check("at t = 5 deg it would NOT (11.5x the half-width)",
          (1 / math.cos(math.radians(2.5)) - 1) > MANUAL_TARGET_HALFWIDTH / MANUAL_TARGET,
          "%.8f %%" % (100 * (1 / math.cos(math.radians(2.5)) - 1)))
    check("the wedge patch area formula", abs(WEDGE_PATCH_AREA - 1.363469252912774e-08)
          < 1e-22, "%.15e m2" % WEDGE_PATCH_AREA)

    print("")
    print("[D] the unit conversions, both directions")
    check("k_OF = k/rho is KINEMATIC", abs(K_OF - 0.01) < 1e-18, "%g m2/s^(2-n)" % K_OF)
    check("using the manual's k raw inflates dp by 1000^n",
          abs(1000.0 ** N_IDX - 15.848931924611133) < 1e-12,
          "x%.6f -> %.1f Pa" % (1000.0 ** N_IDX, DP_EXACT_FROZEN * 1000.0 ** N_IDX))
    check("the p/rho conversion is rho = %g" % RHO, RHO == 1000.0)

    print("")
    print("[E] the powerLaw class trap -- REAL negative arms")
    dp_b = DP_EXACT_FROZEN * (1e-05 / K_OF_FROZEN) ** N_IDX
    check("the WRONG class (nu0 = 1e-05) gives a WRONG dp",
          abs(dp_b - MANUAL_TARGET) / MANUAL_TARGET > TOL_GATE,
          "%.2f Pa, %+.2f %% -- FAILS the gate" % (dp_b, 100 * (dp_b - MANUAL_TARGET) / MANUAL_TARGET))
    check("and its min(nu) is outside the frozen band",
          not (NU_MIN_BAND[0] <= NU_MIN_IF_WRONG_CLASS <= NU_MIN_BAND[1]),
          "%.4e vs band %r" % (NU_MIN_IF_WRONG_CLASS, NU_MIN_BAND))
    check("the RIGHT class's wall nu IS inside the band",
          NU_MIN_BAND[0] <= NU_WALL_EXACT <= NU_MIN_BAND[1],
          "%.9e" % NU_WALL_EXACT)
    check("a factor of %.0f separates them" % (NU_WALL_EXACT / NU_MIN_IF_WRONG_CLASS),
          NU_WALL_EXACT / NU_MIN_IF_WRONG_CLASS > 100)
    check("an UNCONVERTED k also fails the gate",
          abs(DP_EXACT_FROZEN * 1000.0 ** N_IDX - MANUAL_TARGET) / MANUAL_TARGET > TOL_GATE,
          "%.1f Pa" % (DP_EXACT_FROZEN * 1000.0 ** N_IDX))
    check("a UNIFORM 2 m/s inlet fails the profile-shape clause",
          not (UMAX_BAND[0] <= V_MEAN <= UMAX_BAND[1]),
          "2.0 outside %r; the power-law peak is %.9f" % (UMAX_BAND, U_MAX_PROFILE))
    check("the power-law peak IS inside it",
          UMAX_BAND[0] <= U_MAX_PROFILE <= UMAX_BAND[1])

    print("")
    print("[F] Roache -- every state, and no GCI without CONVERGING")
    check("monotone shrinking -> CONVERGING", roache(1.0, 1.5, 1.75)["state"] == "CONVERGING")
    check("second-order triple recovers p = 2",
          abs(roache(4.0, 1.0, 0.25)["order"] - 2.0) < 1e-12,
          "p = %.14f" % roache(4.0, 1.0, 0.25)["order"])
    check("first-order triple recovers p = 1",
          abs(roache(4.0, 2.0, 1.0)["order"] - 1.0) < 1e-12)
    check("growing differences -> DIVERGENT", roache(1.0, 1.5, 2.5)["state"] == "DIVERGENT")
    check("sign flip -> OSCILLATORY", roache(1.0, 1.5, 1.0)["state"] == "OSCILLATORY")
    check("equal differences -> STAGNANT", roache(1.0, 2.0, 3.0)["state"] == "STAGNANT")
    check("identical values -> EXACT", roache(2.5, 2.5, 2.5)["state"] == "EXACT")
    check("a NON-CONVERGING triple yields NO GCI",
          roache(1.0, 1.5, 2.5)["gci_fine"] is None)
    check("an OSCILLATORY triple yields NO GCI",
          roache(1.0, 1.5, 1.0)["gci_fine"] is None)
    check("an EXACT triple yields NO GCI", roache(2.5, 2.5, 2.5)["gci_fine"] is None)
    hi = roache(64.0, 1.0, 0.015625)
    check("an order ABOVE the formal order is flagged SUSPICIOUS",
          hi["order"] > ORDER_SUSPICIOUS_ABOVE,
          "p = %.4f -> the triple is NOT asymptotic" % hi["order"])

    print("")
    print("[G] the gate, both arms, against real numbers")
    check("the exact closed form PASSES",
          abs(DP_EXACT_FROZEN - MANUAL_TARGET) / MANUAL_TARGET <= TOL_GATE,
          "%+.6f %%" % (100 * (DP_EXACT_FROZEN - MANUAL_TARGET) / MANUAL_TARGET))
    check("the wedge-corrected exact value PASSES",
          abs(DP_EXACT_WEDGE - MANUAL_TARGET) / MANUAL_TARGET <= TOL_GATE,
          "%.4f Pa, %+.6f %%" % (DP_EXACT_WEDGE,
                                 100 * (DP_EXACT_WEDGE - MANUAL_TARGET) / MANUAL_TARGET))
    check("Ansys FLUENT's own reported value PASSES",
          abs(ANSYS_CONTEXT["Fluent_Pa"] - MANUAL_TARGET) / MANUAL_TARGET <= TOL_GATE,
          "%+.4f %%" % (100 * (ANSYS_CONTEXT["Fluent_Pa"] - MANUAL_TARGET) / MANUAL_TARGET))
    check("Ansys CFX's own reported value FAILS -- the gate is NOT a formality",
          abs(ANSYS_CONTEXT["CFX_Pa"] - MANUAL_TARGET) / MANUAL_TARGET > TOL_GATE,
          "%+.4f %%" % (100 * (ANSYS_CONTEXT["CFX_Pa"] - MANUAL_TARGET) / MANUAL_TARGET))
    check("the archive's own stored solution PASSES",
          abs(ANSYS_CONTEXT["archive_srp_inlet_Pa"] - MANUAL_TARGET) / MANUAL_TARGET <= TOL_GATE,
          "%.3f Pa, %+.4f %%" % (ANSYS_CONTEXT["archive_srp_inlet_Pa"],
                                 100 * (ANSYS_CONTEXT["archive_srp_inlet_Pa"] - MANUAL_TARGET) / MANUAL_TARGET))
    edge = MANUAL_TARGET * (1 + TOL_GATE * 1.0001)
    check("a value just outside the band FAILS", abs(edge - MANUAL_TARGET) / MANUAL_TARGET > TOL_GATE,
          "%.2f Pa" % edge)
    edge2 = MANUAL_TARGET * (1 + TOL_GATE * 0.9999)
    check("a value just inside the band PASSES", abs(edge2 - MANUAL_TARGET) / MANUAL_TARGET <= TOL_GATE,
          "%.2f Pa" % edge2)

    print("")
    print("[H] the planted-zero arithmetic control, PZ3")
    try:
        pz3 = control_pz3()
        check("PZ3 fires", pz3["fired"])
    except Refusal as e:
        check("PZ3 fires", False, str(e))

    print("")
    print("[I] the readers -- planting into a COPY and reading it back from DISK")
    tmp = tempfile.mkdtemp(prefix="vmfl007_selftest_")
    try:
        f = os.path.join(tmp, "fake.dat")
        open(f, "w").write(
            "# Region type :     patch inlet\n"
            "# Faces             : 25\n"
            "# Area              : 1.363469252911e-08\n"
            "# Time              \tareaAverage(p)\n"
            "9999\t-6.052196938383e+01\n"
            "10000\t-6.052196938383e+01\n")
        d = read_fo_dat(f)
        check("the .dat reader parses header and rows",
              d["nfaces"] == 25 and len(d["rows"]) == 2 and
              abs(d["area"] - 1.363469252911e-08) < 1e-20)
        g = os.path.join(tmp, "planted.dat")
        plant_into_dat(f, g, PLANT_DAT, 1)
        seen = read_fo_dat(g)["rows"][-1][1] - d["rows"][-1][1]
        check("a planted %.4e is SEEN by the .dat reader" % PLANT_DAT,
              abs(seen - PLANT_DAT) < PLANT_DAT_TOL, "read back %.6e" % seen)
        # a reader that CANNOT see the plant must be caught
        h = os.path.join(tmp, "unplanted.dat")
        shutil.copy(f, h)
        seen0 = read_fo_dat(h)["rows"][-1][1] - d["rows"][-1][1]
        check("an UNPLANTED copy reads back 0 -- so the control can fail",
              abs(seen0) < 1e-18 and abs(seen0 - PLANT_DAT) > PLANT_DAT_TOL)

        nf = os.path.join(tmp, "nu")
        open(nf, "w").write(
            "dimensions      [0 2 -1 0 0 0 0];\n\n"
            "internalField   nonuniform List<scalar> \n3\n(\n"
            "4.298435325556426e-05\n1.0e-04\n2.0e-04\n)\n;\n")
        v = read_foam_scalar_field(nf)
        check("the field reader parses a nonuniform list", len(v) == 3 and
              abs(v[0] - 4.298435325556426e-05) < 1e-20)
        nf2 = os.path.join(tmp, "nu_planted")
        plant_into_scalar_field(nf, nf2, PLANT_FIELD)
        v2 = read_foam_scalar_field(nf2)
        check("a planted %.4e is SEEN by the field reader" % PLANT_FIELD,
              abs((v2[0] - v[0]) - PLANT_FIELD) < PLANT_FIELD_TOL,
              "read back %.6e" % (v2[0] - v[0]))
        check("the untouched tail is unchanged", v2[1:] == v[1:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    print("[J] the refusal machinery -- it must actually refuse")
    for what, fn in (
        ("a missing monitor file", lambda: read_fo_dat("/nonexistent/x.dat")),
        ("a missing field file", lambda: read_foam_scalar_field("/nonexistent/nu")),
    ):
        try:
            fn()
            check("%s REFUSES" % what, False, "it did not")
        except Refusal:
            check("%s REFUSES" % what, True)

    print("")
    print("[K] the plateau clause is S13's form, not a fraction of the run")
    check("the window is FIXED, in iterations", isinstance(PLATEAU_WINDOW, int)
          and PLATEAU_WINDOW == 1000)
    check("it yields >= S13's floor of 9 samples",
          PLATEAU_WINDOW // PLATEAU_STRIDE >= PLATEAU_MIN_SAMPLES,
          "%d samples" % (PLATEAU_WINDOW // PLATEAU_STRIDE))
    check("it normalises by the RANGE, not the mean",
          PLATEAU_TOL_FRAC_OF_RANGE == 2.0e-4)
    check("a series that never moved is refused, not passed",
          PLATEAU_NULL_RANGE_PA > 0)

    print("")
    print("[L] the verdict vocabulary and the tier ceiling")
    check("only the six words exist", set(VERDICTS) ==
          {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"})
    check("the tier ceiling is declared in advance", TIER_CEILING == "GATE REACHED")
    check("the reference kind is declared in advance",
          REFERENCE_KIND.startswith("CLOSED-FORM"))

    print("")
    print("selftest: %d ok, %d FAIL" % (ok[0], bad[0]))
    return 0 if bad[0] == 0 else 1


# ===========================================================================
def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--verify-frozen" in argv:
        i = argv.index("--verify-frozen")
        if i + 1 >= len(argv):
            print("REFUSE: --verify-frozen needs a commit-ish", file=sys.stderr)
            return 2
        return verify_frozen(argv[i + 1])
    if "--dryrun-reader" in argv:
        # The PRE-FREEZE reader check (L-286).  It prints STRUCTURE and
        # deliberately NO VALUE, so it cannot leak the answer before the freeze.
        i = argv.index("--dryrun-reader")
        if i + 1 >= len(argv):
            print("REFUSE: --dryrun-reader needs a path", file=sys.stderr)
            return 2
        try:
            d = read_fo_dat(argv[i + 1])
        except Refusal as e:
            print("REFUSE: %s" % e, file=sys.stderr)
            return 2
        print("parsed, %d rows, columns %r, faces %r, cells %r, area %r"
              % (len(d["rows"]), d["cols"], d["nfaces"], d["ncells"], d["area"]))
        return 0
    try:
        res = grade()
    except Refusal as e:
        print("REFUSE: %s" % e, file=sys.stderr)
        return 2
    report(res)
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as fh:
        json.dump(res, fh, indent=2, sort_keys=True, default=str)
    print("grading JSON: %s" % OUT_JSON)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
