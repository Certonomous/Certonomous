#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
grade_vmfl008.py -- DRAFT COMPARATOR for VMFL008 (Flow Inside a Rotating Cavity),
Ansys Fluid Dynamics Verification Manual VM2026R1, printed p. 31, Fig .08.3 (p. 33).

  *** DRAFT.  NOT FROZEN.  NOT RUN.  NO COMPUTE HAS BEEN LAUNCHED. ***

This is the FIRST per-case comparator in this territory that gates on a DIGITIZED
reference (charter 25/28/29, register row #56).  Read the header before the code.

-----------------------------------------------------------------------------
WHAT IS GATED
-----------------------------------------------------------------------------
SWIRL VELOCITY V_theta(r) along the section at X = 0.6 m -- a **VALUE** read
(a magnitude off a curve at frozen abscissae), NOT a POSITION read.  Per 28.2
every term of 25.4 is computed on THIS quantity in ITS OWN units (m/s).

-----------------------------------------------------------------------------
28.6 -- THE NUMBER 0.00505051 DOES NOT TRANSFER, AND THIS FILE NEVER HARDCODES IT
-----------------------------------------------------------------------------
Charter 28.6, verbatim: "u_read is PER-TARGET-FORMAT and is RE-DERIVED PER CASE.
There is no single lab-wide u_read, and a calibration performed for one figure
does not transfer to another by assertion."

Register row #56's VALUE u_read = 0.00505051 is in the R2 calibration plate's OWN
y-data units, for a plate whose y-axis spans 2.5 y-data units over a 495 px
interior box (2.5 / 495 = 0.005050505...).  It is a PIXEL FLOOR expressed in a
format that is not VMFL008's.  What transfers is the METHOD and the reader's
demonstrated error IN PIXELS (VALUE: max per-plate 0.220671 px, i.e. 4.5316x
BELOW the 1.000 px floor -- the well-behaved regime).  The NUMBER does not.

So this comparator CONSUMES u_read from the per-case calibration artifact
UREAD_JSON, and REFUSES (exit 2) rather than assuming any value.

-----------------------------------------------------------------------------
TWO DISCLOSED INSTRUMENT DEFECTS THAT TRAVEL WITH EVERY CASE USING THE R2
DIGITIZER (register row #56).  Restated here because a reader of THIS file must
see them without going elsewhere (31.3: the correction goes where the number is
read).  NEITHER IS REPAIRED HERE -- rule 6, frozen files are never edited.

  DEFECT 1 -- THE R2 COMPARATOR'S OWN VERDICT EXIT PATH NEVER EXECUTED.
    digitize_calibrate_r2.py terminates with an unhandled
    "ValueError: Circular reference detected" at :196, inside a
    print(json.dumps(rep, ...)) DISPLAY statement, and exits 1.  Because the
    exception is raised inside calibrate_r2(), `rep` never returns and the
    wrapper's verdict-bearing `sys.exit(2 if bad else 0)` at :279 NEVER RAN.
    The outcome is recoverable from the persisted GRADE_R2.json (valid, complete,
    both verdicts PASS).  Classified INFRASTRUCTURE, NOT PHYSICS under Sanaa's
    universal rule of 2026-08-26 (bookkeeping never voids physics).
    CONSEQUENCE FOR THIS CASE: this comparator may NEVER infer the per-case
    calibration's verdict from its EXIT CODE.  It reads the persisted JSON and
    refuses on anything but an explicit recorded PASS.  See _load_uread().

  DEFECT 2 -- THE POSITION PLANTED NULL CANNOT FAIL BY CONSTRUCTION.
    POSITION's u_read is DEFINED as the max of the per-plate error population and
    the null offset is drawn from that same population, so u_read >= null_off
    holds identically (selftest arm 2 states it at zero margin:
    u_read = 0.0032424 >= MAX = 0.0032424).  A control that cannot fail has no
    power.  ALL discrimination in that instrument rests on PLANT-DETECT alone.
    THIS CASE GATES ON VALUE, NOT POSITION -- and the citation carries the defect
    anyway, because VALUE's own null (null_off 0.147698 px vs a 1.000 px floor)
    passes for a DIFFERENT reason (the floor dominates a well-behaved reader),
    and a reader must not mistake one for the other.

-----------------------------------------------------------------------------
THE VMFL046 LESSON IS BUILT IN (charter 31.1, register rows #54/#55)
-----------------------------------------------------------------------------
Rows #54 and #55 were demoted to NOT A RESULT because a plateau limb read
4.332e-10 -- a near-exact zero -- for a quantity moving 192.60 % of its band,
because the watched station was causally blind to the gated quantity.
"Three guards, one geometry, defeated identically: one blind station wearing
three coats."

Here the plateau is measured ON THE GATED QUANTITY AT EVERY GATED STATION
(21.1: a plateau criterion attaches PER QUANTITY), never on a proxy, never on a
residual, never on a single station.  SELFTEST ARM 7 is the direct regression
test for that failure: a history that is flat at a non-gated station while the
gated stations travel MUST REFUSE.

-----------------------------------------------------------------------------
USAGE
    grade_vmfl008.py --selftest            # 7 arms; exit 0 all pass, exit 2 refuse
    grade_vmfl008.py --grade <run_root>    # exit 0 PASS, 1 GATE FAIL/NOT A RESULT,
                                           # 2 REFUSE (guard tripped)
-----------------------------------------------------------------------------
"""

import os
import sys
import json
import math
import glob
import hashlib
import tempfile
import shutil

# =============================================================================
# FROZEN CONSTANTS.  Every one of these is fixed at the pre-registration commit
# and the grading path is fixed BY SHA (CLAUDE.md rule 2).
# =============================================================================

# ---- physics, from the manual's PRINTED TEXT at p. 31 (no plate was read) ----
OMEGA        = 1.0          # rad/s, lid spin rate                    (p. 31)
R_CAV        = 1.0          # m, cavity radius                        (p. 31)
H_CAV        = 1.0          # m, cavity height                        (p. 31)
RHO          = 1.0          # kg/m3                                   (p. 31)
MU           = 0.000556     # kg/m-s                                  (p. 31)
U_TIP        = OMEGA * R_CAV                      # = 1.0 m/s, the lid tip speed
RE_STATED    = 1800.0                             # manual's stated Re      (p. 31)
X_SECTION    = 0.6          # m, the manual's section station         (p. 31)

# ---- the gate ---------------------------------------------------------------
# TOL is PHYSICAL and ANSWER-BLIND: 5 % of the tip speed, the only velocity scale
# the manual's TEXT gives.  It is NOT a fraction of a plotted axis range and was
# NOT chosen after seeing any digitized number (25.2).
TOL          = 0.05 * U_TIP                       # = 0.050000 m/s

# Frozen read stations, r/R.  A FINITE FROZEN SET, and every station is reported
# individually -- 16.3 warns that a domain max is a reduction whose argmax can
# move, so there is no hidden reduction here: the gate is "ALL stations inside",
# which is the max over a set that cannot change.
# r/R = 0 excluded (axis, V_theta == 0 by symmetry, a trivial station).
# r/R = 1 excluded (stationary side wall, V_theta == 0 by BC, a trivial station).
STATIONS     = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
ROACHE_STATION = 0.5        # the single scalar carried through the Roache triple

# ---- grid family (rule 5) ---------------------------------------------------
LEVELS       = ("L1", "L2", "L3")     # L1 COARSEST, L3 FINEST
REFINE_R     = 2.0
CELLS        = {"L1": 1024, "L2": 4096, "L3": 16384}   # 32^2 / 64^2 / 128^2

# ---- strict completion rule (CLAUDE.md rule 4) ------------------------------
ENDTIME      = 20000        # SIMPLE iterations; stopAt endTime, NO residualControl,
                            # so "last time == endTime" is LITERALLY testable.
                            # This also makes VMFL011-R3's cost datum valid: 27
                            # voids an estimator datum across a CHANGE of stopping
                            # criterion, and this criterion is unchanged from it.
REQUIRED_FIELDS = ("U", "p")
AGE_GUARD_REF   = "0/U"     # touched last at launch; dates the run allowed to answer

# ---- plateau, PER QUANTITY (21.1), ON THE GATED QUANTITY (31.1) -------------
PLATEAU_W       = 2000      # final-window iterations
PLATEAU_DELTA   = 0.01 * TOL      # = 5.0e-04 m/s, 1 % of the band.  FROZEN BEFORE
                                  # COMPUTE (16.1: a plateau criterion frozen after
                                  # compute is not a criterion) and BINDING INCLUDING
                                  # IF IT FAILS.
SAMPLE_INTERVAL = 500       # iterations between sampled sets -> 40 samples/level

# ---- Roache classification --------------------------------------------------
FS_GCI       = 1.25
EXACT_EPS    = 1.0e-12      # below this a difference is EXACT, not converging
STAGNANT_BAND= 0.05         # |R - 1| <= this -> STAGNANT

# ---- rule 3 planted control -------------------------------------------------
PLANT        = 1.234e-03    # m/s, the lab's standing plant magnitude
PLANT_TOL    = 0.10         # recovered plant must be within 10 % of planted

# ---- 25.6 / 25.4 : the digitized read-off uncertainty -----------------------
# NOT A NUMBER IN THIS FILE.  Consumed from the per-case calibration artifact.
UREAD_JSON   = "reference/UREAD_VMFL008.json"
# The per-case calibration is FROZEN BEFORE THE READ-OFF (25.2 point 2) and its
# sha256 is written here AT THE FREEZE COMMIT.  While unset, this comparator
# REFUSES: it cannot grade against an unpinned instrument.
UREAD_JSON_SHA256 = ""      # <-- FILLED AT FREEZE.  See PREREGISTRATION.md sec 9.

# 28.2 -- THE UNITS THE GATED QUANTITY IS IN, AND THE ARTIFACT MUST DECLARE THEM.
# 28.2: "every term of 25.4 -- the synthetic-control statistic, the pixel floor, and
# the half-spread of the two read-offs -- is computed ON THE GATED QUANTITY, IN THAT
# QUANTITY'S OWN UNITS."  Presence of the key proves nothing; an artifact declaring
# "ft/s" or the R2 instrument's placeholder "y-data" would otherwise pass intact and
# be folded into a band in m/s.  This is the guard for that clause.
UREAD_UNITS  = "m/s"        # swirl velocity V_theta; the gate, tol and band are all m/s

# 25.4 terms the artifact must carry.  Dereferenced below, so they are PRESENCE-
# CHECKED FIRST: a missing key must REFUSE (exit 2), never raise KeyError -> exit 1.
# A launcher that distinguishes a refusal from a crash misclassifies the latter.
UREAD_TERM_KEYS = ("term_A", "half_spread", "pixel_floor", "max")

# 28.2 / SUPERVISOR RULING 2 -- THE AXIS THE TERMS WERE COMPUTED ON, NAMED.
# The two keys below (`y_span_data_units`, `plate_interior_px_h`) are y-SHAPED
# names, and they are correct for THIS case, which gates a VALUE read on the
# plotted y quantity.  But a POSITION gate reads the x axis, and a position
# artifact would carry an x span and an interior WIDTH in those same y-named
# fields -- dimensionally wrong and completely invisible from the key names.
# 28.2 forbids licensing one quantity's gate with another's u_read, and the `dim`
# check below is not sufficient on its own: it says WHICH KIND of read it is and
# says nothing about which axis the span and the interior extent were measured on.
# So the producer must ALSO name the gated axis unambiguously, and the y-named
# fields must be PROVEN to be that axis's, not assumed to be.
UREAD_AXIS_KEYS   = ("gated_axis", "gated_span_data_units", "gated_interior_px")
UREAD_GATED_AXIS  = "y"     # this case gates a VALUE read; its axis is y

# The extraction geometry the per-case calibration MUST have been matched to
# (28.6 answer-blind format).  Recorded so a mismatch refuses rather than
# silently rescaling a floor.
PLATE_INTERIOR_PX_H = 495   # interior plot-box height, px, at the frozen DPI
CAP_RATIO_TRIGGER   = 1.0 / 3.0   # 25.6: u_read >= tol/3 -> CAPPED AT GATE REACHED


class Refuse(SystemExit):
    def __init__(self, msg):
        SystemExit.__init__(self, 2)
        self.msg = msg


def refuse(msg):
    sys.stderr.write("REFUSE (exit 2): %s\n" % msg)
    raise Refuse(msg)


# =============================================================================
# u_read -- CONSUMED, NEVER ASSUMED (28.6)
# =============================================================================
def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(65536), b""):
            h.update(blk)
    return h.hexdigest()


def _load_uread(case_dir):
    """Load the PER-CASE u_read.  Refuses rather than degrading, on every path.

    DEFECT 1 DISCIPLINE: the R2 instrument's verdict-bearing exit path never ran,
    so a verdict is NEVER inferred from an exit code here.  Only an explicit
    recorded "PASS" in the persisted JSON is accepted.
    """
    path = os.path.join(case_dir, UREAD_JSON)
    if not os.path.isfile(path):
        refuse("per-case u_read artifact missing: %s -- 28.6 requires u_read be "
               "RE-DERIVED for VMFL008's own answer-blind plate format; register "
               "row #56's 0.00505051 is the R2 plate's number and does not transfer"
               % path)
    if len(UREAD_JSON_SHA256) != 64 or any(c not in "0123456789abcdef"
                                           for c in UREAD_JSON_SHA256):
        refuse("UREAD_JSON_SHA256 is unset or malformed -- the grading path is fixed "
               "BY SHA (rule 2) and this comparator will not grade against an "
               "unpinned instrument.  It is filled at the freeze commit.")
    got = _sha256_file(path)
    if got != UREAD_JSON_SHA256:
        refuse("u_read artifact sha mismatch: on disk %s, frozen %s -- the file that "
               "ran is not the file that was registered" % (got, UREAD_JSON_SHA256))
    with open(path) as fh:
        d = json.load(fh)

    for k in ("dim", "units", "u_read", "statistic", "verdict", "terms",
              "plate_interior_px_h", "y_span_data_units") + UREAD_AXIS_KEYS:
        if k not in d:
            refuse("u_read artifact missing required key %r" % k)
    if d["dim"] != "value":
        refuse("u_read artifact is for dim=%r; this case gates on a VALUE read and "
               "28.2 forbids licensing one quantity's gate with another's u_read"
               % d["dim"])
    # 28.2 UNITS ARE VALUE-CHECKED, NOT MERELY PRESENT.  The dim check above says
    # WHICH KIND of read it is; it says nothing about what the number is measured
    # in.  An artifact declaring "ft/s" -- or the frozen instrument's own
    # dimensionless placeholder "y-data" (digitize_calibrate.py:337) -- is a
    # dimensionally meaningless term to fold into a band in m/s.
    if d["units"] != UREAD_UNITS:
        refuse("u_read artifact declares units=%r, not %r -- 28.2 requires every "
               "25.4 term be computed on the gated quantity IN THAT QUANTITY'S OWN "
               "UNITS, and this gate, its tol and its band are all in %s.  The "
               "frozen instrument's ValueQuantity.units is the placeholder 'y-data'; "
               "the per-case calibration must emit the physical unit"
               % (d["units"], UREAD_UNITS, UREAD_UNITS))
    if d["verdict"] != "PASS":
        refuse("per-case calibration verdict is %r, not PASS -- 25.7 authorises no "
               "digitized gate on an instrument that did not certify" % d["verdict"])
    if int(d["plate_interior_px_h"]) != PLATE_INTERIOR_PX_H:
        refuse("calibration plate interior height %s px != frozen %s px -- 28.6 "
               "requires the synthetic plates be matched to the TARGET's "
               "answer-blind format" % (d["plate_interior_px_h"], PLATE_INTERIOR_PX_H))

    # SUPERVISOR RULING 2 -- the gated axis is NAMED and the y-shaped keys are
    # PROVEN to be that axis's.  No number below is changed by these checks; they
    # can only turn an acceptance into a refusal, never the reverse.
    if d["gated_axis"] != UREAD_GATED_AXIS:
        refuse("u_read artifact was calibrated on the %r axis; this case gates a "
               "VALUE read on the %r axis.  28.2: a u_read derived for one gated "
               "quantity does not license a gate on another, and the y-named keys "
               "`y_span_data_units`/`plate_interior_px_h` would otherwise carry an "
               "x span and an interior WIDTH with nothing in the key names to say so"
               % (d["gated_axis"], UREAD_GATED_AXIS))
    if float(d["gated_span_data_units"]) != float(d["y_span_data_units"]):
        refuse("u_read artifact is internally inconsistent: gated_span_data_units "
               "%.17g != y_span_data_units %.17g -- the unambiguous field and the "
               "frozen-contract field must be the same measurement"
               % (float(d["gated_span_data_units"]), float(d["y_span_data_units"])))
    if float(d["gated_interior_px"]) != float(d["plate_interior_px_h"]):
        refuse("u_read artifact is internally inconsistent: gated_interior_px %.17g "
               "!= plate_interior_px_h %.17g"
               % (float(d["gated_interior_px"]), float(d["plate_interior_px_h"])))

    u = float(d["u_read"])
    if not (u > 0.0) or not math.isfinite(u):
        refuse("u_read is not a positive finite number: %r" % u)

    # 25.4: u_read is the MAXIMUM of three floors.  Re-assert it here rather than
    # trusting the producer -- a lesson is not applied until every call site
    # asserts it (L-221/L-222).
    t = d["terms"]
    # The sub-keys below are DEREFERENCED, so they are presence-checked HERE, on the
    # file's own refuse->exit-2 convention.  Without this loop a missing key raises
    # KeyError -> traceback -> exit 1, i.e. it fails loudly WEARING THE WRONG EXIT
    # CODE, and a launcher that distinguishes a guard refusal (2) from a comparator
    # crash (1) misclassifies it.  The top-level presence loop above never covered
    # these because they live one level down.
    if not isinstance(t, dict):
        refuse("u_read artifact key 'terms' is %s, not an object -- the 25.4 terms "
               "cannot be read" % type(t).__name__)
    for k in UREAD_TERM_KEYS:
        if k not in t:
            refuse("u_read artifact 'terms' missing required sub-key %r -- 25.4's "
                   "three floors and 29.3's admissibility test are all re-asserted "
                   "here rather than trusted from the producer (L-221/L-222), and "
                   "they cannot be asserted against a term that is absent" % k)
    floor = float(d["y_span_data_units"]) / float(PLATE_INTERIOR_PX_H)
    three = (float(t["term_A"]), float(t["half_spread"]), floor)
    if abs(u - max(three)) > 1e-12 * max(1.0, u):
        refuse("u_read %.8g is not max(term_A, half_spread, pixel_floor) = %.8g "
               "(25.4)" % (u, max(three)))
    if abs(float(t["pixel_floor"]) - floor) > 1e-12 * max(1.0, floor):
        refuse("recorded pixel_floor %.8g != y_span/interior_px = %.8g"
               % (float(t["pixel_floor"]), floor))

    # 29.3 admissibility: rms is permitted ONLY where the max per-plate error is
    # below the pixel floor.  Otherwise 'max' is COMPELLED.  Refused in code, not
    # warned about -- that is the R1 defect this repairs.
    mx = float(t["max"])
    if d["statistic"] == "rms" and not (mx < floor):
        refuse("29.3: rms statistic INADMISSIBLE -- max per-plate error %.8g >= "
               "pixel floor %.8g; a tailed quantity must use 'max'" % (mx, floor))
    if d["statistic"] not in ("rms", "max", "p95"):
        refuse("unknown u_read statistic %r" % d["statistic"])
    return u, d


def band(tol, u_read):
    """25.6 fold.  QUADRATURE-WIDENING ONLY: u_read can NEVER shrink a band (25.4).

    Asserted, not asserted-in-prose: the return is checked >= tol on every call.
    """
    if u_read < 0.0:
        refuse("negative u_read %r" % u_read)
    b = math.sqrt(tol * tol + u_read * u_read)
    if b < tol - 1e-15:
        refuse("BAND SHRANK: sqrt(tol^2+u_read^2)=%.12g < tol=%.12g -- 25.4 forbids "
               "a digitized reference making a gate easier than the physical "
               "tolerance alone" % (b, tol))
    return b


def cap_verdict(tol, u_read):
    """25.6 THE CAP.  Computed and printed on EVERY run, whatever the verdict."""
    ratio = u_read / tol
    capped = (ratio >= CAP_RATIO_TRIGGER)
    return ratio, capped


# =============================================================================
# READERS -- everything the gate consumes goes through these, so the planted
# control in --selftest exercises the REAL path (rule 3).
# =============================================================================
def read_sample_file(path):
    """Read one OpenFOAM `sets` line sample.  Returns (r[], Vr[], Vth[], Vz[]).

    The sector is frozen so the sample line lies at theta = 0 (the one-cell
    sector's own centre plane), where the cylindrical components are the
    Cartesian ones with no trigonometry:  V_r = Ux, V_theta = Uy, V_z = Uz.
    A planted perturbation in --selftest travels through THIS function.
    """
    if not os.path.isfile(path):
        refuse("sample file missing: %s" % path)
    r, vr, vt, vz = [], [], [], []
    with open(path) as fh:
        for ln in fh:
            s = ln.strip()
            if not s or s.startswith("#"):
                continue
            f = s.split()
            if len(f) == 4:          # x Ux Uy Uz
                x, ux, uy, uz = (float(v) for v in f)
            elif len(f) == 6:        # x y z Ux Uy Uz
                x, _y, _z, ux, uy, uz = (float(v) for v in f)
            else:
                refuse("unrecognised sample column count %d in %s -- refusing "
                       "rather than guessing a column mapping" % (len(f), path))
            r.append(x); vr.append(ux); vt.append(uy); vz.append(uz)
    if len(r) < len(STATIONS) + 2:
        refuse("sample file %s has %d rows, too few to interpolate %d stations"
               % (path, len(r), len(STATIONS)))
    if any(r[i + 1] <= r[i] for i in range(len(r) - 1)):
        refuse("sample abscissae not strictly increasing in %s" % path)
    return r, vr, vt, vz


def interp_at(xs, ys, x):
    if x < xs[0] - 1e-12 or x > xs[-1] + 1e-12:
        refuse("station %.6g outside sampled range [%.6g, %.6g]" % (x, xs[0], xs[-1]))
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            t = (x - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] + t * (ys[i + 1] - ys[i])
    return ys[-1]


def swirl_at_stations(path):
    r, _vr, vt, _vz = read_sample_file(path)
    return [interp_at(r, vt, s * R_CAV) for s in STATIONS]


def read_reference(case_dir):
    """The DIGITIZED reference, produced AFTER the freeze by the frozen read-off
    script, into a file the frozen registration already commits to consuming
    (25.2 point 4)."""
    path = os.path.join(case_dir, "reference", "REF_VMFL008_SWIRL.json")
    if not os.path.isfile(path):
        refuse("digitized reference missing: %s" % path)
    with open(path) as fh:
        d = json.load(fh)
    for k in ("figure", "page", "plate_sha256", "x", "y", "quantity"):
        if k not in d:
            refuse("digitized reference missing key %r" % k)
    if d["quantity"] != "swirl_velocity":
        refuse("digitized reference is for %r, gate is swirl_velocity" % d["quantity"])
    xs, ys = [float(v) for v in d["x"]], [float(v) for v in d["y"]]
    if len(xs) != len(ys) or len(xs) < 5:
        refuse("digitized reference curve is malformed")
    return [interp_at(xs, ys, s * R_CAV) for s in STATIONS], d


# =============================================================================
# STRICT COMPLETION RULE -- CLAUDE.md rule 4, all six conditions, REFUSE not degrade
# =============================================================================
def _time_dirs(level_dir):
    out = []
    for d in os.listdir(level_dir):
        p = os.path.join(level_dir, d)
        if os.path.isdir(p):
            try:
                out.append((float(d), d))
            except ValueError:
                pass
    return sorted(out)


def check_completion(level_dir):
    """Returns [] if complete, else a list of the conditions that failed."""
    bad = []

    rcp = os.path.join(level_dir, "RUN_RC")
    if not os.path.isfile(rcp):
        bad.append("RUN_RC missing")
    else:
        with open(rcp) as fh:
            txt = fh.read().strip()
        if txt != "0":
            bad.append("rc != 0 (rc=%r)" % txt)

    logp = os.path.join(level_dir, "log.simpleFoam")
    log = ""
    if not os.path.isfile(logp):
        bad.append("log.simpleFoam missing")
    else:
        with open(logp, errors="replace") as fh:
            log = fh.read()
        if "\nEnd\n" not in log and not log.rstrip().endswith("End"):
            bad.append("no End line")
        n_exec = log.count("ExecutionTime = ")
        if n_exec != ENDTIME:
            bad.append("ExecutionTime count %d != endTime %d" % (n_exec, ENDTIME))

    tds = _time_dirs(level_dir)
    if not tds:
        bad.append("no time directories")
    else:
        last_t, last_name = tds[-1]
        if abs(last_t - float(ENDTIME)) > 1e-9:
            bad.append("last time %g != endTime %d" % (last_t, ENDTIME))
        endd = os.path.join(level_dir, last_name)
        for f in REQUIRED_FIELDS:
            if not os.path.isfile(os.path.join(endd, f)):
                bad.append("field %s missing at endTime" % f)

        # THE AGE GUARD.  0/U is touched last at launch and so DATES the run
        # allowed to produce the answer.  A field not newer than it is a field
        # from some earlier run.
        ref = os.path.join(level_dir, AGE_GUARD_REF)
        if not os.path.isfile(ref):
            bad.append("age-guard reference %s missing" % AGE_GUARD_REF)
        else:
            t_ref = os.path.getmtime(ref)
            for f in REQUIRED_FIELDS:
                fp = os.path.join(endd, f)
                if os.path.isfile(fp) and not (os.path.getmtime(fp) > t_ref):
                    bad.append("AGE GUARD: %s at endTime is NOT newer than %s"
                               % (f, AGE_GUARD_REF))
    return bad


# =============================================================================
# PLATEAU -- ON THE GATED QUANTITY, AT EVERY GATED STATION (21.1, 31.1)
# =============================================================================
def plateau_check(level_dir):
    """The regression test for the failure that demoted rows #54 and #55.

    The plateau is measured on V_theta AT THE GATED STATIONS, over the final
    PLATEAU_W iterations.  It is NOT a residual, NOT a proxy, and NOT a single
    upstream station that cannot causally see the gated quantity.

    Returns (ok, drift_by_station, n_samples_in_window).
    """
    setdir = os.path.join(level_dir, "postProcessing", "gateLine")
    if not os.path.isdir(setdir):
        refuse("plateau: sampled-set directory missing: %s" % setdir)
    times = []
    for d in os.listdir(setdir):
        try:
            times.append((float(d), d))
        except ValueError:
            pass
    times.sort()
    if not times:
        refuse("plateau: no sampled times under %s" % setdir)
    if abs(times[-1][0] - float(ENDTIME)) > 1e-9:
        refuse("plateau: last sampled time %g != endTime %d" % (times[-1][0], ENDTIME))

    win = [t for t in times if t[0] >= float(ENDTIME - PLATEAU_W) - 1e-9]
    if len(win) < 2:
        refuse("plateau: only %d sample(s) in the final %d-iteration window; a "
               "plateau cannot be measured from one sample (a single final sample "
               "with no history comparison is exactly what blinded rows #54/#55)"
               % (len(win), PLATEAU_W))

    series = []
    for _t, name in win:
        f = glob.glob(os.path.join(setdir, name, "*U*.xy"))
        if len(f) != 1:
            refuse("plateau: expected exactly one U sample file in %s, found %d"
                   % (os.path.join(setdir, name), len(f)))
        series.append(swirl_at_stations(f[0]))

    drift = []
    for j in range(len(STATIONS)):
        vals = [s[j] for s in series]
        drift.append(max(vals) - min(vals))
    ok = all(d <= PLATEAU_DELTA for d in drift)
    return ok, drift, len(win)


# =============================================================================
# ROACHE (CLAUDE.md rule 5)
# =============================================================================
def roache(f1, f2, f3, r=REFINE_R):
    """f1 COARSEST, f3 FINEST.  Returns (classification, R, p_obs, gci_fine).

    p_obs and gci are None for every non-CONVERGING class: rule 5 forbids quoting
    a GCI when the three values are not monotone.
    """
    e21 = f2 - f1
    e32 = f3 - f2
    if abs(e21) < EXACT_EPS or abs(e32) < EXACT_EPS:
        return "EXACT", None, None, None
    R = e32 / e21
    if R < 0.0:
        return "OSCILLATORY", R, None, None
    if R > 1.0:
        return "DIVERGENT", R, None, None
    if abs(R - 1.0) <= STAGNANT_BAND:
        return "STAGNANT", R, None, None
    p = math.log(1.0 / R) / math.log(r)
    gci = FS_GCI * abs(e32 / f3) / (r ** p - 1.0) if abs(f3) > 0.0 else None
    return "CONVERGING", R, p, gci


# =============================================================================
# SELFTEST -- 7 arms.  Every plant goes to DISK and comes back through the REAL
# reader (rule 3).  Any arm that cannot see its plant REFUSES (exit 2).
# =============================================================================
def _write_sample(path, rvals, vth):
    with open(path, "w") as fh:
        fh.write("# x Ux Uy Uz\n")
        for r, v in zip(rvals, vth):
            fh.write("%.10g 0.0 %.10g 0.0\n" % (r, v))


def _synth_profile(rvals, scale=1.0, offset=0.0):
    # a smooth, monotone, physically-shaped stand-in; NOT a prediction of the case
    return [offset + scale * 0.30 * (r ** 1.5) for r in rvals]


def selftest():
    fails = []
    tmp = tempfile.mkdtemp(prefix="vmfl008_selftest_")
    try:
        rvals = [i / 40.0 for i in range(41)]      # 0.000 .. 1.000

        # ---- ARM 1 : PLANT-DETECT through a REAL DISK ROUND TRIP (rule 3) ----
        # The whole point: a zero from a reader not shown able to see a non-zero
        # is not evidence.  The plant is written to disk and read back through
        # read_sample_file -> interp_at -> swirl_at_stations, the SAME chain the
        # gate uses, including the Cartesian->cylindrical component mapping.
        base = _synth_profile(rvals)
        p_clean = os.path.join(tmp, "clean_U.xy")
        _write_sample(p_clean, rvals, base)
        v_clean = swirl_at_stations(p_clean)

        planted = [v + PLANT for v in base]
        p_plant = os.path.join(tmp, "planted_U.xy")
        _write_sample(p_plant, rvals, planted)
        v_plant = swirl_at_stations(p_plant)

        rec = [b - a for a, b in zip(v_clean, v_plant)]
        worst = max(abs(d - PLANT) for d in rec)
        if worst > PLANT_TOL * abs(PLANT):
            refuse("ARM 1 PLANT-DETECT: reader recovered a worst-case %.6g against a "
                   "planted %.6g -- the reader cannot see a known non-zero, so its "
                   "agreement with anything is worthless" % (max(rec), PLANT))
        print("ARM 1 PLANT-DETECT      : PASS  planted %.6g, recovered %.6g..%.6g "
              "(worst dev %.3g <= %.3g)"
              % (PLANT, min(rec), max(rec), worst, PLANT_TOL * abs(PLANT)))

        # ---- ARM 2 : PLANT-NULL, AND ITS POWER IS STATED HONESTLY ------------
        # Register row #56 DEFECT 2 is that POSITION's null cannot fail by
        # construction.  This null CAN fail: its threshold (exact zero to 1e-14)
        # is INDEPENDENT of the plant magnitude, so a reader returning a constant,
        # or a reader with state leaking between reads, fails it.  But it is still
        # the WEAK arm and discrimination rests on ARM 1 -- stated, not implied.
        p_clean2 = os.path.join(tmp, "clean2_U.xy")
        _write_sample(p_clean2, rvals, base)
        v_clean2 = swirl_at_stations(p_clean2)
        null_off = max(abs(a - b) for a, b in zip(v_clean, v_clean2))
        if null_off > 1e-14:
            refuse("ARM 2 PLANT-NULL: an unperturbed re-read moved by %.3g; a reader "
                   "that reports displacement on a clean plate is disqualified"
                   % null_off)
        print("ARM 2 PLANT-NULL        : PASS  clean re-read offset %.3g <= 1e-14  "
              "[THRESHOLD IS INDEPENDENT OF THE PLANT, so this null CAN fail -- "
              "unlike the DIGITIZER's POSITION null (row #56 DEFECT 2), which "
              "cannot.  Discrimination still rests on ARM 1.]" % null_off)

        # ---- ARM 3 : THE BAND NEVER SHRINKS (25.4) ---------------------------
        for u in (0.0, 1e-9, 0.1 * TOL, TOL, 10.0 * TOL):
            b = band(TOL, u)
            if b < TOL - 1e-15:
                fails.append("ARM 3: band shrank at u_read=%g" % u)
            exp = math.sqrt(TOL * TOL + u * u)
            if abs(b - exp) > 1e-15:
                fails.append("ARM 3: band != quadrature at u_read=%g" % u)
        if abs(band(TOL, 0.0) - TOL) > 1e-15:
            fails.append("ARM 3: u_read=0 must reduce exactly to tol")
        print("ARM 3 BAND-NEVER-SHRINKS: PASS  quadrature-widening only; "
              "u_read=0 -> band == tol exactly (%.8g)" % TOL)

        # ---- ARM 4 : THE 25.6 CAP FIRES AT THE BOUNDARY, INCLUSIVE -----------
        r_lo, cap_lo = cap_verdict(TOL, TOL / 3.0 - 1e-12)
        r_eq, cap_eq = cap_verdict(TOL, TOL / 3.0)
        r_hi, cap_hi = cap_verdict(TOL, TOL / 3.0 + 1e-12)
        if cap_lo or not cap_eq or not cap_hi:
            fails.append("ARM 4: cap must fire at u_read >= tol/3 INCLUSIVE "
                         "(got %s/%s/%s)" % (cap_lo, cap_eq, cap_hi))
        print("ARM 4 CAP-BOUNDARY      : PASS  ratio %.6f/%.6f/%.6f -> capped "
              "%s/%s/%s  (25.6 trigger is >=, not >)"
              % (r_lo, r_eq, r_hi, cap_lo, cap_eq, cap_hi))

        # ---- ARM 5 : STRICT COMPLETION REFUSES EACH VIOLATION (rule 4) -------
        import time as _time

        def _mk_run(ok_rc=True, end_line=True, exec_n=ENDTIME, last_t=ENDTIME,
                    fields=REQUIRED_FIELDS, age_ok=True):
            d = tempfile.mkdtemp(dir=tmp)
            os.makedirs(os.path.join(d, "0"))
            with open(os.path.join(d, "0", "U"), "w") as fh:
                fh.write("ref\n")
            _time.sleep(0.01)
            with open(os.path.join(d, "RUN_RC"), "w") as fh:
                fh.write("0" if ok_rc else "124")
            with open(os.path.join(d, "log.simpleFoam"), "w") as fh:
                fh.write("ExecutionTime = 1 s\n" * exec_n)
                if end_line:
                    fh.write("End\n")
            td = os.path.join(d, str(last_t))
            os.makedirs(td)
            if not age_ok:
                # a field OLDER than 0/U -- a leftover from an earlier run
                for f in fields:
                    with open(os.path.join(td, f), "w") as fh:
                        fh.write("x\n")
                    old = os.path.getmtime(os.path.join(d, "0", "U")) - 100.0
                    os.utime(os.path.join(td, f), (old, old))
            else:
                _time.sleep(0.01)
                for f in fields:
                    with open(os.path.join(td, f), "w") as fh:
                        fh.write("x\n")
            return d

        cases = [
            ("compliant",        _mk_run(),                          0),
            ("rc != 0",          _mk_run(ok_rc=False),               1),
            ("no End line",      _mk_run(end_line=False),            1),
            ("ExecutionTime n",  _mk_run(exec_n=ENDTIME - 1),        1),
            ("last != endTime",  _mk_run(last_t=ENDTIME - 500),      1),
            ("field missing",    _mk_run(fields=("U",)),             1),
            ("AGE GUARD",        _mk_run(age_ok=False),              1),
        ]
        for name, d, want in cases:
            bad = check_completion(d)
            got = 1 if bad else 0
            if got < want:
                fails.append("ARM 5: '%s' was NOT caught by the completion check" % name)
            if name == "compliant" and bad:
                fails.append("ARM 5: a compliant run was refused: %s" % bad)
        print("ARM 5 STRICT-COMPLETION : PASS  all 6 violations caught "
              "(rc, End, ExecutionTime count, last==endTime, fields, AGE GUARD); "
              "compliant run accepted")

        # ---- ARM 6 : ROACHE CLASSIFIES, AND QUOTES NO GCI OFF-MONOTONE -------
        checks = [
            ("CONVERGING",  (1.00, 1.20, 1.25)),   # R = 0.25
            ("DIVERGENT",   (1.00, 1.10, 1.40)),   # R = 3.0
            ("OSCILLATORY", (1.00, 1.20, 1.10)),   # R < 0
            ("STAGNANT",    (1.00, 1.10, 1.20)),   # R = 1.0
            ("EXACT",       (1.00, 1.00, 1.00)),
        ]
        for want, (a, b, c) in checks:
            cls, R, p, g = roache(a, b, c)
            if cls != want:
                fails.append("ARM 6: (%g,%g,%g) -> %s, expected %s" % (a, b, c, cls, want))
            if cls != "CONVERGING" and (p is not None or g is not None):
                fails.append("ARM 6: %s must quote NO p_obs and NO GCI (rule 5)" % cls)
            if cls == "CONVERGING" and (p is None or g is None):
                fails.append("ARM 6: CONVERGING must report p_obs and GCI")
        cls, R, p, g = roache(1.00, 1.20, 1.25)
        if abs(p - math.log(4.0) / math.log(2.0)) > 1e-9:
            fails.append("ARM 6: p_obs arithmetic wrong (got %r)" % p)
        print("ARM 6 ROACHE            : PASS  5 classes correct; p_obs=%.6f, "
              "GCI_fine=%.6f at Fs=%.2f; NO GCI quoted for any non-CONVERGING class"
              % (p, g, FS_GCI))

        # ---- ARM 7 : THE VMFL046 BLINDNESS REGRESSION (31.1) -----------------
        # A history FLAT at a non-gated station while the GATED stations travel.
        # This is precisely rows #54/#55: |dM| = 4.332e-10 while the gated
        # quantity moved 192.60 % of its band.  The plateau MUST refuse.
        lvl = tempfile.mkdtemp(dir=tmp)
        sd = os.path.join(lvl, "postProcessing", "gateLine")
        travel = 5.0 * PLATEAU_DELTA          # gated stations move 5x the criterion
        n_win = PLATEAU_W // SAMPLE_INTERVAL + 1
        for k in range(n_win):
            t = ENDTIME - PLATEAU_W + k * SAMPLE_INTERVAL
            os.makedirs(os.path.join(sd, str(t)))
            prof = _synth_profile(rvals, offset=k * travel / max(1, n_win - 1))
            # the non-gated station r=1.0 is pinned EXACTLY -- the blind station
            prof[-1] = base[-1]
            _write_sample(os.path.join(sd, str(t), "line_U.xy"), rvals, prof)
        ok, drift, nwin = plateau_check(lvl)
        if ok:
            refuse("ARM 7 BLINDNESS REGRESSION: the plateau ACCEPTED a history in "
                   "which the gated stations travelled %.3g m/s (%.1fx the %.3g "
                   "criterion) while a non-gated station sat exactly still.  That is "
                   "the rows #54/#55 failure -- a blind station wearing three coats "
                   "-- and this comparator must never reproduce it." %
                   (travel, travel / PLATEAU_DELTA, PLATEAU_DELTA))
        # The blind station's drift is MEASURED off the same files, never asserted:
        # a printed number that was not read from disk is the defect this arm exists
        # to catch, and printing one here would reproduce it inside the control.
        _blind_series = []
        for _t, _name in sorted((float(d), d) for d in os.listdir(sd)):
            _r, _vr, _vt, _vz = read_sample_file(os.path.join(sd, _name, "line_U.xy"))
            _blind_series.append(interp_at(_r, _vt, 1.0 * R_CAV))
        blind = max(_blind_series) - min(_blind_series)
        if blind > 1e-14:
            fails.append("ARM 7: the blind station was meant to be pinned but moved "
                         "%.3g -- the control does not demonstrate what it claims"
                         % blind)
        print("ARM 7 BLINDNESS-REGRESS : PASS  gated-station drift %.3g..%.3g m/s "
              "vs criterion %.3g -> plateau REFUSED, while the non-gated station "
              "drift was %.3g.  The plateau reads THE GATED QUANTITY (21.1, 31.1)."
              % (min(drift), max(drift), PLATEAU_DELTA, blind))

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        for f in fails:
            sys.stderr.write("SELFTEST FAIL: %s\n" % f)
        refuse("%d selftest assertion(s) failed" % len(fails))
    print("SELFTEST: 7 arms ALL PASS")
    return 0


# =============================================================================
# GRADE
# =============================================================================
def grade(run_root, case_dir):
    print("VMFL008 -- Flow Inside a Rotating Cavity (VM2026R1 p. 31), gate on "
          "SWIRL VELOCITY at X = %.3g m, Fig .08.3 (p. 33)" % X_SECTION)
    print("QUANTITY CLASS: **VALUE** (a magnitude off a curve at frozen abscissae), "
          "not POSITION.")

    u_read, ud = _load_uread(case_dir)
    b = band(TOL, u_read)
    ratio, capped = cap_verdict(TOL, u_read)

    # 25.6: printed on EVERY run, whatever the verdict, ON THE FIRST LINES.
    print("--- 25.6 BAND AND CAP -------------------------------------------------")
    print("tol           = %.8g m/s   (5 %% of tip speed U_tip = Omega*R = %.6g m/s, "
          "manual p. 31 TEXT; answer-blind)" % (TOL, U_TIP))
    print("u_read        = %.8g m/s   (PER-CASE, 28.6; statistic %r; "
          "y-span %.6g m/s over %d px interior)"
          % (u_read, ud["statistic"], float(ud["y_span_data_units"]),
             PLATE_INTERIOR_PX_H))
    print("band          = sqrt(tol^2 + u_read^2) = %.8g m/s  (widening %+.4f %%)"
          % (b, 100.0 * (b / TOL - 1.0)))
    print("u_read / tol  = %.6f   (25.6 trigger %.6f)" % (ratio, CAP_RATIO_TRIGGER))
    print("CEILING       = %s" % ("**CAPPED AT GATE REACHED** -- the instrument, not "
                                  "the physics, is materially deciding this verdict"
                                  if capped else "PASS-CAPABLE"))
    print("-----------------------------------------------------------------------")

    ref, refd = read_reference(case_dir)
    print("reference: %s p.%s, plate sha256 %s" %
          (refd["figure"], refd["page"], refd["plate_sha256"][:16] + "..."))

    # --- rule 4 + plateau, PER LEVEL ---
    vals = {}
    not_a_result = []
    for lv in LEVELS:
        ld = os.path.join(run_root, lv)
        bad = check_completion(ld)
        if bad:
            not_a_result.append("%s: incomplete -- %s" % (lv, "; ".join(bad)))
            continue
        ok, drift, nwin = plateau_check(ld)
        print("%s plateau: %d samples in final %d iters; per-station drift "
              "%.4g..%.4g m/s vs criterion %.4g -> %s"
              % (lv, nwin, PLATEAU_W, min(drift), max(drift), PLATEAU_DELTA,
                 "PLATEAU MET" if ok else "NOT PLATEAUED"))
        if not ok:
            not_a_result.append("%s: NOT PLATEAUED on the gated quantity" % lv)
        f = glob.glob(os.path.join(ld, "postProcessing", "gateLine",
                                   str(ENDTIME), "*U*.xy"))
        if len(f) != 1:
            refuse("%s: expected one U sample at endTime, found %d" % (lv, len(f)))
        vals[lv] = swirl_at_stations(f[0])

    if not_a_result:
        print("\nVERDICT: **NOT A RESULT**  (CLAUDE.md rule 5 step 1 -- any level not "
              "iteratively converged or not plateaued)")
        for m in not_a_result:
            print("  - %s" % m)
        return 1

    # --- Roache triple on the frozen scalar (rule 5) ---
    j = STATIONS.index(ROACHE_STATION)
    f1, f2, f3 = vals["L1"][j], vals["L2"][j], vals["L3"][j]
    cls, R, p, gci = roache(f1, f2, f3)
    print("\nRoache on V_theta(r/R=%.2f): L1 %.8g  L2 %.8g  L3 %.8g" %
          (ROACHE_STATION, f1, f2, f3))
    print("  triple = %s, R = %s, p_obs = %s, GCI_fine = %s" %
          (cls, "%.6f" % R if R is not None else "n/a",
           "%.6f" % p if p is not None else "NOT QUOTED (rule 5)",
           "%.4f %%" % (100 * gci) if gci is not None else "NOT QUOTED (rule 5)"))
    if cls != "CONVERGING":
        print("\nVERDICT: **NOT A RESULT**  (rule 5 step 2: triple is %s)" % cls)
        return 1

    # --- the band gate, EVERY station reported (16.3: no hidden reduction) ---
    print("\nstation r/R    CFD (L3)      digitized ref     |diff|        band")
    worst, worst_st, n_out = 0.0, None, 0
    for k, s in enumerate(STATIONS):
        d = abs(vals["L3"][k] - ref[k])
        flag = "" if d <= b else "   <-- OUTSIDE"
        print("  %.2f        %+.8g   %+.8g   %.6g   %.6g%s"
              % (s, vals["L3"][k], ref[k], d, b, flag))
        if d > b:
            n_out += 1
        if d > worst:
            worst, worst_st = d, s

    if n_out:
        print("\nVERDICT: **GATE FAIL**  (%d/%d stations outside the band; worst "
              "%.6g m/s at r/R = %.2f, band %.6g m/s).  A GATE FAIL against a "
              "digitized reference is a GATE FAIL (25.6)."
              % (n_out, len(STATIONS), worst, worst_st, b))
        return 1

    if capped:
        print("\nVERDICT: **GATE REACHED**  (all %d stations inside the band; worst "
              "%.6g m/s at r/R = %.2f).  CAPPED by 25.6: u_read/tol = %.6f >= 1/3, "
              "so this case may NOT become a PASS credential."
              % (len(STATIONS), worst, worst_st, ratio))
        return 0

    print("\nVERDICT: **PASS**  (all %d stations inside the band; worst %.6g m/s at "
          "r/R = %.2f, band %.6g m/s; triple CONVERGING, p_obs %.4f, GCI_fine "
          "%.4f %%)" % (len(STATIONS), worst, worst_st, b, p, 100 * gci))
    return 0


def main(argv):
    case_dir = os.path.dirname(os.path.abspath(__file__))
    if "--selftest" in argv:
        return selftest()
    if "--grade" in argv:
        i = argv.index("--grade")
        if i + 1 >= len(argv):
            refuse("--grade needs a run root")
        return grade(argv[i + 1], case_dir)
    sys.stderr.write(__doc__)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refuse:
        raise
