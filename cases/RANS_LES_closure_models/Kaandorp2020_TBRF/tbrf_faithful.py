#!/usr/bin/env python3
"""Tensor Basis Random Forest (Kaandorp & Dwight 2020), numpy implementation.

Each split of a Tensor Basis Decision Tree solves two regularised least-squares
problems for the 10 Pope tensor-basis coefficients g^(m):

    g = ( sum_i That_i^T That_i  +  Gamma I )^-1 ( sum_i That_i^T bhat_i )
                                                         -- their eq. (23), p. 56

and the split (feature j, threshold s) is the one minimising the total Frobenius
mismatch of both bins -- their eq. (18), p. 55.

The accumulated normal-equation blocks A_i = That_i^T That_i (10x10) and
c_i = That_i^T bhat_i (10) are additive in i, so a single sort plus a prefix sum
over the ordered samples gives every candidate split's normal equations at once.
The objective is evaluated from

    J(bin) = sum_i ||b_i||_F^2  -  ( g.c + Gamma |g|^2 ),

which follows from A g = c - Gamma g. No approximation is involved.

Forest: bagging with replacement, a random subset of features per split, and the
MEDIAN over trees of each of the 6 unique components of b (their sec. 2.5, p. 21
and appendix p. 57 -- median, not mean).
"""
from __future__ import annotations
import os, sys, json, time
import numpy as np

GAMMA_PAPER = 1e-12
BF_MAX = 2048        # exact brute force over every distinct threshold at or below
Q_CAND = 128         # quantile candidate thresholds above it
MAX_DEPTH = 30       # D7, compute-safety cap


# --------------------------------------------------------------- basis algebra
def normal_blocks(T, b, scale):
    """A_i (n,10,10) and c_i (n,10) for the scaled basis T/scale."""
    Ts = (T / scale[None, :, None, None]).reshape(T.shape[0], 10, 9)
    A = np.einsum("nmp,nqp->nmq", Ts, Ts)
    c = np.einsum("nmp,np->nm", Ts, b.reshape(b.shape[0], 9))
    return A, c


def basis_scale(T):
    """c_m = RMS of ||T^(m)||_F over the training sample (departure D8)."""
    s = np.sqrt((T.astype(np.float64) ** 2).sum(axis=(2, 3)).mean(axis=0))
    return np.maximum(s, 1e-30)


def solve_g(A, c, gamma):
    """Batched (A + Gamma I)^-1 c."""
    n = A.shape[0]
    Ar = A + gamma * np.eye(10)[None]
    try:
        return np.linalg.solve(Ar, c[..., None])[..., 0]
    except np.linalg.LinAlgError:
        out = np.empty_like(c)
        for i in range(n):
            out[i] = np.linalg.lstsq(Ar[i], c[i], rcond=None)[0]
        return out


def _score(A, c, gamma):
    g = solve_g(A, c, gamma)
    return (g * c).sum(-1) + gamma * (g * g).sum(-1), g


# ------------------------------------------------------------------- the tree
class TBDT:
    __slots__ = ("feat", "thr", "left", "right", "gleaf", "depth_hits", "n_leaf")

    def __init__(self):
        self.feat, self.thr, self.left, self.right, self.gleaf = [], [], [], [], []
        self.depth_hits = 0
        self.n_leaf = 0

    def _new(self):
        self.feat.append(-1); self.thr.append(0.0)
        self.left.append(-1); self.right.append(-1); self.gleaf.append(None)
        return len(self.feat) - 1

    def fit(self, X, A, c, rng, max_features, min_leaf, gamma, max_depth=MAX_DEPTH):
        stack = [(self._new(), np.arange(X.shape[0]), 0)]
        nfeat = X.shape[1]
        while stack:
            node, idx, depth = stack.pop()
            n = idx.size
            At = A[idx].sum(0); ct = c[idx].sum(0)
            if n < 2 * min_leaf or depth >= max_depth:
                if depth >= max_depth and n >= 2 * min_leaf:
                    self.depth_hits += 1
                self.gleaf[node] = solve_g(At[None], ct[None], gamma)[0]
                self.n_leaf += 1
                continue
            cols = (np.arange(nfeat) if max_features >= nfeat
                    else rng.choice(nfeat, max_features, replace=False))
            best = (-np.inf, -1, 0.0, None)
            for j in cols:
                xv = X[idx, j]
                o = np.argsort(xv, kind="stable")
                xs = xv[o]
                cA = np.cumsum(A[idx[o]], axis=0)
                cc = np.cumsum(c[idx[o]], axis=0)
                # valid split after position p (0-based, left = 0..p)
                lo, hi = min_leaf - 1, n - min_leaf - 1
                if hi < lo:
                    continue
                pos = np.arange(lo, hi + 1)
                pos = pos[xs[pos] < xs[pos + 1]]
                if pos.size == 0:
                    continue
                if n > BF_MAX and pos.size > Q_CAND:
                    pos = pos[np.linspace(0, pos.size - 1, Q_CAND).astype(int)]
                AL = cA[pos]; cL = cc[pos]
                AR = At[None] - AL; cR = ct[None] - cL
                sL, _ = _score(AL, cL, gamma)
                sR, _ = _score(AR, cR, gamma)
                tot = sL + sR
                m = int(np.argmax(tot))
                if tot[m] > best[0]:
                    best = (tot[m], int(j), 0.5 * (xs[pos[m]] + xs[pos[m] + 1]),
                            idx[o], pos[m])
            if best[1] < 0:
                self.gleaf[node] = solve_g(At[None], ct[None], gamma)[0]
                self.n_leaf += 1
                continue
            _, j, thr, order, m = best
            self.feat[node] = j; self.thr[node] = thr
            li = self._new(); ri = self._new()
            self.left[node] = li; self.right[node] = ri
            stack.append((li, order[:m + 1], depth + 1))
            stack.append((ri, order[m + 1:], depth + 1))
        self.feat = np.array(self.feat, np.int32)
        self.thr = np.array(self.thr, np.float64)
        self.left = np.array(self.left, np.int32)
        self.right = np.array(self.right, np.int32)
        self.gleaf = np.array([g if g is not None else np.zeros(10)
                               for g in self.gleaf], np.float64)
        return self

    def apply(self, X):
        node = np.zeros(X.shape[0], np.int32)
        for _ in range(MAX_DEPTH + 2):
            f = self.feat[node]
            live = f >= 0
            if not live.any():
                break
            i = np.nonzero(live)[0]
            go_l = X[i, f[i]] <= self.thr[node[i]]
            node[i] = np.where(go_l, self.left[node[i]], self.right[node[i]])
        return node

    def predict_g(self, X):
        return self.gleaf[self.apply(X)]


# ------------------------------------------------------------------ the forest
IDX6 = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]


def b_from_g(g, T, scale):
    """(n,10) coefficients x (n,10,3,3) basis -> (n,3,3)."""
    return np.einsum("nm,nmij->nij", g / scale[None, :], T.astype(np.float64))


def fit_tree(args):
    (seed, X, A, c, max_features, min_leaf, gamma) = args
    rng = np.random.default_rng(seed)
    bag = rng.integers(0, X.shape[0], X.shape[0])
    t = TBDT().fit(X[bag], A[bag], c[bag], rng, max_features, min_leaf, gamma)
    return t


def forest_predict(trees, Xte, Tte, scale):
    n = Xte.shape[0]
    acc = np.empty((len(trees), n, 6), np.float32)
    for ti, t in enumerate(trees):
        b = b_from_g(t.predict_g(Xte), Tte, scale)
        for s, (i, j) in enumerate(IDX6):
            acc[ti, :, s] = b[:, i, j]
    med = np.median(acc, axis=0)
    out = np.empty((n, 3, 3), np.float64)
    for s, (i, j) in enumerate(IDX6):
        out[:, i, j] = med[:, s]
        out[:, j, i] = med[:, s]
    return out
