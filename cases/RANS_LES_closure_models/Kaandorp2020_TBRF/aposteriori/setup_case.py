#!/usr/bin/env python3
"""Build one a-posteriori injection case for the Kaandorp TBRF re-solve.

Copies a benchmark case (read-only clone) to
/home/ubuntu/closure-data/aposteriori/kaandorp/<tag>/, swaps the RAS model to
kOmegaSSTCorrected (sdk/openfoam/sparta, validated in
verification/campaign/W2_SPARTA_FROZEN_CBFS.md), and writes the two static
correction fields the model MUST_READs:

    kDeficit  = 0            (registered: the TBRF predicts b only)
    bijDelta  = b_target + (nu_t/k) S      [W2 record convention, sec. 2]

with nu_t, k and S taken from the case's own converged k-omega SST solution.
Nothing under sdk/ or the benchmark clone is written.
"""
from __future__ import annotations
import os, re, shutil, sys, json
import numpy as np

COMMON = "/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/_common"
sys.path.insert(0, COMMON)
from of_read import read_field, latest_time_dir, sym_to_full, structured_gradient
import sst_baseline_metrics as SB

ROOT = "/home/ubuntu/closure-data/aposteriori/kaandorp"
BENCH = SB.DATA
CASES = {
    "AR_1_Ret_360": (os.path.join(BENCH, "DUCT", "AR_1_Ret_360"), "duct"),
    "AR_3_Ret_360": (os.path.join(BENCH, "DUCT", "AR_3_Ret_360"), "duct"),
    "CBFS13700":    (os.path.join(BENCH, "CBFS"), "hill"),
    "PHLL10595":    (os.path.join(BENCH, "PH_Breuer"), "hill"),
    "alpha_10_9000_3036": (os.path.join(BENCH, "Parm_PH_29", "alpha_10",
                                        "alpha_10_9000_3036"), "hill"),
}
K_FLOOR_FRAC = 1e-4          # registered: bijDelta = 0 where k_RANS underflows


def patch_bcs(case, ncomp):
    txt = open(os.path.join(case, "constant", "polyMesh", "boundary")).read()
    body = txt[txt.index("// *"):]
    zero = "0" if ncomp == 1 else "(" + " ".join(["0"] * ncomp) + ")"
    out = []
    for n, blk in re.findall(r"(\w+)\s*\{([^}]*)\}", body, re.S):
        t = re.search(r"type\s+(\w+)\s*;", blk).group(1)
        if t in ("cyclic", "empty", "symmetry", "symmetryPlane", "wedge"):
            out.append(f"    {n} {{ type {t}; }}")
        else:
            out.append(f"    {n} {{ type calculated; value uniform {zero}; }}")
    return "boundaryField\n{\n" + "\n".join(out) + "\n}\n"


def write_field(path, obj, cls, dims, data, case, ncomp):
    if np.isscalar(data):
        v = str(data) if ncomp == 1 else "(" + " ".join([str(data)] * ncomp) + ")"
        internal = f"internalField   uniform {v};\n"
    else:
        a = np.asarray(data, float)
        if ncomp == 1:
            rows = "\n".join(f"{v:.10g}" for v in a)
        else:
            rows = "\n".join("(" + " ".join(f"{c:.10g}" for c in r) + ")" for r in a)
        internal = (f"internalField   nonuniform List<{'scalar' if ncomp==1 else 'symmTensor'}>\n"
                    f"{a.shape[0]}\n(\n{rows}\n)\n;\n")
    open(path, "w").write(
        f"FoamFile {{ version 2.0; format ascii; class {cls}; object {obj}; }}\n"
        f"dimensions      {dims};\n" + internal + patch_bcs(case, ncomp))


def bij_delta(tag, b_target):
    """b_target (N,3,3) -> bijDelta (N,6) in (xx,xy,xz,yy,yz,zz) order."""
    src, fam = CASES[tag]
    d = SB.load_case(tag, src, fam)
    t = d["time"]
    nut = read_field(os.path.join(src, t, "nut"))
    k = d["k"]
    A = np.asarray(d["gradU"]).reshape(-1, 3, 3).transpose(0, 2, 1)
    S = 0.5 * (A + A.transpose(0, 2, 1))
    kref = float(np.mean(np.abs(d["k_LES"])))
    ok = k > K_FLOOR_FRAC * kref
    lin = np.zeros_like(S)
    lin[ok] = (nut[ok] / k[ok])[:, None, None] * S[ok]
    bd = np.where(ok[:, None, None], b_target + lin, 0.0)
    bd = np.nan_to_num(bd, nan=0.0, posinf=0.0, neginf=0.0)
    idx = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
    return np.stack([bd[:, i, j] for i, j in idx], axis=1), int((~ok).sum()), d


def build(tag, label, b_target, end_iters, write_interval):
    src, fam = CASES[tag]
    case = os.path.join(ROOT, f"{tag}__{label}")
    if os.path.exists(case):
        shutil.rmtree(case)
    shutil.copytree(src, case)
    os.chmod(case, 0o755)
    for r, ds, fs in os.walk(case):
        for x in ds + fs:
            try:
                os.chmod(os.path.join(r, x), 0o755)
            except OSError:
                pass
    for junk in ("postProcessing", "convergencePlots", "dynamicCode", "VTK"):
        shutil.rmtree(os.path.join(case, junk), ignore_errors=True)
    t0 = latest_time_dir(src)
    cd = os.path.join(case, "system", "controlDict")
    s = open(cd).read()
    # LIBS: the DUCT/CBFS/PH_Breuer cases name a library absent on this machine;
    # the 29 Parm_PH_29 hills carry NO libs entry at all. Insert-or-replace, then
    # ASSERT -- a silent string-replace failure costs a whole run (measured twice).
    LIBS = 'libs ( "libspartaTurbulenceModels.so" );'
    if re.search(r"libs\s*\(", s):
        s = re.sub(r"libs\s*\([^)]*\)\s*;", lambda m: LIBS, s)
    else:
        mm = re.search(r"\n// \* \* \*[^\n]*\n", s)
        s = s[:mm.end()] + "\n" + LIBS + "\n" + s[mm.end():]
    assert "libspartaTurbulenceModels" in s, "libs entry not installed in " + cd
    s = re.sub(r"startTime\s+\S+;", "", s)
    s = re.sub(r"startFrom\s+\w+;", f"startFrom       startTime;\nstartTime       {t0};", s)
    s = re.sub(r"endTime\s+\S+;", f"endTime         {int(t0) + end_iters};", s)
    s = re.sub(r"writeInterval\s+\S+;", f"writeInterval   {write_interval};", s)
    s = re.sub(r"functions\s*\{.*?\n\}", "functions\n{\n}", s, flags=re.S)
    open(cd, "w").write(s)
    tp = os.path.join(case, "constant", "turbulenceProperties")
    tps = open(tp).read()
    assert "kOmegaSST" in tps, tp
    tps = re.sub(r"RASModel\s+kOmegaSST\s*;", "RASModel        kOmegaSSTCorrected;", tps)
    open(tp, "w").write(tps)
    td = os.path.join(case, t0)
    write_field(os.path.join(td, "kDeficit"), "kDeficit", "volScalarField",
                "[0 2 -3 0 0 0 0]", 0, case, 1)
    if b_target is None:
        write_field(os.path.join(td, "bijDelta"), "bijDelta", "volSymmTensorField",
                    "[0 0 0 0 0 0 0]", 0, case, 6)
        nmask = 0
    else:
        bd, nmask, _ = bij_delta(tag, b_target)
        write_field(os.path.join(td, "bijDelta"), "bijDelta", "volSymmTensorField",
                    "[0 0 0 0 0 0 0]", bd, case, 6)
    return case, t0, nmask


if __name__ == "__main__":
    print(json.dumps({k: v[0] for k, v in CASES.items()}, indent=1))
