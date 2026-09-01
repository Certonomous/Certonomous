#!/usr/bin/env python3
r"""Curriculum D19O -- the instrument's own controls.

WHAT THIS SUITE CAN AND CANNOT DO, STATED FIRST SO NOBODY OVERREADS IT.
`d19o_xf.py` needs `mphys`, `dafoam`, `pygeo` and `idwarp`, NONE of which are
importable outside the containers.  So this suite drives:

  * the PURE functions -- `plateau_reading`, `aggregate_excl_flagged`,
    `rel_pct`, `plant_relative`, `is_excluded`, and the WRITERS
    `build_fd_step` / `build_fd_row` / `build_ctrl_row`;
  * the PRODUCER HEADER path -- the md5 pins, the anchor count, and the fact
    that the header COMPILES;
  * the AST of `d19o_xf.py` itself, for the structural claims the pre-registration
    makes about it.

IT DOES NOT PROVE THE MODEL BUILDS IN-CONTAINER.  The first `O` arm is the first
real test of the producer.  That residual is named in PREREGISTRATION.md
section 15 and is not papered over here.

THE FIXTURES ARE BUILT BY THE INSTRUMENT'S OWN WRITERS.  Not by this file's idea
of their shape.  See `d19o_xf.py`'s writer block for why.
"""
import ast
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d19o_xf as XF                                              # noqa: E402

FAILED = []


def unit(name, want, got, note=""):
    good = (got == want)
    if not good:
        FAILED.append(name)
    print("  %-16s expect=%-30s got=%-30s %s%s"
          % (name, str(want)[:30], str(got)[:30],
             "OK" if good else "**FAILED**", (" " + note) if note else ""))
    return good


# ---- the REAL measured numbers this item stands on, re-read from D19R's -------
# ---- artefacts at this freeze.  Cited by path so a reader can re-read them. ---
D19R = ("/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-subsonic-plateau")
ADJ_CD_SHAPE = [                       # X2/d19r_X.json -> adjoint.CD.shape
    -0.007221766503489129, -0.01890856088367068, 0.007285025342493189,
    0.0092905364130168, 0.038760188097227685, 0.04092612805123831,
    -0.014133812719678937, -0.00020994801762558475]
ADJ_CD_PATCHV1 = 0.001959450045064941
FD_S1_CD = {                           # S1/d19r_S1.json -> rows[].fd["0.001"].dCD
    ("shape", 0): -0.007216903056488089,
    ("shape", 3): 0.00929699881902727,
    ("shape", 6): -0.014128564295353904,
    ("shape", 7): -0.00020653694659047983,
    ("patchV", 1): 0.001959838476149958}
# S8/d19r_S.json -> rows[shape,7].fd -> dCD, the eight-level sweep
SWEEP_SHAPE7_CD = {3.0e-2: -1.473204985447e-04, 1.0e-2: -2.089091733992e-04,
                   3.0e-3: -2.095615056115e-04, 1.0e-3: -2.064883285469e-04,
                   3.0e-4: -1.946174071898e-04, 1.0e-4: -1.630004736741e-04,
                   3.0e-5: -4.984349414687e-05, 1.0e-5: 2.519174480131e-04}
SWEEP_SHAPE6_CD = {1.0e-2: -1.366191351622e-02, 1.0e-3: -1.413312640519e-02,
                   1.0e-4: -1.418221271976e-02}


def _fd_from_dcd(dcd, step, cd0=0.014600274357917864, cl0=0.42288451566070906,
                 dcl=1.0):
    """Invert a derivative into the (plus, minus) pair the WRITER consumes, so
    the fixture enters through the same door the real run does."""
    return (cd0 + dcd * step, cd0 - dcd * step, cl0 + dcl * step, cl0 - dcl * step)


def main():
    print("D19O INSTRUMENT SELFTEST")
    print("  d19o_xf.py                : %s" % XF.md5_of(os.path.join(HERE, "d19o_xf.py")))
    print("  producer pin (registered) : %s" % XF.PRODUCER_MD5)
    print()

    # ================= A. THE PRODUCER HEADER =================================
    print("A. THE FROZEN PRODUCER HEADER")
    prod = os.path.join(HERE, XF.PRODUCER)
    unit("A1-exists", True, os.path.isfile(prod))
    unit("A2-producer-md5", XF.PRODUCER_MD5, XF.md5_of(prod),
         "(the pin is the file, not a memory of it)")
    src = open(prod).read()
    unit("A3-anchor-once", 1, src.count(XF.ANCHOR))
    import hashlib
    header = src.split(XF.ANCHOR)[0]
    unit("A4-header-md5", XF.HEADER_MD5_SHARED_WITH_D15,
         hashlib.md5(header.encode()).hexdigest(),
         "(byte-identical to D15's -- the reproduction claim rests on it)")
    unit("A5-header-bytes", 7614, len(header.encode()))
    try:
        compile(header, XF.PRODUCER, "exec")
        compiled = True
    except SyntaxError:
        compiled = False
    unit("A6-header-compiles", True, compiled,
         "(compiles; it is NOT executed here -- dafoam is not importable on the host)")
    # The header must NOT carry the driver, or the registered optimiser settings
    # would live in two places and could drift apart.
    unit("A7-no-driver-in-header", False, "pyOptSparseDriver" in header,
         "(max_iter/tol live in d19o_xf.py ALONE and are pinned with it)")
    unit("A8-solver", True, '"solverName": "DARhoSimpleFoam"' in header)
    unit("A9-U0", True, "U0 = 100.0" in header)
    unit("A10-T0", True, "T0 = 300.0" in header)
    unit("A11-CLtarget", True, "CL_target = 0.5" in header)

    # ================= B. THE `shape[7]` REGISTRATION =========================
    print()
    print("B. THE REGISTERED NON-RESULT -- shape[7] IS EXCLUDED BY NAME, NOT BY VALUE")
    unit("B1-excluded", True, XF.is_excluded("shape", 7))
    unit("B2-others-not", [False] * 4,
         [XF.is_excluded(*c) for c in (("shape", 0), ("shape", 3), ("shape", 6),
                                       ("patchV", 1))])
    unit("B3-only-one", 1, len(XF.EXCLUDED_FROM_AGGREGATE))
    # THE LEG THAT MATTERS: at s* shape[7] AGREES to 1.65 %, well inside band D.
    # It is STILL excluded, because the exclusion is registered and not measured.
    agree = XF.rel_pct(ADJ_CD_SHAPE[7], FD_S1_CD[("shape", 7)])
    print("     shape[7] adjoint-vs-FD at s*=1e-3, np=1 : %.5f %% (band D = %.1f %%)"
          % (agree, XF.FD_BAND_PCT))
    unit("B4-inside-band", True, agree < XF.FD_BAND_PCT,
         "(it PASSES band D and is excluded ANYWAY -- see B5)")
    unit("B5-not-rescued", True, XF.is_excluded("shape", 7),
         "(a good number CANNOT rescue it: what is missing is the PLATEAU)")

    # ================= C. THE PLATEAU RULE IS D19R's, UNCHANGED ===============
    print()
    print("C. THE DECADE PLATEAU RULE -- G19R-1b's, re-driven on D19R's OWN sweep bytes")
    unit("C1-tol", 10.0, XF.PLATEAU_TOL_PCT, "(identical to G19R-1b)")
    unit("C2-decade-shape", [1.0e-2, 1.0e-3, 1.0e-4], XF.FD_STEPS_ENDPOINT["shape"],
         "(s* with its DECADE neighbours -- a half-decade bracket would be WEAKER)")
    unit("C3-decade-patchV", [1.0e-1, 1.0e-2, 1.0e-3], XF.FD_STEPS_ENDPOINT["patchV"])
    unit("C4-sstar-is-centre", XF.S_STAR["shape"], XF.FD_STEPS_ENDPOINT["shape"][1])
    unit("C5-sstar-patchV", XF.S_STAR["patchV"], XF.FD_STEPS_ENDPOINT["patchV"][1])

    # Drive the reader on D19R's REAL shape[7] sweep and require it to reproduce
    # the selector's own published number, 21.060684242435336 %.
    per = {s: _fd_from_dcd(SWEEP_SHAPE7_CD[s], s)
           for s in XF.FD_STEPS_ENDPOINT["shape"]}
    r7 = XF.build_fd_row("shape", 7, per)
    p7 = r7["plateau_CD"]
    print("     shape[7]/CD  coarse=%.6f %%  fine=%.6f %%  two_sided=%s"
          % (p7["coarse_pct"], p7["fine_pct"], p7["two_sided"]))
    unit("C6-reproduces", "21.060684", "%.6f" % p7["fine_pct"],
         "(D19R's selector published 21.060684242435336 -- reproduced independently)")
    unit("C7-coarse", "1.172388", "%.6f" % p7["coarse_pct"],
         "(D19R published 1.1723882261986174)")
    unit("C8-not-two-sided", False, p7["two_sided"], "(THE PLATEAU DOES NOT CLOSE)")
    unit("C9-row-flagged", True, r7["registered_non_result"])

    # The GREEN contrast: shape[6], the flat sibling, on the same reader.
    per6 = {s: _fd_from_dcd(SWEEP_SHAPE6_CD[s], s) for s in XF.FD_STEPS_ENDPOINT["shape"]}
    r6 = XF.build_fd_row("shape", 6, per6)
    p6 = r6["plateau_CD"]
    print("     shape[6]/CD  coarse=%.6f %%  fine=%.6f %%  two_sided=%s"
          % (p6["coarse_pct"], p6["fine_pct"], p6["two_sided"]))
    unit("C10-green", True, p6["two_sided"],
         "(the reader CAN return two_sided=True -- it is not stuck on False)")
    unit("C11-not-flagged", False, r6["registered_non_result"])

    # ================= D. THE AGGREGATE EXCLUDES BY NAME ======================
    print()
    print("D. THE AGGREGATE IS OVER FOUR COMPONENTS AND ITS KEY NAME SAYS SO")
    keep = [c for c in XF.COMPONENTS if not XF.is_excluded(*c)]
    unit("D1-four", 4, len(keep))
    idx = {("shape", i): ADJ_CD_SHAPE[i] for i in range(8)}
    idx[("patchV", 1)] = ADJ_CD_PATCHV1
    pairs_keep = [(idx[c], FD_S1_CD[c]) for c in keep]
    pairs_all = [(idx[c], FD_S1_CD[c]) for c in XF.COMPONENTS]
    a_keep = XF.aggregate_excl_flagged(pairs_keep)
    a_all = XF.aggregate_excl_flagged(pairs_all)
    print("     aggregate EXCL flagged (4 components) : %.6f %%" % a_keep)
    print("     aggregate INCL shape[7] (5, NOT USED) : %.6f %%" % a_all)
    unit("D2-differ", True, abs(a_keep - a_all) > 1e-9,
         "(the exclusion CHANGES the number -- it is not decorative)")
    unit("D3-in-band", True, a_keep < XF.AGG_BAND_PCT)
    unit("D4-empty-is-none", None, XF.aggregate_excl_flagged([]))
    unit("D5-zero-den-is-none", None, XF.aggregate_excl_flagged([(1.0, 0.0)]),
         "(a zero denominator returns None, never a spurious 0 or inf)")

    # ================= E. THE PLANTED CONTROL, BOTH LEGS ======================
    print()
    print("E. THE RELATIVE PLANT (CLAUDE.md rule 3), BUILT BY THE REAL WRITER")
    cd0 = 0.014600274357917864
    ctrl = XF.build_ctrl_row(cd0, 0.42288451566070906)
    unit("E1-zero-is-zero", 0.0, float(ctrl["fd"][repr(XF.CTRL_STEP)]["dCD"]))
    unit("E2-crosses", True, ctrl["planted"]["crosses_band"],
         "(K=%.1f moves %s pp against a %.1f pp band)"
         % (XF.PLANT_K, ctrl["planted"]["moved_pp"], XF.FD_BAND_PCT))
    unit("E3-red-leg", False, ctrl["planted_shrunk"]["crosses_band"],
         "(K=%.1f moves %s pp and must NOT cross -- the SO-2M lesson)"
         % (XF.PLANT_K_SHRUNK, ctrl["planted_shrunk"]["moved_pp"]))
    unit("E4-formula", 25.0, float(ctrl["planted"]["moved_pp"]),
         "(K x band = 5.0 x 5.0 = 25.0 pp, BY CONSTRUCTION, at any scale)")
    # The plant is scale-free: the same K must cross at a reference three orders
    # smaller.  SO-2M died because an ABSOLUTE plant did not.
    small = XF.build_ctrl_row(2.0648832854686106e-05, 0.4)
    unit("E5-scale-free", 25.0, float(small["planted"]["moved_pp"]),
         "(same pp move on a reference 1000x smaller)")

    # ================= F. THE TRIVIAL BASELINE (charter section 4) ============
    print()
    print("F. THE CHARTER-4 TRIVIAL BASELINE")
    unit("F1-step", 1.0e-8, XF.TB_STEP)
    unit("F2-max-passing", 1, XF.TB_MAX_PASSING)
    unit("F3-flagged-in-row", True,
         XF.build_fd_step(XF.TB_STEP, 1.0, 1.0, 1.0, 1.0)["is_trivial_baseline"])
    unit("F4-sstar-not-flagged", False,
         XF.build_fd_step(1.0e-3, 1.0, 1.0, 1.0, 1.0)["is_trivial_baseline"])
    # The measured justification: eta at np=1 on this case is 9.652e-11, and the
    # numerator at 1e-8 on a 1e-2 derivative is ~1e-10 -- the same order.
    eta = 9.652218954658842e-11
    numerator = 2.0 * XF.TB_STEP * 1.0e-2
    print("     eta (np=1, MEASURED, D19R S1) = %.6e ; FD numerator at h=%g = %.6e"
          % (eta, XF.TB_STEP, numerator))
    unit("F5-noise-order", True, numerator / eta < 10.0,
         "(the trivial-baseline numerator is within 10x of the noise floor)")

    # ================= G. A NON-FINITE ESTIMATE IS A WRITTEN FAILURE ==========
    print()
    print("G. A FAILED EVALUATION IS WRITTEN, NOT OMITTED")
    inf = float("inf")
    unit("G1-inf-not-ok", False, XF.build_fd_step(1e-3, inf, 0.0, 0.0, 0.0)["ok"])
    nan = float("nan")
    unit("G2-nan-not-ok", False, XF.build_fd_step(1e-3, nan, 0.0, 0.0, 0.0)["ok"])
    unit("G3-good-is-ok", True, XF.build_fd_step(1e-3, 1.0, 0.0, 1.0, 0.0)["ok"])

    # ================= H. STRUCTURAL CLAIMS ABOUT THE INSTRUMENT ==============
    print()
    print("H. THE AST -- the structural claims the pre-registration makes")
    xsrc = open(os.path.join(HERE, "d19o_xf.py")).read()
    tree = ast.parse(xsrc)
    # H1: no `assert` anywhere.  `python3 -O` strips them, so an assert is not a
    # guard (L-332).  Every refusal in this instrument is an explicit exit/Abort.
    n_assert = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Assert))
    unit("H1-no-asserts", 0, n_assert, "(python3 -O strips asserts; L-332)")
    # H1-control: the counter can see a planted assert.  A zero from a reader
    # never shown a non-zero is not evidence (CLAUDE.md rule 3).
    planted = ast.parse(xsrc + "\ndef _planted():\n    assert True\n")
    unit("H1-control", 1,
         sum(1 for n in ast.walk(planted) if isinstance(n, ast.Assert)),
         "(PLANTED assert IS seen -- the counter is not blind)")
    # H2: np is enforced, not requested.
    unit("H2-mpi-abort", True, "MPI.COMM_WORLD.Abort(2)" in xsrc)
    unit("H3-np-required", 1, XF.NP_REQUIRED)
    # H4: the row comes from the .so md5, and there is no -row flag to override it.
    unit("H4-no-row-flag", False, '"-row"' in xsrc,
         "(no flag can stamp a row the toolchain does not prove)")
    unit("H5-two-rows-known", {"PATCHED", "SHIPPED"}, set(XF.ROW_BY_SO_MD5.values()))
    unit("H6-so-md5-count", 2, len(XF.ROW_BY_SO_MD5))
    # H7: the endpoint arms cannot silently fall back to the baseline.
    unit("H7-xopt-required", True, "mode %s needs %s from arm O" in xsrc)
    # H8: the exclusion travels on every record this instrument writes.
    unit("H8-exclusion-travels", 4, xsrc.count('"excluded_from_aggregate":'),
         "(exactly 4: the ONE row writer `row_from_fd`, plus the O, XE and FE "
         "records.  This leg CAUGHT a version in which the FE loop carried its "
         "own copy of the row writer -- two writers that could drift apart.)")
    # H9: the optimiser budget is a budget.
    unit("H9-max-majors", 40, XF.MAX_MAJORS)
    unit("H10-opt-tol", 1.0e-5, XF.OPT_TOL)
    unit("H11-expected-majors", 12, XF.EXPECTED_MAJOR_ROWS)

    print()
    if FAILED:
        print("D19O INSTRUMENT SELFTEST: FAILED -- %d leg(s): %s" % (len(FAILED), FAILED))
        return 1
    print("D19O INSTRUMENT SELFTEST: OK -- every leg driven, every control fired")
    print("RESIDUAL, NAMED: the model is NOT built here.  dafoam/pygeo/idwarp are not")
    print("importable on the host, so the first `O` arm is the first real test of the")
    print("producer.  PREREGISTRATION.md section 15 carries this as R2.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
