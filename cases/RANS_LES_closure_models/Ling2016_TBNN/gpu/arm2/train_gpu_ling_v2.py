#!/usr/bin/env python3
"""GPU driver, ARM 2 — Ling (2016) TBNN, matched-update-count reproduction.

WHY ARM 2 EXISTS (gpu/RESULTS.md D-1): arm 1 ran Ling's learning rate 2.5e-7
with ONE full-batch update per epoch. The paper (sidecar lines 131-132) updated
the weights AFTER EACH TRAINING POINT — ~3.4e5 times more updates per epoch on
341,717 training cells. Arm 2 runs the paper's regime: plain SGD at batch size 1,
    theta <- theta - lr * grad( ||b(theta; x_i) - b_LES_i||_F^2 )
one pass over a fresh per-epoch permutation of the TRAIN rows = 342,014 updates
per epoch (v1's training mask; the scorer's 341,717 additionally drops non-finite b_RANS). TBNN 8x30 LeakyReLU(0.01) at lr 2.5e-7; control MLP 10x10 at 2.5e-6;
seeds 0, 1, 2. The epoch budget E is NOT fixed in code: stage p0 measures the
per-update cost and writes E into status_p0.json (E_TARGET / E_MIN below).

Stages, in order (each skippable if its status JSON says DONE):
  g0         planted-zero controls G0a + G0b (numpy only; runs on the lab box).
  p0         (--frozen) equivalence checks (stacked-eager vs the v1 single-model
             reference; CUDA-graph vs eager), then the timing gate -> E.
  arma2_tbnn ARM-A2 TBNN, 3 seeds, per-point SGD lr 2.5e-7, E epochs.
  arma2_mlp  ARM-A2 control MLP, 3 seeds, per-point SGD lr 2.5e-6, E epochs.
  shutdown   ALWAYS last, on every path (DONE / BLOCKED / refusal / exception):
             writes out/COMPLETE.json, flushes spend.json, then — only with
             --shutdown, only on the GPU node, only with a CUDA device —
             `sudo shutdown -h now` with the attempt logged first.
  smoke      (never with --frozen) CPU/GPU smoke on a --smoke-rows subset.

HOW THE PER-POINT STEP IS MADE CHEAP WITHOUT CHANGING THE MATHEMATICS
  * The three seeds of one model are trained as a STACK: every weight is a
    tensor (S, out, in) and one batched matmul (baddbmm) advances all S models.
    Seed s only ever sees its own row perm[s, t] and its own parameters, so the
    stacked step is exactly S independent per-point SGD steps. The initial
    weights are drawn by v1's own make_tbnn()/make_mlp() under manual_seed(s)
    and copied into the stack, so the initialisation is v1's per seed.
  * The permutation for the epoch and an integer counter live on the device;
    the step indexes the resident TRAIN tensors by perm[:, ctr] and increments
    ctr on the device. No host work and no allocation per update.
  * On CUDA the step is captured ONCE into a CUDA graph, unrolled GRAPH_UNROLL
    times, and replayed; a 1-step graph handles remainders so every history
    point falls on an exact update count. --no-graph selects the eager loop.
  * Two refusable checks run in p0 (and in smoke), each after 1,000 updates
    from the same seed: (a) stacked eager vs v1's nn.Sequential + torch.optim.SGD
    reference, (b) graph vs eager. Both must agree on the parameters to 1e-6
    relative, and the parameters must have MOVED (the check is not vacuous).
    Failure -> BLOCKED, exit 3, after the shutdown stage.

Inherited VERBATIM from v1 train_gpu_ling.py (frozen 11f93da6): the split,
assert_disjoint(), preprocess() (D4 signed-log1p, D5 basis RMS rescaling),
realisability reader, G0 controls, model definitions, status/spend/cap
conventions, prediction file format (pred_<tag>_s<seed>.npz with idx).

Usage (on gpu1):
  ~/r_ling_gpu/venv/bin/python train_gpu_ling_v2.py --frozen --shutdown \
      --data ~/r_ling_gpu/data/dataset.npz --out ~/r_ling_gpu/arm2/out
Lab-box, no GPU, no training:
  python train_gpu_ling_v2.py --stage g0 --data /home/ubuntu/closure-data/tbnn/dataset.npz --out <scratch>
  python train_gpu_ling_v2.py --stage smoke --smoke-rows 2000 --smoke-epochs 2 --data ... --out <scratch>
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, os, socket, subprocess, sys, time, traceback
import numpy as np

# torch imported lazily: the g0 stage is pure numpy and must run on the lab box.

# ---------------------------------------------------------------- constants
PLANT = 1.234e-03            # the lab's standing planted-zero constant
CAP_HOURS = 40.0             # ARM 2 GPU-hour cap (this pre-registration)
E_TARGET = 300               # epoch budget ceiling; p0 may lower it
E_MIN = 50                   # below this p0 writes BLOCKED (not worth running)
BUDGET_FRACTION = 0.8        # E uses 0.8 of the remaining cap
ARMA_LR_TBNN = 2.5e-7        # Ling p. 7, plain SGD, per-point updates
ARMA_LR_MLP = 2.5e-6         # Ling p. 6, plain SGD, per-point updates
SEEDS = [0, 1, 2]
HIST_EVERY = 20_000          # history row every 20,000 updates
P0_UPDATES = 20_000          # timing-gate sample (after warm-up)
CHECK_UPDATES = 1_000        # equivalence checks: updates from the same seed
CHECK_REL_TOL = 1e-6         # ... must agree on the parameters to this
GRAPH_UNROLL = 64            # per-point steps captured per CUDA graph replay
N_TRAIN_REGISTERED = 342_014 # TRAIN rows under v1's training mask (`valid` = k_LES
                             # floor, b_LES defined), asserted at load. NOT 341,717:
                             # that is the SCORER's count (valid AND finite b_RANS,
                             # _common/trainmean_baseline.json n_train_cells vs
                             # n_train_cells_LES_mask_only). Updates/epoch = 342,014.
DATASET_SHA256 = "aad528dbd2cb35d2ac32326cc083bebd1c155fbc1439fe48362ba6b96b0b5459"
GPU_HOST_PREFIX = "ip-172-31-44-162"   # gpu1; --shutdown refuses elsewhere

# ---- pre-registered split, verbatim from ../train_tbnn.py (CPU lane) --------
TEST = {"alpha_15_13929_4048", "alpha_15_13929_2024",
        "alpha_05_4071_4048", "alpha_05_4071_2024",
        "AR_1_Ret_360", "AR_3_Ret_360", "AR_14_Ret_180", "NASA_2DWMH"}
VAL = {"alpha_05_10071_4048", "alpha_05_10071_2024",
       "alpha_15_7929_4048", "alpha_15_7929_2024", "AR_7_Ret_180"}
GROUP_EXCLUDED = {"alpha_15_13929_3036", "alpha_05_4071_3036",
                  "alpha_05_10071_3036", "alpha_15_7929_3036"}


class Halt(Exception):
    """A stage stopped the run. Carries the status state and the exit code;
    main() records it and the shutdown stage still runs."""
    def __init__(self, state, code, reason):
        super().__init__(reason)
        self.state, self.code, self.reason = state, code, reason


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_file(path, chunk=1 << 24):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


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
    rec = dict(stage=stage, state=state, utc=utc(), **extra)
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
    sp["flushed_utc"] = utc()
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
        raise Halt("BLOCKED", 3, "cap reached before stage " + stage)
    return h


# ---------------------------------------------------------------- G0 controls
def stage_g0(out, data_path):
    """G0a planted-zero on the b_rms scorer; G0b plant on the realisability
    reader. Pure numpy on a COPY; the file on disk is never modified.
    Refusal -> exit 2 (NOT A RESULT for the whole arm). Verbatim from v1 apart
    from the dataset-sha check and Halt in place of sys.exit."""
    t0 = time.time()
    dsha = sha256_file(data_path)
    print(f"[g0] dataset sha256 {dsha}", flush=True)
    if dsha != DATASET_SHA256:
        write_status(out, "g0", "REFUSED", dataset_sha256=dsha,
                     reason="dataset sha256 differs from the frozen F.4 value")
        raise Halt("REFUSED", 2, "dataset sha mismatch")
    d = load_data(data_path)
    names, cid, valid, bL = d["names"], d["cid"], d["valid"], d["b_LES"]
    ntr = int(d["masks"]["train"].sum())
    if ntr != N_TRAIN_REGISTERED:
        write_status(out, "g0", "REFUSED", n_train=ntr,
                     reason=f"TRAIN rows {ntr} != registered {N_TRAIN_REGISTERED}")
        raise Halt("REFUSED", 2, "train row count mismatch")

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
        raise Halt("REFUSED", 2, "G0a refusal")

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
        raise Halt("REFUSED", 2, "G0b refusal")

    sec = time.time() - t0
    spend_add(out, "g0", sec)
    write_status(out, "g0", "DONE", plant=PLANT, cell=k, case=case,
                 b01_before=b01, rms_clean=rms_c, rms_planted=rms_p,
                 recovered_plant=recovered, rel_err=rel,
                 g0b_forced_norm=norm, g0b_flagged=g0b_ok, seconds=round(sec, 2),
                 dataset_sha256=dsha, n_train=ntr,
                 n_val=int(d["masks"]["val"].sum()), n_test=int(d["masks"]["test"].sum()),
                 assert_lines=d["assert_lines"])


# ---------------------------------------------------------------- models (v1)
def build_torch():
    import torch
    import torch.nn as nn
    # float32 semantics everywhere: TF32 would make the stacked bmm and the
    # reference mm disagree by construction
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
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
    """v1's forward passes — the REFERENCE implementation the stacked step is
    checked against. TBNN: g = net(lam); b = einsum('ng,ngij->nij', g, T).
    MLP: 6 unique components -> symmetric traceless b (CPU-lane code)."""
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


MODEL = {   # which -> (v1 constructor, v1 forward, lr)
    "tbnn": (lambda nn: make_tbnn(nn), Nets.tbnn_forward, ARMA_LR_TBNN),
    "mlp":  (lambda nn: Nets.make_mlp(nn), Nets.mlp_forward, ARMA_LR_MLP),
}


# ---------------------------------------------------------------- stacked nets
class Stacked:
    """S copies of one v1 net held as stacked tensors W[l] (S,out,in),
    bias[l] (S,out). forward(x (S,B,nin), T (S,B,10,3,3) or None) -> (S,B,3,3).
    Layer l of copy s is exactly nets[s][l]: baddbmm computes, per s,
    h_s @ W_s^T + b_s, which is what nn.Linear computes."""
    MLP_IDX = [[0, 1, 2], [1, 3, 4], [2, 4, 5]]     # v1's (i,j) -> component

    def __init__(self, torch, nets, which, dev):
        self.torch, self.which, self.dev = torch, which, dev
        lin = [m for m in nets[0] if isinstance(m, torch.nn.Linear)]
        self.nlayers = len(lin)
        self.W, self.b = [], []
        for l in range(self.nlayers):
            Ws = [[m for m in n if isinstance(m, torch.nn.Linear)][l] for n in nets]
            self.W.append(torch.stack([m.weight.detach() for m in Ws]).to(dev).clone().requires_grad_(True))
            self.b.append(torch.stack([m.bias.detach() for m in Ws]).to(dev).clone().requires_grad_(True))
        self.P = self.W + self.b
        self.S = self.W[0].shape[0]
        self.idx = torch.tensor(self.MLP_IDX, dtype=torch.long, device=dev)
        self.eye = torch.eye(3, device=dev)

    def forward(self, x, T=None):
        torch = self.torch
        h = x
        for l in range(self.nlayers):
            h = torch.baddbmm(self.b[l].unsqueeze(1), h, self.W[l].transpose(1, 2))
            if l < self.nlayers - 1:
                h = torch.nn.functional.leaky_relu(h, 0.01)
        if self.which == "tbnn":
            return torch.einsum("sbg,sbgij->sbij", h, T)
        b = h[..., self.idx]                                   # (S,B,3,3) symmetric
        tr = b[..., 0, 0] + b[..., 1, 1] + b[..., 2, 2]
        return b - self.eye * (tr / 3.0)[..., None, None]

    # ---- parameter state helpers
    def snapshot(self):
        return [p.detach().cpu().clone() for p in self.P]

    def restore(self, snap):
        with self.torch.no_grad():
            for p, s in zip(self.P, snap):
                p.copy_(s.to(self.dev))

    def seed_slice(self, snap, s):
        return [t[s].clone() for t in snap]

    @staticmethod
    def rel_diff(a, b):
        """max|a-b| / max|b| over the concatenated parameter vectors."""
        num = max(float((x.double() - y.double()).abs().max()) for x, y in zip(a, b))
        den = max(float(y.double().abs().max()) for y in b)
        return num / den

    def linear_params_of(self, net):
        """v1 net's parameters in the stack's order (weights..., biases...)."""
        lin = [m for m in net if isinstance(m, self.torch.nn.Linear)]
        return [m.weight.detach().cpu() for m in lin] + [m.bias.detach().cpu() for m in lin]


# ---------------------------------------------------------------- trainer
class PerPointTrainer:
    """Per-point plain SGD over S stacked seeds on resident tensors.
    One update = for every seed s:  theta_s -= lr * d/dtheta_s ||b_s(x_i) - y_i||_F^2,
    i = perm[s, ctr]; then ctr += 1 (on the device)."""

    def __init__(self, torch, which, seeds, dev, Xtr, Ttr, Ytr, Xva, Tva, Yva,
                 use_graph, lr=None):
        self.torch, self.which, self.seeds, self.dev = torch, which, list(seeds), dev
        make, self.ref_fwd, self.lr = MODEL[which]
        if lr is not None:
            self.lr = lr
        nn = torch.nn
        self.nets = []
        for s in self.seeds:                       # v1's initialisation per seed
            torch.manual_seed(s); np.random.seed(s)
            self.nets.append(make(nn))
        self.net = Stacked(torch, self.nets, which, dev)
        self.S = self.net.S
        self.Xtr, self.Ttr, self.Ytr = Xtr, Ttr, Ytr
        self.Xva, self.Tva, self.Yva = Xva, Tva, Yva
        self.N = Xtr.shape[0]
        self.perm = torch.zeros(self.S, self.N, dtype=torch.long, device=dev)
        self.ctr = torch.zeros(1, dtype=torch.long, device=dev)
        self.loss_acc = torch.zeros(self.S, dtype=torch.float64, device=dev)
        self.use_graph = bool(use_graph and dev.type == "cuda")
        self.gU = self.g1 = None
        self._acc_n = 0                       # updates accumulated into loss_acc
        self.step = self._make_step()

    # ---- the per-point step (identical maths in eager and graph mode)
    def _make_step(self):
        torch, net, P, lr, S = self.torch, self.net, self.net.P, self.lr, self.S
        Xtr, Ttr, Ytr, perm, ctr, loss_acc = (self.Xtr, self.Ttr, self.Ytr,
                                              self.perm, self.ctr, self.loss_acc)
        tbnn = self.which == "tbnn"

        def step():
            idx = perm.index_select(1, ctr).reshape(S)                   # (S,)
            x = Xtr.index_select(0, idx).unsqueeze(1)                     # (S,1,5)
            y = Ytr.index_select(0, idx)                                  # (S,3,3)
            T = Ttr.index_select(0, idx).unsqueeze(1) if tbnn else None   # (S,1,10,3,3)
            b = net.forward(x, T).squeeze(1)                              # (S,3,3)
            loss_s = ((b - y) ** 2).sum(dim=(1, 2))                       # per-sample ||.||_F^2
            grads = torch.autograd.grad(loss_s.sum(), P)                  # seeds are disjoint
            with torch.no_grad():
                torch._foreach_add_(P, grads, alpha=-lr)                  # theta -= lr * grad
                loss_acc.add_(loss_s.detach())
                ctr.add_(1)
        return step

    def capture_graphs(self):
        """Capture GRAPH_UNROLL steps and 1 step into CUDA graphs. Warm-up runs
        on a side stream and mutates state; a snapshot restores it after."""
        torch = self.torch
        snap, ctr0, acc0 = self.net.snapshot(), self.ctr.clone(), self.loss_acc.clone()
        s = torch.cuda.Stream()
        s.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(s):
            for _ in range(3):
                self.step()
        torch.cuda.current_stream().wait_stream(s)
        self.gU = torch.cuda.CUDAGraph()
        with torch.cuda.graph(self.gU):
            for _ in range(GRAPH_UNROLL):
                self.step()
        self.g1 = torch.cuda.CUDAGraph()
        with torch.cuda.graph(self.g1):
            self.step()
        torch.cuda.synchronize()
        self.net.restore(snap)
        with torch.no_grad():
            self.ctr.copy_(ctr0); self.loss_acc.copy_(acc0)

    def run_updates(self, n):
        """Advance exactly n updates from the current ctr."""
        self._acc_n += n
        if self.use_graph:
            if self.gU is None:
                self.capture_graphs()
            for _ in range(n // GRAPH_UNROLL):
                self.gU.replay()
            for _ in range(n % GRAPH_UNROLL):
                self.g1.replay()
        else:
            for _ in range(n):
                self.step()

    def set_epoch_perm(self, epoch):
        """Fresh permutation per seed per epoch, deterministic in (seed, epoch)
        so a restart reproduces it."""
        torch = self.torch
        with torch.no_grad():
            for r, s in enumerate(self.seeds):
                g = torch.Generator(device=self.dev)
                g.manual_seed(1_000_003 * (s + 1) + epoch)
                self.perm[r].copy_(torch.randperm(self.N, generator=g, device=self.dev))
            self.ctr.zero_()

    def sync(self):
        if self.dev.type == "cuda":
            self.torch.cuda.synchronize()

    def pop_train_loss(self):
        """Running mean of the per-sample loss since the last call, per seed."""
        self.sync()
        acc = self.loss_acc.cpu().numpy().copy()
        n, self._acc_n = self._acc_n, 0
        with self.torch.no_grad():
            self.loss_acc.zero_()
        return (acc / max(n, 1)).tolist()

    def val_b_rms(self, chunk=50_000):
        """Full-batch no_grad VAL b_rms per seed (float64 accumulation)."""
        torch = self.torch
        ss = torch.zeros(self.S, dtype=torch.float64, device=self.dev)
        with torch.no_grad():
            for i in range(0, self.Xva.shape[0], chunk):
                x = self.Xva[i:i + chunk].unsqueeze(0).expand(self.S, -1, -1)
                T = (self.Tva[i:i + chunk].unsqueeze(0).expand(self.S, -1, -1, -1, -1)
                     if self.which == "tbnn" else None)
                b = self.net.forward(x, T)
                ss += ((b - self.Yva[i:i + chunk].unsqueeze(0)) ** 2).sum(dim=(1, 2, 3)).double()
        return torch.sqrt(ss / self.Xva.shape[0]).cpu().numpy().tolist()

    def predict(self, X, T, chunk=50_000):
        """(S, n, 3, 3) predictions of the CURRENT parameters."""
        outs = []
        with self.torch.no_grad():
            for i in range(0, X.shape[0], chunk):
                x = X[i:i + chunk].unsqueeze(0).expand(self.S, -1, -1)
                t = (T[i:i + chunk].unsqueeze(0).expand(self.S, -1, -1, -1, -1)
                     if self.which == "tbnn" else None)
                outs.append(self.net.forward(x, t).cpu().numpy())
        return np.concatenate(outs, axis=1)


# ---------------------------------------------------------------- checks
def check_stacked_vs_reference(trainer, n=CHECK_UPDATES):
    """(a) stacked-eager step vs v1's nn.Sequential + torch.optim.SGD, per
    seed, after n per-point updates over the SAME rows. Returns the max
    relative parameter difference and the relative movement from init."""
    torch = trainer.torch
    snap0 = trainer.net.snapshot()
    trainer.set_epoch_perm(0)
    perm_cpu = trainer.perm.cpu().numpy()
    was_graph = trainer.use_graph
    trainer.use_graph = False                      # eager for this check
    trainer.run_updates(n)
    trainer.use_graph = was_graph
    trainer.sync()
    stacked = trainer.net.snapshot()
    worst = 0.0
    for r, s in enumerate(trainer.seeds):
        torch.manual_seed(s); np.random.seed(s)
        net = MODEL[trainer.which][0](torch.nn).to(trainer.dev)     # same init as the stack
        opt = torch.optim.SGD(net.parameters(), lr=trainer.lr, momentum=0.0,
                              dampening=0.0, weight_decay=0.0, nesterov=False)
        for t in range(n):
            i = int(perm_cpu[r, t])
            opt.zero_grad()
            b = trainer.ref_fwd(torch, net, trainer.Xtr[i:i + 1], trainer.Ttr[i:i + 1])
            loss = ((b - trainer.Ytr[i:i + 1]) ** 2).sum()
            loss.backward(); opt.step()
        ref = trainer.net.linear_params_of(net)
        worst = max(worst, Stacked.rel_diff(trainer.net.seed_slice(stacked, r), ref))
    moved = Stacked.rel_diff(stacked, snap0)
    trainer.net.restore(snap0)
    with torch.no_grad():
        trainer.ctr.zero_(); trainer.loss_acc.zero_()
    trainer._acc_n = 0
    return worst, moved


def check_graph_vs_eager(trainer, n=CHECK_UPDATES):
    """(b) CUDA-graph replay vs the eager loop, n updates from the same state."""
    torch = trainer.torch
    snap0 = trainer.net.snapshot()
    trainer.set_epoch_perm(0)
    trainer.use_graph = False
    trainer.run_updates(n); trainer.sync()
    eager = trainer.net.snapshot()
    trainer.net.restore(snap0)
    with torch.no_grad():
        trainer.ctr.zero_(); trainer.loss_acc.zero_()
    trainer.use_graph = True
    trainer.run_updates(n); trainer.sync()
    graph = trainer.net.snapshot()
    rel = Stacked.rel_diff(graph, eager)
    moved = Stacked.rel_diff(graph, snap0)
    trainer.net.restore(snap0)
    with torch.no_grad():
        trainer.ctr.zero_(); trainer.loss_acc.zero_()
    trainer._acc_n = 0
    return rel, moved


def run_checks(out, stage, trainer, want_graph):
    rec = {}
    rel, moved = check_stacked_vs_reference(trainer)
    rec["stacked_vs_v1_reference"] = dict(updates=CHECK_UPDATES, rel_param_diff=rel,
                                          rel_param_movement=moved, tol=CHECK_REL_TOL,
                                          ok=bool(rel < CHECK_REL_TOL and moved > 1e-9))
    print(f"[check] {trainer.which} stacked vs v1 reference: rel={rel:.3e} moved={moved:.3e} "
          f"-> {'OK' if rec['stacked_vs_v1_reference']['ok'] else 'REFUSE'}", flush=True)
    if want_graph:
        rel, moved = check_graph_vs_eager(trainer)
        rec["graph_vs_eager"] = dict(updates=CHECK_UPDATES, rel_param_diff=rel,
                                     rel_param_movement=moved, tol=CHECK_REL_TOL,
                                     ok=bool(rel < CHECK_REL_TOL and moved > 1e-9))
        print(f"[check] {trainer.which} graph vs eager: rel={rel:.3e} moved={moved:.3e} "
              f"-> {'OK' if rec['graph_vs_eager']['ok'] else 'REFUSE'}", flush=True)
    else:
        rec["graph_vs_eager"] = dict(ok=None, note="graph mode not selected/available")
    if not all(v["ok"] for v in rec.values() if v["ok"] is not None):
        write_status(out, stage, "BLOCKED", checks=rec,
                     reason="per-point step implementation failed an equivalence check")
        raise Halt("BLOCKED", 3, "equivalence check refused")
    return rec


# ---------------------------------------------------------------- data to device
def device_data(torch, d, dev, smoke_rows=None):
    lam_n, T_n, scal = preprocess(d)
    tr, va = d["masks"]["train"], d["masks"]["val"]
    tr_idx, va_idx = np.flatnonzero(tr), np.flatnonzero(va)
    if smoke_rows:
        tr_idx, va_idx = tr_idx[:smoke_rows], va_idx[:smoke_rows]
    tt = lambda a: torch.from_numpy(np.ascontiguousarray(a)).to(dev)
    D = dict(Xtr=tt(lam_n[tr_idx]), Ttr=tt(T_n[tr_idx]), Ytr=tt(d["b_LES"][tr_idx]),
             Xva=tt(lam_n[va_idx]), Tva=tt(T_n[va_idx]), Yva=tt(d["b_LES"][va_idx]))
    return D, lam_n, T_n, scal


def new_trainer(torch, which, dev, D, use_graph, seeds=SEEDS):
    return PerPointTrainer(torch, which, seeds, dev, D["Xtr"], D["Ttr"], D["Ytr"],
                           D["Xva"], D["Tva"], D["Yva"], use_graph)


# ---------------------------------------------------------------- P0 timing
def time_updates(trainer, n):
    n = min(n, trainer.N)
    trainer.set_epoch_perm(0)
    trainer.run_updates(min(2 * GRAPH_UNROLL, n)); trainer.sync()     # warm-up
    trainer.set_epoch_perm(1)                                           # fresh counter
    t0 = time.time()
    trainer.run_updates(n); trainer.sync()
    s_upd = (time.time() - t0) / n
    trainer.val_b_rms(); trainer.sync()                                  # warm-up
    t0 = time.time()
    trainer.val_b_rms(); trainer.sync()
    s_val = time.time() - t0
    return s_upd, s_val


def stage_p0(out, data_path, dev_name, use_graph):
    """Equivalence checks, then the timing gate that sets E."""
    cap_guard(out, "p0")
    torch, nn = build_torch()
    dev = torch.device(dev_name)
    t0 = time.time()
    d = load_data(data_path)
    D, _, _, _ = device_data(torch, d, dev)
    N = D["Xtr"].shape[0]
    want_graph = bool(use_graph and dev.type == "cuda")
    rec = dict(mode="graph" if want_graph else "eager", unroll=GRAPH_UNROLL,
               device=dev_name, torch=torch.__version__, n_train=N, checks={}, timing={})
    epoch_s_total = 0.0
    for which in ("tbnn", "mlp"):
        tr = new_trainer(torch, which, dev, D, want_graph)
        rec["checks"][which] = run_checks(out, "p0", tr, want_graph)
        tr0 = time.time()
        fresh = new_trainer(torch, which, dev, D, want_graph)     # fresh init for timing
        s_upd, s_val = time_updates(fresh, P0_UPDATES)
        n_hist = N / HIST_EVERY
        epoch_s = N * s_upd + n_hist * s_val
        rec["timing"][which] = dict(updates_timed=P0_UPDATES, s_per_update=s_upd,
                                    s_per_val_eval=s_val, val_evals_per_epoch=n_hist,
                                    epoch_s=epoch_s, timing_wall_s=time.time() - tr0)
        print(f"[P0] {which}: {s_upd*1e3:.4f} ms/update (stack of {len(SEEDS)} seeds), "
              f"val eval {s_val:.3f} s -> epoch {epoch_s:.1f} s", flush=True)
        epoch_s_total += epoch_s
        del tr, fresh
    sec = time.time() - t0
    spent = spend_add(out, "p0", sec)
    budget_s = BUDGET_FRACTION * (CAP_HOURS - spent) * 3600.0
    E = int(min(E_TARGET, math.floor(budget_s / epoch_s_total)))
    proj_h = E * epoch_s_total / 3600.0
    rec.update(E_target=E_TARGET, E_min=E_MIN, budget_fraction=BUDGET_FRACTION,
               cap_hours=CAP_HOURS, spent_hours=spent, epoch_s_both_models=epoch_s_total,
               E_epochs=E, projected_hours=round(proj_h, 3),
               updates_per_epoch_per_seed=N, seconds=round(sec, 2),
               formula="E = min(E_TARGET, floor(0.8*(CAP-spent)*3600 / (epoch_s_tbnn + epoch_s_mlp))); "
                       "each model runs its 3 seeds as one stack, so 2 stacked runs cover 2 models x 3 seeds")
    print(f"[P0] epoch_s (both models) {epoch_s_total:.1f} s; E = {E} "
          f"(target {E_TARGET}, min {E_MIN}); projected {proj_h:.2f} GPU-h of cap {CAP_HOURS}", flush=True)
    if E < E_MIN:
        write_status(out, "p0", "BLOCKED", reason=f"E={E} < E_MIN={E_MIN} within "
                     f"{BUDGET_FRACTION} of the {CAP_HOURS} GPU-h cap", **rec)
        raise Halt("BLOCKED", 3, "epoch budget below E_MIN")
    write_status(out, "p0", "DONE", **rec)


# ---------------------------------------------------------------- ARM-A2
def train_perpoint(out, tag, trainer, epochs, deadline_check, hist_every=HIST_EVERY):
    """E epochs of per-point SGD; history every hist_every updates; best-val
    state per seed; restartable checkpoint every epoch. Returns
    (final_snapshot, best_snapshot(list per layer, stacked), best(list), stopped)."""
    torch = trainer.torch
    S, N = trainer.S, trainer.N
    ck = os.path.join(out, f"ck_{tag}.pt")
    hists = [os.path.join(out, f"hist_{tag}_s{s}.csv") for s in trainer.seeds]
    e0, gupd = 0, 0
    best = [float("inf")] * S
    best_snap = trainer.net.snapshot()
    if os.path.exists(ck):
        st = torch.load(ck, weights_only=False, map_location="cpu")
        trainer.net.restore(st["params"])
        e0, gupd, best, best_snap = st["epoch"], st["global_updates"], st["best"], st["best_params"]
        print(f"[resume] {tag} from epoch {e0} ({gupd} updates)", flush=True)
    for h in hists:
        if not os.path.exists(h):
            with open(h, "w", newline="") as f:
                csv.writer(f).writerow(["epoch", "update", "train_loss_mean", "val_b_rms", "best_val"])
    trainer._acc_n = 0
    with torch.no_grad():
        trainer.loss_acc.zero_()

    def history(epoch):
        tl = trainer.pop_train_loss()
        v = trainer.val_b_rms()
        cur = None
        for r in range(S):
            if v[r] < best[r] - 1e-12:
                best[r] = v[r]
                if cur is None:
                    cur = trainer.net.snapshot()
                for l in range(len(best_snap)):
                    best_snap[l][r] = cur[l][r]
            with open(hists[r], "a", newline="") as f:
                csv.writer(f).writerow([epoch, gupd, tl[r], v[r], best[r]])
        print(f"[{tag}] ep {epoch} upd {gupd} train {np.round(tl, 5).tolist()} "
              f"val {np.round(v, 5).tolist()}", flush=True)

    stopped = False
    for ep in range(e0, epochs):
        trainer.set_epoch_perm(ep)
        pos = 0
        while pos < N:
            n = min(hist_every - (gupd % hist_every), N - pos)
            trainer.run_updates(n)
            pos += n; gupd += n
            if gupd % hist_every == 0 or (pos == N and ep == epochs - 1):
                history(ep)
        trainer.sync()
        torch.save(dict(params=trainer.net.snapshot(), epoch=ep + 1, global_updates=gupd,
                        best=best, best_params=best_snap, seeds=trainer.seeds), ck)
        if deadline_check():
            stopped = True
            break
    return trainer.net.snapshot(), best_snap, best, stopped


def save_test_preds(trainer, best_snap, lam_n, T_n, d, out, tag):
    """TEST-case predictions per seed, best-val and final, with the global row
    indices (dataset order) — v1's format, one file per seed."""
    torch = trainer.torch
    te = d["masks"]["test"]
    idx = np.flatnonzero(te)
    tt = lambda a: torch.from_numpy(np.ascontiguousarray(a)).to(trainer.dev)
    X, T = tt(lam_n[te]), tt(T_n[te])
    final_snap = trainer.net.snapshot()
    pred_final = trainer.predict(X, T)
    trainer.net.restore(best_snap)
    pred_best = trainer.predict(X, T)
    trainer.net.restore(final_snap)
    paths = []
    for r, s in enumerate(trainer.seeds):
        p = os.path.join(out, f"pred_{tag}_s{s}.npz")
        np.savez_compressed(p, idx=idx.astype(np.int64),
                            pred_best=pred_best[r].astype(np.float32),
                            pred_final=pred_final[r].astype(np.float32))
        paths.append(os.path.basename(p))
    return paths


def stage_arma2(out, data_path, which, dev_name, use_graph):
    stage = f"arma2_{which}"
    cap_guard(out, stage)
    p0 = read_status(out, "p0")
    if not p0 or p0.get("state") != "DONE":
        write_status(out, stage, "BLOCKED", reason="status_p0.json is not DONE; E is unset")
        raise Halt("BLOCKED", 3, "p0 not done")
    E = int(p0["E_epochs"])
    torch, nn = build_torch()
    dev = torch.device(dev_name)
    d = load_data(data_path)
    D, lam_n, T_n, scal = device_data(torch, d, dev)
    want_graph = bool(use_graph and dev.type == "cuda")
    trainer = new_trainer(torch, which, dev, D, want_graph)
    t0 = time.time()

    def deadline_check():
        return spend_hours(out) + (time.time() - t0) / 3600.0 >= CAP_HOURS

    write_status(out, stage, "RUNNING", lr=trainer.lr, epochs=E, seeds=SEEDS,
                 mode=p0["mode"], updates_per_epoch=trainer.N, scaling=scal)
    final_snap, best_snap, best, stopped = train_perpoint(out, which, trainer, E, deadline_check)
    sec = time.time() - t0
    total = spend_add(out, stage, sec)
    if stopped or total >= CAP_HOURS:
        write_status(out, stage, "BLOCKED", best_val=best,
                     reason=f"cumulative {total:.2f} wall-h vs cap {CAP_HOURS} GPU-h")
        raise Halt("BLOCKED", 3, "cap reached during " + stage)
    preds = save_test_preds(trainer, best_snap, lam_n, T_n, d, out, which)
    write_status(out, stage, "DONE", lr=trainer.lr, epochs=E, seeds=SEEDS, mode=p0["mode"],
                 updates_per_epoch=trainer.N, total_updates_per_seed=E * trainer.N,
                 best_val={str(s): best[r] for r, s in enumerate(SEEDS)},
                 preds=preds, seconds=round(sec, 1), scaling=scal)


# ---------------------------------------------------------------- smoke (never frozen)
def stage_smoke(out, data_path, dev_name, use_graph, rows, epochs):
    """Subset smoke of the whole per-point path: checks, timing, a short
    training, prediction files under a smoke_ prefix. Not a result."""
    torch, nn = build_torch()
    dev = torch.device(dev_name)
    if dev.type == "cpu":
        torch.set_num_threads(4)
    d = load_data(data_path)
    D, lam_n, T_n, scal = device_data(torch, d, dev, smoke_rows=rows)
    want_graph = bool(use_graph and dev.type == "cuda")
    rec = dict(rows=rows, epochs=epochs, device=dev_name, mode="graph" if want_graph else "eager",
               torch=torch.__version__, threads=torch.get_num_threads(), checks={}, timing={}, train={})
    t0 = time.time()
    for which in ("tbnn", "mlp"):
        tr = new_trainer(torch, which, dev, D, want_graph)
        rec["checks"][which] = run_checks(out, "smoke", tr, want_graph)
        s_upd, s_val = time_updates(new_trainer(torch, which, dev, D, want_graph),
                                    min(2000, rows))
        rec["timing"][which] = dict(s_per_update=s_upd, s_per_val_eval=s_val,
                                    projected_full_epoch_s=N_TRAIN_REGISTERED * s_upd)
        print(f"[smoke] {which}: {s_upd*1e3:.3f} ms/update -> full epoch would be "
              f"{N_TRAIN_REGISTERED * s_upd:.0f} s on this device", flush=True)
        tr = new_trainer(torch, which, dev, D, want_graph)
        _, best_snap, best, _ = train_perpoint(out, "smoke_" + which, tr, epochs,
                                               lambda: False, hist_every=500)
        preds = save_test_preds(tr, best_snap, lam_n, T_n, d, out, "smoke_" + which)
        rec["train"][which] = dict(best_val=best, preds=preds)
    sec = time.time() - t0
    spend_add(out, "smoke", sec)
    write_status(out, "smoke", "DONE", seconds=round(sec, 1), **rec)


# ---------------------------------------------------------------- shutdown
def stage_shutdown(out, final_state, stages, code, want_shutdown, reason=""):
    """Runs LAST on every path. (i) COMPLETE.json + spend flush FIRST; (ii)
    only with --shutdown, only on gpu1 with a CUDA device: write the intent,
    then call `sudo shutdown -h now`, then record its return code. If the
    intent file exists and the machine is still up, the shutdown failed."""
    spend_add(out, "shutdown", 0.0)                       # flush (re-stamps the file)
    rec = dict(utc=utc(), final_state=final_state, exit_code=code, reason=reason,
               spend_total_hours=spend_hours(out), stages=stages,
               shutdown_requested=bool(want_shutdown))
    with open(os.path.join(out, "COMPLETE.json"), "w") as f:
        json.dump(rec, f, indent=1)
    print(f"[shutdown-stage] COMPLETE.json written: {final_state}", flush=True)
    if not want_shutdown:
        return
    host = socket.gethostname()
    try:
        import torch
        cuda = torch.cuda.is_available()
    except Exception:
        cuda = False
    att = dict(utc=utc(), hostname=host, cuda=cuda, allowed=None, rc=None)
    p = os.path.join(out, "shutdown_attempt.json")
    if not host.startswith(GPU_HOST_PREFIX) or not cuda:
        att["allowed"] = False
        att["refused"] = "hostname/CUDA guard: --shutdown only on gpu1 with a CUDA device"
        with open(p, "w") as f:
            json.dump(att, f, indent=1)
        print(f"[shutdown-stage] REFUSED to shut down {host} (cuda={cuda})", flush=True)
        return
    att["allowed"] = True
    att["intent"] = "sudo shutdown -h now"
    with open(p, "w") as f:                               # intent BEFORE the call
        json.dump(att, f, indent=1)
    sys.stdout.flush()
    rc = subprocess.run(["sudo", "shutdown", "-h", "now"]).returncode
    att["rc"], att["returned_utc"] = rc, utc()
    with open(p, "w") as f:
        json.dump(att, f, indent=1)
    print(f"[shutdown-stage] shutdown returned rc={rc}", flush=True)


# ---------------------------------------------------------------- main
STAGES = ["g0", "p0", "arma2_tbnn", "arma2_mlp"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.expanduser("~/r_ling_gpu/data/dataset.npz"))
    ap.add_argument("--out", default=os.path.expanduser("~/r_ling_gpu/arm2/out"))
    ap.add_argument("--frozen", action="store_true",
                    help="assert the pre-registration is signed/frozen; required "
                         "for every stage that trains (and for p0)")
    ap.add_argument("--stage", choices=STAGES + ["smoke"], default=None,
                    help="run one stage only (default: all in order)")
    ap.add_argument("--device", default=None, help="cuda|cpu (default: auto)")
    ap.add_argument("--no-graph", action="store_true", help="eager loop instead of CUDA graphs")
    ap.add_argument("--shutdown", action="store_true",
                    help="power the node off in the shutdown stage (gpu1 + CUDA only)")
    ap.add_argument("--smoke-rows", type=int, default=0,
                    help="smoke stage only: subset TRAIN/VAL to this many rows")
    ap.add_argument("--smoke-epochs", type=int, default=2)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    if args.device is None:
        try:
            import torch
            args.device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            args.device = "cpu"
    if args.frozen and args.smoke_rows:
        print("[stop] --smoke-rows cannot be combined with --frozen: a subset is not the "
              "registered run.", flush=True)
        sys.exit(1)
    if args.stage == "smoke" and not args.smoke_rows:
        print("[stop] --stage smoke requires --smoke-rows N.", flush=True)
        sys.exit(1)

    todo = [args.stage] if args.stage else STAGES
    final_state, code, reason = "DONE", 0, ""
    try:
        for stage in todo:
            st = read_status(args.out, stage)
            if st and st.get("state") == "DONE":
                print(f"[skip] {stage} already DONE", flush=True)
                continue
            if stage == "g0":
                stage_g0(args.out, args.data)
            elif stage == "smoke":
                stage_smoke(args.out, args.data, args.device, not args.no_graph,
                            args.smoke_rows, args.smoke_epochs)
            elif not args.frozen:
                print(f"[stop] stage {stage} requires --frozen: the pre-registration "
                      "is not signed; no training runs before the freeze.", flush=True)
                raise Halt("NOT_FROZEN", 1, "stage requires --frozen")
            elif stage == "p0":
                stage_p0(args.out, args.data, args.device, not args.no_graph)
            elif stage == "arma2_tbnn":
                stage_arma2(args.out, args.data, "tbnn", args.device, not args.no_graph)
            elif stage == "arma2_mlp":
                stage_arma2(args.out, args.data, "mlp", args.device, not args.no_graph)
        print("[driver] all requested stages processed.", flush=True)
    except Halt as h:
        final_state, code, reason = h.state, h.code, h.reason
        print(f"[driver] halted: {h.state} ({h.reason})", flush=True)
    except BaseException as e:                       # includes KeyboardInterrupt
        final_state, code, reason = "ERROR", 4, traceback.format_exc()
        print(reason, flush=True)
    finally:
        stages = {}
        for s in STAGES + ["smoke"]:
            st = read_status(args.out, s)
            if st:
                stages[s] = st.get("state")
        stage_shutdown(args.out, final_state, stages, code, args.shutdown, reason)
    sys.exit(code)


if __name__ == "__main__":
    main()
