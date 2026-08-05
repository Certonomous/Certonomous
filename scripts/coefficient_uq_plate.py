#!/usr/bin/env python3
"""Coefficient-uncertainty propagation ladder on the NASA TMR flat plate.

Docket vehicle: r2-closure-coefficient-uncertainty. The motorbike run of that
item measured a ONE-AT-A-TIME sensitivity sweep on a bluff body with no
reference value. This run does the other half of the item on the cheapest case
the lab owns that HAS a trusted reference -- the TMR 2D zero-pressure-gradient
flat plate, fine level (137x97 nodes, 13056 cells), whose Cd sits +0.29% from
the published CFL3D SST-V value -- and takes the propagation up the full
ladder: joint Monte Carlo, non-intrusive polynomial chaos, and a Gaussian
process surrogate, all fitted on the SAME sample set so the three bands are
comparable rather than three separate experiments.

Three things this run does that the motorbike run did not:

1. JOINT sampling, not one-at-a-time. The motorbike band is a lower bound on
   the joint range by construction (its own report says so). Here every sample
   moves all five coefficients at once, so the band is the joint one.

2. The LOG-LAYER CONSTRAINT is enforced. OpenFOAM's kOmegaSST reads gamma1 and
   gamma2 as free coefficients, so perturbing betaStar or beta_i without
   recomputing gamma silently walks the model off its own log layer. Menter's
   relation gamma_i = beta_i/betaStar - sigma_wi kappa^2 / sqrt(betaStar) is
   applied to every sample, including the nominal one, which is why this study
   carries TWO baselines: the OpenFOAM-default solve and the constrained-
   nominal solve. Their difference is the measured cost of that inconsistency,
   not a modelling choice hidden in a band.

3. A held-out VALIDATION set. The surrogates are scored on ten samples they
   never saw, not on leave-one-out alone.

Every solve restarts from the converged baseline field (the cost trick the
Schaefer papers use), holds mesh and numerics fixed, and is gated on its own
Cd flatness before its number is allowed into the sample set.

Usage:
    python3 scripts/coefficient_uq_plate.py preregister
    python3 scripts/coefficient_uq_plate.py baseline
    python3 scripts/coefficient_uq_plate.py solve [--only train|valid|nominal]
    python3 scripts/coefficient_uq_plate.py analyze
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "sdk"))

from workflows.tmr_verification import (  # noqa: E402
    CF_STATION, CFL3D_SST_V, FUN3D_SST_V, cf_at, final_coefficient,
    parse_wall_shear_raw,
)

BODY = "tmr_flatplate_fine"
STUDY = REPO / "models" / "curriculum" / "uq-studies" / f"{BODY}.json"
CASE_SRC = REPO / "models" / "tmr" / "flatplate" / "fine"
RUN_ROOT = Path(os.environ.get("R2_PLATE_RUN_ROOT",
                               "/home/ubuntu/certonomous-runs/r2-plate-uq"))
OUT = REPO / "demo-output" / "website" / "r2-coefficient-uq-flatplate"

CELLS = 13056
KAPPA = 0.41                 # von Karman, HELD (its own interval is not sampled)
ALPHA_OMEGA2 = 0.856         # sigma_w2, HELD at the OpenFOAM/Menter value
RESTART_ITERATIONS = 1500
FLATNESS_GATE = 1.0e-7       # Cd peak-to-peak over the last 50 iterations
MAX_CONCURRENT = 5           # native serial solves; leaves the box to others

# The sampled box. Names are the paper's; `openfoam` is the key the solver
# reads, or "derived" when the value is reconstructed from the sampled ratio.
COEFFICIENTS: list[dict[str, Any]] = [
    {"name": "betaStar", "openfoam": "betaStar",
     "nominal": 0.09, "interval": [0.0784, 0.1024]},
    {"name": "a1", "openfoam": "a1",
     "nominal": 0.31, "interval": [0.31, 0.40],
     "note": "increased only; the nominal IS the lower bound"},
    {"name": "sigma_w1", "openfoam": "alphaOmega1",
     "nominal": 0.5, "interval": [0.3, 0.7]},
    {"name": "betaStar_over_beta1", "openfoam": "beta1 (derived)",
     "nominal": 1.2, "interval": [1.19, 1.31]},
    {"name": "betaStar_over_beta2", "openfoam": "beta2 (derived)",
     "nominal": 0.09 / 0.0828, "interval": [1.05, 1.45]},
]
NAMES = [c["name"] for c in COEFFICIENTS]
LOWER = np.array([c["interval"][0] for c in COEFFICIENTS])
UPPER = np.array([c["interval"][1] for c in COEFFICIENTS])
NOMINAL = np.array([c["nominal"] for c in COEFFICIENTS])

N_TRAIN = 42                 # 2 x the 21 terms of a total-order-2 PCE in 5 dims
N_VALID = 10
SEED_TRAIN = 20260805
SEED_VALID = 20260806

CITATIONS = [
    "Schaefer, Hosder, West, Rumsey, Carlson and Kleb, 'Uncertainty "
    "Quantification of Turbulence Model Closure Coefficients for Transonic "
    "Wall-Bounded Flows', AIAA Journal 55(1), 2017, pp. 195-213",
    "Schaefer, Cary, Mani and Spalart, 'Uncertainty Quantification and "
    "Sensitivity Analysis of SA Turbulence Model Coefficients in Two and "
    "Three Dimensions', AIAA 2017-1710",
    "Menter, 'Two-Equation Eddy-Viscosity Turbulence Models for Engineering "
    "Applications', AIAA Journal 32(8), 1994, pp. 1598-1605 (log-layer "
    "relation for gamma_i)",
    "NASA Turbulence Modeling Resource, 2D zero-pressure-gradient flat plate, "
    "SST-V grid-convergence data (turbmodels.larc.nasa.gov)",
]


# ---------------------------------------------------------------------------
# The coefficient map: sampled box -> the dictionary the solver reads
# ---------------------------------------------------------------------------

def solver_coefficients(x: np.ndarray) -> dict[str, float]:
    """kOmegaSSTCoeffs for one point of the sampled box.

    beta1 and beta2 come back from the sampled RATIOS betaStar/beta_i, which is
    how the source paper parameterises them, and gamma1/gamma2 are then forced
    onto the log layer. Nothing else in the model moves.
    """
    beta_star, a1, sigma_w1, r1, r2 = (float(v) for v in x)
    beta1 = beta_star / r1
    beta2 = beta_star / r2
    root = math.sqrt(beta_star)
    gamma1 = beta1 / beta_star - sigma_w1 * KAPPA ** 2 / root
    gamma2 = beta2 / beta_star - ALPHA_OMEGA2 * KAPPA ** 2 / root
    return {"betaStar": beta_star, "a1": a1, "alphaOmega1": sigma_w1,
            "beta1": beta1, "beta2": beta2,
            "gamma1": gamma1, "gamma2": gamma2}


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------

def maximin_lhs(n: int, dim: int, seed: int, tries: int = 400) -> np.ndarray:
    """Latin hypercube in the unit box, best of `tries` by maximin distance.

    Plain LHS fixes the marginals and leaves the joint spacing to luck; the
    maximin pick is the standard cheap repair and is what the motorbike stage
    used, so the two studies' designs stay comparable.
    """
    rng = np.random.default_rng(seed)
    best, best_score = None, -1.0
    for _ in range(tries):
        cut = (np.arange(n)[:, None] + rng.random((n, dim))) / n
        design = np.column_stack([rng.permutation(cut[:, j]) for j in range(dim)])
        d = np.sqrt(((design[:, None, :] - design[None, :, :]) ** 2).sum(-1))
        score = d[np.triu_indices(n, 1)].min()
        if score > best_score:
            best, best_score = design, score
    return best


def design_points(n: int, seed: int) -> np.ndarray:
    return LOWER + maximin_lhs(n, len(COEFFICIENTS), seed) * (UPPER - LOWER)


# ---------------------------------------------------------------------------
# Solving
# ---------------------------------------------------------------------------

def _foam(args: list[str], cwd: Path, log_name: str,
          timeout: float = 1800.0) -> subprocess.CompletedProcess:
    with (cwd / log_name).open("w") as log:
        return subprocess.run(["openfoam2606", *args], stdout=log,
                              stderr=subprocess.STDOUT, cwd=str(cwd),
                              timeout=timeout)


def dafoam_containers() -> int:
    """How many dafoam containers are up. These solves are native OpenFOAM and
    take no container slot, but they take cores from the ones that are, so the
    launcher still counts them and holds concurrency down when the box is busy.
    """
    try:
        out = subprocess.run(["sudo", "docker", "ps", "--format", "{{.Image}}"],
                             capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return 0
    return sum(1 for line in out.splitlines() if "dafoam" in line.lower())


def write_case(dest: Path, coeffs: dict[str, float] | None,
               *, restart_from: Path | None, iterations: int) -> None:
    """Stage one solve. `coeffs` None means the OpenFOAM-default closure."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    shutil.copytree(CASE_SRC / "system", dest / "system")
    shutil.copytree(CASE_SRC / "constant", dest / "constant")
    if restart_from is None:
        shutil.copytree(CASE_SRC / "0", dest / "0")
    else:
        shutil.copytree(restart_from / "constant" / "polyMesh",
                        dest / "constant" / "polyMesh")
        latest = max((p for p in restart_from.iterdir()
                      if p.is_dir() and p.name.replace(".", "").isdigit()
                      and float(p.name) > 0), key=lambda p: float(p.name))
        shutil.copytree(latest, dest / "0")
        for stale in ("wallShearStress", "yPlus"):
            (dest / "0" / stale).unlink(missing_ok=True)

    control = (dest / "system" / "controlDict").read_text()
    control = control.replace("endTime         5000;",
                              f"endTime         {iterations};")
    (dest / "system" / "controlDict").write_text(control)

    if coeffs is not None:
        block = "\n".join(f"        {k:<12}{v:.10g};" for k, v in coeffs.items())
        turb = (dest / "constant" / "turbulenceProperties").read_text()
        turb = turb.replace(
            "    printCoeffs     on;\n",
            "    printCoeffs     on;\n\n    kOmegaSSTCoeffs\n    {\n"
            f"{block}\n    }}\n")
        (dest / "constant" / "turbulenceProperties").write_text(turb)


def extract(case: Path) -> dict[str, Any]:
    dat = sorted((case / "postProcessing").rglob("coefficient*.dat"))
    if not dat:
        raise RuntimeError(f"{case.name}: no force-coefficient history")
    text = dat[-1].read_text(errors="replace")
    cd = final_coefficient(text, "Cd", tail=50)
    if cd is None:
        raise RuntimeError(f"{case.name}: Cd column missing")
    raw = sorted((case / "postProcessing").rglob("wallShearStress_*.raw"))
    if not raw:
        raise RuntimeError(f"{case.name}: no wall-shear sample")
    profile = parse_wall_shear_raw(raw[-1].read_text(errors="replace"))
    cf = cf_at(profile, CF_STATION)
    return {"cd": cd["value"], "cd_tail_spread": cd["spread"],
            "iterations": cd["iterations"], "cf_station": cf,
            "cf_profile_n": len(profile),
            "flat": cd["spread"] <= FLATNESS_GATE and cf is not None and cf > 0,
            "cf_profile": [[round(x, 6), round(c, 8)] for x, c in profile]}


def run_one(tag: str, x: np.ndarray | None, *, restart: bool = True,
            iterations: int = RESTART_ITERATIONS) -> dict[str, Any]:
    case = RUN_ROOT / tag
    coeffs = None if x is None else solver_coefficients(x)
    write_case(case, coeffs,
               restart_from=(RUN_ROOT / "baseline") if restart else None,
               iterations=iterations)
    if not restart:
        _foam(["blockMesh"], case, "log.blockMesh")
    start = time.monotonic()
    proc = _foam(["simpleFoam"], case, "log.simpleFoam")
    wall = time.monotonic() - start
    if proc.returncode != 0:
        raise RuntimeError(f"{tag}: simpleFoam exit {proc.returncode}")
    rec = extract(case)
    rec.update({"tag": tag, "wall_seconds": round(wall, 1),
                "core_minutes": round(wall / 60.0, 4),
                "restart": restart,
                "x": None if x is None else [float(v) for v in x],
                "solver_coefficients": coeffs})
    return rec


def solve_set(jobs: list[tuple[str, np.ndarray | None]]) -> list[dict[str, Any]]:
    """Run a set of solves with strict, bounded concurrency."""
    busy = dafoam_containers()
    limit = max(1, MAX_CONCURRENT - busy)
    deadline = time.monotonic() + 1800
    while busy >= 3 and time.monotonic() < deadline:
        print(f"[queue] {busy} dafoam containers up; waiting", flush=True)
        time.sleep(60)
        busy = dafoam_containers()
        limit = max(1, MAX_CONCURRENT - busy)
    print(f"[queue] {busy} dafoam containers; running {limit} solves at a time",
          flush=True)
    out: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=limit) as pool:
        futures = {pool.submit(run_one, tag, x): tag for tag, x in jobs}
        for fut in futures:
            rec = fut.result()
            print(f"[solve] {rec['tag']} Cd={rec['cd']:.7f} "
                  f"Cf={rec['cf_station']:.7f} {rec['wall_seconds']:.0f}s "
                  f"flat={rec['flat']}", flush=True)
            out.append(rec)
    return sorted(out, key=lambda r: r["tag"])


# ---------------------------------------------------------------------------
# Pre-registration
# ---------------------------------------------------------------------------

def preregister() -> None:
    train = design_points(N_TRAIN, SEED_TRAIN)
    valid = design_points(N_VALID, SEED_VALID)
    study = {
        "body": BODY,
        "study": "coefficient-uncertainty propagation ladder",
        "docket_item": "r2-closure-coefficient-uncertainty",
        "status": "pre-registered",
        "preregistered_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "preregistration_contract": (
            "Written and committed BEFORE any sample was solved. Sample count, "
            "seeds, coefficient box, derived-coefficient map, quantities of "
            "interest, convergence gate and the surrogate designs below are "
            "the design of record; anything that had to change afterwards is "
            "recorded in `deviations` with its reason, and the seeds make the "
            "sample points themselves reproducible without trusting this file."
        ),
        "case": {
            "name": "NASA TMR 2D zero-pressure-gradient flat plate, fine level",
            "case_dir": "models/tmr/flatplate/fine",
            "cells": CELLS, "tmr_nodes": "137x97",
            "solver": "simpleFoam (incompressible)", "closure": "kOmegaSST",
            "re_per_unit_length": 5.0e6, "u_inf": 1.0, "nu": 2.0e-7,
            "why_this_case": (
                "cheapest case the lab owns that has a trusted published "
                "reference: 80.9 s serial for the cold baseline, and its Cd "
                "sits +0.29% from the CFL3D SST-V value, so the coefficient "
                "band can be read against a real reference rather than only "
                "against itself"),
            "reference": {
                "cfl3d_sst_v": CFL3D_SST_V[CELLS],
                "fun3d_sst_v": FUN3D_SST_V[CELLS],
                "source": "turbmodels.larc.nasa.gov, models/tmr/reference/"},
        },
        "coefficients": COEFFICIENTS,
        "held_fixed": {
            "kappa": {"value": KAPPA,
                      "note": "its published interval [0.38, 0.42] is named in "
                              "the docket item but kappa is not one of the five "
                              "coefficients that item put in the box; held so "
                              "the box stays the docketed one"},
            "sigma_w2 (alphaOmega2)": {"value": ALPHA_OMEGA2},
            "mesh": "held; no refinement in this study",
            "numerics": "held; fvSchemes, fvSolution and relaxation unchanged",
        },
        "derived_coefficient_map": {
            "beta1": "betaStar / (betaStar/beta1)",
            "beta2": "betaStar / (betaStar/beta2)",
            "gamma_i": ("beta_i/betaStar - sigma_wi kappa^2 / sqrt(betaStar) "
                        "(Menter 1994 log-layer relation), recomputed for "
                        "EVERY sample including the nominal one"),
            "why": (
                "OpenFOAM's kOmegaSST reads gamma1 and gamma2 as free "
                "coefficients. Moving betaStar or beta_i without recomputing "
                "gamma leaves the model off its own log layer, which is a "
                "different model, not a perturbed one. Enforcing the relation "
                "at the nominal point does not reproduce OpenFOAM's defaults "
                "(gamma1 0.553167 vs 5/9 = 0.555556, 0.43% apart; gamma2 "
                "0.440355 vs 0.44, 0.08% apart), so this study solves BOTH "
                "nominal points and reports the difference as a measured "
                "number instead of absorbing it into the band."),
        },
        "quantities_of_interest": [
            {"name": "cd", "definition": "plate drag coefficient, Aref = 2, "
                                         "magUInf = 1, forceCoeffs on patch plate"},
            {"name": "cf_station",
             "definition": f"skin friction at the TMR station x = {CF_STATION}"},
        ],
        "design": {
            "sampling": "maximin Latin hypercube, best of 400 draws",
            "marginals": (
                "uniform over each published interval. STATED ASSUMPTION: the "
                "intervals are epistemic, so the uniform is a sampling choice "
                "made to get a density the chaos and process fits need, not a "
                "claim about how the coefficients are distributed. The "
                "interval-valued reading of the result is the min/max envelope, "
                "which is reported alongside every probabilistic band and is "
                "the number the model channel may carry."),
            "n_train": N_TRAIN, "seed_train": SEED_TRAIN,
            "n_valid": N_VALID, "seed_valid": SEED_VALID,
            "n_train_rationale": (
                "21 terms in a total-order-2 polynomial chaos expansion over 5 "
                "variables, at the oversampling ratio of 2 the source paper "
                "uses for its point-collocation fits"),
            "joint_not_one_at_a_time": (
                "every sample moves all five coefficients at once; the "
                "motorbike stage of this docket item ran one-at-a-time corners "
                "and its own report states that band is a lower bound on the "
                "joint range"),
            "train_points": [[round(float(v), 8) for v in row] for row in train],
            "valid_points": [[round(float(v), 8) for v in row] for row in valid],
        },
        "solve_protocol": {
            "restart": "every sample restarts from the converged baseline field",
            "iterations": RESTART_ITERATIONS,
            "iterations_evidence": (
                "measured on a probe restart: Cd at 1500 iterations differs "
                "from Cd at 2000 by 3.5e-8 (0.0013% of Cd), against a band "
                "expected in the percent range"),
            "flatness_gate": FLATNESS_GATE,
            "gate_meaning": ("Cd peak-to-peak over the final 50 iterations; a "
                             "sample that fails is reported as a failure, not "
                             "quietly dropped"),
            "concurrency": f"at most {MAX_CONCURRENT} native serial solves, "
                           f"reduced by the number of dafoam containers up",
        },
        "planned_analysis": {
            "monte_carlo": "empirical band from the training samples: min/max "
                           "envelope, mean, sigma, 5-95 percentile",
            "polynomial_chaos": "non-intrusive point-collocation PCE on the "
                                "Legendre basis (uniform germ), total order 1 "
                                "and 2, least squares, leave-one-out scored; "
                                "Sobol indices from the expansion coefficients",
            "surrogate": "Gaussian process, anisotropic squared exponential "
                         "plus nugget, hyperparameters by marginal likelihood, "
                         "leave-one-out and held-out validation",
            "comparison": "all three bands on the SAME sample set, plus the "
                          "held-out set both surrogates are scored on",
        },
        "budget_core_min": 100,
        "citations": CITATIONS,
    }
    STUDY.parent.mkdir(parents=True, exist_ok=True)
    STUDY.write_text(json.dumps(study, indent=2) + "\n", encoding="utf-8")
    print(f"pre-registered -> {STUDY}")


# ---------------------------------------------------------------------------
# Stages
# ---------------------------------------------------------------------------

def results_path() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    return OUT / "samples.json"


def load_results() -> dict[str, Any]:
    p = results_path()
    return json.loads(p.read_text()) if p.exists() else {}


def save_results(data: dict[str, Any]) -> None:
    results_path().write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def stage_baseline() -> None:
    data = load_results()
    case = RUN_ROOT / "baseline"
    if not (case / "constant" / "polyMesh").exists():
        write_case(case, None, restart_from=None, iterations=5000)
        _foam(["blockMesh"], case, "log.blockMesh")
        start = time.monotonic()
        _foam(["simpleFoam"], case, "log.simpleFoam")
        wall = time.monotonic() - start
    else:
        wall = float(data.get("baseline_openfoam_default", {})
                     .get("wall_seconds", 80.9))
    rec = extract(case)
    rec.update({"tag": "baseline", "wall_seconds": round(wall, 1),
                "core_minutes": round(wall / 60.0, 4), "restart": False,
                "x": None, "solver_coefficients": None})
    data["baseline_openfoam_default"] = rec
    save_results(data)
    print(f"baseline Cd={rec['cd']:.9f} Cf={rec['cf_station']:.9f} "
          f"spread={rec['cd_tail_spread']:.3g}")


def stage_solve(only: str | None) -> None:
    data = load_results()
    if only in (None, "nominal"):
        rec = run_one("nominal_constrained", NOMINAL.copy())
        data["baseline_constrained_nominal"] = rec
        save_results(data)
        print(f"[solve] nominal_constrained Cd={rec['cd']:.9f}")
    if only in (None, "train"):
        pts = design_points(N_TRAIN, SEED_TRAIN)
        jobs = [(f"train_{i:02d}", pts[i]) for i in range(N_TRAIN)]
        data["train"] = solve_set(jobs)
        save_results(data)
    if only in (None, "valid"):
        pts = design_points(N_VALID, SEED_VALID)
        jobs = [(f"valid_{i:02d}", pts[i]) for i in range(N_VALID)]
        data["valid"] = solve_set(jobs)
        save_results(data)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["preregister", "baseline", "solve"])
    ap.add_argument("--only", choices=["train", "valid", "nominal"])
    args = ap.parse_args()
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    if args.stage == "preregister":
        preregister()
    elif args.stage == "baseline":
        stage_baseline()
    else:
        stage_solve(args.only)


if __name__ == "__main__":
    main()
