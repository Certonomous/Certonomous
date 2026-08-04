# Supervisor sweep: adversarial verification of the `getRotationMatrix3d` degenerate-branch claim

**Session 2026-08-04. Independent verification agent, working under the doctrine that the claim
is wrong until it survives attack. Nothing here was taken on the lab's word: the math was
re-derived, the instruments were audited for the classic self-deception modes, and the headline
A5 number was reproduced from scratch with a driver written for this sweep — not the lab's
script.**

**The claim under attack** (as posed): IDWarp 2.6.2's `getRotationMatrix3d`
(`src/utils/vectorUtils.f90:58`) replaces a removable singularity with a constant branch that
differentiates to a hard zero at the undeformed baseline; the 4-line analytic-limit patch
(`rotation_branch/idwarp_v2.6.2_degenerate_branch_fix.patch`) collapses A1's idx6 634% sign flip
to 5.5e-04%, A5's idx8 207% flip to 3.0e-06 (relative), improves A2's rows 34–115x, with the
primal warp md5-identical.

## Verdicts

| attack | verdict |
|---|---|
| 1. Math (derivation, signs, normalization, cross-product term, guard trigger) | **CONFIRMED** |
| 2. Scripts (seed provenance, FD re-verification, run-pair purity) | **CONFIRMED** |
| 3. Independent reproduction (A5 idx8, own driver, stock and patched, primal md5) | **CONFIRMED** |
| 4. Upstream anchor (idwarp#57: 210% → 8.6e-06%) | **CONFIRMED** — both artifacts on disk |

No defect found. Two presentation caveats are recorded in §5; neither touches a number.

---

## 1. Math: the analytic limit re-derived, then checked numerically outside all lab code

**Guard trigger.** `src/utils/vectorUtils.f90:52-63` (scratch clone
`/home/ubuntu/certonomous-runs/W5-patch/idwarp`, verified at tag `v2.6.2`): `axis = v1 × v2`,
`axisMag = sqrt(|axis|² + 1e-30)`, guard `axisMag < tol = 1.4901161193847656e-08`. The call site
(`src/modules/kd_tree.F90:1639-1640` primal; `:1122`, `:1340` in the generated adjoints) passes
`v1 = tp%normals0(:,i)` (frozen reference normals), `v2 = tp%normals(:,i)` (current normals). At
an undeformed baseline the two are computed from identical coordinates, so `v1 × v2` is exactly
zero in floating point (each component is `a·b − b·a`), `axisMag = 1e-15 < tol`, and **the guard
fires at every non-corner surface node**. Confirmed by reading, not trusted. Inside the guard
`angle = 0`, `axis = x̂`, both constants — Tapenade's derivative of the branch taken is exactly
zero. FD probes at `h = 1e-4` displace the normals far outside the guard, so FD measures the true
slope while AD reports the constant's. The mechanism is as claimed.

**The limit, derived independently.** With `u1 = v1/|v1|`, `u2 = v2/|v2|`:
`sin θ [k]ₓ = [u1 × u2]ₓ` exactly (the normalization of `k` cancels `sin θ`), and
`(1 − cos θ)[k]ₓ² = O(θ²)`. So `Mi = I + [u1 × u2]ₓ + O(θ²)` and, at `u2 = u1`, the projector
term of `du2` dies against the cross product, giving

```
dMi = [w]ₓ ,  w = (v1 × dv2)/(|v1||v2|)          (forward)
v2b += (axial(mib − mibᵀ) × v1)/(|v1||v2|)       (reverse, by the cyclic triple product)
```

identical to PATCH_getRotationMatrix3d.md §2–4. The skew convention was checked against the
primal's `A` matrix (`A(2,1)=+axis(3)` etc. — the standard `[w]ₓ y = w × y`); all six patched
entries in `vectorUtils_d.f90` and the axial/cross component order in `vectorUtils_b.f90` match
the derivation, signs included. Placement was audited in both generated files: the reverse fix
sits inside the `branch .EQ. 0` block where `magv1`/`magv2` are live from the recomputed forward
sweep and `mib` has not yet been consumed; the downstream `CROSS_PRODUCT_3D_B`/`GETMAG_B` calls
receive only zeroed adjoints and cannot disturb the added term. The forward fix executes after
`mib` is assembled (zero in the guard) and re-tests `axismag < tol` with `axismag` still in scope.

**Numeric check, zero lab code.** A 250-draw NumPy check written for this sweep (random unit
`v1`, `v2 = v1`, random `mib` and direction), against Richardson central differences of the
singularity-free exact rotation `R = I + [v]ₓ + [v]ₓ²/(1+c)`:

| formula | worst relative error, 200–250 draws |
|---|---|
| reverse `(a × v1)/(|v1||v2|)` vs FD | 1.76e-08 |
| forward `[v1 × d]ₓ` vs FD (full matrix) | 6.98e-10 |

A first attempt that differenced the *shipped* primal instead left ~2.7e-3 worst-case residual —
which is not a patch error but the shipped `acos` parameterisation's conditioning at tilt ~1e-5
rad. **The lab's "second regime" (PATCH §8, run-1 failure) was thereby rediscovered
independently, by walking into it.**

**Verdict: CONFIRMED.** One boundary note for the record: the guard also fires for exactly
anti-parallel normals (`θ = π`), where the primal itself is already wrong (`Mi = I`) and the
patch formula is not the tangent; no baseline evaluation is at that point, and the patch makes
nothing worse there than the primal already is.

## 2. Scripts: the four self-deception modes, checked and closed

* **Same-seed contamination.** The real seed `w = d(OBJ)/dXv` is captured per run from the
  framework's own reverse call. Its norm is `||w|| = 5.81214119e+03` in the stock record
  (`rotation_branch/D1a_pl_real_rot_ON.txt`) and in the patched record
  (`rotation_branch/patched/A5P_pl_real_rotON.log`) — identical, as it must be: the seed is
  produced upstream of `warpDeriv` and the patch cannot reach it. Not a shared cached vector: my
  own runs (§3) recompute it from a fresh adjoint each time and land on the same norm.
* **FD not re-verified after the patch.** The FD column is bit-identical between the stock and
  patched records on every row (e.g. idx8 `7.87898342e-01` both sides), which is the correct
  invariant since the primal is untouched — and the step itself is verified: the A1 record
  carries `h = 1e-4` and `h = 1e-5` pairs (rel_err 5.5e-06 → 7.6e-07, cleanly FD-limited), and my
  own runs used two steps (§3). The one place a stored FD reference *was* wrong — A5 idx16 — the
  lab itself caught by re-measuring the reference (`W4_IDX16_IS_THE_REFERENCE.md`, L-30), in the
  direction adverse to the patch narrative's tidiness.
* **Comparing against a different mesh/decomposition.** `||Xv0|| = 5.180082220691975e+01` and
  the per-rank partition (`n=4752` × 4) are identical across stock/patched records and my runs;
  same case directory, same np, same restart state.
* **Patched run differing in more than the patch (L-31).** `git diff` of the scratch clone
  (`/home/ubuntu/certonomous-runs/W5-patch/idwarp`, at tag `v2.6.2`, upstream commit `647fd8f`)
  is **byte-identical** to the shipped patch file
  (`rotation_branch/idwarp_v2.6.2_degenerate_branch_fix.patch`) — verified with `diff` today; 2
  files, +44 lines, all comments and the fenced fix. The residual exposure — locally-compiled
  clone vs container-shipped binary — is closed by the live-branch regression
  (`rotation_branch/patched/patched_geom_*_on.log`: bit-identical `verifyWarpDeriv` output on
  `o_mesh`/`co_mesh`/`sym_mesh`/`onera_m6`) and by the primal md5 identity, re-established
  independently in §3.

Claim-trace spot checks, all to artifacts: A1 idx6 before = 634.0265% FLIPPED
(`probewarpderiv_realseed_idx4_idx6_idx7_np4_run1.log`, `FD −1.0656e-03` vs `AN +5.6907e-03`),
after = 5.541e-06 relative (`rotation_branch/patched/A1P_realseed.log`). A2 rows from
`/home/ubuntu/certonomous-runs/W4-a2-provenance/a2_ao_{stock,patched}_checktotals.log`:
CD/shape 1.713791e-02 → 5.059114e-04 (**33.9x**), CL/shape 1.165163e-02 → 2.189473e-04
(**53.2x**), CL/twist 1.120617e-02 → 9.737824e-05 (**115.1x**) — the claimed 34–115x, parsed
from the raw logs today.

**Verdict: CONFIRMED.**

## 3. Independent reproduction: A5 idx8, my own driver, from scratch

Driver written for this sweep: `rotation_branch/supervisor_sweep/supervisor_verify_idx8.py`,
runner `run_one.sh`, on a fresh copy of the UBend case, np=4, in
`dafoam/opt-packages:latest`. Three deliberate instrument differences from the lab's script: the
seed is captured by wrapping `idwarp.USMesh.warpDeriv` itself (the function under test) rather
than the lab's `DAFoamWarper.compute_jacvec_product` hook; the perturbation direction
`eta = dXs/dShape_8` comes from central FD of `DVGeo.update` at two steps (FFD linearity
1.2e-11), not `totalSensitivityProd` (cross-checked to 1.2e-11); and the warp FD is evaluated at
two steps inside each run.

| | stock (`supervisor_sweep/stock_idx8.log`) | patched (`supervisor_sweep/patched_idx8.log`) |
|---|---|---|
| idwarp imported from | container site-packages | `/patched-idwarp` (the clone) |
| `OBJ` at baseline | 5.234521633934580e+01 | 5.234521633934580e+01 |
| `‖w‖` (fresh adjoint each run) | 5.81214119e+03 | 5.81214119e+03 |
| FD, h=1e-4 | **7.8789841553e-01** | **7.8789841553e-01** (bit-identical) |
| FD, h=3e-4 | 7.8790063547e-01 | 7.8790063547e-01 |
| AN (`warpDeriv` contracted with eta) | **−8.4337258081e-01** | **+7.8790074124e-01** |
| framework `dOBJ/dDV[8]` | −8.4337257993e-01 | +7.8790074184e-01 |
| rel. error, sign | **2.070408 (207.04%), FLIP** | **2.95e-06, agree** |

The claim said 207% → 3.0e-06; measured 207.04% → 2.95e-06, with the patched AN sitting between
the two FD steps (truncation ~3e-6 at h=1e-4), i.e. the residual is the FD's, not the patch's.

**Primal invariance, re-established:** per-rank md5 of the baseline warped grid
(4×4752 coordinates) — `76be8dff…`, `560c5a76…`, `47e92065…`, `bb88d63e…` — **identical between
the stock and patched runs**, as is `‖Xv0‖` to 16 digits. The patch touches derivative code
only.

**Verdict: CONFIRMED.**

## 4. Upstream anchor: idwarp#57 traces to disk

`rotation_branch/issue57_rot_on.txt` (stock): DOF 0 `AD 2.87055669475` vs `FD −115.875789153`,
`Err 210.1607921%`; DOF 3 `212.6182649%`. `rotation_branch/patched/patched_issue57_rot_on.log`:
DOF 0 `AD −115.875779229`, `Err 0.8563971860E-05 %`; DOF 3 `0.3350068772E-04 %`. FD identical to
every printed digit between the two; in-plane DOFs 1/2/4/5 untouched. The prepared report's
210% → 8.6e-06% is a straight read of those artifacts, and the AD moved to the pre-existing FD —
the direction a comparison-rigging artifact cannot produce.

**Verdict: CONFIRMED.**

## 5. Caveats — presentation, not substance

1. **The one-line claim mixes units.** A1's "634% → 5.5e-04%" is percent on both sides; A5's
   "207% → 3.0e-06" switches to a fraction on the right (= 3.0e-04%). The underlying records are
   unambiguous; any external filing should state one unit.
2. **"Improves A2 rows 34–115x" is true of the three improved rows and silently passes over the
   fourth:** CD/twist *degrades* 0.389% → 0.505% (both deep in PASS). W5_GRADIENT_REGRADE.md §3a
   reports it as the counter-instance it is; a one-line summary quoting only 34–115x should carry
   the same footnote.

## 6. What this sweep did not re-run

The A2 aero-only pair (472 core-min) and the full A1/A5 `check_totals` tables were traced to
their raw logs and re-parsed, not re-executed; §3's from-scratch reproduction plus the
bit-identity audits are this sweep's independent evidence. The A4/idx16/decomposition threads
(L-30, L-31, PROOF §25) were read for consistency with the claim and do not contradict it —
they are the lab's own record of the two places the tidy version of this story would have been
wrong.

**Bottom line: the claim survives. Math, instruments, headline number, and upstream anchor all
verified, the headline independently reproduced to 2.95e-06 with the sign flip gone and the
primal bit-identical.**
