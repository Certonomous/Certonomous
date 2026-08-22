# MODEL — the FS4 freeze

**Frozen 2026-08-22, before any propagation run whose result is reported**, as
`PREREGISTRATION.md` sec. 4 requires: one term set for `b^Delta`, one for `R`,
with coefficients, terms and the training families used. **After this point no
term is added or removed. Any later change is a new preregistration.**

Machine-readable twin: `MODEL.json` — the file `build_aposteriori.py` reads.
The coefficients below are its values, not a transcription.

> **One earlier `b^Delta` fit was WITHDRAWN**, together with the propagation
> arms built from it, **before any a-posteriori number was read**. Its tensor
> design matrix was stacked through an intermediate `(cell, candidate,
> component)` shape that mixed cells across rows. The sec. 6 a-priori gate
> caught it by returning a model *worse than predicting zero on its own
> training target*, which a least-squares fit cannot be. Record:
> `artefacts/fs3_WITHDRAWN_scrambled_bDelta.json`; `RESULTS.md` departure D-6.
> **`R` was never affected and reproduces bit for bit across the fix.**

## Training data behind these coefficients

12 cases, **172,171 cells** (172,106 after the fit mask), all four training
families: 6 hills, 4 ducts, `PHLL10595`, `CBFS13700`. Every case is a benchmark
**training** case. No TEST or validation case was opened — asserted in code at
the top of `assemble_dataset.py`, `fs3_select.py` and both scorers.

Targets are `kOmegaSSTFrozen`'s `bijDelta` and `kDeficit`; the basis is built on
the frozen fields with `tau = 1/omega`, `A_ij = d_j U_i`, `S = (tau/2)(A+A^T)`,
`Omega = (tau/2)(A-A^T)`, `I1 = S_mn S_nm`, `I2 = Omega_mn Omega_nm <= 0` — the
conventions `kOmegaSSTSparta` itself uses, so a coefficient below is the number
that goes into `RTerms` / `bDeltaTerms` unchanged. That equivalence is measured,
not asserted: **IC1**, an independent Python evaluation of these term sets
against the solver's own construction-time fields, agrees to **1.8e-12**
relative L2 (`artefacts/ic1_discovered.json`).

## The frozen model — the T1–T3 library of PREREGISTRATION sec. 1

`kOmegaSSTSparta` implements **T1, T2, T3 only** and dispatches
`n == 1 ? T1 : n == 2 ? T2 : T3`; a term registered with `n = 4` would silently
evaluate as T3. `build_aposteriori.py` asserts `n in (1,2,3)` before writing any
case, so that defect cannot reach a run from here.

### `R` — the k-equation correction (Schmelzer Eq. 12; the `2k` factor is inside the candidate)

    R = 2 k * [   1.261646025 (T1:A)
                - 42.82547649  I1   (T1:A)
                - 31.54761765  I2   (T1:A)
                + 14.28260064  I2^2 (T1:A) ]

`RTerms ( (1 0 0 1.261646025) (1 1 0 -42.82547649) (1 0 1 -31.54761765) (1 0 2 14.28260064) )`

* leave-one-family-out CV MSE **43.5533** (on the `k*omega`-non-dimensionalised target)
* design-matrix condition number **653.9**
* identical term set at **seeds 0, 1 and 2**
* **planted-zero control: PASS**

### `b^Delta` — the anisotropy correction (Schmelzer Eq. 8)

    b^Delta_ij = -7.550379605 T2_ij  -  16.07577893 I2 T2_ij  +  5.039083086 T3_ij

`bDeltaTerms ( (2 0 0 -7.550379605) (2 0 1 -16.07577893) (3 0 0 5.039083086) )`

* leave-one-family-out CV MSE **0.0156199**, against a zero-model **0.0173846** —
  a 10.2 % reduction in cross-family error
* design-matrix condition number **7.707**
* identical term set at **seeds 0, 1 and 2**
* **planted-zero control: PASS**

## The registered mixed-family fit — sec. 2.1's full T1–T4 library

| target | selected terms | LOFO CV MSE | cond | planted-zero |
|---|---|---|---|---|
| `R` | `T1`, `I1*T1`, `I2^2*T1` | 43.665 | 54.81 | **GATE FAIL** (`I2^2*T1` leave-one-family-out permutation importance **−322.2**, below both planted zeros) |
| `b^Delta` | `T2`, `I2*T2`, **`T4`** | 0.0158092 | 7.707 | PASS |

**Sec. 1's solver constraint costs nothing on this training set, and that is a
measurement.** The T1–T3 `b^Delta` model has a **lower** cross-family error than
the T1–T4 one (**0.0156199** against **0.0158092**): the free `T4` direction buys
no generalisation. The two fits agree exactly on `T2` and `I2*T2`
(−7.550379605, −16.07577893) and differ only in the third term, `+5.0391 T3`
against `−6.7275 T4` — consistent, since `T4 ≈ −T3` wherever the flow is close to
two-dimensional. **No static-field-injection arm was therefore needed**, and none
is claimed: the registered symbolic route is both available and better here.

**No term anywhere in this file is registered with `n = 4` for propagation.**
