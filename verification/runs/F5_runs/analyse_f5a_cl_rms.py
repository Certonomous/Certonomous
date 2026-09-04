#!/usr/bin/env python3
"""F5a cylinder ladder -- the Cl_rms comparator.

WHY THIS FILE EXISTS
--------------------
`verification/campaign/F5a_HIGH_RE_RUNGS_PREREGISTRATION.md` gates G1 on
**Cl_rms**.  The ladder's harvester (`run_rung.py:133-152`) stores **`cl_band`**
-- the peak-to-trough ENVELOPE from `time_weighted_stats` (`hi - lo`) -- and
stores no Cl_rms at all.  G1 therefore had no instrument, and the registration
(section 7, gap 2) says so in its own words: *"A comparator must compute Cl_rms,
and one must exist before grading."*  This is that comparator.

WHAT IT DOES NOT DO
-------------------
It does not freeze the registration, it does not grade G1 by itself, and it
launches no compute.  It reads force-coefficient histories that already exist on
disk and computes one statistic from them, under controls.

`cl_band` AND `Cl_rms` ARE NEVER INTERCHANGEABLE
------------------------------------------------
For a PURE SINUSOID of amplitude A they are rigidly related -- band = 2A and
Cl_rms = A/sqrt(2), so band/Cl_rms = 2*sqrt(2) = 2.8284...  A real shedding
signal is not a pure sinusoid, and this ladder's own five rungs measure that
ratio between 2.78 and 3.08.  The ratio is NOT a constant, so an envelope can
never stand in for an RMS: a reader that silently substituted one would grade
G1 on the wrong statistic and would be wrong by a rung-dependent amount.  Every
report this file prints carries BOTH numbers, both labelled, and says which one
a gate would read.

THE DEFINITION IS NOT FIXED BY THE REGISTRATION -- AND THIS FILE REFUSES
------------------------------------------------------------------------
"Cl_rms" is ambiguous in two independent ways, and the pre-registration fixes
NEITHER:

  (a) ABOUT WHAT.   RMS about the window mean (a fluctuation amplitude) or RMS
      about zero (a signal magnitude)?  They differ by the mean lift, which is
      not zero on any of these rungs (Re 3900 corrected: cl_mean = 0.0696).
  (b) WEIGHTED HOW. The ladder's other statistics are TIME-weighted
      (`time_weighted_stats`, trapezoidal) because the time step is adaptive.
      The lab's only existing Cl_rms code, `analyze_re3900.py:66-70`, is
      SAMPLE-weighted (a plain arithmetic mean over samples in the window).

`--grade` therefore REFUSES (rc 2) unless BOTH `--about` and `--weighting` are
given explicitly.  It is not this file's place to choose, and a comparator that
picked a definition silently would be choosing the gate's answer after the data
existed -- exactly what pre-registration exists to prevent.  `--census` reports
all four combinations side by side so the choice can be made on evidence and
recorded as a pre-compute amendment.

CONTROLS (CLAUDE.md rule 3; VERIFICATION_CHARTER section 2)
-----------------------------------------------------------
A root-mean-square is the statistic most likely to return a plausible small
number from a broken reader, so the controls here are ANALYTIC, not recorded:

  C-P1  pure sinusoid, amplitude A, mean zero        -> Cl_rms == A/sqrt(2)
  C-P2  sinusoid on a known offset B                 -> about_mean == A/sqrt(2)
                                                        about_zero == sqrt(B^2 + A^2/2)
        (C-P2 is what DISCRIMINATES the two definitions; a reader that ignores
        `--about` cannot satisfy both halves of it.)
  C-P3  square wave, amplitude A                     -> Cl_rms == A, while
        band/(2*sqrt(2)) == A/sqrt(2).  This is the control that catches an
        ENVELOPE SUBSTITUTION, which C-P1 and C-P2 provably cannot: on a pure
        sinusoid band/(2*sqrt(2)) and the RMS are the same number.
  C-P4  pre-window garbage (constant 99.0 for t < t_start) in every planted
        file, so a broken window filter cannot pass any plant.
  C-P5  the planted signal is written to a real coefficient.dat on disk and
        read back through the SHIPPED path (`parse_coefficient_history`), not
        handed to the statistic in memory.

  C-M1  mutation: replace the shipped statistic with band/(2*sqrt(2)) -- the
        envelope substitution.  The plant suite MUST go red.
  C-M2  mutation: drop the mean subtraction (always about zero).  The plant
        suite MUST go red.
  C-O1  `--selftest` returns the same rc under `python3` and `python3 -O`.

There is no bare `assert` anywhere in this file (L-332/L-475: `python3 -O`
deletes every one).  Every guard raises.

EXIT CODES
----------
    0   EXIT_OK               -- evaluated
    2   EXIT_REFUSE           -- a registered refusal: the instrument declines
   70   EXIT_INSTRUMENT_ERROR -- internal error.  A CRASH IS NOT A REFUSAL.

READ-ONLY
---------
This module never writes anywhere under `_RUN_ROOT`.  The run tree holds the
only surviving copy of the Re 2000 rung (its `log.pimpleFoam` is already gone,
destroyed by `run_rung.py:58`'s `shutil.rmtree(remote_dir, ignore_errors=True)`
in `stage()`), and re-staging any rung would destroy it.  Plants are written to
a caller-supplied scratch directory or a tempdir, never beside a run.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

EXIT_OK = 0
EXIT_REFUSE = 2
EXIT_INSTRUMENT_ERROR = 70

# The out-of-git run tree.  READ ONLY -- see the module docstring.
_RUN_ROOT = Path.home() / "certonomous-runs" / "f5a-cylinder-ladder"

# The ladder's default averaging window, and the one the registration names in
# every place it quotes a series value ("all on the ladder's default `t >= 45`
# window").  It is 0.5 * end_time in `run_rung.py:107`; it is stated here as a
# number so a reader can see it, and cross-checked against 0.5*end_time in
# `analyse_rung`.
DEFAULT_T_START = 45.0
DEFAULT_END_TIME = 90.0

ABOUT_CHOICES = ("mean", "zero")
WEIGHTING_CHOICES = ("sample", "time")

# The five rungs that have a force history on disk.  re10000 is staged and
# unsolved -- it has no postProcessing at all, which is why the registration
# can still be frozen without its answer existing.
RUNGS = ("re1000", "re1000_coarsespacing", "re2000", "re3900",
         "re3900_correctedspacing")


class Refusal(Exception):
    """A registered refusal -> rc 2.  The instrument declines to judge."""


class InstrumentError(Exception):
    """An internal failure -> rc 70.  Never reported as a refusal."""


class ControlFailure(Exception):
    """A control did not behave as registered -> the suite is RED."""


def _require(condition, message, exc=InstrumentError):
    """The only guard in this file.  Never `assert` (L-332/L-475)."""
    if not condition:
        raise exc(message)


# ---------------------------------------------------------------------------
# THE SHIPPED STATISTIC
# ---------------------------------------------------------------------------

def cl_rms(times, values, t_start, about="mean", weighting="sample"):
    """Root-mean-square of `values` over the window `t >= t_start`.

    `about`     "mean" -> RMS of (v - mu), a FLUCTUATION amplitude
                "zero" -> RMS of v, a signal MAGNITUDE
    `weighting` "sample" -> plain arithmetic mean over samples in the window.
                            This reproduces `analyze_re3900.py:66-70`, the
                            lab's only pre-existing Cl_rms code.
                "time"   -> trapezoidal time weighting over the window span,
                            matching `time_weighted_stats`, which is what every
                            OTHER statistic on this ladder uses.  With an
                            adaptive time step the two are not the same number.

    Raises `InstrumentError` rather than returning a plausible small number
    when the window cannot support the statistic.
    """
    _require(about in ABOUT_CHOICES,
             "about=%r is not one of %r" % (about, list(ABOUT_CHOICES)))
    _require(weighting in WEIGHTING_CHOICES,
             "weighting=%r is not one of %r" % (weighting,
                                                list(WEIGHTING_CHOICES)))
    _require(len(times) == len(values),
             "times/values length mismatch: %d vs %d" % (len(times),
                                                         len(values)))
    window = [(t, v) for t, v in zip(times, values) if t >= t_start]
    _require(len(window) >= 3,
             "averaging window t >= %g holds %d samples; the run is INCOMPLETE, "
             "not a result" % (t_start, len(window)))

    if weighting == "sample":
        n = len(window)
        mu = sum(v for _, v in window) / n if about == "mean" else 0.0
        return math.sqrt(sum((v - mu) ** 2 for _, v in window) / n)

    span = window[-1][0] - window[0][0]
    _require(span > 0.0,
             "averaging window t >= %g has zero span (t=%g to t=%g); a "
             "time-weighted mean is undefined on it"
             % (t_start, window[0][0], window[-1][0]))

    def _trapz(f):
        area = 0.0
        for (t0, v0), (t1, v1) in zip(window, window[1:]):
            area += 0.5 * (f(v0) + f(v1)) * (t1 - t0)
        return area / span

    mu = _trapz(lambda v: v) if about == "mean" else 0.0
    ms = _trapz(lambda v: (v - mu) ** 2)
    _require(ms >= 0.0, "time-weighted mean square came out negative (%r); "
                        "the trapezoid rule cannot do that on a square" % ms)
    return math.sqrt(ms)


def cl_band(times, values, t_start):
    """The peak-to-trough ENVELOPE -- `hi - lo` -- i.e. exactly what
    `record.json`'s `cl_band` holds (`time_weighted_stats`, band = hi - lo).

    THIS IS NOT Cl_rms AND IS NEVER SUBSTITUTED FOR IT.  It is computed here
    only so every report can print the two side by side and be audited for the
    confusion this comparator exists to prevent.
    """
    window = [v for t, v in zip(times, values) if t >= t_start]
    _require(len(window) >= 3,
             "envelope window t >= %g holds %d samples" % (t_start, len(window)))
    return max(window) - min(window)


# ---------------------------------------------------------------------------
# THE SHIPPED READER
# ---------------------------------------------------------------------------

def _import_parser():
    """`parse_coefficient_history` from the lab SDK.

    Located by SEARCHING for the marker rather than by counting `parents[n]`
    up from this file -- a repository root derived by counting segments from a
    path under a moving tree points somewhere else the moment the tree moves
    (the defect class `run_rung.py:26-35` records against itself).
    """
    root = next((p for p in Path(__file__).resolve().parents
                 if (p / "scripts" / "lab_paths.py").is_file()), None)
    _require(root is not None,
             "cannot locate scripts/lab_paths.py above %s; refusing to guess "
             "a repository root" % __file__)
    sdk = str(root / "sdk")
    if sdk not in sys.path:
        sys.path.insert(0, sdk)
    try:
        from chief_engineer.head_engineer import parse_coefficient_history
    except Exception as exc:  # pragma: no cover - environment failure
        raise InstrumentError("cannot import parse_coefficient_history from "
                              "%s: %r" % (sdk, exc))
    return parse_coefficient_history


def load_history(path):
    """Read one `coefficient.dat` through the SHIPPED parser and return
    (times, Cl).  Every plant goes through this function too (C-P5)."""
    path = Path(path)
    _require(path.is_file(), "no force history at %s" % path, Refusal)
    parse = _import_parser()
    hist = parse(path.read_text(errors="replace"))
    _require("Time" in hist, "%s: parser produced no Time column -- header "
                             "layout not recognised" % path)
    _require("Cl" in hist, "%s: parser produced no Cl column; columns seen "
                           "were %r" % (path, sorted(hist)))
    times, cl = hist["Time"], hist["Cl"]
    _require(len(times) == len(cl),
             "%s: Time has %d rows, Cl has %d" % (path, len(times), len(cl)))
    _require(len(times) > 0, "%s: parsed zero data rows" % path, Refusal)
    return times, cl


def rung_history_path(name, run_root=None):
    root = Path(run_root) if run_root is not None else _RUN_ROOT
    return root / name / "postProcessing" / "forceCoeffs1" / "0" / "coefficient.dat"


# ---------------------------------------------------------------------------
# PLANTS -- synthesised coefficient.dat files with an ANALYTIC answer
# ---------------------------------------------------------------------------

_HEADER = (
    "# Force and moment coefficients\n"
    "# magUInf         : 1.0000000000e+00\n"
    "# lRef            : 1.0000000000e+00\n"
    "# Aref            : 1.0000000000e-01\n"
    "#\n"
    "# Time            \tCd                \tCd(f)             \tCd(r)"
    "             \tCl                \tCl(f)             \tCl(r)"
    "             \tCmPitch           \tCmRoll            \tCmYaw"
    "             \tCs                \tCs(f)             \tCs(r)\n"
)

PLANT_GARBAGE = 99.0     # C-P4: what sits BEFORE the window in every plant


def write_plant(path, cl_of_t, t_start=DEFAULT_T_START, periods=20,
                per_period=256, period=1.0):
    """Write a coefficient.dat whose Cl column is `cl_of_t`, sampled uniformly
    on `[t_start, t_start + periods*period)` -- the closing endpoint EXCLUDED so
    an integer number of whole periods is covered exactly and the analytic
    answers below are exact under sample weighting.

    Before `t_start` the file carries `PLANT_GARBAGE`, so a reader whose window
    filter is broken cannot pass any plant (C-P4).
    """
    path = Path(path)
    n = periods * per_period
    _require(n >= 3, "plant needs >= 3 in-window samples, got %d" % n)
    dt = period / per_period
    rows = []
    # 40 pre-window rows of garbage, ending strictly below t_start.
    for k in range(40, 0, -1):
        rows.append((t_start - k * dt, PLANT_GARBAGE))
    for k in range(n):
        t = t_start + k * dt
        rows.append((t, cl_of_t(k * dt)))
    lines = [_HEADER]
    for t, c in rows:
        lines.append("%.10f\t%.10e\t0\t0\t%.10e\t0\t0\t0\t0\t0\t0\t0\t0\n"
                     % (t, 1.0, c))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(lines))
    return path


def _plant_specs():
    """(name, cl_of_t, expectations) for every analytic plant.

    `expectations` maps (about, weighting) -> (expected_value, rel_tol, why).
    A combination that is NOT analytic is simply absent, and the reason is
    written down rather than papered over with a loose tolerance.
    """
    two_pi = 2.0 * math.pi

    # --- C-P1: pure sinusoid, mean zero.  Cl_rms == A/sqrt(2) exactly. -------
    a1 = 0.75
    p1_expect = {
        ("mean", "sample"): (a1 / math.sqrt(2.0), 1e-9,
                             "exact: N uniform samples over whole periods"),
        ("zero", "sample"): (a1 / math.sqrt(2.0), 1e-9,
                             "exact: the planted mean is zero"),
        # Trapezoid over whole periods is O(dt^2) accurate on a smooth signal,
        # and the window span is short by one dt because the closing endpoint
        # is excluded -- hence a finite, stated tolerance rather than 1e-9.
        ("mean", "time"): (a1 / math.sqrt(2.0), 2e-3, "trapezoid, O(dt^2)"),
        ("zero", "time"): (a1 / math.sqrt(2.0), 2e-3, "trapezoid, O(dt^2)"),
    }

    # --- C-P2: sinusoid on a known offset.  THE DISCRIMINATING PLANT. -------
    # about_mean == A/sqrt(2)          (the offset is removed)
    # about_zero == sqrt(B^2 + A^2/2)  (the offset is not)
    # No single number satisfies both, so a reader that ignores `about`
    # cannot pass C-P2.
    a2, b2 = 0.75, 0.40
    p2_expect = {
        ("mean", "sample"): (a2 / math.sqrt(2.0), 1e-9, "offset removed"),
        ("zero", "sample"): (math.sqrt(b2 ** 2 + a2 ** 2 / 2.0), 1e-9,
                             "offset retained"),
        ("mean", "time"): (a2 / math.sqrt(2.0), 2e-3, "trapezoid, O(dt^2)"),
        ("zero", "time"): (math.sqrt(b2 ** 2 + a2 ** 2 / 2.0), 2e-3,
                           "trapezoid, O(dt^2)"),
    }

    # --- C-P3: square wave.  THE ENVELOPE-SUBSTITUTION PLANT. ---------------
    # Cl_rms == A exactly, while band/(2*sqrt(2)) == A/sqrt(2) == 0.7071*A.
    # C-P1 and C-P2 provably CANNOT catch an envelope substitution, because on
    # a pure sinusoid band/(2*sqrt(2)) IS the RMS.  C-P3 is the control that
    # can.  Time weighting is deliberately NOT claimed here: the trapezoid rule
    # is not analytic across a discontinuity, and a control with a tolerance
    # wide enough to absorb that would no longer be a control.
    a3 = 0.60
    p3_expect = {
        ("mean", "sample"): (a3, 1e-9, "square wave, exact"),
        ("zero", "sample"): (a3, 1e-9, "square wave, exact"),
    }

    return [
        ("C-P1 sinusoid A=%.4f" % a1,
         lambda s: a1 * math.sin(two_pi * s), p1_expect,
         {"band": 2.0 * a1}),
        ("C-P2 sinusoid A=%.4f on offset B=%.4f" % (a2, b2),
         lambda s: b2 + a2 * math.sin(two_pi * s), p2_expect,
         {"band": 2.0 * a2}),
        ("C-P3 square wave A=%.4f" % a3,
         lambda s: a3 if (s % 1.0) < 0.5 else -a3, p3_expect,
         {"band": 2.0 * a3}),
    ]


def run_plants(scratch=None, verbose=True):
    """Run every plant through the SHIPPED reader and the SHIPPED statistic.

    Returns a list of (control_name, ok, detail).  Raises nothing on a plant
    MISS -- a miss is reported as not-ok so the caller can decide the rc; that
    is what lets the mutation controls observe a red suite.
    """
    results = []
    tmp = None
    if scratch is None:
        tmp = tempfile.TemporaryDirectory(prefix="f5a_clrms_plant_")
        scratch = tmp.name
    try:
        for name, fn, expect, extra in _plant_specs():
            path = Path(scratch) / (name.split()[0] + ".dat")
            write_plant(path, fn)
            try:
                times, cl = load_history(path)
            except Exception as exc:
                results.append((name + " [read-back]", False,
                                "the SHIPPED reader could not read the plant "
                                "back off disk: %r" % exc))
                continue

            # C-P4: the pre-window garbage must be present in the file and
            # absent from the window.  A window filter that let it through
            # would be caught by the value checks below, but this states it.
            pre = [v for t, v in zip(times, cl) if t < DEFAULT_T_START]
            ok_pre = len(pre) > 0 and all(abs(v - PLANT_GARBAGE) < 1e-9
                                          for v in pre)
            results.append((name + " [C-P4 pre-window garbage present]",
                            ok_pre,
                            "%d pre-window rows, all == %g: %s"
                            % (len(pre), PLANT_GARBAGE, ok_pre)))

            band = cl_band(times, cl, DEFAULT_T_START)
            ok_band = abs(band - extra["band"]) <= 1e-9 * abs(extra["band"])
            results.append((name + " [envelope cl_band]", ok_band,
                            "cl_band=%.10f expected %.10f"
                            % (band, extra["band"])))

            for (about, weighting), (want, rtol, why) in sorted(expect.items()):
                try:
                    got = cl_rms(times, cl, DEFAULT_T_START,
                                 about=about, weighting=weighting)
                except Exception as exc:
                    results.append((
                        "%s [about=%s weighting=%s]" % (name, about, weighting),
                        False, "the shipped statistic raised: %r" % exc))
                    continue
                err = abs(got - want) / abs(want) if want else abs(got)
                results.append((
                    "%s [about=%s weighting=%s]" % (name, about, weighting),
                    err <= rtol,
                    "got %.12f  expected %.12f  rel.err %.3e  tol %.0e  (%s)"
                    % (got, want, err, rtol, why)))
    finally:
        if tmp is not None:
            tmp.cleanup()

    if verbose:
        for cname, ok, detail in results:
            print("  %-58s %s   %s" % (cname, "ok " if ok else "MISS", detail))
    return results


def run_plants_rc(scratch=None, verbose=True):
    """Plant suite as an rc: 0 if every plant fired, EXIT_REFUSE otherwise.

    The mutation controls call THIS, in a subprocess, with the shipped
    statistic replaced.  It must go non-zero for the mutation to count.
    """
    try:
        results = run_plants(scratch=scratch, verbose=verbose)
    except InstrumentError:
        return EXIT_INSTRUMENT_ERROR
    return EXIT_OK if all(ok for _, ok, _ in results) else EXIT_REFUSE


# ---------------------------------------------------------------------------
# MEASUREMENT
# ---------------------------------------------------------------------------

def analyse_rung(name, run_root=None, t_start=None, end_time=DEFAULT_END_TIME):
    """Every Cl_rms definition for one rung, beside its envelope.  READ ONLY."""
    if t_start is None:
        t_start = 0.5 * end_time
        _require(abs(t_start - DEFAULT_T_START) < 1e-12,
                 "0.5*end_time is %g but the ladder's default window is %g; "
                 "the two disagree and this comparator will not guess"
                 % (t_start, DEFAULT_T_START))
    path = rung_history_path(name, run_root)
    times, cl = load_history(path)
    row = {
        "rung": name,
        "history": str(path),
        "rows": len(times),
        "t_first": times[0],
        "t_last": times[-1],
        "t_start": t_start,
        "cl_band_ENVELOPE": cl_band(times, cl, t_start),
    }
    for about in ABOUT_CHOICES:
        for weighting in WEIGHTING_CHOICES:
            row["Cl_rms_about_%s_%s" % (about, weighting)] = cl_rms(
                times, cl, t_start, about=about, weighting=weighting)
    ref = row["Cl_rms_about_mean_sample"]
    row["band_over_rms_about_mean_sample"] = (
        row["cl_band_ENVELOPE"] / ref if ref else None)
    row["two_root_two"] = 2.0 * math.sqrt(2.0)
    return row


def census(run_root=None, rungs=RUNGS, as_json=False):
    rows = []
    for name in rungs:
        path = rung_history_path(name, run_root)
        if not path.is_file():
            rows.append({"rung": name, "history": str(path),
                         "state": "NO FORCE HISTORY ON DISK"})
            continue
        rows.append(analyse_rung(name, run_root=run_root))
    if as_json:
        print(json.dumps(rows, indent=2))
        return rows
    print("F5a Cl_rms census -- window t >= %g, read-only from %s"
          % (DEFAULT_T_START, run_root or _RUN_ROOT))
    print("")
    print("  cl_band is the peak-to-trough ENVELOPE (record.json's stored")
    print("  quantity).  Cl_rms is a root-mean-square.  They are DIFFERENT")
    print("  statistics; band/rms is 2*sqrt(2)=%.4f only for a pure sinusoid."
          % (2.0 * math.sqrt(2.0)))
    print("")
    head = ("rung", "rows", "cl_band(ENV)", "rms|mean,samp", "rms|zero,samp",
            "rms|mean,time", "rms|zero,time", "band/rms")
    print("  %-24s %6s %13s %14s %14s %14s %14s %9s" % head)
    for r in rows:
        if "state" in r:
            print("  %-24s %s" % (r["rung"], r["state"]))
            continue
        print("  %-24s %6d %13.6f %14.6f %14.6f %14.6f %14.6f %9.4f" % (
            r["rung"], r["rows"], r["cl_band_ENVELOPE"],
            r["Cl_rms_about_mean_sample"], r["Cl_rms_about_zero_sample"],
            r["Cl_rms_about_mean_time"], r["Cl_rms_about_zero_time"],
            r["band_over_rms_about_mean_sample"]))
    print("")
    print("  NO DEFINITION IS MARKED AS THE GATE'S.  The pre-registration does")
    print("  not fix `about` or `weighting`; see this file's docstring.  Pass")
    print("  --grade with --about and --weighting to read one, once the")
    print("  registration names it.")
    return rows


def grade(about=None, weighting=None, run_root=None, rungs=RUNGS):
    """Report Cl_rms under ONE named definition -- refusing until it is named."""
    if about is None or weighting is None:
        raise Refusal(
            "REGISTERED REFUSAL: F5a_HIGH_RE_RUNGS_PREREGISTRATION.md gates G1 "
            "on `Cl_rms` but never says (a) whether the RMS is about the window "
            "MEAN or about ZERO, nor (b) whether it is SAMPLE- or TIME-weighted. "
            "The two axes give four different numbers on every rung (run "
            "--census). Choosing one here, after the data exists, would be "
            "choosing the gate's answer -- the exact thing the freeze exists to "
            "prevent. The document is still unfrozen, so this is a lawful "
            "pre-compute amendment (rule 2), not a gate change. Name the "
            "definition in the registration, then pass --about and --weighting.")
    _require(about in ABOUT_CHOICES, "unknown --about %r" % about, Refusal)
    _require(weighting in WEIGHTING_CHOICES,
             "unknown --weighting %r" % weighting, Refusal)
    print("F5a Cl_rms -- definition: RMS about the %s, %s-weighted, window "
          "t >= %g" % (about, weighting, DEFAULT_T_START))
    print("THE GATE READS THE `Cl_rms` COLUMN.  `cl_band` is the ENVELOPE and "
          "is printed only so the two can never be confused.")
    print("")
    print("  %-24s %14s %14s   %s" % ("rung", "Cl_rms(GATE)", "cl_band(ENV)",
                                      "artifact"))
    out = []
    for name in rungs:
        path = rung_history_path(name, run_root)
        if not path.is_file():
            print("  %-24s %14s %14s   %s" % (name, "-", "-",
                                              "NO HISTORY: %s" % path))
            continue
        r = analyse_rung(name, run_root=run_root)
        value = r["Cl_rms_about_%s_%s" % (about, weighting)]
        r["gate_value"] = value
        r["gate_definition"] = "about_%s_%s" % (about, weighting)
        out.append(r)
        print("  %-24s %14.6f %14.6f   %s"
              % (name, value, r["cl_band_ENVELOPE"], r["history"]))
    return out


# ---------------------------------------------------------------------------
# SELFTEST
# ---------------------------------------------------------------------------

_MUTANTS = {
    # C-M1: the envelope substitution this comparator exists to prevent.
    "C-M1": (
        "shipped Cl_rms replaced by cl_band/(2*sqrt(2)) -- the ENVELOPE "
        "substitution",
        "m.cl_rms = lambda times, values, t_start, about='mean', "
        "weighting='sample': m.cl_band(times, values, t_start) "
        "/ (2.0 * __import__('math').sqrt(2.0))\n"),
    # C-M2: the mean subtraction dropped, so `about` is ignored.
    "C-M2": (
        "shipped Cl_rms always taken about ZERO -- the `about` axis ignored",
        "m.cl_rms = lambda times, values, t_start, about='mean', "
        "weighting='sample': _orig(times, values, t_start, about='zero', "
        "weighting=weighting)\n"),
}

_MUTANT_DRIVER = """\
import importlib.util, sys
spec = importlib.util.spec_from_file_location("m", %(path)r)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
_orig = m.cl_rms
%(mutation)ssys.exit(m.run_plants_rc(verbose=False))
"""


def _expect(condition, message):
    if not condition:
        raise ControlFailure(message)


def run_selftest(include_mutations=True):
    """0 if every control behaved as registered, EXIT_REFUSE otherwise.

    `include_mutations=False` exists ONLY for the C-O1 `-O` parity check, which
    must not recurse into subprocesses.  A green from that reduced run says
    nothing about C-M1/C-M2, and C-O1 says so in its own output.
    """
    here = str(Path(__file__).resolve())
    try:
        print("F5a Cl_rms comparator -- controls")
        print("")
        print("PLANTS (analytic; every one read back off disk through the "
              "shipped parser)")
        results = run_plants(verbose=True)
        misses = [c for c, ok, _ in results if not ok]
        _expect(not misses,
                "planted controls MISSED: %r -- the reader cannot recover a "
                "known non-zero, so no zero or small number it produces is "
                "evidence (CLAUDE.md rule 3)" % misses)
        print("  -> %d planted controls, all fired" % len(results))
        print("")

        if include_mutations:
            print("MUTATIONS (the shipped statistic replaced; the suite MUST "
                  "go red)")
            for tag, (why, mutation) in sorted(_MUTANTS.items()):
                src = _MUTANT_DRIVER % {"path": here, "mutation": mutation}
                proc = subprocess.run([sys.executable, "-c", src],
                                      capture_output=True, text=True,
                                      timeout=300)
                _expect(proc.returncode != EXIT_OK,
                        "%s (%s) left the plant suite GREEN (rc %d). A control "
                        "that cannot fail is not a control."
                        % (tag, why, proc.returncode))
                _expect(proc.returncode == EXIT_REFUSE,
                        "%s owed rc %d (a registered refusal), got %d -- a "
                        "crash is not a refusal. stderr tail: %r"
                        % (tag, EXIT_REFUSE, proc.returncode,
                           proc.stderr[-300:]))
                print("  %-6s ok   suite went red (rc %d): %s"
                      % (tag, proc.returncode, why))
            print("")

            print("C-O1 (`-O` parity: python3 and python3 -O must agree)")
            env = dict(os.environ)
            env["PYTHONDONTWRITEBYTECODE"] = "1"   # stale pycache inverts this
            rcs = {}
            for flags in ((), ("-O",)):
                src = ("import importlib.util, sys\n"
                       "spec = importlib.util.spec_from_file_location('m', %r)\n"
                       "m = importlib.util.module_from_spec(spec)\n"
                       "spec.loader.exec_module(m)\n"
                       "sys.exit(m.run_selftest(include_mutations=False))\n"
                       % here)
                proc = subprocess.run([sys.executable, *flags, "-c", src],
                                      capture_output=True, text=True,
                                      timeout=300, env=env)
                rcs[flags or ("",)] = proc.returncode
            vals = list(rcs.values())
            _expect(len(set(vals)) == 1,
                    "C-O1: --selftest returned %r under python3/-O; every guard "
                    "in this file must raise, never assert (L-332/L-475)" % rcs)
            _expect(vals[0] == EXIT_OK,
                    "C-O1: the reduced selftest returned %d under both "
                    "interpreters, not %d" % (vals[0], EXIT_OK))
            print("  C-O1   ok   rc %d under both interpreters (this reduced "
                  "run skips C-M1/C-M2 and its green says nothing about them)"
                  % vals[0])
            print("")

        print("ALL CONTROLS GREEN")
        return EXIT_OK
    except ControlFailure as exc:
        print("")
        print("CONTROL FAILURE: %s" % exc)
        return EXIT_REFUSE


# ---------------------------------------------------------------------------

_USAGE = """\
usage: analyse_f5a_cl_rms.py [--selftest] [--census] [--grade]
                             [--about {mean,zero}] [--weighting {sample,time}]
                             [--run-root DIR] [--json]

  --selftest   run every control (plants + mutations + -O parity) and exit
  --census     print all four Cl_rms definitions for every rung on disk,
               beside the stored cl_band envelope
  --grade      print ONE definition as the gate value; refuses (rc 2) until
               --about and --weighting are both given
"""


def main(argv):
    if "--help" in argv or "-h" in argv:
        print(_USAGE)
        return EXIT_OK

    def opt(flag):
        if flag in argv:
            i = argv.index(flag)
            if i + 1 < len(argv):
                return argv[i + 1]
            raise Refusal("%s given with no value" % flag)
        return None

    try:
        if "--selftest" in argv:
            return run_selftest()
        run_root = opt("--run-root")
        if "--grade" in argv:
            grade(about=opt("--about"), weighting=opt("--weighting"),
                  run_root=run_root)
            return EXIT_OK
        census(run_root=run_root, as_json="--json" in argv)
        return EXIT_OK
    except Refusal as exc:
        print("")
        print("REFUSED (rc %d): %s" % (EXIT_REFUSE, exc))
        return EXIT_REFUSE
    except InstrumentError as exc:
        sys.stderr.write("INSTRUMENT ERROR: %s\n" % exc)
        return EXIT_INSTRUMENT_ERROR
    except Exception:  # a crash is NOT a refusal
        import traceback
        traceback.print_exc()
        sys.stderr.write("INSTRUMENT ERROR (unhandled): a crash is not a "
                         "refusal; rc %d\n" % EXIT_INSTRUMENT_ERROR)
        return EXIT_INSTRUMENT_ERROR


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
