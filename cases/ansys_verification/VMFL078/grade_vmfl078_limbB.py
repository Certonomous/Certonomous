#!/usr/bin/env python3
"""
VMFL078 LIMB B -- agreement with the Ansys Fluid Dynamics Verification Manual.

Limb A (our own r = 2 grid-convergence property) was graded by the FROZEN comparator
grade_vmfl078.py, blob c749c87d0f465a829a8485556b0c358c55125850.  That file is NOT
touched, NOT edited and NOT re-run here; this comparator IMPORTS it so that limb B
reads the solver output through THE SAME FROZEN READER as limb A did.

Limb B was BLOCKED because the manual prints no scalar for VMFL078: its entire
published result is Figure .78.2 (printed p.224 / PDF p.238).  This comparator grades
against a band digitised from that figure and frozen in
VMFL078_LIMB_B_PREREGISTRATION.md -- and duplicated as literals below, so the gate
survives the loss of any data file.

THE BAND CONTAINS NO SOLVER OUTPUT.  Every number in BAND came from the bitmap and
from the figure's own uncertainty model; see the pre-registration section 4.

Verdicts: PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING only.
Exit 0 = graded (PASS or GATE FAIL).  Exit 2 = REFUSED (BLOCKED / NOT A RESULT):
this comparator refuses, it never degrades.
"""
import hashlib, json, os, shutil, sys, tempfile, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FROZEN_BLOB = "c749c87d0f465a829a8485556b0c358c55125850"
BAND_TABLE  = os.path.join(HERE, "figure_78_2", "limbB_band_table.json")
DIGITISED   = os.path.join(HERE, "figure_78_2", "fig_78_2_digitised.json")
GRADE_LEVEL = "L3"                       # the FINEST level; the Richardson extrapolate
                                         # is deliberately NOT used -- it would import
                                         # limb A's fitted order into limb B.
PLANT       = 1.234e-03                  # m/s, planted into the REAL bytes on disk
PLANT_MIN   = 1.0e-12

BAND = (
    (  9, 0.04955000, -0.219074, 0.026956),   # target y = 0.05
    ( 19, 0.09905000, -0.268669, 0.015580),   # target y = 0.10
    ( 29, 0.14855000, -0.247146, 0.017144),   # target y = 0.15
    ( 39, 0.19805000, -0.201566, 0.021337),   # target y = 0.20
    ( 49, 0.24755000, -0.151656, 0.020292),   # target y = 0.25
    ( 60, 0.30200000, -0.105835, 0.018298),   # target y = 0.30
    ( 70, 0.35150000, -0.072230, 0.015797),   # target y = 0.35
    ( 80, 0.40100000, -0.049907, 0.015731),   # target y = 0.40
    ( 90, 0.45050000, -0.031800, 0.015849),   # target y = 0.45
    (100, 0.50000000, -0.014191, 0.015675),   # target y = 0.50
    (110, 0.54950000, -0.000797, 0.015691),   # target y = 0.55
    (120, 0.59900000, +0.017061, 0.015696),   # target y = 0.60
    (130, 0.64850000, +0.029707, 0.016547),   # target y = 0.65
    (140, 0.69800000, +0.048313, 0.015585),   # target y = 0.70
    (151, 0.75245000, +0.070635, 0.015744),   # target y = 0.75
    (161, 0.80195000, +0.095123, 0.018303),   # target y = 0.80
    (171, 0.85145000, +0.124209, 0.015896),   # target y = 0.85
    (181, 0.90095000, +0.163260, 0.021784),   # target y = 0.90
)
# ---- frozen aggregate gates (section 5 of the pre-registration) ----------------
U_RMS95     = 0.017917      # m/s, RMS of the 18 U95 above
B2_MIN_IN   = 16            # of 18, at a k = 2 coverage ~5 percent are expected out
UMIN_REF    = -0.268700     # m/s, digitised minimum of the reference series
UMIN_U95    = 0.015600      # m/s
YMIN_REF    = 0.098500      # m, its abscissa
YMIN_U95    = 0.033600      # m, half the span over which the curve stays within U95
                            # of its own minimum -- the figure cannot locate it better
UMIN_WINDOW = (0.05, 0.20)  # search window for the extremum, frozen


def refuse(msg):
    print("REFUSED: %s" % msg)
    print("VERDICT: BLOCKED")
    sys.exit(2)


def sha_file(p):
    b = open(p, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def main():
    if len(sys.argv) < 2:
        refuse("usage: grade_vmfl078_limbB.py <run_root>")
    root = os.path.abspath(sys.argv[1])

    # -- 1. the frozen limb-A comparator must be the file that ran ---------------
    fz = os.path.join(HERE, "grade_vmfl078.py")
    if sha_file(fz) != FROZEN_BLOB:
        refuse("grade_vmfl078.py hashes %s, registered %s -- the frozen reader has "
               "changed underneath limb B" % (sha_file(fz), FROZEN_BLOB))
    import grade_vmfl078 as A

    # -- 2. the band file must agree with the literals above --------------------
    if not os.path.isfile(BAND_TABLE):
        refuse("band table absent: %s" % BAND_TABLE)
    tab = json.load(open(BAND_TABLE))
    if len(tab) != len(BAND):
        refuse("band table has %d rows, comparator frozen at %d" % (len(tab), len(BAND)))
    for r, (k, y, ur, uu) in zip(tab, BAND):
        if (r["probe_index"] != k or abs(r["y"] - y) > 1e-9
                or abs(r["u_ref_mps"] - ur) > 1e-9 or abs(r["U95_mps"] - uu) > 1e-9):
            refuse("band table row %s disagrees with the frozen literal" % r)

    # -- 3. the abscissae must be the frozen ones -------------------------------
    ab = A.frozen_abscissae()
    if len(ab) != A.N_PROBE:
        refuse("frozen abscissae count %d" % len(ab))
    for k, y, _ur, _uu in BAND:
        if abs(ab[k] - y) > 1e-9:
            refuse("probe index %d sits at %.9f, band frozen at %.9f" % (k, ab[k], y))

    # -- 4. level completion, and the probe file -------------------------------
    lvl = os.path.join(root, GRADE_LEVEL)
    if not os.path.isdir(lvl):
        refuse("level directory absent: %s" % lvl)
    rcf = os.path.join(root, "RUN_RC.%s" % GRADE_LEVEL)
    if not os.path.isfile(rcf):
        refuse("RUN_RC.%s absent" % GRADE_LEVEL)
    rctxt = open(rcf, errors="replace").read()
    if "rc=0" not in rctxt.replace(" ", ""):
        refuse("RUN_RC.%s does not record rc=0" % GRADE_LEVEL)
    p = A.probe_path(lvl)
    ux = A.read_probe_ux(p)              # THE FROZEN READER

    # -- 5. PLANTED-ZERO CONTROL, on the real bytes, in a COPY ------------------
    #       (the graded tree is never written to)
    work = tempfile.mkdtemp(prefix="vmfl078_limbB_plant_")
    try:
        shutil.copytree(os.path.join(lvl, "postProcessing"),
                        os.path.join(work, "postProcessing"))
        pw = A.probe_path(work)
        base = A.read_probe_ux(pw)
        tgt = BAND[len(BAND) // 2][0]

        # P1a: a single-probe plant must be SEEN, at that index, at exactly its size
        A.plant_into_probe(pw, PLANT, indices={tgt})
        seen = A.read_probe_ux(pw)
        if abs((seen[tgt] - base[tgt]) - PLANT) > 1e-9:
            refuse("PLANT P1a: planted %.6e at probe %d, the gate reader saw %.6e"
                   % (PLANT, tgt, seen[tgt] - base[tgt]))
        for i in range(len(base)):
            if i != tgt and abs(seen[i] - base[i]) > PLANT_MIN:
                refuse("PLANT P1a: unplanted probe %d moved -- the plant leaked" % i)

        # P1b: the GATE FUNCTIONAL itself must move
        rms0 = rms_delta(base)
        rms1 = rms_delta(seen)
        if abs(rms1 - rms0) <= PLANT_MIN:
            refuse("PLANT P1b: a %.6e plant moved the limb-B RMS by %.3e -- the gate "
                   "is blind" % (PLANT, rms1 - rms0))
    finally:
        shutil.rmtree(work, ignore_errors=True)

    # -- 6. the gates ----------------------------------------------------------
    rows = []
    for k, y, ur, uu in BAND:
        d = ux[k] - ur
        rows.append(dict(probe_index=k, y=y, u_ours=ux[k], u_ref=ur,
                         delta=d, U95=uu, inside=bool(abs(d) <= uu)))
    rmsd = rms_delta(ux)
    n_in = sum(1 for r in rows if r["inside"])
    imax = max(rows, key=lambda r: abs(r["delta"]))

    b1 = rmsd <= U_RMS95
    b2 = n_in >= B2_MIN_IN

    lo, hi = UMIN_WINDOW
    win = [(ab[i], ux[i]) for i in range(len(ux)) if lo <= ab[i] <= hi]
    if not win:
        refuse("extremum window %s contains no frozen abscissa" % (UMIN_WINDOW,))
    ymin_o, umin_o = min(win, key=lambda t: t[1])
    b3u = abs(umin_o - UMIN_REF) <= UMIN_U95
    b3y = abs(ymin_o - YMIN_REF) <= YMIN_U95
    b3 = b3u and b3y

    verdict = "PASS" if (b1 and b2 and b3) else "GATE FAIL"
    failed = [n for n, ok in (("B1", b1), ("B2", b2), ("B3", b3)) if not ok]

    print("VMFL078 LIMB B -- agreement with VM2026R1 Figure .78.2 (printed p.224)")
    print("  graded level          : %s   (finest of the r = 2 family)" % GRADE_LEVEL)
    print("  probe file            : %s" % p)
    print("  frozen reader blob    : %s  VERIFIED" % FROZEN_BLOB)
    print("  planted-zero control  : PASSED (P1a single probe, P1b gate functional)")
    print()
    print("   y_probe      u_ours      u_ref      delta      U95     in")
    for r in rows:
        print("  %9.5f  %+9.6f  %+9.6f  %+9.6f  %8.6f   %s"
              % (r["y"], r["u_ours"], r["u_ref"], r["delta"], r["U95"],
                 "yes" if r["inside"] else "NO"))
    print()
    print("  B1 RMS(delta) = %.6f m/s   band %.6f   -> %s" % (rmsd, U_RMS95, "PASS" if b1 else "GATE FAIL"))
    print("  B2 inside     = %d of %d          min %d      -> %s" % (n_in, len(rows), B2_MIN_IN, "PASS" if b2 else "GATE FAIL"))
    print("  B3 u_min      = %+.6f m/s at y = %.5f" % (umin_o, ymin_o))
    print("     band       = %+.6f +- %.6f  at  %.5f +- %.5f -> %s"
          % (UMIN_REF, UMIN_U95, YMIN_REF, YMIN_U95, "PASS" if b3 else "GATE FAIL"))
    print("  worst point   : y = %.5f, delta = %+.6f m/s (U95 %.6f)"
          % (imax["y"], imax["delta"], imax["U95"]))
    print()
    print("VERDICT: %s" % verdict)
    if failed:
        print("FAILED GATES: %s" % ", ".join(failed))

    out = dict(case="VMFL078", limb="B", verdict=verdict, failed_gates=failed,
               graded_level=GRADE_LEVEL, probe_file=p, frozen_reader_blob=FROZEN_BLOB,
               rms_delta_mps=rmsd, U_RMS95_mps=U_RMS95, B1=b1,
               n_inside=n_in, n_points=len(rows), B2_min_inside=B2_MIN_IN, B2=b2,
               u_min_ours_mps=umin_o, y_min_ours_m=ymin_o,
               u_min_ref_mps=UMIN_REF, u_min_U95=UMIN_U95,
               y_min_ref_m=YMIN_REF, y_min_U95=YMIN_U95, B3=b3,
               worst_point=imax, points=rows,
               planted_zero_control="PASSED",
               reference=("Jifei Wang and Decheng Wan, Parallel Simulation of 3D "
                          "Lid-driven Cubic Cavity Flows by Finite Element Method, "
                          "Proc. 21st (2011) ISOPE, Maui, Hawaii, June 19-24 2011 -- "
                          "as cited BY THE MANUAL for VMFL078"),
               figure="VM2026R1 Figure .78.2, printed p.224 / PDF p.238")
    dest = os.path.join(root, "GRADE_VMFL078_LIMB_B.json")
    json.dump(out, open(dest, "w"), indent=1)
    print("wrote %s" % dest)
    return 0


def rms_delta(ux):
    acc = 0.0
    for k, _y, ur, _uu in BAND:
        acc += (ux[k] - ur) ** 2
    return math.sqrt(acc / len(BAND))


if __name__ == "__main__":
    sys.exit(main())
