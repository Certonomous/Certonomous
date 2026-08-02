"""Pope (1975) integrity basis, transcribed from the paper and checked.

Source, READ IN FULL this session:
  S. B. Pope, "A more general effective-viscosity hypothesis",
  J. Fluid Mech. 72 (2), 331-340, 1975.
  Held at docs/papers/pope_jfm1975_effective_viscosity_hypothesis.pdf
  (text extraction alongside; the ten tensors and the Sec. 5 limit case were
  read off the PDF page images, p. 334 and p. 336, because the OCR mangles
  the fractions).

Zero compute: no solver, no mesh, no data. Pure algebra on synthetic velocity
gradients. Nothing here is fitted to anything, so the in-sample question of
LITERATURE_CHARTER section 7 does not arise -- there is no training set.

What this file is for. Two approved reproduction rungs (the tensor-basis
network and the sparse-regression closure) both rest on this basis, and the
lab had read neither it nor a substitute. This script is the substitute for
trusting the methods papers' restatement of it: it transcribes Pope's own
equations and checks every property the methods papers assume.

Pope's definitions, his numbering:
  (3.1)  a_ij   = <u_i u_j> / k - (2/3) delta_ij
  (3.2)  s_ij   = (1/2)(k/eps)(U_i,j + U_j,i)
  (3.3)  omega_ij = (1/2)(k/eps)(U_i,j - U_j,i)
  (3.6)  a = sum_lambda G^lambda T^lambda
         (0 <= lambda <= 2 in two dimensions; 1 <= lambda <= 10 in three)
  (3.7)  <u_i u_j> = (2/3) k delta_ij + k sum_lambda G^lambda T^lambda_ij

Run: python3 sdk/scripts/pope_1975_basis_check.py
Exit 0 iff every check passes.
"""
from __future__ import annotations

import numpy as np

TOL = 1e-12
I3 = np.eye(3)
I2 = np.diag([1.0, 1.0, 0.0])          # Pope's I_2, the 2-D Kronecker delta
tr = np.trace


def s_omega(grad_u: np.ndarray, tau: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """Pope (3.2) and (3.3). ``grad_u[i, j]`` is U_i,j = dU_i/dx_j; tau = k/eps."""
    return 0.5 * tau * (grad_u + grad_u.T), 0.5 * tau * (grad_u - grad_u.T)


def basis_3d(s: np.ndarray, w: np.ndarray) -> list[np.ndarray]:
    """T^1 .. T^10, transcribed from Pope p. 334 (general three-dimensional case).

    Returned 0-indexed: ``basis_3d(s, w)[0]`` is Pope's T^1.
    """
    s2, s3 = s @ s, s @ s @ s
    w2 = w @ w
    return [
        s,                                                        # T1
        s @ w - w @ s,                                            # T2
        s2 - I3 * tr(s2) / 3.0,                                   # T3
        w2 - I3 * tr(w2) / 3.0,                                   # T4
        w @ s2 - s2 @ w,                                          # T5
        w2 @ s + s @ w2 - (2.0 / 3.0) * I3 * tr(s @ w2),          # T6
        w @ s @ w2 - w2 @ s @ w,                                  # T7
        s @ w @ s2 - s2 @ w @ s,                                  # T8
        w2 @ s2 + s2 @ w2 - (2.0 / 3.0) * I3 * tr(s2 @ w2),       # T9
        w @ s2 @ w2 - w2 @ s2 @ w,                                # T10
    ]


def invariants_3d(s: np.ndarray, w: np.ndarray) -> list[float]:
    """Pope p. 334-335: {s^2}, {omega^2}, {s^3}, {omega^2 s}, {omega^2 s^2}."""
    s2, w2 = s @ s, w @ w
    return [tr(s2), tr(w2), tr(s @ s2), tr(w2 @ s), tr(w2 @ s2)]


def basis_2d(s: np.ndarray, w: np.ndarray) -> list[np.ndarray]:
    """T^0, T^1, T^2, transcribed from Pope p. 334 (two-dimensional flows).

    T^0 = (1/3) I_3 - (1/2) I_2,  T^1 = s,  T^2 = s omega - omega s.
    """
    return [I3 / 3.0 - I2 / 2.0, s, s @ w - w @ s]


# --------------------------------------------------------------------------
# velocity-gradient fields used below. Incompressible: trace(grad_u) = 0.

def random_grad_3d(rng: np.random.Generator) -> np.ndarray:
    g = rng.normal(size=(3, 3))
    return g - I3 * tr(g) / 3.0


def random_grad_2d(rng: np.random.Generator) -> np.ndarray:
    """A flow with no x3 velocity and no x3 variation, per Pope's Sec. 3."""
    g = np.zeros((3, 3))
    g[:2, :2] = rng.normal(size=(2, 2))
    g[1, 1] = -g[0, 0]                  # incompressible within the plane
    return g


def simple_shear(gamma: float) -> np.ndarray:
    """Pope's Sec. 5 flow: U_1 the only non-zero velocity, x_2 the only
    direction of variation. Also the exact shape of a fully developed
    unidirectional duct or channel baseline."""
    g = np.zeros((3, 3))
    g[0, 1] = gamma
    return g


# --------------------------------------------------------------------------
CHECKS: list[tuple[str, str]] = []


def record(name: str, ok: bool, detail: str) -> None:
    CHECKS.append((name, ok, detail))


def main() -> int:
    rng = np.random.default_rng(19750001)

    # ---- 1. transcription: every T is symmetric and traceless -------------
    # Relative, because T7..T10 are quartic and sextic in the gradient: their
    # absolute magnitude runs to 1e4 here and machine epsilon rides with it.
    worst_sym = worst_tr = 0.0
    for _ in range(200):
        s, w = s_omega(random_grad_3d(rng), tau=rng.uniform(0.2, 5.0))
        for t in basis_3d(s, w):
            scale = max(np.abs(t).max(), 1e-30)
            worst_sym = max(worst_sym, np.abs(t - t.T).max() / scale)
            worst_tr = max(worst_tr, abs(tr(t)) / scale)
    record("T1..T10 symmetric", worst_sym < 1e-13,
           f"max |T - T^T| / max|T| = {worst_sym:.3e}")
    record("T1..T10 traceless", worst_tr < 1e-13,
           f"max |tr T| / max|T| = {worst_tr:.3e}")

    # The isotropic subtractions carry the tracelessness, and the 1/3 in T3,T4
    # is not the 2/3 in T6,T9. Show the check has teeth: use 1/3 in T6 and it
    # breaks by a finite amount.
    s, w = s_omega(random_grad_3d(rng), tau=1.7)
    w2 = w @ w
    t6_wrong = w2 @ s + s @ w2 - (1.0 / 3.0) * I3 * tr(s @ w2)
    record("the 2/3 in T6 is load-bearing", abs(tr(t6_wrong)) > 1e-6,
           f"T6 with 1/3 instead of 2/3 has tr = {tr(t6_wrong):.3e}, not 0")

    # ---- 2. pointwise rank: complete, and over-determined ------------------
    # A symmetric traceless 3x3 tensor has five independent components, so ten
    # tensors evaluated at one point cannot be ten independent directions.
    def rank_of(tensors: list[np.ndarray]) -> int:
        m = np.array([t.ravel() for t in tensors])
        return int(np.linalg.matrix_rank(m, tol=1e-10))

    ranks3 = {rank_of(basis_3d(*s_omega(random_grad_3d(rng), rng.uniform(0.3, 3.0))))
              for _ in range(200)}
    record("3-D pointwise rank of {T1..T10} is 5", ranks3 == {5},
           f"ranks observed over 200 random gradients: {sorted(ranks3)}; "
           "five is the dimension of the symmetric traceless tensors, so the "
           "basis is complete pointwise and the ten G^lambda are not "
           "identifiable from one point")

    ranks2 = {rank_of(basis_3d(*s_omega(random_grad_2d(rng), rng.uniform(0.3, 3.0))))
              for _ in range(200)}
    record("2-D pointwise rank of {T1..T10} is 3", ranks2 == {3},
           f"ranks observed: {sorted(ranks2)}; matches Pope's count of three "
           "linearly independent two-dimensional tensors")

    ranks2b = {rank_of(basis_2d(*s_omega(random_grad_2d(rng), rng.uniform(0.3, 3.0))))
               for _ in range(200)}
    record("2-D {T0,T1,T2} rank is 3", ranks2b == {3},
           f"ranks observed: {sorted(ranks2b)}")

    # ---- 3. the exact 2-D reduction table ----------------------------------
    # Pope states there are three independent tensors in two dimensions but
    # does not print how the ten collapse onto them. Every one of the ten is a
    # scalar multiple of T0, T1 or T2, and two of them are identically zero.
    # Derived here and checked to machine precision, so a ten-output pipeline
    # run on a 2-D case can be told exactly what it is fitting.
    worst = {}
    for _ in range(300):
        s, w = s_omega(random_grad_2d(rng), tau=rng.uniform(0.3, 3.0))
        t = basis_3d(s, w)
        t0, t1, t2 = basis_2d(s, w)
        l1, l2 = tr(s @ s), tr(w @ w)
        residuals = {
            "T3  = -{s^2} T0":            t[2] + l1 * t0,
            "T4  = -{w^2} T0":            t[3] + l2 * t0,
            "T5  = 0":                    t[4],
            "T6  =  {w^2} T1":            t[5] - l2 * t1,
            "T7  = -{w^2} T2 / 2":        t[6] + 0.5 * l2 * t2,
            "T8  =  {s^2} T2 / 2":        t[7] - 0.5 * l1 * t2,
            "T9  = -{s^2}{w^2} T0":       t[8] + l1 * l2 * t0,
            "T10 = 0":                    t[9],
        }
        scale = max(max(np.abs(x).max() for x in t), 1e-30)
        for key, val in residuals.items():
            worst[key] = max(worst.get(key, 0.0), np.abs(val).max() / scale)
    record("2-D reduction table exact", max(worst.values()) < 1e-13,
           "; ".join(f"{k} ({v:.1e})" for k, v in worst.items()))

    # The consequence, which is the reason the table is worth having.
    record("g5 and g10 are unconstrained on any 2-D flow",
           worst["T5  = 0"] < 1e-13 and worst["T10 = 0"] < 1e-13,
           "T5 and T10 are identically zero in two dimensions, so a "
           "ten-coefficient model trained only on 2-D flows never sees a "
           "gradient for g5 or g10, and the remaining eight enter only "
           "through three identifiable combinations: "
           "G0 = -{s^2}g3 - {w^2}g4 - {s^2}{w^2}g9, G1 = g1 + {w^2}g6, "
           "G2 = g2 - {w^2}g7/2 + {s^2}g8/2")

    # ---- 4. Pope's own Sec. 5 limit case, reproduced from the transcription -
    # p. 336: a11 = -G0/6 - (1/2) G2 [(k/eps) U_1,2]^2
    #         a22 = -G0/6 + (1/2) G2 [(k/eps) U_1,2]^2
    #         a33 =  G0/3
    #         a12 = (1/2) G1 (k/eps) U_1,2 ,  a13 = a23 = 0
    worst = 0.0
    for _ in range(200):
        gamma, tau = rng.uniform(-3, 3), rng.uniform(0.2, 4.0)
        g0, g1, g2 = rng.normal(size=3)
        s, w = s_omega(simple_shear(gamma), tau=tau)
        a = g0 * basis_2d(s, w)[0] + g1 * basis_2d(s, w)[1] + g2 * basis_2d(s, w)[2]
        tg = tau * gamma
        printed = np.array([
            [-g0 / 6.0 - 0.5 * g2 * tg ** 2, 0.5 * g1 * tg, 0.0],
            [0.5 * g1 * tg, -g0 / 6.0 + 0.5 * g2 * tg ** 2, 0.0],
            [0.0, 0.0, g0 / 3.0]])
        worst = max(worst, np.abs(a - printed).max())
    record("Sec. 5 limit case reproduced", worst < TOL,
           f"max component difference against the expressions printed on "
           f"p. 336 = {worst:.3e}, over 200 random (G0, G1, G2, k/eps, U_1,2)")

    # G1 moves only the shear, G0 and G2 only the normals -- Pope's reading of
    # the same five lines, and the reason an isotropic-viscosity hypothesis
    # (G0 = G2 = 0) cannot make the normal stresses differ.
    s, w = s_omega(simple_shear(1.3), tau=0.8)
    b2 = basis_2d(s, w)
    record("G1 does not touch the normal stresses",
           abs(b2[1][0, 0]) < TOL and abs(b2[1][1, 1]) < TOL and abs(b2[1][2, 2]) < TOL,
           f"diag(T1) = {np.diag(b2[1])}")
    record("G0 and G2 do not touch the shear stress",
           abs(b2[0][0, 1]) < TOL and abs(b2[2][0, 1]) < TOL,
           f"T0[0,1] = {b2[0][0, 1]:.3e}, T2[0,1] = {b2[2][0, 1]:.3e}")

    # ---- 5. the invariants of a unidirectional baseline --------------------
    # Every fully developed duct/channel RANS baseline is exactly this field.
    worst = np.zeros(4)
    for _ in range(200):
        gamma, tau = rng.uniform(-4, 4), rng.uniform(0.1, 6.0)
        s, w = s_omega(simple_shear(gamma), tau=tau)
        l1, l2, l3, l4, l5 = invariants_3d(s, w)
        scale = max(abs(l1), 1e-30)
        worst = np.maximum(worst, [abs(l2 + l1) / scale, abs(l3) / scale,
                                   abs(l4) / scale, abs(l5 + 0.5 * l1 ** 2) / max(l1 ** 2, 1e-30)])
    record("pure shear: lambda2 = -lambda1, lambda3 = lambda4 = 0, "
           "lambda5 = -lambda1^2/2", worst.max() < 1e-14,
           f"worst relative residuals {np.array2string(worst, precision=2)}; "
           "these are exact identities of a unidirectional field, not a "
           "property of any particular duct solve")

    # ---- 6. the normalisation bridge ---------------------------------------
    # Pope (3.1) a = <uu>/k - (2/3)I. Ling et al. (2016) b = <uu>/(2k) - (1/3)I.
    rs = rng.normal(size=(3, 3)); rs = rs @ rs.T          # a plausible <u_i u_j>
    k = 0.5 * tr(rs)
    a = rs / k - (2.0 / 3.0) * I3
    b = rs / (2.0 * k) - I3 / 3.0
    record("a (Pope) = 2 b (Ling)", np.abs(a - 2.0 * b).max() < 1e-12,
           f"max |a - 2b| = {np.abs(a - 2.0 * b).max():.3e}; a G^lambda fitted "
           "against b is half the G^lambda of Pope (3.6) for the same flow")

    # ---- 7. the duct baseline, where this stops being an abstraction --------
    # A linear-eddy-viscosity RANS solve on a straight duct produces exactly
    # zero secondary flow -- measured, not assumed, in
    # demo-output/website/closure_challenge_duct_anisotropy_expressivity.json
    # -- so its mean field is U = (u(y,z), 0, 0) and its velocity gradient has
    # one non-zero row. Two shear components, not one: a duct is not the
    # single-component simple shear of section 5.
    def duct_grad(rng: np.random.Generator) -> np.ndarray:
        g = np.zeros((3, 3))
        g[0, 1], g[0, 2] = rng.normal(), rng.normal()
        return g

    worst = np.zeros(4)
    ranks, dead = set(), set()
    for _ in range(500):
        s, w = s_omega(duct_grad(rng), tau=rng.uniform(0.1, 6.0))
        l1, l2, l3, l4, l5 = invariants_3d(s, w)
        sc = max(abs(l1), 1e-30)
        worst = np.maximum(worst, [abs(l2 + l1) / sc, abs(l3) / sc, abs(l4) / sc,
                                   abs(l5 + 0.5 * l1 ** 2) / max(l1 ** 2, 1e-30)])
        t = basis_3d(s, w)
        m = np.array([x.ravel() for x in t])
        ranks.add(int(np.linalg.matrix_rank(m, tol=1e-10)))
        big = max(np.abs(x).max() for x in t)
        dead.add(tuple(i + 1 for i, x in enumerate(t) if np.abs(x).max() < 1e-12 * big))

    record("duct baseline: only lambda1 is independent", worst.max() < 1e-14,
           f"worst relative residuals {np.array2string(worst, precision=2)} over 500 "
           "two-component unidirectional gradients. lambda3 and lambda4 vanish "
           "identically (already proved in this lab's duct expressivity audit); "
           "lambda2 = -lambda1 and lambda5 = -lambda1^2/2 are the same kind of "
           "identity and reduce the five invariants to ONE independent number, "
           "so the seven-feature duct set carries three, not five")

    record("duct baseline: tensor basis has pointwise rank 3", ranks == {3},
           f"ranks observed: {sorted(ranks)}; identically zero: T{sorted(dead)[0]}. "
           "The velocity gradient has one non-zero row, so it is a rotation away "
           "from plane shear and the basis degenerates exactly as it does in 2-D")

    # Which anisotropy directions can no model built on this basis reach?
    g = np.zeros((3, 3)); g[0, 1], g[0, 2] = 0.7, -1.3
    s, w = s_omega(g, tau=1.4)
    m = np.array([t.ravel() for t in basis_3d(s, w)])
    sv = np.linalg.svd(m, compute_uv=False)
    span = np.linalg.svd(m)[2][:3]
    sym_traceless = [np.diag([1., -1., 0.]) / np.sqrt(2),
                     np.diag([1., 1., -2.]) / np.sqrt(6)]
    for i, j in [(0, 1), (0, 2), (1, 2)]:
        e = np.zeros((3, 3)); e[i, j] = e[j, i] = 1 / np.sqrt(2)
        sym_traceless.append(e)
    b = np.array([e.ravel() for e in sym_traceless])
    resid = b - b @ (span.T @ span)
    null_dirs = np.linalg.svd(resid)[2][:2].reshape(2, 3, 3)
    # is one of the two unreachable directions purely cross-plane (no x row/col)?
    streamwise = [max(abs(d[0, 0]), abs(d[0, 1]), abs(d[0, 2])) / np.abs(d).max()
                  for d in null_dirs]
    record("duct baseline: a purely cross-plane anisotropy is unreachable",
           min(streamwise) < 1e-12,
           f"singular values {np.array2string(sv[:5], precision=3)} -- rank 3 with a "
           "clean gap to zero, so a 2-dimensional subspace of the symmetric traceless "
           "tensors cannot be produced by ANY values of the ten coefficients. One of "
           f"the two unreachable directions has zero streamwise row and column "
           f"(max |x-component| / max = {min(streamwise):.1e}): it is a pure y-z "
           "tensor, the component family associated with secondary flow of the "
           "second kind. The other is pure streamwise shear")

    width = max(len(n) for n, _, _ in CHECKS)
    failed = 0
    for name, ok, detail in CHECKS:
        if not ok:
            failed += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {name.ljust(width)}  {detail}")
    print(f"\n{len(CHECKS) - failed}/{len(CHECKS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
