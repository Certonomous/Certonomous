#!/usr/bin/env python3
"""Prescribed-Reynolds-stress forward model on PH10595 -- the `tauFoam` role in
Xiao et al. 2016 sec. 5.1, built from the ALREADY-VALIDATED interface rather than
from new solver code.

Mechanism. `kOmegaSSTCorrected` (sdk/openfoam/sparta) is run with
`turbulence off;` so neither k nor omega is transported and nu_t is frozen at
whatever is written into the start-time directory. The momentum equation then
carries

    tau_model = (2/3) k I  -  2 nu_t S  +  2 k bijDelta

with k and nu_t frozen fields. Setting

    bijDelta = b_target + (nu_t / k) S            (W2 Eq. 2-3 convention)

makes tau_model == tau_target EXACTLY once S has converged, while the linear
-2 nu_t S part stays IMPLICIT -- which is Wu et al. (2019)'s conditioning fix,
flag F19. Because S changes as U changes, bijDelta is refreshed in an outer
deferred-correction loop until the velocity field stops moving.

So the stress CARRIES k by construction: k is a component of the prescribed
tau, not something a transport equation is left to invent. That is the property
the Kaandorp lane's H0 GATE FAIL showed b-only-with-transported-k does not have.

No new solver. No file under sdk/ or the benchmark clone is written.
"""
from __future__ import annotations
import os, re, sys, json, time, shutil, subprocess
import numpy as np

COMMON = "/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/_common"
KDIR = "/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori"
sys.path.insert(0, COMMON); sys.path.insert(0, KDIR)
from of_read import (read_field, read_field_expand, latest_time_dir, sym_to_full,
                     structured_gradient, plane_axes)
import sst_baseline_metrics as SB
from setup_case import patch_bcs, write_field

BENCH = SB.DATA
# DEPARTURE 1 (2026-08-21): the case is selectable so the registered Re-switch
# re-test runs the SAME code path as the frozen PH10595 harness.
_CASES = {"PHLL10595": (os.path.join(BENCH, "PH_Breuer"), 0.1565),
          "alpha_10_9000_3036": (os.path.join(BENCH, "Parm_PH_29", "alpha_10",
                                              "alpha_10_9000_3036"), 0.1556)}
CASE_NAME = os.environ.get("XIAO_CASE", "PHLL10595")
CASE_SRC, SST_URMS = _CASES[CASE_NAME]
ROOT = "/home/ubuntu/closure-data/xiao"
FOAM = "source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1"
IDX6 = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
K_FLOOR_FRAC = 1e-4


def base():
    d = SB.load_case(CASE_NAME, CASE_SRC, "hill")
    d["t0"] = latest_time_dir(CASE_SRC)
    d["nut"] = read_field(os.path.join(CASE_SRC, d["t0"], "nut"))
    return d


def make_case(name, d, iters=4000, write_every=1000):
    case = os.path.join(ROOT, name)
    if os.path.exists(case):
        shutil.rmtree(case)
    shutil.copytree(CASE_SRC, case)
    for junk in ("postProcessing", "convergencePlots", "dynamicCode", "VTK"):
        shutil.rmtree(os.path.join(case, junk), ignore_errors=True)
    t0 = d["t0"]
    cd = os.path.join(case, "system", "controlDict")
    s = open(cd).read()
    # Some benchmark cases carry no `libs` entry at all (the 29 parametric hills),
    # others name a library that does not exist on this machine. Either way the
    # sparta library must be loaded or kOmegaSSTCorrected is not a known model.
    LIBS = 'libs ( "libspartaTurbulenceModels.so" );'
    if re.search(r"libs\s*\(", s):
        s = re.sub(r"libs\s*\([^)]*\)\s*;", lambda m: LIBS, s)
    else:
        m = re.search(r"\n// \* \* \*[^\n]*\n", s)
        s = s[:m.end()] + "\n" + LIBS + "\n" + s[m.end():]
    assert "libspartaTurbulenceModels" in s, "libs entry not inserted"
    s = re.sub(r"startTime\s+\S+;", "", s)
    s = re.sub(r"startFrom\s+\w+;", f"startFrom       startTime;\nstartTime       {t0};", s)
    s = re.sub(r"endTime\s+\S+;", f"endTime         {int(t0) + iters};", s)
    s = re.sub(r"writeInterval\s+\S+;", f"writeInterval   {write_every};", s)
    s = re.sub(r"functions\s*\{.*?\n\}", "functions\n{\n}", s, flags=re.S)
    open(cd, "w").write(s)
    tp = os.path.join(case, "constant", "turbulenceProperties")
    txt = open(tp).read()
    txt = re.sub(r"RASModel\s+\w+\s*;", "RASModel        kOmegaSSTCorrected;", txt)
    txt = re.sub(r"turbulence\s+\w+\s*;", "turbulence      off;", txt)
    open(tp, "w").write(txt)
    fp = os.path.join(case, "system", "fvSolution")
    fs = open(fp).read()
    fs = re.sub(r"residualControl\s*\{[^}]*\}",
                "residualControl\n    {\n        p               1e-6;\n"
                "        U               1e-6;\n    }", fs, flags=re.S)
    open(fp, "w").write(fs)
    return case, t0


def optimal_nut(tau_target, S, k):
    """Wu, Sun, Xiao & Wang (2019) conditioning fix, flag F16/F19: split tau into
    the LINEAR part that a nonnegative eddy viscosity can represent, treated
    implicitly, plus an explicit remainder orthogonal to S by construction.

        nu_t^L = - <tau_dev : S> / (2 <S:S>),   clipped at 0.

    Using the baseline SST nu_t instead leaves a large explicit remainder that is
    NOT orthogonal to S, and the outer deferred-correction loop then oscillates:
    measured max|dU|/|U| of 0.58, 0.18, 0.31 over three outer iterations with the
    LES truth stress prescribed (harness.json, `H0_truth` run of 2026-08-21).
    """
    dev = tau_target - (2.0 / 3.0) * k[:, None, None] * np.eye(3)[None]
    num = -np.einsum("nij,nij->n", dev, S)
    den = 2.0 * np.einsum("nij,nij->n", S, S)
    nut = np.where(den > 1e-30, num / np.maximum(den, 1e-30), 0.0)
    clipped = int((nut < 0).sum())
    return np.maximum(nut, 0.0), clipped


def write_state(case, t, d, tau_target, S, nut_mode="opt", nut_prev=None,
                relax=0.5):
    """Write k, nut, bijDelta, kDeficit consistent with tau_target and this S."""
    n = d["n"]
    k = np.maximum(0.5 * np.einsum("nii->n", tau_target), 1e-12)
    kref = float(np.mean(np.abs(d["k_LES"])))
    ok = k > K_FLOOR_FRAC * kref
    b = tau_target / (2.0 * k[:, None, None]) - np.eye(3)[None] / 3.0
    if nut_mode == "opt":
        nut, nclip = optimal_nut(tau_target, S, k)
        if nut_prev is not None:
            nut = relax * nut + (1.0 - relax) * nut_prev
    else:
        nut, nclip = d["nut"], 0
    lin = np.zeros_like(S)
    lin[ok] = (nut[ok] / k[ok])[:, None, None] * S[ok]
    bd = np.where(ok[:, None, None], b + lin, 0.0)
    bd = np.nan_to_num(bd, nan=0.0, posinf=0.0, neginf=0.0)
    td = os.path.join(case, str(t))
    os.makedirs(td, exist_ok=True)
    for src in ("U", "p", "phi"):
        s = os.path.join(case, str(d["t0"]), src)
        if os.path.exists(s) and not os.path.exists(os.path.join(td, src)):
            shutil.copy(s, os.path.join(td, src))
    # k and nut keep the case's own boundaryField
    for name, vals, ncomp in (("k", k, 1), ("nut", nut, 1)):
        p = os.path.join(case, str(d["t0"]), name)
        s = open(p).read()
        i = s.index("internalField"); j = s.index("boundaryField")
        rows = "\n".join(f"{v:.10g}" for v in vals)
        open(os.path.join(td, name), "w").write(
            s[:i] + f"internalField   nonuniform List<scalar>\n{len(vals)}\n(\n{rows}\n)\n;\n\n"
            + s[j:])
    if not os.path.exists(os.path.join(td, "omega")):
        shutil.copy(os.path.join(case, str(d["t0"]), "omega"), os.path.join(td, "omega"))
    write_field(os.path.join(td, "kDeficit"), "kDeficit", "volScalarField",
                "[0 2 -3 0 0 0 0]", 0, case, 1)
    write_field(os.path.join(td, "bijDelta"), "bijDelta", "volSymmTensorField",
                "[0 0 0 0 0 0 0]", np.stack([bd[:, i, j] for i, j in IDX6], axis=1),
                case, 6)
    return nut, nclip


def run(case, timeout_s=1200):
    t = time.time()
    r = subprocess.run(f"{FOAM}; cd {case} && timeout {timeout_s} simpleFoam -case . "
                       f">> log.run 2>&1", shell=True, executable="/bin/bash")
    return r.returncode, time.time() - t


def latest(case, after):
    c = [(float(x), x) for x in os.listdir(case)
         if os.path.isdir(os.path.join(case, x))
         and os.path.exists(os.path.join(case, x, "U"))
         and _f(x) is not None and _f(x) > float(after)]
    return max(c)[1] if c else None


def _f(x):
    try:
        return float(x)
    except ValueError:
        return None


def forward(name, tau_target, d, outer=3, iters=4000, timeout_s=1200,
            nut_mode="opt", relax=0.5):
    """One prescribed-tau forward evaluation. Returns U and a cost record."""
    case, t0 = make_case(name, d, iters=iters)
    S = 0.5 * (np.asarray(d["gradU"]).reshape(-1, 3, 3).transpose(0, 2, 1)
               + np.asarray(d["gradU"]).reshape(-1, 3, 3))
    t = int(t0)
    rec = {"outer": [], "case": case, "nut_mode": nut_mode, "relax": relax}
    U = d["U"]
    nut_prev = None
    for it in range(outer):
        nut_prev, nclip = write_state(case, t, d, tau_target, S, nut_mode,
                                      nut_prev, relax)
        cd = os.path.join(case, "system", "controlDict")
        s = open(cd).read()
        s = re.sub(r"startTime\s+\S+;", f"startTime       {t};", s)
        s = re.sub(r"endTime\s+\S+;", f"endTime         {t + iters};", s)
        open(cd, "w").write(s)
        rc, wall = run(case, timeout_s)
        tw = latest(case, t)
        if tw is None:
            rec["outer"].append(dict(rc=rc, wall_s=round(wall, 1), failed=True))
            break
        Unew = read_field(os.path.join(case, tw, "U"))
        mv = float(np.abs(Unew - U).max() / max(np.abs(Unew).max(), 1e-30))
        rec["outer"].append(dict(rc=rc, wall_s=round(wall, 1), t_end=tw,
                                 max_dU_rel=mv, n_nut_clipped=nclip,
                                 iters=int(float(tw)) - t))
        U = Unew
        A = structured_gradient(d["C"], U)
        S = 0.5 * (A + A.transpose(0, 2, 1))
        t = int(float(tw))
        if mv < 1e-5:
            break
    rec["wall_total_s"] = round(sum(o["wall_s"] for o in rec["outer"]), 1)
    rec["iters_total"] = int(sum(o.get("iters", 0) for o in rec["outer"]))
    return U, rec


def metrics(U, d):
    UL = d["U_LES"]
    uref = float(np.mean(np.linalg.norm(UL, axis=1)))
    e = np.linalg.norm(U - UL, axis=1)
    A = structured_gradient(d["C"], U)
    dv = np.einsum("nii->n", A)
    g = float(np.sqrt((A ** 2).sum(axis=(1, 2)).mean()))
    return dict(U_rms=float(np.sqrt((e ** 2).mean()) / uref),
                U_mae=float(e.mean() / uref),
                divU=float(np.sqrt((dv ** 2).mean()) / g))


if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    d = base()
    out = {}
    # G0: prescribe the BASELINE SST stress -> must reproduce the baseline field
    S0 = 0.5 * (np.asarray(d["gradU"]).reshape(-1, 3, 3).transpose(0, 2, 1)
                + np.asarray(d["gradU"]).reshape(-1, 3, 3))
    tau_sst = ((2.0 / 3.0) * d["k"])[:, None, None] * np.eye(3)[None] \
        - 2.0 * d["nut"][:, None, None] * S0
    tag = CASE_NAME
    U0, r0 = forward(f"G0_sst_{tag}", tau_sst, d, outer=4, iters=2000, nut_mode="opt")
    out["G0_sst"] = dict(**metrics(U0, d), **r0)
    print("[G0] prescribe baseline SST stress:", json.dumps(out["G0_sst"], indent=1),
          flush=True)
    # H0 harness: prescribe the LES TRUTH stress
    U1, r1 = forward(f"H0_truth_{tag}", sym_to_full(d["tau_LES"]), d,
                     outer=6, iters=2000, timeout_s=1800, nut_mode="opt")
    out["H0_truth"] = dict(**metrics(U1, d), **r1)
    print("[H0] prescribe LES truth stress:", json.dumps(out["H0_truth"], indent=1),
          flush=True)
    out["case"] = CASE_NAME; out["sst_U_rms_baseline"] = SST_URMS
    json.dump(out, open(os.path.join(ROOT, f"harness_{CASE_NAME}.json"), "w"), indent=1)
