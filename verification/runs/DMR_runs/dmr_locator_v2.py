#!/usr/bin/env python3
"""DMR locator v2 -- SUCCESSOR to dmr_locator.py, carrying a planted control.

WHY THIS IS A NEW FILE AND NOT AN EDIT
--------------------------------------
`dmr_locator.py` is the detector named in `DMR_PREREGISTRATION.md` section 4 as
the pre-committed detector, and it is the reader that produced the recorded
Gate V / P1 / P2 verdicts in `DMR_RESULTS.md`.  Editing it would change the
grading path of verdicts already on the record.  This file is therefore a
SUCCESSOR: the original stays byte-identical and keeps its provenance, and this
one is the reader registered for any NEW rung.  That is the same route
`DMR_RESULTS.md` took for the P1 detector defect -- "the repair is a successor
detector ... not an after-the-fact edit here".

PROVENANCE NOTE, recorded because it is true and was not previously stated:
`dmr_locator.py` was first committed at `84933043` (2026-08-08T01:56:04Z),
which is AFTER the runs it graded (2026-08-07T22:44-22:46).  The
pre-registration calls it "the pre-committed detector"; git cannot corroborate
that ordering.  The file content may well have existed on disk before the run,
but the freeze is not hash-provable.  This successor is committed BEFORE the
rung it is registered to grade, so that gap does not recur.

WHAT v2 ADDS (and it adds ONLY these things)
--------------------------------------------
1. A TWO-SIDED PLANTED CONTROL (CLAUDE.md rule 3).
   - PLANTED PERTURBATION: the density field is displaced by a KNOWN INTEGER
     number of cells.  On this uniform Cartesian grid an integer-cell roll is
     an EXACT operation, so the located front MUST move by exactly k*dx.  The
     reader is refused if it does not.
   - PLANTED ABSENCE: the crossing is removed from the row (the row is set to
     the uniform pre-shock state).  The reader MUST refuse, not return a null.
2. AN EXPLICIT REFUSAL where the original returns None.
   `dmr_locator.py`'s `front_x()` returns None silently when it finds no
   crossing, and `locator_result.json` proves this propagates: `x_incident_y09`
   is `null` at t = 0.10 on BOTH rungs of the graded record.  A null that
   reaches a graded record is the failure mode rule 3 exists to stop.  Here a
   missing crossing RAISES.

WHAT v2 DELIBERATELY DOES NOT CHANGE
------------------------------------
The physics, the search windows, the crossing level, the fit and the gate
arithmetic are transcribed from `dmr_locator.py` unchanged.  `--selfcheck`
asserts that v2 reproduces the ORIGINAL recorded Gate V positions on both
existing rungs to 1e-12, so the successor is demonstrably the same instrument
plus a control, not a different one.

Usage:
    dmr_locator_v2.py <case_dir> <N> [--out PATH]   grade a rung
    dmr_locator_v2.py --selfcheck                   controls + regression, no writes

`--out` is REQUIRED to write; without it nothing is written.  This reader will
never overwrite an existing result file: it refuses instead.  The frozen
`locator_result.json` of res60/res120 cannot be clobbered by running this.
"""
import re
import sys
import json
import math
import argparse
from pathlib import Path

import numpy as np

X0 = 1.0 / 6.0
SQ3 = math.sqrt(3.0)
TIMES = [0.1, 0.12, 0.14, 0.16, 0.18, 0.2]

# Gate V constants, transcribed from DMR_PREREGISTRATION.md section 4.
GATEV_TOL = 0.0231
GATEV_Y = 0.9
LEVEL_INCIDENT = 0.5 * (1.4 + 8.0)   # midpoint of pre- and post-shock density
LEVEL_FRONT = 2.7

# The planted control's shift, in whole cells.  Integer by construction: on a
# uniform grid an integer roll is exact, so the expected response is exact too.
PLANT_CELLS = 7
PLANT_TOL = 1e-9


class ReaderRefused(Exception):
    """The reader cannot testify.  Never downgrade this to a None or a zero."""


def read_scalar(path):
    """Parse an OpenFOAM scalar internalField.  Refuses rather than guessing."""
    p = Path(path)
    if not p.exists():
        raise ReaderRefused(f"{p}: field absent -- an absent field reads ABSENT, never clean")
    s = p.read_text()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\(\n(.*?)\n\)", s, re.S)
    if m is None:
        raise ReaderRefused(
            f"{p}: no nonuniform scalar list matched. A uniform or differently "
            f"headed field is not silently reshaped -- this reader refuses to guess.")
    n = int(m.group(1))
    v = np.fromstring(m.group(2), sep="\n")
    if v.size != n:
        raise ReaderRefused(f"{p}: header declares {n} values, parsed {v.size}")
    return v


class Case:
    """One rung's t = 0.2 grid and the fields on it."""

    def __init__(self, case_dir, N):
        self.dir = Path(case_dir)
        self.N = int(N)
        self.dx = 1.0 / self.N
        cx = read_scalar(self.dir / "0.2" / "Cx")
        cy = read_scalar(self.dir / "0.2" / "Cy")
        # NO WRITE ORDER IS ASSUMED.  These cases were solved on four ranks and
        # reconstructed; the reconstructed fields are NOT in x-fastest order and
        # a bare reshape would slice by rank into a plausible wrong picture.
        self.ix = np.rint(cx / self.dx - 0.5).astype(int)
        self.iy = np.rint(cy / self.dx - 0.5).astype(int)
        self.nx = int(self.ix.max()) + 1
        self.ny = int(self.iy.max()) + 1
        if self.ix.size != self.nx * self.ny:
            raise ReaderRefused(
                f"{self.dir}: {self.ix.size} cells do not fill {self.nx}x{self.ny}")
        self.xc = (np.arange(self.nx) + 0.5) * self.dx
        self.yc = (np.arange(self.ny) + 0.5) * self.dx

    def grid(self, v):
        g = np.full((self.ny, self.nx), np.nan)
        g[self.iy, self.ix] = v
        if np.isnan(g).any():
            raise ReaderRefused(f"{self.dir}: gridding left holes; refusing to interpolate over them")
        return g

    def rho(self, t):
        return self.grid(read_scalar(self.dir / f"{t:g}" / "rho"))


def x_incident_exact(y, t):
    return X0 + (y + 20.0 * t) / SQ3


def _crossing_from_left(x, r, level, what):
    """Last downward crossing of `level`, scanning left to right.

    Transcribed from dmr_locator.py's Gate V loop.  RAISES where the original
    left `xinc` as None.
    """
    hit = None
    for k in range(len(x) - 1):
        if r[k] >= level > r[k + 1]:
            f = (level - r[k + 1]) / (r[k] - r[k + 1])
            hit = x[k + 1] + f * (x[k] - x[k + 1])
    if hit is None:
        raise ReaderRefused(
            f"{what}: no downward crossing of rho = {level} in the search window "
            f"[{x[0]:.4f}, {x[-1]:.4f}]. The original reader returned None here and "
            f"the null reached a graded record; this reader refuses instead.")
    return hit


def x_incident_measured(case, t, rho=None):
    """Gate V's reader: incident-shock x on the row nearest y = 0.9."""
    rho = case.rho(t) if rho is None else rho
    j = int(np.argmin(np.abs(case.yc - GATEV_Y)))
    row = rho[j]
    sel = (case.xc >= 2.0) & (case.xc <= 3.8)
    return _crossing_from_left(case.xc[sel], row[sel], LEVEL_INCIDENT,
                               f"incident shock, t = {t:g}, row y = {case.yc[j]:.5f}"), j


# ---------------------------------------------------------------------------
# THE PLANTED CONTROL.  A zero -- or any value -- from a reader not shown able
# to see a known non-zero is not evidence (CLAUDE.md rule 3).
# ---------------------------------------------------------------------------

def plant_shift(rho, k_cells):
    """Displace the density field by EXACTLY k whole cells in +x.

    Integer roll on a uniform grid is exact, so the located front must move by
    exactly k*dx.  The vacated column is filled with the post-shock state so the
    field stays physically admissible and the crossing is not manufactured.
    """
    out = np.roll(rho, k_cells, axis=1)
    out[:, :k_cells] = rho[:, :1]
    return out


def plant_absence(rho, case):
    """Remove the crossing from the Gate V row: uniform pre-shock state."""
    out = rho.copy()
    j = int(np.argmin(np.abs(case.yc - GATEV_Y)))
    out[j, :] = 1.4
    return out


def run_controls(case, verbose=True):
    """Two-sided control.  Returns True only if BOTH sides behave."""
    rho = case.rho(0.2)
    real, _ = x_incident_measured(case, 0.2, rho=rho)

    # --- CONTROL 1: planted perturbation, a known shift the reader must see.
    expected = PLANT_CELLS * case.dx
    moved_x, _ = x_incident_measured(case, 0.2, rho=plant_shift(rho, PLANT_CELLS))
    moved = moved_x - real
    seen = abs(moved - expected) < PLANT_TOL

    # --- CONTROL 2: planted absence, which the reader must REFUSE.
    try:
        x_incident_measured(case, 0.2, rho=plant_absence(rho, case))
        refused, why = False, "returned a value where there was no crossing"
    except ReaderRefused as exc:
        refused, why = True, str(exc).split(".")[0]

    if verbose:
        print(f"  CONTROL 1 planted shift : planted {expected:.9f}  "
              f"reader moved {moved:.9f}  -> {'SEEN' if seen else 'NOT SEEN'}")
        print(f"  CONTROL 2 planted absence: -> {'REFUSED' if refused else 'DID NOT REFUSE'} ({why})")
    if not (seen and refused):
        raise ReaderRefused(
            "PLANTED CONTROL FAILED. No number from this reader is evidence. "
            f"perturbation seen={seen}, absence refused={refused}")
    return True


def grade(case_dir, N):
    """Grade one rung.  The control runs FIRST and refuses before any number."""
    case = Case(case_dir, N)
    print(f"planted control on {case.dir} (dx = {case.dx:.6f}):")
    run_controls(case)

    locates = []
    for t in TIMES:
        rho = case.rho(t)
        try:
            xinc, j = x_incident_measured(case, t, rho=rho)
        except ReaderRefused as exc:
            # Recorded as a NAMED refusal, never as a null.
            xinc, j = None, None
            locates.append(dict(t=t, x_incident_y09="REFUSED", reason=str(exc)))
            continue
        locates.append(dict(t=t, x_incident_y09=float(xinc), y_row=float(case.yc[j])))

    r02 = locates[-1]
    if not isinstance(r02.get("x_incident_y09"), float):
        raise ReaderRefused("Gate V has no reading at t = 0.2; the rung is NOT A RESULT, not a null.")
    j = int(np.argmin(np.abs(case.yc - GATEV_Y)))
    x_meas = r02["x_incident_y09"]
    x_exact_row = float(x_incident_exact(case.yc[j], 0.2))
    err = x_meas - x_exact_row
    gateV = dict(y_row=float(case.yc[j]), x_measured=x_meas,
                 x_exact_at_row=x_exact_row,
                 x_exact_at_0p9=float(x_incident_exact(GATEV_Y, 0.2)),
                 error=err, tol=GATEV_TOL, locator_increment=case.dx,
                 error_in_cells=err / case.dx,
                 PASS=bool(abs(err) <= GATEV_TOL),
                 planted_control="PASSED (shift seen, absence refused)")
    return dict(case=str(case.dir.name), N=case.N, dx=case.dx, times=TIMES,
                locates=locates, gateV=gateV,
                reader="dmr_locator_v2.py", control="two-sided, run before grading")


# --- Recorded Gate V positions from the 2026-08-07 graded record.  The
# --- successor must reproduce them exactly or it is a different instrument.
REGRESSION = {
    "res60": (60, 3.0044811459860723),
    "res120": (120, 2.996658749065891),
}


def selfcheck(root):
    root = Path(root)
    ok = True
    for name, (N, recorded) in REGRESSION.items():
        d = root / name
        if not d.exists():
            print(f"  {name}: ABSENT -- cannot self-check against it")
            ok = False
            continue
        case = Case(d, N)
        print(f"{name}:")
        run_controls(case)
        got, _ = x_incident_measured(case, 0.2)
        delta = abs(got - recorded)
        good = delta < 1e-12
        print(f"  REGRESSION vs graded record: recorded {recorded!r}")
        print(f"                               v2 reads {got!r}  |delta| = {delta:.3e} "
              f"-> {'IDENTICAL' if good else 'DIVERGED'}")
        ok = ok and good
    print("\nSELFCHECK: " + ("PASS -- controls live and instrument unchanged"
                             if ok else "FAIL -- do not grade with this reader"))
    return 0 if ok else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case", nargs="?")
    ap.add_argument("N", nargs="?", type=int)
    ap.add_argument("--out")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()

    if a.selfcheck:
        return selfcheck(Path(__file__).resolve().parent)

    if not a.case or not a.N:
        raise SystemExit("usage: dmr_locator_v2.py <case_dir> <N> [--out PATH] | --selfcheck")

    out = json.dumps(grade(a.case, a.N), indent=1)
    print(out)
    if a.out:
        p = Path(a.out)
        if p.exists():
            raise ReaderRefused(
                f"{p} already exists. This reader never overwrites a result file; "
                f"a graded record is not clobbered by a re-run.")
        p.write_text(out)
        print(f"\nwritten: {p}")
    else:
        print("\n(no --out given: nothing written)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReaderRefused as exc:
        print(f"\nREADER REFUSED: {exc}", file=sys.stderr)
        raise SystemExit(2)
