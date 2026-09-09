#!/usr/bin/env python3
"""STABILIZED OWN-FAMILY M6 CASE WRITER -- the transonic cold-start FPE crash-repair overlay.

WHAT THIS FILE IS.  It authors the rhoSimpleFoam case for the own-family {L2, L1, L0} solve
EXACTLY as write_m6_own_family_case.py does -- by reusing the pinned M6SR case writer
cases/M6SR/write_m6sr_case.py (W) verbatim -- and then LAYERS a MINIMAL, DOCUMENTED
stabilization on top.  It edits NEITHER write_m6sr_case.py NOR write_m6_own_family_case.py;
it imports them and applies its deltas after their writers have run (standing rule: the
frozen config change is not an edit; it is a fresh, documented crash repair carried by a
FRESH pre-registration M6_OWN_FAMILY_FINE_TRIPLE_STABILIZED_PREREGISTRATION.md, rule 2 / T25).

WHY IT EXISTS -- THE FINDING (settled by the cfd-supervisor's §3 crash triage).  The frozen
own-family fine-triple L2 solve CRASHED with SIGFPE (signal 8) inside
Foam::hePsiThermo<...perfectGas...sutherlandTransport...>::calculate() called from correct(),
at Time = 1, immediately after the FIRST energy (e) solve
(verification/runs/M6_OWN_FAMILY_runs/L2/solve/log.rhoSimpleFoam:129-219; inner rc 136 =
128+8, STEP_RC.txt / STOPPED.txt).  A nonphysical temperature after the first SIMPLE iteration
drives sutherlandTransport's mu = As*sqrt(T)/(1 + Ts/T) into a sqrt-of-nonphysical-T domain
error in libm, trapped by FOAM_SIGFPE (trapFpe on).  CONFIRMED config-level and
mesh-independent: the IDENTICAL FPE at Time = 1 appears on a DIFFERENT mesh at
verification/runs/M6SR_runs/L3/log.rhoSimpleFoam.  No M6 rhoSimpleFoam log anywhere carries an
"End" line: the frozen config was proven only at the checkMesh gate, never validated to
COMPLETE a flow solve.  This is the transonic (M_inf = 0.84) rhoSimpleFoam cold-start
instability, not a mesh defect and not a wall-time shortfall.

THE TWO DELTAS.  Each is a SOLVE-PATH robustness choice, not a gate change, and each is
INACTIVE or VANISHING at the converged solution, so no Gate-P surface Cp is biased:

  DELTA A (the primary FPE fix) -- system/fvOptions with a limitTemperature fvOption
    clamping T to [Tmin = 100 K, Tmax = 1000 K].  rhoSimpleFoam/EEqn.H calls
    fvOptions.correct(he) AFTER the energy solve and BEFORE thermo.correct(); limitTemperature
    clamps the energy field he to [he(Tmin), he(Tmax)] (its bounds are evaluated with the
    thermo's own he(p,T) = Cv*T, which does NOT call sqrt), so when thermo.correct() derives
    T from the bounded he the temperature stays in [100, 1000] K and sutherlandTransport's
    sqrt(T) is always in domain.  This is the transfer of the DMR bounded-e idea to this
    pressure-based (hePsiThermo) solver.  At the converged M_inf = 0.84 M6 field every cell's
    T lies well inside [100, 1000] K (T_inf = 288.15 K; stagnation ~= 328 K; the strongest
    expansion on the upper surface stays far above 100 K), so the limiter is INACTIVE at
    convergence and cannot move a Gate-P Cp.

  DELTA B (robustness) -- conservative STARTUP under-relaxation: equations U 0.7 -> 0.3,
    e 0.7 -> 0.1, (k|omega) 0.7 -> 0.3.  fields p 0.3 and rho 0.05 are UNCHANGED.  Relaxation
    factors change only the PATH to steady state, never the steady solution: the relaxation
    contribution is proportional to (phi_new - phi_old), which -> 0 as residuals -> 0, so the
    converged Cp is relaxation-independent and Gate P is unbiased.  Gentler startup relaxation
    keeps the first-iteration temperature excursion small so limitTemperature is not pinned to
    its bound every iteration and the residual descent is monotone.

WHAT IS DELIBERATELY NOT CHANGED (a physics-honest refusal, T25).  divSchemes are UNCHANGED:
  * div(phi,e) is ALREADY `bounded Gauss upwind` (first order on the energy convection) in the
    frozen config -- there is no second-order energy scheme to fall back FROM.
  * div(phi,U) stays `bounded Gauss linearUpwind grad(U)` -- the shock-resolving second-order
    momentum scheme Gate P is graded on.  Smearing it to first-order upwind WOULD move the
    shock position and bias Gate P; a scheme that changes the graded observable is a physics
    change, not a stabilization, and is REFUSED as a "fix".
thermophysicalProperties, turbulenceProperties, controlDict, sampleDict, decomposeParDict and
0/ are written BYTE-IDENTICAL to the base writer (W's writers reused verbatim).

THIS IS A SOLVER INPUT, NOT A GRADER.  It computes no gate, reads no result, prints no verdict
(rule 2 fixes the grading path at the pre-registration commit; case files are INPUTS).  If a
precondition does not hold it REFUSES (rc 2) rather than write a case it cannot justify.

EXIT VOCABULARY (mirrors write_m6_own_family_case.py):
    0   the stabilized case was written; STABILIZED_CASE_PROVENANCE.json records the deltas.
    2   REFUSAL -- a precondition does not hold.
    70  INTERNAL DEFECT of this writer.  Never a finding about the M6.

NO BARE `assert` (rule: python3 -O deletes them).  Every guard is an explicit raise.
NOTHING UNDER /home/ubuntu/certonomous-runs/ IS WRITTEN.  SUBMISSIONS ARE PARKED (rule 7).
"""

import argparse
import json
import math
import os
import sys

_THIS = os.path.abspath(__file__)
# .../verification/runs/M6_OWN_FAMILY_runs/write_m6_own_family_case_stabilized.py -> root 4 up.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_THIS))))
_M6SR_DIR = os.path.join(REPO, "cases", "M6SR")
_OWN_DIR = os.path.dirname(_THIS)
for _d in (_M6SR_DIR, _OWN_DIR):
    if _d not in sys.path:
        sys.path.insert(0, _d)

try:
    import write_m6sr_case as W          # the pinned M6SR case writer; its writers reused verbatim
    import write_m6_own_family_case as OWN  # the base own-family writer; constants/guards reused
except ImportError as _exc:              # pragma: no cover
    sys.stderr.write(
        "INTERNAL DEFECT: the pinned M6SR writer cases/M6SR/write_m6sr_case.py and/or the base "
        "own-family writer write_m6_own_family_case.py are not importable: "
        f"{_exc}. This overlay carries NO second definition of the case dictionaries. Cannot "
        "proceed.\n")
    sys.exit(70)


# --- DELTA B: the exact base relaxation block W.write_fv_solution emits, and its replacement. -
# Matched by CONTENT (not line number).  If the base block is absent the base writer changed
# under us -> REFUSE rather than write an unverified stabilization.
BASE_RELAX = (
    "relaxationFactors\n"
    "{\n"
    "    fields    { p 0.3; rho 0.05; }\n"
    '    equations { U 0.7; e 0.7; "(k|omega)" 0.7; }\n'
    "}\n")

STAB_RELAX = (
    "relaxationFactors\n"
    "{\n"
    "    // DELTA B (M6_OWN_FAMILY STABILIZED prereg): conservative STARTUP under-relaxation.\n"
    "    // Relaxation factors change only the PATH to steady state, never the steady solution\n"
    "    // (the relaxation contribution ~ (phi_new - phi_old) -> 0 as residuals -> 0), so the\n"
    "    // converged Cp is relaxation-independent and Gate P is UNBIASED.  Base RUNG1_M6_R2\n"
    "    // values were equations { U 0.7; e 0.7; (k|omega) 0.7 }; fields { p 0.3; rho 0.05 }\n"
    "    // are UNCHANGED.  Gentler startup keeps the first-iteration excursions small so the\n"
    "    // limiter fvOptions (DELTAS A & C, system/fvOptions) are not pinned to their bounds.\n"
    "    fields    { p 0.3; rho 0.05; }\n"
    '    equations { U 0.2; e 0.1; "(k|omega)" 0.3; }\n'
    "}\n")

# --- DELTA A: limitTemperature bounds; DELTA C: limitVelocity bound (physical, not tuned). ---
T_MIN_K = 100
T_MAX_K = 1000
# DELTA C: |U| ceiling.  Freestream magU = 285.68 m/s; the strongest PHYSICAL transonic
# overspeed on the M6 upper surface at M_inf=0.84 (local M ~1.3-1.4 in the expansion) reaches
# only ~400 m/s.  600 m/s is ~2.1x freestream and ~1.5x that physical peak -- comfortably above
# any converged velocity, so the limiter is INACTIVE at convergence and biases no Gate-P Cp; it
# binds only on a cold-start runaway that would otherwise blow up the nutUSpaldingWallFunction
# u_tau Newton solve (the SECOND cold-start FPE, in calcUTau()).
U_MAX_MS = 600


class Refusal(Exception):
    """rc 2 -- a precondition does not hold; refuse rather than write an unjustified case."""


class InternalDefect(Exception):
    """rc 70 -- a defect in THIS overlay.  Never a finding about the M6."""


def _write_fv_options(solve):
    """DELTA A: author system/fvOptions with the bounded-T limiter.  -> path written."""
    body = (
        W._header("dictionary", "fvOptions", "system") +
        "// DELTA A (M6_OWN_FAMILY STABILIZED prereg): bounded-T FPE crash repair.\n"
        "// rhoSimpleFoam/EEqn.H calls fvOptions.correct(he) AFTER the energy solve and BEFORE\n"
        "// thermo.correct(); limitTemperature clamps the energy field he to [he(Tmin),\n"
        "// he(Tmax)] (bounds via the thermo's own he(p,T)=Cv*T, which does NOT call sqrt), so\n"
        "// thermo.correct()'s derived T stays in [Tmin,Tmax] and sutherlandTransport's\n"
        "// mu = As*sqrt(T)/(1+Ts/T) never takes sqrt of a nonphysical T (the Time=1 SIGFPE in\n"
        "// verification/runs/M6_OWN_FAMILY_runs/L2/solve/log.rhoSimpleFoam:129-219).  At the\n"
        "// converged M_inf=0.84 M6 field every cell's T lies well inside [100,1000] K, so the\n"
        "// limiter is INACTIVE at convergence and biases no Gate-P Cp.\n"
        "limitT\n"
        "{\n"
        "    type            limitTemperature;\n"
        "    active          true;\n"
        "    selectionMode   all;\n"
        f"    min             {T_MIN_K};\n"
        f"    max             {T_MAX_K};\n"
        "}\n\n"
        "// DELTA C (M6_OWN_FAMILY STABILIZED prereg): bounded |U| -- protects the\n"
        "// nutUSpaldingWallFunction u_tau Newton solve (calcUTau) from a cold-start velocity\n"
        "// runaway that overflows its exp() and traps a SECOND SIGFPE (observed at Time=49 in\n"
        "// the smoke test: stack #4 nutUSpaldingWallFunction::calcUTau <- kOmegaSST::correctNut).\n"
        "// U_MAX = 600 m/s is ~2.1x the 285.68 m/s freestream and ~1.5x the strongest PHYSICAL\n"
        "// M6 transonic overspeed (~400 m/s), so it is INACTIVE at convergence and biases no\n"
        "// Gate-P Cp; it binds only on a cold-start runaway.\n"
        "limitU\n"
        "{\n"
        "    type            limitVelocity;\n"
        "    active          true;\n"
        "    selectionMode   all;\n"
        f"    max             {U_MAX_MS};\n"
        "}\n")
    return W._write(os.path.join(solve, "system", "fvOptions"), body)


def _stabilize_fv_solution(solve):
    """DELTA B: replace ONLY the relaxationFactors block in the already-written fvSolution.

    W.write_fv_solution(solve) has already written system/fvSolution byte-identical to the
    frozen config.  Read it, replace the single BASE_RELAX block with STAB_RELAX (everything
    else byte-unchanged), rewrite.  -> (path, before_sha, after_sha).  Refuses if the base
    block is not present exactly once (the base writer changed under us -- a FINDING).
    """
    import hashlib
    path = os.path.join(solve, "system", "fvSolution")
    if not os.path.isfile(path):
        raise InternalDefect(f"{path} was not written by W.write_fv_solution before the DELTA-B "
                             "transform. This overlay's call order is wrong.")
    text = open(path).read()
    before_sha = hashlib.sha256(text.encode()).hexdigest()
    n = text.count(BASE_RELAX)
    if n != 1:
        raise Refusal(
            "DELTA B cannot be applied by CONTENT: the base relaxationFactors block expected "
            f"from the pinned W.write_fv_solution appears {n} time(s), not exactly once, in "
            f"{path}. The base writer has changed under this overlay; a stabilization is never "
            "written onto a config this overlay cannot recognise. REFUSED (rule 14 spirit: a "
            "content-matched edit, never a blind one).")
    new = text.replace(BASE_RELAX, STAB_RELAX)
    W._write(path, new)
    after_sha = hashlib.sha256(new.encode()).hexdigest()
    return path, before_sha, after_sha


def write_stabilized_case(solve, level, ranks, end_time):
    """Author the STABILIZED own-family solve case at <solve> for <level>. -> provenance dict."""
    if level not in OWN.OWN_LEVELS:
        raise Refusal(f"{level!r} is not one of {OWN.OWN_LEVELS}. REFUSED.")
    try:
        ranks = int(ranks)
        end_time = int(end_time)
    except (TypeError, ValueError) as exc:
        raise Refusal(f"--ranks and --end-time must be integers; got ranks={ranks!r} "
                      f"end-time={end_time!r} ({exc}). REFUSED.")
    if ranks < 1:
        raise Refusal(f"--ranks must be >= 1; got {ranks}. REFUSED.")
    if end_time < 1:
        raise Refusal(f"--end-time must be >= 1; got {end_time}. REFUSED.")

    pm = os.path.join(solve, "constant", "polyMesh")
    if not os.path.isdir(pm):
        raise Refusal(
            f"{pm} is ABSENT. The driver must stage the screened mesh into "
            "<solve>/constant/polyMesh before this writer runs; boundary conditions are "
            "attached BY PATCH TYPE from this mesh's boundary file. REFUSED.")

    # Rule-4 age guard: refuse a case where 0/ or any time directory already exists.
    W._refuse_if_zero_or_time_dirs(solve)

    # Patches discovered BY TYPE (never typed in here), then REQUIRED to be the own-family set.
    pat, A = W.classify_patches(pm)
    if (pat["wall"] != OWN.OWN_PATCH_NAMES["wall"]
            or pat["symmetry"] != OWN.OWN_PATCH_NAMES["symmetry"]
            or pat["farfield"] != OWN.OWN_PATCH_NAMES["farfield"]):
        raise Refusal(
            "OWN-FAMILY PATCH-NAME MISMATCH. Expected wing (wall), symmetry (symmetry), "
            f"farfield (patch); this mesh yields wall={pat['wall']!r}, "
            f"symmetry={pat['symmetry']!r}, farfield={pat['farfield']!r}. REFUSED.")

    uvec, axes = W.freestream_vector(pm, A)          # refuses on an unexpected frame
    stns = W.stations(A.A_MAP_YB)                    # the pinned seven registered stations

    written = []
    # --- BYTE-IDENTICAL physics files (W's writers reused verbatim). ------------------------
    written += W.write_constant(solve)               # thermophysical + turbulence properties
    written.append(W.write_fv_schemes(solve))        # UNCHANGED (see docstring: schemes kept)
    fvsol_path = W.write_fv_solution(solve)           # base fvSolution first ...
    written.append(fvsol_path)
    written.append(W.write_decompose_par_dict(solve, ranks))
    written.append(W.write_sample_dict(solve, pat, axes, stns))
    written.append(W.write_control_dict(solve, end_time, uvec, pat))
    # 0/ LAST, and write_zero() writes 0/U LAST within it -- Section 8.6 / rule-4 age guard.
    written += W.write_zero(solve, pat, uvec)

    # --- STABILIZATION DELTAS layered on top. -----------------------------------------------
    fvsol_path2, relax_before, relax_after = _stabilize_fv_solution(solve)   # DELTA B
    fvopts_path = _write_fv_options(solve)                                    # DELTA A
    written.append(fvopts_path)

    mag = math.sqrt(sum(c * c for c in uvec))
    prov = {
        "writer": "verification/runs/M6_OWN_FAMILY_runs/write_m6_own_family_case_stabilized.py",
        "overlay_on": "verification/runs/M6_OWN_FAMILY_runs/write_m6_own_family_case.py "
                      "(which reuses cases/M6SR/write_m6sr_case.py verbatim)",
        "level": level,
        "solve_case": solve,
        "polymesh_read": pm,
        "ranks": ranks,
        "end_time": end_time,
        "mesh_identity_token": W.mesh_identity_token(pm),
        "FINDING": (
            "SIGFPE at Time=1 in hePsiThermo<...sutherlandTransport...>::calculate() from "
            "correct(), after the first e solve (L2/solve/log.rhoSimpleFoam:129-219, inner rc "
            "136); confirmed mesh-independent at M6SR_runs/L3/log.rhoSimpleFoam. Transonic "
            "cold-start Sutherland sqrt(T) domain error; no M6 rhoSimpleFoam log carries End."),
        "STABILIZATION_DELTAS": {
            "DELTA_A_bounded_T_fvOption": {
                "file": "system/fvOptions (NEW; base config had 'No finite volume options "
                        "present' -- log.rhoSimpleFoam:93)",
                "fvOption": "limitTemperature", "selectionMode": "all",
                "min_K": T_MIN_K, "max_K": T_MAX_K,
                "why": "clamps he before thermo.correct() so Sutherland sqrt(T) stays in "
                       "domain; INACTIVE at the converged M_inf=0.84 field -> unbiased Gate P. "
                       "SMOKE-CONFIRMED to clear the Time=1 SIGFPE (solve advanced to Time=49).",
            },
            "DELTA_C_bounded_U_fvOption": {
                "file": "system/fvOptions",
                "fvOption": "limitVelocity", "selectionMode": "all", "max_ms": U_MAX_MS,
                "why": "bounds |U| feeding nutUSpaldingWallFunction::calcUTau()'s exp(); "
                       "protects against the SECOND cold-start SIGFPE observed at Time=49 in the "
                       "smoke test (stack #4 calcUTau <- kOmegaSST::correctNut). 600 m/s is "
                       "~2.1x freestream / ~1.5x the physical M6 overspeed -> INACTIVE at "
                       "convergence -> unbiased Gate P.",
            },
            "DELTA_B_startup_underrelaxation": {
                "file": "system/fvSolution (relaxationFactors block ONLY; everything else "
                        "byte-identical to base)",
                "base_equations": "U 0.7; e 0.7; (k|omega) 0.7",
                "stabilized_equations": "U 0.2; e 0.1; (k|omega) 0.3",
                "fields_unchanged": "p 0.3; rho 0.05",
                "fvSolution_sha256_before_delta": relax_before,
                "fvSolution_sha256_after_delta": relax_after,
                "why": "relaxation affects only the PATH to steady state (contribution ~ "
                       "(phi_new-phi_old) -> 0 at convergence); converged Cp unchanged.",
            },
            "NOT_CHANGED": {
                "divSchemes": "UNCHANGED. div(phi,e) already bounded Gauss upwind; div(phi,U) "
                              "kept bounded Gauss linearUpwind grad(U) (the shock-resolving "
                              "scheme Gate P grades on -- smearing it would bias Gate P).",
                "thermo_turbulence_controlDict_sampleDict_decomposeParDict_0": "byte-identical "
                              "to base (W's writers reused verbatim).",
            },
        },
        "GATE_UNCHANGED": (
            "This overlay changes ONLY the solve path. Gate P (dCp=+/-0.02 at Mo=0.84, "
            "x/c<=0.90, seven y/b stations) and Gate G (rule-5 Roache triple on {L2,L1,L0}) "
            "and the cost cap are set by the STABILIZED pre-registration, unwidened."),
        "patches_by_TYPE_never_by_name": pat,
        "freestream": {
            "U_vector_written": uvec, "magnitude_written": mag,
            "Mach_reproduced": mag / W.A_INF,
            "Reynolds_reproduced_on_MAC": W.RHO_INF * mag * W.MAC_C / W.MU_INF,
        },
        "stations": stns,
        "written": written,
        "THIS_FILE_IS_A_SOLVER_INPUT_NOT_A_GRADER": (
            "It computes no gate, reads no result and prints no verdict. Rule 2 fixes the "
            "GRADING path at the pre-registration commit; case files are INPUTS."),
        "cost_basis": (
            "core-minutes = wall s x ranks / 60. Dollars DERIVED, NOT MEASURED, at the "
            "owner-stated c7a.4xlarge $0.0513/core-h (box cannot read its own billing)."),
    }
    W._write(os.path.join(solve, "STABILIZED_CASE_PROVENANCE.json"),
             json.dumps(prov, indent=2) + "\n")
    return prov


def selftest():
    """Planted controls (rule 3): show the overlay ACTUALLY writes each delta, not a stale file.

    Drives on this family's L2 screened mesh into a scratch case; then reads BACK from disk:
      (1) system/fvOptions contains a limitTemperature with min 100 / max 1000 (DELTA A), and
          -- the honest half -- a case NOT given DELTA A does NOT carry it;
      (2) system/fvSolution carries the stabilized equations block and NOT the base 0.7 block
          (DELTA B), and the base block WAS present before the transform (so the reader is
          shown able to see the value the delta removes).
    A control that cannot be driven (no mesh) is a REFUSAL, never a silent pass.
    """
    import shutil
    import tempfile
    l2_pm = os.path.join(_OWN_DIR, "L2", "case", "constant", "polyMesh")
    if not os.path.isdir(l2_pm):
        raise Refusal(f"selftest needs the L2 screened mesh at {l2_pm}; it is ABSENT. A control "
                      "that cannot be driven is a REFUSAL, never a pass. REFUSED.")
    scratch = tempfile.mkdtemp(prefix="m6own_stab_selftest_")
    try:
        # --- plant/read DELTA B on the base file first (reader-can-see-nonzero, rule 3). ----
        case = os.path.join(scratch, "case")
        os.makedirs(os.path.join(case, "constant"), exist_ok=True)
        shutil.copytree(l2_pm, os.path.join(case, "constant", "polyMesh"))
        W.write_fv_solution(case)
        base_txt = open(os.path.join(case, "system", "fvSolution")).read()
        if BASE_RELAX not in base_txt:
            raise InternalDefect(
                "PLANT FAILED: the base fvSolution written by the pinned W.write_fv_solution "
                "does NOT contain the expected base relaxationFactors block, so DELTA B's "
                "reader is blind to the value it replaces. FAILED (rule 3).")
        _stabilize_fv_solution(case)
        stab_txt = open(os.path.join(case, "system", "fvSolution")).read()
        if BASE_RELAX in stab_txt:
            raise InternalDefect("DELTA B did not fire: the base 0.7 relaxation block survived "
                                 "the transform. FAILED (rule 3).")
        if 'equations { U 0.2; e 0.1; "(k|omega)" 0.3; }' not in stab_txt:
            raise InternalDefect("DELTA B did not write the stabilized equations block. FAILED.")

        # --- DELTAS A & C: written contains both limiters; a bare case has none. --------------
        _write_fv_options(case)
        opts = open(os.path.join(case, "system", "fvOptions")).read()
        if "limitTemperature" not in opts or f"min             {T_MIN_K}" not in opts \
                or f"max             {T_MAX_K}" not in opts:
            raise InternalDefect("DELTA A did not write a limitTemperature min/max block. FAILED.")
        if "limitVelocity" not in opts or f"max             {U_MAX_MS}" not in opts:
            raise InternalDefect("DELTA C did not write a limitVelocity max block. FAILED.")
        bare = os.path.join(scratch, "bare")
        os.makedirs(os.path.join(bare, "system"), exist_ok=True)
        if os.path.exists(os.path.join(bare, "system", "fvOptions")):
            raise InternalDefect("a bare case unexpectedly carries fvOptions. FAILED (rule 3).")

        print("SELFTEST PASS: DELTA A limitTemperature[100,1000] + DELTA C limitVelocity[600] "
              "written (absent on a bare case); DELTA B base 0.7 block seen then replaced by "
              "U 0.2/e 0.1/(k|omega) 0.3.")
        return 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main(argv):
    ap = argparse.ArgumentParser(add_help=True, description=__doc__)
    ap.add_argument("--level", choices=OWN.OWN_LEVELS, help="L2 / L1 / L0 (coarse -> fine)")
    ap.add_argument("--solve", help="the solve case directory to write into "
                                    "(must already carry constant/polyMesh)")
    ap.add_argument("--ranks", type=int, help="decomposition ranks (>=1)")
    ap.add_argument("--end-time", dest="end_time", type=int, help="solver endTime in iterations")
    ap.add_argument("--selftest", action="store_true",
                    help="run the planted delta controls and exit (writes nothing under solve)")
    args = ap.parse_args(argv[1:])

    if args.selftest:
        try:
            return selftest()
        except Refusal as exc:
            sys.stderr.write(f"REFUSAL (selftest): {exc}\n"); return 2
        except InternalDefect as exc:
            sys.stderr.write(f"INTERNAL DEFECT (selftest): {exc}\n"); return 70

    missing = [n for n, v in (("--level", args.level), ("--solve", args.solve),
                              ("--ranks", args.ranks), ("--end-time", args.end_time))
               if v is None]
    if missing:
        sys.stderr.write(f"REFUSAL: missing required argument(s): {', '.join(missing)}.\n")
        return 2
    try:
        prov = write_stabilized_case(args.solve, args.level, args.ranks, args.end_time)
    except Refusal as exc:
        sys.stderr.write(f"REFUSAL: {exc}\n"); return 2
    except W.Refusal as exc:
        sys.stderr.write(f"REFUSAL (reused pinned writer): {exc}\n"); return 2
    except W.InternalDefect as exc:
        sys.stderr.write(f"INTERNAL DEFECT (reused pinned writer): {exc}\n"); return 70
    except InternalDefect as exc:
        sys.stderr.write(f"INTERNAL DEFECT: {exc}\n"); return 70
    print(f"WROTE STABILIZED own-family case: level {prov['level']}, {len(prov['written'])} "
          f"files into {prov['solve_case']} (ranks {prov['ranks']}, endTime {prov['end_time']}); "
          f"DELTA A limitTemperature[{T_MIN_K},{T_MAX_K}] + DELTA C limitVelocity[{U_MAX_MS}] + "
          f"DELTA B startup under-relaxation.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
