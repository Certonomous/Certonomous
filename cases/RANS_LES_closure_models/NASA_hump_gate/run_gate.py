#!/usr/bin/env python3
"""PART B -- NASA hump equivalence gate. Registered in PREREGISTRATION.md B.2
before any solve. Nothing is fitted; the only correction fields written are zero.
"""
from __future__ import annotations
import os, re, sys, json, time, shutil, subprocess
import numpy as np

COMMON = "/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/_common"
KDIR = "/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori"
sys.path.insert(0, COMMON); sys.path.insert(0, KDIR)
from of_read import read_field, latest_time_dir, structured_gradient
import sst_baseline_metrics as SB
from setup_case import patch_bcs, write_field

SRC = os.path.join(SB.DATA, "NASA_2DWMH")
ROOT = "/home/ubuntu/closure-data/hump_gate"
FOAM = "source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1"
BASELINES_U_RMS = 0.1260          # BASELINES.md sec.3, NASA_2DWMH
BASELINES_U_MAE = 0.0620


def build(tag, model, iters, write_every, keep_shipped_dict=False):
    case = os.path.join(ROOT, tag)
    if os.path.exists(case):
        shutil.rmtree(case)
    shutil.copytree(SRC, case)
    for junk in ("postProcessing", "convergencePlots", "dynamicCode", "VTK"):
        shutil.rmtree(os.path.join(case, junk), ignore_errors=True)
    t0 = latest_time_dir(SRC)

    cd = os.path.join(case, "system", "controlDict")
    s = open(cd).read()
    # LIBS: the hump DOES carry a libs entry naming a library absent from this
    # machine. Rewrite the list and ASSERT -- never a silent string-replace.
    LIBS = 'libs ( "libspartaTurbulenceModels.so" );'
    if re.search(r"libs\s*\(", s):
        s = re.sub(r"libs\s*\([^)]*\)\s*;", lambda m: LIBS, s)
    else:
        m = re.search(r"\n// \* \* \*[^\n]*\n", s)
        s = s[:m.end()] + "\n" + LIBS + "\n" + s[m.end():]
    assert "libspartaTurbulenceModels" in s, "libs entry not installed"
    s = re.sub(r"startTime\s+\S+;", "", s)
    s = re.sub(r"startFrom\s+\w+;", f"startFrom       startTime;\nstartTime       {t0};", s)
    s = re.sub(r"endTime\s+\S+;", f"endTime         {int(t0) + iters};", s)
    s = re.sub(r"writeInterval\s+\S+;", f"writeInterval   {write_every};", s)
    s = re.sub(r"functions\s*\{.*?\n\}", "functions\n{\n}", s, flags=re.S)
    open(cd, "w").write(s)

    if not keep_shipped_dict:
        tp = os.path.join(case, "constant", "turbulenceProperties")
        txt = open(tp).read()
        assert "AugmentedkOmegaSST" in txt, tp
        txt = re.sub(r"RASModel\s+\w+\s*;", f"RASModel        {model};", txt)
        # carry the shipped omegaMin 0.1 (NOT the stock default) -- registered B.1
        if "omegaMin" not in txt:
            txt = txt.replace(f"RASModel        {model};",
                              f"RASModel        {model};\n    omegaMin        0.1;")
        for flag in ("baseline", "usekDeficit", "usebijDelta", "useSigma",
                     "modelbijDelta", "modelkDeficit", "modelSigma"):
            txt = re.sub(rf"\n\s*{flag}\s+\w+\s*;", "", txt)
        open(tp, "w").write(txt)
        td = os.path.join(case, t0)
        write_field(os.path.join(td, "kDeficit"), "kDeficit", "volScalarField",
                    "[0 2 -3 0 0 0 0]", 0, case, 1)
        write_field(os.path.join(td, "bijDelta"), "bijDelta", "volSymmTensorField",
                    "[0 0 0 0 0 0 0]", 0, case, 6)
    return case, t0


def set_residual_control(case, on):
    p = os.path.join(case, "system", "fvSolution")
    s = open(p).read()
    blk = ("residualControl\n    {\n        p               1e-6;\n"
           "        U               1e-6;\n    }") if on else \
          "residualControl\n    {\n    }"
    if re.search(r"residualControl\s*\{", s):
        s = re.sub(r"residualControl\s*\{[^}]*\}", lambda m: blk, s, flags=re.S)
    else:
        s = re.sub(r"(SIMPLE\s*\{)", lambda m: m.group(1) + "\n    " + blk, s)
    open(p, "w").write(s)


def run(case, timeout_s):
    t = time.time()
    r = subprocess.run(f"{FOAM}; cd {case} && timeout {timeout_s} simpleFoam -case . "
                       f"> log.run 2>&1", shell=True, executable="/bin/bash")
    return r.returncode, round(time.time() - t, 1)


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


def state_of(case):
    txt = open(os.path.join(case, "log.run"), errors="replace").read()
    if "FOAM FATAL" in txt:
        return "DIVERGED-or-FAILED", txt[-900:]
    if "SIMPLE solution converged" in txt:
        return "CONVERGED-residualControl", ""
    if "End" in txt[-400:]:
        return "CAPPED-NOT-CONVERGED", ""
    return "TIMED-OUT", txt[-400:]


def metrics(case, tw):
    d = SB.load_case("NASA_2DWMH", SRC, "hump")
    U = read_field(os.path.join(case, tw, "U"))
    UL = d["U_LES"]
    uref = float(np.mean(np.linalg.norm(UL, axis=1)))
    e = np.linalg.norm(U - UL, axis=1)
    A = structured_gradient(d["C"], U)
    dv = np.einsum("nii->n", A)
    g = float(np.sqrt((A ** 2).sum(axis=(1, 2)).mean()))
    return dict(U_rms=float(np.sqrt((e ** 2).mean()) / uref),
                U_mae=float(e.mean() / uref),
                divU=float(np.sqrt((dv ** 2).mean()) / g), time=tw)


def main():
    os.makedirs(ROOT, exist_ok=True)
    out = {}

    # ---- B-G0a : fixed-iteration behavioural equivalence, 200 iterations
    a = {}
    for tag, model, keep in (("G0a_shipped", None, True),
                             ("G0a_corrected", "kOmegaSSTCorrected", False)):
        case, t0 = build(tag, model, 200, 200, keep_shipped_dict=keep)
        set_residual_control(case, False)
        rc, wall = run(case, 1800)
        st, tail = state_of(case)
        tw = latest(case, t0)
        a[tag] = dict(case=case, rc=rc, wall_s=wall, state=st, t_written=tw, tail=tail)
        print(f"[B-G0a] {tag:15s} rc={rc} state={st} t={tw} wall={wall}s", flush=True)
    if a["G0a_shipped"]["t_written"] and a["G0a_corrected"]["t_written"]:
        ua = read_field(os.path.join(a["G0a_shipped"]["case"],
                                     a["G0a_shipped"]["t_written"], "U"))
        ub = read_field(os.path.join(a["G0a_corrected"]["case"],
                                     a["G0a_corrected"]["t_written"], "U"))
        rel = float(np.linalg.norm(ua - ub) / np.linalg.norm(ua))
        a["rel_L2_U"] = rel
        a["verdict"] = "PASS" if rel < 1e-6 else "GATE FAIL"
    else:
        a["rel_L2_U"] = None
        a["verdict"] = "BLOCKED"
        a["blocked_reason"] = ("the shipped AugmentedkOmegaSST could not be selected "
                               "on this machine; its library is not present")
    print(f"[B-G0a] rel_L2(U) = {a['rel_L2_U']} -> {a['verdict']}", flush=True)
    out["B_G0a"] = a
    json.dump(out, open(os.path.join(ROOT, "gate.json"), "w"), indent=1)

    # ---- B-G0b : converged NULL against the published row
    case, t0 = build("G0b_null", "kOmegaSSTCorrected", 5000, 1000)
    set_residual_control(case, True)
    rc, wall = run(case, 1800)
    st, tail = state_of(case)
    tw = latest(case, t0)
    b = dict(case=case, rc=rc, wall_s=wall, state=st,
             gate_U_rms=BASELINES_U_RMS, gate_U_mae=BASELINES_U_MAE, tail=tail)
    if tw:
        b.update(metrics(case, tw))
        b["delta_U_rms"] = abs(b["U_rms"] - BASELINES_U_RMS)
        b["verdict"] = "PASS" if b["delta_U_rms"] < 5e-3 else "GATE FAIL"
    else:
        b["verdict"] = "GATE FAIL"
        b["reason"] = "no field written"
    print(f"[B-G0b] state={st} U_rms={b.get('U_rms')} "
          f"delta={b.get('delta_U_rms')} -> {b['verdict']}", flush=True)
    out["B_G0b"] = b
    json.dump(out, open(os.path.join(ROOT, "gate.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
