
# ---------------------------------------------------------------------------
# A2-GC APPENDED BLOCK -- frozen with
# cases/dafoam/A2_GC_GRID_CONVERGENCE_PREREGISTRATION.md.
#
# Everything above this line is the PRISTINE runScript_AeroOnly.py
# (md5 2906d52a5dbed2bacbaeaf85a37d3fe8), byte for byte. The full diff is
# written to driver_vs_pristine.diff beside every level so the departure is
# on the record and can be read as a diff.
#
# Invoked as --task=run_model, so the pristine chain has already run one
# primal at aoa0 = 4.0 by the time control reaches here. That primal is the
# warm start for the trim and it is budgeted.
#
# What this block does, and nothing else:
#   1. asserts the geometry is the BASELINE (twist = shape = 0) -- this study
#      grades the baseline wing's CD, not the optimised wing's;
#   2. trims INCIDENCE to CL = 0.5 with the case's OWN trim routine, the same
#      optFuncs.findFeasibleDesign that produced the published baseline and
#      the A2 decomposition's row B1. FIXED CL, not fixed alpha;
#   3. runs the trimmed primal and emits the level's GC_ lines;
#   4. writes cd_history.json for the GATE I iterative-convergence check.
# ---------------------------------------------------------------------------
import json as _json
import os as _os

import numpy as _np


def _a2gc_emit(line):
    print(line, flush=True)


def _a2gc_level():
    return _os.environ.get("A2GC_LEVEL", "L?")


def _a2gc_main():
    lvl = _a2gc_level()
    rank = MPI.COMM_WORLD.rank

    # --- 1. baseline geometry control -------------------------------------
    tw = _np.asarray(prob.get_val("twist"), dtype=float)
    sh = _np.asarray(prob.get_val("shape"), dtype=float)
    tw_max = float(_np.max(_np.abs(tw))) if tw.size else 0.0
    sh_max = float(_np.max(_np.abs(sh))) if sh.size else 0.0
    if rank == 0:
        _a2gc_emit(f"GC_GEOM {lvl} twist_absmax {tw_max:.12e} shape_absmax {sh_max:.12e}")
    if max(tw_max, sh_max) > 1e-12:
        # A study of the BASELINE wing that silently ran the optimised one
        # would be a wrong answer that looks right. Refuse instead.
        raise RuntimeError(
            f"A2GC REFUSE: geometry is not the baseline "
            f"(|twist|max {tw_max:.3e}, |shape|max {sh_max:.3e})")

    # --- 2. trim incidence to fixed CL ------------------------------------
    optFuncs.findFeasibleDesign(
        ["scenario1.aero_post.CL"], ["patchV"],
        targets=[CL_target], designVarsComp=[1])
    prob.run_model()

    CD = float(prob.get_val("scenario1.aero_post.CD")[0])
    CL = float(prob.get_val("scenario1.aero_post.CL")[0])
    aoa = float(_np.asarray(prob.get_val("patchV"), dtype=float)[1])

    # --- 3. iterative-convergence history for GATE I ----------------------
    # Source: the stock OpenFOAM forceCoeffs functionObject, written every
    # SIMPLE iteration by the trimmed primal. Its Cd uses its own reference
    # area, so the series is rescaled by the ratio of final values onto
    # DAFoam's CD -- a pure unit conversion, which leaves the SWING in the
    # same units as the level-to-level difference the gate compares it with.
    # The rescale factor is asserted into [0.5, 2.0]; outside that the two
    # coefficients are not the same quantity and the history is DISCARDED
    # (empty), which makes GATE I NOT A RESULT rather than silently passed.
    hist = []
    if rank == 0:
        raw = []
        for base, _dirs, files in _os.walk("postProcessing"):
            for fn in files:
                if fn.startswith("coefficient") and fn.endswith(".dat"):
                    for ln in open(_os.path.join(base, fn), errors="replace"):
                        if ln.startswith("#"):
                            continue
                        parts = ln.split()
                        if len(parts) > 2:
                            try:
                                raw.append(float(parts[1]))
                            except ValueError:
                                pass
        if raw and abs(raw[-1]) > 1e-12:
            factor = CD / raw[-1]
            _a2gc_emit(f"GC_HISTSCALE {lvl} factor {factor:.9f} n {len(raw)}")
            if 0.5 <= factor <= 2.0:
                hist = [v * factor for v in raw]
                hist[-1] = CD          # G-HIST: the last sample IS the reported CD
        _json.dump(hist, open("cd_history.json", "w"))

    # --- 4. emit ----------------------------------------------------------
    # The residual and y+ readers are NOT here. PYDAFOAM on this image exposes
    # only calcPrimalResidualStatistics and getResiduals (probed read-only,
    # 2026-09-01); getResidualNorm and getyPlus DO NOT EXIST and an earlier
    # draft of this block guessed at them. GC_RESID is emitted by the shell
    # stage from the solver's OWN printed per-equation residual lines, using
    # the parser already proven on the A2 decomposition
    # (cases/dafoam/grade_a2_decomposition.py:32-34), and GC_YPLUS likewise
    # from the stock OpenFOAM yPlus functionObject output.
    if rank == 0:
        _a2gc_emit(f"GC_RESULT {lvl} CD {CD:.11f} CL {CL:.11f} AoA {aoa:.11f}")


if args.task == "run_model":
    _a2gc_main()
