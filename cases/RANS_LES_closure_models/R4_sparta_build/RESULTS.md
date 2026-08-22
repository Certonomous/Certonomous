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

| step | state |
|---|---|
| 1. target extraction (`kOmegaSSTFrozen`) | **done, 12 of 27 training cases COMPLETE** (sec. 2) |
| 2. FS3 library + selection | done (sec. 3) |
| 3. model discovery + FS4 freeze | done (sec. 4, `MODEL.md`) |
| 4. a-posteriori propagation | see sec. 5 |
| 5. gates | see sec. 6 |

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

