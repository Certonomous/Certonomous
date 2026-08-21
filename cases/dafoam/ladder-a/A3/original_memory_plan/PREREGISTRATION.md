# A3 ONERA M6, original rung (399,360 cells), SERIAL: MEMORY PRE-REGISTRATION

**Filed 2026-08-21 ~19:05Z, Lane A, BEFORE any arm is launched — and, as it turns out, before any arm
*can* be launched.** This file exists to discharge Sanaa's condition on the A3 original memory plan:

> **Run ONLY if the predicted serial peak RSS at 399,360 cells is ≤ 24 GiB with margin.
> Otherwise the row stays BLOCKED, with numbers.**

**The prediction is 66.0–93.6 GiB across eight independent constructions. The condition is not met by
a factor of 2.7×–3.9×. NO ARM IS RUN. The row stays BLOCKED.** No compute of any kind was spent on
A3 by this lane; the two container invocations behind §4 were read-only source greps costing seconds.

Nothing filed, sent or registered anywhere. This file edits no frozen record.

---

## 1. What is being predicted, and why serial

A3's original rung is the **399,360-cell** ONERA M6 mesh (6,240 surface faces × 64 pyHyp layers),
`DARhoSimpleCFoam`. Its adjoint is currently **BLOCKED** after eight disclosed mitigations
(`../grading_confirmation/RESULTS.md:57-79`). Those eight are **not repeated here and must not be
re-run** — they are enumerated in §5 purely so the reader can see what is already spent.

**Why serial (np=1) is the configuration predicted.** Mitigation #3 already tried np=4 → np=2 and
made things worse in practice (host `MemAvailable` fell to 1.77 GB). np=1 is the remaining untried
rank count, and it is the one this lane can measure, since the lane cap is 4 cores. **§3 shows it is
not a memory lever at all**, which is the load-bearing new result in this file.

## 2. The measurement base — every point, with its provenance and its defects

| # | case | cells | np | solver | measured peak RSS | source | defect to carry |
|---|---|---|---|---|---|---|---|
| D1 | A3 M6 sweep n15 | 21,840 | 4 | `DARhoSimpleCFoam` | **5,876.6 MiB** (5.739 GiB) | `../../ADJOINT_MEMORY_ENVELOPE.md:423-427` | diverged, `reason −5`; ran with `transonicPCOption 2` (**dead code**, `:608-635`) |
| D2 | A3 M6 sweep n28 | 42,120 | 4 | same | **9,991.9 MiB** (9.758 GiB) | same | same |
| D3 | A3 M6 probe80k | 79,560 | 4 | same | **17,603.8 MiB** (17.191 GiB) | same | same |
| D4 | A3 rung 3 n52 | 79,560 | 4 | same | **11.65 GiB** | `../../A3_RUNG3_N52_RESULT.md:50-51` | `transonicPCOption 1`, `reason −3` |
| **D5** | **A6-2b CRM rung N=16** | **41,760** | **1** | same | **9.787 GiB** | **`../../A6/rung_n16_np1/RESULTS.md` §6.6** (this lane, today) | `rc=0`, adjoint **converged, reason 2** — the only converged point in the set |
| D6 | B3 arm Pβ | 21,000 | 4 | `DASimpleFoam` + **complete LU** | 9.044 GiB | `../../ladder-b/B3/adjoint_unblock_reproduce/RESULTS.md:277` | **EXCLUDED from every model** — see below |

**D5 is new and it is the first np=1 adjoint memory measurement the lab has ever had.** It is also the
first CRM-specific one. It was produced today by the A6 rung and is imported here, not re-run.

**D6 is deliberately excluded from all eight models.** It is `DAFOAM_SUBPC_TYPE=lu`, a complete LU of
each sub-block whose `nnz(L+U)` is **24–28× the matrix's own 13,710,468 nonzeros**
(`../../ladder-b/B3/decomposition_np4/PREREGISTRATION.md:69`). Folding an LU point into an
ILU-based envelope would inflate every prediction and would be an error. It is listed because it is
the second-largest RSS the lab has measured and a reader will otherwise ask why it is missing.

**D3 and D4 disagree by 1.48× at identical cells and identical ranks** (17.19 vs 11.65 GiB), and the
discrepancy is unreconciled anywhere in the record. The likeliest cause is `transonicPCOption` (dead
`2` in D3, live `1` in D4), which changes the assembled `dRdWTPC` sparsity — but that is a hypothesis,
not a measurement. **The band in §3 spans both, deliberately.**

## 3. THE PREDICTION

### 3.1 The new measured fact: rank count is not a memory lever

D5 and D2 are the same solver, the same size class, and 0.9% apart in cells — and differ only in rank
count:

| | cells | np | peak RSS | **MiB per cell** |
|---|---|---|---|---|
| D5 A6-2b CRM | 41,760 | **1** | 10,021.9 MiB | **0.23999** |
| D2 A3 M6 n28 | 42,120 | **4** | 9,991.9 MiB | **0.23722** |

**Ratio np=1 / np=4 = 1.0116.** Serial costs **1.2% more** aggregate memory than 4-way, not less.

**This is a real finding and it should be read with its caveats.** The two points are different
geometries (CRM vs ONERA M6) and different convergence outcomes (D5 converged, D2 diverged at
`reason −5`), so 1.0116 is not a clean isolation of the rank axis. What it does establish, to within
those confounders, is that **np=1 is not a 2×-or-better memory saving**, which is the only thing the
prediction needs. Mechanically that is expected: `useAD.mode` defaults to `"reverse"`, so `dRdWT` is
a matrix-free `MATSHELL` (`DASolver.C:1345-1348`, §4) and the resident cost is the **preconditioner
`dRdWTPC` plus ILU factors plus the Krylov basis** — all of which are partitioned across ranks
without duplication, while going serial removes 3 copies of the Python/PETSc/OpenFOAM runtime and
adds back the halo rows that partitioning duplicated. Those roughly cancel.

**Consequence: the np=4 envelope models apply to np=1 essentially unchanged**, and A3 mitigation #3's
failure to buy anything by dropping 4 → 2 ranks is retrospectively explained rather than merely
recorded.

### 3.2 Eight constructions at 399,360 cells

| model | form | predicted RSS | × the 24 GiB gate |
|---|---|---|---|
| M2 affine (A6 doc) | `2048 + 0.164 × cells` MiB | **65.96 GiB** | 2.7× |
| **N3 D5-anchored power law** | `9.787 GiB × (c/41760)^0.8485` | **66.48 GiB** | 2.8× |
| E1 envelope power law | `1.2125 × cells^0.8485` MiB (`ADJOINT_MEMORY_ENVELOPE.md:432`, R²=0.9992) | **67.01 GiB** | 2.8× |
| M1 rate (A6 doc) | `0.18451 × cells` MiB | **71.96 GiB** | 3.0× |
| M4 affine censored | `2048 + 0.18462 × cells` MiB | **74.00 GiB** | 3.1× |
| **N2 D5-anchored affine** | `2048 + 0.19095 × cells` MiB | **76.47 GiB** | 3.2× |
| M3 rate censored | `0.20513 × cells` MiB | **80.00 GiB** | 3.3× |
| **N1 D5-anchored pure rate** | `0.23999 × cells` MiB | **93.60 GiB** | 3.9× |

> ### **PREDICTED SERIAL PEAK RSS AT 399,360 CELLS: 66.0 – 93.6 GiB. Median 74.0 GiB.**
> **Gate: ≤ 24 GiB with margin. NOT MET — the *lowest* of eight constructions is 2.7× over, and the
> three anchored on the lab's only np=1 measurement (N1/N2/N3) span 66.5–93.6 GiB.**

The three `N` models are new in this file and are the only ones anchored on a **converged, serial,
`rc=0`** adjoint. They bracket the older np=4 models rather than undercutting them.

**Sensitivity, stated so the verdict does not rest on a model choice.** For the gate to be met, the
true value would have to be **≤ 24 GiB**, i.e. **2.7× below the most optimistic model and 3.9× below
the most pessimistic**. No measured point in §2 is off its own model by more than **12.6%** (D5
against M2). A 2.7× model error is roughly **21× larger than the worst error the envelope has ever
exhibited.** The verdict is not sensitive to which model is preferred.

**One number that would change this, stated in advance:** a measured serial peak RSS **below 25 GiB**
on any A3 mesh at or above ~150,000 cells. That would falsify the whole family at once. Nothing in
the record comes close.

### 3.3 The corollary worth having: the largest mesh that WOULD fit

Inverting each model at 24 GiB, np=1:

| model | largest mesh fitting 24 GiB |
|---|---|
| N1 D5-anchored rate | **102,405 cells** |
| N2 D5-anchored affine | 117,981 cells |
| E1 envelope power law | 119,074 cells |
| N3 D5-anchored power law | 120,193 cells |
| M2 affine | 137,366 cells |

**~102,000–137,000 cells.** This is corroborated, not merely computed: A3 mitigation #4 coarsened to
**99,840 cells** — squarely inside that band — and the coloring step **succeeded** there (1,391
colors) before OOM-ing later in GMRES against an **8 GiB** cap. A 99,840-cell mesh needing ≥18.4–20.5
GiB (`../../A6/adjoint_feasibility/PREREGISTRATION.md:76-82`) is exactly what these models predict
and is why an 8 GiB cap could not hold it.

**399,360 cells is 9.56× the D5 rung and ~3.5× the largest mesh that fits.** The gap is structural,
not marginal.

## 4. `daOptions` storage levers — enumerated with in-container citations

Container source root `$R = /home/dafoamuser/dafoam/repos/dafoam`, verified on
`dafoam/opt-packages:latest` and re-checked on `dafoam-idwarp-rot:v1` — **every option below sits at
the identical line number in both images** (same `pyDAFoam.py`, 112,059 bytes, dated Jul 12 12:48).

**The structural fact that governs the whole list.** `useAD.mode` defaults to `"reverse"`
(`$R/dafoam/pyDAFoam.py:426`), which makes `dRdWT` **matrix-free** — it is never assembled:

```
$R/src/adjoint/DASolver/DASolver.C:1345   MatCreateShell(PETSC_COMM_WORLD, localSize, localSize, ..., &dRdWTMF_);
$R/src/adjoint/DASolver/DASolver.C:1348   Info << "dRdWT Jacobian Free created!" << endl;
```

**So the only large adjoint objects resident in RAM are (i) the preconditioner `dRdWTPC`, (ii) its
ILU factors, and (iii) the GMRES Krylov basis.** Every lever below acts on one of those three, and
**the single biggest memory decision in DAFoam is already at its optimal setting by default.** That
is the reason this case has no cheap win left.

| lever | in-container `path:line` (default) | what it does to memory | status |
|---|---|---|---|
| `useAD.mode` | `$R/dafoam/pyDAFoam.py:426` (`"reverse"`) | `reverse` ⇒ `dRdWT` is a `MATSHELL`, never stored | **already optimal; no headroom** |
| `maxResConLv4JacPCMat` | `$R/dafoam/pyDAFoam.py:568` (per-field, all `2` except `phiRes: 1`); consumed `$R/src/adjoint/DASolver/DASolver.C:577`, `:628-635` | sets the stencil width ⇒ **nnz of `dRdWTPC` directly**. Upstream docstring `pyDAFoam.py:565-567`: *"Reducing the connectivity level reduce the memory usage, however, it may slow down the adjoint equation convergence."* | **the lab's only working cut: −29.6%** (`../../ADJOINT_MEMORY_ENVELOPE.md:200-205`) |
| `jacLowerBounds` | `$R/dafoam/pyDAFoam.py:586` (`{"dRdW": 1e-30, "dRdWPC": 1e-30}`); consumed `DASolver.C:1060-1067` | drops PC entries below the bound. Docstring `pyDAFoam.py:558-559`: *"Setting a large lower bound for preconditioner (PC) can help to reduce memory."* Default is effectively off | already exercised with the row above |
| `adjEqnOption.pcFillLevel` | `$R/dafoam/pyDAFoam.py:531` (`1`); consumed `$R/src/adjoint/DALinearEqn/DALinearEqn.C:84-85`, applied `:239` | ILU(k) fill ⇒ stored factor size. Docstring `DALinearEqn.C:59-62`: *"the memory usage generally grows exponetially. We rarely set it more than 2."* | **exhausted — mitigation #6**, 1→0 gave `reason −5` then OOM |
| `adjEqnOption.jacMatReOrdering` | `$R/dafoam/pyDAFoam.py:530` (`"rcm"`); consumed `DALinearEqn.C:82-83`, applied `:238` | docstring `DALinearEqn.C:56-57`: *"re-order the lhs matrix to reduce memory usage. Usually we use nd, rcm, or natural"* — shrinks ILU fill-in | **UNTRIED.** `"nd"` is the untested alternative |
| `adjStateOrdering` | `$R/dafoam/pyDAFoam.py:608` (`"state"`); consumed `$R/src/adjoint/DAIndex/DAIndex.C:211-213`, `:263`, `:569-571`, `:602` | `"state"` vs `"cell"` changes global DOF numbering ⇒ `dRdWTPC` bandwidth ⇒ ILU fill-in and preallocation | **UNTRIED — never varied in any lab run** |
| `adjEqnOption.asmOverlap` | `$R/dafoam/pyDAFoam.py:528` (`1`); consumed `DALinearEqn.C:78-79`, applied `:215-216` | docstring `DALinearEqn.C:50-52`: *"Setting a higher number increases the convergence but significantly increase the memory usage"* — **already at its cheapest value** | no headroom downward; A3 measured 1→2 as 1.062× worse (`../grading_confirmation/RESULTS.md:224`) |
| `adjEqnOption.gmresRestart` | `$R/dafoam/pyDAFoam.py:533` (`1000`); consumed `DALinearEqn.C:74-75`, applied `:146` | Krylov basis = `restart × localVecLen × 8 B` | **exhausted — mitigation #5**, 1000→200 OOM'd at the identical point |
| `adjUseColoring` | `$R/dafoam/pyDAFoam.py:521` (`True`); consumed `$R/src/adjoint/DAJacCon/DAJacCon.C:1946`, `:2765` | `False` drops the coloring graph but costs one color per matrix row (`DAJacCon.C:1953-1959`) | **not viable — `False` crashes reproducibly** (`DAColoring.C:1021`, `ADJOINT_MEMORY_ENVELOPE.md:141-168`) |
| `adjEqnSolMethod` | `$R/dafoam/pyDAFoam.py:334` (`"Krylov"`); `fixedPoint` at `$R/src/adjoint/DASolver/DASimpleFoam/DASimpleFoam.C:216-218` | `fixedPoint` avoids both `dRdWTPC` and the Krylov basis | **NOT AVAILABLE — implemented only in `DASimpleFoam`** (incompressible). A3 is `DARhoSimpleCFoam` |
| `adjPCLag` | `$R/dafoam/pyDAFoam.py:417` (`10000`); consumed `$R/dafoam/mphys/mphys_dafoam.py:513-524` | recompute interval for `dRdWTPC`; default = compute once, keep resident forever | **does not change peak** in either direction |
| `readPCMat` | `$R/dafoam/pyDAFoam.py:547` (`0`); consumed `mphys_dafoam.py:469-471`, `:520-522` | loads `dRdWTPC` from `dRdWTPC.bin` instead of assembling it | **same resident size** — saves assembly time, not memory |
| `transonicPCOption` | `$R/dafoam/pyDAFoam.py:396` (`-1`); live branch `$R/src/adjoint/DAResidual/DAResidualRhoSimpleCFoam.C:173` | `==1` drops `fvm::div(phid,p)` from the PC pressure equation — marginally fewer entries | **primarily a conditioning lever, not a memory one.** May explain the D3/D4 1.48× spread (§2) |
| `writeJacobians` | `$R/dafoam/pyDAFoam.py:506` (`["None"]`); consumed `DASolver.C:1080` | dumps Jacobians to **disk** | costs disk, not RAM |
| `adjPartDerivFDStep` | `$R/dafoam/pyDAFoam.py:390` (`{"State": 1e-6}`); consumed `$R/src/adjoint/DAPartDeriv/DAPartDeriv.C:412` | — | **no memory effect**; accuracy only |

**Three keys that a reader may expect and that DO NOT EXIST in this build**, checked rather than
assumed: **`runLowOrderPrimal4PC`** (zero hits over `$R` in `.py`/`.C`/`.H`); **a standalone `PCMat`
option** (only `readPCMat` and the unsteady `PCMatPrecomputeInterval`/`PCMatUpdateInterval`,
`pyDAFoam.py:403-404`, inert for steady A3); and **`dRdWColoring` as a daOptions key** — it is a
runtime *cache filename*, `$R/src/adjoint/DAJacCon/DAJacCon.C:1943`:
`word fileName = modelType_ + "Coloring" + postFix + "_" + Foam::name(nProcs);`.

Also: **the preconditioner family is hardcoded and not exposed** — `DALinearEqn.C:185`
`PCSetType(MLRMasterPC, PCKSP)`, `:212` `PCSetType(MLRGlobalPC, PCASM)`, `:266-267`
`PCType localPCType = PCILU;`. There is no Jacobi / block-Jacobi / LU switch in `daOptions`, which is
why Lane B had to build a patched image to get complete LU.

**And an upstream comment that corroborates the whole diagnosis**, `$R/src/adjoint/DASolver/DASolver.C:1031-1033`:
`// need to first setup preallocation vectors for the dRdWCon matrix / because directly initializing
the dRdWCon matrix will use too much memory`. **DAFoam's own authors treat the connectivity matrix as
the memory-critical structure** — consistent with A3 mitigations #1 and #2 dying *during adjoint
Jacobian-coloring setup*, not in the linear solve.

**Net lever budget.** Of fifteen keys: one is already optimal by default and dominates everything
(`useAD.mode`); four are exhausted or non-viable (`pcFillLevel`, `gmresRestart`, `asmOverlap`,
`adjUseColoring`); four have no memory effect (`adjPCLag`, `readPCMat`, `writeJacobians`,
`adjPartDerivFDStep`); one is unavailable for this solver (`adjEqnSolMethod`); one already delivered
the only measured cut (`maxResConLv4JacPCMat`, −29.6%, with `jacLowerBounds`). **Two are genuinely
untried: `jacMatReOrdering` (`rcm` → `nd`) and `adjStateOrdering` (`state` → `cell`).**

**Neither can close a 2.7× gap.** Both act on ILU fill-in, the same structure `pcFillLevel` already
addresses; `pcFillLevel` 1→0 — a far more aggressive change than a reordering — did not prevent the
OOM. Even stacking them with the measured −29.6% from `maxResConLv4JacPCMat` gives
**66.0 GiB × 0.704 = 46.4 GiB**, still **1.9× over the gate.** The arithmetic is offered so the
BLOCKED verdict is not mistaken for "nobody looked".

## 5. The eight already-exhausted mitigations — cited, NOT repeated

Full table: `../grading_confirmation/RESULTS.md:57-66`; summary at `:68-69`
(*"Levers exhausted: 2 memory caps (12g, 18g), 2 rank counts (4, 2), 2 mesh coarsenings (4×, 16×),
GMRES restart (1000→200), ILU fill level (1→0)"*). In one line each:

1. fine 399,360, 12g, np=4, no lever — **OOM during adjoint Jacobian-coloring setup**
2. fine 399,360, **18g**, np=4 — **OOM at the identical step**, reproduced after a host reboot
3. fine 399,360, 18g, **np=2** — host `MemAvailable` fell to **1.77 GB**, below the 6 GB floor; killed
4. coarse **99,840**, 8g, np=4 — coloring **succeeded** (1,391 colors), then **OOM in GMRES**
5. coarse 99,840, **`gmresRestart` 1000→200** — **OOM at the identical GMRES point**
6. coarse 99,840, **`pcFillLevel` 1→0** — `reason −5` (DIVERGED_BREAKDOWN), then OOM on `d[aero_residuals]/d[aero_vol_coords]`
7. vcoarse **24,960** — **SEGV during `decomposePar`**, not memory; host had ~20 GB free
8. vcoarse 24,960, retry of #7 — **same SEGV, twice-reproduced**

**None of these is re-run by this file.** §3.1 adds the one thing they left open — the np=1 rate — and
adds it **from a measurement that already exists** (D5), at zero further cost.

The structural reason narrowing the target did not help is on record at `:71-76`: OpenMDAO's
reverse-mode sweep for `of=CD` *"walks every upstream input in the model graph in one backward
pass"*, which in this mphys/DAFoam coupling always includes `aero_vol_coords`, so
`d[state_residuals]/d[vol_coords]` — a **mesh-sized** matrix — is computed even for `wrt=patchV`.
**That is why cell count, and not DV count, sets the memory.** It is also why §3's models are
functions of cells alone.

## 6. VERDICT

> ## **BLOCKED.**
>
> **Predicted serial (np=1) peak RSS at 399,360 cells: 66.0 – 93.6 GiB (median 74.0 GiB), across
> eight independent constructions, three of them anchored on the lab's only converged np=1
> measurement (9.787 GiB at 41,760 cells).**
>
> **Sanaa's gate is ≤ 24 GiB with margin. The most optimistic model is 2.7× over it; the most
> pessimistic is 3.9× over. The largest error any of these models has ever shown against a measured
> point is 12.6%.**
>
> **NO ARM IS RUN. Zero core-min, $0.00 spent on A3 by this lane.**

**What would change the verdict, registered now so a future lane does not have to re-litigate it:**

1. A **measured** serial peak RSS below 25 GiB at ≥150,000 cells on this solver — falsifies the whole
   model family at once.
2. A machine with **≥ 96 GiB** of RAM. The box is 30 GiB total, ~27 GiB available. This is a hardware
   gate, not a software one, and it is the honest summary of the whole item.
3. An `adjEqnSolMethod: fixedPoint` implementation for `DARhoSimpleCFoam` — which would remove
   `dRdWTPC` and the Krylov basis, i.e. essentially all of the resident cost. **It does not exist
   upstream** (`DASimpleFoam.C:216-218` is incompressible-only). This is an upstream feature request,
   not a configuration change, and **nothing is filed upstream.**
4. Reducing the mesh to **≤ ~102,000–137,000 cells** (§3.3) — but that is a different rung, not the
   original memory plan, and A3's sweep has already graded rungs at 21,840 (PASS), 42,120 (PASS) and
   79,560 (GATE FAIL, `reason −3`) cells. **The interesting frontier is between 79,560 and 102,000,
   and it is a conditioning frontier, not a memory one** — the 79,560-cell rung stagnated at 11.65 of
   22 GiB, with memory comfortable. Enlarging the memory budget would not have saved it.

## 7. What this prediction cannot see

1. **It is a prediction, not a measurement.** No A3 arm ran. The band rests on six points, of which
   **four diverged** (`reason −5`), one stagnated (`reason −3`), and **exactly one converged** — D5,
   which is a **different geometry** (CRM, not ONERA M6).
2. **The np=1 rate rests on a single cross-geometry comparison** (§3.1), confounded by geometry and by
   convergence outcome. It is sufficient to exclude a 2×+ serial saving; it is not a clean isolation
   of the rank axis, and it is not offered as one.
3. **The D3/D4 1.48× spread at 79,560 cells is unexplained.** If `transonicPCOption` is the cause, the
   whole envelope — fitted entirely on `transonicPCOption 2` runs (`ADJOINT_MEMORY_ENVELOPE.md:608-635`)
   — may be biased high by up to that factor. **Even the full 1.48× correction leaves 66.0/1.48 =
   44.6 GiB, still 1.9× over the gate**, which is why the verdict is stated as robust; but the
   discrepancy is real and is not resolved here.
4. **A ~26% cross-session RSS methodology gap is disclosed and unresolved upstream of this file**
   (`ADJOINT_MEMORY_ENVELOPE.md:261-273`), and the 2,185.216 MiB point underpinning the 2,048 MiB
   affine floor in M2/M4/N2 sits on the far side of it.
5. **`docker stats` `MemUsage` is a cgroup figure, not `ps` RSS**, and may include reclaimable page
   cache. D5 in particular should be read as an **upper bound** on true RSS. This biases the
   prediction high — in the direction that makes BLOCKED easier to reach — and is disclosed for that
   reason.
6. **The two untried levers were not tried.** §4 argues from their mechanism and from `pcFillLevel`'s
   measured failure that they cannot close a 2.7× gap. That is an argument, not a measurement, and it
   is the weakest link in this file. It would cost ~30 core-min on the 99,840-cell mesh to test —
   **but testing it would not unblock 399,360 cells even if both worked perfectly**, which is why it
   is not proposed.

## 8. Verdict vocabulary

PASS, GATE REACHED, GATE FAIL, NOT A RESULT, BLOCKED, PENDING. **This item's verdict is BLOCKED** —
the arm was never launched, so it is neither a GATE FAIL nor a NOT A RESULT.
