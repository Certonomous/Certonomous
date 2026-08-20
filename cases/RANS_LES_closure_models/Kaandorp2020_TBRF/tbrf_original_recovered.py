#!/usr/bin/env python3
"""Tensor Basis Random Forest (Kaandorp & Dwight 2020) - a numpy implementation.

A tensor-basis decision tree fits, in every node, the tensor-polynomial
    b_ij = sum_{n=1..10} g^(n) T^(n)_ij
by ridge least squares, and chooses the split that minimises the sum of the two
children's residual sums of squares. Because the normal equations of that fit are
sums over the node's samples, all candidate thresholds along a feature can be
scored from one cumulative sum - which is what makes this tractable in numpy.

Prediction is the **median** over trees, component-wise, as Kaandorp & Dwight
report is better than the mean (VERIFIED-PDF: arXiv:1810.08794v2, p. 26).
"""
from __future__ import annotations
import numpy as np

NB = 10                       # basis size
IU = np.triu_indices(NB)      # 55 unique entries of the 10x10 gram


def sample_grams(T, b):
    """Per-sample gram (N,55), rhs (N,10) and b:b (N,)."""
    M = T.reshape(T.shape[0], NB, 9).astype(np.float64)
    y = b.reshape(b.shape[0], 9).astype(np.float64)
    G = np.einsum("nai,nbi->nab", M, M)[:, IU[0], IU[1]]
    c = np.einsum("nai,ni->na", M, y)
    s = (y * y).sum(1)
    return G.astype(np.float64), c, s


def _unpack(Gv):
    """(K,55) -> (K,10,10) symmetric."""
    K = Gv.shape[0]
    G = np.zeros((K, NB, NB))
    G[:, IU[0], IU[1]] = Gv
    G[:, IU[1], IU[0]] = Gv
    return G


def _fit_sse(Gv, c, s, gamma):
    """Ridge fit and residual SSE for a batch of nodes. Returns (g, sse)."""
    G = _unpack(Gv)
    tr = np.trace(G, axis1=1, axis2=2) / NB
    reg = gamma * np.maximum(tr, 1e-30)
    G = G + reg[:, None, None] * np.eye(NB)[None]
    try:
        g = np.linalg.solve(G, c[:, :, None])[:, :, 0]
    except np.linalg.LinAlgError:
        g = np.stack([np.linalg.lstsq(G[i], c[i], rcond=None)[0] for i in range(G.shape[0])])
    sse = s - 2.0 * (g * c).sum(1) + np.einsum("ka,kab,kb->k", g, _unpack(Gv), g)
    return g, sse


class TensorBasisDecisionTree:
    def __init__(self, max_depth=15, min_leaf=9, mtry=11, n_thresh=32,
                 gamma=1e-12, rng=None):
        self.max_depth, self.min_leaf, self.mtry = max_depth, min_leaf, mtry
        self.n_thresh, self.gamma = n_thresh, gamma
        self.rng = rng or np.random.default_rng(0)

    def fit(self, X, Gv, c, s):
        self.feat, self.thr, self.left, self.right, self.g = [], [], [], [], []
        stack = [(np.arange(X.shape[0]), 0)]
        node_ids = [self._new_node()]
        while stack:
            idx, depth = stack.pop()
            nid = node_ids.pop()
            Gsum = Gv[idx].sum(0)[None]; csum = c[idx].sum(0)[None]; ssum = np.array([s[idx].sum()])
            gfit, sse0 = _fit_sse(Gsum, csum, ssum, self.gamma)
            self.g[nid] = gfit[0]
            if depth >= self.max_depth or len(idx) < 2 * self.min_leaf:
                continue
            best = self._best_split(X, Gv, c, s, idx, sse0[0])
            if best is None:
                continue
            f, t, lm = best
            li, ri = idx[lm], idx[~lm]
            self.feat[nid], self.thr[nid] = f, t
            ln, rn = self._new_node(), self._new_node()
            self.left[nid], self.right[nid] = ln, rn
            stack.append((li, depth + 1)); node_ids.append(ln)
            stack.append((ri, depth + 1)); node_ids.append(rn)
        self.feat = np.array(self.feat); self.thr = np.array(self.thr)
        self.left = np.array(self.left); self.right = np.array(self.right)
        self.g = np.array(self.g)
        return self

    def _new_node(self):
        self.feat.append(-1); self.thr.append(0.0)
        self.left.append(-1); self.right.append(-1); self.g.append(np.zeros(NB))
        return len(self.feat) - 1

    def _best_split(self, X, Gv, c, s, idx, sse_parent):
        nf = X.shape[1]
        feats = self.rng.choice(nf, size=min(self.mtry, nf), replace=False)
        best = None; best_sse = sse_parent - 1e-12
        for f in feats:
            v = X[idx, f]
            order = np.argsort(v, kind="stable")
            vs = v[order]; ii = idx[order]
            qs = np.unique(np.quantile(vs, np.linspace(0.05, 0.95, self.n_thresh)))
            cut = np.searchsorted(vs, qs, side="right")
            cut = np.unique(cut[(cut >= self.min_leaf) & (cut <= len(ii) - self.min_leaf)])
            if cut.size == 0:
                continue
            cG = np.cumsum(Gv[ii], 0); cc = np.cumsum(c[ii], 0); cs = np.cumsum(s[ii])
            GL, cL, sL = cG[cut - 1], cc[cut - 1], cs[cut - 1]
            GR, cR, sR = cG[-1] - GL, cc[-1] - cL, cs[-1] - sL
            _, sseL = _fit_sse(GL, cL, sL, self.gamma)
            _, sseR = _fit_sse(GR, cR, sR, self.gamma)
            tot = sseL + sseR
            j = int(np.argmin(tot))
            if tot[j] < best_sse:
                best_sse = tot[j]
                thr = vs[cut[j] - 1]
                best = (int(f), float(thr), X[idx, f] <= thr)
        return best

    def predict_g(self, X):
        n = X.shape[0]
        node = np.zeros(n, np.int64)
        active = np.ones(n, bool)
        for _ in range(self.max_depth + 2):
            internal = active & (self.feat[node] >= 0)
            if not internal.any():
                break
            f = self.feat[node[internal]]; t = self.thr[node[internal]]
            go_left = X[np.where(internal)[0], f] <= t
            nxt = np.where(go_left, self.left[node[internal]], self.right[node[internal]])
            node[internal] = nxt
        return self.g[node]


class TensorBasisRandomForest:
    def __init__(self, n_trees=100, seed=0, **kw):
        self.n_trees, self.seed, self.kw = n_trees, seed, kw
        self.trees = []

    def fit(self, X, T, b, verbose=True, checkpoint=None):
        Gv, c, s = sample_grams(T, b)
        rng = np.random.default_rng(self.seed)
        n = X.shape[0]
        for i in range(len(self.trees), self.n_trees):
            bs = rng.integers(0, n, n)                       # bootstrap
            tr = TensorBasisDecisionTree(rng=np.random.default_rng(self.seed * 1000 + i),
                                         **self.kw)
            tr.fit(X[bs], Gv[bs], c[bs], s[bs])
            self.trees.append(tr)
            if verbose:
                print(f"  tree {i+1}/{self.n_trees} nodes={len(tr.feat)}", flush=True)
            if checkpoint:
                checkpoint(self, i + 1)
        return self

    def predict(self, X, T, chunk=50000):
        out = np.empty((X.shape[0], 3, 3), np.float32)
        for s0 in range(0, X.shape[0], chunk):
            Xc, Tc = X[s0:s0 + chunk], T[s0:s0 + chunk]
            G = np.stack([t.predict_g(Xc) for t in self.trees])   # (ntree, n, 10)
            gmed = np.median(G, axis=0)
            out[s0:s0 + chunk] = np.einsum("ng,ngij->nij", gmed, Tc.astype(np.float64))
        return out
