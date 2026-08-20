#!/usr/bin/env python3
"""Ling, Kurzawski & Templeton (2016) TBNN, reproduced as a labelled VARIANT on
the Closure Challenge benchmark. See PREREGISTRATION.md - written first.

Trains, over 5 seeds:
  * TBNN  : 5 invariants -> 8x30 hidden -> 10 g^(n) -> sum_n g^(n) T^(n)  [Ling p.9]
  * MLP   : 5 invariants -> 10x10 hidden -> 6 components of b directly    [Ling p.6]
    (Ling's own control; the difference between the two is the entire test of the
     invariance embedding.)

Everything is bounded: hard epoch cap, wall-clock self-timeout, checkpoint every
CKPT_EVERY epochs so a restart resumes. No `kill` is ever needed.

Usage:  /home/ubuntu/closure-venv/bin/python train_tbnn.py [--seeds 0 1 2 3 4]
"""
from __future__ import annotations
import argparse, json, os, sys, time
import numpy as np
import torch
import torch.nn as nn

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "_common")
sys.path.insert(0, COMMON)
from of_read import realisability_violation

DATA = "/home/ubuntu/closure-data/tbnn/dataset.npz"
CKPT = "/home/ubuntu/closure-data/tbnn/ckpt"
os.makedirs(CKPT, exist_ok=True)

MAX_EPOCHS = 400
CKPT_EVERY = 25
WALL_LIMIT_S = 3600 * 3          # self-timeout: 3 h total, then stop and report
BATCH = 8192
LR_TBNN = 1e-3                   # see RESULTS.md departure note D3
LR_MLP = 1e-3
PATIENCE = 60                    # early stop on validation b_rms

# ---- pre-registered split (PREREGISTRATION.md sec. 6) -----------------------
TEST = {"alpha_15_13929_4048", "alpha_15_13929_2024",
        "alpha_05_4071_4048", "alpha_05_4071_2024",
        "AR_1_Ret_360", "AR_3_Ret_360", "AR_14_Ret_180", "NASA_2DWMH"}
VAL = {"alpha_05_10071_4048", "alpha_05_10071_2024",
       "alpha_15_7929_4048", "alpha_15_7929_2024", "AR_7_Ret_180"}
# group leak-blockers: same (alpha, length) triple as a TEST hill
GROUP_EXCLUDED = {"alpha_15_13929_3036", "alpha_05_4071_3036",
                  "alpha_05_10071_3036", "alpha_15_7929_3036"}


def hill_group(name):
    """(alpha, length) group key for a parametric hill, else the case name."""
    p = name.split("_")
    if p[0] == "alpha" and len(p) >= 4:
        return ("alpha_" + p[1], p[2])          # e.g. ('alpha_15','13929')
    return (name,)


def assert_disjoint(names, split_of):
    """Pre-registered disjointness assertion. Raises before any training."""
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


# ------------------------------------------------------------------ models
class TBNN(nn.Module):
    """Ling 2016 Fig. 3: invariants -> hidden stack -> 10 g^(n) -> merge with T."""
    def __init__(self, nin=5, nh=30, nlayers=8, nbasis=10):
        super().__init__()
        L, d = [], nin
        for _ in range(nlayers):
            L += [nn.Linear(d, nh), nn.LeakyReLU(0.01)]
            d = nh
        L += [nn.Linear(d, nbasis)]
        self.net = nn.Sequential(*L)

    def forward(self, lam, T):
        g = self.net(lam)                              # (N,10)
        return torch.einsum("ng,ngij->nij", g, T)      # (N,3,3)


class PlainMLP(nn.Module):
    """Ling 2016's control: same inputs, no basis, regress b's 6 components."""
    def __init__(self, nin=5, nh=10, nlayers=10):
        super().__init__()
        L, d = [], nin
        for _ in range(nlayers):
            L += [nn.Linear(d, nh), nn.LeakyReLU(0.01)]
            d = nh
        L += [nn.Linear(d, 6)]
        self.net = nn.Sequential(*L)

    def forward(self, lam, T):
        y = self.net(lam)
        i = [0, 0, 0, 1, 1, 2]; j = [0, 1, 2, 1, 2, 2]
        b = torch.zeros(y.shape[0], 3, 3, dtype=y.dtype, device=y.device)
        for c in range(6):
            b[:, i[c], j[c]] = y[:, c]
            if i[c] != j[c]:
                b[:, j[c], i[c]] = y[:, c]
        tr = b[:, 0, 0] + b[:, 1, 1] + b[:, 2, 2]
        b = b - torch.eye(3, device=y.device)[None] * (tr / 3.0)[:, None, None]
        return b


# ------------------------------------------------------------------ helpers
def frob_rms(x):
    return float(np.sqrt((x ** 2).sum(axis=(1, 2)).mean()))


def per_case_rms(pred, true, case_id, names, keep):
    out = {}
    for i, nm in enumerate(names):
        m = keep & (case_id == i)
        if m.sum() == 0:
            continue
        out[nm] = frob_rms(pred[m] - true[m])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    args = ap.parse_args()
    t_start = time.time()
    torch.set_num_threads(4)   # measured: 16 threads is 60x SLOWER than 4 on these tiny
                               # batches (scratchpad/numerics_B.md, N-B4). Not a typo.

    z = np.load(DATA, allow_pickle=True)
    names = [str(x) for x in z["names"]]
    lam_all = z["lam"]; T_all = z["T"]; bL = z["b_LES"]; bR = z["b_RANS"]
    valid = z["valid"]; cid = z["case_id"]

    split_of = {}
    for n in names:
        split_of[n] = "test" if n in TEST else ("val" if n in VAL else
                                                ("excluded" if n in GROUP_EXCLUDED else "train"))
    assert_lines = assert_disjoint([n for n in names if split_of[n] != "excluded"],
                                   split_of)
    for L in assert_lines:
        print("[assert] " + L, flush=True)

    idx_of = {s: np.zeros(len(cid), bool) for s in ("train", "val", "test")}
    for i, n in enumerate(names):
        s = split_of[n]
        if s in idx_of:
            idx_of[s] |= (cid == i)
    for s in idx_of:
        idx_of[s] &= valid
    print({s: int(v.sum()) for s, v in idx_of.items()}, flush=True)

    # ---- input scaling, computed on TRAINING CELLS ONLY -------------------
    tr = idx_of["train"]
    lam_s = np.sign(lam_all) * np.log1p(np.abs(lam_all))
    mu = lam_s[tr].mean(0); sd = lam_s[tr].std(0) + 1e-12
    lam_n = ((lam_s - mu) / sd).astype(np.float32)
    # exact reparametrisation of g^(n): scale each basis tensor to unit train RMS
    tscale = np.sqrt((T_all[tr] ** 2).sum(axis=(2, 3)).mean(axis=0)) + 1e-30
    T_n = (T_all / tscale[None, :, None, None]).astype(np.float32)
    print("lam mu:", mu.round(3), "sd:", sd.round(3), flush=True)
    print("basis train RMS:", tscale.round(4), flush=True)

    dev = torch.device("cpu")
    tens = lambda a: torch.from_numpy(np.ascontiguousarray(a)).to(dev)
    Xtr, Ttr, Ytr = tens(lam_n[tr]), tens(T_n[tr]), tens(bL[tr])
    Xva, Tva, Yva = tens(lam_n[idx_of["val"]]), tens(T_n[idx_of["val"]]), tens(bL[idx_of["val"]])

    results = {}
    for tag, Model, lr in (("TBNN", TBNN, LR_TBNN), ("MLP", PlainMLP, LR_MLP)):
        results[tag] = {}
        for seed in args.seeds:
            ck = os.path.join(CKPT, f"{tag}_s{seed}.pt")
            torch.manual_seed(seed); np.random.seed(seed)
            model = Model().to(dev)
            opt = torch.optim.Adam(model.parameters(), lr=lr)
            e0, best, best_state, bad = 0, np.inf, None, 0
            if os.path.exists(ck):
                st = torch.load(ck, weights_only=False)
                model.load_state_dict(st["model"]); opt.load_state_dict(st["opt"])
                e0, best, best_state, bad = st["epoch"], st["best"], st["best_state"], st["bad"]
                print(f"[resume] {tag} seed {seed} from epoch {e0}", flush=True)
            n = Xtr.shape[0]
            for ep in range(e0, MAX_EPOCHS):
                if time.time() - t_start > WALL_LIMIT_S:
                    print(f"[self-timeout] stopping at {tag} seed {seed} epoch {ep}", flush=True)
                    break
                model.train()
                perm = torch.randperm(n)
                tot = 0.0
                for s in range(0, n, BATCH):
                    b = perm[s:s + BATCH]
                    opt.zero_grad()
                    loss = ((model(Xtr[b], Ttr[b]) - Ytr[b]) ** 2).sum(dim=(1, 2)).mean()
                    loss.backward(); opt.step()
                    tot += float(loss.detach()) * len(b)
                model.eval()
                with torch.no_grad():
                    vb = model(Xva, Tva)
                    v = float(torch.sqrt(((vb - Yva) ** 2).sum(dim=(1, 2)).mean()))
                if v < best - 1e-6:
                    best, bad = v, 0
                    best_state = {k: t.clone() for k, t in model.state_dict().items()}
                else:
                    bad += 1
                if ep % 10 == 0 or ep == MAX_EPOCHS - 1:
                    print(f"  {tag} s{seed} ep{ep:4d} train_mse={tot/n:.5f} val_b_rms={v:.5f} best={best:.5f} bad={bad}", flush=True)
                if (ep + 1) % CKPT_EVERY == 0:
                    torch.save(dict(model=model.state_dict(), opt=opt.state_dict(),
                                    epoch=ep + 1, best=best, best_state=best_state, bad=bad), ck)
                if bad >= PATIENCE:
                    print(f"  {tag} s{seed} early stop at epoch {ep}", flush=True)
                    break
            if best_state is not None:
                model.load_state_dict(best_state)
            model.eval()
            with torch.no_grad():
                pred = np.concatenate([model(tens(lam_n[i:i + 50000]), tens(T_n[i:i + 50000])).numpy()
                                       for i in range(0, len(lam_n), 50000)])
            results[tag][seed] = dict(
                val_best=best,
                per_case=per_case_rms(pred, bL, cid, names, idx_of["test"]),
                pred_path=os.path.join(CKPT, f"pred_{tag}_s{seed}.npy"))
            np.save(results[tag][seed]["pred_path"], pred.astype(np.float32))
            torch.save(dict(model=model.state_dict(), opt=opt.state_dict(),
                            epoch=MAX_EPOCHS, best=best, best_state=best_state, bad=bad), ck)
            print(f"[done] {tag} seed {seed} val={best:.5f} test={results[tag][seed]['per_case']}", flush=True)

    json.dump(dict(results={k: {str(s): {kk: vv for kk, vv in d.items() if kk != 'pred_path'}
                               for s, d in v.items()} for k, v in results.items()},
                   assert_lines=assert_lines,
                   n_train=int(idx_of["train"].sum()), n_val=int(idx_of["val"].sum()),
                   n_test=int(idx_of["test"].sum()),
                   seconds=round(time.time() - t_start, 1)),
              open(os.path.join(HERE, "train_log.json"), "w"), indent=1)
    print("wrote train_log.json", flush=True)


if __name__ == "__main__":
    main()
