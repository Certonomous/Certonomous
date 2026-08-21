# A6 CRM wing-alone — adjoint feasibility: COSTING AND OPTIONS (nothing run)

**Filed 2026-08-21, Lane A, BEFORE any A6 compute. Zero solver core-minutes spent to date on this
item.** Per the supervisor's instruction this document **costs the work and stops**; it launches
nothing and requests a pick. Nothing filed upstream.

---

## 0. The standing fact this item exists to price

**No adjoint of any kind has ever been attempted on A6.** Executed, not assumed
(`../../S1_A1_A5_A6_HEAD_SETTLEMENT_2026-08-15.md` §3.6): the markers `Main iteration` and
`KSP Residual` — which fire 16–18 times in every log in this archive that actually solves an
adjoint — appear **zero** times in all four A6 logs. The run *did* register
`Global Adjoint States: 5244840` and print `dRdWT Jacobian Free created!`
(`run_model_run1.log:666`), then completed 1000 SIMPLE iterations and exited `End`. So the
matrix-free operator was constructed without distress; nothing downstream of it was ever run.

The record's stated reason for not attempting it is A3's memory evidence, and the label attached to
that reason is **wrong at its source**: `docs/PRODUCT_LIST.md:179` says A3's blocker is
*"conditioning, not memory"* while `:251` calls A6's inherited blocker a *memory wall*. This
document does not inherit either label. It computes the number.

**Case identity, read from the log rather than from any record** (`run_model_run1.log:225-230`):
`Global Cells: 579072`, `Global Faces: 1770408`, `Global Xv: 1838706`, `Undecomposed points:
593865`, **`Global Adjoint States: 5244840`** over 5 registered states (`U, nuTilda, phi, p, T`).
Solver `DARhoSimpleCFoam`, np=4, image `dafoam/opt-packages:latest`, stock IDWarp.

---

## 1. Memory prediction at full size, from the lab's own envelope

Source: `../../ADJOINT_MEMORY_ENVELOPE.json`, option 5 (`scaling-law study (bytes per cell)`),
status **PARTIAL — cross-case envelope only**. Its own caveat is carried, not suppressed:

> Each data point below is a different pre-existing case (different solver, field count, rank count,
> design-variable count). A global bytes/cell constant fit across all of them would overstate
> precision; reported as an honest envelope, not a regression.

| case | cells | solver family | ranks | peak RSS (MiB) | MiB/cell | censored |
|---|---|---|---|---|---|---|
| A1 NACA0012 | 4,032 | incompressible | 2 | 2,185.216 | 0.5420 | no |
| A5 U-Bend | 4,800 | incompressible | 4 | 2,664.448 | 0.5551 | no |
| naca0015 sail coarse | 63,920 | incompressible | 3 | 10,240.0 | 0.1602 | **yes** — hit the 10g cap exactly; true peak higher |
| A3 M6 coarse | 99,840 | **compressible +T** | 4 | 18,421.76 | 0.1845 | no |
| A3 M6 coarse (fill1 variant) | 99,840 | **compressible +T** | 4 | 20,480.0 | 0.2051 | **yes** — censored at 20g |

The compressible points are the right family for A6. Five models, stated so the spread is visible:

| model | basis | rate | predicted peak at 579,072 cells |
|---|---|---|---|
| **M1** average rate, compressible uncensored | 18,421.76 / 99,840 | 0.18451 MiB/cell | **104.3 GiB** |
| **M2** affine, fixed overhead 2,048 MiB | (18,421.76 − 2,048)/99,840 | 0.16400 MiB/cell marginal | **94.7 GiB** |
| **M3** average rate, censored upper variant | 20,480 / 99,840 | 0.20513 MiB/cell | **116.0 GiB** |
| **M4** affine on the censored upper variant | (20,480 − 2,048)/99,840 | 0.18462 MiB/cell marginal | **106.4 GiB** |
| **M5** adjoint-state count, family-independent | A6 = 579,072×6 + 1,770,408 faces = **5,244,840** states exactly; A3-coarse ≈ 899,040 ⇒ ratio 5.83 | — | **105.0 GiB** |
| ~~M6~~ naive small-case rate | 0.542–0.555 MiB/cell from the 4–5k-cell points | — | ~~307–314 GiB~~ **REJECTED**: folds fixed overhead into a per-cell rate, which is why the record itself notes those two points give a nonphysical negative intercept |

The 2,048 MiB overhead in M2/M4 is the Python/OpenMDAO/PETSc/MPI/OpenFOAM runtime floor, read off
the 4–5k-cell points (2,185 and 2,664 MiB), where cell-proportional cost is small.

### 1a. The model is validated against a point it was not fitted on

M2 is checked against A3 rung 3, an independent measurement that is **not** in the envelope JSON:

| | model M2 | measured |
|---|---|---|
| A3 rung 3, 79,560 cells, compressible, np=4 | **14.7 GiB** | **11.65 GiB** (`../../A3_RUNG3_N52_RESULT.md`, Stage 1: *"Peak container usage 11.65 GiB against the 22 GiB cap"*) |

**M2 overpredicts by 1.27×.** That is the direction a feasibility model should err in, and it means
the full-size figure is an upper-ish bound, not an optimistic one. De-biasing by 1.27 still leaves
**74.6 GiB**.

### 1b. Two corroborations that need no extrapolation at all

These do not depend on the fit and are the load-bearing half of the prediction:

1. **A3's fine mesh OOM'd at 399,360 cells at both a 12g and an 18g container cap**, twice, at the
   same pipeline step (`../../A3_onera_m6.md` Stage 3, attempts 1–2). **A6 is 1.45× larger than
   that**, same solver family.
2. **A3's coarse mesh needed ≥18.4–20.5 GiB at 99,840 cells even with every memory lever applied**
   (`ADJOINT_MEMORY_ENVELOPE.json`, option 2). **A6 is 5.80× larger than that.**

### 1c. Prediction, registered

> **PREDICTION P1 (memory): the A6 adjoint at 579,072 cells is BLOCKED by memory on this box.**
> Predicted peak RSS **95–116 GiB** (74.6 GiB after de-biasing M2), against a **30 GiB** machine
> with ~29 GiB available and a team cap that leaves this lane realistically ≤ 20 GiB while Lane B
> works. That is a shortfall of **3.2×–5.8×**, and the two corroborations in §1b bracket it without
> any extrapolation.
>
> **Falsifier:** a measured peak RSS below 25 GiB on a full-size A6 adjoint. If that happened, both
> the envelope and both corroborations would be wrong together, and the envelope's PARTIAL status
> would be the thing to fix.

> **PREDICTION P2 (conditioning): even with unlimited memory, the A6 adjoint at 579,072 cells would
> not converge.** `DARhoSimpleCFoam` — **the same solver** — stagnates at **79,560 cells** with
> memory comfortable (11.65 of 22 GiB) and reason −3 after a 1.31× residual reduction over 4,000
> iterations (`../../A3_RUNG3_N52_RESULT.md`). A6 at full size is **7.3×** the largest rung that
> converges (42,120) and **7.28×** the rung that stagnates. Memory is not the only blocker and is
> arguably not the first one.
>
> **Falsifier:** a converged (`PetscConvergedReason: 2`) A6 adjoint at any size above 79,560 cells.

**Conclusion: OPTION A6-1 (full-size adjoint) is predicted BLOCKED on two independent grounds and
is NOT RECOMMENDED for a run.** Note that its *dollar* cost is trivial (~$0.10); what makes it a bad
buy is that it would drive host `MemAvailable` toward the 6 GB safety floor and endanger Lane B's
concurrent work, to demonstrate something two existing measurements already bracket.

---

## 2. Costed options — the supervisor picks, I do not

**Mesh recipe as recorded** (`../../A6_crm_wingbody.md` §1): download `CRM_surfMesh.cgns.tar.gz`
(official DAFoam release asset, `github.com/dafoam/files`) → **one** `cgns_utils coarsen` pass →
`genWingMesh.py` (pyHyp hyperbolic extrusion, **N=53 layers**, `s0=1e-4`,
`marchDist=25*3.758151`) → `plot3dToFoam` → `autoPatch 45` → `createPatch` → `renumberMesh`.
Result 579,072 cells over a **wing patch of 11,136 faces** — and 579,072 / 11,136 = **52 = N−1**
exactly, so the cell count is a clean product of surface faces and layer count. That is what makes
a coarsened ladder cheap and predictable.

**Coarsening handle:** one *additional* `cgns_utils coarsen` pass quarters the surface, 11,136 →
**2,784 faces**. Then cells = 2,784 × (N−1), and N is the only remaining knob — exactly the
structure of A3's own sweep ladder (1,560 surface faces × (N−1): n9→21,840… wait, n15→21,840,
n28→42,120, n52→79,560, i.e. 1,560×14, ×27, ×51).

**Memory column below = M2 with the 1.27× de-bias from §1a applied.** **Core-minutes anchored on
A3's measured ladder**, which is the same solver at the same sizes.

| option | recipe | cells | A3 analogue | predicted peak RSS | predicted core-min | budget w/ contingency | **$** | predicted verdict |
|---|---|---|---|---|---|---|---|---|
| **A6-1** | as-shipped, N=53, 1 coarsen | **579,072** | — (4.7× rung 3) | **95–116 GiB** (74.6 de-biased) | 60–120 before death | — | ~$0.10 | **BLOCKED (memory), and P2 says conditioning too. DO NOT RUN.** |
| **A6-2a** | +1 coarsen, **pyHyp N=9** | **22,272** | rung 1 (21,840) — **PASSED** | **~4.4 GiB** (cap 8g) | mesh 0.5 + primal ~3 + adjoint ~8 + FD ~30 = **~42** | **60** | **$0.051** | **PASS expected** |
| **A6-2b** | +1 coarsen, **pyHyp N=16** | **41,760** | rung 2 (42,120) — **PASSED** | **~6.8 GiB** (cap 10g) | mesh 0.5 + primal ~5 + adjoint ~30 + FD ~35 = **~70** | **110** | **$0.094** | **PASS expected** |
| **A6-2c** | +1 coarsen, **pyHyp N=29** | **77,952** | rung 3 (79,560) — **DIVERGED** | **~11.4 GiB** (cap 16g) | adjoint ~95 to reach the 4000-iteration cap | **130** | **$0.111** | **GATE FAIL expected** — worth buying only as a discriminator, see §2a |
| **A6-3** | run A6-2a **and** A6-2b | 22,272 + 41,760 | rungs 1+2 | ≤7 GiB | ~112 | **170** | **$0.145** | two-rung ladder, both PASS expected |

**Every option on this list is under $0.15. The $25 gate does not bind anywhere on Ladder A.** The
binding constraints are host RAM and the shared box, not money — which is worth saying plainly so
nobody reads the cheap dollar figure on A6-1 as a reason to run it.

### 2a. What A6-2c would buy that A6-2a/2b would not

A6-2a and A6-2b would confirm that CRM behaves like ONERA M6 at sizes where M6 already works —
useful, but largely expected. **A6-2c is the only option on the list that can return a surprise**:
if CRM *converges* at ~78k cells where M6 stagnates at ~79.5k, then the reopened ladder's ceiling is
a property of the M6 case rather than of the solver, and the "structural wall" framing that has been
projected from A3 onto A6 since 2026-07-28 is wrong. If it stagnates, the ceiling is a
`DARhoSimpleCFoam` property and the projection was right for the right reason.
**Recommended pick if only one option is bought: A6-2b, then A6-2c.**

### 2b. Predicted adjoint/FD error band, given A3's behaviour

At the rungs that converge, A3 measured **0.0077%–0.93%** on evaluable components and returned
**NOT EVALUABLE** on its two smallest-|g| components (step-inconsistency 5.29% and 8.20%). The
registered prediction for A6-2a/2b, using the same pre-registered protocol
(`../../A3_FD3_PREREGISTRATION.md` §3–§4 — central FD at h and 2h, noise floor from a repeat
baseline, evaluability at 10× the floor, step-consistency < 1%):

> **PREDICTION P3: on the largest-|g| component of each DV group, adjoint-vs-FD relative error
> < 5% (PASS band), with the smallest-|g| components likely returning NOT EVALUABLE.** Falsifier:
> any evaluable component above 15%, or any sign flip.

**The honest uncertainty in P3, stated because it is the interesting one.** A6 would run on **stock
IDWarp**, so the `getRotationMatrix3d` degenerate-branch defect is fully present, and
`check_totals` evaluates at exactly the undeformed baseline where the guard is guaranteed to fire.
On A1, A2, A5 and the naca0015 sail that defect accounted for **97–99.5%** of the measured
shape-derivative error. **A3's rungs nonetheless pass at 0.0077–0.93% without the patch, and nobody
has explained why.** Either A3's `dObj/dXv` sensitivity field happens to contract weakly with the
discarded rotation term, or the A3 rungs' component selection (patchV, twist, one shape component)
avoided the exposed directions. **If A6-2a/2b return small errors too, that is a second
unexplained instance and should be chased, not banked.** A cheap way to settle it inside the same
arm: run the FD arm once on stock and once with the patched IDWarp mounted — the FD column must be
bit-identical between them, and any movement in the analytic column is the defect's contribution,
measured rather than inferred. Cost: roughly +30 core-min (+$0.026) on top of whichever option is
picked. **Recommended as an add-on to the pick.**

### 2c. The one configuration change that is not optional

Whichever rung is picked, `daOptions` must set **`transonicPCOption: 1`**. Every archived M6 `-5`
ran with `2`, which is dead code for `DARhoSimpleCFoam`
(`../../A3_TPC1_ARM_PREREGISTRATION.md` §2; `DAResidualRhoSimpleCFoam.C:172-176`), and flipping that
single token is what converts double DIVERGED_BREAKDOWN into double `reason 2` at 368/383
iterations. A6's shipped `runScript.py` inherits the tutorial default and must be checked. **An A6
adjoint run that omits this is predicted to return `-5` and would be a wasted arm.**

Two further carry-overs, both cheap and both learned the hard way on this exact case:
`sudo rm -rf processor*` before every invocation; and the Bash tool's own `timeout` parameter set
generously, because a shell-level `timeout` wrapper does **not** bound a foreground `docker run` —
that is what orphaned A6's first attempt and corrupted the `processor*/250/p` checkpoint
(`../../A6_crm_wingbody.md` §2, §5).

---

## 3. What this costing cannot see

1. **The envelope is PARTIAL by its own status field.** Options 3 (more ranks) and 4
   (coarse-adjoint boundary) were never run, and option 5 is a cross-case envelope, not the
   controlled single-geometry sweep it asks for. Two of its five points are censored at a container
   cap. The §1a validation against A3 rung 3 is the only out-of-sample check that exists.
2. **No CRM-specific memory point exists at any size.** Every number in §1 is transferred from
   ONERA M6 and NACA0012/U-bend. CRM's wing-alone topology, its `autoPatch 45` patch structure and
   its FFD/DV count are all different.
3. **The design-variable set for an A6 adjoint has never been defined.** A6 ran `run_model` only;
   there is no FFD box, no `nom_addLocalDV`/`nom_addShapeFunctionDV` call, and no DV count in the
   record. The FD arm's cost scales linearly with the number of components chosen, so the
   core-minute columns above assume A3's 3–4-component protocol and would grow with a wider set.
4. **Coarsening by 4× in surface and ~6× in layers changes the physics that is being verified.** A
   22,272-cell CRM wing will not reproduce the tutorial's CD = 0.02090; that is not what the rung is
   for, and no drag-accuracy claim should be attached to it.
5. **It says nothing about whether the full-size case would converge if the memory existed** beyond
   P2's argument by analogy to a different geometry.

---

## 4. Ledger and request

| item | value |
|---|---|
| solver core-minutes spent by this document | **0.00** |
| dollars spent | **$0.00** |
| containers started | 0 |
| frozen files edited | 0 |
| filed upstream | nothing |

**Request to the supervisor: pick from §2.** My recommendation, stated so it can be overruled:
**A6-2b (41,760 cells, $0.094) with the §2b stock-vs-patched add-on (+$0.026)**, then **A6-2c
($0.111)** only if the ceiling question is worth 130 core-min. **A6-1 should not be run**, and if
the full-size number is wanted for the record, §1's prediction plus the two corroborations in §1b
are a cheaper and safer answer than an OOM on a shared box.
