#!/usr/bin/env python3
"""F5a HARVEST-PATH PLANTED CONTROLS -- Cd_mean, -Cpb and Lr/D.

WHY THIS FILE EXISTS
--------------------
`CLAUDE.md` rule 3: *a zero from a reader not shown able to see a non-zero is
not evidence.*  `F5a_HIGH_RE_RUNGS_PREREGISTRATION.md` section 11.7 measured the gap
and registered it OPEN: of the seven Python modules under
`verification/runs/F5_runs/`, exactly ONE (`analyse_f5a_cl_rms.py`) carried a
planted control.  The harvest path that produces `cd_mean`, `cpb` and
`recirculation` -- `run_rung.py:harvest()` by way of `cylinder_ladder.py` --
planted nothing.  Two of G1's three gated quantities and the whole of G4 were
therefore unreportable under rule 3.  THIS FILE CLOSES THAT.

G4 IS THE SHARP ONE, AND IT IS WHY THE NULL CONTROLS ARE TRIPLED
----------------------------------------------------------------
G4's registered outcome is a **NULL** -- *"NOT MEASURABLE BY THIS METRIC ON
THIS FLOW"*.  A null is exactly the reading rule 3 refuses to accept on trust.
So `recirculation_length` is not merely shown able to return a number; it is
shown able to return **each of its three distinct outcomes**, and to tell them
apart:

  G4-P1  a bubble inside the probe rake      -> a NON-NULL `lr_over_d`, known analytically
  G4-P2  no reversed flow anywhere           -> NULL, and `any_reversed_flow` False
  G4-P3  reversed flow across the whole rake -> NULL, and `any_reversed_flow` True

G4-P2 and G4-P3 both produce `lr_over_d = None`, and they mean **opposite
physical things** ("there is no bubble" versus "the bubble is longer than the
rake can see").  A NULL reported without distinguishing them is not a result.
The mutation M-LR2 is the matching negative: a reader that ALWAYS returns
`None` -- the precise shape of a blind reader manufacturing G4's registered
answer -- and the suite must go RED on it.

EVERY NUMBER IS READ BACK THROUGH THE SHIPPED READER
----------------------------------------------------
Nothing here reimplements a statistic.  Each plant is written to disk in the
solver's own on-disk format and read back through the very functions
`run_rung.harvest()` calls:

  Cd_mean  `chief_engineer.head_engineer.parse_coefficient_history`
           -> `workflows.tmr_verification.time_weighted_stats(...)["mean"]`
  -Cpb     `cylinder_ladder.base_cpb(out_dir, t_start)["cpb_magnitude"]`
  Lr/D     `cylinder_ladder.recirculation_length(out_dir, t_start, points)`

They are reached as MODULE ATTRIBUTES (`CL.base_cpb`, not a `from` import) for
one reason: the mutation controls must be able to replace the SHIPPED
statistic itself, not a local copy of it.  A mutation that only breaks a
private wrapper proves nothing about the code that grades.

CONTROLS
--------
  C-CD1   Cd_mean plant, constant + whole-period sinusoid; trapezoid mean is
          the constant EXACTLY.  Read back off disk through the shipped chain.
  C-CD2   the same file read with the window opened wide must give a DIFFERENT
          answer -- this proves the pre-window garbage really is in the file,
          so C-CD1's window filter is being tested rather than assumed.
  C-CPB1  -Cpb plant through `base_cpb`, including the 1/(0.5 rho U^2)
          normalisation, analytic.
  C-CPB2  the C-CD2 argument, for the probesBase file.
  G4-P1   Lr/D plant with an analytic crossing: lr_over_d = 0.900 exactly.
  G4-P2   NULL reachable, no reversed flow.
  G4-P3   NULL reachable, wholly reversed rake -- distinguished from G4-P2.
  G4-P4   the C-CD2 argument, for the probesCenterline file.
  M-CD1   shipped `time_weighted_stats` loses its window filter  -> RED
  M-CPB1  shipped `base_cpb` loses its dynamic-pressure normalisation -> RED
  M-LR1   shipped `recirculation_length` forgets to subtract D/2  -> RED
  M-LR2   shipped `recirculation_length` ALWAYS returns None -- the blind
          reader that would manufacture G4's registered NULL -> RED
  C-AST   this file contains ZERO bare `assert` statements, established by
          `ast.parse` of its own source and a walk for `ast.Assert` nodes --
          NOT by grep, which cannot tell an assert from the word in a comment
          or a string (L-332/L-475: `python3 -O` deletes every bare assert).
  C-O1    `--selftest` returns the same rc under `python3` and `python3 -O`.

EXIT VOCABULARY
---------------
  0   every control behaved as registered
  2   a REGISTERED REFUSAL -- a control did not fire, or a mutation left the
      suite green.  No number from this harvest path may be reported.
  70  INSTRUMENT ERROR -- this file could not run its own controls.  Not a
      verdict about the physics.

This module GRADES NOTHING and LAUNCHES NOTHING.  It certifies that the
harvest path's readers can see what they claim to see.
"""
from __future__ import annotations

import ast
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

EXIT_OK = 0
EXIT_REFUSE = 2
EXIT_INSTRUMENT = 70

# ---------------------------------------------------------------------------
# Import the SHIPPED readers.  Repository root is DERIVED BY SEARCHING for a
# marker file, never by counting `parents[N]` up from this file: a root
# obtained by counting segments points somewhere else the moment the tree
# moves, and run_rung.py carries the scar of exactly that defect.
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent))

_REPO_ROOT = next((_p for _p in _HERE.parents
                   if (_p / "scripts" / "lab_paths.py").is_file()), None)
if _REPO_ROOT is None:
    raise RuntimeError(
        "cannot locate scripts/lab_paths.py above %s; refusing to guess a "
        "repository root" % __file__)
sys.path.insert(0, str(_REPO_ROOT / "sdk"))

import cylinder_ladder as CL                                    # noqa: E402
from workflows import tmr_verification as TMR                   # noqa: E402
from chief_engineer import head_engineer as HE                  # noqa: E402


class Refusal(Exception):
    """A registered refusal -> EXIT_REFUSE."""


class InstrumentError(Exception):
    """The instrument could not run -> EXIT_INSTRUMENT."""


class ControlFailure(Exception):
    """A control did not behave as registered -> EXIT_REFUSE."""


def _require(condition, message, exc=InstrumentError):
    """The ONLY guard idiom in this file.  `assert` is banned: `python3 -O`
    deletes it, and a control that evaporates under an optimisation flag is
    not a control (L-332/L-475).  C-AST proves the ban held."""
    if not condition:
        raise exc(message)


def _expect(condition, message):
    if not condition:
        raise ControlFailure(message)


# ---------------------------------------------------------------------------
# PLANT CONSTANTS -- every expected value below is ANALYTIC, not a previously
# observed number.  A control whose expectation was read off the reader it is
# testing is circular.
# ---------------------------------------------------------------------------

PLANT_GARBAGE = 99.0        # sits BEFORE t_start in every plant
T_START = 45.0              # the harvest path uses t_start = 0.5 * end_time
PERIODS = 20
PER_PERIOD = 64
PERIOD = 1.0
N_GARBAGE = 40

CD_LEVEL = 1.234567         # C-CD1: trapezoid mean over whole periods == this
CD_AMPLITUDE = 0.4

P_LEVEL = -0.5661           # C-CPB1: kinematic p; cpb_magnitude == -2 * this
P_AMPLITUDE = 0.25
# U_INF is 1.0 and rho is 1: Cp = p / (0.5 * U_INF**2) = 2p, so -Cpb = -2p.
CPB_EXPECT = -P_LEVEL / (0.5 * CL.U_INF ** 2)

# G4-P1: the crossing is placed so the interpolation is exact.
#   u = -0.40 at x = 1.30 and u = +0.40 at x = 1.50
#   frac = 0.40 / 0.80 = 0.5  ->  x_cross = 1.40
#   lr   = x_cross - D/2 = 1.40 - 0.50 = 0.90   ->  lr_over_d = 0.90
LR_POINTS = [(0.55, 0.0, 0.005), (0.70, 0.0, 0.005), (0.90, 0.0, 0.005),
             (1.10, 0.0, 0.005), (1.30, 0.0, 0.005), (1.50, 0.0, 0.005),
             (1.80, 0.0, 0.005), (2.20, 0.0, 0.005)]
LR_U_BUBBLE = [-0.30, -0.45, -0.50, -0.44, -0.40, 0.40, 0.55, 0.62]
LR_U_NO_REVERSAL = [0.10, 0.22, 0.35, 0.48, 0.56, 0.61, 0.66, 0.70]
LR_U_ALL_REVERSED = [-0.30, -0.45, -0.50, -0.44, -0.40, -0.35, -0.22, -0.11]
LR_EXPECT = 0.90

TOL = 1e-9

_COEFF_HEADER = (
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


def _window_times():
    """Uniform samples on [T_START, T_START + PERIODS*PERIOD], CLOSING
    ENDPOINT INCLUDED.

    The endpoint matters.  `time_weighted_stats` is TRAPEZOIDAL and takes
    span = last - first, so the window must cover a WHOLE number of periods
    for a sinusoid to integrate to exactly zero.  With f(first) == f(last)
    the trapezoid sum collapses to dt * sum_k f(t_k), and the discrete sum of
    a sinusoid over whole periods is analytically zero.  Drop the endpoint and
    the mean acquires an O(dt) error that no tolerance below would survive --
    which is why this is written down rather than tuned around.
    """
    dt = PERIOD / PER_PERIOD
    n = PERIODS * PER_PERIOD
    return dt, [T_START + k * dt for k in range(n + 1)]


def _garbage_times(dt):
    """`N_GARBAGE` rows ending STRICTLY below T_START."""
    return [T_START - k * dt for k in range(N_GARBAGE, 0, -1)]


def write_cd_plant(path):
    """A coefficient.dat whose Cd column is CD_LEVEL + a whole-period sinusoid,
    preceded by PLANT_GARBAGE.  Trapezoid mean over the window == CD_LEVEL."""
    dt, ts = _window_times()
    rows = [(t, PLANT_GARBAGE) for t in _garbage_times(dt)]
    for t in ts:
        phase = 2.0 * math.pi * (t - T_START) / PERIOD
        rows.append((t, CD_LEVEL + CD_AMPLITUDE * math.sin(phase)))
    out = [_COEFF_HEADER]
    for t, cd in rows:
        out.append("%.10f\t%.12e\t0\t0\t%.12e\t0\t0\t0\t0\t0\t0\t0\t0\n"
                   % (t, cd, 0.0))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(out))
    return path


def write_cpb_plant(out_dir):
    """`postProcessing/probesBase/0/p` in OpenFOAM probes scalar format."""
    dt, ts = _window_times()
    rows = [(t, PLANT_GARBAGE) for t in _garbage_times(dt)]
    for t in ts:
        phase = 2.0 * math.pi * (t - T_START) / PERIOD
        rows.append((t, P_LEVEL + P_AMPLITUDE * math.sin(phase)))
    lines = ["# Probe 0 (0.5 0 0.005)\n", "#       Probe             0\n",
             "#        Time\n"]
    for t, p in rows:
        lines.append("%.10f\t%.12e\n" % (t, p))
    target = Path(out_dir) / "postProcessing" / "probesBase" / "0" / "p"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(lines))
    return target


def write_lr_plant(out_dir, u_profile):
    """`postProcessing/probesCenterline/0/U` in OpenFOAM probes vector format.

    Each probe's ux is CONSTANT in time, so the trapezoidal time-weighted mean
    is that constant exactly and the crossing arithmetic stays analytic.  The
    pre-window rows carry PLANT_GARBAGE in ux for EVERY probe, so a reader
    that lost its window filter sees an all-positive rake, finds no crossing,
    and fails G4-P1 rather than passing it.
    """
    _require(len(u_profile) == len(LR_POINTS),
             "LR plant needs one ux per probe point: %d points, %d values"
             % (len(LR_POINTS), len(u_profile)))
    dt, ts = _window_times()
    lines = ["# Probe 0 (0.55 0 0.005)\n", "#        Time\n"]

    def _row(t, us):
        body = " ".join("(%.12e %.12e %.12e)" % (u, 0.0, 0.0) for u in us)
        return "%.10f\t%s\n" % (t, body)

    for t in _garbage_times(dt):
        lines.append(_row(t, [PLANT_GARBAGE] * len(LR_POINTS)))
    # Three in-window samples is the floor `time_weighted_stats` enforces;
    # a handful is plenty because ux is constant, and it keeps the file small.
    for t in ts[:8]:
        lines.append(_row(t, u_profile))
    target = Path(out_dir) / "postProcessing" / "probesCenterline" / "0" / "U"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(lines))
    return target


# ---------------------------------------------------------------------------
# READERS -- the shipped chain, reached by module attribute so a mutation can
# replace the shipped statistic itself.
# ---------------------------------------------------------------------------

def read_cd_mean(coeff_path, t_start):
    """Exactly `run_rung.harvest()`'s chain for `record["cd_mean"]`."""
    history = HE.parse_coefficient_history(
        Path(coeff_path).read_text(errors="replace"))
    _require("Time" in history and "Cd" in history,
             "shipped parser produced no Time/Cd columns from the plant -- "
             "the plant is malformed or the parser changed shape")
    stats = TMR.time_weighted_stats(history["Time"], history["Cd"], t_start)
    if stats is None:
        return None
    return stats["mean"]


def read_cpb(out_dir, t_start):
    """Exactly `run_rung.harvest()`'s `CL.base_cpb(out_dir, t_start)`."""
    got = CL.base_cpb(Path(out_dir), t_start)
    if got is None:
        return None
    return got.get("cpb_magnitude")


def read_lr(out_dir, t_start, points=None):
    """Exactly `run_rung.harvest()`'s `CL.recirculation_length(...)`."""
    return CL.recirculation_length(Path(out_dir), t_start,
                                   LR_POINTS if points is None else points)


# ---------------------------------------------------------------------------
# THE PLANT SUITE
# ---------------------------------------------------------------------------

def _close(got, want, tol=TOL):
    if got is None:
        return False
    scale = max(1.0, abs(want))
    return abs(got - want) <= tol * scale


def run_plants(scratch=None, verbose=True):
    """Run every plant.  Returns [(tag, ok, detail)] and RAISES only on an
    instrument fault -- a MISSED plant is a result of this suite, not a crash,
    so the mutation controls can observe it as a refusal."""
    results = []
    tmp = None
    if scratch is None:
        tmp = tempfile.mkdtemp(prefix="f5a_harvest_controls_")
        scratch = tmp
    root = Path(scratch)

    # ---- Cd_mean -------------------------------------------------------
    cd_dir = root / "cd"
    coeff = write_cd_plant(cd_dir / "postProcessing" / "forceCoeffs1" / "0"
                           / "coefficient.dat")
    got = read_cd_mean(coeff, T_START)
    results.append(("C-CD1", _close(got, CD_LEVEL),
                    "Cd_mean planted %.6f, shipped chain read %s"
                    % (CD_LEVEL, "None" if got is None else "%.12f" % got)))

    wide = read_cd_mean(coeff, -1.0e30)
    results.append(("C-CD2", (wide is not None) and not _close(wide, CD_LEVEL),
                    "window opened wide reads %s -- must DIFFER from %.6f, "
                    "which is what proves the pre-window garbage is really "
                    "in the file"
                    % ("None" if wide is None else "%.6f" % wide, CD_LEVEL)))

    # ---- -Cpb ----------------------------------------------------------
    cpb_dir = root / "cpb"
    write_cpb_plant(cpb_dir)
    got = read_cpb(cpb_dir, T_START)
    results.append(("C-CPB1", _close(got, CPB_EXPECT),
                    "-Cpb planted %.6f (p=%.6f through 1/(0.5 rho U^2)), "
                    "shipped base_cpb read %s"
                    % (CPB_EXPECT, P_LEVEL,
                       "None" if got is None else "%.12f" % got)))

    wide = read_cpb(cpb_dir, -1.0e30)
    results.append(("C-CPB2", (wide is not None) and not _close(wide, CPB_EXPECT),
                    "window opened wide reads %s -- must DIFFER from %.6f"
                    % ("None" if wide is None else "%.6f" % wide, CPB_EXPECT)))

    # ---- Lr/D (G4) -----------------------------------------------------
    g1_dir = root / "lr_bubble"
    write_lr_plant(g1_dir, LR_U_BUBBLE)
    got = read_lr(g1_dir, T_START)
    lr_val = got.get("lr_over_d") if got else None
    results.append(("G4-P1", _close(lr_val, LR_EXPECT),
                    "bubble inside the rake: planted lr_over_d %.6f, shipped "
                    "recirculation_length read %s -- THE NON-NULL rule 3 "
                    "demands before any NULL is evidence"
                    % (LR_EXPECT,
                       "None" if lr_val is None else "%.12f" % lr_val)))

    g2_dir = root / "lr_no_reversal"
    write_lr_plant(g2_dir, LR_U_NO_REVERSAL)
    got = read_lr(g2_dir, T_START)
    ok = (got is not None and got.get("lr_over_d") is None
          and got.get("any_reversed_flow") is False
          and got.get("u_min", -1.0) > 0.0)
    results.append(("G4-P2", ok,
                    "no reversed flow: NULL reached with any_reversed_flow=%s, "
                    "u_min=%s -- the null means THERE IS NO BUBBLE"
                    % (None if got is None else got.get("any_reversed_flow"),
                       None if got is None else got.get("u_min"))))

    g3_dir = root / "lr_all_reversed"
    write_lr_plant(g3_dir, LR_U_ALL_REVERSED)
    got = read_lr(g3_dir, T_START)
    ok = (got is not None and got.get("lr_over_d") is None
          and got.get("any_reversed_flow") is True)
    results.append(("G4-P3", ok,
                    "rake wholly reversed: NULL reached with "
                    "any_reversed_flow=%s -- the null means THE BUBBLE IS "
                    "LONGER THAN THE RAKE, which is NOT what G4-P2 means"
                    % (None if got is None else got.get("any_reversed_flow"))))

    got = read_lr(g1_dir, -1.0e30)
    wide_lr = got.get("lr_over_d") if got else None
    results.append(("G4-P4", not _close(wide_lr, LR_EXPECT),
                    "window opened wide on the bubble plant reads %s -- must "
                    "DIFFER from %.6f"
                    % ("None" if wide_lr is None else "%.6f" % wide_lr,
                       LR_EXPECT)))

    if verbose:
        for tag, ok, detail in results:
            print("  %-7s %-4s %s" % (tag, "ok" if ok else "MISS", detail))
    if tmp is not None:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    return results


def run_plants_rc(scratch=None, verbose=True):
    """EXIT_OK when every plant fired, EXIT_REFUSE otherwise.  This is the
    entry point the mutation driver calls, so a mutation is observed as a
    REFUSAL rather than as a traceback."""
    try:
        results = run_plants(scratch=scratch, verbose=verbose)
    except InstrumentError as exc:
        print("INSTRUMENT ERROR: %s" % exc)
        return EXIT_INSTRUMENT
    misses = [t for t, ok, _ in results if not ok]
    if misses:
        print("REFUSAL: planted controls MISSED: %r -- the harvest path's "
              "reader cannot recover a known value, so NO number it produces "
              "(and no NULL it produces) is evidence (CLAUDE.md rule 3)"
              % misses)
        return EXIT_REFUSE
    return EXIT_OK


# ---------------------------------------------------------------------------
# MUTATIONS -- each replaces the SHIPPED statistic and the suite must go RED.
# ---------------------------------------------------------------------------

_MUTANTS = {
    "M-CD1": (
        "shipped time_weighted_stats loses its window filter (t_start ignored)",
        "_o = m.TMR.time_weighted_stats\n"
        "m.TMR.time_weighted_stats = (lambda times, values, t_start: "
        "_o(times, values, -1.0e30))\n"),
    "M-CPB1": (
        "shipped base_cpb loses the 1/(0.5 rho U^2) normalisation",
        "_o = m.CL.base_cpb\n"
        "def _mut(out_dir, t_start):\n"
        "    g = _o(out_dir, t_start)\n"
        "    if g is None:\n"
        "        return None\n"
        "    g = dict(g)\n"
        "    g['cpb_magnitude'] = -g['p_mean']\n"
        "    return g\n"
        "m.CL.base_cpb = _mut\n"),
    "M-LR1": (
        "shipped recirculation_length forgets to subtract D/2 from the crossing",
        "_o = m.CL.recirculation_length\n"
        "def _mut(out_dir, t_start, points):\n"
        "    g = _o(out_dir, t_start, points)\n"
        "    if g is None or g.get('lr_over_d') is None:\n"
        "        return g\n"
        "    g = dict(g)\n"
        "    g['lr_over_d'] = g['lr_over_d'] + 0.5\n"
        "    return g\n"
        "m.CL.recirculation_length = _mut\n"),
    "M-LR2": (
        "shipped recirculation_length ALWAYS returns a NULL lr_over_d -- the "
        "blind reader that would manufacture G4's registered NULL",
        "_o = m.CL.recirculation_length\n"
        "def _mut(out_dir, t_start, points):\n"
        "    g = _o(out_dir, t_start, points)\n"
        "    if g is None:\n"
        "        return None\n"
        "    g = dict(g)\n"
        "    g['lr_over_d'] = None\n"
        "    return g\n"
        "m.CL.recirculation_length = _mut\n"),
}

_MUTANT_DRIVER = """\
import importlib.util, sys
spec = importlib.util.spec_from_file_location("m", %(path)r)
m = importlib.util.module_from_spec(spec)
sys.modules["m"] = m
spec.loader.exec_module(m)
%(mutation)ssys.exit(m.run_plants_rc(verbose=False))
"""


# ---------------------------------------------------------------------------
# C-AST -- the bare-assert ban, established by PARSING, not by grep.
# ---------------------------------------------------------------------------

def bare_assert_count(path=None):
    """Number of `assert` STATEMENTS in a source file, by AST.

    grep cannot do this job: it cannot tell `assert x` from the word "assert"
    in a comment, a docstring or a string literal -- and this file's own
    docstring says the word several times.  `ast.parse` sees statements.
    """
    src = Path(path or __file__).read_text(errors="replace")
    tree = ast.parse(src)
    return sum(1 for node in ast.walk(tree) if isinstance(node, ast.Assert))


# ---------------------------------------------------------------------------
# SELFTEST
# ---------------------------------------------------------------------------

def run_selftest(include_mutations=True):
    """EXIT_OK if every control behaved as registered, EXIT_REFUSE otherwise.

    `include_mutations=False` exists ONLY for the C-O1 `-O` parity check,
    which must not recurse into subprocesses.  A green from that reduced run
    says nothing about the mutations, and C-O1 prints that in its own output.
    """
    here = str(_HERE)
    try:
        print("F5a harvest-path controls -- Cd_mean, -Cpb, Lr/D")
        print("")
        print("PLANTS (analytic; every one written to disk in the solver's "
              "own format and read back through the SHIPPED reader)")
        results = run_plants(verbose=True)
        misses = [t for t, ok, _ in results if not ok]
        _expect(not misses,
                "planted controls MISSED: %r -- the reader cannot recover a "
                "known value, so neither its numbers nor its NULLs are "
                "evidence (CLAUDE.md rule 3)" % misses)
        print("  -> %d planted controls, all fired" % len(results))
        print("")

        print("C-AST (bare `assert` ban, by ast.parse of this file's own "
              "source -- NOT by grep)")
        n_assert = bare_assert_count()
        _expect(n_assert == 0,
                "C-AST: %d bare `assert` statement(s) in %s. `python3 -O` "
                "deletes every one, so a guard written as an assert is not a "
                "guard (L-332/L-475)." % (n_assert, here))
        print("  C-AST   ok   0 ast.Assert nodes in %d bytes of source"
              % len(Path(here).read_text(errors="replace")))
        print("")

        if include_mutations:
            print("MUTATIONS (the SHIPPED statistic replaced; the suite MUST "
                  "go red)")
            for tag, (why, mutation) in sorted(_MUTANTS.items()):
                src = _MUTANT_DRIVER % {"path": here, "mutation": mutation}
                proc = subprocess.run([sys.executable, "-c", src],
                                      capture_output=True, text=True,
                                      timeout=600)
                _expect(proc.returncode != EXIT_OK,
                        "%s (%s) left the plant suite GREEN (rc %d). A control "
                        "that cannot fail is not a control."
                        % (tag, why, proc.returncode))
                _expect(proc.returncode == EXIT_REFUSE,
                        "%s owed rc %d (a registered refusal), got %d -- a "
                        "crash is not a refusal. stderr tail: %r"
                        % (tag, EXIT_REFUSE, proc.returncode,
                           proc.stderr[-400:]))
                print("  %-7s ok   suite went red (rc %d): %s"
                      % (tag, proc.returncode, why))
            print("")

            print("C-O1 (`-O` parity: python3 and python3 -O must agree)")
            env = dict(os.environ)
            # A stale __pycache__ inverts mutation tests: the clean control
            # fails and the mutated case passes.  PYTHONDONTWRITEBYTECODE is
            # the cheap half of the fix; the driver loads by path, which is
            # the other half.
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            rcs = {}
            for flags in ((), ("-O",)):
                src = ("import importlib.util, sys\n"
                       "spec = importlib.util.spec_from_file_location('m', %r)\n"
                       "m = importlib.util.module_from_spec(spec)\n"
                       "sys.modules['m'] = m\n"
                       "spec.loader.exec_module(m)\n"
                       "sys.exit(m.run_selftest(include_mutations=False))\n"
                       % here)
                proc = subprocess.run([sys.executable, *flags, "-c", src],
                                      capture_output=True, text=True,
                                      timeout=600, env=env)
                rcs[flags or ("",)] = proc.returncode
            vals = list(rcs.values())
            _expect(len(set(vals)) == 1,
                    "C-O1: the reduced selftest returned %r under python3/-O; "
                    "every guard in this file must raise, never assert "
                    "(L-332/L-475)" % rcs)
            _expect(vals[0] == EXIT_OK,
                    "C-O1: the reduced selftest returned %d under both "
                    "interpreters, not %d" % (vals[0], EXIT_OK))
            print("  C-O1    ok   rc %d under both interpreters (this reduced "
                  "run skips the mutations and its green says nothing about "
                  "them)" % vals[0])
            print("")

        print("ALL CONTROLS GREEN")
        return EXIT_OK
    except ControlFailure as exc:
        print("")
        print("CONTROL FAILURE: %s" % exc)
        return EXIT_REFUSE


# ---------------------------------------------------------------------------

_USAGE = """\
usage: analyse_f5a_harvest_controls.py [--selftest] [--plants] [--scratch DIR]

  --selftest   run every control (plants + C-AST + mutations + -O parity)
  --plants     run only the planted controls
  --scratch    write the plants here instead of a temporary directory

exit: 0 all controls green | 2 registered refusal | 70 instrument error

This module GRADES NOTHING and LAUNCHES NOTHING.  It certifies that the F5a
harvest path's readers for Cd_mean, -Cpb and Lr/D can see what they claim to
see -- including, for G4, that its registered NULL is a reading and not a
blindness.
"""


def main(argv):
    if not argv or "--help" in argv or "-h" in argv:
        print(_USAGE)
        return EXIT_OK
    scratch = None
    if "--scratch" in argv:
        i = argv.index("--scratch")
        if i + 1 >= len(argv):
            print("REFUSAL: --scratch needs a directory")
            return EXIT_REFUSE
        scratch = argv[i + 1]
    try:
        if "--selftest" in argv:
            return run_selftest()
        if "--plants" in argv:
            return run_plants_rc(scratch=scratch)
    except InstrumentError as exc:
        print("INSTRUMENT ERROR: %s" % exc)
        return EXIT_INSTRUMENT
    except Refusal as exc:
        print("REFUSAL: %s" % exc)
        return EXIT_REFUSE
    print(_USAGE)
    return EXIT_REFUSE


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
