#!/usr/bin/env python3
"""Standalone C6.3 probe for the T4d MEDIUM level (T4d_IJ_m).

READ-ONLY MEASUREMENT.  This script does NOT grade the rung, does NOT freeze,
register, launch or commit anything.  It reuses the FROZEN readers UNMODIFIED --
`analyse_t4` (the G-row reader and its planted-zero control) and `analyse_t4d`
(for GRADED, PLANT, FIELD_TOL, scratch_copy, FOAM_BASHRC_DEFAULT) -- editing
NEITHER file.  It never writes into the real case tree: every OpenFOAM sampling
run happens inside a scratch copy that mirrors analyse_t4d.scratch_copy, and the
frozen planted-zero control makes its own scratch copy internally.

Order (CLAUDE.md rule 3 -- planted control FIRST, then the number):
  (b) A.planted_zero_control on the MEDIUM field: plants the registered PLANT,
      reads it back off disk through the same A.sample_profile/A.peak_of path the
      C6.3 quantity uses, and REFUSES (sys.exit 2) if the reader is blind.  A zero
      from a reader not shown able to see a non-zero is not evidence.
  (c) C6.3 on the UNPERTURBED medium: max over the GRADED stations G1/G2/G3 of
      |peak(U/U_bulk) change| between the two latest checkpoints, mirroring
      analyse_t4d.grade lines ~530-536, but on a scratch copy so the case dir is
      never mutated.

Exit: 0 measured, 2 REFUSAL (reader blind, missing checkpoints, or reader
returned nothing).
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyse_t4d as T4D            # FROZEN -- GRADED, PLANT, FIELD_TOL, scratch_copy, bashrc default
import analyse_t4 as A              # FROZEN -- sample_profile, peak_of, two_latest_times, planted_zero_control

BASHRC = T4D.FOAM_BASHRC_DEFAULT
MED = os.path.join(HERE, "T4d_IJ_m")
PLANT = T4D.PLANT                    # = analyse_t4.PLANT = 1.234e-03 (registered planted_control_value)
FIELD_TOL = T4D.FIELD_TOL           # = 2.0e-4 (C6.3 threshold)
GRADED = T4D.GRADED                 # [(id, r_over_D, reference_file, half), ...] for G1/G2/G3


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(2)


def main():
    if not os.path.isdir(MED):
        refuse("no medium case directory %s" % MED)
    tt = A.two_latest_times(MED)
    if tt is None:
        refuse("medium has fewer than two time directories -- no field-change quantity")
    t_prev, t_last = tt
    print("T4d MEDIUM C6.3 probe (read-only).  PLANT=%.6g  FIELD_TOL=%g" % (PLANT, FIELD_TOL))
    print("medium two latest checkpoints: %s -> %s" % (t_prev, t_last))
    print("GRADED stations: " + ", ".join("%s(r/D=%.1f)" % (rid, rd) for rid, rd, _, _ in GRADED))

    # ---- (b) rule-3 planted-zero control on the MEDIUM field, FIRST ----------
    # A.planted_zero_control copies the case to scratch, plants the registered
    # PLANT into an AIMED U cell, re-reads through A.sample_profile/A.peak_of,
    # measures a descending detection floor, and sys.exit(2)s if the reader is
    # blind at the registered plant.  Using it verbatim IS the same mechanism.
    print("\n--- (b) PLANTED-ZERO CONTROL on the medium field (rule 3) ---")
    ctrl = A.planted_zero_control(MED, t_last, BASHRC)     # refuses (exit 2) internally if blind
    if ctrl.get("status") != "PASS":
        refuse("planted-zero control did not PASS: %r" % ctrl)
    print("planted-zero control: PASS")
    print("  registered PLANT               = %.6g" % PLANT)
    print("  recovered max abs change       = %.6g" % ctrl["recovered_max_abs_change"])
    print("  planted line (1-based)         = %d" % ctrl["planted_line"])
    print("  planted cell / station r/D     = %d / %.1f" % (ctrl["planted_cell"], ctrl["station_r_over_D"]))
    print("  aim distance to sampling line  = %.4g m" % ctrl["aim_distance_m"])
    print("  negative arm (identical bytes) = %.17g" % ctrl["negative_arm"])
    print("  demonstrated detection floor   = %g" % ctrl["demonstrated_detection_floor"])
    if not (ctrl["recovered_max_abs_change"] > 0.0):
        refuse("reader recovered a non-positive change from the planted PLANT")

    # ---- (c) C6.3 on the UNPERTURBED medium, in a scratch copy ---------------
    print("\n--- (c) C6.3 on the unperturbed medium (scratch copy; case dir untouched) ---")
    tmp, dst = T4D.scratch_copy(MED, t_last)               # copies constant(hardlink)/system/0/t_last
    try:
        # scratch_copy carries only ONE time dir; C6.3 needs both checkpoints.
        prev_src = os.path.join(MED, str(t_prev))
        prev_dst = os.path.join(dst, str(t_prev))
        if not os.path.isdir(prev_dst):
            shutil.copytree(prev_src, prev_dst)
        per_station = []
        for rid, rd, _reffile, _half in GRADED:
            p0 = A.sample_profile(dst, t_prev, rd, BASHRC)
            p1 = A.sample_profile(dst, t_last, rd, BASHRC)
            if p0 is None or p1 is None:
                refuse("field-change reader returned nothing at %s r/D=%.1f (p0=%r p1=%r)"
                       % (rid, rd, p0 is not None, p1 is not None))
            dch = abs(A.peak_of(p1)[0] - A.peak_of(p0)[0])
            per_station.append((rid, rd, dch))
            print("  %s r/D=%.1f: peak(%s)=%.6f  peak(%s)=%.6f  |change|=%.6g"
                  % (rid, rd, t_prev, A.peak_of(p0)[0], t_last, A.peak_of(p1)[0], dch))
        c63 = max(d for _, _, d in per_station)
        print("\nC6.3 = max over G1/G2/G3 of |peak(U/U_bulk) change| = %.6g" % c63)
        print("threshold FIELD_TOL = %g" % FIELD_TOL)
        verdict = "PASS" if c63 <= FIELD_TOL else "FAIL"
        rel = "<=" if c63 <= FIELD_TOL else ">"
        print("C6.3 %s  (%.6g %s %g)" % (verdict, c63, rel, FIELD_TOL))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
