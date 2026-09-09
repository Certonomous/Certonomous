# T23G2Rn2 — PRE-REGISTRATION. §2ba NUMERICS SUCCESSOR TO T23G2Rn's PENDING COST-MISS

Predecessor: T23G2Rn (PENDING — §6 cost-model MISS: `relTol 0` removed GAMG's
relative early-exit, so the linear solver ran to its default `maxIter` (1000
V-cycles) EVERY outer step at 13.79/13.11/14.53× the T23G2R per-iteration cost;
the diagnostic run was stopped and the rung is `PENDING`, infra-confounded /
rule-4 incomplete). Verdict artifact:
`verification/runs/T-family/T23G2Rn_runs/T23G2Rn_RUNG_VERDICT.txt`; cost record
`docs/COST_CALIBRATION.md` row `C-20260909T183500.000000Z-t23g2rn`; lesson
`docs/LESSONS.md` **L-514**.

> ## FROZEN — two-commit freeze, heat-transfer supervisor, 2026-09-09. NO SOLVER LAUNCHED YET.
> The supervisor's §3 measurement-script diff-read of `build_t23g2rn2.py`,
> `analyse_t23g2rn2.py` and the completion wrapper `mark_done_t23g2rn2.py` is DONE
> (all sound; the comparator's grading logic is byte-identical to frozen
> `analyse_t23g2r.py` with `RESID_TOL["p_rgh"]` still **1e-8** — the GATE is NOT
> moved; the build edit is proved p_rgh-block/value-local: `tolerance 1e-8→1e-9`,
> `maxIter 100` inserted, `relTol 0.01` held). **Numerics chosen from MEASUREMENT,
> not the earlier relTol-1e-3 guess:** the near-convergence p_rgh initial residual
> is ~1e-8 (worst 1.966e-8), so the absolute floor 1e-9 (with relTol 0.01 →
> 1.97e-10, below it) binds and drives the solve a decade below the 1e-8 gate;
> `maxIter 100` makes T23G2Rn's relTol-0 runaway structurally impossible. Frozen by
> the **two-commit freeze** (commit 1/2 carries this prereg + the three scripts with
> `GRADING_PATH_FREEZE_COMMIT = "PIN-AT-FREEZE"`; commit 2/2 sets it to commit 1/2's
> sha). SELF member anchored per §2au.2: `EXPECTED_SELF_BLOB = None` (print-only),
> the authoritative blob in the `FREEZE-PIN: analyse_t23g2rn2.py@<blob>` line of the
> commit-2/2 message + grade-time byte-identity. Every number below the "reused
> gates" line is a **DESIGN ESTIMATE** except where it quotes a MEASURED artifact.
> **STILL OWED before the graded launch (personal check 4): the §5.3 pre-flight gate
> (incl. the on-disk p_rgh `tolerance 1e-9` / `maxIter 100` / `relTol 0.01`
> assertion) and the §7 autograder arming with a ≥24 h ceiling (L3 CAP is 22.15 h) —
> no solver launches until both are in place.**

---

## 0. §2ba LINEAGE — a numerics fix, no gate change

**Predecessor: `T23G2Rn` (explicit, for §2ba linkage).** This registration is the
active, dated **numerics** fix-successor to **T23G2Rn**'s **`PENDING` cost-model
miss**, which is itself the successor to **T23G2R**'s **`G-CONV` `GATE FAIL`**.
Under `VERIFICATION_CHARTER.md` §2ba this is a *fix-until-runs numerics change*: it
alters **linear-solver stopping settings only** (an absolute tolerance and an
iteration cap) — no gate, threshold, band, cap, label or directive is created,
moved or retired. It is within-lab authority and under the $25/run
pre-authorisation (CLAUDE.md rule 12).

**T23G2Rn keeps its `PENDING` status and T23G2R keeps its `NOT A RESULT`
verdict** (`§2an.2`). This linkage **moves no verdict** and **creates no gate,
threshold, band, cap or label of its own; it reuses T23G2R's** (which are
themselves reused verbatim from frozen T23G2). The one net-new item T23G2R already
carried (the prospective `R6` refusal) is inherited unchanged and can only add a
refusal.

**Scope boundary, stated plainly.** T23G2R was `NOT A RESULT` because `G-CONV`
floor-pinned p_rgh at ~1e-8 (`tolerance == gate`); T23G2Rn's fix for that
(`tolerance 1e-10`, `relTol 0`) was *correct in direction but unaffordable*: with
no relative early-exit GAMG ran to 1000 V-cycles every step (13-15× the
per-iteration cost, C-20260909T183500-t23g2rn). `G-MESHSIM` PASSED and `G-YPLUS`
PASSED under T23G2R (`T23G2R_RUNG_VERDICT.txt:17,:21`) — **the near-wall fix
worked and is not disturbed here.** T23G2Rn2 changes the ONE thing that made
T23G2Rn unaffordable while preserving the floor-pin repair. If the now-descending
residual lets the triple grade, the previously-voided `G-RATIO`/`G-ORDER` cells
become live again — registered as an open outcome (§4), not a gate change.

---

## 1. THE DIAGNOSIS — the floor-pin repair is right, but `relTol 0` over-corrects

**Two measured facts, both from disk, bracket the fix.**

### 1.1 The original defect (T23G2R): `tolerance == gate` floor-pins p_rgh

The p_rgh outer (initial) residual could not descend below ~1e-8 because the GAMG
linear solver's own `tolerance` (1e-8) EQUALLED the `G-CONV` gate (1e-8). The
comparator read final p_rgh initial residuals of **1.208e-08 (L2)** and **1.036e-08
(L3)**, both just above the `≤ 1e-8` gate
(`verification/runs/T-family/T23G2R_runs/T23G2R_COMPARATOR_STDOUT.txt:61-64`). In
`log.solve` the linear solver reports `No Iterations 0/1` once the residual reaches
the ~1e-8 neighbourhood — it stops the instant its residual crosses its own 1e-8
`tolerance`, so the next outer step bounces back to ~1e-8 (a limit cycle at the
gate). This is a numerics-configuration defect, not physical non-convergence.

### 1.2 The over-correction (T23G2Rn): `relTol 0` runs GAMG to `maxIter=1000`

T23G2Rn dropped the linear floor two decades (`tolerance 1e-10`) AND set `relTol
0`. `relTol 0` removes GAMG's relative early-exit, so the solver iterates until the
absolute 1e-10 floor is met — which, early in the run when the residual is far from
1e-10, means running to the **default `maxIter` of 1000 V-cycles EVERY outer
step**. MEASURED (T23G2Rn diagnostic run, then stopped on the measurement,
C-20260909T183500-t23g2rn):

| level | T23G2R CPU-s/iter (MEASURED) | T23G2Rn `relTol 0` CPU-s/iter (MEASURED) | ratio |
|---|---|---|---|
| L1 | 0.1737 | 2.3947 | **13.79×** |
| L2 | 0.4425 | 5.7996 | **13.11×** |
| L3 | 0.9369 | 13.6170 | **14.53×** |

Confirmed **NOT contention** (ClockTime/ExecutionTime = 1.00 on all three) and
**NOT a cap-timeout** (SIGTERM rc=143, capped=0). The mechanism is exactly `relTol
0` → 1000 V-cycles/step. **L-514.**

### 1.3 The measured near-convergence p_rgh initial linear residual (this decides `relTol`)

Measured from the frozen T23G2R `log.solve` files, over the **last 300 outer
steps** before each endTime (one p_rgh solve per outer step —
`nNonOrthogonalCorrectors 0`, `build_t23g2r.py:837`):

| level | median initial residual | min | **max (the binding value)** | No Iterations (median / mean) |
|---|---|---|---|---|
| L1 | 1.001e-08 | 7.99e-09 | 1.345e-08 | 1 / 0.51 |
| L2 | 1.072e-08 | 8.97e-09 | **1.966e-08** | 1 / 0.76 |
| L3 | 9.463e-09 | 8.80e-09 | 1.042e-08 | 0 / 0.20 |

**The near-convergence p_rgh initial linear residual is ~1e-8 typical, worst-case
1.966e-8 (L2).** GAMG does only 0-1 V-cycles there because it stops at the 1e-8
floor. (This is measured, not the ~1e-6 the L-514 illustrative example and the
C-20260909T183500-t23g2rn "relTol 1e-3" note assumed — the measurement is what
picks `relTol` here, per the drafting brief, not the illustrative guess.)

### 1.4 The repair L-514 prescribes

`relTol` **small-but-NONZERO** (so early steps keep the cheap relative early-exit)
with an **absolute tolerance ONE decade BELOW the gate** (so only near convergence
does the sub-gate absolute floor bind and drive p_rgh below 1e-8), plus an
**EXPLICIT `maxIter`** so a mis-set `relTol` can never silently run to 1000
V-cycles again. That is §2.

---

## 2. THE CHANGE — p_rgh linear-solver: tolerance one decade below the gate, keep relTol, cap iterations

### 2.1 The single edit (`system/fluid/fvSolution`, p_rgh block, all three levels identically)

| p_rgh key | T23G2R (frozen) | T23G2Rn (PENDING) | **T23G2Rn2 (proposed)** |
|---|---|---|---|
| `tolerance` | `1e-08` | `1e-10` | **`1e-09`** (ONE decade below the 1e-8 gate) |
| `relTol` | `0.01` | `0` | **`0.01` — UNCHANGED from T23G2R** (small, nonzero) |
| `maxIter` | *(absent → default 1000)* | *(absent → default 1000)* | **`100`** (INSERTED, explicit) |
| `solver` | `GAMG` | `GAMG` | **`GAMG` — UNCHANGED** |
| `smoother` | `GaussSeidel` | `GaussSeidel` | **`GaussSeidel` — UNCHANGED** |

**Written p_rgh block** (verified from `build_t23g2rn2.py`'s transformation of the
frozen base):
```
    p_rgh
    {
        solver          GAMG;
        tolerance       1e-09;
        maxIter         100;
        relTol          0.01;
        smoother        GaussSeidel;
    }
```

### 2.2 Why `relTol 0.01` (the LOOSEST safe value — measured, not guessed)

GAMG stops a p_rgh solve when its residual falls below **max(`tolerance`,
`relTol`×r0)**, where r0 is that step's initial residual. The design intent is that
**near convergence the absolute floor (1e-9) binds**, driving the linear solve a
full decade below the 1e-8 gate, while **early in the run the relative criterion
exits cheaply**.

For the absolute floor to bind near convergence, `relTol`×r0 must be ≤ the floor:
with the MEASURED worst-case near-convergence r0 = **1.966e-8** (§1.3), `relTol
0.01` gives `0.01 × 1.966e-8 = 1.97e-10`, which is **~5× BELOW the 1e-9 absolute
floor** → the floor binds with comfortable margin, so the linear solve is driven to
≤ 1e-9 (a full decade below the 1e-8 gate) on every near-convergence step. The data
would permit a `relTol` as loose as **0.05** (`0.05 × 1.966e-8 = 9.8e-10 ≤ 1e-9`);
`0.01` is chosen — LOOSER than L-514's illustrative `1e-3` (which assumed a ~1e-6
near-conv residual, 100× larger than measured) and therefore CHEAPER early — for
three reasons: (a) it satisfies the ≤1e-9 criterion with a 5× margin against the
measured worst case; (b) it is T23G2R's own value, so early-iteration cost is
byte-anchored to the measured T23G2R baseline (making §6 directly calibrated); and
(c) it is the minimal delta from the frozen predecessor. **The `relTol` value is
justified by the measured number (§1.3), not assumed.**

### 2.3 Why explicit `maxIter 100`

The default GAMG `maxIter` is 1000, which is exactly what let T23G2Rn's `relTol 0`
run away to 13-15× (§1.2). An explicit `maxIter 100` **caps the worst-case
per-iteration cost at ~2.2×** (F + 100k on the measured relTol-0 calibration, §6) —
it is a hard ceiling on p_rgh V-cycles per step, so no `relTol`/tolerance
mis-configuration can reproduce the 13× blow-up. It is far above the ~3-4 V-cycles
GAMG needs to drive one decade from r0~1.2e-8 to the 1e-9 floor near convergence
(measured reduction ≈ 0.33 decade/V-cycle in this region), so it does not bind in
the intended regime — it binds only if the solve genuinely cannot converge, which
is a finding, not a silent cost.

### 2.4 What is held BYTE-INVARIANT from T23G2R

Everything else, re-asserted not assumed: the **mesh** (first-cell heights, cell
counts `40,320 / 90,720 / 204,120`, 2.25 similarity), the **endTimes** `8000 /
16000 / 28000` (UNCHANGED — the fix is the linear-solver settings, not the
iteration budget), geometry, operating point, properties, turbulence model, wall
treatment, the conjugate interface, all schemes, `ranks = 1`, `deltaT 1`
(`build_t23g2r.py:562` — so rule-4 clause 5 is the fixed-dt form `n_exec ==
endTime`), and **every OTHER solver block**: `rho` (PCG, tol 1e-8, relTol 0),
`"(U|h|k|omega)"` (PBiCGStab, tol 1e-9, relTol 0.01), the solid `h` solver, the
`SIMPLE` block (no `residualControl`), and **all `relaxationFactors`**. The build
script `build_t23g2rn2.py` **REFUSES (exit non-zero) if any non-p_rgh dictionary
differs** from what `build_t23g2r.py` produces, and proves the p_rgh edit is
block-local and limited to the tolerance VALUE plus a single ADDED `maxIter` line
(§5). Any file that differs and is not the p_rgh block is a REFUSAL, not a note.

---

## 3. THE REUSED GATES — VERBATIM FROM T23G2R (which reuses T23G2's), NONE RELAXED

Every gate, threshold and band below is reused BYTE-FOR-INTENT from the frozen
T23G2R comparator (`analyse_t23g2r.py`), transcribed into `analyse_t23g2rn2.py`
whose grading logic is **byte-identical** to it (verified: a lossless case-token
rename of the constants only; §5). Not one is relaxed. The successor freezes these
before it re-runs (prediction-first).

- **`G-CONV` (the failing gate) — REUSED UNCHANGED:** at `endTime`, on every level,
  **`h` ≤ 1e-9** and `Uy Uz p_rgh k omega` initial residual **≤ 1e-8** at the last
  iteration; `Ux` excluded with the exclusion itself measured per level
  (`analyse_t23g2r.py` `RESID_TOL`, transcribed to `analyse_t23g2rn2.py:125-126`).
  **The 1e-8 p_rgh threshold is NOT moved.** §2 lowers the *linear-solver* floor to
  1e-9 and caps iterations so the run can MEET the frozen 1e-8 gate; the gate value
  is untouched (rule 2).
- **`G-MESHSIM` — REUSED UNCHANGED:** cell-count ratio exactly **2.250000** per
  region; first-cell height ratio **1.500 ± 0.005**; per-cell growth **≤ 1.25**;
  housing wall cells **≥ 8** at the coarsest level.
- **`G-YPLUS` — REUSED UNCHANGED:** max y+ ≤ **1.0** on EVERY wall patch, EVERY
  level; two instruments agreeing within 2 %, both planted; the prospective `R6`
  refusal (absent primary log ⇒ REFUSE) inherited from T23G2R.
- **Roache triple gating — REUSED UNCHANGED:** `Fs = 1.25`, `scripts/roache_triple.py`
  under CLAUDE.md rule 5 ordering.
- **`G-ORDER` band — REUSED UNCHANGED:** p(`Q4`) in **[0.5, 1.5]**, with the
  `R7`/`R3` repair in place.
- **`Q3` / band-transfer — REUSED UNCHANGED:** ΔT = T − 288.0 K in **[46.0, 56.0]
  K** transferred to Q1/Q3/Q2. **The band is NOT moved.**
- **The six graded quantities and roles — REUSED UNCHANGED:** Q4 core vol-avg T
  (PRIMARY ORDER), Q5 housing surface heat flux (REPORTED, NEVER GATED), Q1, Q3,
  Q2, Q6.
- **Planted-zero controls — REUSED UNCHANGED:** 6 quantities × 3 levels + 2 y+
  readers = **20**, each asserted, refusing on a control that cannot read its plant
  back (rule 3).

**No gate value, threshold or band above differs from T23G2R by any amount. The
only change is the p_rgh linear-solver tolerance/maxIter (§2.1).**

---

## 4. PREDICTIONS — prediction-first, frozen before the re-run

DESIGN ESTIMATES.

| id | prediction | basis |
|---|---|---|
| **P-CONV** | with the abs floor at 1e-9 (bound near convergence via `relTol 0.01`, §2.2), the p_rgh outer residual descends **below 1e-8 on ALL three levels** at the unchanged endTimes → **`G-CONV` PASS** | the residual was pinned at the linear tolerance, not at a physical plateau; the linear solve is now driven a full decade below the gate each near-conv step; L1 already CONVERGED at 1e-8 with headroom |
| **P-COST** | the run completes at **~1.5× (POINT) and no more than ~2.2× (CAP)** the T23G2R per-iteration cost — **NOT** 13-15× — because `relTol 0.01` restores the relative early-exit and `maxIter 100` caps runaway V-cycles | §6, calibrated on the MEASURED relTol-0 data point (C-20260909T183500-t23g2rn) |
| **P-TRIP** | with all three levels iteratively converged, rule 5 step (a) no longer voids the triple → the Roache triple becomes **gradeable**, and `G-RATIO`/`G-ORDER` become live cells again | T23G2R's NOT A RESULT on those cells was a downstream consequence of G-CONV |
| **P-YM** | y+ and mesh are unchanged by a linear-solver-settings edit → **`G-YPLUS` PASS, `G-MESHSIM` PASS** carry over from T23G2R | the mesh and endTimes are byte-invariant (§2.4) |

**Registered loss modes (honest, not waved).**
- **P-CONV can lose — `relTol` still too loose / floor above 1e-8.** If, despite the
  abs floor at 1e-9, the outer coupling limit-cycles at a **physical plateau above
  1e-8** (a genuine steady-state limit-cycle in this conjugate coupling), `G-CONV`
  `GATE FAIL` again, the rung stays `NOT A RESULT`, and **a further successor is
  owed** — reported as exactly that. (This is a *physical* plateau, distinct from
  the *numerical* floor-pin §2 removes.)
- **P-COST can lose — still too costly.** If GAMG cannot reach the 1e-9 floor
  cheaply near convergence and instead hits `maxIter 100` on most steps, the cost
  rises toward the ~2.2× CAP. It is **bounded** there by `maxIter 100` (it cannot
  reach 13×), but a level that exceeds its CAP timeout **STOPS** (rule 12 — no
  re-budget) and is reported as a cost overrun, not silently re-run.
- **P-TRIP can lose the rung a different way.** If the now-gradeable triple lands
  **out of band** (`G-ORDER` outside [0.5, 1.5], `Q1/Q3/Q2` fine value outside
  [46.0, 56.0] K, or a non-CONVERGING triple), that is a `GATE FAIL` / `NOT A
  RESULT` reported as such. Making the triple *gradeable* is not making it *pass*.

---

## 5. THE SCRIPTS + THE COMPLETION-INSTRUMENT DECISION (supervisor's)

Written by this draft (NOT sha-frozen; the §3 diff-read and freeze are the
supervisor's):

1. **`docs/campaigns/T-family/build_t23g2rn2.py`** — a parametric edit of
   `build_t23g2r.py` that imports it and overrides ONLY the p_rgh block in
   `FLUID_SOLUTION`: substitutes `tolerance 1e-08 → 1e-09`, INSERTS `maxIter 100`,
   and holds `relTol 0.01`, `solver GAMG`, `smoother GaussSeidel` INVARIANT (all
   asserted from the base, never assumed). It **prints the p_rgh block it writes**
   and **REFUSES (exit non-zero)** unless the base has exactly one p_rgh block with
   the expected invariants, `tolerance 1e-08` and NO pre-existing `maxIter`, and the
   modified `FLUID_SOLUTION` differs from the base ONLY inside the p_rgh block and
   inside it ONLY by the tolerance VALUE and one ADDED `maxIter 100;` line (proved
   by a normalize-and-compare that blanks the tolerance value and removes the added
   line). Refusal contract exercised (base-already-has-maxIter, relTol-changed,
   tolerance≠1e-08, two-p_rgh-blocks all REFUSE).
2. **`docs/campaigns/T-family/analyse_t23g2rn2.py`** — the comparator, grading
   LOGIC **byte-identical** to frozen `analyse_t23g2r.py` (verified by a lossless,
   reversible case-token rename of the proven `analyse_t23g2rn.py` template). The
   ONLY differences are the case-name/path constants (`T23G2R`→`T23G2Rn2`, RUNS,
   LEVELS, ENDTIME keys, CELLS keys, SELF_REL, GRADING_PATH, the runtime banner and
   `case_dir` refusal strings) and the self-freeze machinery
   (`GRADING_PATH_FREEZE_COMMIT = "PIN-AT-FREEZE"`, `EXPECTED_SELF_BLOB = None`), so
   the DRAFT guard `verify_self()` REFUSES to grade until the supervisor pins the
   freeze commit. `--selftest` PASSES (the planted-control engine sees plants and
   refuses blind readers). ENDTIME/CELLS are UNCHANGED (same mesh & budget as
   T23G2R).
3. **Reused unchanged, on the grading path:** `scripts/roache_triple.py`,
   `docs/campaigns/T-family/t23g_readonly_diagnosis.py`, and the rule-4 completion
   instrument (§5.1).

### 5.1 The rule-4 completion instrument — OPTION (b), the thin wrapper

Mirroring the T23G2Rn supervisor decision, **OPTION (b)** is wired: the frozen
`mark_done_t23.py` (blob `982e1db6622454c2e5cc3e9eb4d6811e87735b78`) stays
**byte-invariant**, and a thin wrapper
`verification/runs/T-family/T23_runs/mark_done_t23g2rn2.py` **imports** it and
reuses its six-clause logic verbatim, widening only the **in-memory** `CASES` to
add `T23G2Rn2_L1/L2/L3`. `analyse_t23g2rn2.py`'s `require_done()` target and the
first `mark_done` member of `GRADING_PATH` name the wrapper; the frozen base
`mark_done_t23.py` is ALSO carried as an explicit `GRADING_PATH` member so its blob
is recorded on the comparator's face. `--selftest` on the wrapper PASSES (it drives
the frozen base's planted control RED/GREEN). Clause 5 is the fixed-dt form
(`deltaT 1` → `n_exec == endTime`), unmodified. The alternative OPTION (a) (an
additive rule-14 insertion of the three level names into `mark_done_t23.py`'s
`CASES`, changing its blob) is available if the supervisor prefers it; **this lane
does not pick — the supervisor decides in the §3 read.**

### 5.3 PRE-FLIGHT GATE — the p_rgh-value assertion, adapted to the new values

Before the graded launch a pre-flight gate (a launcher-side RUN ARTIFACT that
grades nothing) is OWED, structured like
`verification/runs/T-family/T23G2Rn_runs/preflight_gate_t23g2rn.py` but with the
**§5.3 numerics gate adapted to T23G2Rn2's values**: after a scratch build, grep
the **WRITTEN** `system/fluid/fvSolution` and assert the p_rgh block reads
**`solver GAMG` / `tolerance 1e-09` / `maxIter 100` / `relTol 0.01` / `smoother
GaussSeidel`**, REFUSING otherwise. It also re-checks the rule-4 age guard (`0/` or
any time dir already present ⇒ REFUSE), the twelve `0.orig` fields, the registered
`endTime` (8000/16000/28000), the seven function objects and the `housing_whf`
ordering. **The graded launch is REFUSED until this assertion passes on a real
built case** — it reads off the *written file*, not the in-memory build string, so
a silent non-propagation of `build_t23g2rn2.py`'s module-global override is caught
before any solver iterates. (The build script also prints the p_rgh block and
refuses on any non-p_rgh difference, §2.4; this gate is the independent on-disk
confirmation.) **OWED after the freeze; the supervisor reviews it.**

---

## 6. COST — rule 12, POINT + CAP in core-minutes, cost_basis honest

**`cost_basis = REPORTED-BY-OWNER`:** the rate is owner-stated ($0.0513/core-h,
2026-08-21/22) and the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so no dollar figure here is a measurement.

**Basis — a MEASURED calibration, not the ×1.15 guess that sank T23G2Rn.** The
per-iteration cost model is fitted to two MEASURED points per level: the T23G2R
baseline CPU-s/iter and the T23G2Rn `relTol 0` CPU-s/iter at 1000 V-cycles/step
(both from C-20260909T183500-t23g2rn). Modelling CPU-s/iter = F + k·V (V = p_rgh
V-cycles/step) gives, per level, a fixed per-step cost F (non-p_rgh work) and a
per-V-cycle cost k:

| level | baseline CPU-s/iter (V≈5.2/5.2/11.8) | relTol-0 CPU-s/iter (V=1000) | F | k | **F+100k (maxIter-100 ceiling)** = CAP× |
|---|---|---|---|---|---|
| L1 | 0.1737 | 2.3947 | 0.1620 | 0.002233 | 0.3853 = **2.22×** |
| L2 | 0.4425 | 5.7996 | 0.4144 | 0.005385 | 0.9530 = **2.15×** |
| L3 | 0.9369 | 13.6170 | 0.7852 | 0.012832 | 2.0684 = **2.21×** |

The p_rgh V-cycles are a small fraction of the total conjugate multi-region step
(F is 84-93 % of the baseline step), which is precisely why 1000 V-cycles cost only
13× and not ~190×. With **`maxIter 100`** the per-step V-cycles are capped at 100,
so **F+100k ≈ 2.2× is a HARD per-iteration ceiling** that no configuration can
exceed. The realistic POINT is lower: near-convergence steps need only ~3-4
V-cycles to drive from r0~1.2e-8 to the 1e-9 floor, so the pure linear model
projects ~1.03-1.04×; **POINT is set conservatively at ×1.5** to hedge (a) the
single-calibration-point model risk and (b) the risk that GAMG needs more V-cycles
or stalls toward `maxIter` near the abs floor in the conjugate limit-cycle.
**CAP at ×2.2** is the measured maxIter-100 ceiling.

Applied to T23G2R's MEASURED per-level actuals (ClockTime core-min, `ranks = 1`;
on disk, `T23G2R_L*/log.solve` final `ClockTime` = 1564 / 9072 / 36245 s; these
match the T23G2Rn §6 record):

| level | cells | `endTime` | predecessor actual [core-min] | **POINT** (×1.5) | **CAP** (×2.2) | timeout [s] |
|---|---|---|---|---|---|---|
| `T23G2Rn2_L1` | 40,320 | 8,000 | 26.07 | **39.11** | **57.35** | 3,441 |
| `T23G2Rn2_L2` | 90,720 | 16,000 | 151.20 | **226.80** | **332.64** | 19,958 |
| `T23G2Rn2_L3` | 204,120 | 28,000 | 604.08 | **906.12** | **1328.98** | 79,739 |
| **CAMPAIGN** | | | 781.35 | **1172.03** | **1718.97** | |

(Clean ExecutionTime baseline for reference: 25.74 / 136.74 / 528.63 = 691.11
core-min; ClockTime is used above as the conservative actual, as in the T23G2Rn
§6 — it embeds the observed ≤1.14× contention.)

Timeout = CAP core-min × 60 / ranks (ranks = 1). **The timeout IS the cap. An
overrun STOPS the run; a capped level is not restarted with a bigger number**
(rule 12). L3's CAP timeout is **22.15 h**, so the §7 autograder wall ceiling is
set to **24 h** for this campaign (the T23G2Rn ~20 h ceiling was sized to its
smaller ×1.35 CAP). If the graded run's contention is materially worse than the
baseline's, a level may hit its timeout and STOP — reported as an overrun.

**USD — DERIVED, NEVER MEASURED:** POINT 1172.03 core-min = 19.53 core-h ×
$0.0513 = **$1.00**; CAP 1718.97 core-min = 28.65 core-h × $0.0513 = **$1.47**.
Under the $25/run pre-authorisation, and still costed here per rule 12.
**Estimate-versus-actual calibration (rule 12) is owed at completion**: a row in
`docs/COST_CALIBRATION.md` comparing this POINT against the measured actual, gap
attributed, waste named separately — and, specifically, **closing the loop on
C-20260909T183500-t23g2rn** (whether the measured T23G2Rn2 uplift lands in the
[1.5, 2.2]× band this model predicts).

---

## 7. THE §2ba DETACHED AUTOGRADER — SPECIFIED, NOT ARMED

A `§2ba` detached autograder is specified for T23G2Rn2's levels and is **NOT armed
by this draft** (no solver launches until the freeze is committed). Contract
(modelled on `autograde_t23g2rn.sh`):

- **Detached** under `setsid` (PPID → 1) so it survives the launching lane's exit.
- **Grade-once guard:** a durable marker prevents a second autograde overwriting
  the first verdict.
- **Polls the solver pid(s) with `kill -0`** and does not grade until the run has
  ended; **rc captured INSIDE the detached wrapper**, never around the `setsid`
  line (setsid parent returns 0 for every outcome).
- **~24 h wall ceiling** (sized to L3's 22.15 h CAP timeout, §6) so a stalled poll
  cannot run forever.
- **Clears `__pycache__`** before invoking the comparator (stale pycache inverts
  mutation tests).
- **Runs the FROZEN comparator verbatim** (`analyse_t23g2rn2.py`, once pinned) — no
  re-implementation, no flags that change grading.
- **Exit-map 0/1/2/3:** 0 PASS, 1 GATE FAIL, 2 REFUSAL, 3 NOT A RESULT.
- **Writes a durable `T23G2Rn2_RUNG_VERDICT.txt`** recording the comparator's own
  `RUNG VERDICT` line verbatim, the comparator pin, the mark_done pins, the exit
  code and the stdout artifact path — the same shape as `T23G2Rn_RUNG_VERDICT.txt`.

The autograder script and its arming are **OWED after the freeze** and are the
supervisor's to review; the §5.3 pre-flight gate is also owed before the graded
launch — the launch is refused until it passes — its cost reported separately.

---

## 8. WHAT THIS DRAFT DELIBERATELY DOES NOT DO

- **It does not edit any frozen file.** T23G2R keeps its bytes and `NOT A RESULT`;
  T23G2Rn keeps its `PENDING`; `mark_done_t23.py @982e1db6` is **not** edited
  (OPTION (b) wrapper, §5.1).
- **It does not commit anything, freeze any sha, or run any solver** (the §3
  diff-read, the completion-instrument review, the two-commit freeze, the §5.3
  pre-flight gate, the §7 autograder arming and the launch are the supervisor's).
- **It does not move, widen or relax any gate, threshold, band, cap or label.** The
  only change is the p_rgh linear-solver tolerance (1e-8→1e-9) and an inserted
  explicit `maxIter 100`, with `relTol` kept at 0.01 — a §2ba numerics fix (§2.1).

*Drafted 2026-09-09 by a heat-transfer `lab-lane`. NOT FROZEN — the §3 code
diff-read of `build_t23g2rn2.py`/`analyse_t23g2rn2.py`/`mark_done_t23g2rn2.py`, the
completion-instrument review (§5.1), the blob pins and the two-commit freeze, the
§5.3 pre-flight gate and the §7 autograder arming are the supervisor's
(non-delegable). Nothing is committed, frozen or launched by this lane.*
