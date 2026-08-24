#!/usr/bin/env python3
"""Grading reader for the F4 SWBLI Step 0 / Step 1 clamp-discrimination experiment.

The skeleton -- constants, labels, controls and the refusal structure -- was
COMMITTED BEFORE COMPUTE, per the house rule that the grading path is fixed at
the pre-registration commit (CLAUDE.md rule 2). Frozen alongside
    verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md

FIRST COMPUTE HAS NOW HAPPENED. Both steps ran and landed at commit 7cdb26f4
(COMPLETE / COMPLETE, NOT GRADED). The grading bodies below were written after
that, against the constants frozen above them; they choose no threshold. The one
READING they fix -- which of the two per-timestep boundE.H sets section 8 means
-- is prereg section 14 (ADDENDUM 2, post-compute), ruled on mechanism with both
readings disclosed and with every graded number printed beside its event-2
counterpart.

THE SUPERVISOR MUST READ THIS FILE'S DIFF AS A DIFF BEFORE ANY OUTPUT OF IT IS
BELIEVED. It is a measurement script; SUPERVISION_CHARTER.md 3 makes that read a
supervisor personal check that may not be delegated, and a lane's assurance that
"the controls are in there" is a summary, not a check.

Standing rule 3 governs this file's central design: a zero from a reader not
shown able to see a non-zero is not evidence. Every entry point below routes
through run_controls(), which REFUSES (exit 2) rather than degrading.

Exit codes
    0  graded
    2  a control failed -- nothing was graded (rule 3 / rule 4 refusal)
    3  control C2 reports the two step logs are byte-equivalent: LEVER-INERT,
       the discrimination question is NOT A RESULT and is not graded
    4  a step failed the completion rule (prereg 7) -- BLOCKED
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------
# Constants frozen by the pre-registration. Changing any of these changes a
# gate and is forbidden after first compute (rule 2).
# --------------------------------------------------------------------------

N_CELLS = 29700                      # prereg 8; constant/polyMesh, both blocks
CV_BOUND = 1005.0 - 8314.47 / 28.9   # 717.30208 J/(kg K); createFields.H:110-123
TREF_BOUND = 298.15                  # OpenFOAM Tstd default; same source
T_MIN = 20.0                         # controlDict TMin, unchanged in both steps

# Freestream reference state, NASA TM 101075 Table I (parent record 7a).
# Used by prereg 8.3 ONLY when the worst-low cell is NOT an inlet-face owner --
# see prereg 13.2 (AMENDMENT 1) and INLET_P_PA / R_GAS below.
RHO_INF = 0.0252     # kg/m3
MAG_U_INF = 1274.0   # m/s
T_INF = 81.2         # K

# prereg 13.2 (AMENDMENT 1, pre-compute). When the worst-low cell owns an inlet
# face -- the exact map is constant/polyMesh/owner over [startFace, startFace +
# nFaces) of the `inlet` patch, the SAME order as the 0/U and 0/T nonuniform
# lists -- the 8.3 reference is that face's own Table II profile value, not the
# freestream. All four persistently clamped cells (0, 3960, 6360, 13080; stride
# 120) are inlet-face owners, and 54 of the 110 inlet faces already exceed the
# 5% U_BAND on the prescribed BC alone at t=0. rho_ref = INLET_P_PA / (R_GAS *
# T_face) with T_face read from 0/T; 0/p carries `internalField uniform 576.0`
# and constant/thermophysicalProperties carries perfectGas with molWeight 28.9.
# R_GAS is written in the same 8314.47 / 28.9 form as CV_BOUND above so the two
# cannot drift apart.
INLET_P_PA = 576.0            # Pa; 0/p internalField
R_GAS = 8314.47 / 28.9        # 287.69792 J/(kg K); molWeight 28.9, perfectGas

T_STAR = 1.9e-05     # prereg 8: the matched comparison time
T_END_FULL = 6.5e-05     # prereg 1.3 endTime
T_END_TRUNC = 3.9e-05    # prereg 7.2 pre-declared truncation checkpoint

# prereg 8.1
S0A_BAND = (0.06, 0.24)
# prereg 8.2
THRESHOLD_ARTIFACT_FRAC = 0.80   # of clamped cells in (19.5, 20) K
GENUINE_DIVERGENCE_FRAC = 0.20   # of clamped cells at T <= 10 K
# prereg 8.3
RHO_BAND = 0.10
U_BAND = 0.05
# prereg 8.4
S1A_RATIO = 0.60
FLATTEN_RATIO = 1.5
# prereg 7.3
SIGFPE_MIN_BLOCKS = 200
# prereg 13.3 (AMENDMENT 1, pre-compute). 136 = 128 + SIGFPE(8). This is the
# PRIMARY signal that a step died on a floating-point exception -- it is the
# kernel's own report and cannot be forged by log text. The backtrace frame
# matched by RE_SIGFPE below is SECONDARY: sufficient on its own when rc was not
# captured, but it is a log artefact and is named as such in the results record.
SIGFPE_RC = 136

# prereg 14 (ADDENDUM 2, POST-COMPUTE). boundE.H is included TWICE per timestep:
# at rhoCentralFoamBoundedDiag.C:267 (after the convective rhoE solve and
# `e = rhoE/rho - 0.5*magSqr(U)`, BEFORE thermo.correct()) and at :282 (inside
# `if (!inviscid)`, AFTER the viscous e-diffusion solve and after an intervening
# thermo.correct()). In the Step-1 tree the same two sites sit at :269 and :284,
# shifted by exactly the two lines prereg 5.1 adds. Every `Time = ` block
# therefore carries TWO BOUND/BOUNDDIAG/BOUNDHIST sets, and prereg 8 as frozen
# does not say which it reads.
#
# prereg 14.2 rules that section 8 grades EVENT 1 (the :267 set), on mechanism:
# 8.3's whole construction reasons about the e = rhoE/rho - 1/2|U|^2
# cancellation, which is the state at :267, and 4.2's own frozen instrument
# comment ("rho and U are CURRENT ... T is NOT current: thermo.correct() has not
# yet run for this step") is true at :267 and false at :282. Event 2 is a
# re-clamp of a thermo-corrected, then diffused, e -- a different population.
#
# prereg 14.5 binds this reader: grade event 1; print the event-2 value beside
# EVERY graded number, marked UNGRADED; print the label the event-2 reading
# would return; refuse (exit 2) where a required block carries no set; and report
# an absent event 2 as ABSENT, never as nLow = 0.
EVENT_GRADED = 1
EVENT_ALT = 2

# prereg 7.1. Note `p`, not `p_rgh`: this is a compressible rhoCentralFoam case,
# and the seven names below are quoted verbatim from that clause.
FIELDS_REQUIRED = ("T", "U", "p", "alphat", "k", "nut", "omega")

# prereg 7.2. TRUNCATED-AT-CAP is admissible ONLY when the stop was the 6
# core-min per-step cap. Both steps were launched under `timeout 360` (each
# step's LAUNCH.txt), and GNU timeout reports 124 when it fires. If rc was not
# captured at all a cap stop CANNOT be asserted, and the step is BLOCKED rather
# than handed the pre-declared truncated window on an inference.
CAP_STOP_RC = 124

EXIT_GRADED = 0
EXIT_CONTROL_FAILURE = 2   # rule 3 / rule 4 refusal
EXIT_LEVER_INERT = 3       # control C2, prereg 5.2 / 6
EXIT_BLOCKED = 4           # prereg 7

# Histogram bin edges in K, prereg 4.2 / the fixture header. 12 bins.
BIN_EDGES = [
    (float("-inf"), 0.0), (0.0, 1.0), (1.0, 2.0), (2.0, 5.0),
    (5.0, 10.0), (10.0, 15.0), (15.0, 18.0), (18.0, 19.0),
    (19.0, 19.5), (19.5, 19.9), (19.9, 19.99), (19.99, 20.0),
]

# .../Certonomous/verification/runs/F4_runs/swbli_cylflare/<this file>
REPO = Path(__file__).resolve().parents[4]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "bound_log_fixture.txt"
CRASH_LOG = (REPO / "demo-output" / "website" / "solve_registry"
             / "f4_swbli_warmup20_20260730T004453Z.log")
CRASH_LOG_MD5 = "b658b967377d574d8aacf00e3569cf9c"

# Control C1's expected table, prereg 6. Duplicated from the fixture header ON
# PURPOSE: the reader asserts the fixture and this table agree, so editing one
# without the other is a hard failure rather than a silent drift.
EXPECTED_C1 = [
    # (time, nLow, worst_e, worst_cell, worst_T_implied)
    (1e-08, 7, -199600.5, 0, 19.8844),
    (2e-08, 55, -201234.75, 3960, 17.6061),
    (3e-08, 411, -211681.775, 13080, 3.0417),
]

# Control C4's plant, prereg 6. Planted BY LINE INDEX into a scratch copy of the
# step's own log; the step's real log is never modified.
PLANT_N_LOW = 424242
PLANT_WORST_E = -299999.125
PLANT_WORST_CELL = 12345
PLANT_BLOCK_INDEX = 5   # insert after the 5th `Time = ` line

# --------------------------------------------------------------------------
# Line grammar. Emitted by rhoCentralFoamBoundedDiag_src/boundE.H (prereg 4.2).
# --------------------------------------------------------------------------

RE_TIME = re.compile(r"^Time = (\S+)\s*$")
RE_EXEC = re.compile(r"^ExecutionTime = ([0-9.eE+-]+) s")
RE_END = re.compile(r"^End\s*$")
RE_BOUND = re.compile(
    r"^BOUND: e below eMin in (\d+) cell\(s\) at Time = (\S+), "
    r"worst e = (\S+) J/kg at cell (\d+)\b"
)
RE_DIAG = re.compile(
    r"^BOUNDDIAG: t=(\S+) nLow=(\d+) "
    r"rhoLow=\[(\S+),(\S+)\] magULow=\[(\S+),(\S+)\] TprevLow=\[(\S+),(\S+)\] "
    r"worst: cell=(\d+) rho=(\S+) magU=(\S+) Tprev=(\S+) Timp=(\S+)\s*$"
)
RE_HIST = re.compile(r"^BOUNDHIST: t=(\S+) nLow=(\d+) bins=(.+?)\s*$")
# prereg 13.3 (AMENDMENT 1, pre-compute). The struck pattern was
#     r"Foam::sigFpe|Floating point exception|SIGFPE"
# which matches the OpenFOAM STARTUP BANNER -- `trapFpe: Floating point
# exception trapping enabled (FOAM_SIGFPE).` -- printed by every OpenFOAM run on
# this box whether or not it crashes (measured: line 18 of the F4 crash log, line
# 18 of F5_runs/re3900/log.pimpleFoam and line 29 of
# F7_runs/damBreak_MM_a2p25in_medium/log.interFoam, both of which completed
# cleanly). It would have set sigfpe=True on a clean run and driven prereg 7.3 to
# label a completed step SIGFPE-RECURRENCE. The replacement matches the backtrace
# frame (line 27602 of the F4 crash log) and an anchored bare exception line, and
# matches NEITHER banner wording. Asserted in --selftest.
RE_SIGFPE = re.compile(r"Foam::sigFpe::sigHandler|^Floating point exception\b")


class ControlFailure(RuntimeError):
    """A positive control did not reproduce. Nothing may be graded."""


@dataclass
class ClampEvent:
    time: float
    n_low: int
    worst_e: float
    worst_cell: int
    rho_lo: float = float("nan")
    rho_hi: float = float("nan")
    magu_lo: float = float("nan")
    magu_hi: float = float("nan")
    tprev_lo: float = float("nan")
    tprev_hi: float = float("nan")
    worst_rho: float = float("nan")
    worst_magu: float = float("nan")
    worst_tprev: float = float("nan")
    worst_timp: float = float("nan")
    bins: list[int] = field(default_factory=list)
    # prereg 14.3: which `Time = ` block this set sits in, and its ORDINAL
    # within that block in log order. block == -1 / ordinal == -1 means the set
    # was seen before any `Time = ` line, which no solver log produces.
    block: int = -1
    ordinal: int = -1

    @property
    def fraction(self) -> float:
        return self.n_low / N_CELLS


def implied_T(e: float) -> float:
    """Exact hConst inversion, prereg 4.2. T = Tref + e/Cv, eref = 0."""
    return TREF_BOUND + e / CV_BOUND


def md5_of(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------
# Parsing. ONE code path, used by the controls and by the real logs alike --
# a control that exercises a different function proves nothing about the
# function that grades.
# --------------------------------------------------------------------------

def parse_log(path: Path) -> dict:
    """Parse a solver log into clamp events, time blocks and completion facts.

    prereg 14.3: every clamp event is additionally tagged with the index of the
    `Time = ` block it sits in and its ORDINAL within that block, in log order,
    and the blocks themselves are returned. That is what lets section 8 grade
    event 1 (the :267 include) and print event 2 (the :282 include) beside it.

    `BOUND: e above eMax` is a SEPARATE emission (boundE.H:142-148) with no
    BOUNDDIAG/BOUNDHIST companion. It matches none of the regexes below -- in
    particular not RE_BOUND, which is anchored on `e below eMin` -- so it cannot
    create a set and cannot shift an ordinal. Asserted in --selftest.

    This function is NOT the place for the block-structure refusal: it is the one
    parsing path the controls share, and control C4 deliberately plants an extra
    set into a block. The refusal lives in select_event(), on the grading path.
    """
    events: list[ClampEvent] = []
    times: list[str] = []
    blocks: list[dict] = []
    cur: dict | None = None
    exec_lines = 0
    saw_end = False
    saw_sigfpe = False
    by_time: dict[str, ClampEvent] = {}

    for raw in path.read_text(errors="replace").splitlines():
        line = raw.rstrip("\n")
        if RE_SIGFPE.search(line):
            saw_sigfpe = True
        m = RE_TIME.match(line)
        if m:
            times.append(m.group(1))
            cur = {"index": len(blocks), "time": m.group(1),
                   "events": [], "exec_lines": 0}
            blocks.append(cur)
            continue
        if RE_EXEC.match(line):
            exec_lines += 1
            if cur is not None:
                cur["exec_lines"] += 1
            continue
        if RE_END.match(line):
            saw_end = True
            continue
        m = RE_BOUND.match(line)
        if m:
            ev = ClampEvent(
                time=float(m.group(2)), n_low=int(m.group(1)),
                worst_e=float(m.group(3)), worst_cell=int(m.group(4)),
            )
            if cur is not None:
                ev.block = cur["index"]
                ev.ordinal = len(cur["events"]) + 1
                cur["events"].append(ev)
            events.append(ev)
            by_time[m.group(2)] = ev
            continue
        m = RE_DIAG.match(line)
        if m:
            ev = by_time.get(m.group(1))
            if ev is None:
                raise ControlFailure(
                    f"{path}: BOUNDDIAG at t={m.group(1)} with no matching BOUND line"
                )
            (ev.rho_lo, ev.rho_hi, ev.magu_lo, ev.magu_hi,
             ev.tprev_lo, ev.tprev_hi) = (float(m.group(i)) for i in range(3, 9))
            ev.worst_cell_diag = int(m.group(9))
            ev.worst_rho = float(m.group(10))
            ev.worst_magu = float(m.group(11))
            ev.worst_tprev = float(m.group(12))
            ev.worst_timp = float(m.group(13))
            continue
        m = RE_HIST.match(line)
        if m:
            ev = by_time.get(m.group(1))
            if ev is None:
                raise ControlFailure(
                    f"{path}: BOUNDHIST at t={m.group(1)} with no matching BOUND line"
                )
            ev.bins = [int(x) for x in m.group(3).split()]
            continue

    return {
        "path": path, "events": events, "times": times, "blocks": blocks,
        "exec_lines": exec_lines, "end": saw_end, "sigfpe": saw_sigfpe,
    }


def normalised_md5(path: Path) -> str:
    """md5 with wall-clock-dependent lines stripped (control C2, prereg 6)."""
    keep = [
        ln for ln in path.read_text(errors="replace").splitlines()
        if not ln.startswith("ExecutionTime")
        and not ln.startswith("ClockTime")
        and "Date   :" not in ln and "Time   :" not in ln
        and "Host   :" not in ln and "PID    :" not in ln
        and "Exec   :" not in ln and "Case   :" not in ln
    ]
    return hashlib.md5("\n".join(keep).encode()).hexdigest()


# --------------------------------------------------------------------------
# Positive controls (prereg 6). run_controls() is the ONLY gate to grading and
# raises rather than returning a degraded result.
# --------------------------------------------------------------------------

def control_c1() -> list[str]:
    """The clamp reader sees a known non-zero, from the committed fixture."""
    out = [f"C1 fixture: {FIXTURE}", f"C1 fixture md5: {md5_of(FIXTURE)}"]
    got = parse_log(FIXTURE)["events"]
    if len(got) != len(EXPECTED_C1):
        raise ControlFailure(
            f"C1: expected {len(EXPECTED_C1)} clamp events, read {len(got)}"
        )
    for ev, (t, n, we, wc, wt) in zip(got, EXPECTED_C1):
        if abs(ev.time - t) > 1e-15 * max(1.0, abs(t)):
            raise ControlFailure(f"C1: time {ev.time} != {t}")
        if ev.n_low != n:
            raise ControlFailure(f"C1: nLow {ev.n_low} != {n} at t={t}")
        if abs(ev.worst_e - we) > 1e-6:
            raise ControlFailure(f"C1: worst e {ev.worst_e} != {we} at t={t}")
        if ev.worst_cell != wc:
            raise ControlFailure(f"C1: worst cell {ev.worst_cell} != {wc} at t={t}")
        # The fixture's own quoted implied T must agree with the exact inversion
        # this reader will apply to real logs -- if it does not, the reader's
        # arithmetic is wrong and no histogram it produces is trustworthy.
        if abs(implied_T(ev.worst_e) - wt) > 5e-4:
            raise ControlFailure(
                f"C1: implied_T({ev.worst_e}) = {implied_T(ev.worst_e):.4f} "
                f"!= fixture's {wt} at t={t}"
            )
        if abs(ev.worst_timp - wt) > 5e-4:
            raise ControlFailure(
                f"C1: fixture BOUNDDIAG Timp {ev.worst_timp} != {wt} at t={t}"
            )
        if len(ev.bins) != len(BIN_EDGES):
            raise ControlFailure(
                f"C1: {len(ev.bins)} bins, expected {len(BIN_EDGES)} at t={t}"
            )
        if sum(ev.bins) != ev.n_low:
            raise ControlFailure(
                f"C1: histogram sums to {sum(ev.bins)}, nLow={ev.n_low} at t={t}"
            )
        lowest = next(i for i, b in enumerate(ev.bins) if b > 0)
        lo, hi = BIN_EDGES[lowest]
        if not (lo < wt <= hi or (lowest == len(BIN_EDGES) - 1 and lo < wt < hi)):
            raise ControlFailure(
                f"C1: worst implied T {wt} is not in the lowest occupied bin "
                f"{lowest} = ({lo},{hi}] at t={t}"
            )
        out.append(
            f"C1 ok t={t}: nLow={n} worst_e={we} cell={wc} "
            f"Timp={wt} bins_sum={sum(ev.bins)} lowest_bin={lowest}"
        )
    return out


def control_c3() -> list[str]:
    """The same counter returns zero on a log known to carry no clamp lines."""
    if not CRASH_LOG.exists():
        raise ControlFailure(f"C3: archived crash log missing: {CRASH_LOG}")
    got_md5 = md5_of(CRASH_LOG)
    if got_md5 != CRASH_LOG_MD5:
        raise ControlFailure(
            f"C3: crash log md5 {got_md5} != frozen {CRASH_LOG_MD5}"
        )
    n = len(parse_log(CRASH_LOG)["events"])
    if n != 0:
        raise ControlFailure(f"C3: expected 0 clamp events in the stock-solver log, read {n}")
    return [
        f"C3 ok: {CRASH_LOG.name} md5 {got_md5} -> 0 clamp events",
        "C3 zero is admissible ONLY because C1 returned "
        f"{len(EXPECTED_C1)} on a file that has {len(EXPECTED_C1)} "
        "(standing rule 3).",
    ]


def control_c4(step_log: Path, scratch_dir: Path) -> list[str]:
    """The plant, into THIS step's own log. Planted by line index (rule 3)."""
    lines = step_log.read_text(errors="replace").splitlines()
    seen, insert_at, block_time = 0, None, None
    for i, ln in enumerate(lines):
        m = RE_TIME.match(ln)
        if m:
            seen += 1
            if seen == PLANT_BLOCK_INDEX:
                insert_at, block_time = i + 1, m.group(1)
                break
    if insert_at is None:
        raise ControlFailure(
            f"C4: {step_log} has fewer than {PLANT_BLOCK_INDEX} time blocks; "
            "cannot plant, so this step is not graded"
        )
    planted = list(lines)
    planted[insert_at:insert_at] = [
        f"BOUND: e below eMin in {PLANT_N_LOW} cell(s) at Time = {block_time}, "
        f"worst e = {PLANT_WORST_E} J/kg at cell {PLANT_WORST_CELL} "
        "C = (9.9 9.9 9.9) | low-e cell extent: x=[9.9,9.9] r=[9.9,9.9]",
        f"BOUNDHIST: t={block_time} nLow={PLANT_N_LOW} "
        f"bins={PLANT_N_LOW} 0 0 0 0 0 0 0 0 0 0 0",
    ]
    scratch_dir.mkdir(parents=True, exist_ok=True)
    copy = scratch_dir / f"{step_log.stem}.planted.log"
    copy.write_text("\n".join(planted) + "\n")

    evs = parse_log(copy)["events"]
    hit = [e for e in evs if e.n_low == PLANT_N_LOW]
    if not hit:
        raise ControlFailure(
            f"C4: reader could not see the plant in {step_log.name}'s own log; "
            "this step is NOT graded"
        )
    ev = hit[0]
    if ev.worst_e != PLANT_WORST_E or ev.worst_cell != PLANT_WORST_CELL:
        raise ControlFailure(
            f"C4: plant read back wrong: e={ev.worst_e} cell={ev.worst_cell}"
        )
    if not ev.bins or ev.bins[0] != PLANT_N_LOW:
        raise ControlFailure(f"C4: planted histogram bin 0 read back as {ev.bins[:1]}")
    if md5_of(step_log) == md5_of(copy):
        raise ControlFailure("C4: the plant did not change the file -- reader is blind")
    return [
        f"C4 ok: plant seen in {step_log.name} own log at line index {insert_at} "
        f"(t={block_time}): nLow={PLANT_N_LOW} e={PLANT_WORST_E} "
        f"cell={PLANT_WORST_CELL} bin0={ev.bins[0]}",
        f"C4 scratch copy: {copy} (the real log was NOT modified)",
    ]


def selftest_sigfpe_regex() -> list[str]:
    """prereg 13.3: RE_SIGFPE must not fire on the startup banner, must fire on
    the backtrace frame, and must read the archived crash as a real SIGFPE.

    This is standing rule 3 applied to the crash detector itself: a False from a
    reader not shown able to return True is not evidence that a step did not
    crash. Raises ControlFailure rather than degrading."""
    banners = [
        # the wording this box actually emits (F4 crash log line 18)
        "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).",
        # an alternative wording, excluded too, so the guard does not depend on
        # which OpenFOAM build wrote the log
        "SigFpe : Enabling floating point exception trapping (FOAM_SIGFPE).",
    ]
    for b in banners:
        if RE_SIGFPE.search(b):
            raise ControlFailure(
                f"13.3: RE_SIGFPE matched the STARTUP BANNER {b!r} -- every "
                "clean OpenFOAM run would read as SIGFPE-RECURRENCE"
            )
    frames = [
        "#3  Foam::sigFpe::sigHandler(int) at ??:?",
        # the frame the archived F4 crash log actually carries, at line 27602
        "#1  Foam::sigFpe::sigHandler(int) in "
        "<platforms>/linux64GccDPInt32Opt/lib/libOpenFOAM.so",
    ]
    for f in frames:
        if not RE_SIGFPE.search(f):
            raise ControlFailure(
                f"13.3: RE_SIGFPE did NOT match the backtrace frame {f!r} -- a "
                "real SIGFPE would read as SIGFPE-ABSENT"
            )
    if not parse_log(CRASH_LOG)["sigfpe"]:
        raise ControlFailure(
            f"13.3: {CRASH_LOG.name} is a real SIGFPE crash (backtrace frame at "
            "line 27602) but parse_log read sigfpe=False"
        )
    return [
        f"13.3 ok: RE_SIGFPE = {RE_SIGFPE.pattern!r}",
        f"13.3 ok: does NOT match {len(banners)} startup-banner wordings",
        f"13.3 ok: DOES match {len(frames)} sigHandler backtrace frames",
        f"13.3 ok: {CRASH_LOG.name} parses sigfpe=True (real crash), and C3 "
        "above shows the same file parses 0 clamp events -- the two reads are "
        "independent, so neither zero is a blind zero (rule 3).",
        f"13.3 note: SIGFPE_RC = {SIGFPE_RC} is the PRIMARY signal at run time; "
        "the archived .done sidecar records no rc, so this selftest exercises "
        "the SECONDARY (log) signal only.",
    ]


def control_c2(step0_log: Path, step1_log: Path) -> tuple[bool, list[str]]:
    """Can the reader tell Step 1's log from Step 0's? (prereg 5.2, 6)"""
    a, b = normalised_md5(step0_log), normalised_md5(step1_log)
    out = [f"C2 step0 normalised md5: {a}", f"C2 step1 normalised md5: {b}"]
    if a == b:
        out.append(
            "C2 LEVER-INERT: the two logs are byte-equivalent after stripping "
            "wall-clock lines. Per prereg 5.2 this is a live possibility (the "
            "inlet is supersonic on most of its 110 faces, where a_pos == 0 "
            "exactly and the _pos state drops out of every flux). The "
            "discrimination question is NOT A RESULT and is NOT graded."
        )
        return False, out
    t0 = parse_log(step0_log)["times"]
    t1 = parse_log(step1_log)["times"]
    first = next((x for x, y in zip(t0, t1) if x != y), None)
    out.append(f"C2 ok: logs differ; first differing time token: {first}")
    return True, out


def run_controls(step0_log: Path | None, step1_log: Path | None,
                 scratch_dir: Path) -> list[str]:
    """The single gate. Raises ControlFailure rather than degrading."""
    out: list[str] = ["=== POSITIVE CONTROLS (standing rule 3) ==="]
    out += control_c1()
    out += control_c3()
    for log in (step0_log, step1_log):
        if log is not None:
            out += control_c4(log, scratch_dir)
    out.append(
        "C0 (instrument inertness, prereg 6) is NOT performed by this reader: "
        "it is a 200-step twin-run comparison against the published "
        "rhoCentralFoamBounded and its output is recorded in "
        "<STEP>/POSITIVE_CONTROL.txt at run time. This reader asserts that "
        "file exists and is non-empty before grading Step 0."
    )
    return out


# --------------------------------------------------------------------------
# Event selection (prereg 14.3) -- the rule the whole of section 8 now reads
# through. Written AFTER first compute, as a dated ADDENDUM 2 reading of an
# ambiguous clause; it moves no threshold. It refuses rather than degrading.
# --------------------------------------------------------------------------

def select_event(block: dict, k: int, *, required: bool = True):
    """Event k = the k-th BOUND-family set within a `Time = ` block, log order.

    prereg 14.3. A block with a single set is event 1 only and event 2 is
    ABSENT -- not zero. Where section 8 REQUIRES an event and the block carries
    no such set, this refuses (ControlFailure -> exit 2) rather than reading the
    absence as nLow = 0: boundE.H:107 emits the set only `if (nLow > 0)`, so
    "no line" and "no clamped cells" are indistinguishable from the log alone,
    and a zero a reader cannot tell apart from a silence is not evidence
    (standing rule 3).
    """
    evs = block["events"]
    if len(evs) >= k:
        return evs[k - 1]
    if required:
        raise ControlFailure(
            f"prereg 14.3: `Time = ` block {block['index']} (t={block['time']}) "
            f"carries {len(evs)} BOUND-family set(s); event {k} is required here "
            "and is ABSENT. Refusing rather than reading the absence as "
            "nLow = 0 (standing rule 3)."
        )
    return None


def describe_event(ev) -> str:
    """One-line description of an event, or the word ABSENT (never a zero)."""
    if ev is None:
        return "ABSENT (no such BOUND-family set in this block; NOT nLow = 0)"
    return (f"nLow={ev.n_low} frac={ev.fraction:.6f} ({100*ev.fraction:.4f} %) "
            f"worst_e={ev.worst_e} worst_cell={ev.worst_cell}")


def find_t_star_block(parsed: dict) -> dict:
    """The `Time = ` block whose time is nearest T_STAR from below (prereg 8)."""
    below = [b for b in parsed["blocks"] if float(b["time"]) <= T_STAR]
    if not below:
        raise ControlFailure(
            f"{parsed['path']}: no `Time = ` block at or below t* = {T_STAR}; "
            "section 8's matched comparison point does not exist in this log"
        )
    return max(below, key=lambda b: float(b["time"]))


def find_window_end_block(parsed: dict, window_end: float) -> dict:
    """The block AT the window end (prereg 8; 6.5e-05, or 3.9e-05 under 7.2)."""
    hits = [b for b in parsed["blocks"] if float(b["time"]) == window_end]
    if len(hits) != 1:
        raise ControlFailure(
            f"{parsed['path']}: found {len(hits)} `Time = ` blocks at the window "
            f"end {window_end}; section 8 needs exactly one"
        )
    return hits[0]


# --------------------------------------------------------------------------
# The inlet map and the prereg 13.2 reference state (AMENDMENT 1).
# --------------------------------------------------------------------------

def _strip_foam_comments(text: str) -> str:
    """Remove /* */ and // comments. Necessary, not cosmetic: 0/U's inlet entry
    carries a prose comment containing both `(` and `)`, which would otherwise
    be parsed as list delimiters."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def _foam_list_after(text: str, header_re: str, vector: bool) -> list:
    """Read a `<header> N ( ... )` OpenFOAM list, returning N parsed entries."""
    m = re.search(header_re + r"\s*(\d+)\s*\(", text, re.S)
    if not m:
        raise ControlFailure(f"could not find an OpenFOAM list matching {header_re!r}")
    n = int(m.group(1))
    rest = text[m.end():]
    depth, k = 1, 0
    while k < len(rest) and depth > 0:
        if rest[k] == "(":
            depth += 1
        elif rest[k] == ")":
            depth -= 1
        k += 1
    if depth != 0:
        raise ControlFailure(f"unterminated OpenFOAM list for {header_re!r}")
    body = rest[:k - 1]
    if vector:
        vals = [[float(x) for x in v.split()]
                for v in re.findall(r"\(([^()]*)\)", body)]
    else:
        vals = [float(x) for x in body.split()]
    if len(vals) != n:
        raise ControlFailure(
            f"OpenFOAM list for {header_re!r} declares {n} entries, parsed {len(vals)}"
        )
    return vals


def inlet_owner_cells(step_dir: Path) -> list[int]:
    """The owner cell of every `inlet` face, IN FACE ORDER (prereg 13.2).

    constant/polyMesh/boundary gives the inlet patch's startFace and nFaces; the
    slice of constant/polyMesh/owner over [startFace, startFace + nFaces) is the
    same ordering as the nonuniform Lists of 0/U and 0/T.
    """
    pm = step_dir / "constant" / "polyMesh"
    bnd = (pm / "boundary").read_text()
    bnd = bnd.split("// * * *", 1)[-1]
    m = re.search(r"\binlet\s*\{(.*?)\}", bnd, re.S)
    if not m:
        raise ControlFailure(f"{pm/'boundary'}: no `inlet` patch entry")
    mf = re.search(r"nFaces\s+(\d+)\s*;", m.group(1))
    ms = re.search(r"startFace\s+(\d+)\s*;", m.group(1))
    if not (mf and ms):
        raise ControlFailure(f"{pm/'boundary'}: inlet entry lacks nFaces/startFace")
    n_faces, start_face = int(mf.group(1)), int(ms.group(1))
    if n_faces == 0:
        raise ControlFailure(f"{pm/'boundary'}: inlet has nFaces 0")

    own_txt = (pm / "owner").read_text().split("// * * *", 1)[-1]
    mh = re.search(r"(\d+)\s*\(", own_txt)
    if not mh:
        raise ControlFailure(f"{pm/'owner'}: no list header")
    n_total = int(mh.group(1))
    nums = re.findall(r"-?\d+", own_txt[mh.end():])
    if len(nums) < n_total:
        raise ControlFailure(
            f"{pm/'owner'}: declares {n_total} entries, only {len(nums)} readable"
        )
    owners = [int(x) for x in nums[:n_total]]
    if start_face + n_faces > n_total:
        raise ControlFailure(
            f"{pm/'owner'}: inlet range [{start_face},{start_face+n_faces}) "
            f"runs past the {n_total} owner entries"
        )
    inlet = owners[start_face:start_face + n_faces]
    if len(set(inlet)) != len(inlet):
        raise ControlFailure(
            f"{pm/'owner'}: the inlet owner map is not one-to-one; a cell owning "
            "two inlet faces would make the 13.2 reference ambiguous"
        )
    return inlet


def reference_state(step_dir: Path, cell: int) -> dict:
    """The prereg 8.3 reference state for one cell, per 13.2 (AMENDMENT 1).

    Inlet-face owner  -> that face's own Table II profile: |U| and T from the
                         0/U and 0/T nonuniform Lists, rho = p/(R T) with
                         p = INLET_P_PA and R = R_GAS.
    Otherwise         -> the NASA TM 101075 Table I freestream.
    Quoted NUMERICALLY in the results record, never by name (prereg 13.2's own
    disclosure: p/(R T) at the freestream face is 2.16 % below the tabulated
    rho_inf, which is inside the 10 % band but must be visible to the reader).
    """
    inlet = inlet_owner_cells(step_dir)
    if cell not in inlet:
        return {"kind": "freestream", "inlet_face": None,
                "rho_ref": RHO_INF, "magU_ref": MAG_U_INF, "T_ref": T_INF,
                "note": "not inlet-adjacent (prereg 13.2 second bullet)"}
    face = inlet.index(cell)
    u_txt = _strip_foam_comments((step_dir / "0" / "U").read_text())
    t_txt = _strip_foam_comments((step_dir / "0" / "T").read_text())
    u_txt = u_txt[u_txt.index("boundaryField"):]
    t_txt = t_txt[t_txt.index("boundaryField"):]
    u_txt = u_txt[u_txt.index("inlet"):]
    t_txt = t_txt[t_txt.index("inlet"):]
    uvals = _foam_list_after(u_txt, r"nonuniform\s+List<vector>", vector=True)
    tvals = _foam_list_after(t_txt, r"nonuniform\s+List<scalar>", vector=False)
    if len(uvals) != len(inlet) or len(tvals) != len(inlet):
        raise ControlFailure(
            f"prereg 13.2: inlet map has {len(inlet)} faces but 0/U has "
            f"{len(uvals)} and 0/T has {len(tvals)} entries -- the orderings "
            "cannot be the same map"
        )
    ux, uy, uz = uvals[face]
    mag_u = (ux * ux + uy * uy + uz * uz) ** 0.5
    t_ref = tvals[face]
    return {"kind": "inlet-adjacent", "inlet_face": face,
            "rho_ref": INLET_P_PA / (R_GAS * t_ref),
            "magU_ref": mag_u, "T_ref": t_ref,
            "note": f"inlet face index {face} (prereg 13.2 first bullet)"}


# --------------------------------------------------------------------------
# Completion (prereg 7) and the measurement clauses (prereg 8).
#
# Bodies written AFTER first compute (both steps landed at 7cdb26f4) against the
# constants, labels and refusal structure frozen above. Nothing below chooses a
# threshold: every number it compares against is a module constant taken verbatim
# from the frozen document, and the one reading it fixes -- which of the two
# boundE.H sets section 8 means -- is the subject of ADDENDUM 2 (prereg 14),
# ruled on mechanism with both readings disclosed. This file is a measurement
# script: SUPERVISION_CHARTER.md 3 makes reading its diff AS A DIFF a supervisor
# personal check, and nothing it prints is believed before that read.
# --------------------------------------------------------------------------

def read_rc(step_dir: Path) -> int | None:
    """The solver's exit code, from <STEP>/RC.txt. None if not captured.

    prereg 13.3 rule 1 makes rc the PRIMARY SIGFPE signal, and prereg 7.2 makes
    it the only admissible evidence of a cap stop. `None` is returned rather than
    guessed, and every caller says what it did with the absence.
    """
    rc_file = step_dir / "RC.txt"
    if not rc_file.exists():
        return None
    m = re.search(r"^rc=(-?\d+)", rc_file.read_text(errors="replace"), re.M)
    return int(m.group(1)) if m else None


def _is_numeric_time(name: str) -> bool:
    try:
        float(name)
    except ValueError:
        return False
    return True


def time_dir_state(step_dir: Path, tname: str) -> dict:
    """Fields present under <STEP>/<tname>/ and the age guard against 0/T."""
    ref = step_dir / "0" / "T"
    if not ref.exists():
        raise ControlFailure(
            f"{step_dir}: no 0/T, so the age guard (standing rule 4) cannot be "
            "evaluated; refusing rather than skipping it"
        )
    ref_mtime = ref.stat().st_mtime
    tdir = step_dir / tname
    if not tdir.is_dir():
        return {"time": tname, "exists": False, "missing": list(FIELDS_REQUIRED),
                "stale": [], "ok": False, "ref_mtime": ref_mtime}
    missing, stale = [], []
    for f in FIELDS_REQUIRED:
        p = tdir / f
        if not p.exists():
            missing.append(f)
        elif p.stat().st_mtime <= ref_mtime:
            stale.append(f)
    return {"time": tname, "exists": True, "missing": missing, "stale": stale,
            "ok": not missing and not stale, "ref_mtime": ref_mtime}


def check_completion(step_dir: Path, log: Path,
                     out: list[str] | None = None) -> str:
    """-> 'COMPLETE' | 'TRUNCATED-AT-CAP' | 'SIGFPE-RECURRENCE' | 'BLOCKED'.

    Clauses, all of which must hold for COMPLETE (prereg 7.1):
      rc == 0; an `End` line; last `Time =` == endTime 6.5e-05; every `Time =`
      block carries exactly one ExecutionTime line and the counts are equal;
      T U p alphat k nut omega present under 6.5e-05/; every one of them newer
      than this step's own 0/T (the age guard).
    TRUNCATED-AT-CAP (prereg 7.2) applies the same clauses at 3.9e-05 and only
    when the stop was the 6 core-min cap.
    SIGFPE-RECURRENCE (prereg 7.3) needs >= 200 Time blocks and a field write --
    as amended by 13.1, ANY numeric time directory other than 0 carrying all
    seven fields, every one newer than 0/T (1.3e-05/ is deleted by purgeWrite 3).

    `out`, if given, collects the clause-by-clause evidence. The status string is
    the return value; the SIGFPE-ABSENT / SIGFPE-RECURRENCE label of prereg 7.3's
    last paragraph is recorded UNCONDITIONALLY into `out`, so neither the absence
    nor the presence of a crash can go unrecorded.
    """
    say = out.append if out is not None else (lambda _s: None)
    parsed = parse_log(log)
    rc = read_rc(step_dir)
    blocks = parsed["blocks"]
    n_blocks = len(blocks)
    last_time = parsed["times"][-1] if parsed["times"] else None
    bad_exec = [b["index"] for b in blocks if b["exec_lines"] != 1]

    say(f"completion: step={step_dir.name} log={log.name}")
    say(f"  rc: {rc if rc is not None else 'NOT CAPTURED (no RC.txt / no rc= line)'}")
    say(f"  End line: {parsed['end']}")
    say(f"  `Time = ` blocks: {n_blocks}   ExecutionTime lines: {parsed['exec_lines']}")
    say(f"  blocks NOT carrying exactly one ExecutionTime line: {len(bad_exec)}"
        + (f" (first: {bad_exec[:5]})" if bad_exec else ""))
    say(f"  last `Time = `: {last_time}   endTime (prereg 1.3): {T_END_FULL}")

    # prereg 13.3: rc == SIGFPE_RC is primary, the backtrace frame is secondary.
    sigfpe = (rc == SIGFPE_RC) or parsed["sigfpe"]
    signal = ("rc" if rc == SIGFPE_RC
              else "log backtrace frame (SECONDARY -- a log artefact)"
              if parsed["sigfpe"] else "none")
    say(f"  SIGFPE: {sigfpe} (signal: {signal}); prereg 7.3 label: "
        f"{'SIGFPE-RECURRENCE' if sigfpe else 'SIGFPE-ABSENT'}")

    if sigfpe:
        writes = [d.name for d in sorted(step_dir.iterdir())
                  if d.is_dir() and _is_numeric_time(d.name)
                  and float(d.name) != 0.0]
        usable = [t for t in writes if time_dir_state(step_dir, t)["ok"]]
        say(f"  7.3 (as amended by 13.1): numeric time dirs other than 0: "
            f"{writes}; complete + age-guarded: {usable}")
        if n_blocks >= SIGFPE_MIN_BLOCKS and usable:
            say(f"  -> SIGFPE-RECURRENCE (>= {SIGFPE_MIN_BLOCKS} blocks and a "
                f"surviving field write at {usable[-1]}/)")
            return "SIGFPE-RECURRENCE"
        say(f"  -> BLOCKED: a SIGFPE with {n_blocks} blocks and "
            f"{len(usable)} usable field write(s) fails prereg 7.3")
        return "BLOCKED"

    full = time_dir_state(step_dir, "6.5e-05")
    say(f"  fields at 6.5e-05/: exists={full['exists']} missing={full['missing']} "
        f"older-or-equal-to-0/T={full['stale']}")
    complete = (
        rc == 0
        and parsed["end"]
        and last_time is not None and float(last_time) == T_END_FULL
        and not bad_exec
        and parsed["exec_lines"] == n_blocks
        and full["ok"]
    )
    if complete:
        say("  -> COMPLETE (every prereg 7.1 clause holds)")
        return "COMPLETE"

    trunc = time_dir_state(step_dir, "3.9e-05")
    cap_stop = (rc == CAP_STOP_RC)
    say(f"  7.2: cap stop asserted? {cap_stop} (rc == {CAP_STOP_RC}); "
        f"fields at 3.9e-05/: exists={trunc['exists']} missing={trunc['missing']} "
        f"older-or-equal-to-0/T={trunc['stale']}")
    if (cap_stop and last_time is not None
            and float(last_time) >= T_END_TRUNC and trunc["ok"]):
        say("  -> TRUNCATED-AT-CAP (graded on the pre-declared [0, 3.9e-05] window)")
        return "TRUNCATED-AT-CAP"

    say("  -> BLOCKED (prereg 7.4). BLOCKED is a statement about the run, "
        "never about the physics (L-255's corollary).")
    return "BLOCKED"


# --------------------------------------------------------------------------

def _bin_indices() -> tuple[list[int], list[int]]:
    """prereg 8.2's two bin groups, DERIVED from BIN_EDGES rather than hardcoded
    so the histogram definition and the threshold cannot drift apart."""
    in_1950_20 = [i for i, (lo, _hi) in enumerate(BIN_EDGES) if lo >= 19.5]
    at_or_below_10 = [i for i, (_lo, hi) in enumerate(BIN_EDGES) if hi <= 10.0]
    return in_1950_20, at_or_below_10


def _hist_read(ev) -> dict:
    """prereg 8.2 over one event's clamped population."""
    if ev is None:
        return {"label": None, "note": "event ABSENT"}
    if len(ev.bins) != len(BIN_EDGES):
        raise ControlFailure(
            f"prereg 8.2: event at t={ev.time} carries {len(ev.bins)} histogram "
            f"bins, expected {len(BIN_EDGES)}"
        )
    if sum(ev.bins) != ev.n_low:
        raise ControlFailure(
            f"prereg 8.2: histogram at t={ev.time} sums to {sum(ev.bins)}, "
            f"nLow={ev.n_low}"
        )
    if ev.n_low == 0:
        raise ControlFailure(
            f"prereg 8.2: nLow = 0 at t={ev.time}; the fraction is undefined"
        )
    hi_idx, lo_idx = _bin_indices()
    f_hi = sum(ev.bins[i] for i in hi_idx) / ev.n_low
    f_lo = sum(ev.bins[i] for i in lo_idx) / ev.n_low
    if f_hi >= THRESHOLD_ARTIFACT_FRAC:
        label = "THRESHOLD-ARTIFACT"
    elif f_lo >= GENUINE_DIVERGENCE_FRAC:
        label = "GENUINE-DIVERGENCE"
    else:
        label = "MIXED"
    return {"label": label, "frac_19p5_to_20": f_hi, "frac_le_10K": f_lo,
            "bins": list(ev.bins), "n_low": ev.n_low,
            "bins_in_19p5_to_20": hi_idx, "bins_le_10K": lo_idx}


def _attribution_read(step_dir: Path, parsed: dict, k: int) -> dict:
    """prereg 8.3 with the 13.2 reference rule, for event ordinal k."""
    first = None
    for b in parsed["blocks"]:
        ev = select_event(b, k, required=False)
        if ev is not None and ev.n_low > 0:
            first = (b, ev)
            break
    if first is None:
        return {"label": None, "note": f"no block carries an event {k} with nLow > 0"}
    b, ev = first
    if not hasattr(ev, "worst_cell_diag"):
        raise ControlFailure(
            f"prereg 8.3: the event {k} set at t={b['time']} has no BOUNDDIAG "
            "line, so the worst-low cell's rho and |U| cannot be read"
        )
    if ev.worst_cell_diag != ev.worst_cell:
        raise ControlFailure(
            f"prereg 8.3: BOUND says worst cell {ev.worst_cell} and BOUNDDIAG "
            f"says {ev.worst_cell_diag} at t={b['time']}; refusing"
        )
    ref = reference_state(step_dir, ev.worst_cell)
    d_rho = ev.worst_rho / ref["rho_ref"] - 1.0
    d_u = ev.worst_magu / ref["magU_ref"] - 1.0
    rho_out = abs(d_rho) > RHO_BAND
    u_out = abs(d_u) > U_BAND
    if rho_out and not u_out:
        label = "RHO-FIRST"
    elif u_out and not rho_out:
        label = "U-FIRST"
    elif not rho_out and not u_out:
        label = "E-FIRST"
    else:
        label = "INDETERMINATE"
    return {"label": label, "block": b["index"], "time": b["time"],
            "n_low": ev.n_low, "worst_cell": ev.worst_cell,
            "worst_rho": ev.worst_rho, "worst_magu": ev.worst_magu,
            "reference": ref, "d_rho": d_rho, "d_magU": d_u,
            "rho_outside_band": rho_out, "magU_outside_band": u_out}


def grade_step0(parsed: dict, window_end: float = T_END_FULL) -> dict:
    """S0a/S0b -> BASELINE-RECOVERED | BASELINE-NOT-RECOVERED (prereg 8.1),
    plus the free histogram read (8.2) and the attribution read (8.3).

    prereg 14.2/14.5: EVENT 1 is graded; event 2 is computed and printed beside
    every graded number, UNGRADED, together with the label the event-2 reading
    would return. Nothing here chooses a threshold -- S0A_BAND, the 8.2 fractions
    and the 8.3 bands are frozen module constants.
    """
    step_dir = Path(parsed["path"]).parent
    b_star = find_t_star_block(parsed)
    b_end = find_window_end_block(parsed, window_end)
    res = {"step_dir": str(step_dir), "window_end": window_end,
           "t_star_block": b_star["index"], "t_star_time": b_star["time"],
           "graded_event": EVENT_GRADED, "events": {}, "report": []}
    say = res["report"].append

    say(f"=== prereg 8, Step 0: {step_dir.name} "
        f"(window end {window_end}, t* block {b_star['index']} "
        f"t={b_star['time']}) ===")
    say(f"    Event selection: prereg 14.2/14.3 -- GRADED = event {EVENT_GRADED} "
        "(boundE.H at .C:267); event 2 (.C:282) is UNGRADED and printed beside.")

    for k in (EVENT_GRADED, EVENT_ALT):
        required = (k == EVENT_GRADED)
        ev_star = select_event(b_star, k, required=required)
        ev_end = select_event(b_end, k, required=required)
        e: dict = {"ordinal": k, "graded": required}
        if ev_star is None or ev_end is None:
            e.update({"label_8_1": None,
                      "note": "event ABSENT at t* and/or the window end "
                              "(prereg 14.3: ABSENT, not nLow = 0)"})
            res["events"][k] = e
            say(f"  event {k}: {describe_event(ev_star)} at t*; "
                f"{describe_event(ev_end)} at the window end")
            continue
        f_star, f_end = ev_star.fraction, ev_end.fraction
        s0a = S0A_BAND[0] <= f_star <= S0A_BAND[1]
        s0b = f_end >= f_star
        e.update({
            "n_low_t_star": ev_star.n_low, "frac_t_star": f_star,
            "n_low_end": ev_end.n_low, "frac_end": f_end,
            "S0a": s0a, "S0b": s0b,
            "label_8_1": "BASELINE-RECOVERED" if (s0a and s0b)
                         else "BASELINE-NOT-RECOVERED",
            "read_8_2": _hist_read(ev_end),
            "read_8_3": _attribution_read(step_dir, parsed, k),
        })
        res["events"][k] = e
        tag = "GRADED" if required else "UNGRADED (event 2, :282 re-clamp)"
        say(f"  event {k} [{tag}]:")
        say(f"    t*  {b_star['time']}: nLow={ev_star.n_low}/{N_CELLS} "
            f"= {100*f_star:.4f} %   S0a band {100*S0A_BAND[0]:g}-"
            f"{100*S0A_BAND[1]:g} % -> S0a={s0a}")
        say(f"    end {b_end['time']}: nLow={ev_end.n_low}/{N_CELLS} "
            f"= {100*f_end:.4f} %   S0b (end >= t*) -> S0b={s0b}")
        say(f"    8.1 label: {e['label_8_1']}")
        h = e["read_8_2"]
        say(f"    8.2 label: {h['label']}  "
            f"(in (19.5,20) K: {100*h['frac_19p5_to_20']:.4f} % vs "
            f"{100*THRESHOLD_ARTIFACT_FRAC:g} %; at T <= 10 K: "
            f"{100*h['frac_le_10K']:.4f} % vs {100*GENUINE_DIVERGENCE_FRAC:g} %)")
        a = e["read_8_3"]
        if a["label"] is None:
            say(f"    8.3: {a['note']}")
        else:
            r = a["reference"]
            say(f"    8.3 label: {a['label']}  first block with nLow>0: "
                f"{a['block']} (t={a['time']}), worst cell {a['worst_cell']}")
            say(f"        reference (prereg 13.2): {r['kind']}, {r['note']}; "
                f"rho_ref={r['rho_ref']:.6f} kg/m3 magU_ref={r['magU_ref']:.4f} "
                f"m/s T_ref={r['T_ref']:.4f} K")
            say(f"        worst cell: rho={a['worst_rho']} magU={a['worst_magu']}"
                f"  ->  rho dev {a['d_rho']:+.4f} (band {RHO_BAND}), "
                f"magU dev {a['d_magU']:+.4f} (band {U_BAND})")

    g, alt = res["events"][EVENT_GRADED], res["events"].get(EVENT_ALT, {})
    res["label_8_1"] = g["label_8_1"]
    res["label_8_2"] = g["read_8_2"]["label"]
    res["label_8_3"] = g["read_8_3"]["label"]
    res["alt_label_8_1"] = alt.get("label_8_1")
    res["alt_label_8_2"] = (alt.get("read_8_2") or {}).get("label")
    res["alt_label_8_3"] = (alt.get("read_8_3") or {}).get("label")
    say("  ALTERNATIVE READING (prereg 14.5, NOT a verdict): under event 2 the "
        f"labels would be 8.1={res['alt_label_8_1']} 8.2={res['alt_label_8_2']} "
        f"8.3={res['alt_label_8_3']}.")
    if res["alt_label_8_1"] != res["label_8_1"]:
        say("  MATERIAL: the two readings disagree on the 8.1 label. Per prereg "
            "9.1 a BASELINE-NOT-RECOVERED Step 0 makes the discrimination "
            "question NOT A RESULT whatever Step 1 shows. The ruling that "
            "selects event 1 is prereg 14.2 and rests on mechanism; both columns "
            "are disclosed in 14.4.")
    return res


def first_differing_block(log0: Path, log1: Path) -> dict:
    """The first `Time = ` block whose content differs (prereg 6, C2's record
    requirement: "the results record quotes the first differing `Time = ` block").

    control_c2() answers only whether the logs differ at all, and reports the
    first differing TIME TOKEN -- which is None when both runs take identical
    timestep sequences, as these two do. This function is additive and does NOT
    modify control C2 or normalised_md5: a control is not refactored after first
    compute. The only wall-clock-dependent lines that can occur INSIDE a `Time =`
    block are ExecutionTime and ClockTime (the Date/Host/PID/Exec/Case header
    lines all precede the first block), so those two are the whole filter here.
    """
    def blocks_of(p: Path) -> list[dict]:
        out, cur = [], None
        for ln in p.read_text(errors="replace").splitlines():
            m = RE_TIME.match(ln)
            if m:
                cur = {"time": m.group(1), "lines": []}
                out.append(cur)
                continue
            if cur is None:
                continue
            if ln.startswith("ExecutionTime") or ln.startswith("ClockTime"):
                continue
            cur["lines"].append(ln)
        return out

    b0, b1 = blocks_of(log0), blocks_of(log1)
    for i in range(min(len(b0), len(b1))):
        if b0[i]["time"] != b1[i]["time"] or b0[i]["lines"] != b1[i]["lines"]:
            pair = next(((x, y) for x, y in zip(b0[i]["lines"], b1[i]["lines"])
                         if x != y), (None, None))
            return {"block": i, "time0": b0[i]["time"], "time1": b1[i]["time"],
                    "line0": pair[0], "line1": pair[1],
                    "n_blocks0": len(b0), "n_blocks1": len(b1)}
    if len(b0) != len(b1):
        return {"block": min(len(b0), len(b1)), "time0": None, "time1": None,
                "line0": None, "line1": None,
                "n_blocks0": len(b0), "n_blocks1": len(b1),
                "note": "blocks identical up to the shorter log; lengths differ"}
    return {"block": None, "note": "no differing `Time = ` block"}


def grade_step1(parsed0: dict, parsed1: dict, window_end: float = T_END_FULL,
                status0: str | None = None, status1: str | None = None) -> dict:
    """S1a/S1b -> DEFICIT-IMPLICATED | DEFICIT-NOT-IMPLICATED (prereg 8.4).
    Reached only when control C2 reports the logs differ.

    prereg 8.4 also requires a Step 0 of the SAME completion status (7.2); when
    both statuses are supplied and differ, this refuses rather than producing an
    unmatched ratio. Event 1 is graded and event 2 is printed beside it,
    UNGRADED, with the label the alternative reading would return (14.5).
    """
    if normalised_md5(Path(parsed0["path"])) == normalised_md5(Path(parsed1["path"])):
        raise ControlFailure(
            "prereg 8.4 is evaluated ONLY if control C2 reports the logs differ; "
            "these two are byte-equivalent after stripping wall-clock lines "
            "(LEVER-INERT). The discrimination question is NOT A RESULT."
        )
    if status0 is not None and status1 is not None and status0 != status1:
        raise ControlFailure(
            f"prereg 7.2: Step 0 is {status0} and Step 1 is {status1}. A COMPLETE "
            "step compared against a TRUNCATED-AT-CAP step is not a matched "
            "comparison; both must be re-read on [0, 3.9e-05]. Refusing."
        )
    b0s, b0e = find_t_star_block(parsed0), find_window_end_block(parsed0, window_end)
    b1s, b1e = find_t_star_block(parsed1), find_window_end_block(parsed1, window_end)
    if b0s["time"] != b1s["time"]:
        raise ControlFailure(
            f"prereg 8.4 needs the SAME t*: Step 0 has {b0s['time']}, Step 1 has "
            f"{b1s['time']}. Refusing an unmatched ratio."
        )
    res = {"window_end": window_end, "t_star_time": b0s["time"],
           "graded_event": EVENT_GRADED, "events": {}, "report": []}
    say = res["report"].append
    say(f"=== prereg 8.4, Step 1 vs Step 0 (t* {b0s['time']}, window end "
        f"{window_end}) ===")
    say(f"    Event selection: prereg 14.2/14.3 -- GRADED = event {EVENT_GRADED} "
        "(boundE.H at .C:267 / :269); event 2 UNGRADED and printed beside.")
    fd = first_differing_block(Path(parsed0["path"]), Path(parsed1["path"]))
    res["first_differing_block"] = fd
    say(f"    C2 record requirement (prereg 6): first differing `Time = ` block: {fd}")

    for k in (EVENT_GRADED, EVENT_ALT):
        required = (k == EVENT_GRADED)
        e0s = select_event(b0s, k, required=required)
        e0e = select_event(b0e, k, required=required)
        e1s = select_event(b1s, k, required=required)
        e1e = select_event(b1e, k, required=required)
        e: dict = {"ordinal": k, "graded": required}
        if None in (e0s, e0e, e1s, e1e):
            e.update({"label_8_4": None,
                      "note": "event ABSENT in at least one required block "
                              "(prereg 14.3: ABSENT, not nLow = 0)"})
            res["events"][k] = e
            say(f"  event {k}: step0 t*={describe_event(e0s)}; "
                f"step1 t*={describe_event(e1s)}")
            continue
        f0s, f0e, f1s, f1e = (e0s.fraction, e0e.fraction,
                              e1s.fraction, e1e.fraction)
        s1a = f1s < S1A_RATIO * f0s
        s1b = (f1e < FLATTEN_RATIO * f1s) and (f0e >= FLATTEN_RATIO * f0s)
        e.update({
            "step0_n_low_t_star": e0s.n_low, "step0_frac_t_star": f0s,
            "step0_n_low_end": e0e.n_low, "step0_frac_end": f0e,
            "step1_n_low_t_star": e1s.n_low, "step1_frac_t_star": f1s,
            "step1_n_low_end": e1e.n_low, "step1_frac_end": f1e,
            "ratio_t_star": (f1s / f0s) if f0s else float("inf"),
            "step0_growth": (f0e / f0s) if f0s else float("inf"),
            "step1_growth": (f1e / f1s) if f1s else float("inf"),
            "S1a": s1a, "S1b": s1b,
            "label_8_4": "DEFICIT-IMPLICATED" if (s1a and s1b)
                         else "DEFICIT-NOT-IMPLICATED",
        })
        res["events"][k] = e
        tag = "GRADED" if required else "UNGRADED (event 2, :282 re-clamp)"
        say(f"  event {k} [{tag}]:")
        say(f"    t*  step0 nLow={e0s.n_low} ({100*f0s:.4f} %)   "
            f"step1 nLow={e1s.n_low} ({100*f1s:.4f} %)   "
            f"ratio {e['ratio_t_star']:.4f} vs S1a threshold {S1A_RATIO} "
            f"-> S1a={s1a}")
        say(f"    end step0 nLow={e0e.n_low} ({100*f0e:.4f} %) growth "
            f"{e['step0_growth']:.4f}   step1 nLow={e1e.n_low} "
            f"({100*f1e:.4f} %) growth {e['step1_growth']:.4f}   "
            f"flatten threshold {FLATTEN_RATIO} -> S1b={s1b}")
        say(f"    8.4 label: {e['label_8_4']}")

    res["label_8_4"] = res["events"][EVENT_GRADED]["label_8_4"]
    res["alt_label_8_4"] = res["events"].get(EVENT_ALT, {}).get("label_8_4")
    say("  ALTERNATIVE READING (prereg 14.5, NOT a verdict): under event 2 the "
        f"8.4 label would be {res['alt_label_8_4']}.")
    if res["alt_label_8_4"] != res["label_8_4"]:
        say("  MATERIAL: the two readings disagree on the 8.4 label. Both "
            "columns are disclosed; the ruling that selects event 1 is prereg "
            "14.2 and rests on mechanism, not on these numbers.")
    return res


# --------------------------------------------------------------------------
# Self-test of the prereg 14.3 event-selection rule, on a SYNTHETIC log.
#
# Standing rule 3 applied to the ordinal itself: an event-1 reading from a
# selector not shown able to return a DIFFERENT value for event 2 is not
# evidence that event 1 was read. The synthetic block below carries two sets
# with deliberately distinct counts (100 and 40), so a selector that silently
# took the last set, or the largest, or the only one it happened to key by time
# token, returns the wrong number and the test fails.
# --------------------------------------------------------------------------

SYNTHETIC_TWO_EVENT_LOG = """\
Time = 1e-09
Courant Number mean: 0.01 max: 0.2
BOUND: e below eMin in 100 cell(s) at Time = 1e-09, worst e = -200000.5 J/kg \
at cell 7 C = (0 0 0) | low-e cell extent: x=[0,0] r=[0,0]
BOUNDDIAG: t=1e-09 nLow=100 rhoLow=[0.02,0.03] magULow=[1000,1274] \
TprevLow=[80,82] worst: cell=7 rho=0.0201 magU=1000.5 Tprev=81.2 Timp=19.2
BOUNDHIST: t=1e-09 nLow=100 bins=0 0 0 0 0 0 0 0 0 0 0 100
BOUND: e above eMax in 3 cell(s) at Time = 1e-09, worst e = 5e+06 J/kg at cell 9 C = (0 0 0)
BOUND: e below eMin in 40 cell(s) at Time = 1e-09, worst e = -199530.25 J/kg \
at cell 0 C = (0 0 0) | low-e cell extent: x=[0,0] r=[0,0]
BOUNDDIAG: t=1e-09 nLow=40 rhoLow=[0.024,0.025] magULow=[1270,1274] \
TprevLow=[139.6,139.6] worst: cell=0 rho=0.0246 magU=1274.0 Tprev=139.583 Timp=19.99
BOUNDHIST: t=1e-09 nLow=40 bins=0 0 0 0 0 0 0 0 0 0 0 40
ExecutionTime = 1 s  ClockTime = 1 s

Time = 2e-09
BOUND: e below eMin in 7 cell(s) at Time = 2e-09, worst e = -199600.5 J/kg \
at cell 3 C = (0 0 0) | low-e cell extent: x=[0,0] r=[0,0]
BOUNDDIAG: t=2e-09 nLow=7 rhoLow=[0.024,0.025] magULow=[1270,1274] \
TprevLow=[81,82] worst: cell=3 rho=0.0246 magU=1273.0 Tprev=81.2 Timp=19.8844
BOUNDHIST: t=2e-09 nLow=7 bins=0 0 0 0 0 0 0 0 0 7 0 0
ExecutionTime = 2 s  ClockTime = 2 s

Time = 3e-09
ExecutionTime = 3 s  ClockTime = 3 s
End
"""


def _synthetic_blocks() -> list[dict]:
    """Parse the synthetic log from a real file on disk (not from a string), so
    the test exercises the same read path the real logs take."""
    d = Path(tempfile.mkdtemp(prefix="f4_event_selftest_"))
    p = d / "log.synthetic"
    p.write_text(SYNTHETIC_TWO_EVENT_LOG)
    return parse_log(p)["blocks"]


def selftest_event_selection() -> list[str]:
    """prereg 14.3: event k is the k-th BOUND-family set in a `Time = ` block."""
    blocks = _synthetic_blocks()
    if len(blocks) != 3:
        raise ControlFailure(
            f"14.3 selftest: synthetic log parsed {len(blocks)} `Time = ` blocks, "
            "expected 3"
        )
    b0, b1, b2 = blocks

    if len(b0["events"]) != 2:
        raise ControlFailure(
            f"14.3 selftest: the two-event block parsed {len(b0['events'])} "
            "BOUND-family sets, expected 2 -- the interleaved `BOUND: e above "
            "eMax` line must NOT create a set (boundE.H:142-148)"
        )
    e1, e2 = select_event(b0, 1), select_event(b0, 2)
    if e1.n_low != 100:
        raise ControlFailure(
            f"14.3 selftest: event 1 read nLow={e1.n_low}, expected 100. A "
            "selector that took the LAST set would have read 40."
        )
    if e2.n_low != 40:
        raise ControlFailure(f"14.3 selftest: event 2 read nLow={e2.n_low}, expected 40")
    if e1.n_low == e2.n_low:
        raise ControlFailure(
            "14.3 selftest: the planted counts are not distinct, so this test "
            "could not tell a correct selector from a wrong one"
        )
    if (e1.block, e1.ordinal, e2.block, e2.ordinal) != (0, 1, 0, 2):
        raise ControlFailure(
            f"14.3 selftest: ordinals/blocks wrong: {(e1.block, e1.ordinal)} "
            f"{(e2.block, e2.ordinal)}, expected (0,1) (0,2)"
        )
    if e1.worst_cell != 7 or e2.worst_cell != 0 or e1.bins[11] != 100 or e2.bins[11] != 40:
        raise ControlFailure(
            "14.3 selftest: BOUNDDIAG/BOUNDHIST did not bind to the set they "
            "follow -- the two sets share one time token and must not be merged"
        )

    if len(b1["events"]) != 1 or select_event(b1, 1).n_low != 7:
        raise ControlFailure("14.3 selftest: the single-set block did not read as event 1 only")
    s1 = select_event(b1, 1)
    if (s1.block, s1.ordinal) != (1, 1):
        # the ordinal must RESET at every `Time = ` line. A global counter would
        # make this (1, 3) and coincide with the correct answer in block 0 only.
        raise ControlFailure(
            f"14.3 selftest: the second block's only set reports "
            f"block={s1.block} ordinal={s1.ordinal}, expected (1, 1) -- the "
            "ordinal must be counted WITHIN the block, not globally"
        )
    absent = select_event(b1, 2, required=False)
    if absent is not None:
        raise ControlFailure(
            f"14.3 selftest: event 2 of a single-set block read as {absent}, "
            "expected ABSENT (None)"
        )
    desc = describe_event(absent)
    if "ABSENT" not in desc or "nLow=0" in desc:
        raise ControlFailure(
            f"14.3 selftest: an absent event described as {desc!r} -- it must "
            "read ABSENT, never as a zero (standing rule 3)"
        )

    if b2["events"]:
        raise ControlFailure("14.3 selftest: the third block should carry no set")
    if select_event(b2, 1, required=False) is not None:
        raise ControlFailure("14.3 selftest: a zero-set block returned an event")
    try:
        select_event(b2, 1)
    except ControlFailure:
        pass
    else:
        raise ControlFailure(
            "14.3 selftest: a REQUIRED event 1 on a zero-set block did not "
            "refuse. A reader that cannot tell `no clamped cells` from `no line "
            "emitted` would report a blind zero (standing rule 3)."
        )

    return [
        "14.3 ok: two-event block -> event 1 nLow=100, event 2 nLow=40 "
        "(distinct by construction; a last-set or largest-set selector fails)",
        "14.3 ok: the interleaved `BOUND: e above eMax` line created no set "
        "and shifted no ordinal",
        "14.3 ok: BOUNDDIAG/BOUNDHIST bound to their own set although both "
        "sets carry the same time token",
        "14.3 ok: single-set block -> event 1 only; event 2 reads ABSENT, "
        "never nLow = 0",
        f"14.3 ok: zero-set block -> select_event(..., required=True) REFUSES; "
        f"main maps ControlFailure to exit {EXIT_CONTROL_FAILURE} "
        f"(measure it with --selftest-refusal-probe)",
    ]


# --------------------------------------------------------------------------
# Grading entry point (prereg 6 gates it; prereg 7, 8, 9 and 14 shape it).
# --------------------------------------------------------------------------

def find_step_log(step_dir: Path) -> Path:
    """The one solver log under a step directory. Refuses if it is not one."""
    cands = [p for p in sorted(step_dir.glob("log.*"))
             if p.is_file() and p.suffix != ".gz" and "planted" not in p.name]
    if len(cands) != 1:
        raise ControlFailure(
            f"{step_dir}: found {len(cands)} candidate solver logs "
            f"({[c.name for c in cands]}); need exactly one"
        )
    return cands[0]


def grade_all(step0_dir: Path, step1_dir: Path, scratch_dir: Path) -> tuple[int, list[str]]:
    """Controls first (prereg 6), then completion (7), then section 8/9."""
    log0, log1 = find_step_log(step0_dir), find_step_log(step1_dir)
    out = run_controls(log0, log1, scratch_dir)

    # run_controls() asserts this file must exist and be non-empty before Step 0
    # is graded; C0 itself is the twin-run comparison, not this reader's.
    c0 = step0_dir.parent / "c0_twin_diag" / "C0_RESULT.txt"
    if not (c0.exists() and c0.stat().st_size > 0):
        raise ControlFailure(f"C0 artefact missing or empty: {c0}")
    out.append(f"C0 artefact present: {c0} ({c0.stat().st_size} bytes)")

    differ, c2_lines = control_c2(log0, log1)
    out += c2_lines

    out.append("")
    out.append("=== COMPLETION (prereg 7) ===")
    st0 = check_completion(step0_dir, log0, out)
    st1 = check_completion(step1_dir, log1, out)
    out.append(f"Step 0: {st0}    Step 1: {st1}")

    if "BLOCKED" in (st0, st1):
        out.append("prereg 9.1: a BLOCKED step makes the diagnosis PENDING on "
                   "that step. Nothing in section 8 is graded here.")
        return EXIT_BLOCKED, out

    window = T_END_TRUNC if "TRUNCATED-AT-CAP" in (st0, st1) else T_END_FULL
    suffix = " (TRUNCATED)" if window == T_END_TRUNC else ""
    if window == T_END_TRUNC:
        out.append("prereg 7.2: the two steps do not share a COMPLETE status, so "
                   "BOTH are re-read on [0, 3.9e-05] and BOTH labels carry "
                   "(TRUNCATED).")

    parsed0, parsed1 = parse_log(log0), parse_log(log1)
    out.append("")
    r0 = grade_step0(parsed0, window_end=window)
    out += r0["report"]
    out.append(f"Step 0 section 8.1 label: {r0['label_8_1']}{suffix}")

    if "SIGFPE-RECURRENCE" in (st0, st1):
        out.append("")
        out.append("prereg 9.2: a SIGFPE is a MEASUREMENT here, not a hole "
                   "(L-255). The section 8.4 fraction clauses are unevaluable "
                   "against a crashed arm, so the discrimination question is "
                   "not graded. Goes to the supervisor for triage.")
        return EXIT_GRADED, out

    if not differ:
        out.append("prereg 9.1 row 3 / C2: LEVER-INERT. The discrimination "
                   "question is NOT A RESULT and is not graded.")
        return EXIT_LEVER_INERT, out

    out.append("")
    r1 = grade_step1(parsed0, parsed1, window_end=window,
                     status0=st0, status1=st1)
    out += r1["report"]
    out.append(f"Step 1 section 8.4 label: {r1['label_8_4']}{suffix}")
    out.append("")
    out.append("NOTE: every label above is a prereg section 8 MEASUREMENT "
               "OUTCOME LABEL, deliberately outside the rule-1 verdict "
               "vocabulary (prereg section 0). No PASS, GATE REACHED or GATE "
               "FAIL is issued from this document.")
    return EXIT_GRADED, out


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[1] == "--selftest":
        # C1 and C3 need no run; they are the two that prove the reader can see
        # a non-zero and returns zero on a clean file. The 13.3 and 14.3 checks
        # need no run either.
        try:
            for line in (control_c1() + control_c3() + selftest_sigfpe_regex()
                         + selftest_event_selection()):
                print(line)
        except ControlFailure as exc:
            print(f"CONTROL FAILURE: {exc}", file=sys.stderr)
            return EXIT_CONTROL_FAILURE
        print("selftest: C1, C3, the 13.3 SIGFPE-regex check and the 14.3 "
              "event-selection check reproduce. C0/C2/C4 need run logs.")
        return EXIT_GRADED
    if argv[1] == "--selftest-refusal-probe":
        # Deliberately drives the prereg 14.3 refusal through main's own handler,
        # so "refuses with exit 2" is a MEASUREMENT (run it and read $?), not an
        # inspection of the source.
        try:
            zero_set_block = _synthetic_blocks()[2]
            select_event(zero_set_block, EVENT_GRADED)
        except ControlFailure as exc:
            print(f"CONTROL FAILURE: {exc}", file=sys.stderr)
            return EXIT_CONTROL_FAILURE
        print("REFUSAL PROBE DID NOT REFUSE -- this is itself a failure",
              file=sys.stderr)
        return 1
    if argv[1] == "--grade":
        if len(argv) < 4:
            print("usage: --grade <step0_dir> <step1_dir> [scratch_dir]",
                  file=sys.stderr)
            return EXIT_CONTROL_FAILURE
        step0, step1 = Path(argv[2]).resolve(), Path(argv[3]).resolve()
        scratch = Path(argv[4]).resolve() if len(argv) > 4 else (
            step0 / f"c4_plant_{os.getpid()}")
        try:
            code, lines = grade_all(step0, step1, scratch)
        except ControlFailure as exc:
            print(f"CONTROL FAILURE: {exc}", file=sys.stderr)
            return EXIT_CONTROL_FAILURE
        for line in lines:
            print(line)
        return code
    print("usage: analyse_f4_sigfpe_step01.py "
          "[--selftest | --selftest-refusal-probe | "
          "--grade <step0_dir> <step1_dir> [scratch_dir]]",
          file=sys.stderr)
    return EXIT_CONTROL_FAILURE


if __name__ == "__main__":
    sys.exit(main(sys.argv))
