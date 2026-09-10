# PREREGISTRATION — R5D, identity-preserving completion of the 15 hills

> **STATUS: DRAFT — UNFROZEN — NOTHING MAY RUN AGAINST IT.**
> This file registers nothing yet: no gate, threshold, cap or label below is
> closed, no sha256 binds anything, and no solver, run directory or queue entry
> is authorised by it. It carries **no freeze stamp and no comparator sha-pin**.
> **The closure-supervisor freezes it** — this document **and** `grade_r5d.py`
> together, in one commit — **after a personal `SUPERVISION_CHARTER.md` §3
> check-1 diff-read** of the grader. Until that act, the lane verdict is
> **PENDING** and no number here is of record.
>
> Nothing has been sent, filed, uploaded, registered, posted or commented
> (CLAUDE.md rules 2, 7). Zero solver compute produced this file.

**Lane:** closure. **Predecessor:** `../R5C_omega_repair/` (GATE FAIL, frozen
comparator sha `58eb99e3`). **Successor option:** R5D of
`../R5C_omega_repair/R5C_SUCCESSOR_OPTIONS_DRAFT.md` §3 — the within-R3,
supervisor-freezable, identity-preserving completion. **Date drafted:**
2026-09-10.

---

## 0. WHY R5D EXISTS, AND WHAT IT INHERITS UNCHANGED FROM R5C

R5C returned **GATE FAIL** governed by its identity gate G1. The successor draft
(§1) diagnoses the breach precisely: of R4's 12 frozen targets, **exactly one**
(`alpha_10_12000_4048`, rel-L2 `kDeficit` **1.1848e-04**) genuinely drifts;
**two** (`alpha_15_10929_4048` **4.4e-9**; `PHLL10595` **6.0e-10**) reproduce R4
to 1e-9/1e-10 and were tripped only by the **miscalibrated G3(d) residual-fall
ratio** (`initRes(1)/initRes(N) ≥ 1e6`; L-515). The one genuine drift is a
**stopping-distance artifact**: the Patankar-split sink damps the outer
iteration more strongly, so R5C's **change-based** settle criterion fired
**509 iterations early**, at a point further from a fixed point that is
**confirmed shared** (RESULTS.md §5.1: 11 of 12 settle at the identical
iteration and agree to 1e-7–1e-11). **Nothing in R5C measured distance to the
fixed point** (RESULTS.md §5.2, §6.2).

R5D changes **exactly one thing** relative to R5C: it **replaces R5C's
convergence ladder** — both the change-based settle criterion and the G3(d)
ratio — with a criterion that bounds **distance to the fixed point** by an
**absolute bar** (§3, item 2). Everything else — the operator, the case set, the
identity gate, the planted-zero control, the completion rule, the "used together
or not at all" partial-outcome discipline — is inherited from R5C's frozen
`PREREGISTRATION.md`. **This is a NEW pre-registration, not an amendment to R5C's
frozen file, which is never edited** (CLAUDE.md rule 6).

**Consequence, registered first (as R5C did).** R4's frozen targets and R5D's
targets are compared **only** through the identity gate at ≤1e-6. R4's artefacts
under `/home/ubuntu/closure-data/r4/` and `cases/.../R4_sparta_build/` are read,
never written. No R5D target is merged into any R4 fit — R5D fits nothing.

---

## 1. SCOPE — what R5D does and must not touch

**Does:** re-extract **all 27** R4 training cases under the **R5C Patankar-split
operator** (item 1), the R5D run additionally saving the per-iteration field
snapshots the distance criterion needs (item 2); then grade identity, distance,
completion and the 15-hill completion count.

**Does not, ever:** fit, select, regularise, propagate, or open a TEST/VALIDATION
case (`r4_lib.assert_no_test_case` is called in code); modify or rebuild R4's
binaries (`libspartaTurbulenceModels.so`, `kCorrectiveFrozenFoam`) or the R5C
binaries; edit any case file of the 27; start C2, A′, or any option Sanaa owns
(§5). **Nothing is sent, filed, uploaded, posted or registered outside this box.**

---

## 2. THE FIVE REGISTERED ITEMS (successor draft §3 R5D)

### Item 1 — The Patankar-split operator, in full, and it IS the R5C operator

R5D uses the **identical** repaired operator R5C built and validated; **no
solver source is written or rebuilt.** In `kOmegaSSTFrozenV2` with
`omegaSourceRepair true` (already compiled to `libspartaFrozenV2.so`, driven by
`kCorrectiveFrozenFoamV2`, both under `sdk/openfoam/sparta/` — confirmed present
on disk, R5C RESULTS.md §10):

```
S     = alpha()*rho()*gamma*(PkLim + Rterm)/nutBounded         (unchanged)
Spos  = max(S, 0)      -> added explicitly, at its exact value
Sneg  = min(S, 0)      -> added as  - fvm::SuSp( -Sneg/max(omega(), omegaMin_), omega )
```

so the right-hand side is
```
==  Spos
  - fvm::SuSp( -Sneg/max(omega(), omegaMin_), omega )
  - fvm::SuSp((2.0/3.0)*alpha()*rho()*gamma*divU, omega)
  - fvm::Sp(alpha()*rho()*beta*omega(), omega)
  - fvm::SuSp(alpha()*rho()*(F1() - 1)*CDkOmega()/omega(), omega)
```

**Registered fixed-point identity (the reason the identity gate is a gate, not a
hope):** at a fixed point `omega_prev == omega`, so `Spos + (Sneg/omega)*omega =
Spos + Sneg = S` exactly. The repaired operator has the legacy operator's fixed
point in exact arithmetic — the split changes *which part of the source sits on
the diagonal*, i.e. the iteration path, not the answer. This identity was
**confirmed, not falsified**, by R5C (RESULTS.md §5.1, §5.3).

**The only change R5D makes to the run** (a diagnostic addition that touches no
solved field): the driver writes the last **`DFP_KMIN+2` = 5** consecutive
outer-iteration fields of `omega`, `kDeficit` and `bijDelta` to
`<case>/dfpSnaps/<field>_<iter>`, so the distance criterion (item 2) can measure
a geometric contraction. R5C saved only `omegaHistory.csv` scalar summaries and
a single final time directory — **it saved no field snapshots** — so this is new
run output, and the distance measurement is **compute-gated to the held R5D
run**. If R5D reuses the R5C driver unchanged (no snapshot writer), the snapshot
sequence is produced instead by re-solving from the written field and capturing
the last 5 iterates; either mechanism is registered as acceptable provided the
snapshots are consecutive outer iterates ending at the write iteration. **The
grader fabricates no distance when the snapshots are absent — it returns
PENDING** (`grade_r5d.py:load_snapshots`).

### Item 2 — The distance-to-fixed-point convergence criterion (G-DFP)

**Replaces** R5C's change-based settle criterion **and** the miscalibrated
G3(d) ratio (L-235, L-243, L-515). Registered definition, implemented in
`grade_r5d.py:distance_to_fixed_point`:

Let `f_0 … f_N` be the consecutive outer-iteration snapshots of a target field
(oldest→newest, `N+1 ≥ DFP_KMIN+2 = 5`). Define
```
s_k   = ||f_k - f_{k-1}||_2                      (absolute field-space step)
r_k   = s_k / s_{k-1}                             (measured local contraction factor)
rho   = max(r_k) over the last DFP_KMIN=3 ratios  (conservative rate)
D     = s_N / (1 - rho)                            (tail of a geometric series)
d_rel = D / ||f_N||_2                              (relative distance to fixed point)
```

**A run is CONVERGED-TO-FIXED-POINT iff ALL hold:**
- **(A)** `f_N` is **not spatially uniform**: `std(f_N)/mean|f_N| ≥ DFP_CV_FLOOR
  = 1e-6`. A clipped-flat field fails here (L-235).
- **(B)** the last 3 ratios classify **CONVERGING**: every `r_k ∈ (0,1)` and
  `max(r_k)/min(r_k) ≤ DFP_RATIO_STAB = 4`. A step that collapses to exactly 0
  (a cliff/clip), a stall (`r→1`), divergence (`r>1`), or ratios too erratic for
  the geometric model → **NOT A RESULT**, no distance quoted (rule 5).
- **(C)** `d_rel ≤ DFP_STAR_TARGET = 1e-7` — an **ABSOLUTE bar, not a ratio**.

**What the bound is measured against, and why 1e-7.** The distance is measured
against the run's **own fixed point**, estimated by the geometric tail of the
outer iteration's steps — no external reference is needed. The bar
`DFP_STAR_TARGET = 1e-7` is set **one order below the identity bar IDENT_TOL =
1e-6** and is applied to the **target fields `kDeficit` and `bijDelta`
themselves** (the very quantities the identity gate compares), so a run that
clears G-DFP is provably within the identity bar of its fixed-point target. A
companion diagnostic bar on `omega` (`DFP_STAR_OMEGA = 1e-6`) is **reported, not
gated**.

**Why this defeats the R5C failure.** A strongly-damped iteration has `rho`
close to 1, so even a tiny per-iteration step `s_N` implies a **large** tail
`D = s_N/(1-rho)` — exactly the 509-iteration-early stop R5C could not see. The
selftest exercises this: `rho=0.999`, `d_rel=9.2e-2 ≫ 1e-7` → not converged,
while a genuine `rho=0.5` contraction gives `d_rel=3.8e-13` → CONVERGED.

**On-disk data.** G-DFP needs the per-iteration snapshot sequence of item 1
(**held R5D run produces it**). Everything else the grader reads —
`omegaHistory.csv`, `log.frozen`, the final time directory — already exists in
the R5C-era layout. **No field-space distance can be, or is, computed from R5C's
saved data alone.**

**Roache-triple awareness (rule 5).** `grade_r5d.py:classify_sequence` labels the
iterate step-ratio window CONVERGING / STAGNANT / DIVERGENT / OSCILLATORY; only
CONVERGING may quote a distance, and any other label is NOT A RESULT — the same
discipline as a grid triple, carried onto the iterate axis. R5D is a single-mesh
re-extraction (as R5C was), so grid-refinement Roache triples are out of scope;
the iterate-convergence classification carries the rule-5 discipline here.

### Item 3 — The identity gate, re-registered on R4's frozen 12 at ≤1e-6

**Population:** R4's 12 COMPLETE cases (`../R4_sparta_build/artefacts/
frozen_inventory.json`, `complete==true`). **Quantity:** for each case and each
`f ∈ {kDeficit, bijDelta}`, `e(f) = ||f_R5D − f_R4||_2 / ||f_R4||_2`.
**THRESHOLD: `max` over the 12 cases and both fields ≤ 1e-6** (`IDENT_TOL`,
`grade_r5d.py:gate_identity`). Also **reported, not gated:** the same `e(f)`
against 1e-9 and 1e-12 (VERIFICATION §2a).

**Gates BEFORE the repaired run is trusted (as R5C's G2 passed 14/14):**
- **Fixed-point / W2 byte-identity** (`grade_r5d.py:gate_w2`): the
  `omegaSourceRepair false` legacy branch reproduces the W2 record byte-for-byte
  — settle at **1492**/`ph`, **354**/`cbfs`, and **14 of 14** sha256 field
  matches. A build whose legacy branch differs cannot reproduce 14/14; this
  proves the operator is not a new solver before any repaired number is read.
- **Switch-active control** (inherited from R5C's G1c): `omegaSourceRepair`
  reads `true` and `nNegSourceCells > 0` on ≥1 iteration of each of the 27 runs,
  or the repair was a silent no-op → NOT A RESULT (the L-221 shape).

### Item 4 — Planted-zero control + strict rule-4 completion

**Planted-zero (G0), runs FIRST** (`grade_r5d.py:gate_g0`): plant
`PLANT = 1.234e-03` into cell 0 of a scratch copy of one R5D `kDeficit` field;
the numeric reader must recover `PLANT/‖f‖₂` to within a **PLANT-RELATIVE**
tolerance `PLANT_REL_TOL = 1e-6` (L-508: relative to the plant, never a bare
absolute epsilon tighter than a donor ULP), and the byte reader must report
DIFFERS; else **REFUSE (exit 2)**. The selftest donor is O(10)–O(100) (mean
57.8), matching the real population's magnitude per L-508, so the live predicate
and the fixture agree. This is distinct from the flat-mode control of item 2.

**Strict rule-4 completion** (`grade_r5d.py:completion_rule4`): reuses
`r4_lib.frozen_complete` **UNMODIFIED** — the same six conditions R4 and R5C were
graded by (rc=0; `End`; no `NOT CONVERGED`; last time == the solver's write
iteration; the eight fields present and each newer than `0/` — the age guard;
`[SETTLED]`; zero `bounding omega` before the write) — and **adds the rule-4
clause-5 ExecutionTime-count clause** on top: `n_exec == write_iter`. The frozen
extraction breaks out at its settle iteration and calls `writeNow()`, so
`endTime` is only a backstop cap and `deltaT == 1`; for this unit-step,
adaptive-write family clause-5's `n_exec == round(endTime/deltaT)` maps to
`n_exec == write_iter` (the total outer iterations executed). A guard refuses a
destination already holding `0/` or a numeric time directory.

### Item 5 — Registered rule for the partial outcome

The 27 R5D targets are **one set under one operator**, used **together or not at
all**; a subset of hills is never spliced into R4's 12. Let **M** = the number
of R4's 15 INCOMPLETE hills that are, under R5D, **COMPLETE** (§ item 4) **AND**
**CONVERGED** under G-DFP (§ item 2). Registered ladder (inherited from R5C G4):

| M | verdict |
|---|---|
| **M ≥ 13** | **PASS** |
| **1 ≤ M ≤ 12** | **GATE REACHED** |
| **M = 0** | **GATE FAIL** |

Under GATE REACHED the hills family is still incomplete, no enlarged-dataset
claim is licensed, and whether any R5D target is ever *used* (in A′, C2, anything)
is a separate, later, separately pre-registered decision **not taken by this
lane.**

---

## 3. GATE ORDER AND HOW THEY COMBINE (registered)

Graded in this order:
1. **G0 planted-zero fails** → **NOT A RESULT** (the reader is not evidence). Stop.
2. **Fixed-point/W2 byte-identity fails, or switch-active fails** → **GATE FAIL**
   (the comparison base or the repair is void). Stop.
3. **Identity gate (item 3) fails** → **GATE FAIL**. R4's 12 stand; the 15 remain
   INCOMPLETE; R5D targets feed nothing. Stop.
4. **G0, byte-identity, switch, identity all pass** → the lane verdict is item 5's
   **M-ladder verdict**, with **G-DFP** applied case by case inside it (a hill
   counts toward M only if it is COMPLETE and G-DFP-CONVERGED).
5. Any flat/clipped/damped shape observed by G-DFP → that case is **NOT A RESULT**
   and does not count toward M (never converts a GATE FAIL into a PASS).
6. Cap reached before grading → **BLOCKED**.

### THE NOT-A-RESULT / ESCALATION BRANCH (registered)

**If, under G-DFP, `alpha_10_12000_4048` (or any frozen-12 target) still exceeds
the identity bar `IDENT_TOL = 1e-6`**, the drift is **operator-level, not
stopping-distance**: hill-completion and frozen-12 identity are then in genuine
structural tension, **R5D is GATE FAIL**, and the successor question **escalates
to C2 — a Sanaa call** (re-baselining on the R5C operator voids R4's frozen
reference frame; successor draft §4). The supervisor can freeze R5D alone; the
supervisor **cannot** pre-commit C2 on R5D's behalf. This is the honest fork §2
of the successor draft says R5D must be pre-registered to resolve either way.

---

## 4. COMPUTE — costed before launch (rule 12)

**Rate `$0.0513/core-h`, c7a.4xlarge, owner-stated 2026-08-21/22,
reported-by-owner and NOT measured** (`COMPUTE_BUDGET_CHARTER.md` §5). The box
cannot read its own billing; every dollar figure is **derived, not measured.**

| item | estimate | basis |
|---|---|---|
| 27-case repaired re-extraction (with snapshot writes) | **0.184 core-h** | R5C's registered analogue; R5C actually spent **0.140 core-h measured** on 29 runs (RESULTS.md §9) |
| 2 legacy W2 reproductions (byte-identity) | ~0.006 core-h | R5C §9 |
| identity re-validation on the frozen 12 | ~0 | disk reads |
| **registered total estimate** | **≈ 0.184 core-h ≈ $0.009** | derived at the recorded rate |

Under Charter §18's **487 core-h** and under the **$25** pre-authorised ceiling.
**CAP, registered: 1.0 core-h = $0.0513** (R5C's cap). An overrun **stops the
run**; it does not get a new budget. Modest upward risk if the distance criterion
forces longer iteration on a few cases; bounded well under the cap. At every
process completion the estimate is compared against the actual incurred cost, in
core-minutes from logs, as a row in `docs/COST_CALIBRATION.md` (rule 12).

---

## 5. WHAT IS RESERVED, AND THE FREEZE

Reserved to Sanaa (not this lane, not the supervisor): C2 and any re-baselining;
re-opening R3/the line direction; any send. **The freeze:** the supervisor
freezes **this document and `grade_r5d.py` together in one commit** after a
personal §3 check-1 diff-read of the grader (measurement-script diffs read as
diffs, never delegated). At freeze the comparator sha256 is recorded here and the
frozen file is verified to **be** the file that runs, by hashing against the
committed blob. **Until then: UNFROZEN, PENDING.**

## 6. VERDICT VOCABULARY

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`,
and nothing else. **Lane verdict at draft time: `PENDING` — nothing has been run
and nothing is frozen.**
