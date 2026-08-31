#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VMFL006 -- Multicomponent Species Transport in Pipe Flow.
Ansys Fluid Dynamics Verification Manual, Release 2026 R1, pp. 27-28.

GATE QUANTITY: the MIXING-CUP (mass-weighted) average of the NORMALIZED mass
fraction of species A,  theta = (Y_wall - Y)/(Y_wall - Y_inlet) = (0.9 - Y)/0.4,
at the ten axial stations x = 0.01 ... 0.10 m, read from the solver's own
conserved flux on real mesh faces (surfaceFieldValue, weightedAverage, weightField
phi) -- never interpolated onto a constructed plane and never area-averaged.

REFERENCE: the lab's OWN full-double-precision evaluation of the GRAETZ series
(REF_LAB below; graetz_reference_vmfl006.py), the closed form that
W.M. Kays & M.E. Crawford, "Convective Heat and Mass Transfer", 3rd Ed.,
McGraw-Hill, pp.126-134, 1993 gives and that the manual's Table .06.1 "Target"
column quotes to 4 decimals. THE PRINTED COLUMN IS NOT THE GATE: it is
independent corroboration, printed beside the verdict. Ansys Fluent's own column
is CONTEXT ONLY and is never the gate.

TIER CEILING: **PASS**, per ANSYS_VERIFICATION_CHARTER sec.11.1 (the supervisor's
standing reading, ruled 2026-08-30 on VMFL069 sec.3.3). With equal densities and
viscosities and no reaction the species equation reduces EXACTLY to
div(rho*u*Y) = div(rho*D*grad(Y)), which is what scalarTransportFoam solves, so
the reference is the exact solution of the SAME continuum model the solver
discretises and the residual is DISCRETISATION error. VERIFICATION_CHARTER
sec.2f.3's CONTINUUM cap is the NO-TRIPLE ceiling and does not reach a
registration that declares a Roache triple returning CONVERGING; such a limb is
graded by CLAUDE.md rule 5 step 3. Precedent: register row #46 (VMFL069-R2).

AND THE CONDITION THAT CEILING RESTS ON, MEASURED RATHER THAN ASSUMED: a
TRUNCATED series is an approximation, not an exact solution. The truncation is
bounded at the SMALLEST station, where convergence is slowest -- 5.873210e-21
relative against a 1.0e-02 band, a margin of 1.7e+18. See REF_TRUNC_* below.

WHICH QUANTITY THE MANUAL'S NUMBERS ACTUALLY ARE -- MEASURED, NOT ASSUMED.
The manual's table CAPTION says "Along the Axis"; the manual's own prose one line
above says "the value of species A is the mass-weighted average of the normalized
species mass fraction A at x-locations". Those are two different quantities. The
lab evaluated the Graetz series itself, twice, by two independent instruments,
and the printed targets are the MIXING-CUP MEAN to a worst 0.048 % and differ
from the true ON-AXIS value by up to 78.5 %. The prose is right and the caption
is wrong; the gate is therefore the mixing cup. Full record:
PREREGISTRATION.md sec.3.

TWO FIELD CLASSES (Sanaa's universal rule, 2026-08-26, commit d4d0c29d; L-342:
"a bookkeeping failure invalidates the bookkeeping, never the physics artifacts").

  PHYSICS-CRITICAL -- these decide the verdict and REFUSE (exit 2) when violated:
      solver rc (from RUN_RC.txt WHEN PRESENT; see below for absent),
      the End line, last time vs endTime, the fields present at endTime,
      the residual/convergence clause, the AGE GUARD, the mesh birth certificate,
      the mixing-cup and flux instruments themselves, the face counts,
      the planted-zero control, the Roache triple and the observed-order floor.
      RUN_RC.txt ABSENT is the one special case: the row becomes NOT A RESULT and
      every physics number is still PRINTED -- it is not a refusal that voids the
      solve, because a missing bookkeeping file is not a broken solve.

  INFRASTRUCTURE -- these are REPORTED and NEVER refuse, never void, never move a
  verdict:  COST.txt, LAUNCH_RECORD.txt, CONTENTION.txt, core-minute figures,
      wall seconds, timeout values, pids/sids, and any mtime used for bookkeeping
      rather than for the age guard. A missing or malformed infrastructure field
      prints "WARNING [INFRA] ..." and grading proceeds on the physics artefacts.

CONTROLS (CLAUDE.md rules 3, 4, 5):
  * planted-zero (rule 3) -- a known perturbation is planted into a COPY of the
    mixing-cup data file, read back FROM DISK by the SAME parser, and the control
    REFUSES (exit 2) from INSIDE itself if the reader cannot see it. Calibrated to
    the reader (L-340): the comparator's gate reader is a SINGLE-VALUE parser on
    one .dat row, so a single-value plant is undiluted and the reader delta equals
    the plant. There is no 1/sqrt(N) averaging step on the comparator side -- the
    mass-weighting happens inside the solver, before the file exists.
  * strict completion (rule 4) -- see completion(); REFUSES rather than grading a
    partial run.
  * convergence -- a FIXED 200-sample window on the solver's own solverInfo.dat,
    with a minimum-iteration refusal, a null-range refusal and a trend test
    (PREREG_TEMPLATE Amendment 4). No fractional window is used anywhere.
  * CONSERVATION / ORIENTATION control -- sum(phi) on every station must equal the
    FLAT-WEDGE analytic flow rate 0.5*sin(5 deg)*R^2*Uavg. A face oriented against
    the flow makes the weighted average silently wrong and this sum wrong with it.
  * Roache triple (rule 5) + OBSERVED-ORDER FLOOR P_MIN (FINDING_p_floor.md sec.4),
    both DRIVEN by planted controls, not merely declared.
  * INFRASTRUCTURE-TOLERANCE control -- a constructed run is graded twice, once
    intact and once with COST.txt deleted and LAUNCH_RECORD.txt corrupted, and the
    verdict must be IDENTICAL; a second plant breaks a PHYSICS field (the End line)
    and must still REFUSE. A rule that is only written down is not a rule.

NO `assert` CARRIES ANY GUARD, REFUSAL, CONTROL OR GATE (PREREG_TEMPLATE
Amendment 6): `python3 -O` strips asserts. Every refusal below is SystemExit2.

Verdict vocabulary only: PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.
"""
import os, re, sys, json, math, shutil, tempfile

HERE     = os.path.dirname(os.path.abspath(__file__))
RUN_ROOT = os.path.join(HERE, "..", "..", "..",
                        "verification", "runs", "ansys_verification", "VMFL006")
LEVELS   = ["L1", "L2", "L3"]
NR_OF    = {"L1": 20, "L2": 40, "L3": 80}
NX_OF    = {"L1": 200, "L2": 400, "L3": 800}

STATIONS = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]

# ============================ THE GATE REFERENCE =============================
# THE GATE IS THE LAB'S OWN EVALUATION OF THE GRAETZ SERIES, TO FULL DOUBLE
# PRECISION -- **NOT** the manual's 4-decimal printed Target column.
#
# WHY THIS AND NOT THE PRINTED COLUMN. The manual's Target column is a 4-decimal
# TRANSCRIPTION of the same closed form. Rounding to 4 dp puts a floor of
# 1.406470e-04 relative (worst station, 5e-5/0.3555) under any comparison against
# it, and a transcribed reference is a quotation, not an exact solution: it is the
# transcription ceiling that capped VMFL002 at GATE REACHED. The lab evaluates the
# series ITSELF, by TWO INDEPENDENT INSTRUMENTS (graetz_reference_vmfl006.py), so
# the reference this comparator gates on is the exact solution of the very
# continuum model scalarTransportFoam discretises.
#
# REF_LAB below is INSTRUMENT B (shooting: vectorised RK4 + brentq).
# It is REPRODUCED AT GRADE TIME by INSTRUMENT A (finite-volume Sturm-Liouville,
# 0.11 s), which shares no code, no discretisation and no library routine with B.
# A disagreement beyond REF_REPRO_TOL REFUSES (exit 2): a frozen constant that no
# live instrument can reproduce is a transcription again, by another route.
REF_LAB  = [0.82218145775507556, 0.7305062043265339,  0.65899626674118539,
            0.59893375759528111, 0.54670065061324469, 0.50036111562132735,
            0.45873436650210847, 0.42103757365934918, 0.38671790452501825,
            0.355363267178404]
REF_KIND = ("ANALYTICAL, EXACT, LAB-EVALUATED -- the Graetz series for the "
            "circular-tube constant-wall-composition problem, evaluated in this "
            "lab to full double precision by two independent instruments. "
            "Kays & Crawford 3rd Ed. pp.126-134 (the source the manual cites).")
REF_REPRO_TOL = 1.0e-05     # measured inter-instrument spread is 2.383599e-06

# The manual's printed Target column (p.28, Table .06.1) -- INDEPENDENT
# CORROBORATION of REF_LAB, printed beside the verdict, NEVER the gate.
MANUAL   = [0.8225, 0.7308, 0.6593, 0.5992, 0.5469,
            0.5006, 0.4589, 0.4212, 0.3869, 0.3555]
MANUAL_ROUNDING_FLOOR = 1.406470e-04   # 5e-5/0.3555: why MANUAL cannot be the gate
# Ansys Fluent's own column (p.28) -- CONTEXT ONLY, never the gate.
FLUENT   = [0.8227, 0.7309, 0.6594, 0.5993, 0.5471,
            0.5007, 0.4591, 0.4215, 0.3872, 0.3557]

# ------------------- THE SERIES TRUNCATION, REGISTERED -----------------------
# The PASS ceiling rests on the reference being EXACT, and a truncated series is
# an approximation. MEASURED at the SMALLEST station x = 0.01 m (tau = 0.01144),
# where the series converges SLOWEST and the truncation is WORST -- not at the
# largest station, where it is best:
#   N_TERMS = 14 (what modes_shoot() uses)
#   first neglected term (n=14)  : 4.812803e-21 absolute
#   full neglected tail n=14..59 : 4.828846e-21 absolute = 5.873210e-21 RELATIVE
#   margin against the band      : 1.7026e+18
# Carrying the series from 14 terms to 60 moves theta_m(x=0.01) from
# 0.8221817279127626 to 0.8221817279127627 -- ONE ULP. The truncation is below
# double precision and is not merely negligible but unrepresentable.
REF_TRUNC_N_TERMS   = 14
REF_TRUNC_REL_WORST = 5.873210e-21          # at x = 0.01 m, the WORST station
REF_INSTRUMENT_SPREAD = 2.383599e-06        # shooting vs finite volume, worst station

Y_IN     = 0.5              # manual p.27
Y_WALL   = 0.9              # manual p.27
TOL      = 0.01             # FROZEN BAND, relative, EVERY station, at L3. sec.6.
PLANT    = 1.234e-03        # planted-zero perturbation
FS       = 1.25             # Roache safety factor
RATIO    = 2.0              # grid refinement ratio
P_MIN    = 0.05             # observed-order floor (FINDING_p_floor.md sec.4)

# ------- GCI CEILING: AN UNCERTAINTY MAY NOT EXCEED THE BAND IT QUALIFIES -----
# A triple can be formally CONVERGING and scientifically useless. This team's own
# record: VMFL063 cleared the P_MIN = 0.05 floor carrying a GCI of 120.62 %, and
# register row #46 limb C carries 145.91 % -- an uncertainty LARGER THAN THE VALUE
# it qualifies, riding inside a PASS. P_MIN is a FLOOR on the observed order and
# cannot catch that; nothing did.
#
# GCI_MAX = TOL is set FROM THE BAND, not from any measured GCI -- no VMFL006
# triple exists at any level above the L1 pre-freeze smoke, and no L2/L3 station
# value has been read by anyone. The reasoning is one sentence: the verdict asserts
# "the lab value lies within TOL of the exact reference", and if the fine-grid
# value's OWN uncertainty exceeds TOL then that assertion is not supported by the
# interval attached to it.
#
# THIS CEILING CAN ONLY TURN A PASS OR A GATE FAIL *INTO* NOT A RESULT, never the
# reverse (CLAUDE.md rule 5). It is STRICTER than any ceiling this team has
# previously carried, and it is registered knowing it may cost this case its row.
GCI_MAX  = 0.01             # == TOL, relative, on the fine-grid GCI at Fs = 1.25
TRIPLE_I = 9                # the Roache triple is taken on station x = 0.10 m

# ---- CLAUSE A (ANSYS_VERIFICATION_CHARTER v1.4): THE WEDGE'S GEOMETRIC BIAS ---
# STATED BEFORE THE FREEZE, WITH ITS SIGN, as the clause requires. No grid
# refinement removes it: it is AZIMUTHAL, so it is invisible to the Roache triple,
# invisible to the GCI, and invisible to every convergence check below.
#
# WHAT DOES **NOT** REACH THIS GATE, and this is the half that is easy to get
# wrong: the mixing cup is a RATIO, sum(phi*T)/sum(phi). On a flat wedge the
# azimuthal area factor sin(t)/t is CONSTANT in r -- an annulus r1..r2 has flat
# area (r2^2-r1^2)sin(t)/2 against a true (r2^2-r1^2)t/2 -- so it multiplies
# numerator and denominator alike and CANCELS EXACTLY. N-AV9's 0.1268756046250763 %
# AREA deficit therefore biases sum(phi), which the conservation control gates
# against the FLAT value on purpose, and biases the GATE BY EXACTLY ZERO.
#
# WHAT DOES REACH IT is only the arc/area RATIO. Every radial-diffusion face area
# divided by its cell volume is scaled by sec(t/2), so the effective Graetz
# coordinate is tau*sec(t/2) and theta_wedge(x) = theta_true(tau*sec(t/2)).
WEDGE_ANGLE_DEG   = 5.0
WEDGE_AREA_DEFICIT_PCT = 0.1268756046250763   # sin(t)/t   -- CANCELS in the ratio
WEDGE_ARC_DEFICIT_PCT  = 0.0317279607991883   # sin(t/2)/(t/2)
WEDGE_RATIO_BIAS_PCT   = 0.0952685163319922   # sec(t/2)   -- THIS one reaches it
# Bias ON THE GRADED QUANTITY, per station, DERIVED from the reference above.
# SIGN IS NEGATIVE: theta is biased LOW, growing with x.
WEDGE_BIAS_ON_THETA = [-1.2559e-04, -2.0684e-04, -2.8164e-04, -3.5451e-04,
                       -4.2720e-04, -5.0053e-04, -5.7483e-04, -6.5016e-04,
                       -7.2644e-04, -8.0353e-04]
WEDGE_BIAS_WORST = 8.0353e-04       # 0.080353 %, at x = 0.10 m; band margin 12.45x

ENDTIME_EXPECTED = 3000     # frozen iteration count; there is no residualControl
MIN_ITERS        = 1000     # fewer than this -> CANNOT_TELL, never a pass
PLATEAU_WINDOW   = 200      # FIXED window (never a fraction of the run)
RES_FLOOR        = 1.0e-09  # T_initial must be at or below this across the window

# Flat-sided 5 deg wedge: flow rate = 0.5*sin(5 deg)*R^2*Uavg. This is NOT the
# true circular-sector value pi*R^2*(5/360)*Uavg = 2.7270769562411397e-07 -- the
# two differ by exactly sin(t)/t, N-AV9's azimuthal area deficit of 0.1269 %.
WEDGE_FLUX     = 2.7236169608643178e-07
FLUX_REL_TOL   = 1.0e-06


# --- SCRATCH-PATH NORMALISATION -------------------------------------------
# The launcher gates on `cmp` between the python3 and python3 -O --selftest
# outputs: a control that vanishes under -O is not a control (L-332).  A
# RANDOMISED tempdir name breaks that gate for a reason that has nothing to do
# with an interpreter flag, which would make the gate abort at zero compute on a
# healthy instrument -- a false alarm is not a control either.  Every emitted
# message therefore has its scratch root replaced by a fixed token.
# THIS TOUCHES NO CONTROL, NO READER, NO THRESHOLD AND NO VERDICT: it changes
# only the TEXT that a human and the launcher's `cmp` read.
_SCRATCH_RE = re.compile(r"/tmp/(vmfl006_plant_|vmfl006_infra_|st006_)[A-Za-z0-9_]+")


def _norm(msg):
    return _SCRATCH_RE.sub(lambda m: "/tmp/%s<scratch>" % m.group(1), str(msg))


class SystemExit2(SystemExit):
    def __init__(self, msg):
        sys.stderr.write("REFUSED (exit 2): %s\n" % _norm(msg))
        SystemExit.__init__(self, 2)


INFRA_WARNINGS = []


def infra_warn(msg):
    """INFRASTRUCTURE class (L-342). Reported, never fatal, never verdict-moving."""
    line = "WARNING [INFRA]: %s" % _norm(msg)
    INFRA_WARNINGS.append(line)
    print(line)


def theta_of(y):
    """Normalized mass fraction, the quantity the manual's table reports."""
    return (Y_WALL - y) / (Y_WALL - Y_IN)


# ------------------------------------------------------------- THE AST GUARD --
# `python3 -O` STRIPS EVERY `assert`, so a guard written as an assert is a guard
# that vanishes in exactly the mode someone reaches for to make grading faster.
# Writing "no asserts here" in a docstring is a promise; this READS THE BYTES.
def ast_no_assert_guard(path=None, _src=None):
    """REFUSE (exit 2) if any `assert` survives anywhere in the comparator's own
    source. Parses the FILE ON DISK -- never a copy in memory, never a claim.

    `_src` is for the selftest ONLY, which must prove this guard FIRES: a guard
    only ever seen to pass is an unproven guard."""
    import ast
    if _src is None:
        path = path or os.path.abspath(__file__)
        _src = open(path, errors="replace").read()
        where = path
    else:
        where = "<constructed source, selftest>"
    try:
        tree = ast.parse(_src)
    except SyntaxError as e:
        raise SystemExit2("AST GUARD: cannot parse %s (%s) -- an unparseable "
                          "comparator has proved nothing" % (where, e))
    bad = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    if bad:
        raise SystemExit2("AST GUARD FAILED: %d `assert` statement(s) survive in %s "
                          "at line(s) %s. `python3 -O` STRIPS asserts, so a guard "
                          "written as an assert is not a guard (PREREG_TEMPLATE "
                          "Amendment 6)." % (len(bad), where, bad))
    return {"passed": True, "source": where, "assert_nodes": 0,
            "n_ast_nodes": sum(1 for _ in ast.walk(tree))}


# -------------------- THE GATE REFERENCE, REPRODUCED AT GRADE TIME ------------
_REF_LIVE_CACHE = [None]


def reference_reproduction():
    """REFUSE (exit 2) unless the FROZEN REF_LAB is reproduced, at grade time, by
    the OTHER instrument.

    REF_LAB was produced by instrument B (shooting, ~75 s). The live check runs
    instrument A (finite-volume Sturm-Liouville, ~0.11 s), which shares no code, no
    discretisation and no library routine with B. So this is a genuine
    CROSS-INSTRUMENT reproduction of the gate reference and not a self-check: it
    catches a mistyped constant, a bit-rot, or a reference silently edited to fit
    an answer, in a tenth of a second.
    """
    if _REF_LIVE_CACHE[0] is not None:
        return _REF_LIVE_CACHE[0]
    sys.path.insert(0, HERE)
    try:
        import graetz_reference_vmfl006 as G
    except Exception as e:
        raise SystemExit2("cannot import the reference module graetz_reference_vmfl006 "
                          "(%s) -- the gate reference cannot be reproduced, and an "
                          "unreproduced reference is a transcription" % e)
    try:
        lam, I, J = G.modes_fv()
        live = [G.theta_mixcup(G.tau_of_x(x), lam, I, J) for x in STATIONS]
    except Exception as e:
        raise SystemExit2("the reference module failed to evaluate (%s)" % e)
    if len(live) != len(REF_LAB):
        raise SystemExit2("reference reproduction returned %d values, REF_LAB has %d"
                          % (len(live), len(REF_LAB)))
    devs = [abs(live[i] - REF_LAB[i]) / abs(REF_LAB[i]) for i in range(len(REF_LAB))]
    worst = max(devs)
    if worst > REF_REPRO_TOL:
        raise SystemExit2("REFERENCE REPRODUCTION FAILED: the frozen REF_LAB "
                          "(instrument B, shooting) is not reproduced by instrument A "
                          "(finite volume) -- worst relative disagreement %.6e against "
                          "the frozen REF_REPRO_TOL %.3e. A gate reference no live "
                          "instrument can reproduce is a transcription."
                          % (worst, REF_REPRO_TOL))
    out = {"passed": True, "worst_rel_disagreement": worst,
           "tol": REF_REPRO_TOL, "instrument_frozen": "shooting (RK4 + brentq)",
           "instrument_live": "finite-volume Sturm-Liouville (eigh_tridiagonal)",
           "live_values": live}
    _REF_LIVE_CACHE[0] = out
    return out


# ------------- NUMERIC TIME-DIRECTORY SELECTION (L-339), WITH A REFUSAL --------
_TIME_RE = re.compile(r"^[0-9]+(\.[0-9]+)?$")


def pick_time_dir(parent, expect_n=1, what=""):
    """Select a time directory NUMERICALLY, with a CARDINALITY REFUSAL.

    NEVER `sorted(glob(...))[-1]`. Lexicographic ordering puts '900' after '1500'
    and '0.5' after '0.05', so a lexicographic selector reads a HALF-TIME field and
    grades it as the answer. This is not theoretical: register row #46's grading
    record shows `lexicographic_would_have_misread = True` at ALL THREE levels, and
    the numeric selector is the only reason that PASS was not graded on a
    half-time field.

    The CARDINALITY REFUSAL is the second half and is the one a numeric selector
    alone does not give you: this case runs ONE detached solver per level to
    endTime with no restart path, so exactly ONE time directory is expected here.
    More than one means something happened that this comparator does not model --
    a restart, a resumed run, a second launch into the same root -- and picking
    "the newest" of a set you did not expect is a guess. It refuses instead.
    """
    if not os.path.isdir(parent):
        raise SystemExit2("no directory %s (%s)" % (parent, what))
    names = [d for d in os.listdir(parent) if os.path.isdir(os.path.join(parent, d))]
    numeric = [d for d in names if _TIME_RE.match(d)]
    nonnum = sorted(set(names) - set(numeric))
    if not numeric:
        raise SystemExit2("no numeric time directory under %s (%s); entries present: %r"
                          % (parent, what, sorted(names)))
    if len(numeric) != expect_n:
        raise SystemExit2("CARDINALITY REFUSAL under %s (%s): %d numeric time "
                          "directories %r, but exactly %d is expected. This case runs "
                          "one detached solver per level to endTime with no restart "
                          "path; an unexpected set is not something to pick the newest "
                          "of, it is something to refuse."
                          % (parent, what, len(numeric), sorted(numeric), expect_n))
    chosen = max(numeric, key=float)
    lexical = sorted(numeric)[-1]
    rec = {"dir": chosen, "path": os.path.join(parent, chosen),
           "parent": parent, "what": what,
           "numeric_candidates": sorted(numeric, key=float),
           "non_numeric_ignored": nonnum,
           "lexicographic_would_have_picked": lexical,
           "lexicographic_would_have_misread": (lexical != chosen)}
    TIME_DIR_SELECTIONS.append(rec)
    return rec


TIME_DIR_SELECTIONS = []


# ----------------------------------------------------------------- readers ----
def read_sfv(path, want_op, want_field, want_region):
    """Parse ONE surfaceFieldValue .dat file.

    ANCHORED ON THE QUANTITY NAME, never on a shared token (PREREG_TEMPLATE
    Amendment 5 item 3): the header must name the operation, the field AND the
    region, and the data column is taken by NAME from the header, not by
    position and not by 'the last number on the line'.
    """
    if not os.path.exists(path):
        raise SystemExit2("missing instrument file %s" % path)
    lines = [l.rstrip("\n") for l in open(path).read().splitlines()]
    hdr = [l for l in lines if l.startswith("#")]
    dat = [l for l in lines if l and not l.startswith("#")]
    if not dat:
        raise SystemExit2("%s carries a header and NO data row" % path)
    region = None
    faces = None
    weight = None
    for h in hdr:
        m = re.search(r"Region type\s*:\s*(.+?)\s*$", h)
        if m:
            region = m.group(1).strip()
        m = re.search(r"Faces\s*:\s*(\d+)", h)
        if m:
            faces = int(m.group(1))
        m = re.search(r"Weight field\s*:\s*(\S+)", h)
        if m:
            weight = m.group(1).strip()
    if region is None or want_region not in region:
        raise SystemExit2("%s: region header is %r, expected to contain %r"
                          % (path, region, want_region))
    colhdr = [h for h in hdr if "Time" in h and "(" in h]
    if not colhdr:
        raise SystemExit2("%s: no column header naming the quantity" % path)
    cols = [c.strip() for c in colhdr[-1].lstrip("#").split("\t") if c.strip()]
    target = "%s(%s)" % (want_op, want_field)
    if target not in cols:
        raise SystemExit2("%s: column %r is not present; columns are %r"
                          % (path, target, cols))
    idx = cols.index(target)
    fields = [f for f in dat[-1].split("\t") if f.strip()]
    if idx >= len(fields):
        raise SystemExit2("%s: column %d (%s) missing from the last data row"
                          % (path, idx, target))
    return {"value": float(fields[idx]), "faces": faces, "region": region,
            "weight": weight, "n_rows": len(dat), "time": float(fields[0])}


def read_solver_info(level_dir):
    """The solver's OWN residual record, on disk, one row per iteration."""
    base = os.path.join(level_dir, "postProcessing", "residuals")
    if not os.path.isdir(base):
        raise SystemExit2("no postProcessing/residuals in %s -- convergence is "
                          "UNEVALUABLE, and an unevaluable convergence is not a pass"
                          % level_dir)
    # NUMERIC selection with a CARDINALITY REFUSAL (L-339) -- never a sorted glob,
    # and never a silent concatenation of however many directories happen to exist.
    sel = pick_time_dir(base, expect_n=1, what="solverInfo residuals")
    cand = [os.path.join(sel["path"], "solverInfo.dat")]
    if not os.path.exists(cand[0]):
        raise SystemExit2("no solverInfo.dat under %s" % sel["path"])
    rows, cols = [], None
    for p in cand:
        for l in open(p).read().splitlines():
            if l.startswith("#"):
                if "T_initial" in l:
                    cols = [c.strip() for c in l.lstrip("#").split("\t") if c.strip()]
                continue
            f = [x for x in l.split("\t") if x.strip()]
            if f:
                rows.append(f)
    if cols is None or "T_initial" not in cols:
        raise SystemExit2("solverInfo.dat carries no T_initial column")
    i = cols.index("T_initial")
    out = []
    for f in rows:
        if i < len(f):
            try:
                out.append((float(f[0]), float(f[i])))
            except ValueError:
                pass
    if not out:
        raise SystemExit2("solverInfo.dat has no parseable T_initial rows")
    return out


# ---------------------------------------------------------- strict completion --
def completion(level_dir, level):
    """CLAUDE.md rule 4, in the form FROZEN in PREREGISTRATION.md sec.7.

    There is no residualControl in this case, so the literal clause applies:
    last time == endTime, exactly, on every level.  scalarTransportFoam does not
    print an `ExecutionTime` line, so the equivalent iteration-count clause is
    used and is DECLARED here rather than improvised: the number of `Time = `
    lines in the log must equal endTime.

    PHYSICS-CRITICAL, except where marked. Any failed clause REFUSES (exit 2)
    rather than grading a partial run -- with ONE exception required by L-342:
    a MISSING RUN_RC.txt returns rc_unknown, which forces NOT A RESULT while
    still printing every physics number, because a bookkeeping file that was
    never written does not un-run a solver.
    """
    out = {"rc_unknown": False}
    rcf = os.path.join(level_dir, "RUN_RC.txt")
    if not os.path.exists(rcf):
        out["rc"] = None
        out["rc_unknown"] = True
        infra_warn("no RUN_RC.txt in %s -- the SOLVER RC IS UNKNOWN. Under L-342 "
                   "this does not void the physics: the row is NOT A RESULT and every "
                   "physics number below is still printed." % level_dir)
    else:
        # Parse TOLERANTLY (PREREG_TEMPLATE Amendment 5 item 2) and FAIL SAFE:
        # an unparseable record refuses rather than passes.
        m = re.search(r"^\s*rc\s*=\s*(-?\d+)", open(rcf).read(), re.M)
        if not m:
            raise SystemExit2("RUN_RC.txt in %s has no parseable rc line -- failing "
                              "SAFE (rc defaults to refusing, never to 0)" % level_dir)
        out["rc"] = int(m.group(1))
        if out["rc"] != 0:
            raise SystemExit2("rc=%d at %s (124 == the cap fired)" % (out["rc"], level_dir))

    log = os.path.join(level_dir, "log.scalarTransportFoam")   # EXACT name, never a glob
    if not os.path.exists(log):
        raise SystemExit2("no log.scalarTransportFoam in %s" % level_dir)
    lt = open(log, errors="replace").read()
    if lt.count("\nEnd") < 1:
        raise SystemExit2("no End line in %s/log.scalarTransportFoam" % level_dir)
    out["end_line"] = lt.count("\nEnd")

    times = [int(t) for t in re.findall(r"^Time = (\d+)", lt, re.M)]
    if not times:
        raise SystemExit2("%s: log carries no Time lines" % level_dir)
    out["last_time"] = times[-1]
    out["n_time_lines"] = len(times)

    ctl = os.path.join(level_dir, "system", "controlDict")
    if not os.path.exists(ctl):
        raise SystemExit2("no system/controlDict in %s" % level_dir)
    m = re.search(r"^endTime\s+([0-9.eE+-]+)\s*;", open(ctl).read(), re.M)
    if not m:
        raise SystemExit2("%s/system/controlDict has no endTime" % level_dir)
    out["endTime"] = float(m.group(1))
    if abs(out["endTime"] - ENDTIME_EXPECTED) > 1e-9:
        raise SystemExit2("%s ran endTime %g, but the FROZEN endTime is %d"
                          % (level_dir, out["endTime"], ENDTIME_EXPECTED))
    if out["last_time"] != int(out["endTime"]):
        raise SystemExit2("%s last time %d != endTime %d -- the run did not complete"
                          % (level_dir, out["last_time"], int(out["endTime"])))
    if out["n_time_lines"] != out["last_time"]:
        raise SystemExit2("%s: %d Time lines but last time is %d"
                          % (level_dir, out["n_time_lines"], out["last_time"]))

    # ---- NUMERIC TIME-DIRECTORY SELECTION ON THE LEVEL ITSELF (L-339) ----------
    # This is the selection that decides WHICH FIELDS THE GATE IS GRADED ON, so it
    # is the one that must never be lexicographic. Exactly two numeric directories
    # are expected -- the launch marker `0` and the endTime write -- and the chosen
    # one must BE endTime, not merely the largest of whatever is lying about.
    sel_lvl = pick_time_dir(level_dir, expect_n=2, what="%s field time directories" % level)
    out["time_dir_selection"] = sel_lvl
    if float(sel_lvl["dir"]) != float(out["endTime"]):
        raise SystemExit2("%s: the newest numeric time directory is %r but endTime is "
                          "%g -- the gate would be graded on the wrong field set"
                          % (level_dir, sel_lvl["dir"], out["endTime"]))
    if sel_lvl["dir"] != str(out["last_time"]):
        raise SystemExit2("%s: time directory %r disagrees with the log's last Time %d"
                          % (level_dir, sel_lvl["dir"], out["last_time"]))

    t = sel_lvl["dir"]
    out["time_dir"] = t
    for f in ("T", "U", "phi"):
        if not (os.path.exists(os.path.join(level_dir, t, f))
                or os.path.exists(os.path.join(level_dir, t, f + ".gz"))):
            raise SystemExit2("field %s missing at %s/%s (X and X.gz both checked)"
                              % (f, level_dir, t))

    # AGE GUARD -- PHYSICS-CRITICAL. 0/T is touched last at launch, so it dates the
    # run allowed to produce the answer.
    def mt(p):
        for c in (p, p + ".gz"):
            if os.path.exists(c):
                return os.path.getmtime(c)
        raise SystemExit2("cannot stat %s" % p)
    z = mt(os.path.join(level_dir, "0", "T"))
    for f in ("T", "U"):
        if not mt(os.path.join(level_dir, t, f)) > z:
            raise SystemExit2("AGE GUARD: %s/%s/%s is not newer than 0/T"
                              % (level_dir, t, f))
    out["age_guard"] = "fields at endTime newer than 0/T"

    # Mesh birth certificate -- PHYSICS-CRITICAL (MESH_STANDARD sec.6).
    bc = os.path.join(level_dir, "birth_certificate.json")
    if not os.path.exists(bc):
        raise SystemExit2("no birth_certificate.json in %s -- an uncertified mesh "
                          "does not enter a graded run" % level_dir)
    b = json.load(open(bc))
    if not b.get("mesh_ok"):
        raise SystemExit2("%s: checkMesh did not report Mesh OK" % level_dir)
    if b.get("cells") != NX_OF[level] * NR_OF[level]:
        raise SystemExit2("%s: mesh has %s cells, the frozen level is %d x %d = %d"
                          % (level_dir, b.get("cells"), NX_OF[level], NR_OF[level],
                             NX_OF[level] * NR_OF[level]))
    out["birth_certificate"] = {k: b.get(k) for k in
                                ("cells", "mesh_ok", "max_skewness", "max_aspect_ratio",
                                 "max_non_orthogonality", "nx", "nr")}
    return out


def convergence(level_dir):
    """FIXED-window convergence clause (PREREG_TEMPLATE Amendment 4), PHYSICS-CRITICAL.

    1. FIXED window of PLATEAU_WINDOW samples -- never a fraction of the run, so
       the clause cannot silently loosen when endTime or writeInterval changes.
    2. Fewer than MIN_ITERS iterations -> REFUSE (CANNOT_TELL), never a lenient pass.
    3. NULL-RANGE refusal: a series with no variation at all is REFUSED -- a dead
       channel and a converged one look identical to a tolerance.
    4. A statistic that REJECTS A GROWING SERIES: the second half of the window
       must not sit above the first half (in log10), so a climbing residual fails.
    5. The realised sample count is RECORDED (n_window) in the grading artifact.

    L-338: T is the ONLY equation this solver solves. There is no transverse
    velocity and no pressure channel here, so there is no degenerate (near-zero)
    field whose normalized residual is meaningless noise. The clause gates on the
    driven channel and on nothing else, and that is stated, not inferred.
    """
    ser = read_solver_info(level_dir)
    n = len(ser)
    if n < MIN_ITERS:
        raise SystemExit2("%s: %d iterations recorded, fewer than the frozen minimum "
                          "%d -- CANNOT_TELL, never a pass" % (level_dir, n, MIN_ITERS))
    if n < PLATEAU_WINDOW:
        raise SystemExit2("%s: %d samples, fewer than the FIXED window %d"
                          % (level_dir, n, PLATEAU_WINDOW))
    win = [v for _, v in ser[-PLATEAU_WINDOW:]]
    if min(win) <= 0.0:
        raise SystemExit2("%s: a non-positive residual (%g) in the window -- "
                          "unreadable, refused" % (level_dir, min(win)))
    lg = [math.log10(v) for v in win]
    ptp = max(lg) - min(lg)
    if ptp <= 0.0:
        raise SystemExit2("%s: NULL RANGE -- the residual series is exactly flat over "
                          "the last %d iterations; a dead channel and a converged one "
                          "look identical to a tolerance" % (level_dir, PLATEAU_WINDOW))
    h = PLATEAU_WINDOW // 2
    m1 = sum(lg[:h]) / h
    m2 = sum(lg[h:]) / (PLATEAU_WINDOW - h)
    if m2 > m1:
        raise SystemExit2("%s: the residual is GROWING over the fixed window "
                          "(log10 mean %.4f -> %.4f)" % (level_dir, m1, m2))
    worst = max(win)
    if worst > RES_FLOOR:
        raise SystemExit2("%s: max T_initial over the fixed %d-iteration window is %.4g, "
                          "above the FROZEN floor %.4g -- not converged"
                          % (level_dir, PLATEAU_WINDOW, worst, RES_FLOOR))
    return {"n_iters": n, "n_window": PLATEAU_WINDOW, "res_max_in_window": worst,
            "res_final": win[-1], "log10_ptp": ptp, "log10_mean_first_half": m1,
            "log10_mean_second_half": m2, "floor": RES_FLOOR, "channel": "T (the only driven equation)"}


# ---------------------------------------------------------- gate instruments ---
def station_files(level_dir, i):
    tag = "x%02d" % (i + 1)
    base = os.path.join(level_dir, "postProcessing")
    def one(name):
        d = os.path.join(base, name)
        if not os.path.isdir(d):
            raise SystemExit2("no postProcessing/%s in %s" % (name, level_dir))
        # NUMERIC selection with a CARDINALITY REFUSAL (L-339). The previous form
        # here was `sorted(os.listdir(d))` taking the FIRST match, which is a
        # lexicographic selector by another spelling.
        sel = pick_time_dir(d, expect_n=1, what="postProcessing/%s" % name)
        p = os.path.join(sel["path"], "surfaceFieldValue.dat")
        if not os.path.exists(p):
            raise SystemExit2("no surfaceFieldValue.dat under postProcessing/%s/%s"
                              % (name, sel["dir"]))
        return p
    return one("mixCup_" + tag), one("flux_" + tag), tag


def read_station(level_dir, level, i):
    mp, fp, tag = station_files(level_dir, i)
    region = "outlet" if i == len(STATIONS) - 1 else tag
    mc = read_sfv(mp, "weightedAverage", "T", region)
    fx = read_sfv(fp, "sum", "phi", region)
    if mc["weight"] != "phi":
        raise SystemExit2("%s: the mixing cup is weighted by %r, not by phi -- an "
                          "area-weighted average is the WRONG statistic here and is "
                          "78 %% away from the reference" % (mp, ))
    nr = NR_OF[level]
    for nm, d in (("mixCup", mc), ("flux", fx)):
        if d["faces"] != nr:
            raise SystemExit2("%s %s: %s faces on station %s, the level's radial cell "
                              "count is %d -- the zone does not span one cross-section"
                              % (level, nm, d["faces"], tag, nr))
    rel = abs(fx["value"] - WEDGE_FLUX) / WEDGE_FLUX
    if rel > FLUX_REL_TOL:
        raise SystemExit2("%s CONSERVATION/ORIENTATION CONTROL FAILED at %s: sum(phi) = "
                          "%.12e against the flat-wedge analytic %.12e (rel %.3e > %.1e). "
                          "A face oriented against the flow makes the mixing cup silently "
                          "wrong; a mixing cup whose weight sum is wrong is not a number."
                          % (level, tag, fx["value"], WEDGE_FLUX, rel, FLUX_REL_TOL))
    return {"station_m": STATIONS[i], "tag": tag, "Y_mixcup": mc["value"],
            "theta": theta_of(mc["value"]), "flux": fx["value"], "flux_rel_dev": rel,
            "faces": mc["faces"], "region": mc["region"]}


# ------------------------------------------------------- planted-zero control --
def planted_zero(level_dir):
    """CLAUDE.md rule 3, calibrated to the reader (L-340).

    The comparator's gate reader is a SINGLE-VALUE parser on one .dat row, so a
    single-value plant is undiluted and the reader delta equals the plant exactly.
    FALL-THROUGH REFUSAL (PREREG_TEMPLATE Amendment 6a item 2): the only way this
    function RETURNS is to have seen the plant.
    """
    mp, _, tag = station_files(level_dir, 0)
    tmp = tempfile.mkdtemp(prefix="vmfl006_plant_")
    try:
        dst = os.path.join(tmp, "surfaceFieldValue.dat")
        shutil.copy(mp, dst)
        base = read_sfv(dst, "weightedAverage", "T", tag)["value"]
        lines = open(dst).read().splitlines()
        for k in range(len(lines) - 1, -1, -1):
            if lines[k] and not lines[k].startswith("#"):
                f = lines[k].split("\t")
                cols = [c for c in f if c.strip()]
                cols[1] = "%.12e" % (float(cols[1]) + PLANT)
                lines[k] = "\t".join(cols)
                break
        open(dst, "w").write("\n".join(lines) + "\n")
        seen = read_sfv(dst, "weightedAverage", "T", tag)["value"]
        delta = seen - base
        if abs(delta - PLANT) > 1e-12:
            raise SystemExit2("planted-zero control FAILED: planted %g into the mixing-cup "
                              "record on disk, the reader moved by %g -- a reader not shown "
                              "able to see a non-zero cannot certify a zero (CLAUDE.md rule 3)"
                              % (PLANT, delta))
        return {"passed": True, "planted": PLANT, "reader_delta": delta,
                "file": os.path.basename(mp), "station": tag}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------ Roache triple ----
def roache(f1, f2, f3, r=RATIO, fs=FS):
    """f1 coarse, f2 medium, f3 fine."""
    d32 = f3 - f2
    d21 = f2 - f1
    out = {"f_coarse": f1, "f_med": f2, "f_fine": f3, "ratio": r, "fs": fs,
           "d21": d21, "d32": d32}
    if d21 == 0.0 and d32 == 0.0:
        out["state"] = "EXACT"; out["p"] = None; out["gci_fine"] = None; return out
    if d21 == 0.0 or d32 == 0.0:
        out["state"] = "STAGNANT"; out["p"] = None; out["gci_fine"] = None; return out
    R = d32 / d21
    out["R"] = R
    if R < 0.0:
        out["state"] = "OSCILLATORY"; out["p"] = None; out["gci_fine"] = None; return out
    if R >= 1.0:
        out["state"] = "DIVERGENT"; out["p"] = None; out["gci_fine"] = None; return out
    p = math.log(abs(d21 / d32)) / math.log(r)
    out["p"] = p
    # OBSERVED-ORDER FLOOR. R near 1 is a STAGNANT family and ln(R)/ln(r) of it is a
    # floating-point crumb that reads as a valid, very small order; a GCI computed
    # from it is a number with no meaning. FINDING_p_floor.md sec.4.
    if p < P_MIN:
        out["state"] = "STAGNANT"; out["p_floor"] = P_MIN; out["p_below_floor"] = True
        out["gci_fine"] = None; out["f_extrapolated"] = None
        return out
    out["state"] = "CONVERGING"
    out["f_extrapolated"] = f3 + d32 / (r ** p - 1.0)
    out["gci_fine"] = fs * abs(d32 / f3) / (r ** p - 1.0)
    return out


VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")


def verdict_for(tri, inside, rc_unknown=False):
    """The ONE verdict path. main() grades through it and the planted controls
    DRIVE it, so the controls exercise the code that actually decides."""
    if rc_unknown:
        v, why = ("NOT A RESULT",
                  "the solver rc could not be read (RUN_RC.txt absent). Under L-342 a "
                  "bookkeeping failure invalidates the bookkeeping and not the physics: "
                  "every physics number is printed above and nothing is voided, but a row "
                  "whose rc is unknown is not a result.")
    elif tri["state"] != "CONVERGING":
        if tri.get("p_below_floor"):
            v, why = ("NOT A RESULT",
                      "observed order p = %.6g is below the frozen floor P_MIN = %.3g; the "
                      "triple is %s and NO GCI is quoted (FINDING_p_floor.md sec.4)"
                      % (tri["p"], P_MIN, tri["state"]))
        else:
            v, why = ("NOT A RESULT",
                      "grid triple is %s, not CONVERGING (CLAUDE.md rule 5 step 2) -- "
                      "NOT A RESULT whatever the value" % tri["state"])
    elif tri.get("gci_fine") is not None and tri["gci_fine"] > GCI_MAX:
        # THE GCI CEILING. A triple can be formally CONVERGING and scientifically
        # useless; P_MIN is a floor on the ORDER and cannot catch it.
        v, why = ("NOT A RESULT",
                  "the triple is CONVERGING at p = %.6g, but the fine-grid GCI is "
                  "%.4f %% -- ABOVE the frozen ceiling GCI_MAX = %.4f %%. The verdict "
                  "would assert the lab value lies within %.3g of the exact reference "
                  "while its own uncertainty spans %.2f band-widths, and an uncertainty "
                  "may not exceed the band it qualifies. Rule 5 permits this direction "
                  "only: a gate may turn a PASS into NOT A RESULT, never the reverse."
                  % (tri["p"], 100.0 * tri["gci_fine"], 100.0 * GCI_MAX, TOL,
                     tri["gci_fine"] / TOL))
    elif inside:
        v, why = ("PASS",
                  "every station within %.3g of the LAB-EVALUATED EXACT Graetz "
                  "reference, triple CONVERGING, GCI %.4f %% inside the ceiling "
                  "%.4f %%. PASS is available because the reference is the EXACT "
                  "solution of the SAME continuum model scalarTransportFoam "
                  "discretises -- equal densities and viscosities and no reaction "
                  "reduce the species equation exactly to div(rho*u*Y) = "
                  "div(rho*D*grad(Y)) -- so the residual is DISCRETISATION error and "
                  "CLAUDE.md rule 5 step 3 applies. Ceiling per "
                  "ANSYS_VERIFICATION_CHARTER sec.11.1: sec.2f.3's CONTINUUM cap is "
                  "the NO-TRIPLE ceiling and does not reach a declared triple that "
                  "returns CONVERGING. The series truncation is %.3e relative at the "
                  "WORST (smallest-x) station, %.3e band-widths, so 'exact' is "
                  "measured and not assumed."
                  % (TOL, 100.0 * (tri.get("gci_fine") or 0.0), 100.0 * GCI_MAX,
                     REF_TRUNC_REL_WORST, REF_TRUNC_REL_WORST / TOL))
    else:
        v, why = ("GATE FAIL", "at least one station outside the frozen %.3g band "
                               "against the lab-evaluated exact reference" % TOL)
    # rule 1's vocabulary guard, as an EXPLICIT refusal -- `python3 -O` strips
    # asserts, so this may never be an assert (PREREG_TEMPLATE Amendment 6 item 2).
    if v not in VERDICTS:
        raise SystemExit2("V0: %r is not in the fixed verdict vocabulary %r" % (v, VERDICTS))
    return (v, why)


def p_floor_control():
    """PLANTED CONTROL for the observed-order floor. A floor nobody tests is a floor
    nobody has (FINDING_p_floor.md sec.4). Three constructed triples are fed through
    this comparator's OWN roache() and OWN verdict_for(); any mis-grading REFUSES."""
    def refuse(tag, detail):
        raise SystemExit2("P-FLOOR PLANTED CONTROL FAILED [%s]: %s (P_MIN = %.3g)"
                          % (tag, detail, P_MIN))
    out = {"P_MIN": P_MIN, "probes": {}}

    tri_a = roache(1.0, 1.1, 1.2)            # equally spaced -- FINDING_p_floor sec.2
    v_a, _ = verdict_for(tri_a, True)
    out["probes"]["equally_spaced_1.0_1.1_1.2"] = {
        "state": tri_a["state"], "p": tri_a.get("p"),
        "gci_fine": tri_a.get("gci_fine"), "verdict": v_a}
    if v_a != "NOT A RESULT":
        refuse("equally-spaced", "graded %r, expected NOT A RESULT; state %s"
               % (v_a, tri_a["state"]))
    if tri_a.get("gci_fine") is not None:
        refuse("equally-spaced", "a GCI was produced (%r) for a non-converging triple"
               % (tri_a["gci_fine"],))
    if tri_a["state"] == "CONVERGING":
        refuse("equally-spaced", "classified CONVERGING with p = %r -- the defect this "
               "floor exists for" % (tri_a.get("p"),))

    p_lo = 0.01                              # genuinely computed, BELOW the floor
    tri_b = roache(1.0, 1.1, 1.1 + 0.1 * (RATIO ** (-p_lo)))
    v_b, _ = verdict_for(tri_b, True)
    out["probes"]["below_floor_p_0.01"] = {
        "state": tri_b["state"], "p": tri_b.get("p"),
        "gci_fine": tri_b.get("gci_fine"), "verdict": v_b}
    if tri_b.get("p") is None or abs(tri_b["p"] - p_lo) > 1e-9:
        refuse("below-floor", "constructed p = %.4g was not recovered (got %r)"
               % (p_lo, tri_b.get("p")))
    if not tri_b.get("p_below_floor"):
        refuse("below-floor", "p = %r is under P_MIN and the floor did NOT fire"
               % (tri_b.get("p"),))
    if v_b != "NOT A RESULT":
        refuse("below-floor", "graded %r, expected NOT A RESULT" % (v_b,))
    if tri_b.get("gci_fine") is not None:
        refuse("below-floor", "a GCI was produced (%r) below the floor" % (tri_b["gci_fine"],))

    # ABOVE the floor: the floor must not over-fire. Constructed with a SMALL d32 so
    # its GCI sits inside GCI_MAX -- this probe tests the ORDER FLOOR and must not be
    # confounded by the separate GCI ceiling, which has its own control below.
    p_hi = 0.5
    d32_c = 1.0e-3
    d21_c = d32_c * (RATIO ** p_hi)
    tri_c = roache(1.0, 1.0 + d21_c, 1.0 + d21_c + d32_c)
    v_c, _ = verdict_for(tri_c, True)
    out["probes"]["above_floor_p_0.5"] = {
        "state": tri_c["state"], "p": tri_c.get("p"),
        "gci_fine": tri_c.get("gci_fine"), "verdict": v_c}
    if tri_c["state"] != "CONVERGING" or tri_c.get("p_below_floor"):
        refuse("above-floor", "p = %r is above P_MIN and the floor fired anyway"
               % (tri_c.get("p"),))
    if tri_c.get("gci_fine") is None:
        refuse("above-floor", "no GCI for a converging triple above the floor")
    if tri_c["gci_fine"] > GCI_MAX:
        refuse("above-floor", "the probe's own GCI %.4g exceeds GCI_MAX %.4g, so it "
                              "tests the ceiling and not the floor" % (tri_c["gci_fine"], GCI_MAX))
    if v_c != "PASS":
        refuse("above-floor", "graded %r, expected PASS inside the band" % (v_c,))
    out["passed"] = True
    return out


def gci_ceiling_control():
    """PLANTED CONTROL for GCI_MAX. A ceiling nobody tests is a ceiling nobody has.

    THE DEFECT THIS EXISTS FOR, from this team's own register: VMFL063 cleared the
    P_MIN = 0.05 floor carrying a GCI of 120.62 %, and row #46 limb C carries
    145.91 % -- an uncertainty LARGER THAN THE VALUE it qualifies, riding inside a
    PASS. Every probe below is fed through this comparator's OWN roache() and OWN
    verdict_for(), so the control exercises the code that actually decides.
    """
    def refuse(tag, detail):
        raise SystemExit2("GCI-CEILING PLANTED CONTROL FAILED [%s]: %s (GCI_MAX = %.4g)"
                          % (tag, detail, GCI_MAX))
    out = {"GCI_MAX": GCI_MAX, "TOL": TOL, "probes": {}}

    def probe(tag, f1, f2, f3, expect_verdict, expect_over):
        tri = roache(f1, f2, f3)
        v, why = verdict_for(tri, True)          # inside=True: ONLY the GCI can move it
        rec = {"triple": (f1, f2, f3), "state": tri["state"], "p": tri.get("p"),
               "gci_fine": tri.get("gci_fine"), "verdict": v,
               "gci_over_ceiling": (tri.get("gci_fine") is not None
                                    and tri["gci_fine"] > GCI_MAX)}
        out["probes"][tag] = rec
        if tri["state"] != "CONVERGING":
            refuse(tag, "probe is %s, not CONVERGING -- it cannot test the ceiling"
                   % tri["state"])
        if rec["gci_over_ceiling"] != expect_over:
            refuse(tag, "GCI %.6g vs ceiling %.6g: over=%r, expected over=%r"
                   % (tri["gci_fine"], GCI_MAX, rec["gci_over_ceiling"], expect_over))
        if v != expect_verdict:
            refuse(tag, "graded %r, expected %r (GCI %.4f %%, p %.4f)"
                   % (v, expect_verdict, 100 * tri["gci_fine"], tri["p"]))
        return rec

    # (a) a CONVERGING, in-band triple whose GCI is small -> PASS is reachable.
    probe("gci_small_p2", 1.0, 1.0004, 1.0005, "PASS", False)
    # (b) the VMFL063 SHAPE: converging, p comfortably above P_MIN, GCI far above the
    #     ceiling. This is the row that used to be gradable as a PASS.
    r_b = probe("gci_18pct_p0.5", 1.0, 1.1, 1.1 + 0.1 * (RATIO ** -0.5),
                "NOT A RESULT", True)
    # (c) the ROW #46 LIMB C SHAPE: a GCI LARGER THAN 100 %, i.e. an uncertainty
    #     larger than the value it qualifies, which must never ride inside a PASS.
    r_c = probe("gci_above_100pct", 1.0, 1.9, 1.9 + 0.9 * (RATIO ** -0.25),
                "NOT A RESULT", True)
    if not (r_c["gci_fine"] > 1.0):
        refuse("gci_above_100pct", "probe (c) was meant to exceed 100 %% and its GCI is "
                                   "only %.4f %%" % (100 * r_c["gci_fine"]))
    # (d) the ceiling must not fire just BELOW itself -- no silent over-refusal.
    if r_b["gci_fine"] <= GCI_MAX:
        refuse("ordering", "probe (b) did not exceed the ceiling")
    out["passed"] = True
    return out


def infra_report(run_root, level_dirs):
    """INFRASTRUCTURE class (L-342). EVERY read here is best-effort: absent or
    malformed is a WARNING and grading proceeds. Nothing in this function can
    refuse, and nothing it returns is allowed to reach a verdict."""
    rep = {"cost": None, "launch_record": None, "contention": None, "per_level": {}}
    def kv(path):
        d = {}
        if not os.path.exists(path):
            infra_warn("%s absent -- bookkeeping only, the verdict is unaffected" % path)
            return None
        try:
            for l in open(path, errors="replace").read().splitlines():
                m = re.match(r"^\s*(\w+)\s*=\s*(.*)$", l)
                if m:
                    d[m.group(1)] = m.group(2).strip()
        except Exception as e:
            infra_warn("%s unreadable (%s) -- bookkeeping only" % (path, e))
            return None
        if not d:
            infra_warn("%s parsed to nothing -- bookkeeping only" % path)
            return None
        return d
    rep["cost"] = kv(os.path.join(run_root, "COST.txt"))
    rep["launch_record"] = kv(os.path.join(run_root, "LAUNCH_RECORD.txt"))
    if not os.path.exists(os.path.join(run_root, "CONTENTION.txt")):
        infra_warn("CONTENTION.txt absent -- bookkeeping only")
    for lv, d in level_dirs.items():
        rc = kv(os.path.join(d, "RUN_RC.txt")) or {}
        rep["per_level"][lv] = {"wall_s": rc.get("wall_s"), "core_min": rc.get("core_min"),
                                "timeout_s": rc.get("timeout_s")}
    return rep


# ----------------------------------------------------------- grading of a run --
def grade_levels(root):
    """Reads the three levels and returns the full result dict. Shared by main()
    and by the INFRASTRUCTURE-TOLERANCE control, so the control grades through the
    code that actually decides rather than a paraphrase of it."""
    del TIME_DIR_SELECTIONS[:]
    res = {"case": "VMFL006", "manual_page": "27-28", "tol": TOL, "gci_max": GCI_MAX,
           "reference": REF_LAB, "reference_kind": REF_KIND,
           "reference_truncation_rel_worst": REF_TRUNC_REL_WORST,
           "reference_truncation_n_terms": REF_TRUNC_N_TERMS,
           "reference_instrument_spread": REF_INSTRUMENT_SPREAD,
           "manual_target_corroboration_only": MANUAL,
           "manual_rounding_floor": MANUAL_ROUNDING_FLOOR,
           "ansys_context_only": FLUENT, "stations_m": STATIONS,
           "wedge_bias_on_theta": WEDGE_BIAS_ON_THETA,
           "wedge_bias_worst": WEDGE_BIAS_WORST,
           "wedge_ratio_bias_pct": WEDGE_RATIO_BIAS_PCT,
           "comparator": os.path.abspath(__file__),
           "completion": {}, "convergence": {}, "levels": {}, "planted_zero": {}}
    # CONTROLS THAT MUST FIRE BEFORE ANY LEVEL IS READ. Each REFUSES (exit 2).
    res["ast_guard"] = ast_no_assert_guard()
    res["reference_reproduction"] = reference_reproduction()
    res["p_floor_control"] = p_floor_control()
    res["gci_ceiling_control"] = gci_ceiling_control()
    level_dirs = {}
    rc_unknown = False
    for lv in LEVELS:
        d = os.path.join(root, lv)
        level_dirs[lv] = d
        c = completion(d, lv)
        rc_unknown = rc_unknown or c["rc_unknown"]
        res["completion"][lv] = c
        res["convergence"][lv] = convergence(d)
        st = [read_station(d, lv, i) for i in range(len(STATIONS))]
        res["levels"][lv] = {"stations": st,
                             "theta": [s["theta"] for s in st],
                             "worst_flux_rel_dev": max(s["flux_rel_dev"] for s in st)}
    res["rc_unknown"] = rc_unknown

    # ---- PLANTED-ZERO CONTROL AT **EVERY** LEVEL, NOT JUST ONE -----------------
    # Rows #44 and #46 both carry a disclosed weakness for firing the plant at L1
    # ONLY, which means the readers that produced the L2 and L3 numbers -- and L3
    # is the level the band is decided on, while ALL THREE feed the Roache triple
    # the verdict depends on -- were never shown able to see a non-zero on their
    # OWN bytes. A control that fires on one level's file certifies one level's
    # reader. Each plant below goes to DISK and is read back through the PRODUCTION
    # reader (read_sfv), on that level's own data.
    for lv in LEVELS:
        res["planted_zero"][lv] = planted_zero(level_dirs[lv])
    res["planted_zero_levels"] = list(LEVELS)

    res["infrastructure"] = infra_report(root, level_dirs)
    res["infra_warnings"] = list(INFRA_WARNINGS)
    res["time_dir_selections"] = list(TIME_DIR_SELECTIONS)
    res["lexicographic_would_have_misread_any"] = any(
        s["lexicographic_would_have_misread"] for s in TIME_DIR_SELECTIONS)

    fine = res["levels"][LEVELS[-1]]["theta"]
    # THE GATE: against the LAB-EVALUATED EXACT reference, never the printed column.
    devs = [abs(fine[i] - REF_LAB[i]) / abs(REF_LAB[i]) for i in range(len(STATIONS))]
    res["rel_dev_per_station"] = devs
    res["worst_rel_dev"] = max(devs)
    res["worst_station_m"] = STATIONS[devs.index(max(devs))]
    # CORROBORATION ONLY -- reported beside the gate, deciding nothing.
    res["rel_dev_vs_manual_corroboration"] = [
        abs(fine[i] - MANUAL[i]) / abs(MANUAL[i]) for i in range(len(STATIONS))]
    res["lab_value_x010"] = fine[TRIPLE_I]
    tri = roache(res["levels"]["L1"]["theta"][TRIPLE_I],
                 res["levels"]["L2"]["theta"][TRIPLE_I],
                 res["levels"]["L3"]["theta"][TRIPLE_I])
    res["triple"] = tri
    res["triple_station_m"] = STATIONS[TRIPLE_I]
    inside = res["worst_rel_dev"] <= TOL
    res["inside_band"] = inside
    v, why = verdict_for(tri, inside, rc_unknown)
    res["verdict"], res["why"] = v, why
    return res


# ---------------------------------------------- INFRASTRUCTURE-TOLERANCE control --
def _write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(s)


def build_fake_run(root, thetas_by_level, endtime=ENDTIME_EXPECTED):
    """Construct a complete, gradable run on disk. Used ONLY by the selftest and by
    the infrastructure-tolerance control."""
    for lv in LEVELS:
        d = os.path.join(root, lv)
        nr = NR_OF[lv]
        _write(os.path.join(d, "RUN_RC.txt"),
               "rc = 0\nlevel = %s\nwall_s = 12\nranks = 1\ncore_min = 0.2\ntimeout_s = 600\n" % lv)
        body = "".join("Time = %d\n" % i for i in range(1, endtime + 1))
        _write(os.path.join(d, "log.scalarTransportFoam"), body + "\nEnd\n")
        _write(os.path.join(d, "system", "controlDict"), "endTime %d;\n" % endtime)
        _write(os.path.join(d, "birth_certificate.json"),
               json.dumps({"cells": NX_OF[lv] * nr, "mesh_ok": True, "max_skewness": 0.33,
                           "max_aspect_ratio": 8.8, "max_non_orthogonality": 0.0,
                           "nx": NX_OF[lv], "nr": nr}))
        rows = ["# Solver information",
                "# Time\tT_solver\tT_initial\tT_final\tT_iters\tT_converged"]
        for i in range(1, endtime + 1):
            rows.append("%d\tsmoothSolver\t%.12e\t1e-14\t4\ttrue"
                        % (i, max(1e-14, 1.0 * (0.99 ** i)) + 1e-12 * (1.0 / (1 + i))))
        _write(os.path.join(d, "postProcessing", "residuals", "0", "solverInfo.dat"),
               "\n".join(rows) + "\n")
        for i, th in enumerate(thetas_by_level[lv]):
            tag = "x%02d" % (i + 1)
            region = ("patch outlet" if i == len(STATIONS) - 1 else "faceZone %s" % tag)
            y = Y_WALL - (Y_WALL - Y_IN) * th
            _write(os.path.join(d, "postProcessing", "mixCup_" + tag, "0", "surfaceFieldValue.dat"),
                   "# Region type :     %s\n# Faces             : %d\n# Area              : 2.7e-07\n"
                   "# Scale factor      : 1.000000000000e+00\n# Weight field      : phi\n"
                   "# Time              \tweightedAverage(T)\n%d                  \t%.12e\n"
                   % (region, nr, endtime, y))
            _write(os.path.join(d, "postProcessing", "flux_" + tag, "0", "surfaceFieldValue.dat"),
                   "# Region type :     %s\n# Faces             : %d\n# Area              : 2.7e-07\n"
                   "# Scale factor      : 1.000000000000e+00\n"
                   "# Time              \tsum(phi)\n%d                  \t%.12e\n"
                   % (region, nr, endtime, WEDGE_FLUX))
        # 0/T is the age-guard marker: make it OLDER than the endTime fields.
        _write(os.path.join(d, "0", "T"), "T0\n")
        for f in ("T", "U", "phi"):
            _write(os.path.join(d, str(endtime), f), "%s\n" % f)
        zt = os.path.getmtime(os.path.join(d, str(endtime), "T")) - 10
        os.utime(os.path.join(d, "0", "T"), (zt, zt))
    _write(os.path.join(root, "COST.txt"), "total_wall_s = 36\nranks = 1\ntotal_core_min = 0.6\n")
    _write(os.path.join(root, "LAUNCH_RECORD.txt"), "launched_utc = 2026-01-01T00:00:00Z\nmode = graded\n")
    _write(os.path.join(root, "CONTENTION.txt"), "loadavg = 0 0 0\n")


def infra_tolerance_control():
    """PLANTED CONTROL for Sanaa's universal rule (L-342), DRIVEN not declared.

      plant 1: a constructed run is graded intact, then graded again with COST.txt
               DELETED and LAUNCH_RECORD.txt CORRUPTED. The verdict, the lab value
               and the observed order must be IDENTICAL. If an infrastructure field
               can move a verdict, this control REFUSES.
      plant 2: the same run has a PHYSICS field broken (the End line removed). The
               comparator must still REFUSE (exit 2). A rule that tolerates
               bookkeeping must not thereby tolerate a broken solve.
    """
    def refuse(tag, detail):
        raise SystemExit2("INFRASTRUCTURE-TOLERANCE CONTROL FAILED [%s]: %s" % (tag, detail))
    # a triple that converges cleanly at p = 2 on every station
    base = {}
    for k, lv in enumerate(LEVELS):
        eps = 0.004 / (RATIO ** (2 * k))
        base[lv] = [REF_LAB[i] * (1.0 + eps) for i in range(len(STATIONS))]
    d = tempfile.mkdtemp(prefix="vmfl006_infra_")
    try:
        root = os.path.join(d, "run")
        build_fake_run(root, base)
        del INFRA_WARNINGS[:]
        a = grade_levels(root)
        os.remove(os.path.join(root, "COST.txt"))
        open(os.path.join(root, "LAUNCH_RECORD.txt"), "w").write("<<<corrupt binary garbage>>>\n")
        del INFRA_WARNINGS[:]
        b = grade_levels(root)
        if a["verdict"] != b["verdict"]:
            refuse("plant 1", "verdict moved from %r to %r when COST.txt was deleted and "
                              "LAUNCH_RECORD.txt corrupted" % (a["verdict"], b["verdict"]))
        if a["lab_value_x010"] != b["lab_value_x010"]:
            refuse("plant 1", "the lab value moved (%r -> %r) on an infrastructure change"
                   % (a["lab_value_x010"], b["lab_value_x010"]))
        if a["triple"].get("p") != b["triple"].get("p"):
            refuse("plant 1", "the observed order moved on an infrastructure change")
        if not b["infra_warnings"]:
            refuse("plant 1", "the missing COST.txt produced NO warning -- an unreported "
                              "absence and a healthy read must not look alike")
        # plant 2: break a PHYSICS field. It must still refuse.
        p = os.path.join(root, "L2", "log.scalarTransportFoam")
        _t = open(p).read()          # READ FIRST (see the same trap above)
        _t = _t.replace("\nEnd\n", "\nNOT-AN-END\n")
        open(p, "w").write(_t)
        refused = False
        try:
            del INFRA_WARNINGS[:]
            grade_levels(root)
        except SystemExit as ex:
            refused = (ex.code == 2)
        if not refused:
            refuse("plant 2", "a broken PHYSICS field (the End line) did NOT refuse -- "
                              "tolerating bookkeeping must not tolerate a broken solve")
        return {"passed": True, "verdict_intact": a["verdict"], "verdict_degraded": b["verdict"],
                "infra_warnings_seen": len(b["infra_warnings"]),
                "physics_plant_refused": refused}
    finally:
        del INFRA_WARNINGS[:]
        shutil.rmtree(d, ignore_errors=True)


# ------------------------------------------------------------------- selftest --
def selftest():
    ok = True

    def chk(c, name, got=""):
        nonlocal ok
        print("  [%s] %s  %s" % ("PASS" if c else "FAIL", name, got))
        ok = ok and bool(c)

    print("--- selftest: normalisation and the reference identity")
    chk(abs(theta_of(Y_IN) - 1.0) < 1e-15, "theta(inlet) == 1")
    chk(abs(theta_of(Y_WALL) - 0.0) < 1e-15, "theta(wall) == 0")
    chk(len(MANUAL) == 10 and len(STATIONS) == 10 and len(FLUENT) == 10,
        "ten stations, ten targets, ten Fluent values")
    w = max(abs(REF_LAB[i] - MANUAL[i]) / MANUAL[i] for i in range(10))
    chk(w < 1e-3, "the lab's EXACT reference corroborates the manual's printed column "
                  "within 0.1 % (the manual is the CHECK, never the gate)",
        "worst %.5f %%" % (100 * w))
    chk(w > MANUAL_ROUNDING_FLOOR * 0.1,
        "...and the two are NOT identical -- the printed column is a 4-dp quotation "
        "with a %.3e rounding floor, which is why it is not the gate" % MANUAL_ROUNDING_FLOOR,
        "worst %.5f %%" % (100 * w))

    print("--- selftest: the AST guard, PROVED TO FIRE (not merely to pass)")
    g = ast_no_assert_guard()
    chk(g["passed"] and g["assert_nodes"] == 0,
        "this comparator's own bytes on disk carry ZERO `assert` statements",
        "%d AST nodes scanned" % g["n_ast_nodes"])
    fired = False
    try:
        ast_no_assert_guard(_src="def f(x):\n    assert x > 0, 'stripped by -O'\n    return x\n")
    except SystemExit as ex:
        fired = (ex.code == 2)
    chk(fired, "the AST guard REFUSES (exit 2) a source that DOES contain an assert "
               "-- a guard only ever seen to pass is an unproven guard")
    unparseable = False
    try:
        ast_no_assert_guard(_src="def (:::\n")
    except SystemExit as ex:
        unparseable = (ex.code == 2)
    chk(unparseable, "the AST guard REFUSES an unparseable source rather than passing it")

    print("--- selftest: the gate reference is REPRODUCED by the OTHER instrument")
    rr = reference_reproduction()
    chk(rr["passed"] and rr["worst_rel_disagreement"] < REF_REPRO_TOL,
        "frozen REF_LAB (shooting) reproduced live by finite volume",
        "worst %.3e vs tol %.1e" % (rr["worst_rel_disagreement"], REF_REPRO_TOL))
    chk(REF_TRUNC_REL_WORST / TOL < 1e-12,
        "the registered series truncation is negligible against the band",
        "%.3e relative = %.3e band-widths" % (REF_TRUNC_REL_WORST, REF_TRUNC_REL_WORST / TOL))

    print("--- selftest: NUMERIC time-directory selection with a cardinality refusal")
    dsel = tempfile.mkdtemp(prefix="st006_")
    try:
        base = os.path.join(dsel, "pp")
        for nm in ("0", "900", "1500", "0.orig"):
            os.makedirs(os.path.join(base, nm))
        # FOUR directories are made and only THREE are numeric: '0.orig' is a field
        # backup, not a time, and a [0-9]* glob would have matched it (L-339).
        sel = pick_time_dir(base, expect_n=3, what="selftest")
        chk(sel["dir"] == "1500", "numeric selection picks 1500, not lexicographic '900'",
            "chose %r, lexicographic would have chosen %r"
            % (sel["dir"], sel["lexicographic_would_have_picked"]))
        chk(sel["lexicographic_would_have_misread"],
            "and the record SAYS a lexicographic selector would have misread it")
        chk(sel["non_numeric_ignored"] == ["0.orig"],
            "'0.orig' is not a time directory and is excluded, not matched by a glob")
        card = False
        try:
            pick_time_dir(base, expect_n=1, what="selftest cardinality")
        except SystemExit as ex:
            card = (ex.code == 2)
        chk(card, "an UNEXPECTED NUMBER of time directories REFUSES (exit 2) rather "
                  "than picking the newest of a set it did not expect")
    finally:
        shutil.rmtree(dsel, ignore_errors=True)

    print("--- selftest: Roache classifier")
    chk(roache(1.0, 1.5, 1.75)["state"] == "CONVERGING", "first-order -> CONVERGING")
    chk(abs(roache(1.0, 1.5, 1.75)["p"] - 1.0) < 1e-9, "p == 1")
    chk(abs(roache(1.0, 1.25, 1.3125)["p"] - 2.0) < 1e-9, "second-order family -> p == 2")
    chk(roache(1.0, 2.0, 4.0)["state"] == "DIVERGENT", "divergent")
    chk(roache(1.0, 2.0, 1.5)["state"] == "OSCILLATORY", "oscillatory")
    chk(roache(2.0, 2.0, 2.0)["state"] == "EXACT", "identical -> EXACT")

    print("--- selftest: PLANTED CONTROL -- the observed-order floor P_MIN = %.3g" % P_MIN)
    pf = p_floor_control()
    chk(pf["probes"]["equally_spaced_1.0_1.1_1.2"]["verdict"] == "NOT A RESULT"
        and pf["probes"]["equally_spaced_1.0_1.1_1.2"]["gci_fine"] is None,
        "(1.0, 1.1, 1.2) -> NOT A RESULT, no GCI",
        pf["probes"]["equally_spaced_1.0_1.1_1.2"]["state"])
    chk(pf["probes"]["below_floor_p_0.01"]["verdict"] == "NOT A RESULT",
        "p = 0.01 (below floor) -> NOT A RESULT, no GCI")
    chk(pf["probes"]["above_floor_p_0.5"]["verdict"] == "PASS"
        and pf["probes"]["above_floor_p_0.5"]["gci_fine"] is not None,
        "p = 0.5 (above floor) -> the floor does NOT over-fire, GCI quoted")

    print("--- selftest: PLANTED CONTROL -- the GCI ceiling GCI_MAX = %.4g" % GCI_MAX)
    gc = gci_ceiling_control()
    chk(gc["probes"]["gci_small_p2"]["verdict"] == "PASS"
        and not gc["probes"]["gci_small_p2"]["gci_over_ceiling"],
        "a converging in-band triple with a SMALL GCI -> PASS (the ceiling does not "
        "over-fire and PASS is genuinely reachable)",
        "GCI %.4f %%" % (100 * gc["probes"]["gci_small_p2"]["gci_fine"]))
    chk(gc["probes"]["gci_18pct_p0.5"]["verdict"] == "NOT A RESULT",
        "THE VMFL063 SHAPE: converging, p above P_MIN, GCI %.2f %% -> NOT A RESULT "
        "(this row used to be gradable as a PASS)"
        % (100 * gc["probes"]["gci_18pct_p0.5"]["gci_fine"]))
    chk(gc["probes"]["gci_above_100pct"]["verdict"] == "NOT A RESULT"
        and gc["probes"]["gci_above_100pct"]["gci_fine"] > 1.0,
        "THE ROW #46 LIMB C SHAPE: GCI %.2f %% -- an uncertainty LARGER THAN THE "
        "VALUE it qualifies -> NOT A RESULT"
        % (100 * gc["probes"]["gci_above_100pct"]["gci_fine"]))
    chk(abs(GCI_MAX - TOL) < 1e-15,
        "GCI_MAX is set FROM THE BAND (== TOL), not from any measured GCI",
        "GCI_MAX %.4g == TOL %.4g" % (GCI_MAX, TOL))

    print("--- selftest: the gate can PASS and can FAIL")
    chk(0.005 <= TOL, "+0.5 %% is inside the band")
    chk(not (0.02 <= TOL), "+2 %% is OUTSIDE the band")
    chk(max(abs(FLUENT[i] - REF_LAB[i]) / REF_LAB[i] for i in range(10)) < TOL,
        "Ansys Fluent's own numbers would sit INSIDE this band against the EXACT reference",
        "worst %.4f %%" % (100 * max(abs(FLUENT[i] - REF_LAB[i]) / REF_LAB[i] for i in range(10))))
    chk(WEDGE_BIAS_WORST < TOL,
        "CLAUSE A: the disclosed wedge bias fits inside the band with margin",
        "%.6f %% bias vs %.4f %% band, margin %.2f x"
        % (100 * WEDGE_BIAS_WORST, 100 * TOL, TOL / WEDGE_BIAS_WORST))

    print("--- selftest: end-to-end grading on a CONSTRUCTED run whose answer is known")
    d = tempfile.mkdtemp(prefix="st006_")
    try:
        # a triple converging at p = 2 towards a value 0.4 % above the REFERENCE:
        # inside the 1 % band, so the constructed answer is deliberately NOT the
        # reference itself -- a reader that returned the reference is caught here.
        th = {}
        for k, lv in enumerate(LEVELS):
            eps = 0.004 / (RATIO ** (2 * k))
            th[lv] = [REF_LAB[i] * (1.0 + eps) for i in range(10)]
        root = os.path.join(d, "run")
        build_fake_run(root, th)
        del INFRA_WARNINGS[:]
        r = grade_levels(root)
        chk(r["verdict"] == "PASS", "constructed in-band converging run -> PASS "
                                    "(the gate CAN return the top verdict)", r["verdict"])
        chk(abs(r["triple"]["p"] - 2.0) < 1e-6, "the constructed observed order is recovered",
            "%.6f" % r["triple"]["p"])
        chk(r["triple"]["gci_fine"] <= GCI_MAX,
            "and its GCI sits inside the ceiling, so the PASS is not riding on an "
            "uncertainty larger than its band",
            "GCI %.5f %% vs ceiling %.4f %%" % (100 * r["triple"]["gci_fine"], 100 * GCI_MAX))
        expect_fine = REF_LAB[TRIPLE_I] * (1.0 + 0.004 / (RATIO ** (2 * (len(LEVELS) - 1))))
        chk(abs(r["lab_value_x010"] - expect_fine) < 1e-12
            and abs(r["lab_value_x010"] - REF_LAB[TRIPLE_I]) > 1e-6,
            "the fine value read from disk is the CONSTRUCTED one, not the reference",
            "%.9f (constructed %.9f, reference %.9f)"
            % (r["lab_value_x010"], expect_fine, REF_LAB[TRIPLE_I]))
        chk(sorted(r["planted_zero"].keys()) == sorted(LEVELS),
            "the planted-zero control fired at EVERY level, not just one",
            "levels planted: %r" % sorted(r["planted_zero"].keys()))
        chk(all(r["planted_zero"][lv]["passed"]
                and abs(r["planted_zero"][lv]["reader_delta"] - PLANT) < 1e-12
                for lv in LEVELS),
            "...and each level's plant was seen UNDILUTED on that level's own bytes (L-340)")
        chk(len(r["time_dir_selections"]) >= 3 * (1 + 1 + 2 * len(STATIONS)),
            "every time-directory read went through the numeric selector",
            "%d selections recorded" % len(r["time_dir_selections"]))
        chk(all(s["numeric_candidates"] for s in r["time_dir_selections"]),
            "and every one of them recorded its candidate set for the record")

        # a BLIND reader must REFUSE
        global read_sfv
        _orig = read_sfv
        try:
            read_sfv = lambda p, o, f, rg: {"value": 0.0, "faces": None, "region": rg,
                                            "weight": "phi", "n_rows": 1, "time": 0.0}
            blind = False
            try:
                planted_zero(os.path.join(root, "L3"))
            except SystemExit as ex:
                blind = (ex.code == 2)
            chk(blind, "planted-zero REFUSES (exit 2) a reader that cannot see the plant")
        finally:
            read_sfv = _orig

        # out-of-band construction must GATE FAIL, not silently pass
        th2 = {lv: [v * 1.05 for v in th[lv]] for lv in LEVELS}
        root2 = os.path.join(d, "run2")
        build_fake_run(root2, th2)
        del INFRA_WARNINGS[:]
        r2 = grade_levels(root2)
        chk(r2["verdict"] == "GATE FAIL", "a 5 %% offset run -> GATE FAIL", r2["verdict"])

        # a wrong flux (orientation) must REFUSE
        root3 = os.path.join(d, "run3")
        build_fake_run(root3, th)
        p = os.path.join(root3, "L1", "postProcessing", "flux_x05", "0", "surfaceFieldValue.dat")
        _t = open(p).read()          # READ FIRST -- open(p,"w") truncates before the read runs
        _t = _t.replace("%.12e" % WEDGE_FLUX, "%.12e" % (-WEDGE_FLUX))
        open(p, "w").write(_t)
        ref = False
        try:
            del INFRA_WARNINGS[:]
            grade_levels(root3)
        except SystemExit as ex:
            ref = (ex.code == 2)
        chk(ref, "a reversed sum(phi) REFUSES (conservation/orientation control)")

        # a NON-ZERO rc must REFUSE (this is the clause that says the solver failed)
        root5 = os.path.join(d, "run5")
        build_fake_run(root5, th)
        pr = os.path.join(root5, "L3", "RUN_RC.txt")
        _t = open(pr).read().replace("rc = 0", "rc = 1")
        open(pr, "w").write(_t)
        ref5 = False
        try:
            del INFRA_WARNINGS[:]
            grade_levels(root5)
        except SystemExit as ex:
            ref5 = (ex.code == 2)
        chk(ref5, "a non-zero solver rc REFUSES (exit 2) -- strict completion, rule 4")

        # and an UNPARSEABLE RUN_RC.txt must FAIL SAFE (refuse), never default to 0
        root6 = os.path.join(d, "run6")
        build_fake_run(root6, th)
        open(os.path.join(root6, "L1", "RUN_RC.txt"), "w").write("garbage with no rc key\n")
        ref6 = False
        try:
            del INFRA_WARNINGS[:]
            grade_levels(root6)
        except SystemExit as ex:
            ref6 = (ex.code == 2)
        chk(ref6, "an UNPARSEABLE RUN_RC.txt fails SAFE (refuses), never defaults to rc = 0")

        # a missing RUN_RC.txt must NOT void the physics: NOT A RESULT, numbers printed
        root4 = os.path.join(d, "run4")
        build_fake_run(root4, th)
        os.remove(os.path.join(root4, "L2", "RUN_RC.txt"))
        del INFRA_WARNINGS[:]
        r4 = grade_levels(root4)
        chk(r4["verdict"] == "NOT A RESULT" and r4["lab_value_x010"] == r["lab_value_x010"],
            "absent RUN_RC.txt -> NOT A RESULT with the physics STILL COMPUTED (L-342)",
            r4["verdict"])
    finally:
        del INFRA_WARNINGS[:]
        shutil.rmtree(d, ignore_errors=True)

    print("--- selftest: PLANTED CONTROL -- infrastructure tolerance (L-342)")
    it = infra_tolerance_control()
    chk(it["passed"] and it["verdict_intact"] == it["verdict_degraded"],
        "deleting COST.txt and corrupting LAUNCH_RECORD.txt leaves the verdict IDENTICAL",
        "%s == %s, %d warnings" % (it["verdict_intact"], it["verdict_degraded"],
                                   it["infra_warnings_seen"]))
    chk(it["physics_plant_refused"],
        "breaking a PHYSICS field (the End line) STILL refuses (exit 2)")

    print("\nSELFTEST: %s" % ("all checks passed" if ok else "FAILURES PRESENT"))
    return 0 if ok else 1


# ----------------------------------------------------------------------- main --
def main():
    root = os.path.normpath(RUN_ROOT)
    print("=" * 78)
    print("VMFL006 -- Multicomponent Species Transport in Pipe Flow")
    print("Ansys FD Verification Manual 2026 R1, pp. 27-28")
    print("gate: MIXING-CUP theta = (0.9 - Y)/0.4 at x = 0.01..0.10 m vs the LAB'S OWN")
    print("      full-precision evaluation of the Graetz series (EXACT; the manual's")
    print("      4-dp Target column is CORROBORATION, never the gate)")
    print("      band |theta_lab - theta_ref|/theta_ref <= %.3g at EVERY station, at L3" % TOL)
    print("      GCI ceiling GCI_MAX = %.3g -- an uncertainty may not exceed its band" % GCI_MAX)
    print("=" * 78)

    # PLANTED CONTROLS, driven on the FROZEN grading path itself, before any level
    # is read. Each REFUSES (exit 2) rather than grading.
    ag = ast_no_assert_guard()
    print("AST guard OK: 0 `assert` statements in this comparator's own bytes on disk "
          "(%d AST nodes scanned)" % ag["n_ast_nodes"])
    rr = reference_reproduction()
    print("reference reproduction OK: frozen REF_LAB (shooting) reproduced live by the "
          "INDEPENDENT finite-volume instrument to %.3e (tol %.1e)"
          % (rr["worst_rel_disagreement"], REF_REPRO_TOL))
    print("series truncation REGISTERED: %.3e relative at the SMALLEST station x=0.01 m "
          "(N=%d terms), %.3e band-widths"
          % (REF_TRUNC_REL_WORST, REF_TRUNC_N_TERMS, REF_TRUNC_REL_WORST / TOL))
    pf = p_floor_control()
    print("p-floor planted control OK (P_MIN = %.3g): (1.0,1.1,1.2) -> %s, no GCI"
          % (P_MIN, pf["probes"]["equally_spaced_1.0_1.1_1.2"]["verdict"]))
    gc = gci_ceiling_control()
    print("GCI-ceiling planted control OK (GCI_MAX = %.3g): a GCI of %.2f %% -- larger "
          "than the value it qualifies -> %s"
          % (GCI_MAX, 100 * gc["probes"]["gci_above_100pct"]["gci_fine"],
             gc["probes"]["gci_above_100pct"]["verdict"]))
    it = infra_tolerance_control()
    print("infrastructure-tolerance control OK (L-342): verdict %s with COST.txt present "
          "and %s with it deleted; a broken End line still refuses"
          % (it["verdict_intact"], it["verdict_degraded"]))

    res = grade_levels(root)
    res["p_floor_control"] = pf
    res["gci_ceiling_control"] = gc
    res["infra_tolerance_control"] = it

    print("\n--- mixing-cup theta per station (fine level %s) ---" % LEVELS[-1])
    print("   x (m)    lab theta        EXACT reference   rel dev (GATE)   manual 4dp (corrob.)")
    fine = res["levels"][LEVELS[-1]]["theta"]
    for i, x in enumerate(STATIONS):
        print("   %.2f     %.9f      %.9f      %+8.4f %%        %.4f"
              % (x, fine[i], REF_LAB[i],
                 100 * (fine[i] - REF_LAB[i]) / REF_LAB[i], MANUAL[i]))
    print("  worst |lab - EXACT|/EXACT = %.5f %% at x = %.2f m   [THE GATE]"
          % (100 * res["worst_rel_dev"], res["worst_station_m"]))
    print("  worst |lab - manual 4dp|  = %.5f %%   [corroboration only, decides nothing]"
          % (100 * max(res["rel_dev_vs_manual_corroboration"])))
    print("  worst conservation-control deviation across all levels = %.3e"
          % max(res["levels"][lv]["worst_flux_rel_dev"] for lv in LEVELS))
    print("  CLAUSE A wedge bias on this gate quantity: %+.6f %% at x = 0.10 m "
          "(theta biased LOW; sec(t/2) = 1+%.6f %%; the sin(t)/t AREA deficit "
          "cancels exactly in the ratio)"
          % (100 * WEDGE_BIAS_ON_THETA[-1], WEDGE_RATIO_BIAS_PCT))

    print("\nplanted-zero control -- fired at EVERY level (%s):" % ", ".join(LEVELS))
    for lv in LEVELS:
        pz = res["planted_zero"][lv]
        print("  %s: planted %.6g into %s on disk, production reader moved by %.6g"
              % (lv, pz["planted"], pz["file"], pz["reader_delta"]))
    print("time-directory selection: %d numeric selections, cardinality-checked; "
          "lexicographic_would_have_misread_any = %s"
          % (len(res["time_dir_selections"]), res["lexicographic_would_have_misread_any"]))

    tri = res["triple"]
    print("\n--- Roache triple on theta at x = %.2f m (r = %.1f) ---"
          % (res["triple_station_m"], RATIO))
    print("  %.9f / %.9f / %.9f  -> %s"
          % (tri["f_coarse"], tri["f_med"], tri["f_fine"], tri["state"]))
    if tri["state"] == "CONVERGING":
        print("  observed order p = %.4f   GCI_fine (Fs = %.2f) = %.6f %%"
              % (tri["p"], FS, 100.0 * tri["gci_fine"]))
        print("  GCI / band = %.4f  (ceiling GCI_MAX = %.4f %%, i.e. 1.0000 band-widths) -- %s"
              % (tri["gci_fine"] / TOL, 100.0 * GCI_MAX,
                 "INSIDE the ceiling" if tri["gci_fine"] <= GCI_MAX
                 else "ABOVE the ceiling: NOT A RESULT"))
    elif tri.get("p_below_floor"):
        print("  observed order p = %.6g is BELOW the frozen floor P_MIN = %.3g -- the "
              "triple is\n  reported %s and NO GCI is quoted (FINDING_p_floor.md sec.4)."
              % (tri["p"], P_MIN, tri["state"]))
    else:
        print("  observed order: undefined for a %s triple; NO GCI is quoted." % tri["state"])

    for lv in LEVELS:
        c = res["convergence"][lv]
        print("  %s convergence: n_iters=%d n_window=%d max T_initial in window=%.3e "
              "(floor %.1e)" % (lv, c["n_iters"], c["n_window"], c["res_max_in_window"],
                                c["floor"]))

    print("\nVERDICT: %s -- %s" % (res["verdict"], res["why"]))
    if res["infra_warnings"]:
        print("infrastructure warnings (bookkeeping only, no verdict effect): %d"
              % len(res["infra_warnings"]))

    out = os.path.join(root, "GRADING_VMFL006.json")
    try:
        with open(out, "w") as fh:
            json.dump(res, fh, indent=2, sort_keys=True, default=str)
        print("grading written to %s" % out)
    except Exception as e:
        infra_warn("could not write %s (%s) -- the verdict above stands" % (out, e))
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
