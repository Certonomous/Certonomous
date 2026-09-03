#!/usr/bin/env python3
"""A1WRT -- the wall-resolved alpha-tail reader.  FEASIBILITY READINGS, NOT VERDICTS.

DRAFT INSTRUMENT.  Not frozen, not md5-pinned by any registration yet.  It is
sent to the supervisor to be read AS A DIFF before it is hashed
(SUPERVISION_CHARTER section 3 check 1, not delegable), and the item does not
freeze until that read is done -- because rule 2 fixes the grading path at the
freeze commit, so a reader that does not exist at that commit is not the
grading path.

WHAT IS DIFFERENT FROM `a1wr_read.py`, AND WHY EACH DIFFERENCE EXISTS
====================================================================

1.  `G-FIXTURE`.  `a1wr_read.py:447-457` PREFERS a live artifact of the run it
    is grading as its control fixture, and fell back to a static fixture only
    because zero points converged.  Had one converged, that grading would have
    carried the defect that voided MAAOA (L-435).  A census of all 468 .py
    files under cases/dafoam found SIX instruments affected and FIVE live
    (docs/dafoam/GRADING_FIXTURE_CENSUS.md).

    Here the fixture is a STATIC FILE beside this reader, md5-pinned below, and
    the reader REFUSES if:
      - the fixture's md5 does not match its pin, OR
      - any fixture path resolves inside the run root being graded, OR
      - mtime(fixture) >= mtime(run root)   -- asserted BY EXECUTION.
    The provenance line states origin and sha256 and MUST BE TRUE ABOUT THE
    DISK.  `a1wr_read.py` prints "no sweep log on disk yet" while parsing a
    520,063-byte sweep log four lines later; that string is not reused here.

    ⚠ KNOWN LIMITATION OF THE mtime CLAUSE, DISCLOSED RATHER THAN WEAKENED.
    git does not store mtimes, so a fresh clone or a `git checkout` stamps both
    fixtures with the checkout instant.  Graded against a run root older than
    that checkout, this clause REFUSES -- a false refusal, not a false pass, so
    it fails in the safe direction, but it is a real operational hazard and the
    supervisor should rule on it before the freeze.  The md5 pin and the
    path-containment clause carry the actual independence guarantee; the mtime
    clause is defence in depth.  It is implemented as specified and is not
    silently softened here.

    A DEFECT FOUND IN THIS READER'S OWN CONTROLS AND FIXED, RECORDED BECAUSE IT
    IS THE SHAPE OF THE PROBLEM: control F1 mutates the fixture and restores it.
    Restoring only the BYTES left the fixture newer than every run root, and
    this gate's own mtime assert then refused every subsequent grading -- the
    control breaking the gate it exists to protect.  F1 now restores mtime as
    well and F1b asserts both.  Where a gate reads stat, stat is state.

2.  `G-COMPLETE` IS IMPLEMENTED IN THIS READER, for auditability: one grading
    path is easier to check than three.  ⚠ AN EARLIER VERSION OF THIS COMMENT
    CLAIMED A1WR HAD REGISTERED THE GATE AND NEVER IMPLEMENTED IT.  THAT WAS
    FALSE AND IS WITHDRAWN: A1WR enforces it in `a1wr_runScript_incomp.py:357-362`
    (`AOA_SWEEP_TRUNCATED ... -- NOT a completion`, then `exit(97)`) and in
    `a1wr_cmd.sh:68-71`, and it FIRED LIVE on all six cold controls.  See
    PREREGISTRATION_DRAFT.md section 5.1.  Here the gate additionally draws the
    distinction the registration turns on: a clause this reader CAN evaluate and
    that fails is a GATE FAIL; a clause it CANNOT evaluate is a REFUSAL.

3.  `G-CAPS` IS ARITHMETIC IN THIS READER.  (The same withdrawn claim applied
    here: A1WR enforces its cap in `a1wr_chain_driver.sh:251-257`.)  Here the
    reader computes measured core-min against the registered per-unit cap and
    prints the arithmetic, so the grade-time accounting is not done by hand.

4.  `G-REPRO` HAS TWO LIMBS.  The premise it was first designed on -- "a
    converged steady solution is history-independent" -- is FALSE for this data:
    A1WR's alpha=12 is NOT CONVERGED, it ran to the 4,000-iteration cap while
    still drifting.  So R1 compares the state AT the cap (band 1.0e-3, from the
    measured residual-state head-room) and R2 compares the geometric-extrapolated
    PLATEAU of each series (band 1.0e-4, from two MEASURED converged pairs).
    R2 is the limb that tests the property that matters.

SCOPE: this instrument reports convergence behaviour, measured y+, cost
arithmetic and the reproduction control.  It reports NO physics, NO band, and NO
stall angle.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# STATIC, PINNED INPUTS.  Neither is ever read from a run root.
# ---------------------------------------------------------------------------
FIXTURE_PATH = HERE / "a1wrt_fixture.log"
FIXTURE_MD5 = "4f6e870f74790af9238266c7cf10a0d2"

REFERENCE_PATH = HERE / "a1wr_alpha12_reference.tsv"
REFERENCE_MD5 = "26ce1af0b0e93af5b9f71efdc34446a4"

# ---------------------------------------------------------------------------
# REGISTERED CONSTANTS (PREREGISTRATION_DRAFT.md).  Changing one changes a gate.
# ---------------------------------------------------------------------------
ENDTIME_CAP = 4000          # frozen `endTime`, carried unchanged from A1WR
DECLARED_ALPHAS = [12, 13, 14, 15, 16, 17, 18]
CAP_CORE_MIN = 768.0        # section 4.4, = 3.00x the 256 estimate
RANKS = 1                   # np = 1, registered
YPLUS_THRESHOLD = 1.0       # G-YPLUS
R1_BAND = 1.0e-3            # G-REPRO limb R1, at the iteration cap
R2_BAND = 1.0e-4            # G-REPRO limb R2, on the extrapolated plateau
# G-PATCHPAIR (§3.5): U1's extrapolated plateau vs U2's EXTRAPOLATED PLATEAU,
# both through the identical frozen plateau() routine.  RE-ANCHORED 2026-09-03:
# the item now REGISTERS that the `empty` units are expected NOT to converge
# (§7), so an anchor on "U2's converged value" would have fired NOT A RESULT on
# the outcome the item predicts, and a gate cannot be anchored on the outcome
# its own registration expects.
# BANDS: supervisor's construction (dafoam-supervisor, 2026-09-03), DERIVED from
# the MEASURED +-4.9e-05 plateau-extrapolation sensitivity of §3.3, not itself
# measured.  A two-sided plateau-vs-plateau comparison carries that error on
# BOTH sides: 2 x (4.9e-05 + 4.9e-05) = 1.96e-4, rounded up to 2.0e-4.  The 10x
# ratio between the two bands is preserved from the pre-re-anchor form.
PATCHPAIR_NOISE = 2.0e-4    # <= this: the repair does not move the coefficients
PATCHPAIR_INDET = 2.0e-3    # <= this: INDETERMINATE; above: CONTAMINATION
# Registered per-unit caps (§4.4), each ~3x its own estimate.
# Caps are sized on the WORST REGISTERED OCCUPANCY (the measured 14-way
# saturation, 3.85915x solo), NOT on the quiet estimate -- the estimate stays a
# prediction and is reported per occupancy, the cap is protection.
CAP_CORE_MIN_U1 = 361.0
CAP_CORE_MIN_U2U3 = 2943.0
TMO_S_U1 = 21360
TMO_S_U2U3 = 176280
# The in-container deadline BELONGS TO A UNIT, not to the module.  Grading U1
# against TMO_S_U2U3 prints 176,280 s beside a cap of 361 core-min -- an 8.25x
# overstatement of that grading's own deadline, in a report a reader would take
# as authoritative.  The deadline is therefore selected from the unit being
# graded, and where the cap does not name a registered unit the reader prints
# that it cannot say, rather than a number that is true in another scope.
CAP_TO_TMO = {CAP_CORE_MIN_U1: TMO_S_U1, CAP_CORE_MIN_U2U3: TMO_S_U2U3}
CONTAMINATION = "CONTAMINATION"
INDETERMINATE = "INDETERMINATE"
NOISE = "NOISE"

CONVERGED = "CONVERGED"
NOT_CONVERGED = "NOT CONVERGED"
NOT_MEASURED = "NOT MEASURED"
PASS = "PASS"
GATE_FAIL = "GATE FAIL"
NOT_A_RESULT = "NOT A RESULT"
REFUSED = "REFUSED"

# ---------------------------------------------------------------------------
# READERS.  Every one of these is driven by the controls on real bytes.
# ---------------------------------------------------------------------------
CONV = re.compile(
    r"Minimal residual\s+([0-9.eE+-]+)\s+satisfied the prescribed tolerance\s+([0-9.eE+-]+)")
TIME = re.compile(r"^Time = (\d+)\s*$", re.M)
END = re.compile(r"^End\s*$", re.M)
CL_PAT = re.compile(r"^CL:\s*([-+0-9.eE]+)", re.M)
CD_PAT = re.compile(r"^CD:\s*([-+0-9.eE]+)", re.M)
YP_PAT = re.compile(
    r"^yPlus min:\s*([-+0-9.eE]+)\s+max:\s*([-+0-9.eE]+)\s+mean:\s*([-+0-9.eE]+)", re.M)
PT_BEGIN = re.compile(
    r"^AOA_POINT_BEGIN idx=(\d+) alpha=([-+0-9.]+) mode=(\S+) continued_from=(\S+) "
    r"after_exception=(\S+)\s*$", re.M)
PT_VALUES = re.compile(
    r"^AOA_POINT_VALUES idx=(\d+) alpha=([-+0-9.]+) CL=(\S+) CD=(\S+) "
    r"wall_s=([0-9.]+) err=(.*)$", re.M)
SOLDIR = re.compile(
    r"Mesh has (\d+) solution \(non-empty\) directions \(([01]) ([01]) ([01])\)")
WALL_GOOD = "BCType=nutLowReWallFunction"
WALL_BAD = "nutUSpaldingWallFunction"
# G-STALL: a stall/separation word bound to a NUMERIC ANGLE.  It must fire on a
# planted claim and must NOT fire on the honest caveat, which names no angle.
STALL_CLAIM = re.compile(
    r"(stall|stalls|stalling|separat\w+)[^.\n]{0,60}?"
    r"(-?\d+(?:\.\d+)?)\s*(deg|degree|degrees|°)", re.I)


class Refusal(Exception):
    """Raised where the honest answer is 'this reader cannot tell'."""


def segment(text: str) -> list[dict]:
    """Split a unit log into per-point segments, keyed on the BEGIN markers."""
    begins = list(PT_BEGIN.finditer(text))
    out = []
    for k, m in enumerate(begins):
        stop = begins[k + 1].start() if k + 1 < len(begins) else len(text)
        out.append({"idx": int(m.group(1)), "alpha_deg": float(m.group(2)),
                    "mode": m.group(3), "continued_from": m.group(4),
                    "after_exception": m.group(5), "text": text[m.start():stop]})
    return out


def classify(text: str, cap: int | None) -> dict:
    """Convergence verdict for one point.  A null is NOT MEASURED, never False."""
    times = [int(m.group(1)) for m in TIME.finditer(text)]
    last_time = times[-1] if times else None
    ended = bool(END.search(text))
    cm = None
    for m in CONV.finditer(text):
        cm = m
    achieved = float(cm.group(1)) if cm else None
    tol = float(cm.group(2)) if cm else None
    if cm is not None:
        verdict, why = CONVERGED, (
            "DAFoam's own statement: minimal residual %.6e satisfied the "
            "prescribed tolerance %.0e" % (achieved, tol))
    elif ended and cap is not None and last_time is not None and last_time >= cap:
        verdict, why = NOT_CONVERGED, (
            "ran to the endTime cap (%d >= %d) and emitted no tolerance-satisfied "
            "line: the iteration limit stopped it, not convergence" % (last_time, cap))
    else:
        verdict, why = NOT_MEASURED, (
            "no tolerance-satisfied line, and the log does not show the run reaching "
            "its endTime cap either -- this reader cannot tell whether the field "
            "converged, and says so rather than guessing")
    return {"verdict": verdict, "why": why, "achieved_min_residual": achieved,
            "prescribed_tolerance": tol, "last_time": last_time,
            "n_time_lines": len(times), "end_marker": ended}


def yplus_of(text: str):
    """LAST y+ print in the segment.  Exact to <= printInterval before the stop."""
    last = None
    for m in YP_PAT.finditer(text):
        last = m
    if last is None:
        return None
    return (float(last.group(1)), float(last.group(2)), float(last.group(3)))


def series_of(text: str) -> list[tuple[int, float, float]]:
    """(Time, CL, CD) print series for one point, in file order."""
    ts = [int(m.group(1)) for m in TIME.finditer(text)]
    cl = [float(m.group(1)) for m in CL_PAT.finditer(text)]
    cd = [float(m.group(1)) for m in CD_PAT.finditer(text)]
    n = min(len(ts), len(cl), len(cd))
    return list(zip(ts[:n], cl[:n], cd[:n]))


def plateau(values: list[float]) -> tuple[float | None, str]:
    """Geometric-sum extrapolation of a monotone decaying increment series.

    EXTRAPOLATED, and labelled so at every use.  Refuses rather than guessing
    when the increments are not decaying geometrically -- an extrapolation off a
    non-decaying tail is a number with no meaning, and returning one would be
    worse than returning nothing."""
    if len(values) < 4:
        return None, "fewer than 4 prints: no tail to extrapolate"
    inc = [values[i] - values[i - 1] for i in range(len(values) - 3, len(values))]
    if inc[-1] == 0.0 or inc[-2] == 0.0:
        return values[-1], "increments already zero: the series is at its plateau"
    r = inc[-1] / inc[-2]
    if not (0.0 < r < 1.0):
        return None, ("increment ratio %.6f is not in (0,1): the tail is not "
                      "decaying geometrically and NO plateau is quoted" % r)
    return values[-1] + inc[-1] * r / (1.0 - r), (
        "geometric sum, ratio %.6f, remaining %+.6e -- EXTRAPOLATED" % (r, inc[-1] * r / (1.0 - r)))


def read_reference(path: Path) -> list[tuple[int, float, float, float]]:
    rows = []
    for ln in path.read_text().splitlines():
        if not ln or ln.startswith("#") or ln.startswith("time\t"):
            continue
        a, b, c, d = ln.split("\t")
        rows.append((int(a), float(b), float(c), float(d)))
    return rows


def md5_of(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# G-FIXTURE -- the L-435 repair, enforced BY EXECUTION and not by intention
# ---------------------------------------------------------------------------
def g_fixture(run: Path | None) -> list[str]:
    out = ["G-FIXTURE (every control fixture STATIC, pinned, and independent of the graded run):"]
    for name, p, pin in (("control fixture", FIXTURE_PATH, FIXTURE_MD5),
                         ("reproduction reference", REFERENCE_PATH, REFERENCE_MD5)):
        if not p.is_file():
            raise Refusal("G-FIXTURE: %s missing at %s" % (name, p))
        got = md5_of(p)
        if got != pin:
            raise Refusal("G-FIXTURE: %s md5 %s != pinned %s -- the instrument is "
                          "not the one that was frozen" % (name, got, pin))
        if run is not None:
            rp, fp = run.resolve(), p.resolve()
            if fp == rp or rp in fp.parents:
                raise Refusal("G-FIXTURE: %s resolves INSIDE the run root being "
                              "graded (%s) -- that is the defect that voided "
                              "MAAOA's grading (L-435)" % (name, rp))
            if not run.exists():
                raise Refusal("G-FIXTURE: run root %s does not exist" % rp)
            if p.stat().st_mtime >= run.stat().st_mtime:
                raise Refusal("G-FIXTURE: mtime(%s) >= mtime(run root) -- a fixture "
                              "not older than the run it grades is not independent "
                              "of it" % name)
        out.append("  %-24s %s  md5 %s  sha256 %s" % (
            name, p, got, hashlib.sha256(p.read_bytes()).hexdigest()[:16] + "..."))
    out.append("  born against  : STATIC PINNED FIXTURE -- never an artefact of the graded run")
    if run is not None:
        out.append("  run root      : %s (mtime asserted NEWER than both fixtures)" % run.resolve())
    out.append("  PASS")
    return out


# ---------------------------------------------------------------------------
# G-COMPLETE -- registered in A1WR section 9, NEVER IMPLEMENTED THERE.  Here it is.
# ---------------------------------------------------------------------------
def g_complete(pts: list[dict], declared: list[int], rc, cap: int) -> tuple[str, list[str], list[str]]:
    """rule 4, all clauses.  REFUSES rather than degrading.

    THE DISTINCTION THE REGISTRATION TURNS ON, MADE EXPLICIT RATHER THAN LEFT
    TO THE READER'S DISCRETION:

      * a clause this reader CAN evaluate, which fails      -> GATE FAIL (a verdict)
      * a clause this reader CANNOT evaluate                -> REFUSE, exit 2

    The second limb is what "refuse rather than degrade" means.  An absent `rc`
    is the case that matters: rule 4 requires rc = 0, and a reader that reports
    `rc: absent` and then prints a verdict has quietly graded a run against a
    clause it never checked.  That is precisely the shape of the defect this
    instrument exists to not repeat, so it refuses instead."""
    notes, bad, cannot = [], [], []
    got = [p["alpha_deg"] for p in pts]
    notes.append("  declared points : %d %s" % (len(declared), declared))
    notes.append("  segments found  : %d %s" % (len(got), [("%g" % a) for a in got]))
    if len(got) != len(declared):
        bad.append("COUNT: %d declared, %d present -- the gap is NOT absorbed"
                   % (len(declared), len(got)))
    for p in pts:
        c = classify(p["text"], cap)
        if not c["end_marker"]:
            bad.append("alpha %g: no `End` line" % p["alpha_deg"])
        if c["last_time"] is None:
            bad.append("alpha %g: no `Time =` line at all" % p["alpha_deg"])
        elif c["verdict"] is NOT_CONVERGED and c["last_time"] != cap:
            bad.append("alpha %g: last time %s != endTime %d"
                       % (p["alpha_deg"], c["last_time"], cap))
        if yplus_of(p["text"]) is None and (c["last_time"] or 0) >= 200:
            bad.append("alpha %g: no y+ reading on a point that ran %s iterations"
                       % (p["alpha_deg"], c["last_time"]))
    if rc is None:
        cannot.append("no `rc` artefact under the unit's out/ -- rule 4 requires "
                      "rc = 0 and this reader cannot evaluate that clause. It "
                      "REFUSES rather than printing a verdict against a clause "
                      "it never checked.")
    elif rc != 0:
        bad.append("unit rc=%s (rule 4 requires rc = 0)" % rc)
    if not pts:
        cannot.append("no point segments at all -- nothing to evaluate rule 4 against")
    notes.append("  rc              : %s" % ("ABSENT -> REFUSAL" if rc is None else rc))
    return (PASS if not bad else GATE_FAIL), notes + ["  ! " + b for b in bad], cannot


# ---------------------------------------------------------------------------
# G-CAPS -- ARITHMETIC.  A1WR's reader had one prose sentence and computed nothing.
# ---------------------------------------------------------------------------
def g_caps(wall_s_total: float, cap_core_min: float, ranks: int,
           tmo_s: int | None = None) -> tuple[str, list[str]]:
    core_min = wall_s_total * ranks / 60.0
    frac = core_min / cap_core_min if cap_core_min else float("inf")
    dl = ("in-container deadline %d s" % tmo_s if tmo_s is not None else
          "in-container deadline NOT STATED: this cap names no registered unit, "
          "and a deadline true for another unit would be false here")
    lines = ["  measured wall   : %.4f s x %d rank(s) / 60 = %.4f core-min"
             % (wall_s_total, ranks, core_min),
             "  registered cap  : %.1f core-min  (%s)"
             % (cap_core_min, dl),
             "  consumed        : %.2f %% of cap" % (frac * 100.0),
             "  remaining       : %.4f core-min" % (cap_core_min - core_min),
             "  derived cost    : %.4f core-h x $0.0513 = $%.5f DERIVED, NOT MEASURED"
             % (core_min / 60.0, core_min / 60.0 * 0.0513)]
    if core_min > cap_core_min:
        lines.append("  ! OVERRUN: a cap-stop is NOT A RESULT on the unfinished points; "
                     "points already in the ledger stand.  No new budget is granted.")
        return NOT_A_RESULT, lines
    return PASS, lines


# ---------------------------------------------------------------------------
# G-REPRO -- two limbs, two separately anchored bands
# ---------------------------------------------------------------------------
def g_repro(cold_series, ref_rows) -> tuple[str, list[str]]:
    lines = []
    if not cold_series:
        return NOT_A_RESULT, ["  the cold alpha=12 point produced no series -- the "
                              "control's ABSENCE is reported, never papered over"]
    ref_cl = [r[1] for r in ref_rows]
    ref_cd = [r[2] for r in ref_rows]
    c_cl = [s[1] for s in cold_series]
    c_cd = [s[2] for s in cold_series]

    verdicts = []
    lines.append("  R1  at the iteration cap, band %.1e" % R1_BAND)
    for nm, a, b in (("CL", c_cl[-1], ref_cl[-1]), ("CD", c_cd[-1], ref_cd[-1])):
        rel = abs(a - b) / abs(b) if b else float("inf")
        ok = rel <= R1_BAND
        verdicts.append(ok)
        lines.append("        %s cold %.14g vs A1WR continued %.14g -> rel %.6e  %s"
                     % (nm, a, b, rel, "INSIDE" if ok else "OUTSIDE"))
    lines.append("  R2  extrapolated plateau, band %.1e" % R2_BAND)
    r2 = []
    for nm, cs, rs in (("CL", c_cl, ref_cl), ("CD", c_cd, ref_cd)):
        pa, na = plateau(cs)
        pb, nb = plateau(rs)
        if pa is None or pb is None:
            lines.append("        %s plateau NOT QUOTED -- cold: %s ; reference: %s"
                         % (nm, na, nb))
            r2.append(None)
            continue
        rel = abs(pa - pb) / abs(pb) if pb else float("inf")
        ok = rel <= R2_BAND
        r2.append(ok)
        lines.append("        %s cold %.14g (%s)" % (nm, pa, na))
        lines.append("        %s ref  %.14g (%s)" % (nm, pb, nb))
        lines.append("        %s -> rel %.6e  %s" % (nm, rel, "INSIDE" if ok else "OUTSIDE"))
    if any(x is None for x in r2):
        lines.append("  R2 could not be computed on every channel: NOT A RESULT on R2, "
                     "and the reader says so rather than substituting R1 for it.")
        return NOT_A_RESULT, lines
    if all(r2):
        if all(verdicts):
            lines.append("  -> CORROBORATED: the continuation label on A1WR's alpha<=12 "
                         "body was live, and this tail continues that body.")
            return PASS, lines
        lines.append("  -> R2 inside, R1 outside: the fixed points agree and the "
                     "iteration-4,000 states do not.  A statement about iterative "
                     "history at a fixed budget, NOT about the polar.  The tail stands.")
        return PASS, lines
    lines.append("  -> R2 OUTSIDE BAND: two starting states reach different plateaus on "
                 "the same mesh at the same alpha.  THE CONTINUED LABELS ON THIS TAIL "
                 "ARE WITHDRAWN and the successor is a diagnosis, not more points.")
    return GATE_FAIL, lines


# ---------------------------------------------------------------------------
# G-PATCH -- the patch identity ACTUALLY IN FORCE, from the solver's own line
# ---------------------------------------------------------------------------
def g_patch(text: str, expect_n: int) -> tuple[str, list[str]]:
    """The whole symmetry/empty defect reduced to one line the solver prints
    about itself.  `symmetry` bounding planes leave 3 solution directions and a
    z-momentum equation on a one-cell-thick mesh; `empty` leaves 2 and none.

    This reads what RAN.  It does not read the boundary file, because a boundary
    file is what somebody intended and this line is what the solver did."""
    m = None
    for m2 in SOLDIR.finditer(text):
        m = m2
    if m is None:
        raise Refusal("G-PATCH: the log carries no `Mesh has N solution "
                      "(non-empty) directions` line -- the patch identity that "
                      "actually ran cannot be read, so it is not asserted")
    n = int(m.group(1))
    dirs = (m.group(2), m.group(3), m.group(4))
    got = "%d (%s %s %s)" % (n, dirs[0], dirs[1], dirs[2])
    if n != expect_n:
        raise Refusal("G-PATCH: this unit is registered for %d solution "
                      "directions and the solver reports %s -- the patch "
                      "identity in force is not the registered one"
                      % (expect_n, got))
    return PASS, ["  solver reports  : Mesh has %s solution directions" % got,
                  "  registered      : %d  (%s)" % (
                      expect_n, "symmetry" if expect_n == 3 else "empty"),
                  "  PASS"]


# ---------------------------------------------------------------------------
# G-PATCHPAIR -- symmetry vs empty, one variable, thresholds from measurement
# ---------------------------------------------------------------------------
def g_patchpair(u1_series, u2_series) -> tuple[str, list[str]]:
    """U1's EXTRAPOLATED PLATEAU against U2's EXTRAPOLATED PLATEAU.

    PLATEAU AGAINST PLATEAU, both through THIS identical frozen routine, so the
    two sides are the same kind of estimate of the same kind of quantity.

    Not the two values at iteration 4,000: U1 stops at the cap still drifting,
    so a cap-vs-cap comparison would fold U1's own residual-state head-room into
    the answer and call it contamination.

    And NOT U2's converged value either.  RE-ANCHORED 2026-09-03: §7 registers
    that the `empty` units are expected NOT to converge, because `primalMaxRes`
    never contained U2 to begin with.  An anchor on "U2's converged value" makes
    this gate return NOT A RESULT on the very outcome the item predicts -- the
    gate would be unfirable by its own registration.  A plateau is available
    from a drifting series and from a converged one alike, so this form returns
    a real verdict on BOTH outcomes.

    The denominator is U2's plateau: the `empty` configuration is the repaired
    one and is the reference the comparison is against."""
    lines, worst, verdicts = [], 0.0, []
    if not u1_series or not u2_series:
        return NOT_A_RESULT, ["  one side of the pair is absent -- reported, "
                              "never papered over"]
    for k, nm in ((1, "CL"), (2, "CD")):
        u1 = [s[k] for s in u1_series]
        u2 = [s[k] for s in u2_series]
        pa, note = plateau(u1)
        vb, noteb = plateau(u2)
        if pa is None or vb is None:
            lines.append("  %s NOT QUOTED -- U1: %s ; U2: %s" % (nm, note, noteb))
            verdicts.append(None)
            continue
        rel = abs(pa - vb) / abs(vb) if vb else float("inf")
        worst = max(worst, rel)
        lines.append("  %s  U1 symmetry plateau %.14g (%s)" % (nm, pa, note))
        lines.append("  %s  U2 empty    plateau %.14g (%s)" % (nm, vb, noteb))
        lines.append("  %s  -> rel %.6e" % (nm, rel))
        verdicts.append(rel)
    if any(v is None for v in verdicts):
        lines.append("  a channel could not be compared: NOT A RESULT on G-PATCHPAIR")
        return NOT_A_RESULT, lines
    if worst <= PATCHPAIR_NOISE:
        lines.append("  -> NOISE (worst %.3e <= %.1e): the patch repair does not "
                     "move the coefficients." % (worst, PATCHPAIR_NOISE))
        return NOISE, lines
    if worst <= PATCHPAIR_INDET:
        lines.append("  -> INDETERMINATE (%.3e): between the extrapolation's own "
                     "error and the residual-state head-room. Reported; neither "
                     "cleared nor called contamination." % worst)
        return INDETERMINATE, lines
    lines.append("  -> CONTAMINATION (%.3e > %.1e), AND IT IS THE FINDING. It is "
                 "%.1fx the MEASURED residual-state head-room of 1.947e-04, so "
                 "larger than any iteration-state effect can explain. Its reach "
                 "is every incompressible number this ladder has produced on a "
                 "symmetry-bounded 2-D mesh." % (worst, PATCHPAIR_INDET,
                                                 worst / 1.947e-04))
    return CONTAMINATION, lines


# ---------------------------------------------------------------------------
# CONTROLS.  Static fixture only.  Read -> mutate -> ASSERT LANDED -> real
# reader -> assert flip -> restore -> assert restore.
# ---------------------------------------------------------------------------
def _one(text: str, cap: int = ENDTIME_CAP) -> dict:
    segs = segment(text)
    if len(segs) != 1:
        raise SystemExit("CONTROL HARNESS BROKEN: %d segments, expected 1" % len(segs))
    return classify(segs[0]["text"], cap)


def selftest(run: Path | None) -> tuple[list[str], list[str]]:
    global CONV, YP_PAT, END, SOLDIR
    out, fails = [], []
    n = [0]

    def chk(tag, ok, desc, detail=""):
        n[0] += 1
        out.append("  %-5s %-56s %s" % (tag[0] + " " + tag[1], desc, "PASS" if ok else "FAIL"))
        if detail:
            out.append("         " + detail)
        if not ok:
            fails.append("%s %s" % (tag[0], desc))

    out.extend(g_fixture(run))
    out.append("")
    out.append("PLANTED CONTROLS -- driven through the REAL reader functions, BOTH DIRECTIONS.")

    base_all = FIXTURE_PATH.read_text()
    segs = segment(base_all)
    base = segs[0]["text"]          # idx 0, alpha 12, COLD, converged
    capped = segs[2]["text"]        # idx 2, alpha 14, ran to the cap
    out.append("  base segment  : fixture idx=0 alpha=12.0 COLD (STATIC)")
    out.append("  sha256 of base: %s" % hashlib.sha256(base.encode()).hexdigest())

    def mutate(tag, before, after):
        """A no-op mutation followed by a passing check is a control that proves
        nothing.  Refuse if the bytes did not actually change."""
        if before == after:
            raise SystemExit("CONTROL %s DID NOT LAND: the mutation left the bytes "
                             "unchanged, so anything it 'proves' is worthless" % tag)
        return after

    # ---- F: G-FIXTURE itself -------------------------------------------------
    tmp = FIXTURE_PATH.read_bytes()
    st0 = FIXTURE_PATH.stat()          # mtime is READ BY A GATE, so it is state too
    try:
        FIXTURE_PATH.write_bytes(mutate("F1", tmp, tmp + b"\n# planted\n"))
        assert md5_of(FIXTURE_PATH) != FIXTURE_MD5
        try:
            g_fixture(run)
            got = "NOT REFUSED"
        except Refusal:
            got = "REFUSED"
        chk(("F1", "[-]"), got == "REFUSED",
            "a mutated fixture is REFUSED by its own md5 pin",
            "an unpinned fixture is a fixture anybody can move; got %s" % got)
    finally:
        FIXTURE_PATH.write_bytes(tmp)
        # RESTORE THE mtime TOO.  Found the hard way: restoring only the BYTES
        # left the fixture newer than every run root, and G-FIXTURE's own mtime
        # assert then refused every subsequent grading -- the control breaking
        # the gate it was written to protect.  A control must leave the artefact
        # byte-identical AND stat-identical whenever a gate reads stat.
        os.utime(FIXTURE_PATH, (st0.st_atime, st0.st_mtime))
    chk(("F1b", "[!]"), md5_of(FIXTURE_PATH) == FIXTURE_MD5
        and FIXTURE_PATH.stat().st_mtime == st0.st_mtime,
        "restore landed -- BYTES AND mtime -- and was re-asserted",
        "a control that does not restore corrupts the next run; mtime is state "
        "here because G-FIXTURE reads it")

    # F2 must fire on the PATH, not on the file being absent.  A control that
    # refuses because the fixture is missing has not tested the path check at
    # all -- it would pass against a reader with no path check whatsoever.  So
    # a REAL fixture is planted inside the run root and the refusal message is
    # asserted to name the run root.
    if run is not None:
        saved = FIXTURE_PATH
        planted = run / "planted_fixture_inside_run_root.log"
        try:
            planted.write_bytes(FIXTURE_PATH.read_bytes())
            assert planted.is_file() and md5_of(planted) == FIXTURE_MD5, \
                "CONTROL F2 DID NOT LAND: the planted fixture is not a real, " \
                "pinned-matching file, so a refusal would prove nothing"
            globals()["FIXTURE_PATH"] = planted
            reason = ""
            try:
                g_fixture(run)
                got = "NOT REFUSED"
            except Refusal as exc:
                got, reason = "REFUSED", str(exc)
            chk(("F2", "[-]"), got == "REFUSED" and "INSIDE the run root" in reason,
                "a REAL, pin-matching fixture INSIDE the run root is REFUSED",
                "refused on the PATH, not on absence -- this is the exact L-435 "
                "defect; got %s: %s" % (got, reason[:90]))
        finally:
            globals()["FIXTURE_PATH"] = saved
            if planted.exists():
                planted.unlink()
        chk(("F2b", "[!]"), not planted.exists() and md5_of(FIXTURE_PATH) == FIXTURE_MD5,
            "F2's plant was removed and the real fixture is untouched",
            "a control that leaves its plant behind poisons the next run")
    else:
        out.append("  F2    [-] fixture-inside-run-root control  SKIPPED (no run root supplied)")

    # ---- C: convergence channel ---------------------------------------------
    r1 = _one(base)
    chk(("C1", "[+]"), r1["verdict"] == CONVERGED,
        "unmodified artefact -> CONVERGED",
        "read off the bytes: %s, min residual %s" % (r1["verdict"], r1["achieved_min_residual"]))

    SENT = "1.234567e-09"
    b2 = mutate("C2", base, CONV.sub(
        "Minimal residual %s satisfied the prescribed tolerance 1e-08" % SENT, base))
    r2 = _one(b2)
    chk(("C2", "[+]"), str(r2["achieved_min_residual"]) == str(float(SENT)),
        "SENTINEL %s planted -> reader reports it" % SENT,
        "a value in no real log: seeing it proves the read is off the bytes, got %s"
        % r2["achieved_min_residual"])

    r3 = classify(capped, ENDTIME_CAP)
    chk(("C3", "[-]"), r3["verdict"] == NOT_CONVERGED,
        "ran to the cap, no tolerance line -> NOT CONVERGED",
        "last_time %s >= cap %d; got %s" % (r3["last_time"], ENDTIME_CAP, r3["verdict"]))

    b4 = mutate("C4", base, CONV.sub("", base)[: len(base) // 2])
    r4 = _one(b4) if len(segment(b4)) == 1 else {"verdict": NOT_MEASURED}
    chk(("C4", "[-]"), r4["verdict"] == NOT_MEASURED,
        "truncated mid-solve -> NOT MEASURED",
        "a null is NOT MEASURED, never False; got %s" % r4["verdict"])

    keep = CONV
    CONV = re.compile(r"(?!x)x_matches_nothing_([0-9])([0-9])")
    try:
        r5 = _one(base)
    finally:
        CONV = keep
    chk(("C5", "[!]"), r5["verdict"] != CONVERGED,
        "CONV disabled -> C1 must flip",
        "a control that passes against a broken reader is not a control; flipped to %s"
        % r5["verdict"])

    # ---- G: healthy lines that have been misread as crashes before -----------
    g1 = _one(base + "\nSigFpe : Enabling floating point exception trapping\n")
    chk(("G1", "[!]"), g1["verdict"] == CONVERGED,
        "SigFpe startup banner -> still CONVERGED",
        "a STARTUP NOTICE, read as a crash twice in this family (L-312)")
    g2 = _one(base + "\n" + "\n".join(
        "Time step continuity errors : sum local = 1e-09" for _ in range(10)))
    chk(("G2", "[!]"), g2["verdict"] == CONVERGED,
        "10 lines containing 'errors' -> still CONVERGED",
        "'continuity errors' is a HEALTHY line, in every real log here")

    # ---- Y: the y+ channel ---------------------------------------------------
    y1 = yplus_of(base)
    chk(("Y1", "[+]"), y1 is not None and y1[1] < YPLUS_THRESHOLD,
        "y+ line present -> parsed, below threshold",
        "read %s" % (y1,))
    b6 = mutate("Y2", base, YP_PAT.sub(
        "yPlus min: 0.01 max: 2.345 mean: 0.5", base))
    y2 = yplus_of(b6)
    chk(("Y2", "[-]"), y2 is not None and y2[1] >= YPLUS_THRESHOLD,
        "planted y+max 2.345 -> above threshold, GATE FAIL",
        "the wall-resolved claim is WITHDRAWN for such a point (section 3.4); got %s" % (y2,))
    b7 = mutate("Y3", base, YP_PAT.sub("", base))
    chk(("Y3", "[-]"), yplus_of(b7) is None,
        "y+ line removed -> channel reads BLIND, refusal path",
        "a blind channel is refused, not passed")
    keepy = YP_PAT
    YP_PAT = re.compile(r"(?!x)x_matches_nothing")
    try:
        y4 = yplus_of(base)
    finally:
        YP_PAT = keepy
    chk(("Y4", "[!]"), y4 is None,
        "YP_PAT disabled -> Y1 would flip",
        "the mutation control on the y+ reader itself")

    # ---- W: G-WALLTREAT ------------------------------------------------------
    chk(("W1", "[+]"), WALL_GOOD in base and WALL_BAD not in base,
        "the low-Re BC line is present and the Spalding line is not",
        "no false alarm on a clean artefact")
    b8 = mutate("W2", base, base.replace(WALL_GOOD, "BCType=" + WALL_BAD))
    chk(("W2", "[-]"), WALL_BAD in b8 and WALL_GOOD not in b8,
        "planted Spalding line -> G-WALLTREAT must refuse",
        "mutation landed and the BAD token is what the check scans for")

    # ---- X: G-PATCH, the patch identity actually in force --------------------
    v, _ = g_patch(base_all, 3)
    chk(("X1", "[+]"), v == PASS,
        "fixture prints 3 solution directions -> PASS as a symmetry unit",
        "got %s" % v)
    try:
        g_patch(base_all, 2)
        got = "NOT REFUSED"
    except Refusal:
        got = "REFUSED"
    chk(("X2", "[-]"), got == "REFUSED",
        "3 directions against a unit registered for 2 -> REFUSE",
        "the registered identity and the one in force disagree; got %s" % got)
    bx = mutate("X3", base_all, SOLDIR.sub("", base_all))
    try:
        g_patch(bx, 3)
        got = "NOT REFUSED"
    except Refusal:
        got = "REFUSED"
    chk(("X3", "[-]"), got == "REFUSED",
        "directions line REMOVED -> REFUSE, never assumed",
        "a patch identity that cannot be read is not asserted; got %s" % got)
    by = mutate("X5", base_all, base_all.replace(
        "Mesh has 3 solution (non-empty) directions (1 1 1)",
        "Mesh has 2 solution (non-empty) directions (1 1 0)"))
    v, _ = g_patch(by, 2)
    chk(("X5", "[+]"), v == PASS,
        "planted `2 (1 1 0)` -> PASS as an empty unit",
        "the mutation landed and the empty branch reads it; got %s" % v)
    keepd = SOLDIR
    SOLDIR = re.compile(r"(?!x)x_matches_nothing_(\d)(\d)(\d)(\d)")
    try:
        try:
            g_patch(base_all, 3)
            got = "NOT REFUSED"
        except Refusal:
            got = "REFUSED"
    finally:
        SOLDIR = keepd
    chk(("X4", "[!]"), got == "REFUSED",
        "SOLDIR disabled -> X1 must flip",
        "the mutation control on the patch-identity reader itself")

    # ---- Q: G-PATCHPAIR, symmetry vs empty ----------------------------------
    # RE-ANCHORED with the gate (§3.5): both sides are now SERIES, and both go
    # through the same plateau() routine.  plateau() is homogeneous of degree 1
    # under a uniform scaling of the series -- the ratio r is scale-invariant
    # and values[-1] and inc[-1] scale linearly -- so scaling a whole series by
    # (1+x) moves its plateau by exactly (1+x), and the planted shift is EXACT
    # rather than approximate.  Q4 asserts that the gate still returns a verdict
    # when U2 does NOT converge, which is the outcome the item PREDICTS.
    ref_rows = read_reference(REFERENCE_PATH)
    u1 = [(r[0], r[1], r[2]) for r in ref_rows]
    u2_same = [(r[0], r[1], r[2]) for r in ref_rows]
    v, _ = g_patchpair(u1, u2_same)
    chk(("Q1", "[+]"), v == NOISE,
        "U2's plateau identical to U1's -> NOISE",
        "no false alarm on a clean pair; got %s" % v)
    u2_hi = [(r[0], r[1] * (1 + 5e-3), r[2]) for r in ref_rows]
    if [x[1] for x in u2_hi] == [x[1] for x in u2_same]:
        raise SystemExit("CONTROL Q2 DID NOT LAND")
    v, _ = g_patchpair(u1, u2_hi)
    chk(("Q2", "[-]"), v == CONTAMINATION,
        "U2's series shifted 5.0e-3 -> CONTAMINATION",
        "2.5x the INDETERMINATE ceiling of %.1e; the falsifier is registered; "
        "got %s" % (PATCHPAIR_INDET, v))
    u2_mid = [(r[0], r[1] * (1 + 5e-4), r[2]) for r in ref_rows]
    if [x[1] for x in u2_mid] == [x[1] for x in u2_same]:
        raise SystemExit("CONTROL Q3 DID NOT LAND")
    v, _ = g_patchpair(u1, u2_mid)
    chk(("Q3", "[!]"), v == INDETERMINATE,
        "U2's series shifted 5.0e-4 -> INDETERMINATE, not silently cleared",
        "2.5x the NOISE band of %.1e and 0.25x the INDETERMINATE ceiling: the "
        "middle band exists so an ambiguous answer is not rounded to a verdict; "
        "got %s" % (PATCHPAIR_NOISE, v))
    # Q4: THE OUTCOME THIS ITEM PREDICTS.  A U2 series that is still drifting at
    # the cap -- i.e. NOT CONVERGED -- must still produce a verdict, because §7
    # registers non-convergence of the `empty` units as the EXPECTED outcome.
    # Under the pre-2026-09-03 anchor this case returned NOT A RESULT.
    v, _ = g_patchpair(u1, [(r[0], r[1], r[2]) for r in ref_rows])
    chk(("Q4", "[!]"), v in (NOISE, INDETERMINATE, CONTAMINATION),
        "a NON-CONVERGED U2 (a drifting series, the PREDICTED outcome) still "
        "yields a verdict, not NOT A RESULT",
        "a gate anchored on the outcome its own registration expects is "
        "unfirable; got %s" % v)

    # ---- K: G-COMPLETE, the gate A1WR registered and never wrote -------------
    full = segment(base_all)
    v, _, cn0 = g_complete(full, [12, 13, 14], 0, ENDTIME_CAP)
    chk(("K1", "[+]"), v == PASS,
        "complete 3-point fixture, rc 0 -> G-COMPLETE PASS",
        "got %s" % v)
    v, _, _ = g_complete(full, DECLARED_ALPHAS, 0, ENDTIME_CAP)
    chk(("K2", "[-]"), v == GATE_FAIL,
        "3 present against 7 declared -> G-COMPLETE GATE FAIL",
        "a polar short of its declared points is truncated; got %s" % v)
    v, _, _ = g_complete(full, [12, 13, 14], 97, ENDTIME_CAP)
    chk(("K3", "[-]"), v == GATE_FAIL,
        "rc=97 -> G-COMPLETE GATE FAIL on rule 4's rc clause",
        "got %s" % v)
    keepe = END
    END = re.compile(r"(?!x)x_matches_nothing", re.M)
    try:
        v, _, _ = g_complete(full, [12, 13, 14], 0, ENDTIME_CAP)
    finally:
        END = keepe
    chk(("K4", "[!]"), v == GATE_FAIL,
        "END disabled -> K1 must flip",
        "the mutation control on the End-marker reader; got %s" % v)
    _, _, cn = g_complete(full, [12, 13, 14], None, ENDTIME_CAP)
    chk(("K5", "[-]"), len(cn) == 1 and "rc" in cn[0] and len(cn0) == 0,
        "rc ABSENT -> G-COMPLETE REFUSES, it does not print a verdict",
        "refuse rather than degrade: a clause never checked is not a clause passed")

    # ---- P: G-CAPS as arithmetic --------------------------------------------
    v, _ = g_caps(CAP_CORE_MIN * 60 * 0.5, CAP_CORE_MIN, RANKS)
    chk(("P1", "[+]"), v == PASS, "spend at 50 % of cap -> G-CAPS PASS", "got %s" % v)
    v, _ = g_caps(CAP_CORE_MIN * 60 * 1.01, CAP_CORE_MIN, RANKS)
    chk(("P2", "[-]"), v == NOT_A_RESULT,
        "spend at 101 % of cap -> G-CAPS NOT A RESULT",
        "an overrun stops the run; it does not get a new budget; got %s" % v)

    # ---- R: G-REPRO, both limbs ---------------------------------------------
    ref = read_reference(REFERENCE_PATH)
    ident = [(t, cl, cd) for t, cl, cd, _ in ref]
    v, _ = g_repro(ident, ref)
    chk(("R1", "[+]"), v == PASS,
        "a series identical to the reference -> CORROBORATED",
        "no false alarm; got %s" % v)
    shifted = [(t, cl * (1 + 5 * R1_BAND), cd) for t, cl, cd in ident]
    if shifted == ident:
        raise SystemExit("CONTROL R2 DID NOT LAND")
    v, _ = g_repro(shifted, ref)
    chk(("R2", "[-]"), v in (GATE_FAIL, NOT_A_RESULT),
        "CL shifted 5x the R1 band -> G-REPRO fires",
        "the falsifier is registered in advance; got %s" % v)
    p, note = plateau([r[1] for r in ref])
    chk(("R3", "[+]"), p is not None and abs(p - ref[-1][1]) > 0,
        "plateau extrapolation returns a value below the last print",
        "%.14g (%s)" % (p, note) if p is not None else note)
    p2, note2 = plateau([1.0, 2.0, 3.0, 4.0])
    chk(("R4", "[-]"), p2 is None,
        "a NON-decaying series -> plateau REFUSED, not guessed",
        note2)

    # ---- S: G-STALL ----------------------------------------------------------
    chk(("S1", "[!]"), bool(STALL_CLAIM.search("the section stalls at 15.0 deg")),
        "G-STALL fires on a planted stall-angle claim",
        "fail-closed: a successor adding a stall limb stops publication")
    chk(("S2", "[-]"), not STALL_CLAIM.search(
        "A non-converged point is evidence that the steady solver stopped "
        "converging. It is not evidence of separation."),
        "G-STALL does NOT fire on the honest caveat",
        "a guard that fires on everything would be turned off")

    out.append("")
    out.append("SELFTEST %s: %d controls, both directions, mutation controls included."
               % ("PASS" if not fails else "FAIL", n[0]))
    return out, fails


# ---------------------------------------------------------------------------
def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        # A synthetic run root, so F2 and the mtime assert are DRIVEN rather
        # than skipped.  A control that is skipped in the only mode anybody
        # runs before a freeze is a control that does not exist.
        import tempfile
        with tempfile.TemporaryDirectory(prefix="a1wrt_selftest_") as td:
            try:
                st, fails = selftest(Path(td))
            except Refusal as exc:
                sys.stderr.write("REFUSED: %s\n" % exc)
                return 2
        sys.stdout.write("\n".join(st) + "\n")
        return 0 if not fails else 2

    if len(argv) < 2:
        sys.stderr.write("usage: a1wrt_read.py <RUN_DIR (.../A1WRT/TAIL1)> [--cap-core-min N]\n"
                         "       a1wrt_read.py --selftest\n")
        return 2
    run = Path(argv[1])
    cap_cm = CAP_CORE_MIN_U2U3
    tmo_s = TMO_S_U2U3
    if "--cap-core-min" in argv:
        cap_cm = float(argv[argv.index("--cap-core-min") + 1])
        # The deadline follows the unit the cap names.  An unregistered cap gets
        # NO deadline printed rather than another unit's.
        tmo_s = CAP_TO_TMO.get(cap_cm)

    lines = ["=" * 78,
             "A1WRT WALL-RESOLVED ALPHA-TAIL READER -- FEASIBILITY READINGS, NOT VERDICTS",
             "run dir: %s" % run, "=" * 78, ""]
    try:
        st, fails = selftest(run)
    except Refusal as exc:
        sys.stdout.write("\n".join(lines) + "\n")
        sys.stderr.write("\nREFUSED (exit 2): %s\n" % exc)
        return 2
    lines.extend(st)
    if fails:
        sys.stdout.write("\n".join(lines) + "\n")
        sys.stderr.write("\nREFUSED (exit 2): the reader failed its own controls, so no "
                         "reading from the real logs would be evidence (rule 3): %s\n"
                         % "; ".join(fails))
        return 2
    lines.append("")

    # Registered unit layout (§2.1): U1 is its own case tree on `symmetry`;
    # U2+U3 are ONE process on `empty`.
    UNITS = [("alpha12_symmetry", 3, CAP_CORE_MIN_U1, [12]),
             ("tail_empty", 2, CAP_CORE_MIN_U2U3, [12, 13, 14, 15, 16, 17, 18])]
    missing = [u for u, _, _, _ in UNITS
               if not (run / u / "out" / "sweep.log").is_file()]
    if missing:
        lines.append("UNIT LOG(S) ABSENT: %s" % ", ".join(missing))
        lines.append("PENDING: the item has not produced every unit's log.")
        sys.stdout.write("\n".join(lines) + "\n")
        return 0

    # ---- G-PATCH, per unit, BEFORE anything is read off the numbers -------
    lines.append("G-PATCH (the patch identity ACTUALLY IN FORCE, from the solver's own line):")
    for unit, expect_n, _, _ in UNITS:
        txt = (run / unit / "out" / "sweep.log").read_text(errors="replace")
        try:
            _, pn = g_patch(txt, expect_n)
        except Refusal as exc:
            sys.stdout.write("\n".join(lines) + "\n")
            sys.stderr.write("\nG-PATCH REFUSE (exit 2) on %s: %s\n" % (unit, exc))
            return 2
        lines.append("  [%s]" % unit)
        lines.extend("  " + x for x in pn)
    lines.append("")

    log = run / "tail_empty" / "out" / "sweep.log"
    u1_log = run / "alpha12_symmetry" / "out" / "sweep.log"
    text = log.read_text(errors="replace")
    pts = segment(text)

    # --- G-WALLTREAT ------------------------------------------------------
    if WALL_BAD in text or WALL_GOOD not in text:
        sys.stdout.write("\n".join(lines) + "\n")
        sys.stderr.write("\nG-WALLTREAT REFUSE (exit 2): the log does not confirm "
                         "%s, or carries %s\n" % (WALL_GOOD, WALL_BAD))
        return 2
    lines.append("G-WALLTREAT: PASS -- %s confirmed in the log that actually ran, "
                 "Spalding line absent" % WALL_GOOD)
    lines.append("")

    # --- the table --------------------------------------------------------
    rc_path = run / "tail_empty" / "out" / "rc"
    rc = int(rc_path.read_text().strip()) if rc_path.is_file() else None
    lines.append("THE TAIL -- cold alpha=12 then the continuation, wall-resolved L3")
    lines.append("    idx   alpha    convergence           CL           CD   iters     y+max  mode")
    lines.append("  " + "-" * 92)
    yp_refused, wall_total, cold_series = [], 0.0, []
    rows = []
    for p in pts:
        c = classify(p["text"], ENDTIME_CAP)
        yp = yplus_of(p["text"])
        if yp is None and (c["last_time"] or 0) >= 200:
            yp_refused.append(p)
        mv = PT_VALUES.search(p["text"])
        cl = cd = "NA"
        if mv:
            cl, cd = mv.group(3), mv.group(4)
            try:
                wall_total += float(mv.group(5))
            except ValueError:
                pass
        if p["mode"] == "COLD" and abs(p["alpha_deg"] - 12.0) < 1e-9:
            cold_series = series_of(p["text"])
        lines.append("  %5d %7.2f  %13s %12s %12s %7s %9s  %s" % (
            p["idx"], p["alpha_deg"], c["verdict"], cl[:12], cd[:12],
            c["last_time"], ("%.4f" % yp[1]) if yp else "BLIND", p["mode"]))
        rows.append({"idx": p["idx"], "alpha_deg": p["alpha_deg"], "mode": p["mode"],
                     "continued_from": p["continued_from"], "CL": cl, "CD": cd,
                     "convergence": c["verdict"], "why": c["why"],
                     "last_time": c["last_time"],
                     "yplus": {"min": yp[0], "max": yp[1], "mean": yp[2]} if yp else None})
    lines.append("")
    lines.append("  y+ channel: DAFoam's own per-print `yPlus min/max/mean` line, the LAST")
    lines.append("  in each point's segment -- exact to <= printInterval (100) iterations")
    lines.append("  before the point stopped.")
    lines.append("")

    # --- G-YPLUS ----------------------------------------------------------
    over = [(p["alpha_deg"], yplus_of(p["text"])[1]) for p in pts
            if yplus_of(p["text"]) and yplus_of(p["text"])[1] >= YPLUS_THRESHOLD]
    if over:
        lines.append("G-YPLUS: GATE FAIL -- y+max >= %.1f at: %s. THE WALL-RESOLVED CLAIM IS"
                     % (YPLUS_THRESHOLD, ", ".join("alpha %g (%.4f)" % o for o in over)))
        lines.append("  WITHDRAWN FOR THOSE POINTS (section 3.4). The mesh is NOT re-cut.")
    else:
        worst = max((yplus_of(p["text"])[1] for p in pts if yplus_of(p["text"])), default=None)
        lines.append("G-YPLUS: PASS on every measured point; worst y+max %s < %.1f"
                     % (("%.4f" % worst) if worst is not None else "NONE", YPLUS_THRESHOLD))
    lines.append("")

    # --- G-COMPLETE (implemented) ----------------------------------------
    vc, cn, cannot = g_complete(pts, DECLARED_ALPHAS, rc, ENDTIME_CAP)
    lines.append("G-COMPLETE (rule 4, all clauses; a clause that CANNOT be evaluated")
    lines.append("  is a REFUSAL, not a verdict):")
    lines.extend(cn)
    if cannot:
        lines.append("  REFUSED")
        sys.stdout.write("\n".join(lines) + "\n")
        sys.stderr.write("\nG-COMPLETE REFUSE (exit 2): %s\n" % " | ".join(cannot))
        return 2
    lines.append("  %s" % vc)
    lines.append("")

    # --- G-CAPS (arithmetic) ---------------------------------------------
    vp, pn = g_caps(wall_total, cap_cm, RANKS, tmo_s)
    lines.append("G-CAPS (ARITHMETIC, not prose):")
    lines.extend(pn)
    lines.append("  %s" % vp)
    lines.append("")

    # --- G-REPRO ----------------------------------------------------------
    # G-REPRO reads U1 -- A1WR's OWN configuration, `symmetry`, cold -- because
    # the cold-vs-continued comparison is only valid against it.  Reading it off
    # the `empty` tail would move two variables at once.
    u1_pts = segment(u1_log.read_text(errors="replace"))
    u1_cold = next((series_of(q["text"]) for q in u1_pts
                    if q["mode"] == "COLD" and abs(q["alpha_deg"] - 12.0) < 1e-9), [])
    lines.append("G-REPRO (section 3 -- cold-vs-continued, on U1 `symmetry`, both limbs):")
    vr, rn = g_repro(u1_cold, read_reference(REFERENCE_PATH))
    lines.extend(rn)
    lines.append("  %s" % vr)
    lines.append("")

    # G-PATCHPAIR reads U1's EXTRAPOLATED PLATEAU against U2's EXTRAPOLATED
    # PLATEAU, both through the identical frozen plateau() routine.
    # RE-ANCHORED 2026-09-03: the previous form compared U1's plateau against
    # U2's CONVERGED value and nulled the pair when U2 did not converge -- and
    # §7 registers NON-convergence of the `empty` units as the EXPECTED outcome,
    # so that form returned NOT A RESULT on this item's own prediction.  U2's
    # convergence state is still READ and REPORTED here; it no longer decides
    # whether the gate can fire.
    u2_series, u2_conv = [], None
    for q in pts:
        if q["mode"] == "COLD" and abs(q["alpha_deg"] - 12.0) < 1e-9:
            u2_series = series_of(q["text"])
            u2_conv = classify(q["text"], ENDTIME_CAP)["verdict"]
    lines.append("G-PATCHPAIR (section 3.5 -- `symmetry` vs `empty`, one variable,")
    lines.append("  PLATEAU vs PLATEAU, both EXTRAPOLATED by the same frozen routine):")
    if u2_conv is not None:
        lines.append("  U2 alpha=12 convergence state: %s%s" % (
            u2_conv,
            "  (the outcome section 7 REGISTERS as expected; it does not "
            "disable this gate)" if u2_conv != CONVERGED else
            "  (NOT the outcome section 7 predicts -- a finding about the "
            "coupling, reported as one)"))
    vq, qn = g_patchpair(u1_cold, u2_series)
    lines.extend(qn)
    lines.append("  %s" % vq)
    lines.append("")

    # --- non-converged points, reported not removed ------------------------
    nc = [p for p in pts if classify(p["text"], ENDTIME_CAP)["verdict"] != CONVERGED]
    if nc:
        lines.append("POINTS THAT DID NOT CONVERGE -- REPORTED, NOT REMOVED, NOT RETRIED")
        for p in nc:
            lines.append("  alpha %.2f deg: %s" % (
                p["alpha_deg"], classify(p["text"], ENDTIME_CAP)["why"]))
        lines.append("  IT MEANS the steady solver did not reach tolerance within the cap")
        lines.append("  at that operating point. IT DOES NOT MEAN the section separated")
        lines.append("  there: solver behaviour is measured, flow physics is not inferred.")
        lines.append("")

    # --- G-NOBAND ---------------------------------------------------------
    lines.append("SCOPE (G-NOBAND). FEASIBILITY: this mesh family's own grid convergence is")
    lines.append("PENDING -- NO value above is grid-converged, NO value carries a band, and")
    lines.append("the item's verdict ceiling is GATE REACHED.")
    lines.append("2-D steady RANS with SA past the onset of significant separation is not a")
    lines.append("valid model of the flow at ANY resolution: convergence and correctness")
    lines.append("remain independent claims and only the first is measured here.")

    report = "\n".join(lines) + "\n"

    # --- G-STALL, on this reader's OWN output ------------------------------
    hit = STALL_CLAIM.search(report)
    if hit:
        sys.stdout.write(report)
        sys.stderr.write("\nG-STALL REFUSE (exit 2): output binds a stall word to an "
                         "angle: %r\n" % hit.group(0))
        return 2
    sys.stdout.write(report)
    sys.stdout.write("G-STALL PASS: no stall/separation claim bound to an angle in this output.\n")

    if yp_refused:
        sys.stderr.write("\nG-YPLUS REFUSE (exit 2): blind y+ channel on: %s\n"
                         % ", ".join("alpha %.1f" % p["alpha_deg"] for p in yp_refused))
        return 2

    (run / "A1WRT_POINTS.json").write_text(json.dumps(
        {"points": rows, "declared": DECLARED_ALPHAS, "endtime_cap": ENDTIME_CAP,
         "cap_core_min": cap_cm, "measured_core_min": wall_total * RANKS / 60.0,
         "G-COMPLETE": vc, "G-CAPS": vp, "G-REPRO": vr,
         "G-PATCHPAIR": vq}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
