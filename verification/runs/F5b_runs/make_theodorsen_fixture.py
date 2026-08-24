#!/usr/bin/env python3
"""Generate the F5b Physics rung's C-N1 negative control: an ATTACHED-FLOW
(Theodorsen) hysteresis loop written in the exact column layout OpenFOAM v2606's
``forceCoeffs`` function object produces.

Registered by ``verification/campaign/F5b_PHYSICS_PREREGISTRATION.md`` sections 4
and 10 and committed at that document's freeze, BEFORE any F5b Physics compute
exists.  The point of the fixture is stated in the pre-registration and is worth
repeating at the top of the generator:

    The state in which "dynamic stall occurred" is FALSE but every naive
    signature of it is still present is attached flow with pitch-rate phase lag.
    A solve that never stalls at all still produces an open C_L-alpha loop.  The
    fixture IS that state, built on purpose, and the reader must score it as
    "no stall" -- G1 below band, G2 not firing -- or the reader is broken and its
    verdict on the real run is void.

WHAT IS PHYSICS HERE AND WHAT IS NOT
------------------------------------
Only the ``Cl`` column carries physics.  Every other coefficient column is a
CONSTANT SENTINEL of the form ``-70 - j`` where ``j`` is the column's index in the
coefficient ordering.  That choice is deliberate and is itself a control:

  * no real C_d, C_s or C_m is anywhere near -70, so a positional misread is
    absurd on sight rather than plausible;
  * the value encodes WHICH column was read, so a misread is diagnosable;
  * the columns are constant, so a positional misread of the gate quantity
    produces A_L = 0 exactly and max-pair dC_L = 0 exactly -- which C-N1's
    assertions (a) and (c) both catch.

This matters because of a real trap documented in the pre-registration: E4's
``forceCoeffs1`` dictionary has no ``coefficients`` entry, so OpenFOAM writes ALL
TWELVE coefficients, sorted lexicographically, and ``Cl`` lands at 0-based field
index 4 -- not the index 2 of the familiar ``Time Cd Cl Cm`` layout.  A reader
written positionally would have graded this rung's gate on ``Cd(f)``.

THE COLUMN LAYOUT, FROM THE INSTALLED SOURCE
--------------------------------------------
``/usr/lib/openfoam/openfoam2606/src/functionObjects/forces/forceCoeffs/forceCoeffs.C``

  :337-349  no ``coefficients`` dict entry -> "Selecting all coefficients",
            every entry ``active_ = true``
  :135-151  ``selectCoeffs()`` inserts Cd, Cs, Cl; then front/rear for each of
            those three; then CmRoll, CmPitch, CmYaw   -> twelve
  :237,:256 header and rows both iterate ``coeffs_.csorted()`` -- lexicographic
            key order, NOT insertion order

``/usr/lib/openfoam/openfoam2606/src/OpenFOAM/db/functionObjects/writeFile/``

  writeFile.C:37,:319  ``charWidth() = writePrecision_ + addChars``, addChars = 8
  writeFile.C:218      ``writePrecision_`` defaults to IOstream::defaultPrecision()
  TimeIO.C:379-384     which Time::readDict sets from controlDict writePrecision
                       -- 10 for this case (E4) -- so charWidth() = 18
  writeFile.C:323-336  writeCommented: '#', ' ', str left-justified in setw(cw-2)
  writeFile.C:339-345  writeTabbed:    tab, str right-justified in setw(cw)
  writeFile.C:360-370  writeCurrentTime: Time::timeName right-justified in setw(cw)
  forceCoeffs.C:265    values: ``os << tab << value`` -- tab-separated, NOT padded

USAGE
-----
    python3 verification/runs/F5b_runs/make_theodorsen_fixture.py \
        --out verification/runs/F5b_runs/controls/theodorsen_attached_fixture.dat

Zero compute: no solver, no mesh, no run directory.
"""

from __future__ import annotations

import argparse
import cmath
import hashlib
import math
import os
import sys

# --------------------------------------------------------------------------
# Case constants -- E2, sdk/workflows/pitching_airfoil_case.py
# (md5 06bfcfd40bc011cf2cb2fd41370b5c4b, frozen at PREREGISTRATION section 1)
# --------------------------------------------------------------------------
ALPHA_MEAN_DEG = 15.0
ALPHA_AMP_DEG = 10.0
OMEGA = 0.3
PERIOD = 2.0 * math.pi / OMEGA          # 20.943951023931955
REDUCED_FREQ = 0.15                     # k
PITCH_AXIS_A = -0.5                     # quarter chord, semi-chords from mid-chord
U_INF = 1.0

# The registered run's endTime (PREREGISTRATION section 3).  The fixture spans the
# analysis window W = [endTime - PERIOD, endTime] so that a reader applying the
# registered window rule -- including its assertion t1 >= 1.0 -- runs on the
# fixture UNMODIFIED, which is what C-N1 requires.
END_TIME = 21.9440

# OpenFOAM write formatting, derived above.
CHAR_WIDTH = 18                         # writePrecision(10) + addChars(8)
WRITE_PRECISION = 10                    # controlDict writePrecision (E4)
TIME_PRECISION = 8                      # controlDict timePrecision  (E4)

# Direction vectors, E2:88-91.  liftDir . Uhat = 0 and dragDir . Uhat = 1 exactly,
# so the Cl column is a true C_L (PREREGISTRATION section 2).
_AM = math.radians(ALPHA_MEAN_DEG)
DRAG_DIR = (math.cos(_AM), math.sin(_AM), 0.0)
LIFT_DIR = (-math.sin(_AM), math.cos(_AM), 0.0)
# forces.C:55-90 -- cartesian(origin, e3=liftDir, e1=dragDir); e2 = e3 ^ e1.
SIDE_DIR = (
    LIFT_DIR[1] * DRAG_DIR[2] - LIFT_DIR[2] * DRAG_DIR[1],
    LIFT_DIR[2] * DRAG_DIR[0] - LIFT_DIR[0] * DRAG_DIR[2],
    LIFT_DIR[0] * DRAG_DIR[1] - LIFT_DIR[1] * DRAG_DIR[0],
)                                        # = (0, 0, -1)

SENTINEL_BASE = -70.0
SENTINEL_STEP = -1.0


def theodorsen_C(k: float) -> complex:
    """Jones two-lag approximation to Theodorsen's function.

    C(k) = 1 - 0.165/(1 - 0.0455i/k) - 0.335/(1 - 0.3i/k)
    """
    return 1.0 - 0.165 / (1.0 - 0.0455j / k) - 0.335 / (1.0 - 0.3j / k)


def lift_slope_Z(k: float, a: float) -> complex:
    """Complex C_L per radian of alpha for pitching about ``a`` semi-chords from
    mid-chord (PREREGISTRATION section 2):

        Z = 2 pi C(k) (1 + i k (1/2 - a)) + pi i k + pi a k^2
    """
    C = theodorsen_C(k)
    return 2.0 * math.pi * C * (1.0 + 1j * k * (0.5 - a)) + math.pi * 1j * k \
        + math.pi * a * k * k


def alpha_deg(t: float) -> float:
    """E2's prescribed motion, verbatim (pitching_airfoil_case.py:94-95).

    This is an IDENTITY, not a measurement: alpha is an input to the solve.
    """
    return ALPHA_MEAN_DEG + ALPHA_AMP_DEG * math.sin(OMEGA * t)


def cl_attached(t: float, Z: complex) -> float:
    """Attached-flow C_L(t) for alpha(t) = alpha_m + alpha_a sin(omega t).

    C_L = 2 pi alpha_m  +  alpha_a (Re Z sin(omega t) + Im Z cos(omega t))

    The steady 2 pi alpha_m offset is included so the fixture LOOKS like a real
    lift loop.  It cancels out of both gate quantities exactly -- a constant adds
    nothing to a closed contour integral (G1) and nothing to a difference of two
    C_L values (G2) -- so it changes neither of C-N1's assertions.
    """
    aa = math.radians(ALPHA_AMP_DEG)
    wt = OMEGA * t
    return 2.0 * math.pi * math.radians(ALPHA_MEAN_DEG) \
        + aa * (Z.real * math.sin(wt) + Z.imag * math.cos(wt))


def coefficient_names() -> list[str]:
    """The twelve active coefficient names in the order OpenFOAM writes them.

    Reproduces forceCoeffs.C:135-151 (which entries exist) and :237 (csorted --
    lexicographic key order).
    """
    base = ["Cd", "Cs", "Cl"]
    names = list(base)
    for n in base:                       # front/rear are added from a copy taken
        names.append(n + "(f)")          # BEFORE the moments (forceCoeffs.C:139-145)
        names.append(n + "(r)")
    names += ["CmRoll", "CmPitch", "CmYaw"]
    ordered = sorted(names)              # csorted(): lexicographic on the word key
    expected = ["Cd", "Cd(f)", "Cd(r)", "Cl", "Cl(f)", "Cl(r)",
                "CmPitch", "CmRoll", "CmYaw", "Cs", "Cs(f)", "Cs(r)"]
    if ordered != expected:
        raise AssertionError(
            "coefficient ordering drifted from the layout read out of "
            "forceCoeffs.C: %r != %r" % (ordered, expected))
    return ordered


def _vec(v: tuple[float, float, float]) -> str:
    return "(%s %s %s)" % tuple(_num(x) for x in v)


def _num(x: float) -> str:
    """C++ default float formatting at stream precision 10."""
    return "%.*g" % (WRITE_PRECISION, x)


def _time(x: float) -> str:
    """Time::timeName under timeFormat general / timePrecision 8."""
    return "%.*g" % (TIME_PRECISION, x)


def header_block(names: list[str]) -> list[str]:
    """The forceCoeffs header, in the exact shape writeIntegratedDataFileHeader
    produces (forceCoeffs.C:220-246)."""
    w = CHAR_WIDTH - 2                   # writeCommented / writeHeaderValue field

    def hv(prop: str, val: str) -> str:
        return "# " + prop.ljust(w) + ": " + val

    lines = [
        "# Force and moment coefficients",
        hv("dragDir", _vec(DRAG_DIR)),
        hv("sideDir", _vec(SIDE_DIR)),
        hv("liftDir", _vec(LIFT_DIR)),
        hv("rollAxis", _vec(DRAG_DIR)),
        hv("pitchAxis", _vec(SIDE_DIR)),
        hv("yawAxis", _vec(LIFT_DIR)),
        hv("magUInf", _num(U_INF)),
        hv("lRef", _num(1.0)),
        hv("Aref", _num(1.0)),
        hv("CofR", _vec((0.0, 0.0, 0.0))),
        "#",
    ]
    col = "# " + "Time".ljust(w)
    for n in names:
        col += "\t" + n.rjust(CHAR_WIDTH)
    lines.append(col)
    return lines


def provenance_block(n_samples: int, Z: complex, a_att: float) -> list[str]:
    """Comment lines PREPENDED to the OpenFOAM header so the fixture announces
    itself.  Every line starts with '#', so the registered parse (skip '#' lines,
    take the LAST one whose tokens begin with 'Time') is unaffected."""
    return [
        "# ============================================================",
        "# SYNTHETIC NEGATIVE CONTROL -- NOT SOLVER OUTPUT.  NO SOLVER RAN.",
        "# F5b Physics rung, control C-N1.",
        "#   registered by verification/campaign/F5b_PHYSICS_PREREGISTRATION.md",
        "#   generated by verification/runs/F5b_runs/make_theodorsen_fixture.py",
        "# Attached-flow (Theodorsen/Jones) hysteresis loop for the SAME prescribed",
        "# motion as the registered run: alpha(t) = %.1f + %.1f sin(%.1f t) deg,"
        % (ALPHA_MEAN_DEG, ALPHA_AMP_DEG, OMEGA),
        "# k = %.2f, pitch axis a = %.1f semi-chords, one full period,"
        % (REDUCED_FREQ, PITCH_AXIS_A),
        "# %d samples spanning W = [endTime - PERIOD, endTime]." % n_samples,
        "#   C(k)  = %s" % _fmt_complex(theodorsen_C(REDUCED_FREQ)),
        "#   Z     = %s   [C_L per radian of alpha]" % _fmt_complex(Z),
        "#   A_att = %.8f C_L.deg   (closed form)" % a_att,
        "# THIS LOOP CONTAINS NO STALL.  A reader that scores it as dynamic stall",
        "# is broken and its verdict on the real run is void.",
        "#",
        "# ONLY THE 'Cl' COLUMN CARRIES PHYSICS.  Every other coefficient column is",
        "# a constant sentinel -70 - j (j = its index in the coefficient ordering),",
        "# chosen so a positional misread is absurd on sight, is traceable to the",
        "# column that was read, and drives A_L and max-pair dC_L to exactly zero.",
        "#",
        "# The header-value lines below carry the ANALYTIC normalised direction",
        "# vectors.  A real run's last digits may differ by normalisation round-off.",
        "# No reader parses a header VALUE -- only the column-name line.",
        "# ============================================================",
    ]


def _fmt_complex(z: complex) -> str:
    return "%.7f %+.7fi" % (z.real, z.imag)


def build(n_samples: int) -> tuple[list[str], dict]:
    Z = lift_slope_Z(REDUCED_FREQ, PITCH_AXIS_A)
    aa = math.radians(ALPHA_AMP_DEG)
    a_att_rad = math.pi * aa * aa * Z.imag
    a_att_deg = a_att_rad * 180.0 / math.pi

    names = coefficient_names()
    icl = names.index("Cl")

    t1 = END_TIME - PERIOD
    if t1 < 1.0:
        raise AssertionError("fixture window start %.9f < 1.0" % t1)

    lines: list[str] = []
    lines += provenance_block(n_samples, Z, a_att_deg)
    lines += header_block(names)

    # Sample times are written at 8 significant figures, exactly as Time::timeName
    # would.  The Cl values are then computed FROM THE ROUNDED TIMES, so the file is
    # internally self-consistent: a reader reconstructing alpha from the Time column
    # it parsed gets exactly the alpha the Cl column was built on.  A real run's file
    # has the same 8-figure truncation; the fixture must not be gentler than reality.
    written_t: list[float] = []
    written_cl: list[float] = []
    for i in range(n_samples):
        t_exact = t1 + PERIOD * i / (n_samples - 1)
        ts = _time(t_exact)
        t = float(ts)
        cl = cl_attached(t, Z)
        row = ts.rjust(CHAR_WIDTH)
        for j, n in enumerate(names):
            v = cl if j == icl else SENTINEL_BASE + SENTINEL_STEP * j
            row += "\t" + _num(v)
        lines.append(row)
        written_t.append(t)
        written_cl.append(cl)

    meta = {
        "Z": Z,
        "A_att_deg": a_att_deg,
        "t1": t1,
        "t_end": written_t[-1],
        "n": n_samples,
        "cl_index": icl,
        "names": names,
        "times": written_t,
        "cl": written_cl,
    }
    return lines, meta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--out",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "controls", "theodorsen_attached_fixture.dat"),
        help="output path for the fixture")
    ap.add_argument("--samples", type=int, default=4096,
                    help="number of samples over one period (default 4096)")
    args = ap.parse_args(argv)

    lines, meta = build(args.samples)
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    text = "\n".join(lines) + "\n"
    with open(out, "w") as fh:
        fh.write(text)

    md5 = hashlib.md5(text.encode()).hexdigest()
    print("WROTE   %s" % out)
    print("samples %d   columns %d (Time + %d coefficients)"
          % (meta["n"], len(meta["names"]) + 1, len(meta["names"])))
    print("Cl at 0-based field index %d  (order: %s)"
          % (meta["cl_index"] + 1, " ".join(meta["names"])))
    print("window  t1 = %.9f   t_end = %.9f   span = %.9f (PERIOD = %.9f)"
          % (meta["t1"], meta["t_end"], meta["t_end"] - meta["t1"], PERIOD))
    print("Z       = %s" % _fmt_complex(meta["Z"]))
    print("A_att   = %.8f C_L.deg  (closed form, the value C-N1 asserts)"
          % meta["A_att_deg"])
    print("md5     %s" % md5)
    return 0


if __name__ == "__main__":
    sys.exit(main())
