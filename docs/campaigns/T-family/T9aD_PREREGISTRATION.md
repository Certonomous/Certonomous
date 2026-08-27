# T9a-D. Diagnosis arm: what is the 2.41 mK interface miss?

Campaign T, tier 4, rung T9a, **diagnosis arm D**. Written 2026-08-22,
**before any `D_*` case was built**. Sanaa's directive H-4: *"T9a's 2.4 mK
interface miss: diagnosis arm (interface scheme vs mesh vs property jump), one
change per run."*

Cases live in the existing run tree
`verification/runs/T-family/T9a_runs/` under the prefix `D_`, following T1c's
diagnostic precedent (`T1_runs/D_Pe`, `D_wedge`, `DIAGNOSTIC_PREDICTION.md`)
rather than opening a new tree for seven 35-to-145-cell cases.

**No frozen T9a file is edited.** `build_t9a.py`, `analyse_t9a.py`,
`exact_t9a.py`, `T9a_registered.json`, `mark_done_t9a.py` and the run scripts
are imported or copied from, never modified; their hashes are re-verified at
analysis time and printed.

---

## 0. What this arm is, and the three things it may not do

**T9a GATE FAILED one row.** R1, the composite wall's first interface
temperature, came out **2.41 mK below exact against a 0.92 mK GCI band**
(`T9a_RESULTS.md` §1). The level errors were **−5.43 / −3.33 / −2.41 mK**,
ratios **1.63 then 1.38** — shrinking at roughly first order and then slower —
while the triple's own successive differences implied `p` = 1.738 and armed a
band smaller than the remaining error. `T10a_RESULTS.md` §1.1 records the same
shape on its B1 ceiling row (errors −10.13 / −6.09 / −4.07 W/m², ratios 1.66 /
1.50, `p` = 1.48 from differences, 1.62 bands outside), and says of it: *"As in
T9a's R1…"*. **Two rungs, one pattern, no cause.** This arm goes after the
cause.

**This arm GRADES NOTHING against the T9a band.** It is a diagnosis. Its rows
carry verdicts, but each verdict is **PASS or GATE FAIL against a prediction
registered in this document with an explicit numeric threshold**, never against
T9a's registered references or T9a's GCI band. No T9a row moves. No T9a case is
re-solved: **the baseline numbers are READ from `gate_t9a.json`**, which has
been on disk since 2026-08-20 19:09 Z.

Three prohibitions, registered:

1. **It may not re-grade T9a.** T9a's verdict stands as its frozen comparator
   returned it: GATE FAIL on R1.
2. **It may not repair the frozen comparator.** `analyse_t9a.py`'s `gci()`
   carries the Richardson sign defect recorded in `T9a_RESULTS.md` §8.1 and
   again in `T10a_RESULTS.md` §1.1. The T9a-D comparator is a **NEW
   INSTRUMENT** with its own sign-correct GCI (§5). **This is not a repair.**
   The frozen file is imported unmodified and its `gci()` is not called on any
   T9a-D row. Charter §2d.1's repair exception is **not invoked and not
   needed**: nothing frozen changes.
3. **It may not widen a band because numbers looked wrong.** Charter §2d.1:
   *"a band is not an instrument; it is the hypothesis's own scoring rule."*
   Every threshold below is fixed here, before any `D_*` case exists.

---

## 1. The three hypotheses, one change per run

| arm | the single change | everything else | cases |
| --- | --- | --- | --- |
| **H-A interface scheme** | `laplacian(DT,T)` from `Gauss linear corrected` to **`Gauss harmonic corrected`** | frozen mesh ladder, frozen `k` (400× contrast), same solver, same `endTime` | `D_A_c`, `D_A_m`, `D_A_f` |
| **H-B mesh** | a **fourth level `x`** at ratio 1.6 on the same grading | frozen scheme, frozen `k` | `D_B_x` (one case; the triple tested is m/f/**x**) |
| **H-C property jump** | layer 2 conductivity **0.04 → 0.4 W/mK**, contrast 400× → **40×** | frozen scheme, frozen mesh ladder, geometry, temperatures | `D_C_c`, `D_C_m`, `D_C_f` |
| **CONTROL-R replica** (added §5.1, before compute) | **nothing** | everything frozen — level f, 400×, `Gauss linear` | `D_R_f` |

**No case changes two things.** H-A holds the mesh and the conductivities and
moves only the fvSchemes entry. H-B holds the scheme and the conductivities and
moves only the cell counts. H-C holds the scheme and the cell counts and moves
only one number in `0/DT`.

**The exact solution is re-evaluated for H-C**, not transcribed: `exact_t9a.py`
is imported unmodified and its `WALL_LAYERS` overridden **in memory**, so both
of its independent routes — the series-resistance closed form and a
harmonic-face FV solve by the Thomas algorithm — run on the 40× problem and
must agree, or the comparator refuses. The file on disk is never touched and
its sha256 is printed at every run.

**Registered exact values at 40×** (derived, both routes, before any case):

| quantity | 400× (frozen) | 40× (H-C) |
| --- | ---: | ---: |
| `ΣR` [m²K/W] | 2.563750 | **0.313750** |
| `q″` [W/m²] | 19.502682 | **159.362550** |
| `T_i1` [K] | 348.781082 | **340.039841** |
| `T_i2` [K] | 300.024378 | **300.199203** |
| layer-1 drop [K] | 1.218918 | **9.960159** |

### 1.1 The mesh ladder, including the new level

| level | cells per layer | total | realised ratio from the level below |
| --- | --- | ---: | --- |
| c | 10 / 20 / 5 | 35 | — |
| m | 16 / 32 / 8 | 56 | 1.600 / 1.600 / 1.600 |
| f | 26 / 51 / 13 | 90 | 1.625 / 1.594 / 1.625 |
| **x (new)** | **42 / 82 / 21** | **145** | **1.615 / 1.608 / 1.615** |

`x = f × 1.6` with T1c's integer rounding (26 → 41.6 → 42, 51 → 81.6 → 82,
13 → 20.8 → 21). The GCI uses the **nominal** 1.6, exactly as T9a does, and
this document records the realised ratios rather than hiding them.

---

## 2. Registered predictions, thresholds and falsifiers

**Written before any `D_*` case exists.** Each row's threshold is a number, not
a judgement. The full machine-readable form is `T9aD_registered.json`.

### 2.0 The arm's own arithmetic, registered as a prediction

Before writing thresholds, the arm computed what it expects, with
`predict_t9aD.py` — **a 1-D finite-volume emulator of laplacianFoam's steady
discrete operator on this wall, zero solver compute, no case, no mesh.** It
reproduces the scheme's face conductivity exactly as OpenFOAM forms it
(`Gauss linear`: `k_f = w·k_P + (1−w)·k_N`; `Gauss harmonic`:
`k_f = 1/((1−w)/k_P + w/k_N)`, because ESI v2606's `harmonic` interpolates as
`1/reverseLinear(1/gamma)` and `reverseLinear`'s weights are `1 − cd weights`,
both read from the installed source at
`/usr/lib/openfoam/openfoam2606/src/finiteVolume/.../harmonic.H`), and reads
`q″` and the interface temperatures back through the **same formulas the frozen
`analyse_t9a.measure_wall` uses**.

**It is checked against the frozen published levels before it predicts
anything.** On `W_c`/`W_m`/`W_f` it reproduces the T9a numbers already on disk
to **4.55e-12 K** worst case, and refuses to predict if that ever exceeds 1e-9 K.

> **This agreement is an IDENTITY and is never gated on (Charter §2a).** The
> emulator and laplacianFoam solve the same discrete equations, so agreement is
> arithmetic, not evidence; a wrong treatment of the physics would be
> reproduced by both. It is reported because it **dates** the predictions and
> because a *disagreement* would be a real finding about one of the two.

Its predictions, registered:

| arm | level | predicted `e1 = T_i1 − exact` |
| --- | --- | ---: |
| baseline 400×, `Gauss linear` (reproduced) | c / m / f | −5.4308 / −3.3351 / −2.4092 mK |
| **H-A** 400×, `Gauss harmonic` | c / m / f | **+5.68e-10 / +1.65e-09 / +1.88e-09 mK** |
| **H-B** 400×, `Gauss linear`, level x | x | **−1.5384 mK** |
| **H-C** 40×, `Gauss linear` | c / m / f | **−168.06 / −104.16 / −64.99 mK** |

### 2.1 H-A — interface scheme

- **A1 (the directive as issued).** *The R1 level error drops by more than a
  factor 3 at every level.*
  **Threshold: PASS if `min(drop_c, drop_m, drop_f) > 3.0`**, where
  `drop_k = |e1_frozen(k)| / |e1_harmonic(k)|`. **GATE FAIL otherwise.**
  **Falsifier:** any level whose harmonic `|e1|` exceeds one third of its
  frozen-scheme `|e1|`.
  *Identity test (§2a):* **fails if** a harmonic face conductivity leaves the
  interface error where it was. **Could a wrong treatment pass?** Yes, one way:
  a case that silently ignored the fvSchemes entry could return anything, so
  `D_A_*` are gated on the fvSchemes text being **read back from the case at
  analysis time**, on `q″` and `T_i2` being reported beside `T_i1`, and on the
  frozen mesh refusals (interface faces at `x` = 0.05/0.15, per-cell `DT`
  against the layer map) being re-run. A treatment right for the wrong reason
  is not excluded by A1 alone — which is why this is a diagnosis, not a rung
  verdict.

- **A2 (the directive as issued).** *The error becomes ~second order,
  successive `|e1|` ratios ≈ 2.56 (= 1.6²).*
  **Threshold: PASS if both ratios lie in `[2.0, 3.3]`. GATE FAIL otherwise.
  NOT A RESULT if the collapse floor fires.**
  **Registered collapse floor: 0.001 mK (1 µK), 2400× below the 2.41 mK being
  diagnosed.** If all three `|e1|` fall below it, the ratios measure round-off
  and the row is **reported, not graded**.
  > **REGISTERED DISAGREEMENT WITH THE DIRECTIVE, recorded before the solve.**
  > This arm's own arithmetic predicts A2 is **untestable**: harmonic
  > interpolation makes the discrete wall solution exact for piecewise-constant
  > `k` with interfaces on faces, so `|e1|` collapses to ~2e-09 mK and the
  > ratios (0.34, 0.88) are round-off. **The collapse floor is registered here,
  > before any case exists, precisely so that this escape cannot later be read
  > as one invented to rescue a prediction.** If A2 comes back NOT A RESULT
  > that is the *predicted* outcome, and it is A1 that carries H-A.
  *Identity test:* **fails if** the ratios miss the second-order window on
  errors large enough to carry an order. **Could a wrong treatment pass?** Yes
  — a ratio taken on round-off can land anywhere, including inside [2.0, 3.3].
  That is what the floor is for, and it is a number rather than a judgement.

### 2.2 H-B — mesh

- **B0 (the directive as issued).** *The m/f/x triple reads `p` ≈ 1.*
  **Threshold: PASS if the triple is CONVERGING and `p ∈ [0.7, 1.4]`; GATE FAIL
  if CONVERGING and outside; NOT A RESULT if OSCILLATORY, STAGNANT (`p` < 0.5)
  or DIVERGENT (`p` ≤ 0).** `p` is read from successive **differences**, the
  frozen convention.
  > **REGISTERED DISAGREEMENT.** The arm predicts differences of −0.926 then
  > −0.871 mK across m → f → x, i.e. `p` = **0.130**, **STAGNANT** — so B0 is
  > predicted **NOT A RESULT**. Registered before the solve.

- **B1.** *The R1 level ERRORS keep shrinking at roughly first order across
  m, f, x.*
  **Threshold: PASS if both of `|e1_m|/|e1_f|` and `|e1_f|/|e1_x|` lie in
  `[1.25, 2.05]`. GATE FAIL otherwise.** (First order at `r` = 1.6 is 1.60; the
  window is 1.6 × / ÷ 1.28, the span T9a's own 1.63 / 1.38 already covers.)
  **Not independent of the hypothesis:** this quantity is measured against the
  exact reference, so per Charter §2d.1 condition 2 it **grounds no repair to
  anything**. It grades a registered prediction of a diagnosis arm and nothing
  else.
  *Identity test:* **fails if** the errors stop shrinking (ratio → 1) or
  collapse (ratio ≫ 2). **Could a wrong treatment pass?** Yes — *any* error
  mechanism first order in `dx` reproduces this ratio. B1 establishes the
  **order** of the residual, never its **cause**; the cause is what A1 and C1
  separate.

- **B2 (the directive as issued).** *The band armed on the fourth level still
  fails to cover the true error.*
  **Threshold: PASS if `band_x < |e1_x|`; GATE FAIL if `band_x ≥ |e1_x|`; NOT A
  RESULT if the m/f/x triple is not CONVERGING**, because a band armed on a
  non-converging triple is one the registered rule forbids arming.
  > **REGISTERED DISAGREEMENT.** Predicted NOT A RESULT (stagnant triple). Had
  > the band been armed anyway it would have been **17.21 mK against a 1.54 mK
  > error — 11× too WIDE**, the opposite defect to R1's. That figure is
  > recorded as what a forbidden arming would have produced, and is not a
  > verdict.
  *Identity test:* **fails if** the band covers the error. **Could a wrong
  treatment pass?** Yes — a band can cover an error by being large for a bad
  reason (a stagnant triple inflates the GCI without improving the answer),
  which is exactly why the triple-state rule sits upstream and can void this
  row.

### 2.3 H-C — property jump

- **C1 (the directive as issued).** *With the contrast reduced 400× → 40× the
  first-order error scales roughly with the contrast ratio (≈ 10×).*
  **Threshold: PASS if all three of `shrink_k = |e1_400×(k)| / |e1_40×(k)|` lie
  in `[3, 30]`. GATE FAIL otherwise.**
  **Falsifier:** any shrink factor below 3 — **including growth**, which is a
  shrink factor below 1.
  **Scale:** the comparison is in **millikelvin and is scale-free**, because
  the driving potential `T_hot − T_cold` = 50 K is **identical in both arms**.
  The error as a fraction of the layer-1 drop is reported additionally, since
  that drop is *not* identical (1.2189 K at 400×, 9.9602 K at 40×) — the
  denominator question T9a §8.3 flagged, answered here in advance.
  > **REGISTERED DISAGREEMENT, and the strongest one.** The arm predicts C1
  > **GATE FAILS in the opposite direction**: `|e1|` at 40× is
  > **168.06 / 104.16 / 64.99 mK** against 5.43 / 3.34 / 2.41 mK at 400×, i.e.
  > shrink factors **0.032 / 0.032 / 0.037 — the error GROWS by 27–31×.**
  > Registered before the solve.

- **C2.** *At 40× the error is still first order in `dx`.*
  **Threshold: PASS if both `|e1_c|/|e1_m|` and `|e1_m|/|e1_f|` lie in
  `[1.25, 2.05]`. GATE FAIL otherwise.**
  *Identity test:* as B1 — first order in `dx` is a common signature and names
  no cause on its own.

### 2.4 The triple-state rule, applying to every row

Inherited verbatim from T9a: **a triple that is OSCILLATORY, STAGNANT (`p` <
0.5) or DIVERGENT (`p` ≤ 0) arms no band, and any row that depends on it is
NOT A RESULT.** No band is improvised from a non-converging triple, in either
direction.

---

## 3. Reported and never graded

| what | why it is not gated |
| --- | --- |
| `q″` and `T_i2` on every `D_*` case, each against its own exact reference | only the `T_i1` rows carry verdicts; the others are context |
| emulator agreement with each solved case | **an identity** (§2.0, Charter §2a): both solve the same discrete equations |
| heat-balance closure `\|q_hot − q_cold\|/q̄` | a near-identity on a 1-D wall |
| the frozen file hashes printed at analysis time | provenance, not a measurement |

**Controls are not re-run.** T9a's C1/C2/C3 graded T9a's rows and this arm
grades none of them; the trivial-baseline question (Charter §2c) is already
answered for this geometry by the solved `W_C3`, MET and on disk.

**Planted-zero control (L-141).** Every `D_*` wall case is expected to report
`max_change` = 0.0 exactly between the 900 and 1000 checkpoints, as all four
frozen wall cases did — **and a reader that cannot see anything would report
that same zero while broken.** So: **+1.234e-03 K is planted into one cell of
`900/T` in a SCRATCH COPY of `D_C_f`, outside the run tree**, and the
convergence reader must return `max_change` = 1.234e-03 K and state
NOT_CONVERGED. The case tree is not touched.

---

## 4. What this arm cannot show, registered in advance

- **It cannot make T9a pass.** T9a's verdict is frozen at GATE FAIL and this
  arm has no authority over it.
- **It cannot establish that `Gauss harmonic` is the right scheme for a
  conjugate rung.** It can only establish what happens to *this* error on
  *this* wall when the interpolation changes. A harmonic face conductivity is
  exactly right for piecewise-constant `k` with interfaces on faces and equal
  spacing either side; T9a-D's interface 2 does **not** have equal spacing
  either side at any level (dx 0.00500/0.00400 at c, 0.003125/0.00250 at m,
  0.0019608/0.0015385 at f), so any residual there is a property of the
  weighting and is reported, not generalised.
- **It cannot separate "the scheme" from "the property jump" completely.**
  They are the same mechanism seen from two sides: an arithmetic face
  conductivity is only wrong *because* there is a jump. H-A removes the
  treatment; H-C weakens the jump. **If both move the error, that is one
  mechanism and not two**, and the report must say so rather than counting two
  confirmations.
- **It cannot say anything about the fin rows, about conjugate coupling, about
  turbulence, or about T10a's sphere rows.** T10a's B1 shares R1's *pattern*;
  whether it shares R1's *cause* is not measured here.
- **It grades no band against a reference and produces no fidelity chip.**

---

## 5. The comparator, and why it carries its own GCI

`analyse_t9aD.py` **imports the frozen `analyse_t9a`** and reuses its readers
unmodified: `measure_wall`, `iterative_convergence`, `read_internal`,
`read_points`, `cell_centres`, `latest_time`, `boundary_blocks`, `refuse`. For
the H-C arm, `measure_wall` is called with the **registered layer-`k` map
overridden in memory** (`REG["wall"]["layers"][1]["k"] = 0.4`), because the
frozen reader verifies every cell's `DT` against the registered map and would
otherwise correctly refuse a 0.4 field. **The file on disk is never edited**;
its sha256 is verified against the value recorded in `T9a_RESULTS.md`
(`dd2d6bf0…cac9da`) at every run and printed.

**It carries its OWN `gci()`.** The frozen one returns
`richardson = f_f + (f_m − f_f)/(r^p − 1)`; Roache's extrapolate is
`f_f + (f_f − f_m)/(r^p − 1)`. `T9a_RESULTS.md` §8.1 documents this and
declines to fix it, because *"a repair cannot change a number a verdict depends
on"*; `T10a_RESULTS.md` §1.1 works around it by storing a separate
`richardson_corrected`.

> **This is a NEW INSTRUMENT, not a repair.** `analyse_t9aD.py` is written
> before any `D_*` case exists, for a new arm, with a sign-correct extrapolate
> from the start. Charter §2d.1's four-condition repair exception is **not
> invoked**: nothing frozen changes, no published number moves, and T9a's
> `richardson` field remains exactly as it was printed. The GCI *band* itself
> is unaffected by the sign in either implementation — it uses `|e21|` — so
> **no T9a verdict would have changed either way**, and this is stated so the
> new instrument cannot be read as quietly correcting a graded result.

The comparator has a **`--selftest`** that runs its GCI against constructed
triples with known answers (an exact first-order triple, an exact second-order
triple, an oscillatory triple, a stagnant triple, a divergent triple, and a
Richardson extrapolate whose limit is known by construction) and refuses if any
disagrees.

**sha256 of `analyse_t9aD.py`, recorded before the freeze check and before any
case existed:**

```
8b1a72376201bd0634ac75456fa6061966bed2632fc12bcb07ffdf2eeb2300f3
```

**sha256 of `T9aD_registered.json`:** `92f5db9879be7ba8506c7fd868f1d981e5be3347126db434d19b11f82f547b65`
**sha256 of `predict_t9aD.py`:** `b4f25de2241fd6e77195cc4612e184cee0ad300c32d9c3c22458af2e32112737`

### 5.1 Amendment, made before any compute and after the hash above

**Legal under Charter §2b(1): amendments are legal while there is no answer to
tune to, and the condition must be CHECKED and stated, not asserted.**

**What was added:** an eighth case, **`D_R_f` — the replica control.** It is
the frozen `W_f` rebuilt by the *new* builder with **nothing changed**: same
mesh level f, same `k`, same scheme. **It must reproduce `gate_t9a.json`'s
`W_f` `T_i1`, `T_i2` and `q″` to 1e-9 K / 1e-7 W/m².**

**Why it was needed, and why the arm is weaker without it:** every `D_*` case
is written by `build_t9aD.py`, not by the frozen `build_t9a.py`. Without a
replica, **any difference in `D_B_x` or `D_C_*` could be the new builder rather
than the registered change**, and "one change per run" would be an assertion
about a script instead of a measurement. `D_R_f` makes the builder a
controlled variable.

**It is a near-IDENTITY (Charter §2a) and is therefore NOT one of the seven
graded rows.** It is a **refusal condition**: if it does not reproduce `W_f`,
**every T9a-D row becomes NOT A RESULT**, because the arm's single-change claim
would be false. A control that cannot fail informatively is wired as a refusal,
not as a green light.

**The condition, checked at the moment of the amendment, not asserted:**

```
$ date -u +%FT%T.%3NZ; find verification/runs/T-family/T9a_runs -name 'D_*' -print | wc -l
2026-08-22T17:58:41.441Z
0
```

**It changes no threshold, no row, no band and no reference.** The comparator
was re-hashed after the change this required:

| file | sha256 | when |
| --- | --- | --- |
| `analyse_t9aD.py` (first freeze) | `8b1a7237…eb2300f3` | before the amendment |
| **`analyse_t9aD.py` (as run)** | **`2d4ebb49354eff6a3e22aa5619e1058a9bdf8cb6bd1938603b98df718d4a79e6`** | after the amendment, still before any `D_*` case existed |
| `T9aD_registered.json` (as run) | `4d6f482eed39ffbda1c5e76ea1e520c21e41d78e529ed8745613a8607b3e8637` | after the amendment |

**Both hashes are recorded** so the amendment is visible as an amendment rather
than as a single clean freeze.

---

## 6. Cost, registered before launch

Sanaa has blanket-approved runs; the cost is registered here anyway, before
launch, as the standing rule requires.

- **Cores: ≤ 3 of 16.** The chain is **serial** — one `laplacianFoam` process
  at a time, `nProcs` 1 — so the peak is **1 core**. Twelve cores are carrying
  other lanes' solvers (T1b L4 ×4, T3 ext1 ×8) and **no other process is
  touched**.
- **Basis:** T9a's four wall cases (35, 56, 90, 90 cells) took 0.09 / 0.10 /
  0.09 / 0.10 s wall and 0.05 / 0.05 / 0.06 / 0.06 s solver, on a host under
  the same contention.
- **This arm:** eight wall cases — 35, 56, 90, **145**, 35, 56, 90, 90 cells (the last is the `D_R_f` replica control added in §5.1). The
  new level `x` at **145 cells** is the largest, still 23× smaller than T9a's
  largest fin case (3328 cells, 5.85 s).

| | predicted |
| --- | ---: |
| total cells solved | 597 (8 cases, including the `D_R_f` replica control) |
| core-seconds (honest ceiling, not a point estimate) | **1.2** |
| core-hours | 3.3e-04 |
| **USD at 0.0513 /core-h** | **1.71e-05** |

Comparator, mesh checks and `predict_t9aD.py`: **zero solver compute.**
Actual against predicted is reported in `T9aD_RESULTS.md`.

---

## 7. If the scheme is refused

If `laplacian(DT,T) Gauss harmonic corrected` is not accepted by ESI v2606,
**the exact error text is recorded verbatim, H-A is marked BLOCKED, and no
substitute is improvised.** H-B and H-C continue.

Read from the installed source **before** registration, so that a refusal is
not a surprise dressed up as a finding: `harmonic` is registered as a scalar
`surfaceInterpolationScheme` (`harmonic.C`,
`addMeshConstructorToTable`/`addMeshFluxConstructorToTable`) and interpolates as
`1/reverseLinear(1/gamma)` (`harmonic.H`). **Its `weights()` is
`NotImplemented`**, so any caller reaching for weights rather than
`interpolate()` aborts. Whether the Gauss laplacian reaches for `interpolate()`
is settled by running it, not by this note.

---

## 8. Freeze condition

Per Charter §2b(1) and §2d: the comparator is written and hashed, and the
freeze condition — **no `D_*` case directory anywhere in the run tree** — is
then checked with a timestamped command whose output is pasted into
`T9aD_RESULTS.md` §5, **not asserted**. Only then is the builder written and
run.

## 9. Status at the time of writing

**NOT BUILT AND NOT RUN. Zero solver compute spent.** Every number above comes
either from `gate_t9a.json` (on disk since 2026-08-20) or from
`predict_t9aD.py` (pure Python, no OpenFOAM).

---

# ADDENDUM 1 — 2026-08-27T20:12:13Z. **POST-COMPUTE. CITATION SURGERY ONLY.** Version 1.0 → 1.1.

**`lines whose number changed above this section: 0`.** This addendum is appended at the
foot; nothing above it is edited, struck, reworded or renumbered (standing rule 6). **The
assertion was VERIFIED, not typed:** in the single shell invocation that wrote this
addendum, the bytes of this file above this section were compared byte-for-byte against
this path's committed blob at `HEAD` and the comparison was clean.

**Version convention, stated so it is not read as an invented history:** this document
carried no explicit version string. It is named **v1.0** as it stood, and this addendum
takes it to **v1.1**. No earlier version is claimed to have existed. *(The same
convention was used by `T10a_PREREGISTRATION.md` Amendment A2.)*

**Condition — POST-COMPUTE.** The T9a-D arm has run and graded. `CLAUDE.md` rule 2
governs in its post-compute limb: *"changes land only as dated addenda that cannot alter
a gate, threshold, cap or label."* **This is such an addendum.** **No verdict is
reopened. No byte of any instrument is touched** — `mark_done_t9aD.py` is byte-identical
to its `HEAD` blob before and after.

**Origin.** `docs/L342_GRADER_AUDIT.md` Addendum 8 (`commit:b85111d1`) §5, which found
that `T9a_runs/mark_done_t9aD.py` carries **no freeze citation for its own bytes** and
has already fired.

## AD1.1 THE MISSING CITATION — measured, with the reader's blindness ruled out

Until this addendum, **no committed document in this repository recorded a sha for the
bytes of `verification/runs/T-family/T9a_runs/mark_done_t9aD.py`.** Measured at `HEAD`
over every tracked file, in the invocation that wrote this addendum:

| search | width | hits |
| --- | ---: | ---: |
| sha256 prefix `fff6ba48f392abfb` | 16 | 0 |
| sha256 prefix `fff6ba48f392` | 12 | 0 |
| sha256 prefix `fff6ba48f3` | 10 | 0 |
| sha256 prefix `fff6ba48` | 8 | 0 |
| git blob prefix `38717d23` | 8 | 0 |
| git blob prefix `38717d2` | 7 | 0 |

**A zero from a reader not shown able to see a non-zero is not evidence** (standing rule
3). **The same search, in the same invocation, was run against a PLANTED positive
control** — the sha256 prefix `0feff87e148e1f69`, which belongs to the sibling instrument
`mark_done_t9a.py` — **and returned four tracked files**
(`T9aH_PREREGISTRATION.md`, `T9aH_runs/analyse_t9aH.py`, `T9aH_runs/gate_t9aH.json`,
`docs/L342_GRADER_AUDIT.md`). **The reader can see a citation of exactly this kind when
one exists. The zeros above are therefore evidence and not a blind spot.**

**RECORDED NOW, taken with `git hash-object` in the same shell invocation that wrote this
line, after confirming disk and `HEAD` identical for the path:**

| instrument | git blob sha1 (full) | sha256 (full) |
| --- | --- | --- |
| `verification/runs/T-family/T9a_runs/mark_done_t9aD.py` | `38717d238ec3c325dd8576eb7f2c9e725019733c` | `fff6ba48f392abfb121360d16baeea699c3df18f2568395f59bca0a599d0de39` |

*(For contrast, and to show the gap is specific rather than general: this arm's case
registry `T9aD_registered.json` — the file the instrument reads its `CASES` from — **is**
pinned, at sha256 `4d6f482eed39ffbd…`, in §5 of this document (line 385) and in `gate_t9aD.json`.
**The registry was frozen; the instrument that read it was not.**)*

## AD1.2 ⚠⚠ WHAT THIS CITATION DOES **NOT** ESTABLISH — and it is the whole of the limitation

**THIS CITATION PINS FORWARD FROM ITS DATE, AND NOTHING BEHIND IT.** Recording
`38717d23…` on 2026-08-27 establishes which bytes stand at this instrument's `HEAD` blob
**today** and **nothing whatever** about the bytes that stood at any earlier moment. A
sha recorded after the fact **cannot reach backwards.**

**Eight completions stand behind this pin and are not secured by it.** The eight `DONE.*`
markers for this arm's registered cases — `D_A_c`, `D_A_m`, `D_A_f`, `D_B_x`, `D_C_c`,
`D_C_m`, `D_C_f`, `D_R_f` — were **all written at 2026-08-22T18:02:17Z**, and
`T9aD_RESULTS.md` line 330 records that firing as *"`mark_done_t9aD.py`: 8/8 markers |
18:02:17.863 | marker mtimes"*.

**AND THE INSTRUMENT WAS NOT IN THE REPOSITORY WHEN IT FIRED.** Measured: the earliest —
and only — commit touching this path is `commit:06410acd`, **2026-08-22 18:21:01Z**,
**nineteen minutes AFTER the eight markers were written.** The bytes that decided those
eight completions existed only in the working tree at the moment they decided them.

**So: WHICH REVISION OF `mark_done_t9aD.py` WROTE THOSE EIGHT `DONE` MARKERS IS `NOT
MEASURED`, AND IT IS NOT RECOVERABLE FROM THIS RECORD.** The path holds exactly one blob
in its committed history, but **that is not evidence about the pre-commit worktree**: an
uncommitted file can be edited any number of times and leaves no trace, and the commit
that finally captured it came after the run. A `DONE.<case>` file carries no instrument
identity of its own, and no committed document names a sha for this instrument at or
before 18:02:17Z.

> **This addendum does not, and cannot, retroactively secure those eight completions. It
> makes the NEXT firing of this instrument checkable and leaves the previous eight
> exactly as unsupported as they were before it was written.** Anything read into it
> beyond that is read in error. **This is stated as a limitation of the repair, not as a
> disclaimer attached to a repair that quietly claims more.**

## AD1.3 A CORRECTION TO THE AUDIT'S COUNT — the DONE files beside it are not the DONE files written by it

`L342_GRADER_AUDIT.md` Addendum 8 §5 reads *"`T9a_runs/mark_done_t9aD.py` (**15** beside
it)"* — which is exactly right as written, **`beside`** — but that commit's summary line
carries the same figure as a bare `(15)` and totals *"an instrument that has decided
**28** completions"*. **Two different quantities are being counted as one**, and the
correction is recorded here rather than left to propagate.

Measured: `verification/runs/T-family/T9a_runs/` holds **15** `DONE.*` files and **two**
markers.

- **`mark_done_t9aD.py` reads its `CASES` from `T9aD_registered.json` (`:25`): eight
  cases, `D_A_c D_A_m D_A_f D_B_x D_C_c D_C_m D_C_f D_R_f`. Eight `DONE` files match, and
  `T9aD_RESULTS.md:330` records the firing as 8/8.**
- **The other seven — `W_c W_m W_f W_C3 F_c F_m F_f` — are `mark_done_t9a.py`'s
  module-level `CASES` list (`:18`)**, a different instrument.

**`mark_done_t9aD.py`'s exposure is EIGHT completions, not fifteen**, and the audit's
cross-team total of 28 is correspondingly **21** on this reading (13 for
`mark_done_t10a.py` + 8 here). **`mark_done_t9a.py` is NOT part of this gap: its own
bytes ARE cited**, at sha256 `0feff87e148e1f69…`, in `T9aH_PREREGISTRATION.md` and
`T9aH_runs/gate_t9aH.json` — it is the planted control of §AD1.1.

**The correction reduces this team's exposure, and is therefore stated with its method
attached rather than asserted**: the count is derived from each instrument's own
registered case list, read at `HEAD`, and every one of the fifteen `DONE` files is
accounted for by exactly one of the two lists. **Nothing about the eight is made better
by there being eight rather than fifteen** — §AD1.2 stands unaltered.

## AD1.4 WHAT THIS ADDENDUM DID NOT DO — each stated explicitly

- **No instrument byte changed.** `mark_done_t9aD.py` and `mark_done_t9a.py` are
  byte-identical to their `HEAD` blobs, before and after. Nothing was staged, edited or
  reverted in either.
- **No frozen line above was edited.** Byte-prefix verified against the `HEAD` blob.
- **No gate, threshold, band, cap, label or cost basis moved**, and none could: this
  addendum adds no test and computes no number a verdict depends on.
- **No verdict is reopened, no case re-graded, no case re-run**, and **no `DONE` marker
  was written, deleted or re-dated.**
- **NOTHING WAS LAUNCHED.** No case directory, no mesh, no solver, no pid, no queue
  entry. **Zero core-minutes.**
- **Nothing was sent** (standing rule 7). Submissions remain **PARKED**.
- **No permission setting, `CLAUDE.md` or `.claude/` configuration was touched**
  (standing rule 9). No agent message was treated as Sanaa's consent.

*Addendum written by a heat-transfer lane on the heat-transfer supervisor's
citation-repair brief, from `docs/L342_GRADER_AUDIT.md` Addendum 8 (`commit:b85111d1`) §5,
2026-08-27T20:12:13Z. Zero core-minutes.*
