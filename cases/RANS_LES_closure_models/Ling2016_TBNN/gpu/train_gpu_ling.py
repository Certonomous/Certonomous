#!/usr/bin/env python3
"""GPU driver for the Ling (2016) TBNN GPU arm — PREREGISTRATION_DRAFT.md.

Runs ON gpu1 (NVIDIA L4) under nohup, staged and restartable; every stage writes
a status JSON to --out and records its wall seconds into spend.json. Cumulative
wall-hours are checked against the registered 60 GPU-h cap (DRAFT sec. 6);
exceeding it writes a BLOCKED status and exits 3 — an overrun stops the run, it
does not get a new budget (CLAUDE.md rule 12).

Stages, in order (each skippable if its status JSON says DONE):
  g0            planted-zero controls G0a + G0b (DRAFT sec. 9). CPU/numpy only.
  p0            timing gate (--frozen only): 200 epochs of ARM-A TBNN seed 0,
                full batch SGD lr 2.5e-7, projected over the registered batch;
                projection > 60 GPU-h -> BLOCKED, exit 3.
  arma_tbnn     ARM-A TBNN, plain SGD lr 2.5e-7, full batch, 200,000-epoch cap,
                seeds 0..4 (DRAFT sec. 2, removes CPU-lane departure D3).
  arma_mlp      ARM-A control MLP 10x10, plain SGD lr 2.5e-6, same cap/seeds.
  armb_search   ARM-B: optuna TPE, 100 trials x 3 seeds x 400 epochs, Adam
                inside trials (the CPU lane's optimizer; the paper's SGD rates
                measurably do not move in 400 epochs). Selection on VAL only.
  armb_retrain  best architecture retrained, 5 seeds x 400 epochs.

Training NEVER starts unless --frozen is passed: the pre-registration must be
signed first. Without --frozen only g0 (and explicit --stage g0) will run.

Split, preprocessing (signed-log1p input scaling, basis RMS rescaling),
LeakyReLU(0.01) and the assert_disjoint() text are inherited verbatim from the
CPU lane ../train_tbnn.py (frozen ../PREREGISTRATION.md sec. 6); copied here
because gpu1 does not hold the repository.

Usage (on gpu1):
  ~/r_ling_gpu/venv/bin/python train_gpu_ling.py --frozen \
      --data ~/r_ling_gpu/data/dataset.npz --out ~/r_ling_gpu/out
Lab-box control run (no GPU, no training):
  python train_gpu_ling.py --stage g0 --data /home/ubuntu/closure-data/tbnn/dataset.npz --out <scratch>
"""
from __future__ import annotations
import argparse, csv, json, math, os, sys, time
import numpy as np

# torch imported lazily: the g0 stage is pure numpy and must run on the lab box.

# ---------------------------------------------------------------- constants
PLANT = 1.234e-03            # the lab's standing planted-zero constant
CAP_HOURS = 60.0             # registered GPU-hour cap (DRAFT sec. 6)
ARMA_EPOCHS = 200_000        # registered epoch cap (DRAFT sec. 6)
ARMA_LR_TBNN = 2.5e-7        # Ling p. 7, plain SGD
ARMA_LR_MLP = 2.5e-6         # Ling p. 6, plain SGD
HIST_EVERY = 200             # history row (train loss + val b_rms) every 200 ep
CKPT_EVERY = 2000            # restart checkpoint every 2000 epochs
P0_EPOCHS = 200              # timing-gate sample
ARMB_TRIALS = 100
ARMB_SEEDS = 3
ARMB_EPOCHS = 400
ARMB_RETRAIN_SEEDS = 5
SEEDS = [0, 1, 2, 3, 4]

# ---- pre-registered split, verbatim from ../train_tbnn.py (CPU lane) --------
TEST = {"alpha_15_13929_4048", "alpha_15_13929_2024",
        "alpha_05_4071_4048", "alpha_05_4071_2024",
        "AR_1_Ret_360", "AR_3_Ret_360", "AR_14_Ret_180", "NASA_2DWMH"}
VAL = {"alpha_05_10071_4048", "alpha_05_10071_2024",
       "alpha_15_7929_4048", "alpha_15_7929_2024", "AR_7_Ret_180"}
GROUP_EXCLUDED = {"alpha_15_13929_3036", "alpha_05_4071_3036",
                  "alpha_05_10071_3036", "alpha_15_7929_3036"}


def hill_group(name):
    """(alpha, length) group key for a parametric hill, else the case name."""
    p = name.split("_")
    if p[0] == "alpha" and len(p) >= 4:
        return ("alpha_" + p[1], p[2])
    return (name,)


def assert_disjoint(names, split_of):
    """Pre-registered disjointness assertion. Raises before any training.
    Copied verbatim from ../train_tbnn.py; output printed into the record."""
    tr = {n for n in names if split_of[n] == "train"}
    va = {n for n in names if split_of[n] == "val"}
    te = {n for n in names if split_of[n] == "test"}
    lines = []
    assert tr & va == set() and tr & te == set() and va & te == set(), "case overlap"
    lines.append(f"case sets pairwise disjoint: train={len(tr)} val={len(va)} test={len(te)}")
    gtr = {hill_group(n) for n in tr}
    gva = {hill_group(n) for n in va}
    gte = {hill_group(n) for n in te}
    leak = (gtr & gte) | (gtr & gva)
    assert not leak, f"(alpha,length) group leak between train and val/test: {sorted(leak)}"
    lines.append(f"(alpha,length) groups disjoint: train={len(gtr)} val={len(gva)} test={len(gte)}; no group appears on both sides")
    lines.append("cells are never split across cases: every case contributes all of its cells to exactly one of train/val/test")
    lines.append(f"train cases: {sorted(tr)}")
    lines.append(f"val cases:   {sorted(va)}")
    lines.append(f"test cases:  {sorted(te)}")
    return lines


# ------------------------------------------------------------ realisability
# Copied from _common/of_read.py (barycentric / realisability_violation),
# because gpu1 does not hold the repository. Banerjee et al. (2007) mapping.
def barycentric(b):
    lam = np.linalg.eigvalsh(b)              # ascending
    lam = lam[:, ::-1]                       # descending l1 >= l2 >= l3
    c1 = lam[:, 0] - lam[:, 1]
    c2 = 2.0 * (lam[:, 1] - lam[:, 2])
    c3 = 3.0 * lam[:, 2] + 1.0
    return np.stack([c1, c2, c3], axis=1), lam


def realisability_violation(b, tol=0.0):
    c, _ = barycentric(b)
    mn = c.min(axis=1)
    return mn < -tol, mn


# ---------------------------------------------------------------- data load
def load_data(path):
    z = np.load(path, allow_pickle=True)
    names = [str(x) for x in z["names"]]
    split_of = {}
    for n in names:
        split_of[n] = ("test" if n in TEST else
                       ("val" if n in VAL else
                        ("excluded" if n in GROUP_EXCLUDED else "train")))
    assert_lines = assert_disjoint([n for n in names if split_of[n] != "excluded"],
                                   split_of)
    for L in assert_lines:
        print("[assert] " + L, flush=True)
    cid, valid = z["case_id"], z["valid"]
    masks = {s: np.zeros(len(cid), bool) for s in ("train", "val", "test")}
    for i, n in enumerate(names):
        if split_of[n] in masks:
            masks[split_of[n]] |= (cid == i)
    for s in masks:
        masks[s] &= valid
    return dict(names=names, cid=cid, valid=valid, lam=z["lam"], T=z["T"],
                b_LES=z["b_LES"], masks=masks, assert_lines=assert_lines,
                split_of=split_of)


def preprocess(d):
    """CPU-lane departures D4 (signed-log1p input scaling) and D5 (basis RMS
    rescaling), statistics on TRAINING CELLS ONLY — verbatim convention from
    ../train_tbnn.py."""
    tr = d["masks"]["train"]
    lam_s = np.sign(d["lam"]) * np.log1p(np.abs(d["lam"]))
    mu = lam_s[tr].mean(0); sd = lam_s[tr].std(0) + 1e-12
    lam_n = ((lam_s - mu) / sd).astype(np.float32)
    tscale = np.sqrt((d["T"][tr] ** 2).sum(axis=(2, 3)).mean(axis=0)) + 1e-30
    T_n = (d["T"] / tscale[None, :, None, None]).astype(np.float32)
    return lam_n, T_n, dict(mu=mu.tolist(), sd=sd.tolist(), tscale=tscale.tolist())


def frob_rms64(x):
    """The b_rms scorer: RMS of the Frobenius norm, float64 accumulation."""
    x = np.asarray(x, dtype=np.float64)
    return float(np.sqrt((x ** 2).sum(axis=(1, 2)).mean()))


# --------------------------------------------------------------- status/spend
def status_path(out, stage):
    return os.path.join(out, f"status_{stage}.json")


def read_status(out, stage):
    p = status_path(out, stage)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return None


def write_status(out, stage, state, **extra):
    p = status_path(out, stage)
    rec = dict(stage=stage, state=state, utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **extra)
    with open(p + ".tmp", "w") as f:
        json.dump(rec, f, indent=1)
    os.replace(p + ".tmp", p)
    print(f"[status] {stage}: {state}", flush=True)
    return rec


def spend_add(out, stage, seconds):
    p = os.path.join(out, "spend.json")
    sp = {"stages": {}, "total_hours": 0.0}
    if os.path.exists(p):
        with open(p) as f:
            sp = json.load(f)
    sp["stages"][stage] = sp["stages"].get(stage, 0.0) + seconds
    sp["total_hours"] = round(sum(sp["stages"].values()) / 3600.0, 4)
    with open(p + ".tmp", "w") as f:
        json.dump(sp, f, indent=1)
    os.replace(p + ".tmp", p)
    return sp["total_hours"]


def spend_hours(out):
    p = os.path.join(out, "spend.json")
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)["total_hours"]
    return 0.0


def cap_guard(out, stage):
    h = spend_hours(out)
    if h >= CAP_HOURS:
        write_status(out, stage, "BLOCKED",
                     reason=f"cumulative {h:.2f} wall-h >= registered cap {CAP_HOURS} GPU-h; "
                            "overrun stops the run (CLAUDE.md rule 12)")
        sys.exit(3)
    return h


# ---------------------------------------------------------------- G0 controls
def stage_g0(out, data_path):
    """G0a planted-zero on the b_rms scorer; G0b plant on the realisability
    reader. Pure numpy on a COPY; the file on disk is never modified.
    Refusal -> exit 2 (NOT A RESULT for the whole arm)."""
    t0 = time.time()
    d = load_data(data_path)
    names, cid, valid, bL = d["names"], d["cid"], d["valid"], d["b_LES"]

    # named, recorded cell k: the first valid cell of the first sorted TEST case
    case = sorted(TEST)[0]
    ci = names.index(case)
    k = int(np.flatnonzero((cid == ci) & valid)[0])
    case_mask = (cid == ci) & valid

    # G0a — plant into a float64 COPY, read back through the b_rms scorer
    b_clean = bL[case_mask].astype(np.float64)
    b_plant = b_clean.copy()
    krow = int(np.flatnonzero(np.flatnonzero((cid == ci) & valid) == k)[0])
    b01 = float(b_plant[krow, 0, 1])
    b_plant[krow, 0, 1] += PLANT
    b_plant[krow, 1, 0] += PLANT
    pred = np.zeros_like(b_clean)            # the b=0 predictor as reference
    # (1) the per-case b_rms scorer must see a NON-ZERO difference
    rms_c = frob_rms64(pred - b_clean)
    rms_p = frob_rms64(pred - b_plant)
    diff = rms_p - rms_c
    # (2) back-solve through the known SINGLE-CELL contribution to the RMS
    # (DRAFT sec. 9), with the same scorer on exactly the planted cell: a
    # whole-case float64 back-solve carries ~1e-8 sqrt round-trip error and
    # cannot certify 1e-9 relative; the single-cell contribution can.
    rms_kc = frob_rms64((pred - b_clean)[krow:krow + 1])
    rms_kp = frob_rms64((pred - b_plant)[krow:krow + 1])
    dss = rms_kp ** 2 - rms_kc ** 2          # = 2((b01+P)^2 - b01^2), n = 1
    recovered = -b01 + math.sqrt(max(b01 * b01 + dss / 2.0, 0.0))
    rel = abs(recovered - PLANT) / PLANT
    g0a_ok = (diff != 0.0) and (rel < 1e-9)
    print(f"[G0a] case={case} k={k} b01={b01:.6e} rms_clean={rms_c:.12f} "
          f"rms_planted={rms_p:.12f} diff={diff:.3e} recovered={recovered:.9e} "
          f"rel_err={rel:.3e} -> {'OK' if g0a_ok else 'REFUSE'}", flush=True)
    if not g0a_ok:
        write_status(out, "g0", "REFUSED", plant=PLANT, cell=k, case=case,
                     diff=diff, recovered=recovered, rel_err=rel,
                     reason="b_rms scorer did not read back the plant; "
                            "a zero from a reader not shown able to see a non-zero is not evidence")
        print("[G0a] REFUSAL: scorer cannot see the plant. Exiting 2.", flush=True)
        sys.exit(2)

    # G0b — realisability reader must flag b = diag(1, 1, -2)
    b_test = b_clean[:64].copy()
    forced = np.diag([1.0, 1.0, -2.0])
    b_test[0] = forced
    viol, mn = realisability_violation(b_test)
    norm = float(np.sqrt((forced ** 2).sum()))
    g0b_ok = bool(viol[0])
    print(f"[G0b] forced cell b=diag(1,1,-2) ||b||_F={norm:.4f} "
          f"min_bary_coord={mn[0]:.4f} flagged={g0b_ok} "
          f"-> {'OK' if g0b_ok else 'REFUSE'}", flush=True)
    if not g0b_ok:
        write_status(out, "g0", "REFUSED", reason="realisability reader did not "
                     "flag b=diag(1,1,-2); G3 would be NOT A RESULT")
        print("[G0b] REFUSAL: realisability reader blind. Exiting 2.", flush=True)
        sys.exit(2)

    sec = time.time() - t0
    spend_add(out, "g0", sec)
    write_status(out, "g0", "DONE", plant=PLANT, cell=k, case=case,
                 b01_before=b01, rms_clean=rms_c, rms_planted=rms_p,
                 recovered_plant=recovered, rel_err=rel,
                 g0b_forced_norm=norm, g0b_flagged=g0b_ok, seconds=round(sec, 2),
                 assert_lines=d["assert_lines"])


# ---------------------------------------------------------------- models
def build_torch():
    import torch
    import torch.nn as nn
    return torch, nn


def make_tbnn(nn, depth=8, width=30, act="leakyrelu0.01", nin=5, nbasis=10):
    ACT = {"relu": lambda: nn.ReLU(), "leakyrelu0.01": lambda: nn.LeakyReLU(0.01),
           "tanh": lambda: nn.Tanh(), "sigmoid": lambda: nn.Sigmoid()}
    L, d = [], nin
    for _ in range(depth):
        L += [nn.Linear(d, width), ACT[act]()]
        d = width
    L += [nn.Linear(d, nbasis)]
    return nn.Sequential(*L)


class Nets:
    """TBNN forward: g = net(lam); b = einsum('ng,ngij->nij', g, T).
    MLP forward: 6 unique components -> symmetric traceless b (CPU-lane code)."""
    @staticmethod
    def tbnn_forward(torch, net, lam, T):
        g = net(lam)
        return torch.einsum("ng,ngij->nij", g, T)

    @staticmethod
    def make_mlp(nn, nin=5, nh=10, nlayers=10):
        L, d = [], nin
        for _ in range(nlayers):
            L += [nn.Linear(d, nh), nn.LeakyReLU(0.01)]
            d = nh
        L += [nn.Linear(d, 6)]
        return nn.Sequential(*L)

    @staticmethod
    def mlp_forward(torch, net, lam, T=None):
        y = net(lam)
        i = [0, 0, 0, 1, 1, 2]; j = [0, 1, 2, 1, 2, 2]
        b = torch.zeros(y.shape[0], 3, 3, dtype=y.dtype, device=y.device)
        for c in range(6):
            b[:, i[c], j[c]] = y[:, c]
            if i[c] != j[c]:
                b[:, j[c], i[c]] = y[:, c]
        tr = b[:, 0, 0] + b[:, 1, 1] + b[:, 2, 2]
        b = b - torch.eye(3, device=y.device)[None] * (tr / 3.0)[:, None, None]
        return b


def val_b_rms(torch, fwd, net, Xva, Tva, Yva):
    with torch.no_grad():
        vb = fwd(torch, net, Xva, Tva)
        return float(torch.sqrt(((vb - Yva) ** 2).sum(dim=(1, 2)).mean()))


def predict_all(torch, fwd, net, lam_n, T_n, dev, chunk=100_000):
    outs = []
    with torch.no_grad():
        for i in range(0, len(lam_n), chunk):
            X = torch.from_numpy(lam_n[i:i + chunk]).to(dev)
            T = torch.from_numpy(T_n[i:i + chunk]).to(dev)
            outs.append(fwd(torch, net, X, T).cpu().numpy())
    return np.concatenate(outs)


# ---------------------------------------------------------------- ARM-A
def train_sgd_fullbatch(torch, nn, tag, seed, lr, make_net, fwd, dev,
                        Xtr, Ttr, Ytr, Xva, Tva, Yva, out, epochs,
                        deadline_check):
    """Plain SGD, full batch (train rows only in the gradient), history every
    HIST_EVERY epochs, best-val checkpoint, restartable via .pt checkpoint.
    Returns (net_final_state, best_state, best_val, hist_path, stopped_early)."""
    torch.manual_seed(seed); np.random.seed(seed)
    net = make_net().to(dev)
    opt = torch.optim.SGD(net.parameters(), lr=lr)
    ck = os.path.join(out, f"ck_{tag}_s{seed}.pt")
    hist = os.path.join(out, f"hist_{tag}_s{seed}.csv")
    e0, best, best_state = 0, float("inf"), None
    if os.path.exists(ck):
        st = torch.load(ck, weights_only=False, map_location=dev)
        net.load_state_dict(st["model"]); opt.load_state_dict(st["opt"])
        e0, best, best_state = st["epoch"], st["best"], st["best_state"]
        print(f"[resume] {tag} s{seed} from epoch {e0}", flush=True)
    if not os.path.exists(hist):
        with open(hist, "w", newline="") as f:
            csv.writer(f).writerow(["epoch", "train_loss", "val_b_rms", "best_val"])
    ntr = Xtr.shape[0]
    for ep in range(e0, epochs):
        net.train()
        opt.zero_grad()
        loss = ((fwd(torch, net, Xtr, Ttr) - Ytr) ** 2).sum(dim=(1, 2)).mean()
        loss.backward(); opt.step()
        if (ep % HIST_EVERY == 0) or (ep == epochs - 1):
            net.eval()
            v = val_b_rms(torch, fwd, net, Xva, Tva, Yva)
            if v < best - 1e-12:
                best = v
                best_state = {k: t.detach().cpu().clone() for k, t in net.state_dict().items()}
            with open(hist, "a", newline="") as f:
                csv.writer(f).writerow([ep, float(loss.detach()), v, best])
        if (ep + 1) % CKPT_EVERY == 0:
            torch.save(dict(model=net.state_dict(), opt=opt.state_dict(),
                            epoch=ep + 1, best=best, best_state=best_state), ck)
            if deadline_check():         # cap would be exceeded -> stop cleanly
                return net, best_state, best, hist, True
    torch.save(dict(model=net.state_dict(), opt=opt.state_dict(),
                    epoch=epochs, best=best, best_state=best_state), ck)
    return net, best_state, best, hist, False


def save_test_preds(torch, fwd, net, best_state, lam_n, T_n, dev, d, out, tag, seed):
    """TEST-case predictions per seed, both best-val and final, plus the global
    row indices they correspond to (dataset order)."""
    te = d["masks"]["test"]
    idx = np.flatnonzero(te)
    pred_final = predict_all(torch, fwd, net, lam_n[te], T_n[te], dev)
    if best_state is not None:
        net.load_state_dict(best_state)
    pred_best = predict_all(torch, fwd, net, lam_n[te], T_n[te], dev)
    p = os.path.join(out, f"pred_{tag}_s{seed}.npz")
    np.savez_compressed(p, idx=idx.astype(np.int64),
                        pred_best=pred_best.astype(np.float32),
                        pred_final=pred_final.astype(np.float32))
    return p


def stage_arma(out, data_path, which, dev_name):
    stage = f"arma_{which}"
    cap_guard(out, stage)
    torch, nn = build_torch()
    dev = torch.device(dev_name)
    d = load_data(data_path)
    lam_n, T_n, scal = preprocess(d)
    tr, va = d["masks"]["train"], d["masks"]["val"]
    tt = lambda a: torch.from_numpy(np.ascontiguousarray(a)).to(dev)
    Xtr, Ttr, Ytr = tt(lam_n[tr]), tt(T_n[tr]), tt(d["b_LES"][tr])
    Xva, Tva, Yva = tt(lam_n[va]), tt(T_n[va]), tt(d["b_LES"][va])
    if which == "tbnn":
        make_net = lambda: make_tbnn(nn)                      # 8x30 LeakyReLU(0.01)
        fwd, lr = Nets.tbnn_forward, ARMA_LR_TBNN
    else:
        make_net = lambda: Nets.make_mlp(nn)                  # 10x10 LeakyReLU(0.01)
        fwd, lr = Nets.mlp_forward, ARMA_LR_MLP
    st = read_status(out, stage) or {}
    done_seeds = st.get("seeds_done", {})
    t0 = time.time()
    blocked = False

    def deadline_check():
        # counts this stage's elapsed time against the running total
        return spend_hours(out) + (time.time() - t0) / 3600.0 >= CAP_HOURS

    for seed in SEEDS:
        if str(seed) in done_seeds:
            print(f"[skip] {stage} seed {seed} already DONE", flush=True)
            continue
        net, best_state, best, hist, stopped = train_sgd_fullbatch(
            torch, nn, which, seed, lr, make_net, fwd, dev,
            Xtr, Ttr, Ytr, Xva, Tva, Yva, out, ARMA_EPOCHS, deadline_check)
        if stopped:
            blocked = True
            break
        p = save_test_preds(torch, fwd, net, best_state, lam_n, T_n, dev, d, out, which, seed)
        done_seeds[str(seed)] = dict(best_val=best, pred=os.path.basename(p),
                                     hist=os.path.basename(hist))
        write_status(out, stage, "RUNNING", seeds_done=done_seeds, lr=lr,
                     epochs=ARMA_EPOCHS, scaling=scal)
    sec = time.time() - t0
    total = spend_add(out, stage, sec)
    if blocked or total >= CAP_HOURS:
        write_status(out, stage, "BLOCKED", seeds_done=done_seeds,
                     reason=f"cumulative {total:.2f} wall-h vs cap {CAP_HOURS} GPU-h")
        sys.exit(3)
    write_status(out, stage, "DONE", seeds_done=done_seeds, lr=lr,
                 epochs=ARMA_EPOCHS, seconds=round(sec, 1), scaling=scal)


# ---------------------------------------------------------------- P0 timing
def stage_p0(out, data_path, dev_name):
    """Time P0_EPOCHS of ARM-A TBNN seed 0 full-batch SGD; project the full
    registered batch; projection over the cap -> BLOCKED, exit 3."""
    cap_guard(out, "p0")
    torch, nn = build_torch()
    dev = torch.device(dev_name)
    d = load_data(data_path)
    lam_n, T_n, _ = preprocess(d)
    tr, va = d["masks"]["train"], d["masks"]["val"]
    tt = lambda a: torch.from_numpy(np.ascontiguousarray(a)).to(dev)
    Xtr, Ttr, Ytr = tt(lam_n[tr]), tt(T_n[tr]), tt(d["b_LES"][tr])
    Xva, Tva, Yva = tt(lam_n[va]), tt(T_n[va]), tt(d["b_LES"][va])
    torch.manual_seed(0); np.random.seed(0)
    net = make_tbnn(nn).to(dev)
    opt = torch.optim.SGD(net.parameters(), lr=ARMA_LR_TBNN)
    # one warm-up epoch outside the clock (kernel compilation / allocator)
    loss = ((Nets.tbnn_forward(torch, net, Xtr, Ttr) - Ytr) ** 2).sum(dim=(1, 2)).mean()
    loss.backward(); opt.step(); opt.zero_grad()
    if dev.type == "cuda":
        torch.cuda.synchronize()
    t0 = time.time()
    for ep in range(P0_EPOCHS):
        opt.zero_grad()
        loss = ((Nets.tbnn_forward(torch, net, Xtr, Ttr) - Ytr) ** 2).sum(dim=(1, 2)).mean()
        loss.backward(); opt.step()
        if ep % HIST_EVERY == 0:
            val_b_rms(torch, Nets.tbnn_forward, net, Xva, Tva, Yva)
    if dev.type == "cuda":
        torch.cuda.synchronize()
    sec = time.time() - t0
    s_per_ep = sec / P0_EPOCHS
    # registered batch: ARM-A 10 runs x 200,000 epochs; ARM-B (100 trials x 3
    # seeds + 5 retrains) x 400 epochs. MLP and ARM-B epochs projected at the
    # TBNN-measured full-batch rate (stated assumption: MLP is smaller, ARM-B
    # batches are smaller-or-equal, so this over- rather than under-projects).
    arma_ep = (5 + 5) * ARMA_EPOCHS
    armb_ep = (ARMB_TRIALS * ARMB_SEEDS + ARMB_RETRAIN_SEEDS) * ARMB_EPOCHS
    proj_h = (arma_ep + armb_ep) * s_per_ep / 3600.0
    spent = spend_add(out, "p0", sec)
    print(f"[P0] {P0_EPOCHS} epochs in {sec:.2f} s -> {s_per_ep*1000:.3f} ms/epoch; "
          f"projected {proj_h:.2f} GPU-h for the registered batch "
          f"(+{spent:.2f} h already spent) vs cap {CAP_HOURS}", flush=True)
    if proj_h + spent > CAP_HOURS:
        write_status(out, "p0", "BLOCKED", s_per_epoch=s_per_ep,
                     projected_hours=round(proj_h, 2), spent_hours=spent,
                     cap_hours=CAP_HOURS,
                     reason="projection exceeds the registered 60 GPU-h cap")
        sys.exit(3)
    write_status(out, "p0", "DONE", s_per_epoch=s_per_ep, seconds=round(sec, 2),
                 projected_hours=round(proj_h, 2), cap_hours=CAP_HOURS,
                 device=dev_name)


# ---------------------------------------------------------------- ARM-B
def stage_armb_search(out, data_path, dev_name):
    stage = "armb_search"
    cap_guard(out, stage)
    try:
        import optuna
    except ImportError:
        write_status(out, stage, "BLOCKED",
                     reason="optuna not importable on this host; fallback to "
                            "random search is the supervisor's decision")
        sys.exit(3)
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    torch, nn = build_torch()
    dev = torch.device(dev_name)
    d = load_data(data_path)
    lam_n, T_n, _ = preprocess(d)
    tr, va = d["masks"]["train"], d["masks"]["val"]
    tt = lambda a: torch.from_numpy(np.ascontiguousarray(a)).to(dev)
    Xtr, Ttr, Ytr = tt(lam_n[tr]), tt(T_n[tr]), tt(d["b_LES"][tr])
    Xva, Tva, Yva = tt(lam_n[va]), tt(T_n[va]), tt(d["b_LES"][va])
    ntr = Xtr.shape[0]
    t0 = time.time()

    def train_trial(depth, width, act, batch, lr, seed, epochs=ARMB_EPOCHS):
        """Adam inside trials (CPU lane's optimizer; the paper's SGD rates
        measurably do not move in 400 epochs). Selection on VAL only — TEST
        rows are never touched here. Returns best val b_rms."""
        torch.manual_seed(seed); np.random.seed(seed)
        net = make_tbnn(nn, depth=depth, width=width, act=act).to(dev)
        opt = torch.optim.Adam(net.parameters(), lr=lr)
        bs = ntr if batch == "full" else int(batch)
        best = float("inf")
        for ep in range(epochs):
            net.train()
            perm = torch.randperm(ntr, device=dev)
            for s in range(0, ntr, bs):
                bidx = perm[s:s + bs]
                opt.zero_grad()
                loss = ((Nets.tbnn_forward(torch, net, Xtr[bidx], Ttr[bidx])
                         - Ytr[bidx]) ** 2).sum(dim=(1, 2)).mean()
                loss.backward(); opt.step()
            if (ep % 20 == 0) or (ep == epochs - 1):
                net.eval()
                v = val_b_rms(torch, Nets.tbnn_forward, net, Xva, Tva, Yva)
                if v < best:
                    best = v
        return best, net

    def objective(trial):
        if spend_hours(out) + (time.time() - t0) / 3600.0 >= CAP_HOURS:
            raise KeyboardInterrupt("GPU-hour cap reached inside search")
        depth = trial.suggest_int("depth", 2, 12)
        width = trial.suggest_int("width", 5, 100)
        act = trial.suggest_categorical("act", ["relu", "leakyrelu0.01", "tanh", "sigmoid"])
        batch = trial.suggest_categorical("batch", ["8192", "65536", "full"])
        lr = trial.suggest_float("lr", 1e-7, 1e-2, log=True)
        b = "full" if batch == "full" else int(batch)
        vals = []
        for seed in range(ARMB_SEEDS):
            best, _ = train_trial(depth, width, act, b, lr, seed)
            vals.append(best)
        return float(np.mean(vals))

    db = os.path.join(out, "armb_optuna.db")
    study = optuna.create_study(direction="minimize",
                                sampler=optuna.samplers.TPESampler(seed=0),
                                storage=f"sqlite:///{db}",
                                study_name="armb", load_if_exists=True)
    ndone = len([t for t in study.trials
                 if t.state == optuna.trial.TrialState.COMPLETE])
    remaining = max(ARMB_TRIALS - ndone, 0)
    print(f"[ARM-B] {ndone} trials complete, {remaining} to run", flush=True)
    interrupted = False
    if remaining:
        try:
            study.optimize(objective, n_trials=remaining)
        except KeyboardInterrupt:
            interrupted = True
    sec = time.time() - t0
    total = spend_add(out, stage, sec)
    ndone = len([t for t in study.trials
                 if t.state == optuna.trial.TrialState.COMPLETE])
    if interrupted or ndone < ARMB_TRIALS:
        write_status(out, stage, "BLOCKED", trials_complete=ndone,
                     reason=f"cap reached at {total:.2f} wall-h before "
                            f"{ARMB_TRIALS} trials completed")
        sys.exit(3)
    bp = study.best_params
    write_status(out, stage, "DONE", trials_complete=ndone,
                 best_params=bp, best_value=study.best_value,
                 seconds=round(sec, 1), sampler="TPE(seed=0)")


def stage_armb_retrain(out, data_path, dev_name):
    stage = "armb_retrain"
    cap_guard(out, stage)
    st = read_status(out, "armb_search")
    if not st or st.get("state") != "DONE":
        print("[ARM-B retrain] armb_search not DONE; run it first.", flush=True)
        sys.exit(1)
    bp = st["best_params"]
    torch, nn = build_torch()
    dev = torch.device(dev_name)
    d = load_data(data_path)
    lam_n, T_n, _ = preprocess(d)
    tr, va = d["masks"]["train"], d["masks"]["val"]
    tt = lambda a: torch.from_numpy(np.ascontiguousarray(a)).to(dev)
    Xtr, Ttr, Ytr = tt(lam_n[tr]), tt(T_n[tr]), tt(d["b_LES"][tr])
    Xva, Tva, Yva = tt(lam_n[va]), tt(T_n[va]), tt(d["b_LES"][va])
    ntr = Xtr.shape[0]
    bs = ntr if bp["batch"] == "full" else int(bp["batch"])
    prev = read_status(out, stage) or {}
    done_seeds = prev.get("seeds_done", {})
    t0 = time.time()
    for seed in range(ARMB_RETRAIN_SEEDS):
        if str(seed) in done_seeds:
            continue
        if spend_hours(out) + (time.time() - t0) / 3600.0 >= CAP_HOURS:
            spend_add(out, stage, time.time() - t0)
            write_status(out, stage, "BLOCKED", seeds_done=done_seeds,
                         reason="cap reached during retrain")
            sys.exit(3)
        torch.manual_seed(seed); np.random.seed(seed)
        net = make_tbnn(nn, depth=bp["depth"], width=bp["width"], act=bp["act"]).to(dev)
        opt = torch.optim.Adam(net.parameters(), lr=bp["lr"])
        best, best_state = float("inf"), None
        hist = os.path.join(out, f"hist_armb_s{seed}.csv")
        with open(hist, "w", newline="") as f:
            csv.writer(f).writerow(["epoch", "train_loss", "val_b_rms", "best_val"])
        for ep in range(ARMB_EPOCHS):
            net.train()
            perm = torch.randperm(ntr, device=dev)
            tot = 0.0
            for s in range(0, ntr, bs):
                bidx = perm[s:s + bs]
                opt.zero_grad()
                loss = ((Nets.tbnn_forward(torch, net, Xtr[bidx], Ttr[bidx])
                         - Ytr[bidx]) ** 2).sum(dim=(1, 2)).mean()
                loss.backward(); opt.step()
                tot += float(loss.detach()) * len(bidx)
            net.eval()
            v = val_b_rms(torch, Nets.tbnn_forward, net, Xva, Tva, Yva)
            if v < best:
                best = v
                best_state = {k: t.detach().cpu().clone() for k, t in net.state_dict().items()}
            if (ep % 20 == 0) or (ep == ARMB_EPOCHS - 1):
                with open(hist, "a", newline="") as f:
                    csv.writer(f).writerow([ep, tot / ntr, v, best])
        p = save_test_preds(torch, Nets.tbnn_forward, net, best_state,
                            lam_n, T_n, dev, d, out, "armb", seed)
        done_seeds[str(seed)] = dict(best_val=best, pred=os.path.basename(p))
        write_status(out, stage, "RUNNING", seeds_done=done_seeds, best_params=bp)
    sec = time.time() - t0
    spend_add(out, stage, sec)
    write_status(out, stage, "DONE", seeds_done=done_seeds, best_params=bp,
                 seconds=round(sec, 1))


# ---------------------------------------------------------------- main
STAGES = ["g0", "p0", "arma_tbnn", "arma_mlp", "armb_search", "armb_retrain"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.expanduser("~/r_ling_gpu/data/dataset.npz"))
    ap.add_argument("--out", default=os.path.expanduser("~/r_ling_gpu/out"))
    ap.add_argument("--frozen", action="store_true",
                    help="assert the pre-registration is signed/frozen; required "
                         "for every stage that trains (and for p0)")
    ap.add_argument("--stage", choices=STAGES, default=None,
                    help="run one stage only (default: all in order)")
    ap.add_argument("--device", default=None, help="cuda|cpu (default: auto)")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    if args.device is None:
        try:
            import torch
            args.device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            args.device = "cpu"

    todo = [args.stage] if args.stage else STAGES
    for stage in todo:
        st = read_status(args.out, stage)
        if st and st.get("state") == "DONE":
            print(f"[skip] {stage} already DONE", flush=True)
            continue
        if stage != "g0" and not args.frozen:
            print(f"[stop] stage {stage} requires --frozen: the pre-registration "
                  "is not signed; no training runs before the freeze.", flush=True)
            sys.exit(1)
        if stage == "g0":
            stage_g0(args.out, args.data)
        elif stage == "p0":
            stage_p0(args.out, args.data, args.device)
        elif stage == "arma_tbnn":
            stage_arma(args.out, args.data, "tbnn", args.device)
        elif stage == "arma_mlp":
            stage_arma(args.out, args.data, "mlp", args.device)
        elif stage == "armb_search":
            stage_armb_search(args.out, args.data, args.device)
        elif stage == "armb_retrain":
            stage_armb_retrain(args.out, args.data, args.device)
    print("[driver] all requested stages processed.", flush=True)


if __name__ == "__main__":
    main()
