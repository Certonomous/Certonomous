# T9a-D results: the 2.41 mK interface miss is the interface scheme

Campaign T, tier 4, rung T9a, **diagnosis arm D**, attempt 1. Written
2026-08-22 from a solve completed 2026-08-22 18:02:05.895 Z. Cases in
`verification/runs/T-family/T9a_runs/`, eight of them
(`D_A_c D_A_m D_A_f D_B_x D_C_c D_C_m D_C_f D_R_f`). Pre-registration
`docs/campaigns/T-family/T9aD_PREREGISTRATION.md`, written before any `D_*`
case existed; comparator `analyse_t9aD.py`, written and hashed before any
`D_*` case existed (freeze condition checked, §5). Sanaa's directive H-4.

> **Arm verdict: DIAGNOSIS COMPLETE — the interface scheme explains the whole
> of T9a's R1 miss. 3 PASS, 1 GATE FAIL, 3 NOT A RESULT of 7 registered rows,
> every one of them as this arm's own pre-registered arithmetic predicted,
> including the two rows where that arithmetic contradicted the directive.**
>
> **A1 PASS:** replacing `Gauss linear` with `Gauss harmonic` on
> `laplacian(DT,T)` drops the R1 level error from **−5.43 / −3.34 / −2.41 mK**
> to **0 / −3.2e-09 / −3.0e-09 mK** — a factor **8.2e+08** at the finest level
> against a registered threshold of 3 — and drops the R0 flux excess from
> **+1.806 % to +0.0000000 %**. Every harmonic level reproduces the closed form
> to all nine printed digits, **on the 35-cell coarse mesh included.**
> **A2 NOT A RESULT** (predicted): the error collapses below the registered
> 1 µK floor, so no order can be read from it.
> **B0 and B2 NOT A RESULT** (predicted): the m/f/**x** triple is **STAGNANT,
> `p` = 0.130**, and no band may be armed on it.
> **B1 PASS:** the level errors keep shrinking at first order across four
> levels (−3.335 / −2.409 / −1.538 mK, ratios 1.384 / 1.566).
> **C1 GATE FAIL, and in the opposite direction to the directive:** reducing
> the contrast 400× → 40× made the R1 error **grow by 27–31×**, to
> −168.06 / −104.16 / −64.99 mK.
> **C2 PASS:** the 40× error is still first order (ratios 1.614 / 1.603).
>
> **This arm grades nothing against the T9a band. T9a's verdict — GATE FAIL on
> R1 — is untouched, and no T9a case was re-solved.**

Cost **6.60 core-seconds, 9.41e-05 USD** (§9), against a registered ceiling of
1.2 core-seconds — **the ceiling was low; §9 says by how much and why.**

---

## 1. The rows

Every verdict is against a threshold registered in `T9aD_registered.json`
before any `D_*` case existed. **None is against the T9a band.** `e1` is
`T_i1(measured) − T_i1(exact)`, in millikelvin; the driving potential
`T_hot − T_cold` = 50 K is identical in every case here, so millikelvin is a
scale-free comparison across all three arms.

| row | hypothesis | registered claim | measured | threshold | verdict |
| --- | --- | --- | ---: | --- | --- |
| **A1** | H-A scheme | `\|e1\|` drops > 3× at every level under harmonic | drop **∞ / 1.05e+09 / 8.15e+08** | `min > 3.0` | **PASS** |
| **A2** | H-A scheme | the error becomes ~second order, ratios ≈ 2.56 | `\|e1\|` = 0 / 3.18e-09 / 2.96e-09 mK | `[2.0, 3.3]`, void below the 0.001 mK floor | **NOT A RESULT** (floor fired) |
| **B0** | H-B mesh | the m/f/x triple reads `p` ≈ 1 | **STAGNANT, `p` = 0.1305** | CONVERGING and `p ∈ [0.7, 1.4]` | **NOT A RESULT** |
| **B1** | H-B mesh | the level errors keep shrinking at ~first order | ratios **1.384, 1.566** | `[1.25, 2.05]` | **PASS** |
| **B2** | H-B mesh | the band on level x still fails to cover the error | no band may be armed | band `<` `\|e1_x\|` | **NOT A RESULT** |
| **C1** | H-C jump | `\|e1\|` shrinks ≈ 10× when the contrast drops 10× | **0.0323 / 0.0320 / 0.0371** — it **grew** 27–31× | all in `[3, 30]` | **GATE FAIL** |
| **C2** | H-C jump | the 40× error is still first order | ratios **1.614, 1.603** | `[1.25, 2.05]` | **PASS** |

**3 PASS, 1 GATE FAIL, 3 NOT A RESULT.** The triple-state rule fired twice
(B0, B2) and the registered collapse floor once (A2); **all three were
predicted in the pre-registration, before the solve.**

### 1.1 What each case measured

`q″` and `T_i2` carry no verdict and are reported as context. Every geometric
constant is read from `constant/polyMesh/points` by the **frozen**
`analyse_t9a.measure_wall`; the `laplacian(DT,T)` entry is **read back off
disk** from each case's own `system/fvSchemes` and refused if it is not the
registered one.

| case | cells | `laplacian(DT,T)` | `k₂` | `q″` [W/m²] | vs exact | `T_i1` [K] | `e1` [mK] | `e2` [mK] | closure |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `D_A_c` | 35 | `Gauss harmonic corrected` | 0.04 | 19.502681619 | **+0.0000000 %** | 348.781082399 | **+0.0000000** | +0.0000000 | 1.9e-11 |
| `D_A_m` | 56 | `Gauss harmonic corrected` | 0.04 | 19.502681619 | **+0.0000000 %** | 348.781082399 | **−0.0000032** | +0.0000000 | 6.0e-12 |
| `D_A_f` | 90 | `Gauss harmonic corrected` | 0.04 | 19.502681619 | **+0.0000000 %** | 348.781082399 | **−0.0000030** | +0.0000000 | 4.4e-11 |
| `D_B_x` | **145** | `Gauss linear corrected` | 0.04 | 19.720387602 | +1.11629 % | 348.779544025 | **−1.53837** | −0.31015 | 1.7e-10 |
| `D_C_c` | 35 | `Gauss linear corrected` | **0.4** | 162.956868353 | +2.25543 % | 339.871777974 | **−168.06266** | −14.29084 | 3.4e-12 |
| `D_C_m` | 56 | `Gauss linear corrected` | **0.4** | 161.590158051 | +1.39782 % | 339.935682430 | **−104.15821** | −8.85687 | 7.8e-12 |
| `D_C_f` | 90 | `Gauss linear corrected` | **0.4** | 160.763668218 | +0.87920 % | 339.974846560 | **−64.99408** | −5.38568 | 3.2e-12 |
| `D_R_f` | 90 | `Gauss linear corrected` | 0.04 | 19.854990714 | +1.80646 % | 348.778673215 | −2.40918 | −0.50661 | 1.1e-10 |

Exact references, both re-derived at analysis time by the **frozen**
`exact_t9a.py` along two independent routes that must agree or the comparator
refuses: at 400×, `q″` 19.502681619, `T_i1` 348.781082399, `T_i2`
300.024378352; at 40×, `ΣR` 0.31375, `q″` 159.362549801, `T_i1` 340.039840637,
`T_i2` 300.199203187.

**The T9a baseline was READ, not re-solved.** `W_c`/`W_m`/`W_f` `T_i1` come
from `gate_t9a.json` on disk since 2026-08-20: 348.775651609 / 348.777747338 /
348.778673215, `e1` = −5.4308 / −3.3351 / −2.4092 mK, ratios 1.628 / 1.384.

### 1.2 The replica control, and why it is a refusal and not a row

`D_R_f` is the frozen `W_f` rebuilt by the **new** builder with **nothing
changed**. It reproduces `gate_t9a.json`'s `W_f` **exactly**:

```
T_i1 d = +0.000e+00 K   T_i2 d = +0.000e+00 K   q'' d = +0.000e+00 W/m2
```

Its only textual difference from `W_f` is the explicit
`laplacian(DT,T) Gauss linear corrected;` line that every `D_*` case carries so
the comparator can read the arm's single change off disk (`diff` over
`0.orig/T`, `0.orig/DT`, `constant/transportProperties`, `system/controlDict`,
`system/fvSolution`, `system/blockMeshDict`: **identical**; `system/fvSchemes`:
the four added lines). **So "one change per run" is a measurement here, not a
claim about a script**, and any difference in `D_B_x` or `D_C_*` is the
registered change and not the new builder.

**It is a near-IDENTITY (Charter §2a) and is therefore not one of the seven
graded rows.** It is wired as a **refusal condition**: had it not reproduced
`W_f`, the comparator would have declared every row NOT A RESULT. A control
that cannot fail informatively is wired as a refusal, never as a green light.

---

## 2. The diagnosis, stated with numbers

### 2.1 The scheme is the cause, and harmonic is not merely better — it is exact

At every level, `Gauss harmonic` reproduces the closed form **to all nine
printed digits in all three quantities**: `q″` 19.502681619 against
19.502681619, `T_i1` 348.781082399 against 348.781082399, `T_i2` 300.024378352
against 300.024378352. The residual `|e1|` is **3.0e-09 mK** = 3.0e-12 K, which is
round-off on a 348 K field: **8.5e-15 relative, about 50 ulp of a double at
that magnitude.**

**This is not luck, and it is not restricted to equal spacing.** ESI v2606's
`harmonic` interpolates `gamma` as `1/reverseLinear(1/gamma)`
(`harmonic.H`), and `reverseLinear`'s weights are `1 − cd weights`
(`reverseLinear.H`), so the face conductivity is

```
k_f = 1 / ( (1−w)/k_P + w/k_N ),      w = (dx_N/2) / d,   d = (dx_P + dx_N)/2
```

and since `(1−w) = (dx_P/2)/d`, the face conductance is

```
k_f/d = 1 / ( dx_P/(2 k_P) + dx_N/(2 k_N) )
```

**which is the series resistance of the two half-cells, exactly, for any
spacing ratio.** T9a-D's interface 2 does *not* have equal spacing either side
at any level (dx 0.0019608 | 0.0015385 at level f), and it is reproduced to
round-off anyway. The pre-registration flagged unequal spacing as a place a
residual might survive; **it does not, and the algebra above says why.**

The frozen `Gauss linear` face conductivity at the 0.8 | 0.04 interface is the
arithmetic 0.42 W/mK against the series value 0.0762, and at 0.04 | 16 it is
8.02 against 0.0798 — the numbers `T9a_RESULTS.md` §1.1 already recorded. The
resistance those two faces fail to charge, at level f, is

| | interface 1 | interface 2 | total | as a fraction of `ΣR` | measured `q″` excess |
| --- | ---: | ---: | ---: | ---: | ---: |
| 400× | 2.090e-02 | 2.173e-02 | 4.263e-02 | **1.663 %** | **1.806 %** |
| 40× | 4.150e-04 | 2.050e-03 | 2.465e-03 | **0.786 %** | **0.879 %** |

**The mechanism predicts the measured flux excess to about 12 % of itself at
both contrasts, from nothing but the two face conductivities.** That closes
H-A: the interface scheme is the cause of R0's 1.8 % and of R1's 2.41 mK.

### 2.2 The mesh is not the cause, and a fourth level does not rescue the band

Level `x` (145 cells) behaves exactly as the ladder below it: `e1` goes
−3.335 → −2.409 → **−1.538 mK**, ratios **1.384 then 1.566** — first order,
still first order, converging to zero and in no hurry (**B1 PASS**). Refinement
works. It is simply not a repair: at this rate, reaching 0.1 mK needs roughly a
16-fold further refinement.

**And the fourth level makes the band worse, not better.** The successive
*differences* are −0.926 then −0.871 mK — barely shrinking — so the triple's
observed order is **`p` = 0.130, STAGNANT**, and by the registered rule **no
band may be armed** (**B0, B2 NOT A RESULT**). Had one been armed anyway it
would have been **17.21 mK against a 1.54 mK error: 11× too WIDE.**

> **This is the finding that generalises, and it is the exact inverse of
> T9a's.** On the c/m/f triple the differences fell *faster* than the errors,
> the GCI read `p` = 1.738, and it armed **0.92 mK for a 2.41 mK error — 2.6×
> too narrow**. On m/f/x the differences fall *slower* than the errors, the GCI
> reads `p` = 0.130, and a band armed there would be **11× too wide**. **Same
> quantity, same solver, same error mechanism, same first-order error
> sequence** (−5.43 / −3.34 / −2.41 / −1.54 mK, ratios 1.63 / 1.38 / 1.57) —
> and the Roache band computed from successive differences lands on **opposite
> sides of the truth by an order of magnitude depending on which three of the
> four levels you feed it.** The band is not measuring the error. It is
> measuring how the differences happen to sit.

### 2.3 The property jump matters — but not the way the directive predicted

**C1 GATE FAILS, and in the opposite direction.** Reducing the contrast
400× → 40× **grew** the R1 error by 27–31×, from −5.43 / −3.34 / −2.41 mK to
−168.06 / −104.16 / −64.99 mK. Two things cause that, and both are measurable:

1. **The relative flux error did fall — by 2.05×, not 10×.** `q″` excess went
   1.806 % → 0.879 %. §2.1's table says why: at 400× the two interfaces
   contribute the missing resistance almost equally (49 % / 51 %), but changing
   `k₂` from 0.04 to 0.4 leaves interface 2 **still a 40× jump**, which then
   supplies **83.2 %** of the deficit. **Weakening one of two jumps cannot
   weaken the error by the full contrast ratio.**
2. **The absolute flux error grew 4×, because the exact flux grew 8×.**
   `q″` excess 0.352 → 1.401 W/m². A wall with a less resistive middle layer
   carries more heat, so the same *relative* mistreatment is a bigger *absolute*
   one.

**And then the reconstruction stops hiding it.** `T_i1` is the flux-continuous
face value, weighted `k/d` from the two cells straddling the interface:

| | naive `−δq·R₁` | observed `e1` at level f | how much the reconstruction cancels | weight it puts on the layer-1 cell |
| --- | ---: | ---: | ---: | ---: |
| 400× | −22.02 mK | **−2.41 mK** | **89.1 %** | **95.3 %** |
| 40× | −87.57 mK | **−64.99 mK** | **25.8 %** | **67.1 %** |

At a 400× contrast the reconstruction is 95 % determined by the high-`k` cell
and **cancels 89 % of the flux error**. At 40× the weights even out and it
cancels only 26 %. **So T9a's R1 error is small not because the interface
treatment is nearly right, but because the measurement of `T_i1` nearly cancels
a treatment that is wrong by 1.8 %.**

### 2.4 The conclusion, in one paragraph

**The 2.41 mK is the interface scheme, and nothing else.** Replacing the
arithmetic face conductivity with the harmonic one removes it entirely — not
reduces it, removes it, to round-off, at every level including the coarsest
(A1, drop 8.2e+08). The mesh is not the cause: refinement shrinks the error at
a clean first order across four levels and would need ~16× more to reach 0.1 mK
(B1). The property jump is not a *separate* cause: **H-A and H-C are the same
mechanism seen from two sides** — an arithmetic face conductivity is only wrong
because there is a jump — and the pre-registration said so before the run.
What H-C adds is that the dependence on the jump is **sub-linear in the flux
(2.05× for a 10× contrast change, because the untouched second interface then
dominates) and inverted in the graded quantity (27–31× worse, because the
reconstruction's cancellation collapses when the conductivity weights even
out).**

### 2.5 What this does NOT show

- **It does not make T9a pass.** T9a's R1 verdict is GATE FAIL, frozen, and
  this arm has no authority over it. No T9a case was re-solved and no T9a
  number moved.
- **It does not establish that `Gauss harmonic` is correct for a conjugate
  rung.** It establishes that harmonic is *exact* for **piecewise-constant `k`
  with the interface on a mesh face on a 1-D orthogonal mesh**. T9b's coupled
  interface, a non-orthogonal mesh, a graded `k`, or a temperature-dependent
  `k` are all outside what was measured. The algebra in §2.1 is a statement
  about two half-cells in series, not about conjugate heat transfer.
- **It does not show that harmonic is safe to adopt everywhere.** Nothing here
  measured its behaviour on the fin rows, on any advective term, or on any
  quantity other than this wall's `q″`, `T_i1`, `T_i2`.
- **It does not show that T10a's B1 ceiling row has the same cause.** T10a
  shares R1's *pattern* — errors falling at roughly first order while the
  differences imply a higher order and arm too small a band. §2.2 now gives
  that pattern a mechanism *on this wall*. Whether a view-factor ladder shares
  it is not measured here and must not be assumed.
- **It grades nothing against a reference and produces no fidelity chip.** The
  seven rows grade predictions about a solver's own error, not physics against
  the world.
- **B1 and C2 name an order, never a cause.** Any mechanism first order in `dx`
  reproduces those ratios; the identity test in the pre-registration says so
  for both rows.
- **The rows that read against the exact reference are not instruments
  independent of the hypothesis** (Charter §2d.1 condition 2). They ground no
  repair to anything, and none was made.

---

## 3. Iterative convergence, and the planted zero

`residualControl` absent (L-141); `endTime` 1000, `writeInterval` 100,
`purgeWrite` 2 (L-140), so checkpoints 900 and 1000 exist on every case.

| case | `T` change 900 → 1000 | field range | state |
| --- | ---: | ---: | --- |
| `D_A_c` / `D_A_m` / `D_A_f` | **0.0 K** (internal field byte-identical) | 49.9366 / 49.9604 / 49.9756 K | CONVERGED |
| `D_B_x` | **0.0 K** | 49.9847 K | CONVERGED |
| `D_C_c` / `D_C_m` / `D_C_f` | **0.0 K** | 49.4704 / 49.6718 / 49.7990 K | CONVERGED |
| `D_R_f` | **0.0 K** | 49.9752 K | CONVERGED |

**Eight literal zeros, so the zero needs a live control** (L-141). On a scratch
copy of `D_C_f` **outside the run tree**, +1.234e-03 K planted into one cell of
`900/T` was recovered by the frozen `analyse_t9a.iterative_convergence` reader
as `max_change` **1.2340000e-03 K**, state **NOT_CONVERGED**. The scratch tree
is deleted by the comparator; the case tree was not touched. `DICPCG` at
tolerance 1e-14 reached an initial residual of ~4e-15 with zero iterations from
the second step on every case.

Heat-balance closure `|q_hot − q_cold|/q̄` ran 3.2e-12 to 1.7e-10 across the
eight cases. It is a near-identity on a 1-D wall and is reported, not gated.

---

## 4. Mesh

`checkMesh` rc 0 on all eight (recorded in every `STATUS.*`). Verified
independently by `check_t9aD_mesh.py`, which **imports the frozen
`check_t9a_mesh.check_wall` unmodified** and drives it over the `D_*` cases
(zero solver compute): wall thickness 0.17 exactly on all eight, mesh planes at
`x` = 0.05 and 0.15 **off by 0.00e+00**, per-layer cell counts as registered
with spacing uniform to 8.9e-15 (c, m) and 6.7e-13 (f, x), and `0/DT` carrying
the registered `k` of its layer in 35/35, 56/56, 90/90, 145/145 cells against
cell centres — **including the 0.4 W/mK layer on all three `D_C_*` cases.**
Result: `ALL D_* MESHES VERIFIED`.

Refinement ratios read from the meshes (nominal 1.6, used by the GCI as T9a
does):

| step | layer 1 / 2 / 3 |
| --- | --- |
| `D_A_c → D_A_m`, `D_C_c → D_C_m` | 1.600 / 1.600 / 1.600 |
| `D_A_m → D_A_f`, `D_C_m → D_C_f` | 1.625 / 1.594 / 1.625 |
| **`D_R_f → D_B_x`** | **1.615 / 1.608 / 1.615** |

---

## 5. Provenance, the freeze, and the amendment

| event | time (Z) | evidence |
| --- | --- | --- |
| `predict_t9aD.py` written and run; `T9aD_predictions.json` | 17:52:09 | mtimes |
| `T9aD_registered.json` written | 17:59:26 (final, incl. amendment) | mtime |
| pre-registration written | ~17:55, last edited 18:00:44.954 (§5.1 note) | mtime |
| **`analyse_t9aD.py` written and hashed** `8b1a7237…eb2300f3` | before 17:58 | §5.1 of the pre-registration |
| **amendment: `D_R_f` added; comparator re-hashed** `2d4ebb49…8d4a79e6` | 17:58–17:59 | pre-registration §5.1 |
| **FREEZE CONDITION CHECKED, not asserted** | **17:58:41.441** | see below |
| `build_t9aD.py` written; eight cases built | 18:00:44.959 | mtime, builder output |
| `blockMesh` on all eight, rc 0 | 18:01:2x | `log.blockMesh` |
| `check_t9aD_mesh.py` written and run | 18:01:42 | mtime, §4 |
| run scripts written; **serial chain starts** | 18:01:14; **18:01:59.295** | mtimes, `STATUS.*` |
| chain finishes (`D_R_f` last) | **18:02:05.895** | `CHAIN_DONE_D` |
| `mark_done_t9aD.py`: 8/8 markers | 18:02:17.863 | marker mtimes |
| comparator refuses twice on a tolerance; repaired; runs | 18:02:4x–18:03:16 | §6 |

**The freeze condition, run before the builder existed and pasted verbatim:**

```
$ date -u +%FT%T.%3NZ; find verification/runs/T-family/T9a_runs -name 'D_*' -print | wc -l
2026-08-22T17:58:41.441Z
0
```

**Margin: the comparator was hashed and the run tree confirmed empty of `D_*`
at 17:58:41.4 Z; the first solver started at 18:01:59.3 Z (+197.9 s) and the
earliest completion marker was written at 18:02:17.86 Z (+216.4 s).** Frozen by
construction, and checked rather than claimed.

**The amendment (pre-registration §5.1), disclosed as an amendment.** `D_R_f`
was added **after** the comparator's first hash and **before** any compute,
under Charter §2b(1), whose condition — no answer to tune to — was **checked**
by the command above and stated on its face. It **added a control and a refusal
condition and changed no threshold, no row, no band and no reference.** Both
comparator hashes are recorded in the pre-registration so the amendment is
visible as an amendment.

**One further disclosure with no numerical content.** The pre-registration's
last edit (18:00:44.954 Z) landed 4.7 ms before `build_t9aD.py` was written,
i.e. after the freeze check and before any case existed. It added **one table
row** to §1 naming `D_R_f` — documentation of the amendment already recorded in
`T9aD_registered.json` at 17:59:26. No threshold, prediction, band or reference
was touched.

**The frozen T9a files, hashed at analysis time and matching what
`T9a_RESULTS.md` published:**

| file | sha256 | published as |
| --- | --- | --- |
| `analyse_t9a.py` | `dd2d6bf0…4ecac9da` | `dd2d6bf0…cac9da` ✓ |
| `exact_t9a.py` | `d3f2558c…17d3d0b8` | `d3f2558c…d3d0b8` ✓ |
| `T9a_registered.json` | `66b03c7d…1edb40ed` | `66b03c7d…b40ed` ✓ |
| `build_t9a.py` | `516fee581ecfaa25ffddefbb286de6b78c13b7bb9e9b635581958e4e9a2659e9` | unchanged before and after the D build |

**And T9a's own output is untouched.** `gate_t9a.json` still hashes
`7c4c6826283f98d31e0c313cd713412b969bb2a4486b78ea31617eb1b3a5f4f8` — byte for
byte the value `T9a_RESULTS.md` published — and every T9a marker, `STATUS.*`,
`CHAIN_DONE` and `log.solve` still carries its 2026-08-20/21 mtime. This arm
read that file and wrote nothing into T9a's half of the run tree.

**No frozen file was edited.** Where the frozen readers needed a different
conductivity (H-C) or a different scheme (H-A), the change was made **in
memory** for the duration of one call and restored, and the comparator's
self-test asserts the restoration (`frozen WALL_LAYERS restored`,
`frozen REG k restored`).

---

## 6. The comparator refused twice, and what was repaired

**Disclosed in full because it is a change to a comparator after its first
graded solve.**

On its first run at 18:02 Z, `analyse_t9aD.py` refused before measuring
anything:

```
REFUSE: derived 400x q = 19.502681618722573 disagrees with the registered 19.502682
```

and, after the first repair:

```
REFUSE: derived 40x q = 159.3625498007968 disagrees with the registered 159.36255 (rel error 1.250e-09 > 1.0e-09)
```

**What was wrong.** A single *relative* tolerance of 1e-8 was applied to
constants that are *printed to six and five decimals respectively*. T9a's
`q″` is registered as `19.502682`; the derivation gives 19.502681618…, a
relative difference of 1.96e-08 — **the rounding of the printed decimal, not a
disagreement.** The frozen `analyse_t9a.py` uses 1e-6 for exactly this
comparison and never hit it.

**What was changed.** Each constant is now checked to **half a unit in its own
last printed place** (5e-7 absolute for the six-decimal 400× pair, 5e-6
absolute for the five-decimal 40× `q″`), with the full-precision 40× `T_i1`
still at 1e-9 relative. The `diff` between the frozen version and the version
that ran is **one contiguous block inside that refusal check** — the whole diff
is reproduced in the run tree as
`analyse_t9aD.py.pre_tolerance_2026-08-22` beside the file that ran.

**Why this is Charter §2d's boundary clause 1 and not §2d.1's repair
exception.** §2d's boundary explicitly excludes *"a comparator that cannot run
at all"*, and its test is **"could this change move a number that a verdict
depends on?"** This one cannot: it compares **two derived/transcribed
constants against each other** and touches no measurement, no row, no band, no
threshold and no case. Nothing frozen was edited, so §2d.1's four-condition
repair exception is **not invoked and not needed**. Every measured value in §1
was produced by the code below that check, byte-identical across both versions.

**Reproducibility.** The comparator was run again after the repair and
`gate_t9aD.json` reproduced with **exactly one differing line: the random
`mkdtemp` name of the deleted planted-zero scratch directory**
(`/tmp/t9aD_planted_y8_qd7c8` vs `/tmp/t9aD_planted_x2zy2gc6`). Every
measurement, every triple, every verdict and every hash reproduced byte for
byte. `analyse_t9aD.py` exits 1, its own rule for an arm carrying a GATE FAIL
row.

---

## 7. The comparator's own instrument, and the sign it does not inherit

`analyse_t9aD.py` carries **its own** `gci()`, sign-correct per Roache:
`f_f + (f_f − f_m)/(r^p − 1)`. **This is a new instrument, not a repair.** It
was written before any `D_*` case existed, for a new arm; the frozen
`analyse_t9a.gci()` is imported and **not called on any T9a-D row**; nothing
frozen changed and no published number moved.

Its `--selftest` runs before any case is needed and is reproduced here in
substance: an exact first-order triple returns `p` = 1.000000 and extrapolates
to the constructed limit; an exact second-order triple returns `p` = 2.000000
and the same limit; the GCI matches `Fs·|e21/f_f|/(r^p − 1)` to 1e-12; the
OSCILLATORY, STAGNANT, DIVERGENT and EXACT states are each produced by a triple
built to produce them; and on **T9a's own published R0 triple** the two
instruments are compared side by side:

| | Richardson extrapolate of 20.425588 → 20.069440 → 19.854991 |
| --- | --- |
| frozen `analyse_t9a.gci()` | **20.179541 — ABOVE the fine value**, back toward the coarse |
| this instrument | **19.530441 — below the fine value**, where a monotone falling triple's limit must lie |
| **GCI band, both** | **2.0432503592470312 % — identical** |

The band is identical because both use `|e21|`. **So no T9a verdict would have
changed under either implementation**, which is stated here so this file cannot
be read as quietly correcting a graded result. `T9a_RESULTS.md` §8.1 quotes
19.5304 for this extrapolate; the new instrument reproduces it.

---

## 8. The emulator identity, reported and never gated

`predict_t9aD.py` — a 1-D finite-volume emulator of laplacianFoam's steady
discrete operator, **zero solver compute** — produced every registered
prediction in the pre-registration **before any case existed**. Against the
solved cases:

| case | predicted `T_i1` | solved `T_i1` | difference |
| --- | ---: | ---: | ---: |
| `D_A_c` / `D_A_m` / `D_A_f` | 348.781082399 | 348.781082399 | −5.7e-13 / −4.8e-12 / −4.8e-12 K |
| `D_B_x` | 348.779544025 | 348.779544025 | +1.9e-11 K |
| `D_C_c` / `D_C_m` / `D_C_f` | 339.871777974 / 339.935682430 / 339.974846560 | identical | +1.6e-12 / −3.5e-12 / −1.3e-11 K |
| `D_R_f` | 348.778673215 | 348.778673215 | −3.5e-12 K |

**This is an IDENTITY (Charter §2a) and is gated on nothing.** The emulator and
laplacianFoam solve the same discrete equations, so agreement is arithmetic,
not evidence — a wrong treatment of the physics would be reproduced by both. It
is reported because it **dates** the predictions: every number in §2.1–§2.3 was
written down before the solver was asked, and the solver agreed to 2e-11 K.

**Every registered prediction in the pre-registration came back as
registered**, including the three where this arm's own arithmetic contradicted
the directive it was executing (A2 untestable, B0/B2 stagnant, C1 inverted).
Those disagreements were written into `T9aD_registered.json` and the
pre-registration **before the solve**, which is the only reason they can be read
as predictions rather than as excuses.

---

## 9. Cost, actual against predicted

`nProcs` 1 on every case; the chain is serial, so the arm's peak occupancy is
**1 core of 16**. Twelve cores carried other lanes' solvers (T1b L4 ×4, T3
ext1 ×8) throughout and **no other process was touched**; the box also picked
up unrelated Python load during the run, so wall times include contention.

| case | cells | `STATUS` wall, s | solver `ExecutionTime`, s |
| --- | ---: | ---: | ---: |
| `D_A_c` | 35 | 0.15 | 0.06 |
| `D_A_m` | 56 | 0.23 | 0.06 |
| `D_A_f` | 90 | 0.26 | 0.07 |
| `D_B_x` | 145 | 0.12 | 0.07 |
| `D_C_c` | 35 | 0.25 | 0.06 |
| `D_C_m` | 56 | 0.13 | 0.06 |
| `D_C_f` | 90 | 0.14 | 0.06 |
| `D_R_f` | 90 | 0.11 | 0.06 |
| **total** | **597** | **1.39** | **0.50** |

**Chain wall clock, start to finish: 18:01:59.295 → 18:02:05.895 = 6.60 s.**

| measure | core-seconds | USD at 0.0513/core-h |
| --- | ---: | ---: |
| solver `ExecutionTime` only | 0.50 | 7.13e-06 |
| per-case wrapper wall | 1.39 | 1.98e-05 |
| **chain wall clock (what a core was occupied for) — the figure this arm reports** | **6.60** | **9.41e-05** |

**Predicted: 1.2 core-seconds, 1.71e-05 USD.** Against the measure the
prediction was written on — per-case wrapper wall — **the actual is 1.39 s,
16 % over the registered ceiling**, because two cases took 0.23–0.26 s under
contention rather than the ≤ 0.15 s assumed. Against the honest occupancy
measure, chain wall clock, **the prediction was 5.5× low**, because it counted
only the solver and not `checkMesh`, the `0/` re-copy and process spawn between
cases. **The registered figure was a solver-time ceiling described as a
core-second ceiling; that is the error, and the next arm should register the
chain wall clock.** Every figure is under 1e-04 USD and inside the standing
pre-authorisation (every run under 25 USD, `T3_PREREGISTRATION.md` §10).

`predict_t9aD.py`: **zero OpenFOAM invocations of any kind.**
`check_t9aD_mesh.py` and the comparator: **zero solver compute, but not zero
OpenFOAM** — each ran `postProcess -func writeCellCentres` (and the comparator
also `writeCellVolumes`) once per case, the mesh checker at `t` = 0 and the
comparator at `t` = 1000, leaving one `log.writeCellCentres.t0`,
`log.writeCellCentres` and `log.writeCellVolumes` per case. `postProcess` is a
field-writing utility, not a solver; it is stated here rather than folded into
"zero compute", and it is below the resolution of the cost table.

---

## 10. Arm verdict

**DIAGNOSIS COMPLETE. Of T9a's three candidate causes for the 2.41 mK R1 miss,
the interface scheme is the whole of it.**

**A1 PASS** — `laplacian(DT,T) Gauss harmonic corrected` accepted by ESI v2606
(not BLOCKED), and it reduces the R1 level error from −5.4308 / −3.3351 /
−2.4092 mK to 0 / −3.18e-09 / −2.96e-09 mK, drop factors ∞ / 1.05e+09 /
8.15e+08 against a registered threshold of 3; the flux excess goes 1.806 % →
0.0000000 % and all three quantities reproduce the closed form to nine printed
digits at every level. **A2 NOT A RESULT** — the registered 0.001 mK collapse
floor fired, as this arm's own registered arithmetic predicted. **B0 NOT A
RESULT** — the m/f/x triple is STAGNANT at `p` = 0.1305 and no band may be
armed. **B1 PASS** — level errors −3.3351 / −2.4092 / −1.5384 mK, ratios
1.384 / 1.566 inside [1.25, 2.05]: first order across four levels, converging
but not a repair. **B2 NOT A RESULT** — no band on a stagnant triple; a
forbidden arming would have given 17.21 mK against a 1.54 mK error, 11× too
wide, the exact inverse of T9a's 2.6×-too-narrow band on the same quantity.
**C1 GATE FAIL** — shrink factors 0.0323 / 0.0320 / 0.0371 against a registered
[3, 30]: reducing the contrast 10× **grew** the error 27–31×, because the
untouched second interface then supplies 83 % of the missing resistance and
because the flux-continuous reconstruction's cancellation collapses from 89 %
to 26 %. **C2 PASS** — ratios 1.614 / 1.603, still first order at 40×.

**Replica control `D_R_f` reproduces the frozen `W_f` to 0.000e+00 K in all
three quantities; planted zero recovered at 1.2340000e-03 K; all eight cases
CONVERGED with 0.0 K change between checkpoints; all eight meshes verified;
comparator frozen +197.9 s before the first solver and its output reproduced
with one differing line, a deleted temp-directory name; 6.60 core-seconds,
9.41e-05 USD.**

**T9a's own verdict is unchanged: GATE FAIL on R1. This arm re-solved nothing
and moved nothing.**
