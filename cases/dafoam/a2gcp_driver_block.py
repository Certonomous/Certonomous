# ---------------------------------------------------------------------------
# A2-GC-P APPENDED BLOCK -- registered by
# cases/dafoam/A2_GC_P_PRIMAL_TRIM_GRID_CONVERGENCE_PREREGISTRATION.md.
#
# Everything above this line is the PRISTINE runScript_AeroOnly.py
# (md5 2906d52a5dbed2bacbaeaf85a37d3fe8), byte for byte. The full diff is
# written to driver_vs_pristine.diff beside every level so the departure is on
# the record and can be read as a diff.
#
# WHAT THIS BLOCK DOES DIFFERENTLY FROM THE PARENT ITEM'S BLOCK, and it is the
# whole point of the successor: optFuncs.findFeasibleDesign is NOT called. That
# routine is a GRADIENT-BASED trim, and the adjoint it needs is what cap-stopped
# the parent (A2_GC_GRID_CONVERGENCE_PREREGISTRATION.md section R3: the cap
# fired INSIDE an adjoint GMRES solve, while the primal work in the same run
# totalled 54.71 s). The graded quantity -- CD at fixed CL -- needs no adjoint.
# Incidence is trimmed by a PRIMAL-ONLY SECANT, ~4 primals, no Jacobian
# colouring, no KSP.
#
# Invoked as --task=run_model, so the pristine chain has already run one primal
# at aoa0 = 4.0 by the time control reaches here. THAT PRIMAL IS EVALUATION 1 of
# the secant, and it is costed as the COLD primal in section 8 of the
# registration -- 0.868 core-s/iteration, 7.65x the warm rate.
#
# Order, and it is not negotiable:
#   0. a2gcp_secant.preflight() -- the rule-3 birth register, BEFORE the first
#      trim evaluation. VERIFICATION_CHARTER section 2j: an instrument that has
#      not answered rule 3's question does not grade;
#   1. assert the geometry is the BASELINE (twist = shape = 0);
#   2. primal-only secant trim of incidence to CL = 0.5;
#   3. ONE graded primal at the trimmed incidence, warm, run to the case's own
#      primalMinResTol with the per-level iteration ceiling. CD/CL/AoA come from
#      THAT primal only;
#   4. re-check the GRADED primal's own CL against the trim tolerance. A miss is
#      BLOCKED -- the trim is NOT re-entered on the graded primal, because
#      re-trimming the run that produces the graded number is tuning the answer.
#
# NO cd_history.json is written and NO forceCoeffs rescale happens. The GATE I
# history is the solver's OWN printed "CD:" lines, which is the identical
# quantity the graded number is read from, so there is nothing to rescale and no
# scaling guard to get wrong (registration section 6.3).
# ---------------------------------------------------------------------------
import json as _json
import os as _os
import sys as _sys

import numpy as _np

_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import a2gcp_secant as _sec        # noqa: E402  -- copied beside this file


def _a2gcp_emit(line):
    print(line, flush=True)


def _a2gcp_level():
    return _os.environ.get("A2GCP_LEVEL", "L?")


def _a2gcp_n_final():
    """The graded primal's SAFETY CEILING, not a plan. Registered at 4,000 on
    every level (pre-registration section 4.1). Buying iterations past DAFoam's
    accept floor buys nothing -- see the note on _set_iterations below. Passed in
    by the launcher so the ceiling and the core-minute cap cannot drift apart."""
    return int(_os.environ["A2GCP_N_FINAL_MAX"])


def _a2gcp_n_trim():
    return int(_os.environ.get("A2GCP_N_TRIM", "1000"))


def _set_iterations(n):
    """Set the primal's SIMPLE iteration ceiling for the next run_model().

    `primalMinResTol` (1.0e-8) and `primalMinResTolDiff` (1e3) are NOT TOUCHED,
    by registration. Their product is DAFoam's accept floor AND its hard-fail
    gate -- 1.0e-5 on this case
    (verification/campaign/A2_ACCEPT_FLOOR_BINDING_FIELD_RULING_2026-09-08.md:74,
    where a standing control freezes it UNMOVED in either direction; and
    cases/dafoam/A3_FD3_PREREGISTRATION.md:16-18, which keeps it deliberately
    loose so an unreachable target "reports a shallow plateau instead of
    fabricating a crash"). Tightening it here to make GATE R reachable would move
    a frozen floor and convert every shallow plateau into a fabricated crash.
    The gate does not move either. Both stay, and section 6.2 of the registration
    predicts the consequence in advance.

    So the ONLY knob touched is the iteration ceiling: controlDict's `endTime`,
    which is the case's own SIMPLE iteration count (`endTime 1000; deltaT 1;` in
    the pristine case).
    """
    with open("system/controlDict") as fh:
        cd = fh.read()
    import re as _re
    cd2 = _re.sub(r"^endTime\s+[\d.eE+-]+;", f"endTime         {int(n)};",
                  cd, count=1, flags=_re.M)
    if cd2 == cd:
        raise RuntimeError(
            "A2GCP REFUSE: could not set endTime in system/controlDict. The "
            "iteration ceiling would be a request, not a limit, and the "
            "registered core-minute cap is derived from it.")
    with open("system/controlDict", "w") as fh:
        fh.write(cd2)


def _a2gcp_main():
    lvl = _a2gcp_level()
    rank = MPI.COMM_WORLD.rank

    # --- 0. rule 3 / section 2j PRECONDITION -------------------------------
    # Runs BEFORE the first trim evaluation. If any reader cannot be shown able
    # to see its plant, this raises and the level exits non-zero: an instrument
    # that has not answered rule 3's question does not grade.
    if rank == 0:
        reg = _sec.preflight()
        _json.dump(reg, open("birth_register.json", "w"), indent=1)
        _a2gcp_emit(
            f"GC_BIRTH {lvl} declared {reg['readers_declared']} born "
            f"{reg['readers_born']} zero_passing {reg['zero_passing_readers']} "
            f"on_real_producer_bytes {reg['readers_on_real_producer_bytes']}")

    # --- 1. baseline geometry control --------------------------------------
    tw = _np.asarray(prob.get_val("twist"), dtype=float)
    sh = _np.asarray(prob.get_val("shape"), dtype=float)
    tw_max = float(_np.max(_np.abs(tw))) if tw.size else 0.0
    sh_max = float(_np.max(_np.abs(sh))) if sh.size else 0.0
    if rank == 0:
        _a2gcp_emit(f"GC_GEOM {lvl} twist_absmax {tw_max:.12e} "
                    f"shape_absmax {sh_max:.12e}")
    if max(tw_max, sh_max) > 1e-12:
        # A study of the BASELINE wing that silently ran the optimised one would
        # be a wrong answer that looks right. Refuse instead.
        raise RuntimeError(
            f"A2GCP REFUSE: geometry is not the baseline "
            f"(|twist|max {tw_max:.3e}, |shape|max {sh_max:.3e})")

    # --- 2. primal-only secant trim ----------------------------------------
    _set_iterations(_a2gcp_n_trim())
    n_calls = {"n": 0}

    def _evaluate(alpha_deg):
        """One primal at this incidence. Evaluation 1 reuses the primal the
        pristine chain has already run at aoa0, so it costs nothing extra."""
        n_calls["n"] += 1
        if n_calls["n"] > 1:
            pv = _np.asarray(prob.get_val("patchV"), dtype=float).copy()
            pv[1] = float(alpha_deg)
            prob.set_val("patchV", pv)
            prob.run_model()
        cl = float(prob.get_val("scenario1.aero_post.CL")[0])
        if rank == 0:
            _a2gcp_emit(f"GC_TRIMEVAL {lvl} k {n_calls['n']} "
                        f"alpha {float(alpha_deg):.11f} CL {cl:.11f}")
        return cl

    trim = _sec.run_trim(_evaluate)
    if rank == 0:
        _json.dump(trim, open("trim_record.json", "w"), indent=1)
        _a2gcp_emit(
            f"GC_TRIM {lvl} converged {int(bool(trim['converged']))} "
            f"n_evaluations {trim['n_evaluations']} "
            f"alpha_star {float(trim['alpha_star'] or 0.0):.11f} "
            f"clips {len(trim['clips'])}")
    if not trim["converged"]:
        # BLOCKED, with the reason on the record. NEVER estimated, NEVER
        # interpolated (registration section 4.1).
        raise RuntimeError(
            f"A2GCP BLOCKED {lvl}: trim did not converge -- "
            f"{trim['blocked']['reason']}: {trim['blocked']['detail']}")

    # --- 3. THE GRADED PRIMAL: one warm run at alpha*, longer ---------------
    _set_iterations(_a2gcp_n_final())
    pv = _np.asarray(prob.get_val("patchV"), dtype=float).copy()
    pv[1] = float(trim["alpha_star"])
    prob.set_val("patchV", pv)
    prob.run_model()

    CD = float(prob.get_val("scenario1.aero_post.CD")[0])
    CL = float(prob.get_val("scenario1.aero_post.CL")[0])
    aoa = float(_np.asarray(prob.get_val("patchV"), dtype=float)[1])

    # --- 4. re-check the GRADED primal's OWN CL ----------------------------
    # The trim converged at 1,000 iterations; the graded primal ran longer. If
    # CL drifted out of tolerance the level is BLOCKED. The trim is NOT
    # re-entered here: re-trimming the run that produces the graded number is
    # tuning the answer.
    drift = abs(CL - _sec.CL_TARGET)
    if rank == 0:
        _a2gcp_emit(f"GC_TRIMCHECK {lvl} graded_CL {CL:.11f} "
                    f"abs_dev {drift:.6e} tol {_sec.TRIM_TOL:.1e}")
    if drift > _sec.TRIM_TOL:
        raise RuntimeError(
            f"A2GCP BLOCKED {lvl}: graded_primal_cl_drift -- |CL - "
            f"{_sec.CL_TARGET}| = {drift:.6e} > {_sec.TRIM_TOL:.1e} on the "
            f"graded primal. Reported, never estimated, never re-trimmed.")

    # --- 5. emit ------------------------------------------------------------
    # The residual and y+ readers are NOT here. PYDAFOAM on this image exposes
    # only calcPrimalResidualStatistics and getResiduals (probed read-only,
    # 2026-09-01); getResidualNorm and getyPlus DO NOT EXIST. GC_RESID is
    # emitted by the shell stage from the solver's OWN printed per-equation
    # initRes lines (the parser proven on
    # cases/dafoam/grade_a2_decomposition.py:32-34), and GC_YPLUS likewise from
    # the stock OpenFOAM yPlus functionObject.
    if rank == 0:
        _a2gcp_emit(f"GC_RESULT {lvl} CD {CD:.11f} CL {CL:.11f} AoA {aoa:.11f}")


if args.task == "run_model":
    _a2gcp_main()
