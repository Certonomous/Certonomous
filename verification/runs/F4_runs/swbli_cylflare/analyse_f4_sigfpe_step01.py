#!/usr/bin/env python3
"""Grading reader for the F4 SWBLI Step 0 / Step 1 clamp-discrimination experiment.

SKELETON, COMMITTED BEFORE COMPUTE, per the house rule that the grading path is
fixed at the pre-registration commit (CLAUDE.md rule 2). Frozen alongside
    verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md

NOTHING HAS BEEN LAUNCHED. This file has never been run against a solver log
because no such log exists: every `BOUND:` log from every bounded run of this
case is gone from disk (F4_hypersonic_blunt_body.md 8.8, re-verified
2026-08-23), and the two new runs are not authorised.

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
import re
import sys
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
    """Parse a solver log into clamp events, time blocks and completion facts."""
    events: list[ClampEvent] = []
    times: list[str] = []
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
            continue
        if RE_EXEC.match(line):
            exec_lines += 1
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
        "path": path, "events": events, "times": times,
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
# Completion (prereg 7) and the measurement clauses (prereg 8).
#
# NOT YET IMPLEMENTED -- deliberately. These functions are the graded path and
# their bodies are written when there is a run to grade, under the frozen
# constants above. Writing a grading body now, against no data, would invite
# tuning it to a log that does not exist. The constants, the labels and the
# refusal structure ARE frozen here; the arithmetic that consumes them is
# mechanical and is reviewed as a diff before first use.
# --------------------------------------------------------------------------

def check_completion(step_dir: Path, log: Path) -> str:
    """-> 'COMPLETE' | 'TRUNCATED-AT-CAP' | 'SIGFPE-RECURRENCE' | 'BLOCKED'.

    Clauses, all of which must hold for COMPLETE (prereg 7.1):
      rc == 0; an `End` line; last `Time =` == endTime 6.5e-05; every `Time =`
      block carries exactly one ExecutionTime line and the counts are equal;
      T U p alphat k nut omega present under 6.5e-05/; every one of them newer
      than this step's own 0/T (the age guard).
    TRUNCATED-AT-CAP (prereg 7.2) applies the same clauses at 3.9e-05 and only
    when the stop was the 6 core-min cap.
    SIGFPE-RECURRENCE (prereg 7.3) needs >= 200 Time blocks and a field write.
    """
    raise NotImplementedError(
        "frozen skeleton -- body written when a run exists to grade"
    )


def grade_step0(parsed: dict) -> dict:
    """S0a/S0b -> BASELINE-RECOVERED | BASELINE-NOT-RECOVERED (prereg 8.1),
    plus the free histogram read (8.2) and the attribution read (8.3)."""
    raise NotImplementedError(
        "frozen skeleton -- body written when a run exists to grade"
    )


def grade_step1(parsed0: dict, parsed1: dict) -> dict:
    """S1a/S1b -> DEFICIT-IMPLICATED | DEFICIT-NOT-IMPLICATED (prereg 8.4).
    Reached only when control C2 reports the logs differ."""
    raise NotImplementedError(
        "frozen skeleton -- body written when a run exists to grade"
    )


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[1] == "--selftest":
        # Controls C1 and C3 only: they need no run and are the two that prove
        # the reader can see a non-zero and returns zero on a clean file.
        try:
            for line in control_c1() + control_c3() + selftest_sigfpe_regex():
                print(line)
        except ControlFailure as exc:
            print(f"CONTROL FAILURE: {exc}", file=sys.stderr)
            return 2
        print("selftest: C1, C3 and the 13.3 SIGFPE-regex check reproduce. "
              "C2/C4 need run logs.")
        return 0
    print(
        "This reader is a FROZEN SKELETON. No run exists to grade, and the "
        "grading bodies are NotImplementedError by design (see the module "
        "docstring and the section comment above check_completion).",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
