# MRF_R3 — DRAFT REGISTRATION. **NOT FROZEN. NOTHING HAS LAUNCHED. NO SHA BINDS IT.**

> **STATUS: DRAFT / UNFROZEN. NO COMPUTE HAS RUN UNDER THIS DOCUMENT. NOT A GATE.**
> Drafted by a cfd `lab-lane` 2026-09-12 at the cfd-supervisor's direction. Until a freeze
> commit exists, every gate, threshold, cap and band below is amendable and carries **no
> evidentiary weight** (CLAUDE.md rule 2). **This banner is one block and is struck whole at
> the freeze.** The supervisor's check 4 (pre-registration committed before compute) and
> check 1 (grader diff read as a diff) have **not** been done.

---

## 0. WHY R3 IS A NEW REGISTRATION AND NOT AN EXTENSION OF R2

R2 graded `NOT A RESULT` at 2026-09-12T04:37Z on **two independent limbs**. R3 exists because
**one of those limbs is an instrument defect and the other is not an iteration-count problem
at all** — so neither is reachable by running R2 longer, and R2's own §9 forecloses trying.

| R2 limb | what it was | reachable by a longer run? |
|---|---|---|
| `fine` `NOT_CONVERGED` | the **window-relative** bounding-cascade tell (`nan` = 0, `fpe` = 0, all three levels `PLATEAUED` — cascade is the sole cause) | **Yes, and that is exactly the problem.** It flips at 9,000 iterations with the events on disk unchanged. §A1.14 of the R2 registration discloses it. |
| triple `DIVERGENT` on **both** estimators | settled `e32/e21 = +60.579239`, `p = 8.845670`; raw `e32/e21 = +1.147710`, `p = 0.248048` | **No.** A refinement trend is not an iteration count. |

**And beneath both sits the fact that should drive R3's design:** R2's own record measures
`signal/noise` on the binding difference at **0.445** — the coarse→medium settled difference
(`3.364298e-03`) is **SMALLER than the worst within-level stopping-point range**
(`7.554827e-03`). `MRF_R2_TRIPLE_PRESTATEMENT_2026-09-11.md` **predicted this before `fine`
landed** and the record marks it **UPHELD**.

**A triple cannot be rescued by making its levels quieter in iteration count when its
level-to-level differences are below its own reproducibility noise. R3 attacks the NOISE.**

---

## 1. THE ONE HYPOTHESIS — AND IT IS AN INSTRUMENT HYPOTHESIS, NOT A PHYSICS ONE

**H: the R2 family's reproducibility noise is dominated by an UNCONTROLLED DECOMPOSITION
ARM, and pinning the decomposition collapses it below the level-to-level signal.**

The evidence that motivates H, all of it already on disk and none of it new:

| fact | value | source |
|---|---|---|
| decomposition method, all three levels | **`scotch`** — a **non-deterministic** partitioner | `R2/{coarse,medium,fine}/system/decomposeParDict:3` |
| rank counts across the three compared levels | **2 / 2 / 6** — **MISMATCHED** | same files, `numberOfSubdomains`; `processor*` counts agree |
| measured run-to-run reproducibility floor | **8.274582e-03 relative**, from a **FRESH SCOTCH PARTITION** on the same mesh | `R2/ET8000/FREE_SCATTER_AT_4000.txt` |
| the level that differed in rank count | **`fine` — the level that failed** | census + `DEPARTURES.md` D1 |

`SOLVE_L2/DEPARTURES.md` D1 already names this in the lab's own words: *"MRF R2 was graded
`NOT A RESULT` in part because its three levels ran on 2 / 2 / 6 ranks — an uncontrolled arm
on a non-deterministic scotch partition, where the level that differed in rank count is
exactly the level that failed."*

**H IS UNMEASURED AND IS LABELLED AS A HYPOTHESIS, NOT A DIAGNOSIS.** Nobody has run this
family under a pinned decomposition. §4's precondition gate exists precisely so that H is
**tested before** the family is paid for, not asserted after.

---

## 2. THE THREE CHANGES, AND ONLY THREE

**(1) DETERMINISTIC DECOMPOSITION.** `method scotch` → **`method hierarchical`** with an
explicit `n (nx ny nz)`. Hierarchical is geometric and reproducible: the same mesh and the
same `n` give the same partition every time.

**(2) IDENTICAL RANK COUNT AT ALL THREE LEVELS.** `numberOfSubdomains` **6** at coarse,
medium and fine. Rank count stops being a variable that co-varies with the refinement level.

**(3) A CONVERGENCE CRITERION THAT LENGTHENING THE RUN CANNOT SATISFY.** §3.

**Not changed:** the meshes, the geometry, `Re = 5.0e4`, the solver, the schemes, the
relaxation, the `Np` formula, the band `[4.0, 6.0]`, `Np_ref = 5.0`. **`endTime` STAYS 8000**
— §5.

---

## 3. THE CONVERGENCE CRITERION — **ABSOLUTE WINDOW, NOT RELATIVE**

### 3.1 The defect being repaired

R2's tell: `q = max(n_iters//4, 1)`; `late = #{i > n_iters - q}`; `cascade = late > early`.
**Both edges scale with `n_iters`.** Declaring a longer run slides the window and
re-classifies existing late events as middle. That is how a verdict flips without a solution
improving.

### 3.2 The replacement

> **C1 — BOUNDING QUIESCENCE, ABSOLUTE WINDOW.**
> `W = 2000 iterations, FIXED, independent of endTime.`
> A level is `NOT_CONVERGED` if **any** bounding event occurs in its final `W` iterations.

**Why this cannot be satisfied by lengthening.** The window is a fixed count of iterations
back from the end. Extending a run does **not** move an existing event out of it for free:
the run must actually execute `W` further iterations **without producing a new event**. The
criterion can therefore only be met by genuine quiescence — which is what "converged" is
supposed to mean.

**Applied to the events already on disk, as a control:**

| declared `endTime` | final-`W` window | events inside | C1 |
|---:|---|---:|---|
| 8000 | 6000–8000 | **5** (6335, 6340, 6641, 6642, 7817) | **`NOT_CONVERGED`** — correctly fails, exactly as R2 did |
| 12000 *(events on disk only)* | 10000–12000 | 0 | would pass **only if the run genuinely produces no new event in 10000–12000** |

**The second row is the whole point: C1 makes the answer depend on what the solver does next,
not on where the window lands.**

### 3.3 C1 is STRICTER than R2's tell, and that direction is deliberate

R2's tell tolerated a decaying transient (`late > early`). C1 tolerates none in the final
2000. A strictest reading **can only turn a PASS into a GATE FAIL / NOT A RESULT, never the
reverse** — the same reasoning the cfd-supervisor applied to G-S2 at
`SOLVE_L2/DEPARTURES.md` D3. It is the direction that cannot be accused of having been chosen
to fit an answer.

### 3.4 The limbs C1 does NOT replace

- **S12 (plateau)** is carried **unchanged**. Its window `w = min(max(n//4, 20), 2000)` is
  **already absolute** at `n ≥ 8000` (the cap binds) and does not have the defect.
- **NaN and FPE tells** are carried unchanged.
- **Rule 4 completion** and the **age guard** are carried unchanged.
- **Rule 3 planted control** is carried unchanged — R2's plant (`1.234e-03` into `total_z`,
  read back through the same frozen reader, refusal on failure) passed on all three levels and
  is re-armed here. **A zero from a reader not shown able to see a non-zero is not evidence.**

---

## 4. 🔴 THE PRECONDITION GATE — **THE FLOOR IS MEASURED BEFORE THE FAMILY IS PAID FOR**

**This is the gate that makes R3 worth running rather than a repeat of R2 with tidier
numbers.** It is registered **before** any R3 compute and it fires **before** the medium and
fine levels are launched.

> **G-F1 (PRECONDITION).** Under the pinned `hierarchical` decomposition at 6 ranks, the
> **coarse** level is run **TWICE from `0`**, independently. The relative difference in `Np`
> between the two runs is the **pinned-decomposition reproducibility floor**, `F`.
>
> **The family PROCEEDS only if `F < 0.25 × d21_expected`**, where `d21_expected` is R2's own
> measured coarse→medium settled difference, `3.364298e-03`. **Threshold: `F < 8.41e-04`.**
>
> **If `F ≥ 8.41e-04` the family STOPS at `NOT A RESULT` and the remaining ~6,700 core-min are
> NOT spent.** The finding is then recorded as: *the MRF steady formulation's stopping-point
> reproducibility exceeds its grid signal even under a pinned partition*, which is a real
> result about the formulation and is worth more than a third divergent triple.

**Derivation of the 0.25 factor, fixed here before `F` exists:** a level-to-level difference
must exceed its own noise by a comfortable margin for a Roache order to mean anything. R2
measured `signal/noise = 0.445` and the triple was meaningless. Requiring the floor to be at
most a **quarter** of the binding difference puts `signal/noise ≥ 4`, an order of magnitude
better than R2's and the smallest round factor that clears the failure mode actually observed.

**THE THRESHOLD IS DERIVED FROM R2's ALREADY-PUBLISHED NUMBER AND FROM NOTHING ELSE, AND `F`
DOES NOT YET EXIST.** That is the whole evidentiary content of registering it here.

---

## 5. `endTime` STAYS 8000 — REGISTERED, WITH THE REASON

**No extension. `endTime = 8000` at all three levels, re-run from `0`.**

R2 demonstrated that 8000 is **already sufficient for the plateau limb**: all three levels
read `PLATEAUED`, and `fine`'s only iterative defect was the window-relative cascade. Adding
iterations addresses neither limb of R2's `NOT A RESULT`, and §9 of the R2 registration
forecloses a third extension in terms written before any R2 compute. **R3 spends its
core-minutes on CONTROLLING THE NOISE, not on lengthening the run.**

---

## 6. GATES

| gate | statement | verdict on failure |
|---|---|---|
| **G-F1** | precondition floor, §4 | family **STOPS**, `NOT A RESULT`, remaining spend not incurred |
| **G-C1** | bounding quiescence, absolute `W = 2000`, §3.2, each level | that level `NOT_CONVERGED` → triple `NOT A RESULT` (rule 5 clause 1) |
| **G-S12** | plateau, carried unchanged from R2 | `NOT_PLATEAUED` → `NOT A RESULT` (rule 5 clause 1) |
| **G-T** | Roache triple on the finest three, **BOTH estimators printed, neither quoted alone** | not `CONVERGING` → `NOT A RESULT` (rule 5 clause 2), value and both triples and both orders printed beside it |
| **G-B** | `Np ∈ [4.0, 6.0]`, `Np_ref = 5.0` — **carried BYTE-IDENTICAL from the R2 freeze, NOT re-registered** | `CONVERGING` and inside → `PASS`; `CONVERGING` and outside → `GATE FAIL` |

**The band is not re-registered and its date is not moved.** It was frozen before R2's answer
existed; re-registering it now, with `Np = 4.381719292039071` on disk since 04:37 this
morning, would destroy the only thing a band's freeze is for. **Its anchor remains
un-title-verified and carries the disavowal** — R2 §A1.13, `BLOCKED` on acquisition of
Rushton/Costich/Everett 1950 or Zhou & Kresta.

**GCI at `Fs = 1.25`, and never quoted when the three values are not monotone.**

---

## 7. COST — IN CORE-MINUTES, BEFORE IT RUNS (rule 12)

| stage | ranks | basis | core-min |
|---|---:|---|---:|
| coarse run A (from `0`) | 6 | scaled from fine's measured 0.5138 core-min/it by cell ratio 154,715 / 2,418,780 | **≈ 263** |
| coarse run B (the G-F1 twin) | 6 | identical | **≈ 263** |
| **G-F1 DECIDES HERE — ≈ 526 core-min spent, ~6,700 NOT YET COMMITTED** | | | |
| medium | 6 | cell ratio 601,696 / 2,418,780 | **≈ 1,022** |
| fine | 6 | **MEASURED**: `core_min = 4110.30`, `wall_s = 41103`, `ranks = 6`, rc = 0 | **4,110** |
| **total if G-F1 passes** | | | **≈ 5,658** |
| **total if G-F1 fails** | | | **≈ 526** |

**`cost_basis`:** fine's figure is **MEASURED** from `TRIPLE_R2_RECORD.txt`'s own header; the
coarse and medium figures are **DERIVED** by cell-count scaling from it and are not claimed as
measurements. Dollars at the owner-stated `$0.0513/core-h` — **$4.84 full / $0.45 to the
gate — DERIVED, NOT MEASURED**; this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5). **NO CAP KILLS THIS RUN** (Sanaa 2026-09-12): the figures are
rule-12 predictions scored at completion, and the estimate-versus-actual row is **owed** to
`docs/COST_CALIBRATION.md` at every stage completion.

**The G-F1 split is the point of the cost table: 91 % of the spend is behind a gate that can
refuse it.**

---

## 8. WHAT THIS DRAFT HAS NOT ESTABLISHED

- **That H is true.** Nobody has measured this family's reproducibility under a pinned
  partition. G-F1 exists to find out, and **may well fail.**
- **That `hierarchical` partitions this geometry acceptably.** The MRF rotating zone must not
  be split in a way that degrades the interface. **UNVERIFIED by this lane** — it is a
  precondition on the freeze, not a property claimed here.
- **That a re-run changes R2's verdict.** It does not and cannot: R2 is graded and its
  `NOT A RESULT` stands at the core-minutes it spent. R3 is a **new** rung.
- **Any title verification of the `Np` anchor.** Still `BLOCKED`; the disavowal stands.

*Drafted by a cfd `lab-lane`, 2026-09-12. NOT FROZEN, NOT LAUNCHED, NO SHA BINDS IT.
Submissions parked. No agent's message is Sanaa's consent.*
