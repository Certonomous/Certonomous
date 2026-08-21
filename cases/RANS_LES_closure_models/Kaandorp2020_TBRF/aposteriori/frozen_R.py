#!/usr/bin/env python3
"""POST-HOC diagnostic (decided AFTER the preregistered H0 gate failed).

Registered choice sec. 2.3 set the k-equation correction R = 0, because the TBRF
predicts b only. The H0 truth-injection gate then failed: injecting the TRUE
anisotropy made U worse, with k collapsing from 26.7 to 8.7.

This script asks the one question that separates "the b-only ceiling is weak"
from "the propagation path is broken": run Schmelzer's k-corrective-frozen-RANS
step (kCorrectiveFrozenFoam, sdk/openfoam/sparta, validated in
verification/campaign/W2_SPARTA_FROZEN_CBFS.md) to EXTRACT R and bijDelta from the
LES fields, then propagate BOTH. If U then improves, the path works and R is what
was missing.

NOT a preregistered configuration. Carries no verdict.
"""
from __future__ import annotations
import os, re, sys, json, time, shutil, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = "/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/_common"
sys.path.insert(0, HERE); sys.path.insert(0, COMMON)
from setup_case import build, CASES, ROOT, patch_bcs
from of_read import read_field, latest_time_dir
import sst_baseline_metrics as SB
import run_lane as RL

FOAM = "source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1"


def swap_internal(path, vals, ncomp):
    """Replace internalField of an existing OpenFOAM field, keep boundaryField."""
    s = open(path).read()
    i = s.index("internalField")
    j = s.index("boundaryField")
    if ncomp == 1:
        rows = "\n".join(f"{v:.10g}" for v in vals)
        typ = "scalar"
    else:
        rows = "\n".join("(" + " ".join(f"{c:.10g}" for c in r) + ")" for r in vals)
        typ = "vector" if ncomp == 3 else "symmTensor"
    body = (f"internalField   nonuniform List<{typ}>\n{len(vals)}\n(\n{rows}\n)\n;\n\n")
    open(path, "w").write(s[:i] + body + s[j:])


def frozen(tag):
    src, fam = CASES[tag]
    d = SB.load_case(tag, src, fam)
    case = os.path.join(ROOT, f"{tag}__FROZENEXTRACT")
    if os.path.exists(case):
        shutil.rmtree(case)
    shutil.copytree(src, case)
    for junk in ("postProcessing", "convergencePlots", "dynamicCode", "VTK"):
        shutil.rmtree(os.path.join(case, junk), ignore_errors=True)
    t0 = latest_time_dir(src)
    td = os.path.join(case, t0)
    swap_internal(os.path.join(td, "U"), d["U_LES"], 3)
    swap_internal(os.path.join(td, "k"), d["k_LES"], 1)
    tau = np.asarray(d["tau_LES"])
    rows = "\n".join("(" + " ".join(f"{c:.10g}" for c in r) + ")" for r in tau)
    open(os.path.join(td, "tauij"), "w").write(
        "FoamFile { version 2.0; format ascii; class volSymmTensorField; object tauij; }\n"
        "dimensions      [0 2 -2 0 0 0 0];\n"
        f"internalField   nonuniform List<symmTensor>\n{len(tau)}\n(\n{rows}\n)\n;\n"
        + patch_bcs(case, 6))
    cd = os.path.join(case, "system", "controlDict")
    s = open(cd).read()
    s = s.replace('libs ( "libfrozenIncompressibleTurbulenceModels.so" );',
                  'libs ( "libspartaTurbulenceModels.so" );')
    s = re.sub(r"startTime\s+\S+;", "", s)
    s = re.sub(r"startFrom\s+\w+;", f"startFrom       startTime;\nstartTime       {t0};", s)
    s = re.sub(r"endTime\s+\S+;", f"endTime         {int(t0) + 5000};", s)
    s = re.sub(r"writeInterval\s+\S+;", "writeInterval   5000;", s)
    s = re.sub(r"functions\s*\{.*?\n\}", "functions\n{\n}", s, flags=re.S)
    open(cd, "w").write(s)
    tp = os.path.join(case, "constant", "turbulenceProperties")
    txt = open(tp).read()
    open(tp, "w").write(re.sub(r"RASModel\s+\w+\s*;", "RASModel        kOmegaSSTFrozen;", txt))
    t = time.time()
    r = subprocess.run(f"{FOAM}; cd {case} && timeout 1800 kCorrectiveFrozenFoam -case . "
                       f"> log.frozen 2>&1", shell=True, executable="/bin/bash")
    return case, t0, dict(rc=r.returncode, wall_s=round(time.time() - t, 1))


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "AR_1_Ret_360"
    out = {}
    case, t0, r = frozen(tag)
    tail = open(os.path.join(case, "log.frozen"), errors="replace").read()[-1500:]
    out["frozen"] = dict(case=case, **r, tail=tail[-700:])
    print(f"[frozen] {tag} rc={r['rc']} {r['wall_s']}s", flush=True)
    tw = None
    for x in os.listdir(case):
        p = os.path.join(case, x)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "kDeficit")):
            try:
                if float(x) > float(t0):
                    tw = x if tw is None or float(x) > float(tw) else tw
            except ValueError:
                pass
    if tw is None:
        out["status"] = "BLOCKED: frozen extraction wrote no kDeficit"
        print(out["status"], tail[-600:], flush=True)
        json.dump(out, open(os.path.join(ROOT, "frozen_R.json"), "w"), indent=1)
        return
    kd = read_field(os.path.join(case, tw, "kDeficit"))
    bd = read_field(os.path.join(case, tw, "bijDelta"))
    out["frozen"]["time"] = tw
    out["frozen"]["kDeficit_rms"] = float(np.sqrt((kd ** 2).mean()))
    out["frozen"]["bijDelta_rms"] = float(np.sqrt((bd ** 2).sum(axis=1).mean()))
    # propagate BOTH
    prop, t0p, _ = build(tag, "TRUTHR", None, RL.ITER_CAP, 5000)
    RL.patch_fvsolution(prop)
    tdp = os.path.join(prop, str(t0p))
    shutil.copy(os.path.join(case, tw, "kDeficit"), os.path.join(tdp, "kDeficit"))
    shutil.copy(os.path.join(case, tw, "bijDelta"), os.path.join(tdp, "bijDelta"))
    rr = RL.run_solver(prop)
    p = RL.parse_log(prop)
    s = RL.score(tag, prop, int(t0p) + RL.ITER_CAP)
    out["propagate"] = dict(case=prop, **rr, **p, **s)
    print(f"[TRUTHR] {tag} it={p['iterations']} U_rms={s.get('U_rms')} "
          f"divU={s.get('divU_rms_over_gradscale')}", flush=True)
    json.dump(out, open(os.path.join(ROOT, f"frozen_R_{tag}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
