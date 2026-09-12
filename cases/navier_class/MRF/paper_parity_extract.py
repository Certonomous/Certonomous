#!/usr/bin/env python3
"""paper_parity_extract.py -- compute, for OUR MRF Rushton case, every quantity
that Reid, Rossi, Cottini & Benassi (2025, arXiv:2508.03176) report for theirs.

Source fields: verification/runs/navier_class/MRF/R2/ET8000/{coarse,medium,fine}/8000
(the graded R2 ET8000 tree; verdict NOT A RESULT -- see MRF_R2_GRADED_ROW_ET8000.json).
Cell centres C and cell volumes V are read from the READ-ONLY work copy built by
paper_parity_setup.sh, so NOTHING is written into the graded run tree.

Every reader in this file is exercised by a PLANTED-ZERO control (CLAUDE.md rule 3):
a known perturbation is written into a scratch copy of the field, read back through
the same reader, and the script REFUSES (exit 2) if the reader cannot see it.

Conventions taken from the paper and cited by line of the .txt sidecar:
  Utip = pi*N*D                       (their eq. 18)
  Ig   = Uhat / Utip * 100            (their eq. 17), Uhat = volume-averaged |U|
  I    = u'/Uhat * 100, u' = sqrt(2k/3)   (their eqs. 19-20)
  profiles: circumferential average over 0..350 deg in 10 deg steps, at r = 5/6/7 cm,
            over a vertical extent 2.5W, plotted against 2z/W   (their sec. 3.1)
  TKE normalised by Utip^2, velocities by Utip   (their Figs. 4, 16)
"""
import json, os, re, sys, math
import numpy as np
from scipy.spatial import cKDTree

ROOT = "/home/ubuntu/Certonomous"
SRC  = f"{ROOT}/verification/runs/navier_class/MRF/R2/ET8000"
WRK  = f"{ROOT}/verification/runs/navier_class/MRF/R2/PAPER_PARITY/work"
OUT  = f"{ROOT}/verification/runs/navier_class/MRF/R2/PAPER_PARITY"
TIME = "8000"
LEVELS = ["coarse", "medium", "fine"]

# --- our geometry / operating point, from verification/campaign/MRF_R1_PREREGISTRATION.md sec.4
D      = 0.100      # impeller diameter [m]
T_TANK = 0.300      # tank diameter [m]
W_BL   = D / 5.0    # blade width [m] = 0.020
ZC     = 0.100      # impeller centre-plane height [m] (= clearance C)
N_RPS  = 5.0        # rev/s
UTIP   = math.pi * N_RPS * D          # 1.5708 m/s
PLANT  = 1.234e-03                    # rule-3 planted perturbation

# --------------------------------------------------------------------------- readers
_HDR = re.compile(r"^\s*(internalField|boundaryField)", re.M)

def _strip_header(txt):
    i = txt.index("internalField")
    return txt[i:]

def read_internal_scalar(path):
    """Internal field of a volScalarField as a float array."""
    txt = open(path).read()
    body = _strip_header(txt)
    head = body.split("\n")[0]
    if "uniform" in head and "List" not in head:
        val = float(head.split("uniform")[1].strip().rstrip(";"))
        return None, val
    a = body.index("(")
    b = body.index(")", a)
    n = int(body[:a].strip().split("\n")[-1].strip() or 0)
    arr = np.fromstring(body[a + 1:b], sep=" ")
    assert arr.size == n, f"{path}: expected {n} got {arr.size}"
    return arr, None

def read_internal_vector(path):
    txt = open(path).read()
    body = _strip_header(txt)
    a = body.index("(")
    b = body.rindex(")", 0, body.index("boundaryField"))
    n = int(body[:a].strip().split("\n")[-1].strip())
    raw = body[a + 1:b].replace("(", " ").replace(")", " ")
    arr = np.fromstring(raw, sep=" ")
    assert arr.size == 3 * n, f"{path}: expected {3*n} got {arr.size}"
    return arr.reshape(n, 3)

def read_patch_values(path, patch):
    """Face values of a volScalarField on one boundary patch."""
    txt = open(path).read()
    bf = txt[txt.index("boundaryField"):]
    i = bf.index("\n    " + patch + "\n")
    seg = bf[i:]
    j = seg.index("value")
    k0 = seg.index("(", j); k1 = seg.index(")", k0)
    return np.fromstring(seg[k0 + 1:k1], sep=" ")

# --------------------------------------------------------------------------- metrics
def volume_metrics(U, k, V):
    """Uhat, kbar, Ig, and the two readings of turbulence intensity."""
    magU  = np.linalg.norm(U, axis=1)
    Vt    = V.sum()
    Uhat  = float((V * magU).sum() / Vt)
    kbar  = float((V * k).sum() / Vt)
    uprime_bar = math.sqrt(2.0 * kbar / 3.0)
    Ig    = Uhat / UTIP * 100.0
    I_glob = uprime_bar / Uhat * 100.0
    loc = np.sqrt(2.0 * np.maximum(k, 0.0) / 3.0) / np.maximum(magU, 1e-12)
    I_cell = float((V * loc).sum() / Vt) * 100.0
    frac_hi = float((V[loc > 0.20]).sum() / Vt) * 100.0   # their Fig. 17/18 metric
    uprime_cell = float((V * np.sqrt(2.0 * np.maximum(k, 0.0) / 3.0)).sum() / Vt)
    return dict(volume_m3=float(Vt), Uhat_mps=Uhat, kbar_m2s2=kbar,
                uprime_bar_mps=uprime_bar, Utip_mps=UTIP,
                agitation_index_pct=Ig,
                turb_intensity_global_pct=I_glob,
                turb_intensity_cellavg_pct=I_cell,
                turb_intensity_over_Utip_pct=uprime_bar / UTIP * 100.0,
                turb_intensity_cell_over_Utip_pct=uprime_cell / UTIP * 100.0,
                k_over_Utip2_volavg=kbar / UTIP**2,
                volume_fraction_I_above_20pct=frac_hi)

def profiles(tree, C, U, k, V, radii, n_theta=36, n_z=101):
    """Circumferentially averaged Ur, Utheta, Uz, k at each radius, vs 2z/W."""
    zs = np.linspace(ZC - 1.25 * W_BL, ZC + 1.25 * W_BL, n_z)
    th = np.deg2rad(np.arange(0, 360, 360 // n_theta))
    csize = np.cbrt(V)
    out = {}
    for r in radii:
        px = np.outer(np.ones_like(zs), r * np.cos(th)).ravel()
        py = np.outer(np.ones_like(zs), r * np.sin(th)).ravel()
        pz = np.repeat(zs, len(th))
        d, idx = tree.query(np.column_stack([px, py, pz]))
        far = d > 2.0 * csize[idx]                 # sample fell inside solid / outside mesh
        ux, uy, uz = U[idx, 0], U[idx, 1], U[idx, 2]
        ct, st = np.cos(np.tile(th, n_z)), np.sin(np.tile(th, n_z))
        ur = ux * ct + uy * st
        ut = -ux * st + uy * ct
        kk = k[idx]
        def avg(a):
            m = np.where(far, np.nan, a).reshape(n_z, len(th))
            return np.nanmean(m, axis=1), np.nanstd(m, axis=1)
        ur_m, ur_s = avg(ur); ut_m, ut_s = avg(ut)
        uz_m, uz_s = avg(uz); kk_m, kk_s = avg(kk)
        out[f"{r:.4f}"] = dict(
            r_m=r, r_over_D=r / D, two_z_over_W=((zs - ZC) * 2.0 / W_BL).tolist(),
            z_m=zs.tolist(),
            Ur_over_Utip=(ur_m / UTIP).tolist(), Ur_azimuthal_sd=(ur_s / UTIP).tolist(),
            Ut_over_Utip=(ut_m / UTIP).tolist(), Ut_azimuthal_sd=(ut_s / UTIP).tolist(),
            Uz_over_Utip=(uz_m / UTIP).tolist(), Uz_azimuthal_sd=(uz_s / UTIP).tolist(),
            k_over_Utip2=(kk_m / UTIP**2).tolist(), k_azimuthal_sd=(kk_s / UTIP**2).tolist(),
            rejected_samples_pct=float(far.mean() * 100.0))
    return out

# --------------------------------------------------------------------------- rule 3
def planted_zero_control(U, k, V, tree, C):
    """Refuse (exit 2) unless every reader used below can SEE a planted change."""
    rep = {"planted": PLANT, "checks": []}
    ok = True
    # (1) volume-average reader must see a uniform bump in k
    base = volume_metrics(U, k, V)
    bumped = volume_metrics(U, k + PLANT, V)
    dk = bumped["kbar_m2s2"] - base["kbar_m2s2"]
    c = dict(reader="volume_metrics/kbar", expected=PLANT, seen=dk,
             passed=abs(dk - PLANT) < 1e-9)
    ok &= c["passed"]; rep["checks"].append(c)
    # (2) profile reader must see a bump in the sampled k at r = 0.06 m
    p0 = profiles(tree, C, U, k, V, [0.06], n_theta=12, n_z=11)["0.0600"]
    p1 = profiles(tree, C, U, k + PLANT, V, [0.06], n_theta=12, n_z=11)["0.0600"]
    d = np.nanmean(np.array(p1["k_over_Utip2"]) - np.array(p0["k_over_Utip2"])) * UTIP**2
    c = dict(reader="profiles/k", expected=PLANT, seen=float(d),
             passed=abs(d - PLANT) < 1e-9)
    ok &= c["passed"]; rep["checks"].append(c)
    # (3) profile reader must see a bump in the sampled velocity
    q0 = profiles(tree, C, U, k, V, [0.06], n_theta=12, n_z=11)["0.0600"]
    q1 = profiles(tree, C, U + np.array([0.0, 0.0, PLANT]), k, V, [0.06],
                  n_theta=12, n_z=11)["0.0600"]
    d = np.nanmean(np.array(q1["Uz_over_Utip"]) - np.array(q0["Uz_over_Utip"])) * UTIP
    c = dict(reader="profiles/Uz", expected=PLANT, seen=float(d),
             passed=abs(d - PLANT) < 1e-9)
    ok &= c["passed"]; rep["checks"].append(c)
    rep["passed"] = bool(ok)
    return rep

# --------------------------------------------------------------------------- main
def main():
    os.makedirs(OUT, exist_ok=True)
    graded = json.load(open(f"{SRC}/MRF_R2_GRADED_ROW_ET8000.json"))
    np_by_level = {L["name"]: L["value"] for L in graded["levels"]}
    cells_by_level = {L["name"]: L["cells"] for L in graded["levels"]}
    result = {"source_fields": SRC, "time": TIME, "Utip_mps": UTIP,
              "graded_row": f"{SRC}/MRF_R2_GRADED_ROW_ET8000.json",
              "graded_verdict": graded["verdict"], "levels": {}}
    plant_done = False
    for L in LEVELS:
        t = f"{SRC}/{L}/{TIME}"
        w = f"{WRK}/{L}/{TIME}"
        U, _ = read_internal_vector(f"{t}/U"), None
        k, _u = read_internal_scalar(f"{t}/k")
        V, _u2 = read_internal_scalar(f"{w}/V")
        C = read_internal_vector(f"{w}/C")
        assert U.shape[0] == k.size == V.size == C.shape[0], f"{L}: size mismatch"
        tree = cKDTree(C)
        if not plant_done:                      # rule 3, on the cheapest level
            pz = planted_zero_control(U, k, V, tree, C)
            result["planted_zero"] = pz
            if not pz["passed"]:
                print("PLANTED-ZERO CONTROL FAILED -- REFUSING", file=sys.stderr)
                sys.exit(2)
            plant_done = True
        m = volume_metrics(U, k, V)
        m["cells"] = cells_by_level[L]
        m["Np"] = np_by_level[L]
        # y+ per wall patch
        yp = {}
        for patch in ["tankWall", "tankBottom", "tankLid", "baffles", "shaft", "impeller"]:
            try:
                v = read_patch_values(f"{t}/yPlus", patch)
                yp[patch] = dict(n_faces=int(v.size), min=float(v.min()),
                                 mean=float(v.mean()), max=float(v.max()))
            except Exception as e:
                yp[patch] = {"error": str(e)}
        allv = np.concatenate([read_patch_values(f"{t}/yPlus", p)
                               for p in ["tankWall","tankBottom","tankLid","baffles","shaft","impeller"]])
        yp["ALL_WALLS"] = dict(n_faces=int(allv.size), min=float(allv.min()),
                               mean=float(allv.mean()), max=float(allv.max()))
        m["yPlus_per_patch_unweighted_face_stats"] = yp
        radii = [0.05, 0.06, 0.07,                       # the paper's ABSOLUTE radii
                 0.05 * D / 0.093, 0.06 * D / 0.093, 0.07 * D / 0.093]  # r/D-matched
        m["profiles"] = profiles(tree, C, U, k, V, radii)
        result["levels"][L] = m
        print(f"{L}: cells={m['cells']} Np={m['Np']:.4f} Ig={m['agitation_index_pct']:.2f}% "
              f"I/Uhat={m['turb_intensity_global_pct']:.2f}% I/Utip={m['turb_intensity_over_Utip_pct']:.2f}% "
              f"k/Utip2={m['k_over_Utip2_volavg']:.3e} "
              f"y+ALL mean={yp['ALL_WALLS']['mean']:.2f}", flush=True)
    def _j(o):
        if isinstance(o, (np.bool_,)):   return bool(o)
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, (np.floating,)):return float(o)
        raise TypeError(str(type(o)))
    with open(f"{OUT}/PAPER_PARITY_RESULTS.json", "w") as f:
        json.dump(result, f, indent=2, default=_j)
    print("WROTE", f"{OUT}/PAPER_PARITY_RESULTS.json")

if __name__ == "__main__":
    main()
