#!/usr/bin/env python3
"""Reference loader and verifier for AGARD AR-138 Table B1-1.

M6 WING STREAMWISE SECTION COORDINATES (DESIGN VALUES) -- the ONERA M6 root
section (y/b = 0.0), 72 points, printed at AGARD-AR-138 page B1-7.

WHY THIS FILE EXISTS.  The reference table has a sharpened lookalike -- in fact
at least TWO distinct ones -- in circulation, and every one of them carries
AGARD's own abscissae and AGARD's own forward ordinates.  They differ from the
true table ONLY aft of x/c = 0.9061905, and they end at z/l = 0 instead of
z/l = 0.0007052.  A reader that grabs the nearest-looking section file grades a
sharp surface against a sharp reference and reports perfect agreement.

This module therefore REFUSES (exit 2 / SharpenedReferenceError) rather than
degrade, and it plants a control before it trusts its own eyes.

  load_reference(path)  -> [(x, z)] * 72, or raises.  This is control C19.
  verify(rows)          -> dict of structural + smoothness findings.

Provenance and the L-144 title-page verification are recorded in
models/onera_m6/PROVENANCE.md.  Do not take this file's word for the table's
identity; that document names the printed page and quotes it.
"""

import sys

# AGARD AR-138 Table B1-1, read from the printed page (PDF page 333, printed
# page B1-7) of docs/papers/benchmark_test_cases/agard_1979_ar138_experimental
# _data_base.pdf.  These four anchors are what the loader checks a candidate
# reference against; they are NOT a substitute for the full table.
N_POINTS = 72
X_FIRST, Z_FIRST = 0.0, 0.0
X_LAST, Z_LAST = 1.0, 0.0007052
T_TE_OVER_C = 0.0014104          # = 2 * Z_LAST, the blunt trailing edge
SHARPENING_ONSET_X = 0.9061905   # foilmod.f90 rescales from this row aft

# Rule 3.  The loader must be shown able to SEE a non-zero trailing-edge
# ordinate before a zero from it means anything.
PLANT = 3.21e-04


class SharpenedReferenceError(Exception):
    """The candidate reference has a sharp (zero-thickness) trailing edge."""


class ReferenceStructureError(Exception):
    """The candidate reference is not shaped like Table B1-1."""


def parse(path):
    """Parse a two-column ordinate table.  Structure only -- never the name."""
    rows = []
    with open(path, errors="replace") as fh:
        for ln in fh:
            f = ln.split()
            if len(f) != 2:
                continue
            try:
                rows.append((float(f[0]), float(f[1])))
            except ValueError:
                continue
    return rows


def load_reference(path, _plant=None):
    """Load Table B1-1, REFUSING any sharpened derivative.  Control C19.

    `_plant` is for the planted control only: it replaces the final ordinate so
    the caller can prove this refusal can also PASS a non-zero.
    """
    rows = parse(path)
    if _plant is not None:
        rows = rows[:-1] + [(rows[-1][0], _plant)]

    if len(rows) != N_POINTS:
        raise ReferenceStructureError(
            f"{path}: {len(rows)} points, Table B1-1 has {N_POINTS}. "
            "A different count is a FINDING, never something to round to.")

    xs = [x for x, _ in rows]
    if any(b <= a for a, b in zip(xs, xs[1:])):
        raise ReferenceStructureError(f"{path}: x/l is not strictly increasing.")
    if abs(xs[0] - X_FIRST) > 1e-12 or abs(xs[-1] - X_LAST) > 1e-12:
        raise ReferenceStructureError(
            f"{path}: x/l runs {xs[0]}..{xs[-1]}, expected {X_FIRST}..{X_LAST}. "
            "A table extending BEYOND x/l = 1 has been sharpened by chord "
            "extension (a +0.55 % extension is on record on this box).")

    z_te = rows[-1][1]
    if z_te < 1.0e-05:
        raise SharpenedReferenceError(
            f"{path}: final ordinate z/l = {z_te!r} is a SHARP trailing edge. "
            f"AGARD Table B1-1 ends at z/l = {Z_LAST} (t_TE/c = {T_TE_OVER_C}). "
            "This is a sharpened derivative, NOT Table B1-1.  REFUSED.")
    return rows


def verify(rows):
    """Structural and smoothness findings on a loaded table."""
    xs = [x for x, _ in rows]
    zs = [z for _, z in rows]
    peak = max(range(len(zs)), key=lambda i: zs[i])
    rising = all(b >= a for a, b in zip(zs[:peak + 1], zs[1:peak + 1]))
    falling = all(b <= a for a, b in zip(zs[peak:], zs[peak + 1:]))

    # Digit-corruption scan.  A single mistyped/misOCR'd digit in an otherwise
    # smooth ordinate distribution shows up as a spike in the second difference
    # of z with respect to arc position.  Reported, never used to "correct" a
    # value -- this module edits nothing.
    d2 = []
    for i in range(1, len(zs) - 1):
        h1, h2 = xs[i] - xs[i - 1], xs[i + 1] - xs[i]
        s = 2.0 * ((zs[i + 1] - zs[i]) / h2 - (zs[i] - zs[i - 1]) / h1) / (h1 + h2)
        d2.append((abs(s), i))
    # normalise against the median so the leading-edge singularity does not
    # dominate; report the worst offenders for a human to read.
    d2.sort(reverse=True)

    return {
        "n_points": len(rows),
        "x_first": xs[0], "x_last": xs[-1],
        "z_first": zs[0], "z_last": zs[-1],
        "t_te_over_c": 2.0 * zs[-1],
        "z_max": zs[peak], "x_at_z_max": xs[peak],
        "single_peaked": rising and falling,
        "worst_curvature_rows": [i for _, i in d2[:3]],
    }


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 0
    ref = argv[1]

    # ---- STRUCTURE FIRST, AND IT REFUSES -- IT NEVER CRASHES ---------------
    # An earlier form of this main() ran the planted control first and caught
    # only SharpenedReferenceError in its refuse limb.  Fed the 63-point
    # lookalike, the structure check raised THROUGH the control block and the
    # program died with a traceback and rc=1.  A crash is not a refusal: the
    # contract is refuse (exit 2) rather than degrade, and rc=1 is neither.
    # Both limbs below therefore catch both exception types.
    try:
        load_reference(ref, _plant=PLANT)
    except ReferenceStructureError as exc:
        print(f"REFUSED: {exc}")
        return 2
    except SharpenedReferenceError:
        pass  # cannot happen with a planted non-zero; handled for completeness

    # ---- PLANTED CONTROL (rule 3), run BEFORE the reference is trusted -----
    # A refusal from a reader never shown able to ACCEPT is not evidence, and
    # an acceptance from a reader never shown able to REFUSE is not evidence
    # either.  Both limbs are exercised here and both must fire.
    ok_accept = False
    try:
        load_reference(ref, _plant=PLANT)
        ok_accept = True
    except (SharpenedReferenceError, ReferenceStructureError):
        pass
    ok_refuse = False
    try:
        load_reference(ref, _plant=0.0)
    except SharpenedReferenceError:
        ok_refuse = True
    except ReferenceStructureError:
        pass
    print(f"CONTROL accept-a-planted {PLANT:.3e} trailing edge : "
          f"{'FIRED' if ok_accept else 'DID NOT FIRE'}")
    print(f"CONTROL refuse-a-planted 0.0 trailing edge       : "
          f"{'FIRED' if ok_refuse else 'DID NOT FIRE'}")
    if not (ok_accept and ok_refuse):
        print("REFUSED: the reader has not been shown correct on a planted "
              "case, so nothing it reports about the reference is evidence.")
        return 2

    # ---- the reference itself ---------------------------------------------
    try:
        rows = load_reference(ref)
    except (SharpenedReferenceError, ReferenceStructureError) as exc:
        print(f"REFUSED: {exc}")
        return 2

    f = verify(rows)
    print(f"points                : {f['n_points']}")
    print(f"first (x/l, z/l)      : ({f['x_first']!r}, {f['z_first']!r})")
    print(f"last  (x/l, z/l)      : ({f['x_last']!r}, {f['z_last']!r})")
    print(f"t_TE/c = 2*z_last     : {f['t_te_over_c']:.7f}")
    print(f"max z/l               : {f['z_max']!r} at x/l = {f['x_at_z_max']!r}")
    print(f"single-peaked         : {f['single_peaked']}")
    print(f"largest-curvature rows: {f['worst_curvature_rows']} (reported, not corrected)")

    ok = (f["n_points"] == N_POINTS
          and abs(f["t_te_over_c"] - T_TE_OVER_C) < 1e-12
          and f["single_peaked"])
    print("VERDICT               : "
          + ("reference ACCEPTED as AGARD AR-138 Table B1-1"
             if ok else "REFUSED -- does not match Table B1-1"))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
