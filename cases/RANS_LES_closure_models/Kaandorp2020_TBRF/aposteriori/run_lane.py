#!/usr/bin/env python3
"""Run the preregistered a-posteriori lane. Everything here is fixed by
PREREGISTRATION.md, written before any scored solve.

Bounded by construction: 30,000-iteration cap in controlDict, 3600 s timeout
per solve, background log. No process needs killing.
"""
from __future__ import annotations
import os, re, sys, json, time, pickle, subprocess, shutil, traceback
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
COMMON = "/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/_common"
sys.path.insert(0, HERE); sys.path.insert(0, PARENT); sys.path.insert(0, COMMON)
from setup_case import build, CASES, ROOT, K_FLOOR_FRAC
from of_read import (read_field, read_field_expand, latest_time_dir, sym_to_full, anisotropy,
                     realisability_violation, structured_gradient,
                     structured_shape, plane_axes)
import sst_baseline_metrics as SB
import tbrf_faithful
from tbrf_faithful import b_from_g, IDX6

DD = "/home/ubuntu/closure-data/kaandorp_tbrf"
OUT = "/home/ubuntu/closure-data/aposteriori/kaandorp"
FOAM = "source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1"
ITER_CAP = 30000
WALL_S = 3600
TOL = 1e-7

MEANB = np.array([[0.1358, -0.0536, 0.0], [-0.0536, -0.1410, 0.0], [0.0, 0.0, 0.0052]])
MEANB64 = np.array([[0.1756, -0.0382, 0.0018], [-0.0382, -0.1479, -0.0006],
                    [0.0018, -0.0006, -0.0276]])
GATE = {"AR_1_Ret_360": dict(U_rms=0.1985, inplane_LES=1.508),
        "AR_3_Ret_360": dict(U_rms=0.1846, inplane_LES=1.411),
        "CBFS13700": dict(U_rms=0.0516, U_mae=0.0258, x_reatt_LES=4.241,
                          x_reatt_SST=5.891)}


class RowBlocked(RuntimeError):
    """A registered row cannot be built from what is on disk.

    Raised, not swallowed: main() records the row as BLOCKED in results.json and
    carries on with the rest of the plan, so one unbuildable row cannot take the
    other registered rows down with it when the driver is running detached.
    """


class _Compat(pickle.Unpickler):
    def find_class(self, module, name):
        return super().find_class("tbrf_faithful" if module == "tbrf" else module, name)


def latest_written(case, t_start):
    """Highest written time directory strictly after the start time."""
    c = []
    for x in os.listdir(case):
        d = os.path.join(case, x)
        if not os.path.isdir(d) or not os.path.exists(os.path.join(d, "U")):
            continue
        try:
            v = float(x)
        except ValueError:
            continue
        if v > float(t_start):
            c.append((v, x))
    if not c:
        raise RuntimeError(f"{case}: no written time after {t_start}")
    return max(c)[1]


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ targets
_FEAT = None


def feats():
    global _FEAT
    if _FEAT is None:
        _FEAT = np.load(os.path.join(DD, "features_nodurbin.npz"), allow_pickle=False)
    return _FEAT


def ml_b(tag, seed):
    d = feats()
    names = [str(s) for s in d["names"]]
    if tag not in names:
        raise RowBlocked(
            f"{tag} has no block in {os.path.join(DD, 'features_nodurbin.npz')}, "
            f"which holds {len(names)} cases; the ML rows for {tag} cannot be "
            f"built until that feature file is rebuilt to include it")
    m = np.nonzero(d["case_id"] == names.index(tag))[0]
    ck = _Compat(open(os.path.join(DD, "ckpt_nodurbin",
                                   f"FS15_full_seed{seed}.pkl"), "rb")).load()
    X = d["X"][m][:, ck["cols"]]
    T = d["T"][m]
    good = np.isfinite(X).all(axis=1) & np.isfinite(T).all(axis=(1, 2, 3))
    Xs = np.where(good[:, None], X, 0.0)
    acc = np.empty((len(ck["trees"]), m.size, 6), np.float32)
    for i, t in enumerate(ck["trees"]):
        b = b_from_g(t.predict_g(Xs), T, ck["scale"])
        for s, (a, c) in enumerate(IDX6):
            acc[i, :, s] = b[:, a, c]
    med = np.median(acc, axis=0)
    out = np.zeros((m.size, 3, 3))
    for s, (a, c) in enumerate(IDX6):
        out[:, a, c] = med[:, s]; out[:, c, a] = med[:, s]
    out[~good] = 0.0
    return np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0), int((~good).sum())


def truth_b(tag):
    src, fam = CASES[tag]
    d = SB.load_case(tag, src, fam)
    b, ok = anisotropy(sym_to_full(d["tau_LES"]), d["k_LES"])
    return np.where(ok[:, None, None], np.nan_to_num(b), 0.0), int((~ok).sum())


def target(tag, label):
    if label == "NULL":
        return None, 0
    if label == "TRUTH":
        return truth_b(tag)
    if label == "MEANB":
        n = SB.load_case(tag, *CASES[tag])["n"]
        return np.broadcast_to(MEANB, (n, 3, 3)).copy(), 0
    if label == "MEANB64":
        n = SB.load_case(tag, *CASES[tag])["n"]
        return np.broadcast_to(MEANB64, (n, 3, 3)).copy(), 0
    if label.startswith("ML"):
        return ml_b(tag, int(label[2:]))
    raise ValueError(label)


# -------------------------------------------------------------------- solve
def patch_fvsolution(case):
    p = os.path.join(case, "system", "fvSolution")
    s = open(p).read()
    s = re.sub(r"residualControl\s*\{[^}]*\}",
               "residualControl\n    {\n        p               1e-6;\n"
               "        U               1e-6;\n    }", s, flags=re.S)
    open(p, "w").write(s)


def run_solver(case, model=None):
    if model:
        p = os.path.join(case, "constant", "turbulenceProperties")
        txt = open(p).read()
        assert "RASModel" in txt, p
        txt = re.sub(r"RASModel\s+\w+\s*;", f"RASModel        {model};", txt)
        open(p, "w").write(txt)
    t0 = time.time()
    r = subprocess.run(f"{FOAM}; cd {case} && timeout {WALL_S} simpleFoam -case . "
                       f"> log.run 2>&1", shell=True, executable="/bin/bash")
    return dict(rc=r.returncode, wall_s=round(time.time() - t0, 1))


RES = re.compile(r"Solving for (\w+), Initial residual = ([0-9.eE+-]+)")


def parse_log(case):
    hist = {}
    it = 0
    diverged = False
    for line in open(os.path.join(case, "log.run"), errors="replace"):
        if line.startswith("Time ="):
            it += 1
        m = RES.search(line)
        if m:
            hist.setdefault(m.group(1), []).append(float(m.group(2)))
        if "Floating point exception" in line or "FOAM FATAL" in line:
            diverged = True
    out = dict(iterations=it, diverged=diverged, ended="End" in
               open(os.path.join(case, "log.run"), errors="replace").read()[-4000:])
    for f in ("Ux", "p", "k", "omega"):
        h = hist.get(f, [])
        out[f"res_{f}_final"] = h[-1] if h else None
        out[f"res_{f}_max_last500"] = float(np.max(h[-500:])) if h else None
    # registered criterion: p and Ux initial residuals < 1e-6 sustained 100 its
    hp, hu = hist.get("p", []), hist.get("Ux", [])
    n = min(len(hp), len(hu))
    conv_it = None
    if n >= 100:
        a = (np.array(hp[:n]) < 1e-6) & (np.array(hu[:n]) < 1e-6)
        run = 0
        for i, v in enumerate(a):
            run = run + 1 if v else 0
            if run >= 100:
                conv_it = i + 1
                break
    out["converged_iteration"] = conv_it
    out["converged"] = conv_it is not None
    return out


# ------------------------------------------------------------------- score
def score(tag, case, t_end):
    src, fam = CASES[tag]
    d = SB.load_case(tag, src, fam)
    C, n = d["C"], d["n"]
    try:
        td = os.path.join(case, latest_written(case, t_end - ITER_CAP))
    except RuntimeError:
        return {"scored": False}
    U = read_field(os.path.join(td, "U"))
    k = read_field(os.path.join(td, "k"))
    nut = read_field(os.path.join(td, "nut"))
    UL, kL = d["U_LES"], d["k_LES"]
    uref = float(np.mean(np.linalg.norm(UL, axis=1)))
    e = np.linalg.norm(U - UL, axis=1)
    A = structured_gradient(C, U)
    S = 0.5 * (A + A.transpose(0, 2, 1))
    divU = np.einsum("nii->n", A)
    gscale = float(np.sqrt((A ** 2).sum(axis=(1, 2)).mean()))
    keep, thin = plane_axes(C)
    L = float(C[:, keep[0]].max() - C[:, keep[0]].min())
    kref = float(np.mean(np.abs(kL)))
    ok = k > K_FLOOR_FRAC * kref
    tau = ((2.0 / 3.0) * k)[:, None, None] * np.eye(3)[None] - 2.0 * nut[:, None, None] * S
    bd = read_field_expand(os.path.join(td, "bijDelta"), n)
    tau = tau + 2.0 * k[:, None, None] * sym_to_full(bd)
    b_tot, _ = anisotropy(tau, k, k_ref=kref)
    bL, okL = anisotropy(sym_to_full(d["tau_LES"]), kL)
    both = ok & okL & np.isfinite(b_tot).all(axis=(1, 2))
    viol, _ = realisability_violation(np.nan_to_num(b_tot[both]), tol=TOL)
    out = dict(scored=True, time=os.path.basename(td), n_cells=int(n),
               U_rms=float(np.sqrt((e ** 2).mean()) / uref),
               U_mae=float(e.mean() / uref),
               k_rms=float(np.sqrt(((k - kL) ** 2).mean()) / kref),
               b_rms_total=float(np.sqrt(((b_tot[both] - bL[both]) ** 2)
                                         .sum(axis=(1, 2)).mean())),
               unrealisable_frac=float(viol.mean()),
               divU_rms_over_gradscale=float(np.sqrt((divU ** 2).mean()) / gscale),
               divU_rms_over_UbulkL=float(np.sqrt((divU ** 2).mean()) / (uref / L)),
               Umax=float(np.abs(U).max()))
    if fam == "duct":
        sw = keep[0] if False else None
        # streamwise is the thin/homogeneous axis for these cross-plane meshes
        ip = np.delete(U, thin, axis=1)
        ub = float(np.abs(U[:, thin]).mean())
        ipL = np.delete(UL, thin, axis=1)
        out["inplane_pct_bulk"] = float(np.mean(np.linalg.norm(ip, axis=1)) / ub * 100)
        out["inplane_pct_bulk_LES"] = float(np.mean(np.linalg.norm(ipL, axis=1))
                                            / float(np.abs(UL[:, thin]).mean()) * 100)
    else:
        ns, nf = structured_shape(C)
        x = C[:nf, keep[0]]
        r = SB._longest_reversed_run(x, U[:nf, keep[0]])
        out["x_sep"] = r["x_sep"]; out["x_reatt"] = r["x_reatt"]
    return out


# --------------------------------------------------------------------- main
def g0(tag):
    """G0a: kOmegaSST vs kOmegaSSTCorrected(0,0), same 200 iterations."""
    res = {}
    for label, model in (("G0_stock", "kOmegaSST"), ("G0_corr", "kOmegaSSTCorrected")):
        case, t0, _ = build(tag, label, None, 200, 200)
        patch_fvsolution(case)
        p = os.path.join(case, "system", "fvSolution")
        txt = open(p).read()
        txt = re.sub(r"residualControl\s*\{[^}]*\}",
                     "residualControl\n    {\n    }", txt, flags=re.S)
        open(p, "w").write(txt)
        r = run_solver(case, model)
        res[label] = dict(case=case, t_end=int(t0) + 200, **r)
    ta = latest_written(res["G0_stock"]["case"], res["G0_stock"]["t_end"] - 200)
    tb = latest_written(res["G0_corr"]["case"], res["G0_corr"]["t_end"] - 200)
    assert ta == tb, (ta, tb)
    a = read_field(os.path.join(res["G0_stock"]["case"], ta, "U"))
    b = read_field(os.path.join(res["G0_corr"]["case"], tb, "U"))
    rel = float(np.linalg.norm(a - b) / np.linalg.norm(a))
    return dict(rel_L2_U=rel, passed=rel < 1e-10, compared_at_time=ta,
                **{k: v["wall_s"] for k, v in res.items()})


def main():
    t_lane = time.time()
    results = {"g0": {}, "runs": {}, "gates": GATE}
    todo = sys.argv[1:] if len(sys.argv) > 1 else None

    g = g0("AR_1_Ret_360")
    results["g0"]["AR_1_Ret_360"] = g
    log(f"[G0a] rel_L2(U) stock vs corrected(0,0) after 200 it = {g['rel_L2_U']:.3e} "
        f"-> {'PASS' if g['passed'] else 'FAIL'}")
    json.dump(results, open(os.path.join(OUT, "results.json"), "w"), indent=1)
    if not g["passed"]:
        log("[G0a] FAILED - lane BLOCKED, no scored solve run")
        return

    plan = []
    for tag in ("AR_1_Ret_360", "AR_3_Ret_360", "CBFS13700"):
        labs = ["NULL", "TRUTH", "MEANB", "ML0", "ML1", "ML2"]
        if tag == "AR_1_Ret_360":
            labs.append("MEANB64")
        for lab in labs:
            plan.append((tag, lab))
    for tag, lab in plan:
        key = f"{tag}__{lab}"
        if todo and key not in todo:
            continue
        t0w = time.time()
        cdir = os.path.join(ROOT, f"{tag}__{lab}")
        lg = os.path.join(cdir, "log.run")
        done = (os.path.exists(lg)
                and "End" in open(lg, errors="replace").read()[-2000:])
        try:
            if done:
                t0 = latest_time_dir(CASES[tag][0])
                case, nbad, nmask = cdir, -1, -1
                r = dict(rc=0, wall_s=-1.0, resumed=True)
            else:
                b, nbad = target(tag, lab)
                case, t0, nmask = build(tag, lab, b, ITER_CAP, 5000)
                patch_fvsolution(case)
                r = run_solver(case)
            p = parse_log(case)
            s = score(tag, case, int(t0) + ITER_CAP)
        except Exception as exc:
            # One unbuildable or unscorable row must not abort the plan: record
            # it as BLOCKED, with the full traceback kept, and go on. No metric
            # is written for it, so it can never be read as a result.
            results["runs"][key] = dict(
                case=cdir, label=lab, tag=tag, status="BLOCKED", rc=None,
                scored=False, wall_s=round(time.time() - t0w, 1),
                reason=f"{type(exc).__name__}: {exc}",
                traceback=traceback.format_exc())
            log(f"[run] {key:26s} BLOCKED - {type(exc).__name__}: {exc}")
            json.dump(results, open(os.path.join(OUT, "results.json"), "w"),
                      indent=1)
            continue
        results["runs"][key] = dict(case=case, label=lab, tag=tag,
                                    n_target_nonfinite=nbad, n_kmask=nmask,
                                    **r, **p, **s)
        log(f"[run] {key:26s} rc={r['rc']} it={p['iterations']:6d} "
            f"conv={p['converged_iteration']} wall={r['wall_s']:7.1f}s "
            f"U_rms={s.get('U_rms')} divU={s.get('divU_rms_over_gradscale')}")
        json.dump(results, open(os.path.join(OUT, "results.json"), "w"), indent=1)
    results["lane_wall_hours"] = (time.time() - t_lane) / 3600.0
    json.dump(results, open(os.path.join(OUT, "results.json"), "w"), indent=1)
    log(f"[done] lane wall-hours {results['lane_wall_hours']:.2f}")


if __name__ == "__main__":
    main()
