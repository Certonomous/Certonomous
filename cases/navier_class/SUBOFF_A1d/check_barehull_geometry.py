#!/usr/bin/env python3
"""
A1d GATE X5 — the bare-hull geometry check, run BEFORE the mesh is solved.

Compares the analytic hull used by the lab's builder against Roddy 1990 Table 2,
"Nondimensional offsets and cross sectional areas for the hull" (DTRC/SHD-1298-08,
report p. 16 / PDF p. 24), transcribed by RENDERING THE PAGE AND READING IT — never
from the OCR text layer, which has already been caught dropping a whole table row
elsewhere in this same report (Table 3, Configuration 3's static-stability row).

Two independent sources must agree before a mesh is admitted:
  (1) Groves 1989 DTRC/SHD-1298-01, the analytic definition, as implemented in
      cases/navier_class/SUBOFF_A1/build_suboff_a1_geometry.py :: hull_R_ft
  (2) Roddy 1990 Table 2, below.

REFUSES (exit 2) rather than degrading. Run with --selftest on any edit to the table.
"""
import sys
import os
import importlib.util

TOL_REL = 0.005          # 0.5 %, the A1d §6 registered tolerance
PLANT = 0.05             # planted perturbation for the refusal control (5 %, >> TOL)

# --- Roddy 1990 Table 2, read from the rendered page at 150 dpi ------------------
# station, B/Bmax, A/Amax          (25 stations, 0.0 .. 20.4167)
RODDY_TABLE2 = [
    (0.0,     0.00000, 0.00000),
    (0.1,     0.29058, 0.08444),
    (0.2,     0.39396, 0.15520),
    (0.3,     0.46600, 0.21715),
    (0.4,     0.52147, 0.27194),
    (0.5,     0.56627, 0.32066),
    (0.6,     0.60352, 0.36424),
    (0.7,     0.63514, 0.40340),
    (1.0,     0.70744, 0.50047),
    (2.0,     0.84713, 0.71763),
    (3.0,     0.94066, 0.88484),
    (4.0,     0.99282, 0.98570),
    (7.7143,  1.00000, 1.00000),
    (10.0,    1.00000, 1.00000),
    (15.1429, 1.00000, 1.00000),
    (16.0,    0.97598, 0.95253),
    (17.0,    0.81910, 0.67093),
    (18.0,    0.55025, 0.30278),
    (19.0,    0.26835, 0.07201),
    (20.0,    0.11724, 0.01375),
    (20.1,    0.11243, 0.01264),
    (20.2,    0.10074, 0.01015),
    (20.3,    0.07920, 0.00628),
    (20.4,    0.03178, 0.00101),
    (20.4167, 0.00000, 0.00000),
]

# --- THE STATION MAPPING, DERIVED AND CHECKED, NEVER ASSERTED -------------------
# Roddy p.3 says forces are "nondimensionalized using the length between
# perpendiculars of 13.9792 feet (4.261 m)". IT IS A TRAP TO REUSE THAT LENGTH FOR
# THE STATION AXIS. The first run of this gate did exactly that (LBP/20 = 0.69896
# ft/station) and reported 8 of 25 stations failing with a 65 % error at the tail,
# which reads convincingly like a truncated stern. IT WAS NOT. The whole signature
# was an artifact of the wrong station unit.
#
# The station axis runs 0 .. 20.4167 over the OVERALL length, not the LBP:
#     L_TOTAL_FT / 20.4167 = 14.291667 / 20.4167 = 0.6999989 ft  ->  0.70 ft exactly.
# derive_station_ft() below takes it from the geometry module and REFUSES if it is
# not 0.70 to within a tight tolerance, so a future geometry edit cannot silently
# move the axis this table is read against.
LBP_FT = 13.9792                 # force nondimensionalisation ONLY. Not the station axis.
STATION_NOSE_TO_TAIL = 20.4167   # last station in Roddy Table 2
STATION_FT_EXPECTED = 0.70
STATION_FT_TOL = 1.0e-5


def derive_station_ft(l_total_ft):
    """Derive ft-per-station from the geometry, and refuse a surprising value."""
    k = l_total_ft / STATION_NOSE_TO_TAIL
    if abs(k - STATION_FT_EXPECTED) > STATION_FT_TOL:
        print("REFUSE: station unit derived as %.7f ft from L_TOTAL_FT=%.6f, but "
              "Roddy Table 2's axis requires %.2f ft/station. The geometry's overall "
              "length and the reference table no longer share an axis, so every "
              "comparison below would be meaningless."
              % (k, l_total_ft, STATION_FT_EXPECTED))
        sys.exit(2)
    return k


def check_table_self_consistency():
    """A/Amax must equal (B/Bmax)^2 for a body of revolution.

    This validates THREE things at once with no external input: that the visual
    transcription above is correct, that the tabulated body really is a body of
    revolution (which A1d's whole plane-equivalence argument rests on), and that
    no digit was transposed. A transcription that passes this by accident is
    vanishingly unlikely across 25 rows.
    """
    bad = []
    for st, b, a in RODDY_TABLE2:
        pred = b * b
        # table is printed to 5 dp, so allow half an ulp of the printed precision
        if abs(pred - a) > 1.0e-5 + 1.0e-9:
            bad.append((st, b, a, pred))
    return bad


def load_hull_R_ft():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.normpath(os.path.join(here, "..", "SUBOFF_A1",
                                        "build_suboff_a1_geometry.py"))
    if not os.path.exists(src):
        print("REFUSE: analytic geometry source not found: %s" % src)
        sys.exit(2)
    spec = importlib.util.spec_from_file_location("a1geom", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.hull_R_ft, mod.RMAX_FT, mod.L_TOTAL_FT, src


def compare(hull_R_ft, rmax, station_ft, perturb_station=None):
    """Return list of (station, roddy_B, ours_B, rel_err) exceeding TOL_REL."""
    fails = []
    for st, b_roddy, _a in RODDY_TABLE2:
        x = st * station_ft
        try:
            r = hull_R_ft(x)
        except Exception as exc:                      # noqa: BLE001
            print("REFUSE: hull_R_ft(%.6f) raised %s" % (x, exc))
            sys.exit(2)
        b_ours = r / rmax
        if perturb_station is not None and abs(st - perturb_station) < 1e-9:
            b_ours += PLANT                            # the plant
        denom = b_roddy if b_roddy > 1.0e-6 else 1.0   # absolute at the two zeros
        rel = abs(b_ours - b_roddy) / denom
        if rel > TOL_REL:
            fails.append((st, b_roddy, b_ours, rel))
    return fails


def main():
    selftest = "--selftest" in sys.argv

    print("A1d GATE X5 — bare-hull geometry vs Roddy 1990 Table 2")
    print("  stations: %d   tolerance: %.2f %%" % (len(RODDY_TABLE2), 100 * TOL_REL))

    # --- self-test 1: the table validates itself -------------------------------
    bad = check_table_self_consistency()
    if bad:
        print("REFUSE: Roddy Table 2 transcription fails A/Amax == (B/Bmax)^2 at:")
        for st, b, a, pred in bad:
            print("   station %-8s B/Bmax=%.5f  A/Amax=%.5f  (B/Bmax)^2=%.5f"
                  % (st, b, a, pred))
        sys.exit(2)
    print("  [ok] transcription self-consistent: A/Amax == (B/Bmax)^2 at all %d "
          "stations (body of revolution confirmed from the table itself)"
          % len(RODDY_TABLE2))

    hull_R_ft, rmax, l_total, src = load_hull_R_ft()
    station_ft = derive_station_ft(l_total)
    print("  analytic source: %s" % src)
    print("  RMAX_FT = %.6f   L_TOTAL = %.6f ft" % (rmax, l_total))
    print("  [ok] station axis DERIVED from geometry: %.7f ft/station "
          "(expected %.2f). LBP %.4f ft is the FORCE length and is NOT used here."
          % (station_ft, STATION_FT_EXPECTED, LBP_FT))

    # --- self-test 2: PLANTED CONTROL (rule 3) ---------------------------------
    # A checker that has not been shown able to FAIL is not evidence that it passed.
    if selftest:
        planted = compare(hull_R_ft, rmax, station_ft, perturb_station=10.0)
        if not any(abs(f[0] - 10.0) < 1e-9 for f in planted):
            print("REFUSE: PLANTED CONTROL DID NOT FIRE. A %.0f%% perturbation at "
                  "station 10.0 was not detected — this checker cannot see a "
                  "geometry error and its PASS is worthless." % (100 * PLANT))
            sys.exit(2)
        print("  [ok] planted control fired: +%.0f%% at station 10.0 was caught"
              % (100 * PLANT))

    # --- the actual comparison -------------------------------------------------
    fails = compare(hull_R_ft, rmax, station_ft)
    if fails:
        print("\nGATE X5 FAIL — %d of %d stations exceed %.2f %%:"
              % (len(fails), len(RODDY_TABLE2), 100 * TOL_REL))
        for st, b_r, b_o, rel in fails:
            print("   station %-8s Roddy B/Bmax=%.5f  ours=%.5f  rel=%.3f %%"
                  % (st, b_r, b_o, 100 * rel))
        print("\nThe mesh is NOT admitted. Per A1d §8 X5 the geometry is rejected "
              "BEFORE it is solved.")
        sys.exit(1)

    print("\nGATE X5 PASS — all %d stations within %.2f %%."
          % (len(RODDY_TABLE2), 100 * TOL_REL))
    return 0


if __name__ == "__main__":
    sys.exit(main())
