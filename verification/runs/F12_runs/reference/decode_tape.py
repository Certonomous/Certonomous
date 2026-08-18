"""Decode the RAE 2822 reference data from its archived primary sources.

Run:  python3 decode_tape.py            (writes the .dat files beside itself)

WHERE THE DATA COMES FROM
-------------------------
`f8621.txt` is the text image of flow case 8621 of the AFOSR-HTTM/Stanford
"Collaborative Testing of Turbulence Models" data library (the Bradshaw
database), retrieved 2026-07-30 from the NASA Turbulence Modeling Resource at

    https://tmbwg.github.io/turbmodels/Bradshaw/d2/f8621.txt

(listed on https://tmbwg.github.io/turbmodels/bradshaw.html; the legacy host
turbmodels.larc.nasa.gov now redirects to nasa.gov).

The file's own header states its provenance: evaluator R. E. Melnik (Grumman
Aerospace), revision date 1 November 1981, experiment run in the RAE
2.438 x 1.829 m slotted wind tunnel at Farnborough in May 1979, and reference

    Cook, P.H., McDonald, M.A., Firmin, M.C.P., "Aerofoil RAE 2822 - Pressure
    Distributions and Boundary Layer and Wake Measurements", AGARD AR-138,
    November 1979.

This is therefore a DIGITISED TRANSCRIPTION of AGARD AR-138, not the AR-138
document itself, made by the original experiment's AGARD evaluator and hosted
by NASA. It is treated as a secondary-but-authoritative source and labelled as
such everywhere it is used. No value in this repository was read off a plot.

`nparc_yu.pts`, `nparc_yl.pts`, `nparc_geom.txt` are the RAE 2822 section
ordinates from a second, independent NASA transcription of the same report,
the NPARC Alliance Validation Archive:

    https://www.grc.nasa.gov/www/wind/valid/raetaf/yu.pts
    https://www.grc.nasa.gov/www/wind/valid/raetaf/yl.pts
    https://www.grc.nasa.gov/www/wind/valid/raetaf/geom.txt

They agree with the tape's own design ordinates to 3.0e-6 chord, which is
below the tape's own 6.3e-6 storage quantum -- see the CROSS-CHECK block at
the bottom of this file. The NPARC files carry one more significant figure, so
they are what the mesh is built from.

TAPE ENCODING, quoted from the file's item 11
---------------------------------------------
    X = XMIN + (((XMAX-XMIN)*IXNORM)/10000)
    ALL NULL DATA ARE WRITTEN AS 20000.

Each tape "file" N appears in the text image as block number 1119+N. The
blocks this script reads:

    block 1121  (tape file 2)  section ordinates, 65 stations
    block 1122  (tape file 3)  case conditions for cases 1, 6, 7, 9, 12
    block 1126  (tape file 7)  CASE 9 surface pressures
"""

from __future__ import annotations

import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAPE = (HERE / "f8621.txt").read_text(encoding="utf-8", errors="replace").split("\n")

CASE_FIELDS = ["case", "Mach", "alpha_geometric", "alpha_corrected", "Re",
               "trip_diameter_m", "trip_x_over_c", "CN", "CM", "CD"]


def block(number: int) -> list[str]:
    start = end = None
    for i, line in enumerate(TAPE):
        if line.startswith("-") and f"FILE NUMBER  {number}-" in line:
            if "END OF" in line:
                end = i
                break
            start = i + 1
    return TAPE[start:end]


def e13(line: str, n: int) -> list[float]:
    """n fields of E13.6 in the old Fortran 'E 01' / 'E-02' style."""
    return [float(line[j * 13:(j + 1) * 13].replace("E ", "E+").replace("E", "e"))
            for j in range(n)]


def i6(line: str, n: int) -> list[int]:
    return [int(line[j * 6:(j + 1) * 6]) for j in range(n)]


def denorm(iv: int, lo: float, hi: float) -> float | None:
    return None if iv == 20000 else lo + (hi - lo) * iv / 10000.0


# --------------------------------------------------------------------------
# tape file 3 -- case conditions
# --------------------------------------------------------------------------

def case_conditions() -> dict[int, dict[str, float]]:
    b = block(1122)
    hi = e13(b[0], 5) + e13(b[1], 5)
    lo = e13(b[2], 5) + e13(b[3], 5)
    out = {}
    for row in b[4:]:
        iv = i6(row, 10)
        rec = {CASE_FIELDS[k]: denorm(iv[k], lo[k], hi[k]) for k in range(10)}
        out[round(rec["case"])] = rec
    return out


# --------------------------------------------------------------------------
# tape file 7 -- Case 9 surface pressures
# --------------------------------------------------------------------------

def case9_pressures() -> tuple[list, list]:
    """(upper, lower), each a list of (x/c, pstat/qref, Cp) sorted by x/c."""
    b = block(1126)
    hi, lo = e13(b[0], 6), e13(b[1], 6)
    upper, lower = [], []
    for row in b[2:]:
        v = [denorm(k, lo[j], hi[j]) for j, k in enumerate(i6(row, 6))]
        if v[0] is not None and v[2] is not None:
            upper.append((v[0], v[1], v[2]))
        if v[3] is not None and v[5] is not None:
            lower.append((v[3], v[4], v[5]))
    return sorted(upper), sorted(lower)


# --------------------------------------------------------------------------
# geometry, from the higher-precision NPARC transcription
# --------------------------------------------------------------------------

def nparc_surface(name: str) -> list[tuple[float, float]]:
    """Signed (x/c, y/c) from an NPARC .pts file. Fortran list-directed input,
    so '3*0.E+0' means three zeros and must be expanded, not skipped."""
    text = (HERE / name).read_text()
    points: list[tuple[float, float]] = []
    for line in text.split("\n")[1:]:          # line 1 is the '65,  1' count
        fields: list[float] = []
        for tok in line.split(","):
            tok = tok.strip()
            if not tok:
                continue
            if "*" in tok:
                rep, val = tok.split("*", 1)
                fields.extend([float(val)] * int(rep))
            else:
                fields.append(float(tok))
        if len(fields) >= 2:
            points.append((fields[0], fields[1]))
    return points


def tape_ordinates() -> list[list[float | None]]:
    b = block(1121)
    hi, lo = e13(b[0], 5), e13(b[1], 5)
    return [[denorm(k, lo[j], hi[j]) for j, k in enumerate(i6(row, 5))]
            for row in b[2:]]


# --------------------------------------------------------------------------

def main() -> None:
    cases = case_conditions()
    c9 = cases[9]
    print("Case conditions decoded from the tape (AGARD AR-138):")
    for num in sorted(cases):
        r = cases[num]
        print("  case %2d  M=%.3f  alpha_geom=%.2f  alpha_corr=%.2f  Re=%.3g  "
              "trip x/c=%.2f  CN=%.4f  CM=%+.4f  CD=%.4f"
              % (num, r["Mach"], r["alpha_geometric"], r["alpha_corrected"],
                 r["Re"], r["trip_x_over_c"], r["CN"], r["CM"], r["CD"]))

    upper, lower = case9_pressures()

    # ---- CHECK 1: the highest measured Cp must approach, but not exceed, the
    # isentropic stagnation Cp at the measured Mach number. A decoding error in
    # the min/max records would break this immediately.
    gam, M = 1.4, c9["Mach"]
    cp_stag = ((1 + 0.5 * (gam - 1) * M * M) ** (gam / (gam - 1)) - 1) \
        / (0.5 * gam * M * M)
    cp_peak = max(cp for _, _, cp in upper + lower)
    assert 0.9 * cp_stag < cp_peak <= cp_stag, (cp_peak, cp_stag)
    print("\nCHECK stagnation: peak measured Cp %.4f against isentropic %.4f "
          "at M=%.3f -- OK" % (cp_peak, cp_stag, M))

    # ---- CHECK 2: the tape stores each tap twice, as Cp and as PSTAT/QREF
    # (QREF is the total head). Those are two encodings of one pressure, so
    #     p/p0 = (q/p0)*Cp + p_inf/p0
    # and a least-squares fit of PSTAT/QREF against Cp must return the
    # ISENTROPIC slope and intercept at the case's own Mach number. That is a
    # strong check: it confirms the min/max denormalisation AND recovers the
    # free-stream Mach number from the tap data alone.
    xs = [cp for _, ps, cp in upper + lower if ps is not None]
    ys = [ps for _, ps, cp in upper + lower if ps is not None]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    slope = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) \
        / sum((a - mx) ** 2 for a in xs)
    icept = my - slope * mx
    resid = max(abs(b - (slope * a + icept)) for a, b in zip(xs, ys))
    p0_ratio = (1 + 0.5 * (gam - 1) * M * M) ** (gam / (gam - 1))
    slope_exact, icept_exact = 0.5 * gam * M * M / p0_ratio, 1.0 / p0_ratio
    assert abs(slope / slope_exact - 1) < 0.01, (slope, slope_exact)
    assert abs(icept / icept_exact - 1) < 0.01, (icept, icept_exact)
    print("CHECK Cp/PSTAT affine map over %d taps: fitted slope %.6f against "
          "isentropic q/p0 %.6f (%+.2f%%), fitted intercept %.6f against "
          "p_inf/p0 %.6f (%+.2f%%) -- OK"
          % (n, slope, slope_exact, 100 * (slope / slope_exact - 1),
             icept, icept_exact, 100 * (icept / icept_exact - 1)))
    # The scatter about that map is 2.1e-3 in p/p0, largest and smoothly
    # varying over the aft upper surface, so the two columns were not reduced
    # with one constant QREF. The tape's own item 10 records a free-stream
    # Mach variation of +/- 0.002 during a pressure scan, which is enough to
    # account for it. Recorded, not asserted on: the Cp column is the primary
    # quantity and is what this repository uses.
    print("       residual scatter about that map: %.2e in p/p0 "
          "(recorded, not gated)" % resid)

    # ---- CHECK 3: geometry, two independent NASA transcriptions.
    tape = tape_ordinates()
    yu, yl = nparc_surface("nparc_yu.pts"), nparc_surface("nparc_yl.pts")
    assert len(yu) == len(yl) == len(tape) == 65, (len(yu), len(yl), len(tape))
    dx = max(abs(t[0] - u[0]) for t, u in zip(tape, yu))
    # tape column 4 is yus/c(design); column 5 is yls/c(design) stored as the
    # magnitude BELOW the chord line, so it is the negative of the NPARC value.
    du = max(abs(t[3] - u[1]) for t, u in zip(tape, yu) if t[3] is not None)
    dl = max(abs(t[4] + l[1]) for t, l in zip(tape, yl) if t[4] is not None)
    quantum = 6.29e-6
    assert dx < 1e-4 and du < quantum and dl < quantum, (dx, du, dl)
    thickness = max(u[1] - l[1] for u, l in zip(yu, yl))
    print("CHECK geometry, NPARC against tape design ordinates: "
          "max |dx|=%.1e, |dy_upper|=%.1e, |dy_lower|=%.1e "
          "(tape quantum %.1e) -- OK" % (dx, du, dl, quantum))
    print("CHECK section thickness %.3f%% chord (RAE 2822 is a 12.1%% "
          "section) -- OK" % (thickness * 100))
    assert 0.120 < thickness < 0.123
    assert yu[0] == (0.0, 0.0) and abs(yu[-1][0] - 1.0) < 1e-9

    header = (
        "# RAE 2822 aerofoil, AGARD AR-138 Case 9\n"
        "# Cook, P.H., McDonald, M.A., Firmin, M.C.P., AGARD AR-138 (1979),\n"
        "# RAE 2.438 x 1.829 m slotted tunnel, Farnborough, May 1979.\n"
        "# Digitised transcription: AFOSR-HTTM/Stanford flow 8621 (evaluator\n"
        "# R. E. Melnik, 1981), hosted by the NASA Turbulence Modeling\n"
        "# Resource, https://tmbwg.github.io/turbmodels/Bradshaw/d2/f8621.txt\n"
        "# Conditions as recorded ON THE TAPE:\n"
        "#   free-stream Mach (uncorrected)  = %.3f\n"
        "#   geometric angle of attack       = %.2f deg\n"
        "#   CORRECTED angle of attack       = %.2f deg\n"
        "#   Reynolds number (chord)         = %.4g\n"
        "#   transition trip at x/c          = %.2f\n"
        "#   measured CN = %.4f, CM = %+.4f, CD = %.4f\n"
        "# Quoted tap uncertainty (tape item 10): Cp to within +/- 0.0026 at\n"
        "# Re = 6.5e6.\n"
        % (c9["Mach"], c9["alpha_geometric"], c9["alpha_corrected"],
           c9["Re"], c9["trip_x_over_c"], c9["CN"], c9["CM"], c9["CD"]))

    for name, prof in (("upper", upper), ("lower", lower)):
        path = HERE / f"rae2822_case9_cp_{name}.dat"
        with path.open("w") as fh:
            fh.write(header)
            fh.write("# %d taps\n# x/c            Cp\n" % len(prof))
            for x, _ps, cp in prof:
                fh.write("%.6f  %+.6f\n" % (x, cp))
        print("wrote %s (%d taps)" % (path.name, len(prof)))

    path = HERE / "rae2822_coordinates.dat"
    with path.open("w") as fh:
        fh.write("# RAE 2822 design section ordinates, 65 stations per surface.\n"
                 "# Source: NPARC Alliance Validation Archive yu.pts / yl.pts,\n"
                 "# https://www.grc.nasa.gov/www/wind/valid/raetaf/ , which\n"
                 "# transcribe AGARD AR-138 Table 6.1. Cross-checked against the\n"
                 "# AFOSR-HTTM flow 8621 tape's own design ordinates to %.1e chord.\n"
                 "# Maximum thickness %.4f chord.\n"
                 "# x/c            y_upper/c        y_lower/c\n"
                 % (max(du, dl), thickness))
        for (xu, u), (xl, l) in zip(yu, yl):
            assert abs(xu - xl) < 1e-9
            fh.write("%.6f  %+.7f  %+.7f\n" % (xu, u, l))
    print("wrote %s (%d stations)" % (path.name, len(yu)))


if __name__ == "__main__":
    main()
