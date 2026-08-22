# RESULTS — R4 SpaRTA-class build lane (FS3/FS4)

Preregistration: `PREREGISTRATION.md`, frozen 2026-08-21, **sha256
`058444309f87a9e1f6faccca2086bf16364df7a06bb7702d155c35b1fcacbbe8`** (verified
against disk at the start of this lane and again at commit). The file was never
edited. Every departure is in the dated section at the foot of this file.

**Docket:** D443 / D444 (R3 = SpaRTA-class, R4 approved the same day).
**Verdict vocabulary:** `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` /
`BLOCKED` / `PENDING` — nothing else appears below as a verdict.

**Zero-shot boundary.** No TEST case was opened for any purpose by this lane.
The boundary is asserted in code, not promised in prose: `r4_lib.assert_no_test_case`
raises on any member of the benchmark README's TEST set or of the validation set,
and it is called at the top of the case builder, the dataset assembler, the FS3
selector and both scorers. **The Repo 2 release and the zero-shot scoring call
are Sanaa's alone; this lane ran neither and prepared no submission.**

---

## 0. Status

This table states what is true **at the commit that carries it**, not what is
planned. A step is not "done" until its artefact exists at a path named here.

| step | state at this commit | artefact |
|---|---|---|
| 1. target extraction (`kOmegaSSTFrozen`) | **done** — 12 of 27 training cases COMPLETE under the strict completion rule | `artefacts/frozen_inventory.json`, sec. 2 |
| 2. candidate library on the frozen fields | **done** | `artefacts/dataset_manifest.json`, sec. 3 |
| 3. FS3 selection (3 methods, 3 seeds, planted-zero control) | **PENDING** — `fs3_select.py` is live; the reading that lands in sec. 4 is the one written to `artefacts/fs3.json`, and no FS3 number appears in this file until it does | sec. 4 |
| 4. FS4 term-set freeze | **PENDING** — `MODEL.md` does not exist yet; nothing cites it until it does | `MODEL.md` |
| 5. a-posteriori propagation | **PENDING** — NULL and CEILING in flight, DISCOVERED queued behind step 4 | sec. 5 |
| 6. gates and verdicts | **PENDING** | sec. 6 |

---

## 1. Inventory taken before any new run

The lane was resumed after a session compaction. Everything on disk was
inventoried first and nothing was re-run that met the completion rule.

**What the killed lane left:** `PREREGISTRATION.md` and nothing else. The R4
build directory contained one file; there were no case directories, no logs, no
partial targets and no scripts. `/home/ubuntu/closure-data/` contained **no
`r4/` tree at all**.

**`verification/runs/R4_runs/` is not this lane's.** It holds `c1`–`c5`,
`mesh_rung.sh`, `solve_rung.sh`, `run_c3_replicates.py` and Ahmed-body
`snappyHexMesh`/`simpleFoam` logs dated 2026-08-16 — an earlier, unrelated
campaign whose "R4" is a rung label, five days older than this
preregistration. **It was read and left untouched.** No SpaRTA, frozen-RANS or
closure artefact exists anywhere under it.

**Reused rather than re-run:** the FS1/FS2 feature record
(`/home/ubuntu/closure-data/features/`: 40 case `.npz`, `fs2_audit.json`,
`fs2_training_only.json`, `sparta_basis_train.json`) and the validated solver
`sdk/openfoam/sparta/` (`kCorrectiveFrozenFoam`, `libspartaTurbulenceModels.so`
carrying `kOmegaSSTFrozen`, `kOmegaSSTCorrected`, `kOmegaSSTSparta`). This
lane's training-case registry is asserted equal to the FS2 record's at import
(`r4_lib`), so the two cannot drift.

**Two diagnostic probes visible on the box** at
`/home/ubuntu/closure-data/r4/ktestA` and `ktestB`, and three more (`ktest`,
`ktest2`, `ktest3`), are **this lane's own convergence diagnostics**, not target
extractions, and are recorded as such in sec. 2.3. Applying the strict
completion rule to them: `ktestA` has `rc = 0`, an `End` line and a `20000/`
time directory equal to its `endTime`, **but its log says `NOT CONVERGED:
backstop cap reached at iteration 20000`**, so as a frozen extraction it is
**INCOMPLETE**; it is a measurement of non-convergence, which is what it was run
to be. `ktestB` is the same at 5000. Neither feeds any number in this file.

---

## 2. Step 1 — target extraction with `kOmegaSSTFrozen`

### 2.1 What was built

27 training cases (21 hills, 4 ducts, `PHLL10595`, `CBFS13700`), built by
`build_frozen_cases.py` into `/home/ubuntu/closure-data/r4/frozen/<case>/`:
`0/U ← 0/U_LES`, `0/k ← 0/k_LES`, `0/tauij ← 0/tauij_LES`, `0/omega` and
`0/nut` from the shipped baseline's last time directory, `RASModel
kOmegaSSTFrozen`, backstop `endTime 5000` with the settle criterion in the
solver. Only the FoamFile `object` line is rewritten; every value and boundary
condition is the benchmark's own.

**Registered self-check, and it is a self-check (L-218).** The lane's
`PHLL10595` and `CBFS13700` frozen cases were compared with the W2 reproduction
that `PREREGISTRATION` sec. 5 cites as validated:

| | inputs vs `W2_sparta_runs/{ph,cbfs}_frozen` | settle iteration | outputs `bijDelta`, `kDeficit`, `bijData`, `U`, `k`, `omega`, `nut` |
|---|---|---|---|
| `PHLL10595` | `0/{U,k,tauij,omega,nut}` **byte-identical** | 1243, writes 1492 — **the W2 record's own 1492** | **byte-identical** |
| `CBFS13700` | `0/{U,k,tauij,omega,nut}` **byte-identical** | 295, writes 354 — **the W2 record's own 354** | **byte-identical** |

A broken rebuild could not have produced bit-identical fields, so the two cases
that carry the sec. 6 a-posteriori gate rest on a reproduction, not on a
re-implementation.

### 2.2 Completion inventory — the STRICT COMPLETION RULE applied to all 27

Applied as: recorded `rc = 0`; an `End` line in the log; the last time directory
equal to the iteration the solver says it wrote at; every required field present
in it and newer than `0/`; the solver's own settle criterion met and its
verification-window drift marked `[SETTLED]`; **and** `omega` never bounded
before the write (sec. 2.3 explains why that sixth condition had to be added).

| case | family | cells | verdict | settle iteration | L2(R) drift over verification iters | reason if incomplete |
|---|---|---|---|---|---|---|
| `alpha_05_10071_3036` | hills | — | INCOMPLETE | — | — | log says NOT CONVERGED (backstop cap reached) |
| `alpha_05_4071_3036` | hills | — | INCOMPLETE | — | — | log says NOT CONVERGED (backstop cap reached) |
| `alpha_05_7071_2024` | hills | — | INCOMPLETE | 51 | 0% | omega bounded on 1 iterations before the write (clipped, not settled) |
| `alpha_05_7071_3036` | hills | — | INCOMPLETE | — | — | log says NOT CONVERGED (backstop cap reached) |
| `alpha_05_7071_4048` | hills | — | INCOMPLETE | 51 | 0% | omega bounded on 1 iterations before the write (clipped, not settled) |
| `alpha_075` | hills | — | INCOMPLETE | — | — | log says NOT CONVERGED (backstop cap reached) |
| `alpha_10_12000_2024` | hills | — | INCOMPLETE | — | — | log says NOT CONVERGED (backstop cap reached) |
| `alpha_10_12000_3036` | hills | — | INCOMPLETE | — | — | log says NOT CONVERGED (backstop cap reached) |
| `alpha_10_12000_4048` | hills | 15600 | **COMPLETE** | 1362 | 9.62e-06% |  |
| `alpha_10_6000_2024` | hills | — | INCOMPLETE | — | — | log says NOT CONVERGED (backstop cap reached) |
| `alpha_10_6000_3036` | hills | — | INCOMPLETE | — | — | log says NOT CONVERGED (backstop cap reached) |
| `alpha_10_6000_4048` | hills | — | INCOMPLETE | — | — | log says NOT CONVERGED (backstop cap reached) |
| `alpha_10_9000_2024` | hills | — | INCOMPLETE | — | — | log says NOT CONVERGED (backstop cap reached) |
| `alpha_10_9000_3036` | hills | — | INCOMPLETE | — | — | log says NOT CONVERGED (backstop cap reached) |
| `alpha_10_9000_4048` | hills | — | INCOMPLETE | — | — | log says NOT CONVERGED (backstop cap reached) |
| `alpha_125` | hills | 15600 | **COMPLETE** | 1391 | 1.18e-05% |  |
| `alpha_15_10929_2024` | hills | — | INCOMPLETE | — | — | log says NOT CONVERGED (backstop cap reached) |
| `alpha_15_10929_3036` | hills | 15600 | **COMPLETE** | 1346 | 8.92e-06% |  |
| `alpha_15_10929_4048` | hills | 15600 | **COMPLETE** | 1382 | 4.02e-06% |  |
| `alpha_15_13929_3036` | hills | 15600 | **COMPLETE** | 1174 | 7.76e-06% |  |
| `alpha_15_7929_3036` | hills | 15600 | **COMPLETE** | 1625 | 1.36e-05% |  |
| `AR_1_Ret_180` | ducts | 2209 | **COMPLETE** | 133 | 1.76e-06% |  |
| `AR_3_Ret_180` | ducts | 6627 | **COMPLETE** | 392 | 8.88e-05% |  |
| `AR_5_Ret_180` | ducts | 11045 | **COMPLETE** | 694 | 0.00016% |  |
| `AR_10_Ret_180` | ducts | 22090 | **COMPLETE** | 1378 | 0.000209% |  |
| `PHLL10595` | PHLL10595 | 15600 | **COMPLETE** | 1243 | 9.91e-06% |  |
| `CBFS13700` | CBFS13700 | 21000 | **COMPLETE** | 295 | 0% |  |

**12 of 27 COMPLETE: 6 hills, 4 ducts, `PHLL10595`, `CBFS13700` — 172,171 cells.
All four training families are represented, so every cross-family fold and every
sec. 6 gate remains executable.** The 15 incomplete hills were re-run once under
the rule and are reported incomplete, not silently dropped.

### 2.3 Why 15 hills do not converge — diagnosed, not worked around

The failure has two faces and one cause.

**Face 1, 13 hills: a limit cycle at the backstop.** `omega` initial residual
plateaus and the maximum relative change per iteration freezes at a constant to
fifteen significant figures — on `alpha_10_9000_3036`, `initRes = 4.216561e-04`
and `max rel domega = 0.105158858322751` at iteration 4750, 4800, 4850, 4900,
4950 and 5000. `omega` is driven negative and `bound(omega, omegaMin)` replaces
every negative cell with a local average **on every one of the 5000
iterations**. The six converging hills bound `omega` **zero** times.

**Face 2, 2 hills: a false convergence that the completion rule had to be
extended to catch.** `alpha_05_7071_2024` and `alpha_05_7071_4048` report
`CONVERGED (settle criterion) at iteration 51` with an `L2(R)` drift of
**exactly 0.0**. Their first `omega` solve has an initial residual of 0.933 and
is followed by `bounding omega, min: -193215225.4 max: 762695.6 average:
-50081.6`; after that clip `omega initRes = 9.25840338e-18` and
`max rel domega = 0` at every subsequent iteration. **The field stopped changing
because it had been clipped flat, and a settle criterion that measures change
cannot tell that from convergence.** This is the L-221 shape exactly: a failure
that returns a plausible-looking field. The sixth completion condition
("`omega` bounded before the write ⇒ INCOMPLETE") was added to
`r4_lib.frozen_complete` **after** measuring it, and it is what reclassifies
these two.

**Three repairs were tested and all three failed — recorded so no one retries
them.** Costed and run as diagnostics on `alpha_10_9000_3036`:

| probe | intervention | result |
|---|---|---|
| `ktest` | every `k_LES ≤ 0` cell floored to `1e-4 × mean k_LES` (`_common/of_read.anisotropy`'s own convention) with `tauij` made isotropic there, so `bijData = 0` | still NOT CONVERGED at 5000; residual slightly **worse** |
| `ktestB` | the same at `1e-2 × mean k_LES`, **plus** an inserted `div(phi,omega) Gauss linearUpwind grad(U)` | still NOT CONVERGED at 5000 |
| `ktest2` | the `div(phi,omega)` insertion alone | still NOT CONVERGED, `omega` bounded on all 5000 iterations |
| `ktestA` | backstop raised 5000 → **20000**, nothing else changed | **NOT CONVERGED at 20000**, `initRes = 4.21656145422043e-04` and `max rel domega = 0.105158858322751` — *identical to fifteen figures to the value at iteration 5000*. **Extending the cap is definitively useless; this is a limit cycle, not slow convergence.** |

Two facts were measured along the way and both belong on the record.

* **Every one of the 21 hills carries cells with `k_LES ≤ 0`** — 7 to 51 cells,
  0.045 % to 0.33 % of the mesh, minimum `k_LES` from −2.5e-04 to −6.8e-03. The
  ducts, `PHLL10595` and `CBFS13700` carry **none**. It is an interpolation
  artefact of the LES data onto the RANS mesh, already named in
  `_common/of_read.anisotropy`'s docstring. It is **not** a sufficient cause:
  `alpha_10_12000_4048` has 16 such cells and converges, `alpha_10_9000_3036`
  has 15 and does not.
* **The 21 hills are the only benchmark family whose `system/fvSchemes` declares
  no `div(phi,omega)`** — it falls through to `default Gauss linear`, unbounded
  central differencing on the `omega` convection term, while `PHLL10595` uses
  `bounded Gauss linearUpwind grad(U)`, `CBFS13700` uses
  `Gauss linearUpwind grad(U)` and the ducts use
  `bounded Gauss linearUpwind limited`. A defect in the shipped hill cases, and
  repairing it alone does not fix the extraction (`ktest2`).

**The mechanism, stated as far as it was measured.** The frozen `omega` equation
(`kOmegaSSTFrozen.C`) carries the explicit source
`gamma*(PkLim + Rterm)/max(nut, 1e-12)`. `nut` is recomputed each iteration from
the frozen `k_LES`, and the baseline hills carry `nut` down to **5.55e-12**, so
the source is amplified by up to 1e11 where the numerator is not simultaneously
small. That is where `omega` goes negative. **What this diagnosis cannot see:**
whether a bounded, positivity-preserving discretisation of that source would
converge, because none was written — writing one would change the extraction
operator that `PREREGISTRATION` sec. 5 registers as the W2-validated path, and
that is a new preregistration, not a repair inside this one.

---

## 3. Step 2 — the candidate library, and a correction to the preregistration's own premise

### 3.1 The library, as registered

`assemble_dataset.py` builds Schmelzer's ansatz on the frozen fields of the 12
complete cases: `tau = 1/omega`, `A_ij = d_j U_i` from OpenFOAM's own written
`grad(U)` on the frozen time directory, `S = (tau/2)(A+A^T)`,
`Omega = (tau/2)(A-A^T)`, `I1 = S_mn S_nm`, `I2 = Omega_mn Omega_nm <= 0`, and
`T1 = S`, `T2 = SW-WS`, `T3 = S^2 - I tr(S^2)/3`, `T4 = Omega^2 - I tr(Omega^2)/3`.
Exponent grid `p,q in {0,1,2}, p+q <= 2` (sec. 2.4) — six monomials, so **18
candidates on the T1–T3 library of sec. 1 and 24 on the T1–T4 library of
sec. 2.1**. `R` candidates carry the `2k` factor of Eq. 12 inside the column,
so a fitted coefficient is the number `RTerms` takes unchanged.

**Sec. 2.2 honoured and empty, asserted rather than assumed.** The 12
pooled-training dead features of the 110-feature audit (`trW2SWS2`, `trW2SPS2`,
`trW2SKS2`, `trP2KS2`, `trK2PS2`, `trWPSKS2`, each in both normalisation
variants) are Wu–Xiao–Paterson invariants of `{S, W, A_p, A_k}`, not members of
the `I1^p I2^q T_n` ansatz. `fs3_select.load` asserts the intersection is empty
and would raise if one ever entered.

**Sec. 2.3 honoured by construction.** `nu` is never read by any file in this
lane's fit path. `tau = 1/omega` carries no molecular viscosity; the
Durbin-bounded block-B variant is not built.

### 3.2 The duct degeneracy of sec. 2.1 is a property of the RANS field, not of the field this lane fits

`PREREGISTRATION` sec. 2.1 records, on `AR_1_Ret_180`, that `T4 = -T3` to
machine precision (`||T3+T4||/||T3||` median **2.74e-17**, p99 **6.41e-16**, max
**7.08e-15**), that `I2 = -I1` identically (median **0.000e+00**), and that the
per-cell rank of `{T1..T4}` is **exactly 3.000**, 4,000 of 4,000 sampled cells
at rank 3.

**Those numbers are reproduced here exactly** — median **2.7398e-17**, p99
**6.4084e-16**, max **7.0760e-15**, `|I1+I2|/|I1|` median **0.000e+00**, rank
**3.000** on all 2,209 cells — which fixes the convention and confirms this
lane's `T4` is the preregistration's `T4`. They are reproduced **on the
baseline RANS field**.

**On the frozen fields the SpaRTA regression actually uses, the degeneracy is
gone:**

| `AR_1_Ret_180`, all 2,209 cells | `\|\|T3+T4\|\|/\|\|T3\|\|` median | p99 | `\|I1+I2\|/\|I1\|` median | per-cell rank of `{T1..T4}` |
|---|---|---|---|---|
| baseline RANS (`334/U`, the FS2 measurement) | **2.7398e-17** | 6.4084e-16 | **0.000e+00** | **3.000** (2209 of 2209 at rank 3) |
| frozen (`U = U_LES`), OpenFOAM `grad(U)` | **1.2779e-02** | 4.6889e-01 | 7.0405e-05 | **3.965** (2132 of 2209 at rank 4) |
| frozen, finite-difference gradient | 1.2819e-02 | 4.7060e-01 | 7.1543e-05 | 3.966 |

Per-cell rank on the frozen fields of all four training ducts: **3.965, 3.977,
3.978, 3.977**.

The cause is not numerical. A fully developed duct's *linear-eddy-viscosity*
mean flow has only `dU/dy` and `dU/dz`, so `S^2 + Omega^2` is isotropic and the
deviatoric parts cancel exactly — which is the same fact L-219 states from the
other side, that a linear EVM produces `b_23` and `b_22 - b_33` identically
zero. **The DNS mean flow has secondary motion**, so the in-plane gradients are
not zero and the cancellation does not occur.

**Effect on the registered rule: none, and the rule is not amended.** Sec. 2.1
excludes `T4` and `I2` only "on any fit whose training set is **ducts only**".
This lane runs no ducts-only fit, so both are retained exactly as registered,
and the condition number of every fitted design matrix is reported per fit
(sec. 4). What changes is the *premise*: the exclusion was justified by an
exact collinearity that does not exist in the data being fitted. The
measurement is reported because the rule it justifies is one a future lane
might apply to a ducts-only fit, and it would be applying it for a reason that
is false on frozen fields.

### 3.3 The fit mask, and a trap inside it

`bound(k, kMin)` inside `kOmegaSSTFrozen` replaces every non-positive `k_LES`
cell with a small **positive** number, so the `k` field the solver *writes*
cannot identify the cells where the LES anisotropy is undefined — and
`b^Delta` there is `O(1e5)` nonsense that a `k > 0` mask on the written field
silently admits. On `alpha_10_12000_4048` that mask left an RMS `||b^Delta||_F`
of **35,478** against ~0.3 on every other case. The mask is therefore taken on
the **shipped** `0/k`: **65 cells of 172,171 (0.038 %)** are excluded, all of
them hills. Counts are in `artefacts/fs3.json` under `cell_accounting`.

### 3.4 `R` is non-dimensionalised per case; `b^Delta` is not

`R` has the dimensions of `k*omega`, and its RMS spans **eight orders of
magnitude** across the training families — **0.0066** on `CBFS13700`,
**0.0346–0.0625** on the hills, **0.0588** on `PHLL10595`, **1.61e+06–1.70e+06**
on the ducts, whose bulk velocity is ~37.5 m/s on a 1 mm half-height. An
unweighted pooled fit on the raw quantity is a duct fit with the other three
families as rounding error.

Each case's `R` rows — target **and** candidates alike — are divided by **one
positive constant**, the case median of `k*omega` on the fitted cells. It is a
physical scale of the same dimensions, computed from the frozen fields and not
from the target, and dividing both sides of a linear system by a constant
leaves every coefficient's value and meaning unchanged. `b^Delta` is already
dimensionless and is not scaled. The preregistration registers cross-family
folds but no weighting; this is recorded as a specification it left open, in
the departures section.

---

## 4. Steps 2–3 — FS3 selection and the FS4 freeze

`fs3_select.py`, four fits (`R` and `b^Delta`, each on the T1–T3 library of
sec. 1 and the T1–T4 library of sec. 2.1), **three seeds each**, folds that are
whole families (leave-one-family-out over hills / ducts / `PHLL10595` /
`CBFS13700`), never random cells. Output: `artefacts/fs3.json`. Term sets frozen
in **`MODEL.md`** / `MODEL.json` before the propagation cases whose results are
reported in sec. 5 were built.

**An earlier `b^Delta` fit was withdrawn before any a-posteriori number was
read** — departure D-6, and sec. 4.4 below, because how it was caught is the
most useful thing in this section.

### 4.1 The three registered methods, and they disagree

Spearman rank correlation between the three FS3 rankings over the whole
candidate set (with 18–24 candidates the registered "top-20" *is* the entire
library, so the correlation is over all of it):

| fit | MI vs perm | MI vs elastic net | perm vs elastic net |
|---|---|---|---|
| `R`, T1–T3 | **0.192** | 0.675 | **0.060** |
| `R`, T1–T4 | **−0.283** | 0.619 | **−0.179** |
| `b^Delta`, T1–T3 | **0.114** | 0.875 | **0.006** |
| `b^Delta`, T1–T4 | **−0.119** | 0.604 | **−0.162** |

Sec. 3 registers the reading in advance: *"three methods agreeing is evidence
and three disagreeing is a finding."* **They disagree.** Permutation importance
on a held-out family is near-orthogonal to mutual information on three of the
four fits and *anti*-correlated on the T1–T4 fits, while mutual information and
the elastic-net path agree moderately to strongly (0.60–0.88). The frozen term
sets rest on the cross-family CV of the elastic-net path; the disagreement is
why the planted-zero control does real work below rather than confirming a
foregone conclusion.

### 4.2 The frozen term sets

Full statement and provenance: **`MODEL.md`**. Every one of the four fits
returned the **same term set at seeds 0, 1 and 2**.

| fit | selected terms | LOFO CV MSE | design cond | planted-zero |
|---|---|---|---|---|
| **`R`, T1–T3 (frozen, propagated)** | `T1`, `I1*T1`, `I2*T1`, `I2^2*T1` | 43.5533 | 653.9 | **PASS** |
| **`b^Delta`, T1–T3 (frozen, propagated)** | `T2`, `I2*T2`, `T3` | **0.0156199** | 7.707 | **PASS** |
| `R`, T1–T4 (registered mixed-family fit) | `T1`, `I1*T1`, `I2^2*T1` | 43.665 | 54.81 | **GATE FAIL** |
| `b^Delta`, T1–T4 (registered mixed-family fit) | `T2`, `I2*T2`, **`T4`** | 0.0158092 | 7.707 | PASS |

Three things in that table are worth stating as results rather than as rows.

**`R` recovers Schmelzer's own candidate set.** The form contains `T1`,
`I1 T1` and `I2 T1` — exactly the three the paper names as "the relevant
candidates to regress `R`" — plus `I2^2 T1`. Its `T1` coefficient is **1.2616**,
inside the span of the three published pure-`T1` coefficients (0.39, 0.93, 1.39)
and closest to the 1.39 of their Eq. 23.

**`b^Delta` activates `T2` and `T3`**, the two tensors the W2 record found as
the sparsest forms on PH (`T2`) and CBFS (`T2` then `T2 + T3`). Its cross-family
error is **0.0156199** against a zero-model **0.0173846** — a 10.2 % reduction,
which is a real but modest hold on the anisotropy correction.

**Sec. 1's solver constraint costs nothing here.** The T1–T3 `b^Delta` model has
a **lower** leave-one-family-out error than the unconstrained T1–T4 model
(0.0156199 against 0.0158092). The two agree exactly on `T2` and `I2*T2` and
differ only in the third term — `+5.0391 T3` against `−6.7275 T4` — which is
consistent, `T4` being close to `−T3` wherever the flow is near two-dimensional.
**So no static-field-injection arm was needed**, and none is claimed: the
registered symbolic route is both available and, on this training set, better.
`build_aposteriori.py` asserts `n in (1,2,3)` before writing any case, so the
silent-`n=4`-evaluates-as-`T3` defect of sec. 1 cannot reach a run from here.

### 4.3 The planted-zero controls, and what they caught

**Two controls, and they are different instruments.**

**(a) The reader control** — CLAUDE.md standing rule 3: *"a zero from a reader
that has not been shown able to see a non-zero is not evidence."* Both scorers
plant `PLANT = 1.234e-03` into a scratch copy of a real field **on disk**, read
it back with the same reader they use for every number they report, and
**refuse (exit 2)** unless it comes back. Measured: the plant is recovered on
**all 15,600 values** of `bijDelta` with a median recovery of **0.001234** and a
worst-case error of **8.31e-11**. The bar is machine epsilon at the largest
value in the field (**4.98e-09** here, the field reaching 2.8e+06 in the
undefined-anisotropy cells sec. 3.3 masks out), not a fixed absolute number —
an absolute 1e-12 bar refuses a perfect reader on arithmetic grounds alone, and
did, before the tolerance was made magnitude-aware. **PASS.**

**(b) The regression control** — two columns whose true coefficient is exactly
zero are appended to every design matrix: a seeded permutation of the candidate
most correlated with the target (identical marginal distribution, no physical
relation) and a seeded Gaussian column at the same RMS. It passes only if
neither enters the selected support, both rank below **every** selected term
under mutual information **and** permutation importance, and both enter the
pure-lasso path **after** every selected term.

Three of the four fits **PASS**. `R` on the T1–T4 library **GATE FAILs**, and
not on a threshold technicality:

| fit | the indicted term | its leave-one-family-out permutation importance | the planted zeros |
|---|---|---|---|
| `R`, T1–T4 | `I2^2*T1` | **−322.2** (rank 18 of 26) | −1.63e−03 (rank 14), −1.84e−03 (rank 15) |

Permuting `I2^2*T1` **improves** held-out error by more than a planted zero
does. A held-out family says that term is worse than noise, and the elastic-net
path selected it anyway. **The frozen, propagated model is the T1–T3 one, whose
control passes** — but the failure is on the record because it is the same
selection machinery, one library wider.

In the passing fits the separation is wide: for `b^Delta` on T1–T3 both planted
zeros rank **last on both** mutual information and permutation importance (18/19
and 18/19 of 20) and enter the lasso path at indices **38 and 60** against 1–11
for the selected terms.

**Reported, not graded.** The cross-family-CV-optimal elastic net is **not a
sparse selector at its own optimum**: on `R`/T1–T3 it retains 15 of 20 columns
*including the permuted planted zero*, at coefficient 6.7e−03. That is a
measurement about the method, and it is why the frozen term set is taken from
the cross-validated **form** search and not from the CV-optimal coefficient
vector.

### 4.4 How the withdrawn fit was caught, and by what

The a-priori gate of sec. 6 is registered as a *gate*. On its first run it acted
as a *detector*: it returned a `b^Delta` model whose error against its own
training target was **larger than predicting zero**, on all four families at
once. A least-squares fit cannot do that — the zero vector is in its feasible
set — so the number was not a result, it was a bug. The cause was a design
matrix reshaped through an intermediate `(cell, candidate, component)` shape,
which put candidate row *r* and target row *r* on different cells.

The fit, the frozen term set built on it, and the 24 propagation arms already
launched from it were **withdrawn**; eight in-flight solver runs were stopped
rather than spend budget computing a model that had been withdrawn, which is
disclosed here rather than presented as a clean run (departure D-6). `R` was
never affected and reproduces **bit for bit** across the fix — same terms, same
`43.5533`, same control verdict — which is what localises the fault to the
tensor stacking.

**The lesson is the one the gate was written for by accident.** A registered
comparison against a *constant* baseline catches an implementation fault that no
internal consistency check in the fitting code would have: the elastic-net path,
the CV, the seeds and the planted-zero control all ran happily on the scrambled
matrix and returned a stable, plausible three-term model at three seeds.

### 4.5 The a-priori gate of sec. 6

> *"The discovered `b^Delta` must beat the TRAIN-MEAN tensor on training-family
> `b_rms`. The train-mean constant beats k-omega SST on 8 of 8 held-out cases
> (`BASELINES.md` sec. 6.4), so SST is not the bar and is not quoted as one.
> Registered: PASS requires the discovered model below train-mean `b_rms` on
> `>= 3` of the 4 training families."*

Measured on the frozen fields, where `b_data = b_lin + b^Delta` holds exactly,
so the model's total anisotropy is `b_lin + b^Delta_model` and the truth is
`b_data`. `b_rms = sqrt(mean_cells ||pred - truth||_F^2)`, the Frobenius
convention of `_common/score_prediction.frob_rms`. Source:
`artefacts/apriori.json`.

| family | **discovered** | train-mean (this lane's cells) | train-mean (shipped, `BASELINES` §6.4) | linear EVM — *reported, not the bar* | `b = 0` | beats train-mean? |
|---|---|---|---|---|---|---|
| hills | **0.229615** | 0.258430 | 0.237551 | 0.297866 | 0.313506 | **YES** |
| ducts | **0.483897** | 0.368713 | 0.423414 | 0.600932 | 0.607160 | no |
| `PHLL10595` | **0.212982** | 0.250098 | 0.223426 | 0.279189 | 0.296993 | **YES** |
| `CBFS13700` | **0.376331** | 0.327658 | 0.337050 | 0.327812 | 0.353319 | no |

**A-PRIORI GATE: 2 of 4 families → GATE FAIL** (the registered bar is 3 of 4).

Read beside the gate, three things the table says:

* The model **beats the linear EVM on three of four families** — hills, ducts
  and `PHLL10595` — and loses to it on `CBFS13700` (0.3763 against 0.3278),
  where it makes the anisotropy *worse than doing nothing*.
* The **ducts are where it fails hardest**: 0.4839 against a constant tensor's
  0.3687. A single constant beats the discovered algebraic model on the family
  whose anisotropy a linear EVM gets structurally, not quantitatively, wrong
  (L-219).
* It beats the *shipped* train-mean constant on the same two families, so the
  verdict does not turn on which train-mean is used.

Charter §2 is explicit that an a-priori score alone is **NOT A RESULT**; the
verdict above is the registered a-priori gate and nothing more. The
a-posteriori gates are sec. 6.

### 4.6 Realisability of the discovered anisotropy, measured a-priori

`PREREGISTRATION` sec. 6 requires realisability of the total `tau` at
`tol = 1e-6` beside the truth's own rate, and **registers no threshold on it** —
a gap this lane records rather than fills, because Charter §4 exists precisely
because `Ling2016_TBNN` reported realisability without gating on it. Measured on
the frozen fields for `b_lin + b^Delta_model` (`artefacts/apriori_realisability.json`):

| case | violating fraction, model | truth's own rate | linear EVM | max `\|\|b^Delta_model\|\|_F` |
|---|---|---|---|---|
| `alpha_10_12000_4048` | 0.00199 | 0.01348 | 0.00000 | **7.559** |
| `alpha_125` | 0.00122 | 0.01385 | 0.00000 | 1.316 |
| `alpha_15_10929_3036` | 0.00083 | 0.01353 | 0.00000 | 1.324 |
| `alpha_15_10929_4048` | 0.00096 | 0.01277 | 0.00000 | 1.009 |
| `alpha_15_13929_3036` | 0.00167 | 0.01386 | 0.00000 | 3.827 |
| `alpha_15_7929_3036` | 0.00077 | 0.01270 | 0.00000 | 1.242 |
| `AR_1_Ret_180` | **0.06790** | 0.00000 | 0.00000 | 0.763 |
| `AR_3_Ret_180` | **0.05704** | 0.00000 | 0.00000 | 0.738 |
| `AR_5_Ret_180` | **0.05197** | 0.00000 | 0.00000 | 0.743 |
| `AR_10_Ret_180` | **0.04423** | 0.00000 | 0.00000 | 0.751 |
| `PHLL10595` | 0.00000 | 0.00000 | 0.00000 | 0.439 |
| `CBFS13700` | **0.19062** | 0.03648 | 0.00000 | **5.948** |

The linear EVM violates on **no** cell of any case; the truth violates on
0–3.6 %; the discovered model violates on up to **19.1 %** of `CBFS13700` and
4.4–6.8 % of every duct, and its `b^Delta` reaches a Frobenius norm of **7.56**
where a realisable anisotropy is bounded near 0.82. **This is the a-priori
statement of what sec. 5 then measures in the solved field.**

### 4.7 IC1 — the number in `RTerms` means what `MODEL.md` says

`kOmegaSSTSparta` writes its construction-time corrections when
`writeInitialCorrections` is on. `ic1_check.py` evaluates the same frozen term
sets from the same `0/` fields in Python, independently of the solver, and
compares. Across all 12 cases the worst relative L2 is **3.969e-12** on
`kDeficit` and **5.078e-13** on `bijDelta` — the ascii round-trip floor.
**PASS.** This is what rules out component-ordering, exponent-mapping,
`2k`-factor and `I2`-sign slips between the two implementations
(`artefacts/ic1_discovered.json`).

