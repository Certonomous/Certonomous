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

---

# Results (written after the runs; sections 1-7 above were committed before any code existed)

## 8. The controlled unit experiment (§5): PASS, with two instructive failures on the way

Driver: `rotation_branch/patch_unittest/test_rotderiv.f90`, compiled against the patched clone
inside the pinned image. Logs: `patch_unittest/unittest_run{1,2}.log` (the failures),
`unittest_final.log` (the pass).

| check | result |
|---|---|
| T1 hand answer (`v1=z`, `mib=e_13` → `v2b=(1,0,0)`) | **exact to machine precision** (`1.000000000000000E+00 0.0 0.0`) |
| T2 reverse vs FD of shipped primal, `v2 == v1`, 20 random draws | worst 6.6e-07 (FD-truncation-limited) |
| T2r reverse vs Richardson-FD of the independent singularity-free form | **worst 2.8e-10** |
| T3/T3r inside the guard, tilt 1e-9 rad | 7.1e-07 / 6.6e-08 (the expected O(guard width) linearisation offset) |
| T4 live branch, tilt 0.1 rad | 6.8e-07 (FD-limited; patch inert there) |
| T5 forward-mode vs reverse-mode | **worst 4.3e-15** |

The two intermediate failures are kept on the record because both were reference defects, not
patch defects, and both are the investigation's own phenomena appearing in miniature. Run 1 used
`h = 1e-6`: the FD reference then samples the shipped primal at tilt ~1e-6 rad, where the
`acos`-near-1 conditioning error is ~eps/h² ≈ 2e-4 — **the report's "second regime", showing up in
the reference itself** — measured 2.0e-3/3.9e-3. Run 2 (`h = 1e-4`) left ~7e-7 on all FD checks
including the live-branch T4, identifying it as central-difference truncation; Richardson
extrapolation of the independent reference removed it (T2r 2.8e-10).

## 9. Acceptance results: all five pass

### 9.1 Upstream's own `inflate_cube` verification (issue #57), rotations ON

`rotation_branch/patched/patched_issue57_rot_on.log` vs `rotation_branch/issue57_rot_on.txt`:

| DOF | AD before | AD after | FD (unchanged) | err before | err after |
|---|---|---|---|---|---|
| **0** | 2.87055669475 | **−115.875779229** | −115.875789153 | **210.16%** | **8.56e-06%** |
| 1 | 1.88269575176 | 1.88269575176 | 1.88269497594 | −4.12e-05% | −4.12e-05% |
| 2 | 2.61198372778 | 2.61198372778 | 2.61198227780 | −5.55e-05% | −5.55e-05% |
| **3** | 2.88621881905 | **−94.3795529610** | −94.3795845788 | **212.62%** | **3.35e-05%** |
| 4 | 1.89116899242 | 1.89116899242 | 1.89116821661 | −4.10e-05% | −4.10e-05% |
| 5 | 2.61332356901 | 2.61332356901 | 2.61332211902 | −5.55e-05% | −5.55e-05% |

The **AD moved to the already-converged FD**, not the reverse — the direction a genuine fix must
move and a comparison-zeroing artifact could not. The in-plane DOFs 1, 2, 4, 5 (the guard's
correct-zero directions) are untouched to every printed digit. `sum(dXs)` is unchanged at
`3.229531100101105e+04` (§4.2(b)'s blindness result, reconfirmed from the other side) while
`||dXs||` goes `4.572421801411781e+02 → 1.100755884774263e+03` — the rotation term is now *in*
the derivative. **The five-year-old open bug's numbers are answered by a four-line derivative
correction.**

### 9.2 A1 NACA0012, real `dCD/dXv` seed (`rotation_branch/patched/A1P_realseed.log`)

| idx | before (realseed record) | after, h=1e-4 | sign |
|---|---|---|---|
| 0 | 11.92% (`realseed_idx01_out.log`) | **1.23e-05%** | agree |
| 1 | 11.58% (`realseed_idx01_out.log`) | **1.26e-05%** | agree |
| 4 (control) | 2.65% | **1.47e-04%** | agree |
| **6 (LE combo)** | **634.0%, FLIPPED** | **5.54e-04%** | **agree** |
| 7 (TE combo) | 1.74% | **1.31e-06%** | agree |

idx6's AN was `+5.6907e-03` against FD `−1.0656e-03`; it is now `−1.065632643e-03` against FD
`−1.065638548e-03`. **Both of A1's distinct-looking defects — the sign-flipped combo mode and the
11.6–11.9% single-station residual of PROOF §21 — collapse under the same four lines**, confirming
they were one mechanism at two magnitudes.

### 9.3 A5 UBend, real seed (`rotation_branch/patched/A5P_pl_real_rotON.log`, `A5P_stock_real_rotON.log`)

Pressure-loss objective, rotations ON:

| idx | before | after | AN after / FD (unchanged) |
|---|---|---|---|
| 2 | 2.65% | 2.6e-06 | −4.06881224e-01 / −4.06880154e-01 |
| 3 | 177.8% | 3.4e-06 | 7.08625443e-01 / 7.08623060e-01 |
| **8** | **207.0% FLIP** | **3.0e-06** | 7.87900742e-01 / 7.87898342e-01 |
| 15 | 42.9% | 6e-08 | −2.42564280e+01 / −2.42564294e+01 |
| **17** | **121.6% FLIP** | **7.0e-06** | 2.91313528e+00 / 2.91315567e+00 |
| 26 | 3.02% | 2.3e-06 | −1.89917091e+00 / −1.89917527e+00 |

Stock objective: all 27 components print rel_err 0.0000 (worst residual at idx24, ~5e-06),
against a before-worst of 80.79%. The framework's own `dOBJ/dDV` column now equals the FD of the
warp — **the end-to-end gradient is fixed, not just the isolated function.**

And §4.8's honest partial result is retroactively resolved: the rigid-translation control's
unexplained 1.7%/2.8% y/z residuals — attributed to patch-junction elements tilting — are now
**3.8e-09 and 6.2e-09** with rotations ON. That attribution is thereby *proven*: the residual was
exactly the discarded junction-rotation term, and supplying the term removes it.

### 9.4 Regression control: the live branch is untouched

`repro_geometries.py`, rotations ON, patched vs unpatched: the `verifyWarpDeriv` DOF lines are
**bit-identical** (every printed digit of AD, FD, and Err) for `o_mesh`, `co_mesh`, `sym_mesh` —
worst errors 1.685e-05% / 3.856e-05% / 6.919e-06%, unchanged — **and for `onera_m6`, whose 1.258%
second-regime error is unchanged**, exactly as §6 predicted for a patch that only touches the
degenerate branch. Logs: `rotation_branch/patched/patched_geom_*_on.log`.

### 9.5 Primal invariance, strict form

`rotation_branch/patched/primal_bitcheck.log`: the full 310,284-coordinate warped grid of the
deformed `inflate_cube` case, dumped patched and unpatched: **md5-identical
(`8fafe12f848af490a5041c865112b5fb`), max|diff| = 0.0.** A5's `||Xv0||` fingerprint
(`5.180082220691975e+01`) and inflate_cube's `Sum of vCoords Warped`
(`1.784392128944467e+06`) also match every digit. The patch touches only derivative code.

## 10. What remains true after the fix

- The **second regime is real and untouched**: onera_m6's ~1.26% (§9.4) survives the patch, as
  predicted. The full upstream fix is the reparameterisation in §6, which subsumes both regimes.
- The patch is a **proof of concept on the generated file**; upstream should fix the primal's
  parameterisation and regenerate, not merge a hand-edit of Tapenade output.
- Diff: `rotation_branch/idwarp_v2.6.2_degenerate_branch_fix.patch` (2 files, +44 lines, all in
  `src/adjoint/output{Reverse,Forward}/vectorUtils_{b,d}.f90`).
