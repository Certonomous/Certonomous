#!/usr/bin/env python3
"""Standing model-form batch: the same validated case under four RANS closures.

Design and pre-registration:
``demo-output/website/campaign/MODEL_FORM_BATCH_DESIGN.md``. Read it first --
this file implements that document and does not decide anything on its own.

What it is. The uncertainty doctrine's model channel is measured here the way
the NASA hump headline measured it: solve the same validated case under
kOmegaSST, SpalartAllmaras, kEpsilon and realizableKE, gate every cell on its
own convergence standard, and take the band as the min/max over the CONVERGED
cells only. The hump is why the gate is mechanical: the band that failed to
contain the experiment was the band that still had an unconverged member in it.

What it extends. The case families are the lab's own TMR ladders in
``sdk/workflows/tmr_verification.py`` -- the flat plate, the bump in channel
and the NACA 0012 C-grid -- reused through their own writers and run
functions. Nothing about the meshes, schemes, relaxation or residual targets is
re-invented here; the only thing this module changes inside a case is the
turbulence model and the fields that model needs.

How it survives a fleet death. Every cell writes its own ``record.json`` the
moment it finishes, under
``demo-output/website/campaign/MODEL_FORM_runs/<cell_id>/``. That record is the
unit of truth. A cell that already has one is skipped, so the runner is
idempotent and any future session can continue cold with
``--list`` then ``--family X --max-core-min N``. Launch it detached
(``setsid nohup``) and a session limit costs at most the one cell in flight.

Queueing. This batch is the lowest-priority slot filler on the machine: before
every cell it counts live dafoam/openfoam containers and refuses to launch
while three or more are running, and it never runs more than one solve of its
own at a time (one core, stricter than the ``--cpus=2`` ceiling the docket set
for containers).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field as dc_field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator, Sequence

_SDK_ROOT = Path(__file__).resolve().parents[1]
if str(_SDK_ROOT) not in sys.path:
    sys.path.insert(0, str(_SDK_ROOT))

from workflows import tmr_verification as tv  # noqa: E402
from chief_engineer.log_signatures import detect_unsettled_stop  # noqa: E402

REPO_ROOT = _SDK_ROOT.parent
OUT_ROOT = REPO_ROOT / "demo-output" / "website" / "campaign" / "MODEL_FORM_runs"
BAND_JSON = REPO_ROOT / "demo-output" / "website" / "campaign" / "MODEL_FORM_BAND.json"
BAND_MD = REPO_ROOT / "demo-output" / "website" / "campaign" / "MODEL_FORM_BAND.md"
LEDGER = OUT_ROOT / "ledger.jsonl"
RUNNER_LOG = OUT_ROOT / "runner.log"

MODELS = ("kOmegaSST", "SpalartAllmaras", "kEpsilon", "realizableKE")

# Models needing a field the SST baseline does not carry. kOmegaSST and the
# two k-epsilon variants all solve k; only the epsilon-family needs epsilon and
# only SA needs nuTilda.
EXTRA_FIELD = {"kOmegaSST": None, "SpalartAllmaras": "nuTilda",
               "kEpsilon": "epsilon", "realizableKE": "epsilon"}

C_MU = 0.09
# TMR's Spalart-Allmaras farfield: nuTilda = 3 nu (turbmodels.larc.nasa.gov
# flat-plate and NACA 0012 validation pages). SA carries no k or omega, so it
# cannot be matched to the SST freestream and is given its own standard one --
# recorded as deviation 1 in the design document.
SA_NUTILDA_OVER_NU = 3.0

# Monitor Standard S12 thresholds, used here exactly as adopted.
S12_DRIFT_TOL = 1e-3
S12_MONOTONE_TOL = 0.90
# Mesh Standard 3.1/3.2 hard gates.
MAX_NON_ORTHO = 70.0
MAX_SKEWNESS = 4.0

# R12 mesh-gate exemption (docs/charters/SUPERVISOR_RULINGS.md, ruled
# 2026-08-07 on the Cases family supervisor's C2 escalation). A grid that is
# the reference community's own canonical verification grid may carry a
# MODEL-FORM BAND above the lab's mesh gate, because the band measures
# inter-model spread on a fixed grid -- it needs the same grid, not a
# compliant one, and a home-built compliant replacement would break the
# family's comparability with the reference it exists to be compared to.
# Three conditions, all mandatory and all enforced in code
# (sdk/tests/test_model_form_r12.py pins them):
#   1. the exemption is stated on the band artifact itself, with the failing
#      number beside it (apply_mesh_gate builds the statement from the cell's
#      own measured checkMesh values -- no number, no exemption);
#   2. the exemption is scoped to model-form banding only -- physics gates
#      and credential verdicts still require compliant meshes, and
#      mesh_gate_exemption() raises for any other purpose;
#   3. the exemption names its grid provenance (who published it, where).
R12_BANDING_PURPOSE = "model-form banding"

MESH_GATE_EXEMPT_FAMILIES: dict[str, dict[str, str]] = {
    # Family N solves the TMR-distributed NACA 0012 coarse C-grid whose
    # far-wake skew is characteristic of the topology the verification
    # community standardises on: max non-orthogonality 85.70 deg vs the
    # 70 deg Mesh Standard 3.1 hard gate.
    "N": {
        "ruling": ("R12, docs/charters/SUPERVISOR_RULINGS.md "
                   "(ruled 2026-08-07)"),
        "scope": ("model-form banding only; physics gates and credential "
                  "verdicts still require compliant meshes and this "
                  "exemption never travels to them"),
        "grid_provenance": (
            "NASA Langley Turbulence Modeling Resource NACA 0012 C-grid, "
            "n0012_113-33.p3dfmt as distributed "
            "(turbmodels.larc.nasa.gov, mirror tmbwg.github.io/turbmodels) "
            "-- the verification community's canonical grid family, the "
            "same family whose 897x257 member carries the published CFL3D "
            "references this batch compares against"),
    },
}

_R12_REQUIRED_FIELDS = ("ruling", "scope", "grid_provenance")
for _family, _info in MESH_GATE_EXEMPT_FAMILIES.items():
    _missing = [f for f in _R12_REQUIRED_FIELDS if not _info.get(f)]
    if _missing:
        raise RuntimeError(
            f"R12 exemption for family {_family} is missing mandatory "
            f"field(s) {_missing}; all three ruling conditions are "
            "required before the flag exists at all")


def mesh_gate_exemption(family: str, purpose: str) -> dict[str, str] | None:
    """The R12 exemption for ``family``, or ``None`` if it has none.

    ``purpose`` must be ``R12_BANDING_PURPOSE``: ruling condition 2 scopes
    the exemption to model-form banding only, so any physics-gate or
    credential path that reaches for it is refused with a raise rather than
    quietly granted.
    """
    info = MESH_GATE_EXEMPT_FAMILIES.get(family)
    if info is None:
        return None
    if purpose != R12_BANDING_PURPOSE:
        raise RuntimeError(
            f"R12 mesh-gate exemption for family {family} is scoped to "
            f"{R12_BANDING_PURPOSE!r} only and is REFUSED for purpose "
            f"{purpose!r}: physics gates and credential verdicts still "
            "require compliant meshes (ruling R12, condition 2)")
    return info
# Queue gate: this batch yields while the DAFoam/OpenFOAM fleet is busy.
CONTAINER_CEILING = 3
CONTAINER_POLL_SECONDS = 60.0

# Iteration backstop, and why it is this batch's own number rather than the
# ladder's. ``tv.iteration_backstop`` sizes a run for the SETTLE WATCHER,
# which stops a rung the moment its coefficient goes flat; on these grids it
# returns 3000. This batch has no watcher: its gate is the case's own
# ``residualControl``, so 3000 is not a backstop here, it is a guillotine.
# Measured on the first pass of families P and B, 2026-08-05: nine of twenty
# cells stopped at exactly 3000 with the residual still falling, and the
# archived bump-coarse rung itself was asked for 4000 and still finished with
# a moving tail. 12000 is four times the deepest converged cell of that pass
# (P_re1e6_kOmegaSST at 2230) and three times the archived bump budget.
BATCH_BACKSTOP = 12000


# ---------------------------------------------------------------------------
# The matrix
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Cell:
    family: str            # P | B | N
    regime: str            # regime tag, part of the cell id
    model: str
    params: dict[str, Any] = dc_field(default_factory=dict)

    @property
    def cell_id(self) -> str:
        return f"{self.family}_{self.regime}_{self.model}"

    @property
    def group_id(self) -> str:
        return f"{self.family}_{self.regime}"

    @property
    def out_dir(self) -> Path:
        return OUT_ROOT / self.cell_id


# Family P: TMR zero-pressure-gradient flat plate, medium rung (3264 cells),
# Reynolds number per unit length as the regime axis (U = 1, so nu = 1/Re).
P_REGIMES = {"re1e6": 1.0e6, "re5e6": 5.0e6, "re2e7": 2.0e7}
# Family B: TMR bump in channel, coarse rung (3520 cells), same axis. 3e6 is
# the TMR reference condition for this case.
B_REGIMES = {"re3e6": 3.0e6, "re1p2e7": 1.2e7}
# Family N: TMR NACA 0012 coarse C-grid, angle of attack as the regime axis at
# the case's own Re = 6e6.
N_REGIMES = {"a0": 0.0, "a10": 10.0, "a15": 15.0}
# Family H: the periodic hills on the lab's VERIFIED F6b medium mesh (Gate V
# 0.043%), one regime (the canonical Re_H station), reattachment as the QoI.
# Added 2026-08-08 per negative-verdict review entry 1; pre-registration:
# campaign/MODEL_FORM_H_HILLS_PREREGISTRATION.md. The mesh is COMPLIANT
# (non-ortho 39.66 / skew 0.226 vs gates 70 / 4) -- R12 is not involved.
H_REGIMES = {"re10595": None}
H_SOURCE_CASE = (REPO_ROOT / "demo-output" / "website" / "campaign"
                 / "F6b_runs" / "medium")
H_BACKSTOP = 12000   # ~2x both measured attainments (SST 5997, QCR 6177)
H_NU = 9.438414346389807e-05
H_K_INIT = 0.00375
H_OMEGA_INIT = 0.11022703842524302

FAMILY_CAP_CORE_MIN = {"P": 20.0, "B": 30.0, "N": 60.0, "H": 35.0}


def all_cells() -> list[Cell]:
    cells: list[Cell] = []
    for tag, re_l in P_REGIMES.items():
        for model in MODELS:
            cells.append(Cell("P", tag, model, {"re_per_length": re_l}))
    for tag, re_l in B_REGIMES.items():
        for model in MODELS:
            cells.append(Cell("B", tag, model, {"re_per_length": re_l}))
    for tag, alpha in N_REGIMES.items():
        for model in MODELS:
            cells.append(Cell("N", tag, model, {"alpha_deg": alpha}))
    for tag in H_REGIMES:
        for model in MODELS:
            cells.append(Cell("H", tag, model, {}))
    return cells


# ---------------------------------------------------------------------------
# Field derivation: one closure's fields from the baseline's omega field
# ---------------------------------------------------------------------------
#
# The transformation is textual and deliberately so: it inherits the case's own
# patch names, patch order and boundary types, which differ between the plate,
# the bump and the converted C-grid. The same idea (and the two regex forms
# below) is already in sdk/scripts/run_uq_studies.py; what is added here is the
# wall entry, which that version got wrong for a wall-resolved grid -- nuTilda
# is zero at a no-slip wall, and epsilon needs the low-Re wall function rather
# than a fixed freestream value.

_VALUE_RE = re.compile(r"uniform\s+[0-9eE.+-]+")


def _retype_field(omega_text: str, *, obj: str, dimensions: str,
                  value: float, wall_type: str,
                  wall_value: float | None) -> str:
    """Rewrite the omega field text as another scalar field.

    ``wall_type`` replaces ``omegaWallFunction`` and ``wall_value`` is the
    value written inside that boundary entry (``None`` keeps the freestream
    value, which is what a wall function wants as its seed).
    """
    text = re.sub(r"object\s+omega\s*;", f"object      {obj};", omega_text)
    text = re.sub(r"dimensions\s+\[[^\]]*\]\s*;",
                  f"dimensions      {dimensions};", text)
    out_lines: list[str] = []
    in_wall_entry = False
    for line in text.splitlines():
        if "omegaWallFunction" in line:
            out_lines.append(line.replace("omegaWallFunction", wall_type))
            in_wall_entry = True
            continue
        if in_wall_entry:
            if "blended" in line:
                # omegaWallFunction's blending switch; the replacement carries
                # its own options, appended below.
                continue
            if _VALUE_RE.search(line):
                if wall_value is not None:
                    out_lines.append(_VALUE_RE.sub(
                        f"uniform {wall_value:.8g}", line))
                else:
                    out_lines.append(_VALUE_RE.sub(
                        f"uniform {value:.8g}", line))
                in_wall_entry = False
                continue
        out_lines.append(_VALUE_RE.sub(f"uniform {value:.8g}", line)
                         if _VALUE_RE.search(line) else line)
    return "\n".join(out_lines) + "\n"


def epsilon_field(omega_text: str, k_inf: float, nut_inf: float) -> str:
    """epsilon from omega, at the same freestream eddy viscosity.

    eps = C_mu k^2 / nut is the k-epsilon definition of nut inverted, so the
    k-epsilon cells begin from the same physical freestream state as the
    k-omega cells rather than from a number somebody picked.
    """
    eps = C_MU * k_inf ** 2 / nut_inf
    text = _retype_field(omega_text, obj="epsilon",
                         dimensions="[0 2 -3 0 0 0 0]", value=eps,
                         wall_type="epsilonWallFunction", wall_value=None)
    # epsilonWallFunction on a wall-resolved grid needs its low-Re branch.
    return text.replace("type            epsilonWallFunction;",
                        "type            epsilonWallFunction;\n"
                        "        lowReCorrection true;")


def nutilda_field(omega_text: str, nu: float) -> str:
    """nuTilda from omega: TMR farfield 3 nu, and exactly zero at the wall."""
    return _retype_field(omega_text, obj="nuTilda",
                         dimensions="[0 2 -1 0 0 0 0]",
                         value=SA_NUTILDA_OVER_NU * nu,
                         wall_type="fixedValue", wall_value=0.0)


# ---------------------------------------------------------------------------
# Case patching: turbulence model, solver/scheme entries, freestream scaling
# ---------------------------------------------------------------------------

def turbulence_properties_for(model: str) -> str:
    return tv._foam_header("dictionary", "turbulenceProperties",
                           "constant") + f"""
simulationType  RAS;
RAS
{{
    RASModel        {model};
    turbulence      on;
    printCoeffs     on;
}}
"""


def _extend_fv_solution(text: str, extra: str | None) -> str:
    """Give the extra turbulence field the same solver, target and relaxation
    the baseline gives k and omega. Nothing else in the dictionary moves."""
    if not extra:
        return text
    text = text.replace('"(U|k|omega)"', f'"(U|k|omega|{extra})"')
    text = text.replace('"(k|omega)"     1e-08;',
                        f'"(k|omega|{extra})"     1e-08;')
    text = re.sub(r"equations \{ U ([0-9.]+); k ([0-9.]+); omega ([0-9.]+); \}",
                  lambda m: (f"equations {{ U {m.group(1)}; k {m.group(2)}; "
                             f"omega {m.group(3)}; {extra} {m.group(3)}; }}"),
                  text)
    return text


def _extend_fv_schemes(text: str, extra: str | None) -> str:
    if not extra:
        return text
    marker = "    div(phi,omega)"
    for line in text.splitlines():
        if line.startswith(marker):
            addition = line.replace("div(phi,omega)", f"div(phi,{extra})")
            # keep the column alignment the file already uses
            return text.replace(line, line + "\n" + addition)
    raise RuntimeError("fvSchemes has no div(phi,omega) entry to copy")


def _scale_freestream(text: str, pairs: Sequence[tuple[float, float]]) -> str:
    """Replace the baseline's formatted freestream literals with the regime's.

    ``pairs`` are (old, new) values; the literals are matched exactly as the
    writers formatted them (``:.8g``), so a value that is not a freestream
    constant cannot be hit by accident.
    """
    for old, new in pairs:
        text = text.replace(f"{old:.8g}", f"{new:.8g}")
    return text


def patch_case(case_dir: Path, model: str, *, nu: float,
               k_inf: float, nut_inf: float,
               omega_inf_old: float | None = None,
               omega_inf_new: float | None = None,
               nut_inf_old: float | None = None) -> None:
    """Patch a written case in place for one (model, regime) cell."""
    case_dir = Path(case_dir)
    (case_dir / "constant" / "turbulenceProperties").write_text(
        turbulence_properties_for(model), newline="\n")

    # Regime: nu, and the freestream turbulence that scales with it.
    if omega_inf_new is not None and omega_inf_old is not None:
        (case_dir / "constant" / "transportProperties").write_text(
            tv.transport_properties(nu), newline="\n")
        for name in ("omega", "nut"):
            path = case_dir / "0" / name
            pairs = [(omega_inf_old, omega_inf_new)]
            if nut_inf_old is not None:
                pairs.append((nut_inf_old, nut_inf))
            path.write_text(_scale_freestream(path.read_text(), pairs),
                            newline="\n")

    extra = EXTRA_FIELD[model]
    if extra:
        omega_text = (case_dir / "0" / "omega").read_text()
        if extra == "epsilon":
            body = epsilon_field(omega_text, k_inf, nut_inf)
        else:
            body = nutilda_field(omega_text, nu)
        (case_dir / "0" / extra).write_text(body, newline="\n")
    for name, transform in (("fvSolution", _extend_fv_solution),
                            ("fvSchemes", _extend_fv_schemes)):
        path = case_dir / "system" / name
        path.write_text(transform(path.read_text(), extra), newline="\n")


def set_backstop(case_dir: Path, iterations: int) -> None:
    """Raise the run's iteration backstop without touching anything else.

    The writers size ``endTime`` from ``tv.iteration_backstop``, which is the
    settle watcher's number (see BATCH_BACKSTOP). ``writeInterval`` follows it
    so the case still writes exactly one field set at the end.
    """
    path = Path(case_dir) / "system" / "controlDict"
    text = path.read_text()
    text = re.sub(r"endTime\s+\d+;", f"endTime         {iterations};", text)
    text = re.sub(r"writeInterval\s+\d+;",
                  f"writeInterval   {iterations};", text)
    path.write_text(text, newline="\n")


@contextmanager
def naca_model_context(model: str) -> Iterator[None]:
    """Run ``tv.run_naca_level`` under one closure.

    The NACA path writes its own dictionaries and fields inside the run
    function (the patch names are only known after the PLOT3D conversion), so
    the model is injected by swapping the three module functions that path
    calls rather than by patching a directory. Restored on exit, always.
    """
    extra = EXTRA_FIELD[model]
    orig_turb = tv.turbulence_properties
    orig_sol = tv.fv_solution
    orig_sch = tv.fv_schemes
    orig_fields = tv.naca_fields_tmr

    def turb() -> str:
        return turbulence_properties_for(model)

    def sol(*args: Any, **kwargs: Any) -> str:
        return _extend_fv_solution(orig_sol(*args, **kwargs), extra)

    def sch(*args: Any, **kwargs: Any) -> str:
        return _extend_fv_schemes(orig_sch(*args, **kwargs), extra)

    def fields(*args: Any, **kwargs: Any) -> dict[str, str]:
        out = dict(orig_fields(*args, **kwargs))
        if extra == "epsilon":
            out[extra] = epsilon_field(out["omega"], tv.NACA_K_INF,
                                       tv.NACA_NUT_INF)
        elif extra == "nuTilda":
            out[extra] = nutilda_field(out["omega"], tv.NACA_NU)
        return out

    tv.turbulence_properties = turb
    tv.fv_solution = sol
    tv.fv_schemes = sch
    tv.naca_fields_tmr = fields
    try:
        yield
    finally:
        tv.turbulence_properties = orig_turb
        tv.fv_solution = orig_sol
        tv.fv_schemes = orig_sch
        tv.naca_fields_tmr = orig_fields


# ---------------------------------------------------------------------------
# The gate
# ---------------------------------------------------------------------------

_CONVERGED_RE = re.compile(r"SIMPLE solution converged in (\d+) iterations")
_RESID_RE = re.compile(r"Solving for (\w+), Initial residual = ([0-9.eE+-]+)")


def residual_history(log_text: str) -> dict[str, list[float]]:
    """Initial residual per field, in log order (p appears once per
    corrector; medians below make that harmless)."""
    out: dict[str, list[float]] = {}
    for name, val in _RESID_RE.findall(log_text):
        out.setdefault(name, []).append(float(val))
    return out


def _median(values: Sequence[float]) -> float:
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


def adjusted_settle_verdict(log_text: str, history: dict[str, list[float]],
                            spec: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    """The pre-registered adjusted settle criterion, evaluated mechanically.

    Replaces ONLY the convergence-sentence clause (gate criterion 2) for a
    cell whose record shows an unreachable-tolerance stop; every threshold
    comes from the committed spec file the pre-registration froze
    (see ``--adjusted-settle``), never from this run. Clauses: each named
    residual's final-quarter median is under its cap (one decade above the
    standard target) and has fallen less than ``plateau_factor`` from the
    previous quarter (demonstrably floored); each named QoI's trailing
    ``tail_iters`` peak-to-peak is at or under its decision-scaled cap.
    """
    detail: dict[str, Any] = {"residual_plateau": {}, "qoi_tail_p2p": {}}
    ok = True
    factor = float(spec.get("plateau_factor", 2.0))
    tail = int(spec.get("tail_iters", 2000))
    residuals = residual_history(log_text)
    for field_name, cap in (spec.get("residual_floor") or {}).items():
        series = residuals.get(field_name) or []
        n = len(series)
        if n < 8:
            detail["residual_plateau"][field_name] = {
                "error": f"history has {n} samples; too short to judge"}
            ok = False
            continue
        quarter = max(n // 4, 1)
        last = _median(series[-quarter:])
        prev = _median(series[-2 * quarter:-quarter])
        floored = last >= prev / factor
        under = last <= float(cap)
        detail["residual_plateau"][field_name] = {
            "median_final_quarter": last, "median_previous_quarter": prev,
            "floored_within_factor": factor, "floored": floored,
            "cap": float(cap), "under_cap": under}
        ok = ok and floored and under
    for qoi, cap in (spec.get("qoi_p2p_max") or {}).items():
        series = history.get(qoi) or []
        if len(series) < tail:
            detail["qoi_tail_p2p"][qoi] = {
                "error": f"history has {len(series)} samples; "
                         f"shorter than the {tail} tail window"}
            ok = False
            continue
        window = series[-tail:]
        p2p = max(window) - min(window)
        met = p2p <= float(cap)
        detail["qoi_tail_p2p"][qoi] = {"p2p": p2p, "cap": float(cap),
                                       "tail_iters": tail, "met": met}
        ok = ok and met
    return ok, detail


def log_verdict(log_text: str) -> dict[str, Any]:
    """Monitor Standard S1/S2 fatals and the residualControl stop."""
    fatal: list[str] = []
    if "Foam::sigFpe::sigHandler" in log_text:
        fatal.append("S1 floating point exception")
    for line in log_text.splitlines():
        if "nan" in line.lower() and ("Solving for" in line
                                      or "Initial residual" in line):
            fatal.append("S2 NaN in solver output")
            break
    match = _CONVERGED_RE.search(log_text)
    iterations = None
    for line in reversed(log_text.splitlines()):
        hit = re.match(r"^Time = (\d+)", line)
        if hit:
            iterations = int(hit.group(1))
            break
    return {"fatal": fatal,
            "residual_control_met": bool(match),
            "converged_at": int(match.group(1)) if match else None,
            "last_iteration": iterations}


def mesh_verdict(check_text: str) -> dict[str, Any]:
    """Mesh Standard 3.1/3.2 hard gates from the case's own checkMesh."""
    non_ortho = skew = aspect = None
    # checkMesh's own wording, taken from this batch's first log rather than
    # guessed: the non-orthogonality line is a "Max: <v> average: <v>" pair,
    # skewness is an "= <v>" line, and aspect ratio is only printed at all
    # when cells exceed the reporting threshold.
    hit = re.search(r"Mesh non-orthogonality Max:\s*([0-9.eE+-]+)", check_text)
    if hit:
        non_ortho = float(hit.group(1))
    hit = re.search(r"Max skewness = ([0-9.eE+-]+)", check_text)
    if hit:
        skew = float(hit.group(1))
    hit = re.search(r"Max aspect ratio:?\s*=?\s*([0-9.eE+-]+)", check_text)
    if hit:
        aspect = float(hit.group(1))
    breaches = []
    if non_ortho is None:
        breaches.append("checkMesh non-orthogonality unreadable")
    elif non_ortho > MAX_NON_ORTHO:
        breaches.append(f"non-orthogonality {non_ortho:g} > {MAX_NON_ORTHO:g}")
    if skew is None:
        breaches.append("checkMesh skewness unreadable")
    elif skew > MAX_SKEWNESS:
        breaches.append(f"skewness {skew:g} > {MAX_SKEWNESS:g}")
    return {"max_non_ortho": non_ortho, "max_skewness": skew,
            "max_aspect_ratio": aspect, "breaches": breaches,
            "aspect_ratio_note": ("advisory only per Mesh Standard 3.3; "
                                  "never a lone rejection")}


def apply_mesh_gate(meshv: dict[str, Any], family: str
                    ) -> tuple[list[str], dict[str, Any] | None]:
    """Mesh-gate exclusion reasons for the banding gate, R12-aware.

    Returns ``(reasons, exemption)``. For a family without an R12 entry the
    breaches pass through untouched and ``exemption`` is ``None``. For an
    exempt family, MEASURED breaches move off the exclusion reasons and into
    an exemption record whose statement carries the failing number(s) beside
    the gate value (ruling condition 1) and the grid provenance (condition
    3). An unreadable checkMesh is never exempted: without the measured
    number the statement the ruling demands cannot be written, so the cell
    stays excluded on the unreadable-mesh reason.
    """
    breaches = list(meshv["breaches"])
    failing: list[str] = []
    non_ortho = meshv.get("max_non_ortho")
    if non_ortho is not None and non_ortho > MAX_NON_ORTHO:
        failing.append(f"max non-orthogonality {non_ortho:.2f} deg vs the "
                       f"{MAX_NON_ORTHO:g} deg hard gate")
    skew = meshv.get("max_skewness")
    if skew is not None and skew > MAX_SKEWNESS:
        failing.append(f"max skewness {skew:.2f} vs the "
                       f"{MAX_SKEWNESS:g} hard gate")
    if family not in MESH_GATE_EXEMPT_FAMILIES or not failing:
        return breaches, None
    info = mesh_gate_exemption(family, R12_BANDING_PURPOSE)
    assert info is not None
    exemption = dict(info)
    exemption["failing"] = failing
    exemption["statement"] = (
        "Mesh Standard hard gate EXEMPT under " + info["ruling"] + ": "
        + "; ".join(failing)
        + ", on the reference community's own grid -- "
        + info["grid_provenance"] + ". Scope: " + info["scope"] + ".")
    # Only the measured hard-gate breaches are exempted; anything else
    # (unreadable checkMesh) stays an exclusion reason.
    remaining = [b for b in breaches if "unreadable" in b]
    return remaining, exemption


def assert_mesh_certified_at_entry(remote: Path, family: str, label: str,
                                   *, fallback: Path | None = None) -> None:
    """Refuse the solver launch on an uncertified or gate-breaching mesh.

    Mesh birth certificate, Verification Charter v1.5 section 9, adopted
    2026-08-08: this batch already retained its checkMesh logs and applied
    the hard gates -- but POST HOC, as banding-gate exclusion after the
    solve had already spent its wall time. This is the same record read
    BEFORE launch: an absent or unreadable checkMesh record, or a hard-gate
    breach outside an R12 family exemption, refuses the launch with the
    reason stated. The exemption logic is apply_mesh_gate's own, so nothing
    a family ruling admits post hoc is refused pre-launch.
    """
    check = Path(remote) / "log.checkMesh"
    if not check.exists() and fallback is not None:
        check = Path(fallback) / "log.checkMesh"
    if not check.exists():
        raise RuntimeError(
            f"{label}: no checkMesh record beside the case; the solver does "
            f"not launch on an uncertified mesh (Verification Charter v1.5 "
            f"section 9, born clean or it does not enter)")
    meshv = mesh_verdict(check.read_text(errors="replace"))
    reasons, _ = apply_mesh_gate(meshv, family)
    if reasons:
        raise RuntimeError(
            f"{label}: mesh refused at entry, not excluded after the solve: "
            + "; ".join(reasons)
            + " (Verification Charter v1.5 section 9)")


def settle_verdict_s12(series: Sequence[float]) -> dict[str, Any]:
    """Monitor Standard S12 on the QoI history. Scale-free by construction."""
    finding = detect_unsettled_stop(list(series))
    if finding is None:
        return {"unsettled": False, "detail": None}
    detail = finding if isinstance(finding, dict) else {"finding": str(finding)}
    return {"unsettled": True, "detail": detail}


_LOG_COEFF_RE = re.compile(r"^\s+(C[dls])\s*:\s+(-?[0-9][0-9eE.+-]*)",
                           re.MULTILINE)


def history_from_log(log_text: str) -> dict[str, list[float]]:
    """The coefficient history as the solver's own log printed it.

    Fallback for a cell whose ``coefficient.dat`` did not survive collection
    (seen once on P_re1e6_SpalartAllmaras, 2026-08-05: the solve converged,
    the log carries the full Cd table, and the dat file was absent from the
    copied postProcessing tree). The log block prints one ``Cd :`` /
    ``Cl :`` line per write, total first, so the parse takes the first
    number on the line and skips the (f)/(r) split rows by construction.
    """
    out: dict[str, list[float]] = {}
    for name, value in _LOG_COEFF_RE.findall(log_text):
        out.setdefault(name, []).append(float(value))
    return out


def read_history(post_dir: Path) -> dict[str, list[float]]:
    """Every coefficient column the case wrote, as plain lists."""
    files = sorted(Path(post_dir).rglob("coefficient*.dat"))
    if not files:
        return {}
    text = files[-1].read_text(errors="replace")
    header: list[str] = []
    rows: list[list[float]] = []
    for line in text.splitlines():
        if line.startswith("#"):
            fields = line.lstrip("#").split()
            if fields and fields[0] == "Time":
                header = fields
            continue
        parts = line.split()
        if not parts:
            continue
        try:
            rows.append([float(p) for p in parts])
        except ValueError:
            continue
    if not header or not rows:
        return {}
    out: dict[str, list[float]] = {}
    for idx, name in enumerate(header):
        out[name] = [r[idx] for r in rows if len(r) > idx]
    return out


# ---------------------------------------------------------------------------
# Queue gate
# ---------------------------------------------------------------------------

def live_solver_containers() -> list[str] | None:
    """Names of live solver containers, or ``None`` when docker cannot be
    asked -- the caller must not read a failed query as an empty machine
    (finding C5, CASES_FAMILY_FIRST_PASS_FINDINGS_2026-08-07.md)."""
    try:
        proc = subprocess.run(
            ["sudo", "docker", "ps", "--format", "{{.Names}}\t{{.Image}}"],
            capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    names = []
    for line in proc.stdout.splitlines():
        low = line.lower()
        if "dafoam" in low or "openfoam" in low or "foam" in low:
            names.append(line.split("\t")[0])
    return names


def wait_for_slot(log: Callable[[str], None], *, max_wait: float) -> bool:
    """True when the machine has room for this batch's one core."""
    waited = 0.0
    while True:
        live = live_solver_containers()
        if live is None:
            # Availability over deadlock, but never silently: the yield
            # discipline is disengaged and the log says so.
            log("queue gate: docker query FAILED; gate is blind this cell, "
                "proceeding anyway (recorded, not silent)")
            return True
        if len(live) < CONTAINER_CEILING:
            if live:
                log(f"queue gate: {len(live)} solver container(s) live "
                    f"({', '.join(live)}), under the ceiling of "
                    f"{CONTAINER_CEILING}; proceeding")
            return True
        if waited >= max_wait:
            log(f"queue gate: still {len(live)} solver containers live after "
                f"{waited:.0f}s; yielding and stopping")
            return False
        log(f"queue gate: {len(live)} solver containers live "
            f"(>= {CONTAINER_CEILING}); waiting")
        time.sleep(CONTAINER_POLL_SECONDS)
        waited += CONTAINER_POLL_SECONDS


# ---------------------------------------------------------------------------
# Running one cell
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_record(cell: Cell, record: dict[str, Any]) -> None:
    cell.out_dir.mkdir(parents=True, exist_ok=True)
    (cell.out_dir / "record.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", newline="\n")
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def _grade(cell: Cell, remote: Path, out_dir: Path, wall_seconds: float,
           returncode: int, qoi_names: Sequence[str],
           settle_on: str, *, backstop: int | None = None,
           adjusted_settle: dict[str, Any] | None = None) -> dict[str, Any]:
    """Apply the pre-registered gate and build the cell record."""
    log_text = (remote / "log.simpleFoam").read_text(errors="replace") \
        if (remote / "log.simpleFoam").exists() else ""
    check_text = (remote / "log.checkMesh").read_text(errors="replace") \
        if (remote / "log.checkMesh").exists() else ""
    for name in ("log.simpleFoam", "log.checkMesh", "log.blockMesh"):
        src = remote / name
        if src.exists():
            shutil.copy2(src, out_dir / name)
    # A 12000-iteration solver log is ~18 MB and the archive keeps dozens of
    # cells; the log is evidence and is kept, compressed. Everything the gate
    # reads was read above, from the uncompressed original.
    big = out_dir / "log.simpleFoam"
    if big.exists() and big.stat().st_size > 1_000_000:
        subprocess.run(["gzip", "-f", str(big)], check=False)
    post = remote / "postProcessing"
    if post.exists():
        shutil.rmtree(out_dir / "postProcessing", ignore_errors=True)
        shutil.copytree(post, out_dir / "postProcessing")

    logv = log_verdict(log_text)
    meshv = mesh_verdict(check_text)
    history = read_history(out_dir / "postProcessing")
    qoi_source = "coefficient.dat"
    if not history.get(settle_on):
        history = history_from_log(log_text)
        qoi_source = "solver log (coefficient.dat absent from collection)"
    qoi: dict[str, float | None] = {}
    for name in qoi_names:
        series = history.get(name)
        qoi[name] = series[-1] if series else None
    settle = settle_verdict_s12(history.get(settle_on, []))

    reasons: list[str] = []
    if returncode != 0:
        reasons.append(f"solver exit code {returncode}")
    reasons.extend(logv["fatal"])
    adjusted_admit = False
    adjusted_detail: dict[str, Any] | None = None
    if not logv["residual_control_met"]:
        if adjusted_settle is not None:
            adjusted_admit, adjusted_detail = adjusted_settle_verdict(
                log_text, history, adjusted_settle)
        if not adjusted_admit:
            # "stopped on the backstop" only when the run actually reached
            # it: a cell that crashed at iteration 45 did not stop on any
            # backstop (finding C6 -- the three B_re1p2e7 FPE records
            # carried this wording untruthfully; their verdicts were right,
            # the evidence text was not).
            last = logv["last_iteration"]
            if backstop is not None and last is not None and last >= backstop:
                reasons.append(
                    "residualControl not met (stopped on the backstop)")
            else:
                reasons.append("residualControl not met")
            if adjusted_detail is not None:
                reasons.append(
                    "adjusted settle criterion NOT met (see settle_criterion)")
    if settle["unsettled"]:
        reasons.append("S12 unsettled stop on " + settle_on)
    mesh_reasons, mesh_exemption = apply_mesh_gate(meshv, cell.family)
    reasons.extend(mesh_reasons)
    if any(v is None for v in qoi.values()):
        reasons.append("QoI missing from the coefficient history")

    record: dict[str, Any] = {
        "cell_id": cell.cell_id, "group": cell.group_id,
        "family": cell.family, "regime": cell.regime, "model": cell.model,
        "params": cell.params,
        "converged": not reasons,
        "excluded_reasons": reasons,
        "qoi": qoi,
        "qoi_source": qoi_source,
        "iterations": logv["converged_at"] or logv["last_iteration"],
        "residual_control_met": logv["residual_control_met"],
        "settle_s12": settle,
        "mesh": meshv,
        "mesh_gate_exemption": mesh_exemption,
        "wall_seconds": round(wall_seconds, 1),
        "core_min": round(wall_seconds / 60.0, 3),
        "ranks": 1,
        "toolchain": "native OpenFOAM v2606 (openfoam2606 launcher)",
        "timestamp": _now(),
    }
    if adjusted_settle is not None:
        record["settle_criterion"] = {
            "kind": "adjusted, pre-registered",
            "prereg": adjusted_settle.get("prereg"),
            "spec": {k: v for k, v in adjusted_settle.items()
                     if k != "prereg"},
            "measured": adjusted_detail,
            "admitted_in_place_of_residual_control": adjusted_admit,
        }
    return record


def run_cell_P_or_B(cell: Cell, log: Callable[[str], None], *,
                    backstop: int = BATCH_BACKSTOP,
                    adjusted_settle: dict[str, Any] | None = None
                    ) -> dict[str, Any]:
    """Flat plate (P) or bump in channel (B): blockMesh families."""
    if cell.family == "P":
        level = [lv for lv in tv.LEVELS if lv.name == "medium"][0]
        writer, patch_name = tv.write_case, "plate"
        k_inf, nu_base = tv.K_INF, tv.NU
        omega_base, nut_base = tv.OMEGA_INF, tv.NUT_INF
        qoi_names, settle_on = ("Cd",), "Cd"
    else:
        level = [lv for lv in tv.BUMP_LEVELS if lv.name == "coarse"][0]
        writer, patch_name = tv.write_bump_case, "bump"
        k_inf, nu_base = tv.K_INF, tv.BUMP_NU
        omega_base, nut_base = tv.BUMP_OMEGA_INF, tv.BUMP_NUT_INF
        qoi_names, settle_on = ("Cd",), "Cd"

    nu = tv.U_INF / float(cell.params["re_per_length"])
    omega_inf = 1.0e-6 * (tv.U_INF / tv.MACH) ** 2 / nu
    nut_inf = k_inf / omega_inf

    case_root = Path(tv._RUN_ROOT) / "modelform-cases" / cell.cell_id
    shutil.rmtree(case_root, ignore_errors=True)
    case_root.mkdir(parents=True, exist_ok=True)
    case_dir = writer(case_root, level)
    patch_case(case_dir, cell.model, nu=nu, k_inf=k_inf, nut_inf=nut_inf,
               omega_inf_old=omega_base, omega_inf_new=omega_inf,
               nut_inf_old=nut_base)
    set_backstop(case_dir, backstop)

    remote = Path(tv._RUN_ROOT) / f"modelform-{cell.cell_id}"
    out_dir = cell.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    tv._stage_and_mesh(level, case_root, out_dir, str(remote),
                       lambda root, lv: case_dir, log)
    assert_mesh_certified_at_entry(remote, cell.family, cell.cell_id)
    start = time.monotonic()
    result = tv._foam(["simpleFoam"], remote, "log.simpleFoam", timeout=5400)
    wall = time.monotonic() - start
    record = _grade(cell, remote, out_dir, wall, result.returncode,
                    qoi_names, settle_on, backstop=backstop,
                    adjusted_settle=adjusted_settle)
    record["cells"] = level.cells
    record["iteration_backstop"] = backstop
    record["patch"] = patch_name
    record["nu"] = nu
    record["re_per_length"] = float(cell.params["re_per_length"])
    shutil.rmtree(remote, ignore_errors=True)
    shutil.rmtree(case_root, ignore_errors=True)
    return record


def run_cell_N(cell: Cell, log: Callable[[str], None], *,
               backstop: int = BATCH_BACKSTOP,
               adjusted_settle: dict[str, Any] | None = None
               ) -> dict[str, Any]:
    """NACA 0012 on the TMR-distributed C-grid, one alpha, one closure.

    ``run_naca_level`` applies the TMR ladder's OWN settle/extraction rules
    (absolute tail-50 spread, ``_extract_record``) and raises when they fail.
    Those rules are not this batch's pre-registered gate, so a raise is
    caught, named on the record, and the on-disk evidence is still graded
    under the design section 4 gate (finding C1,
    CASES_FAMILY_FIRST_PASS_FINDINGS_2026-08-07.md). A workflow-flagged cell
    stays EXCLUDED regardless of how it grades -- conservative on purpose --
    but its gate detail and QoI values are recorded rather than lost.
    """
    level = [lv for lv in tv.NACA_LEVELS if lv.name == "coarse"][0]
    alpha = float(cell.params["alpha_deg"])
    out_dir = cell.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    remote = Path(tv._RUN_ROOT) / f"tmr-naca-a{alpha:g}-{level.name}"
    start = time.monotonic()
    workflow_error: str | None = None
    try:
        with naca_model_context(cell.model):
            try:
                tv.run_naca_level(level, alpha, out_dir, log,
                                  iterations=backstop)
            except RuntimeError as exc:
                workflow_error = str(exc)
        wall = time.monotonic() - start
        # returncode 0 on the clean path is guaranteed by run_naca_level's
        # own raise-on-nonzero (finding C4); a raise lands in workflow_error
        # and the gate below reads the solver log itself.
        record = _grade(cell, remote, out_dir, wall, 0, ("Cd", "Cl"), "Cl",
                        backstop=backstop, adjusted_settle=adjusted_settle)
        if workflow_error is not None:
            record["workflow_error"] = workflow_error
            superseded_by_criterion = (
                "still moving" in workflow_error
                and record.get("settle_criterion", {})
                          .get("admitted_in_place_of_residual_control"))
            if superseded_by_criterion:
                # The workflow's absolute tail-50 settle rule is exactly the
                # clause a pre-registered adjusted criterion replaces; when
                # that criterion admitted the cell, forcing exclusion here
                # would let an unregistered rule outrank the registered one
                # (wrapper defect found 2026-08-08 on the N_a10 SA arm --
                # the criterion passed every clause and the old code
                # excluded anyway). The workflow's message stays on the
                # record; the registered criterion decides.
                record["settle_criterion"]["workflow_rule_superseded"] = (
                    "workflow tail-50 rule fired but is replaced by the "
                    f"pre-registered criterion: {workflow_error}")
            else:
                record["converged"] = False
                record["excluded_reasons"].append(
                    "workflow settle/extraction rule fired (not this batch's "
                    f"gate): {workflow_error}")
        record["cells"] = level.cells
        record["iteration_backstop"] = backstop
        record["alpha_deg"] = alpha
        return record
    finally:
        # Cleanup on every path: the runner-error path used to leak the run
        # directory (finding C7).
        shutil.rmtree(remote, ignore_errors=True)


def _hills_crossings(case_dir: Path, time_name: str) -> list[float]:
    """Bottom-wall skin-friction sign changes, x/h ascending, linear-
    interpolated -- the F6b gate.py logic, with the wall single-valued in x."""
    sys.path.insert(0, str(REPO_ROOT / "demo-output" / "website" / "dafoam"
                           / "f6b_periodic_hills" / "case_breuer_re10595"))
    import foam_io as fio
    mesh = case_dir / "constant" / "polyMesh"
    pts = fio.read_points(str(mesh / "points"))
    faces = fio.read_faces(str(mesh / "faces"))
    start, n = fio.read_boundary(str(mesh / "boundary"))["bottomWall"]
    cent = fio.face_centroids(pts, faces, start, n)
    tau, _ = fio.read_vector_boundary_field(
        str(case_dir / time_name / "wallShearStress"), "bottomWall")
    order = sorted(range(len(cent)), key=lambda i: cent[i][0])
    x = [cent[i][0] for i in order]
    # Cf sign = -tau_x sign (attached flow drags the wall in -x by OpenFOAM's
    # convention here); scale cannot move a zero crossing.
    cf = [-tau[i][0] for i in order]
    out = []
    for i in range(len(cf) - 1):
        if cf[i] == 0.0:
            continue
        if (cf[i] > 0) != (cf[i + 1] > 0):
            frac = cf[i] / (cf[i] - cf[i + 1])
            out.append(x[i] + frac * (x[i + 1] - x[i]))
    return out


def _hills_first_crossing_is_separation(case_dir: Path, time_name: str,
                                        crossings: Sequence[float]) -> bool:
    """G3 direction check: the wall must be attached (Cf > 0) upstream of
    the first crossing."""
    sys.path.insert(0, str(REPO_ROOT / "demo-output" / "website" / "dafoam"
                           / "f6b_periodic_hills" / "case_breuer_re10595"))
    import foam_io as fio
    mesh = case_dir / "constant" / "polyMesh"
    pts = fio.read_points(str(mesh / "points"))
    faces = fio.read_faces(str(mesh / "faces"))
    start, n = fio.read_boundary(str(mesh / "boundary"))["bottomWall"]
    cent = fio.face_centroids(pts, faces, start, n)
    tau, _ = fio.read_vector_boundary_field(
        str(case_dir / time_name / "wallShearStress"), "bottomWall")
    order = sorted(range(len(cent)), key=lambda i: cent[i][0])
    first = crossings[0]
    upstream = [-tau[i][0] for i in order if cent[i][0] < first]
    return bool(upstream) and upstream[0] > 0


def _hills_field_from_omega(omega_text: str, model: str) -> tuple[str, str]:
    """(field name, field text) for the model's extra field, derived from
    the case's own 0/omega exactly as the pre-registration froze it."""
    if model in ("kEpsilon", "realizableKE"):
        eps = C_MU * H_K_INIT * H_OMEGA_INIT
        text = _retype_field(omega_text, obj="epsilon",
                             dimensions="[0 2 -3 0 0 0 0]", value=eps,
                             wall_type="epsilonWallFunction", wall_value=None)
        text = text.replace("type epsilonWallFunction;",
                            "type epsilonWallFunction; lowReCorrection true;")
        text = text.replace("type            epsilonWallFunction;",
                            "type            epsilonWallFunction;\n"
                            "        lowReCorrection true;")
        return "epsilon", text
    text = _retype_field(omega_text, obj="nuTilda",
                         dimensions="[0 2 -1 0 0 0 0]",
                         value=SA_NUTILDA_OVER_NU * H_NU,
                         wall_type="fixedValue", wall_value=0.0)
    return "nuTilda", text


def run_cell_H(cell: Cell, log: Callable[[str], None], *,
               backstop: int = H_BACKSTOP) -> dict[str, Any]:
    """Periodic hills, one closure, on the verified F6b medium case.

    Pre-registration: campaign/MODEL_FORM_H_HILLS_PREREGISTRATION.md. The
    gate differs from the coefficient families by declared deviation: the
    settle clause is the case's own residualControl sentence plus the
    exactly-two-crossings steady-bubble rule (with the G3 direction check);
    there is no coefficient history on this case.
    """
    extra = EXTRA_FIELD[cell.model] if cell.model != "kOmegaSST" else None
    remote = Path(tv._RUN_ROOT) / f"modelform-{cell.cell_id}"
    out_dir = cell.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(remote, ignore_errors=True)
    remote.mkdir(parents=True)
    for sub in ("0", "constant", "system"):
        shutil.copytree(H_SOURCE_CASE / sub, remote / sub)
    shutil.copy2(H_SOURCE_CASE / "log.checkMesh", out_dir / "log.checkMesh")

    (remote / "constant" / "turbulenceProperties").write_text(
        turbulence_properties_for(cell.model), newline="\n")
    if extra:
        field_name, field_text = _hills_field_from_omega(
            (remote / "0" / "omega").read_text(), cell.model)
        (remote / "0" / field_name).write_text(field_text, newline="\n")
        sol_path = remote / "system" / "fvSolution"
        sol = sol_path.read_text()
        if field_name == "nuTilda":
            # clone the omega solver block; epsilon already has one
            sol = sol.replace(
                "    omega\n    {",
                "    nuTilda\n    {\n"
                "        solver          PBiCG;\n"
                "        preconditioner  DILU;\n"
                "        tolerance       1e-09;\n"
                "        relTol          0.1;\n"
                "    }\n\n    omega\n    {", 1)
        sol = sol.replace("        omega   1e-6;",
                          f"        omega   1e-6;\n"
                          f"        {field_name} 1e-6;", 1)
        sol = sol.replace("    omega   0.7;",
                          f"    omega   0.7;\n    {field_name} 0.7;", 1)
        sol_path.write_text(sol, newline="\n")
        sch_path = remote / "system" / "fvSchemes"
        sch = sch_path.read_text()
        sch = sch.replace(
            "    div(phi,omega)  bounded Gauss linearUpwind grad(U);",
            "    div(phi,omega)  bounded Gauss linearUpwind grad(U);\n"
            f"    div(phi,{field_name}) bounded Gauss linearUpwind grad(U);",
            1)
        sch_path.write_text(sch, newline="\n")
    ctrl = remote / "system" / "controlDict"
    ctrl.write_text(re.sub(r"endTime\s+\d+;", f"endTime         {backstop};",
                           ctrl.read_text()), newline="\n")

    assert_mesh_certified_at_entry(remote, cell.family, cell.cell_id,
                                   fallback=out_dir)
    start = time.monotonic()
    result = tv._foam(["simpleFoam"], remote, "log.simpleFoam", timeout=7200)
    wall = time.monotonic() - start
    log_text = (remote / "log.simpleFoam").read_text(errors="replace")
    shutil.copy2(remote / "log.simpleFoam", out_dir / "log.simpleFoam")
    big = out_dir / "log.simpleFoam"
    if big.stat().st_size > 1_000_000:
        subprocess.run(["gzip", "-f", str(big)], check=False)

    logv = log_verdict(log_text)
    meshv = mesh_verdict((out_dir / "log.checkMesh").read_text(errors="replace"))
    times = sorted(int(p.name) for p in remote.iterdir()
                   if p.name.isdigit() and int(p.name) > 0)
    reasons: list[str] = []
    if result.returncode != 0:
        reasons.append(f"solver exit code {result.returncode}")
    reasons.extend(logv["fatal"])
    if not logv["residual_control_met"]:
        last = logv["last_iteration"]
        if last is not None and last >= backstop:
            reasons.append("residualControl not met (stopped on the backstop)")
        else:
            reasons.append("residualControl not met")
    reasons.extend(meshv["breaches"])
    qoi: dict[str, float | None] = {"x_R_over_h": None, "x_S_over_h": None}
    crossings: list[float] = []
    if times:
        t_name = str(times[-1])
        # preserve the final fields with the archive
        shutil.copytree(remote / t_name, out_dir / t_name,
                        dirs_exist_ok=True)
        try:
            crossings = _hills_crossings(remote, t_name)
        except Exception as exc:
            reasons.append(f"crossing extraction failed: {exc}")
        if len(crossings) == 2 and _hills_first_crossing_is_separation(
                remote, t_name, crossings):
            qoi["x_S_over_h"] = round(crossings[0], 6)
            qoi["x_R_over_h"] = round(crossings[1], 6)
        elif crossings or not any("extraction failed" in r for r in reasons):
            reasons.append(
                f"no steady bubble: {len(crossings)} skin-friction sign "
                "changes (a steady separation bubble has exactly 2, "
                "separation first)")
    else:
        reasons.append("no written time directory")

    record = {
        "cell_id": cell.cell_id, "group": cell.group_id,
        "family": cell.family, "regime": cell.regime, "model": cell.model,
        "params": cell.params,
        "converged": not reasons,
        "excluded_reasons": reasons,
        "qoi": qoi,
        "qoi_source": "wallShearStress crossings (bottom wall, final time)",
        "crossings_x_over_h": [round(c, 6) for c in crossings],
        "iterations": logv["converged_at"] or logv["last_iteration"],
        "residual_control_met": logv["residual_control_met"],
        "mesh": meshv,
        "mesh_note": ("COMPLIANT F6b medium mesh (Gate V 0.043%); "
                      "R12 not involved"),
        "cells": 15600,
        "iteration_backstop": backstop,
        "prereg": "campaign/MODEL_FORM_H_HILLS_PREREGISTRATION.md",
        "wall_seconds": round(wall, 1),
        "core_min": round(wall / 60.0, 3),
        "ranks": 1,
        "toolchain": "native OpenFOAM v2606 (openfoam2606 launcher)",
        "timestamp": _now(),
    }
    shutil.rmtree(remote, ignore_errors=True)
    return record


def run_cell(cell: Cell, log: Callable[[str], None], *,
             backstop: int = BATCH_BACKSTOP,
             adjusted_settle: dict[str, Any] | None = None) -> dict[str, Any]:
    if cell.family in ("P", "B"):
        return run_cell_P_or_B(cell, log, backstop=backstop,
                               adjusted_settle=adjusted_settle)
    if cell.family == "H":
        # H's own default applies only when the caller passed the batch
        # default; an explicit --iteration-backstop override is honored
        # (the min() this replaces would have silently capped the approved
        # 30,000-iteration extension arm at 12,000).
        h_backstop = H_BACKSTOP if backstop == BATCH_BACKSTOP else backstop
        return run_cell_H(cell, log, backstop=h_backstop)
    return run_cell_N(cell, log, backstop=backstop,
                      adjusted_settle=adjusted_settle)


# ---------------------------------------------------------------------------
# The band
# ---------------------------------------------------------------------------

def load_records() -> list[dict[str, Any]]:
    records = []
    for path in sorted(OUT_ROOT.glob("*/record.json")):
        try:
            records.append(json.loads(path.read_text()))
        except json.JSONDecodeError:
            continue
    return records


REFERENCES = {
    # (family, regime) -> {qoi: {source: value}}; only where the lab's own
    # record already carries a published reference at this exact condition.
    ("P", "re5e6"): {"Cd": {"CFL3D SST-V (3264 cells)": 0.278506994e-2,
                           "FUN3D SST-V (3264 cells)": 0.2678684e-2}},
    ("B", "re3e6"): {},
    ("N", "a0"): {"Cl": {"CFL3D SST (897x257)": -0.76275807991e-5},
                  "Cd": {"CFL3D SST (897x257)": 0.80937292380e-2}},
    ("N", "a10"): {"Cl": {"CFL3D SST (897x257)": 1.0778080613},
                   "Cd": {"CFL3D SST (897x257)": 1.2362110998e-2}},
    ("N", "a15"): {"Cl": {"CFL3D SST (897x257)": 1.5067867358},
                   "Cd": {"CFL3D SST (897x257)": 2.2186245406e-2}},
    # Family H: the literature reattachment band from the F6b
    # pre-registration's own table. Primary containment test per the H
    # pre-registration = the band midpoint; the individual sources are the
    # secondary read.
    ("H", "re10595"): {"x_R_over_h": {
        "literature band midpoint 4.455 (PRIMARY containment test)": 4.455,
        "Rapp & Manhart 2011 (exp)": 4.21,
        "Froehlich et al. 2005 (LES, 4.6-4.7 midpoint)": 4.65,
        "Breuer et al. 2009 (LES)": 4.69}},
}


def build_band(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, dict[str, Any]] = {}
    for rec in records:
        grp = groups.setdefault(rec["group"], {
            "group": rec["group"], "family": rec["family"],
            "regime": rec["regime"], "converged": [], "excluded": [],
            "core_min": 0.0})
        grp["core_min"] = round(grp["core_min"] + rec.get("core_min", 0.0), 3)
        if rec.get("mesh_gate_exemption"):
            # Ruling R12 condition 1: the exemption is stated on the band
            # artifact itself. Every cell of a group shares one grid, so the
            # group carries the statement once, failing number and all.
            grp["mesh_gate_exemption"] = rec["mesh_gate_exemption"]
        if rec["converged"]:
            grp["converged"].append(rec)
        else:
            grp["excluded"].append(
                {"cell_id": rec["cell_id"], "model": rec["model"],
                 "reasons": rec["excluded_reasons"],
                 "qoi_if_it_had_counted": rec["qoi"]})
    out_groups = []
    for name in sorted(groups):
        grp = groups[name]
        members = grp.pop("converged")
        bands: dict[str, Any] = {}
        qoi_names = sorted({k for m in members for k in m["qoi"]})
        for qoi in qoi_names:
            values = {m["model"]: m["qoi"][qoi] for m in members
                      if m["qoi"].get(qoi) is not None}
            if len(values) < 2:
                bands[qoi] = {"band": None,
                              "why": f"{len(values)} converged member(s); a "
                                     "band needs at least 2",
                              "members": values}
                continue
            lo, hi = min(values.values()), max(values.values())
            mean = sum(values.values()) / len(values)
            entry = {
                "band": [lo, hi], "members": values,
                "n_converged": len(values),
                "spread_abs": hi - lo,
                "spread_rel": (hi - lo) / abs(mean) if mean else None,
                "argmin": min(values, key=values.get),
                "argmax": max(values, key=values.get),
            }
            refs = REFERENCES.get((grp["family"], grp["regime"]), {}).get(qoi)
            if refs:
                entry["reference"] = {
                    src: {"value": val, "contained": lo <= val <= hi}
                    for src, val in refs.items()}
            bands[qoi] = entry
        grp["models_converged"] = sorted(m["model"] for m in members)
        grp["n_converged"] = len(members)
        grp["n_excluded"] = len(grp["excluded"])
        grp["bands"] = bands
        out_groups.append(grp)
    total = sum(r.get("core_min", 0.0) for r in records)
    return {
        "title": "Model-form band, inter-model spread on validated cases",
        "design": "demo-output/website/campaign/MODEL_FORM_BATCH_DESIGN.md",
        "rule": ("min/max over CONVERGED cells only; a group with fewer than "
                 "two converged members has no band. Excluded cells are named "
                 "with their reasons. The band is an interval and is never "
                 "converted to a sigma or folded into an RSS total."),
        "models": list(MODELS),
        "cells_total_designed": len(all_cells()),
        "cells_recorded": len(records),
        "core_min_total": round(total, 2),
        "generated_utc": _now(),
        "groups": out_groups,
    }


def band_markdown(band: dict[str, Any]) -> str:
    lines = ["# Model-form band — converged cells only", "",
             f"Generated {band['generated_utc']} by "
             "`sdk/scripts/model_form_batch.py --band`. Design and "
             "pre-registration: `MODEL_FORM_BATCH_DESIGN.md`.", "",
             f"{band['cells_recorded']} of {band['cells_total_designed']} "
             f"designed cells have run, {band['core_min_total']:.2f} core-min "
             "spent.", "",
             "The band is the min/max across CONVERGED members of a group. An "
             "unconverged cell is excluded and named -- the NASA hump lesson: "
             "the band that failed to contain the experiment was the band "
             "that still had an unconverged member in it.", ""]
    for grp in band["groups"]:
        lines.append(f"## {grp['group']} "
                     f"({grp['n_converged']} converged, "
                     f"{grp['n_excluded']} excluded, "
                     f"{grp['core_min']:.2f} core-min)")
        lines.append("")
        if grp.get("mesh_gate_exemption"):
            lines.append("**Mesh-gate exemption on this group (R12):** "
                         + grp["mesh_gate_exemption"]["statement"])
            lines.append("")
        for qoi, entry in sorted(grp["bands"].items()):
            if entry.get("band") is None:
                lines.append(f"- **{qoi}: no band** — {entry['why']}. "
                             f"Members: {entry['members']}")
                continue
            lo, hi = entry["band"]
            rel = entry["spread_rel"]
            lines.append(f"- **{qoi}: {lo:.6g} to {hi:.6g}** "
                         f"(spread {entry['spread_abs']:.4g}"
                         + (f", {100 * rel:.2f}% of the mean" if rel else "")
                         + f"; low {entry['argmin']}, high {entry['argmax']})")
            for model, value in sorted(entry["members"].items()):
                lines.append(f"  - {model}: {value:.6g}")
            for src, ref in (entry.get("reference") or {}).items():
                verdict = "CONTAINED" if ref["contained"] else "NOT contained"
                lines.append(f"  - reference {src}: {ref['value']:.6g} — "
                             f"**{verdict}** by this band")
        if grp["excluded"]:
            lines.append("")
            lines.append("Excluded from the band:")
            for item in grp["excluded"]:
                lines.append(f"  - {item['model']}: "
                             + "; ".join(item["reasons"]))
        lines.append("")
    return "\n".join(lines) + "\n"


def write_study() -> Path:
    """The flat-plate model-form study, in the uq-studies house format.

    Follows the shape ``models/curriculum/uq-studies/motorBike.json`` already
    uses for its ``closures`` key: model -> value for a converged member,
    model -> {"excluded": reason} for one that failed its gate. One
    ``closures`` block per regime, the band beside it, and the doctrine's own
    rule stated on the record: the band is an interval and never enters the
    RSS quadrature.
    """
    sys.path.insert(0, str(_SDK_ROOT))
    from chief_engineer import uq

    records = [r for r in load_records() if r["family"] == "P"]
    regimes: dict[str, Any] = {}
    provenance: list[str] = []
    for tag in P_REGIMES:
        members = [r for r in records if r["regime"] == tag]
        if not members:
            continue
        closures: dict[str, Any] = {}
        for rec in sorted(members, key=lambda r: r["model"]):
            provenance.append(rec["cell_id"])
            if rec["converged"]:
                closures[rec["model"]] = rec["qoi"]["Cd"]
            else:
                closures[rec["model"]] = {
                    "excluded": "; ".join(rec["excluded_reasons"])}
        values = [v for v in closures.values() if isinstance(v, float)]
        entry: dict[str, Any] = {
            "re_per_length": P_REGIMES[tag],
            "closures": closures,
            "n_converged": len(values),
        }
        if len(values) >= 2:
            entry["model_form_band_cd"] = [min(values), max(values)]
            entry["spread_abs"] = max(values) - min(values)
        else:
            entry["model_form_band_cd"] = None
            entry["why_no_band"] = (f"{len(values)} converged member(s); "
                                    "a band needs at least 2")
        refs = REFERENCES.get(("P", tag), {}).get("Cd")
        if refs and entry["model_form_band_cd"]:
            lo, hi = entry["model_form_band_cd"]
            entry["reference"] = {src: {"value": val,
                                        "contained": lo <= val <= hi}
                                  for src, val in refs.items()}
        regimes[tag] = entry
    study = {
        "body": "tmr_flatplate_modelform",
        "case": ("TMR 2-D zero-pressure-gradient flat plate, medium rung "
                 "(3264 cells, TMR 69x49), simpleFoam, "
                 "native OpenFOAM v2606"),
        "quantity": "Cd (plate drag, Aref = plate area 2)",
        "method": ("inter-model spread across kOmegaSST, SpalartAllmaras, "
                   "kEpsilon and realizableKE on an identical mesh, schemes "
                   "and residual targets; band = min/max over CONVERGED "
                   "members only, per the pre-registered gate in "
                   "demo-output/website/campaign/MODEL_FORM_BATCH_DESIGN.md. "
                   "The band is an interval, carried beside the other "
                   "channels and never converted to a sigma inside the RSS "
                   "quadrature."),
        "regimes": regimes,
        "provenance": provenance,
        "design": "demo-output/website/campaign/MODEL_FORM_BATCH_DESIGN.md",
        "band_artifact": "demo-output/website/campaign/MODEL_FORM_BAND.json",
    }
    return uq.save_study("tmr_flatplate_modelform", study)


def write_band() -> dict[str, Any]:
    band = build_band(load_records())
    BAND_JSON.write_text(json.dumps(band, indent=2, sort_keys=True) + "\n",
                         newline="\n")
    BAND_MD.write_text(band_markdown(band), newline="\n")
    return band


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _logger() -> Callable[[str], None]:
    RUNNER_LOG.parent.mkdir(parents=True, exist_ok=True)

    def log(message: str) -> None:
        line = f"[{_now()}] {message}"
        print(line, flush=True)
        with RUNNER_LOG.open("a") as handle:
            handle.write(line + "\n")

    return log


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--family", action="append",
                        choices=["P", "B", "N", "H"],
                        help="restrict to one or more families (repeatable)")
    parser.add_argument("--model", action="append", choices=list(MODELS))
    parser.add_argument("--regime", action="append")
    parser.add_argument("--max-core-min", type=float, default=60.0,
                        help="session budget; the runner stops before "
                             "starting a cell that would exceed it")
    parser.add_argument("--max-queue-wait", type=float, default=900.0,
                        help="seconds to wait for the solver fleet to free a "
                             "slot before giving up (this batch always yields)")
    parser.add_argument("--list", action="store_true",
                        help="print every cell and its state, run nothing")
    parser.add_argument("--iteration-backstop", type=int,
                        default=BATCH_BACKSTOP,
                        help="iteration cap per cell; the gate is the case's "
                             "own residualControl, this only bounds a cell "
                             "that never meets it")
    parser.add_argument("--redo-excluded", action="store_true",
                        help="re-run cells whose record says EXCLUDED, "
                             "superseding the old record rather than deleting "
                             "it (record_superseded_<timestamp>.json is kept "
                             "beside the new one)")
    parser.add_argument("--redo-reason", default=None,
                        help="with --redo-excluded, only cells whose reasons "
                             "contain this substring")
    parser.add_argument("--adjusted-settle", default=None, metavar="SPEC.json",
                        help="path to a COMMITTED pre-registered settle "
                             "criterion spec; replaces only the convergence-"
                             "sentence clause for the cells this run grades, "
                             "with every threshold and measurement stamped "
                             "into the record's settle_criterion block")
    parser.add_argument("--band", action="store_true",
                        help="rebuild the band artifact from the records "
                             "already on disk, run nothing")
    parser.add_argument("--study", action="store_true",
                        help="write the flat-plate model-form study record "
                             "into models/curriculum/uq-studies, run nothing")
    args = parser.parse_args(argv)

    cells = all_cells()
    if args.family:
        cells = [c for c in cells if c.family in args.family]
    if args.model:
        cells = [c for c in cells if c.model in args.model]
    if args.regime:
        cells = [c for c in cells if c.regime in args.regime]

    if args.list:
        for cell in cells:
            record_path = cell.out_dir / "record.json"
            if record_path.exists():
                rec = json.loads(record_path.read_text())
                state = ("converged" if rec["converged"]
                         else "EXCLUDED: " + "; ".join(rec["excluded_reasons"]))
                state += f" ({rec.get('core_min', 0):.2f} core-min)"
            else:
                state = "pending"
            print(f"{cell.cell_id:36s} {state}")
        return 0

    if args.study:
        print(write_study())
        return 0

    if args.band:
        band = write_band()
        print(json.dumps({"groups": len(band["groups"]),
                          "cells_recorded": band["cells_recorded"],
                          "core_min_total": band["core_min_total"]}, indent=2))
        return 0

    log = _logger()
    adjusted_settle: dict[str, Any] | None = None
    if args.adjusted_settle:
        adjusted_settle = json.loads(Path(args.adjusted_settle).read_text())
    spent = 0.0
    log(f"model-form batch starting: {len(cells)} cell(s) in scope, budget "
        f"{args.max_core_min:.1f} core-min"
        + (f"; ADJUSTED settle criterion from {args.adjusted_settle} "
           f"(prereg {adjusted_settle.get('prereg')})"
           if adjusted_settle else ""))
    for cell in cells:
        record_path = cell.out_dir / "record.json"
        existing: dict[str, Any] | None = None
        if record_path.exists():
            existing = json.loads(record_path.read_text())
            redo = (args.redo_excluded and not existing["converged"]
                    and (args.redo_reason is None
                         or any(args.redo_reason in r
                                for r in existing["excluded_reasons"])))
            if not redo:
                log(f"{cell.cell_id}: already recorded, skipping")
                continue
        if spent >= args.max_core_min:
            log(f"budget reached ({spent:.2f} core-min); stopping before "
                f"{cell.cell_id}")
            break
        if not wait_for_slot(log, max_wait=args.max_queue_wait):
            break
        if existing is not None:
            # Superseded, never deleted: the reason a cell was excluded is
            # what a later reading of this batch needs. Renamed only AFTER
            # the budget and queue checks pass: renaming earlier could leave
            # a cell with no live record when the session stopped between
            # the rename and the run (finding C3).
            stamp = _now().replace(":", "").replace("-", "")
            record_path.rename(cell.out_dir / f"record_superseded_{stamp}.json")
            log(f"{cell.cell_id}: superseding an excluded record "
                f"({'; '.join(existing['excluded_reasons'])})")
        log(f"{cell.cell_id}: starting")
        began = time.monotonic()
        try:
            record = run_cell(cell, log,
                              backstop=args.iteration_backstop,
                              adjusted_settle=adjusted_settle)
        except Exception as exc:  # a failed cell is data, not a crash
            wall = time.monotonic() - began
            record = {
                "cell_id": cell.cell_id, "group": cell.group_id,
                "family": cell.family, "regime": cell.regime,
                "model": cell.model, "params": cell.params,
                "converged": False,
                "excluded_reasons": [f"runner error: {exc}"],
                "qoi": {}, "wall_seconds": round(wall, 1),
                "core_min": round(wall / 60.0, 3), "ranks": 1,
                "timestamp": _now(),
            }
        _write_record(cell, record)
        spent += record.get("core_min", 0.0)
        verdict = ("CONVERGED" if record["converged"]
                   else "EXCLUDED (" + "; ".join(record["excluded_reasons"])
                        + ")")
        log(f"{cell.cell_id}: {verdict}; qoi {record.get('qoi')}; "
            f"{record.get('core_min', 0):.2f} core-min "
            f"(session {spent:.2f}/{args.max_core_min:.1f})")
        write_band()
    write_band()
    log(f"model-form batch stopping: {spent:.2f} core-min spent this run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
