# Patch record: the corrected derivative for `getRotationMatrix3d`'s degenerate branch

**Session 2026-07-31, well W5. Derivation written BEFORE the code, per L-26 (the lab has been
burned by sign conventions twice; every sign below is checked by a controlled experiment with a
hand-computed known answer before any system-level run).**

**Nothing in this document has been filed or sent anywhere.** The patch lives in a fresh scratch
clone (`/home/ubuntu/certonomous-runs/W5-patch/idwarp`); no installed package is modified in place.

---

## 1. What is being differentiated

`getRotationMatrix3d(v1, v2, Mi)` (`src/utils/vectorUtils.f90:31-103`, IDWarp v2.6.2) builds the
rotation carrying direction `v1` (the frozen reference normal `n0`) onto direction `v2` (the
current normal `n`):

```
k = (v1 x v2)/|v1 x v2| ,   theta = acos( v1.v2 / (|v1||v2|) )
Mi = I + sin(theta) [k]_x + (1 - cos(theta)) [k]_x^2          (Rodrigues)
```

with the code's skew convention, verified against the source (`A(2,1)=+axis(3)`, `A(3,2)=+axis(1)`,
`A(1,3)=+axis(2)`), being the **standard** one: `([w]_x) y = w x y`, i.e.

```
        [  0   -w3   w2 ]
[w]_x = [  w3   0   -w1 ]
        [ -w2   w1   0  ]
```

Tapenade activity (from the generated header of `GETROTATIONMATRIX3D_B`): *"gradient of useful
results: v2 mi / with respect to varying inputs: v2"* — `v1` is inactive (it is `normals0`, frozen),
so the only derivative owed by the degenerate branch is `dMi/dv2`.

`getMag` regularises with `+1e-30` under the square root; for unit-magnitude normals this shifts
`|v|` by ~5e-31 and is irrelevant to everything below.

## 2. The forward derivative at the degenerate point

Let `u1 = v1/|v1|`, `u2 = v2/|v2|`. Three observations:

**(a) The sin term is exactly a cross product of unit vectors.** `|u1 x u2| = sin(theta)` and
`k = (u1 x u2)/|u1 x u2|`, so

```
sin(theta) [k]_x = [u1 x u2]_x        — exactly, for all theta in [0, pi)
```

**(b) The cos term is second order.** `1 - cos(theta) = theta^2/2 + O(theta^4)` and `[k]_x^2` is
bounded (`k` is unit), so `(1-cos(theta))[k]_x^2 = O(theta^2)`: it contributes nothing to a first
derivative evaluated at `theta = 0`.

**(c) Therefore, near `u2 = u1`:**

```
Mi = I + [u1 x u2]_x + O(theta^2)
```

Differentiate at `u2 = u1` (i.e. `v2 = v1`, the guarded branch's evaluation point):

```
dMi = [ u1 x du2 ]_x
du2 = (I - u2 u2^T) dv2 / |v2|
```

The projector's second piece dies: `u1 x (u2 (u2 . dv2)) = (u1 x u2)(u2 . dv2) = 0` at `u2 = u1`.
Hence

```
  dMi = [ w ]_x ,      w = (v1 x dv2) / (|v1| |v2|)          ...(F)
```

finite and non-zero — the removable singularity removed by hand. This is the term the shipped
branch replaces with exactly zero.

## 3. The reverse-mode (adjoint) contribution

Given the incoming adjoint `mib` of `Mi`, the branch owes `v2b += (dJ/dv2)` where
`dJ = sum_{ik} mib_ik dMi_ik`. Substituting (F) and reading off the six nonzero entries of `[w]_x`
in the convention of §1:

```
dJ = w1 (mib(3,2) - mib(2,3)) + w2 (mib(1,3) - mib(3,1)) + w3 (mib(2,1) - mib(1,2))
   = a . w ,   with  a = axial(mib - mib^T):
       a1 = mib(3,2) - mib(2,3)
       a2 = mib(1,3) - mib(3,1)
       a3 = mib(2,1) - mib(1,2)
```

With `w = (v1 x dv2)/(|v1||v2|)`, the cyclic triple-product identity
`a . (v1 x dv2) = dv2 . (a x v1)` gives

```
  v2b += (a x v1) / (|v1| |v2|)                               ...(R)
```

`|v1| = magv1` and `|v2| = magv2` are already recomputed in the forward sweep at the top of
`GETROTATIONMATRIX3D_B` and are in scope inside the branch. **The whole fix is (R): four lines of
assignments in the `branch .EQ. 0` block of `vectorUtils_b.f90`, replacing nothing — the three
zeroed intermediates (`magv2b`, `axisb`, `axismagb`) stay zeroed, because the dummy-axis path they
belong to really does carry zero; (R) adds the term that path lost.**

## 4. The forward-mode (tangent) contribution, for `warpDerivFwd`

`GETROTATIONMATRIX3D_D` (`outputForward/vectorUtils_d.f90`) has the dual defect: the degenerate
branch sets `axisb = 0, angleb = 0`, making the output tangent `mib` exactly zero. The corrected
tangent is (F) directly, with `dv2` = the incoming tangent `v2b` (Tapenade's unfortunate name for
`v2d`):

```
  w = (v1 x v2d) / (magv1 magv2)
  mid += [w]_x     (six entries: mid(1,2)-=w3, mid(2,1)+=w3, mid(1,3)+=w2,
                    mid(3,1)-=w2, mid(2,3)-=w1, mid(3,2)+=w1)
```

This is patched for completeness and verified at unit level; the system-level acceptance tests
exercise the reverse path, which is the one DAFoam's adjoint calls.

## 5. The controlled experiment with a known answer (run before any system test)

Standalone Fortran driver, no IDWarp infrastructure: compile `vectorUtils.f90` (primal) +
patched `vectorUtils_b.f90` + a `main`.

**Hand-computed case.** `v1 = v2 = (0,0,1)`, `mib` = all zeros except `mib(1,3) = 1`
(J = Mi(1,3)). Prediction of (R): `a = (0, 1, 0)`, `v2b = a x v1 = (1, 0, 0)`.

Independent hand check by explicit geometry, not by the formula: tilt `v2 = (eps, 0, 1)`. Axis
`= v1 x v2 = (0*1-1*0, 1*eps-0*1, 0) = (0, eps, 0)` — the +y axis; angle `= eps` to first order.
`Mi = I + eps [y]_x`, and `[y]_x` has `(1,3)` entry `+1`, so `Mi(1,3) = eps = v2_1`:
`dJ/dv2 = (1, 0, 0)`. Tilt `v2 = (0, eps, 1)` instead: axis `= (-eps, 0, 0)`, `[-x]_x` has
`(1,3)` entry `0`, so `dJ/dv2_2 = 0`. Radial: `0`. **The two routes agree: `v2b = (1,0,0)`.**
The driver must reproduce this to machine precision, and any sign error in (R) flips its x
component to `-1` — the experiment is sensitive to exactly the failure mode L-26 warns about.

**Generic case.** 20 random draws: random unit `v1`, `v2 = v1`, random `mib`, random direction
`d`. Check `v2b . d` against the central difference `[J(v2 + h d) - J(v2 - h d)]/(2h)`,
`J(v2) = sum(mib * Mi(v1, v2))` computed by the *unpatched primal* — the same primal the warp
uses. Expected agreement ~1e-8 relative (FD-limited). The same driver checks the patched
forward-mode `GETROTATIONMATRIX3D_D` against the same FD, and reverse-vs-forward consistency
`v2b . d = sum(mib * mid(d))`.

**Adversarial guard within the driver.** Also evaluate at a *non*-degenerate point
(`v2` rotated 0.1 rad from `v1`): the patched code must return **bit-identical** results to the
unpatched code there, proving the patch touches only the degenerate branch.

## 6. What the patch deliberately does not do

- **It does not touch the primal.** `vectorUtils.f90` is unchanged; `warpMesh` results must be
  bit-identical before/after (acceptance test 5).
- **It does not fix §1.6's second regime** (the ill-conditioned `acos` just above the threshold,
  ~1% errors on ONERA M6). The right upstream fix for both regimes is the reparameterisation
  `R = I + [v]_x + [v]_x^2/(1+c)`, `v = a x b`, `c = a.b` — that changes the primal's floating-point
  path, so a proof-of-concept that must leave the primal bit-identical cannot use it. Recorded as
  the recommended upstream fix, not implemented here.
- **It does not regenerate with Tapenade.** The generated file is hand-edited with a clearly
  fenced, commented block. Upstream would regenerate after fixing the primal's parameterisation;
  for a proof of the root cause, the hand fix is the sharper instrument (nothing else in the
  generated code moves).

## 7. Acceptance tests (stated before the runs)

| # | test | pass criterion |
|---|---|---|
| 1 | upstream `inflate_cube` verification (issue #57), rotations ON | DOFs 0,3 drop from 210%/213% to the ~1e-5% level of DOFs 1,2,4,5 |
| 2 | A1 NACA0012, real `dCD/dXv` seed, idx6/idx7 (108-149% flipped) | collapse to the level of the clean controls |
| 3 | A5 UBend, pressure-loss real seed, idx8 207% / idx17 122% (flipped) | collapse; all 27 stock-objective components likewise |
| 4 | regression control: `o_mesh`/`co_mesh`/`sym_mesh` shear (guard dead, live branch) | stay at their unpatched values — the patch must not perturb the live branch |
| 5 | primal invariance: warped `Xv` (and `Sum of vCoords Warped`) patched vs unpatched | bit-identical |

Test 4 and the §5 non-degenerate bit-identity check are the adversarial half: a patch that
"fixed" things by zeroing or smearing the comparison would fail them.
